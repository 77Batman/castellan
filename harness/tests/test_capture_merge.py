"""Tests for `castellan.capture_merge` -- DATA-INFRA-002 §1, the
dual-writer decision's mechanism.

Builds a synthetic satellite capture store (what the VPS would produce)
and a synthetic target store (what `book/pit.db` would be), then checks:
replay fidelity, idempotency (re-running is a no-op the second time),
document ref-deduplication, and that a genuine value conflict is caught
by the target's ordinary restatement detection and logged to the real
registry -- the A4 escalation path this design depends on.
"""

import pandas as pd
import pytest

from castellan import TrialRegistry
from castellan.data import PITStore
from castellan.capture_merge import merge_capture_store
from castellan.loaders import record_capture_heartbeat


@pytest.fixture
def capture_store(tmp_path):
    s = PITStore(str(tmp_path / "capture.db"))  # no registry -- satellite store, disposable
    yield s
    s.close()


@pytest.fixture
def target(tmp_path):
    reg = TrialRegistry(str(tmp_path / "registry.db"))
    s = PITStore(str(tmp_path / "pit.db"), reg)
    yield s, reg
    s.close()


def _round_df(two_sided=1.0, best_bid=0.4):
    idx = pd.DatetimeIndex([pd.Timestamp("2026-08-05T00:00:00Z")])
    return pd.DataFrame({"two_sided": [two_sided], "best_bid": [best_bid]}, index=idx)


def test_replay_fidelity(capture_store, target):
    target_store, _ = target
    capture_store.ingest("polymarket-clob", "tok1", _round_df(), knowledge_time=1000.0)

    result = merge_capture_store(capture_store.conn, target_store, watermark=0.0)
    assert result["rounds_merged"] == 1
    assert result["observations_new"] == 2  # two_sided + best_bid
    assert result["observations_restated"] == 0

    merged = target_store.asof("polymarket-clob", "tok1", 2000.0)
    assert merged.iloc[0]["best_bid"] == 0.4
    assert merged.iloc[0]["two_sided"] == 1.0


def test_idempotent_rerun_is_all_unchanged(capture_store, target):
    target_store, _ = target
    capture_store.ingest("polymarket-clob", "tok1", _round_df(), knowledge_time=1000.0)

    r1 = merge_capture_store(capture_store.conn, target_store, watermark=0.0)
    r2 = merge_capture_store(capture_store.conn, target_store, watermark=0.0)  # replay same window
    assert r1["observations_new"] == 2
    assert r2["observations_new"] == 0
    assert r2["observations_unchanged"] == 2
    assert r2["observations_restated"] == 0


def test_watermark_skips_already_merged_rounds(capture_store, target):
    target_store, _ = target
    capture_store.ingest("polymarket-clob", "tok1", _round_df(), knowledge_time=1000.0)
    r1 = merge_capture_store(capture_store.conn, target_store, watermark=0.0)
    wm = r1["new_watermark"]
    assert wm == 1000.0

    # a second round arrives later on the capture side
    capture_store.ingest("polymarket-clob", "tok1", _round_df(best_bid=0.5), knowledge_time=2000.0)
    r2 = merge_capture_store(capture_store.conn, target_store, watermark=wm)
    assert r2["rounds_merged"] == 1  # only the new round, not re-scanning the first


def test_documents_dedupe_on_ref(capture_store, target):
    target_store, _ = target
    capture_store.ingest_documents("polymarket-clob", "tok1", [{
        "doc_type": "book_snapshot", "event_time": "2026-08-05T00:00:00+00:00",
        "knowledge_time": 1000.0, "ref": "tok1:1785000000000", "meta": {"a": 1},
    }])
    r1 = merge_capture_store(capture_store.conn, target_store, watermark=0.0)
    assert r1["documents_merged"] == 1
    r2 = merge_capture_store(capture_store.conn, target_store, watermark=0.0)
    assert r2["documents_merged"] == 0  # ref already present
    assert r2["documents_seen"] == 1


def test_heartbeats_are_merged_too(capture_store, target):
    target_store, _ = target
    record_capture_heartbeat(
        capture_store, "2026-08-05T00:00:00+00:00", 1000.0, ok=True,
        n_requested=2, n_captured=2, n_failed=0,
    )
    result = merge_capture_store(capture_store.conn, target_store, watermark=0.0)
    assert result["documents_merged"] == 1
    docs = target_store.conn.execute(
        "SELECT COUNT(*) FROM documents WHERE source='polymarket-capture-meta'"
    ).fetchone()[0]
    assert docs == 1


def test_genuine_conflict_is_detected_as_restatement_and_logged(capture_store, target):
    """The A4 escalation path this whole design depends on: if a merged
    value genuinely differs from what the target already holds at the
    same (symbol, field, event_time), the target's ordinary
    restatement-detection fires -- same code path as any other source --
    and is logged to the REAL registry passed to the target store."""
    target_store, registry = target
    # target already has a different value at the same event_time/field
    target_store.ingest("polymarket-clob", "tok1", _round_df(best_bid=0.4), knowledge_time=500.0)

    capture_store.ingest("polymarket-clob", "tok1", _round_df(best_bid=0.55), knowledge_time=1500.0)
    result = merge_capture_store(capture_store.conn, target_store, watermark=0.0)

    assert result["observations_restated"] == 1
    events = registry.events(kind="data_restatement")
    assert len(events) == 1
    assert events[0]["detail"]["source"] == "polymarket-clob"
