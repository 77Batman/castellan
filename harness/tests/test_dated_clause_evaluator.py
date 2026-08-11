"""Acceptance tests for VALIDATION-SPEC-004 Item 2 (clauses E-1 ... E-25) —
the dated-clause evaluator. Scope widened twice by ruling: not kill
conditions alone, but EVERY dated clause — kill conditions, condition
precedents, observation dates, deadlines of any kind.

Authored by the Head of Quantitative Validation BEFORE implementation.

THE PROPERTY THESE TESTS ARE:

    Every dated clause in a registered family is checked against its
    premise on every invocation, regardless of whom the staleness serves,
    and a clause nothing can evaluate exits nonzero rather than passing
    quietly.

Today no harness path evaluates a dated clause on any date for any family
(I-135, standing). The Director's sweep of PREREG-002 measured the
consequence: 24 dated clauses, 2 evaluated by code, 3 class (b) with a
named executor, and NINETEEN evaluated by a reader noticing.

DIRECTION-BLINDNESS IS THE HARD REQUIREMENT AND IT IS WHY THIS FILE
CARRIES MIRROR PAIRS. The sweep found 15 of 24 clauses carrying false
premises, and the one stale figure that ran FOR the family — section
11.1's 6.571-year span, understated at every later C — survived four
revision passes. Stale dates that cost the firm get found; stale dates
that favour it survive. A checker a sponsor would be RELIEVED to see pass
is not direction-blind. `test_dce_20` and `test_dce_21` are the clauses
that make that structural rather than aspirational.

SEAT 9 DOES NOT MODIFY ANY TEST IN THIS FILE UNDER ANY CIRCUMSTANCES.
A failure here is escalated to Validation in writing (Ruling 004 section
11's standing term), which binds the author as hard as the implementer.

RED BY DESIGN.
"""

from __future__ import annotations

import contextlib
import importlib
import inspect
import re

import pytest

from castellan import TrialRegistry


# ---------------------------------------------------------------------------
# helpers — a missing name is a clean FAIL, never a collection ERROR.
# ---------------------------------------------------------------------------

def _module():
    try:
        return importlib.import_module("castellan.dated_clauses")
    except ImportError:  # pragma: no cover - the red path
        pytest.fail(
            "castellan.dated_clauses does not exist yet — "
            "VALIDATION-SPEC-004 Item 2 is unimplemented. RED BY DESIGN."
        )


def _need(module, name: str):
    obj = getattr(module, name, None)
    assert obj is not None, (
        f"{module.__name__}.{name} does not exist yet — "
        "VALIDATION-SPEC-004 Item 2 is unimplemented. RED BY DESIGN."
    )
    return obj


@contextlib.contextmanager
def _writable(reg, reason="REGISTER_HYPOTHESIS"):
    """Item 1's grant if it exists, a no-op if it does not. Item 2's red
    state must be red for Item 2's reasons, not for Item 1's."""
    wg = getattr(reg, "write_grant", None)
    if wg is None:
        yield
        return
    with wg(reason=reason, dispatch="TEST", token="test-token"):
        yield


HYP = dict(
    statement="s", mechanism="m", falsifier="f", universe="u",
    horizon="h", success_criteria="sc", trial_budget=10,
)


def _build(tmp_path, spec: dict, name="reg.db"):
    """Register one family from a fixture spec and return (registry, family)."""
    reg = TrialRegistry(str(tmp_path / name))
    fields = dict(HYP)
    fields.update(spec.get("fields", {}))
    with _writable(reg):
        reg.open_hypothesis(family="famA", **fields)
        add = _need(reg, "register_dated_clause")
        for c in spec.get("clauses", []):
            add(family="famA", **c)
        for kind, when in spec.get("events", []):
            reg.log_event(kind, "famA", {"at": when})
    return reg, "famA"


def _run(reg, family, as_of=None):
    ev = _need(_module(), "evaluate_dated_clauses")
    return ev(reg, family=family, as_of=as_of)


def _verdicts(rep):
    return sorted(f.verdict for f in rep.findings)


