"""Acceptance tests for VALIDATION-SPEC-003 (clauses B-1 ... B-31) — the
trial-count criterion, I-022's substantive fix.

Authored by the Head of Quantitative Validation BEFORE implementation.

THE PROPERTY THESE TESTS ARE:

    An over-budget family must not be able to read PASS, and the two-stage
    budget's lock must be enforced by the harness rather than asserted by
    the sponsor.

Today `harness/castellan/gates.py` builds this criterion with the verdict
argument hard-coded to the literal `True`:

    over = fam.trial_budget and fam.n_logged > fam.trial_budget
    criteria.append(_crit(
        "Trial count N (registry)", fam.n_trials,
        f"logged; budget {fam.trial_budget}", True,
        "OVER BUDGET — flagged to Director of Research" if over else ""))

`over` is computed and then used ONLY to write a note. A family that has
blown its pre-registered trial budget — the precise condition Charter
house rule 3 and section 4.1 exist to catch — reports PASS.

SEAT 9 DOES NOT MODIFY ANY TEST IN THIS FILE UNDER ANY CIRCUMSTANCES.
A failure here is escalated to Validation in writing (Ruling 004 section
11's standing term). That term has caught a Validation-authored defect
three times this sprint (I-058, I-070, I-065) and it binds the author as
hard as the implementer: if a clause cannot be met as specified, the
clause is wrong and I fix it, in writing, on the record.

RED BY DESIGN.
"""

from __future__ import annotations

import inspect
import re

import numpy as np
import pandas as pd
import pytest

from castellan import TrialRegistry, evaluate_gate1
from castellan import gates

CRIT = "Trial count N (registry)"
PASS, FAIL, INSUFF = "PASS", "FAIL", "INSUFFICIENT-DATA"


# ----------------------------------------------------------------------
# helpers
# ----------------------------------------------------------------------

def _series_at_sharpe(sr_ann, n, ppy=252, std=0.01, seed=0):
    """An i.i.d. draw affine-shifted to hit `sr_ann` EXACTLY in sample.

    Deliberately not `test_seeded_n.py::_calibrated_returns`, which I-067
    records as emitting rho_hat ~ +0.55 against its own docstring. These
    fixtures need a KNOWN N_max, which means they need a known Sharpe AND
    a VIF near 1; a helper with hidden serial structure would deliver
    neither. Every fixture below that depends on N_max asserts its own
    measured VIF rather than assuming it.
    """
    x = np.random.default_rng(seed).standard_normal(int(n))
    x = (x - x.mean()) / x.std(ddof=1)
    return x * std + (sr_ann / np.sqrt(ppy)) * std


def _reg(tmp_path, name="r.db"):
    return TrialRegistry(str(tmp_path / name))


def _open(reg, family, budget, *, n_inherited=0, predecessor=None):
    reg.open_hypothesis(
        family=family, statement="s", mechanism="m", falsifier="f",
        universe="u", horizon="1d", success_criteria="sc",
        trial_budget=budget, n_inherited=n_inherited,
        predecessor_family=predecessor,
    )


def _log(reg, family, k, *, seed0=0, n=200):
    """Log `k` own trials, each with a real return series."""
    for i in range(k):
        reg.log_trial(family, {"i": i, "fam": family},
                      _series_at_sharpe(0.4, n, seed=seed0 + i), 252)


def _evaluate(reg, family, *, sr_ann=0.4, n=1300, seed=7, with_index=True):
    r = _series_at_sharpe(sr_ann, n, seed=seed)
    if not with_index:
        return evaluate_gate1("s", family, reg, r, 252, backtest_years=5.0)
    idx = pd.date_range("2019-01-01", periods=int(n), freq="B")
    years = (idx.max() - idx.min()).days / 365.25
    return evaluate_gate1("s", family, reg, r, 252,
                          backtest_years=years, oos_index=idx)


def _row(rep):
    return next(c for c in rep.criteria if c.name == CRIT)


