#!/usr/bin/env python3
"""
Castellan Capital -- snapshot regime health check. DATA-INFRA-003.

Reads the `<name>.status.json` files `snapshot_book.py` writes and reports,
per database, whether the last snapshot attempt succeeded and how stale the
last KNOWN-GOOD snapshot is. This is the fail-loudly half of the routine: a
snapshot script that only fails loudly to its own stderr is still silent to
everyone who is not tailing that exact log at that exact moment. This script
is designed to be cheap enough (sub-second, no dependencies beyond the
standard library) to run at the start of any working session or as a line
item in an existing daily ritual (Close & Reconcile) -- see
DATA-INFRA-003-snapshot-regime.md §3 for the recommended integration point.

A database is flagged if EITHER:
  (a) the last known-good snapshot is older than --max-age-hours (default 30,
      i.e. tolerant of one missed daily run before flagging, but well inside
      the "surfaces within a week" requirement), or
  (b) the most recent attempt on record failed, even if a good snapshot from
      before that failure still exists within the age window -- a failure
      that is merely "not yet stale" is still a failure and must not read as
      healthy.

Usage:
    python3 harness/scripts/check_snapshot_health.py [--dest book/snapshots]
        [--max-age-hours 30] [--only pit registry book] [--json]

Exit code: 0 if every requested database is healthy. Nonzero otherwise.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import sys
from pathlib import Path

DB_NAMES = ["pit", "registry", "book"]
DEFAULT_MAX_AGE_HOURS = 30.0


def _parse_iso(ts: str) -> _dt.datetime:
    return _dt.datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=_dt.timezone.utc)


def check_one(dest: Path, name: str, max_age_hours: float) -> dict:
    status_path = dest / f"{name}.status.json"
    now = _dt.datetime.now(_dt.timezone.utc)

    if not status_path.exists():
        return {
            "db": name, "healthy": False, "severity": "CRITICAL",
            "reason": f"no status file at {status_path} -- snapshot routine has never run for this database",
        }

    try:
        status = json.loads(status_path.read_text())
    except (json.JSONDecodeError, OSError) as exc:
        return {
            "db": name, "healthy": False, "severity": "CRITICAL",
            "reason": f"status file unreadable: {exc}",
        }

    last_success = status.get("last_success")
    last_attempt = status.get("last_attempt")
    last_attempt_ok = status.get("ok")

    if last_success is None:
        return {
            "db": name, "healthy": False, "severity": "CRITICAL",
            "reason": "no successful snapshot ever recorded",
            "last_attempt": last_attempt, "last_error": status.get("last_error"),
        }

    age_hours = (now - _parse_iso(last_success)).total_seconds() / 3600.0

    if last_attempt_ok is False:
        return {
            "db": name, "healthy": False, "severity": "HIGH",
            "reason": f"most recent attempt FAILED: {status.get('last_error')}",
            "last_success": last_success, "age_hours": round(age_hours, 2),
            "last_attempt": last_attempt,
        }

    if age_hours > max_age_hours:
        return {
            "db": name, "healthy": False, "severity": "HIGH",
            "reason": f"last known-good snapshot is {age_hours:.1f}h old, exceeds --max-age-hours={max_age_hours}",
            "last_success": last_success, "age_hours": round(age_hours, 2),
        }

    return {
        "db": name, "healthy": True,
        "last_success": last_success, "age_hours": round(age_hours, 2),
        "retained_count": status.get("retained_count"),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dest", default=Path("book/snapshots"), type=Path)
    parser.add_argument("--max-age-hours", default=DEFAULT_MAX_AGE_HOURS, type=float)
    parser.add_argument("--only", nargs="+", choices=DB_NAMES, default=DB_NAMES)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    results = [check_one(args.dest, name, args.max_age_hours) for name in args.only]
    overall_ok = all(r["healthy"] for r in results)

    if args.json:
        print(json.dumps({"ok": overall_ok, "checks": results}, indent=2, sort_keys=True))
    else:
        for r in results:
            if r["healthy"]:
                print(f"  {r['db']:9s} OK    last good {r['age_hours']:.1f}h ago, {r.get('retained_count')} retained")
            else:
                print(f"  {r['db']:9s} {r['severity']:8s} {r['reason']}", file=sys.stderr)
        print("OK" if overall_ok else "PROBLEM -- see above", file=sys.stderr if not overall_ok else sys.stdout)

    return 0 if overall_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
