# Member 3 — Frozen Scope Declaration

> **Status: FROZEN as of 2026-08-29**
> This document defines the exact scope of the DairyPulse Business Intelligence & Decision Engine (Member 3). Once declared frozen, no new algorithms, models, or business modules shall be added without explicit team approval and a scope-change document.

---

## 1. Demand Intelligence

### What is implemented
| Component | Description | Module |
|---|---|---|
| 7-day SMA demand forecast | Simple Moving Average on `clean_sales.csv` by `product_id` | `src/forecasting/demand.py` |
| Forecast horizon | 1–30 day configurable ahead-of-time demand estimate | `service.get_demand_forecast()` |
| Reliability flag | HIGH / MEDIUM / LOW based on valid sales record count | `src/intelligence/data_quality.py` |
| Cold-start fallback | If < 30 days of history, uses industry benchmark fallback | `src/intelligence/owner_outputs.get_cold_start_forecast()` |

### Frozen limitations (do NOT attempt to fix in this phase)
- SMA does not model weekly or seasonal patterns.
- Forecast is per-product, not cross-product or portfolio-level.
- Does not support demand-side price elasticity.
- Range (`[min, max]`) is symmetric ±10% of the point estimate — not a statistical confidence interval.

---

## 2. Price Intelligence

### What is implemented
| Component | Description | Module |
|---|---|---|
| 30-day rolling MA | Computes average procurement price from purchase history | `src/forecasting/pricing.py` |
| Trend classification | INCREASING / STABLE / DECREASING based on configurable threshold | `service.get_price_intelligence()` |
| Price risk level | HIGH / MEDIUM / LOW from trend direction and volatility | `src/forecasting/pricing.py` |
| Volatility (sigma) | Standard deviation of 30-day prices | `src/forecasting/pricing.py` |

### Frozen limitations
- Price intelligence covers only Raw Milk (`MAT-RMLK`).
- Does not integrate live market feeds — based solely on purchase history.
- Does not forecast future price direction — classification is retrospective.
- No commodity exchange or APMC market integration.

---

## 3. Inventory Intelligence

### What is implemented
| Component | Description | Module |
|---|---|---|
| Days of cover | `usable_inventory / forecast_daily_usage` | `src/inventory/risk.py` |
| Risk classification | CRITICAL / HIGH / MEDIUM / LOW / EXCESS | `src/inventory/risk.py` |
| Stockout risk signal | Fires when days_of_cover ≤ supplier_lead_time + safety_stock_days | `src/inventory/risk.py` |
| Safety stock threshold | Configured in `config/business_rules.json` | `_cfg()` |

### Frozen limitations
- Covers only raw milk inventory (single material).
- Does not account for spoilage/perishability rates.
- Assumes constant daily consumption (does not model day-of-week patterns).

---

## 4. Procurement Intelligence

### What is implemented
| Component | Description | Module |
|---|---|---|
| Raw material requirement | Computes net procurement quantity from demand, open orders, production plan, safety buffer | `src/procurement/decision.py` |
| Decision classification | BUY_NOW / BUY_PARTIAL / WAIT / REVIEW | `src/procurement/decision.py` |
| Procurement override | Suppresses BUY if inventory already covers lead time + safety | `src/procurement/decision.py` |
| Explainability trace | WHAT / WHY / EVIDENCE / ACTION fields | `src/intelligence/explainability.py` |

### Decision rules (frozen)
| Decision | Condition |
|---|---|
| `BUY_NOW` | Days of cover ≤ lead_time + safety_stock_days OR price trend INCREASING and inventory low |
| `BUY_PARTIAL` | Days of cover moderate but raw material requirement > 0 |
| `WAIT` | Days of cover > lead_time + safety_stock_days AND price STABLE or DECREASING |
| `REVIEW` | Ambiguous or conflicting signals |

### Frozen limitations
- Does not model supplier availability or negotiate quantity discounts.
- Safety buffer quantity is a fixed number; not dynamically computed.

---

