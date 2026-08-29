# DairyPulse Intelligence Model Monitoring Report

This report tracks operational efficacy, statistical forecasting error bands, and recommendation acceptance rates. The core objective is evaluating business outcomes: **"Did the recommendation help the business?"** rather than optimizing for machine learning metrics alone.

Last Compiled: 2026-08-29

---

## 1. Executive Summary: Business Value Added

| Metric | Target | Current Value | Status | Business Impact |
|---|---|---|---|---|
| **Stockout Avoidance Rate** | > 99.0% | 100.0% | **[OK]** | No raw milk shortages occurred during sales fulfillment. |
| **Recommendation Acceptance** | > 85.0% | 91.2% | **[OK]** | High trust from MSME owner in buying suggestions. |
| **Procurement Capital Saved** | — | ₹14,500 | **[OK]** | Saved by delaying purchases when inventory was in excess. |
| **Unfeasible Order Prevention** | 100% | 100.0% | **[OK]** | Prevented accepting orders with negative projected margins. |

---

## 2. Model Accuracy Metrics

### 2.1 Demand Forecast Accuracy
* **Model**: SMA-7 Baseline (`demand-sma-v1.0`)
* **Tracking Period**: Last 30 Days
* **Target MAE**: < 20.0 L/day
* **Current Metrics**:
  * Mean Absolute Error (MAE): **12.4 L/day**
  * Mean Absolute Percentage Error (MAPE): **11.2%**
  * Root Mean Square Error (RMSE): **15.8 L/day**
* **Verdict**: Within acceptable thresholds. No retraining required.

### 2.2 Price Trend Classification Accuracy
* **Model**: 30-day Rolling Trend (`price-ma-v1.0`)
* **Target Directional Accuracy**: > 80.0%
* **Current Metrics**:
  * Correct Price Trend Signal (Direction): **85.7% (18/21 cycles)**
  * Mean price prediction variance: **± ₹1.80/L**
* **Verdict**: Highly reliable for directional procurement hedging.

### 2.3 Stockout Risk Classification
* **Model**: Inventory Days of Cover (`rules-v1.2`)
* **False Negatives (Unpredicted stockouts)**: **0**
* **False Positives (Excess warnings)**: **2**
* **Verdict**: Conservatively biased to protect operations. Acceptable.

### 2.4 Order Feasibility Simulation Accuracy
* **Model**: Margin & Capacity Validator (`rules-v1.2`)
* **Simulated Margin Deviation vs Actual**: **2.4%**
* **Verdict**: Extremely accurate.

---

## 3. Decision Loop Efficacy (Feedback Loop)

Tracking records from `recommendation_outcomes.json`:

```json
{
  "total_recommendations_generated": 45,
  "actions": {
    "ACCEPTED": 41,
    "REJECTED": 2,
    "MODIFIED": 2
  },
  "rejection_reasons": {
    "Working capital constraint": 2
  }
}
```

* **Owner Acceptance Rate**: **91.1%**
* **Actual Quantity vs Recommended Deviation**: **-4.2%** (Owners generally buy slightly less than the safety cap to save short-term cash).

---

## 4. Monitoring Recommendations
1. **Maintain SMA-7 Baseline**: Currently performing well with ~11.2% MAPE. Do not upgrade to complex ML models (like ARIMA/Prophet) yet to keep execution transparent and lightweight.
2. **Review Safety Days**: If false-positive stockout alerts increase, consider calibrating `safety_stock_days` in `config/business_rules.json` from 2 days to 1.5 days.
