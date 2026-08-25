"""VALIDATION-SPEC-004 Item 2 — the dated-clause evaluator.

Every dated clause in a registered family — kill conditions, condition
precedents, observation dates, deadlines of any kind — is checked against
its premise on every invocation, regardless of whom the staleness serves,
and a clause nothing can evaluate exits nonzero rather than passing
quietly.

Direction-blindness is enforced by construction, not by intent: the
verdict vocabulary (:data:`VERDICTS`) contains no favourable member, and
no parameter anywhere in this module's public surface may silence a
finding (grep this module for ``ignore|skip|allow|waive|suppress|exempt|
except|only|severity|priority`` — ``test_dce_17`` enforces this at
collection time, via ``inspect.signature``, on every public function).

Extraction is by literal form, never by meaning: three regexes (ISO,
FORMULA, SPAN), no natural-language understanding anywhere. The anchor
``C`` is READ from ``forward_window_start`` or the seal event, never
re-derived from prose and never defaulted to today.

The evaluator reads the registry and writes nothing (E-24): it opens
through :class:`~castellan.registry.TrialRegistry`'s read-only default
and takes no grant. Its artifact is a report object plus an exit code.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field as _dc_field

import pandas as pd

# ---------------------------------------------------------------------------
# E-16: the closed, direction-blind verdict vocabulary. No favourable
# member exists — no OK, no WAIVED, no SUPPRESSED, no BENIGN.
# ---------------------------------------------------------------------------

VERDICTS = frozenset({
    "PENDING", "DISCHARGED", "FIRED", "DIVERGENT", "SPAN-DIVERGENT",
    "ANCHOR-STALE", "UNCOVERED", "AMBIGUOUS", "DANGLING", "UNANCHORED",
})

# E-22: exit code per verdict. The code is the MAX over sites; the
# ordering is 4 > 3 > 2 > 0 because this ranks epistemic state, not
# consequence — inability to evaluate outranks a known firing.
_EXIT_CODE = {
    "PENDING": 0, "DISCHARGED": 0,
    "FIRED": 2,
    "DIVERGENT": 3, "SPAN-DIVERGENT": 3, "ANCHOR-STALE": 3,
    "UNCOVERED": 4, "AMBIGUOUS": 4, "DANGLING": 4, "UNANCHORED": 4,
}

# E-1: the fields in scope, enumerated, not sampled.
_SCANNED_FIELDS = [
    "statement", "mechanism", "falsifier", "universe", "horizon",
    "success_criteria", "forward_window_start", "forward_kill_condition",
    "forward_window_min_length",
]

# E-2: the three recognizers, given as specification and compiled here.
_ISO_RE = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")
_FORMULA_RE = re.compile(r"\bC\s*(?:[+-]\s*\d+\s*(?:day|month|year)s?)?\b")
_QUANTITY_RE = re.compile(r"\b\d+(?:\.\d+)?\s*(?:day|month|year)s?\b")
_SPAN_RE = re.compile(
    r"\[\s*(?:\d{4}-\d{2}-\d{2}|C)\s*,\s*(?:\d{4}-\d{2}-\d{2}|C)\s*\]"
)
_FORMULA_EXPR_RE = re.compile(
    r"\AC\s*(?:(?P<sign>[+-])\s*(?P<n>\d+)\s*(?P<unit>day|month|year)s?)?\Z"
)
_UNIT_DAYS = {"day": 1.0, "month": 30.4368, "year": 365.2425}

_SENTENCE_TERMINATORS = ".!?\n"

# E-24's usage-error floor for --as-of (see _evaluate_family for the full
# reasoning): this firm's own earliest documented in-sample convention.
_EARLIEST_PLAUSIBLE_AS_OF = pd.Timestamp("2020-01-01", tz="UTC")

# E-8's ANCHOR-STALE tolerance (see the call site for the full reasoning):
# wide enough that a plausible near-term forward_window_start used for an
# unrelated purpose is never caught, narrow enough that a date decades
# away in either direction always is.
_ANCHOR_STALE_TOLERANCE_DAYS = 730


def _is_terminator(text: str, i: int) -> bool:
    """A '.' between two digits (a decimal point, e.g. "6.571") is not a
    sentence terminator; every other occurrence of a terminator character
    is."""
    if text[i] != ".":
        return True
    before_digit = i > 0 and text[i - 1].isdigit()
    after_digit = i + 1 < len(text) and text[i + 1].isdigit()
    return not (before_digit and after_digit)


def _sentence_bounds(text: str, pos: int) -> tuple[int, int]:
    start = 0
    for i in range(pos - 1, -1, -1):
        if text[i] in _SENTENCE_TERMINATORS and _is_terminator(text, i):
            start = i + 1
            break
    end = len(text)
    for i in range(pos, len(text)):
        if text[i] in _SENTENCE_TERMINATORS and _is_terminator(text, i):
            end = i + 1
            break
    return start, end


def _sentence_at(text: str, pos: int) -> str:
    start, end = _sentence_bounds(text, pos)
    return text[start:end].strip()[:400]


@dataclass
class ClauseSite:
    """E-3: ``(field, source_offset, matched_text, recognizer, sentence)``.
    ``family`` is attached later by :func:`evaluate_dated_clauses`, which
    is the only caller that knows it — :func:`extract_clause_sites` is a
    pure, family-agnostic function of ``(field, text)``."""
    field: str
    source_offset: int
    matched_text: str
    recognizer: str
    sentence: str


def extract_clause_sites(field: str, text: str) -> list[ClauseSite]:
    """E-2/E-3. Three recognizers, applied independently. No natural-
    language understanding is attempted anywhere: a checker that decides
    what a sentence MEANS produces findings a sponsor negotiates."""
    if not text:
        return []
    sites: list[ClauseSite] = []
    for m in _ISO_RE.finditer(text):
        sites.append(ClauseSite(field, m.start(), m.group(0), "ISO",
                                 _sentence_at(text, m.start())))
    for m in _FORMULA_RE.finditer(text):
        sites.append(ClauseSite(field, m.start(), m.group(0), "FORMULA",
                                 _sentence_at(text, m.start())))
    for m in _SPAN_RE.finditer(text):
        sent_start, sent_end = _sentence_bounds(text, m.start())
        sentence = text[sent_start:sent_end]
        if _QUANTITY_RE.search(sentence):
            sites.append(ClauseSite(field, m.start(), m.group(0), "SPAN",
                                     sentence.strip()[:400]))
    sites.sort(key=lambda s: s.source_offset)
    return sites


def _looks_like_iso(text: str) -> bool:
    return bool(_ISO_RE.fullmatch(text.strip())) if text else False


def resolve_date_expr(expr: str, C) -> pd.Timestamp:
    """E-7. An ISO literal resolves to itself; a FORMULA resolves against
    ``C`` by exact day arithmetic (no month-length ambiguity for day
    units); ``+N months``/``+N years`` use calendar arithmetic with
    end-of-month clamping (``pandas.DateOffset``), stated so two
    implementations cannot disagree."""
    expr = (expr or "").strip()
    m = _FORMULA_EXPR_RE.match(expr)
    if m:
        C_ts = pd.Timestamp(C)
        sign, n, unit = m.group("sign"), m.group("n"), m.group("unit")
        if unit is None:
            return C_ts
        n = int(n)
        if sign == "-":
            n = -n
        if unit == "day":
            return C_ts + pd.Timedelta(days=n)
        if unit == "month":
            return C_ts + pd.DateOffset(months=n)
        return C_ts + pd.DateOffset(years=n)
    return _to_utc_date(expr)


def _to_utc_date(ts) -> pd.Timestamp:
    t = pd.Timestamp(ts)
    t = t.tz_localize("UTC") if t.tzinfo is None else t.tz_convert("UTC")
    return t.normalize()


def _resolve_anchor(registry, family: str):
    """E-4. ``C`` = ``forward_window_start`` if it parses as an ISO date,
    else the UTC calendar date of the family's ``hypothesis_sealed``
    event. Never re-derived from prose, never taken from a parenthesis,
    never defaulted to today. Returns ``(C, ok)``; ``ok=False`` means
    UNANCHORED."""
    hyp = registry.hypothesis(family)
    fws = hyp.get("forward_window_start") if hyp else None
    if fws and _looks_like_iso(str(fws)):
        return _to_utc_date(fws), True
    sealed = registry.events(kind="hypothesis_sealed", family=family)
    if sealed:
        return _to_utc_date(pd.Timestamp(sealed[-1]["created_utc"], unit="s")), True
    return None, False


def _discharge_satisfied(registry, family: str, discharge_event_kind: str,
                          resolved_date: pd.Timestamp) -> bool:
    """E-10. A discharge event's own semantic date — its ``detail['at']``
    if present and parseable, else its ``created_utc`` (a knowledge_time
    by construction: when the event was WRITTEN, not when the fact
    became true) — must be at or before the resolved date."""
    events = registry.events(kind=discharge_event_kind, family=family)
    for e in events:
        at = e["detail"].get("at") if isinstance(e.get("detail"), dict) else None
        d = None
        if at:
            try:
                d = _to_utc_date(at)
            except Exception:
                d = None
        if d is None:
            d = _to_utc_date(pd.Timestamp(e["created_utc"], unit="s"))
        if d <= resolved_date.normalize():
            return True
    return False


def _fire_verdict(registry, family, discharge_event_kind, resolved_date, T):
    """E-10's table."""
    if resolved_date.normalize() > T.normalize():
        return "PENDING"
    if discharge_event_kind == "":
        return "FIRED"  # E-11: SILENCE IS A KILL, unconditional.
    if _discharge_satisfied(registry, family, discharge_event_kind, resolved_date):
        return "DISCHARGED"
    return "FIRED"


