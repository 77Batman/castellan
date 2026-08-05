"""Validation statistics for Castellan Capital.

Implements the Part IV machinery: Sharpe/t-stat, expected maximum Sharpe
under multiple testing (Bailey, Borwein, Lopez de Prado & Zhu 2014),
Deflated Sharpe Ratio (Bailey & Lopez de Prado 2014), minimum backtest
length, Probability of Backtest Overfitting via CSCV (Bailey et al.),
and Walk-Forward Efficiency.

Conventions
-----------
- "per-period" Sharpe = mean(r) / std(r, ddof=1) on the native bar frequency.
- "annualized" Sharpe = per-period * sqrt(periods_per_year).
- The cross-sectional trial Sharpe dispersion sigma_sr fed to DSR must be
  in the SAME units as the candidate Sharpe (this library uses per-period
  units internally and converts explicitly).
"""

from __future__ import annotations

import itertools
import math
from dataclasses import dataclass

import numpy as np
from scipy.stats import norm, skew, kurtosis

EULER_MASCHERONI = 0.5772156649015329


# ----------------------------------------------------------------------
# Basic performance measures
# ----------------------------------------------------------------------

def sharpe_period(returns: np.ndarray) -> float:
    """Per-period Sharpe ratio (not annualized)."""
    r = np.asarray(returns, dtype=float)
    r = r[~np.isnan(r)]
    if r.size < 2:
        return float("nan")
    sd = r.std(ddof=1)
    if sd == 0:
        return float("nan")
    return float(r.mean() / sd)


def sharpe_annual(returns: np.ndarray, periods_per_year: int = 252) -> float:
    """Annualized Sharpe ratio."""
    return sharpe_period(returns) * math.sqrt(periods_per_year)


def sr_tstat(returns: np.ndarray) -> float:
    """t-statistic of the mean return: SR_period * sqrt(T).

    UNCORRECTED. Assumes serial independence — see VALIDATION-SPEC-001
    (I-050). This function is not edited by that spec (clause E-1) and is
    preserved exactly so every existing call site keeps its meaning. The
    graded Gate 1 t-statistic is ``sr_tstat_corrected(...).t_gate``.
    """
    r = np.asarray(returns, dtype=float)
    r = r[~np.isnan(r)]
    if r.size < 2:
        return float("nan")
    return sharpe_period(r) * math.sqrt(r.size)


# ----------------------------------------------------------------------
# Newey-West / HAC-corrected t-statistic (VALIDATION-SPEC-001, I-050)
# ----------------------------------------------------------------------

def sr_tstat_nw(returns: np.ndarray, lag: int) -> float:
    """Newey-West HAC t-statistic of the mean, Bartlett kernel, at a
    caller-supplied lag ``L`` (VALIDATION-SPEC-001 E-2).

    ``gamma_hat(l) = sum_{i=l}^{T-1} d_i*d_{i-l} / (T-1)`` for every lag,
    including l=0 -- the (T-1) divisor at l=0 is what makes ``lag=0``
    reduce EXACTLY to ``sr_tstat`` (E-2(a)); a (T) divisor would leave a
    permanent, unexplained wedge between the two reported figures.

    ``sigma_hat_NW^2(L) = gamma_hat(0) + 2 * sum_{l=1}^{L} (1 - l/(L+1)) *
    gamma_hat(l)``. Returns ``r_bar / sqrt(sigma_hat_NW^2(L) / T)``, or
    ``nan`` if the long-run variance estimate is <= 0 (reachable only as
    an exact zero, on a constant series -- E-7).

    ``lag`` must be an integer >= 0; ``lag >= T - 1`` is a ``ValueError``.
    """
    r = np.asarray(returns, dtype=float)
    r = r[~np.isnan(r)]
    T = r.size
    L = int(lag)
    if L < 0:
        raise ValueError(f"lag must be >= 0, got {L}")
    if T >= 2 and L >= T - 1:
        raise ValueError(f"lag ({L}) must be < T-1 ({T - 1})")
    if T < 2:
        return float("nan")
    if np.all(r == r[0]):
        # Exactly constant series (E-7): true variance is exactly zero.
        # Detected on bit-identity of the inputs rather than on the
        # floating-point subtraction `r - r.mean()`, whose rounding error
        # (mean() is not bit-exact for a repeated-float sum) would
        # otherwise produce a tiny nonzero variance and mask the
        # degenerate case behind an enormous but finite t-statistic.
        return float("nan")
    d = r - r.mean()

    def gamma(l: int) -> float:
        if l == 0:
            return float(d @ d) / (T - 1)
        return float(d[l:] @ d[: T - l]) / (T - 1)

    s = gamma(0)
    for l in range(1, L + 1):
        s += 2.0 * (1.0 - l / (L + 1.0)) * gamma(l)
    if s <= 0:
        return float("nan")
    return float(r.mean() / math.sqrt(s / T))


