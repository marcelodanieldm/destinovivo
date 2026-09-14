"""
Destino Vivo RMS - 5 Continuous Learning Feedback Loops Engine
Implements:
1. Price-Demand Elasticity Learning Loop
2. Dynamic Forecast Ensemble Weight Tuning Loop
3. Competitor Reaction & Counter-Pricing Loop
4. Recommendation Acceptance & Rule Sensitivity Tuning Loop
5. Channel Net Yield Optimization & Inventory Allocation Loop
"""

import math
import logging
from datetime import datetime
from typing import Dict, Any, List, Tuple, Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("FeedbackLoopsEngine")

class FeedbackLoopsEngine:
    """Engine orchestrating the 5 Continuous Learning Feedback Loops for Destino Vivo RMS."""

    def __init__(self):
        # Initial baseline ensemble model weights
        self.model_weights = {
            "arima": 0.15,
            "prophet": 0.30,
            "lstm": 0.35,
            "xgb": 0.20
        }
        # Initial channel allocations
        self.channel_allocation_shares = {
            "direct": 0.15,
            "booking.com": 0.35,
            "expedia": 0.30,
            "agoda": 0.20
        }
        # Initial rule sensitivity thresholds
        self.rule_sensitivity = {
            "occupancy_threshold_high": 0.85,
            "pace_threshold_high": 1.10,
            "comp_trigger_cheap": 95.0
        }

    def cycle1_update_elasticity(self, price_history: List[float], demand_history: List[float]) -> float:
        """
        Cycle 1: Price-Demand Elasticity Learning Loop.
        Re-estimates elasticity coefficient beta based on actual booking conversions.
        """
        if len(price_history) < 5 or len(price_history) != len(demand_history):
            return -1.40  # Fallback default

        log_p = [math.log(max(1.0, p)) for p in price_history]
        log_d = [math.log(max(0.1, d)) for d in demand_history]

        n = len(log_p)
        mean_p = sum(log_p) / n
        mean_d = sum(log_d) / n

        num = sum((log_p[i] - mean_p) * (log_d[i] - mean_d) for i in range(n))
        den = sum((log_p[i] - mean_p) ** 2 for i in range(n))

        if abs(den) < 1e-9:
            return -1.40

        updated_elasticity = round(max(-3.0, min(-0.3, num / den)), 4)
        logger.info(f"[CYCLE 1] Elasticity updated to {updated_elasticity}")
        return updated_elasticity

    def cycle2_tune_ensemble_weights(self, model_mapes: Dict[str, float]) -> Dict[str, float]:
        """
        Cycle 2: Forecast Accuracy & Dynamic Ensemble Weight Tuning Loop.
        Adjusts ARIMA, Prophet, LSTM, and XGBoost weights inversely proportional to trailing MAPE.
        """
        if not model_mapes:
            return self.model_weights

        # Inverse MAPE weights (lower MAPE -> higher weight)
        inv_mapes = {m: 1.0 / max(0.01, mape) for m, mape in model_mapes.items()}
        total_inv = sum(inv_mapes.values())

        new_weights = {m: round(inv_mapes[m] / total_inv, 4) for m in inv_mapes}
        self.model_weights = new_weights
        logger.info(f"[CYCLE 2] Dynamic Ensemble Weights updated: {new_weights}")
        return new_weights

    def cycle3_adapt_competitor_reaction(self, comp_moves: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Cycle 3: Competitor Reaction & Counter-Pricing Loop.
        Learns competitor price sensitivity and updates market index multipliers.
        """
        if not comp_moves:
            return {"comp_reaction_multiplier": 1.05}

        # Analyze average competitor rate shifts
        comp_deltas = [m.get("comp_price_change_pct", 0.0) for m in comp_moves]
        avg_comp_delta = sum(comp_deltas) / len(comp_deltas)

        if avg_comp_delta > 5.0:
            # Competitors raising prices -> we can capture higher margin
            reaction_mult = 1.08
        elif avg_comp_delta < -5.0:
            # Competitor price war -> protect market share
            reaction_mult = 1.02
        else:
            reaction_mult = 1.05

        logger.info(f"[CYCLE 3] Competitor reaction multiplier adjusted to {reaction_mult}x (Avg Comp Shift: {avg_comp_delta:+.2f}%)")
        return {"comp_reaction_multiplier": reaction_mult, "avg_comp_shift_pct": round(avg_comp_delta, 2)}

    def cycle4_tune_rule_bounds(self, manual_overrides: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Cycle 4: Recommendation Acceptance & Rule Sensitivity Tuning Loop.
        Self-adjusts rule thresholds when manual overrides cluster on specific days or prices.
        """
        if len(manual_overrides) >= 3:
            # High overrides indicate rule boundaries are too aggressive -> adjust threshold upward
            self.rule_sensitivity["occupancy_threshold_high"] = min(0.90, self.rule_sensitivity["occupancy_threshold_high"] + 0.02)
            self.rule_sensitivity["pace_threshold_high"] = min(1.20, self.rule_sensitivity["pace_threshold_high"] + 0.05)
            logger.info(f"[CYCLE 4] High overrides detected. Self-tuned rule thresholds: {self.rule_sensitivity}")
        
        return self.rule_sensitivity

    def cycle5_optimize_channel_shares(self, channel_net_margins: Dict[str, float]) -> Dict[str, float]:
        """
        Cycle 5: Channel Net Yield Optimization Loop.
        Re-allocates inventory shares to channels yielding highest net margin.
        """
        if not channel_net_margins:
            return self.channel_allocation_shares

        total_margin = sum(channel_net_margins.values())
        if total_margin <= 0:
            return self.channel_allocation_shares

        optimized_shares = {c: round(channel_net_margins[c] / total_margin, 4) for c in channel_net_margins}
        self.channel_allocation_shares = optimized_shares
        logger.info(f"[CYCLE 5] Inventory Channel Shares optimized: {optimized_shares}")
        return optimized_shares

    def run_all_feedback_cycles(self, feedback_data: Dict[str, Any]) -> Dict[str, Any]:
        """Executes all 5 continuous learning feedback loops sequentially."""
        res_cycle1 = self.cycle1_update_elasticity(
            feedback_data.get("price_history", []),
            feedback_data.get("demand_history", [])
        )
        res_cycle2 = self.cycle2_tune_ensemble_weights(feedback_data.get("model_mapes", {}))
        res_cycle3 = self.cycle3_adapt_competitor_reaction(feedback_data.get("comp_moves", []))
        res_cycle4 = self.cycle4_tune_rule_bounds(feedback_data.get("manual_overrides", []))
        res_cycle5 = self.cycle5_optimize_channel_shares(feedback_data.get("channel_net_margins", {}))

        return {
            "timestamp": datetime.now().isoformat(),
            "cycle1_updated_elasticity": res_cycle1,
            "cycle2_tuned_weights": res_cycle2,
            "cycle3_comp_reaction": res_cycle3,
            "cycle4_tuned_rules": res_cycle4,
            "cycle5_channel_shares": res_cycle5
        }
