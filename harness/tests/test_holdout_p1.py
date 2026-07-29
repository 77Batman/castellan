"""Tests for the Amendment P-1 holdout regime (Validation Ruling 001).

Each test function is annotated with the acceptance-criterion ID(s) from
Ruling 001 §5 it covers; the mapping is also recorded in
``research/DATA-IMPL-001-p1-vault.md``.
"""

from __future__ import annotations

import io
import time

import numpy as np
import pandas as pd
import pytest

from castellan import (
    TrialRegistry,
    PreRegistrationAmendedError,
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
    HoldoutAcquisitionOverlapError,
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
                  dataset_id="DATASET1", source="test-src", passphrase="hunter2"):
    v = make_vault(tmp_path, registry, store, name, family)
    v.seal(
        source=source, dataset_id=dataset_id,
        instrument_identity="cond-id-0001",
        query_semantics={"fields": ["close"], "freq": "1d"},
        cutoff=cutoff, schema_fingerprint=SCHEMA_FP,
        passphrase=passphrase,
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
               cutoff=PAST_CUTOFF, schema_fingerprint=SCHEMA_FP,
               passphrase="hunter2")


def test_A3_future_cutoff_permitted(tmp_path, registry, store):
    v = sealed_vault(tmp_path, registry, store, FUTURE_CUTOFF)
    assert v.is_sealed()


@pytest.mark.parametrize("bad_field", ["source", "dataset_id", "instrument_identity",
                                        "schema_fingerprint", "query_semantics"])
def test_A3_malformed_spec_raises(tmp_path, registry, store, bad_field):
    """C-10 (Acceptance 001 §3): 'source' was enforced in code (it's in
    seal()'s own `required` dict) but never exercised by this
    parametrization — added here, alongside the pre-existing four."""
    v = make_vault(tmp_path, registry, store)
    kwargs = dict(source="test-src", dataset_id="DATASET1",
                  instrument_identity="cond-id-0001",
                  query_semantics={"fields": ["close"]},
                  cutoff=PAST_CUTOFF, schema_fingerprint=SCHEMA_FP,
                  passphrase="hunter2")
    kwargs[bad_field] = {} if isinstance(kwargs[bad_field], dict) else ""
    with pytest.raises(HoldoutSpecInvalidError):
        v.seal(**kwargs)


def test_A3_malformed_cutoff_raises(tmp_path, registry, store):
    """C-10: the malformed-cutoff branch (``except Exception`` around
    ``_to_utc(cutoff)`` in ``seal()``) was dead code — never exercised by
    any test — until now."""
    v = make_vault(tmp_path, registry, store, name="badcutoff")
    with pytest.raises(HoldoutSpecInvalidError):
        v.seal(source="test-src", dataset_id="DATASET1",
               instrument_identity="cond-id-0001",
               query_semantics={"fields": ["close"]},
               cutoff="not-a-timestamp-at-all",
               schema_fingerprint=SCHEMA_FP, passphrase="hunter2")
    assert not v.is_sealed()


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
    rep = evaluate_gate1("s", "famA", registry, np.random.default_rng(1).normal(0.001, 0.01, 300), 252, backtest_years=1.1905)
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
    rep = evaluate_gate1("s", "famA", registry, np.random.default_rng(1).normal(0.001, 0.01, 1300), 252, backtest_years=5.1587)
    holdout = next(c for c in rep.criteria if c.name == "Holdout single-use")
    assert "1 retry authorization" in holdout.note


