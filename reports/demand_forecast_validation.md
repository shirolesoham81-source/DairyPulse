# Demand Forecast Validation Report

> Generated: 2026-08-29 17:07
> Data: Synthetic 180-day dairy MSME sales (DEMO)

## Dataset Split
| Period     | Days      | Notes                        |
|------------|-----------|------------------------------|
| Training   | 1 – 144   | 80 % of history              |
| Test       | 145 – 180 | 20 % held-out for validation |

## Model Comparison

| Model       | MAE   | RMSE  | MAPE % |
|-------------|-------|-------|--------|
| SMA-7       | 15.81 | 18.2 | 7.17 |
| SMA-14      | 14.82 | 17.53 | 6.67 |
| EMA α=0.3   | 16.26 | 18.67 | 7.35 |

## Selected Model: **SMA-14**

> Rationale: Lowest MAPE on test period. Chosen over XGBoost because deterministic,
> transparent rules are preferred for an MSME owner who needs explainable outputs.

## Notes & Limitations
- All figures are computed on **SYNTHETIC / DEMO** data.
- Calibrate against real MSME billing data before production use.
- MAPE is undefined where actuals = 0; excluded from calculation.
- XGBoost may outperform if richer feature engineering (festivals, weather) is added.
- Paneer and Buttermilk show higher error (wider seasonal variation) — their forecasts
  carry **MEDIUM** confidence until at least 6 months of real data is available.

## Product-Level Summary (Approximate)
| Product    | Method | Estimated MAPE | Confidence |
|------------|--------|----------------|------------|
| Milk       | SMA-7  | ~8–10 %        | MEDIUM     |
| Curd       | SMA-7  | ~10–13 %       | MEDIUM     |
| Paneer     | EMA    | ~12–16 %       | MEDIUM     |
| Buttermilk | SMA-7  | ~14–18 %       | LOW-MEDIUM |
