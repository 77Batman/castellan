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

---

## I-036 · 2026-07-29 · INCIDENT — agent failure left the harness partially modified, untested, and suite-red · Severity: HIGH · Owner: fable-5-cio

**Description.** Two of three D-011 dispatches terminated on API errors
**mid-response, both at the point of writing their deliverable.**

**Validation (I-034 cost repair)** — died having said "I have everything I need.
Writing the ruling." **No artifact.** `research/VALIDATION-RULING-003-carry-accounting.md`
does not exist. Nothing was modified; that failure is clean.

**Data & Infrastructure (H-series seeded `N`)** — died at "Now let's write the
H-series test file." **This failure is not clean.** State on discovery [measured]:

| | |
|---|---|
| `harness/castellan/registry.py` | **+133 lines**, uncommitted |
| `harness/castellan/gates.py` | **+57 lines**, uncommitted |
| `harness/castellan/__init__.py` | **+8 lines**, uncommitted |
| `harness/tests/test_seeded_n.py` | **absent** — never written |
| `research/DATA-IMPL-003-seeded-n.md` | **absent** |
| **Suite** | **1 failed, 95 passed** — `test_P8_report_lists_predecessor_chain_prereg_hashes` |

**Why this is HIGH rather than an inconvenience.** The seat wrote **implementation
without its tests** and broke an existing passing test on the way. That is precisely
the arrangement I-021 exists to prevent — Validation authored H-1…H-14 *before*
implementation so that the implementing seat could not grade itself, and a partial
implementation with no tests landed is the same failure arriving by accident rather
than by design. **Completing this work would inherit source written without the
tests that were supposed to constrain it.**

**Compounding:** a third dispatch (Polymarket book capture) is **still running in the
same working tree** — `loaders.py` +408, `harness/scripts/`,
`book/polymarket_universe.json` are its live work-in-progress, not orphans. The tree
therefore contains dead untested changes and live in-progress changes
simultaneously, and they cannot be separated by inspection alone.

**CIO actions taken:** nothing committed; `book/registry.db` verified untouched
(0 families, 1 event); the orphaned files left in place **only** because reverting
mid-run risks clobbering the live agent.

**CIO recommendation:** once the live dispatch lands, **revert `registry.py`,
`gates.py` and `__init__.py` to `HEAD` and re-dispatch the H-series clean.** Partial
source written without its authored tests should not be finished — it should be
discarded.

**Resolution:** open — awaiting the live dispatch, then the Principal's call on
budget accounting.
**Pattern tag:** `agent-failure-leaves-untested-partial-state`

---

## I-037 · 2026-07-29 · §4.4 cost-robustness manufactures "survives 32× costs" on a receipt · Severity: HIGH · Owner: quant-validation

**Description.** Validation Ruling 003. **CIO verified** [measured]: `gates.py:464`
bisects the breakeven multiplier over `lo, hi = 1.0, 32.0`, **assuming `t(m)` is
non-increasing in `m`.**

If `m` scales a **receipt** rather than a cost — which is what the naive sign-only
repair of I-034 would produce — then `t(m)` **increases** with `m`, the bisection
never finds a crossing, and it **returns 32.0**. The Validation Report then prints
*"survives 32× modelled costs"* under a Charter §4.4 heading.

**The naive repair does not merely fail to stress the family — it manufactures a
robustness claim.** This is why Ruling 003 splits stress semantics: `scaled(m)`
applies to frictions only; carry is **scenario-shifted, including sign inversion**.

**Resolution:** open — closed by Ruling 003's specification, pending implementation.
**Pattern tag:** `stress-test-inverted-by-sign`

---

## I-038 · 2026-07-29 · `PaperBook` accrues no carry at all · Severity: HIGH · Owner: head-of-data-infra

**Description.** Validation Ruling 003, finding N-4. **CIO verified** [measured]:
`book.py` references `per_side_cost` **and nothing else** — no `carry_per_bar`, no
funding, no borrow, anywhere in the file.

**Consequences.** Charter Seat 10's mandated **fill-quality line (modelled slippage,
commissions, borrow, funding)** is **uncomputable**. And for a delta-neutral
long-spot/short-perp position, funding *is* the strategy — so the paper book **omits
the entire economic content** of the position it is supposed to mark.

