# RED-TEAM MEMO 001 — the Sprint 1 agenda, its execution, and the forward-lag family

**Seat:** Devil's Advocate (Seat 5)
**Date:** 2026-07-28
**To:** the Principal · cc CIO, Validation, Director of Research, Pod B
**Invocation:** 1 of 2 Opus units in the Sprint 1 allocation. The second is reserved for the mandatory Gate 1 Red-Team Memo.
**Status:** delivered. Not suppressible by the CIO or the Director of Research (Charter Seat 5).

House rule 6 applies throughout: **[measured]** = read or executed in this repository this session · **[cited]** = external named source · **[inferred]** = reasoned from measured/cited facts · **[assumed]** = unverified premise, flagged.

---

## 0. Scope

Two targets, per the convening instruction.

**Target 1** — the Sprint 1 agenda (`research/AGENDA-2026-07-28.md`), the four dispatches executed under it, and the firm's conduct in executing them. Nothing built before this seat was convened is exempt.

**Target 2** — the forward-lag family, attacked *before* pre-registration, when the memo is worth most because the design is still malleable.

**What I read** [measured]: `FUND_CHARTER.md` Parts II (Seat 5, 7), III, IV, V §5.3–5.4, Appendix B, Appendix C, Appendix D · `CLAUDE.md` · `.claude/agents/devils-advocate.md` · the agenda · `VALIDATION-RULING-001` §4 in full and §1–3 in summary · `VALIDATION-RULING-002` §3.4–4.2 in full · `VALIDATION-ACCEPTANCE-001` §2 · `DATA-SPEC-polymarket-usable-history.md` in full · `DATA-IMPL-002` §1, §12–14 · `DECISION_RECORD.md` D-001…D-006 · `ISSUE_LOG.md` I-001…I-018 · `harness/castellan/{gates,costs}.py` · `git log --stat`.

**What I ran** [measured]: `python3 -m pytest harness/tests -q` → **96 passed, 0 failed**, confirming Seat 9's claim in DATA-IMPL-002 §1 independently.

**What I did not do:** no code modified, no data fetched, no backtest run, no commit. Per instruction.

**Convening lateness is itself a finding and I open with it rather than accept the framing.** The agenda allocated me one unit to red-team the agenda *before* execution. Four dispatches ran first. The CIO self-reported this to the Principal as Appendix B #5 arriving as neglect rather than ceremony, and that self-report is correct and is to the CIO's credit. It does not repair the damage. The specific cost is measurable: **Ruling 001 §4.2 fixed the T1–T7 admissibility bar, and Seat 9's data spec then inherited it "as a fixed constant, not mine to move" (spec §2, T6 and T3).** The spec's own §8 says four of its judgment calls "may be moved *before* measurement runs and not after." I am the seat that was supposed to move them, and I was convened after the spec was written and one commit before measurement. I have found a defect in the T3 bar (§B.2.2 below) that a pre-execution red team would have caught for free. That is the price of the sequencing, in one concrete instance, and I expect it is not the only one.

---

# MEMO A — the agenda, its execution, and the firm's conduct

## A.1 The framing the CIO intends for the Monthly Letter is not honest, and its dishonesty is specific

The proposed framing [cited — convening instruction]: *"the firm discovered its instrument was untrustworthy and fixed it — a better outcome than a Sharpe produced by the old harness."*

**The counterfactual is false, and the firm's own agenda proves it false.** No Sharpe was ever going to be produced by the old harness this sprint, because **not one of the 25 allocated invocations was budgeted to run a backtest.** [measured — agenda compute table]:

| Seat | Units | What the agenda authorises |
|---|---:|---|
| Head of Data & Infra | 7 | ingest + vault change. No runs. |
| Quant Validation | 3 (→4) | rulings + intake verdicts. No runs. |
| Director of Research | 3 | pre-registration records + chair two reviews. No runs. |
| PM Pod B | 4 | *"Design only — no runs until the vault question is ruled and `pit.db` exists."* |
| PM Pod C | 2 | *"spec"* |
| Devil's Advocate | 2 | memos |
| CRO | 2 (→1) | risk meetings on an empty book |
| PM Pod A | 1 | *"Scoping memo, no runs."* |
| Ops | 0 | not activated |

**Zero execution units, by construction.** So the comparison "defects found *instead of* a Sharpe" compares the actual outcome against an outcome the agenda had already foreclosed. It is a counterfactual chosen because it flatters. That is Appendix B #6 — *"reports optimize for readability over honesty"* — applied to the firm's own performance narrative, which is the hardest place to notice it.

**The second falsity is in the word "discovered."** The firm did not discover that a vendor's instrument was untrustworthy. **It debugged code it wrote the same day** [measured — the entire harness lands in commit `64d15bd`, dated 2026-07-28; every subsequent commit is same-day]. Twelve defects in a ~2,000-line codebase written hours earlier is not a finding about the world. It is the ordinary, expected cost of writing software, and the ordinary cost of writing software is not a research result.

**The named failure mode.** The instruction asks me to find it or dismiss it. I find it, and it is two, in combination:

- **Appendix B #9 — "the firm confuses activity with progress."** Seven invocations, ~5,900 lines of artifact, eighteen issue-log entries, six decision records, zero hypotheses in the registry, zero rows in `pit.db`, zero terminal verdicts. The Charter's own remedy — *"the pipeline must have a throughput number and it must be reported"* — is being satisfied in letter (the agenda pre-announces throughput zero) while the letter's *narrative* is being written to make throughput zero read as a success.
- **Appendix B #6, self-applied.** Pre-announcing a zero and then reframing it as a superior outcome is more corrosive than simply missing a target, because the pre-announcement buys the credibility that the reframe then spends.

**What the honest Monthly Letter sentence is.** I will write it, so the firm does not have to negotiate with itself over the wording:

> *Sprint 1 produced no research. The firm spent its first sprint building and then repairing its own tooling, found twelve defects in code it had written the same day, and shipped a green 96-test suite. Four of those defects (I-007, I-014, I-015, I-016) would have produced wrong Gate verdicts and finding them was worth the compute. None of it is evidence about markets. Throughput: 0 against a target of 2. The firm has not yet demonstrated it can do the thing it exists to do.*

That sentence is defensible, complete, and costs the firm nothing it is entitled to keep.

