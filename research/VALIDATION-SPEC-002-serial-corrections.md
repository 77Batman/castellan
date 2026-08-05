# VALIDATION-SPEC-002 — Serial corrections to MinBTL and the Deflated Sharpe Ratio (I-057)

**Seat:** Head of Quantitative Validation · **Date:** 2026-08-04 · **Dispatch:** S2-D-013
**Status:** BINDING on implementation. Specification only — no harness source file is modified by this document.
**Implementer:** Head of Data & Infrastructure (Seat 9), a later dispatch.
**Authority:** the Principal's ruling on I-057, 2026-08-04, recorded verbatim in §0.2.
**Predecessor:** `research/VALIDATION-SPEC-001-estimator-corrections.md` (I-050, I-051). This document reuses SPEC-001's estimator machinery and does not restate it.
**Baseline suite at authoring: 26 failed, 162 passed [measured]. Floor after this spec's tests land: see §11.**

---

## 0. SCOPE, AUTHORITY, AND WHAT THIS DOCUMENT MAY NOT DO

### 0.1 One-sentence statement of each correction

**Item 1 — MinBTL.** The required backtest length is multiplied by a measured variance
inflation factor `VIF`, taken as `max(1.0, HAC long-run-variance ratio, AR(1) plug-in)` on
the family's net return series, and consumed through a construction that takes the
**maximum** of the corrected and uncorrected requirement so the change can never shorten a
requirement, from which the admissible trial ceiling follows as
`N_max = min(N_max at VIF = 1, N_max at the measured VIF)`.

**Item 2 — DSR.** The Deflated Sharpe Ratio's `z` is divided by `√VIF` — an
effective-sample-size substitution applied to the `√(T−1)` factor and **not** to the
published non-normality denominator, which is left byte-for-byte untouched — and the graded
figure is `min(DSR_serial, DSR_iid)` so the change can never raise a DSR.

### 0.2 The Principal's ruling, verbatim

> *"the ceiling is a function of an unmeasured quantity, below 109 at every ρ > 0."*

> *"§10.4 does not seal a constant. It seals the corrected ceiling as a function:
> `N_max = min(109, corrected-MinBTL ceiling at ρ̂)`, where ρ̂ is the family's net-return
> autocorrelation, measured by the harness from logged trials at evaluation time. This is
> monotone-conservative — measurement can only tighten, never loosen, so it is not the
> I-029(d) operation; it is the `min(t_NW, t_raw)` construction extended to `N`."*

And the consequence he ruled in advance, so this specification is written knowing it:

> *"if ρ̂ measures ≥ 0.1, the admissible ceiling falls below the declared `N` = 86 and this
> family cannot clear Gate 1's length criterion on the data we hold. That outcome, should it
> arrive, is the machinery answering — a PARK or kill on measured ρ is a terminal verdict
> under §1, not a malfunction."*

**§7 reports that his stated trigger is not tight enough. The binding threshold for
PREREG-002 is `ρ̂ ≈ 0.034`, not 0.1.** That is a correction to a number in a ruling, made
before the ruling is relied on, and it moves in the tightening direction.

### 0.3 What this document does not do

- **No Charter §4.2 constant moves.** `DSR_MIN = 0.95`, `T_STAT_HURDLE = 3.0`,
  `MIN_YEARS = 4`, `EMBARGO_FRACTION = 0.01`, `CSCV_PARTITIONS_S = 16` are imported and
  never redefined. None appears below as a parameter.
- **No harness source file is edited by this document.** `harness/castellan/` is untouched
  by this dispatch. Specification and new test files only.
- **No hypothesis is opened, no trial is registered, no backtest is run.**
  `book/registry.db` reads **0 hypotheses / 0 trials / 1 event** before and after
  [measured, this session].
- **The holdout is not consulted.** `HoldoutVault.open_once` is not invoked. No vault under
  `book/vaults/` is read, listed, or decrypted. No passphrase is requested, supplied, or
  held. **Holdout status: LOCKED, unopened, unretired.**
- **No path around `run_backtest` is created (A2).** Both items change how a number the
  engine already produced is *evaluated*. Neither produces a number.
- **`test_tstat_hac.py` and `test_cv_purge_embargo.py` are not touched** — they are Seat 9's
  target this hour. All tests added by this dispatch are in new files (§11).

### 0.4 Dependency on SPEC-001, stated as a hard ordering

Every clause below consumes `stats.hac_lag_andrews`, `stats.sr_tstat_nw`'s long-run variance,
and SPEC-001's eligibility guards E-6, E-7 and E-9. **None of those exists yet.** Therefore:

> **M-0 · This specification is implementable only after `test_tstat_hac.py` is green.**
> Seat 9 does not begin SPEC-002 while SPEC-001 Item 1 is red. If the two land in one
> dispatch, Item 1's tests must pass before Item 2's are run. **Building the MinBTL
> correction on an unverified HAC estimator would make a wrong `VIF` indistinguishable from
> a wrong ceiling.**

### 0.5 Provenance discipline

Every number is tagged `[measured]` (computed this session; reproduction in §1.6),
`[cited]` (traced to a named artifact), or `[inferred]` (my judgment, marked wherever it
sets a constant).

---

## 1. ITEM 1 — THE CORRECTED MinBTL · clauses M-1 to M-14

### 1.1 The defect, restated so the fix can be checked against it

`min_backtest_length_years(N, SR_ann, ppy)` returns `(E[max Z_N]/SR_period)²/ppy`
[measured — `stats.py:119–133`]. The construction sets the required length at the point
where the strategy's t-statistic equals the expected maximum of `N` zero-edge trials — and
it computes that t-statistic as `SR_period·√T`, which is the **uncorrected** statistic
I-050 repaired. Under serial dependence the honest t-statistic is smaller by `√VIF`, so the
`T` at which the honest statistic reaches `E[max Z_N]` is larger by `VIF`. **The harness
requires the length that would suffice if the returns were serially independent. They are
not, and the error runs permissive.** [cited — I-057]

### 1.2 The construction — M-1 to M-5

> **M-1 · `min_backtest_length_years` is not edited.** Body, signature, docstring and
> behaviour preserved exactly. It remains the honest i.i.d. figure and every existing call
> site keeps getting it. **The correction is a new function, not a mutation of an old one.**
> Identical in form and in reason to SPEC-001 E-1.

> **M-2 · New function `stats.min_backtest_length_years_serial(n_trials, target_annual_sr,
> periods_per_year=252, *, vif) -> float` — exact construction.**
>
> ```
> mb_iid  =  min_backtest_length_years(n_trials, target_annual_sr, periods_per_year)
> MinBTL_serial  =  max( mb_iid ,  mb_iid · vif )
> ```
>
> `vif` is a **required keyword-only float**. There is no default. A default of `1.0` would
> let a caller obtain the uncorrected figure from the corrected function by omission, which
> is the shape W-1 closed for `feature_lookback` and the shape this clause closes here.
> `vif` non-finite or `vif <= 0` raises `ValueError`.
>
> **The outer `max` is not decoration and it is not redundant with M-8's floor.** It is the
> second of two independent enforcements of monotone-conservatism (§4), and it is the one
> that survives a future change to the estimator. `mb_iid = inf` (non-positive Sharpe)
> propagates unchanged.

