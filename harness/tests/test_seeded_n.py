"""H-series — negative tests for `n_inherited`, authored by Validation
before implementation (I-021 / I-027 / D-012).

Source: `research/VALIDATION-GATE0-001-forward-lag.md` §3 (the fourteen
tests, H-1 .. H-14, with the `FamilyStats` registry contract at §3.0).

Per the Principal's binding rider (D-012): these were transcribed from
Validation's prose specification into runnable pytest functions, run
BEFORE any implementation, and observed to fail (RED) as evidence the
tests constrain the implementation rather than the other way around.
Per I-021 / the covering instruction: assertions are not to be moved,
weakened, or deleted by the implementing seat (head-of-data-infra). Any
assertion below that could not be met as specified is escalated to the
CIO rather than adjusted; see `research/DATA-IMPL-003-seeded-n.md`.
"""

from __future__ import annotations

import re
import sqlite3
import time

import numpy as np
import pandas as pd
import pytest

from castellan import (
    TrialRegistry, PreRegistrationAmendedError, InheritedCountDoubleCountError,
    evaluate_gate1, stats,
)

RNG_SEED = 2026


# ----------------------------------------------------------------------
# helpers
# ----------------------------------------------------------------------

def _returns(mean, std, n, seed):
    """A per-bar return series with the given rng seed. Used wherever a
    trial's exact per-period Sharpe just needs to be KNOWABLE (computed
    independently by the test with the same function the registry uses),
    not hit on a specific target value."""
    return np.random.default_rng(seed).normal(mean, std, n)


