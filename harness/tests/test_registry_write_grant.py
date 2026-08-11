"""Acceptance tests for VALIDATION-SPEC-004 Item 1 (clauses R-1 ... R-18) —
the registry and the vault defend themselves in code. I-095's remedy,
ruled by the Principal at S3-D-009.

Authored by the Head of Quantitative Validation BEFORE implementation.

THE PROPERTY THESE TESTS ARE:

    A handle on the registry is a READ handle until someone says otherwise,
    in a block, with a stated reason, and the saying is itself the first
    row written under it.

Today `harness/castellan/registry.py` L157-162 reads:

    def __init__(self, path: str):
        self.path = path
        self.conn = sqlite3.connect(path)        # read-write. no mode. no uri.
        self.conn.executescript(SCHEMA)          # a write, every construction
        self.conn.commit()                       # a write, every construction
        self._migrate()                          # a write, every construction

Every handle this firm has ever taken on the registry has been a write
handle, and three writes happen before the caller expresses any intention.

WHAT THESE TESTS DO NOT CLAIM, AND SPEC-004 SECTION 4 SAYS IT AT LENGTH:
none of this prevents a seat that decides to write. A seat that can run
python3 can set an environment variable and can open its own connection.
The grant makes writes DELIBERATE, TYPED and ATTRIBUTABLE-BY-DECLARATION.
It does not make them PREVENTED and it authenticates nobody (I-161/I-103).
`test_rwg_16` grades the one property that sees outside the process: a
raw-path write leaves `grant_id IS NULL` and is therefore DETECTED.

SEAT 9 DOES NOT MODIFY ANY TEST IN THIS FILE UNDER ANY CIRCUMSTANCES.
A failure here is escalated to Validation in writing (Ruling 004 section
11's standing term). That term binds the author as hard as the implementer:
if a clause cannot be met as specified, the clause is wrong and I fix it,
in writing, on the record.

RED BY DESIGN.
"""

from __future__ import annotations

import inspect
import os
import sqlite3
import stat

import numpy as np
import pytest

from castellan import TrialRegistry
from castellan import registry as registry_mod


# ---------------------------------------------------------------------------
# helpers — a missing name is a clean FAIL, never a collection ERROR, so the
# red state is legible as "N failed" rather than "N errors".
# ---------------------------------------------------------------------------

def _need(module, name: str):
    obj = getattr(module, name, None)
    assert obj is not None, (
        f"{module.__name__}.{name} does not exist yet — VALIDATION-SPEC-004 "
        "Item 1 is unimplemented. RED BY DESIGN."
    )
    return obj


def _need_method(obj, name: str):
    m = getattr(obj, name, None)
    assert m is not None, (
        f"{type(obj).__name__}.{name}() does not exist yet — "
        "VALIDATION-SPEC-004 Item 1 is unimplemented. RED BY DESIGN."
    )
    return m


def _seeded(tmp_path, name="reg.db") -> str:
    """A registry file that already exists, created the only way today's
    harness can create one. Tests that need a pre-existing store use this
    so they grade R-1/R-4/R-5 rather than R-3."""
    p = str(tmp_path / name)
    TrialRegistry(p).close()
    return p


def _grant(reg, **kw):
    """Open a write grant with SPEC-004 R-9's signature."""
    wg = _need_method(reg, "write_grant")
    kw.setdefault("reason", "LOG_EVENT")
    kw.setdefault("dispatch", "TEST")
    kw.setdefault("token", "test-token")
    return wg(**kw)


HYP = dict(
    statement="s", mechanism="m", falsifier="f", universe="u",
    horizon="h", success_criteria="sc", trial_budget=10,
)


# ---------------------------------------------------------------------------
# R-1 / R-2 / R-3 — the read-only construction
# ---------------------------------------------------------------------------

def test_rwg_01_default_handle_is_read_only(tmp_path):
    """R-1. A default TrialRegistry handle refuses a write at the SQLite
    layer, not merely at the API layer."""
    reg = TrialRegistry(_seeded(tmp_path))
    with pytest.raises(sqlite3.OperationalError, match="readonly"):
        reg.conn.execute("CREATE TABLE rwg01 (x INTEGER)")


