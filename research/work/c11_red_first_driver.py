"""VALIDATION-SPEC-005 sec7's binding red-first requirement, executed.

For each of the 30 acceptance tests in
`harness/tests/test_c11_null_calibration.py`, this driver applies the
NAMED mutation from that test's own docstring (a monkeypatch of the
production module attribute/function the mutation names -- or, for C-4, a
genuine temporary edit of the standalone subprocess script it targets),
runs ONLY that test via `pytest.main`, records the RED (must-fail) result,
reverts the mutation, and re-runs to confirm GREEN (must-pass).

Writes `research/work/c11_red_first_log.json` -- consumed verbatim by
`research/DATA-IMPL-016-c11-null-calibration.md`.

Some rows (D-1, D-2, D-5, per their own docstrings) construct BOTH a
correct and a deliberately-wrong computation INSIDE the same test body and
assert they diverge -- there is no external module attribute to
monkeypatch for these (the "mutation" is a local variable, not a call
site), so they are marked `inline_dual_construction` in the log rather
than `external_monkeypatch`, and their JSON entry additionally records
that the test's own internal wrong-vs-right comparison is what supplies
the red-first evidence, run every time the test runs (including in the
ordinary "AFTER" suite run).
"""

from __future__ import annotations

import contextlib
import json
import sys
from pathlib import Path

import numpy as np
import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "harness"))
sys.path.insert(0, str(REPO_ROOT / "harness" / "tests"))

from castellan import costs as costs_mod  # noqa: E402
from castellan import reconstruction as recon  # noqa: E402
from castellan import nullcal  # noqa: E402
from castellan import stats as stats_mod  # noqa: E402
from castellan import registry as registry_mod  # noqa: E402
import test_c11_null_calibration as T  # noqa: E402

TEST_FILE = "harness/tests/test_c11_null_calibration.py"


@contextlib.contextmanager
def patch_attr(obj, name, value):
    sentinel = object()
    original = getattr(obj, name, sentinel)
    setattr(obj, name, value)
    try:
        yield
    finally:
        if original is sentinel:
            delattr(obj, name)
        else:
            setattr(obj, name, original)


def run_one(test_id: str) -> int:
    return pytest.main(["-q", f"{TEST_FILE}::{test_id}"])


# ---------------------------------------------------------------------------
# Mutation definitions: test_id -> context manager applying the named
# mutation for the duration of the `with` block.
# ---------------------------------------------------------------------------


def mut_a1():
    mutated_perp = costs_mod.CRYPTO_PERP_TAKER.scaled(50.0)
    new_cost_model = {**recon.COST_MODEL,
                       "BTC/USDT:USDT": mutated_perp, "ETH/USDT:USDT": mutated_perp}
    return patch_attr(recon, "COST_MODEL", new_cost_model)


def mut_a2():
    return patch_attr(recon, "EXECUTION_LAG", 2)


def mut_a3():
    orig = registry_mod.TrialRegistry.log_event

    def doubled(self, kind, family, detail):
        orig(self, kind, family, detail)
        return orig(self, kind, family, detail)

    return patch_attr(registry_mod.TrialRegistry, "log_event", doubled)


def mut_a4():
    def hardcoded(prices, funding_panel, w):
        # Ignores COST_MODEL entirely -- inlines the (correct, at the time
        # of writing) literals instead of reading the module attribute.
        target_weights = recon.build_target_weights(prices, w)
        positions = target_weights.shift(1).fillna(0.0)
        asset_rets = prices.pct_change()
        gross = (positions * asset_rets).sum(axis=1)
        trades = positions.diff().abs().fillna(positions.abs())
        trade_cost = trades.sum(axis=1) * 0.00125  # single hardcoded rate for ALL columns
        common = [c for c in prices.columns if c in funding_panel.columns]
        carry = -(positions[common] * funding_panel[common].fillna(0.0)).sum(axis=1)
        return (gross + carry - trade_cost).fillna(0.0)

    return patch_attr(recon, "reconstruct_net_returns", hardcoded)


def mut_a5():
    return patch_attr(recon, "PERIODS_PER_YEAR", 252)


