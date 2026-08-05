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
## 6. WHAT SURVIVES OF RULING-004's NUMBERS

*Every number in Ruling 004 §2 was computed under the uncorrected treatment. This section
goes through them one at a time. Two survive verbatim, one survives as an upper bound, one
is inverted, and one conclusion collapses much faster than anyone has assumed.*

### 6.1 §2.1 — "MinBTL is frequency-invariant" · **the algebra survives; the conclusion was false and is restored only by the correction**

§2.1 proves `MinBTL_years = E[max Z_N]²/SR_ann²`, that `ppy` cancels exactly, and concludes:
*"a family cannot buy length by sampling more finely, and a seat that proposes hourly bars
to 'get more observations' should be shown this line"* [cited].

**The algebra is correct and unchanged. The conclusion drawn from it was wrong, and it was
wrong in the permissive direction.** `ppy` cancels, but `SR_ann` is **not** frequency-
invariant when returns are autocorrelated — the `√ppy` annualization overstates the Sharpe at
fine bars by exactly the factor the VIF removes. On one AR(1) series, ρ = 0.83, N = 86
[measured — R-16]:

| Bars | `SR_ann` | `MinBTL_iid` | `MinBTL_serial` |
|---|---:|---:|---:|
| daily | 2.97 | **0.70 y** | 7.36 y |
| 5-bar | 1.55 | 2.54 y | 8.62 y |
| 7-bar | 1.39 | 3.18 y | 7.63 y |

**Under the uncorrected statistic, moving from weekly to daily bars cuts the required
backtest length by 4.5× on the same data — the exact evasion §2.1 declared impossible.**
Under the correction the requirement varies by 17%. §2.1's *conclusion* is therefore not
something that survives the correction; it is something the correction **creates**. Filed as
**I-061**, and it is the strongest single argument for this specification: the correction
does not merely tighten a number, it restores a property the firm believed it already had.

### 6.2 §2.2 — the `N` = 109 headline and the admissible-search table · **survives only as the `ρ = 0` row, and is now an upper bound**

`MinBTL(109, 1.0) ≤ 6.571 < MinBTL(110, 1.0)` is reproduced exactly this session
[measured]. **The arithmetic stands. Its status changes.**

109 is `max_admissible_trials(6.571, 1.0, vif=1.0)` — the ceiling **under an assumption the
firm has now formally acknowledged its own data violates**. Under M-5 the binding figure is
`N_max = min(109, ceiling at ρ̂)`, and the second term is below the first at every ρ̂ > 0
[measured — the ceiling falls below 109 at ρ̂ > 0.001]:

| ρ̂ | VIF | `N_max` | vs. 109 |
|---:|---:|---:|---|
| 0.00 | 1.000 | **109** | — |
| 0.02 | 1.041 | 95 | −13% |
| 0.034 | 1.070 | 86 | −21% |
| 0.05 | 1.105 | 77 | −29% |
| 0.10 | 1.222 | 55 | −50% |
| 0.20 | 1.500 | 31 | −72% |
| 0.30 | 1.857 | 19 | −83% |
| 0.493 | 2.945 | 8 | −93% |
| 0.829 | 10.696 | 2 | −98% |

[measured — reproduces SPEC-001 §4.2 exactly, which is what M-13(1) requires]

**The whole of §2.2's table — every span × Sharpe cell — is now the `VIF = 1` row of a
three-dimensional surface.** Ruling 004 §2.2's second reading ("on the firm's best data
surface the entire admissible search space at the Gate 1 Sharpe floor is 109") must be read
as **"is at most 109."** `[cited — the Principal's own qualification, adopted verbatim: "the
ceiling is a function of an unmeasured quantity, below 109 at every ρ > 0."]`

§2.2's **third** reading — that MinBTL is weak precisely against a large search that produced
a high in-sample Sharpe, because the ceiling explodes with realized Sharpe, and that DSR is
what bites there through σ_SR — **survives intact and unweakened.** The VIF multiplies
MinBTL at every Sharpe, so it shifts the explosion without removing it. That finding is still
correct and is still the reason ML-16 exists.

### 6.3 §2.3 — the additive term 0.642 · **the number moves; the finding it supports survives verbatim**

§2.3's closed form is `required SR_ann ≈ E[max Z_N]·σ_SR_ann + 0.642`, the additive term
being `1.645·√(365/(T−1))` at `T = 2,398` [cited]. Under D-2 the `√(T−1)` becomes
`√((T−1)/VIF)`, so **the additive term is multiplied by `√VIF` and nothing else is touched**
[measured]:

| ρ̂ | 0.0 | 0.1 | 0.2 | 0.3 | 0.5 | 0.829 |
|---|---:|---:|---:|---:|---:|---:|
| additive term | **0.642** | 0.710 | 0.786 | 0.875 | 1.112 | **2.099** |

**Ruling 004 §2.3's entire table shifts upward by `0.642(√VIF − 1)`** — by 0.07 Sharpe at
ρ̂ = 0.1, by 1.46 at ρ̂ = 0.829. Every cell in it is the `ρ = 0` row. The 2.099 figure quoted
in the dispatch is confirmed [measured].

