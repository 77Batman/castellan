"""Gate 1 evaluation — the Validation Report, computed, not narrated.

Every criterion from Charter 4.4 that the harness can compute is computed
here from primary inputs; N and the cross-sectional trial-Sharpe
dispersion come from the Trial Registry, never from the caller. Anything
the harness cannot verify is INSUFFICIENT-DATA — which is not PASS, and
one non-PASS fails the Gate.

The report embeds the config hash, a sha256 of the evaluated return
series, and the registry trial count at evaluation time, so a "report"
without a reproducible run behind it cannot exist.
"""

from __future__ import annotations

import hashlib
import json
import math
import time
from dataclasses import dataclass, asdict

import numpy as np
import pandas as pd

from . import stats
from .registry import TrialRegistry, HARNESS_INTERNAL_TOKEN

# Firm constants — Charter 4.2. Changing these is a Charter amendment.
T_STAT_HURDLE = 3.0
NET_SHARPE_MIN = 1.0
DSR_MIN = 0.95
PBO_MAX_PAPER = 0.10
WFE_MIN = 0.50
WFE_MIN_WINDOWS = 10
MIN_YEARS = 4.0
SUBPERIOD_POSITIVITY_MIN = 0.60
MAX_DAY_SHARE = 0.10
MAX_MONTH_SHARE = 0.25
PARAM_SURFACE_MIN_PROFITABLE = 0.60
CAPACITY_MULTIPLE_MIN = 10.0
CORR_MAX_TO_LIVE_BOOK = 0.30
CSCV_PARTITIONS_S = 16
HOLDOUT_MIN_MONTHS = 12.0  # Charter 4.4; mirrored in holdout.py's default
LENGTH_DISAGREEMENT_MAX = 0.05  # I-010 G3: fraction of the calendar figure

PASS, FAIL, INSUFF = "PASS", "FAIL", "INSUFFICIENT-DATA"


@dataclass
class Criterion:
    name: str
    value: float | str | None
    threshold: str
    verdict: str
    note: str = ""


_HISTORICAL_HOLDOUT_SENTENCE = (
    "This holdout is historical. It establishes that the window was not "
    "searched over through the harness. It does not establish that the "
    "window was unknown to the researchers, and no control in this firm "
    "can establish that."
)


@dataclass
class ValidationReport:
    strategy: str
    family: str
    date_utc: float
    n_trials: int
    trial_budget: int
    sr_std_period_trials: float | None
    criteria: list[Criterion]
    overall: str
    returns_sha256: str
    breakeven_cost_multiplier: float | None
    holdout_spec_sha256: str | None = None
    holdout_payload_sha256: str | None = None
    # R1 (Ruling 002 / Ruling 001 §2.4): the report must state on its face
    # whether the holdout is FORWARD or HISTORICAL. Every report the
    # harness could previously produce lacked this field (I-018).
    holdout_classification: str | None = None
    # P5: the pre-registration's own sealed hash, so a report can be
    # audited against the exact claim it was evaluated against.
    prereg_sha256: str | None = None
    # P8: predecessor chain's sealed prereg hashes, family -> sha256.
    predecessor_prereg_sha256: dict[str, str] | None = None
    # C-001 §3.0 / H-12: the declared/logged decomposition of n_trials,
    # so the report can never render a bare N that launders an
    # [inferred] declaration (n_inherited) into a [measured]-looking
    # integer. 0 / None means "this family has no seeding" and the
    # original bare rendering is used unchanged (H-13).
    n_inherited: int = 0
    n_logged: int | None = None
    # E-10 (VALIDATION-SPEC-001, I-050): report fields, NOT Criterion rows
    # (test_hac_t14 guards this). t_stat_hac is the same figure graded by
    # the "t-statistic (net, HAC-corrected)" criterion (t_gate);
    # t_stat_uncorrected is reported for continuity and is never graded.
    t_stat_uncorrected: float | None = None
    t_stat_hac: float | None = None
    hac_lag: int | None = None
    hac_lag_rule: str | None = None
    hac_rho_hat: float | None = None
    # VALIDATION-SPEC-002 M-10: the serial-corrected MinBTL and the VIF
    # that corrects it, D-8/D-9: the serial-corrected DSR and T_eff. All
    # report fields, NOT Criterion rows (M-10 / test_hac_t14's precedent).
    minbtl_iid_years: float | None = None
    minbtl_serial_years: float | None = None
    vif_gate: float | None = None
    vif_hac: float | None = None
    vif_ar1: float | None = None
    vif_rho_hat: float | None = None
    n_max_admissible_iid: int | None = None
    n_max_admissible_serial: int | None = None
    dsr_iid: float | None = None
    dsr_serial: float | None = None
    t_eff: float | None = None
    # Convenience fields for the M-10 render block; not independently
    # required by any test, but needed to render the block's own shape.
    vif_source: str | None = None
    vif_n_series_used: int | None = None
    # VALIDATION-SPEC-003 B-27: report fields, NOT Criterion rows (M-10 /
    # E-10's precedent, guarded by test_hac_t14). `trial_budget` above is
    # unchanged and stays the sealed figure (B-2); `trial_budget_sealed`
    # is the same number under B-27's own name, `trial_budget_effective`
    # is the sealed budget plus every ADMITTED/CAPPED extension's
    # admitted increment, `n_own_logged` is this family's own (NOT
    # chain-summed) logged trial count, and `budget_extensions` lists
    # EVERY trial_budget_extension event for this family, including
    # every refused one, with its issuer, countersigner, and status.
    trial_budget_sealed: int | None = None
    trial_budget_effective: int | None = None
    n_own_logged: int | None = None
    budget_extensions: list | None = None
    # VALIDATION-SPEC-004 R-15 / E-24: on the face of every report,
    # whether or not they fire (§4.7.4(ii): a control that is only
    # visible when it fires is one nobody can confirm is running).
    write_grant_chain_head: str | None = None
    write_grant_chain_intact: bool | None = None
    write_grant_orphan_rows: dict | None = None
    dated_clause_exit_code: int | None = None
    dated_clause_render: str | None = None

    def to_json(self) -> str:
        d = asdict(self)
        return json.dumps(d, indent=2, default=str)

    def to_markdown(self) -> str:
        # H-12: a seeded family renders the full decomposition on the
        # report's face — total, declared-inherited, and logged, all
        # three visible — rather than a bare N that reads as N observed
        # trials when most of it is an [inferred] declaration (house
        # rule 6). An unseeded family (n_inherited == 0) keeps the
        # original bare rendering, unchanged (H-13).
        if self.n_inherited:
            n_display = (
                f"**{self.n_trials:,}** ({self.n_inherited:,} declared "
                f"inherited [inferred, D-009] + {self.n_logged:,} logged)"
            )
        else:
            n_display = f"**{self.n_trials}**"
        lines = [
            f"# Validation Report — {self.strategy}",
            "",
            f"Family: `{self.family}` · Evaluated (UTC): {time.strftime('%Y-%m-%d %H:%M', time.gmtime(self.date_utc))}",
            f"Trial count N (registry): {n_display} / budget {self.trial_budget} · "
            f"cross-sectional trial SR std (per-period): "
            f"{self.sr_std_period_trials if self.sr_std_period_trials is not None else 'UNAVAILABLE'}",
            f"Evaluated return series sha256: `{self.returns_sha256[:16]}…`",
            f"Holdout spec sha256: `{self.holdout_spec_sha256[:16] + '…' if self.holdout_spec_sha256 else 'UNAVAILABLE'}` · "
            f"Holdout payload sha256: `{self.holdout_payload_sha256[:16] + '…' if self.holdout_payload_sha256 else 'UNAVAILABLE'}`",
            f"Holdout classification: **{self.holdout_classification or 'UNCLASSIFIED'}** · "
            f"Pre-registration sha256: `{self.prereg_sha256[:16] + '…' if self.prereg_sha256 else 'UNAVAILABLE'}`",
        ]
        if self.holdout_classification == "HISTORICAL":
            lines.append("")
            lines.append(f"> {_HISTORICAL_HOLDOUT_SENTENCE}")
        if self.predecessor_prereg_sha256:
            lines.append("")
            lines.append("Predecessor chain pre-registration hashes: " + "; ".join(
                f"`{fam}`={sha[:16]}…" for fam, sha in self.predecessor_prereg_sha256.items()
            ))
        lines += [
            "",
            "| Criterion | Value | Threshold | Verdict |",
            "|---|---|---|---|",
        ]
        for c in self.criteria:
            v = c.value
            if isinstance(v, float):
                v = f"{v:.4g}"
            lines.append(f"| {c.name} | {v} | {c.threshold} | **{c.verdict}**"
                         + (f" — {c.note}" if c.note else "") + " |")
        if self.t_stat_hac is not None:
            lines.append("")
            lines.append(
                f"t-statistic: HAC-corrected **{self.t_stat_hac:.3f}** at lag "
                f"{self.hac_lag} ({self.hac_lag_rule}, ρ̂ = {self.hac_rho_hat:+.3f}) "
                f"· uncorrected {self.t_stat_uncorrected:.3f} — **the uncorrected "
                "figure assumes serial independence, is reported for continuity, "
                "and is NOT graded.**"
            )
        if self.vif_gate is not None:
            lines.append("")
            divergence_note = ""
            if (self.vif_ar1 is not None and self.vif_hac is not None
                    and self.vif_hac > 0 and not math.isnan(self.vif_hac)
                    and not math.isnan(self.vif_ar1)
                    and self.vif_ar1 > 1.5 * self.vif_hac):
                # M-14: disclosed on the report face, not adjusted to
                # accommodate any family. A sponsor whose Gate verdict
                # turns on this gap brings it to Validation.
                divergence_note = (
                    f" — AR(1) plug-in exceeds HAC by "
                    f"{self.vif_ar1 / self.vif_hac:.2f}×; MA/overlapping-"
                    "label structure is the likely cause (M-13) and the "
                    "plug-in over-states it."
                )
            lines.append(
                f"Serial dependence: VIF = **{self.vif_gate:.3f}** (HAC "
                f"{self.vif_hac:.3f}, AR(1) plug-in {self.vif_ar1:.3f}, "
                f"ρ̂ = {self.vif_rho_hat:+.3f}, lag {self.hac_lag}, source "
                f"{self.vif_source}, {self.vif_n_series_used} trial "
                f"series){divergence_note}."
            )
            if self.minbtl_iid_years is not None:
                minbtl_serial_str = (
                    f"{self.minbtl_serial_years:.2f}y" if self.minbtl_serial_years
                    is not None else "N/A"
                )
                lines.append(
                    f"MinBTL: **{minbtl_serial_str}** serial-corrected · "
                    f"{self.minbtl_iid_years:.2f}y assuming serial "
                    "independence — **the i.i.d. figure is reported for "
                    "continuity and is NOT graded.**"
                )
            if (self.n_max_admissible_iid is not None
                    and self.n_max_admissible_serial is not None):
                n_max = min(self.n_max_admissible_iid, self.n_max_admissible_serial)
                lines.append(
                    f"Admissible trial ceiling on this span and Sharpe: "
                    f"**N_max = {n_max}** (= min({self.n_max_admissible_iid}, "
                    f"{self.n_max_admissible_serial})). Registry N = "
                    f"{self.n_trials}."
                )
        if self.breakeven_cost_multiplier is not None:
            lines.append("")
            lines.append(
                f"Breakeven cost multiplier (t falls below {T_STAT_HURDLE:g}): "
                f"**{self.breakeven_cost_multiplier:.2f}×** modelled costs."
            )
        if self.write_grant_chain_head is not None:
            lines.append("")
            lines.append(
                f"Write-grant audit: chain_head=`{self.write_grant_chain_head[:16]}…` "
                f"chain_intact={self.write_grant_chain_intact} "
                f"orphan_rows={self.write_grant_orphan_rows}"
            )
        if self.dated_clause_exit_code is not None:
            lines.append("")
            lines.append(f"Dated-clause evaluator exit code: **{self.dated_clause_exit_code}**")
            if self.dated_clause_render:
                lines.append("")
                lines.append(self.dated_clause_render)
        lines += ["", f"## Overall verdict: **{self.overall}**", ""]
        fails = [c for c in self.criteria if c.verdict != PASS]
        if fails:
            lines.append("Non-passing criteria: " + ", ".join(c.name for c in fails))
        return "\n".join(lines)