> **M-3 · The variance inflation factor is a ratio of variances, not of standard errors.**
> `VIF = σ²_LR / γ₀` — the long-run variance of the mean over the contemporaneous variance.
> SPEC-001's `HACTStat.inflation` is `t_raw/t_nw = √(σ̂²_NW/γ̂₀)`, a ratio of *standard
> errors*. **`VIF = inflation²`.** Seat 9 will have `inflation` to hand and the squaring is
> the single most likely implementation error in this document. `test_mbs_04` exists for it.

> **M-4 · New function `stats.max_admissible_trials(span_years, target_annual_sr,
> periods_per_year=252, *, vif) -> int`.** The largest integer `N ≥ 1` satisfying
> `min_backtest_length_years_serial(max(N,2), target_annual_sr, periods_per_year, vif=vif)
> ≤ span_years`, found by doubling-then-bisection. Returns `1` if no `N ≥ 2` satisfies it.
> Returns the doubling cap `2**31 − 1` where the constraint never binds, and the caller
> renders that as `"unbounded on this span"` rather than as an integer.
>
> **This function is the Principal's sealed `N_max`, made executable.** It is what the
> report prints and what §10.4-style seals reference. It is a pure function of
> `(span, SR, ppy, vif)` and consumes no sample.

> **M-5 · The ceiling is reported as an explicit `min` of the two, always.**
>
> ```
> n_max_iid     =  max_admissible_trials(span, sr, ppy, vif=1.0)
> n_max_serial  =  max_admissible_trials(span, sr, ppy, vif=vif_gate)
> N_MAX         =  min( n_max_iid ,  n_max_serial )
> ```
>
> M-2's `max` already guarantees `n_max_serial ≤ n_max_iid`, so this `min` can never bind.
> **It is written anyway, and `test_mbs_09` asserts it never binds.** The Principal's ruling
> is stated as a `min` and the code says `min`; a future seat reading the code finds the
> ruling, not a derivation of it. A `min` that provably never binds costs one comparison and
> buys a structural guarantee that does not depend on M-2 staying correct.

### 1.3 The Gate 1 criterion — M-6 to M-9

> **M-6 · The length criterion is renamed and rebuilt.** `gates.py:336–344`'s branch
> becomes:
>
> ```
> minbtl_iid     =  min_backtest_length_years(max(fam.n_trials,2), sr_ann, ppy)
> minbtl_serial  =  min_backtest_length_years_serial(max(fam.n_trials,2), sr_ann, ppy,
>                                                    vif=vif.vif_gate)
> need           =  max(MIN_YEARS, minbtl_serial)
> ```
>
> criterion name **`"Backtest length (years, serial-corrected MinBTL)"`**, threshold string
> `f">= max({MIN_YEARS:g}, MinBTL_serial={minbtl_serial:.2f})"`, verdict
> `years_calendar >= need`, and a `note` that always carries
> `f"MinBTL(iid) = {minbtl_iid:.2f}y; VIF = {vif.vif_gate:.3f}; N_max = {N_MAX}"`.
> **The i.i.d. figure travels on the criterion's face so the size of the correction survives
> into any excerpt of the table.** Precedent: SPEC-001 E-11.

> **M-7 · `n_logged == 0` makes the length criterion INSUFFICIENT-DATA.** Today the branch
> keys on `fam.n_trials >= 1`, which is satisfied by `n_inherited` alone — a declared,
> phantom count with no return series [cited — `registry.py:512–553`]. A family with
> `n_logged = 0` has **no series from which VIF can be measured**, so its length criterion
> would be evaluated at `VIF = 1`: the permissive assumption this entire document exists to
> remove, silently reinstated for exactly the families with the least evidence.
>
> The verdict becomes `INSUFFICIENT-DATA` with note
> `"No logged trial carries a return series; the family's serial dependence is unmeasurable
> and MinBTL cannot be evaluated at an assumed VIF = 1 (I-057). N unknown or unmeasurable ⇒
> INSUFFICIENT-DATA, never PASS."`
>
> **This changes no Gate verdict today or ever** — such a family already draws
> INSUFFICIENT-DATA on the trial-count criterion [measured — `gates.py:233–247`] and one
> non-PASS fails the Gate. It changes the *reason stated on a criterion's face*, which is
> the artifact a later reader relies on. Cheap, and a tightening, therefore mine.

> **M-8 · `vif_gate` is floored at 1.0 inside the estimator (R-7), and M-2's `max` floors it
> again at the consumer.** Two independent guards, specified in two places, tested
> separately (§4). Neither is deleted on the argument that the other exists.

> **M-9 · `MIN_YEARS` and the one-full-regime-cycle requirement are untouched.** The
> criterion remains `≥ max(4 years, MinBTL_serial)`; the correction can only raise the
> binding term, never replace the 4-year floor. Charter §4.4's "≥ 1 full regime cycle" is
> not evaluated by the harness today and is not made evaluable by this document — that
> remains a stated gap.

### 1.4 What the report carries — M-10 to M-11

> **M-10 · `ValidationReport` gains eight fields**, all rendered:
> `minbtl_iid_years`, `minbtl_serial_years`, `vif_gate`, `vif_hac`, `vif_ar1`,
> `vif_rho_hat`, `n_max_admissible_iid`, `n_max_admissible_serial`.
> The markdown renders, directly beneath the criteria table and beneath SPEC-001 E-10's
> t-statistic line, a block of exactly this shape:
>
> ```
> Serial dependence: VIF = **{vif_gate:.3f}** (HAC {vif_hac:.3f}, AR(1) plug-in
> {vif_ar1:.3f}, ρ̂ = {vif_rho_hat:+.3f}, lag {vif_lag}, source {vif_source},
> {vif_n_trials_used} trial series).
> MinBTL: **{minbtl_serial_years:.2f}y** serial-corrected · {minbtl_iid_years:.2f}y assuming
> serial independence — **the i.i.d. figure is reported for continuity and is NOT graded.**
> Admissible trial ceiling on this span and Sharpe: **N_max = {N_MAX}**
> (= min({n_max_admissible_iid}, {n_max_admissible_serial})). Registry N = {fam.n_trials}.
> ```
>
> **These are report fields, not `Criterion` rows.** A `Criterion` carries a verdict and
> `overall` is PASS only if every criterion is PASS; adding an ungraded diagnostic as a
> criterion would fail every Gate forever. Seat 9 must not implement M-10 by appending to
> `criteria`. Precedent and reason: SPEC-001 E-10.

