# DIR-RESTATE-001 — PREREG-002's mechanism, restated with I-045 in hand

**Seat:** Director of Research (Seat 2) · **Date:** 2026-08-04
**To:** the Principal · cc CIO, Quant Validation, Devil's Advocate, PM Pod B, Head of Data & Infrastructure, CRO
**Discharges:** D-014 item 3 · D-015 item 3 (first Director unit of Sprint 2) · I-045
**Subject document:** `research/PREREG-002-crypto-funding-basis.md` — **unsealed**, edited by this memo, pre-seal
**Compute:** 1 Opus unit of Sprint 2's 12 · **Trial budget: ZERO.** No backtest run, no new number produced.

**Scope discipline, stated first because A2 binds it.** `book/registry.db` holds **0 families and 0 trials**
[measured — `PREREG-002` §0, re-confirmed at `DATA-INGEST-002` §7]. Under Amendment A2 no number this seat
could produce would be admissible. **This memo therefore produces no new number.** Every figure it uses is a
prior `[measured]` or `[cited]` finding carried forward with its source named. Where an arithmetic
consequence of a change would require a new computation, this memo **bounds it from figures already
measured** rather than computing it, and says so at the point of use.

House rule 6 throughout: **[measured]** = executed against this repository and recorded in a named artifact ·
**[cited]** = named external or internal source · **[inferred]** = reasoned from measured/cited facts ·
**[assumed]** = unverified premise, flagged as such.

---

## 1. THE DEFECT, IN THE DOCUMENT'S OWN VOCABULARY

I-045 states the defect as a data-homogeneity failure in the family's state variable. That is correct and it
is not complete. Named against the document's own clauses, the defect has **three distinct heads**, only one
of which I-045 identifies, and they do not have the same remedy.

### 1.1 Head one — the universe member (I-045 as filed)

**Clause:** §6.1 *Universe*, row **"Secondary, reported separately and never pooled"** → **SOL**; and §7.1
**K4**, selected option **(2)** *"BTC+ETH primary with SOL reported separately."*

**State variable affected:** §7.1 **K1** — *"deviation of realized funding from its own trailing 30-day mean,
in units of that window's standard deviation."*

**The failure.** Binance changed SOLUSDT's funding settlement frequency to 4 hours and raised its Capped
Funding Rate Multiplier from 0.75 to 1, taking the cap to **±2.00%** — roughly **40×** the default ±0.05%
band — announced **2022-11-09 20:00 UTC** [cited — official, `DATA-VERIFY-001` §3.2, source 4]. Three
independent series date the same break:

| Series | Finding | Provenance |
|---|---|---|
| Vendor announcement | settlement frequency shortened, cap widened ~40× to ±2.00%, dated 2022-11-09 | [cited — official, `DATA-VERIFY-001` §3.2] |
| Funding cadence in the firm's own store | 0 of 787 days with >3 prints **before**; 10 of 1,358 **after**; 2022-11-09 itself carries 4; **BTC control 0 before, 0 after** | [measured — I-045] |
| Basis dislocation | SOL **−1,690.34 bps** on 2022-11-09, an order of magnitude beyond anything BTC/ETH show anywhere in the sample | [measured — `DATA-INGEST-002` §4] |

**The two independent cadence measurements reconcile and this is worth stating.** I-045 counts 10 days with
>3 prints strictly after 2022-11-09 plus that date itself at 4 prints = **11**; Ruling 003 §A2 independently
counts **11 of 2,145 days** across the whole series [measured — `VALIDATION-RULING-003` §A2]. 787 + 1 + 1,358
= 2,146 against Ruling 003's 2,145 — agreement to one day. Two measurements taken in different sessions for
different purposes landing on the same integer is a genuine cross-check, not a coincidence.

**Why K1 breaks on it.** K1 is a deviation from a trailing 30-day baseline, and a deviation is invariant to an
additive constant — so the state variable is **not** broken merely by funding being larger or smaller on one
side of the break. It is broken because the **generating process's scale parameter changed**: a clamp band
40× wider and a settlement interval shortened change the *dispersion* of the printed series, and the z-score's
denominator is that dispersion. "Two standard deviations rich" measured against a ±0.05%-clamped, 3-print/day
process and "two standard deviations rich" measured against a ±2.00%-clamped, up-to-12-print/day process are
**not the same operative state**, and the sizing rule `w(t) = clip(1 − k·max(0, z(t) − d), 0, 1)` maps them to
the same notional. That is the homogeneity defect, stated in the sizing rule's own terms.

### 1.2 Head two — the aggregation clause, which is a specification error and is *not* about SOL

**Clause:** §6.2 *Bar granularity* — *"**Daily, UTC.** Funding aggregated as **the sum of the day's three 8h
prints**"*; identically in §7.1 **K6** and, binding, in the §21 seal block's `universe` field: *"K6 BAR
GRANULARITY. Chosen: DAILY UTC, funding aggregated as **the sum of the day's three prints**."*

**The failure.** That clause asserts a cadence constant. The cadence constant is **measured false** — on 11 of
2,145 SOL days the count is not three, reaching **12 in one day** [measured — `VALIDATION-RULING-003` §A2] —
and Validation has already specified the control that removes it: `pit_funding_panel` returns the **exact
arithmetic sum of realized prints falling in each bar's window**, with *"no annualization, no cadence
constant, no mean, no `periods_per_year`"*, and acceptance test **T-9** exists specifically to fail any
implementation that multiplies by a fixed prints-per-day constant [cited — `VALIDATION-RULING-003` §3.2, §4
T-9].

**So the harness path is already correct and the pre-registration's prose is not.** If sealed as written, P7
freezes a binding field whose text contradicts the sanctioned implementation. On a SOL-cadence day the
executed accrual and the sealed specification disagree, and there is no admissible way to reconcile them
afterwards.

**This head does not go away if SOL is dropped, and that is the finding the Principal could not see from
outside the document.** Binance's own announcement states, verbatim, *"there may be further adjustments to the
funding rate settlement frequency... there will be no further announcement on such adjustments"* [cited —
official, `DATA-VERIFY-001` §3.2]. The vendor has therefore **reserved the right to change the cadence of any
symbol, including BTC and ETH, without notice.** PREREG-002's holdout regime is **FORWARD** (§11.2) and its
kill condition KC-002 is computed over `[C, C+187 days]`. A sealed clause that assumes three prints per day is
a live specification defect **on the primary universe, in the forward window, which is the window that
decides the family.** Dropping SOL fixes the historical instance and leaves the forward instance untouched.

### 1.3 Head three — the mechanism's central persistence claim, which is materially wrong as written

This head is not in I-045. It comes from reading `DATA-VERIFY-001` §5 against §3 of the pre-registration, and
it is the reason D-014 item 3 called for a *restatement* rather than an addition.

**Clause:** §3.3, this seat's stated prior, quoted from the document:

> *"The ~11%/yr baseline is **approximately the market-clearing price** of three risks that a carry supplier
> genuinely bears, and there is no prior reason to expect it to exceed them."*

and §3.4: *"Funding is a **direct observable** of long-side positioning crowding."*

**The failure.** Binance's documented formula is
`F = [P_avg + clamp(interest − P_avg, −0.05%, +0.05%)] / (8/N)` with `interest` fixed at **0.01% per 8h
interval** and the clamp band ±0.05%, so that whenever the premium sits inside **[−4 bp, +6 bp]**, `F` equals
the interest rate **exactly**, regardless of the premium's value [cited — official, `DATA-VERIFY-001` §1.1].
Measured against the firm's own store: the in-band subset's mean funding is **0.986 bp (BTC)** and **1.114 bp
(ETH)** — essentially exactly the 1.00 bp interest rate — while the underlying premium the basis proxy is
attempting to measure averages **slightly negative** (mean basis −1.58 bp BTC, −0.95 bp ETH) [measured —
`DATA-VERIFY-001` §5.2; `DATA-INGEST-002` §4].

**Therefore the ~11%/yr baseline is not a market-clearing price at all. It is an administered constant set by
the exchange**, transferred from longs to shorts by contract rule on every day the premium falls inside a
±5 bp band, whether the market is crowded or empty. The market-determined component — the premium — averages
negative over this sample. Roughly **35% of prints sit at the floor** [measured — `DATA-VERIFY-001` §5.2:
64.9–65.4% *off* the floor].

**Three consequences, each of which changes what the document claims:**

1. **§3.3's equality is unsupported and must be withdrawn.** "Approximately the market-clearing price of the
   tail" is an assertion about a price that is not being set by the market on the majority-adjacent subset of
   days. The firm has no basis for saying the administered rate is above, at, or below the risk price.
   **Replacing an unverifiable equality with "unknown" is the honest move, and the section's *conclusion*
   survives it** — the unconditioned carry is Factor P&L under Charter §5.4 whether or not it is fairly
   priced, so §3.3's argument gets weaker premises and the same result. That is a strictly better argument.

2. **§3.4's "direct observable" is over-strong. The correct word is *censored*.** Realized funding is a
   censored observation of the premium: censored to the interest rate whenever `P_avg ∈ [−4bp, +6bp]`.
   `DATA-VERIFY-001` §6.1 puts this as funding being *"less sensitive to genuine crowding"* inside the band;
   censoring is the precise statement and it has a consequence the softer wording hides — **the trailing
   30-day mean and standard deviation that K1 normalizes by are moments of a censored series**, so `z(t)` is a
   z-score of a censored variable and both of its moments are biased relative to the premium's.

3. **But the censoring argues *for* K1, not against it, and the reason is structural.** Because funding can
   only depart from the floor when the premium escapes the band, **the state variable's "rich funding" state
   is by construction the state "premium has broken the clamp upward."** The conditioning fires precisely when
   crowding is severe enough to overwhelm the administered rate. That is a *stronger* mechanism than the one
   §3.4 currently states, and it is falsifiable in the same terms. `DATA-VERIFY-001` §6.1 reaches the same
   conclusion — *"no change to K1 is indicated"* — by a different route, and this seat agrees with it
   [cited — `DATA-VERIFY-001` §6.1].

**Head three is a mechanism restatement, not a footnote, and it is not the disclosure-only handling the
Principal ruled out.** It withdraws a stated prior, replaces a claimed observable with a censored one, and —
at §5 below — changes a pre-registered expectation about which falsifier leg is most likely to fire. A footnote
does none of those things.

---

## 2. THE FOUR TESTS EVERY CANDIDATE REMEDY IS PUT TO

Per the dispatch, each candidate is scored on four axes. They are not equally weighted and this seat says
which dominates before scoring rather than after.

| Test | Why it matters here |
|---|---|
| **T-A · Does it preserve the family's economic claim?** | The claim is about *conditioning*, not about carry. A remedy that alters what `w(t)` responds to is a different hypothesis. |
| **T-B · Does it cost new `N`?** | §7.2's pre-commitment rule makes a menu-declared, pre-measurement, binding choice contribute **1**. Registry is **0/0** [measured], so nothing has been selected on a result and every change made now is genuinely pre-measurement. |
| **T-C · Does it survive P7 freezing?** | P7 freezes the document permanently. A remedy that is *correct today but under-specified for the forward window* is the worst outcome available, because it cannot be repaired afterwards. |
| **T-D · Does it create a new researcher degree of freedom?** | **This is the dominating test.** The entire value proposition of §7 is that this family has no free knobs. A remedy that fixes a homogeneity defect by installing a tunable parameter has made the document worse while appearing to make it better. |

---

## 3. THE CANDIDATES, EVALUATED

### 3.1 Candidate (a) — per-contract time-varying documented parameters

*Encode, per contract, the documented clamp cap / settlement interval / interest rate as a time-varying table,
and normalize the state variable against the parameters in force (e.g. funding as a fraction of the prevailing
cap, or converted to an 8-hour equivalent).*

| Test | Verdict |
|---|---|
| **T-A** | **Fails.** This changes K1's definition. K1's declared menu of 10 contains no "documented-parameter-normalized funding deviation" — it would be an eleventh option, and the strategy would be conditioning on a transformed variable rather than on the cash flow it receives. |
| **T-B** | Would contribute **+1** if declared now as a new choice pre-measurement; or, if handled as an addition to K1's menu, it enlarges K1's menu from 10 to 11 and inflates the §7.3 counterfactual. Not the binding objection. |
| **T-C** | **Fails hard.** See below. |
| **T-D** | **Fails.** The table's contents are not fully documented, so its unpublished entries would be researcher-constructed. |

> **The decisive objection, and it is a citation the firm has already put on its own record: the required data
> does not exist and Binance says so itself.** The 2022-11-09 announcement states verbatim *"there may be
> further adjustments to the funding rate settlement frequency... there will be no further announcement on
> such adjustments"* [cited — official, `DATA-VERIFY-001` §3.2], and `DATA-VERIFY-001` §7(4) records that a
> full historical reconstruction *"would require either an announcement-archive crawl (not performed) or a
> historical `fundingInfo`-equivalent time series (not known to be published)."* The live `fundingInfo`
> endpoint returns **today's snapshot only** [measured — `DATA-VERIFY-001` §2].
>
> **A time-varying parameter table can therefore be populated for the break's *start* and for nothing else.**
> Its remaining entries would be inferred from the very series they are meant to correct — which is
> **I-029(d) transposed a second time**: setting a control's parameters from the data the control exists to
> protect. I-029 is already filed against this seat for exactly that operation on a lag axis, and F-002 §5.5(d)
> repairs a second instance of it on a size axis. Installing a third instance, in the remedy for a data
> defect, would be the clearest possible evidence that the firm has not learned from its own issue log.

**Verdict on (a): REJECTED. It is the remedy that best matches the diagnosis and the one the firm cannot
execute.** This is worth stating plainly because (a) is the intellectually correct answer in a world with
published parameter history, and the firm does not live in that world. Recording *why* it is unavailable is
more useful than recording that it was not chosen.

### 3.2 Candidate (b) — a declared break control

*Declare 2022-11-09 a structural break and control for it — a partition, a transition-window exclusion, or a
break dummy.*

| Test | Verdict |
|---|---|
| **T-A** | Neutral. BTC/ETH untouched; SOL partitioned. |
| **T-B** | Costs **+1** (a new choice) or changes K3's selection from *"exclude nothing"*, which is a menu move with a counterfactual cost. Not the binding objection. |
| **T-C** | **Fails.** Freezes an under-determined control. |
| **T-D** | **FAILS, and this is the killing objection.** |

> **A break control requires two dates. The firm can cite one.**
>
> The break's **start** is documented and dated: 2022-11-09 [cited — official]. Its **end is not documented at
> all**, and the vendor has stated in the same announcement that it will not be [cited — official,
> `DATA-VERIFY-001` §3.2]. The live endpoint shows SOL back on default parameters today **without any
> corresponding "reverted" announcement** [measured — `DATA-VERIFY-001` §2, §3.2].
>
> So the control's closing boundary would have to be set from the data. The obvious candidate is the measured
> cadence revert — prints return to 3/day by 2022-12-01 [measured — I-045]. **But cadence and clamp cap are two
> different parameters that were changed in the same announcement, and the cadence reverting tells the firm
> nothing about when the ±2.00% cap reverted.** Choosing the cadence revert as the window end would be
> selecting a control boundary from a proxy for the thing being controlled, and choosing anything else would
> be choosing a number.
>
> **A control with a free endpoint inside a pre-registration whose entire claim is that it has no free
> parameters is not a control. It is a knob with a control's name on it, and P7 would freeze it.**

**Verdict on (b): REJECTED**, on T-D, decisively. Not because a break control is the wrong instrument in
general — it is the right instrument when both boundaries are observable — but because here it converts a
documented data defect into an undocumented researcher choice.

### 3.3 Candidate (c) — drop SOL under the existing universe menu

*Move K4's selection from option (2) — "BTC+ETH primary with SOL reported separately" — to option **(4)** —
"BTC+ETH only, SOL discarded entirely."*

| Test | Verdict |
|---|---|
| **T-A** | **Passes.** SOL was never in the primary universe. F-002 is computed *"on the common primary-universe index"* (§5.2 leg 0) — BTC and ETH. No leg of the falsifier ever read SOL. The economic claim is untouched. |
| **T-B** | **Passes, at zero cost.** Option (4) is **already on K4's declared menu of 5** [measured — `PREREG-002` §7.1]. The menu does not grow, the selection moves within it, and under §7.2's pre-commitment rule K4 continues to contribute **1**. The §7.3 counterfactual product `10 × 3 × 9 × 5 × 5 × 4 = 27,000` is unchanged. |
| **T-C** | **Passes.** A within-menu selection, made pre-measurement against an empty registry, frozen at seal, with a dated documented reason on the face of the record. |
| **T-D** | **Passes, and uniquely: it is the only candidate that *removes* degrees of freedom rather than adding one.** It deletes SOL's separate span, its separate `N` accounting, its separate verdict, and its separate reporting obligation. |

**Two objections to (c) that must be answered rather than waved past.**

**Objection 1 — "SOL's 2022-11-10 is the sample's only realization of the fat left tail."** Validation says so
directly: inverting realized funding on SOL makes the worst-20-day mean **4.5× better (−0.02192 → −0.00487)**,
*"deleting the 2022-11-10 event that is the sample's only realization of the fat left tail Charter Seat 7 warns
about"* [measured — `VALIDATION-RULING-003` §A3]. Dropping SOL appears to cost the family its only tail
observation.

**It does not, for two independent reasons.**

- **The traded sample never contained it.** F-002 leg (ii) — the tail test, on the 20 worst daily net returns —
  is computed on the primary universe, which is BTC and ETH. SOL's tail was outside the falsifier before this
  memo and stays outside it after. **Dropping SOL makes explicit a limitation the document already had rather
  than creating one.**
- **The observation is not usable as evidence about the forward tail anyway.** SOL's 2022-11-10 accrual of
  **−0.17166 on a −1.0 perp notional** [measured — `VALIDATION-RULING-003` T-9] is a magnitude the default
  ±0.05% clamp cannot produce; it required the ±2.00% cap and the shortened interval then in force [inferred,
  from cited — `DATA-VERIFY-001` §3.2]. **It is a realization of a contract the symbol no longer runs under.**
  Carrying it forward as evidence about the tail this family will face is precisely the homogeneity defect
  I-045 names, applied to the tail instead of the state variable.

**But it does have a real cost, which this memo records rather than absorbs.** The primary universe's largest
in-sample basis excursions are **−73.65 bps (BTC)** and **−102.95 bps (ETH)**, both on 2020-03-12 [measured —
`DATA-INGEST-002` §4] — roughly **an order of magnitude** milder than SOL's. **F-002 leg (ii) is therefore a
tail test on a mild tail, and leg (ii) surviving is weaker evidence of tail reduction than the leg's
construction implies.** That is now written into the pre-registration as a stated limitation (§5 below, edit
R12) rather than discovered when the result arrives.

**Objection 2 — "does dropping SOL break Ruling 003's acceptance suite?"** No. **T-9 is a fixture over stored
data, not over the traded universe** [cited — `VALIDATION-RULING-003` §4 T-9]. SOL's prints remain in
`book/pit.db` and its perp OHLCV remains ingested [measured — `DATA-INGEST-002` §2]. The test that guards
against a cadence constant continues to run on the window that most needs guarding. Stated explicitly so the
universe change is not read as weakening the control.

**Verdict on (c): ACCEPTED**, and it is the cleanest move available under the document's own rules.

### 3.4 Candidate (d) — the thing (a), (b) and (c) all miss, which this seat raises

**None of (a), (b) or (c) touches head two (§1.2), and head two is the one that binds the forward window.**

All three candidates are treatments of SOL's *history*. The sealed clause *"funding aggregated as the sum of
the day's three prints"* is a **specification error on the primary universe** that survives every one of them,
and it is exposed in the forward window because the vendor has explicitly reserved the right to change any
symbol's cadence without notice [cited — official, `DATA-VERIFY-001` §3.2].

**(d) has two parts, and they are of different kinds.**

**(d1) — the aggregation repair. A defect fix, not a design change, costing nothing.**
Replace the cadence-assuming clause with Ruling 003's already-specified construction: *the exact arithmetic sum
of all realized funding prints whose `event_time` falls in the bar's window, left-open right-closed, with no
assumed cadence* [cited — `VALIDATION-RULING-003` §3.2, alignment rule; §4 T-9]. This **conforms the
pre-registration's prose to a control Validation has already ruled and the harness already implements.** It
adds no choice, contributes no `N`, and removes a contradiction between the sealed text and the sanctioned
code path. It should happen regardless of what is decided about SOL.

**(d2) — a pre-declared parameter-change protocol, `K7`. A genuine new conditioning choice, and it costs `N`.**
The forward-window exposure needs a rule that exists *before* the event, because P3 refuses a post-hoc one and
§7.2's escalation would open a successor family at `n_inherited ≥ menu size × final n_trials`. Declared now,
pre-measurement, against an empty registry, with its full menu:

> **K7 · TREATMENT OF A DOCUMENTED FUNDING-PARAMETER CHANGE ON A UNIVERSE SYMBOL.**
> **Selected — option (1):** on any documented change to the funding formula or to a universe symbol's
> per-contract funding parameters (settlement interval, clamp cap, or interest rate), **that symbol's state
> variable `z(t)` is INSUFFICIENT-DATA for the declared trailing-baseline length — 30 days — beginning on the
> change date**, during which the symbol is held at **benchmark weight `w = 1.0`**; the change is filed to the
> Issue Log by Seat 9 and escalated to Validation.
> **Menu of 5:** (1) ← SELECTED; (2) exclude the affected symbol's bars for that window; (3) exclude the
> affected symbol for the whole post-change period; (4) drop the affected symbol from the universe on the
> change date; (5) no special treatment — pool across the change.

**Four properties that make option (1) the right selection and not merely a selection:**

1. **No free parameter.** The window length is the **already-declared 30-day K1 lookback**, not a new number.
   It is exactly the interval over which the trailing baseline mixes two generating processes, so it is
   derived rather than chosen.
2. **It excludes nothing, so K3 is preserved exactly.** K3 remains *"exclude nothing"* — the bars are traded,
   the returns are counted, only the *conditioning input* is declared unavailable. Options (2), (3) and (4)
   would all have required changing K3 and were rejected for that reason among others.
3. **The default is the conservative direction.** Holding `w = 1.0` reverts the strategy to the benchmark, so
   the family **forgoes** any claimed benefit over the affected interval rather than claiming one on a
   corrupted input.
4. **Its trigger is mechanical, not interpretive.** "A documented change to the formula or parameters" is
   observable; "a change that materially alters the generating process" would require a judgment at run time,
   which is a degree of freedom. **Mechanical and slightly over-inclusive is the correct trade in a
   pre-registration.**

**K7 does real in-sample work, and its one known in-sample trigger is named by date now.** The firm-wide
formula change of **2025-09-18** — introducing the `/(8/N)` divisor — is a documented change to the funding
formula [cited — official, `DATA-VERIFY-001` §3.1]. Its arithmetic effect on BTC/ETH is **nil while both
remain on the 8-hour default** (`8/8 = 1`) [cited — same]. Under a mechanical trigger it **fires anyway**, and
this seat declares that it does: **BTC and ETH carry `z(t)` = INSUFFICIENT-DATA and `w = 1.0` for the 30 days
from 2025-09-18.** Naming the date pre-seal removes the only discretion the rule would otherwise have.

**Verdict on (d): ACCEPTED, both parts.** (d1) is mandatory and free. (d2) is the only part of this memo that
costs anything, and §4 accounts for it exactly.

---

## 4. THE RECOMMENDATION

> ### **Adopt (c) + (d): move K4 within its declared menu from "SOL secondary" to "BTC+ETH only, SOL discarded"; repair the cadence-assuming aggregation clause to Ruling 003's cadence-free construction; declare a new conditioning choice K7 governing documented funding-parameter changes with its trailing-baseline window pinned to the already-declared 30-day lookback; and restate §3's mechanism to withdraw the unsupported market-clearing-price claim and replace "funding is a direct observable of crowding" with the censored-observation form.**
>
> **Reject (a) — the parameter history it needs is not published, and Binance says so itself.**
> **Reject (b) — its closing boundary would have to be chosen from the data, installing a free knob in a document whose entire claim is that it has none.**

### 4.1 Confidence, stated separately per component because they are not equally certain

| Component | Confidence | Basis |
|---|---|---|
| **Reject (a)** | **HIGH** | Rests on a citation, not a judgment: the vendor states it does not announce subsequent adjustments, and no historical parameter series is known to be published [cited — official, `DATA-VERIFY-001` §3.2, §7(4)]. |
| **Reject (b)** | **HIGH** | The missing end date is a fact about the record, not an opinion. The alternative — setting the boundary from the measured cadence revert — is a documented instance of the I-029(d) operation. |
| **Adopt (c)** | **HIGH** | Within-menu, zero-`N`, pre-measurement against an empty registry, and it is the only candidate that reduces degrees of freedom. Both objections to it are answered from measured findings. |
| **Adopt (d1) — aggregation repair** | **HIGH** | The clause is measured false and Validation has already specified its replacement. There is no live question here. |
| **Adopt (d2) — K7** | **MODERATE** | This is the judgment call in the memo. The forward exposure is real and cited, but it is an exposure to an event that has **never occurred on BTC or ETH in 2,145 measured days** [measured — I-045 BTC control]. K7 buys insurance against a low-probability event at a cost of 1 unit of `N`. This seat judges the trade worth it because P7 makes the uninsured case unrepairable; a reasonable seat could decline it. |
| **Adopt head-three mechanism restatement** | **HIGH on the withdrawal, MODERATE on the strengthening** | Withdrawing "approximately the market-clearing price" is forced by a measured finding. The claim that censoring *strengthens* K1 — that the conditioning fires precisely when crowding breaks the clamp — is [inferred] from the formula's structure and is not measured. It is labelled as inferred in the edited document. |

### 4.2 `N` ACCOUNTING — explicit, per the dispatch

**Menu sizes, before and after.** No menu changes size. K4's selection moves **within** its existing menu.
K7 is a **new** choice with a **new** menu.