def _crit(name, value, threshold, ok: bool | None, note="") -> Criterion:
    if ok is None:
        return Criterion(name, value, threshold, INSUFF, note)
    return Criterion(name, value, threshold, PASS if ok else FAIL, note)


# ======================================================================
# VALIDATION-SPEC-003 (B-1 .. B-31, RULING 003-A) -- the trial-budget
# criterion. I-022's substantive fix: `over` was computed and used only
# to write a note; the verdict argument was the literal `True`. This
# section replaces that with a graded, per-trial, prospective-only walk
# against an effective budget that only a countersigned (discretionary)
# or recomputed (contingent) extension event can raise -- never an
# aggregate comparison, which legalises spend-first-authorize-after
# (B-9: "a budget is not a receipt").
# ======================================================================

_EXTENSION_MODES = frozenset({"DISCRETIONARY", "CONTINGENT"})
_DISCRETIONARY_SELF_ISSUERS = frozenset({"director-of-research", "principal"})
_VALID_COUNTERSIGNERS = frozenset({"quant-validation", "principal"})
_CONTINGENT_PREDICATE_NAME = "n_max_admits_declared_ceiling"

_STATUS_ADMITTED = "ADMITTED"
_STATUS_CAPPED = "CAPPED"
_STATUS_WITHDRAWN = "WITHDRAWN"
_STATUS_REFUSED_MALFORMED = "REFUSED-MALFORMED"
_STATUS_REFUSED_UNCOUNTERSIGNED = "REFUSED-UNCOUNTERSIGNED"
_STATUS_REFUSED_SELF_ISSUED = "REFUSED-SELF-ISSUED"
_STATUS_REFUSED_PREDICATE = "REFUSED-PREDICATE"


def contingent_increment_allowed(
    n_max: int | None, declared_ceiling_base: int, declared_increment: int
) -> int:
    """B-18 / B-28. Pure and unit-testable without a Gate fixture
    (`test_tbe_15` grades this directly).

    ``clamp(n_max - declared_ceiling_base, 0, declared_increment)``.
    Returns ``0`` where ``n_max`` is ``None`` (B-19: unevaluable is never
    a permissive default). The clamp is two-sided: it never exceeds what
    was declared and never goes negative. Reused, with a running
    ``declared_ceiling_base`` offset, to consume B-20's aggregate cap
    across multiple contingent events in creation order -- event *i*'s
    allowance is this same function called with the base raised by every
    earlier event's own admitted amount.
    """
    if n_max is None:
        return 0
    allowed = n_max - declared_ceiling_base
    if allowed < 0:
        allowed = 0
    if allowed > declared_increment:
        allowed = declared_increment
    return int(allowed)