> **M-11 · A MinBTL figure quoted without its VIF is inadmissible in a Validation Report,
> and I will return it.** Same standing rule as SPEC-001 E-16 for a `t` quoted without its
> lag. This binds every seat, including me.

### 1.5 The estimator I considered and declined — M-12 to M-14

> **M-12 · The prewhitened (Andrews–Monahan 1992) HAC is not adopted, and this clause
> records why with the measurements, so the decision is not re-litigated from intuition.**
>
> Prewhitening filters the demeaned series by its AR(1) coefficient, applies the Bartlett
> HAC to the residual, and recolours by `(1−ρ̂)⁻²`. On a true AR(1) it is essentially exact
> where the plain HAC is not [measured, 12 seeds, T = 2,398]:
>
> | ρ | true VIF | plain HAC | prewhitened | AR(1) plug-in |
> |---:|---:|---:|---:|---:|
> | 0.1 | 1.222 | 1.187 | 1.222 | 1.222 |
> | 0.3 | 1.857 | 1.778 | 1.858 | 1.856 |
> | 0.5 | 3.000 | 2.826 | 3.002 | 3.004 |
> | 0.83 | 10.765 | 9.092 | 10.801 | 10.854 |
>
> **But on overlapping labels — the case Ruling 004 ML-26 says a fitted family will actually
> be in — prewhitening is the worst of the three** [measured, 12 seeds, MA(k) of i.i.d.
> innovations, true VIF = k]:
>
> | k | true VIF | plain HAC | prewhitened | AR(1) plug-in |
> |---:|---:|---:|---:|---:|
> | 3 | 3.0 | 2.768 | 4.140 | 4.890 |
> | 5 | 5.0 | 4.682 | 10.159 | 8.703 |
> | 21 | 21.0 | 18.756 | 49.437 | 38.765 |
>
> The cause is mechanical: at `ρ̂ = 20/21 = 0.952` the recolouring divides by
> `(1−0.952)² = 0.0023`, a **434× amplification** of any error in the residual's long-run
> variance. **An estimator with a 434× amplifier in it is not one I will put behind a Gate
> criterion.** Declined `[inferred]`.

> **M-13 · The adopted construction is `VIF = max(1.0, VIF_HAC, VIF_AR1)` and the three
> reasons are recorded.**
>
> 1. **It is the construction already on the record.** The 55 / 31 / 19 / 2 ceilings the
>    Principal ruled on are the AR(1) plug-in applied to `min_backtest_length_years`
>    [cited — SPEC-001 §4.2], reproduced exactly this session (§1.6). Binding a different
>    estimator would silently move numbers a ruling was made against.
> 2. **It adds no new estimator machinery.** Both terms fall out of SPEC-001's E-2 and E-3,
>    which Seat 9 is implementing this hour. Implementation risk is the dominant risk in a
>    statistical core and this construction carries almost none.
> 3. **It has no amplifier.** `VIF_AR1` is bounded by SPEC-001 E-9's `|ρ̂| < 0.97` refusal at
>    `(1.97/0.03) = 65.7`, and `VIF_HAC` is a Bartlett-weighted sum, bounded above by
>    `2L+1`.
>
> **What it costs, stated rather than hidden.** On MA(k) structure the plug-in over-states
> by 1.63–1.85× [measured]. **That over-statement lands only where the family is already
> dead.** At true VIF = 3 the ceiling is 8 trials; at the plug-in's 4.89 it is 5. Both are
> single digits; no fitted family operates in either. Where verdicts are actually in play —
> `VIF ∈ [1.0, 1.5]`, ceiling 109 down to 31 — the three estimators agree to **within 1%**
> [measured, table above at ρ = 0.1 and 0.2]. **The choice among them is immaterial where it
> matters and one-sided where it is not.**

> **M-14 · The divergence disclosure, and the one route back to me.** When
> `VIF_AR1 > 1.5 · VIF_HAC`, the report's VIF line appends
> `"— AR(1) plug-in exceeds HAC by {ratio:.2f}×; MA/overlapping-label structure is the
> likely cause (M-13) and the plug-in over-states it."` **A sponsor whose Gate verdict turns
> on that gap brings it to me with the family's label span and I will rule on the family, on
> the record.** I will not change the construction to accommodate one family, and Seat 9
> does not adjust the 1.5 to make anything pass — that adjustment is the Appendix B item 4
> failure in its purest form. `1.5` is `[inferred]`.

### 1.6 Reproduction

Every figure in §1 and §6–§7 is a pure function of `castellan.stats` plus simulated series
and consumes no sample, no PIT row, and no registry row.

```
max{N : min_backtest_length_years(N,1.0) * (1+r)/(1-r) <= 6.571}   -> 109/55/31/19/12/8/5/2/2
min_backtest_length_years(86,1.0)                                  -> 6.1359
6.571 / 6.1359                                                     -> 1.0709  (max admissible VIF)
(1.0709-1)/(1.0709+1)                                              -> 0.03424 (binding rho_hat)
1.645/sqrt(2397)*sqrt(365)*sqrt((1+r)/(1-r))                       -> DSR additive term
```

Scripts: `scratchpad/spec002.py`, `spec002b.py`, `spec002c.py` (session-scoped).

---

## 2. ITEM 2 — THE DSR SERIAL TERM · clauses D-1 to D-10

### 2.1 The decision, stated first

**DSR can carry a serial correction without ceasing to be DSR — but only if the correction
is applied to the sample-size factor and not to the non-normality denominator.** That is the
specification choice I declined to improvise in SPEC-001 §4.3, and it is now made.

`deflated_sharpe_ratio` computes [measured — `stats.py:103–116`]:

```
denom  =  1 − g₃·SR + ((g₄−1)/4)·SR²
z      =  (SR − SR₀) · √(T−1) / √denom
DSR    =  Φ(z)
```

`denom` is the asymptotic variance of the **Sharpe estimator** under i.i.d.-but-non-normal
returns [cited — Bailey & López de Prado 2014, after Mertens]. `√(T−1)` is the i.i.d.
sample-size factor. **The serial defect lives entirely in the second of those two, and the
correction goes there.**

> **D-1 · `deflated_sharpe_ratio`'s behaviour is preserved exactly; one pure extraction is
> authorized.** Seat 9 extracts the `z` arithmetic into a new private
> `stats._dsr_z(returns, n_trials, trial_sr_std_period) -> float` and leaves
> `deflated_sharpe_ratio` as `norm.cdf(_dsr_z(...))` with its signature, docstring and NaN
> contract untouched. **This is a refactor, not a mutation, and it is pinned:** `test_dsr_02`
> asserts the public function's output is **bitwise identical** to today's on 200 randomized
> inputs, and it is a guard test that must pass before and after. **No other edit to
> `deflated_sharpe_ratio` is authorized by this document.**
>
> *Why an extraction is authorized here when M-1 and SPEC-001 E-1 forbade one.* There, the
> corrected statistic was a genuinely different estimator. Here the serial version needs the
> **same `z`**, and the two admissible ways to get it — reimplement the `denom` arithmetic,
> or recover `z = Φ⁻¹(DSR)` — are both defective. See D-3.

