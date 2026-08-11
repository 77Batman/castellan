# Castellan Capital — Validation Protocol & Gates

*Extracted from `FUND_CHARTER.md` Part IV. Owned by the Head of Quantitative Validation. Not relaxable except by the Principal, in writing, in advance. Data walls: `CONSTRAINTS.md`. Document formats: `TEMPLATES.md`.*

## PART IV — THE VALIDATION PROTOCOL

This is the part of the Charter that makes "confirm an edge" mean something. It is owned by the Head of Quantitative Validation and may not be relaxed by anyone except the Principal, in writing, in advance.

### 4.1 The governing fact

If N independent strategy variants are tested on data with **zero true edge**, the expected *best* in-sample Sharpe is [cited — Bailey, Borwein, López de Prado & Zhu, 2014]:

```
E[max SR_N] ≈ σ_SR · [ (1−γ)·Φ⁻¹(1 − 1/N) + γ·Φ⁻¹(1 − 1/(N·e)) ]     γ = 0.5772 (Euler–Mascheroni)
```

where **σ_SR is the cross-sectional standard deviation of Sharpe ratios across the N trials** — precisely why §4.2 and §7.3 require it to be logged and reported. Loose asymptotic upper bound: `√(2·ln N)`. In units of σ_SR:

| Trials N | Expected best Sharpe on pure noise |
|---|---|
| 10 | 1.57 |
| 45 | 2.24 |
| 100 | 2.53 |
| 1,000 | 3.26 |
| 10,000 | 3.86 |

**A backtest Sharpe of 2.0 discovered after 1,000 variants is indistinguishable from noise.** Roughly 20 iterations is typically enough to discover a false strategy at conventional significance [cited — López de Prado]. This is why the Trial Registry is not bureaucracy — it is the denominator without which every other number in this section is uninterpretable.

### 4.2 Firm constants — hard-coded, not negotiable mid-evaluation

```
T_STAT_HURDLE            = 3.0     # multiple-testing adjusted; NOT 2.0
DSR_MIN                  = 0.95    # Deflated Sharpe Ratio
PBO_MAX_PAPER            = 0.10    # Probability of Backtest Overfitting, Gate 1
PBO_MAX_REAL             = 0.05    # Gate 2
EMBARGO_FRACTION         = 0.01    # 1% of bars, purged CV
CSCV_PARTITIONS_S        = 16
WFE_MIN                  = 0.50    # Walk-Forward Efficiency = SR_oos / SR_is
HOLDOUT_FRACTION         = 0.25    # most recent 25%, locked, single use
ADV_PARTICIPATION_MAX    = 0.05
IMPACT_EXPONENT          = 0.5     # square-root law
IMPACT_PREFACTOR_Y       = 1.0     # conservative until own fills calibrate it
PUBLISHED_SIGNAL_HAIRCUT = 0.50    # any edge derived from published research
CORR_MAX_TO_LIVE_BOOK    = 0.30
```

### 4.3 Gate 0 — Admissibility

Binary. Evaluated by Validation at intake, before any compute is spent. **A single failure is fatal at this stage, which is the cheapest stage to fail at.**

1. A written hypothesis stating the **economic or structural mechanism** — why this effect should exist, in terms of who is on the other side and why they accept the loss. "The data says so" is not a mechanism.
2. A **pre-registered falsifier**: the specific observable that means the hypothesis is wrong.
3. Universe, horizon, rebalance frequency, and success criteria stated **before** the first run.
4. The required data **exists** within Part III. No inadmissible dependencies (see `CONSTRAINTS.md`).
5. Survivorship and look-ahead exposure identified and a mitigation named.
6. Trial counter opened and instrumented — the family exists in `book/registry.db` and every backtest routes through `harness` `run_backtest`; numbers produced outside the engine are inadmissible. *(A2, v1.1.)*
7. Holdout period defined and locked.

Output: an **Intake Verdict** — ADMITTED / REJECTED (with reason) / ADMITTED-AS-EXPLORATORY (may be researched but is pre-declared ineligible for Gate 1, used for known-unvalidatable but interesting lines).

### 4.4 Gate 1 — Paper capital

Every criterion must pass. One FAIL fails the Gate.

