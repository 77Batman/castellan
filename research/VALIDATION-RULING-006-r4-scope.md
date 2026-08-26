# VALIDATION RULING 006 — R-4's scope: was the clause written to govern production writers, or all writers?

**Head of Quantitative Validation · Castellan Capital · 2026-08-25 · Dispatch S4-D-008**
**Adjudication of I-100, against `VALIDATION-SPEC-004`, which this seat wrote.**
**Registry at authoring and at close [measured]: `book/registry.db` — 0 hypotheses / 0 trials / 3 events. `book/vaults/` holds `.gitkeep` and nothing else.**

---

## 0. THE RULING, IN ONE SENTENCE

> **R-4 governs ALL WRITERS. A test exercising a write path is a caller like any other, the clause
> was never scoped to a caller class, and it could not have been — R-4 is a property of the method,
> not of who invoked it.**

The 148 pre-existing tests are grant-opened. The remedy follows from the scope, not the other way
round.

**And the fork I was offered was not real.** §3 measures it: **relaxing R-4 restores zero tests.**
The write still dies one layer down at R-5. To restore the 148 by relaxation you must also relax
R-1 — the read-only default, which *is* I-095's remedy — and the rows then land `grant_id IS NULL`,
which under R-15 makes **60 pre-existing `evaluate_gate1` call sites** return overall
`INSUFFICIENT-DATA`. Option (b) was never on the table. I did not decline it; it does not exist.

**And the incident's damage assessment is understated.** §6: `harness/castellan/holdout.py` ships
**8 of 13 `_grant_log` call sites passing 4 positional arguments to a 3-argument method** — an
unconditional `TypeError`, **42 test instances**, introduced by the implementation, unrelated to
R-4's scope, and invisible today because the grant error fires first. **`DATA-IMPL-008` §5's "no
new, independent bugs were found" is false.** I-260 / I-261.

---

## 1. LINE BUDGET — the projection is rejected before it is overrun, per §2.2's extension

**Projection given: ~300. Revised projection stated here, before writing past it: ~370.**

**I accept the comparator and reject the scaling.** `VALIDATION-RULING-005` at 583 authored lines
for four adjudications is the right measured member — it is me adjudicating my own specification's
defects, including I-065 — and ~146 per adjudication plus framing is the right unit. The dispatch's
class gap is real and is the reason the number moves.

**The three named overruns, priced:**

| # | What | Lines |
|---|---|---|
| 1 | A remediation prescription a Sonnet implementer executes **mechanically** across 10 files / 48 functions / 71 grant blocks. RULING-005 prescribed three fixture edits in prose. This one cannot be prose: a per-file table and an exact code shape are what stop the implementer guessing, **and guessing is what produced I-100.** | ~70 |
| 2 | **I-260, found during this adjudication and not in the brief.** A shipped harness regression the incident record does not contain. It changes the acceptance criterion and the dispatch order. | ~35 |
| 3 | §3's measurement — the disproof that option (b) exists. Not compressible to an assertion; asserting it would be the thing this seat refuses in others. | ~30 |

**~300 + 70 is the honest floor; ~370 is the estimate.** Flagged here, at line ~55, before the
document passes 300. S4-D-007 overran 1.58× without flagging and recorded that as a compliance
failure; this is the flag that failure was owed.

**MEASURED ON DELIVERY: 447 — 1.49× the dispatch's ~300 and 1.21× my own revised ~370.** The
pre-flag obligation was met; **my revised estimate was still wrong and I record it as wrong rather
than quietly reporting the ~370.** The miss is entirely in §5: I priced the prescription at ~70 and
it came to ~110, because the visibility mechanism (§5.1) and the anti-bypass meta-test are
themselves specification work I costed as if they were part of the per-file table. **Estimating a
prescription by its table and forgetting the construction the table presumes is the same shape of
error as specifying a clause and not counting its callers** — twice in one dispatch, which is worth
more as a datum than either instance alone.

---

## 2. THE MEASURED FACTS — re-measured by me, not accepted from the brief

Every figure below is `[measured]` this session against the working tree at `917b4bb`.

