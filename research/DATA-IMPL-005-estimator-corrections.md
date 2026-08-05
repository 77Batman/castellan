# DATA-IMPL-005 — Estimator corrections landed: I-050 (HAC t-statistic) and I-051 (CV purge/embargo)

**Seat:** Head of Data & Infrastructure (Seat 9) · **Date:** 2026-08-04
**To:** the CIO · cc Validation
**Work order:** `research/VALIDATION-SPEC-001-estimator-corrections.md` §1 (E-1…E-16)
and §2 (W-1…W-10), authored by Validation, pre-implementation, red-first.
**Dispatch:** S2-D-013 · Issue range allocated: I-070–I-079 (took I-070 only).

**Baseline confirmed before touching anything:** `python3 -m pytest harness/tests -q`
→ **26 failed, 162 passed** [measured], matching the spec's §9 claim exactly.

---

## 1. Result on the two named test files

```
$ python3 -m pytest harness/tests/test_tstat_hac.py harness/tests/test_cv_purge_embargo.py -q
................F...........
1 failed, 27 passed in 1.00s
```

- `harness/tests/test_cv_purge_embargo.py` — **11/11 pass. I-051 closes.**
- `harness/tests/test_tstat_hac.py` — **16/17 pass.** The one failure,
  `test_hac_t17_carry_breakeven_is_corrected`, is a test-fixture defect filed as
  **I-070** (§4 below) and is **not** an estimator defect — see §2 for how that was
  checked. Per VALIDATION-SPEC-001 §0.4's partition ("the two files are independently
  closeable... if Seat 9's dispatch greens one file and not the other, the HIGH issue
  is not held hostage to the MEDIUM one"), I do not declare I-050 closed on my own
  authority while one of its 17 acceptance tests is red for a reason outside the
  estimator itself — that is Validation's call to make, per the standing term that a
  test believed wrong is escalated, not amended or silently worked around.

**Both guard tests, confirmed still green:**

```
$ python3 -m pytest harness/tests/test_tstat_hac.py::test_hac_t13_sr_tstat_is_not_modified \
                    harness/tests/test_tstat_hac.py::test_hac_t14_ungraded_diagnostic_is_not_a_criterion_row -q
..
2 passed in 0.85s
```

`test_hac_t13` (E-1, `sr_tstat` not mutated) and `test_hac_t14` (E-10, the uncorrected
figure is a report field, never a `Criterion` row) both hold.

## 2. Whole-suite number, with the concurrency caveat attached

```
$ python3 -m pytest harness/tests -q
1 failed, 187 passed in 10.24s
```

**188 total = 160 baseline + 28 new, exactly as VALIDATION-SPEC-001 §9 projects.**
This is a live number and is reported **separately** from the two-file result per the
dispatch's explicit instruction, because Validation is concurrently authoring new
tests for the MinBTL/DSR serial correction in new files that were not yet present at
the time of this run (confirmed: no new file under `harness/tests/` besides the two
named ones; `research/VALIDATION-SPEC-002-serial-corrections.md` is present,
untracked, and was not read or acted on — out of scope for this dispatch). If the
whole-suite count moves in a later session, that movement is not this dispatch's
result.

**No regression anywhere else in the suite.** The 160 pre-existing tests plus the two
authorized call-site edits (W-9, W-10, below) all still pass; the only red test is
the one filed as I-070.

## 3. What was mechanical, what required interpretation, and what was escalated

### 3.1 Implemented exactly as specified, no interpretation required