**But §2.3's actual finding survives verbatim, and this is worth stating precisely because
it is the load-bearing conclusion of the whole ruling.** §2.3 concludes that *"σ_SR is
roughly three times more load-bearing than `N` over the ranges an ML family will actually
occupy."* That comparison is between an `N`-sweep (0.56 Sharpe from N = 10 to 100,000 at
σ_SR = 0.20) and a σ_SR-sweep (1.96 Sharpe from 0.20 to 0.80 at N = 1,000). **The serial
correction multiplies only the additive term, which appears in neither difference — it
cancels out of both sweeps exactly.** The 0.56-vs-1.96 comparison is unchanged at every VIF.
**ML-16 and the dispersion sample rest on a finding the correction does not touch.**

### 6.4 §2.4 — the `m ≥ 32` dispersion floor · **arithmetically unaffected, and now in direct collision with the ceiling**

§2.4's relative-standard-error table (`1/√(2(m−1))`: 12.7% at m = 32) contains no serial
content and is unaffected. **The collision is new and it is severe.**

The dispersion sample is *mandatory* under ML-16 and costs 32 trials of the ceiling. At net
SR 1.0 on 6.571 years:

- **at ρ̂ > 0.197 the ceiling falls below 32** [measured — crossing at 0.1969], so **the
  mandatory dispersion sample alone exceeds the entire admissible search space.** The family
  is inadmissible before it searches once.
- The full ML-3 obligation stack — dispersion 32, ±50% grid 25, seed ensemble 10,
  walk-forward 10, falsifier legs 2–3, **total ≈ 79.5** [cited — Ruling 004 ML-3] — exceeds
  the ceiling at **ρ̂ > 0.045** [measured].

Neither number moves in response. **A family that cannot afford its own diagnostics has not
discovered a problem with the diagnostics; it has discovered that this firm's data cannot
support a fitted family at that persistence.** Filed as **I-060**.

### 6.5 ML-3 — "roughly thirty configurations of genuine search" · **survives only at ρ̂ = 0, and reaches zero at ρ̂ ≈ 0.045**

This is the conclusion the dispatch names and it is the one that collapses fastest
[measured, obligations = 79.5]:

| ρ̂ | `N_max` | Remaining for genuine search |
|---:|---:|---:|
| 0.00 | 109 | **≈ 30** *(Ruling 004's headline)* |
| 0.02 | 95 | ≈ 16 |
| 0.034 | 86 | ≈ 7 |
| **0.045** | **80** | **0** |
| 0.10 | 55 | **−25 — the obligations alone are inadmissible** |
| 0.20 | 31 | −49 |

> **"Roughly thirty configurations" is a `ρ̂ = 0` statement. The honest restatement is: at
> most thirty, reaching zero at a net-return autocorrelation of 0.045 — a level far below
> anything this firm has measured on any related series.**

Ruling 004's own framing — *"Not thirty thousand. Not three hundred. Thirty."* — needs one
more clause: **and quite possibly none.** ML-4's foreclosure of large-space ML methods is
strengthened, not weakened; ML-3's *enforcement* blocker (no ML family may be sealed as
Gate-1-eligible until `n_declared_fits` reaches the denominator) remains in force and now has
a second, independent reason to remain in force.

### 6.6 Summary table

| Ruling 004 item | Status |
|---|---|
| §2.1 algebra (`ppy` cancels) | **Survives exactly** |
| §2.1 conclusion (cannot buy length by sampling finely) | **Was false under the uncorrected statistic; created by this correction** (I-061) |
| §2.2 `N` = 109 | **Survives as `max_admissible_trials(6.571, 1.0, vif=1.0)`; is an upper bound, not a budget** |
| §2.2 full span × Sharpe table | **Survives as the `VIF = 1` slice** |
| §2.2 third reading (MinBTL weak at high SR; DSR bites via σ_SR) | **Survives intact** |
| §2.3 additive term 0.642 | **Becomes `0.642·√VIF`; 2.099 at ρ̂ = 0.829 confirmed** |
| §2.3 finding (σ_SR ≈ 3× more load-bearing than `N`) | **Survives verbatim — the correction cancels out of both sweeps** |
| §2.4 `m ≥ 32` and its RSE table | **Unaffected arithmetically; collides with the ceiling at ρ̂ > 0.197** (I-060) |
| ML-3 "≈ 30 configurations" | **`ρ̂ = 0` statement only; reaches zero at ρ̂ ≈ 0.045** |
| ML-4 foreclosure of large-space ML | **Strengthened** |
| §2.2 reconciliation with PREREG-002 §10.4's 110 → 109 | **Unaffected; both are `VIF = 1` figures** |

**No clause of Ruling 004 is amended by this document.** Five numbers in it are re-scoped as
`VIF = 1` special cases, one conclusion (§2.1) is corrected, and the two findings the ruling
is actually built on — §2.2's third reading and §2.3's σ_SR result — survive untouched.
## 7. WHAT THIS DOES TO PREREG-002

*I was explicitly not asked for a specification that lets this family survive. It probably
does not. Here is the arithmetic, and here is the number the Principal's own stated trigger
gets wrong.*

### 7.1 The seal, in the form the Principal ruled it

PREREG-002 §10.4 seals, per the ruling recorded at §0.2:

```
N_max  =  min( 109 ,  max_admissible_trials(span, SR_realized, ppy, vif = VIF_gate(ρ̂)) )
```