# ---------------------------------------------------------------------------
# THE MIRROR-PAIR FIXTURE SET · E-20
# Every *_against has a *_for of identical magnitude running the other way.
# ---------------------------------------------------------------------------

def fx_divergence_against():
    """I-153 exactly. The clause is registered as the formula the field's own
    opening sentence says governs; the field carries a literal that resolves
    LATER than the formula does — the direction that TERMINATES the family."""
    return {
        "fields": {
            "forward_window_start": "2026-08-12",
            "forward_kill_condition": (
                "Observation date = C + 187 days. SILENCE IS A KILL - if the "
                "computation is not performed on 2027-01-31 for ANY reason "
                "the family is killed by default."
            ),
        },
        "clauses": [dict(
            tag="KC-002 clause 5", field="forward_kill_condition",
            source_offset=95, kind="OBSERVATION",
            date_expr="C + 187 days", discharge_event_kind="",
        )],
        "as_of": "2026-08-12",
        "expect": "DIVERGENT", "exit": 3,
    }


def fx_divergence_for():
    """The same magnitude of divergence running the OTHER way: the literal
    resolves LATER than the formula, buying the family more time. A sponsor
    would be relieved to see this one pass. It must not."""
    return {
        "fields": {
            "forward_window_start": "2026-08-12",
            "forward_kill_condition": (
                "Observation date = C + 187 days. SILENCE IS A KILL - if the "
                "computation is not performed on 2027-08-31 for ANY reason "
                "the family is killed by default."
            ),
        },
        "clauses": [dict(
            tag="KC-002 clause 5", field="forward_kill_condition",
            source_offset=95, kind="OBSERVATION",
            date_expr="C + 187 days", discharge_event_kind="",
        )],
        "as_of": "2026-08-12",
        "expect": "DIVERGENT", "exit": 3,
    }


def fx_span_against():
    """A stated span LONGER than its interval computes — an overstatement,
    which flatters MinBTL, DSR and the length criterion."""
    return {
        "fields": {
            "forward_window_start": "2026-07-28",
            "success_criteria": "In-sample [2020-01-01, C] = 8.900 years.",
        },
        "clauses": [], "as_of": "2026-08-12",
        "expect": "SPAN-DIVERGENT", "exit": 3,
    }


def fx_span_for():
    """PREREG-002 section 11.1 ITSELF: [2020-01-01, C] stated as 6.571
    years, measured to 2026-07-28 and UNDERSTATED at any later C.

    THIS IS THE PROOF CASE FOR DIRECTION-BLINDNESS. It is the one stale
    figure in the whole sweep that ran FOR the family, and it is exactly
    why it survived four revision passes. It must return the same verdict
    and the same exit code as its overstating mirror."""
    return {
        "fields": {
            "forward_window_start": "2030-01-01",
            "success_criteria": "In-sample [2020-01-01, C] = 6.571 years.",
        },
        "clauses": [], "as_of": "2030-01-02",
        "expect": "SPAN-DIVERGENT", "exit": 3,
    }


def fx_anchor_against():
    """forward_window_start's literal predates the seal — the sweep's D-8.
    A window that started before the family existed."""
    return {
        "fields": {"forward_window_start": "2020-01-01"},
        "clauses": [], "as_of": "2026-08-12",
        "expect": "ANCHOR-STALE", "exit": 3,
    }


def fx_anchor_for():
    """The same staleness running the other way: a start date AFTER the
    seal, which shortens nothing and delays every deadline in the family's
    favour. Same verdict, same exit code."""
    return {
        "fields": {"forward_window_start": "2099-01-01"},
        "clauses": [], "as_of": "2026-08-12",
        "expect": "ANCHOR-STALE", "exit": 3,
    }


# ---------------------------------------------------------------------------
# E-1 ... E-4 — what is read, and where the anchor comes from
# ---------------------------------------------------------------------------

def test_dce_01_every_registered_field_is_scanned(tmp_path):
    """E-1. The field list is enumerated, not sampled. A date buried in
    `mechanism` is found, because a sponsor does not choose which field a
    dated clause lands in."""
    reg, fam = _build(tmp_path, {"fields": {
        "mechanism": "Funding inverts after 2027-01-31 by assumption.",
        "forward_window_start": "2026-08-12",
    }})
    rep = _run(reg, fam, as_of="2026-08-12")
    assert any(f.field == "mechanism" for f in rep.findings), (
        "E-1: `mechanism` is in scope"
    )


