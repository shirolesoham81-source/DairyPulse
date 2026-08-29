# Member 3 — Error Contract

> All error responses from the DairyPulse Intelligence Service follow a standard envelope. This document defines every error code, its meaning, the response shape, and what the frontend (Member 1) should display.

---

## Standard Error Envelope

```json
{
  "status": "error",
  "error_code": "ERROR_CODE_HERE",
  "message": "Human-readable explanation of what went wrong.",
  "warnings": [],
  "generated_at": "2026-08-29T12:34:56+00:00"
}
```

The service **never** throws raw Python exceptions to the caller. All exceptions are caught and wrapped in this envelope.

---

## Error Code Reference

### `INVALID_INPUT`

**Meaning**: A caller-supplied parameter has a value that makes computation impossible.

**Common causes**:
- `usable_inventory < 0`
- `selling_price <= 0`
- `order_qty <= 0`
- A score parameter outside the 0–100 range
- `percentage_change < 0` in what-if simulation

**HTTP status**: 400 Bad Request (when exposed via HTTP)

**Example response**:
```json
{
  "status": "error",
  "error_code": "INVALID_INPUT",
  "message": "selling_price must be greater than zero.",
  "warnings": ["Negative or zero selling price makes feasibility analysis impossible."],
  "generated_at": "2026-08-29T12:34:56+00:00"
}
```

**Frontend action**: Display a field validation message near the offending input. Do not retry automatically.

---

### `MISSING_DATA`

**Meaning**: A required dataset or column was not found.

**Common causes**:
- CSV file not generated yet (data pipeline has not run)
- Required column absent from the DataFrame
- Empty DataFrame passed where data is required

**HTTP status**: 422 Unprocessable Entity

**Example response**:
```json
{
  "status": "error",
  "error_code": "MISSING_DATA",
  "message": "No valid sales history found. Required columns: date, product_id, quantity.",
  "warnings": ["Run the data pipeline to generate clean_sales.csv before calling this endpoint."],
  "generated_at": "2026-08-29T12:34:56+00:00"
}
```

**Frontend action**: Show a "Data not available" banner. Prompt the user to upload or sync their records.

---

### `INSUFFICIENT_HISTORY`

**Meaning**: The available data is technically present but too sparse for a reliable output.

**Common causes**:
- Fewer than 14 days of purchase records (price trend)
- Fewer than 30 days of sales records (demand forecast)

**HTTP status**: 200 OK with `reliability: LOW` in `data_quality` block (partial success — not a hard error)

> [!NOTE]
> In the current implementation, `INSUFFICIENT_HISTORY` causes a **degraded success** response (not an error envelope). The `data_quality.reliability` field is set to `"LOW"` and a warning is added. A full error envelope with this code is reserved for cases where zero useful output can be produced.

**Example response** (degraded success):
```json
{
  "status": "success",
  "data": {
    "forecast_quantity": 150,
    "trend": "UNKNOWN",
    "reliability": "LOW"
  },
  "warnings": ["Only 12 valid sales days found. Reliability is LOW. Minimum 30 days required for HIGH reliability."],
  "data_quality": {
    "reliability": "LOW",
    "valid_records": 12,
    "data_period_days": 12
  }
}
```

**Frontend action**: Show a yellow warning banner: "Limited data — results are estimates. Add more records for better accuracy."

---

### `BUSINESS_NOT_FOUND`

**Meaning**: The `business_id` provided does not match any rows in the filtered dataset.

**HTTP status**: 404 Not Found

**Example response**:
```json
{
  "status": "error",
  "error_code": "BUSINESS_NOT_FOUND",
  "message": "No data found for business_id='BIZ-9999'. Verify the ID is correct.",
  "warnings": [],
  "generated_at": "2026-08-29T12:34:56+00:00"
}
```

**Frontend action**: Show "Business not found" and direct user to verify their account or re-login.

---

### `PRODUCT_NOT_FOUND`

**Meaning**: The `product_id` supplied does not exist in sales history or configuration.

**HTTP status**: 404 Not Found

**Example response**:
```json
{
  "status": "error",
  "error_code": "PRODUCT_NOT_FOUND",
  "message": "Product 'PRD-XYZ' not found in sales history or product configuration.",
  "warnings": [],
  "generated_at": "2026-08-29T12:34:56+00:00"
}
```

**Frontend action**: Show a "Product not recognized" message. List available products from the config.

---

### `MATERIAL_NOT_FOUND`

**Meaning**: The `material_id` does not exist in purchase history or `raw_materials` config.

**HTTP status**: 404 Not Found

**Example response**:
```json
{
  "status": "error",
  "error_code": "MATERIAL_NOT_FOUND",
  "message": "Material 'MAT-XYZ' not found. Known materials: MAT-RMLK.",
  "warnings": [],
  "generated_at": "2026-08-29T12:34:56+00:00"
}
```

**Frontend action**: Show "Material not configured" and guide user to the materials settings.

---

### `INVALID_DATE_RANGE`

**Meaning**: The `date` parameter is in an invalid format, is in the future, or the range is illogical (start > end).

