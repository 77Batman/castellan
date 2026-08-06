# VALIDATION-SPEC-003 — The trial-count criterion: over-budget must FAIL, and the authorization edge that is the only way past it (I-022)

**Seat:** Head of Quantitative Validation (Seat 3) · **Reports to:** the Principal
**Date:** 2026-08-06
**Status:** BINDING on Seats 1, 2, 6–10. Appealable only to the Principal, in writing.
**Instrument:** the substantive fix for **I-022**, escalated MEDIUM → HIGH by the CIO on
2026-08-06 and routed to Validation by the Principal as owner of harness correctness.
Specifies clauses **B-1 … B-30**. Amends no Charter §4.2 constant and requests none.
**Dispatched by:** the CIO, S2-D-026. Nothing in the dispatch binds the content.
**Type:** specification, authored **before** implementation, with pre-authored acceptance
tests. **No file under `harness/castellan/` is modified by this document or by the seat that
wrote it.** No backtest run, no hypothesis opened, no trial registered, `book/vaults/`
untouched, no holdout passphrase requested or held. `book/registry.db` stands at
**0 hypotheses / 0 trials** [measured, before and after].

House rule 6 throughout: **[measured]** = read or computed in this repository this session ·
**[cited]** = external source or internal document named inline · **[inferred]** = reasoned
from measured facts · **[assumed]** = an unverified premise, flagged as such.

---

## 0. THE CRITERION IN ONE SENTENCE, AND WHAT IT REPLACES

> **A family's own post-seal logged trials are graded, trial by trial in the order they were
> logged, against the effective budget in force at the moment each was logged — sealed budget
> plus only those increments the registry can prove were authorized before that trial existed
> — and any trial logged past that line is a FAIL of Gate 1, never a note.**

What it replaces, verbatim from `harness/castellan/gates.py:334–338` [measured, this session]:

```python
over = fam.trial_budget and fam.n_logged > fam.trial_budget
criteria.append(_crit(
    "Trial count N (registry)", fam.n_trials,
    f"logged; budget {fam.trial_budget}", True,
    "OVER BUDGET — flagged to Director of Research" if over else ""))
```

Four defects live in those five lines, not one. I-022 names the first. **The other three
survive the obvious fix and are the reason this document exists rather than a one-line patch:**

| # | Defect | Survives `True → not over`? |
|---|---|---|
| 1 | The verdict is the literal `True`. `over` is computed and used only to write a note. | No — this is I-022 |
| 2 | `fam.trial_budget and …` **short-circuits at 0**. A family sealed with `trial_budget = 0` (or negative) never evaluates the comparison at all, and reads PASS with unbounded trials. | **Yes.** Filed I-100 |
| 3 | `fam.n_logged` is **chain-summed transitively** across `predecessor_family`. Under a working criterion every successor whose chain out-spends its own budget is born over budget with zero acts — the fix would punish the honest declaration of a predecessor, which is the anti-gaming control inverted. | **Yes.** Filed I-101 |
| 4 | A budget compared only as a **final aggregate** legalises *spend first, authorize after*, which is the pre-registration failure the whole apparatus exists to prevent. | **Yes.** Answered by B-9 |

