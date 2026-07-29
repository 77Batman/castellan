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

import json
import os
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


# ----------------------------------------------------------------------
# Polymarket — live order-book snapshot capture (DATA-INFRA-001)
#
# Firm infrastructure, not family research: historical Polymarket book
# depth is unavailable and structurally unreconstructible on-chain
# (research/DATA-PROBE-001-polymarket-orderbook.md). The only remedy is
# prospective accumulation, starting now. This module polls the live
# `/books` endpoint on a cadence set by whatever calls it
# (harness/scripts/capture_polymarket_book.py) — nothing here schedules
# itself.
#
# Two-timestamp discipline, made concrete for a polled snapshot:
#   event_time     the venue's own `timestamp` field on the book response
#                   -- when Polymarket's matching engine generated that
#                   book state. VERIFIED [measured] to be Unix epoch
#                   MILLISECONDS despite docs.polymarket.com stating
#                   "seconds since epoch" -- a live response's 13-digit
#                   timestamp cross-checked against wall-clock time
#                   confirms milliseconds. Converted with
#                   pd.to_datetime(..., unit="ms", utc=True); never
#                   tz_localize/strip (I-020).
#   knowledge_time  when THIS firm's poller received and parsed the
#                   response -- captured once per batch call, immediately
#                   after the HTTP round trip returns, applied to every
#                   token in that batch.
# These are genuinely different instants here (network + queue latency,
# typically sub-second to a few seconds) rather than the years-apart gap
# a historical backfill produces, and rather than the degenerate
# event_time == knowledge_time most other "current value" fetches default
# to when the vendor supplies no snapshot-generation timestamp of its own.
# ----------------------------------------------------------------------

GAMMA_MARKETS_URL = "https://gamma-api.polymarket.com/markets"
CLOB_BOOKS_URL = "https://clob.polymarket.com/books"


def _ssl_context():
    """Build a verifying SSL context using ``certifi``'s CA bundle when
    available, falling back to the interpreter's own default trust store.
    Purely a robustness measure for unattended (cron-run) execution across
    machines with inconsistent local CA configuration -- not a relaxation
    of certificate verification; verification stays on either way."""
    import ssl

    try:
        import certifi

        return ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        return ssl.create_default_context()


def _gamma_get(params: dict, timeout: float = 10.0) -> list:
    """GET against the documented, public Gamma markets endpoint.

    ``doseq=True``: measured [measured] that Gamma's list-valued filters
    (e.g. ``condition_ids``) require the query key REPEATED once per value
    (``?condition_ids=A&condition_ids=B``), not comma-joined
    (``?condition_ids=A,B``, which silently matches zero markets rather
    than erroring -- the exact "fails permissively" shape this firm has
    hit before in the harness, here in a third-party API instead).
    ``doseq=True`` makes any list-valued entry in ``params`` repeat
    correctly; scalar entries are unaffected.
    """
    import urllib.parse
    import urllib.request

    url = GAMMA_MARKETS_URL + "?" + urllib.parse.urlencode(params, doseq=True)
    req = urllib.request.Request(
        url, headers={"User-Agent": "Castellan-Data-Infra/1.0 (research infrastructure)"}
    )
    with urllib.request.urlopen(req, timeout=timeout, context=_ssl_context()) as resp:
        return json.loads(resp.read().decode())


