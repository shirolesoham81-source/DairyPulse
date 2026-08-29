# Member 3 — Response Examples

> Realistic JSON examples for every endpoint in the DairyPulse Intelligence API.
> All values below are produced by running the demo scenario (`config/demo_business.json`).
> These are **SIMULATED DEMO DATA** — all figures are synthetic.

---

## 1. Dashboard Summary — `GET /intelligence/summary`

```json
{
  "status": "success",
  "data": {
    "business_id": "demo-001",
    "business_name": "Kopargaon Dairy Foods",
    "reference_date": "2026-08-29",
    "today": {
      "sales_inr": 84500,
      "orders_pending": 4
    },
    "inventory": {
      "milk_litres": 1500,
      "milk_days_cover": 3.0,
      "risk": "CRITICAL",
      "recommendation": "Procure immediately to avoid stockout."
    },
    "demand": {
      "paneer_expected_kg_per_day": 195,
      "trend": "INCREASING"
    },
    "price": {
      "milk_current_per_litre": 48.0,
      "milk_trend": "INCREASING",
      "milk_30d_change_pct": 5.49
    },
    "procurement": {
      "recommended_action": "BUY_NOW"
    },
    "order_feasibility": {
      "product": "Paneer",
      "qty_kg": 500,
      "decision": "ACCEPT_WITH_CONDITIONS",
      "estimated_margin_inr": 40500
    },
    "top_actions": [
      "Procure milk",
      "Review New Order Feasibility",
      "Review procurement timing"
    ],
    "business_health": 84.6,
    "credit_readiness": 85.05,
    "scheme_matches": 1,
    "disclaimer": "DEMO DATA — all figures are synthetic. Calibrate with real MSME records."
  },
  "warnings": [],
  "data_quality": {},
  "sources": ["sales_history", "purchase_history", "inventory_history", "order_history", "schemes_reference_data", "demo_config"],
  "generated_at": "2026-08-29T12:34:56+00:00",
  "model_version": "service-v1.0",
  "versions": {
    "demand_model": "demand-sma-v1.0",
    "price_model": "price-ma-v1.0",
    "business_rules": "rules-v1.2",
    "readiness_scoring": "readiness-v1.1",
    "service": "service-v1.0"
  }
}
```

---

## 2. Demand Forecast — `GET /intelligence/demand`

**Request**: `GET /intelligence/demand?business_id=demo-001&product_id=PRD-PNR&horizon=7`

```json
{
  "status": "success",
  "data": {
    "product": "PRD-PNR",
    "forecast_quantity": 195,
    "trend": "INCREASING",
    "range": [175, 215],
    "reliability": "HIGH",
    "data_period_days": 180,
    "valid_sales_records": 176
  },
  "warnings": [],
  "data_quality": {
    "data_period_days": 180,
    "valid_records": 176,
    "missing_rate": 0.022,
    "reliability": "HIGH",
    "assumptions": ["DEMO synthetic data. Calibrate with real MSME records."],
    "warnings": []
  },
  "sources": ["sales_history"],
  "generated_at": "2026-08-29T12:34:56+00:00",
  "model_version": "demand-sma-v1.0"
}
```

---

## 3. Price Intelligence — `GET /intelligence/price`

**Request**: `GET /intelligence/price?business_id=demo-001&material_id=MAT-RMLK`

```json
{
  "status": "success",
  "data": {
    "material_id": "MAT-RMLK",
    "current_price": 48.0,
    "7_day_average": 47.2,
    "30_day_average": 45.5,
    "30_day_change_pct": 5.49,
    "trend_direction": "INCREASING",
    "risk_level": "HIGH",
    "volatility_sigma": 1.8,
    "reliability": "HIGH"
  },
  "warnings": [],
  "data_quality": {
    "data_period_days": 180,
    "valid_records": 174,
    "missing_rate": 0.033,
    "reliability": "HIGH",
    "assumptions": ["DEMO synthetic data."],
    "warnings": []
  },
  "sources": ["purchase_history"],
  "generated_at": "2026-08-29T12:34:56+00:00",
  "model_version": "price-ma-v1.0"
}
```

---

## 4. Inventory Risk — `GET /intelligence/inventory`

