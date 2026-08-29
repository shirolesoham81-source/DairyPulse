# Member 3 — Data Contract

> This document defines the **exact input data schema** that the DairyPulse Business Intelligence Engine (Member 3) expects.
> Member 2 is responsible for providing these datasets from the application database. Member 3 reads them as Pandas DataFrames or structured JSON.

---

## General Rules

1. All date fields must be parseable as ISO 8601 (`YYYY-MM-DD` or `YYYY-MM-DDTHH:MM:SS`).
2. All numeric fields must be non-negative unless explicitly stated.
3. A `business_id` column **must** be present in every dataset if the system is serving multiple businesses from the same store. In single-business (demo) mode it is optional.
4. Missing optional columns are tolerated — the service returns reduced-accuracy outputs with warnings.
5. Missing required columns cause the service to return a `MISSING_DATA` error and skip that module.

---

## Dataset 1 — Sales (`clean_sales.csv`)

Used by: Demand forecasting, Business health, Data quality assessment.

| Column | Type | Unit | Required | Validation | Meaning |
|---|---|---|---|---|---|
| `date` | `date` | YYYY-MM-DD | ✅ | Must be a valid date, not future | Date of sale |
| `business_id` | `string` | — | ⚪ Multi-tenant | Non-empty | Business owner identifier |
| `product_id` | `string` | — | ✅ | e.g. `PRD-PNR`, `PRD-MLK` | Product sold |
| `quantity` | `numeric` | kg or L | ✅ | > 0 | Quantity sold |
| `unit_price` | `numeric` | INR | ✅ | > 0 | Price per unit sold |
| `customer_id` | `string` | — | ⚪ Optional | Non-empty if present | Customer reference |
| `order_id` | `string` | — | ⚪ Optional | Non-empty if present | Linked order reference |
| `revenue_inr` | `numeric` | INR | ⚪ Optional | > 0 if present | Derived from quantity × unit_price if missing |

**Minimum records for reliable output**: 30 valid sale days. Below 30 days, reliability drops to LOW.

---

## Dataset 2 — Purchases (`clean_purchases.csv`)

Used by: Raw material price intelligence, Procurement recommendation.

| Column | Type | Unit | Required | Validation | Meaning |
|---|---|---|---|---|---|
| `date` | `date` | YYYY-MM-DD | ✅ | Valid date | Date of purchase |
| `business_id` | `string` | — | ⚪ Multi-tenant | — | Business identifier |
| `material_id` | `string` | — | ✅ | e.g. `MAT-RMLK` | Raw material purchased |
| `quantity` | `numeric` | Litres | ✅ | > 0 | Volume purchased |
| `unit_price` | `numeric` | INR/L | ✅ | > 0 | Procurement price per litre |
| `supplier_id` | `string` | — | ⚪ Optional | Non-empty if present | Supplier identifier |
| `total_cost_inr` | `numeric` | INR | ⚪ Optional | > 0 if present | Derived from quantity × unit_price if missing |

**Minimum records**: 14 days for price trend. Below 14 days, trend is STABLE by default.

---

## Dataset 3 — Production (`clean_production.csv`)

Used by: Raw material requirement calculation, Capacity planning.

| Column | Type | Unit | Required | Validation | Meaning |
|---|---|---|---|---|---|
| `date` | `date` | YYYY-MM-DD | ✅ | Valid date | Date of production run |
| `business_id` | `string` | — | ⚪ Multi-tenant | — | Business identifier |
| `product_id` | `string` | — | ✅ | e.g. `PRD-PNR` | Finished good produced |
| `quantity_produced` | `numeric` | kg | ✅ | > 0 | Quantity manufactured |
| `raw_material_used` | `numeric` | Litres | ⚪ Optional | > 0 if present | Actual raw milk consumed |
| `batch_id` | `string` | — | ⚪ Optional | — | Production batch reference |

---

## Dataset 4 — Inventory (`clean_inventory.csv`)

Used by: Inventory risk calculation, Days-of-cover, Stockout detection.

| Column | Type | Unit | Required | Validation | Meaning |
|---|---|---|---|---|---|
| `date` | `date` | YYYY-MM-DD | ✅ | Valid date | Snapshot date |
| `business_id` | `string` | — | ⚪ Multi-tenant | — | Business identifier |
| `material_id` | `string` | — | ✅ | e.g. `MAT-RMLK` | Material or product tracked |
| `closing_balance` | `numeric` | Litres or kg | ✅ | ≥ 0 | Stock level at end of day |
| `usable_quantity` | `numeric` | Litres or kg | ⚪ Optional | ≥ 0 | Subset of closing balance that is fit for use |

---

## Dataset 5 — Orders (`order_history.csv` / inline from API)

