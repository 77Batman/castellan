#!/usr/bin/env python3
"""Item 6 of the PREREG-002 seal checklist: the FOUR holdout vault seals.

PRINCIPAL-ONLY. Runs STRICTLY AFTER `execute_seal_prereg002.py --execute` has
returned. It is a separate process on purpose -- see ORDERING below.

Written 2026-09-14 on the Principal's ruling that "a hand-typed Python session at
the vault is not an acceptable procedure for the firm's most irreversible act."

WHY A SCRIPT, AND WHY IT PARSES RATHER THAN RETYPES
---------------------------------------------------
`PREREG-002` §21 already carries the four `HoldoutVault(...).seal(...)` calls in
full, with `instrument_identity` narrowed per vault (R-011) and the three binding
values transcribed from `DATA-IMPL-012` §1, where Seat 9 MEASURED them off
`book/pit.db`. Retyping them here would create a second copy of a hashed spec and
a guaranteed future divergence -- the exact risk `execute_seal_prereg002.py`'s
docstring names for the sixteen fields.

So nothing is typed. The four specs are PARSED out of §21's vault block with
`ast`, after substituting its two deliberate placeholders:

    cutoff=<C = this UTC calendar day>                    -> supplied by --cutoff
    passphrase=<the Principal's, never written to ...>    -> typed at the prompt

Every other argument -- source, dataset_id, instrument_identity, query_semantics,
schema_fingerprint, holdout_end_rule, resolution_source, sealed_by, vault_dir,
name, family -- comes from the document. TEMPLATES.md §7.12 applied to item 6.

ORDERING IS A CONTROL, NOT A PREFERENCE (I-311, I-312)
------------------------------------------------------
`HoldoutVault.seal()` opens its own `write_grant(reason="VAULT_SEAL")`, and grants
do not nest (R-7). A seal called inside the REGISTER_HYPOTHESIS block raises
`RegistryWriteGrantNestedError` AND ROLLS THE REGISTRATION BACK WITH IT.

This script cannot make that mistake, because it runs in a different process from
the registration and opens its own registry handle with no grant held. It
additionally REFUSES unless it can verify, by reading the registry, that item 7
already completed and closed:

    - exactly one hypothesis row for the family
    - the newest write_grant is REGISTER_HYPOTHESIS / CLEAN and is CLOSED
    - the registered forward_window_start equals the --cutoff supplied
    - fewer than four VAULT_SEAL rows already exist (no double-seal)

C8 requires all four seals in the SAME SESSION and the SAME UTC DAY as the
registration. The cutoff equality check is what enforces the second half.

Usage:
    CASTELLAN_REGISTRY_WRITE=S4-D-014-seal \
        python3 harness/scripts/execute_vault_seals_prereg002.py \
            --cutoff YYYY-MM-DD            # verbatim from --execute's "C = ..." line
        [--dry-run]                        # verify + print, seal nothing

`CASTELLAN_REGISTRY_WRITE` PREVENTS accidental and ungranted writes; DETECTS and
ATTRIBUTES deliberate ones through the tamper-evident grant-hash chain; DOES NOT
authenticate anyone. It must never be a secret -- it is stored verbatim in
`write_grants.token` and `book/registry.db` is a tracked, committed file. Use a
dispatch label. (Principal-ruled 2026-09-14; full account in
`execute_seal_prereg002.py`'s docstring.)

EXPECTED READ-BACK IS EIGHT GRANT ROWS, NOT FOUR (I-367)
---------------------------------------------------------
One `seal()` writes TWO `VAULT_SEAL` rows -- `dispatch='HoldoutVault.seal'` (the
vault file write) and `dispatch='HoldoutVault.holdout_spec_sealed'` (the event,
via `_grant_log`, which opens its own grant under the same reason). Four calls
therefore produce eight rows. Four is the count of CALLS. This script computes
all six read-backs and exits non-zero on any mismatch.
"""
from __future__ import annotations

import argparse
import ast
import getpass
import os
import re
import sqlite3
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PREREG = REPO / "research" / "PREREG-002-crypto-funding-basis.md"
REGISTRY = REPO / "book" / "registry.db"
PIT = REPO / "book" / "pit.db"
FAMILY = "funding-carry-conditioning-002"