**HTTP status**: 400 Bad Request

**Example response**:
```json
{
  "status": "error",
  "error_code": "INVALID_DATE_RANGE",
  "message": "Reference date '2030-01-01' is in the future. Use a date on or before today.",
  "warnings": [],
  "generated_at": "2026-08-29T12:34:56+00:00"
}
```

**Frontend action**: Show date picker validation error.

---

### `INVALID_QUANTITY`

**Meaning**: A quantity field (order_qty, usable_inventory, etc.) is zero, negative, or unrealistically large.

**HTTP status**: 400 Bad Request

**Example response**:
```json
{
  "status": "error",
  "error_code": "INVALID_QUANTITY",
  "message": "order_qty must be greater than zero.",
  "warnings": [],
  "generated_at": "2026-08-29T12:34:56+00:00"
}
```

**Frontend action**: Highlight the quantity field with a validation error.

---

### `MISSING_PROFILE`

**Meaning**: Required business profile fields (enterprise_type, location_type, business_activity) are missing for scheme matching or credit readiness.

**HTTP status**: 422 Unprocessable Entity

**Example response**:
```json
{
  "status": "error",
  "error_code": "MISSING_PROFILE",
  "message": "enterprise_type, location_type, and business_activity are all required for scheme matching.",
  "warnings": [],
  "generated_at": "2026-08-29T12:34:56+00:00"
}
```

**Frontend action**: Show "Please complete your business profile before using this feature."

---

### `INVALID_SCENARIO`

**Meaning**: The `scenario_type` parameter in a what-if request is not one of the supported scenarios.

**HTTP status**: 400 Bad Request

**Supported values**: `MILK_PRICE_INCREASE`, `DEMAND_SPIKE`, `PRODUCTION_INCREASE`

**Example response**:
```json
{
  "status": "error",
  "error_code": "INVALID_SCENARIO",
  "message": "scenario_type must be one of {'MILK_PRICE_INCREASE', 'DEMAND_SPIKE', 'PRODUCTION_INCREASE'}.",
  "warnings": [],
  "generated_at": "2026-08-29T12:34:56+00:00"
}
```

**Frontend action**: Show a dropdown validation error. Only present supported scenario types to the user.

---

### `CONFIGURATION_ERROR`

**Meaning**: The service failed to load `config/business_rules.json` or `config/demo_business.json`. This is an infrastructure issue, not a user error.

**HTTP status**: 500 Internal Server Error

**Example response**:
```json
{
  "status": "error",
  "error_code": "CONFIGURATION_ERROR",
  "message": "business_rules.json not found. Check that config/ directory is present.",
  "warnings": [],
  "generated_at": "2026-08-29T12:34:56+00:00"
}
```

**Frontend action**: Show a generic "Service unavailable" message. Do not expose internal paths to the user. Alert the developer team.

---

### Module-specific Internal Errors

These codes indicate a bug or unexpected state inside a specific module. They should never occur in a correctly deployed system.

| Error Code | Module | Meaning |
|---|---|---|
| `FORECAST_ERROR` | `get_demand_forecast` | Unexpected error in demand computation |
| `PRICE_ERROR` | `get_price_intelligence` | Unexpected error in price analysis |
| `INVENTORY_ERROR` | `get_inventory_risk` | Unexpected error in inventory risk |
| `PROCUREMENT_ERROR` | `get_procurement_recommendation` | Unexpected error in procurement logic |
| `ORDER_ERROR` | `check_order_feasibility` | Unexpected error in order evaluation |
| `WHATIF_ERROR` | `run_what_if` | Unexpected error in simulation |
| `ANOMALY_ERROR` | `get_anomalies` | Unexpected error in anomaly detection |
| `HEALTH_ERROR` | `get_business_health` | Unexpected error in health scoring |
| `READINESS_ERROR` | `get_credit_readiness` | Unexpected error in credit scoring |
| `SCHEME_ERROR` | `get_scheme_matches` | Unexpected error in scheme matching |
| `RECOMMENDATIONS_ERROR` | `get_top_recommendations` | Unexpected error in recommendation engine |
| `SUMMARY_ERROR` | `get_business_summary` | Unexpected error in dashboard compilation |
| `OWNER_VIEW_ERROR` | `get_full_owner_view` | Unexpected error in owner view compilation |
| `LENDER_PACKAGE_ERROR` | `generate_lender_data_package` | Unexpected error in lender package |
| `FEEDBACK_ERROR` | `record_feedback` | Unexpected error saving feedback |
| `OUTCOME_ERROR` | `track_outcome` | Unexpected error saving outcome |

**Frontend action for all `*_ERROR` codes**: Show "Something went wrong. Please try again or contact support." Log the full response for developer review.

---

## Safe Failure Guarantee

> [!IMPORTANT]
> The intelligence service is designed to **fail safely**. It will never:
> - Crash with an unhandled exception visible to the caller
> - Return partial data mixed with error states
> - Silently return wrong data without a warning
> - Modify any stored records when an error occurs

Every function in `service.py` wraps its entire body in `try/except` and returns a standard error envelope on failure.
