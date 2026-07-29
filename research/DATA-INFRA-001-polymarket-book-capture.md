# DATA-INFRA-001 — Recurring Capture of Live Polymarket Order-Book Snapshots

**Seat:** Head of Data & Infrastructure
**Date:** 2026-07-29
**Directed by:** Principal direction D-011 §4, on the logic that historical Polymarket book depth cannot be
reconstructed (`DATA-PROBE-001`) but *can* be accumulated prospectively, and every day this is not running is
a day of depth history the firm can never recover.
**Scope:** firm data infrastructure. Not scoped to any hypothesis family — forward-lag is shelved and its
falsifier redesign is explicitly not funded by this task. Nothing here pre-registers a hypothesis, seals a
vault, runs a backtest, or computes a signal/return statistic.
**Status:** built, tested against the live venue, and proven end-to-end against the real `book/pit.db`.
Not installed as a recurring job — the Principal has not authorised a scheduled task; see §5.

House rule 6 throughout: **[measured]** = observed this session · **[cited]** = external source read, not
executed · **[inferred]** = reasoned from measured/cited facts · **[assumed]** = unverified premise, flagged.

---

## 1. What was built

Three additions, all additive — no existing harness file's *behaviour* was changed:

| File | What |
|---|---|
| `harness/castellan/loaders.py` (extended) | `select_polymarket_universe`, `refresh_universe` / `load_universe_state` / `save_universe_state`, `parse_polymarket_book`, `fetch_polymarket_books`, `ingest_polymarket_books` — see §2–§4 |
| `harness/scripts/capture_polymarket_book.py` | the runnable invocation (§5) — one poll per run, exits |
| `book/polymarket_universe.json` | persisted market-tracking state (created by running the script; not a schema file, not committed by this seat) |

Design follows the same separation-of-concerns rule the rest of `loaders.py` already uses: `parse_polymarket_book`
is pure (no I/O, tested offline this session, §7), `fetch_polymarket_books` does I/O only, `ingest_polymarket_books`
composes the two against a `PITStore`.

**Two writes per successfully captured token, both point-in-time:**
1. `store.ingest("polymarket-clob", token_id, df, knowledge_time=...)` — scalar fields (§4), the fast/queryable
   path, at a configurable depth.
2. `store.ingest_documents("polymarket-clob", token_id, [...])` — the **full, un-truncated** raw response,
   `ref`-deduplicated on `f"{token_id}:{venue_timestamp}"`. Nothing above the configured depth is discarded from
   the firm's data — it is only de-prioritized out of the scalar/fast path. A future researcher who needs level 11
   onward can re-parse it from here without re-polling (which would be impossible for a past snapshot regardless).

**Proven against the real store this session**, not a throwaway one — three real (non-dry-run) capture rounds were
run against `book/pit.db` and `book/registry.db` (the real ones), because the task's own framing is that a live
snapshot recorded today already has a valid `knowledge_time = today` and there is no cutoff conflict for a
prospective capture. Result **[measured]**: 20/20 token books captured on every round; 2,244 observation rows and
56 document rows now sit under `source='polymarket-clob'` in `book/pit.db`, covering 10 markets / 20 outcome
tokens. Suite re-run after: see §9 for an important caveat that is **not** this task's doing.

---

## 2. Market-selection rule, and why it is not "pick the top N by volume"