def test_dce_02_three_recognizers_find_sites_at_correct_offsets(tmp_path):
    """E-2 / E-3. Extraction is by literal form, never by meaning. No
    natural-language understanding is attempted anywhere: a checker that
    decides what a sentence MEANS produces findings a sponsor negotiates."""
    mod = _module()
    extract = _need(mod, "extract_clause_sites")
    text = "Window [2020-01-01, C] = 6.571 years; observe at C + 187 days."
    sites = extract("success_criteria", text)
    kinds = {s.recognizer for s in sites}
    assert {"ISO", "FORMULA", "SPAN"} <= kinds
    for s in sites:
        assert text[s.source_offset:s.source_offset + len(s.matched_text)] == s.matched_text


def test_dce_03_anchor_is_read_never_inferred(tmp_path):
    """E-4. C is forward_window_start, else the seal event's UTC date. It is
    never re-derived from prose, never taken from a parenthesis, and never
    defaulted to today — the parenthesis is precisely where PREREG-002's
    false premise lived."""
    reg, fam = _build(tmp_path, {"fields": {
        "forward_window_start": "2026-08-12",
        "horizon": "(drafted against an intended C = 2026-07-28)",
    }})
    rep = _run(reg, fam, as_of="2026-08-12")
    assert str(rep.anchor_C) .startswith("2026-08-12"), (
        "E-4: the parenthesised 2026-07-28 must not become C"
    )


def test_dce_04_an_unanchored_family_cannot_be_evaluated(tmp_path):
    """E-4. UNANCHORED is an inability verdict and exits 4."""
    reg = TrialRegistry(str(tmp_path / "reg.db"))
    with _writable(reg):
        f = dict(HYP)
        f["success_criteria"] = "Observe at C + 187 days."
        reg.open_hypothesis(family="famA", **f)
        reg.conn.execute("DELETE FROM events WHERE kind='hypothesis_sealed'")
    rep = _run(reg, "famA", as_of="2026-08-12")
    assert "UNANCHORED" in _verdicts(rep)
    assert rep.exit_code == 4


# ---------------------------------------------------------------------------
# E-6 — coverage. The clause that converts "19 of 24 evaluated by nothing"
# from an audit finding into a run that fails.
# ---------------------------------------------------------------------------

def test_dce_05_an_unclaimed_site_is_uncovered_and_exits_4(tmp_path):
    """E-6. The evaluator does not decide that an unclaimed date is
    harmless. It declines to evaluate it and says so with a nonzero exit.
    The sponsor's only routes are to structure the clause or strike it —
    both pre-seal, both cheap, both visible."""
    reg, fam = _build(tmp_path, {"fields": {
        "forward_window_start": "2026-08-12",
        "success_criteria": "KC-002 survival is evaluated at 2027-01-31.",
    }})
    rep = _run(reg, fam, as_of="2026-08-12")
    assert "UNCOVERED" in _verdicts(rep)
    assert rep.exit_code == 4


def test_dce_06_double_claim_is_ambiguous_and_a_phantom_claim_dangles(tmp_path):
    """E-6. Both are inability, not a tie-break the evaluator resolves."""
    clause = dict(
        tag="t", field="success_criteria", source_offset=4,
        kind="DEADLINE", date_expr="2027-01-31",
        discharge_event_kind="kc_evaluated",
    )
    reg, fam = _build(tmp_path, {
        "fields": {"forward_window_start": "2026-08-12",
                   "success_criteria": "at 2027-01-31 exactly"},
        "clauses": [clause, dict(clause, tag="t2"),
                    dict(clause, tag="t3", source_offset=999)],
    })
    rep = _run(reg, fam, as_of="2026-08-12")
    v = _verdicts(rep)
    assert "AMBIGUOUS" in v and "DANGLING" in v
    assert rep.exit_code == 4


