"""VALIDATION-SPEC-005 sec6.4's mandatory scratch-registry rehearsal,
followed (only if the rehearsal is clean) by the ONE live write this
dispatch is authorized to make: a single `log_event(kind="null_calibration")`
against `book/registry.db`.

Run as: python3 research/work/c11_rehearsal_and_live_write.py --rehearse
        python3 research/work/c11_rehearsal_and_live_write.py --live

Two separate invocations, deliberately: the rehearsal must be observed
clean BEFORE the live call is even attempted, not merely coded to run
first in the same process.
"""
import argparse
import hashlib
import json
import sys
import tempfile
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "harness"))

from castellan.registry import TrialRegistry, RegistryWriteGrantNestedError  # noqa: E402
from castellan.engine import run_backtest  # noqa: E402
from castellan import reconstruction as recon  # noqa: E402
from castellan.data import PITStore, pit_price_panel, pit_funding_panel  # noqa: E402

DISPATCH = "S4-D-033"
TOKEN = "head-of-data-infra:S4-D-033:c11-null-calibration"  # I-374/I-161: an
# attribution field recorded in the write_grants row, not a validated
# secret (registry.py's own docstring: "a token exists to be RECORDED,
# not to authenticate").


def build_small_real_inputs():
    """A tiny slice of REAL panels (not synthetic) so the rehearsal
    exercises the actual PITStore/reconstruction code path, just on a
    short window -- fast, and still first-of-kind-faithful."""
    store = PITStore(str(REPO_ROOT / "book" / "pit.db"))
    C = pd.Timestamp("2026-09-15", tz="UTC")
    spot = pit_price_panel(store, "binance", list(recon.SPOT_COLS), C)
    perp = pit_price_panel(store, "binanceusdm", list(recon.PERP_COLS), C)
    prices = pd.concat([spot, perp], axis=1).dropna()
    idx = prices.index[prices.index <= pd.Timestamp("2026-08-11")]
    prices = prices.loc[idx][-400:]
    funding = pit_funding_panel(store, "binanceusdm", list(recon.PERP_COLS), C, idx)
    funding = funding.loc[prices.index]
    store.close()
    sched = recon.build_schedule(funding)
    return prices, funding, sched["w_held"]


def rehearse():
    prices, funding, w_held = build_small_real_inputs()
    target_weights = recon.build_target_weights(prices, w_held)

    with tempfile.TemporaryDirectory() as tmp:
        scratch = f"{tmp}/scratch-registry.db"
        reg_s = TrialRegistry(scratch, allow_create=True)

        with reg_s.write_grant(reason="REGISTER_HYPOTHESIS", dispatch=DISPATCH, token=TOKEN):
            reg_s.open_hypothesis(
                family="c11-rehearsal",
                statement="Rehearsal only -- not the sealed funding-carry-conditioning-002 family.",
                mechanism="Rehearsal.",
                falsifier="Rehearsal.",
                universe="BTC/ETH rehearsal slice.",
                horizon="Rehearsal.",
                success_criteria="Rehearsal.",
                trial_budget=8,
            )

        # No outer grant around run_backtest -- it self-grants LOG_TRIAL
        # internally (I-374). Confirm the guard fires if misused:
        nested_raised = False
        try:
            with reg_s.write_grant(reason="LOG_TRIAL", dispatch=f"{DISPATCH}-bad", token=TOKEN):
                run_backtest(
                    prices, target_weights, recon.COST_MODEL, reg_s,
                    family="c11-rehearsal", config={"purpose": "nesting-guard-check"},
                    execution_lag=1, periods_per_year=365, funding_panel=funding,
                )
        except RegistryWriteGrantNestedError:
            nested_raised = True

        res = run_backtest(
            prices, target_weights, recon.COST_MODEL, reg_s,
            family="c11-rehearsal", config={"purpose": "c11-rehearsal-run"},
            execution_lag=1, periods_per_year=365, funding_panel=funding,
        )

        with reg_s.write_grant(reason="LOG_EVENT", dispatch=DISPATCH, token=TOKEN):
            event_id = reg_s.log_event(
                kind="null_calibration", family="c11-rehearsal",
                detail={"rehearsal": True, "spec": "VALIDATION-SPEC-005"},
            )

        audit = reg_s.audit_write_grants()
        reg_s.close()

    report = {
        "nested_grant_raised_as_expected": nested_raised,
        "run_backtest_trial_id": res.trial_id,
        "run_backtest_periods_per_year_persisted": res.config["periods_per_year"],
        "log_event_id": event_id,
        "audit_chain_intact": audit["chain_intact"],
        "audit_n_grants": audit["n_grants"],
        "audit_orphan_rows": audit["orphan_rows"],
    }
    clean = (
        nested_raised
        and res.config["periods_per_year"] == 365
        and audit["chain_intact"]
        and all(len(v) == 0 for v in audit["orphan_rows"].values())
    )
    report["REHEARSAL_CLEAN"] = clean
    print(json.dumps(report, indent=2))
    return 0 if clean else 1


