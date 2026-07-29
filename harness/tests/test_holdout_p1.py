"""Tests for the Amendment P-1 holdout regime (Validation Ruling 001).

Each test function is annotated with the acceptance-criterion ID(s) from
Ruling 001 §5 it covers; the mapping is also recorded in
``research/DATA-IMPL-001-p1-vault.md``.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from castellan import (
    TrialRegistry,
    PITStore,
    HoldoutVault,
    HoldoutError,
    HoldoutRegimeError,
    HoldoutAlreadySealedError,
    HoldoutSpecInvalidError,
    HoldoutSpecTamperedError,
    HoldoutRetiredError,
    HoldoutPassphraseError,
    HoldoutNotYetReachedError,
    HoldoutRetryUnauthorizedError,
    HoldoutAcquisitionFailedError,
    HoldoutSchemaMismatchError,
    HoldoutCeilingError,
    evaluate_gate1,
)
from castellan.holdout import VaultState

SCHEMA_FP = {"columns": ["close"], "dtypes": {"close": "float64"}}


def make_frame(start: str, days: int, seed: int = 1, tz=None) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    idx = pd.date_range(start, periods=days, freq="D", tz=tz)
    close = 100 + np.cumsum(rng.normal(0, 1, days))
    return pd.DataFrame({"close": close.astype("float64")}, index=idx)


def good_fetch(days=400, seed=1):
    """A fetch callable returning a >12-month, schema-matching frame
    starting the day after whatever cutoff the caller sealed."""

    def _fetch(spec):
        cutoff = pd.Timestamp(spec["cutoff"])
        start = (cutoff + pd.Timedelta(days=1)).tz_convert(None)
        return make_frame(start.isoformat(), days, seed=seed)

    return _fetch


class CountingFetch:
    """Wraps a fetch function and counts invocations, so tests can assert
    'no network call attempted' precisely."""

    def __init__(self, fn):
        self.fn = fn
        self.calls = 0

    def __call__(self, spec):
        self.calls += 1
        return self.fn(spec)


class FlakyFetch:
    """Fails `fail_times` times, then succeeds."""

    def __init__(self, fail_times: int, fn):
        self.fail_times = fail_times
        self.fn = fn
        self.calls = 0

    def __call__(self, spec):
        self.calls += 1
        if self.calls <= self.fail_times:
            raise RuntimeError(f"simulated transient failure #{self.calls}")
        return self.fn(spec)


@pytest.fixture
def registry(tmp_path):
    reg = TrialRegistry(str(tmp_path / "registry.db"))
    reg.open_hypothesis(
        family="famA",
        statement="A", mechanism="m", falsifier="f",
        universe="u", horizon="1d", success_criteria="sc", trial_budget=50,
    )
    reg.open_hypothesis(
        family="famB",
        statement="B", mechanism="m", falsifier="f",
        universe="u", horizon="1d", success_criteria="sc", trial_budget=50,
    )
    return reg


@pytest.fixture
def store(tmp_path, registry):
    return PITStore(str(tmp_path / "pit.db"), registry)


def make_vault(tmp_path, registry, store, name="v1", family="famA"):
    return HoldoutVault(str(tmp_path / f"vault-{name}"), registry, name, family, store=store)


def sealed_vault(tmp_path, registry, store, cutoff, name="v1", family="famA",
                  dataset_id="DATASET1", source="test-src"):
    v = make_vault(tmp_path, registry, store, name, family)
    v.seal(
        source=source, dataset_id=dataset_id,
        instrument_identity="cond-id-0001",
        query_semantics={"fields": ["close"], "freq": "1d"},
        cutoff=cutoff, schema_fingerprint=SCHEMA_FP,
    )
    return v


PAST_CUTOFF = pd.Timestamp("2020-01-01", tz="UTC")
FUTURE_CUTOFF = pd.Timestamp.now(tz="UTC") + pd.Timedelta(days=3650)


# ----------------------------------------------------------------------
# Group A — spec sealing (A1-A4)
# ----------------------------------------------------------------------

def test_A1_seal_writes_spec_and_sealed_event(tmp_path, registry, store):
    v = sealed_vault(tmp_path, registry, store, PAST_CUTOFF)
    assert v.is_sealed()
    events = [e for e in registry.events(kind="holdout_spec_sealed", family="famA")
              if e["detail"]["vault"] == "v1"]
    assert len(events) == 1
    assert events[0]["detail"]["spec_sha256"]
    spec = v.load_spec()
    assert spec["dataset_id"] == "DATASET1"
    assert spec["cutoff"] == PAST_CUTOFF.isoformat()


def test_A2_reseal_raises(tmp_path, registry, store):
    v = sealed_vault(tmp_path, registry, store, PAST_CUTOFF)
    with pytest.raises(HoldoutAlreadySealedError):
        v.seal(source="test-src", dataset_id="DATASET1",
               instrument_identity="cond-id-0001",
               query_semantics={"fields": ["close"]},
               cutoff=PAST_CUTOFF, schema_fingerprint=SCHEMA_FP)


def test_A3_future_cutoff_permitted(tmp_path, registry, store):
    v = sealed_vault(tmp_path, registry, store, FUTURE_CUTOFF)
    assert v.is_sealed()


@pytest.mark.parametrize("bad_field", ["dataset_id", "instrument_identity",
                                        "schema_fingerprint", "query_semantics"])
def test_A3_malformed_spec_raises(tmp_path, registry, store, bad_field):
    v = make_vault(tmp_path, registry, store)
    kwargs = dict(source="test-src", dataset_id="DATASET1",
                  instrument_identity="cond-id-0001",
                  query_semantics={"fields": ["close"]},
                  cutoff=PAST_CUTOFF, schema_fingerprint=SCHEMA_FP)
    kwargs[bad_field] = {} if isinstance(kwargs[bad_field], dict) else ""
    with pytest.raises(HoldoutSpecInvalidError):
        v.seal(**kwargs)


def test_A4_registry_hash_matches_disk(tmp_path, registry, store):
    v = sealed_vault(tmp_path, registry, store, PAST_CUTOFF)
    assert v._current_spec_sha256() == v._sealed_event()["detail"]["spec_sha256"]


# ----------------------------------------------------------------------
# Group B — ingest ceiling (B1-B6)
# ----------------------------------------------------------------------

def test_B1_ceiling_row_written_at_seal_time(tmp_path, registry, store):
    sealed_vault(tmp_path, registry, store, PAST_CUTOFF, dataset_id="DS-B1")
    ceilings = store._active_ceilings("test-src", "DS-B1")
    assert len(ceilings) == 1
    assert ceilings[0]["family"] == "famA"


def test_B2_ingest_accepts_at_or_before_cutoff(tmp_path, registry, store):
    cutoff = pd.Timestamp("2024-06-30", tz="UTC")
    sealed_vault(tmp_path, registry, store, cutoff, dataset_id="DS-B2")
    df = make_frame("2024-01-01", 181)  # ends 2024-06-30 exactly
    r = store.ingest("test-src", "DS-B2", df)
    assert r["new"] == 181


def test_B3_ingest_refuses_batch_atomically_and_logs(tmp_path, registry, store):
    cutoff = pd.Timestamp("2024-06-30", tz="UTC")
    sealed_vault(tmp_path, registry, store, cutoff, dataset_id="DS-B3")
    df = make_frame("2024-06-25", 10)  # crosses into 2024-07-04
    before = store.conn.execute("SELECT COUNT(*) FROM observations").fetchone()[0]
    with pytest.raises(HoldoutCeilingError):
        store.ingest("test-src", "DS-B3", df)
    after = store.conn.execute("SELECT COUNT(*) FROM observations").fetchone()[0]
    assert before == after  # atomic: nothing was ingested
    kinds = [e["kind"] for e in registry.events(family="famA")]
    assert "holdout_ceiling_violation" in kinds


def test_B4_non_ceilinged_dataset_unaffected(tmp_path, registry, store):
    df = make_frame("2030-01-01", 5)  # far future, no ceiling exists
    r = store.ingest("test-src", "UNCEILINGED", df)
    assert r["new"] == 5


def test_B5_direct_ceiling_mutation_raises(tmp_path, registry, store):
    sealed_vault(tmp_path, registry, store, PAST_CUTOFF, dataset_id="DS-B5")
    with pytest.raises(HoldoutCeilingError):
        store._lift_ceiling("test-src", "DS-B5", "famA", "bogus-hash-value")
    # ceiling is still active — the bad mutation attempt did not remove it
    assert store._active_ceilings("test-src", "DS-B5")


@pytest.mark.parametrize("tz_input", [None, "UTC"])
def test_B6_boundary_inclusive_at_cutoff(tmp_path, registry, store, tz_input):
    cutoff = pd.Timestamp("2024-06-30T00:00:00", tz="UTC")
    ds = f"DS-B6-{tz_input}"
    sealed_vault(tmp_path, registry, store, cutoff, dataset_id=ds)
    at_cutoff = make_frame("2024-06-30", 1, tz=tz_input)  # == C, in-sample
    r = store.ingest("test-src", ds, at_cutoff)
    assert r["new"] == 1
    one_second_over = pd.DataFrame(
        {"close": [101.0]},
        index=pd.DatetimeIndex([pd.Timestamp("2024-06-30T00:00:01", tz=tz_input or "UTC")]),
    )
    with pytest.raises(HoldoutCeilingError):
        store.ingest("test-src", ds, one_second_over)


# ----------------------------------------------------------------------
# Group C — acquisition (C1-C10)
# ----------------------------------------------------------------------

def test_C1_success_order_and_state(tmp_path, registry, store):
    v = sealed_vault(tmp_path, registry, store, PAST_CUTOFF, dataset_id="DS-C1")
    df = v.acquire_once("hunter2", good_fetch(), acquired_by="validation")
    assert len(df) == 400
    assert v.state == VaultState.RETIRED
    events = [e for e in registry.events(family="famA") if e["detail"].get("vault") == "v1"]
    kinds_in_order = [e["kind"] for e in events]
    assert kinds_in_order.index("holdout_acquisition_attempted") < kinds_in_order.index("holdout_acquired")


def test_C2_second_acquisition_retires(tmp_path, registry, store):
    v = sealed_vault(tmp_path, registry, store, PAST_CUTOFF, dataset_id="DS-C2")
    v.acquire_once("hunter2", good_fetch(), acquired_by="validation")
    with pytest.raises(HoldoutRetiredError):
        v.acquire_once("hunter2", good_fetch(), acquired_by="anyone")
    kinds = [e["kind"] for e in registry.events(family="famA")]
    assert "holdout_second_acquisition_attempt" in kinds


def test_C3_spec_tampered_no_network_call(tmp_path, registry, store):
    v = sealed_vault(tmp_path, registry, store, PAST_CUTOFF, dataset_id="DS-C3")
    with open(v._spec_path, "a") as fh:
        fh.write(" ")  # byte-level edit after sealing
    fetch = CountingFetch(good_fetch())
    with pytest.raises(HoldoutSpecTamperedError):
        v.acquire_once("hunter2", fetch, acquired_by="validation")
    assert fetch.calls == 0
    kinds = [e["kind"] for e in registry.events(family="famA")]
    assert "holdout_spec_tampered" in kinds


def test_C4_bad_passphrase_no_network_call_not_retired(tmp_path, registry, store):
    v = sealed_vault(tmp_path, registry, store, PAST_CUTOFF, dataset_id="DS-C4")
    fetch = CountingFetch(good_fetch())
    with pytest.raises(HoldoutPassphraseError):
        v.acquire_once("", fetch, acquired_by="validation")
    assert fetch.calls == 0
    assert not v.is_retired()
    kinds = [e["kind"] for e in registry.events(family="famA")]
    assert "holdout_bad_passphrase_attempt" in kinds
    # vault still acquirable afterwards
    df = v.acquire_once("hunter2", good_fetch(), acquired_by="validation")
    assert len(df) == 400


def test_C5_fetch_before_cutoff_raises(tmp_path, registry, store):
    v = sealed_vault(tmp_path, registry, store, FUTURE_CUTOFF, dataset_id="DS-C5")
    with pytest.raises(HoldoutNotYetReachedError):
        v.acquire_once("hunter2", good_fetch(), acquired_by="validation")
    kinds = [e["kind"] for e in registry.events(family="famA")]
    assert "holdout_acquisition_premature" in kinds


def test_C5_short_window_flagged_fail_not_insufficient(tmp_path, registry, store):
    v = sealed_vault(tmp_path, registry, store, PAST_CUTOFF, dataset_id="DS-C5b")
    v.acquire_once("hunter2", good_fetch(days=60), acquired_by="validation")
    rep = evaluate_gate1("s", "famA", registry, np.random.default_rng(1).normal(0.001, 0.01, 300), 252)
    holdout = next(c for c in rep.criteria if c.name == "Holdout single-use")
    assert holdout.verdict == "FAIL"
    assert holdout.verdict != "INSUFFICIENT-DATA"


def test_C6_failure_then_blocked_retry(tmp_path, registry, store):
    v = sealed_vault(tmp_path, registry, store, PAST_CUTOFF, dataset_id="DS-C6")
    fetch = FlakyFetch(1, good_fetch())
    with pytest.raises(HoldoutAcquisitionFailedError):
        v.acquire_once("hunter2", fetch, acquired_by="validation")
    assert v.state == VaultState.ACQUISITION_FAILED
    assert not v.is_retired()
    with pytest.raises(HoldoutRetryUnauthorizedError):
        v.acquire_once("hunter2", fetch, acquired_by="validation")
    kinds = [e["kind"] for e in registry.events(family="famA")]
    assert "holdout_acquisition_attempted" in kinds
    assert "holdout_acquisition_failed" in kinds


def test_C7_authorized_retry_succeeds_and_counted(tmp_path, registry, store):
    v = sealed_vault(tmp_path, registry, store, PAST_CUTOFF, dataset_id="DS-C7")
    fetch = FlakyFetch(1, good_fetch())
    with pytest.raises(HoldoutAcquisitionFailedError):
        v.acquire_once("hunter2", fetch, acquired_by="validation")
    v.authorize_retry("hunter2", reason="I-999 vendor 503, retried per Issue Log", authorized_by="cro")
    df = v.acquire_once("hunter2", fetch, acquired_by="validation")
    assert len(df) == 400
    assert v.state == VaultState.RETIRED
    rep = evaluate_gate1("s", "famA", registry, np.random.default_rng(1).normal(0.001, 0.01, 1300), 252)
    holdout = next(c for c in rep.criteria if c.name == "Holdout single-use")
    assert "1 retry authorization" in holdout.note


def test_C8_payload_encrypted_at_rest(tmp_path, registry, store):
    v = sealed_vault(tmp_path, registry, store, PAST_CUTOFF, dataset_id="DS-C8")
    marker = 918273.0

    def fetch(spec):
        df = good_fetch()(spec)
        df.iloc[0, 0] = marker
        return df

    v.acquire_once("hunter2", fetch, acquired_by="validation")
    with open(v._payload_path, "rb") as fh:
        raw = fh.read()
    assert str(marker).encode() not in raw
    assert b"918273" not in raw


def test_C9_read_acquired_wrong_passphrase_raises(tmp_path, registry, store):
    v = sealed_vault(tmp_path, registry, store, PAST_CUTOFF, dataset_id="DS-C9")
    v.acquire_once("hunter2", good_fetch(), acquired_by="validation")
    with pytest.raises(HoldoutPassphraseError):
        v.read_acquired("wrong-passphrase")
    df = v.read_acquired("hunter2")
    assert len(df) == 400


def test_C10_schema_mismatch_treated_as_failure(tmp_path, registry, store):
    v = sealed_vault(tmp_path, registry, store, PAST_CUTOFF, dataset_id="DS-C10")

    def bad_fetch(spec):
        df = good_fetch()(spec)
        df["extra_col"] = 1.0
        return df

    with pytest.raises(HoldoutSchemaMismatchError):
        v.acquire_once("hunter2", bad_fetch, acquired_by="validation")
    assert v.state == VaultState.ACQUISITION_FAILED
    assert not v.is_retired()
    with pytest.raises(HoldoutRetryUnauthorizedError):
        v.acquire_once("hunter2", bad_fetch, acquired_by="validation")


# ----------------------------------------------------------------------
# Group D — leak detection (D1-D2)
# ----------------------------------------------------------------------

def test_D1_pre_acquisition_leak_fails_gate(tmp_path, registry, store):
    cutoff = pd.Timestamp("2024-06-30", tz="UTC")
    # Ingest data spanning into what will become the holdout window,
    # BEFORE the vault seals a ceiling on this dataset — models the case
    # where a universe pull already had these rows before Gate 0.
    leaky = make_frame("2024-06-01", 60)  # runs through 2024-07-30
    store.ingest("test-src", "DS-D1", leaky, knowledge_time=1_000.0)
    v = sealed_vault(tmp_path, registry, store, cutoff, dataset_id="DS-D1")
    v.acquire_once("hunter2", good_fetch(days=400), acquired_by="validation")
    kinds = [e["kind"] for e in registry.events(family="famA")]
    assert "holdout_pre_acquisition_leak" in kinds
    rep = evaluate_gate1("s", "famA", registry, np.random.default_rng(1).normal(0.001, 0.01, 1300), 252)
    holdout = next(c for c in rep.criteria if c.name == "Holdout single-use")
    assert holdout.verdict == "FAIL"


def test_D2_clean_case_no_leak(tmp_path, registry, store):
    v = sealed_vault(tmp_path, registry, store, PAST_CUTOFF, dataset_id="DS-D2")
    v.acquire_once("hunter2", good_fetch(), acquired_by="validation")
    kinds = [e["kind"] for e in registry.events(family="famA")]
    assert "holdout_pre_acquisition_leak" not in kinds
    rep = evaluate_gate1("s", "famA", registry, np.random.default_rng(1).normal(0.001, 0.01, 1300), 252)
    holdout = next(c for c in rep.criteria if c.name == "Holdout single-use")
    assert holdout.verdict != "FAIL"


# ----------------------------------------------------------------------
# Group E — Gate integration (E1-E3; fixes I-007)
# ----------------------------------------------------------------------

def test_E1_second_acquisition_violation_does_not_fail_other_family(tmp_path, registry, store):
    va = sealed_vault(tmp_path, registry, store, PAST_CUTOFF, name="va", family="famA", dataset_id="DS-E1A")
    vb = sealed_vault(tmp_path, registry, store, PAST_CUTOFF, name="vb", family="famB", dataset_id="DS-E1B")
    va.acquire_once("hunter2", good_fetch(), acquired_by="validation")
    with pytest.raises(HoldoutRetiredError):
        va.acquire_once("hunter2", good_fetch(), acquired_by="validation")  # family A violation

    vb.acquire_once("hunter2", good_fetch(), acquired_by="validation")  # family B clean

    rep_a = evaluate_gate1("a", "famA", registry, np.random.default_rng(1).normal(0.001, 0.01, 1300), 252)
    rep_b = evaluate_gate1("b", "famB", registry, np.random.default_rng(2).normal(0.001, 0.01, 1300), 252)
    holdout_a = next(c for c in rep_a.criteria if c.name == "Holdout single-use")
    holdout_b = next(c for c in rep_b.criteria if c.name == "Holdout single-use")
    assert holdout_a.verdict == "FAIL"          # A's own violation fails A
    assert holdout_b.verdict != "FAIL"          # B is unaffected by A's violation (I-007 fix)


def test_E1_acquisition_on_one_family_does_not_satisfy_another(tmp_path, registry, store):
    va = sealed_vault(tmp_path, registry, store, PAST_CUTOFF, name="va2", family="famA", dataset_id="DS-E1C")
    sealed_vault(tmp_path, registry, store, PAST_CUTOFF, name="vb2", family="famB", dataset_id="DS-E1D")
    va.acquire_once("hunter2", good_fetch(), acquired_by="validation")  # only family A acquires

    rep_b = evaluate_gate1("b", "famB", registry, np.random.default_rng(3).normal(0.001, 0.01, 1300), 252)
    holdout_b = next(c for c in rep_b.criteria if c.name == "Holdout single-use")
    assert holdout_b.verdict == "INSUFFICIENT-DATA"  # not satisfied by family A's acquisition


def test_E2_no_acquisition_is_insufficient_never_pass(tmp_path, registry):
    reg = registry
    rep = evaluate_gate1("s", "famA", reg, np.random.default_rng(1).normal(0.001, 0.01, 1300), 252)
    holdout = next(c for c in rep.criteria if c.name == "Holdout single-use")
    assert holdout.verdict == "INSUFFICIENT-DATA"
    assert rep.overall != "PASS"


def test_E3_report_embeds_holdout_hashes(tmp_path, registry, store):
    v = sealed_vault(tmp_path, registry, store, PAST_CUTOFF, dataset_id="DS-E3")
    v.acquire_once("hunter2", good_fetch(), acquired_by="validation")
    rep = evaluate_gate1("s", "famA", registry, np.random.default_rng(1).normal(0.001, 0.01, 1300), 252)
    assert rep.holdout_spec_sha256 == v._sealed_event()["detail"]["spec_sha256"]
    assert rep.holdout_payload_sha256 is not None and len(rep.holdout_payload_sha256) == 64
    assert rep.holdout_spec_sha256[:16] in rep.to_markdown()


# ----------------------------------------------------------------------
# Group F — migration and anti-erosion (F1, F4; F2/F3 covered elsewhere)
# ----------------------------------------------------------------------

def test_F1_legacy_lock_and_open_once_hard_raise(tmp_path, registry, store):
    v = make_vault(tmp_path, registry, store, name="legacy")
    with pytest.raises(HoldoutRegimeError):
        v.lock(make_frame("2024-01-01", 10), passphrase="x")
    with pytest.raises(HoldoutRegimeError):
        v.open_once("x", opened_by="anyone")


def test_F4_predecessor_family_n_starts_at_predecessor_total(tmp_path):
    from castellan import run_backtest, US_EQUITY_LARGE

    reg = TrialRegistry(str(tmp_path / "r.db"))
    reg.open_hypothesis("gen1", "s", "m", "f", "u", "1d", "sc", 50)
    rng = np.random.default_rng(1)
    idx = pd.bdate_range("2020-01-01", periods=300)
    prices = pd.DataFrame(100 * np.exp(np.cumsum(rng.normal(0, 0.01, (300, 2)), axis=0)),
                           index=idx, columns=["A", "B"])
    w = prices * 0.0 + 0.1
    for k in range(4):
        run_backtest(prices, w, US_EQUITY_LARGE, reg, "gen1", {"v": k})
    assert reg.family_stats("gen1").n_trials == 4

    with pytest.raises(ValueError):
        reg.open_hypothesis("orphan", "s", "m", "f", "u", "1d", "sc", 50,
                            predecessor_family="does-not-exist")

    reg.open_hypothesis("gen2", "s2", "m", "f", "u", "1d", "sc", 50,
                        predecessor_family="gen1")
    assert reg.family_stats("gen2").n_trials == 4  # starts at predecessor's total, not 0
    run_backtest(prices, w, US_EQUITY_LARGE, reg, "gen2", {"v": "new"})
    assert reg.family_stats("gen2").n_trials == 5
    assert reg.family_stats("gen1").n_trials == 4  # predecessor's own count is untouched
    assert reg.predecessor_chain("gen2") == ["gen1"]