**Rule.** Two strata, both drawn from the same ranked candidate pool (Gamma's `active=true&closed=false&
enableOrderBook=true`, sorted by trailing-24h volume, top 100 candidates):

- **Liquid tier** (default 5): the top-N markets by 24h volume.
- **Thin tier** (default 5): N markets from volume-rank band 20–40 of the same pool.

**Why a thin tier is not optional — the actual argument, not a hedge.** Quote-liveness (T2) is close to
trivially true on the most liquid markets on this venue: the Fed-rate and similar top-volume markets essentially
never go one-sided **[inferred, consistent with the measured sample below]**. Polling only the liquid tier would
accumulate a year of book history that still could not answer the question Gate 0(4) actually failed on, because
there would be no variance in the outcome being measured — every day would trivially pass T2. **The thin tier is
where two-sidedness is actually contested**, which is what makes the eventual measurement informative rather than
a foregone conclusion. This is the direct answer to the task's own warning that "a badly chosen universe
accumulates useless history at full cost": an *all-liquid* universe is the badly-chosen one for this specific
purpose, even though it is the more defensible choice by every conventional liquidity screen.

**Measured within the first ~20 minutes of running** — proof the design choice is doing its job, not a
coincidence: of 10 tracked markets, one **liquid-tier** market ("Will the Fed decrease interest rates by 50+ bps…")
and one **thin-tier** market ("Will the price of Bitcoin be above $62,000…") already showed `two_sided = 0`
(one-sided book) at the most recent snapshot, alongside the rest reading `two_sided = 1` **[measured]**. The
phenomenon this infrastructure exists to measure is already present in the first few samples — not just a
theoretical justification for the stratification.

**Stability vs. churn.** The tracked set is **not** re-selected every run. `refresh_universe` loads the persisted
state, re-checks only the *currently tracked* markets' status (one batched Gamma call), retires any that have
closed, and tops up freed slots from a fresh ranked pull. An already-tracked, still-open market is left alone
indefinitely, so its history stays continuous for as long as it remains open — this is what makes "was there a
two-sided quote in this bar" answerable per-contract later rather than only across a shuffled cross-section.

**Exclusion floor.** Candidates with `volume24hr < 1` are excluded from both tiers — a market with no observed
trading in the last 24h is not distinguishable from one with no functioning book at all, and capturing it
accumulates snapshots that answer a question ("is this market's book alive at all") nobody asked.

**What this rule deliberately does not do.** It does not target any specific category (politics, sports, crypto
price) — Gamma's own cross-category volume ranking is taken as the neutral ordering, so the universe is not hand-
picked toward whatever a pod happens to be interested in. Measured composition today **[measured]**: 3 Fed-rate
markets, 1 geopolitical (Ethiopia PM), 1 crypto-price market, and 3 sports contract-pairs — a spread that fell out
of the rule, not a spread anyone chose.

---

## 3. Cadence, depth, and storage — the tradeoffs actually reasoned through

### 3.1 Depth

**Default: top 10 price levels per side**, configurable via `--depth`. `n_bid_levels`/`n_ask_levels` always record
the *true* level count regardless of the cap (so a 3-level book is distinguishable from a 30-level book truncated
to 10), and the **full untruncated book is always stored separately** in `documents` (§1), so depth is a
fast-path/storage tradeoff, never a data-loss decision. Rationale for 10: T4's definition (`DATA-SPEC` §2) is
resting size *within `S_max` of the touch*, and a realistic tradable edge implies a price band close to the
touch — 10 levels comfortably covers that band for the markets observed this session (one sample book had 83 ask
levels total; the ones near the touch, which is what T4 needs, were within the first handful).

### 3.2 Cadence

**Recommended: every 15 minutes** (96 polls/day). Reasoning, not a default reached for convenience:
- A polled snapshot cannot see a quote flicker between polls **by construction** — this is a sampling process,
  not a continuous log, and that limit does not go away at any cadence. Faster polling narrows the blind window;
  it cannot close it.
- The venue's own documented rate limit on `/books` is 500 requests/10s **[cited — docs.polymarket.com]**; this
  firm's entire universe (20 tokens) fits in **one** batched request per poll (§4), so rate limits are not
  remotely binding at any cadence this firm would plausibly choose — the real constraint is storage, not the API.
- 15 minutes is a starting point chosen to be conservative on storage (§3.3) while still resolving intraday
  liveness patterns; it is a parameter of the script (`--depth`, `--n-liquid`, `--n-thin` are also exposed), not a
  hard-coded constant, and should move if measured storage growth or research need argues for it.

### 3.3 Storage — measured, not estimated

Two isolated real capture rounds were measured directly against `book/pit.db` (20 tokens, depth 10, before vs.
after file size and row counts) **[measured]**:

| Quantity | Measured value |
|---|---|
| `book/pit.db` growth, one poll round (20 tokens) | 339,968 bytes |
| Observation rows added, one round | 732 (≈36.6 fields/token) |
| Document rows added, one round | 18–20 (raw JSON, avg 3,187 bytes/doc) |

**The dominant cost is not the raw JSON documents — it is the observations table.** Roughly 283 KB of the 340 KB
per round (≈83%) is observation rows, versus ≈57 KB for the full raw-book documents. This is because
`PITStore.observations` carries the full `symbol` string (a Polymarket token_id, a 75–78 digit decimal number) on
*every* row and in its composite index, repeated across ~37 fields per token per poll. This was **not** what I
expected going in — the natural assumption is that storing full raw order books is the expensive part; measured,
it is the opposite. Flagged in §8 as a candidate future optimization (a short local alias for `symbol`), not
undertaken here — changing `PITStore`'s schema is outside this task's scope and touches a shared, actively-
developed file other seats are also mid-edit on this session (§9).

**Projection at the recommended cadence (15 min, 10 markets / 20 tokens, depth 10), extrapolated linearly from
the measured per-round figure** — labelled `[inferred]` beyond the measured base case:

| Horizon | Rows (obs + doc) | Disk |
|---|---|---|
| 1 day (96 rounds) | ≈ 73,300 | ≈ 31.9 MB |
| 1 week | ≈ 513,000 | ≈ 223 MB |
| 1 month (30d) | ≈ 2.2M | ≈ 957 MB |
| 1 year | ≈ 26.7M | ≈ 11.6 GB |

Trivial on local disk at this universe size. **Does not scale for free**: if the universe were later widened to,
say, 100 markets (200 tokens), the same arithmetic gives ≈ 116 GB/year — still SQLite-tractable but no longer
"don't think about it," and single-table query performance on `observations` (already ≈303K rows firm-wide before
this task, from the yfinance/binance/binanceusdm ingest in `DATA-INGEST-001` — **[measured]**) is worth watching
as it grows. No retention/rollup policy is proposed here — flagged open in §8.

---

## 4. Data dictionary

`source = 'polymarket-clob'`. `symbol` = the outcome token's `asset_id` (a Polymarket CLOB token_id) — **Yes and
No are stored as separate symbols**, not merged, because they are genuinely separate resting order books on
Polymarket's CLOB, not guaranteed complementary.

| Field | Meaning | `event_time` semantics | `knowledge_time` semantics |
|---|---|---|---|
| `best_bid`, `best_ask` | Touch price, this side | Venue's own snapshot `timestamp` on the `/books` response — see note below | Instant this firm's poller received & parsed the batch HTTP response (§ two-timestamp note) |
| `bid_size_at_touch`, `ask_size_at_touch` | Resting size at the touch | same | same |
| `mid`, `spread` | `(best_bid+best_ask)/2`, `best_ask-best_bid`; present only when both sides are non-empty | same | same |
| `two_sided` | `1.0` iff both bids and asks non-empty, else `0.0` — the literal T2 flag per contract-day-and-snapshot | same | same |
| `n_bid_levels`, `n_ask_levels` | TRUE level count on each side, uncapped by `--depth` | same | same |
| `bid_price_l{i}`, `bid_size_l{i}` (i=1..depth) | Price/size at the i-th resting bid level, best-first | same | same |
| `ask_price_l{i}`, `ask_size_l{i}` (i=1..depth) | Price/size at the i-th resting ask level, best-first | same | same |
| `last_trade_price` | Venue-reported last trade price, when present in the response | same | same |
| **`documents` table, `doc_type='book_snapshot'`** | Full, untruncated `bids`/`asks`, plus `hash`, `tick_size`, `min_order_size`, `neg_risk`, and the tracked market's `condition_id`/`question`/`slug`/`outcome` | same | same |

**`event_time` — a measured correction to the vendor's own documentation.** `docs.polymarket.com` states the
`/book` response's `timestamp` field is "seconds since epoch." **Measured [measured] against a live response**:
the field is a 13-digit string (`"1785345770396"`); interpreted as **milliseconds** it cross-checks exactly
against wall-clock time at the moment of the call (2026-07-29, matching the request's actual timestamp);
interpreted as seconds per the docs it is nonsensical (year 58545). **The response is milliseconds; the
documentation is wrong.** Converted via `pd.to_datetime(int(ts), unit="ms", utc=True)` — **converted, never
`tz_localize`/stripped**, the exact discipline I-020 named as missing from the yfinance loader. This finding is
recorded here rather than assumed away, in the same spirit as I-020: verify units against a live response, never
trust a vendor's stated units at face value.

**Why `event_time` and `knowledge_time` are genuinely distinct here, unlike most of this firm's other sources.**
For a historical backfill (yfinance, ccxt), `event_time` is years in the past and `knowledge_time` is "whenever
this firm first fetched it" — the two differ by years, and every backfilled row from the same session shares
(approximately) one `knowledge_time`. For this loader, capturing *forward* in real time, the two differ by
**network and queue latency only** — typically sub-second to a few seconds, measured this session in the low
hundreds of milliseconds. That is the load-bearing distinction the task named: this is the one source in the firm
where the two timestamps are close together but *not identical*, both non-degenerate, and both meaningful — as
opposed to a vendor "current value" fetch with no snapshot-generation timestamp of its own, where implementers
typically (and correctly, absent better information) default both to the same `now()`.

---

## 5. The runnable invocation, and its stated cadence

```
python3 harness/scripts/capture_polymarket_book.py [--pit-db PATH] [--registry-db PATH]
    [--state PATH] [--depth N] [--n-liquid N] [--n-thin N]
    [--thin-lo N] [--thin-hi N] [--dry-run]
```

One poll per invocation; the script does not loop, sleep, or daemonize — recurrence is the caller's/scheduler's
responsibility, per the task's explicit instruction not to create a scheduled task this session. **Documented,
not installed**, recommended line for whoever the Principal authorises to install it:

```
*/15 * * * *  cd /path/to/castellan-capital && \
    python3 harness/scripts/capture_polymarket_book.py \
    >> logs/polymarket_capture.log 2>&1
```

**Verified working this session** against the real store, three times, non-dry-run **[measured]**:

```
[2026-07-29T17:45:28Z] universe: 10 active (5 liquid / 5 thin), 0 resolved/retired (tracked, not polled)
[2026-07-29T17:45:28Z] captured 20/20 token books across 10 markets
[2026-07-29T17:46:10Z] universe: 10 active (5 liquid / 5 thin), 0 resolved/retired (tracked, not polled)
[2026-07-29T17:46:10Z] captured 20/20 token books across 10 markets
[2026-07-29T17:48:12Z] universe: 10 active (5 liquid / 5 thin), 0 resolved/retired (tracked, not polled)
[2026-07-29T17:48:12Z] captured 20/20 token books across 10 markets
```

`--dry-run` refreshes and prints the universe (with per-market tier and volume) without fetching books or writing
anything — used above to sanity-check selection before the first real write.

---

## 6. How the quote-liveness query would be served

This is the exact gate Gate 0(4) failed on: "the quote-liveness gate is unexecutable on measured data" (I-033
item 3). It becomes a direct query against `observations` once enough history has accumulated:

```sql
SELECT symbol, event_time, value AS two_sided
FROM observations
WHERE source = 'polymarket-clob' AND field = 'two_sided'
  AND event_time > :window_start AND event_time <= :window_end
ORDER BY symbol, event_time;
```

Grouped per contract-day (or whatever bar the family defines) and averaged, this **is** T2's own metric
(`DATA-SPEC` §2, T2: "both a bid and an ask present... for ≥ θ_2 of the observation window") computed directly
from stored samples — `fraction_two_sided = mean(two_sided)` over the snapshots falling in that bar, compared
against the spec's `θ_2 = 0.80` threshold. No proxy, no upper bound, no trade-print substitute — the thing T2
actually asks for. The same query pattern against `bid_size_l{i}`/`ask_size_l{i}`/`bid_price_l{i}`/
`ask_price_l{i}` answers T4 (resting size within `S_max` of the touch) directly, for whatever `P_notional`/`S_max`
a future pre-registration states, once `PITStore.asof`/`rows_in_window` is used rather than a raw SELECT so the
point-in-time discipline (`knowledge_time ≤ decision_time`) is preserved for any actual measurement — the query
above is illustrative of the *shape* of the answer, not itself a sanctioned measurement path (no signal or
return statistic was computed from it this session, per this task's own constraint).

**The honest limit, stated plainly.** This only answers the question for the calendar time the capture has
actually been running. It is silent, permanently, about every day before the day this was turned on — exactly
the same structural limit `DATA-PROBE-001` established for the historical case, now simply moved forward to
"today onward." Nothing about running this script retroactively improves the pre-2026-07-29 record.

---

## 7. Failure handling — reasoned through, and exercised where it could be

- **Per-token parse/write failure** (malformed entry, unexpected field shape): caught individually inside
  `ingest_polymarket_books`; that token is recorded in `failed`, the rest of the batch proceeds. **Tested this
  session [measured]** with synthetic one-sided and empty books (§ code excerpt below) — no `KeyError`, correct
  `two_sided=0.0`, no `mid`/`spread` fields when one side is absent.
- **Whole-batch HTTP failure** (timeout, connection error, 5xx): retried up to 3 times with exponential backoff
  (2s, 4s, 8s); if all attempts fail, **nothing is written** and every requested token is reported failed — this
  keeps `PITStore.ingest`'s own all-or-nothing-per-call property intact at the poll level, rather than silently
  writing a partial, misleading poll.
- **Resolved markets stop being polled.** `refresh_universe` re-checks every *currently tracked* market's
  `active`/`closed` status against Gamma on every run (one batched call for the whole tracked set) and retires
  any that have closed — retired markets are **kept in the state file** (the record of what was tracked and for
  how long) but dropped from the token set actually sent to `/books`. **Tested this session [measured]** via a
  synthetic tracked market whose status check was made to return "not found," which correctly flipped it to
  `status: "resolved"`.
- **Rate limiting**: not encountered this session (well under the documented 500 req/10s on `/books`, since the
  whole universe is one batched call). If it were hit, the existing retry/backoff path handles a 429 the same as
  any other transient failure; no separate code path exists for it specifically, which is a reasonable choice at
  this firm's scale but would be worth revisiting if the universe grows into double digits of batched requests
  per poll.
- **A genuine finding, corrected in-session, not left as a footnote:** the Gamma API's `condition_ids` filter
  requires the query parameter **repeated** (`?condition_ids=A&condition_ids=B`), not comma-joined
  (`?condition_ids=A,B`) — the comma-joined form does not error, it **silently matches zero markets** [measured].
  First implementation used the comma-joined form and, within three seconds of a working dry run, incorrectly
  marked all 10 tracked markets "resolved" because the status check legitimately found none of them. Caught by
  the very next command (a real capture reporting `0 active`) before any bad state was left running unattended,
  and fixed (`urlencode(..., doseq=True)` with a list value) before this deliverable was written. Recorded because
  it is the same *shape* of hazard this firm has already logged twice (I-010, I-022): an external interface that
  **fails permissively/silently** rather than erroring, discovered only by watching the actual numbers rather than
  trusting that "no exception" meant "correct."

---

## 8. What remains unresolved

- **No retention/rollup policy.** Storage is trivial at the current 10-market universe (§3.3) but has no defined
  ceiling or downsampling strategy if the universe or history grows substantially. Not designed this session —
  flagged for whoever next revisits cadence/universe size.
- **The `symbol`-string storage overhead** (§3.3) — token_ids are long decimal strings, repeated per row and in
  the index; a firm-wide `PITStore` schema change (e.g., an interned short alias) would help every source, not
  just this one, but is out of scope for an infra task that should not be modifying shared harness schema mid-
  session, especially while other work is concurrently in flight against the same files (§9).
- **No monitoring/alerting on missed polls.** If the scheduler (whichever the Principal authorises) fails to run
  for an extended period, nothing in this design detects or reports the gap — it would simply show up later as a
  hole in the coverage timeline. Worth a lightweight heartbeat check once a real cadence is running, not built
  here.
- **Universe size (5 liquid / 5 thin) is a starting point, not a researched optimum.** Larger would give broader
  coverage sooner at proportionally higher storage cost (§3.3); no attempt was made to derive an optimal N, since
  there is no stated research demand yet to size it against.
- **How long until quote-liveness is actually answerable is a function of accumulation time, not code.** See the
  final message to the CIO for a stated estimate.

---

## 9. A finding that is not this task's doing, reported because it should not be misattributed

The harness suite was **96/96 passing** at the start of this session (confirmed before writing any code). It is
**95/96 passing** now — one failure, `test_holdout_p1.py::test_P8_report_lists_predecessor_chain_prereg_hashes`,
raising `InheritedCountDoubleCountError` on an edge case (`n_inherited=0` compared against a predecessor family
with zero real trials). **This is not caused by this task.** `git diff` shows uncommitted, in-progress changes to
`harness/castellan/registry.py` and `harness/castellan/gates.py` (the I-027 `n_inherited` fix, referencing
`VALIDATION-GATE0-001` H-3a/H-5b) already present in the working tree before this task touched anything — this
task's only source changes are additive, confined to `loaders.py` and the new `harness/scripts/` file, and never
touch `registry.py`, `gates.py`, or `holdout.py`. Opening `TrialRegistry("book/registry.db")` as part of this
task's normal operation did trigger that file's own `_migrate()` (adding the already-in-progress `n_inherited`
column if not already present) as a side effect of simply connecting — `book/hypotheses` remains empty (zero
families registered, confirmed) and `book/registry.db`'s only other content-relevant activity from this task is
zero logged `data_restatement` events (no restatements occurred). Reported here so the CIO does not attribute an
unrelated, pre-existing (and separately owned) registry defect to this deliverable.

---

*Head of Data & Infrastructure · Castellan Capital · 2026-07-29*
*Firm infrastructure. No hypothesis pre-registered, no vault sealed, no backtest run, no signal or return
statistic computed. Not committed to git — the CIO commits.*
