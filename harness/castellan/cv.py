"""Cross-validation splitters: purged K-fold with embargo, walk-forward.

Purged K-fold (Lopez de Prado 2018): training observations whose
information overlaps the test fold are purged, and an embargo of
EMBARGO_FRACTION of bars after the test fold is additionally dropped
from training, so serially-correlated leakage cannot flatter the fit.
"""

from __future__ import annotations

import numpy as np

EMBARGO_FRACTION_DEFAULT = 0.01


def purged_kfold_splits(
    n_samples: int,
    n_splits: int = 5,
    embargo_fraction: float = EMBARGO_FRACTION_DEFAULT,
    label_span: int = 1,
):
    """Yield (train_idx, test_idx) with purge and embargo.

    label_span: bars over which each observation's label is realized
    (1 for next-bar returns). Training bars within `label_span` before
    the test fold are purged; `embargo` bars after it are embargoed.
    """
    idx = np.arange(n_samples)
    embargo = int(np.ceil(n_samples * embargo_fraction))
    folds = np.array_split(idx, n_splits)
    for fold in folds:
        t0, t1 = fold[0], fold[-1]
        train_mask = np.ones(n_samples, dtype=bool)
        # test fold itself
        train_mask[t0 : t1 + 1] = False
        # purge: labels overlapping the test window
        train_mask[max(0, t0 - label_span) : t0] = False
        # embargo after the test window
        train_mask[t1 + 1 : min(n_samples, t1 + 1 + embargo)] = False
        yield idx[train_mask], fold


def walk_forward_windows(
    n_samples: int,
    n_windows: int = 10,
    min_train_fraction: float = 0.3,
):
    """Yield (train_idx, test_idx) for expanding-window walk-forward.

    The final `1 - min_train_fraction` of the sample is split into
    `n_windows` consecutive test windows; each is preceded by all prior
    bars as training. Charter requires >= 10 windows.
    """
    idx = np.arange(n_samples)
    start = int(n_samples * min_train_fraction)
    test_region = idx[start:]
    folds = np.array_split(test_region, n_windows)
    for fold in folds:
        if fold.size == 0:
            continue
        yield idx[: fold[0]], fold
