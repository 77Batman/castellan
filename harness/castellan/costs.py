"""The shared cost library. Researchers may not hand-roll costs.

Charter cost stack, applied per side:

    commission + 0.5 * spread * capture_factor
    + Y * sigma_daily * sqrt(Q / ADV)          (square-root impact)
    + carry (borrow / funding), accrued per bar on held notional

All figures in decimal return terms (1 bp = 1e-4).
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
    funding_bps_annual: float = 0.0  # charged on held notional (sign: cost)
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

    def carry_per_bar(
        self, long_notional: float | np.ndarray, short_notional: float | np.ndarray
    ) -> float | np.ndarray:
        """Holding cost per bar as a fraction of book (borrow on shorts,
        funding on gross)."""
        borrow = self.borrow_bps_annual * BP / self.periods_per_year
        fund = self.funding_bps_annual * BP / self.periods_per_year
        return (
            np.asarray(short_notional, dtype=float) * borrow
            + (np.asarray(long_notional, dtype=float)
               + np.asarray(short_notional, dtype=float)) * fund
        )

    def scaled(self, multiplier: float) -> "CostModel":
        """Stress copy — e.g. 2x for the Gate 1 cost-robustness test."""
        return replace(
            self,
            name=f"{self.name}_x{multiplier:g}",
            commission_bps=self.commission_bps * multiplier,
            half_spread_bps=self.half_spread_bps * multiplier,
            impact_y=self.impact_y * multiplier,
            borrow_bps_annual=self.borrow_bps_annual * multiplier,
            funding_bps_annual=self.funding_bps_annual * multiplier,
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
    funding_bps_annual=1095.0,  # 0.01%/8h baseline against structural longs
    periods_per_year=365,
)

POLYMARKET = CostModel(
    name="polymarket",
    commission_bps=0.0,
    half_spread_bps=100.0,    # thin books; 1c on a 50c contract ~ 2%, be honest
    impact_y=2.0,
    periods_per_year=365,
)