def test_rwg_02_construction_creates_no_schema_and_runs_no_migration(tmp_path):
    """R-2. `executescript(SCHEMA)` and `_migrate()` leave `__init__`.

    Schema creation and schema migration are writes, they were always
    writes, and the only thing that made them invisible was that they
    happened before anyone looked. This is the 'sanctioned migrations'
    third of Sprint 2's external-state policy landing here.

    A file that is a valid SQLite database but carries none of the
    registry's tables must NOT acquire them by being opened. Today
    executescript() runs unconditionally and creates all three."""
    path = str(tmp_path / "bare.db")
    raw = sqlite3.connect(path)
    raw.execute("CREATE TABLE placeholder (x INTEGER)")
    raw.commit()
    raw.close()

    reg = TrialRegistry(path)
    tables = {
        r[0] for r in reg.conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
    }
    assert tables == {"placeholder"}, (
        "R-2: construction created schema. Opening a registry is a read; "
        f"creating one is a write and needs a MIGRATION grant. Found {tables}"
    )
    # and the filesystem agrees: nothing was written
    os.chmod(path, stat.S_IRUSR)
    try:
        TrialRegistry(path)
    finally:
        os.chmod(path, stat.S_IRUSR | stat.S_IWUSR)


def test_rwg_03_missing_registry_raises_and_creates_nothing(tmp_path):
    """R-3. A path that does not exist is a typed, loud failure — never a
    silently-created empty registry reading N=0, which is not a
    measurement."""
    err = _need(registry_mod, "RegistryNotInitializedError")
    path = str(tmp_path / "absent.db")
    with pytest.raises(err):
        TrialRegistry(path)
    assert not os.path.exists(path), (
        "R-3: a failed construction must leave no file behind"
    )


# ---------------------------------------------------------------------------
# R-4 / R-5 — the guard, and the backstop underneath it
# ---------------------------------------------------------------------------

def test_rwg_04_log_trial_without_grant_raises_before_any_sql(tmp_path):
    """R-4. Raised at method entry, before any statement executes — so the
    traceback points at the caller's line, and so no partial state exists."""
    err = _need(registry_mod, "RegistryWriteNotGrantedError")
    reg = TrialRegistry(_seeded(tmp_path))
    with pytest.raises(err):
        reg.log_trial("famA", {"p": 1}, np.zeros(64), 252)
    n = reg.conn.execute("SELECT COUNT(*) FROM trials").fetchone()[0]
    assert n == 0


def test_rwg_05_open_hypothesis_and_log_event_without_grant_raise(tmp_path):
    """R-4, the other two write methods."""
    err = _need(registry_mod, "RegistryWriteNotGrantedError")
    reg = TrialRegistry(_seeded(tmp_path))
    with pytest.raises(err):
        reg.open_hypothesis(family="famA", **HYP)
    with pytest.raises(err):
        reg.log_event("anything", "famA", {})


def test_rwg_06_reaching_around_the_api_fails_at_execute_not_at_commit(tmp_path):
    """R-5. The dispatch's fourth settlement question, answered: an existing
    store opened `ro` fails LOUDLY AT EXECUTE, never silently at commit.
    This is the backstop that makes R-4 non-bypassable from inside the
    process — R-4 is a guard the caller can decline to call; R-5 is a
    property of the handle."""
    reg = TrialRegistry(_seeded(tmp_path))
    with pytest.raises(sqlite3.OperationalError, match="readonly"):
        reg.conn.execute(
            "INSERT INTO events (kind, family, detail_json, created_utc) "
            "VALUES ('x', NULL, '{}', 0.0)"
        )


# ---------------------------------------------------------------------------
# R-6 / R-7 / R-8 — the grant is a block, and it closes
# ---------------------------------------------------------------------------