| Choice | Menu size before | Menu size after | Selection before | Selection after |
|---|---:|---:|---|---|
| K1 state variable | 10 | **10** | (2) funding deviation | (2) — **unchanged** |
| K2 direction | 3 | **3** | (1) de-scale | (1) — unchanged |
| K3 period exclusions | 9 | **9** | (0) exclude nothing | (0) — **unchanged, and K7 was designed to keep it so** |
| K4 asset universe | 5 | **5** | (2) BTC+ETH primary, SOL secondary | **(4) BTC+ETH only, SOL discarded** |
| K5 venue | 5 | **5** | (1) binance | (1) — unchanged |
| K6 bar granularity | 4 | **4** | (1) daily | (1) — unchanged; **its aggregation text is repaired, which is not a selection** |
| **K7 parameter-change protocol** | — | **5 (new)** | — | **(1) INSUFFICIENT-DATA for the 30-day baseline, held at benchmark weight** |

**The multiple-testing count at the ceiling does not move.**

```
BEFORE:  N_conditioning = 6   trial budget = 80   ceiling N = 86
AFTER:   N_conditioning = 7   trial budget = 79   ceiling N = 86
```

- `N_conditioning` rises **6 → 7** (K7).
- The trial budget falls **80 → 79**, by striking the *"SOL on its own span"* item from §10.5's pre-grid
  diagnostics line (≤8 → ≤7). The work is genuinely removed, not re-labelled.
- **Ceiling `N` is 86 in both accountings.** §10.4's measured `MinBTL(86, SR 1.0) = 6.14 years` against
  **6.571 years** available, with **0.43 years of margin**, therefore **stands unedited and no new number is
  produced by this memo.**
- The **absolute admissible ceiling of `N = 110`** (§10.4) is untouched.

> **This seat flags its own convenience rather than leaving it to be noticed.** Reducing the budget by exactly
> **1** — rather than 0 or 2 — was chosen *in part* because it preserves an already-measured `MinBTL` and
> avoids producing a new number under A2 against a 0/0 registry [stated as a judgment]. It is also
> independently justified: the struck line was one of five items sharing a ≤8 cap, so −1 is the proportionate
> reduction and −2 would not be. **Both reasons are true and the first is the more convenient one, which is
> why it is written down.** If Validation prefers the budget held at 80, the consequence is `ceiling N = 87`
> and `MinBTL(87, SR 1.0)` must be computed by Validation or Pod B before sealing; it is **bounded by already
> measured figures** in `[6.14, 6.574]` years — `MinBTL` being monotone increasing in `N`, with `MinBTL(86) =
> 6.14` and `MinBTL(110) = 6.574` both measured at §10.4 — so **the Gate 1 length criterion clears either
> way** and the margin is between 0.00 and 0.43 years.

**The §7.3 counterfactual grows, and the conclusion it supports strengthens.** Had K1–K7 been chosen after
seeing results, the honest product becomes `10 × 3 × 9 × 5 × 5 × 4 × 5 = 135,000` [arithmetic on declared menu
sizes]. `MinBTL` is monotone increasing in `N`, so the measured `MinBTL(27,000) = 16.79 years` against 6.571
available is now a **lower bound** on the counterfactual death sentence. **No new number is computed and none
is needed** — the conclusion was already fatal and is more so.

### 4.3 What evidence would change this recommendation

| # | Component | What would change it |
|---:|---|---|
| 1 | **Reject (a)** | A published, dated, per-contract historical parameter series — an `fundingInfo`-equivalent time series, or a completed announcement-archive crawl establishing the ±2.00% cap's **revert date** for SOLUSDT with a citation. That single date is the whole difference between (a)/(b) being executable and not. If Seat 9 finds it, **(b) becomes the better answer than (c)**, because it would let the firm keep SOL's cross-section and its tail observation under a fully documented control. |
| 2 | **Adopt (c)** | Evidence that BTC or ETH also carries an undocumented parameter change inside the sample. That would not save SOL — it would mean the *primary* universe has the defect too, and the correct response would be to escalate to Validation for an admissibility ruling on the whole family rather than to trim the universe. **This is why C12 (§6) is blocking.** |
| 3 | **Adopt (d2) — K7** | A Validation ruling that a data-validity rule triggered by a vendor's documented act is not a conditioning choice and contributes **0**, not 1. This seat took the conservative reading deliberately — D-009 records that erring low on `N` is the sycophantic direction — and would accept a ruling either way. If it contributes 0, `N_conditioning` returns to 6 and the budget should return to 80. |
| 4 | **The censoring restatement (head three)** | Ingestion of Binance's true premium-index history via `premiumIndexKlines`, which `DATA-VERIFY-001` §6.3 names as available and not wired into `castellan.loaders`. That series would make the censoring **measurable** rather than inferred from the formula, and would additionally let a successor family condition on the *uncensored* premium — K1 option (7)-adjacent, and a genuinely different hypothesis. **Not on this family's critical path and not proposed for it.** |
| 5 | **The whole disposition** | A Validation ruling that a within-menu selection change made pre-measurement nonetheless contributes the menu size. `PREREG-002` §22 item 2 already names this as the single ruling that most changes the document; it applies to K4's move as much as to the original choices. If that is the ruling, this family's honest `N` is in the tens of thousands and it is dead on arithmetic, and this seat would write the KILL memo the same day. |

---

## 5. THE EDITS MADE TO `PREREG-002`

All are pre-seal, against a registry holding **0 families and 0 trials** [measured]. Every changed clause is
struck-and-replaced in place with an `[Rn · 2026-08-04]` marker; **nothing was silently rewritten**, and the
revision block at the head of the document indexes all seven.

| # | Clauses touched | Change |
|---|---|---|
| **R1** | §3.3 · §21 `mechanism` | **Withdrew** *"the ~11%/yr baseline is approximately the market-clearing price."* Replaced with the administered-constant decomposition. **Explicitly re-derived the surviving conclusion on its new, weaker premises** rather than leaving it standing unexplained. |
| **R2** | §3.4 · §21 `mechanism` | *"Direct observable"* → **censored observation**, with the consequence for K1's moments stated and the [inferred] argument that censoring *strengthens* K1 labelled as inferred. |
| **R3** | §6.1 · §7.1 K4 · §7.4 · §9.1 S1 · §10.4 · §10.5 · §12.4 · §15 step 5 · §17 #10 · §21 `universe`, `success_criteria`, vault block · §22 #9 | **SOL dropped.** K4 moves within its declared menu, (2) → (4). Both objections answered on the face of the document; the one genuine cost — a two-asset cross-section and a mild in-sample tail — written in as a limitation. |
| **R4** | §6.2 · §7.1 K6 · §21 `universe` | **Cadence constant deleted**, replaced by Ruling 003's exact-arithmetic-sum construction. Marked as a defect repair and explicitly flagged as *not* SOL-specific. |
| **R5** | §7.1 (new K7 row) · new §7.1.1 · §7.2 · §7.3 · §7.4 · §17 #12 · §20 C12 · §21 `universe` · §22 #10 | **K7 declared** with its menu of 5, its four justifying properties, and its **one in-sample trigger named by date (2025-09-18)**. |
| **R6** | §10.1 · §10.3 · §10.5 · §21 `success_criteria`, `trial_budget` | `N_conditioning` 6 → 7; budget 80 → 79; **ceiling `N` = 86 unchanged**; the convenience in choosing −1 disclosed. |
| **R7** | §5.3 · §14.2 · §17 #11 · §19.3 · §22 #11 | Pre-registered expectations sharpened **against the family**: leg (iii) declared near-worthless, leg (ii) declared to be testing a mild tail, and **KC-002 clause (b) promoted to leading cause of death with the clamp as its named mechanism**. |

**One structural decision worth naming: the declared menus were not edited.** K1 option (8) still reads
*"cross-asset funding dispersion across BTC/ETH/SOL"* and K4 option (2) still names SOL. **A menu records the
alternatives available at the moment of choosing; retroactively editing one to match a later universe would
destroy the only property that makes declaring it worth anything.** The menus are the historical record, the
selections are the specification, and only selections moved.

---

## 6. SEAL-READINESS

> ### **The I-045 defect is closed. The document is NOT seal-ready, and the binding blockers are not I-045's — including one this revision itself created.**

| Blocker | Status | Owner |
|---|---|---|
| **C12 · in-sample cadence sweep on BTC and ETH** | **OPEN — BLOCKING. Created by this revision.** K7 cannot be sealed while the primary universe's cadence homogeneity is *asserted rather than measured*: I-045's control covers **BTC only**, and only in the `>3 prints` direction, so a cadence **lengthening** was never tested and **ETH was never measured at all**. Sealing K7 on an unverified homogeneity claim would be the I-045 defect committed inside its own remedy. **Row-count query, not a trial** — same class as §0's diagnostics and as I-045's own measurement. Fraction of a Sonnet unit. | Seat 9 → Validation |
| **C2 · Gate 0 intake verdict on PREREG-002** | **OPEN — BLOCKING.** None exists. `VALIDATION-RULING-003` §7.2 states expressly that it is a cost-model specification and **must not be read or cited as an intake verdict**. | Validation |
| **C11 · leg-(ii) null calibration** | **OPEN — BLOCKING.** Required measured before sealing [cited — `VALIDATION-RULING-003` §6.6]. ≤2 trials. | DoR on Validation's requirement |
| **C7 · KC-002 signed · C8 · seal and vault same session/UTC day** | **OPEN — BLOCKING**, executional. | Pod B / Principal |
| **C3 · Red-Team Memo** | **OPEN.** Blocking on Gate 1. | Devil's Advocate |
| **C1 · funding-cost repair** | **DISCHARGED as a specification**; **implementation open as I-034**, closing only when the 19 acceptance tests plus the existing suite are green. Ruling 003 makes the ordering binding: **repair green → seal → F-002**, because the sponsor's own E2 adoption forbids re-running F-002 after the repair. | Seat 9 |
| **C9 · perp OHLCV** | **CLOSED** [measured — `DATA-INGEST-002` §2]. | — |

**This seat says plainly that it is proposing a blocker of its own making and is not apologizing for it.**
D-015 records the Principal's reading — *"the ceiling binding at the seal is the control functioning; the seal
that didn't happen this week is a seal that would have frozen two defects permanently."* C12 is that
principle applied one level deeper: **a remedy for an unverified-homogeneity defect that itself rests on an
unverified homogeneity claim is not a remedy.** The cost of finding out is a fraction of a Sonnet unit; the
cost of being wrong is permanent under P7.

### 6.1 What this memo did NOT resolve, stated so it is not assumed resolved

- **Whether K7 contributes 1 or 0 to `N_conditioning`.** Declared at 1, conservatively. **Validation's call.**
- **Whether the K4 within-menu move is genuinely free.** This seat argues it is, from three checkable facts
  (documented vendor cause, zero SOL statistics ever computed, destination already on the menu). **Validation's
  call, and `PREREG-002` §22 item 2 already names the ruling that would reverse it.**
- **Whether the 2025-09-18 firm-wide formula change should trigger K7 for BTC/ETH given that its arithmetic
  effect on them is nil.** This seat declared that it fires, on the ground that a mechanical trigger is worth
  more than a correct one that requires a run-time judgment. **A reasonable seat could rule otherwise, and the
  cost of this seat's choice is ~30 bars of conditioning forgone in the conservative direction.**
- **Anything requiring a number.** Trial budget for this dispatch was zero and the registry is untouched.

---

# ADDENDUM — REVISION R-002 · 2026-08-05 · PRE-SEAL

**Dispatch:** S2-D-010 · **Compute:** 1 Opus unit · **Trial budget: ZERO.**
**Registry state at open and at close: `book/registry.db` — 0 hypotheses, 0 trials** [measured — `SELECT COUNT(*)`, this session]. **No number was computed. No harness code was touched. Nothing was sealed and nothing was committed.**

## 7. WHAT R-002 CHANGED IN `PREREG-002`, AND WHY

R-001 was occasioned by a defect in the family's own data (I-045). **R-002 is occasioned entirely by findings made outside this seat and pointed at it** — Validation's `RULING-004`, the Principal's approval of I-050, Seat 9's `DATA-VERIFY-002` — and its honest one-line summary is: **three of the four repairs make the document worse-looking and none of them makes it wrong.**

### 7.1 R8 — the admissible ceiling is 109, not 110, and the mislabel was internal

**The change.** `VALIDATION-RULING-004` §2.2 computes, by bisection, the maximum total `N` satisfying `MinBTL(N, 1.0) ≤ 6.571 years` and returns **109**; §12 records the correction against this document's stated 110 [cited]. `PREREG-002` §10.4's table is corrected, the `N = 110` row is re-verdicted **FAILS**, and every downstream hard stop moves 110 → 109 (§1, §10.5, §18, §19.2, §21).

**What moves and what does not — the question the dispatch pressed, answered in both directions.**

| Quantity | Before | After | Moves? |
|---|---:|---:|---|
| Declared ceiling `N` (budget 79 + conditioning 7) | 86 | **86** | No |
| `MinBTL(86, SR 1.0)` | 6.14 yr | **6.14 yr** | No |
| **Margin at the declared ceiling** — R6's figure | **0.43 yr** | **0.43 yr** | **NO** |
| Absolute admissible ceiling | 110 | **109** | Yes, by one |
| **Unused headroom, declared → absolute** | **24 trials** | **23 trials** | **Yes — this is the margin that shrank** |

**`109 − 86 = 23`** [arithmetic on two integers already `[cited]`/`[measured]`; no `castellan.stats` call, no market data].

**This seat considered and rejected reporting the correction as a narrowing of R6's margin.** It is not one. 86 < 109, so the correction does not reach `MinBTL(86)` at all, and presenting a one-trial change to a ceiling the family does not intend to approach as though it were a change to the criterion the family intends to clear would be **theatre in the pessimistic direction** — which is a defect of the same kind as theatre in the optimistic direction and is not made acceptable by being uncomfortable. **What genuinely shrank is the family's room to be wrong about its own budget, and that is what is written.**

**The part worth more than the number.** `MinBTL(110) = 6.574` was **already `[measured]` in this document**, against 6.571 available. The row's verdict cell nevertheless read *"exactly at the span — zero margin."* **6.574 > 6.571.** The correction was available inside the document, in the permissive direction, and required no external input — Validation found it by reading this document's own table more carefully than its author had. That is recorded in `PREREG-002` §10.4 in those terms, because **a correction absorbed without saying it could have been caught internally is how the same class of defect survives**.

