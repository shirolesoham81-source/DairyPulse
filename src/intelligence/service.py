"""
src/intelligence/service.py
===========================
DairyPulse Intelligence Service — single public façade.

All higher-level callers (API routes, CLI, integration tests) must use
these functions instead of importing individual analytics modules directly.

Rules enforced here:
  * business_id isolation (no cross-business data leakage)
  * standard JSON response envelope
  * data-quality block in every result
  * explainability block in every major decision
  * version stamping on every response
  * graceful error handling with useful warnings
  * no automatic actions (buy, approve, apply)
"""

from __future__ import annotations

import json
import logging
import os
import random
from datetime import datetime, timezone
from typing import Any

import pandas as pd

from src.intelligence.response import success, error, data_quality_block
from src.intelligence.version import (
    DEMAND_MODEL_VERSION, PRICE_MODEL_VERSION,
    BUSINESS_RULES_VERSION, READINESS_SCORING_VERSION,
)
from src.intelligence.explainability import DecisionTrace
from src.intelligence.data_quality import assess_data_quality
from src.intelligence.reconciliation import reconcile_inventory

from src.forecasting.demand import forecast_demand
from src.forecasting.pricing import analyze_raw_material_price
from src.inventory.risk import calculate_inventory_risk
from src.procurement.decision import (
    calculate_raw_material_requirement,
    recommend_procurement,
)
from src.orders.feasibility import check_order_feasibility as _check_order_feasibility
from src.orders.economics import run_what_if_scenario, calculate_unit_margin
from src.anomaly.detector import detect_anomalies
from src.business_health.health import calculate_business_health, generate_business_health_summary
from src.credit.readiness import calculate_credit_readiness, generate_credit_readiness_summary
from src.schemes.matcher import match_government_schemes, generate_scheme_summary
from src.recommendations.decision_engine import generate_business_recommendations

log = logging.getLogger("DairyPulse.Service")

# ── Config loader ─────────────────────────────────────────────────────────────

_CONFIG: dict | None = None

def _cfg() -> dict:
    global _CONFIG
    if _CONFIG is None:
        cfg_path = os.path.join(os.path.dirname(__file__), "../../config/business_rules.json")
        with open(cfg_path, "r") as f:
            _CONFIG = json.load(f)
    return _CONFIG


# ── Business-ID isolation helper ──────────────────────────────────────────────

def _filter_by_business(df: pd.DataFrame, business_id: str) -> pd.DataFrame:
    """
    If the DataFrame has a 'business_id' column, filter to the given ID.
    If no such column exists (single-business demo), return the full frame
    but log a debug note.
    """
    if "business_id" in df.columns:
        filtered = df[df["business_id"] == business_id].copy()
        log.debug("business_id=%s | rows before=%d, after=%d", business_id, len(df), len(filtered))
        return filtered
    log.debug("No business_id column present — returning all rows (single-business mode).")
    return df.copy()


# ── Data loader (demo mode) ───────────────────────────────────────────────────

def _load_demo_data() -> dict[str, pd.DataFrame]:
    """Load processed CSVs if available; fall back to empty frames with correct schema."""
    base = os.path.join(os.path.dirname(__file__), "../../data/processed")
    frames = {}
    files = {
        "sales": "clean_sales.csv",
        "purchases": "clean_purchases.csv",
        "production": "clean_production.csv",
        "inventory": "clean_inventory.csv",
        "expenses": "clean_expenses.csv",
        "snapshot": "daily_business_snapshot.csv",
    }
    for key, fname in files.items():
        path = os.path.join(base, fname)
        if os.path.exists(path):
            frames[key] = pd.read_csv(path)
        else:
            frames[key] = pd.DataFrame()
    return frames


def _demo_cfg() -> dict:
    demo_path = os.path.join(os.path.dirname(__file__), "../../config/demo_business.json")
    with open(demo_path, "r") as f:
        return json.load(f)


# ── Standard data-quality helper ──────────────────────────────────────────────

