"""Acceptance tests for I-057, Item 2 — the DSR serial term.

Authored by the Head of Quantitative Validation under VALIDATION-SPEC-002
section 2 (D-1 ... D-10), BEFORE implementation. Seat 9 implements against
these and does not amend them; a test Seat 9 believes is wrong is escalated
to Validation in writing before it is changed (Ruling 004 section 11).

RED BY DESIGN.

The specification choice under test: the serial correction goes to the
SAMPLE-SIZE factor and NOT to the published non-normality denominator.
`denom` is untouched. That is what keeps the statistic reconstructable by
an external reader who sets VIF = 1.

One test is a GUARD and passes today: test_dsr_02, which pins
deflated_sharpe_ratio's output against an independent restatement so the
D-1 extraction cannot change behaviour.
"""

import math

import numpy as np
import pandas as pd
import pytest
from scipy.stats import norm, skew, kurtosis

from castellan import TrialRegistry, evaluate_gate1, stats

DSR_MIN = 0.95


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


def _ar1(T, rho, mu, seed, sd=0.01):
    rng = np.random.default_rng(seed)
    e = rng.standard_normal(T)
    x = np.empty(T)
    x[0] = e[0] / math.sqrt(1.0 - rho ** 2)
    for t in range(1, T):
        x[t] = rho * x[t - 1] + e[t]
    return mu + sd * x


def _ref_z(r, n_trials, sigma):
    """The published z, restated independently from stats.py:103-116."""
    r = np.asarray(r, dtype=float)
    r = r[~np.isnan(r)]
    T = r.size
    if T < 10:
        return float("nan")
    sr = stats.sharpe_period(r)
    g3 = float(skew(r))
    g4 = float(kurtosis(r, fisher=False))
    sr0 = stats.expected_max_sharpe(n_trials, sigma)
    denom = 1.0 - g3 * sr + ((g4 - 1.0) / 4.0) * sr ** 2
    if denom <= 0:
        return float("nan")
    return (sr - sr0) * math.sqrt(T - 1) / math.sqrt(denom)


@pytest.fixture()
def registry(tmp_path):
    return TrialRegistry(str(tmp_path / "reg.db"))


# ======================================================================
# D-1 / D-5 -- the reduction property, which is what keeps it DSR
# ======================================================================

def test_dsr_01_reduces_to_published_dsr_at_vif_one():
    """D-5: exact, not approximate. A reader who reconstructs Bailey &
    Lopez de Prado's statistic from the paper must get the firm's number
    back by setting VIF = 1."""
    fn = _cap("deflated_sharpe_ratio_serial", "D-2")
    rng = np.random.default_rng(11)
    for _ in range(200):
        T = int(rng.integers(60, 900))
        r = rng.standard_normal(T) * 0.01 + rng.uniform(-0.001, 0.002)
        n = int(rng.integers(2, 5000))
        sigma = float(rng.uniform(0.01, 0.5))
        assert fn(r, n, sigma, vif=1.0) == stats.deflated_sharpe_ratio(
            r, n, sigma), "D-5: vif=1.0 must reduce EXACTLY"


def test_dsr_02_published_dsr_is_unchanged_by_the_extraction():
    """D-1 -- GUARD, green today, must stay green. The extraction of
    _dsr_z is a refactor, not a mutation."""
    rng = np.random.default_rng(5)
    for _ in range(200):
        T = int(rng.integers(60, 900))
        r = rng.standard_normal(T) * 0.01 + rng.uniform(-0.001, 0.002)
        n = int(rng.integers(2, 5000))
        sigma = float(rng.uniform(0.01, 0.5))
        got = stats.deflated_sharpe_ratio(r, n, sigma)
        want = norm.cdf(_ref_z(r, n, sigma))
        if math.isnan(got):
            assert math.isnan(want)
        else:
            assert got == pytest.approx(want, abs=1e-12)


