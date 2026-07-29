"""Castellan Capital backtest harness.

The only sanctioned path to a backtest number. Enforces, in code:
pre-registration before any run, automatic trial counting, one shared
cost library, minimum one-bar execution lag, an encrypted single-use
holdout, and Gate 1 evaluation whose N and trial dispersion come from
the registry rather than the sponsor.
"""

from .errors import (
    HoldoutError, HoldoutRegimeError, HoldoutAlreadySealedError,
    HoldoutSpecInvalidError, HoldoutSpecTamperedError, HoldoutRetiredError,
    HoldoutPassphraseError, HoldoutNotYetReachedError,
    HoldoutRetryUnauthorizedError, HoldoutAcquisitionFailedError,
    HoldoutSchemaMismatchError, HoldoutCeilingError,
)
from .registry import TrialRegistry, PreRegistrationError
from .holdout import HoldoutVault
from .engine import run_backtest, SameBarFillError, BacktestResult
from .costs import (
    CostModel, US_EQUITY_LARGE, US_EQUITY_SHORT, CRYPTO_PERP_TAKER, POLYMARKET,
)
from .gates import evaluate_gate1, ValidationReport
from .data import PITStore, pit_adjusted_close, pit_price_panel
from .grid import grid_from_center, run_parameter_grid, GridResult
from .book import PaperBook, BookError, SameBarBookFillError
from . import loaders
from . import stats, cv

__all__ = [
    "TrialRegistry", "PreRegistrationError", "HoldoutVault",
    "HoldoutError", "HoldoutRegimeError", "HoldoutAlreadySealedError",
    "HoldoutSpecInvalidError", "HoldoutSpecTamperedError",
    "HoldoutRetiredError", "HoldoutPassphraseError",
    "HoldoutNotYetReachedError", "HoldoutRetryUnauthorizedError",
    "HoldoutAcquisitionFailedError", "HoldoutSchemaMismatchError",
    "HoldoutCeilingError",
    "run_backtest", "SameBarFillError",
    "BacktestResult", "CostModel", "US_EQUITY_LARGE", "US_EQUITY_SHORT",
    "CRYPTO_PERP_TAKER", "POLYMARKET", "evaluate_gate1", "ValidationReport",
    "PITStore", "pit_adjusted_close", "pit_price_panel",
    "grid_from_center", "run_parameter_grid", "GridResult",
    "PaperBook", "BookError", "SameBarBookFillError",
    "stats", "cv", "loaders",
]
__version__ = "0.1.0"