**R8(c), incidental.** Three clauses still carried the superseded trial budget `80` after R6 moved it to `79` (§1's recommendation box, §18, §19.2). Conformed, disclosed, not silently fixed.

### 7.2 R9 — I-053, and whether the escalation rule was repairable at the document level

**The finding, stated precisely, because "unexecutable" understates it.** §7.2's binding escalation rule had **three** defects, of which the dispatch named one.

**(i) Scope.** The rule read *K1–K6*. R5 declared **K7** and R6 discounted it to 1 **on the same pre-commitment reasoning** — and the escalation rule is the entire mechanism that makes that reasoning conservative rather than convenient. **A choice discounted by a rule it is not subject to is discounted for nothing.** This is a defect R-001 introduced in the same revision that created K7, inside the section whose job is to prevent exactly that class of omission. **Repaired: K1–K7 throughout, including in KC-002's anti-reinterpretation clause 2 and in the sealed `universe` and `forward_kill_condition` fields.**

**(ii) Quantity.** `family_stats` sums `n_inherited` and logged trials **transitively across `predecessor_chain`** [measured — `registry.py`], so a successor's denominator **already contains** its predecessor's total the moment `predecessor_family` is set. `n_inherited ≥ menu_size × chain_total` therefore yields `(menu_size + 1) × chain_total`. **The correct declaration for the intended denominator is `(menu_size − 1) × chain_total`.** The same misreading appears in **four** places — §7.2, KC-002 clause 3, §19.3's successor, and **`RULING-004` ML-17, which copies this document's formula citing it as the source.** Filed **I-055**. Direction of error: **conservative**, which is why it survived R-001, Validation's read of R-001, and ML-17's drafting.

**(iii) Executability — I-053.** `open_hypothesis` refuses `n_inherited ≥ chain_total`; K1–K7's menu sizes are 10, 3, 9, 5, 5, 4, 5, **all ≥ 3**, so **both** the struck and the corrected forms are refused, on every choice, always.

> **The sharpest statement of I-053, which this seat did not find in the entry itself: the harness can carry the CHAIN, but it cannot carry a MULTIPLIER ON the chain.** Set `predecessor_family` and declare `n_inherited = 0` and the registration succeeds, the predecessor's count is carried, and **the menu-size factor — the entire economic content of the escalation rule — is never charged.** The registry has no expression for "this successor's search is `K` times the whole chain that preceded it." **That is the hole, and it is exactly the size of the discount §7.2 grants.**

**Was it repairable at the document level? PARTLY, AND THE PARTITION IS THE ANSWER.**

- **Heads (i) and (ii) are fully repairable in the document, and are repaired.** Both are defects in what the rule *says*.
- **Head (iii) is NOT repairable at the document level.** No sentence in a pre-registration can make `registry.py` accept a registration it refuses. **A document cannot repair a harness.**
- **But the document CAN change what the rule REQUIRES, to something the harness executes today — and refusal is something the harness executes.** The replacement therefore states both: the **quantity** to be declared if and when I-053's repair lands (`(menu_size − 1) × chain_total`), **and** the operative content until then — **a post-result revision of any of K1–K7 TERMINATES THE LINE**, with the under-declaration route **forbidden by name**. **The rule is now executable, and what it executes is a hard stop.**

**Four alternatives considered and rejected, with reasons, so the choice is auditable:**

| # | Alternative | Rejected because |
|---|---|---|
| **(a)** | Declare a **lower** `n_inherited` that satisfies the guard | This is precisely what I-053 names as *"the one that will be taken under schedule pressure"* and is Appendix B #2 — the trial count lost. **It is forbidden by name in the sealed text**, so that a future seat must overrule a written sentence rather than fill a silence. |
| **(b)** | Omit `predecessor_family`, so the guard never fires | This is the **abandon-and-re-pre-register loophole Ruling 001 F4 exists to close** [cited — `registry.py` docstring]. Rejected on sight. |
| **(c)** | Stage the count through intermediate registrations until the guard is satisfied | Gaming a guard by construction, and it corrupts the chain with families that never existed. A rule that can be satisfied by manufacturing predecessors is not a rule. |
| **(d)** | Make I-053's harness repair a **blocking condition on sealing** | Rejected, and this is the closest call. The rule fires **only on a post-result revision**, which this family is forbidden to make; it can seal, run F-002, reach a verdict and be killed without the repair ever being needed. I-030's *"delay is strictly cheaper than sealing defective"* applies to defects **the seal would freeze** — and the sealed text here is **correct under both harness states**, naming the quantity for the repaired world and the hard stop for the current one. **Blocking the seal on it would delay for a contingency the document forbids.** |

**What the rejection of (d) costs, stated rather than glossed.** It costs the successor family at §19.3 — *"the same claim, on 1-hour or 8-hour bars"* — which is **this seat's stated most-likely deliverable**. A successor changing K6 (menu size 4) requires `3 × chain_total`, which is refused. **Until I-053 is repaired, the family this document expects to produce CANNOT BE OPENED.** That is written into §19.3 rather than discovered on the day the KILL memo names it.

**One thing this seat raises and does not decide.** Validation rated I-053 **MEDIUM** on the ground that it is *"latent and has never fired."* That rating is defensible on the firm-wide view. **On this family's view, its expected firing date is this family's own KILL memo, which §19.3 predicts as the most likely terminal outcome.** This seat therefore **raises the rating for Validation's reconsideration and does not overwrite it** — re-rating another seat's Issue Log entry is not this seat's to do, and the raise belongs in the record either way.

### 7.3 R10 — what the I-050 estimator correction changes for this family

**The correction, as approved:** the Gate 1 `t` is `SR × √T`, which assumes serial independence; the firm's one measured instance is **ρ = 0.83 → ≈3.3× inflation**, in the **permissive** direction; the estimator is being corrected; **`T_STAT_HURDLE = 3.0` does not move** [cited — `RULING-004` §14, §14.1; I-050, Principal-approved].

**Dependency check on every pre-registered expectation the dispatch named — §5, §14, §16, §19:**

| Clause | Depends on the uncorrected statistic? |
|---|---|
| **F-002 leg (i)** | **No.** Pre-committed as a **Newey–West `t`, 21-bar truncation**, expressly because *"a carry residual is autocorrelated by construction and an OLS `t` on it is inflated in a known direction."* **The falsifier was written to the corrected estimator one document before the correction was ruled.** §5.3's `α = 0.0013` and the joint false-survival rate of **1.3 × 10⁻⁴ stand unedited.** |
| **F-002 legs (0), (ii), (iii)** | **No.** A bar count, a ratio of tail means, a sign test. |
| **§14 KC-002 (a), (b), (c)** | **No.** Three bare one-sided comparisons; *"none has a null distribution, an alpha, or a power statement."* **Stated explicitly in the document so no seat re-opens the kill condition on an estimator change.** |
| **§16** | **Yes, in one row, which was wrong as written.** §16's first row claimed net Sharpe, `t`-stat, DSR and PBO *"correctly denominatored."* **The denominator was honest; the estimator was not.** The `t` is split into its own row and re-verdicted. |
| **§19.3** | **Yes.** Revised **against the family** — see below. |
| **§5.4** | **Yes, and it becomes MORE coherent.** §5.4 compared F-002's Newey–West `t(α)` against Gate 1's `t`; before the correction that was an implicit comparison of a corrected statistic against an uncorrected one. The `≈6.0` pre-haircut figure is arithmetic on the haircut alone and does not move; its **meaning** sharpens. |

**The narrowing, bounded rather than computed.** The R4(b) haircut requires ≈**2×** the pre-haircut `t`; the correction multiplies the required *uncorrected* `t` by the inflation factor at the family's realized autocorrelation, ≈**3.3** at the firm's one measured ρ. Composed: **an uncorrected, pre-haircut `t` of order 3.0 × 2 × 3.3 ≈ 20** [inferred — arithmetic on two cited multipliers, stated as an order of magnitude, **not** a forecast].

**Three disciplines applied to that number, all against the family.**
1. **The family's own ρ is UNMEASURED and may be much lower than 0.83** — 0.83 is measured on the *funding series*, not on this family's *net returns*. **Measuring it is a trial and the registry is at 0**, so it is not measured here.
2. **This seat nevertheless does not discount the figure on that ground.** *"Probably small"* is `[assumed]` doing the work of `[measured]` — Validation's own formulation [cited — `RULING-004` §13] — and this seat adopts it against its own family.
3. **The consequence is written as a revised pre-registered expectation, not as a caveat:** **§11.6 recorded the 50% haircut as *"the largest single hurdle this family faces."* It is no longer the largest.** And **conditional on F-002 surviving in full, the expected Gate 1 outcome is PARK-WITH-TRIGGER, not PROCEED.**

**What it does not change.** The §19 verdict — fund it, ~4 Sonnet units — **stands**, because that case rests on a *verdict being reachable*, and **F-002 and KC-002 both deliver a verdict without touching a `t`.** A pre-registration whose Gate 1 odds worsen while its falsifier's decisiveness is untouched has become **more** worth running per unit of compute, not less: the compute buys the kill, and the kill is what §19.3 expects to deliver.

### 7.4 R11 — does `RULING-004` bind this family? Yes, in three places, and the `N` accounting survives

**The dispatch asked the right question and the answer is not the summary line.** `RULING-004` §12 records `PREREG-002` §10 as *"Untouched."* **That is correct about §10 and would be wrong if read as "the ruling does not reach this document."**

**(a) ML-1's fitted-family trigger does NOT fire — and one row of the check was a genuine gap.** K1–K7 were each selected pre-measurement from a declared menu against a 0-trial registry, and **K4's R3 move — the only selection that changed after data existed — moved on a documented vendor act dated 2022-11-09, not on any statistic**, with no return statistic on SOL ever computed. The ±50% grid compares candidates on the sample but **the plateau centroid advances by rule**, which is ML-1's own boundary case verbatim. F-002 selects nothing.

> **The gap: the ≥10 walk-forward windows were UNSPECIFIED as to whether each re-selects its configuration.** Per-window re-selection at an argmax **would have fired ML-1**, made this a fitted family, and charged the grid's full cardinality **per window** — against an absolute ceiling of 109. **Silence here does not default to the safe reading: a walk-forward that re-optimizes per window is the ordinary implementation.** Sealing the silence would have left the fitted/not-fitted question to whoever wrote the loop, after `C`. **Repaired: every window is refit at the FIXED plateau-centroid configuration; no window re-selects.** It removes a degree of freedom and adds none, which is what makes it admissible pre-seal.

**(b) ML-2 binds every family including this one, and this document was silent.** ML-2 requires the non-fitted assertion **as a sentence in the sealed block** and states *"Silence is not that assertion"*; a missing or partial ML block is **REJECTED, not deferred**. **Added verbatim to §21**, with §10.7(a)'s choice-by-choice check behind it. **`PREREG-001` is also silent and is also unsealed — filed I-056.**

**(c) ML-13 leaves the `N` accounting intact, and the reason is checkable per choice.** The discount survives for all seven of K1–K7 **on ML-13's own stated condition** — selection determined at sealing without reference to a sample-computed quantity. `N_conditioning` = **7**, budget **79**, ceiling `N` = **86**, `MinBTL(86) = 6.14` against 6.571. **This is stated as a conclusion drawn per choice rather than as a citation of Validation's summary line, because the summary line would have read "Untouched" even if one of the seven had failed, and the party best placed to find that is the seat that made the seven choices.**

**One asymmetry recorded against the family, in the sealed text.** The discount from 135,000 to 7 rests on a condition the family asserts about itself, enforced by §7.2's escalation rule — **and R9 has just established that the enforcement was inoperative for the whole interval between R-001 and R-002.** **That is the sharpest single criticism available against this family's `N` accounting, and it is raised by this seat rather than left for the Red-Team Memo to find.**

**(d) A fourth reach, not asked about and carried anyway: I-051.** `RULING-004` ML-18 finds `purged_kfold_splits` embargoes `⌈0.01·T⌉` = **24 bars** on a 2,398-bar sample, and `walk_forward_windows` applies **no purge and no embargo at all** [cited]. **This family's K1 lookback is 30 days — longer than the embargo.** A training bar 25–30 bars after a test fold computes `z(t)` from inside it. **This is a live leakage channel sized against this family's own declared parameter, in the permissive direction.** `EMBARGO_FRACTION = 0.01` is a Charter §4.2 constant and not this seat's to raise; ML-18 rules it *"a floor rather than a target."* **Named in §9.2, §15 step 7 and the sealed field set so a WFE number is not read as clean.** Owner `head-of-data-infra` under I-051.

### 7.5 R12 — C12 discharged, and why the discharge is recorded as narrow

**`DATA-VERIFY-002` delivers exactly what C12 asked for and delivers it clean:** BTC and ETH carry **exactly three funding prints on every one of 2,401 days each — 4,802 symbol-days, zero deviating days in either direction**, `2,401 × 3 = 7,203` exactly, span independently confirmed gap-free [measured]. **SOL's 11 deviating days are the working positive control** that the instrument detects a break when there is one [measured — I-045; Ruling 003 §A2] — **a null from a test with no demonstrated positive is worth much less, and this one has its positive.** **C12 is DISCHARGED and this seat, which created it, says so plainly rather than holding it open to look careful.**

> **And the discharge is narrower than the premise it was protecting, which is the part worth reading.** It verifies the **CADENCE** dimension. **The document's own named K7 trigger is the proof that this is not the same as the parameter dimension: 2025-09-18 — the firm-wide `/(8/N)` formula change — shows 3 prints on BTC and 3 on ETH** [measured — `DATA-VERIFY-002` §4, checked by name]. **A documented, dated, real change to the funding formula is INVISIBLE to a cadence sweep.** So is a clamp-cap change — **the exact change that killed SOL's usability.**
>
> **Therefore: K7 governs the parameter dimension BY DECLARATION, not by measurement**, its trigger being an observable in the vendor's announcements rather than in the firm's store. §17 risk #12's residual is **not** narrowed by C12's clean result, and **any reading of `DATA-VERIFY-002` as "the primary universe has no in-sample parameter break" is a misreading of a cadence measurement as a parameter measurement.** That refusal is written into `PREREG-002` §7.1.1 — inside the sealed text — so it is refused in advance rather than corrected later.

**Two boundaries observed rather than crossed.** **I-045 is not closed by this revision** — its owner line routes closure to `quant-validation`, and C12's discharge is a different act on a different object. And **no Issue Log entry is filed against `DATA-VERIFY-002`**: a clean measurement is not an issue, Seat 9's escalation rule was correctly conditional on finding a deviation, and the narrowness of what the instrument covers is a property of the question C12 asked — **which this seat wrote.**

### 7.6 Issues filed, with the rating reasoning exposed

| # | Finding | Severity | Owner |
|---|---|---|---|
| **I-055** | The `n_inherited` escalation formula over-declares by one `chain_total`; one misreading of `family_stats` written into four binding clauses across two documents, including `RULING-004` ML-17 | **MEDIUM** | director-of-research → quant-validation |
| **I-056** | `RULING-004` ML-2 makes a missing ML declaration a Gate 0 **rejection**, and neither existing pre-registration carries one; `PREREG-002` repaired, `PREREG-001` open | **MEDIUM** | director-of-research |

**Neither is HIGH and neither is under-rated to avoid the interrupt.** The test applied is the log's own: *a Charter criterion unenforceable or wrong in a way that changes verdicts* — the shape of I-029, I-034, I-037, I-050. **I-055's error runs conservative, is latent at 0 trials, and blocks nothing**; rating it HIGH to force a §4 interrupt on a conservative arithmetic error in a latent clause would be the inflation the Standing Order warns against. **I-056's consequence is a rejection rather than a deferral and it applies firm-wide going forward**, which takes it above LOW; but no number is wrong, nothing is blocked, and the fix is one sentence per unsealed document, which keeps it below HIGH. **The one HIGH-severity matter in R-002's field of view is I-050, and it is already filed, already rated HIGH by Validation, and already before the Principal.**

### 7.7 Seal-readiness after R-002

**R-001 created a blocker and named it first. R-002 creates none and discharges one — and still leaves the document further from a comfortable seal than it found it**, because the three repairs are, in substance: a ceiling one trial too generous, **a control this document called its most important one that was inoperative for the whole of its existence**, and **a Gate 1 margin materially narrower than R-001 recorded.**

| Condition | Status |
|---|---|
| **C2** · Validation's Gate 0 intake verdict | **OPEN — BLOCKING.** None exists. |
| **C3** · Devil's Advocate Red-Team Memo | **OPEN.** Blocking on Gate 1. |
| **C7** · KC-002 signed by sponsor and Principal | **OPEN — BLOCKING**, executional. |
| **C8** · seal and vault in one session, same UTC day | **OPEN — BLOCKING**, executional. |
| **C11** · leg-(ii) null calibration | **OPEN — BLOCKING.** ≤2 trials, required measured before sealing. |
| **C12** · in-sample cadence sweep | **[R12] DISCHARGED, narrowly** — cadence dimension only. |
| **C13** **[NEW]** · Validation's ruling on R-002's three items | **OPEN — not a separate blocker**; resolved inside C2's intake verdict. |
| **C1** · funding-cost repair | Specification **discharged**; implementation open as **I-034**. |
| **C9** · perp OHLCV | **CLOSED.** |

**Nothing in R-002 relaxes a condition, and R-002 does not seal.** Sealing is sequenced separately and is not this seat's to trigger.

### 7.8 What R-002 did not do

- **No seal, no vault, no registry write, no commit, no harness change.**
- **I-045 not closed** — `quant-validation`'s.
- **No declared menu edited, and in this revision NO SELECTION MOVED AT ALL.** R8–R12 touch a ceiling, an escalation rule, a disclosure, an assertion and a condition's status. **`N_conditioning` remains 7; the trial budget remains 79.**
- **No number computed.** The one arithmetic operation is `109 − 86 = 23`, on two integers each already `[cited]` or `[measured]`.

---

*Director of Research · Castellan Capital · 2026-08-04 · **addendum §7 added 2026-08-05 for revision R-002***
*Reasoning memo for revisions R-001 and R-002 of `research/PREREG-002-crypto-funding-basis.md`. No hypothesis was opened, no trial was run, no vault was sealed, and `book/` was not touched.*

---

# ADDENDUM — REVISION R-003 · 2026-08-06 · PRE-SEAL

**Occasion:** `research/VALIDATION-SPEC-002-serial-corrections.md` (Validation, 2026-08-04, 57 binding clauses) and `research/DATA-IMPL-006-serial-corrections.md` (Seat 9, 2026-08-05) · Issue Log **I-057, I-060, I-061, I-063, I-064** · dispatch **S2-D-020**.
**Trial budget for this revision: ZERO.** `book/registry.db` reads **0 hypotheses / 0 trials / 1 event** [measured, this session]. **No number was computed.** Every `N_max` figure is `[cited]` from `VALIDATION-SPEC-002` §6.2's measured table; the only arithmetic performed is integer summation of line items already declared at PREREG-002 §10.5.

---

## 8. WHAT R-003 CHANGED IN `PREREG-002`, AND WHY

### 8.1 R13 — the ceiling is sealed as a FUNCTION, and the defence is preserved rather than re-argued

The Principal ruled that §10.4 does not seal a constant. The sealed form, in one line:

```
N_max  =  min( 109 ,  max_admissible_trials(span, SR_realized, ppy, vif = VIF_gate(ρ̂)) )
```

`109` is `max_admissible_trials(6.571, 1.0, vif = 1.0)` — the first argument of a `min`, not a constant that happens to bind. `ρ̂` is the family's **net-return** autocorrelation, measured by the harness from logged trials at every `evaluate_gate1` call.

**This memo deliberately does not re-derive the admissibility argument.** The Principal's own defence is adopted verbatim: the construction is **monotone-conservative** — measurement can only tighten, never loosen — so **it is not the I-029(d) operation; it is the `min(t_NW, t_raw)` construction extended to `N`.** I-029(d) moves a constant in the permissive direction *after seeing an outcome*; this seals a function *in advance* whose every argument moves the requirement only toward tightening.

**What R-003 adds is that the property is now demonstrated rather than specified.** Seat 9 swept it directly [measured — `DATA-IMPL-006` §2]: **145 draws for `N_max` and 900 for DSR across ρ ∈ [−0.6, +0.8], using real measured VIFs from `variance_inflation` rather than adversarially injected ones — zero violations.** That distinction matters: the measured-VIF path is the one that governs every live Gate 1 evaluation of this family. **A sponsor benefits from believing the assurance, so this document records the demonstration.**

**The rejected alternative, stated because the memo's job is to record what was not done.** The obvious alternative was to leave 109 as a sealed constant and disclose the correction in a footnote. It was rejected for the reason R-001 rejected the same move: a footnote does not change what the harness grades against, and §10.4's number is graded. Sealing 109 as a constant would have sealed a figure the harness would then decline to use.

### 8.2 R14 — writing the document against 0.034, and why a sponsor adopts a tightening that came from below

`MinBTL(86, 1.0) = 6.1359 y` against 6.571 y available gives a maximum admissible VIF of 1.0709 and a binding AR(1) `ρ̂` of **0.0342** [all cited — `VALIDATION-SPEC-002` §7.2; I-064]. The Principal's stated figure was 0.1; at 0.1 the ceiling is 55 and `N` = 86 is **31 trials over, not marginally over**.

**The governance point is the one worth recording.** Validation tightened a figure the Principal had stated, **without requesting an act**, under the §8 asymmetry that places tightening within Validation's authority — and filed it as I-064 rather than exercising it silently. The Principal countersigned: *"my number was a prediction, Validation's is a derivation."*

**A sponsor quoting the looser figure because it came from higher up is Appendix B failure mode 1 in miniature** — the firm becoming a machine for agreeing upward. PREREG-002 is written against 0.034 throughout from R-003 forward, and `0.10` survives in the document exactly once more, explicitly **not** as a threshold (§8.3).

### 8.3 R15 — the conservative `ρ`, named, and the budget rebuilt against it

**`ρ_plan` = 0.10, declared at §10.5.1, before any measurement of `ρ̂` exists for this family or any other.** `N_max(0.10) = 55` [cited].

**Why a `ρ` had to be named at all.** The budget PREREG-002 carried through R-002 was set against `ρ = 0` — **not by argument but by silence**, because no other assumption existed when it was written. At 7 + 79 = 86 it sat **exactly** at `N_max(0.034) = 86`: **zero trials of margin at its own binding threshold.** That is the self-inflicted wound the Principal named — a budget set against an optimistic `ρ` that the measurement then disallows.

**Why 0.10.** Four reasons, three of them checkable and one of them this seat's judgment, all recorded at §10.5.1: it is the top of `VALIDATION-SPEC-002` §7.4's *repairable* PARK band (≤ 11 months of history); it is the largest `ρ` at which this family can still fund its **Charter-mandatory** work (at `N_max(0.20) = 31` the ±50% grid alone is 25 and the ≥10 walk-forward windows take it to 35, inadmissible before F-002 runs); it is the Principal's own figure re-used in the role where it is valid, since **a number that was permissive as a trigger is conservative as a budget**; and — the judgment — **this family's net series is structurally carry-heavy in a way the generic dilution argument does not cover.**

**That fourth reason cuts against the family and is stated anyway.** `VALIDATION-SPEC-002` §7.5 places `ρ̂` "plausibly anywhere in [0.0, 0.5]" on the reasoning that a net series is `gross + carry − costs` and *"its price-return component is close to serially independent."* **This position is delta-neutral by construction — the price-return component is deliberately hedged out** — so the term that would dilute `ρ̂` toward zero is precisely the term this family removes on purpose. What remains is funding carry (persistent) and a weight `w(t)` that is a closed-form function of a trailing-30-day standardized deviation (persistent by construction). **This family should be expected in the upper half of that interval.** `[inferred — reasoning, not measurement.` The funding autocorrelations 0.829 / 0.802 are **not** `ρ̂` and R-15 forbids quoting them as such; they establish only that the carry term is the persistent one.`]` **It is not a forecast and it does not narrow the cited interval. If `ρ̂` measures 0.4 this family dies on arithmetic, and declaring 0.10 is not a claim that 0.4 is unlikely.**

**Why staged rather than a flat cut — the four reasons, and the third is the real one.**

1. **A flat cut forfeits capability on an assumption; staging forfeits it only on a measurement.** The unlock is contingent on `ρ̂`, which is **not a result** — it is a nuisance parameter of the return series, computed by the harness inside `evaluate_gate1`, printed on the report face, and not suppliable by the sponsor (V-1, V-2, M-10). PREREG-002 §10.4's prohibition — *"expanding a trial budget because early results look good is the overfitting operation wearing a schedule's clothing"* — is not weakened, because `ρ̂` is not a result and it moves the authorization in **whichever direction it measures**.
2. **The evasions are closed by the correction itself, not by this seat's assurance.** Coarser bars to depress `ρ̂`: closed by R-16, which is the clause that makes the corrected requirement approximately frequency-invariant (17% versus the uncorrected 4.5%). Selective logging: closed by R-6/R-7/R-8's max-then-median with the candidate series as a floor, and R-9's refusal above a 25% exclusion rate.
3. **STAGING IS WHAT MAKES §7.4's PARK VERDICT OPERATIONAL RATHER THAN NOMINAL.** Under a flat 79-trial budget, a family PARKed at ρ̂ = 0.10 would keep spending its ≤ 22 forward-window regenerations while waiting for the ≤ 11 months of history that is its **only honest remedy** (V-5). **Every one of those trials raises `N`, which raises `MinBTL`, which raises the span required — the parked family digs its own hole while waiting in it.** Stage 2's gate stops that by construction. **A PARK that keeps burning `N` is not a PARK**, and this is the reason that persuaded this seat.
4. **It is the only remedy a sponsor controls.** Of V-5's four, three do not work. The one that does is calendar span, and the one thing a sponsor can do to help is not spend trials while it accrues.

**The objection, raised here rather than left for C3.** A two-stage budget is a budget with a door in it, and doors get opened under schedule pressure. The key is held by the harness; **the latch is I-022, and it is broken** — `gates.py` hard-codes the trial-count criterion's verdict to the literal `True`. **C10's weight therefore goes up under R-003, not down**, and PREREG-002 §20 records that.

**What it costs, stated first in the revision block and repeated here.** Authorized budget 79 → 47, a **40% cut**; declared ceiling 86 → 54. If `ρ̂` measures ≤ 0.034 the cut will have been unnecessary and Stage 2 restores the family exactly. **The asymmetry is decisive: an unnecessary Stage-1 cut costs a scheduling delay; an unauthorized Stage-2 spend at ρ̂ = 0.10 costs the Gate 1 verdict permanently, because trials cannot be unspent and `InheritedCountDoubleCountError` closes the successor route.**

### 8.4 R16 — recording the verdict bands in the sponsor's own document

`VALIDATION-SPEC-002` §7.4's bands are transcribed at PREREG-002 §10.8: ρ̂ ≤ 0.034 PASS · 0.034–0.15 FAIL-on-length, **PARK**, ≤ 11 months of history repairs it at 0.1 · 0.15–0.30 PARK nominal, kill in practice · **> 0.30 KILL** · `|ρ̂| ≥ 0.97` or `n_logged = 0` **INSUFFICIENT-DATA, never PASS**.

**Why transcribe a Validation clause into a sponsor document at all.** Because the party who will want to renegotiate a near-miss at Gate 1 is the sponsor, and **a band the sponsor pre-registered is one the sponsor cannot renegotiate.** Pre-committing the verdict rule before the measurement exists is Ruling 001 §4.4's own device.

**The Sharpe escape is recorded as closed by construction**, because it is the route this seat would reach for: `MinBTL ∝ 1/SR²`, so a realized net `SR_ann ≥ 1.068` clears the criterion at ρ̂ = 0.10 on the span already held — **but raising the realized Sharpe by searching raises `N`, which raises `MinBTL`, which raises the Sharpe required.** It works only on data not yet seen, which is the calendar-span remedy wearing a hat (V-5). **Any artifact on this family presenting a search-improved Sharpe as relief from the length criterion is defective, with §10.8 as the pre-registered reason.**

### 8.5 R17 — I-063 disclosed rather than implied away

The Gate 0 intake ceiling is **necessarily** computed at `VIF = 1`: at intake no trial has a return series, so `ρ̂` is unmeasurable at exactly the moment the ceiling is quoted. **Structural, not closeable.** V-6's mandatory render string is carried verbatim at §10.4.3 — **UPPER BOUND · re-evaluated at Gate 1 · can only fall · not a budget** — and the exposure is stated against this family by name: it could be ADMITTED against 109, spend 86, and fail because the measured ceiling is 55, with the trials unspendable-back and neither sponsor nor machinery at fault.

**What this seat does not claim: that disclosure removes the exposure.** It does not. Validation rates I-063 MEDIUM because it cannot produce a wrong PASS — it produces **wasted research and a false sense of budget**. §10.5.2 reduces the waste; nothing removes the structure.

### 8.6 R18 — I-060 and I-061 settled, choice by choice

**I-060 — does not bite as a clause; bites harder as arithmetic.** The row-by-row pass is at §10.9(a). ML-16's mandatory 32-trial dispersion sample is inside ML-3–ML-27 and **does not reach a non-fitted family** (§10.7(a) establishes non-fitted row by row, conditional on the plateau-centroid commitment and §10.7(c)'s walk-forward fix). **And the family gets ML-16's statistical content free:** §10.6's 25 grid points plus ≥10 walk-forward refits give **35 series at Stage 1 alone, above Ruling 004 §2.4's `m ≥ 32` floor, at zero incremental `N`**, because they are already budgeted trials. Under the conservative reading the Principal has ruled governs pending Sprint 3 — **diagnostics count toward `N`** — every diagnostic this family will run was **already inside its declared `N` before R-003**, with no exception found on the pass. **This seat looked for one and reports that there is none.**

**But I-060's actual content is not "ML-16 is expensive."** It is: *a family that cannot afford its own diagnostics has not discovered a problem with the diagnostics; it has discovered that this firm's data cannot support that family at that persistence.* **On that reading it reaches PREREG-002 directly and at a tighter threshold than its own headline** — I-060's obligations exhaust the ceiling at ρ̂ > 0.045; this family's declared 86 exhausts it at **ρ̂ > 0.034**. **Not being a fitted family does not exempt it from the collision.** §10.5.2 is the response and it does not repair the collision; nothing does.

**I-061 — nothing in PREREG-002 rested on it.** Checked at §10.9(b) against every clause touching bar frequency: `periods_per_year = 365` (a calendar fact), K6's daily bars and the R4 aggregation rule (a data-correctness argument from Ruling 003 §3.2), §16.1's intraday problem (instrument resolution), §19.3/§22-row-4's finer-bar successor (resolution, not observation count), and §10.4/§10.5's `MinBTL` arithmetic (`ppy` never varies in this document, so frequency-invariance is never invoked in either direction). **K6 was fixed as a declared conditioning choice with a full menu, before any measurement, for data-correctness and risk-observability reasons — not because this document believed bar choice was free of length consequences.**

**One forward-looking consequence recorded so a future seat does not re-discover it as a remedy:** the successor family at 1h or 8h bars named at §19.3 buys **no** relief on the length criterion by sampling more finely — the `√ppy` annualization overstates `SR_ann` at fine bars by exactly the factor the VIF removes, and the two cancel to within 17% (R-16). **The successor's case is resolution and nothing else.**

### 8.7 Seal-readiness after R-003

**The same five remain open and blocking — C2, C3, C7, C8, C11. R-003 clears none and creates no sixth.** C13 is extended by two items folded into C2's intake (the §10.4.1 functional form; the §10.5.2 Stage 2 unlock rule). C10's weight increases.

**R-003 moved seal-readiness in one direction only, and it is the unflattering one.** It cut authorized `N` by 40% on a named assumption, replaced a constant this document had defended twice with a function whose value is unknown and can only fall, recorded the bands under which the sponsor loses, and disclosed that the 109 quoted since 2026-07-28 **was never a budget and cannot be made into one.** D-015's reading holds: *"the ceiling binding at the seal is the control functioning."*

### 8.8 What R-003 did not do

- **No seal, no vault, no registry write, no commit.** `book/registry.db` unchanged at 0/0/1.
- **No `harness/` file touched, no test run, no suite state reported** — Validation is adjudicating those concurrently and they are not this dispatch's.
- **No `VALIDATION-*` document touched.**
- **I-045 not closed** — `quant-validation`'s, unchanged.
- **No declared menu edited and no selection moved.** `N_conditioning` remains **7**. R-003 moves a ceiling's *form*, a budget's *size and authorization structure*, and adds three disclosures.
- **No number computed.** Every `N_max` is `[cited]` from `VALIDATION-SPEC-002` §6.2. The arithmetic performed is `2+3+7+25+10 = 47`, `47+22+10 = 79`, `7+47 = 54`, `7+79 = 86` — integer sums of already-declared line items, of the same class as R-002's `109 − 86 = 23`.

---

*Director of Research · Castellan Capital · **addendum §8 added 2026-08-06 for revision R-003***
*Reasoning memo for revisions R-001, R-002 and R-003 of `research/PREREG-002-crypto-funding-basis.md`. No hypothesis was opened, no trial was run, no vault was sealed, `harness/` was not touched, and `book/` was not written to.*

---

## 9. THE §4.7.2 AUDIT — every limit `PREREG-002` claims, against the field that enforces it

**Added 2026-08-10 for revision R-004.** Dispatch S3-D-001, Task 1. **Trial budget: ZERO. No number
computed.** Every harness fact below is `[measured — read from source this session]` at the named file
and line; every figure about this family is `[cited]` from `PREREG-002`, `VALIDATION-SPEC-002/003`, or
`VALIDATION-RULING-004/005`, carried forward with its source.

### 9.0 The test, and why it is applied to sixteen fields and not to a document

`GATES.md` §4.7.2, ruled 2026-08-06 (S2-D-029):

> **For every limit the document claims, name the field the harness reads to enforce it. If there is
> no such field, there is no limit.**

The binding field set is enumerated at `harness/castellan/registry.py:82`, `_BINDING_FIELDS`
[measured]. **Sixteen fields.** Anything not in that list is not sealed, whatever the document says
about it. And — the distinction this audit turns on and which §4.7.2's own wording does not force —
**being in that list means a field is *hashed*, not that it is *read*.** `prereg_sha256` gives
tamper-evidence. Tamper-evidence is not enforcement. **A field can be sealed, shadow-copied, and
hash-verified at every Gate 1 call, and still have no consumer anywhere in the harness.** Nine of the
sixteen are in exactly that state, and that is §9.2's finding.

**The verification method, so it is reproducible rather than asserted.** For each of the sixteen
field names, `grep -rn <field> harness/castellan/ | grep -v registry.py` [measured]. Every field with
zero non-`registry.py` hits is read by nothing outside the module that stores it; every field with
hits was then read at each call site to establish whether the read *enforces* or merely *renders*.

### 9.1 What each of the sixteen binding fields actually does

| # | Field | What reads it, beyond being hashed into `prereg_sha256` | Enforces a limit? |
|---:|---|---|---|
| 1 | `family` | `hypotheses` PK; `trials.family` FK; `log_trial`'s registration check (`registry.py:485`); `predecessor_chain`; every `evaluate_gate1` lookup | **Yes** — A2's whole mechanism |
| 2 | `statement` | `open_hypothesis`'s non-empty check (`registry.py:~250`). Nothing else, anywhere | Presence only |
| 3 | `mechanism` | Same non-empty check. Nothing else | Presence only |
| 4 | `falsifier` | Same non-empty check. Nothing else | Presence only |
| 5 | `universe` | **Nothing.** Zero non-`registry.py` hits [measured] | **No** |
| 6 | `horizon` | **Nothing.** Zero hits [measured] | **No** |
| 7 | `success_criteria` | **Nothing.** Zero hits [measured] | **No** |
| 8 | `trial_budget` | `gates._trial_budget_criterion` — `sealed = fam.trial_budget` (`gates.py:562`), B-7's zero-budget branch, B-9's per-trial ordering walk, `declared_ceiling_base` (`gates.py:565`), `trial_budget_sealed`/`_effective` on the report face | **YES — the only binding field that enforces a numeric limit** |
| 9 | `predecessor_family` | Validated at registration (must itself be registered); `predecessor_chain`; `family_stats`' transitive sum; `returns_matrix`; `InheritedCountDoubleCountError`'s guard | **Yes** |
| 10 | `holdout_classification` | Validated at registration against `{FORWARD, HISTORICAL}`; gates `HISTORICAL` into the R3 presence check; rendered on the report face (`gates.py:1055`, `:165`) | Partly — a domain check and a render |
| 11 | `forward_window_start` | **Presence check iff `holdout_classification == "HISTORICAL"`.** This family is FORWARD, so **nothing reads it at all.** Zero non-`registry.py` hits [measured] | **No, for this family** |
| 12 | `forward_window_min_length` | Same. **Nothing, for a FORWARD family.** No code anywhere compares it to an elapsed span, and no code knows its unit | **No** |
| 13 | `forward_kill_condition` | Same. **Nothing, for a FORWARD family.** No harness path evaluates a kill condition, on any date, for any family | **No** |
| 14 | `model_prior_provenance` | **Nothing.** Zero hits [measured] | **No** |
| 15 | `published_signal_haircut_applied` | **Nothing.** Zero hits [measured]. No code path applies a haircut to a return series, a Sharpe, or an alpha | **No** |
| 16 | `n_inherited` | `family_stats.n_trials = n_inherited + n_logged`, summed transitively; **DSR's `N`** (`gates.py:779`, `:788`); **MinBTL's `N`** (`gates.py:856`); `declared_ceiling_base` for the contingent-extension arithmetic (`gates.py:565`); PBO's H-9 disclosure note; the H-11 note on the zero-logged branch | **Yes — four consumers** |

### 9.2 CATEGORY (c) — the limits nothing reads. **This is the deliverable.**

Every entry below is a limit `PREREG-002` states in operative, binding language, for which the answer
to §4.7.2's question is **there is no such field, and therefore no limit.** Ordered by how much the
document leans on it.

