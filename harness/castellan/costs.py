"""The shared cost library. Researchers may not hand-roll costs.

Charter cost stack, applied per side:

    commission + 0.5 * spread * capture_factor
    + Y * sigma_daily * sqrt(Q / ADV)          (square-root impact)
    + borrow, accrued per bar on short notional

All figures in decimal return terms (1 bp = 1e-4).

Funding does NOT live here (Validation Ruling 003, I-034): it is a
signed asset cash flow, not a friction, and belongs in engine P&L
accrual (see ``engine.run_backtest``'s ``funding_panel`` argument and
``data.pit_funding_panel``). A field whose correct value is always zero
and whose wrong value silently double-counts with the sign inverted is
a lapse waiting to happen, so it does not exist here at all -- misuse
is a ``TypeError``, not a convention.
"""

from __future__ import annotations

from dataclasses import dataclass, replace

import numpy as np

BP = 1e-4


@dataclass(frozen=True)
class CostModel:
    name: str
    commission_bps: float          # per side
    half_spread_bps: float         # 0.5 * spread * capture_factor
    impact_y: float = 1.0          # square-root law prefactor
    impact_exponent: float = 0.5
    borrow_bps_annual: float = 0.0   # charged on short notional
    periods_per_year: int = 252

    def per_side_cost(
        self,
        trade_notional: float | np.ndarray,
        sigma_daily: float | np.ndarray = 0.0,
        adv_notional: float | np.ndarray | None = None,
    ) -> float | np.ndarray:
        """Cost per side as a fraction of trade notional."""
        base = (self.commission_bps + self.half_spread_bps) * BP
        if adv_notional is None:
            return base * np.ones_like(np.asarray(trade_notional, dtype=float))
        q = np.asarray(trade_notional, dtype=float)
        adv = np.asarray(adv_notional, dtype=float)
        with np.errstate(divide="ignore", invalid="ignore"):
            part = np.where(adv > 0, q / adv, 0.0)
        impact = self.impact_y * np.asarray(sigma_daily) * part ** self.impact_exponent
        return base + impact

    def borrow_per_bar(
        self,
        short_notional: float | np.ndarray,
        *,
        periods_per_year: int | None = None,
    ) -> float | np.ndarray:
        """Borrow cost per bar as a fraction of book, charged on short
        notional only (Ruling 003 section 3.1 -- the renamed, single-
        notional replacement for the old ``carry_per_bar``, which took
        ``long_notional + short_notional`` and is the exact shape of the
        I-034 gross bug: that shape is no longer expressible because
        this signature only accepts one).

        ``periods_per_year`` is keyword-only and defaults to this
        model's own field, but the ENGINE always passes its own
        ``periods_per_year`` explicitly (Ruling 003 N-1): the old
        function annualized against ``cost_model.periods_per_year``
        while ``run_backtest`` annualized returns against its own,
        separate argument, and nothing reconciled them. Passing two
        positional arguments (the old ``(long, short)`` shape) raises
        ``TypeError`` by construction, since there is no second
        positional parameter at all.
        """
        ppy = periods_per_year if periods_per_year is not None else self.periods_per_year
        rate = self.borrow_bps_annual * BP / ppy
        return np.asarray(short_notional, dtype=float) * rate

    def scaled(self, multiplier: float) -> "CostModel":
        """Stress copy — e.g. 2x for the Gate 1 cost-robustness test.

        Frictions only (Ruling 003 section 3.6): commission, half-spread,
        impact, and borrow. There is no field left for a multiplier to
        apply to a receipt -- doubling a receipt is not a stress, and
        after this change there is nothing here shaped like one.
        """
        return replace(
            self,
            name=f"{self.name}_x{multiplier:g}",
            commission_bps=self.commission_bps * multiplier,
            half_spread_bps=self.half_spread_bps * multiplier,
            impact_y=self.impact_y * multiplier,
            borrow_bps_annual=self.borrow_bps_annual * multiplier,
        )


# ----------------------------------------------------------------------
# Presets — conservative until the firm's own fills calibrate them
# ----------------------------------------------------------------------

US_EQUITY_LARGE = CostModel(
    name="us_equity_large",
    commission_bps=0.5,
    half_spread_bps=2.5,
    impact_y=1.0,
)

US_EQUITY_SHORT = CostModel(
    name="us_equity_short",
    commission_bps=0.5,
    half_spread_bps=2.5,
    impact_y=1.0,
    borrow_bps_annual=400.0,  # Charter: assume specials >= 4%/yr
)

CRYPTO_PERP_TAKER = CostModel(
    name="crypto_perp_taker",
    commission_bps=5.0,       # taker fee, major venue
    half_spread_bps=1.0,
    impact_y=1.0,
    periods_per_year=365,
    # No funding term (Ruling 003, I-034): funding is a signed cash flow
    # and is accrued in the engine from the realized `pit_funding_panel`
    # series, never as a scalar rate here.
)

# D-013 section 1: authorized by the Principal, numbers not this seat's to
# adjust. LONG SPOT ONLY -- shorting spot needs its own preset and its own
# Principal decision; generalising this one by implication is exactly how
# a cost library stops being a control. No carry fields, per Ruling 003's
# deletion principle. Conservative-pending-calibration; the Devil's
# Advocate is explicitly free to contest it at Gate 1.
CRYPTO_SPOT_TAKER = CostModel(
    name="crypto_spot_taker",
    commission_bps=10.0,
    half_spread_bps=2.5,
    impact_y=1.0,
    periods_per_year=365,
)

POLYMARKET = CostModel(
    name="polymarket",
    commission_bps=0.0,
    half_spread_bps=100.0,    # thin books; 1c on a 50c contract ~ 2%, be honest
    impact_y=2.0,
    periods_per_year=365,
)
