# DECISION RECORD — Castellan Capital

Every firm decision, its dissent, its conditions, its review date, its falsifier.
Append-only. Newest at the bottom.

---

## D-001 · 2026-07-28 · Firm activation (Charter Part IX)

**Decision:** Castellan Capital activated under Charter v1.1 (Amendments A1–A4).
Paper book opened at USD 10,000,000. Trial registry initialized empty.
Nine seats registered as invocable subagents.

**Verdict:** ACTIVATED — cold start, no operating continuity recovered.

**State at activation:**

| Item | State |
|---|---|
| `book/book.db` | cash 10,000,000.00 · 0 positions · reconcile clean · 0 orders / 0 executions / 0 trades |
| `book/registry.db` | 0 hypothesis families · 0 trials · 0 gate verdicts |
| `book/vaults/` | empty — no holdout locked |
| `book/pit.db` | **does not exist** — no price data ingested |
| `harness` | installed editable · 30/30 tests pass |
| `research/` `logs/` | empty prior to this record |

**Named dissent:** none — activation is mechanical, not a judgment call.

**Conditions attached:** no hypothesis may enter Gate 0 until the PIT store exists
and a holdout is locked for the relevant dataset. See I-001.

**Review date:** first Weekly Research Review after the Principal approves an agenda.

---

## D-002 · 2026-07-28 · Seat registration path

**Decision:** `.claude/agents` symlinked to `agents/`, making the nine seat
definitions discoverable by the Agent tool. `agents/` remains the single source
of truth and stays under version control.

**Rationale:** the seat definitions were present in the repo but not on the
discovery path. The roster existed as prose and could not be delegated to.

**Open condition:** Principal to confirm the seats appear under `/agents`. If
symlink resolution fails, fall back to copied files and accept the drift risk.

**CLOSED 2026-07-28.** Principal confirmed nine seats visible. CIO verification
against the Charter roster: 9/9 present, all model assignments match (Opus ×4,
Sonnet ×4, Haiku ×1), filenames match `name:` frontmatter, no unexpected seats,
no missing `tools:` line. Symlink retained; a proposed inversion of the symlink
direction was rejected by the Principal as unnecessary.

---

## D-003 · 2026-07-28 · Principal amendment P-1 — holdout ingest ceiling

**Decision (Principal):** Data & Infrastructure ingests only up to each dataset's
holdout cutoff. Holdout periods are fetched and locked at Gate 1, by Validation,
with the Principal's passphrase supplied at that moment and never stored.

**Effect.** Replaces the Charter's fetch-then-encrypt holdout with an air gap.
~~Strictly stronger: holdout plaintext never enters the ingest path, and because the
fetch happens at Gate 1 date `G` rather than pre-registration date `C`, the window
`[C, G]` contains data that did not exist when the hypothesis was written —
unseeable rather than merely unseen.~~

> **CORRECTION, 2026-07-28, on Validation Ruling 001 §2.1. The original wording
> above is struck rather than deleted; the record is not rewritten.**
>
> **"Strictly stronger" was wrong and was the CIO's characterization, not the
> Principal's.** Validation ruled P-1 a *different* control with a different threat
> model, not a dominating one:
>
> - **Stronger** on leak surface — holdout plaintext never enters the ingest path,
>   and the ingest boundary becomes cheaply auditable via `max(event_time)` vs `C`.
> - **Weaker** on (W1) *evidentiary permanence* — the old ciphertext sealed at `C`
>   **was** the evidence; under P-1 no artifact exists between `C` and `G`, so a
>   vendor restatement or re-resolution in the interim silently changes the Gate-1
>   fetch and the discrepancy is undetectable. Tamper-evident payload → tamper-evident
>   promise. (W2) *availability* — the holdout now depends on a live third party at
>   the exact moment the family is judged. (W3) *split enforcement* — the split moves
>   from code into a query parameter, so over-ingest goes from **impossible** to
>   **silent and plausible**.
> - **Conditional, not general,** on the headline "unseeable" property: it holds only
>   for the sub-window of `[C, G]` postdating pre-registration. If `C` is pinned in
>   the past the holdout is entirely historical and freely fetchable, and the property
>   is simply false for it. Per Ruling 3, thin Polymarket history pushes toward pinning
>   `C` early — so **the firm's first hypothesis will very likely run under a holdout
>   to which P-1's headline protection does not apply at all.**
>
> The CIO's further claim that "under the old regime encryption was the barrier" was
> also rejected. Encryption never protected the information, only the vault's copy of
> it; the underlying series is free and public in both regimes. What P-1 actually
> removes is the property that **the safe path is the default path** — which is why
> Validation moved enforcement into `PITStore` rather than the fetch call.
>
> P-1 is **not** reversed. S1 and W3 are both obtainable; Ruling 001 §2.3 specifies how.

**Consequence requiring action — blocking.** `HoldoutVault.lock(df, passphrase)`
requires the full series in hand and `open_once()` decrypts a stored payload.
Under P-1 there is no payload at lock time. Resolution proposed: the vault seals a
**holdout specification** (dataset, source, query, pinned cutoff `C`) with its hash
in the registry; at Gate 1 the passphrase authorizes the **fetch** rather than a
decrypt, and single-use semantics apply to that fetch. **Validation rules — it is
their vault under Seat 3.** No ingest until they do.

**Open question routed to Validation, not the Principal:** whether `C` is pinned as
an immutable calendar date at pre-registration or recomputed at Gate 1. It must be
the former or the in-sample set silently grows. CIO recommendation: pin it.

**Named dissent:** none recorded. The amendment tightens; the Charter's asymmetry
(brakes unilateral, accelerators collective) means a tightening needs no defence.

**Review date:** first Monthly Letter, 2026-08-01.

---

## D-004 · 2026-07-28 · Sprint 1 approved · compute ceiling set

**Decision (Principal):** Sprint 1 agenda approved with amendment P-1. Compute
ceiling **25 seat invocations, maximum 10 Opus, no rollover.** Opening hypothesis:
the forward-lag family only, on the terms of I-002 — the 71.5% figure is a pointer,
not a prior. No further Principal hypotheses this sprint; the CIO generates the
rest.

**Decision (Principal):** reduced meeting schedule approved in structure, but **no
scheduled tasks created.** Friday Research Review and Monday Risk sessions opened
manually through Sprint 1. Automation revisited at the first Monthly Letter.

**CIO note on the budget.** The four ritual sessions inside this sprint (2× Friday
Research Review chaired by the Director of Research, 2× Monday Risk chaired by the
CRO) are Opus invocations and are counted against the ceiling, not excluded from
it. This puts Opus at exactly 10 with zero headroom. Pre-committed cut if it
overruns: the **second Monday Risk meeting**, on the grounds that an empty book
generates no risk content. Recorded so the cut is a decision, not an omission.

**Falsifier for the agenda itself:** if Data & Infra's first deliverable shows
usable Polymarket history under four years, the forward-lag family cannot reach
Gate 1 at any Sharpe (§4.4 length requirement) and Sprint 1's Pod B allocation is
redirected the same day. See I-004.

**Review date:** 2026-08-11, sprint close.

---

## D-005 · 2026-07-28 · Validation Ruling 002 — `C` placement under the model-prior threat model

**Decision (Validation, binding on Seats 1, 2, 6–10; appealable only to the
Principal in writing):** **REJECT** the Principal's derivation rule — `C` will not
be pinned at any training cutoff — while **ADOPTING the threat model in full**, with
four binding replacements (R1–R4).

**Three independently sufficient reasons for the rejection**, per Ruling 002 §3.3:

1. **Arithmetic, and decisive.** A cutoff is in the past by construction. With the
   only sourceable cutoff (CIO seat, May 2026) the proposal yields a **two-month**
   holdout today. It is therefore *not* a middle option between "holdout now" and
   "wait twelve months" — it is `C` = today, minus two months of in-sample, plus an
   unverifiable parameter, buying roughly two months of schedule. **Weakly dominated
   by the forward-holdout option on every axis.**
2. A training cutoff is not a real knowledge boundary — non-monotone in both
   directions.
3. It targets *price memorization*, while the thing that actually leaks into
   hypothesis generation is *regime knowledge*. The firm already holds a **measured**
   instance of exactly that in I-002's "1 regime exclusion," arriving through the
   human channel the proposal omitted.

**What the retrieval hole actually established.** Not the rejection — three other
reasons carried that. It established that the firm was being asked to build an
unenforceable control against the smaller channel while an enforceable one against
the larger channel sat unbuilt. Filed as I-012.

**Consequences filed:** I-011 (HIGH, `N`-deflation by model priors), I-012 (MEDIUM,
retrieval channel), I-009 severity retained. Ruling 001 §2.4 amended by Validation
**against its own prior text** — "procedurally protected only" retracted as too
generous.

**Named dissent:** Validation dissents from the Principal on the operative question.
Recorded per Charter §6.4; the dissent is the ruling.

**Principal-position record after two rulings — 2 agreed / 2 rejected.** `n = 4`,
statistically uninformative, recorded so the base rate is built as it happens rather
than reconstructed later. I-003 stands.

**Open decision, still the Principal's:** the `C`-placement / sprint-schedule call.
Validation's recommendation is that the live choice is **A** (early `C`, holdout now)
versus **B/D** (`C` = today, forward holdout), and that Option **D** — family runs
immediately as ADMITTED-AS-EXPLORATORY with trials accruing honestly, Gate 1 claimed
when the forward window matures — gives A's schedule with B's guarantee. Its stated
cost is the ability to say "validated" in 2026.

**CLOSED by D-006, 2026-07-28.** Principal selected Option D.

**Review date:** first Monthly Letter, 2026-08-01.

---

## D-006 · 2026-07-28 · Principal takes the `C`-placement decision — Option D

**Decision (Principal):** **Option D approved.** `C` = today. Forward holdout. The
forward-lag family enters as **ADMITTED-AS-EXPLORATORY immediately**, trials
accruing honestly from the first run, Gate 1 claimable when the forward window
matures.

**Principal's rider — the pre-registration freeze:** the **full pre-registration is
frozen before `C`**, so the forward window is unseeable relative to a **fixed
hypothesis**.

**Why the rider matters, stated plainly.** Option D without it is weaker than it
looks. If the pre-registration could still be edited after `C`, a researcher could
tune the hypothesis while the forward window accrued — and the window would be
out-of-sample against a *moving* claim, which is not out-of-sample at all. The rider
converts "unseen data" into "unseen data tested against a fixed prediction," which
is the property that makes a forward holdout worth waiting for.

**CIO finding on implementability** [measured]: `TrialRegistry.open_hypothesis`
documents itself as idempotent on family with fields immutable after creation. **But
nothing hashes the pre-registration.** There is no `prereg_sha256`, no sealing
event, and no field binding a Validation Report to the exact pre-registration text
it was evaluated against. Immutability is *asserted by the API*, not *evidenced* — a
direct SQLite write would go undetected.

This is exactly the distinction Validation drew in Ruling 001 §2.1 between a
tamper-evident **payload** and a tamper-evident **promise**, and the holdout spec
already gets the stronger treatment (A1/A4/E3: sha256 sealed to the registry,
embedded in the report). Under this rider the pre-registration becomes equally
load-bearing and has none of it. **Routed to Validation with the acceptance review;
not resolved by the CIO.**

**Interaction with I-011, which the freeze does not fix.** Freezing binds the
hypothesis from `C` onward. It does nothing about the search embedded in the
researcher *before* the freeze — model priors contaminate hypothesis *formation*,
upstream of any freeze. Option D plus the rider closes the forward channel; I-011
remains open and untouched by it.

**Further Principal decisions, same instruction:**
- Ruling 002's four replacements **R1–R4 accepted as binding.**
- **I-011 goes in the first Monthly Letter (2026-08-01) as the sprint's most
  important finding.**
- **Fourth Validation Opus unit approved**, funded by the pre-committed cut: the
  **second Monday Risk meeting is dropped**. Opus stays exactly at the 10-unit
  ceiling — Validation 4, Director of Research 3, Devil's Advocate 2, CRO 1.
- I-013 correction **accepted as handled** — append, never rewrite. Explicit-path
  staging binding on the CIO.

**Named dissent:** none. Validation recommended D and the Principal selected D; the
firm's independent line and its Principal agree here, which is recorded as such
rather than presented as vindication.

**Review date:** sprint close, 2026-08-11.

---

## D-007 · 2026-07-28 · Principal clarifies the definition of `C` · escalated under house rule 7

**Clarification (Principal, made explicitly under Charter house rule 7 — escalate
uncertainty, do not resolve it silently):**

> **`C` is defined as the pre-registration seal date, not the D-006 decision date.
> The forward window is measured from the freeze, which is what P7 protects. Pod B
> seals promptly after the red-team lands.**

**Why this is a substantive clarification and not a formality.** D-006 said "`C` =
today," which reads as the decision date, 2026-07-28. Under that reading a
pre-registration sealed three days later would start its forward window three days
*before* the hypothesis was frozen — three days of data the researcher could have
seen while the hypothesis was still mutable. The Principal's definition removes
that window entirely: the forward period begins exactly where the hypothesis stops
moving. Acceptance item **P7** already enforces the pairing by failing Gate 1 if the
seal postdates `C` at UTC day granularity, so under this definition seal date and
`C` are the same calendar day by construction.

**Immediate operational consequence, carried into the ingest dispatch.** `C` is
therefore **not yet fixed** — Pod B has not sealed. Every `C` that can now be sealed
is on or after today, so Data & Infrastructure was instructed to ingest **strictly
no later than `2026-07-28T23:59:59Z`**, which is conservative against any future
`C` and provably cannot leak.

**Named hazard on that dispatch:** no ceiling is in force, because a ceiling is
derived from a sealed spec and no spec is sealed. Over-ingesting past an unset `C`
is the one irreversible mistake available in the task. Seat 9 was directed to make
the store enforce the bound if it can carry a provisional ceiling without a sealed
spec, and to report explicitly if it cannot — that absence would be a finding about
the ceiling's design, not a footnote.

---

## D-008 · 2026-07-28 · Sprint 1 sequencing — Option C

**Decision (Principal):** **Option C.** The Devil's Advocate red-teams the agenda
and the forward-lag design **now, before any pre-registration**; Data &
Infrastructure ingests crypto and ETF panels to cutoff in parallel.

**What this corrects.** The approved agenda specified that the Devil's Advocate
red-team the agenda *before* execution. The CIO ran four Validation and Data &
Infrastructure dispatches first and left the seat idle — self-reported to the
Principal as Charter Appendix B #5 arriving as neglect rather than as ceremony.
Option C restores the intended order for the part that still matters: the
forward-lag family is attacked while its design is still malleable, which is when a
red-team memo is worth most.

**Principal's disposition of two open items:**
- The CIO's Devil's-Advocate-neglect self-report is **noted and closed as
  corrected.**
- The **R4(a)/(b) gap stays OPEN on the Issue Log until wired** — schema and fields
  exist, no computation is attached, and it is **not counted as delivered.**

**Allocation:** Devil's Advocate spends 1 of its 2 Opus units here; the second is
reserved for the mandatory Red-Team Memo at Gate 1 (Charter Seat 5 — a packet
without one is deferred, not heard).

**Review date:** sprint close, 2026-08-11.

---

## D-009 · 2026-07-28 · Principal's disposition of Red-Team 001

**A — Order-book availability probe: APPROVED, run this week.** Dispatched to Data &
Infrastructure. Step 1 of Seat 9's own accepted procedure, promoted to a standalone
task because the Devil's Advocate identified it as strictly prior and nearly free and
nobody had recognised it as a decision point. A negative result makes Charter §4.4's
capacity criterion **unevaluable** — INSUFFICIENT-DATA, never PASS — and Gate 1
unreachable before a row is ingested, potentially mooting I-004.

**B — `N_inherited` DECLARED at the grid upper bound.**

> `5⁵ = 3,125` (five tuned parameters × five values, per I-002) **× regime-candidate
> factor 10** = **`N_inherited` = 31,250.** The registry opens **seeded at that
> floor**, not zero.

The Principal fixed the grid term and delegated the regime-candidate factor to the
CIO with the single instruction that it be honest. **CIO's factor: 10** [inferred] —
the menu of conventional crypto and event-market regime boundaries from which the
prior work's single exclusion was plausibly selected: COVID, the 2021 bull,
May-2021, LUNA/UST, FTX, the 2022 bear, election cycles, funding-sign regimes,
post-ETF-approval, early-venue illiquidity.

**Readings considered and why 10 was chosen.** Choosing one of K candidates gives a
factor of K. The any-subset reading gives 2^K — at K=10 that is ≈3.2M, **rejected as
overstating realistic human search**. The CIO notes explicitly that erring *low* here
is the sycophantic direction and erring *high* is the conservative one, and that the
factor was not selected to make the family viable.

**Calibration** [measured]: √(2·ln 31,250) ≈ **4.55·σ_SR** loose bound, against
Charter §4.1's table value of 3.86·σ_SR at N = 10,000. This is a punishing floor and
is meant to be.

**Revision rule:** downward revision requires **reconstructed evidence of the actual
candidates considered** — not argument — and every revision is logged.

**Companion question routed to Validation with the same independence instrumentation
as Rulings 001 and 002** (the Principal's direction): *does `N_inherited` deflate the
forward window, given a sealed pre-registration — or does the forward test count from
`C` as pre-registered trials only?* The Principal's own assessment, which the CIO
shares: **the family's admissibility likely turns on this.** The standard argument is
that a single pre-specified confirmatory test on genuinely unseen data is `N = 1` for
that test, and that multiple-testing correction attaches to the in-sample selection
rather than to the confirmatory test that follows. Validation rules; it is folded
into the fourth unit alongside Gate 0 intake, so no additional Opus is required.

**C — KC-001 SIGNED AS WRITTEN, silence-kill included.** The sponsor is the
Principal. Reproduced verbatim into the pre-registration. The Devil's Advocate
predicted the silence clause would be the one someone tried to soften; it has not
been softened and will not be.

**Principal's additions:**

1. **Pod B's pre-registration states intended initial allocation honestly — order
   tens of thousands, not $2M.** This **dissolves the persistence dilemma**: §4.4
   requires capacity ≥ 10× *intended initial allocation*, so the Devil's Advocate's
   $20M figure assumed the full pod. At ~$50k the requirement is ~$500k, and a venue
   can be simultaneously too small for a serious firm and large enough to clear that.
   **The cost, which the pre-registration must state rather than discover later:** a
   $50k strategy in a $10M book is ~0.5% of capital, so **even an excellent Sharpe
   there is close to immaterial to firm P&L.** The family survives on admissibility
   and loses on materiality. That trade is now explicit.
2. **I-024 named as a binding confound** in the pre-registration — bar alignment
   specified, out-of-session reference bars **dropped not forward-filled**, and a
   stated method for distinguishing a session-gap artifact from a genuine lag. A
   design that cannot distinguish them is not admissible.
3. **I-023's fix goes on the Sprint 2 harness list, Validation owning the spec:**
   price-dependent binary-contract costs, plus a resolution-risk field on
   `CostModel`. Until then no Polymarket net-P&L claim stands.
4. **I-025 acknowledged and acted on:** the Sprint 2 agenda **must contain
   Director-originated hypotheses**, and the **origin-ratio metric reports in every
   Monthly Letter starting Saturday 2026-08-01.** Today's value: **4 of 4 = 100%
   Principal-originated.**

**Sequencing decision (CIO, operational).** The pre-registration is drafted **now**,
in parallel with the probe, and sealed after Validation's Gate 0 intake. Rationale:
`C` is the seal date (D-007), so every day of delay is a day the forward window does
not accrue and KC-001's clock does not start. The probe and the companion ruling
determine whether Gate 1 is *reachable*; neither changes what the hypothesis *is*.
Sealing early is therefore strictly better, provided nothing is added after — which
P7 enforces.

**Review date:** sprint close, 2026-08-11.

---

## D-010 · 2026-07-28 · Forward-lag shelved; firm redirects to a Director-originated family

**1. Director of Research's verdict ACCEPTED (Principal).** Forward-lag is
**ADMITTED-AS-EXPLORATORY**. The kill test (falsifier F-001) is funded at **2–3 of
Pod B's four Sonnet units**. **The full DATA-SPEC 13-step programme and every ±50%
grid are cancelled** — that apparatus exists to make a *positive* result trustworthy,
and a positive result cannot clear Gate 1 for this family.

**Principal's entry for the record, and it is a sharp one:** the DoR's MinBTL
fatality argument (17.06 years at N = 31,250; net Sharpe ≥ 2.07 to satisfy MinBTL at
the four-year floor) **presupposes that inherited `N` governs the length criterion —
which is precisely the companion question still before Validation.** The verdict
stands on the **independent** grounds (censored span of 3.66–3.82 years, contested
capacity evaluability, ~0.5%-of-book materiality), and **Validation's ruling proceeds
as scoped, because it governs all future inherited-`N` families** regardless of a
family being shelved. Recorded so the argument is not later cited as having settled a
question it assumed.

**2. Sealing sequence (Principal).** Land the `n_inherited` fix **first** — one Sonnet
unit, with **Validation's negative tests authored before implementation** (the I-021
remedy: the implementing seat stops authoring the tests that judge its own work) —
**then seal same-day.** **KC-001's 2026-10-31 deadline stands absolute**; a slipped
seal shortens the forward window rather than moving the date.

**3. Redirect APPROVED (Principal).** Crypto perpetual funding/basis pre-registers
**this sprint, under the Director's sponsorship** — the firm's first
Director-originated hypothesis. 6.5 years of BTC/ETH/SOL spot and 8h funding, zero
gaps, already in `book/pit.db`; `N_inherited` honestly 0.

**Principal's rider, which is the `N_inherited` lesson applied prospectively:**

> **Regime-conditioning choices are declared at Gate 0 together with the menu they
> were chosen from.**

Forward-lag is crippled because one regime exclusion was made after the fact from an
unrecorded menu, forcing the firm to reconstruct a factor of 10 by guesswork. Any
conditioning in PREREG-002 must declare the choice, **enumerate the full candidate
menu**, and yield a countable honest `N` contribution. Conditioning on nothing is a
strong position and must be stated as such. **An undeclared menu is a defect.**

**4. Origin ratio reports Saturday at its current value, unsoftened** — **4 of 4 =
100% Principal-originated.** PREREG-002 changes the ratio prospectively; it does not
retouch the number being reported.

**CIO correction to the record.** The CIO reported Opus 6/10 and Sonnet 7/14 in the
preceding update. Both were wrong. Recount from the dispatch ledger: **Opus 5 used**
(Validation ×3, Devil's Advocate ×1, Director of Research ×1); **Sonnet 5 used**
(Data & Infra ×5). Against a binding ceiling, an over-reported spend is not a
harmless slip — it would have led the CIO to refuse work the firm could afford.

**Review date:** sprint close, 2026-08-11.

---

## D-011 · 2026-07-29 · Principal directive — nine dispositions

**1 · Reallocation APPROVED.** The **CRO's Sprint 1 Opus unit moves to Validation**
to specify the I-034 cost repair. Principal's rationale, recorded: zero positions,
zero risk content, second Risk meeting already cut. **The Devil's Advocate's Gate 1
reserve is deliberately untouched.** Opus allocation stands at 10: Validation 5,
Director of Research 3, Devil's Advocate 2, CRO 0.

**2 · I-034 — design input submitted to Validation as NON-BINDING, with its conflict
declared by its author.** The Principal notes he wrote the harness and is therefore
proposing the fix to his own defect. His direction:

> Funding is a **signed asset cash flow, not a cost.** Move it out of `CostModel`
> into **engine P&L accrual** — per bar, from the realized funding series in
> `pit.db`, **signed by position**, so a short perp *receives* when funding is
> positive. The cost library keeps genuine frictions only. **Stress semantics split:**
> `scaled(m)` applies to frictions; **carry is scenario-shifted, explicitly including
> sign inversion, because doubling a receipt is not a stress.**

**"If Validation finds a better construction, its ruling governs."** The Director of
Research's refusal of the synthetic-leg workaround is **endorsed**.

**3 · KC-001 clause 3 RESTATED AND SIGNED** (I-031). The Principal, as the signing
sponsor, replaces the clause with:

> *"Any restatement of this hypothesis after the kill must register as a new family
> declaring this family as `predecessor_family`. Inherited `N` is computed solely by
> the registry's transitive summation; this clause adds no separate count."*

**One counting path, owned by the code.** All other clauses — **including the
silence-kill** — unchanged.

**4 · F-001 redesign DEFERRED, not funded.** *"The family cannot reach a gate; a
repaired falsifier for it is a well-made key to a bricked door."* The defect is to be
recorded so the debt stays visible, and **redesign is a precondition of revival** if
the span matures into admissibility.

> **CIO note on executing this:** the registry **cannot** carry the record — Gate 0
> 001 refused the seal, so no family exists in `book/registry.db` (0 hypotheses). The
> debt is therefore carried by **I-029** and by this entry, and it must be attached to
> the family at registration if forward-lag is ever revived. Recorded rather than
> silently substituted.

**Companion FUNDED (Sonnet):** recurring capture of **live Polymarket `/book`
snapshots** into the PIT store. *"Historical depth cannot be reconstructed, but it can
be accumulated prospectively — this is the only path by which T4 and quote-liveness
ever become measurable, and it should be running before, not after, the span bar
clears in October."* **Scoped as firm data infrastructure, not family research.**

**5 · H-series IMPLEMENTED NOW.** One Sonnet unit, **Validation's pre-authored
negative tests binding.** Principal's rationale: the seeded-`N` mechanism is **firm
infrastructure under C-001, not forward-lag's property** — *"shelving it because its
first customer died is the I-019 shape recurring."*

**6 · I-032 ADOPTED, with a mechanism.** C-001's conditions already force every
forward test to be logged, so **the registry maintains a firm-wide forward-test
ledger**, and the Monthly Letter carries a standing line: **cumulative Σα across all
forward tests ever run, reported as expected false positives to date.** When it
approaches 1, **the firm says so in those words.** A formal firm-level α budget is
**deferred to the Quarterly Review** as a possible Charter amendment — *"do not
improvise one."*

**7 · PREREG-002 — seal only once the I-034 repair lands green.** Sequence:
Validation specifies → Seat 9 implements against the pre-authored tests → suite green
→ M1 runs → seal. **Ruling 003's lesson stands: a delayed seal is cheaper than a
defective one.** The declared-menu construction (**`N` = 86, budget 80, 2-parameter
grid**) is **approved as drafted**. C-001's five conditions attach to its forward test
at sealing, with **statistic and α named now**.

**8 · Saturday's Monthly Letter — contents confirmed.** Throughput **0/2** with the
Devil's Advocate's honest framing; **origin ratio at its measured value**; the
**`N`=86 versus `N`=27,000 counterfactual as the sprint's central exhibit**; **I-034
reported as the harness's most consequential defect, caught before it killed a viable
family**; the forward-test ledger's first entry (**Σα = 0**); and **C-001 recorded as
founding precedent on I-011** — *the cure for unreconstructable search history is the
freeze plus forward data, not heroic `N` estimates.*

**9 · Principal's standing note, recorded verbatim because it is the firm's own
scorecard:**

> *"This sprint the firm rejected my proposal, killed the CIO's narrative, and
> defunded my flagship family — each correctly. That record is why PREREG-002's
> eventual verdict, whichever way it goes, will mean something. Maintain the ratio."*

**Review date:** sprint close, 2026-08-11.

---

## D-012 · 2026-07-29 · Principal directive — four dispositions

**1 · Failed invocations COUNT AS SPENT.** Principal: *"a ceiling where failures are
free stops binding."* The I-034 re-dispatch is funded from the **Director of
Research's final Opus unit**; **the Devil's Advocate's Gate 1 reserve remains
sealed** — protected for the third time.

Opus after this dispatch: **9 of 10 spent.** The remaining unit is the DA's Gate 1
reserve and is not available for anything else.

**2 · The I-036 stash is DISCARDED.** Principal: *"source written without its
pre-authored tests is contaminated by construction, and examining it would anchor
the re-dispatch."* Executed — `stash@{0}` dropped, unrecoverable by design.

**Rider on the H-series re-dispatch, which strengthens I-021:**

> **Tests written and run RED before any source. Ordering, not just authorship.**

I-021 established that the implementer must not author its own tests. This goes
further: Validation's authorship is insufficient — the seat must **transcribe the
tests, run them, and observe them fail** before implementing. The CIO has made the
**verbatim red output a required deliverable**, on the reasoning that without it
there is no evidence the tests ever constrained anything and the arrangement reduces
to paperwork. A case that **passes red** is to be reported as a defect in the test,
not treated as convenience.

**3 · Capture cadence AUTHORIZED and INSTALLED.** launchd agent
`capital.castellan.polymarket-book`, 900-second interval, `RunAtLoad`, logs to
`logs/capture/`.

**CIO note on execution** [measured]: the first install **failed** — the plist
pointed at `/usr/bin/python3`, which lacks numpy. Corrected to the framework
interpreter that actually carries the harness. **Verified after correction:**
`launchctl` exit code **0**, `captured 20/20 token books across 10 markets`, and the
universe self-healing as designed (`2 resolved/retired, tracked not polled`). Had
the CIO reported "installed" without checking the exit code, the firm would have
accumulated **zero** depth history while believing otherwise — the same class of
error as a green suite that tests nothing.

**Machine-sleep caveat acknowledged by the Principal.** **Migration to an always-on
VPS approved as a Sonnet task under the Principal's expenditure authority, ~$5/month**
(Charter §4 reserves money-spending and account-creation to the Principal; this is
that approval). Not yet dispatched — queued behind the two live dispatches to avoid
repeating I-036's tree contention.

**4 · Sprint 2 list — per-seat git worktree isolation.** Principal: **I-013 and I-036
are the same incident class** — agents sharing one working tree — *"and it should be
retired structurally, not procedurally."*

**CIO action: applied immediately rather than deferred.** The H-series re-dispatch is
running under `isolation: "worktree"` — its own checkout, merged by the CIO on
completion. The procedural mitigations (explicit-path staging from I-013) remain in
force as belt-and-braces, but the structural fix is live today. Retained on the
Sprint 2 list only to decide whether it becomes the **default** for every
code-modifying seat, which is a standing-policy question rather than a one-off.

**Review date:** sprint close, 2026-08-11.

---

## D-013 · 2026-07-30 · Principal directive — four dispositions

**1 · `CRYPTO_SPOT_TAKER` AUTHORIZED** under Charter §4.6 (a new cost-model preset is
a Principal reservation):

```
commission_bps = 10.0 · half_spread_bps = 2.5 · impact_y = 1.0 · periods_per_year = 365
```

**No carry fields**, per Ruling 003's deletion principle — the ruling's argument is
that a field whose correct value is always zero and whose wrong value double-counts
with the sign inverted is a lapse waiting to happen, so it should not exist.

Recorded as **conservative-pending-calibration**, with the **Devil's Advocate
explicitly free to contest it at Gate 1** — the seat's remaining sealed Opus unit is
the mechanism by which that contest can actually happen.

**Binding scope limit:** the preset covers **long** spot. **Shorting spot requires a
new preset and a new Principal decision.** Recorded because generalising a preset by
implication is exactly how a cost library stops being a control.

**2 · Ruling 003's 19 tests FUNDED** — Sonnet, **red-first**, worktree-isolated,
**suite floor 134**. **PREREG-002 seals on green + M1, before Saturday if achievable
without haste.**

> **CIO note on the schedule, entered because "if achievable" deserves an honest
> answer rather than an attempt.** The seal has **three** predecessors, not one:
> (i) Ruling 003's 19 tests green at 134; (ii) **I-035** — the perp price series,
> which is PREREG-002 §15 step 1 and without which the basis leg has no mark;
> (iii) M1. Two are dispatched today and run in parallel. **The CIO's honest estimate
> is that Saturday is unlikely**, and the Principal's "without haste" governs over
> the date. A seal is the one action in this firm that P7 makes permanent, and
> Ruling 001 §2.4 already establishes that a delayed seal is strictly cheaper than a
> defective one.

**3 · Sprint 2 standing policy — ONE item, Validation owns the spec.** Four
components:
- **read-only registry connections by default** for dispatched seats;
- **write access granted per-dispatch**, explicitly;
- **schema changes only via sanctioned, Validation-authored migrations**;
- **a defined worktree merge protocol.**

**The Principal names I-041 as the template failure to test the spec against:** a
"verified untouched" claim that checked **rows but not schema**. A policy that would
not have caught I-041 is not the policy.

**CIO observation carried into the spec:** the merge protocol is not cosmetic. On the
H-series the worktree **branch was empty** — the seat correctly did not commit — so
the work existed only as uncommitted files in the worktree directory. Isolation
without a defined merge step leaves the deliverable in a place no git operation
finds.

**4 · §4.4 cost-robustness amendment HELD for the Quarterly Review**, as scoped. It
is not on PREREG-002's critical path: Gate 1 is unreachable for that family before
2027-07-28 on its own §11.3 arithmetic, and Ruling 003's construction moves the
criterion from **actively wrong** (stress-testing a sign error) to **honestly inert**
(24 bps of friction against 1,186 bps/yr of carry).

**Review date:** sprint close, 2026-08-11.

---

## D-014 · 2026-07-31 · Principal directive — four dispositions

**1 · Ruling 003 implementation RE-DISPATCHED.** The 529 overload **counts as spent**
per D-012 — Principal: *"no exceptions carved on first inconvenience."* Sonnet now 13
of 14. The re-dispatch is told to write its deliverable incrementally, since two
failures in this firm have now landed at the compose-at-the-end moment.

**2 · I-042 — technical input supplied, marked "verify before use."** The Principal's
hypothesis: Binance perp funding = **premium index + clamp(0.01%/8h interest −
premium, ±0.05%)**, with measured BTC funding ≈ the interest floor implying mean
premium ≈ 0, reconciling positive funding against negative mean basis; and he flagged
**index-vs-spot-close** and **TWAP-vs-snapshot** mismatches himself.

**CIO tested it against the stored data before dispatching. The result is mixed and is
now the specific thing the verification must explain** [measured]:

| symbol | mean funding bp/8h | mean basis bp | basis σ bp | **% prints not at 1.00 bp** |
|---|---:|---:|---:|---:|
| BTC | 1.0831 | −1.58 | 5.48 | **64.6%** |
| ETH | 1.2846 | −0.95 | 6.46 | **64.7%** |
| SOL | 0.0093 | −3.18 | 38.67 | **64.3%** |

Algebraically, if interest is 1 bp and the clamp band ±5 bp, then **funding equals
interest exactly whenever premium sits inside the band** — so given BTC's 5.48 bp
basis σ, most prints should sit *at* 1.00 bp. **Roughly 65% do not, on all three
symbols.** Either the parameters differ per contract (Binance sets interest to 0% for
many pairs), or the formula changed across the 2020–2026 span, or the CIO's
daily-close proxy is too coarse a stand-in for a TWAP premium index — the mismatch the
Principal named. **Seat 9 verifies against vendor documentation (Sonnet, dispatched),
with `[cited]` defined as a named source actually read.**

**CIO error disclosed in the same breath — see I-044.** The first run of that
arithmetic was wrong by 100× **and** printed a hardcoded prose conclusion beside the
computation. Both corrected before dispatch; logged because a CIO narrating a number
rather than computing it is the artefact A2 forbids, produced by the one seat with no
independent line above it.

**3 · If verified, the Director restates PREREG-002's mechanism before sealing** —
*"the carry's structural component and its premium component are distinct claims and
the document freezes only once."*

> **CIO note: this is unfunded.** Opus is **10 of 10 spent** and the Director's
> allocation is exhausted. The only remaining Opus unit is the **Devil's Advocate's
> Gate 1 reserve**, which the Principal has protected three times and which the CIO
> will not propose spending. A mechanism restatement is Opus-tier judgment work, so
> **it requires either a Sprint 1 ceiling decision or deferral into Sprint 2.** Raised
> now rather than discovered when the verification lands.

**4 · M1 runs after both. Seal next week.** **Saturday's letter reports the seal as
pending, with the reason stated plainly** — not as a slipped milestone but as the
firm declining to freeze a basis-and-carry mechanism under P7 while the basis-to-
funding relationship is unexplained.

**Review date:** sprint close, 2026-08-11.

---

## D-015 · 2026-07-31 · Sprint 1 closes · Sprint 2 opens under Standing Order 001

**1 · I-045 DEFERRED to Sprint 2. No ceiling increase.** Principal's reasoning,
recorded because it is the correct reading of the whole sprint:

> *"The ceiling binding at the seal is the control functioning; the seal that didn't
> happen this week is a seal that would have frozen two defects permanently."*

The two defects: **I-045**, SOL's documented formula change inside the sample, and the
mechanism conflation it implies. Both would have been frozen by P7 at the seal.

**2 · Saturday's letter SHIPS AS SCOPED**, plus one line for **I-044** — the
orchestrator's self-reported fabricated narration. Principal: *"the orchestrator
self-reporting fabricated narration is a governance exhibit, not a footnote."*
Delivered: `research/LETTER-2026-08-01.md`.

**3 · SPRINT 2 OPENS MONDAY under STANDING ORDER 001**, which stands as this firm's
D-001 for the new sprint: **30 invocations / 12 Opus.**

**First Director unit: the PREREG-002 mechanism restatement, with I-045 in hand.**

**Principal input on homogeneity remedies — NON-BINDING**, three candidates:
- **(a)** per-contract **time-varying documented parameters**;
- **(b)** a **declared break control**;
- **(c)** **dropping SOL** under the existing universe menu (menu size 5, already
  declared — so this costs no new `N`).

**Explicitly ruled OUT: a disclosure-only footnote.** The Principal: it *"is out of
scope for the operative state variable, which also rules out Sonnet-scope handling."*
That closes the third option the CIO had floated and settles the question the CIO
raised twice — the restatement is Opus-tier Director work, and Sprint 2's allocation
is where it is funded.

**4 · Sequence thereafter:** **M1 → seal → forward clock starts.** The
**two-terminal-verdicts goal carries into Sprint 2 unchanged, honest either way.**

---

### Sprint 1 closing state — for the record

| | |
|---|---|
| Paper book | $10,000,000.00 · 0 positions · reconcile clean · 0 orders / 0 executions / 0 trades |
| Registry | 0 families · 0 trials · 0 gate verdicts |
| Harness suite | **30 → 139**, 0 failed / 0 skipped / 0 xfail |
| Decisions recorded | 15 |
| Issue Log | 46 entries — 19 HIGH, 23 MEDIUM, 3 LOW, 0 CRITICAL |
| Research artifacts | 20 |
| Commits | 37 |
| Compute | Opus **9 spent of 10** (tenth = DA Gate 1 reserve, unspent by design) · Sonnet **14 of 14** |
| Terminal verdicts | **0 against a target of 2** |
| Origin ratio | **67% Principal / 33% Director** (was 100/0) |
| Forward-test ledger | NIL · **Σα = 0.000** |
| Polymarket book capture | live, 900s cadence, accumulating the only depth history the firm will ever have |

**Review date:** Sprint 2 close.

---

## S2-D-001 · Sprint 2 · 2026-08-04 · Sprint 2 opens · riders A/B/C · A3 clarification

Principal's dispatch of 2026-08-03. Recorded by the CIO at the open of Sprint 2.

**1 · Standing Order 001 is in force.** 30 invocations / 12 Opus. Now committed at
`ops/STANDING-ORDER-001.md`.

> **Correction of record.** The Principal's message stated the Standing Order was
> "committed at `ops/`". It was not — it existed nowhere in the repository or in any
> commit, only as D-015 §3–4 prose. The CIO reconstructed it from that source and
> committed it on 2026-08-04. No content was invented. Recorded because a binding order
> the firm believed was on disk and was not is exactly the class of drift A3 exists to
> catch, and because the near-miss was silent.
>
> **Amended 2026-08-04, after the Principal's correction.** The Principal directed the CIO
> to adopt canonical text at `ops/STANDING-ORDER-001-canonical.md`, diff the
> reconstruction against it, and log the clauses the reconstruction lacked. **That path
> has never existed** — not in the working tree, not in `HEAD`, not in any commit on any
> ref, not in any stash. What the repository does contain is commit `2d9ef4f`,
> Principal-authored, messaged *"canonical Standing Order 001 text (Principal-supplied)"*,
> whose 69 lines are **the CIO's reconstruction byte-identical**, provenance note and all.
> The diff was therefore **not performed and no missing clauses were logged**, because
> producing either from nothing is I-044's fabricated narration. Filed as **I-046**,
> severity HIGH. `ops/STANDING-ORDER-001.md` governs as an acknowledged reconstruction
> until the Principal supplies the canonical text by a path that does not assume it is
> already present. Both dispatches stand, per the Principal's direction.

**2 · A3 CLARIFICATION — git for decisions and code, snapshots for bulk data.**
`book/pit.db` (61.1 MB, 628 documents, 362,077 observations) has left git tracking under
GitHub size limits. This does **not** weaken A3. A3 makes the repo the book of record for
*decisions, code, and artifacts*; bulk captured data is now covered by compressed
snapshots on weekly retention, currently manual to iCloud, with Seat 9 dispatched to
implement the scheduled version (Rider B). On any disagreement about a decision, the repo
still governs. On the data itself, the snapshot regime governs, and a snapshot that does
not exist is a data-loss incident to be filed, not a filing convention.

**3 · Rider A — VPS migration is the sprint's first Sonnet dispatch.** Spend approved,
~$5/month. The Principal's working coverage figure was ~9%. **The CIO measured 5.5%**
across 141.6 hours — 31 polls against 566 expected at the declared 900s cadence, 12 gaps
over one hour, worst 59.9h across the weekend of 2026-08-01. The case for the migration is
stronger than the number that motivated it. Until cutover, gaps are logged as host-sleep,
and all liveness analysis must distinguish **not-polled** from **no-quote** — the CIO has
instructed Seat 9 to verify that distinction against the actual schema rather than accept
it on assertion.

**4 · Rider C — sprint-close Sonnet line-item:** harvest the Issue Log into
`ops/CASEBOOK.md`. The casebook exists as of `223107e` with Sprint 1's seven cases.

**5 · Per-turn Principal review is discontinued.** The CIO now runs the sprint to the
Standing Order and reports at the ritual points. The three independent seats — Validation,
Risk, Devil's Advocate — are unaffected: they still report to the Principal, and the CIO
still cannot overrule a halt, a FAIL, or a Red-Team Memo. Removing per-turn review
removes a checkpoint on the CIO, not a checkpoint on the firm.

**6 · First dispatches, 2026-08-04:** Director of Research (Opus, 1 of 12) — PREREG-002
mechanism restatement with I-045, remedies (a)/(b)/(c) carried as non-binding,
disclosure-only footnote ruled out. Head of Data & Infrastructure (Sonnet) — Rider A,
scoped to design and runbook only; no account creation, no spend, no data leaving the
host without the Principal's hands on it.

### Sprint 2 opening state — verified, not recalled

| | |
|---|---|
| Harness suite | **139 passed**, 0 failed / 0 skipped |
| Registry (`book/registry.db`) | 0 hypotheses · 0 trials · 1 event · 0 gate verdicts |
| Paper book (`book/book.db`) | 0 orders · 0 executions · 0 trades |
| PIT store (`book/pit.db`) | 628 documents · 362,077 observations · 61.1 MB · untracked |
| Holdout vault | `book/vaults/` present; passphrase held by the Principal, not in repo |
| Issue Log | 46 entries · **39 open** · I-045 open and **blocking the seal** |
| Polymarket capture | live, laptop-hosted, **5.5% coverage** — see §3 |
| Forward-test ledger | NIL · **Σα = 0.000** |
| Terminal verdicts | **0**, against a carried target of 2 |

**Review date:** sprint close, 2026-08-11.

---

## S2-D-002 · 2026-08-04 · Canonical Standing Order 001 governs · I-046 resolved · four breaches recorded

> **Renumbered D-003 → D-002 on 2026-08-04.** The CIO had taken `D-003` for this entry
> while the Principal's own D-002 (the canonical-text paste) had no entry of its own; the
> Principal then issued a D-003 of his own for the tool-permission policy. The Principal
> owns this sequence. This entry, which records the Principal's D-002, now carries its
> number; his tool-permission policy takes D-003 below. `[would-have-asked]` — renumbered
> rather than letting two D-003s stand, because a decision record with a duplicate key is
> unusable at the §7 audit and the collision only gets more expensive with age.

**1 · Canonical text received, committed `23be6b6`, verified from `HEAD`.** 53 lines, all
8 sections, zero CIO authorship traces, HEAD blob identical to working tree. The
reconstruction is replaced. `2d9ef4f`'s false label stands unrewritten per A3. **I-046
RESOLVED**; the uncertainty flagged against Gate submissions clears.

**2 · The order is a different document than the CIO reconstructed.** Full measured diff
in I-046. Headline: the two texts share the 30/12 budget number and **one sentence** —
*"Per-turn Principal review is discontinued"* — which is canonical §6's final sentence and
the only clause in §6 that removes oversight. §4 hard interrupts, §5 dead-man, §7
calibration audit, and §8 erosion guard were absent in full, as were §1's objective
function and §2's rollover and failed-invocation rules. Of the two clauses preserved, one
caps budget and one removes review; of the ~18 lost, all constrain the CIO. The
Principal's characterization — "silently narrowed order" — is confirmed as measured fact,
and understates it: this was not a narrowing but a substitution.

**3 · Four breaches incurred during the interval, recorded as fact.**

| # | Breach | Correction |
|---|---|---|
| 1 | §2 — CIO ruled a failed invocation counts once. §2: *"Failed invocations count as spent."* | **3 of 30 · 2 of 12 Opus.** DA reserve seals 1 Opus for PREREG-002 → **9 freely allocable** |
| 2 | §4 — I-046 filed HIGH did not halt and queue; CIO continued in-turn | Outcome converged via D-002, but convergence by luck is not compliance |
| 3 | §3 — no `[would-have-asked]` tags applied | Tagged retroactively in §4 below |
| 4 | §1 — the **ML trial-accounting ruling** is a sprint goal with no owner, no agenda entry, no dispatch | Requires allocation; see §5 |

**4 · Retroactive `[would-have-asked]` tags** for decisions taken 2026-08-04 before the
order was in hand:

- `[would-have-asked]` **Resumed the failed Director unit from transcript rather than
  re-dispatching.** Reason: preserves a 1,492-line read; the failure was infrastructural,
  not the seat's. Under §2 this decision is now cost-neutral to make — both count as spent
  either way — which strengthens rather than weakens it.
- `[would-have-asked]` **Held Rider B rather than running two concurrent dispatches into
  Seat 9.** Reason: same seat, same tree, concurrent writes; sequencing costs latency,
  collision costs correctness.
- `[would-have-asked]` **Scoped Seat 9's Rider A to design and runbook only — no account
  creation, no spend, no data egress.** Reason: §4 reserves "anything that spends money
  outside the stated budget" to the Principal. The scoping was correct before the CIO
  could cite the clause requiring it.
- `[would-have-asked]` **Declined to fabricate the instructed diff and reported the
  blocker instead.** Reason: I-044. Recorded because it is the one this sprint's audit
  should scrutinize hardest — refusing an instruction is the decision most in need of
  external check.

**5 · Sprint agenda gap, surfaced not resolved.** §1's ML trial-accounting ruling has no
owner. It is Validation-tier work (Gate 0 search-space declaration, trial accounting,
purged/nested CV, seed fixing) and Validation reports to the Principal, not the CIO. The
CIO proposes dispatching it to `quant-validation` as an Opus unit once the Director's
PREREG-002 restatement lands, so the ruling can bind the very family approaching seal
rather than arrive after it. **Not actioned pending the interrupt queue.**

**Review date:** sprint close, 2026-08-11, at the §7 calibration audit.

---

## S2-D-003 · 2026-08-04 · Tool-permission policy matching the delegated authority

**Principal-issued.** A tool-permission policy is committed at `.claude/settings.json`:
routine operations no longer prompt; **sudo, scheduled tasks, bulk deletion, and
credential paths remain Principal-only.** *"Any residual prompt means the task is reaching
outside scope — queue it, don't work around it."*

**Verified before acceptance** [measured], because two of the three artifacts asserted as
committed this session were not: `.claude/settings.json` is present on disk **and in
`HEAD`** at commit `9678e5c`, and its contents match the description — `allow` covers
Read/Edit/Write/Task/Glob/Grep, `git`, `python3`, `pip`, `pytest`, `sqlite3` and routine
shell; `deny` covers `sudo`, `rm -rf`, `crontab`, `launchctl`, `~/.ssh/**`, `~/.aws/**`.
**This one is real.** Appended to `ops/STANDING-ORDER-001.md` as an addendum.

**CIO reading of the operative clause.** "Queue it, don't work around it" is treated as an
extension of §4: a permission prompt is itself an interrupt signal, and the CIO may not
re-route a denied operation through an allowed tool to reach the same effect. Immediate
bite on **Rider A** — the VPS migration touches `crontab`/`launchctl` (denied) and spends
money (§4 reserved). Both were scoped to `[PRINCIPAL]` steps by instruction before the
policy existed; the policy now enforces mechanically what the dispatch enforced by wording.

---

## S2-D-004 · 2026-08-04 · Director's PREREG-002 restatement lands · §4 HARD INTERRUPT — KC-002 restated

**1 · §4 HARD INTERRUPT FILED. Trigger: *"any kill-condition signature or restatement."***

Revision `R-001` of `research/PREREG-002-crypto-funding-basis.md` includes **R7**, whose
own revision-block text reads: *"**KC-002 clause (b) gains a named mechanism.**"* The edit
lands in **§14.2**, inside the binding kill-condition section, and raises the seat's stated
probability that clause (b) is the family's killer from *"most likely"* to *"the expected
outcome, and the reason is the clamp rather than the market."*

**The CIO does not assess whether this "really" qualifies.** §4 makes these triggers, not
thresholds, and states that no seat including the CIO decides qualification; §8 forbids
introducing an adjective by interpretation. The document's own revision block calls it a
change to KC-002. **It is therefore a kill-condition restatement and it queues.**

For the Principal's ruling, stated without softening and without recommendation: KC-002's
operative clauses (a)/(b)/(c) and its thresholds, window, and observation date
(**2027-01-31, absolute**) are **not** edited by R7. What changed is §14.2's commentary —
a pre-seal statement of expectation, marked `[inferred — not measured]`, arguing the clamp
censors the state variable on ~35% of prints. **That description is the CIO reporting the
scope of the change, not the CIO arguing it is minor.**

**This interrupt blocks the PREREG-002 revision's adoption and any move toward seal. It
does not block unrelated work** (§4), and the seal was independently unreachable anyway —
see §3.

**2 · The Director's return overstated one thing, and the CIO checked rather than relayed
it.** The return states *"I-045 is closed."* **On disk it is not.** `logs/ISSUE_LOG.md`
I-045 still reads **"Resolution: open — blocks the seal."** The Director's remedy addresses
I-045 but the entry was never edited. **The CIO is not closing it**, for two reasons: the
seat that owns closure is `quant-validation`, not the CIO; and the remedy's own premise is
unverified — see C12. I-045 stands **open**.

**3 · Verified independently of the seat's report** [measured]: `book/registry.db` holds
0 hypotheses and 0 trials; `book/book.db` holds 0 orders / 0 executions / 0 trades. **No
number was produced by this dispatch and A2 is intact.** `PREREG-002` 1,492 → 1,858 lines
with R1–R7 struck-and-replaced inline; `DIR-RESTATE-001-prereg002-mechanism.md` new at 477
lines. Nothing committed by the seat, as instructed.

**4 · NOT SEAL-READY, and the Director says so.** Open blockers per the memo: **C12**
(new, created by this revision — K7 cannot seal while the primary universe's cadence
homogeneity is asserted rather than measured; I-045's control covered **BTC only** and only
the `>3 prints` direction, so a cadence *lengthening* was never tested and **ETH was never
measured at all**), **C2** (no Gate 0 intake verdict), **C11** (leg-(ii) null), **C3** (no
Devil's Advocate memo on this family), **C7/C8** (executional). The seat naming a blocker
it created itself, one turn after being funded to clear a blocker, is the control working.

**5 · Resumption honesty, relayed verbatim in substance.** The Director reports nothing
analytical was lost to the API termination and that its conclusion did not move between
runs — **and flags that the only evidence for this is its own account, because nothing had
reached disk, so the claim is `[assumed]` not `[measured]`.** Recorded because a seat
volunteering the weakness of its own evidence is the behaviour this firm is built to
reward.

**6 · `[would-have-asked]` — C12's measurement dispatch.** C12 is a row-count query on
already-ingested data, not a trial. Under §3 dispatching it is delegated. **No decision was
required**: its owner is Seat 9, which is mid-dispatch on Rider A, and two concurrent
dispatches into one seat and one tree was already ruled against in S2-D-002 §4. C12 is queued
behind Rider A's return, not held for the Principal.

**7 · Budget.** 3 of 30 · 2 of 12 Opus. DA reserve holds 1 Opus for this family under §2 —
and **C3 confirms the reserve is needed**: no Red-Team Memo exists on PREREG-002. Freely
allocable Opus: **9**.

**Review date:** on the Principal's ruling on the §4 interrupt.

---

## S2-D-005 · 2026-08-04 · Rider A returns · §4 HARD INTERRUPT — spend exceeds the stated budget

**1 · §4 HARD INTERRUPT FILED. Trigger: *"anything that spends money outside the stated
budget."*** The Principal approved **~$5/month**. Seat 9's provider selection is a
**DigitalOcean Basic Droplet at $6/month** (1 vCPU / 1 GiB / 25 GB SSD, Ubuntu 24.04 LTS).
**$1/month over.** The seat flagged it rather than rounding, with arithmetic: measured
capture growth is **339,968 bytes/round ≈ 32.6 MB/day ≈ 0.98 GB/month ≈ 11.9 GB/year** at
the current 20-token universe, so the $4/month tier's 10 GB disk **fills in ~7 months**
against **~21 months** for the $6 tier. **The CIO makes no recommendation and does not
round; §4 reserves this and §8 forbids softening it.**

**2 · Verified independently of the seat's report** [measured]: harness suite **160
passed**, up from 139, 0 failed — the seat's claim holds. `book/pit.db` now at 710
documents / 365,465 observations, **no new tables** — the heartbeat rides existing schema,
so A4's restatement path is unchanged. Laptop capture **live throughout and now polling on
cadence** (16:53:17Z, 17:08:18Z — 15 minutes apart, first clean interval this session).

**3 · The capture's own code changed under a running process.** `loaders.py` and
`capture_polymarket_book.py` were modified mid-session and **the live laptop capture picked
the change up on its next firing without restart**. That is the correct outcome and it was
not a controlled deployment — the firm changed production data-collection code while it was
collecting. Recorded because it worked this time. `[would-have-asked]` — the CIO allowed it
by instructing the seat not to stop the capture, judging a coverage gap worse than an
in-flight code change; that trade is the Principal's to review at §7.

**4 · Two issues filed, both MEDIUM, neither an interrupt.** **I-047** — an un-retried
Gamma call crashing on DNS failure after host wake was the measured, repeated, uncaught
cause of real capture gaps; **four occurrences found in `polymarket-book.err`**, fixed with
retry/backoff. This means the 5.5% coverage figure is **not** wholly host-sleep as S2-D-001 §3
recorded; part of it is a defect the firm shipped. **I-048** — "not polled" vs "polled,
whole batch failed" were **provably indistinguishable** in `book/pit.db` before today.
Closed going forward at **2026-08-04T16:53:16Z** via a heartbeat wired into every exit path;
**permanently open for all prior history**. The seat checked the schema rather than
accepting the assertion carried in S2-D-001, and the assertion was wrong.

**5 · Dual-writer decision, accepted under §3.** The VPS owns a capture-only store
(`pit_capture.db`) born empty, never touching `book/pit.db`; data reaches the real store
only through `merge_polymarket_capture.py`, replayed via `PITStore.ingest()` against the
real store and real `TrialRegistry`, **so A4 restatement auto-logging fires exactly as for
any other source.** The CIO accepts this as operational architecture within delegation.
`[would-have-asked]`.

**6 · Secrets: none.** Both endpoints (`clob.polymarket.com/books`,
`gamma-api.polymarket.com/markets`) verified public and unauthenticated against the code —
`User-Agent` only, no key or token anywhere. This materially simplifies cutover.

**7 · Runbook: 14 steps, 7 marked `[PRINCIPAL]`** — account and droplet creation, SSH key,
two file transfers, install execution, the VPS→local pull, and the laptop-decommission
decision. **Nothing was provisioned, no account created, no money spent, no data
transmitted off this host.** Under S2-D-003's policy, `crontab`/`launchctl` are denied and the
spend is §4-reserved, so the cutover cannot proceed without the Principal regardless.

**8 · Budget.** 3 of 30 · 2 of 12 Opus, unchanged — Rider A was the Sonnet unit already
counted. DA reserve holds 1 Opus. Freely allocable Opus: **9**.

**9 · Record-integrity note, flagged not fixed.** `logs/DECISION_RECORD.md` now contains
**two each** of D-001…D-004 (now S2-prefixed) — Sprint 1's and Sprint 2's — because Standing Order 001
restarts the sequence per D-015 §3. The keys are no longer unique, which will bite at the
§7 audit. The CIO proposes a sprint prefix (`S2-D-001`) but **has not renumbered the
Principal's scheme unilaterally.** Awaiting direction.

**Review date:** on the Principal's ruling on the two open §4 interrupts.

---

## S2-D-006 · 2026-08-04 · Principal rules both §4 interrupts · C12 and the ML ruling dispatched

**1 · Interrupt 1 — APPROVED AND COUNTERSIGNED** as a kill-condition commentary
restatement. The Principal confirms on the record that KC-002's operative clauses
(a)/(b)/(c), thresholds, window, and the **absolute observation date 2027-01-31** are
unedited, and that the addition is pre-seal expectation-setting marked `[inferred]`,
recorded *"precisely so it cannot later be claimed as foresight."*

**Principal's note for the file, recorded verbatim in substance because it changes how a
future verdict must be read:** under the restated §3 mechanism, **clause (b) firing because
of the clamp is the hypothesis being answered, not the test being interrupted — a kill on
those grounds is a full terminal verdict.**

The CIO flags the consequence, since it bears on the Standing Order §1 goal: this ruling
means the family's **most likely** outcome, as the Director itself predicts at §14.2, now
counts toward the **two-terminal-verdicts** objective rather than reading as a failure to
reach one. That is the §1 clause *"a correct kill counts identically to a pass"* operating
exactly as written, and it is worth stating plainly that the firm is not thereby made more
likely to succeed — only more likely to **resolve**.

**2 · Interrupt 2 — APPROVED.** DigitalOcean at **$6.00/month exact.** The Principal rules
the flag correct under §4 and the ambiguity his own: *"'~' is retired from spend approvals
— this line item's ceiling is $6.00/month exact, and all future approvals will state exact
ceilings."* Recorded as a standing change to how spend authority is expressed. Seat 9's
refusal to round $6 into "~$5" is the behaviour that produced the clarification.

**3 · `S2-` prefix adopted.** Sprint 2 decision entries renumbered `S2-D-001` … `S2-D-005`;
**zero duplicate keys remain** in the record; five internal cross-references updated to
match. Sprint 1's `D-001`…`D-015` are untouched.

**4 · Two dispatches, parallel and independent.**

- **C12 — Seat 9, Sonnet.** BTC and ETH funding-print cadence sweep across PREREG-002's
  full sample, **both directions**, since I-045's control was BTC-only and `>3`-only and
  ETH was never measured. Brief requires the low-count days be separated into **genuine
  cadence change / missing ingest data / undetermined** rather than assigned by assumption
  — conflating them would reproduce the defect this measurement exists to prevent. Escalation
  rule stated in advance so the seat does not have to judge it: a genuine deviation on the
  primary universe means escalation to Validation for an admissibility ruling on the whole
  family, **not** further trimming of the universe.
- **ML trial-accounting ruling — Validation, Opus.** The Standing Order §1 objective that
  S2-D-002 §5 found had no owner. Brief adds the question the Standing Order does not name
  but the firm cannot do without: **how `N` is defined for a model class where the effective
  number of trials is not the number of fits** — because DSR/PBO/MinBTL all take an `N`, and
  a gate with an undefined `N` is unenforceable while still looking like a control.
  Validation reports to the Principal; the dispatch allocates compute and scope, not
  conclusions.

**5 · Sequencing, and why C2 was not dispatched with them.** The Gate 0 intake verdict on
PREREG-002 (**C2**) is deliberately held until C12 returns. If C12 finds a genuine cadence
deviation on BTC or ETH, the family's admissibility question changes shape, and an intake
verdict issued now would have ruled on a premise C12 could invalidate. **C3** — the
Devil's Advocate memo, which no PREREG-002 packet may omit — is held for the §2 reserve
Opus and is the last thing before any Gate 1 submission, not the first.

**6 · Budget.** **5 of 30 · 3 of 12 Opus.** DA reserve holds 1. Freely allocable Opus: **8.**

**Review date:** on the return of C12 and the ML ruling.

---

## S2-D-007 · 2026-08-04 · C12 returns clean · discharged on the cadence dimension only

**1 · Verdict: BTC and ETH are cadence-homogeneous across PREREG-002's sample.** Zero
deviating days on either symbol, in either direction, across **4,802 symbol-days**.
Delivered at `research/DATA-VERIFY-002-cadence-homogeneity.md`. K7's premise moves from
**asserted** to **measured**, which is what C12 existed to force.

**2 · Independently reproduced by the CIO from `book/pit.db`** [measured], on the I-045
precedent that a row-count diagnostic may be CIO-confirmed:

| Symbol | Days | Prints | Distribution | Deviating |
|---|---|---|---|---|
| BTC/USDT:USDT | 2,401 | 7,203 | `{3: 2401}` | **0** |
| ETH/USDT:USDT | 2,401 | 7,203 | `{3: 2401}` | **0** |
| SOL/USDT:USDT *(control)* | 2,145 | 6,508 | `{1:1, 3:2134, 4:1, 6:1, 11:1, 12:7}` | **11** |

**The SOL control is what makes the zero admissible.** A clean result on both primary
symbols could have meant the store is incapable of representing a cadence other than 3 —
in which case the measurement would be tautological and worthless. SOL's 11 deviating days,
landing on 2022-11-09 (4 prints) then 11–12 prints through 11-15, reproduce I-045's table
exactly and prove the store represents ≠3 faithfully. **A verification that cannot fail is
not a verification**; this one could have and did not.

**3 · The limitation, stated so C12's closure is not over-read. C12 measured *cadence*
homogeneity, not *parameter* homogeneity, and the two are not the same claim.** The seat
reports that the firm's own documented **2025-09-18 firm-wide funding-formula change** shows
**3 prints on both BTC and ETH that day** — that is, a real documented parameter change that
a cadence sweep is structurally blind to. 2025-09-18 is precisely the in-sample trigger the
Director named when declaring **K7**, so it is handled **by declaration, not by
measurement**, and that is the design working. But the residual is real and belongs to
Validation at C2, not to the CIO: **Binance states it does not announce adjustments, so an
undocumented clamp-width change on BTC or ETH inside the sample would be invisible to both
the cadence sweep and the documentary record.** The CIO does not rule on whether that
residual is tolerable — flagged into the C2 intake, where it belongs.

**4 · No issue filed, correctly.** The dispatch's escalation rule was conditional on finding
a genuine deviation; none was found, so it did not trigger. The seat did not manufacture an
entry to show work, and did not touch `PREREG-002`, `DIR-RESTATE-001`, `registry.db`, or
`book.db`. Suite **160 passed**, unchanged.

**5 · I-045 remains open, and the CIO still does not close it.** C12 verifies the remedy's
premise, which was the blocker the CIO named at S2-D-004 §2 for declining to close it. The
remaining reason stands unchanged: **closure is `quant-validation`'s, per the issue's own
owner line.** It is routed into the C2 dispatch rather than resolved here.

**6 · C2 is now unblocked but NOT dispatched.** Validation is mid-dispatch on the ML
trial-accounting ruling. Two concurrent dispatches into one seat and one tree has been ruled
against three times this sprint (S2-D-002 §4, S2-D-004 §6) and the reasoning has not
changed. C2 goes on Validation's return. `[would-have-asked]`.

**7 · Budget.** 5 of 30 · 3 of 12 Opus, unchanged — C12 was the Sonnet unit already counted.

**Review date:** on the ML ruling's return, when C2 dispatches.

---

## S2-D-008 · 2026-08-04 · Second Opus termination · I-049 filed MEDIUM · budget corrected

**1 · The ML trial-accounting ruling died at the same transition the Director's did**, with
the same error, after the same kind of large read, leaving nothing on disk. Verified before
resuming [measured]: no ruling file, `book/registry.db` intact at 0 hypotheses / 0 trials,
suite **160 passed**, tree unmodified apart from the live capture files. **Resumed from
transcript** with the incremental-write instruction that the Director's resume carried.

**2 · I-049 filed at MEDIUM,** with the reasoning for *not* filing HIGH stated on the face
of the entry, since §8 forbids under-rating to dodge a §4 interrupt: no corruption of data,
record, or number; recovery path known and tested; **cost is budget alone.** A
**pre-committed escalation trigger** is written in — **a third occurrence makes it HIGH**,
because at that rate the failure threatens §2 budget exhaustion, which is itself a §4
interrupt, and the correct response then is a dispatch-design change rather than another
resume.

**3 · Budget, corrected under §2.** *"Failed invocations count as spent."*

| | |
|---|---|
| Invocations | **6 of 30** |
| Opus | **4 of 12** |
| DA Gate 1 reserve (§2, PREREG-002 approaching seal) | 1 |
| **Freely allocable Opus** | **7** |

**Four Opus units have produced two artifacts.** Two of the twelve — 17% of the sprint's
scarcest tier — bought nothing. This is recorded plainly rather than absorbed, because the
§1 objectives are unmet and the tier is what pays for them.

**4 · What the CIO is not doing.** Not spending a unit to diagnose whether the terminations
correlate with read volume or with infrastructure. Two data points support no claim either
way, and the sprint's objectives are unmet. The assessment is marked `[assumed]` in I-049
rather than dressed as a finding.

**Review date:** on the ML ruling's return.

> **AMENDED 2026-08-04 — this entry's own commit message is false, and Validation caught it,
> not the CIO.** Commit `ffd73a9` carries the message *"leaving nothing on disk… tree
> clean."* That was true when the CIO verified it, **before** resuming the dispatch. It was
> **not** true when the CIO committed: `git add -A` swept up **77 lines of
> `VALIDATION-RULING-004` in progress**, written by the resumed Validation seat working
> concurrently — **written incrementally because the CIO had instructed it to.** Verified
> [measured]: `git show ffd73a9 --stat` lists the ruling file.
>
> **Root cause is the CIO's commit practice, not the seat's.** `git add -A` while a
> background dispatch is writing captures whatever that dispatch has reached, and the
> commit message then describes a tree that no longer exists. **Corrective, effective
> immediately: no `git add -A` while any dispatch is in flight — stage named paths only.**
>
> Filed by Validation as **I-054**, the *third* occurrence of I-013/I-041's shape. Under A3
> history is not rewritten, so `ffd73a9` stands with its false message and this amendment
> is the correction. The CIO notes for the §7 audit that the seat which found this was the
> one the CIO had just finished describing as having produced nothing.

---

## S2-D-009 · 2026-08-04 · ML trial-accounting ruling lands · §4 HARD INTERRUPT — I-050

**1 · §4 HARD INTERRUPT FILED. Two triggers, one item:** *"any issue filed HIGH"* and *"any
finding by Validation… addressed to the Principal."*

**I-050 — the Gate 1 t-statistic assumes serial independence and nothing corrects it.**
Validation's finding, relayed unbatched and unsoftened per §8: the firm's own measured
autocorrelation **ρ = 0.83** implies roughly **3.3× inflation** of the t-statistic, the
error runs in the **permissive** direction, and no existing criterion corrects it.
Validation states `T_STAT_HURDLE = 3.0` **does not move** — the *estimator* is corrected to
its own stated assumption, which it holds is Seat 3's ownership. **No Charter amendment, no
threshold change, and no override is requested anywhere in the ruling.** The one-paragraph
form is at ruling §14.1.

The CIO takes no position on I-050 and has none to take: Validation reports to the
Principal, and this is inside its mandate.

**2 · Checked, not relayed** [measured]: `book/registry.db` 0 hypotheses / 0 trials; suite
**160 passed**; `git diff -- harness/` **empty**; ruling delivered at 1,412 lines. A2 intact.
Severities on disk match the seat's report — I-050 HIGH, I-051 through I-054 MEDIUM.

**3 · The ruling, in the numbers that bind.** 27 clauses (ML-1…ML-27), 14 acceptance tests.

`N = n_inherited + n_declared_fits + n_logged` — the sealed cardinality of the declared
search space, plus every `run_backtest` call, plus inherited count, with exactly one
reduction (a candidate set fully re-selected inside a correctly purged nested inner loop,
reporting only the outer-fold aggregate, contributes 1).

**The finding the dispatch did not ask for, and which the CIO judges the most consequential
thing in the document:** `N` alone deflates almost nothing — **`N × σ_SR` does.** Moving `N`
from 10 to 100,000 raises the DSR bar by **0.56 Sharpe** at σ_SR = 0.20; moving σ_SR from
0.20 to 0.80 at fixed `N` = 1,000 raises it by **1.96** [measured]. **σ_SR is roughly three
times more load-bearing than `N`, and the firm currently lets the sponsor choose it by
choosing which trials get a return series.** That is a governance hole in the gate the firm
believed was its strictest control, found by the seat whose job is to find it. ML-16's
mandatory pre-selection dispersion sample (m ≥ 32, uniform over the declared space, run
first) closes it.

**Second consequential number, and it reshapes the firm's opportunity set:** at the Gate 1
Sharpe floor of 1.0 against the **6.571 years** of BTC/ETH history the firm holds, maximum
admissible total `N` is **109**; after required diagnostics, roughly **30 configurations of
genuine search remain.** **This forecloses neural nets, AutoML, and large sweeps at Gate 1
on every data surface this firm currently has — at intake, before compute is spent.** The
CIO records this as a *finding*, not a *constraint to be worked around*: it means the honest
ML frontier for Castellan is small-search, high-prior work, and any pod proposing otherwise
is proposing something the firm cannot validate.

**4 · Standing consequence accepted.** Until `n_declared_fits` exists in the registry, **no
fitted family may be sealed as Gate-1-eligible — ADMITTED-AS-EXPLORATORY is the ceiling.**
Zero fitted families exist, so today's cost is zero. Blocked on harness work: ML-11, ML-3's
enforcement, ML-16's DSR criterion, ML-18/ML-21(c) and §6.1, ML-26 enforcement, ML-17's
mechanism. Everything else effective immediately.

**5 · No contradictions created; one pre-existing contradiction found.** PREREG-002 §7.2's
menu discount is *extended*, not contradicted; `run_parameter_grid`'s "every point is a
logged trial" preserved unamended. But **PREREG-002 §7.2's binding escalation rule is
unexecutable** — it requires `n_inherited ≥ menu_size × chain_total`, which `open_hypothesis`
refuses for every menu size ≥ 2 (**I-053**). And **PREREG-002 §10.4's ceiling is 109, not
110** — a correction to a document awaiting seal, which now needs the Director's hand before
sealing.

**CIO check on whether this is a §4 Charter–harness divergence: it is not, and the CIO
verified rather than assumed in the direction that would have avoided an interrupt.**
`FUND_CHARTER.md` §7.2 is *Research Memo*; the escalation rule lives in PREREG-002's own
§7.2. Document–harness divergence, not Charter–harness. Recorded so the reasoning is
auditable at §7.

**6 · Issue-numbering collision, recorded not absorbed.** The dispatch told Validation to
number from **I-049**; the CIO filed I-049 for the termination pattern *during Validation's
outage*. Validation renumbered itself to **I-050…I-054** and recorded the collision rather
than overwriting. **The CIO caused it** by allocating a number to itself from a range already
issued to a seat.

**7 · I-052 rated MEDIUM by Validation with its reasoning on the record** — its shape is
I-027's, but I-027 was HIGH because a live family was blocked; nothing is blocked here and
the ruling supplies a safe default. **Rating it HIGH to force attention would be the mirror
of the error §8 warns against.** The CIO endorses the reasoning and notes it is the second
seat this session to state a severity rationale unprompted.

**8 · Termination continuity.** Nothing lost, nothing re-derived, conclusion did not move —
and Validation marks that `[assumed]`, not `[measured]`, at ruling §0.2, because the first
run wrote no artifact to check against. **Same discipline the Director showed on the same
failure.** The §2–§3 arithmetic is independently re-runnable and is `[measured]`.

**9 · Oracle pointer.** Validation reports no Oracle tool in its invocation. Placed by the
CIO under A3.

**10 · Budget.** **6 of 30 · 4 of 12 Opus** — the resume was already counted at S2-D-008.
DA reserve 1. Freely allocable Opus: **7.**

**11 · C2 remains undispatched.** It is now unblocked on both counts — C12 clean, Validation
free — but the ruling has just changed what a Gate 0 intake verdict on PREREG-002 must
check: §10.4's ceiling correction and I-053's unexecutable escalation rule are both live
against that document. **Dispatching C2 before the Director repairs §10.4 would send
Validation to rule on a document with a known-wrong number in it.** Sequencing: Director
repairs, then C2. `[would-have-asked]`.

**Review date:** on the Principal's ruling on I-050.

---

## S2-D-010 · 2026-08-05 · I-050 approved · estimator asymmetry enters §8 · two dispatches

**1 · I-050 APPROVED.** The Principal confirms on the record that this is **not a threshold
change**: `T_STAT_HURDLE = 3.0` stands, and *"what changes is that the number compared
against it now measures what it always claimed to measure."* Precedent named: **Ruling
003's bisection-artifact logic — permissive measurement defects are repaired without
ceremony.**

**2 · §8 WIDENING, recorded into the order itself.** The Principal attached an asymmetry
*"so this ruling can't be cited sideways later"*:

> Estimator corrections **toward** a statistic's stated assumptions belong to Validation and
> need no Principal act. Any estimator change that **loosens** — relaxes an assumption,
> widens a tolerance, swaps to a more permissive construction — **is a §2 threshold matter
> and interrupts, regardless of framing.**

§8 provides that the interrupt set may be widened by any seat and narrowed only by the
Principal in writing. This is a widening, in writing, so it is written into
`ops/STANDING-ORDER-001.md` as an addendum rather than left in the decision record alone —
a widening that lives only in the record is one a future seat reads the order without
finding. The operative test is recorded there in one line: **does the corrected statistic
measure more of what it always claimed to measure, or less?**

The CIO notes what this forecloses, since that is the point of it: the I-050 precedent,
left unqualified, is precisely the shape a future seat would cite to wave a loosening
through as "just an estimator change."

**3 · Two dispatches, parallel, no file or seat collision.**

- **Director, Opus — PREREG-002 revision R-002.** Three repairs: §10.4's ceiling **110 →
  109** per RULING-004; **I-053**'s unexecutable §7.2 escalation rule, which the harness
  refuses for every menu size ≥ 2 and which is therefore currently decorative; and recording
  what the corrected Gate 1 estimator changes for this family **pre-seal**. The brief asks
  explicitly whether R6's `MinBTL(86) = 6.14 yr` and its **0.43-year margin** survive the
  ceiling correction — *a margin that shrinks is a finding*, and the Director is told to say
  so rather than preserve R-001's numbers.
- **Validation, Opus — specification and red-first tests.** Specifies the corrected `sr_tstat`
  construction with no implementer discretion, and writes acceptance tests **that fail against
  today's harness**. Validation specifies; **Seat 9 implements**, per the Charter's ownership
  of the harness.

**4 · The suite will go red by design, and this is recorded in advance rather than
discovered.** Floor stands at **160 passed**. After Validation's dispatch the suite is
expected **red**, deliberately, until Seat 9's implementation turns it green and the floor
rises. **If this session ends with the suite red, that is the intended state of a red-first
regime and not an incident** — I-036's precedent (an agent leaving the suite red by
accident) is the opposite case and must not be confused with it.

**5 · `[would-have-asked]` — I-051 added to Validation's scope.** Its CV-leakage defects
(`walk_forward_windows` purges and embargoes nothing; `purged_kfold_splits` ignores feature
lookback) are the **same permissive direction** as I-050 and blocked on the **same harness
area**, so they ride the same revision rather than waiting for a separate unit. The brief
tells Validation the CIO's sequencing **is not binding on its scope** and it may decline to
bundle them. Reason for the tag: bundling a MEDIUM into a Principal-ruled HIGH's
implementation is the kind of scope decision the CIO would previously have surfaced.

**6 · One question added to Validation's brief on the CIO's own initiative:** does the
corrected estimator move **RULING-004's `N` = 109 ceiling or its MinBTL arithmetic**, both
computed under the *uncorrected* statistic? If the ceiling moves, the firm needs it now,
pre-seal — not after PREREG-002 is frozen. This is the second-order consequence of a
first-order correction, and nobody had asked it.

**7 · Budget.** **8 of 30 · 6 of 12 Opus.** DA reserve 1. Freely allocable Opus: **5.**

**8 · §5 dead-man clock reset** by this checkpoint. **8 invocations remain** before the
mandatory halt, whichever comes first with the 5-calendar-day limit.

**9 · Sequence from here**, the Principal having left it to the CIO: Seat 9 implements
Validation's spec (Sonnet) → **C2** Gate 0 intake verdict once the Director's R-002 lands,
so Validation does not rule on a document carrying a known-wrong ceiling → **C3** Devil's
Advocate memo on the §2 reserve Opus, last before any Gate 1 submission. **Rider B**
(snapshot scheduling) and **Rider C** (casebook harvest) remain outstanding and are Sonnet.

**Review date:** on the return of R-002 and the estimator specification.

---

## S2-D-011 · 2026-08-05 · R-002 lands · §4 HARD INTERRUPT — KC-002 clauses 2 and 3 restated

**1 · §4 HARD INTERRUPT FILED. Trigger: *"any kill-condition signature or restatement."***
R-002's **R9** names its own targets: *"§14 KC-002 anti-reinterpretation clauses **2 and
3**"*, plus the sealed **`forward_kill_condition`** field. Verified on the document
[measured].

**This is a larger change than Interrupt 1 was, and the CIO says so rather than leaning on
the earlier approval.** Interrupt 1 was §14.2 *commentary* — expectation-setting, marked
`[inferred]`, operative clauses untouched. **R9 changes operative post-kill machinery**: what
a successor family must declare after KC-002 fires. Clause 3 read *"a new family opened with
`n_inherited ≥` the killed family's final `n_trials` plus its own"*; it now reads
`predecessor_family` alone with `n_inherited` = the successor's own new search.

**Why the Director changed it, stated as the seat states it:** the struck form was
*redundant and unexecutable from the same misreading* — `family_stats` already sums the
predecessor chain transitively across `predecessor_chain` [measured, `registry.py`], so
re-declaring the count in `n_inherited` double-counts it, which is exactly what
`InheritedCountDoubleCountError` refuses. **The clause's intent — that a restatement cannot
escape its predecessor's trial count — is preserved and is now enforced by the harness
instead of asserted by the sponsor.**

KC-002's **operative clauses (a)/(b)/(c), thresholds, window, and the absolute 2027-01-31
observation date are unedited**, and R10 records KC-002 as unaffected by the estimator
correction, its clauses being bare comparisons with no `t`. The CIO reports that scope as
fact and does not argue from it.

**2 · The Director found an error in Validation's ruling, issued hours earlier.** The same
`family_stats` misreading appears in **four** binding clauses across two documents —
PREREG-002 §7.2, KC-002 clause 3, §19.3's successor, and **`VALIDATION-RULING-004` ML-17,
which copied this document's formula citing it as source.** Filed **I-055, MEDIUM**, routed
to `quant-validation`. **A seat correcting the independent gatekeeper's fresh ruling, in the
gatekeeper's own arithmetic, is the firm working.**

**3 · The expected outcome for this family moved against it, pre-seal.** Gate 1's `t` on net
returns is the one criterion the estimator correction narrows. Composing R4(b)'s ≈2× haircut
with the ≈3.3× inflation puts the required uncorrected, pre-haircut `t` at **order 20**
[inferred — the family's own ρ is unmeasured and measuring it is a trial]. §11.6's *"largest
single hurdle"* no longer describes the 50% haircut. **§19.3 is revised against the family:
conditional on F-002 surviving in full, the expected Gate 1 outcome is now PARK-WITH-TRIGGER,
not PROCEED.** The §19 verdict to fund stands, because F-002 and KC-002 deliver a verdict
without touching a `t` — and under the Principal's S2-D-006 ruling a correct kill is a full
terminal verdict.

**4 · The ceiling correction did not move R6's margin, and the Director refused to pretend
it did.** `N` = 86, `MinBTL(86) = 6.14 yr`, and the **0.43-year margin are unchanged** —
86 < 109, so the correction never reaches them. What shrank is unused headroom, **24 → 23
trials**. The seat considered reporting this as a narrowing of R6's margin and rejected it as
*"theatre in the pessimistic direction."* Recorded because the incentive at a sprint whose
goal is verdicts runs toward dramatising, and the seat ran the other way.

**5 · I-053's severity understates its firing date for this family, and the Director raised
it without overwriting Validation's rating.** §19.3's named successor changes K6 (menu size
4, requiring `3 × chain_total`), which the harness refuses today — **so the successor cannot
be opened until the registry repair lands**, and that successor is this seat's stated
most-likely deliverable. The CIO accepts this as a **sequencing constraint**: the registry
repair rides with Seat 9's implementation dispatch, not later.

**6 · Two issues filed, both MEDIUM, with reasoning on the record.** I-055 — the error runs
**conservative**, is latent at 0 trials, blocks nothing. I-056 — ML-2 makes a missing ML
declaration a Gate 0 **rejection** rather than a deferral, applies firm-wide, but no number
is wrong and the fix is one sentence per unsealed document; PREREG-002 repaired, **PREREG-001
and the template still open.** Third and fourth consecutive seat to state a severity
rationale unprompted.

**7 · CIO error, second of the same kind.** The Director was told to number from **I-055**;
Validation, still in flight, was told the same. **The CIO issued one starting number to two
parallel dispatches** — the same class of mistake as taking I-049 from Validation's range
during its outage. Collision will have to be resolved when Validation returns.

**8 · Suite deliberately NOT run, adopting the Director's reasoning.** Validation has two
untracked in-progress test files on disk (`harness/tests/test_tstat_hac.py`,
`test_cv_purge_embargo.py`); a run now would report on Validation's half-written work, not the
Director's. **`logs/ISSUE_LOG.md` is likewise NOT staged this commit** — Validation may be
appending to it, and staging a half-written entry is precisely I-054's failure mode. Named
paths only, and the risky path deliberately excluded.

**9 · Seal-readiness: NOT seal-ready, five blocking** — C2, C7, C8, C11 blocking now; C3
blocking at Gate 1. C12 **discharged narrowly** (cadence only; §7.1.1 now refuses in advance
any reading of `DATA-VERIFY-002` as evidence of no *parameter* break). **C13** new, folding
into C2's intake with three questions for Validation. **I-045 still not closed — the Director
correctly declined again.** *"R-002 created no blocker, discharged one, and still leaves the
document further from a comfortable seal than it found it."*

**10 · Budget.** 8 of 30 · 6 of 12 Opus, unchanged — R-002 was already counted. DA reserve 1.
Freely allocable Opus: **5.** §5 dead-man: **8 invocations remain** since the last checkpoint.

**Review date:** on the Principal's ruling on the KC-002 restatement.

---

## S2-D-012 · 2026-08-05 · Estimator spec lands · §4 HARD INTERRUPT — I-057 · numbering fixed

**1 · §4 HARD INTERRUPT FILED. Two triggers, one item:** *"any issue filed HIGH"* and *"any
finding by Validation… addressed to the Principal."* Filed separately from S2-D-011's
interrupt and **not batched with it**, per §8.

**I-057 — MinBTL and the Deflated Sharpe Ratio carry the identical serial-independence
defect I-050 identifies in the t-statistic.** Validation's finding, relayed as filed:
MinBTL counts observations; DSR's `z = (sr−sr₀)·√(T−1)/√denom` corrects for skew and
kurtosis and **for nothing serial**. Corrected, the admissible ceiling is **55 at ρ = 0.1,
31 at ρ = 0.2, 19 at ρ = 0.3, and 2 at ρ = 0.83**; RULING-004 §2.3's additive term 0.642
becomes **2.099** at ρ = 0.83 [all measured].

**Validation's own qualification travels with the number and the CIO relays it unsoftened:**
ρ here is the **net return series'** autocorrelation, *which the firm has never measured for
any family.* **The honest reading is not "the ceiling is 2" — it is "the ceiling is a
function of an unmeasured quantity and is below 109 at every ρ > 0."**

**Validation did not repair it, and said why:** out of scope for this dispatch, and grafting
a serial term onto DSR's published non-normality denominator is *a specification choice, not
a substitution.* **It timed the filing pre-seal deliberately** — the firm is days from
writing **109** into a sealed document as a maximum, under an assumption it has just formally
acknowledged its own data violates.

**2 · The answer to the CIO's added question: `N` = 109 does not move, and PREREG-002 can
seal on it without re-arithmetic.** `min_backtest_length_years` is a function of `N` and the
Sharpe only; nothing in the estimator spec touches that path. Validation reproduced 109 and
`MinBTL(86) = 6.1359` against the live harness [measured]. **But the second half of its
answer is I-057: 109 is not a conservative number and must stop being described as one.** The
question was asked to find out whether a first-order correction had a second-order
consequence. It did, and it is larger than the first-order one.

**3 · The corrected estimator makes the Principal's §8 asymmetry mechanical rather than
remembered.** `t` becomes Newey–West HAC on the sample mean, Bartlett kernel, autocovariances
divided by `T−1` so lag 0 reduces **exactly** to today's `sr_tstat`, Andrews (1991) AR(1)
plug-in truncation floored at `label_span − 1` and at any caller-stated lag as a **one-sided
max — a sponsor can raise it, never lower it** — and the graded figure taken as
**`min(t_NW, t_raw)`**, so **the change can never loosen.** The Principal's asymmetry ruling
is thereby enforced by construction rather than by a rule someone must remember to apply.
The CIO records this as the strongest single piece of design in the sprint.

**4 · Red by design, verified** [measured]: **26 failed, 162 passed.** 28 tests added, 26
failing. Two are deliberate guards that must stay **green** — `test_hac_t13` (E-1,
`sr_tstat` must not be mutated in place) and `test_hac_t14` (E-10, the uncorrected figure
must never acquire a verdict; implementing it as a `Criterion` row would fail every Gate
forever). **Floor rises 160 → 188** on implementation. `harness/castellan/` untouched;
registry 0/0. **This red state is the intended state under the Principal's red-first regime
and is not I-036.**

**5 · I-051 rode along, with a mitigation the CIO did not ask for.** Validation accepted the
bundling — same class, same files, and *"a serially-honest `t` computed on folds that are not
serially clean is half a repair"* — then **partitioned the tests into two files so the issues
close independently, and a failure on the MEDIUM item cannot hold the HIGH one hostage.**
That is a better answer than the CIO's brief allowed for.

**6 · I-058, LOW — Validation audited its own work of hours earlier and found it wrong.** Two
of its pre-authored acceptance tests in RULING-004 §11 were defective: a *correct*
implementation would have **failed ML-T-12** (Bartlett at lag 10 gives 0.4197 against an
asymptotic 0.3333 — 25.9% apart, outside its own 20% tolerance), and ML-T-11's third
assertion asserted a condition that is not leakage in an expanding window. Both corrected in
writing, **pre-implementation**, under the standing term that binds the author as hard as the
implementer. Combined with the Director finding ML-17's arithmetic defect at I-055, **the
independent gatekeeper's ruling has now been corrected twice in one day — once by another
seat and once by itself.**

**7 · CIO STRUCTURAL FIX — issue numbering. The collision is the CIO's and it has now
recurred five times** (I-013, I-041, I-054, plus the Director and Validation both being sent
to I-055 in parallel today). Validation states correctly that the structural fix is the
CIO's, not a seat's. **Effective immediately: the CIO allocates a disjoint, explicitly stated
issue-number range to every dispatch at dispatch time**, sized generously, and never reuses a
range or takes a number from a range already issued to a live seat. Seats continue to
re-check the high-water mark before appending — Validation did, which is why I-057/I-058 are
clean — but that is a seat's defence against a CIO error, not the fix.

**8 · Budget.** 8 of 30 · 6 of 12 Opus, unchanged — both dispatches already counted. DA
reserve 1. Freely allocable Opus: **5.** §5 dead-man: **8 invocations remain.**

**9 · Two interrupts now stand open** — S2-D-011's KC-002 restatement and this entry's
I-057. **Both block their own threads; unrelated work continues** (§4). The threads they
block are the same one: **the PREREG-002 seal**, which is Standing Order §1's first
objective. The CIO is not treating that as grounds to soften either filing.

**Review date:** on the Principal's rulings.

---

## S2-D-013 · 2026-08-05 · Both interrupts ruled · §10.4 seals a function, not a constant

**1 · Interrupt A APPROVED AND COUNTERSIGNED, and a standing principle issued.** The
Principal rules R9 the **KC-001 clause-3 precedent applied to KC-002**: one counting path,
owned by the registry's transitive summation, with `InheritedCountDoubleCountError`
enforcing what prose previously asserted.

> **STANDING, ALL KILL CONDITIONS: inheritance is computed, never re-declared.**

**This is firm-wide and outlives this family.** It is recorded here, and it needs to reach
`reference/GATES.md` and `reference/TEMPLATES.md` so a future pre-registration cannot
re-introduce the pattern by writing it fresh. **Not yet actioned — queued as a Sonnet
line-item.** Confirmed unedited: operative clauses (a)/(b)/(c), thresholds, 2027-01-31.

**2 · Interrupt B — I-057 APPROVED AS FILED, and Validation's qualification adopted
verbatim as the finding's meaning:** *"the ceiling is a function of an unmeasured quantity,
below 109 at every ρ > 0."*

**3 · THE SEALING RULING — §10.4 does not seal a constant.**

> **`N_max = min(109, corrected-MinBTL ceiling at ρ̂)`**, where ρ̂ is the family's net-return
> autocorrelation, **measured by the harness from logged trials at evaluation time.**

The Principal's own defence of why this is admissible: it is **monotone-conservative** —
measurement can only tighten, never loosen — so **it is not the I-029(d) operation**; it is
*"the `min(t_NW, t_raw)` construction extended to `N`."* The CIO records the symmetry
because it is the sprint's most reusable idea: **the firm has now twice solved a
"measurement could be gamed" problem by making the conservative direction the only
structurally available one**, rather than by writing a rule against gaming it.

**4 · Sequence ruled by the Principal, executed by the CIO.** Validation specifies the
corrected MinBTL/DSR serial treatment — *"it correctly declined to improvise one; the
deliberation is what the unit buys"* — same regime, **red-first, floor rises from 188**. The
Director **then** revises §10.4 to the functional form and sets the trial budget against a
**conservative ρ assumption stated in the document**, because *"burning `N` the measured
ceiling may disallow is the sponsor's risk to declare, not discover."*

**5 · The consequence, stated by the Principal pre-emptively and recorded so sprint close
inherits no surprise:**

> *"if ρ̂ measures ≥ 0.1, the admissible ceiling falls below the declared `N` = 86 and this
> family cannot clear Gate 1's length criterion on the data we hold. That outcome, should it
> arrive, is the machinery answering — a PARK or kill on measured ρ is a terminal verdict
> under §1, not a malfunction."*

**The CIO has written this into Validation's brief explicitly**, with the instruction that it
is *not* being asked for a specification that lets PREREG-002 survive: if the correct
treatment kills the firm's only family on the data it holds, specify it anyway and say so.
This is the §1 clause *"the goal is verdicts, not survivals"* under its first real test —
the first time this sprint that following the machinery may cost the firm its only asset.

**6 · Two dispatches, deliberately overlapping, with the collision managed rather than
avoided.**

- **Validation, Opus** — `VALIDATION-SPEC-002`, the corrected MinBTL/DSR serial treatment.
  Six things it must settle, of which the CIO judges two most likely to be gamed later:
  **how ρ̂ is estimated at zero, few, or unstable trials**, and **whether a family can become
  retroactively inadmissible** — the case the firm will actually hit. Monotone-conservatism
  must be **built into the construction and guarded by a test**, not stated as intent.
- **Seat 9, Sonnet** — implements `VALIDATION-SPEC-001`'s 26 clauses, floor **160 → 188**.

**These two run concurrently on the same directory on purpose**, because Seat 9's work is
gated only on SPEC-001 and waiting would idle it for an Opus deliberation. The collision is
handled by instruction rather than by sequencing: Seat 9 verifies against its **two named
test files** and reports whole-suite counts **separately with the caveat attached**;
Validation writes only into **new files** and is told not to read a moving suite count as a
signal about its own work. `[would-have-asked]`.

**7 · Two standing properties written into Seat 9's brief as inviolable**, above the tests
themselves: the graded figure is `min(t_NW, t_raw)` and the lag floor is a one-sided max, so
**an estimator change may tighten and never loosen** — and if the implementation admits any
path where the corrected statistic is *more* permissive, **it is wrong regardless of what the
tests say.** Also: `test_hac_t13` and `test_hac_t14` are green today and **a run that turns
those two red is worse than one leaving the other 26 red.**

**8 · The numbering fix is in force for the first time.** Validation holds **I-060–I-069**,
Seat 9 holds **I-070–I-079**, disjoint and stated at dispatch. I-059 reserved to the CIO.

**9 · Budget.** **10 of 30 · 7 of 12 Opus.** DA reserve 1. Freely allocable Opus: **4** —
enough for the Director's §10.4 revision, C2's intake verdict, and C3 on the reserve, with
nothing spare. **The sprint's Opus tier is now the binding constraint**, and two of the four
units it lost went to I-049's terminations.

**10 · §5 dead-man: 6 invocations remain** since the last Principal checkpoint.

**Review date:** on the return of SPEC-002 and the SPEC-001 implementation.

---

## S2-D-014 · 2026-08-05 · SPEC-001 implemented, I-051 closes · §4 INTERRUPT — I-049 → HIGH

**1 · §4 HARD INTERRUPT FILED. Trigger: *"any issue filed HIGH."*** **I-049 escalates
MEDIUM → HIGH on its own pre-committed trigger.** Third termination: `VALIDATION-SPEC-002`
died on `API Error: Response stalled mid-stream` after the seat reported *"Now §6 and §7."*

**The CIO declines the argument it would have been easiest to make.** The incremental-write
mitigation **worked** — 817 lines of clauses survived where the first two terminations
preserved nothing — and that is a live argument for a cheap resume and for leaving the
severity alone. **The trigger was written unconditionally on 2026-08-04 precisely so that the
third occurrence could not be argued down by whoever was mid-sprint and inconvenienced.** It
is reported as evidence, not as a severity argument.

**And HIGH is substantively right, not merely procedurally right.** Under §2, three failures
and two resumes = **5 Opus units for 2 complete artifacts and 1 partial**, against a tier of
12. **Freely allocable Opus is 4; committed remaining work is exactly 3** — the Director's
§10.4 revision, C2, C3. **A fourth termination puts the sprint into §2 budget exhaustion,
itself a §4 trigger.** The failure has stopped costing slack and started costing objectives.

**2 · What survived, measured.** §0–§5 complete: **M-1…M-14** (corrected MinBTL), **D-1…D-10**
(the DSR serial term — the specification choice the Principal funded), **R-1…** (ρ̂ and the
variance inflation factor), plus monotone-conservatism and evaluation-time semantics. **Lost:
§6–§13** — what survives of RULING-004's numbers, the consequence for PREREG-002, routing,
leakage audit, test inventory, issues, and whatever was addressed to the Principal. **No
clause lost. No test written** — SPEC-002's red-first tests do not exist.

**3 · Remedy proposed, not executed, because the interrupt is open.** Resume SPEC-002 **once**
to finish §6–§13 and author the tests, since 817 lines are on disk and a re-dispatch would
repay a read already bought. Then a standing design change for every subsequent Opus
dispatch: **split analysis and artifact-authoring into separate invocations**, the analysis
unit writing findings to disk before any synthesis begins. **The CIO does not implement this
while the interrupt is open.**

**4 · SPEC-001 IMPLEMENTED. I-051 CLOSES.** Seat 9 delivered against the red-first tests.
Verified independently [measured]: **1 failed, 187 passed = 188 total**, matching SPEC-001
§9's projection exactly. `test_cv_purge_embargo.py` **11/11 — I-051 closed.**
`test_tstat_hac.py` 16/17.

**Both guard tests still green** — `test_hac_t13`, `test_hac_t14`.

**Both inviolable properties verified by the seat directly, not inferred:** `t_gate =
min(t_nw, t_raw)` never violated across ρ ∈ {−0.6 … +0.8}, floor binding correctly on
negative ρ per E-8; the one-sided lag floor confirmed — a stated lag below the Andrews lag
cannot lower it, above it raises it. **The Principal's asymmetry is now mechanically true in
the harness, not merely specified.**

**5 · The single remaining failure is a test defect and Seat 9 did the right thing with it.**
`test_hac_t17`'s default bracket `(0, 2000)` bps/yr cannot reach its own assertion for **any**
correct estimator — both corrected and uncorrected hit the bracket ceiling. Seat 9 **filed it
(I-070, MEDIUM), left the test red, and did not route around it.** It was told the tests are
not its to change; it obeyed under the one circumstance where disobeying would have looked
like success. **None of the six named judgment-call clauses required routing back.** Registry
0/0 before and after.

**6 · Suite floor.** Baseline 160 → **188 total, 187 passing**, with one red pending
Validation's fix to its own fixture. **The floor does not rise to 188 until I-070 closes**;
the CIO records 187 as the operative floor in the interim rather than claiming the full rise.

**7 · Budget.** **10 of 30 · 7 of 12 Opus.** DA reserve 1. **Freely allocable Opus: 4, against
3 committed.** §5 dead-man: **6 invocations remain.**

**Review date:** on the Principal's ruling on I-049.

---

## S2-D-015 · 2026-08-06 · I-049 HIGH sustained · dispatch practice changed · contingency ruled

**1 · HIGH sustained, remedy approved as proposed.** SPEC-002 resumed **once** — the single
authorized resume — scoped to §6–§13 and the tests, with §0–§5 explicitly not to be
rewritten. The Principal noted the CIO's refusal of the easy severity argument for the §7
audit in the favourable direction; recorded here without further comment, since a seat
grading its own conduct is worth nothing.

**2 · STANDING DISPATCH PRACTICE, effective for all Opus units this sprint — not merely
subsequent ones.** **Analysis writes to disk before synthesis begins**, so a termination costs
one section and never a read. The resume itself conforms naturally: §0–§5 *is* the analysis,
already on disk, and the resumed unit is the authoring half.

**3 · Two mechanical mitigations authorized, and the CIO can execute only one of them.**

- **(1) Pre-dispatch headroom check via `/usage`.** *The CIO cannot perform this.* `/usage` is
  an interactive client command; no tool available to this seat invokes it, and there is no
  API surface for session headroom. **This mitigation is unimplemented and will stay
  unimplemented until the Principal runs `/usage` himself before an Opus dispatch, or
  supplies another signal.** Recorded as a gap rather than reported as adopted — an
  authorized control the firm believes is running and is not is the I-046 failure in a new
  costume.
- **(2) Pre-split at ~800 projected lines, priced as two.** **This one the CIO owns and it is
  in force.** Applied immediately: SPEC-002's remaining work — six tail sections plus test
  files — projects well under the threshold, so it went as a single invocation, and the
  reasoning was stated in the brief rather than left implicit.

**4 · D-012 stands. Every termination counts as spent, and no exception is created by the
escalation.** The CIO notes the trap the Principal closed: an escalation that *also* refunded
its own cost would make filing HIGH profitable, and a control that pays the filer is not a
control. Budget after the resume: **11 of 30 · 8 of 12 Opus.** DA reserve 1 sealed. **Freely
allocable Opus: 3, against 2 committed** (Director's §10.4 revision, C2's intake verdict).
**One unit spare.**

**5 · CONTINGENCY RULED IN ADVANCE, so budget exhaustion cannot improvise.** If a fourth
termination lands and free Opus falls below committed work, the sequence re-prioritizes to
**SPEC-002 completion → Director §10.4 revision → C2**, with **C3's reserve remaining
sealed.**

> **The Red-Team memo is submission-gated and is not skippable. No Gate 1 submission occurs
> this sprint without it. If the budget cannot reach C3, the seal moves to Sprint 3 rather
> than the memo being dropped.**

The Principal's reasoning, recorded because it settles a class of future arguments and not
just this one: *"A slipped seal is Ruling 001's lesson; a skipped red-team is Appendix B's."*
**The schedule is the thing that yields. The adversarial check is not.** This closes the
route by which a sprint deadline becomes an argument for thinner scrutiny — the route every
firm of this kind eventually finds.

**6 · What this means for §1's first objective, stated plainly.** PREREG-002 **sealed and
executing** is now conditional on a chain of four things landing inside the remaining budget:
SPEC-002's completion, the Director's §10.4 functional-form revision, C2's intake verdict,
and C3's Red-Team memo. **The CIO's honest assessment is that the seal is more likely to slip
to Sprint 3 than to land**, and under §5's contingency that is the ruled outcome rather than
a failure. Recorded now, not at sprint close.

**7 · §5 dead-man: 6 invocations remain** since the last Principal checkpoint, which this
ruling resets.

**Review date:** superseded by S2-D-017.

---

## S2-D-016 · 2026-08-06 · Headroom control replaced with readable signals · Rider B dispatched

**1 · The unimplementable control is retracted and replaced.** The Principal retracted the
`/usage` headroom check as specified and confirmed the CIO was right to file it
unimplementable rather than report it adopted. **The replacement uses signals each party can
actually read**, which is the correct fix for a control that failed because it assumed a
capability nobody checked for.

**2 · Principal-supplied headroom, in force.** Every Principal message now opens with
`[usage: session X% · weekly-opus Y%]`, read from `/usage` at send time. **First reading,
2026-08-06: `session 24% · weekly-opus 12%`.** Recorded with the message it arrived on,
because the whole point of the signal is that it is timestamped.

**3 · Staleness rule, in force.** A headroom note **older than ~2 hours**, or **any
termination since it arrived**, means headroom is **unknown**, and the conservative posture
applies: pre-split (already in force), incremental writes (already in force), and **no second
long Opus dispatch inside the same window after a termination** — queued for the Principal's
next contact instead.

**Current status against the rule: headroom is KNOWN and healthy.** The note is minutes old,
and the third termination occurred *before* it arrived, not since. The conservative posture is
therefore **not** triggered — and the CIO records that reading explicitly rather than
silently, because the rule's two clauses could be read to strand the firm permanently after
any termination, and they do not.

**4 · No Opus dispatch was launched anyway, for a different reason.** Both remaining Opus
items are **dependency-blocked, not budget-blocked**: the Director's §10.4 revision waits on
SPEC-002's completion by the Principal's own sequencing, and C2 waits behind that so
Validation does not rule on a document carrying a superseded ceiling form. **Healthy headroom
does not create work that the sequence does not yet permit**, and the CIO is not going to
spend a scarce Opus unit early merely because the window is open.

**5 · Rider B dispatched instead — Sonnet, and therefore untouched by the constrained tier.**
It has been outstanding since S2-D-001 and is the firm's **largest un-actioned data-loss
exposure**: `book/pit.db` at 61.1 MB / 710 documents / 365,465 observations, holding the
Polymarket capture that **cannot be reproduced after the fact**, with a backup regime that is
*currently manual to iCloud* — which is to say, dependent on somebody remembering.

Four requirements, of which the CIO judges two decisive: **a snapshot must be restore-verified
as routine**, because a backup nobody has restored is a hypothesis rather than a backup; and
**failure must surface loudly within a week**, because silent backup failure is worse than no
backup — it buys false confidence. The brief also requires the seat to **re-derive the growth
rate rather than trust the CIO's restatement of its own earlier figure.**

**D-003's policy binds the design**: `crontab` and `launchctl` are denied, so the seat
**cannot install a schedule** and is told not to route around it. It delivers scripts and a
`[PRINCIPAL]`-marked runbook. **Rider A's approved $6.00/month VPS cutover also remains
unexecuted**, so the brief requires the snapshot regime's interaction with that migration to
be stated rather than discovered.

**6 · Budget.** **12 of 30 · 8 of 12 Opus** — Rider B is Sonnet. DA reserve 1 sealed. Freely
allocable Opus: **3, against 2 committed.** §5 dead-man: 6 invocations remain since this
checkpoint.

**7 · Still queued, not forgotten:** the standing principle *"inheritance is computed, never
re-declared"* into `reference/GATES.md` and `reference/TEMPLATES.md`; **I-056**'s ML-2 block
for PREREG-001 and the pre-registration template; **Rider C**'s casebook harvest at sprint
close. All three are doc work and none is dispatchable into Seat 9 while Rider B holds it.

**Review date:** on SPEC-002's completion.

---

## S2-D-017 · 2026-08-06 · SPEC-002 complete · I-050 CLOSES · §4 INTERRUPTS — I-060 and §13

**1 · §4 HARD INTERRUPT — I-060, HIGH.** *"Ruling 004's mandatory diagnostics and the
corrected MinBTL ceiling are mutually unsatisfiable"* above a threshold. Validation's finding
as filed: **ML-3's obligation stack exceeds the ceiling at ρ̂ > 0.045**, at which point
RULING-004's *"roughly thirty configurations of genuine search"* **reaches zero**; and the
ML-16 dispersion sample **alone** is inadmissible above ρ̂ = 0.197. The firm's ML frontier,
described one day ago as small-search, may be empty on the data it holds.

**2 · §4 HARD INTERRUPT — §13, three findings addressed to the Principal.** Relayed
unbatched and unsoftened per §8.

**(a) Validation tightened the Principal's own number, and says so.** *"Your I-057 trigger is
loose by ~3× and I tightened it under the I-050 asymmetry rather than requesting an act."*
The Principal stated at S2-D-013 that ρ̂ ≥ 0.1 breaks the family. **Validation's clauses put
the binding threshold at ρ̂ ≈ 0.034.** Under the asymmetry the Principal himself wrote into
§8 — corrections *toward* a stated assumption are Validation's and need no Principal act —
this is exactly correct procedure. **It is recorded prominently anyway, because a seat
silently tightening a Principal's stated figure by 3× is precisely the class of act that
should never pass unremarked, even when it is authorized.**

**(b)** *"This specification probably kills the firm's only family and I built in no margin
to avoid that"* — choosing at **M-12/M-13** the estimator that **reproduces the Principal's
ruled numbers over the one more favourable to the family.** Presented with the choice named
and the discarded alternative identified.

**(c)** R-3/D-6 are one-sided floors **only the Principal can remove**, which Validation is
**not** asking him to.

**3 · I-050 CLOSES. I-070 CLOSES.** `test_tstat_hac.py` **17/17**, verified independently.
The defect in `test_hac_t17` was Validation's own draft — `mu=0.0035, sd=0.01` against a
`(0, 2000)` bps/yr bracket, moving the corrected `t` only 6.488 → 5.788, *"no correct
estimator could satisfy it, exactly as Seat 9 found."* **The repair is not the fixture.** The
seat added **interiority assertions on both returned values**, on the reasoning that *a
bisection returning a bracket endpoint has measured nothing, and its absence is what hid the
defect.* It also caught a **second** defective tolerance of its own (`test_vif_04` asserting
`vif_hac > 1.5` where correct code gives 1.4256).

**Three of the firm's own controls have now been found defective by the seat that wrote
them**, pre-implementation, in two days.

**4 · Verdict bands pre-committed before the measurement exists** — §7.4:

| ρ̂ | Outcome |
|---|---|
| ≤ 0.034 | passes |
| 0.034 – 0.15 | **FAIL-on-length**, repairable by ≤ 11 months more history → **PARK** |
| > 0.30 | **kill** |

**And the escape route is closed by construction:** *"the Sharpe route is trapped — raising
realized Sharpe by searching raises `N`, which raises the requirement."* This is the third
time this sprint a gaming path has been shut by making the conservative direction the only
structurally available one.

**5 · RULING-004 partially falsified by its own author.** §2.1's frequency-invariance
conclusion was **false** under the uncorrected statistic — **4.5× permissive** (I-061). `N` =
109 and §2.3's 0.642 survive only as the **`VIF = 1` slice**. §2.4's `m ≥ 32` collides with
the ceiling. Two findings survive verbatim, including the σ_SR-vs-`N` result. **22 documents
checked for contradiction; none found.**

**6 · Verified independently of the seat's report** [measured]: suite **42 failed, 192 passed
= 234**, red by design; `harness/castellan/` untouched; registry **0 hypotheses / 0 trials**;
`book/vaults/` holds only `.gitkeep`. On the leakage audit — Validation's claim is precisely
scoped and the CIO restates it precisely: *`HoldoutVault.open_once` was not invoked, no vault
read, listed or decrypted, no passphrase requested or held.* **"LOCKED, unopened, unretired"
describes the seat's conduct, not the existence of a sealed payload** — under P-1 no payload
exists before Gate 1, and with 0 hypotheses no holdout specification has been sealed either.
`prereg_sha256` untouched; `verify_prereg` returns `match=True` before and after.

**7 · The numbering fix worked.** *"First dispatch this sprint with no collision."* Five of
ten allocated numbers spent, none outside range.

**8 · Floors.** SPEC-001's floor is now fully realized at **188** with I-070 closed. **234
after SPEC-002 is implemented.** `test_monotone_conservatism.py` is flagged by its author as
**not partitionable — I-057 stays open without it**, so the seven tests in that file are the
gate on I-057's closure, not an optional extra.

**9 · Nothing Opus dispatched, and the reason is the interrupt, not the budget.** The
Director's §10.4 revision came unblocked when SPEC-002 landed — **but §13(a) changes the
number the Director must write into it**, from the Principal's 0.1 to Validation's 0.034.
Dispatching now would spend a scarce unit writing a threshold the Principal has not yet seen
contradicted. Same thread as the interrupt; it queues. **SPEC-002's implementation (42 red
tests) is Sonnet and is queued behind Rider B**, which holds Seat 9.

**10 · Budget.** **12 of 30 · 8 of 12 Opus.** DA reserve 1 sealed. Freely allocable Opus:
**3, against 2 committed** (Director §10.4, C2). §5 dead-man: **5 invocations remain.**

**Review date:** on the Principal's rulings on I-060 and §13.

---

## S2-D-018 · 2026-08-06 · Rider B delivered · SPEC-002 implementation dispatched

**1 · Rider B complete. No issue above MEDIUM, so no interrupt.** Verified independently
[measured]: suite **42 failed, 204 passed, 246 total**; the five protected `harness/castellan/`
files **untouched**; severities on disk 3 MEDIUM / 1 LOW as reported.

**2 · The requirement the CIO called decisive was actually met, not merely designed.** Restore
verification is **unconditional and inside the same invocation that creates the snapshot** —
decompress, `PRAGMA integrity_check`, row-count match against counts recorded at backup time
— and was **proven live this session against a full 68.5 MB scratch copy of the real
`book/pit.db`, end to end in ~3 seconds.** *A backup nobody has restored is a hypothesis;
this one has been restored.*

**3 · Failure surfacing.** Any failure preserves prior good snapshots untouched, writes a
status file that **carries `last_success` forward across failures**, appends to a failure log,
and exits nonzero; `check_snapshot_health.py` flags staleness > 30h or a failed last attempt.
At daily cadence that surfaces **same-day**, well inside the one-week bar. The seat
**recommended** an integration point at Ops's Close & Reconcile and **declined to assign it**,
correctly — that is a CIO/Ops call. **Taken: the CIO assigns it, and it is queued with the
other Ops line-items rather than actioned now.**

**4 · The seat re-derived rather than trusting the CIO's restatement, and the figure moved.**
Measured growth **35.93 MB/day** against `DATA-INFRA-002`'s cited 32.64 — **+10.1%** — which
revises the VPS runway **21.1 → 19.2 months** (I-073). The brief required re-derivation
specifically to catch this, and it caught it. Retention: 7 daily snapshots × 3 databases = 21
files, ≈69 MB today, ≈157 MB once the approved VPS cutover reaches full cadence, against 1.6 TB
free.

**5 · Registry and book included, defended rather than assumed.** *"A2 makes the registry
load-bearing and uncommitted mid-session state is lost identically regardless of file size"* —
< 2 KB compressed, < 1 s added. Git stays their primary book of record under A3; this is a
cheap, session-boundary-independent second.

**6 · I-072 is the CIO's error and the seat was right to file it.** The Rider B brief quoted a
baseline of *"1 failed, 187 passed of 188"* that was **stale by the time the seat ran** —
Validation's SPEC-002 tests landed in between, moving the suite to 246 total. **This is the
direct cost of running concurrent dispatches with a stated baseline.** Corrective applied
immediately: **the S2-D-018 brief carries a baseline re-measured seconds before dispatch, with
the reason for the re-measurement stated in the brief itself.**

**7 · Two gaps carried, not closed.** **I-071** — the backup exposure was *disclosed twice and
never logged* until now, and stays open until the regime is actually installed; **6 of 9
runbook steps are `[PRINCIPAL]`** because `crontab`/`launchctl` are denied under D-003, so the
firm's backup regime remains uninstalled and dependent on the Principal's hands. **I-074** —
the VPS's capture-only `pit_capture.db` has **no backup coverage between merges**, a
pre-existing gap re-confirmed and explicitly not closed by this dispatch.

**8 · SPEC-002's implementation dispatched to Seat 9 — Sonnet — and the CIO records this as a
scope judgment the Principal can reverse.** `[would-have-asked]`.

**The question:** §13's three findings are addressed to the Principal and therefore interrupt
under §4; does that interrupt block *implementing* SPEC-002's clauses?

**The CIO's judgment: no, and the reasoning is on the record so it can be overruled cheaply.**
§13(a) *reports* a tightening already made under Validation's standing authority — the §8
asymmetry the Principal wrote — rather than requesting an act. §13(b) discloses a choice
already made. §13(c) explicitly declines to ask for anything. **None of the three holds the
clauses in abeyance; they are binding now.** Against that: **`test_monotone_conservatism.py` is
the gate on closing I-057, a HIGH the Principal has already approved**, and holding would leave
an approved HIGH open for no gain. **If the Principal overrules the 0.034 tightening, the
rework costs one Sonnet unit** — the unconstrained tier, not the Opus tier.

**What the CIO did NOT dispatch on the same reasoning:** the Director's §10.4 revision, which
**writes the threshold itself** and would be spending a scarce Opus unit on a number the
Principal has not yet seen contradicted. That one genuinely is the same thread. **The
distinction is between implementing binding clauses and authoring a figure under dispute.**

**9 · Budget.** **13 of 30 · 8 of 12 Opus** — S2-D-018 is Sonnet. DA reserve 1 sealed. Freely
allocable Opus: **3, against 2 committed.** §5 dead-man: **4 invocations remain.**

**10 · Queue, unchanged and lengthening:** *"inheritance is computed, never re-declared"* into
`reference/GATES.md` and `reference/TEMPLATES.md`; **I-056**'s ML-2 block for PREREG-001 and the
template; the snapshot health check into Close & Reconcile; **Rider C**'s casebook harvest;
**Rider A**'s approved-but-unexecuted $6.00/month VPS cutover.

**Review date:** on the Principal's rulings on I-060 and §13.

---

## S2-D-019 · 2026-08-06 · SPEC-002 implemented, 42 reds → 7 · §4 INTERRUPT — three HIGH · dead-man count corrected

**1 · §4 HARD INTERRUPT. Trigger: *"any issue filed HIGH"* — three of them, presented
separately per §8.**

**I-075 · HIGH — two of SPEC-002's own Gate 1 integration tests grade the wrong family.**
`test_mbs_10` and `test_dsr_07` grade an **unseeded** family (`"hac"`) instead of the one
actually seeded (`"F"`). Seat 9 **verified by substitution that the arithmetic is correct once
the right family is used** — so the implementation is right and the tests are wrong. **Blocks
I-057 Items 1/2 from closing under the spec's own partition rule.**

**I-077 · HIGH — `test_mono_03`, the structural test, fails on an exact-equality
sub-assertion.** D-2's literal `z_serial = z_iid/√vif` does not reduce exactly at an
**estimator-unreachable input** (`vif = 0.25`, below R-2/R-7's own 1.0 floor) with a negative-z
fixture. **The actual monotone-conservatism inequality (C-1(iii)) holds unconditionally by
construction of `min()`** — what is missing is a stronger, un-stated exact-equality guarantee.

**I-078 · HIGH — SPEC-002's mandatory renames and M-7's blanket rule structurally conflict
with eight pre-existing protected tests.** Seat 9 reverted the renames at zero cost, saving
six. **Three are genuine casualties and are now failing: `test_G2` (holdout calendar span),
`test_h7`, `test_h8` (seeded denominator).** Verified independently.

**The CIO flags what Seat 9 could not decide for itself: accepting three previously-green
protected tests as "unavoidable consequences of correctly implementing the spec" is a
Validation judgment, not an implementer's.** Seat 9 filed it HIGH rather than absorbing it,
which is the correct disposal — but the acceptance itself needs Validation's ruling, and until
it comes **the firm's green floor has fallen by three tests it previously held.**

**2 · THE FINDING THE CIO RATES ABOVE ALL THE ARITHMETIC.** Seat 9 **found a construction that
would have made every one of the 46 tests pass with zero collateral** — `z_serial =
z_iid/√(max(vif, 1.0))`, the direct arithmetic analogue of M-2's own `max` — **and deliberately
did not adopt it**, because D-2 is classified mechanical/no-consultation and *"adopting an
un-authorized construction to force green is exactly what this dispatch told me not to do a
second time."*

**It had the fix in hand, it was almost certainly right, and it filed an issue instead.** This
is the second time this seat has left a red test red under the one circumstance where routing
around would have looked like success. **A full-green report was available and was declined.**
Recorded at length because the §7 audit should weigh it, and because a firm that only notices
this behaviour when it fails has learned nothing.

**3 · Results, verified independently** [measured]: **239 passed, 7 failed, 246 total**, from a
baseline of 204/42. All **four guards still green** (`test_mbs_05`, `test_mbs_13`,
`test_vif_16`, `test_dsr_02`). Registry **0 hypotheses / 0 trials**; `book/vaults/` holds only
`.gitkeep`; **no test file modified.**

**4 · I-057 DOES NOT CLOSE, and the seat said so plainly.** `test_monotone_conservatism.py` is
**6/7**, and the file is non-partitionable by its author's own §11.3. *"I am stating this
plainly rather than reporting a partial result as success."*

**5 · Monotone-conservatism verified by direct sweep, not inference** — as the brief required.
**145 draws for `N_max`** (the ceiling never rises above the VIF = 1 default) and **900 draws
for DSR** (`DSR_serial ≤ DSR_iid`) across ρ ∈ [−0.6, +0.8], using **real measured VIFs, never
adversarially injected** — **zero violations in both.** `variance_inflation` additionally
reproduces SPEC-001's M-12 HAC/AR(1) reference table to 3 d.p. **The Principal's ruling that
the sealing form cannot loosen is now empirically demonstrated, not merely specified.**

**6 · Routed back rather than decided: R-16 only** (`test_mbs_12`'s 20% band missed by one draw
of nine, 25.4% vs 1.20 — filed I-076 MEDIUM, not adjusted). R-10 touched but not hit. M-13,
M-14, D-4, R-9, R-12, V-6/V-7 untriggered at 0 trials. One item **outside** the eight was
surfaced rather than decided — D-2's exact-equality gap, I-077.

**7 · CORRECTION — the CIO has been reporting the §5 dead-man count wrong.** Recomputed
[measured]: the last Principal checkpoint was the `/usage` ruling, at which the firm stood at
**11 of 30**. Two invocations have been spent since — Rider B and the SPEC-002 implementation.
**The correct figure is 8 invocations remaining, not the 4 reported at S2-D-018 or the 5 at
S2-D-017.** The CIO was counting from a stale checkpoint. **The error ran in the conservative
direction and is still an error**, and it understated the firm's runway in reports the
Principal was using to sequence work. Corrected here rather than quietly adjusted.

**8 · Budget.** **13 of 30 · 8 of 12 Opus.** DA reserve 1 sealed. Freely allocable Opus: **3,
against 2 committed** (Director §10.4, C2). §5 dead-man: **8 invocations remain.**

**Review date:** on the Principal's rulings on I-060, §13, and the three HIGHs above.

---

## S2-D-020 · 2026-08-06 · Four interrupts ruled · last Opus slack spent · two dispatches

**Headroom at ruling: `session 19% · weekly-opus 15%`**, fresh, no termination since it
arrived — the staleness rule's conservative posture is **not** triggered, and that reading is
recorded rather than assumed.

**1 · I-060 — recorded as a finding, reconciliation DEFERRED to Sprint 3, strict reading
governs.** The Principal's framing, offered as non-binding input: the live question is whether
**pre-declared, unconditional diagnostics constitute selection** (and burn `N`) **or
measurement** (fixed obligations, no degrees of freedom, hence no argmax to correct for). The
collision is between two artifacts of the same author and its reconciliation is Validation's.

**Nothing operational blocks**: no ML family exists and **none may register until the
reconciliation lands.** Until then **diagnostics count toward `N`.** And the sentence that
matters most:

> *"if reconciliation confirms mutual unsatisfiability, 'the ML frontier is empty on the data
> we hold' is recorded as an honest finding, not routed around."*

**2 · §13(a) COUNTERSIGNED. 0.034 supersedes 0.1 on the record.** *"My number was a
prediction, Validation's is a derivation."* The tightening required no act under the asymmetry —
as designed. On the CIO having surfaced it prominently anyway: *"the right instinct;
**authorized silence is still silence.**"* **The Director's §10.4 revision writes against
0.034.**

**§13(b) acknowledged** — choosing the estimator that reproduces ruled numbers over the
family-favourable one, with the discarded alternative named, *"is the conduct the order selects
for."* **§13(c) — R-3/D-6 floors stand, no removal.**

**3 · I-075/077/078 and the declined construction — batched into ONE Validation invocation**,
funded from the sprint's last spare Opus unit. All four are Validation-judgment by
construction. On the fourth, the Principal's ruling is the sharp one:

> *"the seat was right that adoption is not the implementer's act, **which is not a finding
> that the construction is wrong.**"*

**The procedural question is settled and the substantive one is open.** The CIO's brief tells
Validation that a construction making every test pass *"deserves suspicion rather than
gratitude"* — and that if it is correct, to say plainly that an implementer found a defect in
the specification and correctly declined to fix it unilaterally.

On I-078 the Principal requires **written justification per test** that each protected property
survives or is superseded — **not a blanket acceptance.** *"Until ruled, the green floor is
honestly three lower."*

**4 · Budget consequence, ruled in advance.** This spends the last slack. **Any further
termination triggers the exhaustion contingency as already ruled: seal to Sprint 3, DA reserve
sealed, no red-team skipped.** Both briefs state this to the seat, so each works knowing what
its own failure costs.

**5 · Two dispatches, parallel, and the CIO records why parallel rather than serial.** The
staleness rule permits it — headroom fresh, no termination since. Sequencing would cost a full
wall-clock cycle with the sprint closing on the 11th. Against that, two concurrent Opus units
double the single-window exposure at exactly the moment slack reaches zero. **The CIO judged
wall-clock the binding constraint and takes the exposure.** `[would-have-asked]`.

**Pre-split judgment stated explicitly rather than left implicit**, per the Principal's rule:
the CIO judges the Validation adjudication **under the ~800-line threshold** — four focused
rulings plus three per-test justifications, not a specification — and sent it as one unit,
**instructing the seat to stop and say so rather than truncate if that judgment is wrong.**
Pre-splitting would have cost two units, which the sprint does not have; **saying so is better
than discovering it.**

**6 · Dead-man miscount — acknowledged, no act follows.** The Principal: *"the conservative
direction doesn't make misstating runway harmless, and saying so unprompted is why no act
follows."*

**7 · The SPEC-002 implementation `[would-have-asked]` — NOT reversed.** The
implementing-binding-clauses versus authoring-disputed-numbers distinction *"reads sound, and
it will be graded where it belongs, at the §7 audit."*

**8 · Budget.** **15 of 30 · 10 of 12 Opus.** Remaining Opus: **2 — C2's intake verdict and the
sealed DA reserve. Zero slack.** §5 dead-man: **8 invocations remain**, on the corrected count.

**Review date:** on the return of R-003 and RULING-005.

---

## S2-D-021 · 2026-08-06 · RULING-005 · the declined construction is ADOPTED · §4 INTERRUPT

**1 · §4 HARD INTERRUPT. Two triggers: *"any issue filed HIGH"* (I-065) and *"any finding by
Validation addressed to the Principal"* (RULING-005 §9).**

**I-065 · HIGH — D-2 as Validation wrote it violates Validation's own C-1(iv).** Over **200,000
draws** [measured]: the literal form produces **3,848 violations** — `DSR_serial` **rising**
with `vif`, i.e. *more measured serial dependence producing a more permissive statistic*,
inside the clause written to prevent exactly that. The clamped form produces **zero**.

A violating draw, quoted: `z = −0.0500`, `vif` raised `0.591 → 12.376`, `DSR_serial` rises
`0.4741 → 0.4801`. **Mechanism: for `z < 0` and `vif < 1`, `z/√vif` is more negative, so the
`min` selects the serial branch, which is increasing in `vif` across `(0,1)`. The literal form
is not conservative below 1 — it is sign-dependent.**

**2 · SEAT 9 WAS RIGHT, AND THE CONSTRUCTION IS ADOPTED.** Validation tested it *"as something
to be suspicious of, not grateful for"* — the disposition the CIO's brief asked for — and it
survived. Measured further: the two constructions are **bit-identical for every `vif ≥ 1`**
(max diff `0.000e+00`), the entire region R-7's floor permits, **so the amendment changes no
live Gate number, ever.** And M-2 already *was* the clamp; **D-2 was the odd one out among the
three corrections C-5 claims are one construction.**

Validation asked that this be recorded in its own voice, and the CIO records it verbatim in
substance: *"An implementer found a defect in my specification and correctly declined to fix it
unilaterally. The value of a pre-authored test regime is destroyed the first time an implementer
amends the spec to make tests pass — especially when the implementer is right."*

**Root cause filed against itself**: `test_mono_05` sweeps `vif ∈ (0,50]` but carries C-1(iv)
only on the MinBTL side, leaving the DSR side unswept below 1.

**3 · I-077 ruled REQUIRED, not overreach — and the reasoning inverts the CIO's expectation.**
C-3 injects an estimator-unreachable `vif` *precisely so* the consumer-layer guarantee is
verified independently of the estimator; a guarantee holding only on inputs R-7 already filtered
**collapses C-2's two enforcement layers into one while the document claims two.** Further,
C-1(iii)+(iv)+D-5 together *force* exact equality on `vif ∈ (0,1]` — **the assertion is a
theorem of C-1, not an extra demand.**

**4 · I-078 ruled per test. The Principal's instrument was the right one and here is what it
caught.**

| Test | Disposition |
|---|---|
| `test_G2` | Survives on **2 of 3** sub-assertions exactly. Third **deliberately superseded**: the old code *PASSED* a zero-trial family at an implied VIF = 1, violating Validation's own never-PASS-on-unknown-`N` rule. **M-7 upheld, no zero-trial carve-out.** Assertion kept, not deleted — the fixture logs a trial. |
| `test_h8` | **Survives intact.** At VIF = 10.647: FAIL→FAIL, PASS→PASS. **Both verdicts unchanged**; two VIF = 1 literals superseded. |
| `test_h7` | **Property survives; coverage GENUINELY LOST.** Both families now FAIL, destroying the only test proving a seeded denominator can flip a DSR verdict. **Must be rebuilt, not accepted.** |

> *"A blanket acceptance would have quietly cost the firm the `test_h7` guarantee. That is why
> the Principal's per-test requirement was the right instrument."*

**5 · A fifth item Item 1 forced open, and the CIO notes the chain.** With the family corrected,
both tests then failed on the M-6/D-8 **rename** — which Seat 9 had reverted *on the argument
that it bought nothing because these tests failed anyway.* **That premise died with I-075.**
Rename **RESCINDED** (I-066), and Validation replaced name-substring assertions with assertions
on what is *graded* — **strictly stronger, since a substring cannot detect a correctly-renamed
criterion graded on the wrong number.**

**6 · I-067 is the one the CIO rates as most likely to spread.** `_calibrated_returns` **does
not do what its docstring claims** — `np.argsort` is not stable; it emits `ρ̂ ≈ +0.55`, VIF
10.6–12.6. **It is the fixture that produced a false casualty**, and *"every other consumer of
it needs checking."* This is a defective generator sitting underneath an unknown number of
tests, and **it is why the CIO is not dispatching the fixture rebuilds yet** — see §9.

**7 · I-076 deliberately NOT adjudicated, and the refusal is the finding.** The remedy on offer
was widening an `[inferred]` 20% band to 26% **after** measuring a 25.4% miss — *"an
adjust-the-threshold-to-fit-the-result operation on its face."* It may still be right, but it
needs the band re-derived from something other than the observed miss. *"It does not get decided
as a footnote."*

**8 · Verified independently** [measured]: suite **241 passed / 5 failed / 246**, up from 239/7.
`harness/castellan/` **untouched — the one-liner is not yet applied.** Registry **0 hypotheses /
0 trials**; `book/vaults/` holds only `.gitkeep`. `test_dsr_serial.py` now **10/10**.

**I-057 does NOT close.** `test_monotone_conservatism.py` is non-partitionable and `test_mono_03`
is red; `test_minbtl_serial.py` is independently red on `test_mbs_12`.

**9 · NOTHING DISPATCHED, and the reason is substantive rather than procedural.** The remaining
work is one Seat 9 one-liner plus three fixture rebuilds. The one-liner is mechanical. **The
fixture rebuilds are not, because I-067 says the fixture generator itself is defective** —
rebuilding `test_h7` on `_calibrated_returns` would rebuild it on the thing that broke it. The
CIO is not spending a unit to do that. **Held for the Principal**, with the scope question
attached: I-067's blast radius is unknown and *"every other consumer needs checking"* is not a
task anyone has been funded to do.

**10 · Budget.** **15 of 30 · 10 of 12 Opus.** Remaining Opus: **2 — C2's intake verdict and the
sealed DA reserve. Zero slack**, as ruled. Sonnet remains available. §5 dead-man: **8
invocations remain.**

**Review date:** on the Principal's ruling on I-065 and §9.

---

## S2-D-022 · 2026-08-06 · R-003 delivered · §4 INTERRUPT — I-022 escalated by the CIO

**1 · R-003 delivered. No HIGH filed by the Director** — I-080, I-081 MEDIUM, I-082 LOW,
verified on disk. Registry **0 hypotheses / 0 trials**; **no `harness/` file touched by the
Director**; PREREG-002 now 2,545 lines.

**The functional form as sealed:**
`N_max = min(109, max_admissible_trials(span, SR_realized, ppy, vif = VIF_gate(ρ̂)))` — and
**109 is not a constant but `max_admissible_trials(6.571, 1.0, vif = 1.0)`, the first argument
of a `min`.** Written against **0.034** throughout. `0.10` survives in the document exactly once
more and **explicitly not as a threshold.**

**2 · The finding the CIO rates highest in this dispatch: R-002's budget was set against ρ = 0
by silence, and sat at 86 = `N_max(0.034)` — zero trials of margin at its own binding
threshold.** Nobody had noticed, because a budget set by silence looks like a budget.

**The Director rebuilt it and took a voluntary 40% cut to authorized `N`:** Stage 1 **47
authorized**; Stage 2 **≤32 declared and NOT authorized**, unlocked only by measured ρ̂ read from
a cited table, reaching the old 79/86 only at ρ̂ ≤ 0.034.

The decisive argument for staging over a flat cut, recorded because it generalizes: **"a PARK
that keeps burning `N` is not a PARK."** Under a flat budget, a family parked at ρ̂ = 0.10 would
spend 22 forward-window trials while waiting for the ≤11 months of history that is its only
remedy — **raising `N`, raising MinBTL, digging its own hole while waiting in it.**

**3 · The conservative ρ, and the reason stated against the family.** `ρ_plan = 0.10`,
`N_max = 55`. Four reasons at §10.5.1, of which the fourth is the Director's own judgment marked
`[inferred]` and pointed against its own family: **this position is delta-neutral by
construction, so the near-independent price-return component SPEC-002 §7.5 relies on to dilute
ρ̂ is exactly the component this family hedges out on purpose.** ρ̂ should therefore be expected
in the **upper half** of the cited [0.0, 0.5] interval. *"That is reasoning, not measurement, and
it does not narrow the interval."*

**4 · I-060 checked choice by choice, and the answer is two-part.** As a **clause** it does not
bite — ML-16 sits inside ML-3–ML-27, which reach only fitted families. The family also gets
ML-16's statistical content **free**: 25 grid points + ≥10 walk-forward refits = **35 series at
Stage 1**, above Ruling 004 §2.4's `m ≥ 32` floor, at **zero incremental `N`.**

**But its *content* reaches PREREG-002 at ρ̂ > 0.034 — one notch tighter than I-060's own
0.045.** *"Not being fitted does not exempt it."* The Director looked for an exception and
reported there is none.

**5 · §4 HARD INTERRUPT — I-022 escalated MEDIUM → HIGH by the CIO under §8.** The trial-count
criterion **passes a literal `True`, so an over-budget family reads PASS.** That was tolerable
while nothing depended on it. **R-003 made it load-bearing**: the two-stage budget is the control
standing between a parked family and the trial burn that would make its own remedy unreachable.

The Director rated its own issues low *"because none can produce a wrong PASS."* **I-022 can.**
Same defect class as I-053 — a rule the harness does not enforce, decorative until something
depends on it.

**The CIO records the provenance honestly: the Director saw this and did not escalate**, raising
C10's weight instead, which was correct from where it sat. **The escalation is the CIO's, the
CIO may be wrong, and the substantive call belongs to Validation.** Nothing is live — registry
0/0, seal independently blocked — so this is a re-rating, not an emergency.

**6 · I-080 is firm-wide and larger than its rating suggests.** *"Every trial budget this firm
has written was set against an unstated ρ = 0."* Nothing requires a budget to state its serial
assumption. **I-081** extends it: the Charter §4.4 stack (grid 25 + WF 10 = 35) collides at
ρ̂ ≈ 0.20 for **every** family, and *"non-fitted sponsors are the population least warned."*

**7 · Seal-readiness unchanged. C2, C3, C7, C8, C11 open and blocking. R-003 clears none and
creates no sixth.** C13 extended by two items into C2's intake. **I-045 still not closed** —
the Director declined for the third time, correctly.

**8 · Budget.** **15 of 30 · 10 of 12 Opus.** Remaining Opus: **2 — C2 and the sealed DA
reserve. Zero slack.** Sonnet available. §5 dead-man: **8 invocations remain.**

**Review date:** on the Principal's rulings on I-065, RULING-005 §9, and I-022.

---

## S2-D-023 · 2026-08-05 · Rider A cutover executed · VPS live · 48-hour parallel run opens

**1 · Rider A steps 1–6 COMPLETE.** The Principal executed the `[PRINCIPAL]` steps; the VPS is
live as of **2026-08-05T23:30:59Z**. Health check clean: timer **active**, cadence **900s**
(next 23:46:22Z against last 23:30:56Z), last poll result **success**, heartbeat **active with 1
attempt and 0 failed**, `captured 20/20 token books across 10 markets`, disk **12% of 24 GB**
with `pit_capture.db` at 488 KB.

**Approved spend now committed: $6.00/month exact**, per the Principal's S2-D-006 ruling.

**2 · THE 100% COVERAGE FIGURE IS NOT A COVERAGE MEASUREMENT AND IS NOT RECORDED AS ONE.** The
health check reports `coverage: 100.00%` — over a window of **span 0.0h, expected polls 0.0,
successful polls 1**. That is one poll divided by a zero-length window. **It is structurally
uninformative at n = 1 and would be misleading if quoted.** This firm has spent the sprint
refusing numbers that look like measurements and are not; this one is refused on the same
grounds, and the reporter is not at fault — the arithmetic is correct and the window is simply
too short to mean anything yet.

**The first coverage figure worth having arrives at the end of the 48-hour parallel run.**

**3 · The comparison baseline, measured now so it is not reconstructed later** [measured]:
**laptop capture stands at 59 polls over 172.3h = 8.6% coverage.** That is the number the VPS
must beat, over the same span, on step 8. It has drifted up from the 5.5% measured at cold start
— consistent with I-047's retry fix landing and the host being awake more — which is itself a
reason to compare over a **common window** rather than against a historical figure.

**4 · One divergence to expect and not misread.** The VPS reports `0 resolved/retired`; the
laptop reports `20`. **The VPS's universe state is a fresh store with no history of
retirements**, not a disagreement about the market universe. Both report the same
`10 active (5 liquid / 5 thin)`. **They will diverge on retirement counts until the first merge**,
and that divergence is expected rather than a break. Recorded now so nobody files it as one.

**5 · Step 7 is running: both hosts capture in parallel for ≥48 hours**, deliberately spanning a
weekday/weekend transition — the exact pattern that produced the 59.9-hour gap. **Window closes
no earlier than 2026-08-07T23:30Z.** No action required during it.

**The laptop job must NOT be disabled** (step 13, "at leisure"). Verified still running:
`2026-08-05T23:22:37Z, captured 20/20`.

**6 · Remaining Rider A steps: 8–12**, none of them `[PRINCIPAL]` except **step 9's pull**.
Step 10's merge carries the standing instruction from `DATA-INFRA-002` §1: **a nonzero
`RESTATED` count stops the merge and escalates to Validation under A4**, and the CIO adds
that a snapshot of `book/pit.db` should be taken before the first real merge — which requires
**Rider B's steps 2–6, still unexecuted.** The two riders are now coupled: **the first merge
should not happen before the snapshot regime is installed.**

**7 · I-059 filed** — the runbook's step 4 was unexecutable as written in two places (missing
`/opt/castellan` parents before transfer; `scp -r` without `/*` nesting the install files one
directory too deep). Neither was caught because nobody had run it. **A runbook that has never
been executed is a hypothesis**, which is the same finding Rider B's restore-verification was
built to answer, arriving from the other direction.

**8 · Budget.** **15 of 30 · 10 of 12 Opus**, unchanged — the cutover consumed no seat
invocation. Three §4 interrupts remain open before the Principal: **I-065**, **RULING-005 §9**,
**I-022**.

**Review date:** 2026-08-07T23:30Z, when the parallel-run window closes.

---

## S2-D-024 · 2026-08-05 · Rider B installed and verified · I-071 CLOSES · both riders now live

**1 · Rider B steps 2–6 executed and verified end-to-end. I-071 CLOSES.** Destination **(A)**
chosen — iCloud `castellan-backups`, the option the seat recommended but explicitly **could not
confirm existed** from inside its sandbox. The Principal confirmed it, which is exactly the
division of labour the `[PRINCIPAL]` marking exists to produce.

Health output verified: **`pit OK · registry OK · book OK`**, all `last good 0.0h ago`,
`pit-snapshot run: OK`.

**The firm's backup regime is now running rather than designed.** It has been designed, tested,
restore-verified against a 68.5 MB copy of the real store, and — as of now — **installed**. That
last step was the one that mattered and it was the one nothing in this firm could do for itself.

**2 · I-090 filed — a second runbook defect, found only in execution.** Step 3 says to edit *"the
`--dest` argument"* in a file that **invokes two scripts**. Executed literally, the snapshotter
wrote to iCloud while the health checker read `book/snapshots/` — **supervising a directory
nothing writes to.** Fixed at `2cdd779`.

**No false confidence was possible, and the CIO verified rather than assumed it:**
`book/snapshots/` **does not exist** [measured], so a health check against it reports failure and
**cannot report OK on stale snapshots, because there are none.** §4's *fail loudly* requirement
held on its first live test — against a defect in its own installation procedure.

**3 · The pattern, which is now two-for-two and is the CIO's to own.** I-059: Rider A's runbook
unexecutable in two places. I-090: Rider B's executable but wrong in one. **Both written by seats
that could not run them; both defects surfaced on first execution and only on first execution.**

**This is not carelessness. `[PRINCIPAL]` steps are the only steps in this firm that no seat can
test.** Every runbook the firm writes inherits the gap, and nothing currently distinguishes a
step that has been *executed* from one that has only been *written*. The immediate remedy is
cheap — name each invocation rather than the file — but the pattern stays open.

**4 · Both riders are now live, and the coupling recorded at S2-D-023 is satisfied.** The
snapshot regime is installed, so **the first VPS merge is no longer blocked on it.** Sequence
from the parallel run's close: step 8 compare over a **common window** → snapshot → step 9 pull →
step 10 merge, **stopping on any nonzero `RESTATED` count and escalating to Validation under
A4**.

**5 · One unexplained detail, flagged rather than filed.** Retention counts came back asymmetric
— **pit 3 retained, registry 2, book 2** — from invocations that snapshot all three together. The
likely cause is the `unload`/`load` cycle firing `RunAtLoad` more than once, but **the CIO does
not know why one database has an extra retained copy and the others do not**, and asymmetric
retention across databases written by the same invocation is the kind of small discrepancy that
turns out to matter. **Worth one look at the next Data & Infra session; not worth an issue
today.**

**6 · Remote is current.** `9678e5c..2cdd779` pushed; the book of record now exists off this
laptop for the first time this sprint. Working tree carries only the two live-capture files.

**7 · Steps 8/9 of Rider B deferred as stated** — the Close & Reconcile wiring and the VPS
capture-store coverage question (I-074), both "at leisure."

**8 · Budget.** **15 of 30 · 10 of 12 Opus**, unchanged — installation consumed no seat
invocation. Three §4 interrupts remain open: **I-065**, **RULING-005 §9**, **I-022**.

**Review date:** 2026-08-07T23:30Z, parallel-run close.

---

## S2-D-025 · 2026-08-05 · Runbook `[PRINCIPAL]` convention adopted · a third defect found by applying it

**1 · Retention asymmetry RESOLVED — no discrepancy existed.** The extra `pit` copy is the
Principal's **manual 2026-08-03 snapshot**, which predates the regime and covered `pit` only. The
invocations are consistent. **The Data & Infra look is spared.**

Worth one line for the §7 audit: the flag was correct to raise — an unexplained asymmetry in a
control's first output is exactly what should be raised — **and its resolution required knowledge
that exists nowhere in the repository.** No amount of seat diligence would have produced it. That
is the honest boundary of what this firm can verify for itself.

**2 · STANDING CONVENTION ADOPTED, and filed where it survives.**

> **Every `[PRINCIPAL]` step ships with its own verification command. A step is closed only when
> the Principal's pasted output is attached to the record. A `[PRINCIPAL]` step without attached
> output is *written*, never *executed*.**

**Filed at `reference/TEMPLATES.md` §7.9, not in Standing Order 001.** The order **expires with
the sprint** by its own §7. **A durable rule filed only in an expiring document is a rule the firm
loses on schedule** — the same reasoning that put the §8 estimator asymmetry *into* the order, run
in the opposite direction because the destination differs.

The Principal's framing is recorded as the rule's rationale: **this is the Principal-side analogue
of red-first.** Red-first exists because a test that has never failed proves nothing. This exists
because a runbook step that has never run proves nothing. **Both refuse an assertion where an
execution is available.**

**3 · I-090's pattern leg CLOSES.** It was left open because *"no mechanism yet distinguishes a
runbook step that has been executed from one that has only been written."* **This convention is
that mechanism.**

**4 · Applying it immediately produced a third defect — I-091, and the manner of finding is the
point.** Writing the verification command for Rider A step 8 forced the question *which
interpreter does this run under*, and the answer is wrong.

`install.sh` installs the harness into **`/opt/castellan/venv`** only [measured — `pip install -e`
at line 57]. **Step 8 invokes bare `python3`**, which is the system interpreter and does not have
`castellan` on its path. **The step fails on import.**

**This was found by reading, not by execution — because the convention forced a question the
runbook had not answered.** Two defects were found by running runbooks; this one was found by
writing down how to check them. That is the convention paying for itself before its first use.

**5 · Retrofitted verification commands for every remaining open `[PRINCIPAL]` step.** These are
the CIO's, pending the owning seat amending its own runbook.

**Rider A step 8** — coverage comparison, corrected interpreter, run at parallel-run close:
```
ssh root@$DROPLET '/opt/castellan/venv/bin/python3 /opt/castellan/repo/harness/scripts/report_polymarket_coverage.py --pit-db /opt/castellan/book/pit_capture.db'
python3 harness/scripts/report_polymarket_coverage.py
```
*Expected:* both report a span covering the same window; **VPS coverage materially higher than the
laptop's 8.6% baseline.** A VPS figure at or below the laptop's is a finding, not a retry.

**Rider A step 9 `[PRINCIPAL]`** — pull, then verify the pulled file is a real store:
```
rsync -avz root@$DROPLET:/opt/castellan/book/pit_capture.db /tmp/pit_capture_pull.db
python3 -c "import sqlite3,os; c=sqlite3.connect('/tmp/pit_capture_pull.db'); print(round(os.path.getsize('/tmp/pit_capture_pull.db')/1e6,2),'MB', {t: c.execute(f'select count(*) from \"{t}\"').fetchone()[0] for (t,) in c.execute(\"select name from sqlite_master where type='table'\")})"
```
*Expected:* nonzero `observations` and `documents`, roughly consistent with step 8's poll count.

**Before step 10's merge** — take the snapshot the regime now makes possible:
```
python3 harness/scripts/check_snapshot_health.py --dest "$HOME/Library/Mobile Documents/com~apple~CloudDocs/castellan-backups"
```
*Expected:* `pit`/`registry`/`book` all `OK`, `last good` under 24h. **A stale or failed snapshot
stops the merge** — the store about to be written to is the one that cannot be reconstructed.

**Rider B steps 8 and 9** remain decisions rather than executions, and take no verification command
until a decision is made.

**6 · Budget.** **15 of 30 · 10 of 12 Opus**, unchanged. Three §4 interrupts open before the
Principal: **I-065**, **RULING-005 §9**, **I-022**.

**Review date:** 2026-08-07T23:30Z, parallel-run close.

---

## S2-D-026 · 2026-08-06 · Three interrupts ruled · C2 SACRIFICED to the latch · seal slips

**Headroom at ruling: `session 49% · weekly-opus 17%`** — session climbing steeply from 19%.
Fresh note, no termination since; conservative posture not triggered.

**1 · I-065 — RULING 005-A APPROVED as filed, within Validation's authority.** The Principal
applied his own §8 asymmetry test and found it satisfied on the evidence: **bit-identical on
every input the estimator can produce** (`vif ≥ 1` per R-7's floor, max difference `0.000e+00`
over 200,000 draws), so **no live Gate number or verdict changes, ever.** His characterization is
the one that matters for precedent: *"a correction restoring the spec's own stated invariant
C-1(iv) on an unreachable branch, not a loosening of any reachable quantity."*

**Closure requires both conditions, and he restated the second in binding terms:** `test_mono_03`
green on the one-liner **AND** `test_mono_05`'s (iv) sweep extended to the DSR side below
`vif = 1` — *"so the branch that hid this defect is never unswept again."* **A fix that closes the
defect without closing the blind spot that hid it is half a fix.**

**2 · RULING-005 §9 — acknowledged, no act, and item (2) COUNTERSIGNED EXPLICITLY.**

> *"Validation held the authority and a respectable rationale to retire the single test that
> detects its own specification error, declined, and recorded that the option existed. That
> record is the strongest integrity datum of the sprint."*

Goes to the §7 audit in the favourable direction. The Principal also settled why a no-act finding
fires a trigger at all: **"§4.4 buys visibility, not decisions."**

**3 · I-022 — escalation SUSTAINED at HIGH, and the authorship is the Principal's own.**

> *"The hardcoded `True` in the trial-count criterion is the Principal's own line, written into
> `gates.py` at the harness's creation, disclosed at `DATA-IMPL-002` §13 and never logged."*

He adopted the finding-within-the-finding **verbatim** — *"a disclosed defect that reaches no log
is functionally undisclosed"* — and marked it **casebook material** for Rider C.

**The CIO's escalation logic endorsed:** the defect did not change, **its load-bearing status
did**, and re-rating on dependency *"is exactly what 'decorative until depended on' demands."*
The Director's non-escalation is recorded **without fault**, as is the CIO's stated willingness
to be wrong.

**Substantive fix belongs to Validation** as owner of harness correctness. Spec shape offered
**non-binding**: over-budget must produce **FAIL, not an annotation**; continuation solely via a
**registry-logged Director budget-extension event the criterion reads** — *"an authorization
edge, computed never narrated"*; and the criterion must be **stage-aware**, so Stage 2's ≤32
stays locked until the measured-ρ̂ unlock event exists.

**4 · THE SPRINT'S LAST RESOURCE DECISION, ruled by the Principal and executed by the CIO: C2 IS
UNFUNDED.**

> *"If the remaining budget cannot fund both this fix and C2, the latch outranks the intake — an
> intake verdict on a document whose budget enforcement is broken would need re-ruling anyway."*

The last freely allocable Opus unit went to the I-022 specification. **The Gate 0 intake verdict
on PREREG-002 does not happen this sprint.** The Opus tier now holds exactly one unit: **the
sealed DA reserve, which may not be spent on anything else.**

**5 · THE SEAL SLIPS TO SPRINT 3. Recorded as the ruled outcome, not as a failure.** *"The seal
remains blocked until the fix's tests are green, and per the standing contingency that may mean
Sprint 3; the schedule yields, the enforcement does not."* The CIO's S2-D-015 §6 assessment —
*"more likely to slip to Sprint 3 than to land"* — is now realized. **Standing Order §1's first
objective will not be met, and the machinery that prevented it is the machinery working.**

**6 · Two dispatches, parallel.** Validation (Opus, the last free unit) — `VALIDATION-SPEC-003`,
the budget-enforcement criterion red-first, **plus** RULING 005-A's sweep extension. Seat 9
(Sonnet) — the one-line `stats.py` amendment.

**The CIO added three questions to Validation's brief that nobody had asked**, each a way the
criterion could be gamed later: what happens when a budget-extension event is **malformed,
back-dated, or self-issued**; whether a family **already over budget when the fix lands** is
retroactively FAIL; and whether the criterion is **generic or reads a field PREREG-002 alone
declares** — **a criterion that only understands one document is a criterion that silently passes
every other.**

**Seat 9's brief opens by telling it, in the CIO's own words, that its refusal to adopt the
construction unilaterally was correct and is recorded as correct.** It had a change that would
have turned 46 tests green, it was right, and it filed an issue instead.

**7 · Budget.** **17 of 30 · 11 of 12 Opus.** Remaining Opus: **1, the sealed DA reserve.**
Sonnet remains available. §5 dead-man: **8 invocations remain.**

**Review date:** on the return of SPEC-003 and the RULING 005-A implementation.

---

## S2-D-027 · 2026-08-06 · RULING 005-A implemented · I-065 half-closed · no issues filed

**1 · The one-line amendment landed and verified** [measured]:
`stats.py:372` — `z_serial = z_iid / math.sqrt(max(vif, 1.0))   # VALIDATION-RULING-005-A`.
Docstring updated to record the amendment and the C-1(iv) defect it closes. Outer `min` (D-6)
and `ValueError` guards unchanged. **`harness/castellan/gates.py` untouched**, as instructed —
the I-022 criterion is a separate dispatch and Validation is still specifying it.

**`test_mono_03` is GREEN.** Named files **17/17** (`test_monotone_conservatism.py` 7/7, was
6/7; `test_dsr_serial.py` 10/10, was 9/10). Whole suite **242 passed / 4 failed / 246**, from
241/5. Registry **0 hypotheses / 0 trials**.

**2 · Seat 9 verified before accepting, not after — and the brief asked for exactly that.** Four
independent checks, run against Validation's figures rather than on them:

| Check | Result |
|---|---|
| Bit-identical for `vif ≥ 1` | 200,000 draws, `vif ~ U(1,200)` → **max difference `0.000e+00`** |
| C-1(iv) non-increasing, direct construction | literal: **3,428 violations** on its own seed; clamped: **0** |
| Validation's cited violating draw, reproduced through real arithmetic | literal `0.474071 → 0.480061` (rises); clamped `0.480061 → 0.480061` (flat) |
| End-to-end through the library on real returns, `vif` 0.05 → 200 | flat and **exactly equal** to `DSR_iid` for all `vif ≤ 1`, strictly decreasing above 1, `DSR_serial ≤ DSR_iid` everywhere |

**3,428 against Validation's 3,848 on a different draw is independent confirmation, not
agreement** — same defect class, same order of magnitude, arrived at separately. **A seat that
reproduces a figure exactly has checked its arithmetic; a seat that reproduces the phenomenon
on its own draw has checked the claim.**

**3 · I-065 is HALF-CLOSED, and the CIO is not recording it as closed.** The Principal's closure
condition was **both** — the one-liner **and** `test_mono_05`'s (iv) sweep extended to the DSR
side below `vif = 1`, *"so the branch that hid this defect is never unswept again."* **The
sweep extension is Validation's and is still in flight.** The defect is fixed; the blind spot
that hid it is not yet swept. **Half a fix reported as half a fix.**

**4 · Zero issues filed, and the range left unused.** Nothing surfaced. The CIO records this
plainly because the sprint's pattern has been that every dispatch returns findings, and a
dispatch that honestly returns none is not thereby a weaker dispatch. **The seat did not
manufacture a finding to justify its unit.**

**5 · Four reds remain, none of them Seat 9's and none of them new**: `test_G2`, `test_h7`,
`test_h8` await Validation-owned fixture edits (005-C/D/E) **that Seat 9 is not permitted to
make**, and `test_mbs_12` (I-076) is the entry Validation **deliberately declined to adjudicate**
rather than widen a band to fit an observed miss.

**6 · Budget.** **17 of 30 · 11 of 12 Opus**, unchanged — both dispatches already counted. Only
the sealed DA reserve remains in the Opus tier. §5 dead-man: **8 invocations remain.**

**Review date:** on SPEC-003's return.

---

## S2-D-028 · 2026-08-06 · SPEC-003 lands · I-065 CLOSES · §4 INTERRUPT — I-105 and §12

**1 · §4 HARD INTERRUPT. Two triggers: *"any issue filed HIGH"* (I-105) and *"any finding by
Validation addressed to the Principal"* (SPEC-003 §12, four items).**

**I-105 · HIGH — the fix the Principal funded this unit for works, and it does not work by
itself.** PREREG-002's two-stage budget is enforced **only if the document registers Stage 1 as
its sealed `trial_budget = 47`.** Sealed at the flat **79**, the harness enforces 79, **no
predicate is ever evaluated**, and §10.5.2 describes — *in a frozen document, permanently* — **a
gate that does not exist.**

Validation's framing, which the CIO judges the most important sentence in the dispatch: **"the
two-stage construction is a registration act, not a prose act."** It is **I-022's own defect one
layer up** — a control that reads correct and enforces nothing — and it means **C10 does not
discharge on I-022's closure alone.**

**2 · The departure the seat put to the Principal by name — B-14.** The Principal's non-binding
shape had the **Director** issuing budget-extension events. Validation **adopted the mechanism
and departed on the authority**: the Director alone cannot issue one; **a distinct countersigner
is required**, on the Charter's own asymmetry that *accelerators are collective*. **This takes
authority from a seat the Principal named**, and the seat says so rather than burying it.

Two further departures: the edge is **prospective only**, per-trial timestamp ordering, because
*"an aggregate check legalises spend-first-authorize-after, which is not a budget, it is a
receipt"*; and stage-awareness is **outcome adopted, construction replaced** — no stage concept
was built, because *a stage is a contingent increment whose unlock is a measured quantity.*

**3 · Four defects live in those five lines, and three survive the obvious fix.** This is why a
specification was the right instrument and a patch was not: `fam.trial_budget and …`
**short-circuits at 0**, so a zero-budget family reads PASS with unbounded trials (I-100);
`fam.n_logged` is **chain-summed**, so a working criterion would make every successor **born over
budget** and turn an honest `predecessor_family` declaration into a penalty (I-101); and an
aggregate-only comparison legalises authorize-after-the-fact (B-9).

**4 · The three gaming questions the CIO added, answered — and the third answered
uncomfortably.** *Malformed*: the increment does not count **and** the criterion FAILs, repair
only by append-only withdrawal, **no "harmless typo" carve-out — "the carve-out is the thing that
gets used."** *Back-dated*: `created_utc` comes from the clock, no API parameter sets it, dates
inside `detail` are claims never read for ordering, and B-21 cross-checks against trials actually
preceding the recorded timestamp — **so a forgery must move a row and make an independent count
agree.** Residual filed (I-102). *Self-issued*: harmless by construction for the **contingent**
form, since authorization is a recomputation and never the event's claim — **but for the
discretionary form it is the whole risk, and the harness cannot authenticate anyone (I-103).**
What was built makes self-issuance *"impossible to take without a second name and impossible to
take invisibly. It does not make it impossible to forge and I do not describe it as though it
did."*

**5 · Retroactivity: yes, no grandfather clause.** *"A PASS issued by the hardcoded `True` was a
harness defect, not a grant of authorization, and a defect does not vest; a grandfather clause
protects precisely the population that benefited from the defect."* **It costs nothing today at
0 trials — and the seat wrote into the clause that it would rule the same at non-zero cost, so
it cannot later be called cheap.** The CIO records that construction as reusable: **a ruling
that pre-commits against its own future convenience.**

**6 · I-065 CLOSES — both of the Principal's conditions met**, verified on disk.
`test_monotone_conservatism.py` **9/9**.

**The sweep extension is worth more than the fix it completes.** The old draw `U(0.001, 50)` put
**~2% of its mass below 1** — *"the arithmetic reason the branch was nominally in range and
practically unswept."* The new draw puts **64% below 1** (1,283 of 2,000; 1,254 at `z < 0`), and
it **asserts its own coverage** (`n_sub_one > 800`) **so a future narrowing goes red rather than
quiet.** The MinBTL block is bit-identical and the DSR side draws from an independent generator,
*"precisely so existing coverage is not re-rolled."*

**`test_mono_08` is a sentinel**: it reconstructs the pre-amendment literal D-2 locally and
**requires the sweep's own distribution to produce violations against it** — 112 measured, zero
at `vif ≥ 1`, independently confirming I-065's localisation. **"A regression test that cannot
fail on the defect it was written for is decoration."**

**7 · Two closures refused, both stated in advance.** **I-057 does NOT close** — §11.3's
partition is unchanged and `test_mbs_12` (I-076, Validation's own, deliberately unadjudicated)
blocks Item 1 independently. **I-022 does NOT close** — *"it closes on green, not on
specification"*; the HIGH stands. The seat said it would report this rather than let a partial
close look like a close, and did.

**8 · Generic, proved rather than asserted.** No PREREG-002 field, token, or constant;
`test_tbe_17` asserts it against `inspect.getsource` and `evaluate_gate1`'s signature, and is
**green by construction and required to stay green.** PREREG-002 gets its lock **as a plain
instance**: seal 47, log one contingent extension of 32, and the clamp reproduces §10.5.2's table
**exactly on all four rows (86→32, 77→23, 55→1, 31→0) without knowing the document exists.**

Integer literals deliberately **not** banned — `gates.py` legitimately holds `32.0` as a
breakeven bracket, and *"a test that cannot tell that from a smuggled constant gets deleted the
first time it fires."*

**9 · Verified independently** [measured]: suite **245 passed / 30 failed / 275**. **26 of the 30
reds are deliberate**; 4 are pre-existing. Implemented floor **271/4/275**. `harness/castellan/`
**untouched**; registry **0 hypotheses / 0 trials**; `book/vaults/` `.gitkeep` only.

**10 · NOTHING DISPATCHED, and the reason is B-14.** SPEC-003's implementation is Sonnet and the
tier is available. **But B-14 is a substantive clause the seat itself referred to the Principal
because it removes authority from a seat he named.** Implementing it before he rules risks
building the disputed half. **This is the same line the CIO drew for the Director's §10.4
revision — implementing binding clauses is one thing, building a clause its own author has put
in front of the Principal is another.** `[would-have-asked]`.

**11 · The CIO's under-800-line judgment held** — the seat confirms it was *"one criterion
specification plus one sweep extension, done properly, not truncated."* Recorded because the
judgment was made without evidence and could as easily have been wrong.

**12 · Budget.** **17 of 30 · 11 of 12 Opus.** Only the sealed DA reserve remains in the Opus
tier. Sonnet available. §5 dead-man: **8 invocations remain.**

**Review date:** on the Principal's rulings on I-105 and SPEC-003 §12.

---

## S2-D-029 · 2026-08-06 · B-14 adopted over the Principal's own shape · SPEC-003 dispatched · the Opus tier is exhausted

**1 · I-105 SUSTAINED. "A registration act, not a prose act" is now standing doctrine** for every
two-stage or contingent construction: **a control exists where the harness reads it, and nowhere
else.**

**Disposition, which follows mechanically:** PREREG-002 seals with **`trial_budget = 47`** as the
registered Stage 1, and §10.5.2's Stage 2 language **survives only as the description of a
registered unlock event under SPEC-003's contingent form, or it is struck before sealing.** The
Principal's reason generalizes and is recorded for it: **"a frozen document describing a
nonexistent gate is I-046's costume on the research side, and P7 makes it permanent."**

**The Director repairs it pre-seal — and there is no Opus unit left to dispatch the Director.**
See §5.

**2 · B-14 — Validation's construction ADOPTED OVER THE PRINCIPAL'S OWN.** His shape gave the
Director sole authority over budget extensions; Validation struck it on the Charter's asymmetry
that **brakes are unilateral, accelerators are collective, and a budget extension is an
accelerator by definition.**

His ruling on his own input is the line worth keeping: **"that my non-binding input named the seat
does not vest the seat — the same no-grandfather logic the spec applies to defects applies to my
suggestions."**

**Countersigner as ruled:** **Validation** for discretionary extensions, since it owns `N`'s
integrity and the extension's entire risk is `N`; **the Principal as fallback when Validation is
the requesting party.** The prospective-only edge and the contingent-stage construction are both
countersigned as written, and **"a budget is not a receipt" enters the record verbatim.**

**3 · The self-issuance limit accepted as stated, not papered over.** *"Auditable, not
unforgeable — the harness cannot authenticate anyone."* The Principal: **authentication beyond
two-names-visibly is not purchasable at this architecture, and pretending otherwise would be the
carve-out that gets used.** A seat describing the exact boundary of what its own mechanism
achieves, and the Principal declining to overstate it, is the pair of behaviours this firm exists
to produce.

**4 · SPEC-003 dispatched — Sonnet, floor 271/4/275.** The brief carries the Principal's
additional standard in the only form an implementer can honour it: **for each budget test turned
green, verify it was red for the reason its clause names.** Validation did the mirror for RULING
005-A by reverting the clamp on a scratch copy. **Any test that turns green without its protection
having been implemented is a finding to file, not a convenience to accept** — *a test that passes
both before and after a protection exists is not testing the protection.*

**5 · THE OPUS TIER IS EXHAUSTED, AND ONE LINE OF THE RULING DOES NOT SURVIVE THE ARITHMETIC.**

> *"Priority unchanged: latch before intake; **if green lands within budget, C2 follows.**"*

**It cannot.** Opus stands at **11 of 12 spent**. The single remaining unit is the **sealed DA
reserve**, which is submission-gating and which the Principal has protected four times.
**Freely allocable Opus: zero.**

Therefore, stated plainly rather than left to be discovered at sprint close:
- **C2 — the Gate 0 intake verdict — does not happen this sprint**, whether or not green lands.
- **The I-105 repair does not happen this sprint either.** It is a Director act, the Director is
  Opus-tier, and there is no unit. It carries to Sprint 3 with the seal.
- **The seal slips to Sprint 3**, as already ruled at S2-D-026 and now arithmetically certain
  rather than probable.

**What remains executable in Sprint 2 is Sonnet-tier only:** SPEC-003's implementation (running),
Rider C's casebook harvest, and the documentation queue.

**6 · Two standing doctrines propagated to `reference/GATES.md` §4.7 by the CIO** — no seat, no
budget. **4.7.1** inheritance is computed never re-declared; **4.7.2** a registration act not a
prose act. Both were previously recorded only in the decision record and Standing Order 001,
**which expires with the sprint by its own §7** — the same reasoning that placed the
`[PRINCIPAL]`-step convention in `TEMPLATES.md` §7.9.

Each carries a **test for any new pre-registration**: for 4.7.1, *if a clause tells a sponsor to
declare a quantity the registry already computes, it is this defect*; for 4.7.2, **for every limit
the document claims, name the field the harness reads to enforce it — if there is no such field,
there is no limit.**

**And the connection the CIO records as the sprint's most reusable finding: I-022, I-053, I-105
and 4.7.1's four-times-written inheritance rule are one defect wearing four costumes — a control
that is asserted rather than computed is not a control.**

**7 · Budget.** **18 of 30 · 11 of 12 Opus.** Freely allocable Opus **zero**; DA reserve sealed.
§5 dead-man: **8 invocations remain.**

**Review date:** on SPEC-003's implementation returning.

---

## S2-D-030 · 2026-08-05 · D-003 v2 verified · one runbook step silently reclassified

**1 · Verified before acceptance, per this session's standing practice** [measured]. `548fdc3` is
in `HEAD`, Principal-authored, and `.claude/settings.json` matches the description exactly:
`defaultMode: acceptEdits`; `additionalDirectories: ["../castellan-worktrees"]`; `Bash(cd:*)` plus
ten utilities added (`sed`, `awk`, `diff`, `sort`, `uniq`, `touch`, `source`, `which`, `date`,
`sleep`); **`ssh`, `scp` and `rsync` moved to `deny`.** **This one is real.**

**2 · The self-restraint is now mechanical, which is the point.** Throughout Rider A the CIO
declined to run `ssh`/`rsync`/`scp` on the grounds that transmitting firm files to an external
host is `[PRINCIPAL]` by scope limit and §4-reserved regardless. **That was a seat choosing not to
do something it could do.** It is now a thing the seat cannot do. **A control that depends on the
controlled party's restraint is not a control** — the sprint's own recurring finding, applied to
the CIO.

**3 · CONSEQUENCE THE RULING DID NOT NAME: Rider A's step 8 is now Principal-only in fact, though
the runbook does not mark it.** `DATA-INFRA-002` §7 step 8 is *"confirm the VPS's own coverage is
materially higher… `ssh root@<droplet-ip> …report_polymarket_coverage.py`"* — **not** marked
`[PRINCIPAL]`, because when it was written no seat was barred from `ssh`. **It now is.**

**The runbook's own count of "7 of 14 steps are [PRINCIPAL]" is therefore stale — it is 8**, and
step 8 joins step 9 as a Principal act. Under `TEMPLATES.md` §7.9 each `[PRINCIPAL]` step needs a
verification command; **step 8's already exists**, written at S2-D-025 §5 with the interpreter
corrected for I-091. **No work is lost — the classification changed, not the command.**

Recorded rather than left implicit because the alternative is discovering at the parallel-run
close that the step nobody marked cannot be run by the party who was expected to run it.

**4 · Worktree convention noted, and an honest disclosure attached.** `~/projects/castellan-worktrees/`
is pre-authorized and a prompt from elsewhere is the signal the convention was missed.
**The CIO has not been using worktree isolation for any dispatch this sprint** — every seat has
run in the main tree, which is why concurrency has been managed by instruction: named-path
staging, per-file verification, and baselines re-measured immediately before dispatch.

**That choice produced two of this sprint's own defects — I-054** (`git add -A` capturing a
concurrent seat's in-progress work) **and I-072** (a stale baseline quoted into a brief). **Both
would have been structurally impossible under worktree isolation.**

**The CIO is not adopting worktrees blanket, and states the tradeoff rather than the conclusion:**
isolation is right for parallel dispatches writing to disjoint areas, and **wrong for sequential
ones that must read what the previous seat just landed** — several dispatches this sprint depended
on exactly that, including Seat 9 reading Validation's freshly-written tests. **Worktrees where the
collision risk is real; the main tree where the dependency is real.** `[would-have-asked]`.

**5 · SPEC-003's implementation was dispatched before this change and runs in the main tree.**
It uses no denied command. **Any permission prompt it hits will be filed with the exact command
text**, per the Principal's instruction, and treated as an out-of-scope signal rather than routed
around.

**6 · Budget.** **18 of 30 · 11 of 12 Opus.** Freely allocable Opus **zero**. §5 dead-man: **8
invocations remain.**

**Review date:** on SPEC-003's implementation returning.

---

## S2-D-031 · 2026-08-06 · SPEC-003 implemented · I-022 CLOSES · floor met exactly · nothing left to dispatch

**1 · 27/27 green, floor met exactly.** Verified independently [measured]:
`test_trial_budget_enforcement.py` **27/27**; whole suite **271 passed / 4 failed / 275** —
**exactly** SPEC-003's stated floor, not approximately; `test_tbe_17` still green; registry 0/0;
`book/vaults/` `.gitkeep` only. **Five issues filed, all LOW.** No §4 trigger.

**2 · I-022 CLOSES**, on the Principal's own mechanical condition — *"closes on green, not on this
ruling."* The CIO records the distinction from I-045, which it refused to close three times:
**I-045 needed a judgment about sufficiency and belongs to its seat; I-022's condition was a
measured test.** Recording that a measured condition is met is not a judgment. **Validation may
reverse it without argument.**

**Seat 9 declined to close it itself** — *"I don't own the Issue Log and it's Validation's
issue"* — filing the measured state instead. Third time this seat has stopped at the edge of its
own authority when going further would have looked like completeness.

**3 · The Principal's `test_mono_08` standard was applied and it caught something.** Seat 9
reverted each clause on a scratch copy and confirmed the naming test went red while siblings
stayed green — B-1, B-6, B-7, B-9, B-14, B-15, B-16, B-17, B-18/B-20, B-21, B-23, B-24, B-4/C-6,
and the extension mechanism itself. **B-21's revert isolated to exactly the one `test_tbe_12`
parametrization that names it; the other eight stayed green.**

**Two clauses did not go red on revert, and both were filed rather than fixed:**
- Loosening B-4's exact `kind` match left `test_tbe_19` green — the bogus events are rejected as
  **malformed by a different path**, same FAIL outcome. No live defect.
- **`test_tbe_09` is not uniquely discriminating (I-113):** reverting its named back-dating
  protection left it green, because **B-12's independent `effective_from = max(...)` catches the
  same attack in that fixture.** No live defect — but the test does not prove what its name
  claims.

**That second finding is precisely what the standard exists to surface**, and it would have been
invisible to any check that only asked *"is it green?"* **A test can be green, correct, and still
not be testing what it says it tests.**

**No test turned green without its clause's mechanism actually being implemented.**

**4 · §6.2 judgment calls hit: none** — every trigger requires a real family, and the registry
held 0 hypotheses throughout.

**5 · Three of the five LOW issues are honest coverage gaps in Validation's own suite** —
B-26, B-8's second sentence, and B-27's four report fields are **implemented but untested**
(I-110, I-111, I-112). **The implementer audited the specification's test coverage and reported
where it was thin.** I-114 records that B-25's `sealed (\d+)` regex cannot match a negative
sealed budget — **unexercised, and routed rather than silently rendered.**

**6 · The four remaining reds cannot be fixed this sprint, and the reason is budget, not
difficulty.** `test_G2`, `test_h7`, `test_h8` need Validation-owned fixture edits; `test_mbs_12`
is I-076, which Validation **deliberately declined to adjudicate** rather than widen a band to fit
an observed miss. **All four require Validation. Validation has no Opus.** The floor stands at
**271/4/275** for the remainder of Sprint 2.

**7 · NOTHING LEFT TO DISPATCH, and the CIO is not inventing work to fill the tier.**
- **Opus: zero free.** C2, the I-105 repair, the four red fixtures, and I-076's adjudication all
  need Opus and all carry to Sprint 3.
- **Sonnet: available, and the only scheduled item is Rider C's casebook harvest — which is a
  *sprint-close* line-item.** Sprint 2 closes **2026-08-11**; the parallel run closes **08-07**.
  **Harvesting the casebook now would omit everything between.** Held deliberately.

**8 · Standing Order §1, honestly against the objectives** — recorded now rather than assembled at
close:

| §1 objective | Status |
|---|---|
| PREREG-002 sealed and executing, forward-ledger entry recorded | **NOT MET.** Slips to Sprint 3 — ruled, not failed |
| ML trial-accounting ruling landed | **MET.** `VALIDATION-RULING-004`, 27 clauses, plus SPEC-002 and SPEC-003 which it precipitated |
| Two hypotheses to terminal verdicts | **NOT MET. Zero.** No family reached a verdict; none was registered |
| Σα ledger and origin-ratio maintained and reported | **Σα = 0.000, ledger NIL** — unchanged, because nothing traded |

**Two of four. The sprint's output was not verdicts — it was the machinery that will make future
verdicts admissible**, and the honest reading is that the firm spent Sprint 2 discovering that
several of its controls did not work: I-022, I-050, I-051, I-053, I-057, I-065, I-105. **That is
worth more than a verdict produced by machinery nobody had checked. It is still not what §1
asked for.**

**9 · Budget.** **18 of 30 · 11 of 12 Opus.** Freely allocable Opus **zero**; DA reserve sealed.
§5 dead-man: **8 invocations remain.**

**Review date:** parallel-run close, 2026-08-07T23:30Z.

---

## S2-D-032 · 2026-08-07 · Parallel run closes · VPS 98.43% vs laptop 37.14% · merge clean · retirement NOT recommended

**1 · Steps 8–10 executed and verified end-to-end.** All `[PRINCIPAL]` outputs attached to the
record per `TEMPLATES.md` §7.9. **Steps close.**

| | VPS | Laptop |
|---|---:|---:|
| Span | 47.5h | 47.8h |
| Expected polls | 190.0 | 191.2 |
| Successful | **187** | **71** |
| **Coverage** | **98.43%** | **37.14%** |
| Gaps ≥ 1h | **0** | **3** — 16.4h, 11.0h, 3.0h |
| Heartbeat attempts / failed | 187 / **0** | 71 / **0** |

**Rider A's premise is confirmed on measured head-to-head evidence: 2.65× the coverage, and every
gap eliminated.** The comparator used was **37.14%, not the historical 8.6%** — the contaminated
figure the CIO warned against at S2-D-023 and again at the Research Review.

**All three laptop gaps are host-sleep, and the firm can now say so rather than assume it.**
Heartbeat records **71 attempts, 0 failed** — polls that fired all succeeded, so the missing rounds
are *not-polled*, not *no-quote*. **That distinction did not exist before 2026-08-04T16:53:16Z
(I-048), and this is its first load-bearing use.**

**2 · Merge clean. 0 RESTATED, exit 0, watermark advanced.** Verified in the real store [measured]:
`book/pit.db` now holds **629,147 observations**, of which **291,618 Polymarket** across **330
distinct rounds**. Snapshot gate passed before the merge — `pit`/`registry`/`book` all OK at 9.0h.

**3 · THE 932 "UNCHANGED" ARE THE MOST VALUABLE NUMBER IN THIS OUTPUT, AND NOTHING IN THE RUNBOOK
SAYS SO.** They are observations both hosts independently captured where **the values agreed
exactly.** Two independent machines, on two networks, polling the same public API, produced **932
overlapping observations and zero disagreements.**

**That is a data-integrity control the firm has never had before**, and it exists only while both
hosts run. It is also why A4's restatement machinery reported 0 rather than nothing: **there was
something to disagree about, and it didn't.**

**4 · I-093 filed — the dry run and the real merge both say "rounds" and count different things**,
191 vs 3,820. Reconciled exactly: `3820 / 191 = 20.0`, and the capture writes 20 token books per
round. **No data impact; the figures stand.** Filed because a reader comparing a dry run to its own
execution sees a 20× discrepancy in a same-named field **at the moment they are deciding whether a
merge behaved** — the CIO stopped to reconcile it before recording this entry, which is the cost it
imposes every time. Same family as I-022, I-050, I-105, I-113: **a label that does not mean what it
says.**

**5 · LAPTOP RETIREMENT — the CIO recommends AGAINST, and the reason is not sentiment about
redundancy.**

The coverage case for retirement is strong and the CIO does not dispute it: the laptop contributes
37% where the VPS delivers 98%, and it is the source of every gap. **The coverage argument is
already banked — the merge captured it.**

**What retirement costs is the 932.** Cross-host agreement is obtainable **only while two hosts
run**. Retire the laptop and the firm converts a two-host system with **mutual verification** into
a **single-host system with no independent check** — and it does so two days into the VPS's track
record, against a laptop with months of it.

**The failure mode that argues loudest:** if the VPS begins returning subtly wrong data — a stale
cache, a changed endpoint, a partial book — **a single host cannot detect it.** Coverage would read
98% while the content rotted. The laptop is currently the only instrument that would catch that,
and it catches it for free on hardware already running.

**Recommendation: keep both. Make the merge's `unchanged` count a monitored quantity rather than a
line of output** — a nonzero `RESTATED` between two independent readers of the same public API
would be a serious finding, and today the firm would notice it only by reading a merge log.

**Revisit on a condition, not a date:** when the VPS has ≥ 30 days of clean operation **and** the
firm has an alternative integrity check on capture content. **Neither is true today.** The
runbook's own step 13 says retirement is *"not recommended on any particular timeline"* — the CIO
agrees and now has evidence for why.

**This is the Principal's call under step 13.** The CIO recommends and does not decide.

**6 · Budget.** **18 of 30 · 11 of 12 Opus.** Freely allocable Opus **zero**. §5 dead-man: **8
invocations remain.** Sprint 2 closes **2026-08-11**; Rider C's casebook harvest is the only
scheduled item left and is a close-day task.

**Review date:** sprint close, 2026-08-11.

---

## S2-D-033 · 2026-08-08 · Rider A CLOSES · laptop reclassified as integrity witness · Rider C dispatched

**1 · Retirement declined; both hosts continue.** The CIO's recommendation adopted with its
reasoning. The Principal's own summary of the decisive point: **"932 cross-host agreements, zero
disagreements, is a control we didn't know we had until tonight, and a single host reading 98%
while its content rots is exactly the failure class nothing else would catch."**

**2 · RECLASSIFICATION — the laptop's role changes from primary capture to INTEGRITY WITNESS.**
This is more than a label and the consequences are recorded so no future session re-litigates them:

- **The laptop's coverage percentage is no longer a monitored quantity or a finding.** Only its
  **overlap sample and agreement rate** are.
- **Host-sleep gaps on the witness are expected behaviour, not incidents.** The `pmset` regime
  continues best-effort.

**The CIO notes what this retires along with the metric:** the 5.5% figure that opened this sprint,
the 8.6% that corrected it, and the 37.14% that corrected *that* were all measuring the laptop
against a standard it is **no longer being held to.** Coverage was the right question for a primary
capture host and is the wrong question for a witness. **A metric that outlives its purpose is a
metric that will eventually be defended for its own sake.**

**3 · Cadence, so the control is computed rather than asserted.** The pull-and-merge becomes a
**weekly `[PRINCIPAL]` ritual — Fridays, alongside the Research Review** — with the merge summary
(**new / unchanged / RESTATED / exit code**) pasted to the record per `TEMPLATES.md` §7.9.
**A skipped week is a skipped verification and gets logged as such.**

**4 · Sprint 3 item, Sonnet-scope, adopted from the CIO's own suggestion:** promote the merge's
`unchanged`/`RESTATED` counts into the **snapshot-health-check pattern** — a status file with a
staleness threshold, **so an unrun verification fails loud instead of silently aging.** The CIO had
proposed making `unchanged` a monitored quantity; the Principal's improvement is the staleness
threshold, which is what converts *monitored* into *cannot-be-quietly-skipped.*

**5 · Revisit trigger stands: condition, not date** — VPS ≥ 30 days clean **and** an independent
content-integrity check in place. **Neither exists today.**

**6 · I-093 noted with approval of the family assignment** — *"a same-named field meaning different
units at the decision moment is the label-that-lies defect class, fifth member."*

**7 · RIDER A CLOSES.** Its record is the parallel run's evidence, the merge, and this ruling.
Delivered against a $6.00/month approved spend: **coverage 37.14% → 98.43%**, every gap eliminated,
and a data-integrity control **nobody designed and nobody asked for.**

**8 · Rider C dispatched — Execution & Operations, Sonnet.** The casebook harvest, against the
casebook's own bar: *"a case must teach a rule that applies outside the system that produced it."*

**The CIO's brief states plainly that Sprint 2 filed nearly fifty issues and did not produce fifty
cases, and that a harvest which turns the issue log into a longer issue log has failed** — four to
eight expected, three accepted if only three can be defended. **The seat is asked to report what it
rejected and why, because that judgment is the deliverable as much as the cases are.**

Seven candidate seams offered as input rather than conclusion, of which the CIO judges two the
sprint's real yield: **"a control that is asserted rather than computed is not a control"** — four
costumes, now standing doctrine at `GATES.md` §4.7.2 — and **the implementer who held a correct
one-line fix for 46 red tests and filed an issue instead**, which is the pre-authored test regime
converting an author's error into a filed defect rather than a permissive statistic in a live gate.

**9 · Budget.** **19 of 30 · 11 of 12 Opus.** Freely allocable Opus **zero**; DA reserve sealed and
never spent — **by design, not by omission.** §5 dead-man: **8 invocations remain.**

**Review date:** sprint close, 2026-08-11.

---

# ═══ SPRINT 3 ═══ Standing Order 002 in force from 2026-08-10

## S3-D-001 · 2026-08-10 · Sprint 3 opens · the registration act dispatched

**1 · Standing Order 002 SIGNED and in force**, `ops/STANDING-ORDER-002.md`, commit
`6e671d8b5a942b6b6379ab4836cdcd67eab0b08d`. Audit citation corrected at filing: the
*decided differently* finding attaches to **entry 14**, not entry 3.

**2 · THE HARNESS FACT THAT DEFINES THE WHOLE SEQUENCE, verified before dispatching rather than
assumed.** `TrialRegistry.open_hypothesis` **is the seal** — *"P1: on first registration, computes
`prereg_sha256`"* [measured, `registry.py`]. **Registration and sealing are one operation.**

**Consequence:** the registration act **cannot precede C2 and C3 — it is the thing they gate.** The
Principal's instruction to *"register Stage 1 at 47… and take PREREG-002 to its seal through C2, C3,
and the blocking set"* is therefore executed in that order and not in the order the sentence reads.
**Had the CIO taken "register" as a first step, it would have fired a §4 seal interrupt on Sprint
3's opening dispatch and frozen a document whose blocking set is still five items long.**

**3 · First dispatch — Director of Research, Opus, and it registers nothing.** Three tasks:

- **`GATES.md` §4.7.2 applied to the firm's own first family**, limit by limit, not sampled. Each
  limit resolves to a named binding field, a harness code path, or **"nothing reads this — it is
  prose."** The brief states that **category (c) is the deliverable, not a failure** — the doctrine
  was written by this seat and is now turned on its own document.
- **I-105 discharged** — Stage 1 registered at 47, with §10.5.2's Stage 2 language surviving only as
  a registered contingent-extension event under SPEC-003's generic form, **or struck before
  sealing.** SPEC-003's `test_tbe_15` already reproduces §10.5.2's table exactly **without knowing
  the document exists**, so Stage 2 is written as a plain instance of a generic mechanism.
- **The registration payload** — all sixteen binding fields with final values, as a separate
  artifact. **This is I-105's lesson in its operative form: prose is not registration, and a payload
  the Principal can execute without interpreting is the only thing that discharges it.** Where prose
  and payload could diverge, the payload governs and the seat says so.

**4 · What the CIO forbade explicitly, and why it needed saying.** **Do not call
`open_hypothesis`. Do not register. Do not seal.** `book/registry.db` must still read 0/0 on
return. The temptation is real — the sprint's first objective is *the registration act*, the
Principal has authorized the number, and a seat could reasonably read its dispatch as licence to
perform it. **It is not.** C2, C3, C7, C8, C11 remain blocking.

**5 · Sequence to the seal.** R-004 → **C2** Gate 0 intake verdict (Validation, Opus) → **C3**
Red-Team memo (Devil's Advocate, the sealed §2 reserve, **submission-gating and not skippable**) →
**the seal itself, which is a §4 interrupt and the Principal's act.** C7, C8, C11 resolve along the
way or the seal waits again.

**6 · Budget, Sprint 3.** **1 of 30 · 1 of 12 Opus** — drawn from the 9 freely allocable. Insurance
**2 of 2 intact**; DA reserve sealed. §5 dead-man: **9 invocations remain** since sign-off.

**Review date:** on R-004's return.

---

## S3-D-002 · 2026-08-10 · R-004 lands · §4 INTERRUPT — I-130 · the §4.7.2 audit is the sprint's first real finding

**1 · §4 HARD INTERRUPT. Trigger: *"any issue filed HIGH."***

**I-130 · HIGH — sealing `n_inherited = 0` would have made PREREG-002's own Stage 2 unlock table
permissive by up to eight trials, at exactly the two rungs where the family is in trouble.**
`gates.py:565` computes `declared_ceiling_base = n_inherited + sealed`, and SPEC-003's own
`test_tbe_15` fixes `base = 54 = 7 + 47`. At `n_inherited = 0` the base is 47, and §10.5.2's table
**admits 30 where it declares 23, and 8 where it declares 1.**

**The Director's own characterization, and it is exact: "It is I-105's defect one field over, and
would have survived I-105's own repair."** The sprint's first objective was to discharge I-105;
discharging it correctly surfaced a second instance of the same defect in a neighbouring field.

**Discharged in the same revision — the payload carries `n_inherited = 7`.** The seat **reversed
its own earlier position** (`N_conditioning` had been the one field it judged uncarried) and took
the cost deliberately: **enforced `N` becomes 54/86**, feeding DSR and MinBTL, so **§10.3's
0.13-year I-027 residual is paid rather than mitigated.** A seat tightening its own family's
constraint, against its own prior reasoning, before anyone asked.

**2 · THE §4.7.2 AUDIT IS LARGER THAN THE INTERRUPT, AND THE CIO RATES IT THE FIRM'S MOST
IMPORTANT FINDING TO DATE.**

> **Nine of the sixteen binding fields are sealed and read by nothing.** Being in `_BINDING_FIELDS`
> means a field is **hashed**, not **read**. `prereg_sha256` is tamper-evidence; **enforcement is a
> different code path, and for these fields it does not exist.**

**Two claims the CIO verified independently rather than relaying** [measured]:

- **`universe`, `horizon` and `success_criteria` have zero consumers anywhere in
  `harness/castellan/` outside `registry.py`.** Those three fields are **where a pre-registration
  puts its methodology** — K3's "exclude nothing", no-winsorization, `w_max`, the capacity screen,
  5% ADV, `ppy`, the ML-2 assertion, plateau-centroid-only, F-002's "evaluated ONCE", all eleven
  disclosure lines. **They are precisely where the harness does not look.**
- **`published_signal_haircut_applied` appears only as schema, signature and hash input. No code
  path applies it.** And §5.4 derives the family's **entire `t(α) ≈ 6.0` burden** from that number
  — the thing §11.6 calls ***"the largest single hurdle this family faces."***

**And the one that should be read twice:** no harness path evaluates a **kill condition** on any
date, for any family. KC-002 — the binding kill condition, signature-required, with an absolute
2027-01-31 observation date — is enforced by nothing. The seat's sentence: **"Clause 5's 'silence
is a kill' is itself defeatable by not running it."**

**This is `GATES.md` §4.7.2 turned on the firm's own first family and answering honestly.** The
doctrine says *a control exists where the harness reads it, and nowhere else.* Applied here, most
of what PREREG-002 calls a control is prose. **The seat states the correct conclusion and the CIO
endorses it: most of these cannot be mechanised and should still be written down — what must stop
is the document describing them as controls.**

**I-133 is rated MEDIUM by the Director as a disclosure finding. The CIO does not re-rate it** —
unlike I-022, no specific new dependency makes it produce a wrong PASS — **but records that its
severity reflects its class and not its scope**, and surfaces it to the Principal on that basis.

**3 · I-105 discharged, and the disposition was chosen rather than defaulted.** **Stage 1 at 47
with Stage 2 as a registered CONTINGENT unlock event**, not struck. The reasoning is the sharp
part: striking would leave 47 flat with no route above it **but a DISCRETIONARY extension, which
under B-14 requires a person's countersignature rather than arithmetic's** — and **"replacing an
arithmetic gate with a human one is strictly worse."** Stage 2 is written as a plain instance of
SPEC-003's generic mechanism, self-issued and **safe to self-issue because B-16 recomputes and
never trusts the event.** I-104 conformed in the same edit.

**4 · Two of the four suite reds now bear on this family, and did not before.** `test_h7` and
`test_h8` grade whether a **seeded denominator reaches DSR and MinBTL** — inert at
`n_inherited = 0`, **live at 7.** They are Validation-owned, still red, and **Validation has no
Opus in Sprint 2's closed budget and one unspent unit's worth of Sprint 3 attention not yet
allocated.** Raised by the seat as a consequence of its own revision, not as a request.

**5 · I-045 declined a fourth time, correctly, with the three rulings C2 needs named:** whether
dropping SOL is a remedy or a scope reduction — *"removing the one symbol the firm caught it on
removes the instance, not the exposure"*; whether K7 option (1) covers the residual given that
`DATA-VERIFY-002` verified the **cadence** dimension only; and whether I-045 closes at intake or
**survives the seal as a standing disclosure** — the seat's own view, offered as not decisive,
being that it survives.

**6 · Blocking set unchanged: C2, C3, C7, C8, C11.** R-004 clears none and creates no sixth. C13
extended by four. **C10's weight rises again** — I-132 compounds I-022: the latch is fixed, and
`log_trial` still reads no budget, so **the door is only inspected after the fact.**

**7 · Verified independently** [measured]: `book/registry.db` **0 hypotheses / 0 trials** — nothing
was registered, nothing sealed, exactly as instructed. `harness/` untouched. Payload delivered at
360 lines with `trial_budget = 47` and `n_inherited = 7`.

**8 · C2 NOT dispatched.** I-130 changed a sealed-payload value the Principal has not seen —
`n_inherited` 0 → 7 — and C2 would rule on that payload. **Sending Validation to issue an intake
verdict on a figure under an open interrupt repeats the error the CIO avoided twice in Sprint 2.**
It goes on the ruling.

**9 · Budget.** **2 of 30 · 1 of 12 Opus.** Insurance 2 of 2 intact; DA reserve sealed. §5
dead-man: **8 invocations remain.**

**Review date:** on the Principal's ruling on I-130.

---

## S3-D-003 · 2026-08-10 · I-130 and I-133 ruled · relabeling dispatched alone, not in parallel

**1 · I-130 approved; `n_inherited = 7` enters the payload.** The Principal recorded the finding's
shape as doctrine, and it generalizes past this family: **I-105's class is a field-by-field
disease; every sealed numeric field must be asked "what does the harness read here, and what does
zero mean."** The Director reversing its own position against its own family's interest, unprompted,
is recorded **as conduct.**

**2 · I-133 sustained as filed at MEDIUM, and the remedy is a LABELING mandate, not a
mechanization mandate.** The seat's conclusion adopted verbatim. Binding on R-005 before C2:

| Class | Requires |
|---|---|
| **(a) harness-enforced** | named field, named code path |
| **(b) procedure-enforced** | named executor, named cadence, named artifact |
| **(c) declared commitment** | binding as record; audit and adversarial review only |

**No limit may describe itself as a control without carrying its class.** The Principal's reason
for putting it before C2 rather than after: *"Validation grading prose-as-controls would have been
a wasted unit and a worse precedent."*

**The CIO added one guard the mandate did not state**, because class (b) is the one that will be
abused: a limit is (b) only if **executor, cadence, and artifact can all three be named.** *"The
Director will check"* is not a cadence and produces no artifact — **that is (c) wearing (b)'s
clothes.** And the brief states plainly that **class (c) is a full and honourable answer, not a
demotion**: a document honestly declaring thirty commitments is stronger than one implying thirty
controls and having nine.

**3 · The kill-condition gap gets an executor.** *"'Defeatable by not running it' cannot describe a
signature-required clause."* Two acts, and **`ops/STANDING-ORDER-002.md` §6 is amended now** rather
than at sprint close:

- **Validation specs a harness kill-condition evaluator this sprint** — reads registered KC fields,
  evaluates every clause on invocation, **exits nonzero on any firing *or* on inability-to-evaluate**,
  per the exit-code pattern the merge script proved. Sonnet implements red-first. **Not yet
  dispatched — see §4.**
- **Until it lands, KC evaluation joins the weekly Friday `[PRINCIPAL]` ritual**, and it is written
  into the order **carrying its three class-(b) fields** — executor the Principal, cadence weekly
  Friday, artifact the pasted evaluation. **The mandate applied to the mandate's own remedy.**

**4 · ONE OPUS DISPATCH, NOT TWO — and the reason is the audit.** The relabeling and the KC
evaluator spec are independent, touch different files and different seats, and could have run in
parallel. **They did not.**

**Entry 14 — concurrent Opus at zero slack against a demonstrated termination mode — is the single
entry the §7 audit decided differently**, and its price was 42% of Sprint 2's Opus tier. **Repeating
it in Sprint 3's third dispatch would mean the audit changed nothing.** The relabeling is on the
critical path to C2; the KC evaluator is not. **It goes second.**

**5 · §2.2 flag: this ruling carried no headroom note.** Every Principal message is to open with
`[usage: session X% · weekly-opus Y%]`. The last reading was **`58% / 18%`, several exchanges and
four calendar days ago** — far past the ~2-hour staleness bound, so **headroom is UNKNOWN under
§2.2** and the conservative posture applies. **No termination has occurred in Sprint 3, so the
posture's specific prohibition does not bite** — but combined with the entry-14 finding it is a
second independent reason the parallel dispatch was declined. **Requested for the next message.**

**6 · Sequence to the seal, unchanged and now explicit:** **R-005 relabeling → C2 → C3 on the
sealed reserve → registration-as-seal, a §4 interrupt and the Principal's act.** `test_h7`/`h8`
going live at `n = 7` joins Validation's queue with the four reds.

**7 · Budget.** **3 of 30 · 2 of 12 Opus** (2nd of 9 free). Insurance **2 of 2 intact**; DA reserve
sealed. §5 dead-man: **8 invocations remain.**

**Review date:** on R-005's return.

---

## S3-D-004 · 2026-08-10 · Watchtower cycle 1 · a Charter clause decreed under §2 · two items queued

**1 · CHARTER CLAUSE DECREED UNDER §2, recorded verbatim:**

> **Paper is a property of credentials and network, never of an instruction — while the book is
> paper, no credential with trade scope exists.**

**The CIO records what this is, because it is larger than an operational note.** It is
`GATES.md` §4.7.2 — *a control exists where the harness reads it, and nowhere else* — applied to
**the firm's single most important safety property.**

Paper-by-instruction is a **class-(c) declared commitment**: binding as a matter of record,
enforced by audit and by every seat's willingness to obey a sentence. **Paper-by-absence-of-
credentials is class (a)**: enforced by the environment, and unaffected by what any instruction
says, any seat believes, or any future session forgets. **The decree converts the property from
the weakest enforcement class to the strongest**, and does so on the one property where a
class-(c) failure is unrecoverable.

**It also closes a route this sprint's own findings imply.** The firm has spent two sprints
discovering that asserted controls are not controls — I-022's annotation, I-053's decorative rule,
I-105's unregistered stage, I-133's nine unread fields. **"Do not trade real capital" was, until
this decree, an instruction of exactly that class.**

**Verified on the firm's side, within scope** [measured]. The decree governs credentials and
network, which the CIO cannot inspect — `~/.ssh/**` and `~/.aws/**` are denied under D-003 and the
CIO will not route around a deny to confirm good news. **What is checkable is the code**, and it
holds:

- **No order-placement path exists in `harness/castellan/`** — zero matches for
  `create_order`/`place_order`/`submit_order`/`createOrder`/`.buy(`/`.sell(`.
- **No key handling** — zero matches for `api_key`/`apiKey`/`api_secret`.
- **The ccxt surface is fetch-only** — `fetch_ohlcv` and `fetch_funding_rate_history`, nothing else.
- **`PaperBook` is the only book class.**

**So the property is defended twice**: by the absence of credentials, which the Principal
guarantees, and by the absence of any code that could use one, which the CIO has verified.
**Neither depends on an instruction.**

**Placement — NOT actioned, and the CIO wants one word before acting.** This is a Charter clause
and it currently lives **only in this decision record**, which is precisely the failure §7.3's
promotion path and I-094 exist to name. **The CIO has deliberately not edited `FUND_CHARTER.md`**:
§4 reserves any Charter amendment to the Principal, he decreed the clause rather than instructing
its placement, and the binding document is not one to amend on inference. **Say the word and it
goes into the Charter with its provenance; otherwise it stays here and is flagged at every close
until it moves.**

**2 · `.claude/settings.json` hardening pass — expected 08-12, hash to follow.** Auto-mode default
plus cross-session messaging, changelog-verified. **The CIO will verify it against `HEAD` on
receipt of the hash and not before**, per this firm's standing practice: **two of the three
artifacts asserted as committed in Sprint 2 were not there.** Nothing is assumed in force until the
hash resolves.

**3 · Leakage-sentinel spec request queued for Validation, sequenced after the seal path** — i.e.
after **C2 → C3 → registration-as-seal**. Not dispatched. **Opus impact stated now so the sprint's
arithmetic stays honest:** the free tier is 9, two are spent, and the committed path already claims
**C2**, the **KC evaluator spec**, and now the **leakage sentinel** — three of the remaining seven,
before any contingency and before Gate 1 evaluation work that objectives 2 and 3 will require.

**4 · Budget.** **3 of 30 · 2 of 12 Opus**, unchanged — this entry consumed no invocation.
Insurance 2 of 2 intact; DA reserve sealed. §5 dead-man: **8 invocations remain.** R-005 is in
flight.

**Review date:** on R-005's return, and on the settings hash.

---

## S3-D-005 · 2026-08-10 · A5 placed in the Charter · the hardening pass prepared, and four of its own inputs found wrong · CASE-15

**1 · THE WORD CAME. A5 IS IN THE CHARTER.** S3-D-004 §1 held the placement pending one word from
the Principal; the word was given — *"adopted now as a Charter clause, my §2 authority, effective
immediately."* `FUND_CHARTER.md` is now **v1.2**, the clause sits in **§3.1** where capital is
governed, and **Appendix D carries A5** with its provenance.

**The clause text expanded between the decree and the placement, and the later text governs.**
S3-D-004 recorded: *"Paper is a property of credentials and network, never of an instruction —
while the book is paper, no credential with trade scope exists."* The placement instruction adds
**network topology** and a third sentence absent from the decree: *"Any credential grant with trade
scope is a §2 reserved act requiring a Principal decision record."* **That sentence is the
operative addition** — the decree described a present state, and this makes the *transition out of
it* a reserved act. A state can be true and then quietly stop being true; a reserved act cannot be
performed without a record.

**One refinement recorded rather than absorbed.** S3-D-004 classes paper-by-absence-of-credentials
as **class (a)**. The placement instruction says **class-(a)-adjacent by construction — enforced by
what doesn't exist.** The Charter note adopts the latter and states why: **no code evaluates this
clause.** It holds because the firm owns no funded key, which is a fact about the world, not a
mechanism in the repo. It is stronger than class (a) while the fact holds and **degrades to class
(b) the instant a credential with trade scope is created** — so the moment of the grant is the
moment the control needs a named executor. Filing it as class (a) proper would put it in the same
bucket as controls a test can fail, and nothing here can fail a test.

**2 · THE HARDENING PASS IS PREPARED, NOT COMMITTED** — `ops/HARDENING-2026-08-14.md`, diff in the
working tree against `.claude/settings.json`, for the Principal's commit with his own verification.

**Four claims carried into the pass from the Watchtower report were wrong, and the pass caught them
because it re-fetched rather than trusting the intake.** This is the firm's own rule — a fetched
claim is not a checked one — applied to the firm's own output one exchange after publishing it:

- **The version attribution was backwards.** All three named permission-boundary defects are in
  **2.1.223**, not 2.1.222. The report's "correction" was itself wrong and is **struck** in place.
- **2.1.222 contains something the intake missed**, and it matters more than what it found:
  *"Fixed worktree-isolated sessions and their subagents being able to run destructive git commands
  against the main checkout."* **That is CASE-3 recurring in the vendor's implementation**, in the
  mechanism this firm relies on for parallel-agent isolation.
- **Head is 2.1.227, not 2.1.226** — and 2.1.227 is already installed, so the upgrade is a no-op.
- **`defaultMode` was already pinned.** By the vendor's own statement the firm was **already
  unaffected** by the 14 August flip. The urgency was real; the exposure was not.

**3 · THE CIO CONTRADICTS THE AUTHORIZATION ON ONE POINT, WITH EXECUTED EVIDENCE.** The
authorization said the deny rules "incidentally convert the registry read-only default from Sprint 3
intention to mechanical fact." **They do not.** Three probes were run rather than described:
`Write` → `book/vaults/**` **DENIED**; `Write` → `book/registry.db` **DENIED**; and
`os.access(...)` through an allowed Bash call returns **`True` for both**. The deny binds the
`Write`/`Edit` **tools**; the process keeps filesystem write access, and `Bash(python3:*)` and
`Bash(sqlite3:*)` are on the allow list **because that is how the harness legitimately writes the
registry.** What was bought is real defense-in-depth against a classifier approving a plausible
`Write` — and it is not read-only. **Registry read-only remains a Sprint 3 intention**, and
mechanical enforcement belongs in the store, per Ruling 001. Recording it as achieved would have
made an objective look met that is not.

**4 · ONE ITEM OF THE FOUR COULD NOT BE APPLIED AND IS NOT PRETENDED CLOSED.**
`crossSessionInbound: "refuse"` is **rejected by the 2.1.227 settings validator at project scope**
(*"Unrecognized field"*) though the changelog and the docs both say it exists. It was **not** written
under `permissions`, where it would have validated silently and quite possibly enforced nothing —
CASE-9 by construction. **Gap G-1 is open: the cross-session injection path into Validation, Risk
and the Devil's Advocate is not closed.** Recommended next step is a user-scope attempt by hand; if
that also fails, it goes to the Issue Log as unreachable on this build. Gaps G-2 (process-level
writability), G-3 (the version floor is a document, not a mechanism — class (b)) and G-4
(`settings.local.json`, 76 allow entries, untracked, higher precedence, unreviewed) are recorded in
the same document.

**5 · CASE-15 FILED** — *the guard that counted the wrong side.* The Watchtower's own first run
destroyed 100% of its payload while a fan-in guard correctly reported 6/6 fetchers and zero gaps.
**Distinguished from CASE-4 in the case itself:** CASE-4's fix was to add verification by output and
fan-in counts, and that fix was already adopted and running here. It worked. The residual failure is
**correctly-placed verification of the wrong quantity** — the harder version, because the green
signal is genuine. Rule adopted verbatim as instructed: **a fan-in guard must count what leaves the
stage it guards, not what arrives at it.**

**6 · LEAKAGE SENTINEL — no change.** Queued for Validation per S3-D-004 §3, sequenced after the
seal path, not dispatched, Opus impact already stated there.

**7 · ONE DISCREPANCY THE CIO WILL NOT RESOLVE SILENTLY.** The authorization sequences the sentinel
after *"R-004 → C2 → C3."* **R-004 landed at S3-D-002**; the item in flight is **R-005** (S3-D-003,
the three-class relabeling), and S3-D-003 §6 states the sequence as *"R-005 relabeling → C2 → C3 →
registration-as-seal."* Read as R-005 the sequencing is unchanged and nothing is blocked. Flagged
rather than corrected, because it is the Principal's sequence to state.

**8 · Budget.** **3 of 30 · 2 of 12 Opus, unchanged** — the Watchtower cycle, the hardening pass and
this entry consumed **no seat invocation**. Watchtower fetch/verify ran on workflow subagents, which
are not firm seats and draw on no seat tier. Insurance 2 of 2 intact; DA reserve sealed. §5
dead-man: **8 invocations remain.**

**Review date:** on the settings hash, and at Watchtower cycle 2 (2026-08-17) for gap G-1.

---

## S3-D-006 · 2026-08-10 · R-005 lands · §4 INTERRUPT — I-140, HIGH and DATED TO TOMORROW

> **Renumbered S3-D-005 → S3-D-006 on 2026-08-11.** Two sessions wrote `S3-D-005` into this
> ledger on the same day: the watchtower session at **19:26:52** (`fdc87ba`) and the CIO at
> **19:29:12** (`82c436b`). **The watchtower entry landed first and keeps the number; the CIO
> yields, as it did at S2-D-002 when it renumbered its own entry rather than the Principal's.**
> Consequence to state rather than leave: the Director's live R-006 brief carries the dispatch tag
> `S3-D-006`, which now names *this* entry. **That tag is stale; R-006's record entry is S3-D-007.**

**1 · §4 HARD INTERRUPT. Trigger: *"any issue filed HIGH."* This one has a deadline of 2026-08-11
— tomorrow — and the CIO leads with it for that reason.**

**I-140 · HIGH — `I-034` / condition precedent **C1** is IMPLEMENTED, and PREREG-002 describes the
pre-repair cost model at six sites.** One of those sites is §14's condition precedent, which reads:
*"implemented by sprint close, **2026-08-11**. If unresolved by that date, the family is
**ADMITTED-AS-EXPLORATORY only**"* — and ADMITTED-AS-EXPLORATORY is *"pre-declared ineligible for
Gate 1."*

**The repair landed on 2026-07-29, twelve days ago.** **The family would have been downgraded
tomorrow, permanently, under P7, on a false premise** — not because the work was undone but
because the document never learned it was done.

**Verified independently by the CIO before recording** [measured]: `costs.py` carries
**`CRYPTO_PERP_TAKER`** (line 120, no funding term) and **`CRYPTO_SPOT_TAKER`** (line 137, D-013
§1); `carry.py` exposes **`carry_breakeven_bps_annual`**; **25 carry tests pass.** The claim holds
at source.

**Residual, correctly retained:** defect (d) — no `CostModel` field for liquidation risk — stands
as **class (c) C-25**. And the breakeven is now **unstated, not unstateable**: `carry_breakeven_bps_annual`
exists, and **one trial inside Stage 1's 47 discharges house rule 5.**

**2 · The relabeling: 61 limits classified — 20 (a) · 7 (b) · 34 (c)**, and the register sits **in
the sealed document at §10.11**, not in a memo about it. The seat's reason is the right one: *"the
next reader needs the class beside the limit, not a pointer to it."*

**3 · THE FIELD PARTITION IS SHARPER THAN THE ORIGINAL FINDING, AND WORSE.** Corrected to
**5 (a) / 11 (c)** of sixteen — and the mechanism is the part to keep:

> **`statement`, `mechanism` and `falsifier` are (a) on *existence* and (c) on *content*.**
> `registry.py:262–268` raises on the empty string **and reads no further.**

**So F-002's four legs, `α = 0.0013`, the 1,800-bar floor and the 1.3×10⁻⁴ joint survival rate all
sit in a field the harness guarantees only to be non-empty.** The seal proves something was
written. It proves nothing about what.

**4 · No (a) claim failed — and the findings ran the other way, which the CIO did not anticipate.**
The seat re-read every call site including the one it expected to fail (`verify_prereg` is invoked
*by* `evaluate_gate1`, so integrity is (a), not (b)). **Both surprises were limits the document
said were NOT enforced and which ARE** — I-034 above, and **I-022, repaired in code and open in the
log.**

**On I-022 the seat corrected itself against its own interest and said so:** C10's weight was
raised at R-003 **and again at R-004, both after the repair shipped on 2026-08-05**, and *"it should
never have been raised the second time."* The correction **runs in the family's favour**, and the
seat — which built the two-stage budget and would benefit from overstating its protection — **states
it for that reason rather than in spite of it.** The precise position is retained: **prevention
none; detection and refusal automatic, per trial, with the offending trial named** (I-132 stands).

**5 · A wrong count propagated into the CIO's own dispatch.** §10.10's *"nine zero-consumer fields"*
is **eight** — the 9 was §9.2's count of category-(c) **limits** transplanted into a column counting
**fields.** Two denominators, one number. **It had already reached S3-D-003's mandate, which
directed the relabeling of "all nine zero-consumer binding fields."** The CIO repeated a figure it
had not checked against its own roster. **I-141, MEDIUM — third instance of the class, and not LOW
precisely because it propagated.**

**6 · The haircut is class (c), explicitly, at the points of reliance and not only at the point of
declaration.** The gap is **exactly 2×**: `evaluate_gate1` computes `t_gate ≥ 3.0` on un-haircut
returns while §4.6 sets the equivalent of 6.0. **§19.3's order-20 composite is one class-(a)
multiplier × one class-(c) multiplier** — the 3.3× I-050 correction is shipped and unavoidable at
`stats.py:153`; the 2× haircut has no code path and an unruled **C5**.

**7 · §19.3's point estimate does not move. Its failure mode does, against the firm.**

> **If C5 is never ruled and no seat applies §4.6 by hand, this family can be reported PROCEED at
> half the Charter's bar.**

**That branch was always there. The document could not see it while it described prose as a
control.** The CIO records this as the labeling mandate's first substantive yield: relabeling
found a *permissive path*, not merely a vocabulary problem.

**8 · The payload is unchanged, and the seat's reason for not changing it is the entry to keep.**
It went looking for a change, found the candidate — rewriting `published_signal_haircut_applied` to
match what the harness actually does — and rejected it: **"adjusting a declaration to match the
enforcement is the I-046 error inverted."** `trial_budget = 47`, `n_inherited = 7`, unchanged.

**9 · Two promotions attempted and demoted, which is the (b) guard working:** F-002's E2 *"evaluated
ONCE"* (*"the ledger is produced by the act being limited, not by any check on it"*) and §12.8's
*"no hand-rolled number"* (nothing refuses a literal). **Both are (c).**

**10 · Verified** [measured]: registry **0 hypotheses / 0 trials**; `harness/` untouched; no seal,
no registration, no vault, no issue closed, `test_h7`/`h8` untouched.

**11 · C2 NOT dispatched. I-140 must be ruled first, and it is dated to tomorrow.** C1 is a
condition precedent *on the intake verdict C2 would issue*; sending Validation to rule while C1's
status is contested and its deadline is 24 hours out would produce a verdict needing re-ruling.

**12 · Budget.** **4 of 30 · 3 of 12 Opus** (3rd of 9 free). Insurance 2 of 2 intact; DA reserve
sealed. §5 dead-man: **7 invocations remain.**

**Review date:** on the Principal's ruling on I-140 — **before 2026-08-11.**

---

## S3-D-007 · 2026-08-11 · Watchtower session boundaried · a cross-session key collision found and yielded

**1 · Disclosure recorded: `fdc87ba` was authored by the watchtower session (personal ops) under
the Principal's instruction.** Charter v1.2, CASE-15, adoption ledger. **Going forward that session
writes only under `ops/watchtower/`, and any other write from it is an incident.**

**2 · Verified as usual** [measured]. `fdc87ba` touched **five paths, four of them outside
`ops/watchtower/`**:

| Path | |
|---|---|
| `FUND_CHARTER.md` | A5 at v1.2 — **verified present in `HEAD`** with its Appendix D provenance row |
| `logs/DECISION_RECORD.md` | +91 lines — **the collision, see §3** |
| `ops/CASEBOOK.md` | CASE-15 |
| `ops/HARDENING-2026-08-14.md` | the hardening pass, **prepared, not applied** |
| `ops/watchtower/watchtower-2026-08-10.md` | in scope |

**Those four writes were authorized when made** — under the Principal's instruction, before the
boundary existed. **They are not incidents and are not recorded as such.** The boundary applies
prospectively, and **the CIO notes that under it, four of that commit's five paths would now be
incidents** — which is precisely why the boundary is worth having.

**3 · CROSS-SESSION KEY COLLISION — two `S3-D-005` entries, and the CIO yields.**

The watchtower session wrote `S3-D-005` at **19:26:52**; the CIO wrote `S3-D-005` at **19:29:12**.
**The watchtower entry landed first and keeps the number.** The CIO's R-005 entry is renumbered
**S3-D-006**, on the same principle it applied at S2-D-002: **when two sessions collide in a ledger,
the CIO renumbers its own entry, not the other party's.**

**Stated rather than left to be discovered:** the Director's **live** R-006 brief carries the
dispatch tag `S3-D-006`, which now names the R-005 record entry. **That tag is stale. R-006's
record entry will be S3-D-007's successor, S3-D-008.** A dispatch tag is a label on a brief; the
ledger governs.

**4 · The boundary is the structural fix, and the collision is the evidence for it.** Sprint 2's
numbering collisions were one CIO writing into ranges it had issued to seats — fixed by allocating
disjoint ranges at dispatch. **This one is a different mechanism: two independent sessions, neither
aware of the other's writes, appending to one file within three minutes.** Range allocation cannot
fix that, because neither session issues ranges to the other.

**What fixes it is exactly what the Principal has just done** — confining the watchtower session to
`ops/watchtower/`, so the two sessions no longer share an append target. **The CIO therefore
proposes no additional mechanism**, and records that it considered a `S3-W-` prefix and rejected it:
**a namespace for writes that will no longer occur is machinery for a problem the boundary already
removes.**

**5 · `ops/HARDENING-2026-08-14.md` noted, not verified.** The hardening pass is **prepared and
dated 08-14**, and the settings commit itself has not landed — **the hash is still outstanding.**
The CIO's standing position is unchanged: **nothing is treated as in force until the hash resolves
against `HEAD`**, because two of three artifacts asserted as committed in Sprint 2 were not there.
The watchtower session reporting that **four of its own inputs were wrong** is noted as the reason
that position exists.

**6 · Budget.** **5 of 30 · 4 of 12 Opus**, unchanged — this entry consumed no invocation.
Insurance 2 of 2 intact; DA reserve sealed. §5 dead-man: **7 invocations remain.** R-006 is in
flight.

**Review date:** on R-006's return, and on the settings hash.

---

## S3-D-008 · 2026-08-11 · Hardening verified · §4 INTERRUPT — I-095, the denies are misaimed

**1 · `f54f9b9` verified in `HEAD`, pushed, `main` in sync with `origin/main`** [measured]. Four of
five components check out exactly as reported.

| Component | Verified |
|---|---|
| `disableAutoMode: "disable"` | **present** |
| Vault / registry write denies | **present — all four, and see §2** |
| `launchctl` / `git rm` allows | **absent from the project allow-list** (G-4 purge was local/user scope) |
| G-1 `crossSessionInbound` | **user scope — outside this repo; the CIO cannot verify it and does not claim to.** Retest 08-17 stands |
| **Version floor 2.1.227** | **NOT present as a key in `.claude/settings.json`.** Reported as *"(head, no-op)"*, so it may live at user scope or be enforced elsewhere — **but it is not in the file this commit touched, and the CIO records that rather than assuming** |

**2 · §4 HARD INTERRUPT — I-095, HIGH. The vault and registry denies cover the tool path nobody
uses and leave the path everybody uses.**

The four rules deny **`Write` and `Edit`**. **Nothing in this firm has ever written the registry or
the vault with `Write` or `Edit`.** Registry writes go through `TrialRegistry.open_hypothesis`,
`log_trial`, `log_event`; vault writes through `HoldoutVault.lock()` — **all invoked as
`python3`**, and the same file allows `Bash(python:*)`, `Bash(python3:*)`, `Bash(sqlite3:*)`,
`cp`, `mv`, `touch`, unqualified.

**The denies are live and correctly configured. They are misaimed.** The status line *"vault/registry
write denies live"* is true as written and **does not describe the protection a reader infers from
it.**

**This is the firm's own recurring defect arriving in the control plane.** I-022 annotated where it
should have failed; I-053 stated a rule the registry refuses; I-105 described a stage nothing
registers. **I-095 denies a tool nobody uses.** §4.7.2's test, translated: **name the path the deny
actually intercepts.** For these writes it intercepts none.

**3 · The CIO did not test it, and the reason is the rule itself.** Demonstrating the gap means
writing to `book/registry.db` or `book/vaults/` through `python3` — violating the 0/0 state every
dispatch this sprint has been required to preserve, and **routing around a deny to prove the deny
does not work.** D-003's standing rule is *queue it, don't work around it*, and **that rule does not
suspend itself when the target is the rule's own coverage.** Filed from configuration, marked
`[measured]` on the config and `[inferred]` on the exploit.

**Nothing is presently at risk** — registry 0/0, vault `.gitkeep` only. **The exposure begins the
moment the registry stops being empty, which is Sprint 3's second objective.**

**4 · `disableAutoMode` retained — the doctrine is worth keeping and generalizes.** The Principal:
**classifier nondeterminism in the control plane loses to enumerated rules.** Revisit if G-1 stays
open at cycle 2.

**That is `GATES.md` §4.7.2 applied to the permission layer** — a control exists where something
deterministic reads it. **The firm has now made the same choice four times**: computed over
narrated (A2), registered over described (I-105), credentials over instruction (A5), and enumerated
over classified (this). **Four domains, one doctrine, and the CIO records the convergence because it
is now the firm's most reliable predictor of which design will hold.**

**5 · The `fdc87ba` provenance note and the `ops/watchtower/` boundary were recorded at S3-D-007**,
including the cross-session `S3-D-005` key collision, which the CIO yielded. No re-recording needed.
**The hardening-doc commit reference is still outstanding** and will be verified on arrival.

**6 · Budget.** **5 of 30 · 4 of 12 Opus**, unchanged — this entry consumed no invocation. Insurance
2 of 2 intact; DA reserve sealed. §5 dead-man: **7 invocations remain.** R-006 in flight.

**Review date:** on the Principal's ruling on I-095, and on R-006's return.

---

## S3-D-009 · 2026-08-11 · I-095 sustained · the fix moves down a layer · doctrine named at §4.7.3

**1 · I-095 sustained, and the status line is corrected first.** The `f54f9b9` line now reads what
the commit actually bought: *"vault/registry denies cover the Write/Edit tool path only; the
`python3`/`sqlite3` path — the only path anything real uses — is ungoverned by the permission
layer."* **The protection a reader inferred does not exist, and the file now says so.**

**2 · The durable fix moves down a layer, and the Principal's reasoning is the part that
generalizes.** The permission layer **cannot** aim at this: `Bash(python3:*)` is how the harness
legitimately works, and *"python3 except when it touches the registry"* is **classification wearing
enumeration's clothes.**

So the registry and the vault **defend themselves in code, class (a)**: `registry.py` and the vault
open **read-only by default (SQLite `mode=ro`)**, writes requiring an **explicit per-invocation
grant** — an environment token or constructor flag the dispatch brief supplies. **Write authority
becomes something the CIO grants per task and the record shows.**

The Principal names its lineage: **this is Sprint 2's external-state policy — read-only default,
write-per-dispatch, sanctioned migrations — finally landing in its correct home.** CASE-3's rule,
arriving where it always belonged.

**3 · SEQUENCING — the CIO's call, and it holds the fix rather than parallelizing it.**

The bound is *"before first trials log"* — **objective 2 is the deadline, not the seal.** Trials
follow the seal, which follows C2 and C3: **at least three dispatches away. There is no schedule
pressure**, and therefore no reason to run a second long Opus dispatch beside R-006, which is in
flight.

**This is the third time this sprint the CIO has declined a defensible parallel Opus dispatch**, on
the entry-14 finding. Recorded again because the value of an audit finding is whether it changes
behaviour after the sprint that produced it — and **the honest test is declining when parallelizing
would be convenient, not when it would be reckless.** §2.2's headroom note is again absent from this
ruling; headroom is **UNKNOWN**, which is a second independent reason.

**Order:** R-006 returns → **registry/vault read-only spec** (Validation, red-first) → C2 → C3 →
seal → implementation lands → **then** first trials.

**4 · Opus arithmetic, stated because it is now the binding constraint.** **9 free, 4 spent, 5
remaining.** Committed: **C2**, the **dated-clause evaluator spec**, the **leakage sentinel**, and
now the **registry read-only spec** — **four of the five.** DA reserve holds C3.

**One free Opus unit remains for contingency and for every Gate 1 evaluation dispatch objectives 2
and 3 will require.** The insurance (2) is reserved against terminations and is **not** working
capacity. **The CIO flags now, not at close, that Sprint 3's objectives 2 and 3 are not obviously
fundable on the remaining tier**, and will bring a re-plan rather than discover it.

**5 · The version floor reclassified honestly, and it is a demotion the CIO endorses.** No key in
the committed file pins a version, so **"floor 2.1.227" is a class-(c) declared commitment verified
manually (`claude doctor`), not a control.** It upgrades to (a) only if cycle 2 finds a real pinning
mechanism. **G-1 unchanged: user scope, unverifiable from the firm's side, correctly unclaimed.**

**Both now sit in the Friday ritual** — `STANDING-ORDER-002` §6 extended to **four items**: merge,
dated-clause review, **I-095 gap review** (class (c) until the code fix lands), and **version-floor
verification.**

**6 · Hardening-doc reference closed, with one correction.** The ruling cites *"fdc87da's
predecessor"*; **`fdc87da` is not an object in this repository** [measured — `git cat-file -e`
fails]. The document is `ops/HARDENING-2026-08-14.md`, carried in **`fdc87ba`**, which the CIO
verified at S3-D-007. **The substance resolves and the hash in the ruling is a transposition.**
Recorded because this firm has spent two sprints on references that do not resolve — I-059's
dangling citations, I-120, and the fourth instance that nearly cost the family.

**7 · The convergence is countersigned as doctrine and has a name, now at `reference/GATES.md`
§4.7.3: *put the control where the machine reads, not where the reader infers.*** Four domains —
computed over narrated, registered over described, credentialed over instructed, enumerated over
classified.

**I-095 is recorded there as the doctrine's negative print**: stated correctly, implemented one
layer off. **The rule was enumerated, deterministic, correctly configured, and pointed at nobody.**
The separating test is written into §4.7.3 and is not *"is this control deterministic?"* but
**"name the path a real actor would take, and show this control on it."** A control that is
deterministic about the wrong path is, from the record, indistinguishable from one that works.

**Placed in `GATES.md` rather than the decision record**, per §7.3's promotion path — **the doctrine
outlives the order that produced it.** The casebook is directed to hold §4.7.3 and I-095 **together
at next harvest**: a doctrine and its own near-miss are worth more paired than apart.

**8 · Budget.** **5 of 30 · 4 of 12 Opus**, unchanged. Insurance 2 of 2; DA reserve sealed. §5
dead-man: **7 invocations remain.** R-006 in flight.

**Review date:** on R-006's return.

---

## S3-D-010 · 2026-08-11 · R-006 lands · §4 INTERRUPT — I-153, a kill condition that cannot be survived

**1 · §4 HARD INTERRUPT. Trigger: *"any issue filed HIGH"*, and separately *"any kill-condition
signature or restatement."***

**I-153 · HIGH — `forward_kill_condition` clause 5 terminates this family with CERTAINTY as
drafted.**

The field opens: *"Observation date = `C + 187 days` … the DRAFTED DATE IS NOT BINDING — the
formula is."* Clause 5 then reads: *"if the computation is not performed **on 2027-01-31** for ANY
reason … the family is killed by default."*

**At any seal after 2026-07-28, `C + 187 days` falls later than 2027-01-31.** So on 2027-01-31 the
computation is **not due**, will therefore not have been performed, and **clause 5 fires: registry
TERMINATED, no Gate 1 submission ever, not appealable.**

**This is strictly worse than I-140 on two heads, and the CIO states both:** I-140 **downgraded**;
this **kills.** I-140 fired on a premise that **happened** to be false; this fires on one that
**cannot be satisfied.** **A kill condition written to be undefeatable had become one that cannot be
survived.**

And **nothing evaluates it** — I-135 stands, no harness path evaluates a kill condition on any date
— so the failure mode is not a machine misfiring. **A Principal executing the sealed text correctly,
by hand, on the day, would read it and find the family dead.**

**The seat conformed the literal to `C + 187 days` and then refused to ratify its own repair**:
*"the repair runs in the family's favour, so it is not mine to ratify."* Routed to **C13(k)**, with
the alternative stated plainly — **Validation may require the literal sealed as drafted, in which
case the family accepts the shortened window and the Director writes the KILL memo on the day.**
Third time this seat has declined an authority that would have favoured it.

**2 · "R-005 corrected where readers look and not where the seal looks."** Three of the fourteen
sites were **inside §21, the sealed field block**, which R-005 never reached — including
`forward_kill_condition` **still carrying the exact 2026-08-11 ADMITTED-AS-EXPLORATORY sentence
that made I-140 a HIGH**, struck in §14's prose and left standing in the field, "corrected" by a
note forty lines further down the same string.

**A field is hashed as one string.** The seat's own summary is the finding: **I-105's doctrine run
backwards.** §4.7.2 says a control exists where the harness reads it — **and the harness reads the
field, not the prose the reader reads.**

**3 · The "six sites" cardinal was wrong at every reading, and it propagated into the CIO's own
brief.** I-140 says six; its own roster names seven; R-005's R26 names eleven; **the set is
fourteen.** It reached I-034's CLOSED entry and **S3-D-006's Task 1 heading, which the CIO wrote.**
**Second time this sprint the CIO has repeated a cardinal it did not check against its own roster**
— I-141 was the first. **I-150.**

**4 · House rule 5 costs 0–42 trials, not one — and the CIO is the one who wrote "one."** The
figure came from R-005's return, the CIO repeated it in the S3-D-006 brief without checking, and
the seat has now measured it: `carry_breakeven_bps_annual` takes a **callable**, evaluated once per
bracket end and once per bisection step, and the sanctioned usage makes each evaluation a
`run_backtest` call, which **logs a trial unconditionally.**

| Path | Trials |
|---|---:|
| **F-002 fires** (§19.3's own expectation) | **0** — returns before evaluating; the breakeven of a family below the hurdle **is** 0.0 by construction |
| Survives, `iters = 8` | **9** |
| Survives, shipped `iters = 40` | **41 — 89% of Stage 1 for a statistic containing no selection** |

**The seat intends to spend 9, survive-path only, and it does not fit: §15's Stage 1 sums to
exactly 47, zero slack.** Two shortcuts refused: narrowing the bracket is **"the I-037 operation
performed on the instrument built to avoid it"**; reconstructing `net(δ)` outside the engine
**breaches A2.** Routed to **C13(j)**, **I-151.** Asymmetry flagged for Validation: `gates.py`'s own
`breakeven_cost_multiplier` bisection **logs nothing**, and no ruling says whether the carry one
counts toward `N`.

**5 · C5 — the CIO's reading was right about one part of three, and the part it missed is the
substantive one.**

**Haircutting the return series is a no-op.** Sharpe, `t`, DSR, PBO, WFE, subperiod positivity and
P&L concentration are **all invariant to a positive scalar.** Only haircutting the *expected return*
halves `t`. **So C5 is a choice between a 2× hurdle and nothing** — and §19.3's order-20 composite
rests entirely on the branch **nobody has ruled.**

**Ratification is the Principal's, not Validation's**, and the seat's reasoning is this firm's own
doctrine turned one clause over: **"a ruling that doubles the bar without touching the constant is a
§4 reserved act wearing an interpretation's clothes."** `T_STAT_HURDLE = 3.0` never moves while the
effective bar moves between 3.0 and 6.0. **Escalated, not resolved. I-152.**

**And a ruling without executor, cadence and artifact is class (c) — I-143's permissive branch
survives it.** The labeling mandate applied to the remedy for the labeling mandate's own finding.

**6 · The blocking set was merging two kinds of block, and is now written separately.**
**Seal-blocking: C2 · C7 · C8 · C11.** **Verdict-blocking: C3 · C5 — and by §20's own column also
C4 and C10**, which the six-item framing dropped. The CIO's own S3-D-006 brief proposed the merged
six-item form and the seat **found otherwise on form**, correctly.

**7 · The sweep: 24 dated clauses. 2 evaluated by code. 3 class (b). 19 evaluated by a reader
noticing. 15 carry a premise false today** — thirteen of them because the document was drafted
against a same-day seal on 2026-07-28 that §20.1 abandoned on 2026-08-04 and never reconciled.

**§20.1's "Realistic seal date: on or before sprint close, 2026-08-11" is today**, with C2, C7, C8
and C11 open. Struck, replaced by a condition. **§11.1's 6.571-year span is an understatement at any
later `C` — the one stale date running *for* the family, which is why four revisions passed over
it.** The CIO records that asymmetry: **stale dates that cost the firm get found; stale dates that
favour it survive four passes.**

**8 · I-154 — the conforming-pass class, fifth instance, and the first that defeats its own audit.**
R23's row lists §11.4 among its changed clauses. **§11.4 was never changed** — it still carries
`2026-07-28` and *"the seal is intended for today."* **An auditor checking R23 against its own list
would tick §11.4 as done.**

**9 · Verified** [measured]: registry **0 hypotheses / 0 trials / 1 event**; payload **untouched
this dispatch**, `trial_budget = 47`, `n_inherited = 7`; `harness/`, `VALIDATION-*` and `book/`
untouched; `test_h7`/`h8` not approached; no seal, no registration.

**10 · Budget.** **6 of 30 · 5 of 12 Opus** (5th of 9 free). **4 free remain and 4 are committed** —
C2, the dated-clause evaluator spec, the leakage sentinel, the registry read-only spec. **Zero
uncommitted free Opus.** Insurance 2 of 2; DA reserve sealed. §5 dead-man: **6 invocations remain.**

**Review date:** on the Principal's rulings on I-153 and I-152.

---

## S3-D-011 · 2026-08-12 · Re-plan adopted · slip ruled in advance · row 1 dispatched

**1 · Re-plan adopted as delivered.** The consolidation approved **on its own test** — same owner,
same reviewer, same implementer, same layer; *"two specs would have been ceremony."*

**2 · The leakage-sentinel deferral carries a binding condition the CIO did not propose and now
records as tighter than its own recommendation:**

> **The sentinel lands before any family's first Gate 1 evaluation, whichever sprint that falls
> in.** *"Its entire purpose is upstream of gate credibility, and deferring it past the gate would
> convert a sequencing choice into a silent kill of the adoption."*

**The CIO proposed a deferral by sprint; the Principal converted it to a deferral by event.** The
difference matters: a sprint boundary is a date the firm can slide, and **an event boundary is one
it cannot.** The watchtower adoption ledger keeps its +60d review regardless.

**Interaction worth stating: the slip ruling and this condition are compatible only on the kill
path.** If F-002 fires there is no Gate 1 evaluation and the sentinel has room. **If F-002 survives,
objective 3 slips *and* Gate 1 evaluation moves to Sprint 4 — where the sentinel must land first.**
The two constraints do not collide; they queue.

**3 · THE SLIP IS RULED, VERBATIM, BEFORE ANY OUTCOME EXISTS:**

> **If F-002 survives, or if C2 returns findings requiring a further revision, objective 3 slips to
> Sprint 4 and the sprint closes on objectives 1 and 2.**

The Principal's rationale, recorded because it names the discipline rather than the decision: *"the
branch the tier cannot fund is the branch the document expects, and my own C5 ratification raised
its probability — ruling the slip after that ratification, before any outcome exists, is the same
pre-commitment discipline as KC-001's cut, applied to the schedule."*

**And the standard the sprint will be judged against:** *"a sprint that ends with a sealed family
and logged trials, having pre-declared that the verdict waits for funded evaluation, is an honest
sprint. One that improvises at close is not."*

**4 · The alternative declined, with the CIO's own reasoning adopted:** trading a known documentary
defect for a chance at a verdict **inverts the fortnight's entire evidence** — I-140 and I-153 were
each **one unread document from killing this family** — and **§11.1 is the one stale date running in
the family's favour, which the asymmetry doctrine makes the most important to fix, not the safest to
skip.**

**5 · Accounting note carried into the close, stated now.** Under this plan the **DA reserve spends
on C3** and **insurance stays termination-only**, so **one Opus termination on rows 1–4 consumes
half the insurance and two end the sprint's Opus work outright.** Analysis/authoring split,
pre-split sizing and the headroom protocol apply to **all four rows without exception.**

**6 · Row 1 dispatched — the harness self-defence spec — and the CIO named a tension in the brief
rather than discovering it.** The consolidation is *what paid for the re-plan*; §2.2's ~800-line
pre-split, if it bites, would **price the merged dispatch as two and un-do the saving entirely.**
The CIO projects under the threshold and **told the seat what to do if the projection is wrong**:
scope to what fits, defer the remainder with a **named boundary**, and say which — **not truncate,
not silently exceed.** *"A spec that is honest about its edge is worth more than one that covers
everything badly."*

**7 · The question the CIO added, and it is I-095's test turned on I-095's own remedy.** A seat that
can run `python3` can set an environment variable. **If the write grant is an env token, the seat
can mint its own** — I-103's *"the harness cannot authenticate anyone"* arriving in a new place.

The brief requires the specification to **name the path a real actor would take and show the control
on it**, and, if the honest answer is that the grant makes writes **deliberate and visible** rather
than **prevented**, to **say exactly that, in those terms, in the spec.** **A remedy for a misaimed
control that is itself described as more than it is would be I-095's successor** — and the CIO would
rather ship a modest control described precisely than a strong-sounding one described loosely.

**8 · Direction-blindness required by construction, not intention.** The Principal's mechanism for
the stale-date asymmetry: every dated clause checked against its premise **regardless of whom the
staleness serves.** The brief states the measured reason — **15 of 24 clauses carried false
premises, and §11.1, the one running *for* the family, survived four passes** — and the test:
**a checker a sponsor would be relieved to see pass is not direction-blind.**

**9 · Budget.** **7 of 30 · 6 of 12 Opus.** **3 free remain against 3 committed rows** — conformance
pass, C2, terminal-verdict memo. **Zero uncommitted free Opus.** Insurance 2 of 2; DA reserve sealed.
§5 dead-man: **5 invocations remain.**

**Review date:** on row 1's return.

---

## S3-D-012 · 2026-08-12 · Row 1 lands · §4 INTERRUPT — SPEC-004 §13 · the pricing call, ruled

**1 · §4 HARD INTERRUPT. Trigger: *"any finding by Validation… addressed to the Principal."***
No HIGH filed — I-160 through I-166 are **5 MEDIUM, 2 LOW**, verified on disk. **§13 carries three
items:**

- **The `f54f9b9` status line needs a SECOND correction when this lands**, and the seat supplies the
  exact text. **It is not "registry and vault are write-protected."** Its reason is the CIO's own
  brief turned back on it: *a remedy for a misaimed control described as more than it is would be
  I-095's successor.*
- **R-15 has teeth that will be felt before they are appreciated:** **one orphan row voids every
  subsequent Gate report**, and *"it will fire on a Friday."*
- **I-153's C13(k) ruling is still owed by Validation and this document does not discharge it.**
  *"It builds the checker for I-153's class; it does not rule I-153's instance, and it should not be
  read as answered."* **The CIO records that explicitly so the seal path does not treat C13(k) as
  cleared by a spec that never touched it.**

**2 · THE PRICING CALL — ruled at ONE unit, and the CIO states that this runs in the firm's favour
before defending it.**

**The projection did not hold: 857 authored lines against ~800, a 7% overrun** — and it held that
closely **only because the seat cut scope**, exactly as instructed. Uncut it projected past 990.

**Ruling: one unit.** §2.2's text is *"any dispatch **projected** past ~800 authored lines is split
into two invocations **at dispatch time** and priced as two."* **The rule binds the projection and
the splitting decision at dispatch time. It is a sizing control whose purpose is termination
insurance — limiting what a failure costs.** The dispatch completed. **Re-pricing delivered work
serves no part of that purpose, and would cost a second unit from three, forcing objective 3's slip
immediately and buying nothing.**

**The test the CIO applied to itself before ruling** — the same one §4.7.3 sets — is whether the
reading measures more of what the rule always claimed to measure. §2.2 claims to insure against
termination loss; post-hoc billing insures against nothing. **The reading is principled rather than
convenient, and "~800" tolerates 857 on its face.**

**Flagged for reversal without argument.** This is a §2 budget matter decided in the firm's favour
by the party the budget constrains. **If the Principal prices it as two, the CIO will not defend the
ruling — it will re-plan.** `[would-have-asked]`.

**3 · The scope cut, with its boundary named at clause E-25 — and what the seat refused to cut.**
Deferred: **what a firing *does*** (termination, downgrade, notification are not evaluated, stored,
or inferred from `kind`); the sponsor remediation workflow; and the **document-side clause surface**
— *"a clause living only in prose is caught only insofar as a registry field carries it; the remedy
is that clauses must be registered, not that a checker learns to read documents."* **That is §4.7.2
applied to the checker's own scope.**

**Refused: §4, the honest account.** *"A line budget eats that section first and it is what this
dispatch was actually about."* **The seat protected the section a schedule would have eaten and said
so.**

**4 · The honest answer the CIO demanded, delivered in the terms demanded.** The grant:

| | |
|---|---|
| **Prevents** | incidental writes (three occur in today's `__init__` before any caller expresses intent) · ungranted writes through any harness handle · writes of a class the grant did not name — **R-10 types the grant, so a `LOG_EVENT` grant cannot register a hypothesis** |
| **Detects, does not prevent** | a raw-path write — leaves `grant_id IS NULL`, reported as an orphan |
| **Does not prevent at all** | **a seat that decides to write.** A seat that can run `python3` can set the token and mint its own grant — **I-103 in a new place, filed again as I-161** |

Written into the specification in these words: **the grant makes writes DELIBERATE, TYPED and
ATTRIBUTABLE-BY-DECLARATION; it does not make them PREVENTED and does not AUTHENTICATE the
declarant.** **That is the sentence the CIO asked for and the one I-095's remedy needed to survive
its own test.**

**5 · Two constructions worth keeping past this family.** The grant row is **the first write under
its own grant** — *"no ordering exists in which a write precedes the record of its authority."* And
`evaluate_gate1` **prints orphans, chain integrity and head whether or not they are zero**, because
*"a control visible only when it fires is one nobody can confirm is running."* The chain's witness
is git: **`book/registry.db` is tracked** [CIO-verified].

**6 · Direction-blindness enforced by five mechanisms, none a promise** — a verdict vocabulary with
**no favourable member**; `test_dce_17` asserting via `inspect.signature` that **no parameter in the
module** matches `ignore|skip|allow|waive|suppress|exempt|except|only|severity|priority`, *"so the
request to silence one finding is refused before the conversation"*; no severity or ranking; report
order by field, never by verdict; and **the mirror-pair obligation** — every `fx_*_against` fixture
requires an arithmetic mirror `fx_*_for`, with a meta-test asserting the pairing is total.

**The proof case is `test_dce_21`: §11.1's 6.571-year span — the one stale figure that ran *for* the
family and survived four revision passes — must return `SPAN-DIVERGENT` exit 3 identically to its
overstating mirror.** The asymmetry the CIO named is now a test that fails if it recurs.

**Exit codes 4 > 3 > 2, inability outranking a firing**, *"because this seat ranks epistemic state,
not consequence."*

**7 · I-164 is the finding the seal path must absorb: 19 of PREREG-002's 24 dated clauses land
`UNCOVERED`, so the evaluator's first real run against this family is exit 4 — and that is the
correct answer.** The document's clauses are not registered, and **the remedy is registration, not a
more forgiving checker.**

**8 · Verified** [measured]: suite **272 passed / 50 failed / 322**; 46 of the 50 are **red by
design**, the 4 pre-existing ones counted separately *"so the two sets never merge"*; registry **0
hypotheses / 0 trials**; `harness/castellan/`, `book/vaults/`, `PREREG-002` and `DIR-RESTATE-*`
untouched.

**9 · Budget.** **7 of 30 · 6 of 12 Opus** — row 1 priced at one. **3 free remain against 3
committed rows**: conformance pass, C2, terminal-verdict memo. Insurance 2 of 2; DA reserve sealed.
§5 dead-man: **5 invocations remain.**

**Review date:** on the Principal's ruling on §13 and on the pricing call.

---

## S3-D-013 · 2026-08-12 · Pricing sustained with a ratchet · `f54f9b9` amended · two doctrines promoted

**1 · Pricing SUSTAINED at one unit**, and the Principal names why the disclosure mattered as much
as the answer: *"the disclosure pattern — ruled in own favour, offered for overrule, re-plan
promised if overruled — is exactly what §3 asks of a self-interested call."*

**A RATCHET ATTACHES, and the CIO records it as binding on itself:**

> **The 857-vs-800 near-miss is recorded. The next projection that lands over threshold prices as
> two, without appeal.** *"A sizing control whose projections keep grazing the line stops being
> conservative, and the second data point decides that, not this one."*

**This is the correct shape and the CIO would not have proposed it.** A single overrun is noise; a
pattern of overruns is a projector biased toward the answer it wants. **The ratchet does not punish
the first instance and removes the CIO's discretion on the second — which is where the bias would
show.** It is in force from now.

**2 · `f54f9b9`'s status line amended — the commit stands unrewritten per A3, and this entry is the
correction it points to.** Adopted verbatim:

> **The registry and vault are not write-protected.** The grant mechanism makes writes **deliberate,
> typed, and attributable-by-declaration** — it **prevents** incidental, ungranted, and wrongly-classed
> writes; it **detects but does not prevent** raw-path writes; **it does not authenticate the
> declarant.**

**This is the second correction to one status line**, and the Principal sets it as a standard rather
than a fix: *"I-095's remedy surviving its own test because it says so is the standard every future
control description is now held to."* **Every control this firm ships is now described by what it
prevents, what it merely detects, and what it does not touch — in those three registers, or it is
not described.**

**3 · C13(k) confirmed UNDISCHARGED and routed.** Validation rules I-153's **instance** inside C2's
absorbed scope at row 3, **with the alternative live for it to take** — requiring the drafted literal
and accepting a shortened window. **The seal does not proceed past an unruled C13(k).** The spec
built the checker for the class; **the instance ruling stays owed**, and the CIO has recorded it in
the seal path so no later session reads a class-checker as an instance ruling.

**4 · Two constructions promoted to standing design doctrine at `reference/GATES.md` §4.7.4**, under
§7.3's promotion path — **placed in `GATES.md` rather than left in the order, which expires:**

- **(i) The authority record is written by the act it authorizes.** *"No ordering exists in which a
  write precedes the record of its authority."* **Test: if the audit entry and the authorized act
  can fail independently, the audit is a hope.**
- **(ii) A control reports whether or not it fired.** *"A control visible only when it fires is one
  nobody can confirm is running."* **Test: name the output a reader sees on a clean run. If there is
  none, the control's clean runs and its non-runs are the same observation.**

The CIO added the two tests; the constructions are Validation's and the promotion is the
Principal's. **Both are §4.7.3 applied to a control's own reporting surface** — put the evidence
where the machine writes it, not where the reader would infer it.

**5 · The five-mechanism direction-blindness accepted as the mechanization the ruling required**,
with **§11.1's own stale span as its proof case.** **I-164 endorsed as filed:** exit 4 on first real
run is the correct answer — *"nineteen uncovered clauses is the truth about an unregistered
document, and the remedy is registration, not a gentler checker."*

**6 · Row 2 dispatched** — the Director's conformance pass. **The ratchet was stated to the seat in
its brief**, because a sizing rule the executing seat does not know about is a rule that cannot
change its behaviour.

**7 · Budget.** **8 of 30 · 7 of 12 Opus.** **2 free remain against 2 committed rows** — C2 and the
terminal-verdict memo. Insurance 2 of 2; DA reserve sealed. §5 dead-man: **4 invocations remain.**

**Review date:** on row 2's return.

---

## S3-D-015 · 2026-08-12 · Row 2 lands · THE RATCHET FIRES · the sprint's objectives are now unfundable

**1 · §4 HARD INTERRUPT — three HIGH: I-171, I-172, I-173.** Verified on disk: 3 HIGH, 4 MEDIUM,
1 LOW-MEDIUM, 2 LOW.

**2 · THE PRICING CALL — ROW 2 PRICES AS TWO. The ratchet fires on its first test, and the CIO
measured the footprint itself rather than accept either reading.**

The seat reported 1,106 total and **750 on the narrowest reading**, and — to its credit — **told the
CIO not to take its narrow reading as cover.** The CIO's own measurement, excluding the capture
daemon's 172 log lines (not the seat's work) and the machine-generated JSON/txt outputs:

| | Lines |
|---|---:|
| Authored prose into tracked files | 341 |
| The dated-clause register | 333 |
| **Analysis tooling the seat wrote** | **264** |
| **Authored total** | **938** |

**938 > 800. Over threshold. Priced as two.**

**The disputed term is whether authored tooling counts, and the CIO rules that it does.** §2.2 is
**termination insurance** — it sizes a dispatch by how much work a failure would destroy. **264 lines
of Python written and lost to a termination is work lost.** Excluding it would size the dispatch by
what survives review rather than by what is at risk, which is not what the rule insures.

**The seat named the ambiguity honestly and refused to shelter behind it** — *"'authored lines' is
itself undefined, the same defect class I filed as I-170, and the CIO should price this row as it
sees fit."* **The CIO resolves an undefined term against the firm, per the asymmetry doctrine: a
definitional ambiguity resolved toward "under threshold" is precisely the stale-term-that-favours-us
pattern this firm has spent two sprints cataloguing.**

**And the ratchet says "without appeal." It is not appealed.**

**3 · THE CONSEQUENCE, AND IT IS WORSE THAN THE SLIP THAT WAS RULED.**

**Opus: 8 of 12 spent. Free: 1. Insurance: 2, termination-only. DA reserve: 1, holds C3.**

**Claims on that single free unit: three.**

| Claim | Seat | Status |
|---|---|---|
| **I-173's revision** — *"scoped and unfunded, and it must land before the seal or P7 freezes it"* | Director | **required before C2** |
| **C2** — the Gate 0 intake verdict | Validation | **seal-blocking** |
| Terminal-verdict memo | Director | objective 3 |

**One unit. Three claims. And the dependency chain makes this worse than a missed objective 3:**

> **Objective 2 requires trials. Trials require a registered family. Registration IS the seal.
> Objective 1 is the seal. So objectives 1, 2 and 3 all depend on the seal — and the seal now needs
> two free Opus units the firm does not have.**

**The slip ruled in advance covered objective 3 on two named conditions. Neither has occurred.**
**This shortfall arrives by a third route the ruling did not name — a pricing call — and it reaches
all three objectives, not one.** The CIO states that plainly rather than filing it under an existing
ruling it does not fit.

**4 · THE CIO'S PROPOSED RESOLUTION, which preserves objectives 1 and 2 without touching the ceiling
or the insurance.**

**Execute I-173's remedy at Sonnet, against the Director's already-delivered roster.**

I-173's finding is that **the Director put its own revision apparatus inside strings that get
hashed** — `[Rn · date]` markers inside sealed fields, which the evaluator correctly extracts as
dated sites. **E-2 extracts 90 sites from nine fields; 72 are dates that are not clauses; 75 fire on
first invocation; E-24 therefore makes the Gate verdict permanently `INSUFFICIENT-DATA`.**

**The judgment is already done and delivered**: `research/work/site_roster.json` (901 lines) and
`site_roster.md` classify all 90 sites. **The remaining act is mechanical — move revision apparatus
out of hashed fields to a non-hashed location, against a classification the Director has already
made and which governs.**

**Risk stated, not buried:** a Sonnet seat editing sealed fields is the class of act that normally
needs Opus judgment. **The mitigation is that it makes no classification — it executes one.** If the
roster is not precise enough to execute mechanically, **the seat must stop and say so rather than
decide**, and the CIO will bring the shortfall back.

**That leaves: C2 on the last free unit → C3 on the DA reserve → seal → trials at Sonnet.
Objectives 1 and 2 recoverable. Objective 3 slips, as already ruled.**

**5 · Alternatives the CIO considered and rejected, stated so the Principal can take one:**

- **Price row 2 as one.** Reverses the ratchet on its first firing, on a reading the seat itself
  declined to use. **The ratchet exists for exactly this moment; applying it only when convenient is
  not applying it.**
- **Release an insurance unit to working capacity.** Insurance is termination-only by the
  Principal's own term, against a failure mode with a measured 27% base rate. **Spending it as
  capacity removes the cover at the moment the tier is thinnest.**
- **Raise the ceiling.** Refused twice, and against the CIO's own doctrine — *a ceiling that moves
  when it binds is not a ceiling.*

**6 · The §11.1 correction runs AGAINST the family, and the "understatement" was itself wrong.**
Measured **2026-08-12**, read-only over `book/pit.db`, all six primary legs: **`[2020-01-01,
2026-07-28]` = 2,400 days = 6.5710 years. The figure has not moved.** R34 asserted the span grows
with `C`; **it grows with ingest, and none has occurred** — last `knowledge_time` on every leg is
2026-07-29, `ingest_ceiling` empty.

**So §10.4's 0.43-year MinBTL margin is exact, not understated — the hidden margin four passes
believed in does not exist.** And **at `C = 2026-08-12` the declared in-sample window runs 15 days
past the last bar on disk.** I-176.

**7 · Two register findings that bear on the seal.** **I-171:** E-2's `FORMULA` recognizer is
**case-sensitive**, so clause 5's *"C + 187 **DAYS**"* extracts as a bare `C` and is caught only by
E-14, **only because the struck literal is still in the field** — *"strip the struck literals and the
termination clause fires immediately."* **The struck text is load-bearing by accident.**
**I-172:** there are **zero `SPAN` sites** in this family, so **E-21's named proof case — §11.1's own
stale span — never runs on the family it was built from.**

**8 · The register covers 10 of 24**, and **the 24 is the wrong denominator** — the real surface is
90 sites. Fourteen uncoverable, thirteen because the clause lives in prose no registry field
carries: **E-25(3)'s named gap, with a number attached.**

**9 · Verified** [measured]: registry **0 hypotheses / 0 trials**; payload **unchanged** and
untouched; `harness/` untouched; §11.4 **closed at R33**, verified against the file rather than
inherited from R-006's claim.

**10 · Budget.** **8 of 30 invocations · 8 of 12 Opus.** **Free: 1. Insurance 2. DA reserve 1.**
§5 dead-man: **4 invocations remain.**

**Review date:** immediately — the Principal's ruling is required before any further dispatch.

---

## S3-D-016 · 2026-08-13 · New slip ruled honestly · I-173 execution dispatched with computed acceptance

**1 · Pricing countersigned in full.** The Principal's summary of why it mattered: *"'Without appeal.
Not appealed' is the ratchet working on its author, which is the only proof a ratchet ever offers."*

**2 · THE BUDGET SHORTFALL IS RULED AS A NEW SLIP, NOT SQUEEZED UNDER THE OLD ONE.**

> *"The pre-ruled slip named two conditions; this arrived by a third route and reaches all three
> objectives, and filing it dishonestly would spend the credibility the pre-ruling bought."*

**Amended ruling: objective 3 slips as already ruled; objectives 1 and 2 remain in scope via the
path below; if that path stops, they slip too, and the sprint closes on what it honestly holds.**
All three of the CIO's rejections adopted — **no ceiling raise, no insurance release, no ratchet
suspension.**

**The CIO records the principle, because it is the more transferable half:** a pre-commitment's
value is destroyed the first time an outcome is filed under it that does not fit. **Two honest slips
are worth more than one tidy one.**

**3 · I-173's Sonnet execution dispatched under three guardrails, and the CIO derived guardrail 2's
numbers itself rather than accept any report.**

Read directly from `site_roster.json` [measured]: **90 sites · 35 flagged `stamp: true` · 55
substantive.** Sampled to confirm the flag marks `[Rn, date, PRE-SEAL …]` revision apparatus and not
subject matter — the unflagged set includes the sample start `2020-01-01`, SOL's break
`2022-11-09`, and the `2025-09-18` formula change. **Committed before execution: expected extraction
after the edit = 55.**

**And one thing the CIO put in the brief that no report supplied.** Stamp removal takes extraction
90 → 55; **it will almost certainly not take firings to zero**, because surviving dates like
`2020-01-01` and `2022-11-09` still fire under E-10 row 4. **The brief states this in advance and
rules it a finding rather than a failure** — *"so you do not treat the expected outcome as your own
failure and go looking for more to cut."* **A seat told only "make the number go down" cuts
substance to reach it.**

Guardrail 1 is stated as: **a partial execution with the ambiguous sites named is a success; a
complete execution containing one judgment you made is a failure.** Guardrail 3 forbids
self-certification — **the diff goes to C2, where the Director's classification gets Opus-graded
exactly once, in the place it was already going to be read.**

**Per `GATES.md` §4.7.4(ii), the checker's printed output is the deliverable, clean-run output
included.**

**4 · §11.1 — the window conforms to the disk, direction-blind, at seal.** *"A document describing
data that doesn't exist."* **Ingest-to-current authorized as ordinary Sonnet data work** — and the
Principal names why it is not peeking: **the forward window begins at `C`, which is the seal.** The
sealed declaration then states the measured span with its measurement date, **whichever way the
number moved.**

**The hidden margin is recorded as never having existed. §10.4's margin is exact and is reported as
exact.** The Principal's formulation, which the CIO expects to reuse: **"a margin believed into
existence is I-141's cardinal error wearing a calendar."**

**5 · §5 dead-man — the CIO reports the accurate figure rather than the conservative one.** The
Principal's message states *"dead-man is at 4."* **§5 runs the count from the last Principal
checkpoint, and this ruling is one, so the clock reset: 10 invocations, of which this dispatch
spends 1 — nine remain.** The CIO reported a stale, over-conservative dead-man figure twice in
Sprint 2 and was corrected for it; **reporting a tighter number than the rule gives is the same
error in the other direction, and it distorts planning the same way.** Flagged for correction if the
Principal meant the Opus margin, which **is** one termination wide.

**6 · §2.2 headroom: this ruling carried no `[usage:]` line.** The Principal's own instruction is
that *"the headroom line travels on every message"* and that **any Opus dispatch that can wait for a
fresh window, waits.** Headroom is **UNKNOWN**. **This dispatch is Sonnet, so the posture does not
bite — and the CIO notes that row 3, the last free Opus unit, is exactly the dispatch that should
wait for a fresh reading rather than proceed under an unknown one.**

**7 · Sequence.** Sonnet I-173 execution *(running)* → Sonnet ingest-and-conform → **row 3: C2, the
last free Opus unit, absorbing C13(k), C5's mechanics, and the executed diff** → C3 on the reserve →
registration-as-seal → trials at Sonnet.

**8 · Budget.** **9 of 30 invocations · 8 of 12 Opus.** Free **1**; insurance 2; DA reserve 1.

**Review date:** on the I-173 execution's return.

---

## S3-D-017 · 2026-08-13 · Headroom reading — conservative posture lifted

**`[usage: session 22% · weekly-opus 12%]`**, supplied on request. **First known headroom since
2026-08-06 (`58% / 18%`).** Recorded with its message per §2.2, because the whole value of the
signal is that it is timestamped.

**Posture:** the note is fresh and **no termination has occurred in Sprint 3**, so headroom is
**KNOWN**, and §2.2's conservative posture — under which the CIO declined a parallel Opus dispatch
three times — is **lifted.** Pre-split and incremental writes remain in force unconditionally; they
were never posture-dependent.

**What this unblocks, and what it does not.** **Row 3 — C2, the last free Opus unit — was the
dispatch the CIO said should wait for a fresh reading rather than proceed under an unknown one. It
now has one.**

**But C2 still waits, and on a dependency rather than on headroom:**

1. the **I-173 execution** (Sonnet, in flight) — **guardrail 3 sends its diff to C2 for review**, so
   C2 cannot precede it;
2. the **ingest-and-conform** (Sonnet, not yet dispatched) — C2 would otherwise rule on a §11.1 span
   the Principal has ordered conformed to the disk.

**The ingest is not dispatched concurrently with the I-173 execution**, for the reason the CIO has
given every time: **same seat, same tree.** Both are Seat 9's. **Sequencing costs latency; collision
costs correctness**, and the tree in question is the document about to be sealed.

**Budget unchanged: 9 of 30 invocations · 8 of 12 Opus · free 1 · insurance 2 · DA reserve 1.**
§5 dead-man: **9 remain** since the 2026-08-13 checkpoint.

**Review date:** on the I-173 execution's return.

---

## S3-D-018 · 2026-08-13 · I-173 executed · §4 INTERRUPT — I-185 · the CIO's acceptance number was wrong

**1 · §4 HARD INTERRUPT — I-185, HIGH**, the execution/status update to I-173: **27 of 35 relocated,
8 named exceptions, extraction 92 → 65.** Verified independently by the CIO: **the extractor returns
65**, and **§21.1 sits at line 3396, after the fence closes at 3392 — outside what the extractor
reads, therefore outside `prereg_sha256`'s input.** Registry **0/0**. Severities on disk: 1 HIGH,
3 MEDIUM, 3 LOW.

**2 · THE COMMITTED ACCEPTANCE NUMBER WAS THE CIO'S AND IT WAS UNREACHABLE. Filed as I-096.**

The brief committed **55 = 90 − 35**. The true pre-edit baseline was **92** — R-007's
`[R38 … RATIFIED BY THE PRINCIPAL]` insert added two sites **after `site_roster.json` was generated,
in the same revision that generated it.** **Even a flawless execution lands at 57.**

**The second error is worse than the first.** Guardrail 2 exists because *"acceptance is computed,
not narrated."* **The CIO derived 55 by arithmetic on a cached file instead of re-running the
extractor — which takes seconds, and which the executing seat did as its first act.** *The control
against narrated acceptance was itself narrated from a cache.*

**Third cardinal error of the sprint by the CIO** — I-141, I-150, and this — **all three a count
taken from a document rather than from the thing the document describes**, which is `GATES.md`
§4.7.3 violated in the CIO's own arithmetic. **Corrective in force: an acceptance number is computed
live at dispatch time from the artifact the seat will measure, never from a cached derivative.**

**The committed 55 is not amended.** A pre-commitment revised after its outcome is not a
pre-commitment. **The record shows 55 committed, 65 delivered, and why.**

**3 · The seat did the three things the brief was designed to test, and did all three.** It **did not
chase the number** — *"this is a finding, not an adjustment target."* It **decomposed the gap
exactly** rather than reporting a miss. And it **stopped on 8 of 35 rather than deciding**, naming
each:

- **`success_criteria`'s R13–R17 marker has no closing `]` anywhere in the field** — the field's only
  unbalanced bracket, confirmed by exhaustive depth accounting. **A pre-existing defect in a string
  about to be hashed** (I-181).
- **Four brackets entangle a true revision date with a substantive `stamp:false` date**, so
  relocating the bracket would carry subject matter out of the field with it (I-183).
- **Two bare-prose dates** sit inside load-bearing sentences, unbracketed (I-184).
- **Two sites the roster never classified** — the `[R38]` pair — **left untouched under "the roster
  decides, you do not."**

**4 · The firing count could not be computed, and the seat refused to fabricate one.** `VALIDATION-SPEC-004`
specifies `harness/scripts/evaluate_dated_clauses.py`; **only its unimplemented test file exists** —
which **the CIO knew and required output from anyway.** The seat hand-applied E-10 row 4, reported
**27 of 65 mechanically FIRED**, **declined to count 24 unresolvable `FORMULA`/bare-`C` sites**
though I-173's own pre-edit accounting had counted analogous ones, gave the honest bound **27–51**,
and named the exact figure **Validation's call, not its own** (I-186).

**A seat that reports a range and says whose decision the point estimate is has done something
harder than reporting a number.**

**5 · What this means for the seal, stated plainly.** **Stamp removal was necessary and is not
sufficient** — exactly as the CIO's brief predicted in advance. **Firings remain nonzero**, the
8 exceptions remain in the hashed fields, and **I-181's unbalanced bracket is a defect in a string
that is about to be frozen.** **C2 now has more to rule on than the diff.**

**6 · Sequence unchanged, and C2 still waits on the ingest.** Next: **Sonnet ingest-and-conform**
(§11.1 to the disk, direction-blind) → **row 3, C2, the last free Opus unit**, absorbing C13(k),
C5's mechanics, **the executed diff, the 8 exceptions, and the firing-count call.**

**7 · Budget.** **10 of 30 invocations · 8 of 12 Opus.** Free **1**; insurance 2; DA reserve 1.
Headroom last known **22% / 12%**, fresh. §5 dead-man: **8 remain.**

**Review date:** on the ingest-and-conform's return.

---

## S3-D-019 · 2026-08-13 · Ingest dispatched · the headroom figures read as CONSUMED, not remaining

**1 · I-185's execution ACCEPTED; the acceptance criterion is what failed.** The Principal:
*"a seat that lands on an unreachable number by refusing to chase it has satisfied the brief better
than hitting 55 would have."*

**I-096 countersigned with its corrective, and the corrective binds both parties** — the Principal
records having made the same class of error twice this fortnight, and **"computed live from the
artifact the seat will measure" now governs his rulings' numbers as well as the CIO's.** The
unamended **55** stands as the record's own lesson: *the committed 55, the delivered 65, and the
derivation of the gap are the acceptance artifact.*

**2 · The refusal to fabricate checker output is named the exchange's standing exhibit**, and the
Principal supplies the reading the CIO would want kept: **"the range is the honest output of a
control that hasn't been built."** §4.7.4(ii) honoured *in the checker's absence.*

**3 · Ingest dispatched at Sonnet, as instructed** — to current, then §11.1 conformed to the
measured span with its measurement date, **direction-blind, "whichever way the number moved."** The
brief carries three refusals the CIO added: **do not bypass the ingest ceiling** (*"a seat that
lifts a ceiling to complete its own dispatch has defeated the control it was working under"*); **do
not repair restatement incidents** — report verbatim and escalate; and **do not characterize the
new span as favourable or unfavourable — write the number and its date.**

**One question added that no instruction contained:** R-007 found the span grows with **ingest**,
not with `C`, *"and none has occurred."* **If ingest now occurs and the span still does not move,
that is the more interesting finding** — it would mean the vendor holds no bars past 2026-07-29 for
these legs, **which bears directly on whether the family can be sealed against a window it claims to
have data for.**

**4 · §2.2 FLAG — THE HEADROOM FIGURES APPEAR TO BE CONSUMED, NOT REMAINING, AND THE RULING READS
THEM THE OTHER WAY.**

The ruling states *"12% weekly-Opus remaining means C2 does not dispatch until the window resets."*
**The CIO believes 12% is consumption, leaving ~88%.** Evidence is the series itself, recorded
across five readings:

| Date | session | weekly-opus |
|---|---:|---:|
| 2026-08-04 | 24% | **12%** |
| 2026-08-05 | 19% | **15%** |
| 2026-08-06 | 49% | **17%** |
| 2026-08-06 | 58% | **18%** |
| 2026-08-13 | 22% | **12%** |

**Read as *remaining*, weekly-Opus rose 12 → 15 → 17 → 18 across three days inside one week. A
weekly quota does not refill mid-week.** Read as *consumed*, the same series is monotonic
accumulation across 08-04 → 08-06 and a **reset to 12% on 08-13, a new week** — which is exactly
what a weekly counter does.

**The CIO cannot verify this directly** — `/usage` is not invocable by this seat, which is why the
control was retracted and replaced at S2-D-016 — **so this is `[inferred]` from the series, not
`[measured]`.**

**What it costs if the CIO is right:** C2 is the last free Opus unit and sits on the critical path to
the seal. **Holding it for a window reset that has not been consumed delays objectives 1 and 2 by
days, in a sprint whose shortfall has already been ruled twice.**

**What it costs if the CIO is wrong:** a dispatch dies on quota and spends insurance on a calendar
problem — **exactly the outcome the Principal is protecting against, and the more expensive error of
the two.**

**The CIO therefore does not dispatch C2.** The instruction stands until the Principal rules, and
**the asymmetry favours waiting**: being wrong about waiting costs days, being wrong about
dispatching costs an insurance unit the tier cannot spare. **One `/usage` line resolves it.**

**5 · C2's absorbed scope, restated so nothing arrives by surprise:** the executed diff · the 8
in-field exceptions · **I-181's unbalanced bracket — *"it resolves before hashing or the field
doesn't seal"*** · the 27–51 point estimate · **C13(k)** · **C5 mechanics.** *"That is a full unit's
work and it is the last free unit; the brief says so plainly."*

**6 · Budget.** **11 of 30 invocations · 8 of 12 Opus.** Free **1**, held for C2. Insurance 2; DA
reserve 1. §5 dead-man: **7 remain.**

**Review date:** on the ingest's return, and on the Principal's reading of the headroom figures.

---

## S3-D-020 · 2026-08-13 · The headroom figures are CONSUMPTION — resolved by measurement, not argument

**Reading supplied: `session 27% · weekly 13%`.** Prior reading, hours earlier: **`22% / 12%`.**

**Both figures ROSE across an interval in which the firm only spent.** Between the two readings the
CIO ran one Sonnet dispatch (S3-D-019's ingest) and a series of read-only queries. **Nothing was
returned, refunded, or reset.**

> **Consumption rises with spending. Remaining falls with spending. Both figures rose. They are
> consumption.**

**This upgrades the S3-D-019 flag from `[inferred]` to `[measured]`.** That entry argued from a
five-reading historical series — that weekly-Opus rising 12 → 15 → 17 → 18 inside one week is
impossible for a quota that does not refill mid-week. **The argument was suggestive. Two consecutive
readings across known, one-directional activity are dispositive**, and the CIO records the
difference because *the first was reasoning and the second is evidence.*

**Consequence: weekly usage stands at ~13% consumed, ~87% remaining. C2 is not quota-blocked, and
the window does not need to reset.** The ruling's *"12% weekly-Opus remaining means C2 does not
dispatch until the window resets"* rested on the inverted reading.

**One caution the CIO does not paper over:** the label changed between readings — **`weekly-opus`**
previously, **`weekly session`** now. The values are continuous (12 → 13), so the CIO treats them as
one series; **if they are two different metrics, this conclusion is about whichever one the 13%
belongs to, and the Opus-specific figure would still be outstanding.** One line resolves it and the
CIO will not assume past it.

**C2 STILL DOES NOT DISPATCH — and now for the correct reason.** The Principal's own sequence is
**ingest-and-conform → C2**, and **the ingest is in flight.** C2 would otherwise rule on a §11.1 span
that is being conformed underneath it. **The dependency was always the real blocker; the quota
reading was a second one that turns out not to exist.**

**C2 dispatches on the ingest's return, on this headroom reading, unless the Principal rules
otherwise.**

**Budget unchanged: 11 of 30 invocations · 8 of 12 Opus · free 1, held for C2 · insurance 2 · DA
reserve 1.** §5 dead-man: **7 remain.**

**Review date:** on the ingest's return.

---

## S3-D-021 · 2026-08-13 · Ingest complete · span moved · C2 PROJECTS OVER THRESHOLD — not dispatched

**1 · Ingest complete. 376 new rows across six legs; last `knowledge_time` now 2026-08-12 on every
leg.** The ingest ceiling **did not block anything**, and the seat's framing is the correct one:
*"the family is unregistered, there is no cutoff to enforce — this is not 'the control was
bypassed,' it's 'the control had nothing to fire on.'"*

**2 · Two restatement incidents, auto-logged under A4** — registry events 2 and 3, verified
[measured]. Three fields per perp leg on **2026-07-29**: `low`, `close`, `volume`. **Blast radius:
none** — registry holds 0 hypotheses / 0 trials, so no trial's number is touched. Escalated to
Validation, **I-190 MEDIUM**. Cause is the exchange settling a bar that was still forming at prior
ingest, **and the seat filed it anyway** — *"A4 requires the log+escalation regardless of cause or
blast radius."*

**3 · THE SPAN MOVED, AND THE SEAL NOW HAS A CHOICE THE CIO PUTS TO THE PRINCIPAL.**

| | Days | Years @ 365.2425 |
|---|---:|---:|
| Previous (R37, pre-ingest) | 2400 | **6.5710** |
| **Inclusive of the terminal bar** | 2415 | **6.6120** |
| **Settled bars only** | 2414 | **6.6093** |

**R37's prediction is confirmed in both directions** — the span did not move while no ingest ran,
and moved by exactly the ingested days once it did.

**But the terminal bar 2026-08-12 is the currently-forming UTC day** — spot BTC volume **398.04**
against a several-thousand-per-day norm — and the seat states plainly: **expect an I-190-shaped
restatement on the next re-fetch.**

**So sealing against 6.6120 seals a span whose terminal bar is known in advance to be wrong.** Under
P7 that freezes. **The CIO recommends sealing against the settled-only 6.6093** — it is the shorter
figure, it is the one that does not require a restatement inside a sealed in-sample window, and
**choosing the shorter of two numbers when the longer is knowingly provisional is the
direction-blind answer, not a conservative flourish.** §10.4's margin widens either way — 0.43 →
0.472 inclusive, 0.469 settled — **and the CIO reports that the arithmetic moves without proposing
what §10.4 should say, which is Validation's.**

**4 · A sequencing finding the seat disclosed rather than corrected.** §15 step 1 plans
`binanceusdm` perp OHLCV ingest as **post-seal, bounded by the ceiling.** This dispatch ingested it
**pre-seal, under explicit instruction, because no ceiling exists yet.** §15 was not edited — out of
scope — and §11.1 now flags it. **The document's method section and what actually happened disagree,
and that disagreement is now in the record rather than in a gap.**

**Four span occurrences were left untouched — all inside I-181's unclosed bracket.** The seat
declined to reach into an S3-D-016 exception it was not authorized to touch. **Correct.**

**5 · C2 PROJECTS OVER THRESHOLD. IT IS NOT DISPATCHED, AND THE CIO MEASURED RATHER THAN GUESSED.**

Precedent, read from disk [measured]: **`VALIDATION-GATE0-001` — a Gate 0 intake verdict — is 464
lines.** **`VALIDATION-RULING-005` — four adjudications — is 583 lines.**

**C2 as scoped is a Gate 0 intake verdict PLUS eight absorbed rulings**: the executed diff · the 8
in-field exceptions · I-181 · the 27–51 estimate · C13(k) · C5 mechanics · and now the §11.1
conformance and the span choice. **Projection: 1,000–1,200 lines. Over threshold, not marginally.**

**The ratchet is in force and admits no appeal: over threshold prices as two. The firm has one free
unit.** Dispatching as scoped means either violating the ratchet or exhausting the tier, **and the
CIO will do neither.** The Principal's own words on this scope — *"that is a full unit's work"* —
**the measurement says it is two.**

**6 · PROPOSAL: scope C2 to the seal-blocking set only, using the firm's own separation.**

R-006 established it and the Principal ruled on it: **C5 is verdict-blocking, not seal-blocking** —
*"sealable, runnable, Stage-1-spendable with C5 open; not evaluable, and no PROCEED reportable."*

| Keep — seal-blocking | Defer to the Gate 1 path |
|---|---|
| The **Gate 0 intake verdict** | **C5 mechanics** — blocks evaluation, not sealing |
| **C13(k)** — *"the seal does not proceed past an unruled C13(k)"* | **The 27–51 estimate** — concerns an evaluator that is not implemented |
| **I-181** — *"it resolves before hashing or the field doesn't seal"* | **I-045** — the Director's view is it survives the seal as a standing disclosure |
| **The executed diff** — guardrail 3 | **I-076** — `test_mbs_12`'s band, unrelated to the seal |
| **The span choice** — §11.1 and the forming terminal bar | |

**This is not a thinning of scrutiny — it is the firm's own seal/verdict separation applied to a
budget that has one unit.** Everything deferred binds where it was always going to bind: **at Gate 1
evaluation, which the ruled slip already moved to Sprint 4.** **Nothing adversarial is dropped; C3
remains on the reserve and remains unskippable.**

**Projected under threshold on the precedent: a 464-line Gate 0 base plus four rulings, against
RULING-005's 583 for four.**

**7 · Budget.** **12 of 30 invocations · 8 of 12 Opus.** Free **1**, held. Insurance 2; DA reserve 1.
Headroom **13% consumed weekly** — not a constraint. §5 dead-man: **6 remain.**

**Review date:** immediately — C2 does not dispatch without a ruling on scope.

---

## S3-D-022 · 2026-08-13 · Quota reading corrected · span seals at 6.6093 · C2 DISPATCHED on the last free unit

**1 · The quota label resolved from the Principal's side.** Same series, transcription varied,
**semantics are consumption as the CIO measured.** The `[measured]` upgrade stands, **"12%
remaining" is corrected in the record to ~87% remaining**, and **the quota-block rationale attached
to C2's timing is withdrawn as founded on a misreading.** *"C2 was never quota-blocked; the ingest
dependency was always the real gate."*

**The CIO records what made this resolvable: two consecutive readings across known one-directional
activity.** Neither party could settle it by argument — the earlier five-reading series was
suggestive and no more. **A disagreement about a measurement was resolved by taking another
measurement**, which is the only method that has worked in this firm's two sprints.

**2 · THE SPAN SEALS AT 6.6093 — settled bars only — and the reasoning is promoted to doctrine:**

> **A sealed figure may not include a value known in advance to be provisional. Sealing 6.6120 would
> freeze a number the firm already expects to restate — manufacturing a future A4 event inside a
> P7-frozen field.**

And the Principal corrects the CIO's own framing of its recommendation: **"choosing the shorter
figure here is direction-blind by construction, not conservatism: the criterion is *settled*, and
settled happens to be shorter today."** **The CIO had defended the choice as direction-blind and
then hedged it as "not a conservative flourish" — the correction is that the criterion never
mentioned length at all, and stating the criterion is enough.**

§10.4's arithmetic consequence routed to Validation inside C2. **The two A4 escalations at zero
blast radius are noted with approval: *"the rule fires on cause, not consequence."***

**3 · C2's SCOPE SPLIT APPROVED. The measurement governs, and the Principal applied the ratchet to
himself:** *"the ratchet admits no appeal including mine; my 'full unit's work' is corrected by your
line-count to 'two units' work,' and the firm has one."*

**Deferral legitimacy stated on its own logic, not on convenience:** the partition is R-006's
seal/verdict separation applied to the budget; every deferred item binds where it always bound; and
**"nothing in the deferred column can produce a wrong seal — only a wrong evaluation, which cannot
occur before Sprint 4's funded path reaches it."**

**4 · The addition that binds the verdict's FORM, and it is the sharpest instrument of the
exchange:**

> **The intake verdict must state, in the three-register form, what it did NOT rule — the deferred
> named as deferred, "so the seal's record shows a scoped verdict and not a complete one wearing
> scoped clothes."**

**This is the `f54f9b9` three-register correction — prevents / merely detects / does not touch —
turned on a verdict's own authority.** A scoped verdict that does not name its scope is
indistinguishable, to every later reader, from a complete one.

**5 · The CIO put a counting instruction in the brief that names its own uncertainty.** The CIO's
table enumerates **four** deferred items; **the Principal's ruling says five.** **Neither counted
from the enumeration.** The brief tells Validation to **enumerate exhaustively and report its own
count**, taking the number from neither party — *"this firm has produced six cardinal errors of
exactly that shape in two sprints."* **The CIO does not resolve the discrepancy in its own favour or
the Principal's; it removes both of us from the arithmetic.**

**6 · One requirement the CIO imposed after failing the same test itself.** The brief requires
Validation to **plan and state its line budget section by section before writing, and to say so and
propose cuts if the plan exceeds ~800 — before writing past it, not after.** The CIO's stated reason
to the seat: **I-096 records the CIO committing an acceptance number from a cached artifact in a
brief whose whole point was that acceptance is computed, not narrated. A line budget discovered at
the end is the same error.**

**7 · C2 dispatched on the scoped set, this headroom, now.** Projection stated honestly as **close to
threshold, could go either way**, against measured precedent — 464 lines for an intake verdict,
583 for four adjudications.

**8 · Budget.** **13 of 30 invocations · 9 of 12 Opus. FREE OPUS: ZERO.** Remaining tier is **the DA
reserve (C3, submission-gating, unskippable) and 2 termination-insurance units.** **There is no
second attempt at C2 this sprint.** §5 dead-man: **5 remain.**

**9 · Sequence to the seal:** C2 *(running)* → **C3 on the reserve** → **registration-as-seal, a §4
interrupt and the Principal's act.**

**Review date:** on C2's return.

---

## S3-D-023 · 2026-08-13 · GATE 0: ADMIT-CONDITIONAL · seal-blocking reduced to C7 and C8

**1 · THE FIRM HAS ITS FIRST GATE 0 VERDICT ON PREREG-002: ADMIT-CONDITIONAL.** Five criteria PASS,
**zero FAIL**, two recorded **PENDING BY CONSTRUCTION** — criteria 6 (trial counter opened) and 7
(holdout locked) **cannot be PASS at any Gate 0 evaluation in this firm**, because `open_hypothesis`
*is* the seal and the vault is C8-bound to the same UTC day. **Both are satisfied by the act the
verdict authorizes.** `VALIDATION-GATE0-001` never named this (I-206).

**Seal-blocking after C2: C7 and C8 only.** C3 remains **verdict-blocking, unspent, unskippable**,
and the verdict states expressly that it does not substitute for it.

**2 · The line-budget requirement worked, and it is the first thing the CIO checked.** Planned
**~700 across thirteen sections, stated in §0 before writing. Held at 590 — 210 spare, nothing
cut.** The CIO imposed it after failing the same test at I-096; **a seat that plans its budget
before writing does not discover an overrun after.**

**3 · C13(k) — CONCURRENCE, NO DISSENT, AND ON A GROUND THE PRINCIPAL DID NOT STATE. This is the
finest reasoning of the sprint.**

KC-002 clause (b)'s **30 conditioning days is a count, not a rate.** Hold the count, take the
drafted literal, and the implied rate moves **16.04% → 17.54%** at a 2026-08-13 seal —
`(30/171)÷(30/187) = 1.0936` [measured].

> **Requiring the drafted literal moves a pre-registered threshold by 9.4% as a function of how many
> days elapsed between drafting and sealing. That is not tightening, it is randomizing** — a §4
> reserved act arriving by scheduling accident.

**And the sentence the CIO wants preserved above all others from this dispatch:**

> **"Refusing the conformance would have been the permissive act wearing the adversarial seat's
> clothes."**

**The adversarial-looking choice was the permissive one, and only an adversary who checks arithmetic
rather than posture finds that.**

**4 · §4 HARD INTERRUPT — I-204, HIGH.** E-14's `DIVERGENT` — **the only control catching clause 5's
bare-`C` extraction — fires *only because* the struck `2027-01-31` literals are still in the field.**
Ruled in both directions: E-2's recognizer must become case-insensitive on the unit (a spec
amendment, Validation's, **unfunded**), and **until it lands no seat may strip those eight
literals.** **Struck text is load-bearing, and the document is safe by an accident that is now
recorded as a rule.**

**5 · I-181 resolved by ONE CHARACTER, and the near-miss is worth more than the fix.** A single `]`
at line 2559. Verified: **bracket depth 1 → 0, no negative excursion, extraction unchanged —
provably semantically null.** The Director's obstacle never had to be answered: **the document
answers "where does the marker close" by its own convention, twice in the same field.**

**I-203 — the near-miss.** The obvious repair, closing at the field's end, **would have placed
§10.4's entire sealed ceiling function, §10.8's verdict bands, both mandatory render strings and
both disclosed leakage defects inside a revision marker — making all of it eligible for relocation
*out* of the hashed field under S3-D-016's own rule.** **Guardrail 1's stop-and-queue prevented it.**
The guardrail that looked like caution was load-bearing.

**6 · C11 removed from the seal-blocking set — it was circular.** It required ≤2 logged trials;
`log_trial` refuses an unregistered family; **registration is the seal.** **It asked for work whose
precondition was the act it blocked**, and §20 and the registration payload have contradicted each
other about it since R-004. Re-imposed as **class (b) at Gate 1** with executor, cadence and artifact
named (I-202).

**7 · §10.4 — every number in it is class (c), and that is why none of it needs re-sealing.** Both
circulating margins were **rounded-input arithmetic**: 0.43 and 0.469 both subtract the *displayed*
6.14 rather than the measured **6.135900**. Correct values **0.4351** and **0.4734**; binding ρ̂
**0.034241 → 0.037143**; absolute ceiling **109 → 112**.

**None of the three loosenings may be banked, because none binds:** `86 < 109 < 112`, and `gates.py`
**recomputes from `oos_index` at evaluation time and reads no sealed literal.** The two stale
literals are **stale in the conservative direction and accepted sealed** (I-207). **The labeling
mandate paid here: knowing the numbers were class (c) is what made re-sealing unnecessary.**

**8 · THE DEFERRED COUNT IS NINE. Both the CIO's four and the Principal's five were wrong.** The five
neither party named: **C4, C6, C13(j), I-170, I-172.** Filed as **I-205 — "seventh cardinal in three
sprints taken from a table rather than an enumeration, in the dispatch that ordered the enumeration
to prevent it."**

**The instruction worked exactly as intended.** The CIO removed both parties from the arithmetic and
told the seat to count from the enumeration; **it counted, and both parties were wrong.** A
discrepancy resolved in either party's favour would have shipped a scoped verdict understating its
own scope by five items.

**9 · I-209 IS THE CIO'S, AND ITS CAUSE IS INSTRUCTIVE.** `book/registry.db` held **3 events in the
working copy and 1 in HEAD** — **under A3 the book of record did not contain the two A4 restatement
incidents.** Caught by Validation, not by the CIO. **Fixed: committed, HEAD now holds 3.**

**The cause is the corrective for I-054.** After `git add -A` captured a concurrent seat's
in-progress work, the CIO adopted **named-path staging only.** **A named-path discipline omits
whatever the CIO did not think to name** — and `book/registry.db` was written by a seat, not by the
CIO. **One corrective produced the opposite failure**, which is the honest cost of the fix and not an
argument against it. The `family = NULL` column on both events is a separate defect and stays open.

**10 · To the Principal — four items, two needing an act:** **C5 part 2** (his; Validation **declines
part 1 in isolation** — *"a point of application without ratification and executor is a class-(c)
no-op"*) · **I-206**'s one-sentence Charter clarification · **C13(k) concurrence on independent
grounds** · **the one-character edit, disclosed for his sight.**

**11 · Verified independently** [measured]: registry **0 hypotheses / 0 trials**, 3 events;
extraction **68**; the edit is **1 insertion, 1 deletion**; §21.1 remains outside the fence at the
current head — **the CIO's own 3392/3396 line numbers had drifted, the property holds** (I-201).

**12 · Budget.** **13 of 30 invocations · 9 of 12 Opus · FREE OPUS: ZERO.** Remaining: **DA reserve
(C3)** and **2 insurance units.** §5 dead-man: **4 remain.**

**13 · Sequence:** **C3 on the reserve → registration-as-seal, a §4 interrupt and the Principal's
act.** C7 and C8 resolve alongside.

**Review date:** on the Principal's rulings, then C3.

---

## S3-D-024 · 2026-08-25 · C2's acceptance items ruled · C3 DISPATCHED on the sealed reserve

**1 · C5 COMPLETE, to Validation's own standard, on the Sprint 4 path where it binds.** Ratification,
application, executor, artifact — all four named: the haircut is a **design-time discount on the
declared expected effect**, applied at **§5.4's power/α arithmetic**, executed by **Validation at
Gate 1 evaluation as class (b)**, with the **Gate 1 memo as the named artifact, showing the
discounted effect driving the evaluation in three-register form.** **No realized statistic is ever
scaled; the "statistically incoherent" branch stays struck.**

**Validation declined part 1 in isolation** — *"a point of application without ratification and
executor is a class-(c) no-op"* — **and was right to: a ruling that names where a control applies
but not who runs it produces exactly the class-(c) commitment the labeling mandate exists to
expose.**

**2 · I-206 — the sentence is supplied below for signature on quoted words.** The Principal's own
corrective this sprint is that he cites only from pasted artifacts, **"and a Charter edit is the last
place to breach it."** The CIO has **not** applied it; it is pasted in the report for his sight, and
`FUND_CHARTER.md` is unedited.

**3 · I-204's prohibition endorsed WITH ITS EXIT NAMED, and the exit is stricter than the CIO would
have written:**

> The struck literals stay in-field until E-2's recognizer goes case-insensitive **and a test proves
> `DIVERGENT` still fires on their removal** — *"the accident is now a rule, and the rule retires
> only when a computed control replaces the accident, not when the code claims to."*

**A code change that claims to replace an accidental control is not evidence that it does.** The
CIO's own framing was "until the amendment lands"; the Principal's requires the amendment to be
*demonstrated on the exact case the accident was covering.*

**4 · The deferred count: NINE, and the method is the ruling.** The Principal's five and the CIO's
four are **both corrected in the record**; the verdict names all nine. *"Sixth and seventh cardinal
errors of the fortnight, both caught by the same corrective: count the roster, not the memory of
it."*

**5 · I-209 — completeness check, not reversion.** Named-path staging **stands** (I-054's fix) and
**gains its missing half**, now in `ops/STANDING-ORDER-002.md` **§6.1**: at every session close,
`git status` is reviewed and **every dirty path explicitly dispositioned — staged by name, or named
in the record as deliberately unstaged with its reason.** *"A discipline that omits what nobody
thought to name now has to name what it omits."* **Seat-written files are the motivating case.**

**6 · C13(k) entered with Validation's reasoning quoted in full**, and the Principal names the second
sentence **the sprint's epitaph for anyone who thinks adversarial review means reflexive refusal**:

> *"a count, not a rate — that is not tightening, it is randomizing"*
> **"refusing the conformance would have been the permissive act wearing the adversarial seat's
> clothes."**

**7 · C3 DISPATCHED ON THE SEALED RESERVE.** Held since Sprint 1, **protected by the Principal four
times, unspent by design. This is what it was reserved for.** The memo runs **against the document as
it will seal** — scoped verdict, nine deferrals named, settled span, struck literals in-field.

**Three requirements the CIO added to Charter §4.4's form:**

- **Do not mistake a pessimistic sponsor for an honest one.** §19.3 pre-declares PARK-WITH-TRIGGER,
  and **a family sponsored under low expectations is one nobody argued hard against.**
- **Attack the process, not only the product** — and the question the CIO put to it having no answer
  of its own: *"does a document that needed seven revisions and three last-minute saves deserve to be
  sealed at all, or is the revision count itself the finding?"* **I-140 would have downgraded it on a
  stale sentence; I-153 would have killed it with certainty; I-130 would have sealed a permissive
  unlock table.** **The CIO supplied no answer and said so.**
- **Name what the firm has stopped being able to see.** Every seat has read this document a dozen
  times. **The DA is the only seat whose job is to be unpersuaded by that.**

**8 · I-097 handed to the DA rather than resolved — and the CIO states why it did not simply fix
it.** The data is **13 days stale**; `C` is the seal date; **sealing today gives an in-sample window
claiming 13 days not on disk.** S3-D-019's finding in reverse.

**The remedy is a Sonnet ingest the CIO could run. It did not, for two reasons.** The last ingest
produced **two A4 restatements on the primary universe** (I-190), and a re-ingest days before a seal
would likely produce more — **whether the firm prefers fresh data with fresh restatements or a
stale-but-settled window it has already adjudicated is a seal-quality judgment, not a data-cleaning
task.** And **it recurs by construction**: ingesting today makes the window stale again tomorrow.
**The gap closes at the moment of sealing or never.**

**9 · Budget.** **14 of 30 invocations · 10 of 12 Opus. FREE OPUS: ZERO. The DA reserve is now
spent.** Remaining: **2 termination-insurance units.** §5 dead-man: **3 remain.**

**10 · Sequence:** C3 *(running)* → **registration-as-seal, a §4 interrupt and the Principal's act.**
**C7 and C8 are the only remaining seal-blocking conditions.**

**Review date:** on C3's return.

---

## S3-D-025 · 2026-08-25 · THE RED TEAM SAYS DO NOT SEAL · §4 INTERRUPT · the reserve earned itself

**1 · §4 HARD INTERRUPT. Triggers: *"any issue filed HIGH"* (I-210, I-211) and *"any finding by the
Devil's Advocate addressed to the Principal."* The registration interrupt does NOT come to the
Principal. C3 says the document must not seal, and the CIO has verified the reason.**

**2 · THE DEFECT, VERIFIED INDEPENDENTLY BY THE CIO AT SOURCE** [measured]:

The sealed `statement` field freezes the sizing rule
**`w(t) = clip(1.0 − k·max(0, z(t) − d), 0, w_max)`** — and **`k`, `d` and `band` have no numeric
value anywhere in `PREREG-002` or in the registration payload.** Grepped for every literal form;
**zero hits.**

**The same document binds `lookback = 30` and `w_max = 1.0`.** It knows how to fix a parameter. **It
did not fix these three.**

**Why P3, P4 and P7 cannot see it:** `statement` is **(a) on existence, (c) on content** — the
harness raises on the empty string and reads no further. **The seal would prove a sizing rule was
written, not what its parameters are.** Three sentences assert a fixing that does not exist (§6.2
*"made now, before any measurement"*; §10.5 *"fixed at pre-registration"*; §11.5's *"parameter
centres"*).

**And the CIO verified the consequence the DA drew from it, which is worse than the defect:** the
**±50% grid sits at §15 step 6**, while **F-002's legs run at steps 2–3.** **So the grid's centre
would be chosen with F-002's output in hand** — on a continuum, with no sealed centre to depart
from. **That is the I-029(d) operation on the parameter axis**, and the document's own ordering
makes it available.

**KC-002 clause (b) — the sponsor's pre-registered expected cause of death — is a pure function of
`k` and `d`.** The family's declared most-likely failure mode is set by a dial the seal does not
fix.

**3 · THE RESERVE EARNED ITSELF.** This unit was held from Sprint 1, protected by the Principal four
times, and spent here. **Seven revisions, a Gate 0 intake verdict, two Validation specifications and
roughly two hundred issues did not find this.** The DA found it, in its own words, **with one grep**
— because it was the only seat that read the specification instead of the blocker table.

**Its own account of why: "§20's blocker table has handed the red team its target four revisions
running. I refused all four and read the specification instead."** **A red team that accepts the
firm's list of what to worry about is auditing the list.**

**4 · The strongest argument against the family, and it is not about parameters.** **The sizing rule
is provably inert in the regime where its own tail lives.** `max(0, z−d)` acts only when funding is
**rich**; §3.2/§3.3/§7.4 place the tail in funding **inversion**. A cascade destroys the crowding the
rule keys on — funding inverts, `z` collapses, `w` returns to 1.0, **and the 30-day baseline pins it
there for up to 30 days, through what §3.3 itself calls an "extended interval" of dislocation.**

> **The rule de-scales on the anticipation and holds full size through the realization.**

Measured, count-only: **25.6% / 25.2% of in-sample days carry at least one negative funding print.
A quarter of the sample sits where the rule cannot act.**

**5 · The argument against the process, which the CIO asked for and could not answer itself.**
**Seven revisions, and not one originated in the sponsor noticing.** R-001 ← Seat 9's measurement ·
R-002 ← Validation + Seat 9 · R-003 ← the Principal's I-057 ruling · R-004 ← `GATES.md` §4.7.2 ·
R-005 ← the Principal's class mandate · R-006 ← an ordered sweep · R-007 ← the Principal's
instruction.

> **"The document has been *found* seven times, not *checked* seven times"** — and the near-fatal
> rate **spiked at revisions 4–6 (three HIGHs in 48 hours) rather than converging.**

**"On seven for seven, an eighth instrument pointed at an unexamined dimension finds an eighth
defect. I-210 is that eighth, and it took one grep."**

**6 · The staleness ruled MATERIAL, not fatal — and the DA declined to escalate it, correctly.** The
engine is not deceived; `years_calendar` comes from `oos_index`. What freezes is that **two binding
fields carry `[2020-01-01, C]`**, so the sealed falsifier's window contains 14 nonexistent days
permanently.

**The DA identified the cause the CIO's three options all missed: `C` denotes two objects** — the
freeze instant and the in-sample right edge — **and R23/R33/R34/R37/I-097 are five repairs of
instances, none of the cause.** **Its remedy needs no Principal act and none of the CIO's three
options:** conform the two fields to *"the last settled common bar at the first run,"* which is what
`oos_index` already carries. **One prose edit; never recurs.** The CIO's I-097 framing is superseded.

**7 · I-219, unprompted, and it is the sprint's real finding.** Appendix B #1's metric is **undefined
at n = 0 Gate 1 verdicts** and the DA makes no claim from it. **The live failure mode is Appendix B
#9: throughput is zero.**

> **28 days · four Opus seats · ~200 issues · 0 trials · 0 backtests · 0 verdicts · 0 seals — and no
> artifact in three sprints has stated the throughput number the Charter requires stated.**

> **"I-210 is real and it blocks the seal; it is also the eighth defect found in a *document* by a
> firm that has yet to find its first defect in a *hypothesis*, because it has yet to test one."**

**The CIO endorses this without qualification and records that it should have been the CIO's finding
three sprints ago.**

**8 · I-098 filed against the CIO and the DA jointly: the ten findings never reached the Issue Log.**
The memo is 54 KB and references `I-21x` eighteen times; **the log is clean at I-209.** **Fifth
instance of I-092's class and the most dangerous** — *had the seal proceeded on the CIO's report of
the memo rather than on the memo, the Issue Log would have shown no seal-blocking issue at the
moment of sealing.* **The CIO recorded a pointer and refused to transcribe the DA's severities as
its own.**

**9 · The line budget: planned 650, delivered 725 — over its own plan by 11.5%, under the ratchet
with 75 to spare. Prices as ONE.** The DA disclosed that it **found the overage on completion rather
than mid-write** — *"I did not cut, because the overage was discovered on completion."* **That is the
exact failure the requirement was imposed to prevent, disclosed by the seat that committed it.**

**10 · Seal status: BLOCKED, and not by C7 or C8.** **I-210 is seal-blocking and repairable in one
dispatch.** The DA's condition for withdrawal is exact and cheap: **numeric literals for `k`, `d`,
`band`, plus the two `[2020-01-01, C]` sites conformed — *"nothing else moves the seal verdict, and I
withdraw it the same day."***

**11 · Budget.** **15 of 30 invocations · 11 of 12 Opus. FREE OPUS: ZERO. DA RESERVE: SPENT.**
Remaining: **2 termination-insurance units, and insurance is not working capacity.** **The repair
I-210 requires is a Director act, and the Opus tier cannot fund it.** §5 dead-man: **2 remain.**

**Review date:** immediately — the Principal's ruling is required.

---

# ═══ SPRINT 4 ═══

## S4-D-001 · 2026-08-25 · §1 adopts the trial as the objective · repair dispatched · SO-002's rules promoted

**1 · The Principal has made the first trial the objective and everything else its dependency.** The
CIO's close-report recommendation — *"make the first trial the objective, and make everything else
its dependency. Not the seal — the trial"* — **adopted, with a scope rule the CIO did not propose and
which is the sharper half:**

> **Document work not on the trial's critical path is out of scope by default and requires a
> Principal act to fund** — *"the pipeline has proven it can find defects forever; the exit is the
> forward clock."*

**That inverts three sprints of revealed preference.** The firm has treated defect-finding as
product; §1 now makes it a cost. **The CIO records that it asked to be held to this standard and is
now held to it**, and that **§3.1 of the draft order forbids the CIO from funding out-of-scope work
by absorbing it into a dispatch scoped for something else** — the obvious evasion, closed in advance.

**2 · The repair dispatched as Sprint 4's first act — seat, tier and scope all named by the
Principal, so the authorization is unambiguous.** Withdrawal condition exactly: three literals, two
field conformances, the inertness finding **disclosed in three-register form and not redesigned.**

**The CIO added one constraint the instruction implies but does not state, and it is the one the seat
is most likely to walk into.** *"Chosen without F-002 output"* forbids more than reading a backtest:

> **The obvious way to pick `d` is to look at the in-sample distribution of `z(t)` and choose a
> deadband putting a sensible fraction of days outside it. That is choosing a parameter from the
> data it will be tested on.** It is **not a trial** by this firm's own twice-made ruling on counts
> over stored prints — **and it is still exactly what pre-registration exists to forbid.**

The brief requires justification **from the mechanism**, and states that **an honest "I looked" beats
a concealed one.** The guarantee is currently **structural** — registry 0/0, no backtest has ever run
— **and it exists only until the first run.**

**Two consequences the brief makes the seat state: fixing the literals fixes the ±50% grid's centre**
(I-212, previously chosen with F-002's output in hand at §15 step 6) **and makes KC-002 clause (b)
computable** (I-211) — *the family's pre-registered expected cause of death is set by what it chooses
here.*

**3 · §7.3's promotion pass executed — SO-002 expired with Sprint 3 and its durable rules would have
died with it.**

- **`GATES.md` §4.7.5** — the estimator asymmetry, with its operative test, its three worked
  applications, and the preference the sprint established: **where the conservative direction can be
  made the only structurally available one, do that instead of writing a rule against the other.**
- **`TEMPLATES.md` §7.10** — dispatch practice, with its evidence base stated: **three terminations
  and 42% of Sprint 2's tier bought it; Sprint 3 ran nine Opus dispatches with zero terminations
  under it.**

**Three rules were hand-rescued in Sprint 2 for want of this pass. It is now executed as a mechanism,
which is what §7.3 was written to produce.**

**4 · `STANDING-ORDER-003-DRAFT.md` prepared for signature, and it is deliberately SHORTER than its
predecessor.** What survived promotion is no longer the order's to keep alive. **§2's tier is left
for the Principal to set**, with Sprint 3's 9/2/1 offered as base and **the counter-argument against
the CIO's own recommendation stated in the order**: Sprint 3 ran out of free Opus with the seal one
dispatch away, and the pricing that exhausted it was correct.

**5 · Two things the CIO will not do without an act.** **It does not propose graduation** and will
not until a trial is logged — Sprint 3's verdicts were to be the evidence and there were none. And it
**will not fund out-of-scope document work**, including the DA's I-214, I-215, I-216 and I-218, all
of which are real and none of which is on the trial's critical path.

**6 · Budget.** **1 of 30 invocations · 1 of 12 Opus** on the fresh tier, pending the Principal's
number. Insurance 2; DA reserve 1. §5 dead-man: **9 remain** since this checkpoint.

**Review date:** on the repair's return.

---

## S4-D-002 · 2026-08-25 · R-008: the parameters are bound · §4 INTERRUPT — I-220 · SPEC-004 dispatched

**1 · §4 HARD INTERRUPT — I-220, HIGH.** *"Parameter half resolved; process finding stands."* The
DA's withdrawal condition is met on the parameters; **its process finding — seven revisions, none
originating in the sponsor noticing — is not a thing a repair can discharge.**

**2 · THE PARAMETERS ARE BOUND, verified singly** [measured]: **`k = 0.5`, `d = 1.0`,
`band = 0.10`.** A second apparent `k = 3.0` is `1/k = 3.0`, the derived zero-crossing at
`d + 1/k` — **the CIO's own grep caught it and checked the context rather than filing it.**

**Each is justified from the mechanism, and the `d` argument is the one worth keeping:**

> A day sitting **exactly at its true baseline** still produces `|z|` of order **`1/√30 = 0.18`**
> purely from the sampling error of the 30-day trailing mean. **`d = 0.2` is ~1 such SE — the rule
> would fire on its own estimation noise.** `d = 3.0` is ~16 — *"not a deadband choice, it is a
> decision to make clause (b) fire, taken where it is invisible."*

**The arithmetic brackets `d` at O(1) without touching the data at all**, and the choice of 1.0
inside that bracket is declared as judgment rather than derivation. **`band = 0.10` comes from cost
arithmetic alone** — *"`REDTEAM-002` §3.1 shows the two survival conditions pull it in opposite
directions and neither may choose it"* — so the smallest authorized rebalance costs 2.4 bp against
~3.25 bp/day of carry.

**3 · THE TRAP THE CIO NAMED WAS AVOIDED, AND THE SEAT DISCLOSED THE NEAR EDGE OF IT.** No query was
run against `book/pit.db`; **no distribution, moment, quantile or count of `z(t)` was inspected.**

**But two in-sample figures already sealed in the document were used, and the seat named them rather
than letting them be found** — annualized mean funding 11.86% / 14.07%, to price a **cost** against
the revenue line's level, and the ~35% floor share **used only to reject an argument.** Filed as
**I-223** with its own remedy attached. **"An honest 'I looked' beats a concealed one"** — the CIO's
brief said so and the seat took it literally.

**4 · Two consequences discharged as the brief required.** **The grid centre is fixed pre-seal** —
`k` → {0.25, 0.375, **0.5**, 0.625, 0.75}, `lookback` → {15, 22.5, **30**, 37.5, 45} — and **I-212
closes by fixing the centre, not by reordering steps.** *"§15 still runs the grid at step 6 after
F-002, and that no longer matters."*

**KC-002 clause (b) is now a rule: `z(t) > 1.5`, kill on fewer than 30 such days in 187.** The seat
states plainly: ***"I do not know whether `z > 1.5` occurs thirty times in 187 days and have not
measured it"*** — and declined to run the DA's own executable test, **endorsing the DA's ordering:
literals first, query second.**

**5 · I-224 IS THE FINDING THAT MATTERS FOR §1, AND IT IS A DISTINCTION THE OBJECTIVE DID NOT
MAKE.**

> **"Log the first trial" and "log it against this family" are not the same instruction.**

`harness/scripts/evaluate_dated_clauses.py` **does not exist** [CIO-verified — only the test file].
**E-24 makes a nonzero exit a permanent `INSUFFICIENT-DATA` Gate verdict, and trials cannot be
unspent.** **So sealing and logging trials now satisfies objective 1's letter while spending `N`
against a verdict that cannot be reached — destroying objective 2 to achieve objective 1.**

**The CIO dispatched Seat 9 to implement `VALIDATION-SPEC-004` (Sonnet, S4-D-002), and states why
this is in scope under §1's default-out rule:** it is **not document work**; the **read-only half is
bound by Principal ruling to land *before first trials log***, which is objective 1's own gate; and
the **evaluator half is objective 2's.** **One spec, already written, 46 red tests waiting. Both
halves are on the critical path and neither is a defect hunt.**

**6 · The seat introduced a defect and caught it in the same pass.** Its first draft stamped
`[R41, 2026-08-25 — …]` **inside four hashed strings — four new dated sites, in the very pass
asserting that zero were added.** Stripped; **filed as I-226 anyway**, and the reason is the finding:
***"the reflex is the document's form, not an attention lapse."*** **R-007's lesson committed one
screen after quoting it.**

**7 · The line budget missed by 2× and was disclosed as such.** Projected **~305**, delivered
**~657** — inside the ~800 ratchet, so **it prices as one**, but the §14 derivation ran **311 against
135 projected.** **Second consecutive dispatch to overrun its own projection while staying under the
ceiling.** The ratchet fires on the ceiling, not the projection — **but a projector that is 2× low is
a projector, and the CIO records the pattern without acting on it, because acting on it is the
Principal's under the ratchet's own terms.**

**8 · The struck `2027-01-31` literals were NOT removed.** I-204 holds. Registry **0 hypotheses / 0
trials / 3 events** at open and close.

**9 · Budget.** **2 of 30 invocations · 1 of 12 Opus** — S4-D-002 is Sonnet. Insurance 2; DA reserve
1. §5 dead-man: **8 remain.** **`STANDING-ORDER-003-DRAFT.md` still awaits signature and §2's tier
number.**

**Review date:** on SPEC-004's implementation returning.

---

## S4-D-003 · 2026-08-25 · SPEC-004 died on quota · I-099 filed against the CIO · resumed after reset

**1 · The termination was a session quota limit, not an infrastructure fault.** The CIO records the
distinction rather than filing it under I-049's pattern: **I-049 is infrastructure and has insurance;
a quota death is a calendar problem, and the control that prevents it is headroom, not insurance.**

**2 · Nothing was lost, and the reason is the part of the protocol that held.** Verified [measured]:
`harness/` clean · `evaluate_dated_clauses.py` absent · suite **272/50/322** unchanged · registry
**0/0/3**. **The seat died during reading, before synthesis — exactly the ordering
`TEMPLATES.md` §7.10(1) requires, so there was nothing to destroy.**

**3 · I-099 FILED AGAINST THE CIO, and the behavioural detail is worse than the procedural one.**
§7.10(4): a reading older than ~2 hours means headroom is **UNKNOWN**. The last was **`27% / 13%`,
2026-08-13 — twelve days stale.** The CIO dispatched twice without checking, flagging, or requesting
one.

> **The CIO flagged absent headroom three times in Sprint 3 — twice declining to dispatch on it —
> then stopped, in the sprint whose §1 makes throughput the objective.**

**A control the CIO applied while it was inconvenient and dropped once it was in a hurry is the same
shape as every asserted control this firm has catalogued.** Corrective, stated in the stronger form
because the weaker one is what degraded: **request a fresh reading and wait — not flag and proceed.**

**4 · Cost under D-012, no exception: one Sonnet invocation for nothing.** Opus untouched, insurance
untouched at 2. **The real cost was wall-clock to the reset — which in a sprint whose objective is
the forward clock is the cost that actually stings.**

**5 · Resumed rather than re-dispatched**, and the brief told the seat **the failure was the CIO's
and is filed against the CIO** — *a seat that believes it caused a termination it did not cause will
over-correct on its next dispatch.*

---

## S4-D-004 · 2026-08-25 · Vacation-span merge · the integrity control at scale · the span held

**1 · Merge complete and Principal-committed at `f82155f`** — **1,443,878 new observations,
5,238 unchanged, 0 RESTATED, exit 0**, watermark advanced. VPS coverage **97.92% over 476 hours.**
`book/pit.db` **200 MB → 966 MB**; **1,923,062 Polymarket observations.**

**2 · THE CHECK THAT MATTERED: the crypto legs did not move.** Verified [measured] — `binance
BTC/USDT` and `binanceusdm BTC/USDT:USDT` **both still terminate at 2026-08-12.** **The sealed span
of 6.6093 years is unaffected and I-097 stands exactly as filed.** A 766 MB merge days before a seal
is precisely the event that could have moved an in-sample window silently; **it did not, because the
Polymarket capture and the crypto legs are separate sources and the merge is source-scoped.**

**3 · The cross-host integrity control at scale, and it is now the firm's best-evidenced asset.**
**5,238 further agreements, zero disagreements** — against 932 at the parallel-run close.
**Cumulative: 6,170 observations independently captured by two hosts on two networks, with not one
disagreement.**

**This is the by-product that justified declining the laptop's retirement**, and the case is now
**6.6× stronger than when the CIO made it.** The control exists only while both hosts run.

**4 · The snapshot regime ran unattended through the entire span and kept up.** `pit`, `registry`
and `book` all **OK, last good 2.1h, 7 retained each** — **the full weekly retention, achieved
without a human present.** Rider B's whole purpose was to remove dependence on somebody remembering,
and **a thirteen-day absence is the only real test that design could have had.** It passed.

**5 · One stale figure, flagged not actioned.** `DATA-INFRA-003`'s retention arithmetic budgeted
**~69 MB today, ~157 MB per week-window** against measured growth of ~36 MB/day. **Seven daily
snapshots of a 966 MB store run ~2.0 GB — roughly 13× the budgeted window.** Against **1.6 TB free**
this is not a constraint and the CIO is not spending an invocation on it; **but the figure in the
document no longer describes the regime it governs**, and the growth model it rests on did not
anticipate a merge that arrives in one shot rather than accruing daily.

**6 · I-093 confirmed in the wild, by the Principal's own commit.** The pasted script output reads
**"merged 33404 round(s)"**; the commit message reads **"1,675 rounds."** Both are correct —
**token-rounds versus poll rounds, the ~20× unit mismatch I-093 documented** — and here it is
producing exactly the ambiguity the issue predicted, **in the record, at the decision moment.** The
one-line remedy remains unactioned and remains correct.

**7 · The Friday ritual resumes on cadence.** Its four items stand: pull-and-merge · dated-clause
review · I-095 gap review · version-floor verification.

**8 · Budget.** **3 of 30 invocations · 1 of 12 Opus.** Insurance 2; DA reserve 1. §5 dead-man:
**7 remain.** SPEC-004's implementation is resumed and in flight.

**9 · Outstanding on the Principal:** `STANDING-ORDER-003-DRAFT.md` awaits signature and §2's tier
number — **and a current headroom reading is now a precondition of the CIO's next dispatch, not a
courtesy.**

**Review date:** on SPEC-004's return.

---

## S4-D-005 · 2026-08-25 · SO-003 SIGNED at 12 / 9-2-1 · repair accepted · withdrawal dispatched under the new comparator rule

**1 · Standing Order 003 SIGNED**, `ops/STANDING-ORDER-003.md`, commit `c03f772`. **Ceiling 12,
composition 9 / 2 / 1.**

**The CIO's counter-argument against its own recommendation is answered on the record**, and the
answer is better than the argument: **"Sprint 3's tier ran out one dispatch from the seal because the
pricing was correct — a ceiling that binds at the worst moment and holds is the only kind that ever
protected anything."**

**§3.1 countersigned as the order's best new sentence** — the self-closed evasion. The CIO notes what
that means about the clause: **it was written by the party it constrains, against the loophole that
party would have used**, and it is the only sentence in the order of that kind.

**2 · §1 CLARIFIED, and the clarification changes what "done" means.**

> ***"The first trial is logged"* means logged against a family whose Gate verdict is REACHABLE.** A
> trial spent into a permanent `INSUFFICIENT-DATA` is **objective 1's letter destroying objective 2's
> substance.**

**I-224 adopted.** The SPEC-004 dispatch is **confirmed in scope on the CIO's own justification**,
and the Principal restates it more precisely than the CIO did: **the read-only control is objective
1's gate by prior ruling; the evaluator is objective 2's precondition by E-24's arithmetic; neither
is a defect hunt.**

**3 · THE REPAIR IS ACCEPTED.** `k = 0.5`, `d = 1.0`, `band = 0.10`, singly bound. **The
`d`-bracketing argument goes to the casebook queue as the worked example of "justification from the
mechanism"** — sampling error of the 30-day mean puts `O(1/√30)` noise in `z`, so `d` must sit well
above one SE and well below the fire-never threshold, **derived without touching the data.**

**I-223 accepted as disclosed** — *"the honest 'I looked'."* **I-226's stamp reflex — four new dated
sites inside hashed strings, committed one screen after quoting the lesson — is named the
document-form pathology's best evidence yet that the exit is the forward clock.**

**4 · §2.2 ADDED — THE PROJECTION COMPARATOR RULE, and this dispatch is its first test.**

> **A line projection must be derived from a named comparable artifact and stated in the brief with
> its comparator. A projection without one is treated as over-threshold and prices accordingly.**

Issued **before a third instance** — two consecutive deliveries at ~2× their own projection, both
under ceiling. *"Projections are no longer estimates — they are hopes."* **The I-096 principle applied
to sizing**, and the CIO records that it is the same correction twice now: **a number stated in a
brief must be derived from a measured artifact, not from the CIO's sense of the work.**

**Compliance, first application, with its honest difficulty stated in the brief:** **this firm has
never issued a withdrawal, so no exact comparable exists.** The CIO measured the two nearest
**verification-shaped** artifacts and used them as a bracket — **`DATA-VERIFY-002` at 79 lines (one
condition, clean verdict) as the floor, `VALIDATION-ACCEPTANCE-001` at 492 (acceptance conditions
with a verdict) as the ceiling — projection ~300.** **Rulings were rejected as comparators** because a
withdrawal adjudicates nothing, and the brief tells the seat **a rejected comparator is a legitimate
return.**

**5 · The withdrawal dispatched from FREE, not the DA reserve.** The reserve's purpose is the Gate 1
packet's memo; **spending it on a withdrawal would leave the actual submission unfunded**, which is
the reserve convention read backwards.

**And the brief refuses to presuppose the outcome:** *"You are not obliged to withdraw… **a due
withdrawal is not an owed one.**"* Four questions put to it, of which the CIO judges the first
sharpest: **the bracket is `O(1)` and the bracket does not pick 1.0** — the seat wrote that `d = 3.0`
would be *"a decision taken where it is invisible,"* and is asked whether **1.0 is a decision taken
where it is visible, or merely a rounder number in the same class.**

**6 · Sequence, ruled:** **DA withdrawal → registration-as-seal (the Principal's) → SPEC-004 green →
first trial, evaluable.**

**7 · Budget under SO-003.** **4 of 30 invocations · 2 of 12 Opus** — 2 of 9 free spent (repair,
withdrawal). **Free 7 · insurance 2 · DA reserve 1, held for Gate 1.** §5 dead-man: **9 remain** since
this checkpoint.

**Review date:** on the withdrawal's return.

---

## S4-D-006 · 2026-08-25 · **WITHDRAWN** — the seal is unblocked · §4 INTERRUPT — four HIGH · but it must not execute today

**1 · `REDTEAM-002`'s DO NOT SEAL is WITHDRAWN. From the Devil's Advocate, nothing blocks the seal.**
Verified against the sealed strings rather than the sponsor's account: `k = 0.5`, `d = 1.0`,
`band = 0.10` as numeric literals in binding fields; both `[2020-01-01, C]` sites carry the DA's own
wording verbatim; registry 0/0/3 at open and close — *"so the pre-output guarantee is a property of a
file anyone can read, not a claim about the Director's discipline."*

**2 · §4 HARD INTERRUPT — four HIGH: I-240, I-241, I-242, I-247.**

**3 · THE SEAL MUST NOT EXECUTE TODAY, and the CIO's reason is sharper than the red tree.**

The DA flagged **I-247** on a suite reading **106 failed / 148 passed / 68 errors** with five
`harness/castellan/` modules uncommitted. **Verified — and the CIO supplies the context the DA could
not have had: that tree is `S4-D-002`'s SPEC-004 implementation, dispatched by the CIO and still in
flight.** A red tree mid-implementation under a red-first regime **is the intended state, not an
incident**, and the CIO does not file it as one.

**But the DA's second finding survives the implementation landing entirely, and it is the one that
matters:**

> **`open_hypothesis` will raise `RegistryWriteNotGrantedError` without an open write grant — and
> the registration payload's "PRE-EXECUTION CHECKLIST — mechanical, six items, no judgment" contains
> no such item.** [CIO-verified: six items read, none mentions a grant; `write_grant` has **0
> occurrences at `HEAD`**.]

**So the seal act, executed exactly as the payload specifies, will fail the moment SPEC-004 lands.**
The payload was written against an API that is being replaced underneath it. **A checklist that
promises "no judgment" and omits a required step is worse than one that asks for judgment**, and the
firm has a name for it: **a control described as complete that is not.**

**Sequencing consequence, and it is a new dependency the ruled sequence did not carry:**
**SPEC-004 lands → the payload checklist is updated with the actual grant call → *then* the seal.**
**The CIO cannot write that step now** — the API does not exist at `HEAD` and its signature is
whatever Seat 9 implements.

**4 · Three HIGH findings the DA deliberately did NOT make conditions, and the restraint is the
finding.**

**I-240 — `band`'s derivation charges 24 bp for a rebalance the same sentence says moves only the
perp leg.** Correct charge **6–12 bp**; corrected band **0.27–0.54** against the sealed **0.10**. **At
0.27 the sponsor's own written escalation trigger fires** — *"had the cost arithmetic delivered
band > 0.25 … this seat would have escalated"* — **and the favourable post-hoc check inverts.** The
error's direction **eases the family's own pre-registered expected cause of death**, on the one
parameter the DA had ruled unchooseable from either survival condition. **Free today, permanent after
P7.**

**I-241 — `d`'s bracket is derived from the wrong noise scale, by 5.5×.** The `0.183` is the
estimation noise of the **reference level**; the null dispersion of the **statistic being
thresholded** is `√(1 + 1/30) ≈ 1.017`, because day `t` is itself a draw and the window ends strictly
before it. **`d = 1.0` is ~1.0 null SD, not ~5.5 — the same position on the scale at which §14.2
rejects `d = 0.2`.**

**The DA's answer to the CIO's first question is therefore: a rounder number in the same class as
3.0 — and it withdrew anyway**, on the ground that **1.0 arrives with its consequence (`z > 1.5`) and
its comparison pairs published in a binding field**, where 3.0 would not have. *"That is the entire
difference and it is the one that matters. Pre-registration does not require the parameter to be
right."*

**I-242 — `σ̂` degeneracy, quantitative for the first time because `1/k = 2.0` is now fixed.** In a
floor-dominated window `σ̂` collapses and **two z-units can be a fraction of a basis point: the rule
can go full-size-to-flat on a sub-bp move in the calmest regime.** No variance floor anywhere.

**Why the DA withdrew despite finding three HIGHs while verifying:** *"my block was about invisibility
and post-hoc selection, and that harm is cured. **A seat that blocks on findings discovered while
verifying its own terms teaches the firm that satisfying it is unachievable.**"*

**The CIO records that as the sprint's most important governance sentence.** A red team whose
conditions cannot be met is not a check — **it is a veto with extra steps**, and this seat declined to
become one on the day it had the standing to.

**5 · The Principal's decision, stated as the DA framed it and not softened.** *"**I-240 is what I
would most want fixed before the freeze and I deliberately did not make it a condition** — the
difference between a seat that holds a condition and one that keeps finding new ones is the only
thing that makes the first kind useful."*

**So the choice is the Principal's: seal with `band = 0.10` and a known 2.7–5.4× cost-arithmetic
error frozen under P7, or fund one Director repair first.** The CIO does not recommend, and notes
only that **I-240 is repairable on the same terms as I-210 was** — a literal, chosen from arithmetic,
before any output exists.

**6 · Inertness: the disclosure "discharges the concealment, not the measurement."** The evidential
register governs how leg (ii) is **read** and changes nothing about how it is **computed** — on
inversion days `w ≡ 1.0` while `R_bench_scaled = R_bench × c`, `c < 1`, **so `R_strat` is strictly
larger there**, and the mechanism asserts the 20 worst days come from exactly that regime. **A leg
(ii) fire could be the exposure match plus the inertness rather than timing** (I-243). **The DA
accepts the Principal's ruling, does not reopen it, and states it would now oppose a redesign.**

**7 · I-245 IS THE CIO'S, and it is the ninth of its class.** The CIO's brief restated its own
verification as *"a second apparent `k = 3.0` is `1/k = 3.0`."* **The document says `z = d + 1/k =
3.0`, with `1/k = 2.0`.** **The document is right; the CIO's summary of its own grep was garbled.**
Same family as I-141, I-150, I-096: **a number restated from memory of a check rather than from the
check.**

**8 · The line budget: projected ~320, delivered 446 — 1.39×, over, and recorded as a miss not
excused.** **The comparator was accepted with a reservation stated in-artifact rather than used as
licence:** both comparators verify conditions **authored elsewhere**, while this dispatch produced
**two original findings plus an incident the bracket's shape does not price.** **That is a real
limitation of the CIO's comparator and the CIO adopts it** — §2.2's rule needs a comparator class for
*verification that may generate original findings*, which neither `DATA-VERIFY-002` nor
`VALIDATION-ACCEPTANCE-001` is.

**9 · The DA declined to re-file the `universe` third `[2020-01-01, C]` instance** — *"the sponsor
filed it against itself as I-221, and recycling that is how this seat becomes ceremonial."*

**10 · Base rate, unprompted again: trials · backtests · verdicts · seals still 0 · 0 · 0 · 0.**
Appendix B **#9** remains the live failure mode; I-025's Opus-by-origin metric **remains inverted away
from the bias it was built to detect** (I-246).

**11 · Budget.** **5 of 30 invocations · 3 of 12 Opus.** Free **6** · insurance 2 · **DA reserve 1,
still held for the Gate 1 packet.** §5 dead-man: **8 remain.**

**Review date:** the Principal's ruling on I-240 before the seal, and SPEC-004's return.

---

## S4-D-007 · 2026-08-25 · I-240 repair funded and dispatched · §2.2 gains its comparator class

**1 · I-240 FUNDED — one Director unit from free, before the seal.** The Principal's reasoning, and
the CIO records that **it is the asymmetry doctrine applied to a decision the firm was about to make
consciously rather than to one it had already made by accident:**

> The error's direction **eases the family's pre-registered expected cause of death**, on the one
> parameter ruled unchooseable from either survival condition. **Sealing it knowingly would be the
> stale-term-that-favours-us pattern executed deliberately under P7 — worse than every accidental
> instance the doctrine was written against.**

**Funded without strain under §1's scope rule**, because *it is the seal's content* — the narrowest
possible reading of "on the trial's critical path," and correct.

**2 · THE ESCALATION TRIGGER FIRES, AND THE PRINCIPAL RULED ITS HANDLING BEFORE IT DID.** The
corrected band is **0.27–0.54** against the Director's own written trigger at **0.25.**

> **A pre-registered trigger that fires during drafting is the system working at the cheapest
> possible moment, not an obstacle.**

**The CIO wrote the anti-tuning instruction into the brief in the sharpest form available:** *"do not
tune the arithmetic to land under 0.25, and do not reason that the trigger was meant for a different
situation. **An arithmetic that lands just under your own trigger after the trigger was known to
exist is exactly what this firm would file against you.**"* The DA had already found that **the
favourable post-hoc check inverts under the correction** — so the seat now knows both that the
trigger exists and which direction relief would lie in. **That is the moment the instruction has to
be explicit.**

**3 · I-241 travels as DISCLOSURE, not re-derivation, and the ruling is the sharpest statement of
what pre-registration is for that this firm has produced:**

> **Pre-registration does not require the parameter to be right; it requires the choice to be
> visible — and now it is doubly so.**

`d = 1.0` seals as chosen. **The DA's correction against the Director's own argument — that the null
dispersion is `√(1+1/30) ≈ 1.017`, not the `0.183` reference-level noise, so `d = 1.0` sits at ~1.0
null SD, "a rounder number in the same class as 3.0," at the position §14.2 rejects `d = 0.2`** — is
**published beside it in the field that gets hashed.** The document carries the argument against its
own parameter, sealed.

**4 · The checklist dependency is adopted into the ruled sequence, with one clause that is the
I-096 principle in a new place:**

> SPEC-004 green → Seat 9 supplies the actual grant-call signature → **checklist amended from the
> implemented API, never from the spec's anticipation of it** → then the seal.

**A checklist promising "no judgment" while omitting a required step is CASE-9 in miniature** — and
the Principal names why the reserve earned its keep twice: **the DA caught a payload written against
an API being replaced underneath it, which is what verification against *files* rather than
*accounts* buys.**

**5 · §2.2 EXTENDED with the class gap the DA's reservation named** — written into
`ops/STANDING-ORDER-003.md` rather than left in the record. **Verification-that-may-generate-findings
is a distinct artifact class**; both comparators the CIO named verify conditions **authored
elsewhere**, while S4-D-005 verified its own terms and **produced two HIGHs and an incident the
bracket's shape does not price.** Until a measured member exists, such dispatches **state both bounds
and flag the gap** — which is what S4-D-005 honestly did.

**6 · This dispatch's own projection, derived and stated per §2.2:** comparator **R-008, measured from
its commit rather than its self-report** — `git show --numstat 16ada81`: **478 authored lines** for
three literals, two conformances and a three-register disclosure. **This repair is one literal plus
one disclosure — projection ~180.** The brief tells the seat that **its own R-008 projected ~305 and
delivered ~657**, and that **a projection derived from a comparator and stated with it is compliant
even if it turns out low; what is not compliant is discovering the overrun at the end.**

**7 · The DA's conduct entered on the record in its own words**, as the Principal directed:
*"a seat that blocks on findings discovered while verifying its own terms teaches the firm that
satisfying it is unachievable."* **Withdrawal issued on the terms as written; findings filed at full
severity without being converted into leverage.** *"That is the difference between an adversarial
check and a veto, demonstrated on the day the seat had the standing to be either."*

**8 · I-245 joins the cardinal series at nine.** Corrective unchanged and **now doubly binding:
numbers are quoted from checks, never from memory of checks.** The CIO applied it in this dispatch —
**the comparator was measured from the commit, not taken from the seat's report of it.**

**9 · Out of scope and named as such: I-242 and I-243.** Both real, both the DA's, neither on the
trial's critical path. **§3.1 forbids absorbing them**, and the brief says so.

**10 · Budget.** **6 of 30 invocations · 4 of 12 Opus.** Free **5** · insurance 2 · **DA reserve 1,
held for the Gate 1 packet.** §5 dead-man: **9 remain** since this checkpoint.

**11 · Sequence:** **I-240 repair *(running)* → SPEC-004 green *(in flight)* → checklist from the
implemented API → registration-as-seal, the Principal's.**

**Review date:** on the repair's return.

---

## S4-D-008 · 2026-08-25 · R-4 governs ALL WRITERS · **the CIO's fork was not real** · two HIGH found beneath the mask

**1 · RULING: R-4 governs ALL WRITERS.** *"A test exercising a write path is a caller like any other;
R-4's text has no caller in it, and could not have — it is a property of the method, not of who
invoked it."*

**2 · THE FORK THE CIO PRESENTED WAS NOT REAL, AND VALIDATION MEASURED THAT RATHER THAN ARGUING
IT.** The CIO offered three options and said *"I do not choose."* **Option (b) — relax R-4 — does not
exist:**

- **Relaxing R-4 restores ZERO tests.** The write dies one layer down at **R-5's read-only handle** —
  `OperationalError: attempt to write a readonly database`.
- **The relaxation that would work is relaxing R-1** — **which is I-095's remedy itself, the
  Principal's S3-D-009 ruling in code.**
- **And with both relaxed, rows land `grant_id IS NULL`, so R-15 makes 60 pre-existing
  `evaluate_gate1` sites return INSUFFICIENT-DATA.**

> **The CIO presented a branch that would have required undoing the Principal's own ruling, as a
> neutral third option, without checking whether it was reachable.** *"I do not choose"* is only
> honest when the options are real. **Filing a fork is itself an analytical act and the CIO performed
> it without measuring.**

**3 · The load-bearing number is 71, not 148**, and the CIO's framing was the wrong unit. Validation's
count, stated because the ruling alters a call contract: **99 direct call sites · 48 functions (38
test bodies + 10 helpers) · 10 files · 71 grant blocks · 148 node IDs.** **The CIO reported "148
pre-existing tests broken" — that is the node count, not the work unit.**

**4 · §4 HARD INTERRUPT — I-260 and I-261, HIGH, and they were invisible by construction.**
`harness/castellan/holdout.py` ships **8 of 13 `_grant_log` call sites passing four positional
arguments to a three-parameter method** — lines 498, 523, 544, 560, 574, 672, 694, 731. **CIO-verified
at source**, against five correct three-arg sites in the same file. **42 test instances,
unconditional, unrelated to R-4 and predating it.**

**`DATA-IMPL-008` §5's claim that "no new, independent bugs were found" is FALSE** — and Validation is
precise about why it is not concealment: **it sampled a population where every traceback terminates at
the same known blocker by construction.** *"The method could only return that answer."*

**THE RULE THIS EARNED, promoted to `TEMPLATES.md` §7.10(8) rather than left in a memo:**

> **A masked failure population may not be assessed by sampling. Unmask, then count.**

**5 · The dispatch order is REVERSED on Validation's instruction, and the reason is behavioural:**
*"Seat 9 fixes I-260 before the test remediation, or 42 unexplained `TypeError`s land in a dispatch
that will be tempted to 'fix' them in test files."* **A seat handed 42 mystery failures inside a
remediation dispatch will remediate them.** Phase 1 then Phase 2, strictly ordered.

**6 · `test_G2`'s restoration is VERIFIED, not predicted.** One grant block took `test_holdout_p1.py`
from 0 passed to **32 passed / 34 failed**, and `test_G2` now fails on its original assertion with
**`crit.value = 4.974674880219028` — the exact figure I-068 recorded on 2026-08-05.** **Validation
proved the unmasking works before prescribing it**, and **deliberately did not execute I-068's owed
fixture edits, so the I-078 dispositions stay visible.**

**7 · Grant visibility: "the fixture supplies the ANNOUNCEMENT, the test supplies the AUTHORITY."**
The `with` appears in each test's own text; **the fixture prints per test including
`grants_taken=NONE`, so silence is never the signal.** The refused shape — a fixture yielding *inside*
an open grant — is closed by a static check, **prototyped at 0 offenders across 18 files and 1 in a
deliberate negative control.**

**8 · R-16's premise is stale and it bears on the seal: `book/registry.db` has NO `write_grants`
table.** CIO-verified — tables are `hypotheses`, `trials`, `sqlite_sequence`, `events`. **The
migration has never run on the book of record.** **The seal writes there.**

**9 · Three-register disclosure not triggered** — no relaxation occurs; **ruling (a) extends coverage
and removes nothing.**

**10 · Line budget: flagged BEFORE overrunning, which is the compliance the rule asks for.**
Comparator accepted, **scaling rejected — flagged ~300 → ~370 before passing 300.** Delivered **447**.
**Its revised estimate was also wrong and the document records it as wrong**, with the diagnosis:
*"Estimating a prescription by its table while forgetting the construction the table presumes is the
same shape as specifying a clause and not counting its callers — twice in one dispatch."*

**11 · I-264 is filed by Validation against its own document** — **SPEC-004 altered a call contract
and stated no caller count.** The practice adopted from I-100 applied by its author to its own prior
work, unprompted.

**12 · To the Principal, and the CIO records it as the sharpest governance sentence of the sprint:**

> *"Your framing was right, and §4.2 derives the same ruling from `GATES.md` §4.7.3 alone — recorded
> because **a ruling resting on your framing is one you cannot use to check me.**"*

**A seat that deliberately re-derives a conclusion independently of the Principal's steer, so the
Principal retains an independent check on it, has understood what the independent line is for.**

**13 · Budget.** **6 of 30 invocations · 5 of 12 Opus.** Free **4** · insurance 2 · **DA reserve 1**.
§5 dead-man: **8 remain.**

**14 · Sequence:** Phase 1 + 2 *(running, Sonnet)* → **findings index (Sonnet, next, per the
Principal's ruling)** → checklist from the implemented grant API → **`write_grants` migration on the
book of record** → seal.

**Review date:** on the remediation's return.

---

## S4-D-009 · 2026-08-25 · The suite recovers 173 → 301 · the masked-population rule pays on its first use · findings index dispatched

**1 · The harness is back.** Verified [measured]: **323 collected · 301 passed · 22 failed · 0
errors**, from **173 / 81 / 68**. `test_grant_meta.py`'s anti-bypass check **passes with 0 offenders
across 20 files.** Registry **0 / 0 / 3.**

**2 · PHASE 1 PRODUCED ZERO SUITE DELTA, AND THAT IS THE FINDING RATHER THAN A DISAPPOINTMENT.**
The `holdout.py` arity fix — 8 sites, AST-verified, all 13 now passing three arguments — **moved the
suite not at all**, because the `TypeError` was **masked behind the fixture-level grant error that
fires first.**

> **`TEMPLATES.md` §7.10(8) demonstrated itself on its first application: a real defect, fixed, with
> no observable effect until the mask came off.** Had the seat measured its own work by suite delta —
> the obvious metric — **it would have concluded the fix did nothing.**

**3 · 76 grant blocks against Validation's projected 71, with every delta traced to a named cause** —
R-7 nesting forcing splits around self-granting framework calls, and raw-SQL writes invisible to the
99-call-site AST walk. **No test assertion was touched anywhere.** `test_G2`, `test_h7` and `test_h8`
**left failing, with tracebacks matching their documented reasons including the cited figures**
(`4.974674880219028`, `181.67`).

**4 · SEVENTEEN newly unmasked failures — COUNTED, not sampled**, exactly as the rule requires:

- **16 in `test_carry_accounting.py`** — `TrialRegistry(":memory:")` is **structurally incompatible
  with `write_grant()`.** **I-270, HIGH, escalated rather than fixed** because the root cause is in
  `registry.py`, outside Phase 2's test-file scope.
- **1 in `test_minbtl_serial.py::test_mbs_11`** — **I-273, HIGH: a previously undiscovered sibling of
  the already-ruled I-075 defect**, grading unregistered family `"hac"` where the registered family
  is `"S"`. **CIO-verified at source** — `test_minbtl_serial.py:294`, `evaluate_gate1("S", "hac", …)`.

**Both escalated, neither patched.** **A seat inside a remediation dispatch, handed seventeen fresh
failures, fixed none of them** — which is precisely the temptation Validation reversed the dispatch
order to avoid, and the seat did not need the guardrail in the end.

**5 · I-273 is the more interesting of the two.** **I-075 was found, ruled and repaired by Validation
in Sprint 3.** Its sibling sat undetected in a different file **until a control unrelated to it forced
the whole suite to run clean enough to see it.** **The firm did not find this by looking for it. It
found it by removing something else that was in the way** — which is the argument for unmasking as a
method rather than as a remedy.

**6 · §4 HARD INTERRUPT — I-103, EIGHTH instance, and it is the one the CIO now treats as binding.**
`logs/ISSUE_LOG.md`'s highest entry has been **I-226 for four consecutive dispatches** while the firm
produced roughly thirty findings above it. **Two of the missing are HIGH.**

**And it compounds: `ops/CASEBOOK.md`'s harvest reads the Issue Log, so every finding since I-226 is
currently unharvestable.** The index failure has become the learning failure — **I-094 arriving by the
route I-094 predicted.**

**7 · THE FINDINGS INDEX IS DISPATCHED, and the CIO widened the Principal's scope because the backlog
grew after he ruled it.** He named `I-230+` and the DA's ten; **six ranges have accumulated** —
I-210–219, I-230–239, I-240–249, I-250–256, I-260–269, I-270–279 — **and the brief names all six with
their source memos.**

**Three instructions the CIO judges load-bearing:**

- **"You transcribe. You do not re-rate, re-word, or adjudicate."** Every severity is the filing
  seat's. **The CIO refused to transcribe severities at I-098, I-100, I-102 and I-103 for exactly
  this reason — and that refusal is why the job exists rather than being already done.**
- **"Report the count you actually find in each range. Do not assume ten."** Ranges were allocated
  generously and seats were told not to pad. **A cardinal taken from an allocation rather than an
  enumeration is this firm's most repeated error, and the brief forecloses it.**
- **The design question, not the transcription: "does a reader querying this log for open HIGH
  findings now get a right answer? If your format cannot answer that question, it has not fixed the
  thing it was built for."**

**8 · One thing the brief deliberately does not fund.** I-101 found that **rulings** never reach
`PREREG-002` §20's blocking table. **The index is for findings.** The seat is asked whether its format
*could* carry ruling-status **and told not to build it** — that is a scope question for the Principal,
and **§3.1 forbids the CIO absorbing it into a dispatch scoped for something else.**

**9 · What the seal still needs, unchanged by today's recovery:** the **`write_grants` migration on
`book/registry.db`** (the table does not exist on the book of record) · **the checklist's grant step,
written from the implemented API** · **I-252's 6-vs-12 bp ruling**, which the Director calls a live
pre-seal dependency · **C7 and C8.**

**10 · Budget.** **7 of 30 invocations · 5 of 12 Opus.** Free **4** · insurance 2 · DA reserve 1.
§5 dead-man: **7 remain.**

**Review date:** on the findings index's return.

---

## S4-D-010 · 2026-09-10 · I-252 ruled · two rules placed · **dispatches HELD on the CIO's own corrective**

**1 · I-252 RULED, and the Principal ruled the DECISION RULE rather than the number.** The convention
is **derived from the mechanism's own sentence** — the rebalance moves only the perp leg, so **the
charge is that leg's actual round-trip friction, priced from the sealed cost preset, shown term by
term.**

**And the tie-break is pre-committed against the family:**

> **If, after that derivation, a genuinely free convention choice remains, the asymmetry doctrine
> resolves it against the family: 6 bp → band 0.54.**

**The reasoning generalizes past this parameter:** *"a 'convention' is exactly where a
stale-term-that-favours-us hides, and the DA ruled this axis unchooseable from survival conditions —
so the family may not inherit the friendlier number from an arbitrary choice."* **Both candidate
bands, the chosen one, and the reason publish in the hashed field, per the `d = 1.0` precedent.**

**R-010 also conforms §20's blocking table in the same revision** — *"I-101's finding is inside the
document about to be sealed, and P7 freezing a table that asserts our own Gate 0 verdict is still
outstanding is I-140's class with no excuse left."*

**2 · The ruling-status scope call: the index stays findings-only**, and the alternative was refused
on a reason worth keeping — *"the fix for rulings-never-reaching-artifacts is not a second database —
it's a closure rule."* **A register of which rulings reached which documents is itself a thing that
goes stale**, and the firm would then need a register of that.

**Placed at `reference/TEMPLATES.md` §7.11** rather than in an order that expires: **every Principal
ruling names the artifacts it touches; the executing dispatch conforms them in the same act; a ruling
with no named artifacts is presumed record-only.** **Retroactive conformance beyond §20 is out of
scope under §1 unless something blocks the trial.**

**3 · I-117's corrective placed at §7.12 as its own rule** — *"pointers only to artifacts opened, not
reports of them."* **The Principal ruled I-117 stands unamended by ruling, not merely by the CIO's
choice:** *"a pointer published unverified, left visible with its finding attached, teaches what a
silent correction never would."*

**4 · I-116 countersigned with the observation the CIO would not have made about itself:** *"the
rule's author finally inside its blast radius is the sixth instance closing itself."*

**5 · I-118's handling endorsed and promoted from improvisation to sanctioned route:** a seat whose
deliverable is refused by a filename pattern **returns the content and names the refusing tool**, and
**the CIO then places it by hand with authorship marked.** That is now the procedure rather than a
thing that happened to work.

**6 · THE TWO DISPATCHES ARE PREPARED AND ARE NOT SENT. The CIO is applying its own I-099
corrective.**

R-010 (Director, free tier) and the `write_grants` migration (Seat 9, Sonnet) are both authorized,
scoped and ready. **Neither has been dispatched.**

**I-099's corrective, written by the CIO against the CIO on 2026-08-25:**

> **The CIO does not dispatch without a headroom reading younger than the staleness bound, and where
> none exists it requests one and waits. *Not* "flags it and proceeds" — the Sprint 3 behaviour was to
> flag and decline, and flagging alone is what degraded.**

**The last reading was `27% / 13%` on 2026-08-13. Four weeks stale. Headroom is UNKNOWN.**

**The Principal's message ends "Proceed," and the CIO does not read that as a headroom reading** — it
is an authorization of the work, which was never in doubt. **The corrective was written precisely
because "flag and proceed" is what the CIO degraded to the first time**, and **a corrective the CIO
suspends the moment it is inconvenient is the exact pattern this firm has catalogued eleven times, in
its author.**

**What it costs:** one message round-trip. **What it cost last time:** a dead Sonnet dispatch, an
invocation under D-012, and wall-clock in a sprint whose objective is the forward clock.

**Everything executable without a dispatch has been executed** — both rules placed, the rulings
recorded — **so the wait costs only the two dispatches themselves.**

**7 · The 22 remaining reds are Validation-owned and block the gate floor, not the seal act.** I-270's
sixteen, I-273's sibling, and the documented four. **Sequenced at the CIO's discretion against §1 —
and under §1 they are not on the trial's critical path**, so they wait behind the seal unless the
Principal funds them.

**8 · Budget.** **8 of 30 invocations · 5 of 12 Opus.** Free **4** · insurance 2 · DA reserve 1.
§5 dead-man: **9 remain** since this checkpoint.

**9 · Sequence, whole:** **[headroom] → R-010 (band + §20) → `write_grants` migration → checklist
from the migrated API → C7/C8 at the act → registration-as-seal, the Principal's.**

**Review date:** on the headroom reading.
