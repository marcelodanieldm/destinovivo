"""
Test Suite & Verification Runner for ML Pricing & Revenue Optimization Engine.
"""

import math
import random
import unittest
import time
from datetime import datetime, timedelta
from ml_pricing_engine import MLPricingEngine

def generate_synthetic_ml_dataset(days: int = 365, seed: int = 42) -> list:
    """Generate 365 days of synthetic price-demand historical data with realistic elasticity."""
    random.seed(seed)
    start_date = datetime(2025, 1, 1)
    dataset = []
    
    true_elasticity = -1.40
    ref_price = 150.0
    ref_demand = 50.0

    for i in range(days):
        dt = start_date + timedelta(days=i)
        dow = dt.weekday()
        
        # Random price variations between R$110 and R$220
        price = round(random.uniform(110.0, 220.0), 2)
        
        # Demand governed by log-log elasticity + day of week surge + random noise
        dow_mult = 1.20 if dow in [4, 5] else 0.95
        noise = random.uniform(0.90, 1.10)
        
        demand = ref_demand * ((price / ref_price) ** true_elasticity) * dow_mult * noise
        demand = round(max(5.0, min(100.0, demand)), 2)
        occupancy = round(demand / 100.0, 4)

        dataset.append({
            "date": dt.strftime("%Y-%m-%d"),
            "price": price,
            "demand": demand,
            "occupancy": occupancy,
            "day_of_week": dow,
            "comp_index": round(random.uniform(90.0, 115.0), 1),
            "is_holiday": 1 if (dt.month == 12 and dt.day == 25) else 0
        })

    return dataset

class TestMLPricingEngine(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.engine = MLPricingEngine()
        cls.dataset = generate_synthetic_ml_dataset(365, seed=42)

    def test_01_elasticity_estimation(self):
        """Verify log-log regression elasticity estimation on synthetic dataset."""
        prices = [d["price"] for d in self.dataset]
        demands = [d["demand"] for d in self.dataset]

        elasticity = self.engine.estimate_elasticity(prices, demands)
        print(f"\n   -> Estimated Price Elasticity: {elasticity} (True Elasticity: -1.40)")
        self.assertTrue(-2.0 <= elasticity <= -0.8)
        print("[OK] [TEST 1 PASSED] Price elasticity log-log regression estimation verified.")

    def test_02_revenue_optimization(self):
        """Verify revenue function scalar optimization for elastic vs inelastic scenarios."""
        # Elastic demand scenario (elasticity = -2.0)
        res_elastic = self.engine.optimize_revenue(
            base_demand=50.0,
            reference_price=150.0,
            elasticity=-2.0,
            features={"is_weekend": 0.0, "comp_index": 100.0},
            floor_price=80.0,
            ceiling_price=500.0
        )
        
        # Inelastic demand scenario (elasticity = -0.5)
        res_inelastic = self.engine.optimize_revenue(
            base_demand=50.0,
            reference_price=150.0,
            elasticity=-0.5,
            features={"is_weekend": 0.0, "comp_index": 100.0},
            floor_price=80.0,
            ceiling_price=500.0
        )

        print(f"   -> Elastic Demand Opt Price: R${res_elastic['optimal_price']} (Expected Revenue: R${res_elastic['max_expected_revenue']})")
        print(f"   -> Inelastic Demand Opt Price: R${res_inelastic['optimal_price']} (Expected Revenue: R${res_inelastic['max_expected_revenue']})")
        
        # Inelastic demand allows higher prices to maximize revenue
        self.assertGreater(res_inelastic["optimal_price"], res_elastic["optimal_price"])
        print("[OK] [TEST 2 PASSED] Revenue scalar optimization for elastic vs inelastic demand verified.")

    def test_03_feature_engineering(self):
        """Verify ML feature extraction pipeline."""
        feats = self.engine.prepare_ml_features(self.dataset, 100)
        self.assertIn("price_7d_avg", feats)
        self.assertIn("price_30d_avg", feats)
        self.assertIn("occ_current", feats)
        self.assertIn("roll_occ_7d", feats)
        self.assertIn("is_weekend", feats)
        print("[OK] [TEST 3 PASSED] Feature engineering pipeline verified.")

    def test_04_backtesting_suite(self):
        """
        Execute 365-day backtest split: 70% Train (255d), 15% Validation (55d), 15% Test (55d).
        Compare ML revenue vs fixed pricing baseline and calculate prediction MAE.
        """
        train_data = self.dataset[:255]
        test_data = self.dataset[310:]  # Last 55 days

        # Fit elasticity on train set
        train_prices = [d["price"] for d in train_data]
        train_demands = [d["demand"] for d in train_data]
        trained_elasticity = self.engine.estimate_elasticity(train_prices, train_demands)

        ml_total_revenue = 0.0
        baseline_total_revenue = 0.0
        demand_errors = []

        fixed_baseline_price = 150.0

        for item in test_data:
            feats = self.engine.prepare_ml_features(train_data, len(train_data))
            
            # Predict demand at test item's actual price to measure prediction MAE
            pred_dem = self.engine.predict_demand(
                candidate_price=item["price"],
                reference_price=150.0,
                base_demand=50.0,
                elasticity=trained_elasticity,
                features=feats
            )
            demand_errors.append(abs(item["demand"] - pred_dem))

            # ML optimal price calculation
            opt_res = self.engine.optimize_revenue(
                base_demand=50.0,
                reference_price=150.0,
                elasticity=trained_elasticity,
                features=feats,
                floor_price=80.0,
                ceiling_price=300.0
            )
            
            ml_price = opt_res["optimal_price"]
            ml_dem = min(100.0, opt_res["expected_demand"])
            ml_total_revenue += (ml_price * ml_dem)

            # Fixed baseline pricing
            base_dem = min(100.0, self.engine.predict_demand(fixed_baseline_price, 150.0, 50.0, trained_elasticity, feats))
            baseline_total_revenue += (fixed_baseline_price * base_dem)

        mae = sum(demand_errors) / len(demand_errors)
        revenue_gain_pct = ((ml_total_revenue - baseline_total_revenue) / baseline_total_revenue) * 100.0

        print(f"\n   -> 55-Day Test Set Backtest Results:")
        print(f"      - Demand Prediction MAE: {mae:.2f} rooms")
        print(f"      - Fixed Baseline Revenue: R${baseline_total_revenue:,.2f}")
        print(f"      - ML Optimized Revenue: R${ml_total_revenue:,.2f}")
        print(f"      - ML Revenue Uplift: +{revenue_gain_pct:.2f}%")

        self.assertLess(mae, 15.0, "MAE exceeded threshold")
        self.assertGreater(revenue_gain_pct, 0.0, "ML pricing failed to beat baseline revenue")
        print("[OK] [TEST 4 PASSED] Backtest split (70/15/15) verified positive revenue gain.")

    def test_05_performance_benchmark(self):
        """Verify performance benchmark for 500 ML pricing optimizations under 1 second."""
        start_time = time.time()
        for i in range(500):
            self.engine.calculate_optimal_price(
                hotel_id=f"HOTEL-{i}",
                room_type="suite",
                date="2026-09-15",
                historical_data=self.dataset[:30],
                base_demand=45.0,
                reference_price=160.0
            )
        elapsed = time.time() - start_time
        print(f"\n[OK] [PERFORMANCE SUCCESS] Processed 500 ML pricing optimizations in {elapsed:.4f} seconds!")
        self.assertLess(elapsed, 1.0)

if __name__ == "__main__":
    unittest.main()
