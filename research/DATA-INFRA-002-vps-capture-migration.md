# DATA-INFRA-002 — VPS Migration for Polymarket Order-Book Capture

**Seat:** Head of Data & Infrastructure
**Date:** 2026-08-04
**Dispatch:** D-001/Sprint-2 · Rider A · Compute: 1 Sonnet unit · Spend approved by the Principal: ~$5/month
**Status:** design, runbook, and provisioning artifacts complete. **No account created, no money spent, no
infrastructure provisioned, no firm data transmitted to any host.** Every step requiring the Principal's hands
is marked **[PRINCIPAL]** below. The laptop capture was not stopped and continues running throughout this
document's preparation (see §9 for live evidence of that).

House rule 6 throughout: **[measured]** = observed this session, reproducible · **[cited]** = external source
read, not executed · **[inferred]** = reasoned from measured/cited facts · **[assumed]** = unverified premise,
flagged.

---

## 0. The measured case, verified independently

The CIO's morning figures, recomputed from `logs/capture/polymarket-book.out` directly rather than trusted:
31 successful polls, 2026-07-29T19:04:05Z → 2026-08-04T16:38:15Z, span 141.569 hours, 566.28 expected polls at
900s cadence, coverage **5.474%** (rounds to 5.5%), 12 gaps over one hour, worst 59.918h (2026-08-01T08:16:33Z →
2026-08-03T20:11:39Z, the weekend), second 18.521h, third 16.551h (rounds to 16.6h). **All confirmed exactly**
[measured, this session, independent script — see §5]. The Principal's original ~9% working figure was the
more-wrong of the two prior estimates, as the dispatch states.

**A refinement, found by querying `book/pit.db` directly instead of the log.** The log only ever sees rounds
`launchd` fired. `book/pit.db` additionally holds 3 successful rounds run manually during `DATA-INFRA-001`'s
own testing (17:45:28Z, 17:46:10Z, 17:48:12Z on 2026-07-29), **before** the launchd job existed
(`capital.castellan.polymarket-book.plist` was written at 15:04 that day but the log only starts at 19:04).
Over the full store-derived history: **34 → 35 successful rounds** (growing as the still-running laptop
capture continues; see §9), span 142.9h → 143.1h, coverage **5.95% → 6.11%**. This is not a contradiction of
the CIO's figure — it is the same measurement over a slightly larger, more complete window, and it is what
`harness/scripts/report_polymarket_coverage.py` (§5) reports by default because it reads the store, not a
host-specific log file that will not exist in this form on a VPS.

---

## 1. The dual-writer problem — decision and defence

**Decision, one sentence: the VPS owns a capture-only PITStore of its own and never touches `book/pit.db`
directly; its data reaches the real store only by being pulled down and replayed through a dedicated,
idempotent, restatement-aware merge script that runs against the real store with the real registry.**

### Why not make the VPS authoritative for the whole store

Rejected. `book/pit.db` is 61.1 MB, 628 documents, 362,077 observations, spanning yfinance, Binance spot,
Binance USDM funding, EDGAR, and Polymarket — it is the firm's entire data layer, not a Polymarket-specific
artifact. Making a $6/month VPS authoritative for it would mean:

- Every other seat's research session (which runs on this machine, not the VPS) would need live network
  access to the VPS to read prices at all — turning a local, always-available SQLite file into a networked
  dependency with a new latency and availability surface, for zero benefit to the sources that have nothing to
  do with Polymarket.