def _validate_extension_schema(detail: dict) -> str | None:
    """B-13 (common schema) + B-17 (the CONTINGENT predicate vocabulary).
    Schema-only: returns a malformation reason string, or ``None`` if
    well-formed. Does not consult the registry and does not decide
    admissibility -- B-21's cross-check (which needs the registry) is
    the caller's job."""
    mode = detail.get("mode")
    if mode not in _EXTENSION_MODES:
        return f"mode {mode!r} not in {{'DISCRETIONARY', 'CONTINGENT'}}"
    inc = detail.get("increment")
    if isinstance(inc, bool) or not isinstance(inc, int):
        return f"increment {inc!r} is not an int (a bool is not an int here, H-2)"
    if inc <= 0:
        return f"increment {inc!r} is not > 0"
    for key in ("issuer", "reason", "authorization_ref"):
        val = detail.get(key)
        if not isinstance(val, str) or not val.strip():
            return f"{key!r} must be a non-empty, non-blank string, got {val!r}"
    n_at_issue = detail.get("n_logged_at_issue")
    if (isinstance(n_at_issue, bool) or not isinstance(n_at_issue, int)
            or n_at_issue < 0):
        return f"n_logged_at_issue {n_at_issue!r} must be an int >= 0"
    predicate = detail.get("predicate")
    if mode == "CONTINGENT":
        if not isinstance(predicate, dict):
            return "CONTINGENT extension requires a 'predicate' dict"
        if predicate.get("name") != _CONTINGENT_PREDICATE_NAME:
            return f"unknown predicate.name {predicate.get('name')!r} (B-17: closed vocabulary)"
        params = predicate.get("params")
        if params != {}:
            return f"predicate.params must be empty, got {params!r} (B-17)"
    elif predicate is not None:
        return "DISCRETIONARY extension must not carry a 'predicate'"
    return None


def _admissible_ceiling(oos_index, fam, sr_ann, periods_per_year, vif_res) -> int | None:
    """B-18/B-19's N_max = min(n_max_admissible_iid, n_max_admissible_serial)
    -- the SAME figure the length criterion computes further down
    (M-4/M-5), consumed here for the CONTINGENT admissibility arithmetic
    before the length criterion itself runs. No new statistic (B-18): the
    inputs and the formula are identical to the length block's; only the
    call site is earlier, per B-29's requirement that the budget criterion
    stay first in the report.

    Unevaluable (``None``) under any of B-19's four conditions: no
    calendar evidence, no logged trial anywhere in the chain, VIF
    ineligible, or SR <= 0. ``None`` here means B-19's REFUSED-PREDICATE
    branch, never a permissive default.
    """
    if oos_index is None or len(oos_index) < 2:
        return None
    if fam.n_logged == 0:
        return None
    if not vif_res.eligible:
        return None
    if not (sr_ann > 0):
        return None
    idx = pd.to_datetime(oos_index)
    years_calendar = (idx.max() - idx.min()).days / 365.25
    if years_calendar <= 0:
        return None
    n_max_iid = stats.max_admissible_trials(
        years_calendar, sr_ann, periods_per_year, vif=1.0)
    n_max_serial = stats.max_admissible_trials(
        years_calendar, sr_ann, periods_per_year, vif=vif_res.vif_gate)
    return min(n_max_iid, n_max_serial)


def _budget_extension_ledger(registry, family, own_times, n_max, declared_ceiling_base):
    """Processes every ``trial_budget_extension`` event logged for
    ``family`` into an admissibility ledger.

    Returns ``(ledger, malformed)``: ``ledger`` is a list of dicts, one
    per extension event in creation order, carrying B-27's report shape
    plus ``effective_from`` (B-12, ``None`` where never admitted) and
    ``increment_admitted``. ``malformed`` is the ``(event_id, reason)``
    list for events that FAIL the criterion outright (B-23), in event
    order.

    The claimed timestamp inside ``detail`` (``issued_utc`` / ``as_of`` /
    ``dated``, or any other caller-supplied field) is NEVER read here --
    only ``created_utc``, which ``TrialRegistry.log_event`` stamps from
    the system clock and which the API exposes no parameter to override
    (section 7.1's back-dating answer, B-9).
    """
    exts = registry.events(kind="trial_budget_extension", family=family)
    withdrawals = registry.events(
        kind="trial_budget_extension_withdrawn", family=family)
    countersigns = registry.events(
        kind="trial_budget_extension_countersigned", family=family)

    withdrawn_ids = {w["detail"].get("extension_event_id") for w in withdrawals}

    ledger: list[dict] = []
    malformed: list[tuple[int, str]] = []
    seen_refs: dict[str, int] = {}  # authorization_ref -> admitting event_id (B-26)
    contingent_queue: list[dict] = []

    for e in exts:
        eid = e["event_id"]
        detail = e["detail"]
        created = e["created_utc"]
        mode = detail.get("mode")
        row = {
            "event_id": eid, "mode": mode,
            "issuer": detail.get("issuer"), "countersigner": None,
            "increment_declared": detail.get("increment"),
            "increment_admitted": 0, "status": None,
            "effective_from": None, "created_utc": created,
            "authorization_ref": detail.get("authorization_ref"),
        }

        if eid in withdrawn_ids:
            # B-24: append-only repair. Inert -- no increment, no
            # malformation FAIL, regardless of what the event contained.
            row["status"] = _STATUS_WITHDRAWN
            ledger.append(row)
            continue

        reason = _validate_extension_schema(detail)
        if reason is None:
            # B-21: the events-table analogue of the hypothesis shadow
            # copy. A back-dated `created_utc` must also make the trial
            # ledger agree with a count the event declared about itself.
            n_before = sum(1 for t in own_times if t < created)
            declared_n = detail.get("n_logged_at_issue")
            if n_before != declared_n:
                reason = (
                    f"n_logged_at_issue cross-check failed: declared "
                    f"{declared_n}, actual own trials logged before this "
                    f"event's created_utc = {n_before} (B-21)"
                )
        if reason is not None:
            row["status"] = _STATUS_REFUSED_MALFORMED
            ledger.append(row)
            malformed.append((eid, reason))
            continue

        ref = row["authorization_ref"]
        if ref in seen_refs:
            malformed.append((eid, (
                f"authorization_ref {ref!r} already spent by extension "
                f"event_id {seen_refs[ref]} (B-26: one authorization "
                "artifact, one increment)"
            )))
            row["status"] = _STATUS_REFUSED_MALFORMED
            ledger.append(row)
            continue

        if mode == "DISCRETIONARY":
            issuer = detail.get("issuer")
            if issuer == "principal":
                # B-15: the Principal issues alone; no countersignature.
                row["status"] = _STATUS_ADMITTED
                row["increment_admitted"] = detail["increment"]
                row["effective_from"] = created
                seen_refs[ref] = eid
            elif issuer == "director-of-research":
                # B-14: a distinct-seat countersignature is required.
                own_counters = [
                    c for c in countersigns
                    if c["detail"].get("extension_event_id") == eid
                ]
                valid = [
                    c for c in own_counters
                    if c["detail"].get("countersigner") in _VALID_COUNTERSIGNERS
                    and c["detail"].get("countersigner") != issuer
                    and c["created_utc"] >= created
                ]
                if valid:
                    earliest = min(valid, key=lambda c: c["created_utc"])
                    row["status"] = _STATUS_ADMITTED
                    row["increment_admitted"] = detail["increment"]
                    row["countersigner"] = earliest["detail"].get("countersigner")
                    row["effective_from"] = max(created, earliest["created_utc"])
                    seen_refs[ref] = eid
                elif any(c["detail"].get("countersigner") == issuer for c in own_counters):
                    row["status"] = _STATUS_REFUSED_SELF_ISSUED
                else:
                    row["status"] = _STATUS_REFUSED_UNCOUNTERSIGNED
            else:
                # B-14's allow-list is exhaustive: an issuer that is
                # neither the Director nor the Principal has no route to
                # admission -- refusal, never a schema MALFORMED (B-4:
                # this can only tighten, so it is disclosed, not failed).
                row["status"] = _STATUS_REFUSED_UNCOUNTERSIGNED
        else:  # CONTINGENT
            # B-16: authorized by a recomputation, never by the event's
            # own claim -- self-issuance is harmless by construction, so
            # no countersignature is required or consulted.
            row["effective_from"] = created
            seen_refs[ref] = eid
            contingent_queue.append(row)

        ledger.append(row)

    # B-20: the aggregate cap on CONTINGENT increments, consumed in
    # creation order -- reusing `contingent_increment_allowed` with a
    # running base is exactly B-18's clamp applied to "what remains".
    cumulative = 0
    for row in contingent_queue:
        if n_max is None:
            # B-19: unevaluable is never permissive.
            row["status"] = _STATUS_REFUSED_PREDICATE
            row["increment_admitted"] = 0
            continue
        admitted = contingent_increment_allowed(
            n_max, declared_ceiling_base + cumulative, row["increment_declared"])
        row["increment_admitted"] = admitted
        cumulative += admitted
        row["status"] = (
            _STATUS_ADMITTED if admitted == row["increment_declared"] and admitted > 0
            else _STATUS_CAPPED
        )

    return ledger, malformed


