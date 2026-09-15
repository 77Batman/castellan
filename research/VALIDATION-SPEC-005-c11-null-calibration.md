# VALIDATION-SPEC-005 — C11, THE LEG-(ii) NULL CALIBRATION

**Head of Quantitative Validation · dispatch S4-D-030 · 2026-09-15**
**Status: SPECIFICATION ONLY. Zero trials run. Zero registry writes made. No backtest executed by this seat.**
**Number checked free before writing: `research/` holds `VALIDATION-SPEC-001` … `-004`; `-005` was unused [measured — directory enumeration, 2026-09-15].**

**Binds:** the Sonnet seat that executes C11 (`PREREG-002` §15 step 1b, §5.5(e)), and — on the four interpretive rulings at §4 — the seat that later executes §15 step 3.
**Does not bind:** any threshold in `PREREG-002`. Nothing in this document moves a threshold, edits the sealed text, or alters how F-002 is evaluated.

---

## 0. Provenance — what was opened, not what was reported about it

| Artifact | How read | Used for |
|---|---|---|
| `research/PREREG-002-crypto-funding-basis.md` | read in full at §5.1–§5.5, §6.1–§6.3, §7.1–§7.2, §10.5, §10.11.3, §15, §16, §20, §22 | the governing specification. **Not edited.** |
| `book/registry.db` | `sqlite3.connect("file:…?mode=ro", uri=True)` — read-only URI, no `PITStore`, no `TrialRegistry` construction, no write | family state, trial 1's config, the sealed binding fields, `prereg_sha256` |
| `harness/castellan/engine.py`, `registry.py`, `costs.py`, `stats.py`, `carry.py`, `data.py` | source read | the exact arithmetic the off-engine reconstruction must reproduce |
| `research/DATA-IMPL-013-f002-step2.md` | read in full | the executed shape of trial 1, and the two mechanical defects (I-374, I-375) it hit |
| `research/DIR-RESTATE-001-prereg002-mechanism.md` §14–§16 | read | the derivation of `k`, `d`, `band`, and the leg/side count |

**`book/pit.db` was NOT opened by this seat.** No panel was built, no `w(t)` was computed, no statistic was evaluated. Every figure below that describes the data is either read from the registry or cited from an artifact that measured it.

> **OPERATIONAL NOTE FOR THE EXECUTING SEAT — `book/pit.db` IS LIVE-MUTATING UNDER A SCHEDULED AGENT.** Observed from file metadata only, without opening the file: `book/pit.db` grew from **1,590,419,456 bytes at 12:50:03** to **1,590,775,808 bytes at 13:05:31** during this dispatch, with `book/polymarket_universe.json` rewritten at **13:05:22** [measured — `stat`]. Two launchd agents are installed: `capital.castellan.polymarket-book.plist` and `capital.castellan.pit-snapshot.plist` [measured — `~/Library/LaunchAgents`]. **The coincident Polymarket-universe rewrite identifies the growth as the Polymarket book capture, a dataset this family does not touch** — but the store is nevertheless mutating under the executing seat's feet, and a restatement of the `binanceusdm` funding series between trial 1 and C11 would silently put the calibration on different data than the falsifier. **Test B-7 — the `funding_panel_sha256` equality against trial 1's `971d037d…` — is the control for exactly this, and it is a STOP, not a warning.** `book/registry.db` is unchanged at 12:50:03, before this dispatch opened it.

---

## 1. THE RECOMMENDATION, STATED FIRST

**C11 should be required, and it is executable as the Principal ruled the sequence.** This seat does not refuse the dispatch, does not find the ordering unsatisfiable, and does not find that C11 should be dropped. It finds the opposite, and more strongly than the sponsor did: **C11 is the only instrument the firm has that can check leg (ii) in the direction nobody has looked.**

`PREREG-002` §5.3 states leg (ii)'s 25% margin is *"a declared materiality margin, so the leg neither fires nor spares on noise."* That sentence has two halves. Every treatment of C11 in the record — §5.5(e), §22 row 2b, R47's class-(b) re-imposition — checks only the **spares** half (`α`, the false-spare rate). **The fires half has never been checked by anything.** §4.6 and §7.3 below make it a required, deterministic, zero-cost output of this calibration.

**Cost: 0 of the ≤2 authorized trials.** §6 gives the arithmetic and the reason, and names the alternative this seat declined.

---

## 2. THE CONSTRUCTION — chosen, not offered

### 2.1 Choice: **block bootstrap. Specifically, circular block permutation of the conditioning schedule.** Sign-randomization is REJECTED.

The sealed text at §5.5(e) offers *"a block-bootstrap or sign-randomization of the conditioning schedule against the realized `R_bench` series, holding average exposure fixed."* It does not choose. This seat chooses, and gives the three reasons.

**Reason 1 — sign-randomization cannot satisfy the sealed cap.** `w(t) ∈ [0, 1]`, `w_max = 1.0`, and C-08 is binding: *"`w_max = 1.0`; never long perp; the strategy never exceeds delta-neutral"* [cited — `PREREG-002` §10.11.4 C-08]. Sign-randomizing a schedule means flipping its deviations about its mean: `w*(t) = w̄ ± (w(t) − w̄)`. Every bar with `w(t) < 2w̄ − 1` maps to `w*(t) > 1.0`. K2 selects *de-scaling only* — `w` never rises above the benchmark — so `w̄` sits near the top of `[0,1]` and the flip pushes de-scaled bars **above the cap**, i.e. into a long-perp position the family is forbidden to hold. Clipping at 1.0 restores the cap and **destroys the exact mean**, which is the one thing §5.5(e) requires be held fixed. There is no repair that keeps both.

**Reason 2 — sign-randomization presumes a symmetry that is false by construction.** It is the right surrogate for a zero-centred, roughly symmetric series. `w(t)` is one-sided (K2), clipped at both ends, and **atomic at 1.0** — `max(0, z − d) = 0` for all `z ≤ d`, so `w ≡ 1.0` on roughly a quarter of in-sample days on the state variable alone [cited — `PREREG-002` §6.2 R42, citing `REDTEAM-002` §2.1], before the `band = 0.54` hysteresis makes it stickier still. A surrogate built on a symmetry assumption is a null that does not describe the object.

**Reason 3 — block permutation enforces "average exposure held fixed" EXACTLY, by construction, rather than approximately.** A permutation of contiguous blocks re-orders the schedule and preserves its **exact multiset of values**. Therefore for every resample: `mean(w*) = mean(w)` to floating-point identity; `max(w*) = max(w) ≤ 1.0`; the marginal distribution is exact; and the within-block serial structure survives. The exposure-match scalar `c` is therefore **invariant across resamples and is asserted as such** (test C-2), not recomputed and hoped over. The ordinary with-replacement block bootstrap cannot do this — it perturbs the mean, and the two available repairs (rejection sampling, or rescaling by `c/mean(w*)`) respectively distort the null and breach the cap.

**Both constructions run. One is primary and it is named in advance.**

| | Primary | Secondary (disclosure only) |
|---|---|---|
| Construction | **Circular block permutation**, without replacement | Stationary block bootstrap, with replacement (Politis–Romano), the shape `castellan.carry.tail_bootstrap_carry` already uses in this harness [measured — `carry.py:126–171`] |
| Mean exposure | **Exact** | Perturbed; the realized deviation `mean(w*) − w̄` is reported as a distribution and is a **disclosure**, never a correction |
| Role | **The measured α.** | Sensitivity. **May not be substituted for the primary under any result.** |