**Authorship, recorded because the Principal put it on the record himself and because it
belongs in the log rather than in a dispatch.** The hardcoded `True` is the Principal's own
line, written at the harness's creation. It was disclosed by Seat 9 at
`DATA-IMPL-002` §13 — *"the verdict is hardcoded PASS with a note, even when `n_trials >
trial_budget` … a design question I am flagging rather than silently passing over"*
[measured, `research/DATA-IMPL-002-acceptance-remediation.md:346`] — and reached no Issue Log
entry for eight days. The Principal's own adopted formulation stands: **a disclosed defect
that reaches no log is functionally undisclosed.** I add one sentence to it, because this
document is the second instance in three days: *a disclosure that reaches a log but no test is
functionally a promise.* I-022 was logged on 2026-07-28 and remained live because nothing in
the suite asserted the property.

---

## 1. SCOPE AND AUTHORITY

### 1.1 What this document may do

Charter §4.3(6) and house rule 3 make the trial counter a Gate 0 admissibility condition and
make N the denominator of every Part IV statistic. Charter Seat 3 gives Validation "the
backtest harness's statistical correctness." **A criterion that computes a violation and then
reports PASS is a correctness defect, and specifying its repair is inside this seat's
mandate.** The Principal has ruled it there explicitly.

### 1.2 What this document may not do, and does not

- **No Charter §4.2 constant moves.** `T_STAT_HURDLE`, `DSR_MIN`, `PBO_MAX_PAPER`,
  `EMBARGO_FRACTION`, `HOLDOUT_FRACTION`, `CSCV_PARTITIONS_S`, `WFE_MIN` are untouched and
  none is requested.
- **No new numeric threshold is invented.** Every number this criterion consumes is either a
  sponsor's own sealed declaration (`trial_budget`, `n_inherited`) or a quantity the harness
  already computes for another criterion (`N_max`, via M-4/M-5). **The one thing I refused to
  do is invent a cap on how large a budget may be, or how much an extension may add** — see
  B-27. A number I chose would be a threshold I set on the sponsor's search, and I have no
  basis for it that the existing machinery does not already price better.
- **No criterion is renamed.** RULING 005-B's precedent is one week old and its reasoning
  applies unchanged: a criterion name is not graded, enters no arithmetic, and is what eight
  protected acceptance tests resolve criteria by. The row keeps the name
  `"Trial count N (registry)"`.
- **No test in `harness/tests/` outside the two files named in §7 is touched.**

### 1.3 Disposition on the Principal's three-element shape

He offered it as non-binding input on a matter inside my mandate, and said so. I record the
disposition element by element before the clauses, so a reader can see what is his, what is
mine, and where I departed.

| Element, as offered | Disposition |
|---|---|
| **(1) Over-budget must produce FAIL, not an annotation.** | **ADOPTED unchanged.** B-6. It is also the only element that is not really a choice: V-3 of `VALIDATION-SPEC-002` already rules that a requirement whose every input is known and unmet is FAIL and not INSUFFICIENT-DATA, and every input here is known. |
| **(2) Continuation solely via a registry-logged Director budget-extension event that the criterion reads — "an authorization edge, computed never narrated."** | **ADOPTED in mechanism, with three departures.** (a) The event is **prospective only**, enforced by per-trial timestamp ordering (B-9): an extension logged after the overspend authorizes nothing. (b) **The Director alone cannot issue one** — a discretionary extension requires a countersignature from a distinct seat (B-13/B-14). (c) The extension comes in **two forms**, and the second is not a Director act at all (B-16). |
| **(3) The criterion must be stage-aware, so PREREG-002's Stage 2 stays locked until the measured-ρ̂ unlock event exists.** | **OUTCOME ADOPTED, CONSTRUCTION REPLACED.** I do not build a "stage" concept. A stage is a contingent budget increment whose unlock predicate is a measured quantity — which is element (2)'s mechanism with a computed admissibility test instead of a human one. **PREREG-002 gets its lock and the criterion contains no field, token, or constant that PREREG-002 alone declares** (B-16 … B-22, proved by `test_tbe_17`). |

**The departure that most needs justifying is (2b), because it takes authority away from a
seat the Principal named.** The reasoning is at B-14 and it is short: the harness cannot
authenticate anyone, so `issuer` is a claim; the only control available against a seat acting
alone inside its own scope is to make a single seat's act structurally insufficient; and the
Charter already models this asymmetry in Seat 4's terms — **brakes are unilateral,
accelerators are collective.** A budget extension is an accelerator. The Principal himself
remains able to issue one alone (B-15), because his authority is final and because the logged
event *is* the override record the Charter §4 requires.

---

## 2. THE GENERAL RULE THAT GENERATES THE SPECIFIC ANSWERS · B-1 … B-5

> **B-1 · The graded quantity is the family's OWN post-seal logged trials.**
> `n_own_logged(family)` = `COUNT(*)` of `trials` rows whose `family` column equals this
> family exactly. **Not transitive.** The predecessor chain's spend is prior search: it is
> priced where it belongs, in `N` — which flows into MinBTL, `N_max` and DSR through
> `family_stats`, transitively, already, and costs the sponsor there. Charging it a second
> time against the successor's budget would make an honest `predecessor_family` declaration
> the expensive option, which inverts the control that Ruling 001 §3.3 F4 built.
> **Consequence, disclosed rather than discovered:** a sponsor can chain successor families to
> obtain fresh budgets. That route is priced by `N` and gated by the fact that each successor's
> budget is itself a sealed, Director-authored declaration. **It is not additionally capped
> here, and B-25 requires the chain total on the report face so the pattern is visible on
> every report.**

> **B-2 · The reported quantity is unchanged.** `Criterion.value` stays `fam.n_trials`
> (= `n_inherited` + chain-summed `n_logged`). The criterion grades one number and reports
> another, and both are on the row (B-24/B-25). H-12's rule holds: a report may not render a
> bare N that launders a declaration into a measured-looking integer.

> **B-3 · `n_inherited` is never charged against the budget.** Declared prior search carries
> no timestamps, was not spent post-seal, and is already the subject of H-5b's own refusal.
> The budget governs the firm's post-seal search. This is H-10/H-11's keying, preserved.

> **B-4 · THE TIE-BREAK RULE, from which most of §4's answers follow mechanically.**
> **A defect in an authorization artifact that could only TIGHTEN the criterion is disclosed
> on the report face and does not fail the Gate. A defect that could LOOSEN it is a FAIL.**
> A malformed extension (which could raise a budget) fails. A malformed *withdrawal* (which
> could only fail to lower one) is disclosed. An unparseable event kind the criterion does not
> recognise authorizes nothing and is inert. **Non-permissive by construction; there is no
> case where the implementer has to judge which way to resolve an ambiguity.**

> **B-5 · Nothing in this criterion is cached.** V-1's rule, applied here: every quantity is
> recomputed from the registry as it stands at the `evaluate_gate1` call. No extension's
> admissibility is read from a sealed field, carried forward from a prior evaluation, or taken
> from what the event says about itself. **Two evaluations of the same family may reach
> different budget verdicts because the registry grew between them; both reports stand and
> neither is amended** (V-2).

---

## 3. THE VERDICT · B-6 … B-12

> **B-6 · Over-budget is FAIL.** Where any trial was logged past the effective budget in
> force at its own moment (B-9), the criterion's verdict is `FAIL`. **Not a note, not
> INSUFFICIENT-DATA.** One FAIL fails the Gate (Charter §4.4). V-3's reasoning applies without
> modification: the sealed budget is known, the trial timestamps are known, the increments are
> known or provably absent. **INSUFFICIENT-DATA is for a quantity that cannot be established.
> This one is established and it is not met.**

> **B-7 · A non-positive sealed budget with one or more own logged trials is FAIL.**
> `trial_budget <= 0` and `n_own_logged >= 1` ⇒ FAIL, with note prefix
> `"NO AUTHORIZED BUDGET: "`. This is I-100 and it is the defect that survives the obvious fix:
> the existing `fam.trial_budget and …` short-circuits to falsy at 0 and never evaluates the
> comparison. **A family that pre-registered no authorization and then spent trials is the
> purest case the criterion exists for, and the current construction is the only one under
> which it passes.**

> **B-8 · Zero own logged trials leaves the existing branch untouched.** Where
> `fam.n_logged == 0`, the criterion's existing INSUFFICIENT-DATA branch (H-10/H-11, keyed on
> the chain-summed figure) governs and **is not modified by this document**. Where the chain
> has logged trials but this family has none (`n_own_logged == 0`, `fam.n_logged >= 1`), the
> family is vacuously within budget and the budget dimension is PASS.

> **B-9 · THE ORDERING WALK — per trial, not per aggregate.** Let `t₁ ≤ t₂ ≤ … ≤ t_m` be the
> `created_utc` of this family's own logged trials, ascending, `m = n_own_logged`. Let
> `eff(t)` be the effective budget in force at time `t` (B-10). The family is within budget
> **iff for every k ∈ [1, m], `k ≤ eff(t_k)`.**
>
> **Why not the aggregate.** Budget 47, sponsor logs 60 trials, Director then issues a +20
> extension: the aggregate test reads `60 ≤ 67` and PASSES. The walk reads trial 48 as logged
> when `eff` was 47 and FAILS. **The aggregate test legalises spend-first-authorize-after,
> which is not a budget at all — it is a receipt.** This is the single most important clause in
> the document and it is also the complete answer to back-dating (§4.2).

> **B-10 · The effective budget function.**
> ```
> eff(t) = sealed_trial_budget + Σ { admitted_increment(e) : e ∈ E, effective_from(e) ≤ t }
> ```
> where `E` is the set of `trial_budget_extension` events for this family, `admitted_increment`
> is B-13/B-16's admissibility arithmetic (0 for any refused, withdrawn or malformed event),
> and `effective_from(e)` is B-12's.

> **B-11 · The reported failure is the FIRST violating trial, not the count.**
> Note format, mandatory: `"OVER BUDGET: trial {k} of {m} was logged when the effective budget
> was {eff(t_k)} (sealed {sealed}); …"`. A count of the overage tells a reader how far past the
> line the family is; the index tells them **when authorization ran out**, which is the fact the
> Director and the Devil's Advocate both need and the only one that distinguishes a family that
> over-ran by one from a family that ignored the budget from trial 6 onward.