| Criterion | Threshold |
|---|---|
| Net Sharpe, out-of-sample, after full cost stack | ≥ 1.0 |
| t-statistic on net returns | ≥ 3.0 |
| Deflated Sharpe Ratio (using logged N and cross-sectional trial variance) | ≥ 0.95 |
| Probability of Backtest Overfitting (CSCV, S = 16) | ≤ 0.10 |
| Backtest length | ≥ MinBTL(N) **and** ≥ 4 years **and** ≥ 1 full regime cycle |
| Holdout window | most recent 25%, ≥ 12 months, opened once |
| Walk-Forward Efficiency across ≥ 10 windows | ≥ 0.50 |
| Purged k-fold with 1% embargo applied | required |
| Subperiod positivity (independent blocks) | ≥ 60% net-positive |
| P&L concentration | no single day > 10%, no single month > 25% of total |
| Parameter surface | plateau not spike; ≥ 60% of the ±50% grid net-profitable |
| Cost robustness | retains t ≥ 3.0 at **2× modelled costs** |
| Capacity | ≥ 10× the intended initial allocation at target net Sharpe |
| Correlation to any live pod strategy | \|ρ\| ≤ 0.30 |
| Red-Team Memo | present, with a binding named kill condition accepted by the sponsor |

**Report the breakeven cost** — the round-trip cost in basis points at which t falls below 3.0 — on every submission. It is more informative than the net Sharpe itself.

### 4.5 Gate 2 — Real capital · PRINCIPAL ONLY

Everything in Gate 1, **tightened**, plus a live paper record. The firm may **recommend**; only the Principal may **authorize**.

| Criterion | Threshold |
|---|---|
| Paper trading period | ≥ 3 months, or ≥ MinTRL observations at the claimed Sharpe, whichever is longer |
| Realized paper Sharpe vs. backtest net Sharpe | ≥ 50% |
| Realized modelled costs vs. predicted | within 1.5×, with no systematic underestimate |
| PBO recomputed with final N | ≤ 0.05 |
| DSR recomputed with final N | ≥ 0.95 |
| Independent re-implementation | a second seat rebuilds from the spec and reproduces within tolerance |
| Kill switch | pre-registered drawdown and Sharpe-decay triggers for automatic de-allocation |
| Initial sizing | ≤ 25% of target allocation, ramped on realized performance |

### 4.6 Standing methodological requirements

- **Prices are consumed only through the harness PIT store** (`pit_adjusted_close`); vendor pre-adjusted series are inadmissible inputs. *(A4, v1.1.)*
- **Every field carries two timestamps** — `event_time` (when it became true) and `knowledge_time` (when it was first observable). All queries filter on `knowledge_time ≤ decision_time`. Never on `event_time`.
- **Never fill at the same bar that generated the signal.** Minimum one-bar lag; for daily equity data, execute at next open or VWAP. A documented one-day reversal strategy's Sharpe collapsed from 1.41 to 0.26 on this change alone [cited — DB *Seven Sins*].
- **Standard cost stack, applied per side, from the shared library:**
  `commission + 0.5·spread·capture_factor + Y·σ_daily·√(Q/ADV) + delay cost + borrow/funding carry`
- **Any edge derived from published research is haircut 50%** before it is considered, on the documented base rate that anomalies lose ~26% out-of-sample and ~58% post-publication [cited — McLean & Pontiff 2016, *Journal of Finance*].
- **Expect 88% erosion as the base case.** The average documented anomaly goes from 66 bp/month gross in-sample to roughly 8 bp/month net, post-publication, post-2005 [cited — Chen & Velikov, *JFQA*]. A strategy whose thesis requires that this time is different must say so explicitly.
- **Prefer the plateau centroid to the argmax.** Selecting the peak of a parameter surface *is* the overfitting operation.

---

---

### 4.7 Standing doctrines — Principal-ruled, binding on every family

*Recorded here rather than only in the decision record or Standing Order 001. The order **expires
with the sprint** by its own §7; a doctrine filed only there is a doctrine the firm loses on
schedule. Both entries below were ruled by the Principal in Sprint 2 and bind prospectively.*

---

#### 4.7.1 · Inheritance is computed, never re-declared

**Ruled 2026-08-05 (S2-D-013), standing for all kill conditions.**

> One counting path, owned by the registry's transitive summation, with
> `InheritedCountDoubleCountError` enforcing what prose previously asserted.

A successor family declares `predecessor_family` and **its own new search only**. It does **not**
re-declare the predecessor's count in `n_inherited`: `family_stats` already sums the chain
transitively across `predecessor_chain`, so re-declaring double-counts, which the harness refuses.

**The rule this replaces was written four separate times** — PREREG-002 §7.2, KC-002 clause 3,
§19.3's successor, and `VALIDATION-RULING-004` ML-17, which copied the error citing PREREG-002 as
source (I-055). **The firm's requirement that a restatement cannot escape its predecessor's trial
count is delivered better by the harness than by any of the four sentences that tried to state
it.**

**Test for any new pre-registration:** if a clause tells a sponsor to *declare* a quantity the
registry already computes, it is this defect.

---

#### 4.7.2 · A registration act, not a prose act

**Ruled 2026-08-06 (S2-D-029), standing doctrine for every two-stage or contingent construction.**

> **A control exists where the harness reads it, and nowhere else.**