**Request**: `GET /intelligence/inventory?business_id=demo-001&usable_inventory=1500&forecast_daily_usage=500`

```json
{
  "status": "success",
  "data": {
    "days_of_cover": 3.0,
    "risk_level": "CRITICAL",
    "recommendation": "Procure immediately to avoid stockout.",
    "supplier_lead_time": 3,
    "safety_stock_days": 2,
    "explainability": {
      "WHAT": "CRITICAL",
      "WHY": "Procure immediately to avoid stockout.",
      "EVIDENCE": {
        "current_stock": 1500,
        "forecast_daily_usage": 500,
        "days_of_cover": 3.0,
        "supplier_lead_time": 3
      },
      "ACTION": "Review procurement based on risk level."
    }
  },
  "warnings": [],
  "data_quality": {
    "reliability": "HIGH",
    "assumptions": ["Real-time inventory figure provided by caller."]
  },
  "sources": ["inventory_history", "business_rules_config"],
  "generated_at": "2026-08-29T12:34:56+00:00",
  "model_version": "rules-v1.2"
}
```

---

## 5. Procurement Recommendation — `GET /intelligence/procurement`

**Request**: `GET /intelligence/procurement?business_id=demo-001&usable_inventory=1500&forecast_daily_usage=500&planned_production=0&safety_buffer=200&conversion_ratio=5.5&price_trend=INCREASING`

```json
{
  "status": "success",
  "data": {
    "decision": "BUY_NOW",
    "recommended_quantity": 1350,
    "reason": ["Days of cover is 3.0, which is at or below the lead time + safety threshold.", "Milk prices are trending increasing — buy before further price rise."],
    "raw_material_detail": {
      "recommended_procurement": 1350,
      "safety_buffer_applied": 200
    },
    "explainability": {
      "WHAT": "BUY_NOW",
      "WHY": "Days of cover is 3.0, which is at or below the lead time + safety threshold.",
      "EVIDENCE": {
        "days_of_cover": 3.0,
        "supplier_lead_time": 3,
        "forecast_daily_use": 500,
        "recommended_procurement_litres": 1350,
        "price_trend": "INCREASING"
      },
      "ACTION": "Procure approximately 1350 L."
    }
  },
  "sources": ["inventory_history", "demand_forecast", "purchase_history"],
  "generated_at": "2026-08-29T12:34:56+00:00",
  "model_version": "rules-v1.2"
}
```

---

## 6. Order Feasibility — `POST /intelligence/order-feasibility`

**Request body**:
```json
{
  "business_id": "demo-001",
  "product_id": "PRD-PNR",
  "order_qty": 500,
  "selling_price": 350,
  "current_fg_inventory": 80,
  "raw_material_inventory": 1500,
  "conversion_ratio": 5.5,
  "raw_material_cost_per_unit": 48.0,
  "processing_cost_per_unit": 5.0
}
```

```json
{
  "status": "success",
  "data": {
    "decision": "ACCEPT_WITH_CONDITIONS",
    "required_raw_material": 2750,
    "procurement_quantity_needed": 1250,
    "estimated_margin": 40500,
    "reasons": ["Insufficient raw-material inventory for full order. Additional procurement of 1250 L required."],
    "explainability": {
      "WHAT": "ACCEPT_WITH_CONDITIONS",
      "WHY": "Insufficient raw-material inventory for full order. Additional procurement of 1250 L required.",
      "EVIDENCE": {
        "current_fg_inventory": 80,
        "raw_material_available": 1500,
        "required_raw_material": 2750,
        "procurement_needed": 1250,
        "estimated_margin": 40500
      },
      "ACTION": "Confirm order after securing raw material."
    },
    "trace_id": "REC-2026-a1b2",
    "warning": "This is an estimated feasibility check. User authorisation required to confirm the order."
  },
  "sources": ["inventory_history", "production_capacity_config"],
  "generated_at": "2026-08-29T12:34:56+00:00",
  "model_version": "rules-v1.2"
}
```

---

## 7. What-if Simulation — `POST /intelligence/what-if`

**Request body**:
```json
{
  "business_id": "demo-001",
  "current_margin": 12.5,
  "scenario_type": "MILK_PRICE_INCREASE",
  "percentage_change": 5
}
```