> **B-12 · `effective_from`.** For a CONTINGENT extension (B-16): the event's own
> `created_utc`. For a DISCRETIONARY extension (B-13): `max(extension.created_utc,
> earliest_valid_countersignature.created_utc)` — **an authorization is complete only when
> both halves exist**, which closes "issue now, countersign after the spend."

---

## 4. THE AUTHORIZATION EDGE · B-13 … B-22

Two forms, one mechanism. Both are `trial_budget_extension` events in the registry's
append-only `events` table. **There is no third route past the budget and no `evaluate_gate1`
keyword argument that can supply one** — Acceptance 001 C-6's rule, which removed the
caller-asserted `holdout_opened_once` boolean from the firm's most-protected criterion, binds
here identically: a narrated authorization is not an authorization.

### 4.1 Common schema · B-13

> **B-13 · A `trial_budget_extension` event's `detail` MUST contain exactly these keys, with
> these types. Any deviation is MALFORMED (B-23).**
>
> | Key | Type | Constraint |
> |---|---|---|
> | `mode` | str | `"DISCRETIONARY"` or `"CONTINGENT"`. Any other value is malformed. |
> | `increment` | int | `> 0`. A bool is not an int here (H-2's precedent). A float is malformed, not truncated. |
> | `issuer` | str | non-empty, stripped |
> | `reason` | str | non-empty, stripped |
> | `authorization_ref` | str | non-empty; a repo-relative path to the written artifact. **Must be unique among this family's admitted extensions** — B-26. |
> | `n_logged_at_issue` | int | `>= 0`; the family's own logged trial count at issue time. Cross-checked — B-21. |
> | `predicate` | dict | REQUIRED iff `mode == "CONTINGENT"`; MUST be absent otherwise |
>
> Unknown **extra** keys are permitted and ignored: forbidding them would make every future
> provenance field a breaking change, and an extra key cannot loosen anything (B-4).

### 4.2 The DISCRETIONARY form · B-14 … B-15

> **B-14 · A discretionary extension requires a countersignature from a distinct seat.**
> `issuer` must be `"director-of-research"` or `"principal"`. Where `issuer` is the Director,
> the increment is admitted only if a `trial_budget_extension_countersigned` event exists for
> this family with `detail.extension_event_id` equal to the extension's `event_id`,
> `detail.countersigner ∈ {"quant-validation", "principal"}`, `countersigner != issuer`, and
> `created_utc >= ` the extension's. The **earliest valid** countersignature governs.
>
> **Why, stated plainly and with its limit stated too.** The harness has no principal
> identity — there is no authentication anywhere in `registry.py`, and any seat holding a
> registry handle can write any event with any `issuer` string (filed I-103). `issuer` is
> therefore a **claim**. Against a determined forger two strings cost exactly what one costs,
> and I am not going to describe this control as though it were security. **What it does
> control is the failure mode this firm actually has**: a seat, under schedule pressure, taking
> an action that is inside its own scope and that nobody else has to see. A countersignature
> requirement makes that structurally impossible without a second seat's name on the record and
> a second artifact to point at. That is the Charter's own asymmetry — *brakes are unilateral,
> accelerators are collective* — applied to the accelerator this criterion guards.

> **B-15 · The Principal issues alone.** `issuer == "principal"` requires no countersignature.
> His authority is final (Charter §4), and the event **is** the permanent override record the
> Charter requires for every override. No seat may write `issuer: "principal"` on his behalf;
> the harness cannot detect a seat that does, and I say so here rather than implying otherwise.

### 4.3 The CONTINGENT form · B-16 … B-20 — *this is the stage lock, and it is generic*

> **B-16 · A contingent extension is authorized by a computation, not by a person, and is
> therefore safe to self-issue.** The event declares a predicate from a **closed vocabulary**;
> the criterion **re-evaluates that predicate at evaluation time and never trusts the event's
> assertion that it held.** Forging the event buys nothing, because the number that governs is
> recomputed. **This is why the contingent form needs no countersignature and why "self-issued"
> is not a hazard for it:** the authorization is arithmetic, and arithmetic does not care who
> requested it.

> **B-17 · The vocabulary is closed and has exactly one member at v1.**
> `predicate.name` must be `"n_max_admits_declared_ceiling"`. `predicate.params` must be
> present and **empty**. Any other name, or a non-empty `params`, is MALFORMED — it does not
> degrade to a permissive default, and it routes to Validation (§6.2). **An open vocabulary
> would put a narrated condition inside the firm's most-protected criterion, which is I-014's
> shape exactly.** Adding a member is an amendment to this document, by me, not an
> implementer's call.

> **B-18 · `n_max_admits_declared_ceiling`, in full.**
> ```
> declared_ceiling_base = fam.n_inherited + sealed_trial_budget
> N_max                 = min(n_max_admissible_iid, n_max_admissible_serial)      # M-5
> allowed               = clamp(N_max - declared_ceiling_base, 0, increment)
> ```
> `N_max` is the figure the length criterion already computes and the report already carries
> (`ValidationReport.n_max_admissible_iid` / `.n_max_admissible_serial`). **No new statistic is
> introduced by this document.**

> **B-19 · Unevaluable ⇒ zero, and the family is over its proven budget.** Where `N_max`
> cannot be computed — no `oos_index`, VIF ineligible, `sr_ann <= 0`, or `fam.n_logged == 0` —
> `allowed = 0` and the event's status is `REFUSED-PREDICATE`. **The criterion's verdict is then
> FAIL, not INSUFFICIENT-DATA, if the family is over its sealed budget without the increment.**
> The predicate is unestablished; the budget is established; the family exceeded the budget it
> can prove. B-4's tie-break, and V-3's reasoning, both land the same way.

> **B-20 · Contingent increments are capped IN AGGREGATE, not per event.** The sum of admitted
> contingent increments for a family is capped at `max(0, N_max − declared_ceiling_base)`.
> Without this, ten contingent events declaring 32 each would sum to 320 against a ceiling that
> admits 32 once. Admission order is `created_utc` ascending; the aggregate cap is consumed in
> that order and later events are `CAPPED` at whatever remains.

> **B-21 · The `n_logged_at_issue` cross-check.** An extension is MALFORMED if
> `detail.n_logged_at_issue` differs from the count of this family's own trials whose
> `created_utc` is strictly less than the event's `created_utc`. **This is the events table's
> analogue of P4's shadow copy**, and it is the only defence available against a `created_utc`
> forged by raw SQL: a back-dated row must now also make the trial ledger agree with a count it
> declared, at a timestamp it moved. It is not proof against a careful forger and is not
> presented as one (I-102).

> **B-22 · Genericity, as a testable property.** The criterion reads **no field, token,
> constant or string that any single pre-registration declares.** `gates.py`'s source must
> contain none of `PREREG-002`, `PREREG_002`, `prereg002`, `rho_plan`, `0.034`, `stage_2`,
> `crypto-funding`, `funding-basis` (case-insensitive), and `evaluate_gate1`'s signature must
> gain no parameter naming a budget, a stage, or an authorization. `test_tbe_17` asserts both
> against `inspect`. **Bare integer literals are deliberately NOT banned** — `gates.py`
> legitimately contains `32.0` as the breakeven bisection's upper bracket [measured,
> `gates.py:714`], and a test that cannot distinguish that from a smuggled budget constant is a
> test that will be deleted the first time it fires. **A criterion that only understands one
> document is a criterion that silently passes every other**, and that failure mode is
> invisible until the second document arrives.

