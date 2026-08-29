import pytest
from src.recommendations.decision_engine import generate_business_recommendations
from src.inventory.risk import calculate_inventory_risk

def mock_price_trend(trend="STABLE", pct=0.0):
    return {"trend_direction": trend, "30_day_change_pct": pct, "current_price": 45, "30_day_average": 45}

def test_scenario_1_low_inventory_long_lead_time():
    inv = calculate_inventory_risk(usable_inventory=500, forecast_daily_usage=500, supplier_lead_time=3, safety_stock=200)
    recs = generate_business_recommendations(inv, mock_price_trend())
    
    assert recs['priority_actions'][0]['priority'] == "CRITICAL"
    assert recs['priority_actions'][0]['decision'] == "BUY"

def test_scenario_2_high_inventory_low_demand():
    inv = calculate_inventory_risk(usable_inventory=5000, forecast_daily_usage=200, supplier_lead_time=3, safety_stock=200)
    recs = generate_business_recommendations(inv, mock_price_trend())
    
    assert recs['priority_actions'][0]['priority'] == "LOW"
    assert recs['priority_actions'][0]['decision'] == "WAIT"

def test_scenario_3_price_rising_low_inventory():
    inv = calculate_inventory_risk(usable_inventory=1000, forecast_daily_usage=500, supplier_lead_time=3, safety_stock=200)
    price = mock_price_trend("INCREASING", 5.0)
    recs = generate_business_recommendations(inv, price)
    
    # Priority sorting puts CRITICAL/HIGH (Inventory) before MEDIUM (Price)
    assert len(recs['priority_actions']) == 2
    assert recs['priority_actions'][0]['decision'] == "BUY"
    assert recs['priority_actions'][1]['decision'] == "REVIEW PRICE"
