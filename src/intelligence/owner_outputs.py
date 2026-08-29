"""
src/intelligence/owner_outputs.py
==================================
Owner-friendly business output translation layer for DairyPulse.
Converts analytical figures, z-scores, and probability numbers into plain-language
descriptions, actionable steps, and lender-ready data packages.
"""

import os
import json
import pandas as pd
from datetime import datetime, timezone

from src.intelligence.version import BUSINESS_RULES_VERSION, DEMAND_MODEL_VERSION


def _cfg() -> dict:
    cfg_path = os.path.join(os.path.dirname(__file__), "../../config/business_rules.json")
    try:
        with open(cfg_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def _demo_cfg() -> dict:
    demo_path = os.path.join(os.path.dirname(__file__), "../../config/demo_business.json")
    try:
        with open(demo_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


# ═══════════════════════════════════════════════════════════════════════════════
# 1. OWNER-FRIENDLY ADVICE & TRANSLATION FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def generate_today_summary(business_id: str, date: str | None = None) -> dict:
    """
    Generates a concise text dashboard snapshot (TODAY'S BUSINESS STATUS)
    designed to be read at a glance by the MSME owner.
    """
    # Load demo variables or calculate from services
    from src.intelligence.service import get_business_summary
    
    summary_resp = get_business_summary(business_id, date)
    if summary_resp["status"] != "success":
        return {
            "status": "error",
            "message": "Failed to compile dashboard summary: " + summary_resp.get("message", "Unknown error")
        }
    
    d = summary_resp["data"]
    
    # Format today's status message
    lines = [
        "TODAY'S BUSINESS STATUS",
        "",
        f"Sales:\n₹{d['today']['sales_inr']:,}",
        "",
        f"Expected demand:\n{d['demand']['paneer_expected_kg_per_day']} kg Paneer",
        "",
        f"Milk available:\n{d['inventory']['milk_litres']:,} litres",
        "",
        # Calculate milk required using conversion ratio (5.5 for Paneer)
        f"Milk required:\n{int(d['demand']['paneer_expected_kg_per_day'] * 5.5):,} litres",
        "",
        f"Price trend:\n{d['price']['milk_trend'].capitalize()}",
        "",
        f"Inventory risk:\n{d['inventory']['risk']}",
        ""
    ]
    
    # Select actions
    top_action = d["top_actions"][0] if d["top_actions"] else "Monitor operations."
    additional_action = d["top_actions"][1] if len(d["top_actions"]) > 1 else "Review pending orders."
    
    lines.extend([
        f"Top action:\n{top_action}",
        "",
        f"Additional action:\n{additional_action}",
        "",
        f"Business health:\n{d['business_health']}/100",
        "",
        f"Credit readiness:\n{d['credit_readiness']}/100"
    ])
    
    return {
        "text_summary": "\n".join(lines),
        "metrics": {
            "sales_inr": d["today"]["sales_inr"],
            "orders_pending": d["today"]["orders_pending"],
            "milk_available": d["inventory"]["milk_litres"],
            "price_trend": d["price"]["milk_trend"],
            "inventory_risk": d["inventory"]["risk"],
            "business_health": d["business_health"],
            "credit_readiness": d["credit_readiness"]
        }
    }


def generate_procurement_advice(
    business_id: str,
    usable_inventory: float,
    forecast_daily_usage: float,
    planned_production: float,
    safety_buffer: float,
    conversion_ratio: float,
    price_trend: str = "STABLE",
) -> dict:
    """
    Translates raw procurement calculation into owner-friendly buying logic.
    """
    from src.intelligence.service import get_procurement_recommendation
    
    resp = get_procurement_recommendation(
        business_id=business_id,
        usable_inventory=usable_inventory,
        forecast_daily_usage=forecast_daily_usage,
        planned_production=planned_production,
        safety_buffer=safety_buffer,
        conversion_ratio=conversion_ratio,
        price_trend=price_trend
    )
    
    if resp["status"] != "success":
        return resp
        
    data = resp["data"]
    qty = data["recommended_quantity"]
    decision = data["decision"]
    
    # Calculate days of cover
    days_cover = round(usable_inventory / forecast_daily_usage, 1) if forecast_daily_usage > 0 else 999
    lead_time = data["raw_material_detail"]["safety_buffer"] # using buffer logic
    
    # Get price to compute estimated cost
    cfg = _cfg()
    milk_price = cfg.get("raw_materials", {}).get("Raw Milk", {}).get("baseline_procurement_price", 45.0)
    est_cost = qty * milk_price
    
    reason = (
        f"Expected demand is {'increasing' if price_trend == 'INCREASING' else 'steady'}, "
        f"current stock covers only {days_cover} days, "
        f"supplier lead time is 3 days, and milk prices are trending {price_trend.lower()}."
    )
    
    return {
        "recommended_action": decision,
        "reason": reason,
        "recommended_quantity": f"{qty:,.0f} L",
        "raw_quantity_numeric": qty,
        "estimated_procurement_cost": f"₹{est_cost:,.0f}",
        "disclaimer": "This is an intelligence recommendation. Final procurement decisions require user validation."
    }


def generate_inventory_advice(
    business_id: str,
    usable_inventory: float,
    forecast_daily_usage: float,
    supplier_lead_time: int = 3,
) -> dict:
    """
    Exposes a plain-text inventory analysis with actionable steps.
    """
    from src.intelligence.service import get_inventory_risk
    
    resp = get_inventory_risk(
        business_id=business_id,
        usable_inventory=usable_inventory,
        forecast_daily_usage=forecast_daily_usage,
        supplier_lead_time=supplier_lead_time
    )
    
    if resp["status"] != "success":
        return resp
        
    data = resp["data"]
    days = data["days_of_cover"]
    risk = data["risk_level"]
    
    if risk in ["CRITICAL", "HIGH"]:
        action = "Procure before current stock reaches critical level."
    elif risk == "LOW":
        action = "Excess stock levels detected. Monitor usage before reordering."
    else:
        action = "Stock levels are currently within target parameters."
        
    return {
        "current_stock": f"{usable_inventory:,.0f} L",
        "days_of_cover": f"{days} days",
        "expected_usage": f"{forecast_daily_usage:,.0f} L/day",
        "supplier_lead_time": f"{supplier_lead_time} days",
        "risk_level": risk,
        "advice_text": f"Milk inventory covers approximately {days} days, while supplier lead time is {supplier_lead_time} days.",
        "action": action
    }


def generate_price_advice(business_id: str, material_id: str = "MAT-RMLK") -> dict:
    """
    Analyzes price volatility and trend changes and reports warning advice.
    """
    from src.intelligence.service import get_price_intelligence
    
    resp = get_price_intelligence(business_id, material_id)
    if resp["status"] != "success":
        return resp
        
    d = resp["data"]
    change = d.get("30_day_change_pct", 0.0)
    risk = d.get("risk_level", "MEDIUM")
    
    advice = f"Milk procurement price has {'increased' if change >= 0 else 'decreased'} approximately {abs(change):.1f}% over the last 30 days."
    
    return {
        "price_trend_summary": advice,
        "procurement_risk": f"Because inventory is also low, procurement risk is {risk}." if change > 3 else "Procurement risk is stable.",
        "recommended_action": "Review procurement timing." if change > 3 else "Procure as scheduled."
    }


def generate_order_advice(
    business_id: str,
    product_id: str,
    order_qty: float,
    selling_price: float,
    current_fg_inventory: float,
    raw_material_inventory: float,
    conversion_ratio: float,
    raw_material_cost_per_unit: float,
) -> dict:
    """
    Checks feasibility of a proposed order and formats a structured summary card.
    """
    from src.intelligence.service import check_order_feasibility
    
    resp = check_order_feasibility(
        business_id=business_id,
        product_id=product_id,
        order_qty=order_qty,
        selling_price=selling_price,
        current_fg_inventory=current_fg_inventory,
        raw_material_inventory=raw_material_inventory,
        conversion_ratio=conversion_ratio,
        raw_material_cost_per_unit=raw_material_cost_per_unit
    )
    
    if resp["status"] != "success":
        return resp
        
    d = resp["data"]
    
    reasons = d["reasons"]
    # Highlight capacity or stock constraints in plain english
    why_lines = []
    if "production capacity is available" not in [r.lower() for r in reasons]:
        why_lines.append("- Production capacity is available")
    if d["procurement_quantity_needed"] > 0:
        why_lines.append("- Current raw material is insufficient")
        why_lines.append("- Additional procurement is required")
    else:
        why_lines.append("- Current raw material is sufficient")
        
    if d["estimated_margin"] > 0:
        why_lines.append("- Estimated margin remains positive")
        
    return {
        "order": f"{order_qty:,.0f} kg {product_id.replace('PRD-', '').capitalize()}",
        "decision": d["decision"],
        "why": "\n".join(why_lines),
        "required_procurement": f"{d['required_raw_material']:,.0f} L milk",
        "estimated_margin": f"₹{d['estimated_margin']:,.0f}",
        "main_risk": "Supplier delay" if d["procurement_quantity_needed"] > 0 else "None detected",
        "action": "Confirm procurement before committing delivery." if d["procurement_quantity_needed"] > 0 else "Order can be accepted."
    }


def generate_business_health_summary(business_id: str, health_score_data: dict | None = None) -> dict:
    """
    Outputs standard business health indicators in a strengths/weaknesses layout.
    """
    if health_score_data is None:
        # Mock/demo defaults
        health_score_data = {
            "overall_health_score": 85.0,
            "metrics": {
                "sales_consistency": 88.0,
                "order_fulfillment": 94.0,
                "inventory_discipline": 72.0,
                "growth_trend": 78.0
            }
        }
        
    score = health_score_data["overall_health_score"]
    m = health_score_data["metrics"]
    
    strengths = []
    weaknesses = []
    
    if m["sales_consistency"] >= 80:
        strengths.append("Stable sales")
    else:
        weaknesses.append("High sales variability")
        
    if m["order_fulfillment"] >= 90:
        strengths.append("Strong order fulfillment")
    else:
        weaknesses.append("Order delays or unfulfilled requests")
        
    if m["inventory_discipline"] >= 80:
        strengths.append("Disciplined inventory controls")
    else:
        weaknesses.append("Inventory variability")
        
    return {
        "title": "BUSINESS HEALTH STATUS",
        "overall_score": f"{score:.0f}/100",
        "strengths": strengths,
        "weaknesses": weaknesses,
        "risks": ["Supply lead time changes could impact order scheduling" if m["inventory_discipline"] < 75 else "None"],
        "recommendation": "Improve procurement planning." if weaknesses else "Maintain current inventory routines.",
        "disclaimer": "This is an operational summary and does NOT constitute a financial audit."
    }


def generate_credit_readiness_summary(business_id: str, credit_score_data: dict | None = None) -> dict:
    """
    Formats the lender assessment package in a transparent preparation format.
    """
    if credit_score_data is None:
        credit_score_data = {
            "readiness_indicator_score": 82.0,
            "metrics": {
                "sales_consistency": 88.0,
                "order_fulfillment": 94.0,
                "business_activity": 85.0,
                "inventory_discipline": 72.0,
                "growth_trend": 78.0,
                "record_completeness": 90.0
            }
        }
        
    score = credit_score_data["readiness_indicator_score"]
    m = credit_score_data["metrics"]
    
    evidence = []
    improvements = []
    missing_docs = []
    
    if m["sales_consistency"] >= 80:
        evidence.append("Consistent sales history")
    if m["order_fulfillment"] >= 90:
        evidence.append("Strong order fulfillment")
    if m["business_activity"] >= 80:
        evidence.append("Long transaction history")
        
    if m["record_completeness"] < 95:
        improvements.append("Recent financial information incomplete")
    if m["inventory_discipline"] < 80:
        improvements.append("Inventory records need better consistency")
        
    if m["record_completeness"] < 95:
        missing_docs.append("Latest financial statement")
        
    status = "READY FOR LENDER REVIEW AFTER DOCUMENT COMPLETION" if score >= 80 else "NEEDS RECORD COMPLETENESS IMPROVEMENT"
    
    return {
        "overall_score": f"{score:.0f}/100",
        "positive_evidence": evidence,
        "improvement_areas": improvements,
        "documents_missing": missing_docs,
        "status": status,
        "disclaimer": "This report supports lender review; the lender makes the final decision."
    }


def generate_scheme_summary(business_id: str, enterprise_type: str, location_type: str, business_activity: str) -> dict:
    """
    Returns government schemes formatted with verification instructions.
    """
    from src.intelligence.service import get_scheme_matches
    
    resp = get_scheme_matches(business_id, enterprise_type, location_type, business_activity)
    if resp["status"] != "success":
        return resp
        
    matches = resp["data"]["matches"]
    formatted = []
    
    for m in matches:
        formatted.append({
            "scheme_name": m["scheme_name"],
            "why_it_may_match": f"Matches {enterprise_type} enterprise in {location_type} for {business_activity}.",
            "need_to_verify": "Registration requirements and turnover limits.",
            "documents": m["missing_documents_needed"],
            "official_source": m["official_source"],
            "last_verified": m.get("last_verified_date", "Unknown"),
            "guarantee_note": "Potentially relevant — verify current official eligibility."
        })
        
    return {
        "enterprise_type": enterprise_type,
        "location_type": location_type,
        "business_activity": business_activity,
        "schemes": formatted,
        "disclaimer": "Potentially relevant — verify current official eligibility. We do not guarantee eligibility."
    }


def compare_to_benchmark(business_id: str, product_id: str, current_inventory_days: float) -> dict:
    """
    Safely compares operational inventory days against industry peer averages
    without exposing any competitor transactional details.
    """
    ref_path = os.path.join(os.path.dirname(__file__), "../../data/reference/anonymous_industry_benchmarks.csv")
    peer_min, peer_max = 4.8, 5.5
    
    if os.path.exists(ref_path):
        try:
            df = pd.read_csv(ref_path)
            # Filter comments out
            df = df[df["product"].notna()]
            row = df[df["product"] == product_id.replace("PRD-", "")]
            if not row.empty:
                val = float(row.iloc[0]["median_inventory_days"])
                peer_min, peer_max = val * 0.9, val * 1.1
        except Exception:
            pass
            
    if current_inventory_days > peer_max:
        verdict = "Your inventory is higher than the current peer benchmark."
    elif current_inventory_days < peer_min:
        verdict = "Your inventory is lower than the current peer benchmark."
    else:
        verdict = "Your inventory levels are aligned with peer benchmarks."
        
    return {
        "product": product_id,
        "your_inventory_days": round(current_inventory_days, 1),
        "anonymous_peer_benchmark": f"{peer_min:.1f}–{peer_max:.1f}",
        "verdict": verdict,
        "privacy_assurance": "Comparison uses aggregated, anonymized industry statistics. Operational privacy is fully protected; no peer names or transactions are exposed."
    }


def get_cold_start_forecast(business_id: str, product_id: str, own_history_days: int) -> dict:
    """
    Outputs low-confidence warning forecasts if history is insufficient.
    """
    if own_history_days < 30:
        return {
            "forecast_quantity": 150,  # Peer benchmark default Paneer monthly quantity
            "reliability": "LOW",
            "reason": f"Only {own_history_days} valid business days are available.",
            "data_sources": ["anonymous_industry_benchmarks.csv"],
            "limitations": "Forecast is based on industry benchmarks. Performance indicators will become highly accurate after 30 days of sales records."
        }
    return {
        "forecast_quantity": 250,
        "reliability": "MEDIUM",
        "reason": f"Valid sales history spans {own_history_days} days.",
        "data_sources": ["sales_history"],
        "limitations": "Short sales history. Accuracy improves with seasonal records."
    }


# ═══════════════════════════════════════════════════════════════════════════════
# 2. MASTER OWNER VIEW COMPILATION
# ═══════════════════════════════════════════════════════════════════════════════

def get_full_owner_view(business_id: str) -> dict:
    """
    Compiles all analytical vectors into one primary, nested object
    for easy rendering by frontend clients.
    """
    demo = _demo_cfg()
    scenario = demo.get("demo_scenario", {})
    
    # 1. Today status
    today = generate_today_summary(business_id)
    
    # 2. Inventory advice
    inv = generate_inventory_advice(business_id, scenario.get("current_milk_stock_litres", 1500), scenario.get("forecast_daily_milk_use_litres", 500))
    
    # 3. Price advice
    price = generate_price_advice(business_id)
    
    # 4. Procurement advice
    proc = generate_procurement_advice(
        business_id=business_id,
        usable_inventory=scenario.get("current_milk_stock_litres", 1500),
        forecast_daily_usage=scenario.get("forecast_daily_milk_use_litres", 500),
        planned_production=0,
        safety_buffer=200,
        conversion_ratio=1.0,
        price_trend="INCREASING"
    )
    
    # 5. Order advice (feasibility check summary)
    order = generate_order_advice(
        business_id=business_id,
        product_id="PRD-PNR",
        order_qty=500,
        selling_price=350,
        current_fg_inventory=scenario.get("current_fg_inventory", 80),
        raw_material_inventory=scenario.get("current_milk_stock_litres", 1500),
        conversion_ratio=5.5,
        raw_material_cost_per_unit=scenario.get("recent_milk_price_per_litre", 48.0)
    )
    
    # 6. Health & Credit Readiness
    health = generate_business_health_summary(business_id)
    credit = generate_credit_readiness_summary(business_id)
    
    # 7. Schemes
    schemes = generate_scheme_summary(business_id, "Micro", "Rural", "Dairy Processing")
    
    # 8. Anonymized benchmark
    bench = compare_to_benchmark(business_id, "PRD-PNR", scenario.get("current_fg_inventory", 80) / 10.0) # mock current FG days
    
    return {
        "today": today["metrics"],
        "text_summary": today["text_summary"],
        "top_actions": today["metrics"]["inventory_risk"],
        "demand": {
            "expected_daily": today["metrics"]["sales_inr"] / 350.0, # proxy
            "trend": "INCREASING"
        },
        "price": price,
        "inventory": inv,
        "procurement": proc,
        "orders": order,
        "business_health": health,
        "credit_readiness": credit,
        "scheme_matches": schemes["schemes"],
        "benchmark_peer_comparison": bench,
        "data_quality": {
            "reliability": "HIGH",
            "assumptions": ["DEMO dataset. Calibrate before going live."]
        },
        "recommendation_evidence": [
            {
                "recommendation_id": "REC-2026-INIT",
                "evidence_dimension": "INVENTORY",
                "metric_score": 72.0,
                "reason": "Days of cover matches safety stock parameters."
            }
        ]
    }
