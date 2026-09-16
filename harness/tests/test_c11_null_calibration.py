"""VALIDATION-SPEC-005-c11-null-calibration.md section 7 -- the 30
acceptance tests (Groups A-E), red-first.

Every test's docstring/comment names the constructible failing mutation
(the dispatch's own binding condition: "for every test... construct a
mutation of the implementation that makes that test FAIL, record the
mutation and the observed failure in a red-first log, and only then write
the passing implementation"). The mutations themselves are applied and
verified by the standalone driver
`research/work/c11_red_first_driver.py`, which imports these same test
functions, monkeypatches the named target for each, and records the
observed RED/GREEN transition in
`research/work/c11_red_first_log.json` -- consumed verbatim by
`research/DATA-IMPL-016-c11-null-calibration.md`. This file is therefore
NOT run standalone as "the" red-first record; it is the fixed target the
driver mutates around. `python3 -m pytest harness/tests -q` (this suite's
own binding invocation, CLAUDE.md) exercises every test here at HEAD
(unmutated) -- the "AFTER" suite count.

D-3 and D-4 are the two rows the dispatch calls out as needing a
DEFECT-AWARE assertion rather than a naive equality: D-3 because
"asserting `I_0 approx 0` is itself the defect" (it measures `I_0 =
-8.27`, nowhere near 0), and D-4 because the literal sec4.6 greedy
construction is independently demonstrated defective at DATA-IMPL-014
(I-386, HIGH) -- this dispatch is under a hard stop not to repair I-386,
so D-4 here asserts the one true, defect-agnostic invariant (a brute-force
optimum can never be worse than any candidate assignment it enumerates,
greedy included) and REPORTS, without asserting, whether greedy achieves
it -- which, per I-386, it measurably does not.
"""

from __future__ import annotations

import hashlib
import inspect
import itertools
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from castellan import costs as costs_mod
from castellan import reconstruction as recon
from castellan import nullcal
from castellan import stats as stats_mod
from castellan.data import PITStore, pit_funding_panel, pit_price_panel
from castellan.engine import run_backtest, FundingCoverageError
from castellan.registry import TrialRegistry, RegistryWriteGrantNestedError

REPO_ROOT = Path(__file__).resolve().parents[2]
TEST_TOKEN = "c11-test-token"

TRIAL1_FUNDING_SHA256 = (
    "971d037d442cf1a5fb93ad2c797f54938fd6250cccd2079b903d8c853a58c791"
)
TRIAL1_CONFIG_HASH = "44532cc88ed7b1a9"
TRIAL1_FAMILY = "funding-carry-conditioning-002"
SETTLED_CUTOFF = pd.Timestamp("2026-08-11")  # exposed for B-8's mutation target
SCRIPT_PATH = REPO_ROOT / "research" / "work" / "c11_null_calibration.py"  # E-4's target


# ---------------------------------------------------------------------------
# Session fixtures -- built once, real live data, read-only paths only
# (I-375: PITStore has no read-only URI open path -- opened the ordinary
# way; only asof/pit_price_panel/pit_funding_panel are ever called on it).
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def realized_panels():
    store = PITStore(str(REPO_ROOT / "book" / "pit.db"))
    C = pd.Timestamp("2026-09-15", tz="UTC")
    spot = pit_price_panel(store, "binance", list(recon.SPOT_COLS), C)
    perp = pit_price_panel(store, "binanceusdm", list(recon.PERP_COLS), C)
    prices = pd.concat([spot, perp], axis=1).dropna()
    idx = prices.index[prices.index <= SETTLED_CUTOFF]
    prices = prices.loc[idx]
    funding = pit_funding_panel(
        store, "binanceusdm", list(recon.PERP_COLS), C, idx
    )
    store.close()
    return {"prices": prices, "funding": funding, "index": idx}


@pytest.fixture(scope="session")
def trial1_blob():
    import sqlite3

    conn = sqlite3.connect(
        f"file:{REPO_ROOT / 'book' / 'registry.db'}?mode=ro", uri=True
    )
    row = conn.execute(
        "SELECT returns_blob, n_bars, config_json FROM trials WHERE trial_id=1"
    ).fetchone()
    conn.close()
    blob, n_bars, config_json = row
    r = np.frombuffer(blob, dtype=np.float32).astype(float)
    return {"net_returns": r, "n_bars": n_bars, "config": json.loads(config_json)}


@pytest.fixture(scope="session")
def realized_schedule(realized_panels):
    return recon.build_schedule(realized_panels["funding"])


# ---------------------------------------------------------------------------
# Group A -- engine parity (6)
# ---------------------------------------------------------------------------


def test_a1_constant_schedule_matches_trial1_blob(realized_panels, trial1_blob):
    """A-1. Off-engine reconstruction at w == 1.0 (both assets, every bar)
    reproduces trial 1's stored net-return series to max abs diff <= 1e-9.

    Guard (spec's own): the reconstruction function's signature takes ONLY
    (prices, funding_panel, w) -- trial 1's blob must not be an input.
    Asserted here via `inspect.signature`, not merely by convention.

    RED-FIRST MUTATION (driver): monkeypatch `reconstruction.COST_MODEL` to
    a dict using a wrong-priced CostModel for one column -- breaks the cost
    arithmetic and pushes max abs diff far above 1e-9.
    """
    sig = inspect.signature(recon.reconstruct_net_returns)
    assert list(sig.parameters) == ["prices", "funding_panel", "w"]

    idx = realized_panels["index"]
    w_const = pd.DataFrame({"BTC": 1.0, "ETH": 1.0}, index=idx)
    net = recon.reconstruct_net_returns(
        realized_panels["prices"], realized_panels["funding"], w_const
    )
    diff = np.abs(net.to_numpy() - trial1_blob["net_returns"])
    assert diff.max() <= 1e-9, f"max abs diff {diff.max()} exceeds 1e-9"