Used by: Order feasibility, Margin calculation, Business health.

| Column | Type | Unit | Required | Validation | Meaning |
|---|---|---|---|---|---|
| `order_id` | `string` | — | ✅ | Unique | Order identifier |
| `date` | `date` | YYYY-MM-DD | ✅ | Valid date | Order received date |
| `business_id` | `string` | — | ⚪ Multi-tenant | — | Business identifier |
| `customer_id` | `string` | — | ⚪ Optional | — | Customer reference |
| `product_id` | `string` | — | ✅ | e.g. `PRD-PNR` | Product ordered |
| `qty` | `numeric` | kg | ✅ | > 0 | Quantity requested |
| `selling_price` | `numeric` | INR/kg | ✅ | > 0 | Price agreed with buyer |
| `status` | `string` | — | ⚪ Optional | OPEN/FULFILLED/CANCELLED | Order status |
| `delivery_date` | `date` | YYYY-MM-DD | ⚪ Optional | ≥ order date | Requested delivery |

---

## Dataset 6 — Expenses (`clean_expenses.csv`)

Used by: Business health (cost discipline dimension), Credit readiness.

| Column | Type | Unit | Required | Validation | Meaning |
|---|---|---|---|---|---|
| `date` | `date` | YYYY-MM-DD | ✅ | Valid date | Expense incurred |
| `business_id` | `string` | — | ⚪ Multi-tenant | — | Business identifier |
| `category` | `string` | — | ✅ | e.g. LABOUR, PACKAGING, ELECTRICITY | Expense category |
| `amount_inr` | `numeric` | INR | ✅ | > 0 | Amount spent |

---

## Dataset 7 — Products (`config/business_rules.json → products`)

Used by: Margin calculation, Order feasibility, Demand forecasting.

| Field | Type | Required | Meaning |
|---|---|---|---|
| `product_id` | string | ✅ | e.g. `PRD-PNR` |
| `name` | string | ✅ | Human-readable product name |
| `unit` | string | ✅ | kg / L |
| `conversion_ratio` | numeric | ✅ | Litres of raw milk per kg of finished product |
| `min_margin_inr` | numeric | ✅ | Minimum acceptable margin (INR per unit) |

---

## Dataset 8 — Materials (`config/business_rules.json → raw_materials`)

Used by: Price intelligence, Procurement recommendation.

| Field | Type | Required | Meaning |
|---|---|---|---|
| `material_id` | string | ✅ | e.g. `MAT-RMLK` |
| `name` | string | ✅ | Human-readable name |
| `unit` | string | ✅ | L / kg |
| `baseline_procurement_price` | numeric | ✅ | INR per unit, fallback if no history |

---

## Dataset 9 — Customers (inline / from API)

Used by: Order feasibility, Scheme matching (enterprise size).

| Field | Type | Required | Meaning |
|---|---|---|---|
| `customer_id` | string | ✅ | Unique identifier |
| `name` | string | ⚪ Optional | Customer name (not exposed in analytics) |
| `type` | string | ⚪ Optional | RETAIL / WHOLESALE / INSTITUTIONAL |
| `city` | string | ⚪ Optional | Customer city (for regional analytics) |

---

## Dataset 10 — Suppliers (inline / from API)

Used by: Lead-time configuration, Procurement recommendation.

| Field | Type | Required | Meaning |
|---|---|---|---|
| `supplier_id` | string | ✅ | Unique identifier |
| `name` | string | ⚪ Optional | Supplier name |
| `lead_time_days` | integer | ✅ | Days from order to delivery |
| `payment_terms` | string | ⚪ Optional | e.g. "Cash on delivery" |

---

## Dataset 11 — Business Profile (`config/demo_business.json` / API payload)

Used by: Business summary, Credit readiness, Scheme matching.

| Field | Type | Required | Meaning |
|---|---|---|---|
| `business_id` | string | ✅ | Unique identifier |
| `business_name` | string | ✅ | Trading name |
| `location` | string | ✅ | City, State, Country |
| `location_type` | string | ✅ | Rural / Urban / Semi-Urban |
| `enterprise_type` | string | ✅ | Micro / Small / Medium |
| `business_activity` | string | ✅ | e.g. "Dairy Processing" |
| `udyam_registration` | string | ⚪ Optional | Available / Missing |
| `gstin_record` | string | ⚪ Optional | Available / Missing |

---

## Business ID Isolation Rule

> **Critical security requirement**: When the `business_id` column is present in a DataFrame, Member 3 **always** filters rows to the exact matching `business_id` before any computation. Cross-business data leakage is explicitly blocked by `service._filter_by_business()`.

---

## Schema Version

| Version | Date | Change |
|---|---|---|
| `data-contract-v1.0` | 2026-08-29 | Initial frozen schema |
