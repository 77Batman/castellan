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

*Harvest note for Sprint 2: candidate cases already visible — the delayed-seal principle (commitment timing vs. defect discovery), the interrupt-queue design (mechanical triggers vs. adjectives), and whatever the [would-have-asked] audit reveals about delegation calibration.*