E-1 (untouched `sr_tstat`), E-2/E-3 (`sr_tstat_nw`, `hac_lag_andrews`, pinned bit-exact
against the spec's independent reference formulas in `test_hac_t2`/`test_hac_t5`),
E-4 (`HACTStat` dataclass), E-5 (the one-sided `max`/`min` lag construction), E-7
(degenerate variance), E-8 (`t_gate = min(t_nw, t_raw)`, unconditional), E-10 (five
report fields, not `Criterion` rows), E-11/E-12 (criterion renames and value
substitutions), E-13/E-14 (lag hoisted once, held fixed across both bisections),
W-1…W-7 (both CV signatures, `CVSpecificationError`, the `max()` gap/embargo
constructions), W-9/W-10 (the three authorized call-site edits, verbatim).

### 3.2 Required interpretation, but stayed within "how to implement" (Seat 9's mandate)

- **`lag_rule`'s exact string set.** E-4's dataclass comment lists only
  `"andrews" | "label_span" | "stated" | "andrews(capped)"`, but E-5's prose is the
  authority and says plainly: *"`lag_rule` records which of the three terms attained
  the max, with `"(capped)"` appended when `L_pre > L_cap`"* — with no restriction to
  the Andrews term. I implemented literally against the prose (any of the three names,
  with `(capped)` appended whenever it applies), not against the illustrative comment,
  since the prose is unambiguous and no test in scope constrains this further than
  `"label" in lag_rule` (`test_hac_t6`).
- **The graded criterion's `note` field.** E-11 says the note "always carries" the
  uncorrected-t/inflation string, and separately that INSUFFICIENT-DATA verdicts carry
  `HACTStat.note`. Implemented as: the uncorrected-t/inflation string is always
  present, with `HACTStat.note` prepended when `eligible` is False — satisfying both
  sentences rather than picking one. No test in scope asserts the note's exact
  content, only its presence.
- **Floating-point degeneracy detection in `sr_tstat_nw` (E-7).** The spec says a
  non-positive long-run variance is "reachable only as an exact zero, on a constant
  series." In practice, `np.full(1000, 0.001).std(ddof=1)` is `~4.3e-19`, not exactly
  `0.0` — a genuine floating-point artifact of `mean()`/subtraction rounding on a
  repeated float, not a defect in the formula — so the naive computation produced a
  huge finite `t` instead of `nan` on `test_hac_t11`'s literal fixture. I added a
  bit-identity check (`np.all(r == r[0])`) ahead of the floating subtraction, which
  detects the mathematically-exact-zero-variance case the spec describes without
  touching `sr_tstat` (E-1 forbids that) or loosening any tolerance. This is a
  numerical-robustness implementation choice, not a threshold or asymmetry judgment,
  and I did not escalate it.

### 3.3 The six named judgment-call clauses — none required routing back

- **E-6** (`T>=32`/`T>=10*(L+1)` floors) — not triggered by any real family (none
  exist; registry is 0/0). The two tests that exercise ineligibility (`test_hac_t9`)
  do so by deliberate fixture design, not by a family the firm actually runs. No route
  back; constants used exactly as specified (32, 10).
- **E-9** (0.97 near-unit-root refusal) — only triggered by `test_hac_t10`'s
  deliberate `rho=0.99` fixture, not by any real family's series. No route back.
- **E-11** (label span source) — I did not implement I-052's registry field in this
  dispatch (out of scope, as the spec directs); `label_span` remains
  `evaluate_gate1`'s keyword, defaulting to 1. No route back triggered.
- **E-13** (fixed lag across a bisection) — checked for non-monotonicity in the swept
  statistic; none observed. `test_hac_t16`'s bisection converges cleanly and the
  corrected breakeven falls strictly below the uncorrected one, as expected. No route
  back.
- **W-6** (`feature_lookback` in the walk-forward gap) — no training window was
  observed to empty on any tested parameter combination (`test_cvt7`, `test_cvt9`,
  `test_cvt10` all pass with non-empty, correctly-ordered windows). No route back.
- **W-8** (no forward embargo in walk-forward) — implemented exactly as specified
  (§2.1(c)'s withdrawal); I agree with the withdrawal and did not find grounds to
  argue the original ML-T-11 assertion was right. No escalation.

**Nothing among the six was escalated. One item outside the six was escalated — see
§4.**

## 4. Escalated to Validation rather than decided: I-070

`test_hac_t17_carry_breakeven_is_corrected` reuses `test_hac_t16`'s fixture
(`r = _ar1(4000, 0.8, 0.0035, 5)`, per-bar mean ≈0.0035, ≈127%/yr annualized) against
`carry_breakeven_bps_annual`'s **default** bracket `(0.0, 2000.0)` bps/yr (0–20%/yr).
Measured: at the bracket's ceiling (2000 bps/yr), the HAC-corrected `t` is still
5.79 and the uncorrected `t` is still 16.83 — both far above `T_STAT_HURDLE = 3.0` —
so both the corrected and uncorrected bisections hit the function's own documented,
spec-unchanged degenerate branch (`t_hi >= hurdle → return hi`) and return the
bracket ceiling. The test's assertion that `t` at the returned breakeven equals
`3.0 ± 0.05` then fails, **for any correct implementation of either estimator** — a
bracket that is roughly 3–5× too narrow for this fixture's magnitude, not an
estimator defect. Full arithmetic, severity reasoning, and disposition are in
`logs/ISSUE_LOG.md` under **I-070** (Severity: MEDIUM, escalated to
`quant-validation`). The test file is unmodified; nothing was fudged to chase the
assertion.

## 5. The two invariants, checked directly

```
min(t_NW, t_raw) never violated, across rho in {-0.6, -0.2, 0.0, +0.3, +0.8}:
  rho=-0.6  t_raw=5.232  t_nw=8.972  t_gate=5.232 (= t_raw, floored)
  rho=-0.2  t_raw=6.507  t_nw=7.480  t_gate=6.507 (= t_raw, floored)
  rho=+0.0  t_raw=6.792  t_nw=6.652  t_gate=6.652 (= t_nw)
  rho=+0.3  t_raw=6.925  t_nw=5.006  t_gate=5.006 (= t_nw)
  rho=+0.8  t_raw=6.844  t_nw=2.271  t_gate=2.271 (= t_nw)
  -> t_gate never exceeds t_raw; the correction only ever tightens.

One-sided lag floor, AR(1) rho=0.8, Andrews lag = 48:
  stated_lag=0        -> L = 48 (Andrews wins; stated cannot lower it)
  stated_lag=1        -> L = 48
  stated_lag=43       -> L = 48 (below Andrews; cannot lower it)
  stated_lag=98       -> L = 98 (above Andrews; caller CAN raise it)
```

Both properties hold in every case checked, matching the Principal's asymmetry
mechanically: a caller can raise the lag and never lower it, and the graded figure
is never more permissive than the uncorrected one.

## 6. Files touched

`harness/castellan/stats.py` — three new functions (`sr_tstat_nw`,
`hac_lag_andrews`, `sr_tstat_corrected`) and one new dataclass (`HACTStat`);
`sr_tstat` untouched, verified byte-for-byte behaviourally identical
(`test_hac_t13`).
`harness/castellan/cv.py` — `purged_kfold_splits` gains required
`feature_lookback`; `walk_forward_windows` gains required `label_span` and
`feature_lookback` plus the mandatory gap.
`harness/castellan/errors.py` — new `CVSpecificationError(ValueError)`.
`harness/castellan/gates.py` — the t-statistic criterion renamed and regraded on
`HACTStat.t_gate`; the 2×-costs criterion renamed and regraded on `sr_tstat_nw` at
the base-series lag; the breakeven bisection regraded on `sr_tstat_nw` at a fixed
lag; five new `ValidationReport` fields and the required markdown line;
`evaluate_gate1` gains `label_span: int = 1`.
`harness/castellan/carry.py` — `carry_breakeven_bps_annual` gains `label_span` and
optional `lag`; bisects on `sr_tstat_nw` at a fixed lag, selected once when `lag` is
not given.
`harness/castellan/__init__.py` — exports `CVSpecificationError`.
`harness/tests/test_harness.py` — the two authorized call-site edits (W-9), every
existing assertion preserved verbatim.
`harness/examples/demo_workflow.py` — the one authorized call-site edit (W-10).
`logs/ISSUE_LOG.md` — **I-070** filed.
`research/DATA-IMPL-005-estimator-corrections.md` — this note.

**Not touched:** any test file other than the two edits authorized in W-9/W-10; no
new test file created; `research/PREREG-002-crypto-funding-basis.md`; any
`VALIDATION-*` document; `book/registry.db` (confirmed 0 hypotheses, 0 trials before
and after, via direct query). No hypothesis opened, no trial registered, no backtest
run. No commit made — the CIO commits under A3.
