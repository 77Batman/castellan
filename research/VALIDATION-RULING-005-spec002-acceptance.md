# VALIDATION RULING 005 — VALIDATION-SPEC-002 acceptance: the family retarget, the exact-equality guarantee, the three protected casualties, and the construction Seat 9 declined

**Seat:** Head of Quantitative Validation (Seat 3) · **Reports to:** the Principal
**Date:** 2026-08-05
**Status:** BINDING on Seats 1, 2, 6–10. Appealable only to the Principal, in writing.
**Instrument:** adjudication of `research/DATA-IMPL-006-serial-corrections.md`, issues I-075
through I-078; amends VALIDATION-SPEC-002 clauses D-2, M-6 and D-8.
**Dispatched by:** the CIO, S2-D-020. Nothing in the dispatch binds the verdict.
**Type:** ruling. Four test files of mine were edited; **no file under `harness/castellan/`
was modified**, no data fetched, no backtest run, no hypothesis opened, no trial registered,
`book/vaults/` untouched. `book/registry.db` stands at **0 hypotheses / 0 trials** [measured,
before and after].

House rule 6 applies throughout: **[measured]** = read or computed in this repository this
session; **[cited]** = external source or internal document named inline; **[inferred]** =
reasoned from measured facts; **[assumed]** = an unverified premise, flagged as such.

---

## 0. The four rulings, one sentence each

| Item | Issue | Ruling |
|---|---|---|
| 1 | I-075 | **Retarget authorized and executed** — `test_mbs_10` and `test_dsr_07` were mine and were wrong; they now grade family `"F"`, both pass, and both carry a new guard assertion that makes the same slip fail loudly instead of silently drawing INSUFFICIENT-DATA. |
| 2 | I-077 | **The exact-equality guarantee is REQUIRED, not an overreach** — C-3 injects an estimator-unreachable `vif` precisely so the consumer-layer guarantee is verified independently of the estimator, and a guarantee that only holds on inputs the estimator can produce collapses C-2's two layers into one. |
| 3 | I-078 | **Ruled per test, not in bulk** — `test_G2`'s failing sub-assertion is superseded and its protected property survives in full on two other sub-assertions; `test_h8`'s property survives with its verdicts intact and only two VIF=1 literals superseded; `test_h7`'s property survives but its coverage is lost on a defective fixture and must be rebuilt, not accepted. |
| 4 | I-077 | **The declined construction is ADOPTED** — `z_serial = z_iid/√(max(vif, 1.0))` is correct, and the reason it is correct is that **D-2 as I wrote it violates my own C-1(iv)**; an implementer found a defect in my specification and correctly declined to fix it unilaterally. |

**Suite count** [measured]: `239 passed / 7 failed / 246` at the start of this dispatch →
**`241 passed / 5 failed / 246`** now, after the Item 1 and RULING 005-B edits to my own two
files. A further **+1** lands on Seat 9's one-line D-2 change (Item 4) and **+3** on the three
fixture amendments this ruling orders to files I may not touch (Item 3), giving a ruled floor
of **245/246**. The single remainder is `test_mbs_12` (I-076), deliberately **not** adjudicated
in this dispatch — see §5. Full ledger in §6.

**I-057 does NOT close.** §11.3's partition is unchanged and `test_monotone_conservatism.py`
is not partitionable. It stays open until Seat 9 lands the D-2 clamp.

---

## 1. ITEM 1 — I-075, the family retarget · AUTHORIZED, EXECUTED

**The defect is mine and it is exactly as Seat 9 describes it.** `test_mbs_10` and
`test_dsr_07` each seed family `"F"` and then call
`evaluate_gate1("F", "hac", registry, …)` — passing `"F"` into the `strategy` slot and `"hac"`
into the `family` slot, the latter copied from `test_tstat_hac.py`, whose own fixture pre-opens
a family by that name. Both tests therefore graded a family with zero trials and hit M-7's
INSUFFICIENT-DATA branch instead of the fully-computed branch they exist to exercise. Seat 9
verified the arithmetic by substitution rather than assuming it, and I reproduced that
verification independently before editing anything [measured, this session]:

```
test_dsr_07 fixture, family "F", 12 logged trials at rho=0.5:
  Criterion(name='Deflated Sharpe Ratio', value=0.9372, threshold='>= 0.95',
            verdict='FAIL', note='DSR(iid) = 0.9955, VIF = 2.904, T_eff = 483')
test_mbs_10 fixture, family "F", 12 logged trials at rho=0.6:
  Criterion(name='Backtest length (years)', value=5.363,
            threshold='>= max(4, MinBTL_serial=14.51)', verdict='FAIL',
            note='MinBTL(iid) = 3.39y; VIF = 4.284; N_max = 3')
```