> **D-2 · New function `stats.deflated_sharpe_ratio_serial(returns, n_trials,
> trial_sr_std_period, *, vif) -> float`.**
>
> ```
> z_iid    =  _dsr_z(returns, n_trials, trial_sr_std_period)
> z_serial =  z_iid / sqrt(vif)
> DSR      =  min( Φ(z_serial) , Φ(z_iid) )     # D-6, the non-permissive floor
> ```
>
> `vif` is a required keyword-only float; no default; non-finite or `<= 0` raises
> `ValueError`. `z_iid` NaN propagates as NaN (`T < 10`, `denom ≤ 0`, degenerate series).

> **D-3 · Neither reimplementing `denom` nor recovering `z` from `Φ⁻¹(DSR)` is acceptable,
> and the second one hides a permissive precision loss.**
>
> *Reimplementing* the `denom` arithmetic in a second function creates a second place for it
> to drift, and the two would then disagree on a graded criterion with no test able to say
> which was right.
>
> *Recovering* `z = Φ⁻¹(DSR_iid)` is worse and the failure is one-sided. `norm.cdf`
> saturates at exactly `1.0` for `z ≳ 8.3`, so `norm.ppf` returns `+inf` [measured:
> `norm.ppf(norm.cdf(9.0)) = inf`; `norm.ppf(norm.cdf(8.0)) = 7.9916`, already a 0.1%
> loss]. A family with `z_iid = 10` and `VIF = 100` has a true `z_serial = 1.0` and a true
> DSR of **0.841 — a FAIL**. The recovery route computes `inf/10 = inf` and returns
> **1.000 — a PASS.** The left tail is exact to `1e-15` and the right tail, the only tail
> where a family passes, silently loses the correction entirely. **`test_dsr_06` constructs
> exactly this case and asserts FAIL.**

> **D-3a · A NaN `vif` is not permitted to become a PASS.** `vif` NaN raises `ValueError` at
> the function boundary (D-2), and R-11 routes an unmeasurable VIF to INSUFFICIENT-DATA at
> the criterion. There is no path on which an unknown VIF silently behaves as `1.0`.

### 2.2 Why the sample-size factor and not the denominator — D-4 to D-5

> **D-4 · The omitted term is permissive, it is bounded, and it is negligible only in the
> regime where verdicts turn. I measured it rather than asserting it.**
>
> A fully general treatment would also serially correct `denom` itself, since `g₃` and `g₄`
> are moments of a dependent process. `z_full/z_chosen = √(denom_iid/denom_serial)`, and
> bounding `denom_serial ≤ 1 + VIF·(denom_iid − 1)` — a deliberate **upper bound**, since it
> scales the entire non-normality excess by the full VIF when the skew term does not scale
> that way — gives the shortfall in `z` [measured, `SR_ann = 1.0` daily]:
>
> | | `VIF = 1.5` | `VIF = 3.0` | `VIF = 11.0` |
> |---|---:|---:|---:|
> | normal (`g₃ = 0, g₄ = 3`) | 0.03% | 0.14% | 0.7% |
> | realistic (`g₃ = −1, g₄ = 8`) | **1.3%** | 5.0% | 19.4% |
> | extreme (`g₃ = −2, g₄ = 15`) | 2.5% | 8.9% | 29.7% |
>
> **The omission runs permissive — `z_chosen ≥ z_full` — and I state that plainly rather
> than claiming the approximation is neutral.**
>
> Why it is nonetheless the right choice, on the same argument as M-13. Verdicts turn in the
> `VIF ∈ [1.0, 1.5]` band, where the ceiling runs from 109 down to 31 and a family is alive.
> There the omission costs **at most 2.5% of `z`**, against a `√VIF` correction of up to
> 22% — the correction being made is an order of magnitude larger than the correction being
> omitted. Above `VIF ≈ 3` the omission grows to 5–9%, but a family at `VIF = 3` needs
> **18.4 years** of history to clear MinBTL at `N = 86` [measured, §7] and is dead on the
> length criterion long before DSR is reached. **The residual permissive error is confined
> to families that fail on another criterion first.**
>
> **What would change this.** A family that clears the corrected length criterion, is
> materially non-normal, and fails or passes DSR within 3% of 0.95. That family comes to me
> and I will compute option (b) by hand for it, on the record, as a one-family ruling.
> `[inferred]`

> **D-5 · At `vif = 1.0` the corrected function reduces to the published statistic exactly,
> and this is a tested property, not a claim.** `z/√1 = z`, `min(Φ(z), Φ(z)) = Φ(z)`, and
> `test_dsr_01` asserts bitwise equality across 200 randomized inputs. **This is what makes
> it still DSR:** a reader who reconstructs Bailey & López de Prado's statistic from the
> paper gets the firm's number back exactly by setting `VIF = 1`, and the firm's report
> states the `VIF` it used. Precedent: SPEC-001 E-2(a)'s lag-0 identity, and it is why that
> clause insisted on the `T − 1` divisor.

### 2.3 What I am choosing against — D-6 is the floor, this is the menu

Four options were on the table. **The one chosen is (c).**

| | Option | Why not |
|---|---|---|
| (a) | **Leave DSR uncorrected; report a serial diagnostic beside it.** | Leaves a Charter §4.4 graded criterion running permissive while printing the evidence that it does. That is I-057 restated as a feature. **Rejected outright.** |
| (b) | **Replace the i.i.d. SE with a full Lo (2002) HAC standard error of the Sharpe** — a HAC on the joint `(r, r²)` moment process. | This is the reference-correct answer and I record it as such. Rejected because: it is a far more fragile finite-sample object than the mean's HAC; it has no published DSR precedent, so the number reported as "DSR" would not be reconstructable by any external reader; and **it can produce a smaller standard error than the i.i.d. one in a given sample, i.e. it loosens** — which the Principal's I-050 asymmetry places outside my authority. Under D-6's floor it would loosen nothing, but a construction whose correct behaviour is masked by a floor half the time is a construction I do not understand well enough to bind. |
| (c) | **Effective-sample-size substitution: `z → z/√VIF`, `denom` untouched.** | **Chosen.** Minimal; single-parameter; exact reduction at `VIF = 1` (D-5); uses the identical `VIF` that corrects MinBTL and the identical long-run variance that corrects the t-statistic, so the three cannot disagree about one series (D-7); first-order correct with a quantified second-order error (D-4). |
| (d) | **Abandon DSR for a different multiple-testing statistic.** | `DSR_MIN = 0.95` is a Charter §4.2 constant naming the statistic. Replacing it is a §2 amendment decided by the Principal in advance — **not mine, and I am not requesting it.** |

