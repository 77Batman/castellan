# VALIDATION ACCEPTANCE 001 — the P-1 Holdout Vault implementation (I-005)

**Seat:** Head of Quantitative Validation
**Date:** 2026-07-28
**Rules on:** `research/DATA-IMPL-001-p1-vault.md` against `VALIDATION-RULING-001-holdout-regime.md` §5
(A1–F4); the F1/F2 collision escalated in DATA-IMPL-001 §3; the D-006 pre-registration-freeze rider;
and I-010.
**Binding on:** Seats 1, 2, 6–10. Appealable only to the Principal, in writing.

---

## 1. Scope and what was read / run

**Read in full:** `.claude/agents/quant-validation.md`; `VALIDATION-RULING-001-holdout-regime.md`
§2–§7; `VALIDATION-RULING-002-c-placement.md` §3 (R1–R4); `DATA-IMPL-001-p1-vault.md`;
`harness/castellan/{holdout,data,registry,gates,errors}.py`; `harness/tests/test_holdout_p1.py`;
`harness/tests/test_harness.py`; `harness/README.md`; `logs/DECISION_RECORD.md` D-005/D-006;
`logs/ISSUE_LOG.md` I-005, I-007–I-013.

**Run:** `python3 -m pytest harness/tests -q` → **63 passed, 1 failed of 64 collected** [measured].
The one failure is `test_harness.py::test_holdout_locks_splits_and_opens_once`, exactly as Seat 9
disclosed.

**Also run — five read-only probes against the shipped code in a temp directory**, because a test
that passes is evidence about the test, not about the code. Nothing in the repo was modified; no
data was fetched; no backtest was run; nothing was committed. Every probe result below is labelled
[measured] and is reproducible from §3.

**Not done:** Gate 0 intake (reserved to my fourth Opus unit, per D-006).

---

## 2. ACCEPTANCE VERDICT

> ### GRANTED WITH CONDITIONS.
> ### Ingest (I-001) remains BLOCKED. It unblocks automatically when conditions **C-1 through C-7**
> ### have landed and the suite is 100% green — no further Validation invocation is required.

The implementation is competent, faithful to the design, and Seat 9's disclosure was materially
above the bar this firm has any right to expect — it escalated rather than edited, it reported
63/64 rather than rounding to "green", it flagged seven interpretive decisions unprompted, and it
volunteered the git-history problem that became I-013. I am recording that because the incentive
this seat creates should not be "disclose less."

I am nonetheless withholding unconditional acceptance, on five findings that the tests did not
catch and that the implementation note did not disclose. Four of them I demonstrated by execution
against the shipped code [measured]. The one that decides it:

> **A wrong-but-non-empty passphrase at `acquire_once()` does not refuse. It fetches, seals the
> holdout under the typo, retires the vault, and the Principal can never decrypt it.** The family is
> permanently bricked with no recovery path. Acceptance criterion C4's own text is *"a typo must not
> brick a family"* [cited — Ruling 001 §5 C4]. The implementation delivers precisely the outcome the
> criterion was written to forbid, and the test that claims to cover C4 tests only the empty string,
> which is not the typo anyone will actually make.

Granting on my signature would mean the firm begins consuming data with the D2 ceiling opt-in, a
second un-ceilinged ingest path open, the Gate-1 holdout criterion carrying a caller-asserted
bypass that I measured returning **PASS on zero registry events**, and a one-character slip able to
destroy a hypothesis family. That is not a signature I can give.

### Conditions — blocking. All are precedent to the first ingest call.

| # | Condition | Why | Deadline |
|---|---|---|---|
| **C-1** | Land the F1/F2 replacement test per §4, in `test_harness.py`, in place. Suite to 0 failed / 0 skipped / 0 xfail. | Ruling 001 F2 | 2026-07-30 |
| **C-2** | Seal-time passphrase verifier; `acquire_once` refuses a wrong passphrase **before any fetch**, does not retire. 3 negative tests. | C4 is currently defeated | 2026-07-30 |
| **C-3** | `PITStore` becomes a **required** constructor argument; `seal()` raises without one. 1 negative test. | D2 must not be opt-in | 2026-07-30 |
| **C-4** | `ingest_documents()` enforces the same ceiling. 2 tests (1 negative, asserting row count unchanged). | Second ingest path bypasses D2 entirely | 2026-07-30 |
| **C-5** | Normalise `event_time` to UTC at ingest so store comparisons are instant comparisons, not string comparisons. 2 tests incl. the measured false negative. | The D1 leak detector currently misses real leaks | 2026-07-30 |
| **C-6** | **Remove** the `holdout_opened_once` parameter from `evaluate_gate1`. Removal, not deprecation — same logic as F1. | Measured: returns PASS with zero events | 2026-07-30 |
| **C-7** | `acquire_once` refuses a fetched frame containing any row with `event_time <= C`, as a C6-class acquisition failure. 1 negative test. | Measured: the full in-sample history seals as "the holdout" and the Gate reads PASS | 2026-07-30 |

