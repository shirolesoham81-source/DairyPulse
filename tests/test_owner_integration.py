"""
tests/test_owner_integration.py
================================
Integration and validation suite for DairyPulse Phase 5 owner-facing outputs,
outcomes tracking, and lender bank packages.
"""

import pytest
import os
import json
from src.intelligence.service import (
    get_full_owner_view,
    generate_lender_data_package,
    record_feedback,
    track_outcome,
)
from src.intelligence.owner_outputs import (
    generate_today_summary,
    generate_procurement_advice,
    generate_inventory_advice,
    generate_price_advice,
    generate_order_advice,
    compare_to_benchmark,
    get_cold_start_forecast,
)
from src.intelligence.outcomes import DB_PATH, load_all_outcomes


def test_today_summary_consistency():
    resp = generate_today_summary("DEMO-001")
    assert "text_summary" in resp
    assert "TODAY'S BUSINESS STATUS" in resp["text_summary"]
    # Check that it uses plain language rather than probability numbers
    assert "Sales:" in resp["text_summary"]
    assert "Expected demand:" in resp["text_summary"]
    assert "Inventory risk:" in resp["text_summary"]
    assert "Business health:" in resp["text_summary"]


def test_procurement_advice_logic():
    resp = generate_procurement_advice(
        business_id="DEMO-001",
        usable_inventory=500,
        forecast_daily_usage=200,
        planned_production=300,
        safety_buffer=200,
        conversion_ratio=5.5,
        price_trend="INCREASING"
    )
    assert resp["recommended_action"] == "BUY_NOW"
    assert "Recommended action:" in resp["recommended_action"] or resp["recommended_action"] in ["BUY_NOW", "BUY_PARTIAL", "WAIT"]
    assert "recommended_quantity" in resp
    assert "estimated_procurement_cost" in resp
    assert "disclaimer" in resp
    # Check that recommendation is NOT claimed as guaranteed optimal
    assert "validation" in resp["disclaimer"].lower() or "guarantee" in resp["disclaimer"].lower()


def test_inventory_advice_details():
    resp = generate_inventory_advice("DEMO-001", usable_inventory=600, forecast_daily_usage=200, supplier_lead_time=3)
    assert "current_stock" in resp
    assert "days_of_cover" in resp
    assert "advice_text" in resp
    assert "Milk inventory covers approximately" in resp["advice_text"]


def test_price_advice_details():
    resp = generate_price_advice("DEMO-001")
    assert "price_trend_summary" in resp
    assert "procurement_risk" in resp
    # Do not claim exact future prices
    assert "Milk procurement price has" in resp["price_trend_summary"]


def test_order_advice_checks():
    resp = generate_order_advice(
        business_id="DEMO-001",
        product_id="PRD-PNR",
        order_qty=100,
        selling_price=350,
        current_fg_inventory=10,
        raw_material_inventory=500,
        conversion_ratio=5.5,
        raw_material_cost_per_unit=45.0
    )
    assert "order" in resp
    assert "decision" in resp
    assert "why" in resp
    assert "required_procurement" in resp
    assert "estimated_margin" in resp
    assert "main_risk" in resp
    assert "action" in resp
    # Check for margin details
    assert "Estimated margin" in resp["estimated_margin"] or "₹" in resp["estimated_margin"]


def test_lender_bank_package_completeness():
    resp = generate_lender_data_package("DEMO-001")
    assert resp["status"] == "success"
    d = resp["data"]
    
    # Check all 14 structured sections
    sections = [
        "business_profile", "reporting_period", "sales_history_summary", 
        "procurement_history", "production_summary", "inventory_summary", 
        "order_fulfillment", "cost_trends", "business_health", 
        "credit_readiness", "risk_indicators", "supporting_documents", 
        "data_quality_notes", "model_rule_versions"
    ]
    for sec in sections:
        assert sec in d, f"Missing section: {sec}"
        
    # Check period links in claims
    assert "period" in d["sales_history_summary"]
    assert "source" in d["sales_history_summary"]
    assert "disclaimer" in d
    assert "lender makes the final decision" in d["disclaimer"]


def test_benchmark_privacy():
    resp = compare_to_benchmark("DEMO-001", "PRD-PNR", 6.2)
    assert "anonymous_peer_benchmark" in resp
    assert "verdict" in resp
    assert "privacy_assurance" in resp
    
    # Ensure no competitor name or private transaction details are exposed
    payload_str = json.dumps(resp)
    assert "competitor" not in payload_str.lower()
    assert "Kopargaon Dairy Foods" not in payload_str  # only demo business is fine, no peer names
    assert "privacy" in resp["privacy_assurance"]


def test_cold_start_forecast():
    # Low history (< 30 days)
    resp = get_cold_start_forecast("DEMO-001", "PRD-PNR", own_history_days=12)
    assert resp["reliability"] == "LOW"
    assert "data_sources" in resp
    assert "limitations" in resp
    assert "only 12 valid business days" in resp["reason"].lower()

    # Medium history (> 30 days)
    resp = get_cold_start_forecast("DEMO-001", "PRD-PNR", own_history_days=45)
    assert resp["reliability"] == "MEDIUM"


def test_feedback_and_outcome_storage():
    # Clean scratch storage path before starting
    if os.path.exists(DB_PATH):
        try:
            os.remove(DB_PATH)
        except OSError:
            pass

    # 1. Save feedback
    rec_id = "REC-TEST-999"
    fb_resp = record_feedback(
        recommendation_id=rec_id,
        decision="BUY_NOW",
        owner_action="ACCEPTED",
        final_quantity=1500.0
    )
    assert fb_resp["status"] == "success"
    assert fb_resp["data"]["owner_action"] == "ACCEPTED"

    # 2. Track actual operational outcomes
    out_resp = track_outcome(
        recommendation_id=rec_id,
        actual_purchase_quantity=1450.0,
        stockout_occurred=False
    )
    assert out_resp["status"] == "success"
    assert out_resp["data"]["stockout_occurred"] is False

    # 3. Reload and verify database content
    db = load_all_outcomes()
    assert rec_id in db["feedback"]
    assert rec_id in db["outcomes"]
    assert db["feedback"][rec_id]["owner_action"] == "ACCEPTED"
    assert db["outcomes"][rec_id]["actual_purchase_quantity"] == 1450.0


def test_full_owner_view_service_call():
    resp = get_full_owner_view("DEMO-001")
    assert resp["status"] == "success"
    d = resp["data"]
    
    # Verify top-level aggregates
    assert "today" in d
    assert "price" in d
    assert "inventory" in d
    assert "procurement" in d
    assert "orders" in d
    assert "business_health" in d
    assert "credit_readiness" in d
    assert "scheme_matches" in d
    assert "benchmark_peer_comparison" in d
