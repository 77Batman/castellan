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

----------------------------------------------------------------------
2026-08-06 -- RULING 005-A's SECOND CLOSURE CONDITION (I-065)
----------------------------------------------------------------------
The Principal's closure condition for RULING 005-A is BOTH halves:
`test_mono_03` green on Seat 9's one-line D-2 clamp, AND this file's
C-4 sweep extended to the DSR side below `vif = 1`, "so the branch that
hid this defect is never unswept again."

The root cause, in my own words at I-065: `test_mono_05` swept
`vif in (0, 50]` but carried the C-1(iv) assertion ONLY on the MinBTL
side, leaving the DSR side of (iv) unswept below 1 -- and `test_mono_04`,
the dedicated sub-1 sweep, tested `min_backtest_length_years_serial` and
`max_admissible_trials` and NOT `deflated_sharpe_ratio_serial` at all.
Two tests whose names promise the sub-1 branch, neither of which reached
DSR there. That is why a specification defect reached an implementer
instead of a test.

Three additions close it, and they are additive -- the existing draw
sequence of `test_mono_05` is bit-identical (the DSR side draws from an
independent generator, `_RNG_DSR_SEED`, precisely so the pre-existing
coverage is not perturbed):

  * `test_mono_05`  -- now carries C-1(iii) and BOTH sides of C-1(iv)
                       on a LOG-uniform `vif` draw, ~64% of which lands
                       below 1, plus the (iii)+(iv)+D-5 equality theorem
                       on (0, 1].
  * `test_mono_08`  -- the SENTINEL: reconstructs the pre-RULING-005-A
                       literal D-2 locally and asserts the extended
                       sweep's own draw distribution DOES produce
                       C-1(iv) violations under it. A regression test
                       that cannot fail on the defect it was written for
                       is decoration; this proves the sweep has teeth.
  * `test_mono_09`  -- the dense deterministic grid on (0, 1], closing
                       `test_mono_04`'s face of the same gap.
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


# The DSR side of the C-4 sweep draws from its OWN generator so that the
# pre-existing (i)/(ii)/MinBTL-(iv) draw sequence in `test_mono_05` is
# bit-identical to what it was before the I-065 extension. Additive
# coverage must not silently re-roll existing coverage.
_RNG_DSR_SEED = 20260806


