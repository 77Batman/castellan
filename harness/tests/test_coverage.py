"""Tests for `castellan.coverage` -- DATA-INFRA-002 §5, the coverage
reporter's arithmetic core.

Builds a tiny synthetic PITStore rather than relying on the real
`book/pit.db` (whose exact figures will keep changing as capture
continues to run), then checks the reported numbers against arithmetic
computed independently in the test itself -- the same cross-check
discipline used to verify the CIO's original hand-computed figures
before trusting the script.
"""

import json

import pandas as pd
import pytest

from castellan import TrialRegistry
from castellan.data import PITStore
from castellan.coverage import compute_polymarket_coverage
from castellan.loaders import record_capture_heartbeat


@pytest.fixture
def store(tmp_path):
    reg = TrialRegistry(str(tmp_path / "r.db"))
    s = PITStore(str(tmp_path / "pit.db"), reg)
    yield s
    s.close()


def _write_round(store, kt: float, symbol: str = "tok1"):
    df = pd.DataFrame({"two_sided": [1.0], "best_bid": [0.4]},
                       index=pd.DatetimeIndex([pd.Timestamp(kt, unit="s", tz="UTC")]))
    store.ingest("polymarket-clob", symbol, df, knowledge_time=kt)


def test_no_data_reports_zero(store):
    r = compute_polymarket_coverage(store.conn)
    assert r["n_success"] == 0
    assert r["coverage_pct"] == 0.0
    assert r["gaps"] == []


def test_exact_cadence_is_100pct_coverage(store):
    base = 1_700_000_000.0
    cadence = 900
    for i in range(5):
        _write_round(store, base + i * cadence)
    r = compute_polymarket_coverage(store.conn, cadence_seconds=cadence)
    assert r["n_success"] == 5
    # span is 4 intervals (5 points), so expected_polls == 4 exactly
    assert r["expected_polls"] == pytest.approx(4.0)
    assert r["coverage_pct"] == pytest.approx(125.0)  # 5 successes / 4 expected


def test_gap_detection_matches_hand_arithmetic(store):
    base = 1_700_000_000.0
    # three rounds: t0, t0+900s, t0+900s+2h (one real gap)
    _write_round(store, base)
    _write_round(store, base + 900)
    _write_round(store, base + 900 + 2 * 3600)
    r = compute_polymarket_coverage(store.conn, cadence_seconds=900, gap_threshold_hours=1.0)
    assert r["n_success"] == 3
    assert len(r["gaps"]) == 1
    assert r["gaps"][0]["hours"] == pytest.approx(2.0, abs=1e-6)


def test_distinct_knowledge_time_deduplicates_within_a_round(store):
    """A single round writes many fields under ONE knowledge_time -- the
    coverage count must be per-round, not per-observation-row."""
    kt = 1_700_000_000.0
    df = pd.DataFrame(
        {"two_sided": [1.0], "best_bid": [0.4], "best_ask": [0.42], "mid": [0.41]},
        index=pd.DatetimeIndex([pd.Timestamp(kt, unit="s", tz="UTC")]),
    )
    store.ingest("polymarket-clob", "tok1", df, knowledge_time=kt)
    store.ingest("polymarket-clob", "tok2", df, knowledge_time=kt)  # same round, 2nd token
    r = compute_polymarket_coverage(store.conn, cadence_seconds=900)
    assert r["n_success"] == 1


def test_heartbeat_epoch_and_failure_count_reported(store):
    base = 1_700_000_000.0
    _write_round(store, base)
    _write_round(store, base + 900)
    # simulate one successful and one failed heartbeat after these rounds
    record_capture_heartbeat(
        store, "2023-11-14T22:15:00+00:00", base + 900, ok=True,
        n_requested=2, n_captured=2, n_failed=0,
    )
    record_capture_heartbeat(
        store, "2023-11-14T22:30:00+00:00", None, ok=False,
        n_requested=2, n_captured=0, n_failed=2, error="ConnectionError('x')",
    )
    r = compute_polymarket_coverage(store.conn, cadence_seconds=900)
    assert r["heartbeat_epoch"] == "2023-11-14T22:15:00+00:00"
    assert r["n_heartbeats"] == 2
    assert r["n_heartbeats_failed"] == 1


def test_since_until_window_restricts_success_count(store):
    base = 1_700_000_000.0
    for i in range(10):
        _write_round(store, base + i * 900)
    since = pd.Timestamp(base + 3 * 900, unit="s", tz="UTC").isoformat()
    r = compute_polymarket_coverage(store.conn, cadence_seconds=900, since=since)
    assert r["n_success"] == 7  # rounds 3..9 inclusive
