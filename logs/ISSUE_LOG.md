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

---

## I-004 · 2026-07-28 · Forward-lag family may be inadmissible on data length · Severity: HIGH · Owner: quant-validation

**Description.** Charter §4.4 requires backtest length **≥ 4 years and ≥ 1 full
regime cycle**, with a holdout window **≥ 12 months**. The forward-lag family's
binding leg is Polymarket, whose history the Charter itself describes as thin
(§3.2). If usable contract history is under four years, the family **cannot pass
Gate 1 at any Sharpe** — the failure is evidentiary length, not absence of edge.

**Why this is filed at intake rather than discovered later.** §4.3 exists so that
impossibility is found at the cheapest stage. Spending Pod B's four Sonnet units on
a design that cannot reach a Gate would be exactly the waste the Gate 0 structure
is built to prevent.

**Interaction with P-1 (D-003):** because the holdout becomes `[C, G]` and grows
with elapsed calendar time, a family short on holdout today can become admissible
by waiting. That is the only legitimate use of elapsed time here — the in-sample
set does not grow with it.

**Blocking action:** Data & Infra reports **measured** usable Polymarket history as
its first deliverable, before Pod B spends a unit. Validation then rules ADMITTED /
ADMITTED-AS-EXPLORATORY / REJECTED at Gate 0.

**Resolution:** open.
**Pattern tag:** `evidentiary-length-ceiling`

---

## I-005 · 2026-07-28 · Harness holdout contract does not implement P-1 · Severity: HIGH · Owner: quant-validation → head-of-data-infra

**Description.** Principal amendment P-1 (D-003) requires that holdout data never
be fetched until Gate 1. `HoldoutVault.lock(df, passphrase)` requires the complete
series in hand at lock time and `open_once()` decrypts an already-stored payload.
The harness therefore **cannot express the regime the Principal just mandated**.

**Consequence.** A divergence between the Charter and the harness is a defect by
the Charter's own terms (Appendix D closing line). Until it is closed, any holdout
locked through the current code path violates P-1.

**Blocking action:** no ingest begins until Validation rules on the proposed
specification-sealing design and on whether cutoff `C` is pinned at
pre-registration. Data & Infra then implements to that ruling.

**Resolution:** open — blocks I-001.
**Pattern tag:** `charter-harness-divergence`

---

## I-006 · 2026-07-28 · Seats not invocable in the activation session · Severity: MEDIUM · Owner: fable-5-cio

**Description.** The nine seat definitions are on the discovery path and visible to
the Principal under `/agents`, but this session's agent registry was fixed at
startup — before `.claude/agents` existed — so `quant-validation` was not callable
by name. Dispatch failed with "Agent type not found."

**Workaround used, and its cost.** Validation Ruling 001 was dispatched through a
generic Opus agent instructed to read `.claude/agents/quant-validation.md` in full
and adopt it as its operating definition. This preserves the seat's instructions,
its independence framing, and its Opus tier. It does **not** preserve the
definition's `tools:` restriction, so the invoked agent held broader tool access
than the seat is scoped for.

**Why this is logged rather than absorbed.** Substituting a generic agent for a
registered independent seat is a structural change, and Charter house rule 7
forbids resolving those silently. The firm's independence guarantee rests on the
seat's instructions and on the CIO not overruling it — neither of which the
registry enforced anyway — so the degradation is narrower than it first appears.
It is still a degradation and it is on the record.

**Resolution:** self-clearing. A new session picks up the registered seats. Artifacts
are written to disk, so nothing is lost by restarting at any point.
**Pattern tag:** `session-startup-registry-lag`

---

## I-007 · 2026-07-28 · Live harness defect — Gate 1 holdout check is not family-scoped · Severity: HIGH · Owner: head-of-data-infra

**Description.** Found by Validation during Ruling 001. `harness/castellan/gates.py`
lines 209–210 query the holdout event log **globally, with no family filter**:

```python
opened = [e for e in registry.events(kind="holdout_opened")]
second  = [e for e in registry.events(kind="holdout_second_open_attempt")]
```

`TrialRegistry.events()` accepts a `family` argument (`registry.py:230`). It is not
passed. **CIO independently verified both facts in the source before this entry was
written** [measured].

**Consequence.** Family A opening its holdout would satisfy family B's Gate-1
single-use criterion. Family A's *violation* would fail family B's Gate. The
Charter's most-protected object — "the holdout is sacred," house rule 4 — is checked
against the wrong scope.

**Why it has never fired.** Zero families exist. It would have fired on the second
family the firm ever registered, which under the Sprint 1 agenda is the perp funding
carry family, roughly two weeks out. The 30/30 green suite did not catch it because
no test registers two families with holdout events.

**This is the first thing the harness has been caught getting wrong, and it was
caught by the seat whose job is to assume guilt.** That is the independent line
working as designed, and it is worth recording as such.

