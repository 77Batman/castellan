# PRE-REGISTRATION 002 — the funding-carry conditioning family

**Seat:** Director of Research (Seat 2) · **Date:** 2026-07-28
**To:** the Principal · cc CIO, Quant Validation, Devil's Advocate, PM Pod B, Head of Data & Infrastructure, CRO
**Family identifier:** `funding-carry-conditioning-002`
**Status:** **DRAFT, COMPLETE, SEALABLE.** Not sealed. Not registered. `book/registry.db` is untouched by this seat.

**What this document is.** The Charter §4.3 Gate 0 pre-registration record for the funding-carry conditioning family, in §7.2 Research Memo structure adapted for a pre-registration. All seven Gate 0 items are labelled `GATE 0 (n)`. §21 is the seal block: the exact binding field set for `TrialRegistry.open_hypothesis`, ready to execute.

**What this document is not.** It is not an intake verdict — that is Validation's, at Gate 0, and it is final short of the Principal. It is not a seal. **Sealing fixes `C` (D-007) and is Pod B's act after Validation's intake.** Nothing may be added after sealing: acceptance item **P7** fails Gate 1 if `hypothesis_sealed` postdates `C` at UTC day granularity, and every field left blank at sealing is a field a later retrieval can still move (Ruling 002 §3.5). This document is therefore written to be complete rather than skeletal.

**Origin, stated because it is the point.** This is the **first Director-originated hypothesis in the firm's history.** I-025 records today's origin ratio as **4 of 4 = 100% Principal-originated** and D-009 §4 directs that the Sprint 2 agenda contain Director-originated hypotheses. This document is that directive discharged by doing the work rather than by writing a justification for not doing it. It is not thereby entitled to a lower bar, and §19 recommends against it in one specific respect.

House rule 6 applies throughout: **[measured]** = read or executed in this repository this session · **[cited]** = external or internal named source · **[inferred]** = reasoned from measured/cited facts · **[assumed]** = unverified premise, flagged.

---

## REVISION BLOCK — R-008 · 2026-08-25 · PRE-SEAL · **THE THREE LITERALS**

> **UNSEALED. `book/registry.db` reads 0 hypotheses / 0 trials / 3 events [measured — read-only `SELECT COUNT(*)`, at open and at close]. Trial budget ZERO. NO NUMBER WAS COMPUTED FROM MARKET DATA: no query was run against `book/pit.db`, no distribution, moment, quantile or count of `z(t)` was inspected in any form, no backtest ran, no grid ran, no `harness/`, `book/`, `VALIDATION-*` or `REDTEAM-*` file was opened for writing, no test was run, and nothing was committed.**
>
> **The property that makes this revision worth making now, and which expires the moment it is used: the registry holds ZERO trials and no backtest has ever run in this firm, so a parameter chosen today is provably pre-output. That guarantee is a fact about `book/registry.db`, verifiable by anyone, not a claim about this seat's discipline.**

**Authority:** dispatch **S4-D-001** · the Principal's Sprint 4 §1 objective 1 (*"the first trial is logged; everything else is its dependency"*) · the Principal's ruling that the inertness finding is **disclosed and not redesigned**.
**Occasion:** `research/REDTEAM-002-funding-carry-seal.md` — **I-210, HIGH, seal-blocking** — and the Devil's Advocate's stated withdrawal condition, which is same-day on these three items and nothing else.
**Reasoning memo:** `research/DIR-RESTATE-001-prereg002-mechanism.md` **§14** — the full derivation of each literal, the trap named before the derivation, and the honest account of what was consulted.
**Payload:** `research/REGISTRATION-PAYLOAD-PREREG-002.md` — **no literal in the table of sixteen moves. `trial_budget` = 47, `n_inherited` = 7, `published_signal_haircut_applied` = 0.50, all unchanged.** Three prose-field bodies change **value**, by the R-004 mechanism, and §3.3 of the payload records the deltas.

| # | Clause changed | What changed | Why |
|---|---|---|---|
| **R41** | §6.2 sizing row and the parameter note; §10.5 grid note; §11.5 R4(a) row; §21 `statement`; §21 `horizon` | **`k` = 0.5, `d` = 1.0, `band` = 0.10 — NUMERIC LITERALS IN BINDING FIELDS.** Each is derived from the mechanism or from estimator arithmetic on the already-declared 30-day lookback, never from the series. **`d`:** a day sitting exactly at its true baseline still produces `\|z\|` of order `1/√30 = 0.18` from the sampling error of the rule's own 30-day reference level, so the deadband must be several multiples of that — O(1), not O(0.1) and not O(3); **1.0 is the round number in that bracket and the choice inside it is a declared judgment.** **`k`:** the interpretable quantity is `1/k`, the z-width from deadband to flat; selected at 2.0 because the hypothesis is about **sizing** and not timing, because K2 refused both up-scaling and the sign-flip so zero is the floor and should be reached only in an extreme, and because the resulting rule states in one sentence — **full size at or below one trailing standard deviation of excess funding, half size at two, flat at three.** **`band`:** derived from cost arithmetic alone, because `REDTEAM-002` §3.1 shows the two survival conditions pull it in **opposite** directions and neither may choose it — the smallest authorized rebalance must cost less than the daily carry it adjusts: `Δw × 24 bp ≤ ~3.25 bp/day` ⇒ `Δw ≤ 0.135`, rounded down. | **`REDTEAM-002` §2.2 / I-210 is correct and is not contested.** The sealed `statement` froze a sizing rule with two free symbols; §6.2's *"made now, before any measurement"*, §10.5's *"fixed at pre-registration"* and §11.5's *"parameter centres"* each asserted a fixing that did not exist. **`statement` is class (a) on existence and (c) on content, so P3, P4 and P7 could not have seen a post-seal choice** — the family's most consequential dial would have been set by whoever ran §15 step 3, invisibly to `prereg_sha256`, on the same day the grid centre and KC-002 clause (b)'s survival were decided. **Derivation in full: `DIR-RESTATE-001` §14.2–§14.4, including the two in-sample figures used and why.** |
| **R41(b)** | §10.5 grid note; §15 step 6 reading | **THE ±50% GRID NOW HAS A CENTRE, FIXED PRE-SEAL — I-212's SUBSTANCE DISCHARGED.** `lookback` centred at 30 → {15, 22.5, **30**, 37.5, 45}; `k` centred at 0.5 → {0.25, 0.375, **0.5**, 0.625, 0.75}. **§15 still runs the grid at step 6, after F-002 at steps 2–3, and that no longer matters**, because the centre is a sealed literal rather than a value chosen when step 6 arrives. | **I-029(d) relocated to the parameter axis is closed by fixing the centre, not by reordering the steps.** The plateau centroid still advances and `argmax` is still reported alongside it and never carried forward. **One residual, named and not repaired: `lookback`'s grid produces non-integer day counts (22.5, 37.5)** and this document does not specify the rounding. Filed **I-222**. |
| **R41(c)** | §14.2 (this note); §10.5 | **KC-002 CLAUSE (b) IS NOW COMPUTABLE — I-211's COMPUTABILITY DISCHARGED AND ITS SENSITIVITY MADE VISIBLE.** `\|Δw\| > 0.25` ⟺ `k·(z − d) > 0.25` ⟺ `z > d + 0.25/k`. **At the sealed literals: clause (b) kills on fewer than 30 days in the 187-day forward window with `z(t) > 1.5`.** | **The direction the Devil's Advocate named is real:** larger `k` and smaller `d` lower that threshold and make the sponsor's own pre-registered expected cause of death easier to survive — `(1.0, 0.5)` gives `z > 0.75`, `(0.25, 2.0)` gives `z > 3.0`. **The selected pair sits between them and this seat states plainly that it does not know whether `z > 1.5` occurs thirty times in a hundred and eighty-seven days.** §14.2's R7 expectation — clause (b) is the expected outcome, and the reason is the clamp rather than the market — **is unchanged and is not softened by having numbers.** **`band` = 0.10 is strictly below 0.25, so the turnover band cannot suppress a clause-(b) day; that check was run AFTER the choice and it ran in the family's favour, and this seat says so rather than presenting it as design.** |
| **R42** | §21 `mechanism`; §21 `statement`; §21 `falsifier` | **THE INERTNESS FINDING IS DISCLOSED IN THREE BINDING FIELDS AND THE RULE IS NOT CHANGED.** `max(0, z − d)` is zero whenever `z ≤ d`, so the rule acts only when funding is **rich** relative to its own baseline and does nothing when funding is cheap or negative — while §3.2 population 3, §3.3 risk 3 and §7.4 all place this family's left tail in funding **inversion**. **619 of 2,415 BTC days (25.63%) and 609 of 2,415 ETH days (25.22%) carry at least one negative funding print** [cited — `REDTEAM-002` §2.1, **measured by that seat**, read-only count over stored prints; **not re-measured here and not this seat's number**]. **Economic register — `mechanism`:** the field that names hedgers as the mechanism of inversion now says in the same field that the rule holds **benchmark weight** through inversion, a deliberate risk posture and **not** tail reduction. **Mechanical register — `statement`:** on the face of the frozen rule, including that the 30-day trailing baseline holds `w` at benchmark for up to thirty days after a cascade has collapsed `z`. **Evidential register — `falsifier`, on leg (ii):** whatever tail improvement leg (ii) measures cannot originate in the inversion regime, and a leg (ii) pass must not be read as tail protection there. | **The Principal ruled disclosure, not redesign, and this seat does not seek to reopen it.** K2 remains option (1); option (3) — sign-flip on inversion — remains declared, considered and not selected. **Changing K2 in response to an argument is a post-hoc conditioning move, priced by §7.2's escalation rule, and it costs the LINE.** **Three registers and not one because R29(b) is this document's own hardest-won lesson:** a correction exists where the seal reads it and nowhere else, and R-005 struck a condition where readers meet it and left it standing where the seal meets it. **What it costs the family, stated plainly: it removes the reading under which leg (ii) certifies tail protection generally. The claim under test narrows to tail reduction on the APPROACH to crowding, and the document now says so in the three strings that get hashed.** |
| **R43** | §21 `statement`; §21 `falsifier` | **THE TWO `[2020-01-01, C]` SITES ARE CONFORMED TO "THE LAST SETTLED COMMON BAR OF THE PRIMARY UNIVERSE AT THE FIRST RUN" — I-213's REMEDY, ADOPTED IN FULL.** `statement`'s *"over 2020-01-01 to C"* and `falsifier`'s *"over the full in-sample [2020-01-01, C]"* both move. **`C` is NOT redefined** and keeps its meaning as the freeze instant, still defining `forward_window_start`, the holdout and KC-002's window. | **The Devil's Advocate's remedy supersedes the CIO's three options and needs no Principal act.** `C` has been doing two jobs — the freeze instant and the in-sample right edge — and R23, R33, R34, R37 and I-097 are five repairs of the instances and none of the cause. **There is no seal date at which `[2020-01-01, C]` is true**, which is the whole finding. The replacement is (i) exactly what `oos_index` carries, (ii) exactly what Validation §7.3 has already ruled governs, and (iii) not a change to `C`. **The `universe` field carries a THIRD instance which the DA's remedy did not name and which this revision does not touch** — a span *measurement* with its own superseding note, not a computation window any seat runs. **Named rather than repaired.** Filed **I-221**. |

**WHAT R-008 COSTS THIS FAMILY, AND FOR THE FIFTH REVISION RUNNING IT MOVES IN BOTH DIRECTIONS.**

**For the family:** the seal's single blocking objection is discharged and the Devil's Advocate's withdrawal condition is met in full. **No source of death is removed.** Clause (b) is not made easier by having a number — it is made *visible*, and the visible number is one this seat cannot predict.

**Against the document, which is the half that matters:** **this document has been describing a trading rule it did not specify since 2026-07-28, through seven revisions, a 590-line Gate 0 verdict, two Validation specifications and roughly two hundred issues.** Three separate sentences asserted the fixing. **The eighth instrument found it with one grep, and the reason the first seven did not is that all seven were pointed at the document's metadata — its dates, denominators, classes and harness facts — and none at whether its specification specifies.** That is `REDTEAM-002` §7.1's base rate arriving exactly as that memo predicted, and this seat records it against itself.

**WHAT R-008 DOES TO THE DATED-CLAUSE OBLIGATION: IT ADDS NOTHING AND REMOVES TWO.** No replacement text inside a binding field carries an ISO date or a `C`-form expression, and none of the three literals is a date. **And R43 deletes the `FORMULA C` right-edge site from both `statement` and `falsifier`**, so the obligation falls by two. **This is the first revision of this document that does not grow it.**

> **AND THE FIRST DRAFT OF THIS REVISION DID GROW IT, BY FOUR, AND THIS SEAT CAUGHT IT IN THE SAME SESSION AND SAYS SO.** The R41/R42/R43 tags were first written into `statement`, `mechanism`, `falsifier` and `horizon` as **`[R41, 2026-08-25 — …]`** — **four new ISO sites inside four hashed strings, in the same pass that asserted zero were being added.** That is R-007's lesson committed by the seat quoting it, one screen after quoting it. **The dates are stripped; the R-numbers stay, and they are not dates.** Filed **I-226**. *A seat that only reports the version of its work that survived its own check is reporting a fiction.*

**What was NOT done, and why, so the absence is legible:**

- **No seal, no registration, no `open_hypothesis`, no registry write, no vault, no commit.** The seal is the Principal's act and follows this repair. Registry 0 / 0 / 3 at open and at close.
- **No trial, no backtest, no grid, no query against `book/pit.db`.** The Devil's Advocate's DA(2) dynamic-range test **is now executable at `(k, d) = (0.5, 1.0)` — `z > 1.5` — and this seat has NOT run it and endorses running it in the DA's own ordering: literals first, query second.** Reversed, it is selection over a continuum.
- **No change to the sizing rule, to K2, or to any declared menu or selection.** `N_conditioning` remains **7**.
- **No removal of the struck `2027-01-31` literals** — **I-204's standing prohibition holds.** They are load-bearing; E-14's `DIVERGENT` fires only because they are there, and the prohibition retires only when a test proves otherwise.
- **No repair of I-214, I-215, I-216 or I-218**, and no repair of the `universe` third instance. All named; none touched. **Out of scope by default under Sprint 4 §1.**
- **Nothing else that genuinely blocks the FIRST TRIAL was found. What is blocked is the first VERDICT** — I-173 / I-186, `harness/scripts/evaluate_dated_clauses.py` does not exist [measured, this session] and E-24 makes a nonzero exit a permanent INSUFFICIENT-DATA. **Trials may be logged into that state and cannot be unspent.** Filed **I-224**, addressed to the CIO and the Principal, **named and not repaired.**

---

## REVISION BLOCK — R-001 · 2026-08-04 · PRE-SEAL

> **This document remains UNSEALED. Every change below was made before `open_hypothesis` was called, against a registry holding 0 families and 0 trials [measured — `DATA-INGEST-002` §7], and therefore before any result on this family existed to select on. P7 has not yet bitten. Nothing here is an amendment to a sealed document; there is no sealed document.**

**Authority:** D-014 item 3 (*"If verified, the Director restates PREREG-002's mechanism before sealing — the carry's structural component and its premium component are distinct claims and the document freezes only once"*) · D-015 item 3 (first Director unit of Sprint 2, I-045 in hand).
**Issue:** **I-045** — SOL's dated structural break inside the sample. **Also discharges** the mechanism addition `DATA-VERIFY-001` §6.1 requested and I-042's underlying finding.
**Reasoning memo:** `research/DIR-RESTATE-001-prereg002-mechanism.md`, which evaluates the rejected alternatives and their reasons.

| # | Clause changed | What changed | Why |
|---|---|---|---|
| **R1** | §3.3, and the `mechanism` field of §21 | **Withdrawn:** the claim that ~11%/yr *"is approximately the market-clearing price"* of the carry supplier's risks. **Replaced** with the administered-constant/premium decomposition, and the conclusion re-derived on weaker premises. | The 0.01%/8h interest rate is an exchange-administered constant applied whenever the premium is inside a ±5 bp band, not a market-clearing price [cited — official, `DATA-VERIFY-001` §1.1; measured — §5.2]. |
| **R2** | §3.4, and the `mechanism` field of §21 | *"Funding is a **direct observable** of crowding"* → **funding is a *censored* observation of the premium**, censored to the interest rate inside the clamp band. | Same source. The censoring is what D-014 called the structural and premium components being distinct claims. |
| **R3** | §6.1 universe; §7.1 **K4**; §9.1; §11.1 vault; §12.4; §17; §21 `universe` | **SOL dropped from the universe.** K4's selection moves **within its declared menu of 5**, from option (2) to option **(4) "BTC+ETH only, SOL discarded entirely."** | I-045. SOL's funding series is generated by different formula parameters before and after 2022-11-09 [cited + measured, three converging series]. Neither remedy that would keep it is executable — see the memo §3.1–3.2. |
| **R4** | §6.2 *Bar granularity*; §7.1 **K6**; §21 `universe` | **The cadence constant is deleted.** *"the sum of the day's three 8h prints"* → the **exact arithmetic sum of realized prints in the bar's window, left-open right-closed, no assumed cadence**. | The three-print assumption is **measured false** (up to 12 prints in a day, 11 of 2,145 days) and Validation has already specified the replacement [cited — `VALIDATION-RULING-003` §3.2, §4 T-9]. **Not a design change — a defect repair conforming this document's prose to the sanctioned code path.** |
| **R5** | §7.1 (new row), §7.2, §7.3, §10.1, §10.4–10.5, §21 `universe` | **New conditioning choice K7** — treatment of a documented funding-parameter change on a universe symbol — declared with its full menu of 5, selected pre-measurement. | Binance states it does **not announce** subsequent cadence adjustments [cited — official, `DATA-VERIFY-001` §3.2]. The holdout is FORWARD and KC-002 is computed forward; a parameter change on BTC or ETH inside that window would otherwise require a post-hoc choice, which P3 refuses. |
| **R6** | §10.1, §10.5, §21 `trial_budget` | **`N_conditioning` 6 → 7. Trial budget 80 → 79** (the *"SOL on its own span"* diagnostic is struck). **Ceiling `N` = 86, unchanged.** | K7 costs 1; the removed SOL run returns 1. §10.4's measured `MinBTL(86, SR 1.0) = 6.14 yr` and its 0.43-year margin stand unedited, and **no new number was produced by this revision.** |
| **R7** | §5.3 (leg iii premise), §14.2, §16.1, §17, §19.3 | Pre-registered expectations **sharpened**: leg (iii)'s premise is now measured rather than cited; KC-002 clause (b) gains a named mechanism; and the primary universe's tail is recorded as **mild relative to the one the family theorises about**. | Consequences of R1–R3. Recorded now so none of it is claimed as foresight later. |

**What was NOT done, and why, so the absence is legible:**

- **No disclosure-only footnote.** Ruled out by the Principal (D-015 item 3) as *"out of scope for the operative state variable."* Every change above alters an operative clause.
- **No per-contract time-varying parameter table** (Principal's candidate (a)). The parameter history is not published and the vendor states it will not be [cited — official, `DATA-VERIFY-001` §3.2, §7(4)].
- **No declared break control** (Principal's candidate (b)). The break's start is documented; **its end is not**, and setting it from the measured cadence revert would be choosing a control's boundary from the data it exists to protect — the I-029(d) operation, for the third time.
- **No change to K1, K2, K3 or K5.** In particular **K3 remains "exclude nothing,"** and K7 was designed with that constraint binding: it excludes no bars and no returns, only declares a conditioning input unavailable.
- **No number computed.** Trial budget for this revision was **zero** and the registry is untouched.

---

## REVISION BLOCK — R-002 · 2026-08-05 · PRE-SEAL

> **This document remains UNSEALED. `book/registry.db` holds 0 hypotheses and 0 trials [measured — this session, `SELECT COUNT(*)` on `hypotheses` and `trials`]. Every change below was made before `open_hypothesis` was called and therefore before any result on this family existed to select on. P7 has not yet bitten. Trial budget for this revision was ZERO and no number was computed — every figure used is a prior `[measured]` or `[cited]` finding carried forward with its source named, or arithmetic on two already-cited integers, labelled at the point of use.**

**Authority:** dispatch S2-D-010 · **Occasion:** `research/VALIDATION-RULING-004-ml-trial-accounting.md` (Validation, 2026-08-04) and Issue Log **I-050**, **I-053**; `research/DATA-VERIFY-002-cadence-homogeneity.md` (Seat 9, 2026-08-04).
**Reasoning memo:** `research/DIR-RESTATE-001-prereg002-mechanism.md` §7, which records what changed and why.

| # | Clause changed | What changed | Why |
|---|---|---|---|
| **R8** | §1 recommendation box; §10.4 table and note; §10.1 contingent branch; §18 family exit; §19.2; §21 `success_criteria` | **The absolute admissible ceiling is `N` = 109, not 110.** The `N = 110` row's verdict cell — *"exactly at the span — zero margin"* — was **mislabelled**: `MinBTL(110) = 6.574` exceeds the 6.571 available, so 110 **fails**. Corrected, and the hard-stop trigger moves 110 → 109. | [cited — `VALIDATION-RULING-004` §2.2, §12, which states *"The true maximum is 109 and I am recording the correction."*] The measured figure `MinBTL(110) = 6.574` was already in this document; only the verdict drawn from it was wrong. |
| **R8(b)** | §10.4 | **R6's figures do NOT move, and the margin that does move is named.** Ceiling `N` = 86, `MinBTL(86, SR 1.0) = 6.14 yr`, margin **0.43 yr** — all unchanged, because 86 < 109. **What shrinks is the unused headroom above the declared ceiling: 24 → 23 trials.** | Stated because the dispatch is right that a shrinking margin is a finding, and because the honest finding here is that the *binding* margin is untouched while a *different* margin lost one trial. Reporting the second as though it were the first would be theatre in the pessimistic direction. |
| **R8(c)** | §1 recommendation box; §18 family exit; §19.2 | **Three surviving instances of the superseded trial budget `80` are conformed to R6's `79`.** R6 moved the budget 80 → 79 and these three clauses were not moved with it. | An internal contradiction between a document's recommendation box and its own budget section is exactly the kind of thing P7 freezes permanently and no later artifact can reconcile. Found on this pass, repaired on this pass, disclosed rather than silently conformed. |
| **R9** | §7.1.1; §7.2 BINDING ESCALATION RULE and the paragraph defending it; §14 KC-002 anti-reinterpretation clauses **2 and 3**; §19.3's named successor; §21 `universe`, `forward_kill_condition`; §22 (new row 12) | **The escalation rule is repaired on three heads and made executable.** (i) **Scope:** it read *K1–K6* and now reads **K1–K7** — K7 is discounted to 1 by the same rule and was not covered by the mechanism that makes the discount honest. (ii) **Quantity:** `n_inherited ≥ menu_size × chain_total` **over-declares by one `chain_total`**, because `family_stats` already sums the predecessor chain transitively; the correct declaration for a target denominator of `menu_size × chain_total` is **`n_inherited = (menu_size − 1) × chain_total`**. (iii) **Executability:** the registry refuses **both** forms for every menu size ≥ 2, so the rule as written was **decorative**. It is replaced by a form the harness executes today — **refusal, i.e. a hard stop** — with the harness change named and escalated rather than assumed. | **I-053** [cited — `logs/ISSUE_LOG.md` I-053; `VALIDATION-RULING-004` ML-17]. Head (ii) is **this seat's own arithmetic defect, found in its own rule** [measured — `harness/castellan/registry.py` `family_stats`, which sums `n_inherited` and logged trials transitively across `predecessor_chain`]. Filed **I-055**. |
| **R10** | §5.4; §16 row 1; §19.3; §21 `success_criteria`; §22 (new row 13) | **What the I-050 estimator correction changes for this family's Gate 1 submission is recorded pre-seal.** `T_STAT_HURDLE = 3.0` **does not move.** F-002 leg (i) **already** uses a Newey–West `t` and is therefore unaffected; **KC-002 is unaffected**, its clauses being bare comparisons with no `t`. **Gate 1's t-criterion is the one that narrows**, on a return series that is autocorrelated by construction. §19.3's expectation is revised **against** the family. | **I-050**, approved by the Principal [cited — `VALIDATION-RULING-004` §14, §14.1: the `t` assumed serial independence; the firm's one measured instance is ρ = 0.83, implying ≈3.3× inflation, and the error ran **permissive**]. A pre-registration that did not say what a known-pending correction does to its own Gate 1 margin would be arranging a later surprise. |
| **R11** | New §10.7; §10.5 walk-forward clause; §9.2 (new look-ahead row); §15 step 7; §16 (t-stat and σ_SR rows); §20 C13; §21 `success_criteria`; §22 (new row 14) | **`VALIDATION-RULING-004` binds this family in two places and neither was previously carried.** (i) **ML-2** requires a family asserting it is *not* fitted to carry that assertion **as a sentence in the sealed block** — *"Silence is not that assertion"* — and a missing or partial ML block is **REJECTED at Gate 0, not deferred**. The sentence is added. (ii) **ML-1**'s boundary case spares this family **only because** the plateau centroid advances by rule; the **walk-forward step was unspecified**, and per-window re-selection at an argmax would have made this a **fitted family**, at which point ML-13 charges the grid's full cardinality per window. The walk-forward configuration is now **fixed at the plateau centroid** and no per-window selection occurs. | [cited — `VALIDATION-RULING-004` ML-1, ML-2, ML-13, §12]. Validation's §12 records PREREG-002 §10 as *"Untouched"* — that is correct **for the `N` accounting** and §10.7 confirms it choice by choice; it is **not** correct that the ruling leaves the document alone, and this row records the difference rather than resting on the summary line. |
| **R12** | §7.1.1 blocking-check paragraph; §20 C12; the seal-readiness block | **C12 is DISCHARGED, and the discharge is narrower than the premise it was protecting.** `DATA-VERIFY-002` measures **0 deviating days of 4,802 symbol-days** on BTC and ETH, both directions, full span [measured — Seat 9]. **That verifies the CADENCE dimension only, not the PARAMETER dimension:** the documented 2025-09-18 firm-wide change shows **3 prints on both symbols**, so a cadence sweep is structurally blind to it, and **K7 governs it by declaration rather than by measurement.** | [measured — `research/DATA-VERIFY-002-cadence-homogeneity.md` §3, §4]. C12's own text asked for a print-count sweep and got a clean one; recording the discharge without recording what the instrument cannot see would leave the family's homogeneity claim resting on a control that was never pointed at the risk. |

**ONE ROOT CAUSE UNDER R9, NAMED BECAUSE IT APPEARS IN FOUR PLACES AND WAS REPAIRED FOUR TIMES.** Every head-(ii) defect above is the same misreading: **that a successor must carry its predecessor's trial count in `n_inherited`, when `family_stats` already carries it transitively through `predecessor_family`** [measured — `registry.py`]. It appears in (1) §7.2's escalation rule, (2) **KC-002 anti-reinterpretation clause 3** — *"a new family opened with `n_inherited ≥` the killed family's final `n_trials` plus its own"*, which is **redundant and unexecutable for the same reason and is replaced by `predecessor_family` alone**, (3) §19.3's named successor, and (4) **`VALIDATION-RULING-004` ML-17, which copies this document's formula citing it as the source** [cited]. **The firm's rule that a restatement cannot escape its predecessor's count is delivered better by the harness than by any of the four sentences that tried to state it.** Filed **I-055**.

**What was NOT done, and why, so the absence is legible:**

- **No seal.** Sealing is sequenced separately and is not this seat's to trigger. **C2, C3, C7, C8 and C11 remain open** and the seal-readiness block at the foot of this document is updated rather than relaxed.
- **I-045 is NOT closed by this revision.** Its owner line routes closure to `quant-validation` and this seat does not have it. C12 — a condition in this seat's own document — is discharged; **that is not the same act and the two must not be read as one.**
- **No declared menu edited.** K1's option (8) still names SOL and K4's option (2) still names SOL. Only selections move, and in this revision **no selection moved at all** — R8 through R12 touch a ceiling, an escalation rule, a disclosure, an assertion, and a condition's status. **`N_conditioning` remains 7 and the trial budget remains 79.**
- **No number computed.** The one arithmetic operation performed is `109 − 86 = 23`, on two integers each already `[cited]` or `[measured]` — the same treatment §7.3 gives its counterfactual product.

---

## REVISION BLOCK — R-003 · 2026-08-06 · PRE-SEAL

> **This document remains UNSEALED. `book/registry.db` holds 0 hypotheses, 0 trials and 1 event [measured — this session, `SELECT COUNT(*)` on `hypotheses`, `trials`, `events`]. Every change below was made before `open_hypothesis` was called and therefore before any result on this family existed to select on. P7 has not yet bitten. Trial budget for this revision was ZERO. NO NUMBER WAS COMPUTED: every figure below is `[cited]` from `VALIDATION-SPEC-002-serial-corrections.md`, `DATA-IMPL-006-serial-corrections.md`, `VALIDATION-RULING-004`, or the Issue Log, or is integer arithmetic on two already-declared integers, labelled at the point of use.**

**Authority:** dispatch S2-D-020 · the Principal's ruling on I-057, recorded verbatim at `VALIDATION-SPEC-002` §0.2 · Validation's countersigned tightening at `VALIDATION-SPEC-002` §7.2 and I-064.
**Occasion:** `research/VALIDATION-SPEC-002-serial-corrections.md` (Validation, 2026-08-04, 57 binding clauses) and `research/DATA-IMPL-006-serial-corrections.md` (Seat 9, 2026-08-05) · Issue Log **I-057, I-060, I-061, I-063, I-064**.
**Reasoning memo:** `research/DIR-RESTATE-001-prereg002-mechanism.md` §8.

| # | Clause changed | What changed | Why |
|---|---|---|---|
| **R13** | §10.4 (new §10.4.1); §1 recommendation box; §21 `success_criteria` | **§10.4 SEALS A FUNCTION, NOT A CONSTANT.** The absolute ceiling is no longer the integer 109. It is `N_max = min(109, max_admissible_trials(span, SR_realized, ppy, vif = VIF_gate(ρ̂)))`, with `ρ̂` the family's **net-return** autocorrelation measured by the harness from logged trials at every `evaluate_gate1` call. `109` is not a constant that happens to bind; it is `max_admissible_trials(6.571, 1.0, vif = 1.0)` and it is the first argument of a `min`. | The Principal's ruling on I-057, verbatim [cited — `VALIDATION-SPEC-002` §0.2]. The construction is **monotone-conservative** — measurement can only tighten, never loosen — so it is **not** the I-029(d) operation; it is *"the `min(t_NW, t_raw)` construction extended to `N`."* **Seat 9 has since demonstrated this empirically rather than merely implemented it:** 145 draws for `N_max` and 900 for DSR across ρ ∈ [−0.6, +0.8] using real measured VIFs, **zero violations** [measured — `DATA-IMPL-006` §2]. |
| **R14** | §10.4 (new §10.4.2); §1 recommendation box | **THE BINDING THRESHOLD IS ρ̂ ≤ 0.034, NOT 0.1.** The functional form in R13 is written against **0.034**. `MinBTL(86, 1.0) = 6.1359 y` against 6.571 y available ⇒ maximum admissible VIF 1.0709 ⇒ binding AR(1) `ρ̂ = 0.0342` [all cited — `VALIDATION-SPEC-002` §7.2; I-064]. At the Principal's originally-stated 0.1 the ceiling is **55** and this family is **31 trials over, not marginally over**. | Validation tightened the trigger ~3× under the Principal's own §8 asymmetry, **without requesting an act, which is exactly how that asymmetry is designed to work**, and filed it as I-064 rather than exercising it silently. The Principal has countersigned: *"my number was a prediction, Validation's is a derivation."* **0.034 supersedes 0.1 wherever the two appear.** |
| **R15** | §10.5 (rebuilt); §10.1; §1 recommendation box; §18; §19.2; §21 `trial_budget` | **THE TRIAL BUDGET IS NOW SET AGAINST A DECLARED CONSERVATIVE PLANNING `ρ`, AND THE `ρ` IS NAMED: `ρ_plan = 0.10`.** The budget becomes **two-stage**. **Stage 1 — 47 post-seal trials, AUTHORIZED NOW**, admissible at `ρ_plan = 0.10` (`N_max` = 55 [cited]; declared ceiling 7 + 47 = **54**, one trial of margin). **Stage 2 — up to 32 further trials, DECLARED BUT NOT AUTHORIZED**, unlocked only by a measured `ρ̂` whose cited `N_max` admits them; in full only at `ρ̂ ≤ 0.034` (7 + 79 = 86). The former flat budget of 79 is preserved **exactly** as Stage 2's contingent ceiling. | The Principal: *"burning `N` the measured ceiling may disallow is the sponsor's risk to declare, not discover."* **The old budget was set against `ρ = 0` by silence and sat at 7 + 79 = 86 = `N_max(0.034)` — ZERO trials of margin at its own binding threshold.** `ρ_plan` and its justification are §10.5.1; the two-stage construction and its anti-gaming answer are §10.5.2. **This satisfies V-7's declared-planning-`ρ` clause, which is non-binding and grades nothing — but this seat elects to make it binding on its own budget, which is the seat's to do.** |
| **R16** | New §10.8 | **`VALIDATION-SPEC-002` §7.4's PRE-COMMITTED VERDICT BANDS ARE RECORDED IN THIS DOCUMENT, before any measurement exists.** ρ̂ ≤ 0.034 → PASS on length · 0.034 < ρ̂ ≤ 0.15 → **FAIL on length, PARK**, repairable by ≤ 11 months more history at ρ̂ = 0.1 · 0.15 < ρ̂ ≤ 0.30 → FAIL, PARK nominal / kill in practice · ρ̂ > 0.30 → **KILL** · `\|ρ̂\| ≥ 0.97` or `n_logged = 0` → **INSUFFICIENT-DATA, never PASS**. **And the Sharpe escape is recorded as closed by construction: raising realized Sharpe by searching raises `N`, which raises `MinBTL`, which raises the Sharpe required.** | [cited — `VALIDATION-SPEC-002` §7.4, §7.3 route 2, V-5]. Pre-committing the verdict rule before the measurement exists is Ruling 001 §4.4's own device and is used here for the same reason. **A band recorded in the sponsor's own pre-registration cannot be renegotiated by the sponsor at Gate 1.** |
| **R17** | §10.4 (new §10.4.3) | **I-063 IS DISCLOSED ON THE FACE OF §10.4 RATHER THAN IMPLIED AWAY.** The Gate 0 intake ceiling is **necessarily** computed at `VIF = 1` — at intake no trial has a return series, so `ρ̂` is unmeasurable at exactly the moment the ceiling is quoted. V-6's mandatory render string is carried verbatim: the figure is an **UPPER BOUND**, will be re-evaluated at Gate 1, **can only fall**, and **is not a budget**. | [cited — I-063; `VALIDATION-SPEC-002` V-6]. **Structural and not closeable** — no construction can measure a family's serial dependence before it has produced a return series. Disclosure is the only remedy and it is mandatory. This document previously quoted 109 with no such label. |
| **R18** | New §10.9 | **I-060 AND I-061 CHECKED AGAINST THIS DOCUMENT CHOICE BY CHOICE, AND THE ANSWERS ARE NOT THE SAME.** **I-060 does not bite as a clause** — this family is not a fitted family (§10.7(a)), ML-3–ML-27 do not reach it, and its diagnostics were already counted toward `N` under the conservative reading the Principal has ruled governs pending Sprint 3. **The arithmetic pattern I-060 names DOES bite in substance, at a tighter `ρ` than I-060's own 0.045** — this family's obligations exceed its ceiling above **ρ̂ = 0.034**. **I-061: nothing in this document rests on RULING-004 §2.1's frequency-invariance conclusion**, verified clause by clause; one forward-looking consequence for the §19.3 successor is recorded. | Confirming rather than asserting is the dispatch's instruction and it is the right instruction: **the summary line "not a fitted family" would still have read that way if one of the seven choices had failed the test**, exactly as §10.7(d) says of Validation's own "Untouched." |

**WHAT R-003 COSTS THIS FAMILY, STATED FIRST BECAUSE IT IS THE LESS FLATTERING HALF.**

**The authorized budget falls from 79 to 47 and the declared ceiling from 86 to 54.** That is a **40% cut to authorized `N`**, taken voluntarily, before any measurement, against a `ρ` this seat named rather than discovered. If `ρ̂` measures at or below 0.034 the cut will have been unnecessary and Stage 2 restores the family to exactly where R-002 left it. **This seat regards the asymmetry as decisive and says so plainly: an unnecessary Stage-1 cut costs a scheduling delay, and an unauthorized Stage-2 spend at ρ̂ = 0.10 costs the family its Gate 1 verdict permanently, because trials cannot be unspent** [cited — `VALIDATION-SPEC-002` V-5, and `InheritedCountDoubleCountError` closes the successor route].

**What was NOT done, and why, so the absence is legible:**

- **No seal.** C2, C3, C7, C8 and C11 remain open. The seal-readiness block is updated, not relaxed. **R-003 adds no new blocker and clears none.**
- **I-045 is NOT closed.** Its owner line routes closure to `quant-validation` and this seat does not have it. Unchanged by R-003.
- **No declared menu edited.** K1–K7's menus are untouched and **no selection moved.** `N_conditioning` remains **7**. R-003 moves a ceiling's *form*, a budget's *size and authorization structure*, and adds three disclosures.
- **No harness file touched, no test run, no suite state reported.** `harness/` is Validation's this dispatch.
- **No number computed.** The arithmetic performed is `2+3+7+25+10 = 47`, `47+22+10 = 79`, `7+47 = 54`, `7+79 = 86` — integer sums of line items already declared at §10.5, of the same class as R-002's `109 − 86 = 23`. `N_max` at every `ρ` quoted is `[cited]` from `VALIDATION-SPEC-002` §6.2's measured table and **is not re-derived here**, because re-deriving it is a computation a zero-trial budget does not authorize.

---

## REVISION BLOCK — R-004 · 2026-08-10 · PRE-SEAL

> **This document remains UNSEALED. `book/registry.db` holds 0 hypotheses, 0 trials and 1 event [measured — this session, read-only `SELECT COUNT(*)`; the one event is `book_open`]. Every change below was made before `open_hypothesis` was called and therefore before any result on this family existed to select on. P7 has not yet bitten. Trial budget for this revision was ZERO. NO NUMBER WAS COMPUTED: every figure is `[cited]` from `VALIDATION-SPEC-002`, `VALIDATION-SPEC-003`, `VALIDATION-RULING-004/005` or the Issue Log, or is `clamp`/integer arithmetic on already-declared integers, labelled at the point of use. No `harness/` file was touched, no test was run, and no suite state is reported.**

**Authority:** dispatch S3-D-001 · Standing Order 002 §1 objective 1 · the Principal's disposition on **I-105**.
**Occasion:** `GATES.md` **§4.7.2** — *"for every limit the document claims, name the field the harness reads to enforce it; if there is no such field, there is no limit"* — applied to this document, limit by limit; and **I-105**, which requires that the two-stage budget be **registered** rather than described.
**Reasoning memo:** `research/DIR-RESTATE-001-prereg002-mechanism.md` **§9** (the audit) and **§10** (I-045).
**Payload:** `research/REGISTRATION-PAYLOAD-PREREG-002.md` — the sixteen binding fields with their final values. **Where that payload and this document's prose could diverge, the payload governs, and this row is the authority for saying so.**

| # | Clause changed | What changed | Why |
|---|---|---|---|
| **R19** | §1 recommendation box; §10.1; §10.3 (struck); §21 `n_inherited` (**new field, previously absent from the block**); §21 `success_criteria`; §21 `universe`; §18 | **`n_inherited` IS SEALED AT 7, NOT 0. `N_conditioning` MOVES FROM A DECLARED FLOOR NOTHING READS TO A REGISTERED FIELD WITH FOUR CONSUMERS.** The seven menu-declared pre-measurement choices K1–K7 are registered in the field built for exactly that quantity. | **§10.5.2's own Stage 2 unlock table is reproduced only at `declared_ceiling_base = 54`.** `gates.py:565` computes `declared_ceiling_base = fam.n_inherited + sealed`, and `VALIDATION-SPEC-003`'s `test_tbe_15` fixes `base, inc = 54, 32` [cited]. **54 = 7 + 47.** At `n_inherited = 0` the base is 47 and the same mechanism admits **30 where this document declares 23**, and **8 where it declares 1** — **permissive, at the two rungs that bind.** Filed **I-130, HIGH**. Derivation: `DIR-RESTATE-001` §9.4. |
| **R19(b)** | §10.3 | **§10.3's PREMISE IS STALE AND IS STRUCK.** *"There is no `n_inherited` parameter and no `n_inherited` column"* was true when written and is **false now** [measured — `registry.py`: the column is in `SCHEMA`, `_migrate` ALTERs it onto pre-existing DBs, the signature carries it, and it is the sixteenth entry of `_BINDING_FIELDS`]. **I-018 / I-027 / C-001 §3.0 shipped the column this document says does not exist.** | Sealing it freezes a **false statement of harness fact**, permanently, and freezes with it a §21 disclosure line — *"the 7-trial conditioning floor is declared and unenforced (I-027)"* — that would then be **false on the face of every Validation Report on this family.** Filed **I-131**. |
| **R19(c)** | §10.3 table; §10.4; §1 | **WHAT R19 COSTS, PAID RATHER THAN MITIGATED.** Registry-enforced `N` at a full Stage 1 spend is **54, not 47**; at full Stage 2 **86, not 79**. DSR is deflated against 86 (`gates.py:779`, `:788` pass `fam.n_trials`) and MinBTL evaluated at 86 (`gates.py:856`) [measured]. **§10.3's 0.13-year I-027 residual is not mitigated — it is paid.** | `MinBTL(86, SR 1.0) = 6.14 yr` against 6.571 available, margin **0.43 yr** — **already measured, not re-derived** [cited — §10.4]. **§10.3's "honest (registry + declared conditioning)" row becomes the ENFORCED row; its "registry as it will read" row is struck.** The change moves the family's own length criterion in the **tightening** direction, and this seat takes it deliberately. |
| **R20** | §10.5.2 (unlock rule rebuilt); §21 `success_criteria`; §20 C13 | **STAGE 2 IS REGISTERED, NOT DESCRIBED — I-105's DISCHARGE.** The sealed `trial_budget` is **47** (Stage 1). Stage 2 survives **only** as the description of a `trial_budget_extension` event in `VALIDATION-SPEC-003`'s **CONTINGENT** form: `increment = 32`, `predicate = {"name": "n_max_admits_declared_ceiling", "params": {}}`, self-issued and safe to self-issue because **the criterion recomputes `N_max` and never trusts the event** (B-16). | **The Principal offered two dispositions and this seat chooses the first — register, do not strike — and does not regard it as close.** Striking would leave 47 flat with no route above it but a **DISCRETIONARY** extension, which under B-14 needs a **person's** countersignature rather than **arithmetic's**. Replacing an arithmetic gate with a human one is strictly worse on the axis this firm cares about. Every property of the contingent form runs **against** the sponsor: B-17's closed vocabulary and required-empty `params`; B-19's unevaluable-⇒-FAIL; B-20's aggregate cap; B-23's malformed-⇒-FAIL even inside budget. |
| **R20(b)** | §10.5.2 | **I-104 CONFORMED. *"READ FROM THE CITED TABLE AND NEVER INTERPOLATED"* IS STRUCK.** The nine-row table at `VALIDATION-SPEC-002` §6.2 is a **rendering** of `stats.max_admissible_trials`, which is continuous. **RULING 003-A: the function governs** [cited — `VALIDATION-SPEC-003` §7.3]. | A lookup forbidding interpolation has **no defined value at `ρ̂` = 0.07**. The sponsor's intent — *no Stage 2 trial spent on an unmeasured or stale `ρ̂`* — is preserved exactly, and the family receives the allowance its own `ρ̂` earns rather than the next rung down, which is more accurate in **both** directions. |
| **R21** | New §10.10; §21 `universe`, `success_criteria`, `forward_kill_condition` | **THE §4.7.2 AUDIT IS RECORDED ON THE FACE OF THIS DOCUMENT, INCLUDING ITS UNFLATTERING HALF.** **Nine of the sixteen binding fields are sealed and read by nothing** [measured — zero non-`registry.py` consumers]. The three fields a pre-registration puts its methodology in — **`universe`, `horizon`, `success_criteria` — have ZERO consumers in the entire harness.** K3's "exclude nothing," the no-winsorization clause, `w_max = 1.0`, the capacity screen, the ML-2 assertion, the plateau-centroid commitment, F-002's E2 "evaluated ONCE," and all eleven mandatory disclosure lines are **enforced by the seat that writes the loop and by nothing else.** | **The seal gives tamper-EVIDENCE, not enforcement**, and this document has been written in places as though the two were the same. Filed **I-133**. Two entries are separately sized: **`published_signal_haircut_applied = 0.50` is applied by no code path** (**I-134**) though §5.4 derives this family's entire `t(α) ≈ 6.0` burden from it; and **no harness path evaluates a kill condition on any date** (**I-135**), so KC-002 clause 5's *"silence is a kill"* — the clause that exists precisely to defeat non-execution — is itself defeatable by not running it. **Neither is a repair request. Both are the document ceasing to describe a control it does not have.** |
| **R22** | §15 step table | **§15's OWN STEP BUDGET SUMS TO 83 AGAINST A DECLARED 79, AND IS CONFORMED.** Diagnostics read **8** (step 4 ≤2 + step 5 ≤6) against §10.5.3's **≤7**; `N_forward` reads **≤25** (step 8) against §10.5.2's **≤22**. `2+1+2+2+6+25+20+25 = 83` [integer arithmetic on already-declared line items]. | R3, R6 and R15's conforming passes moved §10.5 and did **not** reach §15's arithmetic — **the same defect class R8(c) repaired for the three surviving instances of the superseded 80.** An internal contradiction between a document's method section and its own budget is exactly what P7 freezes permanently. Filed **I-136**. Found on this pass, repaired on this pass, disclosed rather than silently conformed. |
| **R23** | §11.4; §21 `forward_window_start` | **THE LITERAL `"2026-07-28"` IS NOT BINDING AND THE PAYLOAD SAYS SO.** `forward_window_start` = **`C`, the UTC calendar day of the `open_hypothesis` call**, computed at the instant of the act. | The literal was drafted against an intended same-day seal that **§20.1 then recommended against**, and it has been stale in this document since 2026-08-04. `forward_kill_condition` already carries the correct treatment for the observation date — *"the DRAFTED DATE IS NOT BINDING — the formula is"* — and R23 extends it to the window's start. **One field's literal cannot be fixed before the act; naming the computation is mechanical, not interpretive.** |

**WHAT R-004 COSTS THIS FAMILY, STATED FIRST BECAUSE IT IS THE LESS FLATTERING HALF.**

**The registry-enforced denominator rises by 7 at every stage** — 47 → 54 authorized, 79 → 86 at full Stage 2 — and it rises into DSR and into MinBTL, not merely onto a report face. **R-003 cut what this family may spend; R-004 raises what it is charged for what it spends.** The two move in the same direction and neither was forced by a measurement. **And R21 records that the majority of this document's stated limits are enforced by no field at all** — including the 50% haircut from which §5.4 derives the family's largest acknowledged hurdle, and KC-002's silence clause, which this seat wrote and defended and which the engine has never been able to fire.

**What was NOT done, and why, so the absence is legible:**

- **No seal, no registration, no registry write.** **`open_hypothesis` IS the seal** — P1 computes `prereg_sha256` on first registration [measured] — so registering and sealing are one act, and that act is a Standing Order 002 §4 hard interrupt. **C2, C3, C7, C8 and C11 remain open and R-004 clears none and creates no sixth.** `book/registry.db` must read 0/0 when this revision is put down, and it does.
- **I-045 is NOT closed. Declined for the fourth time.** Its owner line routes closure to `quant-validation`. `DIR-RESTATE-001` §10 states, as three answerable questions rather than as a request, what C2 needs in order to rule.
- **No declared menu edited. No selection moved.** K1–K7's menus are untouched and **`N_conditioning` remains 7.** R19 changes **where the 7 lives**, not what it is.
- **No `harness/` file touched, no test run, no suite state reported.** The four remaining reds — `test_G2`, `test_h7`, `test_h8`, `test_mbs_12` — are Validation's. **`test_h7` and `test_h8` do not block the registration act and do bear on what it is worth**, because they grade whether a seeded denominator reaches DSR and MinBTL — which, at `n_inherited = 7`, is now this family's question and was not at 0. Raised as a consequence, not as a request. See `DIR-RESTATE-001` §9.6.
- **No number computed.** The arithmetic performed is `clamp(N_max − 54, 0, 32)` on four already-cited `N_max` integers, `7 + 47 = 54`, `7 + 79 = 86`, and `2+1+2+2+6+25+20+25 = 83` — the same class as R-002's `109 − 86 = 23`.

---

## REVISION BLOCK — R-005 · 2026-08-10 · PRE-SEAL

> **This document remains UNSEALED. `book/registry.db` holds 0 hypotheses, 0 trials and 1 event [measured — this session, read-only `SELECT COUNT(*)`; the one event is `book_open`]. Every change below was made before `open_hypothesis` was called and therefore before any result on this family existed to select on. P7 has not yet bitten. Trial budget for this revision was ZERO. NO NUMBER WAS COMPUTED: every harness fact is `[measured]` at a named file and line, every figure about this family is `[cited]` from a prior artifact, and the only arithmetic is `4+4+8 = 16`, `5+11 = 16` and `20+7+34 = 61` on already-enumerated sets. No `harness/` file was touched, no `VALIDATION-*` document was touched, no `book/` artifact was written, no test was run, and no suite state is reported.**

**Authority:** dispatch **S3-D-003** · the Principal's adoption of this seat's **I-133** conclusion, verbatim: *"most of these cannot be mechanized and should still be written down; what must stop is the document describing them as controls."*
**Occasion:** the **class mandate** — every limit this document claims must carry its class, **(a) harness-enforced** (named field, named code path) · **(b) procedure-enforced** (named executor, named cadence, named artifact) · **(c) declared commitment** (binding as a matter of record, enforced by audit and adversarial review only).
**Reasoning memo:** `research/DIR-RESTATE-001-prereg002-mechanism.md` **§11**.
**Payload:** `research/REGISTRATION-PAYLOAD-PREREG-002.md` — **UNCHANGED. `trial_budget = 47`, `n_inherited = 7`, all sixteen literals as recorded.** Three prose fields receive conforming inserts by the R-004 mechanism (its own §3.1 records four); the document is unsealed and a prose-field edit is a draft edit, not an amendment.

**THIS IS A LABELLING REVISION, NOT A MECHANIZATION ONE. Nothing below is made enforceable that was not. A class-(c) label is a full and honourable answer, and this document now declares thirty-four class-(c) commitments rather than implying sixty-one controls and holding twenty.**

| # | Clause changed | What changed | Why |
|---|---|---|---|
| **R24** | **New §10.11 — THE CLASS REGISTER**; §10.10 (superseded as a partition, retained as the finding) | **EVERY LIMIT THIS DOCUMENT CLAIMS NOW CARRIES ITS CLASS, IN THIS DOCUMENT.** **Sixty-one limits classified: 20 (a) · 7 (b) · 34 (c).** For every (a): the field where one exists and the code path always. For every (b): executor, cadence, artifact. **The register is in the sealed text and not in a memo about it**, which inverts R-004's placement convention deliberately — R21 put the audit's conclusions here and its table in `DIR-RESTATE-001` §9; **the next reader needs the class beside the limit, not a pointer to it.** | §4.7.2 delivered the test; this delivers the answer in the place the answer is read. A limit whose class lives in another file is a limit whose class the next reader will not have. |
| **R25** | §10.10 (count cells struck); §10.11.1 | **§10.10's FIELD-COUNT ARITHMETIC IS WRONG AND IS CORRECTED: the partition is 5 (a) / 11 (c), not 4 / 3 / 9.** §10.10's count cells read **4 / 3 / 9** while its own rosters name **4 / 4 / 8**. **Eight binding fields have zero consumers, not nine.** The **9** is **§9.2's count of category-(c) *limits* — c1 through c9 — transplanted into a column that counts *fields*.** Two denominators, one number. | **R8(c)'s and R22's defect class for the third time** — an internal contradiction between a count and its own roster, which P7 freezes permanently. **It had already propagated: S3-D-003's own mandate directs the relabelling of "all nine zero-consumer binding fields."** The roster it names is complete; the cardinal is not. Filed **I-141, MEDIUM.** Found on this pass, repaired on this pass, disclosed rather than silently conformed. |
| **R26** | §1 recommendation box; **§12.1, §12.2, §12.3, §12.6, §12.7**; §14's condition precedent; §15 step 0; §16 row 1; §17 risk 1; §20 C1; the seal-readiness block | **I-034 / C1 IS IMPLEMENTED, AND THIS DOCUMENT DESCRIBED THE PRE-REPAIR COST MODEL AT SIX SITES.** `CRYPTO_PERP_TAKER` **carries no funding term** — *"funding is a signed cash flow and is accrued in the engine from the realized `pit_funding_panel` series, never as a scalar rate here"*; **`CRYPTO_SPOT_TAKER` exists** (D-013 §1, Principal-authorized); `carry.py` supplies the sanctioned carry-stress path; **`scaled(m)` leaves carry bit-identical (T-16)** [all measured — `harness/castellan/costs.py`, `carry.py`]. `DATA-IMPL-004` §5–§6: ***"All nineteen T-cases are implemented and pass."*** | **R19(b)'s defect class, running in the conservative direction, which is why four revisions passed over it.** **One of the six sites has a dated consequence one day away:** §14's condition precedent downgrades this family to **ADMITTED-AS-EXPLORATORY on 2026-08-11** — *"pre-declared ineligible for Gate 1"* — **on a premise that is false.** Filed **I-140, HIGH**, which is a Standing Order 002 §4 hard interrupt; **the interrupt is a consequence of the severity, not the purpose of the filing.** **This seat records the measurement and conforms its own document; it does NOT close I-034 and does NOT close C1** — both route to `quant-validation → head-of-data-infra`, exactly as R12 discharged C12 while declining I-045. |
| **R26(b)** | §1 recommendation box; §12.5; §16 | **WHAT R26 DOES NOT REPAIR, PAID RATHER THAN GLOSSED.** **§12's defect (d) stands: `CostModel` has no field that can charge liquidation or venue-insolvency risk** — the largest risk in the mandate — and `VALIDATION-RULING-003` §4 declines to invent a number [cited]. **Class (c), disclosed.** And **the breakeven cost is still unstated — but the reason changes.** It is no longer *"unstateable because the instrument is broken"*; it is **"unstated because computing it is a trial and this dispatch's budget is ZERO."** `carry.carry_breakeven_bps_annual` is the house-rule-5 instrument, it exists, and it is monotone in its shift by construction. | **House rule 5 becomes satisfiable by this family and is not yet satisfied**, and the document must say which of those two it is. The recommendation box has read *"cannot be stated, and the reason is a defect not an omission"* since 2026-07-28. **It is now an omission, and a cheap one — one trial inside Stage 1's 47.** |
| **R27** | §10.5.2 (the objection paragraph); §20 **C10**; §10.11 | **I-022 IS REPAIRED IN CODE AND OPEN IN THE LOG, AND THREE CLAUSES IN THIS FAMILY'S PAPERS REST ON IT BEING LIVE.** `gates.py:527–640` `_trial_budget_criterion` **FAILs three separate ways** — B-7 *"NO AUTHORIZED BUDGET"* (`:598`), **B-9's ordering walk per trial naming the offending k** (`:606–620`), and B-23's malformed-extension branch checked ahead of both [measured]. `DATA-IMPL-007` §5: *"Can close. All 19 test functions green."* **The literal `True` I-022 quotes does not exist in `gates.py`.** | **The correct statement is neither the old one nor a naive repair. I-132 stands: `log_trial` reads no budget, so nothing *prevents* an over-budget spend. Prevention: none. Detection and refusal: automatic, per trial, with the offending trial named.** §10.5.2's two-stage budget has **a better defence than this document gives it** — and this seat, who built the two-stage budget and would benefit from overstating its protection, notes that this correction runs **in the family's favour** and states it for that reason rather than in spite of it. **C10's weight, raised at R-003 and again at R-004, falls; it should never have been raised the second time, because the repair had shipped on 2026-08-05.** Filed **I-142, MEDIUM.** |
| **R28** | **§5.4** (the point of reliance); **§19.3**; §11.6; §21 `success_criteria` | **THE HAIRCUT CARRIES CLASS (c) WHERE IT IS RELIED UPON, NOT ONLY WHERE IT IS DECLARED — AND THE GAP IS SIZED AT 2×.** `published_signal_haircut_applied = 0.50` has **zero consumers** and **no haircut computation exists anywhere** [measured]. **§19.3's order-20 composite is built from two multipliers that are not the same kind of object: the 3.3× I-050 correction is class (a) — `t_gate = min(t_NW, t_raw)` is *"the ONLY figure graded (E-8)"* [measured — `stats.py:153`] — and the 2× haircut is class (c).** The bar `evaluate_gate1` computes is `t_gate ≥ 3.0` on **un-haircut** net returns; the bar §4.6 sets is the equivalent of **6.0**. | **The Principal's instruction, discharged where he directed it.** **§19.3's expectation of PARK-WITH-TRIGGER does NOT move** — it was a judgment about what this payoff can deliver and it remains one. **What moves is the failure mode attached to it, and it moves against the firm: a second branch now exists that the document did not carry — if C5 is never ruled and no seat applies §4.6 by hand, this family can be reported PROCEED at half the Charter's bar.** A PARK that should have been a PARK is a correct outcome; **a PROCEED that should have been a PARK is the failure this firm exists to prevent.** Filed **I-143, MEDIUM**; put to C2 at **C13(i)**. |

**WHAT R-005 COSTS THIS FAMILY, STATED FIRST BECAUSE IT IS THE LESS FLATTERING HALF — AND FOR THE SECOND REVISION RUNNING IT MOVES IN BOTH DIRECTIONS.**

**Against the document:** **thirty-four of this family's sixty-one stated limits are enforced by nobody and nothing except audit and adversarial review**, and the document has been written in places as though a sealed field were an enforcing one. **That includes F-002 itself: the falsifier's four legs, its α, its 1,800-bar floor and its 1.3 × 10⁻⁴ joint false-survival rate live in a field whose only guarantee is that it is not the empty string.** And **the haircut gap runs permissive by exactly 2× at Gate 1's t-criterion**, at the hurdle §11.6 calls the largest this family faces.

**For the family, and this seat states it in the same breath rather than in a separate paragraph where it would read better:** **two limits this document says are unenforced turn out to be enforced.** The cost model is repaired, so every net number this family produces will mean something on the first run rather than after a blocking condition; and the trial budget is refused automatically per trial rather than *"by this seat and by nothing else."* **Both corrections were available on 2026-08-05 and 2026-07-29 respectively, and this document carried the stale statement through R-003 and R-004. The finding is not that the harness improved — it is that this seat did not check.**

**What was NOT done, and why, so the absence is legible:**

- **No seal, no registration, no registry write, no vault.** **C2, C3, C7, C8 and C11 remain open. R-005 clears none and creates no sixth.** `book/registry.db` must read 0/0 when this revision is put down, and it does.
- **No issue closed. I-034, I-022, I-045 and C1 are recorded as measured and routed to their owners.** Recording a measurement and closing an issue are different acts and this seat holds only the first.
- **No `harness/` file touched, no test run, no suite state reported. `test_h7` and `test_h8` were not approached** — they are Validation's queue and went live for this family at `n_inherited = 7`.
- **No `VALIDATION-*` document touched. No `book/` artifact touched.**
- **No declared menu edited. No selection moved. `N_conditioning` remains 7.**
- **No binding field value changed.** The payload is unchanged in every literal.
- **No number computed.** `4+4+8 = 16`, `5+11 = 16`, `20+7+34 = 61` — integer arithmetic on already-enumerated sets, of the same class as R-002's `109 − 86 = 23`.

---

## REVISION BLOCK — R-007 · 2026-08-12 · PRE-SEAL · **CONFORMANCE ONLY**

> **UNSEALED. `book/registry.db` reads 0 hypotheses / 0 trials. Trial budget ZERO.** One number is produced and the Principal instructed it: the §11.1 span, a read-only `SELECT` over `book/pit.db` and a subtraction of two calendar dates. **No market data was modelled, no return series was touched, no backtest ran, no `harness/` file was opened, no `VALIDATION-*` document was touched, no `book/` artifact was written, no test was run, `test_h7` / `test_h8` were not approached, and nothing was committed.**

**Authority:** dispatch **S3-D-014** · the Principal's instruction to measure §11.1's span rather than label it · the Principal's ratification of I-153's conformance, by his own act, pre-seal.
**Payload:** `research/REGISTRATION-PAYLOAD-PREREG-002.md` — **UNCHANGED. `trial_budget = 47`, `n_inherited = 7`, all sixteen literals as recorded. No binding field VALUE moves.** Three prose-field bodies receive conforming inserts by the R-004 mechanism.
**New artifact:** `research/REGISTRATION-PAYLOAD-DATED-CLAUSES-PREREG-002.md` — the `dated_clauses` rows, produced as a payload because `dated_clauses` does not exist and this seat cannot write rows.

| # | Clause changed | What changed | Why |
|---|---|---|---|
| **R37** | §11.1 in-sample row | **THE SPAN IS MEASURED AND R34's LABEL IS STRUCK AS UNEARNED. It is 6.571 years and it has not moved** — `[2020-01-01, 2026-07-28] = 2400 days = 6.5710 y` [measured 2026-08-12, read-only `SELECT` over `book/pit.db`; six primary-universe legs; `ingest_ceiling` zero rows; last `knowledge_time` 2026-07-29]. **R34 asserted the span grows with `C`. It grows with INGEST**, and none has occurred since 2026-07-29. At `C = 2026-08-12` the declared in-sample window runs **15 days past the last bar on disk.** The figure is **exact today, not understated**, and §10.4's 0.43-year margin is exact with it. | **The asymmetry doctrine's own prediction, confirmed against the seat that benefits.** R34 replaced a stale-favourable *figure* with a stale-favourable *label* and neither was measured. **This correction runs AGAINST the family — it removes a claimed hidden margin — which is what a genuine check on a favourable claim looks like.** Filed **I-176, MEDIUM.** |
| **R38** | §21 `forward_kill_condition`, after the C13(k) sentence | **I-153's CONFORMANCE IS RATIFIED BY THE PRINCIPAL, IN-FIELD, AND C13(k) IS NOT DISCHARGED BY IT.** The Principal conformed clause 5 to `C + 187 days` by his own act, pre-seal, with **zero outcome knowledge**, on the field's own declaration that *"the drafted date is not binding — the formula is."* His ruling, recorded verbatim: *"the committed quantity is the 187-day window; fixing it pre-seal with zero outcome knowledge is conforming a document to its own governing terms, not extending a test that is going badly. 'Absolute' meant absolute against results-based movement; it still is."* | **This seat's refusal to ratify its own favourable repair was correct routing and is the third such refusal.** It now stands ratified by the seat whose act it is. **And the insert says what the ratification does NOT do:** Validation holds I-153's **instance** inside C2 at row 3, the alternative — the drafted literal and a shortened window — is **live**, and **the seal does not proceed past it.** A Principal ratification of a routing is not a Validation ruling on an instance and this seat will not present it as one. |
| **R39** | §21 `model_prior_provenance` | **I-150's CARDINAL WAS STILL "SIX" INSIDE THE SEALED FIELD.** Conformed to **fourteen**. | **R29(b)'s lesson for the sixth time and in the same direction:** the cardinal was corrected in the prose that describes the payload and left standing in the payload. **The register at §12.2 of the memo says fourteen; the hashed string said six.** Filed **I-177, LOW-MEDIUM.** |
| **R40** | seal-readiness block | **REFRESHED. R-006's two-set separation carried intact. R-007 clears nothing and creates no new blocker.** | **Seal-blocking: C2 · C7 · C8 · C11. Verdict-blocking: C3 · C5 · C4 · C10.** |

**WHAT R-007 COSTS, AND FOR THE FOURTH REVISION RUNNING IT MOVES IN BOTH DIRECTIONS.**

**For the family:** nothing. **No source of death is removed and none is added.** R38 records a ratification the family already had the benefit of.

**Against the document, which is the half that matters:** **the one figure four revisions passed over, and which R34 labelled rather than measured, was labelled wrongly.** The span does not grow with the seal date and the margin R34 said was understated is exact. **And the dated-clause register the Principal ordered returns 10 of 24, not 24 of 24** — thirteen of the fourteen misses are clauses living in document prose that no registry field carries, which is E-25(3)'s named gap arriving with a number attached. **The register's larger finding is worse than its headline:** E-2 extracts **90** sites from this document's own binding fields, **72 of them dates that are not clauses**, **75 of them firing on the first invocation**, and **`evaluate_gate1` makes any nonzero exit INSUFFICIENT-DATA.** **This family cannot pass Gate 1 while its sealed prose fields carry their own revision history**, and the revision history is this seat's.

---

## REVISION BLOCK — R-006 · 2026-08-11 · PRE-SEAL

> **This document remains UNSEALED. `book/registry.db` holds 0 hypotheses, 0 trials and 1 event [measured — this session, read-only `SELECT COUNT(*)`]. Every change below was made before `open_hypothesis` was called and therefore before any result on this family existed to select on. P7 has not yet bitten. Trial budget for this revision was ZERO. NO NUMBER WAS COMPUTED: every harness fact is `[measured]` at a named file and line, every figure about this family is `[cited]` from a prior artifact, and the only arithmetic is `2 + 40 = 42`, `1 + 8 = 9`, `2 + 1 + 2 + 2 + 5 + 25 + 10 = 47` and `187 − 172 = 15` on already-declared integers. No `harness/` file was touched, no `VALIDATION-*` document was touched, no `book/` artifact was written, no test was run, no suite state is reported, and `test_h7` / `test_h8` were not approached.**

**Authority:** dispatch **S3-D-006** · **the Principal's ruling of 2026-08-11 on I-140**, verbatim: *"a family does not get downgraded because its paperwork didn't learn what its repository did"* · the Principal's ruling on §19.3 / I-143: *"the family may not be evaluated at Gate 1, and no PROCEED may be reported, until C5 is ruled"* · `STANDING-ORDER-002` §6 as widened to **all dated clauses**.
**Occasion:** **I-034 is CLOSED**, satisfied **2026-07-29** on commit `875874f`'s evidence, recorded 2026-08-11, **discovery credit R-005**. **Condition precedent C1 is DISCHARGED, not extended.**
**Reasoning memo:** `research/DIR-RESTATE-001-prereg002-mechanism.md` **§12** — the site roster, the house-rule-5 arithmetic, the C5 decomposition, and the full dated-clause sweep.
**Payload:** `research/REGISTRATION-PAYLOAD-PREREG-002.md` — **UNCHANGED. `trial_budget = 47`, `n_inherited = 7`, all sixteen literals as recorded.** Three prose-field bodies receive conforming inserts by the R-004 mechanism; the document is unsealed and a prose-field edit is a draft edit, not an amendment.

| # | Clause changed | What changed | Why |
|---|---|---|---|
| **R29** | §1 recommendation box (**two rows**); §12's R26 note; §12.3; §12.8 (two rows); §19 verdict; §19.2 (two cells); §20 **C1**; the seal-readiness block; **§21 `success_criteria`'s COST-STACK paragraph, `forward_kill_condition`'s condition-precedent sentence, and `falsifier`'s E2** | **C1 IS DISCHARGED AND I-034 IS CLOSED. EVERY SITE THAT SAID THE OPPOSITE IS CONFORMED — FOURTEEN OF THEM, NOT SIX.** The family's Gate 0 recommendation is now **ADMITTED, conditional on C3 and C11** — C1 is gone from the conditional. | **The Principal's ruling.** Satisfaction date **2026-07-29** (commit `875874f`, *"Ruling 003 implemented: carry accounting, 139/139. **Closes I-034**"*); recording date 2026-08-11; both stated, nothing backdated. **The residual is retained and NOT swept up with it: §12 defect (d) — no `CostModel` field can charge liquidation or venue-insolvency risk — stands as class (c), C-25, and is not a condition precedent because there is nothing to wait for.** |
| **R29(b)** | §21 `forward_kill_condition`; §21 `success_criteria`; §21 `falsifier` | **R-005 STRUCK THE CONDITION PRECEDENT WHERE A READER MEETS IT AND LEFT IT STANDING WHERE THE SEAL MEETS IT.** §14's prose was struck at R26. **The identical sentence — *"implemented by 2026-08-11; if unresolved by that date the family is ADMITTED-AS-EXPLORATORY only"* — survived un-struck inside `forward_kill_condition`**, corrected only by an R26 note roughly forty lines further down the same field. So did the whole pre-repair cost diagnosis inside `success_criteria`, ending *"NO NET NUMBER … IS ADMISSIBLE UNTIL C1 LANDS."* | **A field is hashed as ONE string.** A reader of the sealed value meets the downgrade before the correction. **This is I-105's doctrine inverted — *a control exists where the harness reads it, and nowhere else*, run backwards: a correction exists where the SEAL reads it, and nowhere else.** Finding it required reading the payload rather than the prose that describes the payload. |
| **R30** | §1 recommendation box (breakeven row); **new §15 step 3b**; §19.2 | **HOUSE RULE 5 COSTS BETWEEN 0 AND 42 TRIALS, NOT ONE, AND THE DOCUMENT NOW SAYS WHICH.** `carry_breakeven_bps_annual` takes a **callable** and evaluates it once at `bracket[0]`, once at `bracket[1]`, and once per bisection step — **42 evaluations at the shipped `iters = 40`** [measured — `carry.py:107, :113, :116–122`]. The harness's own sanctioned usage (T-18, `test_carry_accounting.py:580–592`) implements the callable as **a `run_backtest` call per shift**, and `run_backtest` logs a trial unconditionally (`engine.py:248`). **On the KILL path the cost is 0** — `t_lo < hurdle` returns at `:111–112` before evaluating anything else, and the breakeven of a family below the hurdle **is** 0.0 bps/yr by construction. **On the survive path this seat authorizes 9, at `iters = 8`, bracket unchanged, resolution 7.8 bps/yr.** | **I-140 and this dispatch both say "one trial." It is not one trial, and Stage 1's line items sum to exactly 47 with ZERO slack.** A seat following this document's own instruction would blow the budget the document was written to protect. **Two available shortcuts are named and refused: narrowing the bracket is the I-037 operation performed on the instrument built to avoid it (`carry_breakeven_bps_annual` returns its bracket ENDPOINT when the root lies outside — `:111–115`; `VALIDATION-SPEC-002` §1286 records it doing exactly that once already); reconstructing `net(δ)` arithmetically outside the engine costs zero trials and breaches A2.** Preference stated, not taken: fund the 9 from **Stage 2's contingent 32**. Put to C2 as **C13(j)**. Filed **I-151, MEDIUM.** |
| **R31** | §20 **C5** (blocking column and body); the seal-readiness block; §5.4; §19.3 | **C5 BECOMES A LOCK: BLOCKING ON GATE 1 EVALUATION AND ON ANY REPORTED VERDICT, ABSOLUTELY.** The family may be sealed, may be run, and may spend Stage 1 with C5 open. **It may not be evaluated at Gate 1, and no PROCEED may be reported, until C5 is ruled.** **And the ruling C5 needs is in three parts, only the first of which is Validation's:** (1) **the point of application — Validation's, final short of the Principal**, and the three readings are not equivalent: **haircutting the return series is a NO-OP**, because Sharpe, `t`, DSR, PBO, WFE, subperiod positivity and P&L concentration are **all invariant to a positive scalar**; only haircutting the *expected return* halves `t`; (2) **the ratification — the PRINCIPAL's**, because a ruling that moves the effective bar between 3.0 and 6.0 without touching `T_STAT_HURDLE = 3.0` is a §4 reserved act wearing an interpretation's clothes; (3) **the executor — or Part 1 changes nothing**: the ruling must carry **executor, cadence and artifact** or it is class (c) and I-143's permissive branch survives the ruling meant to close it. | **The Principal's reason, recorded because it sets the standard for findings of this class:** *"a path to half the Charter's bar existing quietly is exactly what the relabeling mandate existed to surface, and its first substantive yield gets a lock, not a footnote."* **The finding is stronger than "the haircut is unenforced": C5 is a choice between a 2× hurdle and nothing**, and §19.3's order-20 composite rests entirely on the branch nobody has ruled. **Escalated under house rule 7, not resolved here.** Filed **I-152, MEDIUM.** |
| **R32** | §21 `forward_kill_condition` (three date literals); §14 observation-date paragraph; §11.4 R3 table; §6.3; §10.5.2; §10.5.3 | **THE SECOND C1. `forward_kill_condition`'s CLAUSE 5 TERMINATES THIS FAMILY WITH CERTAINTY, AS SEALED.** The field's opening declares the observation date is **`C + 187 days`** and that *"the DRAFTED DATE IS NOT BINDING — the formula is."* **Clause 5 then reads *"if the computation is not performed ON 2027-01-31 for ANY reason … the family is killed by default."*** At any seal after 2026-07-28, `C + 187 days` falls **later** than 2027-01-31; on 2027-01-31 the computation will not have been performed **because it is not due**; **clause 5 fires. Registry TERMINATED, no further trials, no Gate 1 submission ever, automatic, not appealable.** The three `2027-01-31` literals in the field body are conformed to **`C + 187 days`** — the rule the same field's opening already governs by and which §15 step 8 already computes. | **Strictly worse than I-140's condition precedent, on two heads.** I-140 **downgraded**; this **terminates**. I-140 fired on a premise that *happened* to be false; **this fires on a premise that cannot be satisfied.** **A kill condition written to be undefeatable had become one that cannot be survived**, and P7 would have made it permanent. **THE REPAIR RUNS IN THE FAMILY'S FAVOUR AND IS DISCLOSED AT MAXIMUM VOLUME FOR THAT REASON:** a sponsor deleting a clause that terminates its own family is the shape of act this firm exists to distrust. **Put to C2 as C13(k) — Validation may refuse the conformance and require the literal sealed as drafted, in which case the family accepts a shortened window and this seat writes the KILL memo on the day.** Filed **I-153, HIGH.** |
| **R32(b)** | §14's observation-date paragraph | **§14's PROSE RULE AND §21's FIELD RULE ARE TWO DIFFERENT RULES, AND THE PROSE IS CONFORMED TO THE FIELD RATHER THAN THE REVERSE.** §14 read *"the date is fixed and does not move… if the seal slips, **the window shortens**."* The field reads *"fixed **at sealing** and ABSOLUTE thereafter."* **This seat will not present that as conformance: it is a change of meaning and it is stated as one.** | **R-004's payload rule governs the direction** — *"anywhere this document's prose and that payload could diverge, the payload is what gets passed to `open_hypothesis`"* — and the field's opening is the sentence that already anticipated the slip. **And §14's rule had a silent cost:** at a seal on 2026-08-12 its window is **172 days, 8% shorter**, against **KC-002 clause (b)'s unchanged 30-conditioning-day threshold, which was calibrated against 187 days** and against *"~184 daily bars and ~552 funding prints."* **A kill condition tightened by scheduling rather than by design.** |
| **R33** | §11.4 R3 table (**both rows**) | **R23 NAMED §11.4 AS A CHANGED CLAUSE AND NEVER REACHED IT.** `forward_window_start` still read **`2026-07-28` (= `C`; the seal is intended for today)** and `forward_kill_condition` still read **Observation date 2027-01-31, absolute** — **both struck in §21 at R-004 and both left standing here.** The parenthesis *"the seal is intended for today"* has been false since 2026-08-04, which is R23's own stated reason for striking the literal in §21. | **The fifth instance of `conforming-pass-did-not-reach-every-instance`** — R8(c), R22, R25, I-140, and now this — **and the first in which a revision row names the site it failed to reach.** A reader auditing R23 against its own clause list would tick §11.4 as done. Filed **I-154, MEDIUM.** |
| **R34** | §11.3 (three rows); §16; §17 rank 9; §22 row 6; §11.1 in-sample row | **EVERY REMAINING DATE COMPUTED OFF THE ABANDONED `C = 2026-07-28` IS RE-EXPRESSED AS A FORMULA.** Earliest Gate 1 becomes **`C + 12 months` / `C + ~27 months` / `C + 4 years`** in place of the literals 2027-07-28 / 2028-10-05 / 2030-07-28, which appear in **four** places between them. **And §11.1's in-sample span of 6.571 years is labelled as measured to 2026-07-28 and therefore an UNDERSTATEMENT at any later `C`** — the one stale date in this document that runs **for** the family, which is exactly why four revisions passed over it. | **The Principal's doctrine, applied where it was aimed:** *"a condition precedent with a date is a kill condition wearing different clothes, and nothing evaluates it."* **The sweep is at `DIR-RESTATE-001` §12.5: twenty-four dated clauses, fifteen with a premise false today, and NINETEEN evaluated by nothing at all.** Two are class (a) — P7's UTC-day check and the `PITStore` ingest ceiling. Three are class (b). **The remaining nineteen are enforced by a reader noticing.** |
| **R35** | §20 blocking column; the seal-readiness block | **THE BLOCKING SET IS WRITTEN AS TWO SETS, BECAUSE IT WAS ALWAYS TWO.** **Seal-blocking: C2 · C7 · C8 · C11.** **Verdict-blocking: C3 · C5**, and by §20's own column also **C4** (Gate 1 scheduling) and **C10** (Gate 1; met in substance, formal closure outstanding). **The directed six-item set `C2, C3, C5, C7, C8, C11` is the union minus C4 and C10, and this seat names the two it drops.** | **R-005's own block already conflated the two**, listing C3 — §20's *"Blocking on Gate 1, not on sealing"* — among *"the same five open and blocking"* seal conditions. **Merging two kinds of block into one list is the shape of error that produced I-140**, and a blocking set that quietly loses two members is the defect this dispatch exists to correct. |
| **R36** | §20.1 | **THE DATED SEAL COMMITMENT IS STRUCK AND REPLACED BY A CONDITION.** *"Realistic seal date: on or before sprint close, **2026-08-11**"* is **today**, and C2, C7, C8 and C11 are open. **A dated commitment nothing evaluates, which is false on the day it was written for, is D-14 of the sweep and is the sweep's own author's document.** Replaced by: **seal when C2, C7, C8 and C11 have cleared, and not before.** | **Retaining it would freeze, under P7, a schedule the document itself knows it missed** — and this seat is the one who wrote it. **The unflattering half is that R-006 found it by running a sweep it was ordered to run, not by remembering.** |

**WHAT R-006 COSTS THIS FAMILY, AND FOR THE THIRD REVISION RUNNING IT MOVES IN BOTH DIRECTIONS.**

**For the family — and this seat states it first only because it is short:** C1 is discharged rather than extended, the condition precedent does not fire, and the certain termination at R32 is removed pre-seal. **Three sources of death removed in one revision, every one of them clerical.**

**Against the document, which is the half that matters:** **fifteen of this document's twenty-four dated clauses carry a premise that is false today, and nineteen of the twenty-four are evaluated by nothing.** The document has been carrying a schedule it never reconciled to its own sequencing decision of 2026-08-04. **The mandatory house-rule-5 statistic costs between 9 and 42 trials, not the one this document and its own Issue Log entry both assert, and Stage 1 has zero slack.** **C5 is a choice between a 2× hurdle and a no-op**, and §19.3's most conservative pre-registered expectation rests entirely on the branch nobody has ruled. **And R-005's celebrated repair was made where readers look and not where the seal looks** — R29(b) — which required reading the payload rather than the prose about the payload to find.

**What was NOT done, and why, so the absence is legible:**

- **No seal, no registration, no registry write, no vault.** `book/registry.db` must read 0/0 when this revision is put down, and it does.
- **No trial. No number computed. No `harness/` file touched, no test run, no suite state reported.** `test_h7` / `test_h8` not approached.
- **No `VALIDATION-*` document touched. No `book/` artifact touched. No commit.**
- **No declared menu edited. No selection moved. `N_conditioning` remains 7.**
- **No binding field VALUE changed.** `trial_budget` = 47 and `n_inherited` = 7 are untouched. Three prose-field bodies receive conforming inserts.
- **No issue closed by this seat.** **I-034's closure is the Principal's act of 2026-08-11 and is recorded here, not performed here.**

---

## 0. Provenance — what was read, what was run, and what this seat did not do

**Read this session** [measured]: `FUND_CHARTER.md` Parts II (Seats 2, 7, 9, 10), III (§3.1–3.5), IV (§4.1–4.6), V (§5.1–5.4), VI (§6.6), VII (§7.2–7.8), Appendices C and D · `CLAUDE.md` · `.claude/agents/director-of-research.md` · `research/PREREG-001-forward-lag.md` **in full** · `research/DATA-INGEST-001-crypto-etf.md` **in full** · `VALIDATION-RULING-002` §3.4 (R1–R4) in full · `VALIDATION-ACCEPTANCE-001` §5 (P1–P8) and §6 (G1–G5) in full · `VALIDATION-RULING-001` §3–4 headings · **`VALIDATION-GATE0-001-forward-lag.md` §1.2–1.6 (C-001 and the E1–E5 conditions), §2 (C-002 capacity), §4.1.1 (the four F-001 defects), §4.3** · `logs/DECISION_RECORD.md` D-006, D-007, D-008, D-009 in full · `logs/ISSUE_LOG.md` I-011, I-019, I-023, I-024, I-025, I-026, I-027, I-028, **I-029, I-030, I-031, I-032, I-033** in full · `harness/castellan/{costs,engine,grid,gates,registry,loaders,data,holdout}.py`.

**Validation's Gate 0 ruling on PREREG-001 landed while this document was being drafted, and it changed it.** **I-029 — *"Falsifier F-001 passes pure noise ~31% of the time"* — is filed against this seat**, and the standard it sets is the standard F-002 must meet. **§5.5 is the audit of F-002 against all four of the F-001 defects, and two of them were live in this document's first draft and are repaired here rather than argued around.** I-030's ruling that *delay is strictly cheaper than sealing defective* likewise overturns the sequencing rationale this document originally carried; **§20 now adopts Validation's position against this seat's earlier one.**

**Ran** [measured]:

| What | Why it is not a trial |
|---|---|
| `castellan.stats.expected_max_sharpe` and `min_backtest_length_years` at candidate `N` | Closed-form functions of `N` and `SR`. They touch no market data and produce no backtest number. |
| `castellan.costs.CRYPTO_PERP_TAKER.per_side_cost` / `.carry_per_bar` / `.scaled` on scalar unit notionals | Arithmetic on the preset's own constants. No price series is involved. §12 is the result. |
| `SELECT source, symbol, field, COUNT(*), MIN(event_time), MAX(event_time)` on `book/pit.db` | **Row counts and calendar spans only.** No price was read into memory, no return computed, no correlation, no signal. Per instruction, and because computing one here would be an unlogged trial — the I-011 failure exactly. |

**Did not do:** no data fetched, no backtest run, no signal or return statistic computed on `pit.db`, no registry write, no vault seal, no git commit. Per instruction and per seat boundary.

**State of the world at the time of writing** [measured]:

| Fact | Value |
|---|---|
| Families in `book/registry.db` | **0** — `hypotheses` table empty |
| Trials logged | **0** |
| Sealed holdout vaults | **0** — `book/vaults/` contains only `.gitkeep` |
| `book/pit.db :: ingest_ceiling` | **0 rows** — no ceiling on any of the fourteen datasets |
| BTC/USDT, ETH/USDT spot daily close | **2,401 rows each**, `2020-01-01` → `2026-07-28`, **0 gaps** |
| SOL/USDT spot daily close | **2,178 rows**, `2020-08-11` → `2026-07-28`, **0 gaps** |
| BTC/USDT:USDT, ETH/USDT:USDT funding | **7,203 prints each**, `2020-01-01` → `2026-07-28T16:00Z`, 8h cadence, **0 gaps** |
| SOL/USDT:USDT funding | **6,508 prints**, `2020-09-13T16:00:00.004Z` → `2026-07-28T16:00Z`, **0 gaps** |
| **Perpetual *price* series (`binanceusdm` OHLCV)** | **ZERO ROWS. Not ingested.** See §8 — this is the family's one open data dependency. |
| ccxt OHLCV loader (`fetch_ccxt_ohlcv`) | **exists and is exercised** — the same function that produced the spot panel |

**The honest starting position, in one line:** this family has clean, gap-free, 6.57-year funding and spot history already on disk, no prior search to charge itself for, and exactly one missing series that an existing loader retrieves in a single session.

---

## 1. Recommendation box

| Field | Value |
|---|---|
| **Hypothesis** | The *unconditioned* delta-neutral long-spot / short-perp position is crypto **carry factor** exposure, which Charter §5.4 explicitly does not pay for. The claim under test is narrower: **de-scaling that position as the realized funding rate rises above its own trailing baseline produces positive alpha to the unconditioned position**, because the funding premium is compensation for a crowding-cascade tail that is worst precisely where funding is richest. |
| **Verdict sought** | **Gate 0 intake.** Director of Research recommends **ADMITTED** — not ADMITTED-AS-EXPLORATORY — ~~**conditional on C1, C3 and C11 (§20)**~~ **[R29 · 2026-08-11] conditional on C3 and C11 (§20). C1 IS DISCHARGED — I-034 CLOSED by the Principal 2026-08-11, satisfied 2026-07-29 on commit `875874f` (*"Ruling 003 implemented: carry accounting, 139/139. Closes I-034"*), discovery credit R-005.** The residual — §12 defect (d), no `CostModel` field for liquidation or venue-insolvency risk — **stands as class (c), C-25, and is NOT a condition precedent because there is nothing to wait for.**, and **recommends against sealing today (§20.1, adopting I-030 against this seat's own earlier position)**. This is a stronger recommendation than PREREG-001 received and §19.1 gives the arithmetic reason. |
| **Expected Sharpe net** | **Unknown. No forecast is offered and none may be inferred from this document.** No admissible number exists: `book/registry.db` is empty and nothing has been run. |
| **Proposed sizing** | **USD 250,000** intended initial allocation (§13). 12.5% of Pod B's $2M; **2.5% of the firm's $10M paper book.** |
| **Horizon** | Continuous. Daily rebalance with a turnover band. No event trigger, no holding-period cap. |
| **Conviction** | **Moderate on the mechanism; low on the conditioning claim; high on the falsifier's ability to settle it.** This seat's stated expectation (§19.3) is that the family produces a **KILL memo naming a successor**, and that the kill comes from bar granularity rather than from the market. |
| **Trial count `N` at seal** | ~~**`N_inherited` = 0** [measured — no prior search exists]. **`N_conditioning` = 6**, declared with menus at §7. **Declared floor `N` = 6.**~~ **[R19 · 2026-08-10] `n_inherited` = 7, REGISTERED, not declared.** No prior *external* search exists [measured]; the 7 is `N_conditioning` — the seven menu-declared pre-measurement choices K1–K7 — **sealed in the binding field built for exactly that quantity** rather than asserted in prose nothing reads. **Registry-enforced `N` = 7 + logged.** Declared ceiling **54** at Stage 1, **86** at full Stage 2. `predecessor_family = None`, so `family_stats` has no chain to sum and `InheritedCountDoubleCountError` cannot fire [measured]. **This is not the GATES.md §4.7.1 defect: the registry cannot compute `N_conditioning`, and §4.7.1 governs inheritance from a predecessor this family does not have.** |
| **Trial budget** | ~~**80** post-seal trials~~ ~~**[R8(c) · 2026-08-05] 79 post-seal trials**~~ **[R15 · 2026-08-06] 47 post-seal trials AUTHORIZED (Stage 1), declared ceiling `N` = 54; a further ≤ 32 DECLARED BUT NOT AUTHORIZED (Stage 2), unlocked only by a measured `ρ̂`, reaching the former 79 / ceiling 86 only at ρ̂ ≤ 0.034.** The budget is set against a **declared conservative planning `ρ_plan` = 0.10**, named at §10.5.1 before any measurement exists, because *"burning `N` the measured ceiling may disallow is the sponsor's risk to declare, not discover."* |
| **Absolute admissible ceiling `N`** **[R13 · 2026-08-06]** | ~~**110**~~ ~~**[R8 · 2026-08-05] 109**~~ **NOT A CONSTANT. `N_max = min(109, max_admissible_trials(span, SR_realized, ppy, vif = VIF_gate(ρ̂)))`, with `ρ̂` this family's net-return autocorrelation measured by the harness from logged trials at evaluation time.** `109` is `max_admissible_trials(6.571, 1.0, vif = 1.0)` and is an **UPPER BOUND that can only fall**, not a budget (§10.4.3, I-063). **The binding threshold for the R-002 ceiling of `N` = 86 is `ρ̂` ≤ 0.034, not 0.1** (§10.4.2) [cited — `VALIDATION-SPEC-002` §0.2, §7.1, §7.2; I-064]. |
| **Breakeven cost** (house rule 5) | ~~**Cannot be stated, and the reason is a defect not an omission.** `CRYPTO_PERP_TAKER` charges funding as a cost on **gross** notional, so on this family's delta-neutral pair it applies **−21.9%/yr** where the strategy **receives** +10.95%/yr [measured — §12]. The sign is inverted and the base doubled. **No net number from this family means anything until that is repaired.**~~ **[R26/R26(b) · 2026-08-10 — STRUCK. THE PREMISE IS FALSE AND HAS BEEN SINCE 2026-07-29.]** **I-034 / C1 IS IMPLEMENTED:** `CRYPTO_PERP_TAKER` carries **no funding term** — *"funding is a signed cash flow and is accrued in the engine from the realized `pit_funding_panel` series, never as a scalar rate here"* — `CRYPTO_SPOT_TAKER` exists (D-013 §1, Principal-authorized), `carry.py` supplies the sanctioned carry-stress path, and `scaled(m)` leaves carry bit-identical (T-16) [all measured — `harness/castellan/costs.py`, `carry.py`; `DATA-IMPL-004` §5–§6: *"All nineteen T-cases are implemented and pass"*]. **THE BREAKEVEN IS NOW UNSTATED RATHER THAN UNSTATEABLE, AND THE DIFFERENCE IS THE WHOLE POINT: it is unstated because computing it is a trial and R-005's budget is ZERO.** `carry.carry_breakeven_bps_annual` is the house-rule-5 instrument, it exists, and it is monotone in its shift by construction. ~~**One trial inside Stage 1's 47 discharges house rule 5 for this family.**~~ **[R30 · 2026-08-11 — STRUCK. IT IS NOT ONE TRIAL, AND THE FIGURE WAS THIS SEAT'S, REPEATED BY I-140 AND BY THE DISPATCH.]** `carry_breakeven_bps_annual` takes a **callable**, not a series, and evaluates it once at `bracket[0]` (`carry.py:107`), once at `bracket[1]` (`:113`), and **once per bisection step** (`:116–122`) — **42 evaluations at the shipped `iters = 40`**; the harness's own sanctioned usage (T-18, `test_carry_accounting.py:580–592`) makes each evaluation a **`run_backtest` call**, and `run_backtest` logs a trial unconditionally (`engine.py:248`) [all measured]. **The honest cost is a schedule, not a scalar: 0 trials on the KILL path** — `t_lo < hurdle` returns at `:111–112` before evaluating anything else, and the breakeven of a family below the hurdle **is** 0.0 bps/yr by construction, on a δ=0 series step 3 has already logged — **and 9 on the survive path at `iters = 8`, bracket `(0, 2000)` unchanged, resolution 7.8 bps/yr.** **This seat authorizes the 9 at new §15 step 3b, spendable only if F-002 survives in full, and records that §15's Stage 1 line items sum to exactly 47 with ZERO slack: the 9 must come from Stage 2's contingent 32 or from a Validation ruling that a monotone reporting statistic containing no selection does not deflate DSR.** Put to C2 as **C13(j)**. Filed **I-140, HIGH** (closed 2026-08-11) and **I-151, MEDIUM**. |
| **Falsifier decisiveness** (I-029) | **P(F-002 survives \| the conditioning is pure noise) ≈ 1.3 × 10⁻⁴**, against F-001's measured **31%** [cited — I-029]. **F-002 contains no `argmax` and no selection of any kind.** Nulls, α, and a minimum-sample leg are stated at §5.3; the audit against all four F-001 defects is §5.5, including **two that were live in this document's first draft and are repaired rather than argued around.** |

---

## 2. Thesis in three bullets

- **The claim.** Perpetual funding is the rental price of leverage, not a mispricing, and 11%/yr is roughly the fair price of the tail a carry supplier bears. Harvesting it at constant size therefore earns the crypto carry factor and nothing more. **The testable claim is that the price of the tail is not linear in the observable — that the marginal funding point beyond a threshold is *over*-compensated by cascade risk, so a position that shrinks into rich funding gives up less mean than it gives up tail, and the difference is alpha to the unconditioned position.**
- **Why it might persist.** The crowded trade is the *constant-size* carry. This family does not claim the crowd has missed the premium — it claims the crowd is wrong about how to **size** it, because the participants who supply the carry at scale are structurally the ones least able to de-scale (they are running it as a yield product against liabilities, not as a risk-managed sleeve). That is a narrower, weaker, and consequently more defensible claim than "the premium is free."
- **Why the firm's own rules may kill it anyway.** The strategy's risk materializes intraday — liquidation cascades, basis blowouts, margin calls — and `book/pit.db` holds **daily** bars. **A daily backtest of this family will look better than the family is, by an amount the daily data cannot measure.** §5 leg (ii) exists to catch that, §16 states what remains uncatchable, and §19.3 predicts this is where the family dies.

---

## 3. GATE 0 (1) — MECHANISM

*Charter §4.3(1): a written hypothesis stating the economic or structural mechanism — why this effect should exist, in terms of who is on the other side and why they accept the loss. "The data says so" is not a mechanism.*

### 3.1 What the Charter has already established, and which this section does not re-derive

Charter Seat 7 states the structural fact this family is built on [cited — `FUND_CHARTER.md` §II Seat 7]:

> *perpetual funding at the 0.01%/8h baseline is roughly **11% per year** [measured: 0.01% × 3 × 365 = 10.95%] against a structurally long perp position. Any long-perp strategy must clear that before it clears anything else. Conversely, funding is a documented carry source for structurally short-perp positioning — **with a fat left tail when funding inverts**.*

Appendix C sources the baseline and adds: funding positive **>92% of Q3 2025** [cited — BitMEX funding study, Q3 2025].

**The Charter has therefore already granted this family its premise and already named its trap in the same sentence.** This section's job is not to re-establish that funding is positive. It is to answer the two questions the Charter leaves open: *who pays, and why do they keep paying* — and then to explain why a premium that satisfies both is nevertheless **not an edge**, which is the argument that forces the hypothesis into its actual, narrower form.

### 3.2 Who is on the other side

| # | Population | Why they pay |
|---|---|---|
| **1** | **Leveraged directional retail buying leverage as a service.** | The perpetual swap is the cheapest and most accessible leveraged long in crypto: no expiry, no roll, no dated-contract basis to manage, high leverage available, and reachable by account types and jurisdictions that cannot access CME futures or prime brokerage. **Funding is the rental price of that leverage, not an error.** They keep paying for the same reason a credit-card revolver keeps paying: the alternative on offer is not a cheaper rate, it is not having the position. |
| **2** | **Structurally long allocators using perps as an index proxy.** | Funds, treasuries and offshore vehicles that want crypto exposure without self-custody, key management, or an audited wallet policy take it in perps. Funding is paid as a substitute for custody-and-operations cost, and it is paid knowingly. |
| **3** | **Hedgers of illiquid crypto exposure** — miners, token treasuries, locked or vesting positions. | These are **short** perp. They are not a source of the positive premium; **they are the reason funding inverts in drawdowns**, when their hedging demand spikes at the same moment leveraged longs are being liquidated. They are named here because they are the mechanism of the left tail, not of the carry. |

**This is a mechanism and not a data observation.** Populations 1 and 2 are paying a price for a service they are receiving. That is the strongest form a persistence argument can take, because it does not require anyone to be making a mistake.

### 3.3 The trap: a mechanism this good is a reason *not* to expect an edge

**A premium that persists because it is a fair price for a service is, by construction, not alpha.** If the answer to "why do they keep paying" is "because they are buying something," then the answer to "why has it not been arbitraged" is "it has been priced," and the supplier's expected return is the risk they bear. This seat's position, stated before any measurement:

> ~~**The ~11%/yr baseline is approximately the market-clearing price of three risks that a carry supplier genuinely bears**, and there is no prior reason to expect it to exceed them:~~
>
> **[R1 · 2026-08-04 · WITHDRAWN. The struck sentence is not supportable and this seat withdraws it rather than defending it.]** Binance's documented formula is `F = [P_avg + clamp(interest − P_avg, −0.05%, +0.05%)] / (8/N)` with `interest` fixed at **0.01% per 8h**, so that whenever the premium sits inside **[−4 bp, +6 bp]** the funding rate equals the interest rate **exactly, regardless of the premium's value** [cited — official, `DATA-VERIFY-001` §1.1]. Measured on the firm's own store: the in-band subset's mean funding is **0.986 bp (BTC)** and **1.114 bp (ETH)** — essentially exactly the 1.00 bp interest rate — while mean basis over the same sample is **negative** (−1.58 bp BTC, −0.95 bp ETH) [measured — `DATA-VERIFY-001` §5.2; `DATA-INGEST-002` §4]. **Roughly 35% of prints sit at the floor** [measured — `DATA-VERIFY-001` §5.2].
>
> **The ~11%/yr baseline is therefore an ADMINISTERED CONSTANT, not a market-clearing price.** It is set by the exchange and transferred from longs to shorts by contract rule on every day the premium falls inside a ±5 bp band, whether the market is crowded or empty. The market-determined component — the premium — averages **slightly negative** over this sample. **The firm has no basis for asserting that the administered rate is above, at, or below the price of the risks below, and this seat states that it does not know rather than filling the gap.**
>
> The three risks a carry supplier genuinely bears are unchanged, and they are real whatever the rate compensating them is:
>
> 1. **Venue insolvency.** The short-perp leg and its margin sit on the same exchange whose failure is a live base rate, not a hypothetical (FTX, November 2022) [cited — general market record; **not measured in this repository**].
> 2. **Liquidation and basis dislocation.** In a cascade the perp can trade far from spot for an extended interval. A delta-neutral pair is first-order flat to *spot*, but it is not flat to the **basis**, and the basis is where the loss arrives — while the spot collateral backing the short-perp margin is falling at the same time.
> 3. **Funding inversion in exactly the wrong state.** Funding turns negative in drawdowns, so the carry stops paying precisely in the periods when the position is losing on the basis. The two losses are positively correlated by construction.

**[R1 · 2026-08-04 · the conclusion survives the withdrawal, on weaker premises, and this is stated rather than glossed.]** The struck sentence was doing real work: it argued the unconditioned carry is not alpha *because it is fairly priced*. That argument is no longer available. **The conclusion does not depend on it.** Charter §5.4 classifies carry as Factor P&L **whether or not it is fairly priced**, so the unconditioned position decomposes to 100% factor and 0% idiosyncratic on the firm's own attribution scheme regardless of what the administered rate is worth. **An argument that rests on the firm's own classification rather than on an unverifiable equality is the stronger of the two**, and the family is better off having lost the weaker one. Recorded because a withdrawal that quietly leaves the conclusion standing without saying what now supports it is the shape of a later argument.

**Therefore the unconditioned carry is not admitted as the hypothesis, and Charter §5.4 is what forces the issue.** §5.4's attribution decomposition names **carry** explicitly as a *factor*:

```
├── Factor P&L  = Σ (exposure × factor return) → momentum, value, size, sector, carry
├── Idiosyncratic = residual                   → THE ONLY THING THE FIRM PAYS FOR
```

> **A strategy whose entire return is harvesting funding decomposes to 100% factor P&L and 0% idiosyncratic under the firm's own attribution scheme. It could pass every Gate 1 criterion and still score zero on the only line the firm pays for.** That is not a risk this family runs; it is a certainty about the unconditioned form, and it is why §5's falsifier is written against a benchmark rather than against zero.

### 3.4 The mechanism of the actual claim

If ~11%/yr is the fair price of the tail, the only way to earn something the market is not already paying for is to **bear less tail per unit of premium collected**. That is a claim about sizing, and it is testable.

**The specific asymmetry claimed.** ~~Funding is a direct observable of long-side positioning crowding~~ **[R2 · 2026-08-04]** **Funding is a *censored* observation of long-side positioning crowding** — it is high precisely when leveraged longs are numerous and levered, **but only outside the clamp band.** Cascade severity is convex in crowding: a liquidation cascade's depth depends on the stock of positions that must be force-closed, which grows faster than the funding rate that signals it. **The claim is that the funding premium is roughly linear in crowding while the tail is convex in it**, so beyond some level of funding the marginal premium no longer pays for the marginal tail.

> **R2 — THE CENSORING, AND WHY IT ARGUES FOR K1 RATHER THAN AGAINST IT.**
>
> **The precise statement.** Realized funding is a **censored** observation of the premium: censored to the interest rate whenever `P_avg ∈ [−4bp, +6bp]` [cited — official, `DATA-VERIFY-001` §1.1]. `DATA-VERIFY-001` §6.1 puts this as funding being *"less sensitive to genuine crowding"* inside the band; **censoring is the exact word and it carries a consequence the softer wording hides** — the trailing 30-day mean and standard deviation that K1 normalizes by are **moments of a censored series**, so `z(t)` is a z-score of a censored variable and both of its moments are biased relative to the premium's own. That is a stated property of the state variable, not a defect to be corrected, because **the strategy conditions on the cash flow it actually receives.**
>
> **Why the censoring strengthens the mechanism** [inferred — from the formula's structure; **not measured**, and labelled accordingly]. Because funding can depart from the floor **only** when the premium escapes the band, the state variable's "rich funding" state is **by construction** the state *"crowding has become severe enough to overwhelm the administered rate."* The conditioning therefore fires on exactly the event the mechanism theorises about, rather than on a continuous proxy for it. `DATA-VERIFY-001` §6.1 reaches the same conclusion by a different route — *"no change to K1 is indicated... if anything it is reinforced"* [cited] — and this seat agrees. **K1 is unchanged (§7.1) and this paragraph is the reason it survived a finding that looked at first like a reason to change it.**
>
> **What the censoring costs, stated in the same breath.** On the ~35% of prints pinned at the floor [measured — `DATA-VERIFY-001` §5.2], funding is **identically** the interest rate and carries **no** information about how rich or cheap the premium actually is. The state variable is a mixture with a point mass, and its entire informational content sits in the off-floor subset. §14.2 and §19.3 are revised for the consequence.

**Who is on the other side of *this* claim, and why they accept the loss.** The marginal supplier of carry at scale is running it as a **yield product** — a structured note, a "delta-neutral yield" vault, an exchange earn programme, a treasury overlay with a stated target return. Those vehicles have three properties that make de-scaling costly or impossible for them: they advertise a yield and lose subscriptions when they stop earning it; they de-scale into a redemption cycle rather than a risk signal; and their mandate is written in terms of notional deployed rather than risk taken. **They accept the tail because their liability structure will not let them step aside for it.** That is a structural constraint, not a mistake, and constraints of that kind are the most durable source of a persistent premium the firm can hope to find.

**What is explicitly not offered as mechanism.** *"Leveraged longs are impatient."* That sentence is a restatement of the observation, not an explanation, and this seat rejects it. It is named here because the dispatch asked whether the persistence question could be answered better than that; §3.2 and this section are the attempt, and §4 records what would falsify them.

---

## 4. Variant perception, and the persistence escape this family picks

*§7.2(4): what does the market believe, what do we believe, why does the mispricing persist?*

**What the market believes:** funding is a premium to be harvested, and more funding is better. **What we believe:** funding is a premium *and* a crowding gauge, and past some level the second meaning dominates the first.

**Why it would persist.** Three candidate escapes were considered and one is selected.

| Escape | Selected? | Reason |
|---|---|---|
| (a) **The premium is simply un-arbitraged** | **No.** | Rejected on its face. Cash-and-carry is the single most institutionalized trade in crypto. Claiming it is un-arbitraged would be the "nobody has looked" argument the Devil's Advocate correctly refuses [cited — REDTEAM-001 §B.3.1, applied here by analogy]. |
| (b) **Capital constraint** — not enough balance sheet supplies the carry | **No.** | This was true in 2019–2021 and is decreasingly true. An escape whose validity decays with market maturation is a trade with an expiry date, not a validated edge — the same objection PREREG-001 §4 raised against regulatory and settlement-friction escapes, and it applies with equal force here. |
| **(c) Mandate segmentation** — the marginal supplier of carry cannot de-scale | **Yes.** | It is the only escape that supports a durable edge, and it is falsifiable: it makes a specific claim about *who* supplies the carry and *what they are prevented from doing*. |

**What would falsify escape (c)** — recorded here because a persistence argument with no falsifier is a story:

> Evidence that the marginal carry supplier does de-scale — i.e. that aggregate short-perp open interest **falls** as funding rises above its trailing baseline, rather than rising or staying flat. If the supply side already contracts into rich funding, then the sizing behaviour this family claims is unoccupied is in fact occupied, and (c) is dead.

**Measurability of that falsifier, stated honestly.** Aggregate open interest is **not in `book/pit.db`** and **no loader exists for it** [measured — `castellan.loaders` exposes yfinance, ccxt OHLCV, ccxt funding, EDGAR, and nothing else]. `ccxt` exposes OI history on major venues [assumed — not verified this session]. **This is therefore a named, currently-unmeasured falsifier of the persistence claim, not a measured one, and it is listed at §20 as a non-blocking condition.** Recording it as unmeasured is the correct treatment; recording it as satisfied would be the defect.

---

## 5. GATE 0 (2) — THE FALSIFIER · **F-002**

*Charter §4.3(2) and house rule 2: the specific observable that means the hypothesis is wrong.*

**Design note, stated so the seat's judgment is auditable.** KC-002 (§14) is a *kill condition*: an economic verdict on a forward window, on a date. F-002 is a *falsifier*: a verdict on whether the structural claim was ever true. The Charter requires **both** and they are not substitutes. A carry strategy can make money for six months with no mechanism at all — that is the defining property of a short-tail payoff — so a kill condition alone would be actively misleading for this family. **F-002 is mine.**

### 5.1 The three return series F-002 is computed on

All produced by `castellan.run_backtest` against this family, all net of the full §4.6 cost stack as repaired per C1, all on the same daily UTC index over the full in-sample `[2020-01-01, C]`:

| Series | Definition |
|---|---|
| **`R_bench`** | The **unconditioned** benchmark. Delta-neutral long-spot / short-perp, **constant** notional `w ≡ 1.0`, equal-weight across the primary universe, rebalanced daily inside the turnover band. *This is the crypto carry factor as this family would actually trade it, and it is the thing the strategy must beat.* |
| **`R_strat`** | The **conditioned** strategy. Identical in every respect except that per-asset notional is scaled by `w(t)` per the declared state variable, direction, cap and deadband (§7, K1/K2). |
| **`R_bench_scaled`** | **The exposure-matched benchmark.** `R_bench` × `c`, where `c` = (time-average of `R_strat`'s gross exposure) ÷ (time-average of `R_bench`'s gross exposure), computed over the full in-sample. **A constant-notional position holding the same *average* size as the conditioned strategy.** §5.5(d) explains why this series is load-bearing and not a refinement. |

**Three backtest runs. Registered as `N = 3`.** *(`R_bench_scaled` is a constant rescaling of `R_bench` and could in principle be derived arithmetically rather than run. It is run anyway, and counted, because a derived series is a number produced outside the engine and A2 makes those inadmissible.)*

### 5.2 F-002, in full

> **The hypothesis is FALSIFIED — and the family is written up as a KILL memo — if ANY of the following four legs fires.**
>
> **(0) INSUFFICIENT SAMPLE — the qualifying floor.** Fewer than **1,800 qualifying daily bars** on the common primary-universe index. *Fires before any other leg is evaluated, and when it fires the verdict is **INSUFFICIENT-DATA, not survival.*** 1,800 is ~75% of the 2,398 bars the in-sample span implies at 365 bars/year [measured], so the floor is breached only by a material data failure. **This leg exists because I-029(c) is filed against this seat: a falsifier with no minimum observation count is a statistic with a decimal point on noise.**
>
> **(iii) NO PREMIUM TO CONDITION ON.** The annualized **net** return of `R_bench` over the full in-sample is **≤ 0**. There is nothing to size, on this venue, at this trade size, once both legs are charged. *Cheapest leg; requires only the benchmark run; **runs first**.* Kills the family root and branch.
>
> **(i) NO ALPHA TO THE FACTOR.** In the OLS regression `R_strat = α + β·R_bench + ε` over the full in-sample, the **Newey–West `t`-statistic on `α`, at a 21-bar lag truncation, is ≤ 3.0** — the firm's own multiple-testing hurdle (§4.2 `T_STAT_HURDLE`), applied to the residual rather than to the raw return. *Newey–West rather than OLS standard errors because a carry residual is autocorrelated by construction and an OLS `t` on it is inflated in a known direction; 21 bars is one calendar month, pre-committed.* The conditioning contributes nothing the constant-size position did not already have; the family is carry factor beta, which Charter §5.4 does not pay for.
>
> **(ii) NO TAIL REDUCTION PER UNIT OF EXPOSURE GIVEN UP.** The mean of `R_strat`'s **20 worst daily net returns** is not better (less negative) than the mean of **`R_bench_scaled`**'s 20 worst daily net returns by at least **25%**. **The comparison is against the exposure-matched benchmark, never against `R_bench`.** *The mechanism's entire content is tail reduction achieved by choosing **when** to be small, not by being smaller on average. If the tail is not reduced on an exposure-matched basis, the mechanism is wrong **even if leg (i) passes** — and an alpha with no accompanying tail reduction is an unexplained alpha in a family the wider market has searched heavily, which is a measurement finding rather than an edge.*

**No leg contains an `argmax`, a peak, a grid search, or any selection over candidates. Every threshold is a pre-committed constant with a stated basis and a stated null.**

### 5.3 The falsifier's constants, its nulls, and its stated α

**I-029(b) — *"no null distribution and no significance level… this is the root defect"* — is answered here explicitly rather than by assertion.** The rider at §7 applies to F-002's own constants as much as to the strategy's.

| Leg | Threshold | Basis of the threshold | **Null hypothesis** | **P(leg fails to fire \| null)** |
|---|---|---|---|---:|
| **(0)** | ≥ 1,800 bars | ~75% of the 2,398 bars the span implies [measured] | — (a data condition, not a test) | — |
| **(iii)** | `R_bench` net ann. return > 0 | Zero is the only non-arbitrary threshold available | **H₀: no funding premium net of costs**, i.e. true net drift ≤ 0 | **< 0.05** [inferred] — with a strictly negative cost drag, a zero-edge series' net mean is negative in expectation and the sample mean's sign is decided over ~2,398 observations |
| **(i)** | Newey–West `t(α) > 3.0` | Charter §4.2 `T_STAT_HURDLE`. Not invented here. | **H₀: α = 0** — the conditioning is noise. Test statistic asymptotically standard normal under H₀ | **α = 0.0013**, one-sided [measured — `1 − Φ(3.0)`] |
| **(ii)** | ≥ 25% tail improvement vs. **`R_bench_scaled`** | A declared materiality margin, so the leg neither fires nor spares on noise. Not derived; declared as a judgment. **20 days ≈ 0.83% of 2,398** [measured] — the conventional ~1% tail cut and the smallest window that is not a single-observation artifact | **H₀: the conditioning's timing carries no tail information**, i.e. `R_strat` is `R_bench_scaled` re-weighted independently of the tail | **≤ 0.10** [assumed — stated as an assumption, and §5.5(e) records how it becomes measured] |

> **JOINT FALSE-SURVIVAL RATE — the number I-029 demands and which PREREG-001 never stated.**
>
> **Under the null that the conditioning carries no information** — which is the null that matters, since the funding premium's existence is not in doubt (Charter Appendix C) and leg (iii) would therefore not fire:
>
> **[R7 · 2026-08-04 — this premise is upgraded from [cited] to [measured], and the upgrade cuts both ways.]** The premise *"the premium's existence is not in doubt"* rested on Charter Appendix C. It is now **measured on the firm's own store**: annualized mean funding is **BTC 11.86%, ETH 14.07%** [measured — `DATA-INGEST-002` §4, independently reproducing I-040]. **That strengthens the joint arithmetic's premise and simultaneously weakens leg (iii) as a falsifier.** Leg (iii) now tests, in substance, whether ~1,186 bps/yr of largely *administered* carry (§3.3, R1) exceeds ~24 bps of round-trip friction [cited — D-013 §4]. **It will almost certainly not fire, and this seat records now that its non-firing is worth nothing as evidence.** The joint false-survival arithmetic is unaffected because §5.3 already conditions on leg (iii) not firing; what changes is that **the family's real falsification burden sits entirely on legs (i) and (ii)**, and no artifact may present leg (iii)'s survival as a result.
>
> ```
> P(F-002 survives | conditioning is pure noise)  ≤  0.0013 × 0.10  ≈  1.3 × 10⁻⁴
> ```
>
> **Against F-001's measured 31%** [cited — I-029], **that is a factor of roughly 2,400.** The difference is structural and not a matter of tuning: **F-001's leading term is an `argmax` over a 73-candidate grid; F-002 contains no selection at all.**
>
> **Under the joint null that there is also no premium**, leg (iii) fires with probability > 0.95 on its own and the joint survival rate falls below `10⁻⁵`.
>
> **Stated honestly: the `≤ 0.10` on leg (ii) is [assumed], and it is the one term in this arithmetic that is not derived.** If Validation requires it measured before sealing, the route is §5.5(e) and this seat does not resist it.

### 5.4 The interaction with the R4(b) haircut, stated so it is not conflated later

F-002's leg (i) tests the **pre-haircut** `t(α)`. Gate 1's `t ≥ 3.0` applies to **net returns after** the §4.6 50% published-signal haircut, which this family accepts in full (§11.5). A 50% haircut on expected return halves the t-statistic without touching the standard error, so **clearing Gate 1's t-hurdle post-haircut requires a pre-haircut `t(α) ≈ 6.0`, twice F-002's bar** [inferred].

> ### **[R28 · 2026-08-10 · CLASS (c), CARRIED AT THE POINT OF RELIANCE AND NOT ONLY AT THE POINT OF DECLARATION.]**
>
> **THE `t(α) ≈ 6.0` ABOVE IS DERIVED FROM A NUMBER NO CODE PATH APPLIES.** `published_signal_haircut_applied = 0.50` has **zero consumers** and **no haircut computation exists anywhere in `gates.py`, `stats.py`, `engine.py` or `costs.py`** [measured — §10.11.1 field 15, class **(c)**]. §11.6 declares the acceptance; **this paragraph is where the acceptance is spent, and the class belongs here too.**
>
> **THE GAP HAS A SIZE AND IT IS EXACTLY 2×.** The bar `evaluate_gate1` will actually compute is **`t_gate ≥ 3.0` on un-haircut net returns.** The bar Charter §4.6 sets for this family is the equivalent of **`t_gate ≥ 6.0`.** **The difference is enforced by Validation applying §4.6 by hand, under a point of application (C5) that is still unruled** — an unspecified operation that is also not implemented.
>
> **WHAT THIS OPENS, STATED BECAUSE IT RUNS AGAINST THE FIRM.** §19.3's expectation of **PARK-WITH-TRIGGER** described one way to be wrong. **There is now a second: if C5 is never ruled and no seat applies §4.6 by hand, this family can be reported PROCEED at half the Charter's bar.** A PARK that should have been a PARK is a correct outcome. **A PROCEED that should have been a PARK is the failure this firm exists to prevent, and it is a named, reachable branch rather than an unexamined assumption.** Filed **I-143, MEDIUM**; put to C2's intake at **C13(i)**.
>
> **The composite at §19.3 is built from two multipliers that are not the same kind of object, and this document treated them as though they were:** the **3.3× I-050 correction is class (a)** — `t_gate = min(t_NW, t_raw)` is *"the ONLY figure graded (E-8)"* [measured — `stats.py:153`, `:221`; `gates.py:752`], implemented, shipped and unavoidable — and the **2× haircut is class (c)**.

**These are deliberately different bars and the difference is deliberate.** F-002 asks whether the family should continue to exist. Gate 1 asks whether it should receive capital. A family that clears the first and not the second is a legitimate outcome and is written up as a PARK-WITH-TRIGGER, not a PROCEED.

> ### **[R10 · 2026-08-05] WHAT THE I-050 ESTIMATOR CORRECTION CHANGES FOR THIS FAMILY'S GATE 1 SUBMISSION — recorded pre-seal, because a Gate 1 margin that narrows under a correction the firm has already approved is not a later surprise, it is a present fact.**
>
> **The correction, as approved.** The Gate 1 `t`-statistic is computed as `SR × √T`, which **assumes the return series is serially independent**. The firm holds one measured instance where that assumption fails badly — **daily funding autocorrelation ρ = 0.83, implying a `t` overstated by ≈3.3×** — and **the error runs in the permissive direction** [cited — `VALIDATION-RULING-004` §14, §14.1; I-050, approved by the Principal]. The estimator is being corrected to its own stated assumption in a parallel Validation dispatch. **`T_STAT_HURDLE = 3.0` DOES NOT MOVE.** This is an estimator repair, not a threshold change, and it requires no Charter amendment [cited — same].
>
> **Whether this family is exposed: yes, structurally, and the exposure is not a possibility but a property of the payoff.** The measured ρ = 0.83 is on the **funding rate series**, which is this family's revenue line and its state variable. A delta-neutral carry position's net return is **funding accrual plus a basis increment**, and funding accrual is the persistent term. **A carry residual is autocorrelated by construction** — this document already asserts exactly that at §5.2 leg (i), which is why leg (i) was written with a Newey–West `t` in the first place. **This seat therefore states pre-seal that this family's net return series is expected to carry material positive autocorrelation** [inferred — from the payoff's construction and from the measured ρ = 0.83 on the funding series; **NOT measured on this family's net returns, which would be a trial against a 0-trial registry**].
>
> **What moves, and what does not, clause by clause:**
>
> | Clause | Depends on the uncorrected statistic? | Consequence |
> |---|---|---|
> | **F-002 leg (i)** (§5.2) | **NO.** It specifies a **Newey–West `t` at 21-bar truncation**, pre-committed, *"because a carry residual is autocorrelated by construction and an OLS `t` on it is inflated in a known direction."* | **Unaffected.** The falsifier was already written to the corrected estimator, one document before the correction was ruled. §5.3's `α = 0.0013` and the joint false-survival rate of **1.3 × 10⁻⁴ stand unedited.** |
> | **F-002 legs (0), (ii), (iii)** | **NO.** A bar count, a ratio of tail means, and a sign test on an annualized return. No `t` appears. | Unaffected. |
> | **KC-002 clauses (a), (b), (c)** (§14) | **NO.** Three bare one-sided comparisons against thresholds — *"none has a null distribution, an alpha, or a power statement"* (§14.1). | **Unaffected. Stated explicitly so nobody re-opens the kill condition on the strength of an estimator change.** |
> | **DSR, PBO, WFE, subperiod positivity, P&L concentration, capacity, correlation** | **NO.** None is a `t`. | Unaffected. |
> | **Gate 1's `t ≥ 3.0` on net returns** (§4.4, §6.3) | **YES. This is the one that narrows, and it is the criterion §5.4 above is entirely about.** | **See below.** |
>
> **The arithmetic of the narrowing, bounded rather than computed.** §5.4 establishes that clearing Gate 1's `t ≥ 3.0` **post-haircut** requires roughly **2×** the pre-haircut figure, the 50% haircut halving expected return without touching the standard error. The I-050 correction multiplies the required *uncorrected* `t` by the inflation factor at the family's realized autocorrelation. **At the firm's one measured ρ of 0.83 that factor is ≈3.3** [cited — I-050]. Composing the two: **an uncorrected, pre-haircut `t` of order 3.0 × 2 × 3.3 ≈ 20** [inferred — arithmetic on two cited multipliers, stated as an order of magnitude and **not** as a forecast; **the family's own ρ is unmeasured and may be materially lower than 0.83, in which case the factor is materially smaller**].
>
> **This seat will not pretend that number is anything other than forbidding, and will not soften it by assuming the family's ρ is small.** *"Probably small"* is `[assumed]` doing the work of `[measured]` — Validation's own words on this point [cited — `VALIDATION-RULING-004` §13] — and this seat adopts them against its own family.
>
> **The honest reading, stated pre-seal:** **§11.6 already recorded the 50% haircut as *"the largest single hurdle this family faces."* It is no longer the largest.** The composition of the haircut with the corrected estimator is, and unlike the haircut it is **not** a policy this seat accepted for argumentative credit — it is arithmetic on a payoff shape this family chose. **The family's Gate 1 margin is narrower than R-001 recorded, before a single bar has been fitted, and the correct place for that fact is this document rather than a Validation Report in 2027.**
>
> **What this does NOT change.** It does not change the verdict at §19 (fund it, ~4 Sonnet units) — the case there is that a **verdict is reachable**, and F-002 and KC-002, which deliver the verdict, are both unaffected. It does not make the family exploratory. **It reprices what a Gate 1 PASS would take, and §19.3 is revised to say so.** A family that could clear F-002 and not Gate 1 was already pre-registered as a **PARK-WITH-TRIGGER** outcome (§5.4 above); **R10's effect is to make that the expected outcome conditional on surviving F-002, rather than one of two.**

**Live defect that makes this less certain than it reads.** §4.6 does not specify the **point of application** of the haircut — halve the return series, halve the Sharpe, or halve the alpha — and the three give materially different Gate 1 outcomes. **I-019 records that R4(a)/(b) have schema and no computation attached**, so nothing in the harness resolves it either. **This is escalated to Validation at Gate 0 intake as an interpretive question this seat does not own** (§20, C5).

### 5.5 F-002 audited against the four F-001 defects · **I-029, filed against this seat**

**I-029 is owned by the Director of Research and it is the correct owner.** F-001 was this seat's design, this seat asserted it "selects nothing from a menu and is registered as `N = 1`," and Validation demonstrated the assertion false. The obligation that creates is not to apologize but to show that the successor does not repeat it — **defect by defect, including the two that were live in this document's first draft.**

| I-029 defect in F-001 | Present in F-002? | Disposition |
|---|---|---|
| **(a) `argmax` over 73 lags asserted as `N = 1`; ~31% pure-noise survival** | **NO** | F-002 contains **no `argmax`, no grid, no peak, and no selection over candidates of any kind.** There is no lag dimension — the strategy holds both legs simultaneously and continuously, so there is nothing to time. Every statistic is a fixed functional of three pre-specified series. |
| **(b) No null distribution, no stated α — "the root defect"** | **WAS PRESENT. REPAIRED.** | The first draft of this document named thresholds and stated no null and no α — **the same defect, one document later.** §5.3 now states H₀ for every leg, the test statistic's distribution where one exists, the α, and the **joint false-survival rate of ≈1.3 × 10⁻⁴**. Leg (i) is additionally moved from an OLS `t` to a **Newey–West `t`**, because a carry residual is autocorrelated and an OLS `t` on it is inflated in a known direction — a second, independent route to the same over-survival that (b) describes. |
| **(c) No minimum qualifying-bar count** | **WAS PRESENT. REPAIRED.** | **Leg (0)** adds a **1,800-bar floor**, and it returns **INSUFFICIENT-DATA rather than survival** when breached. The distinction matters: a falsifier whose sample-size failure reads as "not falsified" is a falsifier that rewards missing data. |
| **(d) Leg (iii) of F-001 evaluates capture at the argmax of its own sample — biased toward the falsifier's own survival** | **NOT PRESENT IN THAT FORM. AN ANALOGUE WAS PRESENT AND IS REPAIRED.** | F-002 selects no exit and no lag. **But leg (ii) carried a structurally identical bias:** `R_strat` is a re-weighted `R_bench`, and **any rule that reduces average size mechanically improves the tail whether or not the mechanism is real.** Comparing `R_strat`'s tail to `R_bench`'s would therefore have been biased toward the falsifier's survival by construction — Validation's (d), transposed from a lag axis to a size axis. **The repair is `R_bench_scaled`** (§5.1): leg (ii) compares against a constant-notional benchmark holding the **same average exposure**, so any tail improvement must come from **when** the size was reduced and cannot come from **how much** on average. |
| *(minor) F-001's D1 clause is a percentage difference on a small integer index — undefined at zero, and 2 vs 3 is 50%* | **NO ANALOGUE** | F-002's thresholds are all on continuous quantities: an annualized return, a `t`-statistic, and a ratio of two tail means. None is a percentage of a small integer. |

**Two further disciplines adopted from Validation's C-001 conditions, which govern how F-002 may be *used* rather than how it is defined:**

- **E2 — computed once.** F-002 is evaluated **once**, on the first complete run of the three series ~~after C1 lands~~ **[R29 · 2026-08-11] under the repaired cost stack, C1 having landed 2026-07-29**. **There is no re-run "with the corrected costs," no second look, and no "we also checked."** ~~If C1's repair changes the cost stack after F-002 has been computed, that is a **new family**, not a re-computation~~ **[R29] The contingency this clause guarded against cannot now arise — the repair preceded the seal by a fortnight — and the clause is retained in the general form it always had: ANY change to the cost stack after F-002 has been computed makes the recomputation a NEW FAMILY, not a re-computation** — because a falsifier that may be re-run until it spares the family is not a falsifier. ~~*This is why §15 puts C1 at step 0 and F-002 at steps 2–3, and not the reverse.*~~ **[R29] §15 step 0 is DISCHARGED and the test plan starts at step 1; the ordering argument stands and no longer has a condition to order against.**
- **E3 — no forward search wearing a confirmation as a hat.** Validation's E3 names PREREG-001's 30 forward trials specifically. **This family's ≤25 forward trials (§10.5) are `N_forward`, they are logged as trials, and no reported result may be selected from among them.** KC-002 is computed on the sealed specification once, and §14.2 records what KC-002 does and does not establish.

**(e) How leg (ii)'s `≤ 0.10` becomes measured rather than assumed.** It is the one term in §5.3 that is [assumed]. It is measurable **before sealing and without touching market data**: a block-bootstrap or sign-randomization of the conditioning schedule against the *realized* `R_bench` series, holding average exposure fixed, gives the null distribution of leg (ii)'s statistic directly. **That is a computation on `pit.db` and is therefore a trial**, and this seat will not run it in this document. **It is offered to Validation as condition precedent C11**, at a cost of 1–2 trials against a budget of ~~80~~ **[R15 · 2026-08-06] 47 authorized (Stage 1), which is the authorization C11 runs against**, and this seat's recommendation is that Validation require it — because I-029's finding is that an unstated α is how a formality gets reported as a falsifier, and one assumed probability in an otherwise derived chain is exactly where that returns.

---

## 6. GATE 0 (3) — UNIVERSE, HORIZON, REBALANCE FREQUENCY, SUCCESS CRITERIA

*Stated before the first run, per §4.3(3).*

### 6.1 Universe

| Element | Specification |
|---|---|
| **Venue** | `binance` (spot) and `binanceusdm` (perpetual). **Single venue, both legs.** Declared as conditioning choice **K5** (§7). |
| **Primary universe** | **BTC/USDT and ETH/USDT** spot, paired against **BTC/USDT:USDT and ETH/USDT:USDT** perpetuals. Common span **2020-01-01 → `C`** = **6.571 years** [measured]. |
| ~~**Secondary, reported separately and never pooled**~~ **[R3 · 2026-08-04] SOL IS DROPPED FROM THE UNIVERSE ENTIRELY.** | ~~**SOL**, on its own span. SOL spot begins 2020-08-11 (5.96 yr) and SOL funding begins 2020-09-13 (5.87 yr) [measured]. Pooling SOL into the primary would truncate the panel to **5.87 years** and cut the admissible trial ceiling from **110 to 74** (§10.4) — a real cost paid for a third asset. SOL is reported with its own span, its own `N`, and its own verdict, following **R2**'s refusal to average windows of different character.~~ **There is no secondary universe. The universe is BTC and ETH, and nothing else is traded or reported as a universe member.** K4's selection moves **within its already-declared menu of 5**, from option (2) to option **(4) — "BTC+ETH only, SOL discarded entirely"** (§7.1). **Reason: I-045.** Binance changed SOLUSDT's settlement frequency and widened its funding clamp roughly **40× to ±2.00%** on **2022-11-09** [cited — official, `DATA-VERIFY-001` §3.2], confirmed independently by a measured cadence break (0 of 787 days with >3 prints before, 11 including the day itself after; **BTC control 0 and 0**) [measured — I-045, reconciling with `VALIDATION-RULING-003` §A2's independent count of 11 of 2,145 days] and by a measured **−1,690.34 bp** basis dislocation on the same date [measured — `DATA-INGEST-002` §4]. **SOL's funding series is generated by different formula parameters before and after that date, so K1's z-score does not denote the same operative state across the sample.** The two remedies that would have kept SOL are unavailable — the parameter history is unpublished and the vendor states it will not announce further changes [cited — official, `DATA-VERIFY-001` §3.2, §7(4)], and a break control's **closing** boundary would have to be chosen from the data. Full reasoning: `research/DIR-RESTATE-001-prereg002-mechanism.md` §3. |
| **What dropping SOL does and does not cost, recorded pre-seal** | **Does not cost the falsifier anything.** F-002 is computed on the **common primary-universe index** (§5.2 leg 0) — BTC and ETH. **No leg of F-002 ever read SOL**, so the tail realization on SOL's 2022-11-10 (`−0.17166` accrual on `−1.0` perp notional [measured — `VALIDATION-RULING-003` T-9]) was never inside the test. **Does cost this:** the primary universe's largest in-sample basis excursions are **−73.65 bp (BTC)** and **−102.95 bp (ETH)**, both 2020-03-12 [measured — `DATA-INGEST-002` §4] — roughly **an order of magnitude** milder than SOL's. **F-002 leg (ii) is therefore a tail test on a mild tail, and leg (ii) surviving is weaker evidence of tail reduction than the leg's construction implies.** Stated here rather than discovered at the result. Note also that SOL's own tail observation was **not usable as forward evidence in any case**: its magnitude required the ±2.00% cap then in force and could not occur under the parameters the contract runs on today [inferred, from cited — `DATA-VERIFY-001` §3.2]. |
| **Ruling 003's acceptance suite is unaffected, stated so this is not misread** | **T-9's fixture is over stored data, not over the traded universe** [cited — `VALIDATION-RULING-003` §4 T-9]. SOL's prints remain in `book/pit.db` and its perp OHLCV remains ingested [measured — `DATA-INGEST-002` §2]. **The test that guards against a cadence constant continues to run on the window that most needs guarding.** |
| **Unit of observation** | **The asset-day.** One daily UTC bar of one (spot, perp) pair. |
| **Position construction** | Per asset, per day: **long 1.0 unit spot notional, short `w(t)` units perp notional**, where `w(t) ∈ [0, w_max]` and `w(t) = 1.0` for the benchmark. Delta-neutral at `w = 1.0`. The position is **never long perp** — declared as conditioning choice **K2** (§7). |
| **Position notional** | `P_notional = USD 125,000` per asset (2 assets × $125,000 = $250,000 allocated, §13). Gross at `w = 1.0` is **$500,000** — two legs. |
| **Capacity screen** | Trailing-20-session median daily notional ≥ **20 × `P_notional` = USD 2,500,000** per leg, per asset, evaluated on a trailing window ending **strictly before** the day screened. **The instrument to measure this is already on disk** — the `volume` field of the spot panel — and arrives for the perp leg with the §15 step-1 ingest. *Unlike PREREG-001, capacity here is measurable with data the firm has* (contrast I-026). |
| **Regime cells** | Reported separately in every artifact: {funding positive, funding negative} × {trailing spot vol above / below its own median}. **All four cells are traded.** No cell is excluded — declared at **K3** (§7). Pooled figures never stand alone. |

### 6.2 Horizon and rebalance

| Element | Specification |
|---|---|
| Signal | `z(t)` = deviation of the trailing-24h realized funding rate from its own trailing **30-day** mean, in units of that window's standard deviation, computed from `event_time ≤ t` funding prints only. |
| Sizing rule | `w(t) = clip(1.0 − k · max(0, z(t) − d), 0, w_max)`, **with `k` = 0.5, `d` = 1.0, `w_max` = 1.0 [R41 · 2026-08-25 · NUMERIC LITERALS].** In words: **full size at or below one trailing standard deviation of excess funding, half size at two, flat at three** (`w` reaches 0 at `z = d + 1/k = 3.0`). **Size falls monotonically as funding gets rich relative to its own baseline; it never rises above the benchmark.** **[R42] And it is INERT below the baseline:** `max(0, z − d) = 0` for `z ≤ d`, so `w = 1.0` whenever funding is cheap or negative — roughly a quarter of in-sample days [cited — `REDTEAM-002` §2.1] — which is the regime §3.2, §3.3 and §7.4 name as where the left tail lives. **Disclosed, not redesigned (the Principal's ruling); K2 is unchanged.** |
| Entry / exit | Continuous. `run_backtest(execution_lag=1)`. The weight decided at bar `t`'s close earns returns from `t+1`. §4.6's minimum-one-bar rule is satisfied by the engine and is **not** waivable [measured — `SameBarFillError` is raised for `execution_lag < 1`]. |
| Rebalance | Daily, subject to a turnover band: no trade unless `|w_target − w_held| > band`. |
| `periods_per_year` | **365.** Crypto trades every calendar day; there are no session gaps on either leg. Matches the `CRYPTO_PERP_TAKER` preset. |
| Bar granularity | **Daily, UTC.** ~~Funding aggregated as the sum of the day's three 8h prints.~~ **[R4 · 2026-08-04 — THE CADENCE CONSTANT IS DELETED.]** Funding aggregated as the **exact arithmetic sum of all realized `funding_rate` prints whose `event_time` falls in the bar's window, left-open right-closed `(t−1, t]`, with NO assumed cadence, no mean, no annualization and no `periods_per_year`** — i.e. `pit_funding_panel` exactly as Validation specified it [cited — `VALIDATION-RULING-003` §3.2 and its alignment rule]. Declared as conditioning choice **K6** (§7), and §16 records what it forecloses. |
| **Why R4 is a defect repair and not a design change** | The struck clause asserted a **cadence constant that is measured false**: up to **12 prints in one day**, on **11 of 2,145 days** [measured — `VALIDATION-RULING-003` §A2]. Acceptance test **T-9** exists specifically to fail any implementation that multiplies by a fixed prints-per-day constant [cited — same, §4]. **The harness path was already correct; this document's prose was not.** Sealing the struck clause would have frozen a binding field whose text contradicts the sanctioned implementation, with no admissible way to reconcile them afterwards. **This repair is NOT confined to SOL and does not go away with SOL:** Binance states verbatim that *"there may be further adjustments to the funding rate settlement frequency... there will be no further announcement on such adjustments"* [cited — official, `DATA-VERIFY-001` §3.2], so a cadence change on **BTC or ETH inside the forward window** — the window KC-002 is computed over — is a live exposure that the struck clause would have mis-specified. **K7 (§7.1) governs what happens to the state variable when it occurs; R4 governs the arithmetic.** |
| Holding period | **None.** There is no target, no stop, and no maximum hold. A stop on a delta-neutral carry position would convert a mean-reverting basis excursion into a realized loss at the worst possible moment, which is the second-order effect Charter §5.2 names explicitly. Risk is controlled by **size**, which is what the hypothesis is about. |

**On the parameter values.** ~~`lookback = 30 days`, `d`, `k`, `band` and `w_max = 1.0` are~~ **[R41 · 2026-08-25 — THE SENTENCE ASSERTED A FIXING THAT DID NOT EXIST AND IS NOW TRUE.** Two of the five carried no value from 2026-07-28 until today, in a sentence claiming all five were fixed; `REDTEAM-002` §2.2 / **I-210** found it with one grep after seven revisions. **The values are: `lookback` = 30 days, `d` = 1.0, `k` = 0.5, `band` = 0.10, `w_max` = 1.0.** Derivation — from the mechanism and from estimator arithmetic on the declared 30-day lookback, never from the series — at `DIR-RESTATE-001` §14.2–§14.4.**]** These are **this seat's choices, made now, before any measurement, from no prior work** — and *now* means against a registry holding **0 hypotheses and 0 trials**, which is what makes the claim checkable rather than merely asserted. There is no inherited tuning to declare and no `N_inherited` to charge — a genuine difference from `forward-lag-001` and the single largest reason this family's arithmetic works (§10). Three of them go into the ±50% grid (§10.5); `w_max` does not, and §10.5 says why.

### 6.3 Success criteria — stated before the first run

| Level | Criterion |
|---|---|
| **F-002 survival** | All three legs of §5.2 fail to fire. |
| **KC-002 survival** | All four clauses of §14 fail to fire, at ~~2027-01-31~~ **[R32 · 2026-08-11] the observation date `C + 187 days`**. |
| **Gate 1** | Every criterion of Charter §4.4, unmodified, computed by `castellan.evaluate_gate1` against `book/registry.db`, with `backtest_years` passed **explicitly** as true calendar span and `oos_index` supplied (G1–G5 — without `oos_index` the length criterion is INSUFFICIENT-DATA, never PASS). No threshold relaxation is sought and none would be accepted. |
| **Plus two criteria §4.4 does not contain, which this seat imposes on itself** | **(1) Alpha to `R_bench`**, not raw Sharpe, is the reported headline. **(2) A skew and expected-shortfall line** on every artifact, because §4.4's battery is Sharpe-centric and structurally cannot see a short-tail payoff (§16). A family that hides behind a Sharpe its own payoff shape invalidates would be this seat's failure, not Validation's. |
| **What "success" is honestly worth** | §13. At $250,000 an excellent result is worth ~15–30 bp of firm NAV per year, unlevered. |

---

## 7. THE REGIME-CONDITIONING DECLARATION — the Principal's binding rider

> **Principal's rider:** *Regime-conditioning choices are declared at Gate 0 together with the menu they were chosen from.*

**Why this section exists and why it is the most important one in the document.** The forward-lag family is crippled because a single regime exclusion was made after the fact from an unrecorded menu, and the firm then had to reconstruct a factor of 10 by **[inferred]** guesswork (D-009 §B, I-027). `MinBTL(31,250)` at the Gate 1 Sharpe floor is **17.06 years** [measured] — a venue-history requirement no prediction market can meet, imposed not by the market but by the firm's own honest accounting of an unrecorded search.

**This family will not create that problem again.** Every conditioning choice in the design is enumerated below with the full menu it was selected from. Where the design conditions on nothing, it says so explicitly.

### 7.1 The ~~six~~ **[R5 · 2026-08-04] seven** conditioning choices, each with its menu

> **[R5] A note on how the menus themselves were edited, because the answer is: they were not.** K1's menu option (8) still reads *"cross-asset funding dispersion across BTC/ETH/SOL"* and K4's option (2) still names SOL. **Those strings are left verbatim.** A declared menu records the alternatives that were available *at the moment of choosing*, and retroactively editing one to match a later universe would destroy the only property that makes the menu worth declaring. **The menus are the historical record; the selections are the specification.** Only selections moved (K4), only one clause was repaired (K6), and only one menu was added (K7).

| # | Choice | **Selected** | Full menu enumerated | Menu size |
|---|---|---|---|---:|
| **K1** | **The state variable** — what position size is conditioned on | **Deviation of realized funding from its own trailing 30-day mean, in units of that window's standard deviation** | (1) raw funding level; **(2) funding deviation from own trailing mean ← SELECTED**; (3) funding **sign** only — the Charter's own framing; (4) trailing realized spot volatility; (5) spot trend / momentum state; (6) spot drawdown from trailing high; (7) basis level (perp − spot) independent of funding; (8) cross-asset funding dispersion across BTC/ETH/SOL; (9) calendar (day-of-week, funding-print-of-day); (10) **no conditioning at all** (= `R_bench`) | **10** |
| **K2** | **Direction of conditioning** | **De-scale into rich funding.** `w(t)` falls as `z(t)` rises; `w` never exceeds 1.0; the position is never long perp | **(1) de-scale at extremes ← SELECTED**; (2) up-scale at extremes (funding momentum); (3) sign-flip to long-perp when funding inverts | **3** |
| **K3** | **Period exclusions** | **NONE.** The full span `2020-01-01 → C` is used, **including** COVID-March-2020, May-2021, LUNA/UST May-2022, FTX November-2022, the 2022 bear, the 2024 spot-ETF approval, and every negative-funding episode | **(0) exclude nothing ← SELECTED**; (1) exclude COVID Mar-2020; (2) exclude May-2021; (3) exclude LUNA/UST; (4) exclude FTX; (5) exclude the 2022 bear; (6) exclude the pre-ETF period; (7) exclude the first *n* months after each listing as illiquid; (8) exclude negative-funding regimes | **9** |
| **K4** | **Asset universe** | ~~**BTC + ETH primary; SOL secondary, reported on its own span and never pooled**~~ **[R3 · 2026-08-04] BTC + ETH ONLY. SOL discarded entirely.** | (1) BTC only; ~~(2) BTC+ETH primary with SOL reported separately ← was selected~~; (3) BTC+ETH+SOL pooled on the common 5.87-yr span; **(4) BTC+ETH only, SOL discarded entirely ← SELECTED**; (5) a wider alt universe (not ingested, no loader run) | **5 — UNCHANGED** |
| **K5** | **Venue** | **`binance` / `binanceusdm` only** | **(1) binance ← SELECTED**; (2) coinbase; (3) bybit; (4) kraken; (5) cross-venue pooled or averaged | **5** |
| **K6** | **Bar granularity** | **Daily, UTC**, ~~funding aggregated as the sum of the day's three prints~~ **[R4 · 2026-08-04] funding aggregated as the exact arithmetic sum of realized prints in the bar's window `(t−1, t]`, no assumed cadence** | **(1) daily ← SELECTED**; (2) 8h (the funding-print cadence); (3) 1h; (4) 1m | **4 — UNCHANGED** |
| **K7** **[R5 · NEW · 2026-08-04]** | **Treatment of a documented funding-parameter change on a universe symbol** | **On any documented change to the funding formula, or to a universe symbol's per-contract funding parameters (settlement interval, clamp cap, or interest rate): that symbol's state variable `z(t)` is INSUFFICIENT-DATA for the declared trailing-baseline length — 30 days — beginning on the change date, during which the symbol is held at BENCHMARK WEIGHT `w = 1.0`; the change is filed to the Issue Log by Seat 9 and escalated to Validation.** | **(1) INSUFFICIENT-DATA for the trailing-baseline length, held at benchmark weight ← SELECTED**; (2) exclude the affected symbol's bars for that window; (3) exclude the affected symbol for the whole post-change period; (4) drop the affected symbol from the universe on the change date; (5) no special treatment — pool across the change | **5** |

### 7.1.1 **[R5 · 2026-08-04]** Why K7 exists, why option (1) is the selection, and the one in-sample trigger named by date

**Why the choice must exist at all.** Binance states verbatim that *"there may be further adjustments to the funding rate settlement frequency... there will be no further announcement on such adjustments"* [cited — official, `DATA-VERIFY-001` §3.2]. This family's holdout classification is **FORWARD** (§11.2) and KC-002 is computed over `[C, C+187 days]` (§14). **A funding-parameter change on BTC or ETH inside that window is therefore a live possibility with no pre-registered treatment**, and any treatment invented afterwards is a post-seal conditioning choice — refused by P3, and pursuable only as a successor family at the §7.2 escalated `n_inherited`. ~~**Declaring the rule now costs 1; discovering the need for it later costs the menu size times the family's final trial count.**~~ **[R9 · 2026-08-05] Declaring the rule now costs 1; discovering the need for it later costs the LINE — the escalated registration is refused by the harness today (I-053) and §7.2's replacement makes the hard stop the sealed behaviour.** The incentive this paragraph describes therefore points the same way and points harder. That is the §7.2 incentive working as designed, and this seat is paying the cheap side of it deliberately.

**Four properties that make option (1) a defensible selection rather than merely a selection:**

1. **No free parameter.** The window length is the **already-declared 30-day K1 lookback** (§6.2), not a new number. It is exactly the interval over which the trailing baseline mixes two generating processes, so it is *derived* from a field already in this document rather than chosen. **This is the specific respect in which K7 differs from the break control this seat rejected** — that construction needed a *closing* boundary the record does not contain (`DIR-RESTATE-001` §3.2).
2. **It excludes nothing, so K3 survives intact.** K3 remains **"exclude nothing."** The bars are traded, the returns are counted, the costs are charged; only the **conditioning input** is declared unavailable. Options (2), (3) and (4) would each have forced a change to K3 and were rejected partly for that.
3. **The default is the conservative direction.** Holding `w = 1.0` reverts to the benchmark, so the family **forgoes** any claimed benefit over the affected interval rather than claiming one computed on a corrupted input. A rule whose failure mode flatters the strategy would not be worth having.
4. **The trigger is mechanical, not interpretive.** "A documented change to the formula or to per-contract parameters" is an observable. *"A change that materially alters the generating process"* would require a judgment at run time, which is a researcher degree of freedom wearing a rule's clothing. **Mechanical and slightly over-inclusive is the correct trade in a pre-registration**, and the over-inclusion costs conditioning days in the conservative direction.

> **THE ONE KNOWN IN-SAMPLE TRIGGER, NAMED BY DATE NOW SO NO DISCRETION EXISTS AT RUN TIME.**
>
> **2025-09-18.** Binance changed the funding formula firm-wide on that date, introducing the `/(8/N)` divisor [cited — official, `DATA-VERIFY-001` §3.1, source 3]. Its arithmetic effect on BTC and ETH is **nil** while both remain on the 8-hour default, since `8/8 = 1` [cited — same]. **Under a mechanical trigger it fires regardless, and this seat declares that it does: BTC and ETH carry `z(t)` = INSUFFICIENT-DATA and `w = 1.0` for the 30 days from 2025-09-18.**
>
> **Naming it pre-seal is the whole point.** A rule that fires only on events nobody has yet identified invites a run-time argument about whether it fires. This one has its single known in-sample instance written into the sealed text, dated, with its arithmetic effect conceded to be nil and the rule applied anyway.
>
> ~~**What is not yet known, and is a blocking pre-seal check (§20, C12):** whether BTC or ETH carries any *other* cadence departure inside the sample. I-045 measures a BTC control at **0 days with >3 prints, before and after** [measured], which is decisive for BTC in the *shortening* direction only — a cadence **lengthening** (fewer than 3 prints/day) would not be caught by that test, and **ETH was not the control and has not been measured at all.** Sealing K7 while asserting that the primary universe has no other in-sample break would be the I-045 defect committed a second time in its own remedy.~~
>
> **[R12 · 2026-08-05 · C12 IS DISCHARGED — AND THE DISCHARGE IS NARROWER THAN THE PREMISE IT WAS PROTECTING, WHICH IS THE PART WORTH READING.]**
>
> **What was measured** [measured — `research/DATA-VERIFY-002-cadence-homogeneity.md` §3–§4, Seat 9, via `PITStore.asof` on `field='funding_rate'`]: **BTC and ETH carry exactly three funding prints on every one of 2,401 calendar days each — 4,802 symbol-days, 7,203 prints per symbol, `2,401 × 3 = 7,203` exactly, zero deviating days in EITHER direction, and a calendar span independently confirmed gap-free.** The `value_counts()` of prints-per-day returns a single bucket, `{3: 2401}`, for both symbols. **SOL's 11 deviating days serve as the working control that the instrument can in fact detect a break** [measured — I-045; `VALIDATION-RULING-003` §A2] — a null result from a test with no demonstrated positive is worth much less, and this one has its positive.
>
> **What that verifies, and what it does NOT.** It verifies the **CADENCE** dimension. **It does not verify the PARAMETER dimension, and the document's own named trigger is the proof:** **2025-09-18 — the firm-wide `/(8/N)` formula change — shows 3 prints on BTC and 3 on ETH** [measured — `DATA-VERIFY-002` §4, checked by name]. **A documented, dated, real change to the funding formula is INVISIBLE to a cadence sweep.** So is a clamp-cap change, an interest-rate change, or any parameter change that leaves the settlement interval alone — **which is the majority of the parameter space, and includes the exact change (the ±2.00% cap) that killed SOL's usability.**
>
> **The consequence, stated as the load-bearing sentence of this whole paragraph:** **K7 governs the parameter dimension BY DECLARATION, not by measurement.** Its trigger is *"a **documented** change to the formula or to per-contract parameters"* — an observable in the vendor's announcements, not in the firm's store. **C12 has confirmed the premise K7 was built on in the one dimension the firm can measure, and has thereby made visible that the other dimension has no instrument at all.** §17 risk #12's residual — *"an unnoticed change is still possible, since detection depends on Seat 9 observing it"* — is therefore **not** narrowed by C12's clean result, and any reading of `DATA-VERIFY-002` as *"the primary universe has no in-sample parameter break"* is a **misreading of a cadence measurement as a parameter measurement.** It is written here, in the sealed text's own section, so that the misreading is refused in advance rather than corrected later.
>
> **Also unchanged by the clean result:** the 2025-09-18 trigger **still fires** on BTC and ETH, exactly as declared above, with its arithmetic effect conceded to be nil and the rule applied anyway. `DATA-VERIFY-002` is evidence about K7's **premise**; it is not a substitute for K7 and it does not narrow K7's scope by one day [cited — `DATA-VERIFY-002` §6, which says the same in Seat 9's own words].

### 7.2 The `N` contribution, and the rule that makes it honest

> ~~**`N_conditioning` = 6. One per choice. Declared floor `N` at seal = 6, over an `N_inherited` of 0.**~~
>
> **[R5/R6 · 2026-08-04] `N_conditioning` = 7. One per choice, K1 through K7. Declared floor `N` at seal = 7, over an `N_inherited` of 0.**
>
> **K4's change is NOT a new contribution.** Its selection moved **within its already-declared menu of 5**, from option (2) to option (4), before any measurement and against a registry holding 0 families and 0 trials [measured]. The menu did not grow; nothing was searched over; **K4 continues to contribute 1.** The entire increment from 6 to 7 is **K7**, which is a genuinely new choice with a genuinely new menu.
>
> **This seat took the conservative reading deliberately.** A defensible case exists that K7 is a *data-validity rule* triggered by a vendor's documented act rather than a researcher's conditioning choice, and therefore contributes **0**. D-009 records that erring **low** on `N` is the sycophantic direction, so this seat declares 1 and invites Validation to rule it down rather than declaring 0 and inviting Validation to rule it up.

**The reasoning, stated so it can be attacked.** The multiple-testing denominator prices a **search**. A choice made *before any measurement*, from a menu declared *in the sealed pre-registration*, and *binding thereafter*, involves no search over results and contributes **1**, not the menu size. **The menu declaration is precisely what converts a factor of K into a factor of 1** — it is the pre-commitment made checkable.

**And the pre-commitment is enforced, not asserted:**

> ~~**BINDING ESCALATION RULE.** If any of K1–K6 is revised after any result on this family is seen, the revision is **not** an amendment to this family — P3 refuses it and logs `hypothesis_amendment_refused`. It requires a **successor family**, opened with `n_inherited ≥ (menu size of the revised choice) × (this family's final n_trials)`, and if more than one is revised, the **product** of the revised menu sizes. The successor inherits neither this family's schedule, nor its allocation, nor its narrative.~~
>
> **[R9 · 2026-08-05 · STRUCK AND REPLACED. The struck rule was UNEXECUTABLE and therefore decorative, and it was defective on two further heads this seat found while repairing the first. All three are stated before the replacement, because a rule replaced without naming what was wrong with it is a rule that gets re-broken.]**
>
> **Head (i) — SCOPE. The rule covered K1–K6 and did not cover K7.** R5 declared K7 and R6 discounted it to a contribution of **1**, on the same pre-commitment reasoning that discounts K1–K6. **The escalation rule is the entire mechanism that makes that discount conservative rather than convenient** (see the paragraph below, which says so in terms). A choice discounted by a rule it is not subject to is discounted for nothing. **This is a defect R-001 introduced in the same revision that created K7, inside the section whose job is to prevent exactly that.**
>
> **Head (ii) — QUANTITY. `n_inherited ≥ menu_size × chain_total` over-declares by one `chain_total`.** `TrialRegistry.family_stats` computes `n_trials = Σ n_inherited(chain, including self) + Σ logged(chain, including self)` and sums transitively across `predecessor_chain` [measured — `harness/castellan/registry.py`, `family_stats`]. The predecessor's own total is therefore **already inside** the successor's denominator by summation. Declaring `n_inherited = menu_size × chain_total` on top of it yields a successor denominator of `(menu_size + 1) × chain_total`, not `menu_size × chain_total`. **For a target denominator of `menu_size × chain_total`, the correct declaration is `n_inherited = (menu_size − 1) × chain_total`.** The error runs in the **conservative** direction — it over-charges the successor — which is why it survived R-001 unnoticed, and it is a defect regardless: a denominator nobody can reproduce from the rule that produced it is not a denominator. Filed **I-055**. *(The identical formula appears in `VALIDATION-RULING-004` **ML-17**, which cites this document's rule as its source [cited]; I-055 is addressed to Validation as well as to this seat for that reason.)*
>
> **Head (iii) — EXECUTABILITY, which is I-053 and is the head that makes the other two academic.** `open_hypothesis` raises `InheritedCountDoubleCountError` whenever a successor declares `n_inherited ≥ chain_total` [measured — `registry.py`, the `chain_total > 0 and n_inherited >= chain_total` guard]. **Both the struck form and the corrected form of head (ii) exceed `chain_total` for every menu size ≥ 2**, and K1–K7's menu sizes are 10, 3, 9, 5, 5, 4, 5 — **every one of them ≥ 3**. The rule the firm wrote could not be executed against the registry the firm built, on any of its seven choices, ever. **The guard is not wrong**; its docstring states the design intent — *"A genuine new search larger than the entire predecessor chain is a Validation escalation, not a silent registration"* [cited — `registry.py`]. **What is missing is the continuation: there is no argument, event, or authorized route by which Validation, having adjudicated the escalation, can then permit the registration** [cited — I-053].
>
> ### THE REPLACEMENT — BINDING, AND EXECUTABLE BY THE HARNESS AS IT STANDS TODAY
>
> **If any of K1–K7 is revised after any result on this family is seen**, the revision is **not** an amendment to this family — P3 refuses it and logs `hypothesis_amendment_refused` [measured]. The sanctioned continuation is a **successor family** under `predecessor_family`, opened with
>
> ```
> n_inherited  =  (menu size of the revised choice  −  1)  ×  (this family's final n_trials)
> ```
>
> — the product of `(menu size − 1)` across dimensions where more than one is revised — **so that the successor's `family_stats` denominator, which already sums this family's chain transitively, totals the intended `menu_size × chain_total`.** The successor inherits neither this family's schedule, nor its allocation, nor its narrative.
>
> **AND, BECAUSE THAT REGISTRATION IS REFUSED BY THE HARNESS TODAY, THE RULE'S OPERATIVE CONTENT UNTIL I-053 IS REPAIRED IS THIS:**
>
> > **A post-result revision of any of K1–K7 TERMINATES THE LINE.** The successor cannot be registered; an unregistered family cannot run a backtest (A2); and this document **forbids by name** the one move that would obtain a registration — **declaring a lower `n_inherited` than the escalation requires, in order to satisfy the guard.** That is the under-declaration I-053 names as *"the one that will be taken under schedule pressure"* [cited], it is Appendix B #2 (*"trial counts are lost"*), and no seat may take it on this family for any reason, including that the alternative is abandoning a line of work.
>
> **What this costs and what it buys, stated rather than left to be discovered.** It costs the family its only sanctioned route out of a revision: until the harness repair ships, revising a declared choice is not expensive, it is **fatal**. It buys the property that the rule now describes something the firm can actually do — refuse — rather than something it merely says. **A hard stop is a worse outcome for this family and a better rule than an escalation path that terminates in an exception nobody can clear.**
>
> **THE HARNESS CHANGE IS ESCALATED, NOT ASSUMED.** This seat does not own `registry.py` and does not repair it here. The repair required is I-053's: *an explicit Validation-authorized route — a keyword argument carrying a logged authorization event reference, or equivalent — that **preserves the raise by default** and permits registration only against a recorded authorization, logged as `n_inherited_escalation_authorized`*, against pre-authored acceptance test **ML-T-14**, which *"requires both halves: a change that merely removes the guard fails it"* [cited — I-053; `VALIDATION-RULING-004` §11.5]. **Owner: `head-of-data-infra`. This document does not wait on it and is not blocked by it** — the hard stop above is the sealed behaviour, and if the repair lands the escalated registration becomes available at `(menu size − 1) × chain_total` without any amendment to this family, because the sealed text already names that quantity.

**Why erring toward 1 is not the sycophantic direction here.** D-009 records that erring *low* on `N` is the sycophantic direction and erring *high* is conservative. The escalation rule is what makes 1 conservative rather than convenient: it is cheap only for as long as the choices are never touched, and it becomes ruinous the instant they are. **A researcher who intends to revise pays the full menu price with interest; a researcher who does not, pays 1.** That is the correct incentive and it is the only design this seat could find that gives one.

> **[R9 · 2026-08-05 — this paragraph was TRUE OF A RULE THAT COULD NOT BE EXECUTED, and that is worth saying plainly.]** Between R-001 and this revision, the sentence *"it becomes ruinous the instant they are"* was **false in operation**: the price it threatened could not be charged, because the registration that would have charged it was refused for every menu size ≥ 2 [measured — I-053]. **The discount to 1 was therefore, for that interval, resting on a deterrent that did not exist.** Under R9's replacement the sentence is true again and in a stronger form — the price is not ruinous, it is **terminal**, until the harness repair lands. **This is recorded rather than quietly fixed because the interesting fact is not that the rule is now sound; it is that a control this document called its most important one was inoperative and nobody, including its author, noticed until Validation read the harness against it.**

### 7.3 The counterfactual — the number that makes the rider's value concrete

Had K1–K6 been selected *after* seeing results, from these same menus, the honest `N` contribution would be their product:

```
10 × 3 × 9 × 5 × 5 × 4  =  27,000
```

> **[R5 · 2026-08-04] With K7 declared, the counterfactual product becomes `10 × 3 × 9 × 5 × 5 × 4 × 5 = 135,000`** [arithmetic on declared menu sizes; **no market data touched, no new statistic computed**]. **`MinBTL` is monotone increasing in `N`, so the measured `MinBTL(27,000, SR 1.0) = 16.79 years` below is now a LOWER BOUND on the counterfactual requirement.** No new number is computed and none is needed: the conclusion drawn from 16.79 years against 6.571 available was already fatal and is strictly more so. **This is the correct treatment under A2 — bound the consequence from a measured figure rather than produce an unregistered one.**

| Quantity at `N` = 27,000 | Value | Provenance |
|---|---|---|
| BLP&Z expected max Sharpe on pure noise | **4.10 · σ_SR** | [measured — `expected_max_sharpe(27000, 1.0)`] |
| **`MinBTL` at the Gate 1 Sharpe floor of 1.0** | **16.79 years** | [measured — `min_backtest_length_years(27000, 1.0, 365)`] |
| Available history | **6.571 years** | [measured] |

> **16.79 years against 6.571 available.** That is the same death sentence, to within three months, that `MinBTL(31,250) = 17.06` imposes on the forward-lag family. **The two families' data surfaces differ by an order of magnitude in quality and it would not have mattered.** Undeclared conditioning would have killed this one on arithmetic exactly as it killed that one.
>
> **This is what the Principal's rider is worth, in years: 16.79 → 6.14** (§10.4). It is not a documentation requirement. It is the difference between a family that can reach Gate 1 and one that cannot.

### 7.4 What this family conditions on that is **not** declared above — the honest sweep

Checked deliberately, because an undeclared conditioning is a defect and the failure mode is forgetting rather than concealing:

| Candidate conditioning | Present? |
|---|---|
| Excluded period, date range, or event window | **No.** K3 = none. |
| Post-event window (post-crash, post-listing, post-halving) | **No.** None used. |
| Volatility-state filter gating entry | **No.** Volatility appears only as a **reporting** cut (§6.1 regime cells), never as a filter on what is traded. Stated explicitly because a reporting cut and a filter are one edit apart. |
| Funding-sign filter (trade only when funding > 0) | **No**, and this is deliberate. The negative-funding regime is where the left tail lives; excluding it is the single most tempting and most dishonest exclusion available to this family. K3 forbids it. |
| Basis-level filter | **No.** Basis is not used as a state variable — that was K1 option (7) and it was not selected. |
| Winsorization, outlier removal, or return clipping | **No.** None applied anywhere, at any stage. A short-tail strategy that winsorizes its own tail is not measuring itself. |
| Survivorship selection in the universe | **No** — see §9.1. ~~BTC, ETH and SOL are three~~ **[R3]** **BTC and ETH are two** named continuously-listed instruments, not a screen output. |
| **[R5 · 2026-08-04]** Treatment of a vendor funding-parameter change | **YES, and it is now declared at K7** with its full menu of 5. It was **undeclared in the pre-R5 document, whose implicit selection was K7 option (5) — "no special treatment, pool across the change."** **I-045 is the finding that option (5) is wrong**, and this row records that the pre-R5 document made that choice silently. An implicit selection is exactly the defect §7 exists to prevent, and it was present in the section that prevents it. |

**Nothing else conditions. That is the full declaration.**

---

## 8. GATE 0 (4) — THE REQUIRED DATA EXISTS WITHIN PART III

*§4.3(4): the required data exists within Part III. No inadmissible dependencies.*

**Honest answer: all but one series exists, on disk, gap-free; the missing one is retrieved by a loader the firm has already run.**

| Requirement | Status | Provenance |
|---|---|---|
| Crypto exchange data available to the firm | Charter §3.2: *"Deep minute-level history. **Best data surface the firm has**"* | [cited] |
| BTC/ETH spot daily OHLCV, 2020-01-01 → 2026-07-28 | **PRESENT. 2,401 bars each. Zero gaps.** | [measured — `book/pit.db`] |
| SOL spot daily OHLCV, 2020-08-11 → 2026-07-28 | **PRESENT. 2,178 bars. Zero gaps.** | [measured] |
| BTC/ETH 8h funding prints, 2020-01-01 → 2026-07-28T16:00Z | **PRESENT. 7,203 prints each. Zero gaps.** | [measured] |
| SOL 8h funding prints, 2020-09-13 → 2026-07-28T16:00Z | **PRESENT. 6,508 prints. Zero gaps.** | [measured] |
| **Perpetual *price* series (`binanceusdm` OHLCV)** | **ABSENT. Zero rows.** | [measured — `book/pit.db` holds `binanceusdm` `funding_rate` only] |
| Loader for it | **EXISTS** — `fetch_ccxt_ohlcv(store, "binanceusdm", "BTC/USDT:USDT", timeframe="1d", ...)`, the same function that produced the spot panel | [measured — `castellan/loaders.py:103`] |
| Aggregate open interest (the §4 persistence falsifier) | **ABSENT, no loader.** | [measured] |
| Intraday bars on either leg | **ABSENT, not fetched.** Available in principle [cited — §3.2]; the volume is large. | [measured — DATA-INGEST-001 §5: "Daily bars only"] |

### 8.1 Why the missing perp price series is decision-relevant and not a footnote

**The strategy has two legs and the harness prices positions from a price panel.** Without `binanceusdm` OHLCV the firm cannot compute the perp leg's mark-to-market, cannot compute the **basis** (perp − spot), and therefore cannot compute the strategy's P&L at all. `run_backtest` takes a `(T, A)` price frame and differences it; there is no path by which a funding-rate series alone produces a position return.

**The tempting shortcut is inadmissible and is named here so it is not taken later.** One could assume `perp ≈ spot` and treat the position's entire return as accrued funding. **That assumption sets the basis to zero, and the basis is exactly the term this family's left tail lives in.** A backtest run on that assumption would produce a smooth, monotone, near-riskless equity curve with a spectacular Sharpe, and it would be measuring the assumption rather than the market. **It is inadmissible under this pre-registration and any result produced under it is void.**

**Cost to close: one Sonnet unit, one session.** The loader exists, the pagination pattern is written and exercised, and the ingest is bounded by the ceiling `HoldoutVault.seal()` writes at `C`. §15 step 1.

### 8.2 A mechanical gap in the sanctioned data path, flagged as small

`pit_adjusted_close` and `pit_price_panel` reconstruct an adjusted **close** from `close` + `split` + `dividend` [measured — `data.py:482`, `:526`]. **There is no sanctioned panel accessor for a `funding_rate` field.** Research must read funding through `PITStore.asof` / `rows_in_window` on `field='funding_rate'`.

**This seat's reading, offered for Validation to confirm or reject rather than assumed:** that path is admissible under A4, because A4's concern is *vendor pre-adjusted series*, and a funding print is never adjusted — it is final at settlement [cited — DATA-INGEST-001 §3 data dictionary: *"Historical funding prints are not revised; each print is final at settlement"*]. The two-timestamp rule still binds and every query filters `knowledge_time ≤ decision_time`. **Routed to Validation at intake (§20, C6) rather than decided here.**

### 8.3 Inadmissible dependencies

**None claimed.** This family requires no point-in-time fundamentals, no survivorship-free equity universe, no equity tick data, no borrow data, no paid news, and no brokerage connectivity. Every Part III hard wall in §3.3 is untouched. **It requires one series the firm does not have and a loader the firm has already run to get it.**

---

## 9. GATE 0 (5) — SURVIVORSHIP AND LOOK-AHEAD EXPOSURE, WITH MITIGATIONS NAMED

*§4.3(5).*

### 9.1 Survivorship

**The exposure is genuinely small here, and the reason is worth stating rather than asserting.** The universe is ~~**three named instruments**~~ **[R3 · 2026-08-04] two named instruments**, chosen because they are ~~the three~~ **among the three** the firm ingested, not produced by a screen over a candidate set. There is no delisting channel: BTC/USDT and ETH/USDT have traded continuously on Binance since before the sample opens. ~~and SOL since its listing date, which DATA-INGEST-001 §2 confirms is a **listing date and not a truncation** [cited].~~

> **[R3] The honest hazard the drop creates, named rather than left implicit.** Removing an asset from a universe *after* the firm has looked at its data is, in general, exactly the operation `N` accounting exists to price. **Three facts are what make it admissible here, and all three are checkable:** (i) the reason is a **documented vendor act dated 2022-11-09** [cited — official], not a property of SOL's returns; (ii) **no return statistic on SOL has ever been computed by this family** — the registry holds 0 trials [measured] — so there is no result the drop could have been selected on; (iii) the destination **was already on K4's declared menu** as option (4) before I-045 existed. **Had any of the three been false, the correct move would have been a successor family, not an edit.**

**Where survivorship does enter, and it is not zero:**

| # | Channel | Mitigation | Binding on |
|---|---|---|---|
| **S1** | **Asset selection is itself survivorship.** ~~BTC, ETH and SOL are three assets~~ **[R3 · 2026-08-04] BTC and ETH are two assets** that *are still here in 2026*. The population of 2020-vintage perpetual contracts includes many that delisted, and their funding histories would look worse. **[R3] The R3 drop makes this exposure worse, not better: a two-asset universe is a narrower survivorship claim than a three-asset one, and §17 risk #10 carries it.** | ~~**The claim is stated about these three instruments**~~ **[R3] The claim is stated about these two instruments** **and is not generalized to "crypto perpetuals."** Any generalization requires a wider universe and a delisted-contract enumeration, neither of which exists. Stated on the face of every artifact. | Director of Research |
| **S2** | **Venue survivorship.** Binance is a venue that did not fail. FTX-listed carry books did not survive to be backtested. **The strategy's single largest risk is the one the venue's survival selects out of the sample.** | **Named, not mitigable with this data.** It cannot be measured, it cannot be charged (§12(d)), and it is carried into §17 as risk #2 rather than dissolved. | Director of Research → CRO |
| **S3** | **Zero contracts are excluded for any reason.** No screen, no filter, no ambiguity handling. | K3 = none (§7). There is no removal rate to report because nothing is removed. | — |

**S2 is the honest one and this seat will not dress it up.** A carry strategy backtested on a surviving venue is a carry strategy backtested on the branch where the tail did not happen. **This is a Gate 0(5) exposure that is identified and whose mitigation is disclosure rather than correction**, and Validation should weigh it as such at intake.

### 9.2 Look-ahead

| Channel | Mitigation |
|---|---|
| **Filling on the signal bar** | `run_backtest(execution_lag=1)`. `execution_lag < 1` raises `SameBarFillError` [measured — `engine.py:30`]. The weight decided at bar `t`'s close earns returns from `t+1`. Not waivable. |
| **The funding print vs. the bar it is attributed to** | Funding posts at 00:00 / 08:00 / 16:00 UTC. The day's three prints are complete only at 16:00 UTC, after which no further print lands that calendar day [measured — max `event_time` on every funding series is `T16:00:00Z`]. **The day-`t` aggregate is therefore knowable at 16:00Z on day `t`, and it is consumed as a decision input at day `t`'s close, filling at `t+1`. That is a genuine 8-hour margin, not a boundary case.** Stated explicitly so nobody re-derives it. |
| **Trailing-window screens** | The 30-day funding baseline, the volatility cut, and the T-capacity screen are all evaluated on windows ending **strictly before** the day screened [cited — Ruling 001 §4.2 overriding constraint]. |
| **[R11 · 2026-08-05 · NEW] The CV embargo is shorter than this family's own feature lookback** | **NOT MITIGATED. A live channel, named at Gate 0 rather than discovered in a WFE number.** `purged_kfold_splits` embargoes `⌈0.01·T⌉` = **24 bars** on a 2,398-bar sample; **K1's lookback is 30 days**, so a training bar 25–30 bars after a test fold computes `z(t)` from **inside that fold**. `walk_forward_windows` applies **no purge and no embargo at all** [cited — `VALIDATION-RULING-004` §1(5), ML-18, §6.1; **I-051**]. **The 1% embargo is a Charter §4.2 constant (`EMBARGO_FRACTION = 0.01`) and is not this seat's to raise**; ML-18 rules it *"a floor rather than a target."* **Consequence for this family, stated plainly: its purged-CV and walk-forward results carry a leakage channel proportional to the excess of its 30-day lookback over the 24-bar embargo, in the permissive direction, until I-051 is repaired.** Owner `head-of-data-infra`; escalated, not absorbed. |
| **Vendor pre-adjusted series (A4)** | **Not applicable and this is a real advantage.** Neither leg has splits or dividends; nothing is back-adjusted; `auto_adjust` has no meaning for a crypto pair. **A4's hazard does not exist for this family**, in contrast with the eight ETFs in the same store. |
| **I-020 (`yfinance` UTC offset)** | **Does not touch this family.** I-020 is a `yfinance` defect; `parse_ccxt_ohlcv` and `parse_ccxt_funding` build timestamps from milliseconds-since-epoch, which are absolute [cited — DATA-INGEST-001 §4: *"it holds for ccxt, not for yfinance"*]. **No `yfinance` series is used here.** Stated so this is not read as a general clearance of I-020. |
| **`knowledge_time` on the backfill** | **Declared limitation** [cited — DATA-INGEST-001 §3]: every row backfilled this session carries `knowledge_time` = the ingestion instant. **This family may not claim to have tested point-in-time *knowledge* for dates before its ingest session.** It tests point-in-time *ordering*, which is what the hypothesis needs. Identical to PREREG-001's position and equally binding. |
| **I-011 — the search inside the researcher** | Not a look-ahead channel but a selection channel. **Handled at §7 by the menu declaration, which is the only instrument the firm has against it.** `N_inherited = 0` is honest about prior *harness* search; it is silent about model priors, and §7's ~~`N_conditioning = 6`~~ **[R6 · 2026-08-04] `N_conditioning = 7`** is this seat's attempt to put a countable floor under the part that can be counted. |

### 9.3 I-024 — clock alignment, and why it is **not** a live confound here

I-024 is HIGH severity and open, and PREREG-001 §8.3 devotes its longest section to it. **This family is materially less exposed and the reason is structural, not lucky:**

1. **Both legs trade on the same venue, 24/7, with no session calendar.** `binance` spot and `binanceusdm` perpetual never close. There is no overnight gap, no weekend gap, and no session boundary for a "lag" to hide in.
2. **Both legs' timestamps are epoch-milliseconds through `parse_ccxt_ohlcv`** — absolute instants with no local-time ambiguity to discard [cited — DATA-INGEST-001 §4].
3. **The strategy is not a lead-lag strategy.** It holds both legs simultaneously and continuously. There is no asynchrony for a confound to exploit, because nothing is being timed against anything.
4. **Zero gaps are measured on every series used** [measured — §0].

**The residual, named rather than waved away.** One anomaly is on the record: SOL's first funding print carries `event_time = 2020-09-13T16:00:00.004000+00:00` — a **4-millisecond** offset from the 8h grid [measured]. It is cosmetic at daily granularity and it is recorded here because an unexplained timestamp irregularity that goes unmentioned at pre-registration is the shape of a later argument. It is filed as an observation for Seat 9, not an issue.

---

## 10. GATE 0 (6) — TRIAL COUNTER, `N`, AND THE BUDGET ARITHMETIC

*§4.3(6) as amended by A2: the hypothesis family exists in `book/registry.db` and every backtest routes through `castellan.run_backtest`. A backtest number produced outside the engine is inadmissible in any document.*

### 10.1 The declaration

> ~~**`N_inherited` = 0.**~~ **[R19 · 2026-08-10 · THE FIELD IS SEALED AT 7.]** No prior work on this hypothesis exists in this firm or in the Principal's prior work, and **there is no unreconstructable EXTERNAL search to charge the family for** — that much is measured, not asserted: `book/registry.db` `hypotheses` is empty, `trials` is empty, and the hypothesis is originated by this seat in this document [measured]. **What changes is where `N_conditioning` is carried. `n_inherited = 7` is registered.**
>
> ~~**`N_conditioning` = 6**~~ **[R6 · 2026-08-04] `N_conditioning` = 7**, declared with full menus at §7 (K1–K7), each contributing 1 under the pre-commitment rule and each carrying the §7.2 escalation.
>
> ~~**Declared `N` floor at seal = 6.**~~ ~~**[R6] Declared `N` floor at seal = 7.**~~ **[R19 · 2026-08-10] `N` floor at seal = 7, AND IT IS NO LONGER A DECLARATION.** It is the sealed value of `n_inherited`, a binding field with **four consumers** in the harness: `family_stats.n_trials`; **DSR's `N`** (`gates.py:779`, `:788`); **MinBTL's `N`** (`gates.py:856`); and **`declared_ceiling_base = fam.n_inherited + sealed`** (`gates.py:565`), which is the base of `VALIDATION-SPEC-003` B-18's contingent-unlock arithmetic [all measured].
>
> > **WHY THE FIELD AND NOT THE PROSE — §10.5.2's OWN TABLE IS THE PROOF.** B-18 computes `allowed = clamp(N_max − declared_ceiling_base, 0, increment)`, and `VALIDATION-SPEC-003`'s `test_tbe_15` fixes `base, inc = 54, 32` and reproduces §10.5.2's four unlock rungs **exactly, without knowing this document exists** [cited]. **54 = 7 + 47.** At `n_inherited = 0` the base is 47, and the same mechanism admits **30 where §10.5.2 declares 23** (`ρ̂` ≈ 0.05) and **8 where it declares 1** (`ρ̂` ≈ 0.10) — **permissive, at exactly the two rungs where this family is in trouble, which is the direction the staged construction exists to close.** [`clamp` arithmetic on four already-cited `N_max` integers; no harness call made, no test run.] Filed **I-130, HIGH**. Full derivation at `DIR-RESTATE-001` §9.4.
> >
> > **What it costs, and it is a cost this seat takes deliberately.** Registry-enforced `N` at a full Stage 1 spend is **54, not 47**; at full Stage 2 **86, not 79**. **§10.3's 0.13-year I-027 residual is not mitigated — it is paid.** `MinBTL(86, SR 1.0) = 6.14 yr` against 6.571 available, margin 0.43 yr, **already measured and not re-derived** (§10.4). The change moves this family's own length criterion in the **tightening** direction and reduces its unused headroom below the absolute ceiling. **A declared floor that nothing reads is not conservatism; it is a number in a sentence.**
>
> **[R6] The multiple-testing count at the ceiling DOES NOT MOVE, and this is the whole `N` consequence of the 2026-08-04 revision:**
>
> ```
> BEFORE:  N_conditioning = 6   trial budget = 80   ceiling N = 86
> AFTER:   N_conditioning = 7   trial budget = 79   ceiling N = 86
> ```
>
> **[R15 · 2026-08-06] `N_conditioning` REMAINS 7 AND THE `N` FLOOR REMAINS 7. NEITHER MOVES UNDER R-003, AND NO SELECTION MOVED.** What moves is what may be **spent**:
>
> ```
> R-002:   N_conditioning = 7   trial budget = 79            ceiling N = 86
> R-003:   N_conditioning = 7   trial budget = 47 AUTHORIZED  ceiling N = 54  [Stage 1, at rho_plan = 0.10]
>                               + <= 32 NOT AUTHORIZED        ceiling N = 86  [Stage 2, only at rho_hat <= 0.034]
> ```
>
> **The ceiling itself is no longer an integer — it is the function at §10.4.1, and 86 and 54 are both readings of it at a stated `rho`.** §10.5.1 names the `rho` this budget is set against and §10.5.2 gives the two-stage construction and its unlock rule. **The convenience disclosed in the paragraph below concerned a −1; R-003's is a −32, taken against this family's interest, and the reasoning for it is at §10.5.2 rather than here.**
>
> K7 adds 1; striking the *"SOL on its own span"* diagnostic from §10.5 removes 1 of genuinely-removed work. **§10.4's measured `MinBTL(86, SR 1.0) = 6.14 years` against 6.571 available, with 0.43 years of margin, therefore stands unedited, and the 2026-08-04 revision produced no new number** — which is what A2 requires of a revision made against a registry holding 0 trials.
>
> **The convenience in that arithmetic is flagged rather than left to be noticed.** Reducing the budget by exactly 1 — rather than 0 or 2 — was chosen *in part* because it preserves an already-measured `MinBTL` and avoids computing a new one [stated as a judgment, not a derivation]. It is also independently justified: the struck line was one of five items sharing a ≤8 cap, so −1 is proportionate and −2 is not. **Both reasons are true and the first is the more convenient, which is why it is written down.** If Validation prefers the budget held at 80, ceiling `N` becomes 87 and `MinBTL(87, SR 1.0)` must be computed before sealing; it is **bounded by figures already measured at §10.4** in `[6.14, 6.574]` years, `MinBTL` being monotone increasing in `N` — **so the Gate 1 length criterion clears either way** and the margin lies between 0.00 and 0.43 years.

### 10.2 Why `N_inherited = 0` is the family's single most valuable property

PREREG-001 §9.4 is unambiguous: seeded at 31,250, `MinBTL` at the Gate 1 Sharpe floor is **17.06 years**, Polymarket does not have 17 years, and *"the family's binding risk is arithmetic, not absence of edge."* At 3,125 — the grid alone, no regime factor — it is still **12.72 years**. Both readings fatal.

**This family starts at 0, and the 6.571 years on disk are therefore usable rather than decorative.** That is not a claim that the hypothesis is better. It is a claim that a verdict on it is *reachable*, which is the property the forward-lag family lacks and which no amount of measurement can give it.

### 10.3 ~~I-027 — the harness still cannot seed `N`, and here it does not matter~~ **[R19(b) · 2026-08-10] I-027 IS CLOSED FOR THIS FAMILY — THE PREMISE OF THIS SECTION WAS TRUE WHEN WRITTEN AND IS NOW FALSE**

> **[R19(b) · 2026-08-10 · STRUCK. THE STRUCK SENTENCE IS A STATEMENT OF HARNESS FACT THAT HAS SINCE BECOME UNTRUE, AND SEALING IT WOULD FREEZE IT PERMANENTLY.]**

~~**[measured — `registry.py`, `open_hypothesis` signature]** There is no `n_inherited` parameter and no `n_inherited` column. `family_stats` computes `COUNT(*) FROM trials`. **I-027 is open and this family does not fix it.**~~

**[R19(b) · 2026-08-10] The column exists, the parameter exists, and the field is binding.** `n_inherited INTEGER NOT NULL DEFAULT 0` is declared in `SCHEMA`; `_migrate` ALTERs it onto pre-existing DBs — **`book/registry.db` is named in that method's own docstring as the DB that needs it**; `open_hypothesis`'s signature carries `n_inherited: int = 0`; `family_stats` computes `n_trials = n_inherited + n_logged` summed transitively; and it is the **sixteenth entry of `_BINDING_FIELDS`**, hashed into `prereg_sha256` and shadow-copied into `hypothesis_sealed` [all measured — `registry.py`, this session]. **I-018 / I-027 / C-001 §3.0 shipped the column this section says does not exist.**

**Why this is a repair and not a design change, and why it could not wait.** Sealing the struck sentence would freeze **a false statement about the harness** under P7, and would freeze with it the §21 disclosure line *"the 7-trial conditioning floor is declared and unenforced (I-027)"* — **which would then be false on the face of every Validation Report this family ever receives.** That is the R4 shape exactly: **the harness path was already correct and this document's prose was not.** Filed **I-131**. **R19 registers the 7; this section records that it was registrable all along and that this document had not noticed.**

**Its consequence here is small and quantified rather than assumed.** The undeliverable quantity is ~~`N_conditioning = 6`, against a trial budget of 80~~ ~~**[R6 · 2026-08-04] `N_conditioning` = 7, against a trial budget of 79**~~ **[R15 · 2026-08-06] `N_conditioning` = 7, against an AUTHORIZED trial budget of 47 (Stage 1). I-027's cost is unchanged in kind and SMALLER in size, because a smaller authorized budget means the undeclarable 7 sits against a smaller denominator's `MinBTL`, not a larger one — the bound below is therefore conservative and is retained rather than recomputed.**

| Reading | `N` | `MinBTL` at SR 1.0 | Provenance |
|---|---:|---:|---|
| ~~Registry as it will read (budget exhausted, 6 unseeded)~~ | ~~80~~ | ~~6.01 yr~~ | ~~[measured]~~ |
| ~~**[R6]** Registry as it will read (budget exhausted, **7** unseeded)~~ | ~~**79**~~ | ~~**≤ 6.01 yr**~~ | ~~**[bounded from measured]**~~ **[R19(c) · 2026-08-10 · STRUCK. THIS ROW DESCRIBES A REGISTRY STATE THAT WILL NOT OCCUR: the 7 is seeded, so there is no "unseeded" reading.** |
| ~~Honest (registry + declared conditioning)~~ **[R19(c)] THE ENFORCED READING — registry `n_inherited` 7 + logged** | **86** *(at full Stage 2; **54** at Stage 1)* | **6.14 yr** | [measured — unchanged] |
| ~~**Difference**~~ **[R19(c)] Difference between the two readings** | ~~6~~ ~~**7**~~ **0 — there is one reading now** | ~~**≤ 0.13 years**~~ **0** | **[R19(c)]** |

> ~~**I-027 costs this family** ~~0.13~~ **[R6] no more than 0.13** **years of required backtest length against 6.571 available.**~~ **[R19(c) · 2026-08-10] I-027 COSTS THIS FAMILY NOTHING, BECAUSE THE FAMILY PAYS THE 0.13 YEARS RATHER THAN AVOIDING THEM.** The residual this section quantified was the gap between the honest `N` (86) and the enforceable one (79). **R19 closes it by registering the 7, which raises the enforced `N` to the honest one and raises `MinBTL` with it** — `MinBTL(86, SR 1.0) = 6.14 yr` against 6.571 available, margin **0.43 yr** [measured, unchanged]. **The mitigation was never that the cost was small; it was that the harness could not charge it. It can, and this family elects to be charged.**
>
> **It cost the forward-lag family the difference between 17.06 years and a number in the tens**, and that contrast stands — but it stands now as a statement about a defect this firm has **fixed**, not one it is living with.
>
> **The disclosure obligation changes shape rather than disappearing.** ~~Every Validation Report on this family reads on its face: *`declared N = 86; registry-enforced N = <count>; the 7-trial conditioning floor is declared and unenforced (I-027)`.*~~ **[R19(b) · 2026-08-10 · STRUCK — this line would be FALSE in a sealed field once the 7 is registered, which is the sharpest possible illustration of why R19(b) could not wait.]** **The replacement line, binding on every artifact: *`registry N = n_inherited 7 (the K1–K7 conditioning floor, SEALED) + logged <count>; declared ceiling 54 at Stage 1, 86 at full Stage 2`.*** A control that has been connected is disclosed as connected; a report that still called it unenforced would be describing a document one revision out of date.

### 10.4 The admissible ceiling on `N` — ~~the number that sets the budget~~ **[R13 · 2026-08-06] the FUNCTION that sets the budget**

> **[R13 · 2026-08-06 · READ §10.4.1 BEFORE READING THE TABLE BELOW.]** **Everything in §10.4 as written through R-002 is the `ρ = 0` slice of a surface.** The integer 109 is not the ceiling; it is `max_admissible_trials(6.571, 1.0, vif = 1.0)` — the ceiling under an assumption the firm has now formally acknowledged its own data violates [cited — I-057]. **The ceiling this document seals is the function at §10.4.1, and it is below 109 at every ρ̂ > 0** [cited — `VALIDATION-SPEC-002` §6.2, whose measured table shows the ceiling falling below 109 at ρ̂ > 0.001]. The table and the R8 note below are **retained unedited** because they are the record of how the `VIF = 1` figure was reached and corrected, and because §10.4.3 turns on the fact that the intake ceiling is *necessarily* that figure.

`evaluate_gate1` computes `min_backtest_length_years(max(n_trials, 2), sr_ann, periods_per_year)` and requires `years_calendar ≥ max(4.0, MinBTL)` [measured — `gates.py`]. The binding case is the **Gate 1 Sharpe floor of 1.0**, because a lower realized Sharpe demands a longer history.

Against the primary universe's **6.571 years**:

| `N` | `MinBTL` at SR 1.0 | Verdict against 6.571 yr | Margin |
|---:|---:|---|---:|
| 6 | 1.69 yr | clears | 4.88 |
| 35 | 4.56 yr | clears | 2.01 |
| 80 | 6.01 yr | clears | 0.56 |
| **86** *(budget exhausted + conditioning)* | **6.14 yr** | **clears** | **0.43** |
| ~~110~~ **[R8 · 2026-08-05] 109** | ~~6.574 yr~~ **≤ 6.571 yr** | ~~**exactly at the span — zero margin**~~ **the true maximum; clears** | ~~0.00~~ **≥ 0.00** |
| **110** **[R8]** | **6.574 yr** | **FAILS — 0.003 yr past the span.** The verdict cell above read *"exactly at the span — zero margin"* and that was **wrong**: 6.574 > 6.571. | — |
| 125 | 6.80 yr | **FAILS** | — |

> **[R8 · 2026-08-05 — THE CEILING IS 109, NOT 110, AND THE ERROR WAS THIS DOCUMENT'S OWN READING OF ITS OWN MEASURED NUMBER.]**
>
> ~~**`N = 110` is the absolute ceiling.**~~ **`N` = 109 is the absolute ceiling** [cited — `VALIDATION-RULING-004` §2.2, which computes the maximum total `N` satisfying `MinBTL(N, 1.0) ≤ span` by bisection at 6.571 years and returns **109**, and §12, which records: *"The true maximum is 109 and I am recording the correction."*]. **`MinBTL(109)` is not computed here** — the ceiling is `[cited]`, not re-derived, because re-deriving it is a computation this seat's zero-trial budget does not authorize and because monotonicity plus the two figures already on this table settle it.
>
> **The correction was available inside this document before Validation made it.** `MinBTL(110) = 6.574` was already `[measured]` here, against **6.571** available. 6.574 > 6.571. **The row's verdict cell nevertheless read *"exactly at the span — zero margin."*** That is a mislabel of a measured number, not a measurement error, and it ran in the **permissive** direction — it admitted one trial the arithmetic refuses. Recorded in this form because a correction that arrives from outside and is absorbed without saying it could have been caught inside is how the same defect survives.
>
> Beyond 109, this family is arithmetically dead at the Gate 1 Sharpe floor and **no result can revive it** — exactly the position the forward-lag family occupies from its first day. Stated at pre-registration rather than discovered at Gate 1.
>
> **WHAT THIS DOES AND DOES NOT DO TO R6's FIGURES — the question the dispatch asks, answered plainly in both directions.**
>
> | Quantity | Before R8 | After R8 | Moves? |
> |---|---:|---:|---|
> | Declared ceiling `N` (budget 79 + conditioning 7) | 86 | **86** | **No** |
> | `MinBTL(86, SR 1.0)` | 6.14 yr | **6.14 yr** | **No** — 86 < 109, so nothing about the ceiling correction reaches it |
> | **Margin against 6.571 yr at the declared ceiling** | **0.43 yr** | **0.43 yr** | **NO. R6's margin does not shrink.** |
> | Absolute admissible ceiling | 110 | **109** | **Yes, by one trial** |
> | **Unused headroom between declared and absolute ceiling** | **24 trials** | **23 trials** | **Yes — this is the margin that shrinks** |
>
> **`109 − 86 = 23`** [arithmetic on two integers, one `[cited]` and one `[measured]`; no market data touched, no `castellan.stats` call made — the same treatment §7.3 gives its counterfactual product].
>
> **The finding, stated so it is neither buried nor inflated.** The margin the Gate 1 length criterion actually turns on — 0.43 years at `N` = 86 — **is untouched**, and this seat will not dress a one-trial change to a ceiling it does not intend to approach as though it were a change to the criterion it does intend to clear. **What genuinely shrank is the family's room to be wrong about its own budget:** the distance between what it declared and what the arithmetic permits is now 23 trials rather than 24, i.e. **one over-budget family-year of slack out of twenty-four**. If the trial budget is ever argued upward, the argument now has one trial less to work with, and §10.5's prohibition on expanding the budget on the strength of an early result is one trial more binding.
>
> ~~On the SOL-inclusive 5.87-year span the ceiling is **74**, which is why K4 puts SOL secondary [measured].~~ **[R3 · 2026-08-04] MOOT. SOL is not in the universe (§6.1, K4 option 4), so no SOL-inclusive span exists and the 74-trial ceiling never binds. The measured figure is left struck rather than deleted because it is part of the record of why K4 was originally selected as it was.**
>
> **The ceiling relaxes only on a higher realized Sharpe** — `MinBTL(110, 1.5) = 2.92 yr`, **[R8 · 2026-08-05]** a figure measured at the superseded 110 and retained unrecomputed because it is quoted only to make a qualitative point and `MinBTL` is monotone, so the value at 109 is no larger — but **the budget is not permitted to expand on that basis.** **[R8]** `VALIDATION-RULING-004` §2.2 puts the same point in the firm's most uncomfortable form: the admissible `N` at 6.571 years is **109 at SR 1.0 and 9,384 at SR 1.5** [cited], and *"a rule that lets a sponsor pick which column of that table applies to them is not a rule"* [cited — same, §13]. **This family fixes its column at SR 1.0 and does not move.** Expanding a trial budget because early results look good is the overfitting operation wearing a schedule's clothing.

### 10.4.1 **[R13 · 2026-08-06 · BINDING]** What §10.4 seals: a FUNCTION, not a constant

> **THE SEALED FORM, IN ONE LINE:**
>
> ```
> N_max  =  min( 109 ,  max_admissible_trials(span, SR_realized, ppy, vif = VIF_gate(ρ̂)) )
> ```
>
> where **`ρ̂` is this family's NET-return autocorrelation, measured by the harness from logged trials at evaluation time**, `VIF_gate` is `stats.family_variance_inflation` (R-6) computed from `TrialRegistry.trial_returns("funding-carry-conditioning-002")` plus the graded candidate series, and **`109` is not a constant that happens to bind — it is `max_admissible_trials(6.571, 1.0, vif = 1.0)`, and it is the first argument of a `min` that M-5 makes explicit in code precisely so this document and the source agree** [all cited — the Principal's ruling on I-057, verbatim at `VALIDATION-SPEC-002` §0.2; the construction at §7.1, M-4, M-5, R-6, V-1].

**Five properties of this form, each of which this seat is bound by rather than merely aware of:**

1. **It is recomputed at every `evaluate_gate1` and `evaluate_gate2` call, from the registry as it stands at that call.** Not cached, not carried forward from a prior evaluation, not read from a sealed field. The value used is printed on the report face [cited — V-1, M-10].
2. **Two evaluations of this family at different times may use different VIFs, and neither supersedes nor amends the other.** Each report states its own VIF, its own `n_series_used`, and its own registry `N` [cited — V-2].
3. **The declared `N` is graded against `N_max` through Charter §4.4's length criterion, not against 109 directly** [cited — `VALIDATION-SPEC-002` §7.1].
4. **`N > N_max` is a FAIL, not INSUFFICIENT-DATA.** Every input is known: `N` from the registry, the span from `oos_index`, the Sharpe from the graded series, the VIF from logged trials. The requirement is computed and unmet. One FAIL fails the Gate [cited — V-3].
5. **The ceiling can FALL between Gate 0 and Gate 1 and can never rise.** This seat, as sponsor, **cannot plan against the Gate 0 ceiling as a guarantee**, and §10.5 is now built on that fact rather than around it [cited — C-6, V-4].

> **WHY THIS IS ADMISSIBLE, PRESERVED RATHER THAN RE-ARGUED — AND WHY IT IS NOW DEMONSTRATED RATHER THAN SPECIFIED.**
>
> The Principal's own defence, which this document adopts and does not attempt to improve: the construction is **monotone-conservative — measurement can only tighten, never loosen — so it is not the I-029(d) operation; it is "the `min(t_NW, t_raw)` construction extended to `N`"** [cited — verbatim, `VALIDATION-SPEC-002` §0.2]. I-029(d) moves a constant in the permissive direction **after seeing an outcome**. This seals a function **in advance** whose every argument can only move the requirement in the tightening direction [cited — C-5].
>
> **That property is no longer a specification claim. Seat 9 has demonstrated it empirically** [measured — `DATA-IMPL-006` §2]:
>
> ```
> N_max:  max_admissible_trials(6.571, 1.0, 252, vif=measured) <= ...(vif=1.0)
>         rho in [-0.6, +0.8] step 0.05, 5 seeds each — 145 draws — 0 violations
> DSR:    deflated_sharpe_ratio_serial(r, N, sigma, vif=measured) <= deflated_sharpe_ratio(r, N, sigma)
>         rho in [-0.6, +0.8] step 0.1, 10 seeds, N in {2,100,5000}, sigma in {0.05,0.3} — 900 draws — 0 violations
> ```
>
> Both sweeps use a **real, measured VIF** from `variance_inflation` — never an adversarially injected one — which is the property that governs every live Gate 1 evaluation of this family. **It holds without exception.** This seat records the demonstration rather than the assurance, because the assurance is what the sponsor benefits from believing.
>
> **The construction is enforced at two independent layers and this family may not rely on either alone:** the estimator floors each series at `max(1.0, vif_hac, vif_ar1)` before aggregation (R-2, R-7), and the consumer takes `max(mb_iid, mb_iid·vif)` and `min(Φ(z/√vif), Φ(z))` (M-2, D-6) [cited — C-2].

### 10.4.2 **[R14 · 2026-08-06 · BINDING]** The threshold this family is written against is **ρ̂ = 0.034**, not 0.1

> **This supersedes the Principal's own stated figure, at Validation's derivation, and the supersession is countersigned.**

The Principal's I-057 ruling stated the consequence as *"if ρ̂ measures ≥ 0.1, the admissible ceiling falls below the declared `N` = 86"* [cited — `VALIDATION-SPEC-002` §0.2]. **That is true and it understates the tightness by roughly 3×** [all figures cited — `VALIDATION-SPEC-002` §7.2; I-064; **none re-derived here**]:

```
MinBTL(86, 1.0)                    =  6.1359 years
available span                     =  6.571 years          [cited — §8 of this document]
maximum admissible VIF             =  6.571 / 6.1359  =  1.0709
binding AR(1) ρ̂                    =  (1.0709 − 1)/(1.0709 + 1)  =  0.0342
```

> **THIS FAMILY SURVIVES GATE 1's LENGTH CRITERION AT ITS R-002 CEILING OF `N` = 86 ONLY IF ITS MEASURED NET-RETURN VIF IS AT MOST 1.071 — AN AR(1) ρ̂ OF 0.034. NOT 0.1. At ρ̂ = 0.1 the ceiling is 55 and this family is 31 trials over, not marginally over.** The margin is **0.435 years, 7.1% of the required length** [cited].

**Why this document adopts the tightening rather than the ruling that granted it.** Validation moved the trigger ~3× under the Principal's own §8 asymmetry — tightening is Validation's without a Principal act — **and filed it as I-064 rather than exercising it silently.** The Principal has countersigned: *"my number was a prediction, Validation's is a derivation."* **This is the asymmetry working as designed, and a sponsor who quoted the looser figure because it came from higher up would be the failure mode the asymmetry exists to prevent.** `test_mbs_13_prereg002_binding_rho_is_0034_not_0100` pins it as a green guard so it cannot drift back [cited — I-064; `DATA-IMPL-006` §1, which confirms that guard green].

**0.034 is the number every clause of this document is written against from R-003 forward.** Wherever `0.1` appears as a threshold in an artifact about this family, it is superseded. `0.10` appears once more in this document and **not as a threshold** — it is §10.5.1's declared *planning* `ρ`, which is a budgeting assumption and grades nothing.

### 10.4.3 **[R17 · 2026-08-06]** I-063 — the intake ceiling is computed at the permissive assumption, necessarily, and this document says so

**The ceiling quoted at Gate 0 intake — including the 109 in the table above and in §1 — is computed at `VIF = 1`.** At intake no trial has a return series, so `ρ̂` is unmeasurable at **exactly the moment the ceiling is quoted**. This is R-11's condition at the one moment it cannot be repaired [cited — I-063; V-6].

**It is structural and is not closeable. No construction can measure a family's serial dependence before it has produced a return series.** This document does not imply a ceiling it cannot yet justify, and V-6's mandatory render string is carried here verbatim as the form in which this family's intake ceiling must be read:

```
Admissible N at intake: <= 109 — computed assuming serial independence, which is
an assumption this firm's data violates. This ceiling is an UPPER BOUND that will be
re-evaluated at Gate 1 on the family's measured net-return autocorrelation and can only
fall. It is not a budget.
```

> **THE CONCRETE EXPOSURE, STATED AGAINST THIS FAMILY BY NAME.** This family could be ADMITTED at Gate 0 against a ceiling of 109, spend 86 trials against it, and fail Gate 1's length criterion because the measured ceiling is 55. **The trials could not be unspent** — reducing `N` is unavailable and `n_inherited` closes the successor route [cited — V-5]. **Neither the sponsor nor the machinery would be at fault, and that is precisely why the exposure has to be declared here rather than discovered there.** §10.5's two-stage budget is this document's answer to it, and it is the only answer available to a sponsor.
>
> **What this seat does NOT claim:** that the disclosure removes the exposure. It does not. I-063 is rated MEDIUM by Validation because it cannot produce a wrong PASS — it produces **wasted research and a false sense of budget** [cited]. §10.5 reduces the waste; nothing removes the structure.

### 10.5 Trial budget

> **[R15 · 2026-08-06 · THE BUDGET IS REBUILT AGAINST A DECLARED CONSERVATIVE `ρ`. READ §10.5.1 AND §10.5.2 FIRST — THE TABLE BELOW IS NOW STAGE 1 PLUS STAGE 2, NOT A SINGLE AUTHORIZATION.]**

> ~~**80 post-seal trials, pre-committed.**~~ ~~**[R6 · 2026-08-04] 79 post-seal trials, pre-committed.**~~ **[R15 · 2026-08-06] 47 post-seal trials AUTHORIZED, pre-committed, admissible at the declared planning `ρ_plan = 0.10`. A further ≤ 32 DECLARED BUT NOT AUTHORIZED, unlocked only by measurement. The flat 79 survives exactly, as the contingent ceiling, reachable only at ρ̂ ≤ 0.034.**

### 10.5.1 **[R15 · 2026-08-06]** The conservative `ρ` this budget is set against: **`ρ_plan` = 0.10**

> **THIS SEAT DECLARES, BEFORE ANY MEASUREMENT OF `ρ̂` EXISTS FOR THIS FAMILY OR ANY OTHER, THAT IT IS BUDGETING AGAINST `ρ_plan` = 0.10, AND THAT THE CORRESPONDING CEILING IS `N_max` = 55** [cited — `VALIDATION-SPEC-002` §6.2's measured table; **not re-derived here**].

**Why a conservative `ρ` must be named at all.** The Principal: *"burning `N` the measured ceiling may disallow is the sponsor's risk to declare, not discover."* **The budget this document carried through R-002 was set against `ρ = 0` — not by argument but by silence, because no other assumption existed when it was written.** At 7 + 79 = 86 it sits **exactly** at `N_max(0.034) = 86`: **zero trials of margin at its own binding threshold.** That is a budget an optimistic assumption sets and a measurement disallows, and it is the self-inflicted wound this revision exists to avoid pre-registering.

**Why 0.10 and not something else — the four reasons, and the one that is a judgment.**

| # | Reason | Provenance |
|---|---|---|
| 1 | **It is the top of the band `VALIDATION-SPEC-002` §7.4 calls repairable.** 0.034 < ρ̂ ≤ 0.15 is a FAIL-on-length whose remedy is calendar span — **≤ 11 months at ρ̂ = 0.1** — i.e. a PARK, not a kill. Above ~0.15 the remedy is 1.7–4.8 more years and PARK is nominal. **Budgeting to the top of the survivable band is the conservative choice that does not also concede the family.** | [cited — §7.3, §7.4] |
| 2 | **It is the largest ρ at which this family can still fund its Charter-mandatory work.** At `N_max(0.20) = 31` the ±50% grid alone is 25 and the ≥ 10 walk-forward windows take it to 35 — **inadmissible before F-002 runs.** At `N_max(0.10) = 55` the mandatory stack fits with margin. **A planning `ρ` that makes the Charter's own requirements inadmissible is not conservatism, it is a kill by budgeting.** | [cited — `VALIDATION-SPEC-002` §6.2; Charter §4.4] |
| 3 | **It is the Principal's own originally-stated figure, re-used where it is actually valid.** 0.1 is wrong as a *threshold* (§10.4.2) and it is a defensible *planning* value, and the two roles are distinct: a threshold that is too loose admits a family it should refuse; a planning value that is too tight only costs the sponsor. **The number that was permissive as a trigger is conservative as a budget.** | [inferred] |
| 4 | **This family's net series is structurally carry-heavy, and that is an argument AGAINST the generic dilution reasoning, not for it.** `VALIDATION-SPEC-002` §7.5 puts `ρ̂` "plausibly anywhere in [0.0, 0.5]" on the reasoning that a net series is `gross + carry − costs` and *"its price-return component is close to serially independent."* **This position is delta-neutral by construction — the price-return component is deliberately hedged out** — so the term that would dilute `ρ̂` toward zero is the term this family removes on purpose, and the persistent terms (funding carry; a weight `w(t)` that is a function of a trailing-30-day standardized deviation, hence persistent by construction) are what remain. **This family should therefore be expected in the upper half of that interval, not the middle.** | **[inferred — this seat's reasoning, stated as reasoning and not as measurement.** The funding autocorrelations 0.829 / 0.802 [cited — Ruling 003 §3.2] are **NOT `ρ̂`** and R-15 forbids quoting them as such; they are cited here only to establish that the carry term is the persistent one.] |

> **THE HONEST STATEMENT OF WHAT IS UNKNOWN, SO REASON 4 IS NOT READ AS A FORECAST.** **`ρ̂` has never been measured for this family and cannot be until it logs trials.** Reason 4 is a structural argument about which end of a cited interval this family occupies. **It is not a measurement, it is not a prediction, and it does not narrow the interval.** `VALIDATION-SPEC-002` §7.5's own sentence stands unamended: *"It could plausibly land anywhere in [0.0, 0.5]. Half that interval is a PASS-or-park and half is a kill."* **If `ρ̂` measures 0.4, `ρ_plan` = 0.10 will have been optimistic and this family dies on arithmetic, exactly as `forward-lag-001` does. Declaring 0.10 is not a claim that 0.4 is unlikely.**

### 10.5.2 **[R15 · 2026-08-06]** The two-stage budget, and why staging rather than a flat cut

**STAGE 1 — AUTHORIZED NOW. 47 post-seal trials. Declared ceiling `N` = 7 + 47 = 54, against `N_max(ρ_plan = 0.10)` = 55 [cited]. Margin: 1 trial.**

| Allocation | Trials | Change from R-002 |
|---|---:|---|
| **C11** — the leg-(ii) null calibration (§5.5(e)), if Validation requires it, **run before F-002** | ≤ **2** | unchanged |
| **F-002** (§5) — `R_bench`, `R_strat`, `R_bench_scaled` | **3** | unchanged |
| Pre-grid diagnostics: per-regime-cell decomposition, capacity measurement, cost sensitivity at 1× / 2× / repaired-preset, skew & expected-shortfall line | ≤ **7** | unchanged |
| **±50% parameter grid** (§10.5 below) — Charter §4.4 mandatory, not reducible | **25** | unchanged |
| Walk-forward efficiency — **Charter §4.4's floor of 10 windows**, each a refit **at the fixed plateau-centroid configuration**, no per-window re-selection (§10.7(c)) | ≤ **10** | ~~≤ 20~~ **windows 11–20 move to Stage 2** |
| **Stage 1 total** | **≤ 47** | ~~79~~ |

**STAGE 2 — DECLARED, NOT AUTHORIZED. ≤ 32 further trials. Unlocked only by a measured `ρ̂` whose cited `N_max` admits them.**

| Allocation | Trials |
|---|---:|
| **`N_forward`** — forward-window generation through ~~2027-01-31~~ **[R32 · 2026-08-11] `C + 187 days`**. **These are trials, not confirmations** (Validation C-001 **E3**), they are logged as such, and **no reported result may be selected from among them** | ≤ **22** |
| Walk-forward windows **11–20**, same fixed plateau-centroid configuration | ≤ **10** |
| **Stage 2 total** | **≤ 32** |
| **Stage 1 + Stage 2** | **≤ 79** — *identical to R-002's flat budget, preserved rather than replaced* |
| **Ceiling `N` at full Stage 2** | **7 + 79 = 86** — *identical to R-002; reachable only at ρ̂ ≤ 0.034* |

> ~~**THE UNLOCK RULE, PRE-COMMITTED.** Stage 2 trials may be spent only while the family's declared ceiling `N` remains at or below the `N_max` implied by the **most recently measured** `ρ̂` on this family's own logged trials, read from the cited table at `VALIDATION-SPEC-002` §6.2 and **never interpolated by this seat**.~~
>
> ### **[R20 · 2026-08-10 · STRUCK AND REPLACED. THE STRUCK RULE WAS A PROSE ACT AND I-105 IS THE FINDING THAT A PROSE ACT IS NOT A REGISTRATION ACT. IT WAS ALSO UNIMPLEMENTABLE AS WRITTEN (I-104). BOTH ARE STATED BEFORE THE REPLACEMENT.**
>
> **Head (i) — IT WAS NOT REGISTERED, AND THEREFORE DID NOT EXIST.** `gates.py:562` reads `sealed = fam.trial_budget` [measured]. **Sealed at the flat 79 — which is what every version of this document through R-003 would have sealed — the harness enforces 79, no contingent predicate is ever evaluated, and the paragraph above describes, in a frozen document, permanently, a gate that does not exist.** That is **I-105, HIGH**, and it is `GATES.md` §4.7.2's worked example by name: *"a control exists where the harness reads it, and nowhere else."*
>
> **Head (ii) — THE LOOKUP HAD NO DEFINED VALUE BETWEEN ITS RUNGS.** *"Read from the cited table … never interpolated"* is undefined at `ρ̂` = 0.07. The nine rows at `VALIDATION-SPEC-002` §6.2 are a **rendering** of `stats.max_admissible_trials`, which is continuous. **RULING 003-A rules that the function governs** [cited — `VALIDATION-SPEC-003` §7.3]. That is **I-104**, and it is conformed here rather than reconciled against a frozen document later.
>
> ### THE REPLACEMENT — REGISTERED, GENERIC, AND EXECUTABLE BY THE HARNESS AS IT STANDS TODAY
>
> **The sealed `trial_budget` is 47.** Stage 2 is **not** in that field and is not added to it. Stage 2 is a **`trial_budget_extension` event** in the registry's append-only `events` table, written after the seal, in `VALIDATION-SPEC-003`'s **CONTINGENT** form (B-13, B-16 … B-20):
>
> ```
> mode              = "CONTINGENT"
> increment         = 32
> issuer            = "director-of-research"
> authorization_ref = "research/PREREG-002-crypto-funding-basis.md"
> n_logged_at_issue = <this family's own logged count at the instant of the write>   # B-21 cross-check
> predicate         = {"name": "n_max_admits_declared_ceiling", "params": {}}        # B-17, closed vocabulary
> ```
>
> **and the criterion computes, at every evaluation and never on the event's word:**
>
> ```
> declared_ceiling_base = fam.n_inherited + sealed_trial_budget          = 7 + 47 = 54
> N_max                 = min(n_max_admissible_iid, n_max_admissible_serial)          # M-5, recomputed
> allowed               = clamp(N_max − declared_ceiling_base, 0, increment)
> ```
>
> **This document declares an INSTANCE. It does not describe the mechanism and has no standing to.** B-22 makes genericity a tested property: `gates.py`'s source may contain none of `PREREG-002`, `rho_plan`, `0.034`, `stage_2`, or `crypto-funding`, and **`test_tbe_15` already reproduces the table below without knowing this document exists** [cited].
>
> | Measured `ρ̂` | `N_max` [cited — SPEC-002 §6.2] | Admitted | This document's own words |
> |---:|---:|---:|---|
> | ≤ 0.034 | 86 | **32** | "the whole of Stage 2" |
> | ≈ 0.05 | 77 | **23** | "≤ 23 of the 32" |
> | ≈ 0.10 | 55 | **1** | "≤ 1 of the 32" |
> | ≥ 0.20 | 31 | **0** | "NONE, and Stage 1 itself is already over" |
>
> *(`clamp` on four already-cited integers at base 54; no harness call made, no test run. **The table holds only at `n_inherited = 7` — at 0 the base is 47 and the middle two rows read 30 and 8. That is R19 and it is why R19 and R20 are one revision.**)*
>
> **Six properties, every one of which runs AGAINST this sponsor and none of which this seat can soften:**
>
> 1. **Self-issue is safe and needs no countersignature** — B-16: *"authorized by a computation, not by a person… Forging the event buys nothing, because the number that governs is recomputed."* The door's key is arithmetic and this seat does not hold it.
> 2. **The vocabulary is closed and `params` must be EMPTY** (B-17). A sponsor-supplied `N_max` is MALFORMED, not a hint.
> 3. **Unevaluable ⇒ zero, and FAIL rather than INSUFFICIENT-DATA** (B-19): no `oos_index`, ineligible VIF, `sr_ann ≤ 0`, or `n_logged = 0`.
> 4. **The cap is AGGREGATE** (B-20). Ten events declaring 32 each admit 32 once.
> 5. **A malformed, un-withdrawn event FAILS the criterion even where the family is comfortably inside its sealed budget** (B-23), and the repair is a **withdrawal, not an edit** (B-24).
> 6. **`n_logged_at_issue` is cross-checked against the trial ledger** (B-21) and a reused `authorization_ref` is refused (B-26).
>
> **THE INTENT IS PRESERVED EXACTLY AND ONE SENTENCE OF IT IS NOW HONEST THAT WAS NOT.** *"No Stage 2 trial is spent on an unmeasured or a stale `ρ̂`"* **remains the pre-commitment, and R-004 records that it has NO SPEND-TIME CONTROL.** `log_trial` reads no budget — its only precondition is that the family is registered [measured — `registry.py:477–502`]. **The budget is enforced RETROSPECTIVELY, at `evaluate_gate1`, by B-9's ordering walk over the trial timestamps.** Nothing prevents the spend; the spend fails the gate afterwards, and **trials cannot be unspent** [cited — V-5]. Filed **I-132**. **The sentence is a discipline on the seat that writes the loop, and R-004 stops this document from implying otherwise.**

**Why staged rather than a flat cut to 47 — and this is the substantive argument, not a convenience.**

1. **A flat cut forfeits capability on an assumption; staging forfeits it only on a measurement.** The unlock is contingent on `ρ̂`, which is **not a result**. It is a nuisance parameter of the return series, measured by the harness, not chosen or reported by the sponsor. **Expanding a budget because early results look good is the overfitting operation wearing a schedule's clothing** — §10.4 says so and R-003 does not weaken it. **`ρ̂` is not "results look good"; it is the denominator's own denominator, and it moves the budget in whichever direction it measures.**
2. **The gaming route is closed by the correction itself, not by this seat's assurance.** A sponsor could try to lower measured `ρ̂` by aggregating to coarser bars. **Under the uncorrected statistic that evasion works and works enormously — 4.5× — and under the correction the requirement varies by 17%** [cited — R-16; I-061]. K6 additionally fixes bars at daily and moving it is a §7.2 escalation. **Selective logging is closed by R-6/R-7/R-8's max-then-median construction with the candidate series as a floor, and by R-9's refusal above a 25% exclusion rate** [cited].
3. **STAGING IS WHAT MAKES `VALIDATION-SPEC-002` §7.4's PARK VERDICT OPERATIONAL RATHER THAN NOMINAL, AND THIS IS THE STRONGEST REASON.** Under a flat 79-trial budget, a family PARKed at ρ̂ = 0.10 would keep spending its ≤ 22 forward-window regenerations while waiting for the ≤ 11 months of history that is its **only honest remedy** [cited — V-5]. **Every one of those trials raises `N`, which raises `MinBTL`, which raises the span required — the parked family digs its own hole while waiting in it.** Stage 2's gate stops that by construction. **A PARK that keeps burning `N` is not a PARK.**
4. **It is the only remedy a sponsor actually controls.** Of V-5's four remedies, three do not work — `N` cannot be reduced, a successor family inherits transitively, and a higher realized Sharpe is more search wearing a hat. **The one that works is calendar span, and the one thing a sponsor can do to help it is not spend trials while it accrues.**

> **THE OBJECTION TO THIS CONSTRUCTION, RAISED HERE RATHER THAN LEFT FOR THE RED TEAM.** A two-stage budget is a budget with a door in it, and doors get opened under schedule pressure. **The defence is that the door's key is held by the harness and not by this seat** — `VIF_gate` is computed inside `evaluate_gate1` from the registry, printed on the report face, and cannot be supplied by the sponsor [cited — V-1, V-2, M-10]. ~~**The residual risk is that a future seat spends Stage 2 without checking, and the only control against that is that this sentence is in a sealed document.** This seat rates that control as real but weaker than a hard refusal in code, and notes that **I-022 — `gates.py` hard-codes the trial-count criterion's verdict to the literal `True`** — means the budget is still enforced by this seat and by nothing else. **C10 therefore now bears on Stage 2's gate, not merely on the headline budget, and its weight goes up rather than down.**~~
>
> ### **[R27 · 2026-08-10 · STRUCK. I-022 IS REPAIRED AND HAS BEEN SINCE 2026-08-05. THIS PARAGRAPH UNDERSTATED THE PROTECTION OF THE SPONSOR'S OWN CONSTRUCTION, AND THE SPONSOR IS THIS SEAT.]**
>
> **`gates.py:527–640`, `_trial_budget_criterion`, read in source this session [measured]. The literal `True` that I-022 quotes DOES NOT EXIST in `gates.py`.** What replaced it FAILs in three separate ways:
>
> - **B-7** — `sealed <= 0` with logged trials → **FAIL**, *"NO AUTHORIZED BUDGET"* (`:598`);
> - **B-9** — an ordering walk **per trial, not per aggregate**: the k-th trial logged above the then-effective budget → **FAIL**, naming k (`:606–620`);
> - **B-23** — a malformed, un-withdrawn extension → **FAIL**, *"checked ahead of B-7/B-8/B-9, all of which describe a WELL-FORMED registry state."*
>
> `VALIDATION-SPEC-003` §12: *"I-022 closes on Seat 9's implementation of B-1 … B-31 with all 19 tests green."* `DATA-IMPL-007` §5: ***"Can close. All 19 test functions (27 collected items) are green."*** [both cited]. **The implementation landed 2026-08-05 and the Issue Log entry still reads `open`.**
>
> **THE CORRECT STATEMENT, WHICH IS NEITHER THE STRUCK ONE NOR A NAIVE REPAIR.** **I-132 stands unchanged: `log_trial` reads no budget** [measured — `registry.py:477–502`], so nothing *prevents* an over-budget spend and trials cannot be unspent. **Prevention: none. Detection and refusal: automatic, per trial, with the offending trial named.** The residual risk is real and it is **that the family fails its own gate afterwards**, not that nobody notices.
>
> **C10's weight, raised at R-003 and raised again at R-004, FALLS — and it should never have been raised the second time, because the repair had shipped five days earlier.** **This seat built the two-stage budget, would benefit from overstating its protection, and is recording a correction that runs in the family's favour; it states that conflict rather than letting the correction pass as routine.** Filed **I-142, MEDIUM.**

### 10.5.3 The line items as R-002 declared them — **[R15 · 2026-08-06] RETAINED AS THE RECORD, SUPERSEDED AS THE AUTHORIZATION**

> **[R15 · 2026-08-06] The table below is the R-002 flat budget. It is NOT struck, because every line item survives unchanged in substance and the only two that move are the walk-forward allocation (≤ 20 → ≤ 10 authorized + ≤ 10 contingent) and `N_forward` (≤ 22, entirely contingent). It is superseded as an authorization by §10.5.2's two stages. Where the two disagree, §10.5.2 governs.**

| Allocation | Trials |
|---|---:|
| **C11** — the leg-(ii) null calibration (§5.5(e)), if Validation requires it, **run before F-002** | ≤ **2** |
| **F-002** (§5) — `R_bench`, `R_strat`, `R_bench_scaled` | **3** |
| Pre-grid diagnostics: per-regime-cell decomposition, capacity measurement, cost sensitivity at 1× / 2× / repaired-preset, skew & expected-shortfall line, ~~SOL on its own span~~ **[R3/R6 · 2026-08-04 — struck; SOL is not in the universe]** | ~~≤ **8**~~ **≤ 7** |
| **±50% parameter grid** (below) | **25** |
| Walk-forward efficiency — Charter §4.4 requires **≥ 10 windows**, each a refit and therefore a logged trial. **[R11 · 2026-08-05] Each window is refit AT THE FIXED PLATEAU-CENTROID CONFIGURATION; no window re-selects and no per-window optimum is computed or reported — §10.7(c), which is what keeps ML-1's fitted-family trigger from firing** | ≤ **20** |
| **`N_forward`** — forward-window generation through ~~2027-01-31~~ **[R32 · 2026-08-11] `C + 187 days`**. **These are trials, not confirmations** (Validation C-001 **E3**), they are logged as such, and **no reported result may be selected from among them** | ≤ **22** |
| **Total** | ~~**80**~~ ~~**[R6] 79**~~ **[R15 · 2026-08-06] 79 = 47 AUTHORIZED (Stage 1) + 32 CONTINGENT (Stage 2)** |

> ~~**[R6 · 2026-08-04] Ceiling `N` = 79 + 7 = 86 — unchanged from the pre-revision 80 + 6.**~~ **[R15 · 2026-08-06] Ceiling `N` = 7 + 47 = 54 AUTHORIZED, against `N_max(ρ_plan = 0.10)` = 55 [cited]. Ceiling `N` = 7 + 79 = 86 at full Stage 2, against `N_max(ρ̂ ≤ 0.034)` = 86 [cited] — reachable only on measurement.** §10.4's measured `MinBTL(86, SR 1.0) = 6.14 yr` and its 0.43-year margin stand unedited **and are now correctly read as the `VIF = 1` slice** (§10.4, §10.4.1). The convenience in choosing −1 rather than −2 is disclosed at §10.1.

**The ±50% grid: 2 parameters × 5 steps = 25 points, and the constraint is measured not chosen.**

`grid_from_center(fraction=0.5, steps=5, max_points=200)` **raises `ValueError` above 200 points** [measured — `grid.py:27`], and independently §10.4 caps total `N` at ~~110~~ **[R8 · 2026-08-05] 109**. A 3-parameter grid is 5³ = **125 points**, which alone would put `N` at 125 + 2 + 8 = 135 and **fail the length criterion outright** — **[R8]** and fails it against 109 by more, not less, so the constraint that fixed the grid at 2 parameters is strengthened rather than disturbed. A 4-parameter grid is 625 points and the harness refuses it.

> **[R41(b) · 2026-08-25 · THE GRID NOW HAS A CENTRE, AND UNTIL TODAY IT DID NOT.** `grid_from_center(fraction=0.5, steps=5)` requires a centre; §15 runs the grid at **step 6, after F-002 at steps 2–3**, so the centre would have been chosen with F-002's output in hand — **I-029(d) relocated from the lag axis to the parameter axis, in the family whose §5.5 table exists to certify it committed no such operation. I-212.** **The centres are sealed literals: `lookback` = 30 → {15, 22.5, 30, 37.5, 45}; `k` = 0.5 → {0.25, 0.375, 0.5, 0.625, 0.75}.** Fixing the centre closes it; reordering the steps was never the remedy. **Residual, named and not repaired: `lookback`'s grid produces non-integer day counts (22.5, 37.5) and this document does not specify the rounding — filed I-222.**]**
>
> **Therefore: `lookback` and `k` (the de-scale slope) are gridded at ±50%, 5 steps each = 25 points. `d` = 1.0 (the deadband) and `band` = 0.10 (the turnover band) are fixed at pre-registration — **[R41] with values, which is a claim this sentence could not previously support** — and are not gridded. `w_max = 1.0` is not a free parameter — it is the statement that the strategy never exceeds the benchmark's size, which is part of K2 and not a tuning knob.**
>
> **The choice of which two to grid is itself pre-committed here, from a menu of the four candidates, and falls under the §7.2 escalation rule if revised.**

**Plateau centroid, not argmax — stated as policy, per §4.6 and the CLAUDE.md standing constraint.** `run_parameter_grid` returns both `argmax_params` and `plateau_centroid_params`. **Only `plateau_centroid_params` advances.** `argmax_params` is reported alongside it in every artifact, because the *distance* between the two is itself the overfitting diagnostic: a plateau has them close together and a spike has them far apart. **Every one of the 25 points is a logged trial and is paid for in the DSR** [cited — `grid.py` module docstring].

**The budget is real.** A family over budget is this seat's finding to raise before Validation raises it. The live defect that makes saying so necessary: **I-022 — `gates.py` builds the trial-count criterion with the verdict argument hard-coded to the literal `True`, so an over-budget family reads PASS with a note** [measured — confirmed again this session at `gates.py`, the `_crit("Trial count N (registry)", ..., True, ...)` branch]. **Until I-022 is fixed, the budget is enforced by this seat and by nothing else.**

### 10.6 What `σ_SR` will and will not mean

`deflated_sharpe_ratio` takes `fam.sr_period_std` — the cross-sectional standard deviation of Sharpe ratios across **logged** trials. With 25 grid points plus ~20 walk-forward refits, this family will produce a **genuinely populated** trial distribution, which is the input §4.1's whole apparatus requires and which a family with three hand-run variants cannot supply. **This is a real methodological advantage of budgeting a grid, and it is the argument for spending 25 trials on one rather than treating the grid as a Gate 1 tax.** Recorded so the budget's shape is understood as a design choice.

### 10.7 **[R11 · 2026-08-05]** `VALIDATION-RULING-004` — does it bind this family, and where the answer is not "no"

**The short answer, stated first because the long one has three parts:** the ruling's **`N` accounting** leaves this document's accounting **intact**, and the reason is checkable choice by choice rather than assertable. **But the ruling is not silent on this family**, and two of its clauses reach this document in ways nothing here previously carried. Both are repaired below. **A third — its correction of §10.4's ceiling — is R8.**

**Validation's own summary line is `PREREG-002 §10: "Untouched"`** [cited — `VALIDATION-RULING-004` §12]. **That line is correct about §10 and would be wrong if read as "the ruling does not reach this document,"** and this seat records the difference rather than resting on the summary.

#### (a) ML-1's trigger — does this family fire it?

> **ML-1:** *"A hypothesis family is a **fitted family** … if **any** number that enters a reported result is selected by comparing two or more candidates on a quantity computed from the sample"* [cited].

| Candidate operation in this family | Selected on a sample-computed quantity? | Verdict |
|---|---|---|
| **K1–K7** — the seven conditioning choices | **No.** Each was selected **before any measurement**, from a menu declared in this document, against a registry holding 0 families and 0 trials [measured]. **K4's R3 move is the only selection that changed after data existed, and it moved on a DOCUMENTED VENDOR ACT dated 2022-11-09, not on any statistic — §9.1 records the three checkable facts that establish this, including that no return statistic on SOL has ever been computed by this family.** | Does not fire |
| **The ±50% parameter grid** (§10.5, 25 points) | **The grid compares candidates on the sample — but the configuration that ADVANCES is the plateau centroid, fixed by rule.** ML-1's boundary case rules exactly this: *"The ±50% parameter grid Charter §4.4 already requires of every family … does not by itself make a family a fitted family, because the configuration that advances is the plateau centroid, fixed by rule, not the grid's argmax. **A family becomes a fitted family the moment any selection is made at an argmax rather than by a declared rule**"* [cited]. | **Does not fire — CONDITIONALLY, and the condition is §10.5's commitment that only `plateau_centroid_params` advances. That commitment is now load-bearing in a way it was not when it was written.** |
| **Walk-forward, ≥10 windows** (§10.5, §15 step 7) | **UNSPECIFIED IN R-001, AND THAT WAS THE GAP.** *"Each a refit and therefore a logged trial"* does not say whether each window **re-selects** its configuration. **If it did, ML-1 would fire, this would become a fitted family, and ML-13 would charge the grid's full cardinality — per window.** | **REPAIRED. See (c).** |
| **F-002's three series and its four legs** | **No.** Three pre-specified series, four pre-committed constants, *"no `argmax`, no grid, no peak, and no selection over candidates of any kind"* (§5.5). | Does not fire |

**Verdict: this family is NOT a fitted family**, and ML-3 through ML-27 do not reach it — **conditional on (c) below, without which the answer would have been the opposite.**

#### (b) ML-2 binds every family, including this one, and this document did not carry it

> **ML-2:** *"A family that asserts it is not a fitted family carries, in the same sealed block, the single sentence: 'No number reported by this family is selected by comparing candidates on a quantity computed from the sample.' **Silence is not that assertion.**"* And: *"A Gate 0 intake with a missing or partial ML block is **REJECTED, not deferred**"* [cited].

**This document was silent, and silence is the failure mode ML-2 names by name.** The sentence is added verbatim to §21's `success_criteria` field, where it is hashed into `prereg_sha256` and frozen under P3. **It is an assertion of fact in a sealed document and this seat makes it deliberately and checkably** — (a) above is the check, and if any one of its rows is later found to be wrong, the assertion is false in a sealed field, which is a heavier consequence than a wrong verdict and is the correct weight for it.

**Filed as I-056:** `PREREG-001-forward-lag` is also silent and is also unsealed. **Under ML-2 as written it would be REJECTED at Gate 0 for a missing ML block** — a rejection on a paperwork clause, of a family already crippled on arithmetic, which is a poor use of a Gate 0 verdict. It is cheap to fix pre-seal and expensive to discover at intake.

#### (c) The walk-forward specification — the one place the answer changed the document

> **[R11 · 2026-08-05 · BINDING.]** **The ≥10 walk-forward windows are evaluated at the FIXED plateau-centroid configuration carried forward from §10.5's grid. No window re-selects, re-fits by comparison, or reports a per-window optimum. Each window is a refit of the strategy's estimated quantities at a FIXED configuration — which ML-1 explicitly does not catch (*"OLS coefficients under a declared specification, a covariance matrix, a rolling mean — these are unique minimizers of a declared objective, not selections among candidates"* [cited]) — and each remains a logged trial against the ≤20 allocation.**
>
> **This is a defect repair, not a design change, and the distinction is the same one R4 turned on.** The struck state was **silence**, and silence here does not default to the safe reading — a walk-forward that re-optimizes per window is the ordinary implementation and is what an unspecified instruction would most likely have produced. **Sealing the silence would have left the fitted/not-fitted question to be settled by whoever wrote the loop, after `C`, which is a researcher degree of freedom of the largest possible kind: it decides whether ML-3's 109-trial ceiling is charged against a declared `N` of 86 or against 86 plus 25 configurations per window.**
>
> **It costs the family nothing it had.** §10.5 already committed that *"only `plateau_centroid_params` advances"*; this clause states the consequence for the step that would otherwise have quietly re-opened the selection. **It removes a degree of freedom and adds none, which is why it is admissible pre-seal against a 0-trial registry.**

#### (d) ML-13 leaves §7.2's menu discount intact for K1–K7, and the reason is the discount's own stated condition

> **ML-13:** *"The pre-commitment discount — menu size reduced to 1 — is available **if and only if** the selection is fully determined at sealing by facts stated in the sealed document, without reference to any quantity computed from the sample… **No fitting search ever receives the discount.**"* And: *"This is an extension of PREREG-002 §7.2, not an exception to it"* [cited].

**Every one of K1 through K7 satisfies the condition on the row-by-row evidence at (a).** `N_conditioning` therefore remains **7**, the trial budget remains **79**, ceiling `N` remains **86**, and `MinBTL(86) = 6.14` against 6.571 stands. **This is what "the extension leaves the `N` accounting intact" means, and it is worth stating as a conclusion drawn per choice rather than as a citation of Validation's summary line** — because the summary line would still have read "Untouched" if one of the seven had failed the test, and the party best placed to find that is the seat that made the seven choices.

**One asymmetry recorded against this family's interest.** ML-13's *"declaration still buys the family something real… It is just not worth a factor of `|Θ|`"* is the ruling's statement of what a menu declaration is worth to a **fitted** family. This family claims the full factor — 7 rather than 135,000 (§7.3) — **on the strength of a condition it asserts about itself.** §7.2's escalation rule is the enforcement, and R9 has just established that the enforcement was **inoperative** between R-001 and this revision. **The discount and its enforcement were, for that interval, not in the same document in any operative sense. That is the sharpest single criticism available against this family's `N` accounting, it is this seat's to raise, and it is raised here rather than left for the Red-Team Memo to find.**

### 10.8 **[R16 · 2026-08-06]** The pre-committed verdict bands on `ρ̂`, recorded in the sponsor's own document

*`VALIDATION-SPEC-002` §7.4 pre-commits the verdict rule **before the measurement exists**, which is Ruling 001 §4.4's own device used for the same reason. It is recorded here, in the pre-registration, so that **the sponsor cannot renegotiate at Gate 1 a band the sponsor pre-registered at Gate 0.** All figures `[cited]`; **none is re-derived and none is this seat's.***

| Measured `ρ̂` (or VIF) | `N_max` | Verdict on the length criterion, pre-committed |
|---:|---:|---|
| **ρ̂ ≤ 0.034** (VIF ≤ 1.071) | ≥ 86 | **PASS**, if every other §4.4 criterion passes |
| **0.034 < ρ̂ ≤ 0.15** | 41–85 | **FAIL on length.** Remedy is calendar span; **≤ 11 months at ρ̂ = 0.1**. **PARK, re-evaluate on more history** |
| **0.15 < ρ̂ ≤ 0.30** | 19–41 | **FAIL on length.** Remedy is 1.7–4.8 more years. **PARK is nominal; this is a kill in practice** |
| **ρ̂ > 0.30** | ≤ 19 | **FAIL on length. KILL.** The family spent its trials into a space that admits fewer than 19 |
| **\|ρ̂\| ≥ 0.97**, or `n_logged` = 0, or R-9's exclusion rate | — | **INSUFFICIENT-DATA**, escalated to Validation. **NEVER PASS** |

> **NONE OF THESE IS A MALFUNCTION AND THIS SEAT WILL NOT DESCRIBE ANY OF THEM AS ONE.** The Principal has already ruled the frame: *"a PARK or kill on measured ρ is a terminal verdict under §1, not a malfunction"* [cited — `VALIDATION-SPEC-002` §0.2]. **A KILL memo on this family arriving from `ρ̂ > 0.30` is a successful deliverable under Charter house rule 1 and §19.3 already predicts a KILL from a different cause.**
>
> **`n_logged = 0` deserves separate emphasis because it is the one band a sponsor might read as safe.** There is **no fallback to `VIF = 1`** — *"a VIF of 1 is not a neutral default; it is the permissive assumption this document exists to remove"* [cited — R-11]. A family with zero logged trials draws **INSUFFICIENT-DATA on the length criterion, the DSR criterion, and the trial-count criterion**, and never PASS. **This family cannot reach Gate 1 by declining to run.**

> ### **THE SHARPE ESCAPE IS CLOSED BY CONSTRUCTION, AND IT IS THE ONE A SPONSOR WILL REACH FOR.**
>
> `MinBTL ∝ 1/SR²`, so at ρ̂ = 0.10 a realized net `SR_ann ≥ 1.068` clears the length criterion on the 6.571 years already held [cited — `VALIDATION-SPEC-002` §7.3]. **That route is arithmetically genuine and it is trapped: raising the realized Sharpe by searching raises `N`, which raises `MinBTL`, which raises the Sharpe required.** It works **only** if the Sharpe rises *without new trials* — i.e. on data not yet seen — **which is the calendar-span remedy wearing a hat** [cited — V-5].
>
> **This seat records the closure in its own pre-registration because this seat is the party that would reach for it.** Charter §4.6's *"prefer the plateau centroid to the argmax"* and §10.5's commitment that only `plateau_centroid_params` advances are the same discipline at the configuration level; this is that discipline at the family level. **A family that improves its Sharpe by searching does not improve its position, and any artifact on this family that presents a search-improved Sharpe as relief from the length criterion is defective, with this clause as the pre-registered reason why.**

### 10.9 **[R18 · 2026-08-06]** I-060 and I-061 checked against this document, choice by choice

#### (a) I-060 — does the diagnostics-versus-ceiling collision bite this family? **Not as a clause. It does bite as arithmetic, at a tighter `ρ` than I-060's own.**

**The conservative reading governs.** The Principal has deferred reconciliation of I-060 to Sprint 3 and ruled that, meanwhile, **diagnostics count toward `N`** [cited]. **The check is run below rather than asserted, because the assertion "this family is not fitted, so I-060 does not reach it" is exactly the shape of claim §10.7(d) warns is invisible when it is wrong.**

| I-060 obligation | Does it reach this family? | Is it already counted toward `N` here? |
|---|---|---|
| **ML-16's mandatory 32-trial dispersion sample** | **No.** ML-16 is inside ML-3–ML-27, and §10.7(a) establishes row by row that this family is **not a fitted family** [cited — ML-1's boundary case; the condition is §10.5's plateau-centroid commitment and §10.7(c)'s walk-forward fix]. | **N/A — and the family gets the statistical content free.** §10.6: 25 grid points + walk-forward refits produce a **genuinely populated** trial distribution for `σ_SR`. At Stage 1 alone that is 25 + 10 = **35 series ≥ Ruling 004 §2.4's `m ≥ 32` floor**, at **zero incremental `N`**, because they are already budgeted trials. **The dispersion requirement's arithmetic is satisfied without the dispersion sample's cost.** |
| **±50% grid, 25** | **Yes** — Charter §4.4, not ML-3. | **Counted. Stage 1, 25 trials.** |
| **Walk-forward, ≥10 windows** | **Yes** — Charter §4.4. | **Counted. Stage 1 ≤ 10, Stage 2 ≤ 10.** |
| **Seed ensemble, 10** | **No.** An ML-family obligation. This family has no stochastic fit and no seed to ensemble; `w(t)` is a closed-form clip of a trailing standardized deviation. | **N/A, and not counted — correctly, since it will not be run.** |
| **Falsifier legs, 2–3** | **Yes** — F-002. | **Counted. Stage 1, 3 trials.** |
| **Pre-grid diagnostics (regime decomposition, capacity, cost sensitivity, skew/ES)** | **Yes** — this document's own, not Ruling 004's. | **Counted. Stage 1, ≤ 7 trials.** |
| **C11 null calibration** | **Yes** — this document's own. | **Counted. Stage 1, ≤ 2 trials.** |
| **`N_forward` forward-window generation** | **Yes** — Validation C-001 E3 rules these are trials, not confirmations. | **Counted. Stage 2, ≤ 22 trials.** |

> **VERDICT ON I-060: THE CLAUSE DOES NOT BITE. THE FINDING BEHIND IT DOES, AND HARDER.**
>
> **Not as a clause** — ML-16 does not reach a non-fitted family, and every diagnostic this family *will* run was already inside its declared `N` before R-003, under the conservative reading, with no exception found on the row-by-row pass above. **This seat looked for one and reports that there is none.**
>
> **But I-060's actual content is not "ML-16 is expensive." It is: *a family that cannot afford its own diagnostics has not discovered a problem with the diagnostics; it has discovered that this firm's data cannot support that family at that persistence*** [cited — I-060]. **On that reading it reaches this family directly and at a tighter threshold than its own headline.** I-060's obligations exhaust the ceiling at **ρ̂ > 0.045**; this family's declared 86 exhausts it at **ρ̂ > 0.034** (§10.4.2), and its Stage-1-only 54 exhausts it at approximately the `ρ_plan` = 0.10 row. **This family is inside the same collision, one notch tighter, and it is not exempt from it by not being a fitted family. §10.5.2 is the response and it does not repair the collision — nothing does.**

#### (b) I-061 — does anything in this document rest on RULING-004 §2.1's frequency-invariance conclusion? **No.** Checked, not assumed.

**I-061 finds §2.1's algebra correct and its conclusion — *"a family cannot buy length by sampling more finely"* — false under the uncorrected statistic, permissively, by 4.5×** [cited — I-061; `VALIDATION-SPEC-002` §6.1]. Every place this document touches bar frequency:

| Clause | What it rests on | Rests on §2.1? |
|---|---|---|
| **§6.2 `periods_per_year` = 365** | Crypto trades every calendar day; no session gaps on either leg; matches the `CRYPTO_PERP_TAKER` preset. A calendar fact. | **No** |
| **§6.2 / K6 — daily bars, funding as the exact arithmetic sum of realized prints in `(t−1, t]`** | `VALIDATION-RULING-003` §3.2's alignment rule and the R4 deletion of the cadence constant. A data-correctness argument. | **No** |
| **§16.1 — the intraday problem** | That `book/pit.db` holds daily bars and this strategy's risk materializes intraday. An instrument-resolution argument, entirely about *what can be measured*. | **No** |
| **§19.3 / §22 row 4 — the successor family at 1h or 8h bars** | That a daily instrument cannot observe an intraday liquidation cascade. **Resolution, not observation count.** | **No** |
| **§10.4 / §10.5 — `MinBTL`, the ceiling, the grid cardinality** | `MinBTL(N, SR)` at the Gate 1 Sharpe floor of 1.0 on a fixed daily bar. **`ppy` never varies in this document**, so a frequency-invariance property is never invoked in either direction. | **No** |

> **VERDICT ON I-061: NOTHING IN THIS DOCUMENT RESTED ON IT.** This family fixed its bar granularity at daily as a **declared conditioning choice (K6) with a full menu, before any measurement**, for data-correctness and risk-observability reasons — **not because it believed bar choice was free of length consequences.** The mistaken conclusion was never load-bearing here.
>
> **ONE FORWARD-LOOKING CONSEQUENCE, RECORDED SO A FUTURE SEAT DOES NOT RE-DISCOVER IT AS A REMEDY.** §19.3 and §22 row 4 name a successor family at 1h or 8h bars. **Under the correction, that successor buys NO relief on the length criterion by sampling more finely** — the `√ppy` annualization overstates `SR_ann` at fine bars by exactly the factor the VIF removes, and the two cancel to within 17% [cited — R-16]. **The successor's case is resolution and nothing else.** A seat proposing 8h bars *to get more observations* should be shown this line — which is what §2.1 said, and it is true now because the correction makes it true rather than because §2.1 established it.

---

### 10.10 **[R21 · 2026-08-10]** The `GATES.md` §4.7.2 audit — every limit this document claims, against the field that enforces it

*§4.7.2, ruled 2026-08-06 (S2-D-029): **"For every limit the document claims, name the field the harness reads to enforce it. If there is no such field, there is no limit."** This section is that test applied to this document. **The full limit-by-limit table is at `DIR-RESTATE-001` §9; the conclusions are here because §9 is a memo and this is the sealed text.***

**The binding set is sixteen fields** [measured — `registry.py:82`, `_BINDING_FIELDS`]. **Being in that set means a field is HASHED, not that it is READ**, and §4.7.2's own wording does not force the distinction. `prereg_sha256` gives tamper-**evidence**; enforcement is a different property and a different code path.

| | Count | The fields |
|---|---:|---|
| **Read and enforcing** | ~~**4**~~ **[R25 · 2026-08-10] 5 — `holdout_classification` belongs here** | `family` (A2's `PreRegistrationError`) · **`trial_budget`** (`gates.py:562` → B-7/B-9/`declared_ceiling_base`) · **`n_inherited`** (four consumers, §10.1) · `predecessor_family` (chain summation, `InheritedCountDoubleCountError`) **· `holdout_classification`** (domain check; HISTORICAL → R3 presence requirement; report render) |
| **Read, but only as a check or a render** | ~~**3**~~ **[R25] 3 fields, and the check is on EXISTENCE ONLY** | `statement`, `mechanism`, `falsifier` — **non-empty at registration and nothing more.** **[R25] The distinction this row did not force: these are class (a) on EXISTENCE and class (c) on CONTENT.** `registry.py:262–268` raises on the empty string and reads not one character further. **F-002 — four legs, α = 0.0013, an 1,800-bar floor, a joint false-survival rate of 1.3 × 10⁻⁴ — is stored in a field whose only guarantee is that it is not empty.** |
| **SEALED AND READ BY NOTHING** | ~~**9**~~ **[R25 · 2026-08-10] EIGHT. THE 9 IS WRONG AND THE ROSTER IS RIGHT.** | `universe` · `horizon` · `success_criteria` · `model_prior_provenance` · `published_signal_haircut_applied` · `forward_window_start` · `forward_window_min_length` · `forward_kill_condition` — **eight, all with zero non-`registry.py` consumers** [measured] |

> ### **[R25 · 2026-08-10] THIS TABLE'S COUNT CELLS AND ITS OWN ROSTERS DISAGREED, AND THE DISAGREEMENT PROPAGATED BEFORE ANYONE MEASURED IT.**
>
> The cells read **4 / 3 / 9**; the rosters name **4 / 4 / 8**. **The corrected partition of the sixteen is 5 class-(a) and 11 class-(c)**, of which three carry an (a)-class existence check on presence only.
>
> **Where the 9 came from, which is the part worth recording:** it is **`DIR-RESTATE-001` §9.2's count of category-(c) *limits* — c1 through c9 — transplanted into a column that counts *fields*.** Two different denominators, one number, in text about to be frozen.
>
> **This is R8(c)'s and R22's defect class for the third time**, and it had already escaped this document: **dispatch S3-D-003 directs the relabelling of *"all nine zero-consumer binding fields."* There are eight.** The roster it names is complete; the cardinal is not. Filed **I-141, MEDIUM**. **Found on this pass, repaired on this pass, disclosed rather than silently conformed.**

> ### **THE FINDING, AND IT IS UNCOMFORTABLE FOR THIS DOCUMENT SPECIFICALLY.**
>
> **The three fields a pre-registration puts its methodology in — `universe`, `horizon`, `success_criteria` — have ZERO consumers in the entire harness.** That is where this document put K3's *"exclude nothing"*, the no-winsorization clause, `w_max = 1.0` and never-long-perp, the capacity screen, the 5% ADV cap, `periods_per_year = 365`, the ML-2 non-fitted assertion, the plateau-centroid commitment, §10.7(c)'s fixed-centroid walk-forward clause, F-002's E2 *"evaluated ONCE"*, §7.2's escalation rule, and all eleven mandatory disclosure lines. **Every one of them is enforced by the seat that writes the loop and by nothing else.** Filed **I-133**.
>
> **Two adjacent harness protections must not be mistaken for enforcement of these clauses.** `SameBarFillError` (`engine.py`) and `grid_from_center`'s 200-point `ValueError` (`grid.py:27`) are real and this document leans on both — **and neither reads a sealed field. Both would fire identically for a family that declared the opposite.**
>
> **Three limits this document leans on hardest are in the "read by nothing" column, and each is filed by name:**
> 1. **`published_signal_haircut_applied = 0.50`** — **I-134**. §5.4's `t(α) ≈ 6.0`, which §11.6 calls *"the largest single hurdle this family faces,"* is derived from a number no code path applies.
> 2. **`forward_kill_condition` = KC-002** — **I-135**. **No harness path evaluates a kill condition on any date, for any family**, and for FORWARD the field is not even presence-checked. **Clause 5's "silence is a kill" is itself defeatable by not running it.**
> 3. **§7.2's escalation rule and its hard stop.** What the harness enforces is real but narrower and different: `PreRegistrationAmendedError` refuses a changed binding field and `InheritedCountDoubleCountError` refuses the successor. **The hard stop is an emergent property of two guards, not a reading of the clause.**
>
> **And one that is not sealed at all: `log_trial` reads no budget** [measured — `registry.py:477–502`]. **The trial budget is enforced retrospectively, at `evaluate_gate1`.** Filed **I-132**. §10.5.2 carries the full statement.

**WHAT THIS SECTION IS NOT, said plainly so the finding is neither buried nor over-claimed.** It is **not** a list of defects to repair. Most of the nine belong in a sealed document and could not sensibly be mechanised — **no harness will ever check that no winsorization was applied**, and demanding one be built is not what §4.7.2 asks for. **The instruction is to name the field or to say there is none.** The finding is that **this document must stop describing prose as though it were a control**, and that of the two limits here which genuinely *could* be mechanised, one is mechanised by R19 (the conditioning floor, into `n_inherited`) and the other is filed and is not this seat's (the haircut).

**Why this is in the sealed text and not only in the memo.** §4.7.2's own reasoning: *"A frozen document describing a nonexistent gate is I-046's costume on the research side — an asserted control that is not there — and P7 makes it permanent. The repair is always pre-seal and never after."* **A sponsor who sealed this document while believing its methodology was enforced because it was binding would have made exactly that error, and the sponsor in question is this seat.**

---

### 10.11 **[R24 · 2026-08-10]** THE CLASS REGISTER — every limit this document claims, with its class

> ### **THE MANDATE. No limit may describe itself as a control without carrying its class.**
>
> | Class | Requires | What it is |
> |---|---|---|
> | **(a) harness-enforced** | a **named code path**, and the **named field** it reads where one exists | the engine refuses |
> | **(b) procedure-enforced** | a **named executor**, a **named cadence**, and the **named artifact** the execution produces | a person does it, on a schedule, and leaves a record |
> | **(c) declared commitment** | nothing further | **binding as a matter of record; enforced by audit and adversarial review only** |
>
> **THIS IS A LABELLING MANDATE, NOT A MECHANIZATION MANDATE. Nothing in this register was made enforceable that was not. A class-(c) label is a full and honourable answer and is NOT a demotion** — a document that honestly declares thirty-four class-(c) commitments is stronger than one implying sixty-one controls and holding twenty.
>
> **Why the register is here and not in the memo.** §10.10 put the audit's conclusions in the sealed text and its table in `DIR-RESTATE-001` §9. **R24 inverts that deliberately: the next reader needs the class beside the limit, not a pointer to it.** A limit whose class lives in another file is a limit whose class the next reader will not have.
>
> ### **COUNTS: 20 class (a) · 7 class (b) · 34 class (c) · SIXTY-ONE limits classified.**

#### 10.11.1 The sixteen binding fields — the §4.7.2 evidence, corrected

*Method: for each name in `registry.py:80–91` (`_BINDING_FIELDS`), `grep -rn "\b<field>\b" harness/castellan/ --include=*.py | grep -v registry.py`, then every surviving hit read at its call site to distinguish an enforcing read from a render from an unrelated use of the same English word [all measured, this session]. **Partition: 5 (a) · 11 (c).***

| # | Field | Class | (a): the code path · (c): why nothing reads it |
|---:|---|---|---|
| 1 | `family` | **(a)** | `registry.py:485` `log_trial` → `PreRegistrationError` (A2); `predecessor_chain`; every `evaluate_gate1` lookup |
| 2 | `statement` | **(a)** existence · **(c)** content | `registry.py:262–268` raises on empty; reads no further |
| 3 | `mechanism` | **(a)** existence · **(c)** content | same check |
| 4 | `falsifier` | **(a)** existence · **(c)** content | same check. **F-002's entire specification is (c)** |
| 5 | `universe` | **(c)** | zero real consumers [measured] |
| 6 | `horizon` | **(c)** | zero consumers |
| 7 | `success_criteria` | **(c)** | zero consumers |
| 8 | `trial_budget` | **(a)** | `gates.py:562`; B-7 `sealed <= 0` → FAIL (`:598`); B-9 ordering walk → FAIL (`:606–620`); `declared_ceiling_base` (`:565`) |
| 9 | `predecessor_family` | **(a)** | `registry.py:269–273`; `:294–308` `InheritedCountDoubleCountError`; `family_stats` transitive sum |
| 10 | `holdout_classification` | **(a)** | `registry.py:309–313` domain check; `:314–329` HISTORICAL → R3 presence; `gates.py:165`, `:168`, `:1055` |
| 11 | `forward_window_start` | **(c)** for this family | presence-checked **iff** HISTORICAL (`registry.py:314`). **This family is FORWARD** |
| 12 | `forward_window_min_length` | **(c)** | same; and the column is an unlabelled `REAL` (I-033(5)) |
| 13 | `forward_kill_condition` | **(c)** *as a field* | same. **The obligation it carries is (b)** — **B-01** below |
| 14 | `model_prior_provenance` | **(c)** | zero consumers |
| 15 | `published_signal_haircut_applied` | **(c)** | **no haircut computation exists** in `gates.py`, `stats.py`, `engine.py` or `costs.py` |
| 16 | `n_inherited` | **(a)** | `registry.py:277–284` validators; `family_stats`; `gates.py:148–152` (H-12 render), `:542`, `:565`, `:779`, `:788`, `:856` |

#### 10.11.2 CLASS (a) — twenty limits the harness enforces

*Fourteen of these read **no sealed field**. **They are class (a) regardless: a `ValueError` does not become a procedure because no sealed string triggers it.** The field column reads `—` where none exists, which is the honest answer to "name the field," not an omission.*

| # | The limit, as this document states it | Field | Code path [all measured] |
|---|---|---|---|
| **A-01** | No trial may be logged against an unregistered family (A2) | `family` | `registry.py:485` → `PreRegistrationError` |
| **A-02** | A pre-registration must carry a non-empty statement, mechanism and falsifier | those three | `registry.py:262–268` `ValueError`. **Presence only** |
| **A-03** | **The authorized budget is 47 own-logged trials, and the k-th trial logged above the then-effective budget FAILs the gate** | `trial_budget` | `gates.py:562`; B-7 (`:598`); **B-9's ordering walk, per trial, naming k** (`:606–620`) |
| **A-04** | `N` = `n_inherited` + logged, summed transitively, and it is the denominator DSR and MinBTL consume | `n_inherited`, `predecessor_family` | `family_stats`; `gates.py:779`, `:788`, `:856` |
| **A-05** | A successor may not re-declare its predecessor chain's count | `predecessor_family` | `registry.py:294–308` `InheritedCountDoubleCountError` |
| **A-06** | `holdout_classification` ∈ {FORWARD, HISTORICAL}; HISTORICAL requires the three R3 fields | `holdout_classification` | `registry.py:309–329` |
| **A-07** | **Stage 2 admits `clamp(N_max − 54, 0, 32)`, recomputed at every evaluation, never trusting the event** | `n_inherited` + `trial_budget` | `gates.py:565`; `_budget_extension_ledger` `:378–398`; B-16…B-21 |
| **A-08** | A malformed, un-withdrawn extension FAILs even inside the sealed budget (B-23) | — | `gates.py` B-23 branch, checked ahead of B-7/B-8/B-9 |
| **A-09** | `N_max` is a recomputed **function**, monotone-conservative (R13) | — | `gates.py:344` `_admissible_ceiling` = `min(iid, serial)` |
| **A-10** | The live `hypotheses` row must match the sealed shadow copy; a mismatch FAILs (P4) | all sixteen, via `prereg_sha256` | `registry.verify_prereg`, **called automatically at `gates.py:991`** |
| **A-11** | A re-registration differing on any binding field is refused (P3) | all sixteen | `registry.py:356–369` `PreRegistrationAmendedError` |
| **A-12** | The seal must not postdate `C` at UTC day granularity (P7) | — | `gates.py` P7 branch: `sealed_created_utc` vs the vault's `holdout_spec_sealed.cutoff` → FAIL |
| **A-13** | No `hypothesis_sealed` event ⇒ INSUFFICIENT-DATA, never PASS (P6) | — | `gates.py:1003` |
| **A-14** | The holdout is acquired exactly once | — | `HoldoutVault.acquire_once()`; the "Holdout single-use" criterion |
| **A-15** | Never fill at the bar that generated the signal | — | `engine.py` `SameBarFillError`. **Unconditional** |
| **A-16** | A ±50% grid may not exceed 200 points, and every point is a logged trial | — | `grid.py:27` `ValueError`; `grid.run_parameter_grid`. **Unconditional** |
| **A-17** | **The graded `t` is `min(t_NW, t_raw)` and never the raw figure** (I-050 / E-8) | — | `stats.py:153`, `:221`; `gates.py:752` |
| **A-18** | `\|ρ̂\| ≥ 0.97` or `n_logged = 0` ⇒ INSUFFICIENT-DATA, never PASS (E-9) | — | `stats.py:177–188` |
| **A-19** | **Carry is a signed cash flow; `CostModel.scaled(m)` never multiplies it** (T-16) | — | `costs.py:119–128` (no funding term on `CRYPTO_PERP_TAKER`); `carry.py` |
| **A-20** | **The registry-`N` decomposition and the holdout classification are rendered on every report face** (H-12, R1) | `n_inherited` **≠ 0**; `holdout_classification` | `gates.py:148–152`, `:165` |

> **Two disclosures this register must repeat rather than bury.**
>
> **A-15 and A-16 read no sealed field and would fire identically for a family that declared the opposite.** They are class (a) and they are **not** enforcement of anything this document says.
>
> **A-10 and A-11 are tamper-EVIDENCE across all sixteen fields and tamper-PREVENTION on none.** A raw `UPDATE hypotheses SET universe = ...` succeeds; what fails is the next `evaluate_gate1`, because the sealed event carries a **full shadow copy** and because `verify_prereg` is called **by the gate rather than by a person** [measured — `gates.py:991`]. **That last clause is what makes it (a) rather than (b), and this seat checked it rather than assuming it.**
>
> **A-20 is the mandate's one upgrade and it is small and real.** Two of the eleven mandatory disclosure lines are **written by the engine itself** and cannot be omitted by a seat that forgets. One of them became (a) **at R19**, because `gates.py:148` branches on `if self.n_inherited:` and the branch was dead while the field was 0. **R19 was argued as a tightening of the denominator; it also moved one disclosure line from (c) to (a), and nobody noticed until this pass.** The other nine remain (c).

#### 10.11.3 CLASS (b) — seven limits a named seat executes on a named cadence, producing a named artifact

*Applied strictly. **"The Director will check" is not a cadence and produces no artifact — that is (c) wearing (b)'s clothes.** Everything that failed all three tests is in (c), including two this seat wanted to promote.*

| # | The limit | **Executor** | **Cadence** | **Artifact** |
|---|---|---|---|---|
| **B-01** | **KC-002 is computed on `C` + 187 days, and SILENCE IS A KILL** | **the Principal** | **the weekly Friday ritual, alongside the pull-and-merge** | **the pasted evaluation attached to the record, per `TEMPLATES.md` §7.9** |
| **B-02** | Has any pre-registered falsifier been hit and not acted on (F-002) | **Director of Research** | **Friday 16:00, Weekly Research Review** — Charter §6.3 item 4 | **the weekly pipeline status** — every hypothesis by stage with age, trial count, next action |
| **B-03** | A Red-Team Memo with a binding named kill condition is present (C3) | **Devil's Advocate** | **every Gate 1 submission and every IC packet** — Charter §6.4: a packet without one is *deferred, not heard* | **the Red-Team Memo** |
| **B-04** | The Gate 0 intake verdict, and the C13(a)–(i) items ruled with it (C2) | **Head of Quantitative Validation** | **once, at intake, before the seal** | **the Intake Verdict** — ADMITTED / REJECTED / ADMITTED-AS-EXPLORATORY |
| **B-05** | Sponsor acceptance of KC-002 and the Principal's signature before any capital (C7) | **PM Pod B + the Principal** | **once, before any allocation** | **the signed acceptance in `logs/DECISION_RECORD.md`** |
| **B-06** | Vault sealed in the same session and UTC day as `open_hypothesis` (C8) | **PM Pod B + the Principal** | **once, at the seal** | **the `holdout_spec_sealed` event and the vault under `book/vaults/`** |
| **B-07** | Reconciliation breaks are filed verbatim and never repaired | **Execution & Operations** | **every Close & Reconcile, weekdays 17:15** | **the reconciliation note in the Daily Risk & P&L Pack** |

> ### **B-01's TRANSITION TO CLASS (a) IS NAMED, BECAUSE THE PRINCIPAL REQUIRED IT NAMED.**
>
> **KC-002 reverts to class (a) when Validation's harness kill-condition evaluator lands — specced this sprint, NOT YET DISPATCHED.** Until it does, *"a kill condition that can be defeated by not running it is not a kill condition"* (clause 5) **is a clause enforced by a person on a calendar.**
>
> **This seat wrote clause 5, defended it, and now labels it (b).** *"Defeatable by not running it"* cannot describe a signature-required clause, and **the honest repair is to name who runs it, how often, and what the running produces — rather than to hope.** The three fields above are the Principal's own, supplied with the mandate, and they are reproduced verbatim rather than paraphrased.
>
> **B-06 is the execution of a limit that is itself class (a).** The act is procedural; its violation is caught by A-12. Both are listed because a reader who saw only A-12 would not know a human has to do something on the day.

#### 10.11.4 CLASS (c) — thirty-four declared commitments

**Binding as a matter of record. Enforced by audit and adversarial review only. This is not a defect list and it is not a repair queue.** Most of these belong in a sealed document and could not sensibly be mechanised — **no harness will ever check that no winsorization was applied, and demanding one be built is not what the mandate asks for.**

| # | The commitment | Where |
|---|---|---|
| **C-01** | The `statement`'s content — the hypothesis as stated | §1, §21 |
| **C-02** | The `mechanism`'s content — the administered-constant / premium decomposition, the censoring, the crowding-cascade claim | §3, §21 |
| **C-03** | **The `falsifier`'s content — F-002 in full: three constructed series, four legs, α = 0.0013, the 1,800-bar floor, the joint false-survival rate of 1.3 × 10⁻⁴** | §5, §21 |
| **C-04** | **F-002's E2 — *"evaluated ONCE. No re-run with the corrected costs, no second look, no we also checked"*** | §5.5 |
| **C-05** | E3 — no forward search wearing a confirmation as a hat; `N_forward` logged as trials, no reported result selected from among them | §5.5 |
| **C-06** | **K3 = "exclude nothing"** — no date, asset or regime exclusion at any stage | §7.1, §21 |
| **C-07** | **"NO WINSORIZATION, OUTLIER REMOVAL OR RETURN CLIPPING anywhere at any stage"** | §6, §21 |
| **C-08** | `w_max = 1.0`; never long perp; the strategy never exceeds delta-neutral | §6, §18, §21 |
| **C-09** | The capacity screen at 20 × `P_notional` | §6.1, §21 |
| **C-10** | The ≤ 5%/day ADV participation cap per leg and the 15%-of-20-day-ADV liquidity floor | §18, §21 |
| **C-11** | `periods_per_year = 365` | §21 |
| **C-12** | The **ML-2 non-fitted assertion** — *"no number reported by this family is selected by comparing candidates"* | §10.7, §21 |
| **C-13** | **"Only `plateau_centroid_params` advances"** — the argmax is reported and never advanced | §10.5, §21 |
| **C-14** | The walk-forward **fixed-centroid** clause — no per-window re-selection | §10.7(c), §21 |
| **C-15** | **§7.2's escalation rule and its hard stop** — *"a post-result revision of any of K1–K7 TERMINATES THE LINE"* | §7.2, §14 cl. 2 |
| **C-16** | The K1–K7 menus and the 1-per-choice pre-commitment discount | §7.1, §7.2 |
| **C-17** | K7's declaration governing the **parameter** dimension, which C12's cadence sweep is structurally blind to | §7.1.1, §20 C12 |
| **C-18** | The four regime cells reported separately; **pooled figures never stand alone** | §21 |
| **C-19** | Raw **and** effective observation counts side by side | §21 |
| **C-20** | Gross and net with the breakeven cost, always (house rule 5) | §1, §21 |
| **C-21** | Hit rate **paired with** slugging ratio | §21 |
| **C-22** | **Alpha to `R_bench`** as the reported headline, not raw Sharpe | §21 |
| **C-23** | The **skew and expected-shortfall** line on every artifact | §21 |
| **C-24** | **The remaining nine of the eleven mandatory disclosure lines** (A-20 is the two that are not) | §21 |
| **C-25** | §16's disclosures — **venue survivorship and liquidation / venue-insolvency risk cannot be charged** and are disclosed on the face of every artifact. **§12's defect (d) is not repaired and this is where it lives** | §12.5, §16 |
| **C-26** | **`published_signal_haircut_applied = 0.50`, and everything derived from it — §5.4's pre-haircut `t(α) ≈ 6.0` and §19.3's order-20 composite. NO CODE PATH APPLIES IT; C5 is unruled** | §5.4, §11.6, §19.3, §21 |
| **C-27** | §10.8's **PASS / PARK / KILL dispositions** at ρ̂ = 0.034 / 0.15 / 0.30 *(the INSUFFICIENT-DATA branch is **A-18**)* | §10.8 |
| **C-28** | `ρ_plan = 0.10` as a planning assumption **that grades nothing** — (c) by its own text, and correctly so | §10.5.1 |
| **C-29** | **"No Stage 2 trial is spent on an unmeasured or stale `ρ̂`"** — `log_trial` reads no budget (I-132); **the retrospective FAIL is A-03 / A-07** | §10.5.2 |
| **C-30** | KC-002's anti-reinterpretation clauses **1, 2 and 4** *(clause 3's substance is **A-05**)* | §14 |
| **C-31** | KC-002's 187-day window and the absolute observation date `C` + 187 | §14 |
| **C-32** | §18's sizing table — USD 250,000 allocation, USD 125,000 per asset, gross USD 500,000, the BTC/ETH single-cluster treatment, no position exit | §18 |
| **C-33** | §12.8's **"No hand-rolled number, under any circumstance"** — the presets exist; **nothing refuses a literal float** | §12.8 |
| **C-34** | §19.3's pre-registered expectations themselves — (c) by nature, and correctly so | §19.3 |

> ### **TWO COMMITMENTS THIS SEAT TRIED TO PROMOTE TO (b) AND COULD NOT. THEY ARE THE WORKED EXAMPLES OF WHY (b) IS THE CLASS MOST LIKELY TO BE ABUSED.**
>
> **C-04 — F-002's "evaluated ONCE."** The three F-002 runs are logged trials, so a second evaluation would be **visible in the ledger afterwards**, and it is tempting to call that an artifact and file E2 as (b). **It is not.** The artifact is produced by the act being limited, not by any check on it, and **no seat and no cadence is named for asking the question.** Class **(c)** — discoverable by audit, prevented by nothing.
>
> **C-33 — "no hand-rolled number, under any circumstance."** The presets exist and using them is easy. **Nothing refuses a literal.** No executor, no cadence, no artifact. Class **(c)**, and the Charter's Seat-9 standing rule is a discipline rather than a gate.

> ### **WHAT THE REGISTER SAYS ABOUT THIS FAMILY, IN THREE LINES, WITHOUT SOFTENING AND WITHOUT OVER-CLAIMING.**
>
> **Thirty-four of sixty-one limits are enforced by nobody and nothing except audit and adversarial review — including F-002 itself, whose four legs and stated α sit in a field guaranteed only to be non-empty.**
>
> **Seven are enforced by named people on named schedules, and the most emphatic clause this document contains — KC-002's silence-kill — is one of them, pending an evaluator that is specced and not dispatched.**
>
> **Twenty are enforced by the engine, and two of those were enforced all along while this document said they were not (R26, R27).** **The mandate did not weaken this family. It told it, for the first time, which of its own sentences are load-bearing.**

---

## 11. GATE 0 (7) — HOLDOUT DEFINED AND LOCKED · and the R1–R4 fields

*§4.3(7). R1–R4 are binding under D-006.*

### 11.1 The holdout

| Field | Value |
|---|---|
| **Regime** | Option D (D-006). `C` = the pre-registration seal date (D-007). Holdout = `[C, G]`, forward, growing with wall-clock. |
| **`C`** | **The seal date.** Not fixed by this document. Fixed by Pod B's `open_hypothesis` call, on the same UTC day as the vault seal. |
| **In-sample** | `[2020-01-01, C]` for BTC/ETH — ~~**6.571 years**~~ **6.612 years, gap-free, measured, not estimated [S3-D-019, 2026-08-12 — see below].** ~~**[R34 · 2026-08-11] 6.571 years is measured to 2026-07-28. `C` is later than that and the true span at the seal is LONGER — so 6.571 is an UNDERSTATEMENT, and every margin quoted from it (§10.4's 0.43-year MinBTL margin above all) is understated with it.** **This is the one stale date in this document that runs FOR the family, which is precisely why four revisions passed over it. The figure is NOT re-derived here — re-deriving it is a computation a zero-trial budget does not authorize — and it is labelled rather than corrected.**~~ **[R37 · 2026-08-12 — MEASURED, AND R34's LABEL IS STRUCK AS UNEARNED.] The span is 6.571 years and it has not moved. Measured this session, `[2020-01-01, 2026-07-28] = 2400 days = 6.5710 years` (6.570977 at E-9's 365.2425; 6.570842 at 365.25), from a read-only `SELECT` over `book/pit.db`: BTC/USDT and ETH/USDT spot close, BTC and ETH perp close, and both funding series, common coverage `[2020-01-01, 2026-07-28]`, `ingest_ceiling` **zero rows** [all measured — 2026-08-12; last `knowledge_time` on every leg is 2026-07-29]. **R34 asserted the span grows with `C`. It does not: it grows with INGEST, and no bar has been ingested since 2026-07-29.** At `C = 2026-08-12` the declared in-sample window runs 15 days past the last bar on disk. **The figure is therefore EXACT today, not understated, and §10.4's 0.43-year MinBTL margin is exact with it.** Any larger span is contingent on §15 step 1's post-seal ingest actually running to `C` — **an assumption, not a measurement**, and R34 recorded it as though the margin were already banked. **This is a correction that runs AGAINST the family: it removes a claimed hidden margin. Filed I-176, MEDIUM.** [S3-D-019 · Head of Data & Infrastructure · 2026-08-12 — INGEST RAN; THE SPAN MOVED, RE-MEASURED.] Per dispatch S3-D-019, primary universe (BTC/ETH only — SOL excluded per R3, not ingested) taken to current via `castellan.loaders.fetch_ccxt_ohlcv` / `fetch_ccxt_funding` against `binance` (spot) and `binanceusdm` (perp + funding), through `PITStore`, raw, two-timestamp discipline. `book/registry.db` read 0 hypotheses / 0 trials before this ingest and reads 0 / 0 after it. `ingest_ceiling` held **zero rows** throughout and blocked nothing — the family remains unregistered, so there is no cutoff to enforce; this is not a bypass, there was nothing to bypass. Re-measured, same read-only `SELECT` methodology as R37: common coverage across all six legs is now `[2020-01-01, 2026-08-12] = 2415 days = 6.6120 years` at E-9's 365.2425 (6.611910 at 365.25) — **up from 2400 days / 6.5710 years, a growth of exactly 15 days: the same 15 days R37 measured the declared window as running past the last bar.** Last `knowledge_time` on every leg is now 2026-08-12. **Caveat, disclosed rather than smoothed over:** the terminal bar (`2026-08-12`) is every leg's currently-forming, unsettled UTC day — spot BTC volume 398.04 against a several-thousand-per-day trailing norm confirms it is partial — and should be expected to restate before day-close, on the identical pattern this same ingest run just produced and logged for the prior terminal bar (`2026-07-29`; see the restatement note below). Excluding the partial terminal day, the last fully-settled common bar is `2026-08-11`: `2414 days = 6.6093 years`. **Both figures are longer than R37's 6.5710, not shorter — reported whichever way the number moved, uncharacterized.** §10.4's `MinBTL(86, SR 1.0) = 6.14 yr` is an input unaffected by the available span and is not recomputed here; mechanically, the margin against it widens from 0.43 yr to **0.472 yr** (inclusive figure) or **0.469 yr** (settled-only figure) — this seat reports the arithmetic moves, and leaves whether/how to re-seal §10.4 on it to Validation. **Restatement, auto-logged under A4, reported verbatim:** ingesting `binanceusdm` perp OHLCV re-fetched the (already-partial) `2026-07-29` bar for both `BTC/USDT:USDT` and `ETH/USDT:USDT` and found it had settled differently — 3 fields each (`low`, `close`, `volume`), logged as two `data_restatement` events (`book/registry.db` event_id 2, 3). **Blast radius: none** — 0 hypotheses / 0 trials exist against this family or any other, so no trial's number is invalidated by this restatement; it is reported because A4 requires it reported regardless of blast radius, not because this one has teeth yet. Escalated to Validation the same session. Filed **I-190, MEDIUM** (restatement) and **I-191, MEDIUM** (span re-measurement / partial-terminal-bar caveat). Full detail: dispatch S3-D-019 return. |
| **Vault** | One `HoldoutVault` per (dataset, family) under `book/vaults/`, sealed with `family="funding-carry-conditioning-002"`, `cutoff=C`, `holdout_end_rule="open-ended, forward from C"`. **The passphrase is the Principal's and is never written to this repo, to Oracle, or to any file.** Acceptance 001 C-2 writes only a salted one-way verifier, which is what lets `acquire_once()` refuse a wrong-but-non-empty passphrase before any fetch (I-015). |
| **Sequencing, binding** | The vault is sealed **on or before the calendar day of `C`, in the same session as the `open_hypothesis` call.** P7 fails Gate 1 if the seal postdates `C` at UTC day granularity. |
| **Ingest ceiling** | `seal()` writes the ceiling into `PITStore`. ~~**The `binanceusdm` perp OHLCV ingest (§15 step 1) occurs after the seal and is bounded by it.** The spot and funding panels already on disk are bounded at `2026-07-28T23:59:59Z` [measured — DATA-INGEST-001 §1.2, §2], conservative against any `C ≥ 2026-07-28`.~~ **[S3-D-019, 2026-08-12 — SUPERSEDED, DISCLOSED RATHER THAN QUIETLY OVERTAKEN.] All six primary legs — spot close, perp close, AND both funding series — were ingested to current under direct dispatch, pre-seal, not per §15 step 1's planned post-seal sequencing.** There was still no ceiling to bound anything by (no cutoff exists until a seal writes one), so nothing was blocked and nothing needed lifting; this is not the D2 control firing, it is the control having nothing yet to fire on. All six legs are now bounded at `2026-08-12T00:00:00Z` on disk (the currently-forming, unsettled UTC day — see the In-sample row's caveat). **§15 step 1, as currently written, describes an ingest that has already happened, ahead of its planned position in the sequence — a sequencing-table finding, not corrected here because this dispatch does not authorize touching §15.** `book/pit.db :: ingest_ceiling` currently has **zero rows** [reconfirmed 2026-08-12], so there is still no collision to manage [measured]. |
| **Opened** | Once, at Gate 1, by Validation, with the Principal notified. A second look permanently retires it. |

### 11.2 R1 — holdout classification

> **`holdout_classification = FORWARD`.**

`[C, G]` postdates the pre-registration wall-clock in its entirety and therefore closes channels K1–K5 for that window. **R2 does not fire** — the in-sample is entirely historical, the holdout entirely forward, no mixed window exists to decompose. The R1 sentence required for a HISTORICAL classification is therefore not required and is not reproduced; its absence is deliberate and is stated so it is not read as an omission.

**What FORWARD does not fix:** **I-011**, the search embedded in the researcher before the freeze. It contaminates the in-sample, is invariant to where `C` sits, and cannot be fixed by waiting. §7's menu declaration is this family's only instrument against it, and §10.3 records that the instrument is only partly connected.

### 11.3 An unresolved §4.4 interpretive question, escalated rather than assumed

**Raised because assuming the favourable reading is exactly how a Gate 1 submission gets deferred, and because it bears on both families.**

Under Option D the holdout is forward and grows with wall-clock. Charter §4.4 requires **`Holdout window: most recent 25%, ≥ 12 months, opened once`** and, separately, **`Backtest length ≥ MinBTL(N) and ≥ 4 years`**. `evaluate_gate1` evaluates the length criterion on the **`oos_index` calendar span** [measured — G2/G4]. Three readings give three different earliest-Gate-1 dates:

| Reading of what `oos_index` carries | Earliest Gate 1 **[R34 · 2026-08-11 — RE-EXPRESSED AS FORMULAE. The three literals struck below were each computed at `C = 2026-07-28`, a premise false since 2026-08-04.]** | Basis |
|---|---|---|
| Purged k-fold OOS across the full in-sample; the forward holdout is a separate criterion | **`C` + 12 months** ~~≈ 2027-07-28~~ | The 12-month holdout floor binds; length is satisfied by the 6.571-year span |
| The forward holdout window itself, at the §4.4 ≥12-month floor | **`C` + 4 years** ~~2030-07-28~~ | The forward window must itself reach 4 years |
| The forward holdout at a strict **25% of total** | **`C` + ~2.19 years** ~~≈ 2028-10-05~~ for the 25% clause alone; later still if the 4-year length also binds | 6.571 / 3 = 2.19 years of forward window |

> **This seat does not resolve it and does not assume the first.** It is an admissibility and point-in-time-correctness question, which Charter Seat 3 owns and Seat 2 does not. **Routed to Validation at Gate 0 intake (§20, C4).** It bears identically on `forward-lag-001`, whose §6.3 reads the length criterion against the backtest span, and this seat flags that reading as unconfirmed rather than wrong.

### 11.4 R3 — the forward-window falsifier

R3 is mandatory only for a HISTORICAL classification. **This family carries one anyway**, for the same reason PREREG-001 does: a claim about data that did not exist when the claim was made is worth having regardless of classification.

| R3 field | Value |
|---|---|
| `forward_window_start` | ~~`2026-07-28` (= `C`; the seal is intended for today)~~ **[R33 · 2026-08-11] `C` — the UTC calendar day of the `open_hypothesis` call, computed at the instant of the act.** |
| `forward_window_min_length` | `12.0` — **units: MONTHS.** Charter §4.4's holdout floor. *Latent defect carried forward from PREREG-001 §10.3: the harness stores this as an unlabelled `REAL`. A float with no unit is a misreading waiting to happen.* **[R21] And nothing in the harness reads this field for a FORWARD family [measured] — no code compares it to an elapsed span and no code knows its unit.** |
| `forward_kill_condition` | **KC-002, §14, in full.** ~~Observation date **2027-01-31**, **absolute**~~ **[R32/R33 · 2026-08-11] Observation date `C + 187 days`, computed at sealing, ABSOLUTE thereafter** — it does not move with the sprint calendar, the ingest schedule, or the harness. |

> ### **[R33 · 2026-08-11] THIS TABLE WAS NAMED BY R23 AS A CHANGED CLAUSE AND R23 NEVER REACHED IT. FILED I-154, MEDIUM.**
>
> **R-004's R23 row lists its changed clauses as *"§11.4; §21 `forward_window_start`."*** §21 was changed. **§11.4 was not.** Both rows above stood un-struck until today, carrying **`2026-07-28`** and the parenthesis ***"the seal is intended for today"*** — a sentence R23's own text records as having been false **since 2026-08-04** — alongside the observation-date literal R32 has just found to be the second C1.
>
> **This is the fifth instance of `conforming-pass-did-not-reach-every-instance`** — R8(c) (three surviving instances of a superseded budget), R22 (§15's step table summing to 83), R25 (§10.10's 4/3/9 against its own 4/4/8), I-140 (the cost model at fourteen sites), and now this. **It is the first in which a revision row NAMES the site it failed to reach**, which is what makes it worse than the four before it: **a reader auditing R23 against its own clause list would tick §11.4 as done.**

### 11.5 R4(a) — model-prior provenance

Which seats originated or ratified each binding design field, with model and stated cutoff. Per **I-009** the firm does not know its own seats' training cutoffs and the authoritative reference does not publish them; every cutoff below therefore reads `unknown` and **that is itself the finding**, recorded rather than filled with a plausible number.

| Binding field | Originated by | Ratified by | Model | Stated cutoff |
|---|---|---|---|---|
| Hypothesis statement, mechanism (§3) | **Director of Research** | — | Opus | unknown [assumed] |
| The §3.3 argument that the unconditioned carry is factor beta under §5.4 | **Director of Research**, on Charter §5.4 as written | — | Opus / human (Charter) | unknown [assumed] |
| Falsifier F-002 (§5) | **Director of Research** | — | Opus | unknown [assumed] |
| Conditioning declarations ~~K1–K6~~ **[R9 · 2026-08-05] K1–K7** and their menus (§7) — **K7 was declared at R5 and this provenance row was not extended with it** | **Director of Research** | **the Principal** (the rider requiring them) | Opus / human | unknown [assumed] |
| The §7.2 pre-commitment rule and its escalation | **Director of Research** | — | Opus | unknown [assumed] |
| Universe, sizing rule, parameter centres (§6) — **[R41 · 2026-08-25] the phrase "parameter centres" claimed a provenance for objects that did not exist until today; `k` = 0.5, `d` = 1.0 and `band` = 0.10 are named at §6.2 and derived at `DIR-RESTATE-001` §14** | **Director of Research** | — | Opus | unknown [assumed] |
| Trial budget and the ~~`N ≤ 110`~~ **[R8 · 2026-08-05] `N ≤ 109`** ceiling (§10.4–10.5) | **Director of Research**, on `castellan.stats` output; **[R8] the ceiling's correction from 110 to 109 originates with Quant Validation** [cited — `VALIDATION-RULING-004` §2.2, §12] | Quant Validation | Opus | unknown [assumed] |
| KC-002 (§14) | **Director of Research**, adopting KC-001's shape (Devil's Advocate, REDTEAM-001 §B.5) including the silence clause | **requires the Principal's signature before any capital** | Opus / human | unknown [assumed] |
| `CRYPTO_PERP_TAKER` audit (§12) | **Director of Research** [measured from source] | — | Opus | unknown [assumed] |
| The redirect of Pod B compute to this mandate | **Director of Research** (PREREG-001 §17.2 item 4) · **the Principal** (approved) | — | Opus / human | unknown [assumed] |
| Holdout regime | Validation (Rulings 001, 002) · **the Principal** (D-006 Option D, D-007 `C` definition) | — | Opus / human | unknown [assumed] |

**The origin line, stated plainly because I-025 asks for it:** every binding design field in this document except the holdout regime and the rider originates with **Seat 2**. It is the firm's first such record.

### 11.6 R4(b) — the published-signal haircut

> **`published_signal_haircut_applied = 0.50`. The presumption is accepted. No exemption is sought.**

Ruling 002 R4(b) makes a hypothesis generated from an LLM seat's priors presumptively an edge derived from published research, carrying §4.6's 50% haircut unless the sponsor argues at Gate 0 that the mechanism is not publicly documented and Validation accepts.

**This seat does not make that argument, and states why so the decision is auditable:**

1. **The carry premium is unambiguously published** — the Charter cites it in its own Appendix C.
2. **The conditioning claim is also plausibly published.** The nearest analogue is the FX carry-crash literature and its standard prescription, and this family's sizing rule is that prescription transposed. **Claiming novelty here would be a claim this seat does not believe**, and spending Validation's scarcest unit on it would be waste.
3. **It bites, and this seat states the cost rather than minimizing it.** §5.4: post-haircut Gate 1 clearance requires a pre-haircut `t(α)` of roughly 6.0. **That is the largest single hurdle this family faces and it is accepted deliberately, not conceded.**

**Live defect noted:** **I-019** records that R4(a)/(b) have schema and **no computation attached**. The `0.50` recorded here is a declaration, not an enforced deduction, until I-019 closes — and §5.4 records that even its *point of application* is unspecified.

---

## 12. THE §4.6 COST STACK — and the audit of `CRYPTO_PERP_TAKER`

*§4.6: costs from `castellan.costs.CostModel` presets or Principal-approved additions. No hand-rolled cost numbers, anywhere, including the paper book. Charter Seat 9 standing rule: **researchers may not hand-roll transaction costs. There is one cost library. Every strategy uses it.***

**The dispatch asked whether the crypto preset is also wrong. It is, and it is worse than I-023.**

> ### **[R26 · 2026-08-10 · THE WHOLE OF §12.1–§12.3 AND §12.6 DESCRIBES A COST MODEL THAT NO LONGER EXISTS. RETAINED AS THE RECORD OF THE DEFECT AND ITS DIAGNOSIS; SUPERSEDED AS A STATEMENT OF HARNESS FACT.]**
>
> **`VALIDATION-RULING-003`'s own header names its target: *"Blocks: `research/PREREG-002-crypto-funding-basis.md` condition precedent C1; I-034."*** The ruling specified the repair with **nineteen acceptance tests authored before implementation**; `DATA-IMPL-004` §5–§6 implemented it and reports ***"All nineteen T-cases … are implemented and pass with the assertions Validation authored"*** [cited]. **The state of `harness/castellan/` today** [measured, this session]:
>
> ```python
> CRYPTO_PERP_TAKER = CostModel(
>     name="crypto_perp_taker", commission_bps=5.0, half_spread_bps=1.0,
>     impact_y=1.0, periods_per_year=365,
>     # No funding term (Ruling 003, I-034): funding is a signed cash flow
>     # and is accrued in the engine from the realized `pit_funding_panel`
>     # series, never as a scalar rate here.
> )
> CRYPTO_SPOT_TAKER = CostModel(          # D-013 §1, Principal-authorized
>     name="crypto_spot_taker", commission_bps=10.0, half_spread_bps=2.5,
>     impact_y=1.0, periods_per_year=365)
> ```
>
> | §12 defect | Status [measured] |
> |---|---|
> | **(a)** the sign of funding is inverted and its base doubled | **REPAIRED** — the field is deleted, not zeroed. Ruling 003's A1: *"zeroing is not enough — the field must be removed"* |
> | **(b)** funding is a constant, and this family's signal is its variation | **REPAIRED** — realized per-print accrual from `pit_funding_panel` |
> | **(c)** a two-legged strategy, a one-legged cost model | **REPAIRED** — `CRYPTO_SPOT_TAKER`, Principal-authorized |
> | **(e)** the 2× cost-robustness test stresses the error | **REPAIRED** — T-16: `scaled(2.0)` leaves `carry_accrual` **bit-identical**; `carry.py` is the sanctioned stress path |
> | **(d)** no field can charge liquidation or venue-insolvency risk | **NOT REPAIRED. STANDS.** Ruling 003 §4 declines to invent a number [cited]. **Class (c) — C-25 in §10.11.4, disclosed on the face of every artifact** |
>
> **This is R19(b)'s defect class running in the conservative direction, which is why R-001 through R-004 all passed over it.** Filed **I-140, HIGH** — **HIGH because §14's condition precedent has a dated, mechanical consequence one day away.** ~~**This seat records the measurement and conforms its own document; it does NOT close I-034 and does NOT close C1**, both of which route to `quant-validation → head-of-data-infra`.~~
>
> ### **[R29 · 2026-08-11] I-034 IS CLOSED AND C1 IS DISCHARGED — BY THE PRINCIPAL, NOT BY THIS SEAT.**
>
> **Closed 2026-08-11, satisfied 2026-07-29, discovery credit R-005.** Evidence: commit **`875874f`**, message ***"Ruling 003 implemented: carry accounting, 139/139. Closes I-034, I-037, I-039"*** [cited]. **The satisfaction date is the work's date and the recording date is today, and the record states both** — nothing is backdated, which is the distinction between this and the I-046 inversion.
>
> **The finding inside the finding, and the CIO supplied the fact this seat did not have: the commit message itself announced the closure.** The work landed, the commit said *"Closes I-034"*, and `logs/ISSUE_LOG.md` read *"open — blocking execution of PREREG-002"* for **thirteen days**, while §14's condition precedent stood ready to downgrade this family permanently. **It is the fourth instance of I-092's class and the first with a dated consequence.**
>
> **The residual is retained and is NOT swept up with the closure: defect (d) stands as class (c), C-25.** `CostModel` has no field that can charge liquidation or venue-insolvency risk, `VALIDATION-RULING-003` §4 declines to invent a number, and **it is not a condition precedent because there is nothing to wait for.**

### 12.1 The preset as shipped **[R26 · 2026-08-10 — the block below is the preset as shipped ON 2026-07-28. It is NOT the preset as shipped today; the current source is quoted in the R26 note above.]**

```python
CRYPTO_PERP_TAKER = CostModel(
    name="crypto_perp_taker",
    commission_bps=5.0,          # taker fee, major venue
    half_spread_bps=1.0,
    impact_y=1.0,
    funding_bps_annual=1095.0,   # 0.01%/8h baseline against structural longs
    periods_per_year=365,
)
```
[measured — `harness/castellan/costs.py`]

### 12.2 Defect (a) — **the sign of the strategy's central term is inverted, and its base is doubled**

`CostModel.carry_per_bar(long_notional, short_notional)` returns

```
short · borrow_bps/ppy  +  (long + short) · funding_bps/ppy
```

and `run_backtest` computes `net = gross − (trade_cost + carry)` [measured — `engine.py`]. Funding is therefore **applied to gross notional** and is **always a cost**. There is no sign, no direction, and no way to express a receipt.

On this family's position — long 1.0 spot, short 1.0 perp — gross is **2.0**:

| Quantity | Value | Provenance |
|---|---:|---|
| `carry_per_bar(1.0, 1.0)` | `0.0006` per day | [measured] |
| Annualized | **−21.9%/yr charged** | [measured — `0.0006 × 365`] |
| What the strategy actually **receives** at the Charter's own baseline | **+10.95%/yr** on 1.0 unit of short-perp notional | [cited — Charter Seat 7] |
| `carry_per_bar(0.0, 1.0)` — a naked short perp, no spot leg | **−10.95%/yr charged** | [measured] |

> **The preset applies −21.9%/yr where the economics deliver +10.95%/yr. The sign is inverted and the magnitude doubled — a 32.85-point-per-year error on a strategy whose entire claimed edge is 10.95 points per year.**
>
> This is not conservatism. A conservative error makes a good strategy look mediocre. **This error makes the strategy's defining revenue line into its largest cost, deterministically, in every backtest, at three times the size of the thing being measured.** Any net number produced by this family under the preset as shipped is not merely wrong — it is wrong in a way that guarantees a KILL verdict regardless of the market.

### 12.3 Defect (b) — funding is a constant, and this family's signal is its variation

`funding_bps_annual` is a scalar. `carry_per_bar` accepts no time-varying input. **The 7,203 realized funding prints per asset sitting in `book/pit.db` cannot enter the P&L through the sanctioned cost path at all** — and the entire hypothesis is a claim about the *variation* of that series.

**The only admissible route is to move funding out of the cost stack and into the return series** — construct a synthetic perp total-return leg from the PIT-consumed perp price and the PIT-consumed funding prints, set `funding_bps_annual = 0.0` so it is not double-counted with the wrong sign, and let the position return carry it.

> **This seat flags that construction as the thing it is least comfortable with in the whole design, and refuses to authorize it unilaterally.** It relocates a cash flow from the cost stack — which Seat 9 owns and researchers may not touch — into the price panel, which researchers build. **That is exactly the boundary the standing rule exists to defend, and a Director of Research quietly redrawing it because the alternative is inconvenient would be a governance failure larger than the arithmetic it fixes.** ~~It is condition precedent **C1** and it is Validation's to specify, not this seat's to implement.~~ **[R29 · 2026-08-11] SPECIFIED, IMPLEMENTED, AND DISCHARGED. Validation specified it at `VALIDATION-RULING-003` and chose neither of the two constructions this paragraph offered: funding is accrued in the ENGINE from the realized `pit_funding_panel` series as a signed cash flow, `CostModel` carries no funding field at all, and the boundary this paragraph refused to redraw was redrawn by the seat that owns it. `DATA-IMPL-004` §5–§6 landed it 2026-07-29 with all nineteen Validation-authored T-cases green [cited]. C1 is DISCHARGED; I-034 is CLOSED (Principal, 2026-08-11).** The paragraph is retained because the boundary argument it makes is correct and was the reason this seat declined to act unilaterally — **which is the part that generalizes, and the part worth keeping.**

### 12.4 Defect (c) — a two-legged strategy, a one-legged cost model

`run_backtest` accepts **one** `CostModel` for the whole price panel. This family trades a **spot** leg and a **perp** leg with different fee schedules, and there is no `CRYPTO_SPOT_TAKER` preset — the preset list is `US_EQUITY_LARGE`, `US_EQUITY_SHORT`, `CRYPTO_PERP_TAKER`, `POLYMARKET` [measured].

Costing both legs at the perp preset's 5.0 bp commission understates the spot leg, whose taker fee on a major venue is materially higher [assumed — published exchange schedule, **not verified this session**]. Per-side cost under the preset is **6.0 bps** (5.0 commission + 1.0 half-spread) [measured], so a full two-leg round trip is **24 bps** on the preset — and the true figure is higher by the spot/perp fee differential, in a known direction.

**`half_spread_bps = 1.0` is also universe-dependent:** plausible for BTC perp, optimistic for SOL, ~~which is a further reason K4 puts SOL secondary~~ **[R3 · 2026-08-04] which is now moot as a universe question — SOL is dropped (K4 option 4) — but is retained here because the same universe-dependence argument applies to any future widening of K4 and should not have to be rediscovered.**

### 12.5 Defect (d) — no field can charge the largest risk in the mandate

`CostModel`'s fields are commission, half-spread, impact, borrow, funding, periods-per-year. **Nothing charges for venue insolvency, forced liquidation, or margin-call funding.** This is structurally identical to **I-023(b)** — *"`CostModel` has no field capable of expressing oracle or resolution risk… the paper book will systematically over-report net P&L because it cannot be charged"* — with liquidation-and-insolvency substituted for resolution risk.

**The consequence is the same and its sign is known: the paper book will over-report this family's net by an unmeasured amount.**

### 12.6 Defect (e) — the 2× cost-robustness test stresses the error

`CostModel.scaled(2.0)` multiplies `funding_bps_annual` along with everything else: `1095.0 → 2190.0` [measured]. **Charter §4.4's cost-robustness criterion — "retains t ≥ 3.0 at 2× modelled costs" — therefore doubles the phantom drag to −43.8%/yr for any funding family.** The criterion is not testing cost robustness; it is stress-testing a sign error. **Filed here because a Gate 1 criterion that measures the wrong thing reads as satisfied in every audit that checks the criterion was run.**

### 12.7 Verdict on the preset, and the comparison the dispatch asked for

> **`CRYPTO_PERP_TAKER` is NOT fit for purpose for any funding-carry family, and the defect is more severe than I-023.**
>
> | | I-023 (`POLYMARKET`) | This finding (`CRYPTO_PERP_TAKER`) |
> |---|---|---|
> | Nature | A cost is **misstated in magnitude** — a bps constant where the true cost is price-proportional | A **revenue is recorded as a cost**, at double the base |
> | Size | ~2.5× understated at 20¢, ~5× at 10¢ [cited — I-023(a)] | **32.85 points/yr wrong**, on an edge of 10.95 points/yr [measured] |
> | Direction | Optimistic — flatters the strategy | Pessimistic in sign, but **deterministic and total** — it guarantees a false KILL |
> | Missing risk field | resolution / oracle risk [cited — I-023(b)] | liquidation / venue insolvency — **the same gap** |
>
> **Filed as a new HIGH-severity Issue Log candidate: `the crypto perp cost preset charges funding on gross and cannot express it as a receipt`. Owner: head-of-data-infra → quant-validation. It is the CRO's log to write; this seat raises it.**

**Two things the preset gets right, recorded so the finding is not read as a rejection of the whole preset:** `periods_per_year = 365` is correct for a 24/7 daily-bar crypto strategy, and `impact_y = 1.0` matches Charter §4.2's `IMPACT_PREFACTOR_Y = 1.0` exactly [measured]. **The trading-cost half of the preset is usable; the carry half is not.**

### 12.8 What this family will use

| Component | Source |
|---|---|
| Commission and half-spread, both legs | ~~`CRYPTO_PERP_TAKER` as shipped, **plus** a Principal-approved `CRYPTO_SPOT_TAKER` addition if C1's specification calls for one.~~ **[R29 · 2026-08-11] `CRYPTO_PERP_TAKER` on the perp leg and `CRYPTO_SPOT_TAKER` on the spot leg — BOTH EXIST TODAY** (`CRYPTO_SPOT_TAKER`: `commission_bps = 10.0`, `half_spread_bps = 2.5`, D-013 §1, Principal-authorized) [measured — `costs.py`]. `run_backtest` accepts a `dict[str, CostModel]` mapping asset → model (Ruling 003 §3.4) and **raises rather than defaulting on an omitted traded column** [measured]. **The conditional is spent.** **No hand-rolled number, under any circumstance.** |
| Impact | `CRYPTO_PERP_TAKER.impact_y = 1.0`, `impact_exponent = 0.5`, on measured ADV from the `volume` field. |
| **Funding** | ~~**Realized per-print funding from `book/pit.db`, routed per Validation's C1 specification. `funding_bps_annual` set to `0.0` in the cost model to prevent double-counting.**~~ **[R29 · 2026-08-11] Realized per-print funding from `book/pit.db` via `castellan.data.pit_funding_panel`, passed to `run_backtest(funding_panel=...)` and accrued in the ENGINE as a signed cash flow `−(positions × funding_panel)`. There is no `funding_bps_annual` to zero — the field was DELETED, not zeroed (Ruling 003 A1: *"zeroing is not enough — the field must be removed"*) [measured].** Carry stress is `carry.py`'s sanctioned path — `CarryScenario` REALIZED / ZERO / SIGN_INVERTED, `shift_carry_panel`, `tail_bootstrap_carry` — **never `CostModel.scaled(m)`, which leaves carry bit-identical by construction (T-16).** |
| Liquidation / venue risk | **Cannot be charged.** Disclosed on the face of every artifact (§16). |

---

## 13. INTENDED INITIAL ALLOCATION — stated honestly, with its materiality consequence

> **Intended initial allocation: USD 250,000.** Order hundreds of thousands.
> **`P_notional` = USD 125,000 per asset** across BTC and ETH. **Gross at `w = 1.0` is USD 500,000** — the position has two legs and the gross is double the allocation, which is stated here rather than discovered at the Risk Meeting.

### 13.1 Why it is larger than PREREG-001's $50,000, and why that is honest rather than ambitious

| Assumption | Allocation | §4.4 capacity requirement | Measurable? |
|---|---:|---:|---|
| `forward-lag-001` (PREREG-001 §11) | $50,000 | $500,000 | **Yes in principle, no in fact** — C-002 rules capacity is an **ADV-plus-impact** construction, not a book-depth one, so I-026 does not sink it; but Polymarket has no ADV series in `pit.db` and no loader [measured] |
| **This family** | **$250,000** | **$2,500,000** | **Yes, and the instrument is on disk** — the `volume` field of the spot panel, with perp volume arriving at §15 step 1 |

**Validation's C-002 ruling is what makes this straightforward and it is cited rather than re-derived** [cited — `VALIDATION-GATE0-001` §2]: *"§4.4 capacity does NOT require order-book depth. The ADV-plus-impact-model route is not merely permissible — it is the construction the Charter already specifies."* **This family's capacity criterion is therefore evaluated from ADV and `castellan.costs` impact, both of which it has** — `ADV_PARTICIPATION_MAX = 0.05` and `IMPACT_EXPONENT = 0.5` are Charter §4.2 constants and no new instrument is needed.

**The allocation is therefore set by risk appetite rather than by evidentiary convenience.** PREREG-001 was driven toward $50,000 partly because a small number was the only way to make a hard-to-evaluate capacity criterion arguable. **$2.5M of daily ADV on BTC and ETH perpetuals is expected to clear comfortably** [inferred — **not measured**; the measurement is §15 step 4 and it is cheap].

### 13.2 What it costs — materiality, stated now rather than discovered later

| Measure | Value |
|---|---|
| $250,000 as a share of Pod B's $2,000,000 | **12.5%** |
| $250,000 as a share of the firm's $10,000,000 paper book | **2.5%** |
| Firm contribution at a 6%/yr net sleeve return | $15,000/yr = **~15 bp of firm NAV** [inferred — arithmetic on a stated assumption, not a forecast] |
| Firm contribution at a 12%/yr net sleeve return | $30,000/yr = **~30 bp of firm NAV** [inferred] |

> **15–30 bp of firm NAV. Better than PREREG-001's 12–25 bp, and still not a firm-moving number.**

### 13.3 The leverage trade, named because it is the honest shape of this family's materiality problem

**Delta-neutrality is what makes the sleeve safe and is the same thing that makes it immaterial.** Hedging out the direction hedges out most of the volatility; a low-volatility sleeve at 2.5% of capital cannot move the firm's return. The only route to materiality is **leverage on the short-perp leg** — and leverage on the short-perp leg is exactly the operation that converts a fat left tail into a solvency event, because it is the margin on that leg that a liquidation cascade attacks.

> **The strategy is immaterial unlevered and uninvestable levered. The interesting region is in between, and locating it — not harvesting the carry — is what this research is actually for.** If F-002 leg (ii) shows the conditioning genuinely reduces the tail, then the levered version becomes discussable at a specific leverage, and that number is the family's real deliverable. If leg (ii) fires, no leverage is defensible and the unlevered version is not worth the firm's compute.

**This seat states that trade at pre-registration rather than discovering it at Gate 1**, per D-009's instruction that the materiality consequence be stated and not found later.

---

## 14. KC-002 — THE BINDING KILL CONDITION

*Charter §4.3(2) / Ruling 002 R3 / D-009 §C. Written to KC-001's shape, including the silence clause, which is not softened by one word.*

> ### KC-002 — funding-carry conditioning family
>
> **Sponsor:** PM Pod B. **Accepted by the sponsor in writing, and signed by the Principal, before any capital — paper or real — is allocated to this family.**
>
> ~~**Observation date: 2027-01-31**, being 187 days after an intended pre-registration seal `C = 2026-07-28`. **The date is fixed and does not move** with the sprint calendar, the ingest schedule, the cost-model repair, or the harness. If the seal slips, the window shortens; the date does not extend.~~
>
> ### **[R32/R32(b) · 2026-08-11 · THIS IS A CHANGE OF MEANING AND IS NOT PRESENTED AS CONFORMANCE.]**
>
> **Observation date = `C + 187 days`, computed at sealing, ABSOLUTE thereafter.** It does not move with the sprint calendar, the ingest schedule, the cost-model repair, or the harness. **Once written at the seal it does not extend for any reason.**
>
> **Why the struck sentence had to go, and the reason is not tidiness.** `C = 2026-07-28` **is a false premise** — §20.1 recommended against sealing that day on 2026-08-04 and the seal has not occurred. **The sealed field at §21 has always governed by the formula**, reading *"Observation date = `C + 187 days` … the DRAFTED DATE IS NOT BINDING — the formula is"*, and §15 step 8 computes *"through `C + 187 days`."* **§14's prose was the lone dissenter and it stated a different rule, not a stale instance of the same one:** under it the window is `[C, 2027-01-31]` and **shrinks with every day of slippage.** At a seal on 2026-08-12 that is **172 days, 8% short of 187**, against **clause (b)'s unchanged 30-conditioning-day threshold — which was calibrated against 187 days** and against *"~184 daily bars and ~552 funding prints."* **A kill condition tightened by scheduling rather than by design is a kill condition nobody chose.**
>
> **Direction of the repair, stated because R-004's payload rule fixes it:** *"anywhere this document's prose and that payload could diverge, the payload is what gets passed to `open_hypothesis`."* **The prose is conformed to the field. The field is not conformed to the prose.**
>
> **Put to C2 as C13(k). Validation may refuse this and require `2027-01-31` sealed as drafted** — in which case the family accepts a window shortened by however long the seal took, KC-002 clause (b) becomes correspondingly harder, and **this seat writes the KILL memo on the day without argument.**
>
> **Why 187 days and not 95.** KC-001's window suits an event-driven family that either generates signals or does not. This family is continuous and always-on; 187 days yields ~184 daily bars and ~552 funding prints — **enough to measure expectancy and to count conditioning events, and deliberately not enough to measure a Sharpe.** KC-002 tests neither Sharpe nor statistical significance, and clause (b) is what stops it degenerating into "wait longer."
>
> **On that date, Validation computes — from `book/registry.db` and `book/pit.db` alone, on the frozen pre-registration, over the forward window ~~`[C, 2027-01-31]`~~ [R32] `[C, C + 187 days]`:**
>
> **(i)** cumulative **net** return of the sealed conditioned strategy `R_strat`, after the full §4.6 cost stack at **1× modelled costs** using `CRYPTO_PERP_TAKER` **as repaired under condition precedent C1**;
> **(ii)** the count of days on which the sealed conditioning moved the position's notional by more than **±25%** from the benchmark's constant notional; and
> **(iii)** the sealed strategy's **worst single-day net return** in the window, expressed as a fraction of allocated sleeve notional.
>
> ### The family is KILLED — registry marked TERMINATED, no further trials, no Gate 1 submission ever — if ANY of:
> ### (a) cumulative net return ≤ 0; OR
> ### (b) fewer than 30 days on which the conditioning moved notional by more than ±25%; OR
> ### (c) any single day on which the net loss exceeds 4.0% of allocated sleeve notional.
>
> **Clause (b) is not a technicality and must not be waived as one.** It kills on **the conditioning never having conditioned.** If the state variable did not move the position, then whatever the P&L was, it was the benchmark's — the family is the crypto carry factor by construction, and Charter §5.4 pays nothing for it. This is the outcome nobody plans for and which otherwise becomes "the signal will fire eventually" indefinitely. It is KC-001 clause (b)'s logic — kill on insufficient signal — transposed to a continuous strategy.
>
> **Clause (c) is the tail clause and it exists because the backtest cannot see it.** A delta-neutral pair at 1× notional should not lose 4% of allocation in a day; if it does, either the hedge failed or a basis dislocation ran through it, and both are the intraday risk that daily bars structurally cannot measure (§16). **4.0% is Charter §5.2's Tier-2 formal-notice threshold, applied to a single day at the sleeve level rather than to a drawdown at the pod level** — a deliberate borrowing, and stated as such. **The firm should not learn how large this tail gets by holding on through it.** At sleeve scale a 4% single-day loss is $10,000, or 10 bp of firm NAV, which is trivial in money and decisive in information; the kill is for the information.
>
> **Anti-reinterpretation clauses, binding:**
> 1. **No re-parameterisation.** All three quantities are computed on the **sealed** specification — not a tuned variant, not the plateau centroid discovered later, not a subset, not "the version we would have run."
> 2. **No post-`C` exclusions.** Any regime filter, date exclusion, asset exclusion, venue change, or universe restriction not present in the sealed pre-registration is inadmissible in this computation. **This clause is the §7 declaration made enforceable**, and any of ~~K1–K6~~ **[R9 · 2026-08-05] K1–K7** revised in order to change this computation's answer is refused by P3 and, if pursued, ~~opens a successor family at the §7.2 escalated `n_inherited`~~ **[R9] TERMINATES THE LINE — §7.2's replacement records that the escalated successor registration is refused by the harness today (I-053), that the sealed continuation is `n_inherited = (menu size − 1) × chain_total` if and when that repair lands, and that declaring a lower figure in order to satisfy the guard is forbidden by name.**
> 3. **No restatement as continuation.** A hypothesis restated after ~~2027-01-31~~ **[R32] the observation date `C + 187 days`** is a **new family**, ~~opened with `n_inherited ≥` the killed family's final `n_trials` plus its own~~ **[R9 · 2026-08-05] opened with `predecessor_family = "funding-carry-conditioning-002"` and `n_inherited` = its OWN new search only**, and inherits neither this family's schedule, nor its allocation, nor its narrative. **[R9 — the struck form was both redundant and unexecutable, from the same misreading as §7.2's head (ii).]** `family_stats` sums `n_inherited` and logged trials **transitively across `predecessor_chain`** [measured — `registry.py`], so setting `predecessor_family` carries this family's entire final count into the successor's denominator **automatically**; re-declaring it in `n_inherited` double-counts it, which is exactly what `InheritedCountDoubleCountError` refuses. **The clause's intent — that a restatement cannot escape this family's trial count — is delivered by `predecessor_family` alone, and is delivered better, because the harness enforces it instead of the sponsor asserting it.**
> 4. **Kill is automatic on the date.** It requires no meeting, no vote, and no CIO concurrence. **It is not appealable to the CIO.** Only the Principal may reverse it, in writing, logged in `logs/DECISION_RECORD.md` as an Appendix-B-#4 override with its reason on the face of the record and reported in the next Monthly Letter.
> 5. **SILENCE IS A KILL.** If the computation is not performed on ~~2027-01-31~~ **[R32 · 2026-08-11 · THE SECOND C1. THE LITERAL IN THIS CLAUSE MADE THE KILL CERTAIN — see the note below KC-002.]** **the observation date `C + 187 days`** — **for any reason, including that the perp price series was never ingested, that the cost model was never repaired, that Validation had no unit available, or that the harness was not ready — the family is killed by default.** A kill condition that can be defeated by not running it is not a kill condition. **This clause is copied deliberately from KC-001, where the Devil's Advocate predicted it would be the one someone tried to soften. It has not been softened here either, and the seat that would benefit most from softening it is the seat that wrote it.**

~~**Condition precedent, separately binding:** the **C1 cost-model repair** (§12) is specified by Validation and implemented by **sprint close, 2026-08-11**. **If unresolved by that date, the family is ADMITTED-AS-EXPLORATORY only and remains so until it is resolved** — because until then no net number this family produces means anything, and clause (a) would be computing a −21.9%/yr artifact.~~

> ### **[R26 · 2026-08-10 · STRUCK. THE CONDITION IS SATISFIED AND THE DOWNGRADE MUST NOT FIRE. THIS IS THE SITE THAT MADE I-140 A HIGH.]**
>
> **The C1 cost-model repair is specified AND implemented.** Specification: `VALIDATION-RULING-003`, whose header names *"Blocks: PREREG-002 condition precedent C1"* [cited]. Implementation: `DATA-IMPL-004` §5–§6, ***"All nineteen T-cases are implemented and pass"***, landed **2026-07-29** [cited], verified in source this session — `CRYPTO_PERP_TAKER` carries no funding term, `CRYPTO_SPOT_TAKER` exists under D-013 §1, `carry.py` supplies the sanctioned stress path, `scaled(m)` leaves carry bit-identical [measured].
>
> **HAD THIS SENTENCE BEEN SEALED AS WRITTEN, THIS FAMILY WOULD HAVE BEEN DOWNGRADED TO ADMITTED-AS-EXPLORATORY ON 2026-08-11 ON A PREMISE THAT WAS FALSE ELEVEN DAYS BEFORE THE DEADLINE** — and ADMITTED-AS-EXPLORATORY is *"pre-declared ineligible for Gate 1"* (Charter §4.3). **A family that spent three sprints earning an ADMITTED recommendation would have lost it to a stale sentence, permanently, under P7.**
>
> **The condition precedent is retained in one narrower form, because one head of §12 is genuinely not repaired:** **`CostModel` still has no field that can charge liquidation or venue-insolvency risk** (§12.5 defect (d)). **That is class (c) — C-25 — it is disclosed on the face of every artifact, and Validation Ruling 003 §4 declines to invent a number for it.** It is **not** a condition precedent, because there is nothing to wait for.
>
> **KC-002 clause (i) is unaffected in every word.** It reads *"using `CRYPTO_PERP_TAKER` as repaired under condition precedent C1"* — and the preset **is** as repaired. **No clause of KC-002 moves. R-005 does not soften this kill condition by one word, and clause 5 binds this seat exactly as it did before.**
>
> **[R29 · 2026-08-11] AND C1 IS NOW DISCHARGED OUTRIGHT.** I-034 CLOSED by the Principal 2026-08-11, satisfied 2026-07-29 (commit `875874f`, *"Closes I-034"*), discovery credit R-005. **The condition precedent does not fire, is not extended, and is gone from §1's and §19's conditional.** The residual — defect (d), no `CostModel` field for liquidation or venue-insolvency risk — **stands as class (c), C-25, and is not a condition precedent because there is nothing to wait for.**

> ### **[R32 · 2026-08-11 · THE SECOND C1 — AND IT TERMINATES WHERE THE FIRST ONLY DOWNGRADED. FILED I-153, HIGH.]**
>
> **The dated-clause sweep this dispatch ordered found a second one, and the CIO was right to assume there would be. It is inside `forward_kill_condition` itself — the field that carries KC-002 into the registry — and it is a contradiction between that field's opening sentence and its own clause 5.**
>
> | | Text, as it stood |
> |---|---|
> | **Field opening** | *"Observation date = `C + 187 days`… (Drafted against an intended `C` = 2026-07-28, giving 2027-01-31; §20.1 recommends NOT sealing that day, so the executed value is whatever `C + 187 days` resolves to and **the DRAFTED DATE IS NOT BINDING — the formula is**.)"* |
> | **Clause 5** | *"**SILENCE IS A KILL** — if the computation is not performed **on 2027-01-31** for ANY reason … **the family is killed by default.**"* |
>
> **Read as sealed, clause 5 terminates this family with certainty.** The observation date the field itself schedules is `C + 187 days`. **At any seal after 2026-07-28 that date falls LATER than 2027-01-31.** On 2027-01-31 the computation will not have been performed — **it is not due** — and clause 5 fires: **registry TERMINATED, no further trials, no Gate 1 submission ever, automatic, not appealable to the CIO.**
>
> **Strictly worse than I-140's condition precedent, on two heads.** I-140's clause **downgraded** the family to ADMITTED-AS-EXPLORATORY; **this one kills it.** I-140's clause fired on a premise that *happened* to be false; **this one fires on a premise that cannot be satisfied.** **A kill condition written to be undefeatable had become one that cannot be survived** — and P7 would have made it permanent on the day of the seal.
>
> **And nothing evaluates it.** I-135 stands unchanged: **no harness path evaluates a kill condition on any date, for any family**, and for a FORWARD classification `forward_kill_condition` is not even presence-checked [measured]. The clause is **class (b)** — executor the Principal, cadence the weekly Friday ritual, artifact the pasted evaluation — **and a Principal executing it correctly, reading the sealed text, would find the family dead.**
>
> **THE REPAIR RUNS IN THIS FAMILY'S FAVOUR, AND THAT IS WHY IT IS STATED AT THIS VOLUME AND WHY THE RULING IS NOT THIS SEAT'S.** The three `2027-01-31` literals in the field body are conformed to `C + 187 days` — **the rule the same field's opening already declares and which §15 step 8 already computes.** No new rule is introduced and no threshold moves. **But a sponsor deleting a clause that terminates its own family is the exact shape of act this firm exists to distrust, and this seat will not have it recorded as housekeeping.** **Put to C2 as C13(k): Validation may refuse the conformance and require the literal `2027-01-31` sealed as drafted.**

### 14.1 What KC-002 is NOT — and it is not what a reader will assume

**Recorded because Validation predicted the exact sentence.** C-001 §1.6 states: *"KC-001 is a kill condition, not a confirmatory test. It tests `expectancy > 0` and `events ≥ 30` — a one-sided screen with no α and no power statement. **Surviving KC-001 confirms nothing at any `N`.** Recorded because 'the family passed its forward test' is the sentence I expect to read on 2026-11-01 if this is not said now."*

> **The identical statement binds KC-002, and this seat makes it here rather than waiting to be told.**
>
> **KC-002 is a one-sided kill screen with no α and no power statement. Surviving it confirms nothing at any `N`.** Clauses (a), (b) and (c) are each a bare comparison against a threshold; none has a null distribution; none is a test. **"The family survived its forward window" is not a result and may not appear in any artifact as one.**
>
> **This family does not claim the C-001 `N = 1` confirmatory exemption**, and nothing in this pre-registration should be read as claiming it. Should it ever seek one, it must satisfy **E1–E5** — one statistic, one α, named at sealing; computed once; every other forward computation logged to `N_forward`; the freeze mechanically evidenced by P1–P8; and `holdout_classification = FORWARD` — **and it must be entered in the firm-level register of outstanding confirmatory exemptions that I-032 requires and that does not yet exist.** Validation's measured figure — 20 families each holding one exemption gives a **firm-level false-positive rate of ≈2.7%** — is the reason that register is a precondition and not a formality.

### 14.2 Two notes on KC-002, neither of which softens it

1. **The 4.0% in clause (c) is calibrated, not arbitrary.** It is Charter §5.2 Tier 2. This seat expects [inferred, **not measured** — no return statistic has been computed on `pit.db`] that a clause-(c)-scale event occurred at least once in the in-sample period, most plausibly in March 2020 or May 2021. **If the in-sample run shows such days and the family survives F-002 anyway, that is important information and the pre-registration must be read as having anticipated it.** If clause (c) then fires in the forward window, the family dies having already told the firm it might.
2. **This seat's honest expectation, recorded now so it is not claimed as foresight later** [inferred]: **clause (b) is the most likely killer**, ahead of (a) and (c). A 30-day baseline on a mean-reverting funding series may simply not produce 30 days of ±25% notional movement in 187 days. **That would be a finding about the state variable's dynamic range, not about the market**, and it points directly at the successor family named in §19.3.

> **[R7 · 2026-08-04 — clause (b)'s prediction now has a named mechanism and this seat raises its own stated probability.]** §3.4's R2 restatement establishes that realized funding is **censored** to the interest rate whenever the premium sits inside the ±5 bp clamp band, and that **roughly 35% of prints sit exactly at the 1.00 bp floor** [measured — `DATA-VERIFY-001` §5.2]. **The state variable is therefore a mixture with a point mass, and its entire dynamic range lives in the off-floor subset.** A z-score computed on a series that is *identically constant* on about a third of its observations has a compressed numerator and a denominator inflated by the off-floor tail — both of which push `z(t)` toward the deadband and `w(t)` toward 1.0.
>
> ### **[R41(c) · 2026-08-25 · CLAUSE (b) IS NOW COMPUTABLE, AND ITS SENSITIVITY TO THE PARAMETERS IS NOW VISIBLE RATHER THAN INVISIBLE.]**
>
> `|Δw| > 0.25` ⟺ `k·(z − d) > 0.25` ⟺ `z > d + 0.25/k`. **At the sealed literals `k` = 0.5 and `d` = 1.0, clause (b) evaluates to: KILL on fewer than 30 days in the 187-day forward window with `z(t) > 1.5`.**
>
> **The Devil's Advocate's I-211 is correct and the direction is knowable a priori without running anything:** larger `k` and smaller `d` lower the threshold and make the sponsor's own pre-registered expected cause of death easier to survive. `(k, d) = (1.0, 0.5)` would give `z > 0.75`; `(0.25, 2.0)` would give `z > 3.0` and near-certain death. **The selected pair sits between them, was chosen from the mechanism before any output existed (§14 of the reasoning memo), and this seat states plainly that it DOES NOT KNOW whether `z > 1.5` occurs thirty times in a hundred and eighty-seven days and has not measured it.** That is what a pre-registration is for.
>
> **The Devil's Advocate's DA(2) is now executable at `z > 1.5` and this seat endorses it in the DA's own ordering — literals first, query second. It has not been run.**
>
> **This seat therefore states, pre-seal: clause (b) is not merely the most likely killer, it is the expected outcome, and the reason is the clamp rather than the market.** [inferred — from the formula's structure and the measured floor share; **not measured**, because measuring it is a trial and the registry is at 0.] If clause (b) fires, the correct reading is *"the administered floor censors the signal on a third of days,"* and the successor named at §19.3 should condition on the **uncensored premium index** (`premiumIndexKlines`, available and not ingested [cited — `DATA-VERIFY-001` §6.3]) rather than merely on finer bars.

---

## 15. METHOD — the sequenced test plan, cheapest kill first

*§7.2(5): universe, data, timestamps, splits, embargo, cost model, trial history. Universe and timestamps are §6 and §9.2. This section is the order of operations.*

| # | Step | Cost | Kills what | Registry trials |
|---:|---|---|---|---:|
| **0** **[R26 · 2026-08-10 · DISCHARGED. THIS STEP IS DONE AND BLOCKS NOTHING.]** | ~~**C1 — Validation specifies the funding-cost repair** (§12)~~ **Specified by `VALIDATION-RULING-003` (19 acceptance tests authored before implementation) and IMPLEMENTED by `DATA-IMPL-004` §5–§6 — *"All nineteen T-cases are implemented and pass"* — landed 2026-07-29; verified in source this session [measured].** **The test plan starts at step 1.** Residual, class (c): `CostModel` still cannot charge liquidation or venue-insolvency risk (§12.5 defect (d), C-25), disclosed and not waited on. | ~~fraction of an Opus unit~~ **spent, 2026-07-29** | ~~Nothing directly. **Blocks everything.**~~ **Blocks nothing.** | 0 |
| **1** | **Ingest `binanceusdm` daily OHLCV** for BTC/ETH/SOL perpetuals via `fetch_ccxt_ohlcv`, bounded by the sealed ceiling at `C`, two-timestamp discipline, raw only. | ~1 Sonnet unit | Nothing — enabling. §8's single open dependency. | 0 |
| **1b** | **C11 — the leg-(ii) null calibration** (§5.5(e)), if Validation requires it. Block-bootstrap / sign-randomization of the conditioning schedule against realized `R_bench`, average exposure fixed. **Runs before F-002, never after** — a null measured after seeing the statistic is not a null. | fraction of a unit | Nothing. Converts §5.3's one [assumed] probability to [measured]. | ≤ 2 |
| **3b** **[R30 · NEW · 2026-08-11]** | **HOUSE RULE 5 — the breakeven adverse carry shift.** `carry.carry_breakeven_bps_annual(net_at_shift, periods_per_year = 365, bracket = (0.0, 2000.0), iters = 8)`, with `net_at_shift(0.0)` supplied from step 3's already-logged engine output and every other shift a fresh `run_backtest` on `shift_carry_panel(panel, δ, 365)`. **Bracket NOT narrowed** (the function returns its endpoint when the root lies outside it — the I-037 operation). **Resolution `2000 / 2⁸` = 7.8 bps/yr.** **Runs ONLY if F-002 survives in full.** | shared with step 3 | Nothing — **required reporting.** House rule 5: no performance number is quoted without its cost-inclusive twin **and the breakeven cost at which the edge dies** | **≤ 9 on the survive path · 0 on the KILL path** (`t_lo < hurdle` returns before evaluating anything else, and the breakeven of a family below the hurdle **is** 0.0 bps/yr by construction). **NOT INSIDE STAGE 1's 47, WHICH SUMS EXACTLY — routed to C13(j)** |
| **2** | **F-002 leg (0) then leg (iii) — the qualifying-bar count, then the benchmark run alone.** Is the sample sufficient, and is there a premium to condition on net of both legs' costs? | ~1 Sonnet unit | **The family, root and branch.** Cheapest killing test; this seat's standing discipline is to run it first. | **1** |
| **3** | **F-002 legs (i) and (ii) — the strategy run, the exposure-matched benchmark run, and the two comparisons.** Newey–West alpha to `R_bench`; exposure-matched tail reduction vs `R_bench_scaled`. **Evaluated ONCE (E2). No re-run with corrected costs — that would be a new family.** | shared with step 2 | **The thesis.** Two independent ways it dies. | **2** |
| **4** | **Capacity measurement** — trailing-20-session median notional per leg per asset against the $2.5M screen; and the skew / expected-shortfall line on both series. | ~1 Sonnet unit | §4.4 capacity, if depth is absent. Reported regardless. | ≤ 2 |
| **5** | Per-regime-cell decomposition, cost sensitivity at 1× / 2× / repaired preset, ~~SOL on its own span,~~ **[R3 · struck]** T-capacity window robustness. | ~1 Sonnet unit | Nothing — required reporting | ~~≤ 6~~ **[R22] ≤ 5** |
| **6** | **±50% grid**, 2 parameters × 5 steps, via `run_parameter_grid`. **Plateau centroid advances; argmax is reported alongside it and never carried forward.** | ~1 Sonnet unit | §4.4 parameter surface | **25** |
| **7** | Walk-forward, ≥ 10 windows, purged k-fold with 1% embargo. **[R11 · 2026-08-05] Every window refit at the FIXED plateau-centroid configuration — no per-window selection (§10.7(c)).** **[R11] Two harness defects are carried into this step rather than assumed away:** `walk_forward_windows` applies **no purge and no embargo at all**, and `purged_kfold_splits` embargoes `⌈0.01·T⌉` = **24 bars on a 2,398-bar sample — SHORTER THAN THIS FAMILY'S OWN 30-DAY FEATURE LOOKBACK**, so a training bar after the test fold computes its state variable from inside it [cited — `VALIDATION-RULING-004` §1(5), ML-18, §6.1; **I-051**, MEDIUM, owner `head-of-data-infra`]. **This is a live leakage channel for THIS family specifically, because its 30-day K1 lookback is longer than the embargo the harness applies.** Not this seat's to repair; **named at Gate 0 so a WFE result is not read as clean.** | ~1 Sonnet unit | §4.4 WFE | ≤ 20 |
| **8** | Forward-window generation through `C + 187 days`, for KC-002. **[R20] STAGE 2 — NOT AUTHORIZED AT THE SEAL.** Spendable only against an admitted CONTINGENT extension (§10.5.2). | ongoing | KC-002 | ~~≤ 25~~ **[R22] ≤ 22** |

> **[R22 · 2026-08-10 — THIS TABLE'S OWN ARITHMETIC WAS OVER THE DECLARED BUDGET BY 4, AND THE REPAIR IS DISCLOSED RATHER THAN SILENTLY CONFORMED.]** As written through R-003 the steps summed to `2 + 1 + 2 + 2 + 6 + 25 + 20 + 25 = 83` against a declared **79** [integer arithmetic on already-declared line items]. Two discrepancies, both against the firm: **diagnostics read 8** (step 4's ≤2 plus step 5's ≤6) against §10.5.3's **≤7**, and **`N_forward` read ≤25** against §10.5.2's **≤22**. **R3, R6 and R15 each conformed §10.5 and none of them reached §15's arithmetic** — the same defect class R8(c) repaired for the three surviving instances of the superseded 80, in the section that sequences the spending rather than the one that authorizes it. Conformed to `2 + 1 + 2 + 2 + 5 + 25 + 20 + 22 = 79`. Filed **I-136**. **The staging is also carried here now, because §15 is what a researcher reads before running anything: steps 1b–6 and walk-forward windows 1–10 are Stage 1's authorized 47; walk-forward windows 11–20 and all of step 8 are Stage 2 and are NOT authorized at the seal.**

> **Steps 0–3 are the whole decision.** Everything from step 4 onward exists to make a *positive* result trustworthy. **None of it is needed to make a negative result decisive**, and if step 2 fires the firm has spent one Sonnet unit and one ingest to kill a family, which is a successful deliverable and is written up as one.

**Standing methodological requirements, all binding and none waived:** prices via `PITStore` only (A4); every backtest through `castellan.run_backtest` against this family (A2); `execution_lag = 1` minimum, enforced by the engine; purged k-fold with 1% embargo; costs from `castellan.costs` presets or Principal-approved additions only — **no hand-rolled cost numbers anywhere, including the paper book**; gross and net always, with the breakeven cost; `backtest_years` passed **explicitly** as true calendar span **and `oos_index` supplied** (G1–G5 — without it the length criterion is INSUFFICIENT-DATA, never PASS).

---

## 16. WHAT CANNOT BE EVALUATED, AND WHY IT MATTERS BEFORE THE FIRST RUN

*Stated at pre-registration rather than discovered at Gate 1.*

| §4.4 criterion / concern | Status | Reason |
|---|---|---|
| **Net Sharpe, DSR, PBO** | **Computable and — uniquely among the firm's families so far — correctly denominatored** | `N_inherited = 0` is honest, the grid populates `σ_SR` genuinely, and I-027's residual is **0.13 years of MinBTL** (§10.3). |
| **t-statistic** **[R10 · 2026-08-05 — SPLIT OUT OF THE ROW ABOVE, WHERE IT DID NOT BELONG]** | **Computable, and its ESTIMATOR is currently wrong in the permissive direction** | The row above previously carried the `t`-stat and claimed it *"correctly denominatored."* **The denominator was honest; the estimator was not.** `SR × √T` assumes serial independence; the firm's measured instance is **ρ = 0.83 → ≈3.3× inflation**, permissive [cited — I-050, Principal-approved]. **This family's net return is funding accrual plus a basis increment and is autocorrelated by construction** [inferred]. Correct after I-050's estimator repair; **`T_STAT_HURDLE = 3.0` does not move.** F-002 leg (i) is unaffected — it was written Newey–West from the start (§5.4 R10). |
| **`σ_SR` — the input DSR is actually denominated in** **[R10 · NEW]** | **Populated, and this family is on the right side of a defect it did not know about** | `deflated_sharpe_ratio` benchmarks against `expected_max_sharpe(N, σ_SR)`, **linear in σ_SR**, and `family_stats.sr_period_std` is computed **from logged trials only** — so a family that logs only near-identical survivors reports σ_SR near zero and **defeats DSR at any `N`** [cited — `VALIDATION-RULING-004` §2.3, §1(3), which calls this *"the largest hole in the firm's apparatus"* and finds σ_SR *"roughly three times more load-bearing than `N`"*]. **This family logs all 25 grid points and ~20 walk-forward refits and reports the plateau centroid, not a survivor subset** (§10.5–10.6), so its σ_SR is estimated on the space searched. **Recorded because §10.6 previously argued this as a methodological advantage without knowing it was also a defence against a named hole.** |
| **Backtest length ≥ MinBTL(N) and ≥ 4 years** | **Clears, with margin, at the declared budget** | 6.571 years available; `MinBTL(86, SR 1.0) = 6.14`. **This is the criterion that kills `forward-lag-001` and this family clears it** (§10.4). |
| **Holdout ≥ 12 months, most recent 25%** | **Reachable but the earliest date is contested** | §11.3 — three readings, three earliest-Gate-1 dates ~~from 2027-07-28 to 2030-07-28~~ **[R34 · 2026-08-11] from `C + 12 months` to `C + 4 years`, re-expressed as formulae because the literals were computed at the abandoned `C` = 2026-07-28**. **Escalated to Validation, not assumed.** |
| **Capacity ≥ 10× allocation** | **Evaluable with data on disk** | The `volume` field already exists for spot; perp volume arrives at step 1. **Contrast I-026**, where the instrument does not exist at all. |
| **Cost robustness at 2× modelled costs** **[R26 · 2026-08-10 · NOW EVALUABLE AND MEANINGFUL]** | ~~**Evaluable but currently meaningless**~~ **EVALUABLE.** T-16 [measured — `carry.py`, `DATA-IMPL-004`]: **`cost_model.scaled(2.0)` leaves `carry_accrual` bit-identical**, carry living entirely outside `CostModel`. The 2× test now stresses the costs and only the costs, and `carry.carry_breakeven_bps_annual` supplies the separate, monotone carry stress. | ~~**§12.6:** `scaled(2.0)` doubles `funding_bps_annual`, so the 2× test stresses the sign error rather than the costs. Meaningful only after C1.~~ **[R26] Superseded — retained as the record.** |
| **Parameter surface — ≥60% of ±50% grid net-profitable** | **Evaluable, and budgeted** | 25 grid points, §10.5. A real advantage over PREREG-001, which authorized no grid. |
| **Correlation to live pod strategies** | Trivially satisfiable | No live strategies exist. Recorded so the PASS is not read as informative. |
| **Red-Team Memo with a binding kill condition** | **NOT YET SATISFIED** | KC-002 exists and is written to KC-001's shape, **but no Devil's Advocate memo has been written on this family.** §4.4 requires one and §6.4 defers a packet without it. **Condition precedent C3.** |
| **Liquidation / venue-insolvency charge** | **Cannot be expressed at all** | **§12.5** — `CostModel` has no field for it. Same shape as I-023(b). **The paper book will over-report this family's net by an unmeasured amount whose sign is known.** |
| **THE INTRADAY RISK** | **STRUCTURALLY UNMEASURABLE ON THIS DATA** | See below. |

### 16.1 The intraday problem, stated at full strength

**The strategy's risk materializes intraday. `book/pit.db` holds daily bars.**

A liquidation cascade compresses into minutes to hours: the perp dislocates from spot, margin is called on the short-perp leg, and the position is force-closed at the worst basis of the day. **A daily bar shows the open and the close and nothing in between.** A backtest on daily bars sees a basis excursion that opened and closed on the same day as *no event at all*, and it marks a position that would have been liquidated as still held and recovering.

> **The measurable part of this strategy is the part that flatters it. The part that kills it is the part the data cannot see. A daily-bar backtest of a funding-carry family will produce a smoother equity curve, a higher Sharpe, and a shallower maximum drawdown than the strategy has, and the gap is not estimable from within the daily data.**

**This is the same structural shape as I-023(b) and I-026** — the firm's instrument cannot measure the mandate's dominant risk — and it is named at Gate 0 for the same reason: so that a good-looking result is read correctly.

**Three responses, all of which this document takes:**

1. **F-002 leg (ii) is written on the tail**, so the family must demonstrate tail reduction rather than merely a good Sharpe.
2. **KC-002 clause (c) is a forward-window tail trigger**, which catches at wall-clock what the backtest cannot catch in history.
3. **Skew and expected shortfall are required on every artifact** (§6.3), because §4.4's battery — Sharpe, t-stat, DSR, subperiod positivity, P&L concentration — **rewards a short-tail carry profile at every single criterion and contains no criterion that can see one.** That is a gap in the firm's own Gate 1 design, surfaced here because this is the first family that walks straight into it. **Proposed as a Charter §4.4 addition for the Principal's consideration; not asserted as binding.**

**The fix that would close it is cheap in principle and expensive in volume:** `ccxt` exposes minute-level history [cited — Charter §3.2 *"Deep minute-level history"*]. 1-hour bars over 6.571 years across 3 assets × 2 legs is ~345,000 bars — feasible, unscheduled, and **not required for a KILL verdict.** It is named in §19.3 as the successor family's data requirement.

---

## 17. RISKS, AND WHAT KILLS THIS

Ranked by how much each should move the decision.

| Rank | Risk | Kills it how |
|---:|---|---|
| **1** **[R26 · 2026-08-10 · RESOLVED — see the R26 note at §12 and at §14. `CRYPTO_PERP_TAKER` carries no funding term; `carry.py` is the sanctioned path; all nineteen T-cases pass. The row below is retained as the record of the risk and is NO LONGER LIVE. The residual that IS live is §12.5 defect (d): no field can charge liquidation or venue-insolvency risk — class (c), C-25, disclosed on every artifact.]** | ~~**The cost preset inverts the sign of funding (§12)**~~ | Every net number is wrong by 32.85 points/yr, deterministically. **Blocking on every net claim, including the paper book.** ~~Condition precedent C1. Fixable, and the fix is Validation's to specify.~~ **[R29 · 2026-08-11] SPECIFIED, IMPLEMENTED 2026-07-29, AND DISCHARGED. C1 is gone from this document's conditional and I-034 is CLOSED (Principal, 2026-08-11).** |
| **2** | **The intraday risk is unmeasurable on daily bars (§16.1)** | Not a Gate 1 failure — **worse.** It produces a Gate 1 *pass* that the firm cannot rely on. Mitigated by F-002 (ii), KC-002 (c), and mandatory skew/ES reporting; **not eliminated.** |
| **3** | **The conditioning never conditions (KC-002 clause b)** | The most likely proximate cause of death [inferred]. A 30-day baseline may not move the position enough to matter. Kills the family and points at the successor. |
| **4** | **Venue survivorship (§9.1 S2)** | The backtest runs on the branch where the venue survived. **Unmeasurable, uncharageable, disclosed.** |
| **5** | **Crowding — the alpha is competed away** | The unconditioned carry is unambiguously crowded and §3.3 concedes it. The conditioning claim is narrower and therefore less crowded, but §11.6 accepts the full 50% haircut and §5.4 shows the resulting pre-haircut bar is `t(α) ≈ 6.0`. **This is the largest honest hurdle and it is accepted, not argued down.** |
| **6** | **Short-vol payoff defeats the firm's own validation battery (§16.1)** | Sharpe, t-stat, DSR, subperiod positivity and P&L concentration all reward a carry profile. **The firm's Gate 1 cannot see the risk it is gating.** Raised as a §4.4 gap, not as this family's excuse. |
| **7** | **The missing perp price series (§8)** | One session of ingest. **The only reason it is on this list is that the tempting shortcut — assume perp ≈ spot — would zero out the basis and produce a spectacular, meaningless result.** Named so it is not taken. |
| **8** | **Materiality (§13.2)** | Does not kill the research. **Caps the investment case at 15–30 bp of firm NAV unlevered, and the levered version is the thing the research exists to price.** |
| **9** | **The §11.3 holdout-reading ambiguity** | Could push earliest Gate 1 from ~~2027-07-28 to 2030-07-28~~ **[R34 · 2026-08-11] `C + 12 months` to `C + 4 years`** — the literals were computed at the abandoned `C` = 2026-07-28. **Decidable by Validation for a fraction of a unit; undecided, it is a schedule risk the firm does not know it is carrying.** |
| **10** | ~~**Three assets is a thin cross-section**~~ **[R3 · 2026-08-04] TWO assets is a thinner one** | `N_eff` across BTC and ETH will be far below 2 — the two are highly co-moving and their funding series more so. **Raw and effective observation counts are required side by side in every artifact**, as PREREG-001 §15 requires for its own pooling. **The R3 drop of SOL makes this risk worse, not better, and it is the one genuine cost of that decision** (§6.1). It was already the case that SOL never entered the primary cross-section, so `N_eff` is unchanged in fact — what is lost is a **separate corroborating report on an asset whose funding behaved differently** (annualized mean funding **SOL +0.10%** against **BTC 11.86% / ETH 14.07%** [measured — `DATA-INGEST-002` §4]). |
| **11** **[R7 · NEW]** | **The state variable is censored on ~35% of prints** | Realized funding equals the administered interest rate exactly whenever the premium sits inside the ±5 bp clamp band [cited — official, `DATA-VERIFY-001` §1.1], and **~35% of prints sit at that floor** [measured — `DATA-VERIFY-001` §5.2]. `z(t)` is therefore a z-score of a **censored** series with a point mass. **This is now the leading candidate cause of death** (§14.2 R7) — ahead of the granularity argument that previously held that position. Not fixable within this family; the successor conditions on the uncensored premium index. |
| **12** **[R5 · NEW]** | **A vendor funding-parameter change inside the FORWARD window** | Binance states it does **not announce** subsequent settlement-frequency adjustments [cited — official, `DATA-VERIFY-001` §3.2]. On BTC or ETH inside `[C, C+187 days]` this would corrupt the state variable in the window KC-002 is computed over. **K7 (§7.1) is the pre-declared treatment and R4 is the arithmetic repair.** Residual after both: **an unnoticed change is still possible**, since detection depends on Seat 9 observing it — which is why C12 (§20) requires the in-sample cadence sweep to establish a baseline the forward window can be compared against. |

**Three things this seat will not claim as risk mitigation:** that the mechanism's quality is evidence the edge exists; that a good Sharpe on a short-tail payoff is evidence of anything; and that delta-neutrality makes the position safe — it makes it *directionally* neutral and leaves it fully exposed to the basis, which is where the loss lives.

---

## 18. SIZING, LIMITS, EXIT CRITERIA

| Element | Value |
|---|---|
| Intended initial allocation | **USD 250,000** (§13) |
| Per-asset notional | **USD 125,000** × 2 assets |
| Maximum concurrent gross | **USD 500,000** at `w = 1.0` — two legs. **2.5× the allocation is inside Pod B's 4× gross limit** (§5.1) and it is stated here because a two-legged strategy's gross is not its allocation. |
| Leverage | **None. `w_max = 1.0`.** The strategy never exceeds delta-neutral. §13.3 records that this is what makes it immaterial and why the leverage question is deferred to a result rather than assumed. |
| Participation cap | ≤ 5%/day of trailing-20-session volume per leg (§4.2 `ADV_PARTICIPATION_MAX`); liquidity floor ≤ 15% of 20-day ADV (§5.1). |
| Correlated cluster | **BTC and ETH are one cluster, not two positions.** Their funding series co-move; treating them as independent would understate concentration. Cluster cap 15% of pod capital (§5.1) applies to the crypto-carry cluster as a whole. |
| Position exit | **None.** No target, no stop, no maximum hold (§6.2). Risk is managed by size, which is the hypothesis. |
| **Family exit** | **F-002 fires** → KILL memo, written with the same care as a PROCEED memo (house rule 1). **KC-002 fires** → registry TERMINATED, automatic, not appealable to the CIO. ~~**Trial budget exhausted at 80, or `N` reaching 110**~~ ~~**[R8 · 2026-08-05] Trial budget exhausted at 79, or `N` reaching 109**~~ **[R19/R20 · 2026-08-10] AUTHORIZED budget exhausted at 47 own-logged trials (Stage 1), or registry `N` = `n_inherited` 7 + logged reaching 109** → this seat halts the family and reports it before Validation raises it. **Stage 2's further ≤32 are reachable only through an admitted CONTINGENT extension (§10.5.2) and are not part of this trigger until admitted.** **Neither figure is discretionary — and R-004 records that neither is enforced at spend time either: `log_trial` reads no budget (I-132), so this exit is a discipline on this seat, checked retrospectively by `evaluate_gate1`.** |
| Sizing on a Gate 1 pass | ≤ 25% of target allocation initially, ramped on realized performance (§4.5). |
| Drawdown | Charter §5.2 ladder applies at pod level. **This seat notes for the CRO that a $250k sleeve cannot on its own reach a pod-level Tier 3, which is why KC-002 clause (c) operates at the sleeve level** — the firm's standing ladder is too coarse to see this family fail. |

---

## 19. VERDICT — should this hypothesis get the compute?

*Within this seat's mandate ("decides alone: which hypotheses enter and their priority; test design; when to abandon a line") and given plainly.*

> ### VERDICT: **FUND IT.** Recommended Gate 0 intake verdict: **ADMITTED**, conditional on ~~**C1, C3 and C11**~~ **[R29 · 2026-08-11] C3 and C11 — C1 IS DISCHARGED.**
> **Approximately 4 Sonnet units and a fraction of one Opus unit. Not a flagship allocation.**
> **AND: DO NOT SEAL TODAY (§20.1).** Sealing waits on the three conditions. This seat held the opposite position earlier in this session and states the reversal at §20.1 rather than quietly adopting Validation's.

### 19.1 Why this is a different verdict from PREREG-001's, and the difference is arithmetic

PREREG-001 §17 recommended **ADMITTED-AS-EXPLORATORY** and *"fund the falsifier, not the family."* The reason was not doubt about the mechanism — the Devil's Advocate conceded the mechanism was coherent — but that **Gate 1 was unreachable at any Sharpe**, because `MinBTL(31,250) = 17.06 years` against a venue with less than four.

| | `forward-lag-001` | `funding-carry-conditioning-002` |
|---|---|---|
| `N_inherited` | **31,250** [inferred, D-009] | **0** [measured] |
| `MinBTL` at Gate 1 Sharpe floor | **17.06 yr** | **6.14 yr** at the full budget |
| History available | **unmeasured; plausibly < 4 yr** [cited — I-004] | **6.571 yr, zero gaps** [measured] |
| Gate 1 length criterion | **FAILS before the first run** | **CLEARS with 0.43 yr of margin** |
| Data on disk | **0 rows; no loader; unaccepted spec** [measured] | **all but one series; loader exists and has been run** [measured] |
| Capacity measurable? | **No** — depth is structurally unreconstructible [cited — I-026] | **Yes** — from the `volume` field on disk |
| Blocking harness defect | **I-027**, worth a factor of ~1,000 in `N` | **I-027**, worth **0.13 years** — not blocking here |
| Blocking cost defect | I-023, ~2.5–5× a cost | **§12, a sign inversion — larger, and fixable** |

> **The verdict differs because the arithmetic differs. A hypothesis whose verdict is reachable deserves compute; one whose verdict is not, does not — however good its story.** That is the whole content of the redirect the Principal approved, and it is not an argument that this family's mechanism is better than the other's.

### 19.2 What to spend, and what not to

| Spend | Do not spend |
|---|---|
| ~~**C1** — Validation's funding-cost specification. Fraction of an Opus unit. **Everything else is blocked on it.**~~ **[R29 · 2026-08-11] SPENT, 2026-07-29. Nothing is blocked on it. This row is retained as the record of what was budgeted and is no longer a call on the firm's compute.** | ~~Any net-P&L claim, in any document or in the paper book, before C1 lands.~~ **[R29] Net claims are admissible.** **[R30] What is NOT to be spent: `carry_breakeven_bps_annual` at its shipped `iters = 40`, which is 42 logged trials — 89% of Stage 1's 47 — for a statistic containing no selection. Nine at `iters = 8`, survive-path only, §15 step 3b.** |
| **Steps 1–3** — perp ingest, benchmark run, strategy run, F-002 in full. **~2 Sonnet units.** | Intraday ingest (~345,000 bars) **until F-002 survives.** It is the successor's requirement, not this family's. |
| **Steps 4–7** — capacity, diagnostics, the 25-point grid, walk-forward. **~2 Sonnet units, conditional on F-002 surviving.** | Any expansion of the trial budget past ~~80~~ **[R8(c) · 2026-08-05] 79**, or of `N` past ~~110~~ **[R8] 109**, on the strength of an early result. §10.4. |
| **One Devil's Advocate Opus unit** for the mandatory Red-Team Memo (C3). | Any Gate 1 apparatus before §11.3's holdout reading is settled. |

### 19.3 The honest expectation, recorded now so it is not claimed as foresight later

[inferred, from the design rather than from any measurement]

- **Leg (iii) survives.** A positive net carry over 6.5 years on BTC and ETH is the most likely of the three outcomes, and it would confirm what the Charter already says rather than discovering anything.
- **Leg (i) is close to a coin flip**, and the 50% haircut makes clearing Gate 1's version of it (`t(α) ≈ 6.0` pre-haircut) considerably less than even. **[R10 · 2026-08-05 — this line is revised AGAINST the family and the revision is the largest single change R-002 makes to a pre-registered expectation.]** F-002 leg (i) itself is **unaffected** by I-050 — it was pre-committed as a Newey–West `t` — but **Gate 1's `t` on net returns was not**, and its estimator is being corrected from `SR × √T` to one that does not assume serial independence. On a payoff whose revenue line is the firm's one measured ρ = 0.83 series, the composition of the 50% haircut with the corrected estimator puts the required **uncorrected, pre-haircut `t` at order 20** (§5.4 R10) [inferred — arithmetic on two cited multipliers; the family's own ρ is unmeasured]. **This seat therefore states pre-seal: conditional on F-002 surviving in full, the expected Gate 1 outcome is PARK-WITH-TRIGGER, not PROCEED.** That is a worse pre-registered expectation than R-001 carried, it is recorded before any result exists to be embarrassed by, and **it is not a reason to withdraw the family** — §19.1's case is that a *verdict* is reachable, and F-002 and KC-002 deliver the verdict without touching a `t`.
- **Leg (ii) is the most likely killer, and the reason is granularity, not the market.** A daily conditioning signal is being asked to reduce a tail that materializes intraday. **That is asking a daily instrument to dodge an intraday event, and the honest prior is that it cannot.**

> **[R7 · 2026-08-04 — two revisions to this expectation, both against the family.]**
>
> **(1) Leg (iii)'s survival is now near-certain and worth nothing.** See §5.3 R7. Annualized mean funding of **11.86% (BTC) / 14.07% (ETH)** [measured — `DATA-INGEST-002` §4] against ~24 bps of round-trip friction [cited — D-013 §4] makes leg (iii) a formality. **This seat withdraws leg (iii) as a source of information about the family and states that its survival may not be reported as a finding.**
>
> **(2) Leg (ii) is now testing a MILDER tail than the one the mechanism theorises about.** With SOL dropped (R3), the primary universe's largest in-sample basis excursions are **−73.65 bp (BTC)** and **−102.95 bp (ETH)**, both 2020-03-12 — against SOL's **−1,690.34 bp** on 2022-11-09 [measured — `DATA-INGEST-002` §4], roughly an order of magnitude larger. **F-002 leg (ii)'s "20 worst days" on BTC/ETH is a test on a tail the family does not actually fear.** This does not make leg (ii) invalid — it was always computed on the primary universe and never on SOL — but it does mean **leg (ii) surviving is weaker evidence of tail reduction than the leg's construction implies**, and no artifact may report it otherwise.
>
> **(3) The composite expectation, restated.** The family's most likely terminal outcome is now, in this seat's judgment [inferred]: **KC-002 clause (b) fires on the censored state variable before F-002 leg (ii) gets a decisive tail to measure.** That is a finding about the *instrument* — a daily, clamp-censored funding series — and the successor it names needs both finer bars **and** the uncensored premium index, not one or the other.

> **If leg (ii) fires, the KILL memo names a specific successor and that successor is the family worth the firm's compute:**
>
> **the same claim, on 1-hour or 8-hour bars, opened with `predecessor_family = "funding-carry-conditioning-002"`** and ~~`n_inherited ≥` this family's final `n_trials`~~ **[R9 · 2026-08-05] `n_inherited` = its own new search only, this family's count arriving through `predecessor_family` by transitive summation** — **and note that a successor changing K6 is a revision of a declared choice, so §7.2's replacement governs it: at K6's menu size of 4 the escalated declaration is `3 × chain_total`, which the harness refuses today, and until I-053 is repaired THIS SUCCESSOR CANNOT BE OPENED.** That is a real and newly-visible cost of the family's most likely terminal outcome (§19.3(3)), and it is stated here rather than discovered on the day the KILL memo names the successor. It would need ~345,000 bars of ccxt history, which the firm can retrieve, and it would be able to see the risk this family cannot.
>
> **That is the result this seat actually expects to deliver: not an edge, and not a bare null, but a measured demonstration that the edge is unmeasurable at daily granularity — which is a finding the firm can act on, and which costs ~4 Sonnet units to establish rather than the 20 it would cost to go straight to intraday.**

> ### **[R28 · 2026-08-10] DOES THE CLASS MANDATE MOVE THIS EXPECTATION? THE POINT ESTIMATE DOES NOT. THE FAILURE MODE DOES, AND IT MOVES AGAINST THE FIRM.**
>
> **The expectation of PARK-WITH-TRIGGER is NOT restated and NOT withdrawn.** It was a judgment about what this payoff can deliver, and it remains one. **This seat states that plainly rather than manufacturing a revision to look responsive to a mandate.**
>
> **What moves is what surrounds it.** The order-20 composite above is `3.0 × 2 × 3.3`, and under the class register the two multipliers are **different kinds of object**:
>
> | Multiplier | Class | Evidence |
> |---|---|---|
> | **3.3× — the I-050 estimator correction** | **(a)** | `t_gate = min(t_NW, t_raw)`, *"the ONLY figure graded (E-8)"* [measured — `stats.py:153`, `:221`]. **Unavoidable** |
> | **2× — the published-signal haircut** | **(c)** | **no code path; C5 unruled** (§5.4 R28) |
>
> **So this document's most conservative pre-registered expectation is half-computed and half-declared, and the declared half is the one that could silently not happen.** §5.4 names the branch it opens: **a PROCEED at half the Charter's bar.** **That branch was always there. Until this revision, nothing in this document could see it, because the document did not distinguish a limit the engine applies from one a seat has to remember.**
>
> **This is the mandate paying for itself in one line, and it is the honest reason to run it: the relabelling did not weaken the expectation — it exposed a permissive branch that a document describing prose as a control could not have found.**

### 19.4 What this verdict is not

**It is not a claim that the funding carry is an edge.** §3.3 says explicitly that it is not, that it is factor beta under §5.4, and that the firm should not pay for it.

**It is not a recommendation to prefer this family because this seat originated it.** I-025's origin-ratio metric is a diagnostic, not a target, and a Director-originated hypothesis funded because it is Director-originated would corrupt the metric it was created to inform. **The case is made at §19.1 on arithmetic that would hold whoever wrote it.**

**It does not soften KC-002 by one word,** and clause 5 — silence is a kill — binds this seat exactly as KC-001's binds Pod B.

---

## 20. CONDITIONS PRECEDENT TO SEALING

*Nothing may be added after sealing (D-007, P7). These must be resolved — or explicitly accepted as unresolved by Validation at Gate 0 intake — before Pod B calls `open_hypothesis`.*

| # | Condition | Owner | Blocking? |
|---|---|---|---|
| **C1** | **The funding-cost repair (§12).** Validation specifies how realized funding enters the P&L — a signed carry term on `CostModel`, or a synthetic perp total-return leg with `funding_bps_annual = 0.0` — **and rules on whether the latter breaches the Seat 9 standing rule that researchers may not hand-roll costs.** A `CRYPTO_SPOT_TAKER` preset is added if the specification requires one, Principal-approved. **Acceptance test authored by Validation before implementation** (I-021). | Quant Validation → head-of-data-infra → Principal | ~~**BLOCKING on every net claim.**~~ **[R29 · 2026-08-11] NOT BLOCKING. DISCHARGED.** | ~~**[R26 · 2026-08-10 · DISCHARGED IN SUBSTANCE, AND THIS SEAT DOES NOT CLOSE IT.]**~~ **[R29 · 2026-08-11 · DISCHARGED OUTRIGHT BY THE PRINCIPAL. I-034 IS CLOSED — satisfied 2026-07-29 on commit `875874f` (*"Ruling 003 implemented: carry accounting, 139/139. Closes I-034"*), recorded 2026-08-11, discovery credit R-005. The Principal's words: *"a family does not get downgraded because its paperwork didn't learn what its repository did."* C1 IS DISCHARGED, NOT EXTENDED, and it is struck from §1's and §19's conditional.** Specification: `VALIDATION-RULING-003`, header — *"Blocks: PREREG-002 condition precedent C1"*. Implementation: `DATA-IMPL-004` §5–§6, ***"All nineteen T-cases are implemented and pass"***, landed **2026-07-29** [cited], verified in source this session [measured]. **Defect (d) — no `CostModel` field can charge liquidation or venue-insolvency risk — is NOT repaired, is class (c) (C-25), and is not a condition precedent because there is nothing to wait for.** **C1's formal closure routes to `quant-validation → head-of-data-infra` and this seat holds neither.** Filed **I-140, HIGH.**
| **C2** | Validation's Gate 0 intake verdict on this document. | Quant Validation | **BLOCKING** — sealing is what fixes `C`, and it follows intake |
| **C3** | **A Devil's Advocate Red-Team Memo on this family.** §4.4 requires one and §6.4 defers a packet without one. **None exists.** KC-002 is written to KC-001's shape but is **this seat's**, not the red team's, and a kill condition authored by the sponsor is structurally weaker than one authored against it. | Devil's Advocate | Blocking on **Gate 1**, not on sealing |
| **C4** | **Validation's ruling on §11.3** — which window `oos_index` carries under Option D, and therefore the earliest date Gate 1 is reachable. Bears identically on `forward-lag-001`. | Quant Validation | Blocking on **Gate 1 scheduling**, not on sealing |
| **C5** **[R31 · 2026-08-11 · PROMOTED TO A LOCK BY THE PRINCIPAL]** | **Validation's ruling on §5.4** — the point of application of the §4.6 50% haircut (returns, Sharpe, or alpha), which is unspecified in the Charter and uncomputed in the harness (I-019). **[R31] AND THE RULING IS IN THREE PARTS, ONLY THE FIRST OF WHICH IS VALIDATION'S.** **(1) THE POINT OF APPLICATION — Validation's, final short of the Principal — and the three readings are NOT equivalent, because one of them is a NO-OP:** haircutting the **return series** (`r → 0.5·r`) changes **nothing** at Gate 1, since Sharpe, `t`, DSR, PBO, WFE, subperiod positivity and P&L concentration are **all invariant to a positive scalar** [inferred — from the definitions; no measurement involved], leaving only capacity and cost-robustness to move; haircutting the **expected return** (`μ → 0.5·μ`, `σ` as measured) **halves `t`** and sets the effective hurdle at **6.0**, which is §5.4's reading; haircutting the **computed Sharpe** matches the second for the Sharpe criterion and is **undefined** for `t` and for DSR's benchmark. **C5 is therefore not a choice among three shades of one control — it is a choice between a 2× hurdle and nothing.** **(2) THE RATIFICATION — THE PRINCIPAL'S, and Validation cannot supply it.** Either reading moves the bar a family must clear between 3.0 and 6.0 **while `T_STAT_HURDLE = 3.0` never moves.** Charter §4 reserves *"any change to the Gate thresholds in Part IV"* to the Principal in writing; **a ruling that changes the effective bar by 2× without touching the literal constant is a §4 reserved act wearing an interpretation's clothes** — the Principal's own 2026-08-11 doctrine applied one clause over. **Escalated under house rule 7, not resolved here.** **(3) THE EXECUTOR — without which (1) changes nothing.** `published_signal_haircut_applied = 0.50` has **zero non-`registry.py` consumers** and **no haircut computation exists anywhere in the harness** [measured — I-134]. **A ruling naming a point of application and no executor is class (c) and leaves I-143's permissive branch exactly where it is.** C5 discharges only when the ruling carries **executor, cadence and artifact**: *Validation, at every `evaluate_gate1` call on this family, with the point of application and the applied value named on the Validation Report's face.* | Quant Validation **(1)** · **the Principal (2)** · Quant Validation **(3)** | ~~Blocking on **Gate 1**, not on sealing~~ **[R31 · 2026-08-11 · A LOCK, NOT A FOOTNOTE] BLOCKING ON GATE 1 EVALUATION AND ON ANY REPORTED VERDICT — ABSOLUTELY.** The family may be sealed, may be run, and may spend Stage 1 with C5 open. **IT MAY NOT BE EVALUATED AT GATE 1, AND NO PROCEED MAY BE REPORTED, UNTIL C5 IS RULED.** The Principal's reason is recorded with it because it sets the standard for findings of this class: *"a path to half the Charter's bar existing quietly is exactly what the relabeling mandate existed to surface, and its first substantive yield gets a lock, not a footnote."* Filed **I-152, MEDIUM.** |
| **C6** | **Validation confirms §8.2** — that reading `field='funding_rate'` via `PITStore.asof` / `rows_in_window` is an admissible A4 path, there being no `pit_*` panel accessor for a non-close field. | Quant Validation | Blocking on **measurement**, not on sealing |
| **C7** | Pod B's written acceptance of **KC-002** as sponsor, and the Principal's signature, before any capital paper or real. | PM Pod B / the Principal | **BLOCKING** (KC-002 preamble) |
| **C8** | The seal and `HoldoutVault.seal()` occur in the **same session, same UTC day**; passphrase supplied by the Principal and written nowhere. | PM Pod B + the Principal | **BLOCKING** (P7) |
| **C9** | `binanceusdm` perpetual OHLCV ingested for BTC/ETH/SOL, bounded by the sealed ceiling at `C`. | head-of-data-infra | Blocking on **measurement**, not on sealing |
| **C10** **[R15 · WEIGHT INCREASED · 2026-08-06]** | **I-022** — the trial-count criterion stops returning a literal `True`. Until then the ~~80-trial~~ **[R15] 47-trial authorized** budget is enforced by this seat and by nothing else. **[R15 · 2026-08-06] C10's weight goes UP, not down.** It now bears on §10.5.2's **Stage 2 gate** as well as on the headline budget: a two-stage budget is a budget with a door in it, and the only code-level control that would refuse an over-budget spend is the one I-022 disables. **The door's key — `VIF_gate`, computed inside `evaluate_gate1` from the registry and printed on the report face — is held by the harness and not by this seat (V-1, V-2, M-10); the door's LATCH is I-022 and it is broken.** | head-of-data-infra | Blocking on **Gate 1**, not on sealing | **[R27 · 2026-08-10 · WEIGHT FALLS. I-022 IS REPAIRED IN CODE AND OPEN IN THE LOG.]** `gates.py:527–640` `_trial_budget_criterion` FAILs three ways — B-7 (`:598`), **B-9's ordering walk per trial naming k** (`:606–620`), B-23's malformed-extension branch [measured]. **The literal `True` I-022 quotes does not exist in `gates.py`.** `DATA-IMPL-007` §5: ***"Can close. All 19 test functions green"***, landed **2026-08-05** [cited]. **`VALIDATION-SPEC-003` §12 makes C10's discharge conditional on I-022 closing AND on this document registering Stage 1 as its sealed `trial_budget` — R-004 did the second at 47.** **Both of C10's conditions are met in substance; only the formal closure of I-022 is outstanding, and it is not this seat's.** Filed **I-142, MEDIUM.**
| **C12** **[R5 · 2026-08-04]** · **[R12 · 2026-08-05 · DISCHARGED, NARROWLY — see the note under this table]** | **The in-sample cadence sweep on the PRIMARY universe, to establish that K7 has no unnamed in-sample trigger.** Seat 9 measures, for **BTC and ETH** across the full span, the count of `funding_rate` prints per UTC day, and enumerates **every** date on which the count departs from 3 — **in both directions**. I-045's BTC control tests only `>3 prints` and **ETH was never the control** [measured — I-045], so the primary universe's cadence homogeneity is currently **asserted, not measured**. Any date found is a K7 trigger and **must be named in the sealed text by date**, alongside 2025-09-18 (§7.1.1). **This is a row-count query on `book/pit.db` and is NOT a trial** — the same class as §0's `COUNT(*)`/`MIN`/`MAX` diagnostics and as I-045's own measurement. Cost: a fraction of a Sonnet unit. | head-of-data-infra → quant-validation | **BLOCKING ON SEALING.** Sealing K7 while asserting an unverified homogeneity claim about the primary universe would be the I-045 defect committed a second time inside its own remedy. |
| **C11** | **The leg-(ii) null calibration (§5.5(e)).** A block-bootstrap or sign-randomization of the conditioning schedule against the realized `R_bench` series, average exposure held fixed, converting §5.3's `≤ 0.10` from **[assumed]** to **[measured]**. ≤ 2 trials. **This seat recommends Validation require it.** | Director of Research, on Validation's requirement | **Recommended BLOCKING on sealing** — see below |
| **C13** **[R11/R9 · NEW · 2026-08-05]** | **Validation's ruling, at the C2 intake and not separately, on three items R-002 puts in front of it: (1) the ML-2 non-fitted assertion at §21 and the §10.7(a) check that supports it — ACCEPTED or REJECTED, ML-2 making a partial ML block a Gate 0 rejection rather than a deferral; (2) whether §7.2's repaired escalation rule, whose operative content until I-053 is repaired is a HARD STOP, is the form Validation wants sealed, or whether it prefers the family to wait on the harness repair instead; (3) whether ML-17's own formula should be corrected to `(menu size − 1) × chain_total` per I-055, since RULING-004 copies this document's arithmetic and inherits its defect.** | Quant Validation | **NOT a separate blocker — resolved inside C2's intake verdict.** Listed so the intake knows what it is being asked, not to lengthen the blocker list. |
| **C13(e)–(h)** **[R-004 · 2026-08-10]** | **Four further items for C2's intake, none of them a new blocker.** **(e)** **`n_inherited = 7`** — does Validation accept `N_conditioning` registered in `n_inherited`, or does it rule the field reserved for inheritance from a predecessor chain only? **If it rules the latter, the 7 returns to being a floor nothing reads, §10.5.2's unlock table is permissive by 7 and by 8 trials at its two binding rungs, and this seat asks Validation to say which of those two outcomes it prefers, because there is no third.** **(f)** **The Stage 2 CONTINGENT extension** — is `predicate = {"name": "n_max_admits_declared_ceiling", "params": {}}`, `increment = 32`, self-issued by this seat under B-16, the form Validation wants, or does it require the **DISCRETIONARY** form with a countersignature? **(g)** **I-045** — `DIR-RESTATE-001` §10 puts three answerable questions to Validation; this seat declines closure for the fourth time. **(h)** **I-134 / I-135** — does the absence of any harness consumer for the 50% haircut and for `forward_kill_condition` bear on the Gate 0 verdict, or is disclosure sufficient? | Quant Validation | **NOT separate blockers — resolved inside C2's intake verdict.** | **[R28 · 2026-08-10] (i) THE PUBLISHED-SIGNAL HAIRCUT'S 2× PERMISSIVE GAP.** `published_signal_haircut_applied = 0.50` is class **(c)** — zero consumers, no haircut computation anywhere [measured]. **The bar `evaluate_gate1` computes is `t_gate ≥ 3.0` on un-haircut net returns; the bar §4.6 sets is the equivalent of 6.0.** **Does Validation apply §4.6's haircut by hand at Gate 1, and at which point of application (C5, still unruled)? If neither, this family can be reported PROCEED at half the Charter's bar** — the branch §5.4 R28 and §19.3 R28 now name. ~~**Not a new blocker; it is C5 given a size and a deadline.**~~ **[R31 · 2026-08-11] C5 IS NOW A LOCK — see §20's C5 row. The Principal has ruled that this family may not be evaluated at Gate 1 and that no PROCEED may be reported until C5 is ruled.** Filed **I-143, MEDIUM**; **I-152, MEDIUM** for the ruling's three-part structure and its §4 escalation. |
| **C13(j)** **[R30 · NEW · 2026-08-11]** | **HOUSE RULE 5's INSTRUMENT COSTS BETWEEN 0 AND 42 TRIALS, NOT ONE, AND STAGE 1 HAS ZERO SLACK.** `carry_breakeven_bps_annual` takes a **callable** and evaluates it once at `bracket[0]`, once at `bracket[1]`, and once per bisection step — **42 at the shipped `iters = 40`** — each evaluation being a `run_backtest` call and therefore a logged trial under the harness's own sanctioned usage (T-18) [measured — `carry.py:107, :113, :116–122`; `engine.py:248`; `test_carry_accounting.py:580–592`]. **Zero on the KILL path** (`t_lo < hurdle` returns at `:111–112`); **nine on the survive path at `iters = 8`**, resolution 7.8 bps/yr. **§15's Stage 1 line items sum to exactly 47.** **Three questions for Validation:** does the nine come from **Stage 2's contingent 32** (this seat's stated preference, untaken); or does Validation rule that **a monotone reporting statistic containing no selection does not deflate DSR and is not charged against `N`**; or must the family accept `iters ≤ 3` inside step 5's ≤ 5, at 250 bps/yr resolution on an 11–14%/yr carry, which this seat regards as a number that cannot discriminate? **This seat will NOT narrow the bracket** — the function returns its **endpoint** when the root lies outside it (`:111–115`), `VALIDATION-SPEC-002` §1286 records it doing exactly that once already, and narrowing to save trials is the **I-037 operation performed on the instrument built to avoid it** — **and will NOT reconstruct `net(δ)` outside the engine**, which costs zero trials and breaches **A2**. | Quant Validation | **NOT a separate blocker — resolved inside C2's intake verdict.** Filed **I-151, MEDIUM.** |
| **C13(k)** **[R32 · NEW · 2026-08-11]** | **THE SECOND C1, AND THE CONFORMANCE RUNS IN THIS FAMILY'S FAVOUR, WHICH IS WHY VALIDATION AND NOT THIS SEAT MUST RULE IT.** `forward_kill_condition`'s opening declares the observation date to be `C + 187 days` and that *"the DRAFTED DATE IS NOT BINDING — the formula is"*; **its clause 5 read *"if the computation is not performed on 2027-01-31 for ANY reason … the family is killed by default."*** At any seal after 2026-07-28 those two sentences **terminate this family with certainty** — the computation is not due on 2027-01-31, so clause 5 fires, and P7 makes it permanent. **R32 conforms the three `2027-01-31` literals in the field body to `C + 187 days`. No new rule is introduced and no threshold moves.** **Validation may refuse the conformance and require the literal sealed as drafted** — in which case the family accepts a window shortened by however long the seal took, **KC-002 clause (b)'s 30-conditioning-day threshold becomes correspondingly harder against a window calibrated at 187 days**, and this seat writes the KILL memo on the day without argument. **A sponsor deleting a clause that kills its own family does not get to rule on the deletion.** | Quant Validation | **NOT a separate blocker — resolved inside C2's intake verdict.** Filed **I-153, HIGH.**

> **[R12 · 2026-08-05] ON C12's DISCHARGE, AND WHY IT IS RECORDED AS NARROW RATHER THAN AS CLOSED.**
>
> **C12 as written asked for a print-count sweep on BTC and ETH, both directions, full span. It got one, and the result is clean: 0 deviating days of 4,802 symbol-days** [measured — `DATA-VERIFY-002` §3–§4], **with SOL's 11 deviating days as a working positive control that the instrument detects a break when one is there** [measured — I-045; Ruling 003 §A2]. **The condition is DISCHARGED and this seat, which created it, says so plainly rather than holding it open to look careful.**
>
> **It verified the CADENCE dimension only.** The documented 2025-09-18 firm-wide formula change shows **3 prints on both symbols** — a real, dated parameter change that a cadence sweep is structurally blind to. **K7 governs the parameter dimension by DECLARATION, not by measurement**, and §7.1.1's R12 note carries the full statement. **`DATA-VERIFY-002` must not be cited as evidence that the primary universe has no in-sample parameter break. It is not evidence about that at all.**
>
> **Two boundaries this seat observes rather than crosses.** **(1) I-045 is NOT closed by this revision** — its owner line routes closure to `quant-validation`, and C12's discharge is a different act on a different object. **(2) `DATA-VERIFY-002` §6 records that Seat 9 filed no Issue Log entry because its escalation rule was conditional on finding a deviation and none was found. That is correct** [cited], and this seat adds no entry either: **a clean measurement is not an issue, and the narrowness of what it covers is disclosed in this document rather than filed as a defect in Seat 9's work, which contained none.**

### 20.1 The sequencing call — this seat adopts Validation's ruling against its own earlier position

**The rationale this document originally carried is overturned and is not repeated.** The first draft argued: seal now, record C1 as unresolved on the face of the document, because `C` is the seal date and every day of delay is forward window that does not accrue. **That is the CIO's rationale from D-009, and Validation overturned it while this document was being written** [cited — I-030; `VALIDATION-GATE0-001` §4.3]:

> *delay is **strictly cheaper** than sealing defective, because P7 freezes the document permanently and the only remedy for a bad seal is a **successor family whose window starts later anyway** — so a bad seal buys nothing and forfeits the correction.*

**The argument is correct and it applies with more force here than it did there.** PREREG-001's unresolved condition would have frozen a decorative denominator. ~~**This family's would freeze a specification whose every P&L number is deterministically wrong by 32.85 points/yr, and freeze a falsifier one of whose four probabilities is assumed.**~~ **[R29/R32 · 2026-08-11] THE FIRST HALF IS SPENT AND THE SECOND HAS BEEN REPLACED BY SOMETHING WORSE.** The cost model was repaired on **2026-07-29**, so a seal today would freeze no sign error. **What a seal before today WOULD have frozen is a kill condition that terminates this family with certainty (R32, I-153), a condition precedent that downgrades it on a false premise (R29, I-140), and fifteen dated clauses whose premises are false.** The falsifier's assumed probability (C11) stands unchanged. **The argument survives its own premises being replaced, which is the strongest form in which it could survive:** a seal today buys days of forward window and forfeits the ability to fix any of them.

> ### **THIS SEAT'S SEQUENCING RECOMMENDATION, REVISED: DO NOT SEAL TODAY.**
>
> ~~**Seal when C1, C3 and C11 have landed** — the cost-model repair specified, the Devil's Advocate memo written, and leg (ii)'s null measured. **Realistic seal date: on or before sprint close, 2026-08-11.**~~
>
> ### **[R35/R36 · 2026-08-11 · THE DATED COMMITMENT IS STRUCK AND REPLACED BY A CONDITION, AND THE BLOCKING SET IS WRITTEN AS THE TWO SETS IT ALWAYS WAS.]**
>
> **`2026-08-11` IS TODAY, AND C2, C7, C8 AND C11 ARE OPEN.** *"Realistic seal date: on or before sprint close, 2026-08-11"* is **D-14 of the dated-clause sweep — a dated commitment nothing evaluates, false on the day it was written for, in the sweep's own author's document.** Retaining it would freeze that schedule under P7. **Struck.**
>
> **Replaced by: SEAL WHEN C2, C7, C8 AND C11 HAVE CLEARED, AND NOT BEFORE.** **C1 is DISCHARGED and is no longer a condition of any kind. C3 is not a seal condition** — §20's own column reads *"Blocking on Gate 1, not on sealing"* — **and R-005's block, which listed it among *"the same five open and blocking"* seal conditions, merged two kinds of block into one list.** That is the shape of error that produced I-140.
>
> | Set | Members | Meaning |
> |---|---|---|
> | **SEAL-BLOCKING** | **C2 · C7 · C8 · C11** | `open_hypothesis` may not be called until all four clear |
> | **VERDICT-BLOCKING** | **C3 · C5**, and by §20's own column also **C4** (Gate 1 scheduling) and **C10** (Gate 1; met in substance, formal closure of I-022 outstanding) | the family may be sealed and run; **no Gate 1 verdict and no PROCEED may exist** until these clear |
>
> **The directed set `C2, C3, C5, C7, C8, C11` is the union minus C4 and C10, and this seat names the two it drops rather than inheriting a list.**
>
> `C` moves with the seal, **KC-002's observation date moves with it to `C + 187 days` — which R32 has now made true of the sealed field's clause 5 as well as of its opening** — and the firm loses the intervening days of a forward window it will hold for at least twelve months.
>
> **What this costs, stated rather than minimized:** the intervening days of forward accrual, and ~~a KC-002 date that this document currently writes as 2027-01-31 and which must be restated as `C + 187 days` at sealing~~ **[R32 · 2026-08-11] a KC-002 date this document wrote as 2027-01-31 in FOUR places, three of them inside the sealed `forward_kill_condition` field including clause 5, and which R32 has now restated as `C + 187 days` everywhere. The restatement was not cosmetic: as drafted, clause 5 terminated this family with certainty (I-153).** **What it buys: the ability to fix a sign-inverted cost model and an assumed probability, neither of which P7 will let anyone touch afterwards.**
>
> **This seat had the other position four hours ago and states the reversal plainly rather than quietly adopting the new one.**

**I-027 is deliberately NOT a condition precedent for this family** (§10.3). It costs 0.13 years of required backtest length against 6.571 available. It remains open, it must still be disclosed on the Validation Report's face, and it must not be closed on the strength of this family's indifference to it. **Note also I-033(1): H2's seeding would make every seeded family read OVER BUDGET, since seeded `N` is compared against a budget counting only real runs. This family is unaffected — `n_inherited = 0` — and that immunity is a fact about this family, not evidence the defect is benign.**

---

## 21. THE SEAL BLOCK — exact binding field set for `TrialRegistry.open_hypothesis`

*P2 names the binding set exhaustively. These strings are what get hashed into `prereg_sha256` and shadow-copied into the `hypothesis_sealed` event. **Pod B executes this. This seat does not.*** ~~*Note that `n_inherited` is absent from the signature — I-027 — and is 0 for this family in any case.*~~

> **[R19/R23 · 2026-08-10 · THREE CORRECTIONS TO THIS SECTION'S PREAMBLE AND TO THE BLOCK BELOW.]**
>
> **(1) The struck sentence is false.** `n_inherited` **is** in the signature and **is** the sixteenth entry of `_BINDING_FIELDS` [measured — `registry.py`]. It is added to the block below at **7**. §10.3 carries the full statement.
> **(2) `open_hypothesis` IS THE SEAL.** P1: *"on first registration, computes `prereg_sha256`"* [measured]. **Registration and sealing are one operation, not two**, and this block is therefore not a preparation for a seal — executing it **is** the seal, and is a Standing Order 002 §4 hard interrupt.
> **(3) THE PAYLOAD GOVERNS.** `research/REGISTRATION-PAYLOAD-PREREG-002.md` carries the sixteen fields with their final values. **Anywhere this document's prose and that payload could diverge, the payload is what gets passed** — which is I-105's lesson stated as a rule rather than as a finding.

```
family                            = "funding-carry-conditioning-002"

statement                         = "On binance/binanceusdm, a delta-neutral long-spot / short-perpetual
                                     position in BTC and ETH earns perpetual funding; the UNCONDITIONED
                                     form of that position is crypto CARRY FACTOR exposure, which Charter
                                     5.4 attributes to Factor P&L and does not pay for. The claim under
                                     test is narrower: de-scaling that position as the realized funding
                                     rate rises above its own trailing 30-day baseline produces POSITIVE
                                     ALPHA to the unconditioned position, at the firm's own t >= 3.0
                                     hurdle, over 2020-01-01 to THE LAST SETTLED COMMON BAR OF THE PRIMARY
                                     UNIVERSE AT THE FIRST RUN [R43 - the window is bounded by the last
                                     ingested settled bar, which is what oos_index carries and what
                                     Validation section 7.3 has ruled governs; C is NOT redefined and keeps
                                     its meaning as the freeze instant], net of the full Charter 4.6 cost
                                     stack on both legs. Position: long 1.0 unit spot notional, short w(t)
                                     units perp notional, w(t) = clip(1.0 - k*max(0, z(t) - d), 0, 1.0),
                                     where z(t) is the deviation of the trailing-24h realized funding rate
                                     from its own trailing 30-day mean in units of that window's standard
                                     deviation. w never exceeds 1.0 and the position is NEVER long perp.
                                     PARAMETERS, AS NUMERIC LITERALS [R41]: k = 0.5, d = 1.0, band = 0.10,
                                     lookback = 30 days, w_max = 1.0. In words: FULL SIZE at or below one
                                     trailing standard deviation of excess funding, HALF SIZE at two, FLAT
                                     at three. Each literal is derived from the mechanism or from estimator
                                     arithmetic on the declared 30-day lookback and NOT from the series;
                                     derivation at DIR-RESTATE-001 section 14.2-14.4. w reaches 0 at
                                     z = d + 1/k = 3.0.
                                     DISCLOSURE, MECHANICAL REGISTER [R42 - the rule is DISCLOSED, not
                                     redesigned, by the Principal's ruling]: max(0, z - d) is ZERO whenever
                                     z <= d, so w = 1.0 - BENCHMARK WEIGHT, FULL SIZE - whenever realized
                                     funding is at or below its own trailing baseline, INCLUDING throughout
                                     a negative-funding regime. THIS RULE CANNOT ACT WHEN FUNDING IS CHEAP
                                     OR INVERTED. And the 30-day trailing baseline extends that: after a
                                     run of rich funding the baseline is high, so a cascade that collapses
                                     z holds w pinned at benchmark weight for up to thirty days AFTER the
                                     event. The rule reduces exposure to the APPROACH to crowding and holds
                                     full exposure through the REALIZATION. This is a deliberate risk
                                     posture under K2 option (1) - option (3), sign-flip to long-perp on
                                     inversion, was declared, considered and NOT selected - and it is NOT
                                     tail reduction in the inversion regime."

mechanism                         = "Perpetual funding is the rental price of leverage, not a mispricing.
                                     Who pays: (1) leveraged directional retail, for whom the perp is the
                                     cheapest and most accessible leveraged long in crypto - no expiry, no
                                     roll, no dated-contract basis, reachable by account types and
                                     jurisdictions that cannot access CME futures or prime brokerage;
                                     they keep paying because the alternative on offer is not a cheaper
                                     rate but not having the position; (2) structurally long allocators
                                     using perps as an index proxy to avoid self-custody, paying funding
                                     as a custody-and-operations substitute; (3) hedgers of illiquid
                                     crypto exposure - miners, token treasuries, locked positions - who
                                     are SHORT perp and are the mechanism of funding INVERSION in
                                     drawdowns, not of the positive premium.

                                     WHY THIS IS NOT ITSELF AN EDGE, stated at Gate 0: a premium that
                                     persists because it is a fair price for a service is not alpha.
                                     Binance's
                                     documented formula is F = [P_avg + clamp(interest - P_avg, -0.05%,
                                     +0.05%)] / (8/N) with interest FIXED at 0.01% per 8h, so whenever the
                                     premium sits inside [-4bp, +6bp] the funding rate equals the interest
                                     rate EXACTLY, regardless of the premium's value [cited - official,
                                     DATA-VERIFY-001 section 1.1]. Measured on the firm's own store: the
                                     in-band subset's mean funding is 0.986bp (BTC) and 1.114bp (ETH) -
                                     essentially exactly the 1.00bp interest rate - while mean basis over
                                     the same sample is NEGATIVE (-1.58bp BTC, -0.95bp ETH), and roughly
                                     35% of prints sit at the floor [measured - DATA-VERIFY-001 section
                                     5.2; DATA-INGEST-002 section 4]. THE ~11%/yr BASELINE IS THEREFORE AN
                                     ADMINISTERED CONSTANT SET BY THE EXCHANGE, NOT A MARKET-CLEARING
                                     PRICE: it is transferred from longs to shorts by contract rule on
                                     every day the premium falls inside a +/-5bp band, whether the market
                                     is crowded or empty, while the market-determined component averages
                                     slightly negative. THE FIRM HAS NO BASIS FOR ASSERTING THAT THE
                                     ADMINISTERED RATE IS ABOVE, AT, OR BELOW THE PRICE OF THE RISKS A
                                     CARRY SUPPLIER BEARS, AND THIS SEAT STATES THAT IT DOES NOT KNOW.
                                     The three risks are unchanged and real whatever compensates them:
                                     venue insolvency (FTX is the base rate, not a hypothetical),
                                     liquidation and basis dislocation during cascades, and funding
                                     inversion positively correlated with basis loss.
                                     THE CONCLUSION SURVIVES THE WITHDRAWAL ON WEAKER PREMISES, AND THAT
                                     IS STATED RATHER THAN GLOSSED: the withdrawn sentence argued the
                                     unconditioned carry is not alpha BECAUSE IT IS FAIRLY PRICED. That
                                     argument is gone. Charter 5.4 classifies carry as Factor P&L WHETHER
                                     OR NOT IT IS FAIRLY PRICED, so the unconditioned carry decomposes to
                                     100% Factor P&L and 0% idiosyncratic on the firm's own attribution
                                     scheme regardless of what the administered rate is worth, and the
                                     firm pays only for the third line. An argument resting on the firm's
                                     own classification rather than on an unverifiable equality is the
                                     stronger of the two.

                                     THE ACTUAL CLAIM: FUNDING IS A CENSORED OBSERVATION OF LONG-SIDE
                                     POSITIONING CROWDING - censored to the administered interest rate
                                     whenever the premium sits inside the +/-5bp clamp band, and therefore
                                     informative about crowding ONLY OUTSIDE THAT BAND. Consequence for
                                     the state variable, stated so it is not discovered later: the
                                     trailing 30-day mean and standard deviation that K1 normalizes by are
                                     MOMENTS OF A CENSORED SERIES, so z(t) is a z-score of a censored
                                     variable and both moments are biased relative to the premium's own.
                                     This is a stated property, not a defect to correct, because the
                                     strategy conditions on the cash flow it actually receives. WHY THE
                                     CENSORING ARGUES FOR K1 RATHER THAN AGAINST IT [inferred from the
                                     formula's structure; NOT measured]: because funding can depart from
                                     the floor ONLY when the premium escapes the band, the state
                                     variable's 'rich funding' state is BY CONSTRUCTION the state
                                     'crowding has become severe enough to overwhelm the administered
                                     rate' - so the conditioning fires on exactly the event the mechanism
                                     theorises about rather than on a continuous proxy for it.
                                     DATA-VERIFY-001 section 6.1 reaches the same conclusion by a
                                     different route ('no change to K1 is indicated... if anything it is
                                     reinforced') and this seat agrees; K1 IS UNCHANGED. WHAT THE
                                     CENSORING COSTS, in the same breath: on the ~35% of prints pinned at
                                     the floor [measured] funding is IDENTICALLY the interest rate and
                                     carries NO information about how rich the premium is, so the state
                                     variable is a mixture with a point mass whose entire informational
                                     content sits in the off-floor subset. THIS IS NOW THE LEADING
                                     CANDIDATE CAUSE OF DEATH FOR THE FAMILY, ahead of the bar-granularity
                                     argument that previously held that position: see the KC-002 clause
                                     (b) note. The premium is approximately LINEAR in crowding
                                     while cascade severity is CONVEX in it, because cascade depth depends
                                     on the stock of positions that must be force-closed. Beyond some
                                     funding level the marginal premium no longer pays for the marginal
                                     tail. Persistence escape selected: MANDATE SEGMENTATION - the
                                     marginal supplier of carry at scale runs it as a yield product
                                     (structured note, delta-neutral vault, exchange earn programme,
                                     treasury overlay) whose liability structure will not permit
                                     de-scaling: it advertises a yield and loses subscriptions when it
                                     stops earning it, de-scales on redemption cycles rather than risk
                                     signals, and is mandated in notional deployed rather than risk taken.
                                     Escapes REJECTED: (a) 'the premium is un-arbitraged' - rejected on
                                     its face, cash-and-carry is the most institutionalized trade in
                                     crypto; (b) capital constraint - decays with market maturation, an
                                     edge with an expiry date. FALSIFIER OF THE PERSISTENCE CLAIM:
                                     aggregate short-perp open interest FALLING as funding rises above its
                                     trailing baseline would show the supply side already de-scales and
                                     kills escape (c). Open interest is NOT in pit.db and NO LOADER
                                     EXISTS; this falsifier is declared unmeasured, not satisfied.
                                     REJECTED AS MECHANISM: 'leveraged longs are impatient' - a
                                     restatement of the observation, not an explanation.
                                     DISCLOSURE, ECONOMIC REGISTER [R42 - the finding is
                                     DISCLOSED, not redesigned, by the Principal's ruling]: population (3)
                                     above - hedgers of illiquid crypto exposure - is named in this same
                                     field as THE MECHANISM OF FUNDING INVERSION IN DRAWDOWNS, and the
                                     document's risk section places this family's left tail in exactly
                                     that regime. THE SIZING RULE CANNOT ACT THERE. It is one-sided by
                                     K2's selection: it de-scales only into funding that is RICH relative
                                     to its own trailing baseline, and holds BENCHMARK WEIGHT when funding
                                     is cheap or negative. A liquidation cascade is the event that
                                     DESTROYS the crowding the rule is keyed to - longs are force-closed,
                                     hedgers pile in short, realized funding collapses and inverts - so
                                     the rule carries FULL SIZE into and through it. Roughly a QUARTER of
                                     in-sample days sit in that state: 619 of 2,415 BTC days (25.63%) and
                                     609 of 2,415 ETH days (25.22%) carry at least one negative funding
                                     print [cited - REDTEAM-002 section 2.1, MEASURED BY THE DEVIL'S
                                     ADVOCATE by read-only count over stored prints; NOT this seat's
                                     number and NOT re-measured here]. HOLDING BENCHMARK WEIGHT THROUGH AN
                                     INVERSION IS A DEFENSIBLE RISK POSTURE AND IT IS THIS FAMILY'S. IT IS
                                     NOT TAIL REDUCTION, and no artifact from this family may present it
                                     as one. K2 option (3), sign-flip to long-perp when funding inverts,
                                     was declared in the menu, considered, and NOT selected; changing that
                                     selection now would be a post-hoc conditioning move priced by the
                                     section 7.2 escalation rule."

falsifier                         = "F-002. Computed from THREE runs through castellan.run_backtest
                                     against this family, on the same daily UTC index over the full
                                     in-sample [2020-01-01, THE LAST SETTLED COMMON BAR OF THE PRIMARY
                                     UNIVERSE AT THE FIRST RUN] [R43 - conformed from the
                                     former right edge 'C'. The in-sample window is bounded by the last
                                     ingested SETTLED bar, which is what oos_index carries and what
                                     Validation section 7.3 has already ruled governs; C is NOT redefined
                                     and keeps its meaning as the freeze instant, still defining
                                     forward_window_start, the holdout and KC-002's window. There is no
                                     seal date at which the former text was true, which is why the fix is
                                     to the right edge and not to C], all net of the full Charter 4.6 cost
                                     stack AS REPAIRED PER CONDITION PRECEDENT C1:
                                     R_bench = the UNCONDITIONED benchmark (delta-neutral long-spot /
                                       short-perp, CONSTANT notional w == 1.0, equal-weight, daily
                                       rebalance inside the turnover band);
                                     R_strat = identical except notional scaled by w(t) per the declared
                                       state variable, direction, cap and deadband;
                                     R_bench_scaled = the EXPOSURE-MATCHED benchmark, R_bench x c where
                                       c = (time-average gross exposure of R_strat) / (time-average gross
                                       exposure of R_bench) over the full in-sample - a CONSTANT-notional
                                       position holding the SAME AVERAGE SIZE as the conditioned strategy.
                                     The hypothesis is FALSIFIED if ANY of the following four legs fires:
                                     (0) INSUFFICIENT SAMPLE - fewer than 1,800 qualifying daily bars on
                                       the common primary-universe index (~75% of the 2,398 bars the span
                                       implies). Evaluated FIRST, and when it fires the verdict is
                                       INSUFFICIENT-DATA, NOT survival. Present because I-029(c) is filed
                                       against this seat: a falsifier with no minimum observation count is
                                       a statistic with a decimal point on noise, and one whose
                                       sample-size failure reads as 'not falsified' rewards missing data.
                                     (iii) NO PREMIUM TO CONDITION ON - annualized NET return of R_bench
                                       over the full in-sample <= 0. Cheapest leg; requires only the
                                       benchmark run; RUNS FIRST among the substantive legs; kills the
                                       family root and branch. H0: no funding premium net of costs.
                                     (i) NO ALPHA TO THE FACTOR - in the OLS regression R_strat = alpha +
                                       beta*R_bench + eps over the full in-sample, the NEWEY-WEST
                                       t-statistic on alpha at a 21-bar (one calendar month, pre-
                                       committed) lag truncation is <= 3.0 (Charter 4.2 T_STAT_HURDLE
                                       applied to the residual, not to the raw return). Newey-West rather
                                       than OLS because a carry residual is autocorrelated by construction
                                       and an OLS t on it is inflated in a known direction. H0: alpha = 0,
                                       statistic asymptotically standard normal, ALPHA = 0.0013 one-sided.
                                       If it fires, the conditioning contributes nothing the constant-size
                                       position did not have; the family is carry factor beta and Charter
                                       5.4 pays nothing for it.
                                     (ii) NO TAIL REDUCTION PER UNIT OF EXPOSURE GIVEN UP - the mean of
                                       R_strat's 20 WORST daily net returns is not better (less negative)
                                       than the mean of R_bench_scaled's 20 worst daily net returns by at
                                       least 25%. THE COMPARISON IS AGAINST THE EXPOSURE-MATCHED
                                       BENCHMARK, NEVER AGAINST R_bench: R_strat is a re-weighted R_bench,
                                       so ANY rule that reduces average size mechanically improves the
                                       tail whether or not the mechanism is real, and comparing against
                                       R_bench would bias this leg toward the falsifier's own survival -
                                       I-029(d) transposed from a lag axis to a size axis. Matching
                                       average exposure forces any tail improvement to come from WHEN size
                                       was reduced rather than from HOW MUCH on average. H0: the
                                       conditioning's timing carries no tail information; P(leg fails to
                                       fire | H0) <= 0.10 [ASSUMED - the one term in this chain that is
                                       not derived; condition precedent C11 measures it by block-bootstrap
                                       or sign-randomization of the conditioning schedule against the
                                       realized R_bench with average exposure held fixed, and this seat
                                       RECOMMENDS Validation require it before sealing].
                                       DISCLOSURE, EVIDENTIAL REGISTER, BINDING ON HOW LEG (ii) MAY BE
                                       READ [R42]: the sealed sizing rule is ONE-SIDED -
                                       max(0, z - d) is zero whenever funding is at or below its own
                                       trailing baseline - so the rule holds BENCHMARK WEIGHT throughout
                                       the negative-funding regime, which is roughly a quarter of
                                       in-sample days [cited - REDTEAM-002 section 2.1, measured by that
                                       seat] and is the regime this document's own mechanism and risk
                                       sections name as where the left tail lives. THEREFORE: whatever
                                       tail improvement leg (ii) measures CANNOT ORIGINATE IN THE
                                       INVERSION REGIME, and leg (ii) failing to fire MUST NOT be read,
                                       in any artifact from this family, as evidence of tail protection
                                       in inversion. What leg (ii) can establish is narrower and is the
                                       claim actually under test: tail reduction on the APPROACH to
                                       crowding, achieved by choosing WHEN to be small. The rule is
                                       disclosed here and is NOT redesigned - the Principal's ruling - and
                                       K2 is unchanged.
                                     Any single leg firing is sufficient. NO LEG CONTAINS AN ARGMAX, A
                                     PEAK, A GRID SEARCH, OR ANY SELECTION OVER CANDIDATES; there is no
                                     lag dimension because the strategy holds both legs simultaneously and
                                     continuously and there is nothing to time. Thresholds pre-committed
                                     with stated bases: t >= 3.0 is Charter 4.2, not invented here; 20
                                     days is ~0.83% of the 2,398-bar in-sample, the conventional ~1% tail
                                     cut and the smallest window that is not a single-observation
                                     artifact; 25% is a declared materiality margin so the leg neither
                                     fires nor spares on noise; 1,800 bars is ~75% of the implied count;
                                     zero is the only non-arbitrary floor for leg (iii).
                                     JOINT FALSE-SURVIVAL RATE, the figure I-029 requires and which F-001
                                     never stated: P(F-002 survives | the conditioning is pure noise) <=
                                     0.0013 x 0.10 ~ 1.3e-4, against F-001's MEASURED 31% [cited, I-029] -
                                     a factor of roughly 2,400, structural rather than tuned. Under the
                                     joint null that there is also no premium, leg (iii) fires with
                                     probability > 0.95 on its own and joint survival falls below 1e-5.
                                     F-002 is registered as N=3 (three backtest runs), plus C11's <= 2 if
                                     required. It is DISTINCT FROM and ADDITIONAL TO the kill condition
                                     KC-002.
                                     E2 DISCIPLINE, BINDING (Validation C-001): F-002 is evaluated ONCE,
                                     on the first complete run of the three series under the repaired
                                     cost stack [R29, 2026-08-11: "after C1 lands" STRUCK - C1 is
                                     DISCHARGED, the repair landed 2026-07-29, and the contingency
                                     this clause guarded against cannot now arise; the clause is
                                     retained in the general form it always had, ANY post-computation
                                     change to the cost stack making the recomputation a NEW FAMILY]. There
                                     is NO re-run 'with the corrected costs', no second look, no 'we also
                                     checked'. If C1's repair changes the cost stack after F-002 has been
                                     computed, that is a NEW FAMILY, not a re-computation - a falsifier
                                     that may be re-run until it spares the family is not a falsifier.
                                     NOTE ON THE HAIRCUT: F-002 leg (i) tests the PRE-haircut t(alpha);
                                     Gate 1's t >= 3.0 applies POST the R4(b) 50% haircut, which halves
                                     expected return without touching the standard error, so Gate 1
                                     clearance requires a pre-haircut t(alpha) of roughly 6.0. These are
                                     DELIBERATELY DIFFERENT BARS and must not be conflated: F-002 asks
                                     whether the family should continue to exist, Gate 1 whether it should
                                     receive capital. A family clearing F-002 but not Gate 1 is written up
                                     as PARK-WITH-TRIGGER, not PROCEED."

universe                          = "Venue: binance (spot) and binanceusdm (perpetual). SINGLE VENUE, both
                                     legs. UNIVERSE: BTC/USDT and ETH/USDT spot paired against
                                     BTC/USDT:USDT and ETH/USDT:USDT perpetuals, common span 2020-01-01 to
                                     C = 6.571 years [SUPERSEDED - S3-D-019, 2026-08-12: ingest ran; common
                                     span re-measured at 6.612 years (2415 days, through the currently-
                                     forming terminal bar) / 6.609 years (2414 days, last SETTLED bar only);
                                     see PREREG-002 section 11.1 In-sample row for full detail], zero gaps
                                     [measured]. THERE IS NO SECONDARY
                                     UNIVERSE. 
                                     REASON, per I-045: Binance changed SOLUSDT's funding settlement
                                     frequency and raised its Capped Funding Rate Multiplier from 0.75 to
                                     1 - taking the cap to +/-2.00%, roughly 40x the default +/-0.05% band
                                     - announced 2022-11-09 20:00 UTC [cited - official, DATA-VERIFY-001
                                     section 3.2]. Three independent series date the same break: the
                                     vendor announcement; a measured funding-cadence break (0 of 787 days
                                     with >3 prints BEFORE, 11 including the day itself AFTER, with the
                                     BTC CONTROL AT 0 AND 0) [measured - I-045, reconciling to one day
                                     with VALIDATION-RULING-003 section A2's independent count of 11 of
                                     2,145 days]; and a measured -1,690.34bp basis dislocation on the same
                                     date [measured - DATA-INGEST-002 section 4]. SOL'S FUNDING SERIES IS
                                     GENERATED BY DIFFERENT FORMULA PARAMETERS BEFORE AND AFTER THAT DATE,
                                     SO K1'S Z-SCORE DOES NOT DENOTE THE SAME OPERATIVE STATE ACROSS THE
                                     SAMPLE - a DATA-HOMOGENEITY defect, not a regime-exclusion question.
                                     THE TWO REMEDIES THAT WOULD HAVE KEPT SOL ARE UNAVAILABLE AND THE
                                     REASONS ARE CITED, NOT PREFERRED: (a) a per-contract time-varying
                                     documented-parameter table cannot be populated - Binance states
                                     verbatim 'there may be further adjustments to the funding rate
                                     settlement frequency... there will be no further announcement on such
                                     adjustments', the live fundingInfo endpoint returns TODAY'S SNAPSHOT
                                     ONLY, and no historical parameter series is known to be published
                                     [cited - official, DATA-VERIFY-001 sections 2, 3.2, 7(4)]; (b) a
                                     declared break control needs TWO dates and the firm can cite ONE -
                                     the break's START is documented, its END is not and the vendor states
                                     it will not be, so the closing boundary would have to be chosen from
                                     the data (the measured cadence revert is a proxy for a DIFFERENT
                                     parameter than the clamp cap), which is the I-029(d) operation -
                                     setting a control's boundary from the data the control exists to
                                     protect - for a third time in this firm. WHAT THE DROP DOES NOT COST:
                                     F-002 is computed on the common PRIMARY-universe index (BTC, ETH), so
                                     NO LEG OF F-002 EVER READ SOL and SOL's 2022-11-10 tail realization
                                     (-0.17166 accrual on -1.0 perp notional [measured -
                                     VALIDATION-RULING-003 T-9]) was never inside the test; that
                                     realization is in any case NOT usable as forward evidence, its
                                     magnitude having required the +/-2.00% cap then in force [inferred
                                     from cited]. WHAT IT DOES COST, recorded pre-seal: the universe's
                                     largest in-sample basis excursions are -73.65bp (BTC) and -102.95bp
                                     (ETH), both 2020-03-12 [measured - DATA-INGEST-002 section 4] -
                                     roughly an ORDER OF MAGNITUDE milder than SOL's - so F-002 LEG (ii)
                                     IS A TAIL TEST ON A MILD TAIL AND ITS SURVIVAL IS WEAKER EVIDENCE OF
                                     TAIL REDUCTION THAN THE LEG'S CONSTRUCTION IMPLIES; and the firm
                                     loses a corroborating report on the one asset whose funding behaved
                                     differently (annualized mean funding SOL +0.10% against BTC 11.86%
                                     and ETH 14.07% [measured]). RULING 003'S ACCEPTANCE SUITE IS
                                     UNAFFECTED: T-9's fixture is over STORED DATA, not over the traded
                                     universe, SOL's prints and perp OHLCV remain in pit.db, and the test
                                     guarding against a cadence constant continues to run on the window
                                     that most needs guarding. Unit of
                                     observation: the ASSET-DAY, one daily UTC bar of one (spot, perp)
                                     pair. Position: long 1.0 unit spot notional, short w(t) units perp
                                     notional, w in [0, 1.0]; w = 1.0 for the benchmark; NEVER long perp.
                                     P_notional = USD 125,000 per asset; intended initial allocation USD
                                     250,000; gross at w=1.0 is USD 500,000 (two legs). Capacity screen:
                                     trailing-20-session median daily notional >= 20 x P_notional = USD
                                     2,500,000 per leg per asset, evaluated on a window ending STRICTLY
                                     BEFORE the day screened. Regime cells {funding positive, negative} x
                                     {trailing spot vol above, below own median} are all TRADED and all
                                     REPORTED SEPARATELY; pooled figures never stand alone. Raw AND
                                     effective observation counts reported side by side (BTC and ETH
                                     co-move; N_eff will be far below 2).

                                     REGIME-CONDITIONING DECLARATION (Principal's binding rider - the
                                     choice AND the menu it was chosen from):
                                     K1 STATE VARIABLE. Chosen: deviation of realized funding from its own
                                       trailing 30-day mean, in units of that window's standard deviation.
                                       Menu of 10: (1) raw funding level; (2) CHOSEN; (3) funding sign
                                       only; (4) trailing realized spot volatility; (5) spot trend
                                       /momentum; (6) spot drawdown from trailing high; (7) basis level
                                       (perp-spot); (8) cross-asset funding dispersion; (9) calendar
                                       (day-of-week / funding-print-of-day); (10) no conditioning at all.
                                     K2 DIRECTION. Chosen: DE-SCALE into rich funding; w falls as z rises;
                                       w never exceeds 1.0; never long perp. Menu of 3: (1) CHOSEN;
                                       (2) up-scale at extremes (funding momentum); (3) sign-flip to
                                       long-perp when funding inverts.
                                     K3 PERIOD EXCLUSIONS. Chosen: NONE. Full span, INCLUDING COVID-Mar
                                       2020, May-2021, LUNA/UST May-2022, FTX Nov-2022, the 2022 bear, the
                                       2024 spot-ETF approval, and every negative-funding episode. Menu of
                                       9: (0) CHOSEN - exclude nothing; (1) COVID; (2) May-2021; (3) LUNA;
                                       (4) FTX; (5) 2022 bear; (6) pre-ETF; (7) first n months post-
                                       listing as illiquid; (8) negative-funding regimes.
                                     K4 ASSET UNIVERSE. 
                                       Chosen: BTC+ETH ONLY, SOL DISCARDED ENTIRELY.
                                       Menu of 5, UNCHANGED: (1) BTC only; (2) BTC+ETH primary with SOL
                                       reported separately [WAS CHOSEN, now superseded]; (3) BTC+ETH+SOL
                                       pooled on the 5.87-yr common span; (4) CHOSEN; (5) a wider
                                       alt universe (not ingested).
                                     K5 VENUE. Chosen: binance/binanceusdm only. Menu of 5: (1) CHOSEN;
                                       (2) coinbase; (3) bybit; (4) kraken; (5) cross-venue pooled.
                                     K6 BAR GRANULARITY. Chosen: DAILY UTC. Funding is
                                       aggregated as the EXACT ARITHMETIC SUM of all realized funding_rate
                                       prints whose event_time falls in the bar's window, LEFT-OPEN
                                       RIGHT-CLOSED (t-1, t], with NO assumed cadence, no mean, no
                                       annualization and no periods_per_year - i.e. pit_funding_panel
                                       exactly as ruled [cited - VALIDATION-RULING-003 section 3.2 and its
                                       alignment rule; acceptance test T-9 fails any implementation
                                       multiplying by a fixed prints-per-day constant]. THIS IS A DEFECT
                                       REPAIR, NOT A DESIGN CHANGE: the harness path was already correct
                                       and this document's prose was not, and sealing the prior text would
                                       have frozen a binding field contradicting the sanctioned
                                       implementation. IT IS NOT CONFINED TO SOL AND DOES NOT GO AWAY WITH
                                       SOL: Binance reserves the right to change ANY symbol's cadence
                                       without announcement [cited - official, DATA-VERIFY-001 section
                                       3.2], and this family's holdout is FORWARD with KC-002 computed
                                       forward, so a cadence change on BTC or ETH inside that window is a
                                       live exposure the prior clause would have mis-specified.
                                       Menu of 4, UNCHANGED: (1) CHOSEN; (2) 8h (the
                                       funding-print cadence); (3) 1h; (4) 1m.
                                     K7 TREATMENT OF A DOCUMENTED FUNDING-PARAMETER CHANGE ON A UNIVERSE
                                       SYMBOL. 
                                       Chosen (1): on ANY documented change to the funding formula, or to
                                       a universe symbol's per-contract funding parameters (settlement
                                       interval, clamp cap, or interest rate), THAT SYMBOL'S STATE
                                       VARIABLE z(t) IS INSUFFICIENT-DATA FOR THE DECLARED
                                       TRAILING-BASELINE LENGTH - 30 DAYS - BEGINNING ON THE CHANGE DATE,
                                       during which the symbol is HELD AT BENCHMARK WEIGHT w = 1.0; the
                                       change is filed to the Issue Log by Seat 9 and escalated to
                                       Validation. Menu of 5: (1) CHOSEN; (2) exclude the affected
                                       symbol's bars for that window; (3) exclude the affected symbol for
                                       the whole post-change period; (4) drop the affected symbol from the
                                       universe on the change date; (5) no special treatment - pool across
                                       the change.
                                       WHY OPTION (1) AND NOT ANOTHER: (i) NO FREE PARAMETER - the window
                                       length is the ALREADY-DECLARED 30-day K1 lookback, not a new
                                       number, and is exactly the interval over which the trailing
                                       baseline mixes two generating processes, so it is DERIVED rather
                                       than chosen (this is the specific respect in which K7 differs from
                                       the break control rejected above, which needed a CLOSING boundary
                                       the record does not contain); (ii) IT EXCLUDES NOTHING, SO K3
                                       SURVIVES INTACT AT 'EXCLUDE NOTHING' - bars are traded, returns
                                       counted, costs charged, and only the CONDITIONING INPUT is declared
                                       unavailable, whereas options (2)/(3)/(4) would each have forced a
                                       change to K3; (iii) THE DEFAULT IS THE CONSERVATIVE DIRECTION -
                                       holding w = 1.0 reverts to the benchmark, so the family FORGOES any
                                       claimed benefit over the affected interval rather than claiming one
                                       computed on a corrupted input; (iv) THE TRIGGER IS MECHANICAL, NOT
                                       INTERPRETIVE - 'a documented change to the formula or parameters'
                                       is an observable, whereas 'a change that materially alters the
                                       generating process' would require a run-time judgment, which is a
                                       researcher degree of freedom wearing a rule's clothing; mechanical
                                       and slightly over-inclusive is the correct trade in a
                                       pre-registration and its over-inclusion costs conditioning days in
                                       the conservative direction.
                                       THE ONE KNOWN IN-SAMPLE TRIGGER, NAMED BY DATE SO NO DISCRETION
                                       EXISTS AT RUN TIME: 2025-09-18, on which Binance changed the
                                       funding formula FIRM-WIDE, introducing the /(8/N) divisor [cited -
                                       official, DATA-VERIFY-001 section 3.1]. Its arithmetic effect on
                                       BTC and ETH is NIL while both remain on the 8-hour default, since
                                       8/8 = 1 [cited - same]. UNDER A MECHANICAL TRIGGER IT FIRES
                                       REGARDLESS, AND THIS SEAT DECLARES THAT IT DOES: BTC and ETH carry
                                       z(t) = INSUFFICIENT-DATA and w = 1.0 for the 30 days from
                                       2025-09-18. Condition precedent C12 requires Seat 9 to establish,
                                       BEFORE SEALING, that no OTHER in-sample trigger exists on BTC or
                                       ETH - I-045's control tests only '>3 prints' and only on BTC, so a
                                       cadence LENGTHENING would not have been caught and ETH was never
                                       measured at all.
                                     N CONTRIBUTION: 7 - one per choice, K1
                                     through K7. K4's change is NOT a new contribution: its selection
                                     moved WITHIN its already-declared menu of 5, before any measurement,
                                     against a registry holding 0 families and 0 trials [measured] - the
                                     menu did not grow, nothing was searched over, and K4 continues to
                                     contribute 1. The entire increment is K7. THIS SEAT TOOK THE
                                     CONSERVATIVE READING DELIBERATELY: a defensible case exists that K7
                                     is a DATA-VALIDITY RULE triggered by a vendor's documented act rather
                                     than a researcher's conditioning choice and therefore contributes 0,
                                     and D-009 records that erring LOW on N is the sycophantic direction,
                                     so this seat declares 1 and invites Validation to rule it down rather
                                     than declaring 0 and inviting Validation to rule it up. Each was made BEFORE any
                                     measurement, from a menu declared IN THIS SEALED PRE-REGISTRATION,
                                     and is BINDING; a choice involving no search over results contributes
                                     1, not the menu size, and the menu declaration is what makes that
                                     checkable.
                                     BINDING ESCALATION. 
                                     THE REPLACEMENT, BINDING: any revision to any of K1-K7 after any
                                     result on this family is seen is refused by P3 and requires a
                                     SUCCESSOR FAMILY under predecessor_family opened with
                                     n_inherited = (menu size of the revised choice - 1) x this family's
                                     final n_trials, the product of (menu size - 1) across dimensions where
                                     more than one is revised, SO THAT THE SUCCESSOR'S family_stats
                                     DENOMINATOR - which already sums this chain transitively - TOTALS THE
                                     INTENDED menu_size x chain_total; the successor inherits neither
                                     schedule nor allocation nor narrative. AND, BECAUSE THAT REGISTRATION
                                     IS REFUSED BY THE HARNESS AS IT STANDS, THE OPERATIVE CONTENT UNTIL
                                     I-053 IS REPAIRED IS: A POST-RESULT REVISION OF ANY OF K1-K7
                                     TERMINATES THE LINE. The successor cannot be registered, an
                                     unregistered family cannot run a backtest (A2), and THIS DOCUMENT
                                     FORBIDS BY NAME the one move that would obtain a registration -
                                     declaring a LOWER n_inherited than the escalation requires in order to
                                     satisfy the guard. That is the under-declaration I-053 names as 'the
                                     one that will be taken under schedule pressure', it is Appendix B #2,
                                     and no seat may take it on this family for any reason including that
                                     the alternative is abandoning a line of work. The harness change is
                                     ESCALATED, NOT ASSUMED: I-053's repair is an explicit Validation-
                                     authorized route that PRESERVES THE RAISE BY DEFAULT and permits
                                     registration only against a logged n_inherited_escalation_authorized
                                     event, against pre-authored acceptance test ML-T-14 which requires
                                     BOTH halves - a change that merely removes the guard fails it [cited -
                                     I-053; RULING-004 section 11.5]. Owner: head-of-data-infra. This
                                     family is NOT blocked on it: the hard stop is the sealed behaviour,
                                     and if the repair lands the escalated registration becomes available
                                     at (menu size - 1) x chain_total WITHOUT ANY AMENDMENT TO THIS FAMILY,
                                     because this sealed text already names that quantity.
                                     COUNTERFACTUAL, recorded so
                                     the rider's value is legible: had K1-K7 been selected AFTER seeing
                                     results, the product would be 10 x 3 x 9 x 5 x 5 x
                                     4 x 5 = 135,000 [arithmetic on declared menu sizes; NO market data
                                     touched, NO new statistic computed]. MinBTL is MONOTONE INCREASING in
                                     N, so the measured MinBTL(27,000, SR 1.0) = 16.79 years against 6.571
                                     [SUPERSEDED - S3-D-019, 2026-08-12: 6.612 (or 6.609 settled-only); see
                                     section 11.1. Conclusion below UNCHANGED - 16.79 exceeds either figure
                                     by more than an order of magnitude and this bound does not move]
                                     available is now a LOWER BOUND on the counterfactual requirement -
                                     the same arithmetic death sentence MinBTL(31,250) = 17.06 imposes on
                                     forward-lag-001, and strictly worse. No new number is computed and
                                     none is needed: bounding the consequence from an already-measured
                                     figure is the correct treatment under A2 against a 0-trial registry.
                                     EXPLICITLY NOT CONDITIONED ON, checked deliberately: no excluded
                                     period, date range or event window; no post-event window; no
                                     volatility-state filter (volatility is a REPORTING cut only, never a
                                     filter on what is traded); no funding-sign filter (excluding the
                                     negative-funding regime is the most tempting and most dishonest
                                     exclusion available to this family and K3 forbids it); no basis-level
                                     filter; NO WINSORIZATION, OUTLIER REMOVAL OR RETURN CLIPPING anywhere
                                     at any stage (a short-tail strategy that winsorizes its own tail is
                                     not measuring itself); no survivorship screen - [R3, 2026-08-04] BTC
                                     and ETH are TWO named continuously-listed instruments, not a screen
                                     output. ON THE ONE HAZARD THE R3 DROP CREATES, NAMED RATHER THAN LEFT
                                     IMPLICIT: removing an asset from a universe after the firm has looked
                                     at its data is, in general, exactly the operation N accounting exists
                                     to price. THREE FACTS MAKE IT ADMISSIBLE HERE AND ALL THREE ARE
                                     CHECKABLE: (i) the reason is a DOCUMENTED VENDOR ACT DATED 2022-11-09
                                     [cited - official], not a property of SOL's returns; (ii) NO RETURN
                                     STATISTIC ON SOL HAS EVER BEEN COMPUTED BY THIS FAMILY - the registry
                                     holds 0 trials [measured] - so there is no result the drop could have
                                     been selected on; (iii) the destination WAS ALREADY ON K4'S DECLARED
                                     MENU as option (4) before I-045 existed. HAD ANY OF THE THREE BEEN
                                     FALSE, THE CORRECT MOVE WOULD HAVE BEEN A SUCCESSOR FAMILY, NOT AN
                                     EDIT."

horizon                           = "CONTINUOUS. No event trigger, no target, no stop, no maximum holding
                                     period - a stop on a delta-neutral carry position converts a
                                     mean-reverting basis excursion into a realized loss at the worst
                                     moment, the second-order effect Charter 5.2 names explicitly. Risk is
                                     managed by SIZE, which is what the hypothesis is about. Daily
                                     rebalance subject to a turnover band: no trade unless
                                     |w_target - w_held| > band, where band = 0.10 [R41 -
                                     NUMERIC LITERAL. Derived from cost arithmetic ALONE, because the two
                                     survival conditions pull this parameter in OPPOSITE directions -
                                     widening it lowers cost and eases F-002 leg (i) while making KC-002
                                     clause (b) harder - and neither may therefore choose it. The
                                     principle: the smallest rebalance the band authorizes must cost less
                                     than the daily carry it adjusts. Only the perp leg moves, at roughly
                                     24 bp round-trip [cited, D-013 section 4] against roughly 3.25 bp/day
                                     of carry on that notional at the measured 11.86%/yr BTC funding
                                     [measured, DATA-INGEST-002 section 4], giving delta-w <= 0.135;
                                     rounded down. At 0.10 the smallest authorized trade costs 2.4 bp,
                                     about three-quarters of one day of carry. NOTED AND RUN AFTER THE
                                     CHOICE, NOT BEFORE: 0.10 < 0.25, so the band cannot suppress a KC-002
                                     clause-(b) day; that check ran in the family's favour and is
                                     disclosed as post-hoc]. run_backtest(execution_lag=1): the weight
                                     decided at bar t's close earns returns from t+1; execution_lag < 1
                                     raises SameBarFillError and is not waivable. periods_per_year = 365 -
                                     crypto trades every calendar day and there are no session gaps on
                                     either leg. Bars daily, UTC, both legs from the same venue and both
                                     24/7, so I-024's cross-venue clock confound HAS NO SESSION BOUNDARY
                                     TO HIDE IN here: no overnight gap, no weekend gap, no asynchrony,
                                     and the strategy is not a lead-lag strategy - it holds both legs
                                     simultaneously and continuously. Funding is knowable at 16:00Z on day
                                     t (the day's last print), consumed as a decision input at day t's
                                     close, filled at t+1 - a genuine 8-hour margin, not a boundary case.
                                     All trailing windows (30-day funding baseline, volatility cut,
                                     capacity screen) end STRICTLY BEFORE the day screened. Neither leg
                                     has splits or dividends, so A4's vendor-pre-adjustment hazard does
                                     not exist for this family; I-020 is a yfinance defect and no yfinance
                                     series is used, which is stated so this is not read as a general
                                     clearance of I-020. Declared limitation carried from DATA-INGEST-001
                                     section 3: every backfilled row carries knowledge_time = the
                                     ingestion instant, so this family may NOT claim to have tested
                                     point-in-time KNOWLEDGE for dates before its ingest session; it tests
                                     point-in-time ORDERING, which is what the hypothesis needs."

success_criteria                  = "
                                     NO NUMBER REPORTED BY THIS FAMILY IS SELECTED BY COMPARING CANDIDATES
                                     ON A QUANTITY COMPUTED FROM THE SAMPLE.
                                     This family is NOT a fitted family under RULING-004 ML-1 and ML-3
                                     through ML-27 do not reach it. The assertion is checkable and section
                                     10.7(a) is the check, choice by choice: K1-K7 were each selected
                                     BEFORE any measurement from a menu declared in this document against
                                     a registry holding 0 families and 0 trials [measured], and K4's R3
                                     move - the only selection that changed after data existed - moved on a
                                     DOCUMENTED VENDOR ACT DATED 2022-11-09, not on any statistic, with no
                                     return statistic on SOL ever computed by this family; the +/-50%
                                     parameter grid compares candidates on the sample but the configuration
                                     that ADVANCES is the PLATEAU CENTROID FIXED BY RULE, never the argmax,
                                     which is ML-1's own boundary case verbatim ('a family becomes a fitted
                                     family the moment any selection is made at an argmax rather than by a
                                     declared rule'); THE >=10 WALK-FORWARD WINDOWS ARE EVALUATED AT THE
                                     FIXED PLATEAU-CENTROID CONFIGURATION AND NO WINDOW RE-SELECTS,
                                     RE-FITS BY COMPARISON, OR REPORTS A PER-WINDOW OPTIMUM [R11 - this was
                                     UNSPECIFIED before this revision, and an unspecified walk-forward
                                     would most likely have been implemented as a per-window
                                     re-optimization, which WOULD have fired ML-1 and charged the grid's
                                     full cardinality PER WINDOW; sealing the silence would have left the
                                     fitted/not-fitted question to whoever wrote the loop, after C]; and
                                     F-002 contains no argmax, no grid, no peak and no selection of any
                                     kind. IF ANY ROW OF THAT CHECK IS LATER FOUND WRONG, THIS ASSERTION IS
                                     FALSE IN A SEALED FIELD, WHICH IS A HEAVIER CONSEQUENCE THAN A WRONG
                                     VERDICT AND IS THE CORRECT WEIGHT FOR IT.
                                     ML-13 accordingly leaves this document's N accounting INTACT and the
                                     reason is the discount's own stated condition, satisfied choice by
                                     choice above rather than asserted: N_conditioning = 7, trial budget
                                     79, ceiling N = 86, MinBTL(86, SR 1.0) = 6.14 years against 6.571
                                     [SUPERSEDED - S3-D-019, 2026-08-12: 6.612 (6.609 settled-only); margin
                                     widens from 0.43 to ~0.47 yr; MinBTL(86) itself unrecomputed; see
                                     section 11.1]
                                     available. THE ASYMMETRY RECORDED AGAINST THIS FAMILY'S INTEREST: the
                                     discount from 135,000 to 7 rests on a condition the family asserts
                                     about itself, whose enforcement is section 7.2's escalation rule - and
                                     R9 establishes that that enforcement was INOPERATIVE between R-001 and
                                     R-002 (I-053). That is the sharpest criticism available against this
                                     family's N accounting and this seat raises it rather than leaving it
                                     to the Red-Team Memo.
                                     [R13/R14/R15/R16/R17, 2026-08-06, PRE-SEAL - THE CEILING IS A
                                     FUNCTION AND THE BUDGET IS STAGED AGAINST A DECLARED RHO. The line
                                     above reading 'trial budget 79, ceiling N = 86' is the R-002 figure
                                     and is SUPERSEDED AS AN AUTHORIZATION: AUTHORIZED trial budget = 47,
                                     declared ceiling N = 54, against N_max(rho_plan = 0.10) = 55 [cited].
                                     A further <= 32 trials are DECLARED AND NOT AUTHORIZED and reach
                                     budget 79 / ceiling 86 ONLY at a measured rho_hat <= 0.034. Neither
                                     N_conditioning (7) nor the MinBTL figures move; what moves is what
                                     may be SPENT.]
                                     [R20, 2026-08-10, PRE-SEAL - I-105's DISCHARGE. THE TWO-STAGE
                                     BUDGET IS A REGISTRATION ACT, NOT A PROSE ACT, AND UNTIL THIS
                                     REVISION IT WAS THE SECOND. THE SEALED trial_budget IS 47 - STAGE
                                     1 - AND STAGE 2 IS NOT IN IT AND IS NOT ADDED TO IT. Sealed at the
                                     flat 79, gates.py reads 79, NO CONTINGENT PREDICATE IS EVER
                                     EVALUATED, and every sentence above describing a staged unlock
                                     would describe - in a frozen document, permanently under P7 - a
                                     gate that does not exist. Stage 2 survives ONLY as the description
                                     of a registered unlock event: a trial_budget_extension event in
                                     the registry's append-only events table, written AFTER the seal,
                                     in VALIDATION-SPEC-003's CONTINGENT form, with mode CONTINGENT,
                                     increment 32, predicate {name: n_max_admits_declared_ceiling,
                                     params: {}} - the vocabulary being CLOSED with exactly one member
                                     and params REQUIRED EMPTY (B-17) - authorization_ref pointing at
                                     this document, and n_logged_at_issue cross-checked against the
                                     trial ledger (B-21). The criterion computes declared_ceiling_base
                                     = n_inherited + sealed = 7 + 47 = 54, recomputes N_max =
                                     min(n_max_admissible_iid, n_max_admissible_serial) AT EVERY
                                     EVALUATION, and admits clamp(N_max - 54, 0, 32). IT NEVER TRUSTS
                                     THE EVENT'S ASSERTION THAT THE PREDICATE HELD (B-16), WHICH IS
                                     WHY SELF-ISSUE IS SAFE AND WHY NO COUNTERSIGNATURE IS REQUIRED:
                                     the authorization is arithmetic and arithmetic does not care who
                                     requested it. THIS DOCUMENT DECLARES AN INSTANCE AND HAS NO
                                     STANDING TO DESCRIBE THE MECHANISM - B-22 makes genericity a
                                     TESTED property, gates.py's source may contain none of PREREG-002,
                                     rho_plan, 0.034, stage_2 or crypto-funding, and SPEC-003's own
                                     test_tbe_15 reproduces section 10.5.2's four rungs WITHOUT KNOWING
                                     THIS DOCUMENT EXISTS. Every property of the contingent form runs
                                     AGAINST this sponsor: B-19 unevaluable-implies-zero-and-FAIL
                                     rather than INSUFFICIENT-DATA; B-20's cap is AGGREGATE, so ten
                                     events declaring 32 each admit 32 once; B-23 FAILS the criterion
                                     on a malformed un-withdrawn event EVEN WHERE THE FAMILY IS
                                     COMFORTABLY INSIDE ITS SEALED BUDGET; B-24 makes the repair a
                                     WITHDRAWAL, NOT AN EDIT; B-26 refuses a reused authorization_ref.
                                     I-104 CONFORMED IN THE SAME EDIT: 'read from the cited table and
                                     NEVER INTERPOLATED' is STRUCK - it described a lookup with no
                                     defined value at rho_hat = 0.07. The nine rows at
                                     VALIDATION-SPEC-002 section 6.2 are a RENDERING of
                                     stats.max_admissible_trials, which is continuous, and RULING 003-A
                                     rules THE FUNCTION GOVERNS [cited - VALIDATION-SPEC-003 section
                                     7.3]. The sponsor's intent is preserved exactly and the family
                                     receives the allowance its own rho_hat earns rather than the next
                                     rung down. AND ONE SENTENCE IS NOW HONEST THAT WAS NOT: 'no Stage
                                     2 trial is spent on an unmeasured or a stale rho_hat' HAS NO
                                     SPEND-TIME CONTROL. log_trial reads no budget - its only
                                     precondition is that the family is registered [measured -
                                     registry.py] - so the budget is enforced RETROSPECTIVELY at
                                     evaluate_gate1 by B-9's ordering walk. Nothing prevents the spend;
                                     the spend fails the gate afterwards; and trials cannot be
                                     unspent [cited - V-5]. Filed I-132. The sentence is a discipline
                                     on the seat that writes the loop and this document no longer
                                     implies otherwise.] The ceiling this family is graded against is
                                     N_max = min(109, max_admissible_trials(span, SR_realized, ppy,
                                     vif = VIF_gate(rho_hat))), rho_hat being this family's NET-return
                                     autocorrelation measured by the harness from logged trials at every
                                     evaluate_gate1 call [cited - the Principal's I-057 ruling,
                                     VALIDATION-SPEC-002 0.2, 7.1; monotone-conservative, hence not the
                                     I-029(d) operation, and demonstrated empirically at 145 + 900 draws
                                     with zero violations, DATA-IMPL-006 2]. THE BINDING THRESHOLD IS
                                     rho_hat <= 0.034, NOT 0.1 [cited - VALIDATION-SPEC-002 7.2; I-064];
                                     0.1 was the Principal's stated figure, Validation derived 0.034 under
                                     the section 8 asymmetry without requesting an act, and 0.034 governs.
                                     109 is an UPPER BOUND computed at VIF = 1 that can only fall, NOT A
                                     BUDGET (I-063). The section 7.4 verdict bands are pre-committed at
                                     section 10.8: rho_hat <= 0.034 PASS; 0.034-0.15 FAIL-on-length, PARK,
                                     <= 11 months of history repairs it at 0.1; 0.15-0.30 PARK nominal,
                                     kill in practice; > 0.30 KILL; |rho_hat| >= 0.97 or n_logged = 0
                                     INSUFFICIENT-DATA, NEVER PASS. The Sharpe escape is closed by
                                     construction: raising realized Sharpe by searching raises N, which
                                     raises MinBTL, which raises the Sharpe required, so it works only on
                                     data not yet seen, which is the calendar-span remedy wearing a hat.
                                     TWO FURTHER MANDATORY DISCLOSURE LINES ON EVERY ARTIFACT: 'admissible
                                     N ceiling: <= 109 - computed assuming serial independence, an
                                     assumption this firm's data violates; an UPPER BOUND re-evaluated at
                                     Gate 1 on measured net-return autocorrelation, able only to fall; NOT
                                     A BUDGET'; and 'declared planning rho_plan = 0.10 [budgeting
                                     assumption, grades nothing]; measured rho_hat = <value, unclipped and
                                     signed>; VIF_gate = <value>; n_series_used = <count>; N_max at that
                                     VIF = <value>; authorized budget stage = <1 or 2>'.
                                     TIERED SUCCESS CRITERIA. (1) F-002 survival: no leg fires, and leg (0) firing is
                                     INSUFFICIENT-DATA rather than survival. (2) KC-002 survival at
                                     C + 187 days: no clause fires - and per KC-002's own text, SURVIVING
                                     IT CONFIRMS NOTHING. (3) Gate 1: every criterion of Charter
                                     4.4 unmodified, computed by castellan.evaluate_gate1, with
                                     backtest_years passed EXPLICITLY as true calendar span AND oos_index
                                     supplied (G1-G5: without oos_index the length criterion is
                                     INSUFFICIENT-DATA, never PASS). No threshold relaxation is sought.
                                     PLUS two criteria Charter 4.4 does not contain, which this seat
                                     imposes on itself: (a) ALPHA TO R_bench, not raw Sharpe, is the
                                     reported headline; (b) a SKEW AND EXPECTED-SHORTFALL line on every
                                     artifact, because Charter 4.4's battery - Sharpe, t-stat, DSR,
                                     subperiod positivity, P&L concentration - rewards a short-tail carry
                                     profile at every single criterion and contains no criterion that can
                                     SEE one. Required in every artifact regardless of verdict: per-
                                     regime-cell decomposition (all four cells); raw AND effective
                                     observation counts side by side; gross and net with the breakeven
                                     cost; hit rate PAIRED with slugging ratio (Charter 5.4 - neither
                                     means anything alone); the plateau centroid AND the argmax reported
                                     together, with only the centroid advancing, the distance between them
                                     being itself the overfitting diagnostic; [R3, 2026-08-04: the item
                                     'SOL on its own span with its own N' is STRUCK - SOL is not in the
                                     universe]; [R19(b), 2026-08-10, PRE-SEAL - STRUCK. The line below
                                     would be FALSE IN A SEALED FIELD the moment n_inherited = 7 is
                                     registered, and it is the sharpest available illustration of why
                                     R19(b) could not wait: 'declared N = 86; registry-enforced N =
                                     <count>; the 7-trial conditioning floor is declared and unenforced
                                     (I-027)'. REPLACED BY:] the disclosure line 'registry N =
                                     n_inherited 7 (the K1-K7 conditioning floor, SEALED, with four
                                     harness consumers) + logged <count>; declared ceiling 54 at Stage 1,
                                     86 at full Stage 2; authorized budget stage <1 or 2>'; and the
                                     disclosure line 'F-002 false-survival rate under
                                     the no-information null: 1.3e-4 [derived, with the leg-(ii) term
                                     ASSUMED / MEASURED per C11]' - because I-029's finding is that an
                                     unstated alpha is how a formality gets reported as a falsifier;
                                     and [R10, 2026-08-05] the disclosure line 'Gate 1 t-statistic:
                                     computed under the I-050-corrected estimator; the uncorrected
                                     SR x sqrt(T) figure is reported alongside it and the two must be
                                     shown together' - because this family's net return is funding accrual
                                     plus a basis increment and is AUTOCORRELATED BY CONSTRUCTION, the
                                     firm's one measured instance of the failing assumption being rho =
                                     0.83 on the funding series itself, implying ~3.3x inflation in the
                                     PERMISSIVE direction [cited - I-050, Principal-approved; RULING-004
                                     sections 14, 14.1].
                                     WHAT I-050 CHANGES FOR THIS FAMILY, RECORDED PRE-SEAL SO IT IS NOT A
                                     LATER SURPRISE: T_STAT_HURDLE = 3.0 DOES NOT MOVE - this is an
                                     estimator repair, not a threshold change, and requires no Charter
                                     amendment. F-002 LEG (i) IS UNAFFECTED: it was pre-committed as a
                                     NEWEY-WEST t at 21-bar truncation, one document before the correction
                                     was ruled, expressly because 'a carry residual is autocorrelated by
                                     construction and an OLS t on it is inflated in a known direction' - so
                                     section 5.3's alpha = 0.0013 and the joint false-survival rate of
                                     1.3e-4 STAND UNEDITED. F-002 legs (0), (ii) and (iii) contain no t and
                                     are unaffected. KC-002 CLAUSES (a), (b) AND (c) CONTAIN NO t AND ARE
                                     UNAFFECTED - stated explicitly so no seat re-opens the kill condition
                                     on the strength of an estimator change. DSR, PBO, WFE, subperiod
                                     positivity, P&L concentration, capacity and correlation are unaffected.
                                     THE ONE CRITERION THAT NARROWS IS GATE 1's t >= 3.0 ON NET RETURNS,
                                     and it narrows materially: section 5.4 already established that the
                                     R4(b) 50% haircut requires roughly 2x the pre-haircut figure, and
                                     composing that with the correction at the firm's one measured rho puts
                                     the required UNCORRECTED, PRE-HAIRCUT t at ORDER 20 [inferred -
                                     arithmetic on two cited multipliers, stated as an order of magnitude
                                     and NOT as a forecast; THIS FAMILY'S OWN rho IS UNMEASURED and may be
                                     materially lower, in which case the factor is materially smaller -
                                     but 'probably small' is [assumed] doing the work of [measured], which
                                     is Validation's own formulation and this seat adopts it AGAINST its
                                     own family]. CONSEQUENCE FOR THE PRE-REGISTERED EXPECTATION, revised
                                     against the family: section 11.6 recorded the 50% haircut as 'the
                                     largest single hurdle this family faces' and IT IS NO LONGER THE
                                     LARGEST - the composition of the haircut with the corrected estimator
                                     is, and unlike the haircut it is not a policy accepted for
                                     argumentative credit but arithmetic on a payoff shape this family
                                     chose. CONDITIONAL ON F-002 SURVIVING IN FULL, THE EXPECTED GATE 1
                                     OUTCOME IS PARK-WITH-TRIGGER, NOT PROCEED. This does NOT change the
                                     section 19 verdict: that case rests on a VERDICT being reachable, and
                                     F-002 and KC-002 both deliver one without touching a t.
                                     TWO HARNESS LEAKAGE DEFECTS ARE CARRIED RATHER THAN
                                     ASSUMED AWAY, because one of them is sized against THIS family's own
                                     parameter: walk_forward_windows applies NO purge and NO embargo at
                                     all, and purged_kfold_splits embargoes ceil(0.01*T) = 24 BARS on a
                                     2,398-bar sample - SHORTER THAN THIS FAMILY'S 30-DAY K1 LOOKBACK - so
                                     a training bar 25-30 bars after a test fold computes z(t) from INSIDE
                                     that fold [cited - RULING-004 section 1(5), ML-18, section 6.1;
                                     I-051, MEDIUM, owner head-of-data-infra]. EMBARGO_FRACTION = 0.01 is a
                                     Charter 4.2 constant and is not this seat's to raise; ML-18 rules it a
                                     FLOOR RATHER THAN A TARGET. The purged-CV and walk-forward results of
                                     this family therefore carry a leakage channel proportional to the
                                     excess of its 30-day lookback over the 24-bar embargo, IN THE
                                     PERMISSIVE DIRECTION, until I-051 is repaired. Named at Gate 0 so a
                                     WFE number is not read as clean.
                                     
                                     NINE OF THE SIXTEEN BINDING FIELDS ARE SEALED AND READ BY NOTHING
                                     [measured - zero non-registry.py consumers for universe, horizon,
                                     success_criteria, model_prior_provenance,
                                     published_signal_haircut_applied, forward_window_start,
                                     forward_window_min_length, forward_kill_condition; statement,
                                     mechanism and falsifier are non-empty-checked and nothing more].
                                     THE THREE FIELDS A PRE-REGISTRATION PUTS ITS METHODOLOGY IN -
                                     universe, horizon, success_criteria - HAVE ZERO CONSUMERS IN THE
                                     ENTIRE HARNESS. Everything asserted in them is enforced by the
                                     seat that writes the loop and by nothing else: K3's 'exclude
                                     nothing'; 'NO WINSORIZATION, OUTLIER REMOVAL OR RETURN CLIPPING
                                     anywhere at any stage'; w_max = 1.0 and never long perp; the
                                     capacity screen at 20 x P_notional; the 5% ADV participation cap;
                                     periods_per_year = 365; the ML-2 non-fitted assertion; 'only
                                     plateau_centroid_params advances'; the fixed-centroid
                                     walk-forward clause; F-002's E2 'evaluated ONCE'; and every
                                     mandatory disclosure line in this field. THE SEAL GIVES
                                     TAMPER-EVIDENCE, NOT ENFORCEMENT, and this document has been
                                     written in places as though the two were the same. Filed I-133.
                                     TWO ENTRIES ARE SIZED SEPARATELY BECAUSE THEY ARE LOAD-BEARING
                                     HERE: (1) published_signal_haircut_applied = 0.50 IS APPLIED BY
                                     NO CODE PATH ANYWHERE [measured] - no haircut computation exists
                                     in gates.py, stats.py, engine.py or costs.py - yet section 5.4
                                     derives this family's entire Gate 1 burden, a pre-haircut
                                     t(alpha) of roughly 6.0, from it; I-019 named this and R21 sizes
                                     it against this family; filed I-134. (2) NO HARNESS PATH
                                     EVALUATES A KILL CONDITION ON ANY DATE, FOR ANY FAMILY, and for a
                                     FORWARD classification forward_kill_condition is not even
                                     presence-checked [measured] - so KC-002 clause 5, 'SILENCE IS A
                                     KILL', the clause written expressly to defeat non-execution, is
                                     ITSELF DEFEATABLE BY NOT RUNNING IT, and is enforced by the
                                     calendar and by seats; filed I-135. NEITHER IS A REPAIR REQUEST.
                                     Most of what is listed above could not sensibly be mechanised -
                                     no harness will ever check that no winsorization was applied -
                                     and the finding is not that these should be enforced but that
                                     THIS DOCUMENT MUST STOP DESCRIBING THEM AS THOUGH THEY WERE. The
                                     two that COULD be mechanised are the 50% haircut and the
                                     conditioning floor; the second is mechanised at R19 and the first
                                     is filed and is not this seat's.
                                     EVERY LIMIT THIS
                                     DOCUMENT CLAIMS NOW CARRIES ITS CLASS AT SECTION 10.11: (a)
                                     HARNESS-ENFORCED, named field where one exists and named code
                                     path always; (b) PROCEDURE-ENFORCED, named executor, named
                                     cadence, named artifact; (c) DECLARED COMMITMENT, binding as a
                                     matter of record and enforced by audit and adversarial review
                                     only. COUNTS: 20 (a), 7 (b), 34 (c), SIXTY-ONE LIMITS CLASSIFIED.
                                     A CLASS-(c) LABEL IS A FULL AND HONOURABLE ANSWER AND IS NOT A
                                     DEMOTION; NOTHING WAS MADE ENFORCEABLE THAT WAS NOT.
                                     CORRECTION 1 [R25]: the paragraph above and section 10.10 said
                                     NINE binding fields are read by nothing. THERE ARE EIGHT. The
                                     nine was DIR-RESTATE-001 section 9.2's count of category-(c)
                                     LIMITS transplanted into a column counting FIELDS - two
                                     denominators, one number. The corrected partition of the sixteen
                                     is 5 class-(a) and 11 class-(c), of which statement, mechanism
                                     and falsifier carry an (a)-class check on EXISTENCE ONLY:
                                     registry.py raises on the empty string and reads not one
                                     character further, so F-002's four legs, its alpha of 0.0013, its
                                     1,800-bar floor and its 1.3e-4 joint false-survival rate sit in a
                                     field guaranteed only to be non-empty. Filed I-141.
                                     CORRECTION 2 [R28]: the 50% haircut is class (c) AT THE POINT OF
                                     RELIANCE AND NOT ONLY AT THE POINT OF DECLARATION. The bar
                                     evaluate_gate1 computes is t_gate >= 3.0 on UN-HAIRCUT net
                                     returns; the bar Charter 4.6 sets is the equivalent of 6.0. THE
                                     GAP IS EXACTLY 2x, IT SITS AT THE LARGEST HURDLE THIS FAMILY
                                     ACKNOWLEDGES, AND IT RUNS PERMISSIVE. Section 19.3's order-20
                                     composite is built from two multipliers that are NOT the same
                                     kind of object: the 3.3x I-050 correction is class (a) -
                                     t_gate = min(t_NW, t_raw) is the ONLY figure graded (E-8),
                                     stats.py:153 [measured] - and the 2x haircut is class (c) with no
                                     code path and an unruled point of application (C5). IF C5 IS
                                     NEVER RULED AND NO SEAT APPLIES 4.6 BY HAND, THIS FAMILY CAN BE
                                     REPORTED PROCEED AT HALF THE CHARTER'S BAR. Filed I-143; put to
                                     C2's intake at C13(i).
                                     TWO DISCLOSURE LINES IN THIS FIELD ARE CLASS (a) AND THE OTHER
                                     NINE ARE (c): the registry-N decomposition is rendered by
                                     gates.py:148-152 (H-12) and the holdout-classification line by
                                     gates.py:165 [measured]. The first became (a) AT R19, because
                                     gates.py:148 branches on 'if self.n_inherited:' and the branch was
                                     DEAD while the field was 0. R19 was argued as a tightening of the
                                     denominator; it also moved one disclosure line from (c) to (a),
                                     and nobody noticed until R-005.
                                     RECORDED AT PRE-REGISTRATION, all [measured] from castellan.stats:
                                     ~~n_inherited = 0 (no prior search exists)~~ ; 
                                     N_conditioning = 7 (was 6; K7 adds one); trial
                                     budget 79 (was 80; the 'SOL on its own span' diagnostic is struck
                                     with the asset); CEILING N = 86 IN BOTH ACCOUNTINGS - THE
                                     MULTIPLE-TESTING COUNT AT THE CEILING DOES NOT MOVE - so
                                     MinBTL(86, SR 1.0) = 6.14 years against
                                     6.571 available, clearing with 0.43 years of margin, STANDS UNEDITED
                                     AND THE 2026-08-04 REVISION PRODUCED NO NEW NUMBER, which is what A2
                                     requires of a revision made against a 0-trial registry. THE
                                     CONVENIENCE IN THAT ARITHMETIC IS DISCLOSED RATHER THAN LEFT TO BE
                                     NOTICED: reducing the budget by exactly 1 rather than 0 or 2 was
                                     chosen PARTLY because it preserves an already-measured MinBTL and
                                     avoids computing a new one [stated as a judgment, not a derivation],
                                     and partly because the struck line was one of five items sharing a
                                     <=8 cap so -1 is proportionate and -2 is not; both reasons are true
                                     and the first is the more convenient, which is why it is written
                                     down. If Validation prefers the budget held at 80, ceiling N becomes
                                     87 and MinBTL(87, SR 1.0) must be computed before sealing; it is
                                     BOUNDED BY ALREADY-MEASURED FIGURES in [6.14, 6.574] years, MinBTL
                                     being monotone increasing in N, so the Gate 1 length criterion clears
                                     either way and the margin lies between 0.00 and 0.43 years. 
                                     ABSOLUTE ADMISSIBLE CEILING N = 109 - the true maximum satisfying
                                     MinBTL(N, 1.0) <= 6.571 years [cited - VALIDATION-RULING-004 section
                                     2.2 by bisection, and section 12: 'The true maximum is 109 and I am
                                     recording the correction']. MinBTL(109) IS NOT RECOMPUTED HERE; the
                                     ceiling is cited, not re-derived, against a 0-trial registry. BEYOND
                                     109 THE FAMILY IS ARITHMETICALLY DEAD AT THE GATE 1 SHARPE FLOOR AND
                                     NO RESULT CAN REVIVE IT. WHAT THIS DOES NOT MOVE, stated because the
                                     opposite would be assumed: the DECLARED ceiling N = 86 (budget 79 +
                                     conditioning 7), MinBTL(86, SR 1.0) = 6.14 years, and the 0.43-year
                                     margin against 6.571 available are ALL UNCHANGED, because 86 < 109.
                                     WHAT IT DOES MOVE: the unused headroom between the declared ceiling
                                     and the absolute one falls from 24 trials to 23 (109 - 86 = 23,
                                     arithmetic on two integers, no market data touched). The margin the
                                     length criterion turns on is untouched; the margin for being wrong
                                     about the budget is one trial smaller. The
                                     ceiling relaxes on a higher realized Sharpe (MinBTL(110,1.5)=2.92 -
                                     [R8] measured at the superseded 110 and retained unrecomputed because
                                     it is quoted only qualitatively and MinBTL is monotone, so the value
                                     at 109 is no larger; the admissible N at 6.571 years is 109 at SR 1.0
                                     and 9,384 at SR 1.5 [cited - RULING-004 section 2.2], and THIS FAMILY
                                     FIXES ITS COLUMN AT SR 1.0 AND DOES NOT MOVE)
                                     but THE BUDGET MAY NOT EXPAND ON THAT BASIS - expanding a trial
                                     budget because early results look good is the overfitting operation
                                     wearing a schedule's clothing.
                                     COST STACK, and this is a Gate 0 finding not a footnote: the shipped
                                     CRYPTO_PERP_TAKER preset is NOT FIT FOR PURPOSE for this family.
                                     CostModel.carry_per_bar applies funding to GROSS notional and always
                                     as a COST (net = gross - cost). On this family's delta-neutral pair
                                     gross is 2.0, so carry_per_bar(1.0,1.0) = 0.0006/day = -21.9%/yr
                                     charged [measured] where the economics deliver +10.95%/yr received -
                                     THE SIGN INVERTED AND THE BASE DOUBLED, a 32.85 point/yr error on an
                                     edge of 10.95 points/yr. Further: funding_bps_annual is a SCALAR and
                                     carry_per_bar takes no time-varying input, so the 7,203 realized
                                     funding prints per asset in pit.db CANNOT ENTER THE P&L THROUGH THE
                                     SANCTIONED COST PATH AT ALL, and this family's entire signal is that
                                     series' variation; run_backtest accepts ONE CostModel for a
                                     TWO-LEGGED strategy and there is no CRYPTO_SPOT_TAKER preset;
                                     CostModel has NO FIELD for liquidation or venue-insolvency risk (the
                                     same gap as I-023(b)); and scaled(2.0) doubles funding_bps_annual to
                                     2190, so Charter 4.4's 2x cost-robustness criterion stress-tests the
                                     SIGN ERROR rather than the costs.
                                     The sentence
                                     that stood here - "CONDITION PRECEDENT C1: Validation specifies
                                     the repair - a signed carry term, or a synthetic perp total-
                                     return leg with funding_bps_annual = 0.0 - and rules whether the
                                     latter breaches the Seat 9 standing rule that researchers may
                                     not hand-roll costs. NO NET NUMBER FROM THIS FAMILY, IN ANY
                                     DOCUMENT OR IN THE PAPER BOOK, IS ADMISSIBLE UNTIL C1 LANDS" -
                                     IS STRUCK. C1 IS DISCHARGED; I-034 IS CLOSED (Principal,
                                     2026-08-11; satisfied 2026-07-29, commit 875874f). THE STATE OF
                                     THE COST STACK TODAY [measured, costs.py / carry.py / engine.py]:
                                     CRYPTO_PERP_TAKER carries NO funding term - the field was
                                     DELETED, not zeroed (Ruling 003 A1) - and funding is accrued in
                                     the ENGINE as a signed cash flow -(positions x funding_panel)
                                     from the realized pit_funding_panel series; CRYPTO_SPOT_TAKER
                                     exists (commission 10.0 bp, half-spread 2.5 bp, D-013 section 1,
                                     Principal-authorized); run_backtest accepts a dict[str,
                                     CostModel] mapping asset -> model and RAISES rather than
                                     defaulting on an omitted traded column (Ruling 003 section 3.4);
                                     and scaled(m) leaves carry BIT-IDENTICAL (T-16), so the Charter
                                     4.4 2x cost-robustness criterion now stresses the costs and only
                                     the costs, with carry.py supplying the separate sanctioned carry
                                     stress. All nineteen Validation-authored T-cases pass
                                     (DATA-IMPL-004 sections 5-6, landed 2026-07-29) [cited].
                                     NET NUMBERS FROM THIS FAMILY ARE ADMISSIBLE. THE ONE HEAD NOT
                                     REPAIRED IS DEFECT (d) - CostModel has no field that can charge
                                     liquidation or venue-insolvency risk, the largest risk in this
                                     mandate - which is CLASS (c), C-25 in the section 10.11.4
                                     register, disclosed on the face of every artifact, and NOT a
                                     condition precedent because there is nothing to wait for.
                                     HOUSE RULE 5, AND THE COST IS NOT ONE TRIAL :
                                     carry.carry_breakeven_bps_annual is the instrument and it takes
                                     a CALLABLE, evaluating it once at bracket[0], once at
                                     bracket[1], and once per bisection step - 42 evaluations at the
                                     shipped iters=40, each a run_backtest call and therefore a
                                     LOGGED TRIAL under the harness's own sanctioned usage (T-18)
                                     [measured: carry.py:107,113,116-122; engine.py:248]. ON THE KILL
                                     PATH IT COSTS ZERO - t_lo < hurdle returns at :111-112 before
                                     evaluating anything else, and the breakeven of a family below
                                     the hurdle IS 0.0 bps/yr by construction. ON THE SURVIVE PATH
                                     THIS FAMILY AUTHORIZES NINE, at iters=8, bracket (0, 2000)
                                     UNCHANGED, resolution 7.8 bps/yr, at section 15 step 3b. THE
                                     BRACKET IS NOT NARROWED TO SAVE TRIALS: the function returns its
                                     bracket ENDPOINT when the root lies outside it (:111-115) and
                                     I-037 names returning a search's ceiling as fabricated
                                     robustness. THE SHIFTED SERIES IS NOT RECONSTRUCTED OUTSIDE THE
                                     ENGINE: that costs zero trials and breaches A2. Filed I-151.
                                     STRUCTURALLY UNMEASURABLE ON THIS DATA, declared at Gate 0 so a
                                     good-looking result is read correctly: the strategy's risk
                                     materializes INTRADAY - liquidation cascades, basis dislocations,
                                     margin calls - and pit.db holds DAILY bars. A daily backtest marks a
                                     position that would have been liquidated as still held and
                                     recovering. The measurable part of this strategy is the part that
                                     flatters it. F-002 leg (ii), KC-002 clause (c) and mandatory skew/ES
                                     reporting are the three responses; none eliminates it. Also
                                     unmeasurable and disclosed rather than corrected: VENUE SURVIVORSHIP
                                     - the backtest runs on the branch where the venue did not fail, and
                                     FTX-listed carry books did not survive to be backtested."

trial_budget                      = 47        # [R15, 2026-08-06] AUTHORIZED BUDGET. Was 79 (R6), was 80.
                                              # [R20, 2026-08-10 - I-105's DISCHARGE. THIS FIELD IS THE
                                              # ONLY PLACE THE TWO-STAGE BUDGET EXISTS. gates.py:562 reads
                                              # `sealed = fam.trial_budget` and hands it to B-7's
                                              # zero-budget branch, B-9's per-trial ordering walk, and
                                              # declared_ceiling_base [measured]. SEALED AT THE FLAT 79 -
                                              # which is what every version of this document through R-003
                                              # would have sealed - the harness enforces 79, NO CONTINGENT
                                              # PREDICATE IS EVER EVALUATED, and section 10.5.2 describes a
                                              # gate that does not exist, permanently, under P7. STAGE 2
                                              # IS NOT IN THIS FIELD AND MUST NOT BE ADDED TO IT: it is a
                                              # trial_budget_extension event of mode CONTINGENT, written
                                              # after the seal - see the R20 note in success_criteria and
                                              # section 4 of research/REGISTRATION-PAYLOAD-PREREG-002.md.
                                              # Sealing 79 in order to "cover" Stage 2 IS the defect.]
                                              # CEILING N = 47 + 7 = 54, against N_max(rho_plan = 0.10) = 55
                                              # [cited - VALIDATION-SPEC-002 section 6.2]. One trial of margin.
                                              #
                                              # THE CEILING THIS FAMILY IS GRADED AGAINST IS A FUNCTION, NOT A
                                              # CONSTANT (section 10.4.1, the Principal's I-057 ruling):
                                              #   N_max = min(109, max_admissible_trials(span, SR_realized,
                                              #                     ppy, vif = VIF_gate(rho_hat)))
                                              # with rho_hat the family's NET-return autocorrelation measured
                                              # by the harness from logged trials at every evaluate_gate1 call.
                                              # 109 is max_admissible_trials(6.571, 1.0, vif=1.0) - an UPPER
                                              # BOUND that can only fall, not a budget (I-063).
                                              # [SUPERSEDED - S3-D-019, 2026-08-12: available span is now
                                              # 6.612 (6.609 settled-only), not 6.571; 109 itself not
                                              # recomputed here - see section 11.1 and section 10.4.]
                                              #
                                              # BINDING THRESHOLD FOR THE R-002 CEILING OF N = 86 IS
                                              # rho_hat <= 0.034, NOT 0.1 [cited - VALIDATION-SPEC-002 7.2;
                                              # I-064]. At rho_hat = 0.1 the ceiling is 55 and 86 is 31 over.
                                              #
                                              # A FURTHER <= 32 TRIALS ARE DECLARED AND NOT AUTHORIZED
                                              # (section 10.5.2, Stage 2: N_forward <= 22, walk-forward
                                              # windows 11-20 <= 10). They are spendable ONLY while the
                                              # declared ceiling N remains at or below the N_max implied by
                                              # the MOST RECENTLY MEASURED rho_hat on this family's own logged
                                              # trials, read from the cited table and never interpolated.
                                              # Full Stage 2 (budget 79, ceiling 86) is reachable ONLY at
                                              # rho_hat <= 0.034. No Stage 2 trial is spent on an unmeasured
                                              # or a stale rho_hat.
                                              #
                                              # DECLARED PLANNING RHO (V-7, non-binding on the Gate, made
                                              # binding on this budget by the sponsor's own election):
                                              # rho_plan = 0.10. Justified at section 10.5.1. It is a
                                              # BUDGETING ASSUMPTION AND GRADES NOTHING. rho_hat has never
                                              # been measured for this family and could plausibly land
                                              # anywhere in [0.0, 0.5] [cited - VALIDATION-SPEC-002 7.5];
                                              # declaring 0.10 is not a claim that 0.4 is unlikely.

n_inherited                       = 7        # [R19, 2026-08-10] NEW FIELD IN THIS BLOCK. It was omitted
                                             # entirely through R-003 on this section's own preamble
                                             # statement that "n_inherited is absent from the signature -
                                             # I-027". THAT STATEMENT IS FALSE [measured - registry.py:
                                             # the column is in SCHEMA, _migrate ALTERs it onto
                                             # pre-existing DBs and names book/registry.db in its
                                             # docstring, the signature carries it, and it is the
                                             # SIXTEENTH ENTRY OF _BINDING_FIELDS]. Section 10.3 carries
                                             # the strike.
                                             #
                                             # THE VALUE IS N_conditioning: the seven menu-declared,
                                             # pre-measurement conditioning choices K1 through K7, each
                                             # contributing 1 under section 7.2's pre-commitment rule.
                                             # Declared, phantom, NO RETURN SERIES - which is the field's
                                             # documented purpose verbatim.
                                             #
                                             # FOUR CONSUMERS, none of them cosmetic [measured - gates.py]:
                                             #   family_stats.n_trials = n_inherited + n_logged
                                             #   DSR's N                 (gates.py:779, :788)
                                             #   MinBTL's N              (gates.py:856)
                                             #   declared_ceiling_base = n_inherited + sealed  (:565)
                                             #
                                             # WHY 7 AND NOT 0: SPEC-003 B-18 admits
                                             # clamp(N_max - declared_ceiling_base, 0, increment), and
                                             # SPEC-003's own test_tbe_15 fixes base = 54 = 7 + 47 and
                                             # reproduces section 10.5.2's four unlock rungs exactly. At
                                             # n_inherited = 0 the base is 47 and the same mechanism
                                             # admits 30 where this document declares 23, and 8 where it
                                             # declares 1 - PERMISSIVE at the two rungs that bind, in the
                                             # exact direction the staged budget exists to close. I-130.
                                             #
                                             # NOT THE GATES.md 4.7.1 DEFECT: 4.7.1 forbids re-declaring
                                             # a quantity THE REGISTRY ALREADY COMPUTES. The registry
                                             # cannot compute N_conditioning - it holds no knowledge of
                                             # menus, choices or the pre-commitment discount - and with
                                             # predecessor_family = None there is no chain to sum and
                                             # InheritedCountDoubleCountError's guard is not entered.
                                             #
                                             # WHAT IT COSTS, TAKEN DELIBERATELY: registry-enforced N is
                                             # 54 at a full Stage 1 spend and 86 at full Stage 2, and it
                                             # rises INTO DSR and INTO MinBTL, not merely onto a report
                                             # face. Section 10.3's 0.13-year I-027 residual is PAID
                                             # rather than mitigated. MinBTL(86, SR 1.0) = 6.14 yr against
                                             # 6.571 available, margin 0.43 yr [cited - section 10.4,
                                             # already measured, NOT re-derived].
                                             # [SUPERSEDED - S3-D-019, 2026-08-12: available span is now
                                             # 6.612 (6.609 settled-only); margin now ~0.47 yr; MinBTL(86)
                                             # itself unrecomputed here - see section 11.1.]

predecessor_family                = None     # No prior family exists; book/registry.db holds zero
                                             # hypotheses [measured]. Consequences, both load-bearing:
                                             # family_stats has no chain to sum transitively, and
                                             # InheritedCountDoubleCountError's guard - conditioned on
                                             # `predecessor_family is not None` - is never entered, which
                                             # is why n_inherited = 7 registers cleanly.

holdout_classification            = "FORWARD"   # Validated at registration against {FORWARD, HISTORICAL}.
                                                # FORWARD does NOT trigger the R3 presence check on the
                                                # three forward_* fields - that branch is gated on
                                                # == "HISTORICAL" [measured]. This family supplies them
                                                # anyway (section 11.4) and R21 records that for a FORWARD
                                                # family NOTHING IN THE HARNESS READS THEM (I-135).

forward_window_start              = <C - the UTC calendar day of the open_hypothesis call>
                                             # [R23, 2026-08-10] THE LITERAL "2026-07-28" IS STRUCK AND IS
                                             # NOT BINDING. It was drafted against an intended same-day
                                             # seal that section 20.1 then recommended against, and has
                                             # been stale in this document since 2026-08-04.
                                             # C IS THE SEAL DATE (D-007) and the seal date is the moment
                                             # open_hypothesis is called, so the value is a computation
                                             # performed at the instant of the act:
                                             #   datetime.now(timezone.utc).date().isoformat()
                                             # This is MECHANICAL, NOT INTERPRETIVE - there is exactly one
                                             # correct value and one expression that produces it. It MUST
                                             # equal HoldoutVault.seal(cutoff=...), same session, same UTC
                                             # day (C8); P7 fails Gate 1 if hypothesis_sealed postdates C
                                             # at UTC day granularity. forward_kill_condition already
                                             # carries the same treatment for the observation date - "the
                                             # DRAFTED DATE IS NOT BINDING, the formula is" - and R23
                                             # extends it to the window's start.

forward_window_min_length         = 12.0         # UNITS: MONTHS (Charter 4.4 holdout floor).
                                                 # I-033(5): the schema stores this as a UNITLESS REAL and
                                                 # days, months and years are indistinguishable in it.
                                                 # [R21, 2026-08-10] NOTHING IN THE HARNESS READS THIS
                                                 # FIELD for a FORWARD family [measured - zero
                                                 # non-registry.py consumers]. No code compares it to an
                                                 # elapsed span and no code knows its unit. The ambiguity
                                                 # has cost nothing only because no consumer exists to be
                                                 # confused by it. I-135.

forward_kill_condition            = "KC-002. Observation date = C + 187 days, fixed at sealing and ABSOLUTE
                                     thereafter - it does not move with the sprint calendar, the ingest
                                     schedule, the cost-model repair, or the harness; once written it does
                                     not extend for any reason. (Drafted against an intended C =
                                     2026-07-28, giving 2027-01-31; section 20.1 recommends NOT sealing
                                     that day, so the executed value is whatever C + 187 days resolves to
                                     and the DRAFTED DATE IS NOT BINDING - the formula is.)
                                     187 days yields ~184 daily bars and ~552 funding prints -
                                     enough to measure expectancy and count conditioning events, and
                                     DELIBERATELY NOT ENOUGH to measure a Sharpe; KC-002 tests neither
                                     Sharpe nor significance. On that date Validation computes, from
                                     registry.db and pit.db ALONE, on the FROZEN pre-registration, over
                                     [C, C + 187 days] [R32, 2026-08-11: the literal "2027-01-31"
                                     that stood here is STRUCK and conformed to the formula this
                                     field's own opening declares governing]: (i) cumulative NET
                                     return of the sealed conditioned
                                     strategy after the full Charter 4.6 cost stack at 1x modelled costs
                                     using CRYPTO_PERP_TAKER AS REPAIRED PER C1; (ii) the count of days on
                                     which the sealed conditioning moved position notional by more than
                                     +/-25% from the benchmark's constant notional; (iii) the worst single
                                     day net return as a fraction of allocated sleeve notional. The family
                                     is KILLED - registry TERMINATED, no further trials, no Gate 1
                                     submission ever - if ANY of: (a) cumulative net return <= 0; OR
                                     (b) fewer than 30 days on which the conditioning moved notional by
                                     more than +/-25%; OR (c) any single day on which the net loss exceeds
                                     4.0% of allocated sleeve notional.
                                     Clause (b) kills on THE CONDITIONING NEVER HAVING CONDITIONED: if the
                                     state variable did not move the position then whatever the P&L was it
                                     was the benchmark's, and the family is the crypto carry factor by
                                     construction, which Charter 5.4 does not pay for. It must not be
                                     waived as a technicality; it is KC-001 clause (b)'s kill-on-
                                     insufficient-signal transposed to a continuous strategy.
                                     Clause (c) is the TAIL clause and exists because the backtest cannot
                                     see it: a delta-neutral pair at 1x notional should not lose 4% of
                                     allocation in a day, and if it does either the hedge failed or a
                                     basis dislocation ran through it - both being the intraday risk daily
                                     bars structurally cannot measure. 4.0% is Charter 5.2's Tier-2
                                     formal-notice threshold applied to a single day at the SLEEVE level
                                     rather than to a drawdown at the pod level, a deliberate borrowing
                                     made because a USD 250,000 sleeve cannot on its own reach a pod-level
                                     Tier 3 and the firm's standing ladder is too coarse to see this
                                     family fail. At sleeve scale the loss is USD 10,000, ~10 bp of firm
                                     NAV: trivial in money, decisive in information, and the kill is for
                                     the information.
                                     BINDING ANTI-REINTERPRETATION CLAUSES: (1) No re-parameterisation -
                                     all three quantities are computed on the SEALED specification, not a
                                     tuned variant, not the plateau centroid discovered later, not a
                                     subset, not the version we would have run. (2) No post-C exclusions -
                                     any regime filter, date exclusion, asset exclusion, venue change or
                                     universe restriction not present in the sealed pre-registration is
                                     inadmissible in this computation; this clause is the 
                                     K1-K7 declaration
                                     made enforceable, and any of K1-K7 revised in order to change this
                                     computation's answer is refused by P3 and, if pursued, [R9]
                                     TERMINATES THE LINE - the escalated successor registration being
                                     refused by the harness today (I-053), the sealed continuation being
                                     n_inherited = (menu size - 1) x chain_total if and when that repair
                                     lands, and a lower declaration to satisfy the guard being forbidden by
                                     name. (3) No restatement as
                                     continuation - a hypothesis restated after the observation date
                                     C + 187 days [R32, 2026-08-11: literal "2027-01-31" STRUCK] is a NEW family
                                     opened with predecessor_family = this family and n_inherited =
                                     ITS OWN NEW SEARCH ONLY, inheriting neither schedule nor allocation
                                     nor narrative. family_stats sums n_inherited and logged trials
                                     TRANSITIVELY across predecessor_chain [measured - registry.py], so
                                     predecessor_family alone carries this family's entire final count into
                                     the successor's denominator; re-declaring it in n_inherited
                                     double-counts and is refused by InheritedCountDoubleCountError. The
                                     clause's INTENT - that a restatement cannot escape this family's trial
                                     count - is delivered by predecessor_family alone and is delivered
                                     BETTER, because the harness enforces it instead of the sponsor
                                     asserting it.
                                     This field's opening declares the
                                     observation date to be C + 187 days and states that THE DRAFTED
                                     DATE IS NOT BINDING - THE FORMULA IS. Clause 5 as drafted read
                                     "if the computation is not performed ON 2027-01-31 for ANY
                                     reason ... the family is killed by default." READ AS SEALED,
                                     THOSE TWO SENTENCES TERMINATE THIS FAMILY WITH CERTAINTY: at any
                                     seal after 2026-07-28, C + 187 days falls LATER than 2027-01-31,
                                     so on 2027-01-31 the computation will not have been performed
                                     BECAUSE IT IS NOT DUE, and clause 5 fires - registry TERMINATED,
                                     no further trials, no Gate 1 submission ever. This is STRICTLY
                                     WORSE than section 14's C1 condition precedent on two heads:
                                     that one DOWNGRADED and this one KILLS, and that one fired on a
                                     premise that HAPPENED to be false while this one fires on a
                                     premise that CANNOT BE SATISFIED. A kill condition written to be
                                     undefeatable had become one that cannot be survived, and P7
                                     would have made it permanent. NOTHING EVALUATES IT (I-135: no
                                     harness path evaluates a kill condition on any date, for any
                                     family; for a FORWARD classification this field is not even
                                     presence-checked) - it is class (b), executor THE PRINCIPAL, and
                                     a Principal executing it correctly would read this text and find
                                     the family dead. THE LITERAL IS CONFORMED TO C + 187 DAYS in
                                     clause 5 below, in the two clauses above, and in section 14's
                                     prose. NO NEW RULE IS INTRODUCED AND NO THRESHOLD MOVES - the
                                     conformance is to the rule this field's own opening already
                                     governs by and which section 15 step 8 already computes. THE
                                     REPAIR RUNS IN THIS FAMILY'S FAVOUR AND IS RECORDED AT THIS
                                     VOLUME FOR THAT REASON: a sponsor deleting a clause that
                                     terminates its own family is the shape of act this firm exists
                                     to distrust, and it is NOT recorded as housekeeping. PUT TO C2
                                     AS C13(k) - VALIDATION MAY REFUSE THIS CONFORMANCE AND REQUIRE
                                     THE LITERAL 2027-01-31 SEALED AS DRAFTED, in which case the
                                     family accepts a window shortened by however long the seal took,
                                     clause (b)'s 30-day threshold becomes correspondingly harder
                                     against a window calibrated at 187 days, and this seat writes
                                     the KILL memo on the day without argument.
                                     [R38, PRE-SEAL: RATIFIED BY THE PRINCIPAL, BY HIS OWN ACT, WITH
                                     ZERO OUTCOME KNOWLEDGE. This seat REFUSED to ratify its own
                                     favourable repair and routed it instead - the third such refusal
                                     - and that routing is recorded as correct. The Principal
                                     conformed clause 5 to C + 187 days himself, pre-seal, on this
                                     field's own declaration that THE DRAFTED DATE IS NOT BINDING -
                                     THE FORMULA IS. His ruling, verbatim and binding: the committed
                                     quantity is the 187-day window; fixing it pre-seal with zero
                                     outcome knowledge is conforming a document to its own governing
                                     terms, not extending a test that is going badly. ABSOLUTE meant
                                     absolute against RESULTS-BASED movement; it still is. WHAT THIS
                                     RATIFICATION DOES NOT DO: it does not discharge C13(k). The
                                     INSTANCE inside C2 at row 3 remains Validation's, the
                                     alternative - the drafted literal 2027-01-31 and a shortened
                                     window - remains LIVE for Validation to take, and the seal does
                                     not proceed past it. A ratification by the Principal of the
                                     seat's routing is not a ruling by Validation on the instance,
                                     and this seat will not present it as one.]
                                     (4) Kill is automatic on the date, requires no meeting, no vote and no
                                     CIO concurrence, and IS NOT APPEALABLE TO THE CIO; only the Principal
                                     may reverse it, in writing, logged in DECISION_RECORD.md as an
                                     Appendix-B-#4 override with its reason on the face of the record and
                                     reported in the next Monthly Letter. (5) SILENCE IS A KILL - if the
                                     computation is not performed on THE OBSERVATION DATE C + 187 DAYS
                                     [R32, 2026-08-11: literal "2027-01-31" STRUCK - see the R32 note
                                     above; the literal made this clause fire with certainty] for ANY reason, INCLUDING
                                     that the perp price series was never ingested, that the cost model was
                                     never repaired, that Validation had no unit available, or that the
                                     harness was not ready, the family is killed by default. A kill
                                     condition that can be defeated by not running it is not a kill
                                     condition. This clause is copied deliberately from KC-001, and the
                                     seat that would benefit most from softening it is the seat that wrote
                                     it.
                                     The sentence
                                     that stood here - "CONDITION PRECEDENT, separately binding: the
                                     C1 cost-model repair is specified by Validation and implemented
                                     by 2026-08-11; if unresolved by that date the family is
                                     ADMITTED-AS-EXPLORATORY only and remains so until it is, because
                                     until then clause (a) would be computing a -21.9%/yr artifact" -
                                     IS STRUCK AND IS NOT PART OF THIS FIELD. C1 IS DISCHARGED:
                                     I-034 CLOSED by the Principal 2026-08-11, satisfied 2026-07-29
                                     (commit 875874f, "Ruling 003 implemented: carry accounting,
                                     139/139. Closes I-034"), discovery credit R-005. R-005 struck
                                     this sentence in section 14's PROSE at R26 and left it standing
                                     HERE, corrected only by a note some forty lines further down
                                     this same field. A FIELD IS HASHED AS ONE STRING: a reader of
                                     the sealed value meets the downgrade before the correction.
                                     That is I-105's doctrine run backwards - a control exists where
                                     the harness reads it, and a correction exists where the SEAL
                                     reads it, and nowhere else.
                                     The residual is retained and is NOT swept up with the closure:
                                     CostModel has no field that can charge liquidation or
                                     venue-insolvency risk (section 12.5 defect (d)), it is class (c)
                                     C-25 in the section 10.11.4 register, VALIDATION-RULING-003
                                     section 4 declines to invent a number for it, and it is NOT a
                                     condition precedent because there is nothing to wait for.
                                     WHAT KC-002 IS NOT, stated here rather than waiting to be told
                                     (Validation C-001 section 1.6 makes the identical statement about
                                     KC-001): KC-002 IS A KILL CONDITION, NOT A CONFIRMATORY TEST. Clauses
                                     (a), (b) and (c) are bare one-sided comparisons against thresholds;
                                     none has a null distribution, an alpha, or a power statement.
                                     SURVIVING KC-002 CONFIRMS NOTHING AT ANY N, and 'the family passed its
                                     forward test' may not appear in any artifact as a result. This family
                                     DOES NOT claim the C-001 N=1 confirmatory exemption; should it ever
                                     seek one it must satisfy E1-E5 in full and be entered in the
                                     firm-level register of outstanding confirmatory exemptions that I-032
                                     requires and that does not yet exist - at 20 families each holding one
                                     exemption the firm-level false-positive rate is ~2.7% [cited,
                                     Validation], which is why the register is a precondition and not a
                                     formality. Separately, per C-001 E3: the family's <= 22 forward-window
                                     trials are N_forward, they are LOGGED AS TRIALS, and NO REPORTED
                                     RESULT MAY BE SELECTED FROM AMONG THEM.
                                     NO HARNESS PATH EVALUATES A KILL
                                     CONDITION, ON ANY DATE, FOR ANY FAMILY [measured - zero
                                     non-registry.py consumers of forward_kill_condition]. For a
                                     FORWARD classification this field is not even PRESENCE-CHECKED:
                                     registry.py's R3 check is gated on holdout_classification ==
                                     'HISTORICAL' and this family is FORWARD, so the string is stored,
                                     hashed into prereg_sha256, shadow-copied into hypothesis_sealed,
                                     and READ BY NOTHING THEREAFTER. THE CONSEQUENCE, STATED WITHOUT
                                     SOFTENING: clause 5 - 'SILENCE IS A KILL... if the computation is
                                     not performed for ANY reason the family is killed by default... a
                                     kill condition that can be defeated by not running it is not a
                                     kill condition' - IS ITSELF DEFEATABLE BY NOT RUNNING IT. Every
                                     clause of KC-002 is enforced by the calendar, by Validation, and
                                     by the seats bound to it, and by no line of code. THE SEAL MAKES
                                     THE TEXT IMMUTABLE; IT DOES NOT MAKE IT OPERATIVE, and this
                                     document has in places been written as though those were the same
                                     thing. NOTHING IN KC-002 IS CHANGED, SOFTENED OR MADE CONDITIONAL
                                     BY THIS NOTE - the observation date, the three clauses, their
                                     thresholds and all five anti-reinterpretation clauses stand
                                     exactly as sealed; what changes is that the document now names who
                                     enforces them. Filed I-135. THIS IS A DISCLOSURE, NOT A REPAIR
                                     REQUEST: a harness that fires kill conditions on wall-clock dates
                                     is not a thing this firm has, and GATES.md 4.7.2's instruction is
                                     to NAME THE FIELD OR SAY THERE IS NONE - not to demand one be
                                     built.
                                     
                                     CLASS (b) - PROCEDURE-ENFORCED. EXECUTOR: THE PRINCIPAL. CADENCE:
                                     THE WEEKLY FRIDAY RITUAL, ALONGSIDE THE PULL-AND-MERGE. ARTIFACT:
                                     THE PASTED EVALUATION ATTACHED TO THE RECORD, PER TEMPLATES.md
                                     SECTION 7.9 - under which a step is CLOSED only when the
                                     Principal's pasted output is attached, and a step without
                                     attached output is 'written', NEVER 'executed'.
                                     IT REVERTS TO CLASS (a) WHEN VALIDATION'S HARNESS KILL-CONDITION
                                     EVALUATOR LANDS - SPECCED THIS SPRINT, NOT YET DISPATCHED. Until
                                     it does, clause 5 is enforced by a person on a calendar, and
                                     'DEFEATABLE BY NOT RUNNING IT' CANNOT DESCRIBE A
                                     SIGNATURE-REQUIRED CLAUSE. This seat wrote clause 5, defended it,
                                     and now labels it (b): the honest repair is to name WHO runs it,
                                     HOW OFTEN, and WHAT THE RUNNING PRODUCES - not to hope.
                                     The C1 cost-model
                                     repair is SPECIFIED (VALIDATION-RULING-003, whose header names
                                     'Blocks: PREREG-002 condition precedent C1') AND IMPLEMENTED
                                     (DATA-IMPL-004 sections 5-6, 'All nineteen T-cases are
                                     implemented and pass', landed 2026-07-29; verified in source
                                     [measured]: CRYPTO_PERP_TAKER carries NO funding term,
                                     CRYPTO_SPOT_TAKER exists under D-013 section 1, carry.py supplies
                                     the sanctioned stress path, and scaled(m) leaves carry
                                     bit-identical per T-16). SECTION 14's CONDITION PRECEDENT WOULD
                                     HAVE DOWNGRADED THIS FAMILY TO ADMITTED-AS-EXPLORATORY ON
                                     2026-08-11 - 'pre-declared ineligible for Gate 1' - ON A PREMISE
                                     FALSE ELEVEN DAYS BEFORE THE DEADLINE, AND P7 WOULD HAVE MADE IT
                                     PERMANENT. Filed I-140, HIGH. CLAUSE (i) IS UNAFFECTED IN EVERY
                                     WORD: it reads 'using CRYPTO_PERP_TAKER AS REPAIRED PER C1', and
                                     the preset IS as repaired. NO CLAUSE OF KC-002 MOVES. The one
                                     head of section 12 that is NOT repaired is defect (d) - CostModel
                                     has no field that can charge liquidation or venue-insolvency risk
                                     - which is class (c), is C-25 in the register, is disclosed on
                                     the face of every artifact, and is NOT a condition precedent
                                     because there is nothing to wait for."

model_prior_provenance            = "R4(a). Per I-009 the firm does not know its seats' training cutoffs
                                     and the authoritative reference does not publish them; every cutoff
                                     below is [assumed] unknown and that absence is itself the finding.
                                     THIS IS THE FIRM'S FIRST DIRECTOR-ORIGINATED HYPOTHESIS (I-025:
                                     today's origin ratio is 4 of 4 = 100% Principal-originated; D-009
                                     item 4 directs that the Sprint 2 agenda contain Director-originated
                                     hypotheses). Every binding design field below except the holdout
                                     regime and the conditioning rider originates with Seat 2, Opus,
                                     cutoff unknown: hypothesis statement and mechanism; the Charter-5.4
                                     argument that the unconditioned carry is factor beta; falsifier
                                     F-002 and each of its four pre-committed constants; conditioning
                                     declarations [R9, 2026-08-05] K1-K7 and their menus (K7 was declared
                                     at R5 and this provenance line was not extended with it); the
                                     pre-commitment rule that a
                                     menu-declared pre-measurement choice contributes 1 rather than the
                                     menu size, and its escalation rule; universe, sizing rule and
                                     parameter centres; the trial budget and the [R8, 2026-08-05] N <= 109
                                     ceiling (the ceiling's correction from 110 originates with Quant
                                     Validation, RULING-004 sections 2.2 and 12), derived
                                     from castellan.stats output; KC-002, adopting KC-001's shape
                                     (originated by the Devil's Advocate, REDTEAM-001 B.5, Opus) including
                                     the silence clause verbatim in force; the CRYPTO_PERP_TAKER audit,
                                     measured from source. The REDIRECT of Pod B compute from the
                                     forward-lag family to this mandate: originated by the Director of
                                     Research (PREREG-001 section 17.2 item 4, Opus), approved by the
                                     Principal (human). The CONDITIONING RIDER requiring that every regime
                                     choice be declared together with its menu: the Principal (human), and
                                     it is the single most load-bearing instruction in this document -
                                     without it the honest N contribution would be 27,000 and MinBTL would
                                     be 16.79 years against 6.571 [SUPERSEDED - S3-D-019, 2026-08-12: 6.612
                                     / 6.609 settled-only; see section 11.1; conclusion unchanged] available.
                                     Holdout regime: Validation
                                     Rulings 001 and 002 (Opus) and the Principal (D-006 Option D, D-007
                                     C = the seal date). NOT YET ORIGINATED BY ANYONE AND REQUIRED: a
                                     Devil's Advocate Red-Team Memo on this family (Charter 4.4; Charter
                                     6.4 defers a packet without one). KC-002 is the SPONSOR's kill
                                     condition, which is structurally weaker than one authored against the
                                     family, and that weakness is recorded here rather than left to be
                                     noticed.
                                     [R-004, 2026-08-10] ORIGINATED BY THE DIRECTOR OF RESEARCH (Seat
                                     2, Opus, cutoff unknown [assumed]): the GATES.md 4.7.2 audit of
                                     this document against the harness field by field (R21), the
                                     correction of n_inherited from 0 to 7 (R19), the registration of
                                     Stage 1 as the sealed trial_budget with Stage 2 as a CONTINGENT
                                     extension event (R20, discharging I-105), and the conformance of
                                     section 15's step arithmetic (R22). THE DOCTRINE APPLIED IS THE
                                     PRINCIPAL'S: GATES.md 4.7.2, ruled 2026-08-06 (S2-D-029) -
                                     'a control exists where the harness reads it, and nowhere else' -
                                     and the DISPOSITION between registering Stage 2 and striking it
                                     is the Principal's, with the choice between the two made by this
                                     seat and defended at section 10.5.2. THE MECHANISM STAGE 2 USES
                                     IS NOT THIS SEAT'S AND IS NOT THIS FAMILY'S: it is
                                     VALIDATION-SPEC-003's generic CONTINGENT form (Quant Validation,
                                     Opus), whose test_tbe_15 reproduces this document's own unlock
                                     table WITHOUT KNOWING THIS DOCUMENT EXISTS, and whose B-22 makes
                                     that independence a tested property. This document declares an
                                     instance of it and claims no authorship of it.
                                     [R-005, 2026-08-10] ORIGINATED BY THE DIRECTOR OF RESEARCH (Seat
                                     2, Opus, cutoff unknown [assumed]): the CLASS REGISTER at section
                                     10.11 (R24) - sixty-one limits, 20 (a) / 7 (b) / 34 (c); the
                                     correction of section 10.10's field-count arithmetic from nine
                                     zero-consumer fields to eight (R25, I-141); the finding that
                                     I-034/C1 is IMPLEMENTED and that this document described the
                                     pre-repair cost model at ~~six~~ [R39, PRE-SEAL: FOURTEEN. The
                                     cardinal "six" is I-150 and it had propagated into this SEALED
                                     field while the prose that describes the field carried the
                                     corrected fourteen - R29(b)'s lesson, a sixth time, in the same
                                     direction] fourteen sites including a condition
                                     precedent one day from firing (R26, I-140); the finding that
                                     I-022 is REPAIRED and that C10 and two further clauses rest on it
                                     being live (R27, I-142); and the placement of the haircut's class
                                     (c) at its points of reliance with the gap sized at 2x (R28,
                                     I-143). THE CLASS TAXONOMY IS NOT THIS SEAT'S: the three classes
                                     and their required fields are the PRINCIPAL'S, adopting this
                                     seat's own I-133 conclusion verbatim - 'most of these cannot be
                                     mechanized and should still be written down; what must stop is
                                     the document describing them as controls.' KC-002's three class-(b)
                                     fields - executor the Principal, cadence the weekly Friday ritual,
                                     artifact the pasted evaluation per TEMPLATES.md 7.9 - are the
                                     PRINCIPAL'S, supplied with the mandate and reproduced verbatim
                                     rather than paraphrased. TWO OF R-005's FOUR FINDINGS RUN IN THIS
                                     FAMILY'S FAVOUR (R26, R27) AND THIS SEAT RECORDS THAT IT WOULD
                                     BENEFIT FROM BOTH."

published_signal_haircut_applied  = 0.50     # [R21, 2026-08-10] NOTHING IN THE HARNESS APPLIES THIS
                                             # [measured - zero non-registry.py consumers; no haircut
                                             # computation exists in gates.py, stats.py, engine.py or
                                             # costs.py]. The presumption is accepted in full and no
                                             # exemption is sought (section 11.6); the 0.50 is a
                                             # DECLARATION, not an enforced deduction, and section 5.4
                                             # derives this family's entire Gate 1 burden - a pre-haircut
                                             # t(alpha) of roughly 6.0, described at section 11.6 as
                                             # "the largest single hurdle this family faces" - FROM A
                                             # NUMBER NO CODE PATH READS. I-019 named this; R21 sizes it
                                             # against this family by name. Filed I-134.
```

---

### 21.1 REVISION MARKERS RELOCATED FROM THE SEALED FIELDS — I-173 repair, dispatch S3-D-016

**Why this subsection exists.** `VALIDATION-SPEC-004`'s dated-clause extractor (E-2) reads the eight prose fields of §21 by literal form, not by meaning, and cannot distinguish a revision timestamp from a substantive date. Section 21's fenced block previously carried inline `[Rn, date, ...]` revision markers inside the strings that get hashed into `prereg_sha256`, so every marker date fired as a "dated site" — I-173. **Per dispatch S3-D-016, `head-of-data-infra` relocated 27 of the 35 marker sites flagged `stamp: true` in `research/work/site_roster.json` out of the hashed §21 block and into this subsection, verbatim, word for word, removing them from the field text they previously sat inside.** The remaining 8 flagged-true sites were **not** relocated — they are entangled with adjacent `stamp: false` (substantive) text in the same bracket or sentence, or sit inside a bracket this document itself never closes (§10.4's `[R13/R14/R15/R16/R17...` marker in `success_criteria` has no closing `]` anywhere in the field — a pre-existing document defect, not something this seat introduced or repaired). Every one of the 8, plus 2 additional dated sites discovered inside a marker not covered by the roster at all (`[R38, PRE-SEAL...]` in `forward_kill_condition`, added to the document after the roster was generated), is named in the Issue Log rather than edited. This subsection is **outside** the fence that `extract_dated_sites.py` reads for §21, and therefore outside `prereg_sha256`'s input — the audit trail below is not hashed and never will be under the current seal mechanism (P2).

**Nothing below is new. Every word is copied unedited from the field named, at the position named.** No word was added, paraphrased or summarized; only the hard line-wrapping (presentation, not content) is removed for readability outside the fixed-width fence.

**Field `mechanism`:**

> [R1, 2026-08-04, PRE-SEAL - WITHDRAWN AND REPLACED. The withdrawn sentence read: 'The ~11%/yr baseline is approximately the market-clearing price of three risks a carry supplier genuinely bears.' It is not supportable and this seat withdraws it.]

> [R2, 2026-08-04, PRE-SEAL - RESTATED. The prior text read 'funding is a DIRECT OBSERVABLE of long-side positioning crowding'.]

**Field `universe`:**

> [R3, 2026-08-04, PRE-SEAL - SOL IS DROPPED ENTIRELY. The prior text made SOL a SECONDARY member reported separately on its own 5.87-year span with its own N and its own verdict, never pooled.]

> [R3, 2026-08-04: selection MOVED WITHIN the already-declared menu, from (2) to (4). The menu did NOT grow.]

> [R4, 2026-08-04: THE CADENCE CONSTANT IS DELETED. The prior text read 'funding aggregated as the sum of the day's three prints'. That asserted a cadence constant which is MEASURED FALSE - up to 12 prints in one day, on 11 of 2,145 days [measured - VALIDATION-RULING-003 section A2] - and Validation has already specified its replacement.]

> [R5, 2026-08-04: NEW CHOICE, declared pre-measurement against a registry holding 0 families and 0 trials. The pre-R5 document made this choice SILENTLY, its implicit selection being option (5) - pool across the change - and I-045 IS THE FINDING THAT OPTION (5) IS WRONG. An implicit selection is exactly the defect the conditioning declaration exists to prevent, and it was present inside the section that prevents it.]

> [R5/R6, 2026-08-04: 6 -> 7]

> [R19, 2026-08-10, PRE-SEAL: THE 7 IS NOW REGISTERED, NOT MERELY DECLARED. It is sealed as n_inherited = 7, a binding field with four consumers - family_stats.n_trials, DSR's N, MinBTL's N, and declared_ceiling_base = n_inherited + sealed budget, which is the base of VALIDATION-SPEC-003 B-18's contingent-unlock arithmetic [measured - gates.py]. Section 10.5.2's own unlock table is reproduced ONLY at a base of 7 + 47 = 54, which is the base SPEC-003's own test_tbe_15 fixes; at n_inherited = 0 the base is 47 and the same mechanism admits 30 where this document declares 23 and 8 where it declares 1 - PERMISSIVE at the two rungs that bind. This is not the GATES.md 4.7.1 defect: the registry cannot compute N_conditioning, and 4.7.1 governs inheritance from a predecessor this family does not have (predecessor_family = None, so the chain summation and InheritedCountDoubleCountError's guard are both inapplicable). The cost is taken deliberately and runs against the family: registry-enforced N is 54 at full Stage 1 and 86 at full Stage 2, so section 10.3's 0.13-year I-027 residual is PAID rather than mitigated.]

> [R9, 2026-08-05, PRE-SEAL - STRUCK AND REPLACED ON THREE HEADS. The struck rule read: 'any revision to any of K1-K6 after any result on this family is seen is refused by P3 and requires a SUCCESSOR FAMILY opened with n_inherited >= (menu size of the revised choice) x this family's final n_trials, or the PRODUCT of the menu sizes if more than one is revised.' HEAD (i) SCOPE: it covered K1-K6 and NOT K7, which R5 declared and R6 discounted to 1 on the same reasoning - a choice discounted by a rule it is not subject to is discounted for nothing. HEAD (ii) QUANTITY: family_stats computes n_trials = SUM n_inherited(chain incl. self) + SUM logged(chain incl. self), summing TRANSITIVELY across predecessor_chain [measured - registry.py], so the predecessor's total is ALREADY inside the successor's denominator; declaring menu_size x chain_total on top yields (menu_size + 1) x chain_total. The correct declaration for a target denominator of menu_size x chain_total is (menu_size - 1) x chain_total. The error ran CONSERVATIVE, which is why it survived, and it is a defect regardless - filed I-055, and addressed to Validation as well because RULING-004 ML-17 copies the same formula citing this document as its source. HEAD (iii) EXECUTABILITY (I-053): open_ hypothesis raises InheritedCountDoubleCountError whenever a successor declares n_inherited >= chain_total [measured - registry.py], and BOTH the struck and the corrected forms exceed chain_total for every menu size >= 2 - K1-K7's sizes are 10, 3, 9, 5, 5, 4, 5, all >= 3 - so the rule could not be executed on any of its seven choices, ever. THE GUARD IS NOT WRONG; what is missing is the continuation, there being no argument, event or authorized route by which Validation, having adjudicated the escalation, can then permit the registration.]

> [R5, 2026-08-04]

**Field `success_criteria`:**

> [R11, 2026-08-05, PRE-SEAL - THE ML-2 ASSERTION, ADDED VERBATIM AND PLACED FIRST BECAUSE RULING-004 ML-2 MAKES ITS ABSENCE A GATE 0 REJECTION RATHER THAN A DEFERRAL, AND BECAUSE 'SILENCE IS NOT THAT ASSERTION'.]

> [R11, 2026-08-05]

> [R21, 2026-08-10, PRE-SEAL - THE GATES.md 4.7.2 AUDIT, RECORDED IN THE SEALED TEXT INCLUDING ITS UNFLATTERING HALF, BECAUSE A DOCUMENT THAT DESCRIBES CONTROLS IT DOES NOT HAVE IS I-046'S COSTUME ON THE RESEARCH SIDE AND P7 MAKES IT PERMANENT.]

> [R24/R25/R28, 2026-08-10, PRE-SEAL - THE CLASS REGISTER, AND THE TWO CORRECTIONS THE AUDIT ABOVE GOT WRONG.]

> [R19, 2026-08-10: n_inherited = 7 - REGISTERED, not declared. No prior EXTERNAL search exists; the 7 is N_conditioning, the K1-K7 floor, sealed in the field built for that quantity. See the N CONTRIBUTION note in `universe` and section 10.3.]

> [R5/R6, 2026-08-04]

> [R8, 2026-08-05, PRE-SEAL - THE ABSOLUTE CEILING IS CORRECTED FROM 110 TO 109. The prior text read: 'ABSOLUTE ADMISSIBLE CEILING N = 110, at which MinBTL = 6.574 = the entire available span and margin is zero.' That was a MISLABEL OF THIS DOCUMENT'S OWN MEASURED NUMBER, in the PERMISSIVE direction: MinBTL(110) = 6.574 EXCEEDS the 6.571 available, so 110 FAILS by 0.003 years and is not 'exactly at the span'.]

> [R3, 2026-08-04: the clause 'On the SOL-inclusive 5.87-year span the ceiling is 74' is MOOT - no SOL-inclusive span exists and the 74 ceiling never binds. Retained struck because it is part of the record of why K4 was originally selected as it was.]

> [R29(b), 2026-08-11, PRE-SEAL - THE WHOLE OF THE PRECEDING COST- STACK PARAGRAPH DESCRIBES A COST MODEL THAT NO LONGER EXISTS AND IS RETAINED ONLY AS THE RECORD OF THE DEFECT. IT IS NOT A STATEMENT OF HARNESS FACT AND MUST NOT BE READ AS ONE. R-005 CORRECTED THIS DIAGNOSIS IN SECTION 12'S PROSE AND DID NOT REACH THIS FIELD, WHICH IS THE ONE THAT GETS HASHED.]

> [R30, 2026-08-11]

**Field `forward_kill_condition`:**

> [R9, 2026-08-05]

> [R9, 2026-08-05: the prior text read 'opened with n_inherited >= the killed family's final n_trials plus its own', which was REDUNDANT AND UNEXECUTABLE from the same misreading of family_stats as head (ii) above]

> [R32, 2026-08-11, PRE-SEAL - THE SECOND C1, AND IT IS IN CLAUSE 5 BELOW. FILED I-153, HIGH.]

> [R29(b), 2026-08-11, PRE-SEAL - STRUCK IN THIS FIELD, WHICH IS WHERE IT MATTERED AND WHERE R-005 DID NOT REACH.]

> [R21, 2026-08-10, PRE-SEAL - WHAT THE HARNESS DOES WITH THIS FIELD, RECORDED ON KC-002'S OWN FACE BECAUSE THE ANSWER IS NOTHING, AND BECAUSE THE SEAT THAT WOULD PREFER NOT TO SAY SO IS THE SEAT THAT WROTE CLAUSE 5.]

> [R24/R26, 2026-08-10, PRE-SEAL - KC-002 IS CLASS (b), AND ITS THREE FIELDS ARE NAMED. THIS IS THE PART R21 LEFT UNDONE: 'ENFORCED BY THE CALENDAR AND BY SEATS' IS NOT AN ANSWER, IT IS THE ABSENCE OF ONE.]

> [R26, 2026-08-10, PRE-SEAL - THE CONDITION PRECEDENT IS SATISFIED AND THE DOWNGRADE MUST NOT FIRE.]

---

**Vault seal, same session, same UTC day:**

```
HoldoutVault(vault_dir="book/vaults/funding-carry-conditioning-002-binance",
             registry=registry, name="funding-carry-conditioning-002-binance",
             family="funding-carry-conditioning-002", store=pit_store).seal(
    source="binance",                       # a second vault for source="binanceusdm"
    dataset_id=<the ingested dataset identifier>,
    # [R3 · 2026-08-04] SOL removed from the universe; it is removed from the vault identity with it.
    instrument_identity="BTC/USDT, ETH/USDT (spot); "
                        "BTC/USDT:USDT, ETH/USDT:USDT (perp), "
                        "fields close/open/high/low/volume and funding_rate",
    query_semantics=<the exact query, per Ruling 001 section 3.4>,
    cutoff=<C = this UTC calendar day>,
    schema_fingerprint=<field names and dtypes>,
    passphrase=<the Principal's, never written to repo, Oracle, or any file>,
    holdout_end_rule="open-ended, forward from C",
    resolution_source="exchange settlement; funding prints final at settlement, never revised",
    sealed_by="pm-digital-markets")
```

---

## 22. WHAT WOULD CHANGE THIS SEAT'S MIND

| # | On what | What would change it |
|---:|---|---|
| 1 | **The verdict at §19** (fund it, ~4 Sonnet units) | Validation ruling that the §12.3 synthetic-total-return construction breaches the Seat 9 standing rule **and** that no signed carry term will be added to `CostModel`. That would leave the family with no admissible way to price its own central term, and the correct verdict would become REJECTED at Gate 0(4) — not exploratory, rejected — because a strategy whose revenue cannot be expressed in the firm's only cost library cannot be validated to this firm's standard. |
| 2 | **`N_conditioning` = 6** (§7.2) | A ruling from Validation that a menu-declared, pre-measurement, binding choice nonetheless contributes its full menu size. **If that is the ruling, this family's honest `N` is 27,000, `MinBTL` is 16.79 years against 6.571 available, and the family is dead on arrival exactly as `forward-lag-001` is.** This seat would accept that and write the KILL memo the same day. It is the single ruling that most changes this document. |
| 2b | **F-002's decisiveness** (§5.3, §5.5) | A measured leg-(ii) false-spare rate materially above 0.10 under C11's calibration. The joint figure of 1.3 × 10⁻⁴ is only as good as its weakest term, and **that term is the one this seat assumed.** If C11 returns 0.4, F-002's joint rate is 5 × 10⁻⁴ — still decisive; if it returns something near 1.0, leg (ii) is decorative and must be replaced before sealing. **I-029 is filed against this seat and the correct response to it is to name the term that could repeat it.** |
| 3 | **Persistence escape (c)** — mandate segmentation (§4) | Measured aggregate open interest **falling** as funding rises above its trailing baseline. That shows the supply side already de-scales, the sizing behaviour this family claims is unoccupied is occupied, and the only escape supporting a durable edge is dead. **Currently unmeasured: OI is not in `pit.db` and no loader exists.** |
| 4 | **The bar-granularity choice K6** (daily) | F-002 leg (ii) firing. That would be the measured demonstration that a daily instrument cannot dodge an intraday event, and the response is the successor family at 1h or 8h bars (§19.3) — **not a defence of the daily choice.** |
| 5 | **The intended allocation of $250,000** (§13) | A measured capacity below $2.5M of daily depth per leg on BTC or ETH perpetuals. The measurement is cheap (§15 step 4) and this seat expects it to clear comfortably [inferred]; if it does not, the allocation falls to whatever 1/10th of measured depth supports, and §13.2's materiality gets worse rather than better. |
| 6 | **The claim that this family's arithmetic works** (§19.1) | Validation ruling §11.3 in the second or third sense — that `oos_index` must carry the forward holdout window. **Earliest Gate 1 then moves from `C + 12 months` to `C + ~2.19 years` or `C + 4 years`** ~~from 2027-07-28 to 2028-10-05 or 2030-07-28~~ **[R34 · 2026-08-11]**, **and the honest verdict becomes ADMITTED-AS-EXPLORATORY**, because a family whose verdict is four years out is not meaningfully different from one whose verdict is unreachable. **This is the ruling this seat most wants and least controls.** |
| 7 | **The recommendation to accept the R4(b) haircut without argument** (§11.6) | Nothing this seat currently anticipates. The FX carry-crash literature is the direct public analogue of this family's sizing rule and this seat is not going to pretend otherwise to save 3 points of t-statistic. |
| **9** **[R3 · NEW]** | **The R3 decision to drop SOL rather than control for the break** | **A published, dated citation establishing when SOLUSDT's ±2.00% cap REVERTED.** That single date is the entire difference between a break control being executable and not. `DATA-VERIFY-001` §7(4) records that no such source was found and that Binance states it does not announce subsequent adjustments [cited — official]. **If Seat 9 finds it, candidate (b) becomes better than (c)** — it would let the family keep SOL's cross-section and its tail observation under a fully documented control, and this seat would reverse R3 pre-seal and say so. |
| **10** **[R5 · NEW]** | **K7 contributing 1 to `N_conditioning`** | A Validation ruling that a data-validity rule triggered by a vendor's documented act is not a conditioning choice and contributes **0**. This seat declared 1 deliberately, per D-009's finding that erring low on `N` is the sycophantic direction. **If ruled to 0, `N_conditioning` returns to 6 and the trial budget should return to 80** — ceiling `N` = 86 either way, so nothing downstream moves. |
| **11** **[R7 · NEW]** | **The prediction that KC-002 clause (b) is the leading cause of death** (§14.2 R7) | A measured dynamic range on `z(t)` showing the ±25% notional threshold is crossed on ≥30 days despite the ~35% floor censoring. **That is not computable before sealing** — it is a trial — so this prediction is pre-registered as [inferred] and will be settled by the family's own forward window rather than argued about now. **If it is wrong, the successor named at §19.3 needs finer bars only; if it is right, the successor needs the uncensored premium index as well.** |
| **12** **[R9 · NEW · 2026-08-05]** | **The §7.2 escalation rule's replacement — a hard stop rather than an escalated successor** | **The I-053 harness repair landing**: a Validation-authorized route that preserves the `InheritedCountDoubleCountError` raise by default and permits registration against a logged `n_inherited_escalation_authorized` event, green against acceptance test ML-T-14. **On that day the sealed text's own formula — `n_inherited = (menu size − 1) × chain_total` — becomes executable and the hard stop lifts without any amendment to this family.** Nothing else changes it: **this seat will not accept a lower `n_inherited` to obtain a registration the escalation refuses**, and says so here so that a future seat under schedule pressure has to overrule a written sentence rather than fill a silence. |
| **13** **[R10 · NEW · 2026-08-05]** | **The pre-registered expectation that Gate 1 is PARK-WITH-TRIGGER rather than PROCEED conditional on F-002 surviving** (§19.3, §5.4 R10) | **A measured autocorrelation on THIS family's net return series materially below the firm's one measured instance of ρ = 0.83.** The order-20 required uncorrected pre-haircut `t` is arithmetic on two cited multipliers at *that* ρ, and the family's own ρ is **unmeasured** — measuring it is a trial and the registry is at 0. **If the family's net-return ρ comes in near zero, the corrected and uncorrected `t` figures agree, the composition collapses to the haircut alone, and §11.6's original reading stands.** Both figures are required side by side on every artifact for exactly this reason (§21). **This seat states its expectation is the pessimistic branch and will accept the measurement either way.** |
| **14** **[R11 · NEW · 2026-08-05]** | **The ML-2 assertion that this is not a fitted family** (§10.7, §21) | **Validation ruling any row of §10.7(a)'s check wrong at intake.** The most exposed row is the ±50% grid: ML-1 spares it *only* because the plateau centroid advances by rule, so **any future artifact that reports or carries forward `argmax_params` as the configuration makes this family a fitted family retroactively**, at which point ML-13 charges the grid's full cardinality and ML-3's ceiling of 109 is breached by the grid alone. **The assertion is sealed and false-in-a-sealed-field is the penalty; that is the correct weight and this seat chose it deliberately.** |
| **15** **[R14/R16 · NEW · 2026-08-06]** | **The threshold this document is written against: `ρ̂` ≤ 0.034** | **A Validation act moving it, in either direction, made BEFORE a Gate 1 evaluation on this family and never during one.** Nothing else — and specifically **not** a measured `ρ̂` that lands just above it. **The bands at §10.8 are pre-committed precisely so that a near-miss is a PARK and not a negotiation**, and this seat has recorded them in its own pre-registration so that it is the sponsor, not Validation, who is bound by them first. **If `ρ̂` measures 0.036, this family is PARKed and this seat writes the PARK memo without argument.** |
| **16** **[R15 · NEW · 2026-08-06]** | **The declared planning `ρ_plan` = 0.10 and the 47-trial Stage 1 authorization** | **A measured `ρ̂` on this family's own logged trials.** That is the whole content of the two-stage construction: `ρ_plan` is a budgeting assumption held **only** until measurement replaces it, and it moves the authorization in **whichever direction it measures** — up to the full 79 at ρ̂ ≤ 0.034, down to zero further trials at ρ̂ ≥ 0.20. **What would NOT change it: a good early result, a schedule, or an argument that the Stage 1 cut is costing the family capability.** It is costing the family capability; that is the price of not pre-registering a budget the measurement may disallow, and §10.5.2's asymmetry argument is the pre-registered reason it is worth paying. |
| **17** **[R18 · NEW · 2026-08-06]** | **The finding that I-060 does not bite this family** | **A Validation ruling that any row of §10.7(a)'s not-a-fitted-family check is wrong** — at which point ML-3–ML-27 reach this family, ML-16's 32-trial dispersion sample becomes a mandatory *incremental* cost rather than a free by-product of the grid, and ML-13 charges the grid's full cardinality. **§10.9(a) is written so that this dependency is visible rather than buried: the I-060 answer is downstream of the fitted-family answer, and if the latter flips the former flips with it.** **Separately, and NOT contingent on that ruling: the substantive collision I-060 names already reaches this family at ρ̂ > 0.034, one notch tighter than I-060's own 0.045, and no ruling repairs that.** |
| **18** **[R19/R20 · NEW · 2026-08-10]** | **`n_inherited = 7`, and with it the claim that §10.5.2's Stage 2 unlock table is the one the harness will apply** | **A Validation ruling that `n_inherited` is reserved for inheritance from a predecessor chain and may not carry a family's own declared conditioning floor.** That is the one ruling that reverses R19, and this seat has put it to C2 directly at C13(e) rather than assuming the favourable reading. **If it is the ruling, the consequence must be stated with it and this seat states it now: `declared_ceiling_base` returns to 47, §10.5.2's table becomes permissive by 7 trials at `ρ̂` ≈ 0.05 and by 8 at `ρ̂` ≈ 0.10, and the two-stage construction admits materially more than the document declares at exactly the rungs where the family is in trouble.** There is no third outcome — the base is `n_inherited + sealed` and nothing else feeds it [measured]. **This seat would accept the ruling and would ask that the permissiveness be recorded on the face of every Validation Report on this family, because a gate looser than its own document says is worse than no gate that anyone believes in.** |
| **19** **[R21 · NEW · 2026-08-10]** | **The weight this document places on any limit stated in `universe`, `horizon` or `success_criteria`** | **Nothing available to this seat, and that is the point of recording it.** Those three fields have **zero consumers in the harness** [measured] and no ruling changes that; only code does. **What would change this seat's mind is a harness that reads one of them** — and this seat is not asking for one, because most of what is in them (K3's "exclude nothing," the no-winsorization clause, F-002's "evaluated ONCE") **cannot be mechanised and should still be written down.** **The change R21 makes is to the document's language, not to its content: these are commitments by the seats bound to them, and every sentence that implied a machine was watching has been corrected.** If a future artifact on this family cites a clause in one of those three fields **as though the harness enforced it**, that artifact is defective and §10.10 is the pre-registered reason why. |
| 8 | **Anything about the funding carry being an edge** | Nothing. §3.3 says it is not, §5.4 of the Charter says the firm does not pay for it, and **the only claim this document makes is about conditioning.** If a future artifact reports this family's raw carry Sharpe as though it were the result, that artifact is defective and this section is the pre-registered reason why. |

---

*Director of Research · Castellan Capital · 2026-07-28 · **revised R-001, 2026-08-04, pre-seal (I-045)** · **revised R-002, 2026-08-05, pre-seal (RULING-004 ceiling correction · I-053 · I-050 · C12)** · **revised R-003, 2026-08-06, pre-seal (SPEC-002 · the ceiling sealed as a function · ρ̂ ≤ 0.034 · staged budget at ρ_plan = 0.10 · I-057 · I-060 · I-061 · I-063 · I-064)** · **revised R-004, 2026-08-10, pre-seal (GATES.md §4.7.2 audit · `n_inherited` 0 → 7 · Stage 1 registered as the sealed `trial_budget` = 47 with Stage 2 as a SPEC-003 CONTINGENT extension · I-104 · I-105 · I-130 · I-131 · I-132 · I-133 · I-134 · I-135 · I-136)***

> **[R-004 · 2026-08-10] THE REGISTRATION PAYLOAD IS A SEPARATE ARTIFACT AND IT GOVERNS.** `research/REGISTRATION-PAYLOAD-PREREG-002.md` carries the sixteen binding fields with their final values. **Anywhere this document's prose and that payload could diverge, the payload is what gets passed to `open_hypothesis`** — which is I-105's lesson stated as a rule rather than as a finding, and the reason the payload exists at all. **`open_hypothesis` IS the seal** (P1 computes `prereg_sha256` on first registration [measured]); registration and sealing are one act; and that act is a Standing Order 002 §4 hard interrupt, blocked on **C2, C3, C7, C8, C11**.

*~~This document is complete and sealable.~~ **[R-001 · 2026-08-04] This document is COMPLETE and NOT YET SEALABLE.** It is not sealed. Sealing fixes `C` (D-007) and is Pod B's act, after Validation's Gate 0 intake. Nothing may be added after.*

> **SEAL-READINESS, STATED HONESTLY BY THE SEAT THAT WOULD BENEFIT FROM STATING IT OTHERWISE.**
>
> **[R-002 · 2026-08-05] The I-045 defect is closed. C12 is discharged. The document is STILL NOT SEAL-READY, and five conditions remain open — none of them created by this revision, and none of them relaxed by it.**
>
> | Blocker | Status |
> |---|---|
> | ~~**C12 · in-sample cadence sweep on BTC and ETH** **[R5 · NEW]** — **OPEN, BLOCKING**~~ | **[R12 · 2026-08-05] DISCHARGED, NARROWLY.** 0 deviating days of 4,802 symbol-days on BTC and ETH, both directions, full span [measured — `DATA-VERIFY-002` §3–§4], with SOL's 11 deviating days as a working positive control. **Verified the CADENCE dimension only: the documented 2025-09-18 formula change shows 3 prints on both symbols, so a cadence sweep is blind to the PARAMETER dimension, which K7 governs by declaration rather than by measurement.** §20 and §7.1.1 carry the full statement. **This is not the closure of I-045, which is `quant-validation`'s.** |
> | **C2 · Validation's Gate 0 intake verdict on this document** | **OPEN — BLOCKING.** No Gate 0 intake verdict on PREREG-002 exists; Ruling 003 is a cost-model specification and explicitly is not one [cited — `VALIDATION-RULING-003` §7.2]. |
> | **C11 · the leg-(ii) null calibration** | **OPEN — BLOCKING.** Required measured before sealing [cited — `VALIDATION-RULING-003` §6.6]. ≤2 trials. |
> | **C3 · Devil's Advocate Red-Team Memo** | **OPEN.** None exists. Blocking on Gate 1, and the seat's reserved Opus unit is the mechanism. |
> | **C7 · KC-002 signed by sponsor and Principal** · **C8 · seal and vault in one session/UTC day** | **OPEN — BLOCKING**, and executional rather than analytical. |
> | **C1 · the funding-cost repair** | **DISCHARGED as a specification** [cited — `VALIDATION-RULING-003` §7.1]; **implementation open as I-034**, which closes when the 19 acceptance tests plus the existing suite are green **and not before**. Ruling 003 makes the ordering binding: **repair green → seal → F-002.** |
> | **C9 · perp OHLCV** | **CLOSED** [measured — `DATA-INGEST-002` §2]. |
> | **C13 · Validation's ruling on R-002's three items** **[R11/R9 · NEW · 2026-08-05]** | **OPEN — NOT a separate blocker.** Resolved inside C2's intake verdict: the ML-2 assertion and its §10.7(a) check; the repaired §7.2 escalation rule in its hard-stop form; and whether ML-17's own formula takes I-055's correction. Listed so the intake knows what it is being asked. |
>
> **D-015 records the Principal's reading and R-001 was an instance of it: *"the ceiling binding at the seal is the control functioning."* A seal that should not happen is not a failure.**
>
> **[R-002 · 2026-08-05] WHAT THIS REVISION DID TO SEAL-READINESS, IN THE DIRECTION THAT IS LESS FLATTERING.** R-001 created a blocker (C12) and named it first. **R-002 creates none, discharges one, and nonetheless leaves the document further from a comfortable seal than it found it** — because the three repairs are, in substance: a ceiling that was one trial too generous, a **control this document called its most important one that was inoperative for the whole of its existence** (§7.2, I-053), and a **Gate 1 margin that is materially narrower than R-001 recorded** (§5.4, §19.3, I-050). **None of those blocks the seal. All three make the sealed document a worse-looking and more accurate description of the same family, which is the only direction a pre-registration is allowed to move in before it freezes.**
>
> **The five that remain open and blocking — C2, C3, C7, C8, C11 — are unchanged by this revision and are not this seat's to clear.**
>
> ---
>
> ### **[R-003 · 2026-08-06] SEAL-READINESS AFTER R-003.**
>
> **THE SAME FIVE REMAIN OPEN AND BLOCKING — C2, C3, C7, C8, C11. R-003 CLEARS NONE OF THEM AND CREATES NO SIXTH.** It is a disclosure-and-budget revision, not a condition-clearing one, and this seat states that plainly rather than presenting three new sections as progress toward a seal.
>
> | Blocker | Status after R-003 |
> |---|---|
> | **C2 · Validation's Gate 0 intake verdict** | **OPEN — BLOCKING.** Unchanged. **R-003 adds to what C2 is being asked**, without adding a blocker: whether the §10.4.1 functional form as written is the form Validation wants sealed, and whether §10.5.2's Stage 2 unlock rule is an acceptable sponsor-side control or must be refused as a budget with a door in it. **Folded into C13, not listed separately.** |
> | **C3 · Devil's Advocate Red-Team Memo** | **OPEN.** Unchanged. **R-003 hands the red team a new and better target: §10.5.2's two-stage budget, and §10.5.1 reason 4, which is this seat's own [inferred] structural argument that this family sits in the upper half of the cited `ρ̂` interval.** That argument cuts against the family and is offered for attack anyway. |
> | **C7 · KC-002 signed · C8 · seal and vault same UTC day** | **OPEN — BLOCKING**, executional. Unchanged. |
> | **C11 · leg-(ii) null calibration** | **OPEN — BLOCKING.** Unchanged. **≤ 2 trials, and they are now inside Stage 1's 47, which is the authorization they run against.** |
> | **C1 · funding-cost repair** | Specification **discharged**; implementation open as **I-034**. Unchanged. |
> | **C10 · I-022** | **OPEN, WEIGHT INCREASED** — see §20. It now latches Stage 2's gate as well as the headline budget. |
> | **C12 · cadence sweep · C9 · perp OHLCV** | **DISCHARGED (narrowly) / CLOSED.** Unchanged. |
> | **C13 · Validation's ruling on R-002's three items** | **OPEN — NOT a separate blocker.** **[R-003] Extended by two: the §10.4.1 functional form, and the §10.5.2 Stage 2 unlock rule.** |
>
> **WHAT R-003 DID TO SEAL-READINESS, IN THE DIRECTION THAT IS LESS FLATTERING — WHICH IS THE ONLY DIRECTION IT MOVED.**
>
> **R-003 cut this family's authorized trial budget by 40% and its declared ceiling from 86 to 54, voluntarily, on an assumption this seat named rather than measured.** It replaced a constant this document had defended twice with a function whose value is unknown and can only fall. It recorded, in the sponsor's own pre-registration, the verdict bands under which the sponsor loses. And it disclosed that **the intake ceiling of 109 that §1 and §10.4 have quoted since 2026-07-28 was never a budget and cannot be made into one** (I-063).
>
> **None of that blocks the seal, and all of it makes the sealed document a worse-looking and more accurate description of the same family — which R-002 recorded as the only direction a pre-registration is allowed to move in before it freezes.** The Principal's reading, recorded at D-015, applies to R-003 exactly as it applied to R-001: **"the ceiling binding at the seal is the control functioning." A seal that should not happen is not a failure, and a ceiling that binds tighter than the sponsor hoped is the machinery answering.**
>
> ---
>
> ### **[R-004 · 2026-08-10] SEAL-READINESS AFTER R-004.**
>
> **THE SAME FIVE REMAIN OPEN AND BLOCKING — C2, C3, C7, C8, C11. R-004 CLEARS NONE OF THEM AND CREATES NO SIXTH.** It is a registration-correctness revision: it changes what the sixteen fields will contain, and it changes nothing about whether they may yet be written.
>
> | Blocker | Status after R-004 |
> |---|---|
> | **C2 · Validation's Gate 0 intake verdict** | **OPEN — BLOCKING.** Unchanged. **R-004 adds four items to what C2 is being asked** — `n_inherited = 7`; the Stage 2 CONTINGENT form; I-045; and whether I-134/I-135 bear on the verdict — **folded into C13(e)–(h), not listed separately.** |
> | **C3 · Devil's Advocate Red-Team Memo** | **OPEN.** Unchanged. **R-004 hands the red team its best target yet and this seat names it rather than waiting: §10.10's finding that nine of sixteen binding fields are read by nothing means most of this document's asserted controls are assertions.** The DA should attack the three that are load-bearing — the haircut, KC-002's silence clause, and §7.2's escalation rule — and this seat will not defend any of them as enforced. |
> | **C7 · KC-002 signed · C8 · seal and vault same UTC day** | **OPEN — BLOCKING**, executional. Unchanged. **C8 gains one mechanical requirement from R23: `forward_window_start` must equal the vault's `cutoff`, both being the UTC day of the call.** |
> | **C11 · leg-(ii) null calibration** | **OPEN — BLOCKING.** Unchanged. ≤ 2 trials, inside Stage 1's 47. |
> | **C1 · funding-cost repair** | Specification **discharged**; implementation open as **I-034**. Unchanged. |
> | **C10 · I-022** | **OPEN, WEIGHT INCREASED AGAIN.** R-003 raised it because Stage 2's gate depends on the same criterion. **R-004 adds I-132: `log_trial` reads no budget at all, so the budget has no spend-time control in either stage** — the latch is broken *and* the door is only inspected after the fact. |
> | **C12 · cadence sweep · C9 · perp OHLCV** | **DISCHARGED (narrowly) / CLOSED.** Unchanged. |
> | **C13 · Validation's ruling on the items folded into C2** | **OPEN — NOT a separate blocker. [R-004] Extended by four: (e)–(h) above.** |
>
> **WHAT R-004 DID TO SEAL-READINESS, AND FOR ONCE IT MOVED IN BOTH DIRECTIONS.**
>
> **Toward a seal, and this is the first revision of which that is true:** the document that would have been sealed before this revision **would have sealed a Stage 2 gate that does not exist** (I-105), **a false statement of harness fact** (I-131), **a disclosure line that becomes false the moment the correction is made** (I-105/I-131 together), **a base that makes its own unlock table permissive by up to eight trials** (I-130), **a method section over its own budget by four** (I-136), and **a stale window-start literal** (R23). **Six defects, all pre-seal, all cheap now and all permanent later.** R-004 is the first revision whose content is *the document being made registrable* rather than the family being made smaller.
>
> **Against the family, which is the half that matters more:** **the registry-enforced denominator rises by 7 at every stage.** R-003 cut what this family may spend; **R-004 raises what it is charged for what it spends**, and the charge lands in DSR and in MinBTL rather than on a report face. And §10.10 records that **the majority of this document's stated limits are enforced by no field at all** — including the 50% haircut from which §5.4 derives the family's largest acknowledged hurdle, and KC-002's silence clause, which this seat wrote, defended, and has now established the engine has never been able to fire.
>
> **D-015's reading holds a fourth time.** *"The ceiling binding at the seal is the control functioning."* **A control that turns out not to exist is the same lesson arriving one layer up, and finding it costs a revision now and would cost the family its Gate 1 verdict later.**
>
> ---
>
> ### **[R-005 · 2026-08-10] SEAL-READINESS AFTER R-005.**
>
> **THE SAME FIVE REMAIN OPEN AND BLOCKING — C2, C3, C7, C8, C11. R-005 CLEARS NONE OF THEM AND CREATES NO SIXTH.** It is a labelling revision with two stale-harness-fact corrections attached, and **it changes no binding field's value.**
>
> | Blocker | Status after R-005 |
> |---|---|
> | **C2 · Validation's Gate 0 intake verdict** | **OPEN — BLOCKING.** Unchanged. **R-005 adds one item, C13(i)**, and hands C2 two findings it does not have to discover: **I-140** (C1 implemented; six stale sites, one of which downgrades this family tomorrow) and **I-142** (I-022 repaired; C10's two conditions met in substance). |
> | **C3 · Devil's Advocate Red-Team Memo** | **OPEN.** Unchanged — and **R-005 hands the red team the sharpest target this document has yet produced: thirty-four class-(c) commitments, named, in one table, with F-002 itself among them.** The register is an attack surface presented as a map, deliberately. |
> | **C7 · KC-002 signed · C8 · seal and vault same UTC day** | **OPEN — BLOCKING**, executional. Unchanged. **Both are now class (b) with executor, cadence and artifact named (B-05, B-06), so what has to happen is legible rather than implied.** |
> | **C11 · leg-(ii) null calibration** | **OPEN — BLOCKING.** Unchanged. ≤ 2 trials, inside Stage 1's 47. |
> | ~~**C1 · the funding-cost repair** — specification discharged; implementation open as I-034~~ | **[R26] DISCHARGED IN SUBSTANCE. THE IMPLEMENTATION LANDED 2026-07-29 AND THIS BLOCK CARRIED "implementation open" THROUGH R-002, R-003 AND R-004.** Formal closure of I-034 and of C1 routes to `quant-validation → head-of-data-infra` and **this seat does not hold it.** Filed **I-140, HIGH.** |
> | ~~**C10 · I-022**, weight increased twice~~ | **[R27] WEIGHT FALLS. I-022 is repaired and passing since 2026-08-05** (`DATA-IMPL-007` §5, all 19 green). `VALIDATION-SPEC-003` §12 conditions C10's discharge on I-022 closing **and** on this document registering Stage 1 as its sealed `trial_budget` — **R-004 did the second at 47. Both conditions are met in substance; only the formal closure is outstanding.** Filed **I-142, MEDIUM.** |
> | **C12 · cadence sweep · C9 · perp OHLCV** | **DISCHARGED (narrowly) / CLOSED.** Unchanged. |
> | **C13 · Validation's ruling on the items folded into C2** | **OPEN — NOT a separate blocker. [R-005] Extended by one: (i), the haircut's 2× permissive gap and the C5 ruling that closes it.** |
>
> **WHAT R-005 DID TO SEAL-READINESS, AND IT MOVED IN BOTH DIRECTIONS FOR THE SECOND REVISION RUNNING.**
>
> **Toward a seal:** the document that would have been sealed before this revision **would have frozen a condition precedent that downgrades this family to ADMITTED-AS-EXPLORATORY on 2026-08-11 on a false premise**, would have frozen a recommendation box saying its own breakeven cost is unstateable when the instrument to compute it shipped eleven days ago, and would have frozen the claim that its trial budget is *"enforced by this seat and by nothing else."* **All three are stale statements of harness fact and all three run against the family. R-004 caught one of this class (R19(b)); R-005 caught two more, and the honest reading is not that the harness improved — it is that this seat did not check.**
>
> **Against the document, which is the half that matters more:** **thirty-four of this family's sixty-one stated limits are enforced by nobody and nothing except audit and adversarial review**, and that now includes **F-002 itself**, whose four legs and stated α live in a field guaranteed only to be non-empty. **And the haircut gap runs permissive by exactly 2× at Gate 1's t-criterion** — at the hurdle §11.6 calls the largest this family faces — opening a branch in which this family is reported PROCEED at half the Charter's bar.
>
> **D-015's reading holds a fifth time, and the direction is worth naming.** *"The ceiling binding at the seal is the control functioning."* **R-004 found a control that turned out not to exist. R-005 found two that turned out to exist while the document said they did not.** Both are the same failure of verification, and only one of them is the kind a seat is tempted to look for. **A document that only ever discovers its own protections are weaker than claimed is not being audited — it is being flattered in the other direction.**
>
> ---
>
> ### **[R-006 · 2026-08-11] SEAL-READINESS AFTER R-006 — AND THE BLOCKING SET IS RE-STATED AS THE TWO SETS IT ALWAYS WAS.**
>
> **SEAL-BLOCKING: C2 · C7 · C8 · C11 — four, not five.** **VERDICT-BLOCKING: C3 · C5 · C4 · C10.** **R-006 clears none of either set and creates no new member of either.** The directed six-item set — **C2, C3, C5, C7, C8, C11** — is the union minus C4 and C10, and **this seat names the two it drops rather than inheriting a list**, because R-005's own block already merged a Gate-1 condition (C3) into a list of seal conditions and **merging two kinds of block into one list is the shape of error that produced I-140.**
>
> | Blocker | Set | Status after R-006 |
> |---|---|---|
> | **C2 · Validation's Gate 0 intake verdict** | **SEAL** | **OPEN — BLOCKING.** Unchanged. **R-006 adds two items, C13(j) and C13(k)**, and hands C2 three findings it does not have to discover: **I-151** (house rule 5's instrument costs 0–42 trials against a Stage 1 that sums to exactly 47), **I-153** (`forward_kill_condition` clause 5 terminates this family with certainty as drafted), and **I-154** (§11.4's R3 table was named by R23 and never reached). |
> | **C7 · KC-002 signed · C8 · seal and vault same UTC day · C11 · leg-(ii) null** | **SEAL** | **OPEN — BLOCKING.** Unchanged. |
> | **C5 · the point of application of the §4.6 haircut** | **VERDICT — A LOCK** | **OPEN — BLOCKING ON GATE 1 EVALUATION AND ON ANY REPORTED VERDICT, ABSOLUTELY**, on the Principal's ruling: *"a path to half the Charter's bar existing quietly is exactly what the relabeling mandate existed to surface, and its first substantive yield gets a lock, not a footnote."* **And the ruling is in three parts, only the first Validation's** — the point of application (Validation), its ratification as a §4 threshold act (**the Principal**, because the effective bar moves between 3.0 and 6.0 while the literal constant does not), and the executor without which the first changes nothing (§20 C5). **The finding is that haircutting the RETURN SERIES is a no-op at every scale-invariant Gate 1 criterion, which is nearly all of them: C5 is a choice between a 2× hurdle and nothing.** |
> | **C3 · Devil's Advocate Red-Team Memo** | **VERDICT** | **OPEN.** **Moved out of the seal-blocking list, where R-005 had it, on §20's own column.** R-006 hands the red team its most concrete target yet: **the conformance at R32, which deletes a clause that would have killed this family, made by the family's own sponsor.** |
> | **C4 · the §11.3 holdout reading** · **C10 · I-022's formal closure** | **VERDICT** | **OPEN.** **Named here because the six-item framing drops both.** C4's three earliest-Gate-1 dates are now formulae in `C` (R34); C10's two conditions are met in substance (R27). |
> | ~~**C1 · the funding-cost repair**~~ | — | **[R29] DISCHARGED. I-034 CLOSED by the Principal 2026-08-11**, satisfied **2026-07-29** on commit `875874f` (*"Ruling 003 implemented: carry accounting, 139/139. **Closes I-034**"*), **discovery credit R-005.** *"A family does not get downgraded because its paperwork didn't learn what its repository did."* **Residual retained, not swept up: defect (d), class (c), C-25.** |
> | **C12 · cadence sweep · C9 · perp OHLCV** | — | **DISCHARGED (narrowly) / CLOSED.** Unchanged. |
>
> **WHAT R-006 DID TO SEAL-READINESS, AND IT MOVED IN BOTH DIRECTIONS FOR THE THIRD REVISION RUNNING.**
>
> **Toward a seal, and it is the shorter half:** the document that would have been sealed before this revision would have frozen **a condition precedent that downgrades this family on a premise false since 2026-07-29**, and — **found only by running the sweep this dispatch ordered** — **a clause 5 that terminates it with certainty on 2027-01-31 for failing to perform a computation its own field schedules for a later date.** **Two deaths, both clerical, both removed pre-seal, and the second strictly worse than the first because it kills where the first only downgraded and because its premise cannot be satisfied rather than merely happening to be false.**
>
> **Against the document, which is the half that matters more:** **fifteen of this document's twenty-four dated clauses carry a premise that is false today, and nineteen of the twenty-four are evaluated by nothing at all.** Two are class (a) — P7's UTC-day check and the `PITStore` ingest ceiling. **The document has been carrying a schedule it never reconciled to its own sequencing decision of 2026-08-04, including its own seal date, which was today and did not happen.** **And the mandatory house-rule-5 statistic costs between 9 and 42 logged trials, not the one this document, its Issue Log entry and its dispatch all assert, against a Stage 1 whose line items sum to exactly 47 with zero slack** — a seat following this document's own instruction would have blown the budget the document was written to protect.
>
> **D-015's reading holds a sixth time, and the pattern has now completed itself.** *"The ceiling binding at the seal is the control functioning."* **R-004 found a control that did not exist. R-005 found two that existed while the document said they did not. R-006 found a control that existed, was written to be undefeatable, and would have fired on the family that wrote it.** **A kill condition that kills correctly is the machinery working; a kill condition that kills with certainty is a clerical error wearing the machinery's clothes, and the only difference between them is a date nothing evaluates.**

> ---
>
> ### **[R-007 · 2026-08-12] SEAL-READINESS AFTER R-007 — REFRESHED, WITH R-006's SEPARATION CARRIED INTACT.**
>
> **SEAL-BLOCKING: C2 · C7 · C8 · C11.** **VERDICT-BLOCKING: C3 · C5 · C4 · C10.**
> **R-007 clears no member of either set and creates no new member of either.** It is a conformance pass and a register; **it moves no binding field's value, no threshold, no menu and no selection.**
>
> | Blocker | Set | Status after R-007 |
> |---|---|---|
> | **C2 · Validation's Gate 0 intake verdict** | **SEAL** | **OPEN — BLOCKING.** Unchanged. **R-007 adds no C13 item and hands C2 four findings it does not have to discover: I-171** (the `FORMULA` recognizer is case-sensitive, so clause 5 — the automatic-termination clause — extracts as a **bare `C`**, and the field is caught only by E-14, only because the struck literal is still in it), **I-172** (there are **zero `SPAN` sites** in this family, so E-9 and **E-21's named proof case** never run), **I-173** (registering as the document stands returns a permanent nonzero exit and therefore a permanent `INSUFFICIENT-DATA`), and **I-176** (§11.1's span is exact, not understated). |
> | **C13(k) · the I-153 instance** | **SEAL, inside C2 at row 3** | **UNDISCHARGED, AND EXPLICITLY NOT DISCHARGED BY R38.** The Principal has ratified the seat's **routing**; **Validation holds the instance** and the alternative — the drafted literal `2027-01-31` sealed as drafted, with a window shortened by however long the seal took — **is live for Validation to take. The seal does not proceed past it.** If Validation takes it, the dated-clause payload's rows 74 and 76 and D-7's mapping change and the payload is reissued. |
> | **C7 · KC-002 signed · C8 · seal and vault same UTC day · C11 · leg-(ii) null** | **SEAL** | **OPEN — BLOCKING.** Unchanged. |
> | **C5 · the point of application of the §4.6 haircut** | **VERDICT — A LOCK** | **OPEN — BLOCKING ON GATE 1 EVALUATION AND ON ANY REPORTED VERDICT, ABSOLUTELY.** Unchanged by R-007. |
> | **C3 · Devil's Advocate Red-Team Memo** | **VERDICT** | **OPEN.** R-007 hands the red team a second concrete target beside R32's conformance: **R38 is the Principal ratifying a repair that removed a certain kill from the sponsor's own family**, and the red team should read it as such. |
> | **C4 · the §11.3 holdout reading** · **C10 · I-022's formal closure** | **VERDICT** | **OPEN.** Unchanged. **C4 gains weight at R37:** its three readings are formulae in `C`, and R37 establishes that the in-sample span backing them is bounded by ingest and not by `C`. |
> | ~~**C1**~~ · **C12 · C9** | — | **DISCHARGED / DISCHARGED (narrowly) / CLOSED.** Unchanged. |
>
> **WHAT R-007 DID TO SEAL-READINESS.** **Nothing, toward a seal — and that is the correct outcome for a conformance pass.** Against the document it did two things. **First, it measured the one figure the firm had agreed to label rather than measure, and the label was wrong in the family's favour** — R34 said the 0.43-year MinBTL margin was understated; it is exact. **Second, it produced the number the Principal asked for and the number is 10 of 24.** Thirteen of the fourteen misses are clauses that live in prose no registry field carries. **E-25(3) named that gap in advance and this seat's answer is the one Validation already gave: the remedy is registration, not a gentler checker — and registration here means moving the clause into a binding field or striking it, which is a revision this dispatch did not fund and did not start.**
>
> **D-015's reading holds a seventh time, and the direction has now reversed.** *"The ceiling binding at the seal is the control functioning."* **R-004 found a control that did not exist. R-005 found two that existed while the document said they did not. R-006 found a control that would have fired on the family that wrote it. R-007 found a control — E-21's direction-blindness proof case, built specifically to catch §11.1's span — that exists, is correct, and has no site to act on.** **A control aimed at a defect it cannot reach is the most expensive kind, because everyone downstream believes the defect is covered.**

---

*Director of Research · Castellan Capital · **revised R-005, 2026-08-10, pre-seal (S3-D-003, the class mandate)** · **revised R-006, 2026-08-11, pre-seal (S3-D-006 — C1 DISCHARGED / I-034 CLOSED · house rule 5 priced · C5 locked · the dated-clause sweep · I-150 · I-151 · I-152 · I-153 · I-154)** · **revised R-007, 2026-08-12, pre-seal (S3-D-014 — §11.1's span MEASURED · I-153 ratified in-field · seal-readiness refreshed · the dated-clause register · I-170 … I-179)***
*Trial budget ZERO. No hypothesis opened, no trial run, no registry write, no vault sealed, no issue closed, `harness/` not touched, no `VALIDATION-*` document touched, `book/` not written to, no test executed, no suite state reported, no commit. `test_h7` and `test_h8` not approached. `book/registry.db` reads **0 hypotheses / 0 trials** and must still read 0 / 0 when this document is put down.*