A pre-registration that *describes* a staged budget, a contingent unlock, or any conditional
limit **has not created one**. The control exists only if the value the harness reads is the
staged value. **PREREG-002 is the worked example (I-105):** its two-stage budget is enforced only
if the document registers Stage 1 as its sealed `trial_budget = 47`. Sealed at the flat 79, the
harness enforces 79, **no predicate is ever evaluated**, and the document's own §10.5.2 describes
a gate that does not exist.

**The Principal's disposition, which generalizes:** such language **survives only as the
description of a registered unlock event**, or it is **struck from the document before sealing.**

**Why it is not a filing convention.** A frozen document describing a nonexistent gate is
**I-046's costume on the research side** — an asserted control that is not there — and **P7 makes
it permanent.** The repair is always pre-seal and never after.

**Test for any new pre-registration:** for every limit the document claims, name the field the
harness reads to enforce it. **If there is no such field, there is no limit.**

---

*Both doctrines share one shape, and it is the sprint's most reusable finding: **a control that
is asserted rather than computed is not a control.** I-022 (a criterion that annotated instead of
failing), I-053 (an escalation rule the registry refuses), I-105 (a stage the harness never
reads), and 4.7.1's four-times-written inheritance rule are the same defect wearing four costumes.*

---

#### 4.7.3 · Put the control where the machine reads, not where the reader infers

**Named as doctrine by the Principal, 2026-08-11 (S3-D-009), on a four-domain convergence.**

The firm has made the same choice in four unrelated places, and the convergence is now its most
reliable predictor of which design will hold:

| Domain | Rejected | Adopted |
|---|---|---|
| Numbers | narrated | **computed** — A2, every figure through `run_backtest` |
| Limits | described | **registered** — I-105, §4.7.2 |
| Trading | instructed | **credentialed** — Charter A5, paper as a property of credentials |
| Permissions | classified | **enumerated** — `disableAutoMode`, *"classifier nondeterminism in the control plane loses to enumerated rules"* |

**One principle: a control exists where something deterministic reads it, and nowhere else.**

**I-095 is this doctrine's negative print** — the doctrine stated correctly and the implementation
landed **one layer off.** Vault and registry write denies were aimed at the `Write`/`Edit` tool
path, which nothing in this firm has ever used, while the `python3`/`sqlite3` path that every real
write uses stayed ungoverned. **The rule was enumerated, deterministic, correctly configured, and
pointed at nobody.**

**The test that separates the two:** not *"is this control deterministic?"* but **"name the path a
real actor would take, and show this control on it."** A control that is deterministic about the
wrong path is indistinguishable, from the record, from one that works.

**Consequence for remedies, which is where I-095 was ultimately fixed:** when the control cannot be
aimed at the real path from outside — `Bash(python3:*)` is how the harness legitimately works, and
*"python3 except when it touches the registry"* is **classification wearing enumeration's clothes**
— **the control moves down a layer into the thing being protected.** The registry and vault defend
themselves in code, read-only by default, write authority granted per-invocation and visible in the
record.

*The casebook holds §4.7.3 and I-095 together: a doctrine and its own near-miss are worth more
paired than apart.*

---

#### 4.7.4 · Two constructions binding on every future harness control

**Promoted to standing design doctrine by the Principal, 2026-08-12 (S3-D-013), from
`VALIDATION-SPEC-004`. Placed here under §7.3's promotion path rather than left in the order, which
expires.**

**(i) The authority record is written by the act it authorizes.**

> **"No ordering exists in which a write precedes the record of its authority."**

The grant row in `write_grants` **is the first write performed under its own grant.** Not written
before the work as an intention, not appended after as a log — **the record of authority and the
first exercise of it are the same operation.** A control whose audit trail is a separate write can
be defeated by the write that does not happen; this one cannot, because skipping the record means
skipping the authority.

**Test for a proposed control:** if the audit entry and the authorized act can fail independently,
the audit is a hope. **Make them the same act or accept that you have a log, not a control.**

**(ii) A control reports whether or not it fired.**

> **"A control visible only when it fires is one nobody can confirm is running."**

`evaluate_gate1` prints orphan count, chain integrity and chain head **on every invocation,
including when all three are zero.** A control that is silent when clean is indistinguishable —
from the record, and from every downstream reader — **from a control that has been switched off, has
crashed, or was never wired in.** Silence is not evidence of health; it is absence of evidence, and
this firm has spent two sprints learning the difference.

**Test for a proposed control:** **name the output a reader sees on a clean run.** If there is none,
the control cannot be confirmed to exist, and its clean runs and its non-runs are the same
observation.

*Both are §4.7.3's principle applied to the control's own reporting surface: **put the evidence
where the machine writes it, not where the reader would have to infer it.***