CUTOFF_PLACEHOLDER = "<C = this UTC calendar day>"
PASSPHRASE_PLACEHOLDER = "<the Principal's, never written to repo, Oracle, or any file>"

EXPECTED_PAIRS = [
    ("binance", "BTC/USDT"),
    ("binance", "ETH/USDT"),
    ("binanceusdm", "BTC/USDT:USDT"),
    ("binanceusdm", "ETH/USDT:USDT"),
]


def extract_vault_specs() -> list[dict]:
    """Parse §21's four HoldoutVault(...).seal(...) calls out of the document.

    Returns one dict per vault carrying the constructor kwargs under 'ctor' and
    the seal kwargs under 'seal'. `cutoff` and `passphrase` are omitted -- they
    are the two runtime values and are never read from the document.
    """
    lines = PREREG.read_text().split("\n")
    start = next(i for i, L in enumerate(lines) if re.match(r"^## 21[.\s]", L))
    fences = [i for i in range(start, len(lines)) if lines[i].strip().startswith("```")]
    block = None
    for a, b in zip(fences[0::2], fences[1::2]):
        candidate = "\n".join(lines[a + 1 : b])
        if "HoldoutVault(" in candidate:
            block = candidate
            break
    if block is None:
        raise SystemExit(
            "§21 carries no fenced block containing `HoldoutVault(` -- refusing "
            "to proceed. The vault specification is the document's, not this "
            "script's, and this script will not invent one."
        )

    # The block is a SPECIFICATION, not source: two arguments are deliberate
    # placeholders. Substitute them for parseable sentinels; every other value
    # is a literal and survives untouched.
    src = block.replace(f"cutoff={CUTOFF_PLACEHOLDER}", "cutoff=None")
    src = src.replace(f"passphrase={PASSPHRASE_PLACEHOLDER}", "passphrase=None")
    # `registry=registry` / `store=pit_store` are free names; ast.parse is fine
    # with them because nothing here is executed.
    try:
        tree = ast.parse(src)
    except SyntaxError as e:
        raise SystemExit(
            f"§21's vault block did not parse ({e}). A placeholder may have been "
            f"reworded. Refusing to guess at the seal arguments."
        )

    specs = []
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)):
            continue
        if node.func.attr != "seal":
            continue
        ctor_call = node.func.value
        if not (isinstance(ctor_call, ast.Call) and getattr(ctor_call.func, "id", "") == "HoldoutVault"):
            continue

        def literals(call):
            out = {}
            for kw in call.keywords:
                try:
                    out[kw.arg] = ast.literal_eval(kw.value)
                except ValueError:
                    out[kw.arg] = f"<non-literal: {ast.unparse(kw.value)}>"
            return out

        seal_kwargs = literals(node)
        seal_kwargs.pop("cutoff", None)      # runtime, from --cutoff
        seal_kwargs.pop("passphrase", None)  # runtime, from the prompt
        specs.append({"ctor": literals(ctor_call), "seal": seal_kwargs})

    if len(specs) != 4:
        raise SystemExit(
            f"Parsed {len(specs)} vault call(s) from §21, expected 4. C8 requires "
            f"FOUR locks (one per (source, dataset_id) pair, exact match, no "
            f"wildcard -- I-327). Refusing to seal a partial set."
        )

    got = [(s["seal"]["source"], s["seal"]["dataset_id"]) for s in specs]
    if got != EXPECTED_PAIRS:
        raise SystemExit(
            f"§21's four pairs are {got}, expected {EXPECTED_PAIRS}. Refusing: a "
            f"dataset_id that does not exactly match the symbol future ingest() "
            f"calls use seals successfully and then never binds (DATA-IMPL-012 §2)."
        )
    for s in specs:
        fp = s["seal"].get("schema_fingerprint")
        if not (isinstance(fp, dict) and "columns" in fp and "dtypes" in fp):
            raise SystemExit(
                f"{s['seal']['dataset_id']}: schema_fingerprint lacks the literal "
                f"'columns'/'dtypes' keys. Without them _schema_matches returns "
                f"True unexamined at Gate 1 (I-326) and seal()'s truthiness check "
                f"would not catch it. Refusing."
            )
    return specs


