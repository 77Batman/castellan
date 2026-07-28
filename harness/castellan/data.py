"""Point-in-time data store — Charter 4.6, enforced.

Every observation carries two timestamps:

- ``event_time``      when the value became true (the bar's date)
- ``knowledge_time``  when this value was first observable to the firm
                      (the ingestion moment, UTC epoch)

The store is append-only. A vendor restating a value (yfinance
retroactively re-adjusting a close, FRED revising a series) produces a
NEW version row with a later ``knowledge_time``; the old row is never
touched, and the restatement is logged to the Trial Registry as an
incident (Charter, Seat 9: a leak discovered late invalidates every
result derived from it — so restatements are first-class events).

``asof(decision_time)`` reconstructs exactly what was knowable at that
moment: the latest version of each (event_time, field) with
``knowledge_time <= decision_time``. Backtests that query through
``asof`` are structurally incapable of the retro-adjustment look-ahead.
"""

from __future__ import annotations

import json
import math
import sqlite3
import time

import numpy as np
import pandas as pd

from .registry import TrialRegistry

SCHEMA = """
CREATE TABLE IF NOT EXISTS observations (
    obs_id         INTEGER PRIMARY KEY AUTOINCREMENT,
    source         TEXT NOT NULL,
    symbol         TEXT NOT NULL,
    field          TEXT NOT NULL,
    event_time     TEXT NOT NULL,     -- ISO-8601, sortable
    knowledge_time REAL NOT NULL,     -- UTC epoch seconds
    value          REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_obs
    ON observations (source, symbol, field, event_time, knowledge_time);

CREATE TABLE IF NOT EXISTS documents (
    doc_id         INTEGER PRIMARY KEY AUTOINCREMENT,
    source         TEXT NOT NULL,
    symbol         TEXT NOT NULL,
    doc_type       TEXT NOT NULL,     -- e.g. 8-K, 10-Q
    event_time     TEXT NOT NULL,     -- filing/acceptance datetime, ISO
    knowledge_time REAL NOT NULL,
    ref            TEXT NOT NULL,     -- accession number or URL
    meta_json      TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_docs
    ON documents (source, symbol, doc_type, event_time);
"""


def _iso(ts) -> str:
    return pd.Timestamp(ts).isoformat()