with `VIF_gate` measured by `stats.family_variance_inflation` (R-6) from
`TrialRegistry.trial_returns(F-002)` and the graded candidate series, at every
`evaluate_gate1` call (V-1). **`109` is not a constant in that expression that happens to
bind; it is `max_admissible_trials(6.571, 1.0, vif=1.0)` and it is the first argument of a
`min` that M-5 makes explicit in code precisely so the seal and the source agree** (M-4, M-5).

The declared `N` = 86 [cited — PREREG-002 §10.4] is graded against `N_max` through Charter
§4.4's length criterion, not against 109 directly.

### 7.2 **The Principal's stated trigger is not tight enough. The binding threshold is ρ̂ ≈ 0.034, not 0.1.**

> *"if ρ̂ measures ≥ 0.1, the admissible ceiling falls below the declared `N` = 86…"*

That is true but it understates the tightness by roughly **3×**. The exact arithmetic
[measured]:

```
MinBTL(86, 1.0)                    =  6.1359 years
available span                     =  6.571 years          [cited — PREREG-002 §8]
maximum admissible VIF             =  6.571 / 6.1359  =  1.0709
binding AR(1) ρ̂                    =  (1.0709 − 1)/(1.0709 + 1)  =  0.0342
```

> **PREREG-002 survives Gate 1's length criterion only if the family's measured net-return
> VIF is at most 1.071 — an AR(1) autocorrelation of 0.034. Not 0.1. At ρ̂ = 0.1 the ceiling
> is 55 and the family is 31 trials over, not marginally over.**

I am reporting this because a ruling's stated consequence will be relied on, and this one is
loose in the permissive direction. **It moves the trigger toward tightening, which is within
my authority to correct without a Principal act, and I am recording it rather than exercising
it silently.** §13 addresses it to him.

### 7.3 What survival would require — the four routes, priced

The margin is 0.435 years (6.571 − 6.136), or 7.1% of the required length. Priced against
`ρ̂` [measured]:

| ρ̂ | VIF | Span needed at `N` = 86, SR 1.0 | Extra span | Or: net `SR_ann` needed on 6.571 y |
|---:|---:|---:|---:|---:|
| 0.034 | 1.071 | 6.568 y | — | 1.000 |
| 0.05 | 1.105 | 6.782 y | +0.21 y | 1.016 |
| 0.10 | 1.222 | 7.499 y | **+0.93 y** | 1.068 |
| 0.15 | 1.353 | 8.302 y | +1.73 y | 1.124 |
| 0.20 | 1.500 | 9.204 y | +2.63 y | 1.184 |
| 0.30 | 1.857 | 11.395 y | +4.82 y | 1.317 |
| 0.50 | 3.000 | 18.408 y | +11.84 y | 1.674 |

**Reading the two right-hand columns is the whole of "what would have to be true to pass."**

1. **More calendar span.** At ρ̂ = 0.10 the family needs **11 more months** of history. That
   is the only honest remedy (V-5) and it is *reachable by waiting* — which makes ρ̂ ≤ ~0.15 a
   PARK, not a kill. **Below ρ̂ ≈ 0.3 this family is a waiting problem, not a dead one.**
2. **A higher realized net Sharpe.** At ρ̂ = 0.10 a realized net `SR_ann ≥ 1.068` clears it on
   the span already held. **This is a genuine route and it is the one I expect a sponsor to
   reach for — and it is trapped.** Raising the realized Sharpe by searching raises `N`,
   which raises `MinBTL`, which raises the Sharpe required. It works only if the Sharpe rises
   without new trials, i.e. on data not yet seen, which is route 1 wearing a hat (V-5).
3. **Reduce `N` below 86.** Not available. Trials are spent and the registry is append-only.
4. **A successor family.** Not available. `n_inherited` carries the count forward transitively
   and `InheritedCountDoubleCountError` refuses the declaration that would hide it
   [measured — `registry.py:294–308`].

### 7.4 The verdict shape, pre-committed here so it is not negotiated later

Pre-committing the verdict rule before the measurement exists is Ruling 001 §4.4's own
device, and it is used here for the same reason.

| Measured ρ̂ (or VIF) | `N_max` | Verdict on the length criterion, pre-committed |
|---:|---:|---|
| ρ̂ ≤ 0.034 (VIF ≤ 1.071) | ≥ 86 | **PASS**, if every other §4.4 criterion passes |
| 0.034 < ρ̂ ≤ 0.15 | 41–85 | **FAIL on length.** Remedy is calendar span; ≤ 11 months at ρ̂ = 0.1. **PARK, re-evaluate on more history** |
| 0.15 < ρ̂ ≤ 0.30 | 19–41 | **FAIL on length.** Remedy is 1.7–4.8 more years. PARK is nominal; this is a kill in practice |
| ρ̂ > 0.30 | ≤ 19 | **FAIL on length. Kill.** The family spent 86 trials into a space that admits fewer than 19 |
| \|ρ̂\| ≥ 0.97, or `n_logged` = 0, or R-9's exclusion rate | — | **INSUFFICIENT-DATA**, escalated to me. **Never PASS** |

**None of these is a malfunction and I will not describe any of them as one.** The Principal
has already ruled the frame: *"a PARK or kill on measured ρ is a terminal verdict under §1,
not a malfunction."*

