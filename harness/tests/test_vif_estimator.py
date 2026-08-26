"""Acceptance tests for I-057 — rho_hat and the variance inflation factor.

Authored by the Head of Quantitative Validation under VALIDATION-SPEC-002
section 3 (R-1 ... R-16), BEFORE implementation. Seat 9 implements against
these and does not amend them; a test Seat 9 believes is wrong is escalated
to Validation in writing before it is changed (Ruling 004 section 11).

RED BY DESIGN.

A ceiling that depends on rho_hat is only as sound as rho_hat. These are
the tests for the clause most likely to be gamed later, and test_vif_11 is
the most important single assertion in the file: NO trial set, of any
construction, can lower the graded VIF below that of the series actually
being graded.

One test is a GUARD and passes today: test_vif_16, which documents the
returns_matrix truncation defect (I-062) that R-10 exists to route around.
"""

import math

import numpy as np
import pytest

from castellan import TrialRegistry, stats


def _cap(name, clause):
    if not hasattr(stats, name):
        pytest.fail(
            f"NOT IMPLEMENTED: castellan.stats.{name} does not exist. "
            f"Required by VALIDATION-SPEC-002 clause {clause} (I-057)."
        )
    return getattr(stats, name)


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


@pytest.fixture()
def registry(tmp_path):
    return TrialRegistry(str(tmp_path / "reg.db"))


# ======================================================================
# R-1 / R-2 -- the per-series estimator
# ======================================================================

def test_vif_01_result_carries_every_reported_field():
    """R-1: the report renders each of these (M-10); a missing field is a
    report that cannot state the size of its own correction."""
    vi = _cap("variance_inflation", "R-2")
    got = vi(_ar1(2000, 0.3, 0.0005, 1))
    for field in ("vif_gate", "vif_hac", "vif_ar1", "rho_hat", "lag",
                  "lag_rule", "source", "n_series_used",
                  "n_series_excluded", "eligible", "note"):
        if not hasattr(got, field):
            pytest.fail(
                f"NOT IMPLEMENTED: VIFResult.{field} does not exist "
                "(VALIDATION-SPEC-002 R-1).")


def test_vif_02_iid_series_gives_vif_near_one():
    """R-2: on a serially independent series the correction is nearly the
    identity. Estimation noise costs a little and must not cost much."""
    vi = _cap("variance_inflation", "R-2")
    vals = [vi(np.random.default_rng(500 + s).standard_normal(2398)).vif_gate
            for s in range(20)]
    assert min(vals) >= 1.0, "R-7: the floor must bind at 1.0"
    assert np.mean(vals) < 1.10, (
        f"R-2: mean VIF on i.i.d. noise is {np.mean(vals):.4f}; the "
        "estimator is costing a clean family too much")


def test_vif_03_ar1_recovers_the_theoretical_vif():
    """R-2 / M-13: the adopted max(HAC, AR(1)) construction must recover the
    truth on the one process class this firm has actually measured."""
    vi = _cap("variance_inflation", "R-2")
    for rho in (0.1, 0.2, 0.3, 0.5, 0.83):
        got = np.mean([vi(_ar1(2398, rho, 0.0, s)).vif_gate
                       for s in range(8)])
        truth = _vif_ar1(rho)
        assert got == pytest.approx(truth, rel=0.15), (
            f"R-2: at rho={rho} recovered VIF {got:.3f} vs truth "
            f"{truth:.3f}")
        assert got >= truth * 0.95, (
            "M-13: the construction may over-state; it may not under-state "
            "materially -- that error runs permissive")


def test_vif_04_hac_term_sees_structure_the_lag_one_term_cannot():
    """R-2: vif_hac uses the WHOLE Bartlett-weighted profile to lag L, not a
    single lag. Constructed so lag-1 autocorrelation is zero but lag-2 is
    not: the AR(1) plug-in is blind to it and the HAC term is not.

    label_span=8 is deliberate. At label_span=3 the E-5 lag floor is 2, the
    Bartlett weights reach only (1 - 2/4) on the lag-2 autocovariance, and a
    CORRECT implementation recovers 1.4256 against a true VIF of 2.0 -- the
    draft of this test asserted >1.5 there and would have failed correct
    code [measured; VALIDATION-SPEC-002 section 11.4].
    """
    vi = _cap("variance_inflation", "R-2")
    rng = np.random.default_rng(77)
    e = rng.standard_normal(4002)
    r = e[2:] + e[:-2]                       # x_t = e_t + e_{t-2}; rho1 = 0
    got = vi(r, label_span=8)
    assert abs(got.rho_hat) < 0.05, "fixture: lag-1 autocorrelation is ~0"
    assert got.vif_ar1 == pytest.approx(1.0, abs=0.12), (
        "the AR(1) plug-in is structurally blind to this series")
    assert got.vif_hac > 1.5, (
        "R-2: the HAC term must see the lag-2 structure; true VIF is 2.0")
    assert got.vif_gate == pytest.approx(got.vif_hac, rel=1e-9)


