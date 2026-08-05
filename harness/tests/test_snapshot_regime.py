"""
Tests for the DATA-INFRA-003 snapshot regime (`harness/scripts/snapshot_book.py`,
`harness/scripts/check_snapshot_health.py`). New file, per S2-D-016 Rider B's
constraint against modifying test files outside a clearly-named new one.

These import the scripts as modules (both live under harness/scripts/, not
harness/castellan/, and touch no file this dispatch was told not to touch).
"""

from __future__ import annotations

import gzip
import importlib.util
import json
import shutil
import sqlite3
import sys
import time
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"


def _load(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS_DIR / filename)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


snap = _load("snapshot_book", "snapshot_book.py")
health = _load("check_snapshot_health", "check_snapshot_health.py")


def _make_book_dir(tmp_path: Path, n_obs: int = 5, n_docs: int = 2) -> Path:
    book_dir = tmp_path / "book"
    book_dir.mkdir()

    pit = sqlite3.connect(book_dir / "pit.db")
    pit.execute("""CREATE TABLE observations (
        obs_id INTEGER PRIMARY KEY AUTOINCREMENT, source TEXT, symbol TEXT,
        field TEXT, event_time TEXT, knowledge_time REAL, value REAL)""")
    pit.execute("""CREATE TABLE documents (
        doc_id INTEGER PRIMARY KEY AUTOINCREMENT, source TEXT, symbol TEXT,
        doc_type TEXT, event_time TEXT, knowledge_time REAL, ref TEXT, meta_json TEXT)""")
    for i in range(n_obs):
        pit.execute("INSERT INTO observations (source, symbol, field, event_time, knowledge_time, value) "
                    "VALUES ('test','SYM','f','2026-01-01T00:00:00Z', 1.0, 1.0)")
    for i in range(n_docs):
        pit.execute("INSERT INTO documents (source, symbol, doc_type, event_time, knowledge_time, ref, meta_json) "
                    "VALUES ('test','SYM','doc','2026-01-01T00:00:00Z', 1.0, 'ref{}', '{{}}')".format(i))
    pit.commit()
    pit.close()

    registry = sqlite3.connect(book_dir / "registry.db")
    registry.execute("CREATE TABLE hypotheses (id INTEGER PRIMARY KEY)")
    registry.execute("CREATE TABLE trials (id INTEGER PRIMARY KEY)")
    registry.execute("CREATE TABLE events (id INTEGER PRIMARY KEY)")
    registry.commit()
    registry.close()

    book = sqlite3.connect(book_dir / "book.db")
    book.execute("CREATE TABLE orders (id INTEGER PRIMARY KEY)")
    book.execute("CREATE TABLE executions (id INTEGER PRIMARY KEY)")
    book.execute("CREATE TABLE trades (id INTEGER PRIMARY KEY)")
    book.commit()
    book.close()

    return book_dir


# --- core mechanics -----------------------------------------------------

def test_snap_01_fresh_snapshot_succeeds_all_three(tmp_path):
    book_dir = _make_book_dir(tmp_path)
    dest = tmp_path / "snapshots"
    results = [snap.snapshot_one(name, book_dir, dest, retain=7, repo_root=tmp_path) for name in snap.DB_SPECS]
    assert all(r["ok"] for r in results), results
    for name in snap.DB_SPECS:
        assert (dest / f"{name}.status.json").exists()
        status = json.loads((dest / f"{name}.status.json").read_text())
        assert status["ok"] is True
        assert status["last_success"] is not None
        gz_files = list(dest.glob(f"{name}-*.db.gz"))
        assert len(gz_files) == 1


def test_snap_02_restore_verification_actually_opens_the_snapshot(tmp_path):
    """The dispatch's own requirement: a snapshot must be opened and its row
    counts checked, not merely assumed restorable because the write succeeded."""
    book_dir = _make_book_dir(tmp_path, n_obs=11, n_docs=3)
    dest = tmp_path / "snapshots"
    result = snap.snapshot_one("pit", book_dir, dest, retain=7, repo_root=tmp_path)
    assert result["ok"]

    gz_path = dest / result["snapshot_file"]
    with gzip.open(gz_path, "rb") as f_in, open(tmp_path / "restored.db", "wb") as f_out:
        shutil.copyfileobj(f_in, f_out)
    restored_counts = snap.read_counts(tmp_path / "restored.db", ["observations", "documents"])
    assert restored_counts == {"observations": 11, "documents": 3}

    manifest_lines = (dest / "pit.manifest.jsonl").read_text().strip().splitlines()
    entry = json.loads(manifest_lines[-1])
    assert entry["restore_verified"] is True
    assert entry["integrity_check"] == "ok"
    assert entry["backup_counts"] == restored_counts