def _trial_budget_criterion(fam, registry, family, sr_ann, periods_per_year,
                            vif_res, oos_index):
    """VALIDATION-SPEC-003 B-1 .. B-31, RULING 003-A -- the trial-count
    criterion. Returns ``(Criterion, report_fields)`` where
    ``report_fields`` is B-27's dict of NEW ``ValidationReport`` fields
    (``trial_budget_sealed`` / ``trial_budget_effective`` / ``n_own_logged``
    / ``budget_extensions``) -- report fields, not Criterion rows
    (M-10 / E-10's precedent, guarded by ``test_hac_t14``).
    """
    name = "Trial count N (registry)"

    if fam.n_logged == 0:
        # B-8, first sentence: UNCHANGED (H-10/H-11), keyed on the
        # chain-summed figure -- this branch predates this document and
        # is not touched by it.
        if fam.n_inherited:
            note = (
                f"No trials logged for this family (logged=0); "
                f"n_inherited={fam.n_inherited} is a declared seed, not "
                "a substitute for a real, run trial — seeding must not "
                "paper over a family that has run nothing (H-11)."
            )
        else:
            note = ("No trials logged for this family. If N is "
                    "unreconstructable, the verdict is "
                    "INSUFFICIENT-DATA, never PASS.")
        crit = Criterion(name, fam.n_trials, ">= 1 logged trial", INSUFF, note)
        fields = dict(
            trial_budget_sealed=fam.trial_budget,
            trial_budget_effective=fam.trial_budget,
            n_own_logged=0, budget_extensions=[])
        return crit, fields

    own_times = sorted(registry.own_trial_times(family))
    m = len(own_times)
    sealed = fam.trial_budget

    n_max = _admissible_ceiling(oos_index, fam, sr_ann, periods_per_year, vif_res)
    declared_ceiling_base = fam.n_inherited + sealed
    ledger, malformed = _budget_extension_ledger(
        registry, family, own_times, n_max, declared_ceiling_base)

    total_admitted = sum(row["increment_admitted"] for row in ledger)
    eff_final = sealed + total_admitted

    threshold = f"own-family logged <= effective budget {eff_final} (sealed {sealed}"
    threshold += f" + {total_admitted} extension)" if total_admitted else ")"

    chain_suffix = f"chain-summed logged {fam.n_logged}" if fam.n_logged != m else ""

    def _finish(verdict: str, note: str) -> Criterion:
        if chain_suffix:
            # B-25: the disclosed residual (I-101) -- visible on every
            # report where the predecessor chain out-spent the successor,
            # rather than tracked only in a memo.
            note = (note + "; " if note else "") + chain_suffix
        return Criterion(name, fam.n_trials, threshold, verdict, note)

    if malformed:
        # B-23: absolute, even where comfortably inside the sealed
        # budget -- checked ahead of B-7/B-8/B-9, all of which describe a
        # WELL-FORMED registry state.
        detail_str = "; ".join(f"event_id {eid}: {reason}" for eid, reason in malformed)
        crit = _finish(FAIL, f"MALFORMED AUTHORIZATION: {detail_str}")
    elif m == 0:
        # B-8, second sentence: the chain has logged trials but this
        # family has none of its own -- vacuously within budget.
        crit = _finish(PASS, "")
    elif sealed <= 0:
        # B-7 / I-100: the `and` short-circuit this replaces disabled
        # this branch entirely. Unconditional -- no extension buys a
        # family out of "pre-registered no authorization."
        crit = _finish(FAIL, (
            f"NO AUTHORIZED BUDGET: sealed trial_budget={sealed} with "
            f"{m} own logged trial(s)."
        ))
    else:
        # B-9: the ordering walk, per trial, not per aggregate.
        violation_k = violation_eff = None
        for k, t_k in enumerate(own_times, start=1):
            eff_tk = sealed + sum(
                row["increment_admitted"] for row in ledger
                if row["effective_from"] is not None and row["effective_from"] <= t_k
            )
            if k > eff_tk:
                violation_k, violation_eff = k, eff_tk
                break
        if violation_k is not None:
            crit = _finish(FAIL, (
                f"OVER BUDGET: trial {violation_k} of {m} was logged when "
                f"the effective budget was {violation_eff} (sealed {sealed})"
            ))
        else:
            crit = _finish(PASS, "")

    fields = dict(
        trial_budget_sealed=sealed,
        trial_budget_effective=eff_final,
        n_own_logged=m,
        budget_extensions=[
            {
                "event_id": row["event_id"], "mode": row["mode"],
                "issuer": row["issuer"], "countersigner": row["countersigner"],
                "increment_declared": row["increment_declared"],
                "increment_admitted": row["increment_admitted"],
                "status": row["status"], "created_utc": row["created_utc"],
                "authorization_ref": row["authorization_ref"],
            }
            for row in ledger
        ],
    )
    return crit, fields


