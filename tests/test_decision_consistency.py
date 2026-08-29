import pytest
from src.inventory.risk import calculate_inventory_risk
from src.procurement.decision import recommend_procurement
from src.orders.feasibility import check_order_feasibility

def test_high_stockout_never_wait():
    # HIGH risk means days_of_cover <= lead_time + safety
    # Wait is only allowed if recommended qty <= 0, but if risk is high, procurement should trigger.
    inv = calculate_inventory_risk(100, 500, 3, 200) # days of cover = 0.2
    assert inv['risk_level'] == "CRITICAL"
    
    decision = recommend_procurement("FLAT", inv['days_of_cover'], 3, "STABLE", 1500)
    assert decision['decision'] != "WAIT"
    assert decision['decision'] == "BUY_NOW"

def test_negative_margin_never_accept():
    # If margin is negative, decision must be HIGH_RISK, never ACCEPT
    feasibility = check_order_feasibility(
        product_id="PRD-PNR", order_qty=500, selling_price=10, # Very low selling price
        current_fg_inventory=600, raw_material_inventory=1000, 
        conversion_ratio=5.5, raw_material_cost_per_unit=45
    )
    assert feasibility['estimated_margin'] < 0
    assert feasibility['decision'] == "HIGH_RISK"
    assert feasibility['decision'] != "ACCEPT"

def test_insufficient_raw_material_never_accept_blindly():
    feasibility = check_order_feasibility(
        product_id="PRD-PNR", order_qty=500, selling_price=350, 
        current_fg_inventory=0, raw_material_inventory=0, 
        conversion_ratio=5.5, raw_material_cost_per_unit=45
    )
    assert feasibility['decision'] == "ACCEPT_WITH_CONDITIONS"
    assert feasibility['procurement_quantity_needed'] > 0