def test_C8_payload_encrypted_at_rest(tmp_path, registry, store):
    """C-8 (Acceptance 001 §3): the original assertions could not fail —
    they checked that two specific numeric strings were absent from
    ``payload.enc``, but an UNENCRYPTED parquet of the same frame also
    lacks those strings (parquet stores doubles as binary, not ASCII), so
    the test passed identically against plaintext. Strengthened to a
    property that is actually falsifiable: capture what the genuine
    plaintext parquet bytes ARE, then assert the on-disk payload differs
    from them structurally (not just "doesn't contain one string") and
    cannot itself be parsed as parquet — i.e. it is not, and does not
    start with, plaintext parquet. If encryption were silently removed,
    every one of these assertions would fail."""
    v = sealed_vault(tmp_path, registry, store, PAST_CUTOFF, dataset_id="DS-C8")
    captured = {}

    def fetch(spec):
        df = good_fetch()(spec)
        buf = io.BytesIO()
        df.to_parquet(buf)
        captured["plaintext_parquet"] = buf.getvalue()
        captured["df"] = df
        return df

    v.acquire_once("hunter2", fetch, acquired_by="validation")
    with open(v._payload_path, "rb") as fh:
        raw = fh.read()
    plaintext_parquet = captured["plaintext_parquet"]

    assert raw != plaintext_parquet
    # Parquet files begin (and end) with the magic bytes "PAR1"; genuine
    # ciphertext must not.
    assert not raw.startswith(b"PAR1")
    assert plaintext_parquet.startswith(b"PAR1")  # sanity: the fixture itself IS parquet
    with pytest.raises(Exception):
        pd.read_parquet(io.BytesIO(raw))  # ciphertext does not parse as parquet
    # and the correct passphrase recovers exactly the original frame
    recovered = v.read_acquired("hunter2")
    pd.testing.assert_frame_equal(recovered, captured["df"], check_freq=False)


def test_ACC_C9_ceiling_records_which_acquisition_lifted_it(tmp_path, registry, store):
    v = sealed_vault(tmp_path, registry, store, PAST_CUTOFF, dataset_id="DS-ACCC9")
    v.acquire_once("hunter2", good_fetch(), acquired_by="validation")
    row = store.conn.execute(
        "SELECT active, lifted_utc, lifted_by_event_id FROM ingest_ceiling "
        "WHERE source=? AND dataset_id=? AND family=?",
        ("test-src", "DS-ACCC9", "famA"),
    ).fetchone()
    assert row[0] == 0  # inactive
    assert row[1] is not None and row[1] > 0  # lifted_utc recorded
    acquired_event = registry.events(kind="holdout_acquired", family="famA")[-1]
    assert row[2] == acquired_event["event_id"]  # WHICH acquisition, not just active=0


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
# Group ACC — Validation Acceptance 001 blocking conditions C-2..C-7.
# Numbered ``ACC_C-n`` (not ``Cn``) to avoid colliding with Ruling 001's
# own C1-C10 test names above, several of which are DIFFERENT criteria
# that happen to share a digit (Ruling 001's C7 is "authorized retry
# succeeds"; Acceptance 001's C-7 is the acquisition-side non-overlap
# enforcement below — unrelated properties, same numeral, different
# documents).
# ----------------------------------------------------------------------

def test_ACC_C2_wrong_nonempty_passphrase_refused_not_retired(tmp_path, registry, store):
    """I-015 regression, verbatim: a TYPO (non-empty, wrong) passphrase
    must be refused before any fetch, must NOT seal a payload, must NOT
    retire the vault, and the vault must remain acquirable with the
    correct passphrase afterwards. This is the exact scenario the
    presence-only check let through — the test that claimed to cover C4
    before only tried the empty string."""
    v = sealed_vault(tmp_path, registry, store, PAST_CUTOFF, dataset_id="DS-ACCC2a",
                      passphrase="hunter2")
    fetch = CountingFetch(good_fetch())
    with pytest.raises(HoldoutPassphraseError):
        v.acquire_once("hunter2-TYPO", fetch, acquired_by="validation")
    assert fetch.calls == 0
    assert not v.is_retired()
    assert v.state == VaultState.SEALED
    kinds = [e["kind"] for e in registry.events(family="famA")]
    assert "holdout_bad_passphrase_attempt" in kinds


def test_ACC_C2_correct_passphrase_recovers_after_wrong_attempt(tmp_path, registry, store):
    v = sealed_vault(tmp_path, registry, store, PAST_CUTOFF, dataset_id="DS-ACCC2b",
                      passphrase="hunter2")
    with pytest.raises(HoldoutPassphraseError):
        v.acquire_once("wrong-guess", good_fetch(), acquired_by="validation")
    df = v.acquire_once("hunter2", good_fetch(), acquired_by="validation")
    assert len(df) == 400
    assert v.state == VaultState.RETIRED
    # and the payload decrypts with the real passphrase, unharmed
    assert len(v.read_acquired("hunter2")) == 400


