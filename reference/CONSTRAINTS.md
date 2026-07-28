# Castellan Capital — Constraints

*Extracted from `FUND_CHARTER.md` Part III. The Charter governs where they differ. Validation gates: `GATES.md`. Limits: `RISK.md`.*

## PART III — CONSTRAINTS: WHAT THIS FIRM ACTUALLY HAS

A professional firm knows its own constraints precisely and designs around them. Pretending to capabilities it lacks is the fastest route to confident garbage. These constraints are binding and must be restated in any report where they materially limit the conclusion.

### 3.1 Capital

- **No real capital is deployed under any circumstances without the Principal's explicit written approval (Gate 2).**
- The firm operates a **paper book of USD 10,000,000 notional**, marked to real prices, charged real modelled costs, and subject to the full risk framework.
- Initial trading levels: **USD 2,000,000 per pod**, **USD 4,000,000 held in unallocated reserve** by the CIO for reallocation and for new-strategy ramps.
- Paper P&L is tracked, attributed, and reported exactly as if real. The discipline is the point.

### 3.2 Data — what is available

| Source | Covers | Cost | Notes |
|---|---|---|---|
| Yahoo Finance / `yfinance` | Equity & ETF OHLCV, daily and intraday-limited | Free | Split/dividend adjusted **retroactively** — a live look-ahead hazard |
| SEC EDGAR | Filings, 8-K/10-K/10-Q, insider, institutional holdings | Free | Genuinely point-in-time by filing date. The best PIT surface available |
| FRED | Macro series, rates, spreads | Free | Watch revision vintages — ALFRED has vintages, FRED does not |
| Public crypto exchange APIs (`ccxt`, Binance, Coinbase, Bybit) | Spot, perps, funding rates, order book | Free | Deep minute-level history. Best data surface the firm has |
| Polymarket / Kalshi public APIs | Event-contract prices, volume, order book | Free | Thin history; heterogeneous contracts; resolution rules matter enormously |
| Public web via search/fetch | News, filings, research | Free | Not usable as a systematic backtest input |

### 3.3 Data — what is NOT available, and what that forecloses

These are hard walls. Any strategy that requires crossing one is **inadmissible at Gate 0** and must be rejected at intake rather than discovered to be impossible three weeks later.

- **No point-in-time fundamentals.** No Compustat PIT, no Capital IQ PIT. Vendor-restated financials are the only fundamentals available, and roughly 78% of companies restate audited annual revenue at least once within 400 days [cited — S&P Global Market Intelligence, *PIT vs. Lagged Fundamentals*]. **Consequence: cross-sectional fundamental factor strategies on equities cannot be validated to this firm's standard.** They may be researched and discussed; they may not pass Gate 1. Say this out loud when the topic arises rather than producing a backtest whose number is meaningless.
- **No survivorship-free equity universe.** Delisted tickers are largely absent from free sources. Any equity universe study must either (a) restrict itself to a currently-constituted, explicitly-acknowledged-as-biased universe with the bias quantified, or (b) use ETFs and indices where the survivorship problem is embedded in the instrument rather than in the researcher's universe construction.
- **No tick data, no order-book history for equities.** Minimum equity holding period is **one trading day**. No intraday, no market-making, no latency-sensitive strategies.
- **No borrow-availability or borrow-cost data.** Short equity strategies must assume specials at ≥4%/yr, hard-to-borrow names excluded, and must run the constraint sensitivity. Applying real borrow constraints has been documented to cut a live model's cumulative performance by roughly half [cited — Deutsche Bank, *Seven Sins of Quantitative Investing*].
- **No paid news, transcripts, or alternative data.**
- **No brokerage connectivity.** The firm cannot transmit an order anywhere. Execution is simulated.
- **No MNPI. No scraping of authenticated sources.** Logged-off public data only.

### 3.4 Operational constraints

- **Sessions are ephemeral.** The working environment is reclaimed. Anything that must survive the session goes to Oracle memory or to a delivered file — see Part VIII.
- **Compute is finite and is the firm's real scarce resource.** Every seat spends it. Fable 5 allocates it and is accountable for the allocation.
- **Wall-clock scheduling exists** via recurring scheduled tasks, which start fresh sessions with no memory of prior ones. Every scheduled meeting prompt must therefore be self-contained and must begin by recalling state from Oracle.
- **No seat runs continuously.** The firm exists when invoked. "Since the last session" is the correct unit of elapsed time in every report, never "since yesterday" unless verified.

### 3.5 The honest framing to hold

This firm's genuine comparative advantage is **not** data, speed, or capital. It is **research discipline applied to markets where free public data is genuinely adequate** — crypto funding and basis, prediction-market microstructure, ETF-level macro and calendar effects, and event-driven equity work keyed to EDGAR filing timestamps. Those four are where the firm should spend most of its compute, and any research agenda that drifts away from them without an explicit reason should be challenged by the Devil's Advocate.

---
