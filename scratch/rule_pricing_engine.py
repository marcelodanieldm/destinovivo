"""
Destino Vivo RMS - Deterministic Rule-Based Pricing Engine
Implements Occupancy, Booking Pace, Competitive Index, Calendar/Event, and Inventory pressure rules.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("RulePricingEngine")

class RuleBasedPricingEngine:
    """Deterministic, predictable rule-based pricing engine for hotel revenue management."""

    EVENT_MULTIPLIERS = {
        "festival": 1.40,
        "holiday": 1.30,
        "weekend": 1.20,
        "regular_day": 1.00
    }

    # Rule 1: Occupancy-Based Pricing Rule
    @staticmethod
    def occupancy_rule(occupancy_pct: float) -> float:
        """
        Occupancy rules:
        - < 50%: 0.80 (-20%)
        - < 70%: 0.90 (-10%)
        - < 85%: 1.00 (Base)
        - < 95%: 1.15 (+15%)
        - >= 95%: 1.30 (+30%)
        """
        if occupancy_pct < 0.50:
            return 0.80
        elif occupancy_pct < 0.70:
            return 0.90
        elif occupancy_pct < 0.85:
            return 1.00
        elif occupancy_pct < 0.95:
            return 1.15
        else:
            return 1.30

    # Rule 2: Booking Pace Rule
    @staticmethod
    def pace_rule(pace: float) -> float:
        """
        Booking pace rule (current bookings / historical avg):
        - > 1.3: 1.25 (+25%)
        - > 1.1: 1.15 (+15%)
        - > 0.9: 1.00 (Base)
        - > 0.7: 0.85 (-15%)
        - <= 0.7: 0.65 (-35%)
        """
        if pace > 1.3:
            return 1.25
        elif pace > 1.1:
            return 1.15
        elif pace > 0.9:
            return 1.00
        elif pace > 0.7:
            return 0.85
        else:
            return 0.65

    # Rule 3: Competitive Pricing Rule
    @staticmethod
    def competitive_rule(comp_index: float) -> float:
        """
        Competitive index = (our_price / avg_competitor_price) * 100
        - < 95: 1.05 (Too cheap -> raise price)
        - > 120: 0.95 (Too expensive -> lower price)
        - else: 1.00
        """
        if comp_index < 95.0:
            return 1.05
        elif comp_index > 120.0:
            return 0.95
        else:
            return 1.00

    # Rule 4: Calendar / Event Rule
    @classmethod
    def calendar_rule(cls, event_type: str) -> float:
        """
        Calendar/Event multiplier lookup.
        """
        return cls.EVENT_MULTIPLIERS.get(event_type.lower(), 1.00)

    # Rule 5: Inventory Forecast Rule
    @staticmethod
    def inventory_rule(occupancy_forecast: float) -> float:
        """
        Inventory forecast remaining capacity pressure:
        - > 95%: 1.40 (+40%)
        - > 90%: 1.25 (+25%)
        - > 75%: 1.10 (+10%)
        - else: 1.00
        """
        if occupancy_forecast > 0.95:
            return 1.40
        elif occupancy_forecast > 0.90:
            return 1.25
        elif occupancy_forecast > 0.75:
            return 1.10
        else:
            return 1.00

    # Constraint Enforcement
    @staticmethod
    def apply_constraints(
        raw_price: float,
        floor_price: float = 80.0,
        ceiling_price: float = 800.0
    ) -> Tuple[float, Dict[str, bool]]:
        """Apply hard floor and ceiling price boundaries."""
        floor_triggered = raw_price < floor_price
        ceiling_triggered = raw_price > ceiling_price

        constrained_price = max(floor_price, min(ceiling_price, raw_price))
        flags = {
            "floor_triggered": floor_triggered,
            "ceiling_triggered": ceiling_triggered
        }
        return round(constrained_price, 2), flags

    @staticmethod
    def validate_rate_parity(
        direct_price: float,
        ota_price: float,
        commission_pct: float
    ) -> Tuple[bool, float]:
        """
        Golden Rule: Direct Rate <= OTA Rate * (1 - commission %)
        Returns (is_valid, max_allowed_direct_price)
        """
        max_direct = ota_price * (1.0 - commission_pct)
        is_valid = direct_price <= (max_direct + 0.01)  # small float tolerance
        return is_valid, round(max_direct, 2)

    def calculate_price(
        self,
        base_price: float,
        occupancy_pct: float,
        pace: float,
        comp_index: float,
        event_type: str,
        inventory_forecast: float,
        floor_price: float = 80.0,
        ceiling_price: float = 800.0,
        ota_commission: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Calculate final rule-based price by evaluating all 5 rules sequentially,
        multiplying multipliers, and applying hard constraints.
        """
        mult_occupancy = self.occupancy_rule(occupancy_pct)
        mult_pace = self.pace_rule(pace)
        mult_comp = self.competitive_rule(comp_index)
        mult_event = self.calendar_rule(event_type)
        mult_inventory = self.inventory_rule(inventory_forecast)

        multipliers = {
            "occupancy": mult_occupancy,
            "pace": mult_pace,
            "competitive": mult_comp,
            "event": mult_event,
            "inventory": mult_inventory
        }

        # Combined multiplier product
        combined_mult = (
            mult_occupancy * mult_pace * mult_comp * mult_event * mult_inventory
        )

        unconstrained_price = base_price * combined_mult
        final_price, constraint_flags = self.apply_constraints(
            unconstrained_price, floor_price, ceiling_price
        )

        # OTA rate parity calculation if commission provided
        parity_info = {}
        if ota_commission is not None:
            # Default OTA price calculation (Direct price / (1 - commission))
            ota_price = round(final_price / (1.0 - ota_commission), 2)
            is_valid, max_direct = self.validate_rate_parity(final_price, ota_price, ota_commission)
            parity_info = {
                "ota_commission": ota_commission,
                "suggested_ota_price": ota_price,
                "parity_valid": is_valid,
                "max_allowed_direct": max_direct
            }

        return {
            "base_price": base_price,
            "combined_multiplier": round(combined_mult, 4),
            "multipliers_breakdown": multipliers,
            "unconstrained_price": round(unconstrained_price, 2),
            "final_price": final_price,
            "floor_price": floor_price,
            "ceiling_price": ceiling_price,
            "constraints_applied": constraint_flags,
            "rate_parity": parity_info
        }
