# Castellan Harness

The backtest harness for Castellan Capital. This package is the answer to the Charter's weakest point: without it, every number in a Validation Report is narration. With it, the rules in Part IV are properties of the code path rather than promises.

## What is enforced in code, not prose

**Pre-registration before any run.** `run_backtest` refuses to execute unless the hypothesis family exists in the registry with a non-empty statement, mechanism, and falsifier (Gate 0, items 1–2). `PreRegistrationError` otherwise.

**Every run is a trial.** There is no way to run a backtest through the engine without incrementing N for the family and storing the config hash and the *full net return series*. Exploratory runs count. The registry — not the sponsor — is where Gate 1 gets N and the cross-sectional trial-Sharpe dispersion that the Deflated Sharpe Ratio requires, and the stored return matrix is what CSCV/PBO runs on.

**Same-bar fills are impossible.** `execution_lag < 1` raises `SameBarFillError`. The test suite includes a perfect-foresight signal that would print money at lag 0 and verifies the mandatory lag destroys it.

**One cost library.** `castellan.costs.CostModel` implements the Charter stack (commission + half-spread + square-root impact + borrow/funding carry) with presets for US equities, equity shorts (4%/yr specials assumed), crypto perps (taker + funding), and Polymarket. `.scaled(2.0)` produces the stress copy for the cost-robustness criterion. Researchers may not hand-roll costs; the engine only accepts a `CostModel`.

**The holdout is never fetched before Gate 1 (Amendment P-1).** `HoldoutVault.seal(..., passphrase=...)` writes a hash-committed `spec.json` at pre-registration — cutoff `C`, dataset identity, schema fingerprint — and (paired with a **required** `PITStore`) writes a physical ingest ceiling: `PITStore.ingest` and `PITStore.ingest_documents` both raise `HoldoutCeilingError` and ingest nothing if a batch contains any observation after `C`, so a seat that calls a loader with the "wrong" end date cannot leak the holdout by accident. `seal()` also writes a salted, one-way passphrase verifier — never the passphrase itself — so `HoldoutVault.acquire_once(passphrase, fetch, ...)` can refuse a wrong-but-non-empty passphrase *cryptographically, before any fetch* (a typo does not brick the family). Acquisition runs at Gate 1, exactly once: it logs the attempt before any network call, verifies the sealed spec hasn't been tampered with, refuses if `C` hasn't been reached yet, and refuses a fetched frame containing any row at or before `C` (the acquisition-side twin of the ingest ceiling — a fetch cannot silently hand back in-sample history and have it sealed as "the holdout"). On success it encrypts and permanently retains the fetched series (PBKDF2 → Fernet) and lifts the ceiling, recording which acquisition did so. A second acquisition raises `HoldoutRetiredError` and is logged; a failed fetch (network error, schema mismatch, or in-sample overlap) moves the vault to `ACQUISITION_FAILED` without retiring it, and a further attempt requires an explicit, logged retry authorization against the same cryptographic passphrase check. A leak-detection check flags any row in the holdout window that was knowable in `pit.db` before the acquisition happened — `event_time` is normalized to UTC at ingest, so this comparison is an instant comparison, not a string comparison with a hidden offset. Gate 1 reads all of this, per family, with no caller-asserted bypass. The legacy fetch-then-lock API (`lock()` / `open_once()`) is retired and hard-raises `HoldoutRegimeError`. See `research/VALIDATION-RULING-001-holdout-regime.md` and `research/VALIDATION-ACCEPTANCE-001-p1-vault.md` for the full design and acceptance history, and `research/DATA-IMPL-002-acceptance-remediation.md` for this remediation.

**The pre-registration is sealed too.** `TrialRegistry.open_hypothesis` computes a sha256 over the canonical JSON of the binding field set (statement, mechanism, falsifier, universe, horizon, success criteria, trial budget, predecessor family, and the R1/R3/R4 forward-holdout fields) and logs it, with a full shadow copy of every field, as a `hypothesis_sealed` event in the append-only event log — a full copy, not a pointer to the mutable row. Re-registering an existing family with any differing binding field raises `PreRegistrationAmendedError`; a raw SQL `UPDATE` to the row is detected (not prevented) by `TrialRegistry.verify_prereg` and fails Gate 1's `Pre-registration integrity` criterion, which also fails if the pre-registration was sealed after the holdout cutoff `C`'s calendar day (the D-006 freeze rider, mechanised).

