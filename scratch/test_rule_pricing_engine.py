"""
Test Suite & Verification Runner for Deterministic Rule-Based Pricing Engine.
"""

import unittest
import time
from rule_pricing_engine import RuleBasedPricingEngine

class TestRuleBasedPricingEngine(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.engine = RuleBasedPricingEngine()

    def test_01_occupancy_rule(self):
        """Verify 5 brackets of Occupancy-Based Pricing Rule."""
        self.assertEqual(self.engine.occupancy_rule(0.40), 0.80)  # <50% (-20%)
        self.assertEqual(self.engine.occupancy_rule(0.65), 0.90)  # <70% (-10%)
        self.assertEqual(self.engine.occupancy_rule(0.80), 1.00)  # <85% (Base)
        self.assertEqual(self.engine.occupancy_rule(0.90), 1.15)  # <95% (+15%)
        self.assertEqual(self.engine.occupancy_rule(0.98), 1.30)  # >=95% (+30%)
        print("\n[OK] [TEST 1 PASSED] Occupancy rule 5-bracket evaluation verified.")

    def test_02_pace_rule(self):
        """Verify 5 brackets of Booking Pace Rule."""
        self.assertEqual(self.engine.pace_rule(1.45), 1.25)  # >1.3 (+25%)
        self.assertEqual(self.engine.pace_rule(1.20), 1.15)  # >1.1 (+15%)
        self.assertEqual(self.engine.pace_rule(1.00), 1.00)  # >0.9 (Base)
        self.assertEqual(self.engine.pace_rule(0.80), 0.85)  # >0.7 (-15%)
        self.assertEqual(self.engine.pace_rule(0.50), 0.65)  # <=0.7 (-35%)
        print("[OK] [TEST 2 PASSED] Booking pace rule 5-bracket evaluation verified.")

    def test_03_competitive_rule(self):
        """Verify 3 brackets of Competitive Pricing Rule."""
        self.assertEqual(self.engine.competitive_rule(90.0), 1.05)   # <95 (+5% raise)
        self.assertEqual(self.engine.competitive_rule(125.0), 0.95)  # >120 (-5% lower)
        self.assertEqual(self.engine.competitive_rule(105.0), 1.00)  # ok (base)
        print("[OK] [TEST 3 PASSED] Competitive rule 3-bracket evaluation verified.")

    def test_04_calendar_rule(self):
        """Verify Event/Calendar Multipliers."""
        self.assertEqual(self.engine.calendar_rule("festival"), 1.40)
        self.assertEqual(self.engine.calendar_rule("holiday"), 1.30)
        self.assertEqual(self.engine.calendar_rule("weekend"), 1.20)
        self.assertEqual(self.engine.calendar_rule("regular_day"), 1.00)
        self.assertEqual(self.engine.calendar_rule("unknown_type"), 1.00)
        print("[OK] [TEST 4 PASSED] Calendar/Event rule multipliers verified.")

    def test_05_inventory_rule(self):
        """Verify 4 brackets of Inventory Forecast Rule."""
        self.assertEqual(self.engine.inventory_rule(0.98), 1.40)  # >95% (+40%)
        self.assertEqual(self.engine.inventory_rule(0.92), 1.25)  # >90% (+25%)
        self.assertEqual(self.engine.inventory_rule(0.80), 1.10)  # >75% (+10%)
        self.assertEqual(self.engine.inventory_rule(0.50), 1.00)  # <=75% (Base)
        print("[OK] [TEST 5 PASSED] Inventory pressure rule 4-bracket evaluation verified.")

    def test_06_combined_multiplier_engine(self):
        """Verify end-to-end price calculation with combined multipliers."""
        res = self.engine.calculate_price(
            base_price=100.0,
            occupancy_pct=0.90,     # mult = 1.15
            pace=1.20,              # mult = 1.15
            comp_index=90.0,        # mult = 1.05
            event_type="weekend",   # mult = 1.20
            inventory_forecast=0.80 # mult = 1.10
        )
        
        # Combined mult = 1.15 * 1.15 * 1.05 * 1.20 * 1.10 = 1.833075 -> R$183.31
        expected_mult = round(1.15 * 1.15 * 1.05 * 1.20 * 1.10, 4)
        self.assertEqual(res["combined_multiplier"], expected_mult)
        self.assertAlmostEqual(res["final_price"], 183.31, places=1)
        print(f"\n   -> Combined Multipliers Breakdown: {res['multipliers_breakdown']}")
        print(f"   -> Combined Multiplier Product: {res['combined_multiplier']}x")
        print(f"   -> Base Price: R$100.00 -> Final Price: R${res['final_price']:.2f}")
        print("[OK] [TEST 6 PASSED] Full combined pricing engine calculation verified.")

    def test_07_constraint_enforcement(self):
        """Verify floor price and ceiling price clamping."""
        res_floor = self.engine.calculate_price(
            base_price=100.0,
            occupancy_pct=0.40,     # mult = 0.80
            pace=0.50,              # mult = 0.65
            comp_index=125.0,       # mult = 0.95
            event_type="regular_day",# mult = 1.00
            inventory_forecast=0.50,# mult = 1.00
            floor_price=100.0,
            ceiling_price=500.0
        )
        self.assertEqual(res_floor["final_price"], 100.00)
        self.assertTrue(res_floor["constraints_applied"]["floor_triggered"])

        res_ceiling = self.engine.calculate_price(
            base_price=500.0,
            occupancy_pct=0.98,     # mult = 1.30
            pace=1.40,              # mult = 1.25
            comp_index=90.0,        # mult = 1.05
            event_type="festival",  # mult = 1.40
            inventory_forecast=0.98,# mult = 1.40
            floor_price=100.0,
            ceiling_price=800.0
        )
        self.assertEqual(res_ceiling["final_price"], 800.00)
        self.assertTrue(res_ceiling["constraints_applied"]["ceiling_triggered"])

        print("[OK] [TEST 7 PASSED] Floor price and ceiling price constraints strictly enforced.")

    def test_08_rate_parity_validation(self):
        """Verify Direct Rate <= OTA Rate * (1 - commission) constraint."""
        res = self.engine.calculate_price(
            base_price=150.0,
            occupancy_pct=0.75,
            pace=1.00,
            comp_index=100.0,
            event_type="regular_day",
            inventory_forecast=0.50,
            ota_commission=0.15 # 15% Booking.com commission
        )
        
        parity_info = res["rate_parity"]
        self.assertTrue(parity_info["parity_valid"])
        is_valid, max_direct = self.engine.validate_rate_parity(
            direct_price=res["final_price"],
            ota_price=parity_info["suggested_ota_price"],
            commission_pct=0.15
        )
        self.assertTrue(is_valid)
        print(f"   -> Rate Parity Check: Direct=R${res['final_price']:.2f} <= OTA=R${parity_info['suggested_ota_price']:.2f} * (1 - 15%)")
        print("[OK] [TEST 8 PASSED] Rate parity validation verified.")

    def test_09_performance_benchmark(self):
        """Verify performance benchmark for 1,000 price calculations under 1 second."""
        start_time = time.time()
        for i in range(1000):
            self.engine.calculate_price(
                base_price=100.0 + (i % 50),
                occupancy_pct=0.40 + (i % 60) / 100.0,
                pace=0.60 + (i % 80) / 100.0,
                comp_index=85.0 + (i % 40),
                event_type="weekend" if i % 2 == 0 else "regular_day",
                inventory_forecast=0.50 + (i % 45) / 100.0
            )
        elapsed = time.time() - start_time
        print(f"\n[OK] [PERFORMANCE SUCCESS] Processed 1,000 price calculations in {elapsed:.4f} seconds!")
        self.assertLess(elapsed, 1.0)

if __name__ == "__main__":
    unittest.main()
