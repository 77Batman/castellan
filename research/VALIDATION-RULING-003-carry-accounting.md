# VALIDATION RULING 003 — carry accounting: the I-034 repair specification

**Seat:** Head of Quantitative Validation · reports to the Principal
**Date:** 2026-07-29
**Instrument:** binding specification + pre-authored acceptance tests (Charter §4.6, Seat 9
standing rule, Amendments A1/A2/A4)
**Funded by:** the Director of Research's final Sprint 1 Opus unit, per D-012. Recorded because
the arithmetic of the ceiling is part of the record.
**Blocks:** `research/PREREG-002-crypto-funding-basis.md` condition precedent **C1**; I-034.

---

## 0. Provenance — what was read, what was run, what this seat did not do

**Read in full:** `harness/castellan/costs.py`, `harness/castellan/engine.py`,
`harness/castellan/grid.py`; `logs/ISSUE_LOG.md` I-023, I-034, I-035, I-036;
`logs/DECISION_RECORD.md` D-011; `research/DATA-INGEST-001-crypto-etf.md`;
`research/PREREG-002-crypto-funding-basis.md` §5, §12, §13; `research/VALIDATION-GATE0-001-forward-lag.md`
§1; `FUND_CHARTER.md` §4.3–§4.6, Seats 7/9/10.
**Read in part:** `harness/castellan/data.py` (`PITStore.asof`, `pit_adjusted_close`,
`pit_price_panel`), `harness/castellan/gates.py` (`evaluate_gate1` signature; the cost-robustness
and breakeven block, lines 456–480), `harness/castellan/book.py` (cost surface).

**Run:** the harness suite — **96 passed, 0 failed** [measured]. Read-only queries against
`book/pit.db` (opened `mode=ro`) and arithmetic on `castellan.costs` in a throwaway interpreter.

**Not done, per the constraints:** no code modified, no data fetched, nothing sealed, nothing
committed, no trial logged, `book/registry.db` untouched. Every measurement below is either a
read-only query or a pure function of `costs.py`.

---

## 1. VERDICT

> **The defect is confirmed and is worse than I-034 records.**
>
> **The Principal's direction SURVIVES on its central claim — funding is a signed asset cash
> flow and belongs in engine P&L accrual, not in the cost library — and it survives on its
> stress-semantics split. I adopt both.**
>
> **It is INCOMPLETE in three respects, each of which I amend on measured grounds:**
>
> **(A1) Zeroing is not enough — the field must be removed.** PREREG-002 §12.8 already plans to
> set `funding_bps_annual = 0.0`. A field that must be manually zeroed to avoid a sign-inverted
> double count is a defect waiting on a lapse of discipline. `CostModel` gets no funding field
> and `CRYPTO_PERP_TAKER` gets no funding term.
>
> **(A2) "From the realized funding series" needs an alignment rule and no cadence constant.**
> The 8-hour cadence asserted in `DATA-INGEST-001`'s data dictionary is **measured false**: SOL
> settles at 2h and 4h intervals during stress, up to **12 prints in one day**, on **11 of 2,145
> days**. Any implementation that annualizes by a fixed prints-per-year constant is wrong, and it
> is wrong precisely on the days that matter.
>
> **(A3) Sign inversion is not a conservative operator and cannot stand as "the stress case."**
> [measured] On SOL, inverting realized funding makes the worst-20-day mean **4.5× better**
> (−0.02192 → −0.00487), deleting the 2022-11-10 event that is the sample's only realization of
> the fat left tail Charter Seat 7 warns about. Inversion is required; it is not sufficient. The
> reported scalar is the **breakeven adverse carry shift in bps/yr**, not a multiplier.
>
> **Liquidation and venue insolvency do NOT become a chargeable `CostModel` field.** Ruled in
> §3.5, against the shape of the request in I-034(3) and I-023(b).
>
> **§4.4's cost-robustness criterion does not bind a carry family under any correct
> implementation. That is a Charter-amendment question, it is the Principal's, and I name it
> without resolving it (§5).**
>
> **Nineteen acceptance tests, authored below, before implementation. Seat 9 implements against
> them and does not amend them.**

---

## 2. THE DEFECT, INDEPENDENTLY MEASURED

I re-derived every number rather than accept I-034's. All confirm.

| Quantity | Value | Provenance |
|---|---:|---|
| `CRYPTO_PERP_TAKER.carry_per_bar(1.0, 1.0)` | `0.0006` / bar | [measured] |
| — annualized at `periods_per_year=365` | **−21.90 %/yr charged** | [measured] |
| `carry_per_bar(0.0, 1.0)` — naked short perp | **−10.95 %/yr charged** | [measured] |
| `scaled(2.0).funding_bps_annual` | `2190.0` → **−43.80 %/yr** | [measured] |
| Realized BTC funding, 2020-01-01 → 2026-07-28, 7,203 prints | **+11.86 %/yr** | [measured] |
| Realized ETH funding, 7,203 prints | **+14.07 %/yr** | [measured] |
| Realized SOL funding, 6,508 prints | **+0.10 %/yr** | [measured] |

Two things follow that I-034 does not say.

**2.1 A sign-corrected scalar is still inadmissible, and on SOL it manufactures edge.** The
obvious minimal repair — flip the sign, halve the base, keep the scalar — would credit a
short-SOL-perp position with **+10.95 %/yr** against a realized **+0.10 %/yr**: a **107×
overstatement**, erring *optimistically*, on the asset PREREG-002 puts secondary precisely
because it is the marginal one. The scalar's error is not conservative in either direction; it
is whatever the asset happens to make it. **This is the argument that forecloses the cheap fix,
and it is why the realized series is mandatory rather than preferable.**

**2.2 The 11 %/yr structural constant is a Charter modelling assumption, not a measurement of
this data.** Charter Seat 7's `0.01% × 3 × 365 = 10.95%` is arithmetically correct as stated
[cited]. It is not what the firm's own panel realized: BTC +11.86 %, ETH +14.07 %, SOL +0.10 %
[measured]. Seat 7's structural note remains a legitimate *prior* for a strategy that must clear
it; it is not admissible as an *input* to a P&L once a realized series exists. Recorded so that
"the Charter says 11 %" is never offered as a substitute for the 7,203 prints on disk.

**2.3 The defective function has zero test coverage.** `carry_per_bar` has exactly one caller
(`engine.py:116`) and **no test in the 96-test suite references it, or `funding_bps_annual`, or
`borrow_bps_annual`, or `CRYPTO_PERP_TAKER`** [measured — grep across `harness/tests/`]. The
single most consequential arithmetic error in the harness sits in the only function in `costs.py`
that nothing tests. That is the finding behind I-021's arrangement and it is why §4 exists before
Seat 9 writes a line.

---

## 3. THE SPECIFICATION

The governing principle, stated once so every clause below is derivable from it:

> **A cost is a friction the firm pays to change a position. A carry is a cash flow the position
> earns or pays for existing. The first is a function of trades and belongs to the cost library.
> The second is a function of holdings and a signed market rate, and belongs to the return.**
>
> `CostModel` may hold a friction. It may not hold a cash flow whose sign depends on which side
> the firm is on.

### 3.1 What leaves `CostModel` — removal, not zeroing

**Delete `funding_bps_annual` from `CostModel`.** Delete `funding_bps_annual=1095.0` from
`CRYPTO_PERP_TAKER`. Delete the funding term from `carry_per_bar` and from `scaled`.

**Why removal rather than a `0.0` default.** PREREG-002 §12.8 commits to "`funding_bps_annual`
set to `0.0` in the cost model to prevent double-counting" [cited]. That is a convention, and the
harness's own docstring states its design philosophy — *"Two properties are enforced structurally
rather than by convention"* [cited — `engine.py:3`]. A field whose correct value is always zero,
whose wrong value silently double-counts **with the sign inverted**, and which no test covers
(§2.3) is the I-036 shape waiting to recur. After removal, double-counting is not a discipline
problem; it is a `TypeError`.

**`borrow_bps_annual` STAYS, provisionally, and I record why rather than leave it looking
consistent.** Equity borrow is the same defect one asset class over — a signed, time-varying cash
flow (rebates exist) modelled as a constant cost on gross short notional. It stays because there
is **no realized borrow series in `pit.db` and no loader for one** [measured], so migrating it now
would replace a documented approximation with an undocumented one, and because no equity-short
family is live. **The rule that prevents it becoming a back door:** where a realized carry series
exists for an instrument, the accrual path of §3.3 is **mandatory** and the scalar path is
inadmissible; where none exists, the scalar is permitted **and its use is declared in the sealed
field set**, naming the instrument and the assumed rate. A family may not choose the scalar
because the accrual is inconvenient.

`carry_per_bar` is renamed **`borrow_per_bar(short_notional)`** — one argument, one meaning, and
no signature that invites a gross computation. **This kills the gross bug by construction:** the
function that took `long + short` no longer takes `long`.

**A second defect closed in passing.** `carry_per_bar` divides by `self.periods_per_year` while
`run_backtest` accrues returns against its **own** `periods_per_year` argument, and nothing
reconciles them [measured — `costs.py:54–55` vs `engine.py:51–63`]. A caller passing
`periods_per_year=365` with `US_EQUITY_SHORT` (`periods_per_year=252`) accrues borrow at 252 and
annualizes at 365, silently. `borrow_per_bar` must take the bar count from the engine's
`periods_per_year`, not the model's, and the model's field is retained only as a default the
engine overrides. **No Issue Log entry covers this** (§8, N-1).

### 3.2 Where the realized prints come from — a sanctioned accessor, not researcher code

This is the clause that answers the Director of Research's refusal, and it is why the refusal was
correct. The DoR declined to build a synthetic perp total-return leg because *"it relocates a cash
flow from the cost stack — which Seat 9 owns and researchers may not touch — into the price panel,
which researchers build"* [cited — PREREG-002 §12.3]. The objection is sound and the repair is
not to overrule it but to move the boundary so the researcher never crosses it.

**Add to `castellan.data`, owned by Seat 9, alongside `pit_adjusted_close` and `pit_price_panel`:**

```
pit_funding_panel(store, source, symbols, decision_time, bar_index) -> pd.DataFrame
```

- Returns a `(T, A)` frame on **exactly** `bar_index`, columns aligned to `symbols`, values equal
  to the **arithmetic sum of realized `funding_rate` prints falling in each bar's window**.
- Consumes `PITStore.asof(..., fields=["funding_rate"])`, which already filters
  `knowledge_time <= decision_time` — so Amendment A4's PIT discipline covers funding by the same
  mechanism that covers prices, and nothing new is trusted.
- **No annualization. No cadence constant. No mean. No `periods_per_year`.** The panel is a sum
  of realized cash-flow rates per bar and carries no units beyond "fraction of notional."
- Missing bar → `0.0` **only** where the symbol has coverage spanning that bar; a bar outside the
  symbol's coverage is `NaN` and the engine refuses to accrue against `NaN` rather than treat it
  as zero carry. **Absent data must not read as zero funding** — that is the free-carry failure
  mode and it is the direction that flatters.
- Stamps `decision_time`, the per-symbol print counts, and the `sha256` of the returned values
  into `df.attrs`, which `run_backtest` copies into the trial config (A2 reproducibility).

**The alignment rule, fixed in code and not left to the caller.** The engine's bar-`t` return is
`prices.pct_change()[t]`, the return over **`(t−1, t]`**. The funding accrued to bar `t` is
therefore the sum of prints with `event_time ∈ (t−1, t]` — **left-open, right-closed.**

This is not a nicety. A naive `groupby(date).sum()` assigns day `t`'s 00:00, 08:00 and 16:00
prints to bar `t`, i.e. two prints settling up to **16 hours after** the bar the position was held
over. Daily funding autocorrelation is **0.829 (BTC), 0.802 (ETH), 0.493 (SOL)** [measured], so a
one-bar forward misalignment is strongly informative — and PREREG-002's conditioning variable *is*
funding, so the strategy is sized on the same series the accrual would be leaking. That is Charter
§4.6's same-bar-fill prohibition arriving through the carry line instead of the price line, and it
is the highest-probability implementation error in this whole repair. **T-10 exists for it.**

### 3.3 Where funding enters — the engine, signed, per asset, never gross

`run_backtest` gains an optional keyword:

```
run_backtest(..., funding_panel: pd.DataFrame | None = None)
```

and computes, **after** `positions = target_weights.shift(execution_lag)` and from the same
`positions` object the gross return uses:

```
carry_accrual_t  =  −(positions_t · funding_panel_t)        # per-asset dot product
net_t            =  gross_t + carry_accrual_t − trade_cost_t − borrow_t
```

Three properties, each of which is a test below:

1. **Signed by position.** Positive funding means longs pay shorts, so the cash flow to a signed
   notional `n` is `−n · f`. Short perp (`n < 0`), positive funding → **receipt**. This is the
   whole ruling in one minus sign, and **the minus sign lives in the engine, where no researcher
   writes it.** The DoR's governance objection is answered: the researcher supplies a panel from
   a sanctioned accessor and never expresses a direction.
2. **Per asset, never on an aggregate.** The accrual is a dot product over columns. `long_n`,
   `short_n` and gross notional appear nowhere in it. A spot column with no funding coverage
   contributes exactly zero however large its notional.
3. **On lagged positions.** The accrual uses `positions`, which is already shifted by
   `execution_lag ≥ 1`. A position decided at bar `t` cannot accrue carry at bar `t`. Same
   invariant as `SameBarFillError`, same reason.

**`carry_accrual` is reported as its own series on `BacktestResult`** — not netted into
`cost_returns`, which must remain frictions-only. A signed cash flow inside a field named
`cost_returns` is how this defect got written in the first place. `total_cost_drag_annual_bps`
continues to describe frictions and gains a companion `total_carry_accrual_annual_bps`, signed.

