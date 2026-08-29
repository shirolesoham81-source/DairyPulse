import pytest
from src.inventory.risk import calculate_inventory_risk
from src.procurement.decision import recommend_procurement
from src.orders.feasibility import check_order_feasibility
from src.orders.economics import calculate_unit_margin

def test_inventory_risk_critical():
    risk = calculate_inventory_risk(usable_inventory=1000, forecast_daily_usage=500, supplier_lead_time=3, safety_stock=200)
    assert risk['days_of_cover'] == 2.0
    assert risk['risk_level'] == "CRITICAL"

def test_inventory_risk_healthy():
    # 5000L / 500L = 10 days cover; lead_time=3; 10 > 3*3=9 → LOW (excess stock)
    risk = calculate_inventory_risk(usable_inventory=5000, forecast_daily_usage=500, supplier_lead_time=3, safety_stock=200)
    assert risk['days_of_cover'] == 10.0
    assert risk['risk_level'] == "LOW"  # excess inventory band

def test_inventory_risk_medium():
    # 7 days cover with lead_time=3, safety_days=2 → 7 > 3+2=5, 7 < 3*3=9 → MEDIUM
    risk = calculate_inventory_risk(usable_inventory=3500, forecast_daily_usage=500, supplier_lead_time=3, safety_stock=200)
    assert risk['days_of_cover'] == 7.0
    assert risk['risk_level'] == "MEDIUM"

def test_procurement_decision_buy_now():
    decision = recommend_procurement(demand_forecast_trend="FLAT", days_of_cover=2, supplier_lead_time=3, price_trend="STABLE", recommended_qty=1500)
    assert decision['decision'] == "BUY_NOW"

def test_order_feasibility_accept():
    feasibility = check_order_feasibility(product_id="PRD-PNR", order_qty=500, selling_price=350, 
                                          current_fg_inventory=600, raw_material_inventory=0, 
                                          conversion_ratio=5.5, raw_material_cost_per_unit=45)
    assert feasibility['decision'] == "ACCEPT"
    assert feasibility['delivery_risk'] == "LOW"

def test_order_feasibility_conditions():
    feasibility = check_order_feasibility(product_id="PRD-PNR", order_qty=500, selling_price=350, 
                                          current_fg_inventory=100, raw_material_inventory=1000, 
                                          conversion_ratio=5.5, raw_material_cost_per_unit=45)
    assert feasibility['decision'] == "ACCEPT_WITH_CONDITIONS"
    assert feasibility['procurement_quantity_needed'] > 0

def test_unit_margin():
    margin = calculate_unit_margin(rm_cost=250, processing_cost=5, packaging_cost=2, selling_price=350)
    assert margin['estimated_unit_margin'] == 93.0