**Suite target after C-1…C-7: ≥ 73 collected, 0 failed, 0 skipped, 0 xfail.** The count is
secondary; what I require is that every negative case named in §3 and §4 exists and passes.

**Acceptance is void if any condition is met by weakening an assertion rather than strengthening
the code.** That is checkable in the diff and I expect the CIO to check it. If a condition turns out
to be genuinely unimplementable, the correct response is a written escalation to me — the same
response Seat 9 already got right once.

### Conditions — non-blocking, deadline sprint close 2026-08-11

| # | Condition |
|---|---|
| **C-8** | Strengthen `test_C8_payload_encrypted_at_rest`. Its assertions are vacuous — see §3. |
| **C-9** | `_lift_ceiling` records which acquisition lifted it (`lifted_utc` + event id), not just `active=0`. |
| **C-10** | A3: add the untested malformed-`cutoff` branch and `source` to the parametrisation. |

### Conditions — deadline: before Gate 0 intake of the first family (i.e. before my fourth unit)

**P1–P8** (§5) and the R1 report/pre-registration fields. These gate my own next invocation: I cannot
take a Gate 0 intake for a family whose binding fields have nowhere to live in the registry.

### Conditions — deadline: before the first Gate 1 evaluation

**G1–G5** (§6, I-010).

---

## 3. Item-by-item audit — A1 through F4

Legend: **C** covered · **P** partially covered · **N** not covered / criterion defeated.

