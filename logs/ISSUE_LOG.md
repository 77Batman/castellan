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

**UPDATE 2026-07-28:** schema and the FORWARD/HISTORICAL report field delivered;
Gate 0 intake is no longer blocked by this. **Does not close** — see I-019.

---

## I-019 · 2026-07-28 · R4(a)/(b) have schema but no enforcement · Severity: MEDIUM · Owner: head-of-data-infra

**Description.** Ruling 002's **R4 is binding** under D-006: R4(a) requires
model-prior provenance to be recorded, R4(b) applies the Charter §4.6 50%
published-signal haircut **presumptively to LLM-generated hypotheses**.

Seat 9 delivered the **schema and fields** for both and disclosed, unprompted, that
**no computation is wired to them.** Nothing records provenance automatically and
nothing applies the haircut.

**Why it is logged rather than tracked informally.** A binding requirement that
exists as an empty column is the most dangerous shape a control can take: it reads
as satisfied in every audit that checks for the field's existence. R4(b) is also the
single measure that imposes a cost on the Principal's own flagship family, which
Validation cited in Ruling 002 §5 as its evidence against deference — an unwired
R4(b) quietly removes that cost.

**Principal's disposition, 2026-07-28:** stays **open until wired**, explicitly
**not counted as delivered**.

**Partial mitigation only:** R4(b) was itself only a partial mitigation of I-011,
which remains the larger and unsolved problem.

**Resolution:** open.
**Pattern tag:** `binding-control-declared-not-enforced`

---

## I-020 · 2026-07-28 · `yfinance` loader discards exchange-local UTC offset instead of converting it · Severity: MEDIUM · Owner: head-of-data-infra

**Description.** During DATA-INGEST-001, verifying that the I-016/C-5 UTC-normalization
fix holds for both loaders as instructed. It holds for `ccxt` (millisecond epoch
timestamps are absolute, so `pd.to_datetime(ms, unit="ms")` is correct by
construction) but **not** for `yfinance`.

`loaders.parse_yfinance_history` does `hist.index = pd.to_datetime(hist.index).tz_localize(None)`.
`yfinance` returns timestamps **tz-aware in the instrument's exchange-local zone**
(measured: `Ticker("SPY").history(...)` returns a `DatetimeIndex` tz = `America/New_York`,
values at local midnight, e.g. `2024-06-25 00:00:00-04:00`). `tz_localize(None)` on a
tz-aware index **strips the offset without converting** — it keeps the wall-clock
reading and discards the `-04:00`, rather than calling `tz_convert("UTC")` first. The
naive result is then handed to `PITStore._iso()`, which (correctly, per its own C-5
contract) treats a naive input as *already UTC* and localizes it as such. Net effect,
measured: a true instant of `2024-06-25T04:00:00Z` (SPY's local-midnight bar,
converted) is stored as `2024-06-25T00:00:00+00:00` — wrong by the exchange's UTC
offset, in the direction the offset points.

**Why this did not corrupt DATA-INGEST-001.** All eight ETF symbols ingested are
US-domiciled (`America/New_York`, UTC−4/−5). The error only shifts the stored
instant earlier within the same UTC calendar day (local midnight west-of-UTC never
crosses a UTC day boundary going backward) — it does not relabel any bar onto a
different UTC date, so the cutoff-bound assertions in DATA-INGEST-001 all still
report truthfully and no leak occurred in this ingest.

**Why it is still a real defect, not a footnote.** The direction of the error is
symbol-domicile-dependent. For an instrument on an exchange **east** of UTC by
enough hours (e.g., a Tokyo- or Sydney-listed ETF, if ever added to the panel), the
same `tz_localize(None)` bug would shift a bar's stored `event_time` **onto the
wrong UTC calendar date** — potentially the wrong side of a sealed holdout cutoff
`C` compared at day granularity (the exact comparison P7 and the D2 ingest ceiling
both use). The two-timestamp rule this seat's whole mandate rests on requires
`event_time` to be the true instant, not an instrument-dependent approximation of
it. Not fixed in-session: this task's instructions were to ingest and verify, not
to patch harness source outside the acceptance/remediation cycle Validation just
ran; flagging for the same review path C-5 went through rather than editing
`loaders.py` unilaterally mid-ingest.