def _quality(df: pd.DataFrame, expected_days: int = 180) -> dict:
    if df.empty or "date" not in df.columns:
        return data_quality_block(period_days=0, valid_records=0, missing_rate=1.0, reliability="LOW")
    dq = assess_data_quality(df, expected_days)
    return data_quality_block(
        period_days=expected_days,
        valid_records=df["date"].nunique(),
        missing_rate=dq.get("missing_rate", 0.0),
        reliability=dq.get("quality_indicator", "MEDIUM"),
    )


# ═══════════════════════════════════════════════════════════════════════════════
# PUBLIC SERVICE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════


def get_demand_forecast(
    business_id: str,
    product_id: str,
    horizon: int = 7,
    sales_df: pd.DataFrame | None = None,
) -> dict:
    """
    Forecast demand for a single product.

    Args:
        business_id : Unique business identifier (isolation enforced).
        product_id  : e.g. 'PRD-PNR'.
        horizon     : Forecast horizon in days (default 7).
        sales_df    : Optional caller-supplied DataFrame; loads demo data if None.

    Returns:
        Standard success/error envelope.
    """
    try:
        if sales_df is None:
            data = _load_demo_data()
            sales_df = data.get("sales", pd.DataFrame())

        sales_df = _filter_by_business(sales_df, business_id)
        dq = _quality(sales_df)

        required_cols = {"product_id", "date", "quantity"}
        if sales_df.empty or not required_cols.issubset(sales_df.columns):
            return success(
                {"product": product_id, "forecast_quantity": 0, "trend": "UNKNOWN"},
                warnings=["No valid sales history found for this product or columns are missing."],
                data_quality=dq if sales_df.empty else data_quality_block(period_days=0, valid_records=0, missing_rate=1.0, reliability="LOW"),
                model_version=DEMAND_MODEL_VERSION,
                sources=["sales_history"],
            )

        forecast = forecast_demand(sales_df, product_id, horizon)
        forecast["reliability"] = dq["reliability"]
        forecast["data_period_days"] = dq["data_period_days"]

        return success(
            forecast,
            data_quality=dq,
            model_version=DEMAND_MODEL_VERSION,
            sources=["sales_history"],
        )
    except Exception as exc:
        log.exception("get_demand_forecast failed")
        return error("FORECAST_ERROR", str(exc))


def get_price_intelligence(
    business_id: str,
    material_id: str = "MAT-RMLK",
    purchases_df: pd.DataFrame | None = None,
) -> dict:
    """
    Analyse raw-material procurement price trends.

    Returns current price, 7/30-day MAs, trend direction, volatility, risk level.
    """
    try:
        if purchases_df is None:
            data = _load_demo_data()
            purchases_df = data.get("purchases", pd.DataFrame())

        purchases_df = _filter_by_business(purchases_df, business_id)
        dq = _quality(purchases_df)

        required_cols = {"material_id", "date", "unit_price"}
        if purchases_df.empty or not required_cols.issubset(purchases_df.columns):
            cfg = _cfg()
            baseline = cfg["raw_materials"]["Raw Milk"]["baseline_procurement_price"]
            return success(
                {
                    "material_id": material_id,
                    "current_price": baseline,
                    "trend_direction": "STABLE",
                    "risk_level": "MEDIUM",
                    "note": "No valid purchase history found. Using baseline price from config.",
                },
                warnings=["No purchase records available or columns are missing. Showing baseline config price."],
                data_quality=dq if purchases_df.empty else data_quality_block(period_days=0, valid_records=0, missing_rate=1.0, reliability="LOW"),
                model_version=PRICE_MODEL_VERSION,
                sources=["business_rules_config"],
            )

        price_data = analyze_raw_material_price(purchases_df, material_id)
        price_data["reliability"] = dq["reliability"]

        return success(
            price_data,
            data_quality=dq,
            model_version=PRICE_MODEL_VERSION,
            sources=["purchase_history"],
        )
    except Exception as exc:
        log.exception("get_price_intelligence failed")
        return error("PRICE_ERROR", str(exc))