```json
{
  "status": "success",
  "data": {
    "scenario_type": "MILK_PRICE_INCREASE",
    "percentage_change": 5,
    "current_margin": 12.5,
    "new_margin": 7.5,
    "impact_inr": -5.0,
    "recommendation": "Consider increasing selling price by ₹5–₹8/kg or renegotiating procurement terms.",
    "warning": "This is an estimated projection only. Actual outcomes depend on market conditions."
  },
  "sources": ["user_inputs", "business_rules_config"],
  "generated_at": "2026-08-29T12:34:56+00:00",
  "model_version": "rules-v1.2"
}
```

---

## 8. Anomaly Detection — `GET /intelligence/anomalies`

```json
{
  "status": "success",
  "data": {
    "metric": "daily_sales_inr",
    "anomalies": [
      {
        "date": "2026-07-15",
        "value": 142000,
        "z_score": 3.4,
        "label": "SPIKE"
      }
    ],
    "count": 1
  },
  "sources": ["business_transactions"],
  "generated_at": "2026-08-29T12:34:56+00:00",
  "model_version": "rules-v1.2"
}
```

---

## 9. Business Health — `GET /intelligence/business-health`

**Request**: `GET /intelligence/business-health?business_id=demo-001&sales_consistency=88&order_fulfillment=94&inventory_discipline=72&growth_trend=78`

```json
{
  "status": "success",
  "data": {
    "overall_health_score": 84.6,
    "component_scores": {
      "sales_consistency": 88.0,
      "order_fulfillment": 94.0,
      "inventory_discipline": 72.0,
      "growth_trend": 78.0
    },
    "strengths": ["Consistent order fulfillment", "Stable sales pattern"],
    "weaknesses": ["Inventory discipline has room for improvement"],
    "summary_text": "Business health is GOOD at 84.6/100. Strengthen inventory management to reach EXCELLENT status.",
    "verdict": "GOOD"
  },
  "sources": ["sales_history", "order_history", "inventory_history"],
  "generated_at": "2026-08-29T12:34:56+00:00",
  "model_version": "rules-v1.2"
}
```

---

## 10. Credit Readiness — `GET /intelligence/credit-readiness`

**Request**: `GET /intelligence/credit-readiness?business_id=demo-001&sales_consistency=88&order_fulfillment=94&business_activity=85&inventory_discipline=72&growth_trend=78&record_completeness=90`

```json
{
  "status": "success",
  "data": {
    "readiness_indicator_score": 85.05,
    "component_scores": {
      "sales_consistency": 88.0,
      "order_fulfillment": 94.0,
      "business_activity": 85.0,
      "inventory_discipline": 72.0,
      "growth_trend": 78.0,
      "record_completeness": 90.0
    },
    "positive_evidence": ["Consistent sales history", "Strong order fulfillment", "High record completeness"],
    "improvement_areas": ["Inventory management records"],
    "missing_documents": ["Latest financial statement"],
    "summary_text": "Credit readiness indicator: 85.05/100. READY FOR LENDER REVIEW AFTER DOCUMENT COMPLETION.",
    "disclaimer": "This is a readiness indicator based on available platform data. It is NOT a loan approval or rejection decision. The lending institution makes the final credit decision."
  },
  "sources": ["sales_history", "order_history", "inventory_history", "expenses_history"],
  "generated_at": "2026-08-29T12:34:56+00:00",
  "model_version": "readiness-v1.1"
}
```

---

## 11. Scheme Matching — `POST /intelligence/scheme-match`

**Request body**:
```json
{
  "business_id": "demo-001",
  "enterprise_type": "Micro",
  "location_type": "Rural",
  "business_activity": "Dairy Processing"
}
```

