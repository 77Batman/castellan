"""Acceptance tests for I-050 — the serially-corrected Gate 1 t-statistic.

Authored by the Head of Quantitative Validation under VALIDATION-SPEC-001,
BEFORE implementation. Seat 9 implements against these and does not amend
them; a test Seat 9 believes is wrong is escalated to Validation in writing
before it is changed (Ruling 004 §11 standing terms, I-036).

RED BY DESIGN. 17 tests; 15 fail against the harness as it stands today
[measured, this session]. That is the intended state. The two that pass
today are guards, not drivers: ``test_hac_t13_*`` (E-1, sr_tstat must not
be mutated in place) and ``test_hac_t14_*`` (E-10, the uncorrected figure
must never become a graded Criterion row). Both must still pass after the
change.

Clause references are to VALIDATION-SPEC-001 §1 (E-1 … E-16).

These tests supersede Ruling 004 §11.4's ML-T-12 as drafted: that draft
asserted the deflation ratio at a FIXED lag of 10 lies within 20% of the
asymptotic sqrt((1-rho)/(1+rho)). Against a correct Bartlett-kernel
implementation the ratio at lag 10 is 0.4197 vs an asymptotic 0.3333 —
25.9% apart [measured] — so the draft would have failed a correct
implementation. VALIDATION-SPEC-001 §5 records the correction: the
assertion is made at the Andrews-selected lag, where it holds.
"""

import math

import numpy as np
import pandas as pd
import pytest

from castellan import TrialRegistry, evaluate_gate1, stats
from castellan import carry as carry_mod

T_STAT_HURDLE = 3.0


# ----------------------------------------------------------------------
# Harness capability probes — a missing capability is a FAILURE, not an
# import-time collection error, so the red state is legible per-test.
# ----------------------------------------------------------------------

def _cap(module, name, clause):
    if not hasattr(module, name):
        pytest.fail(
            f"NOT IMPLEMENTED: {module.__name__}.{name} does not exist. "
            f"Required by VALIDATION-SPEC-001 clause {clause} (I-050)."
        )
    return getattr(module, name)


def _field(obj, name, clause):
    if not hasattr(obj, name):
        pytest.fail(
            f"NOT IMPLEMENTED: {type(obj).__name__}.{name} does not exist. "
            f"Required by VALIDATION-SPEC-001 clause {clause} (I-050)."
        )
    return getattr(obj, name)


def _criterion(report, needle):
    hits = [c for c in report.criteria if needle.lower() in c.name.lower()]
    if not hits:
        names = [c.name for c in report.criteria]
        pytest.fail(f"No criterion matching {needle!r}. Present: {names}")
    return hits[0]


# ----------------------------------------------------------------------
# Reference constructions — the SPEC's arithmetic, restated independently
# here so the tests pin the formula rather than whatever the harness does.
# ----------------------------------------------------------------------

def _ar1(T, rho, mu, seed, sd=0.01):
    rng = np.random.default_rng(seed)
    e = rng.normal(0.0, sd, T)
    x = np.empty(T)
    x[0] = e[0]
    for i in range(1, T):
        x[i] = rho * x[i - 1] + e[i]
    return x + mu


def _ref_gamma(d, lag, T):
    """E-2: autocovariance with divisor (T-1) at EVERY lag."""
    return float(d[lag:] @ d[: len(d) - lag]) / (T - 1)


def _ref_nw_t(r, lag):
    """E-2, restated independently of the harness."""
    r = np.asarray(r, dtype=float)
    T = r.size
    d = r - r.mean()
    s = _ref_gamma(d, 0, T)
    for l in range(1, lag + 1):
        s += 2.0 * (1.0 - l / (lag + 1.0)) * _ref_gamma(d, l, T)
    if s <= 0:
        return float("nan")
    return float(r.mean() / math.sqrt(s / T))


