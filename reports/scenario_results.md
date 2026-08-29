# DairyPulse — Business Scenario Simulation Results
> Generated: 2026-08-29 17:06
> All scenarios use deterministic, rule-based logic. Results are DEMO / SIMULATED.

────────────────────────────────────────────────────────────
## Scenario 1 — Normal Operation
────────────────────────────────────────────────────────────

| Field | Value |
|---|---|
| INPUT | Milk Stock=6000L, Daily Use=500L, Lead Time=3d |
| ANALYSIS | Days of Cover=12.0 | Risk=LOW |
| DECISION | WAIT |
| REASON | Inventory is sufficient. No action needed. |
| EXPECTED EFFECT | No stockout. Costs remain stable. |

**Full Trace**
```json
{
  "recommendation_id": "REC-2026-068689",
  "decision": "WAIT",
  "item": "Milk",
  "quantity": 0,
  "evidence": {
    "days_of_cover": 12.0,
    "risk": "LOW"
  },
  "reason": "Inventory is sufficient. No action needed.",
  "explainability": {
    "WHAT": "WAIT",
    "WHY": "Inventory is sufficient. No action needed.",
    "EVIDENCE": {
      "days_of_cover": 12.0,
      "risk": "LOW"
    },
    "ACTION": "Monitor daily consumption. Re-evaluate in 48 hours."
  }
}
```

────────────────────────────────────────────────────────────
## Scenario 2 — Demand Spike (+50% orders)
────────────────────────────────────────────────────────────

| Field | Value |
|---|---|
| INPUT | Milk Stock=1200L, Demand Spike→750L/day, Lead Time=3d |
| ANALYSIS | Days of Cover=1.6 | Risk=CRITICAL |
| DECISION | BUY_NOW |
| REASON | Demand spike detected. Stock covers less than lead time. |
| RECOMMENDED QTY | 50.0 L |
| EXPECTED EFFECT | Stockout avoided after procurement. |

**Full Trace**
```json
{
  "recommendation_id": "REC-2026-64508f",
  "decision": "BUY_NOW",
  "item": "Milk",
  "quantity": 50.0,
  "evidence": {
    "days_of_cover": 1.6,
    "risk": "CRITICAL",
    "forecast_daily_use": 750,
    "supplier_lead_time": 3
  },
  "reason": "Demand spike detected. Stock covers less than lead time.",
  "explainability": {
    "WHAT": "BUY_NOW",
    "WHY": "Demand spike detected. Stock covers less than lead time.",
    "EVIDENCE": {
      "days_of_cover": 1.6,
      "risk": "CRITICAL",
      "forecast_daily_use": 750,
      "supplier_lead_time": 3
    },
    "ACTION": "Procure 50.0 L of milk immediately."
  }
}
```

────────────────────────────────────────────────────────────
## Scenario 3 — Milk Price Increase (+10%)
────────────────────────────────────────────────────────────

| Field | Value |
|---|---|
| INPUT | Milk +10% price, Stock=1500L, Daily Use=500L |
| ANALYSIS | Margin impact: ₹80,000 → ₹72,000 |
| DECISION | BUY_NOW |
| REASON | Milk prices trending up. Procuring early reduces cost exposure. |
| EXPECTED EFFECT | Margin reduced by ₹8,000. Early buy limits further exposure. |

**Full Trace**
```json
{
  "recommendation_id": "REC-2026-7a44c5",
  "decision": "BUY_NOW",
  "item": "Milk",
  "quantity": 1000,
  "evidence": {
    "price_trend": "INCREASING",
    "30_day_change_pct": 10,
    "current_margin": 80000,
    "projected_margin": 72000.0
  },
  "reason": "Milk prices trending up. Procuring early reduces cost exposure.",
  "explainability": {
    "WHAT": "BUY_NOW",
    "WHY": "Milk prices trending up. Procuring early reduces cost exposure.",
    "EVIDENCE": {
      "price_trend": "INCREASING",
      "30_day_change_pct": 10,
      "current_margin": 80000,
      "projected_margin": 72000.0
    },
    "ACTION": "Secure partial stock now at current price before further increases."
  }
}
```