def hac_lag_andrews(returns: np.ndarray) -> tuple[int, float]:
    """Andrews (1991) AR(1) plug-in lag truncation for a Bartlett kernel
    (VALIDATION-SPEC-001 E-3), mechanical, no discretion.

    Returns ``(lag, rho_hat)`` where ``rho_hat`` is the UNCLIPPED lag-1
    autocorrelation of the demeaned series (E-9 keys on it) and ``lag``
    is ``floor(1.1447 * (alpha(1) * T) ** (1/3))``, computed from the
    ``[-0.97, 0.97]``-clipped coefficient (for lag selection only), and
    then bounded to the valid domain ``[0, min(T//4, T-2)]`` so it is
    always a usable argument to :func:`sr_tstat_nw`.
    """
    r = np.asarray(returns, dtype=float)
    r = r[~np.isnan(r)]
    T = r.size
    d = r - r.mean()
    denom = float(d[:-1] @ d[:-1]) if T >= 2 else 0.0
    rho_hat = float(d[1:] @ d[:-1]) / denom if denom != 0 else 0.0
    rho_clipped = min(max(rho_hat, -0.97), 0.97)
    alpha1 = (
        4.0 * rho_clipped ** 2
        / ((1.0 - rho_clipped) ** 2 * (1.0 + rho_clipped) ** 2)
    )
    lag = int(math.floor(1.1447 * (alpha1 * T) ** (1.0 / 3.0)))
    lag = min(max(lag, 0), min(T // 4, T - 2)) if T >= 2 else 0
    return lag, rho_hat


@dataclass(frozen=True)
class HACTStat:
    """Every figure a caller needs from the corrected estimator
    (VALIDATION-SPEC-001 E-4)."""

    t_raw: float       # sr_tstat(r) -- uncorrected, never graded
    t_nw: float        # sr_tstat_nw(r, lag) -- honest HAC, may exceed t_raw
    t_gate: float      # min(t_nw, t_raw) -- the ONLY figure graded (E-8)
    lag: int
    lag_rule: str      # e.g. "andrews" | "label_span" | "stated" | "...(capped)"
    rho_hat: float     # unclipped lag-1 autocorrelation
    inflation: float   # t_raw / t_nw; nan if t_nw is 0 or nan
    eligible: bool     # False => the criterion is INSUFFICIENT-DATA
    note: str          # why, when eligible is False; "" otherwise


def sr_tstat_corrected(
    returns: np.ndarray, *, label_span: int = 1, stated_lag: int | None = None
) -> HACTStat:
    """The full I-050 correction (VALIDATION-SPEC-001 E-5 to E-9).

    The lag actually used is::

        L_pre = max(hac_lag_andrews(r).lag, label_span - 1, stated_lag or 0)
        L_cap = min(floor(T/4), T - 2)
        L     = min(L_pre, L_cap)

    one-sided by construction: a caller may raise the lag and can never
    lower it (E-5). ``eligible`` is False (INSUFFICIENT-DATA, never PASS)
    on small samples (E-6: T < 32 or T < 10*(L+1)), a degenerate/zero
    long-run variance (E-7), or near-unit-root autocorrelation
    (E-9: |rho_hat| >= 0.97). ``t_gate = min(t_nw, t_raw)`` unconditionally
    (E-8) -- the firm never gets credit for measured negative
    autocorrelation; that would be an estimator change that loosens.
    """
    r = np.asarray(returns, dtype=float)
    r = r[~np.isnan(r)]
    T = r.size
    t_raw = sr_tstat(r)

    if T < 2:
        return HACTStat(
            t_raw=t_raw, t_nw=float("nan"), t_gate=float("nan"),
            lag=0, lag_rule="andrews", rho_hat=float("nan"),
            inflation=float("nan"), eligible=False,
            note=f"T={T} < 2 observations; matches sr_tstat's existing "
                 "contract (E-7).",
        )

    andrews_lag, rho_hat = hac_lag_andrews(r)
    label_term = label_span - 1
    stated_term = stated_lag if stated_lag is not None else 0
    L_pre = max(andrews_lag, label_term, stated_term)

    if stated_lag is not None and stated_term > andrews_lag and stated_term >= label_term:
        rule = "stated"
    elif label_term > andrews_lag:
        rule = "label_span"
    else:
        rule = "andrews"

    L_cap = min(T // 4, T - 2)
    L = min(L_pre, L_cap)
    if L_pre > L_cap:
        rule += "(capped)"

    t_nw = sr_tstat_nw(r, L)
    if math.isnan(t_nw) or t_nw == 0:
        inflation = float("nan")
    else:
        inflation = t_raw / t_nw

    if math.isnan(t_nw) or math.isnan(t_raw):
        t_gate = float("nan")
    else:
        t_gate = min(t_nw, t_raw)

    notes: list[str] = []
    eligible = True
    if T < 32 or T < 10 * (L + 1):
        eligible = False
        notes.append(
            f"small sample: T={T}, L={L} (need T>=32 and T>=10*(L+1)="
            f"{10 * (L + 1)}) — E-6"
        )
    if abs(rho_hat) >= 0.97:
        eligible = False
        notes.append(
            f"near-unit-root: |rho_hat|={abs(rho_hat):.3f} >= 0.97 — E-9, "
            "escalated to Validation"
        )
    if math.isnan(t_nw):
        eligible = False
        notes.append(
            "degenerate long-run variance: sigma_NW^2 <= 0 (constant "
            "series) — E-7"
        )

    return HACTStat(
        t_raw=t_raw, t_nw=t_nw, t_gate=t_gate, lag=L, lag_rule=rule,
        rho_hat=rho_hat, inflation=inflation, eligible=eligible,
        note="; ".join(notes),
    )


# ----------------------------------------------------------------------
# Multiple testing: expected max Sharpe, DSR, MinBTL
# ----------------------------------------------------------------------

def expected_max_sharpe(n_trials: int, sr_std: float = 1.0) -> float:
    """E[max SR] across n_trials of zero-edge strategies (BLP&Z 2014).

    E[max] ~= sr_std * [ (1-g)*Z(1 - 1/N) + g*Z(1 - 1/(N*e)) ],
    g = Euler-Mascheroni. `sr_std` is the cross-sectional std of trial
    Sharpes, in whatever units the caller works in.
    """
    n = int(n_trials)
    if n < 1:
        raise ValueError("n_trials must be >= 1")
    if n == 1:
        return 0.0
    g = EULER_MASCHERONI
    z1 = norm.ppf(1.0 - 1.0 / n)
    z2 = norm.ppf(1.0 - 1.0 / (n * math.e))
    return float(sr_std * ((1.0 - g) * z1 + g * z2))


def deflated_sharpe_ratio(
    returns: np.ndarray,
    n_trials: int,
    trial_sr_std_period: float,
) -> float:
    """Deflated Sharpe Ratio (Bailey & Lopez de Prado, 2014).

    Probability that the true Sharpe exceeds the expected maximum Sharpe
    obtainable from `n_trials` zero-edge trials, given non-normality.

    Parameters
    ----------
    returns : candidate strategy's per-bar returns.
    n_trials : total logged trials in the hypothesis family (registry N).
    trial_sr_std_period : cross-sectional std of PER-PERIOD trial Sharpes
        from the registry. Passing annualized dispersion here inflates the
        benchmark and is a defect.
    """
    r = np.asarray(returns, dtype=float)
    r = r[~np.isnan(r)]
    T = r.size
    if T < 10:
        return float("nan")
    sr = sharpe_period(r)
    g3 = float(skew(r))
    g4 = float(kurtosis(r, fisher=False))  # raw kurtosis; normal => 3
    sr0 = expected_max_sharpe(n_trials, trial_sr_std_period)
    denom = 1.0 - g3 * sr + ((g4 - 1.0) / 4.0) * sr**2
    if denom <= 0:
        return float("nan")
    z = (sr - sr0) * math.sqrt(T - 1) / math.sqrt(denom)
    return float(norm.cdf(z))


def min_backtest_length_years(
    n_trials: int, target_annual_sr: float, periods_per_year: int = 252
) -> float:
    """Minimum backtest length (years) so that a target annualized Sharpe
    is not explainable as the expected max of N zero-edge trials
    (BLP&Z 2014, MinBTL).

    MinBTL ~= ( E[max Z_N] / SR_target_period )^2 periods.
    """
    if target_annual_sr <= 0:
        return float("inf")
    emax = expected_max_sharpe(n_trials, 1.0)  # units of per-trial SR std
    sr_p = target_annual_sr / math.sqrt(periods_per_year)
    periods = (emax / sr_p) ** 2
    return float(periods / periods_per_year)


# ----------------------------------------------------------------------
# Probability of Backtest Overfitting via CSCV
# ----------------------------------------------------------------------

@dataclass
class PBOResult:
    pbo: float
    n_combinations: int
    n_trials: int
    n_partitions: int
    logits: np.ndarray


def probability_backtest_overfitting(
    trial_returns: np.ndarray,
    n_partitions: int = 16,
    max_combinations: int | None = 3000,
    seed: int = 7,
) -> PBOResult:
    """PBO via Combinatorially Symmetric Cross-Validation.

    Parameters
    ----------
    trial_returns : (T, N) matrix — per-bar returns of every logged trial
        in the family, aligned on the same T bars. This is why the registry
        stores full return series, not just headline Sharpes.
    n_partitions : S, the number of contiguous blocks (Charter: 16).
    max_combinations : cap on the C(S, S/2) combinations evaluated
        (sampled without replacement if exceeded); None = all.

    Returns PBO = fraction of splits where the in-sample-best trial ranks
    in the bottom half out of sample. Noise ~= 0.5; a robust genuine edge
    pushes it toward 0.
    """
    M = np.asarray(trial_returns, dtype=float)
    if M.ndim != 2:
        raise ValueError("trial_returns must be (T, N)")
    T, N = M.shape
    if N < 2:
        raise ValueError("CSCV needs at least 2 trials")
    S = int(n_partitions)
    if S % 2 != 0:
        raise ValueError("n_partitions must be even")
    if T < S * 2:
        raise ValueError(f"Need at least {S * 2} bars for S={S} partitions")

    blocks = np.array_split(np.arange(T), S)
    combos = list(itertools.combinations(range(S), S // 2))
    if max_combinations is not None and len(combos) > max_combinations:
        rng = np.random.default_rng(seed)
        idx = rng.choice(len(combos), size=max_combinations, replace=False)
        combos = [combos[i] for i in idx]

    def _sr_cols(rows: np.ndarray) -> np.ndarray:
        sub = M[rows]
        mu = sub.mean(axis=0)
        sd = sub.std(axis=0, ddof=1)
        with np.errstate(divide="ignore", invalid="ignore"):
            return np.where(sd > 0, mu / sd, -np.inf)

    logits = []
    for combo in combos:
        is_rows = np.concatenate([blocks[i] for i in combo])
        oos_rows = np.concatenate(
            [blocks[i] for i in range(S) if i not in combo]
        )
        sr_is = _sr_cols(is_rows)
        sr_oos = _sr_cols(oos_rows)
        best = int(np.argmax(sr_is))
        # relative OOS rank of the IS winner, in (0, 1)
        rank = (np.sum(sr_oos <= sr_oos[best])) / (N + 1.0)
        rank = min(max(rank, 1e-9), 1 - 1e-9)
        logits.append(math.log(rank / (1.0 - rank)))

    logits = np.array(logits)
    pbo = float(np.mean(logits <= 0))
    return PBOResult(
        pbo=pbo,
        n_combinations=len(combos),
        n_trials=N,
        n_partitions=S,
        logits=logits,
    )


# ----------------------------------------------------------------------
# Walk-forward efficiency
# ----------------------------------------------------------------------

def walk_forward_efficiency(
    sr_pairs: list[tuple[float, float]]
) -> float:
    """WFE = mean(SR_oos) / mean(SR_is) across walk-forward windows.

    `sr_pairs` is a list of (sr_is, sr_oos) in consistent units. The
    Charter requires >= 10 windows and WFE >= 0.50.
    """
    if not sr_pairs:
        return float("nan")
    sr_is = np.array([p[0] for p in sr_pairs], dtype=float)
    sr_oos = np.array([p[1] for p in sr_pairs], dtype=float)
    m_is = np.nanmean(sr_is)
    if not np.isfinite(m_is) or m_is <= 0:
        return float("nan")
    return float(np.nanmean(sr_oos) / m_is)


# ----------------------------------------------------------------------
# Concentration and subperiod diagnostics
# ----------------------------------------------------------------------

def pnl_concentration(returns: np.ndarray, bars_per_month: int = 21) -> dict:
    """Max single-bar and single-month share of total P&L.

    Shares are computed against total absolute P&L when total P&L is near
    zero-safe; Charter limits: day <= 10%, month <= 25% of total.
    """
    r = np.asarray(returns, dtype=float)
    r = r[~np.isnan(r)]
    total = r.sum()
    if abs(total) < 1e-12:
        return {"max_day_share": float("inf"), "max_month_share": float("inf")}
    day_share = float(np.max(r) / total) if total > 0 else float("inf")
    n_months = max(1, r.size // bars_per_month)
    month_pnl = [
        r[i * bars_per_month : (i + 1) * bars_per_month].sum()
        for i in range(n_months)
    ]
    month_share = float(np.max(month_pnl) / total) if total > 0 else float("inf")
    return {"max_day_share": day_share, "max_month_share": month_share}


def subperiod_positivity(returns: np.ndarray, n_blocks: int = 8) -> float:
    """Fraction of independent contiguous blocks with positive net P&L."""
    r = np.asarray(returns, dtype=float)
    r = r[~np.isnan(r)]
    blocks = np.array_split(r, n_blocks)
    pos = sum(1 for b in blocks if b.sum() > 0)
    return pos / n_blocks
