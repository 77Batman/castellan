"""Acceptance tests for VALIDATION-RULING-003 (carry accounting), I-034.

Authored by Validation as a prose specification (T-1 .. T-19,
`research/VALIDATION-RULING-003-carry-accounting.md` section 4);
transcribed here by Seat 9 into executable assertions. Per the D-012
rider, this file is written and run RED against unmodified source
BEFORE any implementation, and the verbatim red output is a required
deliverable (see `research/DATA-IMPL-004-carry-accounting.md`).

Fixtures: committed extracts of the realized `funding_rate` series for
BTC/ETH/SOL under `harness/tests/fixtures/`, sha256-checked at the top
of every test that reads one, so a silent fixture edit fails loudly
rather than quietly changing what "realized" means.

    funding_btc.csv  sha256 cdbeab9ba759560e628f9ab18f93fd01b30fdc7315b8b531207c9186baa432c5
    funding_eth.csv  sha256 64c7ee3baa65d6a00ec5599e68300fed4ccae36efe6e7ef1ed13bcd8819c5d70
    funding_sol.csv  sha256 a309fe1b564eb3389d86fa728d8d8d933b992e27739566449a8e0ff86e2ccf66

These tests must NOT read `book/pit.db` at runtime (Ruling 003 section
4: "tests must not read book/pit.db at runtime") -- every row below
comes from the committed CSV extract.
"""

from __future__ import annotations

import dataclasses
import hashlib
import math
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from castellan import (
    CostModel,
    CRYPTO_PERP_TAKER,
    CRYPTO_SPOT_TAKER,
    TrialRegistry,
    PITStore,
    run_backtest,
    pit_funding_panel,
    FundingCoverageError,
    CarryScenario,
    apply_carry_scenario,
    shift_carry_panel,
    carry_breakeven_bps_annual,
    tail_bootstrap_carry,
    evaluate_gate1,
    stats,
)

FIXTURES = Path(__file__).parent / "fixtures"

_FIXTURE_SHA256 = {
    "btc": "cdbeab9ba759560e628f9ab18f93fd01b30fdc7315b8b531207c9186baa432c5",
    "eth": "64c7ee3baa65d6a00ec5599e68300fed4ccae36efe6e7ef1ed13bcd8819c5d70",
    "sol": "a309fe1b564eb3389d86fa728d8d8d933b992e27739566449a8e0ff86e2ccf66",
}


# ----------------------------------------------------------------------
# Shared fixture / harness plumbing
# ----------------------------------------------------------------------

def _check_fixture(name: str) -> Path:
    path = FIXTURES / f"funding_{name}.csv"
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    assert actual == _FIXTURE_SHA256[name], (
        f"funding_{name}.csv sha256 drifted: expected "
        f"{_FIXTURE_SHA256[name]}, got {actual}"
    )
    return path


def _load_funding_csv(name: str) -> pd.DataFrame:
    df = pd.read_csv(_check_fixture(name))
    df["event_time"] = pd.to_datetime(df["event_time"], format="ISO8601")
    if df["event_time"].dt.tz is not None:
        df["event_time"] = df["event_time"].dt.tz_convert(None)
    return df


def _new_registry() -> TrialRegistry:
    return TrialRegistry(":memory:")


def _new_store(registry: TrialRegistry | None = None) -> PITStore:
    return PITStore(":memory:", registry=registry)


def _open_family(registry: TrialRegistry, family: str) -> str:
    # VALIDATION-RULING-006 section 5.1: a helper's own write, wrapped and
    # closed in the helper's own body.
    with registry.write_grant(reason="REGISTER_HYPOTHESIS",
                              dispatch="TEST:_open_family", token="test-token"):
        registry.open_hypothesis(
            family=family,
            statement="carry-accounting acceptance-test fixture family",
            mechanism="n/a -- harness self-test, Ruling 003",
            falsifier="n/a -- harness self-test, Ruling 003",
            universe="n/a",
            horizon="n/a",
            success_criteria="n/a",
            trial_budget=10_000,
        )
    return family


