"""Tests for the PIT data layer, loader parsers, grid runner, and paper book."""

import numpy as np
import pandas as pd
import pytest

from castellan import TrialRegistry, US_EQUITY_LARGE
from castellan.data import PITStore, pit_adjusted_close
from castellan.loaders import (
    parse_yfinance_history, parse_ccxt_ohlcv, parse_ccxt_funding,
    parse_edgar_submissions,
)
from castellan.grid import grid_from_center, run_parameter_grid
from castellan.book import PaperBook, SameBarBookFillError, BookError


@pytest.fixture
def registry(tmp_path):
    reg = TrialRegistry(str(tmp_path / "r.db"))
    reg.open_hypothesis("fam", "s", "m", "f", "u", "1d", "sc", 100)
    return reg


# ----------------------------------------------------------------------
# PIT store: versioning, asof, restatements
# ----------------------------------------------------------------------

def test_asof_reconstructs_what_was_knowable(tmp_path, registry):
    store = PITStore(str(tmp_path / "pit.db"), registry)
    idx = pd.bdate_range("2024-01-01", periods=5)
    v1 = pd.DataFrame({"close": [10, 11, 12, 13, 14]}, index=idx)
    store.ingest("src", "XYZ", v1, knowledge_time=1_000.0)

    # vendor restates bar 3 later
    v2 = pd.DataFrame({"close": [12.5]}, index=[idx[2]])
    r = store.ingest("src", "XYZ", v2, knowledge_time=2_000.0)
    assert r["restated"] == 1

    before = store.asof("src", "XYZ", 1_500.0)
    after = store.asof("src", "XYZ", 2_500.0)
    assert before.loc[idx[2], "close"] == 12       # old truth preserved
    assert after.loc[idx[2], "close"] == 12.5      # new truth after kt
    # restatement incident hit the registry
    assert any(e["kind"] == "data_restatement" for e in registry.events())
    assert len(store.restatement_history("src", "XYZ")) == 1


def test_unchanged_reingest_is_deduplicated(tmp_path):
    store = PITStore(str(tmp_path / "pit.db"))
    idx = pd.bdate_range("2024-01-01", periods=3)
    df = pd.DataFrame({"close": [1.0, 2.0, 3.0]}, index=idx)
    store.ingest("s", "A", df, knowledge_time=100.0)
    r = store.ingest("s", "A", df, knowledge_time=200.0)
    assert r == {"new": 0, "unchanged": 3, "restated": 0}


def test_pit_adjustment_ignores_future_split(tmp_path):
    """The yfinance hazard, demonstrated: a split ingested later must not
    alter the adjusted series as it was knowable before the ingest."""
    store = PITStore(str(tmp_path / "pit.db"))
    idx = pd.bdate_range("2024-01-01", periods=6)
    raw = pd.DataFrame({"close": [100, 102, 104, 52, 53, 54]}, index=idx)
    store.ingest("yf", "SPLITCO", raw, knowledge_time=1_000.0)
    # 2-for-1 split effective idx[3], but the firm learns of it at kt=2000
    split = pd.DataFrame({"split": [2.0]}, index=[idx[3]])
    store.ingest("yf", "SPLITCO", split, knowledge_time=2_000.0)

    adj_before = pit_adjusted_close(store, "yf", "SPLITCO", 1_500.0)
    adj_after = pit_adjusted_close(store, "yf", "SPLITCO", 2_500.0)

    assert adj_before.loc[idx[0]] == 100          # no split known yet
    assert adj_after.loc[idx[0]] == 50            # halved once known
    assert adj_after.loc[idx[3]] == 52            # post-split bars untouched
    # after adjustment the artificial cliff disappears
    rets = adj_after.pct_change().dropna()
    assert rets.abs().max() < 0.05