| Fact | Measured | Brief said | Agrees |
|---|---|---|---|
| Suite | **173 passed / 81 failed / 68 errors / 322** | 173 / 81 / 68 | ✓ |
| Baseline | 272 / 50 / 322 | same | ✓ (cited, not re-measured) |
| Distinct failing/erroring node IDs | **149** | 149 | ✓ |
| …of which in SPEC-004's own two files | **1** (`test_rwg_03`) | exactly 1 | ✓ |
| …pre-existing | **148** | 148 | ✓ |
| SPEC-004 files | **46 of 47** | 46 of 47 | ✓ |
| `test_dce_17`, `test_dce_21` | **pass** — direction-blindness proved on §11.1's own stale span | same | ✓ |
| `book/registry.db` | **0 / 0 / 3** | 0/0/3 | ✓ |

**The caller count, which nobody stated and which the new standing practice now requires** —
measured by AST walk over `harness/tests/*.py`, counting `open_hypothesis` / `log_trial` /
`log_event` calls:

| Quantity | Measured |
|---|---|
| Direct call sites, pre-existing files | **99** |
| …in test bodies / in helpers & fixtures | **87 / 12** |
| Distinct functions containing them | **48** (38 test bodies + 10 helpers/fixtures) |
| Files | **10** |
| **Grant blocks required** (R-7 forbids nesting; R-10 splits the vocabulary) | **71** |
| Functions needing ≥2 blocks | **17** |
| Pre-existing `evaluate_gate1` call sites at risk under relaxation | **60** |

**The load-bearing number is 71, not 148.** 148 is the blast radius; 71 is the work. The ratio —
one edit restoring roughly two tests — is what makes ruling (a) affordable, and **it is a number
that existed before R-4 was written and that I did not go and get.** I-264.

---

## 3. WHY THE FORK WAS NOT REAL — the measurement that decides this before any doctrine does

I ran the relaxation rather than reasoning about it. `TrialRegistry` subclassed with
`_require_grant` as a no-op — which is exactly and only what "relax R-4" means:

```
A. R-4 relaxed, ungranted open_hypothesis
   -> OperationalError: attempt to write a readonly database
B. R-4 AND R-1 both relaxed
   -> write succeeds
   -> audit_write_grants orphan_rows: {'hypotheses': 1, 'trials': 0, 'events': 2}
      n_grants: 0
```

**Three consequences, all measured, none arguable:**

1. **Relaxing R-4 alone restores nothing.** R-5's read-only handle refuses the write at `execute`.
   R-4 is a guard *in front of* a door that is independently locked. This is exactly the property
   R-5 was specified to have — *"R-5 answers a question R-4 cannot"* — and it means the relaxation
   fork was priced against the wrong clause.
2. **The relaxation that works is relaxing R-1**, the read-only default. R-1 is not a convenience;
   it is the whole of the Principal's S3-D-009 remedy to I-095, the four-domain doctrine at
   §4.7.3 landing in code. **"Relax R-4" is, when measured, "undo I-095."** Nobody proposed that,
   and it is not mine to do in any case.
3. **Even relaxed both ways it does not work**, because the rows arrive `grant_id IS NULL` — R-14 —
   and R-15 makes any Gate 1 evaluation against a registry carrying one orphan return **overall
   `INSUFFICIENT-DATA`**. `test_rwg_17` passes today and asserts precisely this. **60 pre-existing
   `evaluate_gate1` call sites** would then return `INSUFFICIENT-DATA` where they assert graded
   verdicts. Relaxation does not restore the suite; it re-breaks it more quietly, in the one mode
   this firm is least able to see.

**A control cannot be relaxed for a caller class when the record it writes is keyed to the row and
not to the caller.** R-14 stamps `grant_id` on the *row*. There is no schema in which a row knows
it was written by a test and should be forgiven. That is not an argument about doctrine — it is
what the table looks like. I-262.

---

## 4. THE RULING AND ITS REASONS — what the clause was for

### 4.1 The clause has no caller in it, and this is not an oversight

R-4's text, verbatim: *"An ungranted write raises `RegistryWriteNotGrantedError` at method entry,
before any SQL. `open_hypothesis`, `log_trial` and `log_event` each begin with
`self._require_grant(...)`."*

