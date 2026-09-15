"""Item 6's script, verified end-to-end on a THROWAWAY registry (I-311 method).

The Principal's ruling of 2026-09-14: "a hand-typed Python session at the vault
is not an acceptable procedure for the firm's most irreversible act." This tests
the script that replaces it.

What is asserted here that matters at the vault door:

  1. The four specs are PARSED out of PREREG-002 §21, not retyped -- so the
     sealed spec cannot drift from the document that freezes.
  2. The ordering control holds: the script refuses when item 7 has not run,
     when the newest grant is still OPEN (grants do not nest -- R-7/I-311), and
     when four VAULT_SEAL rows already exist.
  3. The cutoff must EQUAL the registered forward_window_start -- C8's same-day
     requirement, enforced rather than trusted.
  4. A real four-vault seal against a throwaway registry produces EIGHT
     VAULT_SEAL/CLEAN grants -- two per seal(), measured, I-367 -- four
     ingest_ceiling rows and four spec.json files.

Nothing here touches book/registry.db or book/pit.db.
"""

from __future__ import annotations

import importlib.util
import sqlite3
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
VAULT_SCRIPT = REPO / "harness" / "scripts" / "execute_vault_seals_prereg002.py"
SEAL_SCRIPT = REPO / "harness" / "scripts" / "execute_seal_prereg002.py"
FAMILY = "funding-carry-conditioning-002"


def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def vault_mod():
    return _load(VAULT_SCRIPT, "execute_vault_seals_prereg002")


def test_four_specs_parse_from_the_document(vault_mod):
    specs = vault_mod.extract_vault_specs()
    assert len(specs) == 4
    pairs = [(s["seal"]["source"], s["seal"]["dataset_id"]) for s in specs]
    assert pairs == vault_mod.EXPECTED_PAIRS


def test_every_parsed_spec_carries_the_literal_schema_keys(vault_mod):
    """I-326's seal-time condition: without these, _schema_matches passes blind."""
    for s in vault_mod.extract_vault_specs():
        fp = s["seal"]["schema_fingerprint"]
        assert "columns" in fp and "dtypes" in fp
        assert set(fp["dtypes"].values()) == {"float64"}
        assert fp["columns"] == sorted(fp["columns"]), "pivot-table order is alphabetical"


def test_runtime_values_are_never_taken_from_the_document(vault_mod):
    """cutoff and passphrase are the two values the document does not supply."""
    for s in vault_mod.extract_vault_specs():
        assert "cutoff" not in s["seal"]
        assert "passphrase" not in s["seal"]


def test_instrument_identity_is_narrowed_to_one_pair_per_vault(vault_mod):
    """R-011/I-341: the prior single string named all four symbols at once."""
    for s in vault_mod.extract_vault_specs():
        ident = s["seal"]["instrument_identity"]
        others = [d for _, d in vault_mod.EXPECTED_PAIRS if d != s["seal"]["dataset_id"]]
        # The vault's own dataset_id must appear; no OTHER pair's may.
        assert s["seal"]["dataset_id"] in ident
        for o in others:
            if s["seal"]["dataset_id"].startswith(o):
                continue  # "BTC/USDT" is a prefix of "BTC/USDT:USDT"
            assert o not in ident, f"{ident!r} also names {o}"


# ---------------------------------------------------------------------------
# End-to-end on a throwaway registry.
# ---------------------------------------------------------------------------