- The `book/pit.db` snapshot-backup regime the Principal and CIO established this same sprint (D-001 §2, "git
  for decisions and code, snapshots for bulk data") is scoped to this host. Moving authority to the VPS either
  duplicates that regime on a third-party box or abandons it.
- It multiplies the blast radius of a VPS compromise from "a few weeks of public Polymarket order-book history"
  to "the firm's entire proprietary data layer, including whatever a future hypothesis's registry entries and
  price history reveal about what the firm is researching." A $6/month box is not where that risk belongs.

None of this is required to solve the actual problem, which is narrower: **give the Polymarket capture a host
that stays awake.** A capture-only satellite store does that with none of the above cost.

### The mechanism, concretely

1. The VPS runs the *same, unmodified* `harness/scripts/capture_polymarket_book.py`, pointed via
   `--pit-db`/`--registry-db` at its own local files (`/opt/castellan/book/pit_capture.db`,
   `/opt/castellan/book/registry_capture.db`) — never at the real ones. These files are born empty on the VPS
   and contain only what this script writes from the moment it starts running: `source='polymarket-clob'`
   observations/documents and `source='polymarket-capture-meta'` heartbeats (§2). Nothing of the firm's
   existing 362,077 observations or 628 documents is ever present on, or transmitted to, the VPS.
2. Periodically (the runbook, §7, recommends weekly, at a Data & Infra working session; more often is fine and
   is a performance question only, not a correctness one), the capture-only file is pulled to wherever this
   repo lives (`rsync`/`scp` over SSH — **[PRINCIPAL]**, since it is the only step in this whole design that
   moves bytes between hosts).
3. `harness/scripts/merge_polymarket_capture.py` (new this session) replays every round from the pulled file
   into the real `book/pit.db`, through `PITStore.ingest()` / `ingest_documents()` — **the same code path every
   other source in the firm already goes through**, not a bespoke bulk-copy. It is initialized with the real
   `TrialRegistry` (`book/registry.db`), so any anomaly is logged to the actual registry, not a throwaway one.
4. The merge is idempotent by construction (`ingest()` skips unchanged values, `ingest_documents()` dedupes on
   `ref`) and watermarked (`book/polymarket_merge_state.json`, a persisted `max(knowledge_time)` merged so far)
   purely as a performance optimization — deleting the watermark and re-running from scratch produces the
   identical end state, only slower. Verified this session with a real merge, a real re-run, and a real
   watermark-skip (`harness/tests/test_capture_merge.py`, plus a manual end-to-end run against files in the
   scratch directory, both reproduced above and in the trial log this document is committed alongside).

### How a restatement incident is still detected and auto-logged under A4

Exactly the same way any other source's is: `PITStore.ingest()` compares every incoming `(source, symbol,
field, event_time)` against what the real store already holds, and if the value differs, it inserts a new
version **and calls `registry.log_event("data_restatement", ...)`** — because the merge script opens the real
`TrialRegistry`, this is not a special case, it is the store's ordinary behaviour, exercised on satellite data
instead of a vendor refresh. `merge_polymarket_capture.py` additionally checks the merge result for
`observations_restated > 0` and, if any fired, prints an explicit stop-and-escalate instruction to stderr and
exits with a distinct code (3) rather than treating it as routine — because for this specific source a
restatement is **not** expected the way a yfinance re-adjustment is: Polymarket `event_time` is the venue's own
millisecond snapshot timestamp, so two different values landing at the same `(symbol, field, event_time)` would
mean either a genuine parsing bug, a clock-skewed replay, or two pollers somehow reading the identical venue
snapshot differently — worth investigating immediately, every time, not routine noise (documented in
`harness/castellan/capture_merge.py`'s module docstring and pinned by a test,
`test_genuine_conflict_is_detected_as_restatement_and_logged`). **The blast-radius note this seat owes
Validation on any such event, today, is: zero — `book/registry.db` presently holds zero pre-registered
hypothesis families depending on `source='polymarket-clob'`** (re-confirmed this session; unchanged from
`DATA-INFRA-001` §9's finding), so a restatement here would currently invalidate no trial. That will not remain
true once a family is opened against this source, and the escalation duty does not lapse because the number is
zero today.

---

## 2. The not-polled vs. no-quote distinction — verified against the schema, not assumed

**Checked directly, both directions, before writing anything:**

- **"Polled, no quote" IS distinguishable from a missing row, and always was.** `parse_polymarket_book` sets
  `two_sided = 1.0 if (bids and asks) else 0.0` **unconditionally** — a genuinely empty book (both sides empty)
  still produces a row with `two_sided=0.0`, `n_bid_levels=0`, `n_ask_levels=0`. This was asserted in
  `DATA-INFRA-001` ("tested this session") but had no reproducible test; it now does
  (`test_parse_empty_book_still_writes_a_row`, `harness/tests/test_polymarket_capture.py`).
- **"Not polled" and "polled, and the whole batch failed" were NOT distinguishable, and this was not a
  theoretical gap.** `ingest_polymarket_books`'s own docstring states the design plainly: "if every attempt
  fails, NOTHING is written." A round the scheduler never fired *also* writes nothing. Both leave an identical
  absence of rows in `observations` and `documents` for that timestamp — checked directly against
  `harness/castellan/data.py`'s schema, not inferred from prose. **This is not hypothetical**: `I-047`
  (`logs/ISSUE_LOG.md`) documents 4 real, uncaught occurrences of exactly this failure mode in the laptop's own
  history, discovered while preparing this document — a network call inside `refresh_universe` had no retry
  logic (unlike the CLOB fetch, which did), crashed on transient DNS failure, and left **zero trace anywhere**,
  not even the ordinary stdout log line.

**What was built to close it, specified in the dispatch and delivered, not merely specified.**
`record_capture_heartbeat` (`harness/castellan/loaders.py`) writes one document per poll *attempt*, regardless
of outcome, to `source='polymarket-capture-meta'`, `symbol='__heartbeat__'`, carrying `ok`, `n_requested`,
`n_captured`, `n_failed`, and `error`. It is wired into every exit path a poll can take:

| Path | Heartbeat written? |
|---|---|
| Successful round (all or some tokens captured) | Yes, `ok=True` |
| Whole-batch CLOB fetch fails after retries | Yes, `ok=False`, error recorded |
| Universe refresh returns zero active tokens | Yes, `ok=True`, `n_requested=0` |
| **Any other uncaught exception, anywhere in the round** (I-047's fix) | Yes, `ok=False`, error recorded |
| Scheduler never fires the process at all | No row, correctly — nothing happened |

This is additive-only: no change to `PITStore`'s schema, no migration, reusing the existing
`ingest_documents()` API the way EDGAR filings already do. **The honest limit, and it does not go away**: this
resolves the ambiguity from the moment the mechanism exists in a running capture forward — the running laptop
capture picked it up on its very next scheduled firing, unprompted, at **2026-08-04T16:53:16Z** [measured, live,
not a test] — and is structurally incapable of resolving it for any capture history before that instant. Every
gap in the 143-hour window this document's §0 measures remains permanently ambiguous between "scheduler did not
fire" and "fired and failed outright." `harness/scripts/report_polymarket_coverage.py` reports the two windows
(pre-heartbeat / post-heartbeat) separately rather than pretending the distinction applies retroactively.
Logged as `I-048`.

---

## 3. Provider and cost

**DigitalOcean Basic Droplet, the $6/month tier** — 1 vCPU, 1 GiB RAM, 25 GB SSD, 1,000 GiB outbound transfer,
billed per-second [confirmed against DigitalOcean's own pricing page, 2026-08-04]. Ubuntu 24.04 LTS. This is
$1/month over the Principal's stated "~$5/month," flagged rather than silently rounded — the reason is the disk
ceiling (below), where the $4/month tier (512 MiB RAM, 10 GB SSD) reaches roughly 7 months of runway at full
cadence against 21 months for the $6 tier, which is not "boring and durable" for an asset this document's own
Charter language calls irreproducible. **[PRINCIPAL] to confirm the extra $1/month is acceptable, or to direct
the $4/month tier with a shorter retention/rollup horizon accepted up front.**

Reasoning for the provider, not just the number: boring and durable over clever, per the dispatch's own
instruction. DigitalOcean is a well-established, single-purpose-VM provider with a stable pricing page, a
straightforward web console the Principal can drive without a CLI, native snapshots (a second recovery path
beyond the merge-based one this document builds), and no product-bundling complexity. Hetzner and Linode were
also priced and are comparable-to-cheaper for equivalent specs, and would not be a wrong choice — DigitalOcean
is recommended on simplicity of the Principal's one-time provisioning step, not a claim that it is
technically superior.

### Growth-rate arithmetic, computed from measured data

`DATA-INFRA-001` §3.3 measured **339,968 bytes per successful round** (20 tokens, depth 10 — the firm's current
universe size) directly, as a before/after file-size diff against the real store. Extended here to the
recommended full 900s cadence:

```
339,968 bytes/round × 96 rounds/day (86,400s / 900s)  =  32,636,928 bytes/day   ≈ 32.6 MB/day
× 30                                                    = 979,107,840 bytes/month ≈ 0.98 GB/month
× 365                                                    = 11,912,478,720 bytes/year ≈ 11.9 GB/year
```

Against the $6/month tier's 25 GB SSD, netting roughly 4 GB for OS + Python venv + logs, **usable ≈ 21 GB**:

```
21 GB / 32.6 MB/day  ≈  643 days  ≈  21.1 months  ≈  1.76 years
```

**What happens at the ceiling, named rather than left implicit.** SQLite writes begin failing
(`SQLITE_FULL`/`disk I/O error`) once the volume is exhausted — the capture-only store stops accepting new
rounds, and depending on exactly where the write lands, a partially-written round could in principle be left
inconsistent (mitigated in practice by SQLite's own transaction atomicity, but not something to rely on
discovering after the fact). This is a real outage, not a graceful degradation, and it is silent unless
`health_check.sh` (§7) is actually run. Two remedies exist and neither is exercised by this document: (a) a
retention/rollup policy — e.g. downsample or archive book snapshots older than N months once they have been
merged into the real store and are no longer needed on the VPS at all — is free within the existing schema and
is this seat's to design when the runway starts running out, or (b) a bigger volume/droplet, which is
additional spend and therefore **[PRINCIPAL]**'s call, not mine, the same as the original $5/month approval.
Neither is urgent at ~21 months of runway; both are flagged now so the ceiling is not discovered by an outage.

**If the universe widens** (more markets tracked), this arithmetic scales roughly linearly and the runway
shrinks proportionally — `DATA-INFRA-001` §3.3 already flagged that a 100-market universe would run
≈116 GB/year, well past this tier. Any such widening is a Data & Infra design call, but the storage consequence
should be computed and stated before it is made, not discovered afterward.

---

## 4. Secrets

**None are required, and this materially simplifies the migration, exactly as the dispatch anticipated.**
Checked directly against every network call the capture script makes, not assumed:

- `fetch_polymarket_books` (`POST https://clob.polymarket.com/books`) — `Content-Type` and a `User-Agent` header
  only. No API key, no bearer token, no signature.
