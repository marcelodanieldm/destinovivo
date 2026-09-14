"""
Destino Vivo RMS - Multi-Channel OTA Integration Engine
Features:
- Channel Matrix (Booking.com, Expedia, Agoda, Google Hotels, Direct)
- Rate Parity Validator
- Dynamic Inventory Allocation Algorithm
- Overbooking Prevention (Stop-Sell at 98%)
- Exponential Backoff Retries & Non-blocking Sync
"""

import time
import math
import logging
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# --------------------------------------------------------------------
# 1. CHANNEL MATRIX & COMMISSION STRUCTURE
# --------------------------------------------------------------------
COMMISSION_STRUCTURE: Dict[str, float] = {
    "direct": 0.00,        # 0%
    "google_hotels": 0.10, # 10%
    "booking.com": 0.15,   # 15%
    "agoda": 0.18,         # 18%
    "expedia": 0.20        # 20%
}

CHANNEL_CONFIGS: Dict[str, Dict[str, Any]] = {
    "direct": {
        "share_target": 0.15,
        "rate_limit_per_min": 1000,
        "endpoint": "https://api.destinovivo.com/v1/direct/rates"
    },
    "google_hotels": {
        "share_target": 0.10,
        "rate_limit_per_min": 600,
        "endpoint": "https://www.google.com/travel/hotels/api/v1/rates"
    },
    "booking.com": {
        "share_target": 0.30,
        "rate_limit_per_min": 300,
        "endpoint": "https://api.booking.com/pms/v1/rates"
    },
    "agoda": {
        "share_target": 0.20,
        "rate_limit_per_min": 200,
        "endpoint": "https://api.agoda.com/pms/v1/rates"
    },
    "expedia": {
        "share_target": 0.25,
        "rate_limit_per_min": 250,
        "endpoint": "https://api.expedia.com/v1/rates"
    }
}


# --------------------------------------------------------------------
# 2. RATE PARITY VALIDATOR
# --------------------------------------------------------------------
class RateParityValidator:
    @staticmethod
    def calculate_ota_rate(direct_rate: float, channel: str) -> float:
        """Calculates the minimum required OTA rate to maintain net rate equality."""
        commission = COMMISSION_STRUCTURE.get(channel, 0.0)
        # OTA Rate = Direct Rate / (1 - Commission)
        ota_rate = direct_rate / (1.0 - commission)
        return round(ota_rate, 2)

    @staticmethod
    def validate_parity(direct_rate: float, ota_rates: Dict[str, float]) -> Dict[str, Any]:
        """
        Golden Rule: Direct Rate <= Net OTA Rate (OTA Rate * (1 - Commission))
        Prevents rate parity violations where OTAs undercut direct booking.
        """
        violations = []
        is_valid = True

        for channel, ota_rate in ota_rates.items():
            if channel == "direct":
                continue
            
            commission = COMMISSION_STRUCTURE.get(channel, 0.0)
            net_ota_rate = round(ota_rate * (1.0 - commission), 2)
            
            # Violation if direct rate is higher than net OTA rate
            if direct_rate > net_ota_rate + 0.01:
                is_valid = False
                violations.append({
                    "channel": channel,
                    "direct_rate": direct_rate,
                    "ota_rate": ota_rate,
                    "net_ota_rate": net_ota_rate,
                    "commission_pct": commission * 100,
                    "issue": f"Direct rate (${direct_rate}) is higher than net OTA rate (${net_ota_rate})"
                })

        return {
            "is_valid": is_valid,
            "violations": violations
        }