@pytest.fixture
def throwaway(tmp_path, vault_mod, monkeypatch):
    """A registry with the family registered exactly as item 7 leaves it."""
    sys.path.insert(0, str(REPO / "harness"))
    from castellan.registry import TrialRegistry
    from castellan.data import PITStore

    reg_path = tmp_path / "registry.db"
    pit_path = tmp_path / "pit.db"

    seal_mod = _load(SEAL_SCRIPT, "execute_seal_prereg002_for_test")
    fields = seal_mod.gather()
    cutoff = "2026-09-14"
    fields["forward_window_start"] = cutoff

    reg = TrialRegistry(str(reg_path), allow_create=True)
    with reg.write_grant(reason="REGISTER_HYPOTHESIS", dispatch="throwaway",
                         token="test-token") as granted:
        granted.open_hypothesis(**fields)
    PITStore(str(pit_path), registry=reg)  # materialise schema

    monkeypatch.setattr(vault_mod, "REPO", tmp_path)
    monkeypatch.setattr(vault_mod, "REGISTRY", reg_path)
    monkeypatch.setattr(vault_mod, "PIT", pit_path)
    return {"tmp": tmp_path, "registry": reg_path, "pit": pit_path, "cutoff": cutoff}


def test_refuses_when_cutoff_does_not_equal_registered_forward_window_start(
    throwaway, vault_mod
):
    """C8's same-UTC-day requirement, enforced."""
    with pytest.raises(SystemExit) as e:
        vault_mod.verify_item_7_completed("2026-09-15")
    assert "forward_window_start" in str(e.value)


def test_accepts_when_item_7_completed_and_closed(throwaway, vault_mod):
    vault_mod.verify_item_7_completed(throwaway["cutoff"])


def test_refuses_when_the_newest_grant_is_still_open(throwaway, vault_mod):
    """Grants do not nest: a seal inside an open grant rolls the registration back."""
    c = sqlite3.connect(throwaway["registry"])
    c.execute("update write_grants set closed_utc = NULL "
              "where grant_id = (select max(grant_id) from write_grants)")
    c.commit()
    c.close()
    with pytest.raises(SystemExit) as e:
        vault_mod.verify_item_7_completed(throwaway["cutoff"])
    assert "OPEN" in str(e.value)


def test_full_four_vault_seal_end_to_end(throwaway, vault_mod, monkeypatch, capsys):
    monkeypatch.setattr(vault_mod.getpass, "getpass", lambda prompt="": "throwaway-pass")
    monkeypatch.setattr(sys, "argv", ["x", "--cutoff", throwaway["cutoff"]])

    assert vault_mod.main() == 0

    c = sqlite3.connect(throwaway["registry"])
    n_vault = c.execute("select count(*) from write_grants where reason='VAULT_SEAL' "
                        "and outcome='CLEAN'").fetchone()[0]
    assert n_vault == 8  # TWO grants per seal() -- measured, I-367

    # I-311: every VAULT_SEAL grant must sit AFTER the registration grant.
    reg_id = c.execute("select grant_id from write_grants "
                       "where reason='REGISTER_HYPOTHESIS'").fetchone()[0]
    vault_ids = [r[0] for r in c.execute(
        "select grant_id from write_grants where reason='VAULT_SEAL'")]
    assert all(v > reg_id for v in vault_ids)
    # And the registration survived -- a nested grant would have rolled it back.
    assert c.execute("select count(*) from hypotheses where family=?",
                     (FAMILY,)).fetchone()[0] == 1
    c.close()

    p = sqlite3.connect(throwaway["pit"])
    ceilings = p.execute("select source, dataset_id, cutoff from ingest_ceiling "
                         "order by source, dataset_id").fetchall()
    p.close()
    assert len(ceilings) == 4
    assert [(s, d) for s, d, _ in ceilings] == sorted(vault_mod.EXPECTED_PAIRS)
    # seal() NORMALISES the cutoff to a full UTC datetime; the ceiling read-back
    # shows "2026-09-14T00:00:00+00:00", not the bare date passed in. Asserted
    # so the Principal does not read the widened form as a mismatch at the door.
    assert all(str(cut).startswith(throwaway["cutoff"]) for _, _, cut in ceilings)
    assert {str(cut) for _, _, cut in ceilings} == {throwaway["cutoff"] + "T00:00:00+00:00"}

    assert len(list((throwaway["tmp"] / "book" / "vaults").glob("*/spec.json"))) == 4
    assert "ITEM 6 COMPLETE" in capsys.readouterr().out