### 2.2 The exact resampling procedure

```
T      = 2415 bars, the index of trial 1 [measured — registry trials.n_bars]
L      = 30 bars                                  (primary block length; §2.3)
n_blk  = ceil(T / L) = 81   -> 80 blocks of 30 and one of 15
B      = 10,000 resamples                          (§2.4)
```

**Per resample `b`:**
1. Draw a rotation offset `s_b ~ Uniform{0, …, T−1}`. Form the circularly rotated index `idx = (arange(T) + s_b) mod T`.
2. Cut `idx` into the 81 contiguous blocks above.
3. Draw a uniform random permutation `π_b` of the 81 blocks; concatenate.
4. The result is a length-`T` index `σ_b`, a bijection on `{0,…,T−1}`. The surrogate schedule is `w*(t) = w(σ_b(t))`, applied **identically to the BTC and ETH columns** (one common permutation, §2.5).
5. **Reject and redraw if `σ_b` is the identity** (test C-3). The identity is the realized alignment, and drawing it would put the realized leg-(ii) statistic inside the null sample — spending F-002's single leg-(ii) evaluation inside the calibration that exists to precede it.

The rotation is what makes the block *boundaries* random across resamples; without it, the 80 cut points are a fixed artifact of the sample and every surrogate inherits them.

### 2.3 Block length `L = 30`, and why it is not a free parameter

`L` must be at least the timescale over which `w(t)` is persistent, or the permutation destroys dependence the null is supposed to keep. `w(t)` is a function of `z(t)`, a **30-day rolling standardization** — the persistence is generated by that window. `L = 30` is therefore **the already-declared K1 lookback**, not a new number, and this seat is applying the sealed document's own discipline for exactly this situation: K7's window length was defended on the ground that *"the window length is the already-declared 30-day K1 lookback (§6.2), not a new number… derived from a field already in this document rather than chosen"* [cited — `PREREG-002` §7.1.1 property 1].

**Disclosure grid, reported and never substituted: `L ∈ {21, 30, 60, 90}`.** `21` is included specifically because it is the sealed text's *other* declared timescale (leg (i)'s Newey–West truncation) and the harness bootstrap's own default [measured — `carry.py:130`]; `60` and `90` bracket it upward. **The primary α is the `L = 30` figure and is pre-committed here, before any measurement. The maximum, minimum or any other selection over the grid is NOT the reported α** — selecting over a grid on a sample-computed quantity is the operation this family's own `success_criteria` forbids.

If the grid's α values straddle `0.10`, **that fact is itself a reported finding** and the primary still governs.

### 2.4 `B = 10,000`

α is a binomial proportion over `B`. At `α = 0.10`, `SE = √(0.1·0.9/10,000) = 0.0030` [measured — arithmetic]. That resolves the `0.10` boundary to better than ±0.006 at 95%. Each resample is one permutation, one element-wise product over 2,415 bars, one `np.partition` of size 20, and one HAC pass — the whole run is seconds. Report **Clopper–Pearson exact 95% intervals**, not normal-approximation intervals, because the interesting region includes small α where the normal approximation misbehaves.

### 2.5 RNG seeding, recorded for reproducibility

```
prereg_sha256 = e5ebd3a6db02b97955518bc70db3906918e702f9879d3ad9928223ad6d2a105f
                [measured — book/registry.db :: events, event_id 5, kind 'hypothesis_sealed']
master_seed   = int(prereg_sha256[:16], 16) = 16567568367804922233     [measured — arithmetic]

ss   = numpy.random.SeedSequence(master_seed)
kids = ss.spawn(8)        # index: 0..3 = permutation at L in (21,30,60,90)
                          #        4..7 = stationary bootstrap at the same L
rng  = numpy.random.default_rng(kids[i])
```

**The seed is derived from the sealed document's own identity hash.** It is pre-committed, it is reproducible by anyone who can read the registry, and it cannot be shopped — there is no second seed to try. `SeedSequence.spawn` is required rather than `seed + i` so that each `(construction, L)` cell draws from an independent stream and no cell's result is an artifact of another cell's draw order.

**Recorded on the face of the deliverable and in the registry event (§6.3):** `master_seed`, the numpy version, the spawn index of every cell, and the **sha256 of the raw improvement-statistic array** for the primary cell. Test C-4 requires the script be run twice and the two array hashes compared.

---

## 3. WHAT IS RANDOMIZED AND WHAT IS HELD

> **`R_bench` is realized, never resampled.** The sealed text is explicit — *"of the conditioning schedule against the **realized** `R_bench` series"* — and this specification obeys it literally. The price panel, the funding panel, and the return series are the realized ones on the realized index. **The only object that moves is the time ordering of `w(·)`.**

### 3.1 The position, as the sealed payload defines it — and it is NOT what §5.1's prose says

**This is the load-bearing correction in this document and everything downstream depends on it.**

The sealed `statement` field reads, verbatim: *"Position: long 1.0 unit spot notional, short w(t) units perp notional, w(t) = clip(1.0 − k·max(0, z(t) − d), 0, 1.0)"* [measured — `book/registry.db :: hypotheses.statement`, read directly, not narrated from the prose].

`PREREG-002` §5.1's prose says something different: *"Identical in every respect except that **per-asset notional is scaled by `w(t)`**."* Read naturally, that says both legs scale, which would make `R_strat` a scalar re-weighting of `R_bench`.

**The payload governs**, by the document's own rule: *"Anywhere this document's prose and that payload could diverge, the payload is what gets passed to `open_hypothesis`"* [cited — `PREREG-002` R-004]. The Director of Research read it the same way when re-deriving `band`: *"`w(t)` scales **perp** notional; spot is fixed at 1.0 unit [measured — the sealed `statement`]"* [cited — `DIR-RESTATE-001` §15.2], and `band = 0.54` is sealed **on that reading** of the side count.

**Three consequences, all of which change the calibration:**

1. **`R_strat` is not a re-weighting of `R_bench`.** `R_strat(t) ≠ w(t−1)·R_bench(t)` for any `w`. The obvious cheap surrogate — multiply trial 1's logged net series by a surrogate schedule — **is wrong and must not be used.** The surrogate has to be rebuilt from the component panels.
2. **Whenever `w < 1` the position is net long spot.** Gross notional falls; **directional delta rises from zero.** "De-scaling into rich funding" does not make the position smaller in risk — it *un-hedges* it. C-08's *"never exceeds delta-neutral"* is consistent with this: the position may be under-hedged, never over-hedged.
3. **Leg (ii)'s exposure match is on gross notional only and therefore does not match the dimension that drives the tail.** `R_bench_scaled` is delta-neutral at `c×` size. `R_strat` at the same *average gross* exposure carries residual long-spot delta. **Filed I-377, HIGH** — and §4.6's `I_0` is the instrument that measures how much of leg (ii) this accounts for.

**Filed I-376, HIGH:** §5.1's prose and the sealed `statement` field describe different position constructions; the payload governs and the prose is the one that is wrong. Not repairable — the document is P7-frozen. Recorded so that no later reader reconstructs `R_strat` from §5.1 and gets a different series than step 3 produced.

### 3.2 The surrogate, in full

Let the realized index be trial 1's 2,415 bars, `2020-01-01 → 2026-08-11`. Columns as trial 1 ran them: `BTC/USDT`, `ETH/USDT` (spot), `BTC/USDT:USDT`, `ETH/USDT:USDT` (perp).