def _ingest_funding(store: PITStore, source: str, symbol: str, df: pd.DataFrame,
                     knowledge_time: float = 0.0) -> None:
    wide = df.set_index("event_time")[["value"]].rename(columns={"value": "funding_rate"})
    store.ingest(source, symbol, wide, knowledge_time=knowledge_time)


def _eod_bar_index(start, end) -> pd.DatetimeIndex:
    """Daily bars labeled at end-of-day (23:59:59.999999 UTC-naive) so a
    bar's left-open/right-closed window (prev, t] captures exactly that
    calendar day's prints without an exact-midnight boundary collision.
    """
    days = pd.date_range(pd.Timestamp(start).normalize(), pd.Timestamp(end).normalize(), freq="D")
    offset = pd.Timedelta(hours=23, minutes=59, seconds=59, microseconds=999999)
    return pd.DatetimeIndex([d + offset for d in days])


def _zero_cost(periods_per_year: int = 365) -> CostModel:
    return CostModel(name="zero", commission_bps=0.0, half_spread_bps=0.0,
                      impact_y=0.0, borrow_bps_annual=0.0,
                      periods_per_year=periods_per_year)


# ----------------------------------------------------------------------
# 4.1 Structural -- the defect cannot be re-expressed
# ----------------------------------------------------------------------

def test_t1_costmodel_has_no_funding_field():
    field_names = {f.name for f in dataclasses.fields(CostModel)}
    assert "funding" not in field_names
    assert not hasattr(CostModel, "funding_bps_annual")
    with pytest.raises(TypeError):
        CostModel(name="x", commission_bps=1.0, half_spread_bps=1.0,
                  funding_bps_annual=1095.0)
    perp_field_names = {f.name for f in dataclasses.fields(CRYPTO_PERP_TAKER)}
    assert not any("funding" in n for n in perp_field_names)


def test_t2_carry_per_bar_gone_borrow_per_bar_single_notional():
    assert not hasattr(CostModel, "carry_per_bar")
    model = CRYPTO_PERP_TAKER
    result = model.borrow_per_bar(1.0)
    assert np.isscalar(result) or hasattr(result, "shape")
    with pytest.raises(TypeError):
        model.borrow_per_bar(1.0, 2.0)


@pytest.mark.parametrize("m", [0.5, 2.0, 8.0])
def test_t3_scaled_touches_frictions_only(m):
    base = CostModel(name="base", commission_bps=10.0, half_spread_bps=4.0,
                      impact_y=1.0, impact_exponent=0.5, borrow_bps_annual=400.0,
                      periods_per_year=365)
    scaled = base.scaled(m)
    assert scaled.commission_bps == pytest.approx(base.commission_bps * m)
    assert scaled.half_spread_bps == pytest.approx(base.half_spread_bps * m)
    assert scaled.impact_y == pytest.approx(base.impact_y * m)
    assert scaled.borrow_bps_annual == pytest.approx(base.borrow_bps_annual * m)
    assert scaled.periods_per_year == base.periods_per_year
    assert scaled.impact_exponent == base.impact_exponent
    assert not any("funding" in f.name for f in dataclasses.fields(scaled))


# ----------------------------------------------------------------------
# 4.2 Sign and base -- the headline
# ----------------------------------------------------------------------

def test_t4_delta_neutral_pair_receives():
    registry = _new_registry()
    family = _open_family(registry, "t4-family")
    n = 366  # 365 active bars + 1 execution_lag warm-up bar (position 0 there)
    idx = pd.date_range("2024-01-01", periods=n, freq="D")
    prices = pd.DataFrame({"spot": [100.0] * n, "perp": [100.0] * n}, index=idx)
    weights = pd.DataFrame({"spot": [1.0] * n, "perp": [-1.0] * n}, index=idx)
    # f = 0.0001 per 8h at 3 prints/bar -> 0.0003/bar, funding on the perp leg only
    funding = pd.DataFrame({"perp": [0.0003] * n}, index=idx)

    result = run_backtest(
        prices, weights, _zero_cost(), registry, family, config={},
        execution_lag=1, periods_per_year=365, funding_panel=funding,
    )
    active = result.carry_accrual.iloc[1:]  # drop the lag warm-up bar
    annualized = active.mean() * 365
    assert annualized == pytest.approx(0.1095, abs=1e-9)
    assert result.net_returns.sum() > 0
    assert annualized != pytest.approx(-0.219, abs=1e-3)
    assert annualized != pytest.approx(-0.1095, abs=1e-3)