**Fix sketch, not applied:** `parse_yfinance_history` should call
`hist.index.tz_convert("UTC").tz_localize(None)` (convert, then strip), not
`tz_localize(None)` alone.

**Resolution:** open.
**Pattern tag:** `timezone-offset-discarded` (sibling to I-016's
`timezone-string-comparison` — different failure, same family of hazard: local time
handled as if it were already UTC).

---

## I-006 — CLOSED 2026-07-28

Superseded in practice: seats have been dispatched successfully all session through
the generic-slot workaround, with the seat definition adopted by instruction. The
`tools:` restriction remains unenforced for those invocations — **the residual risk
is now carried by I-012**, which measures the tool grants directly. No separate
tracking needed.

---

## Devil's-Advocate neglect — CLOSED 2026-07-28

The CIO self-reported to the Principal that the Devil's Advocate held 2 Opus units
and had been dispatched zero times, despite the approved agenda specifying a
red-team **before** execution — Charter Appendix B #5 arriving as neglect rather
than as ceremony. Corrected by D-008 (Option C): the seat is convened before any
pre-registration, with its memo attacking the forward-lag family while the design
is still malleable. **Principal noted and closed as corrected.** Recorded here
rather than only in the decision record so the pattern is visible at quarterly
review.

---

## I-021 · 2026-07-28 · The implementing seat authors the tests that judge its own implementation · Severity: MEDIUM · Owner: fable-5-cio

**Description.** Raised by the Devil's Advocate. Data & Infrastructure writes both
the implementation and the acceptance tests that certify it. **I-015 is the direct
consequence** — a test claiming to cover C4 passed while C4's stated property
("a typo must not brick a family") was inverted in the code.

**Why structural rather than a one-off:** `DATA-IMPL-002` §13 records the *identical
shape* recurring in `authorize_retry()` **after** the pattern had been named and the
seat was explicitly tasked to hunt for it. A defect class that survives being named
is a property of the arrangement, not of the effort.

**Proposed fix, zero Opus cost:** acceptance tests authored by the criteria-setting
seat (Validation), **before** implementation.

**Resolution:** open. **Pattern tag:** `implementer-grades-own-work`

---

## I-022 · 2026-07-28 · Trial-count criterion passes a literal `True` — over-budget reads PASS · Severity: MEDIUM · Owner: head-of-data-infra

**Description.** Raised by the Devil's Advocate; **CIO verified in source**
[measured]. `harness/castellan/gates.py` builds the trial-count criterion with the
verdict argument hard-coded:

```python
over = fam.trial_budget and fam.n_trials > fam.trial_budget
criteria.append(_crit(
    "Trial count N (registry)", fam.n_trials,
    f"logged; budget {fam.trial_budget}", True,
    "OVER BUDGET — flagged to Director of Research" if over else ""))
```

`over` is computed and then used **only to write a note**. A family that has blown
its pre-registered trial budget — the precise condition Charter house rule 3 and
§4.1 exist to catch — reports **PASS**.

**Disclosed but never logged.** Seat 9 recorded this in `DATA-IMPL-002` §13 as a
design question. It reached no Issue Log entry until now. **A disclosed defect that
reaches no log is functionally undisclosed** — which is itself the finding.

Fails permissively, same direction as I-010.

**Resolution:** open. **Pattern tag:** `harness-correctness-latent`

---

## I-023 · 2026-07-28 · Cost model cannot express Polymarket's real costs · Severity: HIGH · Owner: head-of-data-infra → quant-validation

**Description.** Raised by the Devil's Advocate; **CIO verified in source**
[measured]. `costs.py` is the firm's **only admissible cost source** (Charter Seat 9
standing rule: researchers may not hand-roll costs). Two defects:

**(a) The Polymarket half-spread is a constant where the true cost is a ratio.**
`POLYMARKET = CostModel(..., half_spread_bps=100.0, ...)`, with the inline comment
"1c on a 50c contract ~ 2%". A 1¢ spread on a **10¢** contract is 10%, not 2% —
roughly **5× understated** — and data-spec criterion T6 admits every contract above
2¢. Cost is proportional to price; the model treats it as fixed.

**(b) `CostModel` has no field capable of expressing oracle or resolution risk.**
Fields are commission, half-spread, impact, borrow, funding, periods-per-year.
Nothing charges for a contract resolving against its economic meaning. **That is the
largest idiosyncratic risk in the entire Pod B mandate**, and the paper book will
systematically over-report net P&L because it cannot be charged.

**Resolution:** open — blocking on any Polymarket net-P&L claim.
**Pattern tag:** `cost-model-cannot-express-the-risk`

---

## I-024 · 2026-07-28 · Cross-venue clock alignment is unaddressed everywhere · Severity: HIGH · Owner: quant-validation

**Description.** Raised by the Devil's Advocate; **CIO confirmed the absence**
[measured] — session/clock-alignment terms appear essentially nowhere across
`FUND_CHARTER.md`, `reference/`, `research/` (pre-memo), `logs/`, or the harness.

Charter §4.6's "never fill at the same bar that generated the signal" is satisfied by
a fill **53 hours later across a weekend**. Polymarket trades 24/7; the equity or ETF
reference leg does not. A measured "lag" between them is then **the overnight and
weekend information gap relabelled as alpha** — large, robust, reproducible, and
entirely uncapturable.

**Compounding it:** the data spec screens Polymarket contract-days through T1–T7 and
**never screens the reference leg at all.**

**Resolution:** open — must be resolved before any forward-lag measurement is
interpreted. **Pattern tag:** `cross-venue-clock-unmodelled`

---

## I-025 · 2026-07-28 · Bias is measured too late — pass rates postdate the selection · Severity: MEDIUM · Owner: devils-advocate

**Description.** Appendix B #1 and I-003 track Gate 1 pass rates by hypothesis
origin. The Devil's Advocate's objection: **by the time pass rates are measurable,
the selection has already happened at attention allocation.** A firm can be perfectly
unbiased in pass rates and wholly captured in what it chose to test.

**Proposed replacement metric, computable today rather than after 8–10 verdicts:**
**Opus units by hypothesis origin.** Today's value: **4 of 4 = 100%
Principal-originated.**

Recorded as a live number, not a caveat.

**Resolution:** open — supersedes nothing; runs alongside I-003.
**Pattern tag:** `bias-metric-lags-the-decision`

---

## I-026 · 2026-07-28 · Polymarket depth history does not exist and is structurally unreconstructible · Severity: HIGH · Owner: quant-validation

**Description.** Answered by Data & Infrastructure in `DATA-PROBE-001`, promoted to a
standalone task by the Principal on the Devil's Advocate's argument that it was
strictly prior and nearly free.

**Measured** [measured]: historical Polymarket **order-book depth** is unavailable
from any confirmed public source and is **structurally unreconstructible on-chain** —
resting orders never touch the chain, only matched fills do. Verified against the
official `orderbook-subgraph` schema and the order-lifecycle documentation. `/book`
is live-only with no time parameter in the spec; `/prices-history` is price, not
depth. One undocumented endpoint was correctly **not** probed per instruction and is
recorded as an open unknown rather than folded into the answer.

**This converts data-spec criterion T4 from `[assumed]` unmeasurable to `[measured]`
unmeasurable.**

**Second, independent finding — the usable history is shorter than platform age.**
The trade-print proxy is **left-censored at the CLOB launch (late 2022, cited)**; a
2020-era market returns zero trades. Pre-CLOB AMM-era history is invisible regardless
of how old the platform is. **CIO calculation** [measured]: that gives **3.66–3.82
years** of calendar span to today — **under the Charter §4.4 four-year bar, before
any T1–T7 tradability screening has removed a single day.** This is I-004 resolving,
and resolving negative, by a route nobody anticipated: not thin history, but a
censored *start date*.

