# VALIDATION-SPEC-001 — Estimator corrections: the serially-corrected t-statistic (I-050) and the CV splitters' purge and embargo (I-051)

**Seat:** Head of Quantitative Validation · **Date:** 2026-08-04 · **Dispatch:** S2-D-010
**Status:** BINDING on implementation. Specification only — no harness code is modified by this document.
**Implementer:** Head of Data & Infrastructure (Seat 9), next dispatch.
**Authority:** Principal's ruling on I-050, 2026-08-04, recorded verbatim in §0.2.
**Baseline suite:** 160 passed [measured, this session]. Floor after this spec's tests land: see §9.

---

## 0. SCOPE, AUTHORITY, AND WHAT THIS DOCUMENT MAY NOT DO

### 0.1 One-sentence statement of each correction

**Item 1 (I-050).** The Gate 1 t-statistic is replaced by a Newey–West HAC t-statistic on
the sample mean, with a Bartlett kernel, an Andrews (1991) AR(1) plug-in lag truncation
floored at the declared label span, taken as the **minimum** of itself and the uncorrected
statistic so the change can never loosen, and reported alongside the uncorrected figure
which is explicitly labelled uncorrected and is not graded.

**Item 2 (I-051).** `walk_forward_windows` acquires a mandatory purge and gap it does not
today possess, and `purged_kfold_splits` acquires a mandatory, must-be-stated
`feature_lookback` that raises the effective embargo to `max(⌈0.01·T⌉, feature_lookback)`.

### 0.2 The Principal's ruling, verbatim, and the asymmetry it attaches

> *"The correction is an estimator being brought into agreement with its own stated
> assumption — the t-statistic claimed serial independence, the data measurably violates it
> (ρ = 0.83 → ~3.3× inflation), and the error runs permissive. Fixing that is Seat 3's
> ownership, and I confirm on the record: this is not a threshold change. `T_STAT_HURDLE =
> 3.0` stands; what changes is that the number compared against it now measures what it
> always claimed to measure. Precedent noted: this is Ruling 003's bisection-artifact
> logic — permissive measurement defects are repaired without ceremony."*

> *"Estimator corrections toward a statistic's stated assumptions belong to Validation and
> need no Principal act. Any estimator change that loosens — relaxes an assumption, widens
> a tolerance, swaps to a more permissive construction — is a §2 threshold matter and
> interrupts, regardless of framing."*

**This second paragraph is load-bearing on the design and it produced clause E-8.** A
Newey–West correction is not unconditionally tightening. When the sample autocorrelation is
negative, `σ̂²_NW < s²` and the corrected `t` is **larger** than the uncorrected one. Shipping
that under Validation's own authority would be an estimator change that loosens, which the
Principal has just placed outside Validation's authority. **E-8 therefore floors the graded
statistic at the uncorrected one.** The firm does not get the benefit of negative
autocorrelation without a Principal act. That is a deliberate, stated, one-sided bias and
it is the price of shipping this without interrupting him.

### 0.3 What this document does not do

- **`T_STAT_HURDLE = 3.0` does not move**, is not referenced as movable, and appears in no
  clause below as a parameter. Neither does any other Charter §4.2 constant.
- **No harness source file is edited by this document.** `harness/castellan/` is untouched.
- **No hypothesis is opened, no trial is registered, no backtest is run.**
  `book/registry.db` reads 0 hypotheses / 0 trials before and after this dispatch.
- **No path around `run_backtest` is created (A2).** Both items change how a number already
  produced by the engine is *evaluated*; neither produces a number, and neither adds an
  input the engine does not already carry.
- **The holdout is not consulted.** No vault is opened; `HoldoutVault.open_once` is not
  invoked; no holdout plaintext is held by this seat.

### 0.4 Whether I-051 rides with I-050 — my judgment, not the CIO's

**They ride together. I concur with the CIO's §3 addition and record why in my own terms,
since the sequencing is mine to refuse.**

Three reasons and one reservation.