@pytest.mark.parametrize("position,funding_value,expect_positive", [
    (-1.0, 0.0002, True),    # short perp, f>0 -> receipt
    (1.0, 0.0002, False),    # long perp,  f>0 -> payment
    (-1.0, -0.0002, False),  # short perp, f<0 -> payment
    (1.0, -0.0002, True),    # long perp,  f<0 -> receipt
])
def test_t5_full_sign_matrix(position, funding_value, expect_positive):
    registry = _new_registry()
    family = _open_family(registry, f"t5-family-{position}-{funding_value}")
    n = 3
    idx = pd.date_range("2024-01-01", periods=n, freq="D")
    prices = pd.DataFrame({"perp": [100.0] * n}, index=idx)
    weights = pd.DataFrame({"perp": [position] * n}, index=idx)
    funding = pd.DataFrame({"perp": [funding_value] * n}, index=idx)
    result = run_backtest(
        prices, weights, _zero_cost(), registry, family, config={},
        execution_lag=1, periods_per_year=365, funding_panel=funding,
    )
    accrual = result.carry_accrual.iloc[-1]
    assert accrual != 0
    assert (accrual > 0) == expect_positive


def test_t6_accrual_never_a_function_of_gross():
    registry = _new_registry()
    family = _open_family(registry, "t6-family")
    n = 3
    idx = pd.date_range("2024-01-01", periods=n, freq="D")
    fval = 0.0004
    prices = pd.DataFrame({"spot": [100.0] * n, "perp": [100.0] * n}, index=idx)
    funding = pd.DataFrame({"perp": [fval] * n}, index=idx)  # funding on perp only

    weights_a = pd.DataFrame({"spot": [1.0] * n, "perp": [-1.0] * n}, index=idx)
    weights_b = pd.DataFrame({"spot": [-1.0] * n, "perp": [1.0] * n}, index=idx)

    res_a = run_backtest(prices, weights_a, _zero_cost(), registry, family,
                         config={"book": "a"}, execution_lag=1,
                         periods_per_year=365, funding_panel=funding)
    res_b = run_backtest(prices, weights_b, _zero_cost(), registry, family,
                         config={"book": "b"}, execution_lag=1,
                         periods_per_year=365, funding_panel=funding)

    a = res_a.carry_accrual.iloc[-1]
    b = res_b.carry_accrual.iloc[-1]
    assert a != 0 and b != 0
    assert a == pytest.approx(-b)


def test_t7_funding_applies_only_where_it_exists():
    registry = _new_registry()
    family = _open_family(registry, "t7-family")
    n = 3
    idx = pd.date_range("2024-01-01", periods=n, freq="D")
    fperp = 0.0005
    prices = pd.DataFrame(
        {"perp": [100.0] * n, "spot": [50.0] * n, "etf": [10.0] * n}, index=idx
    )
    # "etf" has NO funding coverage at all -> absent from the panel entirely.
    funding = pd.DataFrame({"perp": [fperp] * n, "spot": [0.0] * n}, index=idx)
    assert "etf" not in funding.columns

    accruals = []
    for etf_weight in (0.0, 5.0, 50.0):
        weights = pd.DataFrame(
            {"perp": [-1.0] * n, "spot": [1.0] * n, "etf": [etf_weight] * n}, index=idx
        )
        res = run_backtest(prices, weights, _zero_cost(), registry, family,
                           config={"w": etf_weight}, execution_lag=1,
                           periods_per_year=365, funding_panel=funding)
        accruals.append(res.carry_accrual.iloc[-1])

    expected = -(-1.0) * fperp
    for val in accruals:
        assert val == pytest.approx(expected)
    assert accruals[0] == accruals[1] == accruals[2]


# ----------------------------------------------------------------------
# 4.3 Realized prints, not a scalar
# ----------------------------------------------------------------------

