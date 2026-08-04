#!/usr/bin/env python3
"""Merge a pulled-down VPS Polymarket capture store into `book/pit.db` --
DATA-INFRA-002 §1.

This is the ONLY sanctioned path a satellite capture's data takes into
the firm's real store (see `castellan.capture_merge` for the full
argument). The VPS itself never touches `book/pit.db`; it writes to its
own capture-only PITStore file, which is pulled to wherever this repo
lives (rsync/scp over SSH -- a [PRINCIPAL] step, see the cutover
runbook) and replayed here.

Idempotent: safe to re-run over an overlapping or already-merged window.
A small watermark state file (`--state`, default
`book/polymarket_merge_state.json`) makes repeat runs fast by skipping
already-merged rounds, but is a performance optimization only -- deleting
it and re-running from scratch produces the same end state, just slower.

Usage:
    python3 harness/scripts/merge_polymarket_capture.py \\
        --capture-db /path/to/pulled/pit_capture.db
        [--pit-db PATH] [--registry-db PATH] [--state PATH]
        [--reset-watermark] [--dry-run]
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
_HARNESS_SRC = REPO_ROOT / "harness"
if str(_HARNESS_SRC) not in sys.path:
    sys.path.insert(0, str(_HARNESS_SRC))

from castellan import PITStore, TrialRegistry  # noqa: E402
from castellan.capture_merge import merge_capture_store, MERGE_SOURCES  # noqa: E402


def _load_watermark(state_path: Path) -> float:
    if not state_path.exists():
        return 0.0
    with open(state_path) as f:
        return float(json.load(f).get("watermark", 0.0))


def _save_watermark(state_path: Path, watermark: float) -> None:
    tmp = state_path.with_suffix(state_path.suffix + ".tmp")
    with open(tmp, "w") as f:
        json.dump({"watermark": watermark, "last_merged_utc": time.time()}, f, indent=2)
    tmp.replace(state_path)  # atomic on POSIX


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--capture-db", required=True,
                     help="path to the pulled-down VPS capture-only PITStore file")
    ap.add_argument("--pit-db", default=str(REPO_ROOT / "book" / "pit.db"),
                     help="the real firm store (default: book/pit.db)")
    ap.add_argument("--registry-db", default=str(REPO_ROOT / "book" / "registry.db"),
                     help="the real TrialRegistry -- restatement events log here for real")
    ap.add_argument("--state", default=str(REPO_ROOT / "book" / "polymarket_merge_state.json"),
                     help="watermark state file (performance only, not correctness)")
    ap.add_argument("--reset-watermark", action="store_true",
                     help="ignore the persisted watermark and re-merge from the beginning "
                          "(safe -- idempotent at the target -- just slower)")
    ap.add_argument("--dry-run", action="store_true",
                     help="report how many rounds/documents are pending merge; write nothing")
    args = ap.parse_args(argv)

    capture_path = Path(args.capture_db)
    if not capture_path.exists():
        print(f"no capture store at {capture_path} -- did the pull step run?", file=sys.stderr)
        return 1

    state_path = Path(args.state)
    watermark = 0.0 if args.reset_watermark else _load_watermark(state_path)

    source_conn = sqlite3.connect(f"file:{capture_path}?mode=ro", uri=True)
    try:
        if args.dry_run:
            placeholders = ",".join("?" * len(MERGE_SOURCES))
            n_obs = source_conn.execute(
                f"SELECT COUNT(DISTINCT knowledge_time) FROM observations "
                f"WHERE source IN ({placeholders}) AND knowledge_time > ?",
                (*MERGE_SOURCES, watermark),
            ).fetchone()[0]
            n_docs = source_conn.execute(
                f"SELECT COUNT(*) FROM documents "
                f"WHERE source IN ({placeholders}) AND knowledge_time > ?",
                (*MERGE_SOURCES, watermark),
            ).fetchone()[0]
            print(f"dry run: {n_obs} round(s), {n_docs} document(s) pending merge "
                  f"(watermark={watermark})")
            return 0

        registry = TrialRegistry(args.registry_db)
        target = PITStore(args.pit_db, registry)
        try:
            result = merge_capture_store(source_conn, target, watermark=watermark)
        finally:
            target.close()
    finally:
        source_conn.close()

    print(f"merged {result['rounds_merged']} round(s): "
          f"{result['observations_new']} new obs, "
          f"{result['observations_unchanged']} unchanged, "
          f"{result['observations_restated']} RESTATED")
    print(f"documents: {result['documents_merged']}/{result['documents_seen']} inserted "
          f"(rest already present, ref-deduplicated)")

    if result["observations_restated"]:
        print(
            f"\n*** {result['observations_restated']} restatement(s) logged to "
            f"{args.registry_db} under source='polymarket-clob' -- this is unexpected "
            "for this source (see castellan.capture_merge docstring). STOP and escalate "
            "to Validation this session with a blast-radius note per the Charter.",
            file=sys.stderr,
        )

    _save_watermark(state_path, result["new_watermark"])
    print(f"watermark advanced to {result['new_watermark']}")
    return 0 if not result["observations_restated"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