def test_refuses_a_second_run_after_four_seals(throwaway, vault_mod, monkeypatch):
    monkeypatch.setattr(vault_mod.getpass, "getpass", lambda prompt="": "throwaway-pass")
    monkeypatch.setattr(sys, "argv", ["x", "--cutoff", throwaway["cutoff"]])
    assert vault_mod.main() == 0
    with pytest.raises(SystemExit) as e:
        vault_mod.verify_item_7_completed(throwaway["cutoff"])
    assert "already exist" in str(e.value)


# ---------------------------------------------------------------------------
# I-368 -- the read-back path, which had no test until it crashed live.
# ---------------------------------------------------------------------------


def test_hypotheses_has_no_prereg_sha256_column(throwaway):
    """The premise of I-368, asserted so it cannot be quietly reintroduced."""
    c = sqlite3.connect(throwaway["registry"])
    cols = [r[1] for r in c.execute("pragma table_info(hypotheses)")]
    c.close()
    assert "prereg_sha256" not in cols, (
        "If this column now exists the read-back may be simplified -- but it did "
        "not exist when the firm's most irreversible act first ran."
    )


def test_read_prereg_sha256_returns_the_sealed_hash(throwaway, vault_mod):
    """The evidence path of the seal. It must return a 64-hex digest, not None."""
    seal_mod = _load(SEAL_SCRIPT, "execute_seal_prereg002_readback")
    c = sqlite3.connect(throwaway["registry"])
    from_vault = vault_mod.read_prereg_sha256(c)
    from_seal = seal_mod.read_prereg_sha256(c)
    c.close()
    assert from_vault == from_seal, "the two scripts must agree on the sealed hash"
    assert isinstance(from_vault, str) and len(from_vault) == 64
    assert all(ch in "0123456789abcdef" for ch in from_vault)


def test_read_prereg_sha256_matches_the_event_payload(throwaway, vault_mod):
    """Cross-checked against the raw event, parsed independently."""
    import json as _json

    c = sqlite3.connect(throwaway["registry"])
    raw = c.execute(
        "select detail_json from events where kind='hypothesis_sealed' "
        "order by event_id desc limit 1"
    ).fetchone()[0]
    expected = _json.loads(raw)["prereg_sha256"]
    got = vault_mod.read_prereg_sha256(c)
    c.close()
    assert got == expected


def test_read_prereg_sha256_returns_none_rather_than_raising_when_absent(
    throwaway, vault_mod
):
    """A missing event must degrade to None, never crash the read-back again."""
    c = sqlite3.connect(throwaway["registry"])
    c.execute("delete from events where kind='hypothesis_sealed'")
    c.commit()
    assert vault_mod.read_prereg_sha256(c) is None
    c.close()


def test_every_column_the_script_queries_exists(throwaway, vault_mod):
    """I-368's general form: no query may name a column that does not exist."""
    c = sqlite3.connect(throwaway["registry"])
    p = sqlite3.connect(throwaway["pit"])
    have = {
        ("registry", "hypotheses"): {r[1] for r in c.execute("pragma table_info(hypotheses)")},
        ("registry", "write_grants"): {r[1] for r in c.execute("pragma table_info(write_grants)")},
        ("registry", "events"): {r[1] for r in c.execute("pragma table_info(events)")},
        ("pit", "ingest_ceiling"): {r[1] for r in p.execute("pragma table_info(ingest_ceiling)")},
    }
    c.close()
    p.close()
    required = {
        ("registry", "hypotheses"): {"family", "forward_window_start"},
        ("registry", "write_grants"): {"grant_id", "reason", "outcome", "closed_utc", "dispatch"},
        ("registry", "events"): {"kind", "family", "detail_json", "event_id"},
        ("pit", "ingest_ceiling"): {"source", "dataset_id", "cutoff"},
    }
    for key, cols in required.items():
        missing = cols - have[key]
        assert not missing, f"{key} is missing {missing}"