def _ref_andrews_lag(r):
    """E-3, restated independently of the harness."""
    r = np.asarray(r, dtype=float)
    T = r.size
    d = r - r.mean()
    rho = float(d[1:] @ d[:-1]) / float(d[:-1] @ d[:-1])
    rc = min(max(rho, -0.97), 0.97)
    a1 = 4.0 * rc ** 2 / ((1.0 - rc) ** 2 * (1.0 + rc) ** 2)
    lag = int(math.floor(1.1447 * (a1 * T) ** (1.0 / 3.0)))
    lag = min(max(lag, 0), min(T // 4, T - 2))
    return lag, rho


def _ref_bartlett_ar1_ratio(rho, lag):
    """Closed-form t_NW/t_raw for a true AR(1) at a Bartlett truncation."""
    s = 1.0
    for l in range(1, lag + 1):
        s += 2.0 * (1.0 - l / (lag + 1.0)) * rho ** l
    return 1.0 / math.sqrt(s)


@pytest.fixture
def registry(tmp_path):
    reg = TrialRegistry(str(tmp_path / "registry.db"))
    reg.open_hypothesis(
        family="hac", statement="s", mechanism="m",
        falsifier="net Sharpe below 0 for 2 consecutive quarters",
        universe="u", horizon="1d", success_criteria="Gate 1", trial_budget=50,
    )
    return reg


# ======================================================================
# E-1 — the uncorrected estimator is preserved, not mutated
# ======================================================================

def test_hac_t13_sr_tstat_is_not_modified():
    """E-1. GREEN TODAY BY DESIGN — a regression guard, not a driver.

    ``sr_tstat`` must keep returning SR_period * sqrt(T) exactly. If the
    correction is implemented by mutating this function in place, every
    existing call site silently changes meaning and the transition becomes
    unauditable.
    """
    r = _ar1(2000, 0.4, 0.0008, 21)
    expected = float(r.mean() / r.std(ddof=1) * math.sqrt(r.size))
    assert stats.sr_tstat(r) == pytest.approx(expected, rel=1e-12)
    assert math.isnan(stats.sr_tstat(np.array([0.01])))


# ======================================================================
# E-2 — the estimator itself
# ======================================================================

def test_hac_t1_lag0_reduces_exactly_to_sr_tstat():
    """E-2(a). At lag 0 the correction is the identity, EXACTLY.

    This is what forces the (T-1) divisor. With divisor T the two differ by
    sqrt(T/(T-1)) = 1.000125 at T=4000 [measured] and the report would carry
    a permanent unexplained wedge between its two t-statistics.
    """
    nw = _cap(stats, "sr_tstat_nw", "E-2")
    for seed in (1, 2, 3):
        r = _ar1(4000, 0.8, 0.0015, seed)
        assert nw(r, 0) == pytest.approx(stats.sr_tstat(r), rel=1e-12, abs=1e-12)


def test_hac_t2_matches_the_specified_bartlett_construction():
    """E-2. The harness's number must equal the SPEC's formula, not merely
    resemble it. Any other kernel, weighting or divisor fails here."""
    nw = _cap(stats, "sr_tstat_nw", "E-2")
    r = _ar1(4000, 0.8, 0.0015, 1)
    for lag in (0, 1, 5, 10, 48):
        assert nw(r, lag) == pytest.approx(_ref_nw_t(r, lag), rel=1e-10)


def test_hac_t3_deflates_ar1_toward_theory():
    """E-2/E-3 (supersedes ML-T-12's first two assertions).

    On AR(1) with rho = 0.8 the corrected statistic must be materially
    SMALLER than the uncorrected one, and the ratio must sit near both the
    closed-form Bartlett-truncated value at the selected lag (within 15%)
    and the asymptotic sqrt((1-rho)/(1+rho)) = 0.3333 (within 20%).

    Measured over 10 seeds: max deviation 6.3% from the closed form and
    11.4% from the asymptotic value. The tolerances are not tight.
    """
    nw = _cap(stats, "sr_tstat_nw", "E-2")
    corrected = _cap(stats, "sr_tstat_corrected", "E-5")
    rho = 0.8
    asym = math.sqrt((1 - rho) / (1 + rho))
    for seed in range(6):
        r = _ar1(4000, rho, 0.0015, seed)
        h = corrected(r)
        lag = _field(h, "lag", "E-4")
        assert lag == _ref_andrews_lag(r)[0], "E-3: lag rule must be Andrews"
        ratio = nw(r, lag) / stats.sr_tstat(r)
        assert ratio < 1.0, "E-2: positive autocorrelation must DEFLATE t"
        assert ratio == pytest.approx(
            _ref_bartlett_ar1_ratio(rho, lag), rel=0.15)
        assert ratio == pytest.approx(asym, rel=0.20)


def test_hac_t4_iid_series_is_left_alone():
    """E-2/E-3 (supersedes ML-T-12's third assertion). On a serially
    independent series the correction must be near-inert — within 5%."""
    corrected = _cap(stats, "sr_tstat_corrected", "E-5")
    for seed in range(100, 105):
        r = np.random.default_rng(seed).normal(0.0008, 0.01, 3000)
        h = corrected(r)
        t_nw = _field(h, "t_nw", "E-4")
        assert t_nw == pytest.approx(stats.sr_tstat(r), rel=0.05)


# ======================================================================
# E-3 / E-5 — lag selection, and that it is one-sided
# ======================================================================

def test_hac_t5_andrews_lag_matches_the_specified_formula():
    """E-3. The lag rule is mechanical. Pinned against an independent
    restatement of the formula so no discretion can enter."""
    fn = _cap(stats, "hac_lag_andrews", "E-3")
    for seed, rho in ((1, 0.8), (2, 0.3), (3, 0.0), (4, -0.4)):
        r = _ar1(3000, rho, 0.001, seed)
        lag, rho_hat = fn(r)
        exp_lag, exp_rho = _ref_andrews_lag(r)
        assert lag == exp_lag
        assert rho_hat == pytest.approx(exp_rho, rel=1e-10), \
            "E-3 returns the UNCLIPPED rho_hat — E-9 keys on it"


def test_hac_t6_lag_floor_is_one_sided():
    """E-5. THE CLAUSE THAT CLOSES THE DISCRETIONARY ROUTE.

    A caller may raise the lag and may never lower it. A sponsor stating
    lag 0 on an autocorrelated family gets the Andrews lag anyway.
    """
    corrected = _cap(stats, "sr_tstat_corrected", "E-5")

    r_ar = _ar1(4000, 0.8, 0.0015, 1)
    andrews = _ref_andrews_lag(r_ar)[0]
    assert andrews >= 40, "fixture sanity: Andrews must pick a long lag here"

    # stated_lag = 0 cannot defeat the data-driven lag
    assert _field(corrected(r_ar, stated_lag=0), "lag", "E-4") == andrews
    # label_span = 1 cannot defeat it either
    assert _field(corrected(r_ar, label_span=1), "lag", "E-4") == andrews
    # a LARGER stated lag is honoured
    assert _field(corrected(r_ar, stated_lag=200), "lag", "E-4") == 200

    # on an iid series Andrews picks ~0-2; a declared label span of 50 must
    # still floor the lag at 49 [measured: Andrews returns 1 on this fixture]
    r_iid = np.random.default_rng(9).normal(0.0008, 0.01, 4000)
    assert _ref_andrews_lag(r_iid)[0] <= 3, "fixture sanity"
    h = corrected(r_iid, label_span=50)
    assert _field(h, "lag", "E-4") == 49
    assert "label" in _field(h, "lag_rule", "E-4")


# ======================================================================
# E-8 — the non-permissive floor
# ======================================================================

def test_hac_t7_negative_autocorrelation_is_floored():
    """E-8. THE PRINCIPAL'S ASYMMETRY, MECHANISED.

    With rho < 0 the HAC standard error is smaller and t_nw EXCEEDS t_raw.
    Grading on it would be an estimator change that loosens, which is a §2
    threshold matter outside Validation's authority. t_gate is floored at
    the uncorrected figure; t_nw is still reported unmodified so the bind
    is visible.
    """
    corrected = _cap(stats, "sr_tstat_corrected", "E-5")
    r = _ar1(3000, -0.5, 0.0006, 7)
    h = corrected(r)
    t_raw = _field(h, "t_raw", "E-4")
    t_nw = _field(h, "t_nw", "E-4")
    t_gate = _field(h, "t_gate", "E-4")

    assert t_raw == pytest.approx(stats.sr_tstat(r), rel=1e-12)
    assert t_nw > t_raw, "fixture sanity: negative rho must inflate t_nw"
    assert t_gate == pytest.approx(t_raw, rel=1e-12), \
        "E-8: t_gate = min(t_nw, t_raw); the firm gets no credit for rho<0"
    assert _field(h, "eligible", "E-4") is True


def test_hac_t8_floor_never_binds_upward_on_positive_autocorrelation():
    """E-8. The floor must not become a way to grade on the raw figure
    when the correction bites. min() must select t_nw whenever rho > 0."""
    corrected = _cap(stats, "sr_tstat_corrected", "E-5")
    r = _ar1(4000, 0.8, 0.0015, 1)
    h = corrected(r)
    assert _field(h, "t_gate", "E-4") == pytest.approx(
        _field(h, "t_nw", "E-4"), rel=1e-12)
    assert _field(h, "t_gate", "E-4") < _field(h, "t_raw", "E-4")


# ======================================================================
# E-6 / E-7 / E-9 — refusals. Never PASS, never a silently large t.
# ======================================================================

def test_hac_t9_small_sample_is_ineligible():
    """E-6. T < 32, and T < 10*(L+1), are both INSUFFICIENT-DATA."""
    corrected = _cap(stats, "sr_tstat_corrected", "E-5")
    h = corrected(np.random.default_rng(4).normal(0.001, 0.01, 20))
    assert _field(h, "eligible", "E-4") is False
    assert _field(h, "note", "E-4").strip() != ""

    # T/L guard: 300 bars with a declared label span of 50 needs T >= 500
    h2 = corrected(np.random.default_rng(6).normal(0.001, 0.01, 300),
                   label_span=50)
    assert _field(h2, "lag", "E-4") == 49
    assert _field(h2, "eligible", "E-4") is False


def test_hac_t10_near_unit_root_is_refused():
    """E-9. |rho_hat| >= 0.97 is not a correction, it is a number."""
    corrected = _cap(stats, "sr_tstat_corrected", "E-5")
    r = _ar1(3000, 0.99, 0.0002, 3)
    h = corrected(r)
    assert abs(_field(h, "rho_hat", "E-4")) >= 0.97, "fixture sanity"
    assert _field(h, "eligible", "E-4") is False
    assert "0.97" in _field(h, "note", "E-4") or "unit root" in _field(h, "note", "E-4").lower()


def test_hac_t11_degenerate_series_returns_nan_not_a_verdict():
    """E-7. A constant series has zero long-run variance."""
    corrected = _cap(stats, "sr_tstat_corrected", "E-5")
    h = corrected(np.full(1000, 0.001))
    assert _field(h, "eligible", "E-4") is False
    assert math.isnan(_field(h, "t_gate", "E-4"))


# ======================================================================
# E-10 / E-11 — the report grades the honest number and shows both
# ======================================================================

def test_hac_t12_gate1_grades_the_corrected_statistic(registry):
    """E-10/E-11 (supersedes ML-T-13). THE TEST THAT CARRIES I-050.

    A series whose UNCORRECTED t clears 3.0 (3.868) and whose corrected t
    does not (1.357) [measured] must FAIL the criterion, must render both
    figures, and must label the uncorrected one as uncorrected and ungraded.

    A criterion that reports the honest number and grades on the flattering
    one is worse than reporting neither.
    """
    r = _ar1(4000, 0.8, 0.0015, 1)
    assert stats.sr_tstat(r) > T_STAT_HURDLE, "fixture sanity"
    lag = _ref_andrews_lag(r)[0]
    assert _ref_nw_t(r, lag) < T_STAT_HURDLE, "fixture sanity"

    idx = pd.bdate_range("2014-01-01", periods=4000)
    rep = evaluate_gate1("hac-strat", "hac", registry, r, 252,
                         backtest_years=(idx.max() - idx.min()).days / 365.25,
                         oos_index=idx)

    crit = _criterion(rep, "t-statistic")
    assert "HAC" in crit.name, "E-11: the graded criterion is renamed"
    assert crit.verdict == "FAIL"
    assert float(crit.value) == pytest.approx(_ref_nw_t(r, lag), rel=1e-6)

    assert _field(rep, "t_stat_hac", "E-10") == pytest.approx(
        _ref_nw_t(r, lag), rel=1e-6)
    assert _field(rep, "t_stat_uncorrected", "E-10") == pytest.approx(
        stats.sr_tstat(r), rel=1e-9)
    assert _field(rep, "hac_lag", "E-10") == lag
    _field(rep, "hac_lag_rule", "E-10")
    _field(rep, "hac_rho_hat", "E-10")

    md = rep.to_markdown()
    assert "uncorrected" in md.lower(), "E-10: both figures on the face"
    assert "not graded" in md.lower() or "NOT graded" in md, \
        "E-10: the uncorrected figure must be labelled ungraded"
    assert f"{stats.sr_tstat(r):.3f}" in md


def test_hac_t14_ungraded_diagnostic_is_not_a_criterion_row(registry):
    """E-10. The uncorrected figure is a REPORT FIELD, never a Criterion.

    A Criterion carries a verdict and ``overall`` is PASS only if every
    criterion is PASS. Implementing E-10 by appending to ``criteria`` would
    fail every Gate forever.
    """
    r = _ar1(3000, 0.3, 0.0012, 12)
    idx = pd.bdate_range("2014-01-01", periods=3000)
    rep = evaluate_gate1("x", "hac", registry, r, 252,
                         backtest_years=(idx.max() - idx.min()).days / 365.25,
                         oos_index=idx)
    graded = [c for c in rep.criteria if "t-statistic" in c.name.lower()]
    assert len(graded) == 1, \
        "exactly one graded t-statistic criterion; the uncorrected figure " \
        "is a report field (E-10), not a second row"
    assert "uncorrected" not in graded[0].name.lower()


# ======================================================================
# E-12 / E-13 / E-14 — the cost stack and the bisections
# ======================================================================

def test_hac_t15_cost_robustness_uses_the_corrected_estimator(registry):
    """E-12. Leaving the 2x-costs criterion uncorrected would preserve the
    whole of I-050 inside the criterion most likely to be binding."""
    r = _ar1(4000, 0.8, 0.0035, 5)
    lag = _ref_andrews_lag(r)[0]
    c = 0.0002

    def at_mult(m):
        return r - (m - 1.0) * c

    idx = pd.bdate_range("2014-01-01", periods=4000)
    rep = evaluate_gate1("x", "hac", registry, r, 252,
                         backtest_years=(idx.max() - idx.min()).days / 365.25,
                         oos_index=idx, net_returns_at_cost_multiplier=at_mult)

    crit = _criterion(rep, "2×")
    assert "HAC" in crit.name, "E-12: renamed to state the estimator"
    assert float(crit.value) == pytest.approx(
        _ref_nw_t(at_mult(2.0), lag), rel=1e-6), \
        "E-12/E-13: computed at the lag selected on the BASE series"
    assert float(crit.value) < stats.sr_tstat(at_mult(2.0))


def test_hac_t16_breakeven_uses_a_fixed_lag_and_falls(registry):
    """E-13/E-14. The breakeven multiplier must be computed on the
    corrected statistic at a lag fixed on the base series, and must land
    strictly below the multiplier the uncorrected statistic would give.

    Fixed lag is not a convenience: re-selecting the lag at each bisection
    step makes t a step function of the multiplier and the bisection
    converges on a bracket artifact rather than a breakeven — the exact
    failure I-037 records and Ruling 003 repaired.
    """
    r = _ar1(4000, 0.8, 0.0035, 5)
    lag = _ref_andrews_lag(r)[0]
    c = 0.0002

    def at_mult(m):
        return r - (m - 1.0) * c

    assert _ref_nw_t(r, lag) > T_STAT_HURDLE, "fixture sanity: bisection runs"

    idx = pd.bdate_range("2014-01-01", periods=4000)
    rep = evaluate_gate1("x", "hac", registry, r, 252,
                         backtest_years=(idx.max() - idx.min()).days / 365.25,
                         oos_index=idx, net_returns_at_cost_multiplier=at_mult)

    be = rep.breakeven_cost_multiplier
    assert be is not None and 1.0 < be < 32.0

    # the reported multiplier is where the CORRECTED t crosses the hurdle
    assert _ref_nw_t(at_mult(be), lag) == pytest.approx(T_STAT_HURDLE, abs=0.02)

    # ... and it is strictly more conservative than the uncorrected answer
    lo, hi = 1.0, 32.0
    for _ in range(40):
        mid = 0.5 * (lo + hi)
        if stats.sr_tstat(at_mult(mid)) >= T_STAT_HURDLE:
            lo = mid
        else:
            hi = mid
    assert be < lo - 1e-6, \
        "E-14: the corrected breakeven must fall, not stay put"


def test_hac_t17_carry_breakeven_is_corrected(registry):
    """E-14. carry_breakeven_bps_annual bisects on sr_tstat today
    [measured — carry.py:97,100,105]. Carry is precisely the autocorrelated
    P&L component I-050 is about; leaving this path uncorrected leaves the
    defect where it is largest.
    """
    fn = carry_mod.carry_breakeven_bps_annual
    r = _ar1(4000, 0.8, 0.0035, 5)
    lag = _ref_andrews_lag(r)[0]
    ppy = 365

    def at_shift(delta_bps):
        return r - delta_bps * 1e-4 / ppy

    try:
        be = fn(at_shift, ppy, lag=lag)
    except TypeError as exc:
        pytest.fail(
            "NOT IMPLEMENTED: carry_breakeven_bps_annual does not accept "
            f"`lag` (VALIDATION-SPEC-001 E-14). {exc}")

    assert _ref_nw_t(at_shift(be), lag) == pytest.approx(T_STAT_HURDLE, abs=0.05)
    be_uncorrected = fn(at_shift, ppy, lag=0)
    assert be < be_uncorrected, \
        "E-14: the corrected carry breakeven must be strictly tighter"
