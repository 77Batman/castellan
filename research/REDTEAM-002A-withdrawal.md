# RED-TEAM MEMO 002A — WITHDRAWAL OF THE `DO NOT SEAL` VERDICT

**Devil's Advocate · Castellan Capital · 2026-08-25 · dispatch S4-D-005**
**Subject: `funding-carry-conditioning-002`, revision R-008 · Supersedes `REDTEAM-002` §10 row 1 only.**

---

# **WITHDRAWN.**

**`REDTEAM-002`'s `DO NOT SEAL` verdict is withdrawn. From this seat, nothing blocks the seal.**

The condition was stated in `REDTEAM-002` §9 row 1 and §12 item 1, in these words: *"`k`, `d` and `band`
carrying numeric literals in a binding field, and the two `[2020-01-01, C]` sites conformed. **Nothing
else.**"* **It has been met — verified against the sealed strings, not against the sponsor's account of
them.** I withdraw on the day the repair landed, as I said I would.

**I found two new defects while verifying it. Neither blocks, and §1.3 states why not, at length,
because that reasoning is the only thing standing between this seat's conditions and worthlessness.**

---

## 0. LINE BUDGET AND THE COMPARATOR — stated before writing, per Standing Order 003 §2.2

**Comparator ACCEPTED, with one reservation stated rather than used as licence.**
`DATA-VERIFY-002` (79) and `VALIDATION-ACCEPTANCE-001` (492) are the right bracket: measure named
conditions, issue a verdict, do not adjudicate. **The reservation:** both comparators verify conditions
authored elsewhere and return clean or unclean. This artifact verified conditions and, in verifying
them, produced two original findings (§3.1, §3.2) that neither comparator's shape required. That is
roughly 70 lines the bracket does not price.

**Projection: ~320 lines.** Comparator midpoint ~300, plus the two findings. **Well under the ~800
ratchet, and 1.07× the CIO's figure rather than 2×.**

---

## 1. THE VERIFICATION — what I read, and what it says

### 1.1 DA(1) is met on the letter · [measured — the sealed strings at `PREREG-002` §21]

DA(1) required each of `k`, `d`, `band` to appear **as a numeric literal inside a binding field** at the
instant `open_hypothesis` is called. `statement`, `horizon` and `universe` are three of the sixteen
fields hashed into `prereg_sha256` [measured — `registry.py:82` `_BINDING_FIELDS`, via the payload §1].

| Literal | Binding field | Line | Singly bound? |
|---|---|---:|---|
| `k = 0.5` | `statement` | 2099 | **Yes** — the only assignment to `k` in any field |
| `d = 1.0` | `statement` | 2099 | **Yes** |
| `band = 0.10` | `statement` 2099 **and** `horizon` 2609 | 2099 / 2609 | **Yes — two sites, one value, no divergence** |
| `lookback = 30`, `w_max = 1.0` | `statement` | 2100 | already bound pre-R-008 |

**The apparent second `k`, checked because the dispatch told me to verify rather than take on report.**
The sealed text reads `w reaches 0 at z = d + 1/k = 3.0`. At `k = 0.5`, `1/k = 2.0` and `d + 1/k = 3.0`.
**The document's arithmetic is correct.** The dispatch's restatement of the CIO's verification —
*"an apparent second `k = 3.0` is `1/k = 3.0`"* — **is not**: `1/k` is 2.0, and the 3.0 is the sum.
Filed **I-245**, LOW, because a verification passed down in garbled form is how the next seat that
trusts the summary instead of the string gets it wrong.

**Not a defect: `w_max`.** `statement` writes the rule as `clip(..., 0, 1.0)` and separately binds
`w_max = 1.0`. Same value, no ambiguity.

### 1.2 The two `[2020-01-01, C]` sites are conformed · [measured]

| Field | Now reads | Line |
|---|---|---:|
| `statement` | *"over 2020-01-01 to **THE LAST SETTLED COMMON BAR OF THE PRIMARY UNIVERSE AT THE FIRST RUN**"* | 2089 |
| `falsifier` | *"over the full in-sample [2020-01-01, **THE LAST SETTLED COMMON BAR …**]"* | 2242 |