| # | The limit, as the document states it | Where | Why nothing reads it |
|---:|---|---|---|
| **c1** | **`published_signal_haircut_applied = 0.50`** — §11.6: *"The presumption is accepted. No exemption is sought,"* and §5.4 derives the family's entire Gate 1 burden (`t(α) ≈ 6.0` pre-haircut) from it | §11.6, §5.4, §21 | **The field is stored and hashed and read by no code, anywhere** [measured — zero non-`registry.py` hits]. There is no haircut computation in `gates.py`, `stats.py`, `engine.py` or `costs.py`. §11.6 already cites I-019 for *"schema and no computation attached"*; **this audit sizes it: the largest single acknowledged hurdle this family faces is a number in a column** |
| **c2** | **`forward_kill_condition` = KC-002 in full**, including *"SILENCE IS A KILL — if the computation is not performed … for ANY reason … the family is killed by default"* | §14, §11.4, §21 | **No harness path evaluates a kill condition on any date.** For a FORWARD classification the field is not even presence-checked. **KC-002 — the document's most emphatic control, whose clause 5 exists precisely to defeat non-execution — is enforced by the calendar and by seats, and by nothing in the engine.** The clause that says a kill condition defeatable by not running it is not a kill condition is itself defeatable by not running it |
| **c3** | **`forward_window_min_length = 12.0` MONTHS** — Charter §4.4's holdout floor | §11.4, §21 | Nothing reads it, and **the schema stores it as an unlabelled `REAL`** — the document's own I-033(5) note. Days, months and years are indistinguishable in the column, and no consumer exists to be confused, which is the only reason the ambiguity has not yet cost anything |
| **c4** | **`forward_window_start`** | §11.4, §21 | Same. Inert for FORWARD. The P7 sequencing rule it exists to support — *seal on or before the UTC day of `C`* — is checked by `verify_prereg`'s `sealed_created_utc` against the **vault**, not against this field |
| **c5** | **The §7.2 escalation rule and its hard stop** — *"A post-result revision of any of K1–K7 TERMINATES THE LINE"* | §7.2, §14 clause 2, §21 `universe` | The rule lives in `universe`, **which nothing reads.** What the harness *does* enforce is narrower and different: `PreRegistrationAmendedError` refuses re-registration of a changed binding field, and `InheritedCountDoubleCountError` refuses the successor. **The hard stop is real but it is an emergent property of two guards, not a reading of this clause.** A revision that changed *only* prose inside `universe` would be refused as an amendment — which is the correct outcome reached for an unrelated reason |
| **c6** | **`N_conditioning = 7`, the declared `N` floor** | §7.2, §10.1, §21 | **No field carries it, and the document knows this** (§10.3, I-027). **It is deliverable — see §9.4, which is the finding that reverses it** |
| **c7** | **Every methodological limit stated in `universe`, `horizon` or `success_criteria`**: K3 = "exclude nothing"; "NO WINSORIZATION, OUTLIER REMOVAL OR RETURN CLIPPING anywhere at any stage"; `w_max = 1.0` / never long perp; the capacity screen at 20 × `P_notional`; the ≤5% ADV participation cap; `periods_per_year = 365`; the ML-2 non-fitted assertion; "only `plateau_centroid_params` advances"; the walk-forward fixed-centroid clause; F-002's E2 "evaluated ONCE"; all eleven mandatory per-artifact disclosure lines | §6, §7.4, §10.5, §10.7, §18, §21 | **Three fields, zero consumers.** Every one of these is enforced by the seat that writes the loop. Two have *adjacent* harness protections that must not be mistaken for enforcement of the clause: `execution_lag < 1` raises `SameBarFillError` (`engine.py`), and `grid_from_center` raises above 200 points (`grid.py:27`). **Neither reads the sealed text; both would fire identically for a family that declared the opposite** |
| **c8** | **"No Stage 2 trial is spent on an unmeasured or a stale `ρ̂`"** | §10.5.2 | **`log_trial` reads no budget** [measured — `registry.py:477–502`: the only precondition is that the family is registered]. The budget is enforced **retrospectively**, at `evaluate_gate1`, by B-9's ordering walk over `own_trial_times`. **Nothing prevents the spend; the spend fails the gate afterwards, and trials cannot be unspent** (V-5). This is a real control and it is not the control the sentence describes |
| **c9** | **"the trial budget remains 79 … ceiling `N` remains 86"** as an authorization | §10.7(d), §21, §10.5.3 | Superseded by R-003 as an authorization but **still present verbatim in the `success_criteria` string**, i.e. inside a field nothing reads, next to the R-003 note that supersedes it. Harmless only because no consumer exists to be misled |

**The pattern, stated once.** Eight of these nine are the same shape: **the limit is written into
`universe`, `horizon` or `success_criteria` — the three binding fields with zero consumers in the
entire harness.** Those three fields are where a pre-registration puts its methodology, and they are
precisely where the harness does not look. **The seal makes them immutable; it does not make them
operative.** A sponsor reading `_BINDING_FIELDS` and concluding "my methodology is enforced because it
is binding" has made the I-046 error on the research side, which is what §4.7.2 says in the abstract
and what this table says with line numbers.

**What this does NOT mean, said plainly so the finding is not over-claimed.** Category (c) is not a
list of defects to repair. Most of these belong in a sealed document and could not sensibly be
mechanised — no harness will ever check "no winsorization was applied." **The finding is not that they
should be enforced; it is that the document must stop describing them as though they were, and that
the two that CAN be mechanised (c1's haircut, c6's `N` floor) are the ones worth acting on.** c6 is
acted on in R-004. c1 is filed and is not this seat's.

### 9.3 CATEGORY (a) and (b) — the limits that are real

| The limit | The field, or the code path | Note |
|---|---|---|
| **Trial budget 47 (Stage 1)** | **(a)** `trial_budget`, `gates.py:562` → B-7 / B-9 / `declared_ceiling_base` | **Only if 47 is what is sealed.** This is I-105 |
| **Stage 2 ≤ 32, contingent on measured `ρ̂`** | **(b)** `gates.contingent_increment_allowed` + `_budget_extension_ledger`, against a `trial_budget_extension` event of `mode="CONTINGENT"` | **Only if the event is written.** No document can write it; it is a post-seal registry act |
| **`N` = `n_inherited` + logged, transitively summed** | **(a)** `n_inherited`, `predecessor_family` → `family_stats` | Four consumers: DSR, MinBTL, `declared_ceiling_base`, PBO's disclosure |
| **`N_max` ceiling as a function** | **(b)** `_admissible_ceiling` (`gates.py:344`) = `min(n_max_admissible_iid, n_max_admissible_serial)`, recomputed at every call | R13's functional form is real and is computed, not declared |
| **Pre-registration immutability after seal** | **(a)** all sixteen, via `prereg_sha256` + `PreRegistrationAmendedError` + `verify_prereg`'s shadow copy | Tamper-**evidence** across all sixteen; tamper-**prevention** on none |
| **Successor cannot escape the chain's count** | **(a)** `predecessor_family` + `InheritedCountDoubleCountError` | §4.7.1's doctrine, mechanised |
| **A2 — no unregistered run** | **(a)** `family` → `log_trial`'s `PreRegistrationError` | The firm's strongest single control |
| **Minimum one-bar lag** | **(b)** `SameBarFillError`, `engine.py` | Reads no sealed field; unconditional |
| **Grid cardinality ≤ 200** | **(b)** `grid.py:27` `ValueError` | Reads no sealed field; unconditional |

### 9.4 THE FINDING THAT CHANGES THE PAYLOAD — `n_inherited` must be **7**, not 0

**§10.3's premise is stale and its consequence runs permissive.** The document states, at §10.3
[cited — `PREREG-002` §10.3]:

> *"[measured — `registry.py`, `open_hypothesis` signature] There is no `n_inherited` parameter and
> no `n_inherited` column."*

**That was true when it was written and is false now** [measured — `registry.py:83` declares
`n_inherited INTEGER NOT NULL DEFAULT 0` in `SCHEMA`; `_migrate` ALTERs it onto pre-existing DBs;
`open_hypothesis`'s signature carries `n_inherited: int = 0`; and it is the sixteenth entry of
`_BINDING_FIELDS`]. **I-018 / I-027 / C-001 §3.0 shipped the column this document says does not
exist.** Sealing §10.3 as written freezes a false statement of fact about the harness, permanently,
under P7 — and freezes with it the §21 disclosure line *"the 7-trial conditioning floor is declared
and unenforced (I-027)"*, which would then be false on the face of every Validation Report.

**The consequence is not cosmetic, and it runs against the firm.** `gates.py:565`:

```
declared_ceiling_base = fam.n_inherited + sealed
```

and B-18's contingent predicate is `allowed = clamp(N_max − declared_ceiling_base, 0, increment)`.
`VALIDATION-SPEC-003`'s own `test_tbe_15` fixes `base, inc = 54, 32` and reproduces §10.5.2's four
rungs exactly [cited — `harness/tests/test_trial_budget_enforcement.py:497–518`]. **54 = 7 + 47.**
At `n_inherited = 0` the base is 47, and §10.5.2's own table does not hold:

| Measured `ρ̂` | `N_max` [cited — SPEC-002 §6.2] | §10.5.2 declares | At `n_inherited = 7` (base 54) | **At `n_inherited = 0` (base 47)** |
|---:|---:|---:|---:|---:|
| ≤ 0.034 | 86 | "the whole of Stage 2" — 32 | 32 ✓ | 32 ✓ |
| ≈ 0.05 | 77 | "≤ 23 of the 32" | 23 ✓ | **30 — seven more than declared** |
| ≈ 0.10 | 55 | "≤ 1 of the 32" | 1 ✓ | **8 — eight times the declared allowance** |
| ≥ 0.20 | 31 | "NONE" | 0 ✓ | 0 ✓ |

*(All four `N_max` figures `[cited]`; the four right-hand columns are `clamp(N_max − base, 0, 32)`
evaluated by hand on already-cited integers — the same treatment §7.3 gives its counterfactual
product. **No harness call was made and no test was run.**)*

**The error runs PERMISSIVE at exactly the two rungs where the family is in trouble**, which is the
direction §10.5.2's whole staged construction exists to close. **A document that seals
`n_inherited = 0` describes a Stage 2 gate tighter than the one the harness would open** — I-105's
defect, one field over, and it would survive I-105's own repair. **Filed I-130, HIGH.**

**Why declaring 7 is not the §4.7.1 defect, addressed because a reader will raise it.** GATES.md
§4.7.1's test is: *"if a clause tells a sponsor to declare a quantity the registry already computes,
it is this defect."* **The registry does not compute `N_conditioning`.** It has no knowledge of
conditioning choices, menus, or pre-commitment discounts; it cannot derive 7 from anything it holds.
§4.7.1 governs *inheritance from a predecessor chain*, which `family_stats` does compute — and this
family's `predecessor_family` is `None`, so there is no chain, no transitive sum, and nothing to
double-count. `InheritedCountDoubleCountError`'s guard is explicitly conditioned on
`predecessor_family is not None` [measured — `registry.py`] and does not fire. **`n_inherited = 7` is
the field's documented purpose used for its documented purpose**: the docstring reads *"the prior
search attributable to THIS family and not already carried by its predecessor chain — declared,
phantom, no return series."* Seven menu-declared pre-measurement choices with no return series is
that quantity exactly.

**What it costs this family, stated because it is a cost and it is taken deliberately.** The
registry-enforced `N` at a full Stage 1 spend rises from 47 to **54**, and at full Stage 2 from 79 to
**86**. DSR is deflated against 86 rather than 79; MinBTL is evaluated at 86 rather than 79. **The
0.13-year I-027 residual §10.3 quantifies as this family's cost of the unenforced floor is not
mitigated — it is paid.** `MinBTL(86, SR 1.0) = 6.14 yr` against 6.571 available, margin 0.43 yr
[cited — §10.4, unchanged and already measured]. **This is the document's own "honest" row (§10.3)
becoming the enforced one, and no new number is required to say so** — both readings were already on
that table. §10.3's *"Registry as it will read"* row is what R-004 strikes.

**And it repairs c6.** `N_conditioning = 7` moves from category (c) — a floor nothing reads — to
category (a): a sealed field with four consumers. **That is §4.7.2's doctrine turned on this document
and producing an act rather than a disclosure**, which is the outcome the doctrine is for.

### 9.5 I-105 — the disposition chosen, and the argument for it

**The Principal offered two: register Stage 1 at 47 with §10.5.2's Stage 2 language surviving as the
description of a registered unlock event under SPEC-003's contingent form, or strike it before
sealing. This seat chooses the FIRST, and does not regard it as close.**

**Why not strike.** Striking makes the sealed budget 47 flat, with no route above it that does not
require a discretionary extension — which under B-14 needs a countersignature from a distinct seat,
which is a *person's* authorization rather than *arithmetic's*. **That is strictly worse on the axis
the firm cares about.** B-16: *"A contingent extension is authorized by a computation, not by a
person, and is therefore safe to self-issue… Forging the event buys nothing, because the number that
governs is recomputed."* Striking Stage 2 would replace an arithmetic gate with a human one and
would, on the way, forfeit the §10.5.2 argument that makes a PARK operational (a parked family that
keeps regenerating its forward window digs its own hole while waiting in it).

**Why the contingent form is not a favour to this family.** It is not a door the sponsor opens. The
predicate is `n_max_admits_declared_ceiling`, `params` empty and required-empty (B-17); the criterion
**recomputes** `N_max` at evaluation time and never trusts the event's assertion (B-16); the
aggregate cap is `max(0, N_max − declared_ceiling_base)` regardless of how many events are written
(B-20); unevaluable `N_max` gives `allowed = 0` and a FAIL, not INSUFFICIENT-DATA (B-19); and a
malformed event FAILS the criterion even where the family is comfortably inside its sealed budget
(B-23). **Every one of those runs against the sponsor.**

**The Stage 2 clause must be written as a plain instance of the generic mechanism, not as this
family's special construction.** `test_tbe_15` already reproduces §10.5.2's four rungs **without
knowing this document exists**, and B-22 makes genericity a tested property — `gates.py`'s source may
not contain `PREREG-002`, `rho_plan`, `0.034`, `stage_2`, or `crypto-funding`. **The document has no
standing to describe the mechanism; it may only declare an instance of it.** R-004 rewrites §10.5.2's
unlock rule accordingly, and I-104 is conformed in the same edit: the nine-row table is a rendering,
`stats.max_admissible_trials` is the function of which those rows are printed evaluations, and
**RULING 003-A rules that the function governs.** *"Never interpolated"* is struck; it described a
lookup with no defined value between its rungs.

### 9.6 What the four remaining suite reds do to this family's registration

`test_G2`, `test_h7`, `test_h8`, `test_mbs_12` are Validation-owned and were not touched, not run, and
not reported on. **Read only, to answer one question: does any of them bear on the registration act?**

| Red | What it grades | Bears on registration? |
|---|---|---|
| `test_G2` | `oos_index` calendar span is used and reported by the **length criterion** (`evaluate_gate1`) | **No.** Gate 1 evaluation. `open_hypothesis` has no calendar input |
| `test_mbs_12` | Corrected `MinBTL` is approximately frequency-invariant across bar aggregations | **No.** A property of `stats.min_backtest_length_years_serial`. §10.9(b) already establishes nothing in this document rests on frequency invariance in either direction |
| `test_h7` | DSR consumes the **seeded** denominator — `famU` at `n_inherited=0` PASSes, `famS` at 31,250 FAILs | **Not on the act. On what the act is worth.** `open_hypothesis(..., n_inherited=7)` executes today; `gates.py:779/:788` passes `fam.n_trials` (= 7 + logged) to `deflated_sharpe_ratio` [measured]. **Whether the 7 arrives intact at the DSR verdict is what h7 grades, and it is red** |
| `test_h8` | `MinBTL` consumes the seeded denominator and fails a short backtest | **Same.** `gates.py:856` passes `fam.n_trials` to `min_backtest_length_years` [measured] |

**The honest statement, and it is a change from what this seat would have written before R-004.** At
`n_inherited = 0` the answer was a clean "none of the four bears on registration," because a zero
seed makes h7/h8 inert for this family. **At `n_inherited = 7` that is no longer true.** h7 and h8 do
not block the act — nothing in them touches `open_hypothesis`, and the registration is mechanical and
executable today — **but they are exactly the two tests that determine whether the 7 this family is
about to seal is consumed by DSR and by MinBTL or is merely displayed on the report face.** This seat
does not own them, has not touched them, and states the dependency rather than assuming the code
paths it read are the ones under test. **Raised to Validation as a consequence of R-004, not as a
request.**

### 9.7 Issues filed by this audit

| # | Severity | Finding | Owner | Disposition |
|---|---|---|---|---|
| **I-130** | **HIGH** | `n_inherited = 0` makes §10.5.2's own unlock table permissive by 7 and by 8 trials at the two rungs that bind. `declared_ceiling_base = n_inherited + sealed` and SPEC-003's `test_tbe_15` fixes the base at 54 | director-of-research | **Discharged by R-004** — payload seals `n_inherited = 7` |
| **I-131** | MEDIUM | §10.3's *"there is no `n_inherited` parameter and no column"* is stale; sealing it freezes a false statement of harness fact, and with it a §21 disclosure line that would be false on every Validation Report | director-of-research | **Discharged by R-004** |
| **I-132** | MEDIUM | `log_trial` reads no budget. The trial budget is enforced retrospectively at `evaluate_gate1` and never at spend time; *"no Stage 2 trial is spent on an unmeasured `ρ̂`"* has no spend-time control, and trials cannot be unspent | quant-validation → head-of-data-infra | Open; disclosed on the face of §10.5.2 by R-004 |
| **I-133** | MEDIUM | Nine of the sixteen binding fields are sealed and read by nothing. The three fields a pre-registration puts its methodology in — `universe`, `horizon`, `success_criteria` — have **zero** consumers in the harness | quant-validation | Open — disclosure; not a repair request |
| **I-134** | MEDIUM | `published_signal_haircut_applied = 0.50` is applied by no code path. I-019 named it; this sizes it against this family, whose §5.4 derives a `t(α) ≈ 6.0` burden from a number nothing reads | quant-validation | Open |
| **I-135** | LOW | `forward_window_start`, `forward_window_min_length` and `forward_kill_condition` are inert for a FORWARD classification — presence-checked only when `HISTORICAL`. KC-002's *"silence is a kill"* has no harness trigger | quant-validation | Open |
| **I-136** | MEDIUM | §15's step table sums to **83** against a declared 79: diagnostics 8 (steps 4+5) vs §10.5.3's ≤7, and `N_forward` ≤25 (step 8) vs ≤22. R3/R6/R15's conforming passes did not reach §15's arithmetic — the same defect class R8(c) repaired | director-of-research | **Discharged by R-004** |

### 9.8 What §9 did not do

- **No seal, no registration, no registry write.** `book/registry.db` reads **0 hypotheses / 0 trials /
  1 event** [measured — read-only `SELECT COUNT(*)`, this session; the single event is `book_open`].
- **No `harness/` file touched, no test run, no suite state produced.** Every harness fact is a read.
- **No `VALIDATION-*` document touched. No `book/` write.**
- **I-045 not closed.** See §10.
- **No number computed.** Every `N_max`, `MinBTL` and `ρ̂` figure is `[cited]`. The arithmetic performed
  is `clamp` on already-cited integers and `2+1+2+2+6+25+20+25 = 83`, of the same class as R-002's
  `109 − 86 = 23`.

---

## 10. I-045 — DECLINED, FOR THE FOURTH TIME, AND WHAT C2 NEEDS IN ORDER TO RULE ON IT

**I-045's owner line reads `director-of-research → quant-validation` [cited — `logs/ISSUE_LOG.md`
I-045]. Closure is Validation's. This seat declines to close it, as it declined at R-001, R-002 and
R-003, and the reason has not changed and is not modesty.**

**What this seat has discharged is a different object.** R-001 removed SOL from the universe (R3) and
declared K7 (R5); R-002 discharged C12 (R12); R-004 changes neither. **C12 is a condition in this
seat's own document and C12 is discharged. I-045 is an Issue Log entry recording a data-homogeneity
defect, and discharging the remedy is not the same act as ruling the remedy sufficient.** A sponsor
closing an issue on the strength of its own repair is the structure the independent line exists to
prevent.

**What C2 needs in order to rule, stated as three answerable questions rather than as a request:**

1. **Is dropping SOL a sufficient remedy, or a scope reduction that leaves the finding live?** I-045's
   substance is that *a funding series can be regenerated by different formula parameters mid-sample
   without announcement*. **Removing the one symbol on which the firm caught it does not remove the
   exposure** — it removes the instance. R12 says so in the sealed text: `DATA-VERIFY-002`'s clean
   4,802 symbol-days verify the **cadence** dimension only, and the documented 2025-09-18 formula
   change shows 3 prints on both BTC and ETH, so **a cadence sweep is structurally blind to the
   parameter dimension** [cited]. Validation must rule whether K7's declaration is an adequate
   substitute for an instrument the firm does not have.
2. **Does K7 option (1) — 30 days at benchmark weight from a documented change date — cover the
   residual?** §17 risk #12 records the residual explicitly: *"an unnoticed change is still possible,
   since detection depends on Seat 9 observing it."* **C12's clean result does not narrow that
   residual by one day.** Validation must rule on a control whose trigger is a vendor announcement
   nobody is contractually obliged to make.
3. **Does I-045 close at Gate 0 intake, or does it survive the seal as a standing disclosure?** This
   seat's view, offered and not decisive: **it survives.** The defect is a property of the venue, not
   of the document, and a family whose forward window runs to `C + 187 days` carries it forward.

**All three are answerable inside C2's intake verdict and none of them requires a separate
dispatch.** C13 is the mechanism and R-004 adds a fourth item to it (§20).

---

*Director of Research · Castellan Capital · **addendum §9–§10 added 2026-08-10 for revision R-004***
*Dispatch S3-D-001. Trial budget ZERO. No hypothesis opened, no trial run, no vault sealed, `harness/`
not touched, `book/` not written to, no test executed, no suite state reported.*

---

# ADDENDUM — REVISION R-005 · 2026-08-10 · PRE-SEAL

## 11. THE CLASS MANDATE — every limit carries its class, or it stops calling itself a control

**Added 2026-08-10 for revision R-005.** Dispatch **S3-D-003**. **Trial budget: ZERO. No number
computed. `book/registry.db` reads 0 hypotheses / 0 trials.** Every harness fact below is
`[measured — read from source this session]` at the named file and line.

### 11.0 The mandate, and the one thing it is not

The Principal adopted this seat's I-133 conclusion verbatim: *"most of these cannot be mechanized and
should still be written down; what must stop is the document describing them as controls."* Three
classes, and **no limit may describe itself as a control without carrying its class**:

| Class | Requires |
|---|---|
| **(a) harness-enforced** | a **named code path**, and the **named field** it reads where one exists |
| **(b) procedure-enforced** | a **named executor**, a **named cadence**, and the **named artifact** the execution produces |
| **(c) declared commitment** | binding **as a matter of record**, enforced by **audit and adversarial review only** |

**This is a labelling mandate, not a mechanization mandate.** Nothing below is made enforceable that
was not. **A class-(c) label is a full and honourable answer.** This document declares **thirty-four**
class-(c) commitments and is stronger for saying so than it was implying sixty-one controls and
holding twenty.

> ### **A TAXONOMY COLLISION THIS SEAT CREATED AT R-004 AND MUST NAME BEFORE IT PROPAGATES.**
>
> **§9.3 of this memo already uses the letters (a) and (b), and it does not mean by them what the
> mandate means.** §9.3's *(a)* = enforced through a **sealed field**; §9.3's *(b)* = enforced by a
> **code path with no sealed field** (`SameBarFillError`, `grid.py:27`, the contingent-extension
> ledger). **Under the mandate's taxonomy every one of §9.3's "(b)" entries is class (a)** — they are
> harness-enforced; they simply read no sealed field.
>
> **A reader arriving at §9.3 with the mandate's vocabulary in hand would read "procedure" where there
> is code, and would conclude that a `ValueError` in `grid.py` depends on somebody remembering to run
> something.** That is the exact confusion this mandate exists to end, manufactured by the mandate's
> own letters landing on an earlier table. **§9.3 is therefore superseded as a taxonomy and retained as
> evidence**, and §11.2 below re-maps every row of it. The register in `PREREG-002` §10.11 uses the
> mandate's letters and only those.

### 11.1 The sixteen binding fields, reclassified — and §10.10's arithmetic corrected

**Method, reproducible rather than asserted:** for each of the sixteen names in
`harness/castellan/registry.py:80–91` (`_BINDING_FIELDS`),
`grep -rn "\b<field>\b" harness/castellan/ --include=*.py | grep -v registry.py`, then every surviving
hit read at its call site to establish whether it **enforces**, **renders**, or is an unrelated use of
the same English word [all measured, this session].

| # | Field | Non-`registry.py` hits | Of which real consumers | **Class** | (a): field + code path · (c): why |
|---:|---|---:|---:|---|---|
| 1 | `family` | 123 | many | **(a)** | `registry.py:485` `log_trial` → `PreRegistrationError` (A2); `predecessor_chain`; every `evaluate_gate1` lookup |
| 2 | `statement` | 5 | **0** | **(a)** existence · **(c)** content | `registry.py:262–268` raises on empty. The five hits are the English word in `cv.py`/`errors.py` |
| 3 | `mechanism` | 4 | **0** | **(a)** existence · **(c)** content | same check. The four hits are prose in `loaders.py`/`coverage.py`/`data.py` |
| 4 | `falsifier` | **0** | 0 | **(a)** existence · **(c)** content | same check. **F-002's entire specification is (c)** |
| 5 | `universe` | 3 | **0** | **(c)** | the three hits are the English word in `loaders.py` docstrings |
| 6 | `horizon` | **0** | 0 | **(c)** | — |
| 7 | `success_criteria` | **0** | 0 | **(c)** | — |
| 8 | `trial_budget` | 8 | 8 | **(a)** | `gates.py:562` `sealed = fam.trial_budget`; B-7 `sealed <= 0` → FAIL (`:598`); B-9 ordering walk → FAIL (`:606–620`); `declared_ceiling_base` (`:565`) |
| 9 | `predecessor_family` | **0** | 0 **outside** `registry.py` — **and enforcing inside it** | **(a)** | `registry.py:269–273` existence check; `:294–308` `InheritedCountDoubleCountError`; `predecessor_chain`; `family_stats`/`returns_matrix` transitive sum |
| 10 | `holdout_classification` | 5 | 5 | **(a)** | `registry.py:309–313` domain check; `:314–329` HISTORICAL → R3 presence requirement; `gates.py:1055`, `:165`, `:168` |
| 11 | `forward_window_start` | **0** | 0 | **(c)** for this family | presence-checked **iff** `holdout_classification == "HISTORICAL"` (`registry.py:314`). This family is **FORWARD** |
| 12 | `forward_window_min_length` | **0** | 0 | **(c)** | same; and the column is an unlabelled `REAL` (I-033(5)) |
| 13 | `forward_kill_condition` | **0** | 0 | **(c)** *as a field* | same. **The obligation it carries is (b)** — §11.3 B-01 |
| 14 | `model_prior_provenance` | **0** | 0 | **(c)** | — |
| 15 | `published_signal_haircut_applied` | **0** | 0 | **(c)** | no haircut computation exists in `gates.py`, `stats.py`, `engine.py` or `costs.py` |
| 16 | `n_inherited` | 15 | 15 | **(a)** | `registry.py:277–284` validators; `family_stats`; `gates.py:148–152` (H-12 render), `:542`, `:565`, `:779`, `:788`, `:856` |