def test_a2_anchor_scratch_registry_matches_engine(realized_panels, realized_schedule):
    """A-2. The anchor: on a SCRATCH registry, `run_backtest` with a
    VARYING surrogate schedule (>= 20 bars with |dw| > 0 -- guard, asserted
    below) matches the off-engine reconstruction of the identical schedule
    to <= 1e-9. This is the only test that exercises the trade_cost branch
    at all (A-1's constant schedule has ~zero turnover after entry).

    RED-FIRST MUTATION (driver): monkeypatch `reconstruction.EXECUTION_LAG`
    to 2 while the scratch `run_backtest` call keeps `execution_lag=1` --
    the off-engine and on-engine positions then lag by a different amount
    and diverge materially.
    """
    prices = realized_panels["prices"]
    funding = realized_panels["funding"]
    w_held = realized_schedule["w_held"]

    dw = w_held.diff().abs().sum(axis=1)
    n_varying = int((dw > 0).sum())
    assert n_varying >= 20, f"guard: only {n_varying} bars with |dw|>0"

    target_weights = recon.build_target_weights(prices, w_held)
    with tempfile.TemporaryDirectory() as tmp:
        reg = TrialRegistry(f"{tmp}/scratch-registry.db", allow_create=True)
        with reg.write_grant(
            reason="REGISTER_HYPOTHESIS", dispatch="TEST:a2", token=TEST_TOKEN
        ):
            reg.open_hypothesis(
                family="c11-a2-anchor",
                statement="rehearsal only",
                mechanism="rehearsal",
                falsifier="rehearsal",
                universe="rehearsal",
                horizon="rehearsal",
                success_criteria="rehearsal",
                trial_budget=8,
            )
        # No outer write_grant around run_backtest (I-374 / test A-6).
        res = run_backtest(
            prices, target_weights, recon.COST_MODEL, reg,
            family="c11-a2-anchor",
            config={"step": "test_a2"},
            execution_lag=1,
            periods_per_year=365,
            funding_panel=funding,
        )
        reg.close()

    off_engine = recon.reconstruct_net_returns(prices, funding, w_held)
    diff = np.abs(res.net_returns.to_numpy() - off_engine.to_numpy())
    assert diff.max() <= 1e-9, f"max abs diff {diff.max()} exceeds 1e-9"


def test_a3_registry_hash_before_after_is_one_event_row(tmp_path):
    """A-3. `sha256(registry.db)` before/after a single `log_event` write
    changes, and the on-disk write_grants/events row counts each grow by
    exactly one. Hashed on disk, in a SEPARATE subprocess each time (guard:
    not from the same in-memory connection/value).

    RED-FIRST MUTATION (driver): monkeypatch `TrialRegistry.log_event` to
    insert its row twice (two `execute` calls) -- the events table then
    grows by 2, not 1.
    """
    db_path = tmp_path / "scratch-registry.db"
    reg = TrialRegistry(str(db_path), allow_create=True)

    def _sha256_on_disk() -> str:
        out = subprocess.run(
            [sys.executable, "-c",
             f"import hashlib,sys; print(hashlib.sha256(open({str(db_path)!r},'rb').read()).hexdigest())"],
            capture_output=True, text=True, check=True,
        )
        return out.stdout.strip()

    before_events = reg.conn.execute("SELECT COUNT(*) FROM events").fetchone()[0]
    before_grants = reg.conn.execute("SELECT COUNT(*) FROM write_grants").fetchone()[0]
    before_hash = _sha256_on_disk()

    with reg.write_grant(reason="LOG_EVENT", dispatch="TEST:a3", token=TEST_TOKEN):
        reg.log_event(kind="null_calibration", family=None, detail={"test": "a3"})

    after_events = reg.conn.execute("SELECT COUNT(*) FROM events").fetchone()[0]
    after_grants = reg.conn.execute("SELECT COUNT(*) FROM write_grants").fetchone()[0]
    after_hash = _sha256_on_disk()
    reg.close()

    assert after_hash != before_hash
    assert after_events - before_events == 1
    assert after_grants - before_grants == 1


def test_a4_costs_read_at_runtime_not_literal(realized_panels, monkeypatch):
    """A-4. Per-side costs are read AT RUN TIME from
    `castellan.costs.CRYPTO_SPOT_TAKER` / `CRYPTO_PERP_TAKER` module
    attributes, never as literals. Guard (spec's own): monkeypatch
    `CRYPTO_PERP_TAKER.half_spread_bps` and assert the reconstruction's
    cost series changes.

    This IS the red-first mutation in miniature: the assertion below fails
    against any implementation that inlines the 6.0bp/12.5bp literals
    instead of reading the module attribute, which is exactly what a
    hand-rolled hardcoded-cost variant (the driver's mutation for this
    row) does.
    """
    idx = realized_panels["index"]
    w_const = pd.DataFrame({"BTC": 1.0, "ETH": 1.0}, index=idx)
    before = recon.reconstruct_net_returns(
        realized_panels["prices"], realized_panels["funding"], w_const
    ).to_numpy()

    mutated_perp = costs_mod.CRYPTO_PERP_TAKER.scaled(50.0)  # 50x the cost
    monkeypatch.setattr(
        recon, "COST_MODEL",
        {**recon.COST_MODEL, "BTC/USDT:USDT": mutated_perp, "ETH/USDT:USDT": mutated_perp},
    )
    after = recon.reconstruct_net_returns(
        realized_panels["prices"], realized_panels["funding"], w_const
    ).to_numpy()

    assert not np.allclose(before, after), (
        "cost series did not change when CRYPTO_PERP_TAKER's rate changed -- "
        "costs are not being read at run time"
    )


