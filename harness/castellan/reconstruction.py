"""Off-engine reconstruction of `funding-carry-conditioning-002`'s position
and net-return series, built from PIT component panels rather than from a
`castellan.engine.run_backtest` call.

**I-388 (LOW, filed at DATA-IMPL-015, S4-D-032):** this exact reconstruction
was independently derived twice already -- at DATA-IMPL-014 (S4-D-031, the
`I_0`/`I_max` feasibility gate) and DATA-IMPL-015 (S4-D-032, the leg-(i)
oracle-agreement fixture) -- with no importable artifact checked in either
time, so each seat re-derived the arithmetic from the sealed formulas from
scratch. **This module is that checked-in artifact.** It is the reusable
form of `VALIDATION-SPEC-005-c11-null-calibration.md` sec3.2/sec3.3/sec3.4:
the surrogate construction the C11 null calibration (DATA-IMPL-016) both
BUILDS and PERMUTES.

Position (PREREG-002's sealed `statement` field, not sec5.1's prose -- see
`VALIDATION-SPEC-005` sec3.1, I-376/I-377): **long 1.0 unit spot notional
(0.5 BTC + 0.5 ETH), short w(t) units perp notional per asset (-0.5*w_BTC,
-0.5*w_ETH).** The spot leg is FIXED; only the perp leg scales. This is why
`R_strat` is never a scalar re-weighting of `R_bench` -- de-scaling `w`
un-hedges the position rather than shrinking it.

`reconstruct_net_returns` reproduces `castellan.engine.run_backtest`'s
arithmetic EXACTLY (see `engine.py` line references throughout) on the
constant-`per_side`, no-`sigma_daily`/`adv_notional` branch -- the branch
trial 1 (`config_hash 44532cc88ed7b1a9`) actually ran on, and the ONLY
branch on which this off-engine reconstruction is possible at all (a
varying, sample-dependent impact term could not be reproduced bit-exact
off-engine). Engine parity is asserted by
`harness/tests/test_reconstruction.py` groups A-1 (constant schedule vs
trial 1's stored blob) and A-2 (varying schedule vs a live `run_backtest`
call on a SCRATCH registry).

This module never calls `run_backtest` and never constructs a
`TrialRegistry`. It is pure arithmetic on caller-supplied panels.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from .costs import CRYPTO_PERP_TAKER, CRYPTO_SPOT_TAKER
from .engine import FundingCoverageError

# ---------------------------------------------------------------------------
# The sealed literals (PREREG-002 sec6.2 K1/K2, sec21; hypotheses.statement,
# R41/R44/R46) -- not this module's to choose.
# ---------------------------------------------------------------------------

SPOT_COLS = ("BTC/USDT", "ETH/USDT")
PERP_COLS = ("BTC/USDT:USDT", "ETH/USDT:USDT")
ASSETS = ("BTC", "ETH")
PERP_OF = {"BTC": "BTC/USDT:USDT", "ETH": "ETH/USDT:USDT"}
SPOT_OF = {"BTC": "BTC/USDT", "ETH": "ETH/USDT"}

K_SIZING = 0.5
D_SIZING = 1.0
W_MAX = 1.0
BAND = 0.54
LOOKBACK = 30
PERIODS_PER_YEAR = 365
EXECUTION_LAG = 1
BOOK_NOTIONAL = 1.0

# R-2 (VALIDATION-SPEC-005 sec3.4): the 2025-09-18 Binance funding-formula
# change (PREREG-002 K7, sec6.2) forces z(t) INSUFFICIENT-DATA for 30 days
# from that date inclusive, both assets.
R2_TRIGGER_START = pd.Timestamp("2025-09-18")
R2_TRIGGER_LEN_DAYS = 30

COST_MODEL = {
    "BTC/USDT": CRYPTO_SPOT_TAKER,
    "ETH/USDT": CRYPTO_SPOT_TAKER,
    "BTC/USDT:USDT": CRYPTO_PERP_TAKER,
    "ETH/USDT:USDT": CRYPTO_PERP_TAKER,
}


# ---------------------------------------------------------------------------
# The schedule: z(t), w_target(t), the R-1/R-2 forcing, the R-3 turnover band
# ---------------------------------------------------------------------------


def compute_z(funding: pd.Series, lookback: int | None = None) -> pd.Series:
    """z(t) (PREREG-002 sec6.2 K1): the trailing-24h realized funding rate's
    deviation from its own trailing `lookback`-day mean, in units of that
    window's standard deviation -- both moments computed on the `lookback`
    bars STRICTLY BEFORE t (``rolling(lookback)`` then ``shift(1)``), so
    `z(t)` never uses bar t's own funding print to normalize itself.

    Sample standard deviation (``ddof=1``), matching this codebase's own
    convention throughout `castellan.stats` -- the sealed text does not
    state the divisor explicitly; this is a disclosed ruling, immaterial to
    the calibration of `d=1.0` against its own bracketing (PREREG-002
    sec14.2-14.4, which brackets `d` against a null dispersion argument
    that is insensitive to the N vs N-1 divisor at `lookback=30`).

    The first `lookback` bars (and any bar whose preceding window is not
    yet full) are `NaN` by construction -- R-1's burn-in condition.

    `lookback=None` resolves the CURRENT value of the module-level
    `LOOKBACK` constant at CALL time (not a bound default evaluated at
    import time) -- deliberate, so a test can `monkeypatch.setattr(recon,
    "LOOKBACK", ...)` and have every caller that omits the argument
    observe the change (VALIDATION-SPEC-005 sec7's red-first mutations
    patch these module constants).
    """
    if lookback is None:
        lookback = LOOKBACK
    mean = funding.rolling(lookback).mean().shift(1)
    std = funding.rolling(lookback).std(ddof=1).shift(1)
    with np.errstate(invalid="ignore", divide="ignore"):
        z = (funding - mean) / std
    return z


def w_target_from_z(
    z: pd.Series,
    k: float | None = None,
    d: float | None = None,
    w_max: float | None = None,
) -> pd.Series:
    """w(t) = clip(1 - k*max(0, z(t)-d), 0, w_max) (PREREG-002 sec6.2 K2).

    R-1 (VALIDATION-SPEC-005 sec3.4): wherever `z(t)` is undefined (`NaN`),
    `w` is the benchmark weight `w_max` -- K7 option (1), already sealed for
    exactly this situation (PREREG-002 sec6.2 K7): "held at BENCHMARK WEIGHT
    w = 1.0" while the state variable is INSUFFICIENT-DATA.

    `k`/`d`/`w_max` resolve `K_SIZING`/`D_SIZING`/`W_MAX` at CALL time when
    omitted -- see :func:`compute_z`'s docstring for why.
    """
    if k is None:
        k = K_SIZING
    if d is None:
        d = D_SIZING
    if w_max is None:
        w_max = W_MAX
    excess = (z - d).clip(lower=0.0)
    w = (1.0 - k * excess).clip(lower=0.0, upper=w_max)
    return w.where(z.notna(), w_max)


def r2_forced_mask(
    index: pd.DatetimeIndex,
    start: pd.Timestamp | None = None,
    length: int | None = None,
) -> pd.Series:
    """R-2 (VALIDATION-SPEC-005 sec3.4): True for the 30 bars from
    2025-09-18 inclusive -- the sealed, dated K7 trigger (PREREG-002 sec6.2,
    "BTC and ETH carry z(t) = INSUFFICIENT-DATA and w = 1.0 for the 30 days
    from 2025-09-18"). `start`/`length` resolve `R2_TRIGGER_START`/
    `R2_TRIGGER_LEN_DAYS` at call time when omitted."""
    if start is None:
        start = R2_TRIGGER_START
    if length is None:
        length = R2_TRIGGER_LEN_DAYS
    idx = pd.DatetimeIndex(index)
    end = start + pd.Timedelta(days=length)
    return pd.Series((idx >= start) & (idx < end), index=index)


def apply_turnover_band(
    w_target: pd.Series, forced_mask: pd.Series, band: float | None = None
):
    """R-3 (VALIDATION-SPEC-005 sec3.4): `w_held` is a per-asset state
    variable initialised to 1.0. On a FORCED bar (R-1 burn-in -- `w_target`
    itself is already `w_max` there by construction of
    :func:`w_target_from_z` -- or the R-2 window), `w_held` is set directly
    to the forced target, bypassing the band test: "held at" is a direct
    assignment, not a target that must clear the band. On every other bar:
    if ``|w_target - w_held_prev| > band`` (STRICT), snap to target; else
    unchanged.

    Returns ``(w_held, triggered)`` -- `triggered` is True on bars where the
    non-forced band condition itself fired (for B-6's reported count; it
    does NOT include forced bars, which move unconditionally). `band`
    resolves `BAND` at call time when omitted.
    """
    if band is None:
        band = BAND
    n = len(w_target)
    tgt = w_target.to_numpy(dtype=float)
    forced = forced_mask.to_numpy(dtype=bool)
    held = np.empty(n, dtype=float)
    triggered = np.zeros(n, dtype=bool)
    prev = 1.0
    for i in range(n):
        if forced[i]:
            cur = tgt[i]
        elif abs(tgt[i] - prev) > band:
            cur = tgt[i]
            triggered[i] = True
        else:
            cur = prev
        held[i] = cur
        prev = cur
    idx = w_target.index
    return pd.Series(held, index=idx), pd.Series(triggered, index=idx)


def build_schedule(funding_panel: pd.DataFrame) -> dict:
    """The full realized `w_held(t)` schedule for both assets, per
    VALIDATION-SPEC-005 sec3.4 R-1/R-2/R-3, plus the diagnostics
    sec4.7 row 5 requires.

    `funding_panel` : columns `BTC/USDT:USDT`, `ETH/USDT:USDT` (perp funding
    rate panels, e.g. from `castellan.data.pit_funding_panel`), any index.

    Returns a dict: `w_held` (DataFrame, columns "BTC","ETH"), `forced_mask`
    (DataFrame, same columns, True on R-1 burn-in OR R-2 trigger bars),
    `triggered` (DataFrame, True where the non-forced band condition fired),
    `z` (DataFrame, the raw z-scores, NaN where undefined).
    """
    index = funding_panel.index
    r2_mask = r2_forced_mask(index)

    w_held_cols = {}
    forced_cols = {}
    triggered_cols = {}
    z_cols = {}
    for asset in ASSETS:
        perp_col = PERP_OF[asset]
        funding = funding_panel[perp_col]
        z = compute_z(funding)
        w_target = w_target_from_z(z)
        burn_in_mask = z.isna()
        forced = burn_in_mask | r2_mask
        # R-2 forces the TARGET to 1.0 too (it is not merely a band
        # override): a documented parameter change makes z(t) itself
        # INSUFFICIENT-DATA for the window, exactly like the R-1 burn-in.
        w_target = w_target.where(~r2_mask, 1.0)
        w_held, triggered = apply_turnover_band(w_target, forced)
        w_held_cols[asset] = w_held
        forced_cols[asset] = forced
        triggered_cols[asset] = triggered
        z_cols[asset] = z

    return {
        "w_held": pd.DataFrame(w_held_cols),
        "forced_mask": pd.DataFrame(forced_cols),
        "triggered": pd.DataFrame(triggered_cols),
        "z": pd.DataFrame(z_cols),
    }


# ---------------------------------------------------------------------------
# The position and the off-engine net-return reconstruction
# ---------------------------------------------------------------------------


def build_target_weights(prices: pd.DataFrame, w_held: pd.DataFrame) -> pd.DataFrame:
    """VALIDATION-SPEC-005 sec3.2's `target_weights*(t)`: spot fixed at
    +0.5/+0.5 (BTC/ETH), perp at `-0.5 * w_held` per asset. `prices.columns`
    fixes the column order and set (must be exactly `SPOT_COLS + PERP_COLS`,
    in some order)."""
    missing = [c for c in SPOT_COLS + PERP_COLS if c not in prices.columns]
    if missing:
        raise ValueError(f"prices is missing required column(s): {missing}")
    tw = pd.DataFrame(0.0, index=prices.index, columns=prices.columns)
    for asset in ASSETS:
        tw[SPOT_OF[asset]] = 0.5
        tw[PERP_OF[asset]] = -0.5 * w_held[asset].reindex(prices.index)
    return tw


def reconstruct_net_returns(
    prices: pd.DataFrame,
    funding_panel: pd.DataFrame,
    w: pd.DataFrame,
) -> pd.Series:
    """The off-engine reconstruction. Signature deliberately restricted to
    `(prices, funding_panel, w)` (VALIDATION-SPEC-005 test A-1's guard): a
    trial's stored blob is never an input to this function, only to a
    comparison performed by the CALLER after this returns.

    Reproduces `castellan.engine.run_backtest`'s arithmetic exactly on the
    dict-cost-model, no-`sigma_daily`/`adv_notional` branch (`engine.py`
    lines 137-234), the branch trial 1 actually ran on: `execution_lag=1`,
    `periods_per_year=365`, `book_notional=1.0`, cost models
    `CRYPTO_SPOT_TAKER`/`CRYPTO_PERP_TAKER` (module attributes, read at call
    time -- never a literal; VALIDATION-SPEC-005 test A-4).

    `w` : DataFrame, columns "BTC", "ETH" -- the realized OR surrogate
    schedule, e.g. from :func:`build_schedule`'s `w_held`, or a permuted
    copy of it. This is the ONE object C11 permutes; `prices` and
    `funding_panel` are always the realized panels (VALIDATION-SPEC-005
    sec3: "R_bench is realized, never resampled... the only object that
    moves is the time ordering of w(.)").
    """
    target_weights = build_target_weights(prices, w)

    positions = target_weights.shift(EXECUTION_LAG).fillna(0.0)
    asset_rets = prices.pct_change()
    gross = (positions * asset_rets).sum(axis=1)

    trades = positions.diff().abs().fillna(positions.abs())

    trade_cost = pd.Series(0.0, index=prices.index)
    borrow = pd.Series(0.0, index=prices.index)
    for col in prices.columns:
        cm = COST_MODEL[col]
        tr = trades[col]
        per_side = float(np.asarray(cm.per_side_cost(1.0)).ravel()[0])
        trade_cost = trade_cost + tr * per_side
        short_col = (-positions[col].clip(upper=0)).to_numpy()
        borrow = borrow + pd.Series(
            cm.borrow_per_bar(short_col, periods_per_year=PERIODS_PER_YEAR),
            index=prices.index,
        )
    cost_ret = (trade_cost + borrow).fillna(0.0)

    common = [c for c in prices.columns if c in funding_panel.columns]
    if common:
        fp = funding_panel[common]
        pos_common = positions[common]
        nan_gap = fp.isna() & (pos_common != 0)
        if nan_gap.to_numpy().any():
            raise FundingCoverageError(
                "funding_panel has a coverage gap (NaN) at a bar where the "
                "position is non-zero (engine.py FundingCoverageError parity)."
            )
        carry = -(pos_common * fp.fillna(0.0)).sum(axis=1)
    else:
        carry = pd.Series(0.0, index=prices.index)

    return (gross + carry - cost_ret).fillna(0.0)


def prepare_batch_inputs(prices: pd.DataFrame, funding_panel: pd.DataFrame) -> dict:
    """Precompute the realized, resample-INDEPENDENT arrays
    :func:`reconstruct_net_returns_batch` needs, once, so a caller sweeping
    thousands of surrogate schedules (C11's B=10,000 resamples) does not
    rebuild them per resample. Returns realized per-asset spot/perp simple
    returns and funding arrays (`NaN` at bar 0, from `pct_change`, replaced
    with 0.0 -- multiplied by a zero position there regardless, matching
    `engine.py`'s `(positions * asset_rets).sum(axis=1)` under pandas'
    skip-NaN row sum; explicit here because plain numpy's `0 * nan = nan`
    would not otherwise resolve the same way) and the two sanctioned
    per-side cost rates, read at call time from the shared cost library
    (test A-4 — never literals).
    """
    T = len(prices)
    asset_rets = prices.pct_change().fillna(0.0)
    out = {
        "T": T,
        "per_side_spot": float(np.asarray(CRYPTO_SPOT_TAKER.per_side_cost(1.0)).ravel()[0]),
        "per_side_perp": float(np.asarray(CRYPTO_PERP_TAKER.per_side_cost(1.0)).ravel()[0]),
    }
    for asset in ASSETS:
        out[f"ret_spot_{asset}"] = asset_rets[SPOT_OF[asset]].to_numpy()
        out[f"ret_perp_{asset}"] = asset_rets[PERP_OF[asset]].to_numpy()
        out[f"funding_{asset}"] = funding_panel[PERP_OF[asset]].fillna(0.0).to_numpy()
    spot_active = np.ones(T)
    spot_active[0] = 0.0  # execution_lag=1: no position is held yet at bar 0
    out["spot_active"] = spot_active
    return out


def reconstruct_net_returns_batch(
    prepared: dict, w_btc: np.ndarray, w_eth: np.ndarray
) -> np.ndarray:
    """Vectorized form of :func:`reconstruct_net_returns`: `w_btc`/`w_eth`
    are (B, T) matrices (one row per surrogate resample -- e.g. B=10,000
    circular-block-permuted copies of the realized schedule) and this
    returns the (B, T) matrix of net returns, exactly reproducing the same
    arithmetic as the single-schedule, pandas-based function (verified to
    `1e-12` in `harness/tests/test_reconstruction.py`'s
    `test_batch_matches_single_reconstruction`), because the position
    construction is linear in `w` on the constant-per-side-cost branch
    (VALIDATION-SPEC-005 sec3.2: "this is the only reason a faithful
    off-engine reconstruction is possible at all").

    `prepared` : the dict :func:`prepare_batch_inputs` returns.
    """
    T = prepared["T"]
    B = w_btc.shape[0]
    if w_btc.shape != (B, T) or w_eth.shape != (B, T):
        raise ValueError(f"w_btc/w_eth must both be shape (B, {T})")

    per_side_spot = prepared["per_side_spot"]
    per_side_perp = prepared["per_side_perp"]
    spot_active = prepared["spot_active"]

    gross = np.zeros((B, T))
    carry = np.zeros((B, T))
    trade_perp_cost = np.zeros((B, T))
    trade_spot_cost = np.zeros(T)

    for asset, w in (("BTC", w_btc), ("ETH", w_eth)):
        ret_spot = prepared[f"ret_spot_{asset}"]
        ret_perp = prepared[f"ret_perp_{asset}"]
        funding = prepared[f"funding_{asset}"]

        wl = np.zeros((B, T))
        wl[:, 1:] = w[:, :-1]  # position_perp(t) = -0.5 * w(t-1), w(-1) := 0

        gross += 0.5 * ret_spot[None, :] * spot_active[None, :] - 0.5 * wl * ret_perp[None, :]
        carry += 0.5 * wl * funding[None, :]

        wl_ext = np.concatenate([np.zeros((B, 1)), wl], axis=1)  # implicit wl(-1) = 0
        trade_perp_cost += 0.5 * np.abs(np.diff(wl_ext, axis=1)) * per_side_perp

        trade_spot_cost += 0.5 * np.abs(np.diff(np.concatenate([[0.0], spot_active]))) * per_side_spot

    net = gross + carry - trade_spot_cost[None, :] - trade_perp_cost
    return net


def exposure_match_c(prices: pd.DataFrame, w_held: pd.DataFrame) -> float:
    """VALIDATION-SPEC-005 sec3.3: `c` = (time-avg R_strat gross exposure)
    / (time-avg R_bench gross exposure): ``gross_exposure_strat(t) = 1.0 +
    0.5*w_BTC(t-1) + 0.5*w_ETH(t-1)``, ``gross_exposure_bench(t) = 2.0``.

    Deliberately computed from the PLAIN time-average of `w_held` itself
    (``1.0 + 0.5*mean(w_BTC) + 0.5*mean(w_ETH)``) rather than from the
    engine's literal ``shift(execution_lag).fillna(0.0)`` positions: the
    two differ only in a single-bar edge effect (bar 0's position is 0
    before any decision has been made, and the schedule's own final bar
    is never applied to a position) of order `1/T` (~4e-4 relative at
    T=2415) -- immaterial to `c` itself, but NOT immaterial to test C-2,
    which requires `c` to be EXACTLY invariant under any permutation of
    the multiset (VALIDATION-SPEC-005 sec2.1 reason 3 / sec3.3: "because
    block permutation preserves the multiset exactly, the surrogates' own
    average exposure equals c identically, and test C-2 asserts it rather
    than assuming it"). The shift-based edge effect depends on WHICH value
    lands at the first/last bar after permutation and so is NOT exactly
    permutation-invariant; the plain-mean formula here is a pure function
    of `mean(w)`, which every permutation preserves exactly (verified to
    floating-point identity by C-2), and is the formula VALIDATION-SPEC-005
    sec3.3 itself states as a simple time-average, not as the engine's
    literal lag-and-fill construction.
    """
    w_bar = w_held.mean()
    return float((1.0 + 0.5 * w_bar["BTC"] + 0.5 * w_bar["ETH"]) / 2.0)
