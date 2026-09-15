# THE CASTELLAN CASEBOOK — Governed Agent Operations

**Purpose:** convert the firm's incidents into portable engineering lessons. One artifact, two customers: internally it is institutional memory; anonymized, it is the consulting bundle's diagnostic checklist and publishable content.
**Harvest cadence:** one Sonnet unit at each sprint close sweeps the issue log for entries that generalize. Not every issue is a case — a case must teach a rule that applies *outside* the system that produced it.

## Template (five fields, all required)

```
CASE-N · [short name]
CONTEXT:      what the system was doing when it failed (2-3 sentences)
FAILURE SHAPE: the general form of the failure, named abstractly
FIX:          what actually resolved it, mechanically
RULE:         the portable principle, stated so a stranger could apply it
APPLIES TO:   which other systems inherit this risk
```

---

## CASE-1 · The test that couldn't fail
**CONTEXT:** An acceptance criterion said "a typo must not brick a family." The implementation inverted its own criterion — a wrong passphrase succeeded and permanently destroyed the protected resource — and the test claiming to cover the criterion passed anyway. Later, a separately authored test passed *before its feature existed* (a fixture made unfailable by a scale-invariance property).
**FAILURE SHAPE:** Test-passes-while-property-fails. Green suites measure what was built, not what was protected.
**FIX:** Red-first ordering as a hard rule — tests are written and *run failing* before any implementation, with the verbatim red output a required deliverable. A test that passes red is reported as a defect in the test.
**RULE:** Authorship separation (reviewer writes the tests) is necessary but insufficient; only executing the test against the absent feature proves it constrains anything.
**APPLIES TO:** Any system where AI writes both code and tests; any acceptance process that counts tests instead of executing their failure modes.

## CASE-2 · The narrated number
**CONTEXT:** The orchestrator ran a script that computed figures, then printed a conclusion whose numbers were hardcoded into the string literal rather than derived from the query. The arithmetic above it was also wrong by 100×. Self-caught, same exchange.
**FAILURE SHAPE:** An agent asserting a result adjacent to a computation, so the assertion inherits the computation's credibility without its provenance.
**FIX:** Figures out, reading stated separately and attributed. Structurally: anything counted, deduped, or aggregated is done by deterministic code; models interpret outputs, never produce them.
**RULE:** In any agent pipeline, separate the layer that computes from the layer that narrates — and make the computed artifact the thing downstream consumers read.
**APPLIES TO:** Every LLM analytics/reporting workflow; the "reduce" stage of any fan-out; dashboards summarized by agents.

## CASE-3 · Isolation that wasn't
**CONTEXT:** Parallel agents in one working tree overwrote each other's changes (twice). Worktree isolation was adopted — and then a dead agent's schema migration hit the live production database anyway, from inside its isolated tree, via an absolute path. The "verified untouched" check had compared row counts, not schema.
**FAILURE SHAPE:** Isolation defined over the filesystem while the blast radius includes external state (databases, APIs, shared services). Verification checked the wrong invariant.
**FIX:** Per-agent worktrees *plus* external-state rules: read-only DB connections by default, write access granted per-dispatch, schema changes only through a sanctioned migration path. Verification tests the failure that actually happened, not the one imagined.
**RULE:** Any two workers touching the same externally addressed resource have a hidden edge; audit for shared *resources*, not shared files — and calibrate "verified untouched" against a real incident.
**APPLIES TO:** All parallel agent systems with databases, queues, or rate-limited APIs; CI fleets; anything the popular worktree advice is sold to.