```
target_weights*(t):   spot_BTC = +0.5                 spot_ETH = +0.5
                      perp_BTC = −0.5·w*_BTC(t)       perp_ETH = −0.5·w*_ETH(t)

positions*      = target_weights*.shift(1).fillna(0.0)          # engine.py:138
asset_rets      = prices.pct_change()                           # engine.py:137
gross*(t)       = (positions* · asset_rets).sum(axis=1)         # engine.py:139
trades*         = positions*.diff().abs().fillna(positions*.abs())   # engine.py:142
trade_cost*(t)  = Σ_col trades*[col](t) · per_side[col]         # engine.py:157–175, no-ADV branch
borrow*(t)      = 0                                             # both presets: borrow_bps_annual = 0.0
carry*(t)       = −(positions*[perp cols] · funding_panel).sum(axis=1)   # engine.py:219–228
net*(t)         = (gross* + carry* − trade_cost*).fillna(0.0)   # engine.py:231
```

`per_side` is read **at run time from the shared library**, never written as a literal:
`CRYPTO_SPOT_TAKER.per_side_cost(1.0) = 12.5 bp`, `CRYPTO_PERP_TAKER.per_side_cost(1.0) = 6.0 bp` [measured — `costs.py:39–46, 120–143`]. This is the sanctioned cost path, not a hand-roll; test A-4 enforces that the module attribute is what is read.

`sigma_daily` and `adv_notional` are **not** supplied, matching trial 1 exactly [cited — `DATA-IMPL-013` §3], which puts `run_backtest` on the constant-`per_side` branch and makes the cost term exactly linear in `|Δw|`. **This is the only reason a faithful off-engine reconstruction is possible at all**, and it is why test A-2 must anchor it against the engine on a *varying* schedule (§7.1).

### 3.3 The exposure-match scalar `c`

Per §5.1, `c` = (time-avg `R_strat` gross exposure) ÷ (time-avg `R_bench` gross exposure), on **held (lagged) positions**, as the engine computes them:

```
gross_exposure_strat(t) = 0.5 + 0.5 + 0.5·w_BTC(t−1) + 0.5·w_ETH(t−1)
gross_exposure_bench(t) = 2.0
c = mean_t[ gross_exposure_strat(t) ] / 2.0   ∈ [0.5, 1.0]
R_bench_scaled = c · R_bench          (trial 1's logged net series, scaled — as sealed)
```

`c` is computed **once**, from the **realized** schedule, and is **held constant across every resample** — that is the enforcement of "average exposure held fixed." Because block permutation preserves the multiset exactly, the surrogates' own average exposure equals `c` identically, and test C-2 asserts it rather than assuming it.

### 3.4 The schedule `w(t)` — the three under-specified details, ruled

`w(t)` is a deterministic function of `pit.db`. Building it requires three decisions the sealed document does not make. **This seat rules them here, before any leg-(i) or leg-(ii) statistic exists, and the rulings bind step 3 as well as C11** — the two must use the identical schedule or the calibration is of a different object than the test.

| # | Gap | Ruling | Basis |
|---|---|---|---|
| **R-1** | The first 30 bars have no 30-day trailing baseline, so `z(t)` is undefined. The sealed text is silent. | **`w = 1.0` (benchmark weight) for the first 30 bars.** | K7 option (1), already selected and sealed: when the trailing baseline is unavailable, `z(t)` is INSUFFICIENT-DATA *"during which the symbol is held at BENCHMARK WEIGHT `w = 1.0`"* [cited — §7.1 K7]. The rule already exists in the document; it is applied, not invented. It is also the conservative direction (§7.1.1 property 3 — the family forgoes benefit rather than claiming it). **Filed I-379, MEDIUM.** |
| **R-2** | K7's one named in-sample trigger. | **`w = 1.0` for the 30 bars from 2025-09-18 inclusive, on BOTH BTC and ETH.** | Sealed and dated in the frozen text, with its arithmetic effect conceded nil and the rule applied anyway [cited — §7.1.1]. Test B-5 asserts it by date. |
| **R-3** | The turnover band's state. | **`w_held` is a per-asset state variable initialised to 1.0; on each bar, if `\|w_target − w_held\| > 0.54` then `w_held ← w_target`, else unchanged.** Strict inequality, per the sealed text's *"no trade unless \|w_target − w_held\| > band."* | Sealed literal `band = 0.54` [measured — `hypotheses.statement`]. The strict inequality is the sealed text's own word. |

**`w(t)` for the calibration means `w_held(t)`, the decision series, permuted before the engine's `shift(1)` is applied.** Permuting the decision series and then lagging is what preserves the correspondence with how the engine will construct `R_strat` at step 3.

---

## 4. THE OUTPUT

### 4.1 Leg (ii)'s statistic, written once

`M(x)` = the arithmetic mean of the **20 smallest** elements of series `x`, selected from `x` itself.

```
M_b = M( R_bench_scaled ) = c · M( R_bench )          # c > 0 preserves order
M_s = M( R_strat )                                     # or M( R*_strat ) for a surrogate
improvement  I = ( M_s − M_b ) / |M_b|
leg (ii) FIRES  iff  I < 0.25
```

### 4.2 Interpretive ruling — the denominator (I-378, MEDIUM)

The sealed text says the strategy's tail mean must be *"better (less negative) than… by at least 25%"* and **does not name what the 25% is a percentage of.** Two readings exist and they are not equivalent. **Ruled: the denominator is `|M_bench_scaled|` — the baseline being improved upon.** That is the ordinary reading of "better than X by 25%," and it is the reading under which the leg spares iff `|M_s| ≤ 0.75·|M_b|`, a clean statement about the strategy's tail as a fraction of the benchmark's.

This ruling is made **before the measurement exists**, which is what makes it a pre-commitment rather than a threshold move. The executing seat reports α under the alternative denominator (`|M_s|`) as a **sensitivity** so the ruling's materiality is visible and the Principal can see what the choice bought.

### 4.3 Guard — the denominator's sign

**If `M_b ≥ 0`, the statistic is undefined and the verdict is INSUFFICIENT-DATA, not survival and not firing.** A percentage improvement on a non-negative baseline is F-001's minor defect — *"a percentage difference on a small integer index — undefined at zero"* [cited — §5.5] — transposed. Test D-2. On 2,415 bars of a levered crypto basis position `M_b < 0` is near-certain; the guard exists because a falsifier whose arithmetic silently degenerates is the class of defect this seat exists to catch.

### 4.4 The primary output: **the measured α that replaces the [assumed] `≤ 0.10`**

```
α̂₂ = (1/B) · #{ b : I*_b ≥ 0.25 }          with Clopper–Pearson 95% interval
```

reported as **[measured]**, at `L = 30`, primary construction, cost-inclusive, denominator `|M_b|`.

**Direction of the residual error, stated so the figure is not read as exact.** The surrogate reproduces the engine's arithmetic exactly on the anchored path (§7.1), so the residual is not numerical. It is that the null's turnover differs slightly from the realized schedule's at the ~80 block joins, changing the cost term by a few tenths of a basis point per year against a ~12.7%/yr net level [cited — `DATA-IMPL-013` §6]. **Immaterial, and its sign is not knowable in advance.** This is stated instead of the more comfortable claim that the figure is conservative.

### 4.5 The required second output: **the JOINT null, measured directly (I-382, HIGH)**

§5.3's headline is not α₂. It is:

> `P(F-002 survives | conditioning is pure noise) ≤ 0.0013 × 0.10 ≈ 1.3 × 10⁻⁴`

