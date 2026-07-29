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


class FundingCoverageError(ValueError):
    """Ruling 003 T-12: a funding panel cell is ``NaN`` (genuine coverage
    gap — the symbol is not yet listed) at a bar where the position is
    non-zero. Absent data must not read as zero funding — that is the
    free-carry failure mode, and it is the direction that flatters — so
    the engine refuses to accrue rather than silently treating it as
    ``0.0``. A bar within a symbol's coverage span with no matching print
    is legitimately ``0.0`` and does not raise."""


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
    # Ruling 003 section 3.3: a signed cash flow, reported as its OWN
    # series, never netted into `cost_returns` (which stays frictions-
    # only). Defaults to an empty Series so an unseeded, funding-free
    # caller sees an explicit zero-length field rather than a missing
    # attribute -- run_backtest below always fills it in against the real
    # index for anything it actually constructs.
    carry_accrual: pd.Series = field(default_factory=lambda: pd.Series(dtype=float))

    @property
    def total_cost_drag_annual_bps(self) -> float:
        ppy = self.config.get("periods_per_year", 252)
        return float(self.cost_returns.mean() * ppy / 1e-4)

    @property
    def total_carry_accrual_annual_bps(self) -> float:
        """Companion to `total_cost_drag_annual_bps` (Ruling 003 section
        3.3): describes the signed carry cash flow, never frictions."""
        ppy = self.config.get("periods_per_year", 252)
        return float(self.carry_accrual.mean() * ppy / 1e-4)