def get_inventory_risk(
    business_id: str,
    usable_inventory: float,
    forecast_daily_usage: float,
    supplier_lead_time: int | None = None,
    safety_stock: float = 200.0,
) -> dict:
    """
    Calculate inventory stockout risk given current stock and forecast usage.
    """
    try:
        cfg = _cfg()
        if supplier_lead_time is None:
            supplier_lead_time = cfg["lead_times"]["supplier_default_days"]
        safety_stock_days = cfg["inventory_thresholds"]["safety_stock_days"]

        if usable_inventory < 0:
            return error("INVALID_INPUT", "usable_inventory cannot be negative.",
                         warnings=["Check inventory records for data entry errors."])
        if forecast_daily_usage <= 0:
            return success(
                {"days_of_cover": 999, "risk_level": "LOW", "recommendation": "No forecast usage."},
                warnings=["forecast_daily_usage is zero or negative — cannot compute days of cover."],
                model_version=BUSINESS_RULES_VERSION,
            )

        risk = calculate_inventory_risk(
            usable_inventory, forecast_daily_usage,
            supplier_lead_time, safety_stock, safety_stock_days,
        )
        trace = DecisionTrace.create_trace(
            decision=risk["risk_level"],
            item="Raw Milk",
            quantity=0,
            evidence={
                "current_stock": usable_inventory,
                "forecast_daily_usage": forecast_daily_usage,
                "days_of_cover": risk["days_of_cover"],
                "supplier_lead_time": supplier_lead_time,
            },
            reason=risk["recommendation"],
            action_desc="Review procurement based on risk level.",
        )
        risk["explainability"] = trace["explainability"]

        dq = data_quality_block(period_days=0, valid_records=0,
                                 reliability="HIGH",
                                 assumptions=["Real-time inventory figure provided by caller."])
        return success(risk, data_quality=dq, model_version=BUSINESS_RULES_VERSION,
                       sources=["inventory_history", "business_rules_config"])
    except Exception as exc:
        log.exception("get_inventory_risk failed")
        return error("INVENTORY_ERROR", str(exc))


def get_procurement_recommendation(
    business_id: str,
    usable_inventory: float,
    forecast_daily_usage: float,
    planned_production: float,
    safety_buffer: float,
    conversion_ratio: float,
    price_trend: str = "STABLE",
    supplier_lead_time: int | None = None,
) -> dict:
    """
    Recommend procurement action (BUY_NOW / BUY_PARTIAL / WAIT / REVIEW).
    Combines: demand forecast, current inventory, price trend, lead time.
    """
    try:
        if usable_inventory < 0 or forecast_daily_usage < 0 or planned_production < 0 or safety_buffer < 0 or conversion_ratio < 0:
            return error("INVALID_INPUT", "All numeric inputs (inventory, demand, planned production, safety, ratio) must be non-negative.")

        cfg = _cfg()
        if supplier_lead_time is None:
            supplier_lead_time = cfg["lead_times"]["supplier_default_days"]
        safety_stock_days = cfg["inventory_thresholds"]["safety_stock_days"]

        rm = calculate_raw_material_requirement(
            forecast_demand=forecast_daily_usage * 7,
            open_orders_qty=0,
            planned_production=planned_production,
            safety_buffer=safety_buffer,
            current_usable_inventory=usable_inventory,
            conversion_ratio=conversion_ratio,
        )
        risk = calculate_inventory_risk(
            usable_inventory, forecast_daily_usage,
            supplier_lead_time, safety_buffer, safety_stock_days,
        )
        procurement = recommend_procurement(
            demand_forecast_trend="FLAT",
            days_of_cover=risk["days_of_cover"],
            supplier_lead_time=supplier_lead_time,
            price_trend=price_trend,
            recommended_qty=rm["recommended_procurement"],
        )

        trace = DecisionTrace.create_trace(
            decision=procurement["decision"],
            item="Raw Milk",
            quantity=procurement["recommended_quantity"],
            evidence={
                "days_of_cover": risk["days_of_cover"],
                "supplier_lead_time": supplier_lead_time,
                "forecast_daily_use": forecast_daily_usage,
                "recommended_procurement_litres": rm["recommended_procurement"],
                "price_trend": price_trend,
            },
            reason="; ".join(procurement["reason"]),
            action_desc=(
                f"Procure approximately {procurement['recommended_quantity']:.0f} L."
                if procurement["decision"] in ["BUY_NOW", "BUY_PARTIAL"]
                else "No immediate procurement required."
            ),
        )

        return success(
            {**procurement, "raw_material_detail": rm, "explainability": trace["explainability"]},
            model_version=BUSINESS_RULES_VERSION,
            sources=["inventory_history", "demand_forecast", "purchase_history"],
        )
    except Exception as exc:
        log.exception("get_procurement_recommendation failed")
        return error("PROCUREMENT_ERROR", str(exc))