**That arithmetic multiplies leg (i)'s α by leg (ii)'s α as though the two were independent. They are not, and the document nowhere states the assumption.** Legs (i) and (ii) are computed on the *same two return series* under the *same* surrogate schedule. A schedule that happens to sit small on bad days both lifts the regression alpha and improves the tail — positive dependence. Under positive dependence `P(both fail to fire) > P(i fails)·P(ii fails)`, so **the sealed `1.3 × 10⁻⁴` understates the joint false-survival rate, and it does so independently of whatever C11 measures for α₂.** The "factor of roughly 2,400" against F-001's 31% rests on an unstated assumption.

**This is measurable directly, on the same surrogates, at zero extra cost.** For each surrogate, compute *both* leg statistics and record the joint event:

```
α̂_joint = (1/B) · #{ b : t_NW(α*_b) > 3.0  AND  I*_b ≥ 0.25 }
α̂₁      = (1/B) · #{ b : t_NW(α*_b) > 3.0 }
```

**Report `α̂_joint`, `α̂₁`, `α̂₂`, and the product `α̂₁·α̂₂` side by side.** The gap between `α̂_joint` and the product is the measured size of the independence error, and it is the number §5.3 should have carried. This extension is authorized by this ruling; it is squarely within C11's purpose because item 5 of the dispatch asks what the *joint* rate becomes, and the joint rate cannot be recomputed as a product once the product is known to be wrong.

**Scope guard:** the leg-(i) statistic is computed **only on surrogates, never on the realized alignment.** Test C-3 forbids the identity permutation and the script must not emit a realized leg-(i) or leg-(ii) figure. E2's single evaluation belongs to step 3 and this calibration must be structurally incapable of spending it.

### 4.6 The required third output: **the two-sided feasibility check — the half nobody was going to look at (I-384, HIGH)**

§5.3 declares the 25% margin is set *"so the leg neither fires nor spares on noise."* C11 as scoped checks only "spares." Three further quantities, all deterministic or near-deterministic, all free, check the other half:

| Quantity | Definition | What it detects |
|---|---|---|
| **`I_0` — the construction offset** | `I` evaluated at the constant schedule `w* ≡ w̄` (both assets, every bar). | **The part of leg (ii) that has no timing content at all.** Because the spot leg is fixed and only the perp leg scales (§3.1), a *constant* `w̄ < 1` position is **not** `R_bench_scaled` — it is net long spot at the same average gross exposure. `I_0 ≠ 0`. **`I_0` is the null's structural centre, and it is the §5.5(d) bias re-appearing on the delta axis after the `R_bench_scaled` repair closed it on the size axis.** |
| **`I_max` — the feasibility bound** | Assign the realized multiset of `w` values to bars greedily: smallest `w` on the most-negative bars, largest on the least. A deterministic upper bound on `I` over **every** schedule with this average exposure. | **Whether 25% is reachable at all.** If `I_max < 0.25`, **no schedule whatsoever — including a perfectly clairvoyant one — can spare leg (ii) at this exposure. The leg fires by construction.** |
| **`I_min`** | The same assignment reversed. | The null's lower support; a sanity bracket. |

**Pre-committed readings, before the measurement:**

- **`I_max < 0.25` ⇒ leg (ii) is not a test.** It fires on every possible world. Its firing carries no information about the mechanism. This is the **T-18 condition named in the dispatch — a test that passes (here: fires) by construction — and it is a defect finding, not a result.**
- **`I_0 ≥ 0.25` ⇒ leg (ii) is spared by construction**, by the un-hedging offset alone, with zero timing content. The mirror defect.
- **`I_0` materially above zero but below 0.25 ⇒ leg (ii) measures the un-hedging effect plus timing**, and the two are not separated by anything in the sealed text. Disclose the decomposition; the leg still runs as sealed.

`I_0` and `I_max` are functions of the realized `w` multiset and the realized `R_bench` — **they are alignment-free and therefore do not compute, or bound from below, the realized leg-(ii) statistic.** `I_max` bounds it from above. Learning before step 3 that leg (ii) cannot be spared is not a breach of E2; **it is precisely the value the Principal's ordering ruling was designed to buy**, and discovering it after the single evaluation would have been worthless.

### 4.7 Full required output set

| # | Figure | Mark |
|---|---|---|
| 1 | `α̂₂`, Clopper–Pearson 95% CI, at `L = 30`, primary construction | [measured] |
| 2 | `α̂₁`, `α̂_joint`, `α̂₁·α̂₂`, and the independence gap `α̂_joint − α̂₁·α̂₂` | [measured] |
| 3 | `I_0`, `I_max`, `I_min` | [measured] |
| 4 | Null percentiles of `I*`: 1 / 5 / 25 / 50 / 75 / 95 / 99, and the count of exact ties | [measured] |
| 5 | `c`, `w̄` per asset, count of bars at `w = 1.0`, count of band-triggered rebalances, count of distinct de-scaling episodes | [measured] |
| 6 | `α̂₂` across `L ∈ {21, 30, 60, 90}` × {permutation, stationary bootstrap} — 8 cells | [measured] — **disclosure only** |
| 7 | `α̂₂` under the alternative denominator `\|M_s\|` | [measured] — **disclosure only** |
| 8 | `α̂₂` cost-free (surrogate with `trade_cost* ≡ 0`) | [measured] — **disclosure only** |
| 9 | Recomputed joint false-survival rate, reported **alongside** the sealed `1.3 × 10⁻⁴`, never replacing it | [measured] |
| 10 | Engine-parity residuals: max abs difference, A-1 and A-2 | [measured] |
| 11 | `master_seed`, numpy version, spawn indices, sha256 of the primary `I*` array, sha256 of `book/registry.db` before and after | [measured] |

**I-044 is binding on all eleven.** The script computes figures and writes them to a JSON artifact. **No `print()` may assert a conclusion beside a computation.** Every reading — every use of the words "decisive," "weak," "defective," "fires," "spares" — is written in the deliverable's prose by the executing seat, attributed to that seat, sourced to a numbered figure above.

---

## 5. THE RULING THE FROZEN DOCUMENT CANNOT MAKE FOR ITSELF

> *Dispatch item 5: what happens if the measured α exceeds 0.10? Does the family's falsifier weaken? Is the correct disposition a disclosure, a recomputed joint rate reported alongside, or something that bears on Gate 1?*

### 5.1 First, what does NOT happen

**F-002 does not change. No leg changes. No threshold moves. The 25% margin, the `t > 3.0` hurdle, the 1,800-bar floor and the zero-drift test are frozen and are evaluated exactly as sealed, whatever C11 returns.** Validation's own standing rule: *"Thresholds do not move mid-evaluation. If a threshold should change, that is a Charter amendment, decided by the Principal, before the next evaluation — never during this one."* A measured α is not a reason to re-open a falsifier; it is a measurement of what that falsifier's survival is worth.

**The distinction that settles the question: `α` is not a threshold in F-002. It appears nowhere in §5.2. It is a *property* of §5.2, reported in §5.3.** A frozen document may not have its thresholds edited; a frozen document's *reported properties* may be measured and corrected, and must be, because the alternative is knowingly carrying a false number forward. The sealed `1.3 × 10⁻⁴` becomes a **known-superseded figure**: every artifact from Gate 1 onward carries **both**, the sealed one marked `[assumed — superseded by C11]` and the measured one marked `[measured]`. The sealed one is never deleted and never silently replaced.

### 5.2 The bands — pre-committed here, before the measurement

