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

## D-001 · Sprint 2 · 2026-08-04 · Sprint 2 opens · riders A/B/C · A3 clarification

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

## D-002 · 2026-08-04 · Canonical Standing Order 001 governs · I-046 resolved · four breaches recorded

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

## D-003 · 2026-08-04 · Tool-permission policy matching the delegated authority

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

## D-004 · 2026-08-04 · Director's PREREG-002 restatement lands · §4 HARD INTERRUPT — KC-002 restated

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
dispatches into one seat and one tree was already ruled against in D-003 §4. C12 is queued
behind Rider A's return, not held for the Principal.

**7 · Budget.** 3 of 30 · 2 of 12 Opus. DA reserve holds 1 Opus for this family under §2 —
and **C3 confirms the reserve is needed**: no Red-Team Memo exists on PREREG-002. Freely
allocable Opus: **9**.

**Review date:** on the Principal's ruling on the §4 interrupt.

---

## D-005 · 2026-08-04 · Rider A returns · §4 HARD INTERRUPT — spend exceeds the stated budget

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
retry/backoff. This means the 5.5% coverage figure is **not** wholly host-sleep as D-001 §3
recorded; part of it is a defect the firm shipped. **I-048** — "not polled" vs "polled,
whole batch failed" were **provably indistinguishable** in `book/pit.db` before today.
Closed going forward at **2026-08-04T16:53:16Z** via a heartbeat wired into every exit path;
**permanently open for all prior history**. The seat checked the schema rather than
accepting the assertion carried in D-001, and the assertion was wrong.

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
transmitted off this host.** Under D-003's policy, `crontab`/`launchctl` are denied and the
spend is §4-reserved, so the cutover cannot proceed without the Principal regardless.

**8 · Budget.** 3 of 30 · 2 of 12 Opus, unchanged — Rider A was the Sonnet unit already
counted. DA reserve holds 1 Opus. Freely allocable Opus: **9**.

**9 · Record-integrity note, flagged not fixed.** `logs/DECISION_RECORD.md` now contains
**two each** of D-001…D-004 — Sprint 1's and Sprint 2's — because Standing Order 001
restarts the sequence per D-015 §3. The keys are no longer unique, which will bite at the
§7 audit. The CIO proposes a sprint prefix (`S2-D-001`) but **has not renumbered the
Principal's scheme unilaterally.** Awaiting direction.

**Review date:** on the Principal's ruling on the two open §4 interrupts.
