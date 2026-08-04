"""Tests for the Polymarket order-book capture path -- DATA-INFRA-002.

Covers three things that were asserted narratively but never pinned down
in the test suite:

1. `parse_polymarket_book` on two-sided, one-sided, and empty books --
   confirming `two_sided` is always written and `mid`/`spread` only when
   both sides are present (DATA-INFRA-001 said this was "tested this
   session"; it was not previously committed as a reproducible test).
2. `record_capture_heartbeat` / `ingest_polymarket_books`'s heartbeat
   write -- the mechanism that makes "we did not poll" distinguishable
   from "we polled and got nothing" (DATA-INFRA-002 §2). No network
   access is used; the batch fetch is monkeypatched.
3. `_gamma_get`'s retry/backoff -- added under I-047 after the measured
   evidence in `logs/capture/polymarket-book.err` showed this call's
   *lack* of retry logic was the actual, repeated, uncaught cause of
   several real capture gaps.
"""

import json

import pandas as pd
import pytest

from castellan import TrialRegistry
from castellan.data import PITStore
from castellan.loaders import (
    parse_polymarket_book,
    ingest_polymarket_books,
    record_capture_heartbeat,
)
import castellan.loaders as loaders


# ----------------------------------------------------------------------
# parse_polymarket_book (pure, offline)
# ----------------------------------------------------------------------

def test_parse_two_sided_book():
    raw = {
        "timestamp": "1785345770396",  # ms epoch, per the measured unit finding
        "asset_id": "tok1",
        "bids": [{"price": "0.40", "size": "100"}, {"price": "0.39", "size": "50"}],
        "asks": [{"price": "0.42", "size": "80"}],
    }
    df = parse_polymarket_book(raw, depth=10)
    row = df.iloc[0]
    assert row["two_sided"] == 1.0
    assert row["best_bid"] == 0.40
    assert row["best_ask"] == 0.42
    assert row["mid"] == pytest.approx(0.41)
    assert row["spread"] == pytest.approx(0.02)
    assert row["n_bid_levels"] == 2
    assert row["n_ask_levels"] == 1
    # event_time parsed as milliseconds, matching the measured unit correction
    assert df.index[0] == pd.Timestamp("2026-07-29T17:22:50.396Z")


def test_parse_one_sided_book_no_mid_no_error():
    raw = {"timestamp": "1785345770396", "asset_id": "tok1",
           "bids": [{"price": "0.40", "size": "100"}], "asks": []}
    df = parse_polymarket_book(raw)
    row = df.iloc[0]
    assert row["two_sided"] == 0.0
    assert row["best_bid"] == 0.40
    assert "best_ask" not in row.dropna().index
    assert "mid" not in row.dropna().index
    assert "spread" not in row.dropna().index


def test_parse_empty_book_still_writes_a_row():
    """The load-bearing fact behind the not-polled/no-quote finding: a
    genuinely empty book (both sides empty) still produces a row with
    `two_sided=0.0`, not a missing/errored parse. 'We polled and there
    was no quote' IS distinguishable from a missing row -- it is only
    'we polled and the request itself failed' that isn't (see the
    heartbeat tests below)."""
    raw = {"timestamp": "1785345770396", "asset_id": "tok1", "bids": [], "asks": []}
    df = parse_polymarket_book(raw)
    assert len(df) == 1
    assert df.iloc[0]["two_sided"] == 0.0
    assert df.iloc[0]["n_bid_levels"] == 0
    assert df.iloc[0]["n_ask_levels"] == 0


# ----------------------------------------------------------------------
# record_capture_heartbeat / ingest_polymarket_books
# ----------------------------------------------------------------------

@pytest.fixture
def store(tmp_path):
    reg = TrialRegistry(str(tmp_path / "r.db"))
    s = PITStore(str(tmp_path / "pit.db"), reg)
    yield s
    s.close()


def _heartbeats(store):
    cur = store.conn.execute(
        "SELECT event_time, meta_json FROM documents "
        "WHERE source='polymarket-capture-meta' AND symbol='__heartbeat__' "
        "ORDER BY event_time"
    )
    return [(r[0], json.loads(r[1])) for r in cur.fetchall()]


