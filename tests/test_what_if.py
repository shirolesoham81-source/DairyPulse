import pytest
from src.orders.economics import run_what_if_scenario

def test_what_if_milk_price_increase():
    current_margin = 100000
    res = run_what_if_scenario(current_margin, "MILK_PRICE_INCREASE", 0.10) # +10% price
    
    assert res['simulated_margin'] < current_margin
    assert res['simulated_margin'] == 90000
    assert res['risk'] == "HIGH"

def test_what_if_demand_spike():
    current_margin = 100000
    res = run_what_if_scenario(current_margin, "DEMAND_SPIKE", 0.20) # +20% demand
    
    assert res['simulated_margin'] > current_margin
    assert res['simulated_margin'] == 120000
    assert res['risk'] == "MEDIUM"