These are stated **now**, before `α̂₂` exists, which is what distinguishes a pre-commitment from a renegotiation. The device is the sponsor's own (§10.8 pre-committed the `ρ̂` verdict bands into the sponsor's document for exactly this reason: *"a band the sponsor pre-registered is one the sponsor cannot renegotiate"*). Band boundaries are taken from the sealed document's own arithmetic wherever one exists, rather than invented.

| Band | Measured `α̂₂` | Disposition |
|---|---|---|
| **A** | **≤ 0.10** | The assumption holds. Mark §5.3's term `[measured]`; report the recomputed joint rate (it will be at or below `1.3 × 10⁻⁴` on the product, and separately the *measured* `α̂_joint`, which may exceed it — see §5.3 below). No further consequence. |
| **B** | **0.10 < α̂₂ ≤ 0.40** | **DISCLOSURE + RECOMPUTED JOINT RATE.** F-002 proceeds unchanged and remains decisive. The upper bound is **the sponsor's own pre-committed number**, not this seat's: *"If C11 returns 0.4, F-002's joint rate is 5 × 10⁻⁴ — still decisive"* [cited — `PREREG-002` §22 row 2b]. The sponsor pre-registered that reading; Validation holds it to it, in the direction that costs the sponsor nothing and in the direction that costs it something alike. |
| **C** | **0.40 < α̂₂ < 0.90** | Disclosure + recomputed rate, **plus: leg (ii)'s non-firing carries no independent evidentiary weight.** F-002 survival, if it occurs, rests on leg (i) alone and every artifact says so in those words. **This is not a new device** — §5.3 R7 already applies exactly this treatment to leg (iii): *"it will almost certainly not fire, and this seat records now that its non-firing is worth nothing as evidence."* Validation is applying the document's own existing treatment of a weak leg to a second leg, not inventing a sanction. |
| **D** | **≥ 0.90** | Leg (ii) is **decorative** — the sealed document's own word. F-002 still runs as sealed (E2, the frozen text). But Validation records that **the family's falsifier is effectively single-legged**, and **no Gate 1 PROCEED may rest on F-002 survival**: a PROCEED requires a successor family with a repaired leg (ii), opened at the §7.2 escalated `n_inherited`. See §5.4 — the sealed remedy for this band is unreachable and this is its post-seal substitute. |
| **X** | **overrides A–D** | **`I_max < 0.25` or `I_0 ≥ 0.25` (§4.6).** Leg (ii) fires, or spares, **by construction**. This is a defect in the falsifier, not a value of α, and it outranks the α bands because α is a statement about a test that in this case is not one. Disposition: **a Validation finding to the Principal, unbatched**; step 3 still runs the sealed falsifier in full (Validation does not decline to evaluate a sealed falsifier); leg (ii)'s result is recorded as **non-informative in advance** on the face of the Gate 1 report; and if leg (ii) fires and the family is written up as a KILL, the KILL stands as sealed **and** the finding stands that the leg that killed it was not a test. A successor family may re-pre-register with a repaired leg (ii). |

**Bands B, C and D are disclosure dispositions, not gates.** Band D and band X bear on Gate 1 — and that is where C11 already lives: R47 re-imposed C11 as a **class-(b) Gate 1 condition**, *"executor: Validation; cadence: once, at the first `evaluate_gate1` on this family; artifact: the Validation Report states on its face whether §5.3's `≤ 0.10` is `[assumed]` or `[measured]`"* [cited — §20, R47]. The vehicle exists and this ruling fills it.

### 5.3 The honest complication in bands A and B

`α̂_joint` (§4.5) may exceed `α̂₁ · α̂₂` even when `α̂₂ ≤ 0.10`. In that case **the sealed `1.3 × 10⁻⁴` is wrong in the permissive direction for a reason that has nothing to do with C11's assigned term.** The bands above are keyed on `α̂₂` because that is what the dispatch asked and what §5.3 marked `[assumed]`. **The reported joint rate is `α̂_joint`, the measured one, in every band — not the product, in any band, ever again.** If `α̂_joint` exceeds `10⁻³` the family is in band C's evidentiary posture regardless of `α̂₂`'s value, and this seat states that now so it cannot be argued later.

### 5.4 The sealed remedy is unreachable, and that is a finding (I-383, MEDIUM)

§22 row 2b pre-registers the sponsor's own remedy for a large α: *"if it returns something near 1.0, leg (ii) is decorative and **must be replaced before sealing**."*

**The document is sealed.** `open_hypothesis` was called; `prereg_sha256` is computed; P3 refuses any amendment. **The branch the sponsor pre-committed to has no post-seal form.** This happened because C11 was removed from the seal-blocking set as circular (R47, I-202 — *"it requires ≤2 logged trials, `log_trial` refuses an unregistered family, and registration IS the seal"*) and re-imposed at Gate 1, but §22's remedy clause was written against the pre-seal placement and was never conformed. Band D above **is** the post-seal substitute: what cannot be replaced before sealing can be replaced by a successor family, and the sealed family cannot be reported PROCEED on a falsifier one of whose two live legs is decorative.

### 5.5 Summary answer to item 5

**Does the family's falsifier weaken?** Its *definition* does not weaken; it does not change at all. Its *evidentiary value* weakens, continuously, in the measured α — and the record must carry the measured value, not the assumed one.
**Is the correct disposition a disclosure, a recomputed joint rate, or something bearing on Gate 1?** **All three, banded.** Disclosure in every band; the recomputed joint rate (measured, not the product) in every band; and a Gate 1 consequence in bands D and X only, delivered through the class-(b) condition that already exists.

---

## 6. TRIAL ACCOUNTING

### 6.1 The arithmetic

```
trial_budget (Stage 1, sealed)          47      [measured — registry hypotheses.trial_budget]
n_inherited                              7      [measured — registry hypotheses.n_inherited]
denominator                             54      [inferred — 47 + 7]
own logged trials to date                1      [measured — registry trials, trial_id 1, grant_id 11]
C11 authorization (§15 step 1b)         ≤ 2
C11 COST UNDER THIS SPECIFICATION        0      of the ≤2
own logged trials after C11              1
```

### 6.2 Why zero, and what each step logs

C11 needs four objects. **None of them requires a `run_backtest` call against `book/registry.db`.**

| Object | Source | Live trial? |
|---|---|---|
| `R_bench`, realized net daily series | **Already logged — trial 1**, 2,415 bars, `periods_per_year = 365`, `config_hash 44532cc88ed7b1a9` [measured] | **No.** Reading a logged trial is a read. |
| `w(t)`, the realized schedule | Deterministic transform of `pit_funding_panel` under the §3.4 rulings | **No.** Not a backtest; produces no performance number. |
| `c`, `w̄` | Arithmetic on `w(t)` | **No.** |
| Surrogate net series, ×B | Off-engine reconstruction of `engine.py`'s arithmetic (§3.2), anchored to the engine by tests A-1 and A-2 | **No** — the A-2 anchor runs on a **scratch registry** (§6.4). |

**§5.5(e)'s `≤ 2` is an authorization ceiling, not a mandate; 0 is inside it.** The sealed clause says the calibration *"is a computation on `pit.db` and is therefore a trial… at a cost of 1–2 trials."* That was written pre-seal, when the registry held **zero** trials and C11 would have had to produce `R_bench` itself. **S4-D-028 has since produced it.** The sealed budget line survives untouched; its occasion has gone.

### 6.3 What C11 DOES write to the live registry: one event, not a trial