class PITStore:
    def __init__(self, path: str, registry: TrialRegistry | None = None):
        self.path = path
        self.registry = registry
        self.conn = sqlite3.connect(path)
        self.conn.executescript(SCHEMA)
        self.conn.commit()

    # ------------------------------------------------------------------
    # Ingest (append-only, restatement-aware)
    # ------------------------------------------------------------------

    def ingest(
        self,
        source: str,
        symbol: str,
        df: pd.DataFrame,
        knowledge_time: float | None = None,
        rtol: float = 1e-9,
    ) -> dict:
        """Append a wide frame (DatetimeIndex, numeric columns = fields).

        For each (event_time, field): if the store has no version, insert;
        if the latest version equals the incoming value, skip; if it
        DIFFERS, insert a new version and log a ``data_restatement``
        incident. Returns counts {'new', 'unchanged', 'restated'}.

        ``knowledge_time`` defaults to now. Passing a historical value is
        for reconstructing vendor vintages (e.g. ALFRED) and is the
        caller's assertion about when the data was truly observable.
        """
        kt = time.time() if knowledge_time is None else float(knowledge_time)
        latest = self._latest_map(source, symbol)
        new = unchanged = restated = 0
        rows = []
        restatements = []
        for et, row in df.sort_index().iterrows():
            et_iso = _iso(et)
            for field, val in row.items():
                if val is None or (isinstance(val, float) and math.isnan(val)):
                    continue
                val = float(val)
                key = (field, et_iso)
                prev = latest.get(key)
                if prev is None:
                    rows.append((source, symbol, field, et_iso, kt, val))
                    new += 1
                elif math.isclose(prev, val, rel_tol=rtol, abs_tol=1e-12):
                    unchanged += 1
                else:
                    rows.append((source, symbol, field, et_iso, kt, val))
                    restated += 1
                    restatements.append(
                        {"field": field, "event_time": et_iso,
                         "old": prev, "new": val}
                    )
                latest[key] = val
        if rows:
            self.conn.executemany(
                "INSERT INTO observations (source, symbol, field, "
                "event_time, knowledge_time, value) VALUES (?,?,?,?,?,?)",
                rows,
            )
            self.conn.commit()
        if restatements and self.registry is not None:
            self.registry.log_event(
                "data_restatement", None,
                {"source": source, "symbol": symbol,
                 "count": len(restatements),
                 "sample": restatements[:10]},
            )
        return {"new": new, "unchanged": unchanged, "restated": restated}

    def _latest_map(self, source: str, symbol: str) -> dict:
        cur = self.conn.execute(
            "SELECT field, event_time, value FROM observations "
            "WHERE source=? AND symbol=? "
            "ORDER BY knowledge_time ASC",
            (source, symbol),
        )
        out: dict = {}
        for field, et, val in cur.fetchall():
            out[(field, et)] = val  # later rows overwrite => latest wins
        return out

    # ------------------------------------------------------------------
    # Point-in-time queries
    # ------------------------------------------------------------------

    def asof(
        self,
        source: str,
        symbol: str,
        decision_time: float | str | pd.Timestamp,
        fields: list[str] | None = None,
    ) -> pd.DataFrame:
        """What was knowable at ``decision_time``: latest version of each
        (event_time, field) with knowledge_time <= decision_time. Returns
        a wide frame indexed by event_time."""
        if not isinstance(decision_time, (int, float)):
            decision_time = pd.Timestamp(decision_time).timestamp()
        q = (
            "SELECT o.field, o.event_time, o.value FROM observations o "
            "WHERE o.source=? AND o.symbol=? AND o.knowledge_time<=? "
            "AND o.knowledge_time = ("
            "  SELECT MAX(o2.knowledge_time) FROM observations o2 "
            "  WHERE o2.source=o.source AND o2.symbol=o.symbol "
            "  AND o2.field=o.field AND o2.event_time=o.event_time "
            "  AND o2.knowledge_time<=?)"
        )
        args = [source, symbol, decision_time, decision_time]
        if fields:
            q += f" AND o.field IN ({','.join('?' * len(fields))})"
            args += list(fields)
        cur = self.conn.execute(q, args)
        rows = cur.fetchall()
        if not rows:
            return pd.DataFrame()
        df = pd.DataFrame(rows, columns=["field", "event_time", "value"])
        wide = df.pivot(index="event_time", columns="field", values="value")
        wide.index = pd.to_datetime(wide.index)
        wide.columns.name = None
        return wide.sort_index()

    def latest(self, source: str, symbol: str,
               fields: list[str] | None = None) -> pd.DataFrame:
        return self.asof(source, symbol, time.time() + 1, fields)

    def restatement_history(self, source: str, symbol: str) -> pd.DataFrame:
        """All (event_time, field) with more than one version."""
        cur = self.conn.execute(
            "SELECT field, event_time, COUNT(*) c, MIN(value), MAX(value) "
            "FROM observations WHERE source=? AND symbol=? "
            "GROUP BY field, event_time HAVING c > 1",
            (source, symbol),
        )
        return pd.DataFrame(
            cur.fetchall(),
            columns=["field", "event_time", "versions", "min_value", "max_value"],
        )

    # ------------------------------------------------------------------
    # Documents (EDGAR filings etc.)
    # ------------------------------------------------------------------

    def ingest_documents(self, source: str, symbol: str,
                         docs: list[dict]) -> int:
        """Each doc: {doc_type, event_time, ref, meta(dict),
        knowledge_time(optional)}. De-duplicated on (source, ref)."""
        inserted = 0
        for d in docs:
            exists = self.conn.execute(
                "SELECT 1 FROM documents WHERE source=? AND ref=?",
                (source, d["ref"]),
            ).fetchone()
            if exists:
                continue
            self.conn.execute(
                "INSERT INTO documents (source, symbol, doc_type, "
                "event_time, knowledge_time, ref, meta_json) "
                "VALUES (?,?,?,?,?,?,?)",
                (source, symbol, d["doc_type"], _iso(d["event_time"]),
                 float(d.get("knowledge_time", time.time())),
                 d["ref"], json.dumps(d.get("meta", {}), default=str)),
            )
            inserted += 1
        self.conn.commit()
        return inserted

    def documents_asof(self, source: str, symbol: str,
                       decision_time) -> pd.DataFrame:
        dt = pd.Timestamp(decision_time).isoformat()
        cur = self.conn.execute(
            "SELECT doc_type, event_time, ref, meta_json FROM documents "
            "WHERE source=? AND symbol=? AND event_time<=? "
            "ORDER BY event_time",
            (source, symbol, dt),
        )
        rows = [
            {"doc_type": r[0], "event_time": r[1], "ref": r[2],
             "meta": json.loads(r[3])}
            for r in cur.fetchall()
        ]
        return pd.DataFrame(rows)

    def close(self):
        self.conn.close()


# ----------------------------------------------------------------------
# Point-in-time adjustment — the yfinance retro-adjustment fix
# ----------------------------------------------------------------------

def pit_adjusted_close(
    store: PITStore,
    source: str,
    symbol: str,
    decision_time,
    include_dividends: bool = True,
) -> pd.Series:
    """Back-adjusted close using ONLY corporate actions knowable at
    ``decision_time``.

    Raw closes are stored unadjusted; splits (field ``split``, ratio,
    e.g. 4.0 for 4-for-1) and dividends (field ``dividend``, cash per
    share, ex-date) are stored as their own point-in-time observations.
    A split announced after ``decision_time`` therefore cannot leak into
    a signal computed for that date — which is exactly the hazard of
    consuming yfinance's pre-adjusted series directly.
    """
    df = store.asof(source, symbol, decision_time,
                    fields=["close", "split", "dividend"])
    if df.empty or "close" not in df:
        return pd.Series(dtype=float)
    close = df["close"].dropna().sort_index()
    factor = pd.Series(1.0, index=close.index)

    # Splits: all prices strictly before the split date divide by ratio.
    if "split" in df:
        for ex_date, ratio in df["split"].dropna().items():
            if ratio and ratio > 0 and ratio != 1.0:
                factor.loc[factor.index < ex_date] /= ratio

    # Dividends: multiply prices before ex-date by (1 - div / prev close).
    if include_dividends and "dividend" in df:
        for ex_date, div in df["dividend"].dropna().sort_index().items():
            prior = close.loc[close.index < ex_date]
            if div and len(prior):
                prev_close_raw = prior.iloc[-1]
                if prev_close_raw > 0 and div < prev_close_raw:
                    factor.loc[factor.index < ex_date] *= (
                        1.0 - div / prev_close_raw
                    )

    return (close * factor).rename(symbol)


def pit_price_panel(
    store: PITStore,
    source: str,
    symbols: list[str],
    decision_time,
    include_dividends: bool = True,
) -> pd.DataFrame:
    """Adjusted close panel, one asof reconstruction per symbol."""
    cols = [
        pit_adjusted_close(store, source, s, decision_time, include_dividends)
        for s in symbols
    ]
    return pd.concat(cols, axis=1).sort_index()
