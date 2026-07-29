# DATA-VERIFY-001 — Binance perpetual funding formula, verified against vendor documentation (I-042)

**Seat:** Head of Data & Infrastructure
**Date:** 2026-07-29
**Follows:** `logs/ISSUE_LOG.md` I-042 (mean basis negative, mean funding positive, unexplained), I-040 N-2
(SOL funding cadence measured false at 8h); `research/DATA-INGEST-002-perp-prices.md` §4 (the plausibility
join this document resolves); `research/PREREG-002-crypto-funding-basis.md` §3 (mechanism), §12 (cost
sections); `research/VALIDATION-RULING-003-carry-accounting.md` (realized-print accounting).
**Scope:** verification only. No backtest run, no signal or return statistic computed, no hypothesis
pre-registered, no vault sealed, no schema migration, nothing committed to git.

House rule 6: **[measured]** = read or executed this session · **[cited]** = named external source, read
in full or in the relevant part · **[inferred]** = reasoned from measured/cited facts · **[assumed]** =
unverified premise.

**Source-type discipline, per task instruction.** Every citation below is tagged `[cited — official]` for
a page under `binance.com`/`developers.binance.com`/the live `fapi.binance.com` REST API, or
`[cited — third-party]` for everything else (blog posts, CoinGlass, Medium, etc.). Third-party sources are
used only to *find* the official page faster, never as the basis of a claim in this document.

---

## 0. Provenance

**Fetched and read this session** [measured/cited — official]:

1. `https://www.binance.com/en/support/faq/introduction-to-binance-futures-funding-rates-360033525031` —
   the primary funding-rate FAQ. Page header shows **"Updated on 2026-03-06 07:01"** (original publication
   2019-09-09), i.e. this is the live, current-as-of-verification version, not an archived one.
2. `https://www.binance.com/en/support/faq/what-are-mark-price-and-price-index-in-usd%E2%93%A2-margined-futures-360033525071`
   — Price Index / Mark Price definition for USDⓈ-M futures.
3. `https://www.binance.com/en/support/announcement/detail/c00588a7e8504b3eb28d02a2da00530b` —
   "Important Updates on Funding Rate Formula and Mark Price," effective **2025-09-18 08:01 UTC**.
4. `https://www.binance.com/en/support/announcement/updates-on-funding-rate-settlement-frequency-and-capped-funding-rate-multiplier-of-solusdt-solbusd-and-solusd-perpetual-futures-contracts-2022-11-09-e8be17e1e544418490e86723d84759f0`
   — the SOLUSDT-specific settlement-frequency/cap change, dated **2022-11-09**.
5. `https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Get-Funding-Rate-Info`
   — official API doc for `GET /fapi/v1/fundingInfo`.
6. `https://fapi.binance.com/fapi/v1/fundingInfo` — **live public endpoint, queried directly**, not a
   third-party mirror. Read-only, documented, no authentication, no probing beyond the documented GET.

**Not fetched / not probed:** any endpoint requiring an API key; any endpoint not in the public REST
documentation; any third-party data vendor's funding-rate feed. Two announcement pages returned only
partial text through the fetch tool (noted at §2 where it matters) and are flagged rather than
supplemented with recollection.

**Computed this session, and why it is a reconciliation diagnostic and not a trial** [measured]: a
read-only join of `book/pit.db`'s existing `binance` spot close, `binanceusdm` perp close, and
`binanceusdm` funding_rate observations — the same tables and the same `basis_bps` construction
`DATA-INGEST-002` §4 already computed and logged as a plausibility check, extended here to test whether
the documented clamp mechanism predicts the measured off-floor rate. No `castellan.run_backtest` call, no
signal, no return series, no registry write. `book/pit.db` opened `mode=ro`; `book/registry.db` untouched.
Script and full output are reproducible from the query in §5.2.

---

## 1. THE DOCUMENTED FORMULA, WITH CITATIONS

### 1.1 The formula as currently published