> **D-6 · THE NON-PERMISSIVE FLOOR. `DSR_gate = min(DSR_serial, DSR_iid)`,
> unconditionally.** `z_iid` is negative whenever the candidate Sharpe falls below the
> deflation benchmark — the common case for an overfitted family, and exactly the case the
> statistic exists to catch. Dividing a **negative** `z` by `√VIF > 1` moves it toward zero
> and **raises** DSR: at `z = −2, VIF = 4`, DSR goes 0.023 → 0.159. That is an estimator
> change that loosens. The `min` is taken without a sign condition, and it also absorbs any
> `vif < 1` that a future estimator change might produce. Identical in shape and in
> justification to SPEC-001 E-8. **What would have to be true to remove it: a Principal act
> under §2. I do not recommend it and I am not requesting it.** `[inferred]`

### 2.4 The criterion, the report, and Gate 2 — D-7 to D-10

> **D-7 · One VIF, three consumers.** The same `vif_gate` value corrects the t-statistic
> (via SPEC-001's `t_nw`, whose `inflation² = VIF`), MinBTL (M-2) and DSR (D-2), computed
> **once** per `evaluate_gate1` call and passed to all three. A report that deflated `t` by
> 1.9× and inflated MinBTL by 10.7× from the same series would be incoherent on its face.
> **`test_dsr_08` asserts the coherence: `HACTStat.inflation² == vif_hac` to `1e-9`.**

> **D-8 · The graded criterion.** `gates.py:266–268`'s criterion is renamed
> **`"Deflated Sharpe Ratio (serial-corrected)"`**, its value is `DSR_gate`, its threshold
> string is unchanged (`">= 0.95"`), verdict `PASS` iff `DSR_gate ≥ DSR_MIN` and the VIF is
> eligible, `INSUFFICIENT-DATA` if the VIF is ineligible (R-11) or fewer than 2 registry
> trials exist (existing behaviour, unchanged), `FAIL` otherwise. Its `note` always carries
> `f"DSR(iid) = {dsr_iid:.4f}, VIF = {vif:.3f}, T_eff = {t_eff:.0f}"`.

> **D-9 · `T_eff` is a reported diagnostic and is defined once.**
> `T_eff = (T − 1)/VIF + 1`, chosen so that `√(T_eff − 1) = √(T−1)/√VIF` **exactly** and the
> reported effective sample size is the one the arithmetic actually used. `T_eff` is never
> fed back into any other statistic. Reporting `T/VIF` instead would differ by `~0.03` bars
> at `T = 2,398, VIF = 10.7` [measured] and would make the report internally inconsistent
> for no benefit.

> **D-10 · Gate 2 uses the same construction.** Charter §4.5's "DSR recomputed with final N"
> is `deflated_sharpe_ratio_serial` at the VIF measured at Gate 2 evaluation time, against
> the unchanged `DSR_MIN = 0.95`. **A Gate 2 evaluation that recomputed the i.i.d. DSR would
> reintroduce the whole defect at the moment real capital is authorized**, which is the worst
> possible place for it.
## 3. ρ̂ AND THE VARIANCE INFLATION FACTOR · clauses R-1 to R-16

*A ceiling that depends on `ρ̂` is only as sound as `ρ̂`. This is the section a future seat
will try to move, and every clause in it is written to be moved only by a Principal act.*

### 3.1 The per-series estimator — R-1 to R-5

> **R-1 · New dataclass `stats.VIFResult`, frozen.**
>
> ```
> @dataclass(frozen=True)
> class VIFResult:
>     vif_gate:        float   # max(1.0, vif_hac, vif_ar1) — the ONLY figure consumed
>     vif_hac:         float   # sigma^2_NW(L) / gamma0, both at divisor T-1
>     vif_ar1:         float   # (1 + rho+) / (1 - rho+),  rho+ = max(0, rho_hat)
>     rho_hat:         float   # unclipped lag-1 autocorrelation (SPEC-001 E-3)
>     lag:             int     # L, the SPEC-001 E-5 lag
>     lag_rule:        str
>     source:          str     # "candidate-only" | "max(candidate, family-median)"
>                              # | "unmeasurable"
>     n_series_used:   int     # trial series entering the family term
>     n_series_excluded: int   # excluded by R-9's length floors
>     eligible:        bool    # False => INSUFFICIENT-DATA (R-11)
>     note:            str
> ```

> **R-2 · New function `stats.variance_inflation(returns, *, label_span=1) -> VIFResult`
> — the single-series estimator, no discretion.**
>
> ```
> L, rho_hat  =  the SPEC-001 E-5 lag and E-3 rho_hat, computed on `returns`
> gamma0      =  sum(d^2) / (T - 1)                       # d = returns - mean(returns)
> vif_hac     =  sigma^2_NW(returns, L) / gamma0          # SPEC-001 E-2's numerator
> rho_plus    =  max(0.0, rho_hat)
> vif_ar1     =  (1 + rho_plus) / (1 - rho_plus)
> vif_gate    =  max(1.0, vif_hac, vif_ar1)
> ```
>
> **Lags, answered exactly.** `vif_hac` uses the **whole Bartlett-weighted autocovariance
> profile from lag 1 to `L`** — it is not a single-lag statistic, and that is the point: it
> is what sees MA structure the lag-1 coefficient cannot. `vif_ar1` uses **lag 1 only**.
> `L` is SPEC-001 E-5's `min(max(andrews, label_span − 1, stated_lag or 0),
> min(⌊T/4⌋, T−2))` — Andrews-selected, floored at the declared label span, capped, and
> **one-sided: a caller can raise `L` and can never lower it.** That is what closes the
> discretionary route around the whole of §3.

> **R-3 · `rho_plus = max(0, rho_hat)` — the firm takes no credit for negative
> autocorrelation.** At `rho_hat < 0` the AR(1) term is `1.0` and only the floor and the
> HAC term remain, and the floor makes `vif_gate ≥ 1` regardless. **This is the same
> deliberate one-sided bias as SPEC-001 E-8 and it has the same justification:** giving a
> family a *shorter* required backtest because its returns mean-revert is an estimator
> change that loosens, which the Principal's I-050 asymmetry places outside my authority.
> Removing it requires a Principal act under §2. I do not recommend it and I am not
> requesting it. `[inferred]`

> **R-4 · Degenerate variance.** `gamma0 == 0` (constant series) ⇒ `vif_hac`, `vif_ar1`,
> `vif_gate` are `nan` and `eligible = False`. `sigma^2_NW(L) ≤ 0` is unreachable under the
> Bartlett kernel except as an exact zero; if it occurs, `vif_hac = nan`, the term is
> **dropped from the max** (not treated as zero), and `vif_gate = max(1.0, vif_ar1)` with the
> omission named in `note`.

> **R-5 · The eligibility guards are SPEC-001's, inherited verbatim, not re-derived.**
> `eligible = False` when **any** of: `T < 32`; `T < 10·(L+1)` (E-6); `gamma0 == 0` (E-7);
> `|rho_hat| ≥ 0.97` (E-9). **A near-unit-root series is refused, not corrected**: at
> `rho_hat = 0.96` the AR(1) term is 49 and the ceiling is 1 trial, so a family is
> comprehensively dead well before the refusal threshold and the refusal is not a loophole.
> A refusal is escalated to Validation. **Seat 9 does not re-implement or re-tune these
> four constants here; they have exactly one definition, in SPEC-001.**

### 3.2 The family estimator — R-6 to R-10 · *this is the anti-gaming construction*

> **R-6 · New function `stats.family_variance_inflation(trial_series, candidate_returns, *,
> label_span=1, m_min=8) -> VIFResult`.**
>
> ```
> v_cand   =  variance_inflation(candidate_returns, label_span=label_span)
> usable   =  [ variance_inflation(s, label_span=label_span) for s in trial_series
>               if that result is eligible ]
> if len(usable) >= m_min:
>     v_fam    =  median( u.vif_gate for u in usable )
>     vif_gate =  max( v_cand.vif_gate , v_fam )
>     source   =  "max(candidate, family-median)"
> else:
>     vif_gate =  v_cand.vif_gate
>     source   =  "candidate-only"
> ```
>
> **`max`, then `median`, and both choices are load-bearing.**
>
> | Choice | What it defends against | What the alternative would do |
> |---|---|---|
> | **`max`** against the candidate's own series | A sponsor advancing the one configuration in the family whose net series happens to be least autocorrelated | Using the family term alone would let the graded series be cleaner than the number grading it |
> | **`median`**, not `max`, across trials | One pathological throwaway trial killing the family | `max` across trials would create **an incentive not to log a trial** — the single worst incentive this firm can create, and disqualifying on its own |
> | **`median`**, not `mean` | Padding the registry with cheap low-`ρ` trials to pull the family term down | A mean is moved by a minority of extreme values; but note the padding attack is already closed by R-8 regardless of the statistic |
>
> `median` of an even-length sample is the arithmetic mean of the two central order
> statistics (numpy default). Stated so it is not a discretionary choice.

> **R-7 · The floor at `1.0` is applied inside `variance_inflation`, per series, before any
> aggregation.** A median of already-floored values is itself `≥ 1`. **The floor is never
> applied only at the end**, because a per-series value below 1 entering a median would let
> one mean-reverting trial buy a discount for the family.

> **R-8 · The padding attack, closed, and the closure stated as a property.**
> **`vif_gate ≥ v_cand.vif_gate` always, for any `trial_series` whatsoever.** No number of
> logged trials, of any construction, can drive the graded VIF below the VIF of the series
> actually being graded — whose `sha256` is on the report. **`test_vif_11` asserts this
> against 500 adversarially-constructed trial sets, including sets of pure i.i.d. noise, sets
> of length-33 minimal series, and empty sets.** This is the single most important property
> in §3 and it is the one a future change is most likely to break.

> **R-9 · Trials excluded from the family term, and the dilution attack.** A trial series
> failing R-5's guards is excluded from the median and counted in `n_series_excluded`.
> **If `n_series_excluded > 0.25 · (n_series_used + n_series_excluded)`, `eligible = False`**
> with a note naming the count, and the criterion is INSUFFICIENT-DATA and escalated to me.
>
> *Why.* Without this, a sponsor logs a few dozen 20-bar trials, each individually excluded,
> and the family term either vanishes or is computed on an unrepresentative remainder. With
> it, the dilution triggers a refusal instead of a discount. **Excluded trials still count in
> full toward `N`** — there is no construction in which logging a trial reduces the
> denominator. `0.25` is `[inferred]`.

> **R-10 · The family term reads full-length trial series, never
> `TrialRegistry.returns_matrix`.** `returns_matrix` truncates every column to the shortest
> common length [measured — `registry.py:555–577`], so **one 20-bar logged trial truncates
> the entire family's matrix to 20 bars.** Consumed here, that would drop every series below
> R-5's `T ≥ 32` floor and evaporate the family term — a one-line attack. Seat 9 adds
> **`TrialRegistry.trial_returns(family) -> list[np.ndarray]`**, transitive across the
> predecessor chain in the same way `returns_matrix` is, returning each series at its own
> full length. **This is new registry capability and it is required, not optional.**
>
> **The same truncation silently degrades PBO/CSCV today** and is filed as **I-062**; it is
> a pre-existing defect this clause discovered and does not repair.

### 3.3 Zero trials, too few trials, instability — R-11 to R-14

> **R-11 · Zero logged trials ⇒ `source = "unmeasurable"`, `eligible = False`, and both the
> length criterion (M-7) and the DSR criterion (D-8) are INSUFFICIENT-DATA.**
> There is no fallback to `VIF = 1`. **A VIF of 1 is not a neutral default — it is the
> permissive assumption this document exists to remove**, and defaulting to it on the
> families with the least evidence would put the defect back exactly where it does the most
> damage. `n_logged == 0` already draws INSUFFICIENT-DATA on the trial-count criterion, so
> no Gate verdict changes; the criterion faces now state the true reason.
>
> **`evaluate_gate1` still runs to completion and still returns a report.** It does not
> raise. A Gate evaluation that crashes teaches nothing; one that returns INSUFFICIENT-DATA
> with a reason on three criterion faces teaches exactly what is missing.

> **R-12 · Too few logged trials: `1 ≤ len(usable) < m_min = 8` ⇒ `source =
> "candidate-only"`, and the report says so on its face.** The candidate term alone is a
> valid, conservative estimate — R-8 guarantees it is the floor in every case — but it is a
> single series and the report must not present it as a family measurement.
>
> **Why `m_min = 8` and not 32.** §2.4 of Ruling 004 sets `m ≥ 32` for `σ_SR`, because
> `σ_SR` is a **standard deviation** feeding `E[max]` **linearly**, so its 12.7% relative
> error passes straight into the benchmark [cited — Ruling 004 §2.4]. The family VIF term is
> a **median** feeding a **`max` against an independently sufficient floor**; its error can
> only cost a modest over-tightening, and it cannot be permissive at all. The two numbers
> answer different questions and importing 32 here would be a false economy of consistency.
> `8` is `[inferred]` and I will move it only on a reasoned argument received **before** a
> family's Gate 1, never during one.

> **R-13 · Negative `ρ̂`.** Handled at R-3 (AR(1) term → 1.0) and R-7 (floor → 1.0). The
> family receives no credit. `rho_hat` is still reported **unclipped and signed** so the fact
> is visible: a report that showed `VIF = 1.000` without showing `ρ̂ = −0.31` would conceal
> that a floor bound rather than that the series was clean.

> **R-14 · Unstable `ρ̂`.** Three distinct instabilities, three distinct behaviours, none of
> them silent:
>
> | Condition | Behaviour |
> |---|---|
> | `\|ρ̂\| ≥ 0.97` | `eligible = False`, INSUFFICIENT-DATA, escalated (R-5 / SPEC-001 E-9) |
> | `T < 32` or `T < 10(L+1)` | `eligible = False` for that series; excluded from the family term (R-9); if it is the **candidate**, the whole result is ineligible |
> | `VIF_AR1 > 1.5 · VIF_HAC` | Eligible, graded, **disclosed** on the report face (M-14) — this is misspecification, not instability, and it is the sponsor's to explain |

### 3.4 What ρ̂ is measured **on** — R-15 to R-16

> **R-15 · `ρ̂` is measured on NET return series, post-cost, at the family's own bar
> frequency — never on the signal, the gross return, or the underlying price.** The quantity
> the correction needs is the serial dependence of the series whose mean is being tested,
> and that is the net series. **The funding autocorrelations of 0.829 / 0.802 / 0.493
> [cited — Ruling 003 §3.2] are NOT `ρ̂`.** They are the autocorrelation of an input. A net
> series is `gross + carry − costs` and its price-return component is close to serially
> independent, so the realized `ρ̂` lies below the funding figure and is **family-specific and
> still unmeasured for every family this firm holds.** SPEC-001 §4.3's qualification, which
> the Principal adopted verbatim as the finding's meaning, is binding here: *the ceiling is a
> function of an unmeasured quantity, below 109 at every ρ > 0.* **No document may quote 0.829
> as this firm's `ρ̂`.**

> **R-16 · Bar-frequency evasion is closed, and the correction is what closes it.**
> A sponsor could try to reduce measured `ρ̂` by aggregating to coarser bars. Under the
> **uncorrected** statistic that evasion works, and works enormously. On one AR(1) series,
> ρ = 0.83, T = 2,398, N = 86 [measured]:
>
> | Bars | Realized `SR_ann` | `MinBTL_iid` | `VIF` | `MinBTL_serial` |
> |---|---:|---:|---:|---:|
> | daily | 2.97 | **0.70 y** | 10.57 | 7.36 y |
> | 5-bar | 1.55 | 2.54 y | 3.40 | 8.62 y |
> | 7-bar | 1.39 | 3.18 y | 2.40 | 7.63 y |
>
> **The uncorrected requirement varies by 4.5× with a choice of bar size. The corrected one
> varies by 17%** [measured; the pattern holds across ρ ∈ {0.3, 0.5, 0.83} and three seeds
> each]. The `√ppy` annualization overstates `SR_ann` at fine bars under positive
> autocorrelation by exactly the factor the VIF removes, and the two cancel.
>
> **This inverts Ruling 004 §2.1** — see §6.1. `test_mbs_12` is the acceptance test and it
> asserts a **20% band across 1/5/7-bar aggregation**, which is the measured spread plus
> margin, not a tolerance chosen to be satisfiable. `[inferred — the 20% band]`

---

## 4. MONOTONE-CONSERVATISM, MECHANICALLY ENFORCED · clauses C-1 to C-6

*The Principal's ruling rests on the property that measurement can only tighten. This
section is that property built into the construction rather than stated as an intention. It
is what keeps the ruling out of I-029(d) territory.*

> **C-1 · The property, stated as a theorem the tests check.**
> For every `(N, SR, ppy, span)` and every `vif`:
>
> ```
> (i)   MinBTL_serial(N, SR, ppy, vif)      >=  MinBTL_iid(N, SR, ppy)
> (ii)  max_admissible_trials(span,SR,ppy,vif) <= max_admissible_trials(span,SR,ppy,1.0)
> (iii) DSR_serial(r, N, sigma, vif)        <=  DSR_iid(r, N, sigma)
> (iv)  MinBTL_serial is non-decreasing in vif;  DSR_serial is non-increasing in vif
> ```
>
> **These hold for ALL `vif > 0`, including `vif < 1`.** That universality is the whole
> design: the guarantee must not depend on the estimator producing a value above 1.

> **C-2 · Two independent enforcements, at two different layers, neither removable on the
> argument that the other exists.**
>
> | Layer | Mechanism | Clause | Test |
> |---|---|---|---|
> | **Estimator** | `vif_gate = max(1.0, vif_hac, vif_ar1)`, applied per series before aggregation | R-2, R-7 | `test_vif_05` |
> | **Consumer** | `MinBTL_serial = max(mb_iid, mb_iid·vif)` and `DSR_gate = min(Φ(z/√vif), Φ(z))` | M-2, D-6 | `test_mono_01`–`test_mono_04` |
>
> A single enforcement is a single point of failure. Two enforcements at different layers
> mean a future seat must defeat both, in two files, to make the machinery loosen — and each
> has its own test naming this clause.

> **C-3 · THE STRUCTURAL TEST: the guarantee is verified with a deliberately loosening VIF
> injected.** `test_mono_03` calls `min_backtest_length_years_serial(..., vif=0.25)` and
> `deflated_sharpe_ratio_serial(..., vif=0.25)` — values the estimator can never produce —
> and asserts the outputs are **exactly** the uncorrected ones. `test_mono_04` sweeps
> `vif ∈ {0.01, 0.1, 0.5, 0.9, 0.999}` and asserts no loosening at any of them.
>
> **This is why M-2 and D-2 take `vif` as an explicit required argument rather than
> computing it internally.** An estimator that computed its own VIF could not be tested this
> way, and the guarantee would rest on reading the estimator's code correctly. **Separating
> estimation from consumption is what makes monotone-conservatism checkable rather than
> asserted, and Seat 9 may not collapse the two for convenience.**

> **C-4 · The regression test that fails if a future change breaks the property.**
> `test_mono_05` is a randomized property test: 2,000 draws of
> `(N ∈ [2, 10⁶], SR ∈ (0, 5], ppy ∈ {12, 52, 252, 365}, vif ∈ (0, 50])` from a **fixed
> seed**, asserting (i), (ii) and (iv) on every draw. `test_mono_06` does the same for (iii)
> over 2,000 draws of `(returns, N, σ_SR, vif)` including negative-`z` cases, which are the
> ones D-6 exists for.
>
> **This test is the clause. If a future change makes it fail, that change is a threshold
> movement under Charter §2 regardless of how it is described, and it interrupts the
> Principal.** Seat 9 does not modify `test_mono_*` under any circumstances; a `test_mono_*`
> failure is escalated to me in writing, per Ruling 004 §11's standing term.

> **C-5 · What this construction is NOT.** It is not I-029(d) — a threshold moved to
> accommodate a result — and the distinction is mechanical, not rhetorical. **I-029(d) moves
> a constant in the permissive direction after seeing an outcome. This construction seals a
> function in advance whose every argument can only move the requirement in the tightening
> direction.** The Principal's own framing: *"it is the `min(t_NW, t_raw)` construction
> extended to `N`."` The extension is exact — E-8 floors a graded statistic at its
> uncorrected value; M-2 and D-6 do the same for two more.