**Both carry my wording verbatim, both carry the R43 note that `C` is not redefined, and R-008 adds
zero new dated sites** [verified — no ISO date and no `C`-form expression in either replacement].
I-213's cause, not its instances, is closed: `C` now denotes one object.

**The third instance at `universe` line 2358.** It is a binding field, and it does assert
*"common span 2020-01-01 to C = 6.571 years"* — a figure the same field then supersedes in-line with
6.612 / 6.609. **It is a superseded span measurement, not a computation window any seat runs, and the
correction travels inside the frozen string.** My remedy named two sites; this is the third; the
sponsor named it and filed I-221 rather than quietly touching it. **I do not block on it and I do not
re-file it** — re-filing an issue the sponsor filed against itself is how this seat becomes ceremonial.

### 1.3 The pre-output guarantee is verifiable, and it is the whole of why the repair is worth anything

`book/registry.db` reads **0 hypotheses / 0 trials / 3 events** [measured, read-only `SELECT COUNT(*)`,
this session]. **No backtest has ever run in this firm. No output exists on this family that a
parameter could have been fitted to.** That is not a claim about the Director's discipline; it is a
property of a file anyone can read.

**`harness/scripts/evaluate_dated_clauses.py` does not exist** [measured — `find . -name`, and
`harness/scripts/` holds five Polymarket/snapshot scripts and nothing else]. DA(3)'s premise stands.

**The data-discipline disclosure at I-223 is an unverifiable negative and I accept it on two grounds
rather than on trust.** First, the *shape* of the three derivations is consistent with it: none of the
three literals is a quantile, a moment, a count, or a threshold on `z(t)`. Second, the sponsor
volunteered the two in-sample figures it did use (11.86% / 14.07%, and the ~35% floor share) and named
the second as used **only to reject** an argument. **A seat concealing a look does not hand you the
list.** The exposure is real and the remedy the sponsor offered — re-derive `band` from an assumed
carry floor — is now moot for a different reason (§3.1).

---

## 2. THE FOUR QUESTIONS

### 2.1 · Is `d = 1.0` a parameter or a choice dressed as a derivation?

> **It is a choice, correctly and repeatedly labelled as a choice — inside a derivation that
> understates its own safety margin by a factor of 5.5.**

**The derivation is arithmetically correct and answers the wrong question.** `μ̂` over 30 days carries
SE `σ/√30 = 0.183σ`, so *conditional on day `t` sitting exactly at the true baseline*, `z(t)` has
dispersion 0.183. True. But the quantity a deadband on `z` must clear is **`z`'s own null dispersion**,
and day `t`'s value is itself a draw. The trailing window ends **strictly before** the day screened
[sealed — `horizon`], so under an iid null:

```
Var(x_t − μ̂) = σ²(1 + 1/30)   ⇒   sd(z | null) ≈ 1.017
```

**`d = 1.0` is ~1.0 null standard deviations, not ~5.5.** [inferred — estimator arithmetic on n = 30;
no market data touched, no `pit.db` query, consistent with the ordering I named.]

**The consequence is that the document's own rejection criterion reaches its own selection.** §14.2
rejects `d = 0.2` at *"~1.1 [SE] — the rule fires on the sampling error of its own 30-day mean."* At the
null dispersion of the statistic actually being thresholded, **`d = 1.0` sits at 0.98** — the same
position on the scale, in different units. Under a normal reference the rule would fire on ~16% of days
with no crowding present at all.

**And the bracket does not pick 1.0 even on the document's own terms.** If the only noise to filter is
the reference level's 0.183, three to four SE is 0.55–0.73; five and a half is over-filtering. The
document says the bracket is `O(1)` and the point inside it is judgment. **That is honest and it is
also the whole content of the derivation.**

**Now the question as the CIO put it: is 1.0 a decision taken where it is visible, or a rounder number
in the same class as 3.0?**

> **It is a rounder number in the same class — and unlike 3.0 it arrives with its consequence published
> in a binding field, which is the entire difference and it is the one that matters.**