### 3.4 Two legs, two cost models

`run_backtest(cost_model=...)` accepts **either** a single `CostModel` (unchanged, applied to all
columns — full backwards compatibility) **or** a `dict[str, CostModel]` mapping asset column →
model. A mapping that omits a column raises rather than defaulting.

**Rejected alternative — run each leg as its own backtest and add the series.** This is the
construction a hurried seat will reach for and it is inadmissible: adding two net return series
outside the engine produces a number produced outside the engine, which Amendment A2 forbids
[cited]; it doubles the family's trial count for one economic strategy, corrupting the DSR
denominator that is the point of the registry; and it makes the delta-neutral pair's carry
irrecoverable, because the netting that produces the receipt happens across legs.

**Rejected alternative — cost both legs at `CRYPTO_PERP_TAKER` and call it conservative.** It is
not conservative; PREREG-002 §12.4 records that the spot leg's taker fee is higher in a known
direction [assumed — exchange schedule, unverified], so the single-model route understates.

**`CRYPTO_SPOT_TAKER` is a new preset and therefore the Principal's to approve** (Charter §4.6:
"presets or Principal-approved additions"). I specify its shape and refuse to set its numbers
without a source: `commission_bps` and `half_spread_bps` from the venue's **published maker/taker
schedule at the family's `C`**, cited in the sealed field set, `impact_y = 1.0` and
`impact_exponent = 0.5` per Charter §4.2, `periods_per_year = 365`. A preset added with numbers
nobody can cite is a hand-rolled cost with a variable name, and I will refuse a Validation Report
resting on one.

**Trial identity.** `config["cost_model"]` currently stores one name string [measured —
`engine.py:125`]. It becomes a deterministically-ordered mapping of column → model name, plus the
funding panel's `decision_time` and value `sha256`. Two runs differing only in which model priced
which leg must hash differently, or the registry cannot tell them apart and A2's reproducibility
guarantee is void.

### 3.5 Liquidation and venue insolvency — NOT a chargeable field

I-034(3) and I-023(b) both ask for a `CostModel` field that charges the risk that ends carry
strategies. **Refused, on three grounds, and the refusal is the substantive ruling of this
section.**

**(a) A per-bar deduction converts a fat left tail into a thin constant drag — and that
*improves* the statistics the firm uses to detect exactly this risk.** Subtracting an expected
loss `p·L` from every bar's mean lowers the numerator of the Sharpe by a little and leaves the
denominator untouched. Meanwhile the criteria built to catch jump exposure — §4.4's P&L
concentration limits, subperiod positivity, and F-002's leg (ii) tail comparison — all read
*better*, because a smooth drag is not a bad day. **The field would make the firm's tail
detectors less sensitive to the tail they exist to detect, while producing a document that says
the risk was charged.** That is a worse outcome than the current honest silence.

**(b) There is nothing to parameterize it with.** `pit.db` contains zero venue-failure
observations and the firm has no source for either `p` or `L`. A number chosen for the field is a
hand-rolled cost with a schema around it, and it is worse than a hand-rolled cost because it
looks measured.

**(c) The two halves have different correct homes, and conflating them is the error.**

| Component | Nature | Correct home |
|---|---|---|
| **Forced liquidation** | Not a risk to be charged — a **position that cannot be held**. It is a function of maintenance margin and the basis, both observable | A **position constraint in weight construction**. A family whose weights ignore margin has an inadmissible position path, not an under-charged one. Where a family cannot express it, its backtest over-reports and the Validation Report says so on its face |
| **Venue insolvency** | An uninsurable, undiversifiable, un-hedgeable jump on **custody**, not on the position | **Risk and disclosure.** Not a cost. Declared as an uncharged exposure on every artifact, sized as a scenario (`−100 % of venue-held notional`), and carried to the CRO |

**Binding, and it is the enforceable part:** any Gate 0 or Gate 1 artifact for a family with
venue-held notional carries, on its face, the named uncharged exposure, the notional exposed, and
the sentence *"This risk is not charged in any number in this report."* Same instrument as
C-001's disclosure requirement, same reason: the defect is not that the number is missing, it is
that a reader assumes it is present. **I-023(b)'s oracle/resolution risk takes the identical
treatment** — it is the same shape and this ruling covers both.

**Escalated, not decided:** whether §4.4 should acquire a criterion for uncharged catastrophic
exposure is a Charter question and it is the Principal's. I will not invent a threshold
mid-evaluation.

### 3.6 Stress semantics — the Principal's split, adopted and completed

**Adopted:** `scaled(m)` applies to **frictions only** — commission, half-spread, impact, borrow.
It does not touch carry. Carry is varied by an explicit, named **scenario**.

**The measured argument that makes this decisive, which the Principal's note does not contain.**
`evaluate_gate1` uses the `net_returns_at_cost_multiplier` callable for two things: the 2× test
**and a 24-iteration bisection for the breakeven cost multiplier over `[1, 32]`** [measured —
`gates.py:463–476`]. That bisection assumes `t(m)` is **non-increasing** in `m`. If `m` scaled a
*receipt*, `t(m)` would be **increasing** — BTC carry is +11.86 %/yr [measured] against a
round-trip friction of 24 bps on a low-turnover hold — and the bisection would drive `lo → 32.0`
and report **"survives 32× costs."** So the naive multiplicative construction does not merely
fail to stress the family: **it manufactures a robustness result equal to the ceiling of its own
search bracket, and reports it under a Charter §4.4 heading.** The split is not a preference.

**Completion (A3) — sign inversion is not a conservative operator.** [measured] Under a
short-perp receiver, comparing realized funding to `f → −f`:

| Symbol | Realized mean | Inverted mean | Realized worst-20-day mean | Inverted worst-20-day mean | Tail under inversion |
|---|---:|---:|---:|---:|---|
| BTC | +11.86 %/yr | −11.86 %/yr | −0.00106 | −0.00395 | **3.7× worse** |
| ETH | +14.07 %/yr | −14.07 %/yr | −0.00138 | −0.00529 | **3.8× worse** |
| SOL | +0.10 %/yr | −0.10 %/yr | −0.02192 | −0.00487 | **4.5× BETTER** |

Inversion is adverse in the mean by construction and **arbitrary in the tail**, because its effect
depends on the skew of the series it is applied to. On SOL it **deletes the 2022-11-10 event**
(daily funding **−17.17 %**, from prints settling at 2-hour intervals) — the sample's one
realization of the fat left tail Charter Seat 7 explicitly warns about, and worth **1.6× the
entire annual magnitude of the 10.95 %/yr scalar in a single day**. A family reporting sign
inversion as *the* stress case would be reporting a scenario that improves its own worst-day
statistic and calling it conservatism.

**The mandatory scenario set, declared at sealing, not chosen after.**