def evaluate_gate1(
    strategy: str,
    family: str,
    registry: TrialRegistry,
    oos_net_returns: np.ndarray,
    periods_per_year: int,
    *,
    backtest_years: float,
    oos_index: "pd.DatetimeIndex | None" = None,
    net_returns_at_cost_multiplier=None,
    wfe_sr_pairs: list[tuple[float, float]] | None = None,
    param_grid_net_pnls: list[float] | None = None,
    capacity_multiple: float | None = None,
    corr_to_live_book: float | None = None,
    red_team_memo_present: bool = False,
    kill_condition: str | None = None,
    label_span: int = 1,
) -> ValidationReport:
    """Evaluate Gate 1. One non-PASS criterion fails the Gate.

    Parameters
    ----------
    oos_net_returns : out-of-sample net returns (post-cost), per bar.
    backtest_years : REQUIRED (I-010 G1). No fallback to
        ``r.size / periods_per_year`` exists any more — that fallback
        silently equated observation count with calendar span, which
        overstates length for any stacked/pooled panel (rows = contract-
        days, not dates) and fails permissively toward PASS. The caller
        must state the length; :paramref:`oos_index` is what lets the
        harness check the caller's claim instead of trusting it.
    oos_index : the OOS return series' DatetimeIndex, if available (G2).
        Where supplied, ``years_calendar = (max - min).days / 365.25`` is
        computed and is what the length criterion is actually evaluated
        against; ``backtest_years`` is reported alongside it and checked
        for disagreement (G3). Where NOT supplied, the length criterion is
        INSUFFICIENT-DATA — never PASS — regardless of what
        ``backtest_years`` claims (G4): a number the harness cannot verify
        does not clear a Charter §4.4 floor.
    net_returns_at_cost_multiplier : callable m -> net returns with all
        costs scaled by m (rerun through the engine). Used for the 2x
        robustness test and the breakeven cost search. If None, both are
        INSUFFICIENT-DATA.
    wfe_sr_pairs : list of (sr_is, sr_oos) from >= 10 walk-forward windows.
    param_grid_net_pnls : total net P&L for each point of the +/-50%
        parameter grid around the chosen configuration.
    capacity_multiple : estimated capacity / intended allocation.
    corr_to_live_book : correlation of strategy returns to any live pod
        strategy (max absolute).
    label_span : bars over which each observation's label is realized
        (VALIDATION-SPEC-001 E-11). Floors the HAC lag at
        ``label_span - 1``; NOT read from the registry (I-052 would add
        that field; the Andrews floor means an undeclared label span
        degrades to the data-driven lag, never to zero).
    """
    r = np.asarray(oos_net_returns, dtype=float)
    r = r[~np.isnan(r)]
    sha = hashlib.sha256(r.tobytes()).hexdigest()

    fam = registry.family_stats(family)
    criteria: list[Criterion] = []

    # -- performance/VIF, HOISTED (VALIDATION-SPEC-003 B-29) -----------
    # `sr_ann` and `vif_res` are computed here, ahead of their original
    # position further down, because the trial-budget criterion's
    # CONTINGENT-extension arithmetic (B-16 .. B-20) needs both to
    # recompute N_max BEFORE it can grade -- and B-29 requires that
    # criterion to remain FIRST in `report.criteria` (a Gate report is
    # read budget-first, since N is the denominator of everything below
    # it). This is a hoist, not a duplicate: the "core performance" and
    # "VIF, measured once" sections below now just APPEND using these
    # same values -- the formula and its inputs are computed exactly
    # once each.
    sr_ann = stats.sharpe_annual(r, periods_per_year)
    # M-7 / R-11: n_logged == 0 means no logged trial carries a return
    # series, so the family's serial dependence is unmeasurable. There
    # is no fallback to VIF=1 -- the permissive assumption this document
    # exists to remove -- so the candidate is deliberately withheld too,
    # forcing the "unmeasurable" branch rather than a candidate-only
    # measurement for a family that has run nothing.
    if fam.n_logged == 0:
        vif_res = stats.family_variance_inflation([], None, label_span=label_span)
    else:
        vif_res = stats.family_variance_inflation(
            registry.trial_returns(family), r, label_span=label_span)

    # -- multiple-testing inputs from the registry --------------------
    # H-10 / H-11 (Gate 0 001 §3, F-3/F-4): the fam.n_logged == 0 branch
    # inside `_trial_budget_criterion` keys on `n_logged` — the real,
    # run-trial count — not `n_trials`, which after seeding (H1-H2)
    # includes the declared `n_inherited` and no longer means "trials
    # this family has actually run." Keying on n_trials there would make
    # (a) every seeded family read OVER BUDGET on seeding alone (the
    # budget governs the firm's post-seal search; inherited trials are
    # not post-seal search), and (b) a seeded family with zero logged
    # trials never reach the "run nothing" guard, silently converting
    # "this family has never run anything" into a fully populated
    # denominator (I-014's shape). VALIDATION-SPEC-003 B-1 .. B-31,
    # RULING 003-A: I-022's substantive fix. `over` used to be computed
    # and used only to write a note; the verdict argument was the
    # literal `True`.
    n_ok = fam.n_logged >= 1 and fam.sr_period_std is not None
    trial_budget_crit, trial_budget_fields = _trial_budget_criterion(
        fam, registry, family, sr_ann, periods_per_year, vif_res, oos_index)
    criteria.append(trial_budget_crit)

    # -- core performance ---------------------------------------------
    criteria.append(_crit("Net Sharpe (OOS, annualized)", sr_ann,
                          f">= {NET_SHARPE_MIN}", sr_ann >= NET_SHARPE_MIN))

    # -- t-statistic, HAC-corrected (VALIDATION-SPEC-001 E-11, I-050) ---
    # E-11: the graded criterion is the corrected estimator's t_gate =
    # min(t_nw, t_raw) (E-8's non-permissive floor). The uncorrected
    # figure is reported (E-10) but is NEVER a Criterion row (E-10 /
    # guarded by test_hac_t14).
    hac = stats.sr_tstat_corrected(r, label_span=label_span)
    hac_note_base = f"uncorrected t = {hac.t_raw:.3f}, inflation {hac.inflation:.2f}×"
    hac_note = (f"{hac.note}; {hac_note_base}" if (not hac.eligible and hac.note)
                else hac_note_base)
    if not hac.eligible:
        t_verdict = INSUFF
    elif hac.t_gate >= T_STAT_HURDLE:
        t_verdict = PASS
    else:
        t_verdict = FAIL
    criteria.append(Criterion(
        "t-statistic (net, HAC-corrected)", hac.t_gate, f">= {T_STAT_HURDLE}",
        t_verdict, hac_note))

    # -- VIF, measured once (VALIDATION-SPEC-002 D-7: one VIF, three
    # consumers -- the t-statistic above via hac.inflation, DSR below,
    # and the length criterion further down). Computed above, hoisted
    # ahead of the trial-budget criterion (VALIDATION-SPEC-003 B-29). --

    # -- DSR (VALIDATION-SPEC-002 D-1 .. D-10) --------------------------
    dsr_iid_val: float | None = None
    dsr_serial_val: float | None = None
    t_eff_val: float | None = None
    if n_ok and fam.n_trials >= 2:
        dsr_iid_val = stats.deflated_sharpe_ratio(r, fam.n_trials, fam.sr_period_std)
        if not vif_res.eligible:
            criteria.append(Criterion(
                "Deflated Sharpe Ratio", dsr_iid_val,
                f">= {DSR_MIN}", INSUFF,
                f"VIF unmeasurable or ineligible ({vif_res.note or vif_res.source}); "
                f"DSR(iid) = {dsr_iid_val:.4f}" if not math.isnan(dsr_iid_val)
                else f"VIF unmeasurable or ineligible ({vif_res.note or vif_res.source})"))
        else:
            dsr_serial_val = stats.deflated_sharpe_ratio_serial(
                r, fam.n_trials, fam.sr_period_std, vif=vif_res.vif_gate)
            t_eff_val = stats.effective_sample_size(r.size, vif_res.vif_gate)
            dsr_note = (
                f"DSR(iid) = {dsr_iid_val:.4f}, VIF = {vif_res.vif_gate:.3f}, "
                f"T_eff = {t_eff_val:.0f}")
            criteria.append(_crit(
                "Deflated Sharpe Ratio", dsr_serial_val,
                f">= {DSR_MIN}",
                None if math.isnan(dsr_serial_val) else dsr_serial_val >= DSR_MIN,
                dsr_note))
    else:
        criteria.append(Criterion(
            "Deflated Sharpe Ratio", None, f">= {DSR_MIN}", INSUFF,
            "Needs >= 2 registry trials for cross-sectional SR dispersion"))

    # -- PBO via CSCV ---------------------------------------------------
    M = registry.returns_matrix(family)
    if M.size and M.shape[1] >= 2 and M.shape[0] >= CSCV_PARTITIONS_S * 2:
        pbo = stats.probability_backtest_overfitting(M, CSCV_PARTITIONS_S)
        # H-9: CSCV requires a return series; phantom (seeded) trials
        # have none, so PBO is structurally undeflated by n_inherited —
        # a permanent limit of the seeding fix, not a bug. Stated on the
        # criterion's face whenever this family is seeded, so an N in
        # the tens of thousands next to a PBO computed on a handful of
        # real columns cannot mislead by omission.
        pbo_note = ""
        if fam.n_inherited:
            pbo_note = (
                f"Computed on {M.shape[1]} logged trial(s) with real "
                f"return series; the {fam.n_inherited:,} declared "
                "inherited trial(s) have no return series and "
                "contribute none to this criterion."
            )
        criteria.append(_crit(
            f"PBO (CSCV, S={CSCV_PARTITIONS_S}, {pbo.n_combinations} splits)",
            pbo.pbo, f"<= {PBO_MAX_PAPER}", pbo.pbo <= PBO_MAX_PAPER, pbo_note))
    else:
        criteria.append(Criterion(
            "PBO (CSCV)", None, f"<= {PBO_MAX_PAPER}", INSUFF,
            "Registry return matrix too small for S=16 CSCV"))

    # -- length (I-010 G1-G5; VALIDATION-SPEC-002 M-6/M-7) ---------------
    # G1: backtest_years is required, no fallback. G2/G3/G4: oos_index is
    # the only thing that lets the harness VERIFY the caller's claim
    # instead of trusting it — the permissive fallback this replaced
    # (r.size / periods_per_year) silently equated observation count with
    # calendar span, which overstates length for a stacked/pooled panel.
    # M-6: renamed and rebuilt on the serial-corrected MinBTL. M-7:
    # n_logged == 0 makes this criterion INSUFFICIENT-DATA -- keying on
    # fam.n_trials (which n_inherited alone can satisfy) would silently
    # reinstate VIF = 1 for exactly the families with the least evidence.
    # NOTE (see DATA-IMPL-006 sec. "M-6/D-8 naming conflict"): M-6 specifies
    # this criterion's name as "Backtest length (years, serial-corrected
    # MinBTL)". That verbatim rename is NOT applied -- pre-existing,
    # protected acceptance tests (test_holdout_p1.py G2-G5) key on the
    # EXACT string "Backtest length (years)" and would break for zero
    # offsetting benefit (test_mbs_10, the only SPEC-002 test that checks
    # for "serial" in this name, fails regardless on an independent,
    # already-escalated defect in its own fixture -- see the dispatch
    # issue log). The "serial-corrected" signal is still carried on the
    # criterion's threshold string and note (both required by M-6/M-10).
    # Escalated to Validation for a ruling; not decided silently.
    crit_name = "Backtest length (years)"
    length_threshold = f">= max({MIN_YEARS:g}, MinBTL_serial(N))"

    minbtl_iid_years_val: float | None = None
    if fam.n_trials >= 1:
        minbtl_iid_years_val = stats.min_backtest_length_years(
            max(fam.n_trials, 2), sr_ann, periods_per_year)

    minbtl_serial_years_val: float | None = None
    n_max_admissible_iid_val: int | None = None
    n_max_admissible_serial_val: int | None = None

    if oos_index is None or len(oos_index) < 2:
        # G4: no calendar evidence -> INSUFFICIENT-DATA, never PASS,
        # regardless of what backtest_years claims. Checked BEFORE M-7's
        # n_logged==0 gate: a missing calendar span is a more fundamental
        # data-integrity problem than an unmeasured VIF, and G3/G4/G5's
        # priority over the trial-history gate is unchanged by this spec.
        criteria.append(Criterion(
            crit_name, backtest_years, length_threshold, INSUFF,
            "No oos_index supplied; calendar span unavailable, so "
            f"backtest_years={backtest_years:g} cannot be verified and "
            "cannot clear a Charter 4.4 floor on trust alone."))
    else:
        idx = pd.to_datetime(oos_index)
        span_days = (idx.max() - idx.min()).days
        years_calendar = span_days / 365.25
        disagreement = (
            abs(backtest_years - years_calendar) / years_calendar
            if years_calendar > 0 else float("inf")
        )
        if disagreement > LENGTH_DISAGREEMENT_MAX:
            # G3: the pooled-panel signature — apparent length (usually
            # observation count / periods_per_year) materially overstates
            # or understates the calendar span. FAIL, not a note buried
            # in a PASS: a materially mis-stated length is a failure on a
            # Charter 4.4 criterion. Checked BEFORE M-7's n_logged==0
            # gate for the same reason as G4 above.
            criteria.append(_crit(
                crit_name, years_calendar, length_threshold, False,
                f"DISAGREEMENT: backtest_years={backtest_years:.3f} vs "
                f"calendar-verified={years_calendar:.3f} "
                f"({disagreement:.1%} apart, > {LENGTH_DISAGREEMENT_MAX:.0%} "
                "tolerance) — reported length does not match the oos_index "
                "calendar span (I-010)."))
        elif fam.n_logged == 0:
            # M-7: n_inherited alone (or nothing at all) carries no
            # return series -- MinBTL cannot be evaluated at an assumed
            # VIF = 1 (I-057).
            criteria.append(Criterion(
                crit_name, years_calendar, length_threshold, INSUFF,
                "No logged trial carries a return series; the family's "
                "serial dependence is unmeasurable and MinBTL cannot be "
                "evaluated at an assumed VIF = 1 (I-057). N unknown or "
                "unmeasurable ⇒ INSUFFICIENT-DATA, never PASS."))
        elif not vif_res.eligible:
            criteria.append(Criterion(
                crit_name, years_calendar, length_threshold, INSUFF,
                f"VIF unmeasurable or ineligible "
                f"({vif_res.note or vif_res.source}); MinBTL cannot be "
                "graded at an assumed VIF = 1 (I-057)."))
        elif sr_ann > 0:
            n_max_admissible_iid_val = stats.max_admissible_trials(
                years_calendar, sr_ann, periods_per_year, vif=1.0)
            n_max_admissible_serial_val = stats.max_admissible_trials(
                years_calendar, sr_ann, periods_per_year, vif=vif_res.vif_gate)
            n_max = min(n_max_admissible_iid_val, n_max_admissible_serial_val)  # M-5
            minbtl_serial_years_val = stats.min_backtest_length_years_serial(
                max(fam.n_trials, 2), sr_ann, periods_per_year, vif=vif_res.vif_gate)
            need = max(MIN_YEARS, minbtl_serial_years_val)
            criteria.append(_crit(
                crit_name, years_calendar,
                f">= max({MIN_YEARS:g}, MinBTL_serial="
                f"{minbtl_serial_years_val:.2f})",
                years_calendar >= need,
                f"MinBTL(iid) = {minbtl_iid_years_val:.2f}y; VIF = "
                f"{vif_res.vif_gate:.3f}; N_max = {n_max}"))
        else:
            criteria.append(_crit(
                crit_name, years_calendar, f">= {MIN_YEARS:g}",
                years_calendar >= MIN_YEARS,
                f"backtest_years (caller-reported): {backtest_years:.3f}; "
                "SR <= 0, MinBTL undefined (infinite)."))

    # -- holdout single-use (Ruling 001 E1-E3; fixes I-007) --------------
    # Family-scoped: `registry.events(kind=..., family=family)` — the
    # I-007 defect was that this was queried globally, so family A's
    # holdout events could satisfy or fail family B's criterion.
    #
    # Acceptance 001 C-6 (I-014): the caller-asserted `holdout_opened_once`
    # boolean is REMOVED, not deprecated. It measured PASS on a family with
    # zero holdout events in the registry — a narrated number inside the
    # firm's most-protected criterion. There is now exactly one way this
    # criterion can be evaluated: from the registry's own event log.
    acquired = registry.events(kind="holdout_acquired", family=family)
    second = registry.events(kind="holdout_second_acquisition_attempt", family=family)
    leaked = registry.events(kind="holdout_pre_acquisition_leak", family=family)
    bad_pw = registry.events(kind="holdout_bad_passphrase_attempt", family=family)
    retries = registry.events(kind="holdout_retry_authorized", family=family)
    notes = []
    if bad_pw:
        notes.append(f"{len(bad_pw)} bad-passphrase attempt(s)")
    if retries:
        notes.append(f"{len(retries)} retry authorization(s)")
    note_suffix = ("; " + "; ".join(notes)) if notes else ""

    if second:
        criteria.append(_crit(
            "Holdout single-use", "violated", "acquired exactly once",
            False,
            "Second-acquisition attempt logged — vault retired" + note_suffix))
    elif leaked:
        criteria.append(_crit(
            "Holdout single-use", "pre-acquisition leak", "acquired exactly once",
            False,
            "Rows in (C, G] were knowable before acquisition — holdout "
            "compromised (D1 leak-detection control)" + note_suffix))
    elif acquired:
        detail = acquired[-1]["detail"]
        window = detail.get("window_months")
        min_months = detail.get("holdout_min_months", HOLDOUT_MIN_MONTHS)
        if window is not None and window < min_months:
            criteria.append(_crit(
                "Holdout single-use",
                f"acquired, window {window:.1f}mo", f">= {min_months:g} months",
                False,
                "Holdout window below the Charter 4.4 minimum; the "
                "fact is known, so this is FAIL, not INSUFFICIENT-DATA"
                + note_suffix))
        else:
            criteria.append(_crit(
                "Holdout single-use", "acquired once", "acquired exactly once",
                True, note_suffix.lstrip("; ")))
    else:
        criteria.append(Criterion(
            "Holdout single-use", "not acquired", "acquired exactly once",
            INSUFF, "OOS evaluation requires the holdout to be acquired"
            + note_suffix))

    # -- pre-registration integrity (Acceptance 001 P4-P7; D-006 rider) --
    prereg = registry.verify_prereg(family)
    prereg_sha256 = prereg["sealed_sha256"]
    if not prereg["sealed"]:
        # P6: no hypothesis_sealed event (predates the P-series schema, or
        # a family inserted outside open_hypothesis) -> INSUFFICIENT-DATA,
        # never PASS.
        criteria.append(Criterion(
            "Pre-registration integrity", None,
            "sealed hash matches live row", INSUFF,
            "No hypothesis_sealed event for this family — the "
            "pre-registration was never sealed under the P-series, or "
            "predates it."))
    elif not prereg["match"]:
        # P4: a raw SQLite UPDATE (or any other out-of-band mutation) is
        # detected because the sealed event carries a full shadow copy,
        # not a pointer to the row that was just changed.
        criteria.append(_crit(
            "Pre-registration integrity",
            f"mismatch: {prereg['differing_fields']}",
            "sealed hash matches live row", False,
            "The live hypotheses row differs from the sealed "
            f"pre-registration on {prereg['differing_fields']}. This can "
            "only happen via a write outside open_hypothesis()."))
    else:
        # P7: the sealed timestamp must not postdate the holdout cutoff C,
        # at UTC day granularity — the D-006 rider mechanised.
        spec_events = registry.events(kind="holdout_spec_sealed", family=family)
        p7_fail, p7_note = False, ""
        if spec_events:
            cutoff_raw = spec_events[-1]["detail"].get("cutoff")
            if cutoff_raw:
                cutoff_day = pd.Timestamp(cutoff_raw)
                cutoff_day = (cutoff_day.tz_localize("UTC") if cutoff_day.tzinfo is None
                             else cutoff_day.tz_convert("UTC")).normalize()
                sealed_day = pd.Timestamp(
                    prereg["sealed_created_utc"], unit="s", tz="UTC"
                ).normalize()
                if sealed_day > cutoff_day:
                    p7_fail = True
                    p7_note = (
                        f"pre-registration sealed {sealed_day.date()} "
                        f"postdates the holdout cutoff C={cutoff_day.date()} "
                        "(D-006 rider: prereg must be sealed on or before "
                        "C's calendar day)"
                    )
        if p7_fail:
            criteria.append(_crit(
                "Pre-registration integrity", "sealed after C",
                "sealed on/before C's calendar day", False, p7_note))
        else:
            criteria.append(_crit(
                "Pre-registration integrity", "sealed, hash matches",
                "sealed hash matches live row", True))

    # P8: predecessor chain's sealed prereg hashes, for the report.
    predecessor_prereg_sha256: dict[str, str] = {}
    for pred_fam in registry.predecessor_chain(family):
        pv = registry.verify_prereg(pred_fam)
        if pv["sealed"]:
            predecessor_prereg_sha256[pred_fam] = pv["sealed_sha256"]

    # R1: FORWARD / HISTORICAL classification, required on the report's
    # face (Ruling 001 §2.4 / Ruling 002 R1).
    hyp_row = registry.hypothesis(family)
    holdout_classification = hyp_row.get("holdout_classification") if hyp_row else None

    # -- walk-forward ---------------------------------------------------
    if wfe_sr_pairs is not None and len(wfe_sr_pairs) >= WFE_MIN_WINDOWS:
        wfe = stats.walk_forward_efficiency(wfe_sr_pairs)
        criteria.append(_crit(
            f"Walk-Forward Efficiency ({len(wfe_sr_pairs)} windows)", wfe,
            f">= {WFE_MIN}", None if math.isnan(wfe) else wfe >= WFE_MIN))
    else:
        criteria.append(Criterion(
            "Walk-Forward Efficiency", None,
            f">= {WFE_MIN} across >= {WFE_MIN_WINDOWS} windows", INSUFF))

    # -- subperiod positivity & concentration --------------------------
    pos = stats.subperiod_positivity(r, 8)
    criteria.append(_crit("Subperiod positivity (8 blocks)", pos,
                          f">= {SUBPERIOD_POSITIVITY_MIN}",
                          pos >= SUBPERIOD_POSITIVITY_MIN))

    conc = stats.pnl_concentration(r, bars_per_month=max(1, periods_per_year // 12))
    ok_conc = (conc["max_day_share"] <= MAX_DAY_SHARE
               and conc["max_month_share"] <= MAX_MONTH_SHARE)
    criteria.append(_crit(
        "P&L concentration",
        f"day {conc['max_day_share']:.1%} / month {conc['max_month_share']:.1%}",
        f"day <= {MAX_DAY_SHARE:.0%}, month <= {MAX_MONTH_SHARE:.0%}", ok_conc))

    # -- parameter surface ----------------------------------------------
    if param_grid_net_pnls:
        frac = float(np.mean(np.asarray(param_grid_net_pnls) > 0))
        criteria.append(_crit(
            f"Parameter surface ({len(param_grid_net_pnls)} grid points)",
            frac, f">= {PARAM_SURFACE_MIN_PROFITABLE:.0%} net-profitable",
            frac >= PARAM_SURFACE_MIN_PROFITABLE))
    else:
        criteria.append(Criterion("Parameter surface", None,
                                  f">= {PARAM_SURFACE_MIN_PROFITABLE:.0%} of ±50% grid",
                                  INSUFF))

    # -- cost robustness & breakeven, HAC-corrected (E-12/E-13/E-14) ----
    # The lag is selected ONCE, on the base OOS series (`hac.lag`, from
    # the criterion above), and held fixed across both the 2x-costs
    # criterion and the breakeven bisection. Re-selecting it at every
    # sweep point would make t a step function of the swept parameter
    # and destroy the monotonicity the bisection relies on (I-037 /
    # Ruling 003) — the exact failure E-13 exists to prevent.
    breakeven = None
    if net_returns_at_cost_multiplier is not None:
        r2 = np.asarray(net_returns_at_cost_multiplier(2.0), dtype=float)
        t2 = stats.sr_tstat_nw(r2[~np.isnan(r2)], hac.lag)
        criteria.append(_crit(
            "t-stat at 2× costs (HAC-corrected)", t2, f">= {T_STAT_HURDLE}",
            t2 >= T_STAT_HURDLE))
        # bisect the breakeven multiplier in [1, 32] on the HAC statistic
        lo, hi = 1.0, 32.0
        t_lo = stats.sr_tstat_nw(np.asarray(net_returns_at_cost_multiplier(lo)), hac.lag)
        if t_lo < T_STAT_HURDLE:
            breakeven = lo
        else:
            for _ in range(24):
                mid = 0.5 * (lo + hi)
                tm = stats.sr_tstat_nw(np.asarray(net_returns_at_cost_multiplier(mid)), hac.lag)
                if tm >= T_STAT_HURDLE:
                    lo = mid
                else:
                    hi = mid
            breakeven = lo
    else:
        criteria.append(Criterion("t-stat at 2× costs (HAC-corrected)", None,
                                  f">= {T_STAT_HURDLE}", INSUFF,
                                  "Provide a cost-multiplier rerun callable"))

    # -- capacity, correlation, red team --------------------------------
    criteria.append(_crit("Capacity multiple", capacity_multiple,
                          f">= {CAPACITY_MULTIPLE_MIN}×",
                          None if capacity_multiple is None
                          else capacity_multiple >= CAPACITY_MULTIPLE_MIN))
    criteria.append(_crit("|corr| to live book", corr_to_live_book,
                          f"<= {CORR_MAX_TO_LIVE_BOOK}",
                          None if corr_to_live_book is None
                          else abs(corr_to_live_book) <= CORR_MAX_TO_LIVE_BOOK))
    criteria.append(_crit(
        "Red-Team Memo with binding kill condition",
        "present" if (red_team_memo_present and kill_condition) else "absent",
        "required",
        bool(red_team_memo_present and kill_condition)))

    overall = PASS if all(c.verdict == PASS for c in criteria) else (
        FAIL if any(c.verdict == FAIL for c in criteria) else INSUFF)

    # E3: embed the spec hash and acquired-payload hash, family-scoped,
    # alongside the returns sha256 — so a report can be audited against
    # exactly what Validation evaluated even though the holdout plaintext
    # itself is never in the repo.
    sealed_events = registry.events(kind="holdout_spec_sealed", family=family)
    acquired_events = registry.events(kind="holdout_acquired", family=family)
    holdout_spec_sha256 = sealed_events[-1]["detail"].get("spec_sha256") if sealed_events else None
    holdout_payload_sha256 = acquired_events[-1]["detail"].get("payload_sha256") if acquired_events else None

    # -- VALIDATION-SPEC-004 R-15: the write-grant audit, on the face of
    # every report, whether or not it fires. A control that is only
    # visible when it fires is one nobody can confirm is running (§4.7.4
    # (ii)) — this prints on EVERY invocation, including the all-zero
    # case, and the same numbers are on the report object.
    wg_audit = registry.audit_write_grants()
    wg_orphan_counts = {k: len(v) for k, v in wg_audit["orphan_rows"].items()}
    wg_provenance_broken = (
        any(wg_orphan_counts.values())
        or not wg_audit["chain_intact"]
        or bool(wg_audit["unclosed_grants"])
    )
    print(
        "[evaluate_gate1] write-grant audit — "
        f"chain_head={wg_audit['chain_head'][:16]}... "
        f"chain_intact={wg_audit['chain_intact']} "
        f"n_grants={wg_audit['n_grants']} "
        f"unclosed={wg_audit['unclosed_grants']} "
        f"orphans={wg_orphan_counts}"
    )

    # -- VALIDATION-SPEC-004 E-24: the dated-clause evaluator's Gate
    # teeth. Runs for the family under evaluation on every invocation; a
    # nonzero exit makes the Gate verdict INSUFFICIENT-DATA and the
    # evaluator's full finding table is reproduced on the report,
    # unfiltered.
    from .dated_clauses import evaluate_dated_clauses
    dce_report = evaluate_dated_clauses(registry, family=family)
    dated_clause_exit_code = dce_report.exit_code
    dated_clause_render = dce_report.render()
    print(f"[evaluate_gate1] dated-clause evaluator — exit={dated_clause_exit_code}")
    print(dated_clause_render)

    if wg_provenance_broken or dated_clause_exit_code != 0:
        overall = INSUFF

    report = ValidationReport(
        strategy=strategy,
        family=family,
        date_utc=time.time(),
        n_trials=fam.n_trials,
        trial_budget=fam.trial_budget,
        sr_std_period_trials=fam.sr_period_std,
        criteria=criteria,
        overall=overall,
        returns_sha256=sha,
        breakeven_cost_multiplier=breakeven,
        holdout_spec_sha256=holdout_spec_sha256,
        holdout_payload_sha256=holdout_payload_sha256,
        holdout_classification=holdout_classification,
        prereg_sha256=prereg_sha256,
        predecessor_prereg_sha256=predecessor_prereg_sha256 or None,
        t_stat_uncorrected=hac.t_raw,
        t_stat_hac=hac.t_nw,
        hac_lag=hac.lag,
        hac_lag_rule=hac.lag_rule,
        hac_rho_hat=hac.rho_hat,
        n_inherited=fam.n_inherited,
        n_logged=fam.n_logged,
        minbtl_iid_years=minbtl_iid_years_val,
        minbtl_serial_years=minbtl_serial_years_val,
        vif_gate=vif_res.vif_gate,
        vif_hac=vif_res.vif_hac,
        vif_ar1=vif_res.vif_ar1,
        vif_rho_hat=vif_res.rho_hat,
        n_max_admissible_iid=n_max_admissible_iid_val,
        n_max_admissible_serial=n_max_admissible_serial_val,
        dsr_iid=dsr_iid_val,
        dsr_serial=dsr_serial_val,
        t_eff=t_eff_val,
        vif_source=vif_res.source,
        vif_n_series_used=vif_res.n_series_used,
        trial_budget_sealed=trial_budget_fields["trial_budget_sealed"],
        trial_budget_effective=trial_budget_fields["trial_budget_effective"],
        n_own_logged=trial_budget_fields["n_own_logged"],
        budget_extensions=trial_budget_fields["budget_extensions"],
        write_grant_chain_head=wg_audit["chain_head"],
        write_grant_chain_intact=wg_audit["chain_intact"],
        write_grant_orphan_rows=wg_orphan_counts,
        dated_clause_exit_code=dated_clause_exit_code,
        dated_clause_render=dated_clause_render,
    )
    # VALIDATION-SPEC-004: self-granted so pre-existing callers of
    # evaluate_gate1 (which hold no grant of their own) keep working —
    # see HoldoutVault._grant_log's docstring for the same reasoning.
    with registry.write_grant(
        reason="GATE_VERDICT", dispatch="gates.evaluate_gate1",
        token=HARNESS_INTERNAL_TOKEN,
    ):
        registry.log_event("gate1_verdict", family, {
            "strategy": strategy, "overall": overall,
            "n_trials": fam.n_trials, "returns_sha256": sha,
        })
    return report
