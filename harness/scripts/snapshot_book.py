#!/usr/bin/env python3
"""
Castellan Capital -- scheduled snapshot regime for book/*.db. DATA-INFRA-003
(Sprint 2, S2-D-001 Rider B).

Snapshots `book/pit.db`, `book/registry.db`, and `book/book.db` via SQLite's
online backup API, verifies every snapshot is restorable IN THE SAME
INVOCATION (not a manual afterthought -- see `verify_restore()`), enforces
N-snapshot retention per database, and fails loudly: any failure leaves prior
good snapshots untouched, writes a machine-readable status file per database,
and appends a human-readable line to a durable failure log. See
`check_snapshot_health.py` for the reader half of the fail-loudly contract.

Why the backup API, not `cp` / `shutil.copy`:
    The laptop's Polymarket capture writes to book/pit.db roughly every 15
    minutes and is explicitly NOT stopped for this routine (S2-D-016, "do not
    stop the running laptop capture"). A plain file copy racing a writer's
    transaction can capture a torn, inconsistent page image -- SQLite gives
    no guarantee that a byte-level copy of a live database file is even
    openable. `sqlite3.Connection.backup()` uses SQLite's own online backup
    API: it takes the appropriate read locks and copies a transactionally
    consistent snapshot even against a concurrent writer, retried against
    SQLITE_BUSY. This is the only correctness-preserving way to snapshot a
    database this routine does not have exclusive access to.

Why append-only monotonicity is checked, not just "the copy succeeded":
    Every table this script counts (`observations`, `documents`, `hypotheses`,
    `trials`, `events`, `orders`, `executions`, `trades`) is append-only under
    this firm's harness -- PITStore never deletes, the registry never deletes,
    the paper book never deletes. So for any backup taken between a
    "before" count and an "after" count, the backup's own count MUST fall in
    [before, after]. A backup whose count falls outside that bracket means
    the backup is not a faithful copy of this store at any real instant, and
    is treated as a failure, not a warning.

Usage:
    python3 harness/scripts/snapshot_book.py [--book-dir book] [--dest DEST]
        [--retain N] [--only pit registry book] [--json]

Exit code: 0 if every requested database snapshotted, verified, and pruned
cleanly. Nonzero (count of failed databases) otherwise.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import gzip
import hashlib
import json
import os
import shutil
import sqlite3
import sys
import tempfile
import traceback
from pathlib import Path

DB_SPECS: dict[str, dict] = {
    "pit": {"file": "pit.db", "count_tables": ["observations", "documents"]},
    "registry": {"file": "registry.db", "count_tables": ["hypotheses", "trials", "events"]},
    "book": {"file": "book.db", "count_tables": ["orders", "executions", "trades"]},
}

DEFAULT_RETAIN = 7  # rolling week of daily snapshots -- see DATA-INFRA-003 §2
FAILURE_LOG_REL = "logs/capture/snapshot-failures.log"


def _utc_now_iso() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _utc_now_stamp() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def read_counts(db_path: Path, tables: list[str]) -> dict[str, int]:
    """Read row counts for the given tables. Missing table -> count 0 (does
    not raise), so a database that predates a table (e.g. a fresh test file)
    is measurable rather than crashing the whole routine."""
    counts: dict[str, int] = {}
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    try:
        existing = {
            r[0] for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
        }
        for t in tables:
            if t in existing:
                counts[t] = conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
            else:
                counts[t] = 0
    finally:
        conn.close()
    return counts


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def backup_db(src: Path, dst: Path) -> None:
    """Online backup via the SQLite backup API. Consistent against a
    concurrent writer; never a raw file copy (see module docstring)."""
    src_conn = sqlite3.connect(f"file:{src}?mode=ro", uri=True)
    dst_conn = sqlite3.connect(str(dst))
    try:
        src_conn.backup(dst_conn)
    finally:
        dst_conn.close()
        src_conn.close()


def integrity_check(db_path: Path) -> str:
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    try:
        row = conn.execute("PRAGMA integrity_check").fetchone()
        return row[0] if row else "no result"
    finally:
        conn.close()


def verify_restore(compressed_path: Path, expected_counts: dict[str, int], tables: list[str]) -> tuple[bool, str]:
    """Decompress the snapshot just written, open it, integrity-check it, and
    confirm its row counts equal what was recorded at backup time -- exactly,
    not a bracket, because this is the identical bytes being re-read.
    This is what makes restore-verification part of the routine rather than
    a manual, occasional afterthought (dispatch requirement #2)."""
    with tempfile.TemporaryDirectory() as td:
        restored = Path(td) / "restored.db"
        with gzip.open(compressed_path, "rb") as f_in, open(restored, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)
        ic = integrity_check(restored)
        if ic != "ok":
            return False, f"integrity_check on restored copy: {ic!r}"
        restored_counts = read_counts(restored, tables)
        if restored_counts != expected_counts:
            return False, f"restored counts {restored_counts} != backup-time counts {expected_counts}"
        return True, "ok"


def _append_failure_log(repo_root: Path, name: str, message: str) -> None:
    log_path = repo_root / FAILURE_LOG_REL
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with open(log_path, "a") as f:
        f.write(f"{_utc_now_iso()} SNAPSHOT-FAILURE db={name} {message}\n")


def _read_status(dest: Path, name: str) -> dict:
    p = dest / f"{name}.status.json"
    if p.exists():
        try:
            return json.loads(p.read_text())
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def _write_status(dest: Path, name: str, **fields) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    p = dest / f"{name}.status.json"
    prior = _read_status(dest, name)
    prior.update(fields)
    p.write_text(json.dumps(prior, indent=2, sort_keys=True))


def _append_manifest(dest: Path, name: str, entry: dict) -> None:
    p = dest / f"{name}.manifest.jsonl"
    with open(p, "a") as f:
        f.write(json.dumps(entry, sort_keys=True) + "\n")


def _enforce_retention(dest: Path, name: str, retain: int) -> list[str]:
    snaps = sorted(dest.glob(f"{name}-*.db.gz"))
    removed = []
    if len(snaps) > retain:
        for p in snaps[: len(snaps) - retain]:
            p.unlink()
            removed.append(p.name)
    return removed


def snapshot_one(name: str, book_dir: Path, dest: Path, retain: int, repo_root: Path) -> dict:
    spec = DB_SPECS[name]
    src = book_dir / spec["file"]
    tables = spec["count_tables"]
    result = {"db": name, "ok": False, "ts": _utc_now_iso()}

    if not src.exists():
        msg = f"source database missing: {src}"
        _append_failure_log(repo_root, name, msg)
        _write_status(dest, name, ok=False, last_attempt=result["ts"], last_error=msg)
        result["error"] = msg
        return result

    tmp_backup = None
    try:
        pre_counts = read_counts(src, tables)

        with tempfile.TemporaryDirectory() as td:
            tmp_backup = Path(td) / f"{name}.backup.db"
            backup_db(src, tmp_backup)

            post_counts = read_counts(src, tables)
            backup_counts = read_counts(tmp_backup, tables)

            for t in tables:
                lo, hi, mid = pre_counts[t], post_counts[t], backup_counts[t]
                if not (lo <= mid <= hi):
                    raise RuntimeError(
                        f"append-only bracket violated on {name}.{t}: "
                        f"pre={lo} backup={mid} post={hi} "
                        f"(expected pre <= backup <= post)"
                    )

            ic = integrity_check(tmp_backup)
            if ic != "ok":
                raise RuntimeError(f"integrity_check failed on fresh backup: {ic!r}")

            sha_uncompressed = sha256_file(tmp_backup)

            dest.mkdir(parents=True, exist_ok=True)
            stamp = _utc_now_stamp()
            final_path = dest / f"{name}-{stamp}.db.gz"
            partial_path = dest / f"{name}-{stamp}.db.gz.partial"
            with open(tmp_backup, "rb") as f_in, gzip.open(partial_path, "wb", compresslevel=9) as f_out:
                shutil.copyfileobj(f_in, f_out)
            os.rename(partial_path, final_path)  # atomic: no half-written "real" snapshot ever visible

            verified, verify_msg = verify_restore(final_path, backup_counts, tables)
            if not verified:
                final_path.unlink(missing_ok=True)
                raise RuntimeError(f"restore-verification failed, snapshot discarded: {verify_msg}")

            sha_compressed = sha256_file(final_path)
            uncompressed_size = tmp_backup.stat().st_size
            compressed_size = final_path.stat().st_size

        removed = _enforce_retention(dest, name, retain)

        entry = {
            "db": name,
            "ts": result["ts"],
            "pre_counts": pre_counts,
            "post_counts": post_counts,
            "backup_counts": backup_counts,
            "uncompressed_bytes": uncompressed_size,
            "compressed_bytes": compressed_size,
            "sha256_uncompressed": sha_uncompressed,
            "sha256_compressed": sha_compressed,
            "integrity_check": "ok",
            "restore_verified": True,
            "snapshot_file": final_path.name,
            "pruned": removed,
        }
        _append_manifest(dest, name, entry)
        _write_status(
            dest, name,
            ok=True,
            last_success=result["ts"],
            last_attempt=result["ts"],
            last_error=None,
            last_snapshot_file=final_path.name,
            last_compressed_bytes=compressed_size,
            retained_count=min(retain, len(list(dest.glob(f"{name}-*.db.gz")))),
        )
        result.update(ok=True, snapshot_file=final_path.name, compressed_bytes=compressed_size, pruned=removed)
        return result

    except Exception as exc:  # noqa: BLE001 -- deliberately broad: every failure must surface, not raise past this point
        msg = f"{type(exc).__name__}: {exc}"
        _append_failure_log(repo_root, name, msg)
        _write_status(dest, name, ok=False, last_attempt=result["ts"], last_error=msg)
        result["error"] = msg
        result["traceback"] = traceback.format_exc()
        return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--book-dir", default="book", type=Path)
    parser.add_argument("--dest", default=None, type=Path, help="default: <book-dir>/snapshots")
    parser.add_argument("--retain", default=DEFAULT_RETAIN, type=int)
    parser.add_argument("--only", nargs="+", choices=list(DB_SPECS), default=list(DB_SPECS))
    parser.add_argument("--repo-root", default=Path("."), type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    dest = args.dest if args.dest is not None else (args.book_dir / "snapshots")
    results = [snapshot_one(name, args.book_dir, dest, args.retain, args.repo_root) for name in args.only]

    if args.json:
        print(json.dumps(results, indent=2, sort_keys=True))
    else:
        for r in results:
            if r["ok"]:
                print(f"[{r['ts']}] {r['db']}: OK  -> {r['snapshot_file']} ({r['compressed_bytes']} bytes)"
                      + (f"  pruned {r['pruned']}" if r.get("pruned") else ""))
            else:
                print(f"[{r['ts']}] {r['db']}: FAILED -- {r['error']}", file=sys.stderr)

    return sum(0 if r["ok"] else 1 for r in results)


if __name__ == "__main__":
    raise SystemExit(main())
