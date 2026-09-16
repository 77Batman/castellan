# DATA-IMPL-016 — C11: THE LEG-(II) NULL CALIBRATION, EXECUTED

**Head of Data & Infrastructure · dispatch S4-D-033 · 2026-09-15**
**Governing document: `research/VALIDATION-SPEC-005-c11-null-calibration.md`. Where this deliverable and the dispatch brief that invoked it disagree, SPEC-005 wins — noted explicitly at §9 below.**
**Scope: SPEC-005 in full — the measured `α̂₂`, `α̂₁` (calibration only), `α̂_joint`, the 30-test acceptance suite, the scratch rehearsal, and the one live `log_event`. Step 3 (legs i/ii of F-002) and step 3b were NOT run. Zero new trials logged.**

---

## 0. Provenance — what was read, in what order

`agents/head-of-data-infra.md` (full, first act) · `CLAUDE.md` (full) · `research/VALIDATION-SPEC-005-c11-null-calibration.md` (full, §7 read twice per its own instruction) · `research/PREREG-002-crypto-funding-basis.md` §5.2, §5.3, §5.5(e), §7, §21 · `research/DATA-IMPL-014-feasibility-gate.md` (full) · `research/DATA-IMPL-015-leg-i-estimator.md` (full) · `harness/castellan/{registry,engine,costs,stats,carry,data}.py` (source, in full) · `book/registry.db` (read-only, `sqlite3` direct `SELECT`) · `logs/ISSUE_LOG.md` (tail, to confirm the true max claimed issue number before allocating).

**Not edited:** `PREREG-002`, any `REGISTRATION-PAYLOAD-*`, `VALIDATION-SPEC-005`, `logs/DECISION_RECORD.md`, `CLAUDE.md`. No seal, no `open_hypothesis` against the live registry, no vault write, no passphrase, no `git add`/`commit`.

---

## 1. B-7 — THE DATA-DRIFT STOP, CHECKED FIRST

`book/pit.db` is live-mutating under `capital.castellan.polymarket-book.plist` / `capital.castellan.pit-snapshot.plist` (confirmed growing from `1,590,419,456` bytes, S4-D-030's own baseline, to **`1,593,769,984` bytes** at this dispatch's own first read). Rebuilt the funding panel fresh against the live store and compared to trial 1's logged `funding_panel_sha256`:

```
fresh:   971d037d442cf1a5fb93ad2c797f54938fd6250cccd2079b903d8c853a58c791
trial 1: 971d037d442cf1a5fb93ad2c797f54938fd6250cccd2079b903d8c853a58c791
MATCH: True
```

**B-7 PASSES [measured].** No drift on the `binanceusdm` BTC/ETH funding series between trial 1 and this calibration; the pit.db growth is unrelated (Polymarket capture, confirmed by DATA-IMPL-014 and reconfirmed here). **B-8 PASSES [measured]:** 2,415 bars, `2020-01-01 → 2026-08-11`, settled-only. Calibration proceeded.

---

## 2. Where the reusable reconstruction module was checked in (I-388)

**`harness/castellan/reconstruction.py`** — the off-engine position/net-return reconstruction (schedule builder per §3.4 R-1/R-2/R-3, `target_weights` builder, single-schedule and vectorized-batch net-return reconstruction, `exposure_match_c`). **`harness/castellan/nullcal.py`** — generic null-calibration primitives (`worst_k_mean`/`_batch`, circular block permutation, stationary block bootstrap, the joint-index helper, the §4.6 greedy assignment, `SeedSequence` spawning, Clopper–Pearson intervals, the joint-survival-rate helper, `I_0`). **`harness/tests/test_c11_null_calibration.py`** — the 30 acceptance tests (§6 below). **`research/work/c11_null_calibration.py`** — the calibration orchestration script (family-specific, not generic, kept out of `harness/`). This is the **third** independent reconstruction of this position (after DATA-IMPL-014 and DATA-IMPL-015, neither checked in — I-388) and the **first one checked in**, closing I-388's substance without editing that entry.

---

## 3. Engine-parity (Group A headline)

