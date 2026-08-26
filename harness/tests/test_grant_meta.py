"""VALIDATION-RULING-006 section 5.1 -- the anti-bypass static check.

The refused shape: a fixture that opens a write grant and ``yield``s
*inside* it, so a test body's writes ride on authority its own text
never shows (R-7 only catches this if the test ALSO grants explicitly;
a test that takes no grant of its own would ride it silently). Not
foreclosed by construction, therefore foreclosed by this test.
"""
from __future__ import annotations

import ast
import pathlib


def _mentions_grant(with_item: ast.withitem) -> bool:
    call = with_item.context_expr
    if not isinstance(call, ast.Call):
        return False
    func = call.func
    name = func.attr if isinstance(func, ast.Attribute) else getattr(func, "id", "")
    return name in ("write_grant", "grant")


def _contains_yield(node: ast.AST) -> bool:
    for child in ast.walk(node):
        if isinstance(child, (ast.Yield, ast.YieldFrom)):
            return True
    return False


def test_grant_meta_01_no_fixture_yields_inside_an_open_grant():
    offenders: list[str] = []
    test_dir = pathlib.Path(__file__).parent
    for path in sorted(test_dir.glob("*.py")):
        if path.name == "test_grant_meta.py":
            continue
        tree = ast.parse(path.read_text(), filename=str(path))
        for node in ast.walk(tree):
            if not isinstance(node, ast.With):
                continue
            if not any(_mentions_grant(item) for item in node.items):
                continue
            if _contains_yield(node):
                offenders.append(f"{path.name}:{node.lineno}")
    assert offenders == [], (
        "fixture(s) yield inside an open write grant -- the invisible "
        f"bypass VALIDATION-RULING-006 section 5.1 forbids: {offenders}"
    )