| Item | | Finding |
|---|---|---|
| A1 | C | Spec written, event carries sha256, exactly one event, fields round-trip. |
| A2 | C | Re-seal raises. Preserves "C cannot be chosen after the fact." |
| A3 | **P** | Future cutoff permitted (asserts sealed, not "and recorded" — cosmetic). Malformed-field parametrisation covers 4 of 6 required fields; **`source` and the malformed-`cutoff` branch are untested**, and the `cutoff` branch is dead code today. → C-10 |
| A4 | C | Registry hash == disk hash. Byte-level detection is proven by C3, not by A4 itself; Seat 9 disclosed this and I accept the split. |
| B1 | C | Ceiling row written at seal, correct family. |
| B2 | C | `event_time <= C` accepted; 181 rows ending exactly on C. |
| B3 | C | **Atomicity is genuinely asserted**, not merely the raise: row count before == after. Enforcement runs before any write, so it is atomic by construction, not by rollback. Weak spot: the baseline is 0, so the test does not prove pre-existing rows survive a refusal. Not blocking. |
| B4 | C | Un-ceilinged dataset unaffected. |
| B5 | **P** | Bad-hash lift raises and the ceiling survives. Not tested: that a ceiling cannot be **raised**. It cannot be, in fact — enforcement is conjunctive over all active ceilings and `set_holdout_ceiling` refuses a duplicate `(source, dataset_id, family)` even after a lift — but that is proven by reading, not by test. Direct SQL is out of scope by the design's own admission. |
| B6 | **P** | tz-naive and tz-UTC tested, at a UTC-midnight boundary. **The tz-aware case that actually breaks — a non-UTC zone — is untested**, and I measured it breaking a different control. See D1. → C-5 |
| C1 | C | Attempt-before-acquired ordering asserted by index comparison; terminal state asserted. |
| C2 | C | Second acquisition raises and logs. |
| C3 | C | **`assert fetch.calls == 0` — a genuine no-network-call assertion**, via an injected counting callable. This is what the criterion asked for. |
| C4 | **N** | **The criterion is defeated.** The test asserts `fetch.calls == 0` correctly, but only for `passphrase=""`. The implementation's gate is `if not passphrase or not passphrase.strip()` — a presence check. Measured, against the shipped code: `acquire_once("hunter3-TYPO", …)` **succeeded**, state → `RETIRED`; `read_acquired("hunter3")` → `HoldoutPassphraseError`; re-acquisition → `HoldoutRetiredError`. **The holdout is permanently unreadable and the family cannot be re-acquired.** C4's stated purpose is the opposite. Seat 9 flagged the presence-vs-cryptographic distinction (interpretive decision 2) but **did not disclose this consequence**. → C-2 |
| C5 | C | Both clauses. Premature fetch raises and logs; a 60-day window yields Gate verdict **FAIL**, and the test asserts FAIL and separately asserts *not* INSUFFICIENT-DATA. Correct. |
| C6 | C | Failure → `ACQUISITION_FAILED`, not retired, next attempt blocked. |
| C7 | C | Authorized retry succeeds and the count reaches the report note. Asserted on the note text. |
| C8 | **N** | **The assertions cannot fail.** They check that `b"918273"` and `b"918273.0"` are absent from `payload.enc`. Measured: an **unencrypted** parquet of the same frame contains neither string — parquet stores doubles as binary. The test passes identically against plaintext. It is not evidence of encryption. (The property does hold — C9 round-trips through Fernet — but this test is not what establishes it.) → C-8 |
| C9 | C | Real cryptographic verification, wrong passphrase raises, correct one round-trips. The one place passphrase correctness is actually checked today. |
| C10 | C | Schema mismatch → acquisition failure, not retired, retry gated. |
| D1 | **P** | The test is good and the Gate FAILs on a real leak. But the control has a measured false negative: `PITStore` persists `event_time` as `pd.Timestamp(et).isoformat()`, **keeping the caller's UTC offset**, and every store query (`rows_in_window`, `asof`, `_latest_map`) compares those as **strings**. Measured: a bar at `America/New_York 2024-06-30 21:00` = `2024-07-01T01:00Z`, genuinely inside a holdout window opening at `C = 2024-07-01T00:00Z`, is stored as `2024-06-30T21:00:00-04:00` and **`rows_in_window` returns 0 rows**. The leak detector — the only mechanical control in §2.4 — silently misses it. (The D2 ceiling is *not* affected: `_enforce_holdout_ceiling` converts to UTC before comparing Timestamps, and I confirmed it refuses the same bar.) → C-5 |
| D2 | C | Clean case, no leak event, criterion not FAIL. |
| E1 | C | **Both directions, as required.** A's second-acquisition violation → A FAIL, B not FAIL. A's acquisition alone → B **INSUFFICIENT-DATA**, not satisfied. This is the I-007 fix and it is properly tested. |
| E2 | **P** | Correct on the default path. But `evaluate_gate1(..., holdout_opened_once=True)` bypasses the entire family-scoped block. Measured on a family with **zero** holdout events of any kind: criterion verdict **PASS**. A caller-asserted holdout status is a narrated number inside the firm's most-protected criterion, and Amendment A1/A2 exists to make exactly that inadmissible. Undisclosed. → C-6 |
| E3 | C | Both hashes on the report, family-scoped, rendered in markdown. |
| F1 | C | `lock()`/`open_once()` hard-raise `HoldoutRegimeError`. Not deprecated-with-warning. |
| F2 | **N** | Not met — 63/64. Ruled in §4; the path to green is C-1. |
| F3 | C | README holdout paragraph rewritten to the P-1 regime; "(16 tests)" corrected to 64. It also discloses the failing test by name. Closes I-008 on C-1 landing. |
| F4 | C | `predecessor_family` validated against registration, chain is cycle-safe, successor N starts at the predecessor's total, predecessor's own count untouched. |

### Seat 9's seven interpretive decisions — did any quietly weaken an item?