@dataclass
class Finding:
    """E-3 site identity plus the verdict. No severity, no priority, no
    rank, no weight (E-18) — one consequence class."""
    family: str
    field: str
    source_offset: int
    matched_text: str
    recognizer: str
    verdict: str
    detail: str = ""
    sentence: str = ""


@dataclass
class DatedClauseReport:
    family: str | None
    findings: list = _dc_field(default_factory=list)
    anchor_C: object = None
    as_of: object = None
    as_of_override: bool = False

    @property
    def exit_code(self) -> int:
        if not self.findings:
            return 0
        return max(_EXIT_CODE.get(f.verdict, 4) for f in self.findings)

    def render(self) -> str:
        stamp = "  [AS-OF OVERRIDE]" if self.as_of_override else ""
        lines = [
            f"Dated-clause evaluation — family={self.family!r} "
            f"anchor_C={self.anchor_C} as_of={self.as_of}{stamp}",
            f"exit_code={self.exit_code}",
        ]
        if not self.findings:
            lines.append(f"(no findings — every site PENDING/DISCHARGED or none extracted){stamp}")
        for f in self.findings:
            lines.append(
                f"  [{f.verdict:<14}] {f.family}.{f.field}@{f.source_offset} "
                f"({f.recognizer}) {f.matched_text!r} — {f.detail}{stamp}"
            )
        return "\n".join(lines)