def test_t8_realized_beats_any_scalar_and_the_gap_is_material():
    df = _load_funding_csv("sol")
    registry = _new_registry()
    family = _open_family(registry, "t8-family")
    store = _new_store(registry)
    _ingest_funding(store, "binanceusdm", "SOL/USDT:USDT", df)

    bar_index = _eod_bar_index(df["event_time"].min(), df["event_time"].max())
    decision_time = df["event_time"].max().timestamp() + 3600
    panel = pit_funding_panel(store, "binanceusdm", ["SOL/USDT:USDT"], decision_time, bar_index)

    n = len(bar_index)
    prices = pd.DataFrame({"SOL/USDT:USDT": [100.0] * n}, index=bar_index)
    weights = pd.DataFrame({"SOL/USDT:USDT": [-1.0] * n}, index=bar_index)
    result = run_backtest(prices, weights, _zero_cost(), registry, family, config={},
                          execution_lag=1, periods_per_year=365, funding_panel=panel)

    active = result.carry_accrual.iloc[1:]
    years = (bar_index[-1] - bar_index[0]).days / 365.25
    realized_annualized = active.sum() / years
    assert 0.0005 <= realized_annualized <= 0.0020

    scalar_annualized = 1095.0 / 1e4  # Charter's 1095 bps/yr baseline
    assert abs(realized_annualized - scalar_annualized) > 0.10


def test_t9_no_cadence_constant():
    df = _load_funding_csv("sol")
    window = df[(df["event_time"] >= "2022-11-09") & (df["event_time"] < "2022-11-12")].copy()
    registry = _new_registry()
    store = _new_store(registry)
    _ingest_funding(store, "binanceusdm", "SOL/USDT:USDT", window)

    # Bar index starts ON the fixture's first covered day so every bar is
    # within coverage (no NaN "not yet listed" edge case here -- that is
    # T-12's concern, not this one).
    bar_index = _eod_bar_index(pd.Timestamp("2022-11-09"), pd.Timestamp("2022-11-12"))
    decision_time = pd.Timestamp("2022-11-13").timestamp()
    panel = pit_funding_panel(store, "binanceusdm", ["SOL/USDT:USDT"], decision_time, bar_index)

    prev = None
    for i, t in enumerate(bar_index):
        if prev is None:
            mask = window["event_time"] <= t
        else:
            mask = (window["event_time"] > prev) & (window["event_time"] <= t)
        expected = window.loc[mask, "value"].sum()
        assert panel["SOL/USDT:USDT"].iloc[i] == pytest.approx(expected, abs=1e-9)
        prev = t

    nov10 = pd.Timestamp("2022-11-10T23:59:59.999999")
    idx_pos = list(bar_index).index(nov10)
    assert panel["SOL/USDT:USDT"].iloc[idx_pos] == pytest.approx(-0.17166, abs=1e-5)


def test_t10_bar_window_is_left_open_right_closed():
    registry = _new_registry()
    store = _new_store(registry)
    day0 = pd.Timestamp("2024-03-01")
    day1 = day0 + pd.Timedelta(days=1)
    ts = [day0, day0 + pd.Timedelta(hours=8), day0 + pd.Timedelta(hours=16), day1]
    vals = [0.0001, 0.0002, 0.0003, 0.0004]
    df = pd.DataFrame({"funding_rate": vals}, index=pd.DatetimeIndex(ts))
    store.ingest("test_src", "X", df, knowledge_time=0.0)

    bar_index = pd.DatetimeIndex([day0, day1])
    decision_time = (day1 + pd.Timedelta(days=1)).timestamp()
    panel = pit_funding_panel(store, "test_src", ["X"], decision_time, bar_index)

    assert panel["X"].iloc[0] == pytest.approx(0.0001)
    assert panel["X"].iloc[1] == pytest.approx(0.0002 + 0.0003 + 0.0004)
    assert panel["X"].sum() == pytest.approx(sum(vals))