**The subject is the method. There is no clause, sentence, or word about who calls it.** A reader
asking "did she mean production only?" would have to supply the qualifier themselves. §9.1 lists
R-1…R-8 as **mechanical — "implement as written, no consultation."** The implementing seat read it
correctly. There is nothing to interpret.

### 4.2 A caller-class carve-out is the exact construction §4.7.3 forbids

The doctrine's own worked negative print is I-095: a control that was *"enumerated, deterministic,
correctly configured, and pointed at nobody."* Its repair — the Principal's — was that when a
control cannot be aimed from outside, **it moves down a layer into the thing being protected**, and
that *"python3 except when it touches the registry"* is **classification wearing enumeration's
clothes.**

**"All writers except test writers" is the same sentence with a different noun.** It asks the
registry to classify its caller. The registry cannot: it has a connection, a method name, and a
grant, and not one of those knows what a `pytest` process is. Any implementation would key off
something incidental — a module name, an environment variable, an import — and each of those is a
string a real actor can set. **A control that a caller can leave by renaming itself is not a
control.**

### 4.3 The doctrine the Principal stated, which I adopt without needing to be persuaded

> *A test exercising a write path is a caller like any other, and a fixture-level bypass that
> grants invisibly is the control's own defeat installed at birth — CASE-9 with a test decorator.*

It is correct and it is the same principle as §4.7.2's *"a control exists where the harness reads
it, and nowhere else."* I record that **it is non-binding and that I would have reached it from
§4.7.3 alone**, because a ruling that leans on the Principal's framing is a ruling he cannot later
use as an independent check on me. **I have twice ruled against my own specification — I-058 and
I-065 — and neither obliged a third. This one is not a third: my specification is right. The
defect is that I never counted what it would cost, and that is a different failure with a different
remedy.** §7.

### 4.4 What I am NOT ruling

- Not that the suite's 148 tests were wrong to be written as they were. They predate the grant
  system and were correct when authored. **This is a migration, not a fault.**
- Not that the implementing seat erred. It faced two explicit mutually exclusive requirements,
  chose the deliverable, and disclosed. **That is the behaviour this firm wants and I record it as
  such** — with §6's one qualification, which is about the *assessment*, not the *choice*.
- **No relaxation occurs, therefore the three-register disclosure is not triggered.** SPEC-004
  §4.2–4.4's disclosure of what the grant prevents / detects / does not touch stands unamended and
  is not re-opened by this ruling. Ruling (a) extends the control's coverage; it removes nothing.

---

## 5. THE REMEDIATION — specified here, executed by a separate dispatch

**I do not execute it.** Per the dispatch's separability constraint, the ruling and its execution
stay apart. What follows is complete enough that the implementer decides nothing.

### 5.1 The grant's visibility mechanism, under `GATES.md` §4.7.4(ii)

**The Principal refused an invisible fixture grant in advance and I refuse it in the same terms.**
The construction that satisfies both his refusal and §4.7.4(ii) separates two things that a naive
fixture would fuse:

> **The fixture supplies the ANNOUNCEMENT. The test supplies the AUTHORITY.**

A fixture yields a *callable*; the `with` statement appears **in the test's own text**. Verified in
`scratchpad/proto_test.py`, run under `pytest -s`:

```
[write-grant] proto_test.py::test_shape_works reason=REGISTER_HYPOTHESIS dispatch=TEST:test_shape_works
   orphans: {'hypotheses': 0, 'trials': 0, 'events': 0} n_grants: 1 chain_intact: True
[write-grant] proto_test.py::test_shape_works grants_taken=['REGISTER_HYPOTHESIS']
[write-grant] proto_test.py::test_clean_run_is_still_visible grants_taken=NONE
```

**The second line is the §4.7.4(ii) requirement doing its actual job:** a test that takes no grant
prints `grants_taken=NONE`. **Silence is never the signal.** A reader of a clean run sees one line
per test, and a test whose grants vanished is distinguishable from a test that never took one.

**Two ways a caller may satisfy this — both acceptable, neither optional:**

