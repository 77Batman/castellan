# DATA-IMPL-002 — Acceptance 001 remediation (I-014, I-015, I-016, I-017, I-018)

**Seat:** Head of Data & Infrastructure
**Date:** 2026-07-28
**Implements:** `research/VALIDATION-ACCEPTANCE-001-p1-vault.md` conditions C-1…C-10 (blocking + sprint-close),
the P-series (§5), the G-series (§6, I-010), and the R1–R4 registry schema (I-018).
**Status:** all conditions implemented and tested. Suite: **96 collected, 96 passed, 0 failed, 0 skipped,
0 xfail.** Not done by me: granting acceptance (Validation's), committing to git (CIO's), any data fetch
or backtest (out of scope by task instruction).

---

## 1. Suite state

```
python3 -m pytest harness/tests -q
```

**Before this change:** 64 collected, 63 passed, 1 failed (the named F1/F2 escalation).
**After this change:** **96 collected, 96 passed, 0 failed, 0 skipped, 0 xfail.**

Breakdown: `test_data_book.py` 14, `test_harness.py` 16 (incl. the F1/F2 replacement), `test_holdout_p1.py`
66 (34 original + 32 new: 12 Group ACC for C-2/C-3/C-4/C-5/C-7/C-9, 2 for C-10, 5 Group G, 8 Group P,
3 R1/R3, 1 C-2 authorize_retry re-audit fix — see §7).

This clears both suite-related blocking requirements: **0 failed / 0 skipped / 0 xfail**, and every
negative case named in Acceptance 001 §3/§4 exists and passes.

---

## 2. C-1 — the F1/F2 replacement test

`harness/tests/test_harness.py::test_holdout_locks_splits_and_opens_once` is **replaced in place**,
renamed `test_holdout_ceilings_and_acquires_once_p1`, per Ruling R-F1/F2-2/3/4. It asserts, in one test,
all five items Validation specified:

1. the ceiling accepts a batch ending exactly at `C` (181 rows, asserted) and refuses one crossing it,
   with the row count on `observations` unchanged on refusal (`before == after`).
2. **`acquired.index.min() > C`** — the successor of the legacy test's `held.index[0] > insample.index[-1]`,
   the property Acceptance 001 found missing.
3. a wrong, non-empty passphrase (`"wrong-guess"`) is refused with `calls == 0` and `not vault.is_retired()`,
   and the correct passphrase then acquires successfully.
4. a second `acquire_once` raises `HoldoutRetiredError`.
5. `holdout_acquisition_attempted` and `holdout_second_acquisition_attempt` both reach the registry,
   family-scoped (`registry.events(family="demo")`).

Zero lines were changed in `test_data_book.py`; the only file touched for F1/F2 is `test_harness.py`, and
the replaced test is the only one removed from it. This paragraph plus the ruling is the written
justification F2 requires (already supplied by Validation in R-F1/F2-2; recorded here as the landing
point).

---

## 3. C-2 — seal-time passphrase verifier (closes I-015)

**What was wrong:** `acquire_once` checked passphrase *presence* (`if not passphrase or not
passphrase.strip()`), not correctness. A typo (`"hunter3-TYPO"`) passed the presence check, fetched,
sealed the payload under the typo, and retired the vault — permanently, since `read_acquired` with the
real passphrase then raised and re-acquisition raised `HoldoutRetiredError`. C4's own text says "a typo
must not brick a family"; the implementation delivered exactly that outcome.

**Fix:** `HoldoutVault.seal()` gains a required `passphrase` argument. At seal time it writes
`verifier.json` — a salt plus `sha256(_derive_key(passphrase, salt))` — **never the passphrase itself,
never the Fernet key itself** (a second hash sits between the verifier and the encryption key, so a
leaked `verifier.json` cannot be used to decrypt `payload.enc`). `acquire_once` (and, per §7, also
`authorize_retry`) now calls a shared `_verify_passphrase()` that recomputes the verifier hash from the
supplied passphrase and compares it **before any network call and before any state change**. On mismatch:
logs `holdout_bad_passphrase_attempt`, raises `HoldoutPassphraseError`, vault state stays `SEALED`
(unretired, unsealed-payload).