def test_ACC_C2_seal_requires_nonempty_passphrase(tmp_path, registry, store):
    v = make_vault(tmp_path, registry, store, name="noseal")
    with pytest.raises(HoldoutPassphraseError):
        v.seal(source="test-src", dataset_id="DATASET1",
               instrument_identity="cond-id-0001",
               query_semantics={"fields": ["close"]},
               cutoff=PAST_CUTOFF, schema_fingerprint=SCHEMA_FP,
               passphrase="")
    assert not v.is_sealed()


def test_ACC_C2_authorize_retry_requires_correct_passphrase(tmp_path, registry, store):
    """Re-audit finding (see the deliverable note): `authorize_retry` had
    the identical presence-only defect shape C4 had before this sprint —
    just with a smaller blast radius, since a bad retry-authorization
    doesn't seal or retire anything. Fixed the same way (cryptographic
    check against the seal-time verifier); asserted here directly, since
    nothing previously exercised the wrong-passphrase branch of this
    specific method."""
    v = sealed_vault(tmp_path, registry, store, PAST_CUTOFF, dataset_id="DS-ACCC2c",
                      passphrase="hunter2")
    fetch = FlakyFetch(1, good_fetch())
    with pytest.raises(HoldoutAcquisitionFailedError):
        v.acquire_once("hunter2", fetch, acquired_by="validation")
    assert v.state == VaultState.ACQUISITION_FAILED
    with pytest.raises(HoldoutPassphraseError):
        v.authorize_retry("wrong-guess", reason="I-999 vendor 503", authorized_by="cro")
    # the bad attempt did NOT authorize anything: still blocked
    with pytest.raises(HoldoutRetryUnauthorizedError):
        v.acquire_once("hunter2", fetch, acquired_by="validation")
    kinds = [e["kind"] for e in registry.events(family="famA")]
    assert "holdout_retry_authorized" not in kinds
    # the correct passphrase does authorize it
    v.authorize_retry("hunter2", reason="I-999 vendor 503, retried per Issue Log",
                      authorized_by="cro")
    df = v.acquire_once("hunter2", fetch, acquired_by="validation")
    assert len(df) == 400


def test_ACC_C3_store_required_at_construction(tmp_path, registry):
    with pytest.raises(HoldoutSpecInvalidError):
        HoldoutVault(str(tmp_path / "vault-nostore"), registry, "nostore", "famA", None)


def test_ACC_C3_store_required_at_seal(tmp_path, registry, store):
    v = make_vault(tmp_path, registry, store, name="storeremoved")
    v.store = None  # simulate a caller that bypassed the constructor guard
    with pytest.raises(HoldoutSpecInvalidError):
        v.seal(source="test-src", dataset_id="DATASET1",
               instrument_identity="cond-id-0001",
               query_semantics={"fields": ["close"]},
               cutoff=PAST_CUTOFF, schema_fingerprint=SCHEMA_FP,
               passphrase="hunter2")
    assert not v.is_sealed()


def test_ACC_C4_ingest_documents_accepts_at_or_before_cutoff(tmp_path, registry, store):
    cutoff = pd.Timestamp("2024-06-30", tz="UTC")
    sealed_vault(tmp_path, registry, store, cutoff, dataset_id="DS-ACCC4a")
    docs = [{"doc_type": "8-K", "event_time": "2024-06-30", "ref": "doc-1", "meta": {}}]
    n = store.ingest_documents("test-src", "DS-ACCC4a", docs)
    assert n == 1