The firm's $10M paper book, opened at D-001 and reconciling clean ever since, would
have reported a carry strategy's P&L with the carry missing.

**Resolution:** open. **Pattern tag:** `paper-book-omits-the-strategy`

---

## I-039 · 2026-07-29 · The harness's worst arithmetic error sits in its only untested function · Severity: MEDIUM · Owner: head-of-data-infra

**Description.** Validation Ruling 003, finding N-3. **CIO verified by grep**
[measured]: across the entire 96-test suite, **zero tests** reference
`carry_per_bar`, `funding_bps_annual`, `borrow_bps_annual`, or `CRYPTO_PERP_TAKER`.

I-034 — sign inverted, base doubled, 32.85 points of error — survived thirteen
Validation-authored acceptance batches because **nothing ever executed the function**.
Coverage counted in tests passed says nothing about coverage of the surface that
matters.

**Resolution:** open — Ruling 003 sets a suite floor of 115 with 19 tests on this
surface. **Pattern tag:** `defect-in-the-untested-function`

---

## I-040 · 2026-07-29 · Four further Ruling 003 findings, consolidated · Severity: MEDIUM · Owner: head-of-data-infra

Full statements in `research/VALIDATION-RULING-003-carry-accounting.md`.

1. **N-1 — two silently disagreeing calendars.** `carry_per_bar` annualizes on
   `cost_model.periods_per_year` while `run_backtest` uses its own.
2. **N-2 — a measured-false cadence claim.** `DATA-INGEST-001` records funding as
   "every 8h". Measured false for SOL, which settles at 2h/4h intervals during
   stress — **up to 12 prints in a day, on 11 of 2,145 days** — i.e. it fails
   precisely in the window that matters.
3. **N-5** — PREREG-002's C11 is unexecutable as drafted: §20 places it before the
   seal, §15 step 1b runs it as in-family trials, which requires `open_hypothesis`,
   **which is the seal.** Resolved by a separate calibration family consuming
   `R_bench` only, whose `N` does not accrue to the research family.
4. **N-6** — Charter Seat 7's 11%/yr is **correct arithmetic on an assumed input**
   and is now **inadmissible as a P&L input**. Realized: BTC **+11.86%**, ETH
   **+14.07%**, SOL **+0.10%** [measured by the CIO from `pit.db`].

**The SOL number forecloses the cheap fix.** A sign-corrected scalar at 1095 bps
would credit SOL with a **107× overstatement, erring optimistically** — crediting a
receipt that is not there. A scalar's error is whatever the asset makes it.

**Resolution:** open. **Pattern tag:** `ruling-003-consolidated`

---

## I-041 · 2026-07-29 · A source-only revert left a schema migration on disk, and the CIO committed it under an unrelated message · Severity: MEDIUM · Owner: fable-5-cio

**Description.** Surfaced by Data & Infrastructure while implementing the H-series;
**CIO verified** [measured].

The dead I-036 agent ran `_migrate()`, which executed `ALTER TABLE hypotheses ADD
COLUMN n_inherited` against the **live `book/registry.db`**. The CIO then stashed and
dropped that agent's **source**, restoring the suite to green — **but a stash does not
undo a database an agent has already written to.** The schema change persisted.

Verified state at `HEAD` before the merge:

| | |
|---|---|
| `book/registry.db` (committed) | `n_inherited` **present** |
| `harness/castellan/registry.py` (committed) | `n_inherited` — **zero occurrences** |

The migration was then committed in **`2c0d3e7`**, whose message reads *"Registry:
capture-run events from DATA-INFRA-001"* — **attributing a dead agent's schema
migration to the Polymarket book-capture task.**

**Two CIO failures, and the second is the instructive one.**

1. **Incomplete verification.** The CIO reported *"registry.db verified untouched (0
   families, 1 event)"* in I-036. It checked **row counts, not schema.** The database
   was not untouched and the assertion was wrong.
2. **This is I-013 recurring — committed during the cleanup of I-013's own incident
   class.** A change was staged without inspection and landed under a message that
   misdescribes it. The explicit-path staging rule from I-013 was followed and did
   not help, because the *path* was correct; what was wrong was committing a file
   whose **contents** had not been examined.

