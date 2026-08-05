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