> **C-6 · The one asymmetry this creates, named rather than discovered.** Because measurement
> can only tighten, a family's admissible ceiling can **fall** between Gate 0 and Gate 1 and
> can never rise. **A sponsor cannot plan against the Gate 0 ceiling as a guarantee.** §5 is
> the semantics of that, and §5's answer to retroactive inadmissibility is *yes*.

---

## 5. EVALUATION-TIME SEMANTICS AND RETROACTIVE INADMISSIBILITY · clauses V-1 to V-9

> **V-1 · "At evaluation time" means: every `evaluate_gate1` and `evaluate_gate2` call,
> recomputed from the registry as it stands at that call.** The VIF is not cached, not
> carried forward from a prior evaluation, and not read from a sealed field. It is computed
> once per call (D-7) from `TrialRegistry.trial_returns(family)` plus the candidate series
> passed to that call, and the value used is printed on the report face (M-10).

> **V-2 · The report is the audit trail of the measurement.** Two evaluations of the same
> family at different times may use different VIFs, because the registry grew between them.
> Both reports state their own VIF, their own `n_series_used`, and their own registry `N`.
> **Neither supersedes the other and neither is amended.** Precedent: A1 — the report is
> generated by the harness and written unedited.

> **V-3 · `N > N_max` is a FAIL, not INSUFFICIENT-DATA.** Every input is known: `N` from the
> registry, the span from `oos_index`, the Sharpe from the graded series, the VIF from
> logged trials. The requirement is computed and unmet. **INSUFFICIENT-DATA is for a
> quantity that cannot be established; this one is established and it is not met.** One FAIL
> fails the Gate.