**A look at the family's data should be on the record.** The right instrument is the append-only event log, not the trial ledger:

```
registry.log_event(
    kind   = "null_calibration",
    family = "funding-carry-conditioning-002",
    detail = { spec: "VALIDATION-SPEC-005", dispatch: <executing dispatch id>,
               construction: "circular_block_permutation", L: 30, B: 10000,
               master_seed: 16567568367804922233, numpy_version: ...,
               inputs: { trial_id: 1, config_hash: "44532cc88ed7b1a9",
                         funding_panel_sha256: "971d037d442cf1a5fb93ad2c797f54938fd6250cccd2079b903d8c853a58c791" },
               alpha_2: ..., alpha_2_ci95: [...], alpha_1: ..., alpha_joint: ...,
               I_0: ..., I_max: ..., I_min: ..., c: ...,
               improvement_array_sha256: ..., trials_consumed: 0 }
)
```

**Why an event and not a trial.** A logged trial enters `family_stats` and `returns_matrix`, and therefore enters `sr_period_std` — the `σ_SR` that `deflated_sharpe_ratio` is linear in. §16 records that this family's `σ_SR` being *"estimated on the space searched"* is its defence against *"the largest hole in the firm's apparatus"* [cited — `VALIDATION-RULING-004` §2.3]. **Injecting a deliberately-null surrogate Sharpe into that estimate corrupts a defence the family legitimately has.** An event records the look with full provenance and corrupts nothing. The trial ledger prices a *search over candidate strategies*; C11 selects nothing and proposes nothing.

**The grant, named and not scripted (I-374).** `log_event` does **not** self-grant. The executing seat opens exactly one grant of its own:
**reason `LOG_EVENT` · dispatch = the executing dispatch id · attribution: Head of Data & Infrastructure, executing `VALIDATION-SPEC-005` on Validation's requirement · token from `CASTELLAN_REGISTRY_WRITE`.**
`LOG_EVENT` admits `log_event` [measured — `registry.py:152`]. **This brief names that grant's reason and attribution and deliberately does not script a `write_grant` call for any self-granting path** — `run_backtest` self-grants `LOG_TRIAL` internally under SPEC-004 [measured — `engine.py:243–252`], and an outer grant around it raises `RegistryWriteGrantNestedError` [measured — `registry.py:440`]. **Do not wrap `run_backtest`. Anywhere. Including in the scratch rehearsal.**

### 6.4 The mandatory scratch-registry rehearsal — and why it is load-bearing here, not ceremonial

The Principal has ruled the scratch rehearsal standing for every first-of-kind operation. C11 is first-of-kind twice over (first null calibration; first off-engine reconstruction of the engine). **Here the rehearsal is not only a safety step — it is the mechanism that makes C11 cost zero live trials.**

```
scratch = <tempdir>/scratch-registry.db
reg_s   = TrialRegistry(scratch, allow_create=True)          # bootstraps, ungoverned, disclosed
with reg_s.write_grant(reason="REGISTER_HYPOTHESIS", dispatch=<id>, token=<tok>):
    reg_s.open_hypothesis(family="c11-rehearsal", statement=..., mechanism=...,
                          falsifier=..., universe=..., horizon=...,
                          success_criteria=..., trial_budget=8)   # NOT the sealed fields
run_backtest(..., registry=reg_s, family="c11-rehearsal", periods_per_year=365, ...)
#   ^ no outer grant; it self-grants (I-374)
with reg_s.write_grant(reason="LOG_EVENT", dispatch=<id>, token=<tok>):
    reg_s.log_event(kind="null_calibration", family="c11-rehearsal", detail={...})
```

The rehearsal must exercise **the entire live sequence**, including the `log_event` write, before anything touches `book/registry.db`. It is what caught I-374 before the live registry saw it.

**Two live-path mechanics the executing seat will hit, specified around:**
- **`PITStore` has no read-only open path** (I-375): `PITStore("file:book/pit.db?mode=ro")` raises `OperationalError`; the constructor runs `executescript(SCHEMA)` and `commit()` on every open [cited — `DATA-IMPL-013` §7]. **Open it the ordinary way, as S4-D-028 did.** Do not attempt a read-only URI; do not repair I-375 in this dispatch — it is queued behind trials and is not C11's to fix.
- **`run_backtest` defaults `periods_per_year = 252`.** This is a 365-bar crypto series. **Pass `365` explicitly on every call, scratch included** (test A-5).

### 6.5 The alternative this seat declined, stated so it can be overruled

C11 could instead spend **1 live trial** on the A-2 anchor — one surrogate schedule run through `run_backtest` against `book/registry.db` — putting an in-ledger trial id on the calibration. **Declined**, because the anchor's Sharpe is a deliberately-null number and would enter `σ_SR` (§6.3), and because provenance by `config_hash` + `funding_panel_sha256` + the event row is stronger than a trial id, not weaker. **If the CIO or the Principal prefers the in-ledger anchor, it costs 1 of the ≤2 and the `σ_SR` contamination must be disclosed on the Gate 1 report.** This seat's recommendation is 0.

### 6.6 A sealed clause that cannot be satisfied (I-381, MEDIUM)

R47's class-(b) re-imposition names the artifact as: *"the Validation Report states on its face whether §5.3's `≤ 0.10` is `[assumed]` or `[measured]`, and **if measured, the trial ids and that they are trials 1 and 2 of the ledger**."*

**Trial 1 of the ledger is S4-D-028's leg-(0)/leg-(iii) benchmark run.** The Principal's ordering — step 2 before step 1b — is correct and this seat does not contest it, but it means C11's trials cannot be trials 1 and 2 and **the clause is unsatisfiable as written.** The substance is satisfiable and is what the Validation Report will carry: the `[measured]` mark, and the calibration's provenance as **trial 1's `config_hash 44532cc88ed7b1a9`, `funding_panel_sha256 971d037d…`, the `null_calibration` event id, and the statement that C11 consumed 0 of its ≤2 authorized trials.** **This seat will not log a trial in order to produce a trial id that a clerical clause expects.**

---

## 7. ACCEPTANCE TESTS — RED FIRST

**Binding on the executing seat, in the shape `VALIDATION-RULING-003` set and `DATA-IMPL-004` honoured (*"All nineteen T-cases are implemented and pass"*): these are authored before the implementation is written, and the implementation is written to them.**

**THE DEFECT-IN-THE-TEST CONDITION, stated globally and binding on every row.**
*A test that cannot fail on any input is not a test; it is a sentence in a report.* The harness states this against itself, in this repository, about a bootstrap: the T-17 check is *"a meaningful check rather than a tautology"* only because *"it is only true if the block/path combination actually re-draws the extreme bar often enough"* [measured — `carry.py:133–144`]. **The executing seat must, for every test below, first construct a mutation of the implementation that makes that test FAIL, record the mutation and the observed failure in a red-first log, and only then write the passing implementation.** A test for which no failing mutation can be constructed is **reported as a finding, by number, and the deliverable says so** — it is not quietly counted among the passes. **A test that passes on the first run without a recorded red is not a pass.**

### 7.1 Group A — engine parity (6)