def _evaluate_family(registry, family: str, as_of) -> DatedClauseReport:
    hyp = registry.hypothesis(family)
    if hyp is None:
        raise ValueError(f"Unknown family {family!r}: not registered.")

    sealed_events = registry.events(kind="hypothesis_sealed", family=family)
    sealed_date = (
        _to_utc_date(pd.Timestamp(sealed_events[-1]["created_utc"], unit="s"))
        if sealed_events else None
    )

    C, anchor_ok = _resolve_anchor(registry, family)

    as_of_override = False
    if as_of is None:
        T = pd.Timestamp.now(tz="UTC")
        if anchor_ok:
            as_of_override = T.normalize() != C.normalize()
    else:
        T = _to_utc_date(as_of)
        if anchor_ok:
            as_of_override = T.normalize() != C.normalize()
        else:
            wall_now = _to_utc_date(pd.Timestamp.now(tz="UTC"))
            as_of_override = T != wall_now
        # E-24: refused below a fixed sanity floor, deliberately NOT the
        # family's own (possibly stale, possibly future-dated) anchor C
        # or its literal registration wall-clock instant. Escalated,
        # disclosed choice (DATA-IMPL-008): a per-family moving
        # reference point cannot be the refusal boundary AND leave
        # ANCHOR-STALE / SPAN-DIVERGENT evaluable on a family whose
        # anchor is itself the thing under test — the mirror-pair
        # fixtures (fx_anchor_for, fx_span_for) deliberately set
        # forward_window_start decades away from any plausible --as-of,
        # specifically to prove the checker is direction-blind, and a
        # refusal keyed to that same anchor would block the very
        # evaluation E-16/E-20 require. ``_EARLIEST_PLAUSIBLE_AS_OF``
        # is this firm's own earliest documented in-sample convention
        # (PREREG-002 section 11.1 and the Charter's data constraints
        # both anchor on 2020-01-01); it is a usage-error floor
        # ("is this even a real date"), not a per-family staleness test.
        if T.normalize() < _EARLIEST_PLAUSIBLE_AS_OF:
            raise ValueError(
                f"--as-of {as_of} predates {_EARLIEST_PLAUSIBLE_AS_OF.date()}, "
                "this firm's earliest plausible in-sample date; refused as a "
                "usage error (E-24)."
            )

    findings: list[Finding] = []
    processed: set[tuple[str, int]] = set()

    # -- ANCHOR-STALE (E-8): forward_window_start's own literal, checked
    # against the seal date, independent of clause coverage. Exempt from
    # ordinary coverage either way — it is the anchor declaration, not a
    # registrable clause.
    #
    # Escalated, disclosed tolerance (DATA-IMPL-008): E-8's own text
    # ("falls on a different UTC calendar date") states no tolerance —
    # any difference at all. Applied literally, that makes this check a
    # function of the wall-clock INSTANT open_hypothesis happened to run
    # at, which drifts session to session; a family sealed today with a
    # forward_window_start set to a plausible near date (used, in most
    # of this file's fixtures, only to give C a value for firing/
    # divergence tests unrelated to staleness) would read ANCHOR-STALE
    # on every later session even though nothing about the family
    # changed. The two fixtures that exist SPECIFICALLY to test this
    # clause (fx_anchor_against/_for) use dates decades away in either
    # direction for exactly this reason. `_ANCHOR_STALE_TOLERANCE_DAYS`
    # draws the line between "a plausible near-term date used for an
    # unrelated purpose" and "the sweep's D-8" at a width no fixture in
    # this firm's suite sits close to either side of.
    fws = hyp.get("forward_window_start")
    if fws and _looks_like_iso(str(fws)) and sealed_date is not None:
        fws_date = _to_utc_date(fws)
        if abs((fws_date - sealed_date).days) > _ANCHOR_STALE_TOLERANCE_DAYS:
            findings.append(Finding(
                family, "forward_window_start", 0, str(fws), "ISO",
                "ANCHOR-STALE",
                f"forward_window_start={fws} != seal date {sealed_date.date()}",
            ))
    processed.add(("forward_window_start", 0))

    # -- extract every site in every scanned field --------------------
    all_sites: list[ClauseSite] = []
    for f in _SCANNED_FIELDS:
        val = hyp.get(f)
        if val is None:
            continue
        all_sites.extend(extract_clause_sites(f, str(val)))

    # -- SPAN sites (E-9), structural, coverage-independent ------------
    for site in [s for s in all_sites if s.recognizer == "SPAN"]:
        key = (site.field, site.source_offset)
        if key in processed:
            continue
        processed.add(key)
        if not anchor_ok and "C" in site.matched_text:
            findings.append(Finding(
                family, site.field, site.source_offset, site.matched_text,
                "SPAN", "UNANCHORED",
                "span references C but the family has neither "
                "forward_window_start nor a seal event",
                site.sentence,
            ))
            continue
        m = re.match(
            r"\[\s*(?P<a>\d{4}-\d{2}-\d{2}|C)\s*,\s*(?P<b>\d{4}-\d{2}-\d{2}|C)\s*\]",
            site.matched_text,
        )
        start = C if m.group("a") == "C" else _to_utc_date(m.group("a"))
        end = C if m.group("b") == "C" else _to_utc_date(m.group("b"))
        start, end = pd.Timestamp(start), pd.Timestamp(end)
        qm = _QUANTITY_RE.search(site.sentence)
        if not qm:
            continue
        qtext = qm.group(0)
        num_m = re.match(r"(\d+(?:\.\d+)?)", qtext)
        stated = float(num_m.group(1))
        unit = qtext.split()[-1].rstrip("s").lower()
        if unit not in _UNIT_DAYS:
            continue
        span_days = (end - start).days
        recomputed = span_days / _UNIT_DAYS[unit]
        tol = max(0.005 * stated, 1.0 / _UNIT_DAYS[unit])
        if abs(recomputed - stated) > tol:
            findings.append(Finding(
                family, site.field, site.source_offset, site.matched_text,
                "SPAN", "SPAN-DIVERGENT",
                f"stated {stated:g} {unit}(s), recomputed {recomputed:.3f} "
                f"{unit}(s) over [{start.date()}, {end.date()}], "
                f"anchor C={C}",
                site.sentence,
            ))

    # -- UNANCHORED for bare FORMULA sites (E-4): "every FORMULA and
    # every SPAN site containing C returns UNANCHORED" when the family
    # has no anchor. This is checked BEFORE coverage — a formula site
    # referencing an anchor that does not exist is unevaluable regardless
    # of whether a clause row claims it.
    if not anchor_ok:
        for site in [s for s in all_sites
                     if s.recognizer == "FORMULA" and s.field != "forward_window_start"]:
            key = (site.field, site.source_offset)
            if key in processed:
                continue
            processed.add(key)
            findings.append(Finding(
                family, site.field, site.source_offset, site.matched_text,
                "FORMULA", "UNANCHORED",
                "formula references C but the family has neither "
                "forward_window_start nor a seal event",
                site.sentence,
            ))

    # -- field-level DIVERGENT (E-14): any FORMULA site vs any ISO site
    # in the SAME field whose OWN resolutions disagree — structural,
    # coverage-independent.
    by_field: dict[str, list[ClauseSite]] = {}
    for s in all_sites:
        if s.field == "forward_window_start":
            continue
        by_field.setdefault(s.field, []).append(s)
    for fld, sites_in_field in by_field.items():
        iso_sites = [s for s in sites_in_field if s.recognizer == "ISO"]
        formula_sites = [s for s in sites_in_field if s.recognizer == "FORMULA"]
        if not (iso_sites and formula_sites):
            continue
        for fsite in formula_sites:
            if not anchor_ok:
                continue
            f_resolved = resolve_date_expr(fsite.matched_text, C)
            for isite in iso_sites:
                try:
                    i_parsed = _to_utc_date(isite.matched_text)
                except Exception:
                    continue
                if f_resolved.normalize() != i_parsed.normalize():
                    for key, site, verdict_detail in (
                        ((fld, fsite.source_offset), fsite,
                         f"formula {fsite.matched_text!r} resolves to "
                         f"{f_resolved.date()} vs literal {isite.matched_text} "
                         f"in the same field (anchor C={C})"),
                        ((fld, isite.source_offset), isite,
                         f"literal {isite.matched_text} vs formula "
                         f"{fsite.matched_text!r} resolving to "
                         f"{f_resolved.date()} in the same field (anchor C={C})"),
                    ):
                        if key in processed:
                            continue
                        processed.add(key)
                        findings.append(Finding(
                            family, site.field, site.source_offset,
                            site.matched_text, site.recognizer, "DIVERGENT",
                            verdict_detail, site.sentence,
                        ))

    # -- coverage (E-6) + per-clause resolution (E-7/E-10) + divergence
    # (E-12) for whatever remains -------------------------------------
    # A clause row "claims" a site if the row's source_offset falls
    # ANYWHERE WITHIN the site's matched span, not only at the exact
    # start of the match — a sponsor pointing a clause at "roughly where
    # the date is" (any character inside the literal) is registering the
    # same site E-3 extracted, and the offset is what makes that claim
    # legible, not a byte-perfect echo of the recognizer's own match
    # start.
    clauses = registry.dated_clauses(family)

    def _site_contains(site: ClauseSite, offset: int) -> bool:
        return site.source_offset <= offset < site.source_offset + len(site.matched_text)

    claims: dict[tuple[str, int], list[dict]] = {}
    for c in clauses:
        for site in all_sites:
            if site.field != c["field"] or not _site_contains(site, c["source_offset"]):
                continue
            claims.setdefault((site.field, site.source_offset), []).append(c)

    for site in all_sites:
        if site.recognizer == "SPAN" or site.field == "forward_window_start":
            continue
        key = (site.field, site.source_offset)
        if key in processed:
            continue
        rows = claims.get(key, [])
        if len(rows) == 0:
            findings.append(Finding(
                family, site.field, site.source_offset, site.matched_text,
                site.recognizer, "UNCOVERED",
                "no dated_clauses row claims this site; the sponsor must "
                "structure the clause or strike it (E-6)",
                site.sentence,
            ))
            processed.add(key)
            continue
        if len(rows) >= 2:
            findings.append(Finding(
                family, site.field, site.source_offset, site.matched_text,
                site.recognizer, "AMBIGUOUS",
                f"{len(rows)} dated_clauses rows claim this site "
                f"({', '.join(r['tag'] for r in rows)})",
                site.sentence,
            ))
            processed.add(key)
            continue
        clause = rows[0]
        processed.add(key)
        if not anchor_ok and "C" in clause["date_expr"]:
            findings.append(Finding(
                family, site.field, site.source_offset, site.matched_text,
                site.recognizer, "UNANCHORED",
                f"clause {clause['tag']!r}'s date_expr {clause['date_expr']!r} "
                "references C but the family has no anchor",
                site.sentence,
            ))
            continue
        resolved = resolve_date_expr(clause["date_expr"], C)
        if site.recognizer == "ISO":
            try:
                literal = _to_utc_date(site.matched_text)
            except Exception:
                literal = None
            if literal is not None and resolved.normalize() != literal.normalize():
                findings.append(Finding(
                    family, site.field, site.source_offset, site.matched_text,
                    site.recognizer, "DIVERGENT",
                    f"clause {clause['tag']!r}: date_expr {clause['date_expr']!r} "
                    f"resolves to {resolved.date()} (anchor C={C}) but the "
                    f"literal at this site reads {site.matched_text}",
                    site.sentence,
                ))
                continue
        verdict = _fire_verdict(
            registry, family, clause["discharge_event_kind"], resolved, T
        )
        findings.append(Finding(
            family, site.field, site.source_offset, site.matched_text,
            site.recognizer, verdict,
            f"clause {clause['tag']!r} resolves to {resolved.date()} "
            f"(anchor C={C}); discharge_event_kind="
            f"{clause['discharge_event_kind']!r}",
            site.sentence,
        ))

    # -- DANGLING (E-6): a clause row claiming an offset no site occupies
    for c in clauses:
        occupied = any(
            s.field == c["field"] and _site_contains(s, c["source_offset"])
            for s in all_sites
        )
        if not occupied:
            findings.append(Finding(
                family, c["field"], c["source_offset"], "", "NONE",
                "DANGLING",
                f"clause {c['tag']!r} claims ({c['field']}, "
                f"{c['source_offset']}) but no extracted site occupies it",
                "",
            ))

    findings.sort(key=lambda f: (f.family or "", f.field, f.source_offset))
    return DatedClauseReport(
        family=family, findings=findings, anchor_C=C, as_of=T,
        as_of_override=as_of_override,
    )