| # | Decision | Ruling |
|---|---|---|
| 1 | `dataset_id` → existing `symbol` column | **Accepted.** Correct call; widening the schema for a duplicate field is unjustified. The stated break case (one symbol, two logical feeds) is real and I want it re-raised if it arrives, not silently keyed around. |
| 2 | Passphrase presence at acquire, crypto at re-read | **Rejected — this is the one that weakened an item.** See C4. Seat 9 correctly identified the ambiguity and correctly declined to invent a design; the reading it chose is the permissive one, and the disclosure omitted that the permissive reading brings the bricking outcome C4 forbids. → C-2 |
| 3 | `ACQUIRED` folded into `RETIRED` | **Accepted.** C1 does say success moves straight to retired. No item weakened. |
| 4 | Ceiling lift gated by spec-hash rather than a token | **Accepted.** Sound: the hash is already the integrity anchor, and inventing a second capability token adds a second thing to lose. But see C-9 — the lift is permanent and dataset-wide, where D2 says "scoped to that single sealed acquisition." Harmless in fact (vault retired, payload sealed, leak check already run) and the audit trail must still name the acquisition. |
| 5 | `returns_matrix` pooled transitively too | **Accepted and endorsed.** This is a genuine improvement over what F4 asked for, and the reasoning — DSR's N and PBO's matrix must be drawn from the same trial set — is the right reasoning. Had it not been done, I would have required it. |
| 6 | Retry gate fires before the "attempted" event | **Accepted.** "Attempted" should mean "about to make the network call." The separate `holdout_retry_unauthorized_attempt` event preserves the audit trail. |
| 7 | `instrument_identity` unenforced per-venue | **Accepted, and it stays open.** Ruling 001 §3.4 marked the Polymarket on-chain-id assumption `[assumed]`; it is still assumed. This does not block ingest, but the forward-lag family cannot be pre-registered until `DATA-SPEC-polymarket-usable-history.md` settles it, because `instrument_identity` is a binding spec field and a mutable slug in that slot retires the vault the first time the venue renames anything. |

### Not in A1–F4, found anyway

- **`ingest_documents()` has no ceiling enforcement** [measured — `_enforce_holdout_ceiling` is
  called from `ingest()` only]. A second, fully open ingest path. For price data this is minor; for
  an event-contract venue where resolution documents are the payload, it is the leak path. D2's
  governing principle is that enforcement lives below the caller — it currently lives below one
  caller. → C-4
- **Ruling 001 §2.4's required field does not exist.** "The Validation Report must state on its face
  that the holdout is historical" — *"That statement is now a required field."* `ValidationReport`
  has no such field, and R1 (accepted binding by D-006) extends it to FORWARD/HISTORICAL with
  mandatory boilerplate. Every report the harness can currently produce is defective by R1. Folded
  into the P-series deadline, since the classification must live in the pre-registration too.