**Tests:**
- `test_ACC_C2_wrong_nonempty_passphrase_refused_not_retired` — the I-015 scenario verbatim: typo refused,
  `fetch.calls == 0`, `not is_retired()`, `state == SEALED`.
- `test_ACC_C2_correct_passphrase_recovers_after_wrong_attempt` — the vault is not bricked; the correct
  passphrase still acquires and the payload later decrypts.
- `test_ACC_C2_seal_requires_nonempty_passphrase` — negative on `seal()` itself.
- (re-audit) `test_ACC_C2_authorize_retry_requires_correct_passphrase` — see §7.

**Interpretive decision, flagged for Validation:** Ruling 001 D3 describes the passphrase as "supplied at
[Gate 1]," and I have moved *commitment to a verifier* for it to `seal()` (Gate 0). This is the most literal
reading of "**seal-time** passphrase verifier," and Acceptance 001 §8's own fallback text ("a seal-time
passphrase verifier ... store, or ... requires the passphrase twice") anticipates exactly this design.
The operational consequence: **the Principal must decide the Gate-1 passphrase at Gate-0 sealing time**,
not fresh at Gate 1. If that is undesirable, the fallback in §8 (double-supply at `acquire_once`, roll back
to `SEALED` and delete `payload.enc` on a failed self-check) is a straightforward alternative — I did not
need it because the verifier construction avoids storing anything "the Principal would recognise as the
passphrase," which is the condition Validation set for preferring the primary design.

---

## 4. C-3 — `PITStore` required, not optional

`HoldoutVault.__init__`'s `store` parameter lost its `=None` default; passing `None` explicitly (bypassing
static typing) raises `HoldoutSpecInvalidError`. `seal()` carries an independent, redundant guard for the
same reason (`if self.store is None: raise ...`), satisfying the literal "seal() raises without one."

**Tests:** `test_ACC_C3_store_required_at_construction` (constructor), `test_ACC_C3_store_required_at_seal`
(simulates a caller that set `.store = None` post-construction, bypassing the constructor guard).

