"""Null-calibration primitives for `funding-carry-conditioning-002`'s leg
(ii) statistic (VALIDATION-SPEC-005-c11-null-calibration.md sec2/sec4).

Kept separate from `castellan.reconstruction` (the position/return-series
builder) because these functions are generic to ANY worst-tail-mean
statistic and ANY block-resampling null, not specific to this family's
position construction -- the spec itself says the schedule/statistic
ruling "binds step 3 as well as C11" (sec3.4), so this is written to be
reusable there too, not only by the one-off calibration script.

Every function here is pure arithmetic; nothing calls `run_backtest` or
constructs a `TrialRegistry`.
"""

from __future__ import annotations

import math

import numpy as np


def worst_k_mean(x: np.ndarray, k: int = 20) -> float:
    """`M(x)` (VALIDATION-SPEC-005 sec4.1): the arithmetic mean of the `k`
    smallest elements of `x`, selected from `x` ITSELF via `np.partition`
    (test D-1: the worst-`k` INDEX SET must be recomputed per series, never
    reused from a different series' ranking -- reusing it silently destroys
    the null, VALIDATION-SPEC-005's own sharpest-named acceptance row)."""
    arr = np.asarray(x, dtype=float)
    if arr.size < k:
        raise ValueError(f"worst_k_mean needs at least k={k} elements, got {arr.size}")
    return float(np.mean(np.partition(arr, k - 1)[:k]))


def worst_k_mean_batch(x: np.ndarray, k: int = 20) -> np.ndarray:
    """Row-wise :func:`worst_k_mean` over a (B, T) matrix -- each row is
    partitioned independently (D-1's guard, vectorized: `np.partition` with
    `axis=-1` computes the smallest-`k` set PER ROW, never reusing one
    row's rank order for another)."""
    arr = np.asarray(x, dtype=float)
    if arr.ndim != 2:
        raise ValueError("worst_k_mean_batch expects a (B, T) matrix")
    if arr.shape[1] < k:
        raise ValueError(f"worst_k_mean_batch needs T >= k={k}, got T={arr.shape[1]}")
    part = np.partition(arr, k - 1, axis=1)[:, :k]
    return part.mean(axis=1)


def block_boundaries(T: int, L: int) -> list[tuple[int, int]]:
    """The `n_blk = ceil(T/L)` contiguous block boundaries on `range(T)`:
    `n_blk - 1` blocks of size `L` and one final block of the remainder
    (VALIDATION-SPEC-005 sec2.2 -- `T=2415`, `L=30` gives 80 blocks of 30
    and one of 15, `n_blk=81`)."""
    n_blk = math.ceil(T / L)
    bounds = []
    start = 0
    for i in range(n_blk):
        end = min(start + L, T)
        bounds.append((start, end))
        start = end
    return bounds


def circular_block_permutation_index(
    T: int, L: int, rng: np.random.Generator, max_redraws: int = 1000
) -> np.ndarray:
    """One resample of VALIDATION-SPEC-005 sec2.2's PRIMARY construction:
    circular block permutation, without replacement.

    1. Rotation offset `s ~ Uniform{0,...,T-1}`; rotated index
       `idx = (arange(T) + s) mod T`.
    2. Cut `idx` into the `n_blk` contiguous blocks of :func:`block_boundaries`.
    3. A uniform random permutation of the blocks; concatenate.
    4. Reject and redraw if the result is the identity (test C-3) -- the
       realized alignment must never enter the null sample.

    Returns a length-`T` bijection on `{0,...,T-1}` (an index array to be
    used as `w_permuted = w[sigma]`).
    """
    identity = np.arange(T)
    bounds = block_boundaries(T, L)
    n_blk = len(bounds)
    for _ in range(max_redraws):
        s = int(rng.integers(0, T))
        rotated = (identity + s) % T
        block_order = rng.permutation(n_blk)
        sigma = np.concatenate([rotated[a:b] for a, b in (bounds[i] for i in block_order)])
        if not np.array_equal(sigma, identity):
            return sigma
    raise RuntimeError(
        "circular_block_permutation_index: identity redrawn "
        f"{max_redraws} times in a row -- something is wrong upstream "
        "(T or L is degenerate)."
    )