def _calibrated_returns(sr_period_target, n, std=0.01):
    """A per-bar return series whose SAMPLE per-period Sharpe
    (mean / std(ddof=1)) hits `sr_period_target` deterministically —
    half the bars at +std, half at -std, offset so the sample mean over
    std(ddof=1) equals the target exactly (up to floating rounding).
    Used where a downstream statistic (MinBTL, DSR pass/fail) needs a
    precisely-known achieved Sharpe rather than merely a knowable one.
    """
    n = int(n)
    sample_std_factor = (n / (n - 1)) ** 0.5  # ddof=1 correction on a
    # +-std/2 population has variance std**2 * n/(n-1) under ddof=1
    sample_std = std * sample_std_factor
    mean = sr_period_target * sample_std
    half = n // 2
    vals = np.concatenate([
        np.full(half, mean + std),
        np.full(n - half, mean - std),
    ])
    # interleave so no run-length artefact affects any block-based stat
    idx = np.argsort(np.tile([0, 1], n // 2 + 1)[:n])
    return vals[idx]


# Pre-change SCHEMA literal (H-1's migration case) — captured verbatim
# from `harness/castellan/registry.py` as it read before this change,
# i.e. with NO `n_inherited` column. This is what `book/registry.db`
# looked like before the fix, and the migration must handle it.
_PRE_CHANGE_SCHEMA = """
CREATE TABLE IF NOT EXISTS hypotheses (
    family        TEXT PRIMARY KEY,
    statement     TEXT NOT NULL,
    mechanism     TEXT NOT NULL,
    falsifier     TEXT NOT NULL,
    universe      TEXT NOT NULL,
    horizon       TEXT NOT NULL,
    success_criteria TEXT NOT NULL,
    trial_budget  INTEGER NOT NULL,
    created_utc   REAL NOT NULL,
    predecessor_family TEXT,
    holdout_classification TEXT,
    forward_window_start TEXT,
    forward_window_min_length REAL,
    forward_kill_condition TEXT,
    model_prior_provenance TEXT,
    published_signal_haircut_applied REAL
);
CREATE TABLE IF NOT EXISTS trials (
    trial_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    family        TEXT NOT NULL REFERENCES hypotheses(family),
    config_json   TEXT NOT NULL,
    config_hash   TEXT NOT NULL,
    returns_blob  BLOB NOT NULL,
    n_bars        INTEGER NOT NULL,
    periods_per_year INTEGER NOT NULL,
    sr_period     REAL,
    notes         TEXT,
    created_utc   REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS events (
    event_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    kind          TEXT NOT NULL,
    family        TEXT,
    detail_json   TEXT NOT NULL,
    created_utc   REAL NOT NULL
);
"""


def _parse_threshold_number(threshold: str, label: str) -> float:
    m = re.search(rf"{label}=([0-9.]+)", threshold)
    assert m, f"{label}=<num> not found in threshold string: {threshold!r}"
    return float(m.group(1))


# ----------------------------------------------------------------------
# H-1 · test_h1_column_exists_defaults_zero_and_migrates
# ----------------------------------------------------------------------

def test_h1_column_exists_defaults_zero_and_migrates(tmp_path, grant):
    # Fresh registry: PRAGMA table_info(hypotheses) contains n_inherited,
    # type INTEGER, NOT NULL, default 0.
    reg = TrialRegistry(str(tmp_path / "fresh.db"))
    cols = {r[1]: r for r in reg.conn.execute("PRAGMA table_info(hypotheses)")}
    assert "n_inherited" in cols
    _, name, coltype, notnull, dflt, _pk = cols["n_inherited"]
    assert coltype.upper().startswith("INTEGER")
    assert notnull == 1
    assert dflt is not None and int(float(dflt)) == 0

    # open_hypothesis(...) omitting the argument -> row reads 0.
    with grant(reg, "REGISTER_HYPOTHESIS"):
        reg.open_hypothesis("famH1", "s", "m", "f", "u", "1d", "sc", 10)
    assert reg.hypothesis("famH1")["n_inherited"] == 0

    # Construct a DB from the pre-change SCHEMA literal with one
    # hypothesis row, then open it with TrialRegistry -> _migrate() adds
    # the column, no exception, the pre-existing row reads 0. This is
    # the book/registry.db path and it is not hypothetical.
    legacy_path = str(tmp_path / "legacy.db")
    conn = sqlite3.connect(legacy_path)
    conn.executescript(_PRE_CHANGE_SCHEMA)
    conn.execute(
        "INSERT INTO hypotheses (family, statement, mechanism, falsifier, "
        "universe, horizon, success_criteria, trial_budget, created_utc) "
        "VALUES (?,?,?,?,?,?,?,?,?)",
        ("legacy-fam", "s", "m", "f", "u", "1d", "sc", 10, time.time()),
    )
    conn.commit()
    conn.close()

    legacy_reg = TrialRegistry(legacy_path)  # must not raise
    # I-272: constructing over an existing pre-grant-system file does not
    # itself migrate the schema (only a MIGRATION-reason write_grant does,
    # per registry.py's own `_migrate` call site); an empty grant block
    # triggers it -- not one of the 58 counted call sites (no
    # open_hypothesis/log_trial/log_event call), added on the same
    # reasoning as I-271.
    with grant(legacy_reg, "MIGRATION"):
        pass
    legacy_cols = [r[1] for r in legacy_reg.conn.execute("PRAGMA table_info(hypotheses)")]
    assert "n_inherited" in legacy_cols
    assert legacy_reg.hypothesis("legacy-fam")["n_inherited"] == 0


# ----------------------------------------------------------------------
# H-2 · test_h2_value_is_validated
# ----------------------------------------------------------------------

def test_h2_value_is_validated(tmp_path, grant):
    reg = TrialRegistry(str(tmp_path / "r.db"))
    with grant(reg, "REGISTER_HYPOTHESIS"):
        with pytest.raises(ValueError):
            reg.open_hypothesis("famNeg", "s", "m", "f", "u", "1d", "sc", 10,
                                n_inherited=-1)
        with pytest.raises(ValueError):
            reg.open_hypothesis("famFloat", "s", "m", "f", "u", "1d", "sc", 10,
                                n_inherited=3.7)
        reg.open_hypothesis("famZero", "s", "m", "f", "u", "1d", "sc", 10,
                            n_inherited=0)
        assert reg.hypothesis("famZero")["n_inherited"] == 0
        reg.open_hypothesis("famBig", "s", "m", "f", "u", "1d", "sc", 10,
                            n_inherited=31250)
        assert reg.hypothesis("famBig")["n_inherited"] == 31250


# ----------------------------------------------------------------------
# H-3a · test_h3_n_inherited_is_binding_and_changes_the_hash
# ----------------------------------------------------------------------

def test_h3_n_inherited_is_binding_and_changes_the_hash(tmp_path, grant):
    from castellan.registry import _BINDING_FIELDS
    assert "n_inherited" in _BINDING_FIELDS

    reg = TrialRegistry(str(tmp_path / "r.db"))
    with grant(reg, "REGISTER_HYPOTHESIS"):
        reg.open_hypothesis("famA", "s", "m", "f", "u", "1d", "sc", 10,
                            n_inherited=0)
        reg.open_hypothesis("famB", "s", "m", "f", "u", "1d", "sc", 10,
                            n_inherited=5000)
    hash_a = reg.verify_prereg("famA")["sealed_sha256"]
    hash_b = reg.verify_prereg("famB")["sealed_sha256"]
    assert hash_a != hash_b

    events = reg.events(kind="hypothesis_sealed", family="famB")
    assert len(events) == 1
    assert events[0]["detail"]["n_inherited"] == 5000


# ----------------------------------------------------------------------
# H-3b · test_h3_negative_reregistration_with_different_n_inherited_is_refused
# ----------------------------------------------------------------------

def test_h3_negative_reregistration_with_different_n_inherited_is_refused(tmp_path, grant):
    reg = TrialRegistry(str(tmp_path / "r.db"))
    with grant(reg, "REGISTER_HYPOTHESIS"):
        reg.open_hypothesis("famC", "s", "m", "f", "u", "1d", "sc", 10,
                            n_inherited=31250)
        with pytest.raises(PreRegistrationAmendedError):
            reg.open_hypothesis("famC", "s", "m", "f", "u", "1d", "sc", 10,
                                n_inherited=3125)
        events = reg.events(kind="hypothesis_amendment_refused", family="famC")
        assert len(events) == 1
        assert "n_inherited" in events[0]["detail"]["differing_fields"]

        # Byte-identical re-call -> no raise, no new event.
        reg.open_hypothesis("famC", "s", "m", "f", "u", "1d", "sc", 10,
                            n_inherited=31250)
    assert len(reg.events(kind="hypothesis_amendment_refused", family="famC")) == 1


# ----------------------------------------------------------------------
# H-3c · test_h3_negative_raw_sqlite_downgrade_is_detected
# ----------------------------------------------------------------------

def test_h3_negative_raw_sqlite_downgrade_is_detected(tmp_path, grant):
    # I-271-class: the raw downgrade write needs the same open grant as
    # the preceding open_hypothesis (R-1's read-only default applies to
    # reg.conn regardless of how the write is issued).
    reg = TrialRegistry(str(tmp_path / "r.db"))
    with grant(reg, "REGISTER_HYPOTHESIS"):
        reg.open_hypothesis("famD", "s", "m", "f", "u", "1d", "sc", 10,
                            n_inherited=31250)
        reg.conn.execute("UPDATE hypotheses SET n_inherited=0 WHERE family=?", ("famD",))
        reg.conn.commit()

    v = reg.verify_prereg("famD")
    assert v["match"] is False
    assert "n_inherited" in v["differing_fields"]

    rep = evaluate_gate1("s", "famD", reg,
                         np.random.default_rng(1).normal(0.001, 0.01, 1300), 252,
                         backtest_years=1300 / 252)
    crit = next(c for c in rep.criteria if c.name == "Pre-registration integrity")
    assert crit.verdict == "FAIL"


# ----------------------------------------------------------------------
# H-4 · test_h4_n_trials_is_seeded_plus_logged
# ----------------------------------------------------------------------

def test_h4_n_trials_is_seeded_plus_logged(tmp_path, grant):
    reg = TrialRegistry(str(tmp_path / "r.db"))
    with grant(reg, "REGISTER_HYPOTHESIS"):
        reg.open_hypothesis("famE", "s", "m", "f", "u", "1d", "sc", 100,
                            n_inherited=31250)
    with grant(reg, "LOG_TRIAL"):
        reg.log_trial("famE", {"v": 1}, _returns(0.0005, 0.01, 200, 1), 252)
        reg.log_trial("famE", {"v": 2}, _returns(0.0006, 0.01, 200, 2), 252)
    fs = reg.family_stats("famE")
    assert fs.n_trials == 31252
    assert fs.n_inherited == 31250
    assert fs.n_logged == 2

    with grant(reg, "REGISTER_HYPOTHESIS"):
        reg.open_hypothesis("famF", "s", "m", "f", "u", "1d", "sc", 100,
                            n_inherited=31250)
    fs2 = reg.family_stats("famF")
    assert fs2.n_trials == 31250
    assert fs2.n_logged == 0


# ----------------------------------------------------------------------
# H-5a · test_h5_transitive_sum_across_chain_no_double_count
# ----------------------------------------------------------------------

def test_h5_transitive_sum_across_chain_no_double_count(tmp_path, grant):
    reg = TrialRegistry(str(tmp_path / "r.db"))
    with grant(reg, "REGISTER_HYPOTHESIS"):
        reg.open_hypothesis("chA", "s", "m", "f", "u", "1d", "sc", 5000,
                            n_inherited=1000)
    with grant(reg, "LOG_TRIAL"):
        for i in range(3):
            reg.log_trial("chA", {"v": i}, _returns(0.0005, 0.01, 100, 10 + i), 252)

    with grant(reg, "REGISTER_HYPOTHESIS"):
        reg.open_hypothesis("chB", "s", "m", "f", "u", "1d", "sc", 5000,
                            predecessor_family="chA", n_inherited=50)
    with grant(reg, "LOG_TRIAL"):
        for i in range(2):
            reg.log_trial("chB", {"v": i}, _returns(0.0005, 0.01, 100, 20 + i), 252)

    with grant(reg, "REGISTER_HYPOTHESIS"):
        reg.open_hypothesis("chC", "s", "m", "f", "u", "1d", "sc", 5000,
                            predecessor_family="chB", n_inherited=0)
    with grant(reg, "LOG_TRIAL"):
        reg.log_trial("chC", {"v": 0}, _returns(0.0005, 0.01, 100, 30), 252)

    fs_c = reg.family_stats("chC")
    assert fs_c.n_trials == 1056
    assert fs_c.n_inherited == 1050
    assert fs_c.n_logged == 6

    fs_a = reg.family_stats("chA")
    assert fs_a.n_trials == 1003  # predecessor not inflated by successors


# ----------------------------------------------------------------------
# H-5b · test_h5_negative_successor_redeclaring_the_chain_is_refused
# ----------------------------------------------------------------------

def test_h5_negative_successor_redeclaring_the_chain_is_refused(tmp_path, grant):
    reg = TrialRegistry(str(tmp_path / "r.db"))
    with grant(reg, "REGISTER_HYPOTHESIS"):
        reg.open_hypothesis("chD", "s", "m", "f", "u", "1d", "sc", 5000,
                            n_inherited=1000)
    with grant(reg, "LOG_TRIAL"):
        for i in range(3):
            reg.log_trial("chD", {"v": i}, _returns(0.0005, 0.01, 100, 40 + i), 252)
    assert reg.family_stats("chD").n_trials == 1003

    with grant(reg, "REGISTER_HYPOTHESIS"):
        with pytest.raises(InheritedCountDoubleCountError) as exc_info:
            reg.open_hypothesis("chE", "s", "m", "f", "u", "1d", "sc", 5000,
                                predecessor_family="chD", n_inherited=1003)
    msg = str(exc_info.value)
    assert "1003" in msg  # chain total AND the declared value, both 1003


# ----------------------------------------------------------------------
# H-6a · test_h6_sigma_sr_uses_logged_trials_only
# ----------------------------------------------------------------------

def test_h6_sigma_sr_uses_logged_trials_only(tmp_path, grant):
    reg = TrialRegistry(str(tmp_path / "r.db"))
    with grant(reg, "REGISTER_HYPOTHESIS"):
        reg.open_hypothesis("famG", "s", "m", "f", "u", "1d", "sc", 100,
                            n_inherited=31250)
    r1 = _returns(0.0004, 0.01, 250, 51)
    r2 = _returns(0.0009, 0.012, 250, 52)
    s1 = stats.sharpe_period(r1)
    s2 = stats.sharpe_period(r2)
    with grant(reg, "LOG_TRIAL"):
        reg.log_trial("famG", {"v": 1}, r1, 252)
        reg.log_trial("famG", {"v": 2}, r2, 252)

    fs = reg.family_stats("famG")
    assert fs.sr_period_std == pytest.approx(np.std([s1, s2], ddof=1))
    assert fs.sr_period_mean == pytest.approx(np.mean([s1, s2]))
    assert fs.sr_period_best == pytest.approx(max(s1, s2))


# ----------------------------------------------------------------------
# H-6b · test_h6_negative_no_phantom_rows_are_synthesised
# ----------------------------------------------------------------------

def test_h6_negative_no_phantom_rows_are_synthesised(tmp_path, grant):
    reg = TrialRegistry(str(tmp_path / "r.db"))
    with grant(reg, "REGISTER_HYPOTHESIS"):
        reg.open_hypothesis("famH", "s", "m", "f", "u", "1d", "sc", 100,
                            n_inherited=31250)
    n0 = reg.conn.execute(
        "SELECT COUNT(*) FROM trials WHERE family=?", ("famH",)
    ).fetchone()[0]
    assert n0 == 0

    with grant(reg, "LOG_TRIAL"):
        reg.log_trial("famH", {"v": 1}, _returns(0.0005, 0.01, 100, 61), 252)
        reg.log_trial("famH", {"v": 2}, _returns(0.0005, 0.01, 100, 62), 252)
    n2 = reg.conn.execute(
        "SELECT COUNT(*) FROM trials WHERE family=?", ("famH",)
    ).fetchone()[0]
    assert n2 == 2
    assert n2 != 31252
    assert n2 != 31250

    assert reg.returns_matrix("famH").shape[1] == 2


# ----------------------------------------------------------------------
# H-6c · test_h6_negative_one_logged_trial_gives_no_dispersion
# ----------------------------------------------------------------------

def test_h6_negative_one_logged_trial_gives_no_dispersion(tmp_path, grant):
    reg = TrialRegistry(str(tmp_path / "r.db"))
    with grant(reg, "REGISTER_HYPOTHESIS"):
        reg.open_hypothesis("famI", "s", "m", "f", "u", "1d", "sc", 100,
                            n_inherited=31250)
    with grant(reg, "LOG_TRIAL"):
        reg.log_trial("famI", {"v": 1}, _returns(0.0005, 0.01, 300, 71), 252)
    fs = reg.family_stats("famI")
    assert fs.sr_period_std is None

    rep = evaluate_gate1("s", "famI", reg,
                         np.random.default_rng(9).normal(0.0005, 0.01, 1300), 252,
                         backtest_years=1300 / 252)
    crit = next(c for c in rep.criteria if c.name == "Deflated Sharpe Ratio")
    assert crit.verdict == "INSUFFICIENT-DATA"


# ----------------------------------------------------------------------
# H-7 · test_h7_dsr_consumes_the_seeded_denominator
# ----------------------------------------------------------------------

def test_h7_dsr_consumes_the_seeded_denominator(tmp_path, grant):
    reg = TrialRegistry(str(tmp_path / "r.db"))
    with grant(reg, "REGISTER_HYPOTHESIS"):
        reg.open_hypothesis("famU", "s", "m", "f", "u", "1d", "sc", 100,
                            n_inherited=0)
        reg.open_hypothesis("famS", "s", "m", "f", "u", "1d", "sc", 100,
                            n_inherited=31250)

    # The SAME two logged trials, by construction, in both families.
    trial_r1 = _returns(0.0, 0.01, 200, 81)
    trial_r2 = _returns(0.0, 0.012, 200, 82)
    with grant(reg, "LOG_TRIAL"):
        for fam in ("famU", "famS"):
            reg.log_trial(fam, {"v": 1}, trial_r1, 252)
            reg.log_trial(fam, {"v": 2}, trial_r2, 252)

    assert reg.family_stats("famU").n_trials == 2
    assert reg.family_stats("famS").n_trials == 31252
    sr_std = reg.family_stats("famU").sr_period_std
    assert sr_std == reg.family_stats("famS").sr_period_std  # same 2 trials

    # A candidate OOS return series, per-period Sharpe chosen to sit
    # between E[max SR | N=2] and E[max SR | N=31252] at this sigma_sr,
    # so DSR passes at N=2 and fails at N=31252 (verified numerically:
    # DSR@2~=0.99, DSR@31252~=0 at this sigma_sr and target).
    candidate = _calibrated_returns(0.12, 2000)

    rep_u = evaluate_gate1("s", "famU", reg, candidate, 252,
                           backtest_years=2000 / 252)
    rep_s = evaluate_gate1("s", "famS", reg, candidate, 252,
                           backtest_years=2000 / 252)

    assert rep_u.n_trials == 2
    assert rep_s.n_trials == 31252

    dsr_u_expected = stats.deflated_sharpe_ratio(candidate, 2, sr_std)
    dsr_s_expected = stats.deflated_sharpe_ratio(candidate, 31252, sr_std)

    crit_u = next(c for c in rep_u.criteria if c.name == "Deflated Sharpe Ratio")
    crit_s = next(c for c in rep_s.criteria if c.name == "Deflated Sharpe Ratio")
    assert crit_u.value == pytest.approx(dsr_u_expected)
    assert crit_s.value == pytest.approx(dsr_s_expected)
    assert crit_s.value < crit_u.value

    # Seeding must change the VERDICT, not merely the number.
    assert crit_u.verdict == "PASS"
    assert crit_s.verdict == "FAIL"


# ----------------------------------------------------------------------
# H-8 · test_h8_minbtl_consumes_the_seeded_denominator_and_fails_a_short_backtest
# ----------------------------------------------------------------------

def test_h8_minbtl_consumes_the_seeded_denominator_and_fails_a_short_backtest(tmp_path, grant):
    reg = TrialRegistry(str(tmp_path / "r.db"))
    with grant(reg, "REGISTER_HYPOTHESIS"):
        reg.open_hypothesis("famSeeded", "s", "m", "f", "u", "1d", "sc", 100,
                            n_inherited=31250)
        reg.open_hypothesis("famPlain", "s", "m", "f", "u", "1d", "sc", 100,
                            n_inherited=0)
    with grant(reg, "LOG_TRIAL"):
        for fam in ("famSeeded", "famPlain"):
            reg.log_trial(fam, {"v": 1}, _returns(0.0005, 0.01, 200, 91), 252)
            reg.log_trial(fam, {"v": 2}, _returns(0.0005, 0.01, 200, 92), 252)

    periods_per_year = 365
    n_bars = 1462  # 1461 days span / 365.25 == 4.00 years exactly
    idx = pd.date_range("2020-01-01", periods=n_bars, freq="D")
    years_calendar = (idx.max() - idx.min()).days / 365.25
    assert years_calendar == pytest.approx(4.0, abs=1e-6)

    target_sr_period = 1.0 / (periods_per_year ** 0.5)  # net annual SR ~= 1.0
    r = _calibrated_returns(target_sr_period, n_bars, std=0.01)
    achieved_sr_ann = stats.sharpe_annual(r, periods_per_year)
    assert achieved_sr_ann == pytest.approx(1.0, abs=0.01)

    rep_seeded = evaluate_gate1("s", "famSeeded", reg, r, periods_per_year,
                                backtest_years=years_calendar, oos_index=idx)
    rep_plain = evaluate_gate1("s", "famPlain", reg, r, periods_per_year,
                               backtest_years=years_calendar, oos_index=idx)

    crit_seeded = next(c for c in rep_seeded.criteria if c.name == "Backtest length (years)")
    crit_plain = next(c for c in rep_plain.criteria if c.name == "Backtest length (years)")

    minbtl_seeded = _parse_threshold_number(crit_seeded.threshold, "MinBTL")
    assert minbtl_seeded == pytest.approx(17.06, abs=0.05)
    assert crit_seeded.verdict == "FAIL"

    minbtl_plain = _parse_threshold_number(crit_plain.threshold, "MinBTL")
    assert minbtl_plain == pytest.approx(0.27, abs=0.05)
    assert crit_plain.verdict == "PASS"


# ----------------------------------------------------------------------
# H-9 · test_h9_pbo_is_computed_on_logged_trials_only_and_the_report_says_so
# ----------------------------------------------------------------------

def test_h9_pbo_is_computed_on_logged_trials_only_and_the_report_says_so(tmp_path, grant):
    reg = TrialRegistry(str(tmp_path / "r.db"))
    with grant(reg, "REGISTER_HYPOTHESIS"):
        reg.open_hypothesis("famJ", "s", "m", "f", "u", "1d", "sc", 100,
                            n_inherited=31250)
    with grant(reg, "LOG_TRIAL"):
        for i in range(20):
            reg.log_trial("famJ", {"v": i}, _returns(0.0004, 0.01, 50, 100 + i), 252)

    M = reg.returns_matrix("famJ")
    assert M.shape[1] == 20

    rep = evaluate_gate1("s", "famJ", reg,
                         np.random.default_rng(5).normal(0.0005, 0.01, 1300), 252,
                         backtest_years=1300 / 252)
    crit = next(c for c in rep.criteria if c.name.startswith("PBO"))
    assert "20" in crit.note
    assert "inherited" in crit.note.lower()
    assert "none" in crit.note.lower() or "no return" in crit.note.lower()

    md = rep.to_markdown()
    assert "20" in md


# ----------------------------------------------------------------------
# H-10 · test_h10_negative_seeding_alone_does_not_blow_the_trial_budget
# ----------------------------------------------------------------------

def test_h10_negative_seeding_alone_does_not_blow_the_trial_budget(tmp_path, grant):
    reg = TrialRegistry(str(tmp_path / "r.db"))
    with grant(reg, "REGISTER_HYPOTHESIS"):
        reg.open_hypothesis("famK", "s", "m", "f", "u", "1d", "sc", 40,
                            n_inherited=31250)
    with grant(reg, "LOG_TRIAL"):
        reg.log_trial("famK", {"v": 1}, _returns(0.0005, 0.01, 100, 111), 252)
        reg.log_trial("famK", {"v": 2}, _returns(0.0005, 0.01, 100, 112), 252)

    rep = evaluate_gate1("s", "famK", reg,
                         np.random.default_rng(6).normal(0.0005, 0.01, 1300), 252,
                         backtest_years=1300 / 252)
    crit = next(c for c in rep.criteria if c.name == "Trial count N (registry)")
    assert "OVER BUDGET" not in crit.note

    with grant(reg, "LOG_TRIAL"):
        for i in range(3, 42):
            reg.log_trial("famK", {"v": i}, _returns(0.0005, 0.01, 100, 200 + i), 252)
    rep2 = evaluate_gate1("s", "famK", reg,
                          np.random.default_rng(6).normal(0.0005, 0.01, 1300), 252,
                          backtest_years=1300 / 252)
    crit2 = next(c for c in rep2.criteria if c.name == "Trial count N (registry)")
    assert "OVER BUDGET" in crit2.note


# ----------------------------------------------------------------------
# H-11 · test_h11_negative_seeded_family_with_no_logged_trials_is_insufficient_data
# ----------------------------------------------------------------------

def test_h11_negative_seeded_family_with_no_logged_trials_is_insufficient_data(tmp_path, grant):
    reg = TrialRegistry(str(tmp_path / "r.db"))
    with grant(reg, "REGISTER_HYPOTHESIS"):
        reg.open_hypothesis("famL", "s", "m", "f", "u", "1d", "sc", 40,
                            n_inherited=31250)
    rep = evaluate_gate1("s", "famL", reg,
                         np.random.default_rng(7).normal(0.0005, 0.01, 1300), 252,
                         backtest_years=1300 / 252)
    crit = next(c for c in rep.criteria if c.name == "Trial count N (registry)")
    assert crit.verdict == "INSUFFICIENT-DATA"
    assert crit.verdict != "PASS"
    assert "logged=0" in crit.note


# ----------------------------------------------------------------------
# H-12 · test_h12_report_renders_the_decomposition_not_a_bare_total
# ----------------------------------------------------------------------

def test_h12_report_renders_the_decomposition_not_a_bare_total(tmp_path, grant):
    reg = TrialRegistry(str(tmp_path / "r.db"))
    with grant(reg, "REGISTER_HYPOTHESIS"):
        reg.open_hypothesis("famM", "s", "m", "f", "u", "1d", "sc", 100,
                            n_inherited=31250)
    with grant(reg, "LOG_TRIAL"):
        reg.log_trial("famM", {"v": 1}, _returns(0.0005, 0.01, 100, 121), 252)
        reg.log_trial("famM", {"v": 2}, _returns(0.0005, 0.01, 100, 122), 252)

    rep = evaluate_gate1("s", "famM", reg,
                         np.random.default_rng(8).normal(0.0005, 0.01, 1300), 252,
                         backtest_years=1300 / 252)
    md = rep.to_markdown()
    assert "31,252" in md or "31252" in md
    assert "31,250" in md or "31250" in md
    assert re.search(r"\b2\b", md)  # the logged figure
    assert "inherited" in md.lower()


# ----------------------------------------------------------------------
# H-13 · test_h13_negative_an_unseeded_family_is_bit_for_bit_unchanged
# ----------------------------------------------------------------------

def test_h13_negative_an_unseeded_family_is_bit_for_bit_unchanged(tmp_path, grant):
    reg = TrialRegistry(str(tmp_path / "r.db"))
    with grant(reg, "REGISTER_HYPOTHESIS"):
        reg.open_hypothesis("famOmitted", "s", "m", "f", "u", "1d", "sc", 100)
        reg.open_hypothesis("famExplicitZero", "s", "m", "f", "u", "1d", "sc", 100,
                            n_inherited=0)

    with grant(reg, "LOG_TRIAL"):
        for fam in ("famOmitted", "famExplicitZero"):
            reg.log_trial(fam, {"v": 1}, _returns(0.0005, 0.01, 200, 131), 252)
            reg.log_trial(fam, {"v": 2}, _returns(0.0005, 0.01, 200, 132), 252)
            reg.log_trial(fam, {"v": 3}, _returns(0.0007, 0.011, 200, 133), 252)

    fs_o = reg.family_stats("famOmitted")
    fs_z = reg.family_stats("famExplicitZero")
    assert fs_o.n_trials == 3 and fs_o.n_logged == 3 and fs_o.n_inherited == 0
    assert fs_o.sr_period_std == pytest.approx(fs_z.sr_period_std)
    assert fs_o.sr_period_mean == pytest.approx(fs_z.sr_period_mean)
    assert fs_o.sr_period_best == pytest.approx(fs_z.sr_period_best)

    r = np.random.default_rng(4).normal(0.0006, 0.01, 1300)
    rep_o = evaluate_gate1("s", "famOmitted", reg, r, 252, backtest_years=1300 / 252)
    rep_z = evaluate_gate1("s", "famExplicitZero", reg, r, 252, backtest_years=1300 / 252)

    assert len(rep_o.criteria) == len(rep_z.criteria)
    for c_o, c_z in zip(rep_o.criteria, rep_z.criteria):
        assert c_o.name == c_z.name
        assert c_o.value == c_z.value or (
            isinstance(c_o.value, float) and c_o.value == pytest.approx(c_z.value)
        )
        assert c_o.threshold == c_z.threshold
        assert c_o.verdict == c_z.verdict

    hash_omitted = reg.verify_prereg("famOmitted")["sealed_sha256"]
    hash_zero = reg.verify_prereg("famExplicitZero")["sealed_sha256"]
    # NOTE: these two families differ on `family` and `statement`=... no,
    # they share every OTHER binding field and differ only in name. To
    # isolate n_inherited=omitted vs n_inherited=0-explicit precisely,
    # compare hashes of two SAME-NAMED families is impossible (the
    # registry is keyed on family). Instead assert equality the way P1
    # defines it: hash the binding dict directly.
    from castellan.registry import _binding_hash
    omitted_binding = dict(reg.hypothesis("famOmitted"))
    zero_binding = dict(reg.hypothesis("famExplicitZero"))
    omitted_binding["family"] = "SAME"
    zero_binding["family"] = "SAME"
    assert _binding_hash(omitted_binding) == _binding_hash(zero_binding)


# ----------------------------------------------------------------------
# H-14 · test_h14_forward_lag_001_declared_denominator_end_to_end
# ----------------------------------------------------------------------

def test_h14_forward_lag_001_declared_denominator_end_to_end(tmp_path, grant):
    reg = TrialRegistry(str(tmp_path / "r.db"))
    with grant(reg, "REGISTER_HYPOTHESIS"):
        reg.open_hypothesis(
        family="forward-lag-001",
        statement=(
            "On Polymarket, when a high-volume contract reprices by >=20 "
            "price points over a trailing 2h window, economically-paired "
            "later-resolving contracts on the same underlying event "
            "reprice with a directionally consistent delay whose peak "
            "lies strictly between 0 and 24 hours and whose median "
            "fillable capture exceeds 2.0c on a 50c-equivalent contract, "
            "net of the full Charter 4.6 cost stack at 1x modelled costs."
        ),
        mechanism=(
            "The counterparty is a Polymarket participant on the "
            "later-resolving leg who has not updated for news already "
            "impounded in the nearer leg (directional retail, passive "
            "resting liquidity, and per-contract attention allocation). "
            "Persistence rests on participation segmentation, not on "
            "regulatory or settlement friction."
        ),
        falsifier=(
            "F-001: k* = argmax_k rho(k) over k in [-36,+36]h on "
            "paired-quotable bars. FALSIFIED if k*<=0 (DIRECTION), or "
            "k*>=24h or unstable across subsamples (ARTIFACT), or median "
            "signed fillable capture at k* < 2.0c (MAGNITUDE)."
        ),
        universe=(
            "Polymarket only, both legs. Unit of observation is the "
            "PAIR-DAY under DATA-SPEC section 3 mapping. P_notional = "
            "USD 5,000 per leg. All four cells of {UP,DOWN} x "
            "{EARLIER,LATER} are traded."
        ),
        horizon=(
            "Event-driven, no periodic rebalance. Entry 2h after signal; "
            "exit at target +15c, stop -25%, or max hold 36h. Hourly UTC "
            "bars via pit_price_panel. periods_per_year = 365."
        ),
        success_criteria=(
            "Tiered: (1) F-001 survival. (2) KC-001 survival at "
            "2026-10-31. (3) Gate 1: every Charter 4.4 criterion via "
            "castellan.evaluate_gate1 with N = n_inherited + logged "
            "trials, backtest_years passed explicitly as true calendar "
            "span. Recorded at pre-registration: MinBTL(31250) = 17.06 "
            "years at net SR 1.0."
        ),
        trial_budget=40,
        n_inherited=31250,
        predecessor_family=None,
        holdout_classification="FORWARD",
        forward_window_start="2026-07-28",
        forward_window_min_length=12.0,
        forward_kill_condition=(
            "KC-001 (REDTEAM-001 B.5, signed by the Principal). "
            "Observation date 2026-10-31, absolute. KILLED if net "
            "expectancy <= 0 OR fewer than 30 tradable signal events."
        ),
        model_prior_provenance=(
            "R4(a). Statement/mechanism: Principal (D-004), human. "
            "Parameter values carried forward unchanged from the "
            "Principal's prior unaudited work per I-002; charged the "
            "full price of that search via n_inherited."
        ),
        published_signal_haircut_applied=None,
        )
    with grant(reg, "LOG_TRIAL"):
        reg.log_trial("forward-lag-001", {"v": 1},
                      _returns(0.0004, 0.01, 200, 141), 365)
        reg.log_trial("forward-lag-001", {"v": 2},
                      _returns(0.0004, 0.011, 200, 142), 365)

    fs = reg.family_stats("forward-lag-001")
    assert fs.n_trials == 31252

    assert stats.expected_max_sharpe(31252, 1.0) == pytest.approx(4.1308, abs=1e-3)
    assert stats.min_backtest_length_years(31252, 1.0, 365) == pytest.approx(17.063, abs=0.02)

    periods_per_year = 365
    n_bars = 1462
    idx = pd.date_range("2020-01-01", periods=n_bars, freq="D")
    years_calendar = (idx.max() - idx.min()).days / 365.25
    target_sr_period = 1.0 / (periods_per_year ** 0.5)
    r = _calibrated_returns(target_sr_period, n_bars, std=0.01)

    rep = evaluate_gate1("s", "forward-lag-001", reg, r, periods_per_year,
                         backtest_years=years_calendar, oos_index=idx)
    length_crit = next(c for c in rep.criteria if c.name == "Backtest length (years)")
    dsr_crit = next(c for c in rep.criteria if c.name == "Deflated Sharpe Ratio")
    assert length_crit.verdict == "FAIL"
    assert dsr_crit.verdict == "FAIL"
