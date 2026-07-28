"""Tests that prove the harness enforces the Charter, not just implements it."""

import math

import numpy as np
import pandas as pd
import pytest

from castellan import (
    TrialRegistry, PreRegistrationError, HoldoutVault, HoldoutRetiredError,
    run_backtest, SameBarFillError, US_EQUITY_LARGE, evaluate_gate1, stats,
)
from castellan.cv import purged_kfold_splits, walk_forward_windows

RNG = np.random.default_rng(42)


@pytest.fixture
def registry(tmp_path):
    reg = TrialRegistry(str(tmp_path / "registry.db"))
    reg.open_hypothesis(
        family="demo",
        statement="Asset A mean-reverts over 1 day",
        mechanism="Liquidity providers demand a premium after imbalance",
        falsifier="Rolling 1y net Sharpe below 0 for 2 consecutive quarters",
        universe="A,B",
        horizon="1d",
        success_criteria="Gate 1",
        trial_budget=50,
    )
    return reg


def make_prices(n=1200, n_assets=2, drift=0.0002, seed=1):
    rng = np.random.default_rng(seed)
    rets = rng.normal(drift, 0.01, size=(n, n_assets))
    idx = pd.bdate_range("2020-01-01", periods=n)
    cols = [f"A{i}" for i in range(n_assets)]
    return pd.DataFrame(100 * np.exp(np.cumsum(rets, axis=0)), index=idx, columns=cols)


# ----------------------------------------------------------------------
# Registry enforcement
# ----------------------------------------------------------------------

def test_backtest_requires_preregistration(tmp_path):
    reg = TrialRegistry(str(tmp_path / "r.db"))
    prices = make_prices()
    w = prices * 0.0
    with pytest.raises(PreRegistrationError):
        run_backtest(prices, w, US_EQUITY_LARGE, reg, "unregistered", {})


def test_every_run_increments_n(registry):
    prices = make_prices()
    w = prices * 0.0 + 0.1
    assert registry.family_stats("demo").n_trials == 0
    for k in range(3):
        run_backtest(prices, w, US_EQUITY_LARGE, registry, "demo", {"variant": k})
    fs = registry.family_stats("demo")
    assert fs.n_trials == 3
    assert fs.sr_period_std is not None  # dispersion available for DSR


def test_preregistration_requires_falsifier(tmp_path):
    reg = TrialRegistry(str(tmp_path / "r.db"))
    with pytest.raises(ValueError):
        reg.open_hypothesis("x", "claim", "mechanism", "  ", "u", "1d", "sc", 10)


# ----------------------------------------------------------------------
# Engine correctness
# ----------------------------------------------------------------------

def test_same_bar_fill_refused(registry):
    prices = make_prices()
    w = prices * 0.0
    with pytest.raises(SameBarFillError):
        run_backtest(prices, w, US_EQUITY_LARGE, registry, "demo", {},
                     execution_lag=0)


def test_lookahead_signal_is_neutralized_by_lag(registry):
    """A 'perfect foresight' signal (weight = sign of same-bar return)
    would be wildly profitable with lag 0; with the enforced lag >= 1 it
    must collapse to ~nothing on iid data."""
    prices = make_prices(n=2000, drift=0.0, seed=3)
    rets = prices.pct_change().fillna(0.0)
    cheat = np.sign(rets)  # knows the current bar's return
    res = run_backtest(prices, cheat, US_EQUITY_LARGE, registry, "demo",
                       {"variant": "cheat"})
    t = stats.sr_tstat(res.net_returns.values)
    assert abs(t) < 3.0  # foresight destroyed by the mandatory lag


def test_costs_reduce_returns(registry):
    prices = make_prices(seed=5)
    rng = np.random.default_rng(0)
    w = pd.DataFrame(rng.uniform(-0.5, 0.5, size=prices.shape),
                     index=prices.index, columns=prices.columns)
    res = run_backtest(prices, w, US_EQUITY_LARGE, registry, "demo", {"v": "c"})
    assert res.net_returns.sum() < res.gross_returns.sum()
    assert (res.cost_returns >= 0).all()


# ----------------------------------------------------------------------
# Statistics
# ----------------------------------------------------------------------

def test_expected_max_sharpe_matches_charter_table():
    # Charter 4.1 table, in units of sigma_SR
    for n, expected in [(10, 1.57), (100, 2.53), (1000, 3.26), (10000, 3.86)]:
        assert abs(stats.expected_max_sharpe(n) - expected) < 0.05


def test_dsr_rejects_selected_noise():
    """Best of 200 noise strategies has a high raw Sharpe but must be
    deflated to ~nothing given honest N."""
    rng = np.random.default_rng(11)
    T, N = 1000, 200
    trials = rng.normal(0, 0.01, size=(T, N))
    srs = trials.mean(axis=0) / trials.std(axis=0, ddof=1)
    best = trials[:, np.argmax(srs)]
    assert stats.sharpe_annual(best) > 1.0  # looks great...
    dsr = stats.deflated_sharpe_ratio(best, n_trials=N,
                                      trial_sr_std_period=float(srs.std(ddof=1)))
    assert dsr < 0.95  # ...and is correctly rejected