**Gate 1 is computed.** `evaluate_gate1` produces a `ValidationReport` with every computable Charter 4.4 criterion (net Sharpe, t ≥ 3, DSR ≥ 0.95 from registry N and dispersion, PBO ≤ 0.10 via CSCV S=16 on the registry return matrix, length ≥ max(4y, MinBTL(N)) verified against a calendar-span `oos_index` rather than trusted from a caller-supplied `backtest_years`, holdout single-use from the event log alone, pre-registration integrity, WFE, subperiod positivity, P&L concentration, 2× cost robustness, breakeven cost multiplier via bisection). Criteria the harness cannot verify — parameter surface, capacity, correlation to book, Red-Team Memo, and backtest length without a supplied `oos_index` — are INSUFFICIENT-DATA unless supplied, **and INSUFFICIENT-DATA is not PASS**. The report states on its face whether the holdout is FORWARD or HISTORICAL, embeds the pre-registration and holdout hashes and a sha256 of the evaluated return series, and logs its verdict to the registry.

## The workflow

```python
from castellan import (TrialRegistry, PITStore, HoldoutVault, run_backtest,
                       US_EQUITY_LARGE, evaluate_gate1)

reg = TrialRegistry("book/registry.db")
reg.open_hypothesis(family="etf-tsmom", statement=..., mechanism=...,
                    falsifier=..., universe=..., horizon=...,
                    success_criteria=..., trial_budget=20)

store = PITStore("book/pit.db", reg)

# Gate 0: seal the spec — cutoff C, dataset identity, schema — before any
# research begins. This writes the D2 ingest ceiling into `store` too.
vault = HoldoutVault("book/vaults/etf-daily", reg, "etf-daily", family="etf-tsmom",
                     store=store)
vault.seal(source="yfinance", dataset_id="etf-universe-1",
          instrument_identity="...", query_semantics={...},
          cutoff="2025-01-01", schema_fingerprint={...},
          passphrase=PRINCIPAL_ONLY)

# develop freely against pit_adjusted_close()/pit_price_panel() — the
# store refuses any ingest that would cross C, so the safe path is the
# default path. Every variant run through the engine is logged.
res = run_backtest(insample, weights, US_EQUITY_LARGE, reg,
                   "etf-tsmom", {"lookback": 90})

# Gate 1: fetch and seal the holdout — exactly once, ever, and only now.
holdout = vault.acquire_once(PRINCIPAL_ONLY, fetch_from_vendor,
                             acquired_by="quant-validation")
report = evaluate_gate1("ETF TSMOM", "etf-tsmom", reg, oos_net, 252,
                        backtest_years=len(holdout) / 252,
                        oos_index=holdout.index, ...)
print(report.to_markdown())
```

`examples/demo_workflow.py` runs this end to end on synthetic data and shows a noise strategy failing the Gate on eight criteria. `pytest tests/` (95 tests, 0 failed / 0 skipped / 0 xfail) proves: registry enforcement, look-ahead neutralization, the Charter's noise-Sharpe table, DSR rejecting the best of 200 noise trials while accepting a genuine edge, PBO ≈ 0.5 on noise vs ≤ 0.10 with a real signal, purge/embargo correctness, the P-1 holdout regime including its Acceptance 001 remediation (spec sealing with a cryptographic passphrase verifier, the ingest ceiling on both entry points, acquire-once with its retry/tamper/leak-detection/in-sample-overlap controls, family-scoped Gate 1 evaluation with no caller-asserted bypass, and UTC-normalized event times), pre-registration sealing with tamper detection and the D-006 freeze rider mechanised, calendar-verified backtest length, and predecessor-family trial-count chaining. The legacy `HoldoutVault.lock()`/`open_once()` API is retired and its former test (`test_holdout_locks_splits_and_opens_once`) is replaced in place by `test_holdout_ceilings_and_acquires_once_p1` — see `research/VALIDATION-ACCEPTANCE-001-p1-vault.md` §4 and `research/DATA-IMPL-002-acceptance-remediation.md`.

