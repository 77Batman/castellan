# DATA-IMPL-003 — seeded `n_inherited`, the H-series landed

**Seat:** Head of Data & Infrastructure (Seat 9) · **Date:** 2026-07-29
**To:** the CIO · cc Validation
**Work order:** `research/VALIDATION-GATE0-001-forward-lag.md` §3 (H-1 … H-14), the
`FamilyStats` contract at §3.0. Implements I-027 / C1 on `PREREG-001`. Fixes I-036
by re-doing the H-series clean, tests-before-implementation, in an isolated
worktree.

**Environment note.** The installed editable `castellan-harness` package initially
resolved to the main repo tree (`pip show` showed `Editable project location:
.../castellan-capital/harness`), not this worktree — a leftover from whichever
session last ran `pip install -e harness` outside a worktree. Running the test
suite before re-installing would have silently exercised the wrong source tree.
Re-ran `pip install -e harness` from inside this worktree before doing anything
else; `python3 -c "import castellan; print(castellan.__file__)"` then confirmed
resolution to this worktree. Filing this as a process note rather than an Issue
Log entry (nothing wrong was measured under the stale binding — it just had to be
fixed before step 1 could mean anything) — the CIO may want a standing instruction
that every worktree re-installs the harness before its first test run.

---

## 1. The binding rider, satisfied — verbatim red output

Sequence actually followed: transcribed H-1 … H-14 into
`harness/tests/test_seeded_n.py` from Validation's prose specification, changing
none of the named assertions; ran the file against the **unmodified** source
(`registry.py`, `gates.py`, `__init__.py` all at HEAD, confirmed via `git status`
— clean worktree at task start, matching the post-I-036-cleanup state at commit
`cfc508a`); recorded the failure; only then implemented.

```
$ python3 -m pytest harness/tests/test_seeded_n.py -q --no-header
==================================== ERRORS ====================================
___________________ ERROR collecting tests/test_seeded_n.py ____________________
ImportError while importing test module '/Users/.../harness/tests/test_seeded_n.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/Library/Frameworks/Python.framework/Versions/3.13/lib/python3.13/importlib/__init__.py:88: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
harness/tests/test_seeded_n.py:27: in <module>
    from castellan import (
E   ImportError: cannot import name 'InheritedCountDoubleCountError' from 'castellan' (/Users/.../harness/castellan/__init__.py)
=========================== short test summary info ============================
ERROR harness/tests/test_seeded_n.py
!!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
1 error in 0.91s
```

**Reading this honestly.** It is a collection-time `ImportError`, not nineteen
individual assertion failures — the test module references
`InheritedCountDoubleCountError` (needed for H-5b) at import time, and that name
did not exist anywhere in unmodified `castellan`, so pytest could not even build
the 19 test functions. This is still a genuine, unweakened RED: **zero of the
nineteen transcribed test functions passed, ran, or were even collectible against
the pre-implementation source.** None of them is the "test that passes before the
feature exists" the rider warns about — the opposite failure mode (nothing runs at
all) is the maximally strong form of RED available here, and I did not manufacture
a softer per-test failure to produce a longer log. Full output preserved at
`/tmp/h_series_red_output.txt` in this worktree's scratch area (not committed;
reproduced verbatim above).

After implementation, the same file: **19 passed** (`python3 -m pytest
harness/tests/test_seeded_n.py -q` → `19 passed`).

---

## 2. Full suite — final numbers

```
$ python3 -m pytest harness/tests -q
........................................................................ [ 62%]
...........................................                              [100%]
115 passed in ~8s
```

**115 passed, 0 failed, 0 skipped, 0 xfail.** 96 pre-existing + 19 new (H-series).
Verified with `-rA` that no skip/xfail markers are present anywhere in
`harness/tests/` (`grep -rn "skip\|xfail" harness/tests/*.py` → none).

---

## 3. `FamilyStats` contract (§3.0) — implemented as specified

