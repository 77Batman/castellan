# DATA-SPEC — Usable Polymarket History

**Seat:** Head of Data & Infrastructure
**Date:** 2026-07-28
**Status:** DRAFT — awaiting Validation's written acceptance per Ruling 001 §4.4. No measurement has been run. No Polymarket API has been called in the preparation of this document.
**Drafted against:** `research/VALIDATION-RULING-001-holdout-regime.md` §4.1–4.4 (criteria T1–T7, stratification §4.3, effective-N method, continuity floor). References below to "the Ruling" mean that document.
**Blocks:** I-004 (Pod B Gate 0 admissibility), measurement of usable Polymarket history (Ruling 001 §6).

House rule 6 applies throughout: **[measured]** (read in this repository), **[cited]** (external, named), **[inferred]** (reasoned from measured/cited facts), **[assumed]** (unverified premise, flagged). This document is a specification written before measurement, so it is expected to carry very few `[measured]` claims. An unlabelled assumption is a defect — flag anything you find.

---

## 1. Purpose, and the tradable-vs-platform-age distinction

**The question this spec answers is not "how old is Polymarket."** Polymarket has existed since 2020 [assumed — general knowledge, not verified this session, and irrelevant to the ruling either way]. Platform age is a fact about a company's incorporation history. It says nothing about whether a strategy could have been executed at the sizes this firm would need, at any point in that history.

**The question this spec answers is: how many contract-days were genuinely tradable — at the position size and edge magnitude a real strategy would require — and over what calendar span do those contract-days lie?**

Those are two different quantities (§4 develops this in full):

