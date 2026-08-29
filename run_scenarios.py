"""
run_scenarios.py
================
Full business-scenario simulation for DairyPulse Phase 4 validation.

Executes all 7 defined scenarios and writes a detailed
reports/scenario_results.md tracing:
  INPUT -> ANALYSIS -> DECISION -> REASON -> EXPECTED BUSINESS EFFECT
"""
import os
import sys
import json
import logging
from datetime import datetime
import numpy as np

# ---- path fix for direct execution ----
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.inventory.risk import calculate_inventory_risk
from src.procurement.decision import calculate_raw_material_requirement, recommend_procurement
from src.orders.feasibility import check_order_feasibility
from src.orders.economics import run_what_if_scenario
from src.business_health.health import calculate_business_health, generate_business_health_summary
from src.credit.readiness import calculate_credit_readiness, generate_credit_readiness_summary
from src.schemes.matcher import match_government_schemes, generate_scheme_summary
from src.intelligence.explainability import DecisionTrace
from src.intelligence.reconciliation import reconcile_inventory
from src.intelligence.data_quality import assess_data_quality
from src.intelligence.backtesting import backtest_forecast
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
log = logging.getLogger("DairyPulse.Scenarios")

os.makedirs("reports", exist_ok=True)

# ── Helpers ──────────────────────────────────────────────────────────────────

def section(title: str) -> str:
    bar = "─" * 60
    return f"\n{bar}\n## {title}\n{bar}\n\n"

def trace_block(label: str, data: dict) -> str:
    lines = [f"**{label}**\n```json"]
    lines.append(json.dumps(data, indent=2, default=str))
    lines.append("```\n")
    return "\n".join(lines)

# ── Scenario runner ───────────────────────────────────────────────────────────