That is the implementation behaving correctly and my test grading the wrong object. **Seat 9
was right to escalate rather than route around, and right that no implementation choice could
have fixed it** — a family-scoped registry that resolved `"hac"` to `"F"`'s trials would be a
worse defect than the one being fixed.

**Executed.** Both calls now read `evaluate_gate1("<name>-strat", "F", registry, …)`. Both
tests additionally assert `registry.family_stats("F").n_trials == 12` **before** the
evaluation. That guard is the substantive part of this item: the reason this defect survived
authoring is that an empty family produces a *plausible-looking* report rather than an error,
so the test failed for the right-looking wrong reason. The guard converts a silent
mis-target into a named failure.

**One thing this item forced into the open.** With the family corrected, both tests then failed
on a *different* assertion — M-6/D-8's criterion **rename**, which Seat 9 reverted under
I-078(a) on the argument that it bought nothing because these two tests failed anyway. That
argument's premise is now gone, so the rename is live and is ruled in §3.1.

---

## 2. ITEM 4 — the construction Seat 9 declined · ADOPTED, AND THE SPEC IS AT FAULT

I take this item before Item 2 because Item 2's answer follows from it.

### 2.1 The procedural half, which the Principal has settled and I endorse without qualification

Seat 9 found a construction that turns every one of the 46 new tests green with zero
collateral, and **did not adopt it**, because D-2 is classified mechanical/no-consultation in
§8.1 and the standing term says escalate rather than amend. That is the correct call and I
want it recorded as correct in Validation's own voice, not merely tolerated: **the value of a
pre-authored test regime is destroyed the first time an implementer is allowed to change the
specification to make the tests pass, even when — especially when — the implementer is right.**
An implementer who adopts a green-making construction unilaterally and reports success is
indistinguishable, in the artifact, from an implementer who fits the code to the tests. Seat 9
produced a red suite and a written argument instead. That is the more expensive and the correct
behaviour, and it is the second time this seat has done it (siblings: I-070, I-075).

### 2.2 The substantive half, which is mine, and on which the answer is not the one that flatters me

I approached this exactly as the dispatch frames it: **a construction that makes every test
pass is a thing to be suspicious of, not grateful for.** The suspicion has a precise form. The
question is not "does it turn the suite green" but "**does it loosen anything, anywhere, on any
input the machinery can actually receive**". I measured that rather than reasoning about it.

**Test A — do the two constructions ever differ on a reachable input?** R-7 floors `vif_gate`
at 1.0 inside the estimator, per series, before aggregation, so every value the consumer can
receive from `variance_inflation`/`family_variance_inflation` is `≥ 1`. Over 200,000 random
draws of `(z ∈ [−12, 12], vif ∈ [1, 200])` [measured]:

```
max | DSR_literal − DSR_clamped |  =  0.000e+00   (exactly zero, all 200,000 draws)
```

**The clamp changes nothing — not approximately, identically nothing — on the entire region
the estimator can produce.** It cannot loosen a live Gate verdict because it cannot change a
live Gate number. That disposes of the suspicion in the only place it has consequences.

**Test B — which construction actually satisfies C-1?** This is where the answer turned. C-1
asserts four properties **for all `vif > 0`, including `vif < 1`**, and says so in terms: *"That
universality is the whole design: the guarantee must not depend on the estimator producing a
value above 1."* Over 200,000 draws of `(z ∈ [−8, 8], vif₁, vif₂ ∈ (0, 50])` [measured]:

| Property | Literal D-2 | Clamped |
|---|---:|---:|
| C-1(iii) `DSR_serial ≤ DSR_iid`, `vif ∈ (0, 50]` | 0 violations | 0 violations |
| **C-1(iv) `DSR_serial` non-increasing in `vif`, `vif ∈ (0, 50]`** | **3,848 violations** | **0 violations** |
| C-1(iv), restricted to `vif ≥ 1` | 0 violations | 0 violations |

A violating draw, in full [measured]: `z = −0.0500`, `vif` raised from `0.591` to `12.376`,
`DSR_serial` rises `0.4741 → 0.4801`. **More measured serial dependence produced a more
permissive statistic.** That is the exact operation this entire specification exists to
prevent, sitting inside the clause that was supposed to prevent it.

The mechanism is elementary and I should have seen it when I wrote D-2. For `z < 0` and
`vif < 1`, `z/√vif` is *more* negative than `z`, so the `min` selects the serial branch — and
across `vif ∈ (0,1)` that branch is *increasing* in `vif`. The literal construction is
therefore not "conservative at `vif<1`"; it is **sign-dependent**: uncorrected for `z > 0`,
arbitrarily extra-tight for `z < 0`, with the direction of the effect set by the sign of the
candidate's deviation rather than by anything about serial dependence. That is not a
conservative property. It is an unspecified one.

**Test C — is the clamp the analogue of M-2 that Seat 9 claims?** [measured]:

