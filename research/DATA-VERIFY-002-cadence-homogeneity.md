# DATA-VERIFY-002 — BTC/ETH funding cadence homogeneity across PREREG-002's sample

**Seat:** Head of Data & Infrastructure (Seat 9) · **Date:** 2026-08-04
**Dispatch:** S2-D-006 · **Blocks:** C12 (`DIR-RESTATE-001-prereg002-mechanism.md` §6), the K7 seal condition in `PREREG-002` R-001
**Compute:** fraction of 1 Sonnet unit · **Trial budget: ZERO.** This is a row-count query, not a trial. No hypothesis opened, no registry write, no `run_backtest` call, no `book/registry.db` or `book/book.db` touch.

House rule 6: **[measured]** = executed against this repository this session · **[cited]** = named external/internal source · **[inferred]** = reasoned from measured/cited facts.

---

## 1. What was asked, and why it is not the same question I-045 answered

I-045's control measured BTC only, in one direction (`>3 prints/day`), as a check on the SOL break dated 2022-11-09. `DIR-RESTATE-001` §6 (C12) is explicit that K7 — the new conditioning choice governing documented funding-parameter changes on universe symbols — rests on an **unverified premise**: that BTC and ETH are cadence-homogeneous across the sample. This dispatch measures that premise directly, on both symbols, in both directions (`>3` and `<3` prints/day), across PREREG-002's full available sample.

## 2. Method and the sanctioned read path

**Read path used** [measured]: `castellan.data.PITStore.asof(source, symbol, decision_time, fields=["funding_rate"])`, imported from `harness/castellan/data.py`. This is the same PIT accessor `pit_funding_panel` builds on (Amendment A4 / `VALIDATION-RULING-003` §3.2) — it enforces `knowledge_time ≤ decision_time` and returns the latest version of each `(event_time, field)`, which correctly collapses any restated print to its current value rather than double-counting versions. `decision_time` was set to `2026-08-04T23:59:59Z` (today), i.e. "everything currently knowable," since PREREG-002 is unsealed and `C` has not been fixed — this measurement therefore covers the full available store, a superset of any `C` the family will eventually seal at.

No price data was read, no return was computed, no signal was built. The operation is `SELECT`/`asof` plus a `groupby` on calendar date — the identical class of operation as I-045's own measurement and PREREG-002 §0's diagnostics, both of which the Director's own document treats as non-trials.

**Symbols measured:** `binanceusdm` / `BTC/USDT:USDT` and `binanceusdm` / `ETH/USDT:USDT` — the two members of PREREG-002's primary (and, post-R3, only) universe. SOL was not re-measured; I-045 and `VALIDATION-RULING-003` §A2 already cover it and R3 has dropped it from the universe.

**Sample span used:** the full ingested history for both symbols, `2020-01-01T00:00:00Z` → `2026-07-28T16:00:00Z` [measured — identical bounds for BTC and ETH]. This matches PREREG-002 §0's stated span exactly; no funding data has been ingested for either symbol since the document was drafted (max `knowledge_time` unchanged, no new rows).

**Ingest-continuity cross-check, done before counting anything a deviation.** Confirmed [measured]: for each symbol, 7,203 total observation rows = 7,203 distinct `event_time` values (no restated field/event_time pairs for funding on either symbol), inserted in a single ingest session (8 `knowledge_time` batches spanning ~3 seconds each, consistent with a paginated fetch, not a resumed or partial capture). This rules out the class of hazard I-047/I-048 named for the Polymarket laptop capture (DNS failures on a continuously-polling script) — BTC/ETH funding was a one-shot historical `ccxt` pull, not an intermittent poller, so there is no analogous "not polled vs. polled-and-failed" ambiguity to resolve here.

## 3. Per-symbol day counts

| Symbol | Total calendar days in span | Total funding prints | Days with exactly 3 prints | Days with >3 prints | Days with <3 prints |
|---|---:|---:|---:|---:|---:|
| BTC/USDT:USDT | **2,401** [measured] | **7,203** [measured] | **2,401** [measured] | **0** [measured] | **0** [measured] |
| ETH/USDT:USDT | **2,401** [measured] | **7,203** [measured] | **2,401** [measured] | **0** [measured] | **0** [measured] |

