# REGISTRATION PAYLOAD — `funding-carry-conditioning-002`

**The sixteen binding fields of `TrialRegistry.open_hypothesis`, with their final values.**

**Seat:** Director of Research (Seat 2) · **Date:** 2026-08-10 · **Dispatch:** S3-D-001, Task 3
**Discharges:** **I-105** · **I-130** · **I-131** · **I-136**
**Subject family:** `funding-carry-conditioning-002` · **Pre-registration:** `research/PREREG-002-crypto-funding-basis.md` at **R-004**
**Reasoning:** `research/DIR-RESTATE-001-prereg002-mechanism.md` §9

---

## 0. WHAT THIS DOCUMENT IS, AND THE ONE RULE THAT GOVERNS READING IT

**This is the registration payload and nothing else.** It contains no argument, no verdict, no
recommendation, and no analysis. Every one of those lives in `PREREG-002` or in `DIR-RESTATE-001` §9.
**Nothing in this file should be mistaken for a binding field that is not in §1's table of sixteen.**

> ### **THE PAYLOAD GOVERNS.**
>
> **Anywhere `PREREG-002`'s prose and this payload could diverge, this payload is the value that gets
> passed to `open_hypothesis`.** That is the whole content of I-105's lesson: **prose is not
> registration.** A document can describe a budget, a stage, a ceiling or a floor at any length and in
> any number of sections; the registry receives sixteen values, and those sixteen are the
> pre-registration. Everything else is commentary on it.