**One thing in the CIO's framing that is true and should not be lost.** I-014 (a caller boolean returning `PASS` on the holdout criterion with zero registry events) and I-015 (a one-character typo permanently bricking a family against the Principal's own passphrase) are genuinely serious, and both were found by the independent line rather than by the seat that built the code. **The structure paid for itself in Sprint 1.** That is the honest win and it is a governance win, not a research win. It should be reported as such and it should not be laundered into a research narrative.

---

## A.2 Does the CIO's allocation survive Charter §5.3? Not on the composition test.

§5.3 [cited]: *"Compute is allocated on the same axes. A pod producing nothing gets less compute next month."* And: allocation shrinks on **persistent underuse of the risk budget** — *"a pod running at half its allowance is destroying the firm's return on allocated risk and is a real failure mode, not a safe one."*

**The literal test does not bite yet, and I say so rather than stretch it.** No pod has been given compute and wasted it. Pods A, B, C have consumed zero units. §5.3's sanction is prospective and the sprint is one day of fourteen old. An objection built on "the pods have produced nothing" would be theatre.

**The test that does bite is the composition test, and the CIO fails it.** [measured, from `git log` and the artifact set]:

| | Allocated | Spent, day 1 | Burn |
|---|---:|---:|---:|
| **Opus** | 10 | **4** (Validation ×3, this memo) | **40%** |
| Sonnet | 14 | 3 (Data & Infra) | 21% |
| Haiku | 0 | 0 | — |
| **Elapsed** | 14 days | **1 day** | **7%** |

**Opus — the constrained resource, with explicitly zero headroom [cited — agenda: "Opus has zero headroom"] — is burning at nearly six times the calendar rate, and 100% of it has gone to governance of the firm's own instrument.** Not one Opus unit has been spent on a market.

**And the contingency is already spent.** The agenda named exactly one pre-committed cut if Opus overran: the second Monday Risk meeting. D-006 spent it, to fund Validation's fourth unit. [measured — D-006: *"Fourth Validation Opus unit approved, funded by the pre-committed cut: the second Monday Risk meeting is dropped."*] **There is now no named funding source for a fifth Validation unit, and Validation's fourth unit is pre-committed to two jobs at once** — verifying that P1–P8, G1–G5 and R1–R4 actually landed (Acceptance 001: *"These gate my own next invocation"*), *and* taking the Gate 0 intake. [inferred] If that verification finds anything of the class it found in Acceptance 001 — where five findings the implementation note did not disclose emerged from an audit of code whose own suite was 63/64 green — **the Gate 0 intake does not happen this sprint, and there is no unit to pay for it.** The CIO's allocation has no slack on its single binding resource and has already consumed its only stated reserve.

**A second composition failure, quieter.** Seat 9's 7 Sonnet units were assigned an explicit ordered list: *(1) crypto — ccxt OHLCV + perp funding; (2) ETF panel; (3) EDGAR index.* [cited — agenda]. **Three units are spent and none of the three ordered items has begun** [measured — no `book/pit.db`; I-001 still open]. The seat instead produced the Polymarket data spec and two harness-remediation documents. Both were necessary. Neither was on the approved list. **The approved agenda's priority order was inverted in execution and no decision record or issue-log entry records the inversion.** House rule 7 — *"escalate uncertainty, do not resolve it silently"* — and a Principal-approved agenda is precisely the kind of document a silent reordering degrades. The 4 remaining Sonnet units must now cover three ingests *plus* the 13-step Polymarket measurement programme *plus* C-8/C-9/C-10. **That is not four units of work.** [inferred, but not marginally so.]

---

## A.3 Was the compute well spent? Partly. A cheaper sequencing existed and is identifiable.

**Concede first, because the objection is only worth what survives the concession.** Validation's three units produced real findings that could not have been produced more cheaply, and I want to name the specific one: **I-015 was found because Validation knew what acceptance criterion C4 *meant*.** C4's text is *"a typo must not brick a family."* The shipped test asserted only that the empty string is refused. No fuzzer, no property test, no Sonnet-tier reviewer working from the code alone would have found that, because the defect is a mismatch between an implementation and the *intent* of a criterion, and intent lives in prose. That is Opus-tier judgment doing exactly what Opus is for.

**Now the objection.** Four of the twelve defects were found by *executing the shipped code against adversarial inputs* — I-014 (`holdout_opened_once=True` returns PASS on zero events), I-015 (wrong passphrase seals and retires), I-016 (timezone string comparison false negative), I-017 (`ingest_documents()` unguarded). Validation reports these as *"demonstrated by execution against the shipped code"* [cited — Acceptance 001 §2]. **Execution against adversarial inputs is not an Opus task.** It is a Sonnet task, and a cheap one.

**The cheaper sequencing, stated concretely enough to adopt:**

> **Acceptance tests are written by the seat that set the criteria, before the implementing seat writes code.** Ruling 001 §5 itemised C1–C10 as prose. Seat 9 then implemented *and wrote the tests that judge its own implementation*. Every defect in the I-014/I-015 class is structurally an instance of *the implementer choosing the assertion*, and DATA-IMPL-002 §13 documents Seat 9 finding a second instance of the identical shape in `authorize_retry()` during its own re-audit — **which means the pattern recurred even after it was named**.

That change costs zero Opus, is a process amendment rather than a code change, and would have converted I-015 from a HIGH-severity find into a test that failed on day one. **It is not in the Issue Log and I am proposing it as a new entry (§A.6, proposed I-019).**

**What the alternative sequencing would have cost the firm.** Validation's Acceptance 001 unit would still have been needed — for C4-class intent defects and for the F1/F2 collision ruling — but it would have arrived at a codebase that had already failed its own adversarial suite, which is a shorter and cheaper audit. [inferred] Call it a saving of roughly half an Opus unit and, more importantly, the elimination of a *round trip*: Ruling → implement → audit → remediate → re-audit is five stages, and the firm is currently in stage five with its fourth Opus unit pre-committed to it.

---

## A.4 The agenda is not aimed at the firm's stated comparative advantage

Charter §3.5 [cited] names four areas where free public data is genuinely adequate, and instructs **this seat by name** to challenge drift:

> *crypto funding and basis · prediction-market microstructure · ETF-level macro and calendar effects · event-driven equity keyed to EDGAR filing timestamps. Those four are where the firm should spend most of its compute, and any research agenda that drifts away from them without an explicit reason should be challenged by the Devil's Advocate.*

**The allocation touches three of the four; the execution has touched one.** I will not overstate this, so both figures:

| §3.5 area | Charter's own view of the data | Units allocated | Units executed |
|---|---|---:|---:|
| Crypto funding & basis | *"Deep minute-level history. **Best data surface the firm has**"* (§3.2) | ~2 Sonnet (½ of Pod B) + Data&Infra item (1) | **0** |
| Prediction-market microstructure | *"**Thin history**; heterogeneous contracts; resolution rules matter enormously"* (§3.2) | ~2 Sonnet + **all 4 Opus spent to date** | **7 of 7 invocations, directly or as its blocking dependency** |
| ETF-level macro/calendar | — | Data&Infra item (2) | **0** |
| EDGAR-keyed event equity | *"Genuinely point-in-time by filing date. **The best PIT surface available**"* (§3.2) | **1 Sonnet, scoping memo only** | **0** |
| *(not in §3.5)* Pod C regime overlay | — | 2 Sonnet | 0 |

**The finding, stated without softening: the firm has directed 100% of its scarcest resource at the single thinnest data surface named in Part III, and 0% at the two the Charter calls its best.** The two areas the Charter describes in superlatives — crypto ("best data surface") and EDGAR ("best PIT surface") — have between them received one Sonnet unit of scoping that has not been spent.

**The defence, which I will state at its strongest and then reject.** The Polymarket work was not *research* on Polymarket; it was governance work (holdout regime, vault, registry) that happens to have been convened by a Polymarket-specific admissibility question, and the governance is reusable across all four areas. That is largely true of Rulings 001 §1–3 and Acceptance 001. **It is not true of Ruling 001 §4, the T1–T7 bar, the stratification schema, the effective-N method, the continuity rule, or the entire data spec — all of which are prediction-market-specific and none of which transfers.** [measured — Ruling 001 §4.1: *"it applies to prediction-market families"*.] Nor does it explain why item (1) of Data & Infra's ordered list, crypto, is untouched.

**The honest characterisation of the drift.** The agenda is aimed at the Principal's existing interest. That is not illegitimate — the Principal supplies direction and D-004 named the forward-lag family as the opening hypothesis explicitly. **What is illegitimate is that it happened without the explicit reason §3.5 demands, and that the seat §3.5 names as the check was convened after the fact.** The reason may well be good. It has not been written down. Write it down, or move compute to crypto.

---

## A.5 Is a nine-seat firm justified? The independent line, yes. Three pods, not yet.

**Justified, on evidence already in hand:** the three independent seats. The Validation line produced I-007, I-014 and I-015 — defects in code the CIO had reviewed and the building seat had tested green. That is the structural feature the Charter calls its most important, doing exactly what it is for, on day one. I can construct no objection to it and I will not manufacture one.

**Not justified, on evidence:** three pods. Pods A, B and C hold **7 of 14 Sonnet units** and have produced nothing — which is fine at day one — but two of the three are allocated to work the agenda *itself* forbids from reaching any conclusion this sprint ("scoping memo, no runs"; "spec"). Meanwhile Data & Infra, which is on the critical path for every other seat (I-001 blocks everything), is overcommitted by my count in §A.2.

**The reallocation I would make, stated as a recommendation the CIO can accept or reject in writing:** stand Pod C down for Sprint 1 and move its 2 Sonnet units to Data & Infra for the crypto ingest. Pod C's deliverable — a regime overlay spec — is by the agenda's own admission consumed by nobody this sprint (*"Pods A and B therefore condition on nothing until Sprint 2"*). Two units producing a document that no seat will read this sprint, while the seat blocking all three pods is short, is a misallocation the Charter's own §5.3 logic condemns.

**On the broader question — is this an elaborate structure around a two-seat workload?** Today, yes, and that is not damning at day one of fourteen. It becomes damning at sprint close if the ratio has not moved. **I propose that as a measurable test rather than a rhetorical question:** at 2026-08-11, if fewer than four of the nine seats have been invoked, the nine-seat structure has not been exercised and the Monthly Letter must say so.

---

## A.6 What I found that no existing Issue Log entry covers

Five items. Each is [measured] unless marked. None duplicates I-001…I-018.

**Proposed I-019 · The implementing seat writes the tests that judge its own implementation · Severity: MEDIUM · Owner: fable-5-cio (process)**
Ruling 001 §5 set acceptance criteria C1–C10 as prose; Seat 9 implemented and authored the proving tests. I-015 is the direct consequence (criterion said "a typo must not brick a family"; the test asserted only that the empty string is refused). DATA-IMPL-002 §13 records the *same shape recurring* in `authorize_retry()` after the pattern had already been named — evidence it is structural, not a lapse. Fix: acceptance tests authored by the criteria-setting seat, before implementation. Costs zero Opus.

**Proposed I-020 · `gates.py` returns PASS on an over-budget trial count · Severity: MEDIUM · Owner: head-of-data-infra**
[measured — `harness/castellan/gates.py:209–213`]:
```python
over = fam.trial_budget and fam.n_trials > fam.trial_budget
criteria.append(_crit(
    "Trial count N (registry)", fam.n_trials,
    f"logged; budget {fam.trial_budget}", True,          # <- verdict hardcoded True
    "OVER BUDGET — flagged to Director of Research" if over else ""))
```
The verdict argument is the literal `True`. A family that has blown its pre-registered trial budget by any margin reads **PASS** with a note. Charter house rule 3 makes the trial counter the object on which every Part IV statistic depends; a budget that cannot fail is not a budget. Seat 9 flagged this in DATA-IMPL-002 §13 as *"a design question I am flagging rather than silently passing over."* **It was not logged.** A disclosed defect that reaches no log is functionally undisclosed. Note the direction: it fails permissively — the same direction as I-010.

**Proposed I-021 · No cost preset can express prediction-market resolution risk, and the only admissible one mis-scales with contract price · Severity: HIGH · Owner: head-of-data-infra → quant-validation**
Two defects in `harness/castellan/costs.py`, which `CLAUDE.md` makes the *only* admissible source of cost numbers.
1. **`POLYMARKET` uses a fixed `half_spread_bps=100.0`** — its comment says *"1c on a 50c contract ~ 2%"* [measured]. The spread on an event contract is approximately fixed in **cents of contract price**, not in bps of notional. At a 10¢ contract with the same 1¢ spread, the true half-spread is ~500 bps. **The preset understates cost by ~5× at 10¢ and ~2.5× at 20¢**, and T6 admits everything above 2¢. A forward-lag strategy trades wherever the lag is, which is not restricted to 50¢. The error is permissive. [measured for the constant; inferred for the magnitude.]
2. **`CostModel` has no field capable of expressing oracle/resolution risk** [measured — the dataclass has commission, half-spread, impact, borrow, funding, and nothing else]. A Polymarket position carries a fat left tail from adverse or disputed resolution that no reference-asset leg hedges. Since hand-rolled costs are prohibited, **there is currently no admissible way to charge this family for its largest idiosyncratic risk**, and the paper book will systematically over-report its net.