- `_gamma_get` (used by `select_polymarket_universe` and `_check_market_status`, both against
  `https://gamma-api.polymarket.com/markets`) — `User-Agent` only.

Both are documented, public, unauthenticated endpoints [measured, confirmed by direct code inspection,
`harness/castellan/loaders.py`]. The VPS therefore needs **no Polymarket credential of any kind, ever** — there
is nothing to provision, nothing to rotate, and nothing that could leak from the box beyond the box's own SSH
access.

**What the VPS does need, and how it is handled — neither is a repo secret.**
1. **SSH access for the Principal to administer the box** — a public key added at droplet creation
   (**[PRINCIPAL]**), private key never leaves the Principal's machine, never touches this repository.
2. **An SSH key/session for the pull step** (VPS → local capture-store file, §1) — the same mechanism, run from
   whichever machine performs the pull. No new credential type; reuses the administration key.

No `.env`, no vault, no secret ever needs to be written to this repo, to Oracle, or to the VPS's disk for this
capture to run.

---

## 5. Coverage instrumentation

`harness/scripts/report_polymarket_coverage.py` — reads `book/pit.db` directly (portable to the VPS's own
capture-only store via `--pit-db`, which is exactly what `health_check.sh`, §7, uses). No log-tail parsing.

```
python3 harness/scripts/report_polymarket_coverage.py [--pit-db PATH] [--cadence-seconds N]
    [--gap-threshold-hours H] [--since ISO] [--until ISO] [--json]
```