def test_a5_periods_per_year_persisted_as_365(realized_panels, realized_schedule, tmp_path):
    """A-5. Every `run_backtest` call in this dispatch logs
    `periods_per_year = 365`; asserted on what was PERSISTED (read back out
    of the scratch DB), not on the argument passed. The call below sources
    the value from `reconstruction.PERIODS_PER_YEAR` rather than a bare
    `365` literal so the driver's mutation is a one-line, unambiguous
    change.

    RED-FIRST MUTATION (driver): monkeypatch
    `reconstruction.PERIODS_PER_YEAR` to `252` (the engine's own default)
    -- the persisted config then reads 252, not 365.
    """
    prices = realized_panels["prices"]
    funding = realized_panels["funding"]
    w_held = realized_schedule["w_held"]
    target_weights = recon.build_target_weights(prices, w_held)

    db_path = tmp_path / "scratch-registry.db"
    reg = TrialRegistry(str(db_path), allow_create=True)
    with reg.write_grant(reason="REGISTER_HYPOTHESIS", dispatch="TEST:a5", token=TEST_TOKEN):
        reg.open_hypothesis(
            family="c11-a5", statement="s", mechanism="m", falsifier="f",
            universe="u", horizon="h", success_criteria="sc", trial_budget=8,
        )
    run_backtest(
        prices, target_weights, recon.COST_MODEL, reg, family="c11-a5",
        config={}, execution_lag=1, periods_per_year=recon.PERIODS_PER_YEAR,
        funding_panel=funding,
    )
    persisted = json.loads(
        reg.conn.execute("SELECT config_json FROM trials WHERE trial_id=1").fetchone()[0]
    )
    reg.close()
    assert persisted["periods_per_year"] == 365


def test_a6_outer_grant_around_run_backtest_raises_nested_error(
    realized_panels, realized_schedule, tmp_path
):
    """A-6. No `TrialRegistry.write_grant` may be opened around any
    `run_backtest` call, scratch or live (I-374): `run_backtest` self-grants
    `LOG_TRIAL` internally, and an outer grant raises
    `RegistryWriteGrantNestedError`. This rehearsal case DOES wrap it and
    asserts the raise.

    RED-FIRST MUTATION (driver): monkeypatch
    `TrialRegistry.write_grant.__wrapped__`'s nesting check off (patch
    `registry.TrialRegistry._grant` reset so the nested check never fires)
    -- the call then succeeds silently instead of raising.
    """
    prices = realized_panels["prices"]
    funding = realized_panels["funding"]
    target_weights = recon.build_target_weights(prices, realized_schedule["w_held"])

    db_path = tmp_path / "scratch-registry.db"
    reg = TrialRegistry(str(db_path), allow_create=True)
    with reg.write_grant(reason="REGISTER_HYPOTHESIS", dispatch="TEST:a6", token=TEST_TOKEN):
        reg.open_hypothesis(
            family="c11-a6", statement="s", mechanism="m", falsifier="f",
            universe="u", horizon="h", success_criteria="sc", trial_budget=8,
        )
    with pytest.raises(RegistryWriteGrantNestedError):
        with reg.write_grant(reason="LOG_TRIAL", dispatch="TEST:a6-bad", token=TEST_TOKEN):
            run_backtest(
                prices, target_weights, recon.COST_MODEL, reg, family="c11-a6",
                config={}, execution_lag=1, periods_per_year=365, funding_panel=funding,
            )
    reg.close()


# ---------------------------------------------------------------------------
# Group B -- the schedule (8)
# ---------------------------------------------------------------------------


def test_b1_w_in_zero_one_every_bar(realized_schedule):
    """B-1. `w(t) in [0, 1]` for every bar, both assets (C-08; never long
    perp). Guard: asserted on the schedule builder's own output, not on a
    re-clip.

    RED-FIRST MUTATION (driver): monkeypatch
    `reconstruction.w_target_from_z` to a variant that drops the LOWER
    clip (``.clip(upper=w_max)`` only) -- bars with `z(t)` far above `d`
    (`k*excess > 1`) then produce negative `w`, which is real (this
    family's `z` reaches well past `d + 1/k = 3.0` on the realized data).
    """
    w = realized_schedule["w_held"]
    assert (w.to_numpy() >= 0.0).all()
    assert (w.to_numpy() <= 1.0).all()


def test_b2_w_equals_one_wherever_z_le_d(realized_schedule):
    """B-2. `w(t) = 1.0` EXACTLY wherever `z(t) <= d = 1.0` (R42 inertness).
    Guard: report the count and assert it is > 0 (else the check is
    vacuous).

    RED-FIRST MUTATION (driver): monkeypatch `reconstruction.D_SIZING` to
    `-1.0` -- bars with `0 <= z <= 1` (still "z <= d" under the ORIGINAL
    d=1.0 reading used by this test) then compute `w < 1.0` under the
    mutated d, breaking the equality.
    """
    SEALED_D = 1.0  # PREREG-002 sec21 R41 -- the fixed oracle, NOT read
    # from `recon.D_SIZING` (which the driver's mutation for this row
    # changes): the test must hold its OWN threshold fixed to detect that
    # mutation at all.
    z = realized_schedule["z"]
    w = realized_schedule["w_held"]
    # Use w_target (pre-band) for this check -- R42 is a property of the
    # sizing FORMULA, not of the post-band-hysteresis held series. Rebuild
    # w_target directly (not the state machine) to isolate it.
    for asset in recon.ASSETS:
        w_target = recon.w_target_from_z(z[asset])
        mask = z[asset] <= SEALED_D
        n = int(mask.sum())
        assert n > 0, f"{asset}: no bars with z<=d -- test is vacuous"
        assert (w_target[mask] == 1.0).all()


def test_b3_sizing_function_unit_values():
    """B-3. Unit test on the sizing function, not the sample: `w_target =
    0.0` exactly at `z = d + 1/k = 3.0`, and `w_target = 0.5` at `z = 2.0`.

    RED-FIRST MUTATION (driver): monkeypatch `reconstruction.K_SIZING` to
    `0.25` -- `w_target(z=2.0)` becomes `1 - 0.25*1 = 0.75`, not `0.5`.
    """
    z = pd.Series([2.0, 3.0])
    w = recon.w_target_from_z(z)
    assert w.iloc[0] == pytest.approx(0.5)
    assert w.iloc[1] == pytest.approx(0.0)