**Proposed I-022 · Cross-venue clock alignment is unaddressed by the Charter, both rulings, the data spec, and the harness · Severity: HIGH · Owner: quant-validation**
[measured — the strings "cross-venue", "clock align", "venue clock" appear nowhere in `research/`, `reference/`, or `logs/`.] Charter §4.6's protection is *"never fill at the same bar that generated the signal."* The forward-lag family's failure mode is not same-bar; it is **cross-venue**. Polymarket trades 24/7; an ETF or futures reference asset does not. A signal printed on Polymarket at 03:00 UTC Saturday whose "next bar" in the reference asset is Monday's open is separated by ~53 hours during which the underlying news became universally known. **The measured "lag" is then the overnight/weekend gap, relabelled as alpha, and §4.6's one-bar rule is fully satisfied while the strategy reads the future.** I-016 has just demonstrated that this firm's store had a live timezone-comparison defect; this is the same class one level up, and it is the single most likely way this family produces a large, real-looking, uncapturable in-sample number. Full argument at §B.1.3.

**Proposed I-023 · The anti-sycophancy metric measures the wrong stage · Severity: MEDIUM · Owner: devils-advocate**
Appendix B #1 and I-003 track *Gate 1 pass rates* by hypothesis origin. **By the time pass rates are measurable, the selection has already happened one stage earlier, at attention allocation.** Current state [measured]: one hypothesis has a pre-registration pathway, two Validation rulings, a bespoke admissibility bar, a bespoke data spec, and 100% of the firm's Opus spend. It is the Principal's. Three non-Principal lines are allocated (perp funding carry, regime overlay, an EDGAR family) and all three are barred from reaching a conclusion this sprint by the agenda's own terms. **A firm can be perfectly unbiased in its pass rates and completely captured in what it chooses to test.** I-003 is not wrong; it is insufficient, and it will read as a clean bill of health while the real disparity sits upstream of it. I propose the tracked metric become **Opus units by hypothesis origin, reported every Monthly Letter**, which is computable today. Today's value is **4/4 = 100% Principal-originated.**

---

# MEMO B — the forward-lag family

## B.0 Steel-man first

**The thesis, in its strongest form I can construct.** A Polymarket binary contract and a reference asset (a rate future, an index ETF, a crypto perp) are both exposed to the same resolving event. When information about that event arrives, the two venues do not reprice simultaneously. The claim is that this asynchrony is (i) directionally consistent, (ii) long enough to trade, and (iii) larger than round-trip cost.

**The mechanism, stated as Gate 0(1) requires — who is on the other side and why they accept the loss.** Polymarket's marginal participant is an event specialist or a retail directional trader expressing a view on the *outcome*, in a venue with clean binary payoffs and no basis risk. That participant is not monitoring the reference asset and is not running a relative-value book. They accept the loss because they are not playing the same game: they are buying a clean expression of an opinion, and the spread they pay to a relative-value counterparty is the price of that cleanliness. This is the same structural story that explains why index-option skew persists against a hedging flow. **It is a real mechanism and I am not going to pretend it is not.**

**A second, independent supporting fact.** The venue is on a public chain with 24/7 access and no market-hours constraint, while the natural reference assets have closes, halts, and holidays. Asynchrony is *structurally guaranteed* to exist at some horizon. The question is never whether a lag exists — it does, mechanically — but whether it is exploitable.

Everything below attacks this version, not a weaker one.

---

## B.1 The artifact case — the strongest argument that any observed effect is a statistical artifact

Four mechanisms, ranked by how much they should move the decision.

### B.1.1 Selection — the declared `N` will be wrong by three orders of magnitude, and the firm has already measured its own lower bound

This is I-011 (`N`-deflation by model priors) with a specific number attached, and the number is what makes it decisive rather than philosophical.

The registry opens at `N = 0` by construction — D-006, I-002, and that is correct as far as it goes. But the *hypothesis that will be pre-registered* did not arrive at `N = 0`. **The firm has already recorded the prior search's shape: 5 tuned parameters and 1 regime exclusion** [cited — I-002]. A 5-parameter search evaluated at even five values per parameter is `5⁵ = 3,125` variants, and the regime exclusion is a sixth selection made after seeing which regime hurt.

Charter §4.1's own table [cited]:

| Trials N | Expected best Sharpe on pure noise (units of σ_SR) |
|---:|---:|
| 10 | 1.57 |
| 100 | 2.53 |
| 1,000 | 3.26 |
| 10,000 | 3.86 |

**The firm is planning to compute DSR and PBO against an `N` in the tens, while the search that actually selected this hypothesis is plausibly in the thousands.** At `N = 3,125`, a noise-only best Sharpe of ~3.4·σ_SR is expected. A Gate 1 submission reporting `N = 40` and `DSR = 0.96` would be arithmetically valid and substantively meaningless.

**Why none of the firm's existing controls touch this:**

| Control | Does it fix the denominator? |
|---|---|
| D-006 Option D (forward holdout) | No — forward data constrains the *test*, not the count |
| The Principal's pre-registration freeze rider | No — it binds the hypothesis from `C` onward; the search happened before |
| R4(b), the presumptive 50% published-signal haircut | **No** — the haircut scales the *edge magnitude*. `DSR` and `PBO` consume `N` **directly**, not through the edge. Halving a Sharpe does not correct a denominator |
| I-002's "any use of prior tuned parameters must be declared" | Unenforceable. The sponsor is the Principal, the parameters are in his head, and there is no artifact to audit against |

**The specific remedy I require before pre-registration, and I am stating it as a condition rather than a suggestion:**

