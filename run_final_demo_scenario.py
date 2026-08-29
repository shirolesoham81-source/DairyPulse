"""
Final demo scenario: A dairy receives a large Paneer order.
The system evaluates all intelligence dimensions and prints the story.
"""
from src.intelligence.service import (
    check_order_feasibility,
    get_procurement_recommendation,
    get_price_intelligence,
    get_inventory_risk,
    get_business_health,
    get_credit_readiness,
    get_scheme_matches,
)

b = "demo-001"
print("=== FINAL DEMO SCENARIO: Large Paneer Order ===\n")

# 1. Order feasibility
order = check_order_feasibility(b, "PRD-PNR", 500, 350, 80, 1500, 5.5, 48.0, 5.0)
d = order["data"]
print("ORDER DECISION:")
print(f"  Decision : {d['decision']}")
print(f"  Margin   : Rs.{d['estimated_margin']:,}")
print(f"  RM needed: {d['required_raw_material']} L milk")
print(f"  Procure  : {d['procurement_quantity_needed']} L additional\n")

# 2. Procurement
proc = get_procurement_recommendation(b, 1500, 500, 0, 200, 5.5, "INCREASING")
pd_ = proc["data"]
print("PROCUREMENT:")
print(f"  Action   : {pd_['decision']}")
print(f"  Quantity : {pd_['recommended_quantity']} L\n")

# 3. Price
price = get_price_intelligence(b)
pr = price["data"]
print("PRICE:")
print(f"  Trend    : {pr['trend_direction']}")
print(f"  Current  : Rs.{pr['current_price']}/L\n")

# 4. Inventory
inv = get_inventory_risk(b, 1500, 500)
ir = inv["data"]
print("INVENTORY:")
print(f"  Risk     : {ir['risk_level']}")
print(f"  Cover    : {ir['days_of_cover']} days\n")

# 5. Health
health = get_business_health(b, 88, 94, 72, 78)
print(f"BUSINESS HEALTH: {health['data']['overall_health_score']:.1f}/100\n")

# 6. Credit
credit = get_credit_readiness(b, 88, 94, 85, 72, 78, 90)
print(f"CREDIT READINESS: {credit['data']['readiness_indicator_score']:.2f}/100\n")

# 7. Schemes
schemes = get_scheme_matches(b, "Micro", "Rural", "Dairy Processing")
print(f"SCHEME MATCHES: {schemes['data']['count']} potentially relevant\n")

print("Result is understandable without opening the Python code.")
print("FINAL DEMO SCENARIO: PASS")
