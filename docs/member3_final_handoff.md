# Member 3 — Final Handoff

> **FROZEN AND READY FOR SYSTEM INTEGRATION as of 2026-08-29**

---

## Member 3 Responsibility

**Business Intelligence & Decision Engine**

Converts raw MSME business records into explainable, actionable intelligence. Provides a single Python service layer and optional FastAPI HTTP interface that Members 1 and 2 can consume directly.

---

## Completed Modules

| Module | Status | Primary File |
|---|---|---|
| Historical data pipeline | ✅ Complete | `src/data_pipeline/` |
| Demand forecasting | ✅ Complete | `src/forecasting/demand.py` |
| Raw-material price intelligence | ✅ Complete | `src/forecasting/pricing.py` |
| Inventory / stockout risk | ✅ Complete | `src/inventory/risk.py` |
| Raw-material requirement | ✅ Complete | `src/procurement/decision.py` |
| Procurement recommendation | ✅ Complete | `src/procurement/decision.py` |
| Order feasibility | ✅ Complete | `src/orders/feasibility.py` |
| What-if simulation | ✅ Complete | `src/orders/economics.py` |
| Anomaly detection | ✅ Complete | `src/anomaly/detector.py` |
| Business health score | ✅ Complete | `src/business_health/health.py` |
| Credit readiness indicator | ✅ Complete | `src/credit/readiness.py` |
| Government scheme matching | ✅ Complete | `src/schemes/matcher.py` |
| Integrated recommendations | ✅ Complete | `src/recommendations/decision_engine.py` |
| Owner-friendly outputs | ✅ Complete | `src/intelligence/owner_outputs.py` |
| Lender data package | ✅ Complete | `src/intelligence/service.py` |
| Recommendation feedback | ✅ Complete | `src/intelligence/outcomes.py` |
| Outcome tracking | ✅ Complete | `src/intelligence/outcomes.py` |
| Explainability traces | ✅ Complete | `src/intelligence/explainability.py` |
| Data quality assessment | ✅ Complete | `src/intelligence/data_quality.py` |
| Version registry | ✅ Complete | `src/intelligence/version.py` |
| Standard response envelope | ✅ Complete | `src/intelligence/response.py` |
| Unified service façade | ✅ Complete | `src/intelligence/service.py` |

---

## Inputs Required from Member 2

Member 2 must provide the following datasets or call parameters:

| Input | Format | Notes |
|---|---|---|
| `sales` DataFrame | CSV or API-provided | See `docs/member3_data_contract.md` |
| `purchases` DataFrame | CSV or API-provided | See data contract |
| `inventory` snapshot | Numeric value (usable litres) | Passed directly to service functions |
| `orders` list | JSON array or API body | Current open orders for feasibility |
| Business profile | JSON object | `enterprise_type`, `location_type`, `business_activity` |
| `business_id` | String | Required on every API call for isolation |

---

## Outputs Provided to Members 1 & 2

All outputs are standard JSON envelopes (`status`, `data`, `warnings`, `data_quality`, `versions`).

| Output | Endpoint | For Member 1 Screen |
|---|---|---|
| Full dashboard | `GET /intelligence/summary` | Dashboard home |
| Owner-friendly view | `GET /intelligence/owner-view` | **Primary dashboard endpoint** |
| Demand forecast | `GET /intelligence/demand` | Demand planning screen |
| Price trend | `GET /intelligence/price` | Price monitoring screen |
| Inventory risk | `GET /intelligence/inventory` | Inventory screen |
| Procurement advice | `GET /intelligence/procurement` | Procurement screen |
| Order evaluation | `POST /intelligence/order-feasibility` | Order entry screen |
| What-if | `POST /intelligence/what-if` | Simulation screen |
| Anomalies | `GET /intelligence/anomalies` | Alerts screen |
| Business health | `GET /intelligence/business-health` | Health dashboard |
| Credit readiness | `GET /intelligence/credit-readiness` | Finance / Credit screen |
| Scheme matches | `POST /intelligence/scheme-match` | Schemes screen |
| Lender package | `GET /intelligence/lender-package` | Export / Share screen |

---

## Main Python Functions (Service Layer)

```python
from src.intelligence.service import (
    get_business_summary,           # Full dashboard payload
    get_demand_forecast,            # Demand for one product
    get_price_intelligence,         # Milk price trend
    get_inventory_risk,             # Days of cover & risk band
    get_procurement_recommendation, # BUY_NOW / WAIT / etc.
    check_order_feasibility,        # ACCEPT / ACCEPT_WITH_CONDITIONS / HIGH_RISK
    run_what_if,                    # Price / demand simulation
    get_anomalies,                  # Spike/dip detection
    get_business_health,            # 0–100 health score
    get_credit_readiness,           # 0–100 credit indicator
    get_scheme_matches,             # Government scheme list
    get_top_recommendations,        # Top-3 actions
    get_full_owner_view,            # Master owner dashboard
    generate_lender_data_package,   # 14-section bank report
    record_feedback,                # Save owner action
    track_outcome,                  # Save operational result
)
```