No legitimate no-store use case was found; Validation's own fallback (`store=None,
no_ceiling_justification=...`) was not needed.

---

## 5. C-4 — `ingest_documents()` ceiling parity (closes I-017)

`PITStore._enforce_holdout_ceiling` was refactored into a shared `_enforce_holdout_ceiling_on_index`,
callable with any `DatetimeIndex`. `ingest()` calls it via the existing per-DataFrame path;
`ingest_documents()` — previously **unguarded entirely** — now builds an index from every doc's
`event_time` and checks it, atomically, **before any row is inserted**: a batch containing one compliant
doc and one post-`C` doc inserts neither.

**Tests:** `test_ACC_C4_ingest_documents_accepts_at_or_before_cutoff` (positive),
`test_ACC_C4_ingest_documents_enforces_ceiling` (negative, asserts `COUNT(*) FROM documents` unchanged
and `holdout_ceiling_violation` logged).

---

## 6. C-5 — UTC normalization at ingest (closes I-016)

`PITStore._iso()` previously did `pd.Timestamp(ts).isoformat()`, preserving the caller's own UTC offset.
Two observations at the same instant but different offsets therefore sorted and compared as different
strings — the measured false negative: a bar at `America/New_York 21:00` (`= 2024-07-01T01:00Z`), inside a
holdout opening at `C = 2024-07-01T00:00Z`, was stored as `2024-06-30T21:00:00-04:00` and
`rows_in_window` returned zero rows. Fixed: `_iso()` now localizes-or-converts every timestamp to UTC
before formatting, so every stored `event_time` string comparison is an instant comparison.

**Side effect found and fixed in the same change:** `PITStore.asof()` builds its returned DataFrame index
via `pd.to_datetime(wide.index)`, which — once storage is uniformly UTC — started returning a **tz-aware**
index where it previously returned tz-naive (for the common naive-input case). This broke three
pre-existing `test_data_book.py` tests that index the result with naive `Timestamp`s. Fixed by stripping
the tz label on `asof()`'s output (`idx.tz_convert(None)` when tz-aware) — numerically a no-op for the
previously-common naive-input path (identical output to before C-5), and for genuinely tz-aware non-UTC
input it now correctly represents the true UTC instant rather than the caller's local wall-clock string.
This is a storage/comparison-correctness fix, not a promise about what tz-awareness downstream consumers
get back, and I want that distinction on the record rather than discovered later.

**Tests:** `test_ACC_C5_event_time_normalized_to_utc_at_ingest` (exact stored string assertion),
`test_ACC_C5_leak_detector_catches_nonutc_timezone_leak` (the measured probe from Acceptance 001 §3,
now returning 1 leaked row instead of 0).

---

## 7. C-6 — `holdout_opened_once` removed (closes I-014)

`evaluate_gate1`'s `holdout_opened_once: bool | None = None` parameter and its entire bypass branch are
**deleted**, not deprecated. There is now exactly one way the "Holdout single-use" criterion can be
computed: from the registry's own event log, family-scoped. No caller argument can substitute a narrated
verdict for it. (This is also why the call is now keyword-only past `periods_per_year` — see §9 — which
made removing a parameter a source-compatible-by-keyword change rather than a silent positional shift.)

No dedicated regression test asserts "the parameter no longer exists" (Python doesn't need one — a
`TypeError: unexpected keyword argument` would occur naturally if it were reintroduced and any test still
passed it); the property is instead evidenced positively: every existing "Holdout single-use" test
(C1–C10, D1–D2, E1–E3) now exercises the single registry-derived code path, since there is no other path
left to exercise.

---

## 8. C-7 — acquisition-side non-overlap enforcement (the missing half of property 3)

This is the item Validation's ruling spent the most words on, so I'm being explicit about what "enforced,
not merely asserted" means here.

**Where it lives:** `HoldoutVault.acquire_once()`, immediately after `fetch(spec)` succeeds and before the
C10 schema check. The fetched frame's index is normalized to UTC and compared against the sealed cutoff:
if **any** row has `event_time <= C`, the acquisition is refused as a **C6-class failure** — same state
machine as a network error or schema mismatch: `ACQUISITION_FAILED`, not retired, gated behind
`holdout_retry_authorized` for any further attempt. A new exception type,
`HoldoutAcquisitionOverlapError(HoldoutAcquisitionFailedError)`, names the specific cause while preserving
the C6 `isinstance` relationship the state-machine logic depends on.

**Why this is the load-bearing fix.** Acceptance 001 measured, against the shipped code, that a `fetch`
returning 2,000 days starting 2010-01-01 against `C = 2020-01-01` was accepted, sealed, and reported
`PASS` on the holdout criterion. B2/B3/B6 (already covered) guarantee no row after `C` enters `pit.db` via
`ingest()`. They say nothing about what `acquire_once` does with a fetch callable that hands back
in-sample history directly — the half of "no overlap between the two samples" that never touched the
store at all. C-7 closes that.

**Assertion, not just enforcement:** the F1/F2 replacement test (§2) asserts
`acquired.index.min() > cutoff` on a successful acquisition, and two dedicated tests assert the negative
directly:

- `test_ACC_C7_acquisition_refuses_row_at_or_before_cutoff` — a `fetch()` returning the tail of the
  in-sample period (all rows `<= C`) is refused with `HoldoutAcquisitionOverlapError`, state moves to
  `ACQUISITION_FAILED`, `holdout_acquired` never lands, and — the "not bricked" half — an authorized retry
  with a correct `fetch()` still succeeds afterward.
- `test_ACC_C7_acquired_index_min_strictly_after_cutoff` — the positive form, standalone.

---

## 9. P-series — pre-registration sealing (D-006 rider)

`TrialRegistry.open_hypothesis` now:

- **(P1)** computes `prereg_sha256` over canonical (`sort_keys=True`, UTF-8) JSON of the 15-field binding
  set (P2) and logs a `hypothesis_sealed` event carrying the hash **and the complete field set** — a full
  shadow copy in the append-only `events` table, not a pointer to the mutable row.
- **(P3)** on re-registration of an existing family: any differing binding field raises
  `PreRegistrationAmendedError` and logs `hypothesis_amendment_refused` naming the differing fields;
  byte-identical re-registration stays idempotent and logs nothing. Both branches tested.
- New `TrialRegistry.verify_prereg(family)` recomputes the hash from the **live** row and compares it to
  the sealed event — the A4 analogue. **(P4)** A raw `UPDATE hypotheses SET falsifier=...` is detected:
  `verify_prereg` reports the mismatch by field name, and `evaluate_gate1` gains a new
  **"Pre-registration integrity"** criterion that returns **FAIL** on it.
- **(P6)** A family with no `hypothesis_sealed` event (pre-P-series row, or a raw `INSERT` bypassing
  `open_hypothesis`) reads **INSUFFICIENT-DATA**, never PASS.
- **(P7)** the criterion also **FAILs** if the sealed timestamp postdates the family's
  `holdout_spec_sealed` cutoff `C`, compared at **UTC day granularity** — the D-006 rider mechanised.
  Tested both directions (`test_P7_prereg_sealed_after_cutoff_fails_gate`,
  `test_P7_prereg_sealed_on_or_before_cutoff_passes`).
- **(P5)** `ValidationReport` gains `prereg_sha256`, rendered in `to_markdown()`.
- **(P8)** `ValidationReport` gains `predecessor_prereg_sha256: dict[family, sha256]`, populated by
  walking `registry.predecessor_chain()` and calling `verify_prereg` on each ancestor; rendered in the
  markdown.

**Not implemented as a separate mechanism, deliberately:** §2.4/§3.4's `holdout_spec_amended` transport
path remains absent, exactly as Ruling 001 already logged ("the bricking failure mode is avoided by
omission"). Nothing in Acceptance 001's P-series asked for it, and I did not add it.

---

## 10. G-series — I-010 (`backtest_years` / `oos_index`)

- **(G1)** `backtest_years` is now a **required, keyword-only** argument to `evaluate_gate1`; the fallback
  `r.size / periods_per_year` is **deleted**, not defaulted.
- **(G2)** a new `oos_index: pd.DatetimeIndex | None = None` parameter. Where supplied,
  `years_calendar = (max - min).days / 365.25` is computed and is what the length criterion is actually
  evaluated against; `backtest_years` is reported in the criterion's note alongside it.
- **(G3)** if both are supplied and disagree by more than 5% of the calendar figure
  (`LENGTH_DISAGREEMENT_MAX`), the criterion is **FAIL**, with both numbers in the note.
- **(G4)** if `oos_index` is `None`, the criterion is **INSUFFICIENT-DATA**, unconditionally — tested with
  `backtest_years=100.0` (a wildly generous claim) to make sure a large number cannot buy PASS on trust.
- **(G5)** the exact I-010 case reproduced: 1,500 rows at `periods_per_year=252` (≈5.95 apparent years) over
  an 18-month `oos_index` → **FAIL** with a disagreement note. Under the deleted fallback this read as
  clearing the 4-year floor.
- `evaluate_gate1` signature is now `(strategy, family, registry, oos_net_returns, periods_per_year, *,
  backtest_years, oos_index=None, ...)` — everything past `periods_per_year` is keyword-only, which is
  what let `holdout_opened_once`'s removal (C-6) and `backtest_years`'s new required status land without
  touching any call site's positional arguments. **All ~10 call sites** (test files + `demo_workflow.py`)
  were updated under the pre-authorization in Ruling §6 — no assertion moved to accommodate this; every
  edit is an added keyword argument.
- `examples/demo_workflow.py` corrected: it previously passed `len(prices) / 252` (in-sample + holdout
  combined) as `backtest_years` against an `oos_net_returns` that was holdout-only — exactly the "sole
  existing caller already passes the offending value" case I-010 named. Now passes
  `backtest_years=len(holdout) / 252` and `oos_index=holdout.index`.

---

## 11. R1–R4 schema (I-018)

`hypotheses` gains six nullable columns via both `CREATE TABLE` (new DBs) and `_migrate()` (existing
ones, same pattern as the pre-existing `predecessor_family` migration): `holdout_classification`,
`forward_window_start`, `forward_window_min_length`, `forward_kill_condition`, `model_prior_provenance`,
`published_signal_haircut_applied`. `open_hypothesis` accepts all six as optional keyword arguments and
validates `holdout_classification ∈ {FORWARD, HISTORICAL, None}`; **R3** is enforced as a hard requirement:
a `HISTORICAL` classification without `forward_window_start` / `forward_window_min_length` /
`forward_kill_condition` raises `ValueError` at registration, not later at Gate 1.

`ValidationReport` gains `holdout_classification: str | None`, populated from the family's row and
rendered on the report's face (**R1**); a `HISTORICAL` classification renders the exact required sentence
from Ruling 001 §2.4 / Ruling 002 R1 verbatim.

This closes I-018's blocking effect: a family can now be pre-registered with its R1/R3/R4 binding fields,
which is the precondition Validation's fourth Opus unit (Gate 0 intake) needs before it can run.

**Not implemented, and stated so it isn't discovered later:** R4(a)'s per-seat model-cutoff provenance
recording and R4(b)'s presumptive 50% haircut are **not** wired into any automatic enforcement —
`model_prior_provenance` and `published_signal_haircut_applied` are plain optional fields a caller can
set, with no code that currently derives or checks them. Acceptance 001 did not ask for that wiring (it
scoped I-018 to "the schema and the report field," which is done); flagging the boundary so it isn't
assumed to be more automated than it is.

---

## 12. Condition-by-condition summary

| # | Condition | Change | Proving test(s) |
|---|---|---|---|
| C-1 | F1/F2 replacement test | `test_harness.py`, in place, renamed | `test_holdout_ceilings_and_acquires_once_p1` |
| C-2 | Seal-time passphrase verifier | `holdout.py` `seal()`/`_verify_passphrase()` | `test_ACC_C2_*` (4 tests, incl. re-audit) |
| C-3 | `PITStore` required | `holdout.py` `__init__`/`seal()` | `test_ACC_C3_*` (2 tests) |
| C-4 | `ingest_documents()` ceiling | `data.py` shared enforcement helper | `test_ACC_C4_*` (2 tests) |
| C-5 | UTC normalization | `data.py` `_iso()` + `asof()` fix | `test_ACC_C5_*` (2 tests) + 3 pre-existing `test_data_book.py` tests kept green |
| C-6 | `holdout_opened_once` removed | `gates.py` signature + branch deleted | evidenced by every "Holdout single-use" test using the single remaining path |
| C-7 | Acquisition-side non-overlap | `holdout.py` `acquire_once()` post-fetch check | `test_ACC_C7_*` (2 tests) + F1/F2 replacement |
| C-8 | Strengthen vacuous encryption test | `test_holdout_p1.py`, in place | `test_C8_payload_encrypted_at_rest` (rewritten) |
| C-9 | Ceiling lift provenance | `data.py` schema + `_lift_ceiling()`; `holdout.py` passes event id | `test_ACC_C9_ceiling_records_which_acquisition_lifted_it` |
| C-10 | A3 `source` + malformed-cutoff | `test_holdout_p1.py` parametrize + new test | `test_A3_malformed_spec_raises[source]`, `test_A3_malformed_cutoff_raises` |
| P1–P8 | Pre-registration sealing | `registry.py` `open_hypothesis`/`verify_prereg`; `gates.py` criterion | `test_P1`…`test_P8` (8 tests) |
| G1–G5 | `backtest_years`/`oos_index` | `gates.py` signature + length criterion | `test_G1`…`test_G5` (5 tests) |
| R1/R3 | Schema + report field | `registry.py` columns/validation; `gates.py` report field | `test_R1_*` (2), `test_R3_*` (1) |

---

## 13. Re-audit — hunting for the C4/I-015 shape elsewhere

**The shape to hunt for:** a test whose assertions can be satisfied by code that does not have the
property the test's name/docstring claims — C4 asserted `fetch.calls == 0` for `passphrase=""` only, which
is true, but the criterion's actual purpose ("a typo must not brick a family") was never tested and was
in fact violated.

**What I found, and fixed, during implementation (not held back for this section):**

`HoldoutVault.authorize_retry()` had the **identical defect shape**: `if not passphrase or not
passphrase.strip(): raise HoldoutPassphraseError(...)` — a presence check, not a cryptographic one, on
"the Principal's passphrase" that Ruling 001 D3 requires for retry authorization. The existing test,
`test_C7_authorized_retry_succeeds_and_counted`, only ever supplied the correct passphrase
(`"hunter2"`) — it never exercised the wrong-passphrase branch at all, so it could not have caught this
either way. The blast radius is smaller than C4's (a bad retry-authorization doesn't seal a payload or
retire anything — it just logs `holdout_retry_authorized`, which then lets a *subsequent, still-gated*
acquisition proceed), but the property violated is the same one: a typo should not count as "the Principal
authorized this." Fixed by routing `authorize_retry` through the same `_verify_passphrase()` C-2 built, and
added `test_ACC_C2_authorize_retry_requires_correct_passphrase`, which asserts the wrong passphrase raises,
logs nothing, and leaves the retry still blocked — the negative case that was previously untested in
either direction.

**What I checked and found clean:**

- **`pytest.raises(Exception)` (over-broad exception assertions).** Two instances existed after my
  changes. One (`test_C8_payload_encrypted_at_rest`, parsing raw ciphertext as parquet) is legitimately
  generic — the property under test is "this does not parse as valid parquet," and the specific exception
  type is a library-internal detail I don't want the test coupled to. The other, in my own new
  `test_holdout_ceilings_and_acquires_once_p1`, was tightened to `HoldoutCeilingError` specifically once
  I noticed it — a broad `Exception` there would have passed even if the ceiling check were replaced by an
  unrelated bug, which is exactly the "test passes on the wrong evidence" pattern this section is for.
- **C3 (spec-hash mismatch, no network call).** Genuinely asserts `fetch.calls == 0` via an injected
  counting callable — matches what the criterion claims.
- **B3/B5 atomicity and mutation-refusal tests.** Re-checked against the current code; unchanged by this
  sprint's work and still exactly as Validation characterized them in Acceptance 001 (B3 genuine; B5
  proven for the direct-mutation path it tests, with the "cannot be raised even after a prior lift"
  sub-property still proven by reading rather than by test — already disclosed, not newly found, not
  touched here).
- **D1 leak detection.** Still asserts a real logged event and a real `FAIL` verdict; strengthened rather
  than weakened by the C-5 UTC fix (it now catches a class of leak it previously missed).
- **New P-series and G-series tests**, re-read specifically for this section: each asserts either a
  specific exception type, a specific criterion verdict plus its distinguishing note text (e.g.
  `"DISAGREEMENT"`, `"postdates"`), or a specific field-name list — none rely on a vacuous string-absence
  check or an over-broad exception class.

**What I did not chase further, and am saying so rather than declaring the audit exhaustive:** the
`_verify_passphrase` fallback branch for a vault sealed before C-2 (missing `verifier.json` →
`FileNotFoundError` → fail closed) has no dedicated test — it is defensive code for a migration edge case,
not a property any current test claims to cover, so it isn't an instance of the pattern this section is
about, but it is genuinely untested and I want that on the record rather than silently assumed safe. The
"Trial count N (registry) — OVER BUDGET" branch in `gates.py` (verdict is hardcoded PASS with a note, even
when `n_trials > trial_budget`) is pre-existing, untouched by this sprint, and no test claims it fails on
over-budget — so it is not a case of a test passing on a false premise, but it is a design question I am
flagging rather than silently passing over, since an over-budget trial count that still reads PASS is at
least adjacent to the class of finding this review is about.

**Verdict on the re-audit:** one real instance found and fixed (`authorize_retry`), one test tightened
from over-broad to specific (`HoldoutCeilingError`), nothing else in the suite exhibits the "assertion
narrower than the claimed property" shape as far as I can tell from a full read of every test file
touched or adjacent to this sprint's work.

---

## 14. What is not done, and why

- **`DATA-SPEC-polymarket-usable-history.md`** — separate, still-outstanding deliverable per Ruling 001
  §4; not part of this task's instructions and not attempted here.
- **Data fetch / ingest / backtest / commit** — out of scope by explicit task instruction; none performed.
- **Self-granted acceptance** — not claimed; this document records what changed and what tests prove it,
  not a verdict on whether it clears the bar. That is Validation's, per the binding constraints on this
  task and per Ruling 001 §6/§7.
- **R4(a)/(b) automatic enforcement** (model-prior provenance derivation, presumptive haircut
  application) — schema exists, fields are settable, nothing computes or checks them yet; noted in §11 so
  it isn't assumed to be wired up.

---

*Head of Data & Infrastructure · Castellan Capital · 2026-07-28*