def test_t11_no_same_bar_carry():
    registry = _new_registry()
    family = _open_family(registry, "t11-family")
    n = 5
    k = 2
    idx = pd.date_range("2024-01-01", periods=n, freq="D")
    weights = pd.DataFrame({"perp": [0.0] * n}, index=idx)
    weights.iloc[k, weights.columns.get_loc("perp")] = 1.0
    prices = pd.DataFrame({"perp": [100.0] * n}, index=idx)
    funding = pd.DataFrame({"perp": [0.0005] * n}, index=idx)

    result = run_backtest(prices, weights, _zero_cost(), registry, family, config={},
                          execution_lag=1, periods_per_year=365, funding_panel=funding)
    assert result.carry_accrual.iloc[k] == 0.0
    assert result.carry_accrual.iloc[k + 1] != 0.0


def test_t12_absent_coverage_is_nan_not_zero():
    registry = _new_registry()
    family = _open_family(registry, "t12-family")
    store = _new_store(registry)
    prints = pd.DataFrame(
        {"funding_rate": [0.0005, 0.0007]},
        index=pd.DatetimeIndex([pd.Timestamp("2024-01-03T08:00"),
                                 pd.Timestamp("2024-01-06T08:00")]),
    )
    store.ingest("test_src", "X", prints, knowledge_time=0.0)

    bar_index = _eod_bar_index(pd.Timestamp("2024-01-01"), pd.Timestamp("2024-01-07"))
    decision_time = pd.Timestamp("2024-01-08").timestamp()
    panel = pit_funding_panel(store, "test_src", ["X"], decision_time, bar_index)

    assert math.isnan(panel["X"].iloc[0])  # 01-01: not yet listed
    assert math.isnan(panel["X"].iloc[1])  # 01-02: not yet listed
    assert panel["X"].iloc[2] == pytest.approx(0.0005)  # 01-03: the print
    assert panel["X"].iloc[3] == 0.0  # 01-04: within coverage, no print
    assert panel["X"].iloc[4] == 0.0  # 01-05: within coverage, no print
    assert panel["X"].iloc[5] == pytest.approx(0.0007)  # 01-06: the print
    assert panel["X"].iloc[6] == 0.0  # 01-07: within coverage, no print

    n = len(bar_index)
    prices = pd.DataFrame({"X": [100.0] * n}, index=bar_index)
    weights = pd.DataFrame({"X": [1.0] * n}, index=bar_index)  # held from bar 0
    with pytest.raises(FundingCoverageError):
        run_backtest(prices, weights, _zero_cost(), registry, family, config={},
                    execution_lag=1, periods_per_year=365, funding_panel=panel)


def test_t13_pit_discipline_holds_on_funding():
    registry = _new_registry()
    store = _new_store(registry)
    et = pd.Timestamp("2024-01-01T08:00:00")
    et2 = pd.Timestamp("2024-01-01T16:00:00")

    store.ingest("test_src", "TESTPERP",
                pd.DataFrame({"funding_rate": [0.001]}, index=[et]), knowledge_time=100.0)
    store.ingest("test_src", "TESTPERP",  # restatement of the same event_time
                pd.DataFrame({"funding_rate": [0.002]}, index=[et]), knowledge_time=200.0)
    store.ingest("test_src", "TESTPERP",  # a later print, not yet knowable at t<300
                pd.DataFrame({"funding_rate": [0.003]}, index=[et2]), knowledge_time=300.0)

    bar_index = pd.DatetimeIndex([pd.Timestamp("2024-01-02T00:00:00")])

    p1 = pit_funding_panel(store, "test_src", ["TESTPERP"], 150.0, bar_index)
    assert p1["TESTPERP"].iloc[0] == pytest.approx(0.001)
    assert p1.attrs["print_counts"]["TESTPERP"] == 1

    p2 = pit_funding_panel(store, "test_src", ["TESTPERP"], 250.0, bar_index)
    assert p2["TESTPERP"].iloc[0] == pytest.approx(0.002)  # latest version at/before 250
    assert p2.attrs["print_counts"]["TESTPERP"] == 1

    p3 = pit_funding_panel(store, "test_src", ["TESTPERP"], 350.0, bar_index)
    assert p3["TESTPERP"].iloc[0] == pytest.approx(0.002 + 0.003)
    assert p3.attrs["print_counts"]["TESTPERP"] == 2

    for p, dt in [(p1, 150.0), (p2, 250.0), (p3, 350.0)]:
        assert p.attrs["decision_time"] == dt
        assert isinstance(p.attrs["sha256"], str) and len(p.attrs["sha256"]) == 64


