"""Acceptance tests for I-051 — purge and embargo in both CV splitters.

Authored by the Head of Quantitative Validation under VALIDATION-SPEC-001,
BEFORE implementation. Seat 9 implements against these and does not amend
them; a test Seat 9 believes is wrong is escalated to Validation in writing
before it is changed (Ruling 004 §11 standing terms, I-036).

RED BY DESIGN. 11 tests; all 11 fail against the harness as it stands
today [measured, this session]. ``test_cvt3_*`` and ``test_cvt11_*`` are
regression guards rather than drivers — the behaviour they assert is
already correct — but they are red today because they use the post-change
call form, which today's signatures reject.

Clause references are to VALIDATION-SPEC-001 §2 (W-1 … W-10).

These tests supersede Ruling 004 §11.3's ML-T-11 as drafted. That draft's
third assertion — "no training bar in a later window reads within 30 bars
of a previous test fold's end" — is WITHDRAWN by VALIDATION-SPEC-001
§2.1(c). In an expanding-window walk-forward, window k's test fold is
legitimately past data by window k+1; a later training bar reading it is
not leakage. ``test_cvt8_*`` below asserts the opposite of that draft, on
purpose, so the withdrawal cannot be silently reversed by drift.
"""

import math

import numpy as np
import pytest

from castellan.cv import purged_kfold_splits, walk_forward_windows

EMBARGO_FRACTION = 0.01  # Charter §4.2, imported not set here


def _cv_error():
    """W-1: the new refusal exception. Probed lazily so a missing class is
    a per-test FAILURE rather than a collection error."""
    import castellan.errors as errors
    if not hasattr(errors, "CVSpecificationError"):
        pytest.fail(
            "NOT IMPLEMENTED: castellan.errors.CVSpecificationError does not "
            "exist. Required by VALIDATION-SPEC-001 clauses W-1/W-5 (I-051). "
            "It must subclass ValueError so no existing `except ValueError` "
            "handler is broken."
        )
    assert issubclass(errors.CVSpecificationError, ValueError), \
        "W-1: CVSpecificationError must subclass ValueError"
    return errors.CVSpecificationError


# ======================================================================
# W-1 / W-2 / W-3 — purged_kfold_splits
# ======================================================================

def test_cvt1_purged_kfold_refuses_an_unstated_feature_lookback():
    """W-1. THE CLAUSE THAT MAKES THE DECLARATION COMPULSORY.

    A splitter that defaults the lookback to zero is a splitter that lets a
    30-day-lookback family leak by omission. Silence is not a statement.
    """
    err = _cv_error()
    with pytest.raises(err):
        list(purged_kfold_splits(1000, 5, EMBARGO_FRACTION))
    with pytest.raises(err):
        list(purged_kfold_splits(1000, 5, EMBARGO_FRACTION,
                                 feature_lookback=None))
    with pytest.raises(err):
        list(purged_kfold_splits(1000, 5, EMBARGO_FRACTION,
                                 feature_lookback=-1))


def test_cvt2_purged_kfold_embargo_honours_feature_lookback():
    """W-2 (ML-T-9). THE EXACT ARITHMETIC OF THE MEASURED DEFECT.

    n_samples=2398, embargo_fraction=0.01 -> ceil = 24 bars [measured].
    PREREG-002 §7.1 declares a 30-day trailing baseline [cited]. A training
    bar 25-30 places after the fold computes its features from INSIDE the
    fold. The effective embargo must be 30, not 24.
    """
    _cv_error()
    n, fl = 2398, 30
    assert math.ceil(n * EMBARGO_FRACTION) == 24, "fixture sanity"

    folds = list(purged_kfold_splits(n, 5, EMBARGO_FRACTION,
                                     feature_lookback=fl))
    assert len(folds) == 5
    for train, test in folds:
        t1 = int(test[-1])
        forbidden = np.arange(t1 + 1, min(n, t1 + 1 + fl))
        assert len(np.intersect1d(train, forbidden)) == 0, (
            f"W-2: training index within {fl} bars after a test fold ending "
            f"at {t1} — its feature window reads inside the fold")
        assert len(np.intersect1d(train, test)) == 0


