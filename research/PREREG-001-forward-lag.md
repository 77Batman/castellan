# PRE-REGISTRATION 001 — the forward-lag family

**Seat:** Director of Research (Seat 2) · **Date:** 2026-07-28
**To:** the Principal · cc CIO, Quant Validation, Devil's Advocate, PM Pod B, Head of Data & Infrastructure
**Family identifier:** `forward-lag-001`
**Status:** **DRAFT, COMPLETE, SEALABLE.** Not sealed. Not registered. `book/registry.db` is untouched by this seat.

**What this document is.** The Charter §4.3 Gate 0 pre-registration record for the forward-lag family, in §7.2 Research Memo structure adapted for a pre-registration. All seven Gate 0 items are labelled `GATE 0 (n)`. §19 is the seal block: the exact binding field set for `TrialRegistry.open_hypothesis`, ready to execute.

**What this document is not.** It is not an intake verdict — that is Validation's, at Gate 0, and it is final short of the Principal. It is not a seal. **Sealing is what fixes `C` (D-007), and sealing is Pod B's act after Validation's intake.** Nothing in this document may be added to after sealing: under D-007 `C` *is* the seal date, and acceptance item **P7** fails Gate 1 if the `hypothesis_sealed` event postdates `C` at UTC day granularity. Every field left blank at sealing is a field a later retrieval can still move (Ruling 002 §3.5). This document is therefore written to be complete rather than skeletal.

House rule 6 applies throughout: **[measured]** = read or executed in this repository this session · **[cited]** = external or internal named source · **[inferred]** = reasoned from measured/cited facts · **[assumed]** = unverified premise, flagged.

---

## 0. Provenance — what was read, and what this seat did not do

**Read this session** [measured]: `FUND_CHARTER.md` Parts II (Seats 2, 7), III, IV (§4.1–4.6), V (§5.3–5.4), VII (§7.2), Appendix B · `CLAUDE.md` · `.claude/agents/director-of-research.md` · `agents/pm-digital-markets.md` · `reference/TEMPLATES.md` · `research/REDTEAM-001-agenda-and-forward-lag.md` **in full** · `VALIDATION-RULING-001` §4 in full · `VALIDATION-RULING-002` §3 in full · `VALIDATION-ACCEPTANCE-001` §5–6 (P1–P8, G1–G5) · `DATA-SPEC-polymarket-usable-history.md` in full · `DATA-INGEST-001-crypto-etf.md` · `logs/DECISION_RECORD.md` D-005…D-008 · `logs/ISSUE_LOG.md` I-002, I-004, I-011, I-021…I-025 · `harness/castellan/{registry,gates,costs,stats,holdout,loaders}.py`.

**Ran** [measured]: `castellan.stats.expected_max_sharpe` and `min_backtest_length_years` at the declared `N` (§9); SQLite reads of `book/registry.db` schema and contents.

**Did not do:** no data fetched, no backtest run, no registry write, no vault seal, no git commit. Per instruction and per seat boundary.

**State of the world at the time of writing** [measured]:

| Fact | Value |
|---|---|
| Families in `book/registry.db` | **0** — `hypotheses` table empty |
| Trials logged | **0** |
| Sealed holdout vaults | **0** — `book/vaults/` contains only `.gitkeep` |
| Polymarket rows in `book/pit.db` | **0** — `DATA-INGEST-001` §5: "Not touched, not fetched, not probed" |
| Polymarket loader in `castellan.loaders` | **does not exist** — the module exposes yfinance, ccxt OHLCV, ccxt funding, EDGAR, and nothing else |
| `DATA-SPEC-polymarket-usable-history.md` | drafted, **not accepted by Validation** |

This family currently has no data, no loader, and no accepted measurement spec. That is the honest starting position and every schedule claim below is conditioned on it.

---

## 1. Recommendation box

| Field | Value |
|---|---|
| **Hypothesis** | When a high-volume Polymarket contract reprices sharply, economically-paired later-resolving contracts on the same underlying event reprice with a delay that is directionally consistent, bounded, and large enough to clear the round-trip cost of trading the lagging leg. |
| **Verdict sought** | **Gate 0 intake.** Director of Research recommends **ADMITTED-AS-EXPLORATORY**, not ADMITTED — see §17. |
| **Expected Sharpe net** | **Unknown, and the firm does not know the sign of this strategy's expectancy** [measured — no admissible number exists; I-002 gives the prior work zero evidentiary weight]. No forecast is offered. Offering one here would be the defect this document exists to prevent. |
| **Proposed sizing** | **USD 50,000** intended initial allocation (§11). 2.5% of Pod B's $2M; 0.5% of the firm's $10M paper book. |
| **Horizon** | Event-driven. Single round trip, maximum holding period **36 hours**. No periodic rebalance. |
| **Conviction** | **Low on the investment case; moderate on the mechanism.** The mechanism survives adversarial attack (Red-Team §B.6.6). The investment case does not survive the firm's own arithmetic (§9, §11, §17). |
| **Trial count N at seal** | **`N_inherited` = 31,250**, declared and defended at §9. **Not zero.** |
| **Trial budget** | **40** post-seal trials. No ±50% parameter grid authorized under this pre-registration (§13). |
| **Breakeven cost** (house rule 5) | **1.0¢ round-trip spread on a 50¢-equivalent contract** under the `POLYMARKET` preset as shipped [measured — `half_spread_bps=100.0`, i.e. 1% of notional per side, 0.5¢ per side at 50¢]. The falsifier fires below **2.0¢** of captured move, which is that cost plus impact, delay, and a 2× margin (§5). |

---

## 2. Thesis in three bullets

- **The claim.** Two Polymarket contracts on the same underlying event with different resolution dates are exposed to the same news. The nearer, higher-volume contract absorbs it first; the later-resolving contract follows. The follow is slow enough to enter after the first has moved and exit before the second has finished.
- **Why it might persist.** The venue's marginal participant buys a clean binary expression of an opinion about *one* contract. Cross-contract relative value on a thin, retail-facing, crypto-settled venue is not the game they are playing, and the size available does not pay for a professional desk to make it their game.
- **Why the firm's own rules probably kill it anyway.** The prior search that produced this hypothesis was large and is unreconstructable (I-002). Seeded honestly at `N_inherited = 31,250`, Charter §4.4's minimum-backtest-length clause requires **17.1 years of history at the Gate 1 minimum net Sharpe of 1.0** [measured, §9]. Polymarket does not have 17 years. It may not have four. **The family's binding risk is arithmetic, not absence of edge.**

---

## 3. GATE 0 (1) — MECHANISM

*Charter §4.3(1): a written hypothesis stating the economic or structural mechanism — why this effect should exist, in terms of who is on the other side and why they accept the loss. "The data says so" is not a mechanism.*

**Who is on the other side.** The counterparty to the lagging-leg entry is a Polymarket participant holding or quoting the later-resolving contract who has not yet updated for news already impounded in the nearer contract. Three populations, and they accept the loss for different reasons:

1. **Directional retail expressing a view on the outcome.** They are long or short a *belief*, at a horizon measured in weeks, on a venue chosen for its clean binary payoff and absence of basis risk. Their reservation price is a subjective probability, not a relative-value spread. They accept an adverse fill against a faster relative-value counterparty as the price of a clean expression — structurally the same trade as an index-option hedger accepting persistent skew.
2. **Passive resting liquidity that is not being managed continuously.** A limit order left on a later-dated contract is stale between quote refreshes. On a thin venue the refresh interval is long. The loss is the ordinary adverse-selection cost of resting size, accepted because the alternative — continuous management of a low-notional contract — costs more than the loss.
3. **Participants whose attention is allocated by contract, not by event.** A holder of the September contract is not necessarily watching the July contract. The economic linkage is obvious to anyone who looks and invisible to anyone who is not looking at both at once.

**Why the mechanism is structurally supported, independent of any measurement.** The venue trades continuously with no market-hours constraint, positions are settled in USDC on Polygon, and every order and fill is written to a public ledger. Repricing across two contracts of different maturities on the same event is *guaranteed* to be asynchronous at some horizon; asynchrony is mechanical. **The mechanism claim is not "asynchrony exists" — that is trivially true and not worth testing. The claim is that the asynchrony is directional, bounded inside a tradable window, and larger than round-trip cost.** All three are falsifiable and all three are attacked by §5.

**What is explicitly not offered as mechanism.** No appeal is made to the prior work's reported win rate. Under I-002 that number carries **zero evidentiary weight**; it informs only *which* hypothesis this firm chose to test, and it is not cited as support anywhere in this document.

**Devil's Advocate concession on record** [cited — Red-Team §B.6.6]: *"I cannot construct a serious argument that the mechanism is incoherent, and I am not going to pretend to."* That concession is the strongest thing this family has and it is a statement about coherence, not about existence.

---

## 4. Variant perception, and the persistence escape this family is required to pick

*§7.2(4): what does the market believe, what do we believe, why does the mispricing persist?*

**What the market believes:** each contract is priced on its own probability. **What we believe:** the joint pricing of a maturity pair is stale on the far leg for a bounded interval after news.

**Why it would persist — the escape, chosen and defended.** Red-Team §B.3.2 requires this family to name one of three and defend it. It also states the dilemma sharply: *"if the effect persists because the venue is too small to attract arbitrage, it cannot possibly demonstrate $20M of capacity."*

> **The family selects escape (c) — participation segmentation.**

| Escape | Selected? | Reason |
|---|---|---|
| (a) Regulatory segmentation — US-person access restrictions excluded sophisticated capital | **No** | It has a decay date set by regulators, not by the firm, and the restriction is unwinding. An edge whose mechanism is a regulatory barrier is a trade with an expiry, not a validated edge, and the firm should not spend Gate machinery on one. |
| (b) Settlement friction — USDC-on-Polygon deters mandated institutions | **No** | Falls monotonically as infrastructure matures. Same objection as (a), weaker version. |
| **(c) Participation segmentation** — event-market flow is structurally not relative-value flow | **Yes** | It is the only escape that supports a durable edge, and it is measurable: flow composition is on a public ledger. |

**The cost of choosing (c), stated rather than buried.** Red-Team §B.3.2 is right that (c) *"does not explain why professionals do not take the other side."* The honest answer is that it does not have to explain it *at institutional size* — it has to explain it at the size where the edge lives. **That is why §11's honest allocation matters and why the persistence dilemma dissolves at $50k and not at $2M.** The two are the same argument: the venue can be simultaneously too small to interest a professional desk and large enough to clear 10× a $50,000 allocation. **The dilemma the Devil's Advocate identified is real and is created entirely by the assumption of a full $2M pod. Removing that assumption removes the dilemma and costs the firm the materiality (§11).**

**What would falsify escape (c)** — recorded here because a persistence argument with no falsifier is a story: measured on-chain flow composition showing that a material fraction of resting liquidity on later-dated contracts is posted by addresses that also trade the near contract within the same hour. That is the signature of a relative-value participant, and it kills (c).