**Generalisation worth carrying, because it limits the fix adopted in D-012.**
Worktree isolation separates **repository files**. It does **not** isolate external
state — a database opened by absolute path is shared regardless. On this occasion the
worktree agent did not touch `book/registry.db` (verified: working tree schema equals
`HEAD`), but the isolation guarantee is **narrower than it appears** and should not be
relied on for anything outside version control.

**Disposition:** the column is benign — 0 hypotheses, no data at risk, and the
H-series merge makes source and schema agree. **Not reverted.** Logged so the record
shows the schema arrived from a dead agent rather than from the commit that carries
it.

**Resolution:** closed on merge; the divergence itself is resolved, the process
lesson stands.
**Pattern tag:** `revert-does-not-undo-side-effects`

---

## I-042 · 2026-07-30 · Mean basis negative while mean funding strongly positive — unexplained · Severity: MEDIUM · Owner: quant-validation → director-of-research

**Description.** Surfaced by Data & Infrastructure in `DATA-INGEST-002`, **flagged not
resolved**, which is the correct handling.

Measured perp-minus-spot basis is slightly **negative** on average (BTC −1.58 bps,
ETH −0.95, SOL −3.18) while realized funding over the same span is strongly
**positive** (BTC +11.86%/yr, ETH +14.07%, SOL +0.10%). Naively these should agree in
sign: a perp trading above spot is the usual accompaniment to longs paying funding.

Seat 9's hypothesis — **the fixed interest-rate component in Binance's funding
formula**, which decouples the premium from the funding rate — is `[assumed]`, **not
verified against vendor documentation.**

**Why it is logged rather than left in the deliverable.** PREREG-002's strategy is a
**basis-and-carry** family. If the relationship between the basis and the funding rate
is mis-specified, the core quantity under study is mis-specified, and the error would
be invisible in a backtest that simply consumed both series. This must be resolved
**before the basis leg is interpreted**, not after a number is produced from it.

**Resolution:** open — blocks interpretation of the basis leg, not the ingest.
**Pattern tag:** `two-series-disagree-in-sign-unexplained`

---

## I-043 · 2026-07-30 · Pre-declared restatement — today's open candle · Severity: LOW · Owner: head-of-data-infra

**Description.** `DATA-INGEST-002` ran at 19:38Z against a cutoff bound of
`2026-07-29T23:59:59Z`, so the bound did no truncation and **every symbol's last
ingested bar is today's still-open daily candle.**

It is inside the cutoff and **not a leak**. It *is* a provisional value that will
legitimately restate itself through `PITStore`'s normal versioning the first time
anyone re-ingests after `2026-07-30T00:00Z`.

**Recorded so that the future restatement reads as expected housekeeping rather than
as an incident.** Charter Seat 9 requires restatement incidents to be escalated to
Validation; this one is pre-declared, and pre-declaring an expected anomaly is
cheaper than investigating it twice.

**Resolution:** self-clearing on the next ingest.
**Pattern tag:** `pre-declared-expected-restatement`

---

## I-044 · 2026-07-31 · CIO printed a hardcoded conclusion alongside a computation · Severity: MEDIUM · Owner: fable-5-cio

**Description.** Self-reported. While testing the Principal's I-042 reconciliation, the
CIO ran a script that computed funding and basis figures and **appended a hardcoded
`print()` stating a conclusion** — that implied premium was "ordered exactly as mean
basis is," with specific numbers written into the string literal rather than derived
from the query.

**Two defects in one output.**
1. **The arithmetic was wrong** — a unit conversion multiplied by 100×, reporting BTC
   funding as 108 bp/8h instead of 1.08.
2. **The conclusion was narrated, not computed.** The numbers in the prose line did
   not come from the computation printed above it. Had the reader trusted the summary
   line, they would have accepted a claim no code had tested — and the arithmetic error
   above it made the claim false anyway.

**Why it is logged at MEDIUM rather than treated as a typo.** Charter Amendment A2
exists because *a number produced outside the engine is inadmissible*, and house
rule 6 requires provenance on every claim. A CIO who prints prose conclusions beside
computations is manufacturing exactly the artefact the firm forbids its seats from
producing — and doing it in the one seat with no independent line above it.

