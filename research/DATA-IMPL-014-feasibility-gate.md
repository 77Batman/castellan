# DATA-IMPL-014 — THE FEASIBILITY GATE: `I_max`, `I_0`, `I_min`

**Head of Data & Infrastructure · dispatch S4-D-031 · 2026-09-15**
**Scope: `VALIDATION-SPEC-005-c11-null-calibration.md` §4.6 ONLY — the two-sided feasibility check that must run before step 3 (legs i/ii of F-002) spends E2. Nothing else was run.**
**Zero new trials. Zero writes to `book/registry.db`. `book/pit.db` opened read-write-path-only, called for `asof`/`pit_price_panel`/`pit_funding_panel` exclusively — never `ingest`, never `set_holdout_ceiling`. No seal, no `open_hypothesis` against the live registry, no vault write, no `git add`/`commit`.**

---

## 0. What this document is, and is not

This is the deterministic, zero-trial pre-check the Principal ordered ahead of step 3: **does the sealed 25% margin on F-002 leg (ii) admit any possibility of the strategy sparing it (`I_max`), and does the un-hedging structure of the position spare it by construction alone (`I_0`)?** It is not F-002, not a leg-(ii) result, not a survival claim, and it runs no leg of the falsifier. Per hard stop 1 of the dispatch, step 3, step 3b and the C11 null distribution are explicitly out of scope and were not touched.

**Headline, stated first because it changes how the rest of this document should be read:** `I_0` is measured and is unambiguous. **`I_max`/`I_min`, computed by the literal construction `VALIDATION-SPEC-005` §4.6 names, are demonstrated defective** — verified two independent ways, both reported below — and this seat cannot certify a Band X (`I_max < 0.25`) verdict using that construction. A mathematically valid but loose alternative bound is reported in its place; it does not settle Band X either, in the permissive direction. **Findings filed: `I-386` (HIGH), `I-387` (MEDIUM).**

---

## 1. Provenance and admissibility checks

### 1.1 Documents read in full or at the cited sections

| Artifact | Sections | Used for |
|---|---|---|
| `agents/head-of-data-infra.md` | full | operating definition for this seat |
| `CLAUDE.md` | full | orchestrator binding, harness discipline |
| `research/VALIDATION-SPEC-005-c11-null-calibration.md` | full, with §4.5–§4.6 and acceptance rows D-3/D-4 read closely | governing spec for this dispatch |
| `research/PREREG-002-crypto-funding-basis.md` | §5.2, §5.3, §6.1–§6.3, §21 | sealed statement, universe, position construction, numeric literals |
| `research/DATA-IMPL-013-f002-step2.md` | full | trial 1's exact `run_backtest` call, its workarounds (I-374, I-375), its measured `R_bench` |
| `harness/castellan/{engine,costs,data,registry}.py` | source read | exact arithmetic to reproduce off-engine |

### 1.2 The B-7 data-drift STOP — checked first, as instructed

`VALIDATION-SPEC-005` test B-7 requires the funding panel's `sha256` to equal trial 1's logged `funding_panel_sha256`. Rebuilt fresh via `pit_funding_panel(store, "binanceusdm", ["BTC/USDT:USDT","ETH/USDT:USDT"], C, idx)` against the live, currently-mutating `book/pit.db`:

```
fresh funding sha256:   971d037d442cf1a5fb93ad2c797f54938fd6250cccd2079b903d8c853a58c791
trial 1 (config_json):  971d037d442cf1a5fb93ad2c797f54938fd6250cccd2079b903d8c853a58c791
MATCH: True
```