```
min_backtest_length_years_serial(86, 1.0, 252, vif=0.25) = 6.1359
mb_iid * max(0.25, 1.0)                                  = 6.1359     identical
vif=0.5 → 6.1359 = 6.1359 · vif=1.0 → 6.1359 · vif=3.0 → 18.4077 = 18.4077
```

M-2 **is** the clamp: `max(mb_iid, mb_iid·vif) ≡ mb_iid·max(vif, 1)`. D-6's outer `min` is not
the same operation and does not reproduce it. C-5's own framing of this specification — *"it is
the `min(t_NW, t_raw)` construction extended to `N`"* — asserts that the three corrections are
the same construction in three places. **On the `vif < 1` branch they were not, and D-2 was the
odd one out.**

### 2.3 Ruling

> **RULING 005-A. D-2 is amended. The corrected construction is:**
>
> ```
> z_iid    =  _dsr_z(returns, n_trials, trial_sr_std_period)
> z_serial =  z_iid / sqrt(max(vif, 1.0))            # ← the amendment
> DSR      =  min( Φ(z_serial) , Φ(z_iid) )          # D-6, unchanged, NOT removed
> ```
>
> The `max` inside the divisor and the `min` outside are **two independent enforcements and
> neither is removable on the argument that the other exists** — C-2's rule, now satisfied by
> D-2 in the same shape M-2 already satisfied it. D-3, D-3a, D-4, D-5, D-6, D-7, D-9 and D-10
> are unaffected. The `ValueError` contract on `vif ≤ 0` / non-finite is unchanged: the clamp
> is not a licence to accept a garbage VIF, it is a guarantee about what happens if one
> arrives.

**What this says about the specification, stated plainly because the dispatch asks for it and
because it is true.** An implementer found a defect in my specification, was correct about it,
and correctly declined to fix it unilaterally. The defect is not a typo — D-2's literal form
breaks one of the four properties that §4 exists to guarantee, and it breaks it in the
permissive direction, on the branch C-1 explicitly says the guarantee must not depend on. I
wrote C-1(iv) and D-2 in the same document and did not check one against the other. **The check
that would have caught it is the one C-4 was supposed to be**: `test_mono_05` sweeps
`vif ∈ (0, 50]` but carries the (iv) assertion only on the MinBTL side; the DSR side of (iv) is
unswept below 1. That is a gap in my own test inventory, and it is the reason a spec defect
reached an implementer. It is filed as part of I-065 and closes with the same change.

**What I am not doing.** I am not weakening D-6, not touching `DSR_MIN = 0.95`, and not
requesting any Charter §4.2 movement. This amendment moves no constant and changes no number
on any input the estimator can produce.

---

## 3. ITEM 2 — I-077, the exact-equality sub-assertion · REQUIRED, NOT AN OVERREACH

**Ruling: `test_mono_03`'s exact-equality assertion is a required guarantee. It stands
unedited. The implementation moves to meet it.**

The framing the item invites — *"`vif = 0.25` is below R-2/R-7's own 1.0 floor, an input your
estimator cannot produce, so the assertion overreaches"* — has the argument exactly inverted,
and the inversion is worth stating precisely because it is the shape of a plausible future
attack on §4.

