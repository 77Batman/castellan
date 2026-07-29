# VALIDATION RULING 002 — Placement of the holdout cutoff `C` under the model-prior threat model

**Seat:** Head of Quantitative Validation (Seat 3)
**Date:** 2026-07-28
**Reports to:** the Principal. Dispatched by the CIO; nothing in the dispatch binds the verdict.
**Status:** BINDING. Not overrulable except by the Principal, in writing.
**Type:** specification and verdict only. No code modified, no data fetched, no backtest run.
**Follows:** Ruling 001 §2.1, §2.4, §3, §4.4. Ruling 001's other rulings are not reopened.
**Touches:** I-009 (primary), I-002, I-004, D-003.

House rule 6 applies throughout: **[measured]** = read or run in this repository; **[cited]** = external
source named in Charter Appendix C; **[inferred]** = reasoned from measured facts; **[assumed]** = a
premise I could not verify and am flagging as such.

**Disclosure relevant to §4 challenge 2:** I used no `WebSearch` and no `WebFetch` in producing this
ruling. Every fact below is from this repository or is labelled. I state this because I am about to
rule on the retrieval channel and my own conduct on it is auditable evidence.

---

## 1. Scope and what was read

**The question.** The Principal proposes a third `C`-placement option: *pin `C` at the seats' model
training cutoffs, on the grounds that a wholly historical holdout is weak against an LLM researcher
whose weights may already encode the period.* I am asked to rule the option methodologically sound,
unsound, or sound-with-modification. **The scheduling decision that follows remains the Principal's**
and I do not take it.

**Read in full** [measured]: `.claude/agents/quant-validation.md`;
`research/VALIDATION-RULING-001-holdout-regime.md`; `FUND_CHARTER.md` §3.2, §3.3, §3.4, §5 (house
rules), Seat 3, §4.1, §4.2, §4.3, §4.4, §4.5, §4.6, Appendix B, Appendix C, Appendix D;
`logs/DECISION_RECORD.md` D-001–D-004; `logs/ISSUE_LOG.md` I-001–I-009; the `tools:` and `model:`
frontmatter of all nine seat definitions.

**Three facts established in this session that the ruling turns on:**

| # | Fact | Tag |
|---|---|---|
| F1 | **Eight of nine seats hold `WebSearch` and `WebFetch`.** Only `execution-ops` does not. All nine hold `Bash`. | [measured] — `agents/*.md` frontmatter |
| F2 | **The Charter is entirely silent on this threat model.** `grep` over `FUND_CHARTER.md` and `reference/` returns zero hits for `cutoff`, `training data`, `memoriz`, `WebSearch`. | [measured — absence confirmed] |
| F3 | **The CIO seat's stated cutoff is May 2026; no other seat's cutoff is known to this firm, and the authoritative reference does not publish them.** | [measured, per I-009; the non-publication was verified by the CIO, not by me] |

F1 matters twice over. It establishes the retrieval hole as fact rather than speculation — and it
establishes that tool grants are a **live, per-seat, already-exercised control surface** in this firm.
Ops is proof the mechanism works.

---

## 2. The threat model, stated precisely

### 2.1 What a holdout is actually for

A holdout is not a ritual about data secrecy. It exists to supply one quantity: **an estimate of
performance on a sample that did not participate in the search that selected the strategy.** Every
Gate-1 criterion that depends on it — out-of-sample Sharpe, WFE, and by extension the credibility of
DSR and PBO — assumes exactly that and nothing more.

So the property to protect is not "unseen," and not "unfetched." It is:

> **No design choice binding on this family was informed, at any strength, by the holdout window.**

"Unseen" and "unfetched" are *proxies* for that property. The Principal's observation is that for an
LLM researcher the proxies come apart from the thing. That observation is correct and I adopt it
(§3.2). Everything else in this ruling follows from taking it seriously and then following it one step
further than he did.

### 2.2 The channels, and what each candidate control closes

Design choices are contaminable through five distinct channels. Ruling 001 named two. The Principal
names a third. I name two more.

