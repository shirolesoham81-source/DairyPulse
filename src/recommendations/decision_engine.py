import uuid
from datetime import datetime
from src.recommendations.explanation import explain_inventory_risk, explain_price_trend

def generate_business_recommendations(inventory_risk: dict, price_trend: dict, order_feasibility: dict = None) -> dict:
    actions = []
    
    # 1. Inventory Risk Rule
    if inventory_risk['risk_level'] in ["CRITICAL", "HIGH"]:
        rec_id = f"REC-{datetime.now().strftime('%Y')}-{str(uuid.uuid4())[:4]}"
        actions.append({
            "id": rec_id,
            "priority": "CRITICAL" if inventory_risk['risk_level'] == "CRITICAL" else "HIGH",
            "type": "PROCUREMENT",
            "title": "Procure milk",
            "reason": explain_inventory_risk(inventory_risk['days_of_cover'], inventory_risk['supplier_lead_time_days'], inventory_risk['risk_level']),
            "evidence": f"Stock: {inventory_risk['usable_inventory']} L | Use: {inventory_risk['forecast_daily_usage']} L/day | Lead: {inventory_risk['supplier_lead_time_days']} days",
            "decision": "BUY",
            "impact": "reduce stockout risk from CRITICAL/HIGH to LOW"
        })
    elif inventory_risk['risk_level'] == "MEDIUM":
        actions.append({
            "id": f"REC-{datetime.now().strftime('%Y')}-{str(uuid.uuid4())[:4]}",
            "priority": "LOW",
            "type": "INVENTORY",
            "title": "Inventory healthy — monitor",
            "reason": "Stock levels are within the healthy range.",
            "evidence": f"Days of cover: {inventory_risk['days_of_cover']}",
            "decision": "WAIT",
            "impact": "no immediate action needed"
        })
    elif inventory_risk['risk_level'] == "LOW":
        # LOW risk here means excess inventory (days_of_cover > lead_time * 3)
        actions.append({
            "id": f"REC-{datetime.now().strftime('%Y')}-{str(uuid.uuid4())[:4]}",
            "priority": "LOW",
            "type": "INVENTORY",
            "title": "Excess inventory detected",
            "reason": explain_inventory_risk(inventory_risk['days_of_cover'], inventory_risk['supplier_lead_time_days'], inventory_risk['risk_level']),
            "evidence": f"Days of cover: {inventory_risk['days_of_cover']} | Lead time: {inventory_risk['supplier_lead_time_days']} days",
            "decision": "WAIT",
            "impact": "reduce purchase order next cycle to free up working capital"
        })
        
    # 2. Price Risk Rule
    if price_trend['trend_direction'] == "INCREASING":
        actions.append({
            "id": f"REC-{datetime.now().strftime('%Y')}-{str(uuid.uuid4())[:4]}",
            "priority": "MEDIUM",
            "type": "PRICE_RISK",
            "title": "Review procurement timing",
            "reason": explain_price_trend(price_trend['trend_direction'], price_trend['30_day_change_pct']),
            "evidence": f"Current: {price_trend['current_price']} | 30-day: {price_trend['30_day_average']}",
            "decision": "REVIEW PRICE",
            "impact": "estimated cost savings on procurement"
        })
        
    # 3. Order Rule
    if order_feasibility:
        priority = "HIGH"
        if order_feasibility['decision'] == "HIGH_RISK":
            priority = "CRITICAL"
            
        actions.append({
            "id": f"REC-{datetime.now().strftime('%Y')}-{str(uuid.uuid4())[:4]}",
            "priority": priority,
            "type": "ORDER",
            "title": "Review New Order Feasibility",
            "reason": order_feasibility['reasons'][0],
            "evidence": f"Req RM: {order_feasibility['required_raw_material']} | Est Margin: {order_feasibility['estimated_margin']}",
            "decision": order_feasibility['decision'],
            "impact": f"Projected margin: ₹{order_feasibility['estimated_margin']}"
        })
        
    # Sort by priority
    priority_map = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "INFO": 4}
    actions.sort(key=lambda x: priority_map.get(x['priority'], 99))
    
    return {
        "priority_actions": actions[:3]  # Top 3 only
    }
