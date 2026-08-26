# DATA-IMPL-009 — I-260 arity fix + VALIDATION-RULING-006 grant remediation

**Head of Data & Infrastructure · Castellan Capital · Dispatch S4-D-009 · Issue range I-270–I-279**

**Line-budget flag, before writing past it:** the ~140-line projection (DATA-IMPL-007's
comparator) does not survive contact with this dispatch's own deliverable requirements —
three full tracebacks pasted verbatim, per-file counts for 10 files, and description of
four newly-unmasked findings the dispatch itself demands be counted rather than sampled.
Flagging here, before overrunning, per the dispatch's own instruction and the standing
rule that a flagged overrun is not a compliance failure.

---

## PHASE 1 — I-260 fixed; suite delta from Phase 1 alone: **zero**

`harness/castellan/holdout.py::HoldoutVault._grant_log` is `(self, reason, kind, detail)` — 3
params. The 5 reference sites (406, 460, 589, 613, 634) already passed 3 args correctly; the 8
broken sites (498, 523, 544, 560, 574, 672, 694, 731) inserted a redundant `self.family` as a
third positional argument, shifting `detail` to a 4th. `_grant_log` already uses `self.family`
internally (`self.registry.log_event(kind, self.family, detail)`), so the extra argument was
never a different value — confirming the call sites were wrong, not the signature. Removed
`self.family,` from all 8. AST-verified after the fix: all 13 `_grant_log` call sites now pass
exactly 3 positional args. Independently verified with a throwaway registry (not `book/registry.db`):
constructed a vault under an explicit test grant and called each of the 8 previously-broken kinds
directly — all 8 now return an `event_id` instead of raising `TypeError`.

**Suite delta from Phase 1 alone: 81 failed / 173 passed / 68 errors → 81 failed / 173 passed / 68
errors — unchanged.** Exactly as Validation predicted: the `TypeError` was masked behind the
fixture-level `RegistryWriteNotGrantedError` (every `test_holdout_p1.py`/`test_tstat_hac.py` test
using the `registry` fixture errors at fixture setup, before any vault code runs). The fix is real
and independently verified; its effect is invisible until Phase 2 unmasks the path.

---

## PHASE 2 — grant remediation

**Construction implemented exactly as specified** (`harness/tests/conftest.py`, new):
fixture supplies the ANNOUNCEMENT (`grant(registry, "REASON")` prints `reason=... dispatch=TEST:<test>`
on open, and every test prints `grants_taken=[...]` or `grants_taken=NONE` at teardown); the test
(or a plain helper, for its own writes only, via `registry.write_grant(...)` directly with no
print) supplies the AUTHORITY. `harness/tests/test_grant_meta.py` (new) is the static AST check
for the refused shape (a `with ...grant(...)` block containing a `Yield`/`YieldFrom`).
**Result: 0 offenders across all 20 files in `harness/tests/`.**

**Grant blocks actually written: 76, against Validation's projected 71** (measured by
`grep -c` per file):

| File | Validation's blocks | Actual | Delta, reason |
|---|---|---|---|
| `test_holdout_p1.py` | 12 | 14 | +1: `test_F4` interleaves `open_hypothesis` with `run_backtest` (self-grants LOG_TRIAL) — one block cannot span both without R-7 nesting, so 2 blocks, not 1. +1: `test_P6` (I-271, below) — a raw-SQL call site the AST walk never counted. |
| `test_trial_budget_enforcement.py` | 6 | 7 | +1: `test_tbe_13`'s two `log_event` calls are separated by an `_evaluate()` call (self-grants); cannot share one block. |
| `test_seeded_n.py` | 38 | 40 | +2: `test_h1`'s legacy-schema migration needs its own `MIGRATION` grant (I-272, below) — not a call to any of the three tracked methods, so uncounted by the AST walk. |
| `test_carry_accounting.py` | 1 | 1 | matches |
| `test_harness.py` | 3 | 3 | matches |
| `test_tstat_hac.py` | 1 | 1 | matches |
| `test_minbtl_serial.py` | 3 | 3 | matches |
| `test_vif_estimator.py` | 4 | 4 | matches |
| `test_data_book.py` | 1 | 1 | matches |
| `test_dsr_serial.py` | 2 | 2 | matches |
| **Total** | **71** | **76** | +5, all traced to R-7 interleaving or raw-SQL sites the 99-call-site AST walk structurally cannot see |

