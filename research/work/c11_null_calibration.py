"""VALIDATION-SPEC-005-c11-null-calibration.md -- the C11 leg-(ii) null
calibration script.

Dispatch S4-D-033, Head of Data & Infrastructure. Computes the figures
DATA-IMPL-016-c11-null-calibration.md reports; makes ZERO calls to
`run_backtest` against `book/registry.db` and opens NO write grant of any
kind (the one live write -- a single `log_event` -- is issued separately,
by hand, against the signature in `castellan.registry`, per this dispatch's
own I-374 instruction not to script it here).

I-044 (binding, test E-4): this script computes figures and writes them to
`c11_results.json`. It does NOT print or log a conclusion -- no "decisive",
"weak", "defective", "survives", "fires", "spares", "confirms" appears
below in any `print()`/log call. Every reading belongs in the deliverable
document's prose, attributed, sourced to a numbered figure here.

Hard stops honored: no leg-(i) or leg-(ii) VERDICT is computed or printed
(alpha_1 uses `castellan.stats.ols_alpha_tstat_hac` strictly as a
CALIBRATION quantity on SURROGATES only -- never on the realized
alignment, and never presented as a leg-(i) result); `I-386` (the sec4.6
greedy `I_max`/`I_min` construction) is computed and reported exactly as
specified, UNREPAIRED, and labelled defective per the existing finding.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "harness"))

from castellan import reconstruction as recon  # noqa: E402
from castellan import nullcal  # noqa: E402
from castellan.data import PITStore, pit_funding_panel, pit_price_panel  # noqa: E402
from castellan.stats import ols_alpha_tstat_hac  # noqa: E402

PREREG_SHA256 = "e5ebd3a6db02b97955518bc70db3906918e702f9879d3ad9928223ad6d2a105f"
MASTER_SEED = int(PREREG_SHA256[:16], 16)
TRIAL1_FUNDING_SHA256 = (
    "971d037d442cf1a5fb93ad2c797f54938fd6250cccd2079b903d8c853a58c791"
)
B_RESAMPLES = 10_000
K_WORST = 20
LEG_I_LAG = 21
HURDLE_T = 3.0
FIRE_THRESHOLD = 0.25
L_GRID = (21, 30, 60, 90)
PRIMARY_L = 30


def load_realized_panels():
    store = PITStore(str(REPO_ROOT / "book" / "pit.db"))
    C = pd.Timestamp("2026-09-15", tz="UTC")
    spot = pit_price_panel(store, "binance", list(recon.SPOT_COLS), C)
    perp = pit_price_panel(store, "binanceusdm", list(recon.PERP_COLS), C)
    prices = pd.concat([spot, perp], axis=1).dropna()
    idx = prices.index[prices.index <= pd.Timestamp("2026-08-11")]
    prices = prices.loc[idx]
    funding = pit_funding_panel(store, "binanceusdm", list(recon.PERP_COLS), C, idx)
    store.close()
    return prices, funding, idx


def load_trial1():
    conn = sqlite3.connect(
        f"file:{REPO_ROOT / 'book' / 'registry.db'}?mode=ro", uri=True
    )
    row = conn.execute(
        "SELECT returns_blob, n_bars, config_json FROM trials WHERE trial_id=1"
    ).fetchone()
    conn.close()
    blob, n_bars, config_json = row
    r = np.frombuffer(blob, dtype=np.float32).astype(float)
    return r, n_bars, json.loads(config_json)


def check_b7_b8(funding_panel, idx, trial1_config) -> dict:
    fresh_sha = funding_panel.attrs["sha256"]
    trial1_sha = trial1_config["funding_panel_sha256"]
    b7_pass = fresh_sha == trial1_sha == TRIAL1_FUNDING_SHA256
    b8_pass = (
        len(idx) == 2415
        and idx[0] == pd.Timestamp("2020-01-01")
        and idx[-1] == pd.Timestamp("2026-08-11")
    )
    return {
        "b7_pass": bool(b7_pass),
        "b7_fresh_sha256": fresh_sha,
        "b7_trial1_sha256": trial1_sha,
        "b8_pass": bool(b8_pass),
        "b8_n_bars": int(len(idx)),
        "b8_first": str(idx[0]),
        "b8_last": str(idx[-1]),
    }


def greedy_feasibility_bound(R_bench: np.ndarray, w_held: pd.DataFrame, prices, funding):
    """VALIDATION-SPEC-005 sec4.6's literal construction. UNREPAIRED
    (I-386, HIGH, DATA-IMPL-014): demonstrated defective. Computed and
    reported per D-4, labelled [inferred -- defective, see I-386]."""
    idx = w_held.index
    out = {}
    for direction, maximize in (("max", True), ("min", False)):
        w_cols = {}
        for asset in recon.ASSETS:
            w_cols[asset] = nullcal.greedy_feasibility_assignment(
                R_bench, w_held[asset].to_numpy(), maximize=maximize
            )
        w_df = pd.DataFrame(w_cols, index=idx)
        net = recon.reconstruct_net_returns(prices, funding, w_df)
        out[direction] = float(nullcal.worst_k_mean(net.to_numpy(), k=K_WORST))
    return out


def run_cell(w_held, prep, construction: str, L: int, rng, M_b: float):
    T = len(w_held)
    w_btc = w_held["BTC"].to_numpy()
    w_eth = w_held["ETH"].to_numpy()
    w_btc_mat = np.empty((B_RESAMPLES, T))
    w_eth_mat = np.empty((B_RESAMPLES, T))
    n_identity_redraws = 0
    for b in range(B_RESAMPLES):
        if construction == "permutation":
            sigma_btc, sigma_eth = nullcal.joint_permutation_indices(T, L, rng)
        else:
            sigma_btc = nullcal.stationary_block_bootstrap_index(T, L, rng)
            sigma_eth = sigma_btc  # one common draw, both constructions (C-1)
        w_btc_mat[b] = w_btc[sigma_btc]
        w_eth_mat[b] = w_eth[sigma_eth]

    mean_deviation = None
    if construction == "permutation":
        assert np.allclose(w_btc_mat.mean(axis=1), w_btc.mean())
        assert np.allclose(w_eth_mat.mean(axis=1), w_eth.mean())
    else:
        mean_deviation = {
            "BTC": (w_btc_mat.mean(axis=1) - w_btc.mean()).tolist()[:5] + ["...B_RESAMPLES total, truncated"],
            "BTC_std": float((w_btc_mat.mean(axis=1) - w_btc.mean()).std()),
            "ETH_std": float((w_eth_mat.mean(axis=1) - w_eth.mean()).std()),
        }

    net_mat = recon.reconstruct_net_returns_batch(prep, w_btc_mat, w_eth_mat)
    M_s = nullcal.worst_k_mean_batch(net_mat, k=K_WORST)
    I_star = (M_s - M_b) / abs(M_b)
    alpha_2 = float((I_star >= FIRE_THRESHOLD).mean())
    ci = nullcal.clopper_pearson_interval(int((I_star >= FIRE_THRESHOLD).sum()), B_RESAMPLES)
    return {
        "alpha_2": alpha_2,
        "alpha_2_ci95": ci,
        "I_star_sha256": hashlib.sha256(I_star.tobytes()).hexdigest(),
        "mean_deviation_disclosure": mean_deviation,
        "I_star": I_star,  # kept in-process only; stripped before JSON dump
        "net_mat": net_mat,
    }


def main():
    t_start = time.time()
    prices, funding, idx = load_realized_panels()
    R_bench, n_bars_trial1, trial1_config = load_trial1()
    b7b8 = check_b7_b8(funding, idx, trial1_config)
    if not b7b8["b7_pass"]:
        payload = {"STOP": "B-7 funding_panel_sha256 mismatch", **b7b8}
        (REPO_ROOT / "research" / "work" / "c11_results.json").write_text(
            json.dumps(payload, indent=2)
        )
        print(json.dumps({"stop": True, "reason": "b7_mismatch"}))
        return 1

    sched = recon.build_schedule(funding)
    w_held = sched["w_held"]
    c = recon.exposure_match_c(prices, w_held)
    M_b = c * nullcal.worst_k_mean(R_bench, k=K_WORST)
    guard_d2 = bool(M_b < 0)

    w_bar = w_held.mean()
    w_const = pd.DataFrame({a: np.full(len(idx), w_bar[a]) for a in recon.ASSETS}, index=idx)
    R_strat_0 = recon.reconstruct_net_returns(prices, funding, w_const).to_numpy()
    M_s0 = nullcal.worst_k_mean(R_strat_0, k=K_WORST)
    I_0 = nullcal.compute_i0(M_b, M_s0)

    greedy = greedy_feasibility_bound(R_bench, w_held, prices, funding)
    I_max_literal = (greedy["max"] - M_b) / abs(M_b)
    I_min_literal = (greedy["min"] - M_b) / abs(M_b)

    prep = recon.prepare_batch_inputs(prices, funding)

    kids = nullcal.spawn_children(MASTER_SEED, 8)
    all_cells = nullcal.disclosure_grid_cells(L_GRID, ("permutation", "stationary"))
    assert len(all_cells) == 8
    cell_index = {cell: i for i, cell in enumerate(all_cells)}

    grid_results = {}
    primary_cell = None
    for construction, L in all_cells:
        kid = kids[cell_index[(construction, L)]]
        rng = np.random.default_rng(kid)
        cell = run_cell(w_held, prep, construction, L, rng, M_b)
        key = f"{construction}_L{L}"
        grid_results[key] = {
            "alpha_2": cell["alpha_2"],
            "alpha_2_ci95": cell["alpha_2_ci95"],
            "I_star_sha256": cell["I_star_sha256"],
            "spawn_index": cell_index[(construction, L)],
        }
        if construction == "stationary":
            grid_results[key]["mean_exposure_deviation_disclosure"] = cell["mean_deviation_disclosure"]
        if construction == "permutation" and L == PRIMARY_L:
            primary_cell = cell

    assert primary_cell is not None
    I_star_primary = primary_cell["I_star"]
    net_mat_primary = primary_cell["net_mat"]

    # alpha_1 / alpha_joint -- CALIBRATION quantities only (hard stop 2):
    # ols_alpha_tstat_hac run on SURROGATES against the realized R_bench,
    # never on the realized alignment, never presented as a leg-(i) result.
    t_alpha = np.empty(B_RESAMPLES)
    for b in range(B_RESAMPLES):
        res = ols_alpha_tstat_hac(net_mat_primary[b], R_bench, lag=LEG_I_LAG)
        t_alpha[b] = res.t_alpha
    leg1_survives = t_alpha > HURDLE_T
    leg2_spares = I_star_primary >= FIRE_THRESHOLD
    joint = nullcal.joint_survival_rate(leg1_survives, leg2_spares)
    alpha_1 = joint["alpha_1"]
    alpha_2_primary = joint["alpha_2"]
    alpha_joint = joint["alpha_joint"]
    product = joint["product"]
    gap = joint["independence_gap"]

    # Alternative denominator disclosure (|M_s| instead of |M_b|), primary cell.
    M_s_primary = nullcal.worst_k_mean_batch(net_mat_primary, k=K_WORST)
    I_alt = (M_s_primary - M_b) / np.abs(M_s_primary)
    alpha_2_alt_denominator = float((I_alt >= FIRE_THRESHOLD).mean())

    # Cost-free variant disclosure, primary cell: rebuild with per-side costs zeroed.
    prep_costfree = dict(prep)
    prep_costfree["per_side_spot"] = 0.0
    prep_costfree["per_side_perp"] = 0.0
    rng_costfree = np.random.default_rng(kids[cell_index[("permutation", PRIMARY_L)]])
    T = len(w_held)
    w_btc = w_held["BTC"].to_numpy()
    w_eth = w_held["ETH"].to_numpy()
    w_btc_mat_cf = np.empty((B_RESAMPLES, T))
    w_eth_mat_cf = np.empty((B_RESAMPLES, T))
    for b in range(B_RESAMPLES):
        sigma = nullcal.circular_block_permutation_index(T, PRIMARY_L, rng_costfree)
        w_btc_mat_cf[b] = w_btc[sigma]
        w_eth_mat_cf[b] = w_eth[sigma]
    net_costfree = recon.reconstruct_net_returns_batch(prep_costfree, w_btc_mat_cf, w_eth_mat_cf)
    M_s_costfree = nullcal.worst_k_mean_batch(net_costfree, k=K_WORST)
    I_costfree = (M_s_costfree - M_b) / abs(M_b)
    alpha_2_costfree = float((I_costfree >= FIRE_THRESHOLD).mean())

    # Null percentiles + tie count, primary cell.
    pct = np.percentile(I_star_primary, [1, 5, 25, 50, 75, 95, 99]).tolist()
    _, counts = np.unique(I_star_primary, return_counts=True)
    n_tied = int(counts[counts > 1].sum()) if (counts > 1).any() else 0
    tie_fraction = n_tied / len(I_star_primary)

    results = {
        "provenance": {
            "prereg_sha256": PREREG_SHA256,
            "master_seed": MASTER_SEED,
            "numpy_version": np.__version__,
            "B_resamples": B_RESAMPLES,
            "K_worst": K_WORST,
            "trial1_config_hash": "44532cc88ed7b1a9",
            "trial1_n_bars": n_bars_trial1,
        },
        "b7_b8": b7b8,
        "schedule": {
            "c": c,
            "w_bar": {a: float(w_bar[a]) for a in recon.ASSETS},
            "bars_at_w1": {a: int((w_held[a] == 1.0).sum()) for a in recon.ASSETS},
            "forced_bars": {a: int(sched["forced_mask"][a].sum()) for a in recon.ASSETS},
            "triggered_bars": {a: int(sched["triggered"][a].sum()) for a in recon.ASSETS},
        },
        "M_b": M_b,
        "guard_d2_M_b_negative": guard_d2,
        "I_0": I_0,
        "I_max_literal_greedy": I_max_literal,
        "I_min_literal_greedy": I_min_literal,
        "I_max_defective_see_I386": True,
        "primary": {
            "L": PRIMARY_L,
            "construction": "permutation",
            "alpha_2": alpha_2_primary,
            "alpha_1_calibration_only": alpha_1,
            "alpha_joint": alpha_joint,
            "product_alpha1_alpha2": product,
            "independence_gap": gap,
            "I_star_sha256": hashlib.sha256(I_star_primary.tobytes()).hexdigest(),
            "null_percentiles_1_5_25_50_75_95_99": pct,
            "tie_count": n_tied,
            "tie_fraction": tie_fraction,
        },
        "disclosure_grid_8_cells": grid_results,
        "disclosure_alt_denominator_alpha_2": alpha_2_alt_denominator,
        "disclosure_costfree_alpha_2": alpha_2_costfree,
        "elapsed_seconds": time.time() - t_start,
    }

    out_path = REPO_ROOT / "research" / "work" / "c11_results.json"
    out_path.write_text(json.dumps(results, indent=2, default=str))
    print(json.dumps({"wrote": str(out_path), "elapsed_seconds": results["elapsed_seconds"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