> ### **THE CORRECTED PARTITION: FIVE (a) AND ELEVEN (c) — NOT 4 / 3 / 9.**
>
> **`PREREG-002` §10.10's count cells read 4 / 3 / 9 and its rosters name 4 / 4 / 8.** Both cannot be
> right and neither is:
>
> - the **"Read, but only as a check or a render — 3"** cell names **four** fields (`statement`,
>   `mechanism`, `falsifier`, *"plus `holdout_classification`"*);
> - the **"SEALED AND READ BY NOTHING — 9"** cell names **eight** (`universe`, `horizon`,
>   `success_criteria`, `model_prior_provenance`, `published_signal_haircut_applied`,
>   `forward_window_start`, `forward_window_min_length`, `forward_kill_condition`).
>
> **Where the 9 came from, which is the part worth recording.** It is **§9.2's count of category-(c)
> *limits* — c1 through c9 — transplanted into a column that counts *fields*.** Two different
> denominators, one number, in sealed text. **The roster is right and the count is wrong: eight fields
> have zero consumers, not nine.**
>
> **This is R8(c)'s and R22's defect class for the third time** — an internal contradiction between a
> count and its own roster, which P7 would freeze permanently and which no later artifact could
> reconcile. Found on this pass, repaired on this pass, disclosed rather than silently conformed.
> Filed **I-141, MEDIUM**.
>
> **The dispatch's own instruction inherits the error and this seat says so rather than executing it
> silently: S3-D-003 directs the relabelling of *"all nine zero-consumer binding fields."* There are
> eight. The roster it names is complete; the cardinal is not.**

**Three fields need one further distinction the mandate's letters do not supply, and it is load-bearing.**
`statement`, `mechanism` and `falsifier` are **(a) on existence and (c) on content.** `registry.py`
raises `ValueError` if any is empty or whitespace — a real code path, a real refusal. It reads not one
character further. **F-002 — four legs, three constructed series, α = 0.0013, an 1,800-bar floor, a
joint false-survival rate of 1.3 × 10⁻⁴ — is stored in a field whose only guarantee is that it is not
the empty string.** The document has never said otherwise, and it has never said this either.

### 11.2 Class (a) with no sealed field — §9.3's "(b)" re-mapped, and every row verified

**The mandate's question for class (a) is "named field, named code path."** Fourteen of this
document's real controls have the second and not the first. **They are class (a).** A `ValueError`
does not become a procedure because no sealed string triggers it.

| Limit as `PREREG-002` states it | Field | Code path [all measured] |
|---|---|---|
| No trial may be logged against an unregistered family (A2) | `family` | `registry.py:485` → `PreRegistrationError` |
| Every backtest routes through the engine; every grid point is a logged trial | — | `castellan.run_backtest`; `grid.run_parameter_grid` |
| A ±50% grid may not exceed 200 points | — | `grid.py:27` `ValueError` |
| Never fill at the bar that generated the signal | — | `engine.py` `SameBarFillError` |
| `N_max` is a recomputed **function**, monotone-conservative (R13) | — | `gates.py:344` `_admissible_ceiling` = `min(n_max_admissible_iid, n_max_admissible_serial)` |
| Stage 2 admits `clamp(N_max − 54, 0, 32)`, recomputed, never trusting the event (R20) | `n_inherited` + `trial_budget` | `gates.py:565`; `_budget_extension_ledger` `:378–398`; B-16…B-21 |
| A malformed, un-withdrawn extension FAILs even inside the sealed budget (B-23) | — | `gates.py` B-23 branch, checked ahead of B-7/B-8/B-9 |
| The live `hypotheses` row must match the sealed shadow copy; a mismatch FAILs (P4) | all sixteen, via `prereg_sha256` | `registry.verify_prereg`, **called automatically at `gates.py:991`** |
| A re-registration differing on any binding field is refused (P3) | all sixteen | `registry.py:356–369` `PreRegistrationAmendedError` |
| The seal must not postdate `C` at UTC day granularity (P7) | — | `gates.py` P7 branch, `sealed_created_utc` vs the vault's `holdout_spec_sealed.cutoff` → FAIL |
| No `hypothesis_sealed` event ⇒ INSUFFICIENT-DATA, never PASS (P6) | — | `gates.py:1003` |
| The holdout is acquired exactly once | — | `HoldoutVault.acquire_once()`; the "Holdout single-use" criterion |
| The graded `t` is `min(t_NW, t_raw)` and never the raw figure (I-050 / E-8) | — | `stats.py:153`, `:221`; `gates.py:752` |
| `\|ρ̂\| ≥ 0.97` or `n_logged = 0` ⇒ INSUFFICIENT-DATA, never PASS (E-9) | — | `stats.py:177–188` |
| Carry is a signed cash flow; `CostModel.scaled(m)` never multiplies it (T-16) | — | `costs.py:119–128` (no `funding_bps_annual` on `CRYPTO_PERP_TAKER`); `carry.py` |
| The registry-`N` decomposition is rendered on every report face for a seeded family (H-12) | `n_inherited` **≠ 0** | `gates.py:148–152` |
| The holdout-classification line is rendered on every report face (R1) | `holdout_classification` | `gates.py:165` |

> **Two of these deserve their disclosure repeated rather than buried.**
>
> **`SameBarFillError` and `grid.py:27` read no sealed field and would fire identically for a family
> that declared the opposite.** They are class (a) and they are **not** enforcement of anything this
> document says. R-004 said this and it survives the reclassification unchanged.
>
> **P3/P4 are tamper-EVIDENCE across all sixteen fields and tamper-PREVENTION on none.** A raw
> `UPDATE hypotheses SET universe = ...` succeeds. What fails is the next `evaluate_gate1`, because
> the sealed event carries a **full shadow copy** rather than a pointer to the row that was changed —
> and because `verify_prereg` is called by the gate rather than by a person. **That last clause is
> what makes it (a) rather than (b), and this seat checked it rather than assuming it**
> [measured — `gates.py:991`].

**The last two rows are the mandate's one upgrade, and it is small and real.** Two of the eleven
mandatory disclosure lines are **written by the engine itself** and cannot be omitted by a seat that
forgets. One of them — *"registry N = n_inherited 7 … + logged"* — **became class (a) at R19**, because
`gates.py:148` branches on `if self.n_inherited:` and the branch was dead while the field was 0.
**R19 was argued as a tightening of the denominator; it also, unnoticed until this pass, moved one
disclosure line from (c) to (a).** The other nine remain (c).

### 11.3 Class (b) — the strict test, applied strictly

**The CIO's warning is correct and this seat treats it as a filter rather than as advice:** a limit is
(b) only if all three of executor, cadence and artifact can be named. *"The Director will check"* is
not a cadence and produces no artifact. **Seven limits pass. Everything that failed the test is in
(c), including two that this seat would have been tempted to promote.**

| # | Limit | **Executor** | **Cadence** | **Artifact** |
|---|---|---|---|---|
| **B-01** | **KC-002 is computed on `C` + 187 days, and silence is a kill** | **the Principal** | **the weekly Friday ritual, alongside the pull-and-merge** | **the pasted evaluation attached to the record, per `TEMPLATES.md` §7.9** |
| **B-02** | Has any pre-registered falsifier been hit and not acted on (F-002) | **Director of Research** | **Friday 16:00, Weekly Research Review** — Charter §6.3 item 4 | **the weekly pipeline status**: every hypothesis by stage with age, trial count, next action |
| **B-03** | A Red-Team Memo with a binding named kill condition is present (C3) | **Devil's Advocate** | **every Gate 1 submission and every IC packet** — Charter §6.4: a packet without one is *deferred, not heard* | **the Red-Team Memo** |
| **B-04** | The Gate 0 intake verdict, and the C13(a)–(h) items ruled with it (C2) | **Head of Quantitative Validation** | **once, at intake, before the seal** | **the Intake Verdict** — ADMITTED / REJECTED / ADMITTED-AS-EXPLORATORY |
| **B-05** | Sponsor acceptance of KC-002 and the Principal's signature before any capital (C7) | **PM Pod B + the Principal** | **once, before any allocation** | **the signed acceptance in `logs/DECISION_RECORD.md`** |
| **B-06** | Vault sealed in the same session and UTC day as `open_hypothesis` (C8) | **PM Pod B + the Principal** | **once, at the seal** | **the `holdout_spec_sealed` event and the vault under `book/vaults/`** |
| **B-07** | Reconciliation breaks are filed verbatim and never repaired | **Execution & Operations** | **every Close & Reconcile, weekdays 17:15** | **the reconciliation note in the Daily Risk & P&L Pack** |

**B-01's transition to (a) is named, because the Principal required it named.** KC-002 reverts to
class **(a)** when **Validation's harness kill-condition evaluator** lands — **specced this sprint,
not yet dispatched.** Until it does, *"a kill condition that can be defeated by not running it is not
a kill condition"* is a clause enforced by a person on a calendar. **This seat wrote that clause,
defended it, and now labels it (b): "defeatable by not running it" cannot describe a
signature-required clause, and the honest repair is to name who runs it rather than to hope.**

**B-06 is the execution of a limit that is itself class (a).** The *act* is procedural; its *violation*
is caught by the P7 branch at `gates.py`. Both are recorded because a reader who saw only the (a) row
would not know a human has to do something on the day.

> ### **TWO THINGS THIS SEAT DEMOTED TO (c) AFTER TRYING TO MAKE THEM (b). THEY ARE THE WORKED
> EXAMPLES OF THE CIO'S WARNING.**
>
> **F-002's E2 — *"evaluated ONCE. There is no re-run 'with the corrected costs,' no second look, and
> no 'we also checked.'"*** The three F-002 runs are logged trials, so a second evaluation would be
> **visible in the ledger afterwards**. It is tempting to call that an artifact and file E2 as (b).
> **It is not.** The artifact is produced by the act being limited, not by any check on it; **no seat
> and no cadence is named for asking the question.** E2 is **class (c)** — binding as a matter of
> record, discoverable by audit, prevented by nothing.
>
> **§12.8's *"No hand-rolled number, under any circumstance."*** The presets exist
> (`CRYPTO_PERP_TAKER`, `CRYPTO_SPOT_TAKER` — D-013 §1) and using them is easy. **Nothing refuses a
> literal float.** There is no executor, no cadence, no artifact. **Class (c)**, and the Charter's
> Seat-9 standing rule is a discipline rather than a gate.

### 11.4 THE DISPATCH'S HARDEST QUESTION — does any limit claimed as (a) fail its own test?

**The instruction was to check all sixteen fields and every non-field limit rather than assume §9.2's
nine were exhaustive, and that "a tenth would be the more valuable finding."**

> ### **ANSWER: NO. ALL TWENTY CLASS-(a) LIMITS VERIFY AT SOURCE. THE TWO FINDINGS RUN THE OTHER WAY,
> AND ONE OF THEM IS THE MOST CONSEQUENTIAL THING IN THIS REVISION.**

**Every row of §9.3 was re-read at its call site this session and every one holds.** The one this seat
expected to fail did not: `verify_prereg` is invoked **by `evaluate_gate1` itself** (`gates.py:991`),
so pre-registration integrity is checked automatically rather than on request. **No limit this
document claims as harness-enforced turns out not to be.**

**What this audit found instead: two limits the document states are NOT enforced, and which ARE.**
**That is R19(b)'s defect class exactly — a false statement of harness fact about to be frozen by P7 —
running in the conservative direction, which is why four revisions passed over it.**

---

#### 11.4.1 · **I-034 / C1 IS IMPLEMENTED. THIS DOCUMENT DESCRIBES THE PRE-REPAIR COST MODEL AT SIX SITES, AND ONE OF THEM DOWNGRADES THE FAMILY TOMORROW.**

`harness/castellan/costs.py`, read this session [measured]:

```python
CRYPTO_PERP_TAKER = CostModel(
    name="crypto_perp_taker", commission_bps=5.0, half_spread_bps=1.0,
    impact_y=1.0, periods_per_year=365,
    # No funding term (Ruling 003, I-034): funding is a signed cash flow
    # and is accrued in the engine from the realized `pit_funding_panel`
    # series, never as a scalar rate here.
)

CRYPTO_SPOT_TAKER = CostModel(          # D-013 §1, Principal-authorized
    name="crypto_spot_taker", commission_bps=10.0, half_spread_bps=2.5,
    impact_y=1.0, periods_per_year=365,
)
```

`harness/castellan/carry.py` exists and supplies the sanctioned carry-stress path, with
`carry_breakeven_bps_annual` monotone in its shift by construction. `DATA-IMPL-004` §5–§6:
***"All nineteen T-cases … are implemented and pass with the assertions Validation authored"*** [cited].
`VALIDATION-RULING-003`'s header names its own target: ***"Blocks: PREREG-002 condition precedent
C1"*** [cited].

**Six sites in `PREREG-002` still describe the world of 2026-07-28:**

| Site | What it says | Status [measured] |
|---|---|---|
| **§1 recommendation box, breakeven row** | *"Cannot be stated… charges funding as a cost on gross notional… **−21.9%/yr** where the strategy receives +10.95%. The sign is inverted and the base doubled"* | **False.** The field does not exist on the preset |
| **§12.1** | quotes the preset **with `funding_bps_annual=1095.0`** | **The quoted object does not exist** |
| **§12.2 / §12.3 / §12.6** | defects (a) sign inverted, (b) funding is a constant, (e) `scaled(2.0)` stresses the error | **All three repaired.** T-16: `scaled(m)` leaves carry bit-identical |
| **§16 row 1** | *"Cost robustness at 2× — evaluable but currently meaningless"* | **False.** `carry.py` is the sanctioned path and `scaled` no longer touches carry |
| **§17 risk #1** | *"Every net number is wrong by 32.85 points/yr… **blocking on every net claim, including the paper book**"* | **False** |
| **§14, KC-002's condition precedent** | *"the **C1 cost-model repair** is implemented by sprint close, **2026-08-11**. **If unresolved by that date, the family is ADMITTED-AS-EXPLORATORY only**"* | **Resolved.** The downgrade must not fire |
| **seal-readiness block** | *"C1 · DISCHARGED as a specification; **implementation open as I-034**"* | **The implementation landed on 2026-07-29** |

**Why this is the more valuable finding, stated without inflating it.** It cannot produce a wrong
PASS — every error runs *against* the family. But **it is one calendar day from producing a real,
mechanical consequence: KC-002's condition precedent downgrades this family to
ADMITTED-AS-EXPLORATORY tomorrow, on a premise that is false**, and ADMITTED-AS-EXPLORATORY is
*"pre-declared ineligible for Gate 1"* (Charter §4.3). **A family that has spent three sprints earning
an ADMITTED recommendation would lose it to a stale sentence.** And §15's step 0 blocks the whole test
plan on a condition already met, which is a direct cost in the sprint whose stated objective is *"the
science or it is nothing."*

**Filed I-140, HIGH.** The HIGH rating is a **Standing Order 002 §4 hard interrupt** and this seat
records that the interrupt is a **consequence of the severity, not a purpose of the filing**: the
rating is what a sealed document permanently misstating the firm's cost library, at the clause that
decides ADMITTED versus ADMITTED-AS-EXPLORATORY, with the deadline tomorrow, honestly is.

**What this seat does NOT do.** **It does not close I-034 and it does not close C1.** I-034's owner
line routes to `quant-validation → head-of-data-infra`; C1's routes the same way. **This seat records
the measurement and conforms its own document; the closure is somebody else's act, exactly as R12
recorded C12's discharge while declining I-045's.** Two residuals survive and are stated so the
conformance is not read as broader than it is:

1. **§12's defect (d) is NOT repaired.** `CostModel` still has **no field that can charge
   liquidation or venue-insolvency risk** — the largest risk in the mandate. `VALIDATION-RULING-003`
   §4 declines to invent a number and says so. **That defect stands, is class (c), and is disclosed.**
2. **The breakeven cost is still unstated** — but the reason changes, and the change matters.
   **It is no longer "unstateable because the instrument is broken." It is "unstated because computing
   it is a trial and this dispatch's budget is ZERO."** `carry.carry_breakeven_bps_annual` is the
   house-rule-5 instrument and it exists. **House rule 5 is now satisfiable by this family and is not
   yet satisfied.**

---

#### 11.4.2 · **I-022 IS REPAIRED IN CODE AND OPEN IN THE LOG, AND THREE CLAUSES REST ON IT BEING LIVE**

I-022 as filed [cited — `logs/ISSUE_LOG.md:598`]: `gates.py` built the trial-count criterion with the
verdict hard-coded to the literal `True`, so *"a family that has blown its pre-registered trial budget
reports **PASS**."* **Resolution line still reads `open`.**

`gates.py:527–640`, `_trial_budget_criterion`, read this session [measured]. **The literal `True` is
gone and the code that replaced it fails in three separate ways:**

- **B-7:** `sealed <= 0` with logged trials → **FAIL**, *"NO AUTHORIZED BUDGET"* (`:598`);
- **B-9:** an ordering walk **per trial, not per aggregate** — the k-th trial logged above the
  then-effective budget → **FAIL**, naming k (`:606–620`);
- **B-23:** a malformed, un-withdrawn extension → **FAIL**, *"checked ahead of B-7/B-8/B-9"*.

**Three clauses in this family's own papers rest on the defect being live:**

| Where | What it says | Status |
|---|---|---|
| `PREREG-002` §20 **C10** | *"Until then the **47-trial authorized** budget is enforced by this seat and by nothing else"* | **False** |
| `PREREG-002` §10.5.2, the objection paragraph | *"**I-022** … means the budget is still enforced by this seat and by nothing else"*, and *"the only control against that is that this sentence is in a sealed document"* | **False** |
| `REGISTRATION-PAYLOAD` §4 | *"**I-022** — `gates.py` hard-codes a trial-count verdict to the literal `True` in one branch"* | **False** |

**The correct statement, which is neither the old one nor a naive repair.** The budget is enforced
**retrospectively and it FAILs the gate**. **I-132 stands unchanged:** `log_trial` reads no budget
[measured — `registry.py:477–502`], so nothing *prevents* an over-budget spend and trials cannot be
unspent. **Prevention: none. Detection and refusal: automatic, per trial, with the offending trial
named.** §10.5.2's two-stage construction — *"a budget with a door in it, and doors get opened under
schedule pressure"* — has a **better defence than the document gives it**, and this seat, who built
the two-stage budget and would benefit from overstating its protection, notes that the correction here
runs **in this family's favour** and states it for that reason rather than in spite of it.

**Filed I-142, MEDIUM.** Not HIGH: it produces no downgrade, no wrong PASS, and no dated consequence.
**C10's weight, raised at R-003 and raised again at R-004, now falls** — and the honest reading is that
it should never have been raised the second time, because the repair had already landed.

### 11.5 THE HAIRCUT — how it is resolved, and whether §19.3's expectation moves

**The Principal's instruction is specific: the `t(α) ≈ 6.0` derivation must name its computing path or
carry class (c) explicitly, and if nothing computes it the document must say so *where it is relied
upon*, not only where it is declared.**

> ### **RESOLUTION: CLASS (c), EXPLICITLY, AT ALL THREE POINTS OF RELIANCE. NOTHING COMPUTES IT.**
>
> `grep -rn "published_signal_haircut_applied" harness/castellan/ | grep -v registry.py` → **zero
> hits** [measured]. There is **no haircut computation anywhere** — not in `gates.py`, not in
> `stats.py`, not in `engine.py`, not in `costs.py`. The field is stored, hashed into
> `prereg_sha256`, shadow-copied into `hypothesis_sealed`, and **read by nothing**.

**The three points of reliance, and R-005 marks each:**

| Where | What is derived from the 0.50 | Class |
|---|---|---|
| **§11.6** | the presumption accepted in full, no exemption sought; *"it bites, and this seat states the cost"* | **(c)** — where it is **declared** (R-004 already marked this) |
| **§5.4** | *"clearing Gate 1's t-hurdle post-haircut requires a pre-haircut `t(α) ≈ 6.0`, twice F-002's bar"* | **(c)** — R-005 marks it **here, where it is relied upon** |
| **§19.3** | the order-20 composite, and the pre-registered expectation of **PARK-WITH-TRIGGER** | **(c) composed with (a)** — R-005 marks it |

---

#### **§19.3'S EXPECTATION: THE POINT ESTIMATE DOES NOT MOVE. ITS BASIS SPLITS, AND A NEW BRANCH APPEARS THAT RUNS PERMISSIVE.**

**§19.3's composite is `3.0 × 2 (haircut) × 3.3 (I-050 inflation) ≈ 20`.** Under the class mandate the
two multipliers are **not the same kind of object**, and until this pass the document treated them as
though they were:

| Multiplier | Class | Evidence |
|---|---|---|
| **3.3× — the I-050 estimator correction** | **(a)** | `t_gate = min(t_NW, t_raw)` is *"the ONLY figure graded (E-8)"* [measured — `stats.py:153`, `:221`; `gates.py:752`]. **Implemented, shipped, and unavoidable** |
| **2× — the published-signal haircut** | **(c)** | **No code path. Enforced by Validation applying Charter §4.6 by hand — and C5, the ruling on *where* to apply it, is unruled** |

**What follows, stated as arithmetic rather than as concern.** The bar `evaluate_gate1` will actually
compute is **`t_gate ≥ 3.0` on un-haircut net returns.** The bar Charter §4.6 says this family must
clear is the equivalent of **`t_gate ≥ 6.0`.** **The gap is exactly 2×, it sits at the family's single
largest stated hurdle, and it runs in the permissive direction.**

> **Does §19.3's expectation move? This seat's answer, given plainly because a hedged one would be
> worse than useless:**
>
> **No — the expectation of PARK-WITH-TRIGGER does not move, and it is not restated.** It was a
> judgment about what this payoff can deliver, and it remains one.
>
> **What moves is the failure mode attached to it, and it moves against the firm.** Before this pass,
> §19.3 described **one** way to be wrong: the family clears F-002 and then PARKs. **There is now a
> second, which the document did not carry: if C5 is never ruled and no seat applies §4.6 by hand,
> this family can be reported as PROCEED at a bar half the one the Charter sets.** A PARK that should
> have been a PARK is a correct outcome. **A PROCEED that should have been a PARK is the failure this
> firm exists to prevent, and it is now a named, reachable branch rather than an unexamined
> assumption.** R-005 records it at §5.4 and §19.3.
>
> **This is the mandate paying for itself in one line.** The relabelling did not weaken the
> expectation; it exposed a permissive branch that a document describing prose as a control could not
> have seen.

**Filed I-143, MEDIUM.** Distinct from I-134, which records that nothing applies the haircut. **I-143
is the sizing and the placement**: the gap is 2× at Gate 1's t-criterion, one of the two multipliers
building the family's pre-registered expectation is class (a) and the other is class (c), and **C5 is
the only thing that closes it.** Put to C2's intake at **C13(i)**.

### 11.6 The payload — unchanged, and the sense in which that is true

> ### **NO BINDING FIELD'S VALUE CHANGES. `trial_budget = 47`. `n_inherited = 7`. THE SIXTEEN
> LITERALS ARE EXACTLY AS `REGISTRATION-PAYLOAD-PREREG-002.md` §1 records them.**

**The relabelling forced no payload change, and this seat states plainly that it went looking for
one.** The natural candidate was `published_signal_haircut_applied`: if no code applies it, is 0.50
still the honest value? **Yes, and the reasoning is short.** The field's value is a *declaration of
which presumption the sponsor accepted*, and the presumption was accepted in full. **A field being
unread is not a reason to write a different number into it — that would be the I-046 error inverted,
adjusting a declaration to match the enforcement rather than adjusting the description of the
enforcement to match the truth.** The number stays; the sentence about what it does changes.

**Three prose fields receive conforming inserts, and this is the R-004 mechanism, not a new one.**
`success_criteria`, `forward_kill_condition` and `model_prior_provenance` gain text, exactly as
R-004's own §3.1 table records four such inserts. **The document is UNSEALED**, `book/registry.db`
holds **0 hypotheses / 0 trials**, and **P7 has not bitten** — so a prose-field edit is a draft edit,
not an amendment. **This is not a Standing Order 002 §4 interrupt on payload grounds.**

**I-140 IS an interrupt, on its own severity.** The two facts are separate and are stated separately
so that neither borrows the other's weight.

### 11.7 Issues filed by §11, with the rating reasoning exposed

| # | Finding | Severity | Why that rating and not the one above or below |
|---|---|---|---|
| **I-140** | **I-034 / C1 is implemented; `PREREG-002` describes the pre-repair cost model at six sites, one of which downgrades the family to ADMITTED-AS-EXPLORATORY on 2026-08-11 on a false premise** | **HIGH** | Not MEDIUM: it has a **dated, mechanical consequence one day away** that costs the family its Gate 1 eligibility, and P7 would freeze the misstatement permanently. Not higher: every error runs *against* the family and **none can produce a wrong PASS** |
| **I-141** | **`PREREG-002` §10.10's field-count arithmetic — 4 / 3 / 9 against rosters of 4 / 4 / 8; the 9 is §9.2's count of category-(c) *limits* transplanted into a column counting *fields*** | **MEDIUM** | Same rating as **I-136** for the identical defect class — an internal contradiction between a count and its own roster, which P7 freezes and no later artifact can reconcile. Not LOW: it was propagated **into this dispatch's own instructions** before anyone measured it |
| **I-142** | **I-022 is repaired and passing (`DATA-IMPL-007`, all 19 green, 2026-08-05) and reads `open` in the log; C10 and two further clauses rest on it being live** | **MEDIUM** | Not HIGH: no downgrade, no dated consequence, no wrong PASS, and the error runs conservative. Not LOW: **C10's weight was raised twice — at R-003 and again at R-004 — after the repair had already shipped**, so the stale entry actively distorted two revisions |
| **I-143** | **The published-signal haircut's 2× gap at Gate 1's t-criterion: one multiplier of §19.3's expectation is class (a) and the other class (c), and the (c) one runs permissive** | **MEDIUM** | Not a duplicate of **I-134**, which records that nothing applies the haircut. **I-143 sizes it (2×), places it at the two points of reliance, and names the branch it opens — a PROCEED at half the Charter's bar.** Not HIGH: closable by a single C5 ruling already queued at intake |