**The unreachability of the input is the reason the test uses it, not a defect in the test.**
C-3 says so in its own text: *"`vif=0.25` is a value the estimator can NEVER produce (R-2's
floor). Injecting it proves the consumer-layer guarantee does not depend on reading the
estimator's code correctly."* C-2 specifies **two independent enforcements at two different
layers, neither removable on the argument that the other exists** — estimator (R-2/R-7's floor)
and consumer (M-2/D-6). A consumer-layer guarantee that holds only on inputs the estimator
layer already filtered **is not an independent enforcement**. It is the estimator's floor,
observed through the consumer. Accepting the overreach argument would collapse C-2 to a single
point of failure while leaving the documentation claiming two, which is the worst of both: a
future seat who removes or loosens R-7 would silently remove the guarantee as well, and
`test_mono_03` — the test written to catch exactly that — would have been pre-emptively
retired on the grounds that it tests something that cannot happen.

**Second, and decisive: the assertion is not merely defensible, it is the operative statement
of C-1(iv).** §2.2 above measures 3,848 C-1(iv) violations under the literal construction, all
of them on the `vif < 1` branch. `test_mono_03` is the assertion that detects them. It was not
overreaching; **it was right, and the implementation it was grading was wrong.** Had I ruled
this assertion an overreach and adjusted it to a `z ≥ 0` fixture — the alternative Seat 9
offers in I-077's resolution line, in the shape of I-070/test_vif_04 — I would have deleted the
only test standing between this firm and a DSR that gets more permissive as measured serial
dependence rises. That is the closest thing to an I-029(d) operation available in this
dispatch, and it was available under a respectable-sounding rationale ("the estimator can't
produce that input anyway"). I am recording that it was available and that it was declined.

**Third, on the residual.** The exact-equality requirement is not a stronger, un-stated
guarantee, as I-077 characterises it. C-3 states it verbatim (*"asserts the outputs are
**exactly** the uncorrected ones"*), and C-1(iv) implies it: if `DSR_serial` is non-increasing
in `vif` and equals `DSR_iid` at `vif = 1` (D-5, bitwise, `test_dsr_01`), then for `vif < 1` it
must be `≥ DSR_iid`; C-1(iii) requires `≤ DSR_iid`; the two together force **equality** on the
whole `vif ∈ (0, 1]` region. **The exact-equality assertion is a theorem of C-1, not an extra
demand on top of it.** Seat 9's reading — that C-1(iii) is intact and only an unstated stronger
property is missing — is a correct reading of (iii) in isolation and an incomplete reading of
C-1 as a system. That is a fair error on the implementer's part and no criticism attaches to
it; the document did not make the (iii)+(iv)+D-5 interaction explicit. It does now.

`test_mono_03` is **not edited**. It goes green when RULING 005-A lands.

---

## 4. ITEM 3 — I-078, the three protected casualties, ruled one at a time

The Principal requires written justification **per test**. No blanket acceptance is offered and
none should be read into any part of this section. I take the naming question first because
both remaining sub-items depend on it.

### 4.1 The rename (M-6/D-8) · RESCINDED, and the protection re-homed

Seat 9 reverted M-6/D-8's mandatory criterion renames — `"Backtest length (years,
serial-corrected MinBTL)"` and `"Deflated Sharpe Ratio (serial-corrected)"` — on the argument
that applying them breaks 8 protected tests keyed on the exact old name strings for zero
benefit, since the only two tests checking for `"serial"` in the name failed anyway on I-075.
**Item 1 removed that premise**, so I rule the rename on its merits rather than inheriting the
revert.

**Rescinded.** The reasoning, and the test I applied to make sure this is not an accommodation:

1. **Does rescinding move any graded quantity in the permissive direction?** No. The criterion
   `value`, `threshold`, `verdict` and `note` are byte-identical under either name. A criterion
   name is not graded and enters no arithmetic. This is the mechanical test that distinguishes
   a presentational amendment from an I-029(d) operation, and the rename passes it in a way
   that, say, widening `test_mbs_12`'s band would not.
2. **Is the protection M-6 wanted delivered elsewhere?** Yes, and verifiably [measured]: the
   length criterion's threshold string reads `">= max(4, MinBTL_serial=14.51)"` and its note
   `"MinBTL(iid) = 3.39y; VIF = 4.284; N_max = 3"`; the DSR criterion's note reads
   `"DSR(iid) = 0.9955, VIF = 2.904, T_eff = 483"`. **A reader holding only that row cannot
   mistake the graded number for the uncorrected one, because the uncorrected one is printed
   beside it, labelled, along with the VIF.** That is a stronger protection than a substring in
   a label, because it carries the *size* of the correction and not merely its existence.
3. **What is the standing protection against a mis-read excerpt?** M-11, unchanged and
   unweakened: *a MinBTL figure quoted without its VIF is inadmissible in a Validation Report
   and I will return it.* That binds every seat including me, and it does not depend on any
   string.
4. **What does upholding it cost?** Breaking 8 previously-green protected acceptance tests, in
   two files this dispatch may not touch, to change a lookup key that the suite resolves
   criteria by. That is a real cost for a presentational gain already delivered by (2).

Had the rename been load-bearing on any graded quantity I would have upheld it and sent the
8-test bill to the CIO without hesitation. It is not, and I am recording the distinction rather
than the conclusion, because the conclusion happens to be the cheap one and that is precisely
when the reasoning needs to be visible.

> **RULING 005-B. M-6 and D-8's criterion renames are rescinded.** The criteria keep the names
> `"Backtest length (years)"` and `"Deflated Sharpe Ratio"`. M-6/M-10/D-8's threshold-string
> and note requirements are **unchanged and remain mandatory** — they now carry the whole of
> the serial-correction signal, and M-11 remains the enforcement.

`test_mbs_10` and `test_dsr_07` were amended accordingly, in my own files: the name-substring
assertion is replaced by assertions on **what is actually graded** —
`"MinBTL_serial" in crit.threshold` plus the serial figure's own value, and
`crit.value == approx(rep.dsr_serial)` with `rep.dsr_serial < rep.dsr_iid` on a `rho=0.5`
fixture. Both are strictly stronger than the assertion they replace: a substring in a name
cannot detect a criterion that is renamed correctly and graded on the wrong number; these can.

### 4.2 `test_holdout_p1.py::test_G2_oos_index_calendar_span_used_and_reported` · property SURVIVES on two of three sub-assertions; the third is SUPERSEDED

**The property this test protects** is I-010's: *the length criterion's value is the calendar
span taken from `oos_index`, never the observation count, and it is reported as such; and a
sponsor whose claimed `backtest_years` agrees with the calendar is not falsely flagged.* It
carries three sub-assertions on a family (`famA`) with zero trials of any kind:

| Sub-assertion | Status under M-6/M-7 [measured] |
|---|---|
| `abs(crit.value − years_calendar) < 1e-6` | **SURVIVES.** `crit.value = 4.974674880219028`, `years_calendar = 4.974674880219028`. Exact. |
| `"DISAGREEMENT" not in crit.note` | **SURVIVES.** Note carries M-7's INSUFFICIENT-DATA text and no disagreement flag. |
| `crit.verdict != "INSUFFICIENT-DATA"` | **FAILS. Deliberately superseded.** |

**The protected property survives in full.** The calendar span is still computed, still the
criterion's `value`, still exact, and still not falsely flagged — and the three companion tests
that carry the rest of I-010's protection (`G3` disagreement-over-5%, `G4` no-index, `G5`
pooled-panel overstatement) are **all still green** [measured]. Nothing about I-010 has been
given up.

**What is given up, deliberately: the claim that a zero-trial family receives a graded
PASS/FAIL length verdict.** Under the old code this family fell through `elif fam.n_trials >= 1
and sr_ann > 0` to a bare `>= 4 years` check and **PASSED**. That is a PASS issued on a
criterion whose multiple-testing denominator is unknown and whose serial dependence is
unmeasurable — there is no logged return series in the family from which a VIF could be
estimated, so the old PASS was issued at an implied `VIF = 1`, the permissive assumption I-057
exists to remove, applied to the family with the least evidence in the registry. **My own
standing rule forbids it in terms: if N is unknown or unreconstructable, the verdict is
INSUFFICIENT-DATA, never PASS.** G2's third sub-assertion was, without anyone noticing when it
was written, an assertion that the harness must violate that rule on this fixture.

M-7 is therefore upheld **without** the carve-out I-078 offers as option (iii). A carve-out for
"genuinely zero trials" would be a carve-out for exactly the case that most needs the refusal.
`rep.overall` is unaffected either way (`FAIL` in both regimes, since the trial-count criterion
already draws INSUFFICIENT-DATA), so this changes no Gate outcome — it changes the *reason
printed on a criterion's face*, in the direction of the truth.

> **RULING 005-C.** M-7's blanket `n_logged == 0 ⇒ INSUFFICIENT-DATA` stands, with no
> zero-trial carve-out. **`test_G2`'s fixture is amended, not its assertions:** the owning seat
> logs **one** trial return series into `famA` in the `registry` fixture of
> `test_holdout_p1.py`, so the length criterion is fully computed and all three sub-assertions
> are exercised as authored. The third sub-assertion is thereby *kept*, not deleted — it is
> re-pointed at a family that can legitimately carry a graded verdict. `G3`/`G4`/`G5` share
> that fixture and must be re-run; `G4` asserts INSUFFICIENT-DATA on the *no-index* branch,
> which M-6's ordering leaves untouched, and `G3`/`G5` assert FAIL-on-disagreement, which
> precedes the VIF branch by Seat 9's branch ordering (§3.2 of DATA-IMPL-006, which I endorse:
> a misleading calendar span is a more fundamental integrity failure than an unmeasured VIF and
> must be caught first).