> **The pre-registration must declare an `N_inherited`** — a stated, defended lower bound on the prior search — and `TrialRegistry.open_hypothesis` must open the family with `n_trials` seeded at that floor, not at zero. If the sponsor states `N_inherited = 3,125` (5⁵), the family's Gate 1 arithmetic becomes honest and probably fails, which is the correct outcome if it is the true one. **If the sponsor will not or cannot state a defended lower bound, the family is ADMITTED-AS-EXPLORATORY permanently, with no path to Gate 1 at any Sharpe** — on exactly the same logic Validation already pre-committed to for evidentiary length (Ruling 001 §4.4). An unreconstructable `N` is a harder disqualifier than a short history, because a short history at least fails honestly.

I regard this as the **single strongest objection in this memo** and I would act on it myself.

### B.1.2 Leakage — cross-venue clock misalignment, which nothing in this firm currently checks

Full statement of proposed I-022. The signal is *"Polymarket moved at time t, therefore the reference asset moves at t+Δ."* Its validity depends entirely on the two series being aligned to the same UTC instant with a strict causal lag.

**The failure mode.** Polymarket trades continuously. An ETF or futures reference asset does not. If the reference asset's "next bar" is its next *session*, a Polymarket print at 03:00 UTC Saturday is followed by a reference-asset observation ~53 hours later. In that window the news the Polymarket print reflected became universally known. **The backtest then measures the overnight/weekend information gap and labels it a lag.** It will be large, statistically strong, robust across parameters, and entirely uncapturable — because by the time the reference asset opens, its price already incorporates the same news.

**Why the firm's existing protections do not fire:**
- Charter §4.6's *"never fill at the same bar"* is satisfied — the fill is a different bar. The rule was written for a single-venue single-clock world.
- `knowledge_time ≤ decision_time` is satisfied — the Polymarket print genuinely was knowable.
- I-016's UTC normalisation fix (C-5) makes timestamps comparable but says nothing about *tradability windows*.
- The data spec's T1–T7 screen Polymarket contract-days. **It does not screen the reference asset at all** — the reference leg appears nowhere in the spec [measured].

**Required before pre-registration:** the pre-registration must state, as a binding design field, (i) the reference asset's tradable session in UTC, (ii) the rule mapping a Polymarket signal instant to the first *executable* reference-asset instant, and (iii) an explicit exclusion of signals whose execution instant falls more than one session boundary later — or, if such signals are retained, they must be reported as a **separate subperiod** with its own Sharpe, per the same logic as Ruling 002 R2's refusal to average mixed windows.

### B.1.3 Regime luck and fat tail — the stratification rule is blind to the concentration that will actually bite

Ruling 001 §4.3's >50%-concentration rule stratifies on four axes: resolution source class, settlement mechanics, dispute exposure tier, and asserted economic mechanism.

**None of those four is "the underlying event."** [measured — Ruling 001 §4.3; data spec §3 table.] Twenty contracts on twenty candidates in one election share a resolution source class (UMA), settlement mechanics (binary cash-settled), dispute tier, and the pod's asserted mechanism ("post-news forward-price lag"). **They pool into a single stratum and pass the concentration check as one legitimate stratum — while being one event.**

I must be fair about what *is* answered here, per my standing rule against recycling:
- The effective-`N` estimator `N_eff = n/(1+(n−1)ρ̄)` does catch within-cluster correlation via `ρ̄`, and will deflate `N` sharply inside an election cluster. **Genuinely answered.**
- Ruling 001 §4.1's continuity rule (≥60% coverage, no 90-day gap) does prevent "two dense clusters four years apart." **Genuinely answered.**

**The residual, which is not answered:** the >50% concentration rule is the instrument that decides whether *the hypothesis must be restated as being about one thing*, and it will not fire on the case where the family's evidence is one event. `N_eff` shrinks the count; it does not trigger the restatement. **Fix, one line:** add underlying-event identity as a fifth stratification axis, and apply the >50% rule to it. The data spec already builds a contract→event mapping (§3) for the `ρ̄` computation — the input exists and is unused for this purpose.

### B.1.4 Survivorship — completely unaddressed, and the data spec's own T7 makes it worse

