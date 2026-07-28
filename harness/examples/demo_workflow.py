"""End-to-end Castellan workflow on synthetic data.

    pre-register -> lock holdout -> develop in-sample (every run logged)
    -> open holdout ONCE -> evaluate Gate 1 -> render Validation Report

Run:  python examples/demo_workflow.py
"""

import numpy as np
import pandas as pd

from castellan import (
    TrialRegistry, HoldoutVault, run_backtest, US_EQUITY_LARGE,
    evaluate_gate1, stats,
)
from castellan.cv import walk_forward_windows

rng = np.random.default_rng(7)

# --- synthetic market: 6y daily, 3 ETFs, weak momentum planted ---------
T, A = 1550, 3
noise = rng.normal(0.0002, 0.010, size=(T, A))
prices = pd.DataFrame(
    100 * np.exp(np.cumsum(noise, axis=0)),
    index=pd.bdate_range("2020-01-01", periods=T),
    columns=["ETF_A", "ETF_B", "ETF_C"],
)

reg = TrialRegistry("demo_registry.db")
reg.open_hypothesis(
    family="etf-tsmom",
    statement="Liquid ETFs exhibit 3-12 month time-series momentum",
    mechanism="Slow-moving institutional flows under-react to trends; "
              "the other side is rebalancers selling winners on schedule",
    falsifier="Rolling 2y net Sharpe < 0 across the ETF set",
    universe="ETF_A, ETF_B, ETF_C",
    horizon="20d rebalance",
    success_criteria="Gate 1 per Charter 4.4",
    trial_budget=20,
)

# --- lock the holdout BEFORE any research ------------------------------
vault = HoldoutVault("demo_vault", reg, "etf-daily")
PASSPHRASE = "principal-only-passphrase"       # held by the Principal
insample = vault.lock(prices, PASSPHRASE, fraction=0.25)
print(f"In-sample: {insample.index[0].date()} .. {insample.index[-1].date()} "
      f"({len(insample)} bars); holdout locked & encrypted.")

# --- develop: every variant is a logged trial --------------------------
def tsmom_weights(px: pd.DataFrame, lookback: int, cap: float) -> pd.DataFrame:
    sig = np.sign(px.pct_change(lookback))
    return (sig / px.shape[1] * cap).fillna(0.0)

for lookback in (40, 60, 90, 120, 180, 250):
    w = tsmom_weights(insample, lookback, cap=0.9)
    res = run_backtest(insample, w, US_EQUITY_LARGE, reg, "etf-tsmom",
                       {"lookback": lookback, "cap": 0.9})
    print(f"  trial {res.trial_id}: lookback={lookback:>3}  "
          f"net SR={stats.sharpe_annual(res.net_returns.values):+.2f}")

fs = reg.family_stats("etf-tsmom")
print(f"Registry: N={fs.n_trials} trials, per-period SR std={fs.sr_period_std:.4f}")

# --- choose plateau centroid (not argmax) and go to the holdout --------
CHOSEN_LOOKBACK = 90
holdout = vault.open_once(PASSPHRASE, opened_by="quant-validation")
print(f"Holdout opened ONCE: {holdout.index[0].date()} .. {holdout.index[-1].date()}")

def evaluate(cost_multiplier: float) -> np.ndarray:
    w = tsmom_weights(holdout, CHOSEN_LOOKBACK, cap=0.9)
    res = run_backtest(holdout, w, US_EQUITY_LARGE.scaled(cost_multiplier),
                       reg, "etf-tsmom",
                       {"lookback": CHOSEN_LOOKBACK, "cap": 0.9,
                        "phase": "holdout", "cost_x": cost_multiplier})
    return res.net_returns.values

oos_net = evaluate(1.0)

# walk-forward on the full series for WFE
wfe_pairs = []
full_w = tsmom_weights(prices, CHOSEN_LOOKBACK, 0.9)
full = run_backtest(prices, full_w, US_EQUITY_LARGE, reg, "etf-tsmom",
                    {"lookback": CHOSEN_LOOKBACK, "phase": "wfe"})
r_all = full.net_returns.values
for train, test in walk_forward_windows(len(r_all), 10):
    wfe_pairs.append((stats.sharpe_period(r_all[train]),
                      stats.sharpe_period(r_all[test])))

report = evaluate_gate1(
    strategy=f"ETF TSMOM lb={CHOSEN_LOOKBACK}",
    family="etf-tsmom",
    registry=reg,
    oos_net_returns=oos_net,
    periods_per_year=252,
    net_returns_at_cost_multiplier=evaluate,
    wfe_sr_pairs=wfe_pairs,
    param_grid_net_pnls=None,          # left absent on purpose -> INSUFFICIENT-DATA
    red_team_memo_present=False,       # ditto
    backtest_years=len(prices) / 252,
)

print("\n" + report.to_markdown())
print("\nNote how the Gate refuses to PASS without the parameter surface "
      "and the Red-Team Memo — INSUFFICIENT-DATA is not PASS.")