```python
FamilyStats(family, n_trials, n_inherited, n_logged, trial_budget,
            sr_period_std, sr_period_mean, sr_period_best)
```

`n_trials = n_inherited + n_logged`; `n_inherited` sums each family's own declared
seed transitively across `predecessor_family` (never re-declared by a successor —
enforced at registration, not just at read time); `n_logged` is the real
`COUNT(*)` across the chain, exactly as before. `sr_period_std/mean/best` are
computed from real trials' `sr_period` values only — this part of `family_stats`
is **unchanged** from the pre-existing code, which already queried only the
`trials` table. Field order matches §3.0 exactly; the only positional constructor
call site (`registry.py`, inside `family_stats`) was updated to match.

Files touched: `harness/castellan/registry.py`, `harness/castellan/gates.py`,
`harness/castellan/__init__.py`. New: `harness/tests/test_seeded_n.py`. Nothing
else — no data fetched, no backtest run, no vault sealed, no hypothesis
pre-registered against `book/registry.db` (verified after: still 0 hypotheses, 0
trials, 1 event, `git status --porcelain book/` empty).

---

## 4. Each H-case — the change and the test proving it

| # | Test | What changed | Cleared |
|---|---|---|---|
| H-1 | `test_h1_column_exists_defaults_zero_and_migrates` | `SCHEMA` gets `n_inherited INTEGER NOT NULL DEFAULT 0`; `_migrate()` gets the same as an `ALTER TABLE` addition (idempotent — skips if the column already exists). Verified against a DB built from the **pre-change SCHEMA literal** (copied verbatim into the test) with one hypothesis row: opening it raises nothing and the pre-existing row reads `0`. | Yes |
| H-2 | `test_h2_value_is_validated` | `open_hypothesis` gains `n_inherited: int = 0`, validated: not-int (incl. `bool`) or negative → `ValueError`. `3.7` (a `float`, not an `int`) is refused by the `isinstance` check; `-1` by the range check; `0` and `31250` accepted and round-trip. | Yes |
| H-3a | `test_h3_n_inherited_is_binding_and_changes_the_hash` | `n_inherited` added to `_BINDING_FIELDS`. Two families differing only in `n_inherited` hash differently; the `hypothesis_sealed` shadow copy carries the declared value. | Yes |
| H-3b | `test_h3_negative_reregistration_with_different_n_inherited_is_refused` | No new code — falls out of H-3a: `_BINDING_FIELDS` already drives the P3 amendment-refusal path generically. Re-call with a different `n_inherited` raises `PreRegistrationAmendedError`, logs `hypothesis_amendment_refused` naming `n_inherited`; byte-identical re-call is silent, as before. | Yes |
| H-3c | `test_h3_negative_raw_sqlite_downgrade_is_detected` | Same generic mechanism (P4/`verify_prereg`). A raw `UPDATE hypotheses SET n_inherited=0` is caught by hash mismatch, named in `differing_fields`, and fails `evaluate_gate1`'s "Pre-registration integrity" criterion. | Yes |
| H-4 | `test_h4_n_trials_is_seeded_plus_logged` | `family_stats` computes `n_inherited` (summed from the `hypotheses.n_inherited` column across the chain) and `n_logged` (the old `COUNT(*)`) separately, then `n_trials = n_inherited + n_logged`. | Yes |
| H-5a | `test_h5_transitive_sum_across_chain_no_double_count` | The same summation loop walks `predecessor_chain(family)`, so `n_inherited` sums transitively (A=1000, B=+50, C=+0 → C sees 1050) while a predecessor's own stats (`family_stats("A")`) are unaffected by successors. Exact equality asserted, not `>=`. | Yes |
| H-5b | `test_h5_negative_successor_redeclaring_the_chain_is_refused` | New `InheritedCountDoubleCountError` and a guard in `open_hypothesis`: if `predecessor_family` is set and the predecessor chain's own `n_trials` is `> 0`, a declared `n_inherited >= chain_total` is refused before the row is written. This is the D-011 §3 / I-031 non-overlap restatement of KC-001 clause 3, mechanised — not a seat's interpretation of the clause, a direct implementation of the Principal's own restated wording. | Yes |
| H-6a | `test_h6_sigma_sr_uses_logged_trials_only` | No change — the `srs` query in `family_stats` already read only from `trials.sr_period`; verified `sr_period_std/mean/best` come from exactly the 2 logged values, not the seeded 31,250. | Yes |
| H-6b | `test_h6_negative_no_phantom_rows_are_synthesised` | No change — nothing in the implementation writes to `trials` except `log_trial`, which is untouched. `COUNT(*) FROM trials` stays `0` then `2` for a family seeded at 31,250; `returns_matrix(...).shape[1] == 2`. | Yes |
| H-6c | `test_h6_negative_one_logged_trial_gives_no_dispersion` | No change to the `len(srs) >= 2` gate. With 1 logged trial, `sr_period_std is None` and `evaluate_gate1`'s DSR criterion reads `INSUFFICIENT-DATA`. | Yes |
| H-7 | `test_h7_dsr_consumes_the_seeded_denominator` | No new DSR code — `dsr = stats.deflated_sharpe_ratio(r, fam.n_trials, fam.sr_period_std)` already used `fam.n_trials`; correctness follows entirely from `family_stats` now returning the seeded total. Twin families with identical trials and an identical candidate return series: unseeded `DSR ≈ 0.99` (PASS), seeded (`N=31,252`) `DSR ≈ 0` (FAIL) — the verdict flips, not just the number. | Yes |
| H-8 | `test_h8_minbtl...` | Same story as H-7 for the length criterion — `minbtl = stats.min_backtest_length_years(max(fam.n_trials, 2), sr_ann, periods_per_year)` was already wired to `fam.n_trials`. A 4.00-year-exact `oos_index` at net SR ≈ 1.0: seeded family's threshold string reads `MinBTL=17.0x` (parsed and checked within ±0.05 of 17.06) and **FAILs**; the unseeded twin (`N=2`, `MinBTL≈0.27`) **PASSes**. | Yes |
| H-9 | `test_h9_pbo_is_computed_on_logged_trials_only_and_the_report_says_so` | `returns_matrix` was already logged-trials-only (no code change there). Added: the PBO criterion's `note` states, for any seeded family, the real-trial column count and that inherited trials contribute none. Verified the note names `20` and contains `inherited` / `none`, and the rendered markdown carries the count. | Yes |
| H-10 | `test_h10_negative_seeding_alone_does_not_blow_the_trial_budget` | The "Trial count N" criterion's `OVER BUDGET` check changed from `fam.n_trials > fam.trial_budget` to **`fam.n_logged > fam.trial_budget`** — the budget governs post-seal search, which seeding is not. Verified: seeded 31,250 + 2 logged + budget 40 → no `OVER BUDGET`; same family at 41 logged → `OVER BUDGET` appears. | Yes |
| H-11 | `test_h11_negative_seeded_family_with_no_logged_trials_is_insufficient_data` | The zero-trials guard changed from `fam.n_trials == 0` to **`fam.n_logged == 0`**, and its note names `logged=0` explicitly when the family is seeded. Verified: seeded 31,250, 0 logged → `INSUFFICIENT-DATA`, never `PASS`. | Yes |
| H-12 | `test_h12_report_renders_the_decomposition_not_a_bare_total` | `ValidationReport` gained `n_inherited`/`n_logged` fields; `to_markdown()` renders `**31,252** (31,250 declared inherited [inferred, D-009] + 2 logged)` instead of a bare `**31252**` whenever `n_inherited` is truthy. Verified all three integers and the word "inherited" appear. | Yes |
| H-13 | `test_h13_negative_an_unseeded_family_is_bit_for_bit_unchanged` | Negative control. Verified: `family_stats` for `n_inherited` omitted vs. explicit `0` agree on every field; `evaluate_gate1`'s full criteria list (name/value/threshold/verdict) is identical between the two; the binding hash (computed directly via `_binding_dict`/`_binding_hash` on the two rows, family-name-normalised since the registry keys on `family`) is identical. Confirms H1–H2 add a capability, not a behaviour change, for the common case. | Yes |
| H-14 | `test_h14_forward_lag_001_declared_denominator_end_to_end` | End-to-end: registered `forward-lag-001` with the `PREREG-001` §19 field set (statement/mechanism/falsifier/etc. drawn from the actual document; `trial_budget=40`, `n_inherited=31250`, `holdout_classification="FORWARD"`, etc.), 2 logged trials. `family_stats.n_trials == 31252`; `stats.expected_max_sharpe(31252, 1.0) ≈ 4.1308`; `stats.min_backtest_length_years(31252, 1.0, 365) ≈ 17.063`; on a 4.00-year `oos_index` at net SR ≈ 1.0, both length and DSR criteria **FAIL**. | Yes |

