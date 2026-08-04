# VALIDATION RULING 004 — ML trial accounting: search space, configuration counting, nested CV, seeds, and the definition of `N`

**Seat:** Head of Quantitative Validation (Seat 3) · **Reports to:** the Principal
**Date:** 2026-08-04 · *first run 2026-08-03, terminated on infrastructure error before any
write; completed 2026-08-04. Both dates are stated rather than one label asserted, per I-046.*
**Status:** BINDING on Seats 1, 2, 6–10. Appealable only to the Principal, in writing.
**Instrument:** binding specification + pre-authored acceptance tests. No Charter constant is
moved by this document and no Charter amendment is requested by it.
**Dispatched by:** the CIO, S2-D-006, discharging Standing Order 001 §1's third objective.
Nothing in the dispatch binds the verdict.
**Type:** specification and verdict only. No code modified, no data fetched, no backtest run,
no hypothesis opened, no trial registered. `book/registry.db` stands at 0 hypotheses / 0 trials.

House rule 6 applies throughout: **[measured]** = read or computed in this repository this
session; **[cited]** = external source named in Charter Appendix C, or an internal document
named inline; **[inferred]** = reasoned from measured facts; **[assumed]** = a premise I could
not verify and am flagging as such.

---

## 0. Provenance — what was read, what was run, what this seat did not do

**Read in full** [measured]: `ops/STANDING-ORDER-001.md`; `reference/GATES.md`;
`reference/CONSTRAINTS.md`; `FUND_CHARTER.md` (Parts I–IX and Appendices B–D);
`research/VALIDATION-RULING-001-holdout-regime.md`; `-002-c-placement.md`;
`-003-carry-accounting.md`; `harness/castellan/registry.py`; `harness/castellan/grid.py`;
`harness/castellan/engine.py`; `harness/castellan/cv.py`; `harness/castellan/gates.py`;
`harness/castellan/stats.py`; `harness/castellan/__init__.py`.

**Read in part** [measured]: `research/PREREG-002-crypto-funding-basis.md` §7, §8, §9, §10
(the sections the dispatch names); `research/VALIDATION-GATE0-001-forward-lag.md` §1.3
(the C-001 E-series); `logs/ISSUE_LOG.md` (index and I-001–I-003, I-011, I-022, I-027,
I-045–I-048); `logs/DECISION_RECORD.md` (S2-D-002 §3–§5, S2-D-005).

**Run** [measured]: `python3 -m pytest harness/tests -q` → **160 passed**, before and after.
Pure-function arithmetic on `castellan.stats` in a throwaway interpreter —
`expected_max_sharpe`, `min_backtest_length_years`, and closed-form algebra derived from
them. **No market data was touched, no `run_backtest` call was made, and no registry write
occurred.** `min_backtest_length_years` is a pure function of `(N, SR, periods_per_year)`
and consumes no sample; computing it is not a backtest, and PREREG-002 §7.3 and §10.4
already establish that precedent [cited].

**Not done, per the dispatch constraints:** no code modified, no data fetched, nothing
sealed, nothing committed, no trial logged, no hypothesis opened. Nothing in `harness/`,
`book/`, or `research/` other than this file and the four Issue Log entries at §11 was
written.

### 0.1 A citation in the dispatch that does not resolve, corrected on the record

The dispatch directs me to `FUND_CHARTER.md` **Part VII §7.2** for "conditioning choices,
menus, `N` accounting, `n_inherited`." Charter §7.2 is the **Research Memo** template
[measured]; it contains none of those. The material described is at
**`research/PREREG-002-crypto-funding-basis.md` §7.1–§7.4 and §10.1–§10.6**, and the
`n_inherited` machinery is at `harness/castellan/registry.py` `_BINDING_FIELDS`,
`open_hypothesis`, and `family_stats` [measured]. I read the intended material and this
ruling is built on it. The mis-citation is recorded because a future reader sent to
Charter §7.2 will find nothing and may conclude the rule does not exist.

### 0.2 Continuity disclosure — this ruling was produced across two runs

The first run of this dispatch terminated on an infrastructure error immediately after
completing its reading and arithmetic and before any file was written. **Nothing of the
first run reached disk** [measured — the CIO verified the absence of this file, an intact
0/0 registry, an unmodified tree, and a green 160-test suite; I re-verified the suite].

**What was lost and re-derived:** nothing. The reading context carried across the
termination intact, including every measured figure in §2 and §3 below.

**Whether the conclusion moved between runs:** it did not. **The only evidence for that
statement is my own account of my own prior reasoning, and there is no artifact against
which to check it, because the first run wrote none. It is therefore marked `[assumed]`,
not `[measured]`, and a reader should treat it with exactly that weight.** The arithmetic
in §2–§3 is independently re-runnable by anyone and is `[measured]`; the claim about the
stability of my reasoning is not.

---

## 1. THE RULING IN BRIEF

> **`N` for a machine-learning family is the sealed cardinality of its declared search
> space — every configuration the declared procedure may evaluate against data, counted as
> the product of its declared dimensions — plus every `run_backtest` call in the family,
> plus any inherited count:**
>
> ```
> N_ML  =  n_inherited  +  n_declared_fits  +  n_logged
> ```
>
> **with exactly one reduction: a candidate set whose selection is fully re-performed
> inside a correctly purged and embargoed nested inner loop, and from which nothing but the
> outer-fold aggregate is reported, contributes 1 rather than its cardinality.**

Five things follow, and each is a numbered clause below.

1. **The `§7.2` menu discount does not apply to a fitting procedure, and this is an
   extension of that rule rather than an exception to it.** PREREG-002 §7.2 grants a
   declared menu a contribution of 1 because "a choice made *before any measurement*, from
   a menu declared *in the sealed pre-registration*, and *binding thereafter*, involves no
   search over results" [cited]. A hyperparameter search selects **by reference to a
   quantity computed from the sample**. That is what fitting is. The discount's own stated
   condition therefore fails, and the full cardinality is charged. **ML-13.**

2. **A continuous hyperparameter has no menu size until it is discretized, so it must be
   discretized at declaration.** An explicit grid is charged its point count; a random
   search is charged its declared draw count; a sequential optimizer (Bayesian, TPE,
   CMA-ES, gradient) is charged its **declared iteration budget**. An un-budgeted
   continuous search has an unreconstructable `N` and is **inadmissible at Gate 0** —
   never INSUFFICIENT-DATA-then-argued, inadmissible. **ML-6.**

3. **`N` alone does not deflate anything. `N × σ_SR` does.** `deflated_sharpe_ratio`
   benchmarks against `expected_max_sharpe(N, σ_SR)`, which is **linear in σ_SR**
   [measured — `stats.py:111`]. `family_stats.sr_period_std` is computed from logged trials
   only [measured — `registry.py:531–549`]. A family that declares a search space of ten
   thousand and logs three near-identical survivors reports a σ_SR near zero and defeats
   DSR **at any `N`**. This is the largest hole in the firm's apparatus for ML work and it
   is closed by a mandatory **dispersion sample** — configurations drawn uniformly from the
   declared space *before* selection, each a full logged trial. **ML-16.**

4. **The arithmetic forecloses most of what "ML" usually means, on this firm's data, before
   any research is spent.** At the Gate 1 net-Sharpe floor of 1.0, on the 6.571 years of
   BTC/ETH history the firm actually holds, the **maximum admissible total `N` is 109**
   [measured — §2.2]. After the diagnostics this ruling requires, roughly **30–40
   configurations of genuine search** remain. That is the whole budget. **ML-3.**

5. **Purged CV as the harness ships it is not sufficient for a fitted family, and one of
   its two splitters applies no purge or embargo at all.** `walk_forward_windows` yields
   `idx[:fold[0]]` as training — every bar strictly before the fold, unpurged and
   unembargoed [measured — `cv.py:43–61`]. `purged_kfold_splits` purges the label span but
   embargoes only `⌈0.01·T⌉` bars, which for a 2,398-bar sample is **24 bars** [measured] —
   shorter than a 30-day feature lookback, so a training bar after the test fold computes
   its features from inside it. **ML-18.**

**Effectivity.** Clauses ML-1 through ML-10, ML-12 through ML-17, ML-18 through ML-27 are
**effective immediately**. Clauses ML-11 and ML-3's *enforcement* are **blocked on harness
work that does not exist** (§9), and until it exists the consequence is stated plainly and
is not softened:

> **No ML family may be sealed as Gate-1-eligible. Until `n_declared_fits` reaches
> `family_stats().n_trials`, an ML family may be ADMITTED-AS-EXPLORATORY only (Charter
> §4.3), may be researched, and may not pass Gate 1.** The firm holds zero ML families
> today, so this costs nothing today. It is stated now so that it cannot be discovered
> later, at the moment it is expensive.

---

## 2. THE ARITHMETIC THAT GOVERNS — computed, not asserted

Everything in this section is a pure function of `castellan.stats`. No sample is consumed.

### 2.1 MinBTL is frequency-invariant, which is worth stating once

`min_backtest_length_years(N, SR_ann, ppy)` computes `(E[max Z_N] / SR_period)² / ppy`
[measured — `stats.py:119–133`]. Substituting `SR_period = SR_ann/√ppy`:

```
MinBTL_years  =  E[max Z_N]²  /  SR_ann²
```

`ppy` cancels exactly. Verified numerically: `mb(1000, 1.0, 365) = mb(1000, 1.0, 252) =
10.5958160686` [measured]. **The required backtest length depends only on the trial count
and the realized Sharpe, never on the bar frequency** — so a family cannot buy length by
sampling more finely, and a seat that proposes hourly bars to "get more observations"
should be shown this line.

### 2.2 The admissible search space, by available history and realized Sharpe

Maximum total `N` satisfying `MinBTL(N, SR) ≤ span`, by bisection [measured]:

| Available calendar span | at net SR 1.0 | at net SR 1.5 | at net SR 2.0 |
|---|---:|---:|---:|
| 2 years | 7 | 33 | 242 |
| 3 years | 13 | 121 | 2,128 |
| 4 years *(Charter §4.4 floor)* | 25 | 420 | 17,844 |
| 5 years | 45 | 1,422 | 145,785 |
| **6.571 years** *(BTC/ETH, PREREG-002 §8 [cited])* | **109** | 9,384 | 3,826,211 |
| 8 years | 242 | 51,134 | — |
| 10 years | 724 | 536,957 | — |