### 7.5 The one thing that is genuinely unknown, stated so it is not read as a prediction

**Nothing above is a forecast of PREREG-002's fate, because ρ̂ has never been measured for
this family and cannot be until it logs trials.** The autocorrelations of 0.829 / 0.802 /
0.493 are **funding** autocorrelations [cited — Ruling 003 §3.2], and R-15 forbids quoting
them as ρ̂. A net series is `gross + carry − costs`; its price-return component is close to
serially independent and its carry component is not, so the realized ρ̂ depends on the
position-weighted mix and lies somewhere below the funding figure. **It could plausibly land
anywhere in [0.0, 0.5].** Half that interval is a PASS-or-park and half is a kill.

**The honest summary is the Principal's own sentence, and I have nothing to add to it: the
ceiling is a function of an unmeasured quantity, below 109 at every ρ > 0.** What this
document adds is that the quantity is now **measurable, measured automatically, and measured
at the moment it grades** — and that PREREG-002's margin against it is **0.435 years, 7.1%,
and an AR(1) ρ̂ of 0.034.**

### 7.6 Effect on the seal itself

**No binding field of PREREG-002 is amended by this document, and none needs to be.**
`n_inherited`, `trial_budget` and the declared `N` = 86 are unchanged; the seal's
`prereg_sha256` is untouched. What changes is that §10.4's ceiling is sealed **as a function
rather than as the integer 109**, exactly as ruled — and a function whose every argument can
only tighten (§4) is not an amendment to the sealed field set. **`verify_prereg(F-002)`
returns `match = True` before and after this specification.**
## 8. WHAT SEAT 9 IMPLEMENTS MECHANICALLY VS. WHAT IT ROUTES BACK

The Charter gives Seat 9 "how to implement a stated requirement" and gives Validation "what
counts as correct." Drawn clause by clause so it is not negotiated at implementation time.

### 8.1 Mechanical — implement as written, no consultation

| Clause | Why it is mechanical |
|---|---|
| **M-1 / D-1** | A prohibition and one pinned pure extraction. `test_dsr_02` is the pin. |
| **M-2 / M-4 / M-5** | Closed-form arithmetic and a bisection with stated brackets. |
| **M-3** | One squaring. Named as the most likely error in the document; `test_mbs_04` pins it. |
| **M-6 / M-7** | One criterion rename, one substitution, one new INSUFFICIENT-DATA branch with the note given verbatim. |
| **M-9 / M-11 / V-8 / V-9** | Statements of fact; nothing to build. |
| **M-10** | Eight report fields plus a render block whose shape is given verbatim. **Not `Criterion` rows.** |
| **D-2 / D-3a / D-8 / D-9** | Closed-form arithmetic, one guard, one rename, one reported diagnostic. |
| **D-6** | One `min`. |
| **R-1 / R-2 / R-3 / R-4** | A frozen dataclass and `max` of two stated terms against a stated floor. |
| **R-5** | **Import** SPEC-001's E-6/E-7/E-9 guards. Do not re-implement, do not re-tune. |
| **R-6 / R-7 / R-8** | `median`, then `max`, in the stated order, with the floor applied per series first. |
| **R-10** | One new registry accessor, transitive in the same way `returns_matrix` already is. |
| **R-11 / R-12 / R-13** | Stated branches with stated `source` strings and stated verdicts. |
| **C-1 … C-3, C-5** | The guards are M-2, D-6, R-2, R-7 — already listed. Nothing further to build. |
| **V-1 / V-2 / V-3** | Recompute per call; do not cache. |
| **V-6** | One render string, given verbatim. |

**Everything in `harness/castellan/` that this dispatch will touch, named exhaustively:**
`stats.py` (one private extraction, four new functions, one new dataclass — no behavioural
edit to any existing function), `registry.py` (one new accessor), `gates.py` (two criterion
renames, one substitution, one new INSUFFICIENT-DATA branch, eight report fields, one render
block). **No other file, and no Charter §4.2 constant anywhere.**

### 8.2 Judgment calls — route back to me before implementing

| Clause | The judgment, and the trigger that would make Seat 9 route it |
|---|---|
| **M-13** — the estimator choice `max(1.0, VIF_HAC, VIF_AR1)` | `[inferred]`, mine, argued in M-12/M-13 against the prewhitened alternative with measurements. **Route back if a real family's HAC and AR(1) terms diverge by more than 1.5× and the Gate verdict turns on the gap** (M-14). That is a finding about the family's label structure, not about the construction, and I want to see it. Do not switch estimators to make something pass. |
| **M-14** — the `1.5` divergence-disclosure threshold | `[inferred]`. Route back rather than adjust. Adjusting it to suppress a disclosure is the Appendix B item 4 failure in its purest form. |
| **D-4** — omitting the serial correction to `denom` | The omission is permissive by ≤ 2.5% of `z` where verdicts turn and up to 19% at VIF = 11 (measured, D-4). **Route back if a family clears the corrected length criterion, is materially non-normal, and lands within 3% of `DSR_MIN`.** I will compute option (b) by hand for that family, on the record. |
| **R-9** — the `0.25` exclusion-rate refusal | `[inferred]`. **Route back if an honest family trips it**; the fix is the family's trial lengths, not the constant. |
| **R-12** — `m_min = 8` | `[inferred]`, and deliberately not Ruling 004 §2.4's 32; the reasoning for the difference is in R-12. **Route back if any test or example the firm actually runs is made `"candidate-only"` by it.** Do not adjust it to change a `source` string. |
| **R-16** — the 20% aggregation band in `test_mbs_12` | `[inferred]`, set from the measured 17% spread plus margin. **If a correct implementation misses it, escalate in writing before touching the test** — that is I-058's lesson and it binds Seat 9 and me equally. |
| **R-10** — `trial_returns` semantics | I have specified transitive-across-the-chain, full length per series. **If making it transitive is expensive, route back — it is not optional, and I would rather rule on the cost than have it silently scoped to one family.** |
| **V-6 / V-7** — Gate 0's intake ceiling and the non-binding planning ρ | The render string is mechanical. **The decision that the planning ρ grades nothing is mine and is not to be made binding by implementation convenience.** A sealed planning ρ would be a threshold set by the sponsor. |

