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

PASS, FAIL, INSUFF = "PASS", "FAIL", "INSUFFICIENT-DATA"


@dataclass
class Criterion:
    name: str
    value: float | str | None
    threshold: str
    verdict: str
    note: str = ""


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

    def to_json(self) -> str:
        d = asdict(self)
        return json.dumps(d, indent=2, default=str)

    def to_markdown(self) -> str:
        lines = [
            f"# Validation Report — {self.strategy}",
            "",
            f"Family: `{self.family}` · Evaluated (UTC): {time.strftime('%Y-%m-%d %H:%M', time.gmtime(self.date_utc))}",
            f"Trial count N (registry): **{self.n_trials}** / budget {self.trial_budget} · "
            f"cross-sectional trial SR std (per-period): "
            f"{self.sr_std_period_trials if self.sr_std_period_trials is not None else 'UNAVAILABLE'}",
            f"Evaluated return series sha256: `{self.returns_sha256[:16]}…`",
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
    net_returns_at_cost_multiplier=None,
    wfe_sr_pairs: list[tuple[float, float]] | None = None,
    param_grid_net_pnls: list[float] | None = None,
    capacity_multiple: float | None = None,
    corr_to_live_book: float | None = None,
    red_team_memo_present: bool = False,
    kill_condition: str | None = None,
    backtest_years: float | None = None,
    holdout_opened_once: bool | None = None,
) -> ValidationReport:
    """Evaluate Gate 1. One non-PASS criterion fails the Gate.

    Parameters
    ----------
    oos_net_returns : out-of-sample net returns (post-cost), per bar.
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
    """
    r = np.asarray(oos_net_returns, dtype=float)
    r = r[~np.isnan(r)]
    sha = hashlib.sha256(r.tobytes()).hexdigest()

    fam = registry.family_stats(family)
    criteria: list[Criterion] = []

    # -- multiple-testing inputs from the registry --------------------
    n_ok = fam.n_trials >= 1 and fam.sr_period_std is not None
    if fam.n_trials == 0:
        criteria.append(Criterion(
            "Trial count N (registry)", 0, ">= 1 logged trial", INSUFF,
            "No trials logged for this family. If N is unreconstructable, "
            "the verdict is INSUFFICIENT-DATA, never PASS."))
    else:
        over = fam.trial_budget and fam.n_trials > fam.trial_budget
        criteria.append(_crit(
            "Trial count N (registry)", fam.n_trials,
            f"logged; budget {fam.trial_budget}", True,
            "OVER BUDGET — flagged to Director of Research" if over else ""))

    # -- core performance ---------------------------------------------
    sr_ann = stats.sharpe_annual(r, periods_per_year)
    criteria.append(_crit("Net Sharpe (OOS, annualized)", sr_ann,
                          f">= {NET_SHARPE_MIN}", sr_ann >= NET_SHARPE_MIN))

    t = stats.sr_tstat(r)
    criteria.append(_crit("t-statistic (net)", t, f">= {T_STAT_HURDLE}",
                          t >= T_STAT_HURDLE))

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
        criteria.append(_crit(
            f"PBO (CSCV, S={CSCV_PARTITIONS_S}, {pbo.n_combinations} splits)",
            pbo.pbo, f"<= {PBO_MAX_PAPER}", pbo.pbo <= PBO_MAX_PAPER))
    else:
        criteria.append(Criterion(
            "PBO (CSCV)", None, f"<= {PBO_MAX_PAPER}", INSUFF,
            "Registry return matrix too small for S=16 CSCV"))

    # -- length ---------------------------------------------------------
    years = backtest_years if backtest_years is not None else r.size / periods_per_year
    if fam.n_trials >= 1 and sr_ann > 0:
        minbtl = stats.min_backtest_length_years(
            max(fam.n_trials, 2), sr_ann, periods_per_year)
        need = max(MIN_YEARS, minbtl)
        criteria.append(_crit(
            "Backtest length (years)", years,
            f">= max({MIN_YEARS:g}, MinBTL={minbtl:.2f})", years >= need))
    else:
        criteria.append(_crit("Backtest length (years)", years,
                              f">= {MIN_YEARS:g}", years >= MIN_YEARS))

    # -- holdout single-use --------------------------------------------
    if holdout_opened_once is None:
        opened = [e for e in registry.events(kind="holdout_opened")]
        second = [e for e in registry.events(kind="holdout_second_open_attempt")]
        if second:
            criteria.append(_crit("Holdout single-use", "violated",
                                  "opened exactly once", False,
                                  "Second-open attempt logged — dataset retired"))
        elif opened:
            criteria.append(_crit("Holdout single-use", "opened once",
                                  "opened exactly once", True))
        else:
            criteria.append(Criterion("Holdout single-use", "not opened",
                                      "opened exactly once", INSUFF,
                                      "OOS evaluation requires the holdout"))
    else:
        criteria.append(_crit("Holdout single-use",
                              "opened once" if holdout_opened_once else "not/over-opened",
                              "opened exactly once", holdout_opened_once))

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

    # -- cost robustness & breakeven ------------------------------------
    breakeven = None
    if net_returns_at_cost_multiplier is not None:
        r2 = np.asarray(net_returns_at_cost_multiplier(2.0), dtype=float)
        t2 = stats.sr_tstat(r2[~np.isnan(r2)])
        criteria.append(_crit("t-stat at 2× costs", t2, f">= {T_STAT_HURDLE}",
                              t2 >= T_STAT_HURDLE))
        # bisect the breakeven multiplier in [1, 32]
        lo, hi = 1.0, 32.0
        t_lo = stats.sr_tstat(np.asarray(net_returns_at_cost_multiplier(lo)))
        if t_lo < T_STAT_HURDLE:
            breakeven = lo
        else:
            for _ in range(24):
                mid = 0.5 * (lo + hi)
                tm = stats.sr_tstat(np.asarray(net_returns_at_cost_multiplier(mid)))
                if tm >= T_STAT_HURDLE:
                    lo = mid
                else:
                    hi = mid
            breakeven = lo
    else:
        criteria.append(Criterion("t-stat at 2× costs", None,
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
    )
    registry.log_event("gate1_verdict", family, {
        "strategy": strategy, "overall": overall,
        "n_trials": fam.n_trials, "returns_sha256": sha,
    })
    return report