def test_total_fetch_failure_writes_heartbeat_and_nothing_else(store, monkeypatch):
    def boom(token_ids, timeout=10.0):
        raise ConnectionError("simulated outage")

    monkeypatch.setattr(loaders, "fetch_polymarket_books", boom)
    token_meta = {"tok1": {"condition_id": "c1", "question": "q", "slug": "s", "outcome": "Yes"}}
    result = ingest_polymarket_books(store, token_meta, max_retries=1, backoff_s=0)

    assert result["ok"] is False
    # no scalar observations, no book_snapshot documents -- only the heartbeat
    n_obs = store.conn.execute(
        "SELECT COUNT(*) FROM observations WHERE source='polymarket-clob'"
    ).fetchone()[0]
    n_snap = store.conn.execute(
        "SELECT COUNT(*) FROM documents WHERE source='polymarket-clob'"
    ).fetchone()[0]
    assert n_obs == 0
    assert n_snap == 0

    hb = _heartbeats(store)
    assert len(hb) == 1
    meta = hb[0][1]
    assert meta["ok"] is False
    assert meta["n_requested"] == 1
    assert meta["n_failed"] == 1
    assert "simulated outage" in meta["error"]


def test_successful_round_writes_heartbeat_alongside_data(store, monkeypatch):
    raw_response = [{
        "asset_id": "tok1", "timestamp": "1785345770396",
        "bids": [{"price": "0.4", "size": "10"}],
        "asks": [{"price": "0.42", "size": "10"}],
    }]

    def fake_fetch(token_ids, timeout=10.0):
        return raw_response, 1785345771.0

    monkeypatch.setattr(loaders, "fetch_polymarket_books", fake_fetch)
    token_meta = {"tok1": {"condition_id": "c1", "question": "q", "slug": "s", "outcome": "Yes"}}
    result = ingest_polymarket_books(store, token_meta)

    assert result["ok"] is True
    assert result["captured"] == ["tok1"]

    hb = _heartbeats(store)
    assert len(hb) == 1
    meta = hb[0][1]
    assert meta["ok"] is True
    assert meta["n_captured"] == 1
    assert meta["n_failed"] == 0


def test_heartbeat_dedupes_on_replay(store):
    """Replaying the same round (e.g. a merge script re-processing a
    capture-store export) must not accumulate duplicate heartbeat rows --
    `ingest_documents` already dedupes on `ref`; this pins that the
    heartbeat's `ref` construction actually benefits from it."""
    ts = "2026-08-01T00:00:00+00:00"
    for _ in range(3):
        record_capture_heartbeat(
            store, ts, 1785345771.0, ok=True,
            n_requested=5, n_captured=5, n_failed=0,
        )
    hb = _heartbeats(store)
    assert len(hb) == 1


def test_heartbeat_distinguishes_not_polled_from_polled_empty(store):
    """The central claim of DATA-INFRA-002 §2, pinned as a test: after
    this change, a round with genuinely no active tokens (polled, empty
    universe) leaves a heartbeat row; a round that never ran leaves
    nothing at all. Both are distinguishable from 'polled, request
    failed' (previous test) by the `ok` flag."""
    record_capture_heartbeat(
        store, "2026-08-01T00:15:00+00:00", None, ok=True,
        n_requested=0, n_captured=0, n_failed=0,
    )
    hb = _heartbeats(store)
    assert len(hb) == 1
    assert hb[0][1]["ok"] is True
    assert hb[0][1]["n_requested"] == 0
    # A round with NO heartbeat and NO data at all is, by construction,
    # indistinguishable from "did not run" -- which is exactly correct:
    # nothing ran, nothing should be recorded.


# ----------------------------------------------------------------------
# _gamma_get retry/backoff (I-047)
# ----------------------------------------------------------------------

def test_gamma_get_retries_and_recovers(monkeypatch):
    import urllib.error

    calls = {"n": 0}

    class _FakeResp:
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def read(self):
            return b"[]"

    def fake_urlopen(req, timeout=10.0, context=None):
        calls["n"] += 1
        if calls["n"] < 3:
            raise urllib.error.URLError("simulated DNS failure")
        return _FakeResp()

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    monkeypatch.setattr(loaders.time, "sleep", lambda s: None)  # no real waiting in tests

    result = loaders._gamma_get({"active": "true"}, max_retries=3, backoff_s=0.01)
    assert result == []
    assert calls["n"] == 3


def test_gamma_get_raises_after_exhausting_retries(monkeypatch):
    import urllib.error

    def always_fails(req, timeout=10.0, context=None):
        raise urllib.error.URLError("simulated persistent outage")

    monkeypatch.setattr("urllib.request.urlopen", always_fails)
    monkeypatch.setattr(loaders.time, "sleep", lambda s: None)

    with pytest.raises(urllib.error.URLError):
        loaders._gamma_get({"active": "true"}, max_retries=3, backoff_s=0.01)
