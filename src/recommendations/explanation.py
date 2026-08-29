def explain_inventory_risk(days_of_cover: float, lead_time: int, risk: str) -> str:
    if risk == "CRITICAL":
        return "Milk stock may run out before the next supplier delivery. Procurement should be planned now."
    elif risk == "HIGH":
        return f"Milk stock will soon reach the supplier lead time of {lead_time} days. Review procurement."
    elif risk == "LOW":
        return f"Current stock covers {days_of_cover} days — well above the {lead_time}-day lead time. Consider reducing the next purchase order to free working capital."
    else:  # MEDIUM
        return f"Inventory levels are healthy (covers {days_of_cover} days). No action needed right now."


def explain_price_trend(trend: str, pct_change: float) -> str:
    if trend == "INCREASING":
        return f"Milk procurement cost is trending upward (changed by {pct_change}% recently)."
    elif trend == "DECREASING":
        return f"Milk procurement cost is trending downward."
    else:
        return f"Procurement prices are currently stable."
