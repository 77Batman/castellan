"""The paper book — three blotters, kept separate on purpose.

Charter Seat 10: order, execution, and trade are three distinct records
"so that the breaks between them are visible." Merging them hides
exactly the operational errors the split exists to catch.

Enforced here:

- **Same-bar prohibition at the book level too**: a fill timestamped at
  or before its order raises. The engine enforces it for backtests; the
  book enforces it for the live paper flow.
- **One cost library**: fills price costs through a ``CostModel``; there
  is no field for a hand-rolled cost number.
- **Reconciliation reports breaks, never repairs them.** ``reconcile()``
  rebuilds positions and cash from the trade blotter and compares to the
  running state; any difference is returned as a break for the Issue
  Log. Quiet correction is the failure mode, not the feature.
"""

from __future__ import annotations

import json
import sqlite3
import time
from dataclasses import dataclass

import pandas as pd

from .costs import CostModel

SCHEMA = """
CREATE TABLE IF NOT EXISTS orders (
    order_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    ts          TEXT NOT NULL,
    instrument  TEXT NOT NULL,
    side        TEXT NOT NULL CHECK (side IN ('BUY','SELL')),
    qty         REAL NOT NULL CHECK (qty > 0),
    order_type  TEXT NOT NULL,
    pm          TEXT NOT NULL,
    rationale   TEXT NOT NULL,
    mandate     TEXT NOT NULL DEFAULT 'standing'
);
CREATE TABLE IF NOT EXISTS executions (
    exec_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id    INTEGER NOT NULL REFERENCES orders(order_id),
    ts          TEXT NOT NULL,
    price       REAL NOT NULL,
    qty         REAL NOT NULL,
    venue       TEXT NOT NULL,
    cost_frac   REAL NOT NULL,      -- per-side cost as fraction of notional
    cost_cash   REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS trades (
    trade_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    exec_id        INTEGER NOT NULL REFERENCES executions(exec_id),
    instrument     TEXT NOT NULL,
    qty_signed     REAL NOT NULL,
    price          REAL NOT NULL,
    cost_cash      REAL NOT NULL,
    realized_pnl   REAL NOT NULL,
    position_after REAL NOT NULL,
    avg_cost_after REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS state (
    key TEXT PRIMARY KEY, value TEXT NOT NULL
);
"""


class BookError(RuntimeError):
    pass


class SameBarBookFillError(BookError):
    pass


@dataclass
class Fill:
    order_id: int
    exec_id: int
    trade_id: int
    instrument: str
    qty_signed: float
    price: float
    cost_cash: float
    realized_pnl: float
    position_after: float