# ---------------------------------------------------------------------------
# E-7 / E-8 / E-10 / E-11 — resolution, staleness, firing
# ---------------------------------------------------------------------------

def test_dce_07_formula_resolution_is_exact(tmp_path):
    """E-7. Day units are exact; month units clamp at end-of-month. Stated
    so two implementations cannot disagree."""
    resolve = _need(_module(), "resolve_date_expr")
    import pandas as pd
    C = pd.Timestamp("2026-08-12", tz="UTC")
    assert resolve("C + 187 days", C).date().isoformat() == "2027-02-15"
    assert resolve("2027-01-31", C).date().isoformat() == "2027-01-31"
    assert resolve("C + 6 months", pd.Timestamp("2026-08-31", tz="UTC")) \
        .date().isoformat() == "2027-02-28"


def test_dce_08_anchor_staleness_is_reported(tmp_path):
    """E-8. The sweep's D-8: `forward_window_start = 2026-07-28 (= C; the
    seal is intended for today)`, false since 2026-08-04, carried through
    four revisions and named by a revision row that never reached it."""
    reg, fam = _build(tmp_path, fx_anchor_against())
    rep = _run(reg, fam, as_of="2026-08-12")
    assert "ANCHOR-STALE" in _verdicts(rep)


def test_dce_09_a_past_date_with_no_discharge_fires(tmp_path):
    """E-10. Exit 2."""
    reg, fam = _build(tmp_path, {
        "fields": {"forward_window_start": "2026-01-01",
                   "success_criteria": "Evaluate KC-002 at 2026-03-01."},
        "clauses": [dict(tag="kc", field="success_criteria", source_offset=21,
                         kind="OBSERVATION", date_expr="2026-03-01",
                         discharge_event_kind="kc_evaluated")],
    })
    rep = _run(reg, fam, as_of="2026-08-12")
    assert "FIRED" in _verdicts(rep)
    assert rep.exit_code == 2


def test_dce_10_a_discharge_event_on_time_clears_the_clause(tmp_path):
    """E-10. Exit 0 — the only route to zero."""
    reg, fam = _build(tmp_path, {
        "fields": {"forward_window_start": "2026-01-01",
                   "success_criteria": "Evaluate KC-002 at 2026-03-01."},
        "clauses": [dict(tag="kc", field="success_criteria", source_offset=21,
                         kind="OBSERVATION", date_expr="2026-03-01",
                         discharge_event_kind="kc_evaluated")],
        "events": [("kc_evaluated", "2026-02-20")],
    })
    rep = _run(reg, fam, as_of="2026-08-12")
    assert _verdicts(rep) == ["DISCHARGED"]
    assert rep.exit_code == 0


def test_dce_11_a_late_discharge_still_fires(tmp_path):
    """E-10. The event must exist at or before the resolved date. A clause
    discharged afterwards was not discharged; it was noticed."""
    reg, fam = _build(tmp_path, {
        "fields": {"forward_window_start": "2026-01-01",
                   "success_criteria": "Evaluate KC-002 at 2026-03-01."},
        "clauses": [dict(tag="kc", field="success_criteria", source_offset=21,
                         kind="OBSERVATION", date_expr="2026-03-01",
                         discharge_event_kind="kc_evaluated")],
    })
    with _writable(reg, reason="LOG_EVENT"):
        reg.log_event("kc_evaluated", "famA", {"late": True})
    rep = _run(reg, fam, as_of="2026-08-12")
    assert "FIRED" in _verdicts(rep)


def test_dce_12_silence_is_a_kill_is_a_registration_act(tmp_path):
    """E-11. An empty discharge_event_kind means nothing can discharge the
    clause, and it fires on its date, every invocation, forever — which is
    what the clause says it does. It is registrable, but registering it
    means writing '' into a sealed column deliberately, rather than leaving
    a sentence inside a paragraph inside a hashed string."""
    reg, fam = _build(tmp_path, {
        "fields": {"forward_window_start": "2026-01-01",
                   "success_criteria": "SILENCE IS A KILL at 2026-03-01."},
        "clauses": [dict(tag="kc5", field="success_criteria", source_offset=25,
                         kind="OBSERVATION", date_expr="2026-03-01",
                         discharge_event_kind="")],
        "events": [("kc_evaluated", "2026-02-01")],
    })
    rep = _run(reg, fam, as_of="2026-08-12")
    assert "FIRED" in _verdicts(rep)