def test_ACC_C4_ingest_documents_enforces_ceiling(tmp_path, registry, store):
    cutoff = pd.Timestamp("2024-06-30", tz="UTC")
    sealed_vault(tmp_path, registry, store, cutoff, dataset_id="DS-ACCC4b")
    before = store.conn.execute("SELECT COUNT(*) FROM documents").fetchone()[0]
    docs = [
        {"doc_type": "8-K", "event_time": "2024-06-25", "ref": "doc-ok", "meta": {}},
        {"doc_type": "8-K", "event_time": "2024-07-04", "ref": "doc-over", "meta": {}},
    ]
    with pytest.raises(HoldoutCeilingError):
        store.ingest_documents("test-src", "DS-ACCC4b", docs)
    after = store.conn.execute("SELECT COUNT(*) FROM documents").fetchone()[0]
    assert before == after  # atomic: neither doc was inserted, including the compliant one
    kinds = [e["kind"] for e in registry.events(family="famA")]
    assert "holdout_ceiling_violation" in kinds


def test_ACC_C5_event_time_normalized_to_utc_at_ingest(tmp_path, registry, store):
    df = pd.DataFrame(
        {"close": [101.0]},
        index=pd.DatetimeIndex([pd.Timestamp("2024-06-30T21:00:00", tz="America/New_York")]),
    )
    store.ingest("test-src", "DS-ACCC5", df)
    row = store.conn.execute(
        "SELECT event_time FROM observations WHERE source=? AND symbol=?",
        ("test-src", "DS-ACCC5"),
    ).fetchone()
    assert row[0] == "2024-07-01T01:00:00+00:00"  # UTC, not the caller's -04:00 offset


def test_ACC_C5_leak_detector_catches_nonutc_timezone_leak(tmp_path, registry, store):
    """The measured false negative from Acceptance 001 §3 (D1/I-016):
    a bar at America/New_York 21:00 (= 2024-07-01T01:00Z) falling inside a
    holdout opening at C=2024-07-01T00:00Z must now be caught by
    rows_in_window, not missed by a string comparison against a
    caller-offset timestamp."""
    leaky = pd.DataFrame(
        {"close": [101.0]},
        index=pd.DatetimeIndex([pd.Timestamp("2024-06-30T21:00:00", tz="America/New_York")]),
    )
    store.ingest("test-src", "DS-ACCC5b", leaky, knowledge_time=1_000.0)
    cutoff = pd.Timestamp("2024-07-01T00:00:00", tz="UTC")
    leaked = store.rows_in_window(
        "test-src", "DS-ACCC5b", cutoff, cutoff + pd.Timedelta(days=1),
        knowledge_time_before=2_000.0,
    )
    assert len(leaked) == 1  # previously 0 — the measured false negative


def test_ACC_C7_acquisition_refuses_row_at_or_before_cutoff(tmp_path, registry, store):
    """R-F1/F2-4: the acquisition-side half of the legacy test's
    load-bearing property (`held.index[0] > insample.index[-1]`),
    enforced in CODE, not merely asserted. A fetch() that returns rows at
    or before C — e.g. a buggy venue client that hands back the in-sample
    history instead of the holdout — must be refused, not sealed as "the
    holdout"."""
    cutoff = pd.Timestamp("2024-06-30", tz="UTC")
    v = sealed_vault(tmp_path, registry, store, cutoff, dataset_id="DS-ACCC7a")

    def overlapping_fetch(spec):
        # Returns the tail of the IN-SAMPLE period (ends exactly at C),
        # not the holdout — exactly Acceptance 001's measured probe.
        return make_frame("2018-01-01", 2000)  # runs through ~2023-05, all <= C

    with pytest.raises(HoldoutAcquisitionOverlapError):
        v.acquire_once("hunter2", overlapping_fetch, acquired_by="validation")
    assert v.state == VaultState.ACQUISITION_FAILED
    assert not v.is_retired()
    kinds = [e["kind"] for e in registry.events(family="famA")]
    assert "holdout_acquisition_failed" in kinds
    assert "holdout_acquired" not in kinds
    # not bricked: a further attempt after authorization succeeds normally
    v.authorize_retry("hunter2", reason="I-999 bad fetch, corrected", authorized_by="cro")
    df = v.acquire_once("hunter2", good_fetch(), acquired_by="validation")
    assert df.index.min() > cutoff.tz_convert(None)