Two measurement methods, reported side by side rather than blended (house rule 6):

1. **Successful-round count** — `DISTINCT knowledge_time` in `observations` for the source. Exact, works
   retroactively for capture history before the heartbeat mechanism existed (§2). This is what reproduced the
   CIO's 31/566/5.5%/12-gaps figure exactly when the window was restricted to the launchd-only span (§0), and
   found the additional 3 pre-launchd rounds when it was not.
2. **Heartbeat-based attempt count** — from the first heartbeat row onward, reports total attempts and how many
   failed outright, closing the ambiguity §2 describes, for that window only.

Run live against the real store this session:

```
Polymarket capture coverage -- book/pit.db (source=polymarket-clob)
  window:            2026-07-29T17:45:28Z  ->  2026-08-04T16:53:16Z
  span:              143.1h
  expected polls:    572.5
  successful polls:  35  (method 1: distinct knowledge_time)
  coverage:          6.11%
  gaps >= 1.0h: 13   [worst: 59.9h, 18.5h, 16.6h -- matching §0 exactly]
  heartbeat mechanism: active since 2026-08-04T16:53:16Z
    attempts recorded: 1, of which failed: 0
    NOTE: 143.1h of the window predates the first heartbeat row
```

Both `castellan.coverage.compute_polymarket_coverage` (the arithmetic core) and the CLI wrapper are covered by
tests (`harness/tests/test_coverage.py`, 6 tests: zero-data, exact-cadence-is-100%, gap detection against
hand-computed arithmetic, per-round deduplication, heartbeat epoch/failure reporting, `--since` windowing).