def _effective_budget(rep) -> int:
    """B-25's contract regex. The criterion's threshold string MUST expose
    the effective budget as an integer a reader (and this test) can
    recover without knowing the implementation."""
    row = _row(rep)
    m = re.search(r"effective budget (\d+)", row.threshold)
    assert m, (
        "B-25 CONTRACT VIOLATED: the threshold string must expose "
        r"'effective budget <int>'. Got: " + repr(row.threshold))
    return int(m.group(1))


def _sealed_budget(rep) -> int:
    row = _row(rep)
    m = re.search(r"sealed (\d+)", row.threshold)
    assert m, (
        "B-25 CONTRACT VIOLATED: the threshold string must expose "
        r"'sealed <int>'. Got: " + repr(row.threshold))
    return int(m.group(1))


def _extension(reg, family, **detail):
    return reg.log_event("trial_budget_extension", family, detail)


def _countersign(reg, family, extension_event_id, countersigner):
    return reg.log_event(
        "trial_budget_extension_countersigned", family,
        {"extension_event_id": extension_event_id,
         "countersigner": countersigner})


def _discretionary(increment, *, issuer="director-of-research",
                   ref="research/MEMO-1.md", n_logged_at_issue=0,
                   reason="more search authorized"):
    return dict(mode="DISCRETIONARY", increment=increment, issuer=issuer,
                reason=reason, authorization_ref=ref,
                n_logged_at_issue=n_logged_at_issue)


def _contingent(increment, *, issuer="pm-digital-markets",
                ref="research/PREREG-X.md", n_logged_at_issue=0,
                reason="stage 2 unlock", params=None, name=None):
    return dict(mode="CONTINGENT", increment=increment, issuer=issuer,
                reason=reason, authorization_ref=ref,
                n_logged_at_issue=n_logged_at_issue,
                predicate={"name": name or "n_max_admits_declared_ceiling",
                           "params": {} if params is None else params})


# ======================================================================
# B-6, B-7 — the verdict
# ======================================================================

def test_tbe_01_over_budget_is_fail_not_a_note(tmp_path):
    """B-6. THE clause. Six trials against a sealed budget of five is an
    over-budget family, and an over-budget family must not read PASS.

    This is I-022 in one assertion. It has been true and untested since
    2026-07-28.
    """
    reg = _reg(tmp_path)
    _open(reg, "F", 5)
    _log(reg, "F", 6)
    row = _row(_evaluate(reg, "F"))
    assert row.verdict == FAIL, (
        "B-6 VIOLATED: 6 own logged trials against a sealed budget of 5 "
        f"produced verdict {row.verdict!r}. `over` is computed and used "
        "only to write a note; the verdict argument is the literal True.")
    assert "OVER BUDGET" in row.note


def test_tbe_02_at_budget_passes_and_reports_the_effective_budget(tmp_path):
    """B-25. Exactly at budget is PASS — the criterion must not become a
    machine that fails everything — and the row must expose the effective
    budget and the sealed budget as integers."""
    reg = _reg(tmp_path)
    _open(reg, "F", 5)
    _log(reg, "F", 5)
    rep = _evaluate(reg, "F")
    assert _row(rep).verdict == PASS
    assert _effective_budget(rep) == 5
    assert _sealed_budget(rep) == 5


def test_tbe_03_zero_sealed_budget_with_trials_is_fail(tmp_path):
    """B-7 / I-100 — THE DEFECT THAT SURVIVES THE OBVIOUS FIX.

    `over = fam.trial_budget and fam.n_logged > fam.trial_budget`
    short-circuits to a falsy `0` when the budget is zero, so the
    comparison is never evaluated. Changing the hard-coded `True` to
    `not over` leaves this family reading PASS with unbounded trials.

    A family that pre-registered no authorization and then spent trials
    is the purest case this criterion exists for.
    """
    reg = _reg(tmp_path)
    _open(reg, "F", 0)
    _log(reg, "F", 3)
    row = _row(_evaluate(reg, "F"))
    assert row.verdict == FAIL, (
        "B-7 VIOLATED: a sealed budget of 0 with 3 logged trials read "
        f"{row.verdict!r}. The `and` short-circuit disables the check.")
    assert "NO AUTHORIZED BUDGET" in row.note