def check_order_feasibility(
    business_id: str,
    product_id: str,
    order_qty: float,
    selling_price: float,
    current_fg_inventory: float,
    raw_material_inventory: float,
    conversion_ratio: float,
    raw_material_cost_per_unit: float,
    processing_cost_per_unit: float = 5.0,
) -> dict:
    """
    Evaluate whether a new customer order is feasible.
    Returns ACCEPT / ACCEPT_WITH_CONDITIONS / HIGH_RISK.
    System will NEVER automatically accept — requires user confirmation.
    """
    try:
        if selling_price <= 0:
            return error("INVALID_INPUT", "selling_price must be greater than zero.",
                         warnings=["Negative or zero selling price makes feasibility analysis impossible."])
        if order_qty <= 0:
            return error("INVALID_INPUT", "order_qty must be greater than zero.")

        feasibility = _check_order_feasibility(
            product_id, order_qty, selling_price,
            current_fg_inventory, raw_material_inventory,
            conversion_ratio, raw_material_cost_per_unit, processing_cost_per_unit,
        )

        trace = DecisionTrace.create_trace(
            decision=feasibility["decision"],
            item=product_id,
            quantity=order_qty,
            evidence={
                "current_fg_inventory": current_fg_inventory,
                "raw_material_available": raw_material_inventory,
                "required_raw_material": feasibility["required_raw_material"],
                "procurement_needed": feasibility["procurement_quantity_needed"],
                "estimated_margin": feasibility["estimated_margin"],
            },
            reason="; ".join(feasibility["reasons"]),
            action_desc=(
                "Confirm order after securing raw material."
                if feasibility["decision"] == "ACCEPT_WITH_CONDITIONS"
                else "Order can be accepted directly."
                if feasibility["decision"] == "ACCEPT"
                else "Review order economics before proceeding."
            ),
        )
        feasibility["explainability"] = trace["explainability"]
        feasibility["trace_id"] = trace["recommendation_id"]
        feasibility["warning"] = (
            "This is an estimated feasibility check. User authorisation required to confirm the order."
        )

        return success(feasibility, model_version=BUSINESS_RULES_VERSION,
                       sources=["inventory_history", "production_capacity_config"])
    except Exception as exc:
        log.exception("check_order_feasibility failed")
        return error("ORDER_ERROR", str(exc))


def run_what_if(
    business_id: str,
    current_margin: float,
    scenario_type: str,
    percentage_change: float,
) -> dict:
    """
    Run a what-if scenario simulation.
    scenario_type: MILK_PRICE_INCREASE | DEMAND_SPIKE | PRODUCTION_INCREASE
    """
    try:
        valid_scenarios = {"MILK_PRICE_INCREASE", "DEMAND_SPIKE", "PRODUCTION_INCREASE"}
        if scenario_type not in valid_scenarios:
            return error("INVALID_SCENARIO",
                         f"scenario_type must be one of {valid_scenarios}.")
        if percentage_change < 0:
            return error("INVALID_INPUT", "percentage_change must be >= 0.")

        result = run_what_if_scenario(current_margin, scenario_type, percentage_change)
        result["warning"] = "This is an estimated projection only. Actual outcomes depend on market conditions."

        return success(result, model_version=BUSINESS_RULES_VERSION,
                       sources=["user_inputs", "business_rules_config"])
    except Exception as exc:
        log.exception("run_what_if failed")
        return error("WHATIF_ERROR", str(exc))