| # | Channel | Mechanism | Detectable? |
|---|---|---|---|
| **K1** | **Harness-mediated ingest** | Holdout rows land in `pit.db` and are consumed through the loaders | **Yes** — `max(event_time)` vs `C`, plus Ruling 001 D2's ceiling and D1 leak test |
| **K2** | **Direct fetch outside the loaders** | A seat calls `yfinance`/`ccxt`/Polymarket from a scratch script | **No.** Ruling 001 §2.4; unclosable under this firm's constraints |
| **K3** | **Live retrieval mid-research** | `WebSearch`/`WebFetch` (F1), or `curl` under `Bash`, returns post-`C` information | **No** — no log, no artifact, no `pit.db` row |
| **K4** | **Model priors — the Principal's channel** | The researcher's weights already encode the holdout period's prices or regime | **No.** Not merely undetected — *undetectable in principle by this firm*, since we cannot inspect weights and cannot audit a corpus |
| **K5** | **The Principal himself** | The sponsor has lived through wall-clock-now and, per I-002, has already searched this specific family's history with 5 tuned parameters and 1 regime exclusion | **No.** And unlike K4, this one is **documented, not hypothesised** |

Now the control matrix. This is the ruling's central object.

| Control | K1 ingest | K2 direct fetch | K3 retrieval | K4 model priors | K5 the Principal |
|---|---|---|---|---|---|
| Ingest ceiling + vault (Ruling 001 D1–D4) | **closed** | open | open | open | open |
| `C` pinned at pre-registration (Ruling 001 §3.2) | **closed** | open | open | open | open |
| **`C` at training cutoffs (proposed)** | closed | open | open | **partly, unverifiably** | **open** |
| **`C` = today, forward holdout (option B)** | **closed** | **closed** | **closed** | **closed** | **closed** |
| Tool-grant reduction post-sealing | — | — | **narrowed, not closed** (Bash+curl, F1) | — | — |
| Pre-registration freezing binding design fields | — | narrowed | **narrowed** | narrowed | narrowed |

Read the fourth row. **A forward holdout closes all five channels, unconditionally, because the data
does not exist.** [inferred, and the inference is trivial — nothing can retrieve, memorize, or
remember a price that has not printed.] This is Ruling 001's S3, and it remains the only
unconditional protection in the entire design.

Read the third row against it. That is the ruling.

### 2.3 A sixth channel, which is not about the holdout at all

Follow K4 one step past where the proposal stops.

§4.1's apparatus takes `N` — the number of variants searched — as the denominator of everything
[cited — Bailey, Borwein, López de Prado & Zhu 2014]. `TrialRegistry` counts the trials the harness
*ran*. An LLM researcher does not begin its search at zero. It arrives having, in a real sense,
already searched: its priors encode which lead-lag relationships people have found, which parameter
neighbourhoods are conventional, which regimes are worth excluding. A model that "already knows the
answer" converges in three logged trials where an uninformed searcher would have taken three hundred —
**and logs `N = 3`.**

The registry then reports a denominator that omits the search that actually did the selecting. DSR and
PBO are computed against it and are, to that extent, optimistic. This is Appendix B #2 ("trial counts
are lost") in a form the Charter never contemplated (F2), and it is a **larger** problem than the
holdout question, because:

- it contaminates the **in-sample** period, not just `[C, G]`;
- it is **invariant to where `C` is placed** — no cutoff pin touches it;
- and it is not fixable by waiting, since it is a property of the researcher, not of the calendar.

I raise it here because it is the honest consequence of the Principal's own observation, and because
it changes what the firm should do about that observation. If model priors are a real leak, the
proportionate response is to **fix the denominator**, not to move the cutoff. §3.4 specifies how, using
an existing Charter constant.

---

## 3. RULING

### 3.1 Verdict

> **REJECT the proposed derivation rule. ADOPT the threat model that motivates it, in full, with
> consequences specified in §3.3–§3.5.**
>
> `C` shall **not** be derived from any model's training cutoff. `C` remains what Ruling 001 §3.2
> made it: an immutable calendar date pinned at pre-registration, chosen by the Principal as a
> scheduling matter, and audited mechanically as `max(event_time) ≤ C`.

Ruling 001 D2's ingest ceiling is unaffected and is not reopened.

### 3.2 What I am adopting, and it is not nothing

The Principal's observation is correct, it is new, and the Charter does not contain it (F2). Stated in
my terms: **for an LLM researcher, "the holdout was not fetched" no longer implies "the holdout did not
inform the design."** Ruling 001 §2.4 called a historical holdout "procedurally protected only." That
was too generous and I am correcting my own language:

> **Amendment to Ruling 001 §2.4.** A historical holdout is procedurally protected against K1 and K2.
> Against K4 it is **not protected at all, and cannot be** — there is no procedure to comply with and
> no artifact to audit. The phrase "procedurally protected only" must not be read as implying that
> some procedure covers the model-prior channel. None does.