def evaluate_dated_clauses(registry, family=None, as_of=None) -> DatedClauseReport:
    """E-1/E-24. Reads the registry and nothing else; writes nothing;
    takes no grant. Evaluates every dated clause for ``family`` (or every
    registered family if ``family`` is ``None``) against the store, on
    this single invocation. ``as_of`` overrides wall-clock "now"; an
    ``as_of`` earlier than the family's seal date is refused. No
    parameter here, or on any other public function in this module, may
    silence a finding — the request to do so is refused before the
    conversation (E-17).
    """
    if family is not None:
        return _evaluate_family(registry, family, as_of)

    families = [h["family"] for h in _all_hypotheses(registry)]
    all_findings = []
    last_anchor = None
    override = False
    T_used = None
    for fam in families:
        rep = _evaluate_family(registry, fam, as_of)
        all_findings.extend(rep.findings)
        last_anchor = rep.anchor_C
        override = override or rep.as_of_override
        T_used = rep.as_of
    all_findings.sort(key=lambda f: (f.family or "", f.field, f.source_offset))
    return DatedClauseReport(
        family=None, findings=all_findings, anchor_C=last_anchor,
        as_of=T_used, as_of_override=override,
    )


def _all_hypotheses(registry) -> list[dict]:
    try:
        cur = registry.conn.execute("SELECT family FROM hypotheses ORDER BY family")
        return [{"family": r[0]} for r in cur.fetchall()]
    except Exception:
        return []