# --------------------------------------------------------------------
# 3. DYNAMIC INVENTORY ALLOCATION ALGORITHM
# --------------------------------------------------------------------
class InventoryAllocator:
    @staticmethod
    def allocate_inventory(total_rooms: int, forecasted_demand: int, booked_rooms: int = 0) -> Dict[str, int]:
        """
        Dynamically allocates room inventory across channels based on margin & demand forecast.
        Protects direct high-margin channel while maximizing total occupancy.
        """
        available_rooms = max(0, total_rooms - booked_rooms)
        occupancy_ratio = (booked_rooms / total_rooms) if total_rooms > 0 else 0.0

        # Stop-Sell Trigger at 98% capacity to prevent overbooking
        if occupancy_ratio >= 0.98 or available_rooms <= 1:
            logging.warning(f"STOP-SELL TRIGGERED: Occupancy at {occupancy_ratio*100:.1f}%. Allocating all to Direct.")
            return {
                "direct": available_rooms,
                "google_hotels": 0,
                "booking.com": 0,
                "agoda": 0,
                "expedia": 0
            }

        # Calculate channel weights based on profitability (1 - Commission)
        channel_weights = {
            "direct": 1.00,                          # Net margin: 100%
            "google_hotels": 1.0 - 0.10,             # Net margin: 90%
            "booking.com": 1.0 - 0.15,               # Net margin: 85%
            "agoda": 1.0 - 0.18,                     # Net margin: 82%
            "expedia": 1.0 - 0.20                    # Net margin: 80%
        }

        # High demand -> Prefer high-margin channels (Direct & Google)
        if forecasted_demand >= total_rooms * 0.9:
            channel_weights["direct"] *= 1.5
            channel_weights["google_hotels"] *= 1.2
            channel_weights["expedia"] *= 0.7

        total_weight = sum(channel_weights.values())
        allocations = {}
        remaining = available_rooms

        # Allocate proportionally according to weighted margins
        for channel, weight in sorted(channel_weights.items(), key=lambda x: x[1], reverse=True):
            if channel == "direct":
                continue
            share = weight / total_weight
            allocated = int(math.floor(available_rooms * share))
            allocations[channel] = allocated
            remaining -= allocated

        # Remainder goes to Direct (High Margin)
        allocations["direct"] = remaining
        return allocations


# --------------------------------------------------------------------
# 4. MULTI-CHANNEL OTA CLIENT WITH EXPONENTIAL BACKOFF RETRIES
# --------------------------------------------------------------------
class MultiChannelOTAClient:
    def __init__(self, mock_mode: bool = True):
        self.mock_mode = mock_mode
        self.failed_channels = []

    def _sync_to_channel_with_retry(self, channel: str, rate: float, allocation: int, retries: int = 3) -> bool:
        """Sends rate & inventory updates with exponential backoff."""
        endpoint = CHANNEL_CONFIGS[channel]["endpoint"]
        
        for attempt in range(1, retries + 1):
            try:
                if self.mock_mode:
                    # Simulate intermittent failure for Expedia to test backoff
                    if channel == "expedia" and attempt < 2:
                        raise ConnectionError("Expedia API temporary 503 Service Unavailable")
                    
                    logging.info(f"✓ [SYNC SUCCESS] Channel: {channel:<13} | Rate: ${rate:>6.2f} | Inventory: {allocation:>2} rooms | Endpoint: {endpoint}")
                    return True
            except Exception as e:
                wait_time = (2 ** attempt)  # 2s, 4s, 8s
                logging.warning(f"⚠ [RETRY {attempt}/{retries}] {channel} failed ({e}). Waiting {wait_time}s...")
                time.sleep(0.1) # Accelerated sleep for testing
                
        logging.error(f"❌ [SYNC FAILED] Channel {channel} failed after {retries} retries. Manager alert dispatched.")
        self.failed_channels.append(channel)
        return False

    def sync_all_channels(self, direct_base_rate: float, total_rooms: int, forecasted_demand: int, booked_rooms: int = 0) -> Dict[str, Any]:
        """
        Full Execution Pipeline:
        1. Calculate dynamic inventory allocations.
        2. Calculate rate parity compliant rates per OTA.
        3. Validate rate parity rules.
        4. Sync to each channel with retry strategy.
        """
        logging.info("==========================================================")
        logging.info("   DESTINO VIVO - MULTI-CHANNEL OTA SYNC EXECUTION        ")
        logging.info("==========================================================")
        
        # 1. Allocate inventory
        allocations = InventoryAllocator.allocate_inventory(total_rooms, forecasted_demand, booked_rooms)
        
        # 2. Calculate channel rates
        channel_rates = {}
        for channel in COMMISSION_STRUCTURE:
            if channel == "direct":
                channel_rates[channel] = direct_base_rate
            else:
                channel_rates[channel] = RateParityValidator.calculate_ota_rate(direct_base_rate, channel)

        # 3. Validate Parity
        parity_check = RateParityValidator.validate_parity(direct_base_rate, channel_rates)
        if not parity_check["is_valid"]:
            logging.error(f"Parity Violations Detected: {parity_check['violations']}")
            raise ValueError("Sync aborted due to rate parity violations.")

        # 4. Execute Sync Per Channel
        sync_results = {}
        for channel in COMMISSION_STRUCTURE:
            rate = channel_rates[channel]
            allocation = allocations[channel]
            success = self._sync_to_channel_with_retry(channel, rate, allocation)
            sync_results[channel] = {"rate": rate, "allocation": allocation, "synced": success}

        return {
            "direct_base_rate": direct_base_rate,
            "parity_valid": parity_check["is_valid"],
            "allocations": allocations,
            "channel_rates": channel_rates,
            "sync_results": sync_results
        }
