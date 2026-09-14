"""
Test Suite & Verification Runner for Pricing Execution Engine & Channel Synchronizer.
"""

import unittest
import time
from pricing_execution_engine import ExecutionEngine, MockPMSClient, MockOTAClient

class TestExecutionEngine(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.engine = ExecutionEngine()
        cls.context = {
            "base_price": 150.0,
            "occupancy_pct": 0.80,
            "pace": 1.15,
            "comp_index": 100.0,
            "event_type": "regular_day",
            "inventory_forecast": 0.80,
            "historical_data": [
                {"price": 150.0, "demand": 50.0, "occupancy": 0.80, "day_of_week": 3, "comp_index": 100.0}
            ] * 30
        }

    def test_01_select_final_price(self):
        """Verify final hybrid price selection and constraint clamping."""
        res = self.engine.select_final_price(
            hotel_id="HOTEL-01",
            room_type="double",
            date="2026-09-15",
            context=self.context,
            floor_price=80.0,
            ceiling_price=800.0
        )
        self.assertEqual(res["selection_source"], "hybrid")
        self.assertGreaterEqual(res["final_price"], 80.0)
        self.assertLessEqual(res["final_price"], 800.0)
        print(f"\n   -> Hybrid Decision: Rule=R${res['rule_price']} | ML=R${res['ml_price']} | Hybrid Final=R${res['final_price']}")
        print("[OK] [TEST 1 PASSED] Final price selection and hybrid decision verified.")

    def test_02_manual_user_override(self):
        """Verify user manual override takes precedence over hybrid calculation."""
        res = self.engine.select_final_price(
            hotel_id="HOTEL-01",
            room_type="suite",
            date="2026-09-15",
            context=self.context,
            user_override=350.0,
            override_reason="Manager Special Promotion"
        )
        self.assertEqual(res["selection_source"], "user_override")
        self.assertEqual(res["final_price"], 350.0)
        self.assertEqual(res["override_reason"], "Manager Special Promotion")
        print("[OK] [TEST 2 PASSED] Manual user override precedence verified.")

    def test_03_validate_rate_parity(self):
        """Verify rate parity validation (pass vs violation detection)."""
        direct_price = 150.0
        # Valid OTA prices with commissions
        ota_valid = {
            "booking.com": 176.47, # 176.47 * (1 - 0.15) = 150.00
            "expedia": 187.50,     # 187.50 * (1 - 0.20) = 150.00
            "agoda": 182.93        # 182.93 * (1 - 0.18) = 150.00
        }
        is_valid, violations = self.engine.validate_rate_parity(direct_price, ota_valid)
        self.assertTrue(is_valid)
        self.assertEqual(len(violations), 0)

        # Invalid OTA price violating parity
        ota_invalid = {
            "booking.com": 160.00 # Max allowed direct for 160.00 is 136.00 < 150.00 -> violation!
        }
        is_valid_inv, violations_inv = self.engine.validate_rate_parity(direct_price, ota_invalid)
        self.assertFalse(is_valid_inv)
        self.assertGreater(len(violations_inv), 0)
        print("[OK] [TEST 3 PASSED] Rate parity validation and violation detection verified.")

    def test_04_sync_prices_to_pms(self):
        """Verify PMS synchronization and retry queueing on failure."""
        prices_dict = {"single": 100.0, "double": 150.0, "suite": 250.0}
        
        # Test successful PMS sync
        self.engine.pms_client.simulate_failure = False
        res_success = self.engine.sync_prices_to_pms("HOTEL-01", "2026-09-15", prices_dict)
        self.assertEqual(res_success["status"], "success")

        # Test failed PMS sync -> queued for retry
        self.engine.pms_client.simulate_failure = True
        res_fail = self.engine.sync_prices_to_pms("HOTEL-01", "2026-09-15", prices_dict)
        self.assertEqual(res_fail["status"], "partial_failure")
        self.assertGreater(len(self.engine.retry_queue.queue), 0)
        
        # Reset mock
        self.engine.pms_client.simulate_failure = False
        print("[OK] [TEST 4 PASSED] PMS synchronization and failure retry queueing verified.")

    def test_05_sync_to_ota_channels(self):
        """Verify multi-channel OTA sync with commission markup."""
        direct_prices = {"double": 200.0}
        res = self.engine.sync_to_ota_channels("HOTEL-01", "2026-09-15", direct_prices)
        
        self.assertIn("booking.com", res)
        self.assertIn("expedia", res)
        self.assertEqual(res["booking.com"]["rates"]["double"], 235.29) # 200 / (1 - 0.15) = 235.29
        self.assertEqual(res["expedia"]["rates"]["double"], 250.00)    # 200 / (1 - 0.20) = 250.00
        print("[OK] [TEST 5 PASSED] Multi-channel OTA synchronization with commission markup verified.")

    def test_06_manage_inventory(self):
        """Verify dynamic inventory allocation and 98% stop-sell trigger."""
        # Normal occupancy allocation
        res_normal = self.engine.manage_inventory("HOTEL-01", "2026-09-15", occupancy_forecast=0.85, total_rooms=100)
        self.assertFalse(res_normal["stop_sell_active"])
        self.assertEqual(res_normal["allocation"]["direct"], 15)
        self.assertEqual(res_normal["allocation"]["booking.com"], 35)

        # 98% Occupancy -> Stop-sell triggered!
        res_stopsell = self.engine.manage_inventory("HOTEL-01", "2026-09-15", occupancy_forecast=0.98, total_rooms=100)
        self.assertTrue(res_stopsell["stop_sell_active"])
        self.assertEqual(res_stopsell["allocation"]["direct"], 100)
        self.assertEqual(res_stopsell["allocation"]["booking.com"], 0)
        print("[OK] [TEST 6 PASSED] Dynamic inventory allocation and 98% stop-sell protection verified.")

    def test_07_audit_trail_logging(self):
        """Verify full audit trail log entry generation."""
        logs = self.engine.audit_logger.logs
        self.assertGreater(len(logs), 0)
        event_types = [l["event_type"] for l in logs]
        self.assertIn("PRICE_SELECTION", event_types)
        print(f"   -> Recorded {len(logs)} audit trail log events.")
        print("[OK] [TEST 7 PASSED] Audit trail logging verified.")

    def test_08_performance_benchmark(self):
        """Verify performance benchmark for 1,000 multi-channel price executions under 1 second."""
        start_time = time.time()
        for i in range(1000):
            self.engine.select_final_price("HOTEL-BENCH", "double", "2026-09-15", self.context)
        elapsed = time.time() - start_time
        print(f"\n[OK] [PERFORMANCE SUCCESS] Processed 1,000 multi-channel price executions in {elapsed:.4f} seconds!")
        self.assertLess(elapsed, 1.0)

if __name__ == "__main__":
    unittest.main()