def verify_item_7_completed(cutoff: str) -> None:
    """Refuse unless item 7 has already run AND closed its grant."""
    if not REGISTRY.exists():
        raise SystemExit(f"No registry at {REGISTRY}. Item 7 has not run.")
    c = sqlite3.connect(f"file:{REGISTRY}?mode=ro", uri=True)

    n = c.execute("select count(*) from hypotheses where family=?", (FAMILY,)).fetchone()[0]
    if n != 1:
        raise SystemExit(
            f"REFUSING: hypotheses for {FAMILY!r} = {n}, expected 1. Item 6 runs "
            f"STRICTLY AFTER item 7. If this is 0, the registration has not "
            f"happened (or rolled back) and sealing vaults now would lock a "
            f"holdout for a family that does not exist."
        )

    fws = c.execute(
        "select forward_window_start from hypotheses where family=?", (FAMILY,)
    ).fetchone()[0]
    if str(fws) != cutoff:
        raise SystemExit(
            f"REFUSING: registered forward_window_start is {fws!r}, --cutoff is "
            f"{cutoff!r}. C8 requires the vault cutoff to EQUAL C. Pass the value "
            f"--execute printed, verbatim."
        )

    row = c.execute(
        "select reason, outcome, closed_utc from write_grants order by grant_id desc limit 1"
    ).fetchone()
    if row is None:
        raise SystemExit("REFUSING: write_grants is empty; item 7 has not run.")
    reason, outcome, closed = row
    already = c.execute(
        "select count(*) from write_grants where reason='VAULT_SEAL'"
    ).fetchone()[0]
    if already >= 4:
        raise SystemExit(
            f"REFUSING: {already} VAULT_SEAL grants already exist. The four locks "
            f"are sealed. Re-running would attempt a second seal on an immutable "
            f"spec."
        )
    if already == 0:
        if reason != "REGISTER_HYPOTHESIS" or outcome != "CLEAN":
            raise SystemExit(
                f"REFUSING: newest grant is ({reason!r}, {outcome!r}), expected "
                f"('REGISTER_HYPOTHESIS', 'CLEAN'). Item 6 follows item 7."
            )
    if closed is None:
        raise SystemExit(
            "REFUSING: the newest write_grant has closed_utc = NULL -- it is still "
            "OPEN. Grants do not nest (R-7): sealing now would raise "
            "RegistryWriteGrantNestedError and roll the registration back with it "
            "(I-311). Let item 7's process exit first."
        )
    c.close()
    print(f"  precondition: 1 hypothesis, forward_window_start = {fws}, "
          f"newest grant ({reason}, {outcome}) CLOSED, VAULT_SEAL rows = {already}")