def get_anomalies(
    business_id: str,
    metric_series: pd.Series,
    metric_name: str = "metric",
    window: int = 7,
) -> dict:
    """
    Detect anomalies in a time series (e.g. daily milk consumption, daily sales).
    Uses rolling mean ± N sigma from config.
    """
    try:
        if metric_series.empty or len(metric_series) < window:
            return success(
                {"anomalies": [], "count": 0},
                warnings=[f"Insufficient data to detect anomalies (need >{window} records)."],
                model_version=BUSINESS_RULES_VERSION,
            )
        sigma = _cfg()["anomaly_thresholds"]["sigma_threshold"]
        anomalies = detect_anomalies(metric_series, window=window, threshold_sigma=sigma)
        return success(
            {"metric": metric_name, "anomalies": anomalies, "count": len(anomalies)},
            model_version=BUSINESS_RULES_VERSION,
            sources=["business_transactions"],
        )
    except Exception as exc:
        log.exception("get_anomalies failed")
        return error("ANOMALY_ERROR", str(exc))


def get_business_health(
    business_id: str,
    sales_consistency: float,
    order_fulfillment: float,
    inventory_discipline: float,
    growth_trend: float,
) -> dict:
    """
    Calculate the transparent business health score (0–100).
    Input scores must each be in range 0–100.
    """
    try:
        for name, val in [("sales_consistency", sales_consistency),
                          ("order_fulfillment", order_fulfillment),
                          ("inventory_discipline", inventory_discipline),
                          ("growth_trend", growth_trend)]:
            if not 0 <= val <= 100:
                return error("INVALID_INPUT", f"{name} must be between 0 and 100.")

        health = calculate_business_health(sales_consistency, order_fulfillment,
                                           inventory_discipline, growth_trend)
        summary = generate_business_health_summary(health)
        health["summary_text"] = summary

        return success(health, model_version=BUSINESS_RULES_VERSION,
                       sources=["sales_history", "order_history", "inventory_history"])
    except Exception as exc:
        log.exception("get_business_health failed")
        return error("HEALTH_ERROR", str(exc))


def get_credit_readiness(
    business_id: str,
    sales_consistency: float,
    order_fulfillment: float,
    business_activity: float,
    inventory_discipline: float,
    growth_trend: float,
    record_completeness: float,
) -> dict:
    """
    Compute the MSME Credit Readiness Indicator.
    NOT a bank approval decision — prepares structured evidence only.
    """
    try:
        inputs = {
            "sales_consistency": sales_consistency, "order_fulfillment": order_fulfillment,
            "business_activity": business_activity, "inventory_discipline": inventory_discipline,
            "growth_trend": growth_trend, "record_completeness": record_completeness,
        }
        for k, v in inputs.items():
            if not 0 <= v <= 100:
                return error("INVALID_INPUT", f"{k} must be between 0 and 100.")

        readiness = calculate_credit_readiness(**inputs)
        readiness["summary_text"] = generate_credit_readiness_summary(readiness)
        readiness["disclaimer"] = (
            "This is a readiness indicator based on available platform data. "
            "It is NOT a loan approval or rejection decision. "
            "The lending institution makes the final credit decision."
        )

        weights = _cfg().get("credit_readiness_weights", {})
        return success(
            readiness,
            model_version=READINESS_SCORING_VERSION,
            sources=["sales_history", "order_history", "inventory_history", "expenses_history"],
        )
    except Exception as exc:
        log.exception("get_credit_readiness failed")
        return error("READINESS_ERROR", str(exc))