---

## 6. Risk of the migration itself

**The central, load-bearing mitigation: the laptop capture is never stopped by this migration, at any step, and
does not need to be.** Because the VPS writes to its own capture-only store rather than to `book/pit.db`, the
laptop's existing direct-write path and the VPS's satellite-then-merge path do not conflict — they can run
**permanently in parallel**. This changes the shape of the risk from "a cutover window where nothing is
capturing" to "two independent, non-conflicting capture sources, one of which (the laptop) was already running
and is explicitly instructed not to stop." Concretely:

- **If VPS provisioning fails or is delayed** (a bad droplet, `install.sh` erroring, a firewall issue) — zero
  coverage is lost beyond what the laptop's own sleep schedule already costs. The laptop is unaffected by
  anything happening on the VPS.
- **If the merge script has a bug** — `PITStore` is append-only and versioned; a bad merge can, at worst, insert
  an incorrect value or an unwarranted restatement event (caught and surfaced per §1's escalation path,
  never silently absorbed) — it cannot delete or silently overwrite existing true history. As additional
  insurance, `merge_polymarket_capture.py --dry-run` reports pending-merge counts without writing anything, and
  the existing `book/pit.db` snapshot-backup regime (D-001 §2, being scheduled under a separate, concurrent
  Rider B dispatch to this same seat) is the standing safety net before any real (non-dry-run) merge is run
  against the live store — **recommended practice: run a merge only after a recent snapshot exists**, not a
  requirement this document enforces in code.
- **What is lost if a poll is dropped mid-flight during the VPS's own setup** (e.g. the VPS is mid-`install.sh`
  when its timer would have fired) — nothing beyond that single 15-minute slot, and only on the VPS side; the
  laptop is still running its own independent schedule throughout.
- **What is NOT mitigated**: a merge cadence that is too infrequent leaves VPS-captured history sitting only on
  the VPS (a single box, no redundancy of its own beyond DigitalOcean's own infrastructure) for longer than
  ideal. The runbook (§7) recommends weekly pulls; more frequent is a config/operator choice, not a design
  limitation.

**Recommendation, stated plainly: do not disable the laptop launchd job as part of this migration.** Leave it
running as a free, already-paid-for (in the sense that it costs nothing further to keep it running) redundant
capture source. Whether to disable it later, once the VPS has a proven multi-week uptime record, is the
Principal's call and is explicitly out of scope for this dispatch (it involves the Principal's own machine, not
infrastructure this seat provisions) — this document does not recommend a timeline for it.