1. **Same class.** Both are estimators failing to enforce an assumption they already claim,
   both in the permissive direction, both invisible today because the firm holds zero
   families and zero trials, both certain to fire on the first fitted family. The Principal's
   ruling on I-050 is written as a class rule ("estimator corrections toward a statistic's
   stated assumptions"), not a case rule. I-051 sits inside that class.
2. **Same blast radius.** Both land in the statistical core (`stats.py`, `cv.py`, `gates.py`,
   `carry.py`). Splitting them means two red-then-green cycles over the same files and two
   opportunities for a merge to silently revert the other.
3. **They interact.** The serially-corrected `t` and the embargo are two halves of one
   defect: the firm's returns are autocorrelated, and every construction that assumes
   otherwise is permissive. Correcting one and not the other would leave the report stating
   a serially-honest `t` computed on folds that are not serially clean.

**The reservation, stated because it is real.** I-050 is HIGH and I-051 is MEDIUM. Riding
them together means a Seat 9 dispatch that fails on the MEDIUM item blocks the HIGH one.
**Mitigation, binding:** §9 partitions the tests into two files. If Seat 9's next dispatch
greens `test_tstat_hac.py` and not `test_cv_purge_embargo.py`, **I-050 closes and I-051
stays open.** Neither issue's resolution is contingent on the other's.

### 0.5 Provenance discipline

Every number in this document is tagged `[measured]` (computed this session, reproduction
command in §4.4), `[cited]` (traced to a named prior artifact or external source), or
`[inferred]` (my judgment, and marked as such wherever it sets a constant).

## 1. ITEM 1 — THE CORRECTED t-STATISTIC (I-050) · clauses E-1 to E-16

### 1.1 The defect, restated in one paragraph so the fix can be checked against it

`stats.sr_tstat` returns `mean(r)/std(r, ddof=1) · √T` [measured — `stats.py:51–60`], which
is `√T · r̄ / σ̂` with `σ̂²` estimating only the **contemporaneous** variance `γ₀`. The
statistic's null distribution is `N(0,1)` **only if** `Var(r̄) = γ₀/T`, i.e. only if the
series is serially uncorrelated. Under first-order autocorrelation `ρ`, `Var(r̄) →
(γ₀/T)·(1+ρ)/(1−ρ)`, so the reported `t` exceeds the honest one by `√((1+ρ)/(1−ρ))`. At the
firm's own measured `ρ = 0.829` for BTC daily funding [cited — Ruling 003 §3.2] that factor
is **3.27** [measured]. The direction is permissive against `T_STAT_HURDLE = 3.0`.

### 1.2 The estimator — E-1 to E-5

> **E-1 · `stats.sr_tstat` is not edited.** Its body, signature, docstring and behaviour are
> preserved exactly. It remains the honest *uncorrected* statistic and every existing call
> site that wants the uncorrected figure keeps getting it. A change that redefines
> `sr_tstat` in place would silently alter `test_carry_accounting.py:587,609` and
> `test_harness.py:93` and would make the transition unauditable. **The correction is a new
> function, not a mutation of an old one.**

> **E-2 · New function `stats.sr_tstat_nw(returns, lag)` — exact construction.**
> Let `r` be the input with NaNs dropped, `T = r.size`, `r̄ = mean(r)`, `d = r − r̄`.
> Define the autocovariance at lag `l`, **with divisor `T − 1` at every lag**:
>
> ```
> γ̂(l)  =  ( Σ_{i=l}^{T-1} d_i · d_{i-l} ) / (T − 1)        for l = 0, 1, …, L
> ```
>
> Define the Bartlett-weighted long-run variance:
>
> ```
> σ̂²_NW(L)  =  γ̂(0)  +  2 · Σ_{l=1}^{L}  ( 1 − l/(L+1) ) · γ̂(l)
> ```
>
> Return
>
> ```
> sr_tstat_nw(r, L)  =  r̄ / sqrt( σ̂²_NW(L) / T )
> ```
>
> **Three properties this construction is chosen to have, all of them checkable:**
> (a) at `L = 0` it reduces **exactly** to `sr_tstat(r)` — this is why the divisor is `T − 1`
> and not `T`; with divisor `T` the two differ by `√(T/(T−1))` and the reduction is only
> approximate, which would leave a permanent unexplained wedge in the report [measured: with
> divisor `T`, ratio = 1.000125 at T = 4000; with divisor `T − 1`, difference = 0.0 exactly];
> (b) the Bartlett kernel guarantees `σ̂²_NW ≥ 0`, so the correction can never produce an
> imaginary standard error — the multiplication of every `γ̂` by the positive scalar
> `T/(T−1)` preserves that guarantee;
> (c) it is the direct analogue of the existing statistic — the *same* numerator `r̄`, the
> *same* `√T`, with only the variance estimator replaced. Nothing else moves.
>
> `L` is an integer `≥ 0`. `L ≥ T − 1` is a `ValueError`.

> **E-3 · New function `stats.hac_lag_andrews(returns) -> (lag, rho_hat)` — the lag-selection
> rule, mechanical, no discretion.** Compute the AR(1) coefficient on the demeaned series:
>
> ```
> ρ̂  =  ( Σ_{i=1}^{T-1} d_i · d_{i-1} )  /  ( Σ_{i=0}^{T-2} d_i² )
> ρ̃  =  clip(ρ̂, −0.97, +0.97)                    # for lag selection only
> α(1) =  4·ρ̃²  /  ( (1 − ρ̃)² · (1 + ρ̃)² )
> S_T  =  1.1447 · ( α(1) · T )^(1/3)              # Andrews 1991, Bartlett kernel
> lag  =  floor(S_T)
> ```
>
> Return `(lag, ρ̂)` — the **unclipped** `ρ̂`, because E-9 keys on it.
> `α(1) = 0` (i.e. `ρ̂ = 0`) gives `lag = 0`, which by E-2(a) reduces to the uncorrected
> statistic exactly. That is the correct behaviour: on a serially independent series the
> correction is the identity.

**Why Andrews and not the fixed `⌊4(T/100)^(2/9)⌋` rule of thumb.** The fixed rule returns
`L = 8` on a 2,398-bar sample [measured]. At `ρ = 0.829` a Bartlett kernel truncated at 8
recovers a deflation factor of about 1.9 against a true 3.27 — it would under-correct the
firm's single documented case by 42% and the residual error would still run permissive. The
Andrews plug-in returns `L = 46` at that `ρ` and `T` [measured] and recovers **3.08** against
the theoretical 3.27 [measured]. The rule that fails to fix the one case the firm has
measured is not the rule to adopt. `[inferred — the choice between two published bandwidth
rules is mine; the arithmetic that decides it is measured]`

> **E-4 · `HACTStat` — the dataclass every caller receives.**
>
> ```
> @dataclass(frozen=True)
> class HACTStat:
>     t_raw:      float   # sr_tstat(r) — uncorrected, never graded
>     t_nw:       float   # sr_tstat_nw(r, lag) — honest HAC, may exceed t_raw
>     t_gate:     float   # min(t_nw, t_raw) — the ONLY figure graded (E-8)
>     lag:        int
>     lag_rule:   str     # "andrews" | "label_span" | "stated" | "andrews(capped)"
>     rho_hat:    float   # unclipped lag-1 autocorrelation
>     inflation:  float   # t_raw / t_nw, the factor I-050 is about; nan if t_nw == 0
>     eligible:   bool    # False => the criterion is INSUFFICIENT-DATA (E-6, E-7, E-9)
>     note:       str     # why, when eligible is False; "" otherwise
> ```

> **E-5 · New function `stats.sr_tstat_corrected(returns, *, label_span=1, stated_lag=None)
> -> HACTStat`.** The lag actually used is
>
> ```
> L_pre  =  max( hac_lag_andrews(r).lag ,  label_span − 1 ,  stated_lag or 0 )
> L_cap  =  min( floor(T / 4) ,  T − 2 )
> L      =  min( L_pre , L_cap )
> ```
>
> `lag_rule` records which of the three terms attained the max, with `"(capped)"` appended
> when `L_pre > L_cap`. **The maximum is one-sided by construction: a caller can raise the
> lag and can never lower it.** A sponsor who states `stated_lag = 0` on a carry family gets
> the Andrews lag anyway. This is the clause that closes the discretionary route around the
> correction, and it is why `stated_lag` is safe to expose at all.
>
> `label_span − 1` is the floor I-050's repair paragraph requires [cited — I-050]: an
> observation whose label is realized over `L` bars induces `MA(L−1)` structure in the return
> series by construction, and a lag truncation below `L − 1` cannot see it.

### 1.3 Small sample, instability, and the sign of ρ — E-6 to E-9

> **E-6 · Small sample.** `eligible = False`, with `t_raw`, `t_nw`, `t_gate` still computed
> and reported, when **either**:
> (a) `T < 32`; or
> (b) `T < 10 · (L + 1)`.
> Below (a) the HAC estimator's finite-sample bias is larger than the effect it corrects.
> (b) is the standard `T/L → ∞` requirement made concrete. `10` and `32` are `[inferred]` and
> I will move either only on a reasoned argument received **before** a family's Gate 1, never
> during one. Neither binds any Gate-1-eligible family in practice: Charter §4.4's ≥ 4-year
> floor puts `T ≥ 1,008` on daily bars, against a requirement of `T ≥ 350` at `ρ = 0.83`
> [measured].

> **E-7 · Degenerate variance.** If `σ̂²_NW(L) ≤ 0` — reachable only as an exact zero, on a
> constant series — `t_nw = nan`, `t_gate = nan`, `eligible = False`. If `T < 2`, all three
> are `nan` and `eligible = False`, matching `sr_tstat`'s existing contract.

> **E-8 · THE NON-PERMISSIVE FLOOR. `t_gate = min(t_nw, t_raw)`, unconditionally.**
> When `ρ̂ < 0` the HAC standard error is smaller than the i.i.d. one and `t_nw > t_raw`.
> Grading on `t_nw` there would be an estimator change that **loosens**, which the
> Principal's asymmetry places outside Validation's authority. The `min` is taken without a
> sign condition: for `t_raw ≤ 0` the criterion fails on either figure and `min` remains the
> conservative choice. The report still carries `t_nw` unmodified so the fact that the floor
> bound is visible and auditable.
>
> **What would have to be true to remove this floor:** a Principal act under §2, with a
> stated argument that the firm should receive credit for measured negative autocorrelation.
> I do not recommend it and I am not requesting it. `[inferred]`

> **E-9 · Near-unit-root refusal.** If `|ρ̂| ≥ 0.97` (unclipped), `eligible = False` with a
> note naming the value. A series that near the unit circle is not covariance-stationary in
> any useful sense; a HAC standard error computed on it is not a correction, it is a number.
> The verdict is **INSUFFICIENT-DATA and it is escalated to Validation** — never PASS, and
> never a silently large `t`.

### 1.4 What the report says, and what is graded — E-10 to E-12

> **E-10 · `ValidationReport` gains five fields**, all rendered on the markdown face:
> `t_stat_uncorrected`, `t_stat_hac`, `hac_lag`, `hac_lag_rule`, `hac_rho_hat`.
> The markdown renders a line of exactly this shape, directly beneath the criteria table:
>
> ```
> t-statistic: HAC-corrected **{t_stat_hac:.3f}** at lag {hac_lag} ({hac_lag_rule},
> ρ̂ = {hac_rho_hat:+.3f}) · uncorrected {t_stat_uncorrected:.3f} — **the uncorrected figure
> assumes serial independence, is reported for continuity, and is NOT graded.**
> ```
>
> **These are report fields, not `Criterion` rows.** A `Criterion` carries a
> PASS/FAIL/INSUFFICIENT-DATA verdict and `overall` is `PASS` only if every criterion is
> `PASS`; adding an ungraded diagnostic as a criterion would fail every Gate forever. Seat 9
> must not implement E-10 by appending to `criteria`.

> **E-11 · The graded criterion.** `gates.py:260–262`'s criterion is renamed
> **`"t-statistic (net, HAC-corrected)"`**, its value is `HACTStat.t_gate`, its threshold
> string is unchanged (`">= 3.0"`), and its verdict is
> `PASS` if `t_gate ≥ T_STAT_HURDLE` and `eligible`,
> `INSUFFICIENT-DATA` if `not eligible` (note = `HACTStat.note`),
> `FAIL` otherwise.
> The criterion's `note` always carries `f"uncorrected t = {t_raw:.3f}, inflation
> {inflation:.2f}×"` so the comparison survives into any excerpt of the table.
>
> `evaluate_gate1` gains one keyword, `label_span: int = 1`, passed through to E-5. It is
> **not** read from the registry: the registry has no binding field for it (I-052 is the
> issue that would create one) and inventing a caller-asserted registry field here would be
> a narrated number inside a graded criterion — the I-014 shape. The Andrews floor in E-5
> means an undeclared label span degrades to the data-driven lag, never to zero, so the
> permissive route is closed without the field. **When I-052's registry work lands, the
> label span becomes a sealed binding field and this keyword becomes a fallback. That is a
> later dispatch and is not specified here.**

> **E-12 · Cost robustness uses the same estimator.** `gates.py:514`'s `"t-stat at 2× costs"`
> criterion is computed as `sr_tstat_nw(r₂, L)` where `L` is **the lag selected on the base
> OOS series**, not re-selected on `r₂`. Its criterion name becomes
> `"t-stat at 2× costs (HAC-corrected)"`. Leaving this one uncorrected would preserve the
> whole of I-050 inside the robustness test, which is the criterion most likely to be the
> binding one.

### 1.5 The bisections — E-13 to E-14

> **E-13 · The lag is selected once and held fixed across every sweep.** For the breakeven
> cost bisection (`gates.py:517–530`) and for `carry.carry_breakeven_bps_annual`
> (`carry.py:96–110`), the lag `L` is computed **once, on the unmodified base net return
> series**, and passed to every `sr_tstat_nw` evaluation inside the sweep.
>
> **Reason, and it is Ruling 003's own.** A bisection assumes the bracketed statistic is
> monotone in the swept parameter. Re-selecting the lag at each bisection step makes the
> statistic a step function of the parameter — `L` jumps as `ρ̂` drifts — and the bisection
> converges on a bracket artifact rather than a breakeven. That is exactly the failure I-037
> records and Ruling 003 repaired. **A fixed lag preserves monotonicity; a re-selected lag
> destroys it.**

> **E-14 · Both bisections grade on the HAC figure, and the breakeven falls.** The reported
> breakeven cost multiplier and the reported carry breakeven in bps/yr will both be
> **strictly lower** for any family with positive serial correlation, because `t` is lower
> everywhere in the sweep. This is the intended effect: the breakeven round-trip cost is the
> number Validation reports as more informative than the net Sharpe [cited — Charter §4.4],
> and it has been reported against an inflated `t` since the harness was written. The
> degenerate branches are unchanged: `t_lo < hurdle → return lo`, `t_hi ≥ hurdle → return hi`.
>
> **`carry_breakeven_bps_annual`'s signature gains `label_span: int = 1` and an optional
> `lag: int | None = None`.** When `lag` is given it is used directly (E-13's fixed-lag
> contract); when it is `None` the function selects once on `net_returns_at_shift(bracket[0])`
> and holds it.

### 1.6 Transition — E-15 to E-16

> **E-15 · There is no dual-hurdle transition period and no grace window.** The corrected
> statistic is the graded one from the moment it merges. The uncorrected figure is reported
> permanently — not for a transition, but because a report that hides the size of its own
> correction cannot be audited. **The firm holds zero families and zero trials
> [measured — `book/registry.db`], so nothing is retro-fitted and no result changes.** This
> is the entire reason the correction is cheap today and the entire reason it is being made
> today.

> **E-16 · No prior artifact is amended by this clause.** No Validation Report exists; no
> Gate has been evaluated; no `t` has been asserted by any seat against any return series.
> Any future document quoting a `t` quotes the HAC figure and states the lag beside it. **A
> `t` quoted without its lag is not admissible in a Validation Report, and I will return it.**

## 2. ITEM 2 — THE CV SPLITTERS (I-051) · clauses W-1 to W-10

### 2.1 The two defects, and one over-claim in my own filing that I am withdrawing here

**(a) `purged_kfold_splits`'s embargo ignores feature lookback.** It embargoes
`⌈n_samples · 0.01⌉` bars after each test fold [measured — `cv.py:29,39`]. A training
observation at `t` after the fold whose features are computed on a trailing window of width
`W` reads `[t − W, t]`; if `W > embargo`, that window reaches back **inside the test fold**.
On 2,398 bars the embargo is **24** [measured] against PREREG-002 §7.1's declared 30-day
trailing baseline [cited]. This is a genuine forward leak and it is permissive.

**(b) `walk_forward_windows` purges nothing and embargoes nothing.** It yields
`idx[: fold[0]]` — every bar strictly before the fold [measured — `cv.py:43–61`] — and takes
neither `label_span` nor `embargo_fraction`. A training observation at `t0 − 1` whose label
is realized over `L` bars has a label spanning `[t0−1, t0−1+L)`, which for any `L > 1`
**reads returns inside the test fold**. For a fitted family that raises the OOS leg and
therefore raises WFE against `WFE_MIN = 0.50`. Permissive. Charter §4.4 requires "purged
k-fold with 1% embargo applied" **and** WFE across ≥ 10 windows [cited]; the harness
satisfies the second through a splitter satisfying neither.

**(c) The over-claim, withdrawn.** Ruling 004's ML-T-11 asserts, as its third condition,
that *"no training bar in a later window reads within 30 bars of a previous test fold's
end."* **I authored that and it is wrong, and I am correcting it before implementation
rather than after.** In an expanding-window walk-forward, window *k*'s test fold is
legitimately past data by window *k+1*; a later training bar reading it is not leakage, it
is the walk-forward working. Enforcing that assertion would delete correct training data
from every subsequent window for no leakage reason and would cost statistical power. §5
records the replacement and the reasoning in full. **Ruling 004 §11's standing term is that
Seat 9 escalates a test it believes wrong rather than amending it; the same term binds me,
and this is me discharging it in writing, pre-implementation.**

### 2.2 `purged_kfold_splits` — W-1 to W-4

> **W-1 · `feature_lookback` becomes a required, must-be-stated keyword.**
> New signature:
>
> ```
> purged_kfold_splits(n_samples, n_splits=5,
>                     embargo_fraction=EMBARGO_FRACTION_DEFAULT,
>                     label_span=1, *, feature_lookback: int | None = None)
> ```
>
> Calling with `feature_lookback is None` raises **`castellan.errors.CVSpecificationError`**
> (new, subclassing `ValueError` so no existing `except ValueError` handler is broken) with a
> message naming the parameter and I-051. `feature_lookback < 0` raises the same.
> **`feature_lookback = 0` is a legitimate, explicit statement** — it means "this family's
> features use no trailing window" — and is accepted. Silence is not that statement.
>
> This is the clause that makes the declaration compulsory. A splitter that defaults the
> lookback to zero is a splitter that lets a 30-day-lookback family leak by omission.

> **W-2 · The effective embargo.**
>
> ```
> embargo_effective  =  max( ceil(n_samples · embargo_fraction) ,  feature_lookback )
> ```
>
> and no training index may lie in `(t1, t1 + embargo_effective]` for any test fold ending at
> `t1`. On the §2.1(a) arithmetic — `n_samples = 2398`, `embargo_fraction = 0.01`,
> `feature_lookback = 30` — the effective embargo is **30**, not 24 [measured]. The Charter's
> 1% is a floor and is never reduced by this clause: `max`, not `feature_lookback`.

> **W-3 · The purge is unchanged and is protected.** `train_mask[max(0, t0 − label_span):t0]
> = False` is already correct [measured — `cv.py:37`] and must survive the edit byte-for-byte
> in effect. Test `CVT-3` (§9) exists to catch a regression here, not to drive a change.

> **W-4 · Yield contract unchanged.** The generator still yields `(train_idx, test_idx)` with
> `test_idx` the untouched fold. `train_idx` may be empty for pathological parameters; the
> function does not raise on that — the caller's fit does.

### 2.3 `walk_forward_windows` — W-5 to W-8

> **W-5 · Both parameters become required, must-be-stated keywords.**
>
> ```
> walk_forward_windows(n_samples, n_windows=10, min_train_fraction=0.3, *,
>                      label_span: int | None = None,
>                      feature_lookback: int | None = None,
>                      embargo_fraction: float = EMBARGO_FRACTION_DEFAULT)
> ```
>
> `label_span is None` or `feature_lookback is None` raises `CVSpecificationError`. Negative
> values raise. Zero for `feature_lookback` is a statement and is accepted; `label_span` must
> be `≥ 1`.

> **W-6 · The mandatory gap before every test fold.**
>
> ```
> gap  =  max( label_span ,  feature_lookback ,  ceil(n_samples · embargo_fraction) )
> train_idx  =  idx[ : max(0, t0 − gap) ]
> ```
>
> **The three terms are not the same kind of thing and the spec says so rather than hiding it
> behind a `max`:**
>
> | Term | Kind | Justification |
> |---|---|---|
> | `label_span` | **Leakage repair** — mandatory | A training label spanning into the fold reads the fold. Unambiguous, permissive, this is I-051(b) |
> | `⌈n·embargo_fraction⌉` | **Charter requirement** — mandatory | §4.4 requires the 1% embargo applied. `EMBARGO_FRACTION = 0.01` is a §4.2 constant, imported, not set here |
> | `feature_lookback` | **Validation tightening** — my judgment | *Not* a leakage condition in an expanding window. It is imposed because at the firm's measured `ρ ≈ 0.8` [cited — Ruling 003 §3.2] the last `W` training bars and the first `W` test bars carry near-duplicate information, and a WFE ratio computed across a boundary that thin is nominally out-of-sample and substantively not. `[inferred]` |
>
> Validation may tighten unilaterally; the Principal's asymmetry constrains loosening, not
> tightening. **But the third row is a new requirement rather than a repair, and labelling it
> as a repair would be exactly the "defensible-sounding reason" drift Appendix B item 4 names.
> It is labelled as what it is.** Cost: at most `feature_lookback` bars of training data per
> window. On a 4-year daily sample with `W = 30` that is 3% of the first window's training set.

> **W-7 · Window count is preserved.** `n_windows` windows are still produced, still
> covering `idx[int(n·min_train_fraction):]`, still contiguous and non-overlapping, still in
> ascending order, and `train[-1] < test[0]` still holds strictly for every window. The gap
> only shortens training sets; it never merges, drops, or reorders a window. Charter §4.4's
> "≥ 10 windows" is unaffected. A window whose training set would be empty after the gap is
> still yielded, with an empty training array — the caller's fit is what refuses it, and
> silently dropping a window would corrupt the ≥ 10 count.

> **W-8 · What is deliberately NOT required, recorded so it is not added later by drift.**
> No forward embargo after a test fold is applied in `walk_forward_windows`. In an expanding
> window there are no training bars after the fold within the same split, and bars after the
> fold that enter *later* windows' training sets are legitimately past data at that point.
> §2.1(c) is the withdrawal of the contrary assertion. **A future seat proposing to add one
> must argue against this clause explicitly.**

### 2.4 The two legacy call sites — W-9 to W-10

> **W-9 · The two existing tests are amended at their call sites only, and nothing else.**
> W-1 and W-5 make both legacy calls raise. Seat 9 makes exactly these two edits and no
> others:
>
> | File · line | From | To |
> |---|---|---|
> | `harness/tests/test_harness.py:154` | `purged_kfold_splits(1000, 5, 0.01)` | `purged_kfold_splits(1000, 5, 0.01, feature_lookback=0)` |
> | `harness/tests/test_harness.py:162` | `walk_forward_windows(1000, 10)` | `walk_forward_windows(1000, 10, label_span=1, feature_lookback=0)` |
>
> **Every assertion in both tests is preserved verbatim. Not one is deleted, relaxed, or
> re-scoped.** These edits make a previously-implicit assumption explicit — the legacy calls
> were always asserting behaviour *at* zero feature lookback and unit label span; they simply
> could not say so. Both tests still pass afterwards: at `feature_lookback = 0` the effective
> embargo is `⌈0.01·1000⌉ = 10`, so `test_purged_kfold_no_overlap_and_embargo`'s ten-bar
> assertion holds unchanged; and at `label_span = 1, feature_lookback = 0` the walk-forward
> gap is `max(1, 0, 10) = 10`, which only strengthens `train[-1] < test[0]`.
>
> **This is a call-site edit, not a test amendment, and it is authorized here in writing so
> that it is on the record before Seat 9 makes it.** Any edit beyond these two cells is a
> test weakening under I-036 and I will treat it as one.

> **W-10 · `harness/examples/demo_workflow.py:123` is updated by the same rule.** It calls
> `walk_forward_windows(len(r_all), 10)` and will raise. It becomes
> `walk_forward_windows(len(r_all), 10, label_span=1, feature_lookback=0)`. **The example is
> the firm's worked reference and an example that raises teaches the wrong thing.** No other
> line of the example changes.

## 3. WHAT SEAT 9 IMPLEMENTS MECHANICALLY VS. WHAT IT ROUTES BACK

The Charter gives Seat 9 "how to implement a stated requirement" and gives Validation "what
counts as correct." This table draws that line clause by clause so it is not negotiated at
implementation time.

### 3.1 Mechanical — implement as written, no consultation

| Clause | Why it is mechanical |
|---|---|
| **E-1** | A prohibition. Do not touch `sr_tstat`. |
| **E-2** | Closed-form arithmetic, fully specified, pinned by `test_hac_t2` against an independent restatement. |
| **E-3** | Closed-form arithmetic, pinned by `test_hac_t5`. |
| **E-4** | A dataclass with named, typed fields. |
| **E-5** | `max` of three stated terms, `min` against two stated caps. |
| **E-7** | Two guard conditions with stated outputs. |
| **E-8** | One `min`. |
| **E-10** | Five report fields plus a render line whose shape is given verbatim. |
| **E-11 / E-12** | Two criterion renames and a substitution of the value computed. |
| **E-13 / E-14** | Hoist one lag computation out of two existing loops. |
| **E-15 / E-16** | Statements of fact; nothing to build. |
| **W-1 to W-7** | Signature changes, one new exception class, `max` of stated terms, index arithmetic. |
| **W-9 / W-10** | Three call-site cells, given verbatim in the table. |

**Everything in `harness/castellan/` that this dispatch touches is listed here:** `stats.py`
(three new functions, one new dataclass, no edits to existing functions), `cv.py` (two
signatures, two bodies), `errors.py` (one new class), `gates.py` (two criteria, five report
fields, one keyword, one bisection), `carry.py` (one signature, one bisection),
`__init__.py` (exports). **No other file, and no Charter constant anywhere.**

### 3.2 Judgment calls — route back to me before implementing

| Clause | The judgment, and the trigger that would make Seat 9 route it |
|---|---|
| **E-6** — the `T ≥ 32` and `T ≥ 10·(L+1)` floors | The constants are `[inferred]`, mine, and are the kind of number that drifts. **Route back if any test or example the firm actually runs is made INSUFFICIENT-DATA by them.** Do not adjust either number to make something pass. That adjustment is the Appendix B item 4 failure in its purest form. |
| **E-9** — the `0.97` near-unit-root refusal | Same. `[inferred]`. **Route back if a real family's net series trips it** — that is a finding about the family, not about the constant, and I want to see it. |
| **E-11** — where the label span comes from | I have specified a keyword rather than a registry field, deliberately (I-052 is the issue that would create the field). **If implementing I-052 in the same dispatch makes a sealed binding field cheap, route back — I will probably take it, but the decision that a graded criterion may read a registry field is mine.** |
| **E-13** — one fixed lag across a bisection | The alternative — re-selecting per step — is more "honest" per-point and destroys monotonicity. I have ruled. **Route back only if the fixed lag produces a non-monotone `t` in the sweep anyway**, which would mean the bisection needs replacing rather than the lag. |
| **W-6** — `feature_lookback` in the walk-forward gap | Explicitly labelled a Validation tightening, not a leakage repair (§2.3 table). **Route back if the gap empties a training window on a real family's parameters** — the fix would be `n_windows` or `min_train_fraction`, not the gap. |
| **W-8** — no forward embargo in walk-forward | This reverses a condition I myself wrote into Ruling 004 ML-T-11. **If Seat 9 believes the original assertion was right, escalate in writing before touching `test_cvt8`.** I have argued it in §2.1(c) and I may be wrong. |

### 3.3 The standing term, restated because it now runs both ways

Ruling 004 §11's term is that Seat 9 implements against pre-authored tests and escalates
rather than amends. **§5 of this document is me discharging the same obligation against my
own tests.** The term binds the author as hard as the implementer, and a Validation seat
that amended its own test quietly after seeing an implementation fail would be doing exactly
what it forbids Seat 9 from doing.

## 4. THE N = 109 CEILING AND THE MinBTL ARITHMETIC UNDER THE CORRECTED ESTIMATOR

*The CIO asked this explicitly, pre-seal. The answer has two halves and the second half is
the one that matters.*

### 4.1 Direct answer: nothing in Ruling 004 moves under this dispatch's corrections

**No. The `N` = 109 ceiling does not move, the MinBTL arithmetic does not move, and no
number in `VALIDATION-RULING-004` is amended by this specification.** PREREG-002 can be
sealed on 109 without re-arithmetic.

The reason is mechanical and checkable. `min_backtest_length_years` computes
`(E[max Z_N] / SR_period)² / ppy` [measured — `stats.py:119–133`], which reduces to
`E[max Z_N]² / SR_ann²` [cited — Ruling 004 §2.1]. **Its only inputs are the trial count and
the Sharpe.** The corrected estimator changes `sr_tstat`, not `sharpe_period`, not
`sharpe_annual`, not `expected_max_sharpe`, and not `min_backtest_length_years`. Clauses E-1
through E-16 touch no function on that path.

Reproduced this session against the live harness: the maximum `N` satisfying
`MinBTL(N, 1.0) ≤ 6.571` is **109** [measured], and `MinBTL(86, 1.0) = 6.1359` against
PREREG-002 §10.4's 6.14 [measured]. Both stand exactly as Ruling 004 records them.

### 4.2 The half that matters: the same defect sits in MinBTL and in DSR, unrepaired

**MinBTL and the DSR both assume serial independence in precisely the way the t-statistic
did, and in the same permissive direction. I found this while checking the CIO's question
and I am reporting it rather than resolving it here.**

- `min_backtest_length_years` measures required length in **observation count**. Under
  autocorrelation the effective sample size is `T·(1−ρ)/(1+ρ)`, so the calendar span a given
  `N` actually requires is larger by `(1+ρ)/(1−ρ)`.
- `deflated_sharpe_ratio` computes `z = (sr − sr₀)·√(T−1)/√denom` [measured —
  `stats.py:115`]. The `√(T−1)` is the i.i.d. standard error of the Sharpe. `denom` corrects
  for skew and excess kurtosis; **it corrects for nothing serial.**

**What the ceiling becomes if MinBTL is corrected** — maximum `N` with
`MinBTL(N, 1.0)·(1+ρ)/(1−ρ) ≤ 6.571 years` [measured, this session]:

| ρ of the net return series | Variance inflation | Admissible `N` ceiling |
|---|---:|---:|
| 0.0 *(today's assumption)* | 1.00 | **109** |
| 0.1 | 1.22 | 55 |
| 0.2 | 1.50 | 31 |
| 0.3 | 1.86 | 19 |
| 0.4 | 2.33 | 12 |
| 0.493 *(SOL funding [cited — Ruling 003 §3.2])* | 2.95 | 8 |
| 0.6 | 4.00 | 5 |
| 0.802 *(ETH funding [cited])* | 9.10 | 2 |
| 0.829 *(BTC funding [cited])* | 10.70 | **2** |

And the DSR's additive term — Ruling 004 §2.3's `required SR_ann ≈ E[max Z_N]·σ_SR + 0.642`
— becomes `0.875` at ρ = 0.3, `1.112` at ρ = 0.5, and `2.099` at ρ = 0.829 [measured].
**Ruling 004 §2.3's entire table shifts upward by that amount.**

### 4.3 The three things that must be said about that table, in order

**First, and it is the qualification that stops this being alarmism: ρ is the autocorrelation
of the family's NET RETURN SERIES, and the firm has not measured it for any family.** The
figures 0.829 / 0.802 / 0.493 are *funding* autocorrelations [cited — Ruling 003 §3.2]. A
real net series is `gross + carry − costs` and the price-return component is close to
serially independent, so the realized ρ lies somewhere between and is family-specific and
**unmeasured** [cited — I-050's own qualification 1, which I wrote and am holding myself to].
**The honest reading of the table is not "the ceiling is 2." It is: the ceiling is a function
of a quantity the firm has never measured, and at every ρ > 0 it is below 109.**

**Second: 109 is not a conservative number and must not be treated as one.** Ruling 004 §2.2
presents 109 as the *maximum* admissible search. It is the maximum **under an assumption
that runs permissive and that the firm has just formally acknowledged is violated by its own
data.** A family planning to spend all 109 is planning against the loosest version of the
constraint. **PREREG-002's declared ceiling of 86 against an absolute of 109 [cited] is
inside the ρ = 0 arithmetic and outside the ρ = 0.2 arithmetic.** That is worth knowing
before a seal, which is exactly why the CIO asked.

**Third: I am not repairing MinBTL or DSR in this dispatch, and I am saying why rather than
letting the silence read as absence.** The repair is in the same class the Principal has
placed under Validation's own authority, so I do not need an act to make it — but it is not
what I was dispatched to specify, and it carries a genuine design question the t-statistic
did not: the DSR's `denom` already carries a published non-normality adjustment [cited —
Bailey & López de Prado 2014] and grafting a serial-dependence term onto it is a
specification choice, not a substitution. **Doing that badly, fast, inside a dispatch scoped
to something else is how a permissive defect becomes a wrong number.** It is filed as
**I-057** with the arithmetic above attached, and it is rated HIGH.

### 4.4 Reproduction

Every figure in §4 is a pure function of `castellan.stats` and consumes no sample. The
script is `scratchpad/proto.py` + `scratchpad/fix.py` from this session; the two load-bearing
reproductions are:

```
max{N : expected_max_sharpe(N)**2 <= 6.571}                    -> 109
max{N : expected_max_sharpe(N)**2 * (1+r)/(1-r) <= 6.571}      -> table above
1.645/sqrt(2397)*sqrt(365)*sqrt((1+r)/(1-r))                   -> DSR additive term
```

**No holdout, no PIT store, and no registry row was read to produce them.**

## 5. CORRECTIONS TO MY OWN PRE-AUTHORED TESTS (Ruling 004 §11.3–§11.4)

Ruling 004 §11's standing term reads: *"Seat 9 implements against these and does not amend
them. A test Seat 9 believes is wrong is escalated to me, in writing, before it is changed."*
**Two of the five tests in scope were wrong. I am escalating them to myself, in writing,
before implementation, because the term binds the author too.** Both defects are filed as
**I-058**.

### 5.1 ML-T-12 — the tolerance was unsatisfiable by a correct implementation

**As drafted:** *"On a synthetic AR(1) series with ρ = 0.8, assert `sr_tstat_nw(r, lag=10) <
sr_tstat(r)` and that the ratio is within 20% of `√((1−ρ)/(1+ρ))`."*

**Why it fails a correct implementation.** A Bartlett-kernel HAC truncated at lag 10 on a
true AR(1) with ρ = 0.8 recovers a ratio of **0.4197**; the asymptotic target is **0.3333**;
they are **25.9% apart** [measured]. The gap is not an implementation error — it is the
Bartlett kernel's down-weighting, which is what makes the estimator positive semi-definite.
**The draft asked a correct implementation to reproduce an asymptotic value at a truncation
far too short to reach it, and would have failed it.**

**The failure mode this creates is the dangerous one.** Seat 9 implements Newey–West
correctly, the pre-authored test fails, and the pressure is to adjust the *implementation*
until the test passes — which means abandoning the Bartlett kernel or fabricating a scale
factor. **That is I-036's failure arriving through a defective test rather than a weakened
one.**

**Replacement** — `test_hac_t3_deflates_ar1_toward_theory`. The assertion is made at the
**Andrews-selected lag** (≈ 48 on this fixture), where the ratio is 0.344–0.371 across six
seeds, against the closed-form Bartlett-truncated value within **15%** (max observed 6.3%)
and against the asymptotic value within **20%** (max observed 11.4%) [measured, 10 seeds].
The lag-0 identity and the i.i.d. assertions survive unchanged as
`test_hac_t1` and `test_hac_t4`.

### 5.2 ML-T-11 — the third assertion asserted a condition that is not leakage

**As drafted:** *"…assert that no training bar in a later window reads within 30 bars of a
previous test fold's end."*

**Why it is wrong.** In an expanding-window walk-forward, window *k*'s test fold is
**legitimately past data** by the time window *k+1* is evaluated. A window-*k+1* training bar
whose feature window reaches into window *k*'s fold is reading its own past. Enforcing the
assertion would permanently delete correct training data from every subsequent window, for
no leakage reason, at a real cost in statistical power. **I wrote it by transporting the
k-fold forward-embargo intuition into a construction where there are no training bars after
the test fold, and the transport does not hold.**

**What survives.** The first two assertions are correct and are the load-bearing ones: the
missing purge is a genuine, permissive leak, and the function must refuse rather than
silently reproduce today's behaviour. Both are carried into `test_cvt7` and `test_cvt6`.

**Replacement** — `test_cvt8_walk_forward_applies_no_forward_embargo_across_windows`, which
asserts the **opposite** of the withdrawn condition, deliberately, so that the withdrawal
cannot be quietly reversed by a future seat re-reading Ruling 004 §11.3 without this section.

### 5.3 What does not change

ML-T-9 and ML-T-10 are correct as drafted and are implemented verbatim as `test_cvt2` and
`test_cvt3`. ML-T-13 is correct as drafted and is implemented as `test_hac_t12`, with the
added E-10 assertion that the ungraded figure is a report field rather than a criterion row.
**Ruling 004 §11.1, §11.2 and §11.5 (ML-T-1 … ML-T-8, ML-T-14) are untouched by this
document** — they belong to I-052 and I-053 and are not in this dispatch's scope.

---

## 6. LEAKAGE AUDIT

Run in full, as required on every Validation output, against **this dispatch's own work
product**. There is no strategy under evaluation here; the audit's subject is the
specification and the tests.

| # | Question | Finding |
|---|---|---|
| 1 | Any field filtering on `event_time` rather than `knowledge_time`? | **N/A.** No field is queried. No data source is touched. |
| 2 | Restated fundamentals? | **N/A**, and unchanged: the firm has no PIT fundamentals and cross-sectional fundamental equity work still cannot pass Gate 1 [cited — `CONSTRAINTS.md`]. Nothing here alters that. |
| 3 | Survivorship-contaminated universe? | **N/A.** No universe is constructed. |
| 4 | Retroactive split/dividend adjustment? | **N/A.** No price series is read. A4 is untouched: research still consumes `pit_adjusted_close` only. |
| 5 | Same-bar fill? | **N/A**, and the engine's `SameBarFillError` guard is not on any path this dispatch modifies. |
| 6 | Standard k-fold where purged k-fold with a 1% embargo was required? | **THIS IS THE FINDING, and it is I-051.** `walk_forward_windows` is today a splitter satisfying neither purge nor embargo, used to produce a Charter §4.4 criterion. §2 repairs it. The 1% is preserved as a floor by W-2 and W-6 and is never reduced. |
| 7 | Parameter chosen at an argmax rather than a plateau centroid? | **No parameter is chosen from a surface here.** The two constants I set (`0.97`, and the `32`/`10×` small-sample floors) are `[inferred]` judgments stated in advance of any result, not selections off a computed surface. E-5's lag is selected by a published mechanical rule, and by a **one-sided** `max` that a caller can raise and cannot lower — which is the structural opposite of an argmax selection. |
| 8 | Was the holdout consulted, in any form, before this evaluation? | **No.** `HoldoutVault.open_once` was not invoked. No vault under `book/vaults/` was read, listed, or decrypted. No passphrase was requested, supplied, or held. This seat holds no holdout plaintext. **Holdout status: LOCKED, unopened, unretired.** |

**Registry state, before and after this dispatch [measured]:** `book/registry.db` — **0
hypotheses, 0 trials**, 1 pre-existing event. No `open_hypothesis` call, no `run_backtest`
call, no trial logged. The test suite's registries are all `tmp_path`-scoped, as every
existing test's are.

**A2 compliance.** Neither item creates a path around `run_backtest`. Both change how a
number the engine already produced is *evaluated*; neither produces a number, and neither
adds an input the engine does not already carry.

---

## 7. RELATION TO EXISTING RULINGS, PRE-REGISTRATIONS, AND AMENDMENTS

Checked item by item, deliberately, as Ruling 004 §12 did.

| Document | Interaction |
|---|---|
| **Charter §4.2 constants** | **None moved.** `T_STAT_HURDLE = 3.0` and `EMBARGO_FRACTION = 0.01` are used exactly as written and are imported, never redefined. §4.2 appears in no clause as a parameter. |
| **Charter §4.4, "purged k-fold with 1% embargo applied"** | **Now actually satisfied by both splitters.** It was satisfied by one and asserted by the other. |
| **Charter §4.4, breakeven cost reporting** | **Number changes, requirement does not.** The reported breakeven falls for any positively autocorrelated family (E-14). It has been computed against an inflated `t` since the harness was written. |
| **Amendment A1** | **Strengthened.** `evaluate_gate1` remains the only source of a Validation Report and now embeds five further fields that cannot be narrated. |
| **Amendment A2** | **No path around it created.** §6 above. |
| **Amendment A4 / PIT store** | **Untouched.** No price path is modified. |
| **Ruling 001** (holdout regime, ingest ceiling) | **Consistent.** Nothing here reads, opens, or reclassifies a holdout. D1–D4 are not reopened. |
| **Ruling 002 R1** (required HISTORICAL sentence) | **Precedent followed, not amended.** E-10's required ungraded-figure sentence is built on R1's logic — a report that omits the limit of its own control will be read as though the control had none. |
| **Ruling 003 §6.5** (Newey–West for F-002's `t(α)`) | **Generalized, as its own reasoning always pointed.** §6.5 required a serial correction for one falsifier on one family; E-11 applies it to the Gate 1 criterion every family must clear. **F-002 leg (i) is therefore already compliant and its `t` does not change.** |
| **Ruling 003 / I-037** (the bisection-artifact repair) | **Extended.** E-13's fixed lag exists because a re-selected lag would reintroduce exactly the non-monotonicity I-037 records. |
| **Ruling 004 §2.2 (`N` = 109) and §2.1 (MinBTL)** | **Not moved by this document** (§4.1). The unrepaired same-class defect in MinBTL/DSR is filed as I-057 (§4.2). |
| **Ruling 004 §6.1** (interim control: `walk_forward_windows` may not be used by a fitted family) | **Remains in force until W-5/W-6 ship and `test_cv_purge_embargo.py` is green.** It is lifted by the implementation, not by this document. |
| **Ruling 004 §11.3 / §11.4** | **ML-T-9, ML-T-10, ML-T-13 implemented verbatim. ML-T-12 and ML-T-11 corrected by their author, pre-implementation, per §5.** |
| **PREREG-002** | **No clause of it is amended by this document.** Its declared ceiling of 86 sits inside the ρ = 0 arithmetic; §4.3 states what that does and does not mean, pre-seal. Its K1 30-day lookback is the realistic case W-2 is built around [cited — PREREG-002 §7.1]. |
| **I-052 / I-053** | **Not touched, not blocked, not resolved.** E-11 deliberately avoids depending on I-052's registry work so that I-050 is not held hostage to it. |

**Nothing in this specification contradicts any existing ruling or pre-registration.** Two
defects *within a prior Validation artifact of my own* were found and are filed (I-058).

---

## 8. ISSUES FILED

| # | Severity | Subject | Interrupt? |
|---|---|---|---|
| **I-057** | **HIGH** | MinBTL and DSR carry the identical serial-independence defect I-050 identifies in the t-statistic, in the same permissive direction; correcting them moves the admissible `N` ceiling below 109 at every ρ > 0. Pre-seal on PREREG-002. | **Yes — §4 hard interrupt, and it is addressed to the Principal.** |
| **I-058** | LOW | Two of my own pre-authored acceptance tests in Ruling 004 §11.3–§11.4 were defective; a correct implementation would have failed one of them. Caught by the author before implementation; cost zero. | No. |

**Numbering note — the collision happened again, twice, during this dispatch.** I was
instructed to number from **I-055**. While this specification was being written, the Director
of Research wrote **both I-055 and I-056** into `logs/ISSUE_LOG.md` concurrently. I re-checked
the high-water mark immediately before appending and took **I-057** and **I-058**.

This is the **fourth and fifth** instance of the concurrent-work collision the log already
records at I-013, I-041 and I-054. **The source is not carelessness; it is that issue numbers
are allocated by reading a file that another seat may be appending to at the same moment, and
parallel dispatch is the firm's normal operating mode.** Reported to the CIO as a process
finding. **Not filed separately: I-054 is the open entry for this shape and the log is the
CRO's.** The cheap structural fix — seat-prefixed issue numbers, or allocation at dispatch
rather than at filing — is the CIO's call, not mine, and I am not making it.

---

## 9. TEST INVENTORY AND THE INTENDED RED STATE

**Baseline before this dispatch: 160 passed [measured].**
**After this dispatch: 26 failed, 162 passed [measured]. 28 tests added.**

| File | Tests | Red today | Green today | Drives |
|---|---:|---:|---:|---|
| `harness/tests/test_tstat_hac.py` | 17 | 15 | 2 | I-050 · clauses E-1 … E-16 |
| `harness/tests/test_cv_purge_embargo.py` | 11 | 11 | 0 | I-051 · clauses W-1 … W-10 |
| **Total** | **28** | **26** | **2** | |

**The two green-today tests are guards, not drivers, and must still pass afterwards:**
`test_hac_t13_sr_tstat_is_not_modified` (E-1 — the correction must not mutate `sr_tstat` in
place) and `test_hac_t14_ungraded_diagnostic_is_not_a_criterion_row` (E-10 — the uncorrected
figure must never acquire a verdict). `test_cvt3` and `test_cvt11` are also guards rather
than drivers but are red today because they use the post-change call form.

**The floor rises from 160 to 188.** `160 + 28 = 188`, and **no existing test may be
deleted, weakened, or re-scoped.** The two authorized call-site edits in W-9 and the one in
W-10 are the complete list of permitted changes to existing files; every assertion in both
legacy tests survives verbatim.

**Partition, per §0.4's reservation.** The two files are independently closeable.
`test_tstat_hac.py` green ⇒ **I-050 closes**. `test_cv_purge_embargo.py` green ⇒ **I-051
closes**. Neither is contingent on the other. If Seat 9's dispatch greens one file and not
the other, the HIGH issue is not held hostage to the MEDIUM one.

**How to reproduce the red state:**

```
python3 -m pytest harness/tests -q
# expect: 26 failed, 162 passed
python3 -m pytest harness/tests/test_tstat_hac.py harness/tests/test_cv_purge_embargo.py -q
# expect: 26 failed, 2 passed
```

**A note on how the tests fail.** Every missing capability is probed through a helper that
calls `pytest.fail` with the clause reference, so each failure names the clause it is waiting
on rather than producing an import-time collection error. `test_cv_purge_embargo.py` is
importable today and stays importable; nothing in either file depends on a symbol existing at
import time.

---

*End of specification. `T_STAT_HURDLE = 3.0` has not moved. — Head of Quantitative Validation,
2026-08-04.*