**THIS FILE IS NOT AN AUTHORIZATION TO SEAL.** `TrialRegistry.open_hypothesis` **is** the seal —
`registry.py`'s P1: *"on first registration, computes `prereg_sha256`"* [measured]. Registration and
sealing are one operation, not two. The seal remains blocked on **C7 and C8 — those two and nothing
else** [source: `PREREG-002` §20's conformed table, R-010/R-011 — *"Seal-blocking · C7, C8. Nothing
else."*; C2 discharged ADMIT-CONDITIONAL, C3 withdrawn, C11 removed as circular], and a seal is a
Standing Order 002 §4 hard interrupt. **This file
exists so that when the seal is authorized, the act is mechanical and has nothing left to decide.**

**`book/registry.db` reads 0 hypotheses / 0 trials / 1 event as of this writing** [measured —
read-only `SELECT COUNT(*)`, this session; the one event is `book_open`].

---

## 1. THE SIXTEEN FIELDS

*The binding set, enumerated exhaustively at `harness/castellan/registry.py:82`, `_BINDING_FIELDS`
[measured]. These sixteen and only these sixteen are hashed into `prereg_sha256` and shadow-copied
into the `hypothesis_sealed` event. `created_utc` is provenance-only and outside the hash.*

| # | Field | Final value | Form |
|---:|---|---|---|
| 1 | `family` | `"funding-carry-conditioning-002"` | literal, §2.1 |
| 2 | `statement` | §21 block, post-R-004 | prose, §3 |
| 3 | `mechanism` | §21 block, post-R-004 | prose, §3 |
| 4 | `falsifier` | §21 block, post-R-004 | prose, §3 |
| 5 | `universe` | §21 block, post-R-004 | prose, §3 |
| 6 | `horizon` | §21 block, post-R-004 | prose, §3 |
| 7 | `success_criteria` | §21 block, post-R-004 | prose, §3 |
| 8 | **`trial_budget`** | **`47`** | literal, §2.2 |
| 9 | `predecessor_family` | `None` | literal, §2.3 |
| 10 | `holdout_classification` | `"FORWARD"` | literal, §2.4 |
| 11 | `forward_window_start` | `C`, computed at seal time — §2.5 | derived, §2.5 |
| 12 | `forward_window_min_length` | `12.0` | literal, §2.6 |
| 13 | `forward_kill_condition` | §21 block, post-R-004 | prose, §3 |
| 14 | `model_prior_provenance` | §21 block, post-R-004 | prose, §3 |
| 15 | `published_signal_haircut_applied` | `0.50` | literal, §2.7 |
| 16 | **`n_inherited`** | **`7`** | literal, §2.8 |

**Two values changed at R-004 and both are in this table: `trial_budget` 79 → 47, and `n_inherited`
0 → 7.** Neither is a design change. The first is I-105's discharge; the second is I-130's.

---

## 2. THE EIGHT LITERAL FIELDS, WITH THEIR FINAL VALUES

### 2.1 `family`

```python
family = "funding-carry-conditioning-002"
```

Unchanged since 2026-07-28. It is the join key for `trials`, the argument `log_trial` refuses without
(A2's `PreRegistrationError`), and the `HoldoutVault`'s `family=` argument, which must match
character for character.

### 2.2 `trial_budget` — **47** · *I-105's discharge*

```python
trial_budget = 47
```

**This is the Stage 1 authorized budget, and registering it here is the entire content of I-105.**

`gates.py:562` reads `sealed = fam.trial_budget` and hands it to B-7's zero-budget branch, B-9's
per-trial ordering walk, and `declared_ceiling_base` [measured]. **Sealed at the flat 79, the harness
enforces 79, no contingent predicate is ever evaluated, and §10.5.2 describes — in a frozen document,
permanently, under P7 — a gate that does not exist.** Sealed at 47, the staged construction is the
thing the harness reads.

| Stage 1 line item | Trials | Source |
|---|---:|---|
| C11 — leg-(ii) null calibration, run before F-002 | ≤ 2 | §5.5(e), §10.5.2 |
| F-002 — `R_bench`, `R_strat`, `R_bench_scaled` | 3 | §5.1 |
| Pre-grid diagnostics — regime-cell decomposition, capacity, cost sensitivity at 1×/2×/repaired, skew & ES | ≤ 7 | §10.5.2 |
| ±50% parameter grid, 2 params × 5 steps | 25 | §10.5 |
| Walk-forward windows 1–10, fixed plateau centroid | ≤ 10 | §10.5.2, §10.7(c) |
| **Total** | **≤ 47** | |

`2 + 3 + 7 + 25 + 10 = 47` [arithmetic on already-declared line items; no market data touched].

**Stage 2 is NOT in this field and must not be added to it.** Stage 2 is `≤ 32` further trials,
authorized by a `trial_budget_extension` event of `mode="CONTINGENT"` — **a post-seal registry act,
specified at §4 of this document.** Sealing 79 in order to "cover" Stage 2 is the exact defect I-105
names.

### 2.3 `predecessor_family`

```python
predecessor_family = None
```

**No prior family exists.** `book/registry.db` holds zero hypotheses [measured], so there is nothing
this family could name. Consequences, both material and both stated because they are load-bearing:

- `family_stats` has no chain to sum transitively, so `n_trials = n_inherited + n_logged` for this
  family alone.
- **`InheritedCountDoubleCountError` cannot fire.** Its guard is
  `if predecessor_family is not None: ... if chain_total > 0 and n_inherited >= chain_total`
  [measured — `registry.py`]. With `None`, the branch is not entered. **This is why `n_inherited = 7`
  registers cleanly** and is not the double-count GATES.md §4.7.1 forbids.

### 2.4 `holdout_classification`

```python
holdout_classification = "FORWARD"
```

Validated at registration against `{"FORWARD", "HISTORICAL"}`; any other value raises [measured].
`FORWARD` does **not** trigger the R3 presence check on fields 11–13 — that branch is gated on
`== "HISTORICAL"` [measured]. **This family supplies those three fields anyway** (§11.4: *"a claim
about data that did not exist when the claim was made is worth having regardless of classification"*),
and R-004's §4.7.2 audit records that for a FORWARD family nothing in the harness reads them
(**I-135**).

### 2.5 `forward_window_start` — **the one field whose literal cannot be fixed before the act**

```python
forward_window_start = datetime.now(timezone.utc).date().isoformat()   # = C
```

**`C` is the seal date** (D-007) and the seal date is the moment `open_hypothesis` is called. The
value is therefore a computation performed at the instant of the act, not a literal chosen in advance,
and **this is mechanical rather than interpretive**: there is exactly one correct value and it is
produced by the expression above.

**Two binding constraints on it, neither of them this field's to enforce:**

1. **It must equal the `HoldoutVault.seal(cutoff=...)` argument, on the same UTC calendar day, in the
   same session** — C8, and P7 fails Gate 1 if `hypothesis_sealed` postdates `C` at UTC day
   granularity.
2. **`PREREG-002` §11.4 and §21 carry the literal `"2026-07-28"`.** That literal was drafted against
   an intended same-day seal that §20.1 then recommended against. **It is stale and the payload
   governs: the executed value is the seal day, not 2026-07-28.** R-004 conforms §21; this clause is
   the authority if any copy is missed.

### 2.6 `forward_window_min_length`

```python
forward_window_min_length = 12.0   # UNITS: MONTHS
```

Charter §4.4's holdout floor. **The schema stores this as an unlabelled `REAL`** and days, months and
years are indistinguishable in it (I-033(5)). Nothing in the harness reads it (**I-135**), so the
ambiguity has not yet cost anything and the unit is recorded here and in §21 rather than in the
column.

### 2.7 `published_signal_haircut_applied`

```python
published_signal_haircut_applied = 0.50
```

The Ruling 002 R4(b) presumption accepted in full; no exemption sought (§11.6). **Nothing in the
harness applies it** — zero non-`registry.py` consumers [measured] — which R-004 files as **I-134**
and which §5.4's `t(α) ≈ 6.0` burden depends on entirely. The declaration stands; the disclosure that
it is a declaration and not a deduction stands with it.

### 2.8 `n_inherited` — **7** · *I-130's discharge, and R-004's substantive change*

```python
n_inherited = 7
```

**`N_conditioning` = 7 — the seven menu-declared, pre-measurement conditioning choices K1 through K7,
each contributing 1 under §7.2's pre-commitment rule.** Declared, phantom, no return series, which is
the field's documented purpose verbatim: *"the prior search attributable to THIS family and not
already carried by its predecessor chain — declared, phantom, no return series"* [measured —
`registry.py`, `open_hypothesis` docstring].

**Why 7 and not 0, in one paragraph.** `gates.py:565` computes
`declared_ceiling_base = fam.n_inherited + sealed`, and B-18's contingent predicate is
`allowed = clamp(N_max − declared_ceiling_base, 0, increment)`. `VALIDATION-SPEC-003`'s own
`test_tbe_15` fixes `base, inc = 54, 32` and reproduces §10.5.2's four unlock rungs exactly [cited —
`harness/tests/test_trial_budget_enforcement.py:497–518`]. **54 = 7 + 47.** At `n_inherited = 0` the
base is 47 and the same table admits **30** where §10.5.2 declares 23, and **8** where §10.5.2
declares 1 — **permissive, at exactly the two rungs where the family is in trouble.** Full derivation
at `DIR-RESTATE-001` §9.4.

**What it costs, recorded here because the payload is where the cost becomes real.** Registry-enforced
`N` at a full Stage 1 spend is **54**, not 47; at full Stage 2 it is **86**, not 79. DSR is deflated
against 86 (`gates.py:779`, `:788` pass `fam.n_trials`) and MinBTL is evaluated at 86
(`gates.py:856`), rather than against a count that omits the conditioning floor. **`MinBTL(86,
SR 1.0) = 6.14 yr` against 6.571 available, margin 0.43 yr** [cited — §10.4; already measured, not
re-derived]. **§10.3's 0.13-year I-027 residual is not mitigated — it is paid, deliberately, in the
direction that tightens the family's own length criterion.**

**This is not the GATES.md §4.7.1 defect.** §4.7.1 forbids re-declaring a quantity *the registry
already computes*. **The registry cannot compute `N_conditioning`** — it holds no knowledge of menus,
choices, or the pre-commitment discount — and with `predecessor_family = None` there is no chain
summation to duplicate. §4.7.1 governs inheritance from a predecessor; this is a first family with no
predecessor.

---

## 3. THE EIGHT PROSE FIELDS

**Final value for each: the string in `PREREG-002` §21's fenced seal block, as it stands after
revision R-004.** The extraction is mechanical — the text between `<field_name>                    = "`
and its closing `"` in that block — and requires no judgment at any point.

> ### **WHY THESE EIGHT ARE NOT DUPLICATED HERE, STATED AS AN ENGINEERING ARGUMENT AND NOT AS A SHORTCUT.**
>
> `universe` alone runs to roughly 280 lines, `success_criteria` to roughly 150, `forward_kill_condition`
> to roughly 100. **Two verbatim copies of a 280-line binding string, in two files, is a guaranteed
> future divergence** — and a divergence between the payload and the pre-registration on a field that
> is hashed into `prereg_sha256` is the precise failure this payload exists to prevent. **One source,
> named exactly, is the correct form.** R-004 edited §21 in place; §21 post-R-004 **is** the payload
> for these eight, and there is no second copy to drift.
>
> **The payload's authority over these eight was exercised by writing R-004**, not by restating it
> here. The four deltas R-004 applied are enumerated at §3.1 so an auditor can verify the source
> without reading the whole block.

### 3.1 What R-004 changed inside the §21 block

| Field | Changed? | The delta |
|---|---|---|
| `statement` | **No** | Byte-identical to R-003 |
| `mechanism` | **No** | Byte-identical to R-003 |
| `falsifier` | **No** | Byte-identical to R-003 |
| `universe` | **Yes — one insertion** | The `N CONTRIBUTION` paragraph records that the 7 is now **registered as `n_inherited`**, not merely declared, and that this is what makes §10.5.2's unlock table hold |
| `horizon` | **No** | Byte-identical to R-003 |
| `success_criteria` | **Yes — four edits** | (i) `n_inherited = 0` → **7**, with the reason; (ii) the disclosure line *"the 7-trial conditioning floor is declared and unenforced (I-027)"* **struck and replaced**, being false once the 7 is registered; (iii) the Stage 2 unlock rule conformed to `VALIDATION-SPEC-003`'s CONTINGENT form and to **RULING 003-A** (the function governs, the table is a rendering — I-104); (iv) the §4.7.2 category-(c) disclosure added |
| `forward_kill_condition` | **Yes — one insertion** | KC-002 unchanged in every clause. The §4.7.2 finding is recorded on its face: **no harness path evaluates a kill condition on any date**, so clause 5's silence-kill is enforced by seats and the calendar and by nothing in the engine (**I-135**) |
| `model_prior_provenance` | **Yes — one insertion** | R-004's origination recorded: the §4.7.2 audit and the `n_inherited` correction, Director of Research, Opus, cutoff unknown |

**No declared menu was edited. No selection moved. `N_conditioning` remains 7 and every K1–K7 menu
string is untouched.**

### 3.2 What R-005 changed inside the §21 block **[added 2026-08-10 · dispatch S3-D-003]**

> ### **NO LITERAL IN §1's TABLE OF SIXTEEN CHANGES. `trial_budget` = 47. `n_inherited` = 7.**
>
> **R-005 is a labelling revision — every limit `PREREG-002` claims now carries its class, per the
> Principal's adoption of I-133's conclusion. Nothing was made enforceable that was not.** Three prose
> fields receive conforming inserts, by the same mechanism §3.1 records for R-004.

| Field | Changed? | The delta |
|---|---|---|
| `statement` · `mechanism` · `falsifier` · `universe` · `horizon` | **No** | Byte-identical to R-004 |
| `success_criteria` | **Yes — three inserts** | (i) the **class register** pointer and its counts — **20 (a) / 7 (b) / 34 (c), sixty-one limits**, at `PREREG-002` §10.11; (ii) **correction 1 (R25)**: the §4.7.2 audit said **nine** zero-consumer fields and there are **eight** — the 9 was a count of category-(c) *limits* transplanted into a column counting *fields*; the corrected partition is **5 (a) / 11 (c)**, with `statement`/`mechanism`/`falsifier` class (a) on **existence only**; (iii) **correction 2 (R28)**: the 50% haircut carries class (c) **at the point of reliance**, the gap is **2× at Gate 1's t-criterion**, and §19.3's composite is one class-(a) multiplier (I-050, `stats.py:153`) times one class-(c) multiplier |
| `forward_kill_condition` | **Yes — two inserts. KC-002 unchanged in every clause, threshold and date.** | (i) **KC-002 is class (b) with its three fields named**: executor **the Principal**, cadence **the weekly Friday ritual alongside the pull-and-merge**, artifact **the pasted evaluation per `TEMPLATES.md` §7.9** — reverting to class **(a)** when Validation's harness kill-condition evaluator lands, **specced this sprint, not yet dispatched**; (ii) **the C1 condition precedent is satisfied** — clause (i)'s *"`CRYPTO_PERP_TAKER` as repaired per C1"* is correct as written, the preset **is** as repaired, and the ADMITTED-AS-EXPLORATORY downgrade **must not fire on 2026-08-11** |
| `model_prior_provenance` | **Yes — one insert** | R-005's origination recorded, including that **the three classes and KC-002's three (b) fields are the Principal's, not this seat's**, and that **two of R-005's four findings run in this family's favour** |

**Where R-005's corrections bear on §2 of this payload:** **§2.7's note stands and is sharpened.**
`published_signal_haircut_applied = 0.50` remains **0.50** — the value is a declaration of which
presumption the sponsor accepted, and the presumption was accepted in full. **A field being unread is
not a reason to write a different number into it; that would be adjusting the declaration to match the
enforcement rather than adjusting the description of the enforcement to match the truth.** What
changes is the sentence about what it does: **class (c), no code path, and a 2× permissive gap at
Gate 1's t-criterion that only a C5 ruling closes** (I-143).

**And §4's two disclosed defects both move.** **I-022 is repaired and passing** since 2026-08-05
(`DATA-IMPL-007` §5, *"all 19 test functions green"*); `gates.py:527–640` FAILs on B-7, on B-9's
per-trial ordering walk, and on B-23 [measured]. **The literal `True` §4 quotes does not exist in
`gates.py`.** **I-132 is unchanged and is the residual that matters:** `log_trial` reads no budget, so
**prevention: none; detection and refusal: automatic, per trial, with the offending trial named.**
Filed **I-142**.

### 3.3 What R-008 changed inside the §21 block **[added 2026-08-25 · dispatch S4-D-001]**

> ### **NO LITERAL IN §1's TABLE OF SIXTEEN CHANGES. `trial_budget` = 47. `n_inherited` = 7. `published_signal_haircut_applied` = 0.50.**
>
> **But three prose fields change VALUE, not merely wording, and this section exists because that is the trigger this payload recognizes.** R-008 discharges **I-210** (seal-blocking) and **I-213**, and discloses `REDTEAM-002` §2.1's inertness finding without redesigning the rule. **The mechanism is unchanged: §21 post-R-008 IS the payload for the eight prose fields, and there is no second copy to drift.**

| Field | Changed? | The delta |
|---|---|---|
| `statement` | **Yes — three edits, all value-bearing** | (i) **`k` = 0.5, `d` = 1.0, `band` = 0.10 named as NUMERIC LITERALS**, with `lookback` = 30 and `w_max` = 1.0, plus the one-sentence reading of the rule and `w`'s zero point at `z` = 3.0; (ii) the right edge *"over 2020-01-01 to C"* conformed to **"the last settled common bar of the primary universe at the first run"** — `C` is not redefined; (iii) the **mechanical register** of the inertness disclosure |
| `mechanism` | **Yes — one insertion** | The **economic register**: the field that names hedgers as the mechanism of funding inversion now states in the same field that the rule holds benchmark weight through inversion, on roughly a quarter of in-sample days [cited — `REDTEAM-002` §2.1, measured by that seat], and that this is a risk posture and **not** tail reduction |
| `falsifier` | **Yes — two edits** | (i) the in-sample right edge conformed as above; (ii) the **evidential register**, binding on how leg (ii) may be read: no leg (ii) result may be presented as tail protection in the inversion regime |
| `horizon` | **Yes — one edit, value-bearing** | **`band` = 0.10** as a numeric literal, with its cost derivation and the disclosure that the `0.10 < 0.25` check on KC-002 clause (b) was run **after** the choice |
| `universe` · `success_criteria` · `forward_kill_condition` · `model_prior_provenance` | **No** | Byte-identical to R-007. **In particular the struck `2027-01-31` literals are NOT removed — I-204's standing prohibition holds** |

**R-008 adds ZERO new dated sites to the E-2 obligation and REMOVES TWO** — no ISO date or `C`-form expression appears in any replacement text inside a field, and R43 deletes the `FORMULA C` right-edge site from both `statement` and `falsifier`. **The first revision of this document that does not grow the obligation** — and the first draft of it grew the obligation by four before this seat's own check caught it (**I-226**).

**One defect in this payload's own record, filed rather than back-filled: §3 carries deltas for R-004 and R-005 and none for R-006 or R-007**, both of which moved prose-field bodies (`forward_kill_condition`'s three date literals at R32; `universe` and `model_prior_provenance` at R-007). Their revision blocks record it; this file does not. **Filed I-225. Not reconstructed here — a delta table back-filled two revisions late by a seat reading its own revision blocks is a record of what the blocks say, not of what the fields did.**