| # | Test | Passes by construction if… |
|---|---|---|
| **A-1** | The off-engine reconstruction, run at `w ≡ 1.0`, reproduces trial 1's stored net series. **`max abs diff ≤ 1e-9`**; the observed max is reported. | …the reconstruction reads trial 1's blob as an input. **Guard:** the reconstruction function's signature takes only `(prices, funding_panel, w)`; trial 1's blob is loaded *after* it returns, in the comparison scope only. |
| **A-2** | **The anchor.** On the **scratch registry**, `run_backtest` is called with surrogate schedule `b = 0` and `periods_per_year=365`; the off-engine reconstruction of the **same** schedule matches `BacktestResult.net_returns` to `≤ 1e-9`. | …the schedule is constant. A-1 does not exercise the cost path at all — `R_bench` has ~zero turnover after entry (2.8 bp/yr total [cited — `DATA-IMPL-013` §6]) — so **without a varying schedule the whole `trade_cost` branch is unvalidated.** **Guard:** assert the anchor schedule has ≥ 20 bars with `\|Δw\| > 0`. |
| **A-3** | `sha256(book/registry.db)` is recorded before and after the entire C11 run; the only difference is the one `null_calibration` event row. Both hashes reported. | …the hash is computed twice from the same in-memory value. **Guard:** hash the file on disk, in separate subprocess invocations. |
| **A-4** | Per-side costs are read at run time from `castellan.costs.CRYPTO_SPOT_TAKER` / `CRYPTO_PERP_TAKER`, never as literals. | …the test compares a literal to the same literal. **Guard:** monkeypatch `CRYPTO_PERP_TAKER.half_spread_bps` and assert the reconstruction's cost series changes. |
| **A-5** | Every `run_backtest` call in this dispatch logs `periods_per_year = 365` in its config; assert on the scratch trial's persisted `config_json`. | …asserted on the argument passed rather than on what was persisted. **Guard:** read it back out of the scratch DB. |
| **A-6** | No `TrialRegistry.write_grant` is opened around any `run_backtest` call, scratch or live (I-374). | …never exercised. **Guard:** a rehearsal case that *does* wrap it and asserts `RegistryWriteGrantNestedError`. |

### 7.2 Group B — the schedule (8)

| # | Test | Passes by construction if… |
|---|---|---|
| **B-1** | `w(t) ∈ [0, 1]` for every bar, both assets (C-08; never long perp). | …`w` is produced by a `clip(·,0,1)` that is also the test's own expression. **Guard:** assert on the series returned by the schedule builder, not on a re-clip. |
| **B-2** | `w(t) = 1.0` **exactly** wherever `z(t) ≤ d = 1.0` (R42 inertness). | …no bar has `z ≤ 1.0`. **Guard:** assert the count of such bars is > 0 and report it. |
| **B-3** | `w_target = 0.0` exactly at `z = d + 1/k = 3.0`, and `w_target = 0.5` at `z = 2.0`. Unit test on the sizing function, not on the sample. | — |
| **B-4** | **R-1 (§3.4):** the first 30 bars carry `w = 1.0`, both assets. | — |
| **B-5** | **R-2 (§3.4):** `w = 1.0` for the 30 bars from **2025-09-18** inclusive, both assets, asserted **by date**. | …the surrounding bars are also 1.0 for other reasons. **Guard:** report the count of forced bars and confirm it is exactly 30 per asset. |
| **B-6** | **R-3 (§3.4):** a target deviation `≤ 0.54` produces no trade; `> 0.54` snaps `w_held` to target. **Both branches must occur in-sample**, counts reported. | …no bar exceeds the band. **If that is the case the schedule is constant at 1.0, `R_strat ≡ R_bench`, leg (ii) is degenerate, and THAT IS THE FINDING — stop and report it.** |
| **B-7** | The funding panel's `attrs["sha256"]` equals trial 1's logged `funding_panel_sha256 = 971d037d442cf1a5fb93ad2c797f54938fd6250cccd2079b903d8c853a58c791`. **Mismatch ⇒ STOP.** | …the value is read from trial 1's config on both sides. **Guard:** one side is the freshly built panel's own attr. |
| **B-8** | The index is trial 1's: **2,415 bars, terminal `2026-08-11`**, settled-only construction [cited — `DATA-IMPL-013` §5]. | — |

### 7.3 Group C — the surrogate generator (6)

| # | Test | Passes by construction if… |
|---|---|---|
| **C-1** | Every surrogate preserves the exact multiset per column, and preserves `(w_BTC, w_ETH)` as **joint rows** (one common permutation). | …the comparison sorts both sides independently and loses the pairing. **Guard:** compare sorted arrays of the packed pair, not two sorted columns. |
| **C-2** | `mean(w*) == mean(w)` to floating-point identity for every `b`, both columns — therefore `c` is **invariant** and is computed **once**. | …`c` is recomputed per surrogate. **Guard:** `c` is a module-level constant computed before the loop; assert `id`-stability and assert the equality independently. |
| **C-3** | **No surrogate is the identity permutation.** Asserted over all `B`. | …`B` is small enough that identity is improbable. **Guard:** assert explicitly, and separately unit-test the rejection branch by forcing `s_b = 0, π_b = identity`. |
| **C-4** | **Reproducibility.** The script is run twice from the pre-committed seed; `sha256` of the primary `I*` array is identical. Both hashes reported. | …the second run reuses the first run's cached array. **Guard:** separate process, fresh temp dir. |
| **C-5** | At `L = 30`: exactly 81 blocks (80×30 + 1×15); every bar index appears exactly once in `σ_b`. | — |
| **C-6** | The 8 `(construction, L)` cells draw from `SeedSequence.spawn` children, not from a shared or arithmetically-offset stream. | …all cells happen to agree. **Guard:** assert the 8 `I*` arrays are pairwise distinct. |

### 7.4 Group D — the statistic (5)

| # | Test | Passes by construction if… |
|---|---|---|
| **D-1** | `M(x)` selects the 20 smallest **of the series it is given**, by `np.partition` on that series. Unit test: `M` on a series whose worst-20 set differs from `R_bench`'s returns the right 20. | **…the worst-20 index set is computed once from `R_bench` and reused for every surrogate.** This is the single most likely implementation error and it silently destroys the null: the re-weighting *reorders* which days are worst, and that reordering is the statistic's entire content. |
| **D-2** | `M_b < 0` asserted; otherwise **INSUFFICIENT-DATA**, not survival and not firing (§4.3). | …never exercised. **Guard:** unit-test the branch on a synthetic all-positive series. |
| **D-3** | **`I_0` is computed and reported** (§4.6) and the deliverable states it. | …`I_0` is asserted `≈ 0`. **It is not 0** — the constant-`w̄` position is net long spot and `R_bench_scaled` is not (§3.1). **A test asserting `I_0 ≈ 0` is itself the defect, and finding that assertion is the finding.** |
| **D-4** | **`I_max` and `I_min` are computed** by the greedy assignment (§4.6) and reported. Unit test: on a synthetic series the greedy bound is verified against brute force at `T = 10`. | …the greedy is verified only against itself. **Guard:** brute-force comparison at small `T`. |
| **D-5** | Null percentiles and the exact-tie count are reported. If the tie fraction exceeds 0.5 the null is degenerate and **that is reported as a finding**, not smoothed. | — |

### 7.5 Group E — the leg-(i) estimator and the output (5)