class PaperBook:
    def __init__(self, path: str, starting_cash: float):
        self.conn = sqlite3.connect(path)
        self.conn.executescript(SCHEMA)
        if self._get_state("cash") is None:
            self._set_state("cash", starting_cash)
            self._set_state("starting_cash", starting_cash)
            self._set_state("positions", {})
            self._set_state("avg_costs", {})
        self.conn.commit()

    # -- state ---------------------------------------------------------

    def _get_state(self, key):
        row = self.conn.execute(
            "SELECT value FROM state WHERE key=?", (key,)).fetchone()
        return None if row is None else json.loads(row[0])

    def _set_state(self, key, value):
        self.conn.execute(
            "INSERT INTO state (key, value) VALUES (?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (key, json.dumps(value)))

    @property
    def cash(self) -> float:
        return float(self._get_state("cash"))

    @property
    def positions(self) -> dict[str, float]:
        return {k: float(v) for k, v in self._get_state("positions").items()
                if abs(float(v)) > 1e-12}

    # -- order -> execution -> trade -----------------------------------

    def place_and_fill(
        self,
        instrument: str,
        side: str,
        qty: float,
        order_ts,
        fill_ts,
        fill_price: float,
        cost_model: CostModel,
        pm: str,
        rationale: str,
        sigma_daily: float = 0.0,
        adv_notional: float | None = None,
        venue: str = "simulated",
        order_type: str = "MOC-next",
    ) -> Fill:
        """Log an order, simulate its fill through the shared cost
        library, and book the trade. ``fill_ts`` must be strictly after
        ``order_ts`` — the same-bar prohibition, again, structurally."""
        o_ts, f_ts = pd.Timestamp(order_ts), pd.Timestamp(fill_ts)
        if f_ts <= o_ts:
            raise SameBarBookFillError(
                f"Fill at {f_ts} not after order at {o_ts}: a fill on the "
                "bar that generated the decision is look-ahead.")
        if not rationale.strip():
            raise BookError("Every entry carries a position rationale "
                            "(Charter, Seat 6).")
        side = side.upper()
        sgn = 1.0 if side == "BUY" else -1.0
        notional = qty * fill_price

        cur = self.conn.execute(
            "INSERT INTO orders (ts, instrument, side, qty, order_type, "
            "pm, rationale) VALUES (?,?,?,?,?,?,?)",
            (o_ts.isoformat(), instrument, side, qty, order_type, pm,
             rationale))
        order_id = int(cur.lastrowid)

        cost_frac = float(pd.Series(cost_model.per_side_cost(
            notional, sigma_daily, adv_notional)).iloc[0]) \
            if adv_notional is not None else \
            float(pd.Series(cost_model.per_side_cost(1.0)).iloc[0])
        cost_cash = cost_frac * notional

        cur = self.conn.execute(
            "INSERT INTO executions (order_id, ts, price, qty, venue, "
            "cost_frac, cost_cash) VALUES (?,?,?,?,?,?,?)",
            (order_id, f_ts.isoformat(), fill_price, qty, venue,
             cost_frac, cost_cash))
        exec_id = int(cur.lastrowid)

        # book the trade: average-cost accounting
        positions = self._get_state("positions")
        avg_costs = self._get_state("avg_costs")
        pos = float(positions.get(instrument, 0.0))
        avg = float(avg_costs.get(instrument, 0.0))
        q = sgn * qty
        realized = 0.0
        if pos * q >= 0:  # opening / adding
            new_pos = pos + q
            avg = (abs(pos) * avg + abs(q) * fill_price) / abs(new_pos) \
                if abs(new_pos) > 1e-12 else 0.0
            pos = new_pos
        else:  # reducing / crossing
            closing = min(abs(q), abs(pos))
            realized = closing * (fill_price - avg) * (1 if pos > 0 else -1)
            pos = pos + q
            if abs(pos) < 1e-12:
                pos, avg = 0.0, 0.0
            elif (pos > 0) != (pos - q > 0):  # crossed through zero
                avg = fill_price

        cash = self.cash - q * fill_price - cost_cash
        positions[instrument] = pos
        avg_costs[instrument] = avg
        self._set_state("cash", cash)
        self._set_state("positions", positions)
        self._set_state("avg_costs", avg_costs)

        cur = self.conn.execute(
            "INSERT INTO trades (exec_id, instrument, qty_signed, price, "
            "cost_cash, realized_pnl, position_after, avg_cost_after) "
            "VALUES (?,?,?,?,?,?,?,?)",
            (exec_id, instrument, q, fill_price, cost_cash, realized,
             pos, avg))
        self.conn.commit()
        return Fill(order_id, exec_id, int(cur.lastrowid), instrument, q,
                    fill_price, cost_cash, realized, pos)

    # -- marking and packs ---------------------------------------------

    def mark(self, prices: dict[str, float]) -> dict:
        """Daily pack numbers: equity, cash, unrealized, gross/net
        exposure. Raises if a held instrument has no mark — a missing
        price is escalated, not defaulted."""
        positions = self.positions
        avg_costs = self._get_state("avg_costs")
        missing = [k for k in positions if k not in prices]
        if missing:
            raise BookError(f"No mark for held instruments: {missing}. "
                            "Escalate; do not guess.")
        mv = {k: v * prices[k] for k, v in positions.items()}
        unreal = {k: v * (prices[k] - float(avg_costs.get(k, 0.0)))
                  for k, v in positions.items()}
        gross = sum(abs(x) for x in mv.values())
        net = sum(mv.values())
        equity = self.cash + net
        return {
            "ts_utc": time.time(),
            "cash": self.cash,
            "equity": equity,
            "market_values": mv,
            "unrealized_pnl": unreal,
            "gross_exposure": gross,
            "net_exposure": net,
        }

    # -- reconciliation: report breaks, never repair --------------------

    def reconcile(self) -> dict:
        """Rebuild positions and cash from the trade blotter; compare to
        running state. Returns {'clean': bool, 'breaks': [...]} for the
        Issue Log. This method never mutates state."""
        pos: dict[str, float] = {}
        cash_delta = 0.0
        for inst, q, price, cost in self.conn.execute(
                "SELECT instrument, qty_signed, price, cost_cash FROM trades "
                "ORDER BY trade_id"):
            pos[inst] = pos.get(inst, 0.0) + q
            cash_delta += -q * price - cost
        breaks = []
        state_pos = self._get_state("positions")
        for inst in set(pos) | set(state_pos):
            a = round(pos.get(inst, 0.0), 8)
            b = round(float(state_pos.get(inst, 0.0)), 8)
            if abs(a - b) > 1e-8:
                breaks.append({"kind": "position", "instrument": inst,
                               "from_blotter": a, "running_state": b})
        # cash: starting cash (recorded at book open) + blotter deltas
        # must equal the running cash state exactly.
        expected_cash = float(self._get_state("starting_cash")) + cash_delta
        if abs(expected_cash - self.cash) > 1e-6:
            breaks.append({"kind": "cash",
                           "from_blotter": expected_cash,
                           "running_state": self.cash})
        return {"clean": not breaks, "breaks": breaks,
                "n_trades": self.conn.execute(
                    "SELECT COUNT(*) FROM trades").fetchone()[0]}

    def blotters(self) -> dict[str, pd.DataFrame]:
        return {
            name: pd.read_sql_query(f"SELECT * FROM {name}", self.conn)
            for name in ("orders", "executions", "trades")
        }

    def close(self):
        self.conn.close()
