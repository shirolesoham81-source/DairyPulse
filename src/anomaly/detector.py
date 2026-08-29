import pandas as pd

def detect_anomalies(series: pd.Series, window: int = 7, threshold_sigma: float = 2.0) -> list:
    """
    Detects anomalies using a rolling mean and standard deviation.
    """
    anomalies = []
    if len(series) < window:
        return anomalies
        
    rolling_mean = series.rolling(window=window, min_periods=1).mean()
    rolling_std = series.rolling(window=window, min_periods=1).std().fillna(0)
    
    for idx in range(len(series)):
        val = series.iloc[idx]
        mean = rolling_mean.iloc[idx]
        std = rolling_std.iloc[idx]
        
        if std > 0 and abs(val - mean) > (threshold_sigma * std):
            anomalies.append({
                "index": series.index[idx],
                "current_value": val,
                "normal_range": f"{round(mean - std, 2)} - {round(mean + std, 2)}",
                "deviation": round(abs(val - mean) / std, 2),
                "possible_business_interpretation": "Unusual activity detected. Check for data entry errors, sudden demand spikes, or supply chain disruptions."
            })
            
    return anomalies
