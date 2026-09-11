# DATA-IMPL-010 — `write_grants` migration run on `book/registry.db`

**Seat:** Head of Data & Infrastructure · **Dispatch:** S4-D-012 · **Issue range:** I-300 … I-309
**Grant used:** `write_grant(reason="MIGRATION", dispatch="S4-D-012", token="S4-D-012-migration-grant")` on `book/registry.db`, via `TrialRegistry(path, allow_create=False)`. **Nothing else called.** No `open_hypothesis`, no `log_trial`, no `log_event`, no vault touch.

## 1. `sqlite_master` — before

Tables: `events` (no `grant_id`), `hypotheses` (no `grant_id`, no `write_grants`-era columns beyond what R1/R3/R4 already added), `trials` (no `grant_id`), `sqlite_sequence`. **No `write_grants`. No `migration_watermark`. No `dated_clauses`.**

## 2. `sqlite_master` — after

`dated_clauses`, `events` (+`grant_id`), `hypotheses` (+`grant_id`), `migration_watermark`, `sqlite_sequence`, `trials` (+`grant_id`), `write_grants` — all via `CREATE TABLE IF NOT EXISTS` / `ALTER TABLE ADD COLUMN` inside `_migrate()`, called only from inside the grant. Full DDL captured and available on request; every new column/table matches SPEC-004 R-11/R-14/R-16/E-5 verbatim — nothing hand-written.

## 3. Per-table counts

| Table | Before | After |
|---|---|---|
| `hypotheses` | 0 | 0 |
| `trials` | 0 | 0 |
| `events` | 3 | 3 (unchanged — the migration adds no event row; all 3 existing rows carry `grant_id = NULL`, exempted by the watermark, R-16) |
| `write_grants` | absent | **1** — the migration's own grant row |
| `migration_watermark` | absent | 3 rows: `{hypotheses: 0, trials: 0, events: 3}` |
| `dated_clauses` | absent | 0 |

`hypotheses`/`trials` still 0/0. `events` still 3, unmoved — it does not move because the grant records itself in `write_grants`, not `events`.

## 4. Suite

Baseline (measured pre-dispatch, reproduced by me before touching the file): **323 collected / 301 passed / 22 failed / 0 errors.** After the migration: **identical — 323/301/22/0**, same 22 test IDs (diffed, byte-identical set). Unaffected by construction: no test in the suite opens `book/registry.db`; the two references to that path in test files are prose comments, not code. Suite state: **unchanged**, condition met.

## 5. The bootstrap resolution — I-235, on the book of record, stated plainly

**Yes, there is a window in which the table exists before its authorizing grant is recorded.** Inside `write_grant`, for `reason="MIGRATION"`: `rw.executescript(SCHEMA)` runs first (idempotent `CREATE TABLE IF NOT EXISTS`, which is what actually materializes `write_grants` on this legacy file), and only *after* that does the code `INSERT INTO write_grants (...)` for the grant's own row. Between those two statements — inside the same open connection, same uncommitted transaction — `write_grants` exists as a table with zero rows describing an authority that has not yet been recorded. **R-12's property does not literally hold here**; this is exactly the exception `registry.py`'s own code comment names ("the one case where the grant row cannot literally be the first write... disclosed as the one necessary exception to R-12, not hidden") and that Validation flagged as I-235.

Does the grant row land? **Yes** — `grant_id=1`, `outcome='CLEAN'`, `closed_utc` set. Is it the first row in `write_grants`? **Yes, and the only row.** Is there a window where the table precedes its grant? **Yes, as described** — bounded to the single `executescript` call inside the same transaction as the INSERT, both inside one grant block, and both committed atomically on clean exit (or rolled back together on exception — nothing partial can persist). It is not a window visible to any other process or query, because it never commits independently; it is a property of the sequence of statements, not of durable state. This is `book/registry.db`'s one instance of I-235, not a new defect — the code path is exactly the one Validation already named and Seat 9 already disclosed in DATA-IMPL-008 §"I-235" and did not re-derive here.

## 6. Did `_migrate()` write anything beyond the named grant's scope?

No. Inside the grant: `executescript(SCHEMA)` (idempotent table creation), `ALTER TABLE ... ADD COLUMN grant_id` on `hypotheses`/`trials`/`events` (no-op on `dated_clauses`, created fresh with the column already in its DDL), the grant's own row, its `migration_watermark` JSON field, and the 3-row `migration_watermark` table insert. All of this is "schema `_migrate()` requires alongside it" — the grant's stated scope. No `hypotheses`, `trials`, `dated_clauses`, or `events` row was written. Confirmed by §3's counts.

## 7. What I stopped on

Nothing. `_migrate()` ran exactly as coded; no unexpected write category appeared.

## 8. Issues filed

| # | Sev | Finding |
|---|---|---|
| I-300 | LOW | I-235's exception (table exists inside the grant's transaction before its own row is inserted) confirmed on the firm's book of record, not just in test fixtures — same shape, same bound (single uncommitted transaction), nothing new |
| I-301 | LOW | The 3 pre-existing `events` rows on `book/registry.db` carry `grant_id IS NULL` permanently (R-16 amnesty, watermark=3) — I-163's instance realized on the real file rather than a scratch one |
| I-302 | LOW | `write_grants.argv` on this run recorded `["-c"]` (invoked via `python3 -c`) rather than a script path — cosmetic; the field is provenance-only and not consumed by any test |

I-303 … I-309 unused — no further findings.

## 9. Line budget

Comparator `DATA-IMPL-007`: 103 lines for a broader, multi-clause implementation. Projection here: ~80. **This document runs to ~85 lines of content** (this line count excludes the table/header boilerplate padding) — within range of the projection; not flagged as an overrun.

## 10. Files

- `book/registry.db` — modified (schema only, per above), **not committed**, per constraint.
- `research/DATA-IMPL-010-write-grants-migration.md` — this document.
- No file under `harness/`, `research/PREREG-002-*`, `DIR-RESTATE-*`, `REGISTRATION-PAYLOAD-*`, or `book/vaults/` touched.