R41(c) puts `z > 1.5` on the face of the record, states the comparison pairs `(1.0, 0.5) → z > 0.75`
and `(0.25, 2.0) → z > 3.0`, and states plainly that the seat does not know whether the threshold is
met. **`d = 3.0` would have been a decision to make clause (b) fire taken where it is invisible. `d =
1.0` is a decision of unknown sign taken where it is visible.** Pre-registration does not require the
parameter to be right. It requires it to be fixed, pre-output, and legible. All three hold.

Filed **I-241, HIGH** — on the derivation, not on the seal.

### 2.2 · Does `z > 1.5` make clause (b) more or less likely to fire, and does it move my verdict?

**Less likely than the alternatives that would have looked worse, more likely than the alternatives
that would have looked better, and squarely in between. Nobody has measured it and nobody should have.**

Clause (b) kills on **fewer than 30** days with `z(t) > 1.5` in 187. Monotone in the threshold: the
count at `z > 1.5` lies between the count at `z > 0.75` and at `z > 3.0`. The selected pair is not at
either end of the range the sponsor itself published.

**Two directional facts, neither measured, both a priori:**

1. Under a normal reference, `P(z > 1.5) ≈ 6.7%`, giving ~12.5 days in 187 — **kill.**
2. The reference is known false. The series is censored with ~35% of prints at the administered floor
   [cited — `DATA-VERIFY-001` §5.2], and censoring **compresses `σ̂` in quiet windows**, which inflates
   `|z|` on any departure — **survival.**

**The two point opposite ways, which is precisely what the sponsor said, and I will not pretend to
resolve it from an armchair.**

**Does it move my verdict? No — and it sharpens my own kill condition rather than blunting it.** DA(2)
and clause (b) are now the same predicate on different windows, by design: I transcribed the sponsor's
threshold and window without alteration. **What has changed is that fact 2 above gives DA(2) a
confound**, and I record it at §3.2 and at **I-244** as a *reporting* obligation on DA(2)'s executor —
**not as a change to DA(2), which stands verbatim.**

### 2.3 · Does the inertness disclosure discharge the finding, or merely record it?

> **It discharges the concealment. It does not discharge the measurement. I accept the Principal's
> ruling as binding, I do not reopen it, and I state the residue precisely so that it freezes with the
> seal rather than being lost in it.**

**What the disclosure does, and it is more than I asked for.** Three binding fields — `mechanism`
(economic), `statement` (mechanical), `falsifier` (evidential) — now carry it, on R29(b)'s principle
that *a correction exists where the seal reads it and nowhere else.* The `falsifier` register goes
further than disclosure: it **narrows the claim under test** to *tail reduction on the approach to
crowding* and forbids any artifact from reading a leg (ii) result as tail protection in inversion.
**That is a sponsor giving up a reading it could have kept, in a hashed string, and I say so.**

**What it does not do.** The register governs how leg (ii) may be **read**. It changes nothing about
how leg (ii) is **computed**, and the computation is where the finding bites:

- Leg (ii) is the mean of `R_strat`'s 20 worst daily net returns against `R_bench_scaled`'s
  [sealed — `falsifier` 2284].
- On the ~25% of days in inversion, `w ≡ 1.0` and `R_strat ≡ R_bench`. But `R_bench_scaled = R_bench ×
  c` with `c = E[w] < 1`. **So on exactly those days `R_strat` is strictly larger in magnitude than the
  benchmark it is measured against — losses included.**
- The mechanism asserts the worst days *are* inversion days: inversion and basis loss are positively
  correlated (§3.3 risk 3).

**Compose them: leg (ii)'s 20 worst days are drawn preferentially from the regime where the exposure
match is guaranteed to run against the strategy.** A leg (ii) firing would then be a property of the
exposure-match construction and the inertness, not of the timing information the leg claims to test.
That is not a reason to keep the leg out of the seal — it is a reason that a leg (ii) **fire** must not
be reported as *"the conditioning's timing carries no tail information"* without the regime split.