def test_dividend_adjustment(tmp_path):
    store = PITStore(str(tmp_path / "pit.db"))
    idx = pd.bdate_range("2024-01-01", periods=4)
    raw = pd.DataFrame({"close": [100.0, 100.0, 99.0, 99.0]}, index=idx)
    store.ingest("yf", "DIVCO", raw, knowledge_time=100.0)
    div = pd.DataFrame({"dividend": [1.0]}, index=[idx[2]])  # ex-date bar 2
    store.ingest("yf", "DIVCO", div, knowledge_time=100.0)
    adj = pit_adjusted_close(store, "yf", "DIVCO", 200.0)
    assert np.isclose(adj.loc[idx[1]], 99.0)      # 100 * (1 - 1/100)
    assert np.isclose(adj.loc[idx[2]], 99.0)      # total-return continuity


def test_documents_asof(tmp_path):
    store = PITStore(str(tmp_path / "pit.db"))
    docs = [
        {"doc_type": "8-K", "event_time": "2024-03-01T16:05:00",
         "ref": "0001-24-000001", "meta": {}},
        {"doc_type": "10-Q", "event_time": "2024-05-01T09:00:00",
         "ref": "0001-24-000002", "meta": {}},
    ]
    assert store.ingest_documents("edgar", "XYZ", docs) == 2
    assert store.ingest_documents("edgar", "XYZ", docs) == 0  # de-duped
    early = store.documents_asof("edgar", "XYZ", "2024-04-01")
    assert len(early) == 1 and early.iloc[0]["doc_type"] == "8-K"


# ----------------------------------------------------------------------
# Loader parsers (offline)
# ----------------------------------------------------------------------

def test_parse_yfinance_splits_raw_from_actions():
    idx = pd.bdate_range("2024-01-01", periods=3)
    hist = pd.DataFrame({
        "Open": [1, 2, 3.], "High": [1, 2, 3.], "Low": [1, 2, 3.],
        "Close": [1, 2, 3.], "Volume": [10, 20, 30],
        "Dividends": [0.0, 0.5, 0.0], "Stock Splits": [0.0, 0.0, 2.0],
    }, index=idx)
    ohlcv, actions = parse_yfinance_history(hist)
    assert list(ohlcv.columns) == ["open", "high", "low", "close", "volume"]
    assert actions.loc[idx[1], "dividend"] == 0.5
    assert actions.loc[idx[2], "split"] == 2.0
    assert len(actions) == 2


def test_parse_ccxt():
    raw = [[1700000000000, 1, 2, 0.5, 1.5, 100],
           [1700086400000, 1.5, 2, 1, 1.8, 120]]
    df = parse_ccxt_ohlcv(raw)
    assert df.iloc[1]["close"] == 1.8
    fr = parse_ccxt_funding([
        {"timestamp": 1700000000000, "fundingRate": 0.0001},
        {"timestamp": 1700028800000, "fundingRate": None},
    ])
    assert len(fr) == 1 and fr.iloc[0]["funding_rate"] == 0.0001


def test_parse_edgar_submissions():
    payload = {"filings": {"recent": {
        "form": ["8-K", "10-Q"],
        "accessionNumber": ["a1", "a2"],
        "acceptanceDateTime": ["2024-03-01T16:05:00.000Z", ""],
        "filingDate": ["2024-03-01", "2024-05-01"],
        "primaryDocument": ["x.htm", "y.htm"],
    }}}
    docs = parse_edgar_submissions(payload)
    assert len(docs) == 2
    assert docs[0]["doc_type"] == "8-K"
    assert docs[1]["event_time"] == pd.Timestamp("2024-05-01")  # fallback


# ----------------------------------------------------------------------
# Grid runner
# ----------------------------------------------------------------------