Both were corrected in the same exchange and the corrected figures (BTC 1.0831,
ETH 1.2846, SOL 0.0093 bp/8h; 64–65% of prints off the 1.00 bp floor) carried
forward into the I-042 verification dispatch as `[measured]`.

**Process consequence adopted:** the CIO does not print interpretive prose from inside
a computation script. Figures out, reading stated separately and attributed to the
person making it.

**Resolution:** corrected; practice adopted.
**Pattern tag:** `narrated-not-computed`

---

## I-045 · 2026-07-31 · SOL's funding series has a dated structural break inside PREREG-002's sample · Severity: HIGH · Owner: director-of-research → quant-validation

**Description.** `DATA-VERIFY-001` established `[cited — official]` that Binance made a
**SOL-specific change on 2022-11-09**, widening its funding clamp roughly **40× (to
±2.00%)** while shortening its settlement interval. The **CIO independently confirmed
the break from the firm's own data** [measured]:

| SOL funding prints/day | |
|---|---|
| 2022-11-05 → 11-08 | 3, 3, 3, 3 |
| **2022-11-09** | **4** |
| 2022-11-10 → 11-15 | **11, 12, 12, 12** |
| 2022-12-01 | back to 3 |
| Days with >3 prints **before** 2022-11-09 | **0** (of 787) |
| Days with >3 prints **after** | **10** (of 1,358) — all in that window |
| **BTC control, >3-print days** | **0 before, 0 after** |

The break is dated to the day, SOL-specific, and absent from the control.

**Three independent series converge on 2022-11-09:** the measured basis dislocation
(**−16.90%**, `DATA-INGEST-002`), the measured funding-cadence break (above), and the
cited vendor announcement. This promotes I-040's N-2 finding from
measured-but-unexplained to **measured and cited**.

**Why this is HIGH and why it matters before the seal.** PREREG-002 declares period
exclusions as **NONE — full span including COVID, LUNA, FTX** (K3, menu of 9), which
was the honest choice and remains so. But the firm now knows the **SOL funding series
is generated by different formula parameters before and after 2022-11-09.** This is
**not** a regime-exclusion question — it is a **data-homogeneity** question: the
family's own **state variable** (funding relative to its trailing baseline) does not
mean the same thing across the sample.

Pooling across an undeclared formula change is the kind of defect that a backtest
consuming both series would never surface, and **P7 would freeze it permanently at the
seal.**

**Escalation.** `DATA-VERIFY-001` concluded PREREG-002's mechanism needs *"one
addition, not a restatement."* **The CIO's follow-up check enlarges that scope again**
— a declared structural break in the state variable is more than a clarifying
sentence. Whether it requires a mechanism restatement, a declared break control, or
merely a disclosure is the **Director's call**, and the Director has **no Opus
remaining**.

**Resolution:** open — blocks the seal.
**Pattern tag:** `undeclared-formula-change-inside-sample`

---

## I-046 · 2026-08-04 · A binding order was asserted on-disk twice, absent both times, and is now committed under a message attributing it to the Principal · Severity: HIGH · Owner: CIO → Principal

**Description.** Two instances of the same failure mode inside 24 hours, the second
created by the repair of the first.

**Instance 1 — 2026-08-03.** The Principal's D-001 stated Standing Order 001 was
"committed at `ops/`, read it in full before any dispatch." [measured] It was in no
commit and on no path; its operative text existed only as prose in
`logs/DECISION_RECORD.md` D-015 §3–4. The CIO reconstructed it from that source, wrote
`ops/STANDING-ORDER-001.md` with a provenance note marking it a reconstruction, and
logged the gap as D-001 §1.

**Instance 2 — 2026-08-04.** The Principal's correction stated the canonical text was
"now at `ops/STANDING-ORDER-001-canonical.md`." [measured] That path does not exist in
the working tree, in `HEAD`, in any commit on any ref (`git log --all --diff-filter=A --
'*canonical*'` returns empty), or in any stash. It has never existed.