```json
{
  "status": "success",
  "data": {
    "matches": [
      {
        "scheme_name": "Dairy Entrepreneurship Development Scheme (DEDS)",
        "description": "Supports dairy entrepreneurs for establishing modern dairy farms and milk processing units.",
        "eligibility_criteria": ["Micro enterprise", "Dairy Processing", "Rural or Semi-Urban"],
        "missing_documents_needed": ["Udyam Registration Certificate", "Project Report"],
        "official_source": "National Bank for Agriculture and Rural Development (NABARD)",
        "official_url": "https://www.nabard.org/",
        "last_verified_date": "2025-12-01"
      }
    ],
    "count": 1,
    "summary_text": "1 potentially relevant government scheme found. Verify current eligibility at official sources.",
    "disclaimer": "Potentially relevant schemes — verify current official eligibility. We do not guarantee eligibility."
  },
  "sources": ["schemes_reference_data"],
  "generated_at": "2026-08-29T12:34:56+00:00",
  "model_version": "rules-v1.2"
}
```

---

## 12. Lender Package — `GET /intelligence/lender-package`

**Request**: `GET /intelligence/lender-package?business_id=demo-001`

```json
{
  "status": "success",
  "data": {
    "business_profile": {
      "business_name": "Kopargaon Dairy Foods",
      "location": "Kopargaon, Maharashtra, India",
      "enterprise_type": "Micro",
      "business_activity": "Dairy Processing"
    },
    "reporting_period": {
      "start_date": "2026-01-01",
      "end_date": "2026-08-28",
      "label": "Jan 2026–Aug 2026"
    },
    "sales_history_summary": {
      "total_sales_volume_litres": 72000,
      "sales_growth": "+12.4%",
      "period": "Jan 2026–Aug 2026",
      "source": "sales_history"
    },
    "procurement_history": {
      "average_monthly_milk_purchase_litres": 9000,
      "preferred_payment_terms": "Weekly cash/bank transfer",
      "source": "purchase_history"
    },
    "production_summary": {
      "average_daily_processed_milk_litres": 300,
      "conversion_efficiency_pct": 98.5,
      "source": "production_records"
    },
    "inventory_summary": {
      "average_inventory_days_cover": 5.2,
      "safety_stock_level_litres": 200,
      "source": "inventory_history"
    },
    "order_fulfillment": {
      "order_fulfillment_rate_pct": 94.0,
      "average_lead_time_days": 1.5,
      "source": "order_history"
    },
    "cost_trends": {
      "milk_price_30_day_change_pct": 5.8,
      "period": "Last 30 days",
      "source": "purchase_history"
    },
    "business_health": {
      "score": 84.6,
      "verdict": "HEALTHY operational status",
      "source": "business_health_module"
    },
    "credit_readiness": {
      "score": 85.05,
      "status": "READY FOR LENDER REVIEW AFTER DOCUMENT COMPLETION",
      "source": "credit_readiness_module"
    },
    "risk_indicators": {
      "unfulfilled_orders_count": 0,
      "price_volatility_risk": "MEDIUM",
      "source": "anomaly_and_price_risk_modules"
    },
    "supporting_documents": {
      "udyam_registration": "AVAILABLE",
      "gstin_record": "AVAILABLE",
      "latest_financial_statement": "MISSING_NEED_UPLOAD",
      "source": "business_profile_config"
    },
    "data_quality_notes": {
      "sales_records_count": 180,
      "valid_sales_days": 178,
      "missing_records_rate": 0.01,
      "reliability_level": "HIGH",
      "source": "data_quality_module"
    },
    "model_rule_versions": {
      "scoring_logic_version": "readiness-v1.1",
      "business_rules_version": "rules-v1.2",
      "source": "model_version_registry"
    },
    "disclaimer": "This report supports lender review; the lender makes the final decision."
  },
  "sources": ["sales_history", "purchase_history", "inventory_history"],
  "generated_at": "2026-08-29T12:34:56+00:00",
  "model_version": "service-v1.0"
}
```

---

## 13. Owner View — `GET /intelligence/owner-view`

**Request**: `GET /intelligence/owner-view?business_id=demo-001`

