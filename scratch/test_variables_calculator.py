"""
Destino Vivo RMS - 100+ Variables Engine Automated Unit & Load Test Suite
"""

import time
import unittest
from datetime import date
from variables_calculator import VariablesCalculator

class TestVariablesEngine(unittest.TestCase):

    def setUp(self):
        self.calc = VariablesCalculator(mock_mode=True)
        self.pms_data = {"occupancy": {"total_rooms": 100, "occupied": 85, "available": 15}, "bookings": [1, 2, 3, 4, 5]}
        self.comp_data = {"average_competitor_price": 140.00, "our_price": 138.00}
        self.weather_data = {"temp": 25.0, "rain_prob": 5.0, "wind": 10.0}
        self.target_date = date(2026, 9, 15)

    def test_internal_variables(self):
        vars_dict = self.calc.calculate_internal_variables(self.pms_data)
        self.assertEqual(vars_dict["rooms_total"], 100)
        self.assertEqual(vars_dict["rooms_occupied"], 85)
        self.assertEqual(vars_dict["occupancy_rate"], 85.0)
        self.assertIn("occupancy_same_day_last_year", vars_dict)

    def test_external_variables(self):
        vars_dict = self.calc.calculate_external_variables(self.comp_data, self.weather_data, self.target_date)
        self.assertEqual(vars_dict["competitive_index"], 98.57) # (138 / 140) * 100
        self.assertIn("google_searches_trend", vars_dict)
        self.assertEqual(vars_dict["day_of_week"], 1) # Tuesday

    def test_derived_variables(self):
        internal = self.calc.calculate_internal_variables(self.pms_data)
        external = self.calc.calculate_external_variables(self.comp_data, self.weather_data, self.target_date)
        derived = self.calc.calculate_derived_variables(internal, external)
        
        self.assertIn("optimal_price_ml", derived)
        self.assertGreater(derived["optimal_price_ml"], 0)
        self.assertIn("cancellation_risk_score", derived)

    def test_complete_pipeline_and_validation(self):
        res = self.calc.calculate_all_variables("HOT-001", self.target_date, self.pms_data, self.comp_data, self.weather_data)
        self.assertGreaterEqual(len(res), 50)
        self.assertEqual(res["hotel_id"], "HOT-001")

    def test_load_simulation_100_hotels(self):
        start = time.time()
        for i in range(100):
            self.calc.calculate_all_variables(f"HOT-{i}", self.target_date, self.pms_data, self.comp_data, self.weather_data)
        elapsed = time.time() - start
        print(f"\n[LOAD TEST SUCCESS] Generated 100+ variables for 100 hotels in {elapsed:.4f} seconds!")

if __name__ == "__main__":
    unittest.main()