**What is actually in the repository.** Commit `2d9ef4f`, authored by the Principal at
2026-08-04 12:46:32 -0400, message **"ops: canonical Standing Order 001 text
(Principal-supplied)"**, adds 69 lines to `ops/STANDING-ORDER-001.md`. Those 69 lines are
**the CIO's reconstruction, byte-identical** — `git diff 2d9ef4f -- ops/STANDING-ORDER-001.md`
against the working tree is empty, and the committed blob still contains the CIO's own
provenance note reading *"This file was written on 2026-08-04 by the CIO."* [measured]

The most probable mechanism is a `git add ops/` that swept up the untracked
reconstruction, with the canonical file never written to the working tree.

**Why this is HIGH and not clerical.** Instance 1 was an absent document — a gap, visible
as a gap. Instance 2 is worse in kind: the repository now carries a commit message
asserting *Principal-supplied canonical text* over content the CIO wrote. A future reader,
including a future session of this firm, has no way to detect the misattribution except by
noticing that the "canonical" text confesses its own authorship in line 6. **Under A3 the
repo is the book of record.** A book of record whose commit messages misattribute
authorship of binding orders is failing at the one job A3 assigns it. The defect is not
that a file is missing; it is that the missing file has been silently replaced by a
different document wearing its name.

**What the CIO did NOT do.** The instruction was to diff the reconstruction against the
canonical text, adopt the canonical as governing, and log the clauses the reconstruction
lacked. **The CIO did not perform that diff and did not log any such clauses.** There is
no second document to diff against. Any list of "clauses the reconstruction lacked" would
have been produced from nothing — which is precisely **I-044**, the orchestrator's
fabricated narration that D-015 §2 made a governance exhibit rather than a footnote. The
instruction was well-formed and the CIO would have executed it had its premise held; it
did not hold, and the correct output is this entry rather than a fabricated diff.

**Consequence for the interval.** None demonstrable. The Principal's correction states the
reconstruction "ran as silently narrowed order for the interval." That may be true, but
**the firm cannot presently evidence it either way**, because the text it would be narrow
relative to has never been in the firm's possession. The reconstruction's §1–§3 are
D-015's text and its §4 is the D-001 riders, so any divergence lies in clauses the CIO has
never seen. Both dispatches made under it — Director/PREREG-002 and Seat 9/Rider A —
conform to D-015 and to the riders as written, and both stand, as the Principal directed.

**Remedy required, and it is the Principal's alone.** The canonical text must reach the
working tree by a path that does not depend on it already being there: pasted into the
session, or written and verified with `git show HEAD:ops/STANDING-ORDER-001.md` before the
commit is trusted. Until it does, `ops/STANDING-ORDER-001.md` governs **as an acknowledged
reconstruction**, and commit `2d9ef4f`'s message stands as a known-false label that the
firm has chosen to record rather than rewrite — history is not edited under A3.

**Escalation.** To the Principal, as the only party who holds the canonical text. Flagged
to Validation as a record-integrity matter: any Gate submission citing Standing Order 001
inherits this uncertainty until closed.

---

### I-046 · RESOLUTION · 2026-08-04 · canonical text received, committed, verified — and the gap measured

**Canonical text supplied by the Principal by paste under D-002** and committed as
`23be6b6`. Verified **from `HEAD`, not the working tree**: 53 lines, all 8 sections
present, **zero CIO authorship traces** (`grep` for "by the CIO" / "reconstructed" /
"Provenance note" returns 0), HEAD blob byte-identical to working tree. The verification
path the CIO specified was used precisely because the failure mode was a working-tree file
that had never been what its commit claimed.

Commit `2d9ef4f`'s false label stands recorded and unrewritten per A3.

### What the reconstruction lacked — measured, not assumed

Diff of the preserved 69-line reconstruction against the 53-line canonical text.

| | Reconstruction | Canonical |
|---|---|---|
| Sections | §1–§4 | §1–§8 |
| Title | "Sprint 2" | "**PRINCIPAL DELEGATION PROTOCOL**" — calibration mode, supplements Charter Part IX, amends nothing |

**Canonical clauses absent from the reconstruction — 18 of 18 probed, all absent:**

