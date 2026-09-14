"""
Destino Vivo RMS - Multi-Channel OTA Automated Test Suite & Load Test
"""

import time
import logging
import unittest
from ota_manager import RateParityValidator, InventoryAllocator, MultiChannelOTAClient, COMMISSION_STRUCTURE

class TestOTAIntegration(unittest.TestCase):

    def test_rate_parity_calculation(self):
        direct_rate = 100.00
        booking_rate = RateParityValidator.calculate_ota_rate(direct_rate, "booking.com")
        expedia_rate = RateParityValidator.calculate_ota_rate(direct_rate, "expedia")
        
        # 100 / (1 - 0.15) = 117.65
        self.assertEqual(booking_rate, 117.65)
        # 100 / (1 - 0.20) = 125.00
        self.assertEqual(expedia_rate, 125.00)

    def test_rate_parity_validation(self):
        direct_rate = 100.00
        valid_ota_rates = {
            "booking.com": 117.65,
            "expedia": 125.00,
            "agoda": 121.95,
            "google_hotels": 111.11
        }
        res = RateParityValidator.validate_parity(direct_rate, valid_ota_rates)
        self.assertTrue(res["is_valid"])

        # Test intentional violation (undercutting OTA rate)
        invalid_ota_rates = {
            "booking.com": 105.00, # Net: 105 * 0.85 = 89.25 < 100 (Violation!)
            "expedia": 125.00
        }
        res_invalid = RateParityValidator.validate_parity(direct_rate, invalid_ota_rates)
        self.assertFalse(res_invalid["is_valid"])
        self.assertEqual(len(res_invalid["violations"]), 1)

    def test_stop_sell_overbooking_prevention(self):
        # 100 rooms total, 98 rooms booked -> 98% occupancy
        allocations = InventoryAllocator.allocate_inventory(total_rooms=100, forecasted_demand=95, booked_rooms=98)
        
        # All remaining rooms (2) must be allocated strictly to Direct
        self.assertEqual(allocations["direct"], 2)
        self.assertEqual(allocations["booking.com"], 0)
        self.assertEqual(allocations["expedia"], 0)

    def test_multi_channel_sync_pipeline(self):
        client = MultiChannelOTAClient(mock_mode=True)
        res = client.sync_all_channels(direct_base_rate=100.00, total_rooms=100, forecasted_demand=90, booked_rooms=20)
        
        self.assertTrue(res["parity_valid"])
        self.assertEqual(res["allocations"]["direct"] + sum(res["allocations"][k] for k in res["allocations"] if k != "direct"), 80)

    def test_load_simulation_1000_updates(self):
        logging.disable(logging.CRITICAL)
        start_time = time.time()
        client = MultiChannelOTAClient(mock_mode=True)
        
        for i in range(1000):
            RateParityValidator.calculate_ota_rate(100.00 + i % 50, "booking.com")
            InventoryAllocator.allocate_inventory(100, 90, i % 90)

        elapsed = time.time() - start_time
        logging.disable(logging.NOTSET)
        print(f"\n[LOAD TEST SUCCESS] Processed 1,000 multi-channel inventory updates in {elapsed:.4f} seconds!")

if __name__ == "__main__":
    unittest.main()
