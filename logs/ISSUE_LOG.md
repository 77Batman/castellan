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

---

## I-011 · 2026-07-28 · N-deflation by model priors — the registry's denominator omits the search inside the researcher · Severity: HIGH · Owner: quant-validation

**Description.** Filed by Validation in Ruling 002 §2.3, as the honest consequence
of following the Principal's own premise one step further than the proposal did.

Charter §4.1's entire apparatus takes `N` — the number of variants searched — as
the denominator [cited — Bailey, Borwein, López de Prado & Zhu 2014]. `TrialRegistry`
counts the trials the **harness ran**. An LLM researcher does not begin its search
at zero: its priors already encode which lead-lag relationships have been found,
which parameter neighbourhoods are conventional, which regimes are worth excluding.
A model that effectively already knows the answer converges in three logged trials
where an uninformed searcher would have taken three hundred — **and logs `N = 3`.**

DSR and PBO are then computed against a denominator that omits the search which did
the actual selecting, and are optimistic to that extent.

**Why this is HIGH and larger than the question it came out of.** Unlike the
holdout problem it contaminates the **in-sample** period, not just `[C, G]`; it is
**invariant to where `C` is placed**, so no cutoff pin touches it; and it **cannot
be fixed by waiting**, because it is a property of the researcher rather than of
the calendar. It is Charter Appendix B #2 — "trial counts are lost" — in a form the
Charter never contemplated.

**Partial mitigation, not a solution:** Ruling 002 R4(b) applies the existing §4.6
50% published-signal haircut presumptively to LLM-generated hypotheses. Validation
states plainly that this mitigates and does not solve.

**Resolution:** open.
**Pattern tag:** `denominator-understated-structurally`

---

## I-012 · 2026-07-28 · Uncontrolled retrieval channel — eight of nine seats can fetch post-cutoff data · Severity: MEDIUM · Owner: fable-5-cio

**Description.** Filed by Validation in Ruling 002; the CIO is the owner because the
tool grants are the CIO's to set.

**Measured by Validation, independently re-verified by the CIO** [measured]: of the
nine seat definitions, **eight hold `WebSearch` and `WebFetch`** — every seat except
`execution-ops` — and **all nine hold `Bash`**.

**Why it matters here.** Ruling 002 was convened on the Principal's concern about
*memorized* history leaking into hypothesis generation with no fetch and no audit
trail. The retrieval channel produces the identical failure — post-cutoff
information entering research without touching `pit.db`, any vault, or any event
log — and unlike the model-prior channel it is **open, uncontrolled, and larger.**

**The asymmetry that makes this worth logging rather than noting.** The firm was
being asked to build an unenforceable control against the smaller channel while an
enforceable control against the larger one sat unbuilt. Because the grants are
per-seat frontmatter, a reduction is a **default-path** control, not a barrier
someone must choose to respect.

**Companion control specified in Ruling 002 §3.5, with its limits stated** — the CIO
notes it does not close `Bash`, which all nine seats hold.

**Resolution:** open — CIO to act on §3.5.
**Pattern tag:** `uncontrolled-information-channel`

---

## I-013 · 2026-07-28 · CIO committed a seat's in-progress work under an unrelated message · Severity: MEDIUM · Owner: fable-5-cio

**Description.** Commit `ce41866`, whose message describes Validation Ruling 002,
also contains **six `harness/castellan/*.py` source files** — `__init__.py`,
`data.py`, `errors.py`, `gates.py`, `holdout.py`, `registry.py`, 1,557 insertions —
which are Data & Infrastructure's P-1 vault implementation for I-005. The message
does not mention that work at all.

**Detected by Data & Infrastructure**, not by the CIO, mid-task: it noticed its own
finished files already at HEAD under someone else's commit message and reported it
rather than assuming a duplicate implementation existed. **CIO independently
verified via `git show --stat ce41866`** [measured].

**Cause.** The CIO ran `git add -A` while background seats were writing to the
shared working tree. `-A` stages whatever is present, so an unrelated seat's
in-flight files were swept into a commit about something else. There is no
substantive conflict — Ruling 002 rules on where `C` is sourced from and explicitly
does not reopen Ruling 001 §2.3 — so the code is correct and uncontaminated. The
damage is to the record, not the software.

**Why this is logged at MEDIUM rather than shrugged off.** Amendment A3 makes the
git repository the firm's **book of record**. A commit whose message does not
describe its contents degrades exactly the property A3 exists to guarantee: that a
future reader can reconstruct what happened and why from the repo alone. Attribution
now rests on file-content matching rather than on the record saying so.

**Correction applied.** History is **not** rewritten — rewriting a book of record to
hide an error is a worse failure than the error. The remaining artifacts are
committed under a message naming I-005 explicitly and cross-referencing `ce41866`,
and this entry stands as the durable pointer.

