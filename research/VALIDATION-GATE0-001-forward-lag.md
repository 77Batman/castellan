# VALIDATION GATE 0 · 001 — the forward-lag family

**Seat:** Head of Quantitative Validation (Seat 3) · **Date:** 2026-07-28
**To:** the Principal · cc CIO, Director of Research, Devil's Advocate, PM Pod B, Head of Data & Infrastructure
**Invocation:** the fourth and final Sprint 1 Opus unit. There is no fifth. The second Monday Risk meeting was cut to fund this.
**Reports to:** the Principal. Not suppressible or overrulable by the CIO.

**Contents.** §1 the companion ruling on inherited `N` and the forward window (D-009). §2 the ruling on capacity evaluability (I-026). §3 the H-series negative tests, authored before implementation (I-027 / I-021). §4 the Charter §4.3 Gate 0 intake verdict on `PREREG-001`. §5 what would change my mind. §6 findings no Issue Log entry covers.

House rule 6 throughout: **[measured]** = read or executed in this repository this session · **[cited]** = named external or internal source · **[inferred]** = reasoned from measured/cited facts · **[assumed]** = unverified premise, flagged.

**Read this session** [measured]: `PREREG-001-forward-lag.md` in full · `REDTEAM-001-agenda-and-forward-lag.md` in full · `DATA-PROBE-001-polymarket-orderbook.md` in full · `DATA-SPEC-polymarket-usable-history.md` §2 (T2/T4) and §7 · my own `VALIDATION-RULING-001` §4, `VALIDATION-RULING-002` §3, `VALIDATION-ACCEPTANCE-001` §5–6 · `reference/GATES.md` (Charter Part IV) · `logs/DECISION_RECORD.md` D-006…D-009 · `logs/ISSUE_LOG.md` I-002, I-003, I-004, I-011, I-012, I-021…I-028 · `agents/pm-digital-markets.md` · `harness/castellan/{registry,gates,stats,costs}.py`.

**Ran** [measured]: `python3 -m pytest harness/tests -q` → **96 passed**. `castellan.stats.expected_max_sharpe` and `min_backtest_length_years` at every `N` quoted below. SQLite reads of `book/registry.db` (**0 hypotheses, 0 trials, 1 event**), `book/vaults/` (**`.gitkeep` only**).

**Did not do:** no code modified, no data fetched, no backtest run, no registry write, no vault seal, no commit.

---

# 1. RULING C-001 — does `N_inherited` deflate the forward window?

> ## VERDICT
>
> **`N_inherited` does NOT deflate a genuinely confirmatory forward test. That test is `N = 1`.**
>
> **`N_inherited` governs everything else, and the exemption is narrow, conditional, earned, and revocable.**
>
> **The forward-lag family does not currently qualify for it, and would not be rescued if it did.**

This ruling governs **all future inherited-`N` families**. It is issued on its merits. §1.6 states what it does and does not do for the family in front of me, so that it is not read as a rescue.

## 1.1 Why the standard argument is right, and it is not a technicality

Under the global null — every configuration in the prior search has zero true edge — a researcher searches `N` configurations in-sample, selects one, and runs **one** pre-specified test on data that did not exist at selection time. The type-I error of that test is **α**. Not `N·α`, not `α` adjusted by anything.

The reason is structural, not procedural. The Bailey–Borwein–López de Prado–Zhu apparatus that Charter §4.1 imports — `E[max SR_N]`, DSR, MinBTL — is a correction for a **maximization operation**. `expected_max_sharpe(N)` is the expected value of the *maximum* of `N` draws. It is the right benchmark exactly when the reported number is a maximum. On the forward window, **no maximization occurred**: the specification was fixed before the data existed, and one statistic was computed on it. Benchmarking a single non-maximized draw against `E[max of 31,250]` is a category error, and a large one — `expected_max_sharpe(31252, 1.0) = 4.131` [measured] against a null expectation of `0`.

Put the consequence of the opposite ruling on the record, because it is decisive: **if inherited `N` deflated the confirmatory test, holdouts would have no value at all.** A holdout's entire epistemic content is that it converts a selected result into an unselected test. Charging the holdout the selection's denominator would make `[C, G]` no better than `[start, C]`, and the firm would have spent Option D and twelve months of waiting for nothing. D-006 chose Option D on the premise that unseen data tested against a frozen claim is worth waiting for. **That premise and a deflated forward window cannot both be true.**

**I note against my own instinct that my prior is guilt and this ruling is permissive.** I have tested it the only way available: by asking what it would cost the firm if I am wrong. §1.3 is that answer, and it is why the exemption carries five conditions rather than none.

## 1.2 The four things the exemption does NOT cover

The exemption is a statement about *one test*. It is not a statement about the family.

| Not covered | Denominator that applies | Why |
|---|---|---|
| **In-sample Sharpe, t-stat, DSR, PBO, WFE, parameter surface, subperiod positivity** | `N_total = Σ n_inherited(chain) + Σ logged(chain)` | Every one of these is computed over the research record, where the maximization happened. A forward window rehabilitates none of them. There is no route from "the confirmatory test is `N=1`" to "the in-sample statistics are `N=1`", and any submission that draws one is refused. |
| **The `≥ 4 years` and `≥ 1 full regime cycle` conjuncts of §4.4** | Neither — these are **not** MinBTL | Ruling 001 §4.1 already assigned them: MinBTL/DSR bind *effective observation count*; the four-year and regime clauses bind **calendar span**, which is a regime-coverage requirement and has nothing to do with sampling error. A family passing `MinBTL(1)` on a 95-day forward window still fails §4.4 on span. |
| **The `≥ 12 months` holdout floor** | Neither | Independent constant. Unaffected in both directions. |
| **Every forward computation after the first** | `N_forward`, a real and separately logged count | See §1.3. |

## 1.3 The five conditions. The exemption is earned per test, not granted per family

A confirmatory test is `N = 1` **only** where all five hold. Any seat asserting the exemption asserts these five, and Validation verifies them against the registry, not against the narrative.

**E1 — The statistic is named at sealing.** One statistic, one specification, one decision rule, one threshold, and a **stated α**, all inside the sealed binding field set. A statistic identified after the window opened is not confirmatory at any `N`.

**E2 — It is computed once.** The first computation is the test. There is no second look, no re-run "with the corrected costs", no "we also checked". This is the `HoldoutVault.open_once` discipline applied to the statistic rather than the payload, and it is enforced the same way: the computation is an event in the registry and a second one retires the window.

**E3 — Every other forward computation is a logged forward trial.** Diagnostics, per-cell decompositions, robustness checks and signal-generation runs on `[C, G]` are trials, they accrue to `N_forward`, and **if the reported result is selected from among them, the reported result's denominator is `N_forward`, not 1.** `PREREG-001` §9.6 allocates **30 post-seal trials to "forward-window signal generation and its diagnostics"** [measured]. Thirty forward trials with a best-of reported is `MinBTL(30)`, not `MinBTL(1)`. The exemption protects a confirmatory test; it does not protect a forward search wearing one as a hat.