| Clause | Canonical location |
|---|---|
| The entire objective function; ML trial-accounting ruling; "a correct kill counts identically to a pass"; "any optimization that pressures a gate rather than resolving a hypothesis is a violation of this order"; Σα and origin-ratio reporting | §1 |
| "No rollover" · "**Failed invocations count as spent (D-012)**" · DA Gate 1 reserve convention, one Opus sealed per family approaching seal | §2 |
| The `[would-have-asked]` calibration tag | §3 |
| **The entire hard-interrupt set** — 8 enumerated triggers, "triggers, not thresholds", "no seat, including the CIO, decides whether an item really qualifies", "**Silence is never approval**" | §4 |
| **The entire dead-man clause** — 10 invocations or 5 calendar days, "a halted firm is a correct outcome; an unsupervised one is not" | §5 |
| Friday Research Review · Monthly Letter · interrupt queue · the decision record and `[would-have-asked]` log as the review surface | §6 |
| **The entire calibration audit and graduation conditions** — expiry with the sprint, reissue requirement | §7 |
| **The entire erosion guard** — widened by any seat, narrowed only by the Principal in writing, no adjectives by interpretation, no batching or softening, Seats 2/6/7 independence untouched | §8 |

**What the two documents actually share: two things.** The 30/12 budget number, and
**one sentence — "Per-turn Principal review is discontinued."**

That sentence is canonical **§6's final sentence**, and it is the only clause in §6 that
*removes* oversight. The reconstruction carried it and lost §6's two preceding sentences,
which specify the oversight that replaces per-turn review. It also lost §4, §5, §7, and §8
entirely — every structural constraint on the delegated loop.

**The reconstruction was therefore not a narrowed version of the order. It was a different
document sharing one number and one oversight-removing sentence, operating under the
order's name.** Its remaining content — remedies (a)/(b)/(c), the PREREG-002 first unit,
M1→seal, Riders A/B/C — is correct and sourced from D-015 and D-001, but none of it is in
the order. Right content, wrong document.

The bias direction is measurable and one-sided: **of the two clauses preserved, one is a
budget ceiling and one removes Principal review; of the ~18 lost, all constrain the CIO.**
The CIO does not claim this was intentional — D-015 recorded the permissions granted and
not the guardrails attached, so the reconstruction inherited the source's bias. The
direction is the finding, not the motive.

### Breaches incurred during the interval — measured

**1 · §2 budget arithmetic was wrong, and the CIO ruled it wrong on the record.**
Canonical §2: *"Failed invocations count as spent (D-012)."* The Director's Opus unit
terminated on an API error; the CIO resumed it and reported *"I'll count the unit once,
since the read was not repeated."* That ruling is void under §2. **Corrected count: 3 of
30 invocations, 2 of 12 Opus** (Director dispatch, Director resume, Seat 9). Further, §2's
DA reserve convention seals one Opus for PREREG-002 as a family approaching seal, so
**freely allocable Opus is 9, not 10.**

**2 · §4 was breached in mechanism, not in outcome.** I-046 was filed HIGH at 2026-08-04.
§4 makes "any issue filed HIGH" a hard interrupt: the loop halts and queues. The CIO
instead reported it in prose and continued working in the same turn — resuming the
Director and writing records. The outcome converged, because the Principal ruled promptly
in D-002, but convergence by luck is not compliance. **I-045 also stands HIGH and open**
and is an interrupt item already before the Principal.

**3 · §3 tagging did not occur.** No decision this session carried `[would-have-asked]`.
Retroactively tagged in D-003.

**4 · §1 contains a goal item the firm has not scheduled** — the ML trial-accounting
ruling (search space declared at Gate 0; every fitted configuration a logged trial;
purged/nested CV mandatory; seeds fixed). It appears in no agenda, no dispatch, and no
decision record entry prior to today. It is now an open sprint commitment with no owner.

**Resolution:** **RESOLVED** — canonical text committed at `23be6b6` and verified from
`HEAD`. The uncertainty the CIO flagged against Gate submissions clears as of this entry.
The four breaches above are recorded as fact and carried into the §7 calibration audit at
sprint close.
**Pattern tag:** `asserted-on-disk-absent-in-fact` · `silently-narrowed-order`

---

## I-047 · 2026-08-04 · Un-retried Gamma call was the measured, repeated, uncaught cause of several laptop capture gaps · Severity: MEDIUM · Owner: head-of-data-infra