> **V-4 · CAN A FAMILY BE RETROACTIVELY INADMISSIBLE? YES. This is the case the firm will
> actually hit and it is answered here rather than at the moment it is expensive.**
>
> A family admitted at Gate 0 on a ceiling computed at `VIF = 1`, which then measures
> `VIF > 1` at Gate 1 with `N` already spent above the corrected ceiling, **fails Gate 1's
> length criterion and the trials cannot be unspent.**
>
> **This is not a threshold moved mid-evaluation, and the distinction matters enough to
> state precisely.** The Charter §4.4 criterion is, and always was, *"backtest length ≥
> MinBTL(N) and ≥ 4 years and ≥ 1 full regime cycle."* `MinBTL` is a function evaluated at
> Gate 1 on measured quantities. What this document changes is that the function now takes a
> measured `ρ̂` where it previously took an unstated assumption of zero. **The sponsor never
> had a guarantee; the sponsor had an assumption that the harness was making silently on the
> sponsor's behalf, in the sponsor's favour.** Removing a silent favourable assumption is not
> retroactive punishment.
>
> **What it is, honestly: a real reduction in the planning value of a Gate 0 ceiling.** I am
> not dressing that up. A sponsor who spent 86 trials against a ceiling of 109 and measures
> `ρ̂ = 0.1` has spent trials that are now inadmissible, and no one told them in advance
> because no one had measured `ρ̂`. **That is a cost the firm bears once, and it is cheapest
> now, when the firm holds zero trials.**