**E4 — The freeze is mechanically evidenced, not asserted.** `prereg_sha256` sealed (P1), amendment refused (P3), tamper detected (P4), seal not postdating `C` (P7). Without P1–P8 in force the claim "the specification was fixed before the window" is a promise, and Acceptance 001 §5 already ruled what a promise is worth here. **The exemption is unavailable to any family sealed under a registry that cannot evidence its own freeze.**

**E5 — The window is genuinely FORWARD.** `holdout_classification = FORWARD`, `C` = the seal date at UTC day granularity, and no part of `[C, G]` predates the seal. A HISTORICAL holdout gets **no** exemption: channels K4 and K5 are open on it (Ruling 002 §3.2, my own correction against my own prior text), so the "data independent of the selection" premise fails and the whole argument collapses. **This is the largest single limit on the ruling and it is why it does not generalise to historical holdouts.**

Violate any one and the forward window is not confirmatory. It is another in-sample window with a later start date, and it carries `N_total`.

## 1.4 What survives deflation anyway — the Bayesian residue, and it is not rhetorical

Type-I error is unaffected by the search. **Positive predictive value is not.**

The forward test's evidence is a likelihood ratio. At the firm's own hurdle `t ≥ 3.0`, one-sided α = **0.001350** [measured]:

| Power of the confirmatory test | Likelihood ratio | Prior probability needed for posterior > 0.5 |
|---:|---:|---:|
| 0.30 | 222 | **0.45%** |
| 0.50 | 370 | **0.27%** |
| 0.80 | 593 | **0.17%** |

Read it as the honest statement of what a passing forward test buys: **at `t ≥ 3.0` and 50% power, a single confirmatory test is enough to carry a configuration whose prior was as low as 1 in 370, and not one whose prior was lower.** Whether best-of-31,250 leaves a prior above or below 1-in-370 is a judgment the firm cannot source [assumed either way], and I will not pretend to source it. What follows is a disclosure requirement, not an arithmetic deflation:

> **Binding.** Any Validation Report invoking the `N = 1` confirmatory exemption states, **on its face**: the inherited `N`, the α of the test, its power at the pre-registered effect size, and the sentence — *"The confirmatory test's type-I error is not inflated by the inherited search. Its positive predictive value is. This report establishes that the sealed specification survived one pre-specified test on unseen data. It does not establish that the specification was not selected from a large search, and the inherited N stands unreduced on every in-sample statistic in this report."*

A report that omits it is defective and I will return it — the same instrument as R1, for the same reason.

## 1.5 On the Principal's caution — I engage with it directly and do not point at the number

The Principal is right that the Director of Research's MinBTL fatality argument **presupposes the answer to this question**, and I have not used it. The ruling above was reached without reference to 17.06 years. Now the consequence for that number, stated cleanly:

| Where the DoR's arithmetic applies | Status |
|---|---|
| `MinBTL(31,252) = 17.06 yrs` at net SR 1.0, applied to the **in-sample record** `[start, C]` | **Stands, unmodified.** This ruling does not touch it. |
| The same, applied to a **properly-constructed confirmatory forward test** | **Does not apply.** `MinBTL(1) = 0`; `MinBTL(2) = 0.27 yrs` at SR 1.0 [measured]. |
| The claim that the family therefore needs **net SR ≥ 2.07** to clear the length criterion at four years | **Conditional, and the condition is now decided against it — for the forward window only.** It remains correct for the in-sample window. |

**And it changes nothing about the family's fate, for four independent reasons** — stated so the DoR's verdict is not read as having been undermined:

1. `MinBTL(40) = 4.79 years` at net SR 1.0 [measured]. **The family's own post-seal trial budget alone exceeds the four-year floor at the Gate 1 Sharpe minimum, with zero inheritance.** The length problem does not need `N_inherited` to bite.
2. The `≥ 4 years` and `≥ 1 regime cycle` conjuncts are untouched by this ruling and are independently failing today (§4, item 4).
3. DSR and PBO on the in-sample record consume `N_total` regardless.
4. `PREREG-001` has **not pre-registered a confirmatory forward statistic** (§4, item 3), so under E1 the family cannot claim the exemption at all as the document stands — and P7 forbids adding one after sealing.

**The ruling is therefore permissive in principle and inert for this family. That is the correct shape and it is why I am comfortable issuing it in the same unit as the intake verdict.**

## 1.6 Operational consequences, binding from today

- `FamilyStats` and every Validation Report carry **three** counts, never one: `n_inherited`, `n_logged`, and — where a confirmatory test is claimed — `n_forward`. §3 specifies the registry contract.
- `evaluate_gate1` currently applies **one** `n_trials` to the length criterion of whatever return series it is handed, with no concept of whether that series is a selection window or a confirmation window [measured, `gates.py:282–288`]. Under this ruling that is a live harness defect. §6 files it.
- **KC-001 is a kill condition, not a confirmatory test.** It tests `expectancy > 0` and `events ≥ 30` — a one-sided screen with no α and no power statement. **Surviving KC-001 confirms nothing at any `N`.** Recorded because "the family passed its forward test" is the sentence I expect to read on 2026-11-01 if this is not said now.

---

# 2. RULING C-002 — does §4.4 capacity require book depth?

> ## VERDICT
>
> **No. §4.4 capacity does NOT require order-book depth.**
>
> **The CIO's route SURVIVES. ADV-plus-impact-model is not merely permissible — it is the construction the Charter already specifies.**
>
> **Data & Infrastructure's inference is wrong, and so is the Devil's Advocate's. I overturn both.**
>
> **It does not save this family, for a reason that has nothing to do with capacity (§4, item 4).**

## 2.1 The argument, and it is short because the Charter already settles it

Charter §4.6 fixes the firm's cost stack [cited — `reference/GATES.md` §4.6]:

```
commission + 0.5·spread·capture_factor + Y·σ_daily·√(Q/ADV) + delay cost + borrow/funding carry
```

**There is no depth term in it.** The impact term is `Y·σ_daily·√(Q/ADV)` — the square-root law, parameterised on **ADV and daily volatility**, with `IMPACT_EXPONENT = 0.5` and `IMPACT_PREFACTOR_Y = 1.0` fixed as firm constants in §4.2. `CostModel.per_side_cost(trade_notional, sigma_daily, adv_notional)` implements exactly that and takes no depth argument [measured — `costs.py:32–47`]. §4.2 additionally fixes `ADV_PARTICIPATION_MAX = 0.05` — a capacity constraint expressed **entirely in ADV**.