# ---------------------------------------------------------------------------
# E-12 / E-13 / E-14 — formula-versus-literal divergence. I-153's class.
# ---------------------------------------------------------------------------

def test_dce_13_i153_formula_versus_literal_divergence(tmp_path):
    """E-12. I-153 reproduced. `date_expr = C + 187 days`, literal
    2027-01-31 in the same hashed field, C = 2026-08-12. The two disagree,
    the site is DIVERGENT, exit 3 — on the first invocation after
    registration, which under E-24 is before any Gate 1 verdict can read
    anything else."""
    reg, fam = _build(tmp_path, fx_divergence_against())
    rep = _run(reg, fam, as_of="2026-08-12")
    assert "DIVERGENT" in _verdicts(rep)
    assert rep.exit_code == 3


def test_dce_14_a_prose_disclaimer_is_not_a_reconciliation(tmp_path):
    """E-13. THE CLAUSE THAT MATTERS MOST IN THIS FILE.

    PREREG-002's field carried, verbatim, `the DRAFTED DATE IS NOT BINDING
    - the formula is`, and clause 5 fired anyway. The sentence told a
    reader which value to prefer; it did not remove the other value from a
    hashed string, and a hashed string is what gets sealed.

    Only equal values cure a divergence. The evaluator must have no code
    path that reads a governing-clause declaration — which is what makes
    this enforced rather than promised."""
    spec = fx_divergence_against()
    spec["fields"]["forward_kill_condition"] = (
        "Observation date = C + 187 days (drafted against an intended "
        "C = 2026-07-28, giving 2027-01-31; the DRAFTED DATE IS NOT "
        "BINDING - THE FORMULA IS). SILENCE IS A KILL - if the computation "
        "is not performed on 2027-01-31 the family is killed by default."
    )
    spec["clauses"][0]["source_offset"] = spec["fields"][
        "forward_kill_condition"].index("2027-01-31")
    reg, fam = _build(tmp_path, spec)
    rep = _run(reg, fam, as_of="2026-08-12")
    assert "DIVERGENT" in _verdicts(rep), (
        "E-13: a governing-clause disclaimer does not cure divergence"
    )
    assert rep.exit_code == 3


def test_dce_15_intra_field_contradiction_is_reported_at_both_offsets(tmp_path):
    """E-14. The sweep's D-4 against D-5/D-6/D-7: three literals
    contradicting the opening of the same string."""
    reg, fam = _build(tmp_path, fx_divergence_against())
    rep = _run(reg, fam, as_of="2026-08-12")
    div = [f for f in rep.findings
           if f.field == "forward_kill_condition" and f.verdict == "DIVERGENT"]
    assert len({f.source_offset for f in div}) >= 2, (
        "E-14: both the formula site and the literal site are reported"
    )


# ---------------------------------------------------------------------------
# E-16 ... E-21 — DIRECTION-BLINDNESS, ENFORCED RATHER THAN INTENDED
# ---------------------------------------------------------------------------

def test_dce_16_the_verdict_vocabulary_has_no_favourable_member(tmp_path):
    """E-16. There is no field anywhere in the finding record in which a
    direction could be written, so there is no field a later reader could
    filter on."""
    vocab = set(_need(_module(), "VERDICTS"))
    assert vocab == {
        "PENDING", "DISCHARGED", "FIRED", "DIVERGENT", "SPAN-DIVERGENT",
        "ANCHOR-STALE", "UNCOVERED", "AMBIGUOUS", "DANGLING", "UNANCHORED",
    }
    for banned in ("OK", "WAIVED", "SUPPRESSED", "BENIGN", "IN-FAVOUR"):
        assert banned not in vocab