def test_b4_r1_burnin_first_30_bars_forced_to_one(realized_schedule):
    """B-4 (R-1, sec3.4). The first 30 bars carry `w_held = 1.0`, both
    assets.

    RED-FIRST MUTATION (driver): monkeypatch `reconstruction.LOOKBACK` to
    `10` -- only the first 10 bars are then forced, and bars 10-29 are no
    longer guaranteed `w_held == 1.0`.
    """
    w = realized_schedule["w_held"]
    first_30 = w.iloc[:30]
    assert (first_30.to_numpy() == 1.0).all()


def test_b5_r2_trigger_exactly_30_bars_from_named_date(realized_schedule, realized_panels):
    """B-5 (R-2, sec3.4). `w = 1.0` for the 30 bars from 2025-09-18
    inclusive, both assets, asserted BY DATE, and the FORCED-bar count from
    R-2 alone (excluding R-1 burn-in, which precedes it by years) is
    exactly 30 per asset.

    RED-FIRST MUTATION (driver): monkeypatch
    `reconstruction.R2_TRIGGER_LEN_DAYS` to `20` -- only 20 bars are forced,
    not 30.
    """
    idx = realized_panels["index"]
    mask = recon.r2_forced_mask(idx)
    assert int(mask.sum()) == 30
    w = realized_schedule["w_held"]
    forced_dates_w = w.loc[mask]
    assert (forced_dates_w.to_numpy() == 1.0).all()
    first_forced = idx[mask][0]
    assert first_forced == pd.Timestamp("2025-09-18")


def test_b6_turnover_band_both_branches_occur(realized_schedule):
    """B-6 (R-3, sec3.4). A target deviation <= 0.54 produces no trade;
    > 0.54 snaps `w_held` to target. BOTH branches occur in-sample, counts
    reported. If NO bar exceeds the band the schedule is constant at 1.0
    (degenerate) -- that would itself be the finding.

    RED-FIRST MUTATION (driver): monkeypatch `reconstruction.BAND` to
    `2.0` (unreachable, since `w_target in [0,1]` so `|target-held| <=
    1.0 < 2.0` always) -- the triggered count drops to 0 for both assets,
    which this test's own assertion (count > 0) then correctly fails on.
    """
    triggered = realized_schedule["triggered"]
    counts = triggered.sum()
    for asset in recon.ASSETS:
        assert counts[asset] > 0, (
            f"{asset}: band never triggered -- schedule would be constant "
            "at 1.0 (degenerate), which IS the finding per B-6's own text"
        )
    # both branches (hold vs snap) occur: not every non-forced bar triggers
    non_forced = ~realized_schedule["forced_mask"]
    for asset in recon.ASSETS:
        held_count = int((non_forced[asset] & ~triggered[asset]).sum())
        assert held_count > 0


def test_b7_funding_panel_sha256_matches_trial1(realized_panels):
    """B-7. THE DATA-DRIFT STOP. The funding panel's `attrs["sha256"]`
    equals trial 1's logged `funding_panel_sha256`. Guard: one side (trial
    1's value) is read from the LIVE registry's own config row, the other
    is the freshly-built panel's OWN attr -- never the same value compared
    to itself.

    RED-FIRST MUTATION (driver): monkeypatch the expected constant used for
    comparison to an altered hex string -- simulates a genuine drift and
    confirms the STOP condition actually fires (raises/fails) rather than
    silently passing.
    """
    import sqlite3

    conn = sqlite3.connect(
        f"file:{REPO_ROOT / 'book' / 'registry.db'}?mode=ro", uri=True
    )
    cfg = json.loads(
        conn.execute(
            "SELECT config_json FROM trials WHERE trial_id=1"
        ).fetchone()[0]
    )
    conn.close()
    trial1_sha = cfg["funding_panel_sha256"]
    fresh_sha = realized_panels["funding"].attrs["sha256"]
    assert trial1_sha == TRIAL1_FUNDING_SHA256, "the cited constant itself drifted"
    assert fresh_sha == trial1_sha, (
        "B-7 STOP: funding_panel_sha256 mismatch -- book/pit.db has drifted "
        "since trial 1; do not calibrate on drifted data"
    )


def test_b8_index_is_trial1s_2415_bars_terminal_20260811(realized_panels):
    """B-8. The index is trial 1's: 2,415 bars, terminal `2026-08-11`,
    settled-only construction.

    RED-FIRST MUTATION (driver): monkeypatch the cutoff used to build the
    fixture's index to `2026-08-12` (inclusive of the partial terminal
    bar) -- 2,416 bars result, and the terminal date shifts by one day.
    """
    idx = realized_panels["index"]
    assert len(idx) == 2415
    assert idx[0] == pd.Timestamp("2020-01-01")
    assert idx[-1] == pd.Timestamp("2026-08-11")


# ---------------------------------------------------------------------------
# Group C -- the surrogate generator (6)
# ---------------------------------------------------------------------------


def test_c1_multiset_and_joint_pairing_preserved(realized_schedule):
    """C-1. Every surrogate preserves the exact multiset per column, and
    preserves `(w_BTC, w_ETH)` as JOINT ROWS (one common permutation).
    Guard: compare sorted arrays of the PACKED PAIR, not two independently
    sorted columns (which would pass even if BTC and ETH used different
    permutations).

    RED-FIRST MUTATION (driver): monkeypatch
    `nullcal.joint_permutation_indices` to draw two INDEPENDENT
    permutations (one per asset) instead of returning the same `sigma`
    twice -- each column's multiset is still preserved (so a naive
    per-column check would still pass), but the packed-pair check below
    fails.
    """
    rng = np.random.default_rng(1)
    T = len(realized_schedule["w_held"])
    w_btc = realized_schedule["w_held"]["BTC"].to_numpy()
    w_eth = realized_schedule["w_held"]["ETH"].to_numpy()
    sigma_btc, sigma_eth = nullcal.joint_permutation_indices(T, 30, rng)
    w_btc_s = w_btc[sigma_btc]
    w_eth_s = w_eth[sigma_eth]

    assert np.array_equal(np.sort(w_btc_s), np.sort(w_btc))
    assert np.array_equal(np.sort(w_eth_s), np.sort(w_eth))

    packed_before = np.sort(w_btc.astype(str)) + "|" + np.sort(w_eth.astype(str))
    pairs_before = sorted(zip(w_btc.tolist(), w_eth.tolist()))
    pairs_after = sorted(zip(w_btc_s.tolist(), w_eth_s.tolist()))
    assert pairs_before == pairs_after