I may not edit `test_holdout_p1.py` under this dispatch and have not. **Until that one-line
fixture change lands, `test_G2` stays red and the firm's green floor is honestly one test lower
than it would otherwise be.** I am not recording it as accepted-and-closed.

### 4.3 `test_seeded_n.py::test_h8_minbtl_consumes_the_seeded_denominator_and_fails_a_short_backtest` · property SURVIVES INTACT; two literals SUPERSEDED

**The property this test protects** is the seeded-denominator property: *an inherited `N` that
was never logged as individual trials must still flow into MinBTL and must be able to change
the length **verdict**, so that a sponsor cannot launder away a large search by declaring it
rather than logging it.* That property is the whole point of the seeded-N work and it is one of
the load-bearing anti-gaming guarantees in this harness.

I measured the test's fixture under the correction rather than accepting the report's summary
[measured, `ppy=365`, `n_bars=1462`, span exactly 4.00y, achieved `SR_ann = 1.0000`,
`VIF = 10.647`]:

| Family | `N` | MinBTL_iid | old verdict | MinBTL_serial | **new verdict** |
|---|---:|---:|---|---:|---|
| `famSeeded` | 31,252 | 17.063y | FAIL | 181.671y | **FAIL** |
| `famPlain` | 2 | 0.270y (need 4.0) | PASS | 2.876y (need 4.0) | **PASS** |