---

## 5. MALFORMATION, WITHDRAWAL, AND THE REPORT FACE · B-23 … B-27

> **B-23 · A malformed, un-withdrawn extension event FAILS the criterion — even where the
> family is comfortably inside its sealed budget.** Note prefix `"MALFORMED AUTHORIZATION: "`,
> naming the `event_id` and the specific malformation. **Rationale:** a malformed authorization
> artifact in the registry is an attempted authorization the harness could not verify, and this
> firm's answer to an unverifiable authorization is refusal, not tolerance (B-4). The rule is
> deliberately absolute, because "it was only a typo and the family didn't need it anyway" is
> the exact sentence under which a tolerance gets established.

> **B-24 · The documented repair is a withdrawal, not an edit.** A
> `trial_budget_extension_withdrawn` event with `detail.extension_event_id` equal to the
> target's `event_id` renders the target inert: no increment, no malformation FAIL, status
> `WITHDRAWN`. The registry is append-only; nothing is deleted; the error and its repair are
> both permanently on the record. A withdrawal referencing an unknown `event_id` is disclosed
> and does **not** fail the Gate — it could only tighten (B-4). **A withdrawal of a contingent
> unlock after Stage-2-style trials were spent makes those trials unauthorized and the family
> FAILs. That is correct and is not a trap:** withdrawal is a tightening act and tightening is
> always admissible.

> **B-25 · The criterion's row.** Name unchanged (`"Trial count N (registry)"`, RULING 005-B).
> `value` unchanged (`fam.n_trials`, B-2). `threshold` must satisfy both contract regexes:
> ```
> effective budget (\d+)          sealed (\d+)
> ```
> Reference form: `f"own-family logged <= effective budget {eff_final} (sealed {sealed}"` +
> `f" + {total_admitted} extension)"` where extensions exist, else `")"`. Where the chain-summed
> logged count differs from the own count, the note must carry the substring
> `f"chain-summed logged {fam.n_logged}"` — B-1's disclosed residual, made visible on every
> report rather than tracked in a memo.

> **B-26 · One authorization artifact, one increment.** Two admitted extensions for a family
> sharing an `authorization_ref` are malformed from the second onward (by `created_utc`). This
> closes salami-slicing a single written approval into ten increments.

> **B-27 · Report fields, NOT `Criterion` rows** (M-10 / E-10's precedent, guarded by
> `test_hac_t14`): `trial_budget_sealed`, `trial_budget_effective`, `n_own_logged`, and
> `budget_extensions` — a list of `{event_id, mode, issuer, countersigner, increment_declared,
> increment_admitted, status, created_utc, authorization_ref}` with `status ∈ {ADMITTED,
> CAPPED, WITHDRAWN, REFUSED-MALFORMED, REFUSED-UNCOUNTERSIGNED, REFUSED-SELF-ISSUED,
> REFUSED-PREDICATE}`. **Every extension appears, including every refused one.** This ledger is
> the strongest thing the harness can actually do about self-issuance: it cannot authenticate,
> but it can guarantee that no extension is ever invisible to the reader of a Gate report.
> **I set no cap on `increment` and no cap on `trial_budget`.** A cap would be a number I chose
> for someone else's search with no basis; the existing machinery prices a large N far better
> than a constant of mine would, through MinBTL, `N_max` and DSR's σ_SR benchmark.