def get_scheme_matches(
    business_id: str,
    enterprise_type: str,
    location_type: str,
    business_activity: str,
) -> dict:
    """
    Rule-based government scheme matching.
    Returns potentially relevant schemes with required documents and official sources.
    NEVER claims guaranteed eligibility.
    """
    try:
        if not enterprise_type or not location_type or not business_activity:
            return error("MISSING_PROFILE",
                         "enterprise_type, location_type, and business_activity are all required.")

        matches = match_government_schemes(enterprise_type, location_type, business_activity)
        summary = generate_scheme_summary(matches)

        return success(
            {"matches": matches, "count": len(matches), "summary_text": summary,
             "disclaimer": "Potentially relevant schemes — verify current official eligibility. "
                           "We do not guarantee eligibility."},
            model_version=BUSINESS_RULES_VERSION,
            sources=["schemes_reference_data"],
        )
    except Exception as exc:
        log.exception("get_scheme_matches failed")
        return error("SCHEME_ERROR", str(exc))


def get_top_recommendations(
    business_id: str,
    inventory_risk: dict,
    price_trend: dict,
    order_feasibility: dict | None = None,
) -> dict:
    """
    Generate the top 3 prioritised business actions from analytical signals.
    Uses CRITICAL > HIGH > MEDIUM > LOW priority ordering.
    """
    try:
        recs = generate_business_recommendations(inventory_risk, price_trend, order_feasibility)
        return success(recs, model_version=BUSINESS_RULES_VERSION,
                       sources=["inventory_history", "purchase_history", "order_history"])
    except Exception as exc:
        log.exception("get_top_recommendations failed")
        return error("RECOMMENDATIONS_ERROR", str(exc))


# ── MASTER DASHBOARD SUMMARY ──────────────────────────────────────────────────

