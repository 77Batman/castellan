"""Parameter-grid runner — feeds the Gate 1 surface criterion.

Charter 4.4: "plateau not spike; >= 60% of the ±50% grid net-profitable."
Charter 4.6: "Prefer the plateau centroid to the argmax. Selecting the
peak of a parameter surface IS the overfitting operation."

Every grid point runs through ``run_backtest`` and therefore increments
the family's trial counter — a 25-point grid is 25 trials, and that is
the honest accounting the DSR then pays for.
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass
from typing import Callable

import numpy as np
import pandas as pd

from .costs import CostModel
from .engine import run_backtest
from .registry import TrialRegistry
from .stats import sharpe_annual


def grid_from_center(
    center: dict[str, float],
    fraction: float = 0.5,
    steps: int = 5,
    integer_params: set[str] | None = None,
    max_points: int = 200,
) -> list[dict]:
    """Cartesian ±``fraction`` grid around ``center`` with ``steps``
    multipliers per axis. Refuses to explode past ``max_points`` —
    trim the axes rather than silently sampling."""
    integer_params = integer_params or set()
    mults = np.linspace(1.0 - fraction, 1.0 + fraction, steps)
    axes = {}
    for k, v in center.items():
        vals = [v * m for m in mults]
        if k in integer_params:
            vals = sorted({int(round(x)) for x in vals if round(x) >= 1})
        axes[k] = vals
    n_points = int(np.prod([len(v) for v in axes.values()]))
    if n_points > max_points:
        raise ValueError(
            f"Grid has {n_points} points (> {max_points}). Reduce axes or "
            "steps — every point is a logged trial and the budget is real."
        )
    keys = list(axes)
    return [dict(zip(keys, combo))
            for combo in itertools.product(*(axes[k] for k in keys))]


@dataclass
class GridResult:
    params_list: list[dict]
    net_pnls: list[float]
    net_sharpes: list[float]
    trial_ids: list[int]
    fraction_profitable: float
    argmax_params: dict
    plateau_centroid_params: dict

    @property
    def param_grid_net_pnls(self) -> list[float]:
        """Pass directly to ``evaluate_gate1(param_grid_net_pnls=...)``."""
        return self.net_pnls


def run_parameter_grid(
    prices: pd.DataFrame,
    weights_factory: Callable[[pd.DataFrame, dict], pd.DataFrame],
    grid: list[dict],
    cost_model: CostModel,
    registry: TrialRegistry,
    family: str,
    periods_per_year: int = 252,
    profitable_quantile: float = 0.5,
    **backtest_kwargs,
) -> GridResult:
    """Run every grid point through the engine (each is a logged trial).

    ``weights_factory(prices, params) -> target_weights`` is the only
    strategy-specific piece. The plateau centroid is the average of the
    top-``profitable_quantile`` profitable points — the configuration to
    carry forward instead of the argmax.
    """
    pnls, sharpes, ids = [], [], []
    for params in grid:
        w = weights_factory(prices, params)
        res = run_backtest(
            prices, w, cost_model, registry, family,
            {"grid": True, **params},
            periods_per_year=periods_per_year,
            **backtest_kwargs,
        )
        pnls.append(float(res.net_returns.sum()))
        sharpes.append(float(sharpe_annual(res.net_returns.values,
                                           periods_per_year)))
        ids.append(res.trial_id)

    pnl_arr = np.array(pnls)
    frac = float(np.mean(pnl_arr > 0))
    argmax = grid[int(np.argmax(pnl_arr))]

    # Plateau centroid: mean of parameters over the better-profitable half.
    prof_idx = [i for i, p in enumerate(pnls) if p > 0]
    if prof_idx:
        cut = np.quantile(pnl_arr[prof_idx], profitable_quantile)
        top = [i for i in prof_idx if pnl_arr[i] >= cut]
    else:
        top = [int(np.argmax(pnl_arr))]
    keys = grid[0].keys()
    centroid = {
        k: float(np.mean([grid[i][k] for i in top])) for k in keys
    }

    return GridResult(
        params_list=grid,
        net_pnls=pnls,
        net_sharpes=sharpes,
        trial_ids=ids,
        fraction_profitable=frac,
        argmax_params=argmax,
        plateau_centroid_params=centroid,
    )
