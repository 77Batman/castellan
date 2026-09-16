# DATA-IMPL-015 — I-380: THE PREREG-002 §5.2 LEG (I) ESTIMATOR

**Head of Data & Infrastructure · dispatch S4-D-032 · 2026-09-15**
**Scope: implement the OLS + Newey-West/HAC alpha estimator PREREG-002 §5.2 leg (i) specifies. Tests and this document only. NO leg (i) evaluation, no step 3, no step 3b, no C11 null distribution, zero new trials against `book/registry.db`.**

---

## 0. What this document is, and is not

This closes **I-380** (HIGH): F-002 leg (i) specifies a Newey-West `t`-statistic on an OLS regression's intercept, and no such estimator existed anywhere in `castellan` — `stats.sr_tstat_nw` is the Newey-West `t` of a **mean**, not of a regression intercept, by its own docstring. This document records the implementation, its red-first test log, its oracle-agreement figures against `statsmodels`, and the one real convention ambiguity, resolved and stated on the face of the code.

**This document reports no leg (i) verdict, produces no leg (i) result, and does not evaluate F-002 in any way.** Per the Principal's ruling, this estimator does not run in step 3 until Validation has reviewed it. Section 6 confirms this explicitly.

---

## 1. Documents read in full or at the cited sections

| Artifact | Sections | Used for |
|---|---|---|
| `agents/head-of-data-infra.md` | full | operating definition for this seat |
| `CLAUDE.md` | full | orchestrator binding, harness discipline |
| `research/PREREG-002-crypto-funding-basis.md` | §5.2, §5.3, §5.4 (R10), §6.1–§6.3, §21 | the sealed leg (i) statement, position construction, sizing rule, numeric literals |
| `research/DATA-IMPL-013-f002-step2.md` | full | trial 1's exact `run_backtest` call, its identifiers, its position/cost conventions |
| `research/DATA-IMPL-014-feasibility-gate.md` | full | the un-hedging correction (I-376/I-377), the prior off-engine reconstruction's method and parity figure |
| `harness/castellan/{stats,engine,costs,data,registry}.py` | source read in full or at cited lines | existing conventions; exact net-return formula reused off-engine; trial retrieval |
| `statsmodels` 0.14.6 (system `python3`) / 0.15.0 (`.venv`) source | `regression/linear_model.py::RegressionResults.get_robustcov_results`, `stats/sandwich_covariance.py::{cov_hac_simple, S_hac_simple, weights_bartlett, _get_sandwich_arrays, _HCCM2}` | the oracle's own implementation, read directly rather than assumed from memory or documentation |

---

## 2. Dependency change

**`statsmodels` was ABSENT from the project's `.venv`** [measured — `import statsmodels` raised `ModuleNotFoundError` before this dispatch]. Installed: `.venv/bin/pip install statsmodels` → **statsmodels 0.15.0**, pulling in `patsy`, `formulaic`, `packaging`, `narwhals`, `interface-meta`, `wrapt`, `typing-extensions` as transitive dependencies. No project dependency file (`pyproject.toml`, `requirements.txt`) declares test-only dependencies separately from runtime ones in this repo as inspected, so no manifest edit was made; recorded here as the disclosure the dispatch requires.

**Separately measured, and this is the environment that actually matters:** the suite in `CLAUDE.md`'s own binding instruction runs as `python3 -m pytest harness/tests -q`, and system `python3` (`/Library/Frameworks/Python.framework/Versions/3.13/bin/python3`, with `castellan-harness` installed editable via `pip install -e harness`) **already had `statsmodels` 0.14.6 installed** [measured — `python3 -m pip list`], independently of `.venv`. **Both environments were checked; the oracle-agreement tests below were run under system `python3` (statsmodels 0.14.6), the environment the suite and the dispatch's own `pytest` instruction actually use** — the `.venv` install is disclosed because the dispatch asked whether the project venv had it (it did not, and now does), not because `.venv` is where this suite runs. The two `statsmodels` versions' `HAC` code paths were read directly and are identical in the relevant sections (§3).

---

## 3. The estimator

`harness/castellan/stats.py` — new function `ols_alpha_tstat_hac(y, x, lag, *, use_correction=False) -> OLSHACAlpha`, alongside the existing `sr_tstat_nw`/`hac_lag_andrews`/`sr_tstat_corrected` machinery (same module, same conventions: explicit required `lag`, no auto-selection, a frozen dataclass of every figure a caller needs).