**This is `REDTEAM-002` §2.3 / I-214 with its direction now identified**, and it is new: the disclosure
is what made the direction computable. Filed **I-243, MEDIUM.**

**My answer, unhedged: not sufficient as a discharge, sufficient as a disposition.** The rule is
disclosed, the claim is narrowed, and the residue is a named measurement defect in a falsifier leg the
sponsor has already ranked as the most likely killer. **I do not ask for a redesign and I would oppose
one now** — changing K2 in response to my argument is the post-hoc conditioning move §7.2 exists to
price, and it would cost more than the defect does.

### 2.4 · DA(1), DA(2), DA(3)

| Clause | Status |
|---|---|
| **DA(1)** — literals present at `C` | **MET.** §1.1. The three values are quoted verbatim above and must appear on the Gate 0 verdict addendum and every subsequent Validation Report, as the clause requires |
| **DA(2)** — dynamic range at `C + 30` | **STANDS AS WRITTEN. Not one word modified.** Threshold 30, window 187 days, in-sample maximum, **silence is a kill**. At a seal on 2026-08-25 the observation date is **2026-09-24** |
| **DA(3)** — evaluability at `C + 90` | **STANDS AS WRITTEN.** Its premise is verified live: **`harness/scripts/evaluate_dated_clauses.py` does not exist** [measured]. At a seal on 2026-08-25 the observation date is **2026-11-23**. SPEC-004's implementation being in flight is the *"the checker is coming"* answer the clause refuses in advance |

**I am adding no fourth clause.** The sponsor met my stated terms; a seat that responds by writing new
ones has taught the firm that meeting its terms buys nothing. **§3.1's remedy is the sponsor's own
written commitment coming due, not a new condition from me**, and I state the difference because it is
the only thing that keeps the two apart.

---

## 3. THE TWO NEW DEFECTS — found while verifying, blocking nothing

### 3.1 · **`band = 0.10` charges four sides for a one-sided trade, and the error is what avoided the sponsor's own declared escalation** · **HIGH**

The derivation [sealed — `horizon` 2609–2622; `DIR-RESTATE-001` §14.4]:

> *"**Only the perp leg moves** (spot notional is fixed at 1.0), so a rebalance of size `Δw` costs
> roughly `Δw × 24` bp round-trip."*

**The 24 bp is not a perp-leg cost.** `PREREG-002` line 1636, measured, in this document:
*"Per-side cost under the preset is **6.0 bps** … so a full **two-leg** round trip is **24 bps**."*
**24 = 4 sides × 6 bp — both legs, in and out.** A band rebalance is one trade on one leg: **6 bp per
side, 12 bp if charged as an eventual round trip.** The derivation over-charges by **2× to 4×**.

| Charge | `Δw ≤ 3.25 / charge` | Resulting `band` |
|---|---:|---:|
| 24 bp — as written, four sides | 0.135 | **0.10** |
| 12 bp — perp leg, round trip | **0.271** | ~0.25 |
| 6 bp — perp leg, one side | 0.542 | ~0.50 |

**Now read what the sponsor committed to, in the same section, one paragraph below the arithmetic:**

> *"**Had the cost arithmetic delivered `band` > 0.25**, the two survival conditions would have been in
> direct conflict and **this seat would have escalated the conflict rather than picked a side.** It did
> not, and the absence of the conflict is luck rather than design."*

**It is not luck. It is a leg-count error, and correcting it delivers `band = 0.27 > 0.25` — the
escalation trigger, met.** At `band > 0.25` the favourable post-hoc check inverts: the band **can** now
suppress a KC-002 clause-(b) day, because a target move of 0.26 would not execute and the notional
would not move.

**The direction is the one that matters.** `band` was to be derived from cost arithmetic **alone**,
precisely because §3.1 of my prior memo showed the two survival conditions pull it opposite ways. The
cost arithmetic carries a 2–4× error, and its direction eases the sponsor's own pre-registered expected
cause of death. **I allege no intent — this is a citation's leg count, and the sponsor disclosed the
check ordering honestly and unprompted. The consequence is nevertheless exactly the outcome the
discipline was built to prevent.**