def _log_uniform_vif(rng, lo=1e-3, hi=50.0):
    """A `vif` draw that actually populates the sub-1 branch.

    `rng.uniform(0.001, 50.0)` -- what `test_mono_05` drew before -- puts
    only ~2% of its mass below 1, which is the arithmetic reason the gap
    survived: the branch was nominally in range and practically unswept.
    Log-uniform over the same support puts ~64% below 1.
    """
    return float(10.0 ** rng.uniform(math.log10(lo), math.log10(hi)))


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
    """C-4: 2,000 draws from a fixed seed. Asserts C-1 (i), (ii), and --
    since the I-065 extension -- BOTH sides of (iv), on a draw
    distribution that actually populates `vif < 1`.

    RULING 005-A's second closure condition. Before the extension this
    test asserted (iv) on the MinBTL side only; the DSR side below 1 was
    unswept, and a specification defect that made `DSR_serial` RISE with
    measured serial dependence lived there undetected until an
    implementer found it by hand (I-065).

    The MinBTL/ceiling block below is unchanged, draw for draw. The DSR
    block draws `vif` log-uniformly from an independent generator.
    """
    mb = _cap("min_backtest_length_years_serial", "M-2")
    mat = _cap("max_admissible_trials", "M-4")
    ds = _cap("deflated_sharpe_ratio_serial", "D-2")
    rng = np.random.default_rng(20260804)
    rng_d = np.random.default_rng(_RNG_DSR_SEED)

    n_sub_one = 0          # DSR draws that actually landed below 1
    n_sub_one_negz = 0     # ... of those, the negative-z ones D-6 exists for

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

        # ---- I-065 extension: the DSR side, swept below 1 -------------
        # Independent generator; nothing above this line is perturbed.
        T = int(rng_d.integers(40, 400))
        # mu spans both signs so roughly half the draws have z < 0 --
        # the branch on which the literal D-2 loosened.
        r = rng_d.standard_normal(T) * 0.01 + rng_d.uniform(-0.003, 0.003)
        n_d = int(rng_d.integers(2, 100_000))
        sigma = float(rng_d.uniform(0.005, 0.8))
        v_lo = _log_uniform_vif(rng_d)
        v_hi = v_lo * float(10.0 ** rng_d.uniform(0.01, 2.0))

        dsr_iid = stats.deflated_sharpe_ratio(r, n_d, sigma)
        if math.isnan(dsr_iid):
            continue
        got_lo = ds(r, n_d, sigma, vif=v_lo)
        got_hi = ds(r, n_d, sigma, vif=v_hi)

        # (iii) never rises above the uncorrected figure, at ANY vif > 0
        assert got_lo <= dsr_iid + 1e-12, (
            f"C-1(iii) at draw {k}: vif={v_lo:.6f} raised DSR from "
            f"{dsr_iid:.8f} to {got_lo:.8f}")

        # (iv), DSR side -- THE ASSERTION THAT WAS MISSING. Non-increasing
        # in vif across an ORDERED PAIR that may straddle 1. The I-065
        # defect was found at exactly this shape: vif raised 0.591 ->
        # 12.376, DSR rose 0.4741 -> 0.4801.
        assert got_hi <= got_lo + 1e-12, (
            f"C-1(iv) DSR side at draw {k}: vif raised {v_lo:.6f} -> "
            f"{v_hi:.6f} and DSR ROSE {got_lo:.8f} -> {got_hi:.8f}. More "
            "measured serial dependence produced a more permissive "
            "statistic -- the exact operation section 4 exists to prevent.")

        if v_lo < 1.0:
            n_sub_one += 1
            # (iii)+(iv)+D-5 force EQUALITY on (0, 1]: a theorem of C-1,
            # not an extra demand (RULING 005 section 3, third argument).
            assert got_lo == dsr_iid, (
                f"C-1 equality theorem at draw {k}: vif={v_lo:.6f} < 1 "
                f"must yield EXACTLY the uncorrected DSR {dsr_iid!r}, got "
                f"{got_lo!r}")
            if dsr_iid < 0.5:
                n_sub_one_negz += 1

    # The extension is only real if the branch is genuinely populated.
    # A sweep that nominally covers (0, 1] and lands there twice is how
    # this gap survived the first time.
    assert n_sub_one > 800, (
        "the DSR sweep must actually populate the sub-1 branch; only "
        f"{n_sub_one} of 2000 draws had vif < 1")
    assert n_sub_one_negz > 200, (
        "the sub-1 branch must be exercised with z < 0, which is where "
        f"the literal D-2 loosened; only {n_sub_one_negz} such draws")


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


# ======================================================================
# I-065 / RULING 005-A -- the second closure condition
# ======================================================================

def _dsr_serial_literal(returns, n_trials, sigma, *, vif):
    """The PRE-RULING-005-A literal D-2, reconstructed locally.

        z_serial = z_iid / sqrt(vif)          <- no max(vif, 1.0)
        DSR      = min(Phi(z_serial), Phi(z_iid))

    This is the construction that shipped in the specification I wrote,
    and it is here for exactly one purpose: to prove that the extended
    sweep detects it. It is NOT an alternative implementation and nothing
    in `castellan/` may call it.
    """
    z_iid = stats._dsr_z(returns, n_trials, sigma)
    if math.isnan(z_iid):
        return float("nan")
    return float(min(norm.cdf(z_iid / math.sqrt(vif)), norm.cdf(z_iid)))


