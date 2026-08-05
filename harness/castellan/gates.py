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
from .registry import TrialRegistry

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
        if self.breakeven_cost_multiplier is not None:
            lines.append("")
            lines.append(
                f"Breakeven cost multiplier (t falls below {T_STAT_HURDLE:g}): "
                f"**{self.breakeven_cost_multiplier:.2f}×** modelled costs."
            )
        lines += ["", f"## Overall verdict: **{self.overall}**", ""]
        fails = [c for c in self.criteria if c.verdict != PASS]
        if fails:
            lines.append("Non-passing criteria: " + ", ".join(c.name for c in fails))
        return "\n".join(lines)


def _crit(name, value, threshold, ok: bool | None, note="") -> Criterion:
    if ok is None:
        return Criterion(name, value, threshold, INSUFF, note)
    return Criterion(name, value, threshold, PASS if ok else FAIL, note)


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

    # -- multiple-testing inputs from the registry --------------------
    # H-10 / H-11 (Gate 0 001 §3, F-3/F-4): both guards below key on
    # `n_logged` — the real, run-trial count — not `n_trials`, which
    # after seeding (H1-H2) includes the declared `n_inherited` and no
    # longer means "trials this family has actually run." Keying on
    # n_trials here would make (a) every seeded family read OVER BUDGET
    # on seeding alone (the budget governs the firm's post-seal search;
    # inherited trials are not post-seal search), and (b) a seeded
    # family with zero logged trials never reach the "run nothing"
    # guard, silently converting "this family has never run anything"
    # into a fully populated denominator (I-014's shape).
    n_ok = fam.n_logged >= 1 and fam.sr_period_std is not None
    if fam.n_logged == 0:
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
        criteria.append(Criterion(
            "Trial count N (registry)", fam.n_trials, ">= 1 logged trial",
            INSUFF, note))
    else:
        over = fam.trial_budget and fam.n_logged > fam.trial_budget
        criteria.append(_crit(
            "Trial count N (registry)", fam.n_trials,
            f"logged; budget {fam.trial_budget}", True,
            "OVER BUDGET — flagged to Director of Research" if over else ""))

    # -- core performance ---------------------------------------------
    sr_ann = stats.sharpe_annual(r, periods_per_year)
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

    # -- DSR -----------------------------------------------------------
    if n_ok and fam.n_trials >= 2:
        dsr = stats.deflated_sharpe_ratio(r, fam.n_trials, fam.sr_period_std)
        criteria.append(_crit("Deflated Sharpe Ratio", dsr, f">= {DSR_MIN}",
                              None if math.isnan(dsr) else dsr >= DSR_MIN))
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

    # -- length (I-010 G1-G5) --------------------------------------------
    # G1: backtest_years is required, no fallback. G2/G3/G4: oos_index is
    # the only thing that lets the harness VERIFY the caller's claim
    # instead of trusting it — the permissive fallback this replaced
    # (r.size / periods_per_year) silently equated observation count with
    # calendar span, which overstates length for a stacked/pooled panel.
    length_threshold = f">= max({MIN_YEARS:g}, MinBTL(N))"
    if oos_index is None or len(oos_index) < 2:
        # G4: no calendar evidence -> INSUFFICIENT-DATA, never PASS,
        # regardless of what backtest_years claims.
        criteria.append(Criterion(
            "Backtest length (years)", backtest_years, length_threshold, INSUFF,
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
            # Charter 4.4 criterion.
            criteria.append(_crit(
                "Backtest length (years)", years_calendar, length_threshold, False,
                f"DISAGREEMENT: backtest_years={backtest_years:.3f} vs "
                f"calendar-verified={years_calendar:.3f} "
                f"({disagreement:.1%} apart, > {LENGTH_DISAGREEMENT_MAX:.0%} "
                "tolerance) — reported length does not match the oos_index "
                "calendar span (I-010)."))
        elif fam.n_trials >= 1 and sr_ann > 0:
            minbtl = stats.min_backtest_length_years(
                max(fam.n_trials, 2), sr_ann, periods_per_year)
            need = max(MIN_YEARS, minbtl)
            criteria.append(_crit(
                "Backtest length (years)", years_calendar,
                f">= max({MIN_YEARS:g}, MinBTL={minbtl:.2f})",
                years_calendar >= need,
                f"backtest_years (caller-reported): {backtest_years:.3f}"))
        else:
            criteria.append(_crit(
                "Backtest length (years)", years_calendar,
                f">= {MIN_YEARS:g}", years_calendar >= MIN_YEARS,
                f"backtest_years (caller-reported): {backtest_years:.3f}"))

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
    )
    registry.log_event("gate1_verdict", family, {
        "strategy": strategy, "overall": overall,
        "n_trials": fam.n_trials, "returns_sha256": sha,
    })
    return report
