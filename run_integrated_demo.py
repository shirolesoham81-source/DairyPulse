import os
from src.inventory.risk import calculate_inventory_risk
from src.forecasting.pricing import analyze_raw_material_price
from src.recommendations.decision_engine import generate_business_recommendations
from src.orders.feasibility import check_order_feasibility
import pandas as pd

def run_demo():
    print("Running DairyPulse Phase 3: Integrated Decision & Recommendation Layer Demo...")
    
    # Mocking the demo scenario
    # 1. Rising demand (Paneer), Low milk inventory, Increasing milk price, Pending large order
    
    inv_risk = calculate_inventory_risk(1000, 500, 3, 200)
    
    dummy_purchases = pd.DataFrame({"material_id": ["MAT-RMLK", "MAT-RMLK"], "date": ["2023-01-01", "2023-01-02"], "unit_price": [45, 49]})
    price_risk = analyze_raw_material_price(dummy_purchases, "MAT-RMLK")
    
    order = check_order_feasibility("PRD-PNR", 500, 350, 100, 1000, 5.5, 49)
    
    recommendations = generate_business_recommendations(inv_risk, price_risk, order)
    
    report = f"""# DairyPulse Integrated Decision Engine Report

## Architecture
The Decision Engine (`src/recommendations/decision_engine.py`) ingests deterministic signals from forecasting, inventory, and orders to produce a single prioritized list of actionable recommendations for the MSME owner.

## Demo Scenario Traces
**Scenario Setup:**
- Milk Inventory: 1000L (Usage: 500L/day, Lead Time: 3 days) -> CRITICAL RISK
- Milk Price: Rising (from 45 to 49) -> HIGH RISK
- New Order: 500kg Paneer -> REQUIRES RAW MATERIAL

**Top Recommended Actions (Engine Output):**
"""
    for action in recommendations['priority_actions']:
        report += f"""
### Priority: {action['priority']} | Decision: {action['decision']}
- **Title**: {action['title']}
- **Reason**: {action['reason']}
- **Evidence**: {action['evidence']}
- **Estimated Impact**: {action['impact']}
- **Trace ID**: {action['id']}
"""

    os.makedirs('reports', exist_ok=True)
    with open('reports/integrated_decision_engine_report.md', 'w') as f:
        f.write(report)
        
    print("Demo complete. Output saved to reports/integrated_decision_engine_report.md")

if __name__ == "__main__":
    run_demo()
