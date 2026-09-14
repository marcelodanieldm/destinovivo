"""
Destino Vivo RMS - Pricing Execution Engine & Channel Synchronizer
Handles Final Price Selection, Rate Parity Validation, PMS Sync, OTA Multi-Channel Updates,
Inventory Allocation, Retry Queueing, and Audit Logging.
"""

import time
import math
import logging
from datetime import datetime
from typing import Dict, Any, List, Tuple, Optional

from rule_pricing_engine import RuleBasedPricingEngine
from ml_pricing_engine import MLPricingEngine

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("PricingExecutionEngine")

class MockPMSClient:
    """Mock PMS Client simulating external PMS HTTP API."""
    def __init__(self, simulate_failure: bool = False):
        self.simulate_failure = simulate_failure

    def update_room_price(self, hotel_id: str, room_type: str, date: str, price: float) -> Dict[str, Any]:
        if self.simulate_failure:
            return {"status_code": 503, "error": "PMS Service Unavailable (503)"}
        return {"status_code": 200, "message": f"Successfully updated {room_type} price to R${price:.2f}"}

class MockOTAClient:
    """Mock OTA Client simulating external OTA Channel Manager API."""
    def __init__(self, channel_name: str, simulate_failure: bool = False):
        self.channel_name = channel_name
        self.simulate_failure = simulate_failure

    def update_rates(self, hotel_id: str, date: str, rates: Dict[str, float]) -> Dict[str, Any]:
        if self.simulate_failure:
            return {"status_code": 500, "error": f"{self.channel_name} Gateway Timeout"}
        return {"status_code": 200, "message": f"{self.channel_name} rates updated successfully"}

class AuditLogger:
    """Audit Trail Logger recording all pricing decisions and channel sync events."""
    def __init__(self):
        self.logs: List[Dict[str, Any]] = []

    def log_event(self, event_type: str, details: Dict[str, Any]):
        entry = {
            "id": f"LOG-{len(self.logs)+1:05d}",
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "details": details
        }
        self.logs.append(entry)
        return entry

class RetryQueue:
    """In-memory Retry Queue for failed external API synchronizations."""
    def __init__(self):
        self.queue: List[Dict[str, Any]] = []

    def add_retry(self, channel: str, hotel_id: str, date: str, payload: Dict[str, Any], error: str):
        item = {
            "retry_id": f"RETRY-{len(self.queue)+1:04d}",
            "channel": channel,
            "hotel_id": hotel_id,
            "date": date,
            "payload": payload,
            "error": error,
            "attempts": 1,
            "next_retry": datetime.now().isoformat()
        }
        self.queue.append(item)
        logger.warning(f"Queued retry {item['retry_id']} for channel '{channel}' due to error: {error}")
        return item

