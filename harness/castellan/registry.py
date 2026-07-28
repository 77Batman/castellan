"""Trial Registry — the denominator of everything.

House rule 3: every backtest run increments the trial counter for its
hypothesis family. This module makes that a property of the code path
rather than a promise: `engine.run_backtest` refuses to run without a
registry handle, and every run writes its config hash, full net return
series, and per-period Sharpe here. N and the cross-sectional Sharpe
dispersion that DSR needs are then computed from the registry, never
self-reported.

The registry also holds the permanent event log: hypothesis
pre-registrations, holdout lock/open/retire events, and gate verdicts.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
import time
from dataclasses import dataclass

import numpy as np

from .stats import sharpe_period

SCHEMA = """
CREATE TABLE IF NOT EXISTS hypotheses (
    family        TEXT PRIMARY KEY,
    statement     TEXT NOT NULL,
    mechanism     TEXT NOT NULL,
    falsifier     TEXT NOT NULL,
    universe      TEXT NOT NULL,
    horizon       TEXT NOT NULL,
    success_criteria TEXT NOT NULL,
    trial_budget  INTEGER NOT NULL,
    created_utc   REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS trials (
    trial_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    family        TEXT NOT NULL REFERENCES hypotheses(family),
    config_json   TEXT NOT NULL,
    config_hash   TEXT NOT NULL,
    returns_blob  BLOB NOT NULL,
    n_bars        INTEGER NOT NULL,
    periods_per_year INTEGER NOT NULL,
    sr_period     REAL,
    notes         TEXT,
    created_utc   REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS events (
    event_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    kind          TEXT NOT NULL,
    family        TEXT,
    detail_json   TEXT NOT NULL,
    created_utc   REAL NOT NULL
);
"""


def _hash_config(config: dict) -> str:
    return hashlib.sha256(
        json.dumps(config, sort_keys=True, default=str).encode()
    ).hexdigest()[:16]


@dataclass
class FamilyStats:
    family: str
    n_trials: int
    trial_budget: int
    sr_period_std: float | None
    sr_period_mean: float | None
    sr_period_best: float | None


class PreRegistrationError(RuntimeError):
    """Raised when a trial is logged against an unregistered hypothesis."""


class TrialRegistry:
    def __init__(self, path: str):
        self.path = path
        self.conn = sqlite3.connect(path)
        self.conn.executescript(SCHEMA)
        self.conn.commit()

    # -- hypotheses ----------------------------------------------------

    def open_hypothesis(
        self,
        family: str,
        statement: str,
        mechanism: str,
        falsifier: str,
        universe: str,
        horizon: str,
        success_criteria: str,
        trial_budget: int,
    ) -> None:
        """Gate 0 pre-registration. Idempotent on family; fields are
        immutable after creation (history is not rewritten)."""
        for name, val in [
            ("statement", statement),
            ("mechanism", mechanism),
            ("falsifier", falsifier),
        ]:
            if not val or not val.strip():
                raise ValueError(f"Pre-registration requires a non-empty {name}")
        cur = self.conn.execute(
            "SELECT family FROM hypotheses WHERE family=?", (family,)
        )
        if cur.fetchone() is not None:
            return
        self.conn.execute(
            "INSERT INTO hypotheses VALUES (?,?,?,?,?,?,?,?,?)",
            (
                family,
                statement,
                mechanism,
                falsifier,
                universe,
                horizon,
                success_criteria,
                int(trial_budget),
                time.time(),
            ),
        )
        self.log_event(
            "hypothesis_registered", family, {"statement": statement}
        )
        self.conn.commit()

    def hypothesis(self, family: str) -> dict | None:
        cur = self.conn.execute(
            "SELECT * FROM hypotheses WHERE family=?", (family,)
        )
        row = cur.fetchone()
        if row is None:
            return None
        cols = [d[0] for d in cur.description]
        return dict(zip(cols, row))

    # -- trials --------------------------------------------------------

    def log_trial(
        self,
        family: str,
        config: dict,
        net_returns: np.ndarray,
        periods_per_year: int,
        notes: str = "",
    ) -> int:
        if self.hypothesis(family) is None:
            raise PreRegistrationError(
                f"Family '{family}' has no Gate 0 pre-registration. "
                "Register the hypothesis (statement, mechanism, falsifier) "
                "before running any backtest."
            )
        r = np.asarray(net_returns, dtype=np.float32)
        sr = sharpe_period(r)
        cur = self.conn.execute(
            "INSERT INTO trials (family, config_json, config_hash, "
            "returns_blob, n_bars, periods_per_year, sr_period, notes, "
            "created_utc) VALUES (?,?,?,?,?,?,?,?,?)",
            (
                family,
                json.dumps(config, sort_keys=True, default=str),
                _hash_config(config),
                r.tobytes(),
                int(r.size),
                int(periods_per_year),
                None if np.isnan(sr) else float(sr),
                notes,
                time.time(),
            ),
        )
        self.conn.commit()
        return int(cur.lastrowid)

    def family_stats(self, family: str) -> FamilyStats:
        hyp = self.hypothesis(family)
        budget = int(hyp["trial_budget"]) if hyp else 0
        cur = self.conn.execute(
            "SELECT sr_period FROM trials WHERE family=?", (family,)
        )
        srs = [row[0] for row in cur.fetchall() if row[0] is not None]
        n = self.conn.execute(
            "SELECT COUNT(*) FROM trials WHERE family=?", (family,)
        ).fetchone()[0]
        if len(srs) >= 2:
            arr = np.array(srs)
            std, mean, best = (
                float(arr.std(ddof=1)),
                float(arr.mean()),
                float(arr.max()),
            )
        else:
            std = mean = best = None
        return FamilyStats(family, int(n), budget, std, mean, best)

    def returns_matrix(self, family: str) -> np.ndarray:
        """(T, N) matrix of all logged trial return series, truncated to
        the shortest common length from the end (most recent bars)."""
        cur = self.conn.execute(
            "SELECT returns_blob, n_bars FROM trials WHERE family=? "
            "ORDER BY trial_id",
            (family,),
        )
        rows = cur.fetchall()
        if not rows:
            return np.empty((0, 0))
        series = [
            np.frombuffer(blob, dtype=np.float32) for blob, _ in rows
        ]
        t_min = min(s.size for s in series)
        return np.column_stack([s[-t_min:] for s in series]).astype(float)

    # -- events / verdicts --------------------------------------------

    def log_event(self, kind: str, family: str | None, detail: dict) -> int:
        cur = self.conn.execute(
            "INSERT INTO events (kind, family, detail_json, created_utc) "
            "VALUES (?,?,?,?)",
            (kind, family, json.dumps(detail, default=str), time.time()),
        )
        self.conn.commit()
        return int(cur.lastrowid)

    def events(self, kind: str | None = None, family: str | None = None) -> list[dict]:
        q = "SELECT event_id, kind, family, detail_json, created_utc FROM events WHERE 1=1"
        args: list = []
        if kind:
            q += " AND kind=?"
            args.append(kind)
        if family:
            q += " AND family=?"
            args.append(family)
        out = []
        for row in self.conn.execute(q + " ORDER BY event_id", args):
            out.append(
                {
                    "event_id": row[0],
                    "kind": row[1],
                    "family": row[2],
                    "detail": json.loads(row[3]),
                    "created_utc": row[4],
                }
            )
        return out

    def close(self):
        self.conn.close()