**Both verdicts are unchanged. The protected property survives untouched — the differential the
test exists to demonstrate is exactly as strong as it was, and on the seeded side it is an
order of magnitude stronger.** What fails is two hard-coded numeric literals,
`pytest.approx(17.06, abs=0.05)` and `pytest.approx(0.27, abs=0.05)`, which are the MinBTL
figures computed under the assumption `VIF = 1` — i.e. under precisely the assumption I-057
exists to remove. **Those literals were never the property; they were the property's arithmetic
at a moment in time.** Nothing is given up here at all.

> **RULING 005-D.** `test_h8`'s two threshold literals are superseded and must be updated to
> `181.67` and `2.876` (`abs=0.05`), **with the assertion structure and both verdict assertions
> unchanged**, and with a comment naming this ruling and the measured VIF so a future reader
> sees why the numbers moved. The owning seat makes that edit; this dispatch may not.
> Recommended in the same pass: assert the *ratio* `MinBTL_serial / MinBTL_iid ==
> approx(VIF)`, which pins the property rather than the pair of literals and would not need
> touching again if the fixture ever changes.

### 4.4 `test_seeded_n.py::test_h7_dsr_consumes_the_seeded_denominator` · property SURVIVES; **coverage is genuinely lost** and must be rebuilt, not accepted

This is the one of the three where something real is lost, and I am not going to smooth it
over.

**The property this test protects** is the same seeded-denominator property as h8, on the DSR
side, with one addition that h8 does not carry and that the test names explicitly in its own
comment: *"Seeding must change the VERDICT, not merely the number"* — `crit_u.verdict ==
"PASS"` and `crit_s.verdict == "FAIL"` on the identical candidate series. **The PASS/FAIL
differential is the assertion. A test in which both families FAIL demonstrates nothing about
the denominator.**

Measured under the correction [this session, `VIF = 12.571` on the candidate series]:

| `N` | DSR_iid | verdict (old) | DSR_serial | verdict (new) |
|---:|---:|---|---:|---|
| 2 | 0.990036 | PASS | **0.744247** | **FAIL** |
| 31,252 | 0.000000 | FAIL | 0.000000 | FAIL |

Both families now FAIL. **The differential is gone, and with it the only test in the suite that
proves a seeded denominator can flip a DSR verdict.** Two sub-assertions die, not one:
`crit_u.value == approx(deflated_sharpe_ratio(...))` — the uncorrected comparand, correctly
superseded by D-2 — and `crit_u.verdict == "PASS"`, which is coverage, not arithmetic.

**Why this is the fixture's fault and not the correction's, measured rather than asserted.**
The candidate is `_calibrated_returns(0.12, 2000)`, whose docstring states it *"interleave[s] so
no run-length artefact affects any block-based stat."* **It does not** [measured]:

```
_calibrated_returns(0.12, 2000):   sign-runs 452   (i.i.d. expectation ~1000)
                                   rho_hat +0.5488   vif_hac 12.571   vif_gate 12.571   lag 19
_calibrated_returns(1/√365, 1462): sign-runs 342   (i.i.d. expectation ~731)
                                   rho_hat +0.5332   vif_hac 10.647   vif_gate 10.647   lag 16
```

`np.argsort` is not stable by default, so the intended alternation is not produced; the helper
emits a strongly positively autocorrelated series with `ρ̂ ≈ +0.55`. **No real return series a
Gate 1 candidate could plausibly present carries `ρ̂ = +0.55` at daily frequency and survives to
the DSR criterion at all** — a family at `VIF ≈ 12.6` needs, by this harness's own arithmetic,
hundreds of years of history to clear the corrected length criterion and is dead long before
DSR is reached. The fixture is not a hard case; it is an unreachable one. Seat 9's diagnosis
("real structure the estimator is correctly built to see") is correct about the estimator and
incomplete about the helper: the structure is real, and it is an accident of the helper's
construction rather than a property anyone chose.

**The property is recoverable, and I verified that before ruling** — an i.i.d.-drawn candidate
standardised to the same per-period Sharpe of 0.12 restores the differential cleanly
[measured, three seeds]:

| seed | measured VIF | DSR_serial (N=2) | DSR_serial (N=31,252) | differential |
|---:|---:|---:|---:|---|
| 5 | 1.086 | 0.9868 | 0.0000 | **PASS / FAIL** |
| 6 | 1.030 | 0.9887 | 0.0000 | **PASS / FAIL** |
| 7 | 1.048 | 0.9887 | 0.0000 | **PASS / FAIL** |

> **RULING 005-E.** `test_h7`'s protected property is **not** superseded and is **not** given
> up. Its coverage is currently lost and must be **rebuilt**: the owning seat replaces the
> candidate series with an i.i.d. draw standardised to the same per-period Sharpe (`0.12`), and
> re-points the value comparand from `stats.deflated_sharpe_ratio` to
> `stats.deflated_sharpe_ratio_serial(..., vif=<measured>)`, **keeping the
> `crit_u.verdict == "PASS"` / `crit_s.verdict == "FAIL"` differential assertions verbatim** —
> they are the test. The fixture must additionally assert its own `vif_gate < 1.5`, so that a
> future fixture change cannot silently re-introduce the serial structure that broke it. **This
> is the only one of the three where accepting the casualty as written would have cost the firm
> a guarantee**, and it is the reason a blanket acceptance of I-078 would have been the wrong
> instrument.

