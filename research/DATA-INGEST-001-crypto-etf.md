# DATA-INGEST-001 — crypto and ETF panel ingest to cutoff

**Seat:** Head of Data & Infrastructure
**Date:** 2026-07-28 (executed 2026-07-28T21:4x UTC – 2026-07-29T01:46 UTC wall-clock)
**Follows:** `research/DATA-IMPL-002-acceptance-remediation.md` (Acceptance 001 conditions C-1…C-10
cleared, suite 96/96, ingest unblocked automatically per Acceptance 001's own terms).
**Scope:** ccxt crypto OHLCV + perpetual funding; yfinance ETF panel (`auto_adjust=False`, raw +
corporate actions as separate observations). **Polymarket not ingested** — blocked separately on
Validation accepting `DATA-SPEC-polymarket-usable-history.md`, not attempted here.
**Not done:** no backtest run, no hypothesis pre-registered, no vault sealed, nothing committed to
git (CIO's, per I-013).

---

## 1. THE CUTOFF INVARIANT — mechanism used, and why

Per D-007 (Principal, on the record): `C` is the **pre-registration seal date**, not the D-006
decision date, and Pod B has not sealed. **`C` is therefore not yet fixed and will be a date on or
after 2026-07-28.** The task bound: ingest strictly no later than **`2026-07-28T23:59:59Z`**.

### 1.1 Option 1 (`set_holdout_ceiling` as a provisional pre-fetch bound) — probed, not used

I read `PITStore.set_holdout_ceiling` / `_enforce_holdout_ceiling_on_index` / `_lift_ceiling`
(`harness/castellan/data.py`) and ran three probes against an **isolated throwaway store** (not
`book/pit.db`) before touching real data, specifically to answer "is this mechanism usable without a
sealed spec, and is it safe":

1. `store.set_holdout_ceiling("binance", "BTC/USDT", "PROVISIONAL-INGEST-CUTOFF", <cutoff>, "PROVISIONAL-NO-SEALED-SPEC")`
   **succeeded.** The method performs no check that `family` exists in `TrialRegistry` and no check
   that `spec_sha256` corresponds to any real sealed `HoldoutVault` spec — it is a bare INSERT keyed
   on `(source, dataset_id, family)`. **[measured]**
2. A second `set_holdout_ceiling` call for the same `(source, dataset_id)` under a **different**
   family name (simulating Pod B's real future seal, e.g. `"pod-b-forward-lag-v1"`) also
   **succeeded** — ceilings for the same dataset do not collide across families; `_active_ceilings`
   returns and enforces the **conjunction** of every active row. **[measured]**
3. `_lift_ceiling(..., spec_sha256="WRONG-HASH")` was refused (`HoldoutCeilingError`); only the
   **exact** hash supplied at creation lifts it. `_lift_ceiling` is a private method, called from
   nowhere but `HoldoutVault.acquire_once()` after that vault independently verifies its own sealed
   spec hash. **[measured]**

**Conclusion: Option 1 is mechanically callable pre-seal, but I judged it unsafe for this task and
did not use it against the real store.** Reasoning:

- A provisional ceiling created under a placeholder family/hash has **no legitimate path back**. The
  only sanctioned lift path (`HoldoutVault.acquire_once`) requires a `spec_sha256` computed from a
  real sealed spec's canonical JSON — a placeholder hash will never match one, by construction. The
  only way to remove it is to call the private `_lift_ceiling` directly with the exact placeholder I
  chose, which is exactly the kind of untracked, non-audited mutation this control exists to prevent,
  and which nothing else in the codebase does.
- Because ceilings enforce conjunctively and never expire, a ceiling dated 2026-07-28 left active
  would **permanently block all future ingestion** of newer bars for `(binance, BTC/USDT)` etc. —
  including completely routine, non-holdout-related daily updates — from the day after this session
  onward, until someone who remembers the placeholder hash deliberately reverses it. That is a
  standing operational hazard the task did not ask me to create, and probe (2) shows it would not
  even be superseded automatically once Pod B seals for real: the two ceilings coexist and both bind.
- The task's own framing — "a ceiling is derived from a sealed spec and no spec is sealed" — is
  correct as a description of the *intended* use of `set_holdout_ceiling` (it is called from exactly
  one place, `HoldoutVault.seal()`, §5 of `holdout.py`); the fact that the method itself does not
  enforce that intent is a gap in the mechanism's design, not a green light to route around the
  intent. I am reporting this as the finding the task asked for, not treating it as a footnote: **the
  firm has an ingest ceiling that can be created by anyone with a `PITStore` handle and a string,
  entirely outside the sealed-vault path it was built to be paired with.** No harness code was
  changed to close it — that is a design question for Validation/CIO, and outside this task's
  instruction not to touch harness internals mid-ingest.

`book/pit.db`'s `ingest_ceiling` table has **zero rows** after this session (confirmed by direct
query) — no ceiling of any kind exists on any of the fourteen datasets ingested.

### 1.2 Option 2 (used) — explicit end-bound + post-ingest assertion

Every fetch call was bounded with an **explicit end parameter**:

- ccxt: a custom bounded-pagination wrapper (not the stock `fetch_ccxt_ohlcv`/`fetch_ccxt_funding`,
  neither of which accepts an end bound) truncates every page to rows with
  `timestamp_ms <= CUTOFF_MS` **before** calling `store.ingest`, and stops paginating once a page's
  last timestamp reaches or passes the bound.
- yfinance: `fetch_yfinance(..., end="2026-07-29")` (yfinance's `end` is the exclusive upper date,
  so this covers exactly through 2026-07-28 local trading).

**After every dataset's ingest**, I ran `SELECT MAX(event_time) FROM observations WHERE source=? AND
symbol=?` against `book/pit.db` and asserted it `<= 2026-07-28T23:59:59Z`, hard-failing the run on
violation. All fourteen datasets passed; see the per-dataset table in §2 for the measured
`max(event_time)`. The `"truncated": true` flags in the run log (§2) reflect this bound doing its
job — wall-clock at execution was `2026-07-29T01:46Z`, i.e. after the cutoff, so the final page of
every ccxt fetch legitimately contained rows past the bound that were dropped before ingest, not a
rate-limit or outage artifact. Confirmed by page counts (3–8 pages used against a 200-page ceiling —
nowhere near exhaustion).

**Suite re-run after ingest: 96/96, 0 failed, 0 skipped, 0 xfail** — ingest did not touch harness
code and the suite is unaffected.

---

## 2. Per-dataset results

All timestamps below are `max(event_time)` in UTC, read directly from `book/pit.db`, proving the
cutoff bound. Row counts are `observations` rows (wide frames unpack to one row per `(event_time,
field)`, so a daily OHLCV bar is 5 rows).

### Crypto — spot OHLCV (ccxt, `binance`, daily bars)

| Symbol | Span (event_time) | Rows | max(event_time) UTC | Gaps > 4 calendar days |
|---|---|---|---|---|
| BTC/USDT | 2020-01-01 → 2026-07-28 | 12,005 | `2026-07-28T00:00:00+00:00` | 0 [measured] |
| ETH/USDT | 2020-01-01 → 2026-07-28 | 12,005 | `2026-07-28T00:00:00+00:00` | 0 [measured] |
| SOL/USDT | 2020-08-11 → 2026-07-28 | 10,890 | `2026-07-28T00:00:00+00:00` | 0 [measured] |

SOL's start (2020-08-11) reflects its Binance spot listing date, not truncation. 2,401 distinct
trading days for BTC/ETH (2,178 for SOL) — daily coverage is complete, no missing calendar days
found by a diff-based scan of distinct `event_time` values.

### Crypto — perpetual funding-rate history (ccxt, `binanceusdm`, 8h cadence)

| Symbol | Span (event_time) | Rows | max(event_time) UTC | Gaps > 1 day |
|---|---|---|---|---|
| BTC/USDT:USDT | 2020-01-01 → 2026-07-28 16:00 | 7,203 | `2026-07-28T16:00:00+00:00` | 0 [measured] |
| ETH/USDT:USDT | 2020-01-01 → 2026-07-28 16:00 | 7,203 | `2026-07-28T16:00:00+00:00` | 0 [measured] |
| SOL/USDT:USDT | 2020-09-13 16:00 → 2026-07-28 16:00 | 6,508 | `2026-07-28T16:00:00+00:00` | 0 [measured] |

Funding posts every 8h (00:00 / 08:00 / 16:00 UTC); the day's last available funding print by the
time of this run was the 16:00 UTC print, correctly under the 23:59:59Z bound.

### ETF panel (yfinance, `auto_adjust=False`, daily bars + corporate actions as separate observations)

| Symbol | Close span | Trading-day rows (close) | Splits | Dividends | max(event_time) UTC |
|---|---|---|---|---|---|
| SPY | 1993-01-29 → 2026-07-28 | 8,430 | 0 | 135 | `2026-07-28T00:00:00+00:00` |
| QQQ | 1999-03-10 → 2026-07-28 | 6,888 | 1 | 89 | `2026-07-28T00:00:00+00:00` |
| IWM | 2000-05-26 → 2026-07-28 | 6,580 | 1 | 106 | `2026-07-28T00:00:00+00:00` |
| TLT | 2002-07-30 → 2026-07-28 | 6,037 | 0 | 286 | `2026-07-28T00:00:00+00:00` |
| IEF | 2002-07-30 → 2026-07-28 | 6,037 | 0 | 288 | `2026-07-28T00:00:00+00:00` |
| GLD | 2004-11-18 → 2026-07-28 | 5,455 | 0 | 0 | `2026-07-28T00:00:00+00:00` |
| HYG | 2007-04-11 → 2026-07-28 | 4,855 | 0 | 230 | `2026-07-28T00:00:00+00:00` |
| UUP | 2007-03-01 → 2026-07-28 | 4,883 | 0 | 9 | `2026-07-28T00:00:00+00:00` |

No gaps exceeding 10 calendar days found in any close series (weekend/holiday gaps are the only
gaps present) [measured]. Panel spans equities (SPY, QQQ, IWM), rates (TLT, IEF), commodities (GLD),
credit (HYG), and USD (UUP) — chosen for cross-asset macro coverage per Charter §3.5's stated
comparative advantage, not prescribed by the task; a narrower or wider panel is a straightforward
follow-on.

**Zero restatement incidents** were auto-logged by `PITStore` this session (`registry.events(kind="data_restatement")` returns empty) — expected, since every row above is a first-time `new` insert, none `unchanged`/`restated`. Restatement logging is exercised by the harness test suite (`test_ACC_C5_*` etc.), not by this ingest.

---

## 3. Data dictionary

Every field below carries both timestamps per the two-timestamp rule. `knowledge_time` for this
session's backfill is honestly the **ingestion moment** (2026-07-28T21:4x–2026-07-29T01:46 UTC wall
clock) for every row, per `loaders.py`'s own documented design ("Ingestion time is knowledge time...
the store cannot pretend the firm knew a bar before it first fetched it"). This means: a backtest
run today can legitimately use any `event_time <= knowledge_time`, but a **simulated point-in-time
reconstruction of "what was knowable on 2022-06-01"** using this backfill would be wrong — every row
back to 2020 has `knowledge_time ≈ 2026-07-28`, not the date it actually printed. This is not a
defect of this ingest; it is the standing, documented limitation of any historical backfill, and
matters if a family ever wants to claim it tested PIT knowledge for dates before this session.

| Source | Symbol pattern | Field | `event_time` semantics | `knowledge_time` semantics | Update cadence | Known revision behaviour |
|---|---|---|---|---|---|---|
| `binance` | `{BASE}/USDT` | `open`,`high`,`low`,`close` | UTC daily-bar open timestamp (00:00Z), the bar's own date | Backfill ingestion instant (this session); live re-runs would set it to fetch time | Daily; exchange never closes | Binance does not retroactively revise closed daily candles under normal operation; a store-level `restated` count would flag it if it ever does |
| `binance` | `{BASE}/USDT` | `volume` | Same as OHLC, base-asset volume for the UTC day | same | Daily | same |
| `binanceusdm` | `{BASE}/USDT:USDT` | `funding_rate` | The funding print's own timestamp (00:00/08:00/16:00 UTC) — when the rate became true | Backfill ingestion instant | Every 8h | Historical funding prints are not revised; each print is final at settlement |
| `yfinance` | ticker | `open`,`high`,`low`,`close` | **See §4 — measured defect.** Nominally the trading day's date; stored value currently reflects the exchange-local wall-clock reading re-labelled UTC, not a true UTC-converted instant (I-020) | Backfill ingestion instant | Daily | **Retroactive vendor re-adjustment is the documented hazard this store is built to defend against** (Charter §3.2/4.6) — raw OHLCV is fetched `auto_adjust=False` specifically so this field is never itself adjusted; adjustment happens only in `pit_adjusted_close`, computed from the separate `split`/`dividend` observations below, as-of a decision time |
| `yfinance` | ticker | `volume` | Same as OHLC | same | Daily | Not vendor-adjusted |
| `yfinance` | ticker | `split` | The split's ex-date; ratio (e.g. `4.0` = 4-for-1), stored as its own point-in-time observation, never merged into `close` | Backfill ingestion instant — i.e., this session is the first moment the firm "knew" any of these splits, honestly | Irregular, corporate-action-driven | A vendor correction to a historical split ratio would show as a `restated` row, logged as a `data_restatement` incident |
| `yfinance` | ticker | `dividend` | The dividend's ex-date; cash amount per share | Backfill ingestion instant | Irregular | same restatement handling |

`pit_adjusted_close(store, "yfinance", symbol, decision_time)` is the only sanctioned way to consume
an adjusted series — it reconstructs the back-adjustment from `close` + `split` + `dividend` using
only actions with `event_time <= decision_time`, per Amendment A4. Nothing in this ingest calls it;
that is Gate 0/Gate 1 research's job, not ingestion's.

---

## 4. I-016 verification, and a new finding (I-020)

Instructed to verify the I-016/C-5 UTC-normalization fix holds for **both** loaders, including venues
reporting in local time or milliseconds since epoch. Result: **it holds for `ccxt`, not for
`yfinance`.** Filed as **`logs/ISSUE_LOG.md` I-020**, Severity MEDIUM, owner head-of-data-infra — full
detail there; summary:

- **ccxt (correct) [measured].** `parse_ccxt_ohlcv`/`parse_ccxt_funding` build timestamps from
  milliseconds-since-epoch via `pd.to_datetime(ms, unit="ms")`. Epoch milliseconds are absolute —
  there is no local-time ambiguity to get wrong. `PITStore._iso()` then correctly treats the naive
  result as UTC because it genuinely is UTC.
- **yfinance (defective) [measured].** `Ticker(...).history(...)` returns timestamps **tz-aware in
  the instrument's exchange-local zone** (confirmed: `SPY` → `America/New_York`, values at local
  midnight, e.g. `2024-06-25 00:00:00-04:00`). `parse_yfinance_history` calls
  `hist.index.tz_localize(None)`, which **strips the offset without converting** — the wall-clock
  reading survives, the `-04:00` is discarded, rather than calling `tz_convert("UTC")` first. `_iso()`
  then (correctly, per its own contract) treats that now-naive value as already UTC. Measured
  round-trip: a bar whose true UTC instant is `2024-06-25T04:00:00Z` is stored as
  `2024-06-25T00:00:00+00:00`.
- **Why this ingest is not compromised.** All eight ETF symbols are US-domiciled (UTC−4/−5); the
  error only shifts the stored instant *earlier* within the same UTC calendar date, never across a
  day boundary, so every `max(event_time)` reported in §2 is still a truthful bound and no row in
  this session's data crosses `2026-07-28T23:59:59Z` under either the buggy or the corrected
  timestamp.
- **Why it is logged rather than silently worked around:** the error is instrument-domicile-dependent
  and would relabel a bar onto the **wrong UTC calendar date** for an exchange sufficiently east of
  UTC (a future non-US ETF/equity addition), which is exactly the day-granularity comparison both P7
  and the D2 ingest ceiling rely on. Not patched in this session — out of scope for an ingest task,
  and harness source changes go through the same Validation-reviewed cycle C-5 itself just went
  through, not an ad hoc mid-ingest edit.

---

## 5. What was not ingested, and why

- **Polymarket / any prediction-market venue.** Explicitly out of scope this task — blocked on
  Validation accepting `research/DATA-SPEC-polymarket-usable-history.md`, which has not been
  reviewed. Not touched, not fetched, not probed.
- **SEC EDGAR.** Not requested by this task's priority order (crypto, then ETF); the loader
  (`fetch_edgar_filings`) exists and is untouched this session.
- **FRED / macro series.** Not requested; no loader for it exists in `harness/castellan/loaders.py`
  yet.
- **Other crypto venues (Coinbase, Bybit, Kraken, etc.).** Only `binance`/`binanceusdm` were used.
  Charter §3.2 lists ccxt/Binance/Coinbase/Bybit as available; I did not cross-venue-verify pricing or
  diversify venue risk in this pass — a single-venue backfill is a scope choice, not a failure, but
  it means this panel currently has no cross-exchange basis check and no resilience if Binance-specific
  symbol or listing quirks are present. Flagging rather than silently assuming it's representative.
- **Wider crypto/ETF universe.** Three crypto majors (BTC, ETH, SOL) and eight ETFs were chosen for
  cross-asset breadth within a reasonable first pass; no altcoins, no sector/factor ETFs, no
  international equity ETFs, no intraday bars. Extending either panel is straightforward given the
  same bounded-pagination pattern.
- **Intraday granularity.** Daily bars only (`1d`/`1day`). Charter §3.3 already forecloses
  latency-sensitive strategies on the equity side; crypto intraday was not requested and not fetched.

## 6. Outages / rate limits

None encountered. `binance` and `binanceusdm` `load_markets()` succeeded on first attempt; every
paginated fetch completed in 3–8 pages against a 200-page per-dataset ceiling (no exhaustion);
`yfinance` returned non-empty history for all eight tickers on the first request. The only
"truncation" observed (`"truncated": true` in the run log) is the cutoff bound doing its job against
data past `2026-07-28T23:59:59Z` — not a vendor-side failure. Recorded honestly rather than rounded
away.

---

## 7. Ceiling state, for the record

`book/pit.db :: ingest_ceiling` has **zero rows** after this session. No provisional, no partial, no
orphaned ceiling of any kind was left on any of the fourteen `(source, symbol)` pairs ingested. Pod
B's eventual seal is free to call `set_holdout_ceiling` on any of them without collision.

---

*Head of Data & Infrastructure · Castellan Capital · 2026-07-28*