def joint_permutation_indices(
    T: int, L: int, rng: np.random.Generator
) -> tuple[np.ndarray, np.ndarray]:
    """VALIDATION-SPEC-005 sec2.2 step 4: "applied IDENTICALLY to the BTC
    and ETH columns (one common permutation, sec2.5)" -- test C-1's own
    guard. Returns `(sigma, sigma)`, the SAME index array twice: the two
    assets of one resample are never permuted independently. A caller
    indexes `w_btc[sigma_btc]` / `w_eth[sigma_eth]`, so an independent-
    permutation bug (each asset drawing its own `sigma`) is a small,
    isolated, monkeypatchable change to THIS one function rather than a
    change scattered across every call site.
    """
    sigma = circular_block_permutation_index(T, L, rng)
    return sigma, sigma


def stationary_block_bootstrap_index(
    T: int, L: int, rng: np.random.Generator
) -> np.ndarray:
    """One resample of VALIDATION-SPEC-005 sec2.2's SECONDARY construction
    (disclosure only): a stationary/circular block bootstrap WITH
    replacement, fixed block length `L`, matching the shape
    `castellan.carry.tail_bootstrap_carry` already uses in this harness
    (`carry.py:126-171`) -- draw a random start, take `min(L, remaining)`
    bars circularly, repeat until `T` bars are filled.

    Does NOT preserve the exact multiset (this is exactly why it is
    secondary/disclosure: VALIDATION-SPEC-005 sec2.1 reason 3 -- the
    ordinary with-replacement block bootstrap perturbs the mean).
    Returns a length-`T` index array (may repeat indices).
    """
    idx = np.empty(T, dtype=int)
    filled = 0
    while filled < T:
        start = int(rng.integers(0, T))
        take = min(L, T - filled)
        idx[filled:filled + take] = (start + np.arange(take)) % T
        filled += take
    return idx


def greedy_feasibility_assignment(
    ranking_series: np.ndarray, w_multiset: np.ndarray, maximize: bool
) -> np.ndarray:
    """The LITERAL VALIDATION-SPEC-005 sec4.6 construction for `I_max`
    (`maximize=True`) / `I_min` (`maximize=False`): "assign the realized
    multiset of `w` values to bars greedily: smallest `w` on the
    most-negative bars, largest on the least" (for `I_max`; mirrored for
    `I_min`).

    **This construction is DEMONSTRATED DEFECTIVE (I-386, HIGH, filed at
    DATA-IMPL-014/S4-D-031): measured `I_max < I_0` on the realized data
    (internally inconsistent -- a bound cannot fall below a value in its
    own claimed class) and confirmed by exhaustive T=10 brute force
    (3,628,800 permutations) that this greedy-by-`ranking_series` rule does
    not find the true combinatorial optimum in either direction.** Kept
    here, unedited, because VALIDATION-SPEC-005 test D-4 requires it be
    COMPUTED and REPORTED, and because "DO NOT repair I-386" is a hard
    stop of this dispatch (I-386 is Validation's spec defect, not this
    seat's to fix) -- every caller of this function must report its output
    labelled `[inferred -- defective, see I-386]`, never as a certified
    bound.

    `ranking_series` : the realized `R_bench` (or any series) whose
    ascending rank orders which bars get which `w`. `w_multiset` : the
    realized `w` values for ONE asset, in any order (its multiset is what
    is preserved). `maximize=True`: smallest `w` on the most-negative
    `ranking_series` bars (the greedy meant to maximize the tail
    improvement). `maximize=False`: mirrored (largest `w` on the
    most-negative bars).

    Returns a length-`T` array of `w` values, one per bar, in
    `ranking_series`'s own bar order (ready to feed the position builder).
    """
    rank_order = np.argsort(ranking_series, kind="stable")  # ascending: most negative first
    w_sorted = np.sort(w_multiset)  # ascending
    if not maximize:
        w_sorted = w_sorted[::-1]
    out = np.empty_like(w_sorted)
    out[rank_order] = w_sorted
    return out


