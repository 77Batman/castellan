"""Merge a satellite (VPS) capture-only PITStore into the firm's real
``book/pit.db`` -- DATA-INFRA-002 §1 (the dual-writer decision).

**The decision.** The VPS never writes to the firm's real `book/pit.db`
directly, and is never made authoritative for the whole store. It owns a
small, capture-only PITStore of its own (same schema, via the same
`castellan.data.PITStore`, just a different file, holding only
`source='polymarket-clob'` observations/documents and
`source='polymarket-capture-meta'` heartbeats). That file is pulled to
wherever the real repo lives (rsync/scp over SSH -- the Principal's
machine, or a Data & Infra working session) and replayed into
`book/pit.db` through this module, which is the ONLY sanctioned path a
satellite capture's data takes into the book of record.

**Why replay through `PITStore.ingest`/`ingest_documents` rather than a
file-level copy.** A raw file copy or `sqlite3 .dump`/`ATTACH`-and-`INSERT
... SELECT` would bypass every one of `PITStore`'s own guarantees:
holdout-ceiling enforcement (a no-op here today, since no hypothesis
family currently depends on this source, but not forever), and --
critically for A4 -- **restatement detection**. Replaying through
`ingest()` means a value that differs from what the target already holds
at the same `(source, symbol, field, event_time)` is caught by the exact
same code path that catches a yfinance re-adjustment, and logged to the
real `TrialRegistry` as a `data_restatement` event, escalable to
Validation the same way any other restatement is (Charter, Seat 9).

**Why this is expected to almost never fire for this source, and why the
detector stays on anyway.** Polymarket `event_time` is the venue's own
millisecond snapshot timestamp -- for any two poll rounds (laptop or
VPS) to collide on `(symbol, field, event_time)`, the same instant would
need to have produced two different in-store values, which should not
happen absent a genuine bug (e.g. a merge replayed twice with a clock
skew that altered a knowledge_time comparison, or two pollers somehow
both winning a request against the identical venue snapshot with a
transcription error). A restatement event on `source='polymarket-clob'`
is therefore a genuine anomaly worth investigating immediately, not
routine vendor noise the way a yfinance restatement is -- this module
does not special-case that; it reports it exactly like any other.

**Idempotency.** Every unit replayed here is already dedup-safe at the
target: `ingest()` skips unchanged (symbol, field, event_time) rows, and
`ingest_documents()` dedupes on `ref`. Running this merge twice over the
same window, or over a window that overlaps a previous run, is always
safe -- it produces `unchanged` counts, not duplicates or errors. The
watermark (`--since-knowledge-time`, persisted to a small state file by
the calling script) is purely a performance optimization, not a
correctness requirement.
"""

from __future__ import annotations

import json
import sqlite3

import pandas as pd

from .data import PITStore

MERGE_SOURCES = ("polymarket-clob", "polymarket-capture-meta")


def merge_capture_store(
    source_conn: sqlite3.Connection,
    target: PITStore,
    watermark: float = 0.0,
    sources: tuple[str, ...] = MERGE_SOURCES,
) -> dict:
    """Replay every observation/document with `knowledge_time > watermark`
    from `source_conn` (a satellite capture PITStore, read-only for this
    call) into `target` (the real `book/pit.db`, opened with the real
    `TrialRegistry` so restatement detection is live).

    Returns counts and the new watermark (`max(knowledge_time)` seen this
    run, or the input `watermark` unchanged if nothing new was found).
    """
    placeholders = ",".join("?" * len(sources))
    obs_rows = source_conn.execute(
        f"SELECT source, symbol, knowledge_time, field, event_time, value "
        f"FROM observations WHERE source IN ({placeholders}) AND knowledge_time > ? "
        f"ORDER BY knowledge_time, symbol",
        (*sources, watermark),
    ).fetchall()

    doc_rows = source_conn.execute(
        f"SELECT source, symbol, doc_type, event_time, knowledge_time, ref, meta_json "
        f"FROM documents WHERE source IN ({placeholders}) AND knowledge_time > ? "
        f"ORDER BY knowledge_time",
        (*sources, watermark),
    ).fetchall()

    new_obs = unchanged_obs = restated_obs = 0
    rounds_merged = 0
    seen_watermark = watermark

    # Group observation rows into (source, symbol, knowledge_time) rounds
    # -- exactly the unit `ingest_polymarket_books` originally wrote them
    # in, so replay preserves the original round structure rather than
    # re-splitting it.
    groups: dict[tuple[str, str, float], list[tuple[str, str, float]]] = {}
    for src, symbol, kt, field, event_time, value in obs_rows:
        groups.setdefault((src, symbol, kt), []).append((field, event_time, value))
        seen_watermark = max(seen_watermark, kt)

    for (src, symbol, kt), fields in groups.items():
        # All fields in one round share one event_time in this source's
        # writer (one snapshot per token per poll) -- but build a wide
        # frame generically rather than assuming exactly one row, so this
        # stays correct if that ever changes.
        by_event_time: dict[str, dict] = {}
        for field, event_time, value in fields:
            by_event_time.setdefault(event_time, {})[field] = value
        idx = pd.DatetimeIndex([pd.Timestamp(et) for et in by_event_time])
        df = pd.DataFrame(list(by_event_time.values()), index=idx)
        result = target.ingest(src, symbol, df, knowledge_time=kt)
        new_obs += result["new"]
        unchanged_obs += result["unchanged"]
        restated_obs += result["restated"]
        rounds_merged += 1

    documents_merged = 0
    for src, symbol, doc_type, event_time, kt, ref, meta_json in doc_rows:
        n = target.ingest_documents(src, symbol, [{
            "doc_type": doc_type,
            "event_time": event_time,
            "knowledge_time": kt,
            "ref": ref,
            "meta": json.loads(meta_json),
        }])
        documents_merged += n
        seen_watermark = max(seen_watermark, kt)

    return {
        "rounds_merged": rounds_merged,
        "observations_new": new_obs,
        "observations_unchanged": unchanged_obs,
        "observations_restated": restated_obs,
        "documents_merged": documents_merged,
        "documents_seen": len(doc_rows),
        "new_watermark": seen_watermark,
    }