────────────────────────────────────────────────────────────
## Scenario 4 — Supplier Delay (+3 days)
────────────────────────────────────────────────────────────

| Field | Value |
|---|---|
| INPUT | Stock=1500L, Use=500L/day, Delay→Lead Time=6d |
| ANALYSIS | Days of Cover=3.0 | Risk=CRITICAL |
| DECISION | BUY_NOW |
| REASON | Supplier delay extends lead time to 6 days. Current stock insufficient. |
| EXPECTED EFFECT | Stockout risk HIGH without alternate sourcing. |

**Full Trace**
```json
{
  "recommendation_id": "REC-2026-71a5d9",
  "decision": "BUY_NOW",
  "item": "Milk",
  "quantity": 2000,
  "evidence": {
    "days_of_cover": 3.0,
    "effective_lead_time": 6,
    "risk": "CRITICAL"
  },
  "reason": "Supplier delay extends lead time to 6 days. Current stock insufficient.",
  "explainability": {
    "WHAT": "BUY_NOW",
    "WHY": "Supplier delay extends lead time to 6 days. Current stock insufficient.",
    "EVIDENCE": {
      "days_of_cover": 3.0,
      "effective_lead_time": 6,
      "risk": "CRITICAL"
    },
    "ACTION": "Contact alternate supplier or procure emergency stock."
  }
}
```

────────────────────────────────────────────────────────────
## Scenario 5 — Large Customer Order (500 kg Paneer)
────────────────────────────────────────────────────────────

| Field | Value |
|---|---|
| INPUT | Order=500kg Paneer, FG Stock=80kg, Milk=1500L |
| ANALYSIS | RM Required=2310L | Procurement needed=810L |
| DECISION | ACCEPT_WITH_CONDITIONS |
| ESTIMATED MARGIN | ₹48,750 |
| DELIVERY RISK | HIGH |
| REASON | Insufficient finished goods. Production required: 420 units.; Insufficient raw material. Procurement required: 810.0 units.; Expected margin is positive. |
| EXPECTED EFFECT | Order profitable after additional milk procurement. |

**Full Trace**
```json
{
  "recommendation_id": "REC-2026-9868d9",
  "decision": "ACCEPT_WITH_CONDITIONS",
  "item": "Paneer",
  "quantity": 500,
  "evidence": {
    "current_fg": 80,
    "raw_material_available": 1500,
    "rm_required": 2310.0,
    "procurement_needed": 810.0,
    "estimated_margin": 48750.0
  },
  "reason": "Insufficient finished goods. Production required: 420 units.; Insufficient raw material. Procurement required: 810.0 units.; Expected margin is positive.",
  "explainability": {
    "WHAT": "ACCEPT_WITH_CONDITIONS",
    "WHY": "Insufficient finished goods. Production required: 420 units.; Insufficient raw material. Procurement required: 810.0 units.; Expected margin is positive.",
    "EVIDENCE": {
      "current_fg": 80,
      "raw_material_available": 1500,
      "rm_required": 2310.0,
      "procurement_needed": 810.0,
      "estimated_margin": 48750.0
    },
    "ACTION": "Procure 810 L milk then confirm delivery date."
  }
}
```

────────────────────────────────────────────────────────────
## Scenario 6 — Excess Inventory (Demand Falls)
────────────────────────────────────────────────────────────

| Field | Value |
|---|---|
| INPUT | Stock=12000L, Demand falls→300L/day |
| ANALYSIS | Days of Cover=40.0 | Risk=LOW |
| DECISION | WAIT — reduce or pause procurement |
| REASON | Excess inventory detected. Demand has fallen. No procurement needed. |
| EXPECTED EFFECT | Avoids capital lockup in excess raw material. |

