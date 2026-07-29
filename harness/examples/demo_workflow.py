"""End-to-end Castellan workflow on synthetic data, under Amendment P-1.

    pre-register -> seal the holdout spec (Gate 0, before any research)
    -> develop in-sample (every run logged) -> acquire holdout ONCE at
    Gate 1 -> evaluate Gate 1 -> render Validation Report

The holdout series itself is not generated until acquire_once() runs —
that is the entire point of P-1 (research/VALIDATION-RULING-001-holdout-
regime.md). Here the Gate-1 "vendor fetch" is a stub that deterministically
extends the same synthetic process from the sealed cutoff forward, standing
in for a real venue call.

Run:  python examples/demo_workflow.py
"""

import numpy as np
import pandas as pd

from castellan import (
    TrialRegistry, PITStore, HoldoutVault, run_backtest, US_EQUITY_LARGE,
    evaluate_gate1, stats,
)
from castellan.cv import walk_forward_windows

rng = np.random.default_rng(7)
ASSETS = ["ETF_A", "ETF_B", "ETF_C"]


def synthetic_prices(start: str, n: int, seed: int) -> pd.DataFrame:
    r = np.random.default_rng(seed)
    noise = r.normal(0.0002, 0.010, size=(n, len(ASSETS)))
    return pd.DataFrame(
        100 * np.exp(np.cumsum(noise, axis=0)),
        index=pd.bdate_range(start, periods=n),
        columns=ASSETS,
    )


# --- in-sample data: this is all that exists before Gate 1 -------------
IN_SAMPLE_N = 1200
insample = synthetic_prices("2020-01-01", IN_SAMPLE_N, seed=7)

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

# --- seal the holdout spec BEFORE any research (Gate 0) -----------------
store = PITStore("demo_pit.db", reg)
vault = HoldoutVault("demo_vault", reg, "etf-daily", family="etf-tsmom", store=store)
PASSPHRASE = "principal-only-passphrase"       # held by the Principal; never stored
CUTOFF = insample.index[-1]
vault.seal(
    source="synthetic-demo",
    dataset_id="etf-universe-1",
    instrument_identity="ETF_A,ETF_B,ETF_C",
    query_semantics={"fields": ["close"], "freq": "1bd"},
    cutoff=CUTOFF,
    schema_fingerprint={"columns": ASSETS, "dtypes": {c: "float64" for c in ASSETS}},
    # Acceptance 001 C-2: the passphrase is committed here, at seal time,
    # as a salted one-way verifier — never stored in recoverable form.
    # This is what lets acquire_once() refuse a wrong-but-non-empty
    # passphrase cryptographically, before any fetch (the I-015 fix).
    passphrase=PASSPHRASE,
)
print(f"Holdout spec sealed: cutoff C={CUTOFF.date()}. Holdout plaintext does "
      f"not exist yet and will not until Gate 1.")

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

# --- choose plateau centroid (not argmax) and go to Gate 1 -------------
CHOSEN_LOOKBACK = 90

def fetch_holdout_from_vendor(spec: dict) -> pd.DataFrame:
    """Stands in for a real venue call: this is the ONLY place the holdout
    series is generated, and it only runs inside acquire_once(), at Gate 1."""
    cutoff = pd.Timestamp(spec["cutoff"])
    return synthetic_prices((cutoff + pd.Timedelta(days=1)).date().isoformat(),
                            400, seed=8)

holdout = vault.acquire_once(PASSPHRASE, fetch_holdout_from_vendor,
                             acquired_by="quant-validation")
print(f"Holdout acquired ONCE: {holdout.index[0].date()} .. {holdout.index[-1].date()}")
prices = pd.concat([insample, holdout])

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
    # I-010 (Acceptance 001 G1/G5): backtest_years is the OOS holdout's
    # own apparent length (previously this passed len(prices)/252 — the
    # combined in-sample+holdout length — which is exactly the "sole
    # existing caller already passes the offending value" case the ruling
    # named). oos_index is what lets the harness VERIFY it against the
    # holdout's real calendar span rather than trusting it.
    backtest_years=len(holdout) / 252,
    oos_index=holdout.index,
)

print("\n" + report.to_markdown())
print("\nNote how the Gate refuses to PASS without the parameter surface "
      "and the Red-Team Memo — INSUFFICIENT-DATA is not PASS.")
