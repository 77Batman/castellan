#!/usr/bin/env python3
"""Execute the registration-as-seal of `funding-carry-conditioning-002`.

PRINCIPAL-ONLY. This script performs the act the Principal approved at S4-D-014.
It cannot run without the holdout passphrase, which is the Principal's, is never
stored in this repository, and is read here from the environment so that it never
enters a transcript, a log, or an argv.

WHY THIS SCRIPT EXISTS RATHER THAN A HAND-TYPED CALL
----------------------------------------------------
`REGISTRATION-PAYLOAD-PREREG-002.md` gives 8 of the 16 binding fields in executable
form. The other 8 -- statement, mechanism, falsifier, universe, horizon,
success_criteria, forward_kill_condition, model_prior_provenance -- are the long
prose fields, and they are exactly the fields `prereg_sha256` hashes. Hand-assembling
them from a 1,572-line fenced block with 37-space continuation indents, at the moment
of an act P7 makes permanent, is the transcription risk this firm has hit eleven times
(I-141, I-150, I-096, I-245, I-117, ...).

So nothing here is typed. Every one of the sixteen values is EXTRACTED from the
document that declares it:
  - the 8 literals from the payload's own ```python blocks
  - the 8 prose fields from PREREG-002 §21's fenced seal block

The sealed value is the document's value BY CONSTRUCTION, not by anyone's retyping.
That is TEMPLATES.md §7.12 -- cite the artifact you opened -- applied to the seal.

ORDERING IS A CONTROL, NOT A PREFERENCE (I-311, I-312)
-----------------------------------------------------
`HoldoutVault.seal()` opens its own write_grant internally, and grants do not nest
(R-7). Calling the vault seal inside the REGISTER_HYPOTHESIS block raises
RegistryWriteGrantNestedError and ROLLS BACK THE REGISTRATION WITH IT -- verified
twice, by Seat 9 and independently by the CIO on throwaway registries.

This script therefore closes the grant block before touching the vault. The ordering
is enforced by structure here so that it cannot be got wrong by hand.

Usage:
    CASTELLAN_HOLDOUT_PASSPHRASE=... CASTELLAN_REGISTRY_WRITE=... \
        python3 harness/scripts/execute_seal_prereg002.py --inspect
    ... same env ... python3 harness/scripts/execute_seal_prereg002.py --execute
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import os
import re
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PAYLOAD = REPO / "research" / "REGISTRATION-PAYLOAD-PREREG-002.md"
PREREG = REPO / "research" / "PREREG-002-crypto-funding-basis.md"
REGISTRY = REPO / "book" / "registry.db"
FAMILY = "funding-carry-conditioning-002"
COMPUTED_AT_ACT = "<computed at the act: UTC calendar day = C>"

LITERAL_FIELDS = [
    "family", "trial_budget", "predecessor_family", "holdout_classification",
    "forward_window_start", "forward_window_min_length",
    "published_signal_haircut_applied", "n_inherited",
]
PROSE_FIELDS = [
    "statement", "mechanism", "falsifier", "universe", "horizon",
    "success_criteria", "forward_kill_condition", "model_prior_provenance",
]
ALL_FIELDS = [
    "family", "statement", "mechanism", "falsifier", "universe", "horizon",
    "success_criteria", "trial_budget", "predecessor_family",
    "holdout_classification", "forward_window_start", "forward_window_min_length",
    "forward_kill_condition", "model_prior_provenance",
    "published_signal_haircut_applied", "n_inherited",
]


def _strip_inline_comment(expr: str) -> str:
    """Drop a trailing ``# ...`` comment that is not inside a string literal."""
    out, quote = [], None
    for ch in expr:
        if quote:
            out.append(ch)
            if ch == quote:
                quote = None
        elif ch in "\"'":
            quote = ch
            out.append(ch)
        elif ch == "#":
            break
        else:
            out.append(ch)
    return "".join(out).strip()


def extract_literals() -> dict:
    """The 8 executable fields, from the payload's own ```python blocks."""
    src = PAYLOAD.read_text()
    found = {}
    for block in re.findall(r"```python\n(.*?)```", src, re.S):
        m = re.match(r"\s*([a-z_]+)\s*=\s*(.*)", block, re.S)
        if not m:
            continue
        name, raw = m.group(1), _strip_inline_comment(m.group(2))
        if name not in LITERAL_FIELDS or name in found:
            continue
        if name == "forward_window_start":
            # The payload declares this COMPUTED, not fixed:
            #   forward_window_start = datetime.now(timezone.utc).date().isoformat()  # = C
            # That is correct -- C is the seal's own timestamp -- so it is not a literal
            # and must not be literal_eval'd. It is set at execution, below.
            found[name] = COMPUTED_AT_ACT
            continue
        found[name] = ast.literal_eval(raw)
    return found


def extract_prose() -> dict:
    """The 8 prose fields, from PREREG-002 §21's fenced seal block.

    The fence is the authority: these are the strings `prereg_sha256` hashes.
    """
    lines = PREREG.read_text().split("\n")
    start = next(i for i, L in enumerate(lines) if re.match(r"^## 21[.\s]", L))
    fence = [i for i in range(start, len(lines)) if lines[i].strip().startswith("```")][:2]
    if len(fence) != 2:
        raise SystemExit("§21's fenced block could not be located -- refusing to proceed.")
    body = "\n".join(lines[fence[0] + 1:fence[1]])
    found = {}
    for f in PROSE_FIELDS:
        m = re.search(rf"^{f}\s*=\s*(.*?)(?=^[a-z_]+\s*=|\Z)", body, re.S | re.M)
        if m:
            found[f] = m.group(1).rstrip()
    return found