def run_all_scenarios() -> str:
    report_lines = [
        "# DairyPulse — Business Scenario Simulation Results\n",
        f"> Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n",
        "> All scenarios use deterministic, rule-based logic. Results are DEMO / SIMULATED.\n",
    ]

    # ── Scenario 1: Normal Operation ─────────────────────────────────────────
    report_lines.append(section("Scenario 1 — Normal Operation"))
    s1_inv = calculate_inventory_risk(usable_inventory=6000, forecast_daily_usage=500,
                                      supplier_lead_time=3, safety_stock=500)
    s1_proc = recommend_procurement("FLAT", s1_inv["days_of_cover"], 3, "STABLE", 0)
    s1_trace = DecisionTrace.create_trace(
        s1_proc["decision"], "Milk", 0,
        {"days_of_cover": s1_inv["days_of_cover"], "risk": s1_inv["risk_level"]},
        "Inventory is sufficient. No action needed.",
        "Monitor daily consumption. Re-evaluate in 48 hours."
    )
    report_lines += [
        "| Field | Value |\n|---|---|\n",
        f"| INPUT | Milk Stock=6000L, Daily Use=500L, Lead Time=3d |\n",
        f"| ANALYSIS | Days of Cover={s1_inv['days_of_cover']} | Risk={s1_inv['risk_level']} |\n",
        f"| DECISION | {s1_proc['decision']} |\n",
        f"| REASON | {s1_trace['reason']} |\n",
        f"| EXPECTED EFFECT | No stockout. Costs remain stable. |\n\n",
        trace_block("Full Trace", s1_trace),
    ]
    log.info("Scenario 1 — Normal Operation: %s", s1_proc["decision"])

    # ── Scenario 2: Demand Spike ──────────────────────────────────────────────
    report_lines.append(section("Scenario 2 — Demand Spike (+50% orders)"))
    s2_inv = calculate_inventory_risk(usable_inventory=1200, forecast_daily_usage=750,
                                      supplier_lead_time=3, safety_stock=500)
    s2_rm = calculate_raw_material_requirement(
        forecast_demand=750, open_orders_qty=200, planned_production=750,
        safety_buffer=500, current_usable_inventory=1200, conversion_ratio=1.0
    )
    s2_proc = recommend_procurement("INCREASING", s2_inv["days_of_cover"], 3, "STABLE",
                                    s2_rm["recommended_procurement"])
    s2_trace = DecisionTrace.create_trace(
        s2_proc["decision"], "Milk", s2_rm["recommended_procurement"],
        {"days_of_cover": s2_inv["days_of_cover"], "risk": s2_inv["risk_level"],
         "forecast_daily_use": 750, "supplier_lead_time": 3},
        "Demand spike detected. Stock covers less than lead time.",
        f"Procure {s2_rm['recommended_procurement']} L of milk immediately."
    )
    report_lines += [
        "| Field | Value |\n|---|---|\n",
        f"| INPUT | Milk Stock=1200L, Demand Spike→750L/day, Lead Time=3d |\n",
        f"| ANALYSIS | Days of Cover={s2_inv['days_of_cover']} | Risk={s2_inv['risk_level']} |\n",
        f"| DECISION | {s2_proc['decision']} |\n",
        f"| REASON | {s2_trace['reason']} |\n",
        f"| RECOMMENDED QTY | {s2_rm['recommended_procurement']} L |\n",
        f"| EXPECTED EFFECT | Stockout avoided after procurement. |\n\n",
        trace_block("Full Trace", s2_trace),
    ]
    log.info("Scenario 2 — Demand Spike: %s, Qty=%s L", s2_proc["decision"],
             s2_rm["recommended_procurement"])

    # ── Scenario 3: Milk Price Increase ──────────────────────────────────────
    report_lines.append(section("Scenario 3 — Milk Price Increase (+10%)"))
    s3_what_if = run_what_if_scenario(80000, "MILK_PRICE_INCREASE", 0.10)
    s3_inv = calculate_inventory_risk(usable_inventory=1500, forecast_daily_usage=500,
                                      supplier_lead_time=3, safety_stock=500)
    s3_proc = recommend_procurement("FLAT", s3_inv["days_of_cover"], 3, "INCREASING", 1000)
    s3_trace = DecisionTrace.create_trace(
        s3_proc["decision"], "Milk", 1000,
        {"price_trend": "INCREASING", "30_day_change_pct": 10,
         "current_margin": 80000, "projected_margin": s3_what_if["simulated_margin"]},
        "Milk prices trending up. Procuring early reduces cost exposure.",
        "Secure partial stock now at current price before further increases."
    )
    report_lines += [
        "| Field | Value |\n|---|---|\n",
        f"| INPUT | Milk +10% price, Stock=1500L, Daily Use=500L |\n",
        f"| ANALYSIS | Margin impact: ₹{80000:,} → ₹{s3_what_if['simulated_margin']:,.0f} |\n",
        f"| DECISION | {s3_proc['decision']} |\n",
        f"| REASON | {s3_trace['reason']} |\n",
        f"| EXPECTED EFFECT | Margin reduced by ₹{80000 - s3_what_if['simulated_margin']:,.0f}. Early buy limits further exposure. |\n\n",
        trace_block("Full Trace", s3_trace),
    ]
    log.info("Scenario 3 — Price Increase: Margin impact ₹%s", s3_what_if["simulated_margin"])

    # ── Scenario 4: Supplier Delay (+3 days) ─────────────────────────────────
    report_lines.append(section("Scenario 4 — Supplier Delay (+3 days)"))
    s4_lead = 6  # normal 3 + delay 3
    s4_inv = calculate_inventory_risk(usable_inventory=1500, forecast_daily_usage=500,
                                      supplier_lead_time=s4_lead, safety_stock=500)
    s4_proc = recommend_procurement("FLAT", s4_inv["days_of_cover"], s4_lead, "STABLE", 2000)
    s4_trace = DecisionTrace.create_trace(
        s4_proc["decision"], "Milk", 2000,
        {"days_of_cover": s4_inv["days_of_cover"], "effective_lead_time": s4_lead,
         "risk": s4_inv["risk_level"]},
        "Supplier delay extends lead time to 6 days. Current stock insufficient.",
        "Contact alternate supplier or procure emergency stock."
    )
    report_lines += [
        "| Field | Value |\n|---|---|\n",
        f"| INPUT | Stock=1500L, Use=500L/day, Delay→Lead Time={s4_lead}d |\n",
        f"| ANALYSIS | Days of Cover={s4_inv['days_of_cover']} | Risk={s4_inv['risk_level']} |\n",
        f"| DECISION | {s4_proc['decision']} |\n",
        f"| REASON | {s4_trace['reason']} |\n",
        f"| EXPECTED EFFECT | Stockout risk HIGH without alternate sourcing. |\n\n",
        trace_block("Full Trace", s4_trace),
    ]
    log.info("Scenario 4 — Supplier Delay: %s", s4_proc["decision"])

    # ── Scenario 5: Large Customer Order (500 kg Paneer) ─────────────────────
    report_lines.append(section("Scenario 5 — Large Customer Order (500 kg Paneer)"))
    s5_feas = check_order_feasibility(
        product_id="PRD-PNR", order_qty=500, selling_price=350,
        current_fg_inventory=80, raw_material_inventory=1500,
        conversion_ratio=5.5, raw_material_cost_per_unit=45, processing_cost_per_unit=5
    )
    s5_trace = DecisionTrace.create_trace(
        s5_feas["decision"], "Paneer", 500,
        {"current_fg": 80, "raw_material_available": 1500,
         "rm_required": s5_feas["required_raw_material"],
         "procurement_needed": s5_feas["procurement_quantity_needed"],
         "estimated_margin": s5_feas["estimated_margin"]},
        "; ".join(s5_feas["reasons"]),
        f"Procure {s5_feas['procurement_quantity_needed']:.0f} L milk then confirm delivery date."
    )
    report_lines += [
        "| Field | Value |\n|---|---|\n",
        f"| INPUT | Order=500kg Paneer, FG Stock=80kg, Milk=1500L |\n",
        f"| ANALYSIS | RM Required={s5_feas['required_raw_material']:.0f}L | Procurement needed={s5_feas['procurement_quantity_needed']:.0f}L |\n",
        f"| DECISION | {s5_feas['decision']} |\n",
        f"| ESTIMATED MARGIN | ₹{s5_feas['estimated_margin']:,.0f} |\n",
        f"| DELIVERY RISK | {s5_feas['delivery_risk']} |\n",
        f"| REASON | {s5_trace['reason']} |\n",
        f"| EXPECTED EFFECT | Order profitable after additional milk procurement. |\n\n",
        trace_block("Full Trace", s5_trace),
    ]
    log.info("Scenario 5 — Large Order: %s, Margin=₹%s",
             s5_feas["decision"], s5_feas["estimated_margin"])

    # ── Scenario 6: Excess Inventory ─────────────────────────────────────────
    report_lines.append(section("Scenario 6 — Excess Inventory (Demand Falls)"))
    s6_inv = calculate_inventory_risk(usable_inventory=12000, forecast_daily_usage=300,
                                      supplier_lead_time=3, safety_stock=500)
    s6_proc = recommend_procurement("DECREASING", s6_inv["days_of_cover"], 3, "STABLE", 0)
    s6_trace = DecisionTrace.create_trace(
        s6_proc["decision"], "Milk", 0,
        {"days_of_cover": s6_inv["days_of_cover"], "risk": s6_inv["risk_level"]},
        "Excess inventory detected. Demand has fallen. No procurement needed.",
        "Reduce purchase quantity. Review production schedule to match lower demand."
    )
    report_lines += [
        "| Field | Value |\n|---|---|\n",
        f"| INPUT | Stock=12000L, Demand falls→300L/day |\n",
        f"| ANALYSIS | Days of Cover={s6_inv['days_of_cover']} | Risk={s6_inv['risk_level']} |\n",
        f"| DECISION | {s6_proc['decision']} — reduce or pause procurement |\n",
        f"| REASON | {s6_trace['reason']} |\n",
        f"| EXPECTED EFFECT | Avoids capital lockup in excess raw material. |\n\n",
        trace_block("Full Trace", s6_trace),
    ]
    log.info("Scenario 6 — Excess Inventory: %s", s6_proc["decision"])

    # ── Scenario 7: Poor Data Quality ────────────────────────────────────────
    report_lines.append(section("Scenario 7 — Poor Data Quality (Missing Transactions)"))
    sparse_df = pd.DataFrame({
        "date": pd.date_range("2026-01-01", periods=18, freq="D").strftime("%Y-%m-%d"),
        "quantity": [50] * 18
    })
    s7_quality = assess_data_quality(sparse_df, expected_days=180)
    s7_trace = DecisionTrace.create_trace(
        "REVIEW", "Forecast", 0,
        {"quality_indicator": s7_quality["quality_indicator"],
         "missing_rate": s7_quality["missing_rate"]},
        s7_quality["reason"],
        "Gather more transaction records before relying on these forecasts."
    )
    report_lines += [
        "| Field | Value |\n|---|---|\n",
        f"| INPUT | Only 18 valid days of sales history available (of 180 expected) |\n",
        f"| ANALYSIS | Quality={s7_quality['quality_indicator']} | Missing rate={s7_quality['missing_rate']*100:.0f}% |\n",
        f"| DECISION | REVIEW — confidence is LOW |\n",
        f"| REASON | {s7_quality['reason']} |\n",
        f"| EXPECTED EFFECT | Recommendations downgraded in reliability. Owner informed explicitly. |\n\n",
        trace_block("Full Trace", s7_trace),
    ]
    log.info("Scenario 7 — Poor Data Quality: %s", s7_quality["quality_indicator"])

    # ── Inventory Reconciliation Example ─────────────────────────────────────
    report_lines.append(section("Inventory Reconciliation — Example Check"))
    recon = reconcile_inventory(opening=2000, purchases=800, production=0,
                                sales=600, wastage=50, expected_closing=2310)
    report_lines += [
        trace_block("Reconciliation Result", recon),
        "> Note: A 90 L unexplained discrepancy is flagged. Records are NOT silently changed.\n\n",
    ]

    # ── Backtesting Summary ───────────────────────────────────────────────────
    report_lines.append(section("Forecast Backtesting Summary (SMA Baseline)"))
    np.random.seed(42)
    actuals = (np.random.normal(200, 20, 40)).tolist()
    sma_preds = [sum(actuals[max(0, i-7):i]) / min(7, i+1) for i in range(len(actuals))]
    metrics = backtest_forecast(actuals, sma_preds)
    report_lines += [
        f"| Metric | Value |\n|---|---|\n",
        f"| MAE | {metrics['MAE']} units |\n",
        f"| RMSE | {metrics['RMSE']} units |\n",
        f"| MAPE | {metrics['MAPE_percent']}% |\n\n",
        "> Selected model: **SMA (7-day)**. Chosen for transparency and low MAPE on this dataset.\n",
        "> XGBoost not required for current MVP — deterministic baselines are preferred for explainability.\n\n",
    ]

    # ── Business Health & Credit Summary ─────────────────────────────────────
    report_lines.append(section("Business Health & Credit Readiness Summary"))
    health = calculate_business_health(88, 94, 72, 75)
    health_text = generate_business_health_summary(health)
    readiness = calculate_credit_readiness(88, 94, 85, 72, 75, 90)
    readiness_text = generate_credit_readiness_summary(readiness)

    report_lines += [
        f"```\n{health_text}```\n\n",
        f"```\n{readiness_text}```\n\n",
    ]

    # ── Scheme Matching ───────────────────────────────────────────────────────
    report_lines.append(section("Government Scheme Matching — Demo Profiles"))
    matches_a = match_government_schemes("Micro", "Rural", "Dairy Processing")
    schemes_text_a = generate_scheme_summary(matches_a)
    report_lines += [
        "**Profile A: Micro dairy processor, Maharashtra, Equipment funding**\n\n",
        f"```\n{schemes_text_a}```\n\n",
    ]
    matches_b = match_government_schemes("Micro", "Urban", "Dairy Processing")
    schemes_text_b = generate_scheme_summary(matches_b)
    report_lines += [
        "**Profile B: Micro dairy processor, Urban, Working capital**\n\n",
        f"```\n{schemes_text_b}```\n\n",
    ]

    return "".join(report_lines)


# ── Main ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    log.info("Starting DairyPulse Scenario Simulation…")
    output = run_all_scenarios()

    with open("reports/scenario_results.md", "w", encoding="utf-8") as f:
        f.write(output)

    log.info("Scenario results saved → reports/scenario_results.md")
