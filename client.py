"""
Autonomous Agentic Recurring Subscription Governance & Price Hike Autopilot (Zero External Dependencies)
Detects recurring periodicity, stealth price hikes, zombie seats, and generates cancellation workflows.
"""
import time
import math
import json
from typing import Dict, Any, List, Optional

class RecurrentSubscriptionAutopilot:
    def __init__(self, zombie_inactive_days_threshold: int = 45):
        self.zombie_threshold = zombie_inactive_days_threshold
        self.known_subscriptions: Dict[str, Dict[str, Any]] = {}

    def analyze_transaction_stream(
        self,
        transactions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Parses bank or card transactions, identifies recurring cadence (MONTHLY, ANNUAL, WEEKLY),
        and tallies monthly burn rate.
        """
        by_vendor: Dict[str, List[Dict[str, Any]]] = {}
        for tx in transactions:
            vendor = tx.get("vendor", "unknown").strip().title()
            by_vendor.setdefault(vendor, []).append(tx)

        subscriptions = []
        total_monthly_burn = 0.0

        for vendor, txs in by_vendor.items():
            if len(txs) < 2:
                continue

            # Sort by date/timestamp
            sorted_txs = sorted(txs, key=lambda x: x.get("timestamp", 0))
            amounts = [float(t.get("amount", 0.0)) for t in sorted_txs]
            timestamps = [float(t.get("timestamp", 0)) for t in sorted_txs]

            # Calculate day intervals between transactions
            intervals_days = []
            for i in range(1, len(timestamps)):
                diff_days = (timestamps[i] - timestamps[i-1]) / 86400.0
                intervals_days.append(diff_days)

            avg_interval = sum(intervals_days) / len(intervals_days) if intervals_days else 30.0

            cadence = "UNKNOWN"
            normalized_monthly_cost = amounts[-1]

            if 6.0 <= avg_interval <= 8.5:
                cadence = "WEEKLY"
                normalized_monthly_cost = amounts[-1] * 4.33
            elif 26.0 <= avg_interval <= 35.0:
                cadence = "MONTHLY"
                normalized_monthly_cost = amounts[-1]
            elif 85.0 <= avg_interval <= 100.0:
                cadence = "QUARTERLY"
                normalized_monthly_cost = amounts[-1] / 3.0
            elif 340.0 <= avg_interval <= 385.0:
                cadence = "ANNUAL"
                normalized_monthly_cost = amounts[-1] / 12.0

            total_monthly_burn += normalized_monthly_cost

            sub_record = {
                "vendor": vendor,
                "cadence": cadence,
                "latest_charge": round(amounts[-1], 2),
                "normalized_monthly_cost": round(normalized_monthly_cost, 2),
                "annual_projection": round(normalized_monthly_cost * 12.0, 2),
                "charge_count": len(amounts),
                "average_interval_days": round(avg_interval, 1)
            }
            subscriptions.append(sub_record)
            self.known_subscriptions[vendor] = sub_record

        return {
            "total_detected_subscriptions": len(subscriptions),
            "total_monthly_burn_usd": round(total_monthly_burn, 2),
            "total_annual_burn_usd": round(total_monthly_burn * 12.0, 2),
            "subscriptions": subscriptions
        }

    def detect_stealth_hikes(
        self,
        vendor_name: str,
        historical_charges: List[float]
    ) -> Dict[str, Any]:
        """
        Detects silent price creeping, subscription price hikes, or duplicate fees.
        """
        if len(historical_charges) < 2:
            return {"vendor": vendor_name, "stealth_hike_detected": False, "reason": "Insufficient charge history"}

        initial_price = historical_charges[0]
        latest_price = historical_charges[-1]
        delta = latest_price - initial_price
        pct_increase = (delta / initial_price) * 100.0 if initial_price > 0 else 0.0

        is_hike = delta > 0.01 and pct_increase >= 5.0

        return {
            "vendor": vendor_name,
            "initial_rate": round(initial_price, 2),
            "current_rate": round(latest_price, 2),
            "absolute_increase": round(delta, 2),
            "percentage_increase": round(pct_increase, 2),
            "stealth_hike_detected": is_hike,
            "alert_level": "CRITICAL" if pct_increase >= 20.0 else ("WARNING" if is_hike else "STABLE"),
            "recommendation": (
                f"Flagged stealth hike (+{pct_increase:.1f}%). Trigger renegotiation or alternative vendor search."
                if is_hike else "Subscription pricing is stable."
            )
        }

    def audit_zombie_utilization(
        self,
        vendor_name: str,
        monthly_cost: float,
        last_active_days_ago: int
    ) -> Dict[str, Any]:
        """
        Determines whether a subscription seat is a zombie (unused / forgotten).
        """
        is_zombie = last_active_days_ago >= self.zombie_threshold
        wasted_annual_cost = round(monthly_cost * 12.0, 2) if is_zombie else 0.0

        return {
            "vendor": vendor_name,
            "monthly_cost": round(monthly_cost, 2),
            "last_active_days_ago": last_active_days_ago,
            "inactivity_threshold_days": self.zombie_threshold,
            "is_zombie_seat": is_zombie,
            "potential_annual_savings": wasted_annual_cost,
            "action_required": "IMMEDIATE_TERMINATION_RECOMMENDED" if is_zombie else "ACTIVE_KEEP"
        }

    def generate_cancellation_workflow(
        self,
        vendor_name: str,
        account_id: str = "ACC-9921",
        cancellation_reason: str = "Consolidating software stack to reduce SaaS spend"
    ) -> Dict[str, Any]:
        """
        Generates automated cancellation payloads, formal termination email, or Mastercard mandate revocation.
        """
        formal_letter = (
            f"Subject: Formal Cancellation & Revocation of Recurring Billing Mandate - {vendor_name}\n\n"
            f"Dear Billing Team at {vendor_name},\n\n"
            f"Please accept this formal notification to terminate subscription and cancel all recurring authorization mandates "
            f"associated with Account/Customer ID: {account_id}, effective immediately.\n\n"
            f"Reason: {cancellation_reason}.\n"
            f"In accordance with modern payment mandates (including Mastercard Agent Connect & card association rules), "
            f"please immediately cease all recurring tokenized charges and confirm termination in writing.\n\n"
            f"Sincerely,\nGenPark Autonomous Financial Sentinel"
        )

        return {
            "vendor": vendor_name,
            "account_id": account_id,
            "status": "CANCELLATION_WORKFLOW_READY",
            "mandate_action": "REVOKE_RECURRENT_TOKEN",
            "formal_notice_text": formal_letter,
            "api_payload": {
                "event": "subscription.cancel",
                "vendor": vendor_name.lower().replace(" ", "_"),
                "account_id": account_id,
                "cancel_at_period_end": False,
                "reason": cancellation_reason
            }
        }

    def generate_governance_report(self) -> Dict[str, Any]:
        return {
            "monitored_subscriptions_count": len(self.known_subscriptions),
            "subscriptions": list(self.known_subscriptions.values())
        }