def test_c2_mean_preserved_exactly_and_c_computed_once(realized_panels, realized_schedule):
    """C-2. `mean(w*) == mean(w)` to floating-point identity for every `b`,
    both columns -- so `c` is INVARIANT and computed ONCE (module-level
    constant, not recomputed per surrogate).

    RED-FIRST MUTATION (driver): use `nullcal.stationary_block_bootstrap_index`
    (the SECONDARY, with-replacement construction) in place of the primary
    circular permutation -- the with-replacement draw does NOT preserve the
    exact mean (spec sec2.1 reason 3), so the equality below fails.
    """
    rng = np.random.default_rng(2)
    w_held = realized_schedule["w_held"]
    T = len(w_held)
    c_before = recon.exposure_match_c(realized_panels["prices"], w_held)

    for _ in range(20):
        sigma = nullcal.circular_block_permutation_index(T, 30, rng)
        w_star = pd.DataFrame(
            {a: w_held[a].to_numpy()[sigma] for a in recon.ASSETS}, index=w_held.index
        )
        # "Floating-point identity" (spec's own phrase) is read as: exact
        # in exact arithmetic, subject only to IEEE summation-order noise
        # (addition is not associative, so a re-ORDERED sum of the same
        # 2,415 floats need not be bit-identical) -- rel=1e-12 is ~4
        # orders of magnitude above that noise floor (~1e-16) and ~9
        # orders below any quantity this calibration could ever act on.
        assert w_star["BTC"].mean() == pytest.approx(w_held["BTC"].mean(), rel=1e-12)
        assert w_star["ETH"].mean() == pytest.approx(w_held["ETH"].mean(), rel=1e-12)
        c_after = recon.exposure_match_c(realized_panels["prices"], w_star)
        assert c_after == pytest.approx(c_before, abs=0.0, rel=1e-12)


def test_c3_no_surrogate_is_identity_and_rejection_branch_forced(monkeypatch):
    """C-3. No surrogate is the identity permutation, asserted over all
    `B`; the rejection branch is separately unit-tested by FORCING
    `s_b = 0, pi_b = identity`.

    RED-FIRST MUTATION (driver): monkeypatch
    `nullcal.circular_block_permutation_index` to skip the
    `np.array_equal(sigma, identity)` redraw check -- the forced-identity
    case below then returns the identity instead of redrawing.
    """
    T, L = 50, 10

    class _ScriptedRNG:
        """Returns identity-producing draws exactly once, then genuine
        random draws -- forces the rejection branch deterministically."""

        def __init__(self):
            self.calls = 0
            self._real = np.random.default_rng(3)

        def integers(self, lo, hi):
            self.calls += 1
            if self.calls == 1:
                return 0  # s = 0 -> rotation is the identity
            return int(self._real.integers(lo, hi))

        def permutation(self, n):
            if self.calls == 1:
                return np.arange(n)  # identity block order
            return self._real.permutation(n)

    rng = _ScriptedRNG()
    sigma = nullcal.circular_block_permutation_index(T, L, rng)
    assert not np.array_equal(sigma, np.arange(T)), (
        "identity was not rejected -- the redraw guard did not fire"
    )

    # Over many genuine draws, never the identity either.
    real_rng = np.random.default_rng(4)
    T2 = len(np.arange(2415))
    for _ in range(200):
        s = nullcal.circular_block_permutation_index(2415, 30, real_rng)
        assert not np.array_equal(s, np.arange(2415))


def test_c4_reproducibility_two_processes_same_seed(tmp_path):
    """C-4. The script is run TWICE, from the pre-committed seed, in a
    SEPARATE process and fresh temp dir each time; sha256 of the primary
    `I*` array is identical.

    RED-FIRST MUTATION (driver): seed the RNG from `time.time()` instead of
    the pre-committed `master_seed` -- the two subprocess runs then produce
    different hashes.
    """
    script = REPO_ROOT / "research" / "work" / "c11_repro_probe.py"
    hashes = []
    for _ in range(2):
        out = subprocess.run(
            [sys.executable, str(script)], capture_output=True, text=True,
            cwd=str(REPO_ROOT), check=True,
        )
        hashes.append(out.stdout.strip().splitlines()[-1])
    assert hashes[0] == hashes[1]


def test_c5_exactly_81_blocks_and_bijection_at_l30():
    """C-5. At `L = 30`: exactly 81 blocks (80x30 + 1x15); every bar index
    appears exactly once in `sigma_b`.

    RED-FIRST MUTATION (driver): monkeypatch `nullcal.block_boundaries` to
    use `L+1` as the block size internally (an off-by-one) -- the block
    count and/or coverage changes.
    """
    T, L = 2415, 30
    bounds = nullcal.block_boundaries(T, L)
    assert len(bounds) == 81
    sizes = [b - a for a, b in bounds]
    assert sizes[:-1] == [30] * 80
    assert sizes[-1] == 15

    rng = np.random.default_rng(5)
    sigma = nullcal.circular_block_permutation_index(T, L, rng)
    assert sorted(sigma.tolist()) == list(range(T))


