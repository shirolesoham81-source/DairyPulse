# DairyPulse – Member 3 API Contract

## Overview
This document defines the **public HTTP contract** that the Intelligence Service (Member 3) exposes.  All endpoints return a **standard JSON envelope** (see `src/intelligence/response.py`).  The service is completely stateless – any required data is loaded from the CSV data‑warehouse in `data/processed/` or from the demo configuration.

| Endpoint | HTTP Method | Purpose |
|----------|-------------|---------|
| `/intelligence/summary` | **GET** | Aggregate dashboard payload for a specific business and date (see `get_business_summary`). |
| `/intelligence/demand` | **GET** | Forecast demand for a single product (see `get_demand_forecast`). |
| `/intelligence/price` | **GET** | Raw‑material price trend and risk (see `get_price_intelligence`). |
| `/intelligence/inventory` | **GET** | Inventory stock‑out risk calculation (see `get_inventory_risk`). |
| `/intelligence/procurement` | **GET** | Procurement recommendation based on inventory, price trend and demand (see `get_procurement_recommendation`). |
| `/intelligence/order-feasibility` | **POST** | Evaluate a new order – Accept / Accept‑with‑conditions / High‑risk (see `check_order_feasibility`). |
| `/intelligence/what-if` | **POST** | Run a what‑if simulation for price increase, demand spike, etc. (see `run_what_if`). |
| `/intelligence/anomalies` | **GET** | Detect statistical anomalies in a time‑series (see `get_anomalies`). |
| `/intelligence/business-health` | **GET** | Compute the Business Health score (0‑100) (see `get_business_health`). |
| `/intelligence/credit-readiness` | **GET** | Compute Credit Readiness indicator (see `get_credit_readiness`). |
| `/intelligence/scheme-match` | **POST** | Return potentially relevant government schemes (see `get_scheme_matches`). |
| `/intelligence/recommendations` | **GET** | Top‑3 prioritized actions derived from inventory, price and order signals (see `get_top_recommendations`). |

---
### Common Request Parameters
All **GET** endpoints accept the following query parameters:

* `business_id` **(required)** – unique identifier for the MSME.  The service filters all dataframes by this column if present; otherwise it works in *demo* mode.
* `date` *(optional)* – ISO‑8601 date string used as the reference point for the summary.  If omitted the current UTC date is used.

All **POST** endpoints accept a JSON body.  The body must include `business_id` and the fields required by the underlying function (see each endpoint section).

---
### Standard JSON Envelope
**Success**
```json
{
  "status": "success",
  "data": { … },
  "warnings": [],
  "data_quality": { … },
  "sources": [],
  "generated_at": "2026-08-29T12:34:56+00:00",
  "model_version": "service-v1.0",
  "versions": {
    "demand_model": "demand-v1.0",
    "price_model": "price-v1.0",
    "business_rules": "rules-v1.2",
    "readiness_scoring": "readiness-v1.0",
    "service": "service-v1.0"
  }
}
```

**Error**
```json
{
  "status": "error",
  "error_code": "SOME_CODE",
  "message": "Human readable description of the failure.",
  "warnings": [],
  "generated_at": "2026-08-29T12:34:56+00:00"
}
```
---
### Endpoint Specifications
#### 1. GET `/intelligence/summary`
**Purpose** – Return a full dashboard‑ready payload.

**Query parameters**
* `business_id` – required.
* `date` – optional ISO‑8601 date.

**Response – `data`** – See the example below under **Example JSON Responses** (section 9).

**Errors** – `SUMMARY_ERROR` if any internal step fails.
---
#### 2. GET `/intelligence/demand`
**Purpose** – Forecast demand for a product.

**Query parameters**
* `business_id` – required.
* `product_id` – e.g. `PRD-PNR` (required).
* `horizon` – integer days, default 7.

**Response – `data`** – `{ "product": "PRD-PNR", "forecast_quantity": 195, "trend": "INCREASING", "reliability": "HIGH", "data_period_days": 180, … }`

**Errors** – `FORECAST_ERROR`.
---
#### 3. GET `/intelligence/price`
**Purpose** – Provide raw‑material price trend and risk.

**Query parameters**
* `business_id` – required.
* `material_id` – default `MAT-RMLK`.

**Response – `data`** – `{ "material_id": "MAT-RMLK", "current_price": 48.0, "trend_direction": "INCREASING", "risk_level": "HIGH", … }`

**Errors** – `PRICE_ERROR`.
---
#### 4. GET `/intelligence/inventory`
**Purpose** – Compute days‑of‑cover and risk band.

**Query parameters**
* `business_id` – required.
* `usable_inventory` – numeric (litres or kg).
* `forecast_daily_usage` – numeric.
* `supplier_lead_time` – optional; defaults to config value.
* `safety_stock` – optional; defaults to config value.