class ExecutionEngine:
    """End-to-End Pricing Execution & Multi-Channel Synchronization Engine."""

    OTA_COMMISSIONS = {
        "booking.com": 0.15,      # 15%
        "expedia": 0.20,          # 20%
        "agoda": 0.18,            # 18%
        "google_hotels": 0.10,    # 10%
        "direct": 0.00            # 0%
    }

    def __init__(self):
        self.rule_engine = RuleBasedPricingEngine()
        self.ml_engine = MLPricingEngine()
        self.audit_logger = AuditLogger()
        self.retry_queue = RetryQueue()
        
        self.pms_client = MockPMSClient()
        self.ota_clients = {
            "booking.com": MockOTAClient("Booking.com"),
            "expedia": MockOTAClient("Expedia"),
            "agoda": MockOTAClient("Agoda"),
            "google_hotels": MockOTAClient("Google Hotels")
        }

    def select_final_price(
        self,
        hotel_id: str,
        room_type: str,
        date: str,
        context: Dict[str, Any],
        floor_price: float = 80.0,
        ceiling_price: float = 800.0,
        user_override: Optional[float] = None,
        override_reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Calculates Rule-Based price and ML-Optimized price, determines Hybrid price,
        applies user manual override if present, and clamps to absolute floor/ceiling.
        """
        base_price = context.get("base_price", 150.0)
        occupancy_pct = context.get("occupancy_pct", 0.75)
        pace = context.get("pace", 1.0)
        comp_index = context.get("comp_index", 100.0)
        event_type = context.get("event_type", "regular_day")
        inventory_forecast = context.get("inventory_forecast", 0.75)
        historical_data = context.get("historical_data", [])

        # 1. Rule Engine calculation
        rule_res = self.rule_engine.calculate_price(
            base_price=base_price,
            occupancy_pct=occupancy_pct,
            pace=pace,
            comp_index=comp_index,
            event_type=event_type,
            inventory_forecast=inventory_forecast,
            floor_price=floor_price,
            ceiling_price=ceiling_price
        )
        rule_price = rule_res["final_price"]

        # 2. ML Engine calculation
        ml_res = self.ml_engine.calculate_optimal_price(
            hotel_id=hotel_id,
            room_type=room_type,
            date=date,
            historical_data=historical_data,
            base_demand=context.get("base_demand", 50.0),
            reference_price=base_price,
            floor_price=floor_price,
            ceiling_price=ceiling_price,
            total_rooms=context.get("total_rooms", 100)
        )
        ml_price = ml_res["ml_optimization"]["optimal_price"]

        # 3. Hybrid price blending (50/50 weighted blend of Rule & ML)
        hybrid_price = round(0.50 * rule_price + 0.50 * ml_price, 2)

        # 4. Handle manual override or select hybrid
        if user_override is not None:
            final_price = user_override
            selection_source = "user_override"
        else:
            final_price = hybrid_price
            selection_source = "hybrid"

        # 5. Apply hard constraints
        clamped_price = round(max(floor_price, min(ceiling_price, final_price)), 2)

        decision = {
            "hotel_id": hotel_id,
            "room_type": room_type,
            "date": date,
            "rule_price": rule_price,
            "ml_price": ml_price,
            "hybrid_price": hybrid_price,
            "user_override": user_override,
            "override_reason": override_reason,
            "selection_source": selection_source,
            "final_price": clamped_price,
            "floor_price": floor_price,
            "ceiling_price": ceiling_price
        }

        self.audit_logger.log_event("PRICE_SELECTION", decision)
        return decision

    def validate_rate_parity(self, direct_price: float, ota_current_prices: Dict[str, float]) -> Tuple[bool, List[str]]:
        """
        Validates rate parity across OTA channels.
        Golden Rule: Direct Rate <= OTA Rate * (1 - commission %)
        """
        violations = []
        for ota, ota_price in ota_current_prices.items():
            commission = self.OTA_COMMISSIONS.get(ota.lower(), 0.15)
            max_allowed_direct = ota_price * (1.0 - commission)
            
            if direct_price > (max_allowed_direct + 0.01):
                violations.append(
                    f"{ota} violates parity: Direct R${direct_price:.2f} > Max Allowed R${max_allowed_direct:.2f} (OTA R${ota_price:.2f} less {commission*100}% comm)"
                )

        is_valid = len(violations) == 0
        return is_valid, violations

    def sync_prices_to_pms(self, hotel_id: str, date: str, prices_dict: Dict[str, float]) -> Dict[str, Any]:
        """Synchronizes final room prices to Property Management System (PMS)."""
        sync_results = {}
        success_count = 0
        
        for room_type, price in prices_dict.items():
            resp = self.pms_client.update_room_price(hotel_id, room_type, date, price)
            if resp.get("status_code") == 200:
                sync_results[room_type] = {"status": "success", "price": price}
                success_count += 1
                self.audit_logger.log_event("PMS_SYNC_SUCCESS", {"hotel_id": hotel_id, "room_type": room_type, "date": date, "price": price})
            else:
                error_msg = resp.get("error", "Unknown PMS error")
                sync_results[room_type] = {"status": "failed", "error": error_msg}
                self.audit_logger.log_event("PMS_SYNC_FAILED", {"hotel_id": hotel_id, "room_type": room_type, "date": date, "error": error_msg})
                self.retry_queue.add_retry("pms", hotel_id, date, {room_type: price}, error_msg)

        return {
            "status": "success" if success_count == len(prices_dict) else "partial_failure",
            "total_synced": success_count,
            "total_requested": len(prices_dict),
            "details": sync_results
        }

    def sync_to_ota_channels(self, hotel_id: str, date: str, direct_prices: Dict[str, float]) -> Dict[str, Any]:
        """Calculates commission-inclusive rates and synchronizes across all OTA channels."""
        channel_results = {}
        
        for ota_name, client in self.ota_clients.items():
            commission = self.OTA_COMMISSIONS.get(ota_name, 0.15)
            # Add commission markup: OTA Rate = Direct Price / (1 - commission)
            ota_rates = {
                r_type: round(price / (1.0 - commission), 2) for r_type, price in direct_prices.items()
            }
            
            resp = client.update_rates(hotel_id, date, ota_rates)
            if resp.get("status_code") == 200:
                channel_results[ota_name] = {"status": "success", "rates": ota_rates}
                self.audit_logger.log_event("OTA_SYNC_SUCCESS", {"hotel_id": hotel_id, "channel": ota_name, "date": date, "rates": ota_rates})
            else:
                error_msg = resp.get("error", "Unknown OTA error")
                channel_results[ota_name] = {"status": "failed", "error": error_msg}
                self.audit_logger.log_event("OTA_SYNC_FAILED", {"hotel_id": hotel_id, "channel": ota_name, "date": date, "error": error_msg})
                self.retry_queue.add_retry(ota_name, hotel_id, date, ota_rates, error_msg)

        return channel_results

    def manage_inventory(self, hotel_id: str, date: str, occupancy_forecast: float, total_rooms: int = 100) -> Dict[str, Any]:
        """
        Allocates available room inventory across channels.
        Triggers 100% Direct Stop-Sell on OTAs when occupancy forecast >= 98%.
        """
        # Stop-sell protection threshold at 98% occupancy
        if occupancy_forecast >= 0.98:
            logger.info(f"Stop-sell protection activated for Hotel {hotel_id} on {date} (Occupancy: {occupancy_forecast*100:.1f}%)")
            allocation = {
                "direct": total_rooms,
                "booking.com": 0,
                "expedia": 0,
                "agoda": 0,
                "google_hotels": 0
            }
            return {
                "stop_sell_active": True,
                "total_rooms": total_rooms,
                "occupancy_forecast": occupancy_forecast,
                "allocation": allocation
            }

        # Baseline channel share allocation
        direct_rooms = int(total_rooms * 0.15)
        booking_rooms = int(total_rooms * 0.35)
        expedia_rooms = int(total_rooms * 0.30)
        agoda_rooms = int(total_rooms * 0.20)

        allocation = {
            "direct": direct_rooms,
            "booking.com": booking_rooms,
            "expedia": expedia_rooms,
            "agoda": agoda_rooms
        }

        # Normalize allocations if total exceeds physical total_rooms
        total_allocated = sum(allocation.values())
        if total_allocated > total_rooms:
            scale = total_rooms / float(total_allocated)
            allocation = {k: int(v * scale) for k, v in allocation.items()}

        return {
            "stop_sell_active": False,
            "total_rooms": total_rooms,
            "occupancy_forecast": occupancy_forecast,
            "allocation": allocation
        }