---

## 5. GATE 0 (2) — THE FALSIFIER · **F-001**

*Charter §4.3(2) and house rule 2: the specific observable that means the hypothesis is wrong.*

**Design note, stated so the seat's judgment is auditable.** KC-001 (§12) is a *kill condition*: an economic verdict on a forward window, on a date. The Charter requires **both**, and they are not substitutes. A kill condition answers "did it make money." A falsifier answers "was the structural claim ever true." A family can lose money for 95 days with an intact mechanism, and can make money for 95 days with no mechanism at all. **F-001 is the falsifier and it is mine.** It adopts the shape of the Devil's Advocate's §B.4 kill test — my own standing discipline is to run the cheapest killing test first, and that seat named it — with three modifications, each stated and justified below.

### F-001, in full

Let **L** be a *lead* contract and **F** a *forward* contract: the same underlying event, `resolution_date(F) > resolution_date(L)`, both listed simultaneously. A **spike event** is an instant `t₀` at which L's mid moves by ≥ 20 price points (¢) over a trailing 2-hour window.

Compute, on the accepted-spec tradable pair-day sample (§8), the **fillable response function**

```
ρ(k) = cross-correlation of hourly log-odds returns of L and F,  k ∈ [−36, +36] hours
k*   = argmax_k ρ(k)
```

evaluated on **paired-quotable bars only**: a bar enters the estimate only if *both* legs carried a two-sided quote in that bar and in the preceding bar. Bars failing that test are **dropped, never forward-filled** (§8.3).

> **The hypothesis is FALSIFIED — and the family is written up as a KILL memo — if ANY of the following three legs fires.**
>
> **(i) DIRECTION.** `k* ≤ 0`. The forward leg leads, or the two legs are contemporaneous. The asserted direction does not exist. *This is the leg most likely to fire and it is nearly free to evaluate.*
>
> **(ii) ARTIFACT.** Either `k* ≥ 24` hours — a peak a full day out is an information-diffusion story no microstructure mechanism in §3 supports, and is the signature of a data artifact rather than a lag — **or** `k*` computed on the paired-quotable subsample differs from `k*` computed on the all-bars (forward-filled) sample by more than **50%**. *The second clause is the I-024 discriminator and is the reason this leg exists (§8.3).*
>
> **(iii) MAGNITUDE.** The **median** signed fillable capture on the forward leg — measured from the executable price at `t₀ + 2h` to the executable price at `t₀ + k*`, in the direction of `sign(Δp_L)`, across all qualifying spike events — is **< 2.0¢ on a 50¢-equivalent contract**. A lag that exists but is smaller than its own round trip is not this hypothesis; the hypothesis is a *tradable* lag.

**Every leg is a single number, computed once, on one descriptive statistic. F-001 selects nothing from a menu and is registered as `N = 1`.**

### The three modifications to the Devil's Advocate's §B.4 test, each justified

| # | Modification | Reason |
|---|---|---|
| 1 | **Transposed from cross-venue to intra-venue.** §B.4 specifies "the one asset the pod names in advance as the economically-paired instrument" — a rate future, an index ETF, a crypto perp. The inherited family is **Polymarket-vs-Polymarket** (§7). | The red-team steel-manned a construction Pod B does not own. See §20(2) — this is reported to the CIO as a defect in the directed elements, not silently patched. |
| 2 | **Hourly bars over ±36h, not 5-minute bars over ±60min.** | The claimed horizon is 1–30 hours [cited — `agents/pm-digital-markets.md`]. A ±60-minute window cannot see a 20-hour lag and would falsify by construction; a 5-minute grid on a thin venue is mostly empty bars. ±36h brackets the claim with margin and makes leg (ii)'s 24-hour ceiling meaningful. |
| 3 | **Magnitude threshold 2.0¢, with the arithmetic corrected.** §B.4 states 2.0¢ is *"the round-trip cost of the `POLYMARKET` preset."* **It is not** [measured]: `half_spread_bps=100.0` is 1% of notional per side = **0.5¢ per side at 50¢ = 1.0¢ round trip**, which §B.2.3 of the same memo computes correctly. The 2.0¢ figure is 2× the round-trip spread. | I retain **2.0¢** and correct its label. Justified as: 1.0¢ round-trip spread + square-root impact at `impact_y = 2.0` + delay cost, plus margin so the falsifier fires on "cannot pay costs with room to spare" rather than on a knife edge. **The correction moves in the direction of a stricter test, not a softer one.** |

**Units discipline, binding.** Leg (iii) and every spread screen in this document are stated in **price points (cents), never in basis points of notional.** This is I-023(a) applied at the design level: the `POLYMARKET` preset expresses a cost that is approximately fixed in cents as a constant in bps, and therefore understates cost by ~2.5× at a 20¢ contract and ~5× at 10¢. A family whose signal is a *spike* is by construction a family that trades away from 50¢. Any figure in this document expressed in bps would be wrong in a known direction.

---

## 6. GATE 0 (3) — UNIVERSE, HORIZON, REBALANCE FREQUENCY, SUCCESS CRITERIA

*Stated before the first run, per §4.3(3).*

### 6.1 Universe

| Element | Specification |
|---|---|
| **Venue** | Polymarket only. Both legs. No off-venue reference asset is part of this family (§8.3 governs any variant that introduces one). |
| **Unit of observation** | **The pair-day**, not the contract-day. One calendar day of one ordered pair `(L, F)`. *This is a departure from `DATA-SPEC` §2 and is flagged as such: the spec counts contract-days, but this strategy cannot execute unless **both** legs are tradable on the same day.* |
| **Pair admissibility** | `L` and `F` share one underlying event under `DATA-SPEC` §3's contract→event mapping; `resolution_date(F) > resolution_date(L)`; both listed and live at `t₀`. |
| **Screening asymmetry, stated explicitly** | **`L` is read, `F` is executed.** `L` must satisfy T5, T6, T7 (validity of the observation). `F` must satisfy **all seven** of T1–T7 (executability). A pair-day is TRADABLE only if both hold. *The `DATA-SPEC` screens neither leg of a pair jointly; this is the intra-venue form of the gap Red-Team §B.1.2 identified in the reference leg.* |
| **Stratification** | `DATA-SPEC` §3 axes (i)–(iv), **plus underlying-event identity as a fifth axis**, per Red-Team §B.1.3. The >50% concentration rule of Ruling 001 §4.3 applies to the fifth axis too. This family's construction pools same-event pairs by design, so concentration on the fifth axis is **expected**, and if it fires the hypothesis is restated as being about that event class. |
| **Position notional** | `P_notional = USD 5,000` per contract leg. This fixes `DATA-SPEC` T1: **`F = 20 × P_notional = USD 100,000`** trailing-20-session median daily notional, per leg. |
| **Claimed gross edge** | `G = 4.0¢ per round trip on a 50¢-equivalent contract`. This fixes T3 under the Devil's Advocate's §B.2.2 correction: **`S_max = 0.25 × G = 1.0¢ half-spread`** (quoted full spread ≤ 2.0¢), which budgets round-trip spread at ≤ 50% of `G` rather than 100%. **The uncorrected `S_max = 0.5·G` is not used.** |
| **Regime cells** | **All four cells of {direction UP, DOWN} × {relative timing EARLIER, LATER} are traded.** The prior work's exclusion of UP+EARLIER is **not inherited** — see §6.4. |

### 6.2 Horizon and rebalance

| Element | Specification |
|---|---|
| Signal | Spike on `L`: mid move ≥ 20¢ over a trailing 2-hour window. |
| Entry | On `F`, at the first executable price **2 hours after `t₀`**. Never on the signal bar (§4.6). |
| Exit | First of: target +15¢, stop −25% of entry price, or **maximum holding period 36 hours**. |
| Rebalance | **Event-driven. There is no periodic rebalance.** `periods_per_year = 365` for the cost model, matching the `POLYMARKET` preset. |
| Bar granularity | Hourly, UTC. |

**On the parameter values.** The five values above (20¢ threshold, 2h delay, 15¢ target, 25% stop, 36h max hold) are the prior work's tuned settings, carried forward **unchanged and deliberately**. They are not a head start and they are not evidence. They are carried because (a) I-002 requires any use of prior tuned parameters to be declared, and this is the declaration; (b) changing them would be a fresh selection with no basis, adding trials without adding information; and (c) **§9's `N_inherited` already charges the family the full price of the search that produced them.** Having paid for the search, the family may as well use its output. What it may not do is re-tune — see §13.

### 6.3 Success criteria — stated before the first run

| Level | Criterion |
|---|---|
| **F-001 survival** | All three legs of §5 fail to fire. |
| **KC-001 survival** | Net expectancy per round trip > 0 **and** ≥ 30 tradable signal events, at 2026-10-31 (§12). |
| **Gate 1** | Every criterion in Charter §4.4, unmodified, computed by `castellan.evaluate_gate1` against `book/registry.db` with `N` = `N_inherited` + logged trials. **§9 states plainly that the length criterion alone requires a net out-of-sample Sharpe ≥ 2.07 on four years of history, and ≥ 4.14 before the R4(b) haircut.** No relaxation of any threshold is sought and none would be accepted. |
| **What "success" is honestly worth** | §11. At $50,000, an excellent result is worth ~10–25 bp of firm NAV per year. |

### 6.4 The regime exclusion — a design decision made now, and it is mine

The prior work skipped the UP+EARLIER cell [cited — `agents/pm-digital-markets.md`]. **That exclusion is not inherited.** Reasons, in order of weight:

1. **It was selected after seeing which regime hurt.** I-002 records it as one of the six selection acts that constitute the unreconstructable search. Importing it would be importing the single most overfit component of the prior work into a document whose purpose is to be free of it.
2. **KC-001 clause 2 forbids post-`C` exclusions.** The choice must be made *now*, at sealing, in one direction or the other. Deferring it is not available.
3. **Excluding it makes the family unfalsifiable in the one place it is most likely to be wrong.** If the effect is real, it should appear in three cells and be absent in one for a *reason*. If it is an artifact, the four-cell result is where that shows.

**Binding consequence:** the sealed specification trades all four cells, and **per-cell expectancy, event count and slugging ratio are reported separately** in every artifact this family produces, pooled figures never standing alone. If UP+EARLIER is the only loss-making cell, that is a finding to be reported, not a filter to be applied.

---

## 7. GATE 0 (4) — THE REQUIRED DATA EXISTS WITHIN PART III

*§4.3(4): the required data exists within Part III. No inadmissible dependencies.*

**Honest answer: partially, and the unresolved part is decision-relevant.**

