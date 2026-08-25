#!/usr/bin/env python3
"""VALIDATION-SPEC-004 Item 2 (E-1 .. E-25) -- the dated-clause evaluator.

Reads a family's registered fields (or every registered family, if
``--family`` is omitted), evaluates every dated clause -- kill
conditions, condition precedents, observation dates, deadlines of any
kind -- against the store, on this invocation, and exits nonzero on any
firing *or* on any inability to evaluate.

The evaluator writes nothing. It opens the registry through
``TrialRegistry``'s read-only default (E-24) and takes no grant; its
artifact is stdout plus an exit code, pasted into the ritual record.

Exit codes (E-22), the max over every site, 4 > 3 > 2 > 0:
    0  every site PENDING or DISCHARGED (or no clause anywhere)
    1  usage or I/O -- registry absent, family unknown, malformed --as-of
    2  any site FIRED
    3  any site DIVERGENT / SPAN-DIVERGENT / ANCHOR-STALE
    4  any site UNCOVERED / AMBIGUOUS / DANGLING / UNANCHORED

Nonzero is nonzero (E-23): no caller may branch on the specific code to
proceed -- "only a 3, so continue" is forbidden. The code tells a reader
which class to look at first, not whether to look.

Usage:
    python3 harness/scripts/evaluate_dated_clauses.py \\
        [--registry-db PATH] [--family F] [--as-of ISO]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
_HARNESS_SRC = REPO_ROOT / "harness"
if str(_HARNESS_SRC) not in sys.path:
    sys.path.insert(0, str(_HARNESS_SRC))

from castellan import TrialRegistry  # noqa: E402
from castellan.registry import RegistryNotInitializedError  # noqa: E402
from castellan.dated_clauses import evaluate_dated_clauses  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--registry-db", default=str(REPO_ROOT / "book" / "registry.db"),
                     help="the TrialRegistry to read (default: book/registry.db)")
    ap.add_argument("--family", default=None,
                     help="evaluate only this family (default: every registered family)")
    ap.add_argument("--as-of", default=None,
                     help="ISO date to evaluate against instead of wall-clock now. "
                          "Refused if earlier than the family's seal date. Any value "
                          "other than wall-clock stamps AS-OF OVERRIDE on every line "
                          "of the report -- marking, not prevention (I-162).")
    args = ap.parse_args(argv)

    registry_path = Path(args.registry_db)
    try:
        registry = TrialRegistry(str(registry_path), allow_create=False)
    except RegistryNotInitializedError as exc:
        print(f"no registry at {registry_path}: {exc}", file=sys.stderr)
        return 1

    if args.family is not None and registry.hypothesis(args.family) is None:
        print(f"unknown family {args.family!r}: not registered in {registry_path}",
              file=sys.stderr)
        return 1

    try:
        report = evaluate_dated_clauses(registry, family=args.family, as_of=args.as_of)
    except ValueError as exc:
        print(f"cannot evaluate: {exc}", file=sys.stderr)
        return 1

    print(report.render())
    return report.exit_code


if __name__ == "__main__":
    raise SystemExit(main())
