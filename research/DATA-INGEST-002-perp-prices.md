# DATA-INGEST-002 — perpetual OHLCV ingest (I-035)

**Seat:** Head of Data & Infrastructure
**Date:** 2026-07-29 (executed 2026-07-29T19:3x–19:4x UTC wall-clock)
**Follows:** `research/DATA-INGEST-001-crypto-etf.md` (funding rates only); `logs/ISSUE_LOG.md`
I-035 (perp price series absent); `research/PREREG-002-crypto-funding-basis.md` §15 step 1;
`logs/DECISION_RECORD.md` D-007 (definition of `C`), D-013 (I-035 named as one of three seal
predecessors, dispatched today).
**Scope:** `binanceusdm` perpetual daily OHLCV for BTC/USDT:USDT, ETH/USDT:USDT, SOL/USDT:USDT.
Nothing else touched.
**Not done:** no backtest run, no signal or return statistic computed, no hypothesis
pre-registered, no vault sealed, no schema migration run, nothing committed to git (CIO's, per
task instruction).

House rule 6: **[measured]** = read or executed this session · **[cited]** = named external/internal
source · **[inferred]** = reasoned from measured/cited facts · **[assumed]** = unverified premise.

---

## 1. THE CUTOFF INVARIANT — mechanism used, and why

Per D-007, `C` is the **pre-registration seal date**, and PREREG-002 **has not sealed**
[measured — `book/registry.db` `hypotheses` table has 0 rows]. Every `C` that can now be sealed is
on or after today, so the task bound was: ingest strictly no later than **`2026-07-29T23:59:59Z`**.

**Option 2 was used again — explicit end-bound per fetch, plus a post-ingest assertion on
`max(event_time)` — for the same reason DATA-INGEST-001 gave and which still holds
[measured, re-verified this session]:**

- `castellan.loaders.fetch_ccxt_ohlcv` still has **no `end` parameter** [measured —
  `harness/castellan/loaders.py:105-134`, unchanged since DATA-INGEST-001]. A custom
  bounded-pagination wrapper was written instead of adding one to the shared loader, matching the
  prior session's choice: this keeps an unreviewed code path out of `castellan.loaders` mid-task,
  and a genuinely useful `end`-bound feature belongs on the same Validation-reviewed cycle harness
  changes go through, not an ad hoc mid-ingest addition. **No loader addition was made; `loaders.py`
  is unmodified this session** [measured — `git diff --stat -- harness/` is empty].
- `set_holdout_ceiling` (Option 1) was **not probed or used again**. The prior session's finding —
  a ceiling created under a placeholder family/hash has no legitimate lift path, ceilings enforce
  conjunctively and never expire, and the only sanctioned lift (`HoldoutVault.acquire_once`)
  requires a spec hash that a placeholder can never match — was not re-litigated because nothing
  changed: PREREG-002 is still unsealed, no spec exists to derive a real hash from, and
  `ingest_ceiling` still has **0 rows** [measured, confirmed both before and after this session].
  **That judgment stands.**

**Mechanics.** `ex.fetch_ohlcv(symbol, "1d", since=cursor, limit=1000)` was paginated forward from
`2020-01-01T00:00:00Z`; every page was truncated to rows with `timestamp_ms <= CUTOFF_MS`
(`1785369599000`, i.e. `2026-07-29T23:59:59Z`) **before** calling `store.ingest`, and pagination
stopped once a page's own last raw timestamp reached or passed the bound. **After every symbol's
ingest**, `SELECT MIN(event_time), MAX(event_time), COUNT(*) FROM observations WHERE source=?
AND symbol=?` was run directly against `book/pit.db` and asserted `max(event_time) <=
2026-07-29T23:59:59Z`, hard-failing on violation. All three symbols passed; see §2.

