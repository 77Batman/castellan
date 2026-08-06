# DATA-IMPL-007 — Implementation of VALIDATION-SPEC-003 (B-1 … B-31, RULING 003-A)

**Seat:** Head of Data & Infrastructure (Seat 9) · **Dispatch:** S2-D-029 · **Issue range:** I-110 … I-119
**Date:** 2026-08-06
**Instrument implemented:** `research/VALIDATION-SPEC-003-budget-enforcement.md`, clauses B-1 … B-31 and RULING 003-A. Not amended, not touched.
**Files changed:** `harness/castellan/gates.py`, `harness/castellan/registry.py`.
**Files NOT touched:** any test file, any `VALIDATION-*`/`PREREG-*` document, `book/vaults/`, `book/registry.db` (0 hypotheses / 0 trials before and after, measured). Nothing committed, per dispatch constraint.

---

## 1. Result summary

| Check | Result |
|---|---|
| `harness/tests/test_trial_budget_enforcement.py` | **27/27 collected items green** (19 test functions, `test_tbe_12` parametrized ×9) |
| `test_tbe_17` (B-22 genericity guard) | **still green**, checked against the post-implementation source |
| Whole suite | **271 passed / 4 failed / 275** — matches the dispatch's stated floor exactly |
| The 4 failures | `test_G2` (`test_holdout_p1.py`), `test_mbs_12` (`test_minbtl_serial.py`), `test_h7`, `test_h8` (`test_seeded_n.py`) — **identical in identity AND failure reason** to the pre-dispatch baseline (verified by running the same 4 against a `git stash` of this change); none touched, none mine |
| `book/registry.db` | 0 hypotheses / 0 trials, measured before and after |
| `book/vaults/` | untouched |
| I-022 | implementation landed, all 19 tests green — see §5 |

---

## 2. What was mechanical (§6.1's list, B-1/B-2/B-3, B-6/B-7/B-8, B-9…B-12, B-13…B-15, B-16…B-21, B-23/B-24/B-26, B-25/B-27) — implemented as written

The bulk of the specification translated directly into code with no judgment calls:

- **`TrialRegistry.own_trial_times(family)`** (`registry.py`) — B-28's new accessor, exactly as specified: `created_utc` of this family's own trials, ascending, **not** transitive across `predecessor_family`.
- **`contingent_increment_allowed(n_max, declared_ceiling_base, declared_increment)`** (`gates.py`, module-level, pure) — B-18/B-28's clamp, unit-graded directly by `test_tbe_15`.
- **`_validate_extension_schema`** — B-13's exhaustive key/type table plus B-17's closed predicate vocabulary, schema-only (no registry access).
- **`_admissible_ceiling`** — B-18/B-19's `N_max = min(n_max_admissible_iid, n_max_admissible_serial)`, computed from the *same* `stats.max_admissible_trials` calls the length criterion already makes further down — no new statistic, per B-18's own requirement.
- **`_budget_extension_ledger`** — B-9's per-trial ordering walk's data layer: withdrawal (B-24), malformation + B-21's cross-check, B-14/B-15's discretionary admission rule, B-16's contingent recomputation, B-20's aggregate cap consumed in creation order via repeated calls to `contingent_increment_allowed` with a running base offset (this is the same clamp function, not a second formula — B-18's arithmetic generalises to N events exactly by raising the base by each earlier event's own admitted amount).
- **`_trial_budget_criterion`** — B-6/B-7/B-8's three stated verdicts on three stated conditions, B-9/B-11's walk and note format, B-25's row (name unchanged, `value` unchanged at `fam.n_trials`, threshold satisfying both contract regexes, chain-summed disclosure), B-27's four new `ValidationReport` fields as report fields (not `Criterion` rows — `test_hac_t14`'s precedent, unaffected: I added zero new criteria, only new dataclass fields).
- **B-29 ordering** — `sr_ann` and `vif_res` are computed once, hoisted to immediately after `fam = registry.family_stats(family)` (previously computed later, at their original call sites). The trial-budget criterion is still the **first** `criteria.append(...)` call in `evaluate_gate1`, unchanged from before this dispatch — I chose the "hoist the N_max computation" option B-29 offered rather than "build the row later and insert at index 0," because it avoids two independent computations of the same VIF/N_max ever existing in the function (a correctness risk B-29's second option would have introduced for no benefit). The two downstream sections ("core performance", "VIF, measured once") now just *use* the hoisted values; I left comments marking the hoist so a future reader does not "fix" what looks like a duplicate.

## 3. Where the specification required interpretation, and what I did

Nothing here contradicts B-1…B-31; these are places the letter of the clause under-determined an implementation choice, and I record the choice rather than let it be invisible.

1. **Priority ordering among B-7 / B-8 / B-23 / B-9 was not stated explicitly.** I implemented: malformed-extension check first (absolute per B-23's own "even where comfortably inside budget" language, applied regardless of `m`), then B-8's vacuous PASS (`m == 0`), then B-7's non-positive-sealed-budget FAIL, then B-9's walk. This means a malformed extension FAILs the Gate even for a family with zero own trials — B-23 doesn't carve that out, and I didn't invent a carve-out either.
2. **B-7 is unconditional.** A non-positive sealed budget FAILs regardless of any well-formed extension that might otherwise raise the effective budget above zero. The clause's text ("no extension buys a family out of...") doesn't literally say this, but its framing ("the purest case the criterion exists for") reads as absolute, and I implemented it that way rather than adding an extension-rescues-a-zero-budget escape hatch nothing in the spec asks for.
3. **Status granularity beyond what any test checks.** B-27 lists `REFUSED-UNCOUNTERSIGNED` and `REFUSED-SELF-ISSUED` as distinct statuses. I distinguish them: no countersignature at all → `REFUSED-UNCOUNTERSIGNED`; countersigned by the issuer itself → `REFUSED-SELF-ISSUED`; countersigned by someone outside the allow-list → `REFUSED-UNCOUNTERSIGNED`; a `DISCRETIONARY` issuer outside `{director-of-research, principal}` entirely → `REFUSED-UNCOUNTERSIGNED` (no clean home in the enum; this is the closest fit since there is no admission route for it at all). None of this is asserted by any test — see I-112.
4. **The "+ N extension" threshold suffix.** B-25's reference form says `"... + {total_admitted} extension)"` "where extensions exist, else `")"`." I read "extensions exist" as "the total admitted increment is nonzero," not "an extension event was logged" — a family with an extension event that was fully refused renders as if no extension existed (`test_tbe_10`, `test_tbe_19` both confirm `effective budget 5` with no visible "+0 extension" clutter).
5. **`eff_final` (the reported effective budget) vs. the per-trial walk's `eff(t_k)`.** These are computed differently on purpose: `eff_final = sealed + Σ admitted increments` (a "where things stand now" figure, since every logged event's `effective_from` is necessarily ≤ evaluation time), while the walk evaluates `eff(t_k)` per trial using each admitted extension's own `effective_from`. This is what lets `test_tbe_08` report `effective budget 10` (via `eff_final`, in the threshold string — not directly asserted, but consistent) while still FAILing on trial 6 (via the walk).
6. **B-26 (duplicate `authorization_ref`) applied uniformly across both modes**, checked immediately after schema/B-21 validation and before mode-specific admission logic, rather than scoped to one mode. Nothing in B-26's text restricts it to `DISCRETIONARY`, and "one authorization artifact, one increment" reads as mode-agnostic.
7. **Negative sealed budgets are rendered literally** (`sealed -1`), which does not satisfy B-25's `sealed (\d+)` contract regex. No test exercises this combination (`test_tbe_04` never reads the threshold string). I did not invent a rendering convention for it — filed as **I-114** rather than silently picking one, since B-7 already makes this case a terminal, unconditional FAIL where the exact magnitude has no consumer I could find a rule for.

## 4. Red-for-the-right-reason verification

Per the Principal's added standard (mirroring RULING 005-A's method), I reverted each named protection on a **scratch copy** (`/private/tmp/.../scratchpad/harness_scratch`, discarded, never committed, never touched the real repo) and re-ran the naming test(s). All match; the two nuances are filed, not silently absorbed.

| Clause | Protection removed (scratch) | Test(s) | Result |
|---|---|---|---|
| B-6 | Walk violation never produces FAIL | `test_tbe_01`, `05`, `06` | **red** (3/3) |
| B-7 | Non-positive-sealed-budget branch deleted | `test_tbe_03`, `04` | **red** (2/2 — falls through to the walk, which still FAILs on the *first* trial, but the required `"NO AUTHORIZED BUDGET"` note is gone, so the assertion catches it) |
| B-9 | `eff(t_k)` replaced by the aggregate `eff_final` (spend-first-authorize-after) | `test_tbe_08`, `09` | **red** (2/2) |
| B-14 | Director-issued extension auto-admits, no countersignature | `test_tbe_10` | **red** |
| B-15 | Principal also required to obtain a countersignature | `test_tbe_11` | **red** |
| B-16 | Contingent extension trusts the event's own claim instead of recomputing | `test_tbe_14` | **red** |
| B-17 | Predicate vocabulary opened (any name/params accepted) | `test_tbe_16` | **red** |
| B-18/B-20 | `contingent_increment_allowed` returns the declared increment unclamped | `test_tbe_15` | **red** |
| B-21 | `n_logged_at_issue` cross-check removed | `test_tbe_12` (all 9 parametrizations) | **red on exactly `[bad8]`, the one that names the cross-check; the other 8 stay green** — confirms each parametrization is independently diagnostic |
| B-23 | Malformed extension no longer FAILs the Gate | `test_tbe_12` | **red on all 9** |
| B-24 | Withdrawal no longer neutralises | `test_tbe_13` | **red** |
| B-1 | `own_trial_times` made transitive across `predecessor_family` (via `registry.py`) | `test_tbe_18` | **red** (verdict flips PASS→FAIL, as predicted) |
| B-25 | Chain-summed disclosure suffix removed | `test_tbe_18` | **red** (note assertion) |
| B-4 / C-6 | Extension query loosened to a substring ("`budget`" in `kind`) instead of exact `kind == "trial_budget_extension"` | `test_tbe_19` | **stayed green** — see note below |
| — | Extension mechanism deleted entirely (`exts = []`) | `test_tbe_07` | **red**; `test_tbe_02` (unaffected boundary case) stayed green as expected |
| B-9 (back-dating) | `created` read from `detail.get("issued_utc", ...)` | `test_tbe_08`, `09` | **stayed green** — see I-113 |

**Two findings from this table, both filed rather than silently absorbed:**

- **B-4/C-6:** loosening the exact `kind` match to a fuzzy `"budget" in kind` substring still leaves `test_tbe_19` green, because the bogus events in that test's fixture (`{"increment": 100, "issuer": "principal", "mode": "DISCRETIONARY"}`) are missing `reason`/`authorization_ref`/`n_logged_at_issue` and would be rejected as **malformed** if picked up at all — same FAIL verdict, same reported `effective budget 5`, different internal reason. The shipped code uses the exact match (verified by inspection: `registry.events(kind="trial_budget_extension", family=family)`), so there is no live defect, but the test alone does not discriminate "unknown kinds are never even considered" from "unknown kinds are considered and rejected." Not filed as a defect — recorded in this document for completeness; I-113 (below) is the more material sibling of this shape.
- **B-9 back-dating (`test_tbe_09`):** filed as **I-113**. Reverting the single most direct form of "read the claimed date instead of the registry's own timestamp" does not turn the test red, because the fixture's `DISCRETIONARY` + valid-countersignature scenario has a *second* independent protection — B-12's `effective_from = max(created, countersignature.created_utc)` — that catches the same attack via the countersignature's own (real) timestamp. The shipped code has no code path reading a `detail`-embedded date at all, so there is no live defect; the finding is that this specific test cannot, by itself, prove that absence for the `PRINCIPAL`-issued or `CONTINGENT` paths, which lack the countersignature rescue. Full writeup in the Issue Log.

## 5. I-022

**Can close.** All 19 test functions (27 collected items) in `test_trial_budget_enforcement.py` are green, `test_tbe_17` (B-22) is still green post-implementation, and the whole-suite floor (271/4/275) is met exactly, with the 4 remaining failures verified identical to the pre-dispatch baseline. Per SPEC-003 §8's own words — *"I-022 closes on Seat 9's implementation of B-1 … B-31 with all 19 tests green — not before"* — that condition is now satisfied. I have not marked it CLOSED myself in the Issue Log; I do not own the Issue Log (CRO does) and I-022 is Validation's issue. I filed a status entry with the measured facts (`logs/ISSUE_LOG.md`) for the CIO/Validation to record the disposition.

## 6. §6.2 judgment calls hit

**None.** Every §6.2 trigger requires a real family in the registry (an out-of-vocabulary predicate appearing "in any real family," a verdict turning on `REFUSED-PREDICATE` "for a real family," a grandfathering request, a transitive-budget proposal against a real precedent, two real extensions sharing a ref "for an innocent reason," or a named test in the file that cannot be met as specified). `book/registry.db` holds 0 hypotheses throughout this dispatch, and all 27 tests were met exactly as written — nothing routed back.

## 7. Issues filed (I-110 … I-119 range; I-115 … I-119 unused)

| # | Sev | Subject |
|---|---|---|
| I-110 | LOW | B-26 (duplicate `authorization_ref`) implemented, no dedicated acceptance test |
| I-111 | LOW | B-8's second sentence (vacuous PASS, `n_own_logged==0` with chain `>=1`) implemented, no dedicated acceptance test |
| I-112 | LOW | B-27's four new report fields populated, none read directly by any test |
| I-113 | LOW | `test_tbe_09`'s named protection not uniquely discriminated by the test — overlapping protection (B-12) masks it in this fixture; no live defect in shipped code |
| I-114 | LOW | B-25's `sealed (\d+)` contract regex cannot match a negative sealed budget; unexercised, routed rather than silently rendered |

Full text of each: `logs/ISSUE_LOG.md`.

## 8. File paths

- `harness/castellan/gates.py` — `contingent_increment_allowed`, `_validate_extension_schema`, `_admissible_ceiling`, `_budget_extension_ledger`, `_trial_budget_criterion`, hoisted `sr_ann`/`vif_res`, four new `ValidationReport` fields.
- `harness/castellan/registry.py` — `TrialRegistry.own_trial_times`.
- `harness/tests/test_trial_budget_enforcement.py` — read only, not modified.
- `logs/ISSUE_LOG.md` — I-022 status entry, I-110 … I-114.
- `research/DATA-IMPL-007-budget-enforcement.md` — this document.