**What I ask, and it is the sponsor's own procedure and not mine:** correct the leg count pre-seal —
one prose edit, zero trials, nothing sealed yet — and then either take the escalation it triggers, or
state on the record that the seat declines to and why. **I do not block on it.** Filed **I-240, HIGH.**

### 3.2 · **`σ̂` degeneracy under censoring, newly material because `1/k = 2.0` is now fixed** · **HIGH**

`z = (x_t − μ̂)/σ̂`, with `σ̂` the trailing 30-day standard deviation of a series in which ~35% of prints
sit **exactly** at the administered floor [cited — `DATA-VERIFY-001` §5.2]. In a window dominated by
floor prints, **`σ̂` collapses toward zero and `z` is unbounded on an arbitrarily small departure.**

**Why R-008 makes this quantitative for the first time.** Before the literals, `1/k` was a free symbol.
It is now **2.0** — the rule's entire dynamic range, full size to flat, spans two z-units. **In a
floor-collapsed window, two z-units can be a fraction of a basis point of funding. The sealed rule can
travel from `w = 1.0` to `w = 0` on a sub-bp move, in the calmest regime the sample contains.**

**What the document already says, and why it does not reach this.** `mechanism` concedes the moments
are **biased** — *"z(t) is a z-score of a censored variable and both moments are biased"* — and argues
the censoring *"argues for K1 rather than against it"* because funding departs from the floor only when
the premium escapes the clamp band, so a departure **is** a crowding event. **That argument is correct
and it is an argument about the event.** It says nothing about the **magnitude mapping**: the rule does
not merely detect a departure, it scales linearly in `z`, and `z`'s scale is set by `σ̂`. **Two
economically identical departures — same funding rate, same premium — produce different `w` according
to how boring the preceding thirty days were.** Bias is conceded; degeneracy is not, anywhere in
`PREREG-002` [verified — no variance floor, no winsorization, no `σ̂` guard in any field or section].

**Consequences, in order of how much they should move the reader:**

1. **The rule de-scales hardest in the quietest regime**, which is the inverse of the stated mechanism.
2. **Clause (b) and DA(2) both count `z > 1.5` days**, so both are partly counting `σ̂` collapses. A
   DA(2) survival is therefore **weak** evidence of the mechanism. Recorded at **I-244**.
3. **Leg (ii)'s *"when the size was reduced"*** is partly a functional of the denominator rather than
   the numerator.

Filed **I-242, HIGH.** **Not blocking**, for the reason at §4.

---

## 4. WHY NEITHER NEW DEFECT BLOCKS — the reasoning, stated at length on purpose

**A stated condition that is met and then not honoured is worth less than no condition at all.** If
this seat blocks on findings discovered *while verifying its own terms*, it has taught the firm that
satisfying the Devil's Advocate is unachievable, and the rational response to an unachievable condition
is to stop trying to meet it. **That failure mode is more expensive than either defect below.**

**And the two defects are not of the class my block was about.** `REDTEAM-002` §2.2's harm was named
precisely: the parameters would be *"chosen after the freeze, by whoever runs step 3, invisibly to
`prereg_sha256`."* **The harm was invisibility and post-hoc selection. It is cured, verifiably, by a
registry holding zero trials and three strings holding three numbers.** A parameter that is
poorly-derived, frozen, pre-output and publicly argued is exactly what pre-registration is for; a
well-derived parameter chosen after seeing the output is what it forbids. **This document now has the
first and not the second.**

**What I am not saying.** I am not saying the defects are small. I-240 is a 2–4× arithmetic error that
happens to sit on the parameter the sponsor declared could not be chosen from either survival
condition, and it defeats the sponsor's own escalation trigger. I-242 is a specification hazard that
becomes permanent under P7. **Both are cheap to fix today and impossible to fix tomorrow, and I have
said so in the strongest terms available to me short of a block.**

---

## 4A. **AN INCIDENT FOUND WHILE VERIFYING, AND IT IS ABOUT THE SEAL ITSELF** · **HIGH**