**[measured] B-7 PASSES.** No data drift between trial 1 and this computation. `book/pit.db` grew during this session (from the launchd Polymarket-capture agents, per `VALIDATION-SPEC-005`'s own operational note) — confirmed unrelated to the `binanceusdm` funding series used here. `book/registry.db` mtime is unchanged across this entire dispatch (`Sep 15 12:50:03`, the same baseline the spec itself recorded before this dispatch opened it) — **[measured] confirming zero writes to the live registry.**

**B-8** (index is trial 1's: 2,415 bars, terminal `2026-08-11`, settled-only): **[measured] PASSES** — rebuilt index is 2,415 bars, `2020-01-01 → 2026-08-11`, identical construction to `DATA-IMPL-013` §3.

### 1.3 Engine-parity checks (A-1/A-2 style), performed as the mandatory scratch rehearsal

Per the dispatch's instruction that the scratch rehearsal is load-bearing for any first-of-kind off-engine reconstruction:

- **A-1 style, off-engine vs. trial 1's stored blob.** Off-engine reconstruction of `R_bench` (constant `w ≡ 1.0`, both assets, spot fixed at 0.5/0.5, perp at −0.5/−0.5, per §3.2's formulas) was run against the freshly-built panels and compared to trial 1's stored `returns_blob` (`float32`, decoded via `np.frombuffer`). **[measured] max abs diff = 3.69 × 10⁻¹⁰** — within `float32` storage precision, confirms the reconstruction and trial 1 are the same computation on the same data. Reconstructed annualized net return: **+12.681%/yr**, matching `DATA-IMPL-013` §6's reported figure exactly.
- **A-2 style anchor, varying schedule, real engine, scratch registry.** Built `target_weights` from the **realized, varying** `w_held(t)` schedule (207 bars with `|Δw| > 0`, i.e. the turnover-cost branch is genuinely exercised), ran it through the real `castellan.run_backtest` against a **scratch `TrialRegistry`** in a temp directory (never `book/registry.db`), and compared to the off-engine reconstruction of the identical schedule. **[measured] max abs diff = 0.0 (exact).** No outer `write_grant` was wrapped around `run_backtest` (I-374 avoided); the one `open_hypothesis` call on the scratch registry used its own explicit `REGISTER_HYPOTHESIS` grant. The scratch temp directory was deleted after the run. **This is the mandatory first-of-kind rehearsal, and it passed** — the off-engine reconstruction used for every figure below is bit-exact against the sanctioned engine.
- `PITStore` was opened via the ordinary read-write path (I-375 stands, not repaired here, per hard stop 4) and only `asof`/`pit_price_panel`/`pit_funding_panel` were called.

**What was not run:** the full 30-test acceptance suite (Groups A–E) that governs the complete C11 calibration. This dispatch is scoped to §4.6 only; Groups A/B/C/E beyond what is reported above are out of scope and not claimed as passing.

---

## 2. The realized schedule `w(t)`

Built per §3.4's rulings (R-1 burn-in, R-2 the named K7 trigger, R-3 the turnover band), on the sealed literals `k = 0.5`, `d = 1.0`, `band = 0.54`, `lookback = 30`, `w_max = 1.0` (`PREREG-002` §21, confirmed against the sealed `statement` field directly, not narrated from §6.2's prose — the two agree on every numeric literal used here).

| | BTC | ETH |
|---|---:|---:|
| Bars at `w_held = 1.0` | **1,736 / 2,415 (71.9%)** | **1,045 / 2,415 (43.3%)** |
| Bars at `w_held < 1.0` | 679 | 1,370 |
| Burn-in bars (R-1, `z` undefined, first 30) | 30 | 30 |
| R-2 forced bars (2025-09-18, 30 days, both assets) | 30 | 30 |
| Band-triggered rebalances (R-3, strict `> 0.54`) | 126 | 138 |
| Distinct de-scaling episodes (contiguous runs of `w_held < 1.0`) | 42 | 43 |
| `w_held` range | `[0.0, 1.0]` | `[0.0, 1.0]` |
| Percentiles [1, 5, 25, 50, 75, 95, 99] | `0.00, 0.568, 0.861, 1.00, 1.00, 1.00, 1.00` | `0.00, 0.541, 0.894, 0.956, 1.00, 1.00, 1.00` |
| `w̄` (time average) | **0.8804** | **0.8774** |

**[measured] Both branches of the band rule (R-3) occur in-sample** (band-hold and band-trigger both observed, 126/138 triggers on 2,415 bars) — B-6's guard condition is satisfied; the schedule is not degenerate at constant 1.0.

**Exposure-match scalar, per §3.3, on held (lagged) positions as the engine computes them:**

```
gross_exposure_strat(t) = 1.0 + 0.5·w_BTC(t−1) + 0.5·w_ETH(t−1)
c = mean_t[gross_exposure_strat(t)] / 2.0 = 0.93927   [measured]
```

---

## 3. `M_b`, the guard, and `I_0`