def test_dsr_03_requires_vif_and_rejects_bad_values():
    """D-2 / D-3a: no default, keyword-only, and a NaN VIF is never
    silently treated as 1.0."""
    fn = _cap("deflated_sharpe_ratio_serial", "D-2")
    r = _ar1(500, 0.2, 0.0006, 1)

    with pytest.raises(TypeError):
        fn(r, 100, 0.1)
    with pytest.raises(TypeError):
        fn(r, 100, 0.1, 1.5)
    for bad in (0.0, -2.0, float("nan"), float("inf")):
        with pytest.raises(ValueError):
            fn(r, 100, 0.1, vif=bad)


def test_dsr_04_z_is_divided_by_sqrt_vif():
    """D-2: the correction is an effective-sample-size substitution on the
    sqrt(T-1) factor. `denom` is NOT touched."""
    fn = _cap("deflated_sharpe_ratio_serial", "D-2")
    r = _ar1(1200, 0.3, 0.0009, 21)
    n, sigma = 60, 0.02
    z = _ref_z(r, n, sigma)
    assert z == pytest.approx(2.5953, abs=1e-3), (
        "fixture: z must be positive and moderate so the correction bites "
        "and the comparison is not degenerate")
    for vif in (1.25, 2.0, 3.0, 10.7):
        assert fn(r, n, sigma, vif=vif) == pytest.approx(
            float(norm.cdf(z / math.sqrt(vif))), abs=1e-10)


def test_dsr_05_negative_z_is_floored_not_improved():
    """D-6 -- the non-permissive floor, and the case it exists for. z is
    negative whenever the candidate falls below the deflation benchmark,
    which is the common case for an overfitted family. Dividing a negative
    z by sqrt(VIF) RAISES the DSR."""
    fn = _cap("deflated_sharpe_ratio_serial", "D-2")
    r = _ar1(800, 0.2, 0.0002, 33)
    n, sigma = 5000, 0.025
    z = _ref_z(r, n, sigma)
    assert z == pytest.approx(-2.1002, abs=1e-3), (
        "fixture: z must be negative and MODERATE -- a z of -60 makes "
        "norm.cdf underflow to exactly 0.0 and the assertion below passes "
        "trivially against a wrong implementation")

    naive = float(norm.cdf(z / math.sqrt(4.0)))     # 0.1468
    iid = float(norm.cdf(z))                        # 0.0179
    assert naive > iid + 0.1, (
        "fixture sanity: the naive correction would loosen materially")

    got = fn(r, n, sigma, vif=4.0)
    assert got == pytest.approx(iid, abs=1e-12), (
        f"D-6: with z<0 the serial figure would rise from {iid:.4f} to "
        f"{naive:.4f}; min(.,DSR_iid) must floor it at {iid:.4f}")


def test_dsr_06_right_tail_saturation_does_not_launder_a_fail():
    """D-3 -- the reason z is extracted rather than recovered from
    norm.ppf(DSR_iid). norm.cdf saturates at 1.0 for z >~ 8.3, so the
    recovery route computes inf/sqrt(vif) = inf and returns a PASS where
    the true answer is a FAIL. The left tail is exact; the right tail --
    the only tail where a family passes -- is where it breaks."""
    fn = _cap("deflated_sharpe_ratio_serial", "D-2")

    # a series whose i.i.d. z is far into the saturated right tail
    r = _ar1(2000, 0.0, 0.004, 8, sd=0.001)
    n, sigma = 2, 0.001
    z = _ref_z(r, n, sigma)
    assert z > 12.0, f"fixture: z must be deep in the saturated tail, got {z}"
    assert stats.deflated_sharpe_ratio(r, n, sigma) == 1.0, (
        "fixture: the i.i.d. DSR saturates at exactly 1.0")
    assert math.isinf(norm.ppf(stats.deflated_sharpe_ratio(r, n, sigma))), (
        "fixture: the recovery route would produce +inf")

    vif = (z / 1.0) ** 2          # chosen so the true z_serial is 1.0
    got = fn(r, n, sigma, vif=vif)
    assert got == pytest.approx(float(norm.cdf(1.0)), abs=1e-6), (
        f"D-3: true z_serial=1.0 => DSR=0.841, a FAIL. Got {got}. A "
        "norm.ppf recovery would have returned 1.0 and laundered it "
        "into a PASS.")
    assert got < DSR_MIN