**This is not a red-team objection to the family. It is an operational finding, it is the most
decision-relevant thing in this memo today, and I found it because DA(3) required me to check the state
of `harness/`.**

**`open_hypothesis` — the seal — raises against the current working tree.**

```
castellan.registry.RegistryWriteNotGrantedError: No write grant is open.
'open_hypothesis' requires an open TrialRegistry.write_grant(reason=...)
with reason in ['REGISTER_HYPOTHESIS'].
```

**Five harness modules are modified and uncommitted**, all written **today at 18:24–18:25 UTC**, by
another seat, during this session [measured — `git diff --stat`, `stat`]:

| File | Δ lines | Bears on |
|---|---:|---|
| `registry.py` | **+555 / −** | **`open_hypothesis` — the seal**, `log_trial`, `_BINDING_FIELDS` |
| `holdout.py` | +133 | the vault seal, C8 |
| `gates.py` | +79 | `evaluate_gate1`, P7 |
| `data.py` · `engine.py` | +81 | PIT store, `run_backtest` |

**Three findings, in order of severity:**

1. **The suite does not pass: `110 failed, 144 passed, 68 errors`** [measured, run twice]. **This is
   not environmental** — the failures are `RegistryWriteNotGrantedError` from a new `_require_grant`
   gate whose callers in `harness/tests` have not been updated. `CLAUDE.md`'s standing rule is
   unambiguous: *"if the suite does not pass, stop and file an incident."* **I am filing it.**
2. **`write_grant` and `_require_grant` do not exist at HEAD** [measured — 0 occurrences in
   `git show HEAD:harness/castellan/registry.py`]. This is **SPEC-004's self-defence layer in flight**,
   which the dispatch itself told me. The harness is an **editable install**, so the **working tree is
   what executes**, not HEAD.
3. **`REGISTRATION-PAYLOAD-PREREG-002` §6's pre-execution checklist has six mechanical items and none
   of them is "open a write grant."** The payload states its purpose as making the seal *"mechanical,
   with nothing left to decide."* **Executed exactly as specified, against today's working tree, it
   raises.**

**What I checked and found clean, recorded so the absence is legible.** `_BINDING_FIELDS` is
**unchanged** — the same sixteen fields in the same order, `n_inherited` sixteenth [measured,
`registry.py:178–189`]. **My DA(1) verification at §1.1 therefore stands**, and the hash the payload
describes is the hash that would be computed.

**This does not block on my axis and I do not claim it does — my condition was the three literals and
the two sites, and it was met.** But the firm should not execute a seal against a harness whose suite
is 110-red and whose changes are uncommitted, and that is `CLAUDE.md`'s rule and not a new condition
from me. **Same posture as I-240: I hold seats to their own written rules rather than inventing new
ones.** Filed **I-247, HIGH**, to Data & Infrastructure, Validation and the CIO.

---

## 5. THE BASE RATE AND THE THROUGHPUT NUMBER — reported unprompted, as required

| Metric | Value | Reading |
|---|---|---|
| Gate 1 verdicts, any origin | **0** | Appendix B #1's metric remains **undefined at n = 0**. **No claim available and I make none.** |
| Gate 0 verdicts by origin | Principal: 1 ADMITTED-AS-EXPLORATORY · Director: 1 ADMITTED | Unchanged since `REDTEAM-002`. At n = 1 each, uninformative, and the Director's is the better verdict |
| Trials · backtests · verdicts · seals | **0 · 0 · 0 · 0** | Unchanged in Sprint 4 |
| Opus units by origin | Sprint 4 continues entirely on the Director-originated line | I-025's bias metric remains **inverted away** from the failure mode it was built to detect |

**The live failure mode is still Appendix B #9 and not #1, and one thing has changed:** the
pre-registration is, from this seat, **sealable**. Three sprints of compute have gone to the document
rather than to the hypothesis; the throughput number moves on the first logged trial and on nothing
else. **The firm should log its first trial in the same session as the seal, or state why not.** Filed
**I-246, LOW-MEDIUM**, to the CIO and the Principal — not re-filing I-219, which stands.