def select_polymarket_universe(
    n_liquid: int = 5,
    n_thin: int = 5,
    thin_band: tuple[int, int] = (20, 40),
    candidate_pool: int = 100,
    min_volume24hr: float = 1.0,
    timeout: float = 10.0,
) -> list[dict]:
    """Stratified market-selection rule (DATA-INFRA-001) -- stated and
    defensible, not ad hoc.

    Candidates are the `candidate_pool` currently-active, non-closed,
    order-book-enabled Polymarket markets with the highest trailing-24h
    volume (Gamma's own `order=volume24hr` sort, taken as given rather
    than re-derived).

    Two strata are drawn from that ranked pool:
      - 'liquid': the top `n_liquid` by volume. The markets a pod is most
        likely to actually study or trade.
      - 'thin': `n_thin` markets from the volume-rank band `thin_band`
        (default ranks 20-40) -- deliberately less liquid.

    Why a thin tier is not optional. Quote-liveness (T2) is close to
    trivially true on the most liquid markets on this venue -- the top
    handful essentially never go one-sided. Polling only the liquid tier
    would accumulate a year of book history that still cannot answer the
    question Gate 0(4) actually failed on, because there would be no
    variance in the outcome being measured. The thin tier is where
    two-sidedness is actually contested, which is what makes the eventual
    quote-liveness measurement informative rather than a foregone
    conclusion. This is also the honest answer to "a badly chosen universe
    accumulates useless history at full cost": an all-liquid universe is
    the badly chosen one for this purpose, even though it looks like the
    "better" data by every conventional liquidity screen.

    Markets below `min_volume24hr` are excluded from both tiers -- a
    market with no observed trading in the last 24h is not obviously
    distinguishable from one with no book at all, and capturing it
    accumulates snapshots that answer a question ("is this market's book
    alive") the firm did not ask.
    """
    raw = _gamma_get(
        {
            "active": "true",
            "closed": "false",
            "enableOrderBook": "true",
            "order": "volume24hr",
            "ascending": "false",
            "limit": str(candidate_pool),
        },
        timeout=timeout,
    )

    candidates = []
    for m in raw:
        tok_raw = m.get("clobTokenIds")
        out_raw = m.get("outcomes")
        if not tok_raw or not out_raw:
            continue
        try:
            token_ids = json.loads(tok_raw)
            outcomes = json.loads(out_raw)
        except (TypeError, ValueError):
            continue
        if len(token_ids) != len(outcomes) or not token_ids:
            continue
        vol = float(m.get("volume24hr") or 0.0)
        if vol < min_volume24hr:
            continue
        candidates.append(
            {
                "condition_id": m.get("conditionId"),
                "question": m.get("question"),
                "slug": m.get("slug"),
                "volume24hr": vol,
                "end_date": m.get("endDateIso") or m.get("endDate"),
                "tokens": dict(zip(outcomes, token_ids)),
            }
        )
    # candidates is already ranked by volume24hr descending (Gamma's sort);
    # tier assignment is a positional slice of that ranking, not a re-sort.
    lo, hi = thin_band
    liquid = candidates[:n_liquid]
    thin = candidates[lo:hi][:n_thin]
    for c in liquid:
        c["tier"] = "liquid"
    for c in thin:
        c["tier"] = "thin"
    return liquid + thin


def _check_market_status(condition_ids: list[str], timeout: float = 10.0) -> dict[str, dict]:
    """Batch re-check of tracked markets' active/closed state, one Gamma
    call for the whole tracked set."""
    if not condition_ids:
        return {}
    raw = _gamma_get({"condition_ids": condition_ids}, timeout=timeout)
    return {m.get("conditionId"): m for m in raw if isinstance(m, dict)}


def load_universe_state(path: str) -> dict:
    if not os.path.exists(path):
        return {"markets": {}}
    with open(path) as f:
        return json.load(f)


def save_universe_state(path: str, state: dict) -> None:
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(state, f, indent=2, default=str)
    os.replace(tmp, path)  # atomic on POSIX -- a crash mid-write cannot corrupt the state file