**No issue is filed for the eight zero-consumer fields themselves.** They are **I-133**, already filed,
and the mandate's whole point is that a class-(c) label is a full answer rather than a defect report.
**Filing eight issues to say "prose is prose" would be the theatre this order exists to end.**

### 11.8 What §11 did not do

- **No seal, no registration, no registry write, no vault.** `book/registry.db` reads **0 hypotheses /
  0 trials** and read 0 / 0 when this section was put down.
- **No `harness/` file touched, no test run, no suite state reported.** `test_h7` and `test_h8` are
  Validation's queue and were not approached.
- **No `VALIDATION-*` document and no `book/` artifact touched.**
- **No issue closed.** **I-034, I-022, I-045 and C1 are recorded as measured and routed to their
  owners.** Recording a measurement and closing an issue are different acts and this seat holds only
  the first.
- **No declared menu edited. No selection moved. `N_conditioning` remains 7.**
- **No number computed.** The only arithmetic is `4 + 4 + 8 = 16` and `5 + 11 = 16`, on the sixteen
  entries of `_BINDING_FIELDS`, and the class counts `20 + 7 + 34 = 61`.

---

*Director of Research · Castellan Capital · **addendum §11 added 2026-08-10 for revision R-005***
*Dispatch S3-D-003. Trial budget ZERO. No hypothesis opened, no trial run, no vault sealed, `harness/`
not touched, `book/` not written to, no test executed, no suite state reported.*

---

# ADDENDUM — REVISION R-006 · 2026-08-11 · PRE-SEAL

*Dispatch **S3-D-006**. Trial budget **ZERO**. `book/registry.db` reads **0 hypotheses / 0 trials /
1 event** [measured — read-only `SELECT COUNT(*)`, this session]. No `harness/` file touched, no
`VALIDATION-*` document touched, no `book/` artifact written, no test run, no suite state reported,
no commit. `test_h7` / `test_h8` not approached.*

## 12. THE PRINCIPAL'S I-034 RULING APPLIED TO THE DOCUMENT — and the dated-clause sweep it mandates

### 12.1 What was ruled, and the one thing it does NOT do

**Ruled by the Principal, 2026-08-11:** **I-034 is CLOSED**, satisfied **2026-07-29** on commit
`875874f`'s evidence, recorded 2026-08-11, discovery credit **R-005**. **Condition precedent C1 is
DISCHARGED, not extended** — *"a family does not get downgraded because its paperwork didn't learn
what its repository did."*

**The residual is retained and is not swept up with it.** §12 defect **(d)** — `CostModel` has no
field that can charge liquidation or venue-insolvency risk, the largest risk in the mandate — stands
as **class (c), C-25** in the §10.11.4 register. `VALIDATION-RULING-003` §4 declines to invent a
number for it and R-006 does not invent one either. **It is not a condition precedent, because there
is nothing to wait for.**

**One fact this seat did not have at R-005, supplied by the CIO** [cited]: **commit `875874f`'s own
message reads *"Closes I-034."*** The work landed, the commit announced the closure, and
`logs/ISSUE_LOG.md` read *"open — blocking execution of PREREG-002"* for **thirteen days**. R-005's
finding is therefore the **fourth instance of I-092's class** — a closure recorded somewhere the
index never reached — and **the first with a dated consequence attached.**

### 12.2 THE SITE ROSTER — AND THE CARDINAL "SIX" IS WRONG AT EVERY READING

**I-140 states *"six sites."* Its own roster in the same sentence names seven groups. R-005's R26
"clause changed" column names eleven. The set R-006 must actually touch is fourteen.** The cardinal
has never agreed with any roster it has been written beside, and it has now propagated into a CLOSED
Issue Log entry (*"Six stale document sites corrected at R-006"*) and into dispatch S3-D-006's own
task heading.

**This is I-141's defect class for the fourth time** — R8(c) (three surviving instances of a
superseded budget), R22 (§15's step table summing to 83 against 79), R25 (§10.10's 4/3/9 against its
own 4/4/8), and now this. **Filed I-150, LOW-MEDIUM.** LOW because no consequence follows from the
cardinal — the roster is what anyone acts on, and every roster written has been complete or nearly
so. **Not lower, because it propagated twice: once into the Issue Log's closure text and once into a
dispatch, which is precisely the escape route I-141 was rated MEDIUM for.**

**The fourteen sites R-006 corrects**, partitioned by what is wrong with each:

**(A) Sites that state C1 is open, conditional, or not this seat's to close — seven:**

| # | Site | What it said |
|---|---|---|
| S-1 | §1 recommendation box, *Verdict sought* | *"ADMITTED … conditional on **C1**, C3 and C11"* |
| S-2 | §12's R26 note | *"does NOT close I-034 and does NOT close **C1**"* |
| S-3 | §12.3 | *"It is condition precedent **C1** and it is Validation's to specify, not this seat's to implement"* |
| S-4 | §12.8 (two rows) | *"if **C1's** specification calls for one"* · *"routed per Validation's **C1** specification"* |
| S-5 | §19 verdict + §19.2 spend table | *"ADMITTED, conditional on **C1**, C3 and C11"* · *"**C1** … everything else is blocked on it"* / *"Any net-P&L claim … before **C1** lands"* |
| S-6 | §20's C1 row | *"DISCHARGED IN SUBSTANCE, AND THIS SEAT DOES NOT CLOSE IT"* |
| S-7 | seal-readiness block, R-005 row | *"Formal closure of I-034 and of **C1** routes to `quant-validation → head-of-data-infra`"* |

**(B) Sites that still describe the pre-repair cost model, all inside §21 — the SEALED field block,
where the text is hashed into `prereg_sha256` — three, and this is the half R-005 did not reach:**

| # | Site | What is still there, un-struck |
|---|---|---|
| S-8 | `success_criteria`, COST-STACK paragraph | the whole pre-repair diagnosis — *"−21.9%/yr charged … THE SIGN INVERTED AND THE BASE DOUBLED"*, *"there is no `CRYPTO_SPOT_TAKER` preset"*, *"`scaled(2.0)` doubles `funding_bps_annual` to 2190"* — closing with **"NO NET NUMBER FROM THIS FAMILY, IN ANY DOCUMENT OR IN THE PAPER BOOK, IS ADMISSIBLE UNTIL C1 LANDS."** |
| S-9 | `forward_kill_condition`, condition-precedent sentence | *"the C1 cost-model repair is … implemented by **2026-08-11**; if unresolved by that date the family is **ADMITTED-AS-EXPLORATORY** only"* — **the exact sentence that made I-140 a HIGH, struck in §14's prose at R-005 and left standing in the field** |
| S-10 | `falsifier`, E2 | *"the first complete run of the three series **after C1 lands**"* · *"**If C1's repair changes the cost stack** after F-002 has been computed …"* |

> **S-9 is the finding inside the finding.** R-005 struck the condition precedent where a **reader**
> meets it (§14) and left it standing where the **registry** meets it (§21). The R26 note that
> corrects it sits **roughly forty lines further down the same field.** A field is hashed as one
> string; a reader of that string encounters the downgrade before the correction. **The repair R-005
> is credited with was made in the prose and not in the payload — which is I-105's lesson
> (*"a control exists where the harness reads it, and nowhere else"*) arriving from the opposite
> direction: a correction exists where the seal reads it, and nowhere else.**

**(C) Sites conformed at R-005 and re-checked at R-006, correct as they stand — four:** §12's R26
header block, §12.1's preset quotation (correctly labelled *"as shipped ON 2026-07-28"*), §15 step 0,
§16's cost-robustness row. **Named so their absence from the edit list is legible rather than an
omission.**

### 12.3 WHAT HOUSE RULE 5's DISCHARGE ACTUALLY COSTS — AND IT IS NOT ONE TRIAL

**I-140 records, R-005 repeats, and dispatch S3-D-006 restates: *"one trial inside Stage 1's 47
discharges house rule 5."* This seat measured the instrument and the figure is wrong.**

`carry.carry_breakeven_bps_annual(net_returns_at_shift, bracket=(0.0, 2000.0), iters=40)`
[measured — `harness/castellan/carry.py:81–123`] takes a **callable**, not a return series, and
evaluates it:

- once at `bracket[0]` (`:107`), for the base series and the HAC lag;
- once at `bracket[1]` (`:113`), for the ceiling check;
- **once per bisection step**, `iters` times (`:116–122`).

**At the shipped default that is 42 evaluations.** The harness's own sanctioned usage — T-18,
`harness/tests/test_carry_accounting.py:580–592` — implements the callable as a **`run_backtest` call
per shift** [measured], and `run_backtest` calls `registry.log_trial` unconditionally
(`engine.py:248`). **Forty-two logged trials, each a row in `trials`, each feeding `fam.n_trials`,
each deflating DSR and raising MinBTL.**

**Against Stage 1's 47 that is not a rounding error — it is 89% of the authorized budget for a
statistic that contains no selection of any kind.**

**The honest cost, stated as a schedule rather than a scalar:**

| Path | Trials | Why |
|---|---:|---|
| **F-002 fires (this seat's pre-registered expectation, §19.3)** | **0** | `t_lo < hurdle` returns `lo` at `:111–112` **before evaluating anything else**. On a family whose net `t` is below 3.0 the breakeven **is** 0.0 bps/yr, by construction, and the δ=0 series is step 3's own already-logged trial. **The KILL memo's house-rule-5 line is free.** |
| **F-002 survives, `iters = 8`, bracket unchanged** | **9** | 1 ceiling check + 8 bisection steps, δ=0 supplied from step 3's cached engine output. Resolution `2000 / 2⁸` = **7.8 bps/yr** on a carry of 11.86%/14.07% [cited — `DATA-INGEST-002` §4]. |
| **F-002 survives, shipped default `iters = 40`** | **41** | Resolution `2000 / 2⁴⁰`. **Absurd precision bought with the family's entire denominator.** |

**Two things this seat will NOT do to make the number smaller, and they are stated because both are
available and both are wrong.**

1. **It will not narrow the bracket.** `carry_breakeven_bps_annual` returns the **bracket endpoint**
   when the breakeven lies outside it (`:111–115`). `VALIDATION-SPEC-002` §1286 records that this
   function has already once *"returned its bracket ceiling"*, and I-037 names returning a search's
   ceiling as fabricated robustness. **Narrowing the bracket to save trials is the I-037 operation
   performed on the instrument built to avoid it.** Reducing `iters` costs resolution only and can
   never move an endpoint.
2. **It will not construct the shifted net series outside the engine.** The shift is a per-bar
   constant, so `net(δ)` is arithmetically recoverable from one run's positions and carry accrual —
   **at a cost of zero trials and in direct breach of A2**, which makes a number produced outside the
   engine inadmissible. **That is a Validation ruling, not a researcher's convenience**, and it is
   put to C2 rather than taken.

**Does this seat intend to spend it? Yes, conditionally, and the condition is already the
pre-registered expectation.**

> **Nine trials, at `iters = 8`, bracket `(0, 2000)` unchanged, as a new §15 step 3b — spent ONLY if
> F-002 survives in full. On the KILL path it costs nothing and is reported anyway.**

**And it does not fit.** §15's Stage 1 line items sum to **exactly 47** — `2 + 1 + 2 + 2 + 5 + 25 + 10`
[integer arithmetic on already-declared line items] — **zero slack.** So R-006 records the arithmetic
and **does not move the sealed `trial_budget`**, which stays at 47 and is not this revision's to
touch. Three exits exist and this seat names its preference without taking it:

| Exit | Cost | This seat's view |
|---|---|---|
| Spend the 9 from **Stage 2's contingent 32** | Stage 2 falls to 23 | **Preferred.** Stage 2 is contingent on a measured `ρ̂`, and the breakeven is only ever computed on a family that survived F-002 — the same conditional |
| Fund it inside step 5's **≤ 5** diagnostics at `iters ≤ 3` | resolution 250 bps/yr | **Rejected.** 2.5%/yr resolution on an 11–14%/yr carry is a number that cannot discriminate |
| Validation rules a **monotone reporting statistic with no selection in it does not deflate DSR** | 0 against `N` | **The right answer if Validation will give it**, and it is not this seat's to assume |

**Put to C2 as C13(j). Filed I-151, MEDIUM** — permissive in the sense that matters (a document
telling a sponsor a mandatory statistic costs 1 when it costs 9 to 42 is a budget that will be blown
by a seat following instructions), conservative in none.

### 12.4 C5 — THE BLOCKING FORM, AND WHOSE RULING IT ACTUALLY NEEDS

**The Principal's ruling, adopted verbatim into §20 and into the seal-readiness block:**

> **The family may not be evaluated at Gate 1, and no PROCEED may be reported, until C5 is ruled.**

**The CIO reads C5 as Validation's. That reading is right about the first of three parts and
incomplete about the other two, and this seat says so rather than accepting the convenient form.**

**Part 1 — the point of application. Validation's, and final short of the Principal.** §4.6 says an
edge derived from published research *"is haircut 50%"* and does not say haircut **what**. The three
natural readings are **not** equivalent, and one of them is a **no-op**:

| Reading | Operation | Effect on Gate 1's `t ≥ 3.0` |
|---|---|---|
| **(i) haircut the return series** | `r → 0.5·r` | **NONE.** Mean and standard deviation both halve; Sharpe, `t`, DSR, PBO, WFE, subperiod positivity and P&L concentration are **all invariant to a positive scalar** [inferred — from the definitions; no measurement involved]. Only capacity and cost-robustness move, because costs do not scale with the multiplier |
| **(ii) haircut the expected return only** | `μ → 0.5·μ`, `σ` as measured | **`t` halves.** Effective hurdle **6.0**. This is §5.4's reading |
| **(iii) haircut the computed Sharpe** | `SR → 0.5·SR` post hoc | Same as (ii) for the Sharpe criterion; **undefined** for `t` and for DSR's benchmark |

> **The finding, and it is stronger than "the haircut is unenforced": under reading (i) the Charter's
> own §4.6 haircut is mathematically inert on every scale-invariant criterion in Gate 1, which is
> nearly all of them.** C5 is therefore not a choice between three shades of the same control. **It
> is a choice between a 2× hurdle and nothing**, and §19.3's entire order-20 composite
> (`3.0 × 2 × 3.3`) rests on the branch being (ii).

**Part 2 — the ratification, and it is the PRINCIPAL's, not Validation's.** Whichever reading
Validation names, the ruling either **doubles the effective Gate 1 `t`-bar to 6.0** or **leaves it at
3.0 and makes §4.6 inert there**. Charter §4 reserves *"any change to the Gate thresholds in Part
IV"* to the Principal, in writing. **`T_STAT_HURDLE = 3.0` never moves in either case — and the bar
a family must clear moves by a factor of two.** A ruling that changes the effective bar by 2× while
leaving the literal constant untouched is a §4 reserved act wearing an interpretation's clothes, and
it is **the Principal's own doctrine of 2026-08-11 applied one clause over**: *a condition precedent
with a date is a kill condition wearing different clothes.* **Escalated under house rule 7, not
resolved here.**

**Part 3 — the executor, without which Part 1 changes nothing.** `published_signal_haircut_applied
= 0.50` has **zero non-`registry.py` consumers** and **no haircut computation exists anywhere in the
harness** [measured — I-134, R21, R28]. **A ruling that names a point of application and no executor
is class (c) and leaves I-143's permissive branch exactly where it is.** C5 discharges only when the
ruling carries **executor, cadence and artifact** — the §4.7.2/class-(b) triple: *Validation, at
every `evaluate_gate1` call on this family, with the haircut's point of application and its applied
value named on the Validation Report's face.*

**C5's blocking form, as written into §20 and the seal-readiness block:**

> **C5 · BLOCKING ON GATE 1 EVALUATION AND ON ANY REPORTED VERDICT — ABSOLUTELY.** The family may be
> sealed, may be run, and may spend Stage 1 with C5 open. **It may not be evaluated at Gate 1, and no
> PROCEED may be reported, until C5 is ruled.** This is a lock, not a footnote, and the Principal's
> reason is recorded with it because it sets the standard for findings of this class: *"a path to
> half the Charter's bar existing quietly is exactly what the relabeling mandate existed to surface,
> and its first substantive yield gets a lock, not a footnote."*

**And this seat finds otherwise on one point of form.** The set **C2, C3, C5, C7, C8, C11** is
correct as *the set that must be cleared before a PROCEED can exist*. **It is not the seal-blocking
set, and R-005's own block already conflated the two** by listing C3 — §20's *"Blocking on Gate 1,
not on sealing"* — among *"the same five open and blocking"* seal conditions. **Merging two kinds of
block into one list is the shape of error that produced I-140.** The honest partition:

| Set | Members | Meaning |
|---|---|---|
| **Seal-blocking** | **C2 · C7 · C8 · C11** | `open_hypothesis` may not be called until all four clear |
| **Verdict-blocking** | **C3 · C5**, and by §20's own column also **C4** (Gate 1 scheduling) and **C10** (Gate 1, met in substance, formal closure outstanding) | the family may be sealed and run; **no Gate 1 verdict and no PROCEED may exist** until these clear |

**The six-item set is the union minus C4 and C10.** R-006 writes the six with the Principal's force
**and names the two the six-item framing drops**, because a blocking set that quietly loses two
members is the defect this dispatch exists to correct. **Filed I-152, MEDIUM.**

### 12.5 THE DATED-CLAUSE SWEEP — 24 CLAUSES, 15 WITH A FALSE PREMISE, AND A SECOND C1

**Doctrine applied, extracted by the Principal from R-005's I-140:** *"a condition precedent with a
date is a kill condition wearing different clothes, and nothing evaluates it."* `STANDING-ORDER-002`
§6 is widened accordingly and the KC-evaluator spec's scope now covers **all dated clauses**. **This
sweep applies it to PREREG-002 before the evaluator exists.**

**Scope:** every clause in the document naming a calendar date on which something is required, fires,
is evaluated, or is asserted true.

| # | Site | Date | What fires on it | What evaluates it | Premise true today? |
|---|---|---|---|---|---|
| **D-1** | §14 condition precedent (prose) | **2026-08-11** | family → ADMITTED-AS-EXPLORATORY | **nothing** | **FALSE** — struck R-005; C1 discharged R-006 |
| **D-2** | §21 `forward_kill_condition`, same clause **inside the hashed field** | **2026-08-11** | same, on the sealed string | **nothing** | **FALSE** — **un-struck until R-006.** S-9 above |
| **D-3** | §14 observation date | **2027-01-31** | the whole of KC-002 | class (b): Principal, weekly ritual | **FALSE** — premise is *"187 days after an intended seal `C` = 2026-07-28"* and `C ≠ 2026-07-28` |
| **D-4** | §21 field opening | **`C + 187 days`** | the whole of KC-002 | class (b) | **TRUE** — a formula, and by R-004's payload rule **it governs** |
| **D-5** | §21 field body, *"over `[C, 2027-01-31]`"* | **2027-01-31** | the computation's window | **nothing** | **FALSE** — contradicts D-4 **in the same field** |
| **D-6** | §21 field body, anti-reinterpretation clause 3 | **2027-01-31** | the successor-family boundary | **nothing** | **FALSE** — same |
| **D-7** | §21 field body, **clause 5, SILENCE IS A KILL** | **2027-01-31** | **AUTOMATIC TERMINATION** | class (b) | **FALSE — AND THIS IS THE SECOND C1. SEE BELOW.** |
| **D-8** | §11.4 R3 table, `forward_window_start` | **2026-07-28** | the forward window's start | `open_hypothesis` computes `C` (class (a)) | **FALSE** — **R23 named §11.4 as a changed clause and did not reach it** |
| **D-9** | §11.4 R3 table, `forward_kill_condition` row | **2027-01-31 "absolute"** | restates D-3 | **nothing** | **FALSE** — same un-reached table |
| **D-10** | §6.3 success criteria, *"KC-002 survival … at 2027-01-31"* | **2027-01-31** | the success criterion's date | **nothing** | **FALSE** |
| **D-11** | §10.5.2 Stage 2, `N_forward` *"through 2027-01-31"* | **2027-01-31** | the forward budget's span | **nothing** | **FALSE** |
| **D-12** | §10.5.3 line item, same | **2027-01-31** | same | **nothing** | **FALSE** |
| **D-13** | §15 step 8, *"through `C + 187 days`"* | formula | forward generation | **nothing** | **TRUE** |
| **D-14** | §20.1, *"Realistic seal date: on or before sprint close, **2026-08-11**"* | **2026-08-11** | nothing mechanical — a dated commitment | **nothing** | **FALSE** — that is **today**, and C2, C7, C8 and C11 are open |
| **D-15** | §11.3 earliest Gate 1, reading 1 | **2027-07-28** | Gate 1 schedule | C4 | **FALSE** — it is `C + 12 months` computed at `C = 2026-07-28` |
| **D-16** | §11.3 reading 2 | **2030-07-28** | same | C4 | **FALSE** — same basis |
| **D-17** | §11.3 reading 3 | **2028-10-05** | same | C4 | **FALSE** — same basis |
| **D-18** | §16, §17 rank 9, §22 row 6 — restatements of D-15…D-17 | same three | same | C4 | **FALSE** — three further copies |
| **D-19** | §11.1 in-sample `[2020-01-01, C]` = **6.571 years** | span | **MinBTL, DSR, the length criterion** | `evaluate_gate1` — **class (a)** | **FALSE, IN THE FAMILY'S FAVOUR** — 6.571 y is measured to 2026-07-28; at any `C` later than that the true span is longer and every margin quoted from it is understated |
| **D-20** | §11.1 ingest ceiling, *"conservative against any `C ≥ 2026-07-28`"* | 2026-07-28 | the ingest bound | `PITStore` ceiling — class (a) | **TRUE** — written formula-safe on purpose |
| **D-21** | §7.1.1, K7's named in-sample trigger | 2025-09-18 | K7's declaration | class (c) | **TRUE** [cited — official] |
| **D-22** | §14.1's quoted C-001 sentence | 2026-11-01 | nothing here | n/a | **n/a** — a quotation about KC-001 |
| **D-23** | §6.1 / §9.1, SOL's structural break | 2022-11-09 | K4 / R3's universe decision | class (c) | **TRUE** [measured, three converging series] |
| **D-24** | §20 C8, *"same session, same UTC day"* | relative | P7 | `evaluate_gate1` P7 — **class (a)** | **TRUE** |

**Two of twenty-four are evaluated by code. Three more are class (b) with a named executor. Nineteen
are evaluated by nothing at all.** And **fifteen carry a premise that is false today** — thirteen of
those because the document was drafted against a same-day seal on 2026-07-28 that §20.1 then
recommended against, and never fully reconciled.

---

#### **D-7 — THE SECOND C1, AND IT IS WORSE THAN THE FIRST**

**`forward_kill_condition`'s opening sentence and its clause 5 are in direct contradiction, inside
one hashed string.**

> **Opening:** *"Observation date = `C + 187 days`… (Drafted against an intended `C` = 2026-07-28,
> giving 2027-01-31; §20.1 recommends NOT sealing that day, so the executed value is whatever
> `C + 187 days` resolves to and **the DRAFTED DATE IS NOT BINDING — the formula is**.)"*
>
> **Clause 5:** *"**SILENCE IS A KILL** — if the computation is not performed **on 2027-01-31** for
> ANY reason … **the family is killed by default.**"*

**Read as sealed, clause 5 terminates this family with certainty.** The observation date the field
itself schedules is `C + 187 days`; at any seal after 2026-07-28 that date is **later than
2027-01-31**. On 2027-01-31 the computation will not have been performed — **it is not due** — and
clause 5 fires. **Registry TERMINATED, no further trials, no Gate 1 submission ever, automatic, not
appealable to the CIO.**

**Why this is strictly worse than I-140's condition precedent.** I-140's clause downgraded the family
to **ADMITTED-AS-EXPLORATORY** — ineligible for Gate 1, still alive — and it fired on a premise that
merely **happened** to be false. **D-7 terminates**, and it fires on a premise that **cannot be
satisfied**: the field's own schedule makes non-performance on 2027-01-31 the guaranteed state of the
world. **A kill condition written to be undefeatable has become one that cannot be survived.** P7
would make it permanent.

**And nothing evaluates it.** I-135 stands: no harness path evaluates a kill condition on any date,
for any family; for a FORWARD classification the field is not even presence-checked. **The clause is
class (b) — executor the Principal, cadence the weekly Friday ritual, artifact the pasted evaluation
— and a Principal executing it correctly, reading the sealed text, finds the family dead.**

**R-006's repair, and the direction it runs is stated first because it is the flattering one.**
The three `2027-01-31` literals in the field body (D-5, D-6, D-7) are conformed to **`C + 187 days`**,
which is what the same field's opening already declares and what §15 step 8 already computes.
**No new rule is introduced.** The contradiction is removed **in the direction the field's own
governing sentence names**, per R-004's payload rule: *"anywhere this document's prose and that
payload could diverge, the payload is what gets passed to `open_hypothesis`."*

**This runs IN THE FAMILY'S FAVOUR — it removes a certain kill — and that is exactly why it is
disclosed at maximum volume and why the ruling is not this seat's.** A sponsor deleting a clause that
terminates its own family is the shape of act this firm exists to distrust. **Put to C2 as C13(k):
Validation may refuse the conformance and require the literal `2027-01-31` sealed as drafted, in
which case the family accepts a shortened window and this seat writes the KILL memo on the day.
Filed I-153, HIGH.**

**§14's prose changes meaning, and this seat will not present that as conformance.** §14 currently
reads *"The date is fixed and does not move… If the seal slips, the window shortens; the date does
not extend."* The field reads *"fixed at sealing and ABSOLUTE thereafter."* **These are two different
rules.** Under §14 the window is `[C, 2027-01-31]` and shrinks with every day of slippage — which
also silently **tightens KC-002 clause (b)**, whose 30-conditioning-day threshold was calibrated
against 187 days and against *"~184 daily bars and ~552 funding prints."* At a seal on 2026-08-12 the
§14 window is **172 days**, 8% shorter, against an unchanged 30-day threshold. **A kill condition
mechanically tightened by scheduling rather than by design.** R-006 conforms **the prose to the
field**, not the field to the prose, because the field is what gets sealed and because the field's
opening is the sentence that already anticipated the slip.

---

#### **D-8 / D-9 — §11.4's R3 TABLE WAS NAMED BY R23 AND NEVER REACHED**

