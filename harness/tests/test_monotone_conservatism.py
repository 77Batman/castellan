"""Acceptance tests for VALIDATION-SPEC-002 section 4 (C-1 ... C-6) —
monotone-conservatism, enforced mechanically.

Authored by the Head of Quantitative Validation BEFORE implementation.

THIS FILE IS THE CLAUSE. The Principal's I-057 ruling rests on the property
that measurement can only tighten, never loosen -- that is what keeps it out
of I-029(d) territory. These tests are that property made mechanical.

    "N_max = min(109, corrected-MinBTL ceiling at rho_hat) ... This is
     monotone-conservative -- measurement can only tighten, never loosen,
     so it is not the I-029(d) operation; it is the min(t_NW, t_raw)
     construction extended to N."   -- the Principal, 2026-08-04

SEAT 9 DOES NOT MODIFY ANY TEST IN THIS FILE UNDER ANY CIRCUMSTANCES.
A failure here is escalated to Validation in writing (Ruling 004 section 11).
If a future change makes any of these fail, that change is a threshold
movement under Charter section 2 regardless of how it is described, and it
interrupts the Principal.

RED BY DESIGN.
"""

import math

import numpy as np
import pytest
from scipy.stats import norm

from castellan import stats


def _cap(name, clause):
    if not hasattr(stats, name):
        pytest.fail(
            f"NOT IMPLEMENTED: castellan.stats.{name} does not exist. "
            f"Required by VALIDATION-SPEC-002 clause {clause} (I-057)."
        )
    return getattr(stats, name)


# ======================================================================
# C-1 (i) and (iii) -- the two directions
# ======================================================================

def test_mono_01_minbtl_never_shortens():
    """C-1(i): MinBTL_serial >= MinBTL_iid for EVERY vif > 0, including
    vif < 1. The guarantee must not depend on the estimator's floor."""
    fn = _cap("min_backtest_length_years_serial", "M-2")
    for n in (2, 25, 86, 109, 1000, 500_000):
        for sr in (0.25, 1.0, 2.0):
            iid = stats.min_backtest_length_years(n, sr, 252)
            for vif in (0.001, 0.1, 0.5, 0.99, 1.0, 1.01, 2.0, 50.0):
                assert fn(n, sr, 252, vif=vif) >= iid - 1e-12, (
                    f"C-1(i) VIOLATED at n={n}, sr={sr}, vif={vif}: the "
                    "corrected requirement is SHORTER than the uncorrected "
                    "one. The correction has become a loosening.")


def test_mono_02_dsr_never_rises():
    """C-1(iii): DSR_serial <= DSR_iid for EVERY vif > 0."""
    fn = _cap("deflated_sharpe_ratio_serial", "D-2")
    rng = np.random.default_rng(2)
    for _ in range(150):
        T = int(rng.integers(60, 600))
        r = rng.standard_normal(T) * 0.01 + rng.uniform(-0.002, 0.003)
        n = int(rng.integers(2, 20_000))
        sigma = float(rng.uniform(0.01, 0.6))
        iid = stats.deflated_sharpe_ratio(r, n, sigma)
        if math.isnan(iid):
            continue
        for vif in (0.01, 0.5, 0.99, 1.0, 1.5, 12.0):
            got = fn(r, n, sigma, vif=vif)
            assert got <= iid + 1e-12, (
                f"C-1(iii) VIOLATED at vif={vif}: DSR rose from {iid:.6f} "
                f"to {got:.6f}. D-6's min has been removed or bypassed.")


# ======================================================================
# C-3 -- THE STRUCTURAL TEST: a deliberately loosening VIF is injected
# ======================================================================

def test_mono_03_injected_loosening_vif_is_ignored_exactly():
    """C-3. vif=0.25 is a value the estimator can NEVER produce (R-2's
    floor). Injecting it proves the consumer-layer guarantee does not
    depend on reading the estimator's code correctly.

    This is why M-2 and D-2 take `vif` as an explicit required argument
    instead of computing it internally. Seat 9 may not collapse estimation
    and consumption into one function for convenience -- doing so makes
    this test unwritable and the guarantee unverifiable.
    """
    mb = _cap("min_backtest_length_years_serial", "M-2")
    ds = _cap("deflated_sharpe_ratio_serial", "D-2")
    mat = _cap("max_admissible_trials", "M-4")

    for n in (2, 86, 109, 10_000):
        assert mb(n, 1.0, 252, vif=0.25) == stats.min_backtest_length_years(
            n, 1.0, 252), (
            "C-3: an injected vif of 0.25 must yield EXACTLY the "
            "uncorrected requirement, not a shortened one")

    rng = np.random.default_rng(9)
    r = rng.standard_normal(400) * 0.01 + 0.0008
    iid = stats.deflated_sharpe_ratio(r, 500, 0.1)
    assert ds(r, 500, 0.1, vif=0.25) == pytest.approx(iid, abs=1e-12)

    assert mat(6.571, 1.0, 252, vif=0.25) == mat(6.571, 1.0, 252, vif=1.0), (
        "C-3: the ceiling must not RISE above its VIF=1 value on an "
        "injected loosening VIF -- that is precisely the I-029(d) operation")