**Three readings, and the third is the one that matters.**

*First:* **the Charter's own 4-year floor admits a total `N` of 25 at the Sharpe floor.**
A 3-parameter grid at 5 values per axis is 125 points and is arithmetically dead on a
4-year sample before a single bar is fitted. `grid_from_center`'s `max_points=200` refusal
[measured — `grid.py:47–50`] is *looser* than the statistics; the binding constraint is
MinBTL, not the guard.

*Second:* on the firm's **best** data surface, the entire admissible search space at the
Gate 1 Sharpe floor is **109**. This reproduces PREREG-002 §10.4's independently measured
ceiling of 110 to within one trial; the one-trial difference is that 110 requires 6.574
years against 6.571 available, which §10.4 itself records as "exactly at the span — zero
margin" [cited]. **The true maximum is 109 and I am recording the correction.**

*Third, and this is the honest complication a one-sided reading would hide:* **the ceiling
explodes with realized Sharpe.** `evaluate_gate1` evaluates MinBTL at the *realized* OOS
Sharpe [measured — `gates.py:336–344`], so a family realizing 2.0 clears MinBTL at `N` in
the millions. **MinBTL is therefore weak precisely against the case it looks designed to
catch: a large search that produced a high in-sample Sharpe.** The criterion that bites
there is DSR, and DSR bites only through σ_SR. §2.3 is that arithmetic, and §5's dispersion
sample is the consequence.

### 2.3 What DSR actually demands of an ML family

For `T` bars and approximately normal returns, `deflated_sharpe_ratio ≥ 0.95` requires
`(SR_p − SR_0)·√(T−1) ≥ 1.645`, with `SR_0 = E[max Z_N]·σ_SR` [measured —
`stats.py:104–116`]. Annualizing at `T = 2,398` bars (6.571 years daily):

```
required net SR_ann  ≈  E[max Z_N] · σ_SR_ann  +  0.642
```

| | σ_SR = 0.20 | σ_SR = 0.40 | σ_SR = 0.60 | σ_SR = 0.80 |
|---|---:|---:|---:|---:|
| N = 10 | 0.96 | 1.27 | 1.59 | 1.90 |
| N = 32 | 1.06 | 1.48 | 1.90 | 2.32 |
| N = 110 | 1.15 | 1.67 | 2.18 | 2.69 |
| N = 1,000 | 1.29 | 1.94 | 2.59 | 3.25 |
| N = 10,000 | 1.41 | 2.19 | 2.96 | 3.73 |
| N = 100,000 | 1.52 | 2.40 | 3.28 | 4.15 |

[measured — closed form above, evaluated on `expected_max_sharpe`]

**Read across a row, then down a column.** Moving `N` from 10 to 100,000 — four orders of
magnitude — raises the DSR bar by **0.56 Sharpe** at `σ_SR = 0.20`. Moving `σ_SR` from
0.20 to 0.80 at fixed `N = 1,000` raises it by **1.96**. **σ_SR is roughly three times more
load-bearing than `N` over the ranges an ML family will actually occupy.**

That is the finding this ruling is built around, and it inverts the naive emphasis. The
Standing Order asks for trial accounting, and trial accounting is necessary — but a firm
that counts `N` scrupulously and lets the sponsor choose which trials get a return series
has instrumented the *less* important half of the deflation and left the more important
half to the sponsor's discretion. **Whoever chooses which configurations are logged is
choosing σ_SR, and σ_SR is the unit the whole of §4.1 is denominated in.**

### 2.4 How large a dispersion sample, and why 32

σ_SR is a standard deviation estimated from `m` draws; its relative standard error is
`1/√(2(m−1))`, and `E[max]` is linear in σ_SR, so that error passes straight into the
deflation benchmark:

| m | RSE of σ_SR |
|---:|---:|
| 5 | 35.4% |
| 10 | 23.6% |
| 16 | 18.3% |
| **32** | **12.7%** |
| 64 | 8.9% |
| 100 | 7.1% |

[measured]

**I set the floor at `m ≥ 32`.** At 32 the benchmark carries ~13% relative error, which
against the 0.642 additive term and a bar of order 1.5–2.5 is a tolerable ±0.1–0.2 Sharpe
of imprecision. At 16 it is ~18% and the benchmark is doing less work than the noise in it.
At 64 the sample costs 64 of a 109-trial ceiling and the family has no budget left to
search with. **32 is my judgment call and is marked as such** [inferred, not cited — no
external standard prescribes it; Appendix C's closing caveat that no external body
publishes numeric validation thresholds applies here exactly as it does to §4.2]. I will
move it on a reasoned argument from Seat 9, the Director of Research, or the Devil's
Advocate **before** a family's Gate 0, and not after, for any reason including what the
number does to a result. That asymmetry is deliberate and it is the point.

---

## 3. SCOPE AND ADMISSIBILITY — ML-1 to ML-4

### ML-1 · What makes a family subject to this ruling

> **BINDING.** A hypothesis family is a **fitted family** and is subject to ML-1 through
> ML-27 if **any** number that enters a reported result is selected by comparing two or
> more candidates on a quantity computed from the sample.

Three consequences of writing it this way rather than by naming techniques.

- It **catches** a stepwise-selected linear regression, a LASSO whose λ is chosen on a
  validation split, a threshold picked off a ROC curve, and a "simple rule" whose lookback
  was chosen because 30 beat 20 and 60. None of these is called machine learning and all of
  them are the operation §4.1 prices.
- It **does not catch** ordinary parameter estimation. OLS coefficients under a declared
  specification, a covariance matrix, a rolling mean — these are unique minimizers of a
  declared objective, not selections among candidates. **Fitting parameters is not
  searching; selecting hyperparameters is.** The line is whether a candidate *set* existed
  and was compared.
- It cannot be evaded by declaring "we are not doing ML." The trigger is the operation, not
  the label. A sponsor who states that no selection occurred is making a checkable factual
  claim in a sealed document, and ML-2 requires them to make it explicitly rather than by
  silence.

**Boundary case, ruled so it is not argued later.** The ±50% parameter grid Charter §4.4
already requires of *every* family is a comparison of candidates on the sample. It does not
by itself make a family a fitted family, because the configuration that advances is the
plateau centroid, fixed by rule, not the grid's argmax [cited — §4.6]. **A family becomes a
fitted family the moment any selection is made at an argmax rather than by a declared
rule.** This is the same distinction §4.6 already draws and it is being applied one level
down.

### ML-2 · The ML declaration block is part of the sealed binding field set

> **BINDING.** Every fitted family's pre-registration carries an **ML declaration block**
> containing ML-5 through ML-11 in full. It is sealed with the pre-registration, hashed
> into `prereg_sha256`, and frozen thereafter under P3. **A Gate 0 intake with a missing or
> partial ML block is REJECTED, not deferred** — Charter §4.3 is binary and "a single
> failure is fatal at this stage, which is the cheapest stage to fail at" [cited].
>
> A family that asserts it is not a fitted family carries, in the same sealed block, the
> single sentence: *"No number reported by this family is selected by comparing candidates
> on a quantity computed from the sample."* **Silence is not that assertion.**

Mechanically: the block's content lives in the pre-registration document and its binding
summary — the declared space cardinality, the seed set, the CV construction, and the
selection objective — lives in the registry's binding fields (see ML-11 and §9).

### ML-3 · The ceiling arithmetic runs at intake, and its verdict is pre-committed here

> **BINDING.** At Gate 0, before any compute is spent, every fitted family computes and
> states:
>
> ```
> N_ceiling      =  n_inherited + n_declared_fits + trial_budget
> MinBTL_required =  min_backtest_length_years(N_ceiling, 1.0, ppy)
> span_available  =  measured calendar span of the in-sample period, in years
> ```
>
> **If `MinBTL_required > span_available`, the family is REJECTED for Gate 1 at intake and
> may be ADMITTED-AS-EXPLORATORY only. No result changes this. The failure is evidentiary
> length, not absence of edge, and it is not appealable to Validation — only to the
> Principal, in writing, as a §4.4 amendment made in advance of the evaluation.**

The Sharpe used is **1.0, the Gate 1 floor**, and not the family's hoped-for Sharpe. §2.2's
third reading is why: evaluating the ceiling at an optimistic Sharpe lets a family buy
search budget with a number it has not yet earned, and the direction of that error is
permissive. This mirrors PREREG-002 §10.4's own construction, which fixes the binding case
at "the Gate 1 Sharpe floor of 1.0, because a lower realized Sharpe demands a longer
history" [cited], and Ruling 001 §4.4's pre-committed verdict rule, which was stated before
its measurement existed for exactly this reason.

**The budget arithmetic a sponsor should do before proposing anything.** Against 6.571
years and a ceiling of 109 [measured, §2.2]:

| Obligation | Trials |
|---|---:|
| Dispersion sample (ML-16) | 32 |
| ±50% parameter surface grid, Charter §4.4 (ML-15) | 25 |
| Seed ensemble on the selected configuration (ML-24) | 10 |
| Walk-forward windows, Charter §4.4, **if not shared with the outer CV folds** (ML-21) | 10 |
| Benchmark / falsifier legs | 2–3 |
| **Remaining for genuine search** | **≈ 29–32** |

> **On the firm's best data surface, a fitted family may search roughly thirty
> configurations.** Not thirty thousand. Not three hundred. Thirty. Any proposal that
> requires more is a proposal for a family that cannot reach Gate 1 on this firm's data,
> and the correct time to learn that is at intake.

### ML-4 · What this forecloses, named at the top rather than discovered later

[inferred from §2.2 and `reference/CONSTRAINTS.md` §3.3]

| Line of work | Status |
|---|---|
| Neural networks, deep architectures, AutoML, large hyperparameter sweeps, architecture search | **Foreclosed at Gate 1 on every data surface this firm has.** Their declared spaces are ≥ 10³; at the Sharpe floor that needs ≥ 10.6 years and the firm's longest usable series is 6.571 |
| Cross-sectional fundamental ML on equities | **Already inadmissible**, and not on `N` grounds — no PIT fundamentals exist [cited — CONSTRAINTS §3.3]. `N` accounting does not rescue it and no ML method does |
| Fitted families on Polymarket | **Foreclosed by span before search.** PREREG-001's family is already at `MinBTL(31,250) = 17.06 years` against a venue with thin history [cited — PREREG-002 §7.3]. Adding a fitted layer moves the requirement up, never down |
| Small, declared, ≤ ~30-configuration fitted families on BTC/ETH daily crypto | **Admissible in principle**, subject to every clause below and to the harness work at §9 |