### 4.5 Summary of Item 3

| Test | Protected property | Disposition |
|---|---|---|
| `test_G2` | I-010 calendar span used, reported, not falsely flagged | **Survives** on 2 of 3 sub-assertions, exactly; 3rd sub-assertion **superseded** by M-7 and by my own never-PASS-on-unknown-N rule. Fixture amended (log 1 trial), assertion kept. |
| `test_h8` | Seeded `N` flows into MinBTL and moves the verdict | **Survives intact** — both verdicts unchanged. Two VIF=1 literals superseded; update to 181.67 / 2.876. |
| `test_h7` | Seeded `N` flows into DSR and moves the **verdict** | **Survives as a property; coverage lost** on a defective fixture (`ρ̂=+0.55`). Must be **rebuilt**, not accepted. Differential assertions kept verbatim. |

**Nothing in this section is a blanket acceptance and none of the three is closed by this
ruling.** Two require fixture edits by the seat that owns those files; until they land, the
firm's green floor is honestly lower and the CIO should keep recording it that way.

---

## 5. What I did NOT rule, and why

**`test_mbs_12` (I-076) is not adjudicated here and stays red.** It is not among the four items
dispatched, and it is the one open item where the remedy on offer — widening an `[inferred]`
20% band to 26% *after* measuring a 25.4% miss on one draw of nine — is an
adjust-the-threshold-to-fit-the-result operation on its face. That may still be the right
answer (R-16's qualitative finding, a 4× reduction in aggregation-evasion spread at ρ=0.83,
plainly holds), but it needs its own written ruling with the band re-derived from something
other than the observed miss. It does not get decided as a footnote to another dispatch. It
remains open, owned by me, blocking I-057 Item 1 independently of everything above.

**I did not touch `test_holdout_p1.py` or `test_seeded_n.py`.** Ruling on them was the task;
editing them was not, and three of my five rulings in §4 are instructions to another seat
precisely so that the seat that owns those acceptance tests applies them.

**I did not touch `harness/castellan/`.** RULING 005-A requires a one-line change to
`stats.deflated_sharpe_ratio_serial` and it is Seat 9's to make.

---

## 6. The ledger — where the suite stands and what each remaining red is waiting on

| Stage | passed | failed | total |
|---|---:|---:|---:|
| Start of this dispatch [measured] | 239 | 7 | 246 |
| **After Item 1 + RULING 005-B edits [measured]** | **241** | **5** | **246** |
| After RULING 005-A (Seat 9, D-2 clamp) [projected] | 242 | 4 | 246 |
| After RULING 005-C, 005-D, 005-E fixture edits [projected] | 245 | 1 | 246 |
| After a separate I-076 ruling | 246 | 0 | 246 |

The five current reds and their owners:

| Test | Waiting on | Owner |
|---|---|---|
| `test_mono_03` | RULING 005-A, the D-2 clamp | Seat 9 |
| `test_G2` | RULING 005-C, one logged trial in the `registry` fixture | owner of `test_holdout_p1.py` |
| `test_h8` | RULING 005-D, two literals → 181.67 / 2.876 | owner of `test_seeded_n.py` |
| `test_h7` | RULING 005-E, i.i.d. candidate + serial comparand, differential kept | owner of `test_seeded_n.py` |
| `test_mbs_12` | a separate I-076 ruling, not yet written | me |

**I-057 does not close.** §11.3: `test_monotone_conservatism.py` is not partitionable and
`test_mono_03` is red, so neither Item 1 nor Item 2 closes; and `test_minbtl_serial.py` is
independently red on `test_mbs_12`, so Item 1 is blocked twice. `test_dsr_serial.py` is now
**10/10 green** [measured] and `test_vif_estimator.py` remains 16/16, so Item 2 is one Seat 9
one-liner from closeable. **I-057 stays open and I say so, which is what §11.3 committed me to
in advance.**

---

## 7. Implementation change required from Seat 9

Exactly one, and it is one line plus its docstring:

```
# harness/castellan/stats.py :: deflated_sharpe_ratio_serial
- z_serial = z_iid / math.sqrt(vif)
+ z_serial = z_iid / math.sqrt(max(vif, 1.0))   # VALIDATION-RULING-005-A (D-2 as amended):
+                                               # the divisor clamp is the direct analogue of
+                                               # M-2's max(vif, 1.0); C-1(iv) fails without it
+                                               # at vif < 1, z < 0. The outer min (D-6) stays.
```