`2,401 × 3 = 7,203` for both symbols, exactly — every single calendar day in the full span carries exactly three funding prints, no more, no fewer. Calendar span was independently confirmed gap-free: `(max_date − min_date) + 1 = 2,401` days, matching the observed day count exactly, so no calendar day is silently absent from the store either.

## 4. Deviating days

**None. Zero deviating days on either symbol, in either direction, across 2,401 days each (4,802 symbol-days measured).**

Specific dates checked by name, because the dispatch asks whether any deviation clusters the way SOL's did:

| Date | Reason checked | BTC prints | ETH prints |
|---|---|---:|---:|
| 2022-11-08 | day before SOL's break | 3 | 3 |
| **2022-11-09** | **SOL's break date** [cited — official, `DATA-VERIFY-001` §3.2] | 3 | 3 |
| 2022-11-10 | SOL's peak-stress day (12 prints on SOL) | 3 | 3 |
| 2022-11-15 | inside SOL's elevated-cadence window | 3 | 3 |
| 2022-12-01 | SOL's measured cadence revert date | 3 | 3 |
| 2025-09-17 | day before the firm-wide formula change | 3 | 3 |
| **2025-09-18** | **firm-wide `/(8/N)` divisor change** [cited — official, `DATA-VERIFY-001` §3.1] — K7's one named in-sample trigger per `DIR-RESTATE-001` §3.4(d2) | 3 | 3 |
| 2025-09-19 | day after the formula change | 3 | 3 |
| 2020-03-12 | primary universe's largest measured basis excursion date | 3 | 3 |

The full 2,401-day series was checked, not just these nine dates (§3 table above is exhaustive: the "3 prints" bucket contains all 2,401 days for both symbols with no residual). These nine are surfaced because they are the dates the firm's own record already treats as structurally interesting.

## 5. Genuine-change / missing-data / undetermined split

**Vacuous.** There are no deviating days to sort into categories. The genuine/missing/undetermined split required by the dispatch is:

| Category | Count | Reasoning |
|---|---:|---|
| Genuine cadence change | **0** | No day departs from 3 prints/day on either symbol. |
| Missing data (our ingest) | **0** | Same. Independently, the ingest-continuity check (§2) found no restatements, no partial batches, and a calendar span with zero missing days — so even if a deviation had been found, the store shows no structural reason to suspect it as an artifact. |
| Undetermined | **0** | No case required this bucket. |

This is the honest form of the answer, not a rounding of a small nonzero count to zero — the raw `value_counts()` of prints-per-day, computed once per symbol over the full 2,401-day index, returns a single bucket: `{3: 2401}`, for both BTC and ETH.

## 6. Verdict

**BTC + ETH are cadence-homogeneous across PREREG-002's full available sample — YES, measured, not asserted.** [measured] Both symbols carry exactly three funding prints per calendar day, every day, from 2020-01-01 through 2026-07-28, with no departure in either direction, including at both dates the firm's record already flags as structurally live (SOL's 2022-11-09 break and the 2025-09-18 firm-wide formula change). Nothing clusters, because nothing deviates.

**What this does and does not license.** It closes the specific gap C12 named: I-045's BTC-only, one-direction control is now superseded by a two-symbol, two-direction, full-span measurement with the same result (0 and 0). It does **not** extend past 2026-07-28 — Binance has explicitly reserved the right to change any symbol's cadence without notice [cited — official, `DATA-VERIFY-001` §3.2], which is exactly the forward-window exposure K7 is designed to catch mechanically rather than assume away. K7's own construction (trigger on any documented parameter change, not on a measured cadence break) is unaffected by this result either way — this measurement is evidence about the *premise* K7 was built on, not a substitute for K7 itself.

**Per the dispatch's escalation rule:** no genuine cadence deviation was found on BTC or ETH. The escalation rule (do not trim the universe further, escalate to Validation for an admissibility ruling on the whole family) is therefore **not triggered**. No Issue Log entry is filed — the escalation rule is conditional on finding a genuine deviation, and none was found. C12 is reported to the CIO as measured and closeable; the decision to close it belongs to the Director/Validation, not to this seat, and this document does not edit `PREREG-002` or `DIR-RESTATE-001` per the dispatch's constraint.

---

*Head of Data & Infrastructure · Castellan Capital · 2026-08-04*
*Row-count measurement only. No hypothesis opened, no trial run, no vault touched, no registry write. `book/registry.db` and `book/book.db` untouched.*