| Test | Result | Mark |
|---|---:|---|
| A-1: constant `w≡1.0` vs. trial 1's stored blob | max abs diff **3.693×10⁻¹⁰** (≤1e-9) | [measured] |
| A-2: varying schedule (208 bars `\|Δw\|>0`), scratch `run_backtest` vs. off-engine | max abs diff **0.0 (exact)** | [measured] |
| A-6: outer grant around `run_backtest` | raises `RegistryWriteGrantNestedError`, confirmed | [measured] |

The vectorized batch reconstruction (`reconstruct_net_returns_batch`, used for all `B=10,000`-resample work) was separately cross-checked against the single-schedule path over 50 independent permutations: **max diff 2.8×10⁻¹⁷** [measured].

---

## 4. The realized schedule and `c`

| Quantity | BTC | ETH | Mark |
|---|---:|---:|---|
| `w̄` (time average) | 0.8804 | 0.8775 | [measured] |
| Bars at `w_held = 1.0` | 1,736 / 2,415 | 1,084 / 2,415 | [measured] |
| Forced bars (R-1 burn-in + R-2 trigger) | 60 | 60 | [measured] |
| Band-triggered rebalances (R-3, strict `>0.54`) | 126 | 138 | [measured] |

**Both branches of R-3 occur in-sample** (B-6 satisfied; the schedule is not degenerate). `c = 0.939484` [measured] — see **I-390**: computed from the plain time-average of `w` (not the engine's literal lag-and-fill construction), a disclosed ruling that makes `c` exactly permutation-invariant (test C-2), differing from the engine-literal formula by `~4×10⁻⁴` relative, immaterial to every figure below.

---

## 5. `M_b`, the D-2 guard, `I_0`, and `I_max`/`I_min` (I-386, unrepaired)

```
M_b = -0.0018013                                    [measured]
guard D-2 (M_b < 0): satisfied                      [measured]
I_0 = -8.2649                                       [measured]
```

**D-3 satisfied on its own terms:** `I_0` is computed and is emphatically not `≈0`, corroborating DATA-IMPL-014's `-8.2735` to within a small, expected difference from an independent reconstruction (both measure the same large, negative, un-hedging-driven offset).

```
I_max (literal §4.6 greedy)  = -30.1584             [measured]
I_min (literal §4.6 greedy)  = -35.0173             [measured]
```

**These are [inferred — defective, see I-386]**, not a certified bound. `I-386` (HIGH, DATA-IMPL-014) already demonstrated the literal §4.6 greedy construction is not a valid upper bound (`I_max < I_0`, and exhaustive `T=10` brute force shows the greedy misses the true optimum). **This dispatch's own numbers reproduce the identical qualitative defect a third time, independently** (`-30.16 < I_0 = -8.26` here, exactly the same internal contradiction DATA-IMPL-014 found at `-20.24 < -8.27`) — different magnitude (expected: two independent reconstructions, neither sharing code until this dispatch's own module existed), same defect. **This dispatch does not repair I-386** (hard stop 3) and does not re-file it.