---

## 6. ISSUES FILED — I-240 THROUGH I-247

| # | Finding | Sev | Owner |
|---|---|---|---|
| **I-240** | **`band = 0.10`'s cost derivation charges 24 bp — four sides, both legs — for a rebalance the same sentence states moves only the perp leg.** Correct charge is 6 bp (one side) or 12 bp (perp round trip); corrected `band` is **0.27–0.54**. **At 0.27 the sponsor's own declared escalation trigger — *"had the cost arithmetic delivered `band` > 0.25 … this seat would have escalated"* — is met**, and the favourable post-hoc check that the band cannot suppress a clause-(b) day **inverts**. The error's direction eases the sponsor's own pre-registered expected cause of death, on the one parameter declared unchooseable from either survival condition. **One prose edit, zero trials, free pre-seal, permanent after P7** | **HIGH** | director-of-research → quant-validation |
| **I-241** | **`d = 1.0`'s bracket is derived from the wrong noise scale.** The derivation uses `σ/√30 = 0.183` — the estimation noise of the reference level — and omits day `t`'s own sampling variation. With the window ending strictly before the day screened, `sd(z \| null) = √(1 + 1/30) ≈ 1.017`. **`d = 1.0` is ~1.0 null SD, not the ~5.5 the document states — the same position on the scale at which §14.2 rejects `d = 0.2`.** The choice is legitimately pre-registered and legitimately labelled a judgment; the derivation's claim to bracket it is 5.5× weaker than stated | **HIGH** | director-of-research → quant-validation |
| **I-242** | **`σ̂` degeneracy is nowhere handled, and `1/k = 2.0` makes it quantitative for the first time.** In a 30-day window dominated by prints at the administered floor (~35% of prints), `σ̂` collapses and `z` is unbounded on an arbitrarily small departure; the rule's full dynamic range is two z-units, so `w` can travel full-size-to-flat on a sub-bp funding move in the **calmest** regime — the inverse of the stated mechanism. `mechanism` concedes moment **bias** and the *"censoring argues for K1"* answer addresses the **event**, not the **magnitude mapping**. **No variance floor, winsorization or `σ̂` guard exists in any field** [verified] | **HIGH** | director-of-research → quant-validation |
| **I-243** | **The R42 evidential register governs how leg (ii) is READ and changes nothing about how it is COMPUTED, and the disclosure makes the computational bias directional for the first time.** On the ~25% of inversion days `w ≡ 1.0` while `R_bench_scaled = R_bench × c`, `c < 1` — so `R_strat` is strictly larger there, losses included — and the mechanism asserts the 20 worst days are drawn from exactly that regime. **A leg (ii) fire may then be a property of the exposure match plus the inertness rather than of timing information.** I-214 with its direction identified | **MEDIUM** | director-of-research → quant-validation |
| **I-244** | **DA(2) stands verbatim and its power is confounded by I-242.** `z > 1.5` counts `σ̂` collapses alongside crowding events. **Binding on DA(2)'s executor as a reporting obligation, not as a change to the clause:** the trailing-`σ̂` distribution over the qualifying days must be reported alongside the count, so that a DA(2) survival is not read as evidence of the mechanism. **The threshold, the window, the in-sample maximum and the silence-is-a-kill provision are unchanged** | **MEDIUM** | devils-advocate → whoever executes DA(2) |
| **I-245** | **A CIO verification reached this seat garbled.** The dispatch states *"an apparent second `k = 3.0` is `1/k = 3.0`"*; the sealed text reads `z = d + 1/k = 3.0`, where `1/k = 2.0`. **The document is correct and the summary of the verification is not.** Filed because the dispatch instructed *"verify, do not take on report"* — and this is what verification returned | **LOW** | CIO |
| **I-247** | **INCIDENT — the harness is uncommitted, its suite is 110-red, and the failing call is `open_hypothesis` itself.** Five modules modified today 18:24–18:25 UTC by another seat (`registry.py` **+555**, `holdout.py`, `gates.py`, `data.py`, `engine.py`), uncommitted. Suite: **110 failed / 144 passed / 68 errors** [measured, run twice] — **not environmental**: a new `_require_grant` gate (SPEC-004 self-defence, **absent at HEAD**) now requires `TrialRegistry.write_grant(reason="REGISTER_HYPOTHESIS")` and the suite's callers were not updated. The harness is an editable install, so **the working tree executes**. **`REGISTRATION-PAYLOAD-PREREG-002` §6's six-item pre-execution checklist does not contain "open a write grant," so the seal as specified RAISES.** `CLAUDE.md`: *"if the suite does not pass, stop and file an incident."* **Checked clean: `_BINDING_FIELDS` is unchanged, sixteen fields, so §1.1's verification stands** | **HIGH** | head-of-data-infra → quant-validation → CIO |
| **I-246** | **Throughput remains 0 trials / 0 backtests / 0 verdicts / 0 seals, and one thing has changed: the family is sealable from this seat.** Appendix B #9 remains the live failure mode; Appendix B #1's metric remains undefined at n = 0 Gate 1 verdicts and this seat makes no claim from it. **The number moves on the first logged trial and on nothing else. The firm should log it in the same session as the seal or state why not.** I-219 stands and is not re-filed | **LOW-MEDIUM** | CIO → Principal |