**Response – `data`** – Same structure as `src/inventory/risk.py` plus an `explainability` block.

**Errors** – `INVALID_INPUT` or `INVENTORY_ERROR`.
---
#### 5. GET `/intelligence/procurement`
**Purpose** – Recommend a procurement action.

**Query parameters**
* `business_id` – required.
* `usable_inventory`, `forecast_daily_usage`, `planned_production`, `safety_buffer`, `conversion_ratio` – required numeric values.
* `price_trend` – optional (`STABLE`, `INCREASING`, `DECREASING`).

**Response – `data`** – Includes `decision`, `recommended_quantity`, `raw_material_detail`, and full `explainability`.
---
#### 6. POST `/intelligence/order-feasibility`
**Purpose** – Evaluate a new order.

**Body JSON**
```json
{
  "business_id": "demo-001",
  "product_id": "PRD-PNR",
  "order_qty": 500,
  "selling_price": 350,
  "current_fg_inventory": 80,
  "raw_material_inventory": 1500,
  "conversion_ratio": 5.5,
  "raw_material_cost_per_unit": 48,
  "processing_cost_per_unit": 5
}
```
**Response – `data`** – Decision object with `explainability` and `trace_id`.
---
#### 7. POST `/intelligence/what-if`
**Purpose** – Run a what‑if simulation.

**Body JSON**
```json
{ "business_id": "demo-001", "current_margin": 12.5, "scenario_type": "MILK_PRICE_INCREASE", "percentage_change": 5 }
```
**Response – `data`** – Scenario impact (e.g., new margin, procurement suggestion).
---
#### 8. GET `/intelligence/anomalies`
**Purpose** – Detect outliers in a metric series.

**Query parameters**
* `business_id` – required.
* `metric_name` – optional, defaults to `metric`.
* `window` – rolling window size, default 7.

**Response – `data`** – `{ "metric": "sales", "anomalies": [{"date":"2026‑07‑12","value":12345,"z_score":3.2}], "count": 2 }`
---
#### 9. GET `/intelligence/business-health`
**Purpose** – Return the Business Health score.

**Query parameters** – Four numeric inputs (0‑100): `sales_consistency`, `order_fulfillment`, `inventory_discipline`, `growth_trend`.

**Response – `data`** – Full health dict plus a human‑readable `summary_text`.
---
#### 10. GET `/intelligence/credit-readiness`
**Purpose** – Return Credit Readiness indicator.

**Query parameters** – Six numeric inputs (0‑100): `sales_consistency`, `order_fulfillment`, `business_activity`, `inventory_discipline`, `growth_trend`, `record_completeness`.

**Response – `data`** – Score, summary, and disclaimer.
---
#### 11. POST `/intelligence/scheme-match`
**Purpose** – Return potentially relevant government schemes.

**Body JSON**
```json
{ "business_id": "demo-001", "enterprise_type": "Micro", "location_type": "Rural", "business_activity": "Dairy Processing" }
```
**Response – `data`** – `matches` array, `count`, `summary_text`, and disclaimer.
---
#### 12. GET `/intelligence/recommendations`
**Purpose** – Return the top‑3 prioritized actions.

**Query parameters** – `business_id` (required) plus the three pre‑computed signal objects `inventory_risk`, `price_trend`, `order_feasibility` (JSON‑encoded).  In practice the `summary` endpoint calls this internally.

**Response – `data`** – Same payload as `generate_business_recommendations`.
---
#### 13. GET `/intelligence/owner-view`
**Purpose** – Return the full owner‑friendly business status panel.

**Query parameters**
* `business_id` – required.

**Response – `data`** – Nested object containing `today`, `demand`, `price`, `inventory`, `procurement`, `orders`, `business_health`, `credit_readiness`, `scheme_matches`. See the example below under **Example JSON Responses**.
---
#### 14. GET `/intelligence/lender-package`
**Purpose** – Return a structured lender‑ready evaluation package.

**Query parameters**
* `business_id` – required.

**Response – `data`** – Includes business profile, reporting period, sales history summary, procurement history, production summary, inventory summary, order fulfillment, cost trends, business health, credit readiness, risk indicators, supporting documents status, data‑quality notes, and versions.
---
#### 15. POST `/intelligence/outcomes`
**Purpose** – Record owner action feedback or actual operational outcome for recommendation evaluation.

**Body JSON (Feedback)**
```json
{
  "business_id": "demo-001",
  "recommendation_id": "REC-2026-INIT",
  "decision": "BUY_NOW",
  "owner_action": "ACCEPTED",
  "final_quantity": 1500,
  "reason_if_rejected": null
}
```

