"""
tests/test_integration.py
===========================
End-to-end integration test of the DairyPulse Intelligence Service.
Verifies the complete analytical pipeline, standard response format, business_id
isolation, and internal consistency rules.
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
    get_top_recommendations,
    get_business_summary,
)


def test_full_intelligence_flow():
    business_id_a = "DEMO-001"
    business_id_b = "DEMO-002"

    # 1. Load data & verify business_id isolation
    # We create a dummy sales frame with business_id A and B to verify isolation.
    sales_data = pd.DataFrame([
        {"business_id": business_id_a, "date": "2026-08-01", "product_id": "PRD-PNR", "quantity": 10},
        {"business_id": business_id_a, "date": "2026-08-02", "product_id": "PRD-PNR", "quantity": 15},
        {"business_id": business_id_b, "date": "2026-08-01", "product_id": "PRD-PNR", "quantity": 999},  # B's sales
    ])

    # Demand forecast for A
    resp_a = get_demand_forecast(business_id=business_id_a, product_id="PRD-PNR", horizon=7, sales_df=sales_data)
    assert resp_a["status"] == "success"
    assert resp_a["data"]["product"] == "PRD-PNR"
    # Ensure B's data didn't leak into A's forecast
    assert resp_a["data"]["forecast_quantity"] < 100  # A's historical average is small

    # 2. Demand Forecast validation
    # Verify standard envelope structure
    for key in ["status", "data", "warnings", "data_quality", "sources", "generated_at", "model_version", "versions"]:
        assert key in resp_a
    assert resp_a["data_quality"]["reliability"] in ["HIGH", "MEDIUM", "LOW"]

    # 3. Price Intelligence
    # Verify we get price trends using the purchase records
    purchases_data = pd.DataFrame([
        {"business_id": business_id_a, "date": "2026-08-01", "material_id": "MAT-RMLK", "unit_price": 45.0, "quantity": 100},
        {"business_id": business_id_a, "date": "2026-08-15", "material_id": "MAT-RMLK", "unit_price": 48.0, "quantity": 100},
    ])
    price_resp = get_price_intelligence(business_id=business_id_a, material_id="MAT-RMLK", purchases_df=purchases_data)
    assert price_resp["status"] == "success"
    assert "current_price" in price_resp["data"]
    assert "trend_direction" in price_resp["data"]

    # 4. Inventory Risk
    # Usable stock = 500 L, daily use = 200 L/day, lead time = 3 days, safety = 200 L
    inv_resp = get_inventory_risk(business_id=business_id_a, usable_inventory=500, forecast_daily_usage=200, supplier_lead_time=3)
    assert inv_resp["status"] == "success"
    # days of cover = 500 / 200 = 2.5 days. Lead time is 3 days. Since days_of_cover <= lead_time, risk should be CRITICAL
    assert inv_resp["data"]["risk_level"] == "CRITICAL"
    assert "explainability" in inv_resp["data"]
    assert "WHAT" in inv_resp["data"]["explainability"]

    # 5. Procurement Recommendation
    # Forecast daily usage = 200 L, inventory = 500 L, planned production = 300 kg, safety = 200 L.
    # 7-day demand is 200 * 7 = 1400 L (not directly used by requirement logic except forecast).
    # expected_production_req = 300 * 5.5 = 1650 L. Total req = 1650 + 200 = 1850 L.
    # Gap = 1850 - 500 = 1350 L.
    proc_resp = get_procurement_recommendation(
        business_id=business_id_a,
        usable_inventory=500,
        forecast_daily_usage=200,
        planned_production=300,
        safety_buffer=200,
        conversion_ratio=5.5,
        price_trend="STABLE",
        supplier_lead_time=3
    )
    assert proc_resp["status"] == "success"
    assert proc_resp["data"]["decision"] == "BUY_NOW"
    assert proc_resp["data"]["recommended_quantity"] >= 1100

    # INTERNAL CONSISTENCY ASSERTION:
    # If current inventory (500 L) is below forecast requirement + safety (1600 L), and we procure the recommended qty (1100 L),
    # the new inventory (500 + 1100 = 1600 L) should have a better inventory risk profile.
    new_inventory = 500 + proc_resp["data"]["recommended_quantity"]
    inv_post_proc = get_inventory_risk(business_id=business_id_a, usable_inventory=new_inventory, forecast_daily_usage=200, supplier_lead_time=3)
    # 1850 / 200 = 9.25 days cover.
    # 9.25 days cover is > lead_time (3) and safety buffer days (3 + 2 = 5). Risk level should drop from CRITICAL to MEDIUM or LOW.
    assert inv_post_proc["data"]["days_of_cover"] == 9.25
    assert inv_post_proc["data"]["risk_level"] in ["MEDIUM", "LOW"]

    # 6. Order Feasibility
    # Verify order feasibility check for Paneer order of 100 kg, selling price = 350, conversion ratio = 5.5
    feas_resp = check_order_feasibility(
        business_id=business_id_a,
        product_id="PRD-PNR",
        order_qty=100,
        selling_price=350,
        current_fg_inventory=10,
        raw_material_inventory=1000,
        conversion_ratio=5.5,
        raw_material_cost_per_unit=45.0,
        processing_cost_per_unit=5.0
    )
    assert feas_resp["status"] == "success"
    assert "decision" in feas_resp["data"]
    assert "explainability" in feas_resp["data"]

    # 7. What-If Scenario
    whatif_resp = run_what_if(
        business_id=business_id_a,
        current_margin=15.0,
        scenario_type="MILK_PRICE_INCREASE",
        percentage_change=10.0
    )
    assert whatif_resp["status"] == "success"
    # Price increase should decrease margin
    assert whatif_resp["data"]["simulated_margin"] < 15.0

    # 8. Anomaly Detection
    metric_series = pd.Series([100, 102, 98, 105, 101, 99, 100, 300, 101], index=pd.date_range("2026-08-01", periods=9))
    anomaly_resp = get_anomalies(business_id=business_id_a, metric_series=metric_series, metric_name="milk_intake", window=7)
    assert anomaly_resp["status"] == "success"
    # Value 300 is an anomaly (far above mean of 100)
    assert anomaly_resp["data"]["count"] >= 1

    # 9. Business Health
    health_resp = get_business_health(
        business_id=business_id_a,
        sales_consistency=80,
        order_fulfillment=90,
        inventory_discipline=70,
        growth_trend=85
    )
    assert health_resp["status"] == "success"
    assert 0 <= health_resp["data"]["overall_health_score"] <= 100

    # 10. Credit Readiness
    credit_resp = get_credit_readiness(
        business_id=business_id_a,
        sales_consistency=80,
        order_fulfillment=90,
        business_activity=75,
        inventory_discipline=70,
        growth_trend=85,
        record_completeness=95
    )
    assert credit_resp["status"] == "success"
    assert 0 <= credit_resp["data"]["readiness_indicator_score"] <= 100
    assert "disclaimer" in credit_resp["data"]

    # 11. Scheme Matches
    scheme_resp = get_scheme_matches(
        business_id=business_id_a,
        enterprise_type="Micro",
        location_type="Rural",
        business_activity="Dairy Processing"
    )
    assert scheme_resp["status"] == "success"
    assert scheme_resp["data"]["count"] > 0
    assert "matches" in scheme_resp["data"]

    # 12. Top Recommendations
    recs_resp = get_top_recommendations(
        business_id=business_id_a,
        inventory_risk=inv_resp["data"],
        price_trend=price_resp["data"],
        order_feasibility=feas_resp["data"]
    )
    assert recs_resp["status"] == "success"
    assert len(recs_resp["data"]["priority_actions"]) > 0

    # 13. Master Business Summary (dashboard API payload)
    summary_resp = get_business_summary(business_id=business_id_a)
    assert summary_resp["status"] == "success"
    assert summary_resp["data"]["business_id"] == business_id_a
    assert "today" in summary_resp["data"]
    assert "inventory" in summary_resp["data"]
    assert "top_actions" in summary_resp["data"]