| Requirement | Status | Provenance |
|---|---|---|
| Polymarket contract prices and volume | Listed as available in Charter §3.2 | [cited] |
| Polymarket **historical order-book snapshots** (needed for T2 and T4) | **UNCONFIRMED.** §3.2 lists "order book"; a live endpoint is not a retrievable historical snapshot. `DATA-SPEC` §7 step 1 exists to settle this and has not been run. | [cited — Ruling 001 §4.2; DATA-SPEC §8] |
| Resolution-criteria change history / native event grouping (T7, §3 mapping) | **UNCONFIRMED.** Same step 1. | [cited — DATA-SPEC §7] |
| Polymarket rows in `book/pit.db` | **Zero.** | [measured] |
| Polymarket loader in `castellan.loaders` | **Does not exist.** The module exposes yfinance, ccxt OHLCV, ccxt funding, EDGAR. | [measured] |
| `DATA-SPEC` acceptance by Validation | **Not granted.** Measurement does not begin until it is. | [cited — DATA-SPEC closing note] |
| Any off-venue reference asset | **Not required by this family.** Crypto spot/perp and the ETF panel are ingested to `pit.db` and available if a variant ever needs one. | [measured — DATA-INGEST-001 §2] |

**The consequence, drawn rather than left implicit.** Red-Team §B.2.1 is correct and I adopt it as this seat's position: **if T4 is unmeasurable, capacity is unmeasurable; an unevaluable Gate 1 criterion is INSUFFICIENT-DATA, which is never PASS; and Gate 1 requires every criterion to pass. T4-unmeasurable is therefore not a reporting qualifier — it is a Gate 1 disqualifier.** It is decidable by a documentation query costing a fraction of one Sonnet unit, before a single row is ingested, and §14 puts it first in the sequence for that reason.

**Inadmissible dependencies: none claimed.** This family does not require point-in-time fundamentals, a survivorship-free equity universe, tick data, borrow data, paid news, or brokerage connectivity. It requires one thing the firm has not confirmed it has, and the confirmation is cheap.

---

## 8. GATE 0 (5) — SURVIVORSHIP AND LOOK-AHEAD EXPOSURE, WITH MITIGATIONS NAMED

*§4.3(5). Red-Team §B.1.4 asserts that on today's spec this family **cannot** satisfy this item. That assertion is correct as of the red-team's writing. This section is the response, and it is written to be sufficient rather than to be a gesture.*

### 8.1 Survivorship

**The exposure.** Polymarket voids, delists and removes contracts. A universe enumerated by a live API query issued in 2026 returns the contracts that still exist and resolved cleanly. The absent contracts are disproportionately low-volume markets that were pulled, ambiguously-worded markets that were voided, and markets whose resolution was disputed or reversed. **Those are precisely the pairs on which a lag strategy would have lost money** — where the "information" the lead contract impounded turned out not to be information.

**`DATA-SPEC` T7 actively worsens this** [cited — Red-Team §B.1.4]: excluding contract-days whose resolution criteria changed mid-life is correct for measurement cleanliness and structurally removes the loss cases.

**Mitigations, named and binding:**

| # | Mitigation | Binding on |
|---|---|---|
| M1 | **The universe is enumerated from an archival, append-only on-chain source** — the condition registry — not from a live API listing. An append-only ledger cannot retroactively drop a market. | Head of Data & Infrastructure, at ingest |
| M2 | **The API-listing survivorship rate is measured and reported as a number**: count of conditions present on-chain but absent from the live API listing, as a fraction of all conditions in the candidate universe, per year. It is reported in every artifact this family produces. | Head of Data & Infrastructure |
| M3 | **T7-excluded contract-days are counted and reported separately, never silently dropped.** The count of pair-days removed by T7, and their share of the candidate sample, is a required field. If T7 removes >10% of candidate pair-days, the family's results are reported with the removal rate on the face of the document. | Head of Data & Infrastructure → Validation |
| M4 | **Voided and disputed-resolution contracts are retained in the sample as observations, marked, and their P&L attributed at the worst admissible outcome** — not excluded. Exclusion is what makes the survivorship bias; retention at the adverse outcome is the conservative treatment. | PM Pod B |

**If M1 is not achievable — i.e. if the on-chain condition registry is not enumerable by this firm — that is a Gate 0(5) failure and the family is REJECTED, not qualified.** Stated in advance so it is not negotiated later.

### 8.2 Look-ahead

| Channel | Mitigation |
|---|---|
| **Screening on same-day realized volume** | Every T1–T7 screen is evaluated on a **trailing window ending strictly before the day screened** [cited — Ruling 001 §4.2 overriding constraint; DATA-SPEC §2]. Binding on both legs of a pair. |
| **Filling on the signal bar** | Entry is at the first executable price **2 hours after `t₀`** (§6.2). §4.6's minimum-one-bar rule is satisfied by construction, and §8.3 explains why satisfying it is not sufficient here. |
| **Vendor pre-adjusted series** | Not applicable — no adjusted series is involved. All prices consumed via `PITStore` per A4. |
| **`knowledge_time` vs `event_time`** | All queries filter on `knowledge_time ≤ decision_time`. **Declared limitation** [cited — DATA-INGEST-001 §3]: any historical backfill carries `knowledge_time` = ingestion instant, so this family may not claim to have tested PIT *knowledge* for dates before its ingest session. It tests PIT *ordering*, which is what the hypothesis needs. |
| **The prior search** | Not a look-ahead channel but a selection channel. Handled at §9, not here. |

### 8.3 I-024 — CROSS-VENUE CLOCK ALIGNMENT, NAMED AS A BINDING CONFOUND

**This is the confound most likely to produce a large, robust, reproducible and entirely uncapturable number, and the design below is admissible only because it can distinguish it from a genuine lag. A design that cannot distinguish them is not admissible.**

**The confound as the Charter leaves it exposed.** §4.6's protection is *"never fill at the same bar that generated the signal."* That rule was written for a single-venue, single-clock world. It is satisfied by a fill **53 hours later across a weekend**. Polymarket trades 24/7; an equity or ETF reference leg does not. A measured "lag" between them is then the overnight and weekend information gap relabelled as alpha [cited — I-024, Red-Team §B.1.2].

**The transposition, stated because it changes the specification.** The inherited family is **intra-venue**: both legs are Polymarket contracts and both trade 24/7. The literal cross-venue rule — *drop out-of-session reference bars* — has no session calendar to refer to. **The confound does not disappear. It transposes, and in one respect it is worse:** an exchange session calendar is public, fixed, and knowable in advance; a thin Polymarket contract's periods of quote-death are contract-specific, irregular, and observable only from the data itself. **The "lag" then becomes the interval until the forward leg receives any order flow at all — which is exactly the interval in which it was unfillable.**

**Both forms are therefore specified, and both bind.**

**(A) Intra-venue — binding on this family as sealed.**

1. **Alignment.** Both legs are resampled to a **common hourly UTC grid** via `pit_price_panel` (A4). No local time is used anywhere. Timestamps enter `PITStore` as absolute UTC instants; the `yfinance` offset defect (I-020) does not touch this family because no `yfinance` series is used, and this is stated so it is not assumed to be a general clearance.
2. **Quote-liveness gating — the operative rule.** A bar enters any estimate **only if both legs carried a two-sided quote in that bar and in the preceding bar**. Bars failing that test are **DROPPED, NOT FORWARD-FILLED.** Forward-filling is the operation that manufactures the artifact: it converts "no one quoted this contract for 19 hours" into a sequence of unchanged prices followed by a large move, which is indistinguishable from a lag and is unfillable.
3. **Entry executability.** An entry is admitted only if the forward leg carried a two-sided quote within `S_max` **at the entry instant `t₀ + 2h`**, not merely at some point in the interval. An entry priced off a quote that was not there is a fill that did not happen.
4. **Gap exclusion.** A signal whose entry instant falls inside a forward-leg quote gap exceeding **6 consecutive hours** is **excluded from the primary result and reported as a separate subperiod with its own expectancy and event count** — never averaged in. This follows Ruling 002 R2's refusal to average mixed windows, applied to a mixed-liquidity sample rather than a mixed-time one.

**(B) Cross-venue — binding on any variant that introduces an off-venue reference leg, and stated now because nothing may be added after sealing.**

1. The reference asset's **tradable session is stated in UTC**, in writing, before the run.
2. Reference bars **outside that session are dropped, not forward-filled.**
3. A signal whose first executable reference instant falls **more than one session boundary later** is excluded from the primary result and reported as a separate subperiod with its own Sharpe and observation count.
4. The reference leg is screened for tradability on the same standard as the Polymarket leg. *The `DATA-SPEC` screens Polymarket contract-days through T1–T7 and never screens a reference leg at all* [cited — Red-Team §B.1.2]; this clause closes that for any variant.

**(C) The discriminator — how a session-gap or quote-gap artifact is distinguished from a genuine lag.** Two specific observables, both pre-registered, both cheap:

| # | Test | What a genuine lag looks like | What an artifact looks like |
|---|---|---|---|
| **D1** | `k*` on the paired-quotable subsample vs. `k*` on the all-bars forward-filled sample. | The two agree within 50%. The lag is a property of information flow and survives requiring the market to have been open for business. | `k*` collapses toward zero on the quotable subsample, or the effect disappears with it. **The "lag" was the quote gap.** |
| **D2** | Cross-sectional regression of `k*` (estimated per pair) on the forward leg's **median inter-quote interval** over the same window. | Slope statistically indistinguishable from zero. The lag does not care how often the far leg is quoted. | Slope ≈ 1 — `k*` is a monotone function of quote sparsity. **The lag *is* the quote sparsity, measured in a different unit.** |

**D1 is leg (ii) of the falsifier F-001 and can kill the family on its own. D2 is a required diagnostic in every artifact, and a slope indistinguishable from 1 is reported as an artifact finding whether or not F-001 has fired.**

**This is the section that makes the design admissible.** Without D1 and D2 the family produces a number it cannot interpret, and Red-Team §B.1.2's prediction — large, statistically strong, robust across parameters, entirely uncapturable — becomes the expected outcome rather than a risk.

---

## 9. GATE 0 (6) — TRIAL COUNTER OPENED AND INSTRUMENTED · **`N_inherited` = 31,250**

*§4.3(6) as amended by A2: the hypothesis family exists in `book/registry.db` and every backtest routes through `castellan.run_backtest`. A backtest number produced outside the engine is inadmissible in any document.*

### 9.1 The declaration

> **The registry opens seeded at `N_inherited` = 31,250. Not at zero.**

### 9.2 The construction, stated so it can be attacked