That is a genuine weakening of the firm's position, produced by his argument, entered on the record
against my own prior text.

### 3.3 Why the derivation rule is rejected — three independently sufficient reasons

**(1) The option does not occupy a distinct region of the timeline. It is option B minus two months of
in-sample, plus an unverifiable parameter.**

This is decisive on arithmetic alone and I want it seen before any argument about epistemics.

A training cutoff is in the past by construction, so a cutoff-derived `C` is always `≤` today. The only
cutoff this firm can source is May 2026 (F3). Take it at face value and set `C = 2026-05-31`:

- `[C, today]` is **two months**. §4.4 requires a holdout `≥ 12 months`. **The proposal does not give
  the firm a usable holdout today.** It is not a middle option between "have a holdout now" and "wait."
- To reach 12 months of holdout, `G ≥ 2027-05-31`. Option B (`C =` today) reaches it at `G ≥ 2027-07-28`.
  **The proposal buys approximately two months.** [inferred from one measured cutoff]
- Its in-sample is `[start, 2026-05-31]` — **two months shorter than option B's**. For a family whose
  binding risk is evidentiary length (I-004 [measured]), that is a cost in the exact currency the family
  is short of.
- And option B closes K4 **completely and verifiably**, where the proposal closes it partly and
  unverifiably.

So on every axis — holdout quality, in-sample length, auditability — the proposal is weakly dominated
by option B, in exchange for two months. **If the Principal is worried about memorization, option B
already solves his problem, better, at a cost he can verify.** A control that is a strictly weaker
version of one already on the table is not a third option; it is a discount on a control the firm
should not be discounting.

**(2) The control's parameter cannot be sourced, and the firm's own standard forbids that.**

I-009 [measured] records that the cutoffs are unknown and that the authoritative reference does not
publish them. A control whose parameter is unsourceable is not a control; it is a number with a story
attached.

Sharpen it: even a *published* cutoff would be a **vendor claim about its own product, unverifiable by
this firm and not falsifiable by any experiment we can run.** The firm already has a rule for that
class of input. Amendment A4 [cited — Charter §4.6] makes a vendor's pre-adjusted price series
**inadmissible** — not discounted, inadmissible — precisely because the transformation cannot be
verified. A vendor's assertion about the contents of its own training corpus is *further* from
verifiable than a pre-adjusted price series, not closer. Admitting it as the parameter of the firm's
most-protected control while rejecting adjusted closes would be an incoherence I am not prepared to
sign.

And per the standard the CIO wrote into I-009 and which I endorse: an unverifiable control that feels
rigorous is worse than a known-weak one, because it stops people looking. A Validation Report reading
"holdout placed beyond the researchers' knowledge cutoff" would be read as a strong claim. It would be
an [assumed] claim wearing a [measured] costume. Appendix B #4 [cited] — thresholds drifting for
defensible-sounding reasons — begins with sentences exactly like that one.

**(3) The rule's own logic, applied consistently, returns `C =` today — so it is either inconsistent or
redundant.**

The rule is "pin `C` beyond the knowledge of every party that could shape the design." The Principal
shapes the design: he supplied this family (D-004 [measured]) and, per I-002 [measured], he has already
searched its history with five tuned parameters and one regime exclusion. His knowledge cutoff is
wall-clock-now, always, and it advances continuously.

So the max over participants is **today**. That is option B.

A cutoff-derived `C` therefore either (a) applies a max-over-participants rule while silently excluding
the participant with the latest cutoff — inconsistent — or (b) resolves to today and is redundant. I can
construct no third reading. Note the direction of this argument: it is not a rhetorical point about the
Principal. It is that **K5 is documented where K4 is hypothesised** (I-002 is a measured fact; weight
contents are not), so a threat model that takes K4 seriously and omits K5 has its priorities inverted.

### 3.4 What replaces it — four requirements, binding

These are Seat 3 standards under my ownership of admissibility and of what counts as point-in-time
correct. None is a Charter amendment; none moves a Charter constant. Where I use a constant, it is one
that already exists.

**R1 — Holdout classification is a required field, with the model-prior channel named.**
Ruling 001 §2.4 already requires every Validation Report to state whether the holdout is unseeable or
historical. Extended: the pre-registration **and** the Validation Report must classify the holdout as
**FORWARD** (window postdates the pre-registration wall-clock; closes K1–K5 for that sub-window) or
**HISTORICAL** (window predates it), and a HISTORICAL classification must carry this sentence on the
face of the report, not in an appendix:

> *This holdout is historical. It establishes that the window was not searched over through the
> harness. It does not establish that the window was unknown to the researchers, and no control in this
> firm can establish that.*

A report that omits it is defective and I will return it.

**R2 — Mixed windows are decomposed, never averaged.**
Where `[C, G]` straddles the pre-registration wall-clock, the forward and historical sub-windows are
reported **separately**, with their own observation counts. The forward sub-window is the only part
that carries the S3 guarantee, and a blended Sharpe over a 2-month forward and 10-month historical
window is a number whose strongest component has been diluted by its weakest. *(This clause exists
because the Principal's option produces exactly such a window. Rejecting the option does not make the
case disappear — any `C` pinned before today produces it.)*

**R3 — A HISTORICAL holdout requires a pre-registered forward-window falsifier.**
This is the substitute for the property the historical holdout cannot deliver, and it lands within an
existing Gate 0 criterion (§4.3(2), pre-registered falsifier [cited]) rather than inventing one. Any
family pre-registering a HISTORICAL holdout must, at Gate 0, name:

- a forward observation window (start = pre-registration date, minimum length stated);
- a **specific numeric kill condition** on that window — not a mood, a number;
- and the sponsor's written acceptance that the condition is binding.

This costs no calendar time: the window accrues while the family is researched and, if it passes,
paper-traded. It gives the firm the one thing a historical holdout structurally cannot — a claim about
data that did not exist when the claim was made. **This is the modification I would want adopted if
the Principal chooses a historical `C` for schedule reasons.**

**R4 — Model-prior provenance is recorded, and the published-signal haircut is presumptive.**
Two parts.

*(a) Provenance.* The pre-registration records which seats originated or ratified each binding design
field, with each seat's model and its stated cutoff **where published, labelled [assumed] where not**.
This is cheap, it takes the derivation rule's one good instinct — that the record should exist — and
keeps it without pretending the number is verified. If cutoffs are ever published, the record becomes
retrospectively auditable. If they never are, the field reads `unknown` and that itself is the finding.

*(b) The haircut, which is where the teeth are.* §4.6 [cited] already imposes
`PUBLISHED_SIGNAL_HAIRCUT = 0.50` on any edge derived from published research, on the documented base
rates of ~26% out-of-sample and ~58% post-publication decay [cited — McLean & Pontiff 2016]. I rule:

> **A hypothesis generated from an LLM seat's priors is presumptively an edge derived from published
> research, and carries the 50% haircut, unless the sponsor argues at Gate 0 that the mechanism is not
> publicly documented and Validation accepts the argument.**

This is not a new threshold — it is an existing constant applied to a case the Charter did not
anticipate but whose logic it plainly covers. If a model proposes a lead-lag effect because that
effect is well described in its corpus, the effect *is* published research, arriving by a different
delivery mechanism, and McLean & Pontiff's decay applies to it for exactly the reasons it applies to
anything else. §2.3's `N`-deflation is the same problem seen from the denominator side; the haircut is
the instrument the Charter already gives me for it. It bites **today**, on the in-sample period, at no
schedule cost — which is more than the rejected proposal offers.

*Forward notice, not a decision:* whether the forward-lag family's mechanism is publicly documented is
a per-family Gate 0 determination and I will make it at intake, on the sponsor's argument. I am not
prejudging it here.

### 3.5 The companion control on K3 — specified, with its limits stated

Challenge 2 asks whether the retrieval hole sinks the proposal or merely requires a companion. My
answer is in §3.3 and it is neither: **the proposal is sunk by (1)–(3), independently of K3.** But K3
is real (F1), it is larger than K4, and it deserves a control on its own account. Specified here so it
does not go missing when the proposal does:

**The primary control on K3 already exists and needs only to be enforced: pre-registration freezes
binding design fields.** Retrieval is dangerous because it can *change a design choice*. Once the spec
is sealed, the binding fields cannot change without a Validation-reviewed amendment (Ruling 001 §3.4).
So the exposure is not "the whole research period" — it is **everything up to sealing**. That is where
the firm should spend its attention, and it argues for pre-registrations that are *complete*, not
skeletal, since every field left unspecified at sealing is a field a later retrieval can still move.

**Secondary, and I recommend rather than mandate it:** external research on mechanism, venue, and
resolution rules happens **before** sealing and is recorded in the pre-registration. Work dispatched
after sealing should go to seats without `WebSearch`/`WebFetch`. F1 shows the grant is per-seat and
already differentiated.