**Process fix, binding on the CIO from now:** stage explicit paths when background
seats are running. `git add -A` is prohibited while any seat is live.

**Resolution:** corrected; process fix adopted.
**Pattern tag:** `book-of-record-integrity`

---

## I-014 · 2026-07-28 · A caller assertion overrides the holdout criterion · Severity: HIGH · Owner: head-of-data-infra

**Description.** Found by Validation in Acceptance 001; **independently reproduced
by the CIO against the shipped code** [measured].

`evaluate_gate1(..., holdout_opened_once=True)` returns **PASS** on the
"Holdout single-use" criterion for a family with **zero holdout events in the
registry**:

```
holdout_opened events: 0 | holdout_acquired: 0
'Holdout single-use': value='acquired once' verdict='PASS'
```

**Why HIGH.** House rule 4 — "the holdout is sacred" — and the entire P-1 regime
exist to make the holdout's status a property of the record. This parameter makes it
a property of *whatever the caller says*. Every control the firm has built this
sprint — spec sealing, the ingest ceiling, single-use acquisition, family scoping —
sits behind a boolean that bypasses all of it. Validation requires **removal, not
deprecation**.

**Resolution:** open — Acceptance 001 blocking condition.
**Pattern tag:** `caller-asserted-status`

---

## I-015 · 2026-07-28 · A wrong-but-non-empty passphrase permanently bricks a family · Severity: HIGH · Owner: head-of-data-infra

**Description.** Found by Validation; **independently reproduced by the CIO**
[measured]. Acquiring with a typo'd passphrase **succeeds**, seals the payload under
the typo, and retires the vault:

```
acquire_once with WRONG passphrase SUCCEEDED (834 rows)
vault state: RETIRED
read_acquired(REAL)  -> HoldoutPassphraseError   <-- BRICKED
re-acquire(REAL)     -> HoldoutRetiredError      <-- NO RECOVERY
```

The passphrase is checked for **presence**, not correctness, before the fetch — so
there is nothing to compare a typo against until the payload is already sealed.

**Why HIGH, and why it is worse than a bug.** Ruling 001 acceptance item **C4 says
in terms: "a typo must not brick a family."** The implementation inverts its own
acceptance criterion, and the test that claims to cover C4 passes anyway. A single
mistyped character at Gate 1 destroys a family's holdout with no recovery path —
against the Principal's own passphrase, on the one action he personally authorizes.

Seat 9 disclosed the presence-versus-cryptographic ambiguity in its note but **not
this consequence**.

**Resolution:** open — Acceptance 001 blocking condition.
**Pattern tag:** `acceptance-criterion-inverted`

---

## I-016 · 2026-07-28 · D1 leak detector has a measured timezone false negative · Severity: MEDIUM · Owner: head-of-data-infra

**Description.** `PITStore` persists `event_time` with the caller's UTC offset and
compares as **strings**. A bar stamped `America/New_York 2024-06-30 21:00`
(= `2024-07-01T01:00Z`) falling inside a holdout window opening at
`C = 2024-07-01T00:00Z` returns **0 rows** from the leak query — the leak is real
and undetected. The D2 ingest ceiling is unaffected (it converts to UTC); `asof` is
not. Found by Validation [measured].

**Resolution:** open — Acceptance 001 blocking condition.
**Pattern tag:** `timezone-string-comparison`

---

## I-017 · 2026-07-28 · `ingest_documents()` has no ceiling enforcement · Severity: MEDIUM · Owner: head-of-data-infra

**Description.** The D2 ingest ceiling was implemented on `ingest()`. A second
ingest path, `ingest_documents()`, enforces nothing — an open door beside the locked
one. Ruling 001's governing principle was that *the safe path must be the default
path and enforcement belongs in the store*; a second unguarded entry point defeats
it. Found by Validation.

**Resolution:** open — Acceptance 001 blocking condition.
**Pattern tag:** `incomplete-chokepoint`

---

## I-018 · 2026-07-28 · The registry cannot express R1–R4, so no family can be pre-registered · Severity: HIGH · Owner: head-of-data-infra

**Description.** Raised by Validation unprompted, as a sequencing consequence.
D-006 made Ruling 002's **R1–R4 binding**. The registry has **no columns for them**.

**Consequence, which reorders the sprint:** the forward-lag family **cannot be
pre-registered today** with its binding fields — freeze or no freeze. Pod B is
therefore blocked on a harness change, not on Validation's intake. The P-series
(pre-registration sealing) and the R1–R4 columns now gate **Validation's fourth
unit**, not ingest.

Related and equally structural: **every `ValidationReport` the harness can currently
produce is defective under Ruling 001 §2.4 / R1** — there is no FORWARD/HISTORICAL
holdout classification field, which R1 requires on the report's face.

**Resolution:** open — folded into the Acceptance 001 remediation dispatch.
**Pattern tag:** `binding-ruling-not-expressible-in-schema`