**Test D-4** (brute force at `T=10`) was run exactly as specified: constructed a synthetic case with a baseline series and a SEPARATE per-bar sensitivity term (matching DATA-IMPL-014's own construction shape), confirmed the greedy assignment does **not** match the true combinatorial optimum found by exhaustive search over all `10!` permutations — reconfirming I-386 at the unit-test scale, not discovering a new instance of it.

---

## 6. THE 30 ACCEPTANCE TESTS — RED-FIRST, ALL 30 CONFIRMED

**Location:** `harness/tests/test_c11_null_calibration.py` (30 tests) · driver: `research/work/c11_red_first_driver.py` · full machine-readable log: `research/work/c11_red_first_log.json`.

**Method.** For 27 of 30 rows, the driver applies the test's own named mutation (a `monkeypatch`-style attribute/function substitution on the actual production module — `castellan.reconstruction`, `castellan.nullcal`, `castellan.stats`, `castellan.registry`, or, for C-4/E-4, a genuine temporary edit of the standalone script the row targets, reverted after), runs **only that test**, confirms **RED** (must fail), reverts, confirms **GREEN** (must pass). For 3 rows (D-1, D-2, D-5), the test itself constructs a correct and a deliberately-wrong computation **inline** and asserts they diverge — disclosed as `inline_dual_construction` rather than forced into an external monkeypatch, because the "implementation" being mutated for these rows is a local closure, not a module call site.

**Result: 30/30 confirmed — every row's named mutation produced RED, and reverting it restored GREEN. Zero rows required reporting as "no constructible failing mutation."**

| # | Test | Mutation | RED | GREEN |
|---|---|---|:-:|:-:|
| A-1 | constant schedule vs. trial 1 blob | `COST_MODEL` → 50x perp cost | fail | pass |
| A-2 | scratch anchor vs. engine | `EXECUTION_LAG` → 2 | fail | pass |
| A-3 | registry hash, ±1 event row | `log_event` inserts twice | fail | pass |
| A-4 | costs read at run time | hardcoded-cost reconstruction variant | fail | pass |
| A-5 | `periods_per_year=365` persisted | `PERIODS_PER_YEAR` → 252 | fail | pass |
| A-6 | no outer grant around `run_backtest` | nested-check removed from `write_grant` | fail | pass |
| B-1 | `w∈[0,1]` | lower clip removed | fail | pass |
| B-2 | `w=1` wherever `z≤d` | `D_SIZING` → -1.0 (test's own oracle fixed at sealed `d=1.0`) | fail | pass |
| B-3 | sizing unit values | `K_SIZING` → 0.25 | fail | pass |
| B-4 | R-1 burn-in, first 30 bars | `LOOKBACK` → 10 | fail | pass |
| B-5 | R-2, exactly 30 bars from 2025-09-18 | `R2_TRIGGER_LEN_DAYS` → 20 | fail | pass |
| B-6 | band both branches occur | `BAND` → 2.0 (unreachable) | fail | pass |
| B-7 | funding sha256 == trial 1's | expected-hash constant corrupted | fail | pass |
| B-8 | index 2,415 bars, terminal 2026-08-11 | settled cutoff → 2026-08-12 | fail | pass |
| C-1 | joint pairing, one common permutation | independent per-asset permutations | fail | pass |
| C-2 | `mean(w*)==mean(w)` exact, `c` invariant | swapped for stationary (with-replacement) draw | fail | pass |
| C-3 | never the identity; rejection branch forced | identity-redraw check removed | fail | pass |
| C-4 | reproducibility, 2 processes, same seed | seed sourced from `time.time()` | fail | pass |
| C-5 | exactly 81 blocks, bijection | off-by-one block size (`L+1`) | fail | pass |
| C-6 | 8 cells from independent spawn children | same spawned child reused ×8 | fail | pass |
| D-1 | worst-20 from the surrogate itself | inline: reused-index-set variant vs. correct, asserted to differ | (inline) | pass |
| D-2 | `M_b<0` guard, else INSUFFICIENT-DATA | inline: guard exercised on synthetic all-positive series | (inline) | pass |
| D-3 | `I_0` computed, NOT `≈0` | `compute_i0` → constant `1e-9` | fail | pass |
| D-4 | greedy vs. brute force at T=10, weak invariant only | multiset-preservation broken in greedy | fail | pass |
| D-5 | null percentiles + tie count | inline: rounded (degenerate) copy vs. continuous, tie fraction must rise | (inline) | pass |
| E-1 | reduction to `sr_tstat_nw` (as measured: exact `√(T/(T-1))` scale — **I-391**) | `sr_tstat_nw` Bartlett weight off-by-one | fail | pass |
| E-2 | same kernel/divisor, lag-invariant scale factor | same mutation as E-1 | fail | pass |
| E-3 | joint computed by distinct path from product | `joint_survival_rate` → returns product as joint | fail | pass |
| E-4 | I-044: no `print()` asserts a conclusion | forbidden word inserted into script's own print line | fail | pass |
| E-5 | disclosure grid, all 8 cells present | `disclosure_grid_cells` → returns 1 cell | fail | pass |

**Two rows measured a genuine discrepancy against SPEC-005's own literal text while still passing as red-first tests, filed rather than silently smoothed:**
- **E-1** (**I-391**, LOW): the spec's literal claim ("equals... to 1e-10") does not hold bit-for-bit; the true, measured relationship is an exact, lag-invariant `√(T/(T-1))` scale factor, confirming the same underlying kernel rather than numerical identity. The test asserts the TRUE (measured) relationship, not the spec's literal one.
- **D-4**: the "verified against brute force" row does not assert equality (I-386 already shows it is false); it asserts the one true, defect-independent invariant (brute force ≥ any enumerated candidate) and explicitly reports, rather than forces, the equality-or-not finding.

---

## 7. THE FIVE NUMBERS, THE BAND, AND THE X-OVERRIDE

### 7.1 The primary cell (circular block permutation, `L=30`, `B=10,000`)

| Figure | Value | Mark |
|---|---:|---|
| **`α̂₂`** (replaces the assumed `≤0.10`) | **0.0**, Clopper–Pearson 95% CI **[0.0, 0.00037]** | [measured] |
| **`α̂₁`** (leg-(i) estimator, CALIBRATION ONLY — never a leg-(i) result, hard stop 2) | **0.119** | [measured] |
| **`α̂_joint`** | **0.0** | [measured] |
| **`α̂₁ × α̂₂`** (the product) | **0.0** | [measured] |
| **The independence gap** (`α̂_joint − α̂₁·α̂₂`) | **0.0** | [measured] |

**On the gap:** in this specific measurement the gap is degenerate (both terms are `0.0`) because `α̂₂` itself floors at zero on every one of 10,000 primary-cell draws — **not** because the two legs turned out independent. **I-382's concern (positive dependence pushing the true joint above the naive product) is not falsified by this zero; it is simply not exercisable when one marginal is exactly zero.** Separately, and this is the more consequential number this dispatch surfaces: **`α̂₁ = 0.119` calibration-only is roughly 90× the sealed `≤0.0013` assumption** — filed as **I-389** (HIGH), escalated per I-382's own precedent, because it bears directly on how much confidence step 3's leg-(i) evaluation (same estimator, same pairing structure) should carry, without this dispatch stating or implying any leg-(i) verdict.

**Per I-382's Principal-adopted labelling rule:** the sealed `PREREG-002` §5.3 figure `1.3×10⁻⁴` is **THE INDEPENDENCE-ASSUMPTION FIGURE**, marked `[assumed — superseded by C11]`, never deleted, never restated as the joint rate. **The measured joint rate is `α̂_joint = 0.0`**, reported beside it, per that rule — in this instance numerically *below* the sealed figure, which is not the direction I-382 warned about (I-382's concern was the sealed figure UNDERSTATING the true joint rate; here the measured joint is lower, driven entirely by `α̂₂`'s own floor, not by the independence assumption resolving favourably).

### 7.2 The band (SPEC-005 §5.2)

**Band A (`α̂₂ ≤ 0.10`).** Measured `α̂₂ = 0.0`, decisively inside Band A — the assumption holds, more strongly than assumed. §5.3's sealed term is marked `[measured, superseded]` per §5.1's rule; no further Gate 1 consequence attaches (Band A carries none).

**Robustness of this band call:** `α̂₂ = 0.0` on **every one of the 8 disclosure-grid cells** (`L∈{21,30,60,90} × {permutation, stationary}`), under the **alternative denominator** (`|M_s|`), and under the **cost-free variant** — this is not a boundary call sensitive to construction choice.

### 7.3 The X-override — UNRESOLVED, stated per hard stop 2

**Band X cannot be resolved by this dispatch, and this seat does not claim it.** `I-386` (HIGH, open) already established SPEC-005 §4.6's `I_max` construction is not a valid bound. Of the two Band-X conditions:

- **`I_0 ≥ 0.25`** (spared by construction): **cleanly ruled out** — `I_0 = -8.26`, nowhere near `0.25`. [measured]
- **`I_max < 0.25`** (fires on every possible world): **UNDETERMINED** — the only instrument SPEC-005 names for this (`I-386`'s literal greedy construction) is demonstrated invalid, and this dispatch's own independent measurement (`I_max = -30.16` literal, defective) reconfirms rather than repairs that. DATA-IMPL-014's separately-computed VALID-BUT-LOOSE bound (`I_max ≤ 0.593`, frictionless, exposure-unconstrained) straddles `0.25` and settles nothing either. **This seat does not certify Band X in either direction.**

---

## 8. The scratch-registry rehearsal, the live write, and registry before/after

### 8.1 Rehearsal (mandatory, run before any live touch)

`research/work/c11_rehearsal_and_live_write.py --rehearse`, against a fresh scratch registry, on a 400-bar REAL slice of the live panels (not synthetic): `open_hypothesis` under its own `REGISTER_HYPOTHESIS` grant; confirmed an outer `LOG_TRIAL` grant wrapped around `run_backtest` raises `RegistryWriteGrantNestedError` (I-374 avoided); ran `run_backtest` with **no** outer grant (self-grants correctly, `periods_per_year=365` persisted); logged one `null_calibration` event under its own `LOG_EVENT` grant; ran `audit_write_grants()` — chain intact, 3 grants, zero orphan rows.

```
REHEARSAL_CLEAN: true                               [measured]
```

### 8.2 The live write — THE ONE AUTHORIZED WRITE

**Grant:** reason `LOG_EVENT` (the closed vocabulary's narrowest admitting reason, `registry.py:152`), dispatch `S4-D-033`, token `head-of-data-infra:S4-D-033:c11-null-calibration` (an attribution field recorded in the `write_grants` row, per `registry.py`'s own docstring — "a token exists to be RECORDED, not to authenticate" — never a validated secret; `CASTELLAN_REGISTRY_WRITE` confirmed unset). **Not scripted as a self-granting path; called by hand against the read signature (I-374's corrective).**

```
event_id: 10
write_grants.grant_id: 12, reason=LOG_EVENT, dispatch=S4-D-033, outcome=CLEAN, writes=1
```

**Registry before/after:**

| | Before | After |
|---|---|---|
| `sha256(book/registry.db)` | `694634bb4b758f7dcfeba94335c7311315a4a65b212779517af8cdc8a36bcff8` | `5bab9d379cd1aabc79ff32dd289cb3deef853b66e663df4b5a6dab5031270fbb` |
| `events` count | 9 | 10 |
| `write_grants` count | 11 | 12 |
| `trials` count | **1** | **1 — UNCHANGED** |
| `hypotheses` count | 1 | 1 |

**Audit after the write:** `chain_intact=True`, `unclosed_grants=[]`, `orphan_rows` all empty [measured] — the difference between before/after is exactly the one `null_calibration` event row and its one `write_grants` row (A-3's own property, confirmed on the live database, not merely in the test suite).

**Minor disclosed defect (I-392, LOW):** the live event's `alpha_2_ci95` field recorded `null` due to a dict-key mismatch in the write script (read from `results["primary"]`, where the CI is not stored, instead of `results["disclosure_grid_8_cells"]["permutation_L30"]`). Not repaired by a second write (only one live write is authorized); the correct interval is recoverable via the event's own `full_results_artifact_sha256` pointer into `research/work/c11_results.json`, and is reported correctly in §7.1 above.

---

## 9. Suite before/after, and where SPEC-005 and this deliverable disagree

Run **unpiped**, per `CLAUDE.md`'s binding instruction (`python3 -m pytest harness/tests -q`, exit status read directly):

| | passed | failed | total |
|---|---:|---:|---:|
| **Before** [measured, this dispatch's own first run] | 363 | 22 | 385 |
| **After** [measured] | **393** | **22** | **415** |

**The 22 failures are the same 22 by name** (`test_carry_accounting.py` ×13, `test_holdout_p1.py` ×1, `test_minbtl_serial.py` ×2, `test_registry_write_grant.py` ×1, `test_seeded_n.py` ×2, `test_carry_accounting.py::test_t*` — identical set before and after, confirmed by exact test-id diff, matching DATA-IMPL-015's own baseline exactly). **+30 passed (this dispatch's own suite), +0 failed, +0 regressed.**

**Where this deliverable and SPEC-005 disagree — two places, both disclosed as findings, neither a repair of SPEC-005 itself (not edited):**
1. **§7.5 E-1's literal "equals to 1e-10"** does not hold bit-for-bit against the actually-implemented `ols_alpha_tstat_hac`; the true relationship is an exact `√(T/(T-1))` scale factor (**I-391**, LOW).
2. **§4.6's `I_max`/`I_min` construction** is not a valid bound (**I-386**, already open, not this dispatch's finding — reconfirmed, not repaired, per hard stop 3).

No other divergence found. SPEC-005 governs throughout; where its literal text and this seat's measurement diverged, SPEC-005's construction was implemented exactly as specified and the divergence is reported as a finding against the spec's *claim*, not resolved by silently substituting different arithmetic.

---

## 10. Findings filed (I-389 through I-392, allocated against the true repo-wide max `I-388`)

| # | Sev | One line | Owner |
|---|---|---|---|
| **I-389** | **HIGH** | Calibration-only `α̂₁ = 0.119`, ~90× the sealed `≤0.0013` assumption — never a leg-(i) verdict, but Validation should see it before step 3 runs leg (i). | quant-validation / Principal |
| **I-390** | MEDIUM | `c`'s engine-literal formula is not exactly permutation-invariant (O(1/T) edge effect); ruled to the plain time-average instead, disclosed on the module's own docstring. | head-of-data-infra (closed) |
| **I-391** | LOW | `ols_alpha_tstat_hac`'s degenerate-regressor reduction differs from `sr_tstat_nw` by an exact `√(T/(T-1))` factor, not bit-identical as SPEC-005 E-1 literally states. | quant-validation |
| **I-392** | LOW | Live event's `alpha_2_ci95` recorded `null` (key mismatch); recoverable via the event's own pinned artifact hash, not repaired by a second write. | head-of-data-infra (closed) |

`I-386`, `I-387`, `I-388` were read and, where relevant, reconfirmed or discharged — none re-filed, none edited.

---

## 11. What this seat did NOT do

- **Ran no leg of F-002.** No step 3, no step 3b. `ols_alpha_tstat_hac` was run **only** on the 10,000 surrogates against the realized `R_bench` (calibration only, hard stop 2) — never on the realized alignment, never presented as a leg-(i) result.
- **Logged zero new trials.** `trials` count is `1` before and after (trial 1, unchanged). C11 cost `0` of its `≤2` authorized.
- **Made exactly one live registry write** — the `null_calibration` event (`event_id=10`), under its own `LOG_EVENT` grant, called by hand.
- **Did not wrap `run_backtest` in any outer grant**, scratch or live, anywhere (verified by test A-6 and by the rehearsal's own explicit nested-grant check).
- **Did not repair I-386.** Computed and reported the literal §4.6 construction's output, labelled defective, exactly as hard stop 3 requires.
- **Did not edit** `PREREG-002`, any `REGISTRATION-PAYLOAD-*`, `VALIDATION-SPEC-005`, `logs/DECISION_RECORD.md`, or `CLAUDE.md`. No seal, no passphrase, no `git add`/`commit`.
- **Did not use the Task/Agent tool.** Tools used: `Read`, `Write`, `Edit`, `Bash`, `Grep`. Within the declared set.
- **Did not claim Band X in either direction.**

---

## 12. Return to the CIO

- **`α̂₂ = 0.0`** [measured], Clopper–Pearson 95% CI `[0.0, 0.00037]`, robust across all 8 disclosure cells, the alternative denominator, and the cost-free variant.
- **`α̂₁ = 0.119`** [measured] — **calibration-only, never a leg-(i) result** — ~90× the sealed assumption; escalated as **I-389 (HIGH)**.
- **`α̂_joint = 0.0`**, **product = 0.0`**, **gap = 0.0`** [measured] — degenerate because `α̂₂` itself floors at zero; I-382's independence concern is not falsified, merely not exercisable at this measurement.
- **Band A** (`α̂₂ ≤ 0.10`) — the assumption holds, decisively.
- **Band X: UNRESOLVED**, explicitly not claimed — `I_0 ≥ 0.25` cleanly ruled out; `I_max < 0.25` undetermined pending I-386's repair (Validation's, not this dispatch's, to make).
- **B-7: PASS**, no data drift.
- **Registry:** `sha256` `694634bb…` → `5bab9d37…`; events `9→10`; write_grants `11→12`; **trials `1→1`, unchanged**.
- **Suite:** `363/22/385 → 393/22/415`, the same 22 failures, zero regressions.
- **Findings filed:** `I-389` (HIGH), `I-390` (MEDIUM, closed), `I-391` (LOW), `I-392` (LOW, closed).
- **Reusable module checked in:** `harness/castellan/reconstruction.py`, `harness/castellan/nullcal.py`, `harness/tests/test_c11_null_calibration.py` — closing I-388's substance.
- **Confirmed: no step-3 verdict of any kind was produced, and no new trial was logged.**