def test_tbe_04_negative_sealed_budget_is_fail(tmp_path):
    """B-7. `open_hypothesis` performs NO validation on `trial_budget`
    while its adjacent binding sibling `n_inherited` is validated three
    ways (H-2). A negative budget seals without complaint (I-100)."""
    reg = _reg(tmp_path)
    _open(reg, "F", -1)
    _log(reg, "F", 1)
    row = _row(_evaluate(reg, "F"))
    assert row.verdict == FAIL
    assert "NO AUTHORIZED BUDGET" in row.note


def test_tbe_05_over_budget_fails_the_gate_overall(tmp_path):
    """B-6 + Charter 4.4: one FAIL fails the Gate. Asserted as a
    DIFFERENTIAL on one changed input, so it cannot pass on the many
    other criteria a minimal fixture also fails."""
    reg_ok = _reg(tmp_path, "ok.db")
    _open(reg_ok, "F", 50)
    _log(reg_ok, "F", 6)
    rep_ok = _evaluate(reg_ok, "F")

    reg_bad = _reg(tmp_path, "bad.db")
    _open(reg_bad, "F", 5)
    _log(reg_bad, "F", 6)
    rep_bad = _evaluate(reg_bad, "F")

    assert _row(rep_ok).verdict == PASS
    assert _row(rep_bad).verdict == FAIL
    assert rep_bad.overall == FAIL
    non_passing = [c.name for c in rep_bad.criteria if c.verdict != PASS]
    assert CRIT in non_passing
    assert CRIT not in [c.name for c in rep_ok.criteria if c.verdict != PASS]


def test_tbe_06_over_budget_is_fail_not_insufficient_data(tmp_path):
    """B-6 / SPEC-002 V-3. Every input is known: the sealed budget, the
    trial timestamps, the (absent) increments. INSUFFICIENT-DATA is for a
    quantity that cannot be established; this one is established and it
    is not met. The distinction is not cosmetic — INSUFFICIENT-DATA
    invites 'supply the missing input and re-run', which is exactly the
    wrong instruction for a family that has already over-spent."""
    reg = _reg(tmp_path)
    _open(reg, "F", 2)
    _log(reg, "F", 9)
    assert _row(_evaluate(reg, "F")).verdict == FAIL


# ======================================================================
# B-9, B-12 — the authorization edge is PROSPECTIVE
# ======================================================================

def test_tbe_07_countersigned_extension_raises_the_budget(tmp_path):
    """B-13/B-14/B-10. The edge exists and works: a well-formed,
    countersigned extension logged BEFORE the trials it authorizes raises
    the effective budget, and the row says so."""
    reg = _reg(tmp_path)
    _open(reg, "F", 5)
    _log(reg, "F", 5)
    eid = _extension(reg, "F", **_discretionary(3, n_logged_at_issue=5))
    _countersign(reg, "F", eid, "quant-validation")
    _log(reg, "F", 3, seed0=500)

    rep = _evaluate(reg, "F")
    assert _row(rep).verdict == PASS
    assert _effective_budget(rep) == 8
    assert _sealed_budget(rep) == 5


def test_tbe_08_extension_logged_after_the_overspend_authorizes_nothing(tmp_path):
    """B-9 — THE SINGLE MOST IMPORTANT CLAUSE IN THE SPECIFICATION.

    Budget 5, eight trials logged, THEN a +5 extension. The aggregate
    test reads 8 <= 10 and PASSES. The per-trial walk reads trial 6 as
    logged when the effective budget was 5 and FAILS.

    An aggregate comparison legalises spend-first-authorize-after, which
    is not a budget at all — it is a receipt.
    """
    reg = _reg(tmp_path)
    _open(reg, "F", 5)
    _log(reg, "F", 8)
    eid = _extension(reg, "F", **_discretionary(5, n_logged_at_issue=8))
    _countersign(reg, "F", eid, "quant-validation")

    row = _row(_evaluate(reg, "F"))
    assert row.verdict == FAIL, (
        "B-9 VIOLATED: an extension logged AFTER the overspend was "
        "allowed to authorize it retrospectively.")
    assert "OVER BUDGET" in row.note
    assert "trial 6" in row.note, (
        "B-11: the note must name the FIRST violating trial index, which "
        "is when authorization ran out — not the size of the overage. "
        f"Got: {row.note!r}")