**The data spec does not contain the word "survivorship"** [measured — grepped `research/`; the only hits are Ruling 001 §4.3 using it as a rhetorical analogy, and Part III's equity discussion].

Polymarket voids, delists, and removes contracts. A universe enumerated by an API query issued in 2026 returns **the contracts that still exist and resolved cleanly**. The contracts absent are disproportionately: low-volume markets that were pulled, ambiguously-worded markets that were voided, and markets whose resolution was disputed and reversed. **Those are precisely the contracts on which a lag strategy would have lost money** — the ones where the "information" the Polymarket price was leading on turned out not to be information at all.

**T7 actively worsens this.** T7 excludes contract-days where resolution criteria changed mid-life. That is correct for measurement cleanliness and **structurally removes the loss cases from the sample**. The data spec discloses T7's purpose but not its survivorship consequence.

Charter Gate 0(5) [cited] requires *"survivorship and look-ahead exposure identified and a mitigation named."* **On today's spec, the forward-lag family cannot satisfy Gate 0(5)**, because no survivorship exposure has been identified and no mitigation named. This is a Gate 0 failure available today, at zero cost, and I am surfacing it as such.

**Mitigation that would satisfy me:** enumerate the universe from an *archival* source — the on-chain condition registry, which is append-only and cannot retroactively drop a market — rather than from a live API listing, and report the count of markets present on-chain but absent from the API listing as a measured survivorship rate.

---

## B.2 The uncapturable case — real, but you cannot have it

### B.2.1 The capacity criterion is unevaluable, which is a FAIL, and nobody has said so

The data spec §2, T4 [cited]: if historical order-book depth is unretrievable, **"T4 is reported as unmeasurable, not proxied,"** and the count is qualified as *"6-of-7, T4 unconfirmed."*

**Follow that through to Gate 1.** Charter §4.4 requires: *"Capacity — ≥ 10× the intended initial allocation at target net Sharpe."* Capacity on a venue is a function of resting depth at the price the strategy needs. **If T4 is unmeasurable, capacity is unmeasurable.** And an unevaluable Gate 1 criterion is not "unconfirmed" — under Amendment A1 and Validation's own standard, a criterion that cannot be computed is **INSUFFICIENT-DATA, which is never PASS**, and Gate 1 requires *every* criterion to pass.

**Nobody has drawn this line.** Validation's pre-committed verdict rule (Ruling 001 §4.4) covers only calendar span and continuity. The data spec treats T4-unmeasurable as a reporting qualifier. **In fact it is a Gate 1 disqualifier, and it is decidable by a single documentation query — step 1 of the spec's own procedure — before one row is ingested.**

This makes the span question (I-004) potentially moot. The firm has been treating "is there four years of history" as the family's admissibility risk. **The binding risk may be "can depth be measured at all," and it is answerable this week for nearly nothing.**

### B.2.2 The T3 spread ceiling is calibrated one factor of two too loose — a live defect in an accepted bar

Ruling 001 §4.2 T3, inherited verbatim by the data spec §2:

> *Quoted half-spread ≤ 50% of the strategy's claimed per-trade gross edge.*

**Arithmetic.** A round trip pays the half-spread twice. `half_spread ≤ 0.5·G ⟹ round-trip spread cost ≤ 1.0·G`. **T3 as written admits contract-days on which spread alone consumes 100% of the claimed gross edge, before commission, before impact, before delay, before any of the rest of §4.6's stack.** A screen whose passing band includes exact-zero net is not a tradability screen.

This is not a quibble about a threshold; it is a units error between a per-side quantity and a round-trip quantity. **Fix: `S_max = 0.25·G`**, which budgets round-trip spread at ≤50% of gross edge and leaves the rest of the cost stack somewhere to live. This must move **before** measurement, per the spec's own §8 rule that judgment calls move before and not after — and the spec explicitly names the Devil's Advocate as one of two seats entitled to move them. I am exercising that.

### B.2.3 The 71.5% win rate is not merely inadmissible — it is the wrong statistic, and its survival is evidence about how this family has been evaluated

I-002 kills the number on `N` grounds. I want to kill it on a second, independent ground, because the `N` argument leaves the impression that a properly-counted 71.5% would mean something.

Charter §5.4 [cited]: *"hit rate **paired with** slugging ratio (neither means anything alone)."*

Worked example, on the firm's own admissible cost preset. `POLYMARKET` sets `half_spread_bps = 100.0` [measured] — a 1¢ spread on a 50¢ contract, round trip 200 bps of notional, i.e. **1.0¢ per round trip on a 50¢ contract**. For a strategy winning 71.5% of the time to be net positive it needs:

`0.715·W − 0.285·L > 1.0¢`

If wins and losses are symmetric at magnitude `m`, this requires `0.43·m > 1.0¢`, i.e. **`m > 2.3¢` per trade — a 4.6% move on a 50¢ contract, captured systematically.** If the strategy is instead capturing 1¢ moves, it loses money at a 71.5% win rate. **A high win rate on a mean-reverting convergence trade is the signature of a strategy that wins small and loses big**, which is exactly the shape a hit rate conceals.

**The finding is not about the number. It is that this family has been carried in the firm's institutional memory on a statistic the Charter says is meaningless alone**, and that no document produced this sprint has paired it with a slugging ratio or an expectancy. **Nobody, including this firm, currently knows the sign of this strategy's expectancy.** That is the actual state of knowledge and it should be written that way in the pre-registration.

### B.2.4 Resolution risk cannot be charged

Proposed I-021, part 2. The Polymarket leg carries adverse-resolution and dispute risk with a fat left tail. The reference-asset leg does not hedge it — the reference asset does not care how UMA votes. `CostModel` cannot express it, hand-rolled costs are prohibited, and therefore **the paper book will systematically over-report this family's net by an unmeasured amount whose sign is known.**

This is not fatal — it is a required addition to the cost library, approved by the Principal per `CLAUDE.md`. It **is** fatal to any Gate 1 submission made before the addition exists, and it should be a Gate 0 condition.

---

## B.3 The already-arbitraged case — and the dilemma that I think decides this family

### B.3.1 "Nobody has looked" is not merely wrong here; it is close to the opposite of the truth

Who is watching a public prediction market against a public reference asset:

1. **Cross-venue prediction-market arbitrageurs** (Polymarket vs. Kalshi vs. bookmakers), who by construction run the lowest-latency monitoring of exactly these price series and already hold the infrastructure.
2. **Crypto market makers.** The venue settles USDC on Polygon. The firms that make markets in crypto perps are the natural liquidity providers, and they run cross-venue relative value as their core business.
3. **On-chain searchers.** [inferred, and this is the point that should worry the sponsor most] **Every Polymarket order and fill is on a public blockchain, timestamped, permanently, for free.** This is the most transparent order flow of any venue in Part III — more transparent than equities, where the firm has no order book at all. A persistent, mechanically detectable lead-lag on a venue whose complete history is a public ledger, in a market where searchers compete for sub-block-time inefficiencies as a business, requires an affirmative explanation for its survival. **"It has not been looked at" is not available as that explanation.**
4. **The academic literature.** Prediction-market/asset lead-lag is a studied question with public results. Under Ruling 002 R4(b) this family is **presumptively an edge derived from published research** carrying the 50% haircut unless the sponsor argues otherwise at Gate 0 and Validation accepts. [inferred] I expect that argument to fail, and the pod should plan on the haircut rather than on winning the exemption.

### B.3.2 The dilemma — and I believe this is the strongest objection to the family as an *investment*

The sponsor's best persistence argument is **capacity**: the lag survives because the venue is too small to be worth a serious firm's time. A few thousand dollars of edge per contract does not pay for a desk.

**That argument is true, and it is self-defeating for this firm.**

> Charter §4.4 requires **capacity ≥ 10× the intended initial allocation at target net Sharpe.** Pod B's allocation is **USD 2,000,000** [cited — Charter §3.1]. Gate 1 therefore requires the strategy to demonstrate **USD 20,000,000 of capacity.**
>
> **If the effect persists because the venue is too small to attract arbitrage, it cannot possibly demonstrate $20M of capacity. The single best reason to believe the edge is real is the same fact that makes it inadmissible.**

There are exactly three escapes, and the pre-registration must name one and defend it:

| Escape | Mechanism | Checkable? | Decay risk |
|---|---|---|---|
| **(a) Regulatory segmentation** | US-person access restrictions historically excluded a large pool of sophisticated capital from the venue | Yes — the restriction's status is a public, datable fact | **High and active.** This is unwinding. An edge whose mechanism is a regulatory barrier has a decay date set by regulators, not by the firm |
| **(b) Settlement friction** | Requiring USDC on Polygon deters institutions with mandate or custody constraints | Partly | Moderate — falls as infrastructure matures |
| **(c) Participation segmentation** | Event-market retail flow is structurally not relative-value flow | Hard to measure directly; inferable from flow composition | Low, but this argument does **not** explain why professionals do not take the other side |

**(c) is the only mechanism that supports a durable edge, and it is the only one that does not explain the absence of arbitrage.** (a) and (b) explain the absence of arbitrage but come with decay dates. **The pre-registration must pick one, and each choice carries a different and much shorter honest horizon than a Gate 1 "validated edge" implies.** If the answer is (a), the correct product is not a validated edge — it is a trade with an expiry date, and the firm should say so.

---

## B.4 The cheapest test that would most efficiently kill the thesis

Two tests, in strict order. The first is nearly free and kills *eligibility*; the second is the kill test proper and kills *the thesis*.

### Gate check (cost: a fraction of one Sonnet unit) — the T4 measurability query

**Run step 1 of the data spec's own §7, and nothing else.** Query the Polymarket public API and its documentation for one thing: **are historical order-book snapshots retrievable, or only the live book?**

- **If no:** T4 is unmeasurable → depth at intended size is unmeasurable → the Charter §4.4 **capacity** criterion is unevaluable → INSUFFICIENT-DATA → **Gate 1 is unreachable for this family regardless of every other result.** The family is ADMITTED-AS-EXPLORATORY at most, and the firm has learned that for the price of a documentation read, before ingesting a single row.
- **If yes:** proceed to the kill test.

This does not kill the thesis. It kills the *investment case*, which is the more expensive thing to discover late. It is strictly prior to everything else and costs almost nothing. **Run it first. It is already step 1 of Seat 9's accepted procedure; it simply has not been recognised as a decision point.**

### The kill test (cost: 1 Sonnet unit, post-ingest) — the clock-aligned lead-lag cross-correlation

**Specification, concrete enough for Pod B to execute without further design work:**

| Element | Specification |
|---|---|
| **Universe** | The **single** densest Polymarket contract cluster by traded notional over the available history — one underlying event, whichever it is. Not a panel. Not stratified. One cluster. |
| **Reference asset** | The one asset the pod names in advance as the economically-paired instrument. Named **before** the run, in writing. |
| **Alignment** | Both series resampled to a common grid (5-minute bars recommended) in **UTC**, via `pit_price_panel` per A4. Reference-asset bars **outside its tradable session are dropped, not forward-filled** — forward-filling is what manufactures the artifact in §B.1.2. |
| **Statistic** | Cross-correlation of returns, `ρ(k)`, for `k ∈ [−12, +12]` bars (±60 minutes). One number per lag. **This is a descriptive statistic, not a strategy search** — it selects nothing from a menu, so it is honestly registered as **`N = 1`** in the family. |
| **Registration** | Opened through `TrialRegistry.open_hypothesis` and run through `castellan.run_backtest` per A2, in the forward-lag family, with `N_inherited` already seeded per §B.1.1. |
| **Decision rule — pre-registered before the run, not after** | **KILL** if any of: (i) `argmax_k ρ(k) ≤ 0` — the reference asset leads or the venues are contemporaneous, so the asserted direction does not exist; (ii) `argmax_k ρ(k) ≥ +12` — the "lag" is a session-boundary artifact, not microstructure; (iii) the implied per-trade capture at the peak lag is **< 2.0¢ on a 50¢-equivalent contract**, i.e. below the round-trip cost of the `POLYMARKET` preset (§B.2.3). |

**Why this is the cheapest kill and not merely a cheap test.** It delivers, in one run, the three independent ways the thesis dies — **wrong sign, wrong duration, insufficient magnitude** — and it requires no stratification table, no T1–T7 screening, no effective-`N` computation, no holdout, and no Gate machinery, because a kill test does not need to be Gate-admissible to kill. Everything expensive in the data spec exists to make a *positive* result trustworthy. **None of it is needed to make a negative result decisive.** If `ρ(k)` peaks at or before zero on the densest cluster the venue has ever had, no amount of screening rescues the family.

---

## B.5 The binding kill condition

Per Charter §4.4 (*"Red-Team Memo — present, with a binding named kill condition accepted by the sponsor"*) and Seat 5's mandate. **Written to resist reinterpretation.**

> ### KC-001 — forward-lag family
>
> **Sponsor:** the Principal, via PM Pod B. **Accepted by the sponsor in writing before any capital — paper or real — is allocated to this family.**
>
> **Observation date: 2026-10-31**, being 95 days after the pre-registration seal `C = 2026-07-28`. The date is fixed and does not move with the sprint calendar, the ingest schedule, or the harness.
>
> **On that date, Validation computes — from `book/registry.db` and `book/pit.db` alone, on the frozen pre-registration, over the forward window `[2026-07-28, 2026-10-31]`:**
>
> **(i)** realized **net expectancy per round-trip trade**, defined as `(Σ realized P&L) ÷ (count of round-trip trades)`, in price points on the [0,1] contract scale, after the full §4.6 cost stack at **1× modelled costs** using the `POLYMARKET` preset as amended per proposed I-021; and
> **(ii)** the count of **tradable signal events** generated by the frozen specification under its own pre-registered screen.
>
> ### The family is KILLED — registry marked TERMINATED, no further trials, no Gate 1 submission ever — if EITHER:
> ### (a) net expectancy ≤ 0; OR
> ### (b) fewer than 30 tradable signal events occurred in the window.
>
> **Clause (b) is not a technicality and must not be waived as one.** It kills on *insufficient signal*, which is the outcome nobody plans for and which otherwise becomes "wait a little longer" indefinitely. A family that cannot generate 30 events in 95 days on its own chosen venue cannot generate a testable rate on any horizon this firm can wait for, and its capacity is thereby also answered (§B.3.2).
>
> **Anti-reinterpretation clauses, binding:**
> 1. **No re-parameterisation.** Expectancy is computed on the sealed specification. Not a tuned variant, not a subset, not "the version we would have run."
> 2. **No post-`C` exclusions.** Any regime filter, date exclusion, contract exclusion or universe restriction not present in the sealed pre-registration is inadmissible in this computation. This clause exists specifically because the prior work carried **1 regime exclusion** [cited — I-002].
> 3. **No restatement as continuation.** A hypothesis restated after 2026-10-31 is a **new family**, opened with `N_inherited` ≥ the killed family's final `n_trials` plus its own `N_inherited`. It does not inherit the killed family's schedule, its allocation, or its narrative.
> 4. **Kill is automatic on the date.** It requires no meeting, no vote, and no CIO concurrence. **It is not appealable to the CIO.** Only the Principal may reverse it, in writing; the reversal is logged in `logs/DECISION_RECORD.md` as an Appendix-B-#4 override with its reason stated on the face of the record and reported in the next Monthly Letter.
> 5. **Silence is a kill.** If the computation is not performed on 2026-10-31 — for any reason, including that ingest never happened or the harness was not ready — **the family is killed by default.** A kill condition that can be defeated by not running it is not a kill condition. This clause is deliberate and I expect it to be the one someone tries to soften.

**Condition precedent, separately binding:** the T4 measurability query of §B.4 is answered in writing **by sprint close, 2026-08-11**. If unanswered by that date, the family is ADMITTED-AS-EXPLORATORY only, and remains so until it is answered.

---

## B.6 What I am NOT objecting to — anti-theatre rule, stated plainly

Charter Seat 5 and my own standing rules require me to say where I could not build a serious objection, in one line each, rather than manufacture one. Six items.

1. **Validation Ruling 002's rejection of the training-cutoff derivation rule.** I checked reason (1) arithmetically — a training cutoff is in the past by construction, therefore yields a *shorter* holdout than `C` = today, therefore is weakly dominated by the forward-holdout option on every axis. It is correct and I have nothing.
2. **The Principal's D-006 pre-registration freeze rider.** It converts "unseen data" into "unseen data tested against a fixed prediction," which is the property that makes waiting worth anything. I have no objection.
3. **P-1 itself, as corrected.** Once Validation struck "strictly stronger" and specified the compensating controls (Ruling 001 §2.3), I can construct no serious objection to the ingest ceiling.
4. **The refusal to rewrite git history over I-013.** Correct, and the reasoning — that rewriting a book of record to hide an error is worse than the error — is right.
5. **Seat 9's disclosure conduct.** It escalated rather than edited, reported 63/64 rather than rounding to green, flagged seven interpretive decisions unprompted, volunteered I-013 against its own interest, and in DATA-IMPL-002 §13 hunted for and found a second instance of its own defect pattern. I have no objection to any of it and I record it because the incentive the firm creates should not be "disclose less."
6. **The economic mechanism of forward-lag itself.** I attack its measurement, its capturability, its capacity, and its persistence — but the mechanism in §B.0 is coherent, it names who is on the other side and why they accept the loss, and it satisfies Gate 0(1) on its face. **I cannot construct a serious argument that the mechanism is incoherent, and I am not going to pretend to.**

---

## B.7 What would change my mind

| # | On what | What would change it |
|---|---|---|
| 1 | The `N_inherited` objection (§B.1.1) — my strongest | A documented, reconstructable record of the prior search — an actual parameter log, not a recollection — showing the true search was small. Or a demonstration that the hypothesis was fixed *before* any parameter was tried. Either makes `N = 0` honest and my objection collapses |
| 2 | The capacity dilemma (§B.3.2) | Evidence of ≥ $20M realistic capacity — measured resting depth, not extrapolated volume. This would simultaneously answer the dilemma **and** re-open B.3.1: at that size, the absence of arbitrage becomes much harder to explain, and I would want the persistence argument re-run |
| 3 | The clock-alignment objection (§B.1.2) | A pre-registration that specifies the reference asset's tradable session in UTC and drops cross-session signals, with cross-session and intra-session results reported separately. Fully addressable by design |
| 4 | The survivorship objection (§B.1.4) | An archival on-chain universe enumeration with a measured API-listing survivorship rate |
| 5 | The T3 factor-of-two (§B.2.2) | An argument that half-spread is the correct *round-trip* quantity on this venue. I do not believe one exists, but I would read it |
| 6 | The already-arbitraged case (§B.3) | Measured evidence of segmented participation — e.g. flow composition showing the marginal Polymarket participant is not running relative value. This is the strongest available rebuttal and it is measurable on-chain |
| 7 | Memo A's compute objection (§A.2/A.4) | A written statement of why the thinnest data surface in Part III is the correct first target, which §3.5 requires and which does not currently exist. If the reason is good, the objection dissolves |
| 8 | The Monthly Letter framing (§A.1) | Nothing. The counterfactual is false as a matter of arithmetic — no unit was allocated to producing a Sharpe. This one does not move |

---

## Ranking — how much each objection should move the decision

| Rank | Objection | Should it move the decision? |
|---:|---|---|
| 1 | **§B.1.1 `N_inherited`** — the denominator is wrong by ~3 orders of magnitude and no existing control touches it | **Yes. Blocking. I would act on this myself.** Family is exploratory-only until a defended floor is stated |
| 2 | **§B.3.2 the capacity dilemma** — the best reason to believe the edge is the reason it fails §4.4 | **Yes. Decides whether this family can ever be an investment**, independent of whether it is real |
| 3 | **§B.2.1 T4 unmeasurable ⇒ capacity unevaluable ⇒ Gate 1 unreachable** | **Yes, and it is nearly free to resolve.** Run the query this week |
| 4 | **§B.1.2 cross-venue clock (I-022)** | **Yes.** Design-fixable, but if unfixed it produces a large false positive |
| 5 | **§A.1 the Monthly Letter framing** | **Yes.** Costs no compute to fix; the honest sentence is drafted above |
| 6 | **§B.1.4 survivorship (Gate 0(5) fails today)** | **Yes.** Blocking at Gate 0 as written |
| 7 | **§A.2 Opus burn 40% at 7% elapsed, contingency spent** | **Yes.** Schedule risk, quantified, no reserve behind it |
| 8 | **§B.2.2 T3 factor of two** | Yes, but cheap — one constant, moved before measurement |
| 9 | **§A.4 §3.5 drift** | Yes — but the remedy may be a written justification rather than a reallocation |
| 10 | **§B.2.3 win rate vs. slugging** | Corrects the firm's institutional memory; does not by itself change a decision |
| 11 | **§B.1.3 stratification blind to underlying event** | Yes — one added axis. Partly mitigated by `N_eff` already |
| 12 | **§A.5 three pods** | **I would not act on this myself at day 1 of 14.** Labelled as such. Re-test at sprint close |
| 13 | **§A.6 I-020 over-budget PASS** | Real defect, but it cannot fire before a family exists. Fix before Gate 0 |

---

*Devil's Advocate · Castellan Capital · 2026-07-28*
*This memo is a mandatory component of the forward-lag family's Gate 1 submission. It is not suppressible by the CIO or the Director of Research. My second Sprint 1 Opus unit is reserved for the Gate 1 Red-Team Memo and is not spent.*
