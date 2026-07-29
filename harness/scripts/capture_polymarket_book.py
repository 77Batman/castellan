#!/usr/bin/env python3
"""Recurring capture of live Polymarket order-book snapshots into
``book/pit.db``.

Firm data infrastructure (DATA-INFRA-001, Principal direction D-011 §4)
-- NOT scoped to any hypothesis family. Historical Polymarket order-book
depth is unavailable and structurally unreconstructible on-chain
(``research/DATA-PROBE-001-polymarket-orderbook.md``). The only remedy is
prospective accumulation: run this, starting now, so that a future
family has depth history to measure T2/T4/quote-liveness against instead
of nothing.

This script performs exactly ONE poll per invocation and exits.
Recurrence is the caller's responsibility -- nothing here schedules
itself, and nothing in this session installed a cron job or scheduled
task (Principal has not authorised one; see the deliverable doc for the
recommended cadence as a documented, not-yet-installed, invocation line).

Usage:
    python3 harness/scripts/capture_polymarket_book.py [options]

Recommended recurring invocation (documented here for the Principal/CIO
to install explicitly -- NOT run or installed by this script or session):

    */15 * * * *  cd /path/to/castellan-capital && \\
        python3 harness/scripts/capture_polymarket_book.py \\
        >> logs/polymarket_capture.log 2>&1

See research/DATA-INFRA-001-polymarket-book-capture.md for the cadence
rationale, storage projection, and market-selection rule.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
_HARNESS_SRC = REPO_ROOT / "harness"
if str(_HARNESS_SRC) not in sys.path:
    # Works whether or not `pip install -e harness` has been run in the
    # current environment -- this script must be runnable by cron with no
    # guarantee of an activated venv.
    sys.path.insert(0, str(_HARNESS_SRC))

from castellan import PITStore, TrialRegistry  # noqa: E402
from castellan.loaders import ingest_polymarket_books, refresh_universe  # noqa: E402


def _utc_now_str() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pit-db", default=str(REPO_ROOT / "book" / "pit.db"),
                     help="PITStore path (default: book/pit.db, the real firm store)")
    ap.add_argument("--registry-db", default=str(REPO_ROOT / "book" / "registry.db"),
                     help="TrialRegistry path, used only for restatement-incident logging")
    ap.add_argument("--state", default=str(REPO_ROOT / "book" / "polymarket_universe.json"),
                     help="persisted market-universe tracking state")
    ap.add_argument("--depth", type=int, default=10,
                     help="book levels retained per side as scalar (fast-query) fields; "
                          "the full untruncated book is always stored in documents regardless")
    ap.add_argument("--n-liquid", type=int, default=5, help="size of the liquid tier")
    ap.add_argument("--n-thin", type=int, default=5, help="size of the thin tier")
    ap.add_argument("--thin-lo", type=int, default=20, help="thin-tier volume-rank band, lower bound")
    ap.add_argument("--thin-hi", type=int, default=40, help="thin-tier volume-rank band, upper bound")
    ap.add_argument("--dry-run", action="store_true",
                     help="refresh and print the universe; do not fetch books or write to the store")
    args = ap.parse_args(argv)

    state = refresh_universe(
        args.state, n_liquid=args.n_liquid, n_thin=args.n_thin,
        thin_band=(args.thin_lo, args.thin_hi),
    )
    markets = state["markets"]
    active = {cid: m for cid, m in markets.items() if m.get("status") == "active"}
    n_liquid_active = sum(1 for m in active.values() if m["tier"] == "liquid")
    n_thin_active = sum(1 for m in active.values() if m["tier"] == "thin")
    n_resolved = len(markets) - len(active)

    print(f"[{_utc_now_str()}] universe: {len(active)} active "
          f"({n_liquid_active} liquid / {n_thin_active} thin), "
          f"{n_resolved} resolved/retired (tracked, not polled)")

    if args.dry_run:
        for cid, m in sorted(active.items(), key=lambda kv: (-kv[1]["tier"].__eq__("thin"), -kv[1].get("volume24hr", 0))):
            print(f"  [{m['tier']:>6}] {cid[:12]}...  vol24h=${m.get('volume24hr', 0):>12,.0f}  {m['question'][:70]}")
        return 0

    token_meta = {}
    for cid, m in active.items():
        for outcome, tid in m["tokens"].items():
            token_meta[tid] = {
                "condition_id": cid, "question": m["question"],
                "slug": m.get("slug"), "outcome": outcome,
            }

    if not token_meta:
        print(f"[{_utc_now_str()}] no active tokens to capture -- exiting")
        return 0

    registry = TrialRegistry(args.registry_db)
    store = PITStore(args.pit_db, registry)
    result = ingest_polymarket_books(store, token_meta, depth=args.depth)
    store.close()

    if not result["ok"]:
        print(f"[{_utc_now_str()}] CAPTURE FAILED (all retries exhausted): {result['error']}", file=sys.stderr)
        return 1

    msg = (f"[{_utc_now_str()}] captured {len(result['captured'])}/{result['n_requested']} "
           f"token books across {len(active)} markets")
    if result["failed"]:
        msg += f" -- FAILED tokens: {result['failed']}"
    print(msg)
    return 0 if not result["failed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