---

## 7. Cutover runbook

Ordered. **[PRINCIPAL]** marks every step this seat cannot execute under its scope limit (account creation,
spend, provisioning, or any transmission of firm files to an external host). **7 of 14 steps are
[PRINCIPAL].**

1. **[PRINCIPAL]** Create a DigitalOcean account if one does not already exist; add a payment method.
2. **[PRINCIPAL]** Create a Basic Droplet: **$6/month tier** (1 vCPU / 1 GiB RAM / 25 GB SSD), **Ubuntu 24.04
   LTS**, any region (the Polymarket API is not latency-sensitive at this cadence). Add the Principal's SSH
   public key at creation time — do not use a password.
3. **[PRINCIPAL]** Note the droplet's public IP. Confirm SSH access: `ssh root@<droplet-ip>`.
4. **[PRINCIPAL]** From a local checkout of this repository, push only what the VPS needs — never the full
   repo, never `book/`, `research/`, `logs/`, or `agents/`:
   ```
   rsync -avz --delete ./harness/ root@<droplet-ip>:/opt/castellan/repo/harness/
   scp -r ./deploy/polymarket-capture-vps root@<droplet-ip>:/opt/castellan/install
   ```
5. **[PRINCIPAL]** SSH in and run the install script as root:
   ```
   ssh root@<droplet-ip>
   bash /opt/castellan/install/install.sh
   ```
   This installs OS packages, creates an unprivileged `castellan` service user, builds a Python venv, installs
   the harness (base dependencies only — no `yfinance`/`ccxt`, which this path never needs), installs and
   enables the systemd timer (`castellan-polymarket-capture.timer`, 900s cadence, `Persistent=true` so a reboot
   catches up rather than silently waiting), and fires one verification poll immediately.
6. Verify end-to-end: `ssh root@<droplet-ip> bash /opt/castellan/install/health_check.sh` — expect timer
   active, last poll result `success`, low disk usage, and a coverage report against the VPS's own
   `pit_capture.db` showing at least one successful round.
7. **Let both hosts run in parallel for at least 48 hours** (spans a full weekday/weekend transition, the exact
   pattern that produced the 59.9-hour gap in §0). No action required during this window — this is
   observation, not a step.
8. After the parallel-run window, confirm the VPS's own coverage is materially higher than the laptop's over
   the same span: `ssh root@<droplet-ip> python3 /opt/castellan/repo/harness/scripts/report_polymarket_coverage.py --pit-db /opt/castellan/book/pit_capture.db`.
9. **[PRINCIPAL]** Pull the VPS capture store down to wherever this repo's `book/` lives:
   ```
   rsync -avz root@<droplet-ip>:/opt/castellan/book/pit_capture.db /tmp/pit_capture_pull.db
   ```
10. Dry-run the merge to see what is pending, then merge for real:
    ```
    python3 harness/scripts/merge_polymarket_capture.py --capture-db /tmp/pit_capture_pull.db --dry-run
    python3 harness/scripts/merge_polymarket_capture.py --capture-db /tmp/pit_capture_pull.db
    ```
    (Recommended: take a snapshot of `book/pit.db` first, per the existing/being-scheduled snapshot regime,
    before the first real merge — see §6.)
11. Confirm the merge landed cleanly: `python3 harness/scripts/report_polymarket_coverage.py` against
    `book/pit.db` should now show a materially higher combined coverage figure than §0's baseline. Check for
    any `RESTATED` count in the merge output — if nonzero, stop and escalate to Validation per §1's escalation
    path before proceeding further.
12. Establish a recurring pull-and-merge cadence — **recommended weekly**, at a Data & Infra working session
    (steps 9–11 repeated). Nothing in this design requires it to be more frequent; more frequent is a
    performance/staleness tradeoff the operator can tighten at will.