- A **count** — how many independent, tradable observations exist, which binds sampling-error criteria (DSR, PBO, MinBTL(N)).
- A **span** — how much calendar time those observations cover, which binds regime-coverage criteria (§4.4's "≥ 4 years and ≥ 1 full regime cycle", the ≥12-month holdout).

A venue can be four calendar years old and still fail both quantities if most of its life was a handful of illiquid contracts with a one-sided book. Conversely a venue could in principle have a short calendar history that is nonetheless dense and continuously tradable — that would fail the calendar-span criterion but say something different about the count criterion. **Reporting only "the platform has existed since year X" answers neither question and would be exactly the kind of convenient number the Ruling was written to prevent (§4.1).** This spec exists to define "tradable" precisely enough that measuring it produces one answer regardless of who runs the measurement or what answer would be convenient.

**Why this is written blind.** Every threshold below that could be tuned to a desired outcome is instead expressed as a formula referencing a quantity the firm has not yet fixed (intended position notional, claimed edge), per the hard constraint in this task and per the Ruling's own instruction (§4.2: "an absolute number chosen independently of those is a number chosen for convenience"). Where the Ruling itself sets a fixed constant (T6's 2¢/98¢ bound, the 60%/90-day continuity floor), I inherit it rather than re-deriving it, because it is not mine to move (Ruling §7, "Charter constants... not mine to move at all" — note T6 is Validation's judgment call, not a Charter constant, but it is still not mine to move without a reasoned argument made *before* measurement).

---

## 2. Definition of a tradable contract-day

A **contract-day** is one calendar day of one specific Polymarket contract (a single outcome token on a single condition). It counts as **TRADABLE** only if all seven criteria below hold, evaluated strictly on information available at the decision time — `knowledge_time ≤ decision_time` (Charter §4.6 [cited]). **Every screen below is defined on a trailing window ending strictly before the day being screened.** Screening a day on its own realized full-day volume or on same-day book state is look-ahead and is explicitly disallowed, per the Ruling's overriding constraint (§4.2).

### T1 — Volume floor

**Definition.** Trailing-window median daily notional traded ≥ `F`.

**Window.** 20 trading sessions (calendar days on which the contract had any listed trade), trailing, ending at `t-1`. **Rationale for 20 over 5:** Polymarket contract-day volume is `[assumed]` to be noisy and event-clustered (spikes around news, near-zero on quiet days) even for contracts that are genuinely tradable on average — a 5-session median is more exposed to a single quiet week producing a false fail, or a single spike week producing a false pass, than a 20-session median. Since the venue is thin by the Charter's own description (§3.2 [cited]), stability of the screen matters more than responsiveness. **A 5-session window is run as a robustness check** (§7, step 6) and reported alongside; if T1 pass/fail flips materially between the two windows, that instability is itself reported, not resolved by picking whichever window passes more days.

**Threshold `F` — formula, not a constant.**

```
F = 20 × P_notional
```

where `P_notional` is the strategy's intended per-contract position notional in USD, to be supplied by the sponsoring pod at pre-registration. **This is not my number to invent** — it is derived directly from the Ruling's binding requirement: `F ≥ 20 × P_notional` so that `ADV_PARTICIPATION_MAX = 0.05` (Charter §4.2 [cited]) is satisfiable at the intended size, i.e. `P_notional / F ≤ 0.05 ⟺ F ≥ 20 × P_notional`. I take the ruling's floor as equality (the tightest admissible `F`) rather than adding slack, because slack here only inflates the apparent tradable-day count.

**No numeric value of `F` exists yet.** `P_notional` has not been stated by any pod. Until it is, T1 is a formula, not a filter that can run.

### T2 — Two-sided market

**Definition.** Both a bid and an ask present, with a finite quoted spread, for ≥ `θ_2` of the observation window.

**Threshold `θ_2 = 0.80`** of intraday snapshots in the trading day (or of the day's listed quote updates, whichever the underlying data supports — see measurability note below) `[assumed — my judgment call, not derived from any cited source]`. Rationale: a market that is two-sided most but not all of the day is still tradable for an end-of-day or scheduled-rebalance strategy; a market that is one-sided more than a fifth of the day has enough dead time that fills cannot be assumed reliably available at the strategy's chosen rebalance moments. This is a placeholder-grade judgment call and I flag it as one — it should move if Validation or the Devil's Advocate has a reasoned objection, per house rule 7, **before** measurement.

**Measurability — flagged per the Ruling's instruction (§4.2).** T2 requires historical order-book state (not just trade prints). Whether Polymarket's public API exposes retrievable historical book snapshots, as opposed to only the current live book, is **not confirmed** — I have not queried it, per the hard constraint on this document, and I am not relying on training-era recollection of the API surface as a substitute for confirming it. **This is the first mechanical step of the measurement procedure (§7, step 1)**, run once this spec is accepted and before any T1–T7 screening begins. If historical book state is unavailable:

- **Proxy:** treat a contract-day as satisfying T2 if it has ≥ 1 trade print on both sides of the prevailing mid within the day (i.e., at least one trade executed at a price implying a standing bid and at least one implying a standing ask), or, failing that granularity, if daily trade count ≥ some minimum and trades occurred at more than one distinct price level.
- **Bias direction, stated per the Ruling's requirement:** this proxy **overstates** tradability. A market can print occasional two-sided trades from a single opportunistic counterparty while the resting book is thin or absent between prints — exactly the case a genuine market-maker-style strategy could not have executed against. Any T2-derived count is therefore an **upper bound**, and is reported as such, not as a measured value.

### T3 — Spread ceiling

**Definition.** Quoted half-spread ≤ `S_max`.

**Threshold — formula, not a constant.**

```
S_max = 0.5 × G
```

where `G` is the strategy's claimed per-trade gross edge (in the same units as the quoted spread — price points on the [0,1] contract scale, or basis points of notional, whichever the pre-registration uses). This is the Ruling's own formula (§4.2, T3): a half-spread above 50% of the claimed edge is not takeable regardless of anything else measured. **No numeric value exists yet** — `G` is set jointly with pre-registration, per the Ruling, and has not been stated. T3 is unrunnable as a fixed number until it is.

**Note on interaction with T1.** `F` and `S_max` are both downstream of quantities the sponsoring pod must state before Gate 0 admission can even be scoped numerically. Practically: the pod should supply `P_notional` and `G` in the same pre-registration document that opens the hypothesis family, so Data & Infra can run T1 and T3 as concrete numbers rather than symbols.

### T4 — Depth at intended size

**Definition.** Resting size within the T3 band (i.e., within `S_max` of the touch) ≥ `P_notional`, on **both** sides, measured at touch-plus-ceiling — not total book depth. Size resting outside the `S_max` band does not count, because a strategy that requires the T3 spread ceiling to be economic cannot also require walking the book past that ceiling to fill.

**Measurability.** Same order-book dependency as T2, same open question (§7 step 1), same fallback if unavailable: **no volume-only proxy for T4 is proposed**, because depth-at-a-specific-price-band is not recoverable from trade prints or aggregate volume without materially misrepresenting what was actually resting. If historical book depth is unavailable, **T4 is reported as unmeasurable, not proxied**, and any tradable-day count is qualified accordingly: a count that passes T1/T2(proxy)/T3/T5/T6/T7 but cannot evaluate T4 is reported as **"6-of-7, T4 unconfirmed"**, distinct from a true 7-of-7 TRADABLE count, and is not summed into the headline tradable-day number without that qualifier attached.

### T5 — Outside resolution blackout

**Definition.** Contract-days inside the settlement window — where price is mechanically pinned by a known-but-not-yet-formally-settled outcome — do not count as signal observations, because the trailing period before payout is not evidence of a strategy's edge; it is evidence of the market having already converged.

**Blackout rule — formula with contract-specific override.**

```
blackout[contract] = [t_outcome_effectively_known, t_final_settlement + B]
```

where `t_outcome_effectively_known` and `t_final_settlement` are read from the contract's own resolution metadata (resolution-source timestamp and payout timestamp) where the data exposes them, and `B` is a buffer, **default `B = 1` calendar day**, applied when contract-specific dispute-window metadata is not available `[assumed — conservative default, not derived from a cited oracle-liveness figure since I have not verified Polymarket's dispute-window parameters this session]`. Where a contract's resolution source publishes an explicit dispute/liveness window (e.g., an optimistic-oracle challenge period), that window is used in place of the default `B`, per-contract, and the substitution is logged so the measurement is auditable.

**Interaction with T6.** T5 and T6 target different mechanisms — T5 excludes the *settlement-pending* window regardless of price level, T6 excludes days where price has *already* hit the tick-grid bound regardless of settlement status. A day can fail one, the other, both, or neither; they are evaluated independently and a day failing either is not TRADABLE.

### T6 — Price not at the bounds

**Definition.** Contract-days at ≤ 2¢ or ≥ 98¢ excluded by default. **This threshold is the Ruling's, not mine — it is inherited as a fixed constant** (§4.2, T6), not re-derived, because moving it is Validation's judgment call to make on a reasoned argument, not Data & Infra's to set by formula. Rationale as given in the Ruling: at these levels the return distribution is dominated by the tick grid and is degenerate, so a day at the bound contributes negligible information relative to the risk of appearing to inflate the tradable count with days that cannot produce a real fill spread.

**Pre-registered inversion.** If a strategy is specifically a tail-price strategy, this exclusion is inverted only with a stated reason in that strategy's pre-registration — not decided during measurement.

### T7 — Resolution rule known and stable at entry

**Definition.** Resolution criteria, resolution source, and dispute mechanism published and unchanged as of the decision time for that contract-day.

**Mechanism.** At ingest, store a content hash of the market's resolution-criteria text as published at the day's `knowledge_time`, alongside the source's own "last modified" metadata where exposed. A contract-day fails T7 if the criteria hash observed at that day's decision time differs from the hash at the contract's listing date, i.e., the rules were clarified or changed mid-life. `[assumed]`: Polymarket exposes either a resolution-criteria-changed audit trail or at minimum a "last updated" field on market metadata sufficient to detect this; **unconfirmed, to be checked at measurement step 1 alongside the T2/T4 order-book question.** If neither is exposed, the fallback is conservative exclusion: any contract whose resolution source class is known `[cited from public reputation, not this-session-verified]` to have a documented history of criteria disputes for that market category is excluded from the family entirely at the stratification stage (§3), rather than attempting a per-day judgment call that cannot be made mechanically.

---

## 3. Poolability and stratification across heterogeneous resolution rules

Per the Ruling §4.3, contracts pool into one hypothesis family only where they share all four of:

| Axis | Definition |
|---|---|
| (i) Resolution source class | e.g., UMA optimistic oracle, Polymarket-internal admin resolution, third-party data feed, sports-league official result — a categorical tag, not a per-contract free-text field |
| (ii) Settlement mechanics | binary cash-settled / scalar / multi-outcome |
| (iii) Dispute and escalation exposure | whether the resolution source has a formal dispute/challenge mechanism and, if so, its typical duration bucket (none / <48h / ≥48h) |
| (iv) Economic mechanism | the specific mechanism the hypothesis asserts (e.g., "post-news forward-price lag" is a mechanism claim, not "election markets") — this axis is supplied by the sponsoring pod's pre-registration, not inferred from the contract |

**Stratification table schema**, delivered before any pooling:

| Column | Meaning |
|---|---|
| `stratum_id` | firm-internal identifier for the (i)–(iii) combination, distinct from the pod's (iv) mechanism claim |
| `resolution_source_class` | axis (i) |
| `settlement_mechanics` | axis (ii) |
| `dispute_exposure_tier` | axis (iii) |
| `n_contracts` | distinct contracts (condition IDs) in the stratum |
| `raw_contract_days` | Σ tradable contract-days, unadjusted |
| `effective_contract_days` | Σ N_eff-weighted, per §5 |
| `pct_of_family_raw` | stratum's share of the family's total raw tradable contract-days |
| `pct_of_family_effective` | stratum's share on the effective count — reported alongside raw because the two can diverge materially if one stratum is internally correlated |

**Concentration rule (Ruling §4.3, inherited as-is):** if a single stratum contributes **>50%** of a family's tradable contract-days, the family's evidence *is* that stratum's — either the hypothesis is restated as being about that stratum specifically, or the pooled result is reported with the concentration flagged **and** the Charter §4.4 subperiod-positivity criterion (≥60% of blocks net-positive) is additionally evaluated **per stratum**, not only pooled.

**Contract → underlying-event mapping**, feeding §5's independence adjustment: primary mapping uses Polymarket's own event-grouping construct (multiple outcome markets grouped under one parent event, e.g. several candidate-specific markets under one election event) where the API exposes it `[assumed — unconfirmed structure, to be checked at measurement step 1]`. Where the native grouping under- or over-groups relative to genuine economic correlation (e.g., two nominally separate events that are in fact near-deterministic functions of the same underlying outcome), a manual override list is maintained, dated, and justified in one line per override — this is a judgment call and is logged as such rather than silently folded into the automatic grouping.

---

## 4. The unit question: contract-days vs. calendar-days

**Contract-days are the unit of count.** Every criterion in §2 is evaluated per contract-day, and `N` (raw and effective, §5) is a sum of contract-days. This is the unit that answers "how many independent observations exist" and it is what `MinBTL(N)`, DSR, and PBO consume (Ruling §4.1, table).

**Calendar days are the unit of span.** The Charter §4.4 "≥4 years and ≥1 full regime cycle" clause and the "≥12 months" holdout clause are about elapsed calendar time, not observation count, per the Ruling's explicit ruling on this (§4.1): "This clause is about regime coverage, not sample size. Four years of dense data spanning one regime still fails." A family with fifty thousand contract-days packed into eight months of calendar time satisfies no version of the regime-coverage requirement, however large `N` is.

**Both bind, independently, and neither substitutes for the other.** This spec reports both:
- **Calendar span** = `last tradable contract-day's date − first tradable contract-day's date`, for the family (pooled) and per stratum, plus the continuity check of §6.
- **Effective observation count** = `Σ N_eff` per §5, converted to years at the strategy's true rebalance frequency for the `MinBTL(N)` comparison, exactly as the Ruling specifies.

**A harness implementation note that bears directly on this**, found while reading `harness/castellan/gates.py` for this draft `[measured]`: `evaluate_gate1`'s length criterion computes `years = backtest_years if backtest_years is not None else r.size / periods_per_year` (`gates.py`, length-criterion block). **If `backtest_years` is not passed explicitly, the harness silently falls back to treating the *count* of return observations as a proxy for calendar span** — exactly the conflation this spec and the Ruling both warn against. **Operational consequence for the measurement procedure (§7): `backtest_years` must always be passed explicitly, computed as true calendar span from the contract-day timeline, never left to the harness default**, for any Polymarket family. This is a Data & Infra implementation obligation, not a Validation ruling, and I am recording it here so it is not rediscovered as a live defect the way I-007 was.

---

## 5. Effective-N / breadth adjustment method

Adopted verbatim from the Ruling (§4.3), specified here so the measurement step is mechanical:

```
N_eff(period) = n / (1 + (n − 1)·ρ̄)
```

- `n` = number of distinct tradable contracts active in that period (day, or the strategy's rebalance period — see below).
- `ρ̄` = average pairwise correlation of contemporaneous contract returns within the strategy's universe, computed over the same trailing window used for T1 (20 sessions), on the price series of contracts jointly active in that window.
- **Effective observations** = `Σ N_eff` over periods, summed at the strategy's true rebalance frequency (not necessarily daily — if the strategy rebalances weekly, `N_eff` is computed per rebalance period, not per day and then re-aggregated, to avoid double-counting persistence within a period as independent breadth).
- Converted to years for the `MinBTL(N)` comparison using the harness's `min_backtest_length_years(n_trials, target_annual_sr, periods_per_year)` `[measured — harness/castellan/stats.py]`, with `periods_per_year` set to the strategy's actual rebalance frequency, not defaulted to 252.

**Reported side by side**, per the Ruling's requirement: raw contract-day count and effective count, pooled and per stratum. The ratio between them is itself a finding, not just an intermediate — the Ruling states its own prior that the ratio will be large on a venue where correlated contracts cluster around a handful of events `[inferred, per Ruling — this is the hypothesis the measurement settles, not a fact assumed here]`.

**Contract-day vs. period ambiguity, resolved explicitly:** because contracts have finite lifecycles (a given Polymarket contract exists from listing to resolution, typically weeks to months, not years), `n` in a given period counts whichever contracts are simultaneously live and tradable in that window — this is structurally a rolling/panel measure, analogous to counting live futures contracts in a continuous series, not a fixed cross-section. The stratification table (§3) is what makes this comparable across time: `n` is reported per stratum per period, not just pooled, since two contracts from different strata being simultaneously live does not make them correlated observations of the same mechanism.

---

## 6. Continuity requirements

Inherited from the Ruling (§4.1) as fixed constants, not re-derived:

- Tradable days must cover **≥60% of calendar days** in the measured span.
- **No single gap may exceed 90 consecutive calendar days.**

**Definition of "covered," made precise for a venue of finite-lived contracts.** A calendar day is "covered" for continuity purposes if the pooled family (or, when the concentration rule of §3 fires, the dominant stratum) has **at least one** contract-day meeting all seven T1–T7 criteria on that date. This is deliberately an aggregate-across-contracts definition, not a per-contract one: individual Polymarket contracts do not and structurally cannot span four years (§5), so continuity is a property of the family's rolling coverage over its instrument sequence, analogous to a continuous futures series built from individual expiring contracts. This interpretive choice is `[inferred]` from the Ruling's own framing (§4.1's warning about "two dense clusters four years apart") but the aggregate-vs-per-contract question is not addressed explicitly in the Ruling text, so it is flagged here as a judgment call subject to correction before measurement.

**Reported**, per contract per stratum per family: the full daily coverage timeline (a boolean series over the candidate calendar span), the computed coverage fraction, and the location and length of every gap ≥30 calendar days (not only the ones that would fail the 90-day rule) — so the Principal's §4.4 sprint-scheduling tradeoff (Ruling §4.4, the pin-`C`-early-vs-wait table) can be computed from the actual shape of the data rather than a single summary statistic.

---

## 7. Measurement procedure — to be run once this spec is accepted

Mechanical steps, in order, so the measurement is a procedure rather than a series of judgment calls made after seeing partial results.

1. **Resolve the two open measurability questions before touching contract-day data**: (a) does the Polymarket public API expose retrievable historical order-book snapshots, or only current book state (governs T2/T4 — proxy vs. direct); (b) does market metadata expose a resolution-criteria-change history or reliable "last modified" field (governs T7 fallback), and does it expose native event-grouping (feeds §3's mapping). Document findings in writing, with source, before proceeding — this is itself the first `[measured]` claim the follow-on report will carry.
2. **Ingest raw**, via `castellan.loaders`, into `PITStore` (`book/pit.db`) — condition IDs, event groupings, resolution-source metadata, resolution-criteria text/hash, listing and resolution timestamps, trade prints, and order-book state to whatever depth step 1 establishes is available. No pre-adjustment; two-timestamp discipline (`event_time` / `knowledge_time`) applies to every field, including resolution-criteria text.
3. **Enumerate the candidate universe** as defined by the sponsoring pod's pre-registration (category, mechanism claim). Universe definition is the pod's, not Data & Infra's, per the Charter's seat boundaries.
4. **Require `P_notional` and `G`** from the pod's pre-registration before running T1/T3 as numbers. If not supplied, T1 and T3 remain symbolic and the measurement reports coverage under a small labelled grid of illustrative `P_notional`/`G` values rather than inventing a single figure — labelled explicitly as illustrative, not as the firm's answer.
5. **Screen every contract-day** against T1–T7 using only trailing-window / `knowledge_time ≤ decision_time` information, per §2. Record each criterion's individual pass/fail per contract-day, not only the AND-combined result — this makes it possible to answer "which criterion is binding" rather than only "tradable or not."
6. **Run T1 twice** — 20-session and 5-session trailing windows — and report both; flag any material divergence.
7. **Build the stratification table** (§3) before computing any pooled statistic.
8. **Compute raw and effective contract-day counts** (§5), pooled and per stratum, and the >50%-concentration check.
9. **Compute calendar span, coverage fraction, and gap structure** (§6), pooled and per dominant stratum where concentration fires.
10. **Report the full timeline**, not just totals, per the Ruling's requirement (§4.4) — this is what lets the Principal's pin-`C`-early-vs-wait tradeoff be computed rather than guessed.
11. **Pass `backtest_years` explicitly** to any harness call (`evaluate_gate1` et al.) as the calendar-span figure from step 9 — never rely on the harness's `r.size / periods_per_year` default (§4 note).
12. **Label every output** per house rule 6. Anything derived via the T2/T4 proxy (if step 1 finds no historical book data) is reported as an explicit upper bound, segregated from 7-of-7-confirmed counts, never blended into one headline number.
13. **Deliver the measurement as a separate artifact** (not a revision of this spec) to Validation, referencing this spec's accepted version by hash/commit, per the Ruling's sequencing requirement — measurement is reported against the accepted spec unchanged.

---

## 8. What this spec cannot determine, and what would change it

**Cannot determine without measurement (by design):**
- Any actual count, span, or coverage number. That is the entire point of writing this blind.
- Whether the family clears the Ruling's verdict rule (§4.4: <4 years calendar span or continuity failure ⇒ REJECTED / ADMITTED-AS-EXPLORATORY only).
- Whether the >50% stratum-concentration trigger fires, or for which stratum.

**Cannot determine from this session at all (network access withheld by hard constraint):**
- Whether historical order-book snapshots are retrievable (T2/T4 measurability — step 1 of §7).
- Whether resolution-criteria change history or native event-grouping is exposed by the API (T7 fallback, §3 mapping — also step 1 of §7).
- Any Polymarket-specific numeric parameter (typical dispute-window length, actual UMA liveness periods, etc.) used in T5's default buffer — the `B = 1 day` default is a conservative placeholder, not a researched figure.

**What would change this spec, stated as falsifiers per house rule 2, mirroring the Ruling's own §7:**
- If step 1 of §7 confirms historical order-book data IS available, T2/T4 move from proxy/unmeasurable to directly measured, and the proxy-bias caveats in §2 are removed for those criteria.
- If the sponsoring pod's pre-registration states `P_notional` and `G` materially different from any illustrative grid used in an interim report, T1 and T3 are recomputed — they are formulas, not cached numbers, and must be re-run on the actual stated values.
- If Validation or the Devil's Advocate raises a reasoned objection to the `θ_2 = 0.80` T2 threshold, the 20-session T1 window choice, the aggregate-vs-per-contract continuity definition (§6), or the `B = 1 day` T5 default — all four are my judgment calls, explicitly flagged as such, and per the Ruling's own stated asymmetry (§7) they may be moved **before** measurement runs and not after, regardless of what the measurement would show.
- If the API's native event-grouping (§3) is found to materially mis-group contracts relative to true economic correlation, the manual-override mechanism in §3 is exercised and logged, not silently absorbed.

---

*Head of Data & Infrastructure · Castellan Capital · 2026-07-28*
*Draft only. Acceptance is Validation's to grant in writing, per Ruling 001 §4.4. Measurement does not begin until acceptance is recorded.*