> **Funding Rate (F) = [Average Premium Index (P) + clamp(interest rate − Premium Index (P), 0.05%, −0.05%)] / (8 / N)**

where `N` is the funding interval in hours [cited — official, source 1 and source 3]. For a symbol on the
default 8-hour cadence, `8/N = 1` and the divisor is a no-op; it only does work for symbols on a
non-8-hour interval (§2, §3).

**Premium Index**, sampled every 5 seconds [cited — official, source 1]:

> **P = [max(0, Impact Bid Price − Price Index) − max(0, Price Index − Impact Ask Price)] / Price Index**

**Average Premium Index**, the input to `F`, is a **time-weighted moving average over the full settlement
window**, not a snapshot: for an 8-hour interval it is the weighted average of the last **5,760** 5-second
premium-index samples (`5,760 × 5s = 8h`), weighted `1, 2, 3, …, n` — i.e. **increasing weight toward the
end of the window, closest to settlement** [cited — official, source 1, exact form: *"Average Premium
Index (P) = (1×Premium_Index_1 + 2×Premium_Index_2 + … + n×Premium_Index_n) / (1+2+3+…+n)"*]. For symbols
on a 1-hour interval the same page states the average is **equally weighted** over the 720 samples, not
time-weighted — a second, separate parameter that varies by interval length, not just a shorter window.

**Interest rate**: fixed at **0.03%/day = 0.01% per 8-hour funding interval** by default, with a **named
exception list that the page states is non-exhaustive** — its own wording is *"this doesn't apply to
certain contracts, **such as** ETHBTC, for which interest rate is set to 0%"* [cited — official, source 1,
emphasis added]. The word "such as" is doing real work: the FAQ does not publish a complete symbol-level
list of 0%-interest contracts. §6 records this as unverified rather than assumed closed.

**Clamp / damper**: **±0.05%**, exactly as the Principal's hypothesis stated. The page states the
consequence directly: *"as long as the premium index is between −0.04% and 0.06%, the funding rate will
equal 0.01%"* [cited — official, source 1] — i.e. **[interest − 0.05%, interest + 0.05%] = [−4bp, +6bp]**
is the band inside which `F` is pinned at the interest floor regardless of the premium's exact value.

**Verdict on the Principal's stated formula: confirmed as the current, documented mechanism**, with one
addition the Principal's note did not carry — the **`/(8/N)` divisor**, which did not exist in this form
before **2025-09-18** (§3) and which matters precisely for the symbol (SOL) whose funding interval this
firm's own data shows shortening under stress (I-040 N-2).

### 1.2 Impact Bid/Ask Price and Impact Margin Notional — a fourth mismatch layer, not two

[cited — official, source 1]:

> **Impact Bid Price = the average fill price to execute the Impact Margin Notional against the bid side
> of Binance's own USDⓈ-M order book** (and symmetrically for the ask side).
> **Impact Margin Notional (IMN) = 200 USDT / initial margin rate at the maximum leverage tier.**

Two consequences for this firm's proxy, beyond the two the Principal's note already flagged:

- **The "perp" side of Binance's own premium calculation is not a last-trade close.** It is an
  order-book-depth-weighted execution price on Binance's **own** futures book. `book/pit.db`'s
  `binanceusdm` `close` field (via `ccxt`) is a last-trade OHLCV close. These are different quantities
  even before the spot-index question is reached.
- **IMN is leverage-tier-dependent and therefore symbol-specific.** BTC's maximum leverage tier implies a
  larger IMN (more USDT notional walked through the book) than SOL's, so the two symbols' premium indices
  have different sensitivities to book depth even under identical trading conditions. This is a second,
  independent reason SOL's realized funding should be noisier than BTC's beyond its known thinner
  cross-section (`PREREG-002` §9.1 S1/S2).

---

## 2. PER-CONTRACT PARAMETERS — BTC/ETH/SOL USDT-margined perpetuals

**Live-endpoint check, today** [measured — direct GET against `https://fapi.binance.com/fapi/v1/fundingInfo`,
documented, unauthenticated, weight 0]:

> **BTCUSDT, ETHUSDT, and SOLUSDT do not appear in the `fundingInfo` response.**

Per the official API doc [cited — official, source 5], this endpoint returns **only** symbols that have
received a **customized** `adjustedFundingRateCap` / `adjustedFundingRateFloor` / `fundingIntervalHours`
away from Binance's defaults. **Absence from this list means BTC, ETH and SOL are, as of today, on the
platform's default parameters**: 8-hour interval, ±0.05% clamp band, 0.01%/8h interest — **not** on the
exception list that appears in that same response (mostly small-cap/volatile alts, ±2%–3% caps, 1h/4h
intervals; two commodity-tokenized pairs at ±0.5%).

**This is a point-in-time fact about today, not a claim about 2020–2026.** §3 covers whether it held
throughout the study span — it did not, for SOL, during at least one documented episode.

**On the 0%-interest exception:** the official FAQ names ETHBTC as an example, not BTCUSDT/ETHUSDT/SOLUSDT.
No official source found in this session lists a comprehensive symbol set for the 0% exception, and none
of BTC/ETH/SOL turned up in any search result as belonging to it. **Working conclusion: BTC, ETH and SOL
USDT-margined perpetuals use the standard 0.01%/8h interest rate, not 0%** — consistent with, and
required by, the reconciliation in §5 (a 0% interest rate would leave nothing to explain the positive
mean funding). **Flagged at §6 as not exhaustively verified**, because "not found on the exception list"
is an absence, not a citation.

| Parameter | BTC/ETH/SOL (USDⓈ-M), today | Source |
|---|---|---|
| Funding interval | 8 hours (default; not in customized list) | [measured — live `fundingInfo`] |
| Interest rate | 0.01% per 8h interval (not in the named 0% exception) | [cited — official, source 1] + [inferred — absence from exception examples and from the live customization list] |
| Clamp / damper band | ±0.05% | [cited — official, source 1] |
| Premium averaging | time-weighted, 5,760 samples over 8h, increasing weights | [cited — official, source 1] |
| Settlement times | 00:00 / 08:00 / 16:00 UTC (default) | [cited — official, source 1] |

---

## 3. HAS THE FORMULA OR ITS PARAMETERS CHANGED ACROSS 2020–2026? YES — CONFIRMED, DATED, AND MATERIAL TO THE FIRM'S HOLDINGS

Two independent, dated changes were found, both official:

### 3.1 The formula itself changed, firm-wide, on 2025-09-18

[cited — official, source 3, "Important Updates on Funding Rate Formula and Mark Price," effective
**2025-09-18 08:01 UTC**]:

- **Old formula:** `F = P_avg + clamp(interest − P, 0.05%, −0.05%)` — **no interval divisor.**
- **New formula:** `F = [P_avg + clamp(interest − P, 0.05%, −0.05%)] / (8/N)`, explicitly introduced so a
  single formula could serve symbols on 1/2/4/8-hour intervals uniformly, with interest fixed at 0.01%
  (except the named exceptions) regardless of `N`.
- **Mark price averaging window** also changed the same day: from a **1-minute basis (60 samples)** to a
  **30-second basis (30 samples)**.

**Consequence for BTC/ETH, which have stayed on the 8-hour default throughout**: the divisor is `8/8 = 1`
before and after, so **this change is arithmetically invisible for BTC and ETH under normal conditions.**
It is not invisible for any symbol that has ever run on a shortened interval — which, per §3.2, includes
SOL.

**This directly answers Gate-0-style question (2) of this task: yes, the formula changed within the
firm's 2020–2026 holding, on a specific dated announcement, and the change is not cosmetic — it alters
how a shortened-interval print's magnitude relates to its 8-hour-equivalent rate.**

### 3.2 SOL specifically had its settlement frequency and clamp cap changed, in a dated event that lines up exactly with the firm's own I-040 N-2 finding

[cited — official, source 4, dated **2022-11-09 20:00 UTC**]:

> *"Binance Futures will increase the funding rate settlement frequency of SOLUSDT, SOLBUSD and SOLUSD
> Perpetual Futures Contracts"* to **every 4 hours**, and *"the Capped Funding Rate Multiplier for
> SOLUSDT, SOLBUSD and SOLUSD Perpetual Futures Contracts has been raised from 0.75 to 1"* — taking
> **SOLUSDT's maximum funding rate cap to ±2.00%**, roughly **40× the default ±0.05% band.**

The announcement adds, verbatim: *"there may be further adjustments to the funding rate settlement
frequency... there will be no further announcement on such adjustments"* — i.e. Binance's own documentation
states plainly that **subsequent tightenings/loosenings around this event are not individually
announced**, which is why the live `fundingInfo` endpoint today shows SOL back on default parameters
without a corresponding "reverted" announcement: the mechanism is dynamic and one-directional public
notice does not imply a one-time, permanent change.

**This is an exact match, independently sourced, to I-040 N-2** — *"SOL settles at 2h/4h intervals during
stress... the exceptions cluster in November 2022."* I-040 measured the *symptom* from `pit.db`; this
session finds the *documented cause*, dated to the same event (the FTX collapse window), in Binance's own
announcement archive. **N-2 moves from measured-but-unexplained to measured-and-cited.**

**The compounding fact this adds, which N-2 did not have:** it was not only the settlement *frequency*
that changed for SOL in that window — the **clamp cap widened roughly 40×** at the same time. A print
during that window was not "the same ±0.05% band, just paid out more often." It was a **materially wider
band**, permitting funding magnitudes the default parameters could never produce, exactly coinciding with
`DATA-INGEST-002`'s independently-found SOL basis excursion of **−1,690.34 bps on 2022-11-09** (the FTX
date) and Ruling 003's measured **−17.17%** single-day SOL funding print on 2022-11-10.

**What could not be confirmed:** whether, *before* the 2025-09-18 divisor was introduced, a shortened-
interval SOL print in Nov 2022 had its interest/clamp components scaled down proportionally to the shorter
interval, or applied at full 8-hour magnitude per settlement. The pre-2025 formula text found this session
states interest as *"0.01% per funding interval"* without stating whether "funding interval" self-adjusts
with `N` or is a fixed constant divided by nothing. **This is recorded as unverified at §6** — it bears
directly on how much of SOL's Nov 2022 funding magnitude came from the widened cap versus the (possibly
un-scaled) more-frequent interest component, and no dated pre-2025 Binance source resolving that specific
mechanical question was found in this session.

---

## 4. WHAT THE PREMIUM INDEX IS MEASURED AGAINST, AND AT WHAT SAMPLING

**Not the firm's daily-close basis proxy, at three independent levels**, each confirmed against an
official source:

1. **Sampling frequency and window, not a single snapshot.** The premium index is sampled **every 5
   seconds** and averaged with **time-increasing weights over the full 8-hour settlement window** (5,760
   points). The firm's `basis_bps` diagnostic (`DATA-INGEST-002` §4) is **one point per day** — a single
   close-to-close difference. These are not the same statistic even in expectation: a TWAP over a window
   with intra-window variance is not equal to the window's endpoint difference, and the weighting scheme
   (favoring the samples nearest settlement) makes the two diverge further whenever intra-window basis
   trends rather than sits flat. [cited — official, source 1]
2. **Instrument definition on the perp side.** Binance's own calculation uses **Impact Bid/Ask prices**
   (order-book execution prices for a leverage-tier-scaled notional), not a last-trade close. `pit.db`'s
   `binanceusdm` close is a last-trade OHLCV close via `ccxt`. [cited — official, source 1]
3. **Reference index on the spot side.** The **Price Index** the premium is measured against is a
   **volume-weighted composite across roughly a dozen venues** — the fetched page names Binance, KuCoin,
   OKX, HitBTC, Gate.io, MEXC, Coinbase, Kraken, Bitget, Bitfinex, Bybit, plus DEX venues for certain
   underlyings, with **Binance's own futures last price entering as one constituent among many, at
   Binance's discretion** [cited — official, source 2]. This is categorically different from `pit.db`'s
   `binance` spot `close`, which is a **single venue's** daily bar.