---

## 6. WHAT SEAT 9 IMPLEMENTS MECHANICALLY VS. WHAT ROUTES BACK · B-28 … B-30

### 6.1 Mechanical — implement as written, no consultation

| Clause | Why mechanical |
|---|---|
| **B-1 / B-2 / B-3** | Which column is counted. One new non-transitive registry accessor (B-28). |
| **B-6 / B-7 / B-8** | Three stated verdicts on three stated conditions. |
| **B-9 / B-10 / B-11 / B-12** | A sort and a loop with stated arithmetic and a stated note format. |
| **B-13 / B-14 / B-15** | Schema validation against an exhaustive key/type table and two fixed allow-lists. |
| **B-16 … B-21** | Closed-form arithmetic on quantities the harness already computes, one `clamp`, one aggregate cap consumed in timestamp order, one equality cross-check. |
| **B-23 / B-24 / B-26** | Stated verdicts, stated prefixes, one uniqueness check. |
| **B-25 / B-27** | Two contract regexes and four report fields with a stated shape. |

> **B-28 · The one new registry accessor.**
> ```python
> def own_trial_times(self, family: str) -> list[float]:
>     """created_utc of trials whose `family` column is exactly `family`,
>     ascending. NOT transitive -- VALIDATION-SPEC-003 B-1: the budget
>     grades this family's own post-seal search; the chain's spend is
>     priced by N, not by this criterion."""
> ```
> and **one module-level pure function in `gates.py`**, so B-18 is unit-testable without a Gate
> fixture:
> ```python
> def contingent_increment_allowed(n_max: int | None,
>                                  declared_ceiling_base: int,
>                                  declared_increment: int) -> int:
> ```
> returning `0` for `n_max is None`. `test_tbe_15` grades this function directly.

> **B-29 · Ordering inside `evaluate_gate1`.** The criterion consumes `n_max_admissible_*`,
> which the length block computes further down. **The criterion must remain FIRST in
> `report.criteria`** — a Gate report is read budget-first, because N is the denominator of
> everything below it. How Seat 9 achieves that (hoist the `N_max` computation, or build the
> row later and insert at index 0) is an implementation choice and is Seat 9's alone.

### 6.2 Judgment calls — route back to me before implementing

| Trigger | Why it is not the implementer's |
|---|---|
| **A `predicate.name` outside B-17's vocabulary, or a non-empty `params`, appears in any real family.** | Extending the vocabulary is a specification act. Do not add a member to make something pass. |
| **A family's verdict turns on `REFUSED-PREDICATE`** — i.e. it would be within budget if `N_max` were computable. | That is a family whose length criterion is also in trouble; I want to see both together, and B-19's non-permissive resolution is exactly the kind of clause a sponsor will ask to have relaxed. |
| **Any request to grandfather a family that is over budget at the moment the fix lands.** | B-30. The answer is no; the request itself is a finding. |
| **Any proposal to make the budget check transitive across the predecessor chain** (i.e. to reverse B-1). | It is arguable and I argued the other way. It is not arguable *by the implementer, at implementation time*. |
| **Any real family where two extensions share an `authorization_ref` for an innocent reason.** | If B-26 catches an honest pattern I have not anticipated, the fix is the clause, not the family — and it is mine to write. |
| **Any test in `test_trial_budget_enforcement.py` that cannot be met as specified.** | Ruling 004 §11's standing term, which binds me as hard as Seat 9: escalate in writing, do not amend. It has caught a Validation-authored defect three times this sprint (I-058, I-070, I-065). |

---

## 7. THE THREE GAMING QUESTIONS, ANSWERED EXPLICITLY

The CIO asked for these to be settled rather than left to be discovered. Each answer is a
clause above; this section is the answer in one place.

### 7.1 A budget-extension event that is malformed, back-dated, or self-issued

**Malformed** — B-23. The increment does not count **and** the criterion FAILs, even where the
family never needed the increment. The documented repair is a withdrawal event (B-24), which
leaves both the error and the repair permanently on the record. **There is no tolerance for a
malformed authorization artifact and there is deliberately no "harmless typo" carve-out**,
because the carve-out is the thing that gets used.

**Back-dated** — B-9 and B-21, and the answer has two layers.
1. **The criterion never reads a date the caller supplied.** `TrialRegistry.log_event` writes
   `created_utc` from the system clock; the API has no parameter for it [measured,
   `registry.py:605–612`]. Any `issued_utc`, `dated`, or `as_of` field inside `detail` is a
   claim and is **never read for ordering**. A sponsor who wants an extension to predate a
   trial must have logged it before the trial.
2. **Even a `created_utc` forged by raw SQL buys little**, because B-9 walks trial by trial and
   B-21 cross-checks the event's declared `n_logged_at_issue` against the number of the
   family's own trials that actually precede the forged timestamp. The forger must now move a
   row *and* make an independently-recorded count agree with it.
3. **The residual is real and I am not hiding it** (I-102): the `events` table has no
   `hypothesis_sealed`-style shadow copy, so a sufficiently careful raw-SQL write is not
   detectable. That is a property of the registry, not of this criterion, and closing it is a
   separate piece of work I am filing rather than pretending away.

**Self-issued** — the honest answer is in two halves, and only one of them is comfortable.
- **For the CONTINGENT form, self-issuance is harmless by construction** (B-16). The
  authorization is a recomputation the criterion performs at evaluation time; the event's own
  claim that the condition held is never trusted. The sponsor may log its own unlock. It buys
  nothing it would not have been given anyway.