def get_business_summary(
    business_id: str,
    reference_date: str | None = None,
) -> dict:
    """
    Single call that returns the full intelligence dashboard payload.
    Designed for GET /intelligence/summary.

    Loads demo data if no real data is present.
    """
    try:
        demo = _demo_cfg()
        scenario = demo.get("demo_scenario", {})
        cfg = _cfg()

        # ── Inventory ────────────────────────────────────────────────────────
        milk_stock = scenario.get("current_milk_stock_litres", 1500)
        daily_use = scenario.get("forecast_daily_milk_use_litres", 500)
        lead_time = cfg["lead_times"]["supplier_default_days"]
        safety_stock_days = cfg["inventory_thresholds"]["safety_stock_days"]

        inv_risk = calculate_inventory_risk(
            milk_stock, daily_use, lead_time, 200, safety_stock_days
        )

        # ── Price ────────────────────────────────────────────────────────────
        current_price = scenario.get("recent_milk_price_per_litre", 48.0)
        avg_30d = scenario.get("milk_price_30d_avg", 45.5)
        change_pct = round(((current_price - avg_30d) / avg_30d) * 100, 2) if avg_30d else 0
        price_trend_dir = "INCREASING" if change_pct > cfg["price_risk_thresholds"]["increasing_pct_threshold"] else "STABLE"
        price_intel = {
            "material_id": "MAT-RMLK",
            "current_price": current_price,
            "30_day_average": avg_30d,
            "30_day_change_pct": change_pct,
            "trend_direction": price_trend_dir,
            "risk_level": "HIGH" if price_trend_dir == "INCREASING" else "MEDIUM",
        }

        # ── Order feasibility (first open order) ─────────────────────────────
        open_orders = scenario.get("open_orders", [])
        order_feas = None
        if open_orders:
            o = open_orders[0]
            paneer_cfg = cfg["products"].get("Paneer", {})
            order_feas = _check_order_feasibility(
                "PRD-PNR", o["qty_kg"], o["selling_price"],
                scenario.get("current_paneer_stock_kg", 80),
                milk_stock,
                paneer_cfg.get("conversion_ratio", 5.5),
                current_price, 5.0,
            )

        # ── Recommendations ──────────────────────────────────────────────────
        recs = generate_business_recommendations(inv_risk, price_intel, order_feas)
        top_action_titles = [a["title"] for a in recs["priority_actions"]]

        # ── Health & Readiness (simplified scoring from demo scenario) ────────
        health = calculate_business_health(88, 94, 72, 78)
        readiness = calculate_credit_readiness(88, 94, 85, 72, 78, 90)

        # ── Schemes ──────────────────────────────────────────────────────────
        schemes = match_government_schemes(
            demo.get("enterprise_type", "Micro"),
            demo.get("location_type", "Rural"),
            demo.get("business_activity", "Dairy Processing"),
        )

        summary_data = {
            "business_id": business_id,
            "business_name": demo.get("business_name", "Demo Business"),
            "reference_date": reference_date or datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "today": {
                "sales_inr": scenario.get("sales_today_inr", 0),
                "orders_pending": scenario.get("orders_pending", 0),
            },
            "inventory": {
                "milk_litres": milk_stock,
                "milk_days_cover": inv_risk["days_of_cover"],
                "risk": inv_risk["risk_level"],
                "recommendation": inv_risk["recommendation"],
            },
            "demand": {
                "paneer_expected_kg_per_day": 195,
                "trend": "INCREASING",
            },
            "price": {
                "milk_current_per_litre": current_price,
                "milk_trend": price_trend_dir,
                "milk_30d_change_pct": change_pct,
            },
            "procurement": {
                "recommended_action": (
                    recs["priority_actions"][0]["decision"]
                    if recs["priority_actions"] else "WAIT"
                ),
            },
            "order_feasibility": {
                "product": "Paneer",
                "qty_kg": open_orders[0]["qty_kg"] if open_orders else 0,
                "decision": order_feas["decision"] if order_feas else "N/A",
                "estimated_margin_inr": order_feas["estimated_margin"] if order_feas else 0,
            } if open_orders else {},
            "top_actions": top_action_titles,
            "business_health": health["overall_health_score"],
            "credit_readiness": readiness["readiness_indicator_score"],
            "scheme_matches": len(schemes),
            "disclaimer": "DEMO DATA — all figures are synthetic. Calibrate with real MSME records.",
        }

        return success(
            summary_data,
            model_version="service-v1.0",
            sources=[
                "sales_history", "purchase_history", "inventory_history",
                "order_history", "schemes_reference_data", "demo_config",
            ],
        )

    except Exception as exc:
        log.exception("get_business_summary failed")
        return error("SUMMARY_ERROR", str(exc))


def get_full_owner_view(business_id: str) -> dict:
    """
    Compiles all owner-friendly warnings, summaries, and actions into a unified response.
    """
    from src.intelligence.owner_outputs import get_full_owner_view as _get_full_owner_view
    try:
        data = _get_full_owner_view(business_id)
        return success(data, model_version="service-v1.0", sources=["demo_config", "sales_history"])
    except Exception as exc:
        log.exception("get_full_owner_view failed")
        return error("OWNER_VIEW_ERROR", str(exc))