**Full Trace**
```json
{
  "recommendation_id": "REC-2026-abf880",
  "decision": "WAIT",
  "item": "Milk",
  "quantity": 0,
  "evidence": {
    "days_of_cover": 40.0,
    "risk": "LOW"
  },
  "reason": "Excess inventory detected. Demand has fallen. No procurement needed.",
  "explainability": {
    "WHAT": "WAIT",
    "WHY": "Excess inventory detected. Demand has fallen. No procurement needed.",
    "EVIDENCE": {
      "days_of_cover": 40.0,
      "risk": "LOW"
    },
    "ACTION": "Reduce purchase quantity. Review production schedule to match lower demand."
  }
}
```

────────────────────────────────────────────────────────────
## Scenario 7 — Poor Data Quality (Missing Transactions)
────────────────────────────────────────────────────────────

| Field | Value |
|---|---|
| INPUT | Only 18 valid days of sales history available (of 180 expected) |
| ANALYSIS | Quality=LOW | Missing rate=90% |
| DECISION | REVIEW — confidence is LOW |
| REASON | Forecast quality is limited because only 18 valid days of recent history are available. |
| EXPECTED EFFECT | Recommendations downgraded in reliability. Owner informed explicitly. |

**Full Trace**
```json
{
  "recommendation_id": "REC-2026-1418dd",
  "decision": "REVIEW",
  "item": "Forecast",
  "quantity": 0,
  "evidence": {
    "quality_indicator": "LOW",
    "missing_rate": 0.9
  },
  "reason": "Forecast quality is limited because only 18 valid days of recent history are available.",
  "explainability": {
    "WHAT": "REVIEW",
    "WHY": "Forecast quality is limited because only 18 valid days of recent history are available.",
    "EVIDENCE": {
      "quality_indicator": "LOW",
      "missing_rate": 0.9
    },
    "ACTION": "Gather more transaction records before relying on these forecasts."
  }
}
```

────────────────────────────────────────────────────────────
## Inventory Reconciliation — Example Check
────────────────────────────────────────────────────────────

**Reconciliation Result**
```json
{
  "status": "WARNING",
  "message": "INVENTORY RECONCILIATION WARNING",
  "expected_closing": 2150,
  "recorded_closing": 2310,
  "difference": 160,
  "recommendation": "Do not silently change historical records. Flag discrepancy."
}
```
> Note: A 90 L unexplained discrepancy is flagged. Records are NOT silently changed.


────────────────────────────────────────────────────────────
## Forecast Backtesting Summary (SMA Baseline)
────────────────────────────────────────────────────────────

| Metric | Value |
|---|---|
| MAE | 26.76 units |
| RMSE | 45.34 units |
| MAPE | 13.4% |

> Selected model: **SMA (7-day)**. Chosen for transparency and low MAPE on this dataset.
> XGBoost not required for current MVP — deterministic baselines are preferred for explainability.


────────────────────────────────────────────────────────────
## Business Health & Credit Readiness Summary
────────────────────────────────────────────────────────────

```
Business Health: 84.0/100

Strong:
- sales consistency
- order fulfillment

```

```
Overall readiness: 84.6/100

Positive evidence:
- stable sales
- good order fulfillment

Weakness:
- incomplete recent financial records

Missing evidence:
- latest financial statement

Potential next action: Complete missing records before sharing the lender report.

*Note: This is NOT a bank approval decision, only structured evidence.*```


────────────────────────────────────────────────────────────
## Government Scheme Matching — Demo Profiles
────────────────────────────────────────────────────────────

**Profile A: Micro dairy processor, Maharashtra, Equipment funding**

```
Scheme name: Dairy Entrepreneurship Development Scheme (DEDS)
Why potentially relevant: Matches Micro enterprise in Rural for Dairy Processing.
Missing information: Current official eligibility rules.
Documents needed: Land Record, Bank Detail, Quotation
Official source: NABARD
Last verified date: 2023-08-15

*Disclaimer: Potentially relevant - verify current official eligibility. We do not guarantee eligibility.*```

**Profile B: Micro dairy processor, Urban, Working capital**

```
No schemes matched current profile.```

