"""Carry stress semantics — Validation Ruling 003 section 3.6.

Carry is a signed cash flow, not a cost, so ``costs.CostModel.scaled(m)``
never touches it (T-16). This module supplies the SANCTIONED ways to vary
it instead: an explicit scenario (``CarryScenario`` / ``apply_carry_scenario``),
a named adverse shift with its own bisectable breakeven statistic
(``shift_carry_panel`` / ``carry_breakeven_bps_annual``), and a stationary
block bootstrap of the realized series (``tail_bootstrap_carry``).

A multiplicative stress (``f -> m*f``) is deliberately NOT provided here.
Applied to a receipt, it does not stress the family — it manufactures a
robustness result equal to the ceiling of whatever bracket searches for it
(I-037; ``research/VALIDATION-RULING-003-carry-accounting.md`` section 3.6).
``carry_breakeven_bps_annual`` is monotone in its shift by construction
(subtracting a per-bar constant changes the mean and never the standard
deviation), which is precisely the property a multiplier lacks.
"""

from __future__ import annotations

import enum

import numpy as np
import pandas as pd

from . import stats

BP = 1e-4


class CarryScenario(str, enum.Enum):
    """The mandatory scenario set named at sealing (Ruling 003 section 3.6),
    minus ``SHIFT(delta)`` — which takes a parameter and lives in
    :func:`shift_carry_panel` instead — and ``TAIL_BOOTSTRAP``, whose
    output is a distribution, not a panel, and lives in
    :func:`tail_bootstrap_carry`.
    """

    REALIZED = "REALIZED"
    ZERO = "ZERO"
    SIGN_INVERTED = "SIGN_INVERTED"


def apply_carry_scenario(funding_panel: pd.DataFrame, scenario: CarryScenario) -> pd.DataFrame:
    """Apply a REALIZED / ZERO / SIGN_INVERTED scenario to a funding panel.

    ``ZERO`` multiplies by 0.0 rather than constructing a fresh all-zero
    frame, so a genuine coverage gap (``NaN``) stays ``NaN`` under this
    scenario too — "zero funding" and "no data" remain distinct all the
    way through (0.0 * NaN is still NaN).

    ``SIGN_INVERTED`` negates every value exactly, so
    ``apply_carry_scenario(p, SIGN_INVERTED)`` composed with the engine's
    accrual is bit-exact sign flip of the REALIZED accrual (T-16).
    """
    if scenario == CarryScenario.REALIZED:
        return funding_panel
    if scenario == CarryScenario.ZERO:
        return funding_panel * 0.0
    if scenario == CarryScenario.SIGN_INVERTED:
        return -funding_panel
    raise ValueError(f"apply_carry_scenario does not handle {scenario!r}")


def shift_carry_panel(
    funding_panel: pd.DataFrame, delta_bps_annual: float, periods_per_year: int
) -> pd.DataFrame:
    """``SHIFT(delta)``: ``f -> f - delta``, delta expressed in bps/yr and
    converted to a per-bar rate using the ENGINE's own bar cadence
    (``periods_per_year``) — the bar-to-bar calendar spacing, which is
    regular by construction (daily, hourly, ...). This is a different
    thing from the PRINT-level cadence T-9 forbids assuming (funding
    prints within a single bar are irregular; bars themselves are not).
    A genuine coverage gap (``NaN``) stays ``NaN`` (subtracting a
    constant from ``NaN`` is still ``NaN``).
    """
    per_bar = delta_bps_annual * BP / periods_per_year
    return funding_panel - per_bar


def carry_breakeven_bps_annual(
    net_returns_at_shift,
    periods_per_year: int,
    bracket: tuple[float, float] = (0.0, 2000.0),
    hurdle: float = 3.0,
    iters: int = 40,
) -> float:
    """Bisect the adverse carry shift (bps/yr) at which the net return's
    t-statistic falls below ``hurdle`` (Ruling 003 section 3.6's
    ``carry_breakeven_bps_annual``). Monotone by construction of
    :func:`shift_carry_panel` — unlike a multiplier applied to a receipt,
    which is not (I-037; T-18).

    ``net_returns_at_shift`` : callable ``delta_bps_annual -> net returns``.
    """
    lo, hi = bracket
    t_lo = stats.sr_tstat(np.asarray(net_returns_at_shift(lo)))
    if t_lo < hurdle:
        return lo
    t_hi = stats.sr_tstat(np.asarray(net_returns_at_shift(hi)))
    if t_hi >= hurdle:
        return hi
    for _ in range(iters):
        mid = 0.5 * (lo + hi)
        tm = stats.sr_tstat(np.asarray(net_returns_at_shift(mid)))
        if tm >= hurdle:
            lo = mid
        else:
            hi = mid
    return lo


def tail_bootstrap_carry(
    funding_panel: pd.DataFrame,
    positions: pd.DataFrame,
    n_paths: int = 1000,
    block: int = 21,
    seed: int = 0,
) -> dict:
    """Stationary block bootstrap of the REALIZED per-bar carry accrual
    series (Ruling 003 section 3.6's ``TAIL_BOOTSTRAP``) — resampled in
    blocks of ``block`` bars, ``n_paths`` paths, each path's own worst-bar
    value and mean recorded. Because every path is built from resampled
    real observations, no path's worst bar can ever be MORE extreme than
    the realized series' own worst bar — the bootstrap can only ever
    recover that event, never manufacture a worse one, which is exactly
    what makes "the 5th percentile is at least as severe as the realized
    worst day" (T-17) a meaningful check rather than a tautology: it is
    only true if the block/path combination actually re-draws the extreme
    bar often enough.
    """
    common = [c for c in positions.columns if c in funding_panel.columns]
    accrual = -(positions[common] * funding_panel[common]).sum(axis=1)
    accrual = accrual.dropna().to_numpy(dtype=float)
    n = accrual.size

    rng = np.random.default_rng(seed)
    worst = np.empty(n_paths)
    means = np.empty(n_paths)
    for p in range(n_paths):
        path = np.empty(n)
        filled = 0
        while filled < n:
            start = rng.integers(0, n)
            take = min(block, n - filled)
            draw_idx = (start + np.arange(take)) % n
            path[filled:filled + take] = accrual[draw_idx]
            filled += take
        worst[p] = path.min()
        means[p] = path.mean()

    return {
        "worst_day": worst,
        "mean": means,
        "p5_worst_day": float(np.percentile(worst, 5)),
        "realized_worst_day": float(accrual.min()),
        "realized_mean": float(accrual.mean()),
    }