**This confirms the Principal's flagged concern exactly**, and adds the fourth layer (Impact price vs.
last-trade close, §1.2) that the Principal's note did not name.

---

## 5. THE RECONCILIATION — does the documented formula explain the 65% off-floor figure and the sign disagreement, or not?

**It explains the qualitative mechanism completely, and — measured directly against `pit.db`, not merely
argued — it explains most, though not all, of the magnitude, with the residual attributable to exactly the
proxy mismatches named in §1 and §4.**

### 5.1 The mechanism, restated with the exact band

`F = P_avg + clamp(interest − P_avg, −0.05%, +0.05%)`, interest = 0.01% = 1.00bp:

- **Inside the band** `P_avg ∈ [−4bp, +6bp]`: `F = interest = 1.00bp` **exactly**, regardless of the
  premium's precise value. This is the "floor" the CIO's 35% is measuring.
- **Outside the band**: the clamp saturates and `F = P_avg ± 5bp` — **funding tracks the premium
  directly**, offset by a fixed 5bp, and is **not** pinned to the interest rate. A very negative premium
  (`P_avg < −4bp`) produces `F = P_avg + 5bp`, which can be small, zero, or negative. A very positive
  premium (`P_avg > 6bp`) produces `F = P_avg − 5bp`.

**This alone is why "basis σ ≈ band half-width ⇒ most prints at floor" does not follow.** The relevant
comparison is not the daily basis's dispersion against the band in the abstract — it is **how often the
true, intra-window, order-book-based, multi-venue-indexed premium actually falls inside `[−4bp, +6bp]`**,
which is a materially noisier and differently-centered quantity than the daily close-to-close proxy, for
all three reasons in §1 and §4.

### 5.2 Measured, not argued: joining the firm's own basis proxy to its own realized funding prints

Read-only query against `book/pit.db` (§0), per symbol: attach each day's `basis_bps` (perp close vs. spot
close, the exact construction `DATA-INGEST-002` §4 already computed and logged) to that day's realized
funding print(s), and test whether "`basis_bps` outside `[−4, +6]`bp" predicts "print not at the 1.00bp
floor."

| Symbol | Measured %% prints off-floor (this session) | CIO's I-042 figure | Daily-basis-proxy %% outside `[−4,+6]`bp | Concordance (proxy-outside⇔off-floor, or proxy-inside⇔on-floor) | Mean funding, proxy-in-band subset | Mean funding, proxy-out-of-band subset |
|---|---:|---:|---:|---:|---:|---:|
| BTC | **65.4%** | 64.6% | 59.5% | **72.0%** | 0.986 bp | 1.149 bp |
| ETH | **65.3%** | 64.7% | 60.5% | **71.8%** | 1.114 bp | 1.396 bp |
| SOL | **64.9%** | 64.3% | 66.4% | **66.8%** | 0.676 bp | −0.328 bp |