def test_rwg_07_a_grant_admits_its_own_write(tmp_path):
    """R-6. Inside the block the write lands."""
    reg = TrialRegistry(_seeded(tmp_path))
    with _grant(reg, reason="REGISTER_HYPOTHESIS"):
        reg.open_hypothesis(family="famA", **HYP)
    assert reg.hypothesis("famA") is not None


def test_rwg_08_authority_reverts_on_normal_exit(tmp_path):
    """R-6. The block ends, the authority ends."""
    err = _need(registry_mod, "RegistryWriteNotGrantedError")
    reg = TrialRegistry(_seeded(tmp_path))
    with _grant(reg, reason="LOG_EVENT"):
        reg.log_event("inside", None, {})
    with pytest.raises(err):
        reg.log_event("outside", None, {})
    with pytest.raises(sqlite3.OperationalError, match="readonly"):
        reg.conn.execute("CREATE TABLE rwg08 (x INTEGER)")


def test_rwg_09_authority_reverts_and_rolls_back_on_exception(tmp_path):
    """R-6. A process that raises inside a grant does not keep write
    authority, and does not keep the half-written state either."""
    err = _need(registry_mod, "RegistryWriteNotGrantedError")
    reg = TrialRegistry(_seeded(tmp_path))
    before = reg.conn.execute("SELECT COUNT(*) FROM events").fetchone()[0]
    with pytest.raises(ZeroDivisionError):
        with _grant(reg, reason="LOG_EVENT"):
            reg.log_event("doomed", None, {})
            1 / 0
    after = reg.conn.execute("SELECT COUNT(*) FROM events").fetchone()[0]
    assert after == before, "R-6: the block's writes roll back on exception"
    with pytest.raises(err):
        reg.log_event("after", None, {})


def test_rwg_10_grants_do_not_nest(tmp_path):
    """R-7. A callee cannot silently widen its caller's authority, and one
    `with` statement is the whole of the write authority in that block."""
    err = _need(registry_mod, "RegistryWriteGrantNestedError")
    reg = TrialRegistry(_seeded(tmp_path))
    with _grant(reg, reason="LOG_EVENT"):
        with pytest.raises(err):
            with _grant(reg, reason="LOG_TRIAL"):
                pass


# ---------------------------------------------------------------------------
# R-9 / R-10 — the token, and the typed reason
# ---------------------------------------------------------------------------

def test_rwg_11_token_comes_from_argument_or_environment(tmp_path, monkeypatch):
    """R-9. Absent both, R-4's error. The env var alone suffices.

    This test does NOT assert the token is secret or verified. It is
    neither. I-161: a seat that can run python3 can set this variable and
    mint its own grant. The token exists to be RECORDED (R-11), not to
    authorize."""
    err = _need(registry_mod, "RegistryWriteNotGrantedError")
    reg = TrialRegistry(_seeded(tmp_path))
    monkeypatch.delenv("CASTELLAN_REGISTRY_WRITE", raising=False)
    wg = _need_method(reg, "write_grant")
    with pytest.raises(err):
        with wg(reason="LOG_EVENT", dispatch="TEST"):
            pass
    monkeypatch.setenv("CASTELLAN_REGISTRY_WRITE", "from-env")
    with wg(reason="LOG_EVENT", dispatch="TEST"):
        reg.log_event("ok", None, {})


def test_rwg_12_a_typed_grant_refuses_a_write_of_another_class(tmp_path):
    """R-10. The one narrowing here that is real without authentication:
    a grant taken to log an event cannot register a hypothesis without a
    second, separately recorded grant naming that."""
    err = _need(registry_mod, "RegistryWriteNotGrantedError")
    reg = TrialRegistry(_seeded(tmp_path))
    with _grant(reg, reason="LOG_EVENT"):
        with pytest.raises(err) as ei:
            reg.open_hypothesis(family="famA", **HYP)
    msg = str(ei.value)
    assert "LOG_EVENT" in msg and "REGISTER_HYPOTHESIS" in msg, (
        "R-10: the refusal names BOTH the grant taken and the grant needed"
    )