# ======================================================================
# D-7 / D-8 / D-9 -- coherence, the criterion, and T_eff
# ======================================================================

def test_dsr_07_gate1_dsr_criterion_is_serial_corrected(registry):
    """D-8: renamed, graded on the floored serial figure, and the i.i.d.
    figure, VIF and T_eff all travel on the criterion's face."""
    registry.open_hypothesis("F", "s", "m", "f", "u", "h", "sc",
                             trial_budget=500)
    for i in range(12):
        registry.log_trial("F", {"i": i}, _ar1(1400, 0.5, 0.0006, 700 + i),
                           252)
    r = _ar1(1400, 0.5, 0.0011, 4242)
    idx = pd.bdate_range("2016-01-01", periods=1400)
    rep = evaluate_gate1("F", "hac", registry, r, 252,
                         backtest_years=(idx.max() - idx.min()).days / 365.25,
                         oos_index=idx)

    crit = _criterion(rep, "deflated sharpe")
    assert "serial" in crit.name.lower(), (
        "D-8: the criterion must be renamed so an excerpt cannot be read "
        "as the uncorrected statistic")
    note = (crit.note or "").lower()
    for needle in ("dsr(iid)", "vif", "t_eff"):
        assert needle in note, f"D-8: criterion note must carry {needle!r}"

    for field in ("dsr_iid", "dsr_serial", "t_eff"):
        if not hasattr(rep, field):
            pytest.fail(
                f"NOT IMPLEMENTED: ValidationReport.{field} does not exist "
                "(VALIDATION-SPEC-002 D-8/D-9).")
    assert rep.dsr_serial <= rep.dsr_iid, "C-1(iii)"


def test_dsr_08_one_vif_serves_all_three_consumers():
    """D-7: a report that deflated t by 1.9x and inflated MinBTL by 10.7x
    from the same series would be incoherent on its face."""
    vi = _cap("variance_inflation", "R-2")
    for rho in (0.2, 0.5, 0.8):
        r = _ar1(3000, rho, 0.0005, 61)
        hac = stats.sr_tstat_corrected(r)
        assert vi(r).vif_hac == pytest.approx(hac.inflation ** 2, rel=1e-9), (
            "D-7/M-3: the VIF consumed by MinBTL and DSR must be the square "
            "of the inflation the t-statistic reports for the same series")


def test_dsr_09_t_eff_is_defined_so_the_arithmetic_matches():
    """D-9: T_eff = (T-1)/VIF + 1, chosen so sqrt(T_eff - 1) equals
    sqrt(T-1)/sqrt(VIF) EXACTLY. Reporting T/VIF instead would make the
    report internally inconsistent with the number it used."""
    fn = _cap("effective_sample_size", "D-9")
    for T in (500, 2398, 4000):
        for vif in (1.0, 1.5, 3.0, 10.7):
            got = fn(T, vif)
            assert got == pytest.approx((T - 1) / vif + 1.0, rel=1e-12)
            assert math.sqrt(got - 1.0) == pytest.approx(
                math.sqrt(T - 1) / math.sqrt(vif), rel=1e-12)


def test_dsr_10_nan_inputs_propagate_as_nan_never_as_pass():
    """D-2: a degenerate series must not become a PASS through the min."""
    fn = _cap("deflated_sharpe_ratio_serial", "D-2")
    assert math.isnan(fn(np.zeros(5), 10, 0.1, vif=2.0))       # T < 10
    assert math.isnan(fn(np.zeros(500), 10, 0.1, vif=2.0))     # sd == 0