**R-004's R23 row names its changed clauses as *"§11.4; §21 `forward_window_start`."*** §21 was
changed. **§11.4 was not.** Its R3 table still reads, un-struck, today:

> `forward_window_start` | `2026-07-28` (= `C`; **the seal is intended for today**)
> `forward_kill_condition` | KC-002, §14, in full. Observation date **2027-01-31**, **absolute**

**Both premises are false, and the parenthesis *"the seal is intended for today"* has been false
since 2026-08-04** — R23's own stated reason for striking the literal in §21.

**This is the fifth instance of `conforming-pass-did-not-reach-every-instance`** — R8(c), R22, R25,
I-140, and now this — and the first in which a revision row **names the site it failed to reach**,
which is why it is worse than the four before it. A reader auditing R23 against its own clause list
would tick §11.4 as done. **Filed I-154, MEDIUM.**

### 12.6 WHAT R-006 COSTS THIS FAMILY, AND FOR THE THIRD REVISION RUNNING IT MOVES IN BOTH DIRECTIONS

**For the family:** C1 is discharged rather than extended, the condition precedent does not fire, and
the certain termination at D-7 is removed pre-seal. **Three sources of death removed in one
revision, all of them clerical.**

**Against the document, which is the half that matters more:**

- **Fifteen of twenty-four dated clauses carry a premise that is false today**, and **nineteen of
  twenty-four are evaluated by nothing**. The document has been carrying a schedule it never
  reconciled to its own sequencing decision of 2026-08-04.
- **The mandatory house-rule-5 statistic costs between 9 and 42 trials, not one**, and Stage 1 has
  **zero** slack. A seat following this document's own instruction would blow the budget it was
  written to protect.
- **C5 is a choice between a 2× hurdle and a no-op**, and §19.3's most conservative pre-registered
  expectation rests entirely on the branch nobody has ruled.
- **The correction R-005 is credited with was made where readers look and not where the seal
  looks.** S-9 is I-105's lesson inverted, and finding it required reading the payload rather than
  the prose that describes it.

**Payload: UNCHANGED. `trial_budget = 47`, `n_inherited = 7`, all sixteen literals as recorded.**
Three prose-field bodies receive conforming inserts by the R-004 mechanism; the document is unsealed
and a prose-field edit is a draft edit, not an amendment. **No binding field's value moves.**

### 12.7 What §12 did not do

- **No seal, no registration, no registry write, no vault.** `book/registry.db` reads **0/0** and must
  still read 0/0 when this is put down.
- **No trial. No number computed.** Every harness fact is `[measured]` at a named file and line; the
  only arithmetic is `2 + 40 = 42`, `1 + 8 = 9`, `2000 / 2⁸ = 7.8`, `2 + 1 + 2 + 2 + 5 + 25 + 10 = 47`
  and `187 − 172 = 15`, on already-declared integers.
- **No `harness/` file touched, no test run, no suite state reported. `test_h7` / `test_h8` not
  approached.**
- **No `VALIDATION-*` document touched. No `book/` artifact touched. No commit.**
- **No declared menu edited. No selection moved. `N_conditioning` remains 7.**
- **No issue closed by this seat.** I-034's closure is the Principal's act of 2026-08-11 and is
  recorded, not performed, here.

---

*Director of Research · Castellan Capital · **addendum §12 added 2026-08-11 for revision R-006***
*Dispatch S3-D-006. Trial budget ZERO.*

---

# ADDENDUM — REVISION R-007 · 2026-08-12 · PRE-SEAL · CONFORMANCE + REGISTER

*Dispatch **S3-D-014**. Trial budget **ZERO**. `book/registry.db` reads **0 hypotheses / 0 trials**
[measured — read-only `SELECT COUNT(*)`]. No `open_hypothesis`, no registration, no seal, no vault.
No `harness/` file touched, no `VALIDATION-*` document touched, no `book/` artifact **written** — one
read-only `SELECT` over `book/pit.db` for the span the Principal instructed. No test run, no suite
state reported, `test_h7` / `test_h8` not approached. No commit. No issue closed by this seat.*

## 13. THE CONFORMANCE PASS, AND THE REGISTER THE PRINCIPAL ORDERED

### 13.1 The four corrections, in one table

| Item | Disposition |
|---|---|
| **§11.1's span** | **MEASURED, and R34's label struck as unearned.** `[2020-01-01, 2026-07-28]` = **2400 days = 6.5710 years**, measurement date **2026-08-12**. `ingest_ceiling` zero rows; last `knowledge_time` 2026-07-29 on all six primary-universe legs. **The span grows with INGEST, not with `C`** — R34 asserted the opposite without measuring, and the assertion ran in the family's favour. §10.4's 0.43-year margin is **exact, not understated**. `PREREG-002` R37 · **I-176, MEDIUM** |
| **I-153's ratification** | **RECORDED IN-FIELD** at `PREREG-002` §21 `forward_kill_condition`, R38, with the Principal's ruling verbatim. **The insert also states what the ratification does not do**: C13(k)'s instance stays with Validation, the drafted-literal alternative stays live, **the seal does not proceed past it.** This seat's refusal to ratify its own favourable repair is recorded as the third such refusal and as correct routing |
| **Seal-readiness** | **REFRESHED at R40, R-006's separation intact. Seal-blocking C2 · C7 · C8 · C11. Verdict-blocking C3 · C5 · C4 · C10.** R-007 clears none and creates none |
| **§11.4** | **CLOSED BY R-006, at R33.** Both R3 rows are struck-and-replaced in-field — `forward_window_start` → `C`, `forward_kill_condition` → `C + 187 days`, ABSOLUTE — and the I-154 note stands above them naming R23 as the row that listed the site and never reached it. **Verified against the file this session, not inherited from R-006's own claim.** No further action |
| **I-150's cardinal** | **NOT consistent, and the surviving instance was in the sealed string.** `model_prior_provenance` still read *"six sites"*; conformed to **fourteen** at R39. Two further instances named and left: `ISSUE_LOG` I-034's CLOSED entry (**the CRO's**), and R-005's seal-readiness block (**a faithful record of what R-005 said**). **I-177, LOW-MEDIUM** |
| **Payload** | **UNCHANGED. `trial_budget = 47`, `n_inherited = 7`.** No binding field VALUE moved. Nothing interrupts |

### 13.2 The register: **10 of 24**, and the denominator is the finding

`research/REGISTRATION-PAYLOAD-DATED-CLAUSES-PREREG-002.md`. **Fully covered: D-4, D-5, D-6, D-7,
D-10, D-21, D-23. Residue only: D-2. Covered with the mechanism absent: D-19, D-8. Uncoverable:
fourteen**, thirteen of them because the clause lives in prose no registry field carries — E-25(3)'s
named gap, now with a number. **D-24 is the honourable fourteenth: it has no date expression and P7
already evaluates it.**

**The 24 is the wrong denominator.** E-2 extracts by literal form over nine fields and yields **90
sites**, of which **72 are dates that are not clauses**, **75 fire on the first invocation**, and
`kind`'s closed vocabulary describes none of the 72. **`evaluate_gate1` therefore returns
`INSUFFICIENT-DATA` permanently, and the cause is that this seat put its own revision apparatus inside
strings that get hashed.** The remedy is a revision this dispatch did not fund, and it must land before
the seal or P7 freezes it. **I-171 · I-172 · I-173 · I-178 · I-179**, with **I-170** and **I-174** /
**I-175** routed to Validation.

**The unflattering line, stated because it is the whole lesson:** recording the Principal's ratification
in-field — a correct execution of a correct instruction — **added two more sites to the obligation on
the day the register was written.** The register enumerates 90 of 92. **A payload that recedes as you
write it is telling you the container is wrong, not the writing.**

---

*Director of Research · Castellan Capital · **addendum §13 added 2026-08-12 for revision R-007***
*Dispatch S3-D-014. Trial budget ZERO.*

---

# ADDENDUM — REVISION R-008 · 2026-08-25 · PRE-SEAL · **THE THREE LITERALS**

*Dispatch **S4-D-001**. Trial budget **ZERO**. `book/registry.db` read **0 hypotheses / 0 trials /
3 events** at open [measured, read-only `SELECT COUNT(*)`]. No backtest, no `run_backtest`, no grid,
no `open_hypothesis`, no registration, no seal, no commit. No `harness/`, `book/`, `VALIDATION-*` or
`REDTEAM-*` file was opened for writing.*

## 14. `k`, `d` AND `band` — CHOSEN FROM THE MECHANISM, BEFORE ANY OUTPUT EXISTS

### 14.0 What this section is, and the one property that makes it worth anything

**`REDTEAM-002` §2.2 / I-210 is correct and this seat does not contest one word of it.** The sealed
`statement` freezes `w(t) = clip(1.0 − k·max(0, z(t) − d), 0, w_max)` and **no numeric literal is
assigned to `k`, `d` or `band` anywhere in `PREREG-002`, its payload, or its seal block** — in a
document that binds `lookback = 30` and `w_max = 1.0` in the same breath. §6.2's *"made now, before
any measurement"*, §10.5's *"fixed at pre-registration"* and §11.5's *"parameter centres"* each
asserted a fixing that did not exist. **Three sentences claimed a specification the document did not
contain, and it took one grep.**

**The one property that makes choosing them here worth anything is temporal and it expires.** The
registry holds **0 hypotheses and 0 trials**; no backtest has ever run in this firm; **no output of
any kind exists on this family for a parameter to be fitted to.** A choice made now is provably
pre-output in a way no later choice can be. That guarantee is not a claim about this seat's
discipline — it is a claim about the state of `book/registry.db`, and it is verifiable by anyone.

### 14.1 THE TRAP, NAMED BEFORE THE DERIVATION RATHER THAN AFTER

The obvious way to choose `d` is to look at the in-sample distribution of `z(t)` and pick a deadband
that leaves a sensible fraction of days outside it. **That is choosing a parameter from the data it
will be tested on.** It is not a trial by this firm's own rulings — a count over stored funding
prints has twice been ruled not a trial (`DATA-VERIFY-001` §5.2; `REDTEAM-002` §2.1) — **and it is
still exactly the operation pre-registration exists to forbid.** It is I-029(d) performed on a
continuum, where the cardinality of the search is not 73 but uncountable, and no `n_inherited` can
price it.

**The discipline adopted here, stated as a rule and then obeyed:** every one of the three literals is
derived from a quantity **already inside this document or already cited in it**, or from estimator
arithmetic on the declared 30-day lookback. **No query was run against `book/pit.db` this session.
No distribution of `z(t)` was inspected, at any point, in any form.** §14.8 states what was
consulted, in full, including the two figures that are in-sample facts.

**A defensible parameter with a stated mechanism beats a well-fitted one.** Where the arithmetic
brackets a range rather than delivering a point, this section says so and names the judgment.

---

### 14.2 `d` = **1.0** — the deadband

**What `d` means.** `d` is the level of standardized excess funding below which this seat declines to
treat a departure from baseline as information. It is a **noise filter on the crowding signal**, and
the noise it must filter is not the market's — it is **the estimation noise of the rule's own
reference level.**

**The derivation, which uses only the declared lookback.** `z(t)` normalizes against a trailing
**30-day** mean and standard deviation (§6.2, K1). Suppose the funding series sits *exactly* at its
true baseline on day `t`. The 30-day sample mean `μ̂` is still estimated with standard error
`σ/√30 = 0.183σ`, so `z(t) = (μ − μ̂)/σ̂` has dispersion of order **0.18 z-units on a day when
nothing has happened** [inferred — standard estimator arithmetic on n = 30; no market data]. The
trailing `σ̂` carries its own relative error of `1/√(2·29) ≈ 0.13`, which widens this modestly and
in both directions.

**Therefore the deadband is bracketed, not free:**

| Candidate `d` | In units of the baseline's own SE | Verdict |
|---:|---:|---|
| 0.2 | ~1.1 | **Rejected.** The rule fires on the sampling error of its own 30-day mean. A conditioning rule triggered by where the baseline happened to land is not conditioning on crowding |
| **1.0** | **~5.5** | **SELECTED** |
| 3.0 | ~16 | **Rejected.** Restricts the rule to a state that may not occur; that is not a deadband choice, it is a decision to make KC-002 clause (b) fire, taken on the parameter axis where it is invisible |

**The arithmetic delivers an order of magnitude — `d` must be O(1), not O(0.1) and not O(3). The
choice of 1.0 inside that bracket is a judgment and this seat labels it as one**, taken at the round
number that carries an independent reading requiring no reference to this family: **one trailing
standard deviation richer than its own recent baseline** is the ordinary meaning of "elevated" for a
standardized variable.

**What is NOT claimed, and this is the part that matters.** This seat does **not** know what fraction
of in-sample days satisfy `z(t) > 1.0`, has not computed it, and will not. Under a normal reference
distribution it would be ~16%; **the reference distribution is known to be wrong** — §3.4/R2
establishes the series is *censored*, with ~35% of prints at the administered floor [cited —
`DATA-VERIFY-001` §5.2], so it is a mixture with a point mass and its true active fraction is
unknown and plausibly much lower. **That figure is a disclosure of what the choice implies under a
stated and admittedly false reference, not a reason for the choice.** Had the active fraction been
the criterion, this would be the trap at §14.1 with an extra step.

---

### 14.3 `k` = **0.5** — the de-scale slope

**What `k` means, and why the interpretable quantity is `1/k`.** `w = 1 − k·(z − d)` reaches zero at
`z = d + 1/k`. **`1/k` is the width, in z-units above the deadband, over which conviction decays from
full size to flat.** That is the quantity a mechanism can speak to; `k` is its reciprocal and is
chosen only after it.

**Three mechanism constraints, none of them measured:**

1. **The hypothesis is about sizing, not timing.** §4 states the family's claim as *"the crowd is
   wrong about how to **size** it,"* and §19.1 rests on nothing else. A narrow ramp (`1/k` small,
   `k` large) converts a sizing rule into an on/off switch, maximizes turnover per unit of signal,
   and makes the family a timing strategy the document explicitly disclaims.
2. **Zero is a floor the design chose deliberately and it should be reached only in an extreme.**
   K2's declared menu carried *"(2) up-scale at extremes"* and *"(3) sign-flip to long-perp"*, and
   **neither was selected** — `w ∈ [0, 1]` is the whole admissible range. Reaching the bottom of that
   range is the strongest statement the rule can make, and it should correspond to a state the
   trailing baseline itself calls extreme.
3. **A ramp too wide cannot deliver the mechanism's own product.** If `w` never approaches zero
   inside any reachable state, the rule gives up little exposure and can produce no material tail
   reduction — F-002 leg (ii) then measures nothing, and KC-002 clause (b) is near-certain death.

**Selected: `1/k` = 2.0 z-units above the deadband ⇒ `k` = 0.5.** The resulting rule states in one
sentence, which is the test this seat applied to it:

> **Full size at or below one trailing standard deviation of excess funding · half size at two ·
> flat at three.**

**The width of 2.0 is this seat's judgment and is labelled as one** [inferred]. Its content: the
distance the rule takes to travel from full size to flat is **twice** the distance it took to begin
acting at all — a decay that is deliberate rather than abrupt, in a family whose entire claim is
that the *marginal* premium stops paying for the *marginal* tail. A convex tail against a linear
premium argues for a monotone give-up, not a step.

---

### 14.4 `band` = **0.10** — the turnover band

**`REDTEAM-002` §3.1 is the reason this parameter must be derived from something other than either
survival condition.** Widening `band` lowers cost and makes F-002 leg (i) easier while making KC-002
clause (b) harder; narrowing it does the reverse. **A parameter whose two survival tests pull it in
opposite directions cannot honestly be chosen from either.** It is therefore chosen from **cost
arithmetic alone**, which is indifferent to both.

**The principle:** the smallest rebalance the band authorizes must cost less than the daily carry it
is adjusting. A rebalance that costs more than a day of the revenue line is a rebalance the mechanism
cannot pay for, whatever it does to the tail.

| Input | Value | Provenance |
|---|---:|---|
| Round-trip friction, both legs | **~24 bp** | [cited — D-013 §4, carried at `PREREG-002` §5.3] |
| Annualized mean funding, BTC / ETH | **11.86% / 14.07%** | [measured — `DATA-INGEST-002` §4, carried at `PREREG-002` §5.3 and already inside the sealed text] |
| ⇒ daily carry on perp notional | **~3.25 / ~3.86 bp** | [inferred — division by 365, the declared `periods_per_year`] |

Only the perp leg moves (spot notional is fixed at 1.0), so a rebalance of size `Δw` costs roughly
`Δw × 24` bp round-trip. Requiring that to sit inside one day of the thinner asset's carry:
`Δw × 24 ≤ 3.25` ⇒ **`Δw ≤ 0.135`**. **Rounded down to `band` = 0.10**, at which the smallest
authorized trade costs `0.10 × 24 = 2.4` bp — **about three-quarters of one day of BTC carry.**

**Two checks run AFTER the choice, disclosed as post-hoc and one of them favourable:**

- **`band` = 0.10 < 0.25, so the turnover band cannot suppress a KC-002 clause-(b) day.** Clause (b)
  counts days on which notional moved by more than ±25%; any such target move is more than twice the
  band and is therefore always executed. **This runs in the family's favour and this seat states it
  ran the check second, not first.**
- **Had the cost arithmetic delivered `band` > 0.25**, the two survival conditions would have been in
  direct conflict and this seat would have escalated the conflict rather than picked a side. **It did
  not, and the absence of the conflict is luck rather than design.**

---

### 14.5 WHAT THE THREE LITERALS NOW FIX DOWNSTREAM

**(1) The ±50% grid has a centre, chosen before any output exists — I-212's substance discharged.**
`run_parameter_grid` / `grid_from_center(fraction=0.5, steps=5)` on §10.5's two gridded parameters
now evaluates:

| Parameter | Centre | The five points |
|---|---:|---|
| `lookback` | 30 | 15 · 22.5 · **30** · 37.5 · 45 |
| `k` | 0.5 | 0.25 · 0.375 · **0.5** · 0.625 · 0.75 |

**§15 still runs the grid at step 6, after F-002 at steps 2–3 — and that no longer matters**, because
the centre is a sealed literal rather than a value chosen when step 6 arrives. The I-029(d) operation
relocated to the parameter axis is closed by fixing the centre, not by reordering the steps.
**`lookback`'s grid produces non-integer day counts (22.5, 37.5), which is a live specification
question this revision does not resolve** — filed **I-222**.

**(2) KC-002 clause (b) is now a computable rule — I-211's computability discharged, its sensitivity
made visible.** `|Δw| > 0.25` ⟺ `k·(z − d) > 0.25` ⟺ `z > d + 0.25/k`. At the sealed literals:

> ### **Clause (b) evaluates to: fewer than 30 days in the 187-day forward window on which `z(t) > 1.5`.**

**The direction the Devil's Advocate named is real and is now visible instead of invisible.** Larger
`k` and smaller `d` lower that threshold and make the sponsor's own pre-registered expected cause of
death easier to survive: `(k = 1.0, d = 0.5)` would give `z > 0.75`; `(k = 0.25, d = 2.0)` would give
`z > 3.0` and near-certain death. **The selected pair sits between them, and this seat states plainly
that it does not know whether `z > 1.5` occurs thirty times in a hundred and eighty-seven days.**
That is what a pre-registration is for. §14.2's expectation at R7 — that clause (b) is not merely the
most likely killer but the expected outcome — **is unchanged and is not softened by having numbers.**

**(3) The Devil's Advocate's cheapest kill is now executable and this seat endorses it in the DA's
own ordering.** DA(2) — count the in-sample days with `|w(t) − 1| > 0.25`, i.e. `z(t) > 1.5`, and
take the maximum over any rolling 187-day in-sample window; kill below 30 — **can be run the moment
the literals are sealed. It has NOT been run and must not be, until they are.** Reversed, it is the
§14.1 trap.

---

### 14.6 THE INERTNESS FINDING — DISCLOSED IN THREE REGISTERS, NOT REDESIGNED