Capacity is the largest allocation at which the strategy still reaches target net Sharpe. Net Sharpe at size is a function of cost at size. Cost at size is given by the stack above. **The stack above is an ADV construction.** A reading in which §4.4's capacity criterion requires book depth would make the Charter's own cost model structurally incapable of computing the Charter's own capacity criterion. I decline to sign an incoherence.

The CIO's supporting observation is also correct on its own terms and I confirm it independently: full book history is unavailable in equities too, and capacity work there is done on ADV and the square-root law. The impact literature the Charter imports is calibrated on participation rate, not on depth.

**Seat 9 and the Devil's Advocate both made the same inference and it is the same error: they equated data-spec criterion T4 with Charter §4.4 capacity.** They are different objects. T4 is a per-contract-day **tradability screen** — "was resting size within the T3 band ≥ `P_notional`, on both sides, on this day." §4.4 capacity is a **strategy-level scaling question**. T4 remains **[measured] unmeasurable** and I do not disturb that finding; it bites on the tradable-day count, which becomes an upper bound reported as "6-of-7, T4 unconfirmed" exactly as `DATA-SPEC` §2 already provides. It does not make capacity unevaluable.

**I note the shape of what I have just done.** The CIO disclosed his conflict correctly and raised the route without adopting it — which is the conduct the structure is for, and it is the reason I could evaluate the argument rather than the sponsor. Had he adopted it, my answer would be the same, because the argument is right. I record that I checked it against Appendix B #1 and found the argument survives without the sponsor.

## 2.2 The six conditions on the route. It is not a blank cheque

Ruling on the merits does not mean ruling without teeth. Any capacity number produced by this route is admissible **only** with all six:

**K1 — The ADV series is measured, PIT, and ingested.** From the trade-print endpoint into `PITStore` via `castellan.loaders`, two-timestamp discipline, consumed through `pit_price_panel` (A4). Not asserted, not extrapolated, not taken from a vendor page. Its left-censoring at CLOB launch (late 2022) [cited — I-026] is reported with it.

**K2 — ADV is qualified by trade frequency, and this is the condition that actually matters.** The square-root law is an empirical regularity **calibrated on venues with continuous two-sided liquidity provision**. A Polymarket contract-day whose "ADV" is generated by six discrete prints is not the same object as ADV on a continuously-quoted instrument, and the law's calibration does not extend to it. **Required:** the trailing-window median notional is reported alongside the **distribution of daily trade counts and inter-trade intervals**, and a minimum daily trade count is pre-registered below which a contract-day contributes no ADV observation. Where that minimum is not met, capacity on those days is **unevaluable — INSUFFICIENT-DATA, never PASS.** This is where the venue's thinness properly enters, and it enters as a measurement condition rather than as a doctrine about depth.

**K3 — `σ_daily` in price points.** On a `[0,1]`-bounded binary contract, log-return volatility diverges at the bounds — a 1¢ move on a 5¢ contract is 20%. The impact term is computed on **price-point volatility**, stated as such. This is I-023(a)'s units discipline applied to the impact term rather than the spread term; the same error is available in both places and only one of them has been logged.

**K4 — `Y` stays at the Charter's 1.0.** §4.2 fixes it "conservative until own fills calibrate it." The firm has zero fills on this venue. No venue-specific value of `Y` is admissible until it does, and no argument that Polymarket impact is milder than the equity default will be heard from a seat with no fills.

**K5 — Both binding constraints reported, minimum governs.** Capacity under the **participation cap** (`0.05 × ADV × turnover`) and capacity under the **impact model** (the size at which net Sharpe falls to target) are different constraints. Both are reported. **The minimum binds.** Reporting only the looser one is the failure mode this condition exists to prevent, and it is the one I expect.

**K6 — The face-of-report sentence, mandatory, verbatim:**

> *Capacity estimated from realized traded volume and the Charter §4.6 square-root impact model. **No resting book depth was observed at any point in this estimate, and none is retrievable for this venue.** This is capacity under a model whose prefactor is uncalibrated on this venue (Y = 1.0, Charter default, zero own fills). It is not a measurement of available liquidity.*

**I-026 is amended accordingly.** Its "capacity unevaluable → INSUFFICIENT-DATA → never PASS" line is **overturned**. T4-unmeasurable stands. The consequence drawn from it does not.

---

# 3. THE H-SERIES — negative tests for `n_inherited`, authored before implementation

**Authority and sequence.** I-021's finding is that the implementing seat authoring its own acceptance tests is how I-015 happened. The Principal has directed the remedy. **These tests are Validation's. Data & Infrastructure implements to them and does not author its own.** If an assertion below cannot be met, Seat 9 **stops and escalates to Validation** — it does not move the assertion. That instruction is identical to the one I attached to G1–G5 in Acceptance 001 §6, and for the same reason: an assertion that moves to accommodate an implementation was never a test.

**Scope.** These cover the DoR's H1–H4 (`PREREG-001` §9.5) and extend them. **Five of the fourteen cover defects that H1–H2 will *create* rather than defects that exist today** — H-10, H-11, H-13, and the double-count guard in H-5b. Those are the ones I expect to be argued with.

## 3.0 The registry contract these tests assert against

Stated first so the tests are unambiguous. `FamilyStats` becomes:

```
FamilyStats(
    family, 
    n_trials,       # = Σ n_inherited(chain) + Σ logged(chain)   — THE denominator
    n_inherited,    # = Σ n_inherited(chain)                     — declared, phantom, no returns
    n_logged,       # = Σ COUNT(*) trials(chain)                 — real, with returns
    trial_budget, sr_period_std, sr_period_mean, sr_period_best)
```

**Non-overlap rule, which I am deciding because it is operational and mine:** a family's `n_inherited` is the prior search attributable to **that family and not already carried by its predecessor chain**. Chain totals are summed, never re-declared. **KC-001 clause 3 ("opened with `n_inherited ≥` the killed family's final `n_trials` plus its own `n_inherited`") reads as a double count under transitive summation** and must be read as the non-overlap rule. KC-001 is signed by the Principal as written, so I am not amending it — I am recording the conflict and escalating the wording (§6, finding 5).

## 3.1 The fourteen tests

**H-1 · `test_h1_column_exists_defaults_zero_and_migrates`**
- Fresh registry: `PRAGMA table_info(hypotheses)` contains `n_inherited`, type `INTEGER`, `NOT NULL`, default `0`.
- `open_hypothesis(...)` omitting the argument → row reads `0`.
- Construct a DB from the **pre-change** `SCHEMA` literal with one hypothesis row, then open it with `TrialRegistry` → `_migrate()` adds the column, no exception, the pre-existing row reads `0`. *This is the `book/registry.db` path and it is not hypothetical.*

**H-2 · `test_h2_value_is_validated`**
- `n_inherited=-1` → `ValueError`. `n_inherited=3.7` → refused. `n_inherited=0` → accepted. `n_inherited=31250` → accepted and round-trips.

