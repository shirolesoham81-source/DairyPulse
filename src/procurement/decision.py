def calculate_raw_material_requirement(forecast_demand: float, open_orders_qty: float, 
                                       planned_production: float, safety_buffer: float, 
                                       current_usable_inventory: float, conversion_ratio: float) -> dict:
    
    expected_production_req = planned_production * conversion_ratio
    
    total_requirement = expected_production_req + safety_buffer
    
    procurement_needed = max(0, total_requirement - current_usable_inventory)
    
    return {
        "expected_production": planned_production,
        "raw_material_requirement": expected_production_req,
        "current_usable_inventory": current_usable_inventory,
        "safety_buffer": safety_buffer,
        "recommended_procurement": procurement_needed,
        "reason": f"Need {expected_production_req} for production + {safety_buffer} buffer. Have {current_usable_inventory}."
    }

def recommend_procurement(demand_forecast_trend: str, days_of_cover: float,
                          supplier_lead_time: int, price_trend: str,
                          recommended_qty: float) -> dict:
    """
    Returns a procurement decision (BUY_NOW, BUY_PARTIAL, WAIT, REVIEW).

    Safety rule: if days_of_cover <= supplier_lead_time, the decision is ALWAYS
    BUY_NOW regardless of other flags — we never override a stockout-risk signal.
    """
    reasons: list[str] = []
    decision = "WAIT"

    # ── Primary stockout-risk rules ──────────────────────────────────────────
    if days_of_cover <= supplier_lead_time:
        decision = "BUY_NOW"
        reasons.append("Stock cover is at or below supplier lead time.")
    elif days_of_cover <= supplier_lead_time + 2:
        decision = "BUY_PARTIAL"
        reasons.append("Approaching safety threshold.")

    # ── Price-trend escalation (only when no critical risk already) ──────────
    if price_trend == "INCREASING" and decision not in ["BUY_NOW"]:
        if days_of_cover < supplier_lead_time * 3:
            decision = "BUY_PARTIAL"
            reasons.append("Input prices are trending upward — secure stock early.")

    # ── No-action path: safe inventory AND no quantity needed ────────────────
    if decision == "WAIT" and recommended_qty <= 0:
        reasons.append("No immediate procurement required based on forecast.")

    if not reasons:
        reasons.append("Inventory levels are healthy and prices are stable.")

    return {
        "decision": decision,
        "recommended_quantity": recommended_qty if decision in ["BUY_NOW", "BUY_PARTIAL"] else 0,
        "reason": reasons,
    }
