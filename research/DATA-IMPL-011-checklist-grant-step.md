# DATA-IMPL-011 — the checklist's grant step, `funding-carry-conditioning-002`

**Seat:** Head of Data & Infrastructure · **Dispatch:** S4-D-013 · **Issue range:** I-310 … I-319
**Discharges:** I-247. **Edits:** `REGISTRATION-PAYLOAD-PREREG-002.md` §6 only (new item 7 + one note).
**Not done:** no `open_hypothesis` call, no register, no grant, no vault touch on `book/registry.db`.

## 1. The grant step, verbatim, as the sealer will type it

```python
from castellan.registry import TrialRegistry

reg = TrialRegistry("book/registry.db", allow_create=False)
C = <UTC calendar date ISO string, computed once, reused below and in vault.seal(cutoff=C)>
with reg.write_grant(
    reason="REGISTER_HYPOTHESIS", dispatch="<this seal's dispatch id>",
    token="<CASTELLAN_REGISTRY_WRITE token>",
) as reg:
    reg.open_hypothesis(
        family="funding-carry-conditioning-002", statement=..., mechanism=..., falsifier=...,
        universe=..., horizon=..., success_criteria=..., trial_budget=47,
        predecessor_family=None, holdout_classification="FORWARD", forward_window_start=C,
        forward_window_min_length=12.0, forward_kill_condition=..., model_prior_provenance=...,
        published_signal_haircut_applied=0.50, n_inherited=7,
    )
```

**Executed and verified** on a throwaway registry (schema-identical to the migrated `book/registry.db`
per `DATA-IMPL-010` — same `SCHEMA` constant, `write_grants`/`migration_watermark`/`dated_clauses`/
`grant_id` already in it), built via `TrialRegistry(path, allow_create=True)` bootstrap in scratchpad.
**Copying `book/registry.db` itself was denied by this session's permission layer** — noted, not
worked around; bootstrap is schema-equivalent and stated as the substitute. `open_hypothesis` returned
`None`; the block closed `outcome='CLEAN'`, `writes=3` (the three kinds `REGISTER_HYPOTHESIS` admits:
`open_hypothesis`, `log_event`, `register_dated_clause`); `hypotheses` gained exactly one row.

## 2. What the sealer sees

**Nothing, on success.** Neither `write_grant` nor `open_hypothesis` prints; both return silently.
This is the opposite of §4.7.4(ii)'s `evaluate_gate1` construction. Filed as **I-310, LOW** — not
repaired (a library change). The checklist supplies the missing report itself: after the block
closes, read `SELECT COUNT(*) FROM hypotheses WHERE family=?` (expect 1) and
`SELECT outcome, writes FROM write_grants ORDER BY grant_id DESC LIMIT 1` (expect `CLEAN`, `3`).

## 3. What the sealer sees on failure — verified, each on the throwaway registry

| Condition | Exception |
|---|---|
| `open_hypothesis` called with no grant open | `RegistryWriteNotGrantedError` |
| Grant open but its `reason` doesn't admit `open_hypothesis` (e.g. `LOG_TRIAL`) | `RegistryWriteNotGrantedError`, names the admitting reasons |
| `write_grant(reason=...)` outside the closed vocabulary | `RegistryWriteGrantMalformedError` |
| No `token=` and `CASTELLAN_REGISTRY_WRITE` unset | `RegistryWriteNotGrantedError` |
| A second `write_grant` opened while the first is still open, same registry object | `RegistryWriteGrantNestedError` (R-7) |

**On every one of these the block rolls back — including a successful `open_hypothesis` that already
ran earlier in the same block.** Verified directly: opening a second grant *after* a successful
`open_hypothesis` inside the first destroys the registration; it does not survive. Filed **I-311,
HIGH** — the exact shape produced by calling the vault seal from inside the hypothesis grant.

## 4. Ordering — the vault seal sits outside the grant block, never inside