def acquire_passphrase() -> str | None:
    """Interactive only -- never an argument, never an environment variable."""
    try:
        return getpass.getpass(
            "\n  Holdout passphrase (not echoed; Principal's hands only): "
        ) or None
    except (EOFError, KeyboardInterrupt):
        return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cutoff", required=True,
                    help="C, verbatim from --execute's 'forward_window_start = C = ...' line")
    ap.add_argument("--dry-run", action="store_true",
                    help="verify preconditions and print the four specs; seal nothing")
    args = ap.parse_args()

    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", args.cutoff):
        raise SystemExit(f"--cutoff {args.cutoff!r} is not an ISO date (YYYY-MM-DD).")

    print("=" * 78)
    print("ITEM 6 -- FOUR HOLDOUT VAULT SEALS -- PREREG-002")
    print("=" * 78)

    specs = extract_vault_specs()
    print(f"\n  parsed {len(specs)} vault specifications from PREREG-002 §21 "
          f"[not typed, not paraphrased]")
    for s in specs:
        sk = s["seal"]
        print(f"    {sk['source']:<12} {sk['dataset_id']:<16} "
              f"cols={len(sk['schema_fingerprint']['columns'])} "
              f"vault_dir={s['ctor']['vault_dir'].split('/')[-1]}")

    print(f"\n  verifying item 7 completed, cutoff C = {args.cutoff}")
    verify_item_7_completed(args.cutoff)

    if args.dry_run:
        print("\n--dry-run: preconditions pass, nothing was sealed.\n")
        return 0

    passphrase = acquire_passphrase()
    if not passphrase:
        print(
            "\nREFUSING: no passphrase supplied at the prompt. C8 requires all "
            "four vaults sealed in the same session and UTC day as the "
            "registration -- a partial set is refused rather than half-performed.\n",
            file=sys.stderr,
        )
        return 2

    sys.path.insert(0, str(REPO / "harness"))
    from castellan.registry import TrialRegistry       # noqa: E402
    from castellan.data import PITStore                # noqa: E402
    from castellan.holdout import HoldoutVault         # noqa: E402

    registry = TrialRegistry(str(REGISTRY), allow_create=False)
    store = PITStore(str(PIT), registry=registry)

    print("\n  sealing -- one write_grant(VAULT_SEAL) per call, none nested:\n")
    for i, s in enumerate(specs, 1):
        ctor, sk = s["ctor"], dict(s["seal"])
        vault = HoldoutVault(
            vault_dir=str(REPO / ctor["vault_dir"]),
            registry=registry,
            name=ctor["name"],
            family=ctor["family"],
            store=store,
        )
        vault.seal(cutoff=args.cutoff, passphrase=passphrase, **sk)
        print(f"    [{i}/4] SEALED  {sk['source']:<12} {sk['dataset_id']:<16} "
              f"cutoff={args.cutoff}")

    print("\n" + "=" * 78)
    print("READ-BACKS -- the evidence, since these print nothing on success")
    print("=" * 78)
    c = sqlite3.connect(f"file:{REGISTRY}?mode=ro", uri=True)
    print("\n  write_grants, newest first:")
    for gid, reason, outcome in c.execute(
        "select grant_id, reason, outcome from write_grants order by grant_id desc limit 6"
    ):
        print(f"    {gid:>3}  {reason:<22} {outcome}")
    # MEASURED, not assumed: one seal() opens TWO VAULT_SEAL grants -- one for
    # the vault file write (dispatch 'HoldoutVault.seal') and one for the
    # holdout_spec_sealed event (dispatch 'HoldoutVault.holdout_spec_sealed').
    # Four vaults therefore produce EIGHT rows, not four. Checklist item 6 and
    # every prior statement of this read-back say four. See I-367.
    n_vault = c.execute(
        "select count(*) from write_grants where reason='VAULT_SEAL' and outcome='CLEAN'"
    ).fetchone()[0]
    by_dispatch = dict(c.execute(
        "select dispatch, count(*) from write_grants where reason='VAULT_SEAL' "
        "and outcome='CLEAN' group by dispatch"
    ).fetchall())
    print(f"\n  VAULT_SEAL CLEAN rows : {n_vault}   (expected 8 -- TWO per seal(), "
          f"measured; item 6's 'four' is I-367)")
    for d, n in sorted(by_dispatch.items()):
        print(f"      {d:<40} {n}   (expected 4)")
    c.close()

    p = sqlite3.connect(f"file:{PIT}?mode=ro", uri=True)
    print("\n  ingest_ceiling rows:")
    for src, did, cut in p.execute(
        "select source, dataset_id, cutoff from ingest_ceiling order by source, dataset_id"
    ):
        print(f"    {src:<12} {did:<16} cutoff={cut}")
    n_ceil = p.execute("select count(*) from ingest_ceiling").fetchone()[0]
    print(f"\n  ingest_ceiling total  : {n_ceil}   (expected 4; fewer = FAILED)")
    p.close()

    specs_on_disk = sorted((REPO / "book" / "vaults").glob("*/spec.json"))
    print(f"\n  spec.json under book/vaults/ : {len(specs_on_disk)}   (expected 4)")
    for sp in specs_on_disk:
        print(f"    {sp.relative_to(REPO)}")

    ok = (n_vault == 8
          and by_dispatch.get('HoldoutVault.seal') == 4
          and by_dispatch.get('HoldoutVault.holdout_spec_sealed') == 4
          and n_ceil == 4 and len(specs_on_disk) == 4)
    print("\n" + ("  ITEM 6 COMPLETE -- C8's vault half is discharged."
                  if ok else
                  "  ITEM 6 INCOMPLETE -- one or more counts is not 4. DO NOT "
                  "proceed; file an incident."))
    print()
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