**Contested inference, routed to Validation, not accepted as settled.** Seat 9
concluded that unmeasurable depth makes the §4.4 **capacity** criterion unevaluable,
therefore INSUFFICIENT-DATA, therefore never PASS. The Devil's Advocate made the same
inference in REDTEAM-001 §B.4. **The CIO does not accept it as final, for a stated
reason:** `CostModel.per_side_cost` already accepts `adv_notional` and applies the
square-root impact law, and the trade-print endpoint yields **realized volume**, which
is a measured fact rather than an upper bound on depth. Capacity estimated from ADV
plus an impact model — without book depth — is the ordinary approach in equities,
where full book history is likewise unavailable.

**Whether that route satisfies §4.4 is Validation's determination, not Seat 9's**
(Charter Seat 9 cannot decide alone what counts as satisfying a Gate criterion, in
either direction).

**The CIO's own conflict, stated rather than left implicit.** The CIO is the seat
whose Principal sponsors this hypothesis, and "the CIO found a route that keeps the
Principal's family alive" is precisely the shape of Appendix B #1. The route is
therefore **raised, not adopted**; the CIO takes no view on whether it should
succeed, and Validation rules.

**Resolution:** open — Validation to rule with Gate 0 intake.
**Pattern tag:** `criterion-unevaluable-on-free-data`

---

## I-027 · 2026-07-28 · The registry physically cannot seed `N_inherited` · Severity: HIGH · Owner: head-of-data-infra

**Description.** Found by the Director of Research while drafting PREREG-001;
**CIO verified in source and against the live schema** [measured].

D-009 declared `N_inherited = 31,250` and directed that "the registry opens seeded at
that floor, not zero." **It cannot.** `TrialRegistry.family_stats`
(`registry.py:428–451`) computes:

```sql
SELECT COUNT(*) FROM trials WHERE family IN (...)
```

There is **no `n_inherited` column, no parameter, and no path.** Live schema confirms
it — `hypotheses` carries `trial_budget`, `predecessor_family`, and the new R1–R4
fields; neither table has any inheritance column.

**Consequence, and it is the exact failure the declaration was written to prevent.**
Seal today and DSR, PBO and MinBTL all compute against a denominator **in the tens**
while the pre-registration declares 31,250 — **I-011 recurring, now with a paper
trail asserting it was fixed.** A declared-but-unenforced control is worse than an
absent one, which is the same shape as I-019.

**Specified fix (DoR, H1–H4):** an `n_inherited` column; transitive summation across
the predecessor chain; a negative test **authored by Validation before
implementation** per I-021; and **σ_SR still computed from real trials only** —
phantom trials have no returns and **none may be synthesised**.

**Escalated, not resolved:** if H1–H4 cannot land before sealing, the DoR's
recommendation is to seal anyway and record **"declared but unenforced"** on the
Validation Report's face. The CIO carries that to the Principal rather than deciding
it.

**Resolution:** open — condition precedent C1 on PREREG-001.
**Pattern tag:** `binding-control-declared-not-enforced`

---

## I-028 · 2026-07-28 · CIO mis-specified the I-024 remediation — the family is intra-venue · Severity: MEDIUM · Owner: fable-5-cio

**Description.** Raised by the Director of Research against the CIO's own dispatch.

The CIO directed that PREREG-001 address I-024 by aligning bars across venues and
**"dropping out-of-session reference bars, not forward-filling."** That directive
presumes a cross-venue reference leg — Polymarket against an ETF, future or perp.

**The inherited family is intra-venue**: Polymarket spike contract → later-resolving
Polymarket contract on the same event (per `agents/pm-digital-markets.md` and I-002's
parameter list). **There is no session calendar to refer to.** The CIO imported the
Devil's Advocate's steel-man as though it were the design.

**Why the correction makes things worse, not better.** The confound does not
disappear — it **transposes, and is harder**: a session calendar is public, fixed and
knowable in advance, whereas a thin contract's **quote-death is irregular and
observable only from the data itself**. The DoR made **quote-liveness gating** the
operative rule and wrote both forms as binding.