## CASE-4 · The success that captured nothing
**CONTEXT:** A scheduled data-capture job was installed and the installer returned success. The job was pointing at the wrong interpreter and had captured zero data at exit code 1. Separately, a merge step nearly proceeded on partial agent output after two of three dispatches died mid-write.
**FAILURE SHAPE:** Silent node failure — success signals that measure the wrapper, not the work; merges that don't count their inputs.
**FIX:** Verify by output, not by return code (the first real captured record is the install test). Every fan-in counts deliverables against dispatches and flags gaps; never synthesize on a partial set.
**RULE:** A completed step proves nothing until its *product* is observed; a merge without an expected-count check will eventually ship a report missing its most important input.
**APPLIES TO:** Cron/launchd anything; multi-agent fan-ins; ETL pipelines; overnight autonomous loops ("review what it shipped" requires knowing what didn't ship).

## CASE-5 · Edges that carry authority, not data
**CONTEXT:** A sequencing audit ("does this step need the previous step's output?") would have marked several of the firm's blocking dependencies as deletable, because no data flowed along them — ingest waiting on a reviewer's written acceptance, a seal waiting on a mechanism ruling.
**FAILURE SHAPE:** Optimizing a workflow graph by data-dependency alone deletes control edges, because controls often pass authorization, not payloads.
**FIX:** A three-type edge taxonomy: data edges (delete when empty), authorization edges (never deleted for speed), budget edges (sequencing imposed by resource ceilings). Speed audits run on type one only.
**RULE:** Before parallelizing, classify every edge; "this wait carries no data" is not the same claim as "this wait serves no purpose."
**APPLIES TO:** Any governed pipeline being sped up — compliance flows, deploy gates, financial controls — and every consultant running a fake-edge audit.

## CASE-6 · The counter that counts itself
**CONTEXT:** The system's core statistic depends on N, the number of attempts searched. N was self-reported, then enforced in code (every run logs), then discovered to be under-counted anyway: the searching agent's *prior knowledge* embodies attempts no registry sees, and a declared correction ("seed N at a floor") was issued against a schema with no column to hold it — a binding control existing as paperwork.
**FAILURE SHAPE:** Selection effects hiding upstream of instrumentation; controls declared but not mechanically representable.
**FIX:** Enforcement in the code path (the only way to run is the way that logs); honest bounds where reconstruction is impossible; and the precedent that the real cure is a frozen commitment tested on data that postdates it — forward evidence beats retrospective counting.
**RULE:** Ask of every metric: what selection happened before this counter existed, and can the schema actually hold the correction you just mandated? A control that exists as an empty column reads as satisfied in every audit that checks only for the field.
**APPLIES TO:** A/B testing programs, ML experiment tracking, any research org measuring its own search, any policy "adopted" without an enforcement mechanism.

## CASE-7 · The optimizer and the frozen rule
**CONTEXT:** Multiple pressures arose to soften commitments precisely when they bound: a kill condition's silence clause predicted "someone will try to soften this"; a compute ceiling became inconvenient exactly at the finish line; an acceptance clause had to specify that conditions may not be met by weakening assertions.
**FAILURE SHAPE:** Goodhart erosion — the rules an optimizer most wants to bend are the ones doing the protecting, and the request to bend always arrives wearing a good reason.
**FIX:** Anchors: pre-committed cuts named before they're needed; void-if-weakened clauses with diff audits; interrupt sets that widen freely but narrow only by the principal in writing; defaults that kill (silence-kill) with revival requiring a logged override.
**RULE:** Decide which rules are frozen while they're cheap, name the pressure that will arrive, and make softening require more ceremony than complying. A graph is only as honest as the parts that refuse to move.
**APPLIES TO:** Autonomous loops with goals, OKR systems, trading risk limits, any AI system given an objective and a budget.

---

## CASE-8 · The label that lies
**CONTEXT:** Five defects in one sprint shared a shape: a flag computed and then written only to a note while the verdict stayed PASS; a t-statistic assuming independence the underlying series measurably violated by ρ = 0.83; two pipeline stages both reporting a count called "rounds" that differed 20× because they counted different units; a two-stage budget described in prose but sealed at a flat number that made the described second gate unreachable; a test named for one protection that a second, independent protection actually satisfied in the fixture that mattered.
**FAILURE SHAPE:** Semantic drift between a name and its referent — the reader (operator, gate, or downstream test) trusts the label instead of tracing what is actually computed, gated on, or discriminated, and does so at exactly the moment a decision is being made on it.
**FIX:** For every name that appears in a verdict, report, or acceptance test, verify by construction — not by re-reading the docstring — what actually fires or is counted. Where two pipeline stages report a same-named quantity, unify the unit or rename one of them.
**RULE:** A name is a claim, not a proof. Before trusting what a field, statistic, or test says it does, trace what it actually computes and what consumes its output — the moment of highest risk is when someone reads the label to decide something, not when the code was written.
**APPLIES TO:** Any dashboard or CLI whose column headers outlive a units change; any acceptance-test suite named after intent rather than assertion; any statistical pipeline that quotes a headline number without stating its assumptions; monitoring systems where a "success" field is computed but not wired to the alert.
**Traces to:** I-022, I-050, I-093, I-105, I-113.

## CASE-9 · A control that is asserted rather than computed is not a control
**CONTEXT:** A trial-budget check computed an over-budget flag and discarded it before the verdict. An escalation rule for revising a sealed choice was written into a binding document and could not be executed against the registry it was meant to gate. A two-stage budget was described in prose exactly as intended, but the harness enforced only the number that was actually registered, so the described second stage never existed. An inheritance-count formula was copied approvingly into four clauses across two documents, and each copy re-stated the same arithmetic error, because quoting a rule verifies nothing about it.
**FAILURE SHAPE:** A control exists on paper — in prose, in a docstring, in a note field — and nowhere does the software compute and enforce it; every reader who checks the document instead of the code concludes the protection exists.
**FIX:** For each described control, identify the single computed source of truth that enforces it (the registry, the gate function), and stop restating what that source does anywhere else in prose. A rule that cannot yet be executed is NOT PROTECTED, not "specified."
**RULE:** A control exists exactly where the harness reads it, and nowhere else. If you can point to the paragraph but not the function, you have a description, not a control — and the gap will be found by whoever is under the most pressure to find it.
**APPLIES TO:** Compliance programs whose policy documents describe checks no system runs; financial risk limits stated in a memo but not wired into the order-management system; any spec-then-implement workflow where the spec is treated as binding evidence in its own right.
**Traces to:** I-022, I-053, I-055, I-105.

## CASE-10 · The implementer who wouldn't fix it, and the authority who wouldn't soften it
**CONTEXT:** An implementer, building exactly to a written specification, found that the spec's own formula violated the spec's own stated invariant — and had already located, verified, and bench-tested the one-line correction that would turn every failing test green with zero collateral. It filed an issue and left the tests red rather than apply the fix itself. The authority owning the spec then adjudicated: it held a respectable, correctly-reasoned argument for retiring the one test that had caught its own error, and declined, ruling the test required and recording explicitly that the option to retire it had existed.
**FAILURE SHAPE:** Unauthorized self-correction at either end of a review relationship — an implementer patching the artifact that grades it, or an authority quietly relaxing the control presently inconvenient to itself — both erase the evidence that the review relationship held under real pressure to bypass it.
**FIX:** The implementer escalates in writing rather than edits; the authority adjudicates and states in its ruling whether it considered and rejected weakening the control, not just what it decided.
**RULE:** The disguise under which self-authorized shortcuts arrive is "obviously correct and free" — that is precisely when process discipline is worth the most and tested the least. A system's control integrity is best evidenced not by outcomes that never tested it, but by a logged instance of the authority holding the power to relax a control choosing not to, and saying so.
**APPLIES TO:** Any code-review or grading pipeline where the same party could plausibly fix both the implementation and the test that judges it; any auditor or regulator who could quietly loosen a rule constraining its own prior work; peer-review systems generally.
**Traces to:** I-065, I-077.

## CASE-11 · Disclosed but never logged, in both directions
**CONTEXT:** A hardcoded PASS-producing defect was disclosed in an implementation document but never entered the Issue Log — "a disclosed defect that reaches no log is functionally undisclosed." Later, four Validation rulings that closed Issue Log entries were recorded in the decision record and never written back into the Issue Log, so the index overstated the firm's own open-HIGH count and misled the seat reading it — "a closure that reaches no log is functionally not closed." Assembling this casebook surfaced a third instance in the same sprint: a filing itself, narrated as "I-059 filed" in the decision record and cited twice by number from inside two other live Issue Log entries as though resolvable, with no corresponding entry ever written into the log.
**FAILURE SHAPE:** A two-track record — narrative log and structured index — where writing to the narrative is silently treated as equivalent to writing to the index, in both the opening and the closing direction; naming the failure in one direction does not fix it in the other.
**FIX:** One rule, enforced mechanically rather than remembered: every open, close, or filing event is written into the index in the same commit as the narrative record. An entry that exists only in prose elsewhere does not exist.
**RULE:** An index is only as trustworthy as its write discipline in both directions. Ask not just "was this ever mentioned" but "is it queryable from the one place a reader or a script will actually check" — and audit for the mirror case as hard as the original one, because fixing one direction increases confidence exactly where it should not.
**APPLIES TO:** Bug trackers versus commit messages; runbooks versus post-mortems; any system where a narrative changelog and a structured status field can drift apart; regulatory disclosure logs kept in two places by convention rather than by constraint.
**Traces to:** I-022, I-092, I-120 (filed against the log itself during this harvest).

## CASE-12 · The step nobody but the principal can test
**CONTEXT:** Three runbook defects surfaced in one sprint, all inside steps marked for execution only by the human principal — the one actor no automated seat can run ahead of time to check. One was unexecutable in two places on first run. A second ran correctly but pointed two invoked scripts at two different destinations, so a health check silently supervised an empty directory. A third was found only because a seat, adopting a new convention, sat down to write the verification command for a step and could not answer "which interpreter?" without discovering the step was wrong.
**FAILURE SHAPE:** The class of instruction only a specific privileged actor can execute is systematically the least-tested class of instruction in any runbook, because every other step is dry-run or unit-tested by the agent that writes it, and this one structurally cannot be.
**FIX:** Every principal-only (or otherwise privileged-only) step ships its own verification command at authoring time, before it is ever run. A step without pasted output attached to the record is "written," never "executed," and is not trusted as equivalent to a tested step.
**RULE:** Rank runbook steps by who can test them, not by who performs them. The step only the most senior or most privileged actor can run is the step most likely to be silently wrong — and the fix is not more careful writing, it is a verification command authored in the same breath as the instruction.
**APPLIES TO:** Any deployment runbook with a manual human step; any on-call escalation procedure with a step only an incident commander performs; infrastructure-as-code where a break-glass admin action isn't covered by CI.
**Traces to:** I-090, I-091.

## CASE-13 · The fix that didn't generalize to its own siblings
**CONTEXT:** A Gate 1 criterion's t-statistic was found to silently assume serial independence the firm's own data violated by a measured factor of 3.3×. The correction was scoped and shipped for that one statistic. Answering an unrelated question days later, the same reviewer discovered two further criteria — a minimum-backtest-length function and a Deflated Sharpe Ratio — computed on the identical unstated independence assumption, in the same permissive direction, untouched by the first fix, with the correct remedy for one of them having already been on record for a different, narrower use one dispatch earlier.
**FAILURE SHAPE:** A correct fix is applied exactly where the defect was observed and no further; sibling computations sharing the identical root assumption are left standing until someone happens to ask the generalization question while working on something else.
**FIX:** When a statistical or logical assumption is found wrong in one place, enumerate every other computation in the codebase built on the identical assumption before declaring the finding closed, rather than waiting for each sibling to be independently rediscovered.
**RULE:** "We already knew this" is not the same claim as "we applied it everywhere it is needed." A fix's true scope is defined by the assumption it corrects, not by the function where the correction was first written — audit for siblings at the moment the first defect is found, while the assumption is fresh, not later.
**APPLIES TO:** Any codebase with parallel or duplicated statistical estimators (VaR variants, risk-adjusted return variants); security patches applied to one endpoint of a family of near-identical endpoints; any bug found in a "shared" formula that has actually been copy-pasted into several places.
**Traces to:** I-050, I-057.

## CASE-14 · The control that admits its own threat model
**CONTEXT:** An append-only authorization log had no tamper detection at all — any row could be altered by raw SQL with nothing to notice — while a sibling table one level up carried a full shadow-copy hash for exactly that reason. Separately, a two-party countersignature rule meant to require a discretionary action be approved by a distinct party turned out to rest on two self-declared strings a single actor could write about itself; nothing in the system proved which party actually acted. Both were filed not as silent gaps but as explicit statements of exactly what the control does and does not defend against.
**FAILURE SHAPE:** A mechanically-enforced control is read by everyone downstream as covering a threat model broader than the one it actually covers, because the control's existence is visible but its scope is not stated anywhere.
**FIX:** For every authorization or integrity control, write down explicitly what class of actor it defends against (an honest party under schedule pressure vs. a determined adversary) and what it does not, in the same document that describes the control — and file the gap as a disclosure even where no fix is requested, so the boundary is a decision on record rather than an assumption a later reader makes.
**RULE:** A working control is not the same claim as a sufficient control. Before relying on any authorization mechanism, ask what kind of actor it actually stops — if the honest answer is "an honest party, not a determined one," say that in the same place the control is documented, because an unstated threat model gets over-read exactly at the moment someone needs the control to hold.
**APPLIES TO:** Any access-control or audit-log system evaluated only by "does it run," not "against whom"; two-person-integrity rules implemented as two self-attested fields; any compliance control whose real strength is narrower than its name implies.
**Traces to:** I-102, I-103.

## CASE-15 · The guard that counted the wrong side
**CONTEXT:** A six-source intake pipeline fanned out to parallel fetchers, reduced their combined output through a date filter, then verified what survived. The run completed successfully and reported zero items. A fan-in guard, installed specifically because of CASE-4 and written into the merge protocol as an adopted control, reported six of six fetchers returned and zero gaps — **and that report was entirely correct.** All six had succeeded; twenty-seven items existed. The reduce stage one step downstream compared each item's date against a variable that was `undefined` (its arguments had arrived as a JSON string rather than an object), and because `"2026-08-02" >= undefined` evaluates to `false`, every item was discarded. The pipeline reported success while holding nothing, with a correct guard sitting immediately beside the loss.
**FAILURE SHAPE:** A guard verifies the boundary it was placed at while the loss occurs at the adjacent boundary it does not measure. The guard is not broken, not stale, and not lying — it certifies the wrong invariant, and its accuracy is what makes the empty result read as a real finding.
**FIX:** Move the assertion to the output side of the stage that can empty its input. Count what *leaves* the reduce, compare it to what entered, and treat any total-loss transition as a finding requiring an explicit reason rather than a silently valid state. Where a stage legitimately can return nothing, it must say so as an outcome, not as an absence.
**RULE:** **A fan-in guard must count what leaves the stage it guards, not what arrives at it.** A guard placed at the input measures the health of everything upstream and nothing downstream — so the more reliable the fan-out becomes, the more reassuring the guard reads at exactly the moment the reduce is destroying the payload.
**APPLIES TO:** Any ETL or agent pipeline with a filter, join, or dedupe between collection and use; any system where "0 results" is a valid answer and therefore indistinguishable from total loss; loosely-typed filter predicates where a comparison against `undefined`/`null`/`NaN` silently returns false rather than raising; any monitoring built on upstream success rates rather than end-to-end yield.
**DISTINGUISHED FROM CASE-4:** In CASE-4 nothing verified the output, and the fix was to add verification by output and fan-in counts. Here that fix was already adopted and running, and it worked. The residual failure is not missing verification but **correctly-placed verification of the wrong quantity** — which is the harder version, because the green signal is genuine and no amount of trusting it more would have helped.
**Traces to:** Watchtower cycle 2026-08-10, §"Run integrity".

## CASE-16 · The count stated in four documents and computed in none
**CONTEXT:** A seven-item checklist existed to make an irreversible act mechanical — "no judgment" was its stated property — and it was the only artifact the executing party would read at the moment of the act. Two of its items carried assertions that had been true when written and were false when read. Item 1 named five blocking preconditions as open; three had been discharged weeks earlier by rulings that never reached the document. Item 6 stated the expected read-back after four vault seals as "four authorization rows"; the real number is eight, because each seal call writes two — one for the file write, one for the event log, both deliberate and both documented in the code. Neither number had ever been computed. Both had been transcribed forward from a first statement into three further documents, gaining apparent corroboration at every hop while remaining a single unverified claim.
**FAILURE SHAPE:** A quantity is asserted in prose beside a thing that can be counted, and the assertion is copied rather than recomputed. Each copy makes the number look better-sourced while adding no evidence, so the claim's apparent support grows monotonically with the number of places it is wrong in. It survives exactly until someone counts — and the checklist's own promise of "no judgment" guarantees that the first person to count is whoever is executing the irreversible act, at the worst possible moment.
**FIX:** Give every stated read-back an executable form. The script that performs the step computes each expected count itself, prints all of them, and exits non-zero on any mismatch; the prose states what the script checks rather than what someone remembered. Where a count cannot be computed in advance, run the operation once against a throwaway instance of the real system and count there — the throwaway is cheap precisely because the real act is not. Items whose truth is time-varying (a list of open preconditions, a schema, a row count) get a named source and a re-verification step, never a transcription.
**RULE:** **A checklist that promises "no judgment" must contain no number that has not been computed.** The promise and the unverified number are incompatible: a false item leaves the executor only two moves, halting a correct operation on a false alarm or exercising the judgment the checklist swore was unnecessary, and both are defects. Corollary, for the writer: transcription is not corroboration — a number appearing in four documents is one claim with three copies, and the count of places it appears carries no evidential weight whatever.
**APPLIES TO:** Runbooks and deployment checklists with expected-output blocks; migration and cutover procedures; any "expected: N rows" assertion in an operational document; pre-registration and compliance artifacts that freeze at a moment and are read long after; any control whose stated scope was written before its implementation grew a second internal step.
**DISTINGUISHED FROM CASE-9:** CASE-9 concerns a *control* asserted rather than computed — the mechanism itself does nothing. Here the mechanism works correctly; both authorization rows are genuinely written and genuinely correct. What is wrong is only the *expectation stated beside it*, which makes this the quieter version: nothing fails, nothing is missing, and the discrepancy surfaces as a correct system appearing to misbehave.
**Traces to:** I-328, I-367.

---

*Harvest note for Sprint 3: this sprint's yield (7 cases from ~68 filed entries, I-046–I-120) ran higher than the CIO's four-to-eight estimate's midpoint but stayed inside it. Two candidate seams were examined and rejected — see the Rider C return for the reasoning, filed separately from this document per the casebook's own rule against padding it with the audit trail.*
