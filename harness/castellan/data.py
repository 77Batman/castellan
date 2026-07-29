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

from .errors import HoldoutCeilingError
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

CREATE TABLE IF NOT EXISTS ingest_ceiling (
    ceiling_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    source         TEXT NOT NULL,
    dataset_id     TEXT NOT NULL,     -- Ruling 001 D2; maps to `symbol` above
    family         TEXT NOT NULL,
    cutoff         TEXT NOT NULL,     -- ISO-8601, UTC, inclusive lower bound of holdout
    spec_sha256    TEXT NOT NULL,     -- the sealed spec hash that authorizes a lift
    active         INTEGER NOT NULL DEFAULT 1,
    created_utc    REAL NOT NULL,
    lifted_utc     REAL,              -- Acceptance 001 C-9: when the lift happened
    lifted_by_event_id INTEGER        -- and the holdout_acquired event id that did it
);
CREATE INDEX IF NOT EXISTS idx_ceiling
    ON ingest_ceiling (source, dataset_id, active);
"""


def _iso(ts) -> str:
    """Normalize to a UTC-anchored ISO-8601 string (Acceptance 001 C-5).

    Previously this kept the caller's own UTC offset
    (``pd.Timestamp(ts).isoformat()``), so two observations at the same
    instant but different offsets sorted and compared as different
    strings — the measured false negative in I-016: a bar stamped
    ``America/New_York 2024-06-30 21:00`` (= ``2024-07-01T01:00Z``, inside
    a holdout window opening at ``C = 2024-07-01T00:00Z``) was stored as
    ``2024-06-30T21:00:00-04:00`` and every string-comparison query
    (``rows_in_window``, ``asof``, ``_latest_map``) missed it. Normalizing
    to UTC here makes every stored ``event_time`` string comparison an
    instant comparison, not a string comparison with a hidden offset.
    """
    t = pd.Timestamp(ts)
    t = t.tz_localize("UTC") if t.tzinfo is None else t.tz_convert("UTC")
    return t.isoformat()


class PITStore:
    def __init__(self, path: str, registry: TrialRegistry | None = None):
        self.path = path
        self.registry = registry
        self.conn = sqlite3.connect(path)
        self.conn.executescript(SCHEMA)
        self.conn.commit()
        self._migrate()

    def _migrate(self) -> None:
        """Retrofit columns added after a pit.db may already exist, same
        pattern as TrialRegistry._migrate (Acceptance 001 C-9)."""
        cols = [r[1] for r in self.conn.execute("PRAGMA table_info(ingest_ceiling)")]
        changed = False
        for name, sqltype in [("lifted_utc", "REAL"), ("lifted_by_event_id", "INTEGER")]:
            if name not in cols:
                self.conn.execute(f"ALTER TABLE ingest_ceiling ADD COLUMN {name} {sqltype}")
                changed = True
        if changed:
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

        Ruling 001 D2: if ``(source, symbol)`` carries an active holdout
        ingest ceiling, any observation with ``event_time`` strictly after
        the sealed cutoff is refused — the WHOLE batch, atomically. Nothing
        is written; this is the compensating control for the fact that,
        under P-1, over-ingesting is the natural way to leak the holdout.
        """
        kt = time.time() if knowledge_time is None else float(knowledge_time)
        self._enforce_holdout_ceiling(source, symbol, df)
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

    # ------------------------------------------------------------------
    # Holdout ingest ceiling (Ruling 001 D2) — the compensating control
    # for the fact that under Amendment P-1, over-ingesting is the
    # natural way to leak a holdout.
    # ------------------------------------------------------------------

    def _active_ceilings(self, source: str, dataset_id: str) -> list[dict]:
        cur = self.conn.execute(
            "SELECT family, cutoff, spec_sha256 FROM ingest_ceiling "
            "WHERE source=? AND dataset_id=? AND active=1",
            (source, dataset_id),
        )
        return [
            {"family": r[0], "cutoff": r[1], "spec_sha256": r[2]}
            for r in cur.fetchall()
        ]

    def _enforce_holdout_ceiling(self, source: str, symbol: str, df: pd.DataFrame) -> None:
        if df.empty:
            return
        idx = pd.to_datetime(df.index)
        idx = idx.tz_localize("UTC") if idx.tz is None else idx.tz_convert("UTC")
        self._enforce_holdout_ceiling_on_index(source, symbol, idx, kind="ingest")

    def _enforce_holdout_ceiling_on_index(
        self, source: str, symbol: str, idx, kind: str = "ingest"
    ) -> None:
        """Shared enforcement, so every entry point into the store goes
        through the same check (Acceptance 001 C-4). ``ingest()`` calls
        this via :meth:`_enforce_holdout_ceiling` with the frame's
        DatetimeIndex; ``ingest_documents()`` (previously unguarded — a
        second, fully open ingest path, I-017) calls it directly with the
        documents' event_times. ``kind`` only affects the log/error text.
        """
        ceilings = self._active_ceilings(source, symbol)
        if not ceilings or len(idx) == 0:
            return
        for c in ceilings:
            cutoff_ts = pd.Timestamp(c["cutoff"])
            violating = idx > cutoff_ts  # event_time == C is in-sample (B6)
            if violating.any():
                n = int(violating.sum())
                if self.registry is not None:
                    self.registry.log_event(
                        "holdout_ceiling_violation",
                        c["family"],
                        {
                            "source": source,
                            "dataset_id": symbol,
                            "cutoff": c["cutoff"],
                            "n_violating": n,
                            "first_violating_event_time": str(idx[violating].min()),
                            "kind": kind,
                        },
                    )
                raise HoldoutCeilingError(
                    f"{kind.capitalize()} for (source={source!r}, "
                    f"dataset_id={symbol!r}) contains {n} observation(s) "
                    f"with event_time after the sealed holdout cutoff "
                    f"{c['cutoff']} (family {c['family']!r}). Refused; "
                    "nothing was ingested."
                )

    def set_holdout_ceiling(
        self, source: str, dataset_id: str, family: str, cutoff, spec_sha256: str
    ) -> None:
        """Written once, at seal time, from the sealed spec's cutoff `C`.
        Public — this is the only sanctioned way to *create* a ceiling.
        Raising, lowering, or removing one afterwards goes only through
        :meth:`_lift_ceiling`, called from ``HoldoutVault.acquire_once``
        (Ruling 001 B5)."""
        cutoff_iso = _iso(cutoff)
        existing = self.conn.execute(
            "SELECT 1 FROM ingest_ceiling WHERE source=? AND dataset_id=? "
            "AND family=?",
            (source, dataset_id, family),
        ).fetchone()
        if existing is not None:
            raise HoldoutCeilingError(
                f"A ceiling for (source={source!r}, dataset_id={dataset_id!r}, "
                f"family={family!r}) already exists; a vault seals a "
                "dataset's ceiling exactly once."
            )
        self.conn.execute(
            "INSERT INTO ingest_ceiling (source, dataset_id, family, "
            "cutoff, spec_sha256, active, created_utc) VALUES (?,?,?,?,?,1,?)",
            (source, dataset_id, family, cutoff_iso, spec_sha256, time.time()),
        )
        self.conn.commit()

    def _lift_ceiling(
        self, source: str, dataset_id: str, family: str, spec_sha256: str,
        lifted_by_event_id: int | None = None,
    ) -> None:
        """Internal. The *only* way a ceiling becomes inactive. Requires the
        spec hash sealed at creation time — the same hash D4's tamper check
        verifies — so a caller without it (i.e. anyone other than
        ``HoldoutVault.acquire_once`` after it has independently verified
        the sealed spec) cannot lift a ceiling. This is what makes B5 hold:
        "cannot be raised, lowered, or removed through any API other than
        the D3 acquisition path; a direct mutation attempt raises."

        Acceptance 001 C-9: records WHICH acquisition lifted the ceiling
        (``lifted_utc`` + the ``holdout_acquired`` event id), not just
        ``active=0``. Ruling 001 B5/D2's intent is that a lift is scoped to
        a single sealed acquisition; recording the event id is what makes
        that auditable after the fact rather than merely true in code.
        """
        row = self.conn.execute(
            "SELECT spec_sha256 FROM ingest_ceiling WHERE source=? AND "
            "dataset_id=? AND family=? AND active=1",
            (source, dataset_id, family),
        ).fetchone()
        if row is None:
            raise HoldoutCeilingError(
                f"No active ceiling for (source={source!r}, "
                f"dataset_id={dataset_id!r}, family={family!r})."
            )
        if row[0] != spec_sha256:
            raise HoldoutCeilingError(
                "Ceiling lift refused: the supplied spec hash does not "
                "match the hash recorded at seal time. Direct mutation is "
                "not a sanctioned path."
            )
        self.conn.execute(
            "UPDATE ingest_ceiling SET active=0, lifted_utc=?, "
            "lifted_by_event_id=? WHERE source=? AND dataset_id=? AND family=?",
            (time.time(), lifted_by_event_id, source, dataset_id, family),
        )
        self.conn.commit()

    def rows_in_window(
        self, source: str, symbol: str, after, upto, knowledge_time_before: float
    ) -> list[dict]:
        """Ruling 001 D1 leak-detection control: rows for (source, symbol)
        with ``event_time`` in ``(after, upto]`` whose ``knowledge_time`` is
        strictly before ``knowledge_time_before``. Any such row was
        knowable before a legitimate acquisition would have made it
        knowable — i.e. a leak, however it got there."""
        after_iso, upto_iso = _iso(after), _iso(upto)
        cur = self.conn.execute(
            "SELECT field, event_time, knowledge_time, value FROM "
            "observations WHERE source=? AND symbol=? AND event_time>? "
            "AND event_time<=? AND knowledge_time<?",
            (source, symbol, after_iso, upto_iso, knowledge_time_before),
        )
        return [
            {"field": r[0], "event_time": r[1], "knowledge_time": r[2], "value": r[3]}
            for r in cur.fetchall()
        ]

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
        idx = pd.to_datetime(wide.index)
        # C-5 normalizes storage to UTC (fixing the D1 leak-detection false
        # negative), but that is a storage/comparison-correctness fix, not
        # a promise to change what tz-awareness callers get back. Strip
        # the tz label here: since storage is now uniformly UTC, this is a
        # no-op for the previously-common naive-input case (numerically
        # identical to the pre-C-5 output) and, for genuinely tz-aware
        # non-UTC input, now correctly represents the true UTC instant
        # rather than the caller's local wall-clock string.
        wide.index = idx.tz_convert(None) if idx.tz is not None else idx
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
        knowledge_time(optional)}. De-duplicated on (source, ref).

        Ruling 001 D2 / Acceptance 001 C-4: this path previously enforced
        no holdout ceiling at all (I-017) — a second, fully open ingest
        entry point beside ``ingest()``'s guarded one. Checked atomically
        against every doc's ``event_time`` before any row is inserted, on
        the same "the safe path must be the default path" principle: a
        batch containing any post-cutoff document is refused whole,
        nothing is written."""
        if docs:
            idx = pd.to_datetime([d["event_time"] for d in docs])
            idx = idx.tz_localize("UTC") if idx.tz is None else idx.tz_convert("UTC")
            self._enforce_holdout_ceiling_on_index(source, symbol, idx, kind="ingest_documents")
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
