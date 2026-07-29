# DATA-PROBE-001 — Polymarket Order-Book Availability

**Seat:** Head of Data & Infrastructure
**Date:** 2026-07-28
**Status:** COMPLETE — capability probe only. No ingestion performed, no rows written to `book/pit.db`, no backtest run, no pre-registration, no vault action, no git commit.
**Scope authority:** Principal-authorised network access to Polymarket public endpoints and public on-chain/subgraph explorers, this task only. No authenticated sources, no scraping behind a login.
**Answers:** §7 step 1 of `research/DATA-SPEC-polymarket-usable-history.md`; the condition-precedent named in `research/REDTEAM-001-agenda-and-forward-lag.md` §B.4–B.5; blocks on `logs/ISSUE_LOG.md` I-004, I-023, I-024 do not change as a result of this probe (those remain open on their own terms) but this probe determines whether they are reachable at all.

House rule 6 throughout: **[measured]** = an actual call made this session with the response observed · **[cited]** = external source read this session, not executed · **[inferred]** = reasoned from measured/cited facts · **[assumed]** = unverified premise, flagged.

---

## 1. The question, and why it gates everything downstream

The data spec's own criteria T2 (two-sided market) and T4 (depth at intended size) both require **historical order-book state** — not trade prints, not aggregate volume. If Polymarket's public API and on-chain surface expose only current live book state, then:

- T4 has **no proxy at all** (the spec is explicit: "no volume-only proxy for T4 is proposed" — depth-at-a-price-band is not recoverable from trade prints without misrepresenting what was actually resting).
- Depth-at-size, and therefore Charter §4.4's **capacity** criterion (≥10× intended allocation at target net Sharpe), becomes **unevaluable**.
- An unevaluable Gate 1 criterion is not a soft "unconfirmed" — under Amendment A1, a criterion the harness cannot compute is **INSUFFICIENT-DATA, never PASS**. Gate 1 requires every criterion to pass.

That makes this the single cheapest possible test of the forward-lag family's admissibility: a documentation-and-endpoint check, before one row is ingested, that can moot the entire I-004 span question by making it irrelevant.

---

## 2. The answer

**Historical order-book depth snapshots are NOT available from any confirmed, officially-documented, public Polymarket source. Partially available from an unconfirmed, undocumented endpoint that this probe declined to call. NOT reconstructible from on-chain data at all, structurally.**

### 2.1 Official documented API — live state only

**[measured]** `GET https://clob.polymarket.com/book?token_id=<id>` (docs: `docs.polymarket.com/api-reference/market-data/get-order-book`) — accepts a single parameter, `token_id`. No time-range, timestamp, or "as of" parameter exists in the spec. The response carries a `timestamp` field describing when *that* snapshot was taken — not a query parameter for retrieving a past one. This is a current-state-only endpoint by construction, confirmed by reading the API reference page directly.

**[measured]** `GET https://clob.polymarket.com/prices-history?market=<id>&interval=...&fidelity=...` (docs: `docs.polymarket.com/api-reference/markets/get-prices-history`) — returns a time series of `{t, p}` price points (aggregated **price**, not book depth or bid/ask levels), down to 1-minute fidelity by default. No bid/ask, no size, no depth. This is the only historical time-series endpoint in the officially documented market-data surface.

**[measured]** `docs.polymarket.com/quickstart/reference/endpoints` (the full documented endpoint index) and `docs.polymarket.com/llms.txt` (the complete documentation index) — neither lists any endpoint for historical order-book snapshots. The market-data category lists only "Get order book" / "Get order books" (current state) and price/kline/trade history endpoints. **No historical book-depth endpoint appears anywhere in Polymarket's official documentation.**

### 2.2 An undocumented endpoint exists in the wild — not probed, per the hard constraint

**[cited, not measured]** Third-party developer sources — a GitHub issue on the `nautilus_trader` project (`nautechsystems/nautilus_trader#3635`) and independent community write-ups — reference `GET https://clob.polymarket.com/orderbook-history`, accepting `asset_id`, `startTs`, `endTs`, `limit`, `offset`. The GitHub issue reports the endpoint **stopped producing new snapshots around 2026-02-20 ~20:00 UTC** (queries for windows after that return `{"count": 0, "data": []}`), while data from before that date is reported still retrievable.

**This endpoint does not appear anywhere in the official documentation** (checked directly against the endpoint index and `llms.txt`, §2.1 above). Per the task's explicit instruction — *"if an endpoint is undocumented or you are unsure whether it is public, do not probe it"* — **I did not call it.** I cannot confirm from this session: whether it is intended for public use, whether it is stable, what its true retention span or granularity is, whether the "stopped Feb 2026" report is accurate or current, or when it started (i.e., how far back its history goes). This is reported as an open unknown, not folded into the answer as if confirmed.

### 2.3 Third-party commercial resellers claim to sell it — with a load-bearing detail

