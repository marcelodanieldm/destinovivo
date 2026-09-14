"""
Destino Vivo RMS - Machine Learning Pricing & Revenue Optimization Engine
Estimates price elasticity of demand via log-log OLS regression and maximizes expected revenue R(P) = P * Demand(P).
"""

import math
import random
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple, Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("MLPricingEngine")

class MLPricingEngine:
    """Machine Learning Pricing Engine for Revenue Maximization."""

    def __init__(self, default_elasticity: float = -1.5):
        self.default_elasticity = default_elasticity

    @staticmethod
    def estimate_elasticity(prices: List[float], demands: List[float]) -> float:
        """
        Estimate price elasticity using log-log linear regression:
        ln(demand) = alpha + beta * ln(price)
        where beta represents price elasticity.
        """
        if len(prices) < 5 or len(prices) != len(demands):
            return -1.5  # Fallback standard elasticity for hospitality

        # Log transform with non-zero bounds
        log_p = [math.log(max(1.0, p)) for p in prices]
        log_d = [math.log(max(0.1, d)) for d in demands]

        n = len(log_p)
        mean_p = sum(log_p) / n
        mean_d = sum(log_d) / n

        # Ordinary Least Squares (OLS) slope formula
        numerator = sum((log_p[i] - mean_p) * (log_d[i] - mean_d) for i in range(n))
        denominator = sum((log_p[i] - mean_p) ** 2 for i in range(n))

        if abs(denominator) < 1e-9:
            return -1.5

        beta = numerator / denominator
        # Bound elasticity to realistic hospitality range (-3.0 to -0.3)
        bounded_elasticity = max(-3.0, min(-0.3, beta))
        return round(bounded_elasticity, 4)

    @staticmethod
    def prepare_ml_features(historical_series: List[Dict[str, Any]], target_idx: int) -> Dict[str, float]:
        """Extract lag prices, rolling occupancy, pace, competitive index, and calendar drivers."""
        if target_idx < 30:
            padding_len = 30 - target_idx
            first_val = historical_series[0] if historical_series else {"price": 150.0, "demand": 50.0, "occupancy": 0.70}
            series = [first_val] * padding_len + historical_series[:target_idx]
            curr_idx = 29
        else:
            series = historical_series[:target_idx]
            curr_idx = len(series) - 1

        recent_prices = [s["price"] for s in series]
        recent_occ = [s["occupancy"] for s in series]

        # Price history
        price_7d_avg = sum(recent_prices[-7:]) / 7.0
        price_30d_avg = sum(recent_prices[-30:]) / 30.0

        # Occupancy & pace
        occ_current = recent_occ[curr_idx]
        roll_occ_7d = sum(recent_occ[-7:]) / 7.0

        current_item = series[curr_idx]
        dow = current_item.get("day_of_week", 3)
        comp_index = current_item.get("comp_index", 100.0)

        return {
            "price_7d_avg": round(price_7d_avg, 2),
            "price_30d_avg": round(price_30d_avg, 2),
            "occ_current": round(occ_current, 4),
            "roll_occ_7d": round(roll_occ_7d, 4),
            "comp_index": float(comp_index),
            "is_weekend": 1.0 if dow in [5, 6] else 0.0,
            "is_holiday": float(current_item.get("is_holiday", 0))
        }

    def predict_demand(
        self,
        candidate_price: float,
        reference_price: float,
        base_demand: float,
        elasticity: float,
        features: Dict[str, float]
    ) -> float:
        """
        Predict expected demand for a given candidate price point using elasticity model:
        Demand(P) = Base_Demand * (P / P_ref) ^ elasticity * Feature_Modifiers
        """
        price_ratio = max(0.2, candidate_price / max(1.0, reference_price))
        elasticity_effect = price_ratio ** elasticity

        # Feature modifiers (Weekend & Event boost)
        weekend_boost = 1.10 if features.get("is_weekend", 0.0) > 0.5 else 1.0
        comp_boost = 1.05 if features.get("comp_index", 100.0) > 110.0 else 1.0

        predicted_demand = base_demand * elasticity_effect * weekend_boost * comp_boost
        return max(0.0, predicted_demand)

    def optimize_revenue(
        self,
        base_demand: float,
        reference_price: float,
        elasticity: float,
        features: Dict[str, float],
        floor_price: float = 80.0,
        ceiling_price: float = 800.0,
        total_rooms: int = 100
    ) -> Dict[str, Any]:
        """
        Golden-Section Search Bounded Optimizer maximizing Expected Revenue:
        Revenue(Price) = Price * min(Total_Rooms, Demand(Price))
        subject to Floor_Price <= Price <= Ceiling_Price.
        """
        def revenue_function(p: float) -> float:
            dem = self.predict_demand(p, reference_price, base_demand, elasticity, features)
            actual_sold = min(float(total_rooms), dem)
            return p * actual_sold

        # Golden-section search algorithm
        a, b = floor_price, ceiling_price
        phi = (math.sqrt(5) - 1) / 2  # ~0.618
        
        c = b - phi * (b - a)
        d = a + phi * (b - a)

        iterations = 30
        for _ in range(iterations):
            if revenue_function(c) > revenue_function(d):
                b = d
            else:
                a = c

            c = b - phi * (b - a)
            d = a + phi * (b - a)

        optimal_price = (a + b) / 2.0
        optimal_price = round(max(floor_price, min(ceiling_price, optimal_price)), 2)

        opt_demand = self.predict_demand(optimal_price, reference_price, base_demand, elasticity, features)
        opt_sold = min(float(total_rooms), opt_demand)
        max_revenue = round(optimal_price * opt_sold, 2)

        return {
            "optimal_price": optimal_price,
            "expected_demand": round(opt_demand, 2),
            "expected_rooms_sold": round(opt_sold, 2),
            "max_expected_revenue": max_revenue,
            "elasticity_used": elasticity,
            "reference_price": reference_price,
            "floor_price": floor_price,
            "ceiling_price": ceiling_price
        }

    def calculate_optimal_price(
        self,
        hotel_id: str,
        room_type: str,
        date: str,
        historical_data: List[Dict[str, Any]],
        base_demand: float = 50.0,
        reference_price: float = 150.0,
        floor_price: float = 80.0,
        ceiling_price: float = 800.0,
        total_rooms: int = 100
    ) -> Dict[str, Any]:
        """Full ML pricing pipeline: Estimate elasticity -> extract features -> optimize revenue."""
        
        prices = [d["price"] for d in historical_data] if historical_data else []
        demands = [d["demand"] for d in historical_data] if historical_data else []

        elasticity = self.estimate_elasticity(prices, demands)
        features = self.prepare_ml_features(historical_data, len(historical_data))

        opt_res = self.optimize_revenue(
            base_demand=base_demand,
            reference_price=reference_price,
            elasticity=elasticity,
            features=features,
            floor_price=floor_price,
            ceiling_price=ceiling_price,
            total_rooms=total_rooms
        )

        return {
            "hotel_id": hotel_id,
            "room_type": room_type,
            "target_date": date,
            "timestamp": datetime.now().isoformat(),
            "ml_optimization": opt_res,
            "features": features
        }