- **For the DISCRETIONARY form, self-issuance is the whole risk**, and the harness **cannot
  authenticate anyone** (I-103). What I can do, and have: require a distinct countersigner
  from a narrow allow-list (B-14), require a named written artifact and refuse to let one
  artifact be spent twice (B-26), and put **every** extension — admitted, capped, withdrawn and
  refused — on the report face with its issuer, its countersigner and its reason (B-27). **That
  makes a self-issued extension impossible to take without a second seat's name on it and
  impossible to take invisibly. It does not make it impossible to forge, and I will not
  describe it as though it did.**

### 7.2 Is a family already over budget when the fix lands retroactively FAIL?

**Yes. There is no grandfather clause and none is available.**

> **B-30 · No grandfathering.** A family over its effective budget at the moment this
> criterion lands FAILs Gate 1's trial-count criterion on the next evaluation, regardless of
> when its trials were logged, and regardless of any PASS a prior report may show.

Three reasons, in the order they matter.

1. **Nothing changes except that the harness now computes what the document always said.**
   Charter house rule 3 and §4.3(6) made the trial budget binding from the firm's first day;
   `trial_budget` has been a sealed binding pre-registration field since the P-series. The
   budget was never a suggestion that this document is converting into a rule. **A PASS issued
   by the hardcoded `True` was a defect in the harness, not a grant of authorization**, and a
   defect does not vest. This is V-4's reasoning applied to the budget instead of to MinBTL,
   and the firm has already accepted it there: *"the sponsor never had a guarantee; the sponsor
   had an assumption the harness was making silently on the sponsor's behalf, in the sponsor's
   favour. Removing a silent favourable assumption is not retroactive punishment."*

2. **A grandfather clause converts a harness defect into a permanent entitlement for exactly
   the families that benefited from it.** It is the most precisely wrong population to protect.

3. **It costs the firm nothing today** [measured — `book/registry.db` holds 0 hypotheses and
   0 trials, verified before and after this session], which is V-8's position exactly and the
   entire reason to decide it now. **I record that I would rule the same way at non-zero cost,
   so that this ruling cannot later be characterised as cheap-because-nothing-was-at-stake.**
   The seat that would bear it is the seat that over-spent.

### 7.3 Generic, or a criterion that reads one document's field?

**Generic, and it is proved rather than asserted.**

- The criterion contains no PREREG-002 field, token or constant, and `test_tbe_17` asserts that
  mechanically against `inspect.getsource(gates)` (B-22).
- A family with no extension events behaves exactly as before **except** that over-budget now
  FAILs. There is no opt-in, no declaration required, and no stage concept in the schema.
- **PREREG-002 gets its lock as a special case of the general mechanism, with no special
  casing.** It seals `trial_budget = 47` (Stage 1) and `n_inherited = 7`; Stage 2 is one
  CONTINGENT extension with `increment: 32`. B-18's arithmetic then reproduces the document's
  own unlock table exactly, from registry quantities alone:

  | ρ̂ | `N_max` [cited — SPEC-002 §6.2] | `allowed` = clamp(`N_max` − 54, 0, 32) | PREREG-002 §10.5.2 says |
  |---:|---:|---:|---|
  | ≤ 0.034 | 86 | **32** | "the whole of Stage 2" ✓ |
  | ≈ 0.05 | 77 | **23** | "≤ 23 of the 32" ✓ |
  | ≈ 0.10 | 55 | **1** | "≤ 1 of the 32" ✓ |
  | ≥ 0.20 | 31 | **0** | "NONE, and Stage 1 itself is already over" ✓ |

  Four rows, four exact matches, no PREREG-002-specific code. **That is what "generic" has to
  mean to be worth claiming: the general mechanism reproduces the specific document's table
  without knowing the document exists.**

> **RULING 003-A, on an ambiguity in PREREG-002 that would otherwise fall to the implementer.**
> §10.5.2 requires `N_max` to be *"read from the cited table at `VALIDATION-SPEC-002` §6.2 and
> **never interpolated** by this seat."* **A table lookup with no interpolation is undefined
> between its rungs**, and the harness holds `max_admissible_trials`, which is the continuous
> function of which that table is nine printed evaluations. **The function governs.** Where the
> two appear to disagree they do not: the table is a rendering. The practical effect is that a
> family measuring ρ̂ = 0.07 receives the allowance its own ρ̂ earns rather than the next rung
> down, which is more accurate in both directions and is what V-1 requires anyway.
> **Filed I-104**, addressed to the Director, because PREREG-002 is unsealed and this is
> cheaper to conform now than to reconcile against a frozen document later.

> **B-31 · A warning to the Director that this document does not enforce and cannot.**
> The generic mechanism only locks Stage 2 **if PREREG-002 seals `trial_budget = 47`.** If it
> seals the flat `79`, the harness enforces 79, Stage 2's gate does not exist, and §10.5.2
> reads — in a sealed, frozen document — as though it did. **The two-stage construction is a
> registration act, not a prose act.** Filed **I-105, HIGH**, and it is the one finding in this
> document that could still produce a wrong PASS after the fix lands.

---

## 8. TEST INVENTORY AND THE INTENDED RED STATE