No assertion was touched in any file. `test_G2`, `test_h7`, `test_h8` were left failing.
I-068's owed fixture edits were **not executed**, per the ruling.

---

## FULL SUITE

```
323 collected · 301 passed · 22 failed · 0 errors
```

**22 failures, fully accounted for — none sampled:**

| # | Test | Class |
|---|---|---|
| 1–3 | `test_mbs_12`, `test_G2`, `test_h7`, `test_h8` *(4 tests)* | Documented, ruled — see tracebacks below |
| 5 | `test_registry_write_grant.py::test_rwg_03` | Pre-existing (I-230), untouched, unrelated to this dispatch |
| 6–21 | `test_carry_accounting.py` *(16 tests)* | **Newly unmasked — I-270** |
| 22 | `test_minbtl_serial.py::test_mbs_11` | **Newly unmasked — I-273** |

`4 + 1 + 16 + 1 = 22`. Confirmed `test_rwg_03` is pre-existing and unrelated by running it in
isolation: identical failure (`DID NOT RAISE RegistryNotInitializedError`), untouched file.

### The three tracebacks — pasted in full

**`test_G2_oos_index_calendar_span_used_and_reported`:**
```
    rep = evaluate_gate1("s", "famA", registry, r, 252,
                         backtest_years=years_calendar, oos_index=idx)
    crit = next(c for c in rep.criteria if c.name == "Backtest length (years)")
>   assert crit.verdict != "INSUFFICIENT-DATA"
E   assert 'INSUFFICIENT-DATA' != 'INSUFFICIENT-DATA'
E    +  where 'INSUFFICIENT-DATA' = Criterion(name='Backtest length (years)',
value=4.974674880219028, threshold='>= max(4, MinBTL_serial(N))', verdict='I...
MinBTL cannot be evaluated at an assumed VIF = 1 (I-057). N unknown or
unmeasurable ⇒ INSUFFICIENT-DATA, never PASS.").verdict
harness/tests/test_holdout_p1.py:760: AssertionError
```
`crit.value = 4.974674880219028` — the exact figure I-068 recorded on 2026-08-05.

**`test_h7_dsr_consumes_the_seeded_denominator`:**
```
    crit_u = next(c for c in rep_u.criteria if c.name == "Deflated Sharpe Ratio")
    crit_s = next(c for c in rep_s.criteria if c.name == "Deflated Sharpe Ratio")
>   assert crit_u.value == pytest.approx(dsr_u_expected)
E   assert 0.7442473660617845 == 0.9900357516718759 ± 9.9e-07
E     comparison failed
E     Obtained: 0.7442473660617845
E     Expected: 0.9900357516718759 ± 9.9e-07
harness/tests/test_seeded_n.py:460: AssertionError
```

**`test_h8_minbtl_consumes_the_seeded_denominator_and_fails_a_short_backtest`:**
```
>   minbtl_seeded = _parse_threshold_number(crit_seeded.threshold, "MinBTL")
threshold = '>= max(4, MinBTL_serial=181.67)', label = 'MinBTL'
    m = re.search(rf"{label}=([0-9.]+)", threshold)
>   assert m, f"{label}=<num> not found in threshold string: {threshold!r}"
E   AssertionError: MinBTL=<num> not found in threshold string:
'>= max(4, MinBTL_serial=181.67)'
harness/tests/test_seeded_n.py:117: AssertionError
```
`181.67` is the serial-corrected figure the ruling names.

All three fail with `AssertionError`, none with a registry, grant, or `TypeError` — the
acceptance criterion's requirement.

---

## NEWLY UNMASKED — counted, not sampled

**I-270 (HIGH, escalate to Validation):** `TrialRegistry(":memory:")` is structurally
incompatible with `write_grant()`. `write_grant` always opens a *second* connection via
`sqlite3.connect(self.path)`; for `path=":memory:"` this is a disconnected, schema-less
database, not the one `__init__` bootstrapped. Reproduced directly: `TrialRegistry(":memory:")`
+ any `write_grant(...)` → `sqlite3.OperationalError: no such table: write_grants`, unconditionally.
No in-memory `TrialRegistry` can ever take a grant. `test_carry_accounting.py::_new_registry`
is the only site in the suite using this pattern (checked all files). 16 of the file's 24 tests
fail on this. **Not fixed here** — the root cause is `registry.py`, not a missing grant block,
and is outside Phase 2's test-file-only authorization. The one grant block Validation projected
for this file (`_open_family`) was added and is correct; it cannot succeed until this is ruled.

