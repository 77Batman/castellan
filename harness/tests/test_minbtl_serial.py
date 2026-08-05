"""Acceptance tests for I-057, Item 1 — the serially-corrected MinBTL.

Authored by the Head of Quantitative Validation under VALIDATION-SPEC-002,
BEFORE implementation. Seat 9 implements against these and does not amend
them; a test Seat 9 believes is wrong is escalated to Validation in writing
before it is changed (Ruling 004 section 11 standing terms, I-036, I-058).

RED BY DESIGN. Clause references are to VALIDATION-SPEC-002 section 1
(M-1 ... M-14) and section 3 (R-15, R-16).

Two tests here are GUARDS, not drivers, and pass today: test_mbs_05
(M-1 -- min_backtest_length_years must not be mutated in place) and
test_mbs_13 (the section 7.2 arithmetic, a pure function of the existing
library). Both must still pass after the change.
"""

import math

import numpy as np
import pandas as pd
import pytest

from castellan import TrialRegistry, evaluate_gate1, stats

SPAN_BTC_ETH = 6.571          # PREREG-002 section 8 [cited]
CEILING_IID = 109             # Ruling 004 section 2.2 [cited]


# ----------------------------------------------------------------------
# Capability probes -- a missing capability is a FAILURE naming its clause,
# not an import-time collection error.
# ----------------------------------------------------------------------

def _cap(name, clause):
    if not hasattr(stats, name):
        pytest.fail(
            f"NOT IMPLEMENTED: castellan.stats.{name} does not exist. "
            f"Required by VALIDATION-SPEC-002 clause {clause} (I-057)."
        )
    return getattr(stats, name)


def _criterion(report, needle):
    hits = [c for c in report.criteria if needle.lower() in c.name.lower()]
    if not hits:
        pytest.fail(
            f"No criterion matching {needle!r}. "
            f"Present: {[c.name for c in report.criteria]}")
    return hits[0]


# ----------------------------------------------------------------------
# Reference constructions -- the SPEC's arithmetic, restated independently
# ----------------------------------------------------------------------

def _ar1(T, rho, mu, seed, sd=0.01):
    rng = np.random.default_rng(seed)
    e = rng.standard_normal(T)
    x = np.empty(T)
    x[0] = e[0] / math.sqrt(1.0 - rho ** 2)
    for t in range(1, T):
        x[t] = rho * x[t - 1] + e[t]
    return mu + sd * x


def _vif_ar1(rho):
    return (1.0 + rho) / (1.0 - rho)


def _ref_minbtl_serial(n, sr, ppy, vif):
    """M-2, restated independently."""
    mb = stats.min_backtest_length_years(n, sr, ppy)
    return max(mb, mb * vif)


def _ref_ceiling(span, sr, vif, ppy=252):
    """M-4, restated independently by linear scan."""
    best = 1
    n = 2
    while n < 5_000_000:
        if _ref_minbtl_serial(n, sr, ppy, vif) <= span:
            best = n
            n += 1
        else:
            break
    return best


@pytest.fixture()
def registry(tmp_path):
    return TrialRegistry(str(tmp_path / "reg.db"))


def _seed_family(reg, family="F", n_trials=12, rho=0.0, T=1200, mu=0.0006):
    reg.open_hypothesis(
        family, "s", "m", "f", "u", "h", "sc", trial_budget=1000)
    for i in range(n_trials):
        reg.log_trial(family, {"i": i}, _ar1(T, rho, mu, 400 + i), 252)


# ======================================================================
# M-2 -- the construction
# ======================================================================

def test_mbs_01_serial_function_requires_vif_explicitly():
    """M-2: `vif` is required and keyword-only. A default of 1.0 would let a
    caller obtain the uncorrected figure from the corrected function by
    omission -- the shape W-1 closed for feature_lookback."""
    fn = _cap("min_backtest_length_years_serial", "M-2")

    with pytest.raises(TypeError):
        fn(100, 1.0, 252)                      # no vif at all
    with pytest.raises(TypeError):
        fn(100, 1.0, 252, 1.5)                 # positional vif

    for bad in (0.0, -1.0, float("nan"), float("inf")):
        with pytest.raises(ValueError):
            fn(100, 1.0, 252, vif=bad)


def test_mbs_02_reduces_to_iid_at_vif_one():
    """M-2 / D-5's analogue: exact reduction, not approximate."""
    fn = _cap("min_backtest_length_years_serial", "M-2")
    rng = np.random.default_rng(3)
    for _ in range(200):
        n = int(rng.integers(2, 500_000))
        sr = float(rng.uniform(0.05, 4.0))
        ppy = int(rng.choice([12, 52, 252, 365]))
        assert fn(n, sr, ppy, vif=1.0) == stats.min_backtest_length_years(
            n, sr, ppy), "M-2: vif=1.0 must reduce EXACTLY, not approximately"