**Action:** fixed in the same change as the P-1 vault work, under Ruling 001
acceptance test E1. Not deferred.

**Resolution:** open.
**Pattern tag:** `scope-defect-silent-until-second-instance`

---

## I-008 · 2026-07-28 · Harness README understates its own test count · Severity: LOW · Owner: head-of-data-infra

**Description.** `harness/README.md` line 43 states "`pytest tests/` (16 tests)".
Actual suite is 30 [measured — CIO ran it]. Stale documentation.

**Why a LOW-severity doc bug is logged at all.** The rider governing the P-1
implementation is "the full harness suite passing." A README that misstates the
suite size is a document against which "full" could be checked and wrongly cleared.
Ruling 001 sets the target explicitly at **59/59** to remove the ambiguity.

**Resolution:** open — corrected alongside the vault change.
**Pattern tag:** `stale-documentation`

---

## I-009 · 2026-07-28 · The firm does not know its own seats' training cutoffs · Severity: MEDIUM · Owner: fable-5-cio

**Description.** The Principal proposed pinning holdout cutoff `C` at the seats'
model training cutoffs, on the grounds that a wholly historical holdout is weak
against an LLM researcher whose weights may already encode the period. Evaluating
that option requires knowing the cutoffs. The firm does not.

**What is established** [measured]: the CIO seat has a stated knowledge cutoff of
**May 2026**. Today is 2026-07-28 — roughly two months of genuinely post-cutoff
data exist for this seat.

**What is not** [measured — absence confirmed]: the authoritative Anthropic model
reference **does not publish training-cutoff dates**. The cutoffs for the Opus,
Sonnet, and Haiku 4.5 seats are unknown to this firm and were **not** invented to
make the ruling tractable.

**Why a documentation gap is logged as a firm issue.** A control whose parameter
the firm cannot source is not a control. If `C` is derived from a cutoff nobody can
verify, the resulting holdout carries an appearance of rigour the firm cannot
audit — and per Charter Appendix B, an unverifiable control is worse than a
known-weak one because it stops people looking.

**Second-order problem, raised with the ruling:** a training-cutoff pin addresses
*memorization* only. Every research seat holds `WebSearch` and `WebFetch` and can
retrieve post-cutoff information without touching `pit.db` or any vault — the same
"knowledge with no fetch and no audit trail" the proposal aims at, through a
different door. Routed to Validation as part of Ruling 002.

**Resolution:** open — Validation ruling pending.
**Pattern tag:** `unverifiable-control-parameter`

---

## I-010 · 2026-07-28 · Gate 1 length criterion silently equates observation count with calendar span · Severity: MEDIUM · Owner: head-of-data-infra

**Description.** Surfaced by Data & Infrastructure while drafting the Polymarket
data spec. `harness/castellan/gates.py:195`:

```python
years = backtest_years if backtest_years is not None else r.size / periods_per_year
```

`evaluate_gate1` declares `backtest_years: float | None = None` (`gates.py:123`),
so when a caller omits it the Charter §4.4 length criterion — and the MinBTL(N)
comparison built on it — is computed from **observation count**, not calendar span.

**CIO verification** [measured]: **no test in `harness/tests/` passes
`backtest_years` at all.** The only caller that does is
`harness/examples/demo_workflow.py:99`, which passes `len(prices) / 252` — the same
quantity the fallback would compute. **The calendar-span path is therefore never
exercised anywhere in the repo**, and the fallback is the de facto behaviour.

**Direction of failure, which is what makes this MEDIUM rather than LOW.** For a
dense, regular, one-row-per-date series the fallback is approximately correct. For
a **stacked or pooled panel where rows are contract-days rather than dates** — the
natural construction for a thin event-contract venue with many concurrent
contracts — observation count exceeds calendar span, sometimes by a large multiple.
In that case the fallback **overstates** backtest length and the criterion **fails
toward PASS**: a family with eighteen months of calendar history can report as
clearing the four-year floor.

This is the platform-age-versus-tradable-history confusion the Principal's rider
was written to prevent, reappearing inside the harness rather than in the
measurement. It is also the mirror image of I-007: that defect could fail either
way; this one only ever fails permissively.

**Whether it has fired:** no. Zero families exist. It would fire on the first
pooled family evaluated — under the Sprint 1 agenda, plausibly the forward-lag
family itself.

**Action.** Data & Infra flagged this as an implementation obligation for the
measurement run rather than a defect. The CIO is overriding that classification and
logging it: an untested permissive fallback on a Charter §4.4 criterion is a
harness-correctness issue, not a to-do. Validation should decide whether
`backtest_years` becomes required rather than optional.

**Resolution:** open — routed to Validation with Ruling 002.
**Pattern tag:** `harness-correctness-latent`