**Its limit, stated plainly because an overstated control is worse than none** (Ruling 001 §2.3 D3):
all nine seats hold `Bash`, so `curl` defeats a tool-grant reduction entirely. This is a **default-path
control, not a barrier** — the same class as the ingest ceiling, and justified by the same principle
from Ruling 001 §2.2: *the safe path must be the default path.* It converts retrieval from an available
convenience into a deliberate act. It does not prevent one, and no document may claim it does.

---

## 4. The four challenges, answered

### 4.1 Which cutoff binds?

**Moot as a derivation rule, since I have rejected derivation. Answered anyway, because the sub-question
about design influence has consequences that survive the rejection.**

Had the rule been adopted, the binding quantity would be the **maximum over every party that originates
or ratifies a binding design field** — and that set includes the Principal, whose cutoff is today
(§3.3(3)). The rule collapses.

**"Does a seat that never sees the data still contaminate the family by influencing design?"**
**Yes. Emphatically, and this is the part worth keeping.** Contamination is a property of *choices*, not
of data access. A seat that reads a memo and says "narrow the universe to contracts resolving within 30
days" has made a design choice, and if its priors encode why that window worked in the holdout period,
the choice is contaminated — with no fetch, no ingest, no artifact. This is precisely why K4 is
undetectable in principle, and it is the strongest thing in the Principal's argument.

