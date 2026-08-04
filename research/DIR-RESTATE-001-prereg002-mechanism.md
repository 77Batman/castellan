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