**H-3a · `test_h3_n_inherited_is_binding_and_changes_the_hash`**
- `"n_inherited" in registry._BINDING_FIELDS`.
- Two families identical in every other binding field but differing in `n_inherited` → **different** `prereg_sha256`.
- The `hypothesis_sealed` event's shadow copy contains `n_inherited` with the declared value. *A declared denominator that is not sealed is not a denominator (`PREREG-001` H1).*

**H-3b · `test_h3_negative_reregistration_with_different_n_inherited_is_refused`**
- Seal at 31250; re-call `open_hypothesis` with 3125 → raises `PreRegistrationAmendedError`; a `hypothesis_amendment_refused` event is logged listing `"n_inherited"` among the differing fields.
- Byte-identical re-call → no raise, no event. *Both branches asserted (P3).*

**H-3c · `test_h3_negative_raw_sqlite_downgrade_is_detected`**
- Seal at 31250. Raw `sqlite3` `UPDATE hypotheses SET n_inherited=0`.
- `registry.verify_prereg(family)` reports a mismatch **naming `n_inherited`**.
- `evaluate_gate1` returns **FAIL** on `Pre-registration integrity`.
- *Rationale: after this change the denominator is the single field an interested party would most want to move, and D-009's revision rule requires evidence for a downward move. P4 is what makes that rule enforceable rather than aspirational.*

**H-4 · `test_h4_n_trials_is_seeded_plus_logged`**
- `n_inherited=31250`, 2 logged trials → `n_trials == 31252`, `n_inherited == 31250`, `n_logged == 2`.
- `n_inherited=31250`, 0 logged trials → `n_trials == 31250`, `n_logged == 0`.

**H-5a · `test_h5_transitive_sum_across_chain_no_double_count`**
- `A`: `n_inherited=1000`, 3 logged. `B`: `predecessor_family="A"`, `n_inherited=50`, 2 logged. `C`: `predecessor_family="B"`, `n_inherited=0`, 1 logged.
- `family_stats("C")` → `n_trials == 1056`, `n_inherited == 1050`, `n_logged == 6`. **Exact equality, not `>=`** — the exact assertion is the double-count guard.
- `family_stats("A")` → `n_trials == 1003`. A predecessor is not inflated by its successors.

**H-5b · `test_h5_negative_successor_redeclaring_the_chain_is_refused`**
- `A`: `n_inherited=1000`, 3 logged (`n_trials == 1003`).
- Open `B` with `predecessor_family="A"` and `n_inherited=1003` — the naive KC-001 clause-3 reading — → raises `InheritedCountDoubleCountError`, message naming the chain total `1003` and the declared `1003`.
- Rule enforced: a successor's `n_inherited` **must be strictly less than** its predecessor chain's `n_trials`, because the chain is already summed. A genuine new search larger than the entire chain is a Validation escalation, not a silent registration.

**H-6a · `test_h6_sigma_sr_uses_logged_trials_only`**
- `n_inherited=31250`, exactly 2 logged trials with known per-period Sharpes `s1`, `s2`.
- `sr_period_std == approx(np.std([s1,s2], ddof=1))` — from **2** values, not 31252. Likewise `sr_period_mean`, `sr_period_best`.