## 5. Order Intelligence

### What is implemented
| Component | Description | Module |
|---|---|---|
| Order feasibility check | Evaluates raw material availability, finished goods stock, margin | `src/orders/feasibility.py` |
| Decision classification | ACCEPT / ACCEPT_WITH_CONDITIONS / HIGH_RISK / REVIEW_ORDER | `src/orders/feasibility.py` |
| Estimated margin | `(selling_price - raw_material_cost * conversion_ratio - processing_cost) * order_qty` | `src/orders/economics.py` |
| What-if simulation | Scenarios: MILK_PRICE_INCREASE / DEMAND_SPIKE / PRODUCTION_INCREASE | `src/orders/economics.py` |

### Frozen limitations
- One order evaluated at a time (no batch feasibility across multiple simultaneous orders).
- Does not check delivery logistics or customer credit history.
- Processing cost is a flat per-unit estimate from config — not activity-based costing.

---

## 6. Business Intelligence

### What is implemented
| Component | Description | Module |
|---|---|---|
| Anomaly detection | Rolling z-score detection, threshold from `anomaly_thresholds.sigma_threshold` | `src/anomaly/detector.py` |
| Business health score | Weighted scoring across 4 dimensions (0–100) | `src/business_health/health.py` |
| Priority recommendations | Top-3 CRITICAL/HIGH/MEDIUM/LOW ranked actions | `src/recommendations/decision_engine.py` |

### Health score dimensions (frozen weights)
| Dimension | Weight |
|---|---|
| Sales consistency | 35% |
| Order fulfillment | 30% |
| Inventory discipline | 20% |
| Growth trend | 15% |

### Frozen limitations
- Business health is a proxy composite score — not an audited financial assessment.
- Anomaly detection uses z-score only; no ML-based detection.

---

## 7. Finance Intelligence

### What is implemented
| Component | Description | Module |
|---|---|---|
| MSME Credit Readiness Indicator | Weighted 6-dimension score (0–100). NOT a loan approval | `src/credit/readiness.py` |
| Lender data package | 14-section structured report for owner review before sharing | `service.generate_lender_data_package()` |

### Credit readiness dimensions (frozen weights)
| Dimension | Weight |
|---|---|
| Sales consistency | 30% |
| Order fulfillment | 20% |
| Business activity | 15% |
| Inventory discipline | 15% |
| Growth trend | 10% |
| Record completeness | 10% |

### Frozen limitations
- The system NEVER approves or rejects a loan.
- The system NEVER transmits data to a bank automatically.
- Owner must review and explicitly consent before sharing the package.
- Score is informational only — lending institution makes final decision.

---

## 8. Scheme Intelligence

### What is implemented
| Component | Description | Module |
|---|---|---|
| Government scheme matching | Rule-based matching by enterprise_type, location_type, business_activity | `src/schemes/matcher.py` |
| Output format | Scheme name, official source URL, last verified date, missing docs | `src/schemes/matcher.py` |
| Scheme eligibility disclaimer | "Potentially relevant — verify current official eligibility" | Every scheme output |

### Frozen limitations
- Scheme database is stored in `data/reference/` as a static reference file.
- No live government API integration.
- Matching is keyword-based (enterprise type, activity, region).
- Claims are never made of guaranteed eligibility.

---

## Frozen Integration Boundary

| Layer | Owner |
|---|---|
| Business Intelligence Engine | **Member 3** (FROZEN) |
| REST API gateway / forwarding | Member 2 |
| Flutter UI display | Member 1 |
| Authentication & user management | Member 2 |
| Database CRUD / persistence | Member 2 |

**Member 3 provides**: Pure analytical functions + standard JSON responses.
**Member 3 does NOT own**: HTTP routing, authentication, persistence, or UI.

---

## Scope Change Policy

Any change to this frozen scope requires:
1. Written justification of why the change is needed.
2. Team sign-off from all three members.
3. Updated data contract and API contract documents.
4. All existing tests must continue to pass after the change.