**`REDTEAM-002` §2.1 is this seat's strongest objection received and it is correct.** `max(0, z − d)`
is zero whenever `z ≤ d`, so **the rule can act only when funding is rich relative to its own trailing
baseline, and does nothing at all when funding is cheap or negative** — while §3.2 population 3,
§3.3 risk 3 and §7.4 all place this family's left tail in funding **inversion**. The DA measured
**619 of 2,415 BTC days (25.63%)** and **609 of 2,415 ETH days (25.22%)** carrying at least one
negative funding print [cited — `REDTEAM-002` §2.1, measured by that seat, read-only count over
stored prints; **not re-measured here and not this seat's number**].

**The Principal has ruled that this is disclosed and not repaired, and this seat does not seek to
reopen it.** K2 remains option (1); option (3) — sign-flip on inversion — remains declared,
considered and not selected; **the rule is unchanged.** Changing K2 now would be a post-hoc
conditioning move made in response to an argument, which is the operation §7.2's escalation rule
exists to price, and it would cost the line.

**Why three registers and not one.** R29(b) is this document's own hardest-won lesson: *a correction
exists where the seal reads it, and nowhere else* — R-005 struck a condition where readers meet it
and left it standing where the seal meets it. **The disclosure is therefore placed in three binding
fields, so that no reader of any frozen string meets the rule without meeting the regime it cannot
act in:**

| Register | Field | What it says there |
|---|---|---|
| **Economic** | `mechanism` | The field that names hedgers as the mechanism of inversion now says, in the same field, that the sizing rule holds **benchmark weight** through inversion — a deliberate risk posture, **not** tail reduction |
| **Mechanical** | `statement` | On the face of the frozen rule: `max(0, z − d) = 0` for `z ≤ d`, so `w = 1.0` whenever funding is at or below baseline, including throughout a negative-funding regime, and the 30-day trailing baseline holds `w` at benchmark for up to thirty days after a cascade has collapsed `z` |
| **Evidential** | `falsifier` | On leg (ii): whatever tail improvement leg (ii) measures **cannot originate in the inversion regime**, and a leg (ii) pass must not be read as tail protection in the regime where the mechanism places the tail |

**What the disclosure costs the family, stated plainly:** it removes the reading under which F-002
leg (ii) certifies tail protection generally. **The claim under test narrows to tail reduction on the
approach to crowding, and the document now says so in the three places that get hashed.**

---

### 14.7 THE TWO `[2020-01-01, C]` SITES — CONFORMED TO THE DA's REMEDY

**`REDTEAM-002` §8 / I-213 is adopted in full and it needs no Principal act.** `C` has been doing two
jobs — the freeze instant and the in-sample right edge — and R23, R33, R34, R37 and I-097 are five
repairs of the instances and none of the cause. **There is no seal date at which `[2020-01-01, C]` is
true**, because the window is bounded by the last *ingested settled* bar and `C` is bounded by the
calendar.

**Both binding sites are conformed to "the last settled common bar of the primary universe at the
first run"** — which is exactly what `oos_index` already carries, exactly what Validation §7.3 has
already ruled governs, and **not a change to `C`**, which keeps its meaning as the freeze instant and
keeps defining `forward_window_start`, the holdout and KC-002's window.

| Field | Was | Now |
|---|---|---|
| `statement` | *"over 2020-01-01 to C"* | *"over 2020-01-01 to the last settled common bar of the primary universe at the first run"* |
| `falsifier` | *"over the full in-sample [2020-01-01, C]"* | *"over the full in-sample [2020-01-01, the last settled common bar of the primary universe at the first run]"* |

**The `universe` field carries a third instance** — *"common span 2020-01-01 to C = 6.571 years
[SUPERSEDED …]"* — which the DA's remedy did not name and which this revision does **not** touch.
It is a span *measurement* with its own superseding note, not a computation window any seat runs.
**Named rather than repaired**, per this dispatch's scope rule. Filed **I-221**.

**R-008 introduces ZERO new dated sites.** The replacement text contains no ISO date and no `C`-form
expression, and none of the three literals is a date. **This is the first revision of this document
of which that is true**, and it is stated because R-007's own lesson was that recording a correct
ruling in-field added two sites to an obligation that was already unfinishable.

---

### 14.8 DID THIS SEAT CONSULT THE DATA? — THE FULL ANSWER

**No query was run against `book/pit.db` this session, and no distribution, moment, quantile or count
of `z(t)` was inspected in any form.** The only database read was `book/registry.db`, read-only,
`SELECT COUNT(*)` on three tables, at open and at close.

**Two in-sample facts were used, both already inside the sealed text before this revision, and this
seat names them rather than leaving them to be discovered:**

1. **Annualized mean funding, BTC 11.86% / ETH 14.07%** [measured — `DATA-INGEST-002` §4], used only
   to price a *cost* against the *level* of the revenue line in §14.4. It is a first moment of the
   funding series, not a property of `z(t)`'s dispersion, and no threshold on the signal is set from
   it.
2. **The ~35% floor share** [cited — `DATA-VERIFY-001` §5.2], used only in §14.2 to say why the
   normal-reference active fraction is *not* a valid basis for choosing `d`. **It is used to reject
   an argument, not to build one.**

**An honest "I looked" beats a concealed one, and this is the honest version: the two figures above
are in-sample, they were already sealed, and they were used for a cost and for a refusal.** If
Validation regards either as contaminating, the remedy is available and cheap — re-derive `band` from
the 24 bp friction and a stated assumed carry floor, which moves the answer by less than the rounding
already applied. **This seat does not think that is necessary and states the exposure rather than
arguing it away.**

### 14.9 WHAT §14 DID NOT DO

- **No trial, no backtest, no `run_backtest`, no grid, no `open_hypothesis`, no registration, no
  seal, no vault, no registry write, no commit.** Registry read 0/0/3 at open and 0/0/3 at close.
- **No change to the sizing rule, to K2, or to any declared menu or selection.** `N_conditioning`
  remains 7; `trial_budget` remains 47; `n_inherited` remains 7.
- **No repair of I-214, I-215, I-216, I-218, or of the `universe` third instance at §14.7.** All
  named, none touched.
- **No removal of the struck `2027-01-31` literals** — I-204's standing prohibition holds; they are
  load-bearing and E-14's `DIVERGENT` fires only because they are there.
- **No re-measurement of the DA's 25.6% / 25.2%.** Carried with that seat's provenance.

### 14.10 Issues filed by §14

**I-220** (the three literals, and what a specification that does not specify cost seven revisions to
notice) · **I-221** (`universe`'s third `2020-01-01 to C` instance, unrepaired by design) ·
**I-222** (`lookback`'s ±50% grid produces non-integer day counts) · **I-223** (`band`'s derivation
uses two already-sealed in-sample figures — disclosed exposure) · **I-224** (the first trial is not
blocked; the first *verdict* is, and the firm should choose knowingly) · **I-225** (the payload's
delta record skipped R-006 and R-007).

---

*Director of Research · Castellan Capital · **addendum §14 added 2026-08-25 for revision R-008***
*Dispatch S4-D-001. Trial budget ZERO. Registry 0 / 0 / 3 at open and at close.*

---

# ADDENDUM — REVISION R-009 · 2026-08-25 · PRE-SEAL · **THE LEG COUNT**

*Dispatch **S4-D-007**. Trial budget **ZERO**. `book/registry.db` read **0 hypotheses / 0 trials /
3 events** at open [measured, read-only `SELECT COUNT(*)`]. No query against `book/pit.db`. No
backtest, no grid, no `open_hypothesis`, no registration, no seal, no commit. `harness/` not opened.*

## 15. `band` RE-DERIVED — THE LEG COUNT WAS WRONG, THE METHOD WAS NOT

### 15.1 The error, conceded without qualification

**`REDTEAM-002A` §3.1 / I-240 is correct and this seat does not contest one word of it.** §14.4 wrote
*"Only the perp leg moves … so a rebalance of size `Δw` costs roughly `Δw × 24` bp round-trip"* — and
**24 bp is `PREREG-002` §12.4's TWO-leg round trip: 4 sides × 6.0 bp per side** [measured — §12.4,
line 1636, in this document since 2026-08-04]. The sentence names the one-leg construction and then
charges the two-leg constant. **A cited number carried across a change in its unit of account** —
I-141 / I-150 / I-096's family, committed in the derivation of a literal rather than in a summary.

### 15.2 The corrected charge — **12 bp**, and why not 6

`w(t)` scales **perp** notional; spot is fixed at 1.0 unit [measured — the sealed `statement`]. A band
rebalance is therefore one trade on one leg. The DA offers two corrected charges and the choice
between them is not free of consequence, so it is made explicitly:

| Charge | Composition | `Δw ≤ 3.25 / charge` |
|---|---|---:|
| 24 bp — **as sealed, wrong** | 2 legs × 2 sides × 6.0 bp | 0.135 |
| **12 bp — SELECTED** | **1 leg × 2 sides × 6.0 bp** | **0.2708** |
| 6 bp — declined | 1 leg × 1 side × 6.0 bp | 0.542 |

**12 bp is the leg-count correction and nothing else.** It divides the sealed constant by the factor
that was wrong — the leg count, 2 → 1 — and leaves the round-trip framing, the carry input, the
inequality and the rounding step exactly where §14.4 put them. **Moving to 6 bp would additionally
change the *method*** from a round trip to a single side, which this dispatch did not authorize and
which §14.4's own principle argues against: the inequality prices the increment against **one day**
of carry, and an increment adjusted daily is put on and taken off inside that horizon, so a round
trip of the increment is the term that matches the day it is compared to.

> **This seat states the direction of the choice it made, because the choice is on the axis
> `REDTEAM-002` §3.1 ruled unchooseable from either survival condition. 12 bp yields the SMALLER
> corrected band (0.27 against 0.54), and the smaller band is the one that is EASIER on this family's
> own expected cause of death.** The reason for 12 is the leg count and the matching horizon, stated
> above and independent of that. **It remains a survival-relevant convention chosen by the sponsor,
> and this seat does not think it should stand on the sponsor's say-so. Filed I-252 to Validation.**

### 15.3 The arithmetic, in full

```
per-side cost, CRYPTO_PERP_TAKER      = 5.0 commission + 1.0 half-spread = 6.0 bp   [measured, §12.4]
perp-leg round trip                   = 2 x 6.0                          = 12.0 bp  [inferred]
BTC annualized mean funding           = 11.86%                                      [measured, DATA-INGEST-002 §4]
=> daily carry on perp notional       = 1186 / 365                        = 3.249 bp/day [inferred]
constraint: smallest authorized trade costs less than one day of the carry it adjusts
=> band x 12.0 <= 3.249               =>  band <= 0.27083                            [inferred]
SELECTED band = 0.27  (truncation at the precision of the inputs, downward; NO round-number snap)
smallest authorized trade at 0.27     = 3.240 bp against 3.249 bp/day of carry  -> margin 0.3%
```

**ETH is not used**: at 14.07% the bound is 0.321, and §14.4's original choice of the thinner asset's
carry is the tighter of the two and is retained unchanged.

### 15.4 THE ROUNDING RULE IS NOW DECISION-RELEVANT, AND TWO ROUTES TO 0.25 WERE FOUND AND DECLINED

**§14.4 said "rounded down" and stated no rule.** 0.135 → 0.10 is a snap to the nearest 0.05 below,
a 26% reduction, and nothing in the document says so. At R-008 that discretion cost nothing. **At
R-009 it decides whether this seat's own escalation trigger fires**, and this seat found **two**
independently-arguable routes that land the answer at exactly 0.25 — where the trigger reads
`band > 0.25` and therefore does **not** fire, and where the favourable post-hoc check is restored:

1. **Apply §14.4's own unstated snap.** The nearest 0.05 below 0.2708 is **0.25**.
2. **Substitute the administered carry baseline for the measured mean** — the remedy §14.8 itself
   offered against I-223. Charter Seat 7's 0.01%/8h baseline is 10.95%/yr [cited], `1095 / 365` =
   **3.000 bp/day exactly**, and `3.000 / 12` = **0.2500 exactly.**

> **Both are declined and both are disclosed, which is the whole of this subsection.** Route 2 is
> the more dangerous because it is *independently justifiable* — it removes an in-sample figure from
> a binding literal, which is a real improvement — and it silences the trigger as a side effect. **A
> rounding rule or an input substitution selected after the threshold is known, whose effect is to
> land on the threshold, is the operation this dispatch forbids by name, and the fact that route 2
> has a good argument attached is what would have made it survive review.**

**The rule adopted, whose justification makes no reference to 0.25:** take the derived bound at the
precision its inputs support and truncate downward. That is the least-discretion option available —
the null rounding — and it is stated here so that the next revision inherits a rule rather than a
habit. **Filed I-250.** The 0.3% margin this leaves is thin and is itself a finding: **filed I-254.**

### 15.5 THE ESCALATION TRIGGER FIRES. THIS SECTION IS THE ESCALATION.

§14.4 committed this seat, in writing, before the correction existed:

> *"Had the cost arithmetic delivered `band` > 0.25, the two survival conditions would have been in
> direct conflict and **this seat would have escalated the conflict rather than picked a side.**"*

**`band` = 0.27 > 0.25. The trigger fires as written, and this seat escalates rather than picking a
side.** The Principal has ruled the handling in advance — *"a pre-registered trigger that fires
during drafting is the system working at the cheapest possible moment"* — so what follows is the
conflict stated at its exact size, not an argument for relief from it.

**The conflict, quantified.** KC-002 clause (b) counts days on which the conditioning moved notional
by more than **±25% from the benchmark's constant notional** — `|w − 1| > 0.25`, i.e. `z > 1.5` at
the sealed `(k, d)` [measured — §21 `forward_kill_condition`, line 1743]. The turnover band gates
whether `w_held` tracks `w_target` at all. **From the benchmark state `w_held` = 1.0, a target
deviation of `x` executes only if `x > band`. So target deviations in `(0.25, band]` qualify for
clause (b) and never execute, and the day is not counted.**

| `band` | Suppression window, target deviation | In `z` | Width |
|---:|---|---|---:|
| 0.10 (sealed, wrong) | — none, `band < 0.25` | — | 0 |
| **0.27 (corrected, 12 bp)** | **(0.25, 0.27]** | **1.50 < z ≤ 1.54** | **0.02** |
| 0.54 (corrected, 6 bp) | (0.25, 0.54] | 1.50 < z ≤ 2.08 | 0.29 |

**Three honest qualifications, none of which this seat treats as grounds to decline the escalation:**

- **The window at 12 bp is narrow** — 0.02 of deviation, 0.04 of `z`. The conflict is real and small.
- **It is a delay, not a permanent loss, for a persistently-elevated `z`:** if the target deviation
  keeps growing past `band` the trade executes and the day counts thereafter.
- **It bites hardest where the family actually lives.** The inertness finding puts `w_held` at 1.0
  through the ~25% of days in inversion and for up to thirty days after a cascade [cited —
  `REDTEAM-002` §2.1], and the suppression is exactly a property of the benchmark state. **A defect
  that only bites from `w = 1.0` is not thereby rare in this family.**

**At 6 bp the conflict is not narrow: 0.29 of deviation, and clause (b) would be materially
suppressed.** That is the second reason I-252 is Validation's and not this seat's.

**What this seat asks, and it asks for a ruling rather than proposing the answer:** whether the
cost-accounting convention is 12 bp or 6 bp (I-252), and — consequentially, and **not** this seat's
to touch — whether KC-002 clause (b) should count *target* deviations rather than *executed* ones,
which would decouple a kill condition from a cost parameter entirely (**I-253, named and not
repaired**; a clause-(b) restatement is a hard interrupt and is not in this dispatch's scope).

### 15.6 `d` = 1.0 — DISCLOSURE, NOT RE-DERIVATION

**`d` seals as chosen at 1.0 and this seat does not re-derive it**, per the Principal's ruling:
*"pre-registration does not require the parameter to be right; it requires the choice to be visible
— and now it is doubly so."*

**The correction against this seat's own argument, published in the binding field:** §14.2 measured
`d` against `σ/√30 = 0.183`, **the estimation noise of the reference level.** The quantity a deadband
on `z` must clear is `z`'s **own null dispersion**, and day `t` is itself a draw with the trailing
window ending strictly before it, so under an iid null `Var(x_t − μ̂) = σ²(1 + 1/30)` and
**`sd(z | null) = √(1 + 1/30) ≈ 1.017`** [cited — `REDTEAM-002A` §2.1; estimator arithmetic, no
market data]. **`d` = 1.0 is therefore ~1.0 null SD, not the ~5.5 §14.2 claims — the same position on
the scale at which §14.2 rejects `d` = 0.2**, and the DA's characterization travels with it verbatim:
*"a rounder number in the same class as 3.0."*

**§14.2's table is superseded on its safety-margin column by this paragraph and is not rewritten** —
the derivation as delivered is part of the record. What changes is that the document now carries the
argument against its own parameter **in the string that gets hashed**, which is R29(b) applied: a
correction exists where the seal reads it, and nowhere else.

### 15.7 WHAT §15 DID NOT DO

- **No trial, no backtest, no grid, no `open_hypothesis`, no seal, no vault, no registry write, no
  commit, no `book/pit.db` query.** Registry 0 / 0 / 3 at open and 0 / 0 / 3 at close.
- **No change to `k`, `d`, `lookback`, `w_max`, K1–K7, `trial_budget` (47) or `n_inherited` (7).**
- **No repair of I-242 (`σ̂` degeneracy) or I-243 (leg-(ii) directional unfairness).** Both are the
  DA's, both are real, **neither blocks the seal in this seat's judgment**, and SO-003 §3.1 forbids
  absorbing them here. Named and untouched.
- **No removal of the struck `2027-01-31` literals** — I-204's prohibition holds.
- **No re-derivation of `d`**, and no change to KC-002 in any clause, threshold or date.

### 15.8 Issues filed by §15

**I-250** (the rounding rule was never stated, and became decision-relevant) · **I-251** (the
escalation trigger fired; the conflict is live and unresolved at the seal — **HIGH**) · **I-252**
(the 6-vs-12 bp convention is survival-relevant and was chosen by the sponsor — **HIGH**) ·
**I-253** (clause (b) counts executed moves, so any `band` > 0.25 couples a kill condition to a cost
parameter; named, not repaired) · **I-254** (the corrected literal sits 0.3% inside its constraint,
so an in-sample measured mean now sets it almost exactly — I-223 escalated) · **I-255** (the whole
derivation is contingent on the one-leg rebalance; a future two-leg construction reverts the charge
to 24 bp and the band to ~0.135, and nothing in the document flags the coupling).

---

*Director of Research · Castellan Capital · **addendum §15 added 2026-08-25 for revision R-009***
*Dispatch S4-D-007. Trial budget ZERO. Registry 0 / 0 / 3 at open and at close.*

---

*Dispatch **S4-D-011**. Trial budget **ZERO**. `book/registry.db` read **0 hypotheses / 0 trials /
3 events** at open [measured, read-only `SELECT COUNT(*)`]. No query against `book/pit.db`. No
backtest, no grid, no `open_hypothesis`, no registration, no seal, no commit. `harness/` opened
**read-only** (Seat 9 holds the write tree).*

## 16. `band` DERIVED FROM WHAT THE REBALANCE DOES — THE CHARGE IS ONE SIDE, AND THE FREE CHOICE DOES NOT SURVIVE

### 16.1 What was ruled, and what was not

The Principal ruled the **decision rule**, not the number. §15.2 selected 12 bp on a *convention*
("the round-trip framing matches the one-day horizon") and disclosed that the convention yielded
*"the smaller and family-friendlier of the two corrected bands"* — then asked for a ruling (I-252).
The ruling received: **derive the charge from the mechanism's own sentence — the perp leg's actual
friction for what the rebalance actually does, priced term by term from the sealed preset** — and, if
a genuinely free convention choice survives that derivation, **the asymmetry doctrine resolves it
against the family: 6 bp → `band` 0.54.**

**The derivation below eliminates the choice.** It is settled by the harness, not by a convention,
and it lands on the same number the tie-break would have produced. Both facts are stated because
either alone would be a weaker record.

### 16.2 The per-side price, term by term from the sealed preset

`CRYPTO_PERP_TAKER` — the preset the perp leg trades on, Principal-authorized, not this seat's to
adjust [measured — `harness/castellan/costs.py:120–129`]:

| Charter §4.6 stack term | Preset field | Value | Enters the band charge? |
|---|---|---:|---|
| commission, per side | `commission_bps` | **5.0 bp** | **Yes** |
| `0.5 × spread × capture` | `half_spread_bps` | **1.0 bp** | **Yes** |
| `Y · σ_daily · √(Q/ADV)` | `impact_y = 1.0`, `impact_exponent = 0.5` | not a constant | **No — omitted; direction disclosed at §16.7** |
| borrow / funding carry | `borrow_bps_annual` | **0.0** | Zero by value |
| realized funding | *no such field, by construction* | — | **RHS of the inequality, never the LHS** [cited — Ruling 003 / I-034] |

```
per-side price = (commission_bps + half_spread_bps) x 1e-4 = (5.0 + 1.0) bp = 6.0 bp
                                        [measured - costs.py:46, the `base` expression]
```

**6.0 bp per side is determinate.** The preset determines a **price per side** and says nothing about
how many sides a rebalance incurs — the method is named `per_side_cost`, and the side count is a
property of the trade sequence, not of the cost model. That is where §15.2's convention lived.

### 16.3 The side count is determinate too, and the harness is what determines it

**What the rebalance does.** `w(t)` scales **perp** notional; spot is fixed at 1.0 unit [measured —
the sealed `statement`]. One leg moves. A band rebalance is one execution, `w_held → w_target`, at
one bar. **One side.**

**What the engine charges** [measured — `harness/castellan/engine.py:141–143`, `:197–198`]:

```
trades     = positions.diff().abs()          # comment in source: "per side traded"
turnover   = trades.sum(axis=1)
trade_cost = turnover * per_side_cost        # ONE per-side price per unit of |dw|, once, at the bar
```

**The engine charges exactly one side per unit of `|Δw|`, at the bar the weight changes, and never a
second time.** A `band` derived against a 12 bp round-trip charge is derived against a cost
`run_backtest` will never apply — and under A2 `run_backtest` is the only admissible producer of a
number in this firm. **§4.7.2's test, applied to a cost convention: name the field the harness reads
to enforce it. The field is `per_side_cost`, read once per side. There is no round-trip field.**

**And the round-trip charge is not conservative-but-defensible; as a per-rebalance charge it is
arithmetically wrong, because it counts every side twice.** The return leg of any increment **is
itself a band rebalance**, which the same inequality charges again in its own right:

| `w` path | Sides actually traded | Engine cost at 6.0 bp | One-side charge, summed | Round-trip charge, summed |
|---|---:|---:|---:|---:|
| 1.0 → 0.7 → 1.0 | 2 (sell 0.3, buy 0.3) | **3.6 bp** | **3.6 bp** ✓ | 7.2 bp ✗ (2×) |
| 1.0 → 0.7 → 0.4 | 2 (sell 0.3, sell 0.3) | **3.6 bp** | **3.6 bp** ✓ | 7.2 bp ✗ (2×), and **no reversal ever occurs** |

The second row is the one that kills the convention outright: a monotone sequence of same-direction
rebalances contains **no round trip at all**, so the premise §15.2 imported — that the increment is
put on and taken off — is not merely a horizon choice, it is **false on a realizable path.** The
terminal unwind of the whole position is a property the benchmark shares and is not turnover the
band authorizes.

**§15.2's stated reason is therefore withdrawn, not overruled.** Its sentence — *"the inequality
prices the increment against one day of carry, so a round trip of the increment is the term that
matches the day"* — conflates the **increment's life-cycle** with **the rebalance**, and the subject
of the inequality is the rebalance: *"the smallest rebalance the band authorizes must cost less than
the daily carry it adjusts."* The sentence was always one-sided. R-009 read it two-sided.

### 16.4 The arithmetic, in full

```
per-side price, CRYPTO_PERP_TAKER     = 5.0 commission + 1.0 half-spread = 6.0 bp  [measured, costs.py:120-129]
sides per band rebalance              = 1 leg x 1 side                   = 1       [measured, engine.py:141-143, :197-198]
=> charge on the smallest rebalance   = 1 x 6.0                          = 6.0 bp  [derived]
BTC annualized mean funding           = 11.86%                                     [measured, DATA-INGEST-002 section 4]
=> daily carry on perp notional       = 1186 / 365                       = 3.249 bp/day [derived]
constraint (unchanged): the smallest authorized rebalance costs less than one day of the carry it adjusts
=> band x 6.0 <= 3.249                =>  band <= 0.54150                          [derived]
SELECTED band = 0.54   (truncation downward at the precision of the inputs, section 15.4's rule; NO snap)
smallest authorized trade at 0.54     = 3.240 bp against 3.249 bp/day of carry -> margin 0.28%
```

**Three inputs are held byte-identical to R-009 and none is re-chosen here.** The carry input
(11.86% BTC, the thinner of the two — ETH at 14.07% gives 1.157 and is the looser bound); the
one-day budget on the right-hand side; and §15.4's truncation rule. **The only term that moves is
the side count**, which is the term the ruling scoped.

**`k` = 0.5, `d` = 1.0, `lookback` = 30, `w_max` = 1.0 are UNCHANGED and are not re-derived.**

**Two cross-checks, both recorded because both were live hazards at 12 bp and neither recurs at 6:**

1. **§15.4's route (ii)** — substituting the Charter's administered 10.95%/yr baseline — gives
   `3.000 / 6.0` = **0.5000 exactly**, not 0.25. **The trigger-silencing coincidence that made route
   (ii) dangerous at 12 bp is structurally absent at 6 bp.** The measured baseline is retained
   regardless (no change of method authorized), and it yields the **larger** band, 0.54 against 0.50,
   which is the direction against the family. I-223 / I-254's substance is unchanged.
2. **The margin is identical.** 0.28% at 0.54/6.0 as at 0.27/12.0 — the truncation step is the same,
   so **I-254 neither worsens nor improves.** It is not re-filed.

### 16.5 The tie-break never engaged, and would have produced the same number

Recorded explicitly so that no future reader has to reconstruct which of the two routes carried the
number: **the free choice did not survive §16.3, so the asymmetry doctrine was not needed.** Had
§16.3 failed to settle it, the pre-committed tie-break resolves to 6 bp → 0.54 — **the same value.**
A derivation and a doctrine converging on one number is the strongest form this record can take, and
it is the reason this seat reports the derivation as decisive rather than as the friendlier of two
readings.

### 16.6 WHAT R-010 COSTS THIS FAMILY — AND R-009's FIRST QUALIFICATION IS WITHDRAWN

**R-009 offered three qualifications on the escalation and the first of them dies here.** It read:
*"the window at 12 bp is narrow — 0.02 of deviation, 0.04 of `z`. The conflict is real and small."*

At 0.54 the suppression window is **(0.25, 0.54]** of target deviation, i.e. **1.50 < z ≤ 2.08** —
already computed and published in §15.5's own table as its 6 bp row, so **no new number is produced
here.** The width goes from 0.02 to 0.29 of deviation: **14.5× wider** [arithmetic on two published
figures]. **"Narrow" is no longer available as a qualification and this seat withdraws it rather than
restating it in softer form.** The second and third qualifications stand unchanged: it remains a
*delay* for a persistently-elevated `z`, and it still bites hardest from `w_held` = 1.0, where the
inertness disclosure places this family for ~25% of days and for up to thirty days after a cascade.

**The cost, stated as a cost.** KC-002 clause (b) is this family's own pre-registered expected cause
of death. At `band` = 0.54 there is a materially wide band of `z` in which a day **target-qualifies
for clause (b) while the strategy never trades at all** — the family can be killed by a clause in a
state where it was inert. **That is the whole point of the repair and it is not softened.**

**For the family: nothing.** No source of death is removed; no threshold moves in its favour.

**I-251 is not re-escalated.** The trigger fired at R-009, the escalation is on the record, and
re-firing it would be ceremony. What R-010 adds is the conflict's **size**, which is now §15.5's 6 bp
row rather than its 12 bp row. **I-252 is answered on its merits and this seat records that the
answer runs against the convention it itself selected one revision earlier.**

### 16.7 THE ONE CONVENTION THAT SURVIVES, AND IT IS ON THE OTHER SIDE OF THE INEQUALITY

Two terms in §16.4 are not derived, and this seat names them rather than presenting the inequality as
fully determinate:

**(a) The one-day budget on the right-hand side.** *Why* one day of carry is the right allowance for
the smallest authorized rebalance is a declared conservatism, not a derivation. **Its direction runs
in the family's favour and this seat says so:** a two-day budget gives `band ≤ 1.083`, a wider band
and therefore a wider suppression window. **The one-day horizon is retained byte-identical** — the
ruling scoped the charge, the horizon is a different axis, and moving a binding literal's derivation
on an unruled axis inside a dispatch scoped elsewhere is the SO-003 §3.1 violation. **Named, not
repaired: filed I-290.**

**(b) The omitted impact term.** `Y · σ · √(Q/ADV)` is in the preset and is **not** in the 6.0 bp
figure, because it is not a constant and pricing it requires a measured `σ` and a measured ADV —
i.e. an in-sample figure inside a binding literal, which is exactly what I-223 objects to. **Its
direction also runs in the family's favour:** including it raises the charge, lowers the bound and
narrows the suppression window. **Omitting it is therefore the against-family choice and needs no
relief; including it would need a measurement this dispatch forbids.** Filed **I-291**.

**Both are disclosed as conventions running in the family's direction. Neither is used, and a future
ruling on either moves `band` again — pre-seal, per the payload's own standing instruction.**

### 16.8 WHAT §16 DID NOT DO

- **No trial, no backtest, no grid, no `open_hypothesis`, no seal, no vault, no registry write, no
  commit, no `book/pit.db` query.** Registry **0 / 0 / 3** at open and **0 / 0 / 3** at close.
- **`harness/` read-only**, two files, no write. Seat 9 holds that tree for the `write_grants`
  migration.
- **No change to `k`, `d`, `lookback`, `w_max`, K1–K7, KC-002 in any clause or threshold,
  `trial_budget` (47) or `n_inherited` (7).** No re-derivation of `d`.
- **No removal of the struck `2027-01-31` literals** — I-204's prohibition holds.
- **No repair of I-242, I-243, I-253, I-255**, and no retroactive conformance beyond §20.
- **No new measurement.** Every figure is a prior `[measured]` carried with its source, a
  `[measured]` read of harness source this session, or arithmetic on two published figures.

### 16.9 Issues filed by §16

**I-290** (the one-day budget on the RHS is an undeclared convention running in the family's
direction — MEDIUM) · **I-291** (the impact term is in the preset and out of the band derivation;
disclosed, against-family, unpriceable pre-seal — LOW) · **I-292** (**R-009 selected a
survival-relevant cost convention that the sanctioned engine contradicts in source — the seat's own
check reached for the *economic* reading of "cost" and never opened `engine.py`; the cheapest test of
a cost convention is to read what the engine charges** — MEDIUM) · **I-293** (**§20's `Blocking?`
column has carried C12 as `BLOCKING ON SEALING` since R5 while the note directly beneath it has read
`DISCHARGED` since R12 — a table asserting a seal blocker the document itself closed twenty days
earlier, found only because §20 was read column-by-column rather than against a supplied list** —
HIGH) · **I-294** (**`§21 horizon` carries a negative bracket excursion under I-181's own checker criterion
— *"depth 0, no negative excursion"* — caused by the half-open interval notation `(0.25, 0.54]`. It
is legitimate mathematics and not a defect in meaning, but the field FAILS the check that cleared
`success_criteria`, and `VALIDATION-GATE0-002` §5 applied that check to `success_criteria` only. The
site entered at R-009 as `(0.25, 0.27]` and R-010 preserves the counts byte-for-byte in kind — 2
opens, 3 closes, unchanged from HEAD [measured]. Named, NOT repaired: whether the notation or the
checker moves is Validation's, and rewriting a hashed field's notation on an unruled axis is the move
this dispatch forbids** — MEDIUM) · **I-295** (**`research/work/dated_sites.json` has been
uncommitted since 2026-08-25 20:44 UTC [measured — mtime], i.e. R-009 left its dated-site inventory
outside the book of record, and A3 makes the repo the book of record. R-010 has now invalidated its
`statement` and `horizon` offsets and lengths as well. NOT regenerated — no script was run and
`evaluate_dated_clauses.py` does not exist (I-173 / I-186) — and NOT committed, per dispatch** —
MEDIUM) · **I-296** (**this addendum authored 381 lines against a ~220 projection, 73% over, and its
own mid-task budget flag understated the overrun as ~32% because it was estimated rather than
measured; corrected on the face of R-010** — LOW).

---

*Director of Research · Castellan Capital · **addendum §16 added 2026-09-10 for revision R-010***
*Dispatch S4-D-011. Trial budget ZERO. Registry 0 / 0 / 3 at open and at close.*