**One thing worth naming plainly: the bound did no truncation work this time**, unlike
DATA-INGEST-001. Wall-clock at execution was `2026-07-29T19:38Z`, i.e. *before* the cutoff
(`2026-07-29T23:59:59Z`), because `C` is bounded conservatively into the future relative to today's
session. Every page fetched from the venue was already `<=` the bound; `"truncated": false` for
all three symbols in the run log. This does not weaken the control — the assertion still ran and
still would have caught a violation — it is reported because a bound that never fires is worth
distinguishing from one that is actively defending the store, and the next finding (§2.1) is a
direct consequence of it.

Suite re-run after ingest: **115/115, 0 failed** [measured] — matches the pre-ingest baseline
(Ruling 003's suite floor); this session touched no harness source.

---

## 2. Per-symbol results

All timestamps are `max(event_time)` in UTC, read directly from `book/pit.db`.

### Perpetual OHLCV (ccxt, `binanceusdm`, daily bars)

| Symbol | Span (event_time) | OHLCV rows (5 fields × days) | Distinct days | `max(event_time)` UTC | Pages used / ceiling | Truncated |
|---|---|---:|---:|---|---|---|
| BTC/USDT:USDT | 2020-01-01 → 2026-07-29 | 12,010 | 2,402 | `2026-07-29T00:00:00+00:00` | 3 / 200 | false [measured] |
| ETH/USDT:USDT | 2020-01-01 → 2026-07-29 | 12,010 | 2,402 | `2026-07-29T00:00:00+00:00` | 3 / 200 | false [measured] |
| SOL/USDT:USDT | 2020-09-14 → 2026-07-29 | 10,725 | 2,145 | `2026-07-29T00:00:00+00:00` | 3 / 200 | false [measured] |

SOL's perp OHLCV starts **2020-09-14**, one day after its first funding print
(`2020-09-13T16:00:00.004Z`, DATA-INGEST-001) — plausible: the contract must exist before it can
print funding, and a daily bar dated 2020-09-14 is consistent with the swap having listed partway
through 2020-09-13. Not a truncation artifact [measured — probed with `since=2020-01-01` and the
venue itself returned no earlier bars].

Cutoff assertion (`max(event_time) <= 2026-07-29T23:59:59Z`) **passed for all three symbols**
[measured].

**Zero restatement incidents** logged this session (`registry.events(kind="data_restatement")`
returns empty) — every row above was a first-time `new` insert. `volume` was ingested alongside
OHLC (same fields as the spot loader), which is the instrument PREREG-002 §6.1 names as arriving
with this step for the perp-leg capacity screen; present and confirmed [measured — `binanceusdm`
`volume` field, same span as `close` per symbol].

### 2.1 A flagged data-quality note: the final bar is a live, in-progress candle

**Not a defect, but worth stating rather than passing over.** The last bar in every series carries
`event_time = 2026-07-29T00:00:00Z`. Execution wall-clock was `2026-07-29T19:38Z` — **the UTC day
was not yet finished**, so this bar's `open` is settled but its `high`/`low`/`close`/`volume` are
provisional; the exchange will keep revising them until `2026-07-30T00:00Z`. This differs from
DATA-INGEST-001, whose wall-clock ran *after* midnight of the day following its cutoff, so its last
bar was always a closed day.

This is **within the cutoff bound** (`2026-07-29T00:00:00Z <= 2026-07-29T23:59:59Z`) and is not a
leak or a violation. It is also **exactly the case `PITStore.ingest`'s restatement mechanism is
built for** [measured — `data.py` design rule #2, "ingestion time is knowledge time... refreshes
then version any vendor restatements automatically"]: the next time anything re-fetches
`2026-07-29`'s bar after the day closes, the differing `close`/`high`/`low`/`volume` will insert as
a new version with a later `knowledge_time` and log a `data_restatement` event automatically. **No
action taken here** — flagged so a future single-row restatement on today's date is read as
expected housekeeping, not an incident. If a researcher wants to avoid the provisional bar
entirely, filtering `event_time < today` at query time is sufficient; nothing in this ingest depends
on it.

---

## 3. Data dictionary — new field

One row, extending the DATA-INGEST-001 table (unchanged there):

| Source | Symbol pattern | Field | `event_time` semantics | `knowledge_time` semantics | Update cadence | Known revision behaviour |
|---|---|---|---|---|---|---|
| `binanceusdm` | `{BASE}/USDT:USDT` | `open`,`high`,`low`,`close`,`volume` | UTC daily-bar open timestamp (00:00Z), built from ccxt's millisecond epoch via `parse_ccxt_ohlcv` — absolute, no local-time ambiguity (contrast I-020, which is a `yfinance`-only defect and does not touch this loader, re-confirmed this session: `parse_ccxt_ohlcv` is unchanged and untouched) | Backfill ingestion instant (this session, `~2026-07-29T19:3x-19:4xZ`) for every historical bar; the **final bar specifically carries a knowledge_time that predates the bar's own event day closing** — see §2.1, this is expected and self-correcting via the standard restatement path, not a defect of the two-timestamp rule | Daily; the venue never closes | Binance does not retroactively revise **closed** daily candles under normal operation; the **open/current** UTC-day candle is provisional by construction until the day rolls over — see §2.1 |

`funding_rate` (already dictionaried in DATA-INGEST-001) is unchanged by this session.

**I-020 re-verification, scoped to this loader specifically, per the task's instruction to verify
UTC handling for the ccxt path.** `parse_ccxt_ohlcv` builds `pd.to_datetime(ms, unit="ms")` from
epoch milliseconds, same as `parse_ccxt_funding` — absolute instants, no offset to strip or convert
incorrectly. `_iso()` then correctly localizes the naive result as UTC because it genuinely is UTC.
**Confirmed [measured]: every stored `event_time` for all three symbols lands exactly on a UTC
midnight boundary** (`...T00:00:00+00:00`), consistent with a correctly-converted daily bar and with
zero drift from the 8h-cadence funding series' own UTC alignment. I-020 does not apply to this
ingest — no `yfinance` series is involved.

---

## 4. The measured basis (perp vs. spot) — sanity check, not a signal

**Scope discipline, stated up front.** This is a **data-quality plausibility check**: joined,
descriptive statistics on stored prices, computed directly with pandas against `book/pit.db` — not
run through `castellan.run_backtest`, not registered as a trial, not a return series, not a Sharpe,
not a signal. It exists to answer one question honestly: *does the perp price series actually
diverge from spot in a way that looks like a real market, or did something silently collapse the
basis to zero* (the inadmissible shortcut the Director of Research named at PREREG-002 §8.1).

**`basis_bps(t) = 10,000 × (perp_close(t) − spot_close(t)) / spot_close(t)`**, joined on
overlapping `event_time`.

| Symbol | Overlap days | Mean basis (bps) | Std (bps) | Min (bps) | Max (bps) | % days > 0 |
|---|---:|---:|---:|---:|---:|---:|
| BTC | 2,401 | −1.58 | 5.48 | −73.65 | 31.09 | 26.7% |
| ETH | 2,401 | −0.95 | 6.47 | −102.95 | 36.08 | 31.2% |
| SOL | 2,144 | −3.18 | 38.68 | −1,690.34 | 70.94 | 26.2% |

**Plausibility read: passes, and passes for a specific, checkable reason.** [measured]

1. **The basis is non-zero, varies day to day, and has real dispersion.** A `perp ≈ spot`
   shortcut would produce `basis_bps ≡ 0`, every day, by construction. It does not. This is the
   direct falsification of the concern PREREG-002 §8.1 raised.
2. **The extreme dislocations land on named, dateable market-stress events, not on random days.**
   BTC's and ETH's largest absolute basis excursions (−73.65 bps, −102.95 bps) both fall on
   **2020-03-12** — "Black Thursday," the COVID crash and one of the most severe crypto
   liquidation cascades on record [cited — general market record]. SOL's largest excursion
   (−1,690.34 bps, i.e. −16.9%) falls on **2022-11-09** — the FTX collapse, which is exactly the
   kind of venue-stress event §9.1 (S2, venue survivorship) and §17 risk #4 of PREREG-002 already
   named as this family's structurally unmeasurable risk. **A perp/spot series that dislocates on
   the two most-cited crypto stress dates in the sample is strong evidence the two legs are
   independently and correctly priced, not an artifact.**
3. **Basis and funding move together, as the funding mechanism requires.** Correlation between
   daily basis and the day's summed funding print: **BTC 0.70, ETH 0.63, SOL 0.32** [measured].
   Mean basis is less negative on funding-positive days than funding-negative days for all three
   symbols (e.g. BTC: −1.07 bps vs. −5.16 bps). This is the correct sign and shape for Binance's
   documented funding formula (premium component + a fixed interest-rate offset), and it would not
   hold if perp and spot were the same series relabeled.
4. **Independent cross-check against a prior, separately-derived number.** Annualizing the mean
   daily funding computed from this session's join — **BTC 11.86%, ETH 14.07%, SOL 0.10%**
   [measured] — reproduces **exactly** the CIO's I-040 (N-6) figures, computed independently from
   `pit.db` in a different session for a different purpose (auditing the cost-preset sign error).
   Two independent computations landing on the same number to two decimal places is a real
   cross-check, not a coincidence worth dismissing.

**One honest tension, named rather than smoothed over.** Mean basis is **negative** for all three
symbols over the full sample (BTC −1.58, ETH −0.95, SOL −3.18 bps), while mean funding is
**positive and large** (11.86%, 14.07%, 0.10% annualized). These are not contradictory once
Binance's funding formula is accounted for — funding = a premium/basis component **plus a fixed
interest-rate offset** (documented baseline ~0.01%/8h independent of the realized basis), so
funding can run persistently positive even while the basis it is partly derived from averages
slightly negative [inferred — not verified against Binance's published funding-formula
documentation this session, since that is outside this task's scope and not required to answer
the plausibility question asked]. **Flagged for whoever runs PREREG-002's mechanism work**, because
the family's central claim (§3.4) is that funding is a direct observable of positioning crowding —
if funding and basis structurally diverge by a fixed offset rather than moving together one-for-one,
that is relevant to how cleanly "funding rich" maps to "basis rich," and it is a modelling question
for Validation/Director, not a data defect for this seat to resolve.

**What this section is not.** No t-statistic, no Sharpe, no threshold, no pass/fail verdict, and no
number here is a candidate for a Gate 0 or Gate 1 artifact. It answers "is the data plausible,"
nothing more.

---

## 5. Restatement incidents, gaps, outages

- **Restatement incidents this session: zero** [measured — `registry.events(kind="data_restatement")`
  before and after this session both return the empty set for this ingest; every row inserted was
  `new`].
- **Gaps:** none found. Distinct-day counts (2,402 for BTC/ETH, 2,145 for SOL) are continuous
  from each symbol's start date to 2026-07-29 with no calendar-day scan gaps [measured, same method
  as DATA-INGEST-001 §2].
- **Outages / rate limits:** none. `load_markets()` succeeded on first attempt; all three symbols'
  paginated fetches completed in **3 of 200 pages** — nowhere near exhaustion. No retry was needed.
- **The one flagged item is §2.1** (the live in-progress final bar) — not an outage, not a gap, not
  a restatement; a structurally expected characteristic of ingesting on the same UTC day the cutoff
  permits through to its own end.

---

## 6. What was not ingested, and why

- **Perpetual OHLCV for any symbol beyond BTC/ETH/SOL.** Not requested; matches the three-asset
  universe DATA-INGEST-001 and PREREG-002 already use.
- **Any timeframe other than `1d`.** Daily bars only, matching the spot and funding series already
  on disk and PREREG-002 §6.2's declared bar granularity (K6). Intraday is explicitly named in
  PREREG-002 §16.1 as the successor family's data requirement, not this one's.
- **Any venue other than `binanceusdm`.** Task-scoped to `binanceusdm` via ccxt only; no other
  venue was touched.
- **A `loaders.py` change adding an `end` parameter to `fetch_ccxt_ohlcv`.** Judged not needed —
  see §1. Flagged as a reasonable, low-risk follow-on for whoever next runs a bounded ccxt ingest,
  but not made here.
- **`set_holdout_ceiling`.** Not called. See §1 — the prior session's reasoning stands unchanged.
- **Any backtest, signal, correlation used as a trading input, or registry write.** Per task
  instruction. §4's basis statistics are descriptive QC, not inputs to any of these.

---

## 7. Ceiling state and registry touch, for the record

- `book/pit.db :: ingest_ceiling` — **0 rows before this session, 0 rows after** [measured].
- `book/registry.db` — opened via `TrialRegistry(REGISTRY_DB)` **only** so that `PITStore` could
  auto-log any restatement incident (none occurred, §5). `TrialRegistry.__init__` calls its own
  `_migrate()` automatically, same as `PITStore.__init__`; verified **before** connecting that
  `hypotheses.n_inherited` already exists [measured — I-041's disposition, already committed], so
  this session's connection made **zero schema changes** — confirmed by `PRAGMA table_info` showing
  the same column set before and after, and by `hypotheses`/`trials` row counts unchanged (0 and 0).
  **No migration was run by this session; the automatic no-op inside a library constructor is the
  "PITStore does incidentally" case the task scoped in, not a schema change this seat performed.**

---

## 8. Summary for the CIO

| Symbol | OHLCV rows | Distinct days | Span | `max(event_time)` UTC |
|---|---:|---:|---|---|
| BTC/USDT:USDT | 12,010 | 2,402 | 2020-01-01 → 2026-07-29 | `2026-07-29T00:00:00+00:00` |
| ETH/USDT:USDT | 12,010 | 2,402 | 2020-01-01 → 2026-07-29 | `2026-07-29T00:00:00+00:00` |
| SOL/USDT:USDT | 10,725 | 2,145 | 2020-09-14 → 2026-07-29 | `2026-07-29T00:00:00+00:00` |

**Cutoff mechanism:** Option 2 (explicit end-bound per fetch + post-ingest `max(event_time)`
assertion), same as DATA-INGEST-001 and for the same reasons. `set_holdout_ceiling` (Option 1)
again judged unsafe and not used — PREREG-002 remains unsealed, no spec hash exists, nothing
changed since the prior finding. `ingest_ceiling` has zero rows before and after.

**Basis plausibility: passes.** Non-zero, correctly dispersed, dislocates on named historical
stress dates (2020-03-12 Black Thursday, 2022-11-09 FTX), correlates positively with funding
(0.32–0.70), and an independent annualized-funding cross-check reproduces I-040's figures exactly.
One open modelling question flagged for Validation/Director: mean basis is slightly negative while
mean funding is strongly positive, plausibly reconciled by a fixed interest-rate offset in
Binance's funding formula, not verified against vendor documentation this session.

**Gaps: none.** **Outages: none.** **Restatements: zero this session.**

**What surprised this seat:** the cutoff bound did no truncation work this time (§1, §2) — because
`C`'s conservative future-dated bound put the ceiling *after* today's close rather than before it,
every fetched row was already inside the bound, unlike DATA-INGEST-001 where wall-clock had run
past midnight and truncation was real. The consequence worth flagging is §2.1: the final ingested
bar for all three symbols is today's still-open, not-yet-closed daily candle — inside the cutoff,
not a leak, but a provisional value that will restate itself the first time anything re-ingests
this symbol after 2026-07-30T00:00Z. Also notable: the SOL basis excursion on the FTX date
(−16.9%) is an order of magnitude larger than anything BTC/ETH show anywhere in the sample — a
concrete, dated illustration of PREREG-002 §9.1's point that SOL's cross-section is thinner and
its tail risk larger, worth carrying into whatever reads this data next.