def test_rwg_13_out_of_vocabulary_reason_is_malformed(tmp_path):
    """R-10. Extending the vocabulary is a specification act (SPEC-004
    section 9.2). Seat 9 does not add a member to make a script run."""
    err = _need(registry_mod, "RegistryWriteGrantMalformedError")
    reg = TrialRegistry(_seeded(tmp_path))
    wg = _need_method(reg, "write_grant")
    with pytest.raises(err):
        with wg(reason="BECAUSE_I_NEED_TO", dispatch="TEST", token="t"):
            pass


# ---------------------------------------------------------------------------
# R-11 ... R-16 — how the grant appears in the record
# ---------------------------------------------------------------------------

def test_rwg_14_the_grant_row_is_the_first_write_under_its_own_grant(tmp_path):
    """R-12. There is no ordering in which a write precedes the record of
    the authority it was made under."""
    reg = TrialRegistry(_seeded(tmp_path))
    with _grant(reg, reason="LOG_EVENT", dispatch="S3-D-011 row 1"):
        reg.log_event("second", None, {})
    row = reg.conn.execute(
        "SELECT grant_id, reason, dispatch, argv, pid, opened_utc, "
        "closed_utc, writes, outcome FROM write_grants ORDER BY grant_id"
    ).fetchall()
    assert len(row) == 1, "R-11: exactly one grant row"
    g = row[0]
    assert g[1] == "LOG_EVENT"
    assert g[2] == "S3-D-011 row 1"
    assert g[4] == os.getpid()
    assert g[6] is not None, "R-6: a closed grant records closed_utc"
    assert g[8] == "CLEAN"
    ev_grant = reg.conn.execute(
        "SELECT grant_id FROM events WHERE kind='second'"
    ).fetchone()[0]
    assert ev_grant == g[0], "R-14: the write carries its grant_id"


def test_rwg_15_the_chain_verifies_and_an_edit_breaks_it(tmp_path):
    """R-13. What this buys is stated at SPEC-004 section 4.3 and not more:
    it is worth exactly the difficulty of rewriting `book/registry.db`'s git
    history, because that is where the head is externally witnessed."""
    reg = TrialRegistry(_seeded(tmp_path))
    for i in range(3):
        with _grant(reg, reason="LOG_EVENT"):
            reg.log_event(f"e{i}", None, {})
    audit = _need_method(reg, "audit_write_grants")
    assert audit()["chain_intact"] is True
    assert audit()["n_grants"] == 3
    reg.close()
    raw = sqlite3.connect(str(tmp_path / "reg.db"))
    raw.execute("UPDATE write_grants SET dispatch='rewritten' WHERE grant_id=2")
    raw.commit()
    raw.close()
    reg2 = TrialRegistry(str(tmp_path / "reg.db"))
    assert _need_method(reg2, "audit_write_grants")()["chain_intact"] is False


def test_rwg_16_a_raw_path_write_is_an_orphan_and_is_detected(tmp_path):
    """R-14 / R-15. THE ONE PROPERTY THAT SEES OUTSIDE THE PROCESS.

    SPEC-004 section 4.1 path A1: `sqlite3.connect(...)` on a handle the
    harness did not issue. Nothing stops it. It leaves `grant_id IS NULL`,
    because the outside path does not know to set a column it has never
    heard of, and the audit reports it."""
    path = _seeded(tmp_path)
    reg = TrialRegistry(path)
    audit = _need_method(reg, "audit_write_grants")
    assert audit()["orphan_rows"]["events"] == []
    reg.close()
    raw = sqlite3.connect(path)
    raw.execute(
        "INSERT INTO events (kind, family, detail_json, created_utc) "
        "VALUES ('smuggled', NULL, '{}', 1.0)"
    )
    raw.commit()
    raw.close()
    reg2 = TrialRegistry(path)
    orphans = _need_method(reg2, "audit_write_grants")()["orphan_rows"]["events"]
    assert len(orphans) == 1, (
        "R-14: a row written outside the harness carries grant_id IS NULL "
        "and is an orphan"
    )