def test_snap_03_append_only_bracket_violation_is_a_failure_not_a_warning(tmp_path, monkeypatch):
    book_dir = _make_book_dir(tmp_path)
    dest = tmp_path / "snapshots"

    real_read_counts = snap.read_counts
    call_count = {"n": 0}

    def fake_read_counts(path, tables):
        call_count["n"] += 1
        counts = real_read_counts(path, tables)
        # Second call is the "post" live read inside snapshot_one -- force it
        # to report FEWER rows than the "pre" read, which is impossible for
        # an append-only store and must be treated as a hard failure.
        if call_count["n"] == 2:
            return {t: max(0, c - 100) for t, c in counts.items()}
        return counts

    monkeypatch.setattr(snap, "read_counts", fake_read_counts)
    result = snap.snapshot_one("pit", book_dir, dest, retain=7, repo_root=tmp_path)
    assert result["ok"] is False
    assert "bracket" in result["error"]
    assert not list(dest.glob("pit-*.db.gz")), "a bracket-violating backup must not be left on disk"


def test_snap_04_retention_keeps_only_the_newest_n(tmp_path):
    book_dir = _make_book_dir(tmp_path)
    dest = tmp_path / "snapshots"
    for _ in range(5):
        r = snap.snapshot_one("pit", book_dir, dest, retain=3, repo_root=tmp_path)
        assert r["ok"]
        time.sleep(1.05)  # stamps are second-resolution; force distinct filenames
    remaining = sorted(dest.glob("pit-*.db.gz"))
    assert len(remaining) == 3


def test_snap_05_failed_attempt_never_prunes_prior_good_snapshots(tmp_path, monkeypatch):
    book_dir = _make_book_dir(tmp_path)
    dest = tmp_path / "snapshots"
    r1 = snap.snapshot_one("pit", book_dir, dest, retain=7, repo_root=tmp_path)
    assert r1["ok"]
    good_file = dest / r1["snapshot_file"]
    assert good_file.exists()

    def boom(*_a, **_kw):
        raise RuntimeError("simulated integrity failure")

    monkeypatch.setattr(snap, "integrity_check", boom)
    r2 = snap.snapshot_one("pit", book_dir, dest, retain=7, repo_root=tmp_path)
    assert r2["ok"] is False
    assert good_file.exists(), "prior good snapshot must survive a failed subsequent attempt"

    failure_log = tmp_path / "logs" / "capture" / "snapshot-failures.log"
    assert failure_log.exists()
    assert "pit" in failure_log.read_text()

    status = json.loads((dest / "pit.status.json").read_text())
    assert status["ok"] is False
    assert status["last_success"] == r1["ts"], "last_success must be preserved across a failed attempt"


def test_snap_06_missing_source_database_fails_loudly(tmp_path):
    book_dir = tmp_path / "empty_book"
    book_dir.mkdir()
    dest = tmp_path / "snapshots"
    result = snap.snapshot_one("registry", book_dir, dest, retain=7, repo_root=tmp_path)
    assert result["ok"] is False
    assert "missing" in result["error"]
    assert (tmp_path / "logs" / "capture" / "snapshot-failures.log").exists()


def test_snap_07_main_exit_code_reflects_failure_count(tmp_path, monkeypatch):
    book_dir = _make_book_dir(tmp_path)
    dest = tmp_path / "snapshots"
    monkeypatch.chdir(tmp_path)
    rc = snap.main(["--book-dir", str(book_dir), "--dest", str(dest), "--only", "pit", "registry", "book"])
    assert rc == 0


# --- health check --------------------------------------------------------

def test_health_01_never_run_is_critical(tmp_path):
    dest = tmp_path / "snapshots"
    dest.mkdir()
    result = health.check_one(dest, "pit", max_age_hours=30.0)
    assert result["healthy"] is False
    assert result["severity"] == "CRITICAL"


def test_health_02_fresh_success_is_healthy(tmp_path):
    book_dir = _make_book_dir(tmp_path)
    dest = tmp_path / "snapshots"
    r = snap.snapshot_one("pit", book_dir, dest, retain=7, repo_root=tmp_path)
    assert r["ok"]
    result = health.check_one(dest, "pit", max_age_hours=30.0)
    assert result["healthy"] is True


def test_health_03_stale_snapshot_is_flagged(tmp_path):
    dest = tmp_path / "snapshots"
    dest.mkdir()
    old_ts = "2020-01-01T00:00:00Z"
    (dest / "pit.status.json").write_text(json.dumps({
        "ok": True, "last_success": old_ts, "last_attempt": old_ts, "last_error": None,
    }))
    result = health.check_one(dest, "pit", max_age_hours=30.0)
    assert result["healthy"] is False
    assert result["severity"] == "HIGH"
    assert "old" in result["reason"] or "exceeds" in result["reason"]


def test_health_04_recent_failure_flagged_even_if_prior_success_is_fresh(tmp_path):
    dest = tmp_path / "snapshots"
    dest.mkdir()
    from datetime import datetime, timezone
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    (dest / "pit.status.json").write_text(json.dumps({
        "ok": False, "last_success": now_iso, "last_attempt": now_iso,
        "last_error": "simulated failure after an earlier success",
    }))
    result = health.check_one(dest, "pit", max_age_hours=30.0)
    assert result["healthy"] is False
    assert result["severity"] == "HIGH"
    assert "FAILED" in result["reason"]


def test_health_05_main_exit_code_nonzero_on_any_unhealthy_db(tmp_path, monkeypatch):
    dest = tmp_path / "snapshots"
    dest.mkdir()
    rc = health.main(["--dest", str(dest), "--only", "pit"])
    assert rc == 1