def mut_a6():
    import contextlib as _cl
    import json as _json
    import os as _os
    import sys as _sys
    import time as _time

    @_cl.contextmanager
    def no_nesting_check(self, *, reason, dispatch, token=None):
        # Copy of TrialRegistry.write_grant with the `self._grant is not
        # None` nesting guard removed.
        if reason not in registry_mod._REASON_ADMITS:
            raise registry_mod.RegistryWriteGrantMalformedError("bad reason")
        tok = token if token is not None else _os.environ.get("CASTELLAN_REGISTRY_WRITE")
        if not tok:
            raise registry_mod.RegistryWriteNotGrantedError("no token")
        rw = __import__("sqlite3").connect(self.path)
        prev_hash = self._last_grant_hash(rw)
        argv = _json.dumps(_sys.argv, default=str)
        pid = _os.getpid()
        opened_utc = _time.time()
        grant_hash = registry_mod._compute_grant_hash(prev_hash, tok, reason, dispatch, argv, opened_utc)
        cur = rw.execute(
            "INSERT INTO write_grants (token, reason, dispatch, argv, pid, "
            "opened_utc, closed_utc, writes, outcome, prev_hash, grant_hash, "
            "migration_watermark) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
            (tok, reason, dispatch, argv, pid, opened_utc, None, 0, None, prev_hash, grant_hash, None),
        )
        grant_id = cur.lastrowid
        self._grant = {"reason": reason, "grant_id": grant_id, "writes": 0}
        self.conn = rw
        try:
            yield self
        except BaseException:
            rw.rollback()
            raise
        else:
            rw.execute("UPDATE write_grants SET closed_utc=?, outcome='CLEAN', writes=? WHERE grant_id=?",
                       (_time.time(), self._grant["writes"], grant_id))
            rw.commit()
        finally:
            rw.close()
            self.conn = self._ro
            self._grant = None

    return patch_attr(registry_mod.TrialRegistry, "write_grant", no_nesting_check)


def mut_b1():
    def broken(z, k=None, d=None, w_max=None):
        if k is None:
            k = recon.K_SIZING
        if d is None:
            d = recon.D_SIZING
        if w_max is None:
            w_max = recon.W_MAX
        import pandas as pd
        excess = (z - d).clip(lower=0.0)
        w = (1.0 - k * excess).clip(upper=w_max)  # NO lower clip
        return w.where(z.notna(), w_max)

    return patch_attr(recon, "w_target_from_z", broken)


def mut_b2():
    return patch_attr(recon, "D_SIZING", -1.0)


def mut_b3():
    return patch_attr(recon, "K_SIZING", 0.25)


def mut_b4():
    return patch_attr(recon, "LOOKBACK", 10)


def mut_b5():
    return patch_attr(recon, "R2_TRIGGER_LEN_DAYS", 20)


def mut_b6():
    return patch_attr(recon, "BAND", 2.0)


def mut_b7():
    return patch_attr(T, "TRIAL1_FUNDING_SHA256", "0" * 64)


def mut_b8():
    import pandas as pd
    return patch_attr(T, "SETTLED_CUTOFF", pd.Timestamp("2026-08-12"))


def mut_c1():
    def independent(T_, L, rng):
        s1 = nullcal.circular_block_permutation_index(T_, L, rng)
        s2 = nullcal.circular_block_permutation_index(T_, L, rng)
        return s1, s2

    return patch_attr(nullcal, "joint_permutation_indices", independent)


def mut_c2():
    return patch_attr(nullcal, "circular_block_permutation_index", nullcal.stationary_block_bootstrap_index)


def mut_c3():
    def no_reject(T_, L, rng, max_redraws=1000):
        identity = np.arange(T_)
        bounds = nullcal.block_boundaries(T_, L)
        n_blk = len(bounds)
        s = int(rng.integers(0, T_))
        rotated = (identity + s) % T_
        block_order = rng.permutation(n_blk)
        sigma = np.concatenate([rotated[a:b] for a, b in (bounds[i] for i in block_order)])
        return sigma  # no identity check at all

    return patch_attr(nullcal, "circular_block_permutation_index", no_reject)


def mut_c4():
    script = REPO_ROOT / "research" / "work" / "c11_repro_probe.py"
    original = script.read_text()
    mutated = original.replace(
        "MASTER_SEED = int(PREREG_SHA256[:16], 16)",
        "import time as _t; MASTER_SEED = int(_t.time() * 1e6)",
    )
    assert mutated != original, "replacement target not found in c11_repro_probe.py"

    @contextlib.contextmanager
    def _cm():
        script.write_text(mutated)
        try:
            yield
        finally:
            script.write_text(original)

    return _cm()


