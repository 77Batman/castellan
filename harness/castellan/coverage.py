"""Capture-coverage arithmetic -- DATA-INFRA-002 §5.

Pure functions over a raw ``sqlite3.Connection`` onto a ``PITStore``-shaped
database (``observations`` / ``documents`` tables, see ``castellan.data``).
Deliberately independent of ``PITStore`` itself: this only ever reads, and
a read-only connection to a live capture store (including one being
concurrently written to by a running poller) must not go through any
holdout-ceiling or restatement machinery that assumes a writer's
lifecycle.

Two measurement methods are computed and returned side by side rather
than blended, per house rule 6 -- see ``report_polymarket_coverage.py``'s
module docstring for why they answer different questions:

1. **Successful-round count** -- distinct ``knowledge_time`` values in
   ``observations`` for the given source. Every successful capture round
   writes every field of every token under one shared knowledge_time
   (``ingest_polymarket_books`` passes it once per round), so this is an
   exact count with no double-counting risk, and it works retroactively
   for capture history recorded before the heartbeat mechanism existed.
2. **Heartbeat-based attempt count** -- rows under
   ``source='polymarket-capture-meta', symbol='__heartbeat__'``, present
   only from the moment DATA-INFRA-002's heartbeat write was deployed.
   Distinguishes "polled and failed" from "did not poll" going forward;
   silent (by construction) about anything earlier.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone


def _parse_iso(s: str) -> datetime:
    # Storage uses `pd.Timestamp(...).isoformat()`, e.g.
    # "2026-07-29T19:04:05.123456+00:00" -- always has an explicit
    # offset (Acceptance 001 C-5 normalized everything to UTC), so the
    # stdlib parser handles it without needing pandas here.
    return datetime.fromisoformat(s)


def _fmt_z(ts: float) -> str:
    return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def compute_polymarket_coverage(
    conn: sqlite3.Connection,
    source: str = "polymarket-clob",
    cadence_seconds: int = 900,
    gap_threshold_hours: float = 1.0,
    since: str | None = None,
    until: str | None = None,
) -> dict:
    """Returns a dict with the full coverage report. See module docstring
    for the two measurement methods; ``report_polymarket_coverage.py``
    formats this for a human or emits it as JSON unchanged.
    """
    q = "SELECT DISTINCT knowledge_time FROM observations WHERE source=?"
    params: list = [source]
    if since is not None:
        q += " AND knowledge_time >= ?"
        params.append(_parse_iso(since).timestamp())
    if until is not None:
        q += " AND knowledge_time <= ?"
        params.append(_parse_iso(until).timestamp())
    q += " ORDER BY knowledge_time ASC"
    kts = [r[0] for r in conn.execute(q, params).fetchall()]

    n_success = len(kts)
    if n_success == 0:
        return {
            "source": source, "n_success": 0, "first_success": None,
            "last_success": None, "span_hours": 0.0, "expected_polls": 0.0,
            "coverage_pct": 0.0, "gaps": [], "heartbeat_epoch": None,
            "n_heartbeats": 0, "n_heartbeats_failed": 0,
            "pre_heartbeat_span_hours": 0.0,
        }

    first_kt, last_kt = kts[0], kts[-1]
    span_seconds = last_kt - first_kt
    span_hours = span_seconds / 3600.0
    expected_polls = span_seconds / cadence_seconds if cadence_seconds > 0 else 0.0
    coverage_pct = 100.0 * n_success / expected_polls if expected_polls > 0 else 100.0

    gaps = []
    for a, b in zip(kts, kts[1:]):
        hours = (b - a) / 3600.0
        if hours >= gap_threshold_hours:
            gaps.append({"hours": hours, "start": _fmt_z(a), "end": _fmt_z(b)})
    gaps.sort(key=lambda g: -g["hours"])

    # Heartbeat side -- global epoch (first ever heartbeat row in this
    # store), independent of the since/until window, because "when did
    # the mechanism start existing" is a store-wide fact, not a
    # windowed one.
    epoch_row = conn.execute(
        "SELECT MIN(event_time) FROM documents "
        "WHERE source='polymarket-capture-meta' AND symbol='__heartbeat__'"
    ).fetchone()
    heartbeat_epoch = epoch_row[0] if epoch_row and epoch_row[0] is not None else None

    hb_q = ("SELECT event_time, meta_json FROM documents "
            "WHERE source='polymarket-capture-meta' AND symbol='__heartbeat__'")
    hb_params: list = []
    if since is not None:
        hb_q += " AND event_time >= ?"
        hb_params.append(since)
    if until is not None:
        hb_q += " AND event_time <= ?"
        hb_params.append(until)
    hb_rows = conn.execute(hb_q, hb_params).fetchall()
    n_heartbeats = len(hb_rows)
    n_heartbeats_failed = sum(
        1 for _, meta_json in hb_rows if not json.loads(meta_json).get("ok", True)
    )

    pre_heartbeat_span_hours = 0.0
    if heartbeat_epoch is not None:
        epoch_ts = _parse_iso(heartbeat_epoch).timestamp()
        if first_kt < epoch_ts:
            pre_heartbeat_span_hours = (min(epoch_ts, last_kt) - first_kt) / 3600.0

    return {
        "source": source,
        "n_success": n_success,
        "first_success": _fmt_z(first_kt),
        "last_success": _fmt_z(last_kt),
        "span_hours": span_hours,
        "expected_polls": expected_polls,
        "coverage_pct": coverage_pct,
        "gaps": gaps,
        "heartbeat_epoch": heartbeat_epoch,
        "n_heartbeats": n_heartbeats,
        "n_heartbeats_failed": n_heartbeats_failed,
        "pre_heartbeat_span_hours": pre_heartbeat_span_hours,
    }
