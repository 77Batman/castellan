"""The backtest engine — the only sanctioned way to run a backtest.

Two properties are enforced structurally rather than by convention:

1. **Every run is a trial.** `run_backtest` requires a TrialRegistry and
   a pre-registered hypothesis family, and logs the run (config hash +
   full net return series) before returning results. There is no flag to
   turn this off. Exploratory runs count — that is the point.

2. **Same-bar fills are impossible.** Target weights decided at bar t are
   applied from bar t + execution_lag, and execution_lag < 1 raises.
   (DB *Seven Sins*: a reversal strategy's Sharpe fell 1.41 -> 0.26 on
   this one correction.)

Weights are fractions of book notional per asset (long positive, short
negative). Returns are simple per-bar returns of the assets.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from .costs import CostModel
from .registry import TrialRegistry


class SameBarFillError(ValueError):
    pass


@dataclass
class BacktestResult:
    family: str
    trial_id: int
    gross_returns: pd.Series
    net_returns: pd.Series
    cost_returns: pd.Series
    turnover: pd.Series
    positions: pd.DataFrame
    config: dict = field(default_factory=dict)

    @property
    def total_cost_drag_annual_bps(self) -> float:
        ppy = self.config.get("periods_per_year", 252)
        return float(self.cost_returns.mean() * ppy / 1e-4)


def run_backtest(
    prices: pd.DataFrame,
    target_weights: pd.DataFrame,
    cost_model: CostModel,
    registry: TrialRegistry,
    family: str,
    config: dict,
    execution_lag: int = 1,
    periods_per_year: int = 252,
    sigma_daily: pd.DataFrame | None = None,
    adv_notional: pd.DataFrame | None = None,
    book_notional: float = 1.0,
    notes: str = "",
) -> BacktestResult:
    """Run a daily-or-lower-frequency backtest and log it as a trial.

    Parameters
    ----------
    prices : (T, A) close prices, DatetimeIndex ascending.
    target_weights : (T, A) desired weights decided at each bar's close,
        using information available at that close ONLY. The engine shifts
        them by `execution_lag` bars before they earn returns.
    cost_model : from castellan.costs — the shared library, no hand-rolls.
    registry / family / config : trial accounting. `config` should contain
        every parameter that defines this variant; its hash is the trial's
        identity.
    execution_lag : bars between decision and position. Must be >= 1.
    """
    if execution_lag < 1:
        raise SameBarFillError(
            "execution_lag must be >= 1: filling on the bar that generated "
            "the signal is look-ahead. (Charter 4.6.)"
        )
    if not prices.index.equals(target_weights.index):
        raise ValueError("prices and target_weights must share an index")
    if not prices.index.is_monotonic_increasing:
        raise ValueError("prices index must be ascending")

    asset_rets = prices.pct_change()
    positions = target_weights.shift(execution_lag).fillna(0.0)
    gross = (positions * asset_rets).sum(axis=1)

    # Turnover: change in weights each bar (per side traded).
    trades = positions.diff().abs().fillna(positions.abs())
    turnover = trades.sum(axis=1)

    # Per-side trading costs.
    if adv_notional is not None:
        sig = sigma_daily if sigma_daily is not None else asset_rets.rolling(20).std().fillna(0.0)
        per_side = cost_model.per_side_cost(
            trade_notional=trades.values * book_notional,
            sigma_daily=sig.values,
            adv_notional=adv_notional.values,
        )
        trade_cost = pd.Series(
            (per_side * trades.values).sum(axis=1), index=prices.index
        )
    else:
        per_side = cost_model.per_side_cost(1.0)
        trade_cost = turnover * float(np.asarray(per_side).ravel()[0])

    # Carry: borrow on shorts, funding on gross, per bar held.
    long_n = positions.clip(lower=0).sum(axis=1)
    short_n = (-positions.clip(upper=0)).sum(axis=1)
    carry = pd.Series(
        cost_model.carry_per_bar(long_n.values, short_n.values),
        index=prices.index,
    )

    cost_ret = (trade_cost + carry).fillna(0.0)
    net = (gross - cost_ret).fillna(0.0)

    full_config = {
        **config,
        "cost_model": cost_model.name,
        "execution_lag": execution_lag,
        "periods_per_year": periods_per_year,
        "n_bars": int(len(prices)),
        "assets": list(map(str, prices.columns)),
    }
    trial_id = registry.log_trial(
        family=family,
        config=full_config,
        net_returns=net.values,
        periods_per_year=periods_per_year,
        notes=notes,
    )
    return BacktestResult(
        family=family,
        trial_id=trial_id,
        gross_returns=gross.fillna(0.0),
        net_returns=net,
        cost_returns=cost_ret,
        turnover=turnover,
        positions=positions,
        config=full_config,
    )