def refresh_universe(
    state_path: str,
    n_liquid: int = 5,
    n_thin: int = 5,
    thin_band: tuple[int, int] = (20, 40),
) -> dict:
    """Load the persisted market universe, retire any tracked market that
    has resolved since the last run, and top up freed slots with a fresh
    selection.

    This is the mechanism for "resolved markets stop being polled":
    status is checked every call against Gamma's live `closed` flag, and
    a market that flips to closed is marked 'resolved' in the state file
    (kept, not deleted -- it is the record of what was tracked and for how
    long) and dropped from the active set passed to the capture step. The
    tracked set is otherwise stable across runs (existing active markets
    are kept as-is, not re-selected every tick), so a market's history
    stays continuous for as long as it remains open.
    """
    state = load_universe_state(state_path)
    tracked = state.get("markets", {})

    active_ids = [cid for cid, m in tracked.items() if m.get("status") == "active"]
    if active_ids:
        statuses = _check_market_status(active_ids)
        for cid in active_ids:
            m = tracked[cid]
            live = statuses.get(cid)
            if live is None or live.get("closed") or not live.get("active", True):
                m["status"] = "resolved"
                m["resolved_detected_utc"] = time.time()

    n_active_liquid = sum(1 for m in tracked.values() if m.get("tier") == "liquid" and m.get("status") == "active")
    n_active_thin = sum(1 for m in tracked.values() if m.get("tier") == "thin" and m.get("status") == "active")
    need_liquid = max(0, n_liquid - n_active_liquid)
    need_thin = max(0, n_thin - n_active_thin)

    if need_liquid or need_thin:
        candidates = select_polymarket_universe(n_liquid=n_liquid, n_thin=n_thin, thin_band=thin_band)
        existing = set(tracked.keys())
        for c in candidates:
            cid = c["condition_id"]
            if not cid or cid in existing:
                continue
            if c["tier"] == "liquid" and need_liquid > 0:
                c["status"] = "active"
                c["first_tracked_utc"] = time.time()
                tracked[cid] = c
                need_liquid -= 1
            elif c["tier"] == "thin" and need_thin > 0:
                c["status"] = "active"
                c["first_tracked_utc"] = time.time()
                tracked[cid] = c
                need_thin -= 1

    state["markets"] = tracked
    state["last_refreshed_utc"] = time.time()
    save_universe_state(state_path, state)
    return state


def parse_polymarket_book(raw: dict, depth: int = 10) -> pd.DataFrame:
    """Parse one OrderBookSummary (as returned by /book or /books) into a
    single-row wide frame of scalar fields, indexed by the venue's own
    snapshot `event_time`. Pure -- no I/O, testable offline per this
    module's design rule.

    Levels beyond `depth` on either side are dropped from the scalar
    fields (not from the raw response -- the caller separately stores the
    full, undepth-limited response in `PITStore.documents` so no
    information is discarded, only de-prioritized for the fast/queryable
    path). `n_bid_levels`/`n_ask_levels` record the TRUE level count seen,
    regardless of `depth`, so a researcher can tell a 3-level book from a
    30-level book that was merely truncated to `depth`.
    """
    event_time = pd.to_datetime(int(raw["timestamp"]), unit="ms", utc=True)
    bids = sorted(raw.get("bids") or [], key=lambda lv: -float(lv["price"]))
    asks = sorted(raw.get("asks") or [], key=lambda lv: float(lv["price"]))

    fields: dict[str, float] = {
        "n_bid_levels": float(len(bids)),
        "n_ask_levels": float(len(asks)),
        "two_sided": 1.0 if (bids and asks) else 0.0,
    }
    if bids:
        best_bid = float(bids[0]["price"])
        fields["best_bid"] = best_bid
        fields["bid_size_at_touch"] = float(bids[0]["size"])
    if asks:
        best_ask = float(asks[0]["price"])
        fields["best_ask"] = best_ask
        fields["ask_size_at_touch"] = float(asks[0]["size"])
    if bids and asks:
        fields["mid"] = (best_bid + best_ask) / 2.0
        fields["spread"] = best_ask - best_bid
    for i, lv in enumerate(bids[:depth], start=1):
        fields[f"bid_price_l{i}"] = float(lv["price"])
        fields[f"bid_size_l{i}"] = float(lv["size"])
    for i, lv in enumerate(asks[:depth], start=1):
        fields[f"ask_price_l{i}"] = float(lv["price"])
        fields[f"ask_size_l{i}"] = float(lv["size"])
    ltp = raw.get("last_trade_price")
    if ltp not in (None, ""):
        try:
            fields["last_trade_price"] = float(ltp)
        except (TypeError, ValueError):
            pass

    return pd.DataFrame([fields], index=pd.DatetimeIndex([event_time], name="event_time"))