def test_tbe_09_a_dated_field_in_detail_is_never_read_for_ordering(tmp_path):
    """B-9 / section 7.1, the back-dating answer.

    `TrialRegistry.log_event` writes `created_utc` from the system clock
    and the API has no parameter for it. Any `issued_utc` / `as_of` /
    `dated` claim inside `detail` is exactly that — a claim — and the
    criterion must never read it for ordering. Here the event claims to
    have been issued in 1971 and is logged after the overspend.
    """
    reg = _reg(tmp_path)
    _open(reg, "F", 5)
    _log(reg, "F", 8)
    eid = _extension(reg, "F", **{
        **_discretionary(5, n_logged_at_issue=8),
        "issued_utc": 0.0, "as_of": "1971-01-01", "dated": "1971-01-01",
    })
    _countersign(reg, "F", eid, "quant-validation")
    assert _row(_evaluate(reg, "F")).verdict == FAIL


def test_tbe_10_uncountersigned_or_self_countersigned_extension_is_refused(tmp_path):
    """B-14. Three refusals, one property: a single seat acting alone
    inside its own scope cannot move its own budget.

    The harness cannot authenticate anyone (I-103), so this controls
    drift, not fraud, and the specification says so rather than implying
    a strength it does not have.
    """
    # (a) no countersignature at all
    reg = _reg(tmp_path, "a.db")
    _open(reg, "F", 5)
    _log(reg, "F", 5)
    _extension(reg, "F", **_discretionary(3, n_logged_at_issue=5))
    _log(reg, "F", 3, seed0=500)
    rep = _evaluate(reg, "F")
    assert _row(rep).verdict == FAIL
    assert _effective_budget(rep) == 5

    # (b) countersigned by the issuer itself
    reg = _reg(tmp_path, "b.db")
    _open(reg, "F", 5)
    _log(reg, "F", 5)
    eid = _extension(reg, "F", **_discretionary(
        3, issuer="director-of-research", n_logged_at_issue=5))
    _countersign(reg, "F", eid, "director-of-research")
    _log(reg, "F", 3, seed0=500)
    rep = _evaluate(reg, "F")
    assert _row(rep).verdict == FAIL
    assert _effective_budget(rep) == 5

    # (c) countersigned by a seat outside the allow-list
    reg = _reg(tmp_path, "c.db")
    _open(reg, "F", 5)
    _log(reg, "F", 5)
    eid = _extension(reg, "F", **_discretionary(3, n_logged_at_issue=5))
    _countersign(reg, "F", eid, "pm-digital-markets")
    _log(reg, "F", 3, seed0=500)
    rep = _evaluate(reg, "F")
    assert _row(rep).verdict == FAIL
    assert _effective_budget(rep) == 5


def test_tbe_11_principal_issues_alone(tmp_path):
    """B-15. The Principal's authority is final (Charter section 4) and
    the logged event IS the permanent override record the Charter
    requires. No countersignature."""
    reg = _reg(tmp_path)
    _open(reg, "F", 5)
    _log(reg, "F", 5)
    _extension(reg, "F", **_discretionary(
        4, issuer="principal", n_logged_at_issue=5,
        ref="logs/DECISION_RECORD.md"))
    _log(reg, "F", 4, seed0=500)
    rep = _evaluate(reg, "F")
    assert _row(rep).verdict == PASS
    assert _effective_budget(rep) == 9


# ======================================================================
# B-23, B-24, B-26 — malformation and its documented repair
# ======================================================================