def test_cvt3_purged_kfold_purge_is_at_least_the_label_span():
    """W-3 (ML-T-10). A REGRESSION GUARD, not a driver.

    The purge is already correct today [measured — cv.py:37]. This test
    exists so the W-1/W-2 edit cannot break it in passing. It is red today
    only because of the new required keyword, not because of the purge.
    """
    _cv_error()
    n, ls = 2000, 5
    for train, test in purged_kfold_splits(n, 5, EMBARGO_FRACTION,
                                           label_span=ls, feature_lookback=0):
        t0 = int(test[0])
        purged = np.arange(max(0, t0 - ls), t0)
        assert len(np.intersect1d(train, purged)) == 0, (
            f"W-3: a training label spanning {ls} bars from before {t0} "
            "reads returns inside the test fold")


def test_cvt4_feature_lookback_zero_is_a_valid_explicit_statement():
    """W-1. Zero means "this family's features use no trailing window" and
    is accepted. The Charter's 1% floor still applies underneath it."""
    _cv_error()
    n = 1000
    emb = math.ceil(n * EMBARGO_FRACTION)
    assert emb == 10
    for train, test in purged_kfold_splits(n, 5, EMBARGO_FRACTION,
                                           feature_lookback=0):
        t1 = int(test[-1])
        after = np.arange(t1 + 1, min(n, t1 + 1 + emb))
        assert len(np.intersect1d(train, after)) == 0, \
            "W-2: max(), not feature_lookback — the 1% floor is never reduced"


def test_cvt5_embargo_is_the_max_of_the_two_terms_in_both_directions():
    """W-2. Neither term may dominate the other unconditionally."""
    _cv_error()
    n = 2398
    pct = math.ceil(n * EMBARGO_FRACTION)  # 24

    for fl, expected in ((5, pct), (24, 24), (30, 30), (120, 120)):
        for train, test in purged_kfold_splits(n, 5, EMBARGO_FRACTION,
                                               feature_lookback=fl):
            t1 = int(test[-1])
            forbidden = np.arange(t1 + 1, min(n, t1 + 1 + expected))
            assert len(np.intersect1d(train, forbidden)) == 0, (
                f"W-2: effective embargo must be max({pct}, {fl}) = {expected}")


# ======================================================================
# W-5 / W-6 / W-7 / W-8 — walk_forward_windows
# ======================================================================

def test_cvt6_walk_forward_refuses_unstated_parameters():
    """W-5. Today the function takes neither parameter; there is nothing to
    configure [measured — cv.py:43-61]. It must refuse rather than silently
    reproduce today's unpurged, unembargoed behaviour."""
    err = _cv_error()
    with pytest.raises(err):
        list(walk_forward_windows(1000, 10))
    with pytest.raises(err):
        list(walk_forward_windows(1000, 10, label_span=5))
    with pytest.raises(err):
        list(walk_forward_windows(1000, 10, feature_lookback=30))
    with pytest.raises(err):
        list(walk_forward_windows(1000, 10, label_span=0, feature_lookback=0))


def test_cvt7_walk_forward_purges_and_gaps():
    """W-6 (supersedes ML-T-11's first two assertions). THE TEST THAT
    CARRIES I-051.

    Today walk_forward_windows yields idx[:fold[0]] — every bar strictly
    before the fold, unpurged and unembargoed. A training bar at t0-1 whose
    label is realized over 5 bars reads returns INSIDE the test fold. For a
    fitted family that raises the OOS leg and therefore raises WFE against
    WFE_MIN = 0.50. Permissive.

    gap = max(label_span=5, feature_lookback=30, ceil(0.01*2398)=24) = 30.
    """
    _cv_error()
    n, ls, fl = 2398, 5, 30
    gap = max(ls, fl, math.ceil(n * EMBARGO_FRACTION))
    assert gap == 30, "fixture sanity"

    windows = list(walk_forward_windows(n, 10, label_span=ls,
                                        feature_lookback=fl))
    assert len(windows) == 10
    for train, test in windows:
        t0 = int(test[0])
        forbidden = np.arange(max(0, t0 - gap), t0)
        assert len(np.intersect1d(train, forbidden)) == 0, (
            f"W-6: training index inside the {gap}-bar gap before a fold "
            f"starting at {t0}")
        assert len(np.intersect1d(train, test)) == 0
        if train.size:
            assert int(train[-1]) <= t0 - gap - 1


