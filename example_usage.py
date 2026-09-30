"""Example usage for RecurrentSubscriptionAutopilot."""
import json
import time
from client import RecurrentSubscriptionAutopilot

def main():
    print("=== Recurrent Subscription Governance & Price Hike Autopilot Demo ===")
    autopilot = RecurrentSubscriptionAutopilot()

    # 1. Parse Recurring Transaction Stream
    now = time.time()
    stream = [
        {"vendor": "Midjourney AI", "amount": 30.0, "timestamp": now - 60*86400},
        {"vendor": "Midjourney AI", "amount": 30.0, "timestamp": now - 30*86400},
        {"vendor": "Midjourney AI", "amount": 30.0, "timestamp": now},
        {"vendor": "DesignTool Pro", "amount": 15.0, "timestamp": now - 60*86400},
        {"vendor": "DesignTool Pro", "amount": 15.0, "timestamp": now - 30*86400},
        {"vendor": "DesignTool Pro", "amount": 22.50, "timestamp": now} # +50% hike
    ]

    print("\n--- 1. Analyzing Subscription Cadence & Monthly Burn ---")
    analysis = autopilot.analyze_transaction_stream(stream)
    print(f"Total Subscriptions Found: {analysis['total_detected_subscriptions']}")
    print(f"Total Monthly SaaS Burn: ${analysis['total_monthly_burn_usd']} (Annualized: ${analysis['total_annual_burn_usd']})")

    # 2. Flag Stealth Price Creep
    print("\n--- 2. Auditing Price Creep on DesignTool Pro ---")
    hike = autopilot.detect_stealth_hikes("DesignTool Pro", [15.0, 15.0, 22.50])
    print(json.dumps(hike, indent=2))

    # 3. Zombie License Audit
    print("\n--- 3. Auditing Unused Zombie Licenses ---")
    zombie = autopilot.audit_zombie_utilization("Legacy CRM Seat", monthly_cost=65.0, last_active_days_ago=72)
    print(f"Is Zombie Seat: {zombie['is_zombie_seat']} -> Potential Annual Savings: ${zombie['potential_annual_savings']}")

    # 4. Generate Cancellation & Mandate Revocation Workflow
    print("\n--- 4. Generating Automated Cancellation Workflow ---")
    cancel = autopilot.generate_cancellation_workflow("DesignTool Pro", account_id="SUB-DES-8812")
    print(cancel["formal_notice_text"])

if __name__ == "__main__":
    main()