```json
{
  "status": "success",
  "data": {
    "today": {
      "sales_inr": 84500,
      "orders_pending": 4,
      "milk_available": 1500,
      "price_trend": "INCREASING",
      "inventory_risk": "CRITICAL",
      "business_health": 84.6,
      "credit_readiness": 85.05
    },
    "text_summary": "TODAY'S BUSINESS STATUS\n\nSales:\n₹84,500\n\nExpected demand:\n195 kg Paneer\n\nMilk available:\n1,500 litres\n\nMilk required:\n1,072 litres\n\nPrice trend:\nIncreasing\n\nInventory risk:\nCRITICAL\n\nTop action:\nProcure milk\n\nAdditional action:\nReview New Order Feasibility\n\nBusiness health:\n84.60/100",
    "top_actions": "CRITICAL",
    "demand": {
      "expected_daily": 241.4,
      "trend": "INCREASING"
    },
    "price": {
      "price_trend_summary": "Milk procurement price has increased approximately 5.5% over the last 30 days.",
      "procurement_risk": "Because inventory is also low, procurement risk is HIGH.",
      "recommended_action": "Review procurement timing."
    },
    "inventory": {
      "current_stock": "1,500 L",
      "days_of_cover": "3.0 days",
      "expected_usage": "500 L/day",
      "supplier_lead_time": "3 days",
      "risk_level": "CRITICAL",
      "advice_text": "Milk inventory covers approximately 3.0 days, while supplier lead time is 3 days. This is a stockout risk.",
      "action": "Procure before current stock reaches critical level."
    },
    "procurement": {
      "recommended_action": "BUY_NOW",
      "reason": "Expected demand is increasing, current stock covers only 3.0 days, supplier lead time is 3 days, and milk prices are trending increasing.",
      "recommended_quantity": "1,350 L",
      "estimated_procurement_cost": "₹64,800",
      "disclaimer": "Recommendation is based on current data. Validate before placing purchase order."
    },
    "orders": {
      "order": "500 kg Paneer @ ₹350/kg",
      "decision": "ACCEPT_WITH_CONDITIONS",
      "why": "- Current raw material is insufficient for this order\n- Additional procurement of 1,250 L milk is required\n- Estimated margin remains positive at ₹40,500",
      "required_procurement": "2,750 L milk",
      "estimated_margin": "₹40,500",
      "main_risk": "Supplier delay risk — confirm procurement before committing delivery date.",
      "action": "Confirm procurement before committing delivery."
    },
    "business_health": {
      "overall_score": "84.6/100",
      "strengths": ["Consistent order fulfillment", "Stable sales pattern"],
      "weaknesses": ["Inventory management has room for improvement"]
    },
    "credit_readiness": {
      "overall_score": "85.05/100",
      "positive_evidence": ["Consistent sales history", "Strong order fulfillment"],
      "improvement_areas": ["Inventory consistency"],
      "documents_missing": ["Latest financial statement"],
      "status": "READY FOR LENDER REVIEW AFTER DOCUMENT COMPLETION"
    },
    "scheme_matches": [
      {
        "scheme_name": "Dairy Entrepreneurship Development Scheme (DEDS)",
        "why_it_may_match": "Matches Micro enterprise in Rural for Dairy Processing.",
        "need_to_verify": "Registration requirements and turnover limits.",
        "official_source": "NABARD",
        "guarantee_note": "Potentially relevant — verify current official eligibility."
      }
    ],
    "benchmark_peer_comparison": {
      "product": "PRD-PNR",
      "your_inventory_days": 8.0,
      "anonymous_peer_benchmark": "4.8–5.5",
      "verdict": "Your inventory is higher than the current peer benchmark.",
      "privacy_assurance": "Comparison uses aggregated, anonymized industry statistics. Operational privacy is fully protected; no peer names or transactions are exposed."
    },
    "data_quality": {
      "reliability": "HIGH",
      "assumptions": ["DEMO dataset. Calibrate before going live."]
    },
    "recommendation_evidence": [
      {
        "recommendation_id": "REC-2026-INIT",
        "evidence_dimension": "INVENTORY",
        "metric_score": 72.0,
        "reason": "Days of cover matches safety stock parameters."
      }
    ]
  },
  "sources": ["demo_config", "sales_history"],
  "generated_at": "2026-08-29T12:34:56+00:00",
  "model_version": "service-v1.0"
}
```

---

> **IMPORTANT**: All examples above use **SIMULATED DEMO DATA** from `config/demo_business.json`. Numbers will differ when real MSME records are loaded. Do not present demo figures as actual financial projections.