> **V-5 · The four remedies, ranked, and three of them do not work.**
>
> | Remedy | Works? |
> |---|---|
> | **Acquire more calendar span** — wait, or ingest more history | **Yes, and it is the only honest one.** `MinBTL_serial` is fixed; the span grows. §7 prices it for PREREG-002 |
> | **Realize a higher net Sharpe** | **Yes, arithmetically** — `MinBTL ∝ 1/SR²` — but the route to a higher realized Sharpe is more search, which raises `N`, which raises `MinBTL`. It works only if the Sharpe rises *without* new trials, i.e. on new data, which is the first remedy wearing a hat |
> | **Reduce `N`** | **No.** Trials are spent. The registry is append-only |
> | **Open a successor family** | **No.** `n_inherited` carries the spent trials forward transitively and `InheritedCountDoubleCountError` refuses the declaration that would hide them [measured — `registry.py:294–308`]. This route was closed by Ruling 001 §3.3 F4 before this document existed |

> **V-6 · Gate 0's intake ceiling is computed at `VIF = 1` and must be labelled as an upper
> bound, never as a budget.** At intake no trial has a return series, so `ρ̂` is
> unmeasurable — R-11's condition, at the one moment it cannot be repaired. Ruling 004 ML-3's
> intake ceiling check therefore runs at `VIF = 1` and **must** render as:
>
> ```
> Admissible N at intake: <= {n_max_iid} — computed assuming serial independence, which is
> an assumption this firm's data violates. This ceiling is an UPPER BOUND that will be
> re-evaluated at Gate 1 on the family's measured net-return autocorrelation and can only
> fall. It is not a budget.
> ```
>
> **Filed as I-063**, because a structural gap that cannot be closed still has to be
> disclosed at the moment it can mislead.

> **V-7 · A planning `ρ` is declared at Gate 0, is not binding, and is not a threshold.**
> The sponsor states the `ρ` they expect and the intake report prints the ceiling at both
> `VIF = 1` and the planning `VIF`. **The declared value grades nothing** — it is not sealed,
> not compared to the measured value, and no criterion reads it. Its only function is that a
> sponsor who plans at `ρ = 0` has done so **in writing, in advance**, and cannot later
> describe the Gate 1 outcome as a surprise. `[inferred]`

> **V-8 · No evaluation in flight is re-graded, and there are none.** The firm holds **0
> hypotheses, 0 trials, 0 Validation Reports, 0 Gate evaluations** [measured, this session].
> Nothing is retro-fitted; no result changes; no prior artifact is amended. **This is the
> entire reason the correction is cheap today and the entire reason it is being made today.**
> Identical in form and reason to SPEC-001 E-15.

> **V-9 · There is no transition period and no dual-threshold grace window.** The corrected
> MinBTL and the corrected DSR are the graded figures from the moment they merge. The i.i.d.
> figures are reported permanently — not for a transition, but because **a report that hides
> the size of its own correction cannot be audited.**
## 6. What survives of RULING-004's numbers
## 7. What this does to PREREG-002
## 8. Mechanical vs. routed-back
## 9. Leakage audit
## 10. Relation to existing rulings
## 11. Test inventory and the intended red state
## 12. Issues filed
## 13. Addressed to the Principal