| Shape | Where the grant appears | Use when |
|---|---|---|
| **In-test** | `with grant("LOG_TRIAL"):` in the test body | the 38 test bodies |
| **In-fixture, for the fixture's OWN writes only** | `with reg.write_grant(...)` in the fixture body, closing **before** the fixture returns | the 10 helpers/fixtures |

**The refused shape, named so it is not reinvented:** a fixture that opens a grant and `yield`s
*inside* it, so the test body's writes ride on authority its own text never shows. R-7 punishes it
the moment the test also grants explicitly (`RegistryWriteGrantNestedError`), but a test that takes
no grant would ride it silently. **Not foreclosed by construction, therefore foreclosed by a
test** — §4.7.5's preferred order, applied where it can be.

> **`test_grant_meta_01` — static, at collection.** AST-walk every file in `harness/tests/`; for
> each `with` statement whose items mention `write_grant` or `grant`, fail if any `Yield` or
> `YieldFrom` node occurs inside it.

Verified in `scratchpad/meta_check.py`: **0 offenders across the 18 current files; 1 offender in a
negative control that writes the bypass shape deliberately.** The check catches what it claims to.

### 5.2 The per-file prescription

Reason mapping is R-10's, unchanged: `open_hypothesis`→`REGISTER_HYPOTHESIS`,
`log_trial`→`LOG_TRIAL`, `log_event`→`LOG_EVENT`. `dispatch=` is the string `TEST:<function name>`.
`token=` is the literal `"test-token"` (see I-269).

| File | Node IDs failing | Call sites | Functions | **Grant blocks** |
|---|---|---|---|---|
| `test_holdout_p1.py` | 66 | 19 | 12 | 12 |
| `test_trial_budget_enforcement.py` | 25 | 7 | 6 | 6 |
| `test_seeded_n.py` | 19 | 58 | 19 | **38** |
| `test_carry_accounting.py` | 16 | 1 | 1 | 1 |
| `test_harness.py` | 9 | 3 | 3 | 3 |
| `test_tstat_hac.py` | 5 | 1 | 1 | 1 |
| `test_minbtl_serial.py` | 3 | 3 | 2 | 3 |
| `test_vif_estimator.py` | 2 | 4 | 2 | 4 |
| `test_data_book.py` | 2 | 1 | 1 | 1 |
| `test_dsr_serial.py` | 1 | 2 | 1 | 2 |
| **Total** | **148** | **99** | **48** | **71** |

**`test_holdout_p1.py` is the cheapest and most instructive:** its 66 failures are one fixture. I
patched that single fixture in scratchpad — **one grant block** — and the file went from 0 passed
to **32 passed / 34 failed.** One edit, 32 tests.

**`test_seeded_n.py` is the expensive one and the reason is mine.** 19 functions need 38 blocks
because R-7 forbids nesting and R-10 refuses to let one grant both register a family and log trials
into it. `test_h5_transitive_sum_across_chain_no_double_count` needs **6 blocks for 6 calls**. That
is R-10 working exactly as I specified — *"a grant taken to log a trial cannot register a
hypothesis without a second, separately recorded grant naming that"* — and the suite is the first
place the firm pays for it. **I am not softening R-10 to make the edit cheaper.** I-263.

### 5.3 Order of execution — this matters, see §6

