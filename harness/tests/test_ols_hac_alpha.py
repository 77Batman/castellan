"""Acceptance tests for I-380 — the OLS + Newey-West/HAC alpha estimator
PREREG-002 sec5.2 leg (i) requires and the harness did not implement.

Authored by the Head of Data & Infrastructure under dispatch S4-D-032,
BEFORE the implementation existed in ``castellan.stats`` (RED-FIRST,
D-012's rider). Acceptance here is NOT authored by this seat's own
judgment of correctness: it is computed against ``statsmodels`` --
``sm.OLS(y, sm.add_constant(x)).fit(cov_type="HAC", cov_kwds={...})`` --
agreement to 1e-8, per the Principal's 2026-09-16 ruling that the oracle
for this estimator is external to the firm.

Every test below has a corresponding entry in this dispatch's red-first
log (research/DATA-IMPL-015-leg-i-estimator.md), naming the specific
mutation of the reference implementation that was verified to make that
test fail before the passing implementation was written.
"""

import math

import numpy as np
import pytest
import statsmodels.api as sm

from castellan import stats

LAG = 21  # PREREG-002 sec5.2(i): pre-committed, one calendar month


def _oracle(y, x, lag, use_correction=False):
    """The external oracle, called exactly as the Principal's ruling
    specifies. Never reimplemented, never approximated -- this IS the
    acceptance standard, not a check against it."""
    X = sm.add_constant(x)
    res = sm.OLS(y, X).fit(
        cov_type="HAC", cov_kwds={"maxlags": lag, "use_correction": use_correction}
    )
    return {
        "alpha": res.params[0], "beta": res.params[1],
        "se_alpha": res.bse[0], "se_beta": res.bse[1],
        "t_alpha": res.tvalues[0], "t_beta": res.tvalues[1],
    }


def _assert_matches_oracle(y, x, lag, use_correction=False, tol=1e-8):
    got = stats.ols_alpha_tstat_hac(y, x, lag, use_correction=use_correction)
    want = _oracle(y, x, lag, use_correction=use_correction)
    assert got.alpha == pytest.approx(want["alpha"], abs=tol)
    assert got.beta == pytest.approx(want["beta"], abs=tol)
    assert got.se_alpha == pytest.approx(want["se_alpha"], abs=tol)
    assert got.se_beta == pytest.approx(want["se_beta"], abs=tol)
    assert got.t_alpha == pytest.approx(want["t_alpha"], abs=tol)
    assert got.t_beta == pytest.approx(want["t_beta"], abs=tol)
    return got, want


# ======================================================================
# Oracle agreement -- synthetic cases (Principal ruling 2026-09-16)
# ======================================================================

def test_oracle_known_autocorrelated_construction():
    """A true AR(1) residual (rho=0.8) — exactly the shape PREREG-002
    sec5.2(i) is worried about ("a carry residual is autocorrelated by
    construction"). Mutation that fails this: Bartlett weight formula
    off-by-one (``1 - l/lag`` instead of ``1 - l/(lag+1)``, DATA-IMPL-015
    mutation log M2) or dropped kernel symmetrization (M3)."""
    rng = np.random.default_rng(1)
    T = 2000
    x = rng.normal(0, 0.01, T)
    e = np.zeros(T)
    for i in range(1, T):
        e[i] = 0.8 * e[i - 1] + rng.normal(0, 0.005)
    y = 0.0005 + 0.3 * x + e
    got, want = _assert_matches_oracle(y, x, LAG)
    assert got.t_alpha == pytest.approx(want["t_alpha"], abs=1e-8)


def test_oracle_near_zero_alpha():
    """alpha constructed at ~1e-6, far inside the estimator's own noise
    floor -- the case where a sign or scale bug in alpha's arithmetic is
    easiest to hide. Mutation that fails this: alpha/beta column swap
    (M6, also caught directly by test_intercept_is_column_zero)."""
    rng = np.random.default_rng(2)
    T = 2000
    x = rng.normal(0, 0.02, T)
    y = 1e-6 + 1.2 * x + rng.normal(0, 0.01, T)
    _assert_matches_oracle(y, x, LAG)


def test_oracle_high_alpha():
    """alpha an order of magnitude above beta*x's own scale."""
    rng = np.random.default_rng(3)
    T = 2000
    x = rng.normal(0, 0.015, T)
    y = 0.01 + 0.5 * x + rng.normal(0, 0.008, T)
    _assert_matches_oracle(y, x, LAG)


def test_oracle_use_correction_true():
    """The one real ambiguity (small-sample correction), resolved
    explicitly: this library's ``use_correction=True`` must match
    ``cov_kwds={"maxlags": L, "use_correction": True}`` on the oracle
    side, not merely be A convention. Mutation that fails this: wrong
    divisor in the correction factor, e.g. ``nobs/(nobs-1)`` instead of
    ``nobs/(nobs-k_params)`` (M5)."""
    rng = np.random.default_rng(1)
    T = 2000
    x = rng.normal(0, 0.01, T)
    e = np.zeros(T)
    for i in range(1, T):
        e[i] = 0.8 * e[i - 1] + rng.normal(0, 0.005)
    y = 0.0005 + 0.3 * x + e
    _assert_matches_oracle(y, x, LAG, use_correction=True)