# ----------------------------------------------------------------------
# 4.4 Two legs
# ----------------------------------------------------------------------

def test_t14_per_asset_cost_models():
    registry = _new_registry()
    family = _open_family(registry, "t14-family")
    n = 10
    idx = pd.date_range("2024-01-01", periods=n, freq="D")
    prices = pd.DataFrame(
        {"spot": np.linspace(100, 110, n), "perp": np.linspace(100, 109, n)}, index=idx
    )
    weights = pd.DataFrame({"spot": [0.5] * n, "perp": [-0.5] * n}, index=idx)
    model_a = CostModel(name="a", commission_bps=5.0, half_spread_bps=2.0, periods_per_year=365)
    model_b = CostModel(name="b", commission_bps=8.0, half_spread_bps=3.0, periods_per_year=365)

    res_mapped = run_backtest(
        prices, weights, {"spot": model_a, "perp": model_b}, registry, family,
        config={"c": "mapped"}, execution_lag=1, periods_per_year=365,
    )

    positions = weights.shift(1).fillna(0.0)
    trades = positions.diff().abs().fillna(positions.abs())
    expected_cost = (trades["spot"] * float(model_a.per_side_cost(1.0))
                     + trades["perp"] * float(model_b.per_side_cost(1.0)))
    assert np.allclose(res_mapped.cost_returns.values, expected_cost.values)

    with pytest.raises(ValueError):
        run_backtest(prices, weights, {"spot": model_a}, registry, family,
                    config={"c": "missing"}, execution_lag=1, periods_per_year=365)

    single_model = CostModel(name="single", commission_bps=3.0, half_spread_bps=1.5,
                             borrow_bps_annual=200.0, periods_per_year=252)
    res_single = run_backtest(prices, weights, single_model, registry, family,
                              config={"c": "single"}, execution_lag=1, periods_per_year=252)
    per_side = float(single_model.per_side_cost(1.0))
    trade_cost_golden = trades.sum(axis=1) * per_side
    short_n = (-positions.clip(upper=0)).sum(axis=1)
    borrow_golden = short_n * (single_model.borrow_bps_annual * 1e-4 / 252)
    cost_golden = trade_cost_golden + borrow_golden
    assert np.allclose(res_single.cost_returns.values, cost_golden.values)


def test_t15_trial_identity_distinguishes_the_mapping():
    registry = _new_registry()
    family = _open_family(registry, "t15-family")
    n = 5
    idx = pd.date_range("2024-01-01", periods=n, freq="D")
    prices = pd.DataFrame({"spot": [100.0] * n, "perp": [100.0] * n}, index=idx)
    weights = pd.DataFrame({"spot": [0.5] * n, "perp": [-0.5] * n}, index=idx)
    model_a = CostModel(name="a", commission_bps=5.0, half_spread_bps=2.0, periods_per_year=365)
    model_b = CostModel(name="b", commission_bps=8.0, half_spread_bps=3.0, periods_per_year=365)

    res1 = run_backtest(prices, weights, {"spot": model_a, "perp": model_b}, registry, family,
                        config={"c": "1"}, execution_lag=1, periods_per_year=365)
    res2 = run_backtest(prices, weights, {"spot": model_b, "perp": model_a}, registry, family,
                        config={"c": "1"}, execution_lag=1, periods_per_year=365)
    assert res1.trial_id != res2.trial_id
    h1 = registry.conn.execute(
        "SELECT config_hash FROM trials WHERE trial_id=?", (res1.trial_id,)).fetchone()[0]
    h2 = registry.conn.execute(
        "SELECT config_hash FROM trials WHERE trial_id=?", (res2.trial_id,)).fetchone()[0]
    assert h1 != h2
    assert res1.config["cost_model"] == {"spot": "a", "perp": "b"}
    assert res2.config["cost_model"] == {"spot": "b", "perp": "a"}

    store = _new_store(registry)
    funding_df = pd.DataFrame({"funding_rate": [0.0001] * n}, index=idx)
    store.ingest("test_src", "perp", funding_df, knowledge_time=0.0)
    dt = idx[-1].timestamp() + 3600
    panel = pit_funding_panel(store, "test_src", ["perp"], dt, idx)
    res3 = run_backtest(prices, weights, {"spot": model_a, "perp": model_b}, registry, family,
                        config={"c": "2"}, execution_lag=1, periods_per_year=365,
                        funding_panel=panel)
    assert res3.config["funding_panel_decision_time"] is not None
    assert res3.config["funding_panel_sha256"] == panel.attrs["sha256"]