## Charter amendments this implies (for the Principal to ratify)

1. **§7.3 (Validation Report):** a report is valid only if generated by `evaluate_gate1` against the live registry, with the returns sha256 and registry N embedded. A report without a harness artifact is INSUFFICIENT-DATA by definition.
2. **§4.3 item 6:** "trial counter opened and instrumented" now means: the family exists in `registry.db` and all backtests route through `run_backtest`. Any backtest number produced outside the engine is inadmissible.
3. **Part VIII:** `registry.db` and the vault directories live in `book/` in the git repo, which is the book of record; Oracle stores pointers and summaries only.

## The data layer (`castellan.data`, `castellan.loaders`)

**PITStore** is an append-only store where every observation carries `event_time` (when it became true) and `knowledge_time` (when the firm first observed it). `asof(decision_time)` reconstructs exactly what was knowable at that moment. Vendor restatements — yfinance re-adjusting a close, FRED revising a print — create a *new version* with a later `knowledge_time`; the old row is preserved, and the restatement is logged to the Trial Registry as a `data_restatement` incident automatically.

**The yfinance hazard is fixed structurally.** `fetch_yfinance` pulls with `auto_adjust=False` and stores raw OHLCV plus splits/dividends as separate point-in-time observations. Research consumes `pit_adjusted_close(store, ..., decision_time)`, which back-adjusts using only corporate actions *knowable at that decision time*. The test suite demonstrates the trap directly: a split ingested at knowledge-time T₂ cannot alter the adjusted series as it existed at T₁ < T₂.

Loaders exist for yfinance (equities/ETFs), ccxt (crypto OHLCV and perp funding-rate history, paginated), and SEC EDGAR (filing metadata keyed to `acceptanceDateTime` — the genuine point-in-time stamp for event studies; set a compliant `user_agent`). Parsing is separated from fetching so parse logic is tested offline; network fetches run in your environment with `pip install ".[data]"`.

## The grid runner (`castellan.grid`)

`grid_from_center(params, fraction=0.5, steps=5)` builds the Charter's ±50% grid (refusing to explode past a point cap — every point is a logged trial), and `run_parameter_grid` runs each point through the engine, incrementing N honestly, then returns the `param_grid_net_pnls` list that plugs straight into `evaluate_gate1`, the fraction profitable, and the **plateau centroid** parameters to carry forward instead of the argmax (Charter 4.6: selecting the peak *is* the overfitting operation).

## The paper book (`castellan.book`)

Three blotters — orders, executions, trades — kept as three distinct SQLite tables so the breaks between them stay visible (Charter, Seat 10). `place_and_fill` requires a non-empty position rationale, prices costs exclusively through a `CostModel` (no field exists for a hand-rolled number), enforces `fill_ts` strictly after `order_ts` (the same-bar prohibition at the book level), and books average-cost realized P&L including shorts and cross-through-zero. `mark(prices)` raises on a held instrument with no mark — a missing price is escalated, not defaulted. `reconcile()` rebuilds positions and cash from the trade blotter, compares to running state, and **reports breaks without ever repairing them** — quiet correction is the failure mode the Ops seat exists to prevent.

## Not yet built (deliberate)

The scheduled-ritual glue (Morning Call / Close & Reconcile prompts that open the book, mark from the PITStore, and emit the daily pack), the attribution decomposition (beta/factor/idio) for the CRO seat, and Kalshi/Polymarket-specific loaders with resolution-rule metadata. All bolt onto the existing APIs without touching the enforcement core.

## Install

```
pip install -e .          # numpy, pandas, scipy, cryptography, pyarrow
pip install -e ".[data]"  # + yfinance, ccxt when you wire loaders
pytest tests/
```