def test_ACC_C7_acquired_index_min_strictly_after_cutoff(tmp_path, registry, store):
    cutoff = pd.Timestamp("2024-06-30", tz="UTC")
    v = sealed_vault(tmp_path, registry, store, cutoff, dataset_id="DS-ACCC7b")
    df = v.acquire_once("hunter2", good_fetch(), acquired_by="validation")
    # the successor of the legacy test's property 3; df.index is tz-naive
    # (as fetch() returns it), so compare in the same convention.
    assert df.index.min() > cutoff.tz_convert(None)


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
    rep = evaluate_gate1("s", "famA", registry, np.random.default_rng(1).normal(0.001, 0.01, 1300), 252, backtest_years=5.1587)
    holdout = next(c for c in rep.criteria if c.name == "Holdout single-use")
    assert holdout.verdict == "FAIL"


def test_D2_clean_case_no_leak(tmp_path, registry, store):
    v = sealed_vault(tmp_path, registry, store, PAST_CUTOFF, dataset_id="DS-D2")
    v.acquire_once("hunter2", good_fetch(), acquired_by="validation")
    kinds = [e["kind"] for e in registry.events(family="famA")]
    assert "holdout_pre_acquisition_leak" not in kinds
    rep = evaluate_gate1("s", "famA", registry, np.random.default_rng(1).normal(0.001, 0.01, 1300), 252, backtest_years=5.1587)
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

    rep_a = evaluate_gate1("a", "famA", registry, np.random.default_rng(1).normal(0.001, 0.01, 1300), 252, backtest_years=5.1587)
    rep_b = evaluate_gate1("b", "famB", registry, np.random.default_rng(2).normal(0.001, 0.01, 1300), 252, backtest_years=5.1587)
    holdout_a = next(c for c in rep_a.criteria if c.name == "Holdout single-use")
    holdout_b = next(c for c in rep_b.criteria if c.name == "Holdout single-use")
    assert holdout_a.verdict == "FAIL"          # A's own violation fails A
    assert holdout_b.verdict != "FAIL"          # B is unaffected by A's violation (I-007 fix)


def test_E1_acquisition_on_one_family_does_not_satisfy_another(tmp_path, registry, store):
    va = sealed_vault(tmp_path, registry, store, PAST_CUTOFF, name="va2", family="famA", dataset_id="DS-E1C")
    sealed_vault(tmp_path, registry, store, PAST_CUTOFF, name="vb2", family="famB", dataset_id="DS-E1D")
    va.acquire_once("hunter2", good_fetch(), acquired_by="validation")  # only family A acquires

    rep_b = evaluate_gate1("b", "famB", registry, np.random.default_rng(3).normal(0.001, 0.01, 1300), 252, backtest_years=5.1587)
    holdout_b = next(c for c in rep_b.criteria if c.name == "Holdout single-use")
    assert holdout_b.verdict == "INSUFFICIENT-DATA"  # not satisfied by family A's acquisition


def test_E2_no_acquisition_is_insufficient_never_pass(tmp_path, registry):
    reg = registry
    rep = evaluate_gate1("s", "famA", reg, np.random.default_rng(1).normal(0.001, 0.01, 1300), 252, backtest_years=5.1587)
    holdout = next(c for c in rep.criteria if c.name == "Holdout single-use")
    assert holdout.verdict == "INSUFFICIENT-DATA"
    assert rep.overall != "PASS"


def test_E3_report_embeds_holdout_hashes(tmp_path, registry, store):
    v = sealed_vault(tmp_path, registry, store, PAST_CUTOFF, dataset_id="DS-E3")
    v.acquire_once("hunter2", good_fetch(), acquired_by="validation")
    rep = evaluate_gate1("s", "famA", registry, np.random.default_rng(1).normal(0.001, 0.01, 1300), 252, backtest_years=5.1587)
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


# ----------------------------------------------------------------------
# Group G — I-010: backtest_years / oos_index (Ruling Acceptance 001 §6)
# ----------------------------------------------------------------------

def test_G1_backtest_years_is_required(tmp_path, registry):
    with pytest.raises(TypeError):
        evaluate_gate1("s", "famA", registry,
                       np.random.default_rng(1).normal(0.001, 0.01, 300), 252)