def gather() -> dict:
    fields = {**extract_literals(), **extract_prose()}
    missing = [f for f in ALL_FIELDS if f not in fields]
    if missing:
        raise SystemExit(f"REFUSING: {len(missing)} field(s) not extractable: {missing}")
    return fields


def report(fields: dict) -> None:
    print(f"\n{'=' * 78}\nSIXTEEN BINDING FIELDS, EXTRACTED -- none typed\n{'=' * 78}")
    for f in ALL_FIELDS:
        v = fields[f]
        if isinstance(v, str) and len(v) > 46:
            digest = hashlib.sha256(v.encode()).hexdigest()[:12]
            print(f"  {f:34s} {len(v):6d} chars   sha256 {digest}")
        else:
            print(f"  {f:34s} {v!r}")
    print(f"\n  source, literals: {PAYLOAD.relative_to(REPO)}")
    print(f"  source, prose:    {PREREG.relative_to(REPO)} §21 fenced block")


def registry_state() -> dict:
    c = sqlite3.connect(REGISTRY)
    tables = [r[0] for r in c.execute("select name from sqlite_master where type='table'")]
    return {t: c.execute(f'select count(*) from "{t}"').fetchone()[0] for t in tables}


def main() -> int:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--inspect", action="store_true", help="extract and print; write nothing")
    g.add_argument("--execute", action="store_true", help="perform the seal")
    args = ap.parse_args()

    fields = gather()
    report(fields)

    print(f"\n  registry before: {registry_state()}")

    if args.inspect:
        print("\n--inspect: nothing was written. Re-run with --execute to seal.\n")
        return 0

    passphrase = os.environ.get("CASTELLAN_HOLDOUT_PASSPHRASE")
    if not passphrase:
        print(
            "\nREFUSING: CASTELLAN_HOLDOUT_PASSPHRASE is not set.\n"
            "The holdout passphrase is the Principal's. It is never stored in this\n"
            "repository and is not passed on the command line. Item 6 cannot run\n"
            "without it, and C8 requires the vault sealed in the same session and the\n"
            "same UTC day as the registration -- so a partial run is refused rather\n"
            "than leaving a registered family with an unsealed holdout.\n",
            file=sys.stderr,
        )
        return 2

    sys.path.insert(0, str(REPO / "harness"))
    from castellan.registry import TrialRegistry  # noqa: E402

    C = datetime.now(timezone.utc).date().isoformat()
    fields["forward_window_start"] = C
    print(f"\n  item 5: forward_window_start = C = {C}  (computed at the act, per the payload)")

    reg = TrialRegistry(str(REGISTRY), allow_create=False)

    # --- ITEM 7: registration inside its own grant. Nothing else goes in here. ---
    with reg.write_grant(
        reason="REGISTER_HYPOTHESIS",
        dispatch="S4-D-014-seal",
        token=os.environ.get("CASTELLAN_REGISTRY_WRITE"),
    ) as granted:
        granted.open_hypothesis(**fields)
    # --- grant CLOSED. Only now may the vault be touched (I-311). ---

    print("\n  grant block closed. Vault seal follows OUTSIDE it, per I-311/I-312.")

    c = sqlite3.connect(REGISTRY)
    n_fam = c.execute("select count(*) from hypotheses where family=?", (FAMILY,)).fetchone()[0]
    sha = c.execute("select prereg_sha256 from hypotheses where family=?", (FAMILY,)).fetchone()
    grant = c.execute(
        "select reason, outcome, writes from write_grants order by grant_id desc limit 1"
    ).fetchone()

    print(f"\n{'=' * 78}\nREAD-BACK -- the seal's evidence (I-310: nothing prints on success)\n{'=' * 78}")
    print(f"  hypotheses (family) : {n_fam}                 expect 1")
    print(f"  write_grants last   : {grant}   expect ('REGISTER_HYPOTHESIS','CLEAN',n)")
    print(f"  prereg_sha256       : {sha[0] if sha else None}")
    print(f"  registry after      : {registry_state()}")
    print(f"  C (forward_window_start) : {fields['forward_window_start']}")
    print(
        "\n  BOOTSTRAP-WINDOW CITATION (condition 4):\n"
        "    research/DATA-IMPL-010-write-grants-migration.md -- on this file the first\n"
        "    MIGRATION grant materialised write_grants before its own grant row was\n"
        "    inserted (R-12's named exception, Validation's I-235). Bounded: both\n"
        "    statements sat in one connection and one transaction, so no process could\n"
        "    observe the table populated without its grant.\n"
    )
    print(
        "  ITEM 6 -- VAULT SEAL -- IS NOT PERFORMED BY THIS SCRIPT.\n"
        "    HoldoutVault.seal() needs source, dataset_id, instrument_identity,\n"
        "    query_semantics, cutoff=C, schema_fingerprint and passphrase. Those are the\n"
        "    Principal's to supply and are not derivable from the payload. Seal the vault\n"
        "    now, in this session, same UTC day, with cutoff exactly the C printed above.\n"
        "    C8 is not discharged until that is done.\n"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