`HoldoutVault.seal()` opens its own `write_grant(reason="VAULT_SEAL", ...)` internally. Grants do not
nest (R-7). If item 6's vault seal is called while item 7's block is still open, it raises
`RegistryWriteGrantNestedError` and **rolls back the hypothesis registration with it** — confirmed
above. Sequence: close item 7's block first, then call `vault.seal(..., cutoff=C, ...)` with the
identical `C`, same session, same UTC day (C8). Filed **I-312, HIGH** — I-247 is discharged only by
the grant step *and* this ordering together; the grant step alone still permits I-311's failure.

## 5. The six existing items against the migrated schema

None is false on the migrated file. Item 2's `SELECT COUNT(*)` is a read — reads need no grant and
are unaffected by the new `grant_id` columns. Items 3/4 are literal checks, unaffected. Item 5's
check (forward_window_start = call day = vault cutoff) is unchanged; only its execution context moved
(now inside item 7). Item 6's check is unchanged; only its sequencing relative to item 7 is new (§4).
**No item is repaired. §6 gets item 7 plus a note — see the payload edit.**

## 6. Snapshot regime SLA — one paragraph, not built

The snapshot regime's SLA is not compatible with a host the firm has ruled may sleep. S2-D-033's
"integrity witness" reclassification was correct for capture, where a gap means the witness noticed
less, but wrong for the snapshot job, where a gap means the backup of record — `book/pit.db` at 1.58
GB, gitignored, and `book/registry.db`, about to hold the firm's first hypothesis — has no second copy
for as long as the host sleeps; one ruling covered two different failure semantics (I-323, already
filed, HIGH). The nine-day gap shows the *detection* works (the Friday health check caught it) but the
*regime* does not: best-effort is not a recovery-point-objective. Cheapest fix, not built here: point
the same job at the VPS (Rider A's host), which already runs a systemd timer with `Persistent=true`
and does not sleep, and keep the laptop's job as a second copy rather than retiring it — one cron
line, no new architecture decision beyond what I-323 already names.

## 7. State at close

`book/registry.db`: **0 hypotheses / 0 trials**, unchanged, not touched this dispatch.
`write_grants`: **1 row** (`grant_id=1`, MIGRATION, CLEAN — unchanged from `DATA-IMPL-010`).
Throwaway registry: scratchpad only, discarded, never touched `book/registry.db`.

## 8. Issues filed

| # | Sev | Finding |
|---|---|---|
| I-310 | LOW | `write_grant`/`open_hypothesis` print nothing on success; §4.7.4(ii)'s doctrine unmet by the library — checklist item 7's read-back compensates, not repaired here |
| I-311 | HIGH | A grant opened inside an already-open one rolls back the *whole* outer block, including a prior successful `open_hypothesis` — silent loss if the vault seal is called from the wrong place |
| I-312 | HIGH | I-247 needs the grant step *and* the ordering rule together; the grant step alone still permits I-311 |
| I-313–I-319 | — | unused |

## 9. Line budget — OVERRUN, flagged

Comparator `DATA-IMPL-010`: 63 lines [measured, `wc -l`]. Projection: ~50. **Measured, this document:
114 lines [`wc -l`] — roughly 2.3× the projection.** The overrun is real, not padding: it is carried
by three independently-verified failure modes (grant absence, wrong reason, malformed reason, missing
token, nesting) each demonstrated rather than asserted, the ordering finding in §4 (which is the part
of I-247 the grant step alone does not close), and the one required SLA paragraph. Cutting any of
these to hit ~50 would mean asserting a failure mode without having run it, which is the exact defect
this dispatch exists to avoid. Flagged rather than trimmed.

## 10. Files

- `research/REGISTRATION-PAYLOAD-PREREG-002.md` — §6 edited (new item 7, one dated note); nothing else touched
- `research/DATA-IMPL-011-checklist-grant-step.md` — this document
- Throwaway registry (verification only): `/private/tmp/claude-501/-Users-<user>-projects-castellan-capital/ee1a62b4-d951-402b-af49-9859bfe02074/scratchpad/registry_throwaway.db` — scratchpad, not committed, not under `book/`
