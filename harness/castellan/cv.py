"""Cross-validation splitters: purged K-fold with embargo, walk-forward.

Purged K-fold (Lopez de Prado 2018): training observations whose
information overlaps the test fold are purged, and an embargo of
EMBARGO_FRACTION of bars after the test fold is additionally dropped
from training, so serially-correlated leakage cannot flatter the fit.
"""

from __future__ import annotations

import math

import numpy as np

from .errors import CVSpecificationError

EMBARGO_FRACTION_DEFAULT = 0.01


def purged_kfold_splits(
    n_samples: int,
    n_splits: int = 5,
    embargo_fraction: float = EMBARGO_FRACTION_DEFAULT,
    label_span: int = 1,
    *,
    feature_lookback: int | None = None,
):
    """Yield (train_idx, test_idx) with purge and embargo.

    label_span: bars over which each observation's label is realized
    (1 for next-bar returns). Training bars within `label_span` before
    the test fold are purged.

    feature_lookback (VALIDATION-SPEC-001 W-1/W-2, I-051): REQUIRED,
    must be stated explicitly. A training observation at t whose
    features are computed on a trailing window of width W reads
    [t-W, t]; if W exceeds the embargo, that window reaches back inside
    the test fold. The effective embargo is
    max(ceil(n_samples * embargo_fraction), feature_lookback) -- the
    Charter's 1% is a floor and is never reduced by this clause.
    `feature_lookback=0` is a legitimate, explicit statement ("this
    family's features use no trailing window"); silence (`None`) is not,
    and neither is a negative value -- both raise `CVSpecificationError`.
    """
    if feature_lookback is None or feature_lookback < 0:
        raise CVSpecificationError(
            "purged_kfold_splits requires an explicit, non-negative "
            "`feature_lookback` keyword (VALIDATION-SPEC-001 W-1, I-051). "
            "Pass feature_lookback=0 if this family's features use no "
            "trailing window -- silence is not that statement."
        )
    idx = np.arange(n_samples)
    embargo = max(int(np.ceil(n_samples * embargo_fraction)), feature_lookback)
    folds = np.array_split(idx, n_splits)
    for fold in folds:
        t0, t1 = fold[0], fold[-1]
        train_mask = np.ones(n_samples, dtype=bool)
        # test fold itself
        train_mask[t0 : t1 + 1] = False
        # purge: labels overlapping the test window (W-3, unchanged)
        train_mask[max(0, t0 - label_span) : t0] = False
        # embargo after the test window, at the EFFECTIVE embargo (W-2)
        train_mask[t1 + 1 : min(n_samples, t1 + 1 + embargo)] = False
        yield idx[train_mask], fold


def walk_forward_windows(
    n_samples: int,
    n_windows: int = 10,
    min_train_fraction: float = 0.3,
    *,
    label_span: int | None = None,
    feature_lookback: int | None = None,
    embargo_fraction: float = EMBARGO_FRACTION_DEFAULT,
):
    """Yield (train_idx, test_idx) for expanding-window walk-forward.

    The final `1 - min_train_fraction` of the sample is split into
    `n_windows` consecutive test windows; each is preceded by all prior
    bars, less a mandatory gap, as training. Charter requires >= 10
    windows.

    ``label_span`` and ``feature_lookback`` (VALIDATION-SPEC-001 W-5/W-6,
    I-051) are REQUIRED, must be stated explicitly, and gate the
    mandatory purge/gap before every test fold::

        gap = max(label_span, feature_lookback, ceil(n_samples * embargo_fraction))
        train_idx = idx[: max(0, t0 - gap)]

    The three terms are not the same kind of thing: ``label_span`` is a
    leakage repair (a training label spanning into the fold reads the
    fold), the embargo-fraction term is the Charter's 1% floor, and
    ``feature_lookback`` is a Validation TIGHTENING rather than a
    leakage repair -- at the firm's measured rho ~= 0.8 the last W
    training bars and the first W test bars carry near-duplicate
    information, so a WFE ratio computed across that thin a boundary is
    nominally out-of-sample and substantively not.

    No forward embargo is applied after a test fold within the same
    split (W-8, deliberate): in an expanding window a later window's
    training set legitimately includes an earlier window's test fold --
    that is the walk-forward working, not a leak.

    `feature_lookback=0` is a legitimate, explicit statement and is
    accepted; `label_span` must be `>= 1`. Silence (`None`) on either
    raises `CVSpecificationError`, as does a negative value.
    """
    if label_span is None or feature_lookback is None:
        raise CVSpecificationError(
            "walk_forward_windows requires explicit `label_span` and "
            "`feature_lookback` keywords (VALIDATION-SPEC-001 W-5, "
            "I-051). Silence is not the statement that either is zero."
        )
    if label_span < 1:
        raise CVSpecificationError(
            f"label_span must be >= 1, got {label_span} (W-5)."
        )
    if feature_lookback < 0:
        raise CVSpecificationError(
            f"feature_lookback must be >= 0, got {feature_lookback} (W-5)."
        )

    idx = np.arange(n_samples)
    start = int(n_samples * min_train_fraction)
    test_region = idx[start:]
    folds = np.array_split(test_region, n_windows)
    gap = max(label_span, feature_lookback,
              int(math.ceil(n_samples * embargo_fraction)))
    for fold in folds:
        if fold.size == 0:
            continue
        t0 = fold[0]
        train_idx = idx[: max(0, t0 - gap)]
        yield train_idx, fold