def test_vif_05_floor_is_applied_per_series_before_aggregation():
    """R-7 / C-2 (estimator layer). A mean-reverting series must not buy a
    discount -- not for itself, and not for a family through a median."""
    vi = _cap("variance_inflation", "R-2")
    for rho in (-0.2, -0.4, -0.6):
        got = vi(_ar1(3000, rho, 0.0, 9))
        assert got.vif_hac < 1.0, "fixture: HAC term is genuinely below 1"
        assert got.vif_gate == 1.0, (
            f"R-7: vif_gate must be floored at exactly 1.0, got "
            f"{got.vif_gate}")


def test_vif_06_negative_rho_is_reported_unclipped():
    """R-13: a report showing VIF=1.000 without showing rho_hat=-0.31 would
    conceal that a floor bound rather than that the series was clean."""
    vi = _cap("variance_inflation", "R-2")
    got = vi(_ar1(3000, -0.4, 0.0, 9))
    assert got.rho_hat < -0.2, (
        "R-13: rho_hat must be reported unclipped and signed")
    assert got.vif_ar1 == 1.0, "R-3: rho_plus = max(0, rho_hat)"


def test_vif_07_near_unit_root_is_refused_not_corrected():
    """R-5 / SPEC-001 E-9. A HAC computed that near the unit circle is not a
    correction, it is a number. INSUFFICIENT-DATA, never a silent VIF."""
    vi = _cap("variance_inflation", "R-2")
    got = vi(_ar1(4000, 0.985, 0.0, 3))
    assert abs(got.rho_hat) >= 0.97, "fixture: near unit root"
    assert got.eligible is False, (
        "R-5: |rho_hat| >= 0.97 must set eligible=False and escalate")
    assert got.note


def test_vif_08_short_series_is_ineligible():
    """R-5 / SPEC-001 E-6: T < 32 or T < 10(L+1)."""
    vi = _cap("variance_inflation", "R-2")
    assert vi(_ar1(20, 0.2, 0.0, 4)).eligible is False
    assert vi(_ar1(2000, 0.2, 0.0, 4)).eligible is True


# ======================================================================
# R-6 / R-8 -- the family estimator and the anti-gaming property
# ======================================================================

def test_vif_09_family_term_is_a_median_not_a_max():
    """R-6: `max` across trials would create an incentive NOT to log a
    trial -- the single worst incentive this firm can create. One
    pathological throwaway must not kill the family."""
    fvi = _cap("family_variance_inflation", "R-6")
    clean = [_ar1(2000, 0.05, 0.0, 200 + i) for i in range(9)]
    poison = _ar1(2000, 0.90, 0.0, 999)
    cand = _ar1(2000, 0.05, 0.0, 1)

    without = fvi(clean, cand).vif_gate
    with_poison = fvi(clean + [poison], cand).vif_gate

    assert with_poison < 2.0, (
        f"R-6: one rho=0.90 trial moved the family VIF to {with_poison:.3f}; "
        "a median must not be dominated by a single outlier")
    assert with_poison == pytest.approx(without, rel=0.35)


def test_vif_10_family_term_is_maxed_against_the_candidate():
    """R-6: a sponsor must not escape the family's typical persistence by
    advancing the one configuration whose net series is cleanest."""
    fvi = _cap("family_variance_inflation", "R-6")
    persistent = [_ar1(2000, 0.5, 0.0, 300 + i) for i in range(10)]
    clean_candidate = _ar1(2000, 0.0, 0.0, 42)

    got = fvi(persistent, clean_candidate)
    assert got.vif_gate > 2.0, (
        f"R-6: family median must lift the clean candidate; got "
        f"{got.vif_gate:.3f} against a family at rho=0.5 (VIF 3.0)")
    assert got.source == "max(candidate, family-median)"