def test_G2_oos_index_calendar_span_used_and_reported(tmp_path, registry):
    idx = pd.bdate_range("2018-01-01", periods=1300)
    years_calendar = (idx.max() - idx.min()).days / 365.25
    r = np.random.default_rng(1).normal(0.001, 0.01, 1300)
    rep = evaluate_gate1("s", "famA", registry, r, 252,
                         backtest_years=years_calendar, oos_index=idx)
    crit = next(c for c in rep.criteria if c.name == "Backtest length (years)")
    assert crit.verdict != "INSUFFICIENT-DATA"
    assert "DISAGREEMENT" not in (crit.note or "")
    assert abs(crit.value - years_calendar) < 1e-6


def test_G3_disagreement_over_5pct_fails_with_both_numbers(tmp_path, registry):
    idx = pd.bdate_range("2018-01-01", periods=1300)
    years_calendar = (idx.max() - idx.min()).days / 365.25
    r = np.random.default_rng(1).normal(0.001, 0.01, 1300)
    misleading_years = years_calendar * 2.0  # far more than 5% off
    rep = evaluate_gate1("s", "famA", registry, r, 252,
                         backtest_years=misleading_years, oos_index=idx)
    crit = next(c for c in rep.criteria if c.name == "Backtest length (years)")
    assert crit.verdict == "FAIL"
    assert "DISAGREEMENT" in crit.note
    assert f"{misleading_years:.3f}" in crit.note
    assert f"{years_calendar:.3f}" in crit.note


def test_G4_no_oos_index_is_insufficient_never_pass(tmp_path, registry):
    r = np.random.default_rng(1).normal(0.001, 0.01, 1300)
    # backtest_years claims an ample 100 years — must not matter.
    rep = evaluate_gate1("s", "famA", registry, r, 252, backtest_years=100.0)
    crit = next(c for c in rep.criteria if c.name == "Backtest length (years)")
    assert crit.verdict == "INSUFFICIENT-DATA"
    assert rep.overall != "PASS"