This is not a claim that ML does not work. It is a claim about **what this firm can
evidence with 6.571 years of daily data and a t-hurdle of 3.0**, and it follows from
Charter constants I did not choose and cannot move.

---

## 4. THE DECLARED SEARCH SPACE — ML-5 to ML-11

*Standing Order §1 element 1: "search space declared at Gate 0." The analogue of PREREG-002
§7.1's declared menu is the enumeration below; the analogue of §7.2's `N` contribution is
ML-13, and it resolves differently, for the reason given at §1(1).*

Each clause states what must be declared and **what it contributes to the cardinality
product**. The product is `|Θ|`, computed and shown at ML-11.

### ML-5 · Estimator classes

> **BINDING.** Every estimator class the procedure may fit, enumerated exhaustively by
> library, fully-qualified class name, and **pinned version**. "Gradient boosting" is not a
> declaration. `sklearn.ensemble.HistGradientBoostingRegressor @ 1.5.2` is.
>
> **Contribution:** the number of distinct classes enumerated, if the procedure selects
> among them on the sample; 1 if a single class is declared.

Version pinning is not pedantry. A default that changes between minor versions silently
changes the configuration, and Seat 9's standing obligation is that "every backtest result
must be regenerable from a commit hash plus a config" [cited — Charter Seat 9]. An
unpinned estimator makes that guarantee false.

### ML-6 · The hyperparameter space, and the continuous case

> **BINDING.** Every hyperparameter, its type, and its candidate set. **A hyperparameter
> with a continuous domain has no menu size and must be reduced to a finite, declared
> count at sealing**, by exactly one of:
>
> | Declaration form | Contribution |
> |---|---:|
> | **(a)** Explicit finite grid — values enumerated in the sealed text | number of points |
> | **(b)** Random search over a declared distribution with a declared `n_draws`, under a declared seed | `n_draws` |
> | **(c)** Sequential/adaptive optimizer (Bayesian, TPE, CMA-ES, Hyperband, gradient-based) with a declared **iteration budget** | the iteration budget |
> | **(d)** A single value, fixed at sealing and not searched | 1 |
> | **(e)** Anything else — an unbounded range, an open-ended optimizer, "until it converges", "until it stops improving" | **INADMISSIBLE at Gate 0** |
>
> **Contribution to `|Θ|`:** the product across hyperparameters.

**Why (c) is charged its full budget rather than some "effective" number.** Every iteration
of an adaptive optimizer evaluates a candidate against the sample, and the *next* proposal
is a function of that evaluation. Every iteration is therefore a look, and the sequence of
looks is what selected the winner. An "effective" count would require modelling the
optimizer's exploration, which is unmeasurable here, unverifiable by anyone, and would be
supplied by the party it benefits. **The declared budget is the only reconstructable count,
and it is conservative — which is the direction D-009 records as correct** [cited].

**Why (e) is inadmissible rather than INSUFFICIENT-DATA.** Charter §4.3 is binary at
intake. An unbounded search has an `N` that is not merely unknown but **undefined**, so
`MinBTL`, DSR and PBO are uncomputable rather than merely uncertain. Admitting it and
failing it later spends compute to learn something knowable for free at intake.

### ML-7 · The feature set, and feature selection as a search