def test_mono_04_sweep_of_loosening_vifs():
    """C-3: no loosening at any vif < 1."""
    mb = _cap("min_backtest_length_years_serial", "M-2")
    mat = _cap("max_admissible_trials", "M-4")
    base_mb = stats.min_backtest_length_years(86, 1.0, 252)
    base_ceiling = mat(6.571, 1.0, 252, vif=1.0)
    for vif in (0.01, 0.1, 0.5, 0.9, 0.999):
        assert mb(86, 1.0, 252, vif=vif) == base_mb
        assert mat(6.571, 1.0, 252, vif=vif) <= base_ceiling


# ======================================================================
# C-4 -- the randomized property tests that catch a future regression
# ======================================================================

def test_mono_05_randomized_property_minbtl_and_ceiling():
    """C-4: 2,000 draws from a fixed seed. Asserts C-1 (i), (ii) and the
    MinBTL half of (iv)."""
    mb = _cap("min_backtest_length_years_serial", "M-2")
    mat = _cap("max_admissible_trials", "M-4")
    rng = np.random.default_rng(20260804)

    for k in range(2000):
        n = int(rng.integers(2, 1_000_000))
        sr = float(rng.uniform(0.05, 5.0))
        ppy = int(rng.choice([12, 52, 252, 365]))
        vif = float(rng.uniform(0.001, 50.0))

        iid = stats.min_backtest_length_years(n, sr, ppy)
        ser = mb(n, sr, ppy, vif=vif)

        # (i) never shortens
        assert ser >= iid - 1e-9, f"C-1(i) at draw {k}"

        # (iv) non-decreasing in vif
        assert mb(n, sr, ppy, vif=vif * 1.5) >= ser - 1e-9, (
            f"C-1(iv) at draw {k}: MinBTL_serial fell when VIF rose")

        # (ii) the ceiling never rises
        span = float(rng.uniform(0.5, 40.0))
        assert mat(span, sr, ppy, vif=max(vif, 1.0)) <= mat(
            span, sr, ppy, vif=1.0), f"C-1(ii) at draw {k}"


def test_mono_06_randomized_property_dsr():
    """C-4: 2,000 draws from a fixed seed, deliberately including the
    negative-z cases D-6 exists for."""
    ds = _cap("deflated_sharpe_ratio_serial", "D-2")
    rng = np.random.default_rng(20260805)

    n_negative = 0
    for k in range(2000):
        T = int(rng.integers(40, 400))
        # mu spans both signs so roughly half the draws have z < 0
        r = rng.standard_normal(T) * 0.01 + rng.uniform(-0.003, 0.003)
        n = int(rng.integers(2, 100_000))
        sigma = float(rng.uniform(0.005, 0.8))
        vif = float(rng.uniform(0.001, 50.0))

        iid = stats.deflated_sharpe_ratio(r, n, sigma)
        if math.isnan(iid):
            continue
        got = ds(r, n, sigma, vif=vif)
        assert got <= iid + 1e-12, (
            f"C-1(iii) at draw {k}: vif={vif:.4f} raised DSR from "
            f"{iid:.8f} to {got:.8f}")
        if iid < 0.5:
            n_negative += 1
        # (iv) non-increasing in vif, on the tightening side only
        if vif >= 1.0:
            assert ds(r, n, sigma, vif=vif * 1.5) <= got + 1e-12, (
                f"C-1(iv) at draw {k}: DSR rose when VIF rose")

    assert n_negative > 200, (
        "the draw distribution must actually exercise the negative-z branch "
        f"D-6 exists for; only {n_negative} draws had z < 0")


# ======================================================================
# C-2 -- the two enforcements are independent
# ======================================================================

def test_mono_07_estimator_and_consumer_guards_are_independent():
    """C-2: a single enforcement is a single point of failure. The
    estimator floors per series (R-7) AND the consumer floors again (M-2,
    D-6). A future seat must defeat both, in two files, to make the
    machinery loosen."""
    vi = _cap("variance_inflation", "R-2")
    mb = _cap("min_backtest_length_years_serial", "M-2")

    # estimator layer: a mean-reverting series cannot produce vif < 1
    rng = np.random.default_rng(31)
    e = rng.standard_normal(3000)
    reverting = e[1:] - 0.6 * e[:-1]
    got = vi(reverting)
    assert got.vif_hac < 1.0, "fixture: the raw HAC term is genuinely < 1"
    assert got.vif_gate >= 1.0, "C-2 estimator layer: R-7's floor"

    # consumer layer: even handed a sub-1 VIF directly, it cannot shorten
    assert mb(86, 1.0, 252, vif=got.vif_hac) == \
        stats.min_backtest_length_years(86, 1.0, 252), \
        "C-2 consumer layer: M-2's max"