def test_dce_17_no_suppression_parameter_exists_anywhere(tmp_path):
    """E-17. THE CLAUSE THAT MAKES E-16 HOLD UNDER MAINTENANCE PRESSURE.

    The natural first request after this lands will be a way to silence one
    finding, and it will arrive with a good reason. The answer is that the
    DOCUMENT changes, not the checker's configuration — and this test
    refuses the alternative before the conversation happens."""
    mod = _module()
    banned = re.compile(
        r"(?i)ignore|skip|allow|waive|suppress|exempt|except|only|severity|priority"
    )
    checked = 0
    for name, fn in inspect.getmembers(mod, inspect.isfunction):
        if name.startswith("_") or fn.__module__ != mod.__name__:
            continue
        checked += 1
        for p in inspect.signature(fn).parameters:
            assert not banned.search(p), (
                f"E-17: {mod.__name__}.{name} takes a suppression-shaped "
                f"parameter {p!r}. No parameter, anywhere in this module, "
                "may be capable of silencing a finding."
            )
    assert checked > 0


def test_dce_18_findings_carry_no_severity_or_priority(tmp_path):
    """E-18. One consequence class. A finding cannot be de-prioritized
    because there is no priority to set."""
    reg, fam = _build(tmp_path, fx_divergence_against())
    rep = _run(reg, fam, as_of="2026-08-12")
    for f in rep.findings:
        fields = set(getattr(f, "__dataclass_fields__", {})) or set(vars(f))
        assert not {"severity", "priority", "rank", "weight"} & fields


def test_dce_19_report_order_is_offset_order_never_verdict_order(tmp_path):
    """E-19. The shape of the report encodes nothing about direction or
    severity, so a reader skimming the top is not being shown the
    sponsor-relevant findings first."""
    spec = {
        "fields": {
            "forward_window_start": "2026-08-12",
            "success_criteria": "at 2027-01-31 and also [2020-01-01, C] = 9.9 years",
            "mechanism": "and again 2028-05-05",
        },
        "clauses": [],
    }
    reg, fam = _build(tmp_path, spec)
    rep = _run(reg, fam, as_of="2026-08-12")
    keys = [(f.field, f.source_offset) for f in rep.findings]
    assert keys == sorted(keys), "E-19: sorted by (field, source_offset)"


MIRROR_PAIRS = ["divergence", "span", "anchor"]


def test_dce_20_mirror_pairing_is_total_and_enforced_at_collection(tmp_path):
    """E-20. Every fixture whose divergence runs AGAINST the family has an
    arithmetic mirror of the same magnitude running FOR it. A fixture added
    without its mirror is a test failure, not a review comment."""
    mod = globals()
    against = {n[3:-8] for n in mod if n.startswith("fx_") and n.endswith("_against")}
    forr = {n[3:-4] for n in mod if n.startswith("fx_") and n.endswith("_for")}
    assert against == forr == set(MIRROR_PAIRS), (
        f"E-20: pairing is not total. against={sorted(against)} "
        f"for={sorted(forr)}"
    )


@pytest.mark.parametrize("pair", MIRROR_PAIRS)
def test_dce_20b_each_mirror_pair_returns_the_identical_answer(tmp_path, pair):
    """E-20. Same verdict, same exit code, both directions. If the evaluator
    returns anything other than the same answer twice, it is not
    direction-blind and this test says so."""
    out = []
    for i, suffix in enumerate(("_against", "_for")):
        spec = globals()[f"fx_{pair}{suffix}"]()
        reg, fam = _build(tmp_path, spec, name=f"{pair}{i}.db")
        rep = _run(reg, fam, as_of=spec["as_of"])
        assert spec["expect"] in _verdicts(rep), (
            f"fx_{pair}{suffix}: expected {spec['expect']}, got {_verdicts(rep)}"
        )
        out.append((spec["expect"], rep.exit_code))
    assert out[0] == out[1], (
        f"E-20: mirror pair {pair!r} returned different answers by direction: "
        f"{out[0]} against vs {out[1]} for. THIS IS THE FAILURE MODE THE "
        "CLAUSE EXISTS TO PREVENT."
    )


