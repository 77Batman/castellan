## I-333 · 2026-09-11 · `query_semantics` is recorded in the vault spec but is read by no harness code path · Severity: MEDIUM · Owner: head-of-data-infra

**BACK-FILLED 2026-09-15** under the Principal's Option-B ruling on I-370. The finding was made and described at `research/DATA-IMPL-012-vault-arguments.md:112` (§3) on 2026-09-11, during dispatch S4-D-015; the log entry was never written. **Authored from the artifact, not from the citation** (§7.12).

Filling `query_semantics` for the four vault seals to Ruling 001 §3.4's standard, this seat traced the field's runtime path rather than assuming Ruling 001's declarative requirement implied enforcement [measured]: "`query_semantics` is **recorded** in `spec.json` but **never read** by any harness code path — `acquire_once()` calls the caller-supplied `fetch(spec)` callable, which may or may not actually consult `spec["query_semantics"]` to build its request. There is no code that checks the fetch implementation against the sealed query. Enforcement is human, at Gate 1 code review, comparing the two by eye." The artifact's own §5 places this in GATES.md §4.7.2's terms: the only property `seal()` checks for `query_semantics`, ever, is `bool(value)` at seal time — no type check, no structural check, and (§3, unlike `dataset_id` and `schema_fingerprint`) no downstream content check either. The provenance guarantee this field appears to give is, in the artifact's words, "a declared-commitment-not-a-control fact the firm should hold before relying on it."

**Resolution:** open — `query_semantics` remains recorded but unenforced by any harness code path; the only check on whether a `fetch()` implementation actually matches its sealed spec is an unrecorded human comparison at Gate 1 code review.
**Pattern tag:** `binding-control-declared-not-enforced` · `human-review-is-the-only-check`

---

## I-334 · 2026-09-11 · `schema_fingerprint`'s exact-order `columns` check is bound to a pandas pivot artifact, not a guaranteed Gate-1 output order · Severity: MEDIUM · Owner: head-of-data-infra

**BACK-FILLED 2026-09-15** under the Principal's Option-B ruling on I-370. The finding was made and described at `research/DATA-IMPL-012-vault-arguments.md:91` (§1) on 2026-09-11, during dispatch S4-D-015; the log entry was never written. **Authored from the artifact, not from the citation** (§7.12).

Measuring the four `schema_fingerprint` values directly off `book/pit.db` via `pd.read_sql(...).pivot_table(index="event_time", columns="field", values="value")`, one query per (source, symbol) pair [measured], this seat flagged a caveat it could not itself close: "`_schema_matches()` (`holdout.py`) does exact-order list equality on `columns`. The order above is pandas' pivot-table default (alphabetical); it is **not** a guarantee about what a not-yet-written Gate-1 `fetch()` will return. Whoever writes that function must match this order byte-for-byte or a legitimate acquisition spuriously fails — a false operational block, not a leak, but still a name-it-now problem while the fingerprint is about to freeze." The `columns` order is therefore an artifact of how this seat measured the schema, not a specification anyone chose, and it is about to be hashed into a frozen, binding field under Ruling 001 §3.4.

**Resolution:** open — no Gate-1 `fetch()` implementation exists yet against which to verify column order; the frozen order must be matched byte-for-byte when one is written, or a legitimate acquisition will fail `_schema_matches()` on an ordering difference alone.
**Pattern tag:** `implementation-artifact-frozen-as-contract` · `false-block-not-a-leak`