### 8.3 The standing term, restated because it binds me too

Ruling 004 §11's term — *Seat 9 implements against pre-authored tests and escalates rather
than amends* — binds the author as hard as the implementer. **§11.4 of this document is me
discharging it against my own defective test, `test_hac_t17`, which Seat 9 correctly refused
to touch and filed as I-070 instead.** That refusal is the term working, and it is the second
time this sprint the escalation route has caught a Validation-authored test rather than an
implementation (I-058 was the first).

---

## 9. LEAKAGE AUDIT

Run in full, as required on every Validation output. There is no strategy under evaluation
here; the audit's subject is this specification and its tests.

| # | Question | Finding |
|---|---|---|
| 1 | Any field filtering on `event_time` rather than `knowledge_time`? | **N/A.** No field is queried, no data source touched. |
| 2 | Restated fundamentals? | **N/A**, and unchanged: the firm has no PIT fundamentals and cross-sectional fundamental equity work still cannot pass Gate 1 [cited — `CONSTRAINTS.md`]. Nothing here alters that. |
| 3 | Survivorship-contaminated universe? | **N/A.** No universe is constructed. |
| 4 | Retroactive split/dividend adjustment? | **N/A.** No price series is read. A4 untouched. |
| 5 | Same-bar fill? | **N/A.** The engine's `SameBarFillError` guard is not on any path this dispatch modifies. |
| 6 | Standard k-fold where purged k-fold with a 1% embargo was required? | **Closed this sprint, not by this document.** I-051 is closed; `test_cv_purge_embargo.py` is 11/11 [measured, this session]. **This document consumes the same serial-dependence fact from the other side:** the embargo makes folds serially clean, and the VIF makes the *length requirement* serially honest. Both halves of the defect are now addressed. |
| 7 | Parameter chosen at an argmax rather than a plateau centroid? | **No parameter is chosen from a surface here.** The constants I set (`m_min = 8`, the `0.25` exclusion rate, the `1.5` divergence threshold, the 20% aggregation band) are `[inferred]` judgments stated **in advance of any family's result**, not selections off a computed surface. `L` is selected by SPEC-001 E-5's published mechanical rule via a **one-sided `max`** a caller can raise and never lower — the structural opposite of an argmax selection. **`VIF_gate` is itself a `max`, not an argmax: it selects the most conservative of two estimators, not the one that produces the best outcome.** |
| 8 | Was the holdout consulted, in any form, before this evaluation? | **No.** `HoldoutVault.open_once` was not invoked. No vault under `book/vaults/` was read, listed, or decrypted. No passphrase was requested, supplied, or held. This seat holds no holdout plaintext. **Holdout status: LOCKED, unopened, unretired.** |

**Registry state, before and after this dispatch [measured]:** `book/registry.db` — **0
hypotheses, 0 trials, 1 event.** No `open_hypothesis`, no `run_backtest`, no trial logged.
Every registry used by the new tests is `tmp_path`-scoped, as every existing test's is.

**A2 compliance.** No path around `run_backtest` is created. Both items change how a number
the engine already produced is *evaluated*; neither produces a number; neither adds an input
the engine does not already carry. **R-10's `trial_returns` reads trials the engine wrote and
creates no route to write one.**

---

## 10. RELATION TO EXISTING RULINGS, PRE-REGISTRATIONS AND AMENDMENTS

Checked item by item.