def fetch_polymarket_books(token_ids: list[str], timeout: float = 10.0) -> tuple[list[dict], float]:
    """POST https://clob.polymarket.com/books -- the documented batch
    order-book endpoint. One HTTP round trip returns every token's book
    together, which is both why the whole batch shares one knowledge_time
    and why this is the request-count-efficient choice over N calls to
    the singular /book (rate limit for /books is 500 req/10s vs 1500 req/
    10s for /book -- irrelevant at this firm's scale either way, but the
    batch call is also simply kinder to a public venue).

    Returns (raw response list, knowledge_time) where knowledge_time is
    captured immediately after the response is received -- the earliest
    honest instant at which this information was knowable to the firm.
    """
    import urllib.request

    body = json.dumps([{"token_id": t} for t in token_ids]).encode()
    req = urllib.request.Request(
        CLOB_BOOKS_URL, data=body, method="POST",
        headers={"Content-Type": "application/json",
                 "User-Agent": "Castellan-Data-Infra/1.0 (research infrastructure)"},
    )
    with urllib.request.urlopen(req, timeout=timeout, context=_ssl_context()) as resp:
        raw = json.loads(resp.read().decode())
    knowledge_time = time.time()
    return raw, knowledge_time


def ingest_polymarket_books(
    store: PITStore,
    token_meta: dict[str, dict],
    depth: int = 10,
    timeout: float = 10.0,
    max_retries: int = 3,
    backoff_s: float = 2.0,
) -> dict:
    """Fetch and ingest one polling round of order-book snapshots.

    ``token_meta``: token_id -> {"condition_id", "question", "slug",
    "outcome"}, i.e. one entry per outcome side (Yes/No) of every tracked
    market -- Yes and No are genuinely separate resting order books on
    Polymarket's CLOB, not guaranteed complementary, so each is captured
    and stored under its own token_id as ``symbol``. ``source`` is fixed
    as ``'polymarket-clob'``.

    Two writes per successfully-captured token, both point-in-time:
      1. ``store.ingest`` -- the scalar fields from `parse_polymarket_book`,
         queryable via `asof`/`rows_in_window` like any other observation.
      2. ``store.ingest_documents`` -- the full, undepth-limited raw
         response, ``ref`` deduplicated on ``f"{token_id}:{venue_timestamp}"``
         so re-running against an unchanged snapshot is a no-op, not a
         duplicate row.

    Failure handling: the whole batch fetch retries transient HTTP-level
    failures (timeout, connection error, 5xx) up to `max_retries` with
    exponential backoff; if every attempt fails, NOTHING is written and
    the failure is reported for every requested token (the store's own
    ingest() is already all-or-nothing per call; this keeps the same
    property at the poll level for a wholesale outage). A token that is
    present in the request but missing or malformed in a partially-
    successful response is recorded as an individual failure and skipped
    -- it does not block ingestion of the tokens that did come back clean.
    """
    token_ids = list(token_meta.keys())
    raw = None
    knowledge_time = None
    last_err = None
    for attempt in range(max_retries):
        try:
            raw, knowledge_time = fetch_polymarket_books(token_ids, timeout=timeout)
            break
        except Exception as e:  # noqa: BLE001 -- deliberately broad: any network/HTTP failure retries
            last_err = e
            if attempt < max_retries - 1:
                time.sleep(backoff_s * (2 ** attempt))
    if raw is None:
        return {
            "ok": False, "error": repr(last_err), "captured": [],
            "failed": token_ids, "n_requested": len(token_ids),
        }

    by_asset = {r.get("asset_id"): r for r in raw if isinstance(r, dict)}
    captured, failed = [], []
    for tid, meta in token_meta.items():
        entry = by_asset.get(tid)
        if entry is None:
            failed.append(tid)
            continue
        try:
            df = parse_polymarket_book(entry, depth=depth)
            store.ingest("polymarket-clob", tid, df, knowledge_time=knowledge_time)
            store.ingest_documents(
                "polymarket-clob", tid,
                [{
                    "doc_type": "book_snapshot",
                    "event_time": df.index[0],
                    "knowledge_time": knowledge_time,
                    "ref": f"{tid}:{entry.get('timestamp')}",
                    "meta": {
                        "condition_id": meta.get("condition_id"),
                        "question": meta.get("question"),
                        "slug": meta.get("slug"),
                        "outcome": meta.get("outcome"),
                        "raw": entry,
                    },
                }],
            )
            captured.append(tid)
        except Exception:  # noqa: BLE001 -- one bad token must not sink the batch
            failed.append(tid)

    return {
        "ok": True, "captured": captured, "failed": failed,
        "n_requested": len(token_ids), "knowledge_time": knowledge_time,
    }