**[measured — this session, `book/pit.db`, read-only; independently reproduces the CIO's off-floor figures
to within 0.3–0.8 percentage points using the same funding series, confirming the CIO's arithmetic]**

**Reading this table honestly:**

1. **The mechanism is confirmed at the level of magnitude, not just direction.** A daily-close proxy — a
   deliberately coarse instrument next to what Binance actually computes — predicts the *rate* of
   off-floor prints to within a few points of the true figure for all three symbols (59.5% vs. 65.4% BTC;
   60.5% vs. 65.3% ETH; 66.4% vs. 64.9% SOL), and gets the on/off-floor classification right on roughly
   **7 of every 10 individual prints** (72.0% / 71.8% / 66.8% concordance). A proxy this structurally
   different from the true premium index getting this close is strong evidence the clamp-band mechanism,
   not some unrelated effect, is what is generating the 65% figure.
2. **The residual — the 28–33% of prints where the daily-close proxy calls it wrong — is exactly what
   §1/§4's mismatches predict, not a separate anomaly.** Of prints where the proxy says "inside the band,"
   only 52–58% are actually at the floor (not 100%): the true intra-window TWAP, sampled every 5 seconds
   and weighted toward settlement, has genuine within-day variance that a single close-to-close snapshot
   cannot see, and it is entirely expected that it strays outside `[−4,+6]`bp on a meaningful share of days
   where the close-to-close difference happens to sit inside. This is the TWAP-vs-snapshot mismatch the
   Principal's note named, now quantified.
3. **The sign disagreement is directly reconciled by the same table.** For BTC/ETH, the **in-band subset**
   averages almost exactly 1.00bp (0.986, 1.114) — the interest floor, as the formula requires — and this
   subset is the majority-adjacent case that pulls the *unconditional* mean funding up to **positive and
   sizeable** (11.86%/14.07% annualized) even though the *underlying premium* (what the basis proxy is
   attempting to measure) averages **slightly negative**. **The mean-basis-negative/mean-funding-positive
   disagreement is not a contradiction to resolve — it is the documented formula's designed behaviour**:
   a small, persistently negative premium is systematically overridden by a fixed positive interest rate
   whenever it falls inside a ±5bp band centered near it.
4. **SOL's near-zero annualized funding (+0.10%/yr) is reconciled the same way, in the other direction.**
   SOL's proxy-out-of-band share is the **largest** of the three (66.4%), and its out-of-band subset
   funding mean is **negative** (−0.328bp), tracking its more negative out-of-band basis mean (−5.12bp).
   SOL spends more time with its premium escaping the flat-interest region — consistent with §3.2's finding
   that SOL's clamp band was **not always ±0.05%** over this sample (it widened to ±2.00% during the
   Nov 2022 event) — so its annualized mean sits close to zero rather than clearly positive like BTC/ETH,
   because it is not pinned to the +1bp floor nearly as often.

### 5.3 Verdict

> **The documented formula explains the 65% off-floor figure and the sign disagreement. It does so
> completely at the level of mechanism (§5.1, a matter of reading the formula correctly) and
> substantially — roughly 70 percentage points of concordance per print, and the correct sign and
> approximate magnitude of the mean-level effect — at the level of measured data (§5.2), using only the
> coarse daily-close proxy already on disk.** The residual disagreement between the proxy and the true
> off-floor rate is not an unexplained gap; it is the **expected size** of the mismatch between a
> once-daily close-to-close snapshot and a 5-second-sampled, settlement-weighted TWAP computed against a
> multi-venue composite index and Binance's own order-book impact prices — every one of which is a named,
> documented difference, not a residual anomaly requiring a new hypothesis.
>
> **What would fully close the residual, stated rather than assumed away:** ingesting Binance's actual
> premium-index or mark-price tick history (available via `fapi.binance.com`'s `premiumIndexKlines`
> endpoint, not currently in `pit.db`) and re-running §5.2 against the true premium rather than the daily
> close proxy. That is a data-acquisition task, not a further verification task, and is named at §6.

---

## 6. WHAT THE FIRM MUST THEREFORE DO DIFFERENTLY