| Document | Interaction |
|---|---|
| **Charter §4.2 constants** | **None moved.** `DSR_MIN = 0.95`, `T_STAT_HURDLE = 3.0`, `MIN_YEARS = 4`, `EMBARGO_FRACTION`, `CSCV_PARTITIONS_S` imported, never redefined, and none appears as a parameter. |
| **Charter §4.4, "≥ MinBTL(N)"** | **Now actually enforces what it says.** The criterion text is unchanged; the function evaluated at Gate 1 now takes a measured ρ̂ where it took a silent assumption of zero. |
| **Charter §4.4, DSR ≥ 0.95** | **Threshold unchanged; the statistic compared against it now measures what it claimed to measure.** Precedent and phrasing: the Principal's I-050 ruling. |
| **Charter §4.5 (Gate 2)** | **D-10.** "DSR recomputed with final N" uses the serial construction at the Gate 2 VIF. Reintroducing the i.i.d. DSR at the point real capital is authorized would be the worst placement of the defect. |
| **Amendment A1** | **Strengthened.** `evaluate_gate1` remains the only source of a Validation Report and now embeds eight further fields that cannot be narrated. |
| **Amendment A2 / A4** | **No path around either created** (§9). |
| **Ruling 001 §3.3 F4 / `predecessor_family`** | **Load-bearing here and not amended.** It is what closes V-5's successor-family escape from a spent `N`. |
| **Ruling 001 §4.4** (pre-committed verdict rule) | **Precedent followed.** §7.4 pre-commits PREREG-002's length verdict by measured ρ̂ band, before the measurement exists, for the reason §4.4 gives. |
| **Ruling 002 R1** (required HISTORICAL sentence) | **Precedent followed, not amended.** M-10's and V-6's required sentences are built on R1's logic: a report that omits the limit of its own control will be read as though the control had none. |
| **Ruling 003 §3.2** (funding autocorrelations) | **Cited as evidence that ρ > 0 in this firm's data; explicitly NOT used as ρ̂** (R-15). |
| **Ruling 003 / I-037** (bisection-artifact repair) | **Extended.** M-4's bisection over `N` is monotone by construction because `MinBTL` is monotone in `N`; the fixed-lag discipline E-13 established is inherited wherever a VIF enters a sweep. |
| **Ruling 004 §2.1 – §2.4, ML-3** | **Re-scoped, not amended — §6.** One conclusion (§2.1) corrected; two findings survive verbatim. |
| **Ruling 004 §11 standing term** | **Discharged against my own test** — §8.3, §11.4. |
| **Ruling 004 ML-16 / §2.4** | **Not amended, and now in collision with the ceiling at ρ̂ > 0.197** (I-060). Neither number moves in response. |
| **Ruling 004 ML-26** (overlapping labels, effective sample size) | **Partially mechanised.** ML-26 asked for an effective-sample-size treatment for overlapping labels; `T_eff = (T−1)/VIF + 1` (D-9) is that quantity, computed rather than asserted, and the E-5 lag floor at `label_span − 1` is what makes the VIF see the overlap. |
| **VALIDATION-SPEC-001 (I-050, I-051)** | **Hard dependency, not amendment — M-0.** This document consumes E-2, E-3, E-5, E-6, E-7, E-8, E-9 and re-implements none of them. I-051 is closed; I-050 closes when `test_hac_t17` greens (§11.4). |
| **PREREG-002** | **No binding field amended; `prereg_sha256` untouched; `verify_prereg` returns `match = True` before and after** (§7.6). §10.4's ceiling is sealed as a function per the Principal's ruling. |
| **I-052 / I-053** | **Not touched, not blocked, not resolved.** `label_span` reaches R-2 through SPEC-001 E-11's keyword, deliberately not through a registry field, for E-11's stated reason. When I-052 lands the keyword becomes a fallback — a later dispatch, not specified here. |
| **I-029(d)** | **Explicitly distinguished — C-5.** The distinction is mechanical, not rhetorical. |

**Nothing in this specification contradicts any existing ruling or pre-registration.** One
conclusion within a prior Validation artifact of my own is corrected (Ruling 004 §2.1, filed
as I-061) and one of my own acceptance tests is repaired (`test_hac_t17`, §11.4).
## 11. TEST INVENTORY AND THE INTENDED RED STATE

### 11.1 Counts

**Baseline at the start of this dispatch: 1 failed, 187 passed of 188** [measured] — Seat 9
having implemented SPEC-001 in full, with the single red test being mine (§11.4).

**After this dispatch: 42 failed, 192 passed of 234** [measured]. **46 tests added, all in
new files.**

| File | Tests | Red today | Green today | Drives |
|---|---:|---:|---:|---|
| `harness/tests/test_minbtl_serial.py` | 13 | 11 | 2 | M-1 … M-14, R-15, R-16 |
| `harness/tests/test_vif_estimator.py` | 16 | 15 | 1 | R-1 … R-16 |
| `harness/tests/test_dsr_serial.py` | 10 | 9 | 1 | D-1 … D-10 |
| `harness/tests/test_monotone_conservatism.py` | 7 | 7 | 0 | **C-1 … C-6** |
| **Total added** | **46** | **42** | **4** | |

**The four green-today tests are guards, not drivers, and must still pass afterwards:**

| Test | Guards |
|---|---|
| `test_mbs_05_min_backtest_length_years_is_not_edited` | M-1 — the correction must not mutate the existing function |
| `test_mbs_13_prereg002_binding_rho_is_0034_not_0100` | §7.2 — pins the arithmetic that corrects the Principal's stated trigger, so it cannot drift back |
| `test_vif_16_returns_matrix_truncation_is_the_defect_r10_avoids` | I-062 — documents the pre-existing truncation defect deliberately, so R-10's reason survives |
| `test_dsr_02_published_dsr_is_unchanged_by_the_extraction` | D-1 — pins `deflated_sharpe_ratio` against an independent restatement across 200 randomized inputs, so the authorized extraction cannot change behaviour |

### 11.2 The floor

**The floor rises from 187 to 188 immediately (§11.4 closes the outstanding red), and to
234 once this specification is implemented.** `188 + 46 = 234`. **No existing test may be
deleted, weakened, or re-scoped.** The only edit to an existing file authorized by this
document is the `test_hac_t17` fixture and bracket repair in §11.4, which adds assertions and
removes none.

