"""MCP Server for Agentic Recurrent Subscription Autopilot."""
import sys
import json
import time
from client import RecurrentSubscriptionAutopilot

autopilot = RecurrentSubscriptionAutopilot()

def handle_call_tool(params):
    name = params.get("name")
    args = params.get("arguments", {})
    if name != "audit_recurrent_subscriptions":
        raise ValueError(f"Unknown tool: {name}")

    action = args.get("action", "generate_governance_report")
    if action == "analyze_transaction_stream":
        return autopilot.analyze_transaction_stream(args.get("transactions", []))
    elif action == "detect_stealth_hikes":
        return autopilot.detect_stealth_hikes(
            vendor_name=args.get("vendor_name", "Service"),
            historical_charges=args.get("historical_charges", [])
        )
    elif action == "audit_zombie_utilization":
        return autopilot.audit_zombie_utilization(
            vendor_name=args.get("vendor_name", "Service"),
            monthly_cost=float(args.get("monthly_cost", 20.0)),
            last_active_days_ago=int(args.get("last_active_days_ago", 0))
        )
    elif action == "generate_cancellation_workflow":
        return autopilot.generate_cancellation_workflow(
            vendor_name=args.get("vendor_name", "Service"),
            cancellation_reason=args.get("cancellation_reason", "Cost optimization")
        )
    elif action == "generate_governance_report":
        return autopilot.generate_governance_report()
    else:
        raise ValueError(f"Invalid action: {action}")

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print("Running self-test...")
        now = time.time()
        txs = [
            {"vendor": "CloudSaaS", "amount": 29.0, "timestamp": now - 60*86400},
            {"vendor": "CloudSaaS", "amount": 29.0, "timestamp": now - 30*86400},
            {"vendor": "CloudSaaS", "amount": 35.0, "timestamp": now}
        ]
        res = autopilot.analyze_transaction_stream(txs)
        assert res["total_detected_subscriptions"] == 1
        hike = autopilot.detect_stealth_hikes("CloudSaaS", [29.0, 29.0, 35.0])
        assert hike["stealth_hike_detected"] is True
        zombie = autopilot.audit_zombie_utilization("IdleApp", 50.0, 60)
        assert zombie["is_zombie_seat"] is True
        print("Self-test PASSED!")
        sys.exit(0)

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            msg_id = req.get("id")
            method = req.get("method")
            if method == "initialize":
                resp = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "serverInfo": {"name": "RecurrentSubscriptionAutopilot", "version": "1.0.0"},
                        "capabilities": {"tools": {}}
                    }
                }
            elif method == "tools/list":
                resp = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "tools": [{
                            "name": "audit_recurrent_subscriptions",
                            "description": "Autonomous subscription governance: detect recurring billing cadence, flag stealth price hikes, discover zombie licenses, and generate automated cancellation workflows.",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "action": {"type": "string", "enum": ["analyze_transaction_stream", "detect_stealth_hikes", "audit_zombie_utilization", "generate_cancellation_workflow", "generate_governance_report"]},
                                    "transactions": {"type": "array"},
                                    "vendor_name": {"type": "string"},
                                    "historical_charges": {"type": "array"},
                                    "last_active_days_ago": {"type": "integer"},
                                    "monthly_cost": {"type": "number"},
                                    "cancellation_reason": {"type": "string"}
                                },
                                "required": ["action"]
                            }
                        }]
                    }
                }
            elif method == "tools/call":
                res = handle_call_tool(req.get("params", {}))
                resp = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}
                }
            else:
                resp = {"jsonrpc": "2.0", "id": msg_id, "result": {}}
            print(json.dumps(resp), flush=True)
        except Exception as e:
            err_resp = {"jsonrpc": "2.0", "id": None, "error": {"code": -32000, "message": str(e)}}
            print(json.dumps(err_resp), flush=True)

if __name__ == "__main__":
    main()