**Body JSON (Actual Outcome)**
```json
{
  "business_id": "demo-001",
  "recommendation_id": "REC-2026-INIT",
  "actual_purchase_quantity": 1500,
  "stockout_occurred": false
}
```

**Response – `data`** – The recorded entry.
---
### 9. Example JSON Responses
Below are concise real‑world‑ish examples produced by the **demo** configuration.

#### 9.1 `GET /intelligence/summary`
```json
{
  "status": "success",
  "data": {
    "business_id": "demo-001",
    "business_name": "Kopargaon Dairy Foods",
    "reference_date": "2026‑08‑28",
    "today": { "sales_inr": 84500, "orders_pending": 4 },
    "inventory": { "milk_litres": 1500, "milk_days_cover": 3, "risk": "HIGH", "recommendation": "Procure milk" },
    "demand": { "paneer_expected_kg_per_day": 195, "trend": "INCREASING" },
    "price": { "milk_current_per_litre": 48.0, "milk_trend": "INCREASING", "milk_30d_change_pct": 5.8 },
    "procurement": { "recommended_action": "BUY_NOW" },
    "order_feasibility": { "product": "Paneer", "qty_kg": 500, "decision": "ACCEPT_WITH_CONDITIONS", "estimated_margin_inr": 48750 },
    "top_actions": ["Procure milk", "Review large order", "Monitor milk price"],
    "business_health": 87,
    "credit_readiness": 82,
    "scheme_matches": 2,
    "disclaimer": "DEMO DATA — all figures are synthetic."
  },
  "warnings": [],
  "data_quality": {},
  "sources": ["sales_history","purchase_history","inventory_history","order_history","schemes_reference_data","demo_config"],
  "generated_at": "2026‑08‑29T12:34:56+00:00",
  "model_version": "service-v1.0",
  "versions": { "demand_model":"demand-v1.0", "price_model":"price-v1.0", "business_rules":"rules-v1.2", "readiness_scoring":"readiness-v1.0", "service":"service-v1.0" }
}
```
---
#### 9.2 `GET /intelligence/demand`
```json
{"status":"success","data":{"product":"PRD-PNR","forecast_quantity":195,"trend":"INCREASING","range":[185,205],"reliability":"HIGH","data_period_days":180,"valid_sales_records":176},"warnings":[],"data_quality":{…},"generated_at":"…","model_version":"demand-v1.0","versions":{…}}
```
---
#### 9.3 `POST /intelligence/order-feasibility`
```json
{"status":"success","data":{"decision":"ACCEPT_WITH_CONDITIONS","required_raw_material":2750,"procurement_quantity_needed":1250,"estimated_margin":48750,"reasons":["Insufficient raw‑material inventory for full order."],"explainability":{"WHAT":"ACCEPT_WITH_CONDITIONS","WHY":"Insufficient raw‑material inventory for full order.","EVIDENCE":{"current_fg_inventory":80,"raw_material_available":1500,"required_raw_material":2750,"procurement_quantity_needed":1250,"estimated_margin":48750},"ACTION":"Confirm order after securing raw material."},"trace_id":"REC-2026‑a1b2"},"warnings":[],"generated_at":"…","model_version":"rules-v1.2"}
```
---
### 10. Reproducibility & Environment
* **Python** – 3.14 (checked at runtime).
* **Requirements** – `requirements.txt` generated by the repository; exact package versions are frozen via *pip‑freeze* during deployment.
* **Random seeds** – All stochastic helpers (e.g., Monte‑Carlo simulations) set `random.seed(42)` and NumPy’s RNG where applicable, guaranteeing identical outputs for identical inputs.
* **Model parameters** – All algorithms are deterministic (SMA, EMA, rolling‑average, rule‑based decision tree).  No trained ML models are used in the MVP.

---
### 11. Configuration
All thresholds are stored in `config/business_rules.json`.  The service loads this file once on start‑up via `_cfg()`.  Changing a value (e.g., `inventory_thresholds.safety_stock_days`) requires a service restart.

---
### 12. Demo CLI
The command `python -m src.intelligence.demo` prints a nicely formatted snapshot of the demo business.  See `src/intelligence/demo.py`.

---
### 13. Integration Test
The test suite `tests/test_integration.py` exercises the full end‑to‑end flow:
1. Load demo data → demand forecast → raw‑material requirement → inventory risk → price intelligence → procurement recommendation → order feasibility → business health → credit readiness → scheme matches → top recommendations.
2. Assertions verify internal consistency (e.g., procurement quantity reduces inventory risk).
3. Edge‑case scenarios are covered (no historical data, zero inventory, missing lead time, extreme spikes).

---
### 14. Hand‑off
See `docs/member3_handoff.md` for a concise summary for other team members.