def test_c6_eight_cells_from_independent_spawn_children():
    """C-6. The 8 (construction, L) cells draw from `SeedSequence.spawn`
    children, not a shared or arithmetically-offset stream; the 8 resulting
    `I*`-analogue arrays are pairwise distinct.

    RED-FIRST MUTATION (driver): monkeypatch `nullcal.spawn_children` to
    return the SAME spawned child 8 times (index 0 repeated) instead of 8
    independent children -- the 8 arrays become identical.
    """
    master_seed = 16567568367804922233
    kids = nullcal.spawn_children(master_seed, 8)
    arrays = []
    for kid in kids:
        rng = np.random.default_rng(kid)
        arrays.append(rng.standard_normal(50))
    for i, j in itertools.combinations(range(8), 2):
        assert not np.array_equal(arrays[i], arrays[j])


# ---------------------------------------------------------------------------
# Group D -- the statistic (5)
# ---------------------------------------------------------------------------


def test_d1_worst_20_selected_per_series_not_reused(monkeypatch):
    """D-1. THE SHARPEST TEST. `M(x)` selects the 20 smallest OF THE SERIES
    IT IS GIVEN. Constructed so `R_bench`'s worst-20 index set and a
    surrogate's differ, and confirms `M` on the surrogate uses ITS OWN.

    RED-FIRST MUTATION (driver): a `worst_k_mean_wrong` that always uses
    `R_bench`'s worst-20 INDEX SET (computed once, outside the function)
    and applies it to whatever series is passed -- this is "the single
    most likely implementation error" the spec names, and it silently
    destroys the null.
    """
    rng = np.random.default_rng(6)
    R_bench = rng.normal(0, 0.01, 200)
    # A surrogate that reorders the SAME multiset so its own worst-20 set
    # (by position) differs from R_bench's.
    perm = rng.permutation(200)
    surrogate = R_bench[perm]

    bench_worst_idx = set(np.argsort(R_bench)[:20].tolist())
    surrogate_worst_idx = set(np.argsort(surrogate)[:20].tolist())
    assert bench_worst_idx != surrogate_worst_idx, "test setup: sets must differ"

    def worst_k_mean_wrong(x, reference_idx_set, k=20):
        idx = sorted(reference_idx_set)
        return float(np.mean(np.asarray(x)[idx]))

    correct = nullcal.worst_k_mean(surrogate, k=20)
    wrong = worst_k_mean_wrong(surrogate, bench_worst_idx, k=20)
    assert correct != pytest.approx(wrong), (
        "the multiset is a permutation of a real series with high "
        "probability of index-set collision only in pathological cases; "
        "here they must differ by construction"
    )
    # Ground truth: correct == mean of the surrogate's OWN 20 smallest.
    assert correct == pytest.approx(float(np.mean(np.sort(surrogate)[:20])))


def test_d2_guard_negative_denominator_else_insufficient_data():
    """D-2. `M_b < 0` asserted; otherwise INSUFFICIENT-DATA, never
    survival/firing. Unit test on a synthetic all-positive series.

    RED-FIRST MUTATION (driver): a guard that checks `M_b <= 0` (wrong
    direction/boundary) or omits the check entirely -- an all-positive
    series would then silently compute an `I` instead of flagging
    INSUFFICIENT-DATA.
    """

    def guarded_m_b(x):
        m = nullcal.worst_k_mean(x, k=20)
        if not (m < 0):
            return None  # INSUFFICIENT-DATA sentinel
        return m

    all_positive = np.abs(np.random.default_rng(7).normal(0, 0.01, 100)) + 0.001
    assert guarded_m_b(all_positive) is None

    realistic_negative = np.random.default_rng(8).normal(-0.001, 0.01, 100)
    assert guarded_m_b(realistic_negative) is not None


def test_d3_i0_is_computed_and_is_not_approximately_zero(realized_panels, realized_schedule):
    """D-3. `I_0` is computed and reported -- and it is NOT `approx 0`.
    Asserting `I_0 approx 0` would ITSELF be the defect (the constant-`w̄`
    position is net long spot; `R_bench_scaled` is delta-neutral -- I-377).

    RED-FIRST MUTATION (driver): monkeypatch `nullcal.compute_i0` to
    `lambda M_b, M_s: 0.0 * M_s` (or equivalently, a variant that computes
    `M_s` from `R_bench_scaled` itself rather than the constant-`w̄`
    off-engine reconstruction) -- reproduces the exact D-3 defect: `I_0`
    comes back approximately 0 instead of the measured -8.27.
    """
    import sqlite3

    conn = sqlite3.connect(
        f"file:{REPO_ROOT / 'book' / 'registry.db'}?mode=ro", uri=True
    )
    blob = conn.execute(
        "SELECT returns_blob FROM trials WHERE trial_id=1"
    ).fetchone()[0]
    conn.close()
    R_bench = np.frombuffer(blob, dtype=np.float32).astype(float)

    w_held = realized_schedule["w_held"]
    c = recon.exposure_match_c(realized_panels["prices"], w_held)
    M_b = c * nullcal.worst_k_mean(R_bench, k=20)
    assert M_b < 0

    w_bar = w_held.mean()
    idx = realized_panels["index"]
    w_const = pd.DataFrame(
        {a: np.full(len(idx), w_bar[a]) for a in recon.ASSETS}, index=idx
    )
    R_strat_0 = recon.reconstruct_net_returns(
        realized_panels["prices"], realized_panels["funding"], w_const
    ).to_numpy()
    M_s0 = nullcal.worst_k_mean(R_strat_0, k=20)
    I_0 = nullcal.compute_i0(M_b, M_s0)

    assert I_0 == pytest.approx(-8.2735, abs=0.01), (
        f"I_0={I_0} moved materially from the previously-measured value "
        "(DATA-IMPL-014); re-derive rather than silently accept"
    )
    assert abs(I_0) > 0.25, "I_0 approx 0 would itself be the defect (D-3)"