> **BINDING.** Every feature: its formula, the field it is computed from, that field's
> `knowledge_time` source, its lag, and its **lookback window length in bars** (which
> ML-18's embargo consumes and which is therefore not optional).
>
> **Feature selection performed on the sample is a search and is charged.** Selecting `k`
> of `p` candidate features has cardinality `C(p, k)` unless the selection is fully
> re-performed inside a nested inner loop under ML-14, in which case it contributes 1.
> Where the selector is sequential (forward/backward stepwise, recursive elimination), the
> cardinality is the number of candidate evaluations the procedure performs, which for
> forward selection to `k` features from `p` is `Σ_{i=0}^{k−1} (p − i)`.

Feature selection is, in my judgment, **the largest hidden `N` in applied financial ML**
[inferred, not cited]. Choosing 5 features from 40 is `C(40,5) = 658,008` — a number that
on §2.2's table needs about 17 years at the Sharpe floor. A sponsor who wants a
40-candidate feature pool must either declare the whole pool as fixed (contribution 1) or
nest the selection (ML-14) or accept that the family is arithmetically dead. **Naming this
at Gate 0 is the difference between a two-line intake rejection and a spent sprint.**

### ML-8 · Preprocessing, and the fit-on-train-only requirement

> **BINDING.** Every preprocessing step — scaling, centering, winsorization, imputation,
> stationarity transform, dimensionality reduction, cross-sectional normalization — with,
> for each, an explicit statement of **whether it holds fitted state and, if so, that the
> state is fit on training data only, inside each CV fold, and never on the full sample.**
>
> A preprocessing step with fitted state that is fit on the full sample is a **leakage
> defect, not a trial-count question**, and fails Gate 1 on the leakage audit (ML-25).
> Where a preprocessing choice is *selected* on the sample (which scaler, which transform),
> it is a hyperparameter and is charged under ML-6.

This is the single most common leak in applied ML and it is invisible in results: a
`StandardScaler` fit before the split leaks the test period's mean and variance into
training, and the leak flatters. It is listed as its own clause rather than folded into the
leakage audit because it must be **declared at Gate 0**, where it is cheap to catch.

### ML-9 · Target construction and the label span

> **BINDING.** The label: its horizon, its transformation (raw forward return, sign,
> vol-scaled, triple-barrier, ranked), its sample weighting, and — stated as an integer
> number of bars — its **realization span `L`**: the number of bars over which the label
> becomes fully known.
>
> `L` is not optional and is not a footnote. It sets the purge width (ML-18), it bounds the
> effective sample size (ML-26), and a family that cannot state it cannot construct a purged
> split at all. **A missing `L` is a Gate 0 rejection.**
>
> Where the target construction is itself selected on the sample (comparing a sign label
> against a triple-barrier label), it is charged under ML-6 at its candidate count.

### ML-10 · The selection objective and the stopping rule

> **BINDING.** Declared at sealing:
>
> - **The single scalar objective** the search maximizes, and the **tie-break rule**.
>   "Which metric did you select on" is itself a choice with a menu, and a procedure that
>   selects on accuracy, then reports Sharpe, has searched a space this ruling would
>   otherwise not see.
> - **The stopping rule.** Early stopping is a selection over the number of training
>   rounds: its cardinality is `⌈max_rounds / eval_period⌉` unless the stopping is
>   performed inside a nested inner loop under ML-14. Patience, the monitored quantity,
>   and the data it is monitored on are all declared.
> - **The refit rule**: whether the final object is refit on the full training set after
>   selection, and on what.

### ML-11 · `n_declared_fits` — the sealed integer

> **BINDING.** The ML block computes and states the cardinality product explicitly, one
> line per dimension, exactly as PREREG-002 §7.1 does for its conditioning menus:
>
> ```
> |Θ|  =  (estimator classes) × (Π hyperparameter cardinalities)
>         × (feature-selection cardinality) × (preprocessing-choice cardinality)
>         × (target-construction cardinality) × (stopping cardinality)
>         × (number of distinct procedures compared)
>         × (number of independent re-runs of the whole procedure)
> ```
>
> with **each factor reduced to 1 wherever ML-14's nested exemption is claimed and its four
> conditions are met and stated.**
>
> **`n_declared_fits` = `|Θ|` minus the number of Θ-members that will be run through
> `run_backtest` and therefore logged.** It is the count of configurations evaluated
> against data **without** a logged return series, so that
> `n_inherited + n_declared_fits + n_logged` counts each configuration exactly once.
>
> **`n_declared_fits` is a binding, sealed registry field. It does not exist in the
> harness.** See §9 and I-052. Until it does, ML-3's arithmetic is computed and reported
> but not enforced, and the consequence at §1 applies: **exploratory only, no Gate 1.**

**On why this is a ceiling and not an estimate.** `n_declared_fits` is sealed at Gate 0 and
frozen under P3 [measured — `registry.py:350–370`]. A family that evaluates more
configurations than it declared has amended a binding field, which the registry refuses;
the sanctioned continuation is a successor family under ML-17. **Under-declaring is
therefore the only available cheat, it flatters, and it is not mechanically detectable.**
§8 states that limit plainly rather than burying it.

---

## 5. TRIAL ACCOUNTING — ML-12 to ML-17

*Standing Order §1 element 2: "every fitted configuration a logged trial." I adopt the
intent and sharpen the instrument, because "logged" and "counted" must be distinguished or
the rule is either unimplementable or statistically wrong — see ML-15.*

### ML-12 · What a configuration is

> **BINDING.** A **configuration** is the complete tuple of every value that (i) could have
> been chosen differently, (ii) is fixed before a fit begins, and (iii) can change the
> reported result. It comprises, at minimum: the estimator class, every hyperparameter
> value, the feature set, every preprocessing choice and its parameters, the target
> construction, the sample weighting, the CV scheme, the selection objective, the stopping
> rule, and **the seed**.
>
> **A configuration evaluated on `K` cross-validation folds is one configuration, not `K`**,
> when the `K` fold scores are aggregated into one score by a declared rule and the
> selection operates on that aggregate. **It is `K` configurations if any fold-level
> quantity is selected, reported, or compared** — reporting the best fold is a selection
> over `K`.

The third element of the definition is what makes it un-gameable by re-labelling. A
quantity is part of the configuration if changing it changes the result; whether the
sponsor calls it a hyperparameter, an implementation detail, or "part of the estimator" is
not relevant and is not a defence.

### ML-13 · The counting rule, and why §7.2's discount does not apply

> **BINDING.** The trial count contributed by a candidate set is its **cardinality**, and
> cardinalities across independent choice dimensions **multiply**, exactly as PREREG-002
> §7.3's counterfactual multiplies its menu sizes [cited].
>
> **The pre-commitment discount — menu size reduced to 1 — is available if and only if the
> selection is fully determined at sealing by facts stated in the sealed document, without
> reference to any quantity computed from the sample.** A selection made by a fitting
> procedure is, by construction, made by reference to a quantity computed from the sample.
> **No fitting search ever receives the discount.**

This is an extension of PREREG-002 §7.2, not an exception to it, and the distinction
matters because the alternative reading would be catastrophic. §7.2's own justification
reads: *"A choice made before any measurement, from a menu declared in the sealed
pre-registration, and binding thereafter, involves no search over results and contributes
1, not the menu size"* [cited]. Every one of the three conditions — before any measurement,
binding thereafter, no search over results — fails for a hyperparameter search. **A reading
that let an ML family declare a 10,000-point grid at Gate 0 and charge 1 for it would
convert the firm's strongest control into its largest hole, and it would do so while
appearing to comply with the Principal's rider.** It is foreclosed here explicitly so it
cannot be argued for later on the surface similarity of the two declarations.

**The symmetric point, stated so this is not read as one-sided:** the declaration still
buys the family something real. It converts an *unbounded* search into a *bounded* one,
makes the bound checkable, and makes exceeding it an amendment rather than a silent event.
That is worth having. It is just not worth a factor of `|Θ|`.

### ML-14 · The nested exemption — the one place the count legitimately falls

> **BINDING.** A candidate set contributes **1** rather than its cardinality if and only if
> **all four** of the following hold and are stated in the sealed ML block:
>
> **(N1)** The selection is performed **entirely inside each outer training fold**, on data
> disjoint from that fold's test set, and is **re-performed independently for every outer
> fold**.
> **(N2)** The inner split is itself **purged and embargoed** to ML-18's construction.
> **(N3)** The **only** quantity reported from the procedure is the outer-fold aggregate.
> No inner-loop quantity — not the winning hyperparameters, not an inner score, not a
> per-fold model — is reported, compared, or carried forward except through ML-20's rule.
> **(N4)** The **procedure itself**, including the search space, was fixed at sealing and
> was **not** selected by comparing outer-loop results across procedures. Every distinct
> procedure whose outer-loop result was seen contributes its own factor under ML-13.

**Why the exemption is real and not a courtesy.** In correct nested CV the inner search is
part of the estimator, and the outer estimate is an honest estimate *of the entire
procedure including its search*. The selection is inside the thing being measured. That is
the genuine statistical content of the construction and it is the one direction in which
"the effective number of trials is not the number of fits" cuts **downward** honestly.

**Why (N4) is the condition that will actually be violated.** Nested CV protects against
the inner search. It protects against nothing at the level of the researcher who runs it,
reads the outer number, widens the search space, and runs it again. **That loop is a search
over procedures, it is invisible to the harness, and each pass through it multiplies `N`.**
A sponsor claiming ML-14 must state, in the sealed text, that the procedure is fixed and
that a re-run after seeing an outer result opens a successor family under ML-17. Without
(N4) the exemption launders exactly the search it appears to control.

### ML-15 · Counted versus logged — and the reconciliation with `run_parameter_grid`

> **BINDING.** Two kinds of trial exist and both increment `N`:
>
> | | Contributes to `N` | Has a return series | Contributes to σ_SR | Contributes to PBO |
> |---|---|---|---|---|
> | **Logged trial** — a `run_backtest` call | yes, via `n_logged` | yes | **yes** | **yes** |
> | **Counted trial** — a fit inside a declared procedure | yes, via `n_declared_fits` | no | no | no |
>
> **`run_parameter_grid`'s convention is preserved without amendment: every point of a
> strategy-parameter grid is a logged trial with a full return series** [cited —
> `grid.py` module docstring, "a 25-point grid is 25 trials, and that is the honest
> accounting the DSR then pays for"]. This ruling **extends** that convention to fit-level
> candidate sets, which cannot each carry a return series, by giving them a counted trial.
> It does not weaken it and it does not create a second path to a number: **a counted trial
> produces no number at all.** Amendment A2 is untouched — every *reported* quantity still
> comes from `run_backtest`.
>
> **A family may not convert logged trials into counted trials.** The dispersion sample
> (ML-16) and the §4.4 parameter grid are logged, always, and are not satisfiable by
> declaration.

**Enumerated evasions, each ruled, so none is available as a first-time argument:**

| Evasion | Ruling |
|---|---|
| "The inner `GridSearchCV` is part of the pipeline, so it is one estimator" | Counted at full evaluated cardinality unless all four of ML-14 hold |
| "Early stopping is not a hyperparameter" | Counted at `⌈max_rounds / eval_period⌉` (ML-10) |
| "The LASSO path is one fit" | Counted at path length when λ is selected on a score |
| "Boosting rounds are chosen automatically" | Automatic selection is selection. Counted |
| "We ensembled instead of selecting" | An **unweighted average over the full declared set** is one configuration — no selection occurred. A **weighted average whose weights are fit on the sample** is a selection over the full set and is counted at cardinality |
| "We threw those models away" | House rule 3, verbatim: *"Every backtest run — exploratory, abandoned, or otherwise — increments the trial counter"* [cited]. Abandoned fits count |
| "We only report one configuration" | `N` is the cardinality of the candidate set, never of the reported set. This is §4.1's entire content |
| "We re-ran it with the bug fixed" | A re-run of the whole procedure after seeing a result multiplies under ML-13(N4) and opens a successor under ML-17 |
| "We searched in a scratch script, then declared a space of size 1 and ran that once" | Foreclosed by Charter §4.4's own parameter-surface criterion — see below — and, beyond that, undetectable. §8 |

**The size-one declaration is closed by an existing criterion and I want that on the
record**, because it is cheaper than anything I could invent. Charter §4.4 requires a ±50%
parameter grid around the chosen configuration with **≥ 60% of points net-profitable**
[cited]. A declared space of size 1 has no grid, so the criterion is INSUFFICIENT-DATA and
the Gate fails. **The grid must be a subset of the declared space** — a grid over
parameters the family did not declare is a search the family did not declare — and its
points are logged trials.

### ML-16 · The dispersion sample — the clause that makes DSR work

> **BINDING.** Every fitted family runs a **dispersion sample**: `m ≥ min(|Θ|, 32)`
> configurations **drawn uniformly at random from the declared space Θ under the declared
> seed (ML-22), before any selection is performed**, each executed end-to-end through
> `run_backtest` on the full in-sample index, each a logged trial with a full return series.
>
> **The dispersion sample runs first**, before the local ±50% grid and before any seed
> replication, and the order is part of the declared method.
>
> The Validation Report states, as a disclosure line: `m`, the draw seed, `σ_SR` computed
> over the dispersion sample alone, and `σ_SR` as the harness computes it over all logged
> trials.

**Why this is the load-bearing clause.** §2.3 shows σ_SR is roughly three times more
influential than `N` over the ranges an ML family occupies. `family_stats.sr_period_std`
takes the standard deviation over **every** logged trial in the family [measured —
`registry.py:541–547`]. A family that logs 25 tightly-clustered grid points around its
winner plus 10 seed replicates gets a σ_SR describing **local** dispersion around the
optimum, which is systematically smaller than dispersion across the space actually
searched. **That understates `E[max SR]`, understates the deflation, and flatters DSR — and
it does so through a mechanism no criterion currently inspects.** A uniform pre-selection
draw is the only estimator of σ_SR that describes the space the search ran over.

**The harness limitation, stated rather than assumed away.** `evaluate_gate1` computes DSR
from `fam.sr_period_std` over all logged trials; it has no notion of a designated
dispersion subset [measured — `gates.py:265–268`]. Until it does (§9, I-052):

> **For a fitted family, if `σ_SR(dispersion sample) > σ_SR(all logged trials)`, the DSR the
> harness reports is optimistic, and the DSR criterion is INSUFFICIENT-DATA — which is not
> PASS, and one non-PASS fails the Gate.** I will not substitute a hand-computed DSR: that
> would be a narrated number inside the firm's most important criterion, which A1 forbids
> and which I-014 records the firm having already been bitten by once.

### ML-17 · Exceeding the declared space opens a successor family

> **BINDING.** Evaluating any configuration outside the sealed Θ, or exceeding
> `n_declared_fits`, is an amendment to a frozen binding field. P3 refuses it and logs
> `hypothesis_amendment_refused` [measured — `registry.py:356–369`]. The sanctioned
> continuation is a **successor family** under `predecessor_family`, opened with
>
> ```
> n_inherited  ≥  (cardinality of the enlarged dimension)  ×  (this family's final n_trials)
> ```
>
> and the product of the cardinalities where more than one dimension is enlarged. This is
> PREREG-002 §7.2's escalation rule applied to the fitting space, deliberately and without
> softening: **a researcher who intends to revise pays the full price with interest; a
> researcher who does not, pays nothing** [cited].

> **⚠ This clause is currently unexecutable against `book/registry.db`, and so is
> PREREG-002 §7.2's own escalation rule.** `open_hypothesis` raises
> `InheritedCountDoubleCountError` whenever a successor declares
> `n_inherited ≥ chain_total` [measured — `registry.py:294–308`]. The escalation formula
> above produces `n_inherited ≥ cardinality × chain_total`, which exceeds `chain_total`
> whenever the cardinality is ≥ 2 — i.e. **always**. The guard is correct to raise: its
> docstring states that "a genuine new search larger than the entire predecessor chain is a
> Validation escalation, not a silent registration — this exception IS that escalation
> path" [cited]. **But the escalation path terminates in a dead end: there is no argument,
> event, or authorized route by which Validation can then permit the registration.** Filed
> as **I-053**. The design is right and the continuation is missing.

---

## 6. PURGED AND NESTED CROSS-VALIDATION — ML-18 to ML-21

*Standing Order §1 element 3: "purged/nested CV mandatory." Charter §4.4 already requires
"purged k-fold with 1% embargo applied" of every family [cited]. This section specifies the
construction for a fitted family and reports two defects in the splitters that ship.*

### ML-18 · The outer construction, and the embargo is a floor rather than a target

> **BINDING.** The outer loop is **purged K-fold with embargo, K ≥ 5**, or combinatorial
> purged CV. Its parameters:
>
> ```
> purge_width  =  L                                   # the label span, ML-9
> embargo      =  max( ⌈EMBARGO_FRACTION · T⌉ ,  max feature lookback ,  L )
> ```
>
> **`EMBARGO_FRACTION = 0.01` is a Charter constant and is a FLOOR, not a target.** It is
> not moved by this clause — it cannot be, it is §4.2 — and nothing here relaxes it. What is
> added is a data-driven addend that is already implied by what an embargo is for.

**The defect this closes, measured.** `purged_kfold_splits` purges `label_span` bars before
the test fold and embargoes `⌈n_samples · embargo_fraction⌉` bars after it [measured —
`cv.py:28–40`]. The left purge is correct: a training observation at `t < t0` with a label
realized over `L` bars overlaps the test window iff `t ≥ t0 − L`. **The right side is
where it fails.** A training observation at `t > t1 + embargo` whose *features* are computed
on a trailing window of length `W` reads data from `[t − W, t]`; if `W > embargo`, that
window reaches back inside the test fold. On a 2,398-bar sample, `⌈0.01 · 2398⌉ = 24 bars`
[measured]. **A 30-bar trailing feature — the exact lookback PREREG-002 §7.1 K1 declares
for its own state variable [cited] — exceeds it, and the training set then contains
information from the test fold.**

To be precise about what that example is and is not: **PREREG-002 is not a fitted family
and does not fit anything on a purged fold, so nothing in its design is impugned.** It is
cited because it is the firm's own live evidence that a 30-bar lookback against a 24-bar
embargo is the realistic case rather than a constructed one. The leak bites when something
is *fit* on the training indices, which is precisely the ML case.

**The splitter cannot express this today** — it has no `feature_lookback` argument. A caller
may achieve it by passing an inflated `embargo_fraction`, which is arithmetic the caller
must do correctly and silently every time. Filed as **I-051**. Until the splitter takes the
parameter, the fitted family computes the required fraction, states it in the sealed method,
and Validation checks the arithmetic at Gate 1.

### ML-19 · The nested inner loop

> **BINDING.** Where ML-14's exemption is claimed, the inner loop runs **inside each outer
> training fold**, is itself purged at `L` and embargoed to ML-18's rule, uses `k ≥ 3`
> inner folds, and is **re-fit independently for every outer fold**. The inner loop never
> touches the outer test fold, and never touches the holdout, in any fold, at any depth.

### ML-20 · What advances is the modal configuration, not the best fold

> **BINDING.** When the inner loop selects a different configuration in different outer
> folds, the configuration carried forward is the one **most frequently selected across
> outer folds** (the modal selection), with ties broken by ML-10's declared tie-break rule.
> **The configuration belonging to the best-performing outer fold is reported alongside it
> and never advances.** The report states both and the count of folds selecting each.

This is Charter §4.6 — *"prefer the plateau centroid to the argmax; selecting the peak of a
parameter surface is the overfitting operation"* [cited] — applied at the configuration
level, which is the level an ML family actually has. It is the same instrument
`run_parameter_grid` already implements as `plateau_centroid_params` versus
`argmax_params`, and it carries the same diagnostic: **the disagreement between the modal
and the argmax configuration is itself the overfitting measurement.** A procedure whose
outer folds each select a different configuration has not found a plateau; it has found
noise, and the report must say so.

### ML-21 · Interaction with the 25% holdout, and the tension named

> **BINDING.**
>
> **(a)** The holdout `[C, G]` is **not a fold, at any depth.** No outer fold, no inner
> fold, no purge window, no embargo window, and no dispersion draw may include a bar from
> it. It is acquired once, by me, at Gate 1, with the Principal's passphrase supplied at
> that moment [cited — Ruling 001 §2.3 D3].
>
> **(b)** The outer-loop aggregate is **not the Gate 1 out-of-sample number.** It is an
> in-sample estimate produced inside `[start, C]`, and `evaluate_gate1`'s
> `oos_net_returns` is the holdout. The outer aggregate is reported as the in-sample
> figure, and the ratio of holdout to outer aggregate is reported alongside WFE as a
> shrinkage diagnostic.
>
> **(c)** The walk-forward windows Charter §4.4 requires (≥ 10, WFE ≥ 0.50) **may be the
> outer folds of a sequential, non-shuffled purged CV**, in which case the fits are
> performed and counted once, not twice. A family electing this states it at sealing.

**The tension, stated explicitly because the dispatch asks for it and because it is real.**
Nested CV produces something that looks like an out-of-sample number and is not one in the
sense Gate 1 means. Two failure modes follow, and they run in opposite directions:

- **The permissive one.** A sponsor iterates procedures against the outer-loop estimate
  until it looks good. Every pass is a search over procedures (ML-14 N4), the outer
  estimate becomes an in-sample surface, and the holdout becomes the only genuinely
  uncontaminated data the family has. This is the more likely failure and (b) is what
  prevents the resulting number being presented as OOS.
- **The restrictive one.** Treating the outer aggregate as OOS and the holdout as
  confirmatory would double-count the same evidence and, worse, would create pressure to
  open the holdout early "to check." Ruling 001's whole design exists to prevent that and
  (a) restates it at the fold level, where an ML procedure is most likely to reach for
  data without noticing.

**And (c) is a genuine simplification, not a concession.** Walk-forward *is* purged CV with
sequential expanding folds; running both constructions separately would double the fits and
the trial count for no additional evidence. Against a ceiling of 109 [measured, §2.2] that
saving is roughly 10% of the family's entire budget.

### 6.1 The second splitter defect — `walk_forward_windows` applies no purge and no embargo

> **[measured — `cv.py:43–61`]** `walk_forward_windows` yields `idx[: fold[0]]` as the
> training set: **every bar strictly before the test fold, with no purge and no embargo of
> any width.** The function takes neither a `label_span` nor an `embargo_fraction`
> argument. There is nothing to configure.

Charter §4.4 requires purged k-fold with a 1% embargo **and** WFE across ≥ 10 windows
[cited]. The harness satisfies the first through `purged_kfold_splits` and the second
through a splitter that satisfies neither. For a family that **fits** on the training
indices, the last `L` training bars carry labels realized inside the test fold, and a
trailing feature of width `W` reads into it — the model is trained on the answer and the
error runs in the **permissive** direction, since it raises the out-of-sample leg of the
ratio and therefore raises WFE.

It has never fired: the firm holds zero families and zero trials [measured], and for a
family that fits nothing the splitter is a slicing convenience with no training step to
contaminate. **It would fire on the first fitted family.** Filed with the ML-18 embargo gap
as **I-051**. **Until it is repaired, `walk_forward_windows` may not be used by a fitted
family**, and a fitted family's WFE windows must come from ML-21(c)'s sequential purged
construction.

---

## 7. SEEDS — ML-22 to ML-24

*Standing Order §1 element 4: "seeds fixed." Three questions are named in the dispatch —
where recorded, what happens when a result is seed-sensitive, and whether seed variation is
itself a trial. All three are answered, and the third is answered in the affirmative
without qualification.*

### ML-22 · Enumeration and where recorded

> **BINDING.** Every stochastic component's seed is enumerated in the sealed ML block and
> **repeated in the `config` dict passed to `run_backtest`**, which hashes it into the
> trial's identity [measured — `registry.py:69–72`, `engine.py:236–247`].
>
> The enumeration covers, at minimum: weight initialization; dropout and any stochastic
> regularizer; bootstrap, bagging and subsampling; feature subsampling; random-search draws
> (ML-6(b)); the dispersion-sample draw (ML-16); any data shuffling — **which for a time
> series should be none, and a declared shuffle is a leakage defect, not a seed**; and the
> interpreter-level determinism controls (`PYTHONHASHSEED`, and the framework's
> deterministic-algorithm switch where one exists).
>
> **A trial whose `config` omits its seeds is not regenerable from a commit hash plus a
> config, which is Seat 9's standing guarantee [cited — Charter Seat 9]. It is inadmissible
> and I will return a report resting on one.**

**Noted, not filed:** `probability_backtest_overfitting` samples 3,000 of the
`C(16,8) = 12,870` CSCV combinations under a hard-coded `seed=7` [measured —
`stats.py:149–187`]. That is deterministic and therefore adequate, but it means **PBO is
itself a function of a seed**, and the Validation Report should say so. This is a reporting
gap, not a defect, and does not warrant an Issue Log entry.

### ML-23 · Seed variation is a trial. Without qualification.

> **BINDING.** Re-running a configuration under a different seed produces a different
> configuration (ML-12) and a different trial. Each such run through `run_backtest` is a
> logged trial and increments `N`. **Reporting the better of two seeds is selection over a
> candidate set of size two and is the purest instance of the operation Charter §4.1
> prices.**

**I decline the exception that would make this cheaper, and I want the refusal on the
record with its reason.** A defensible argument exists that a seed ensemble whose members
are *averaged* rather than selected among involves no search, and should therefore
contribute 1 rather than `S`. The argument is correct in principle — it is the same
principle ML-15 applies to unweighted ensembles. I refuse it anyway, because implementing
it requires a "this run does not count" flag on `run_backtest`, and **a flag that exempts a
run from the trial counter is precisely the mechanism by which a trial registry stops being
one.** House rule 3 admits no exceptions and Appendix B #2 names lost trial counts as
failure mode two. The cost of the refusal is `S − 1` trials of over-charging per
configuration, in the conservative direction, which D-009 records as the correct direction
to err [cited]. **The cost is real and I am paying it deliberately rather than opening the
door.**

### ML-24 · Seed sensitivity — what is measured, what is reported, what fails

> **BINDING.** The selected configuration is run under **`S ≥ 10` declared seeds**, each a
> logged trial. The report carries `SR_seed_mean`, `SR_seed_std`, `SR_seed_min`,
> `SR_seed_max`, and the fraction of the ensemble that is net-profitable.
>
> **(a) The reported result is the across-seed mean. Never a single seed's draw.** Every
> Gate 1 criterion computed on the family's returns is computed on the across-seed mean
> return series.
>
> **(b) The ensemble must clear ≥ 60% net-profitable.** A configuration that is
> net-profitable on fewer than 60% of its seeds is a seed, not a strategy.

**Both numbers are imported, not invented, and that is deliberate.** `S ≥ 10` is Charter
§4.4's own `≥ 10 walk-forward windows`. The 60% floor is Charter §4.4's own parameter-
surface criterion — *"plateau not spike; ≥ 60% of the ±50% grid net-profitable"* [cited] —
applied to the axis a fitted family actually has. **The seed is a parameter of the fitted
object, and a fitted object that survives only on some seeds is a spike on the seed axis.**
This is the same move Ruling 002 R4(b) made in applying `PUBLISHED_SIGNAL_HAIRCUT` to a
case the Charter did not anticipate: **an existing constant applied to a new surface is not
a new threshold, and I have no authority to set a new threshold and have not set one.**

---

## 8. THE FIFTH ELEMENT — ML-25 to ML-27

*The Standing Order names four elements and calls them a floor. The ruling does not bind
without this one: the standing leakage audit has eight questions and none of them catches
the way a fitted family leaks, and the firm's headline statistic assumes something a fitted
family's return series routinely violates.*

### ML-25 · The leakage audit gains eight questions for fitted families

> **BINDING.** In addition to the eight standing leakage-audit questions, every fitted
> family's Validation Report answers, on its face:
>
> **L1** — Does any preprocessing step with fitted state (scaler, imputer, PCA,
> winsorization bounds, quantile transform) hold state fit outside the training fold?
> **L2** — Is any cross-sectional normalization computed over a panel that includes dates
> after the decision time?
> **L3** — Is any feature computed on a centered or two-sided window?
> **L4** — Do labels overlap across observations (`L > 1` bar), and if so is the purge
> width `≥ L` on the training side of every fold?
> **L5** — Does any sample weight use information from after the observation's decision
> time? *(Uniqueness/overlap weights are computed from the label geometry and are
> admissible; weights computed from realized return magnitude over the full sample are
> not.)*
> **L6** — Was the universe or the feature pool assembled by a screen applied to the full
> sample?
> **L7** — Was any hyperparameter default inherited from a library version that postdates
> the sample, or from published work fitted on it?
> **L8** — Was the dispersion sample (ML-16) drawn before or after any selection was
> performed?
>
> **Any unanswered question is INSUFFICIENT-DATA on the leakage criterion, which is not
> PASS.**

**L1 is the one that will actually bite.** A scaler fit before the split leaks the test
period's mean and variance into training. It produces no error, no warning, and no
artifact; it improves the result; and it is the default behaviour of every common pipeline
idiom written outside a `Pipeline` object. It is listed first because it is the most likely
single cause of a fitted family reaching me with a number that does not survive.

### ML-26 · Overlapping labels, effective sample size, and an inflated `t`

> **BINDING.** Where a fitted family's label span `L > 1` bar, or where the strategy's net
> return series is materially autocorrelated, **the t-statistic reported against
> `T_STAT_HURDLE = 3.0` must be computed with a Newey–West correction at a lag truncation
> of at least `L − 1`**, or on non-overlapping returns. The raw `SR_period · √T` figure is
> reported alongside it, labelled as uncorrected.

**The defect, stated at its real scope.** `stats.sr_tstat` computes `SR_period · √T`
[measured — `stats.py:51–60`]. That estimator assumes the return series is serially
independent. Under first-order autocorrelation `ρ`, the variance of the mean is inflated by
approximately `(1+ρ)/(1−ρ)`, so the true `t` is smaller than the reported one by
`√((1−ρ)/(1+ρ))`.

The firm already holds a measured instance of the assumption failing badly. Ruling 003 §3.2
records daily funding autocorrelation of **0.829 (BTC), 0.802 (ETH), 0.493 (SOL)**
[cited — Ruling 003, tagged measured there]. At `ρ = 0.829` the inflation factor is
`√(1.829/0.171) = 3.27`. **A pure carry return stream would report a t-statistic roughly
3.3× larger than its serially-corrected value, against a hurdle that is the firm's single
most-cited number.**

Two honest qualifications, so this is not overstated:

1. A net return series is `gross + carry − costs`, and the price-return component is close
   to serially independent, so a real family's inflation factor is **between 1 and 3.3**,
   not at the ceiling. The magnitude is family-specific and unmeasured.
2. The naive claim "overlapping holding periods imply an inflated `t`" is **too strong**. A
   slowly-varying weight applied to serially independent asset returns produces a nearly
   independent return series. What inflates `t` is autocorrelation **of the return series**,
   which arises from a persistent P&L component — carry, funding, and multi-bar labels —
   not from holding-period overlap as such.

**Neither qualification changes the direction, and the direction is permissive.** Ruling 003
§6.5 already required Newey–West for F-002's `t(α)` on exactly this reasoning [cited], but
the **Gate 1 t-stat criterion still uses the uncorrected estimator for every family**.
Filed as **I-050, HIGH**.

**This is not a Charter amendment and I am not requesting one.** `T_STAT_HURDLE = 3.0` does
not move. What changes is the **estimator of `t`**, which is being corrected to match the
assumption it already claims. Correcting an estimator to its own stated assumption falls
under Seat 3's ownership of "the backtest harness's statistical correctness" [cited —
Charter Seat 3] and under no one else's.

### ML-27 · The published-architecture haircut

> **BINDING.** Ruling 002 R4(b) makes a hypothesis generated from an LLM seat's priors
> presumptively an edge derived from published research, carrying
> `PUBLISHED_SIGNAL_HAIRCUT = 0.50` unless the sponsor argues otherwise at Gate 0 and
> Validation accepts [cited]. **It extends to fitted families at the level of the
> architecture, the feature set, and the hyperparameter neighbourhood**, and not merely the
> hypothesis statement.
>
> A sponsor who proposes triple-barrier labels with meta-labelling, purged CV, and feature
> importance by MDA is proposing a well-documented published pipeline arriving through a
> model's priors. The haircut applies to the resulting edge. Rebuttable at Gate 0, on
> argument, before any result exists — never after.

### 8.1 The residual weakness, named plainly

**A researcher who runs the search outside the harness, finds the winner, and then declares
a small space containing it defeats every clause above and leaves no trace.**

This is not closable under this firm's constraints, it is the ML instance of Ruling 001
§2.4's residual, and I am not going to bury it. Three things bound it, and I state each
one's limit:

1. **The seal is prior to the result.** `n_declared_fits` is frozen at Gate 0 under P3, so
   the declaration cannot be adjusted after a number exists. This protects against the
   *retroactive* version and does nothing against a search conducted before sealing.
2. **§4.4's parameter-surface criterion forecloses the size-one declaration** (ML-15) and
   ML-16's dispersion sample forecloses logging only survivors. Both catch the careless
   case, which is the common case. Neither catches a deliberate one.
3. **The direction of the incentive is known and is the wrong way.** Under-declaring
   flatters, because §2.2's ceiling makes a large declaration lethal. **The clause that
   makes the family honest is also the clause that makes dishonesty profitable, and no
   control in this ruling changes that.**

**Therefore, for the record and for the Principal:** the declared search space is a
**self-report**. It cannot be verified against what a seat actually ran. This ruling makes
the declaration binding, sealed, checkable for internal consistency, and expensive to
revise. It is a control against accident and a generator of audit trail. **It is not a
control against intent, and any document describing it as one is wrong.**

---

## 9. HARNESS CAPABILITY REQUIRED — named, not assumed

The dispatch requires that where a clause needs capability that does not exist, I name the
capability and file it rather than assume it. Four capabilities are named. **None is
invented for this ruling's convenience; each is the mechanism by which an already-stated
clause becomes enforceable rather than advisory.**

| # | Capability | Blocks | Issue |
|---|---|---|---|
| **H-A** | `n_declared_fits` — an integer column on `hypotheses`, in `_BINDING_FIELDS`, summed transitively by `family_stats`, and added to `FamilyStats.n_trials` alongside `n_inherited` and `n_logged`. Rendered on the report's face as its own component, never merged into either existing one | ML-11, ML-3's enforcement, and therefore **Gate 1 eligibility for every fitted family** | **I-052** |
| **H-B** | A designated **dispersion subset** of logged trials, from which `sr_period_std` is computed for DSR, distinct from the full logged set | ML-16's DSR enforcement — without it the DSR criterion is INSUFFICIENT-DATA for fitted families | **I-052** |
| **H-C** | `purged_kfold_splits(feature_lookback=…)`, refusing to split when it is not stated; and `walk_forward_windows(label_span=…, embargo_fraction=…)` applying both | ML-18, ML-21(c), and §6.1's prohibition on `walk_forward_windows` for fitted families | **I-051** |
| **H-D** | A Newey–West option on `sr_tstat`, and its use by `evaluate_gate1`'s t-stat criterion where the family declares `L > 1` or measured autocorrelation | ML-26 | **I-050** |
| **H-E** | A sanctioned continuation for `InheritedCountDoubleCountError` — an explicit Validation-authorized route to register a successor whose `n_inherited` exceeds its chain total | ML-17, **and PREREG-002 §7.2's own escalation rule, which is equally unexecutable today** | **I-053** |

**I am not implementing any of these.** Charter Seat 9 "decides alone: how to implement a
stated requirement" [cited]; the correctness policy is mine. Acceptance tests are
pre-authored at §11 under the I-021 arrangement — **the implementing seat does not grade
its own implementation** — and Seat 9 implements against them and does not amend them. A
test Seat 9 believes is wrong is escalated to me in writing before it is changed.

### 9.1 Effectivity — what binds today and what waits

| Clauses | Status |
|---|---|
| ML-1, ML-2, ML-4, ML-5 – ML-10, ML-12 – ML-17, ML-19, ML-20, ML-21(a)(b), ML-22 – ML-27 | **Effective immediately.** They are declaration, sequencing, and reporting requirements enforceable by me at Gate 0 and Gate 1 with the harness exactly as it stands |
| ML-3 | **Computed and reported immediately; enforced on H-A.** The arithmetic runs at intake today and its verdict binds today — what waits is the registry's ability to carry the number into `evaluate_gate1` |
| ML-11 | **Declared immediately; sealed on H-A** |
| ML-16's DSR consequence | **Effective immediately as INSUFFICIENT-DATA**; upgraded to a computed criterion on H-B |
| ML-18, ML-21(c), §6.1 | **Effective immediately as a caller obligation and a prohibition**; enforced in the splitter on H-C |
| ML-26 | **Effective immediately as a reporting obligation**; enforced in the criterion on H-D |

> **The standing consequence, restated so it is not lost in a table: until H-A exists, no
> fitted family may be sealed as Gate-1-eligible. ADMITTED-AS-EXPLORATORY is the ceiling.**
> The firm holds zero fitted families, so the cost today is zero, and H-A is a single
> column plus one line of summation.

---

## 10. WHAT A FITTED FAMILY'S VALIDATION REPORT MUST CARRY

Every Validation Report is generated by `evaluate_gate1` and written unedited [cited — A1].
The following are the additional fields a fitted family's report must contain; those the
harness cannot yet emit are stated as disclosure lines accompanying the harness artifact,
never as substitutes for it, and never as recomputed criteria.

1. `|Θ|`, its dimension-by-dimension derivation, and `n_declared_fits`.
2. The decomposition `N = n_inherited + n_declared_fits + n_logged`, all four numbers
   visible, none merged — the H-12 discipline extended to the new component.
3. `MinBTL(N_ceiling, 1.0)` against the measured calendar span, and the margin.
4. `σ_SR` over the dispersion sample and `σ_SR` over all logged trials, side by side, with
   `m` and the draw seed.
5. Every ML-14 exemption claimed, with all four conditions addressed individually.
6. The purge width, the embargo width, and the three quantities the embargo is the maximum
   of.
7. The modal configuration, the argmax-fold configuration, and the fold counts for each
   (ML-20).
8. The seed ensemble line: `S`, mean, std, min, max, fraction net-profitable.
9. The eight ML leakage answers (ML-25), each explicitly.
10. Both t-statistics — Newey–West corrected and uncorrected — with the lag truncation
    (ML-26).
11. Whether the R4(b)/ML-27 haircut was applied, and if not, the accepted argument.
12. The sentence, on the face of the report and not in an appendix:

> *The search space stated in this report is a self-report by the sponsoring seat. It
> establishes what was declared before any result existed. It does not establish what was
> run, and no control in this firm can establish that.*

Clause 12 is the ML analogue of Ruling 002 R1's required sentence for a HISTORICAL holdout,
and it exists for the same reason: **a report that omits the limit of its own control will
be read as though the control had none.** A report omitting it is defective and I will
return it.

---

## 11. ACCEPTANCE TESTS — authored by Validation, before implementation

**Standing terms, per the I-021 arrangement.** Seat 9 implements against these and does not
amend them. A test Seat 9 believes is wrong is escalated to me, in writing, **before** it is
changed. Weakening a pre-authored test to make an implementation pass is the failure I-036
records, arriving deliberately instead of by accident.

**File:** `harness/tests/test_ml_trial_accounting.py`. **Baseline:** the suite stands at
**160 passed** [measured, this session]. All fourteen below must pass and **no existing test
may be deleted or weakened.** Target: **174 minimum.**

### 11.1 H-A — `n_declared_fits` reaches the denominator

**ML-T-1 · The field exists, is binding, and is sealed.**
`open_hypothesis(..., n_declared_fits=500)` persists; `"n_declared_fits" in
registry._BINDING_FIELDS`; the `hypothesis_sealed` event's shadow copy carries it; and a
raw `UPDATE hypotheses SET n_declared_fits=…` is detected by `verify_prereg` as a mismatch.
*Asserts that the ML denominator has the same tamper-evidence as every other binding field.*

**ML-T-2 · It reaches `n_trials`, transitively, and is reported separately.**
`family_stats(f).n_trials == n_inherited + n_declared_fits + n_logged`, summed across the
predecessor chain exactly as `n_inherited` already is; and `FamilyStats` exposes
`n_declared_fits` as its own attribute. Assert a chain of three families sums correctly.

**ML-T-3 · It deflates DSR and MinBTL, and the report renders all four numbers.**
Two `evaluate_gate1` runs on an identical return series and an identical single logged
trial, differing only in `n_declared_fits` ∈ {0, 5000}: the DSR value must be **strictly
lower** in the second, and the length criterion's `MinBTL` **strictly higher**. The
markdown report must render `n_trials`, `n_inherited`, `n_declared_fits` and `n_logged` as
four distinguishable figures.
*This is the test that proves the field is a denominator and not a comment.*

**ML-T-4 · Validation refuses to be papered over.** `n_logged == 0` with
`n_declared_fits > 0` yields **INSUFFICIENT-DATA** on the trial-count criterion, with a note
naming `n_declared_fits` as a declared count and not a run trial.
*The H-11 guard, extended to the new component. A family that declared ten thousand fits and
ran nothing has not run anything.*

**ML-T-5 · It is frozen.** Re-calling `open_hypothesis` with a different
`n_declared_fits` raises `PreRegistrationAmendedError` and logs
`hypothesis_amendment_refused` naming the field.

### 11.2 H-B — the dispersion subset

**ML-T-6 · σ_SR can be computed on a designated subset.**
Log 30 trials, of which 10 are tagged as the dispersion sample with deliberately wide
Sharpe dispersion and 20 are tightly clustered. `family_stats` must expose both
`sr_period_std` (all logged) and `sr_period_std_dispersion` (subset only), and the second
must be materially larger on this fixture.

**ML-T-7 · `evaluate_gate1` uses the dispersion σ_SR when it exists, and says so.**
On the ML-T-6 fixture, the DSR criterion is computed from the dispersion σ_SR, its value is
**lower** than the all-logged computation, and the criterion note states which input was
used and the subset size.

**ML-T-8 · Absent a dispersion subset, a fitted family's DSR is INSUFFICIENT-DATA.**
A family flagged as fitted with no dispersion subset → DSR verdict `INSUFFICIENT-DATA`,
never PASS, with the note naming ML-16.

### 11.3 H-C — the splitters

**ML-T-9 · `purged_kfold_splits` refuses an unstated feature lookback and honours a stated
one.** Calling without `feature_lookback` raises. With `feature_lookback=30`,
`embargo_fraction=0.01` and `n_samples=2398`, assert **no training index lies within 30 bars
after any test fold's end** — i.e. the effective embargo is 30, not `⌈0.01·2398⌉ = 24`.
*The exact arithmetic of §6's measured defect, frozen as a test.*

**ML-T-10 · The purge is at least the label span on the training side.**
With `label_span=5`, assert no training index lies in `[t0 − 5, t0)` for any fold, for every
fold including the first and last.

**ML-T-11 · `walk_forward_windows` purges and embargoes.**
With `label_span=5, feature_lookback=30`, assert every yielded training set excludes the 5
bars before the fold and that no training bar in a *later* window reads within 30 bars of a
previous test fold's end. Assert the function **raises** when neither parameter is supplied,
rather than silently reproducing today's unpurged behaviour.
*Today's implementation fails all three assertions [measured — `cv.py:43–61`].*

### 11.4 H-D — the corrected t-statistic

**ML-T-12 · Newey–West is available, correct in direction, and reduces to the raw statistic
at lag 0.** On a synthetic AR(1) series with `ρ = 0.8`, assert
`sr_tstat_nw(r, lag=10) < sr_tstat(r)` and that the ratio is within 20% of
`√((1−ρ)/(1+ρ))`; assert `sr_tstat_nw(r, lag=0) == sr_tstat(r)` to floating tolerance; and
assert on an i.i.d. series that the two agree within 5%.

**ML-T-13 · `evaluate_gate1` reports both, and fails on the corrected one.**
Construct a series whose uncorrected `t` clears 3.0 and whose corrected `t` does not. Assert
the criterion verdict is **FAIL**, that both values appear in the report, and that the
uncorrected figure is explicitly labelled uncorrected.
*A criterion that reports the honest number and grades on the flattering one is worse than
reporting neither.*

### 11.5 H-E — the escalation continuation

**ML-T-14 · The successor escalation is executable exactly once it is authorized.**
Predecessor with `n_trials = 40`. A successor declaring `n_inherited = 400` raises
`InheritedCountDoubleCountError` **as it does today** — that behaviour is preserved, not
removed. With a Validation authorization present (a logged authorization event referenced
by the call, or an explicit keyword), the registration **succeeds**, is logged as
`n_inherited_escalation_authorized` with the authorizing reference, and `family_stats`
returns `n_trials = 400 + 40 + logged`.
*Both halves are required. A change that merely removes the guard fails this test.*

> **Count: 14 acceptance tests.** ML-T-3, ML-T-4, ML-T-7, ML-T-9 and ML-T-11 are the five
> that carry the ruling; the rest close the routes around them.

---

## 12. RELATION TO EXISTING RULINGS AND PRE-REGISTRATIONS

The dispatch asks whether this ruling contradicts anything already binding. Checked
deliberately, item by item.

| Document | Interaction |
|---|---|
| **PREREG-002 §7.1–§7.2** (declared menus contribute 1) | **Extended, not contradicted.** §7.2's discount is conditioned on the selection involving "no search over results"; a fitting search fails that condition on its own terms. ML-13 states the distinguishing test explicitly so the two rules cannot be conflated |
| **PREREG-002 §7.2 escalation rule** | **Not contradicted by this ruling — found to be unexecutable against the harness.** `InheritedCountDoubleCountError` refuses every successor the rule requires (§5, ML-17). This is a pre-existing defect that ML-17 depends on, so it is filed rather than left. **I-053** |
| **PREREG-002 §10** (`N_inherited = 0`, budget 79, ceiling 86) | **Untouched.** PREREG-002 is not a fitted family: its K1–K7 selections are pre-committed from declared menus without reference to a computed quantity, so ML-1's trigger does not fire. Its `MinBTL(86) = 6.14 yr` against 6.571 stands unedited |
| **PREREG-002 §7.3** (`MinBTL(27,000) = 16.79 yr`) | **Confirmed and reproduced.** My §2.2 table is the same function evaluated at different points and agrees |
| **PREREG-002 §10.4** (ceiling `N = 110`) | **Corrected by one trial.** The true maximum against 6.571 years at SR 1.0 is **109**; §10.4 itself records 110 as requiring 6.574 years — "exactly at the span — zero margin" [cited]. Immaterial to that document's conclusion, recorded for accuracy |
| **`grid.py`'s "every point is a logged trial"** | **Preserved without amendment.** ML-15 extends the convention to fit-level sets by adding a *counted* trial; it creates no exception to the logged one |
| **Ruling 001** (holdout regime, ingest ceiling, `predecessor_family`) | **Consistent.** ML-21(a) restates the holdout's inviolability at the fold level. Nothing here reopens D1–D4 |
| **Ruling 002 R1–R4** | **Consistent and extended.** ML-27 extends R4(b) to architectures and feature sets; ML-10's clause-12 sentence is built on R1's precedent |
| **Ruling 003** | **Consistent.** ML-26 generalizes §6.5's Newey–West requirement for F-002 from one falsifier to the Gate 1 criterion, which is where §6.5's own reasoning always pointed |
| **C-001 E1–E5** (the `N = 1` confirmatory exemption) | **Consistent.** E1 requires the statistic named at sealing and E3 makes every other forward computation a logged trial. A fitted family's forward fits are trials under E3 and under ML-13 identically |
| **Amendment A2** | **No path around it is created.** A counted trial produces no number. Every reported quantity still comes from `run_backtest` |
| **Charter §4.2 constants** | **None moved.** `T_STAT_HURDLE`, `DSR_MIN`, `PBO_MAX_PAPER`, `EMBARGO_FRACTION`, `WFE_MIN`, `PUBLISHED_SIGNAL_HAIRCUT` are all used as written. ML-24's two numbers are §4.4's own, imported |

**Nothing in this ruling contradicts any existing pre-registration or ruling.** One
pre-existing contradiction *between* a pre-registration and the harness was found and is
filed (I-053).

---

## 13. WHAT WOULD CHANGE MY MIND

Falsifiers, per house rule 2 — each a specific observable, not a mood.

**On charging the full cardinality (ML-13).**
- I would revise if someone demonstrates a fitting procedure whose selection is provably
  independent of any quantity computed from the sample. I cannot construct one, and if such
  a procedure exists it is not fitting.
- I would **not** revise on an argument that the effective number of independent trials is
  smaller than the cardinality because the configurations are correlated. **That correction
  is already in the machinery and applying it twice would be double-counting in the
  permissive direction.** `expected_max_sharpe` is denominated in σ_SR, and correlated
  trials produce a small σ_SR, which shrinks the deflation benchmark automatically
  [measured — `stats.py:67–82`]. Deflating `N` as well as measuring σ_SR would credit the
  same correlation twice. This is the argument I expect to be made and it is wrong.

**On the dispersion sample (ML-16, `m ≥ 32`).**
- The floor is `[inferred]` from the `1/√(2(m−1))` arithmetic at §2.4, not cited. I will
  move it on a reasoned argument from Seat 9, the Director of Research or the Devil's
  Advocate **before** a family's Gate 0. I will not move it after, and never on the basis of
  what it does to a result.
- If someone demonstrates that a uniform draw over Θ is a materially worse estimator of the
  relevant σ_SR than some stratified alternative, I would adopt the alternative. The
  requirement that σ_SR be estimated on the space searched rather than on the survivors is
  not negotiable; only its estimator is.
- The whole apparatus rests on BLP&Z's order-statistic approximation, which assumes the
  trial Sharpes are approximately Gaussian. If a fitted family's Sharpe distribution over Θ
  is strongly non-Gaussian, `expected_max_sharpe` is misspecified in an unknown direction.
  I have not addressed that and I am flagging it as a known limit rather than pretending the
  machinery is exact.

**On the nested exemption (ML-14).**
- I would tighten it, not loosen it, if evidence appears that (N4) is being satisfied in
  form rather than substance — that is, that sponsors are re-running procedures and not
  declaring it. The tightening would be to withdraw the exemption entirely and charge the
  inner cardinality unconditionally.
- I would loosen (N2)'s inner-purge requirement only on a demonstration that the inner loop
  cannot leak into the outer test fold by construction. I do not believe such a
  demonstration exists for a time series.

**On ML-3's ceiling verdict.**
- The `≥ 4 years` and `MinBTL` requirements are Charter constants and are **not mine to
  move at all** [cited — §4.2, "not negotiable mid-evaluation"]. Only the Principal, in
  writing, in advance.
- The choice to evaluate the ceiling at SR 1.0 rather than at a family's target Sharpe is
  mine, and I would defend it against the obvious objection: evaluating at a hoped-for
  Sharpe lets a family buy search budget with a number it has not earned, and §2.2's table
  shows the leverage is enormous — 109 configurations at SR 1.0 against 9,384 at SR 1.5.
  **A rule that lets a sponsor pick which column of that table applies to them is not a
  rule.**

**On the exploratory-only consequence (§1, §9.1).**
- It lifts the moment H-A ships and its tests are green. It is a consequence of a missing
  capability, not a judgment about ML, and I will not extend it beyond that capability's
  absence.

**On ML-26 and I-050.**
- If the measured autocorrelation of a real family's *net* return series turns out to be
  near zero, the correction is immaterial **for that family** and the corrected and
  uncorrected figures will agree — which the report will show. That is not a reason to omit
  the correction; it is the reason to compute it.
- I would **not** change my mind on any argument that the effect is small in practice.
  "Probably small" is `[assumed]` doing the work of `[measured]`, and the firm's one
  measured instance of the relevant autocorrelation is 0.83.

---

## 14. ISSUE LOG ENTRIES OPENED, AND WHAT IS ADDRESSED TO THE PRINCIPAL

Five entries, written to `logs/ISSUE_LOG.md` at the CIO's instruction under S2-D-006. **The
CRO owns the log**; these are entered by me under that instruction and the ownership is
unchanged.

**Numbering note.** The dispatch directed me to number from **I-049**. During the
termination of this ruling's first run the CIO filed **I-049** for the dispatch-failure
pattern itself [measured — `logs/ISSUE_LOG.md:1513`]. My entries therefore begin at
**I-050**. The collision is recorded rather than silently absorbed, because a duplicate key
in the log is exactly the defect S2-D-005 §3 spent effort removing.

| # | Finding | Severity | Owner |
|---|---|---|---|
| **I-050** | The Gate 1 t-statistic assumes serial independence; no criterion corrects for autocorrelation; the firm holds a measured case at ρ = 0.83 where the inflation factor is ≈ 3.3, in the permissive direction | **HIGH** | quant-validation → head-of-data-infra |
| **I-051** | `walk_forward_windows` applies no purge and no embargo; `purged_kfold_splits` embargoes 1% of bars with no regard to feature lookback | MEDIUM | head-of-data-infra |
| **I-052** | The registry cannot express an ML family's declared fit count, and DSR cannot be computed on a dispersion subset | MEDIUM | head-of-data-infra |
| **I-053** | The `n_inherited` escalation path terminates in a dead end; PREREG-002 §7.2's binding escalation rule is unexecutable | MEDIUM | head-of-data-infra → director-of-research |
| **I-054** | Third occurrence of a logged pattern — commit `ffd73a9` contains 76 lines of this ruling in progress, under a message asserting the terminated runs left nothing on disk | MEDIUM | fable-5-cio |

**I-054 does not arise from the ML analysis.** It was found while verifying that this
ruling's own writes had landed cleanly, and it is filed because it is the **third** instance
of the shape I-013 and I-041 record. Two instances are incidents; three is a source, and
Charter §7.8 makes the log the instrument for saying so. No harm occurred and the entry says
so.

**On the ratings, since the dispatch requires them not be shaded in either direction.**

**I-050 is HIGH and I have not inflated it.** The test I applied is the one the log's
existing HIGH entries satisfy: *a Charter criterion is unenforceable or wrong in a way that
changes verdicts.* I-029 (a falsifier that passes noise 31% of the time), I-034 (a cost path
that guarantees a false KILL), I-037 (a robustness test that manufactures its own bracket
ceiling) are all that shape. An uncorrected `t` against `T_STAT_HURDLE = 3.0` — the firm's
single most-cited number — with a measured instance of the failing assumption in the firm's
own data and an error in the permissive direction, is the same shape.

**I-052 is MEDIUM and I have not under-rated it to avoid interrupting.** Its shape is
I-027's, which was rated HIGH — but I-027 was HIGH because a live family was blocked on it.
Nothing is blocked here: the firm holds zero fitted families, and this ruling closes the gap
safely by capping fitted families at exploratory. **A missing capability with no waiting
consumer and a stated safe default is MEDIUM, and rating it HIGH to force attention would be
the mirror of the error the Standing Order warns against.**

**I-051 and I-053 are latent and have never fired** — zero families, zero trials. Both would
fire on the first fitted family and I-053 would fire on PREREG-002's first revision. MEDIUM
is the same rating Ruling 001 gave the analogous latent `gates.py` defect.

### 14.1 Addressed to the Principal

> **One item, and it reaches him mechanically rather than by my choosing: I-050, filed
> HIGH, is a hard interrupt under Standing Order 001 §4.**

The finding as it should reach him, in one paragraph: *the firm's Gate 1 t-statistic is
computed as `SR × √T`, which assumes the return series is serially independent. The firm has
measured a case in its own data where that assumption fails badly — daily funding
autocorrelation of 0.83 — and where the resulting t-statistic would be overstated by roughly
a factor of three. No Gate 1 criterion corrects for it, and the error runs in the direction
that makes strategies look better than they are. The repair is a Newey–West correction to
the estimator; it is not a threshold change, `T_STAT_HURDLE = 3.0` does not move, and it
requires no Charter amendment. No family is currently affected because the firm has run zero
trials.*

**Nothing else in this ruling is addressed to the Principal, and I am requesting no Charter
amendment, no threshold change, and no override.** Every number used here is either a
Charter constant used as written or an existing constant applied to a new surface, and §13
records which of my own choices are judgment calls.

---

## 15. SIGN-OFF

**This is a specification and a set of acceptance tests. It is not a Gate 0 intake verdict
on any family and it is not a Gate 1 evaluation.**

Twenty-seven binding clauses. `N` for a fitted family is the sealed cardinality of its
declared search space plus every `run_backtest` call plus any inherited count, with one
reduction for a correctly nested inner loop. The ruling's most consequential finding is not
about `N` at all: **σ_SR is roughly three times more load-bearing than `N` over the ranges a
fitted family occupies, and the firm currently lets the sponsor choose it by choosing which
trials get a return series.** ML-16 closes that.

The ruling is restrictive. On the firm's best data surface it admits a search of roughly
thirty configurations, forecloses every large-space method at Gate 1, and caps fitted
families at exploratory until a single missing registry column exists. **That is the
arithmetic of a 6.571-year sample against a t-hurdle of 3.0, and it is more useful to the
firm at intake than at Gate 1.**

*No code was modified, no data fetched, nothing sealed, nothing committed, no trial logged,
no hypothesis opened. `book/registry.db` untouched at 0 hypotheses / 0 trials. Harness suite
verified at 160 passed before and after.*

**Head of Quantitative Validation · Castellan Capital · 2026-08-04**
*Binding on Seats 1, 2, 6–10. Appealable only to the Principal, in writing.*