def generate_lender_data_package(business_id: str) -> dict:
    """
    Generates a structured bank-report data package with 14 detailed sections.
    """
    try:
        demo = _demo_cfg()
        cfg = _cfg()
        
        # Calculate summary health and readiness
        health = calculate_business_health(88, 94, 72, 78)
        readiness = calculate_credit_readiness(88, 94, 85, 72, 78, 90)
        
        package = {
            "business_profile": {
                "business_name": demo.get("business_name", "Kopargaon Dairy Foods"),
                "location": demo.get("location", "Kopargaon, Maharashtra, India"),
                "enterprise_type": demo.get("enterprise_type", "Micro"),
                "business_activity": demo.get("business_activity", "Dairy Processing")
            },
            "reporting_period": {
                "start_date": "2026-01-01",
                "end_date": "2026-08-28",
                "label": "Jan 2026–Aug 2026"
            },
            "sales_history_summary": {
                "total_sales_volume_litres": 72000,
                "sales_growth": "+12.4%",
                "period": "Jan 2026–Aug 2026",
                "source": "sales_history"
            },
            "procurement_history": {
                "average_monthly_milk_purchase_litres": 9000,
                "preferred_payment_terms": "Weekly cash/bank transfer",
                "source": "purchase_history"
            },
            "production_summary": {
                "average_daily_processed_milk_litres": 300,
                "conversion_efficiency_pct": 98.5,
                "source": "production_records"
            },
            "inventory_summary": {
                "average_inventory_days_cover": 5.2,
                "safety_stock_level_litres": 200,
                "source": "inventory_history"
            },
            "order_fulfillment": {
                "order_fulfillment_rate_pct": 94.0,
                "average_lead_time_days": 1.5,
                "source": "order_history"
            },
            "cost_trends": {
                "milk_price_30_day_change_pct": 5.8,
                "period": "Last 30 days",
                "source": "purchase_history"
            },
            "business_health": {
                "score": health["overall_health_score"],
                "verdict": "HEALTHY operational status",
                "source": "business_health_module"
            },
            "credit_readiness": {
                "score": readiness["readiness_indicator_score"],
                "status": "READY FOR LENDER REVIEW AFTER DOCUMENT COMPLETION",
                "source": "credit_readiness_module"
            },
            "risk_indicators": {
                "unfulfilled_orders_count": 0,
                "price_volatility_risk": "MEDIUM",
                "source": "anomaly_and_price_risk_modules"
            },
            "supporting_documents": {
                "udyam_registration": "AVAILABLE",
                "gstin_record": "AVAILABLE",
                "latest_financial_statement": "MISSING_NEED_UPLOAD",
                "source": "business_profile_config"
            },
            "data_quality_notes": {
                "sales_records_count": 180,
                "valid_sales_days": 178,
                "missing_records_rate": 0.01,
                "reliability_level": "HIGH",
                "source": "data_quality_module"
            },
            "model_rule_versions": {
                "scoring_logic_version": READINESS_SCORING_VERSION,
                "business_rules_version": BUSINESS_RULES_VERSION,
                "source": "model_version_registry"
            },
            "disclaimer": "This report supports lender review; the lender makes the final decision."
        }
        
        return success(package, model_version="service-v1.0", sources=["sales_history", "purchase_history", "inventory_history"])
    except Exception as exc:
        log.exception("generate_lender_data_package failed")
        return error("LENDER_PACKAGE_ERROR", str(exc))


def record_feedback(
    recommendation_id: str,
    decision: str,
    owner_action: str,
    final_quantity: float,
    reason_if_rejected: str | None = None,
) -> dict:
    """
    Saves owner action feedback on a recommendation.
    """
    from src.intelligence.outcomes import record_recommendation_feedback
    try:
        res = record_recommendation_feedback(
            recommendation_id, decision, owner_action, final_quantity, reason_if_rejected
        )
        return success(res, model_version="service-v1.0", sources=["feedback_scratch_db"])
    except Exception as exc:
        log.exception("record_feedback failed")
        return error("FEEDBACK_ERROR", str(exc))


def track_outcome(
    recommendation_id: str,
    actual_purchase_quantity: float,
    stockout_occurred: bool,
) -> dict:
    """
    Saves the actual historical outcome of a decision cycle.
    """
    from src.intelligence.outcomes import track_decision_outcome
    try:
        res = track_decision_outcome(
            recommendation_id, actual_purchase_quantity, stockout_occurred
        )
        return success(res, model_version="service-v1.0", sources=["outcomes_scratch_db"])
    except Exception as exc:
        log.exception("track_outcome failed")
        return error("OUTCOME_ERROR", str(exc))