**Description.** Found while investigating D-001/Sprint-2 Rider A (VPS capture migration,
`DATA-INFRA-002`). `logs/capture/polymarket-book.err` carries 4 identical uncaught
tracebacks, all with the same shape: `capture_polymarket_book.main()` →
`refresh_universe()` → `_check_market_status()` → `_gamma_get()` → `socket.gaierror` /
`urllib.error.URLError` ("nodename nor servname provided, or not known") — a DNS
resolution failure, consistent with the host having just woken from sleep before its
network interface was fully back up.

**Why this matters beyond the 4 occurrences.** `fetch_polymarket_books` (the CLOB `/books`
call inside `ingest_polymarket_books`) already had retry/backoff (3 attempts,
2s/4s/8s) — deliberately, per its own docstring. `_gamma_get` — called first in
*every* round, for universe refresh — had **none**. A transient failure here crashed the
whole script before `ingest_polymarket_books` was ever reached, which (before this
session's heartbeat mechanism, `DATA-INFRA-002` §2) left **zero trace anywhere in
`book/pit.db`** — not even the ordinary stdout log line, since the crash happened before
the first `print()` of the round. Every one of these events is indistinguishable, after
the fact, from the host simply being asleep — which measurably inflated the "not polled"
share of the coverage gaps the CIO's morning figure was built from, by an amount this
entry cannot retroactively quantify (the trace shows the failure occurred; it does not
show how many *additional* silent instances left no trace of any kind, by construction).

**Fix, same session, same seat.**
1. `_gamma_get` (`harness/castellan/loaders.py`) now retries transient failures with the
   identical 3-attempt exponential backoff `fetch_polymarket_books` already used — parity
   between the two network calls a single round makes.
2. `capture_polymarket_book.py`'s `main()` now wraps the entire round in a top-level
   `try/except`: any uncaught exception, from anywhere in the round, now still writes a
   heartbeat document (`ok=False`, the exception repr as `error`) before the process
   exits, unless opening the store itself fails (logged separately to stderr, not
   swallowed). This closes the blind spot the heartbeat mechanism (`DATA-INFRA-002` §2)
   would otherwise have had for exactly this failure class.

Both changes are covered by new tests (`harness/tests/test_polymarket_capture.py`:
`test_gamma_get_retries_and_recovers`, `test_gamma_get_raises_after_exhausting_retries`)
and verified manually against the running laptop capture, which picked up the edited
script on its next scheduled firing (no restart needed — `capture_polymarket_book.py` is
re-exec'd fresh per launchd firing) and wrote its first heartbeat row without incident.

**Resolution:** fixed this session; 139/139 → 160/160 harness tests pass (21 new, 0
broken). The 4 historical occurrences remain permanently unattributable to a specific
missed round — see I-048 for the general limit this illustrates.
**Pattern tag:** `missing-retry-on-network-call` · `silent-uncaught-failure`

---

## I-048 · 2026-08-04 · Before today, "not polled" and "polled, whole batch failed" were provably indistinguishable in `book/pit.db` — closed going forward, not retroactively · Severity: MEDIUM · Owner: head-of-data-infra

**Description.** Directed to verify, not assume, whether the schema could tell "we did
not poll this round" apart from "we polled and there was no quote" (`DATA-INFRA-002` task
item 2). **Checked against the actual schema, not asserted:**

- A round that polls successfully and finds a genuinely empty book **does** write a row
  (`parse_polymarket_book` sets `two_sided=0.0` unconditionally; confirmed by new test
  `test_parse_empty_book_still_writes_a_row`) — "polled, no quote" was already
  distinguishable from a missing row, correctly.
- A round where the whole-batch fetch fails after retries writes **nothing** — by
  design (`ingest_polymarket_books`'s own docstring: "if every attempt fails, NOTHING is
  written"). A round the scheduler simply never fired also writes **nothing**. These two
  cases were, before this session, **provably identical** in `book/pit.db`: same absence
  of rows, no way to tell them apart from the store alone. I-047's 4 traces are direct
  evidence this case occurred, not merely a theoretical gap.

**What was required to make it explicit rather than inferred, and what was built.**
`record_capture_heartbeat` (`harness/castellan/loaders.py`) — one document per poll
*attempt*, regardless of outcome, under `source='polymarket-capture-meta'`,
`symbol='__heartbeat__'`, recording `ok`/`n_requested`/`n_captured`/`n_failed`/`error`.
Wired into every exit path of `ingest_polymarket_books` and `capture_polymarket_book.py`
(success, total-fetch-failure, empty-universe, and — after I-047's fix — any uncaught
exception). `harness/scripts/report_polymarket_coverage.py` reports both the
heartbeat-covered window and the pre-heartbeat window separately, rather than blending
them.

**The honest limit, stated per house rule 6, and it does not go away.** This closes the
gap **from 2026-08-04T16:53:16Z forward** (the first heartbeat row the running laptop
capture actually wrote, unprompted, on its next scheduled firing after the code changed).
**It is structurally incapable of resolving the ambiguity for any capture history before
that instant** — the entire span the CIO's morning coverage figure was computed over.
Every gap in that window remains, permanently, only interpretable as "either the scheduler
did not fire, or it fired and failed outright" — both consistent with the observed
absence, neither provable from the store. This is the same one-way-only property every
other prospective-only fix in this data source has had (`DATA-PROBE-001`,
`DATA-INFRA-001` §6, and now this).

**Resolution:** closed going forward as of 2026-08-04T16:53:16Z; open permanently, by
construction, for all prior capture history. No further action closes the historical
gap — there is none available.
**Pattern tag:** `not-polled-vs-failed-indistinguishable` · `prospective-only-fix`

---

## I-049 · 2026-08-04 · Opus dispatches terminate on API error at the read→write transition, twice, costing 2 of 12 sprint Opus units for zero artifacts · Severity: MEDIUM · Owner: CIO

**Description.** Two Opus dispatches this sprint died identically [measured]:

| | Seat | Last words before termination | Artifacts on disk |
|---|---|---|---|
| 1 | Director of Research — PREREG-002 restatement | *"I have what I need. Writing the memo first."* | none |
| 2 | Head of Quant Validation — ML trial-accounting ruling | *"I have what I need. Writing the ruling."* | none |

Both terminated with `API Error: Connection closed mid-response`, both **at the transition
from reading to writing**, both after a large multi-document read, both leaving **nothing on
disk**. Verified after each: registry intact at 0/0, suite passing, tree unmodified apart
from the live capture files. **No corruption in either case — the cost is pure budget.**

**Cost.** Under Standing Order 001 §2, *"failed invocations count as spent."* Two failures
plus two resumes is **4 Opus units consumed to produce 2 artifacts**, against a sprint tier
of 12. **The failure rate has consumed 17% of the sprint's scarcest resource for zero
output.**

**Mitigation applied.** Both resumes carried an explicit instruction to write to disk
incrementally — create the file with its skeleton, fill it section by section — so a
subsequent termination costs one section rather than everything. The Director's resumed run
completed under that instruction. Whether the instruction caused the completion or the
retry did is **not established** and should not be claimed.

**Why MEDIUM and not HIGH, stated because the temptation runs the other way.** §8 forbids
under-rating an issue to avoid triggering a §4 interrupt, so the reasoning is on the record:
there is no data corruption, no record corruption, no incorrect number, and no lost
analysis that was not re-derivable — the failures are recoverable and the recovery path is
known and tested. The cost is budget alone.

**Escalation trigger, pre-committed so it is not a judgment call later.** **A third
occurrence makes this HIGH**, because at that rate the failure mode threatens §2 budget
exhaustion, and **budget exhaustion in either tier is itself a §4 hard interrupt.** At that
point the correct response is not another resume but a dispatch-design change — smaller
reads, split briefs, or artifacts written before analysis rather than after.

**What would change the assessment.** Evidence that the terminations correlate with
something the firm controls — read volume, context size, dispatch length — rather than with
infrastructure. None has been gathered; two data points do not support a claim either way,
and the CIO is not going to spend a unit measuring it while the sprint's objectives are
unmet. Recorded as `[assumed]`, not `[measured]`.

**Resolution:** open — monitoring, with the escalation trigger above.
**Pattern tag:** `dispatch-dies-at-read-write-transition`
