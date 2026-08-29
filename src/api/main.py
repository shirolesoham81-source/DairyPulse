from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="DairyPulse Intelligence API")

class FeasibilityRequest(BaseModel):
    product_id: str
    order_qty: float
    selling_price: float
    current_fg_inventory: float
    raw_material_inventory: float
    conversion_ratio: float
    raw_material_cost_per_unit: float

@app.get("/")
def root():
    return {"status": "DairyPulse Intelligence API Running"}

@app.get("/dashboard/business-summary")
def get_business_summary():
    """
    Returns the unified payload for the main dashboard (Phase 3 Integrated Output).
    """
    from src.inventory.risk import calculate_inventory_risk
    from src.forecasting.pricing import analyze_raw_material_price
    from src.recommendations.decision_engine import generate_business_recommendations
    from src.recommendations.daily_brief import generate_daily_business_brief
    from src.business_health.health import calculate_business_health
    from src.credit.readiness import calculate_credit_readiness
    
    # Mock parameters for the dashboard payload demonstration
    inventory_risk = calculate_inventory_risk(1000, 500, 3, 200)
    
    # Mock a dummy DataFrame for price analysis to pass the signature
    import pandas as pd
    dummy_purchases = pd.DataFrame({"material_id": ["MAT-RMLK", "MAT-RMLK"], "date": ["2023-01-01", "2023-01-02"], "unit_price": [45, 48]})
    price_risk = analyze_raw_material_price(dummy_purchases, "MAT-RMLK")
    
    top_actions = generate_business_recommendations(inventory_risk, price_risk)
    
    daily_brief = generate_daily_business_brief(
        sales_today=15000, expected_demand=500, inventory_days=inventory_risk['days_of_cover'], 
        main_risk_str="Milk stock may run out", action_rec="Procure 1500L", 
        price_trend=price_risk['trend_direction'], pending_orders=2
    )
    
    health = calculate_business_health(85, 95, 60, 70)
    readiness = calculate_credit_readiness(85, 95, 80, 60, 70, 90)
    
    return {
        "business_health": health,
        "today": {"brief": daily_brief},
        "demand": {"expected_daily_demand": 500, "trend": "INCREASING"},
        "inventory": inventory_risk,
        "price_intelligence": price_risk,
        "top_actions": top_actions['priority_actions'],
        "orders": {"pending": 2},
        "credit_readiness": readiness,
        "scheme_matches": []
    }