def test_dce_21_the_understated_span_fails_exactly_as_loudly(tmp_path):
    """E-9 / E-21. THE PROOF CASE.

    PREREG-002 section 11.1: [2020-01-01, C] stated as 6.571 years,
    measured to 2026-07-28 and understated at every later C. It is the one
    stale figure in the whole 24-clause sweep that ran FOR the family, and
    that is precisely why four revision passes went over it without
    stopping. It must return SPAN-DIVERGENT and exit 3 — the same verdict
    and the same exit code as its overstating mirror."""
    spec = fx_span_for()
    reg, fam = _build(tmp_path, spec)
    rep = _run(reg, fam, as_of=spec["as_of"])
    assert "SPAN-DIVERGENT" in _verdicts(rep)
    assert rep.exit_code == 3


# ---------------------------------------------------------------------------
# E-22 / E-24 — exit codes, and the interlock with Item 1
# ---------------------------------------------------------------------------

def test_dce_22_inability_outranks_a_firing(tmp_path):
    """E-22. The exit code is the max over sites and the ordering is
    4 > 3 > 2 > 0. This seat ranks EPISTEMIC STATE, not consequence,
    because consequence is E-25's boundary and this evaluator does not
    evaluate it: a firing is a fact the firm has, an unevaluable clause is
    a fact the firm does not have."""
    reg, fam = _build(tmp_path, {
        "fields": {"forward_window_start": "2026-01-01",
                   "success_criteria": "fire at 2026-03-01; also 2026-04-01."},
        "clauses": [dict(tag="kc", field="success_criteria", source_offset=8,
                         kind="OBSERVATION", date_expr="2026-03-01",
                         discharge_event_kind="")],
    })
    rep = _run(reg, fam, as_of="2026-08-12")
    v = _verdicts(rep)
    assert "FIRED" in v and "UNCOVERED" in v
    assert rep.exit_code == 4


def test_dce_23_the_evaluator_takes_no_grant_and_writes_nothing(tmp_path):
    """E-24. Item 1 and Item 2 compose here: the read-only default is what
    lets the evaluator run with no grant at all. A checker that wrote to
    the store it checks could in principle discharge a clause by running —
    an information leak from the evaluation into the thing evaluated,
    foreclosed by construction rather than by discipline."""
    reg, fam = _build(tmp_path, fx_divergence_against())
    before = reg.conn.execute("SELECT COUNT(*) FROM events").fetchone()[0]
    _run(reg, fam, as_of="2026-08-12")
    after = reg.conn.execute("SELECT COUNT(*) FROM events").fetchone()[0]
    assert after == before, "E-24: the evaluator writes nothing"


def test_dce_24_as_of_before_the_seal_is_refused_and_an_override_is_stamped(tmp_path):
    """E-24. `--as-of` is a suppression vector and is handled as one:
    refused below the seal date, and STAMPED on every line otherwise.
    Mitigation by marking, not by prevention — I-162, filed rather than
    described as closed."""
    reg, fam = _build(tmp_path, fx_divergence_against())
    rep = _run(reg, fam, as_of="2026-08-12")
    assert rep.as_of_override is False
    rep2 = _run(reg, fam, as_of="2030-01-01")
    assert rep2.as_of_override is True
    assert "AS-OF OVERRIDE" in rep2.render()
    with pytest.raises(ValueError):
        _run(reg, fam, as_of="1999-01-01")


def test_dce_25_a_nonzero_evaluation_makes_the_gate_insufficient_data(tmp_path):
    """E-24's teeth. A family whose dated clauses cannot be evaluated has
    not earned a Gate verdict of any kind."""
    from castellan import evaluate_gate1
    import numpy as np

    reg, fam = _build(tmp_path, fx_divergence_against())
    rng = np.random.default_rng(11)
    with _writable(reg, reason="LOG_TRIAL"):
        for i in range(4):
            reg.log_trial(fam, {"p": i}, rng.normal(0, 0.01, 1200), 252)
    rep = evaluate_gate1("S", fam, reg, rng.normal(0.0006, 0.01, 1200), 252,
                         backtest_years=4.8)
    assert rep.overall == "INSUFFICIENT-DATA"
    assert getattr(rep, "dated_clause_exit_code", None) == 3