def test_G5_pooled_panel_apparent_length_overstated_fails(tmp_path, registry):
    """The I-010 case exactly: 1500 rows at periods_per_year=252 looks like
    ~5.95 apparent years by observation count, but the rows are stacked
    contract-days spanning only ~18 calendar months. Under the deleted
    fallback this read as clearing the Charter 4.4 4-year floor; now it
    must FAIL on disagreement."""
    n = 1500
    apparent_years = n / 252  # what the deleted fallback would have computed
    months = pd.date_range("2024-01-01", periods=18, freq="MS")
    idx = pd.DatetimeIndex(np.tile(months.values, n // len(months) + 1)[:n])
    r = np.random.default_rng(1).normal(0.001, 0.01, n)
    rep = evaluate_gate1("s", "famA", registry, r, 252,
                         backtest_years=apparent_years, oos_index=idx)
    crit = next(c for c in rep.criteria if c.name == "Backtest length (years)")
    assert crit.verdict == "FAIL"
    assert "DISAGREEMENT" in crit.note


# ----------------------------------------------------------------------
# Group P — pre-registration sealing (Acceptance 001 §5 P1-P8; I-018)
# ----------------------------------------------------------------------

def test_P1_seal_writes_hash_and_full_field_copy(tmp_path):
    reg = TrialRegistry(str(tmp_path / "r.db"))
    reg.open_hypothesis("famP1", "stmt", "mech", "fals", "uni", "1d", "sc", 10)
    events = reg.events(kind="hypothesis_sealed", family="famP1")
    assert len(events) == 1
    detail = events[0]["detail"]
    assert detail["prereg_sha256"]
    assert detail["statement"] == "stmt"
    assert detail["falsifier"] == "fals"
    v = reg.verify_prereg("famP1")
    assert v["sealed"] and v["match"]


def test_P3_amendment_refused_and_named(tmp_path):
    reg = TrialRegistry(str(tmp_path / "r.db"))
    reg.open_hypothesis("famP3", "stmt", "mech", "fals", "uni", "1d", "sc", 10)
    with pytest.raises(PreRegistrationAmendedError):
        reg.open_hypothesis("famP3", "DIFFERENT STATEMENT", "mech", "fals",
                            "uni", "1d", "sc", 10)
    events = reg.events(kind="hypothesis_amendment_refused", family="famP3")
    assert len(events) == 1
    assert "statement" in events[0]["detail"]["differing_fields"]
    # the row itself was NOT changed
    assert reg.hypothesis("famP3")["statement"] == "stmt"


def test_P3_byte_identical_reregistration_is_idempotent_no_event(tmp_path):
    reg = TrialRegistry(str(tmp_path / "r.db"))
    reg.open_hypothesis("famP3b", "stmt", "mech", "fals", "uni", "1d", "sc", 10)
    reg.open_hypothesis("famP3b", "stmt", "mech", "fals", "uni", "1d", "sc", 10)  # identical
    assert reg.events(kind="hypothesis_amendment_refused", family="famP3b") == []
    sealed_events = reg.events(kind="hypothesis_sealed", family="famP3b")
    assert len(sealed_events) == 1  # not re-sealed


def test_P4_raw_sql_update_detected_and_fails_gate(tmp_path):
    reg = TrialRegistry(str(tmp_path / "r.db"))
    reg.open_hypothesis("famP4", "stmt", "mech", "original falsifier",
                        "uni", "1d", "sc", 10)
    reg.conn.execute("UPDATE hypotheses SET falsifier=? WHERE family=?",
                     ("TAMPERED", "famP4"))
    reg.conn.commit()
    v = reg.verify_prereg("famP4")
    assert v["match"] is False
    assert "falsifier" in v["differing_fields"]
    rep = evaluate_gate1("s", "famP4", reg,
                         np.random.default_rng(1).normal(0.001, 0.01, 1300), 252,
                         backtest_years=1300 / 252)
    crit = next(c for c in rep.criteria if c.name == "Pre-registration integrity")
    assert crit.verdict == "FAIL"
    assert rep.overall == "FAIL"


def test_P5_report_embeds_prereg_hash(tmp_path):
    reg = TrialRegistry(str(tmp_path / "r.db"))
    reg.open_hypothesis("famP5", "stmt", "mech", "fals", "uni", "1d", "sc", 10)
    rep = evaluate_gate1("s", "famP5", reg,
                         np.random.default_rng(1).normal(0.001, 0.01, 1300), 252,
                         backtest_years=1300 / 252)
    assert rep.prereg_sha256 == reg.verify_prereg("famP5")["sealed_sha256"]
    assert rep.prereg_sha256[:16] in rep.to_markdown()


def test_P6_unsealed_family_is_insufficient_never_pass(tmp_path):
    reg = TrialRegistry(str(tmp_path / "r.db"))
    # Bypass open_hypothesis entirely — models a family that predates the
    # P-series schema (a raw row with no hypothesis_sealed event).
    reg.conn.execute(
        "INSERT INTO hypotheses (family, statement, mechanism, falsifier, "
        "universe, horizon, success_criteria, trial_budget, created_utc) "
        "VALUES (?,?,?,?,?,?,?,?,?)",
        ("famP6", "s", "m", "f", "u", "1d", "sc", 10, time.time()),
    )
    reg.conn.commit()
    v = reg.verify_prereg("famP6")
    assert v["sealed"] is False
    rep = evaluate_gate1("s", "famP6", reg,
                         np.random.default_rng(1).normal(0.001, 0.01, 1300), 252,
                         backtest_years=1300 / 252)
    crit = next(c for c in rep.criteria if c.name == "Pre-registration integrity")
    assert crit.verdict == "INSUFFICIENT-DATA"
    assert rep.overall != "PASS"


def test_P7_prereg_sealed_after_cutoff_fails_gate(tmp_path, registry, store):
    # `registry` fixture seals famA "now"; a vault cutoff pinned in the
    # past (PAST_CUTOFF = 2020-01-01) means the prereg was sealed AFTER C.
    sealed_vault(tmp_path, registry, store, PAST_CUTOFF, dataset_id="DS-P7a")
    rep = evaluate_gate1("s", "famA", registry,
                         np.random.default_rng(1).normal(0.001, 0.01, 1300), 252,
                         backtest_years=1300 / 252)
    crit = next(c for c in rep.criteria if c.name == "Pre-registration integrity")
    assert crit.verdict == "FAIL"
    assert "postdates" in crit.note


def test_P7_prereg_sealed_on_or_before_cutoff_passes(tmp_path):
    reg = TrialRegistry(str(tmp_path / "r.db"))
    reg.open_hypothesis("famP7", "stmt", "mech", "fals", "uni", "1d", "sc", 10)  # sealed "now"
    st = PITStore(str(tmp_path / "pit.db"), reg)
    future_cutoff = pd.Timestamp.now(tz="UTC") + pd.Timedelta(days=365)
    v = HoldoutVault(str(tmp_path / "vault-p7"), reg, "v-p7", "famP7", st)
    v.seal(source="test-src", dataset_id="DS-P7b",
           instrument_identity="cond-id-0001",
           query_semantics={"fields": ["close"]}, cutoff=future_cutoff,
           schema_fingerprint=SCHEMA_FP, passphrase="hunter2")
    rep = evaluate_gate1("s", "famP7", reg,
                         np.random.default_rng(1).normal(0.001, 0.01, 1300), 252,
                         backtest_years=1300 / 252)
    crit = next(c for c in rep.criteria if c.name == "Pre-registration integrity")
    assert crit.verdict == "PASS"


def test_P8_report_lists_predecessor_chain_prereg_hashes(tmp_path):
    reg = TrialRegistry(str(tmp_path / "r.db"))
    reg.open_hypothesis("genP1", "s", "m", "f", "u", "1d", "sc", 10)
    reg.open_hypothesis("genP2", "s2", "m", "f", "u", "1d", "sc", 10,
                        predecessor_family="genP1")
    rep = evaluate_gate1("s", "genP2", reg,
                         np.random.default_rng(1).normal(0.001, 0.01, 1300), 252,
                         backtest_years=1300 / 252)
    assert rep.predecessor_prereg_sha256 == {"genP1": reg.verify_prereg("genP1")["sealed_sha256"]}
    assert "genP1" in rep.to_markdown()


# -- R1/R3 schema (I-018), spot-checked alongside the P-series ----------

def test_R3_historical_classification_requires_forward_window_fields(tmp_path):
    reg = TrialRegistry(str(tmp_path / "r.db"))
    with pytest.raises(ValueError):
        reg.open_hypothesis("famR3", "s", "m", "f", "u", "1d", "sc", 10,
                            holdout_classification="HISTORICAL")
    reg.open_hypothesis("famR3b", "s", "m", "f", "u", "1d", "sc", 10,
                        holdout_classification="HISTORICAL",
                        forward_window_start="2026-08-01",
                        forward_window_min_length=6.0,
                        forward_kill_condition="net Sharpe < 0 for 2 consecutive months")
    assert reg.hypothesis("famR3b")["holdout_classification"] == "HISTORICAL"


def test_R1_report_carries_holdout_classification(tmp_path):
    reg = TrialRegistry(str(tmp_path / "r.db"))
    reg.open_hypothesis("famR1", "s", "m", "f", "u", "1d", "sc", 10,
                        holdout_classification="FORWARD")
    rep = evaluate_gate1("s", "famR1", reg,
                         np.random.default_rng(1).normal(0.001, 0.01, 1300), 252,
                         backtest_years=1300 / 252)
    assert rep.holdout_classification == "FORWARD"
    assert "FORWARD" in rep.to_markdown()


def test_R1_historical_classification_renders_required_sentence(tmp_path):
    reg = TrialRegistry(str(tmp_path / "r.db"))
    reg.open_hypothesis("famR1b", "s", "m", "f", "u", "1d", "sc", 10,
                        holdout_classification="HISTORICAL",
                        forward_window_start="2026-08-01",
                        forward_window_min_length=6.0,
                        forward_kill_condition="net Sharpe < 0 for 2 consecutive months")
    rep = evaluate_gate1("s", "famR1b", reg,
                         np.random.default_rng(1).normal(0.001, 0.01, 1300), 252,
                         backtest_years=1300 / 252)
    assert "This holdout is historical" in rep.to_markdown()
