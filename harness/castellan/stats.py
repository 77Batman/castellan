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

    This is the number held against the firm's T_STAT_HURDLE = 3.0.
    """
    r = np.asarray(returns, dtype=float)
    r = r[~np.isnan(r)]
    if r.size < 2:
        return float("nan")
    return sharpe_period(r) * math.sqrt(r.size)


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