def test_mono_08_sentinel_the_extended_sweep_detects_the_defect_it_was_written_for():
    """I-065's root cause, closed mechanically rather than asserted.

    A regression test that cannot fail on the defect that motivated it is
    decoration. This runs `test_mono_05`'s OWN DSR draw distribution
    against the pre-RULING-005-A construction and requires it to produce
    C-1(iv) violations -- and to produce them ONLY below `vif = 1`, which
    is the precise localisation in I-065 (3,848 violations / 200,000
    draws, all on the sub-1 branch, all at z < 0).

    If a future edit narrows the sweep back onto `vif >= 1`, this test
    goes red because the violations stop being reachable -- which is the
    property the Principal's closure condition actually asked for: "so
    the branch that hid this defect is never unswept again."

    Measured on this seed, 2026-08-06: 2,000 usable draws, 1,283 with
    `vif < 1` (1,254 of them at z < 0), and **112 C-1(iv) violations**
    under the pre-RULING-005-A construction, **zero** of them at
    `vif >= 1`. The floor below is 100, i.e. ~11% margin -- deliberately
    tight, because any edit that moves the count is an edit to the
    sweep's reach and should be looked at rather than absorbed.
    """
    ds = _cap("deflated_sharpe_ratio_serial", "D-2")
    rng_d = np.random.default_rng(_RNG_DSR_SEED)

    violations_literal = 0
    violations_literal_at_or_above_one = 0
    violations_shipped = 0

    for _ in range(2000):
        T = int(rng_d.integers(40, 400))
        r = rng_d.standard_normal(T) * 0.01 + rng_d.uniform(-0.003, 0.003)
        n_d = int(rng_d.integers(2, 100_000))
        sigma = float(rng_d.uniform(0.005, 0.8))
        v_lo = _log_uniform_vif(rng_d)
        v_hi = v_lo * float(10.0 ** rng_d.uniform(0.01, 2.0))

        if math.isnan(stats.deflated_sharpe_ratio(r, n_d, sigma)):
            continue

        lit_lo = _dsr_serial_literal(r, n_d, sigma, vif=v_lo)
        lit_hi = _dsr_serial_literal(r, n_d, sigma, vif=v_hi)
        if lit_hi > lit_lo + 1e-12:
            violations_literal += 1
            if v_lo >= 1.0:
                violations_literal_at_or_above_one += 1

        if ds(r, n_d, sigma, vif=v_hi) > ds(r, n_d, sigma, vif=v_lo) + 1e-12:
            violations_shipped += 1

    assert violations_literal > 100, (
        "SWEEP HAS NO TEETH: the draw distribution in test_mono_05 does "
        "not reach the defect it exists to catch. It produced "
        f"{violations_literal} C-1(iv) violations under the pre-RULING-005-A "
        "construction; a distribution that cannot fail on the known defect "
        "cannot protect against its return.")
    assert violations_literal_at_or_above_one == 0, (
        "I-065's localisation is wrong: the literal construction violated "
        f"C-1(iv) at vif >= 1 in {violations_literal_at_or_above_one} draws. "
        "The defect was ruled to live strictly below 1; if it does not, "
        "RULING 005-A's one-line clamp is not a sufficient remedy and this "
        "interrupts the Principal.")
    assert violations_shipped == 0, (
        "C-1(iv) VIOLATED by the shipped construction in "
        f"{violations_shipped} draws. The D-2 clamp has been removed, "
        "bypassed, or defeated.")


def test_mono_09_dsr_exact_equality_on_a_dense_sub_one_grid():
    """Closes `test_mono_04`'s face of the same gap.

    `test_mono_04` is the file's dedicated sub-1 sweep and it tested
    `min_backtest_length_years_serial` and `max_admissible_trials` and
    NOT `deflated_sharpe_ratio_serial` -- so the two tests whose names
    promised the sub-1 branch both stopped short of DSR there.

    Deterministic grid, both signs of z, exact equality (not approx):
    the (iii)+(iv)+D-5 theorem says DSR_serial IS DSR_iid on (0, 1].
    """
    ds = _cap("deflated_sharpe_ratio_serial", "D-2")
    rng = np.random.default_rng(65065)

    grid = [1e-6, 1e-4, 0.001, 0.01, 0.1, 0.25, 0.5, 0.591, 0.9, 0.99,
            0.999, 0.999999, 1.0]
    checked_negative_z = 0

    for mu in (-0.004, -0.002, -0.0005, 0.0, 0.0005, 0.002, 0.004):
        r = rng.standard_normal(300) * 0.01 + mu
        for n in (2, 86, 500, 31_252):
            for sigma in (0.01, 0.1, 0.6):
                iid = stats.deflated_sharpe_ratio(r, n, sigma)
                if math.isnan(iid):
                    continue
                if iid < 0.5:
                    checked_negative_z += 1
                for vif in grid:
                    assert ds(r, n, sigma, vif=vif) == iid, (
                        f"equality theorem violated at vif={vif}, n={n}, "
                        f"sigma={sigma}, mu={mu}: DSR_iid={iid!r}, "
                        f"DSR_serial={ds(r, n, sigma, vif=vif)!r}")

    assert checked_negative_z > 20, (
        "the grid must exercise z < 0, which is the sign on which the "
        f"literal construction loosened; only {checked_negative_z} cases")