**But the set must be bounded or the rule becomes unenforceable, and unenforceable rules teach seats to
ignore rules** (Appendix B #4 [cited]). I bound it:

> The **contaminating set** is the seats that originate or ratify a **binding design field** —
> hypothesis statement, universe, horizon, rebalance frequency, features, parameters, exclusions,
> falsifier, cost assumptions. The CRO setting a position limit, or Ops reconciling a blotter, is
> **not** in the set: those choices do not shape the signal. Membership is recorded under R4(a).

### 4.2 Does the retrieval hole sink the proposal?

**It does not sink it — reasons (1)–(3) already did, and I want the record to be precise about which
argument carries which weight.** But it does establish two things that matter more than the verdict:

*Why K3 is not fatal in the way the dispatch suggests.* A control is not obliged to close every
channel. Ruling 001 §2.3 D3 already settled this for the passphrase: its job is
authorization-and-sealing, not prevention, and that is what may be claimed for it. A memorization
control with a retrieval hole is not thereby invalid. It is thereby **narrow**, and the requirement is
that nobody claim otherwise.

*Why K3 nevertheless guts the proposal's value at the margin.* Retrieval strictly dominates
memorization as an attack: higher fidelity (actual prices, not recollection), targeted (the seat asks
the exact question), and **available for any window regardless of where `C` sits**. Closing the
second-easiest door while the easiest stands open moves total risk by approximately nothing, because
the careless seat — and carelessness, not intent, is the realistic case — routes through the open one.

And the priority is inverted in a way that is actionable: **K3 is partially controllable with a control
the firm can implement today** (tool grants, F1; pre-registration completeness, §3.5). **K4 is not
controllable at all short of a forward holdout.** The firm is being asked to spend its attention on an
unenforceable control against the smaller channel while an enforceable one against the larger channel
sits unbuilt. **Companion, not casualty — but the companion is the more valuable half, and it should
be built whether or not `C` moves.**

### 4.3 Is a training cutoff a real boundary?

**No, and this is the challenge I find most damaging to the instrument on its own terms** — more so
than the CIO's framing suggests, because the failure runs in both directions.

*Forward:* knowledge does not stop at a date. Post-cutoff information enters a model through
in-context material, through the user, through any retrieved document (K3). "After the cutoff" is not
"unknown."

*Backward — the direction usually missed:* coverage of the months immediately **preceding** a cutoff is
typically thin relative to well-documented earlier periods, because the corpus describing a period
keeps accumulating for years afterwards. So `cutoff − ε` is not reliably *known* either. A cutoff is
not a step function in knowledge; it is a soft, non-monotone boundary on a quantity the firm cannot
measure. Pinning a hard control parameter to it is pinning to noise.

**And the leak object is wrong.** For hypothesis *generation*, the dangerous cargo is not memorized
price levels — those are hard to recall precisely and rarely needed. It is **regime knowledge**:
"prediction-market forwards lagged spot during the 2025 drawdown," "funding inverted in Q1." Regime
knowledge survives complete price-memorization failure, and it is worse, because it tells the
researcher **which regime to condition on and which period to exclude.**

The firm has an instance of this failure mode already on the books: I-002 [measured] records the prior
forward-lag work as carrying **one regime exclusion**. That is exactly the artifact this channel
produces. I-002 correctly rules that the prior work carries zero evidentiary weight for `N` — but
declaring `N = 0` does not un-know a regime. **The contamination survives the accounting.**

A date-pin addresses price memorization, which is the benign half, and addresses regime knowledge only
weakly and non-monotonically. **It does not address the thing that actually leaks.** This alone would
make me reject the instrument even if the cutoffs were published and verified.

### 4.4 Verifiability

**Split the question, because conflating the two halves is what makes the proposal look auditable.**

**The mechanism stays auditable.** `max(event_time) ≤ C` is checkable by anyone against `pit.db`,
whatever `C` is and however it was chosen. Ruling 001 D2's ceiling is unaffected. Nothing in the
proposal breaks the boundary audit, and I want that stated so nobody reads this ruling as reopening D2.

**The derivation is not auditable, and the *claim* is not auditable.** Nobody outside the vendor can
check that `C` was correctly derived; nobody at all can check the claim the derivation is meant to
support. The firm would hold a mechanically auditable enforcement of an unauditable assertion — and
that combination is more dangerous than a known-weak control, because the green check on the mechanism
gets read as validation of the claim.

Contrast option B, which is verifiable **without trusting anybody**: on 2026-07-28, the price of
2027-03-15 does not exist. That is checkable by calendar. It requires no vendor disclosure, no seat's
honesty, and no assumption about weights. It is the only control in this firm's entire holdout design
whose guarantee is physical rather than procedural, and it is the reason it dominates.

---

## 5. Required independence statement

**I reached the ruling independently, and I disagree with the Principal on the operative question.**

**What I rejected:** his proposal, as stated — the derivation rule, which was the whole of what he
proposed. This is not a partial rejection or a friendly amendment. `C` will not be derived from a
training cutoff.

**What I adopted, and why it is not deference:** the threat model. K4 is real, the Charter is silent on
it (F2), and it is a genuine addition to the firm's model. I went further than agreeing with it — I
**amended my own prior text against myself** (§3.2), retracting "procedurally protected only" as too
generous. I do not adopt his conclusion; I adopt his premise and then find that his premise, taken
seriously, argues against his instrument.

**What drove the agreement on the premise, other than that he holds it.** Four things, none of which
appear in his proposal or in the dispatch:

1. **F1**, which I gathered in this session, and which cuts *against* his instrument — it establishes
   that the channel he did not address is larger than the one he did.
2. **K5 and §3.3(3)** — that his own max-over-participants logic includes him and collapses to option
   B. This is mine and it is the reason the rule is internally inconsistent.
3. **§2.3, `N`-deflation** — that his observation, followed one step further, indicts the denominator
   rather than the cutoff, which is a bigger problem and a differently-shaped one.
4. **I-002's regime exclusion** (§4.3) — the firm already has a *measured* instance of the leak he is
   theorising about, arriving through the human channel he omitted. His hypothesised channel is
   unfalsifiable by us; the documented one is not.

**The honest epistemic position, which is why I could not have adopted his instrument even sympathetically.**
His claim — that memorized history leaks into hypothesis generation — is, for this firm, **untestable as
stated**. We cannot inspect weights or audit a corpus. I am accepting it as a plausible mechanism,
labelled **[assumed]**, not as a finding. Building the firm's most-protected control on an [assumed]
mechanism with an unsourceable parameter is precisely what house rule 6 exists to prevent. If I had
adopted it, I would have been importing an unlabelled assumption into the vault — from the seat whose
job is to catch that. §7 specifies a cheap experiment that would move it from [assumed] toward
[measured], because an untestable premise should be made testable rather than merely deferred to.

**On the pattern the dispatch flags.** The dispatch is right that agreeing twice consecutively is the
Appendix B #1 signature, and right that manufactured dissent is equally corrosive. My record on
discrete Principal positions now reads:

| Ruling | Position | Outcome |
|---|---|---|
| 001 §3.2 | `C` pinned at pre-registration | **Agreed**, on reasoning he did not supply |
| 001 §3.4 | Sealed spec pins exact source and query | **Rejected** — ruled semantic identity, not transport |
| 002 §3.2 | A historical holdout is weak against an LLM researcher | **Agreed**, and extended against my own prior text |
| 002 §3.1 | Therefore pin `C` at training cutoffs | **Rejected** |

Two of four rejected. `n = 4` is still statistically uninformative and I-003 [measured] remains
correct that no base rate exists. I record it so the count is built as it happens rather than
reconstructed later. **The disagreement here is not decorative:** it removes the option the Principal
proposed and it does so on arithmetic (§3.3(1)) that anyone can check in thirty seconds.

**The thing that would most embarrass me,** and which I want stated so it can be checked later: if a
future reader finds that I rejected the instrument while adopting enough of the surrounding argument
that the Principal got what he wanted anyway, that reading is available and I have tried to foreclose
it. R1–R4 are not his proposal in softer clothing. R4(b) in particular imposes a cost — a 50% haircut
on in-sample edge — on the flagship family he sponsored, today, which his proposal did not.

---

## 6. Decision table for the Principal

The `C`-placement decision is yours. Dates assume today = 2026-07-28 and §4.4's 12-month holdout floor.

| | **A · `C` early (holdout usable today)** | **B · `C` = today (forward holdout)** | **C · `C` at training cutoff (proposed)** | **D · B plus exploratory start** |
|---|---|---|---|---|
| **`C`** | ≈ 2025-07-28 | 2026-07-28 | ≈ 2026-05-31 [assumed — only sourceable cutoff, F3] | 2026-07-28 |
| **Earliest Gate 1** | **Now** | ≈ 2027-07-28 | ≈ 2027-05-31 | ≈ 2027-07-28 (research runs now) |
| **In-sample length** | **Shortest** — loses 12 months off the constraint I-004 says is already binding | **Longest** | 2 months shorter than B | Longest |
| **Closes K1 ingest** | Yes | Yes | Yes | Yes |
| **Closes K2 direct fetch** | No | **Yes** | No | **Yes** |
| **Closes K3 retrieval** | No | **Yes** | No | **Yes** |
| **Closes K4 model priors** | No | **Yes** | Partly, unverifiably | **Yes** |
| **Closes K5 Principal** | No | **Yes** | No | **Yes** |
| **Boundary auditable (`max(event_time) ≤ C`)** | Yes | Yes | Yes | Yes |
| **Claim auditable** | No — "unseen" unprovable | **Yes — by calendar, trusting nobody** | **No — vendor assertion, unsourced** | **Yes** |
| **Classification (R1)** | HISTORICAL | FORWARD | MIXED → decompose (R2) | FORWARD |
| **Requires forward falsifier (R3)** | **Yes** | No | Yes, for the historical part | No |
| **What the Gate-1 report can claim** | "Not searched through the harness." Nothing about unseen | **"Could not have been known by anyone"** | "Not searched; possibly not memorized" — the weakest sentence on this table | **Strongest, with N accrued honestly** |
| **Sprint 1 yields a Gate-1 verdict** | Yes | No | No | No — but yields a pre-registration, a measured data spec, and logged trials |

**Reading the table.** Option C is dominated by option B on every row except a two-month schedule gain,
and it is the only option that produces an unauditable claim. **It is not a middle path between A and B
— it delivers no usable holdout today (2 months, §3.3(1)), so it does not solve the problem A solves,
and it solves B's problem worse than B does.**

The live choice is **A versus B/D**, and it is a scheduling call, not a methodological one. The
methodological facts you should hold while making it:

- **A shortens the in-sample by 12 months, and I-004 [measured] says in-sample length is this family's
  most likely cause of death.** A buys a holdout that protects against K1 only, at the price of the
  constraint most likely to fail. For the forward-lag family specifically, that is a poor trade and I
  will say so in the Gate-1 report if A is chosen.
- **D is A's schedule with B's guarantee**, at the cost of the *label*: the family is researched now
  under `ADMITTED-AS-EXPLORATORY` (§4.3 [cited], which exists for exactly this), trials accrue honestly
  in the registry, the data spec gets measured, and the Gate-1 claim is made when the forward holdout
  matures. **What you give up under D is the ability to say "validated" in 2026. What you get is that
  the word means something when you do say it.**

---

## 7. What would change my mind

Falsifiers, per house rule 2 — each a specific observable, not a mood.

**On rejecting the derivation rule (§3.3).**

- Reason (1) is arithmetic and cannot be argued away; it can only be *changed*, by a cutoff later than
  the one in F3. **If the max sourceable cutoff across the contaminating set were established at a date
  materially later than May 2026** — say, within four weeks of today — the two-month gap would collapse
  to near zero and reason (1) would go quiet. Reasons (2) and (3) would still stand and I would still
  reject, but the ruling would be weaker and I would say so.
- **If Anthropic published verifiable, per-model training cutoffs**, reason (2) weakens from
  "unsourceable" to "vendor-asserted." That is an improvement but not a sufficient one: A4's logic
  [cited] still bars unverifiable vendor transformations, and §4.3's argument — that a cutoff is not a
  real knowledge boundary and does not bound the leaking object — is untouched by publication. **I
  would not reverse on publication alone.**
- I would **not** change my mind on any argument that the seats can be trusted not to retrieve, or that
  a model's priors are probably weak. Trustworthiness is not a control (Ruling 001 §7) and "probably
  weak" is [assumed] doing the work of [measured].

**On adopting the threat model (§3.2) — the cheap experiment that should be run.**

K4 is currently [assumed] and I dislike that. It is partially testable for **≈ one Sonnet unit**:

> **Probe.** In an isolated seat that will never touch the family, ask for a description of a named
> instrument's behaviour over a named historical window — level, direction, volatility regime, notable
> dislocations — with no retrieval permitted. Compare against the realized series once ingested.

Interpretation is asymmetric and I pre-commit to it now, before the result exists:

- **A strong hit is strong evidence for K4.** If a seat can describe the window accurately with no
  fetch, the channel is real and measured, and I would tighten R1's required sentence and revisit
  whether HISTORICAL holdouts should be capped at `ADMITTED-AS-EXPLORATORY` — a step I have **not**
  taken in this ruling because the evidence does not currently support it.
- **A miss is weak evidence against.** Elicitation failure is not absence of knowledge: the model may
  hold the regime without the prices (§4.3), or hold it without stating it. **A negative result does
  not license relaxing R1–R4**, and I am recording that in advance so it cannot be used that way later.
- The probe must run in a seat isolated from the family, or the probe *is* the leak.

**On R4(b), the presumptive haircut.**

- It is rebuttable at Gate 0 on a sponsor's argument that the mechanism is not publicly documented. I
  will hear that argument on the forward-lag family at intake and have not prejudged it.
- I will move the presumption on a reasoned argument from the Devil's Advocate or the Director of
  Research **before** a family's Gate 0. I will not move it after, and never on the basis of what the
  haircut does to a result. That asymmetry is deliberate and it is the point.
- `PUBLISHED_SIGNAL_HAIRCUT = 0.50` is a Charter constant [cited — §4.2] and is not mine to move at
  all. Only the Principal, in writing, in advance.

**On R3, the forward falsifier.**

- If the Principal amends §4.4 in writing, *in advance*, to define the holdout as a fixed-length forward
  window from pre-registration rather than a fraction of the series, R3 becomes redundant and I would
  withdraw it. That is a coherent alternative design and it is his to make — but it is a Charter
  amendment made before an evaluation, never an in-flight adjustment.
- A cross-sectional (instrument-held-out) design was considered and is **not** recommended: it does not
  protect against regime-common contamination, which §4.3 argues is the dominant channel here, and
  §4.2's `HOLDOUT_FRACTION` [cited] specifies a temporal holdout regardless.

---

## 8. Consequences for the log

Inputs to the CRO, who owns the Issue Log; not edits I have made.

- **I-009** — resolved *in ruling*, with its severity **retained**: the cutoffs remain unknown, and the
  ruling's effect is that the firm no longer needs them. The pattern tag
  `unverifiable-control-parameter` should stay live as a class, since R4(a) will keep recording
  `unknown`.
- **New entry requested, MEDIUM, owner fable-5-cio:** the K3 retrieval channel (F1 — eight of nine
  seats hold `WebSearch`/`WebFetch`; all nine hold `Bash`). Open, uncontrolled, larger than the channel
  the ruling was convened to discuss. Companion control specified in §3.5. Pattern tag
  `uncontrolled-information-channel`.
- **New entry requested, HIGH, owner quant-validation:** `N`-deflation by model priors (§2.3). The
  registry's denominator omits the search embedded in the researcher. Mitigated in part by R4(b);
  **not** solved by it. Pattern tag `denominator-understated-structurally`.
- **Ruling 001 §2.4 amended** per §3.2 above.

---

*Head of Quantitative Validation · Castellan Capital · 2026-07-28*
*Binding on Seats 1, 2, 6–10. Appealable only to the Principal, in writing.*