# ----------------------------------------------------------------------
# 4.5 Stress semantics
# ----------------------------------------------------------------------

def test_t16_sign_inversion_is_a_scenario_not_scaled():
    registry = _new_registry()
    family = _open_family(registry, "t16-family")
    n = 20
    idx = pd.date_range("2024-01-01", periods=n, freq="D")
    prices = pd.DataFrame({"perp": [100.0 + 0.01 * i for i in range(n)]}, index=idx)
    weights = pd.DataFrame({"perp": [-1.0] * n}, index=idx)
    funding = pd.DataFrame({"perp": np.linspace(0.0001, 0.0009, n)}, index=idx)
    base_cost = CostModel(name="base", commission_bps=5.0, half_spread_bps=1.0,
                          periods_per_year=365)

    res_1x = run_backtest(prices, weights, base_cost, registry, family, config={"m": 1},
                          execution_lag=1, periods_per_year=365, funding_panel=funding)
    res_2x = run_backtest(prices, weights, base_cost.scaled(2.0), registry, family,
                          config={"m": 2}, execution_lag=1, periods_per_year=365,
                          funding_panel=funding)
    assert np.array_equal(res_1x.carry_accrual.values, res_2x.carry_accrual.values)

    inverted = apply_carry_scenario(funding, CarryScenario.SIGN_INVERTED)
    res_inv = run_backtest(prices, weights, base_cost, registry, family, config={"m": "inv"},
                           execution_lag=1, periods_per_year=365, funding_panel=inverted)
    assert np.allclose(res_inv.carry_accrual.values, -res_1x.carry_accrual.values)


def test_t17_zero_isolates_and_tail_bootstrap_preserves_the_tail():
    df = _load_funding_csv("sol")
    registry = _new_registry()
    family = _open_family(registry, "t17-family")
    store = _new_store(registry)
    _ingest_funding(store, "binanceusdm", "SOL/USDT:USDT", df)

    bar_index = _eod_bar_index(df["event_time"].min(), df["event_time"].max())
    decision_time = df["event_time"].max().timestamp() + 3600
    panel = pit_funding_panel(store, "binanceusdm", ["SOL/USDT:USDT"], decision_time, bar_index)

    n = len(bar_index)
    prices = pd.DataFrame({"SOL/USDT:USDT": [100.0] * n}, index=bar_index)
    weights = pd.DataFrame({"SOL/USDT:USDT": [-1.0] * n}, index=bar_index)

    zero_panel = apply_carry_scenario(panel, CarryScenario.ZERO)
    res_zero_scenario = run_backtest(prices, weights, _zero_cost(), registry, family,
                                     config={"s": "zero"}, execution_lag=1,
                                     periods_per_year=365, funding_panel=zero_panel)
    res_none = run_backtest(prices, weights, _zero_cost(), registry, family,
                            config={"s": "none"}, execution_lag=1,
                            periods_per_year=365, funding_panel=None)
    assert np.array_equal(res_zero_scenario.net_returns.values, res_none.net_returns.values)

    positions = weights.shift(1).fillna(0.0)
    result = tail_bootstrap_carry(panel, positions, n_paths=1000, block=21, seed=42)
    assert result["p5_worst_day"] <= result["realized_worst_day"] + 1e-9
    se = np.std(result["mean"], ddof=1)
    assert abs(np.mean(result["mean"]) - result["realized_mean"]) <= 2 * se


