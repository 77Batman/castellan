# RED-TEAM MEMO 002 — `funding-carry-conditioning-002`, the document as it will seal

**Seat:** Devil's Advocate (Seat 5) · **Reports to: the Principal** · **Date:** 2026-08-25
**Dispatch:** S3-D-024 · **Discharges:** **C3** · **Issue range: I-210 … I-219**
**Subject:** `research/PREREG-002-crypto-funding-basis.md` at R-007 + S3-D-019 + Validation's §5 edit ·
payload `research/REGISTRATION-PAYLOAD-PREREG-002.md` · verdict `research/VALIDATION-GATE0-002-funding-carry.md`
**Registry:** `book/registry.db` — **0 hypotheses / 0 trials / 3 events** [measured, read-only, opening and closing]

---

## 0. LINE BUDGET, STATED BEFORE WRITING

| § | Section | Projected |
|---|---|---:|
| 1 | Steel-man — the strongest form of the thesis and of the document | 28 |
| 2 | The artifact case | 105 |
| 3 | The uncapturable case | 62 |
| 4 | The already-arbitraged case | 58 |
| 5 | The cheapest kill | 45 |
| 6 | **KC-002-DA** — the binding kill condition, authored against the family | 55 |
| 7 | The process attack — does a document revised seven times deserve to seal | 90 |
| 8 | The 13-day staleness, ruled | 42 |
| 9 | What would change my mind, and what the firm has stopped being able to see | 38 |
| 10 | Ranking by how much each objection should move the decision | 22 |
| 11 | Issues filed, I-210 … I-219 | 42 |
| 12 | To the Principal | 18 |
| — | header, verdict box, provenance footer | 45 |
| | **TOTAL** | **~650** |

**Under the ~800 ratchet with ~150 lines of headroom. Nothing proposed for cutting.**

---

> # VERDICT: **DO NOT SEAL.**
>
> **Not on the ground the CIO handed me. On a defect nobody in three sprints has named:
> the sealed `statement` field freezes a sizing rule with two free symbols in it.**
>
> **`k` (the de-scale slope) and `d` (the deadband) have no numeric value anywhere in this
> document, its payload, or its seal block. Neither does `band`.** The only bound parameters are
> `lookback = 30 days` and `w_max = 1.0`. `R_strat` is therefore not defined by the sealed text, F-002
> legs (i) and (ii) are not computable from it, the ±50% grid has no centre, and **KC-002 clause (b) —
> the sponsor's own pre-registered expected cause of death — is a pure function of the two symbols the
> seal does not fix.**
>
> **This is a one-revision, zero-trial, pre-seal repair of exactly the class R-004 through R-007
> performed six times. It costs a dispatch now and it costs the family permanently after P7.**
>
> **Second, fix in the same pass:** the two binding fields that carry `[2020-01-01, C]` must stop doing
> so (§8). **Third, not seal-blocking but it should go back to Validation:** §19.1's sole ground for
> ADMITTED rather than ADMITTED-AS-EXPLORATORY is *"a verdict is reachable here"* — and Validation's
> own **D-6** says, as the document stands, that it is not (§7.3).
>
> **Everything else in this memo is an argument about whether the family is worth running. The three
> lines above are the argument about whether this document is fit to freeze.**

---

## 1. STEEL-MAN — stated first, at full strength, because attacking a weakened version is worthless

**The thesis, in its strongest form.** Perpetual funding is a fair price for a service, so harvesting it
at constant size is factor beta and the firm should not pay for it — the sponsor says this itself, at
Gate 0, before anyone made it. The narrower claim is that the *price of the tail is not linear in the
observable*: the premium is roughly linear in crowding while cascade severity is convex in it, so beyond
some level of funding the marginal premium stops paying for the marginal tail, and a position that
shrinks into rich funding gives up less mean than it gives up tail. The persistence escape is not "nobody
has looked" but a structural constraint on the marginal supplier — yield vehicles whose liabilities are
written in notional deployed and which lose subscriptions when they stop earning. That is a claim about
*sizing*, it is narrower and weaker than "the premium is free," and it is consequently more defensible.

**The document, in its strongest form.** `N_inherited = 0` measured rather than asserted. Seven
conditioning choices declared with full menus before any measurement, against a registry holding zero
trials, with the counterfactual priced at 135,000 and `MinBTL` at 16.79 years so the reader can see what
the declaration is worth. A falsifier with no `argmax` anywhere in it, four legs, stated nulls, a stated
α, an exposure-matched tail benchmark built specifically to defeat the "any size reduction improves the
tail" bias, and a joint false-survival rate of 1.3e-4 against F-001's measured 31%. A trial budget cut
40% voluntarily against a planning `ρ` the sponsor named rather than discovered. Sixty-one limits
classified, thirty-four of them declared unenforceable *by the seat that would benefit from implying
otherwise*. Three near-fatal defects caught pre-seal, two of which would have killed the family and one
of which the sponsor found by deleting a clause that killed its own family and then refusing to rule on
the deletion.

**I have read every seat's work on this family. The document is the best artifact this firm has
produced. That is exactly why the objections below had to be found somewhere other than where it is
looking, and §7 is about why it was looking everywhere but there.**

---

## 2. THE ARTIFACT CASE

### 2.1 The mechanism: **the sizing rule is provably inert in the regime where its own tail lives**

*This is my strongest argument against the family, it is a mechanism argument rather than a statistical
one, and it is nowhere in the document.*

The sealed rule is one-sided:

```
w(t) = clip(1.0 − k·max(0, z(t) − d), 0, 1.0)
```

`max(0, z − d)` is zero whenever `z(t)` is at or below its trailing baseline. **The rule can only act
when funding is RICH relative to its own 30-day mean. It does nothing at all when funding is cheap, and
nothing at all when funding is negative.**

Now read the document's own account of where the tail is. §3.2 population 3: hedgers *"are **short**
perp… they are the reason funding inverts in drawdowns, when their hedging demand spikes at the same
moment leveraged longs are being liquidated."* §3.3 risk 3: *"funding turns negative in drawdowns, so
the carry stops paying precisely in the periods when the position is losing on the basis."* §7.4:
*"the negative-funding regime is where the left tail lives."*