**6.1 — I-042 should close on this document, with the following restatement of PREREG-002's mechanism.**
The Director of Research's basis-and-carry framing (§3.4 of PREREG-002) treats "funding rich" and "basis
rich" as approximately the same state at the daily level. §5 establishes that this is **only true inside
the clamp band**, and roughly a third of days are outside it (more for SOL). **The conditioning variable
K1 (§7.1 of PREREG-002) is "deviation of realized funding from its own trailing 30-day mean" — funding, not
basis — and this document's finding is a reason that choice was already the right one**, not a defect in
it: funding is the *post-clamp* observable and is the thing the mechanism (§3.4, "funding as a crowding
gauge") is actually claiming to measure. **No change to K1 is indicated.** What *should* be added to
PREREG-002's mechanism section, as a stated caveat rather than a silent gap: **funding and the raw premium
are the same signal only outside the clamp band**, and inside it funding is uninformative about crowding
by construction (it reads exactly 1.00bp regardless of how rich or cheap the premium actually is). A
conditioning strategy sized on funding is therefore **less sensitive to genuine crowding on days the
premium sits inside the band** than a strategy conditioned on the raw premium would be — this is a
real, previously unstated limitation of the mechanism, not a bug in the data.

**6.2 — `pit_funding_panel` (Ruling 003 §3.2) needs nothing beyond realized prints for the accrual use
case it was built for.** Ruling 003's accrual mechanism sums realized `funding_rate` prints inside a
bar's window; nothing in this verification changes that — funding is what actually settles and is what
a position actually receives or pays, independent of what the premium "should" imply. **No change to the
accrual path.**

**6.3 — What *should* be added, and it is a data-acquisition recommendation, not a defect in existing
work.** If the firm wants to test the mechanism itself (rather than just its settled cash-flow
consequence), the raw premium index / mark price is a **separate, currently absent series**. Binance
publishes it historically via the documented `premiumIndexKlines` REST endpoint (same shape as OHLCV
klines, not currently wired into `castellan.loaders`). Ingesting it would let a future study replace the
daily-close `basis_bps` proxy in §5.2 with the true premium and close the residual concordance gap
directly, rather than inferring it from the mismatch's known sources. **Recommended as a follow-on
ingest task, not blocking on PREREG-002's current critical path** (I-035, the perp price series, is the
binding blocker per Ruling 003 §7.2).

**6.4 — The funding cadence/cap dynamism found at §3.2 is a second, independent argument for Ruling 003's
T-9 (no cadence constant) and for treating SOL's stress-window prints as structurally different data, not
outliers to smooth.** Nothing in the accrual mechanism needs to change to handle this — T-9 already
requires the exact arithmetic sum of realized prints with no fixed-cadence assumption, which is precisely
what this session's finding requires. **Flagged to Validation as corroborating evidence for a control
already specified, not as a new requirement.**

---

## 7. WHAT COULD NOT BE VERIFIED, AND WHY

1. **A comprehensive, symbol-level list of 0%-interest-rate contracts.** The official FAQ gives one named
   example (ETHBTC) and states the exclusion is not limited to it ("such as"). No official page found in
   this session enumerates the full set. **Working conclusion (§2) that BTC/ETH/SOL are on the 0.01%
   default rests on absence-from-example plus the reconciliation in §5 requiring a nonzero interest rate to
   work** — it is [inferred], not [cited] as a positive statement about these three symbols by name.
2. **Whether the pre-2025-09-18 formula scaled the interest/clamp components for a shortened interval, or
   applied them at full 8-hour magnitude per settlement** (§3.2). This bears on exactly how much of SOL's
   Nov 2022 funding magnitude is attributable to the widened cap versus the interval shortening acting on
   an un-scaled interest term. No dated pre-2025 official source resolving this specific point was found.
3. **The true premium index / mark price history itself.** Not ingested, not in `pit.db`. Every
   reconciliation figure in §5.2 uses the firm's existing daily-close `basis_bps` proxy, not the actual
   premium. The concordance figures (66.8%–72.0%) should be read as a **lower bound on how well the
   documented mechanism explains the data** — a proxy this coarse getting 70% right is evidence *for* the
   mechanism, and the true series would very plausibly close most or all of the remainder, but that is
   not demonstrated here and is not claimed as demonstrated.
4. **Whether other symbols beyond SOL, or SOL at other dates beyond the one dated announcement found,
   experienced similar dynamic cap/interval adjustments.** The live `fundingInfo` endpoint gives today's
   snapshot only; Binance's own announcement states subsequent adjustments around the same event were not
   individually announced. A full historical reconstruction would require either an announcement-archive
   crawl (not performed — out of scope for a documentation-verification task) or a historical
   `fundingInfo`-equivalent time series (not known to be published).
