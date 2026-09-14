"""
Destino Vivo RMS - Property Management System (PMS) Automated Test Suite
"""

import time
import hmac
import hashlib
import logging
import unittest
from pms_integrator import PMSIntegrator, _PMS_CACHE_STORE

class TestPMSIntegration(unittest.TestCase):

    def setUp(self):
        self.integrator = PMSIntegrator(mock_mode=True)

    def test_fetch_bookings_and_cache(self):
        res = self.integrator.fetch_bookings("HOT-001")
        self.assertEqual(res["hotel_id"], "HOT-001")
        self.assertEqual(res["occupancy"]["total_rooms"], 100)
        self.assertEqual(res["occupancy"]["occupied"], 87)
        self.assertEqual(len(res["bookings"]), 2)
        
        # Verify cached store
        self.assertIn("HOT-001", _PMS_CACHE_STORE)

    def test_sync_prices_sanity_bounds(self):
        valid_prices = {"double": 150.00, "suite": 280.00}
        res = self.integrator.sync_prices_to_pms("HOT-001", valid_prices)
        self.assertEqual(res["status"], "success")

        # Test invalid price (below floor $50)
        invalid_prices = {"double": 30.00}
        with self.assertRaises(ValueError):
            self.integrator.sync_prices_to_pms("HOT-001", invalid_prices)

    def test_webhook_hmac_verification(self):
        secret = "wh_sec_secret_123"
        payload = {"event": "booking_created", "booking": {"id": "BK999", "room_type": "double"}}
        
        valid_sig = hmac.new(secret.encode('utf-8'), str(payload).encode('utf-8'), hashlib.sha256).hexdigest()
        res = self.integrator.handle_webhook(payload, valid_sig)
        self.assertEqual(res["status"], "processed")

        # Test invalid signature
        with self.assertRaises(PermissionError):
            self.integrator.handle_webhook(payload, "invalid_sig_abc")

    def test_pms_outage_failover(self):
        # Populate cache
        self.integrator.fetch_bookings("HOT-FAILOVER")
        
        # Simulate network error
        self.integrator.mock_mode = False
        res = self.integrator.fetch_bookings("HOT-FAILOVER")
        self.assertEqual(res["hotel_id"], "HOT-FAILOVER")

    def test_load_simulation_1000_bookings(self):
        logging.disable(logging.CRITICAL)
        start_time = time.time()
        
        for i in range(1000):
            self.integrator.fetch_bookings(f"HOT-LOAD-{i%10}")

        elapsed = time.time() - start_time
        logging.disable(logging.NOTSET)
        print(f"\n[LOAD TEST SUCCESS] Processed 1,000 PMS booking requests in {elapsed:.4f} seconds!")

if __name__ == "__main__":
    unittest.main()