**[cited]** Several commercial data vendors (PolymarketData, PolyHistorical, PMData, Telonex, DepthFeed) market historical L2 order-book depth archives for Polymarket, at claimed resolutions from 1-minute down to sub-second. These are paid, out of scope for this firm without Principal approval (a new paid data source is the Principal's decision alone, per this seat's charter). **One vendor's own marketing copy states its archive begins "from August 2025 onward"** [cited — vendor's own site]. That is the load-bearing fact, not the existence of the vendors: **even the most data-forward commercial archiver active in this space claims roughly eleven months of book-depth history as of today (2026-07-28)**, not years. If systematic book-depth capture had existed further back, a vendor competing on data depth would be advertising it. Its absence from their own claims is circumstantial but consistent evidence that continuous book-depth archiving of Polymarket is a recent (≈2025) phenomenon, not a multi-year one — **[inferred]**, and flagged as inferred from vendor marketing rather than confirmed.

### 2.4 On-chain route — structurally absent, not merely unretained

**[measured]** `docs.polymarket.com/concepts/order-lifecycle`: orders are EIP-712-signed messages. A client "creates an order object," the "signed order is submitted to the Central Limit Order Book (CLOB) operator" — off-chain. "When orders match, the operator submits the trade to the blockchain," at which point the Exchange contract verifies signatures and transfers tokens, atomically. **Unfilled/resting orders are never submitted to the chain at all** — there is no on-chain event for order placement, only for matched settlement.

**[measured]** `raw.githubusercontent.com/Polymarket/polymarket-subgraph/main/orderbook-subgraph/schema.graphql` — the official subgraph's entities are `MarketData`, `OrderFilledEvent`, `OrdersMatchedEvent`, `Orderbook`, `OrdersMatchedGlobal`. Every one of them represents **executed fills or trade-count/volume aggregates**. None represents a resting order, a price level, or depth at a point in time.

**Conclusion: order-book depth is not reconstructible from on-chain data under any retention policy, because it was never written on-chain in the first place.** This is a permanent structural property of Polymarket's hybrid off-chain-match / on-chain-settle architecture (the same architecture as many other hybrid CLOBs), not a retention gap that a longer archive would fix. On-chain data can answer "what traded, at what price, when" and "how did each condition resolve" — never "what was resting in the book."

---

## 3. Consequences for T2, T4, and §4.4 capacity

| Criterion | Status | Basis |
|---|---|---|
| **T2 — two-sided market** | **Not directly measurable historically.** Falls to the data spec's own pre-specified fallback: a trade-print proxy (≥1 trade on both sides of the prevailing mid within the day). **This proxy is confirmed retrievable** — `data-api.polymarket.com/trades` returned real per-trade records (price, size, timestamp, side, wallet) for a live CLOB-era market [measured, §4 below]. The spec's own stated bias direction stands: this **overstates** tradability, and any T2 count from it is an upper bound, not a measured value. |
| **T4 — depth at intended size** | **Confirmed unmeasurable**, exactly as the spec anticipated as its fallback case — this probe converts that from `[assumed]` to `[measured]`. No confirmed public historical depth source exists (§2.1); the one candidate that might have provided it is undocumented and was correctly not probed (§2.2); on-chain reconstruction is structurally impossible, not merely unretained (§2.4). Per the spec's own rule, T4 must be reported as **unmeasurable, not proxied** — no volume-only substitute is admissible for depth-at-a-price-band. |
| **Charter §4.4 capacity (≥10× intended allocation at target net Sharpe)** | **Unevaluable.** Capacity is a function of resting depth at the price the strategy needs; T4 unmeasurable makes it unmeasurable by direct implication, with no fallback path visible in any surface checked this session. Under Amendment A1, an uncomputable Gate 1 criterion reads **INSUFFICIENT-DATA, never PASS**. |

This is decisive rather than merely inconvenient: Gate 1 requires **every** criterion to pass. One structurally unevaluable criterion is sufficient to block the family from ever reaching Gate 1 on this data, independent of anything the I-004 span/continuity measurement would find. The span question is not mooted in the sense of being answered — it is mooted in the sense of no longer mattering to the outcome.

---

## 4. Survivorship: are resolved and delisted contracts enumerable?

**Partially confirmed; the harder half of the question is unresolved by design, not by omission.**

**[measured]** `GET https://gamma-api.polymarket.com/markets?closed=true&limit=5` returned real, dated markets from **2020**: "Will Joe Biden get Coronavirus before the election?" (closed, end date 2020-11-04), an Airbnb IPO market, a Supreme Court confirmation market, a Kardashian–West divorce market, and a Coinbase IPO market — all `closed: true`, with `conditionId` and `clobTokenIds` populated. **A live query issued in 2026 does enumerate markets resolved six years earlier.** This is real evidence against the naive worst case (that only currently-active markets are listed at all).