1. **Seat 9 repairs I-260 first** (harness code; not mine, not the test dispatch's).
2. **Then** the Validation-owned test remediation, one file per commit, largest ratio first.

**Reversing this order produces 42 unexplained `TypeError`s in a test-remediation dispatch, and the
predictable response is to "fix" them in test files, where the defect is not.**

### 5.4 Acceptance criterion — and it may not be reported before both land

> **322 collected · 318 passed · 4 failed · 0 errors.**
>
> The 4 are `test_mbs_12` (I-076), `test_G2`, `test_h7`, `test_h8` — **and the last three must fail
> with `AssertionError`, not with any registry, grant, or `TypeError`.**

This restores exactly the floor SPEC-004 §10 projected. **It is not verifiable until I-260 is
repaired.** A dispatch reporting a floor with `TypeError`s outstanding has reported a number it did
not measure.

---

## 6. I-260 — THE REGRESSION THE INCIDENT DOES NOT CONTAIN

Found by patching one fixture and reading what appeared underneath.

```
42 × TypeError: HoldoutVault._grant_log() takes 4 positional arguments but 5 were given
```

Static confirmation against the shipped `harness/castellan/holdout.py`, by AST — **not inferred
from the traceback**:

| | |
|---|---|
| `def _grant_log(self, reason, kind, detail)` — accepts | 3 positional after `self` |
| Call sites | **13** |
| **Call sites passing 4** | **8** — lines **498, 523, 544, 560, 574, 672, 694, 731** |

**Every one raises unconditionally.** This is not a scope question, not a test-authoring question,
and not R-4's. It is a defect introduced by `DATA-IMPL-008`'s rewrite of `holdout.py`, currently
invisible because `RegistryWriteNotGrantedError` fires at the fixture before the vault is reached.

**And it makes `DATA-IMPL-008` §5 wrong where it is most load-bearing:**

> *"No new, independent bugs were found in the ~149 collateral failures beyond I-231 itself — I
> sampled across `test_carry_accounting.py`, `test_holdout_p1.py`, and `test_seeded_n.py`…"*

**The sample included the file carrying all 42 instances and did not find them, because the
sampling method could not.** Sampling a *masked* failure population reads the mask, not the
failure. Every sampled traceback terminates at the grant error by construction; the second defect
is behind it in every single one. **The method could only ever have returned the answer it
returned.**

**I do not read this as concealment and I record that plainly** — the seat disclosed the collateral
it knew of, at cost to itself, when hiding it was available. **I record it as the sixth appearance
of the firm's masking pattern**, at 42 instances rather than the 3 the dispatch already named:
**I-092's class in the suite itself, which is the dispatch's own phrase for `test_G2`/`h7`/`h8` and
turns out to describe something fourteen times larger.** I-261.

**The standing rule this earns, and it is the general form of the dispatch's `test_G2` instruction:**

> **A masked failure population may not be assessed by sampling. Unmask first, then count. A
> traceback that terminates at a known blocker is evidence about the blocker and about nothing
> behind it.**

---

## 7. `test_G2`, `test_h7`, `test_h8` — RESTORED, NOT REPAIRED

Currently all three die at `RegistryWriteNotGrantedError` before their own assertions run. A reader
checking I-078 today is shown the wrong cause. **Their documented reasons, from `I-078(b)` and
`I-068`/`RULING-005` §4.2–4.4:**

| Test | Documented failure | Restored by |
|---|---|---|
| `test_G2_oos_index_calendar_span_used_and_reported` | 3rd sub-assertion `crit.verdict != "INSUFFICIENT-DATA"`. `famA` carries zero trials; M-7 makes the length criterion `INSUFFICIENT-DATA` with no zero-trial carve-out. Ruled **deliberately superseded**. | the `registry` fixture's grant block |
| `test_h7_dsr_consumes_the_seeded_denominator` | `crit.value == approx(deflated_sharpe_ratio(...))` — the **uncorrected** DSR, at a fixture measured `VIF = 10.65`. Property survives; **coverage genuinely lost**, must be rebuilt. | 2 grant blocks in the test body |
| `test_h8_minbtl_consumes_the_seeded_denominator_and_fails_a_short_backtest` | MinBTL literals `17.06 / 0.27` years computed at `VIF = 1`; serial-corrected figures are `181.67 / 2.876`. Both verdicts unchanged. | 2 grant blocks in the test body |

**`test_G2` is verified, not predicted.** With the fixture grant applied in scratchpad:

```
>       assert crit.verdict != "INSUFFICIENT-DATA"
E       assert 'INSUFFICIENT-DATA' != 'INSUFFICIENT-DATA'
E        +  where ... Criterion(name='Backtest length (years)', value=4.974674880219028, ...)
trial/test_holdout_p1.py:759: AssertionError
--- Captured stdout setup ---
[write-grant] fixture registry reason=REGISTER_HYPOTHESIS dispatch=TEST:test_holdout_p1.registry
--- Captured stdout call ---
[evaluate_gate1] write-grant audit — chain_head=cd3f2951a6406e65... chain_intact=True n_grants=1 unclosed=[] orphans={'hypotheses': 0, 'trials': 0, 'events': 0}
```

`AssertionError`, on the documented sub-assertion, and `crit.value = 4.974674880219028` — **the
exact figure I-068 recorded on 2026-08-05.** The disposition is legible again. Zero orphans, chain
intact, grant printed on setup and on the Gate line.

> **Binding on the remediation dispatch: paste all three tracebacks into its report.** The evidence
> that a mask is gone is the failure underneath it, and §4.7.4(ii) says name the output a reader
> sees.

**Not executed here and deliberately:** I-068's three owed fixture edits, which would make these
tests *pass*. They have been owed since 2026-08-05 and are now in their second incident. Executing
them inside a remediation dispatch would hide the I-078 dispositions a second time, in the same
motion that unhides them. **They stay red and visible.** I-267.

---

## 8. WHAT ELSE IN SPEC-004 IS AFFECTED

| Clause | Affected | Disposition |
|---|---|---|
| **R-4** | the ruling | **Unchanged. Governs all writers.** |
| **R-1 / R-5** | load-bearing in a way §2 did not state | Unchanged. §3 shows R-5, not R-4, is what actually refuses the write. **The spec undersold R-5 by calling it "the backstop, not the control."** It is the control; R-4 is the diagnostic that makes the traceback readable. Recorded, not amended. |
| **R-3 / `test_rwg_03` / I-230** | **yes — ruled here** | The implementer inverted `allow_create` to `True` to satisfy **my own** `_seeded()` and `_build()` fixtures, which I authored to conflict with **my own** R-3. **Ruled: `allow_create` returns to `False` as R-1/R-3 specify, and the two fixtures pass `allow_create=True` explicitly.** Restores R-3 as written *and* makes `test_rwg_03` pass. A tightening toward the clause's stated assumption — **§4.7.5, Validation's, no Principal act.** I-265. |
| **R-7 × R-10** | measured cost | 17 of 48 functions need ≥2 grant blocks. **Not relaxed.** I-263. |
| **R-14 / R-15** | vindicated | The orphan rule is what makes relaxation incoherent (§3.3). Working as specified. |
| **R-16** | stale premise | Written against *"its 1 existing event row [measured]"*. `book/registry.db` now holds **3**, and **no `write_grants` table** — the migration has never run against the book of record. I-268. |
| **§10's projected floor** | wrong, and mine | *"Intended state: 318 passed / 4 failed / 322"* was computed without the caller count. The number was right; the path to it was uncosted. I-264. |
| **Item 2 (E-1…E-25)** | **not affected** | Entirely independent of R-4's scope. 28/28 green. `test_dce_17` and `test_dce_21` pass; direction-blindness is proved on §11.1's own stale span, which is the one result in this incident that is unambiguously good news. |

---

## 9. ISSUES FILED · I-260 … I-269

| ID | Title | Sev | Owner |
|---|---|---|---|
| **I-260** | `holdout.py` ships **8 of 13** `_grant_log` call sites passing 4 positional args to a 3-arg method; **42 test instances** raise `TypeError`; unconditional, independent of R-4, masked behind the grant error | **HIGH** | quant-validation → head-of-data-infra |
| **I-261** | `DATA-IMPL-008` §5's "no new, independent bugs" is **false**; produced by sampling a masked failure population, a method that could only return that answer. Standing rule at §6: **unmask, then count** | **HIGH** | quant-validation → head-of-data-infra |
| **I-262** | The I-100 "relax R-4" fork **does not exist**: R-5 refuses the write independently; relaxing R-1 too yields `grant_id IS NULL` rows making **60** pre-existing `evaluate_gate1` sites return `INSUFFICIENT-DATA`. Recorded so it is not re-proposed | MEDIUM | quant-validation |
| **I-263** | R-7 × R-10 forces **2+ sequential grant blocks** on the suite's commonest shape; **17 of 48** functions, `test_h5` at 6-for-6. A measured cost of my own design, **not relaxed** | MEDIUM | quant-validation |
| **I-264** | `VALIDATION-SPEC-004` altered a call contract and stated **no caller count**; §10 projected a post-implementation floor that silently assumed zero affected callers. The defect the new standing practice names, in the document that caused it | MEDIUM | quant-validation (self) |
| **I-265** | I-230 ruled: `allow_create` returns to `False`; SPEC-004's own `_seeded()`/`_build()` pass `True` explicitly. **My fixtures contradicted my clause** — the same not-counting defect one layer in | MEDIUM | quant-validation |
| **I-266** | A fixture yielding inside an open grant is **not** foreclosed by R-6/R-7 for a test taking no explicit grant; closed by static `test_grant_meta_01`, prototyped and verified against a negative control | MEDIUM | quant-validation |
| **I-267** | I-068's three owed fixture edits (`G2`/`h7`/`h8`) remain unexecuted since 2026-08-05, now in their **second** incident; **deliberately not executed** under this remediation so the I-078 dispositions stay visible | LOW | quant-validation |
| **I-268** | `book/registry.db` has **no `write_grants` table**: R-11/R-14's migration has never run against the book of record, so R-15's orphan audit has never been exercised on real data. R-16's amnesty was specified against **1** event row; there are now **3** | MEDIUM | quant-validation → head-of-data-infra |
| **I-269** | The suite's grant `token` is a literal string in the test's own text — **I-103 / I-161 arriving in the suite.** Accepted and disclosed: what tests need from the grant is **visibility**, not authentication, and the grant authenticates nobody anywhere | LOW | quant-validation (disclosure) |

---

## 10. ADDRESSED TO THE PRINCIPAL

**1 · Your framing was right and I want it recorded that I did not need it.** *"A test exercising a
write path is a caller like any other"* is `GATES.md` §4.7.3 restated, and §4.2 above derives the
same ruling from the doctrine alone. I say so because a ruling that rests on your framing is a
ruling you cannot afterwards use to check me, and the independent line is worth more than the
agreement.

**2 · The count is the finding, and the new standing practice is aimed correctly at me.** I wrote a
clause that changed a call contract for **99 sites in 48 functions across 10 files** and I stated
no number. The CIO dispatched it and asked for none. **The clause is right; not counting it is what
turned a correct control into a firm-wide outage.** I-264 is filed against my own document and I
will state a measured caller count in every spec I write that alters a call contract.

**3 · I-260 should change how you read incident reports, not how you read that seat.** A seat
disclosed collateral at cost to itself and its damage assessment was still wrong by 42 instances,
because it sampled a population where every traceback terminates at the same known blocker. **No
amount of care fixes that; only unmasking first does.** You already ordered exactly this for three
tests. §6 generalizes your instruction, and I would rather you saw it as your rule scaling than as
my finding.

**4 · What this incident cost, stated plainly.** Zero research output. The seal remains blocked.
Objective 1 is blocked on infrastructure and not on any family. **The registry is untouched at 0 /
0 / 3 and no holdout has been opened, listed, or referenced** — the one guarantee this incident
never put at risk.

---

## 11. VERIFICATION AT CLOSE

| Constraint | Status |
|---|---|
| `book/registry.db` | **0 hypotheses / 0 trials / 3 events** [measured at close] |
| `book/vaults/` | `.gitkeep` only; no vault constructed, no `seal()`, no `open_once`, **no passphrase in this session** |
| `open_hypothesis` / register / seal called | **No.** Registry writes in this session: **zero** |
| `harness/castellan/` or `harness/scripts/` modified | **No** — `git status` clean for both |
| Test files modified | **No.** All prototypes under `scratchpad/`; the ruling and its execution stay separable |
| `PREREG-002-*` · `DIR-RESTATE-*` · `REGISTRATION-PAYLOAD-*` · `REDTEAM-*` | **Untouched** |
| Committed | **No** |

**Holdout status: LOCKED. Never consulted, in any form, before or during this evaluation.**
**Leakage audit: not applicable in substance — this ruling produces no performance number, reads no
price, universe, or fundamental, and grades no returns series. Run and recorded rather than
skipped, per standing obligation.**

---

*Head of Quantitative Validation · Castellan Capital · 2026-08-25 · Dispatch S4-D-008.*
*R-4 governs all writers. The remedy follows from the scope. The prior is guilt.*
