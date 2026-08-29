"""
tests/test_edge_cases.py
========================
Edge-case unit testing for DairyPulse Intelligence Service.
Verifies that invalid or pathological inputs result in standard error responses
or warnings instead of unhandled exceptions.
"""

import pytest
import pandas as pd
from src.intelligence.service import (
    get_demand_forecast,
    get_price_intelligence,
    get_inventory_risk,
    get_procurement_recommendation,
    check_order_feasibility,
    run_what_if,
    get_anomalies,
    get_business_health,
    get_credit_readiness,
    get_scheme_matches,
)


def test_get_demand_forecast_empty_data():
    # Empty DataFrame
    resp = get_demand_forecast("DEMO-001", "PRD-PNR", sales_df=pd.DataFrame())
    assert resp["status"] == "success"  # Returns default/fallback empty forecast
    assert resp["data"]["forecast_quantity"] == 0
    assert len(resp["warnings"]) > 0


def test_get_demand_forecast_missing_columns():
    # Missing columns
    invalid_df = pd.DataFrame([{"product_id": "PRD-PNR", "quantity": 10}])
    resp = get_demand_forecast("DEMO-001", "PRD-PNR", sales_df=invalid_df)
    assert resp["status"] == "success"  # Returns fallback gracefully
    assert resp["data"]["forecast_quantity"] == 0


def test_get_price_intelligence_empty_data():
    # Empty purchase history
    resp = get_price_intelligence("DEMO-001", "MAT-RMLK", purchases_df=pd.DataFrame())
    assert resp["status"] == "success"  # Fallback to config price
    assert "current_price" in resp["data"]
    assert len(resp["warnings"]) > 0


def test_get_inventory_risk_negative_inventory():
    # Negative usable inventory
    resp = get_inventory_risk("DEMO-001", usable_inventory=-500, forecast_daily_usage=100)
    assert resp["status"] == "error"
    assert resp["error_code"] == "INVALID_INPUT"
    assert "usable_inventory cannot be negative" in resp["message"]


def test_get_inventory_risk_zero_demand():
    # Zero daily usage
    resp = get_inventory_risk("DEMO-001", usable_inventory=500, forecast_daily_usage=0)
    assert resp["status"] == "success"
    assert resp["data"]["risk_level"] == "LOW"
    assert "warnings" in resp
    assert len(resp["warnings"]) > 0


def test_get_procurement_recommendation_negative_inputs():
    # Negative planned production
    resp = get_procurement_recommendation(
        business_id="DEMO-001",
        usable_inventory=500,
        forecast_daily_usage=200,
        planned_production=-100,
        safety_buffer=200,
        conversion_ratio=1.0
    )
    assert resp["status"] == "error"  # Fails at low-level requirement calculations


def test_check_order_feasibility_invalid_prices():
    # Zero/negative selling price
    resp = check_order_feasibility(
        business_id="DEMO-001",
        product_id="PRD-PNR",
        order_qty=100,
        selling_price=0,
        current_fg_inventory=10,
        raw_material_inventory=500,
        conversion_ratio=5.5,
        raw_material_cost_per_unit=45
    )
    assert resp["status"] == "error"
    assert resp["error_code"] == "INVALID_INPUT"

    resp = check_order_feasibility(
        business_id="DEMO-001",
        product_id="PRD-PNR",
        order_qty=-10,
        selling_price=350,
        current_fg_inventory=10,
        raw_material_inventory=500,
        conversion_ratio=5.5,
        raw_material_cost_per_unit=45
    )
    assert resp["status"] == "error"
    assert resp["error_code"] == "INVALID_INPUT"


def test_run_what_if_invalid_scenario():
    # Invalid scenario type
    resp = run_what_if("DEMO-001", current_margin=10, scenario_type="INVALID_TYPE", percentage_change=5)
    assert resp["status"] == "error"
    assert resp["error_code"] == "INVALID_SCENARIO"

    # Negative percentage change
    resp = run_what_if("DEMO-001", current_margin=10, scenario_type="MILK_PRICE_INCREASE", percentage_change=-5)
    assert resp["status"] == "error"
    assert resp["error_code"] == "INVALID_INPUT"


def test_get_anomalies_insufficient_data():
    # Too few elements
    metric_series = pd.Series([100, 102])
    resp = get_anomalies("DEMO-001", metric_series=metric_series, window=7)
    assert resp["status"] == "success"
    assert resp["data"]["count"] == 0
    assert len(resp["warnings"]) > 0


def test_get_business_health_out_of_bounds():
    # Out of range input values
    resp = get_business_health("DEMO-001", sales_consistency=-10, order_fulfillment=90, inventory_discipline=80, growth_trend=70)
    assert resp["status"] == "error"
    assert resp["error_code"] == "INVALID_INPUT"

    resp = get_business_health("DEMO-001", sales_consistency=110, order_fulfillment=90, inventory_discipline=80, growth_trend=70)
    assert resp["status"] == "error"
    assert resp["error_code"] == "INVALID_INPUT"


def test_get_credit_readiness_out_of_bounds():
    # Out of range input values
    resp = get_credit_readiness("DEMO-001", sales_consistency=80, order_fulfillment=90, business_activity=75,
                                inventory_discipline=70, growth_trend=85, record_completeness=101)
    assert resp["status"] == "error"
    assert resp["error_code"] == "INVALID_INPUT"


def test_get_scheme_matches_missing_profile():
    # Empty enterprise_type
    resp = get_scheme_matches("DEMO-001", enterprise_type="", location_type="Rural", business_activity="Dairy Processing")
    assert resp["status"] == "error"
    assert resp["error_code"] == "MISSING_PROFILE"