def live_write():
    results_path = REPO_ROOT / "research" / "work" / "c11_results.json"
    results = json.loads(results_path.read_text())
    results_sha256 = hashlib.sha256(results_path.read_bytes()).hexdigest()

    registry_path = REPO_ROOT / "book" / "registry.db"
    before_sha256 = hashlib.sha256(registry_path.read_bytes()).hexdigest()

    reg = TrialRegistry(str(registry_path), allow_create=False)

    detail = {
        "spec": "VALIDATION-SPEC-005",
        "dispatch": DISPATCH,
        "construction": "circular_block_permutation",
        "L": results["primary"]["L"],
        "B": results["provenance"]["B_resamples"],
        "master_seed": results["provenance"]["master_seed"],
        "numpy_version": results["provenance"]["numpy_version"],
        "inputs": {
            "trial_id": 1,
            "config_hash": results["provenance"]["trial1_config_hash"],
            "funding_panel_sha256": results["b7_b8"]["b7_trial1_sha256"],
        },
        "alpha_2": results["primary"]["alpha_2"],
        "alpha_2_ci95": results["primary"].get("alpha_2_ci95"),
        "alpha_1_calibration_only_never_a_leg_i_result": results["primary"]["alpha_1_calibration_only"],
        "alpha_joint": results["primary"]["alpha_joint"],
        "independence_gap_vs_sealed_product": results["primary"]["independence_gap"],
        "I_0": results["I_0"],
        "I_max_literal_greedy_defective_see_I386": results["I_max_literal_greedy"],
        "I_min_literal_greedy_defective_see_I386": results["I_min_literal_greedy"],
        "c": results["schedule"]["c"],
        "improvement_array_sha256_primary_cell": results["primary"]["I_star_sha256"],
        "trials_consumed": 0,
        "reconstruction_module": "harness/castellan/reconstruction.py, harness/castellan/nullcal.py",
        "full_results_artifact": "research/work/c11_results.json",
        "full_results_artifact_sha256": results_sha256,
        "deliverable": "research/DATA-IMPL-016-c11-null-calibration.md",
    }

    with reg.write_grant(reason="LOG_EVENT", dispatch=DISPATCH, token=TOKEN):
        event_id = reg.log_event(
            kind="null_calibration",
            family="funding-carry-conditioning-002",
            detail=detail,
        )
    reg.close()

    after_sha256 = hashlib.sha256(registry_path.read_bytes()).hexdigest()

    import sqlite3
    conn = sqlite3.connect(f"file:{registry_path}?mode=ro", uri=True)
    grant_row = conn.execute(
        "SELECT grant_id, token, reason, dispatch, opened_utc, closed_utc, writes, outcome "
        "FROM write_grants ORDER BY grant_id DESC LIMIT 1"
    ).fetchone()
    n_events_after = conn.execute("SELECT COUNT(*) FROM events").fetchone()[0]
    n_grants_after = conn.execute("SELECT COUNT(*) FROM write_grants").fetchone()[0]
    n_trials_after = conn.execute("SELECT COUNT(*) FROM trials").fetchone()[0]
    conn.close()

    print(json.dumps({
        "event_id": event_id,
        "registry_sha256_before": before_sha256,
        "registry_sha256_after": after_sha256,
        "n_events_after": n_events_after,
        "n_write_grants_after": n_grants_after,
        "n_trials_after": n_trials_after,
        "write_grants_row": {
            "grant_id": grant_row[0], "token": grant_row[1], "reason": grant_row[2],
            "dispatch": grant_row[3], "opened_utc": grant_row[4], "closed_utc": grant_row[5],
            "writes": grant_row[6], "outcome": grant_row[7],
        },
    }, indent=2))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--rehearse", action="store_true")
    ap.add_argument("--live", action="store_true")
    args = ap.parse_args()
    if args.rehearse:
        raise SystemExit(rehearse())
    elif args.live:
        live_write()
    else:
        print("pass --rehearse or --live")
        raise SystemExit(2)
