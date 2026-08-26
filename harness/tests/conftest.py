"""VALIDATION-RULING-006 section 5.1 -- the write-grant visibility fixture.

    The fixture supplies the ANNOUNCEMENT; the test supplies the AUTHORITY.

``grant`` is a factory fixture. It opens nothing itself -- a test (or a
fixture, for its OWN writes only, closing before it returns) opens the
grant explicitly, in its own text:

    with grant(registry, "REGISTER_HYPOTHESIS"):
        registry.open_hypothesis(...)

Every open prints one line; every test prints a summary line at
teardown -- ``grants_taken=[...]`` or ``grants_taken=NONE`` -- so a test
that took no grant is never silent (GATES.md section 4.7.4(ii)).

The refused shape (a fixture that opens ``write_grant`` and ``yield``s
while it is open, so a test's writes ride on authority its own text
never shows) is not used here: this fixture's own ``yield`` hands back a
plain callable, with no registry grant open across it. See
``test_grant_meta.py::test_grant_meta_01`` for the static check that
would catch that shape if it were ever introduced.
"""
from __future__ import annotations

import pytest

TEST_TOKEN = "test-token"


@pytest.fixture
def grant(request):
    taken: list[str] = []
    testname = request.node.name
    fname = request.node.location[0].rsplit("/", 1)[-1]

    def _open(registry, reason: str, dispatch: str | None = None):
        d = dispatch or f"TEST:{testname}"
        print(f"[write-grant] {fname}::{testname} reason={reason} dispatch={d}")
        taken.append(reason)
        return registry.write_grant(reason=reason, dispatch=d, token=TEST_TOKEN)

    yield _open
    print(f"[write-grant] {fname}::{testname} grants_taken={taken if taken else 'NONE'}")