- **§3.4's spec-amendment path does not exist.** No `holdout_spec_amended` event kind, and no
  transport/provenance fields in the spec, so "the amendment count per family is reported at Gate 1"
  is unimplementable. The bricking failure mode §3.4 warned about is avoided by omission (transport
  simply isn't recorded), which is the safe direction. Logged, not conditioned.

---

## 4. RULING on the F1/F2 collision

### The CIO's reading of F2 — checked, and correct, with one correction

F2 reads: *"No existing test may be deleted or weakened… Any existing test requiring modification
needs a written justification to Validation before the change lands."* The CIO reads this as: F2 is
not an absolute bar, and the resolution may be that I approve a replacement.

**That reading is correct.** The clause's own second sentence supplies the exception, and the
purpose named in its third sentence — *"'make the suite pass' is otherwise satisfiable by editing
assertions"* — is a purpose about **assertions**, not about **files**.

One correction, because it changes what "approval" means: **the written justification is a
mechanism, not a waiver.** F2 does not authorise me to bless any edit I find convenient. It requires
that the *properties* the original test protected survive the rewrite, and it puts the burden of
demonstrating that on the person approving. So the operative question is not "may this test be
replaced" — it may — but "what did it protect, and does the replacement still protect it."

### What the original test protected

`test_holdout_locks_splits_and_opens_once` asserted six things:

| | Property | Survives into P-1 as |
|---|---|---|
| 1 | `lock(fraction=0.25)` splits 1000 → 750 in-sample | Retired with the API. Under P-1 the vault does not split; the **ceiling** is the split. |
| 2 | Wrong passphrase (`"wrong"` — non-empty) is refused | **Only C9 preserves it, and only at re-read.** C4 does not: it tests `""`. → this is why C-2 is blocking |
| 3 | **`held.index[0] > insample.index[-1]`** — the holdout is strictly after the in-sample, with no overlap | **NOTHING preserves it.** See below. |
| 4 | Holdout length is 250 | Subsumed by the C5-adjacent window-length check. |
| 5 | Second open → permanent retirement | C2. |
| 6 | Both event kinds reach the registry | C1, C2. |

**Property 3 is the load-bearing one, and it has been lost.** It is the "no overlap between the two
samples" property — the thing a holdout *is*. Under the old regime the vault enforced it in code, so
the test could assert it directly. Under P-1 it decomposes into two halves:

- the **ingest** half — no row after `C` enters `pit.db` — which is B2/B3/B6, and is covered; and
- the **acquisition** half — the fetched frame contains nothing at or before `C` — which is
  **enforced nowhere and asserted nowhere**.

Measured, against the shipped code: a `fetch` returning 2,000 days starting 2010-01-01 against a
vault sealed at `C = 2020-01-01` was **accepted, sealed as the holdout, and the vault retired**;
`evaluate_gate1` then reported the holdout criterion **PASS**. The tests' `good_fetch` starts at
`C + 1 day` by construction, so the suite never probes it.

**Seat 9's claim that C1, C2 and C4 "together cover every property the original test covered" is
therefore incorrect** — not through carelessness, but because property 3 changed shape and the
half that moved into the acquisition path went missing in transit. This is exactly the erosion F2
exists to catch, and it is the reason F2 does not let a rewrite be waved through on the writer's own
assessment.

### Ruling

> **R-F1/F2-1.** The Principal's family-at-construction instruction and F1 are both upheld. There is
> no design that satisfies them and leaves `lock()`/`open_once()` functional; Seat 9's analysis is
> correct and its refusal to edit unilaterally was the right call.
>
> **R-F1/F2-2.** `test_holdout_locks_splits_and_opens_once` is **replaced in place** in
> `test_harness.py` — not deleted, not skipped, not moved. Rename it
> `test_holdout_ceilings_and_acquires_once_p1`. **This paragraph is the written justification F2
> requires.**
>
> **R-F1/F2-3.** Seat 9's proposed replacement is **approved only as amended**. It must assert, in
> one test, all five of:
> 1. the ceiling accepts a batch ending exactly at `C` and refuses one crossing `C`, with the row
>    count unchanged on refusal — *successor of property 1*;
> 2. **`acquired.index.min() > C`** — *successor of property 3*, the one that went missing;
> 3. a **wrong, non-empty** passphrase is refused with `fetch.calls == 0` and the vault is **not**
>    retired, and the correct passphrase then acquires successfully — *successor of property 2*
>    (depends on C-2);
> 4. a second `acquire_once` raises `HoldoutRetiredError`;
> 5. `holdout_acquisition_attempted` and `holdout_second_acquisition_attempt` both reach the
>    registry, family-scoped.
>
> **R-F1/F2-4.** Property 3 must also be enforced in **code**, not only asserted in the replacement
> — condition **C-7**. A test asserting a property the code does not enforce protects the fixture,
> not the firm.

Holding the legacy test as-is and changing the implementation instead was considered and is
rejected: it requires either a functioning `lock()` (violates F1) or an optional `family` (violates
the Principal's direct instruction), and both are more senior than F2's default.

---

## 5. RULING on the pre-registration freeze (D-006 rider)

### Does the rider require a harness change? **Yes.**

The CIO's finding is correct and I am confirming it as my own, with the reason stated in the terms
I used in Ruling 001 §2.1:

> **The pre-registration is currently a tamper-evident *promise*, not a tamper-evident *payload*.**

Under Option D the pre-registration became the object the entire holdout hangs off. The forward
window's value is not "data nobody fetched" — it is "data tested against a claim fixed before the
data existed." **If the claim can move, the window is out-of-sample against nothing.** The rider is
what makes Option D worth twelve months of waiting, and the rider is currently enforced by an API
docstring.

Three specifics [measured]:

1. **No hash.** `open_hypothesis` writes a row and a `hypothesis_registered` event carrying
   `statement` and `predecessor_family` only. `mechanism`, `falsifier`, `universe`, `horizon`,
   `success_criteria`, `trial_budget` exist **nowhere but the mutable `hypotheses` row**. An
   `UPDATE hypotheses SET falsifier=…` leaves no trace anywhere. The `falsifier` is the field
   Gate 0 §4.3(2) and R3 both hang on.
2. **Immutability is invisible, not enforced.** Re-calling `open_hypothesis` on an existing family
   `return`s silently — no error, no event, no diff. A seat that believes it has amended the
   pre-registration is told nothing. That is worse than refusing: it is a silent divergence between
   what the researcher thinks the claim is and what the registry says it is.
3. **No binding to the report.** `ValidationReport` carries `returns_sha256`, `holdout_spec_sha256`
   and `holdout_payload_sha256`. Nothing ties a verdict to the pre-registration text it judged.

**The asymmetry with the holdout spec is not defensible.** A1/A4/E3 give the holdout spec a sealed
hash, on-disk tamper detection, and report embedding — for an object whose integrity matters at one
moment, Gate 1. The pre-registration's integrity now matters continuously, for twelve months, and
has none of the three. The construction is already written and tested in `holdout.seal()`; this is
copying twenty lines, not designing a control.

**And a consequence neither the CIO nor Seat 9 raised:** R1–R4 were made binding by D-006, and
**the registry has no columns for any of them** — no holdout classification, no forward-window
falsifier, no numeric kill condition, no model-prior provenance, no haircut determination. Under
Option D the forward-lag family is next in the queue. It cannot be pre-registered with its binding
fields today, freeze or no freeze. This is why the P-series gates my Gate 0 unit rather than ingest.

### Acceptance criteria — P1 through P8

**P1 — Seal.** `open_hypothesis` computes `prereg_sha256` = sha256 over canonical
(`sort_keys=True`, UTF-8) JSON of the binding field set, and logs a `hypothesis_sealed` event
carrying **the hash and the complete field set** — a full shadow copy in the append-only `events`
table, not a pointer. A pointer to a mutable row is not evidence.

**P2 — The binding set, named exhaustively.** `family`, `statement`, `mechanism`, `falsifier`,
`universe`, `horizon`, `success_criteria`, `trial_budget`, `predecessor_family`,
`holdout_classification` ∈ {FORWARD, HISTORICAL}, `forward_window_start`,
`forward_window_min_length`, `forward_kill_condition`, `model_prior_provenance`,
`published_signal_haircut_applied`. The last six are R1/R3/R4 and require new columns.
Everything else is provenance-only and outside the hash.

**P3 — *(negative)*** Re-calling `open_hypothesis` for an existing family with **any differing
binding field** raises `PreRegistrationAmendedError` and logs `hypothesis_amendment_refused` with
the differing field names. Byte-identical re-registration stays idempotent and logs nothing.
*Test both branches.* This kills the silent no-op.

**P4 — *(negative, the point of the whole thing)*** A test performs a **raw SQLite
`UPDATE hypotheses SET falsifier='…'`**, then asserts (a) `registry.verify_prereg(family)` reports a
mismatch naming the field, and (b) `evaluate_gate1` returns **FAIL** on a new criterion
`Pre-registration integrity`. This is the A4 analogue and it is the criterion that converts the
promise into a payload.

**P5 — Report binding.** `ValidationReport` gains `prereg_sha256` and the
`Pre-registration integrity` criterion, computed by recomputing the hash from the live row and
comparing to the sealed event. Rendered in `to_markdown()` alongside the two holdout hashes (E3
analogue).

**P6 — *(negative)*** A family with no `hypothesis_sealed` event → the integrity criterion is
**INSUFFICIENT-DATA, never PASS** (E2 analogue). This is not hypothetical: `book/registry.db`
predates the change and any family registered under the old schema lands here.

**P7 — *(negative — this is the rider itself, mechanised)*** `evaluate_gate1` returns **FAIL** on
`Pre-registration integrity` if the family's `hypothesis_sealed` event postdates the holdout
cutoff `C` recorded in its `holdout_spec_sealed` event. Compared at **UTC day granularity**, since
`C` is a calendar date and the holdout opens at `C + 1 bar`. *Test: seal a prereg after a vault's
cutoff → FAIL.*
**Operational consequence, stated so it is not discovered at Gate 1:** the pre-registration must be
sealed on or before the calendar day of `C`. Without P7 the rider is a sentence in a decision
record; with it, it is a criterion.

**P8 — Chains.** A successor family's report lists the `prereg_sha256` of every family in its
`predecessor_chain`. The predecessor's claim is part of what its N is a denominator for.

### What this does not do — stated so nobody over-reads it

The freeze is **tamper-evident, not tamper-proof**. A direct SQLite write becomes *detected*, not
*prevented* — the same limit as §2.4, for the same reason, and no document may describe it
otherwise. It also does nothing about I-011: model priors contaminate hypothesis *formation*,
upstream of any freeze, and D-006 already says so. P1–P8 close the channel D-006's rider aimed at.
They close no other.

---

## 6. RULING on I-010 — `backtest_years`

> **Required. And required alone is not sufficient — the CIO's own finding proves it.**

The reflex answer is "make it required." That answer is wrong on its own, and the evidence is in
I-010's own text: **the sole existing caller,** `demo_workflow.py:132`, **already passes
`len(prices)/252`** — the exact quantity the fallback computes. A required parameter that the only
caller in the repo already satisfies with the offending value fixes nothing. It converts a silent
default into a silent argument.

The defect is not that the parameter has a default. It is that **nothing checks the number means
calendar span**, on a criterion that is mine, whose failure direction is permissive, and which the
Charter fixes at four years. The seat's own standard applies: a length the harness cannot verify is
INSUFFICIENT-DATA, not a length it may assume.

### G1–G5

**G1** — `backtest_years: float` becomes **required**, no default. The
`r.size / periods_per_year` fallback at `gates.py:200` is **deleted**, not defaulted.

**G2** — `evaluate_gate1` gains `oos_index: pd.DatetimeIndex | None`. Where supplied,
`years_calendar = (max − min).days / 365.25` is computed and **used**; the caller's
`backtest_years` is reported alongside it.

**G3 — *(negative)*** If both are supplied and disagree by more than 5% of the calendar figure, the
length criterion is **FAIL**, with a note carrying both numbers. That disagreement is the pooled-
panel signature, and on a §4.4 criterion a materially mis-stated length is a failure, not a note.

**G4 — *(negative)*** If `oos_index` is `None`, the criterion is **INSUFFICIENT-DATA**, never PASS,
whatever `backtest_years` says. A number the harness cannot verify does not clear a Charter floor.

**G5 — *(negative, the I-010 case exactly)*** A stacked contract-day panel: 1,500 rows at
`periods_per_year=252` (≈ 5.95 "years" by observation count) over an 18-month `oos_index`.
Criterion must be **FAIL**. Under today's code this reads PASS on the 4-year floor.
Plus: correct `demo_workflow.py` to pass the calendar span.

**On the cost.** G1 breaks every existing `evaluate_gate1` call site (~10). **I authorise those
edits under F2 now**, so this does not need a second escalation: adding a required argument to a
call is not weakening a test, and **no assertion may change**. If any existing assertion has to move
to accommodate G1–G5, stop and escalate — that would mean an existing test was passing on the
permissive fallback, which is itself a finding.

I concur with the CIO's override of Seat 9's classification. An untested permissive fallback on a
Charter §4.4 criterion is a harness-correctness defect, not an implementation obligation for a
measurement that has not been scheduled. I-010's severity of MEDIUM is correct — it is latent, zero
families exist — and it must not be carried past the first Gate 1.

---

## 7. What is unblocked, what remains blocked, on whom

**Unblocked now**

| Work | Owner |
|---|---|
| C-1 … C-7, then C-8 … C-10 | head-of-data-infra |
| P1–P8 and the R1 fields | head-of-data-infra |
| G1–G5 | head-of-data-infra |
| Drafting `DATA-SPEC-polymarket-usable-history.md` | head-of-data-infra — never blocked, needs no data, still outstanding |
| Committing the P-1 deliverable under a message naming I-005 (I-013) | fable-5-cio |

**Still blocked**

| Blocked | On | Owner of the blocker |
|---|---|---|
| **All ingest (I-001)** | C-1 … C-7 landed + suite 100% green. **Then it unblocks without me.** | head-of-data-infra |
| Measurement of usable Polymarket history | My acceptance of the DATA-SPEC draft, which does not exist yet | head-of-data-infra, then me |
| **Gate 0 intake of the forward-lag family** | P1–P8 + R1 fields (nowhere to store the binding fields), and interpretive decision 7 (`instrument_identity` unconfirmed for Polymarket) | head-of-data-infra; then my fourth unit |
| Any Gate 1 evaluation | G1–G5, plus the R1 classification field | head-of-data-infra |

**Issue Log inputs** — the CRO owns the log; these are mine to it:

- **I-005** — resolved in specification and in implementation; **closes on C-1…C-7 landing**, not on
  this document.
- **I-007** — E1 is properly tested in both directions. **Closes with C-1.**
- **I-008** — README corrected to 64. **Closes with C-1.**
- **I-010** — remains open, ruled here; closes on G1–G5.
- **New, HIGH, owner head-of-data-infra:** wrong-non-empty passphrase bricks a family
  (C4 defeated). Pattern tag `control-defeats-its-own-purpose`.
- **New, HIGH, owner head-of-data-infra:** `evaluate_gate1(holdout_opened_once=True)` returns PASS
  on zero registry events. Pattern tag `narrated-number-backdoor`.
- **New, MEDIUM, owner head-of-data-infra:** `PITStore` compares `event_time` as strings with
  caller-supplied UTC offsets; measured false negative in the D1 leak detector, and `asof` affected.
  Pattern tag `harness-correctness-latent`.
- **New, MEDIUM, owner head-of-data-infra:** `ingest_documents()` bypasses the D2 ceiling.
- **New, LOW, owner head-of-data-infra:** `test_C8_payload_encrypted_at_rest` asserts a property it
  cannot falsify. Pattern tag `test-cannot-fail`.
- **New, MEDIUM, owner fable-5-cio:** every `ValidationReport` the harness can currently produce is
  defective under Ruling 001 §2.4 / Ruling 002 R1 — no FORWARD/HISTORICAL field.

---

## 8. What would change my mind

Falsifiers, per house rule 2. Each is an observable, not a mood.

**On the verdict.**
- If Seat 9 shows that a seal-time passphrase verifier cannot be built without storing something
  the Principal would recognise as the passphrase, **C-2 changes shape but does not go away**: the
  fallback is that `acquire_once` requires the passphrase twice and `read_acquired` is invoked
  immediately after sealing, inside `acquire_once`, with failure rolling the vault back to `SEALED`
  and deleting `payload.enc`. That is uglier and I would rather have the verifier. I will not accept
  "the risk is small" — the risk is one keystroke against an object the Charter calls sacred.
- If C-3 (mandatory `PITStore`) turns out to break a legitimate use — a vault for a dataset that
  genuinely never transits `pit.db` — I will convert it to an explicit
  `HoldoutVault(..., store=None, no_ceiling_justification="…")` that logs a
  `holdout_ceiling_waived` event and makes `evaluate_gate1` report the holdout criterion
  **INSUFFICIENT-DATA**. What I will not accept is a silent `None` default.
- **I would not change my mind on any argument that the seats will be careful.** C4's bricking, the
  `holdout_opened_once` bypass and the un-ceilinged document path are all "nobody would do that"
  defects. Ruling 001 §2.2 settles this: the safe path must be the default path, and trustworthiness
  is not a control.

**On F1/F2.**
- If Seat 9 demonstrates that property 3's acquisition half is already enforced somewhere I did not
  find, C-7 drops and R-F1/F2-3(2) becomes an assertion of existing behaviour rather than new. I
  looked and I measured the opposite, so I doubt it — but I have read this code once, not lived in
  it.
- If the Principal instructs that `family` be optional after all, F1 and F2 stop colliding and the
  legacy test could survive with a two-line edit. I would still refuse, because F1 alone kills it.

**On the pre-registration freeze.**
- If the Principal amends D-006 to make the freeze advisory rather than binding, P1–P8 become
  optional and I would say so in every Validation Report for a family under Option D: *"the
  pre-registration was not sealed; the forward window is out-of-sample against a claim that could
  have moved."* That sentence is the honest alternative to the harness change, and I would rather
  build the control than write it.
- **P7 is the clause I am least certain of.** Day-granularity is a judgment call, and if sealing and
  `C` genuinely cannot be ordered within a day for operational reasons, I will move it to
  "sealed no later than `C`'s calendar day" — which is what it already says — but I will not drop
  the criterion. A rider nobody can fail is not a rider.

**On I-010.**
- If Seat 9 establishes that a reliable `oos_index` is unavailable at the `evaluate_gate1` boundary
  for a pooled panel, G2/G3 become unimplementable and **G4 governs**: the length criterion is
  INSUFFICIENT-DATA for every pooled family, permanently, until the boundary is fixed. That is a
  worse outcome for the sponsor and a better one for the firm, and I would take it without
  hesitation.
- The 5% tolerance in G3 is **my judgment call, marked as such** [inferred — no external standard
  prescribes it]. I will move it on a reasoned argument **before** the first Gate 1 evaluation. I
  will not move it after, for any reason including the evaluation's outcome.

---

*Head of Quantitative Validation · Castellan Capital · 2026-07-28*
*Third of four approved Opus units. Gate 0 intake is the fourth and is deliberately not begun here.*