| Scenario | Construction | What it answers |
|---|---|---|
| `REALIZED` | prints as ingested | the base case |
| `ZERO` | `f → 0` | how much of the result is carry harvest and how much is anything else. **The one that tells you whether the family is a strategy or a yield** |
| `SIGN_INVERTED` | `f → −f` | a complete regime flip in the mean. **Reported with its measured tail effect attached, never alone** |
| `TAIL_BOOTSTRAP` | stationary block bootstrap of the realized panel, block ≈ 21 bars, ≥ 1,000 paths, reporting the 5th percentile of net return | the realized tail recurring at other points in the sample. **This is the scenario that carries the 2022-11-10 event, and it is why inversion cannot stand alone** |
| `SHIFT(δ)` | `f → f − δ`, δ in bps/yr, converted to per-bar using the panel's own realized print structure | the reported scalar, below |

**The reported statistic is the breakeven adverse carry shift.** Charter §4.4 already requires
*"the round-trip cost in basis points at which t falls below 3.0 — it is more informative than the
net Sharpe itself"* [cited]. Its correct analogue for a carry family is:

> **`carry_breakeven_bps_annual` — the adverse parallel shift δ, in bps/yr, at which the net
> return's t-statistic falls below 3.0.**

It is monotone in δ (so bisectable, where the multiplier is not), it is in units directly
comparable to the realized series' own dispersion, and it converts an unanswerable question
("is 2× the right stress?") into an answerable one ("the family dies at 640 bps/yr of adverse
carry; realized funding moved that far in *n* windows of the sample"). **Specifying this statistic
is within my mandate — §4.4 already mandates that a breakeven be reported, and this is the
construction of the number it names for the instrument in front of me. Setting a *threshold* on it
is not (§5).**

### 3.7 What does not change

`per_side_cost` and its square-root impact term — untouched; C-002 already ruled the impact
construction correct [cited]. `POLYMARKET`'s I-023(a) price-proportional half-spread defect —
**out of scope here and still open**; nothing in this ruling repairs it. `execution_lag`,
`SameBarFillError`, the registry contract, the vault, `PaperBook`'s fill path. `US_EQUITY_LARGE`
and `US_EQUITY_SHORT` are unchanged in value.

---

## 4. ACCEPTANCE TESTS — authored by Validation, before implementation

**Standing terms.** These are authored under the I-021 arrangement: the implementing seat does not
grade its own implementation. **Seat 9 implements against these tests and does not amend them.** A
test that Seat 9 believes is wrong is escalated to me, in writing, before it is changed —
weakening a pre-authored test to make an implementation pass is the failure I-036 records arriving
deliberately instead of by accident.

**File:** `harness/tests/test_carry_accounting.py`. **Fixtures:** a committed extract of the
realized `funding_rate` series for BTC/ETH/SOL under `harness/tests/fixtures/`, with its `sha256`
recorded in the test module — tests must not read `book/pit.db` at runtime. **All 19 must pass,
and the existing 96 must still pass.** The suite is then 115 minimum.

### 4.1 Structural — the defect cannot be re-expressed

**T-1 · `CostModel` has no funding field.**
`assert not hasattr(CostModel, "funding_bps_annual")` and `"funding" not in
{f.name for f in dataclasses.fields(CostModel)}`. Constructing `CostModel(..., funding_bps_annual=1095.0)`
raises `TypeError`. `CRYPTO_PERP_TAKER` exposes no funding term of any name.
*Fails if the field is merely defaulted to `0.0` — which is the specific outcome this test exists
to prevent (§3.1).*

**T-2 · `carry_per_bar` is gone and its replacement cannot take a long notional.**
`assert not hasattr(CostModel, "carry_per_bar")`. `borrow_per_bar` accepts exactly one positional
notional argument; calling it with two raises `TypeError`.
*The gross bug dies at the signature.*

**T-3 · `scaled(m)` touches frictions only.**
For `m ∈ {0.5, 2.0, 8.0}`: `commission_bps`, `half_spread_bps`, `impact_y`, `borrow_bps_annual`
each scale by exactly `m`; `periods_per_year`, `impact_exponent` are invariant; and the model
carries no field that `m` could apply to a receipt.

### 4.2 Sign and base — the headline

**T-4 · A delta-neutral pair RECEIVES.**
Two assets, `spot` and `perp`, constant prices (so `gross ≡ 0`), constant positive funding
`f = 0.0001` per 8h at 3 prints/bar, positions `+1.0 spot / −1.0 perp`, zero-friction cost model,
365 bars.
Assert: `carry_accrual.mean() * 365 ≈ +0.1095` to 1e-9; `net.sum() > 0`; and — stated as its own
assertion because it is I-034's exact arithmetic — `carry_accrual.mean() * 365` is **not**
`−0.219` and **not** `−0.1095`.
*This is the test the current harness fails by 32.85 points per year. If only one test survives
review, it is this one.*

**T-5 · The full sign matrix.** Four cases, each an independent assertion:

| Position | Funding | Required accrual sign |
|---|---|---|
| short perp (`−1.0`) | `f > 0` | **positive (receipt)** |
| long perp (`+1.0`) | `f > 0` | **negative (payment)** |
| short perp (`−1.0`) | `f < 0` | **negative (payment)** |
| long perp (`+1.0`) | `f < 0` | **positive (receipt)** |

*A sign error passes T-4 in one of these four worlds. It cannot pass all four.*

**T-6 · The accrual is NEVER a function of gross.**
Two books with **identical gross notional 2.0**: book A = `(+1.0 spot, −1.0 perp)`, book B =
`(+1.0 perp, −1.0 spot)`, same funding panel (`f > 0` on the perp column, `NaN`-free zero on
spot). Assert `accrual_A == −accrual_B` and both non-zero.
*Any implementation computing on `long_n + short_n`, `long_n − short_n`, or `abs(positions).sum()`
returns the **same** value for A and B and fails. This is the anti-regression test the task
requires and it discriminates every gross-shaped implementation, not just the current one.*

**T-7 · Funding applies only where it exists.**
Three columns: `perp` (funding), `spot` (zero funding, coverage present), `etf` (no funding
coverage at all → column absent from the panel). With notionals `(−1.0, +1.0, +5.0)`, assert the
accrual equals `−(−1.0)·f_perp` exactly, independent of the `etf` notional; and that varying the
`etf` weight over `{0, 5, 50}` leaves the accrual bit-identical.

### 4.3 Realized prints, not a scalar

**T-8 · Realized beats any scalar, and the gap is material.**
Run the SOL fixture (6,508 realized prints, 2020-09-13 → 2026-07-28) through the accrual path on a
constant `−1.0` perp notional. Assert annualized carry ∈ `[0.0005, 0.0020]` (i.e. ≈ **+0.10 %/yr**
[measured]). Separately assert that the same position under **any** constant-rate construction at
the Charter's `1095 bps` yields ≈ `+0.1095`, and that
`abs(realized − scalar) > 0.10` — **more than ten percentage points per year.**
*This test fails if a scalar path is used anywhere in the accrual, and it fails on the asset where
the scalar errs optimistically (§2.1).*

**T-9 · No cadence constant.**
Fixture containing the SOL 2022-11-09 → 2022-11-11 window, which carries **2-hour and 4-hour
settlement intervals and up to 12 prints in one day** [measured]. Assert the bar accrual equals
the **exact arithmetic sum** of the prints in that bar's window, for every bar in the window;
assert the 2022-11-10 bar's accrual on a `−1.0` perp notional is `−0.17166 ± 1e-6`.
*Any implementation multiplying a mean rate by 3, or by `periods_per_year`, or by any fixed
prints-per-day constant, fails. `DATA-INGEST-001`'s "Every 8h" data dictionary entry is measured
false and this test is what stops the codebase inheriting it (§8, N-2).*

**T-10 · The bar window is left-open, right-closed — the leakage test.**
Fixture with prints at `t 00:00`, `t 08:00`, `t 16:00`, `t+1 00:00`. Assert bar `t`'s accrual
contains the `t 00:00` print and **not** the `t 08:00` or `t 16:00` prints; assert bar `t+1`'s
accrual contains `t 08:00`, `t 16:00` and `t+1 00:00`. Assert the panel's total over the full
index equals the total of the underlying prints (nothing dropped, nothing counted twice).
*A `groupby(date).sum()` implementation fails. Daily funding autocorrelation is 0.83/0.80/0.49
[measured], so this misalignment is strongly informative and PREREG-002's conditioning variable is
the same series — §3.2.*

**T-11 · No same-bar carry.**
Target weights zero everywhere except a single `1.0` at bar `k`; `execution_lag=1`. Assert
`carry_accrual[k] == 0.0` and `carry_accrual[k+1] != 0.0`.
*The carry analogue of `SameBarFillError`. A position decided at `k` cannot earn carry at `k`.*

**T-12 · Absent coverage is `NaN`, not zero carry.**
Funding panel with a genuine coverage gap (symbol not yet listed) → `NaN`, and `run_backtest`
raises rather than accruing `0.0`. A bar *within* coverage with no print → `0.0`, accepted.
*Absent data reading as zero funding is the free-carry failure mode and it flatters.*

**T-13 · PIT discipline holds on funding.**
`pit_funding_panel(..., decision_time=T)` excludes prints with `knowledge_time > T`; a restated
print returns its latest version at or before `T`; and the panel's `attrs` carry `decision_time`,
per-symbol print counts, and the value `sha256`.

### 4.4 Two legs

**T-14 · Per-asset cost models.**
`run_backtest(cost_model={"spot": A, "perp": B})` produces a total trade cost equal to the sum of
the per-leg costs computed independently; a mapping omitting a traded column raises; and a single
`CostModel` argument produces results **bit-identical** to the pre-change harness on a
funding-free fixture (backwards compatibility, asserted against a committed golden series).

**T-15 · Trial identity distinguishes the mapping.**
Two runs identical except that the two models are swapped between columns produce **different**
config hashes and different `trial_id`s; the config records the ordered column→model mapping, the
funding panel's `decision_time`, and its `sha256`.
*Without this, A2's "regenerable from a commit hash plus a config" is false for any two-legged
family.*

### 4.5 Stress semantics

**T-16 · A sign-inversion scenario is expressible, and it is NOT `scaled(m)`.**
One test, two assertions. (a) `scaled(2.0)` leaves `carry_accrual` **bit-identical** — carry is
untouched by the friction multiplier. (b) `CarryScenario.SIGN_INVERTED` produces
`carry_accrual' == −carry_accrual` exactly, and is reachable through a documented API that does
not involve `CostModel`.
*This is the task's explicit requirement and it is also the structural statement of the ruling:
the two operators are disjoint.*

**T-17 · `ZERO` isolates the non-carry component; `TAIL_BOOTSTRAP` preserves the tail.**
`CarryScenario.ZERO` produces `net` identical to a run with `funding_panel=None`.
`TAIL_BOOTSTRAP` on the SOL fixture, 1,000 paths, block 21: assert the 5th-percentile path's
worst-day loss is at least as severe as the realized worst day (the bootstrap must not be able to
lose the 2022-11-10 event), and assert the mean across paths is within 2 standard errors of the
realized mean.

**T-18 · The breakeven adverse carry shift is monotone and bisectable — and the multiplicative
alternative is not.**
On a receiver fixture: assert `t(δ)` is non-increasing over `δ ∈ [0, 2000]` bps/yr at 25 sampled
points, and that `carry_breakeven_bps_annual` returns a finite δ strictly inside the bracket.
Then, in the same test and as the recorded reason for the design, assert that the **multiplicative**
construction `f → m·f` yields a **non-monotone (increasing)** `t(m)` on the same fixture, and that
feeding it to `evaluate_gate1`'s existing `[1, 32]` bisection returns the bracket ceiling `32.0`.
*Locks in §3.6's measured finding: the naive construction reports a fabricated robustness result
equal to the ceiling of its own search bracket.*

### 4.6 Anti-regression on the refused field

**T-19 · No liquidation or insolvency field appears in `CostModel`.**
`assert not any(k in f.name for f in dataclasses.fields(CostModel) for k in
("liquidation", "insolvency", "venue", "oracle", "resolution"))`, with the docstring of the test
citing §3.5.
*Prevents a well-meaning seat closing I-023(b)/I-034(3) by inventing a number. If the Principal
later rules that such a field should exist, this test is deleted by his written decision and not
by an implementer's judgment.*

> **Count: 19 acceptance tests.** T-4, T-6, T-8, T-9, T-10 and T-16 are the six that carry the
> ruling; the rest close the routes around them.

---

## 5. THE CHARTER QUESTION — §4.4's cost-robustness criterion does not bind a carry family

**I name this and I do not resolve it. It is the Principal's.**

The task asks whether the split stress semantics changes what §4.4's cost-robustness criterion
tests. It does, and the honest statement is uncomfortable in both directions:

| Construction | What "retains t ≥ 3.0 at 2× modelled costs" actually tests |
|---|---|
| **Today (shipped)** | A **sign error**, doubled. −21.9 %/yr becomes −43.8 %/yr. The criterion cannot be satisfied by any delta-neutral carry family and its failure carries no information |
| **Naive repair** (carry stays in the multiplier, sign corrected) | Nothing — worse, it **manufactures** a result. `t(m)` becomes increasing, the `[1, 32]` bisection returns **32.0**, and the report reads "survives 32× costs" [measured reasoning, §3.6] |
| **This ruling's split** | A friction stack of **24 bps round trip** against a carry term of **1,186 bps/yr** [measured]. The criterion is **honest and trivially satisfied.** It tests a real thing that is not the thing that decides this family |

**So the criterion moves from actively wrong to honestly inert, and neither is what §4.4 was
written to do.** The 2× multiplier was written for a strategy whose P&L is a signal net of
frictions. It has no purchase on a strategy whose P&L is dominated by a market rate.

**What I am doing about it, within my mandate:**

1. §4.4's criterion is evaluated **as written**, on frictions, at Gate 1. **Thresholds do not move
   mid-evaluation** — that is my own standing rule and it binds me first.
2. The criterion's report line carries a **mandatory note** whenever the run had a funding panel:
   *"Evaluated on frictions only. This family's dominant P&L term is realized carry, which this
   criterion does not stress. See the carry scenario table."* A criterion that reads PASS without
   that note is a defective report and I will return it. **This is a disclosure requirement, which
   is mine, not a threshold change, which is not.**
3. The **carry scenario table** and `carry_breakeven_bps_annual` (§3.6) are reported at Gate 1 as
   **disclosure, not pass/fail**, until the Principal signs a threshold.

**What I recommend the Principal decide, at the Quarterly Review and not before** — because
D-011 §6's own instruction on the α budget was *"do not improvise one"* and the same discipline
applies here:

> Whether §4.4 acquires a **carry-robustness criterion** alongside cost robustness, of the form
> *"retains t ≥ 3.0 under `SIGN_INVERTED` and under the 5th-percentile `TAIL_BOOTSTRAP` path"*,
> with `carry_breakeven_bps_annual` reported on every submission the way the breakeven cost
> already is.

**This is not on PREREG-002's critical path** and must not be allowed to become a reason to
delay. §4.4 is a **Gate 1** criterion; PREREG-002 is at Gate 0 and, on its own §11.3 arithmetic,
cannot reach Gate 1 before **2027-07-28 at the earliest** under the most permissive of the three
readings. The amendment has a year of runway. **The implementation does not wait for it.**

---

## 6. TASK 2 — C-001 attachment terms for PREREG-002

D-011 §7 directs that C-001's five conditions attach to PREREG-002's forward test at sealing,
with statistic and α named now. **I amend the premise, and the amendment is not a technicality.**

### 6.1 F-002 leg (i) is not the C-001 statistic and cannot be nominated as one

F-002's three series are computed **"on the same daily UTC index over the full in-sample
`[2020-01-01, C]`"** [cited — PREREG-002 §5.1]. **C-001's exemption is available only on a
genuinely FORWARD window — E5, which my own ruling calls "the largest single limit on the ruling"**
[cited — VALIDATION-GATE0-001 §1.3]. Nominating an in-sample statistic as the confirmatory test
would be E5 violated at the first opportunity to apply it, by the seat that wrote it.

**F-002 leg (i) carries `N_total`, not `N = 1`.** It is a falsifier on the research record. It is
correctly specified and I confirm its statistic and α **in that role**, below.

### 6.2 KC-002 is not a confirmatory test either — confirmed

PREREG-002 §14.1 states this itself, quoting my §1.6, and explicitly disclaims the exemption:
*"This family does not claim the C-001 `N = 1` confirmatory exemption"* [cited]. **Confirmed and
endorsed.** KC-002's three clauses are bare threshold comparisons with no null and no power
statement. Surviving it confirms nothing at any `N`.

### 6.3 And a confirmatory test on that window would have ~1% power — so none is nominated

Had anyone proposed naming one on the KC-002 window, the arithmetic forecloses it. Over
`[C, C+187 days]` = **0.512 years** [measured]:

| | |
|---|---:|
| Net annualized Sharpe required to reach `t = 3.0` on 187 bars | **4.19** |
| **Power** of that test at the family's own Gate 1 target of net SR **1.0** | **1.1 %** |
| Power at net SR 1.5 / 2.0 / 3.0 | 2.7 % / 5.8 % / 19.7 % |
| Forward window required for `t = 3.0` at net SR 1.0 / 1.5 / 2.0 | **9.00 / 4.00 / 2.25 years** |

*(one-sided, `α = 0.00135`, `t = SR·√T`) [measured]*

**A confirmatory statistic named on that window would be a test that cannot fire, pre-registered
as though it could** — and it would be reported as "the family survived its forward test." That is
precisely the sentence C-001 §1.6 exists to prevent. **A confirmatory test on this family is not
available until roughly 2030 at a Sharpe of 1.5, and 2035 at a Sharpe of 1.0.**

### 6.4 What therefore attaches at sealing — and it satisfies D-011 §7 exactly

> **BINDING. The sealed field set for `funding-carry-conditioning-002` carries an explicit
> negative declaration:**
>
> ```
> c001_confirmatory_exemption_claimed = FALSE
> c001_confirmatory_statistic         = NONE
> c001_confirmatory_alpha             = NONE
> c001_declaration = "This family claims no C-001 N=1 confirmatory exemption. No forward
>   confirmatory statistic is nominated. Under E1 a statistic identified after the window
>   opened is not confirmatory at any N, and under P7 nothing may be added after sealing;
>   the exemption is therefore permanently unavailable to this family and to any restatement
>   of it that inherits this seal."
> ```

**This is the attachment D-011 §7 requires, and it is stronger than naming a statistic.** E1
demands the statistic be named at sealing; the field set must therefore say *something* about it,
and P7 makes whatever it says permanent. Naming nothing silently leaves the question open to a
future seat's interpretation. **Naming the disclaimer closes it by the same mechanism that would
have frozen a statistic.** The exemption becomes unavailable rather than conditionally available,
which is the conservative direction and the one my prior of guilt requires.

**And it is entered in the I-032 firm-level register as a NIL entry** — Σα contribution **0.000**
— so that the register's first substantive act is recording a family that did not claim.

### 6.5 F-002 leg (i), confirmed in its actual role

| Field | Value | Verdict |
|---|---|---|
| Statistic | Newey–West `t(α)` on `R_strat = α + β·R_bench + ε`, lag truncation **21 bars**, over `[2020-01-01, C]` | **CONFIRMED as drafted.** Newey–West rather than OLS is correct — a carry residual is autocorrelated by construction and the OLS `t` is inflated in a known direction |
| Threshold | `t(α) ≤ 3.0` fires the leg | **CONFIRMED.** Charter §4.2 `T_STAT_HURDLE`, imported not invented |
| Stated α | **0.00135**, one-sided [measured — `1 − Φ(3.0)`] | **CONFIRMED** |
| Denominator | **`N_total`**, not `N = 1` | **AMENDED — stated explicitly at sealing.** This is the in-sample record where the maximization happened |
| Computed | **Once (E2 discipline adopted voluntarily by the sponsor, §5.5)** | **CONFIRMED and I hold the sponsor to it.** A re-run "with the repaired costs" after F-002 has been computed opens a new family, as PREREG-002 §5.5 itself states |

**One further constraint, because the sponsor's own E2 adoption creates a trap.** F-002 must be
computed on the **repaired** cost path, first time, once. Since C1 is the repair and F-002 may not
be re-run after it lands, **the ordering is not optional: repair green → seal → F-002.** Sealing
before the repair would force either a defective F-002 or a re-run that opens a successor family.
D-011 §7 already sequences it this way; I record that E2 makes the sequence binding rather than
merely prudent.

### 6.6 C11 — leg (ii)'s `≤ 0.10`: REQUIRED MEASURED BEFORE SEALING

**Required.** The DoR recommended I require it and the recommendation is right, but the decisive
argument is not the one offered.

**The offered argument** — that one [assumed] probability in an otherwise derived chain is where
I-029's finding returns — is sound and I accept it. The `1.3 × 10⁻⁴` joint false-survival figure
is `0.0013 × 0.10`, of which the second factor is asserted. If leg (ii)'s true operating
characteristic is 0.5 rather than 0.10, the joint rate is `6.5 × 10⁻⁴` — still small, and **that
is not the point**: the point is that the family would be advertising a number it does not have.

**The decisive argument is P3/P7.** If C11 is measured *after* sealing and comes back at 0.6, the
correct response is to **redesign leg (ii)** — and P3 refuses amendments to a sealed
pre-registration. The firm would hold a frozen falsifier it knows to be weak and cannot fix, for
the life of the family. **A calibration that can only be acted on before the freeze must happen
before the freeze.** Measuring it after is not conservatism; it is buying information the firm has
disqualified itself from using.

**But C11 as drafted is not executable, and this is the same shape as I-030.** PREREG-002 §20 makes
C11 a condition precedent to sealing; §15 step **1b** schedules it as **≤ 2 registry trials**
running *inside* the family's 80-trial budget — which requires `open_hypothesis`, which **is** the
seal (§11.1: the vault is sealed in the same session as the `open_hypothesis` call). **A registry
trial cannot precede the registry entry.** The two sections contradict each other and the
contradiction is mechanical, not editorial.

> **RESOLUTION, binding.** C11 runs in a **separate methodology family**, opened in
> `book/registry.db` as `falsifier-calibration-f002-legii`, `n_inherited = 0`, budget 4, whose
> trials are the bootstrap/randomization paths. It is admissible and non-contaminating because:
> it consumes **`R_bench` only** — the unconditioned carry factor, not the strategy; it selects
> **no configuration** and carries **no result** forward except the leg's operating
> characteristic; the holdout `[C, G]` does not yet exist and cannot be touched; and A2 is
> satisfied because every path is an engine run and a logged trial.
>
> **Its `N` does not accrue to `funding-carry-conditioning-002`**, and the family's declared
> `N = 86` / budget 80 is unchanged. §15 step 1b is struck; C11 moves wholly before the seal.
>
> **The measured value replaces `[assumed] ≤ 0.10` in §5.3 and in the joint arithmetic, whatever
> it turns out to be.** If it exceeds **0.25**, leg (ii) is redesigned before sealing — that
> threshold is named now, before the number is known, for the same reason every other threshold
> in this firm is.

### 6.7 C6 — answered here, in the negative, with the remedy

PREREG-002's C6 asks me to confirm that reading `field='funding_rate'` through `PITStore.asof` /
`rows_in_window` is an admissible A4 path, *"there being no `pit_*` panel accessor for a non-close
field."* **It is not, and §3.2 is the remedy.** Researcher-side aggregation of a raw cash-flow
series is the boundary crossing the DoR refused to make, and I am not going to authorize by
omission what he correctly declined to authorize directly. **`pit_funding_panel` is Seat 9's, the
alignment rule lives in code, and C6 is discharged by the accessor's existence — not before.**

---

## 7. WHAT UNBLOCKS, WHAT STAYS BLOCKED

### 7.1 Unblocked by this ruling

| Item | Status change |
|---|---|
| **PREREG-002 C1** | **DISCHARGED as a specification.** §3 is the construction, §4 is the acceptance suite. Seat 9 may implement immediately |
| **I-034** | Moves from *"specified by nobody"* to *"specified, unimplemented."* It closes when the 19 tests and the existing 96 are green, and **not before** |
| **I-034(3) / I-023(b)** — the liquidation/insolvency field | **RULED, in the negative** (§3.5). Both are resolved as cost-model questions and re-opened as **disclosure and Risk** questions. T-19 prevents them being closed by invention |
| **PREREG-002 C6** | **Answered in the negative with a remedy** (§6.7). Discharged when `pit_funding_panel` exists |
| **The DoR's refusal** | **Vindicated and made moot.** The synthetic-leg construction is not adopted; the boundary is moved so the researcher never crosses it |

### 7.2 Still blocked — and this ruling does not touch any of it

| Blocker | Why it survives |
|---|---|
| **I-035 — no perp price series** | **Unaffected by this repair, and still fatal to measurement.** Funding is now an accrual; the short-perp leg's *price return* still requires the perp mark. Using spot for both legs zeroes the basis, which is the quantity under study and which the DoR ruled inadmissible. **PREREG-002 §15 step 1 must land** |
| **PREREG-002 C2 — the Gate 0 intake verdict** | **No Gate 0 intake verdict on PREREG-002 exists.** `VALIDATION-GATE0-001` adjudicates the *forward-lag* family. **This document is a cost-model specification and is NOT an intake verdict, and must not be read or cited as one.** C2 is BLOCKING on sealing and remains entirely open |
| **C3 · C7 · C8** | Red-Team Memo absent; KC-002 unsigned; seal/vault session discipline unexecuted |
| **C11** | Now **blocking on sealing** and re-routed through a separate calibration family (§6.6). Unrun |
| **C4 (§11.3 `oos_index` window) · C5 (haircut point of application)** | Validation rulings, both unfunded, both untouched here. C5 in particular still leaves PREREG-002's post-haircut Gate 1 bar undefined |
| **I-019 · I-022 · I-027 · I-023(a)** | Untouched. `POLYMARKET`'s price-proportional half-spread defect is **not** repaired by this ruling and nothing here should be read as having addressed it |
| **§4.4 carry robustness** | Charter amendment, the Principal's, at the Quarterly Review (§5). **Not on the critical path** |

### 7.3 The standing statement, until the tests are green

> **Every net number this family can currently produce is a −21.9 %/yr artifact.** No net figure
> from `funding-carry-conditioning-002`, in any document, from any seat, is admissible until the
> 19 acceptance tests and the existing 96 pass together. **A Validation Report resting on a
> pre-repair number is INSUFFICIENT-DATA by definition (A1), and I will return it unread.**

---

## 8. FINDINGS NO ISSUE LOG ENTRY COVERS

Raised here because a finding that reaches no log is functionally undisclosed — I-022's own
lesson.

**N-1 · `carry_per_bar` and `run_backtest` annualize against different bar counts · MEDIUM ·
head-of-data-infra.** [measured — `costs.py:54–55` vs `engine.py:51–63`] Carry divides by
`cost_model.periods_per_year`; returns are logged and annualized against `run_backtest`'s own
`periods_per_year` argument. Nothing reconciles them. `US_EQUITY_SHORT` (252) run with
`periods_per_year=365` accrues borrow at one calendar and reports at another, silently, in the
optimistic direction for a short book. §3.1 closes it for the engine; **the field's existence as a
second source of truth is the finding.**

**N-2 · The funding cadence in the data dictionary is measured false · MEDIUM ·
head-of-data-infra.** `DATA-INGEST-001` §3 records `funding_rate` update cadence as **"Every 8h"**
and §2 as *"funding posts every 8h (00:00 / 08:00 / 16:00 UTC)"* [cited]. Measured against
`book/pit.db`: BTC and ETH are uniformly 8h (7,202 intervals each, zero exceptions); **SOL has 98
two-hour intervals and 3 four-hour intervals, up to 12 prints in a single day, on 11 of 2,145
covered days** [measured]. The exceptions cluster in November 2022 — i.e. **the cadence assumption
fails precisely in the stress window where the carry accrual matters most.** Charter Seat 9's
standing obligation is to escalate data-dictionary defects to Validation; this one was not
escalated because nobody had looked. T-9 is the guard.

**N-3 · The harness's most consequential arithmetic error sits in its only untested function ·
MEDIUM · head-of-data-infra → quant-validation.** No test in the 96-test suite references
`carry_per_bar`, `funding_bps_annual`, `borrow_bps_annual`, or `CRYPTO_PERP_TAKER` [measured —
grep across `harness/tests/`]. A 96-test suite that is green while the cost library's carry
function is wrong in sign is a suite whose coverage is not where its risk is. **Recommend a
coverage audit of `costs.py` and `engine.py` as a distinct deliverable, not folded into this
repair.**

**N-4 · `PaperBook` accrues no carry at all · MEDIUM · head-of-data-infra → execution-ops.**
[measured] `book.py` calls `per_side_cost` and nothing else; `carry_per_bar` has exactly one
caller and it is the engine. **The paper book books zero funding and zero borrow on any held
position.** Charter Seat 10 is required to produce a fill-quality line including *"modelled
slippage, commissions, borrow, funding"* [cited — Seat 10]; the funding and borrow columns are
uncomputable from the book as built. On a delta-neutral perp position the paper book therefore
omits the entire economic content of the strategy. **§3.3's accrual must extend to `PaperBook`
before any paper allocation to a carry family, and that extension is not in this ruling's scope.**

**N-5 · PREREG-002 contradicts itself on C11's sequencing, mechanically · LOW ·
director-of-research.** §20 makes C11 a condition precedent to sealing; §15 step 1b schedules it
as ≤ 2 trials inside the family's budget, which requires `open_hypothesis`, which is the seal
(§11.1). **A registry trial cannot precede the registry entry.** Resolved in §6.6 by a separate
calibration family; logged because the same shape — a condition precedent scheduled as a
post-condition step — will recur.

**N-6 · Charter Seat 7's 11 %/yr is arithmetic, not measurement, and the distinction is now
material · LOW · quant-validation.** *"0.01% × 3 × 365 = 10.95%"* is labelled `[measured]` in
Charter prose [cited]. The arithmetic is correct; the **input** is a baseline assumption, and the
firm's own panel realizes **+11.86 % / +14.07 % / +0.10 %** [measured]. As a structural prior for
a long-perp strategy the note is sound and stands. **As an input to any P&L it is now
inadmissible**, superseded by the realized series (§2.2). Recorded before someone cites the
Charter against the data.

---

## 9. WHAT WOULD CHANGE MY MIND

| # | Ruling | What would overturn it |
|---|---|---|
| 1 | **Funding leaves `CostModel` entirely** | A demonstration that some admissible family has a genuine funding exposure with **no realized series obtainable** and no accrual path available. I would then reinstate a scalar — but as an **explicitly-declared modelling assumption in the sealed field set**, never as a preset default, and never on gross |
| 2 | **The field is removed, not zeroed** | Evidence that removal breaks a use I have not found. I checked: `carry_per_bar` has one caller and zero tests [measured]. If a second caller exists that I missed, the ruling is unchanged but the migration is larger than I have specified |
| 3 | **Liquidation/insolvency is not chargeable** | A defensible source for `p` and `L` — e.g. a venue-failure base rate the firm can cite rather than assume — **combined with** a construction that charges it as a **jump** rather than as a per-bar drag, so it does not launder a fat tail into a thin one. Both, not either. The Principal may also simply rule the other way; it is a Charter question and my §3.5 is a specification decision inside a gap he owns |
| 4 | **Sign inversion is insufficient as a stress** | It is [measured] on three assets and I would want it re-measured on any new asset. If a family's realized funding is **symmetric**, inversion and bootstrap coincide and the extra scenario is redundant — but that is a per-family measurement, not a general dispensation |
| 5 | **`carry_breakeven_bps_annual` rather than a multiplier** | A demonstration that `t(δ)` is non-monotone for some admissible strategy — e.g. one that flips sign on the carry regime. **T-18 would catch it**, and if it fires the statistic needs a bracket rather than a scalar. I have not proved monotonicity in general; I have specified a test that fails loudly if it does not hold |
| 6 | **C11 required before sealing** | If the calibration cannot be constructed without touching `[C, G]` — it cannot, `[C, G]` does not exist yet — or if the separate-family route is shown to contaminate `funding-carry-conditioning-002`'s denominator. I have argued it does not because no configuration is selected; **a demonstration that the DoR's design choices for leg (ii) would change in response to the calibration's result is exactly the contamination**, and it is also precisely why the measurement must precede the freeze. I have taken the second horn of that dilemma deliberately and it is the weakest joint in this ruling |
| 7 | **No C-001 exemption for PREREG-002** | A forward window long enough to give a confirmatory test real power — **≈ 4 years at net SR 1.5, 9 years at net SR 1.0** [measured]. At that point a **successor family**, sealed at a later `C`, may nominate one. This family cannot, because P7 has frozen the answer at its own seal |

---

## 10. SIGN-OFF

**This is a specification and a set of acceptance tests. It is not a Gate 0 intake verdict, not a
Gate 1 evaluation, and not an approval of `funding-carry-conditioning-002`.** PREREG-002's C2
remains entirely open.

**The Principal's direction survived because it was right, and I have recorded the three places it
was incomplete with the measurements that establish each.** He wrote the code, declared the
conflict, and said my ruling governs. The ruling adopts his construction, amends it on data he did
not have, and names the one question — §4.4's cost-robustness criterion — that is his to answer
and not mine to widen into.

**Standing rules from this ruling, binding from today:**

1. Where a realized carry series exists for an instrument, the accrual path is **mandatory**; the
   scalar is inadmissible. Where none exists, the scalar is permitted **and declared at sealing**.
2. Carry is never reported inside `cost_returns`. Frictions and cash flows are separate lines in
   every artifact, always.
3. Any artifact for a family with venue-held notional carries the uncharged-exposure disclosure of
   §3.5 on its face.
4. Any Gate 1 report whose run carried a funding panel carries the §5(2) note on the
   cost-robustness line. Without it the report is defective and is returned.

*No code was modified, no data fetched, nothing sealed, nothing committed, no trial logged.
`book/registry.db` untouched. Suite verified at 96 passed / 0 failed before and after.*

**Head of Quantitative Validation · Castellan Capital · 2026-07-29**




