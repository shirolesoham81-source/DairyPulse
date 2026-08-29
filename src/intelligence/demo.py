"""
src/intelligence/demo.py
=========================
Simple command‑line entry point that prints a human‑readable snapshot of the
demo business intelligence dashboard.  It demonstrates that the service layer
works end‑to‑end without any external web framework.

Run with:
    python -m src.intelligence.demo
"""

import json
from datetime import datetime

from src.intelligence.service import get_business_summary


def _pretty_number(val):
    """Format numbers with commas and appropriate units for the demo output."""
    if isinstance(val, (int, float)):
        if val == int(val):
            return f"{int(val):,}"  # integer with thousand separators
        return f"{val:,.2f}"  # two‑decimal float
    return str(val)


def _print_section(title: str, content: dict):
    print(f"{title.upper()}:\n")
    for k, v in content.items():
        if isinstance(v, dict):
            # nested dict – flatten one level for readability
            sub = ", ".join(f"{subk}: {_pretty_number(subv)}" for subk, subv in v.items())
            print(f"  {k}: {sub}")
        elif isinstance(v, list):
            print(f"  {k}: {', '.join(str(item) for item in v)}")
        else:
            print(f"  {k}: {_pretty_number(v)}")
    print("\n")


def main():
    # In demo mode we ignore a real business_id – the config contains a single demo profile.
    demo_id = "DEMO-001"
    result = get_business_summary(demo_id)
    if result["status"] != "success":
        print("Failed to generate demo summary:")
        print(json.dumps(result, indent=2))
        return
    data = result["data"]
    print("\n=== DAIRYPULSE BUSINESS INTELLIGENCE DEMO ===\n")
    # TODAY
    _print_section("Today", data.get("today", {}))
    # DEMAND
    _print_section("Demand", data.get("demand", {}))
    # INVENTORY
    _print_section("Inventory", data.get("inventory", {}))
    # PRICE
    _print_section("Price", data.get("price", {}))
    # PROCUREMENT ACTION
    proc = data.get("procurement", {})
    print("ACTION:")
    print(f"  {proc.get('recommended_action', 'WAIT')}\n")
    # ORDER FEASIBILITY (if any)
    if data.get("order_feasibility"):
        _print_section("Order", data["order_feasibility"])
    # BUSINESS HEALTH & CREDIT
    print(f"BUSINESS HEALTH: {_pretty_number(data.get('business_health'))}/100\n")
    print(f"CREDIT READINESS: {_pretty_number(data.get('credit_readiness'))}/100\n")
    # SCHEME MATCHES
    print(f"SCHEME MATCHES: {data.get('scheme_matches')} potentially relevant\n")
    # TOP ACTIONS
    print("TOP ACTIONS:")
    for act in data.get("top_actions", []):
        print(f"  - {act}")
    print("\nDisclaimer: This is simulated demo data. All numbers are synthetic.")


if __name__ == "__main__":
    main()
