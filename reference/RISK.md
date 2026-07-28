# Castellan Capital — Book, Capital & Risk

*Extracted from `FUND_CHARTER.md` Part V. Owned by the Chief Risk Officer.*

## PART V — THE BOOK, CAPITAL, AND RISK

### 5.1 Standing limits (paper book)

| Limit | Value |
|---|---|
| Pod gross exposure | ≤ 4× trading level |
| Pod net exposure | −20% to +20% of trading level |
| Equity book beta to SPY | \|β\| ≤ 0.15 |
| Single-name concentration | ≤ 5% of trading level |
| Single-theme / correlated cluster | ≤ 15% of trading level |
| Liquidity floor | no position exceeding 15% of 20-day ADV; whole book liquidatable in ≤ 3 days at the 5%/day participation cap |
| Cross-pod correlation | flagged above 0.40, reviewed above 0.60 |
| Stress loss ÷ portfolio vol | capped per asset class by the CRO |
| Firm-level annualized vol target | 4–6% |

### 5.2 The drawdown ladder

Measured from the pod's high-water mark, on allocated trading level. **The formal tiers are the visible end of a process that starts much earlier.** A firm that only models hard triggers is modelling a fiction; real pods de-risk voluntarily well before Tier 3.

| Tier | Trigger | Procedure | Authority |
|---|---|---|---|
| **0 — Watch** | 1–2% from peak, or unusual vol/factor drift | Appears on the daily flag list. Informal note. No action required. | Risk |
| **1 — Soft warning** | 2.5% | CRO contacts the PM. PM explains what is happening and the plan. Largest losers reviewed position by position. Monitoring frequency increases. | CRO |
| **2 — Formal notice** | 4.0% | Written notice. PM submits a **written de-risking plan with dates**. Gross exposure reduction requested. Meeting with CRO and CIO. Post-mortem opened on the largest losing positions. | CRO |
| **3 — Mandatory de-risking** | 5.0% | **Trading level cut by 50%.** Limits halve with it, forcing liquidation. **Not appealable to the CIO.** Formal post-mortem required. | Automatic |
| **4 — Strategy closure** | 7.5% | Pod's strategy closed, book liquidated by Ops, strategy retired to the library with a written cause of death. | Automatic |

**Reset:** high-water mark based; the loss budget resets at the start of each calendar quarter (compressed from the industry's annual reset to fit the firm's operating tempo). Fable 5 must watch for and name the end-of-quarter behavioural distortion — a pod up on the quarter protecting it, a pod down on the quarter reaching — because that distortion is real and predictable.

**Second-order effects the firm must acknowledge rather than pretend away:**
- Stops force exits at adverse timing. The protocol that protects the firm harms the individual position. This is an accepted trade, not a bug.
- Conviction sizing versus concentration limits: **limits always win**. A PM's best idea will frequently be capped below what conviction implies.
- Near a trigger, PMs manage to the threshold rather than to the opportunity. Expect it; name it when it happens.

### 5.3 Capital and compute allocation

Reviewed **monthly**, at the Capital & Risk Committee. **Capital** reallocation is proposed by Fable 5 and requires the Principal's approval. **Compute** reallocation is Fable 5's to decide, but must be stated with its rationale in the Monthly Letter.

**Allocation grows on:** realized idiosyncratic (factor-residual) Sharpe over rolling 30/90-day windows; low correlation to the rest of the book; demonstrated capacity with modelled slippage holding as size scales; disciplined risk usage — consistently *near*, not over, budget; drawdown recovery behaviour.

**Allocation shrinks on:** drawdown tiers; **persistent underuse of the risk budget** (a pod running at half its allowance is destroying the firm's return on allocated risk and is a real failure mode, not a safe one); P&L decomposing into factor exposure rather than alpha; crowding with another pod; a strategy failing to reproduce its backtest.

**Compute is allocated on the same axes.** A pod producing nothing gets less compute next month; a pod with a live validated edge gets more. Fable 5 states the reallocation and its rationale in the Monthly Letter.

### 5.4 Attribution — the only score that counts

```
Total P&L
├── Market beta        = β × market return           → "you were just long"
├── Factor P&L         = Σ (exposure × factor return) → momentum, value, size, sector, carry
├── Idiosyncratic      = residual                     → THE ONLY THING THE FIRM PAYS FOR
└── Costs              = commissions, slippage, borrow, funding
```

Every pod is scored on the third line. The CRO reports the decomposition monthly and is required to say plainly when a pod's apparent success is factor exposure in disguise.

Secondary metrics: rolling 30/90-day Sharpe; Sortino; Calmar; hit rate **paired with** slugging ratio (neither means anything alone — a sub-30% hit rate with high slugging is a legitimate and historically successful profile); contribution in basis points of fund NAV; capacity curve; correlation to other pods.

---
