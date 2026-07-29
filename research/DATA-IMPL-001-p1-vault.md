# DATA-IMPL-001 — Implementation of the P-1 Holdout Regime

**Seat:** Head of Data & Infrastructure
**Date:** 2026-07-28
**Implements:** `research/VALIDATION-RULING-001-holdout-regime.md` §2.3 (design D1-D4) and §5
(acceptance criteria A1-F4). Also closes I-007 and I-008.
**Status:** implementation complete, tests green except one named, escalated exception (below).
**Not done, on purpose, per scope limits:** no data fetched, no backtest run, no git commit, no
self-granted acceptance. This note is Data & Infra's delivery; acceptance is Validation's to grant
in writing per Ruling 001 §5 and the Principal's binding rider.

---

## 1. What was built

| File | Change |
|---|---|
| `harness/castellan/errors.py` | **New.** All holdout-related exception types, shared between `holdout.py` and `data.py` to avoid a circular import (`data.py` needs `HoldoutCeilingError` for the D2 ceiling; `holdout.py` needs the rest). |
| `harness/castellan/holdout.py` | **Rewritten.** `HoldoutVault` now implements the two-artifact, four-state P-1 design: `seal()` (D1/A1-A4), `acquire_once()` (D3/C1-C10, plus the D1 leak check and D2 ceiling lift), `authorize_retry()`, `read_acquired()` (C9), and a `state` property (`VaultState`). `lock()`/`open_once()` are retired stubs that hard-raise `HoldoutRegimeError` (F1). Constructor now takes `family` (Principal's direct instruction) and an optional `store: PITStore` — a vault built without a store still works but forgoes the D2 ceiling and D1 leak detection, which is a real degradation and is documented as such rather than silently accepted. |
| `harness/castellan/data.py` | **Extended.** New `ingest_ceiling` table; `PITStore.set_holdout_ceiling()` (public, create-only), `PITStore._lift_ceiling()` (private, spec-hash-gated), `PITStore._active_ceilings()`, `PITStore.rows_in_window()` (D1 leak query). `ingest()` now calls `_enforce_holdout_ceiling()` before writing anything (D2/B3 atomicity). |
| `harness/castellan/registry.py` | **Extended.** `open_hypothesis(..., predecessor_family=None)`; `predecessor_chain()`; `family_stats()` and `returns_matrix()` now sum/pool transitively across the chain (F4, §3.3). A `_migrate()` step `ALTER TABLE`s in `predecessor_family` for the pre-existing `book/registry.db` file, which was created under the old schema. |
| `harness/castellan/gates.py` | **Extended.** Holdout criterion rewritten to be family-scoped (`registry.events(kind=..., family=family)`) — this is the I-007 fix. New logic for the short-window FAIL case (C5's adjacent clause), the leak-detection FAIL case (D1), and surfacing bad-passphrase and retry counts in the note (C4/C7). `ValidationReport` gained `holdout_spec_sha256` / `holdout_payload_sha256` fields (E3), populated family-scoped and rendered in `to_markdown()`. |
| `harness/castellan/__init__.py` | Exports the new error types; `HoldoutVault` import updated (no longer re-exports `HoldoutRetiredError` from `holdout.py` specifically — it now comes from `errors.py`, same public name, no break). |
| `harness/tests/test_holdout_p1.py` | **New.** 34 tests, one function (or parametrized group) per acceptance item — mapping in §2 below. |
| `harness/README.md` | F3: line-15 holdout paragraph rewritten to describe the P-1 regime; stale "(16 tests)" corrected to the actual total; workflow code sample updated to `seal()`/`acquire_once()`. |
| `harness/examples/demo_workflow.py` | Updated to the new API for consistency (not executed this session — see §4). |

---

## 2. Acceptance-criterion -> test mapping

| Item | Test(s) in `test_holdout_p1.py` |
|---|---|
| A1 | `test_A1_seal_writes_spec_and_sealed_event` |
| A2 | `test_A2_reseal_raises` |
| A3 | `test_A3_future_cutoff_permitted`, `test_A3_malformed_spec_raises[dataset_id\|instrument_identity\|schema_fingerprint\|query_semantics]` |
| A4 | `test_A4_registry_hash_matches_disk` (byte-level tamper detection is exercised again, in the acquisition path, by C3) |
| B1 | `test_B1_ceiling_row_written_at_seal_time` |
| B2 | `test_B2_ingest_accepts_at_or_before_cutoff` |
| B3 | `test_B3_ingest_refuses_batch_atomically_and_logs` (asserts row count unchanged, not just the raise) |
| B4 | `test_B4_non_ceilinged_dataset_unaffected` |
| B5 | `test_B5_direct_ceiling_mutation_raises` |
| B6 | `test_B6_boundary_inclusive_at_cutoff[None]` (tz-naive), `[UTC]` (tz-aware); both cross a same-day boundary at `event_time == C` |
| C1 | `test_C1_success_order_and_state` (asserts attempt-before-acquired event ordering and terminal state) |
| C2 | `test_C2_second_acquisition_retires` |
| C3 | `test_C3_spec_tampered_no_network_call` (asserts the injected fetch's call counter is 0) |
| C4 | `test_C4_bad_passphrase_no_network_call_not_retired` |
| C5 | `test_C5_fetch_before_cutoff_raises`, `test_C5_short_window_flagged_fail_not_insufficient` |
| C6 | `test_C6_failure_then_blocked_retry` |
| C7 | `test_C7_authorized_retry_succeeds_and_counted` |
| C8 | `test_C8_payload_encrypted_at_rest` |
| C9 | `test_C9_read_acquired_wrong_passphrase_raises` |
| C10 | `test_C10_schema_mismatch_treated_as_failure` |
| D1 | `test_D1_pre_acquisition_leak_fails_gate` |
| D2 | `test_D2_clean_case_no_leak` |
| E1 | `test_E1_second_acquisition_violation_does_not_fail_other_family`, `test_E1_acquisition_on_one_family_does_not_satisfy_another` — this is the two-family test case named in the Principal's instruction |
| E2 | `test_E2_no_acquisition_is_insufficient_never_pass` |
| E3 | `test_E3_report_embeds_holdout_hashes` |
| F1 | `test_F1_legacy_lock_and_open_once_hard_raise` |
| F2 | Process clause, not a unit test. Honoured by construction: zero lines were changed in `test_harness.py` or `test_data_book.py`. One pre-existing test cannot be reconciled with F1 — see §3, the escalation, rather than an edit. |
| F3 | Manual doc changes (README), no automated test. |
| F4 | `test_F4_predecessor_family_n_starts_at_predecessor_total` (also checks the `predecessor_family`-not-registered `ValueError`, and that the predecessor's own count is unaffected) |

Ruling 001 counted this as 29 cases across six groups; the above is 34 test functions (some
parametrized to 2-4 cases each) because I chose not to merge assertions that test independent
properties, per the "a merge that drops an assertion is a reduction in coverage" instruction.

---

## 3. Escalation: F1 vs. F2 collide on one pre-existing test, and I did not resolve it myself

`harness/tests/test_harness.py::test_holdout_locks_splits_and_opens_once` (lines 171-188) is
written against the *old* API: it constructs `HoldoutVault(vault_dir, registry, name)` with three
positional arguments and calls `.lock(df, passphrase=..., fraction=...)` and `.open_once(...)`
expecting them to succeed.

Two binding requirements collide on this exact test, and I do not believe there is a design that
satisfies both:

- **The Principal's direct instruction** (task constraint #2): `HoldoutVault.__init__` takes
  `family` as a new, required constructor argument. Making it optional-with-a-default would let a
  vault silently omit the family binding the Principal specifically asked for ("the vault takes the
  family, logs it on every event") — so I made it required, not defaulted. This alone breaks the
  old test's `HoldoutVault(vault_dir, registry, name)` call with a `TypeError`, independent of
  anything else.
- **Ruling 001 F1**: `lock()` / `open_once()` must be "removed, or hard-raise `HoldoutRegimeError`
  ... not deprecated-with-warning: a code path that violates a Principal amendment must not remain
  silently callable." There is no version of this that leaves `lock()`/`open_once()` functionally
  working (which is what the old test asserts), because a functioning fetch-then-lock path *is* the
  regime P-1 prohibits.

Ruling 001 F2 requires: "no existing test may be deleted or weakened... Any existing test requiring
modification needs a written justification to Validation before the change lands." My task
instructions from the CIO are explicit on the same point: "if an existing test genuinely must
change, write the justification and escalate; do not edit it unilaterally."

**I judge this a genuine conflict, not a false one** — I checked for a design that avoids it (e.g.
an optional `family` parameter, or a `lock()` that still runs but is clearly marked deprecated) and
concluded both fail the more senior, more recently stated requirement (the Principal's direct
signature instruction and F1's "not deprecated-with-warning" clause, respectively).

**What I did:** left the test file completely untouched. It now fails —
`TypeError: HoldoutVault.__init__() missing 1 required positional argument: 'family'` — as an
honest, visible consequence of the new regime, not a silently edited or skipped test.

**Proposed resolution, for Validation's sign-off, not landed by me:** rewrite the test to exercise
the new API while preserving every property the old test checked — passphrase rejection, correct
temporal ordering (holdout strictly after in-sample), second-attempt permanent refusal, and both
event kinds landing in the registry. Concretely, that would replace `vault.lock(...)` /
`vault.open_once(...)` with `vault.seal(...)` / `vault.acquire_once(...)`, using a `store` fixture
and an injected `fetch` callable in place of the pre-supplied `df`. `test_holdout_p1.py`'s
`test_C1_success_order_and_state`, `test_C4_bad_passphrase_no_network_call_not_retired`, and
`test_C2_second_acquisition_retires` already demonstrate this replacement and, together, cover every
property the original test covered — I did not write the replacement into the old file myself
because that is the exact "edit it unilaterally" the instruction told me not to do.

**Suite count, honestly:** 64 tests total (30 original + 34 new), **63 passing, 1 failing** — the
one named above. This is short of "full harness suite passing," which is the rider's condition for
beginning ingest. Ingest was going to stay blocked regardless (scope limits), but I want this stated
plainly rather than rounded up: **the suite is not green**, and it will not be until Validation
either approves the proposed test rewrite or specifies a different resolution.

---

## 4. Interpretive decisions made under "how to implement" (Seat 9's call, flagged for visibility)

Ruling 001 specifies design and acceptance criteria; several implementation details were left open.
None of these change what the ruling requires; all are flagged here so Validation can correct any
that were read wrong.

1. **`dataset_id` maps to the existing `symbol` column in `PITStore.observations`.** Ruling 001 D2
   keys the ceiling on `(source, dataset_id)`; the store's existing schema has no separate
   `dataset_id` field. Rather than widen `observations` (a schema change with its own migration
   burden, for a field that would just duplicate `symbol` in every realistic use), the ceiling keys
   on `(source, symbol)`, and the vault's `dataset_id` argument is passed straight through as
   `symbol`. If a future dataset needs `dataset_id != symbol` (e.g. one symbol split across two
   logically distinct feeds), this mapping breaks and would need revisiting.

2. **Passphrase "correctness" is a presence check at `acquire_once()`, not a cryptographic one; it
   is a real cryptographic check only at `read_acquired()`.** At first acquisition there is no
   ciphertext yet to test a passphrase against — Ruling 001 D3 says exactly this ("a passphrase
   cannot prevent an HTTP GET... its job is authorization-and-sealing, not prevention"). C4 requires
   "wrong passphrase -> refuse before any fetch," which I read as: an empty/falsy passphrase is
   refused before any network call (`HoldoutPassphraseError`, logged, not retiring). C9 ("re-reading
   ... requires the passphrase; a wrong passphrase raises") is where genuine cryptographic
   verification happens, via Fernet's `InvalidToken`, exactly like the old `open_once()`. If
   Validation intended a stronger pre-acquisition passphrase check (e.g. a verifier committed at
   seal time), that is a design addition I did not make, because nothing in D1-D4 describes storing
   one and Amendment P-1's own text says the passphrase is "never stored."

3. **The four states collapse `ACQUIRED` into `RETIRED`.** D1 describes `SEALED -> (ACQUISITION_FAILED <-> retry) -> ACQUIRED -> RETIRED`, but nothing in C1-C10 describes an
   ACQUIRED-but-not-yet-RETIRED window (C1 itself says success moves the state straight to RETIRED).
   `VaultState` therefore has `UNSEALED / SEALED / ACQUISITION_FAILED / RETIRED` — a successful
   acquisition is atomically both.

4. **Ceiling lift is gated by spec-hash equality, not a token.** B5 requires a ceiling be liftable
   "only through the passphrase-authorized acquisition path... a direct mutation attempt raises." I
   implemented `PITStore._lift_ceiling(source, dataset_id, family, spec_sha256)` to require the
   correct sealed spec hash — the same value D4's tamper check verifies — rather than inventing a
   separate capability token. `acquire_once()` already re-derives and checks this hash before it
   would ever call `_lift_ceiling`, so a caller without legitimate access to the vault's verified
   spec hash cannot lift a ceiling. `test_B5_direct_ceiling_mutation_raises` calls `_lift_ceiling`
   directly with a bogus hash and confirms the ceiling survives.

5. **`returns_matrix()` pools transitively across `predecessor_family`, not just `family_stats()`.**
   F4's text only names `family_stats`. I extended `returns_matrix` the same way because DSR's N
   (from `family_stats`) and PBO's return matrix (from `returns_matrix`) would otherwise be computed
   over different trial sets for a successor family — which is exactly the kind of silent
   inconsistency Ruling 001 Ruling-2 §3.2(1) objects to in a different context. This is a superset of
   what F4 asked for, not a substitute; flagging it as a discretionary extension rather than folding
   it in silently.

6. **Retry-gate ordering:** an unauthorized retry attempt (state `ACQUISITION_FAILED`, no matching
   `holdout_retry_authorized` event) raises `HoldoutRetryUnauthorizedError` *before*
   `holdout_acquisition_attempted` is logged again, on the reasoning that "attempted" should mean
   "about to make the network call," and this gate fires strictly before that. A separate
   `holdout_retry_unauthorized_attempt` event is logged instead, for the same audit-trail reason
   every other refusal path logs something. Ruling 001's prose doesn't pin this ordering explicitly;
   this is the reading I judged most consistent with D3's stated principle.

7. **`instrument_identity` for Polymarket specifically is unconfirmed** (Ruling 001 §3.4 flags this
   itself as `[assumed]`, pending Seat 9 confirming a stable on-chain identifier is exposed by the
   public API). That confirmation requires touching Polymarket's API, which is out of this task's
   scope (no ingest, no network calls). The `seal()` API accepts and requires a non-empty
   `instrument_identity` string generically — enforcement of *which* identifier is valid for a given
   venue is not implemented, and shouldn't be until `DATA-SPEC-polymarket-usable-history.md` (the
   separate, still-outstanding deliverable) settles it.

---

## 5. Suite count

```
python3 -m pytest harness/tests -q
```

**Before this change:** 30/30 passing.
**After this change:** 64 collected, **63 passing, 1 failing** (the named, escalated exception in §3).

This is short of the rider's "full harness suite passing" bar. I am reporting that shortfall
directly rather than resolving it by editing the one test myself, per the CIO's explicit
instruction and Ruling 001 F2.

---

## 6. A git-history note the CIO should see before committing

Partway through this session, `git log` showed `harness/castellan/{errors,holdout,data,registry,
gates,__init__}.py` already present at HEAD, inside commit `ce4186672` ("Validation Ruling 002:
reject training-cutoff C, adopt threat model"), whose message does not mention the P-1 vault at all.
`git diff HEAD` for those six files is empty against my finished working tree — i.e. HEAD already
holds byte-identical copies of exactly what this note describes.

I read Ruling 002 (`research/VALIDATION-RULING-002-c-placement.md`) to check for a substantive
conflict before concluding anything. It rules on a different question entirely — where `C` is
sourced from (rejecting "pin at a seat's training cutoff," adopting a threat model instead) — and
says explicitly it does not reopen Ruling 001's other rulings, including §2.3 (the vault design this
note implements). **There is no design conflict.** `cutoff` is an opaque parameter to `seal()` in
this implementation; nothing here assumes or depends on where `C` is sourced from.

The likeliest explanation is concurrency, not a duplicate independent implementation: the CIO commits
on its own cadence from the same working tree I was editing, and a commit landed after these six
files were already written to disk but before I had written the test suite, this note, or the
README/example fixes. **I did not run `git commit` myself** (out of scope per my instructions), so
this is not a violation on my part — but the CIO should know that the source implementation is
already in history under an unrelated commit message, and that `harness/tests/test_holdout_p1.py`,
this note, `harness/README.md`, and `harness/examples/demo_workflow.py` are the remaining
uncommitted pieces of the same deliverable. I'd suggest the next commit message name I-005/this
implementation explicitly, rather than let the association rest on file-content matching alone.

---

## 7. Readiness for Validation's acceptance review

- **Fully covered, by test:** A (spec sealing), B (ingest ceiling), C (acquisition, all ten items
  including the four rider-named negatives), D (leak detection), E (Gate integration, including the
  I-007 two-family case by name), F1 (legacy retirement) and F4 (predecessor chaining).
- **Not fully closed:** F2's literal "full suite passing" — see the escalation in §3. This is a
  process decision for Validation (approve the proposed rewrite, or specify something else), not a
  missing implementation.
- **Not attempted, in scope terms:** no data was fetched, no backtest run, no commit made, and I am
  not granting acceptance myself — that is Validation's per Ruling 001 §6 and the Principal's rider.
  `research/DATA-SPEC-polymarket-usable-history.md` (Ruling 3, §4.2-4.4) is a separate, still-open
  deliverable and was not part of this task's instructions; it is not included here.
- **My assessment:** the implementation is ready for Validation's review conditional on the F1/F2
  escalation being resolved first — either by approving the proposed test rewrite (in which case the
  suite goes to 64/64 immediately) or by directing a different resolution. I would not describe the
  current state as "ready to accept" on its own, because the rider's own bar (full suite green) is
  not met, by one test, for a reason I consider structural rather than an oversight.
