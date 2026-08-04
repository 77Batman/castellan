#!/usr/bin/env python3
"""Report Polymarket order-book capture coverage on demand -- DATA-INFRA-002 §5.

Answers, without a human parsing a log tail: over the observed capture
history, how many poll rounds actually landed data, how many were
expected at the declared cadence, what fraction that is, and where the
gaps are. Reads only ``book/pit.db`` (or whatever ``--pit-db`` points
at) -- it is portable across the laptop and the VPS, unlike the launchd
stdout log this firm's coverage arithmetic was previously computed from
by hand.

Two measurement methods, reported side by side, because they answer
subtly different questions and this firm does not blend measures that
were verified separately (house rule 6):

1. **Successful-round detection** (``observations``, source
   ``polymarket-clob``): every successful round writes every field of
   every captured token under one shared ``knowledge_time`` (a single
   float epoch-seconds value passed once per ``store.ingest`` call, see
   ``ingest_polymarket_books``). Distinct ``knowledge_time`` values are
   therefore an exact, dedup-safe count of successful rounds -- this
   works for capture history recorded BEFORE the heartbeat mechanism
   existed, and is in fact how this script cross-checked the CIO's
   hand-computed log-based figure (it found 3 additional successful
   rounds the log never saw, run manually during DATA-INFRA-001 before
   the recurring job was installed -- the log only ever saw launchd-
   triggered rounds).

2. **Heartbeat-based attempt detection** (``documents``, source
   ``polymarket-capture-meta``, symbol ``__heartbeat__``): every poll
   ATTEMPT, successful or not, from the moment the heartbeat mechanism
   was deployed (DATA-INFRA-002). This is what makes "we did not poll"
   distinguishable from "we polled and the whole batch failed" --
   method 1 alone cannot make that distinction, by construction, because
   a total-failure round writes nothing to ``observations`` either way.

**The honest limit stated plainly.** For any window entirely before the
first heartbeat row, this script can report *successful* coverage
(method 1) but CANNOT distinguish "scheduler did not run" from "ran and
failed outright" -- it says so explicitly rather than guessing. For any
window from the first heartbeat row onward, both are reported and the
distinction is real.

Usage:
    python3 harness/scripts/report_polymarket_coverage.py
        [--pit-db PATH] [--cadence-seconds N] [--gap-threshold-hours H]
        [--since ISO] [--until ISO] [--json]
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
_HARNESS_SRC = REPO_ROOT / "harness"
if str(_HARNESS_SRC) not in sys.path:
    sys.path.insert(0, str(_HARNESS_SRC))

from castellan.coverage import compute_polymarket_coverage  # noqa: E402


def _fmt_hours(h: float) -> str:
    return f"{h:.1f}h"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pit-db", default=str(REPO_ROOT / "book" / "pit.db"))
    ap.add_argument("--source", default="polymarket-clob",
                     help="observations source recording successful rounds")
    ap.add_argument("--cadence-seconds", type=int, default=900,
                     help="declared poll cadence (default: 900s = 15 min, "
                          "matching capital.castellan.polymarket-book.plist)")
    ap.add_argument("--gap-threshold-hours", type=float, default=1.0,
                     help="gaps at or above this are individually listed")
    ap.add_argument("--since", default=None, help="ISO-8601, restrict window start")
    ap.add_argument("--until", default=None, help="ISO-8601, restrict window end")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args(argv)

    if not Path(args.pit_db).exists():
        print(f"no store at {args.pit_db} -- nothing to report", file=sys.stderr)
        return 1

    conn = sqlite3.connect(args.pit_db)
    try:
        report = compute_polymarket_coverage(
            conn, source=args.source, cadence_seconds=args.cadence_seconds,
            gap_threshold_hours=args.gap_threshold_hours,
            since=args.since, until=args.until,
        )
    finally:
        conn.close()

    if args.json:
        print(json.dumps(report, indent=2, default=str))
        return 0

    if report["n_success"] == 0:
        print(f"no successful '{args.source}' rounds recorded in {args.pit_db} "
              f"for the requested window -- nothing to report")
        return 0

    print(f"Polymarket capture coverage -- {args.pit_db} (source={args.source})")
    print(f"  window:            {report['first_success']}  ->  {report['last_success']}")
    print(f"  span:              {_fmt_hours(report['span_hours'])}")
    print(f"  cadence:           {args.cadence_seconds}s")
    print(f"  expected polls:    {report['expected_polls']:.1f}")
    print(f"  successful polls:  {report['n_success']}  (method 1: distinct knowledge_time)")
    print(f"  coverage:          {report['coverage_pct']:.2f}%")
    print()
    print(f"  gaps >= {_fmt_hours(args.gap_threshold_hours)}: {len(report['gaps'])}")
    for g in report["gaps"]:
        print(f"    {_fmt_hours(g['hours']):>8}  {g['start']}  ->  {g['end']}")

    print()
    if report["heartbeat_epoch"] is None:
        print("  heartbeat mechanism: no heartbeat rows found in this store yet.")
        print("  -> 'not polled' vs 'polled and the whole batch failed' is NOT")
        print("     distinguishable anywhere in this window (DATA-INFRA-002 §2).")
        print("     It will become distinguishable from the first poll run after")
        print("     this mechanism is deployed.")
    else:
        print(f"  heartbeat mechanism: active since {report['heartbeat_epoch']}")
        print(f"    attempts recorded:  {report['n_heartbeats']}")
        print(f"    of which failed:    {report['n_heartbeats_failed']}")
        if report["n_heartbeats_failed"]:
            print("    (a failed attempt IS distinguishable here from a missed one --")
            print("     see the heartbeat documents directly for error detail.)")
        pre = report["pre_heartbeat_span_hours"]
        if pre and pre > 0:
            print(f"    NOTE: {_fmt_hours(pre)} of the window above predates the first")
            print("    heartbeat row -- the not-polled/failed distinction does not apply there.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
