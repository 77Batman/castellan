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
# OLS regression with Newey-West / HAC standard errors (I-380, PREREG-002
# §5.2 leg (i))
# ----------------------------------------------------------------------

@dataclass(frozen=True)
class OLSHACAlpha:
    """Every figure a caller needs from :func:`ols_alpha_tstat_hac`."""

    alpha: float          # OLS intercept
    beta: float           # OLS slope on x
    se_alpha: float       # HAC (Newey-West) standard error of alpha
    se_beta: float        # HAC (Newey-West) standard error of beta
    t_alpha: float        # alpha / se_alpha -- the PREREG-002 sec5.2(i) figure
    t_beta: float
    n: int                # observations used (after joint NaN-drop)
    lag: int              # Bartlett truncation, AS SUPPLIED -- not selected
    use_correction: bool  # small-sample correction convention, see docstring


def ols_alpha_tstat_hac(
    y: np.ndarray,
    x: np.ndarray,
    lag: int,
    *,
    use_correction: bool = False,
) -> OLSHACAlpha:
    """OLS ``y = alpha + beta*x + eps`` with a Newey-West/HAC (Bartlett
    kernel) covariance matrix on the coefficients, at a caller-supplied
    lag truncation ``lag`` (I-380, PREREG-002 sec5.2 leg (i): "In the OLS
    regression R_strat = alpha + beta*R_bench + eps over the full
    in-sample, the Newey-West t-statistic on alpha, at a 21-bar lag
    truncation, is <= 3.0"). The lag is NOT selected here -- PREREG-002
    pre-commits it at 21 bars and this function does not choose,
    default, or auto-select a truncation; unlike :func:`sr_tstat_corrected`
    there is no Andrews rule or one-sided floor in this path, because the
    sealed document specifies the number directly.

    Convention resolved on the face of this function (Principal ruling,
    2026-09-16): acceptance is computed against ``statsmodels`` --
    ``sm.OLS(y, sm.add_constant(x)).fit(cov_type="HAC",
    cov_kwds={"maxlags": lag})`` -- to 1e-8. Reading ``statsmodels``'
    own ``RegressionResults.get_robustcov_results`` source (version
    0.15.0) shows that for ``cov_type="HAC"`` reached this way,
    ``use_correction`` defaults to ``False`` when the caller's
    ``cov_kwds`` does not set it -- i.e. NO small-sample correction is
    applied by the oracle call the dispatch specifies. This function's
    own default, ``use_correction=False``, is chosen to MATCH that
    default exactly rather than to state an independent preference; a
    caller who needs the corrected convention (``cov_kwds={"maxlags":
    L, "use_correction": True}`` on the oracle side) passes
    ``use_correction=True`` here and gets bit-identical agreement to
    that oracle call instead (see the test suite's "AR1-with-correction"
    case). The Bartlett kernel weights (``1 - l/(lag+1)`` for
    ``l=0..lag``) and the HAC sandwich construction (``S = sum_l
    weight[l] * (x_l'x_l + x_l'x_l')`` on the per-observation score
    ``x_i * resid_i``, sandwiched as ``(X'X)^+ S (X'X)^{+T}`` using the
    Moore-Penrose pseudoinverse of ``X`` for both the coefficients and
    the bread of the sandwich) are read directly from
    ``statsmodels.stats.sandwich_covariance.{cov_hac_simple,
    S_hac_simple, weights_bartlett}`` and from ``RegressionResults``'
    own ``pinv``-based fit, not reimplemented from a textbook formula
    independently -- this is why agreement below is exact to double
    precision on every case tested, not merely within 1e-8.

    **Disclosure, not amendable under P7 (Gate 1's Charter 5.4 factor
    attribution must decompose this before any PROCEED):** this
    regression, run on ``R_bench`` alone, cannot separate conditioning
    alpha from spot-directional return earned while un-hedged. The
    sealed position (PREREG-002 statement) is "long 1.0 unit spot
    notional, short w(t) units perp notional" -- when ``w(t) < 1`` the
    position carries NET LONG SPOT exposure, not a smaller delta-neutral
    one. A candidate ``R_strat`` built on that construction can clear
    this test on spot beta (a rising BTC/ETH spot price during the
    sample, correlated with the bars the conditioning happens to
    de-scale on) with no conditioning alpha whatsoever. This function
    reports exactly the statistic PREREG-002 sec5.2(i) specifies and
    nothing more; it does not and cannot detect this confound, which is
    Gate 1 factor attribution's job, not this estimator's.

    Parameters
    ----------
    y, x : equal-length 1-D arrays (``R_strat``, ``R_bench``). Paired
        ``NaN``s are dropped jointly (a ``NaN`` in either series drops
        that bar from both) before any arithmetic, so the two series
        stay aligned bar-for-bar.
    lag : int >= 0, the Bartlett truncation. Raises ``ValueError`` if
        negative or if ``lag >= n - 2`` (need at least one residual
        degree of freedom beyond the 2 estimated parameters).
    use_correction : see above.

    Raises
    ------
    ValueError
        if ``y`` and ``x`` are not the same length, if fewer than 3
        paired observations remain after dropping ``NaN``s, or if
        ``lag`` is out of range.
    """
    y = np.asarray(y, dtype=float)
    x = np.asarray(x, dtype=float)
    if y.shape != x.shape:
        raise ValueError(
            f"y and x must have the same shape, got {y.shape} vs {x.shape}"
        )
    mask = ~(np.isnan(y) | np.isnan(x))
    y = y[mask]
    x = x[mask]
    T = y.size
    L = int(lag)
    if L < 0:
        raise ValueError(f"lag must be >= 0, got {L}")
    if T < 3:
        raise ValueError(f"need at least 3 paired observations, got {T}")
    if L >= T - 2:
        raise ValueError(
            f"lag ({L}) must be < n-2 ({T - 2}) -- at least one residual "
            "degree of freedom beyond the 2 estimated parameters"
        )

    X = np.column_stack([np.ones(T), x])
    # Moore-Penrose pseudoinverse, matching statsmodels' default
    # OLS.fit(method="pinv"): beta = pinv(X) @ y, and
    # normalized_cov_params = pinv(X) @ pinv(X).T -- using the SAME
    # pinv_X for both is what makes this bit-identical to the oracle
    # rather than merely close, on well-conditioned designs.
    pinv_X = np.linalg.pinv(X)
    beta_hat = pinv_X @ y
    resid = y - X @ beta_hat
    xtx_inv = pinv_X @ pinv_X.T

    xu = X * resid[:, None]  # (T, 2) per-observation score x_i * u_i
    weights = 1.0 - np.arange(L + 1) / (L + 1.0)  # Bartlett kernel
    S = weights[0] * (xu.T @ xu)
    for l in range(1, L + 1):
        s = xu[l:].T @ xu[: T - l]
        S = S + weights[l] * (s + s.T)

    cov = xtx_inv @ S @ xtx_inv.T
    if use_correction:
        k_params = 2
        cov = cov * (T / float(T - k_params))

    se = np.sqrt(np.diag(cov))
    alpha, beta = float(beta_hat[0]), float(beta_hat[1])
    se_alpha, se_beta = float(se[0]), float(se[1])
    t_alpha = alpha / se_alpha if se_alpha > 0 else float("nan")
    t_beta = beta / se_beta if se_beta > 0 else float("nan")

    return OLSHACAlpha(
        alpha=alpha, beta=beta, se_alpha=se_alpha, se_beta=se_beta,
        t_alpha=t_alpha, t_beta=t_beta, n=T, lag=L,
        use_correction=use_correction,
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


def _dsr_z(
    returns: np.ndarray,
    n_trials: int,
    trial_sr_std_period: float,
) -> float:
    """The published DSR's z arithmetic (Bailey & Lopez de Prado, 2014),
    extracted verbatim from :func:`deflated_sharpe_ratio` (VALIDATION-SPEC-002
    D-1). This is a refactor, not a mutation -- ``test_dsr_02`` pins
    ``deflated_sharpe_ratio``'s output as bitwise identical to before the
    extraction. Consumed by :func:`deflated_sharpe_ratio_serial` (D-2),
    which needs the SAME z -- reimplementing the `denom` arithmetic a
    second time, or recovering z via ``norm.ppf(DSR)``, are both defective
    (D-3): the former creates a second place for the arithmetic to drift,
    the latter loses the correction entirely in the saturated right tail.
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
    return (sr - sr0) * math.sqrt(T - 1) / math.sqrt(denom)


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

    UNCORRECTED -- assumes serial independence (I-057). This function is
    not edited by VALIDATION-SPEC-002 (clause D-1, same standing as M-1)
    and is preserved exactly so every existing call site keeps its
    meaning. The graded Gate 1 DSR is
    ``deflated_sharpe_ratio_serial(...)``.
    """
    z = _dsr_z(returns, n_trials, trial_sr_std_period)
    if math.isnan(z):
        return float("nan")
    return float(norm.cdf(z))


def deflated_sharpe_ratio_serial(
    returns: np.ndarray,
    n_trials: int,
    trial_sr_std_period: float,
    *,
    vif: float,
) -> float:
    """VALIDATION-SPEC-002 D-2 -- the serial-corrected DSR, as amended by
    VALIDATION-RULING-005-A.

    ``z_serial = z_iid / sqrt(max(vif, 1.0))`` -- an effective-sample-size
    substitution on the ``sqrt(T-1)`` factor, leaving the published
    non-normality ``denom`` byte-for-byte untouched (D-4/D-5). The divisor
    clamp is the direct analogue of M-2's ``max(mb_iid, mb_iid*vif)``: D-2's
    literal (unclamped) form violates C-1(iv) (``DSR_serial`` must be
    non-increasing in ``vif``) on the ``vif < 1``, ``z < 0`` branch -- an
    estimator-unreachable input (R-2/R-7 floor ``vif_gate`` at 1.0), but one
    the consumer-layer guarantee must not depend on being unable to
    receive (C-2). RULING 005-A: the two constructions are bit-identical
    for every ``vif >= 1``, so this changes no live Gate number, ever.
    ``DSR = min(Phi(z_serial), Phi(z_iid))`` -- D-6's non-permissive
    floor, taken unconditionally (no sign condition on z), and is
    UNCHANGED and NOT removable: C-2 requires both enforcements
    independently, same as the divisor clamp does not make the outer
    ``min`` redundant.

    ``vif`` is a required keyword-only float; no default -- a default of
    1.0 would let a caller obtain the uncorrected figure from the
    corrected function by omission (same shape as M-2). Non-finite or
    ``vif <= 0`` raises ``ValueError``, unchanged; there is no path on
    which an unmeasurable VIF silently behaves as 1.0 (D-3a) -- the clamp
    is not a licence to accept a garbage VIF, only a guarantee about what
    happens once a valid one arrives.
    """
    if not math.isfinite(vif) or vif <= 0:
        raise ValueError(f"vif must be finite and > 0, got {vif!r}")
    z_iid = _dsr_z(returns, n_trials, trial_sr_std_period)
    if math.isnan(z_iid):
        return float("nan")
    z_serial = z_iid / math.sqrt(max(vif, 1.0))   # VALIDATION-RULING-005-A (D-2 as amended):
                                                   # the divisor clamp is the direct analogue of
                                                   # M-2's max(vif, 1.0); C-1(iv) fails without it
                                                   # at vif < 1, z < 0. The outer min (D-6) stays.
    dsr_iid = float(norm.cdf(z_iid))
    dsr_serial = float(norm.cdf(z_serial))
    return float(min(dsr_serial, dsr_iid))


def effective_sample_size(T: int, vif: float) -> float:
    """VALIDATION-SPEC-002 D-9 -- ``T_eff = (T-1)/vif + 1``, chosen so
    ``sqrt(T_eff - 1) == sqrt(T-1)/sqrt(vif)`` EXACTLY -- the reported
    effective sample size is the one the DSR arithmetic actually used.
    Reported only; never fed back into any other statistic."""
    return (T - 1) / vif + 1.0


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


def min_backtest_length_years_serial(
    n_trials: int,
    target_annual_sr: float,
    periods_per_year: int = 252,
    *,
    vif: float,
) -> float:
    """VALIDATION-SPEC-002 M-2 -- the serially-corrected MinBTL.

    ``MinBTL_serial = max(mb_iid, mb_iid * vif)``. :func:`min_backtest_length_years`
    is NOT edited (M-1) -- this is a new function, not a mutation.

    The outer ``max`` is the first of two independent monotone-
    conservatism enforcements (C-2): it guarantees ``MinBTL_serial >=
    MinBTL_iid`` for EVERY ``vif > 0``, including ``vif < 1`` -- an
    injected value the estimator can never produce (R-2's floor), but
    which the consumer-layer guarantee must not depend on being unable
    to receive. ``mb_iid = inf`` (non-positive Sharpe) propagates
    unchanged.

    ``vif`` is a required keyword-only float; no default -- a default of
    1.0 would let a caller obtain the uncorrected figure from the
    corrected function by omission (the shape W-1 closed for
    ``feature_lookback``). Non-finite or ``vif <= 0`` raises
    ``ValueError``.
    """
    if not math.isfinite(vif) or vif <= 0:
        raise ValueError(f"vif must be finite and > 0, got {vif!r}")
    mb = min_backtest_length_years(n_trials, target_annual_sr, periods_per_year)
    return max(mb, mb * vif)


def max_admissible_trials(
    span_years: float,
    target_annual_sr: float,
    periods_per_year: int = 252,
    *,
    vif: float,
) -> int:
    """VALIDATION-SPEC-002 M-4 -- the largest integer ``N >= 1`` such that
    ``min_backtest_length_years_serial(max(N, 2), target_annual_sr,
    periods_per_year, vif=vif) <= span_years``, found by
    doubling-then-bisection (monotone in N because ``min_backtest_length_years``
    is monotone in N -- Ruling 003/I-037's fixed-lag discipline extended
    here). Returns ``1`` if no ``N >= 2`` satisfies it. Returns the
    doubling cap ``2**31 - 1`` where the constraint never binds; the
    caller renders that as ``"unbounded on this span"`` rather than as an
    integer.

    This is the Principal's sealed ``N_max``, made executable (M-4). A
    pure function of ``(span, SR, ppy, vif)``; consumes no sample.
    """
    if not math.isfinite(vif) or vif <= 0:
        raise ValueError(f"vif must be finite and > 0, got {vif!r}")
    CAP = 2 ** 31 - 1

    def fits(n: int) -> bool:
        return min_backtest_length_years_serial(
            max(n, 2), target_annual_sr, periods_per_year, vif=vif
        ) <= span_years

    if not fits(2):
        return 1
    if fits(CAP):
        return CAP

    lo, hi = 2, 4
    while fits(hi):
        lo = hi
        hi = hi * 2
        if hi >= CAP:
            hi = CAP
            break
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if fits(mid):
            lo = mid
        else:
            hi = mid
    return lo


# ----------------------------------------------------------------------
# Variance inflation factor (VALIDATION-SPEC-002 R-1 .. R-16)
# ----------------------------------------------------------------------

@dataclass(frozen=True)
class VIFResult:
    """VALIDATION-SPEC-002 R-1."""

    vif_gate: float           # max(1.0, vif_hac, vif_ar1) -- the ONLY figure consumed
    vif_hac: float            # sigma^2_NW(L) / gamma0, both at divisor T-1
    vif_ar1: float            # (1 + rho+) / (1 - rho+), rho+ = max(0, rho_hat)
    rho_hat: float            # unclipped lag-1 autocorrelation (SPEC-001 E-3)
    lag: int                  # L, the SPEC-001 E-5 lag
    lag_rule: str
    source: str                # "candidate-only" | "max(candidate, family-median)"
                                # | "unmeasurable"
    n_series_used: int         # trial series entering the family term
    n_series_excluded: int     # excluded by R-9's length floors
    eligible: bool             # False => INSUFFICIENT-DATA (R-11)
    note: str


def variance_inflation(returns: np.ndarray, *, label_span: int = 1) -> VIFResult:
    """VALIDATION-SPEC-002 R-2 -- the single-series VIF estimator, no
    discretion.

    ``vif_hac = sigma_NW^2(L) / gamma0``, computed as ``inflation ** 2``
    (M-3: ``HACTStat.inflation`` is a ratio of STANDARD ERRORS;
    ``VIF`` is a ratio of VARIANCES). ``vif_ar1 = (1 + rho+) / (1 -
    rho+)``, ``rho+ = max(0, rho_hat)`` (R-3: the firm takes no credit
    for negative autocorrelation). ``vif_gate = max(1.0, vif_hac,
    vif_ar1)`` -- floored per series, before any aggregation (R-7).

    The lag ``L`` is SPEC-001 E-5's rule -- Andrews-selected, floored at
    the declared label span, capped, one-sided -- and the eligibility
    guards (``T < 32``; ``T < 10*(L+1)``; degenerate variance;
    ``|rho_hat| >= 0.97``) are SPEC-001's E-6/E-7/E-9, IMPORTED verbatim
    via :func:`sr_tstat_corrected`, not re-derived or re-tuned here (R-5).

    ``gamma0 == 0`` (constant series, R-4): ``vif_hac``, ``vif_ar1``,
    ``vif_gate`` are all ``nan`` and ``eligible = False``. A degenerate
    ``sigma_NW^2(L) <= 0`` with ``gamma0 != 0`` (unreachable under the
    Bartlett kernel except an exact zero) drops the HAC term from the
    ``max`` rather than treating it as zero.
    """
    r = np.asarray(returns, dtype=float)
    r = r[~np.isnan(r)]
    T = r.size

    hac = sr_tstat_corrected(r, label_span=label_span)  # R-5: SPEC-001's guards, verbatim
    rho_hat = hac.rho_hat

    gamma0 = float((r - r.mean()) @ (r - r.mean())) / (T - 1) if T >= 2 else 0.0

    notes = [hac.note] if hac.note else []

    if gamma0 == 0.0:
        vif_hac = float("nan")
        vif_ar1 = float("nan")
        vif_gate = float("nan")
    else:
        if math.isnan(hac.inflation):
            vif_hac = float("nan")
            notes.append(
                "vif_hac omitted: sigma_NW^2(L) <= 0 with gamma0 != 0 "
                "(R-4); dropped from the max, not treated as zero")
        else:
            vif_hac = float(hac.inflation ** 2)  # M-3
        rho_plus = max(0.0, rho_hat)
        vif_ar1 = (1.0 + rho_plus) / (1.0 - rho_plus)
        terms = [1.0, vif_ar1]
        if not math.isnan(vif_hac):
            terms.append(vif_hac)
        vif_gate = max(terms)  # R-7: floored at 1.0, per series, before aggregation

    return VIFResult(
        vif_gate=vif_gate, vif_hac=vif_hac, vif_ar1=vif_ar1, rho_hat=rho_hat,
        lag=hac.lag, lag_rule=hac.lag_rule, source="candidate-only",
        n_series_used=1, n_series_excluded=0, eligible=hac.eligible,
        note="; ".join(notes),
    )


def family_variance_inflation(
    trial_series: list[np.ndarray],
    candidate_returns: np.ndarray | None,
    *,
    label_span: int = 1,
    m_min: int = 8,
) -> VIFResult:
    """VALIDATION-SPEC-002 R-6 -- the family estimator, and the
    anti-gaming construction.

    ``vif_gate = max(candidate, family-median)`` when at least ``m_min``
    logged trial series are eligible; ``candidate-only`` otherwise
    (R-12). ``max`` against the candidate defends against a sponsor
    advancing the one configuration whose own net series happens to be
    cleanest (R-6); ``median``, not ``max``, across trials defends
    against a single pathological trial killing the family AND against
    the incentive not to log a trial that a ``max`` across trials would
    create -- "the single worst incentive this firm can create" (R-6).

    ``vif_gate >= variance_inflation(candidate_returns).vif_gate``
    ALWAYS, for any ``trial_series`` whatsoever -- R-8, the single most
    important property in this module: no number of logged trials, of
    any construction, can drive the graded VIF below the VIF of the
    series actually being graded.

    No candidate return series (``candidate_returns is None``) ->
    ``source = "unmeasurable"``, ``eligible = False`` -- there is no
    fallback to VIF=1 (R-11). A trial series failing R-5's guards is
    excluded from the median and counted in ``n_series_excluded``; if
    more than 25% of logged trial series are excluded, ``eligible =
    False`` regardless of the source branch -- a refusal, not a discount
    (R-9, the dilution attack). If the candidate itself is ineligible,
    the whole result is ineligible (R-14).
    """
    if candidate_returns is None:
        return VIFResult(
            vif_gate=float("nan"), vif_hac=float("nan"), vif_ar1=float("nan"),
            rho_hat=float("nan"), lag=0, lag_rule="andrews",
            source="unmeasurable", n_series_used=0, n_series_excluded=0,
            eligible=False,
            note="No candidate return series supplied; VIF is "
                 "unmeasurable (R-11). There is no fallback to VIF=1.",
        )

    v_cand = variance_inflation(candidate_returns, label_span=label_span)

    usable: list[VIFResult] = []
    n_excluded = 0
    for s in trial_series:
        v = variance_inflation(s, label_span=label_span)
        if v.eligible:
            usable.append(v)
        else:
            n_excluded += 1

    n_used = len(usable)
    total = n_used + n_excluded

    if n_used >= m_min:
        v_fam = float(np.median([u.vif_gate for u in usable]))
        vif_gate = max(v_cand.vif_gate, v_fam)  # R-8: never below the candidate's own
        source = "max(candidate, family-median)"
    else:
        vif_gate = v_cand.vif_gate
        source = "candidate-only"

    notes: list[str] = []
    eligible = v_cand.eligible
    if not v_cand.eligible:
        notes.append(
            "candidate series is ineligible (R-5); the whole family "
            "result is ineligible (R-14)")
    if total > 0 and n_excluded > 0.25 * total:
        eligible = False
        notes.append(
            f"R-9: {n_excluded}/{total} logged trial series excluded by "
            "the length/eligibility floors (> 25%) -- refused rather "
            "than discounted")

    return VIFResult(
        vif_gate=vif_gate, vif_hac=v_cand.vif_hac, vif_ar1=v_cand.vif_ar1,
        rho_hat=v_cand.rho_hat, lag=v_cand.lag, lag_rule=v_cand.lag_rule,
        source=source, n_series_used=n_used, n_series_excluded=n_excluded,
        eligible=eligible, note="; ".join(notes),
    )


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