def test_mbs_03_scales_linearly_in_vif():
    """M-2: MinBTL_serial = max(mb, mb*vif)."""
    fn = _cap("min_backtest_length_years_serial", "M-2")
    for n in (2, 10, 86, 109, 1000, 100_000):
        for vif in (1.0, 1.0709, 1.222, 1.5, 3.0, 10.696, 47.0):
            assert fn(n, 1.0, 252, vif=vif) == pytest.approx(
                _ref_minbtl_serial(n, 1.0, 252, vif), rel=1e-12)


def test_mbs_04_vif_is_the_square_of_the_inflation_ratio():
    """M-3 -- named in the spec as the single most likely implementation
    error. HACTStat.inflation is a ratio of STANDARD ERRORS; VIF is a ratio
    of VARIANCES. VIF = inflation**2."""
    vi = _cap("variance_inflation", "R-2")
    for rho in (0.2, 0.5, 0.8):
        r = _ar1(4000, rho, 0.0004, 11)
        hac = stats.sr_tstat_corrected(r)
        got = vi(r)
        assert got.vif_hac == pytest.approx(hac.inflation ** 2, rel=1e-9), (
            "M-3: vif_hac must equal HACTStat.inflation**2 -- a ratio of "
            "variances, not of standard errors")


def test_mbs_05_min_backtest_length_years_is_not_edited():
    """M-1 -- GUARD, green today, must stay green. The correction is a new
    function, not a mutation of an old one."""
    for n, sr, ppy, want in [
        (109, 1.0, 252, 6.5576),
        (86, 1.0, 252, 6.1359),
        (1000, 1.0, 365, 10.5958),
    ]:
        assert stats.min_backtest_length_years(n, sr, ppy) == pytest.approx(
            want, abs=1e-3)
    assert stats.min_backtest_length_years(10, 0.0, 252) == float("inf")


# ======================================================================
# M-4 / M-5 -- the ceiling
# ======================================================================

def test_mbs_06_max_admissible_trials_reproduces_109():
    """M-4: the ceiling at VIF=1 on the firm's best data surface is 109."""
    mat = _cap("max_admissible_trials", "M-4")
    assert mat(SPAN_BTC_ETH, 1.0, 252, vif=1.0) == CEILING_IID
    # and 110 does not fit -- the one-trial correction Ruling 004 recorded
    assert stats.min_backtest_length_years(110, 1.0, 252) > SPAN_BTC_ETH


def test_mbs_07_max_admissible_trials_reproduces_the_ruling_table():
    """M-4 + M-13(1): the ceilings the Principal ruled on must come back
    unchanged from the bound construction. If these move, the ruling was
    made against different numbers than the code produces."""
    mat = _cap("max_admissible_trials", "M-4")
    table = {0.0: 109, 0.1: 55, 0.2: 31, 0.3: 19, 0.4: 12,
             0.493: 8, 0.6: 5, 0.802: 2, 0.829: 2}
    for rho, want in table.items():
        got = mat(SPAN_BTC_ETH, 1.0, 252, vif=_vif_ar1(rho))
        assert got == want, (
            f"M-13(1): ceiling at rho={rho} must be {want}, got {got}. "
            "These are the figures the Principal's I-057 ruling was made "
            "against (SPEC-001 section 4.2).")


def test_mbs_08_ceiling_is_non_increasing_in_vif():
    """M-4 / C-1(ii)."""
    mat = _cap("max_admissible_trials", "M-4")
    prev = None
    for vif in np.linspace(1.0, 12.0, 60):
        got = mat(SPAN_BTC_ETH, 1.0, 252, vif=float(vif))
        if prev is not None:
            assert got <= prev, "C-1(ii): the ceiling must never rise with VIF"
        prev = got


def test_mbs_09_the_explicit_min_never_binds():
    """M-5: N_max = min(n_max_iid, n_max_serial) is written in code because
    the ruling is written as a min. It must provably never bind."""
    mat = _cap("max_admissible_trials", "M-4")
    rng = np.random.default_rng(17)
    for _ in range(400):
        span = float(rng.uniform(0.5, 30.0))
        sr = float(rng.uniform(0.2, 3.0))
        vif = float(rng.uniform(1.0, 25.0))
        iid = mat(span, sr, 252, vif=1.0)
        ser = mat(span, sr, 252, vif=vif)
        assert min(iid, ser) == ser, (
            "M-5: the explicit min must never bind -- if it does, M-2's "
            "max has been broken")


# ======================================================================
# M-6 / M-7 -- the Gate 1 criterion
# ======================================================================