**Compose the two.** A liquidation cascade is the event that *destroys* the crowding the rule is keyed
to. During it, longs are force-closed, hedgers pile in short, and realized funding collapses and
inverts. `z(t)` goes sharply negative. `max(0, z − d) = 0`. **`w = 1.0`. Full size.** And the 30-day
trailing mean makes it worse, not better: after a run of rich funding the baseline is high, so
post-event `z` stays deeply negative and **`w` is pinned at benchmark weight for up to thirty days
after the event.**

The family's defence is that the de-scaling happens on the *approach*, so less size is carried into the
event. That survives only if the loss is concentrated on day one. **The document's own §3.3 risk 2 says
it is not:** *"in a cascade the perp can trade far from spot for an **extended interval**."* A rule that
de-scales on the approach and returns to full size on day one of a multi-day basis dislocation is not a
tail-reduction rule. It is a rule that reduces exposure to the *anticipation* and holds full exposure
through the *realization*.

**Measured, so this is not a thought experiment** [measured this session, read-only, COUNT queries on
raw stored `funding_rate` prints — no mean, no z-score, no return, no P&L; same class as §0's
`COUNT`/`MIN`/`MAX` and as `DATA-VERIFY-001` §5.2's floor-share count]:

| Symbol | Prints | Negative | Days with ≥1 negative print |
|---|---:|---:|---:|
| BTC/USDT:USDT | 7,245 | 1,031 (**14.23%**) | **619 of 2,415 (25.63%)** |
| ETH/USDT:USDT | 7,245 | 1,007 (**13.90%**) | **609 of 2,415 (25.22%)** |

**A quarter of the in-sample days sit in the state where the rule is provably inert.** This is not a rare
corner; it is a quarter of the sample, and it is the quarter the mechanism is about.

**Two things I will not claim.** I will not claim the choice was concealed — K2's declared menu carries
option (3), *"sign-flip to long-perp when funding inverts,"* and it was considered and not selected. And
I will not claim inertia in the tail regime is irrational: holding benchmark weight through an inversion
is a defensible risk posture. **What it is not is tail reduction — which is precisely and only what
F-002 leg (ii) claims to measure.** The document names the regime where its risk lives and then
specifies a rule that cannot act in it, and no revision has put those two sentences next to each other.

### 2.2 The selection mechanism: **an undeclared search of unbounded cardinality, invisible to the seal**

The specific artifact mechanism is **selection over a continuum, uncounted**.

`k` and `d` are free symbols in the sealed `statement`. `band` appears in the sealed `horizon` as a
symbol. **No numeric literal is assigned to any of the three anywhere in `PREREG-002`, in
`REGISTRATION-PAYLOAD-PREREG-002`, or in the §21 seal block** [measured — full-text grep of all three].

Three sentences in the document assert a fixing that does not exist:

- §6.2: *"`lookback = 30 days`, `d`, `k`, `band` and `w_max = 1.0` are this seat's choices, **made now,
  before any measurement**."* Two of the five carry no value.
- §10.5 (line 1104): *"`d` (the deadband) and `band` (the turnover band) are **fixed at
  pre-registration** and are not gridded."* Fixed at nothing.
- §11.5 R4(a) claims model-prior provenance for *"universe, sizing rule, **parameter centres** (§6)."*
  There are no parameter centres.

**Why the seal cannot catch this.** `statement` is class **(a) on existence, (c) on content** (§10.11.1
field 2) — `registry.py:262–268` raises on empty and reads no further. A post-seal choice of `k` is not
an amendment, so **P3 does not refuse it**; it changes no binding field, so **P4/`verify_prereg` does not
see it**; it is not a date, so the dated-clause apparatus does not reach it. The sixty-one-limit class
register covers `w_max = 1.0` at C-08 and covers neither `k` nor `d` nor `band` anywhere.

**Three consequences, in ascending order of severity.**

1. **F-002 is not computable from the sealed text.** Legs (i) and (ii) are functionals of `R_strat`, and
   `R_strat` is *"identical [to `R_bench`] except that per-asset notional is scaled by `w(t)`."* Whoever
   runs step 3 picks `k` and `d`. E2 says F-002 is *"evaluated ONCE"* — and E2 is **C-04, class (c),
   which the document's own §10.11.4 flags as one of the two commitments it tried to promote to (b) and
   could not: *"discoverable by audit, prevented by nothing."***
2. **The ±50% grid has no centre.** §10.5 grids `lookback` and `k`; `grid_from_center(fraction=0.5,
   steps=5)` requires a centre. §15 runs the grid at **step 6**, after F-002 at steps 2–3. **The centre
   of the parameter grid is therefore chosen with F-002's output in hand.** That is I-029(d) — *"evaluates
   at the argmax of its own sample"* — relocated from the lag axis to the parameter axis, in the family
   whose §5.5 table exists to certify that it committed no such operation.
3. **KC-002 clause (b) is set by the dial the seal does not fix.** Clause (b) kills on *"fewer than 30
   days on which the conditioning moved notional by more than ±25%."* `|Δw| > 0.25` iff
   `k·(z − d) > 0.25`. **Larger `k` and smaller `d` make clause (b) easier to survive, and the direction
   is knowable a priori without running anything.** §14.2 R7 pre-registers clause (b) as *"not merely the
   most likely killer, it is the expected outcome."* **The sponsor has pre-registered its expected cause
   of death as a function of two numbers it has not written down.** I-153 — which this firm correctly
   treated as near-fatal — was a kill condition that fired with certainty; it was at least *visible in
   the text*. This one is invisible.

**I am not alleging bad faith and the direction of my objection does not require any.** The defect
survives seven revisions, a 590-line Validation verdict, nine enumerated deferrals, and roughly two
hundred issues **because every instrument pointed at this document has been pointed at its dates, its
denominators, its classes and its harness facts — and none at whether its specification specifies.**

### 2.3 Leg (ii)'s exposure match is on the wrong moment, and its effective sample is about six

§5.5(d) is the document's proudest repair: `R_bench_scaled = R_bench × c`, `c` = ratio of time-average
gross exposures, *"so any tail improvement must come from **when** the size was reduced and cannot come
from **how much** on average."*

**`c` matches the first moment of the exposure distribution. Leg (ii)'s statistic is the mean of the 20
worst daily returns — an order statistic, a functional of the joint lower tail of `(w, r)`.** Matching
`E[w]` licenses nothing about `E[min_k(w·r)]`. Under a null in which `w` is dispersed and bounded above
by 1.0 while `c = E[w] < 1`, the worst realizations of `w·r` are drawn preferentially from the
*high*-`w` region — and `w = 1.0` on the ~34% of prints pinned at the administered floor
[measured this session: **33.97% BTC / 34.12% ETH** of prints are exactly `0.0001`, confirming
`DATA-VERIFY-001`'s ~35%] and on the ~25% of days carrying a negative print (§2.1). **The exposure match
is a match on the mean for a test of the extreme, and §5.5(d) asserts a completeness it does not have.**

The document half-knows this. §5.3 concedes leg (ii)'s `≤ 0.10` is the **one [assumed] term** in the
1.3e-4 chain, and §22 row 2b concedes that if the true value is near 1.0 *"leg (ii) is decorative and
must be replaced before sealing."* **C11 — the calibration that would settle it — has just been removed
from the seal-blocking set** (Validation §10.1, I-202) and demoted to a class-(b) Gate 1 condition. The
reclassification is *mechanically correct* — you cannot log a trial against an unregistered family — and
its consequence is that **the family now seals with its falsifier's headline decisiveness resting on an
assumed number, and the only thing preserving the "calibrate before F-002" ordering is §15's step table,
which is class (c).**

**And the tail test's effective sample is much smaller than 20.** §6.1 records the primary universe's
largest in-sample basis excursions as −73.65 bp (BTC) and −102.95 bp (ETH) — **both on 2020-03-12**, the
same day. §18 declares BTC and ETH *"one cluster, not two positions."* §17 rank 10 concedes `N_eff`
across the two is *"far below 2"* — and applies that concession to the cross-section and **never to the
tail test, which is where it bites hardest.** The 20 worst days of a two-asset, one-cluster, crypto-beta
pair are drawn from the market-wide stress episodes of 2020–2026: March 2020, May 2021, LUNA/UST, FTX,
and perhaps two more. **Twenty observations, roughly six independent draws, one of which (2020-03-12)
supplies both assets' extremum.** §4.4's own P&L-concentration criterion — no single day > 10% of total —
exists to catch exactly this shape and is applied to returns, not to the falsifier.

### 2.4 What I checked and found clean, recorded so the absence is legible

- **C12's cadence discharge no longer covers the sealed span.** It measured 4,802 symbol-days through
  2026-07-28; the settled span now carries 4,828. **I swept the 26 uncovered settled symbol-days:
  3 funding prints per day, both symbols, every day. Clean. No new K7 trigger.** [measured, count query]
  Filed I-217 so the discharge's scope matches the span, not because it found anything.
- **The perp `close`/`low`/`volume` row counts (2,417) exceed `high`/`open` (2,416).** That is the
  bitemporal record of I-190's restatement, which is correct `PITStore` behaviour, not a duplicate.
- **I expected the negative-funding regime to be too thin to constitute a regime cycle and it is not** —
  25.6% of days carry a negative print. **That argument is available and I am not making it, because I
  measured it and it is false.**

---

## 3. THE UNCAPTURABLE CASE

### 3.1 The alpha under test *is* turnover, and the parameter that prices it is the one that is unbound

`R_bench` is a constant-notional delta-neutral pair that trades only when `|w_target − w_held| > band` —
at `w ≡ 1.0` it essentially does not trade at all. `R_strat` is identical **except that it trades**.

**The entire quantity leg (i) tests is therefore (tail benefit) minus (incremental transaction cost), and
the incremental transaction cost is a function of `band`.** Which has no value (§2.2).

The two survival conditions pull `band` in **opposite** directions:

| Widen `band` | Narrow `band` |
|---|---|
| fewer round trips ⇒ lower cost ⇒ **leg (i) easier** | more conditioning days ⇒ **KC-002 clause (b) easier** |
| fewer days with `\|Δw\| > 25%` ⇒ **clause (b) harder** | higher cost drag ⇒ **leg (i) harder** |

**A specification whose two survival tests pull an unsealed parameter in opposite directions is tunable
by construction**, and the tuning is invisible to `prereg_sha256`. This is the capture argument and the
selection argument arriving as the same defect, which is why §2.2 is the blocking finding rather than a
ranked objection.

### 3.2 The cost model cannot charge the only cost the hypothesis is about

§12 defect (d) stands, class (c), C-25: **`CostModel` has no field that can charge liquidation or
venue-insolvency risk**, and `VALIDATION-RULING-003` §4 declines to invent a number.

The document treats this as a disclosure. It is more than that. **The entire economic content of the
hypothesis is that the funding premium is compensation for a tail.** A net return computed by a cost
model that cannot charge the tail is not a conservative estimate of this strategy's net return — it is an
accurate estimate of a *different* strategy, one that collects the premium and does not bear the risk.
§16 concedes separately that Sharpe, `t`, DSR, subperiod positivity and P&L concentration **all reward a
carry profile** and that *"the firm's Gate 1 cannot see the risk it is gating."*

**Stack them: a cost model blind to the risk, a battery blind to the payoff shape, and the sole
instrument that can see it — KC-002 clause (c), the 4% single-day sleeve trigger — is class (b),
executed by the Principal, on a weekly cadence, with no harness evaluator specced-and-dispatched
(B-01, I-135).** That is not one disclosure; it is three independent blindnesses to the same object, and
the document lists them in three different sections.

### 3.3 Materiality, and what §19.1's differentiator is actually worth now

$250,000 unlevered; §13.2 puts an **excellent** result at 15–30 bp of firm NAV per year; §13.3 defers the
leverage question to a result. §19.1's case for ADMITTED rather than ADMITTED-AS-EXPLORATORY is not that
the mechanism is better than PREREG-001's — the sponsor is explicit that it is not — but that **"a
verdict is reachable."**

Validation's own report says it is not, as the document stands (§7.3 below). Strip that, and the
difference between the two families is: one has a reachable verdict on paper and an unreachable one in
the repository; the other has an unreachable verdict on arithmetic. **The verdicts differ by a full
category. The families, today, do not differ by nearly that much.**

---

## 4. THE ALREADY-ARBITRAGED CASE

### 4.1 Escape (c) is "nobody has looked," relocated one level up — and §4's own rejection kills it

§4 rejects escape (a) — *the premium is simply un-arbitraged* — **"on its face. Cash-and-carry is the
single most institutionalized trade in crypto. Claiming it is un-arbitraged would be the 'nobody has
looked' argument the Devil's Advocate correctly refuses."** Correct, and I refuse it.

It then selects escape (c) and states the family's claim as: *"This family does not claim the crowd has
missed the premium — it claims the crowd is wrong about how to **size** it."*

**That is the identical claim, moved from the premium axis to the sizing axis, and §4's own rejection
applies to it verbatim.** In the most institutionalized trade in the asset class, on a signal every venue
publishes on its front page, on an eight-hour clock, the assertion that nobody has worked out that you
should carry less of it when it is expensive is a "nobody has looked" claim. The document earns credit
for refusing the weak version and then spends the credit on the same argument with a different noun.

### 4.2 The named counterparty is not the marginal price-setter

The persistence rests on yield vehicles that *"advertise a yield and lose subscriptions when they stop
earning it… de-scale into a redemption cycle rather than a risk signal… mandate written in notional
deployed rather than risk taken."* That is a real population and a real constraint.

**It is not the marginal supplier of short-perp at BTC/ETH scale on Binance.** The marginal supplier is a
basis desk or market maker running automated inventory management — and those desks **vol-target**. Gross
gets cut into rising realized volatility, and rising realized volatility is correlated with rich funding
because both are produced by the same crowding. **De-scaling into rich funding is therefore already
performed at scale, by participants who never read the funding signal, as a by-product of a risk system.**
The behaviour the family claims is unoccupied is occupied by a different route, and the residual is
whatever is left after every automated inventory manager in the venue has already done it.

**The document's own falsifier of escape (c) would settle this and cannot be run.** §4: *"aggregate
short-perp open interest **falls** as funding rises above its trailing baseline… If the supply side
already contracts into rich funding, then (c) is dead."* Aggregate OI is **not in `pit.db`, has no
loader**, and §20 lists it **non-blocking**. **The family seals with its persistence argument declared
falsifiable, its falsifier named, and no instrument to run it inside the family's budget.**

### 4.3 The 50% haircut is calibrated on the wrong diffusion channel and is too generous here

§11.6 accepts the haircut in full and calls it *"the largest single hurdle this family faces."* It is
accepted on McLean–Pontiff's 26% out-of-sample / 58% post-publication decay — **a base rate measured on
equity anomalies published in journals**, where the diffusion channel is peer review, working papers and
years.

This family's mechanism is *"the FX carry-crash literature and its standard prescription… transposed"*
(§11.6(2)) applied to a signal published continuously by the venue, in a market instrumented by
open-source funding-arb bots and by every delta-neutral vault's public risk documentation. **The
diffusion channel here is a GitHub repository and a Discord, not a journal.** Chen & Velikov's 88%
erosion is the closer analogue and is itself an equity number.

Validation §10.3 records that *"this family's thesis does not require that this time is different."*
**It does — on the diffusion rate.** It requires that a monotone one-parameter rule on a public number,
in the most heavily-instrumented carry trade in the asset class, has not been implemented at scale. That
is the claim, it is not stated anywhere in the document as a claim, and it is the one the persistence
argument actually rests on.

---

## 5. THE CHEAPEST KILL — and it is cheaper than the one the document runs first

**§15 runs F-002 leg (iii) first, and the sponsor has already withdrawn leg (iii) as evidence.** R7:
*"It will almost certainly not fire, and this seat records now that its non-firing is worth nothing as
evidence."* The document's declared cheapest-kill-first ordering opens with a trial it has pre-declared
uninformative.

> ### THE TEST: the in-sample dynamic range of `w(t)`, at the (k, d) the seal must now name.
>
> Compute, on data already on disk, the count of days on which `|w(t) − 1| > 0.25`, and the **maximum**
> such count over **any** rolling 187-day in-sample window.
>
> **KILL if the maximum over any in-sample 187-day window is below 30.**

**Why it is the cheapest test available, on four counts.**

1. **It is not a backtest and arguably not a trial.** It touches no perp price, no basis, no spot return,
   no cost model, no P&L. It is a functional of the stored `funding_rate` series only — the same class as
   `DATA-VERIFY-001` §5.2's floor-share measurement and §0's `COUNT`/`MIN`/`MAX` diagnostics, both of
   which this firm has already ruled are not trials. **Cost: a fraction of a Sonnet unit, zero `N`.**
2. **It tests the sponsor's own stated expected cause of death**, on the sponsor's own threshold, with
   the sponsor's own window. §14.2 R7: clause (b) *"is not merely the most likely killer, it is the
   expected outcome, and the reason is the clamp rather than the market."* The clamp is measured — 34%
   of prints at the floor — and its effect on `z(t)`'s dynamic range is exactly what this query returns.
3. **It is maximally generous to the family and therefore undeniable when it fires.** Taking the
   *maximum* over any 187-day window in 6.6 years asks whether the family's *best* half-year in the
   sample would have survived clause (b). If the answer is no, the forward window survives only by luck,
   and **187 days of forward accrual plus a Stage-2 unlock buys the firm nothing that one query gives it
   today.**
4. **It forces the repair.** The query cannot be run until `k` and `d` have values, which is the blocking
   finding at §2.2. The cheapest kill and the blocking defect are discharged by the same act.

> **THE ORDERING IS LOAD-BEARING AND I state it as a condition of the test, not as advice.**
> **`k`, `d` and `band` are named in the sealed text FIRST. The query runs SECOND.** Reversed — choosing
> `(k, d)` with the dynamic-range result in hand — is selection over a continuum, it is the I-029(d)
> operation, and it must be charged at the cardinality of the continuum, which is to say the family dies.
> **If the sponsor wants the diagnostic before the choice, that is a legitimate request and its price is
> a successor family under `predecessor_family`.**

---

## 6. KC-002-DA — THE BINDING KILL CONDITION, AUTHORED AGAINST THE FAMILY

Charter §4.4 requires a **named, dated, observable kill condition accepted by the sponsor before capital**.
KC-002 is the sponsor's own, and Validation §10.2 says plainly that *"a kill condition authored by the
sponsor is structurally weaker than one authored against it."* KC-002 is a good kill condition and I do
not weaken it by one word. **It binds the forward window's P&L, its conditioning-event count and its
worst day. It binds nothing about whether the specification specifies.** KC-002-DA does.

> ### **KC-002-DA — three clauses, binding on `funding-carry-conditioning-002`.**
> **Sponsor: PM Pod B. Accepted in writing, and signed by the Principal, before any capital — paper or
> real — is allocated. Anti-reinterpretation clauses 1–5 of KC-002 apply to KC-002-DA unchanged.**
>
> ---
>
> ### **DA(1) — THE SPECIFICATION CLAUSE. Observation date: `C`, the seal instant.**
>
> **At the moment `open_hypothesis` is called, `k`, `d` and `band` must each appear as a NUMERIC LITERAL
> inside a binding field of the registration payload.** If `prereg_sha256` is computed over a field set
> in which any of the three is a free symbol, an ellipsis, a range, a reference to another document, or a
> phrase of the form *"fixed at pre-registration"*, then **the family is NOT ADMITTED, the registration
> is void, and every trial logged against it is inadmissible under A2.**
>
> **Refused in advance, by name:** *"the value is implied by the grid centre"* · *"the value is in the
> researcher's config"* · *"the value is `w_max`-normalised and therefore free"* · *"a range is a
> pre-registration."* **Observable:** read the sealed strings; the three literals are present or they are
> not. **Executor:** Validation, in the same session as the seal. **Artifact:** the three values quoted
> verbatim on the face of the Gate 0 verdict's addendum and on every subsequent Validation Report.
>
> ---
>
> ### **DA(2) — THE DYNAMIC-RANGE CLAUSE. Observation date: `C + 30 days`, absolute.**
>
> **Within 30 days of the seal, the firm computes, in-sample, at the sealed `(k, d)`: the count of days
> on which `|w(t) − 1| > 0.25`, and the MAXIMUM such count over any rolling 187-day in-sample window.**
>
> ### **If that maximum is below 30, the family is KILLED on that date** — registry marked TERMINATED,
> ### no further trials, no Gate 1 submission ever, automatic, not appealable to the CIO.
>
> The threshold (30) and the window (187 days) are **the sponsor's own**, transcribed from KC-002 clause
> (b) without alteration. The only thing this clause adds is that the in-sample maximum is the test, and
> the reason is that a forward window cannot beat the best window the sample contains except by luck.
> **If the sponsor believes the in-sample maximum is not predictive of the forward count, that belief is
> a statement that clause (b) is not predictable — which makes KC-002 clause (b) a coin flip, and I will
> take that concession instead.**
>
> **And SILENCE IS A KILL.** If the computation is not performed by `C + 30 days` for any reason —
> including that `k` and `d` were never named, that no unit was available, that the harness was not
> ready, or that the seat that owned it changed — **the family is killed by default.**
>
> ---
>
> ### **DA(3) — THE EVALUABILITY CLAUSE. Observation date: `C + 90 days`, absolute.**
>
> **If, 90 days after the seal, `harness/scripts/evaluate_dated_clauses.py` does not exist, or exists and
> does not exit 0 on this family, the family is PARKED: Stage 1's authorization is SUSPENDED and no
> further trial may be logged** until it exists and exits 0.
>
> **Reason, and it is Validation's own:** **E-24 makes a nonzero exit a permanent INSUFFICIENT-DATA**
> (D-6, I-173, I-186). Every trial logged in that state is spent on a family that cannot receive a
> verdict, and trials cannot be unspent. **Refused in advance:** *"the checker is coming"* · *"the exit
> code is a document defect, not a family defect"* · *"the trials will still be good when it lands."*
> **The clause fires on the state of the repository on the date, and nothing else.**

---

## 7. THE PROCESS ATTACK — does a document revised seven times deserve to seal?

**The CIO says nobody in the chain has asked this and supplies no answer. Here is mine: the revision
count is not the finding. The revision PROVENANCE is.**

### 7.1 Seven revisions, and not one of them originated in the sponsor noticing

| Rev | What triggered it |
|---|---|
| **R-001** | `DATA-VERIFY-001` / I-045 — an **external measurement** by Seat 9 |
| **R-002** | `VALIDATION-RULING-004`, I-050, I-053, `DATA-VERIFY-002` — **Validation and Seat 9** |
| **R-003** | The **Principal's** ruling on I-057 · `VALIDATION-SPEC-002` §7.2's countersigned tightening |
| **R-004** | `GATES.md` **§4.7.2** — an instrument Validation built and pointed at the document |
| **R-005** | The **Principal's** class mandate |
| **R-006** | The dated-clause sweep, **ordered by dispatch**. The document's own words: *"the unflattering half is that R-006 found it by running a sweep it was **ordered** to run, not by remembering"* |
| **R-007** | The **Principal's** instruction to measure §11.1's span rather than label it |

**Seven for seven.** This document has not been *checked* seven times. It has been *found* seven times,
by seven instruments built and aimed by other seats. Every one of the three near-fatal defects — I-130,
I-140, I-153 — arrived inside a revision that some other seat commissioned.

**The consequence is a base rate, and it is the honest way to answer the CIO's question.** On seven for
seven, the probability that an eighth instrument pointed at a dimension nobody has yet pointed one at
finds an eighth defect is **high**. §2.2 is that eighth. It was found by asking a question no dispatch
has asked — *does the specification specify?* — and it took one grep.

### 7.2 The near-fatal arrival rate did not converge. It spiked at revisions four through six.

I-130 (2026-08-10, HIGH, permissive unlock table) · I-140 (2026-08-10, HIGH, a condition precedent that
downgrades on a false premise) · I-153 (2026-08-11, HIGH, a clause 5 that terminates the family with
certainty). **Three near-fatal defects in 48 hours, at revisions four through six, in a document that
declared itself "COMPLETE, SEALABLE" on 2026-07-28.**

A converging document finds its worst defects early and its trivial ones late. **This one found a false
harness fact fifth, a certain-death clause sixth, and a mis-measured span seventh.** That is not the
profile of a document approaching a fixed point. It is the profile of a document whose defect density is
being sampled by whatever instrument happens to be built next.

### 7.3 The document, as it will seal, cannot pass Gate 1 — and Validation says so

**This is the argument I most want on the record and it is not mine.** Validation's own verdict, D-6 and
§10.3(2): **I-173 / I-186 — registering as the document stands returns a permanent nonzero exit, and
E-24 makes a nonzero exit a permanent INSUFFICIENT-DATA.** `harness/scripts/evaluate_dated_clauses.py`
**does not exist** [measured — I-186]. Validation §10.3(2) states it plainly: *"This is currently the
family's binding constraint and it is document-side, not statistical."*

Now read §19.1. The **sole** stated ground on which this family was recommended **ADMITTED** rather than
ADMITTED-AS-EXPLORATORY — the whole content of the redirect of Pod B's compute — is:

> *"A hypothesis whose verdict is reachable deserves compute; one whose verdict is not, does not —
> however good its story."*

**Validation has measured that this family's verdict is not currently reachable, and the Gate 0 verdict
that carries that measurement did not revisit the recommendation that rests on it.** ADMIT-CONDITIONAL
was issued in the same document that establishes the ground for ADMITTED is presently false.

I am not asking for the verdict to be reversed — that is Validation's call and I do not hold it. **I am
filing that the two findings are in the same document and were not put next to each other (I-215).**

### 7.4 The sponsor has been writing my memo for three sprints, and that is a structural problem

§20's blocker table, four revisions running:

- R-004: *"hands the red team its **best target yet** and this seat names it rather than waiting"*
- R-005: *"hands the red team the **sharpest target** this document has yet produced"*
- R-006: *"hands the red team its **most concrete target** yet"*
- R-007: *"hands the red team a **second concrete target**"*

**Every one of those four targets is real, and every one of them is a trench the sponsor has already
dug.** A red team that attacks where the sponsor points is producing *"objections the sponsor has already
answered"* — Charter Appendix B **#5**, the ceremonial-red-team failure mode — arriving not through this
seat's laziness but through the sponsor's diligence. **The more honestly a sponsor pre-empts, the more
completely it controls the attack surface.** That is a property of the document's form, not a criticism
of its author's intent, and it is worth naming because the form is about to be frozen and copied.

**I refused all four handed targets and read the specification instead. That is where §2.2 came from.**

### 7.5 The base rate, reported unprompted, and it is not the one I was told to watch

Charter Appendix B **#1** and my own I-003 / I-025: *Principal-originated hypotheses passing Gate 1 at a
materially higher rate than others'.*

| Metric | Value | Reading |
|---|---|---|
| **Gate 1 verdicts, any origin** | **0** | I-003's metric is **undefined at n = 0**, not at n ≥ 8. **No claim is available and I make none.** |
| **Gate 0 verdicts** | PREREG-001 (Principal-originated): **ADMITTED-AS-EXPLORATORY**. PREREG-002 (Director-originated): **ADMITTED** | 1 vs 1. **Uninformative, and I say so rather than reading it.** The Director-originated hypothesis got the strictly better verdict; at n = 1 that is not evidence of anything |
| **I-025 · Opus units by origin** | Sprint 1: **4 of 4 = 100% Principal-originated.** Today: **inverted** — Sprints 2 and 3 and the sealed reserve are entirely on the Director-originated line; `forward-lag-001` has received nothing since Sprint 1 | The bias metric I proposed has moved, and it has moved **away** from the failure mode it was built to detect |
| **Trials logged, firm-wide, since activation** | **0** | — |
| **Backtests run** | **0** | — |
| **Hypotheses reaching a verdict** | **0** | — |
| **Pre-registrations sealed** | **0**, in 28 days, at ~200 issues | — |

> **THE FIRM IS NOT EXHIBITING APPENDIX B #1. IT IS EXHIBITING APPENDIX B #9.**
>
> *"The firm confuses activity with progress. Many hypotheses in flight, none reaching a verdict. **The
> pipeline must have a throughput number and it must be reported.**"*
>
> **The throughput number is zero. I am reporting it because the Charter requires it reported and
> because no artifact in three sprints has stated it.** Twenty-eight days of four Opus seats have
> produced one unsealed pre-registration, two hundred issues, and no measurement of any market.
>
> **This is not an argument for sealing faster.** §2.2 is a real defect and the fix is a dispatch. It is
> an argument that the firm's scarce resource has been spent on the *document* rather than on the
> *hypothesis*, that the ratio is now extreme, and that the seat best placed to notice — the CIO, who
> owns the compute allocation and is accountable for it under Charter §5.3 — has spent three sprints
> allocating to the same artifact. **Addressed to the CIO and to the Principal, at I-218 and I-219.**

---

## 8. THE 13-DAY STALENESS — RULED

**Verdict: MATERIAL. Not fatal. Free to fix, and the firm has repaired its instances five times without
repairing its cause.**

**Not fatal, and here is why the CIO's framing overstates it.** `gates.py` takes `years_calendar` from
`oos_index`, never from `C`; Validation §7.3 has already ruled that *"any figure computed as
`C − 2020-01-01` is inadmissible in any artifact."* The engine is not deceived and the length criterion
is class (a). Leg (0)'s 1,800-bar floor is not breached at 2,414 settled bars. **Nothing about the
arithmetic breaks.**

**Material, and here is what actually freezes.** Two *binding* fields carry the window:

- `statement`: *"over **2020-01-01 to C**, net of the full Charter 4.6 cost stack on both legs"*
- `falsifier`: *"on the same daily UTC index over the full in-sample **[2020-01-01, C]**"*

At `C = 2026-08-25` against a last settled bar of 2026-08-11, **the sealed falsifier's own computation
window contains fourteen days that do not exist**, permanently, under P7. Validation's §7.3 prohibition
is a sentence on a Validation Report — it does not enter `prereg_sha256`, and after the seal the sealed
text and the governing ruling disagree, with `verify_prereg` protecting the sealed text.

**And there is a gap nobody has named.** Under Option D the holdout is `[C, G]`. If in-sample ends at the
last settled bar `B < C`, then `(B, C]` is fourteen days that are **neither in-sample (no data) nor
holdout (starts at `C`)**. Those bars will be ingested post-seal. **A researcher running the sealed
falsifier on `[2020-01-01, C]` then runs it on fourteen bars whose values were not knowable at the
freeze.** That is not look-ahead in the usual direction, and it does mean E2's *"evaluated ONCE"* is
evaluated over a window whose contents were determined after the document was frozen.

**The cause, which is what makes this the fifth instance and not the first.** R23, R33, R34, R37 and
I-097 are five repairs of one conflation: **`C` is used for two different objects — the freeze instant
and the in-sample right edge.** They were the same object only under the same-day-seal plan of
2026-07-28, which §20.1 abandoned on 2026-08-04. Every repair since has chased a literal. **None has
separated the two meanings, which is why the defect returns at every seal date and will return at the
next one.**

> ### **THE FIX IS NOT THE CIO's (a), (b) OR (c), AND IT DOES NOT NEED THE PRINCIPAL.**
>
> The CIO's option (c) — *redefine `C` as the last settled bar* — is a definitional change to a Charter
> term and is correctly the Principal's. **It is also unnecessary.** Nothing needs redefining, because
> `C` is doing a job it should never have been doing.
>
> **Replace `[2020-01-01, C]` in `statement` and `falsifier` with `[2020-01-01, the last settled common
> bar of the primary universe at the first run]`.** That is (i) exactly what `oos_index` will carry,
> (ii) exactly what Validation §7.3 has already ruled governs, and (iii) **not a change to `C`** — `C`
> keeps its meaning as the freeze instant and keeps defining `forward_window_start` and the holdout.
>
> **One prose edit to two fields. Zero trials. Pre-seal. It never recurs.** Option (a) — ingest
> immediately before sealing — is self-defeating: the terminal bar is then partial, and Validation has
> already ruled (§7) that sealing a bar known in advance to restate manufactures a future A4 event.
> **There is no seal date at which `[2020-01-01, C]` is true. That is the whole finding.** Filed I-213.

---

## 9. WHAT WOULD CHANGE MY MIND, AND WHAT THIS FIRM HAS STOPPED BEING ABLE TO SEE

| # | On what | What would change it |
|---:|---|---|
| 1 | **The DO NOT SEAL verdict** | `k`, `d` and `band` carrying numeric literals in a binding field, and the two `[2020-01-01, C]` sites conformed. **Nothing else.** Both are prose edits against a zero-trial registry. If they land, I withdraw the verdict the same day and say so |
| 2 | **§2.1 — the rule is inert in the tail regime** | A demonstration that `z(t)` remains **above** its trailing baseline through a multi-day basis dislocation. That is measurable on stored funding prints alone, costs no backtest, and would make the objection wrong rather than unanswered. **I expect the opposite and I have pre-registered that expectation here** |
| 3 | **§2.3 — leg (ii)'s exposure match** | C11 returning a measured leg-(ii) false-spare rate at or below 0.10 **and** a demonstration that the 20 worst days are not dominated by 2020-03-12 across both assets. The second is a two-line query and nobody has run it |
| 4 | **§4.2 — the behaviour is occupied by vol-targeting basis desks** | Aggregate short-perp open interest **rising or flat** as funding rises above its trailing baseline. That is the sponsor's own falsifier of escape (c), it has no loader, and building one is cheaper than the family |
| 5 | **§7.5 — throughput** | One logged trial. Any trial. The metric is zero and one measurement moves it |
| 6 | **My own seat** | **If a future memo from this seat attacks only targets the sponsor named in §20's blocker table, that memo is ceremonial and this row is the pre-registered reason why** |

> ### **WHAT THE FIRM HAS STOPPED BEING ABLE TO SEE, IN ONE PARAGRAPH.**
>
> Every seat has read this document a dozen times, and every seat now reads it **as a set of known
> defects with known dispositions** — the dates, the denominators, the classes, the harness facts, the
> nine deferrals. That map is excellent and it is complete for the territory it covers. **What it has
> cost is the ability to read the document as a stranger would: as a specification of a trading rule,
> asking whether the rule is specified.** It is not. Two symbols and a band have no values, and the
> reason nobody saw it is that nobody has read §6.2 cold since 2026-07-28 — every subsequent pass
> entered through a revision block, a dispatch, or an issue number, and none of those point at §6.2.
> **The firm has built seven instruments and pointed all seven at the document's metadata. The defect is
> in its content.**

---

## 10. RANKING — by how much each objection should move the decision

| # | Objection | § | Moves the decision |
|---:|---|---|---|
| **1** | **`k`, `d`, `band` unbound in the sealed text** | 2.2 | **BLOCKS THE SEAL.** One dispatch to repair; permanent after P7 |
| **2** | **The sizing rule is inert in the regime where the tail lives** | 2.1 | **Should move the verdict on the family.** Not seal-blocking; it is a reason to expect KILL, and the KILL is the deliverable |
| **3** | **`[2020-01-01, C]` in two binding fields** | 8 | **Fix in the same pass.** Free, and it never recurs |
| **4** | **§19.1's ADMITTED ground contradicted by Validation's D-6** | 7.3 | **Back to Validation.** Not mine to rule |
| **5** | **Leg (ii): first-moment match, ~6 effective draws, assumed null now post-seal** | 2.3 | Substantial. Degrades the falsifier's decisiveness from 1.3e-4 toward 1.3e-3 or worse |
| **6** | **Escape (c) is "nobody has looked" relocated; its falsifier has no loader** | 4.1–4.2 | Substantial on the investment case, nil on admissibility |
| **7** | **The alpha is turnover and `band` prices it** | 3.1 | Substantial, and it is objection 1 wearing different clothes |
| **8** | **Cost model, battery and tail instrument all blind to the same object** | 3.2 | Real, disclosed by the sponsor, and I add only that the three are one finding |
| **9** | **Revision provenance: seven for seven external** | 7.1–7.2 | **Should move how the firm allocates its next unit**, not this seal |
| **10** | **Throughput = 0; Appendix B #9, not #1** | 7.5 | Addressed to the CIO and the Principal, not to this family |
| **11** | **Haircut base rate too generous for this diffusion channel** | 4.3 | **I would not act on this alone.** Labelled as such |
| **12** | **C12's discharge does not cover the sealed span** | 2.4 | **I checked it and it is clean. I would not act on it and I am not asking anyone to.** Filed for scope only |

---

## 11. ISSUES FILED — I-210 THROUGH I-219

| # | Finding | Sev | Owner |
|---|---|---|---|
| **I-210** | **`k`, `d` and `band` carry no numeric value anywhere in `PREREG-002`, the payload, or the seal block.** The sealed `statement` freezes `w(t) = clip(1.0 − k·max(0, z(t) − d), 0, 1.0)` with two free symbols. §6.2's *"made now, before any measurement"*, §10.5's *"fixed at pre-registration"* and §11.5's *"parameter centres"* each assert a fixing that does not exist. `statement` is class (a) on existence and (c) on content, so **P3, P4 and P7 cannot see a post-seal choice.** `R_strat` is undefined; F-002 legs (i) and (ii) are not computable from the sealed text | **HIGH — BLOCKING ON THE SEAL** | director-of-research → quant-validation |
| **I-211** | **KC-002 clause (b) is a pure function of the unsealed `k` and `d`.** `\|Δw\| > 0.25` iff `k·(z − d) > 0.25`; larger `k` and smaller `d` make the sponsor's own pre-registered expected cause of death easier to survive, and the direction is knowable without running anything. **Strictly worse than I-153: that clause was visible in the text** | **HIGH** | quant-validation |
| **I-212** | **The ±50% grid has no centre.** §10.5 grids `lookback` and `k`; `grid_from_center` requires a centre; §15 runs the grid at step 6, **after** F-002 at steps 2–3. The grid's centre is therefore chosen with F-002's output in hand — **I-029(d) relocated from the lag axis to the parameter axis, in the family whose §5.5 table certifies it committed no such operation** | **MEDIUM** | director-of-research → quant-validation |
| **I-213** | **`C` denotes two different objects — the freeze instant and the in-sample right edge — and R23, R33, R34, R37 and I-097 are five repairs of the instances and none of the cause.** Two binding fields carry `[2020-01-01, C]`; at any seal date that window claims data that is not on disk, and `(B, C]` is a gap that is neither in-sample nor holdout. **Remedy: conform the two fields to "the last settled common bar at the first run." No change to `C`, no Principal act, one prose edit, never recurs** | **MEDIUM** | director-of-research → quant-validation |
| **I-214** | **F-002 leg (ii)'s exposure match is on the first moment while its statistic is an order statistic**, and the tail test's effective sample is market-wide stress episodes (≈6 in 6.6 y), not 20 days × 2 assets — §6.1 records both assets' extremum on **2020-03-12** and §18 declares them one cluster. §17 rank 10 concedes `N_eff` far below 2 for the cross-section and never applies it here. Compounded by **I-202** moving C11's calibration downstream of the seal | **MEDIUM** | director-of-research → quant-validation |
| **I-215** | **§19.1's sole ground for ADMITTED rather than ADMITTED-AS-EXPLORATORY — *"a verdict is reachable"* — is contradicted by D-6 in the same document that issued the verdict.** I-173 / I-186 make the family a permanent INSUFFICIENT-DATA as the document stands, and Validation §10.3(2) calls it *"currently the family's binding constraint."* The two findings were not put next to each other | **MEDIUM** | quant-validation |
| **I-216** | **Persistence escape (c) is escape (a) relocated from the premium axis to the sizing axis, and §4's own rejection of (a) applies verbatim.** Its named falsifier — aggregate short-perp OI falling into rich funding — **is not in `pit.db`, has no loader, and is listed non-blocking.** The marginal supplier at BTC/ETH scale is a vol-targeting basis desk that de-scales into rich funding as a by-product of inventory risk, without reading the signal | **MEDIUM** | director-of-research |
| **I-217** | **C12's cadence discharge covers 4,802 symbol-days through 2026-07-28; the settled sealed span carries 4,828.** I swept the 26 uncovered settled symbol-days this session: **3 prints/day, both symbols, every day — clean, no new K7 trigger** [measured]. Filed so the discharge's scope matches the span. **No action requested** | **LOW-MEDIUM** | head-of-data-infra |
| **I-218** | **None of R-001 … R-007 originated in the sponsor noticing.** Each was triggered by an external measurement, an external ruling, or an explicit dispatch order — the document says so of R-006 itself. **And the near-fatal arrival rate spiked at revisions 4–6 (I-130, I-140, I-153, three HIGHs in 48 hours) rather than declining.** The honest prior on an eighth instrument finding an eighth defect is high, and **I-210 is that eighth** | **MEDIUM** | CIO → Principal |
| **I-219** | **Base rate, reported unprompted. Appendix B #1's metric is undefined at n = 0 Gate 1 verdicts and I make no claim from it; I-025's Opus-by-origin metric has inverted from 100% Principal to effectively 100% Director. The live failure mode is Appendix B #9, not #1: throughput is ZERO.** 28 days, 4 Opus seats, ~200 issues, **0 trials, 0 backtests, 0 verdicts, 0 seals** — and no artifact in three sprints has stated the throughput number the Charter requires stated | **LOW-MEDIUM** | devils-advocate → CIO → Principal |

---

## 12. TO THE PRINCIPAL

**Four items. Only the first needs an act before the seal.**

1. **Do not seal until `k`, `d` and `band` have numbers.** This is the whole of my seal objection. It is
   a prose edit to a document that is unsealed, against a registry holding zero trials, by a seat that has
   made six edits of exactly this class already. **The cost of the repair is one dispatch. The cost of
   not making it is that the family's most consequential parameters are chosen after the freeze, by
   whoever runs step 3, invisibly to `prereg_sha256`, on the same day the grid centre and KC-002 clause
   (b)'s survival are decided.**

2. **The 13-day staleness does not need your ruling.** The CIO put three options to you, one of which
   (redefining `C`) is correctly yours. **None of the three is necessary.** `C` is doing a job it was
   never meant to do; separate the freeze instant from the in-sample right edge in two binding fields and
   the problem does not recur at any seal date. §8 has the wording. **I am declining to escalate
   something that does not require you, which is the same discipline as escalating what does.**

3. **The verdict question at §7.3 is Validation's and I have filed it rather than resolved it.** §19.1's
   ground for ADMITTED is contradicted by D-6 in the verdict's own document. I do not hold Gate
   promotion and I am not asking you to overrule Validation. I am asking that the contradiction be ruled
   on rather than left in two sections of one report.

4. **The throughput number is zero and I am the seat that should have said so sooner.** Twenty-eight
   days, four Opus seats, roughly two hundred issues, and not one measurement of a market. **The firm's
   anti-sycophancy machinery is working — this document is the best artifact here and it got that way by
   being attacked.** What is not working is that the machinery has been pointed at itself. I-210 is real
   and it blocks the seal; it is also the eighth defect found in a document, in a firm that has yet to
   find its first defect in a *hypothesis*, because it has yet to test one.

---

*Devil's Advocate · Castellan Capital · 2026-08-25 · dispatch S3-D-024 · **C3 DISCHARGED.***

*`book/registry.db` read **0 hypotheses / 0 trials / 3 events** on opening and reads 0 / 0 / 3 on
closing. **No hypothesis opened. No registration. No seal. No trial. No backtest. No vault. No registry
write. No commit.** `PREREG-002`, `harness/`, `book/`, every `VALIDATION-*` document and both
`REGISTRATION-PAYLOAD-*` artifacts were read and **not modified** by this seat. Measurements taken this
session were **read-only `COUNT`/`MIN`/`MAX` queries over `book/pit.db` and `book/registry.db`** — funding
print counts per UTC day, funding sign counts, floor-value counts, and calendar spans. **No mean, no
z-score, no return, no correlation, no signal, no P&L, and no number produced outside the engine is
quoted anywhere in this memo as a performance figure.***

*Authored lines: 650 planned. **Delivered within budget.***