**What this does not establish, and cannot establish by construction.** `closed=true` is Polymarket's own live catalog's current view of its own history. It tells you what the catalog *still contains*, not what it *ever contained and has since dropped*. A market that was fully **delisted** — removed from the catalog entirely, as opposed to marked closed/resolved — would be invisible to this exact same query, and there is no way to detect that absence from inside the live API: you cannot enumerate what a source does not list. This is the precise shape of the Devil's Advocate's Gate 0(5) point, and this probe confirms rather than resolves it.

**The independent check that would resolve it — named, not performed.** The Devil's Advocate proposed the on-chain **append-only condition registry** (the `ConditionalTokens` contract's `ConditionPreparation` / resolution events on Polygon) as an independent universe source that cannot retroactively drop a market. Diffing that on-chain enumeration against the Gamma API's current listing would produce a **measured survivorship rate** — count present on-chain but absent from the live catalog. **This probe did not perform that diff.** It requires indexing the full history of on-chain condition-preparation events, which is a backfill-scale operation (potentially thousands of events across years), not the handful of sample calls this task authorised. It is the concrete next step if the family survives the T4/capacity blocker above; there is no point running it before that, since a family that cannot reach Gate 1 on the capacity criterion does not need its survivorship rate measured yet either.

**Answer to the stated question:** resolved contracts — yes, enumerable, confirmed to 2020. Delisted contracts (removed rather than closed) — **not determined**; the method to determine it is identified and not yet run.

---

## 5. Best available upper-bound proxy, and its bias direction

**[measured]** `GET https://data-api.polymarket.com/trades?market=<conditionId>&limit=5`, called against a live 2026 CLOB-era market ("Credible FDV above $100M one day after launch?"), returned five real trade records with `price` (0.96–0.999), `size` (10.09–801), Unix `timestamp`, `side` (BUY/SELL), and trader wallet identity. **This endpoint is real, public, and returns genuine per-trade data.**

**[measured]** The same call against a **2020-era** market (the Biden-COVID condition ID) returned an **empty result**. **[cited]** Polymarket's CLOB (the order-book trading engine this endpoint indexes) launched in **late 2022**, replacing an AMM/FPMM model used from the platform's 2020 start. This is consistent and not coincidental: **the trade-print proxy itself is left-censored at the CLOB's launch (~late 2022)**, regardless of how far back Gamma's market catalog goes. Pre-2022 platform history exists in the catalog but not in a form this proxy — or, by the same logic, any order-book concept at all — can reach.

**This is the best available upper bound on tradability, and the data spec already named its bias correctly before this probe ran:** a contract-day can show two-sided trade prints from a single opportunistic counterparty while the resting book was thin or absent between prints — exactly the liquidity a real market-making-style strategy could not have executed against. Any count built on it is an **upper bound**, reported as such, never blended into a 7-of-7-confirmed figure. This probe adds one new fact to that existing bias statement: the proxy's usable span is bounded above by late 2022, not by Polymarket's full platform age.

---

## 6. What this probe could not determine, and why

- **The undocumented `/orderbook-history` endpoint's true parameters, retention span, granularity, and current operational status.** Not probed, per the hard constraint on undocumented/uncertain-public-status endpoints. If Validation or the Principal wants this resolved, it requires either (a) a written ruling that probing it is authorised despite its undocumented status, or (b) direct outreach to Polymarket to ask whether it is a supported public surface — neither of which this task authorised.
- **Whether the "stopped producing snapshots ~2026-02-20" report is accurate, current, or attributable to a permanent shutdown vs. a temporary outage.** Third-party-reported, single source, not independently verified.
- **A measured survivorship rate (on-chain enumeration vs. live catalog).** Method identified (§4), not run — out of scope for a sample-call probe, and arguably moot until the T4/capacity blocker is resolved by the Principal or Validation.
- **Whether any paid vendor's archive, if the Principal approved the spend, would in fact extend depth history earlier than August 2025 or offer genuine (not self-reported) retention.** Not evaluated — this seat cannot add a paid source unilaterally, and none was purchased or trialed.
- **The exact total retention span of `/prices-history`** (price, not depth) — the documentation states granularity options but not a maximum lookback; not tested with a long-range query since it does not bear on the T4/depth question this task was scoped to answer.

---

## 7. Bottom line

**Historical Polymarket order-book depth is not available from any source this probe could confirm as public and documented.** It is not reconstructible from on-chain data under any circumstance, because resting orders never touch the chain — this is structural, not a retention limit. One undocumented endpoint and several paid resellers claim partial access, but the strongest concrete number obtained (vendor's own claimed start date) points to roughly eleven months of coverage at best, against a Charter requirement of four years and a full regime cycle. T4 is confirmed unmeasurable; §4.4 capacity is confirmed unevaluable; a trade-print upper-bound proxy for T2 exists and works but is left-censored at the CLOB's late-2022 launch.

---

*Head of Data & Infrastructure · Castellan Capital · 2026-07-28*
*Capability probe only. No data ingested, no backtest run, no pre-registration opened, no vault sealed, no commit made.*