def test_mbs_10_gate1_length_criterion_is_serial_corrected(registry):
    """M-6: renamed, graded on the serial figure, and the i.i.d. figure,
    the VIF and N_max all travel on the criterion's face."""
    _seed_family(registry, rho=0.6, T=1400)
    r = _ar1(1400, 0.6, 0.0006, 999)
    idx = pd.bdate_range("2016-01-01", periods=1400)
    rep = evaluate_gate1("F", "hac", registry, r, 252,
                         backtest_years=(idx.max() - idx.min()).days / 365.25,
                         oos_index=idx)

    crit = _criterion(rep, "backtest length")
    assert "serial" in crit.name.lower(), (
        "M-6: the criterion must be renamed so an excerpt of the table "
        "cannot be read as the uncorrected requirement")
    note = (crit.note or "").lower()
    for needle in ("minbtl(iid)", "vif", "n_max"):
        assert needle in note, f"M-6: criterion note must carry {needle!r}"

    for field in ("minbtl_iid_years", "minbtl_serial_years", "vif_gate",
                  "vif_hac", "vif_ar1", "vif_rho_hat",
                  "n_max_admissible_iid", "n_max_admissible_serial"):
        if not hasattr(rep, field):
            pytest.fail(
                f"NOT IMPLEMENTED: ValidationReport.{field} does not exist "
                "(VALIDATION-SPEC-002 M-10).")

    assert rep.minbtl_serial_years >= rep.minbtl_iid_years
    assert rep.n_max_admissible_serial <= rep.n_max_admissible_iid


def test_mbs_11_zero_logged_trials_is_insufficient_data_not_pass(registry):
    """M-7 / R-11: n_inherited alone carries no return series, so the VIF is
    unmeasurable. A VIF of 1 is NOT a neutral default -- it is the
    permissive assumption this document exists to remove."""
    registry.open_hypothesis("S", "s", "m", "f", "u", "h", "sc",
                             trial_budget=500, n_inherited=40)
    r = _ar1(1400, 0.1, 0.0012, 5)
    idx = pd.bdate_range("2016-01-01", periods=1400)
    rep = evaluate_gate1("S", "hac", registry, r, 252,
                         backtest_years=(idx.max() - idx.min()).days / 365.25,
                         oos_index=idx)

    crit = _criterion(rep, "backtest length")
    assert crit.verdict == "INSUFFICIENT-DATA", (
        "M-7: with zero logged trials the length criterion must be "
        f"INSUFFICIENT-DATA, never PASS or FAIL. Got {crit.verdict!r}.")
    assert "unmeasurable" in (crit.note or "").lower()
    assert rep.overall != "PASS"


# ======================================================================
# R-16 -- the bar-frequency evasion
# ======================================================================

def test_mbs_12_corrected_minbtl_is_approximately_frequency_invariant():
    """R-16 / section 6.1. Under the UNCORRECTED statistic a family can buy
    length by sampling more finely -- the exact evasion Ruling 004 section
    2.1 declared impossible. The correction is what closes it.

    Tolerance: 20%, set from a measured 17% spread plus margin [inferred].
    If a correct implementation misses this band, ESCALATE in writing
    before touching the test (I-058's lesson).
    """
    fn = _cap("min_backtest_length_years_serial", "M-2")
    vi = _cap("variance_inflation", "R-2")

    for rho in (0.3, 0.5, 0.83):
        for seed in (1011, 1012, 1013):
            r = _ar1(2398, rho, 0.0, seed)
            r = r + (1.0 / math.sqrt(365)) * r.std(ddof=1) * math.sqrt(
                _vif_ar1(rho))
            corrected, uncorrected = [], []
            for agg, ppy in ((1, 365), (5, 73), (7, 52)):
                n = (r.size // agg) * agg
                ra = r[:n].reshape(-1, agg).sum(axis=1)
                sr = stats.sharpe_annual(ra, ppy)
                if sr <= 0:
                    pytest.skip("degenerate draw")
                uncorrected.append(
                    stats.min_backtest_length_years(86, sr, ppy))
                corrected.append(
                    fn(86, sr, ppy, vif=vi(ra).vif_gate))

            spread_c = max(corrected) / min(corrected)
            spread_u = max(uncorrected) / min(uncorrected)
            assert spread_c <= 1.20, (
                f"R-16: corrected MinBTL varies by {spread_c:.2f}x across "
                f"bar sizes at rho={rho} -- the aggregation evasion is open")
            assert spread_c < spread_u, (
                "R-16: the correction must REDUCE frequency sensitivity; "
                f"corrected {spread_c:.2f}x vs uncorrected {spread_u:.2f}x")


# ======================================================================
# Section 7.2 -- the PREREG-002 arithmetic, pinned
# ======================================================================

def test_mbs_13_prereg002_binding_rho_is_0034_not_0100():
    """Section 7.2 -- GUARD, green today. The Principal's stated trigger
    ('if rho_hat measures >= 0.1') understates the tightness by ~3x. This
    test pins the correction so it cannot drift back."""
    mb86 = stats.min_backtest_length_years(86, 1.0, 252)
    assert mb86 == pytest.approx(6.1359, abs=1e-3)

    vif_max = SPAN_BTC_ETH / mb86
    assert vif_max == pytest.approx(1.0709, abs=1e-3)

    rho_max = (vif_max - 1.0) / (vif_max + 1.0)
    assert rho_max == pytest.approx(0.0342, abs=1e-3), (
        "Section 7.2: PREREG-002's declared N=86 survives the length "
        "criterion only up to an AR(1) rho_hat of 0.034")

    # and at the Principal's stated 0.1 the family is 31 trials over, not
    # marginally over
    assert _ref_ceiling(SPAN_BTC_ETH, 1.0, _vif_ar1(0.10)) == 55