Pre-authored by Validation, in a new file, before implementation. **Seat 9 does not modify any
test in it**; a failure is escalated to me in writing (Ruling 004 §11's standing term).

**File:** `harness/tests/test_trial_budget_enforcement.py` — **19 test functions, 27 collected
items** (`test_tbe_12` is parametrised over nine malformations), covering B-1 … B-31.
Measured against the harness as it stands, this session: **26 fail, 1 pass** [measured].

**The single green is `test_tbe_17`, and it is green by construction, not by accident.** It
asserts that `gates.py` contains no PREREG-002 token and that `evaluate_gate1` has gained no
budget/stage/authorization keyword. Both are true today and **must still be true after the
implementation lands** — it is the guard against the fix being fitted to one document, so a
green there before and after is the correct signature. Every other item is red, and every red
is red for the reason its docstring names.

| Test | Clause | Today |
|---|---|---|
| `test_tbe_01_over_budget_is_fail_not_a_note` | B-6 | **RED** |
| `test_tbe_02_at_budget_passes_and_reports_the_effective_budget` | B-25 | **RED** |
| `test_tbe_03_zero_sealed_budget_with_trials_is_fail` | B-7 / I-100 | **RED** |
| `test_tbe_04_negative_sealed_budget_is_fail` | B-7 | **RED** |
| `test_tbe_05_over_budget_fails_the_gate_overall` | B-6 | **RED** |
| `test_tbe_06_over_budget_is_fail_not_insufficient_data` | B-6 / V-3 | **RED** |
| `test_tbe_07_countersigned_extension_raises_the_budget` | B-13/B-14 | **RED** |
| `test_tbe_08_extension_logged_after_the_overspend_authorizes_nothing` | **B-9** | **RED** |
| `test_tbe_09_a_dated_field_in_detail_is_never_read_for_ordering` | B-9 / §7.1 | **RED** |
| `test_tbe_10_uncountersigned_or_self_countersigned_extension_is_refused` | B-14 | **RED** |
| `test_tbe_11_principal_issues_alone` | B-15 | **RED** |
| `test_tbe_12_malformed_extension_fails_even_inside_budget` | B-23 | **RED** |
| `test_tbe_13_withdrawal_neutralises_a_malformed_event` | B-24 | **RED** |
| `test_tbe_14_contingent_extension_is_recomputed_not_trusted` | B-16/B-19 | **RED** |
| `test_tbe_15_contingent_increment_reproduces_prereg002_table` | B-18/B-20 | **RED** |
| `test_tbe_16_unknown_predicate_and_nonempty_params_are_malformed` | B-17 | **RED** |
| `test_tbe_17_criterion_is_generic_and_reads_no_single_documents_fields` | **B-22** | **GREEN — must stay green** |
| `test_tbe_18_predecessor_chain_spend_is_not_charged_to_the_successor` | B-1 | **RED** |
| `test_tbe_19_unknown_event_kinds_and_narrated_kwargs_cannot_authorize` | B-4 / C-6 | **RED** |

**Suite state, with the concurrency caveat the dispatch requires.** `python3 -m pytest
harness/tests -q` reads **245 passed / 30 failed / 275** [measured, end of this session].
That is not comparable to the 241/5/246 the dispatch quoted, and the difference is **not** a
signal about this work: Seat 9's RULING 005-A one-liner landed and committed at `b065039`
mid-dispatch (+1 green, `test_mono_03`), this document adds 2 green in
`test_monotone_conservatism.py` and 27 items in a new file of which 26 are red **by design**.
Netting it out: **4 pre-existing reds, 26 deliberate new reds, everything else green.**

**The floor.** With B-1 … B-31 implemented and nothing else changing: **271 passed / 4 failed
/ 275.** The four are the already-ruled `test_G2` (RULING 005-C), `test_h8` (005-D) and
`test_h7` (005-E) fixture edits owed by the seat that owns those files, plus `test_mbs_12`
(I-076, awaiting my own separate ruling). **None of the four is mine to fix under this
dispatch and none is closed by it.**

---

## 9. LEAKAGE AUDIT

Run on this specification, not on a family — there is no family. The relevant question for a
criterion is the analogue of the eight: **can it read anything at evaluation time that was not
knowable at the moment it grades?**

| # | Check | Finding |
|---|---|---|
| 1 | Does anything filter on an event's *claimed* time rather than its recorded time? | **No — B-9/B-21.** The claimed time is never read for ordering. This is the `event_time` / `knowledge_time` discipline applied to authorization: the criterion filters on `knowledge_time` (the row's `created_utc`) and refuses `event_time` (the `detail`'s claim). |
| 2 | Restated inputs? | **The sealed budget cannot be restated** — `trial_budget` is a binding field; P3 refuses an amendment and P4 detects an out-of-band `UPDATE`. **The events table has no such protection** — I-102. |
| 3 | Survivorship in the trial ledger? | **A trial cannot be un-logged through the API**; the registry is append-only and `V-5` already rules that trials cannot be unspent. A raw `DELETE FROM trials` is undetectable — same class as I-102, same disclosure. |
| 4 | Retroactive adjustment the criterion could not have seen? | **B-5/V-1: nothing is cached.** A later evaluation may reach a different verdict, and both reports stand. |
| 5 | Same-bar fill analogue — is an authorization allowed to act on the thing it authorizes? | **No. B-12** makes a discretionary authorization effective only when *both* halves exist, and B-9 grades each trial against the budget in force *before* it. This is the one-bar-lag rule in a different currency. |
| 6 | Purged/embargo analogue? | Not applicable. |
| 7 | Argmax vs. plateau? | Not applicable — no parameter is selected here. |
| 8 | Holdout consulted? | **No.** `book/vaults/` untouched; no passphrase requested or held; no `HoldoutVault` method called this session [measured]. |

---

## 10. ISSUES FILED

Range allocated **I-100 – I-109**; **I-100 through I-106 taken, I-107–I-109 unused.**

| # | Sev | Subject |
|---|---|---|
| **I-100** | **MEDIUM** | `trial_budget` is unvalidated at registration while its adjacent binding sibling `n_inherited` is validated three ways (H-2: non-int, bool, negative). A budget of `0`, a negative budget, a `bool`, or a silently-truncated float all seal. **And `gates.py`'s `fam.trial_budget and …` short-circuits at 0**, so a zero-budget family never evaluates the comparison at all and reads PASS with unbounded trials. **This survives the obvious fix to I-022** and is why the fix is a specification. Closes on B-7 + `test_tbe_03`/`04`. |
| **I-101** | **MEDIUM** | The comparison quantity in the trial-count criterion was never specified, and the existing code picks the wrong one: `fam.n_logged` is chain-summed transitively, so under a *working* criterion every successor whose predecessor chain out-spends its own budget would be born over budget with zero acts — the anti-gaming control (`predecessor_family`) inverted into a penalty for declaring one. Ruled at B-1: own-family only, with the chain total disclosed on the report face (B-25). |
| **I-102** | **MEDIUM** | **The `events` table has no integrity control.** `hypotheses` rows are protected by `hypothesis_sealed`'s full shadow copy (P1/P4); `events` has nothing equivalent, so any authorization edge built on events is only as strong as "no seat writes raw SQL." Mitigated but not closed by B-21's `n_logged_at_issue` cross-check. Structural; disclosed rather than solved, and it bears on `holdout_acquired` and `gate1_verdict` as much as on this document's events. |
| **I-103** | **MEDIUM** | **The harness has no principal identity.** There is no authentication anywhere in `registry.py`; any seat with a registry handle can write any event with any `issuer` string. Every authorization edge in this firm is therefore **attributable by declaration, not by proof**. B-14's distinct-countersigner requirement controls seat drift, not fraud, and this document says so in terms rather than implying a strength it does not have. |
| **I-104** | **MEDIUM** | PREREG-002 §10.5.2's Stage 2 unlock says `N_max` is *"read from the cited table … and never interpolated."* **A table lookup with no interpolation is undefined between rungs.** The harness holds the continuous function the table renders. Ruled at RULING 003-A: the function governs. Owner: Director of Research — cheaper to conform pre-seal than to reconcile against a frozen document. |
| **I-105** | **HIGH** | **The generic mechanism locks PREREG-002's Stage 2 only if PREREG-002 seals `trial_budget = 47`.** If it seals the flat `79`, the harness enforces 79, Stage 2's gate does not exist, and §10.5.2 reads — in a frozen document — as though it did. **The two-stage construction is a registration act, not a prose act.** This is the one finding here that can still produce a wrong PASS after I-022 is fixed. Owner: Director of Research; bears on C10 and C13. |
| **I-106** | **LOW** | **My I-065 root cause named one test; there were two.** I-065 records the C-1(iv) gap as living in `test_mono_05`'s sweep. `test_mono_04` — the file's *dedicated* sub-1 sweep, named "no loosening at any vif < 1" — tested `min_backtest_length_years_serial` and `max_admissible_trials` and **never called `deflated_sharpe_ratio_serial` at all.** Two tests whose names promised the sub-1 branch, neither of which reached DSR there. Closed in the same change (`test_mono_09`). Recorded because a root cause that under-counts its own instances is a root cause that closes early. |

**I-022 closes** on Seat 9's implementation of B-1 … B-31 with all 19 tests green — not before.
**I-076 remains open**, unadjudicated, owned by me. **I-057** is discussed at §11.

---

## 11. WHAT CLOSES AND WHAT DOES NOT

| Issue | Closes? | On what |
|---|---|---|
| **I-065** | **YES, on this document's Item 1 half** — the extended C-4 sweep is in `harness/tests/test_monotone_conservatism.py` and green, and RULING 005-A's one-line clamp is in `stats.py` and green [measured, this session]. **Both of the Principal's closure conditions are now met.** I-106 is filed alongside it rather than folded into it. |
| **I-057** | **NO.** §11.3's partition is unchanged. `test_monotone_conservatism.py` is now 9/9 green and `test_dsr_serial.py` 10/10, but `test_minbtl_serial.py` is still red on `test_mbs_12` (I-076), which blocks Item 1 independently. **I said in advance that I would report this rather than let a partial close look like a close, and I am.** |
| **I-022** | **NO — not yet.** It closes on implementation, not on specification. The escalation to HIGH stands until then. |
| **C10** (PREREG-002) | **NO.** C10 is discharged when I-022 closes *and* PREREG-002 registers Stage 1 as its sealed `trial_budget` (I-105). Specifying the latch is not the same as fitting it. |

---

## 12. ADDRESSED TO THE PRINCIPAL

Four things. One asks for nothing; three are decisions you may wish to take back.

**(1) I departed from your shape in one place that takes authority from a seat you named.**
You specified continuation via "a registry-logged Director budget-extension event." B-14
requires the Director's extension to be countersigned by a distinct seat. My reasoning is that
the harness cannot authenticate anyone, so a single seat's declaration is structurally
indistinguishable from a single seat's convenience, and the Director is the seat under
schedule pressure. **If you want the Director able to extend a budget alone, that is your call
and it is a one-line change to an allow-list** — but I would rather you make it than have me
assume it. You remain able to extend alone under B-15.

**(2) There is no identity in this harness, and that caps how strong any authorization edge in
this firm can ever be.** `issuer` is a string a seat writes about itself. I have filed it
(I-103) and I have built the strongest thing available on top of it — a distinct countersigner,
a named artifact that cannot be spent twice, and a report face that shows every extension
including every refused one. **I am not asking you to fix this and I do not think it is worth
fixing at this firm's scale.** I am recording it so that nobody later reads B-14 as a security
control. It is a drift control.

**(3) No grandfathering, and I want the reasoning on the record while it is free.** A family
over budget when this lands FAILs (B-30). It costs the firm nothing today — 0 hypotheses,
0 trials [measured] — and I have written into the clause that I would rule the same way at
non-zero cost, precisely so that the ruling cannot later be characterised as easy because
nothing was at stake.

**(4) One finding can still produce a wrong PASS after I-022 is fixed, and it is not in the
harness.** PREREG-002's two-stage budget is enforced only if the document *registers* Stage 1
as its sealed `trial_budget = 47`. Sealed at the flat 79, the prose describes a gate that does
not exist. Filed **I-105, HIGH**, to the Director. **The fix you funded this unit for works;
it does not work by itself.**

**No Charter constant moved and none is requested.** The holdout vault was not opened, listed,
or read; no passphrase was requested or held; `book/registry.db` stands at 0 hypotheses /
0 trials, before and after.

---

*Specified by the Head of Quantitative Validation, 2026-08-06. Not committed — per dispatch
constraint. Files written: `research/VALIDATION-SPEC-003-budget-enforcement.md`,
`harness/tests/test_trial_budget_enforcement.py`. File extended:
`harness/tests/test_monotone_conservatism.py`. Files deliberately NOT modified:
everything under `harness/castellan/`.*