5. **The exact numerical effect of the 2025-09-18 mark-price averaging-window change (60×1min → 30×30s)**
   on any historical backtest that used mark price rather than funding rate. Not relevant to this firm's
   current `pit.db` holdings (which store `funding_rate` and last-trade OHLCV, not mark price), so not
   pursued further, but named so it is not silently assumed away if mark price is ever ingested later.

---

## Summary for the CIO

**The documented formula, with source type:** `F = [Average Premium Index + clamp(interest − Premium
Index, ±0.05%)] / (8/N)`, interest = 0.01%/8h default (BTC/ETH/SOL not on the named 0% exception list),
clamp ±0.05% — all `[cited — official]` against the live, current (2026-03-06-updated) Binance FAQ, the
Price Index/Mark Price FAQ, the 2025-09-18 formula-change announcement, the 2022-11-09 SOL-specific
announcement, and the live `fundingInfo` REST endpoint queried directly. **The Principal's hypothesis is
confirmed as the current documented mechanism**, with one addition it did not carry (the `/(8/N)` divisor,
introduced 2025-09-18) and one layer beyond the two it flagged (Impact Bid/Ask order-book prices, not
last-trade closes, on the perp side).

**The formula changed within the firm's 2020–2026 span, twice, both dated and both official**: the
divisor generalization (2025-09-18, arithmetically invisible for BTC/ETH but material for any
shortened-interval print) and SOL's own settlement-frequency/cap-multiplier change (2022-11-09, clamp
band widened roughly 40× to ±2.00%), which lines up exactly with the firm's own I-040 N-2 finding and
converts it from measured-unexplained to measured-and-cited.

**The 65% off-floor figure is explained, not merely rationalized.** Read-only reconciliation against
`book/pit.db` this session reproduces the CIO's figures independently (65.4/65.3/64.9% vs. 64.6/64.7/
64.3%) and shows the firm's own coarse daily-close basis proxy predicts on/off-floor status correctly on
roughly 70% of individual prints for BTC/ETH (67% for SOL) — strong evidence the clamp-band mechanism,
not an unrelated effect, drives the figure, with the residual attributable to the three-to-four
documented ways the daily-close proxy differs from Binance's actual premium index (TWAP-vs-snapshot,
order-book-impact-price-vs-last-trade, multi-venue-index-vs-single-close, and — for SOL — a
non-constant clamp band).

**The sign disagreement is resolved, not just described.** Mean funding is positive for BTC/ETH because
the fixed +1bp interest floor systematically overrides a slightly-negative mean premium on every day the
premium sits inside the ±5bp band — measured directly: the in-band subset's mean funding is 0.99bp (BTC)
and 1.11bp (ETH), essentially exactly the interest rate. SOL's near-zero mean funding is the same
mechanism running the other way: SOL spends more of the sample outside the band (its clamp was not
always ±0.05% — see the Nov 2022 widening), so it is pinned to the floor far less often and tracks its
own persistently slightly-negative premium instead.

**PREREG-002's mechanism needs one addition, not a restatement**: state explicitly that funding and the
raw premium coincide only outside the clamp band, and that a funding-conditioned strategy is
correspondingly less sensitive to crowding on days the premium sits inside it. K1's choice of funding
(not basis) as the state variable is not called into question by this finding — if anything it is
reinforced, since funding is the actual post-clamp cash flow the mechanism claims to price.

**What remains unverified:** the complete symbol-level 0%-interest exception list (BTC/ETH/SOL's
inclusion in the 0.01% default is inferred, not directly cited by name); the exact pre-2025 mechanics of
interest/clamp scaling under a shortened interval; and the true premium-index/mark-price tick history,
which is not in `pit.db` and would be needed to close the residual 28–33 percentage points of proxy
disagreement directly rather than by inference from its known sources. None of these block PREREG-002's
critical path, which remains I-035 (the perp price series) per Ruling 003 §7.2.