---

## How Member 2 Integrates

```
Flutter App (Member 1)
    ↓ HTTP request
Member 2 Backend (FastAPI / Node / etc.)
    ↓ calls Python function or proxies HTTP
Member 3 Intelligence Service (service.py)
    ↓ returns standard JSON envelope
Member 2 Backend
    ↓ forwards response as-is
Flutter App (Member 1)
    → displays data
```

**Rules for Member 2**:
1. **Do NOT reimplement any intelligence calculation.** All analytics live in Member 3.
2. Call `GET /intelligence/owner-view` for the primary dashboard.
3. Pass `business_id` on every request.
4. Forward the `data` field of the response to Member 1.
5. Forward the `warnings` field so Member 1 can display data quality notices.
6. Do NOT modify the `data` content before forwarding — Member 3 returns display-ready text.
7. For the lender package: show the owner a preview, require explicit "Share" action. Never auto-transmit.

**Example (Python direct call)**:
```python
from src.intelligence.service import get_full_owner_view

response = get_full_owner_view(business_id="biz-123")
# response["status"] == "success"
# response["data"] == { "today": {...}, "procurement": {...}, ... }
```

**Example (HTTP call)**:
```
GET /intelligence/owner-view?business_id=biz-123
→ returns the same JSON envelope
```

---

## How Member 1 Uses the Outputs

Member 1 (Flutter) reads from the `data` field of each response:

### Dashboard Screen
```
data.today.sales_inr          → "Today's Sales: ₹84,500"
data.top_actions[0]           → "Priority Action: Procure milk"
data.inventory.risk_level     → Red/Amber/Green indicator
data.business_health          → Progress bar 0–100
```

### Procurement Screen
```
data.procurement.recommended_action     → "BUY NOW" button
data.procurement.recommended_quantity   → "Recommended: 1,350 L"
data.procurement.reason                 → Explanation text
data.procurement.estimated_cost         → "Estimated cost: ₹64,800"
data.procurement.disclaimer             → Grey footnote text
```

### Order Screen
```
data.orders.order            → "500 kg Paneer @ ₹350/kg"
data.orders.decision         → Green / Orange / Red badge
data.orders.why              → Bullet-list explanation
data.orders.estimated_margin → "Estimated margin: ₹40,500"
data.orders.action           → CTA text
```

### Credit Screen
```
data.credit_readiness.overall_score      → "85/100"
data.credit_readiness.positive_evidence  → Green checkmarks
data.credit_readiness.improvement_areas  → Amber bullets
data.credit_readiness.documents_missing  → Red missing-doc list
data.credit_readiness.status             → Status badge
```

### Schemes Screen
```
data.scheme_matches[0].scheme_name       → Scheme title
data.scheme_matches[0].why_it_may_match  → Matching reason
data.scheme_matches[0].official_source   → "Verify at: NABARD"
data.scheme_matches[0].guarantee_note    → Grey disclaimer
```

**Member 1 must always display**:
- `warnings` array as yellow info banners (if non-empty)
- `data_quality.reliability` as a data confidence indicator
- The disclaimer from any lender/scheme output as grey text
- "DEMO DATA" label when `disclaimer` contains "DEMO" or "synthetic"

---

## Demo Command

```bash
python -m src.intelligence.demo
```

---

## Test Command

```bash
pytest -q
# Expected: 41 passed, 2 skipped
```

---

## Known Limitations

1. **Demo mode only**: The current deployment uses synthetic data from `config/demo_business.json`. Replace with real MSME data before production.
2. **Single material**: Price intelligence and inventory risk cover only Raw Milk (`MAT-RMLK`).
3. **Single business demo**: Business ID isolation is implemented but not stress-tested with concurrent requests across multiple tenants.
4. **No live price feeds**: Milk prices come from purchase history — no real-time market integration.
5. **Scheme data is static**: Government scheme database is a local reference file, not a live API.
6. **Seasonal forecasting not implemented**: SMA does not capture festive or monsoon demand patterns.
7. **scikit-learn dependency**: Listed in `requirements.txt` but not used by any current module.

---

## Frozen Scope

See [`docs/member3_frozen_scope.md`](file:///c:/Users/SOHAM/Desktop/dairypulse/docs/member3_frozen_scope.md) for the complete frozen boundary declaration.

**Once this handoff is accepted, do not modify any file in `src/` without explicit team approval.**