**Reproduction:**

```
python3 -m pytest harness/tests -q
# expect: 42 failed, 192 passed

python3 -m pytest harness/tests/test_minbtl_serial.py harness/tests/test_vif_estimator.py \
                  harness/tests/test_dsr_serial.py harness/tests/test_monotone_conservatism.py -q
# expect: 42 failed, 4 passed
```

Every missing capability is probed through a helper that calls `pytest.fail` naming the
clause it waits on, so each failure states its own clause rather than producing an
import-time collection error. All four files are importable today and stay importable.

### 11.3 Partition — the files are independently closeable

| File green | Consequence |
|---|---|
| `test_minbtl_serial.py` + `test_vif_estimator.py` | **I-057 Item 1 (MinBTL) closes** |
| `test_dsr_serial.py` | **I-057 Item 2 (DSR) closes** |
| `test_monotone_conservatism.py` | **Neither closes without it.** C-4 is the property that makes the Principal's ruling sound; a MinBTL correction that ships without it has shipped the number and not the guarantee |
| `test_vif_estimator.py` alone | **I-062 does not close** — R-10 routes the VIF around the truncation defect; it does not repair PBO |

**`test_monotone_conservatism.py` is not partitionable and not optional.** If Seat 9's
dispatch greens the arithmetic and not the property tests, **I-057 stays open** and I will say
so.

### 11.4 Corrections to my own pre-authored tests — the standing term, discharged twice

Ruling 004 §11's term is that Seat 9 implements against pre-authored tests and **escalates
rather than amends**. It binds the author as hard as the implementer. It fired twice this
dispatch, once in each direction, and both are recorded here rather than fixed silently.

**(a) `test_hac_t17` — escalated by Seat 9 as I-070, repaired by me. I-070 CLOSES.**

The defect was mine. The draft reused `test_hac_t16`'s `mu = 0.0035, sd = 0.01` fixture
against the **production default bracket** `(0, 2000)` bps/yr. A 2000 bps/yr shift is
`5.48e-4` per bar against a mean of `3.5e-3`: it moves the corrected `t` from 6.488 to 5.788
and the uncorrected `t` from 18.870 to 16.835 [measured]. **Neither crosses 3.0**, so
`carry_breakeven_bps_annual` returned its bracket ceiling through the documented
`t_hi >= hurdle → return hi` branch and the assertion compared 5.788 against 3.0.
**Seat 9 is right that no correct estimator could have satisfied it.**

Repaired with two changes, and **the second is the actual repair**:

1. `sd = 0.002, mu = 0.0004, seed = 6` puts both breakevens strictly inside the bracket —
   corrected **686** bps/yr, uncorrected **1808** [measured].
2. An explicit `bracket=(0, 3000)` **plus interiority assertions on both returned values.**
   A bisection that returns a bracket endpoint has measured nothing, and **the absence of
   that check is what let the defect through silently.** The fixture change makes this test
   pass; the interiority assertion is what stops the next one failing the same way.

`test_tstat_hac.py` is now **17/17** [measured]. **I-070 closes, and I-050 closes with it.**

**(b) `test_vif_04` — caught by me, pre-implementation, at zero cost.**

The draft asserted `vif_hac > 1.5` on a constructed `x_t = e_t + e_{t−2}` series (true
VIF = 2.0) at `label_span = 3`. **A correct implementation recovers 1.4256 there** [measured
against a reference implementation of R-2 built this session]. At `label_span = 3` the E-5
lag floor is 2 and the Bartlett weight on the lag-2 autocovariance is only `1 − 2/4 = 0.5`;
the kernel cannot reach 2.0 at that truncation. **This is I-058's defect exactly, and the
dangerous branch is the same one:** the cheapest route to green would have been for Seat 9 to
abandon the Bartlett kernel. Corrected pre-implementation to `label_span = 8`, where a
correct implementation recovers **1.6847** [measured], and the reason is written into the
test's own docstring so it cannot be reverted by someone re-reading only the clause.

**The process commitment I made at I-058 — that this seat numerically verifies every
pre-authored tolerance in the session that authors it — was honoured.** Every tolerance in all
46 tests was checked against a reference implementation of R-2/R-6 and against reference
constructions of M-2, M-4, D-2 before this document was finalized; the two property tests
were additionally verified to have **zero violations across 2,000 draws each** and to run in
4.1 s and 2.4 s [measured]. **One tolerance failed that check. It was the one above.**
## 12. ISSUES FILED

Numbered from the range allocated to this seat, **I-060 – I-069**. Five taken; five unspent.