@pytest.mark.parametrize("bad,why", [
    ({"mode": "APPROVED"}, "mode outside the two-value vocabulary"),
    ({"increment": 0}, "increment must be > 0"),
    ({"increment": -3}, "negative increment"),
    ({"increment": 2.5}, "float increment is malformed, not truncated"),
    ({"increment": True}, "a bool is not an int here (H-2's precedent)"),
    ({"issuer": ""}, "empty issuer"),
    ({"reason": "   "}, "blank reason"),
    ({"authorization_ref": ""}, "no written artifact named"),
    ({"n_logged_at_issue": 99}, "B-21 cross-check: declared count is a lie"),
])
def test_tbe_12_malformed_extension_fails_even_inside_budget(tmp_path, bad, why):
    """B-23 + B-4's tie-break rule.

    The family is comfortably INSIDE its sealed budget in every case
    below. It still FAILs, because a malformed authorization artifact in
    the registry is an attempted authorization the harness could not
    verify, and this firm's answer to an unverifiable authorization is
    refusal, not tolerance.

    The rule is deliberately absolute. "It was only a typo and the family
    didn't need it anyway" is the exact sentence under which a tolerance
    gets established.
    """
    reg = _reg(tmp_path, re.sub(r"\W+", "_", str(bad)) + ".db")
    _open(reg, "F", 50)
    _log(reg, "F", 2)
    detail = {**_discretionary(3, n_logged_at_issue=2), **bad}
    eid = _extension(reg, "F", **detail)
    _countersign(reg, "F", eid, "quant-validation")

    row = _row(_evaluate(reg, "F"))
    assert row.verdict == FAIL, f"B-23 VIOLATED for: {why}"
    assert "MALFORMED AUTHORIZATION" in row.note
    assert str(eid) in row.note, (
        "B-23: the note must name the offending event_id — a malformation "
        "a reader cannot locate is a malformation nobody repairs.")


def test_tbe_13_withdrawal_neutralises_a_malformed_event(tmp_path):
    """B-24. The registry is append-only; nothing is deleted; the error
    and its repair are both permanently on the record.

    Also asserts the second half of B-24: a withdrawal naming an unknown
    event_id could only ever fail to tighten, so under B-4 it is
    disclosed and does NOT fail the Gate.
    """
    reg = _reg(tmp_path, "w.db")
    _open(reg, "F", 50)
    _log(reg, "F", 2)
    eid = _extension(reg, "F", **{**_discretionary(3, n_logged_at_issue=2),
                                  "increment": 0})
    assert _row(_evaluate(reg, "F")).verdict == FAIL

    reg.log_event("trial_budget_extension_withdrawn", "F",
                  {"extension_event_id": eid, "reason": "typo"})
    rep = _evaluate(reg, "F")
    assert _row(rep).verdict == PASS, (
        "B-24 VIOLATED: a withdrawn malformed event must be inert.")
    assert _effective_budget(rep) == 50

    # a withdrawal pointing at nothing can only tighten -> disclosed, not FAIL
    reg.log_event("trial_budget_extension_withdrawn", "F",
                  {"extension_event_id": 999_999, "reason": "fat finger"})
    assert _row(_evaluate(reg, "F")).verdict == PASS