All fourteen numbered items (nineteen test functions counting sub-letters) are
implemented per specification with no assertion moved, weakened, or deleted.

---

## 5. Migration path for the existing database

`_migrate()` gained one more entry in its `additions` list:
`("n_inherited", "INTEGER NOT NULL DEFAULT 0")`, applied via `ALTER TABLE
hypotheses ADD COLUMN ...` exactly like the R1/R3/R4 columns before it, and
skipped if the column is already present (the existing `if name not in cols`
guard — untouched).

**Finding, not covered by any existing Issue Log entry, and worth the CIO's
attention.** `book/registry.db` **already has** the `n_inherited` column —
`PRAGMA table_info(hypotheses)` against the live file shows it: `INTEGER`,
`notnull=1`, `dflt_value='0'`, matching this change's definition exactly — even
though the source at HEAD (before this task started) declared no such column
anywhere and I-036 explicitly recorded `book/registry.db` as "verified untouched
(0 families, 1 event)" at the time of that incident. The most likely explanation:
the orphaned pre-I-036 dispatch's partial `registry.py` (the one with `+133
lines, uncommitted` that got reverted to `HEAD`) opened a `TrialRegistry` against
the live `book/registry.db` before the source revert, and `_migrate()`'s
`ALTER TABLE` — a mutation to the on-disk SQLite file, not to git-tracked
source — persisted through the later source-only revert and was carried forward
into subsequent commits (`06669dd`/`2c0d3e7`) that touched `book/registry.db` for
unrelated reasons (event logging from the live Polymarket-capture dispatch).
**Net effect here is benign** — the column's definition is byte-identical to what
this task adds, `_migrate()`'s `IF NOT EXISTS` guard makes re-applying it a no-op,
and `book/registry.db` still has 0 hypotheses so no data was ever seeded against a
row using it. But it means the book of record's schema and its source code
diverged silently for at least one commit, in the same family of failure A3 exists
to prevent (I-013's shape: the repo should be reconstructable from itself). Flagging
for the CIO rather than filing an Issue Log entry myself, since the causal chain is
inferred from timing rather than measured directly, and the correct owner
(whichever seat's dispatch actually did it) isn't something I can determine from
inside this worktree.

No other migration path exists or is needed — `trials` and `events` are
unchanged.

---

## 6. What could not be implemented as specified

Nothing. All fourteen numbered H-cases (nineteen functions) are implemented and
pass with the exact assertions Validation specified, transcribed without
adjustment. No assertion required escalation.

**One judgment call, disclosed rather than escalated because it is squarely
"how to implement a stated requirement" (this seat's own decision per its charter,
not a moved assertion):** the H-5b non-overlap guard fires only when the
predecessor chain's own `n_trials` is `> 0`. Validation's spec states the rule as
"a successor's `n_inherited` must be strictly less than its predecessor chain's
`n_trials`," without addressing the zero case. Applied literally with no floor, a
predecessor chain totalling `0` (a fresh, unseeded predecessor with no trials
logged yet) would make **any** non-negative `n_inherited` for the successor
(including the default, `0`) satisfy `n_inherited >= chain_total` and raise —
which would have broken the pre-existing, passing `test_F4_predecessor_family_n_...`
and `test_P8_report_lists_predecessor_chain_prereg_hashes` fixtures (both open a
successor of a predecessor with zero trials, at the time of registration, using
the default `n_inherited=0`). The `chain_total > 0` guard is monotonically safe
for idempotent re-registration (chain totals only grow over calendar time, which
makes the inequality *harder*, not easier, to trigger on a later idempotent
re-call), and is the only reading under which the ordinary, common case — a
successor of a family that hasn't run anything yet — remains registrable at all.
Recorded here on the report's face per house rule 6, not hidden as an
implementation detail.

---

## 7. Escalations

None. No assertion was unmeetable; no defect surfaced that this seat is not
positioned to fix; no material judgment call fell outside this seat's charter
(schema, pipeline design, "how to implement a stated requirement" are this seat's
own to decide per `agents/head-of-data-infra.md`). Item 5's non-overlap floor
above is disclosed, not escalated, on that basis. The `book/registry.db` schema
divergence finding at §5 is flagged for the CIO's attention because its cause is
inferred rather than measured, not because it blocks anything today.

---

## 8. Re-audit — "test passes while its property fails"

Ran mutation checks against the five highest-risk assertions (the two H1–H2-
introduced defects, the double-count guard, and the core seeding arithmetic) by
reverting each fix in isolation, re-running the targeted test, confirming failure,
then restoring:

- **H-10's guard** (`n_logged` vs `n_trials` for `OVER BUDGET`): reverted to
  `n_trials`, `test_h10...` failed exactly as expected (`OVER BUDGET` appeared
  where the test asserts it must not).
- **H-11's guard** (`n_logged == 0` vs `n_trials == 0`): reverted, `test_h11...`
  failed (`PASS` where the test asserts `INSUFFICIENT-DATA`).
- **H-5b's double-count guard**: disabled (`predecessor_family is not None and
  False`), `test_h5_negative...` failed (`DID NOT RAISE`).
- **The core seeding arithmetic** (`family_stats`'s `n_inherited` summation):
  disabled entirely (forced to `0`), 9 of the 19 tests failed — every case that
  actually depends on seeding (H-4, H-5a, H-5b, H-7, H-8, H-9, H-11, H-12, H-14) —
  while the 10 that don't depend on it (H-1, H-2, H-3a/b/c, H-6a/b/c, H-13) kept
  passing, exactly as expected for a targeted mutation.

All four mutations were caught. **I found no case of a test passing while the
property it names is false** — this is a legitimate negative result, not an
omission; the mutation set above was chosen to cover the two "H1–H2 will create
this defect" cases named explicitly in the work order (H-10, H-11) plus the two
places a cosmetic implementation would most plausibly have slipped through
(H-5b's guard, and the core arithmetic that seven of the fourteen items rest on).
I did not mutation-test every one of the nineteen functions individually — H-1,
H-2, H-3a/b/c, and H-6a/b/c are either generic-mechanism reuse (H-3b/c ride on the
pre-existing, already-tested `_BINDING_FIELDS`/`verify_prereg` machinery) or
direct, single-line assertions against unchanged code (H-6a/b/c), where the
failure mode a mutation check would catch is essentially the same one already
exercised by the pre-existing 96-test suite's equivalent P-series/F4 coverage.

Suite state at handoff: **115 passed, 0 failed, 0 skipped, 0 xfail.**
`book/registry.db`: unchanged (0 hypotheses, 0 trials, 1 event; `git status
--porcelain book/` empty).