**What it computes**, read directly from `statsmodels`' own source rather than reimplemented from a textbook formula independently:

- OLS via the Moore-Penrose pseudoinverse: `beta_hat = pinv(X) @ y`, `X = [1, x]`, matching `statsmodels`' default `OLS.fit(method="pinv")`.
- `normalized_cov_params` reproduced as `pinv(X) @ pinv(X).T` (the SAME `pinv(X)` used for the coefficients), not a separately-computed `inv(X'X)` — this is what makes agreement below exact to double precision on well-conditioned designs rather than merely close.
- HAC sandwich: per-observation score `xu_i = X_i * resid_i`; Bartlett weights `w_l = 1 - l/(lag+1)` for `l = 0..lag`; `S = w_0 * (xu'xu) + sum_{l=1}^{lag} w_l * (s_l + s_l')` where `s_l = xu[l:]' @ xu[:-l]`; `cov = (X'X)^+ S (X'X)^{+T}`.
- Optional small-sample correction: `cov *= n/(n - k)`, `k=2`, applied only if `use_correction=True`.
- `t_alpha = alpha / sqrt(cov[0,0])` — the PREREG-002 §5.2(i) figure. `t_beta` is also reported (not graded by leg (i), useful for the factor-attribution disclosure below).

**Convention resolved on the face of the function (the one real ambiguity, per the dispatch's own framing):** reading `statsmodels.regression.linear_model.RegressionResults.get_robustcov_results` directly (both 0.14.6 and 0.15.0):

```python
elif cov_type.lower() == 'hac':
    maxlags = kwargs['maxlags']
    ...
    use_correction = kwargs.get('use_correction', False)   # <-- default False
    ...
    res.cov_params_default = sw.cov_hac_simple(
        self, nlags=maxlags, weights_func=weights_func, use_correction=use_correction)
```

**`use_correction` defaults to `False`** when a caller reaches `cov_type="HAC"` via `cov_kwds={"maxlags": L}` without stating `use_correction` explicitly — i.e. the Principal's specified oracle call (`cov_type="HAC", cov_kwds={"maxlags": 21}`) applies **NO small-sample correction**. `ols_alpha_tstat_hac`'s own default, `use_correction=False`, is set to MATCH this exactly — not stated as an independent preference. A caller who needs the corrected convention passes `use_correction=True` and gets bit-identical agreement to `cov_kwds={"maxlags": L, "use_correction": True}` instead (verified, §4). **This resolution is stated on the function's own docstring**, not only here, per the dispatch's instruction that it reach the reader who calls the estimator.

**The un-hedging disclosure (I-376/I-377), also on the function's own docstring, verbatim requirement of this dispatch:** this regression, run on `R_bench` alone, cannot separate conditioning alpha from spot-directional return earned while un-hedged — the sealed position is "long 1.0 unit spot notional, short `w(t)` units perp notional," and at `w(t) < 1` the position is net long spot, not smaller delta-neutral. **The sealed test can pass on spot beta.** Not amendable under P7; Gate 1's Charter 5.4 factor attribution must decompose it before any PROCEED. `test_docstring_carries_the_unhedging_disclosure` (§4) pins this text stays present.

---

## 4. Red-first log

**Each test below was verified, before this document was written, to FAIL against a specific constructed mutation of the reference implementation** — a mutation harness monkeypatched `castellan/stats.py` with each `Mn` variant in turn, ran `harness/tests/test_ols_hac_alpha.py`, and restored the original file (see `harness/tests/test_ols_hac_alpha.py`'s own docstrings, which name the mutation each test targets). **20 tests, 12 mutations, one test REPAIRED mid-dispatch when its first draft did not discriminate its own named mutation (T-18's own failure mode, caught here rather than shipped — see M11 below).**

| Mutation | What it breaks | Tests it turns RED | Result |
|---|---|---|---|
| **M1** | `use_correction` forced `True` internally regardless of the parameter | oracle agreement (all default-`False` cases) | **12 failed** [measured] |
| **M2** | Bartlett weight `1 - l/lag` instead of `1 - l/(lag+1)` (off-by-one denominator) | oracle agreement at every lag > 0, plus `use_correction=True` case | **12 failed** [measured] |
| **M3** | Dropped kernel symmetrization (`S += w*s` instead of `w*(s+s.T)`) | oracle agreement at every lag > 0 | **12 failed** [measured] |
| **M5** | Small-sample correction divisor `n/(n-1)` instead of `n/(n-k_params)` | `test_oracle_use_correction_true` | **1 failed** [measured] |
| **M6** | `alpha`/`beta` swapped in the return value | oracle agreement (every case), `test_intercept_is_column_zero` | **14 failed** [measured] |
| **M7** | Independent (non-joint) NaN dropping, breaking pairwise alignment | `test_joint_nan_dropping_keeps_series_aligned` | **1 failed** [measured] |
| **M8** | Negative `lag` silently coerced via `abs()` instead of raising | `test_lag_must_be_nonnegative` | **1 failed** [measured] |
| **M9** | Upper lag-bound off-by-one (`lag > n-2` instead of `lag >= n-2`) | `test_lag_upper_bound_enforced` | **1 failed** [measured] |
| **M10** | Removed the explicit `y.shape != x.shape` check | `test_length_mismatch_raises` | **1 failed** [measured] |
| **M11** | Relaxed the `n < 3` floor to `n < 2` | `test_too_few_observations_raises` | **FIRST DRAFT: 0 failed** [measured] — **the test did not discriminate its own mutation**; see below |
| **M12** | Deleted the un-hedging disclosure paragraph from the docstring | `test_docstring_carries_the_unhedging_disclosure` | **1 failed** [measured] |

**M11, in full — the one case this dispatch's own red-first process caught rather than shipped.** At `n=2`, the lag-upper-bound guard (`lag >= n-2`, i.e. `lag >= 0`) ALSO raises for any valid nonnegative `lag`, so a message-blind `pytest.raises(ValueError)` passes whether the `n<3` floor fires or the lag-bound guard fires instead — **M11 measured 0 tests failed against the first draft of `test_too_few_observations_raises`**, i.e. a red-first test that could not discriminate the mutation it named, exactly the T-18 precedent the dispatch cites. **Repaired, not shipped as a caveated pass:** the test now asserts on the error MESSAGE (`match="at least 3"`), which the `n<3` branch produces and the lag-bound branch does not. Re-run against M11: **1 failed, as required** [measured]. The repaired test is what ships; the failed-to-discriminate first draft is recorded here rather than smoothed over, per D-012's rider.

**All 20 tests pass against the correct implementation** [measured — `python3 -m pytest harness/tests/test_ols_hac_alpha.py -q` → `20 passed`].

---

## 5. Oracle agreement — Principal ruling 2026-09-16

**Oracle call, exactly as ruled:** `sm.OLS(y, sm.add_constant(x)).fit(cov_type="HAC", cov_kwds={"maxlags": lag[, "use_correction": ...]})`, run under system `python3`'s `statsmodels` 0.14.6 (§2). **Every case below measured `max(|mine - oracle|)` across all six reported figures (`alpha`, `beta`, `se_alpha`, `se_beta`, `t_alpha`, `t_beta`) at exactly `0.0` — bitwise double-precision equality, not merely inside the required `1e-8`** [measured], because the implementation reuses the SAME `pinv(X)` object statsmodels does rather than an independently-derived but mathematically-equivalent inverse (§3).

| Case | Construction | `lag` | `use_correction` | max abs diff (all 6 figures) |
|---|---|---:|---|---:|
| Known-autocorrelated | AR(1) residual, ρ=0.8, T=2000 | 21 | False | **0.0** [measured] |
| Near-zero α | α≈1e-6, T=2000 | 21 | False | **0.0** [measured] |
| High α | α=0.01 (≈2× the β·x scale), T=2000 | 21 | False | **0.0** [measured] |
| Small-sample correction | same AR(1) construction | 21 | **True** | **0.0** [measured] |
| Default-convention check | fresh series, no `use_correction` passed either side | 21 | (default) | **0.0** [measured]; confirms `use_correction=False` is this library's default AND matches the oracle's own default |
| Degenerate lag | T=1000 | **0** | False | **0.0** [measured] |
| Across-lags sweep | AR(1) ρ=0.6, T=3000 | 1, 5, 10, 21, 48 | False | **0.0** at every lag [measured] |
| **Trial 1's derived series** | see §6 | 21 | False | **0.0** [measured] |

**Trial 1's derived series, in full (Principal ruling, "(b) trial 1's derived series"):**

- **`R_bench`** = trial 1's ACTUAL logged return series, read directly (read-only `SELECT`) from `book/registry.db`. Confirmed identifiers: `family='funding-carry-conditioning-002'`, `trial_id=1`, `config_hash='44532cc88ed7b1a9'`, `n_bars=2415`, `periods_per_year=365`, `grant_id=11` [measured — all four match the dispatch's cited values exactly].
- **`R_strat`** = an off-engine reconstruction built **ONLY for this oracle-agreement test — never a leg (i) result, labeled as such in the fixture file itself** (`harness/tests/fixtures/trial1_leg_i_oracle_fixture.npz`). Construction: component panels (`pit_price_panel`/`pit_funding_panel` on `binance`/`binanceusdm`, BTC+ETH, same 2,415-bar index trial 1 ran on), spot leg held CONSTANT at 0.5 notional per asset, perp leg scaled by a reconstructed conditioning schedule `w(t)` per PREREG-002 §5.2/§5.4's sealed sizing rule (`k=0.5`, `d=1.0`, `w_max=1.0`, 30-day trailing z-score lookback, `band=0.54` one-sided turnover band, 30-bar burn-in, the 2025-09-18 K7 trigger) — **so `w(t) < 1` leaves the position net long spot, per the Principal's construction correction (I-376/I-377), and this is emphatically NOT a scalar reweighting of `R_bench`**: measured `corr(R_strat, R_bench) = 0.047` [measured], `R_strat` std ≈ 10.4× `R_bench`'s [measured — 0.00805 vs 0.00077], reflecting the un-hedged spot risk the correction requires.
- **Parity check performed before using this reconstruction for anything:** at constant `w≡1.0` (both assets), the SAME off-engine formula reproduces trial 1's stored blob to **max abs diff = 3.693e-10** [measured] — within `float32` storage precision, and matching `DATA-IMPL-014`'s own cited figure (`3.69e-10`) on the same panels to within rounding. **This reconstruction was NOT imported from `DATA-IMPL-014` — no importable artifact exists to import — it was rebuilt independently from the same sealed formulas and confirmed to converge; filed as `I-388` (LOW), disclosed rather than presented as literal reuse.**
- Zero calls to `run_backtest`, zero trials, zero registry writes of any kind for this construction — it is pure off-engine arithmetic on panels obtained through `PITStore`'s read-only-path methods (`asof`/`pit_price_panel`/`pit_funding_panel` only), so the mandatory scratch-registry rehearsal does not apply (the engine itself was never invoked).