def test_tbe_14_contingent_extension_is_recomputed_not_trusted(tmp_path):
    """B-16/B-19. The stage lock's load-bearing property.

    A CONTINGENT extension needs no countersignature and may be
    self-issued, because the authorization is a computation the criterion
    performs at evaluation time and NEVER the event's own assertion that
    the condition held. Forging the event buys nothing.

    Fixture: sealed budget 5, eight own trials, a self-issued contingent
    extension of +10 declaring the unlock. The family's own measured
    N_max at evaluation time is 2 — far below the declared ceiling base
    of 5 — so the admitted increment is 0 and the family is over its
    proven budget.
    """
    reg = _reg(tmp_path, "c1.db")
    _open(reg, "F", 5)
    _log(reg, "F", 5)
    _extension(reg, "F", **_contingent(10, n_logged_at_issue=5))
    _log(reg, "F", 3, seed0=500)

    rep = _evaluate(reg, "F")
    # fixture guards — RULING 005 section 1's lesson: assert the fixture
    # is the object you think it is, before grading it.
    assert rep.n_max_admissible_iid is not None, (
        "fixture: N_max must be COMPUTABLE here, so this test grades the "
        "recomputation branch and not the unevaluable branch")
    n_max = min(rep.n_max_admissible_iid, rep.n_max_admissible_serial)
    assert n_max <= 5, f"fixture: N_max must not admit the ceiling, got {n_max}"

    assert _row(rep).verdict == FAIL, (
        "B-16 VIOLATED: the criterion trusted the event's claim instead "
        "of recomputing the predicate.")
    assert _effective_budget(rep) == 5

    # B-19: where N_max cannot be computed at all (no oos_index), the
    # increment is 0 and the verdict is FAIL — not INSUFFICIENT-DATA.
    # The predicate is unestablished; the budget is established; the
    # family exceeded the budget it can prove.
    rep2 = _evaluate(reg, "F", with_index=False)
    assert _row(rep2).verdict == FAIL
    assert _effective_budget(rep2) == 5


def test_tbe_15_contingent_increment_reproduces_prereg002_table():
    """B-18/B-20/B-28, graded as a pure function so the arithmetic is
    pinned independently of any Gate fixture.

    The four rows are PREREG-002 section 10.5.2's OWN unlock table, and
    the point of reproducing them is section 7.3's claim: the general
    mechanism reproduces the specific document's table WITHOUT KNOWING
    THE DOCUMENT EXISTS. Base = n_inherited 7 + Stage 1 budget 47 = 54;
    declared Stage 2 increment 32; N_max from SPEC-002 section 6.2.
    """
    fn = getattr(gates, "contingent_increment_allowed", None)
    if fn is None:
        pytest.fail(
            "NOT IMPLEMENTED: gates.contingent_increment_allowed does not "
            "exist. Required by VALIDATION-SPEC-003 B-28 — B-18's "
            "arithmetic must be unit-testable without a Gate fixture.")

    base, inc = 54, 32
    assert fn(86, base, inc) == 32, "rho_hat <= 0.034 -> the whole of Stage 2"
    assert fn(77, base, inc) == 23, "rho_hat ~ 0.05 -> 23 of the 32"
    assert fn(55, base, inc) == 1, "rho_hat ~ 0.10 -> 1 of the 32"
    assert fn(31, base, inc) == 0, "rho_hat >= 0.20 -> none"

    # B-19: unevaluable N_max is zero, never a permissive default.
    assert fn(None, base, inc) == 0

    # B-18's clamp is two-sided: the cap never exceeds what was declared.
    assert fn(10_000, base, inc) == 32
    # and never goes negative.
    assert fn(0, base, inc) == 0


def test_tbe_16_unknown_predicate_and_nonempty_params_are_malformed(tmp_path):
    """B-17. The vocabulary is CLOSED and has exactly one member at v1.

    An open vocabulary puts a narrated condition inside the firm's
    most-protected criterion, which is I-014's shape — the caller-asserted
    `holdout_opened_once` boolean, removed rather than deprecated.
    Neither an unknown predicate name nor a non-empty `params` degrades to
    a permissive default; both are malformed and both route to Validation.
    """
    for bad, why in (
        (dict(name="director_says_so"), "unknown predicate name"),
        (dict(name="n_max_admits_declared_ceiling",
              params={"n_max": 10_000}), "sponsor-supplied params"),
    ):
        reg = _reg(tmp_path, re.sub(r"\W+", "_", why) + ".db")
        _open(reg, "F", 50)
        _log(reg, "F", 2)
        _extension(reg, "F", **_contingent(
            10, n_logged_at_issue=2, **bad))
        row = _row(_evaluate(reg, "F"))
        assert row.verdict == FAIL, f"B-17 VIOLATED: {why}"
        assert "MALFORMED AUTHORIZATION" in row.note