| Component | Value | Provenance |
|---|---|---|
| Tuned parameters in the prior search | **5** — spike threshold, entry delay, target, stop, window length | [cited — I-002; `agents/pm-digital-markets.md`] |
| Values per parameter | **5** | [cited — Red-Team §B.1.1: "evaluated at even five values per parameter"] |
| Parameter-grid component | **5⁵ = 3,125** | [measured — arithmetic] |
| **Regime-candidate factor** | **× 10** | **[inferred]** — the CIO's honest estimate of the menu of conventional crypto and event-market regime boundaries from which the prior work's single regime exclusion was selected: COVID, the 2021 bull, May-2021, LUNA/UST, FTX, the 2022 bear, election cycles, funding-sign regimes, post-ETF-approval, early-venue illiquidity |
| **`N_inherited`** | **31,250** | [inferred — product of the above] |

**The any-subset reading was considered and rejected.** Treating the regime exclusion as a choice over all subsets of a 10-item menu gives `2¹⁰ × 3,125 ≈ 3.2 million`. **Rejected as overstating realistic human search** — a researcher who tries one exclusion at a time does not traverse the power set. The rejection is recorded so that the number 31,250 is understood as a *deliberately conservative* reading of the prior search, not as the largest defensible one.

**Label discipline.** The `× 10` factor is **[inferred]**, not measured and not cited. It is stated as such here, must be stated as such in every downstream artifact, and an unlabelled restatement of it is a house-rule-6 defect.

### 9.3 What would justify revising it

| Direction | Requirement | Logged? |
|---|---|---|
| **Downward** | **Reconstructed evidence of the actual candidates considered** — a parameter log, a run history, a dated record of which regimes were tried. **Not a recollection.** A recollection of the size of one's own prior search is precisely the quantity a researcher cannot report reliably, and I-002 already records that the artifact does not exist. | **Yes.** Any downward revision is a logged Decision Record entry with the evidence attached, and a new `hypothesis_sealed` event on a **successor family** — this family's binding fields cannot be amended (P3). |
| **Upward** | Any evidence that the prior search was larger — additional parameters, additional regime candidates, additional venues or contract classes tried and abandoned. | **Yes**, same mechanism. |

