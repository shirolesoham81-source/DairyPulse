def calculate_inventory_risk(usable_inventory: float, forecast_daily_usage: float,
                             supplier_lead_time: int, safety_stock: float,
                             safety_stock_days: int = 2) -> dict:
    """
    Calculates inventory risk based on days of cover vs supplier lead time.

    Risk bands:
        CRITICAL : days_of_cover <= supplier_lead_time
        HIGH     : days_of_cover <= supplier_lead_time + safety_stock_days
        LOW      : days_of_cover > supplier_lead_time * 3  (excess inventory)
        MEDIUM   : everything else (healthy range)

    Args:
        usable_inventory       : Current usable stock (litres / kg).
        forecast_daily_usage   : Expected consumption per day.
        supplier_lead_time     : Days until next supplier delivery.
        safety_stock           : Safety-stock quantity (used for raw-material
                                 requirement calculations, NOT for risk banding).
        safety_stock_days      : Extra buffer days above lead time before
                                 the risk level drops to MEDIUM. Default = 2.
    """
    if forecast_daily_usage <= 0:
        return {
            "days_of_cover": 999,
            "risk_level": "LOW",
            "recommendation": "No forecast usage. Monitor for slow-moving stock.",
            "usable_inventory": usable_inventory,
            "forecast_daily_usage": forecast_daily_usage,
            "supplier_lead_time_days": supplier_lead_time,
        }

    days_of_cover = round(usable_inventory / forecast_daily_usage, 2)

    if days_of_cover <= supplier_lead_time:
        risk = "CRITICAL"
        rec = "Procure immediately to avoid stockout."
    elif days_of_cover <= supplier_lead_time + safety_stock_days:
        risk = "HIGH"
        rec = "Plan procurement soon. Approaching safety buffer."
    elif days_of_cover > supplier_lead_time * 3:
        risk = "LOW"
        rec = "Excess inventory. Consider reducing next purchase order."
    else:
        risk = "MEDIUM"
        rec = "Inventory level is healthy."

    return {
        "usable_inventory": usable_inventory,
        "forecast_daily_usage": forecast_daily_usage,
        "days_of_cover": days_of_cover,
        "supplier_lead_time_days": supplier_lead_time,
        "risk_level": risk,
        "recommendation": rec,
    }