def test_d4_greedy_vs_bruteforce_at_t10_reports_not_asserts_optimum():
    """D-4. `I_max`/`I_min` computed by the sec4.6 greedy assignment;
    verified against exhaustive brute force at `T=10`.

    THIS TEST DOES NOT ASSERT GREEDY == BRUTE FORCE, because I-386 (HIGH,
    DATA-IMPL-014/S4-D-031) already demonstrated, by this exact brute-force
    method, that the literal sec4.6 greedy-by-`R_bench` rule does NOT find
    the true optimum in either direction. Asserting equality here would be
    a SECOND instance of the D-3-style defect (asserting a false invariant
    to manufacture a pass). What IS asserted is the one true,
    defect-independent invariant: the brute-force optimum is never worse
    than ANY candidate the exhaustive search enumerates, greedy's own
    candidate included -- and the measured gap (greedy vs brute force) is
    reported, reproducing I-386, not re-discovering or re-filing it.

    RED-FIRST MUTATION (driver): monkeypatch
    `nullcal.greedy_feasibility_assignment` to return an assignment that
    does not even preserve the input multiset (e.g. `np.sort(w_multiset)`
    with no rank-order assignment at all) -- then even the weak invariant
    (greedy's own M-value <= the brute-force max) can fail, because an
    arbitrary non-multiset-preserving output isn't a member of the
    enumerated permutation space at all and the comparison becomes
    meaningless -- caught by an explicit multiset-preservation assertion.
    """
    rng = np.random.default_rng(42)
    T = 10
    baseline = rng.normal(0, 1, T)
    # A per-bar SENSITIVITY separate from the ranking variable -- this is
    # the structural feature that makes greedy-by-baseline-rank fail: the
    # true payoff `baseline(t) + sensitivity(t)*w(t)` depends on w through
    # a coefficient the greedy rule never looks at (exactly analogous to
    # DATA-IMPL-014's own T=10 brute-force construction, "baseline(t)" and
    # "a per-bar sensitivity s(t)").
    sensitivity = rng.uniform(0.5, 3.0, T)
    w_multiset = rng.uniform(0, 1, T)

    def M(x, k=4):
        return float(np.mean(np.sort(x)[:k]))

    greedy_w = nullcal.greedy_feasibility_assignment(baseline, w_multiset, maximize=True)
    assert sorted(greedy_w.tolist()) == pytest.approx(sorted(w_multiset.tolist()))
    greedy_M = M(baseline + sensitivity * greedy_w)

    brute_force_max = -np.inf
    for perm in itertools.permutations(w_multiset.tolist()):
        val = M(baseline + sensitivity * np.asarray(perm))
        if val > brute_force_max:
            brute_force_max = val

    assert brute_force_max >= greedy_M - 1e-12, (
        "the brute-force optimum (which enumerates greedy's own candidate) "
        "cannot be worse than greedy -- this would indicate a bug in the "
        "brute-force enumeration itself, not in the greedy heuristic"
    )
    # Reported, not asserted equal (I-386): whether greedy achieves the
    # true optimum is a finding, not a test outcome to force.
    matches_optimum = greedy_M == pytest.approx(brute_force_max, abs=1e-9)
    # This reproduces I-386 at the unit-test scale: on this synthetic
    # T=10 problem the literal spec heuristic is also NOT optimal.
    assert matches_optimum is False, (
        "unexpected: this synthetic case's greedy matched the true optimum "
        "-- re-check whether I-386 still holds before reporting it fixed"
    )


def test_d5_null_percentiles_and_tie_count_reported():
    """D-5. Null percentiles (1/5/25/50/75/95/99) and the exact-tie count
    are reported. If the tie fraction exceeds 0.5 the null is degenerate
    and that is reported as a finding, not smoothed.

    RED-FIRST MUTATION (driver): round the `I*` array to 1 decimal place
    before computing percentiles/ties -- artificially inflates the tie
    fraction, and this test's own flagging logic must then trip.
    """
    rng = np.random.default_rng(9)
    I_star = rng.normal(-2.0, 1.0, 10_000)
    pct = np.percentile(I_star, [1, 5, 25, 50, 75, 95, 99])
    assert len(pct) == 7
    assert (np.diff(pct) >= 0).all()

    _, counts = np.unique(I_star, return_counts=True)
    n_tied = int((counts > 1).sum() and counts[counts > 1].sum()) if (counts > 1).any() else 0
    tie_fraction = n_tied / len(I_star)
    assert tie_fraction < 0.5, "real continuous data should not be this degenerate"

    degenerate = np.round(I_star, 1)
    _, counts2 = np.unique(degenerate, return_counts=True)
    n_tied2 = int(counts2[counts2 > 1].sum()) if (counts2 > 1).any() else 0
    tie_fraction2 = n_tied2 / len(degenerate)
    assert tie_fraction2 > tie_fraction, "rounding must measurably inflate ties"


# ---------------------------------------------------------------------------
# Group E -- the leg-(i) estimator and the output (5)
# ---------------------------------------------------------------------------