**Wider consequence:** several other REDTEAM-001 findings were framed against the
cross-venue steel-man and need the same transposition before they can be applied.

**Resolution:** corrected in PREREG-001. Logged because a CIO directive that
mis-describes the strategy propagates into every downstream document that trusts it.
**Pattern tag:** `directive-mis-specifies-the-strategy`

---

## I-029 · 2026-07-28 · Falsifier F-001 passes pure noise ~31% of the time · Severity: HIGH · Owner: director-of-research

**Description.** Validation, Gate 0 001. **CIO verified the arithmetic** [measured]:
F-001 takes `argmax` over `k ∈ [−36,+36]h` — a **73-lag grid** — and kills only on
`k* ≤ 0` or `k* ≥ 24h`. Under pure noise `argmax` is approximately uniform over the
grid, so **23 of 73 lags survive = 31.5%.**

An `argmax` over 73 candidates **is a selection, not `N = 1`.** Leg (iii) compounds
it by measuring capture **at the argmax of its own sample**, biasing the falsifier
toward survival. There is no null, no stated α, and no minimum bar count.

**Why this matters beyond one document.** A falsifier is the Charter's second Gate 0
item and house rule 2's entire point — *write the falsifier before the test*. A
falsifier that a coin-flip passes one time in three is not a falsifier; it is a
formality that would have produced a "surviving" result on noise and been reported as
one.

**Resolution:** open — F-001 requires redesign before any seal.
**Pattern tag:** `falsifier-not-decisive`

---

## I-030 · 2026-07-28 · "Seal same-day" is not executable · Severity: MEDIUM · Owner: fable-5-cio

**Description.** Validation, Gate 0 001. D-010 directed: land the `n_inherited` fix,
**then seal same-day**. Validation finds the vault **cannot be sealed before the M1
measurement runs**, so the instruction is not executable **regardless of the
H-series**. The Principal's directive rested on a CIO sequencing assumption that was
wrong.

**The CIO's sequencing rationale is also overturned.** The CIO told the Principal
that sealing early is "strictly better" because `C` is the seal date and delay costs
forward window. Validation rules the opposite: **delay is strictly cheaper than
sealing defective**, because P7 freezes the document permanently and the only remedy
for a bad seal is a **successor family whose window starts later anyway** — so a bad
seal buys nothing and forfeits the correction. Six identified defects would have been
frozen.

**Resolution:** open — sequencing to be re-decided by the Principal.
**Pattern tag:** `cio-sequencing-assumption-wrong`

---

## I-031 · 2026-07-28 · KC-001 clause 3 double-counts under transitive summation · Severity: MEDIUM · Owner: PRINCIPAL

**Description.** Validation, Gate 0 001. KC-001 clause 3 provides that a restatement
after a kill is "a new family inheriting the killed `N`." Under the registry's
**transitive summation across the predecessor chain** (F4, and the H-series seeding),
that inheritance is applied **twice** — once through `predecessor_family` and again
through the clause's own text.

**Escalated to the Principal specifically, not resolved by any seat.** KC-001 is
signed by the Principal as sponsor; Validation states the fix **requires the
Principal's restatement, not a seat's interpretation**, because reinterpreting a
signed kill condition is exactly the erosion Charter Appendix B #4 describes.

**Resolution:** open — awaiting the Principal's restatement.
**Pattern tag:** `signed-instrument-needs-author-not-interpreter`

---

## I-032 · 2026-07-28 · No firm-level register of confirmatory tests · Severity: HIGH · Owner: quant-validation

**Description.** Validation, Gate 0 001, as the direct consequence of its own C-001
ruling. The `N = 1` confirmatory exemption is earned **per test**. Nothing in the
firm counts how many such exemptions are outstanding **across families**.

**Measured consequence** [cited — Validation]: at 20 families each holding one
exemption, the **firm-level false-positive rate is ≈2.7%.** Per-family honesty
composes into firm-level dishonesty with no seat positioned to notice.

`evaluate_gate1` additionally has **no concept of a confirmation window**.

