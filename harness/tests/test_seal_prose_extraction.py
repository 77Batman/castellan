"""I-333 — the seal extractor must return the field VALUE, not the delimited literal.

`REGISTRATION-PAYLOAD-PREREG-002.md` §3 defines the extraction:

    "the text between `<field_name>                    = "` and its closing `"`"

BETWEEN the quotes. The quotes are delimiters, not content.

`extract_literals` honours that — it runs `ast.literal_eval`, which unquotes.
`extract_prose` did not: it returned `m.group(1).rstrip()`, delimiters included,
so every one of the eight prose strings that `prereg_sha256` hashes carried a
leading and trailing `"` that §3 says is not part of the value.

Written RED, before the repair, per the Principal's I-333 ruling. At the time of
writing all eight fields failed `test_no_prose_field_is_quote_wrapped`.

Why it matters more than two characters: `prereg_sha256` hashes all sixteen
fields and P7 freezes them at the seal. The repair moves eight hashes exactly
once, and only before the act.

Note recorded with the test, because it is the reason the defect survived: no
test in `harness/tests/` touched `execute_seal_prereg002.py` at all before this
file. That is I-039's pattern — the worst error sitting in the only untested
function.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "harness" / "scripts" / "execute_seal_prereg002.py"

PROSE = (
    "statement",
    "mechanism",
    "falsifier",
    "universe",
    "horizon",
    "success_criteria",
    "forward_kill_condition",
    "model_prior_provenance",
)


def _seal_module():
    spec = importlib.util.spec_from_file_location("execute_seal_prereg002", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def prose():
    return _seal_module().extract_prose()


def test_all_eight_prose_fields_are_extracted(prose):
    assert set(prose) == set(PROSE), f"missing: {set(PROSE) - set(prose)}"


@pytest.mark.parametrize("field", PROSE)
def test_no_prose_field_is_quote_wrapped(prose, field):
    """THE RED ASSERTION. §3's value is the text BETWEEN the delimiters."""
    v = prose[field]
    assert not v.startswith('"'), (
        f"{field} begins with a delimiter: {v[:60]!r} -- §3 defines the value as "
        f"the text BETWEEN the quotes"
    )
    assert not v.endswith('"'), (
        f"{field} ends with a delimiter: {v[-60:]!r} -- §3 defines the value as "
        f"the text BETWEEN the quotes"
    )


@pytest.mark.parametrize("field", PROSE)
def test_prose_field_is_non_empty_and_not_merely_unquoted_whitespace(prose, field):
    """Guards the repair against the degenerate fix of returning ''."""
    assert len(prose[field].strip()) > 100, f"{field} is implausibly short"


def test_passphrase_is_never_read_from_the_environment(monkeypatch):
    """Principal-ruled 2026-09-14: interactive only, never an argument or env var.

    The shipped script read `CASTELLAN_HOLDOUT_PASSPHRASE` from `os.environ` and
    used it ONLY as a presence gate -- it never uses the value, because item 6
    (the vault seal) is not performed by this script. Taking a secret you never
    use is strictly more exposure for no benefit: an environment variable is
    readable from the process table on some platforms and lands in shell history
    when set inline.
    """
    mod = _seal_module()
    monkeypatch.setenv("CASTELLAN_HOLDOUT_PASSPHRASE", "env-var-must-be-ignored")
    monkeypatch.setattr(mod.getpass, "getpass", lambda prompt="": "typed-at-the-prompt")
    assert mod._acquire_passphrase() == "typed-at-the-prompt"


def test_passphrase_prompt_refusing_empty_is_a_refusal_not_a_pass(monkeypatch):
    """An empty prompt must refuse, exactly as the missing env var used to.

    C8 requires the vault sealed in the same session and UTC day as the
    registration, so a partial run -- a registered family with an unsealed
    holdout -- is refused rather than half-performed.
    """
    mod = _seal_module()
    monkeypatch.setattr(mod.getpass, "getpass", lambda prompt="": "")
    assert mod._acquire_passphrase() is None


def test_literal_fields_are_unquoted_and_stay_that_way():
    """`extract_literals` already conforms to §3 via ast.literal_eval.

    Asserted so the I-333 repair cannot be 'fixed' by making prose match
    literals in the wrong direction.
    """
    lits = _seal_module().extract_literals()
    assert lits["family"] == "funding-carry-conditioning-002"
    assert not lits["family"].startswith('"')
    assert lits["trial_budget"] == 47
    assert lits["n_inherited"] == 7
    assert lits["holdout_classification"] == "FORWARD"
    assert not lits["holdout_classification"].startswith('"')


@pytest.mark.parametrize("field", PROSE)
def test_repair_removes_the_delimiters_and_nothing_else(prose, field):
    """The ruled change, stated as arithmetic against an independent extraction.

    §3's value is the text BETWEEN the delimiters -- so the repaired value must
    equal the rstripped raw capture with exactly one leading and one trailing
    character removed. Not `.strip('"')`, which would eat a legitimate run of
    quotes; not a second `.rstrip()` after unquoting, which would eat whitespace
    that sits INSIDE the delimiters and is therefore content.

    The regex is restated here deliberately rather than imported: this is the
    independent check, and a check that calls the thing it checks is not one.
    """
    import re

    lines = _seal_module().PREREG.read_text().split("\n")
    start = next(i for i, L in enumerate(lines) if re.match(r"^## 21[.\s]", L))
    fence = [i for i in range(start, len(lines)) if lines[i].strip().startswith("```")][:2]
    body = "\n".join(lines[fence[0] + 1 : fence[1]])
    raw = re.search(
        rf"^{field}\s*=\s*(.*?)(?=^[a-z_]+\s*=|\Z)", body, re.S | re.M
    ).group(1).rstrip()

    assert raw.startswith('"') and raw.endswith('"'), (
        f"{field}'s source literal is not delimiter-wrapped; the repair's "
        f"premise does not hold for it"
    )
    assert prose[field] == raw[1:-1]
    assert len(prose[field]) == len(raw) - 2