def run_backtest(
    prices: pd.DataFrame,
    target_weights: pd.DataFrame,
    cost_model: CostModel | dict[str, CostModel],
    registry: TrialRegistry,
    family: str,
    config: dict,
    execution_lag: int = 1,
    periods_per_year: int = 252,
    sigma_daily: pd.DataFrame | None = None,
    adv_notional: pd.DataFrame | None = None,
    book_notional: float = 1.0,
    notes: str = "",
    funding_panel: pd.DataFrame | None = None,
) -> BacktestResult:
    """Run a daily-or-lower-frequency backtest and log it as a trial.

    Parameters
    ----------
    prices : (T, A) close prices, DatetimeIndex ascending.
    target_weights : (T, A) desired weights decided at each bar's close,
        using information available at that close ONLY. The engine shifts
        them by `execution_lag` bars before they earn returns.
    cost_model : from castellan.costs — the shared library, no hand-rolls.
        Either a single `CostModel` (applied to every column, full
        backwards compatibility) or a `dict[str, CostModel]` mapping
        asset column -> model (Ruling 003 section 3.4). A mapping that
        omits a traded column raises rather than defaulting — running
        each leg as its own backtest and adding the results outside the
        engine is refused (A2 forbids a number produced outside it; it
        doubles the family's trial count for one economic strategy; and
        it makes a delta-neutral pair's carry irrecoverable, since the
        netting that produces the receipt happens ACROSS legs).
    registry / family / config : trial accounting. `config` should contain
        every parameter that defines this variant; its hash is the trial's
        identity.
    execution_lag : bars between decision and position. Must be >= 1.
    funding_panel : (T, A) realized funding, one column per funded asset,
        aligned to `prices.index` (Ruling 003 section 3.2/3.3) — build it
        with `castellan.data.pit_funding_panel`. Accrued as a SIGNED cash
        flow, `-(positions * funding_panel)`, reported on its own as
        `BacktestResult.carry_accrual` and NEVER netted into
        `cost_returns` (which stays frictions-only). A column absent from
        the panel contributes zero (T-7); a `NaN` cell aligned with a
        non-zero position raises `FundingCoverageError` rather than
        silently accruing zero (T-12) — absent data must not read as
        zero funding, that is the free-carry failure mode.
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
    if funding_panel is not None and not prices.index.equals(funding_panel.index):
        raise ValueError("prices and funding_panel must share an index")

    assets = list(map(str, prices.columns))

    asset_rets = prices.pct_change()
    positions = target_weights.shift(execution_lag).fillna(0.0)
    gross = (positions * asset_rets).sum(axis=1)

    # Turnover: change in weights each bar (per side traded).
    trades = positions.diff().abs().fillna(positions.abs())
    turnover = trades.sum(axis=1)

    if isinstance(cost_model, dict):
        missing = [c for c in assets if c not in cost_model]
        if missing:
            raise ValueError(
                f"cost_model mapping omits traded column(s): {missing}. A "
                "mapping must price every traded column; there is no "
                "default (Ruling 003 section 3.4)."
            )
        # Per-leg, independently computed, then summed (T-14) — never a
        # single blended model across columns with different economics.
        trade_cost = pd.Series(0.0, index=prices.index)
        borrow = pd.Series(0.0, index=prices.index)
        for col in assets:
            cm = cost_model[col]
            tr = trades[col]
            if adv_notional is not None:
                sig_col = (
                    sigma_daily[col].to_numpy()
                    if sigma_daily is not None
                    else asset_rets[col].rolling(20).std().fillna(0.0).to_numpy()
                )
                per_side = cm.per_side_cost(
                    trade_notional=tr.to_numpy() * book_notional,
                    sigma_daily=sig_col,
                    adv_notional=adv_notional[col].to_numpy(),
                )
                trade_cost = trade_cost + pd.Series(per_side * tr.to_numpy(), index=prices.index)
            else:
                per_side = float(np.asarray(cm.per_side_cost(1.0)).ravel()[0])
                trade_cost = trade_cost + tr * per_side
            short_col = (-positions[col].clip(upper=0)).to_numpy()
            borrow = borrow + pd.Series(
                cm.borrow_per_bar(short_col, periods_per_year=periods_per_year),
                index=prices.index,
            )
        cost_model_config: dict | str = {col: cost_model[col].name for col in assets}
    else:
        # Single-model path, kept in its original (pre-Ruling-003) shape
        # so a funding-free single-model run is bit-identical to the
        # pre-change harness (T-14) — a per-column loop would sum in a
        # different floating-point order.
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

        long_n = positions.clip(lower=0).sum(axis=1)
        short_n = (-positions.clip(upper=0)).sum(axis=1)
        borrow = pd.Series(
            cost_model.borrow_per_bar(short_n.values, periods_per_year=periods_per_year),
            index=prices.index,
        )
        cost_model_config = cost_model.name

    # Frictions only — commission, half-spread, impact, borrow. Never a
    # signed cash flow (Ruling 003 section 3.3): that is `carry_accrual`,
    # computed separately below and reported on its own.
    cost_ret = (trade_cost + borrow).fillna(0.0)

    # Carry accrual: a signed cash flow on LAGGED positions (the same
    # `positions` object gross uses), per asset, never on an aggregate
    # (Ruling 003 section 3.3 / T-6 / T-7 / T-11).
    if funding_panel is not None:
        common = [c for c in assets if c in funding_panel.columns]
        if common:
            fp = funding_panel[common]
            pos_common = positions[common]
            nan_gap = fp.isna() & (pos_common != 0)
            if nan_gap.to_numpy().any():
                raise FundingCoverageError(
                    "funding_panel has a coverage gap (NaN) at a bar where "
                    "the position is non-zero — absent data must not read "
                    "as zero funding (Ruling 003 T-12)."
                )
            carry_accrual = -(pos_common * fp.fillna(0.0)).sum(axis=1)
        else:
            carry_accrual = pd.Series(0.0, index=prices.index)
    else:
        carry_accrual = pd.Series(0.0, index=prices.index)

    net = (gross + carry_accrual - cost_ret).fillna(0.0)

    full_config = {
        **config,
        "cost_model": cost_model_config,
        "execution_lag": execution_lag,
        "periods_per_year": periods_per_year,
        "n_bars": int(len(prices)),
        "assets": assets,
    }
    if funding_panel is not None:
        full_config["funding_panel_decision_time"] = funding_panel.attrs.get("decision_time")
        full_config["funding_panel_sha256"] = funding_panel.attrs.get("sha256")

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
        carry_accrual=carry_accrual,
    )