### 3.4 What R-009 changed inside the §21 block **[added 2026-08-25 · dispatch S4-D-007]**

> ### **NO LITERAL IN §1's TABLE OF SIXTEEN CHANGES. `trial_budget` = 47. `n_inherited` = 7. `published_signal_haircut_applied` = 0.50.**
>
> **Two prose fields change VALUE. `band` is a numeric literal living inside two of the eight prose fields, not a field of its own, which is exactly why §3.3's trigger applies again one revision later.** R-009 discharges **I-240** and discloses **I-241** without re-deriving `d`. **§21 post-R-009 IS the payload for the eight prose fields, and there is no second copy to drift.**

| Field | Changed? | The delta |
|---|---|---|
| `statement` | **Yes — two edits, both value-bearing** | (i) **`band` 0.10 → 0.27** in the numeric-literal roster; **`k` = 0.5, `d` = 1.0, `lookback` = 30, `w_max` = 1.0 byte-identical**; (ii) the **noise-scale register** — the DA's I-241 correction published beside `d` = 1.0 in the hashed field: `sd(z \| null) = √(1 + 1/30) ≈ 1.017`, not the `0.183` reference-level noise, so `d` = 1.0 sits at **~1.0 null SD, not ~5.5**, the position at which §14.2 rejects `d` = 0.2, and is *"a rounder number in the same class as 3.0"*. **`d` seals as chosen** |
| `horizon` | **Yes — one edit, value-bearing** | **`band` 0.10 → 0.27**, with the leg-count error named before the corrected arithmetic (24 bp is §12.4's **two-leg** round trip; a band rebalance moves **one** leg; corrected charge **12.0 bp**; `band × 12.0 ≤ 3.249` ⇒ `≤ 0.27083`, truncated to **0.27**), the declined 6 bp alternative and its direction, and **the escalation on the face of the field**: R41's favourable post-hoc check inverts, suppression window `1.50 < z ≤ 1.54`, unresolved at the seal |
| `mechanism` · `falsifier` · `universe` · `success_criteria` · `forward_kill_condition` · `model_prior_provenance` | **No** | Byte-identical to R-008. **KC-002 is unchanged in every clause, threshold and date, and the struck `2027-01-31` literals are NOT removed — I-204 holds** |

**R-009 adds ZERO new dated sites and no `[Rn, <date>]` stamp appears inside any hashed field** — R-numbers only, per I-226.

> **THE ONE THING THIS PAYLOAD MUST CARRY TO WHOEVER EXECUTES THE SEAL: `band` = 0.27 IS ESCALATED, NOT SETTLED.** The sponsor's own pre-registered trigger — *"had the cost arithmetic delivered `band` > 0.25 … this seat would have escalated"* — **fired**, and two live questions belong to Validation before the act: **I-252**, whether the perp-leg charge is 12 bp (round trip, giving 0.27) or 6 bp (one side, giving ~0.54), which moves the suppression window from `1.50 < z ≤ 1.54` to `1.50 < z ≤ 2.08`; and **I-253**, whether KC-002 clause (b) should count *target* rather than *executed* deviations, which would decouple a kill condition from a cost parameter. **Neither is repaired here. A ruling that moves `band` moves two hashed strings and requires an R-010 before the seal, not after it.**

---

### 3.5 What R-010 changed inside the §21 block **[added 2026-09-10 · dispatch S4-D-011]**

> **§3.4 closed with a standing instruction: *"a ruling that moves `band` moves two hashed strings and requires an R-010 before the seal, not after it."* The ruling came, `band` moved, and this is that R-010. The payload's own prediction is the reason this is a conformance rather than a discovery.**

**`band` = 0.27 → `band` = 0.54.** **No literal in the table of sixteen moves.** `trial_budget` = **47**, `n_inherited` = **7**, `published_signal_haircut_applied` = **0.50**, `family`, `predecessor_family`, `holdout_classification`, `forward_window_min_length` — all byte-identical. **`band` is a numeric literal living inside two of the eight prose fields, not a field of its own**, which is why §3.3's trigger has now applied three revisions running.

| Prose field | Changed? | What moved |
|---|---|---|
| `statement` | **Yes — two edits, both value-bearing** | (i) **`band` 0.27 → 0.54** in the numeric-literal roster; **`k` = 0.5, `d` = 1.0, `lookback` = 30, `w_max` = 1.0 byte-identical**; (ii) a new **cost-convention register** on the R45 precedent — **both candidate bands, the chosen one and the reason, published in the hashed field**: 6.0 bp one side → **0.54 SELECTED**, 12.0 bp round trip → 0.27 **DECLINED**, the `engine.py` citation that decides it, that the tie-break never engaged and would have given the same number, and the two surviving conventions (I-290, I-291) with their directions named |
| `horizon` | **Yes — one edit, value-bearing** | **`band` 0.27 → 0.54**, with **both** errors named before the corrected arithmetic (R41's leg count; R44's side count and the withdrawal of R44's stated reason), the engine citation, the double-count argument, `band × 6.0 ≤ 3.249` ⇒ `≤ 0.54150` truncated to **0.54**, the identical 0.28% margin, and the escalation's new size on the face of the field: suppression window **1.50 < z ≤ 2.08**, and **R44's "the window is narrow" qualification WITHDRAWN** |
| `mechanism`, `falsifier`, `universe`, `success_criteria`, `forward_kill_condition`, `data_sources` | **No** | Byte-identical to post-R-009. **`forward_kill_condition` is untouched in every clause, threshold and date; the struck `2027-01-31` literals remain (I-204).** |

> **WHAT THIS PAYLOAD MUST CARRY TO WHOEVER EXECUTES THE SEAL, AND IT IS A DIFFERENT SENTENCE FROM §3.4's.** **`band` = 0.54 is DERIVED, not escalated.** I-252's question — 12 bp or 6 bp — **is answered on the merits and against the convention the sponsor itself selected one revision earlier**: the sanctioned engine charges one per-side price per unit of `|Δw|`, once, so a 12 bp round trip is a cost `run_backtest` will never apply (A2). **What remains open at the seal is not the charge but its consequence:** **I-251** (the escalation, fired at R-009, unresolved, now 14.5× larger) and **I-253** (whether KC-002 clause (b) should count *target* rather than *executed* deviations, which at 0.29 of suppression width is worth materially more than it was at 0.02). **Neither is repaired here. Neither moves a field. A ruling on I-253 moves KC-002, which is a hard interrupt and an R-011, not a footnote.**

> **AND THE TWO CONVENTIONS THAT SURVIVE ARE ON THE PAYLOAD'S FACE BECAUSE A FUTURE RULING ON EITHER MOVES `band` AGAIN, PRE-SEAL:** **I-290**, the one-day carry budget on the inequality's right-hand side (a two-day budget gives `band ≤ 1.083`); **I-291**, the omitted `Y·σ·√(Q/ADV)` impact term. **Both run in this family's favour and both are retained unchanged, because the ruling scoped the charge and neither is the charge.**

---

## 4. STAGE 2 — NOT A FIELD. A SEPARATE, POST-SEAL REGISTRY ACT.

**Stage 2 is not part of this payload and must not be folded into `trial_budget`.** It is a
`trial_budget_extension` event, written to the registry's append-only `events` table **after** the
seal, in `VALIDATION-SPEC-003`'s **CONTINGENT** form (B-13, B-16 … B-20). It is recorded here so that
nothing about the two-stage construction lives only in prose.

```python
registry.log_event(
    "trial_budget_extension",
    "funding-carry-conditioning-002",
    {
        "mode": "CONTINGENT",
        "increment": 32,
        "issuer": "director-of-research",
        "reason": "PREREG-002 §10.5.2 Stage 2: N_forward <= 22 and "
                  "walk-forward windows 11-20 <= 10, declared at "
                  "pre-registration and not authorized at the seal.",
        "authorization_ref": "research/PREREG-002-crypto-funding-basis.md",
        "n_logged_at_issue": <this family's own logged trial count at the instant of the write>,
        "predicate": {"name": "n_max_admits_declared_ceiling", "params": {}},
    },
)
```

**Six properties, every one of which runs against the sponsor:**

1. **No countersignature is required and none is a weakness.** B-16: a contingent extension is
   *"authorized by a computation, not by a person, and is therefore safe to self-issue… Forging the
   event buys nothing, because the number that governs is recomputed."*
2. **The predicate vocabulary is closed and has one member.** `params` must be present and **empty**;
   a non-empty `params` or any other `name` is MALFORMED and routes to Validation (B-17).
3. **The criterion recomputes `N_max` at evaluation time** — `_admissible_ceiling`,
   `min(n_max_admissible_iid, n_max_admissible_serial)` [measured, `gates.py:344`] — **and never
   trusts the event's assertion that the predicate held.**
4. **The cap is aggregate, not per event** (B-20): `max(0, N_max − declared_ceiling_base)` regardless
   of how many events are written. Ten events declaring 32 each admit 32 once.
5. **Unevaluable ⇒ zero, and FAIL rather than INSUFFICIENT-DATA** (B-19): no `oos_index`, VIF
   ineligible, `sr_ann <= 0`, or `n_logged == 0` gives `allowed = 0`.
6. **A malformed, un-withdrawn event FAILS the criterion even if the family is comfortably inside its
   sealed budget** (B-23). `n_logged_at_issue` is cross-checked against the trial ledger (B-21) and a
   reused `authorization_ref` is refused (B-26).

**What the mechanism admits, at `declared_ceiling_base = 7 + 47 = 54` and `increment = 32`** [all
`N_max` figures cited — `VALIDATION-SPEC-002` §6.2; the admitted column is `clamp(N_max − 54, 0, 32)`
on already-cited integers]:

| Measured `ρ̂` | `N_max` | Admitted | §10.5.2 declares |
|---:|---:|---:|---|
| ≤ 0.034 | 86 | **32** | "the whole of Stage 2" |
| ≈ 0.05 | 77 | **23** | "≤ 23 of the 32" |
| ≈ 0.10 | 55 | **1** | "≤ 1 of the 32" |
| ≥ 0.20 | 31 | **0** | "NONE" |

**This is `test_tbe_15` reproducing this family's own table without knowing this family exists**
[cited]. **The document declares an instance; the mechanism is generic and B-22 makes genericity a
tested property** — `gates.py`'s source may contain none of `PREREG-002`, `rho_plan`, `0.034`,
`stage_2`, `crypto-funding`.

**I-104 conformed, in the payload as well as in §10.5.2.** The nine-row table at `SPEC-002` §6.2 is a
**rendering** of `stats.max_admissible_trials`, which is continuous. **RULING 003-A: the function
governs.** §10.5.2's *"read from the cited table and never interpolated"* is struck — it described a
lookup with no defined value at `ρ̂ = 0.07`.

**Two live defects that bear on Stage 2 and are disclosed here rather than in a memo:**

- **I-022** — `gates.py` hard-codes a trial-count verdict to the literal `True` in one branch. C10's
  weight, already increased at R-003, is increased again by the fact that Stage 2's gate depends on
  the same criterion.
- **I-132 (new, R-004)** — **`log_trial` reads no budget** [measured — `registry.py:477–502`]. The
  budget is enforced **retrospectively**, at `evaluate_gate1`. Nothing prevents an over-budget spend;
  the spend fails the gate afterwards, and **trials cannot be unspent** (V-5). §10.5.2's *"No Stage 2
  trial is spent on an unmeasured or a stale `ρ̂`"* has **no spend-time control** and is a discipline
  on the seat that writes the loop.

---

## 5. THE VAULT — NOT PART OF THIS PAYLOAD, AND BINDING ON THE SAME DAY

**C8: the vault seals occur in the same session and on the same UTC calendar day as
`open_hypothesis`.** P7 fails Gate 1 if `hypothesis_sealed` postdates `C` at UTC day granularity.
~~The call is~~ **[R-011] THE CALLS ARE FOUR, NOT ONE, AND THEY ARE** at `PREREG-002` §21's vault
block. **The passphrase is the Principal's and is never written to this repository, to Oracle, or to
any file.**

> **[R-011 · 2026-09-14 · dispatch S4-D-016] THIS SECTION SAID "THE VAULT" AND ITEM 6 SAID "THE
> VAULT." BOTH WERE SINGULAR AND BOTH WERE WRONG.** `HoldoutVault.seal()` and
> `PITStore.set_holdout_ceiling()` each bind exactly **one** `(source, dataset_id)` pair, and
> `_active_ceilings` is an exact-match lookup with **no wildcard** [measured — `data.py:204`, `:271`].
> The primary universe holds **four** such pairs [measured — `DATA-IMPL-012` §1, re-measured
> read-only against `book/pit.db` at S4-D-016]. **Sealing one vault leaves three of four legs with no
> holdout ceiling while this document asserts one for all — P-1 false for 75% of the universe.**
> §21's own block comment said **two**, splitting spot from perp without splitting BTC from ETH; it
> is **struck**, not corrected in place. **THE PAYLOAD GOVERNS, and the payload now says four.**
> **No literal in §1's table of sixteen moves; no vault argument is a binding field of
> `open_hypothesis`** — `prereg_sha256` covers `_BINDING_FIELDS` only, and the vault's arguments hash
> separately into `spec_sha256` [measured — `registry.py`, `holdout.py`]. Filed **I-340, HIGH.**

---

## 6. PRE-EXECUTION CHECKLIST — mechanical, ~~six~~ **[R-011] SEVEN** items, no judgment

> **[R-011] THE HEADING SAID SIX AND THE TABLE HAS HELD SEVEN SINCE S4-D-013 ADDED THE GRANT STEP.**
> Found while conforming item 6, not looked for. **Same class as the vault count and the same
> arithmetic: a cardinal stated in prose beside a list that can be counted.** Filed **I-342, LOW** —
> low because nothing executes off the heading, and filed anyway because the class is now at its
> thirteenth instance and the pattern is the finding.

> ### **[R-012 · 2026-09-14 · I-367] ITEM 6'S GRANT-ROW COUNT WAS FOUR AND THE MEASURED COUNT IS EIGHT.**
>
> **Conformance by CIO hand under Principal ruling I-367.** The Principal extended the I-364
> transcription exception to this class by ruling: **a count measured by a tested script, verified
> against a throwaway registry, is a ruled state for conformance purposes — the measurement is the
> authority.**
>
> **Source, cited as the ruling requires** — `harness/tests/test_vault_seal_script.py`, nine tests
> green, and the direct measurement it rests on [measured, throwaway registry, one `seal()` call]:
>
> ```
> grants before ONE seal(): 0
> grants after  ONE seal(): 2
>     ('VAULT_SEAL', 'HoldoutVault.seal',                'CLEAN')
>     ('VAULT_SEAL', 'HoldoutVault.holdout_spec_sealed', 'CLEAN')
> ```
>
> **Four calls × two grants = eight rows.** Both writes are deliberate, disclosed self-granting —
> `VaultWriteNotGrantedError`'s docstring carries the account. **Neither is a defect; the count stated
> beside them was.**
>
> **This is I-328's shape at the other end of this same checklist.** Item 1 asserted five blocking
> conditions when two were open; item 6 asserted four grant rows when eight are written. **The
> Principal executes this checklist at the vault door with the registration already committed and P7
> already running**, where a read-back that does not match its stated expectation leaves only two
> outcomes: halt a completed seal on a false alarm, or exercise the judgment a no-judgment checklist
> exists to remove. **Three counts sit in this row and two of them were right**, which is the harder
> kind to catch.
>
> **It survived because it was never computed.** The number was stated in prose in four documents and
> propagated by transcription from the first; **no test had ever called `seal()` four times and counted
> the grants.** §7.10(3) — *acceptance is computed, not narrated* — applied to a number nobody ran.
> **The Principal's instruction to write and test item 6's script is what produced the measurement.**
> Filed **I-367, HIGH.** Casebook entry recorded beside I-328.

| # | Check | Passes when |
|---:|---|---|
| 1 | The seal-blocking conditions are cleared or explicitly accepted by Validation at C2 intake | **C7 and C8 — those two and nothing else, both OPEN and both discharged by the act itself** (C7 = Pod B's written acceptance of KC-002 plus the Principal's signature; C8 = four vault seals with the registration, one session, one UTC day, all four after item 7's grant closes). **[Source: `PREREG-002` §20, conformed table at R-010/R-011 — *"Seal-blocking · C7, C8. Nothing else."*]** The other three are not open: **C2 DISCHARGED** — ADMIT-CONDITIONAL, criteria 1–5 PASS (`VALIDATION-GATE0-002` §10.1; S3-D-023) · **C3 WITHDRAWN** (`REDTEAM-002A` §7; S4-D-006) · **C11 REMOVED from seal-blocking as circular** (S3-D-023 §6), re-imposed as a Gate 1 class-(b) condition. *Row conformed 2026-09-14 by the CIO's hand under the Principal's I-328 ruling; the row it replaces asserted all five open as of 2026-08-10.* |
| 2 | `book/registry.db` holds no family named `funding-carry-conditioning-002` | `SELECT COUNT(*) FROM hypotheses WHERE family = ...` returns 0 |
| 3 | `trial_budget` is **47**, not 79 and not 80 | the literal in §2.2 |
| 4 | `n_inherited` is **7**, not 0 | the literal in §2.8 |
| 5 | `forward_window_start` equals the UTC calendar day of the call, and equals the vault's `cutoff` | §2.5 — executed inside item 7's grant; see the note below |
| 6 | ~~The vault is sealed in the same session, same UTC day~~ **[R-011] ALL FOUR VAULTS ARE SEALED — one `HoldoutVault.seal()` call per `(source, dataset_id)` pair — in the same session and the same UTC day as item 7, and EVERY ONE OF THE FOUR AFTER ITEM 7'S GRANT HAS CLOSED. Never inside it. FOUR LOCKS PLUS ONE REGISTRATION, ONE SESSION, ONE UTC DAY.** | **All four of `binance`/`BTC/USDT`, `binance`/`ETH/USDT`, `binanceusdm`/`BTC/USDT:USDT`, `binanceusdm`/`ETH/USDT:USDT` have a `spec.json` under `book/vaults/` and an `ingest_ceiling` row in `book/pit.db`; ~~`write_grants` gains **four** `reason='VAULT_SEAL'` rows, all with `outcome='CLEAN'`~~ **[R-012 · 2026-09-14 · I-367] `write_grants` gains EIGHT `reason='VAULT_SEAL'` rows, all `outcome='CLEAN'` — TWO PER `seal()` CALL: four with `dispatch='HoldoutVault.seal'` (the vault file write) and four with `dispatch='HoldoutVault.holdout_spec_sealed'` (the event, logged through `_grant_log`, which opens its own grant under the same reason). Four is the count of CALLS, not of ROWS**, **all eight timestamped after item 7's row closed**. **Fewer than four ceilings = the check has failed; fewer than eight grant rows = the check has failed.** **The cutoff is normalised by `seal()` to a full UTC datetime — `ingest_ceiling.cutoff` reads `<C>T00:00:00+00:00`, not the bare date. That is correct and is not a mismatch.** §5 — see the note below |
| 7 | `open_hypothesis` executes inside an open `TrialRegistry.write_grant(reason="REGISTER_HYPOTHESIS", dispatch=..., token=...)` block, and no second `write_grant` is opened on the same registry object until that block has closed | `write_grants` gains exactly one new row, `reason='REGISTER_HYPOTHESIS'`, `outcome='CLEAN'`; `hypotheses` gains exactly one row for `family='funding-carry-conditioning-002'` |

**Item 1 is not this seat's to clear and is not cleared. A seal is a Standing Order 002 §4 hard
interrupt.**

**Note, added 2026-09-10, dispatch S4-D-013 (`research/DATA-IMPL-011-checklist-grant-step.md`),
discharging I-247.** The checklist as R-010 left it had no grant step, and `open_hypothesis` now
requires one (`RegistryWriteNotGrantedError` otherwise) — item 7 is that step, transcribed from the
call as executed and verified on a throwaway registry, not from `registry.py`'s docstrings (§7.12).
**Items 5 and 6 are unchanged in what they check; each now depends on being sequenced correctly
around item 7.** `HoldoutVault.seal()` opens its own `write_grant(reason="VAULT_SEAL", ...)`
internally, and grants do not nest (R-7): calling it from inside item 7's open block raises
`RegistryWriteGrantNestedError` **and rolls back item 7's otherwise-successful registration with
it** — full account at `DATA-IMPL-011` §3–§4. No literal in §1's table of sixteen moves.

---

*Director of Research · Castellan Capital · 2026-08-10 · dispatch S3-D-001*
*Trial budget ZERO. No hypothesis opened, no trial run, no registry write, no vault sealed, `harness/`
not touched, `book/` not written to, no test executed, no suite state reported. `book/registry.db`
reads **0 hypotheses / 0 trials** and must still read 0 / 0 when this document is put down.*
