# DairyPulse Member 3 Hand-off Documentation

## Member 3 Deliverables
All completed intelligence modules, services, tests, configurations, and API documentation are listed below:

- **Unified Service Layer** – [`service.py`](file:///c:/Users/SOHAM/Desktop/dairypulse/src/intelligence/service.py): Reusable facade providing clean public signatures, data quality scoring, explainability traces, model version tagging, business isolation, and error handling.
- **Envelope Standardizer** – [`response.py`](file:///c:/Users/SOHAM/Desktop/dairypulse/src/intelligence/response.py): Consistent success and error JSON shapes.
- **Quality Assessor** – [`data_quality.py`](file:///c:/Users/SOHAM/Desktop/dairypulse/src/intelligence/data_quality.py): Data completeness assessor.
- **Trace Recorder** – [`explainability.py`](file:///c:/Users/SOHAM/Desktop/dairypulse/src/intelligence/explainability.py): Trace object with WHAT/WHY/EVIDENCE/ACTION fields.
- **Reconciliation Engine** – [`reconciliation.py`](file:///c:/Users/SOHAM/Desktop/dairypulse/src/intelligence/reconciliation.py): Flow balancer checking inventory ledger consistency.
- **Model Version Registry** – [`version.py`](file:///c:/Users/SOHAM/Desktop/dairypulse/src/intelligence/version.py): Stamping analytics outputs with specific version descriptors.
- **Centralized Rules** – [`business_rules.json`](file:///c:/Users/SOHAM/Desktop/dairypulse/config/business_rules.json): Config mapping all safety stocks, reorder thresholds, credit readiness weights, and anomaly criteria.
- **Testing Suites** – `tests/test_integration.py` (E2E flow verification) and `tests/test_edge_cases.py` (defensive resilience validations).

---

## Exported Functions
The service layer exposes the following public functions:

### 1. `get_business_summary(business_id: str, reference_date: str | None = None) -> dict`
* **Purpose**: Single aggregate call returning today's sales, pending orders count, current inventory cover & risk level, price trends, top 3 recommended actions, health rating, and credit readiness. Used to populate the main dashboard API in one round-trip.

### 2. `get_demand_forecast(business_id: str, product_id: str, horizon: int = 7, sales_df: pd.DataFrame | None = None) -> dict`
* **Purpose**: Simple Moving Average demand forecast for a single product over the specified horizon.

### 3. `get_price_intelligence(business_id: str, material_id: str = "MAT-RMLK", purchases_df: pd.DataFrame | None = None) -> dict`
* **Purpose**: Analyzes purchase logs to output current prices, 7-day and 30-day averages, direction, and volatility.

### 4. `get_inventory_risk(business_id: str, usable_inventory: float, forecast_daily_usage: float, supplier_lead_time: int | None = None, safety_stock: float = 200.0) -> dict`
* **Purpose**: Evaluates days of cover against supplier lead times and safety stocks, outputting CRITICAL, HIGH, MEDIUM, or LOW risk levels.

### 5. `get_procurement_recommendation(...) -> dict`
* **Purpose**: Computes actual quantity of raw materials needed and yields prioritized actions (BUY_NOW, BUY_PARTIAL, WAIT, etc.).

### 6. `check_order_feasibility(...) -> dict`
* **Purpose**: Determines order viability (ACCEPT, ACCEPT_WITH_CONDITIONS, HIGH_RISK) based on raw material availability, price margin, and production capacity.

### 7. `run_what_if(business_id: str, current_margin: float, scenario_type: str, percentage_change: float) -> dict`
* **Purpose**: Simulates demand spikes or raw milk price escalations and estimates simulated margin.

### 8. `get_anomalies(business_id: str, metric_series: pd.Series, metric_name: str = "metric", window: int = 7) -> dict`
* **Purpose**: Highlights statistical anomalies in a metric time series using config-controlled standard deviation bounds.

### 9. `get_business_health(business_id: str, sales_consistency: float, order_fulfillment: float, inventory_discipline: float, growth_trend: float) -> dict`
* **Purpose**: Combines 4 core performance domains into a single health score (0-100).

### 10. `get_credit_readiness(...) -> dict`
* **Purpose**: Evaluates weighted indicator metrics to assess MSME credit readiness (0-100).

### 11. `get_scheme_matches(business_id: str, enterprise_type: str, location_type: str, business_activity: str) -> dict`
* **Purpose**: Rule-based matching against central government scheme criteria.

### 12. `get_top_recommendations(business_id: str, inventory_risk: dict, price_trend: dict, order_feasibility: dict | None = None) -> dict`
* **Purpose**: Ranks priority actions based on critical/high stockouts, rising inputs, or unfeasible orders.

---

## API Contract Reference
All endpoint specifications, parameters, required structures, and response shapes are defined in:
* [`docs/member3_api_contract.md`](file:///c:/Users/SOHAM/Desktop/dairypulse/docs/member3_api_contract.md)

---

## Run Instructions

### Start Demo CLI
Verify dashboard calculation with the mock profile:
```bash
python -m src.intelligence.demo
```

### Run Test Suite
Confirm all integration and edge cases are 100% correct:
```bash
pytest -q
```

---

## Data Dependencies
The intelligence service assumes Phase 1 has generated cleaned CSV files under `data/processed/`:
* `clean_sales.csv` (requires columns: `business_id`, `product_id`, `date`, `quantity`)
* `clean_purchases.csv` (requires columns: `business_id`, `material_id`, `date`, `unit_price`, `quantity`)

---

## Example JSON Responses

### 1. Demand Forecast Response
```json
{
  "status": "success",
  "data": {
    "product": "PRD-PNR",
    "forecast_horizon_days": 7,
    "forecast_quantity": 1365,
    "expected_daily_demand": 195,
    "lower_bound": 1295,
    "upper_bound": 1435,
    "trend": "INCREASING"
  },
  "warnings": [],
  "data_quality": {
    "data_period_days": 180,
    "valid_records": 176,
    "missing_rate": 0.0,
    "reliability": "HIGH",
    "assumptions": ["DEMO synthetic data. Calibrate with real MSME records."],
    "warnings": []
  },
  "sources": ["sales_history"],
  "generated_at": "2026-08-29T12:00:00.000000Z",
  "model_version": "demand-v1.0"
}
```

---

## Limitations and Disclaimers
1. **Forecast Horizon Bounds**: Simple Moving Average is accurate only for short horizons (e.g. 7 days) and assumes no long-term seasonality changes.
2. **Price Trend Direction**: Directional classification is based on recent averages and is not a financial market predictor.
3. **Credit Readiness Disclaimer**: Scoring indicates readiness to apply for financing. It is not an underwriting approval decision.
4. **Scheme Eligibility**: Government scheme lists are indicators. The MSME owner must verify eligibility directly against official ministry announcements.
5. **No Automatic Action**: Recommendations suggest actions; no automated loans, purchases, or order approvals are triggered without explicit confirmation.

---

## Integration Guidelines

### For Member 1 (Backend Integration)
Consume `get_business_summary()` inside your FastAPI handler (as in `src/api/main.py`):
```python
from src.intelligence.service import get_business_summary

@app.get("/api/dashboard/summary")
def dashboard_endpoint(business_id: str):
    result = get_business_summary(business_id)
    return result
```

### For Member 2 (Frontend/Flutter Integration)
The Flutter dashboard should display the standard envelope fields:
- `business_health` (render as circular progress indicator).
- `today.sales_inr` and `today.orders_pending` (dashboard counters).
- `top_actions` (as cards in a prioritized warning list).
- Visual warning badges if `inventory.risk` is `CRITICAL` or `HIGH`.