13. **[PRINCIPAL]** Decide, at leisure and not as part of this runbook, whether/when to disable the laptop
    `capital.castellan.polymarket-book.plist` job once the VPS has a proven track record. Not required, not
    recommended on any particular timeline by this document (§6).
14. Update the data dictionary entry for `source='polymarket-clob'` (already documented in
    `DATA-INFRA-001` §4) with a one-line pointer to this document once the merge cadence is running, so a
    future reader knows two hosts, not one, feed this source. (Left as a follow-up note, not performed in this
    document, since it belongs alongside a proven, running merge cadence rather than a planned one.)

---

## 8. What was built this session — file index

| File | What |
|---|---|
| `harness/castellan/loaders.py` | `record_capture_heartbeat` (new); `ingest_polymarket_books` now writes a heartbeat on every exit path; `_gamma_get` now retries transient failures (I-047) |
| `harness/scripts/capture_polymarket_book.py` | top-level crash safety net — any uncaught exception now still records a heartbeat before exit (I-047); heartbeat also written on the empty-universe path |
| `harness/castellan/coverage.py` | `compute_polymarket_coverage` — the coverage arithmetic core |
| `harness/scripts/report_polymarket_coverage.py` | the on-demand coverage reporter (dispatch item 5) |
| `harness/castellan/capture_merge.py` | `merge_capture_store` — the dual-writer merge mechanism (dispatch item 1) |
| `harness/scripts/merge_polymarket_capture.py` | the merge CLI, idempotent, watermarked |
| `deploy/polymarket-capture-vps/castellan-polymarket-capture.service` | systemd unit, one poll per firing |
| `deploy/polymarket-capture-vps/castellan-polymarket-capture.timer` | systemd timer, 900s cadence, `Persistent=true` |
| `deploy/polymarket-capture-vps/install.sh` | idempotent VPS provisioning script (run by the Principal, §7 step 5) |
| `deploy/polymarket-capture-vps/health_check.sh` | on-demand VPS health/coverage check |
| `harness/tests/test_polymarket_capture.py` | 9 tests: book parsing (two-sided/one-sided/empty), heartbeat on every exit path, `_gamma_get` retry |
| `harness/tests/test_coverage.py` | 6 tests: the coverage arithmetic |
| `harness/tests/test_capture_merge.py` | 6 tests: replay fidelity, idempotency, watermark, document dedup, restatement detection |
| `logs/ISSUE_LOG.md` | `I-047` (un-retried Gamma call, measured cause of real gaps, fixed), `I-048` (not-polled/no-quote schema gap, closed going forward, permanently open historically) |

**Harness suite: 139/139 → 160/160 passing** (21 new tests, 0 broken, verified immediately before this
document was finalized).

---

## 9. What remains unresolved

- **The historical ambiguity in §2/I-048 is permanent** — no future action closes it for capture before
  2026-08-04T16:53:16Z. Stated once here and in the Issue Log; not repeated as a caveat on every future
  coverage report, which instead reports the pre/post-heartbeat split mechanically.
- **No retention/rollup policy exists yet** for the VPS's capture-only store as it approaches its ~21-month
  disk ceiling (§3). Not designed this session — this seat's to build when the runway warrants it, well before
  the ceiling, not at it.
- **The merge cadence is a recommendation (weekly), not an enforced schedule.** Nothing in this design
  currently detects a merge that has not run in longer than expected — a natural extension of
  `health_check.sh` (compare the VPS capture store's most recent `knowledge_time` against the watermark
  recorded in `book/polymarket_merge_state.json`) that was not built this session, flagged for a future pass
  if the manual cadence proves unreliable in practice.
- **Universe size (5 liquid / 5 thin) is unchanged by this migration** — still not a researched optimum
  (`DATA-INFRA-001` §8), and the growth-rate arithmetic in §3 would need to be recomputed if it changes.

---

*Head of Data & Infrastructure · Castellan Capital · 2026-08-04*
*Design, runbook, and provisioning artifacts only. No account created, no spend, no infrastructure
provisioned, no firm data transmitted to any host. Not committed to git — the CIO commits.*