`M(x)` = mean of the 20 smallest elements of `x` (§4.1). `R_bench_scaled = c · R_bench`; since `c > 0`, `M_b = c · M(R_bench)` exactly (order-preserving scalar).

```
M_b = -0.0018009                                    [measured]
```

**Guard D-2:** `M_b < 0` — **[measured] satisfied** (`M_b = -0.0018009 < 0`). The statistic is defined; this is not INSUFFICIENT-DATA.

**`I_0`** — `R_strat` at the constant schedule `w* ≡ w̄` (0.8804 BTC, 0.8774 ETH), both assets, every bar, built and validated exactly as in §1.3:

```
M_s (constant w = w̄) = -0.016700                    [measured]
I_0 = (M_s - M_b) / |M_b| = -8.2735                 [measured]
```

**D-3 is satisfied on its own terms: `I_0` is computed, reported, and is emphatically not `≈ 0`.** It is, in fact, dramatically more negative than the sealed spec's own framing anticipates. `VALIDATION-SPEC-005` §4.6 predicted a non-zero `I_0` because the constant-`w̄` position is net long spot while `R_bench_scaled` is delta-neutral (I-377's un-hedging bias). The measured **sign and magnitude** go further than that framing states: **the constant-`w̄` position's own worst-20-day mean (−1.67%) is materially worse than the exposure-matched benchmark's (−0.18%, scaled)**, i.e. the un-hedging offset alone makes the tail comparison **harder to spare, not easier**, at this point in the parameter space. This is the opposite direction from the concern §5.5(d)'s original repair guarded against (leg (ii) being spared too easily by construction) — here the construction effect runs the other way. **Filed as part of `I-386`'s disposition below; a distinct positive-direction bias was anticipated, a negative one this large was not named in `VALIDATION-SPEC-005`.**

**Reading against the pre-committed bands (§5.2 mirror condition):** `I_0 = -8.2735` is nowhere near `≥ 0.25` — **the "spared by construction" mirror-defect condition of Band X does not hold.** This is unambiguous and needs no further instrument.

---

## 4. `I_max`, `I_min`, and why the named construction cannot be certified

### 4.1 The literal §4.6 construction, as specified

*"Assign the realized multiset of `w` values to bars greedily: smallest `w` on the most-negative bars, largest on the least."* Implemented literally: rank all 2,415 bars by realized `R_bench(t)` ascending (rank 0 = most negative); sort each asset's realized `w_held` multiset ascending; assign `w*_asset(rank) = w_held_sorted[rank]` (mirrored, descending, for `I_min`). Position-level construction validated bit-exact against the engine in §1.3.

```
I_max (literal §4.6 greedy, engine, full cost)      = -20.2425     [measured]
I_max (literal §4.6 greedy, gross+carry only)       = -20.1389     [measured — disclosure: cost is not the driver]
I_min (literal §4.6 greedy, mirrored)               = -47.0427     [measured]
```

### 4.2 Why this cannot be reported as the feasibility bound

**Internal inconsistency.** §4.6 states `I_max` is *"a deterministic upper bound on `I` over every schedule with this average exposure."* The constant-`w̄` schedule used for `I_0` (§3 above) has, by construction, exactly the per-asset average exposure `w̄` — the same phrase (*"average exposure held fixed"*) is used elsewhere in the sealed spec (§5.5(e), of the C11 bootstrap) to mean matching the **mean**, not the exact multiset. Under that reading, `I_0`'s schedule is a member of the class `I_max` is defined to dominate. **`I_max = -20.24` is less than `I_0 = -8.27` — a supremum coming in below a value its own class demonstrably attains is not a supremum.** (§4.6's phrasing is genuinely ambiguous between "every permutation of this exact multiset" and "every schedule matching this mean" — filed separately as `I-387` — but the next check removes the ambiguity entirely.)

**Independent, unambiguous confirmation — D-4's own prescribed brute-force check, run exhaustively.** At `T = 10`, on a synthetic series (`baseline(t)`, per-bar sensitivity `s(t)`, and a 10-element `w`-multiset, all `rng.default_rng(42)`-generated), brute force over **all `10! = 3,628,800` permutations** of the exact multiset was compared against the literal §4.6 greedy-by-`R_bench` rule:

```
greedy (spec heuristic) M_max = -0.0125037
BRUTE FORCE true max of M     = -0.0101913     <- strictly better than the greedy result
MATCH: False

greedy (spec heuristic) M_min = -0.0255320
BRUTE FORCE true min of M     = -0.0286758     <- strictly worse than the greedy result
MATCH: False
```

**The greedy-by-`R_bench` heuristic does not find the true combinatorial optimum in either direction, even restricted to exact permutations of the given multiset — the narrower, unambiguous reading of "this average exposure."** A second heuristic (sorting by the per-bar sensitivity term the payoff actually depends on, rather than by `R_bench` itself) scored `-0.0119`, closer to the brute-force truth (`-0.0102`) than the spec's own rule, but **still did not match it exactly.** The mean of the `k` smallest elements of a linear-in-`w` series is a concave function of the assignment (a minimum over subsets is concave), and its maximum under a multiset-permutation constraint is a genuine combinatorial optimization — **no single-key sort is shown to solve it exactly, on this evidence, and `VALIDATION-SPEC-005` does not derive one; it asserts one.**

**D-4 disposition: the test was performed, exhaustively, as specified. It did not pass — the greedy construction fails to reproduce the brute-force optimum. This is reported as the finding it is (`I-386`, HIGH), not smoothed into a caveated pass.**

### 4.3 A mathematically valid (but loose) alternative bound

Because the named construction cannot be trusted, and because the feasibility question ("can 25% be reached at all") is precisely what a **valid, even if not tight, upper bound** can still answer in one direction: relax the problem to *any* `w ∈ [0, 1]` chosen independently per bar and per asset (dropping both the turnover-cost term and the exposure-match constraint entirely). This is a strict superset of the true feasible set, and dropping cost can only inflate `I` (cost only subtracts), so its optimum is **provably ≥ the true `I_max`** and **provably ≤ the true `I_min`**:

```
I_relaxed_max = +0.5933     [measured — valid, loose, generous upper bound]
I_relaxed_min = -78.8790    [measured — valid, loose, generous lower bound]

Sanity check: I_relaxed_max (0.593) >= I_0 (-8.274)?  TRUE  [as it must be]
```

**This is the only `I_max`-type figure in this document that is both computed and provably valid.** It does **not** clear below 0.25 — it sits at 0.593, comfortably above — so it **does not support** "leg (ii) fires on every possible world" (the Band X `I_max < 0.25` condition). But because it is deliberately loose (frictionless, exposure-unconstrained), **it also does not confirm feasibility** — the true, correctly-constrained `I_max` could in principle be anywhere in `(I_0, I_relaxed_max] = (-8.274, 0.593]`, a range that straddles 0.25 and settles nothing.

---

## 5. Verdict

| Quantity | Value | Mark | Status |
|---|---:|---|---|
| `w̄` (BTC, ETH) | 0.8804, 0.8774 | [measured] | — |
| `c` | 0.93927 | [measured] | — |
| `M_b` | −0.0018009 | [measured] | guard D-2 passes (`< 0`) |
| `I_0` | **−8.2735** | [measured] | not ≈0 (D-3 satisfied); far below the `≥0.25` mirror band |
| `I_max` (§4.6 literal) | −20.2425 | [measured] | **[inferred] defective — fails internal consistency and D-4 brute force; not usable for Band X** |
| `I_min` (§4.6 literal) | −47.0427 | [measured] | same defect, mirrored |
| `I_max` (valid loose bound) | +0.5933 | [measured] | valid but not tight; does not confirm or rule out `I_max < 0.25` |
| B-7 (`funding_panel_sha256`) | match | [measured] | **PASS — no data drift** |
| B-8 (index) | 2,415 bars, `2026-08-11` terminal | [measured] | PASS |
| D-4 (brute force @ T=10) | mismatch, exhaustive | [measured] | **the named construction FAILS this test** |

**Band X verdict: NEITHER condition is confirmed, and the instrument named for one of them is broken.**

