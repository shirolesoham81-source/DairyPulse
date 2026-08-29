def generate_advisor_text(demand: dict, inventory_risk: dict, procurement: dict, price: dict) -> str:
    """
    Creates a clear text recommendation from the JSON contracts.
    """
    text = f"Demand for {demand['product']} is expected to be {demand['expected_daily_demand']} units/day. "
    text += f"Current stock covers approximately {inventory_risk['days_of_cover']} days, while supplier lead time is {inventory_risk['supplier_lead_time_days']} days. "
    
    if price['trend_direction'] == "INCREASING":
        text += "Input procurement cost is trending upward. "
        
    if procurement['decision'] in ["BUY_NOW", "BUY_PARTIAL"]:
        text += f"Recommended action: procure approximately {procurement['recommended_quantity']} units now."
    else:
        text += "Recommended action: Hold. No immediate procurement required."
        
    return text