def test_t18_breakeven_is_monotone_the_multiplier_is_not():
    df = _load_funding_csv("btc")
    registry = _new_registry()
    family = _open_family(registry, "t18-family")
    store = _new_store(registry)
    _ingest_funding(store, "binanceusdm", "BTC/USDT:USDT", df)

    bar_index = _eod_bar_index(df["event_time"].min(), df["event_time"].max())
    decision_time = df["event_time"].max().timestamp() + 3600
    panel = pit_funding_panel(store, "binanceusdm", ["BTC/USDT:USDT"], decision_time, bar_index)

    n = len(bar_index)
    prices = pd.DataFrame({"BTC/USDT:USDT": [100.0] * n}, index=bar_index)
    weights = pd.DataFrame({"BTC/USDT:USDT": [-1.0] * n}, index=bar_index)

    def net_at_shift(delta):
        shifted = shift_carry_panel(panel, delta, periods_per_year=365)
        res = run_backtest(prices, weights, _zero_cost(), registry, family,
                           config={"d": delta}, execution_lag=1,
                           periods_per_year=365, funding_panel=shifted)
        return res.net_returns.values[1:]

    ts = [stats.sr_tstat(net_at_shift(d)) for d in np.linspace(0.0, 2000.0, 25)]
    assert all(ts[i] >= ts[i + 1] - 1e-9 for i in range(len(ts) - 1))

    breakeven = carry_breakeven_bps_annual(net_at_shift, periods_per_year=365,
                                           bracket=(0.0, 2000.0))
    assert 0.0 < breakeven < 2000.0

    # Reconstruct the naive "multiplicative repair" I-037 describes: a
    # real, VOLATILE market/basis return (unaffected by the multiplier)
    # plus a constant per-bar carry credit that -- in the naive repair --
    # stays folded inside the same `scaled(m)`-multiplied cost stack. The
    # realized BTC carry rate (mean of `net_at_shift(0.0)`, which IS the
    # pure carry series on this zero-gross/zero-friction fixture) supplies
    # a realistic, measured magnitude for that constant.
    realized_carry_mean = float(np.mean(net_at_shift(0.0)))
    n_active = len(bar_index) - 1
    gross_noise = 0.002 * np.sin(np.arange(n_active) * 0.7)  # small, deterministic, ~zero-mean

    def net_at_multiplier(m):
        return gross_noise + m * realized_carry_mean

    ms = np.linspace(1.0, 32.0, 25)
    tm = [stats.sr_tstat(net_at_multiplier(m)) for m in ms]
    assert tm[0] >= 3.0  # already PASSes at m=1 -- the "manufactured" case
    assert tm[-1] > tm[0]  # increasing -- non-monotone, the opposite of the shift construction

    report = evaluate_gate1(
        "t18-multiplier-defect", family, registry,
        oos_net_returns=net_at_multiplier(1.0), periods_per_year=365,
        backtest_years=(bar_index[-1] - bar_index[0]).days / 365.25,
        oos_index=bar_index[1:],
        net_returns_at_cost_multiplier=net_at_multiplier,
    )
    assert report.breakeven_cost_multiplier == pytest.approx(32.0, abs=1e-3)


# ----------------------------------------------------------------------
# 4.6 Anti-regression on the refused field
# ----------------------------------------------------------------------

def test_t19_no_liquidation_or_insolvency_field():
    """Ruling 003 section 3.5: liquidation/insolvency is refused as a
    chargeable CostModel field. A per-bar expected-loss deduction turns
    a fat tail into a thin drag, which IMPROVES the firm's own tail
    detectors' readings while making them less sensitive to the tail
    they exist to detect. If the Principal later rules otherwise, THIS
    TEST is deleted by his written decision, not by an implementer's
    judgment (I-023(b) takes identical treatment)."""
    banned = ("liquidation", "insolvency", "venue", "oracle", "resolution")
    names = [f.name for f in dataclasses.fields(CostModel)]
    assert not any(k in name for name in names for k in banned)