def test_rwg_17_gate_report_carries_the_audit_and_orphans_void_it(tmp_path):
    """R-15. The teeth. N is the denominator of every Part IV statistic; a
    registry that cannot account for how its rows arrived has not delivered
    an N, it has delivered an integer. The Charter's own rule — an
    unreconstructable N is INSUFFICIENT-DATA, never PASS — arriving through
    a new door.

    The audit fields are on the report WHETHER OR NOT they are zero: a
    control that is only visible when it fires is one nobody can confirm is
    running."""
    from castellan import evaluate_gate1

    path = _seeded(tmp_path)
    reg = TrialRegistry(path)
    rng = np.random.default_rng(7)
    with _grant(reg, reason="REGISTER_HYPOTHESIS"):
        reg.open_hypothesis(family="famA", **HYP)
    with _grant(reg, reason="LOG_TRIAL"):
        for _ in range(4):
            reg.log_trial("famA", {"p": _}, rng.normal(0, 0.01, 1200), 252)

    rep = evaluate_gate1(
        "S", "famA", reg, rng.normal(0.0006, 0.01, 1200), 252,
        backtest_years=4.8,
    )
    for field in ("write_grant_chain_head", "write_grant_orphan_rows",
                  "write_grant_chain_intact"):
        assert hasattr(rep, field), (
            f"R-15: the report must carry {field} even when it is clean"
        )
    assert rep.write_grant_orphan_rows == {"hypotheses": 0, "trials": 0, "events": 0}
    reg.close()

    raw = sqlite3.connect(path)
    raw.execute(
        "INSERT INTO events (kind, family, detail_json, created_utc) "
        "VALUES ('smuggled', 'famA', '{}', 1.0)"
    )
    raw.commit()
    raw.close()

    reg2 = TrialRegistry(path)
    rep2 = evaluate_gate1(
        "S", "famA", reg2, rng.normal(0.0006, 0.01, 1200), 252,
        backtest_years=4.8,
    )
    assert rep2.overall == "INSUFFICIENT-DATA", (
        "R-15: one orphan row makes the OVERALL verdict INSUFFICIENT-DATA — "
        "not a FAIL of one criterion. The provenance of N is what is in "
        "question, not the value of any statistic computed from it."
    )


def test_rwg_18_the_migration_amnesty_is_not_re_issuable(tmp_path):
    """R-16. The amnesty is bounded to rows that already existed, recorded
    in the row that granted it, and cannot be widened later. Otherwise
    'migrate' becomes the reason any orphan is forgiven (I-163)."""
    err = _need(registry_mod, "RegistryWriteGrantMalformedError")
    path = _seeded(tmp_path)
    reg = TrialRegistry(path)
    audit = _need_method(reg, "audit_write_grants")
    wm = audit()["migration_watermark"]
    assert isinstance(wm, dict) and set(wm) == {"hypotheses", "trials", "events"}
    with pytest.raises(err):
        with _grant(reg, reason="MIGRATION"):
            pass


# ---------------------------------------------------------------------------
# R-17 / R-18 — the vault takes the same default, with one layer not two
# ---------------------------------------------------------------------------

def test_rwg_19_vault_file_writes_require_a_grant(tmp_path):
    """R-17. The vault's registry writes are already covered by R-4. Its
    FILE writes are not SQLite and get an explicit guard.

    R-18 / I-160 is disclosed and NOT tested here because it is not
    testable as a prevention: a caller holding a vault object can open
    `vault._payload_path` directly and the guard never runs. The registry's
    control survives reaching around the API (test_rwg_06); the vault's
    does not. That asymmetry is stated in the specification rather than
    papered over with a test that would assert a property the design does
    not have."""
    from castellan import holdout as holdout_mod
    err = _need(holdout_mod, "VaultWriteNotGrantedError")
    assert inspect.isclass(err)
    seal = getattr(holdout_mod.HoldoutVault, "seal", None)
    assert seal is not None
    src = inspect.getsource(seal)
    assert "_require_grant" in src or "VaultWriteNotGranted" in src, (
        "R-17: HoldoutVault.seal() must begin with the grant guard"
    )
