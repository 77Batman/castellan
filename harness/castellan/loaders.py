"""Loaders — thin, network-facing, all routed through the PITStore.

Design rules:

1. **Raw in, adjusted out.** yfinance is fetched with ``auto_adjust=False``
   and stored as raw OHLCV plus separate split/dividend observations.
   Research consumes ``pit_adjusted_close`` — never the vendor's
   pre-adjusted series.
2. **Ingestion time is knowledge time.** The initial backfill's history
   gets knowledge_time = the backfill moment, honestly recorded. The
   store cannot pretend the firm knew a bar before it first fetched it;
   refreshes then version any vendor restatements automatically.
3. **Parsing is separated from fetching** so the parse logic is testable
   offline. ``fetch_*`` does I/O; ``parse_*`` is pure.

EDGAR etiquette: SEC requires a descriptive User-Agent with a contact
address, and rate limits at 10 req/s. Set ``user_agent`` accordingly.
"""

from __future__ import annotations

import time

import pandas as pd

from .data import PITStore

# ----------------------------------------------------------------------
# yfinance — equities & ETFs (raw prices + corporate actions)
# ----------------------------------------------------------------------

def parse_yfinance_history(hist: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Split a ``Ticker.history(auto_adjust=False, actions=True)`` frame
    into (raw OHLCV, corporate actions with fields split/dividend)."""
    hist = hist.copy()
    hist.index = pd.to_datetime(hist.index).tz_localize(None)
    ohlcv = pd.DataFrame(index=hist.index)
    for src, dst in [("Open", "open"), ("High", "high"), ("Low", "low"),
                     ("Close", "close"), ("Volume", "volume")]:
        if src in hist:
            ohlcv[dst] = hist[src]
    actions = pd.DataFrame(index=hist.index)
    if "Stock Splits" in hist:
        s = hist["Stock Splits"].replace(0.0, pd.NA).dropna()
        actions.loc[s.index, "split"] = s.astype(float)
    if "Dividends" in hist:
        d = hist["Dividends"].replace(0.0, pd.NA).dropna()
        actions.loc[d.index, "dividend"] = d.astype(float)
    actions = actions.dropna(how="all")
    return ohlcv, actions


def fetch_yfinance(
    store: PITStore,
    symbols: list[str],
    start: str,
    end: str | None = None,
    interval: str = "1d",
) -> dict[str, dict]:
    """Fetch raw history + actions per symbol and ingest. Restatements
    (vendor re-adjustments) are detected and logged by the store."""
    import yfinance as yf  # optional dependency: pip install ".[data]"

    results = {}
    for sym in symbols:
        hist = yf.Ticker(sym).history(
            start=start, end=end, interval=interval,
            auto_adjust=False, actions=True,
        )
        if hist.empty:
            results[sym] = {"new": 0, "unchanged": 0, "restated": 0,
                            "note": "empty response"}
            continue
        ohlcv, actions = parse_yfinance_history(hist)
        r1 = store.ingest("yfinance", sym, ohlcv)
        r2 = store.ingest("yfinance", sym, actions) if len(actions) else {
            "new": 0, "unchanged": 0, "restated": 0}
        results[sym] = {k: r1[k] + r2[k] for k in ("new", "unchanged", "restated")}
    return results


# ----------------------------------------------------------------------
# ccxt — crypto OHLCV and perpetual funding history
# ----------------------------------------------------------------------

def parse_ccxt_ohlcv(raw: list[list]) -> pd.DataFrame:
    """[[ms, o, h, l, c, v], ...] -> wide frame."""
    df = pd.DataFrame(raw, columns=["ms", "open", "high", "low", "close",
                                    "volume"])
    df.index = pd.to_datetime(df.pop("ms"), unit="ms")
    return df


def parse_ccxt_funding(raw: list[dict]) -> pd.DataFrame:
    """fetch_funding_rate_history output -> frame with field funding_rate."""
    rows = [(pd.to_datetime(r["timestamp"], unit="ms"),
             float(r["fundingRate"])) for r in raw
            if r.get("fundingRate") is not None]
    df = pd.DataFrame(rows, columns=["ts", "funding_rate"]).set_index("ts")
    return df


def fetch_ccxt_ohlcv(
    store: PITStore,
    exchange_id: str,
    symbol: str,
    timeframe: str = "1d",
    since_ms: int | None = None,
    limit: int = 1000,
    max_pages: int = 50,
) -> dict:
    """Paginate OHLCV forward from ``since_ms`` and ingest."""
    import ccxt  # optional dependency

    ex = getattr(ccxt, exchange_id)({"enableRateLimit": True})
    totals = {"new": 0, "unchanged": 0, "restated": 0}
    cursor = since_ms
    for _ in range(max_pages):
        batch = ex.fetch_ohlcv(symbol, timeframe, since=cursor, limit=limit)
        if not batch:
            break
        df = parse_ccxt_ohlcv(batch)
        r = store.ingest(exchange_id, symbol, df)
        for k in totals:
            totals[k] += r[k]
        nxt = batch[-1][0] + 1
        if cursor is not None and nxt <= cursor:
            break
        cursor = nxt
        if len(batch) < limit:
            break
    return totals


def fetch_ccxt_funding(
    store: PITStore,
    exchange_id: str,
    symbol: str,
    since_ms: int | None = None,
    limit: int = 1000,
    max_pages: int = 50,
) -> dict:
    import ccxt

    ex = getattr(ccxt, exchange_id)({"enableRateLimit": True})
    totals = {"new": 0, "unchanged": 0, "restated": 0}
    cursor = since_ms
    for _ in range(max_pages):
        batch = ex.fetch_funding_rate_history(symbol, since=cursor,
                                              limit=limit)
        if not batch:
            break
        df = parse_ccxt_funding(batch)
        if df.empty:
            break
        r = store.ingest(exchange_id, symbol, df)
        for k in totals:
            totals[k] += r[k]
        nxt = batch[-1]["timestamp"] + 1
        if cursor is not None and nxt <= cursor:
            break
        cursor = nxt
        if len(batch) < limit:
            break
    return totals


# ----------------------------------------------------------------------
# SEC EDGAR — filings with genuine point-in-time acceptance stamps
# ----------------------------------------------------------------------

EDGAR_SUBMISSIONS_URL = "https://data.sec.gov/submissions/CIK{cik:0>10}.json"


def parse_edgar_submissions(payload: dict) -> list[dict]:
    """data.sec.gov submissions JSON -> document dicts for the store.

    ``acceptanceDateTime`` is when EDGAR accepted the filing — the honest
    knowledge_time for event studies. ``event_time`` is set to it too:
    the filing 'became true' when it hit the tape, not the period it
    reports on.
    """
    recent = payload.get("filings", {}).get("recent", {})
    forms = recent.get("form", [])
    acc = recent.get("accessionNumber", [])
    accepted = recent.get("acceptanceDateTime", [])
    fdate = recent.get("filingDate", [])
    primary = recent.get("primaryDocument", [""] * len(forms))
    docs = []
    for i, form in enumerate(forms):
        ts = accepted[i] if i < len(accepted) and accepted[i] else fdate[i]
        stamp = pd.Timestamp(ts).tz_localize(None) if ts else None
        if stamp is None:
            continue
        docs.append({
            "doc_type": form,
            "event_time": stamp,
            "knowledge_time": stamp.timestamp(),
            "ref": acc[i],
            "meta": {"filing_date": fdate[i] if i < len(fdate) else None,
                     "primary_document": primary[i] if i < len(primary) else None},
        })
    return docs


def fetch_edgar_filings(
    store: PITStore,
    cik: int | str,
    symbol: str,
    user_agent: str,
    pause_s: float = 0.15,
) -> int:
    """Fetch the submissions index for a CIK and ingest filing metadata.
    ``user_agent`` must identify you per SEC policy, e.g.
    'Castellan Research contact@example.com'."""
    import urllib.request

    url = EDGAR_SUBMISSIONS_URL.format(cik=int(str(cik).lstrip("0") or 0))
    req = urllib.request.Request(url, headers={"User-Agent": user_agent})
    with urllib.request.urlopen(req, timeout=30) as resp:
        import json as _json
        payload = _json.loads(resp.read().decode())
    time.sleep(pause_s)
    docs = parse_edgar_submissions(payload)
    return store.ingest_documents("edgar", symbol, docs)