def test_grid_runner_logs_every_point_and_finds_plateau(registry):
    rng = np.random.default_rng(4)
    idx = pd.bdate_range("2021-01-01", periods=600)
    prices = pd.DataFrame(
        100 * np.exp(np.cumsum(rng.normal(0.0004, 0.01, (600, 2)), axis=0)),
        index=idx, columns=["A", "B"])

    def factory(px, params):
        lb = int(params["lookback"])
        return (np.sign(px.pct_change(lb)) * params["cap"] / 2).fillna(0.0)

    grid = grid_from_center({"lookback": 60, "cap": 0.8}, 0.5, 3,
                            integer_params={"lookback"})
    n_before = registry.family_stats("fam").n_trials
    res = run_parameter_grid(prices, factory, grid, US_EQUITY_LARGE,
                             registry, "fam")
    assert registry.family_stats("fam").n_trials == n_before + len(grid)
    assert 0.0 <= res.fraction_profitable <= 1.0
    assert set(res.plateau_centroid_params) == {"lookback", "cap"}
    assert len(res.param_grid_net_pnls) == len(grid)


def test_grid_refuses_to_explode():
    with pytest.raises(ValueError):
        grid_from_center({"a": 1, "b": 1, "c": 1, "d": 1}, 0.5, 5,
                         max_points=100)


# ----------------------------------------------------------------------
# Paper book
# ----------------------------------------------------------------------

def test_book_same_bar_fill_refused(tmp_path):
    book = PaperBook(str(tmp_path / "book.db"), 1_000_000)
    with pytest.raises(SameBarBookFillError):
        book.place_and_fill("SPY", "BUY", 10, "2024-01-02 16:00",
                            "2024-01-02 16:00", 470.0, US_EQUITY_LARGE,
                            pm="pod-a", rationale="test")


def test_book_lifecycle_and_reconciliation(tmp_path):
    book = PaperBook(str(tmp_path / "book.db"), 1_000_000)
    f1 = book.place_and_fill("SPY", "BUY", 100, "2024-01-02 16:00",
                             "2024-01-03 09:30", 470.0, US_EQUITY_LARGE,
                             pm="pod-a", rationale="tsmom entry")
    assert f1.position_after == 100
    f2 = book.place_and_fill("SPY", "SELL", 40, "2024-01-04 16:00",
                             "2024-01-05 09:30", 480.0, US_EQUITY_LARGE,
                             pm="pod-a", rationale="partial exit")
    assert f2.position_after == 60
    assert np.isclose(f2.realized_pnl, 40 * 10.0)

    pack = book.mark({"SPY": 485.0})
    assert np.isclose(pack["unrealized_pnl"]["SPY"], 60 * 15.0)
    assert pack["gross_exposure"] == 60 * 485.0

    rec = book.reconcile()
    assert rec["clean"] and rec["n_trades"] == 2

    # tamper with running state -> reconciliation reports, never repairs
    book._set_state("positions", {"SPY": 61})
    book.conn.commit()
    rec2 = book.reconcile()
    assert not rec2["clean"]
    assert rec2["breaks"][0]["kind"] == "position"
    rec3 = book.reconcile()
    assert not rec3["clean"]  # still broken: reconcile never mutates


def test_book_requires_rationale_and_missing_mark_escalates(tmp_path):
    book = PaperBook(str(tmp_path / "book.db"), 1_000)
    with pytest.raises(BookError):
        book.place_and_fill("SPY", "BUY", 1, "2024-01-02", "2024-01-03",
                            470.0, US_EQUITY_LARGE, pm="a", rationale="  ")
    book.place_and_fill("SPY", "BUY", 1, "2024-01-02", "2024-01-03",
                        470.0, US_EQUITY_LARGE, pm="a", rationale="r")
    with pytest.raises(BookError):
        book.mark({})  # held instrument with no mark: escalate, not guess


def test_book_short_and_cross_through_zero(tmp_path):
    book = PaperBook(str(tmp_path / "book.db"), 1_000_000)
    book.place_and_fill("QQQ", "SELL", 50, "2024-01-02", "2024-01-03",
                        400.0, US_EQUITY_LARGE, pm="a", rationale="short")
    f = book.place_and_fill("QQQ", "BUY", 80, "2024-01-04", "2024-01-05",
                            390.0, US_EQUITY_LARGE, pm="a",
                            rationale="cover and flip")
    assert f.position_after == 30
    assert np.isclose(f.realized_pnl, 50 * 10.0)  # short covered 10 lower
    assert book.reconcile()["clean"]