def test_cvt8_walk_forward_applies_no_forward_embargo_across_windows():
    """W-8. THE ANTI-DRIFT TEST, and it asserts the OPPOSITE of Ruling
    004's ML-T-11 third condition, deliberately.

    In an expanding-window walk-forward, window k's test fold is
    legitimately past data by window k+1. Deleting it from later training
    sets is not a leakage repair — it is a loss of statistical power for no
    statistical reason. VALIDATION-SPEC-001 §2.1(c) withdraws the contrary
    assertion; this test stops it being re-added by drift.
    """
    _cv_error()
    n, ls, fl = 2398, 5, 30
    windows = list(walk_forward_windows(n, 10, label_span=ls,
                                        feature_lookback=fl))
    first_train, first_test = windows[0]
    later_train, _ = windows[2]
    overlap = np.intersect1d(later_train, first_test)
    assert overlap.size > 0, (
        "W-8: a later window's training set must still contain an earlier "
        "window's test fold — that is the expanding window working, not a "
        "leak")


def test_cvt9_walk_forward_preserves_window_count_coverage_and_order():
    """W-7. The gap shortens training sets. It must never merge, drop,
    reorder or shrink a window — Charter §4.4's ">= 10 windows" depends on
    the count being exactly what was asked for."""
    _cv_error()
    n, n_windows = 2398, 12
    windows = list(walk_forward_windows(n, n_windows, label_span=5,
                                        feature_lookback=30))
    assert len(windows) == n_windows

    start = int(n * 0.3)
    covered = np.concatenate([t for _, t in windows])
    assert covered.min() == start
    assert covered.max() == n - 1
    assert len(np.unique(covered)) == covered.size, "folds must not overlap"
    assert np.array_equal(covered, np.sort(covered)), "folds must ascend"

    for train, test in windows:
        if train.size:
            assert int(train[-1]) < int(test[0])


def test_cvt10_walk_forward_gap_is_the_max_of_all_three_terms():
    """W-6. Each of the three terms must be able to win on its own."""
    _cv_error()
    n = 2000
    pct = math.ceil(n * EMBARGO_FRACTION)  # 20
    cases = [
        (60, 0, 60),    # label_span wins
        (1, 90, 90),    # feature_lookback wins
        (1, 0, pct),    # the Charter 1% floor wins
    ]
    for ls, fl, expected in cases:
        for train, test in walk_forward_windows(n, 10, label_span=ls,
                                                feature_lookback=fl):
            t0 = int(test[0])
            forbidden = np.arange(max(0, t0 - expected), t0)
            assert len(np.intersect1d(train, forbidden)) == 0, (
                f"W-6: gap must be max({ls}, {fl}, {pct}) = {expected}")


# ======================================================================
# W-9 — the legacy call sites keep every property they asserted
# ======================================================================

def test_cvt11_legacy_properties_survive_at_the_explicit_call_sites():
    """W-9. GREEN AFTER THE TWO AUTHORIZED CALL-SITE EDITS.

    The two legacy tests in test_harness.py asserted behaviour *at* zero
    feature lookback and unit label span; they simply could not say so.
    This test restates both legacy assertions in the post-change call form,
    so that if Seat 9's edit weakens either one, it is caught here as well
    as there.
    """
    _cv_error()
    for train, test in purged_kfold_splits(1000, 5, 0.01, feature_lookback=0):
        assert len(np.intersect1d(train, test)) == 0
        after = np.arange(int(test[-1]) + 1, min(1000, int(test[-1]) + 11))
        assert len(np.intersect1d(train, after)) == 0

    windows = list(walk_forward_windows(1000, 10, label_span=1,
                                        feature_lookback=0))
    assert len(windows) == 10
    for train, test in windows:
        assert int(train[-1]) < int(test[0])