def test_dsr_accepts_genuine_edge():
    rng = np.random.default_rng(12)
    T = 1500
    edge = rng.normal(0.0012, 0.01, size=T)  # ~SR 1.9 annualized, real
    dsr = stats.deflated_sharpe_ratio(edge, n_trials=10,
                                      trial_sr_std_period=0.02)
    assert dsr > 0.95


def test_pbo_high_on_noise_low_on_real_edge():
    rng = np.random.default_rng(13)
    T, N = 800, 30
    noise = rng.normal(0, 0.01, size=(T, N))
    pbo_noise = stats.probability_backtest_overfitting(noise, 16, 500)
    assert pbo_noise.pbo > 0.25  # near 0.5 for pure noise

    real = noise.copy()
    real[:, 7] += 0.0025  # one genuinely strong strategy
    pbo_real = stats.probability_backtest_overfitting(real, 16, 500)
    assert pbo_real.pbo <= 0.10


def test_purged_kfold_no_overlap_and_embargo():
    for train, test in purged_kfold_splits(1000, 5, 0.01):
        assert len(np.intersect1d(train, test)) == 0
        # embargo: the 10 bars after the test fold are not in train
        after = np.arange(test[-1] + 1, min(1000, test[-1] + 11))
        assert len(np.intersect1d(train, after)) == 0


def test_walk_forward_windows_cover_and_order():
    windows = list(walk_forward_windows(1000, 10))
    assert len(windows) == 10
    for train, test in windows:
        assert train[-1] < test[0]  # strictly out of sample


# ----------------------------------------------------------------------
# Holdout vault
# ----------------------------------------------------------------------

def test_holdout_locks_splits_and_opens_once(tmp_path, registry):
    df = make_prices(n=1000)
    vault = HoldoutVault(str(tmp_path / "vault"), registry, "demo-data")
    insample = vault.lock(df, passphrase="hunter2", fraction=0.25)
    assert len(insample) == 750
    # wrong passphrase refused
    with pytest.raises(Exception):
        vault.open_once("wrong", opened_by="validation")
    held = vault.open_once("hunter2", opened_by="validation")
    assert len(held) == 250
    assert held.index[0] > insample.index[-1]
    # second open: permanently retired
    with pytest.raises(HoldoutRetiredError):
        vault.open_once("hunter2", opened_by="anyone")
    kinds = [e["kind"] for e in registry.events()]
    assert "holdout_opened" in kinds
    assert "holdout_second_open_attempt" in kinds


# ----------------------------------------------------------------------
# Gate 1
# ----------------------------------------------------------------------

def test_gate1_insufficient_without_registry_trials(tmp_path):
    reg = TrialRegistry(str(tmp_path / "r.db"))
    reg.open_hypothesis("empty", "s", "m", "f", "u", "1d", "sc", 10)
    rng = np.random.default_rng(1)
    rep = evaluate_gate1("s", "empty", reg,
                         rng.normal(0.001, 0.01, 1200), 252)
    assert rep.overall != "PASS"


def test_gate1_fails_noise_and_verdict_is_logged(registry):
    prices = make_prices(n=1300, drift=0.0, seed=9)
    rng = np.random.default_rng(2)
    for k in range(5):
        w = pd.DataFrame(rng.uniform(-0.3, 0.3, size=prices.shape),
                         index=prices.index, columns=prices.columns)
        run_backtest(prices, w, US_EQUITY_LARGE, registry, "demo", {"v": k})
    noise = rng.normal(0, 0.01, 1200)
    rep = evaluate_gate1("noise-strat", "demo", registry, noise, 252,
                         red_team_memo_present=True, kill_condition="x")
    assert rep.overall == "FAIL"
    fails = {c.name for c in rep.criteria if c.verdict == "FAIL"}
    assert any("t-statistic" in f or "Sharpe" in f for f in fails)
    assert any(e["kind"] == "gate1_verdict" for e in registry.events())


def test_gate1_report_renders(registry):
    prices = make_prices()
    w = prices * 0.0 + 0.2
    run_backtest(prices, w, US_EQUITY_LARGE, registry, "demo", {"v": 1})
    run_backtest(prices, w * 0.5, US_EQUITY_LARGE, registry, "demo", {"v": 2})
    rng = np.random.default_rng(3)
    r = rng.normal(0.0005, 0.01, 1100)
    rep = evaluate_gate1("render", "demo", registry, r, 252,
                         net_returns_at_cost_multiplier=lambda m: r - (m - 1) * 0.0002)
    md = rep.to_markdown()
    assert "Validation Report" in md and "Trial count N" in md
    assert rep.returns_sha256 and len(rep.returns_sha256) == 64
    assert rep.to_json()