def test_oracle_default_use_correction_matches_statsmodels_default():
    """Convention resolution, made an executable test rather than only a
    docstring claim: this library's DEFAULT (no ``use_correction``
    passed) must match the oracle's default when ``cov_kwds`` omits
    ``use_correction`` entirely -- i.e. statsmodels' own
    ``get_robustcov_results`` default of False for plain "HAC". Mutation
    that fails this: flipping this library's default to True (M1)."""
    rng = np.random.default_rng(4)
    T = 1500
    x = rng.normal(0, 0.01, T)
    y = 0.0003 + 0.6 * x + rng.normal(0, 0.006, T)
    got = stats.ols_alpha_tstat_hac(y, x, LAG)  # no use_correction kwarg
    X = sm.add_constant(x)
    res = sm.OLS(y, X).fit(cov_type="HAC", cov_kwds={"maxlags": LAG})  # no use_correction kwarg either
    assert got.t_alpha == pytest.approx(res.tvalues[0], abs=1e-8)
    assert got.use_correction is False


def test_oracle_lag_zero():
    """lag=0 is a degenerate but valid Bartlett truncation (White-style).
    Mutation that fails this: Bartlett weight divide-by-``lag`` instead
    of ``lag+1`` (M2) raises ZeroDivisionError/produces nan at L=0."""
    rng = np.random.default_rng(5)
    T = 1000
    x = rng.normal(0, 0.02, T)
    y = 2e-5 + 1.2 * x + rng.normal(0, 0.01, T)
    _assert_matches_oracle(y, x, 0)


@pytest.mark.parametrize("lag", [1, 5, 10, 21, 48])
def test_oracle_agreement_across_lags(lag):
    """Same series, several truncations -- guards against a formula that
    happens to be right at one lag by coincidence (kernel weight
    mutations M2/M3 fail at every lag > 0 here, not just LAG=21)."""
    rng = np.random.default_rng(6)
    T = 3000
    x = rng.normal(0, 0.012, T)
    e = np.zeros(T)
    for i in range(1, T):
        e[i] = 0.6 * e[i - 1] + rng.normal(0, 0.004)
    y = 0.0002 + 0.4 * x + e
    _assert_matches_oracle(y, x, lag)


def test_oracle_trial1_derived_fixture():
    """(b) trial 1's derived series (Principal ruling 2026-09-16).

    ``R_bench`` here is trial 1's ACTUAL logged return series, read
    directly from ``book/registry.db`` (family
    ``funding-carry-conditioning-002``, ``trial_id=1``,
    ``config_hash=44532cc88ed7b1a9``, 2415 bars, ``periods_per_year``
    365, ``grant_id=11``). ``R_strat`` is an off-engine reconstruction
    built ONLY for this oracle-agreement test -- NEVER a leg (i) result
    -- from component panels (not a scalar reweighting of R_bench, per
    the Principal's construction correction I-376/I-377): spot leg
    constant, perp leg scaled by a reconstructed conditioning schedule
    w(t), so w(t) < 1 leaves the position net long spot. See
    research/DATA-IMPL-015-leg-i-estimator.md sec3 for the full
    construction and its parity check against trial 1's stored blob
    (max abs diff 3.69e-10, matching DATA-IMPL-014's own figure on the
    same panels).
    """
    d = np.load(
        __file__.rsplit("/", 1)[0] + "/fixtures/trial1_leg_i_oracle_fixture.npz"
    )
    assert str(d["config_hash"]) == "44532cc88ed7b1a9"
    assert int(d["trial_id"]) == 1
    assert int(d["periods_per_year"]) == 365
    R_bench = d["R_bench"]
    R_strat = d["R_strat"]
    assert R_bench.size == 2415
    got, want = _assert_matches_oracle(R_strat, R_bench, LAG)
    # sanity: this is genuinely NOT a scalar reweighting of R_bench --
    # if it were, beta would be a near-perfect fit and this check would
    # be nearly vacuous.
    assert abs(np.corrcoef(R_strat, R_bench)[0, 1]) < 0.5


# ======================================================================
# The estimator's own contract -- not oracle-agreement, but load-bearing
# ======================================================================