- **`I_0 ≥ 0.25` (spared by construction):** **[assumed → ruled out, measured].** `I_0 = -8.27` is nowhere near this. Confirmed not to hold, cleanly, no caveats.
- **`I_max < 0.25` (fires on every possible world, T-18):** **[inferred — cannot be certified].** The construction `VALIDATION-SPEC-005` names for this test does not compute a valid bound (§4.2, two independent proofs). A valid substitute bound is loose and lands on the permissive side of 0.25 (0.593), which means it fails to *confirm* Band X but also cannot rule it out. **This seat cannot report a Band X `I_max` verdict with confidence, and reporting the literal-construction number (−20.24) as though it settled the question would itself be the kind of defect this gate exists to catch.**

**What this means for step 3, stated plainly and not softened:** this is not a "proceed, the gate is clear" reading. `I_0`'s magnitude (−8.27) independently establishes that the un-hedging offset is a first-order effect on leg (ii)'s comparison — larger and in the opposite direction from what §4.6's own framing anticipated — and the feasibility question §4.6 was built to answer (is 25% reachable at all) is **open, not closed**, pending a corrected `I_max` construction. Per §5.2's own rule, thresholds do not move and step 3 still runs the sealed falsifier in full regardless of this gate's outcome — but the Principal's stated reason for ordering this gate before step 3 (*"the family learns it before spending E2"*) is only served if the gate's own arithmetic is trustworthy, and for `I_max`/`I_min` as specified, it is not.

---

## 6. Findings filed

| # | Sev | Summary | Owner |
|---|---|---|---|
| **I-386** | **HIGH** | `VALIDATION-SPEC-005` §4.6's greedy `I_max`/`I_min` construction does not compute a valid bound — measured `I_max < I_0` (internally inconsistent under the document's own "average exposure" language) and confirmed by exhaustive `T=10` brute force (3,628,800 permutations) that the greedy-by-`R_bench` rule misses the true combinatorial optimum in both directions. Band X's `I_max < 0.25` leg cannot presently be certified. | quant-validation |
| **I-387** | MEDIUM | §4.6 does not disambiguate "every schedule with this average exposure" between exact-multiset permutation and mean-`w̄`-matching — a genuine ambiguity, though I-386's brute-force result holds under either reading. | quant-validation |

Both filed against the true repository-wide maximum claimed issue number (`I-385`, confirmed by enumeration over the whole tree, not the log's highest heading — per the dispatch's own instruction and I-366's rule). Neither `PREREG-002`, `REGISTRATION-PAYLOAD-*`, `VALIDATION-SPEC-005`, `logs/DECISION_RECORD.md`, nor `CLAUDE.md` was edited.

---

## 7. Where `VALIDATION-SPEC-005` and this seat's execution disagree

**One place, and it is the substance of §4.** The spec states its §4.6 construction *is* a deterministic upper/lower bound. This seat's measurement shows it is not, on the realized data, verified two independent ways. This document does not resolve the disagreement by choosing a different construction on Validation's behalf — it reports the literal construction's output, proves it cannot be the claimed bound, supplies a mathematically valid (if loose) substitute, and returns the open question to Validation as `I-386`.

No other divergence was found between the spec and the frozen `PREREG-002` document: the sealed numeric literals (`k=0.5`, `d=1.0`, `band=0.54`, `lookback=30`, `w_max=1.0`), the position construction (spot fixed at 1.0 unit total, only the perp leg scaled by `w(t)`), and the universe (BTC+ETH only, SOL dropped) were all confirmed directly against the sealed `statement`/`universe` fields in `book/registry.db`, not narrated from prose, and all agree with `VALIDATION-SPEC-005`'s reading of them.

---

## 8. What this seat did not do

- Ran no leg of F-002, no step 3, no step 3b, no C11 null distribution.
- Made no write to `book/registry.db` (confirmed by unchanged file mtime across the dispatch) and no write to `book/vaults/`.
- Did not seal, did not call `open_hypothesis` against the live registry, did not touch a passphrase.
- Did not edit `PREREG-002`, `REGISTRATION-PAYLOAD-*`, `VALIDATION-SPEC-005`, `logs/DECISION_RECORD.md`, or `CLAUDE.md`.
- Did not run the full 30-test C11 acceptance suite (out of this dispatch's scope) — only the engine-parity rehearsal (§1.3) and the D-3/D-4 checks this dispatch was scoped to.
- Did not spawn a subagent. Tools used: `Read`, `Write`, `Edit`, `Bash`, `Grep`. Within the declared set.
- Did not soften, omit, or quietly repair the `I-386` finding to produce a cleaner-looking verdict.