# ======================================================================
# B-22, B-1 — genericity, and what the budget actually grades
# ======================================================================

def test_tbe_17_criterion_is_generic_and_reads_no_single_documents_fields():
    """B-22. A criterion that only understands one document is a
    criterion that silently passes every other, and that failure mode is
    invisible until the second document arrives.

    Bare integer literals are deliberately NOT banned: `gates.py`
    legitimately holds `32.0` as the breakeven bisection's upper bracket,
    and a test that cannot distinguish that from a smuggled budget
    constant is a test that gets deleted the first time it fires.
    """
    src = inspect.getsource(gates).lower()
    for token in ("prereg-002", "prereg_002", "prereg002", "rho_plan",
                  "0.034", "stage_2", "crypto-funding", "funding-basis"):
        assert token not in src, (
            f"B-22 VIOLATED: gates.py contains {token!r}. The criterion "
            "has been fitted to one pre-registration.")

    params = set(inspect.signature(evaluate_gate1).parameters)
    for forbidden in ("trial_budget", "budget", "budget_extension",
                      "trial_budget_extension", "budget_override",
                      "authorized_trials", "stage", "budget_stage"):
        assert forbidden not in params, (
            f"B-22 / Acceptance 001 C-6 VIOLATED: evaluate_gate1 gained a "
            f"{forbidden!r} parameter. An authorization the CALLER supplies "
            "is a narrated authorization, which is precisely what removing "
            "`holdout_opened_once` established this firm does not accept.")


def test_tbe_18_predecessor_chain_spend_is_not_charged_to_the_successor(tmp_path):
    """B-1 / I-101. The comparison quantity was never specified and the
    existing code picks the wrong one.

    `fam.n_logged` is chain-summed transitively. Under a WORKING
    criterion that would make every successor whose chain out-spends its
    own budget over budget with zero acts of its own — turning
    `predecessor_family`, an anti-gaming declaration, into a penalty for
    making it. The chain's spend is priced where it belongs, in N, which
    reaches MinBTL and DSR transitively already.

    The residual (a sponsor chaining successors for fresh budgets) is not
    capped here; B-25 requires it VISIBLE on every report instead.
    """
    reg = _reg(tmp_path)
    _open(reg, "P", 40)
    _log(reg, "P", 40)
    _open(reg, "S", 5, predecessor="P")
    _log(reg, "S", 3, seed0=900)

    rep = _evaluate(reg, "S")
    assert reg.family_stats("S").n_logged == 43, "fixture: chain sums to 43"
    row = _row(rep)
    assert row.verdict == PASS, (
        "B-1 VIOLATED: the successor was charged its predecessor's spend "
        f"and read {row.verdict!r} having logged 3 trials against 5.")
    assert _effective_budget(rep) == 5
    assert "chain-summed logged 43" in row.note, (
        "B-25: where the chain total differs from the graded own-family "
        "count, the report must carry it — the serial-successor pattern is "
        f"disclosed on every report, not tracked in a memo. Got: {row.note!r}")


def test_tbe_19_unknown_event_kinds_and_narrated_kwargs_cannot_authorize(tmp_path):
    """B-4 / Acceptance 001 C-6. There is no third route past the budget.

    An event kind the criterion does not recognise authorizes nothing and
    is inert — including one whose name is designed to read like an
    approval. This is the grandfather clause probe: B-30 says a family
    over budget when the fix lands is retroactively FAIL, and there is no
    event, flag or kwarg that buys it out.
    """
    reg = _reg(tmp_path)
    _open(reg, "F", 5)
    _log(reg, "F", 9)
    for kind in ("budget_grandfathered",
                 "trial_budget_extension_approved_verbally",
                 "trial_budget_waived",
                 "gate1_verdict",
                 "hypothesis_registered"):
        reg.log_event(kind, "F", {"increment": 100, "issuer": "principal",
                                  "mode": "DISCRETIONARY"})
    rep = _evaluate(reg, "F")
    assert _row(rep).verdict == FAIL
    assert _effective_budget(rep) == 5