| # | Test | Passes by construction if… |
|---|---|---|
| **E-1** | **Reduction test.** The regression HAC estimator `nw_alpha_t(y, X, L)` with `X = [1]` (intercept only) equals `castellan.stats.sr_tstat_nw(y, L)` **to 1e-10**. | …the estimator calls `sr_tstat_nw` internally in that case. **Guard:** the sandwich must be computed generically; assert it also matches on a random 2-column `X` against an independent reference implementation. |
| **E-2** | The estimator uses the Bartlett kernel at `L = 21` with the **same `(T−1)` autocovariance divisor** `sr_tstat_nw` uses [measured — `stats.py:105–110`], so C11's null and step 3's realized statistic are the same estimator. | — |
| **E-3** | `α̂_joint`, `α̂₁`, `α̂₂` and the product `α̂₁·α̂₂` are all four reported; the independence gap is reported (§4.5). | …the joint is computed as the product. **Guard:** assert the two are computed by different code paths and report both. |
| **E-4** | **I-044.** No `print()` or log line in the script asserts a conclusion. The script emits a JSON artifact of figures only; every reading is prose in the deliverable, attributed, sourced to a numbered figure. | …enforced by eye. **Guard:** grep the script for the conclusion vocabulary (`decisive`, `weak`, `defective`, `survives`, `fires`, `spares`, `confirms`) and assert zero hits outside comments. |
| **E-5** | The disclosure grid (8 cells), the alternative denominator, and the cost-free variant are reported and **the primary is stated as pre-committed**; no selection over cells is reported as *the* α. | …only one cell is run. **Guard:** assert all 8 cells are present in the JSON. |

**Total: 30 acceptance tests, authored before implementation, each with its named failing mutation.**

---

## 8. ISSUES ALLOCATED

Allocated from **I-376** upward. The true maximum claimed **anywhere in the repository** is **I-375** [measured — `grep -rhoE "\bI-[0-9]{1,4}\b"` over the whole tree, all file types, not the log's highest heading; the single higher hit, `I-999`, is a test-fixture literal in `harness/tests/test_holdout_p1.py:346, 501, 508, 610` and is not a claimed number — §7.14(a), enumeration over the whole namespace rather than the prefixes under suspicion]. **This seat did not edit `logs/ISSUE_LOG.md`.**

| # | Sev | Finding | Owner |
|---|---|---|---|
| **I-376** | HIGH | §5.1's prose (*"per-asset notional is scaled by `w(t)`"*) and the sealed `statement` field (*"long 1.0 unit spot notional, short `w(t)` units perp notional"*) describe **different position constructions**. The payload governs (R-004). `R_strat` is therefore **not** a scalar re-weighting of `R_bench`. Frozen; not repairable. | Validation / Director of Research |
| **I-377** | HIGH | Leg (ii)'s exposure match is on **gross** notional. At equal average gross exposure `R_strat` carries **residual long-spot delta** that `R_bench_scaled` does not. The §5.5(d) repair closed the bias on the size axis and left it open on the delta axis. `I_0` measures it. | Validation |
| **I-378** | MEDIUM | Leg (ii)'s *"better… by at least 25%"* has **no stated denominator** in the sealed text. Ruled here: `\|M_bench_scaled\|`, pre-committed, with the alternative reported as a sensitivity. | Validation (ruled, §4.2) |
| **I-379** | MEDIUM | The sealed document specifies **no burn-in treatment** for the first 30 bars, where `z(t)` is undefined. Ruled here: `w = 1.0`, derived from K7 option (1). Binds C11 and step 3. | Validation (ruled, §3.4 R-1) |
| **I-380** | HIGH | F-002 leg (i) specifies a **Newey–West `t` on a regression intercept**. The `castellan` namespace contains **no OLS or regression-HAC estimator** — enumerated, all 50 public functions across all 17 modules; `sr_tstat_nw` is the NW `t` of a **mean**, not of a regression coefficient. **The estimator step 3 will use is unspecified and unimplemented.** §7.5 E-1/E-2 specify it here so C11 and step 3 share it. | Validation → head-of-data-infra |
| **I-381** | MEDIUM | R47's class-(b) artifact clause requires *"the trial ids and that they are **trials 1 and 2** of the ledger."* Trial 1 is S4-D-028's leg-(0)/leg-(iii) run; the clause is **unsatisfiable as written**. Substitute provenance specified at §6.6. | Validation |
| **I-382** | **HIGH — to the Principal** | §5.3's joint false-survival rate **multiplies leg (i)'s and leg (ii)'s α as though independent**, with the assumption nowhere stated. The two legs are computed on the same pair of series under the same schedule and are **positively dependent** by construction, so the sealed **`1.3 × 10⁻⁴` understates** the joint rate — **independently of anything C11 measures**. The *"factor of roughly 2,400"* against F-001's 31% rests on the unstated assumption. Directly measurable at zero cost (§4.5) and **required** by this specification. | Validation → Principal |
| **I-383** | MEDIUM | §22 row 2b's pre-committed remedy for a large α — *"must be replaced before sealing"* — is **unreachable**: the document is sealed. The remedy branch the sponsor pre-registered has no post-seal form. §5.2 band D supplies one. | Validation |
| **I-384** | **HIGH — to the Principal** | §5.3 claims leg (ii)'s margin is set *"so the leg **neither fires nor spares** on noise."* Every treatment of C11 on the record checks only the **spares** half. **Whether 25% is reachable at all — whether leg (ii) fires on every possible world and is therefore not a test — has never been checked by anything, and the sealed document contains no instrument that would.** §4.6's `I_max` and `I_0` are that instrument, and they are deterministic, free, and must run **before** step 3 spends E2. | Validation → Principal |

---

## 9. WHAT THIS SEAT DID NOT DO

- **Ran no trial. Made no registry write. Executed no backtest.** `book/registry.db` was opened only through a read-only URI; `book/pit.db` was not opened at all.
- **Did not run step 3, step 3b, or any leg of F-002.**
- **Did not edit** `PREREG-002`, `REGISTRATION-PAYLOAD-*`, `logs/ISSUE_LOG.md`, `logs/DECISION_RECORD.md`, `CLAUDE.md`, or anything under `book/`. No seal, no passphrase, no `git add`, no `git commit`.
- **Did not compute `w(t)`, `c`, `w̄`, `I_0`, `I_max`, or any leg statistic.** Every such quantity in this document is a specification of what the executing seat must compute, never a value.
- **Did not spawn a subagent.** Tools used: `Read`, `Write`, `Bash`, `Grep`. Within the declared set.
- **Refused nothing in the dispatch.** C11 is required, the Principal's ordering is satisfiable as ruled, and this seat recommends the sequence proceed.

---

## 10. WHAT WOULD CHANGE THIS SEAT'S MIND

| # | Claim | What would overturn it |
|---|---|---|
| 1 | Block permutation over sign-randomization | A construction of sign-randomization that holds `mean(w*)` exactly fixed **and** respects `w ≤ 1.0` without clipping. This seat found none and states the obstruction (§2.1) rather than asserting the conclusion. |
| 2 | `L = 30` | Evidence that `w(t)`'s persistence runs materially longer than its 30-day generating window — which the `L ∈ {21,30,60,90}` disclosure grid will show, and which would be reported as a finding rather than used to reselect `L`. |
| 3 | Zero trials | A ruling that reading a logged trial's return series, or computing the schedule from `pit.db`, is itself a trial under A2. This seat reads A2 as pricing a **search**, and C11 selects nothing. §6.5 names the 1-trial alternative and its cost so the call can be overruled without re-litigating the design. |
| 4 | The bands at §5.2 | The Principal setting different ones — which is his to do, and which is why they are stated **before** the measurement rather than after. |
| 5 | I-382 (the independence gap) | `α̂_joint ≈ α̂₁·α̂₂` on the measured surrogates. **The specification requires the measurement that could falsify this seat's claim, and reports it either way.** |
EOF
