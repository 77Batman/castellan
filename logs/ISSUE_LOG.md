# ISSUE LOG — Castellan Capital

Owned by the Chief Risk Officer. **Anything that goes wrong is entered here** —
data incident, reconciliation break, missed falsifier, blown assumption, process
failure, model error. Reviewed quarterly for recurring patterns.

| Field | Meaning |
|---|---|
| Severity | LOW / MEDIUM / HIGH / CRITICAL |
| Pattern tag | for quarterly pattern detection |

---

## I-001 · 2026-07-28 · No data layer exists · Severity: MEDIUM · Owner: head-of-data-infra

**Description.** `book/pit.db` does not exist. No prices, no funding rates, no
filings have been ingested. Under Amendment A4 research may consume prices only
through `pit_adjusted_close` / `pit_price_panel`, so **every research line in the
firm is currently blocked on this**, not merely inconvenienced by it.

**Why it is logged rather than silently fixed.** It is the firm's critical path
on day one and its schedule risk belongs on the record, not in a CIO summary.

**Resolution:** open. Blocking condition on all Gate 0 admissions.
**Pattern tag:** `critical-path-infrastructure`

---

## I-002 · 2026-07-28 · Forward-lag legacy claim has unreconstructable N · Severity: HIGH · Owner: quant-validation

**Description.** The Principal's prior Polymarket forward-lag arbitrage work
(reported ~71.5% win rate, 5 tuned parameters, 1 regime exclusion) was produced
outside the harness. Under Amendment A2 its numbers are inadmissible, and under
§4.1 a result whose trial count N is unreconstructable makes every Part IV
statistic uncomputable.

**Consequence, stated in advance so it is not a surprise later:** the prior work
carries **zero evidentiary weight**. Re-validation begins at N = 0 with a fresh
pre-registration and a newly locked holdout. The prior result may inform *which*
hypothesis to test; it may not inform any threshold, parameter, or verdict. Any
use of the prior tuned parameters as starting values is itself a leak of trials
into the new count and must be declared if it happens.

**Resolution:** open — binding constraint on Pod B's first pre-registration.
**Pattern tag:** `inherited-unvalidated-claim`

---

## I-003 · 2026-07-28 · Principal-hypothesis base rate has no denominator yet · Severity: LOW · Owner: devils-advocate

**Description.** Charter Appendix B names failure mode #1 as *Principal-originated
hypotheses passing Gate 1 at a materially higher rate than others'*. Detecting it
requires a base rate, and the firm currently has zero resolved hypotheses of
either origin. The metric is therefore undefined and will remain uninformative
until roughly 8–10 hypotheses have reached a verdict.

**Consequence:** for the firm's first months, the anti-sycophancy guarantee rests
on structure (independent reporting lines) rather than on measurement. This is a
real gap and is stated rather than assumed away.

**Resolution:** open — tracked, first reported when n ≥ 8 resolved.
**Pattern tag:** `metric-undefined-at-cold-start`