def test_vif_11_no_trial_set_can_lower_the_graded_vif():
    """R-8 -- THE anti-gaming property, and the one a future change is most
    likely to break. vif_gate >= variance_inflation(candidate).vif_gate for
    ANY trial_series whatsoever: empty, i.i.d. noise, minimal-length,
    adversarially clean.
    """
    vi = _cap("variance_inflation", "R-2")
    fvi = _cap("family_variance_inflation", "R-6")

    cand = _ar1(2000, 0.45, 0.0, 7)
    floor = vi(cand).vif_gate
    rng = np.random.default_rng(4242)

    assert fvi([], cand).vif_gate >= floor, "R-8: empty trial set"

    for k in range(500):
        m = int(rng.integers(0, 12))
        series = []
        for _ in range(m):
            kind = rng.integers(0, 4)
            if kind == 0:                      # pure noise, maximally clean
                series.append(rng.standard_normal(300))
            elif kind == 1:                    # minimal admissible length
                series.append(rng.standard_normal(33))
            elif kind == 2:                    # below the length floor
                series.append(rng.standard_normal(int(rng.integers(2, 31))))
            else:                              # mean-reverting: VIF < 1
                series.append(_ar1(400, -0.5, 0.0, int(rng.integers(0, 1e6))))
        got = fvi(series, cand).vif_gate
        assert got >= floor - 1e-12, (
            f"R-8 VIOLATED at draw {k}: {m} logged trial series drove the "
            f"graded VIF to {got:.6f}, below the candidate's own "
            f"{floor:.6f}. Padding the registry must never buy a discount.")


def test_vif_12_zero_trials_is_unmeasurable_not_one():
    """R-11: there is no fallback to VIF=1. A VIF of 1 is not a neutral
    default -- it is the permissive assumption this document removes."""
    fvi = _cap("family_variance_inflation", "R-6")
    got = fvi([], None)
    assert got.source == "unmeasurable"
    assert got.eligible is False


def test_vif_13_too_few_trials_is_declared_candidate_only():
    """R-12: the candidate term alone is valid and conservative, but the
    report must not present one series as a family measurement."""
    fvi = _cap("family_variance_inflation", "R-6")
    cand = _ar1(2000, 0.2, 0.0, 5)
    few = [_ar1(2000, 0.2, 0.0, 600 + i) for i in range(4)]
    many = [_ar1(2000, 0.2, 0.0, 700 + i) for i in range(10)]

    assert fvi(few, cand).source == "candidate-only"
    assert fvi(few, cand).n_series_used == 4
    assert fvi(many, cand).source == "max(candidate, family-median)"


def test_vif_14_high_exclusion_rate_refuses_rather_than_discounts():
    """R-9: the dilution attack. Padding with sub-threshold trials must
    trigger a refusal, not evaporate the family term into a discount."""
    fvi = _cap("family_variance_inflation", "R-6")
    cand = _ar1(2000, 0.3, 0.0, 5)
    good = [_ar1(2000, 0.3, 0.0, 800 + i) for i in range(10)]
    runts = [np.random.default_rng(900 + i).standard_normal(15)
             for i in range(6)]           # 6/16 = 37.5% > 25%

    ok = fvi(good, cand)
    assert ok.eligible is True and ok.n_series_excluded == 0

    diluted = fvi(good + runts, cand)
    assert diluted.n_series_excluded == 6
    assert diluted.eligible is False, (
        "R-9: >25% of logged trials excluded by the length floors must set "
        "eligible=False and escalate, not silently shrink the family term")


# ======================================================================
# R-10 -- the registry accessor, and the defect it routes around
# ======================================================================

def test_vif_15_trial_returns_preserves_full_series_length(registry, grant):
    """R-10: one 20-bar logged trial must not truncate the family."""
    if not hasattr(registry, "trial_returns"):
        pytest.fail(
            "NOT IMPLEMENTED: TrialRegistry.trial_returns does not exist. "
            "Required by VALIDATION-SPEC-002 R-10 (I-057).")
    with grant(registry, "REGISTER_HYPOTHESIS"):
        registry.open_hypothesis("F", "s", "m", "f", "u", "h", "sc",
                                 trial_budget=100)
    with grant(registry, "LOG_TRIAL"):
        for n in (2000, 1500, 20):
            registry.log_trial("F", {"n": n}, _ar1(n, 0.3, 0.0, n), 252)

    got = sorted(len(s) for s in registry.trial_returns("F"))
    assert got == [20, 1500, 2000], (
        f"R-10: trial_returns must return each series at its own full "
        f"length; got {got}")


def test_vif_16_returns_matrix_truncation_is_the_defect_r10_avoids(registry, grant):
    """GUARD, green today. Documents I-062: returns_matrix truncates every
    column to the shortest common length, so one short trial collapses the
    whole family's matrix -- which also silently degrades PBO/CSCV. R-10
    exists so the VIF never consumes this."""
    with grant(registry, "REGISTER_HYPOTHESIS"):
        registry.open_hypothesis("F", "s", "m", "f", "u", "h", "sc",
                                 trial_budget=100)
    with grant(registry, "LOG_TRIAL"):
        for n in (2000, 1500, 20):
            registry.log_trial("F", {"n": n}, _ar1(n, 0.3, 0.0, n), 252)

    M = registry.returns_matrix("F")
    assert M.shape == (20, 3), (
        "I-062: a single 20-bar trial truncates the entire family matrix "
        f"to 20 bars; got {M.shape}")