| # | Severity | Subject | Interrupt? |
|---|---|---|---|
| **I-060** | **HIGH** | Ruling 004 ML-16's mandatory 32-trial dispersion sample and the corrected MinBTL ceiling are **mutually unsatisfiable at ρ̂ > 0.197**; the full ML-3 obligation stack (≈79.5 trials) exceeds the ceiling at **ρ̂ > 0.045**, so "roughly thirty configurations of genuine search" reaches **zero** there. Neither number moves in response. | **Yes — §6.4, §6.5** |
| **I-061** | MEDIUM | Ruling 004 §2.1's conclusion that a family "cannot buy length by sampling more finely" is **false under the uncorrected statistic** and in the permissive direction: on one ρ = 0.83 series the required length is **0.70 y at daily bars against 3.18 y at weekly**, a 4.5× understatement [measured]. The correction restores the property the firm believed it already had. | No |
| **I-062** | MEDIUM | `TrialRegistry.returns_matrix` truncates every column to the shortest common length, so **one 20-bar logged trial collapses the entire family's return matrix to 20 bars** — silently degrading PBO/CSCV, a Charter §4.4 graded criterion. R-10 routes the VIF around it via a new `trial_returns` accessor; **PBO is left unrepaired by this document.** | No |
| **I-063** | MEDIUM | Gate 0's intake ceiling (Ruling 004 ML-3) is **necessarily** computed at `VIF = 1`, because no trial has a return series at intake. A family can therefore be ADMITTED against a ceiling it cannot meet at Gate 1. **Structural and not closeable**; the only remedy is disclosure, specified as a mandatory render string in V-6. | No |
| **I-064** | LOW | The Principal's stated I-057 consequence — *"if ρ̂ measures ≥ 0.1, the admissible ceiling falls below the declared `N` = 86"* — **understates the tightness by ~3×.** The binding threshold is **ρ̂ ≈ 0.034** (max admissible VIF 1.0709) [measured]. Corrected in the tightening direction, which is within this seat's authority; recorded rather than exercised silently. | **Addressed to the Principal, §13** |

**I-070 is Seat 9's and closes on this dispatch** (§11.4a) — recorded here because the repair
is mine, not because the number is.

**No numbering collision this dispatch.** The allocated range worked: the high-water mark was
I-058 at authoring, Seat 9 took I-070 from its own range concurrently, and neither seat had to
re-read the log before appending. **This is the sixth dispatch of the sprint and the first
without a collision** — the structural fix is doing what I-054 said was needed, and I record
that as evidence for keeping it.

---

## 13. ADDRESSED TO THE PRINCIPAL

Three items. **None of them requires an act from you; two of them you should know before you
next rely on a number, and the third is a request for nothing.**

### 13.1 Your stated trigger on I-057 is loose, and I have tightened it — ρ̂ ≈ 0.034, not 0.1

You ruled: *"if ρ̂ measures ≥ 0.1, the admissible ceiling falls below the declared `N` = 86."*

That is true, but it is **not the threshold**. The arithmetic [measured, and pinned by
`test_mbs_13`]:

```
MinBTL(86, 1.0) = 6.1359 y   ·   available span = 6.571 y
maximum admissible VIF = 1.0709   ⇒   binding AR(1) ρ̂ = 0.0342
```

**PREREG-002's margin is 0.435 years, 7.1%, and an AR(1) ρ̂ of 0.034.** At your stated 0.1 the
ceiling is 55 and the family is **31 trials over, not marginally over.** I have written 0.034
into the specification and pinned it with a test. This moves the trigger toward tightening,
which the I-050 asymmetry places within my authority, so **I have made the change rather than
requesting it** — but a ruling's stated consequence gets relied on, and this one was loose in
the permissive direction. You should know the number you ruled with is not the number that
binds.

### 13.2 This specification probably kills the firm's only family, and I specified it anyway

You said you were not asking for a specification that lets PREREG-002 survive. It does not
obviously let it survive. **The honest position is that nobody knows, because ρ̂ has never been
measured for this family and cannot be until it logs trials** — and R-15 forbids substituting
the 0.829 / 0.802 / 0.493 funding figures for it, because those are the autocorrelation of an
*input*, not of a net return series.

What I can tell you is the shape of the outcome, pre-committed at §7.4 before the measurement
exists:

- **ρ̂ ≤ 0.034** → the length criterion passes.
- **0.034 < ρ̂ ≤ 0.15** → fails on length; the remedy is **calendar span, ≤ 11 months at
  ρ̂ = 0.1**. This is a **PARK**, not a kill.
- **ρ̂ > 0.30** → fails on length; the remedy is 4.8+ more years. **Kill.**

**Half the plausible interval for ρ̂ is a park and half is a kill.** I want to be explicit that
I have not built in any margin to avoid the second outcome, and that where I had a genuine
choice of estimator (M-12, M-13) I chose the one that reproduces the numbers you ruled on
rather than the one most favourable to the family — and recorded the measurements for both.

### 13.3 Two floors that only you can remove, and I am not asking you to

R-3 (the firm takes no credit for negative autocorrelation) and D-6 (`DSR_gate = min(serial,
iid)`) are **deliberate one-sided biases**. Each has a case where it is arguably too
conservative: a genuinely mean-reverting family gets no benefit from that fact.

Removing either is an estimator change that **loosens**, which your I-050 asymmetry places
outside my authority. **I do not recommend removing them and I am not requesting it.** They
are named here only so that a future seat proposing to remove one cannot present it as a
technical correction — **it is a §2 threshold matter and it interrupts you.**

---

*End of specification. `DSR_MIN = 0.95` has not moved. `T_STAT_HURDLE = 3.0` has not moved.
`MIN_YEARS = 4` has not moved. The registry reads 0 hypotheses / 0 trials. The holdout is
LOCKED, unopened, unretired. — Head of Quantitative Validation, 2026-08-04.*