def spawn_children(master_seed: int, n: int = 8) -> list:
    """VALIDATION-SPEC-005 sec2.5: `numpy.random.SeedSequence(master_seed)
    .spawn(n)` -- `n` INDEPENDENT child seed sequences, one per
    `(construction, L)` cell, so no cell's null draws from another cell's
    stream (test C-6). A thin wrapper only so the driver can monkeypatch a
    defective variant (e.g. `[ss.spawn(1)[0]] * n`, the "reuse index 0 for
    every cell" bug) without touching `numpy` itself.
    """
    ss = np.random.SeedSequence(master_seed)
    return ss.spawn(n)


def disclosure_grid_cells(Ls: tuple[int, ...], constructions: tuple[str, ...]) -> list[tuple]:
    """VALIDATION-SPEC-005 sec4.7 row 6 / test E-5: the 8-cell
    `(construction, L)` disclosure grid, as an explicit list rather than
    an inline loop -- so "only 1 of 8 cells computed" (an off-by-scope bug
    in the driving loop) is a testable property of THIS function rather
    than of an un-inspectable `for` loop body."""
    return [(c, L) for c in constructions for L in Ls]


def joint_survival_rate(leg1_fires: np.ndarray, leg2_spares: np.ndarray) -> dict:
    """VALIDATION-SPEC-005 sec4.5 / test E-3: `alpha_1`, `alpha_2`,
    `alpha_joint` (an AND over the PAIRED boolean arrays -- never a
    multiplication of the two marginals), the product, and the
    independence gap. `leg1_fires`/`leg2_spares` : boolean arrays, one
    element per surrogate resample, ALREADY PAIRED (same resample index).
    """
    leg1_fires = np.asarray(leg1_fires, dtype=bool)
    leg2_spares = np.asarray(leg2_spares, dtype=bool)
    if leg1_fires.shape != leg2_spares.shape:
        raise ValueError("leg1_fires and leg2_spares must be paired (same shape)")
    alpha_1 = float(leg1_fires.mean())
    alpha_2 = float(leg2_spares.mean())
    alpha_joint = float((leg1_fires & leg2_spares).mean())  # AND, not multiplication
    product = alpha_1 * alpha_2
    return {
        "alpha_1": alpha_1,
        "alpha_2": alpha_2,
        "alpha_joint": alpha_joint,
        "product": product,
        "independence_gap": alpha_joint - product,
    }


def compute_i0(M_b: float, M_s_constant_wbar: float) -> float:
    """VALIDATION-SPEC-005 sec4.6 `I_0`: the improvement statistic
    evaluated at the CONSTANT schedule `w* == w_bar` (both assets, every
    bar) -- `M_s_constant_wbar` must be computed from an off-engine
    reconstruction AT THAT CONSTANT SCHEDULE (never from `R_bench_scaled`
    itself, which would trivially give `I_0 approx 0` by construction --
    the exact defect test D-3 exists to catch, DATA-IMPL-014's own
    framing). A thin wrapper so that defect is a patchable, testable
    function rather than inline arithmetic only.
    """
    return (M_s_constant_wbar - M_b) / abs(M_b)


def clopper_pearson_interval(successes: int, n: int, alpha: float = 0.05):
    """Exact Clopper-Pearson 95% CI for a binomial proportion (VALIDATION-
    SPEC-005 sec2.4: "Report Clopper-Pearson exact 95% intervals, not
    normal-approximation intervals, because the interesting region includes
    small alpha where the normal approximation misbehaves"). Uses the
    Beta-distribution quantile identity so no external CI-specific
    dependency is needed beyond `scipy.stats.beta`, already a transitive
    dependency of this package via `scipy.stats.norm`/`skew`/`kurtosis` in
    `castellan.stats`.
    """
    from scipy.stats import beta

    if n == 0:
        return (float("nan"), float("nan"))
    lo = 0.0 if successes == 0 else beta.ppf(alpha / 2, successes, n - successes + 1)
    hi = 1.0 if successes == n else beta.ppf(1 - alpha / 2, successes + 1, n - successes)
    return (float(lo), float(hi))
