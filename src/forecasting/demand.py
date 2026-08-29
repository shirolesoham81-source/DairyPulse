import pandas as pd
import numpy as np

def forecast_demand(sales_df: pd.DataFrame, product_id: str, horizon: int = 7) -> dict:
    """
    Simple Moving Average baseline for demand forecasting.
    """
    prod_sales = sales_df[sales_df['product_id'] == product_id].copy()
    if prod_sales.empty:
        return {
            "product": product_id,
            "forecast_quantity": 0,
            "lower_bound": 0,
            "upper_bound": 0,
            "trend": "FLAT",
            "recommendation": "No historical data."
        }
    
    prod_sales['date'] = pd.to_datetime(prod_sales['date'])
    daily_sales = prod_sales.groupby('date')['quantity'].sum().reset_index()
    daily_sales = daily_sales.sort_values('date')
    
    # Calculate 7-day moving average
    daily_sales['sma_7'] = daily_sales['quantity'].rolling(window=7, min_periods=1).mean()
    
    if len(daily_sales) >= 14:
        recent_avg = daily_sales['sma_7'].iloc[-1]
        past_avg = daily_sales['sma_7'].iloc[-8]
        if recent_avg > past_avg * 1.05:
            trend = "INCREASING"
        elif recent_avg < past_avg * 0.95:
            trend = "DECREASING"
        else:
            trend = "FLAT"
    else:
        trend = "FLAT"

    # Forecast
    latest_sma = daily_sales['sma_7'].iloc[-1]
    std_dev = daily_sales['quantity'].std() if len(daily_sales) > 1 else 0
    
    forecast_total = int(latest_sma * horizon)
    lower = int(max(0, (latest_sma - std_dev) * horizon))
    upper = int((latest_sma + std_dev) * horizon)
    
    return {
        "product": product_id,
        "forecast_horizon_days": horizon,
        "forecast_quantity": forecast_total,
        "expected_daily_demand": int(latest_sma),
        "lower_bound": lower,
        "upper_bound": upper,
        "trend": trend,
        "recommendation": f"Plan approximately {int(latest_sma)} units/day subject to current orders and capacity."
    }