def test_intercept_is_column_zero():
    """t_alpha must be the INTERCEPT's t-stat, not the slope's -- the two
    are numerically distinguishable whenever alpha != beta. Mutation
    that fails this: swapping alpha/beta in the return value (M6)."""
    rng = np.random.default_rng(7)
    T = 1000
    x = rng.normal(0, 0.01, T)
    y = 0.05 + 0.001 * x + rng.normal(0, 0.002, T)  # alpha >> beta
    got = stats.ols_alpha_tstat_hac(y, x, LAG)
    assert got.alpha == pytest.approx(0.05, abs=0.01)
    assert got.beta == pytest.approx(0.001, abs=0.01)
    assert got.t_alpha > got.t_beta * 5  # alpha's t swamps beta's here


def test_joint_nan_dropping_keeps_series_aligned():
    """A NaN at index i in EITHER series drops bar i from BOTH before any
    arithmetic -- the pair must stay aligned bar-for-bar. Mutation that
    fails this: masking each series independently (different nan
    patterns -> different lengths -> misalignment or a crash) (M7)."""
    rng = np.random.default_rng(8)
    T = 500
    x = rng.normal(0, 0.01, T)
    y = 0.0004 + 0.5 * x + rng.normal(0, 0.005, T)
    x_nan = x.copy()
    y_nan = y.copy()
    x_nan[10] = np.nan
    y_nan[20] = np.nan
    got = stats.ols_alpha_tstat_hac(y_nan, x_nan, 5)
    keep = ~(np.isnan(x_nan) | np.isnan(y_nan))
    want = _oracle(y[keep], x[keep], 5)
    assert got.n == int(keep.sum())
    assert got.t_alpha == pytest.approx(want["t_alpha"], abs=1e-8)


def test_lag_must_be_nonnegative():
    """Mutation that fails this: silently taking ``abs(lag)`` instead of
    raising (M8)."""
    with pytest.raises(ValueError):
        stats.ols_alpha_tstat_hac(np.ones(50), np.ones(50), -1)


def test_lag_upper_bound_enforced():
    """Need at least one residual degree of freedom beyond the 2
    estimated parameters: ``lag < n - 2``. Mutation that fails this:
    relaxing the guard to ``lag > n - 2`` (off-by-one, admits the exact
    boundary case) (M9)."""
    rng = np.random.default_rng(9)
    y = rng.normal(0, 0.01, 10)
    x = rng.normal(0, 0.01, 10)
    with pytest.raises(ValueError):
        stats.ols_alpha_tstat_hac(y, x, 8)  # n=10, n-2=8, must raise at lag=8
    stats.ols_alpha_tstat_hac(y, x, 7)  # lag=7 < 8 must NOT raise


def test_length_mismatch_raises():
    """Mutation that fails this: removing the explicit shape check (M10)
    -- numpy would instead raise an unrelated broadcasting error or, on
    some inputs, silently produce a wrong-shaped result."""
    with pytest.raises(ValueError, match="same shape"):
        stats.ols_alpha_tstat_hac(np.ones(50), np.ones(40), 5)


def test_too_few_observations_raises():
    """Mutation that fails this: relaxing the floor from ``n < 3`` to
    ``n < 2`` (M11). At n=2 the subsequent lag-range check (``lag >=
    n-2``) ALSO raises for any valid nonnegative lag, so this test
    pins the ERROR MESSAGE, not merely "raises ValueError" -- without
    that, M11 changes nothing externally observable at n=2 and this
    test would be exactly the T-18 failure mode (a red-first test that
    cannot discriminate the mutation it names). Confirmed against M11
    directly: message-blind, this test still passes under the
    mutation; message-checked, it does not (DATA-IMPL-015 sec2 mutation
    log)."""
    with pytest.raises(ValueError, match="at least 3"):
        stats.ols_alpha_tstat_hac(np.array([0.01, 0.02]), np.array([0.01, 0.02]), 0)


def test_docstring_carries_the_unhedging_disclosure():
    """§4 hard-binding disclosure (I-376/I-377, not amendable under P7):
    this function's docstring must state that a regression on R_bench
    alone cannot separate conditioning alpha from spot-directional
    return earned while un-hedged, so the reader who calls this
    function -- not only the reader of PREREG-002 -- sees it. Mutation
    that fails this: deleting the disclosure paragraph (M12)."""
    doc = stats.ols_alpha_tstat_hac.__doc__ or ""
    assert "un-hedged" in doc or "un-hedging" in doc
    assert "spot beta" in doc or "spot-directional" in doc
    assert "Gate 1" in doc


def test_result_is_a_frozen_dataclass_with_expected_fields():
    got = stats.ols_alpha_tstat_hac(
        np.array([0.01, -0.02, 0.03, 0.01, -0.01, 0.02, 0.0, 0.01]),
        np.array([0.02, -0.01, 0.02, 0.02, -0.02, 0.01, 0.01, 0.0]),
        1,
    )
    for field in ("alpha", "beta", "se_alpha", "se_beta", "t_alpha",
                  "t_beta", "n", "lag", "use_correction"):
        assert hasattr(got, field)
    with pytest.raises(Exception):
        got.alpha = 1.0  # frozen