**Asymmetry, deliberate.** Upward revision requires only evidence that more was tried. Downward revision requires evidence of what was tried *in total*. That asymmetry is the correct one: the failure mode the Charter fears (Appendix B #2) is a lost denominator, and lost denominators are always lost in the direction of being too small.

### 9.4 What this does to the family's prospects — stated plainly, as directed

**Calibration against Charter §4.1's own table.** §4.1 gives the expected best in-sample Sharpe on pure noise at `N = 10,000` as **3.86 · σ_SR**. At `N = 31,250`:

| Quantity | Value at N = 31,250 | Provenance |
|---|---|---|
| Loose asymptotic bound `√(2·ln N)` | **4.55 · σ_SR** | [measured] |
| BLP&Z expected max (the formula §4.1 actually specifies) | **4.13 · σ_SR** | [measured — `castellan.stats.expected_max_sharpe(31250, 1.0)`] |
| Same, at N = 3,125 (grid only, no regime factor) | 3.57 · σ_SR | [measured] |
| Same, at N = 10,000 (the Charter's table endpoint) | 3.86 · σ_SR | [measured — reproduces the Charter's 3.86, confirming the harness implements §4.1] |

**And the consequence that actually decides this family — Charter §4.4's `≥ MinBTL(N)` clause** [measured — `castellan.stats.min_backtest_length_years(31250, SR, 365)`]:

| Required net annual Sharpe, out-of-sample, after full costs | Minimum backtest length the Charter then demands |
|---:|---:|
| 1.0 *(the Gate 1 floor)* | **17.06 years** |
| 1.5 | 7.58 years |
| 2.0 | 4.27 years |
| 2.38 | 3.00 years |
| **2.07** | **4.00 years** |

> **Read the last row.** Charter §4.4 independently requires **≥ 4 years** of backtest length. To satisfy `MinBTL(31,250)` at exactly four years, this family must demonstrate a **net out-of-sample Sharpe of 2.07 after the full §4.6 cost stack.** Under Ruling 002 **R4(b)**, which this family accepts (§10), the presumptive 50% published-signal haircut means the **pre-haircut** requirement is approximately **4.14**.
>
> **A net Sharpe above 4 on a thin prediction-market venue, after costs, sustained over four years, is not a result this firm should expect to see. If it sees one, the first hypothesis is that something is wrong with the measurement — and §8.3 exists to name what.**

**The honest summary, which is the point of declaring `N_inherited` at all:** seeded honestly, **this family's Gate 1 arithmetic probably fails, and that is the correct outcome if it is the true one** [cited — Red-Team §B.1.1]. The family survives on *admissibility* — it can be researched, it can accrue a forward record, it can produce a decisive KILL memo — and it loses on *Gate 1 reachability*.

**One further observation that saves the firm a future argument.** At `N = 3,125` (the grid alone, no regime factor) the expected max is 3.57·σ_SR and `MinBTL` at SR 1.0 is 12.72 years. **Both readings are fatal. The family's fate does not turn on the factor of 10.** Any future debate over whether the multiplier should be 10, or 4, or 20, is not worth compute, and this sentence exists so that it is not spent.

### 9.5 The blocking defect: **the harness cannot seed `N`**

> **[measured — `harness/castellan/registry.py:428–451`]** `TrialRegistry.family_stats` computes `n = COUNT(*) FROM trials WHERE family IN (chain)`. There is **no `n_inherited` column** on `hypotheses`, **no `n_inherited` parameter** on `open_hypothesis`, and **no path by which a declared floor reaches `FamilyStats.n_trials`** — which is the value `gates.py` passes to `deflated_sharpe_ratio`, `min_backtest_length_years`, and the PBO computation.

**Consequence, stated at full strength.** If this family is sealed today and evaluated later, **DSR and PBO will be computed against the count of logged trials — a number in the tens — while this document declares 31,250.** The Validation Report would read `N = 12` and `DSR = 0.97`, would be arithmetically valid, and would be substantively meaningless. **Worse than that: a document would exist claiming the denominator had been fixed.** That is the exact failure Red-Team §B.1.1 called the single strongest objection in its memo, re-created one level down, with a paper trail that makes it harder to notice rather than easier.

**Required remediation, and it is a condition precedent to sealing (§18):**

| # | Requirement | Owner |
|---|---|---|
| H1 | `hypotheses` gains an `n_inherited INTEGER NOT NULL DEFAULT 0` column; `open_hypothesis` gains the parameter; it enters the **P2 binding field set** and therefore the `prereg_sha256`. A declared denominator that is not sealed is not a denominator. | Head of Data & Infrastructure |
| H2 | `family_stats` returns `n_trials = n_inherited + COUNT(*)`, summed transitively across `predecessor_chain` exactly as the count already is. | Head of Data & Infrastructure |
| H3 | **Negative test:** a family with `n_inherited = 31,250` and 2 logged trials must produce `FamilyStats.n_trials == 31252`, and `evaluate_gate1` must **FAIL** the length criterion on any backtest shorter than `MinBTL(31252)`. Under today's code this reads PASS. | **Authored by Validation, before implementation** — per I-021, whose entire finding is that the implementing seat authoring its own acceptance test is how I-015 happened |
| H4 | `σ_SR` (cross-sectional trial-Sharpe standard deviation) is **still computed from real logged trials only.** Phantom trials have no return series and none may be synthesised. This is stated so that H1–H2 are not over-read: seeding `N` corrects the denominator in DSR and MinBTL; it does not and cannot correct `σ_SR`, and any report using the seeded `N` must say so. | Validation |

**Filed as a new HIGH-severity Issue Log candidate: `the declared N_inherited has no path into the registry`.** Owner: head-of-data-infra → quant-validation. It is the CRO's log to write; this seat raises it.

### 9.6 Trial budget

**40** post-seal trials, allocated:

| Allocation | Trials |
|---|---:|
| F-001 (§5) — one descriptive statistic, selects nothing | 1 |
| Sequenced diagnostics of §14 (D2, per-cell decomposition, survivorship rate, cost sensitivity, T1-window robustness) | ≤ 9 |
| Forward-window signal generation and its diagnostics through 2026-10-31 | 30 |

**No ±50% parameter grid is authorized under this pre-registration.** Reason, and it is a research judgment rather than a budget economy: §4.4's parameter-surface criterion (≥60% of the ±50% grid net-profitable) cannot rescue a family that fails the length criterion, and running 3,125 grid points through `run_parameter_grid` to evaluate a criterion on a family that fails a prior criterion is spending the firm's scarcest resource to decorate a corpse. **If — and only if — F-001 survives, Seat 9 measures ≥4 years of continuous tradable span, T4 proves directly measurable, and H1–H4 land, then a successor family is opened with `predecessor_family = "forward-lag-001"`, inheriting `N` transitively, and the grid runs there.** The plateau centroid, never the argmax, is what would advance.

**The budget is real.** A family over budget is this seat's finding to raise before Validation raises it. Note the live defect that makes it necessary to say so: **I-022 — `gates.py` builds the trial-count criterion with the verdict argument hard-coded to the literal `True`, so an over-budget family reads PASS with a note** [measured]. Until I-022 is fixed, the budget is enforced by this seat and by nothing else.

---

## 10. GATE 0 (7) — HOLDOUT DEFINED AND LOCKED · and the R1–R4 fields

*§4.3(7). R1–R4 are binding under D-006.*

### 10.1 The holdout

| Field | Value |
|---|---|
| **Regime** | Option D (D-006). `C` = the pre-registration seal date (D-007). Holdout = `[C, G]`, forward, growing with wall-clock. |
| **`C`** | **The seal date.** Not fixed by this document. Fixed by Pod B's `open_hypothesis` call, on the same UTC day as the vault seal. |
| **In-sample** | `[start of usable Polymarket history, C]`, where "usable" is the accepted-`DATA-SPEC` measurement, unmeasured today. |
| **Vault** | One `HoldoutVault` per (dataset, family) under `book/vaults/`, sealed with `family="forward-lag-001"`, `cutoff=C`, `holdout_end_rule="open-ended, forward from C"`. **The passphrase is the Principal's and is never written to this repo, to Oracle, or to any file.** |
| **Sequencing, binding** | The vault is sealed **on or before the calendar day of `C`, in the same session as the `open_hypothesis` call.** P7 fails Gate 1 if the seal postdates `C` at UTC day granularity. |
| **Ingest ceiling** | `seal()` writes the D2 ceiling into `PITStore`. All Polymarket ingest occurs **after** the seal and is bounded by it. The crypto and ETF panels already in `pit.db` are bounded at `2026-07-28T23:59:59Z` [measured — DATA-INGEST-001 §7], which is conservative against any `C ≥ 2026-07-28`. |
| **Opened** | Once, at Gate 1, by Validation, with the Principal notified. A second look permanently retires it. |

### 10.2 R1 — holdout classification

> **`holdout_classification = FORWARD`.**

The window `[C, G]` postdates the pre-registration wall-clock in its entirety, and therefore closes channels K1–K5 for that window. **R2 does not fire:** the in-sample is entirely historical, the holdout is entirely forward, and no mixed window exists to decompose. If any future variant pins `C` before its own seal date — which P7 forbids — R2's decomposition becomes mandatory.

**The R1 sentence for a HISTORICAL classification is therefore not required and is not reproduced.** Stated explicitly so its absence is not read as an omission.

**What FORWARD does not fix.** It closes the forward channel. It does nothing about **I-011** — the search embedded in the researcher before the freeze — which contaminates the in-sample period, is invariant to where `C` is placed, and cannot be fixed by waiting. §9's `N_inherited` is the firm's only instrument against I-011 for this family, and §9.5 records that the instrument is not currently connected to anything.

### 10.3 R3 — the forward-window falsifier

R3 is mandatory only for a HISTORICAL classification. **This family carries one anyway**, because the property R3 delivers — a claim about data that did not exist when the claim was made — is worth having regardless of classification, and because the Principal has signed it.

| R3 field | Value |
|---|---|
| `forward_window_start` | `2026-07-28` (= `C`; the seal is directed for today) |
| `forward_window_min_length` | `12.0` — **units: months.** Charter §4.4's holdout floor. *Minor latent defect flagged: the harness stores this as an unlabelled `REAL`. A float with no unit is a misreading waiting to happen; recorded for the Issue Log, not blocking.* |
| `forward_kill_condition` | **KC-001, §12, in full.** The observation date is **2026-10-31**, which is 95 days from `C` if the seal lands today. **The date is absolute and does not move** — if the seal slips a day, the window shortens; the date does not extend. |

### 10.4 R4(a) — model-prior provenance

Which seats originated or ratified each binding design field, with model and stated cutoff. Per I-009 the firm does not know its own seats' training cutoffs and the authoritative reference does not publish them; every cutoff below therefore reads `unknown` and **that is itself the finding**, recorded rather than filled with a plausible number.

| Binding field | Originated by | Ratified by | Model | Stated cutoff |
|---|---|---|---|---|
| Hypothesis statement, mechanism | **the Principal** (D-004) | Director of Research | human | n/a — advances continuously; this is K5, and Ruling 002 §3.3(3) notes it is documented where K4 is only hypothesised |
| Parameter values (§6.2) | the Principal's prior work | Director of Research (carried unchanged, §6.2) | human | n/a |
| Regime-cell decision (§6.4) | **Director of Research** | — | Opus | unknown [assumed] |
| Falsifier F-001 (§5) | **Director of Research**, adopting the shape of Devil's Advocate §B.4 | — | Opus | unknown [assumed] |
| I-024 alignment and discriminators (§8.3) | Devil's Advocate (cross-venue form) · Director of Research (intra-venue transposition, D1/D2) | — | Opus | unknown [assumed] |
| `N_inherited` construction (§9) | Devil's Advocate (the requirement) · CIO (the ×10 factor) · **the Principal** (the floor, fixed by direction) | Director of Research | Opus / human | unknown [assumed] |
| KC-001 (§12) | Devil's Advocate | **the Principal, signed as written including the silence clause** | Opus / human | unknown [assumed] |
| T1/T3 numeric values (§6.1) | Director of Research (`P_notional`, `G`) on Head of Data & Infrastructure's formulas | — | Opus / Sonnet | unknown [assumed] |
| Holdout regime | Validation (Rulings 001, 002) · **the Principal** (D-006 Option D, D-007 `C` definition) | — | Opus / human | unknown [assumed] |

### 10.5 R4(b) — the published-signal haircut

> **`published_signal_haircut_applied = 0.50`. The presumption is accepted. No exemption is sought.**

Ruling 002 R4(b) makes a hypothesis generated from an LLM seat's priors presumptively an edge derived from published research, carrying §4.6's 50% haircut unless the sponsor argues at Gate 0 that the mechanism is not publicly documented and Validation accepts.

**This seat does not make that argument, for two reasons, and states them so the decision is auditable:**

1. **It would fail.** Prediction-market lead-lag is a studied question with public results [cited — Red-Team §B.3.1(4)]. Arguing otherwise would spend Validation's scarcest unit on a claim this seat does not believe.
2. **It would not matter.** §9.4 shows the family must clear a net Sharpe of 2.07 to satisfy the length criterion at four years. Winning the exemption changes the pre-haircut requirement from 4.14 to 2.07. **Both are out of reach on this venue.** The haircut is not what kills this family.

**Live defect noted:** I-019 records that R4(a)/(b) have schema but **no computation attached** — the fields exist and nothing enforces them. The 0.50 recorded here is a declaration, not an enforced deduction, until I-019 closes.

---

## 11. INTENDED INITIAL ALLOCATION — stated honestly, with what it dissolves and what it costs

> **Intended initial allocation: USD 50,000.** Order tens of thousands. **Not $2,000,000.**
> **`P_notional` = USD 5,000 per contract leg** (§6.1), i.e. ten concurrent pair-legs at full size.

### 11.1 What this dissolves — the capacity dilemma

Charter §4.4 requires **capacity ≥ 10× the intended initial allocation** at target net Sharpe.

| Assumption | Intended allocation | §4.4 capacity requirement |
|---|---:|---:|
| Devil's Advocate §B.3.2 — the full Pod B book | $2,000,000 | **$20,000,000** |
| **This pre-registration — honest** | **$50,000** | **$500,000** |

Red-Team §B.3.2 framed the dilemma as decisive: *"if the effect persists because the venue is too small to attract arbitrage, it cannot possibly demonstrate $20M of capacity. The single best reason to believe the edge is real is the same fact that makes it inadmissible."*

**The dilemma is real and it is created entirely by the $2M assumption.** At an honest $50,000 the requirement is $500,000 of demonstrated depth at target net Sharpe. **The venue can be simultaneously too small to be worth a serious firm's time and large enough to clear 10× this allocation.** The persistence argument in §4 escape (c) and the capacity criterion stop contradicting each other.

**What it does not dissolve.** §4.4's capacity criterion still has to be *evaluated*, and evaluating it still requires T4 — resting depth within the T3 band, on both sides. **If historical order-book depth is unretrievable, capacity is INSUFFICIENT-DATA at $500k exactly as it is at $20M** (§7, Red-Team §B.2.1). The honest allocation lowers the bar; it does not supply the instrument.

### 11.2 What it costs — materiality

| Measure | Value |
|---|---|
| $50,000 as a share of Pod B's $2,000,000 | **2.5%** |
| $50,000 as a share of the firm's $10,000,000 paper book | **0.5%** |
| Illustrative firm-level contribution at net Sharpe 2.0 and 25% annualized sleeve volatility | ~$12,500/yr = **~12.5 bp of firm NAV** [inferred — arithmetic on stated assumptions, not a forecast] |
| Illustrative firm-level contribution at a 50% annual return on the sleeve | $25,000/yr = **~25 bp of firm NAV** [inferred] |

> **Even an excellent Sharpe here is close to immaterial to firm P&L.** A sleeve at 0.5% of capital cannot move the firm's return, cannot carry a pod, and cannot repay the compute the firm has already spent governing it — four Opus units to date, 100% of the firm's Opus spend, all Principal-originated [measured — I-025].
>
> **The family survives on admissibility and loses on materiality.** That is the trade, and the pre-registration is where it is made explicit rather than discovered later.

### 11.3 The consequence this seat draws from it

A strategy that is immaterial at its honest size is not thereby worthless — it can be a research result, a proof that the firm's protocol works end to end, and a genuine KILL memo. **It is, however, not an investment,** and it should not be given the compute an investment would deserve. §17 acts on that.

---

## 12. KC-001 — THE BINDING KILL CONDITION

*Reproduced verbatim from Red-Team §B.5. The Principal has signed it as written, silence-kill included. It is not softened here, and this seat notes for the record that the Devil's Advocate predicted the silence clause is the one someone would try to weaken.*

> ### KC-001 — forward-lag family
>
> **Sponsor:** the Principal, via PM Pod B. **Accepted by the sponsor in writing before any capital — paper or real — is allocated to this family.**
>
> **Observation date: 2026-10-31**, being 95 days after the pre-registration seal `C = 2026-07-28`. The date is fixed and does not move with the sprint calendar, the ingest schedule, or the harness.
>
> **On that date, Validation computes — from `book/registry.db` and `book/pit.db` alone, on the frozen pre-registration, over the forward window `[2026-07-28, 2026-10-31]`:**
>
> **(i)** realized **net expectancy per round-trip trade**, defined as `(Σ realized P&L) ÷ (count of round-trip trades)`, in price points on the [0,1] contract scale, after the full §4.6 cost stack at **1× modelled costs** using the `POLYMARKET` preset as amended per proposed I-021; and
> **(ii)** the count of **tradable signal events** generated by the frozen specification under its own pre-registered screen.
>
> ### The family is KILLED — registry marked TERMINATED, no further trials, no Gate 1 submission ever — if EITHER:
> ### (a) net expectancy ≤ 0; OR
> ### (b) fewer than 30 tradable signal events occurred in the window.
>
> **Clause (b) is not a technicality and must not be waived as one.** It kills on *insufficient signal*, which is the outcome nobody plans for and which otherwise becomes "wait a little longer" indefinitely. A family that cannot generate 30 events in 95 days on its own chosen venue cannot generate a testable rate on any horizon this firm can wait for, and its capacity is thereby also answered (§B.3.2).
>
> **Anti-reinterpretation clauses, binding:**
> 1. **No re-parameterisation.** Expectancy is computed on the sealed specification. Not a tuned variant, not a subset, not "the version we would have run."
> 2. **No post-`C` exclusions.** Any regime filter, date exclusion, contract exclusion or universe restriction not present in the sealed pre-registration is inadmissible in this computation. This clause exists specifically because the prior work carried **1 regime exclusion** [cited — I-002].
> 3. **No restatement as continuation.** A hypothesis restated after 2026-10-31 is a **new family**, opened with `N_inherited` ≥ the killed family's final `n_trials` plus its own `N_inherited`. It does not inherit the killed family's schedule, its allocation, or its narrative.
> 4. **Kill is automatic on the date.** It requires no meeting, no vote, and no CIO concurrence. **It is not appealable to the CIO.** Only the Principal may reverse it, in writing; the reversal is logged in `logs/DECISION_RECORD.md` as an Appendix-B-#4 override with its reason stated on the face of the record and reported in the next Monthly Letter.
> 5. **Silence is a kill.** If the computation is not performed on 2026-10-31 — for any reason, including that ingest never happened or the harness was not ready — **the family is killed by default.** A kill condition that can be defeated by not running it is not a kill condition. This clause is deliberate and I expect it to be the one someone tries to soften.

**Condition precedent, separately binding** [cited — Red-Team §B.5]: the T4 measurability query of §B.4 is answered in writing **by sprint close, 2026-08-11**. If unanswered by that date, the family is ADMITTED-AS-EXPLORATORY only, and remains so until it is answered.

### 12.1 Three notes on KC-001, none of which soften it

1. **The reference to "proposed I-021" is now I-023** — the Issue Log renumbered the Devil's Advocate's proposals on entry (its I-019→I-021 through I-023→I-025). The cost-model defect KC-001 refers to is **I-023**. This is an identifier correction, not an amendment; the substance is untouched.
2. **The "95 days after `C` = 2026-07-28"** gloss holds only if the seal lands today. **The absolute date 2026-10-31 governs.** If the seal slips, the window shortens and the date does not move — which is the strict reading, consistent with clause 4's "automatic on the date."
3. **This seat's honest expectation, recorded now so it is not claimed as foresight later** [inferred]: given zero Polymarket rows in `pit.db`, no loader, an unaccepted `DATA-SPEC`, and Seat 9 already overcommitted [cited — Red-Team §A.2], **the modal outcome is that KC-001 kills this family by clause 5 on 2026-10-31 without a number ever having been computed.** That is the rule working exactly as designed, and it is a reason to spend less on this family now (§17), not a reason to soften the clause.

---

## 13. METHOD — the sequenced test plan, cheapest kill first

*§7.2(5): universe, data, timestamps, splits, embargo, cost model, trial history. The universe and timestamps are §6 and §8.2. This section is the order of operations.*

| # | Step | Cost | Kills what | Registry trials |
|---:|---|---|---|---:|
| **0** | **The T4 measurability query.** `DATA-SPEC` §7 step 1, and nothing else: are historical Polymarket order-book snapshots retrievable, or only the live book? Also: resolution-criteria change history, native event grouping. **Answered in writing, source cited, by 2026-08-11.** | fraction of a Sonnet unit | **The investment case.** If no: T4 unmeasurable → capacity unevaluable → INSUFFICIENT-DATA → Gate 1 unreachable at any Sharpe. | 0 |
| **1** | **Archival universe enumeration** from the on-chain condition registry (M1), with the API-listing survivorship rate measured (M2). | ~1 Sonnet unit | Gate 0(5) if M1 proves impossible. | 0 |
| **2** | **Minimal ingest** — the single densest pair-cluster by traded notional over available history, hourly, into `PITStore` via a new Polymarket loader. Raw only; two-timestamp discipline; bounded by the sealed D2 ceiling. | ~1 Sonnet unit | nothing — enabling | 0 |
| **3** | **F-001** (§5). One descriptive statistic on the paired-quotable sample. Direction, artifact, magnitude, in one run. | ~1 Sonnet unit | **The thesis.** Three independent ways it dies. | **1** |
| **4** | **D2 diagnostic** (§8.3C) — `k*` regressed on forward-leg quote sparsity. | shared with step 3 | Interprets step 3. A slope near 1 is an artifact finding whether or not F-001 fired. | 1 |
| **5** | Per-cell decomposition (§6.4), survivorship rate (M2), T7 removal rate (M3), cost sensitivity at 1× and 2×, T1 window robustness (20 vs 5 sessions). | ~1 Sonnet unit | nothing — required reporting | ≤ 7 |
| **6** | Forward-window signal generation through 2026-10-31, for KC-001. | ongoing | KC-001 | ≤ 30 |

**Steps 0–4 are the whole decision.** Everything after step 4 exists to make a *positive* result trustworthy, and §9.4 says a positive result cannot clear Gate 1 on this venue's history at this `N`. **None of it is needed to make a negative result decisive** [cited — Red-Team §B.4].

**Standing methodological requirements, all binding and none waived:** prices via `PITStore` only (A4); every backtest through `castellan.run_backtest` against this family (A2); purged k-fold with 1% embargo; costs from `castellan.costs.CostModel` presets only — **no hand-rolled cost numbers anywhere, including the paper book**; gross and net always, with the breakeven cost; `backtest_years` passed **explicitly** as true calendar span, never left to the harness fallback (G1–G5, `DATA-SPEC` §4).

---

## 14. WHAT CANNOT BE EVALUATED, AND WHY IT MATTERS BEFORE THE FIRST RUN

*Stated at pre-registration rather than discovered at Gate 1. Each of these is a criterion §4.4 requires and this family cannot presently deliver.*

| §4.4 criterion | Status | Reason |
|---|---|---|
| **Capacity ≥ 10× allocation** | **UNEVALUABLE unless step 0 returns yes** | T4 requires historical resting depth. Unmeasurable ⇒ INSUFFICIENT-DATA ⇒ never PASS. |
| **Backtest length ≥ MinBTL(N) and ≥ 4 years and ≥ 1 regime cycle** | **Probably FAIL** | §9.4: 17.06 years at SR 1.0; 4 years requires SR ≥ 2.07 net. Polymarket's usable span is unmeasured and per I-004 plausibly under 4 years. Validation has **pre-committed**: <4 years ⇒ REJECTED for Gate 1, exploratory only, no Sharpe changes it. |
| **Parameter surface — ≥60% of ±50% grid net-profitable** | **UNEVALUABLE under this pre-registration** | No grid is authorized (§9.6). Evaluating it requires a successor family. Declared now rather than discovered. |
| **Cost robustness at 2× modelled costs** | **Evaluable but contaminated** | **I-023(a):** the `POLYMARKET` half-spread is a bps constant where the true cost is ~fixed in cents — understated ~2.5× at 20¢, ~5× at 10¢. A spike strategy trades away from 50¢ by construction. Until I-023(a) is fixed, "2× costs" is not 2× the real cost. |
| **Net Sharpe / t-stat / DSR / PBO** | **Computable but wrong-denominatored** | **§9.5:** the harness cannot seed `N_inherited`. Until H1–H4 land, every one of these is computed against a denominator in the tens. |
| **Resolution-risk charge** | **Cannot be expressed at all** | **I-023(b):** `CostModel` has commission, half-spread, impact, borrow, funding — and no field for oracle or adverse-resolution risk. That is the largest idiosyncratic risk in the Pod B mandate. **The paper book will systematically over-report this family's net by an unmeasured amount whose sign is known.** A required addition to the cost library, Principal-approved, and a Gate 0 condition. |
| **Correlation to live pod strategies** | Trivially satisfiable | No live strategies exist. Recorded so the PASS is not read as informative. |
| **Red-Team Memo with a binding named kill condition** | **SATISFIED** | REDTEAM-001, KC-001, signed by the Principal. |

---

## 15. RISKS, AND WHAT KILLS THIS

Ranked by how much each should move the decision, following the Devil's Advocate's own ranking where it applies and departing where this seat disagrees.

| Rank | Risk | Kills it how |
|---:|---|---|
| 1 | **`N_inherited` has no path into the registry (§9.5)** | Every Part IV statistic is computed against the wrong denominator while a document claims otherwise. Blocking; H1–H4. |
| 2 | **MinBTL(31,250) exceeds any plausible venue history (§9.4)** | Gate 1 length criterion FAILs at any Sharpe below 2.07 net. Arithmetic, not opinion. |
| 3 | **T4 unmeasurable ⇒ capacity unevaluable (§7)** | Gate 1 unreachable regardless of every other result. Resolvable for a fraction of a unit — step 0. |
| 4 | **I-024 quote-gap artifact (§8.3)** | Produces a large, robust, uncapturable in-sample number. **Design-fixed here**; D1/D2 are what make the design admissible. |
| 5 | **Survivorship via API enumeration and T7 (§8.1)** | Removes the loss cases. **Design-fixed here** by M1–M4; if M1 is impossible the family is REJECTED at Gate 0(5). |
| 6 | **KC-001 clause 5 fires by default (§12.1.3)** | Modal outcome. The family dies of logistics rather than evidence — correct under the rule, and the reason to spend less now. |
| 7 | **I-023 cost model cannot price this venue or its resolution risk** | Every net number the family produces is optimistic by a known sign and unknown magnitude. Blocking on any net-P&L claim. |
| 8 | **The already-arbitraged case** | Every Polymarket order and fill is on a public ledger — the most transparent order flow of any venue in Part III. A mechanically detectable lead-lag surviving on a public ledger requires an affirmative explanation, and "nobody has looked" is not available [cited — Red-Team §B.3.1]. §4 selects escape (c) and names its falsifier. |
| 9 | **Materiality (§11.2)** | Does not kill the research. Kills the investment case. |
| 10 | **Same-underlying pooling collapses effective N (§6.1)** | The family's construction is same-event pairs by design, so `ρ̄` will be high and `N_eff = n/(1+(n−1)ρ̄)` will collapse toward 1. Raw contract-day counts will overstate evidence badly. Required to be reported raw *and* effective, side by side. |

**Two things this seat will not claim as risk mitigation:** that the mechanism's coherence is evidence of its existence, and that the prior 71.5% figure supports anything. Neither is true.

---

## 16. SIZING, LIMITS, EXIT CRITERIA

| Element | Value |
|---|---|
| Intended initial allocation | **USD 50,000** (§11) |
| Per-contract-leg notional | **USD 5,000** |
| Maximum concurrent gross | **USD 100,000** (2× allocation; well inside Pod B's 4× gross limit, and deliberately conservative on a venue whose depth is unmeasured) |
| Participation cap | ≤ 5%/day of the forward leg's trailing-20-session volume; ≤ 15% of 20-day volume (Pod B standing limit) |
| Correlated cluster | Same-underlying pairs are **one position, not many** [cited — `agents/pm-digital-markets.md`]. Cluster cap 15% of pod capital applies to the underlying event, not the contract. |
| Position exit | Target +15¢ · stop −25% of entry · maximum holding 36 hours (§6.2) |
| **Family exit** | **F-001 fires** → KILL memo, written with the same care as a PROCEED memo (house rule 1). **KC-001 fires** → registry TERMINATED, automatic, not appealable to the CIO. **Trial budget exhausted** → this seat halts the family and reports it before Validation raises it. |
| Sizing on a Gate 1 pass | Would not exceed 25% of target allocation initially, ramped on realized performance (§4.5). Recorded for completeness; §9.4 makes it hypothetical. |

---

## 17. VERDICT — should this hypothesis get the compute?

*The task asks for this seat's judgment. It is within this seat's mandate ("decides alone: which hypotheses enter and their priority; when to abandon a line") and it is given plainly.*

> **VERDICT: FUND THE FALSIFIER, NOT THE FAMILY.**
> **Recommended Gate 0 intake verdict: ADMITTED-AS-EXPLORATORY.** Not ADMITTED.

### 17.1 What that means concretely

| Spend | Do not spend |
|---|---|
| **Step 0** — the T4 measurability query. Fraction of a Sonnet unit. Decides Gate 1 reachability before any ingest. | The full `DATA-SPEC` §7 13-step measurement programme — stratification table, effective-`N` computation, full T1–T7 screen across the venue's history, the 4-year span measurement. |
| **Steps 1–4** — archival enumeration, minimal ingest of the single densest pair-cluster, F-001, D2. **~2–3 Sonnet units total, from Pod B's remaining 4.** | Any ±50% parameter grid (§9.6). |
| The forward window, which accrues at zero compute cost under Option D. | Any Gate 1 apparatus for this family until step 0 returns yes **and** Seat 9 measures ≥4 years of continuous tradable span **and** H1–H4 land. |

### 17.2 The reasoning, in order

1. **The Gate 1 arithmetic is decided before the first run.** `MinBTL(31,250)` demands 17.06 years at the Gate 1 Sharpe floor, or a net out-of-sample Sharpe of 2.07 on four years — 4.14 before the R4(b) haircut. **This is not a forecast about the market. It is a consequence of the firm's own constants applied to the firm's own declared denominator.** Building the machinery that makes a positive result trustworthy, for a family whose positive result cannot be used, is the clearest case of activity mistaken for progress the firm currently has (Appendix B #9).
2. **The negative result is cheap and is a complete deliverable.** F-001 kills on direction, duration or magnitude in one run at `N = 1`. Null results are results (house rule 1) and this seat is scored on hypotheses correctly killed. A fast, well-reasoned kill of the Principal's own family is a successful deliverable and is written up as such, not apologised for.
3. **The materiality argument is dispositive on the investment question.** $50,000 is 0.5% of the book and roughly 12–25 bp of firm NAV at plausible outcomes. **The firm cannot pay for this family's governance out of this family's P&L.** Four Opus units — 100% of the firm's Opus spend to date [measured — I-025] — have gone to this one hypothesis, at 0.5% of capital. That ratio is the finding.
4. **What the firm should do with the freed compute, named specifically because "reallocate" without a destination is not a recommendation.**

> **Move Pod B's remaining ~2 Sonnet units to a crypto perpetual funding/basis family, and pre-register it this sprint.**
>
> The case is measured, not rhetorical:
> - **The data already exists in `book/pit.db`, ingested this session** [measured — DATA-INGEST-001 §2]: BTC/ETH/SOL spot daily 2020-01-01→2026-07-28 with **zero gaps**, and perpetual funding at 8h cadence over the same span with **zero gaps**. 6.5 years of continuous history against a §4.4 floor of 4.
> - **No venue-measurability question**, no survivorship question, no archival-enumeration question, no missing loader, no unaccepted data spec.
> - **`N_inherited` = 0, honestly.** No prior search exists to charge it for. `MinBTL(N)` at a small registered `N` is a bar a real strategy can clear — 2.48 years at `N = 10`, SR 1.0 [measured].
> - Charter §3.2 calls it **"the best data surface the firm has"**; §3.5 names crypto funding and basis first among the four areas where the firm's data is genuinely adequate.
> - It answers Red-Team §A.4's finding — that the firm has directed 100% of its scarcest resource at the thinnest data surface in Part III and 0% at the two the Charter describes in superlatives — **by doing the work rather than by writing a justification for not doing it.**
> - Pod B's own seat definition already names the structural fact that family must clear: ~11%/yr of funding drag against a structurally long perp, positive over 92% of a recent quarter [cited]. That is a hypothesis with a mechanism, a falsifier, and data on disk today.

### 17.3 What this verdict is not

**It is not a recommendation to kill the forward-lag family now.** The mechanism is coherent, the falsifier is cheap, the forward window costs nothing to accrue, and KC-001 will resolve it on 2026-10-31 one way or the other. **It is a recommendation to stop treating it as the firm's flagship** and to size the compute to the honest allocation — which is 0.5% of the book.

**It does not soften KC-001 by one word.** If the F-001 path does not produce 30 tradable events by 2026-10-31, clause 5 fires and the family dies by silence. This seat's expectation is that it will (§12.1.3), and the verdict above is the reason to be honest about that now rather than to spend three more Sonnet units discovering it in October.

---

## 18. CONDITIONS PRECEDENT TO SEALING

*Nothing may be added to this document after sealing (D-007, P7). These must therefore be resolved — or explicitly accepted as unresolved by Validation at Gate 0 intake — before Pod B calls `open_hypothesis`.*

| # | Condition | Owner | Blocking? |
|---|---|---|---|
| **C1** | **H1–H4 (§9.5): the harness carries `n_inherited` and it enters the P2 binding field set.** If sealed without it, the declared denominator is decorative and the document is worse than silence. | Head of Data & Infrastructure; **acceptance test authored by Validation first** (I-021) | **BLOCKING** |
| **C2** | Validation's Gate 0 intake verdict on this document. | Quant Validation | **BLOCKING** — sealing is what fixes `C`, and it follows intake |
| **C3** | Pod B's written acceptance of KC-001 as sponsor, before any capital paper or real. | PM Pod B / the Principal | **BLOCKING** (KC-001 preamble) |
| **C4** | The seal and the `HoldoutVault.seal()` occur in the **same session, same UTC day**; passphrase supplied by the Principal and written nowhere. | PM Pod B + the Principal | **BLOCKING** (P7) |
| **C5** | Validation's acceptance of `DATA-SPEC-polymarket-usable-history.md`, with the amendments this document depends on: **T3 → `S_max = 0.25·G`** (Red-Team §B.2.2), **pair-day as the unit**, **underlying-event as a fifth stratification axis**, **spreads screened in cents not bps**. | Quant Validation | Blocking on **measurement**, not on sealing |
| **C6** | **I-023** — the `POLYMARKET` cost preset expresses spread as a price-point quantity, and `CostModel` gains a resolution-risk field, Principal-approved. | Head of Data & Infrastructure → Validation → the Principal | Blocking on any **net-P&L claim**, including the paper book |
| **C7** | **I-022** — the trial-count criterion stops returning a literal `True`. | Head of Data & Infrastructure | Blocking on **Gate 1**, not on sealing |
| **C8** | Step 0 (T4 measurability) answered in writing by **2026-08-11**. | Head of Data & Infrastructure | Family remains exploratory-only until answered (KC-001 condition precedent) |

**If C1 cannot be met before sealing**, this seat's recommendation is: **seal anyway, and record on the face of the pre-registration that `N_inherited` is declared-but-unenforced**, because the alternative — waiting — leaves `C` unfixed while the Principal's directed floor sits in a draft. But the Validation Report must then read `Pre-registration integrity: declared N_inherited = 31,250, NOT enforced by the registry` on its face, and Gate 1 is unreachable until H1–H4 land. **That is a judgment call and it is escalated, not resolved silently** (house rule 7).

---

## 19. THE SEAL BLOCK — exact binding field set for `TrialRegistry.open_hypothesis`

*P2 names the binding set exhaustively. These strings are what get hashed into `prereg_sha256` and shadow-copied into the `hypothesis_sealed` event. **Pod B executes this. This seat does not.** `n_inherited` is included per C1 and requires H1.*

```
family                            = "forward-lag-001"

statement                         = "On Polymarket, when a high-volume contract reprices by >=20 price
                                     points over a trailing 2h window, economically-paired
                                     later-resolving contracts on the same underlying event reprice
                                     with a directionally consistent delay whose peak lies strictly
                                     between 0 and 24 hours and whose median fillable capture exceeds
                                     2.0c on a 50c-equivalent contract, net of the full Charter 4.6
                                     cost stack at 1x modelled costs."

mechanism                         = "The counterparty is a Polymarket participant on the later-resolving
                                     leg who has not updated for news already impounded in the nearer
                                     leg: (1) directional retail expressing a weeks-horizon view on the
                                     outcome, whose reservation price is a subjective probability and
                                     not a relative-value spread, accepting adverse selection as the
                                     price of a clean binary expression; (2) passive resting liquidity
                                     stale between refreshes on a thin venue, accepting the ordinary
                                     adverse-selection cost of resting size because continuous
                                     management of a low-notional contract costs more; (3) participants
                                     allocating attention by contract rather than by event. Persistence
                                     rests on participation segmentation (escape (c), REDTEAM-001
                                     B.3.2) - event-market flow is structurally not relative-value flow
                                     - NOT on regulatory or settlement friction, both of which carry
                                     decay dates. Falsifier of the persistence claim: on-chain flow
                                     composition showing a material share of resting liquidity on
                                     later-dated legs posted by addresses that also trade the near leg
                                     within the same hour."

falsifier                         = "F-001. Let rho(k) be the cross-correlation of hourly log-odds
                                     returns between lead leg L and forward leg F, k in [-36,+36]
                                     hours, computed ONLY on bars where BOTH legs carried a two-sided
                                     quote in that bar and the preceding bar (non-qualifying bars
                                     DROPPED, never forward-filled); k* = argmax_k rho(k). The
                                     hypothesis is FALSIFIED if ANY of: (i) DIRECTION - k* <= 0;
                                     (ii) ARTIFACT - k* >= 24 hours, OR k* on the paired-quotable
                                     subsample differs by more than 50% from k* on the all-bars
                                     forward-filled sample; (iii) MAGNITUDE - median signed fillable
                                     capture on F, from the executable price at t0+2h to the executable
                                     price at t0+k* in the direction of sign(delta p_L), is < 2.0c on a
                                     50c-equivalent contract. Any single leg firing is sufficient.
                                     F-001 is a descriptive statistic selecting nothing from a menu and
                                     is registered as N=1. It is distinct from and additional to the
                                     kill condition KC-001."

universe                          = "Polymarket only, both legs. Unit of observation is the PAIR-DAY:
                                     one calendar day of one ordered pair (L,F) sharing one underlying
                                     event under DATA-SPEC section 3 mapping, with
                                     resolution_date(F) > resolution_date(L), both listed and live at
                                     t0. L must satisfy T5,T6,T7; F must satisfy all of T1-T7; both
                                     required for a pair-day to be TRADABLE. P_notional = USD 5,000 per
                                     leg, fixing T1 F = 20 x P_notional = USD 100,000 trailing-20-session
                                     median daily notional. G = 4.0c per round trip on a 50c-equivalent
                                     contract, fixing T3 S_max = 0.25 x G = 1.0c half-spread (quoted
                                     full spread <= 2.0c). All spread screens evaluated in price points
                                     (cents), NEVER in bps of notional (I-023(a)). Stratified on
                                     DATA-SPEC section 3 axes (i)-(iv) PLUS underlying-event identity as
                                     a fifth axis. Universe enumerated from the archival on-chain
                                     condition registry, NOT from a live API listing; the API-listing
                                     survivorship rate is measured and reported. All four cells of
                                     {UP,DOWN} x {EARLIER,LATER} are traded - the prior work's
                                     UP+EARLIER exclusion is NOT inherited - with per-cell expectancy,
                                     event count and slugging ratio reported separately."

horizon                           = "Event-driven, no periodic rebalance. Signal: L mid move >= 20c over
                                     a trailing 2h window. Entry: on F at the first executable price
                                     2 hours after t0, admitted only if F carried a two-sided quote
                                     within S_max AT the entry instant. Exit: first of target +15c,
                                     stop -25% of entry price, or maximum holding period 36 hours. Bars
                                     hourly, UTC, both legs on a common grid via pit_price_panel (A4);
                                     bars lacking a two-sided quote on either leg are DROPPED, never
                                     forward-filled. Signals whose entry instant falls inside a
                                     forward-leg quote gap exceeding 6 consecutive hours are excluded
                                     from the primary result and reported as a separate subperiod with
                                     its own expectancy and event count, never averaged in. Any variant
                                     introducing an off-venue reference leg must state that leg's
                                     tradable session in UTC, drop out-of-session bars rather than
                                     forward-fill them, exclude signals whose first executable reference
                                     instant falls more than one session boundary later (reporting them
                                     as a separate subperiod), and screen the reference leg on the same
                                     tradability standard as the Polymarket leg. periods_per_year = 365."

success_criteria                  = "Tiered. (1) F-001 survival: no leg of the falsifier fires.
                                     (2) KC-001 survival at 2026-10-31: net expectancy per round trip
                                     > 0 AND >= 30 tradable signal events. (3) Gate 1: every criterion
                                     of Charter 4.4 unmodified, computed by castellan.evaluate_gate1
                                     with N = n_inherited + logged trials, backtest_years passed
                                     explicitly as true calendar span. No threshold relaxation is
                                     sought. Required diagnostics in every artifact regardless of
                                     verdict: D1 (k* quotable vs forward-filled), D2 (k* regressed on
                                     forward-leg median inter-quote interval; slope near 1 is reported
                                     as an artifact finding), per-cell decomposition, API-listing
                                     survivorship rate, T7 removal rate, raw AND effective contract-day
                                     counts side by side, hit rate paired with slugging ratio, gross and
                                     net with the breakeven cost in cents. Recorded at pre-registration:
                                     MinBTL(31250) = 17.06 years at net SR 1.0, so the Charter 4.4
                                     length criterion requires net out-of-sample SR >= 2.07 on 4 years
                                     (>= 4.14 pre-haircut). The family is expected to fail Gate 1 on
                                     evidentiary length, and a KILL memo is a complete deliverable."

trial_budget                      = 40

n_inherited                       = 31250        # requires H1; see section 9.5 and condition C1

predecessor_family                = None

holdout_classification            = "FORWARD"

forward_window_start              = "2026-07-28"

forward_window_min_length         = 12.0         # UNITS: MONTHS (Charter 4.4 holdout floor)

forward_kill_condition            = "KC-001 (REDTEAM-001 B.5, signed by the Principal as written,
                                     silence-kill included). Observation date 2026-10-31, ABSOLUTE -
                                     it does not move with the sprint calendar, the ingest schedule, or
                                     the harness. On that date Validation computes, from registry.db and
                                     pit.db ALONE, on the frozen pre-registration, over the forward
                                     window: (i) realized net expectancy per round-trip trade =
                                     (sum realized P&L)/(count of round trips), in price points on the
                                     [0,1] scale, after the full Charter 4.6 cost stack at 1x modelled
                                     costs using the POLYMARKET preset as amended per I-023; and (ii)
                                     the count of tradable signal events generated by the frozen
                                     specification under its own pre-registered screen. The family is
                                     KILLED - registry TERMINATED, no further trials, no Gate 1
                                     submission ever - if EITHER (a) net expectancy <= 0 OR (b) fewer
                                     than 30 tradable signal events occurred in the window. Clause (b)
                                     kills on insufficient signal and must not be waived as a
                                     technicality. BINDING ANTI-REINTERPRETATION CLAUSES: (1) No
                                     re-parameterisation - expectancy is computed on the sealed
                                     specification, not a tuned variant, not a subset, not the version
                                     we would have run. (2) No post-C exclusions - any regime filter,
                                     date exclusion, contract exclusion or universe restriction not
                                     present in the sealed pre-registration is inadmissible in this
                                     computation. (3) No restatement as continuation - a hypothesis
                                     restated after 2026-10-31 is a NEW family opened with n_inherited
                                     >= the killed family's final n_trials plus its own n_inherited, and
                                     inherits neither schedule nor allocation nor narrative. (4) Kill is
                                     automatic on the date, requires no meeting, no vote and no CIO
                                     concurrence, and IS NOT APPEALABLE TO THE CIO; only the Principal
                                     may reverse it, in writing, logged in DECISION_RECORD.md as an
                                     Appendix-B-#4 override with its reason on the face of the record
                                     and reported in the next Monthly Letter. (5) SILENCE IS A KILL - if
                                     the computation is not performed on 2026-10-31 for ANY reason,
                                     including that ingest never happened or the harness was not ready,
                                     the family is killed by default. Condition precedent, separately
                                     binding: the T4 measurability query is answered in writing by
                                     2026-08-11; if unanswered the family is ADMITTED-AS-EXPLORATORY
                                     only until it is."

model_prior_provenance            = "R4(a). Per I-009 the firm does not know its seats' training
                                     cutoffs and the authoritative reference does not publish them;
                                     every cutoff below is [assumed] unknown and that absence is itself
                                     the finding. Hypothesis statement and mechanism: originated by the
                                     Principal (D-004), human, cutoff n/a and advancing continuously
                                     (channel K5, documented where K4 is only hypothesised - Ruling 002
                                     3.3(3)); ratified by Director of Research (Opus, cutoff unknown).
                                     Parameter values (20c/2h/15c/25%/36h): originated in the
                                     Principal's prior unaudited work, carried forward UNCHANGED and
                                     declared per I-002; the family is charged the full price of that
                                     search via n_inherited. Regime-cell decision (all four cells
                                     traded, UP+EARLIER exclusion NOT inherited): Director of Research
                                     (Opus, cutoff unknown). Falsifier F-001: Director of Research
                                     (Opus), adopting the shape of Devil's Advocate REDTEAM-001 B.4
                                     (Opus) with three declared modifications - transposition from
                                     cross-venue to intra-venue, hourly bars over +/-36h rather than
                                     5-minute over +/-60min, and correction of the magnitude threshold's
                                     stated basis (2.0c is 2x the POLYMARKET round-trip spread of 1.0c
                                     at 50c, not equal to it; the threshold is retained, its label
                                     corrected, and the correction is strictly stricter).
                                     Clock-alignment design and the D1/D2 discriminators: Devil's
                                     Advocate (cross-venue form, I-024) and Director of Research
                                     (intra-venue transposition and both discriminators), Opus.
                                     n_inherited construction: requirement from Devil's Advocate
                                     REDTEAM-001 B.1.1 (Opus); 5^5 = 3125 grid component from I-002
                                     [cited]; regime-candidate factor of 10 from the CIO [INFERRED, not
                                     measured and not cited]; floor fixed by the Principal by direction.
                                     The any-subset reading (2^10 x 3125 ~ 3.2M) was considered and
                                     rejected as overstating realistic human search. Revision DOWNWARD
                                     requires reconstructed evidence of the actual candidates considered
                                     - a parameter log or run history, NOT a recollection - and is
                                     itself logged as a Decision Record entry with a successor family;
                                     revision upward requires only evidence that more was tried. T1/T3
                                     numeric inputs (P_notional, G): Director of Research (Opus) on
                                     Head of Data & Infrastructure's formulas (Sonnet). Holdout regime:
                                     Validation Rulings 001 and 002 (Opus) and the Principal (D-006
                                     Option D, D-007 C = seal date). KC-001: Devil's Advocate (Opus),
                                     signed by the Principal as written including the silence clause."

published_signal_haircut_applied  = 0.50
```

**Vault seal, same session, same UTC day:**

```
HoldoutVault(vault_dir="book/vaults/forward-lag-001-polymarket",
             registry=registry, name="forward-lag-001-polymarket",
             family="forward-lag-001", store=pit_store).seal(
    source="polymarket",
    dataset_id=<the archival on-chain enumeration identifier>,
    instrument_identity=<condition IDs / outcome token IDs, exhaustive>,
    query_semantics=<the exact query, per Ruling 001 section 3.4>,
    cutoff=<C = this UTC calendar day>,
    schema_fingerprint=<field names and dtypes>,
    passphrase=<the Principal's, never written to repo, Oracle, or any file>,
    holdout_end_rule="open-ended, forward from C",
    resolution_source=<per-stratum resolution source class>,
    sealed_by="pm-digital-markets")
```

---

## 20. WHAT WOULD CHANGE THIS SEAT'S MIND

| # | On what | What would change it |
|---:|---|---|
| 1 | **The verdict at §17** (fund the falsifier, not the family) | Step 0 returning **yes** on retrievable historical order-book depth, **and** a measured Polymarket tradable span ≥ 4 years under the accepted spec at `P_notional = $5,000` with ≥60% continuity and no 90-day gap. Both, not either. That combination makes Gate 1 reachable in principle and the family worth its apparatus. |
| 2 | **`N_inherited` = 31,250** | Reconstructed evidence of the actual candidates considered — a parameter log, a run history, a dated record. Not a recollection. **And note it barely matters:** at 3,125 the expected max is 3.57·σ_SR and MinBTL is 12.72 years at SR 1.0. Both readings are fatal (§9.4). |
| 3 | **The falsifier F-001's magnitude leg at 2.0¢** | A corrected `POLYMARKET` preset expressing spread in price points (I-023(a)), from which the true round-trip cost at the contract prices this family actually trades can be computed. The threshold should then be that number × 2, whatever it turns out to be. |
| 4 | **The choice of persistence escape (c)** | Measured on-chain flow composition showing relative-value participants resting size on later-dated legs. That kills (c) and, with it, the only escape that supports a durable edge. |
| 5 | **The intra-venue framing** | Evidence that Pod B's inherited family is in fact cross-venue. This seat read it as intra-venue from `agents/pm-digital-markets.md` and I-002's parameter list; if that reading is wrong, §5, §6 and §8.3(A) need restating and this document must not be sealed until they are. |
| 6 | **The recommendation to move compute to crypto funding/basis** | A written statement of why the thinnest data surface in Part III is the correct first target, which Charter §3.5 requires and which does not currently exist [cited — Red-Team §A.4, §B.7 item 7]. If the reason is good, the recommendation dissolves. |
| 7 | **Anything about the prior 71.5% figure** | Nothing. It carries zero evidentiary weight under I-002 and it is the wrong statistic regardless — a hit rate unpaired with a slugging ratio means nothing (Charter §5.4), and **nobody, including this firm, currently knows the sign of this strategy's expectancy.** |

---

*Director of Research · Castellan Capital · 2026-07-28*
*This document is complete and sealable. It is not sealed. Sealing fixes `C` (D-007) and is Pod B's act, after Validation's Gate 0 intake. Nothing may be added after.*
