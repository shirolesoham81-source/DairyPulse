import pandas as pd

def assess_data_quality(df: pd.DataFrame, expected_days: int) -> dict:
    if df.empty:
        return {"quality": "LOW", "reason": "No historical data available."}
        
    df['date'] = pd.to_datetime(df['date'])
    unique_days = df['date'].nunique()
    
    missing_rate = max(0, 1.0 - (unique_days / expected_days)) if expected_days > 0 else 0
    
    if missing_rate > 0.5:
        quality = "LOW"
        reason = f"Forecast quality is limited because only {unique_days} valid days of recent history are available."
    elif missing_rate > 0.2:
        quality = "MEDIUM"
        reason = "Some data is missing, reducing confidence."
    else:
        quality = "HIGH"
        reason = "Sufficient historical data."
        
    return {
        "quality_indicator": quality,
        "missing_rate": round(missing_rate, 2),
        "reason": reason
    }