def mut_c5():
    def broken_boundaries(T_, L):
        n_blk = -(-T_ // (L + 1))  # off-by-one block size
        bounds = []
        start = 0
        for _ in range(n_blk):
            end = min(start + L + 1, T_)
            bounds.append((start, end))
            start = end
        return bounds

    return patch_attr(nullcal, "block_boundaries", broken_boundaries)


def mut_c6():
    def broken_spawn(master_seed, n=8):
        ss = np.random.SeedSequence(master_seed)
        child = ss.spawn(1)[0]
        return [child] * n

    return patch_attr(nullcal, "spawn_children", broken_spawn)


def mut_d3():
    return patch_attr(nullcal, "compute_i0", lambda M_b, M_s: 1e-9)


def mut_d4():
    def broken_assignment(ranking_series, w_multiset, maximize):
        # Does not even preserve the input multiset.
        return np.sort(np.asarray(w_multiset)) * 0.0

    return patch_attr(nullcal, "greedy_feasibility_assignment", broken_assignment)


def mut_e1_e2():
    def broken_nw(returns, lag):
        import math
        r = np.asarray(returns, dtype=float)
        r = r[~np.isnan(r)]
        Tn = r.size
        L = int(lag)
        if Tn < 2:
            return float("nan")
        d = r - r.mean()

        def gamma(l):
            if l == 0:
                return float(d @ d) / (Tn - 1)
            return float(d[l:] @ d[: Tn - l]) / (Tn - 1)

        s = gamma(0)
        for l in range(1, L + 1):
            s += 2.0 * (1.0 - l / L if L > 0 else 0.0) * gamma(l)  # off-by-one: /L not /(L+1)
        if s <= 0:
            return float("nan")
        return float(r.mean() / math.sqrt(s / Tn))

    return patch_attr(stats_mod, "sr_tstat_nw", broken_nw)


def mut_e3():
    def broken_joint(leg1_fires, leg2_spares):
        leg1_fires = np.asarray(leg1_fires, dtype=bool)
        leg2_spares = np.asarray(leg2_spares, dtype=bool)
        a1 = float(leg1_fires.mean())
        a2 = float(leg2_spares.mean())
        product = a1 * a2
        return {"alpha_1": a1, "alpha_2": a2, "alpha_joint": product,
                "product": product, "independence_gap": 0.0}

    return patch_attr(nullcal, "joint_survival_rate", broken_joint)


def mut_e4():
    original = T.SCRIPT_PATH.read_text()
    mutated = original.replace(
        'print(json.dumps({"wrote": str(out_path)',
        'print("leg (ii) fires decisively"); print(json.dumps({"wrote": str(out_path)',
    )
    assert mutated != original, "insertion point not found in c11_null_calibration.py"

    @contextlib.contextmanager
    def _cm():
        T.SCRIPT_PATH.write_text(mutated)
        try:
            yield
        finally:
            T.SCRIPT_PATH.write_text(original)

    return _cm()


def mut_e5():
    return patch_attr(nullcal, "disclosure_grid_cells", lambda Ls, cs: [(cs[0], Ls[0])])


INLINE_DUAL_CONSTRUCTION = {
    "test_d1_worst_20_selected_per_series_not_reused":
        "computes worst_k_mean (correct) and worst_k_mean_wrong (reuses "
        "R_bench's index set) on the SAME surrogate inline, asserts they "
        "differ -- the 'RED' evidence is `wrong` disagreeing with `correct`, "
        "exercised every run.",
    "test_d2_guard_negative_denominator_else_insufficient_data":
        "exercises guarded_m_b's INSUFFICIENT-DATA branch on a synthetic "
        "all-positive series inline; the 'RED' case (omitting the guard) is "
        "shown by the fact that nullcal.worst_k_mean(all_positive) alone "
        "returns a definite (wrong-to-use) number rather than the sentinel.",
    "test_d5_null_percentiles_and_tie_count_reported":
        "computes the tie fraction on a continuous series and on a "
        "deliberately-rounded (degenerate) copy inline, asserts the rounded "
        "copy's tie fraction is measurably higher -- the flagging logic's "
        "discriminating power is exercised in the same run.",
}

MUTATIONS = {
    "test_a1_constant_schedule_matches_trial1_blob": mut_a1,
    "test_a2_anchor_scratch_registry_matches_engine": mut_a2,
    "test_a3_registry_hash_before_after_is_one_event_row": mut_a3,
    "test_a4_costs_read_at_runtime_not_literal": mut_a4,
    "test_a5_periods_per_year_persisted_as_365": mut_a5,
    "test_a6_outer_grant_around_run_backtest_raises_nested_error": mut_a6,
    "test_b1_w_in_zero_one_every_bar": mut_b1,
    "test_b2_w_equals_one_wherever_z_le_d": mut_b2,
    "test_b3_sizing_function_unit_values": mut_b3,
    "test_b4_r1_burnin_first_30_bars_forced_to_one": mut_b4,
    "test_b5_r2_trigger_exactly_30_bars_from_named_date": mut_b5,
    "test_b6_turnover_band_both_branches_occur": mut_b6,
    "test_b7_funding_panel_sha256_matches_trial1": mut_b7,
    "test_b8_index_is_trial1s_2415_bars_terminal_20260811": mut_b8,
    "test_c1_multiset_and_joint_pairing_preserved": mut_c1,
    "test_c2_mean_preserved_exactly_and_c_computed_once": mut_c2,
    "test_c3_no_surrogate_is_identity_and_rejection_branch_forced": mut_c3,
    "test_c4_reproducibility_two_processes_same_seed": mut_c4,
    "test_c5_exactly_81_blocks_and_bijection_at_l30": mut_c5,
    "test_c6_eight_cells_from_independent_spawn_children": mut_c6,
    "test_d3_i0_is_computed_and_is_not_approximately_zero": mut_d3,
    "test_d4_greedy_vs_bruteforce_at_t10_reports_not_asserts_optimum": mut_d4,
    "test_e1_reduction_to_mean_nw_tstat": mut_e1_e2,
    "test_e2_same_bartlett_kernel_and_divisor_as_sr_tstat_nw": mut_e1_e2,
    "test_e3_joint_alpha_computed_by_distinct_path_from_product": mut_e3,
    "test_e4_no_print_asserts_a_conclusion": mut_e4,
    "test_e5_disclosure_grid_all_eight_cells_present": mut_e5,
}

ALL_TEST_IDS = [
    "test_a1_constant_schedule_matches_trial1_blob",
    "test_a2_anchor_scratch_registry_matches_engine",
    "test_a3_registry_hash_before_after_is_one_event_row",
    "test_a4_costs_read_at_runtime_not_literal",
    "test_a5_periods_per_year_persisted_as_365",
    "test_a6_outer_grant_around_run_backtest_raises_nested_error",
    "test_b1_w_in_zero_one_every_bar",
    "test_b2_w_equals_one_wherever_z_le_d",
    "test_b3_sizing_function_unit_values",
    "test_b4_r1_burnin_first_30_bars_forced_to_one",
    "test_b5_r2_trigger_exactly_30_bars_from_named_date",
    "test_b6_turnover_band_both_branches_occur",
    "test_b7_funding_panel_sha256_matches_trial1",
    "test_b8_index_is_trial1s_2415_bars_terminal_20260811",
    "test_c1_multiset_and_joint_pairing_preserved",
    "test_c2_mean_preserved_exactly_and_c_computed_once",
    "test_c3_no_surrogate_is_identity_and_rejection_branch_forced",
    "test_c4_reproducibility_two_processes_same_seed",
    "test_c5_exactly_81_blocks_and_bijection_at_l30",
    "test_c6_eight_cells_from_independent_spawn_children",
    "test_d1_worst_20_selected_per_series_not_reused",
    "test_d2_guard_negative_denominator_else_insufficient_data",
    "test_d3_i0_is_computed_and_is_not_approximately_zero",
    "test_d4_greedy_vs_bruteforce_at_t10_reports_not_asserts_optimum",
    "test_d5_null_percentiles_and_tie_count_reported",
    "test_e1_reduction_to_mean_nw_tstat",
    "test_e2_same_bartlett_kernel_and_divisor_as_sr_tstat_nw",
    "test_e3_joint_alpha_computed_by_distinct_path_from_product",
    "test_e4_no_print_asserts_a_conclusion",
    "test_e5_disclosure_grid_all_eight_cells_present",
]


def main():
    log = {}
    for test_id in ALL_TEST_IDS:
        if test_id in INLINE_DUAL_CONSTRUCTION:
            green_rc = run_one(test_id)
            log[test_id] = {
                "method": "inline_dual_construction",
                "note": INLINE_DUAL_CONSTRUCTION[test_id],
                "green_exit_code": green_rc,
                "green_pass": green_rc == 0,
            }
            continue

        mutation_fn = MUTATIONS[test_id]
        with mutation_fn():
            red_rc = run_one(test_id)
        green_rc = run_one(test_id)
        log[test_id] = {
            "method": "external_monkeypatch",
            "red_exit_code": red_rc,
            "red_failed_as_expected": red_rc != 0,
            "green_exit_code": green_rc,
            "green_pass": green_rc == 0,
        }
        print(f"{test_id}: RED={red_rc} GREEN={green_rc}", file=sys.stderr)

    out = REPO_ROOT / "research" / "work" / "c11_red_first_log.json"
    out.write_text(json.dumps(log, indent=2))
    n_ok = sum(
        1 for v in log.values()
        if (v["method"] == "external_monkeypatch" and v["red_failed_as_expected"] and v["green_pass"])
        or (v["method"] == "inline_dual_construction" and v["green_pass"])
    )
    print(json.dumps({"wrote": str(out), "n_tests": len(log), "n_ok": n_ok}))


if __name__ == "__main__":
    main()