The `ValueError` guards on non-finite / `vif <= 0` are **unchanged**. The outer
`min(Φ(z_serial), Φ(z_iid))` is **unchanged and must not be removed** — C-2 requires both
enforcements. `test_mono_03` goes green on this change and no other test's behaviour moves
(measured: the two constructions are bit-identical for every `vif ≥ 1`).

**Seat 9 should also be told, in the dispatch, that its refusal to adopt this unilaterally was
correct and is recorded as correct.** The construction it identified is the one being adopted,
under Validation's authority rather than the implementer's, which is the only difference
between this outcome and the one it declined — and that difference is the whole of the
pre-authored test regime's value.

---

## 8. Issues filed

Range allocated I-065–I-069; **I-065 through I-068 taken, I-069 unused.**

| # | Severity | Subject |
|---|---|---|
| I-065 | **HIGH** | VALIDATION-SPEC-002 D-2 as authored violates its own C-1(iv): `DSR_serial` **increases** with `vif` on the `vif < 1` branch when `z < 0` (3,848 violations / 200,000 draws [measured]). Spec defect, found by the implementer, correctly not fixed unilaterally. D-2 amended to clamp the divisor (RULING 005-A). Includes the root cause: `test_mono_05` sweeps `vif ∈ (0,50]` but carries C-1(iv) only on the MinBTL side, leaving the DSR side unswept below 1 — a gap in my own test inventory. Closes on Seat 9's one-line change + the (iv) sweep extension. |
| I-066 | MEDIUM | M-6/D-8's mandatory criterion renames rescinded (RULING 005-B). Presentational, moves no graded quantity, and the protection is delivered by the threshold string, the note and M-11. Recorded as a specification amendment, with the test applied to confirm it is not an I-029(d) operation, because the conclusion was the cheap one. |
| I-067 | MEDIUM | `test_seeded_n.py::_calibrated_returns` does not do what its docstring claims: `np.argsort` is not stable by default, the intended alternation is not produced, and the helper emits `ρ̂ ≈ +0.55` / `VIF ≈ 10.6–12.6` [measured]. This is the fixture underneath `test_h7`/`test_h8` and any other test using it for a serially-sensitive statistic. No live consequence today (0 hypotheses in the registry); it is a test-integrity defect that produced a false casualty in I-078. |
| I-068 | MEDIUM | I-078's three protected casualties ruled per test (RULING 005-C/D/E): `test_G2` property survives on 2 of 3 sub-assertions with the 3rd superseded; `test_h8` survives intact with two literals superseded; **`test_h7` loses real coverage and must be rebuilt, not accepted.** Tracks the three fixture edits owed by the owning seats and the green floor until they land. |

**I-076 remains open and unadjudicated** by deliberate choice (§5). **I-057 remains open** (§6).

---

## 9. Addressed to the Principal

Three things, none of which requires an act from you.

**(1) A specification I wrote contained a defect that ran permissive, and the implementer
caught it.** VALIDATION-SPEC-002's D-2 made the Deflated Sharpe Ratio *less* conservative as
measured serial dependence rose, on one branch. It was found because Seat 9 implemented the
clause literally, saw the resulting test fail, and escalated in writing instead of adopting the
obvious fix. The structure you insisted on — pre-authored tests, an implementer forbidden to
amend the spec, a written escalation instead of a green suite — is what converted my error into
a filed issue rather than into a permissive statistic in a live Gate. I would rather report
that than have it not happen. It is filed as I-065.

**(2) The nearest thing to a threshold movement in this dispatch was available under a
respectable rationale, and it was declined.** I-077 offered me the option of ruling
`test_mono_03`'s assertion an overreach on the grounds that it injects an input the estimator
cannot produce. Taking it would have retired the one test that detects the defect in (1). The
grounds were plausible and the wording was mine to write. I am recording that it was available.

**(3) No Charter constant moved and none is requested.** `DSR_MIN = 0.95`, `T_STAT_HURDLE =
3.0`, `EMBARGO_FRACTION`, `HOLDOUT_FRACTION` and every other §4.2 constant are untouched. Two
VALIDATION-SPEC-002 clauses are amended by this ruling — D-2 (tightening, on an unreachable
branch) and M-6/D-8's rename (presentational, no graded quantity) — both within my own
authority over my own specification, both recorded, neither requiring a §2 act. The holdout
vault was not opened, listed, or read; no passphrase was requested or held; `book/registry.db`
stands at 0 hypotheses / 0 trials.

---

*Ruled by the Head of Quantitative Validation, 2026-08-05. Not committed — per dispatch
constraint, no commit was made this session. Files modified:
`harness/tests/test_minbtl_serial.py`, `harness/tests/test_dsr_serial.py`. Files ruled on but
deliberately not modified: `harness/tests/test_monotone_conservatism.py`,
`harness/tests/test_holdout_p1.py`, `harness/tests/test_seeded_n.py`,
`harness/castellan/stats.py`.*
