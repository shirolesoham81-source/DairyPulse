def calculate_unit_margin(rm_cost: float, processing_cost: float, packaging_cost: float, selling_price: float) -> dict:
    unit_cost = rm_cost + processing_cost + packaging_cost
    margin = selling_price - unit_cost
    
    return {
        "estimated_unit_cost": round(unit_cost, 2),
        "selling_price": selling_price,
        "estimated_unit_margin": round(margin, 2),
        "note": "Estimated operating economics."
    }

def run_what_if_scenario(current_margin: float, scenario_type: str, percentage_change: float) -> dict:
    new_margin = current_margin
    risk = "MEDIUM"
    rec = "Review operations."
    
    if scenario_type == "MILK_PRICE_INCREASE":
        new_margin = current_margin * (1 - percentage_change)
        risk = "HIGH"
        rec = "Review selling price or procurement timing."
    elif scenario_type == "DEMAND_SPIKE":
        new_margin = current_margin * (1 + percentage_change)
        risk = "MEDIUM"
        rec = "Ensure production capacity and raw materials can handle the spike."
        
    return {
        "scenario": scenario_type,
        "current_total_margin": current_margin,
        "simulated_margin": round(new_margin, 2),
        "risk": risk,
        "recommendation": rec
    }