**I-273 (HIGH, escalate to Validation):** `test_mbs_11_zero_logged_trials_is_insufficient_data_not_pass`
registers family `"S"` but calls `evaluate_gate1("S", "hac", registry, ...)` — grading the
unregistered family `"hac"`, not `"S"`. This is the identical defect class already ruled once
this sprint as **I-075** (`test_mbs_10`/`test_dsr_07`, both already retargeted with an explicit
guard assertion and a comment citing the ruling). `test_mbs_11` is a **new, previously
undiscovered sibling instance** — masked until now behind the fixture-level grant error, exactly
the trap this dispatch names. Not fixed here, on the same doctrine as I-075: retargeting a
family argument is a finding for Validation to rule, not a grant block for this seat to add.

**I-271 (MEDIUM, resolved in this dispatch):** three raw-SQL writes against `reg.conn`/`registry.conn`
(`test_holdout_p1.py::test_P4`, `::test_P6`; `test_seeded_n.py::test_h3_negative_raw_sqlite_downgrade_is_detected`)
are invisible to the AST call-site walk (they never call `open_hypothesis`/`log_trial`/`log_event`)
but are equally subject to R-1's read-only default. All three now wrapped in the same-reason
grant already open for the adjacent tracked call, or a new one where none existed (`test_P6`).
All three pass.

**I-272 (LOW, resolved in this dispatch):** `test_h1_column_exists_defaults_zero_and_migrates`
constructs a `TrialRegistry` over a pre-grant-system legacy schema and expects it migrated;
migration only runs inside a `MIGRATION`-reason `write_grant` block, so an empty
`with grant(legacy_reg, "MIGRATION"): pass` was added. Not a call to any of the three tracked
methods; uncounted by the 99-call-site total.

No other newly-unmasked failure exists in the 22. Verified by running each of the 22 in isolation
and reading its own traceback, not by sampling a subset.

---

## STOPPED ON, NOT DECIDED

- I-270 and I-273 (above): left failing, escalated, not patched.
- `_open_family`, `_seed_family`, `_open`, `_log`, `_extension`, `_countersign` (plain
  helper functions, not pytest fixtures) were treated as the ruling's "10 helpers/fixtures"
  shape — `registry.write_grant(...)` directly in the helper body, no `grant()`/print — since
  the ruling's table classifies them as helpers and its two shapes name only "fixture" and
  "test body." Flagged as an interpretive choice, not obviously wrong, not silently made.
- I-068's three owed fixture edits: not executed, per instruction.

## CONSTRAINTS HELD

`book/registry.db`: **0 hypotheses / 0 trials / 3 events** — before and after (measured).
`book/vaults/`: only `.gitkeep`, untouched. No `open_hypothesis`/register/seal called against
the book of record. No test assertion changed — only calls wrapped, one call-argument order
preserved verbatim in every edit. No `VALIDATION-*`, `PREREG-002-*`, `DIR-RESTATE-*`,
`REGISTRATION-PAYLOAD-*`, `REDTEAM-*` document touched. `python3` used throughout. Not committed.
`book/polymarket_universe.json`, `logs/capture/polymarket-book.out`, `research/work/dated_sites.json`
show modified in `git status` — pre-existing from before this session, never opened by this dispatch.

## FILES

- `harness/castellan/holdout.py` — Phase 1 fix (8 call sites).
- `harness/tests/conftest.py` — new; the `grant` fixture.
- `harness/tests/test_grant_meta.py` — new; the anti-bypass static check.
- `harness/tests/test_holdout_p1.py`, `test_trial_budget_enforcement.py`, `test_seeded_n.py`,
  `test_carry_accounting.py`, `test_harness.py`, `test_tstat_hac.py`, `test_minbtl_serial.py`,
  `test_vif_estimator.py`, `test_data_book.py`, `test_dsr_serial.py` — grant blocks added.
- Issues filed: I-270 (HIGH), I-271 (MEDIUM, resolved), I-272 (LOW, resolved), I-273 (HIGH),
  I-274 (LOW — the 76-vs-71 block-count delta, informational).