---

## 6. Caller count (§7.10(7))

**Measured count of callers of `ols_alpha_tstat_hac`/`OLSHACAlpha` outside their own definition and their own test file: `0`** [measured — `grep -rn "ols_alpha_tstat_hac\|OLSHACAlpha" --include="*.py" .`, only hits in `harness/castellan/stats.py` (the definition) and `harness/tests/test_ols_hac_alpha.py` (this dispatch's own tests)]. This is a new function; no existing call contract moves.

---

## 7. Suite before/after (§ hard stop 5)

Run **unpiped**, per `CLAUDE.md`'s own binding instruction (`python3 -m pytest harness/tests -q`, exit status read directly — never piped):

| | passed | failed | total |
|---|---:|---:|---:|
| **Before** [cited — dispatch's own stated baseline, "measured, six runs today"] | 343 | 22 | 365 |
| **After** [measured, this dispatch] | **363** | **22** | **385** |

**The 22 failures are unchanged** — `test_carry_accounting.py` (13 of them), `test_holdout_p1.py`, `test_minbtl_serial.py` (×2), `test_registry_write_grant.py`, `test_seeded_n.py` (×2), and others already failing before this dispatch touched anything [measured — same test names, same count, none in a module this dispatch edited]. **+20 passed, +0 failed, +0 regressed** — exactly this dispatch's own new test file (`test_ols_hac_alpha.py`, 20 tests, all green). **The suite does not regress.**

---

## 8. What this seat did and did not do

**Did:**
- Read `agents/head-of-data-infra.md` and `CLAUDE.md` in full, first.
- Implemented `ols_alpha_tstat_hac`/`OLSHACAlpha` in `harness/castellan/stats.py`, matching PREREG-002 §5.2(i) exactly: OLS `R_strat = alpha + beta*R_bench + eps`, Newey-West `t` on `alpha`, caller-supplied lag (21, pre-committed, never auto-selected).
- Wrote 20 tests, RED-FIRST, each with a named constructible failing mutation (§4); caught and repaired one test (M11) that did not discriminate its own mutation before shipping it.
- Verified oracle agreement to exact bitwise equality (well inside the required `1e-8`) on three synthetic constructions (known-autocorrelated, near-zero-α, high-α), a `use_correction=True` case, a default-convention case, a degenerate `lag=0` case, a five-lag sweep, and trial 1's derived series.
- Installed `statsmodels` into `.venv` (absent there) and recorded that system `python3` — the environment the suite actually runs under — already had it (§2).
- Resolved and disclosed the one real convention ambiguity (`use_correction` default = `False`, matching the oracle's own default) on the function's own docstring, not only in this document.
- Carried the un-hedging disclosure (I-376/I-377) onto the function's own docstring, pinned by a test.
- Built the trial-1-derived oracle fixture off-engine, zero trials, zero registry writes, parity-checked against trial 1's actual stored series before use.
- Measured the caller count (0) and the suite before/after (343/22/365 → 363/22/385, zero regressions).
- Filed `I-388` (LOW) for the one honest deviation from instruction (could not literally reuse `DATA-IMPL-014`'s reconstruction — no importable artifact exists — rebuilt independently and confirmed convergence instead).

**Did NOT do, per this dispatch's hard stops:**
- **Did not evaluate F-002 leg (i).** `ols_alpha_tstat_hac` was never called on trial 1's `R_bench` paired with any candidate `R_strat` presented as a real leg (i) input — the one call against real data in this entire dispatch (§5, trial-1-derived case) is explicitly an oracle-agreement test on a labeled test fixture, not a leg (i) evaluation, and no PASS/FAIL verdict is stated or implied anywhere in this document for leg (i).
- **Did not run step 3, step 3b, or the C11 null distribution.**
- **Ran zero new trials against `book/registry.db`.** `run_backtest` was never called, against the live registry or any scratch registry — the trial-1-derived fixture is pure off-engine arithmetic on panels, so the mandatory scratch-registry rehearsal does not apply here (nothing first-of-kind touched the engine).
- **Did not wrap anything in `registry.write_grant`** — no grant of any kind was opened, because no registry write of any kind was made.
- **Did not edit** `PREREG-002`, any `REGISTRATION-PAYLOAD-*`, `VALIDATION-SPEC-005`, `logs/DECISION_RECORD.md`, `CLAUDE.md`, or anything under `book/`. No seal, no passphrase, no `git add`/`commit` (the repository is not under git in this environment in any case — confirmed at session start).
- Did not spawn a subagent. Tools used: `Read`, `Write`, `Edit`, `Bash`. Within the declared set (`Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch` — `Grep`/`Glob`/`WebSearch`/`WebFetch` were not needed; `grep`/`find` were run through `Bash` instead).

---

## 9. Return to the CIO

- **Oracle agreement:** exact (0.0 max abs diff, well inside the required `1e-8`) on every case — three synthetic constructions, a small-sample-correction case, a default-convention case, a degenerate-lag case, a five-lag sweep, and trial 1's derived series.
- **Convention matched:** `use_correction=False` (no small-sample correction), Bartlett kernel, `pinv`-consistent sandwich — all read directly from `statsmodels`' own source (0.14.6 and 0.15.0, identical in the relevant code), not assumed.
- **Suite:** 343/22/365 → 363/22/385. Zero regressions, +20 new passing tests.
- **Finding filed:** `I-388` (LOW) — could not literally reuse `DATA-IMPL-014`'s reconstruction (no importable artifact exists); rebuilt independently and confirmed convergence (3.693e-10 vs the cited 3.69e-10) instead of presenting it as reuse.
- **Dependency change:** `statsmodels` installed into `.venv` (0.15.0); system `python3` — the environment the suite actually runs under — already had it (0.14.6).
- **This seat produced no leg (i) verdict, ran no leg of F-002, and did not evaluate the estimator against any candidate `R_strat` presented as a real result.** The estimator is implemented and stopped, awaiting Validation's review, exactly as ruled.