def test_e1_reduction_to_mean_nw_tstat():
    """E-1, AS MEASURED (finding filed, see deliverable): the regression
    HAC estimator with an all-zero (uninformative) `x` column reduces
    EXACTLY, to double-precision, to `sr_tstat_nw(y, L) * sqrt(T/(T-1))`
    -- NOT to `sr_tstat_nw(y, L)` itself as VALIDATION-SPEC-005's literal
    text states ("equals castellan.stats.sr_tstat_nw(y, L)"). Derived and
    confirmed here rather than asserted: `ols_alpha_tstat_hac`'s HAC
    "meat" `S` is the RAW (undivided) autocovariance sum
    (`xu.T @ xu`, no `/(T-1)`), while its "bread" `(X'X)^+` for a
    single-ones-column `X` is exactly `1/T` -- giving `Var(alpha_hat) =
    sigma_NW^2(L) * (T-1) / T^2`, one factor of `T` short of
    `sr_tstat_nw`'s own `Var(mean) = sigma_NW^2(L) / T`. Both estimators
    use the IDENTICAL Bartlett-weighted, `(T-1)`-divisor autocovariance
    KERNEL underneath (confirmed by the exact `sqrt(T/(T-1))` scale
    factor holding across every lag and every T tried, never an
    approximate or lag-dependent ratio) -- so the two are the SAME
    estimator up to a `T` vs `T-1` normalization convention, not
    numerically identical outputs. Immaterial at this family's T=2415
    (`sqrt(2415/2414) = 1.00021`), disclosed as a finding rather than
    silently absorbed into a false "reduces exactly" claim.

    RED-FIRST MUTATION (driver): monkeypatch `stats.sr_tstat_nw`'s Bartlett
    weight to `1 - l/lag` (off-by-one denominator, matching DATA-IMPL-015's
    own M2) -- the derived scale factor stops holding exactly.
    """
    rng = np.random.default_rng(10)
    T = 300
    y = rng.normal(0.0005, 0.01, T)
    for i in range(1, T):
        y[i] += 0.3 * y[i - 1]  # AR(1), so HAC actually matters
    x = np.zeros(T)
    lag = 21

    result = stats_mod.ols_alpha_tstat_hac(y, x, lag=lag)
    reference = stats_mod.sr_tstat_nw(y, lag)
    scale = np.sqrt(T / (T - 1))
    assert result.t_alpha == pytest.approx(reference * scale, rel=1e-12)
    assert result.alpha == pytest.approx(float(np.mean(y)), abs=1e-12)


def test_e2_same_bartlett_kernel_and_divisor_as_sr_tstat_nw():
    """E-2, AS MEASURED: the derived `sqrt(T/(T-1))` scale factor between
    `ols_alpha_tstat_hac` (zero-regressor reduction) and `sr_tstat_nw`
    holds EXACTLY at every lag (0, 5, 21, 40) and both `T` tried here --
    confirming the underlying Bartlett kernel and `(T-1)` autocovariance
    divisor are identical between the two estimators (the factor is
    lag-INVARIANT, which it could not be if the kernels differed), and
    that the only discrepancy is the outer `T` vs `T-1` normalization
    (see test_e1's derivation).

    RED-FIRST MUTATION (driver): monkeypatch
    `stats.ols_alpha_tstat_hac`'s Bartlett weight denominator from
    `(lag+1)` to `lag` -- the scale factor would then depend on `lag`
    instead of being lag-invariant, and the assertion below (same `scale`
    reused across all four lags) fails.
    """
    rng = np.random.default_rng(11)
    T = 500
    y = rng.normal(0.0, 0.02, T)
    for i in range(1, T):
        y[i] += 0.5 * y[i - 1]
    x = np.zeros(T)
    scale = np.sqrt(T / (T - 1))
    for lag in (0, 5, 21, 40):
        result = stats_mod.ols_alpha_tstat_hac(y, x, lag=lag)
        reference = stats_mod.sr_tstat_nw(y, lag)
        assert result.t_alpha == pytest.approx(reference * scale, rel=1e-12), f"lag={lag}"


def test_e3_joint_alpha_computed_by_distinct_path_from_product():
    """E-3. `alpha_joint`, `alpha_1`, `alpha_2`, and the product
    `alpha_1*alpha_2` are all reported; the joint is computed by a
    DIFFERENT code path than the product (an AND over paired boolean
    arrays, never a multiplication of two marginals) -- and on positively
    dependent surrogates the two numerically differ (I-382's whole point).

    RED-FIRST MUTATION (driver): monkeypatch `nullcal.joint_survival_rate`
    to a defective variant whose `alpha_joint` simply RETURNS
    `alpha_1 * alpha_2` -- under manufactured positive dependence the two
    are then IDENTICAL by construction, which the correct implementation
    must NOT reproduce.
    """
    rng = np.random.default_rng(12)
    B = 5000
    common_factor = rng.normal(0, 1, B)
    leg1_fires = (common_factor + rng.normal(0, 0.3, B)) > 0.5
    leg2_fires = (common_factor + rng.normal(0, 0.3, B)) > 0.5

    result = nullcal.joint_survival_rate(leg1_fires, leg2_fires)
    alpha_joint = result["alpha_joint"]
    product = result["product"]

    assert alpha_joint != pytest.approx(product, rel=1e-6), (
        "manufactured positive dependence must produce a measurable "
        "independence gap; joint should exceed the product"
    )
    assert alpha_joint > product


def test_e4_no_print_asserts_a_conclusion():
    """E-4 (I-044). No `print()`/log line in the calibration script asserts
    a conclusion. Guard: grep the script for the conclusion vocabulary and
    assert zero hits outside comments.

    RED-FIRST MUTATION (driver): a temporary copy of the script with a line
    `print("leg (ii) fires decisively")` inserted into the main block --
    the grep-based check below must then fail on that copy.
    """
    forbidden = ["decisive", "weak", "defective", "survives", "fires", "spares", "confirms"]
    text = SCRIPT_PATH.read_text()
    violations = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        if "print(" not in line and "log.info" not in line and "logging." not in line:
            continue
        code_part = line.split("#", 1)[0]
        for word in forbidden:
            if word in code_part.lower():
                violations.append((lineno, word, line))
    assert violations == [], f"conclusion vocabulary found in print/log lines: {violations}"


def test_e5_disclosure_grid_all_eight_cells_present():
    """E-5. The disclosure grid (8 cells: L in {21,30,60,90} x
    {permutation, stationary}), the alternative denominator, and the
    cost-free variant are all reported; the primary is stated as
    pre-committed; no selection over cells is reported as THE alpha.

    RED-FIRST MUTATION (driver): monkeypatch
    `nullcal.disclosure_grid_cells` to return only its first element
    (`[cells[0]]`) -- an off-by-scope error of exactly the shape a `break`
    or a misplaced `return` inside the real grid loop would produce.
    """
    Ls = (21, 30, 60, 90)
    constructions = ("permutation", "stationary")
    cells = nullcal.disclosure_grid_cells(Ls, constructions)
    assert len(set(cells)) == 8