**H-6b · `test_h6_negative_no_phantom_rows_are_synthesised`**
- After `open_hypothesis(n_inherited=31250)`: `SELECT COUNT(*) FROM trials WHERE family=?` == **0**.
- After 2 real trials: == **2**. Never 31252, never 31250.
- `registry.returns_matrix(family).shape[1] == 2`.
- *Rationale (the DoR's H4, and it is the one line of these tests I care about most): phantom trials have no return series and **none may be synthesised**. Seeding corrects the denominator in DSR and MinBTL. It cannot correct σ_SR, and any code that fabricates a return series to make it do so is a fatal defect, not an optimisation.*

**H-6c · `test_h6_negative_one_logged_trial_gives_no_dispersion`**
- `n_inherited=31250`, 1 logged trial → `sr_period_std is None`; `evaluate_gate1`'s DSR criterion is **INSUFFICIENT-DATA**, not PASS, and no dispersion is imputed from the seeded count.

**H-7 · `test_h7_dsr_consumes_the_seeded_denominator`**
- Twin families `U` (`n_inherited=0`) and `S` (`n_inherited=31250`), each with the **same** 2 logged trials and the same evaluated return series.
- `report_U.n_trials == 2`; `report_S.n_trials == 31252`.
- `DSR_S == approx(stats.deflated_sharpe_ratio(r, 31252, sr_std))`; `DSR_U == approx(...(r, 2, sr_std))`; `DSR_S < DSR_U` strictly.
- **Choose `r` such that `U` PASSes `DSR ≥ 0.95` and `S` FAILs it.** Seeding must change the **verdict**, not merely the number. A test that only asserts the number moved would pass on a cosmetic implementation.

**H-8 · `test_h8_minbtl_consumes_the_seeded_denominator_and_fails_a_short_backtest`** *(the DoR's H3, verbatim in intent)*
- Family seeded 31250, 2 logged trials. `evaluate_gate1(returns=r, backtest_years=4.0, oos_index=<daily index spanning exactly 4.00 calendar years>, periods_per_year=365)`, `r` calibrated to net annual Sharpe ≈ 1.0.
- Length criterion threshold string contains `MinBTL=17.06` (±0.05) and verdict is **FAIL**.
- Control: identical call on the unseeded twin (`N=2`, `MinBTL=0.27`) → **PASS**.
- *Under today's code the seeded case reads PASS. That is the defect, and this is the test that reads it.*

**H-9 · `test_h9_pbo_is_computed_on_logged_trials_only_and_the_report_says_so`**
- Seeded family with 20 logged trials → `returns_matrix.shape[1] == 20`; the PBO criterion is computed on 20 columns.
- `ValidationReport.to_markdown()` carries a note on the PBO criterion naming the real-trial column count and stating that inherited trials contribute none.
- *Rationale: CSCV requires return series. Phantom trials have none. **PBO is therefore structurally undeflated by `n_inherited` and always will be.** A report showing `N = 31,252` beside a PBO computed on 20 columns is misleading unless it says so on its face. This is a permanent limit of the seeding fix, not a bug, and it must be visible.*

**H-10 · `test_h10_negative_seeding_alone_does_not_blow_the_trial_budget`**
- Family seeded 31250, `trial_budget=40`, 2 logged trials → the `Trial count N (registry)` criterion note does **not** contain `"OVER BUDGET"`.
- Same family with 41 logged trials → it **does**.
- *Rationale: `gates.py:209` computes `over = fam.trial_budget and fam.n_trials > fam.trial_budget`. After H2, `n_trials` is 31,252 and **every seeded family reads OVER BUDGET on seeding alone.** The budget governs the firm's post-seal search; inherited trials are not post-seal search. This defect does not exist today — H2 creates it. (I-022's separate defect, that the verdict argument is a hard-coded literal `True`, is out of scope here and is not fixed by this test.)*

**H-11 · `test_h11_negative_seeded_family_with_no_logged_trials_is_insufficient_data`**
- Family seeded 31250, **zero** logged trials, `evaluate_gate1` on an external return series.
- The `Trial count N (registry)` criterion is **INSUFFICIENT-DATA**, not PASS, with a note naming `logged=0`.
- *Rationale: the guard today is `if fam.n_trials == 0` (`gates.py:203`). After H2 a seeded family never reaches zero, so seeding would silently convert "this family has never run anything" into a fully populated denominator. **The guard must key on `n_logged`.** H2 creates this. It is the exact shape of I-014 — a criterion reading PASS off a count that does not mean what the criterion thinks it means.*

**H-12 · `test_h12_report_renders_the_decomposition_not_a_bare_total`**
- `ValidationReport.to_markdown()` for a seeded family renders the decomposition on its face: the total, the declared inherited figure, and the logged figure, all three visible — e.g. `N = 31,252 (31,250 declared inherited [inferred, D-009] + 2 logged)`.
- Assert all three integers and the word `inherited` are present.
- *Rationale: house rule 6. A bare `N = 31,252` reads as 31,252 observed trials. 31,250 of them are an **[inferred]** declaration whose ×10 factor is the CIO's estimate, not a measurement. A report that launders an [inferred] declaration into a [measured]-looking integer is precisely the defect the label discipline exists to prevent.*

**H-13 · `test_h13_negative_an_unseeded_family_is_bit_for_bit_unchanged`** — *the negative case the Principal named*
- Family registered with **no** `n_inherited` argument, 3 logged trials.
- `family_stats` → `n_trials == 3`, `n_logged == 3`, `n_inherited == 0`; `sr_period_std / _mean / _best` identical to the pre-change values.
- `evaluate_gate1`'s **full criteria list** — every name, value, threshold string and verdict — is identical to the evaluation of the same family registered with `n_inherited=0` explicitly.
- `prereg_sha256` for `n_inherited=0`-explicit **equals** the hash for the omitted argument. *If the default and the explicit zero hash differently, every family's seal silently changes meaning on upgrade.*
- *This is the test that proves H1–H2 add a capability rather than change a behaviour.*

**H-14 · `test_h14_forward_lag_001_declared_denominator_end_to_end`**
- Register `forward-lag-001` with `PREREG-001` §19's field set verbatim, `n_inherited=31250`, `trial_budget=40`. Log 2 trials.
- `family_stats.n_trials == 31252`.
- `stats.expected_max_sharpe(31252, 1.0) == approx(4.1308, abs=1e-3)` [measured].
- `stats.min_backtest_length_years(31252, 1.0, 365) == approx(17.063, abs=0.02)` [measured].
- `evaluate_gate1` on a 4.00-calendar-year `oos_index` at net SR ≈ 1.0 → length **FAIL**, DSR **FAIL**.
- *Rationale: D-009's declaration stops being a sentence and becomes a computed consequence. This is the acceptance test for the whole change.*

## 3.2 What these tests do not do

They make the declared denominator **enforced**. They do not make it **correct** — the ×10 regime-candidate factor remains **[inferred]** (D-009), and no test can promote a label. They do nothing about I-011, which contaminates hypothesis formation upstream of any registry. And they do not deflate PBO, which is structurally undeflatable (H-9). Anyone reading "H1–H4 landed" as "the denominator problem is solved" has over-read it by a wide margin, and H-12 exists so the report cannot support that reading.

---

# 4. GATE 0 INTAKE VERDICT — `PREREG-001`, the forward-lag family

> ## VERDICT: **ADMITTED-AS-EXPLORATORY**
>
> Pre-declared **ineligible for Gate 1**. This is the Charter's own instrument for "known-unvalidatable but interesting lines" (§4.3) and this family is exactly that shape.
>
> ## **AND THE SEAL IS REFUSED ON THIS TEXT.**
>
> `PREREG-001` as written **is not sealable today.** Six defects are enumerated at §4.2, each of which P7 makes **permanent** at seal. Sealing this document is worse than delaying it, and §4.3 shows the delay is free.

I concur with the Director of Research's recommendation of ADMITTED-AS-EXPLORATORY. **I reach it on different and firmer grounds** — a measured span upper bound and a data dependency that does not exist — and I do not adopt the MinBTL route, for the reasons at §1.5. I considered REJECTED seriously (§4.4) and declined it.

## 4.1 The seven items

| § | Gate 0 item | Verdict | Reason |
|---|---|---|---|
| 4.3(1) | Mechanism | **PASS** | §3 names three counterparty populations and why each accepts the loss. Not "the data says so." The Devil's Advocate conceded coherence [cited — Red-Team §B.6.6] and I concur independently. This item genuinely passes and it is the only one that does so cleanly. |
| 4.3(2) | Pre-registered falsifier | **FAIL** | F-001 is not decisive. Four specific defects, §4.1.1. |
| 4.3(3) | Universe / horizon / rebalance / success criteria before first run | **FAIL** | Stated in detail, but two load-bearing omissions: no confirmatory forward statistic (§1.3 E1), and the quote-liveness gate is unexecutable on measured data with no substitute pre-registered. §4.1.2. |
| 4.3(4) | Required data exists within Part III | **FAIL** | Two independent grounds, both [measured]. §4.1.3. |
| 4.3(5) | Survivorship and look-ahead identified, mitigation named | **PASS on the letter** | M1–M4 and §8.2 identify the exposure and name mitigations. That is what §4.3(5) asks for. **But M1's feasibility is undetermined** — `DATA-PROBE-001` §4 declined the on-chain diff as backfill-scale — and `PREREG-001` §8.1 makes M1-impossible a REJECT trigger by its own terms. Passing on the letter, unresolved in substance. |
| 4.3(6) | Trial counter opened and instrumented | **FAIL** | `book/registry.db`: **0 hypotheses, 0 trials** [measured]. And I-027: no path exists by which the declared denominator reaches `FamilyStats.n_trials`. The item is not satisfiable until the H-series lands. |
| 4.3(7) | Holdout defined and locked | **FAIL** | Defined at §10. **Not locked** — `book/vaults/` holds `.gitkeep` only [measured]. And §4.1.4: it **cannot** be locked today. |

**Four FAILs. One PASS-on-the-letter. §4.3 is binary and a single failure is fatal.** The verdict is not ADMITTED and could not have been.

### 4.1.1 F-001 is not a decisive falsifier — four defects

The Principal asked specifically. My answer is no, and the reasons are arithmetic rather than stylistic.

**(a) `k* = argmax_k ρ(k)` over `k ∈ [−36, +36]` is a selection over 73 candidates, and `PREREG-001` §5 asserts it "selects nothing from a menu and is registered as `N = 1`." That assertion is false.** Under the null of no relationship at any lag, `argmax` of a noisy `ρ(k)` is approximately uniform over the 73 lags. So:

| Leg | Fires under pure noise with probability ≈ | Meaning |
|---|---:|---|
| (i) DIRECTION, `k* ≤ 0` | 37/73 ≈ **51%** | **A pure-noise process survives leg (i) roughly half the time.** |
| (ii) ARTIFACT, `k* ≥ 24` | 13/73 ≈ **18%** | |
| (i) or (ii) | ≈ **69%** | ⇒ ≈**31% of pure-noise pairs survive both** |

`PREREG-001` §5 calls leg (i) "the leg most likely to fire and it is nearly free to evaluate." It is nearly free. It is also close to a coin flip. **A falsifier that a zero-signal process survives ~31% of the time is not a falsifier at any conventional standard**, and there is no stated α anywhere in F-001 against which to judge it.

**(b) No null distribution and no significance level.** F-001 is three bare point comparisons. It states no test statistic distribution, no α, and no power. It therefore cannot falsify at a stated error rate and cannot confirm at one either. This is the root defect and (a) is its consequence.

**(c) No minimum qualifying-bar count.** After the paired-quotable gate, `ρ(k)` may be estimated on a few dozen bars. `PREREG-001` pre-registers no floor. An `argmax` over 73 lags on 40 observations is noise with a decimal point.

**(d) Leg (iii) evaluates capture at `k*` — the argmax of the same sample.** Median signed capture is measured "from the executable price at `t₀+2h` to the executable price at `t₀+k*`," where `k*` was chosen as the peak of `ρ(k)` on that sample. **That is selecting the exit at the peak of a surface, which is item 7 of my standing leakage audit and the operation Charter §4.6 names as *the* overfitting operation.** Here the bias runs *toward survival of the falsifier* — the capture is measured at the lag that maximises co-movement. **A falsifier biased toward its own survival is a defective falsifier**, and this one is biased by construction.

*(Minor, but it will bite: leg (ii)'s D1 clause — "`k*` on the quotable subsample differs by more than 50% from `k*` on the all-bars sample" — is a percentage difference on a small integer lag index. It is undefined at `k*_quotable = 0`, and `2` vs `3` is a 50% difference. Not a threshold, a coin toss.)*

**None of (a)–(d) is expensive to fix.** All four must be fixed **before** sealing, because P7 forbids adding any of them after.

### 4.1.2 Does the quote-liveness gating discriminate a real lag from quote sparsity?

The Principal asked specifically, noting I-028 — the family is intra-venue, so there is no session calendar. My answer: **the design is directionally right and, as pre-registered, it does not discriminate. Two reasons, and the first is decisive.**

**The gate requires an observable the firm has [measured] established it cannot observe.** `PREREG-001` §8.3(A)2: *"a bar enters any estimate only if both legs carried a two-sided quote in that bar and in the preceding bar."* **"Did both legs carry a two-sided quote in this bar" is a historical order-book question.** `DATA-PROBE-001` establishes [measured] that historical book state is unavailable and structurally unreconstructible — resting orders never touch the chain. **The single design element `PREREG-001` §8.3 calls "the section that makes the design admissible" is built on data that does not exist.** The same defect voids §6.2's entry rule, which admits an entry only if the forward leg "carried a two-sided quote within `S_max` **at the entry instant**."

The only substitute is `DATA-SPEC` §2's T2 trade-print proxy, which `PREREG-001` does **not** pre-register for this purpose. Under it the gate becomes *"both legs printed trades in this bar and the preceding bar"* — **a volume gate, not a quote gate.** I grant the DoR the point that the "and the preceding bar" clause gives it real teeth against the specific artifact: a leg that was quote-dead from `t₀` to `t₀+19h` did not print at `t₀+18h`, so the jump bar is dropped. That is a genuine design merit and I record it. But the retained sample is then exactly the set of continuously-active periods, which on a thin venue may be a small and event-concentrated minority of bars — and **no minimum retained-bar count or retained fraction is pre-registered.** D1 then compares a large contaminated estimate against a small possibly-degenerate one, and its "differ by more than 50%" verdict fires or does not at random. Discrimination requires a stated minimum sample and a stated null. F-001 has neither (§4.1.1(b), (c)).

**Second, and independently: D2 is not executable under the family's own ingest plan.** §8.3(C) D2 is a **cross-sectional regression of `k*` (estimated per pair) on the forward leg's median inter-quote interval**. §13 step 2 ingests *"the single densest pair-cluster by traded notional."* **A cross-sectional regression cannot be run across one cluster.** §8.3 calls D2 "a required diagnostic in every artifact." It is required and it is unrunnable — an internal contradiction in the sealable text, and one that P7 would make permanent.

So: the transposition from cross-venue to intra-venue is correct and the DoR was right to make it (I-028 is properly resolved as a matter of design). The instrument it produces cannot be executed on this venue's measured data surface, and that is a Gate 0(4) failure, not a Gate 0(2) quibble.

### 4.1.3 Item 4 — the required data does not exist, on two independent grounds

**(i) Historical quote state.** Above. `PREREG-001` §7 lists order-book snapshots as "UNCONFIRMED." As of `DATA-PROBE-001` they are **[measured] CONFIRMED ABSENT**, and the pre-registration has not been updated to reflect its own firm's probe. Note carefully: **this is not the capacity question I ruled on at §2.** I ruled that §4.4 capacity does not need depth, and I hold that. **The quote-liveness gate needs quote state, which is a different dependency, and it fails.** The family loses item 4 for a reason nobody has named, on the same measured facts from which two seats drew a different and incorrect conclusion.

**(ii) Calendar span, measured upper bound, below the floor.** The trade-print surface is left-censored at CLOB launch, late 2022 [cited — I-026, `DATA-PROBE-001` §5; a 2020-era market returns zero trades]. To 2026-07-28 that is **3.57–3.82 years** [measured — computed this session from 2022-12-31 and 2022-10-01 respectively], **before a single day is removed by T1–T7 screening.** No screening can increase span. **Ruling 001 §4.4's pre-commitment therefore fires now, on an upper bound rather than on a measurement:**

> *"If measured tradable history under the accepted spec is < 4 years of calendar span … the forward-lag family is **REJECTED for Gate 1** and may be **ADMITTED-AS-EXPLORATORY** only. No Sharpe changes this."*

I pre-committed to that rule before the measurement existed, precisely so that I could not be argued out of it afterwards. I apply it. **This, not MinBTL, is what makes the family ineligible for Gate 1 today**, and it is the ground on which the exploratory verdict rests.

**Honest qualification, because the rule cuts both ways:** the span defect is **curable by elapsed time**. Four years from CLOB launch arrives between **2026-10-01 and 2026-12-31** [measured]. This is exactly I-004's observation that a family short today can become admissible by waiting, and it is the strongest single argument against REJECTED.

### 4.1.4 Item 7 — the holdout cannot be locked today, and the "seal same-day" directive is not executable

`PREREG-001` §19's vault block requires, as inputs to `HoldoutVault.seal()`: `dataset_id`, `instrument_identity` (*"condition IDs / outcome token IDs, **exhaustive**"*), `query_semantics`, and `schema_fingerprint`. **All four are `<placeholders>`** — they come from the archival on-chain enumeration (M1), which `DATA-PROBE-001` §4 explicitly did not run.

**You cannot seal a vault whose instrument identity set is undetermined.** C4 and P7 require the prereg seal and the vault seal in the same session on the same UTC day. **Therefore `PREREG-001` cannot be sealed today, regardless of the H-series, and the "land the fix, then seal same-day" plan has a second blocker nobody has stated.** This is a finding, not an obstruction: it is better to know it now than at the seal.

## 4.2 The six defects P7 would make permanent

Sealing is the act that fixes `C` and freezes the binding fields (D-007, P3). After it, nothing may be added and the only remedy is a successor family — whose forward window starts **later** than a delayed seal would have. Six items are missing or wrong today:

| # | Defect | Consequence at seal |
|---|---|---|
| 1 | **No confirmatory forward statistic named**, with no α. `success_criteria` instead commits to `N = n_inherited + logged trials` for all Gate 1 statistics. | Under §1.3 E1, the family **permanently forfeits the `N = 1` confirmatory exemption** — by its own sealed text, on the day I granted the exemption. |
| 2 | **F-001's four defects** (§4.1.1): no null, no α, no minimum bar count, exit at the argmax of the same sample. | A falsifier that cannot falsify, frozen. |
| 3 | **Quote-liveness gate unexecutable; no trade-print substitute pre-registered**, no minimum retained-bar fraction. | The admissibility-making element, frozen unusable. |
| 4 | **D2 unrunnable under §13 step 2's single-cluster ingest.** | A required diagnostic, frozen unrunnable. |
| 5 | **`n_inherited` has no registry field** (I-027). | `n_inherited=31250` in the §19 block is not a valid argument. The call **fails, or silently drops it**. |
| 6 | **Vault seal inputs undetermined** (§4.1.4). | C4/P7 cannot be satisfied. |

## 4.3 The sequencing call, and I overturn the CIO's operational rationale

D-009 records the CIO's reasoning: *"`C` is the seal date, so every day of delay is a day the forward window does not accrue."* The premise is right; the conclusion does not follow.

**Under P3 the binding fields are immutable. The remedy for a defective seal is a successor family — whose window starts on the successor's seal date, which is later than a delayed seal.** Sealing a defective pre-registration therefore costs *more* forward window than delaying, not less, and it additionally poisons the successor's denominator through transitive inheritance. **Delay is strictly cheaper on the CIO's own objective function.** I am not asserting authority over sequencing; I am pointing out the arithmetic runs the other way.

**Second, the delay is close to free anyway**, because item 4's span defect self-cures between 2026-10-01 and 2026-12-31 and the vault cannot be sealed before M1 runs regardless. **Third, KC-001's 2026-10-31 date is absolute and does not move with the seal** [cited — KC-001 clause 4, §12.1.2]. A seal slipping two weeks shortens the KC-001 window and does not extend it. That is a real cost, and I weigh it: a shortened window makes clause (b) — fewer than 30 tradable events — **more** likely to fire, which is a kill on insufficient signal. That is the rule working, not the rule being defeated.

## 4.4 Why not REJECTED

I considered it and I want the reasoning visible.

**For REJECT:** span below the floor; the discriminator unexecutable on measured data; a falsifier that survives noise ~31% of the time; materiality of ~12–25 bp of firm NAV at $50k; and 100% of the firm's Opus spend, including this unit, directed here [cited — I-025]. Under §4.3's own logic — find impossibility at the cheapest stage — it is defensible.

**Against, and it governs:** Charter §4.3 defines ADMITTED-AS-EXPLORATORY as the instrument for *"known-unvalidatable but interesting lines."* **That is a precise description of this family.** The mechanism genuinely passes item 1. The span defect is curable by calendar. The forward window accrues at zero compute. KC-001 resolves it on 2026-10-31 either way, and its silence clause means it resolves even if nothing is done. REJECT would be over-reading the evidence and would discard a coherent mechanism on defects that are cheap to fix or that fix themselves.

**I take the Charter's own instrument.** The exploratory verdict is not a courtesy: it pre-declares the family **ineligible for Gate 1**, which is the substantive consequence, and it is not appealable to the CIO.

## 4.5 Conditions — what must be true before this document is sealed

**Blocking on the seal:**

| # | Condition | Owner |
|---|---|---|
| V1 | **H-series lands**, implemented to §3, tests unmodified. Any assertion that cannot be met is escalated to Validation, not moved. | Head of Data & Infrastructure |
| V2 | **F-001 rebuilt** with a null distribution, a stated α, a minimum qualifying-bar count, and leg (iii)'s exit lag pre-specified as a **fixed constant, not `k*`**. The plateau centroid over `k`, never the argmax, if a data-dependent lag is retained at all. | Director of Research → Validation |
| V3 | **The quote-liveness gate restated on measurable data** — the T2 trade-print substitute, pre-registered, with its bias direction stated ([cited — `DATA-SPEC` §2: it overstates tradability]) and a **minimum retained-bar fraction** below which the estimate is INSUFFICIENT-DATA. | Director of Research → Validation |
| V4 | **D2 made executable or struck.** Either §13 step 2 ingests enough pairs for a cross-sectional regression, or D2 is removed and the loss of the discriminator is stated on the face of the pre-registration. | Director of Research |
| V5 | **A confirmatory forward statistic named with its α**, if the family wants the §1.3 exemption. If it does not, say so explicitly — that is a legitimate choice and is better than silence. | Director of Research / PM Pod B |
| V6 | **M1 run**, so the vault's `instrument_identity`, `dataset_id`, `query_semantics` and `schema_fingerprint` are determinable. | Head of Data & Infrastructure |

**Not blocking on the seal, blocking on Gate 1:** I-023 (both parts, per D-009 addition 3), I-022, and the §2 conditions K1–K6 on any capacity claim.

**Standing, and not negotiable:** the family is ineligible for Gate 1 until measured tradable span under an accepted `DATA-SPEC` clears **4 calendar years** with Ruling 001 §4.1 continuity (≥60% coverage, no 90-day gap) **and** ≥1 full regime cycle. `DATA-SPEC` acceptance (C5) remains ungranted and I am not granting it in this unit — it is not blocking on the seal, and I do not have the unit.

---

# 5. What would change my mind

| # | On | What would change it |
|---:|---|---|
| 1 | **C-001, the `N=1` confirmatory exemption** | A demonstration that the forward window is not independent of the selection — e.g. evidence that any seat consulted `[C, G]` data, or a family sealed without P1–P8 in force. Either collapses the independence premise and the exemption with it. Also: evidence that E3 is unenforceable in practice, i.e. that the firm cannot in fact distinguish a confirmatory computation from a forward search in the registry. If it cannot, the exemption is unadministrable and I would withdraw it rather than leave a rule that only honest seats obey. |
| 2 | **C-002, capacity without depth** | A demonstration that the square-root impact law's calibration fails on episodically-quoted instruments **in a direction and magnitude the participation cap does not bound**. That is measurable from trade prints and it is exactly what condition K2 is for. If K2's measurement shows Polymarket contract-days are generated by a handful of prints, capacity on those days is INSUFFICIENT-DATA by my own condition and the CIO's route dies on the facts having survived on the law. |
| 3 | **Overturning I-026's "never PASS"** | Nothing about who benefits. An argument that §4.6's cost stack **does** contain a depth dependency I have missed. I read `costs.py` and §4.6 and it does not. |
| 4 | **The Gate 0 verdict** | Item 4 cured on both grounds — a pre-registered, executable substitute for quote state **and** measured tradable span ≥ 4 years with continuity — plus V2/V5. Both, not either. That would move the verdict from ADMITTED-AS-EXPLORATORY toward ADMITTED. Nothing less does. |
| 5 | **The refusal to seal** | A demonstration that any of the six §4.2 defects is in fact amendable post-seal without a successor family. It would have to overturn P3, which I wrote. |
| 6 | **The `N = 1` framing for `F-001`** | Nothing. `argmax` over 73 lags is a selection over 73 candidates. The pre-registration's assertion that it "selects nothing from a menu" is arithmetically wrong and no restatement fixes it — only a stated null does. |
| 7 | **The H-series** | Seat 9 demonstrating that a specific assertion is unmeetable **for a stated technical reason**. That is an escalation I will hear and rule on. "It is awkward to implement" is not one. |
| 8 | **`N_inherited = 31,250` itself** | Not mine to move and I am not moving it. D-009 fixed it; downward revision requires reconstructed evidence of the actual candidates considered, and §1.5 note 1 records that `MinBTL(40) = 4.79 years` already exceeds the four-year floor at SR 1.0 with **zero** inheritance. The factor of 10 is not load-bearing. |

---

# 6. Findings no existing Issue Log entry covers

Ten. Each [measured] unless marked. None duplicates I-001…I-028. Filed to the CRO's log via the CIO.

**F-1 · No firm-level register of confirmatory tests · MEDIUM · quant-validation.** C-001 grants `N = 1` **per test**. Family-wise error across *confirmatory tests* is a real and uncontrolled quantity: twenty families each getting one honest `N=1` test at α = 0.00135 yields a firm-level false-positive probability of ~2.7%. The registry counts trials within a family and has no notion of a confirmatory-test count across families. **The exemption creates this exposure and nothing currently measures it.** Remedy: a `confirmatory_test` event kind, counted firm-wide, reported in the Monthly Letter.

**F-2 · `evaluate_gate1` has no concept of a confirmation window · MEDIUM · head-of-data-infra.** [measured — `gates.py:282–288`] One `fam.n_trials` is applied to the length criterion of whatever return series is passed, with no distinction between a selection window and a confirmatory one. Under C-001 the correct denominators differ. The harness cannot express the ruling it must now enforce.

**F-3 · H2 will make every seeded family read OVER BUDGET · MEDIUM · head-of-data-infra.** [measured — `gates.py:209`] `over = fam.n_trials > fam.trial_budget` fires on seeding alone once `n_trials` includes 31,250. Distinct from I-022 (which is that the criterion cannot fail at all); this is that it will always annotate. Test H-10.

**F-4 · H2 will let seeding paper over a family that has run nothing · MEDIUM · head-of-data-infra.** [measured — `gates.py:203`] The `if fam.n_trials == 0 → INSUFFICIENT-DATA` guard never fires for a seeded family. Same shape as I-014 — a criterion reading off a count that no longer means what it means. Test H-11.

**F-5 · KC-001 clause 3 double-counts under transitive summation · MEDIUM · the Principal (wording).** *"a new family opened with `n_inherited ≥` the killed family's final `n_trials` plus its own `n_inherited`"* — but `family_stats` sums the chain, so the predecessor's `N` would be counted twice. KC-001 is signed as written and I am not amending it; §3.0 records the non-overlap reading and H-5b enforces it. **The wording needs the Principal's restatement**, not a seat's interpretation.

**F-6 · The quote-liveness gate requires data measured not to exist · HIGH · quant-validation.** I-026 covers depth → capacity, which I have now overturned. **It does not cover this**, which is the surviving and larger consequence of the same probe: `PREREG-001` §8.3(A)2 and §6.2's entry rule both require historical two-sided quote state. Gate 0(4) fails on it. This is the finding that decides the family and it is currently unlogged.

**F-7 · F-001 leg (iii) selects the exit at the argmax of its own sample · HIGH · director-of-research.** Capture measured to `t₀+k*` where `k*` is the peak of `ρ(k)` on the same data. Charter §4.6 names peak-selection as *the* overfitting operation; here it biases the falsifier toward its own survival. Under §4.1.1(a) the falsifier already survives pure noise ~31% of the time before this is counted.

**F-8 · D2 is unrunnable under the family's own ingest plan · MEDIUM · director-of-research.** §8.3(C) requires a cross-sectional regression across pairs; §13 step 2 ingests one cluster. Internal contradiction in a sealable document.

**F-9 · The vault cannot be sealed before M1 runs · MEDIUM · pm-digital-markets / head-of-data-infra.** All four `HoldoutVault.seal()` identity arguments in §19 are placeholders sourced from an enumeration nobody has run. C4/P7 same-day sealing is not executable today, independent of the H-series.

**F-10 · `forward_window_min_length` is a unitless `REAL` · LOW · head-of-data-infra.** [measured — `registry.py` SCHEMA] `12.0` means months here and nothing in the schema says so. Flagged by the DoR at `PREREG-001` §10.3 and never given an issue number. A float with no unit on a Charter §4.4 floor is a misreading waiting to happen.

---

*Head of Quantitative Validation · Castellan Capital · 2026-07-28*
*Rulings C-001 and C-002 are Gate-level determinations and are final short of a written Principal override. The Gate 0 intake verdict is ADMITTED-AS-EXPLORATORY with the seal refused on this text; it is not appealable to the CIO. No code was modified, no data fetched, nothing sealed, nothing committed.*