---

## 7. TO THE PRINCIPAL — three items, none requiring an act before the seal

1. **The withdrawal is unconditional and I am not asking you to hold the seal.** My condition was
   stated, it was met, and I withdrew the day it landed. **From this seat nothing blocks. C2, C7, C8
   and C11 are Validation's and yours; C3 — this memo — is discharged.**

   **But do not let anyone execute the seal today.** I-247: the harness is uncommitted, its test suite
   is 110-red, and the specific failing call is `open_hypothesis`. That is an incident under
   `CLAUDE.md`'s own rule, it is not mine to rule on, and it is the one thing in this memo that would
   cause real damage if it went unread for a day.

2. **I-240 is the item I would most want fixed before the freeze, and I have deliberately not made it a
   condition.** It is a leg-count error that costs one prose edit today and is permanent tomorrow, and
   correcting it triggers an escalation the sponsor committed in writing to take. **The choice to fix it
   or to decline is the sponsor's and the CIO's. I have put it on the record and I stop there** — the
   difference between a seat that holds a condition and a seat that keeps finding new ones is the only
   thing that makes the first kind useful.

3. **Your ruling on the inertness finding was disclosure, not redesign, and it was the right call.**
   I accept it, I do not reopen it, and §2.3 records what it leaves behind so that the residue freezes
   visibly with the seal instead of being read as discharged. **The sponsor gave up a reading it could
   have kept — leg (ii) may no longer be presented as tail protection in inversion — in a hashed
   string. That is the strongest thing R-008 did and it was not something I asked for.**

---

*Devil's Advocate · Castellan Capital · 2026-08-25 · dispatch S4-D-005 · **`REDTEAM-002`'s DO NOT SEAL
verdict is WITHDRAWN.***

*`book/registry.db` read **0 hypotheses / 0 trials / 3 events** on opening and reads 0 / 0 / 3 on
closing. **No hypothesis opened. No `open_hypothesis`. No registration. No seal. No trial. No backtest.
No vault. No registry write. No commit.** `PREREG-002`, `harness/`, `book/`, every `VALIDATION-*`
document and both `REGISTRATION-PAYLOAD-*` artifacts were read and **not modified** by this seat.
**No query of any kind was run against `book/pit.db` this session** — DA(2)'s test was not run and no
distribution, moment, quantile or count of `z(t)` was computed, per the ordering this seat named:
literals first, query second. The only database read was `book/registry.db`, read-only,
`SELECT COUNT(*)`. All arithmetic in §2.1, §3.1 and §3.2 is estimator or cost arithmetic on figures
already sealed or already cited, and no number produced outside the engine is quoted anywhere in this
memo as a performance figure.*

*Authored lines: ~320 projected against a comparator-derived bracket of 79 / 492. Delivered within
budget.*