**Resolution:** open — register required before the exemption is relied upon.
**Pattern tag:** `per-family-control-no-firm-level-aggregate`

---

## I-033 · 2026-07-28 · Five further defects from Gate 0 001, consolidated · Severity: MEDIUM · Owner: head-of-data-infra

Recorded so none is lost; full statements in `research/VALIDATION-GATE0-001-forward-lag.md`.

1. **H2 makes every seeded family read OVER BUDGET** — seeded `N` is compared against
   a trial budget that counts only real runs.
2. **H2 lets seeding paper over a family that has run nothing** — a large seeded `N`
   with zero logged trials looks substantial.
3. **The quote-liveness gate is unexecutable on measured data** — it requires
   historical quote state that `DATA-PROBE-001` established does not exist. This is
   why Gate 0(4) fails.
4. **Diagnostic D2 is unrunnable** under the single-cluster ingest that §13 permits.
5. **`forward_window_min_length` is a unitless `REAL`** — days, months and years are
   indistinguishable in the schema.

**Resolution:** open. **Pattern tag:** `gate0-001-consolidated`

---

## I-034 · 2026-07-28 · The sanctioned cost path guarantees a false KILL on delta-neutral crypto carry · Severity: HIGH · Owner: quant-validation → head-of-data-infra

**Description.** Found by the Director of Research while drafting PREREG-002.
**CIO verified in source** [measured]. `CostModel.carry_per_bar`
(`costs.py:49–60`) computes:

```python
(long_notional + short_notional) * fund
```

Funding is applied to **gross** notional and **only ever as a cost**.
`CRYPTO_PERP_TAKER` carries `funding_bps_annual = 1095.0` (the 0.01%/8h baseline,
Charter Seat 7).

**On a delta-neutral long-spot / short-perp pair** — gross = 2.0 — the model charges
`2 × 10.95% = ` **−21.9%/yr** where the position in fact **receives +10.95%/yr**.
Sign inverted, base doubled: a **32.85-percentage-point error on a 10.95-point
edge.** Any such strategy is killed by the cost model before the market gets a vote.

**Four compounding defects, all measured:**
1. `funding_bps_annual` is a **scalar**, so the **7,203 realized funding prints per
   asset** now sitting in `pit.db` **cannot enter P&L through the sanctioned path at
   all**.
2. `run_backtest` accepts **one** `CostModel` for a **two-legged** strategy, and **no
   `CRYPTO_SPOT_TAKER` preset exists.**
3. No field can charge **liquidation or venue insolvency** — the same gap as
   I-023(b), on the risk that actually ends carry strategies.
4. `scaled(2.0)` doubles the phantom drag to **43.8%/yr**, so Charter §4.4's
   cost-robustness criterion **stress-tests the sign error.**

**Why it is the firm's most consequential open defect.** Charter Seat 9's standing
rule is that researchers may not hand-roll costs — there is one cost library and every
strategy uses it. That rule now **mandates a calculation that is wrong in sign** for
the family the firm has just redirected to. PREREG-002 cannot be executed through the
sanctioned path.

**The Director of Research refused to authorize the fix**, correctly: the natural
repair moves funding into a synthetic perp total-return leg, which skirts the
no-hand-rolled-costs rule. **The specification is Validation's.** Validation has spent
all four Sprint 1 units, so this requires the Principal's reallocation.

**Resolution:** open — blocking execution of PREREG-002.
**Pattern tag:** `mandated-calculation-wrong-in-sign`

---

## I-035 · 2026-07-28 · Perp price series absent — only funding was ingested · Severity: MEDIUM · Owner: head-of-data-infra

**Description.** `DATA-INGEST-001` brought in `binanceusdm` **funding rates** but no
**perp price series**. The basis leg of PREREG-002 therefore has no perp mark.

Estimated one session with the existing loader. **The shortcut of assuming
perp ≈ spot is declared inadmissible** by the Director of Research, because it zeroes
the basis — which is the quantity under study.

**Resolution:** open. **Pattern tag:** `partial-ingest-silently-incomplete`
