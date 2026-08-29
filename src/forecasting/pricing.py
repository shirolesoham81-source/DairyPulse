import pandas as pd

def analyze_raw_material_price(purchases_df: pd.DataFrame, material_id: str) -> dict:
    """
    Analyzes historical prices to determine trends and near-term expected ranges.
    """
    mat_purchases = purchases_df[purchases_df['material_id'] == material_id].copy()
    if mat_purchases.empty:
        return {"trend": "UNKNOWN", "risk": "UNKNOWN", "recommendation": "No historical price data."}
        
    mat_purchases['date'] = pd.to_datetime(mat_purchases['date'])
    daily_prices = mat_purchases.groupby('date')['unit_price'].mean().reset_index()
    daily_prices = daily_prices.sort_values('date')
    
    if len(daily_prices) < 2:
        return {"current_price": daily_prices['unit_price'].iloc[0], "trend": "FLAT"}

    current = daily_prices['unit_price'].iloc[-1]
    
    # Calculate MAs (approximate days by row count for simplicity if we don't resample, but we assume daily entries exist)
    ma_7 = daily_prices['unit_price'].tail(7).mean()
    ma_30 = daily_prices['unit_price'].tail(30).mean() if len(daily_prices) >= 30 else daily_prices['unit_price'].mean()
    
    change_abs = current - ma_30
    change_pct = (change_abs / ma_30) * 100 if ma_30 > 0 else 0
    
    if change_pct > 3:
        trend = "INCREASING"
        risk = "HIGH"
    elif change_pct < -3:
        trend = "DECREASING"
        risk = "LOW"
    else:
        trend = "STABLE"
        risk = "MEDIUM"
        
    volatility = daily_prices['unit_price'].tail(30).std() if len(daily_prices) > 1 else 0
    
    return {
        "material_id": material_id,
        "current_price": round(current, 2),
        "7_day_average": round(ma_7, 2),
        "30_day_average": round(ma_30, 2),
        "30_day_change_pct": round(change_pct, 2),
        "volatility": round(volatility, 2),
        "trend_direction": trend,
        "risk_level": risk,
        "expected_range": [round(current - volatility, 2), round(current + volatility, 2)]
    }
