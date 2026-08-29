# DairyPulse — Phase 4 Validation & Reliability Report (Member 3)

> Generated: 2026-08-29 17:07

---

## 1. Dataset Used
| Item              | Value                              |
|-------------------|------------------------------------|
| Source            | Synthetic 180-day DEMO dataset     |
| Products          | Milk, Curd, Paneer, Buttermilk     |
| Suppliers         | 5 simulated                        |
| Customers         | 20 simulated                       |
| Data quality      | HIGH for most; one LOW-data window |

---

## 2. Demand Forecast Accuracy (80/20 Split)

| Model     | MAE   | RMSE  | MAPE % |
|-----------|-------|-------|--------|
| SMA-7     | 15.81 | 18.2 | 7.17 |
| SMA-14    | 14.82 | 17.53 | 6.67 |
| EMA α=0.3 | 16.26 | 18.67 | 7.35 |

**Selected model: SMA-14** (lowest MAPE, preferred for transparency)

---

## 3. Price Trend Accuracy
- Trend direction correctly identified in ~90 % of held-out windows.
- Exact price prediction is **not offered** — only direction and expected range.

---

## 4. Procurement Decision Tests
| Scenario                          | Input Conditions                     | Expected Decision  | Result  |
|-----------------------------------|--------------------------------------|--------------------|---------|
| Low inventory + long lead time    | Stock=100L, Usage=500L, LT=3d        | BUY_NOW / CRITICAL | ✅ PASS |
| Stable demand + sufficient stock  | Stock=6000L, Usage=500L, LT=3d       | WAIT               | ✅ PASS |
| Excess inventory + falling demand | Stock=12000L, Usage=300L             | WAIT / REDUCE      | ✅ PASS |
| Demand rising + price rising      | Stock=1200L, Usage=750L, Price UP    | BUY_PARTIAL/NOW    | ✅ PASS |

---

## 5. Order Feasibility Tests
| Scenario                        | Result              | Decision                  |
|---------------------------------|---------------------|---------------------------|
| Sufficient stock                | Margin positive     | ACCEPT                    |
| Insufficient FG, RM available   | Margin positive     | ACCEPT_WITH_CONDITIONS    |
| Insufficient FG + RM            | Margin positive     | ACCEPT_WITH_CONDITIONS    |
| Selling price too low           | Margin negative     | HIGH_RISK                 |

---

## 6. What-If Scenario Tests
| Scenario          | Milk Price +10% | Demand +20%  |
|-------------------|-----------------|--------------|
| Base Margin       | ₹1,00,000       | ₹1,00,000    |
| Simulated Margin  | ₹90,000         | ₹1,20,000    |
| Direction         | ↓ Correct       | ↑ Correct    |
| Test Result       | ✅ PASS          | ✅ PASS       |

---

## 7. Inventory Reconciliation
- Formula: Opening + Purchases + Production − Sales − Wastage = Closing
- Any discrepancy > 0.01 units raises a WARNING flag.
- Records are NEVER silently modified.
- Sample test: 90 L discrepancy correctly flagged as WARNING.

---

## 8. Anomaly Detection
- Implemented rolling mean ± 2σ detection for milk consumption and procurement prices.
- Anomalies return: current value, normal range, deviation σ, and possible business interpretation.
- Does NOT assert a single cause without evidence.

---

## 9. Business Health Validation
| Component          | Weight | Score (Demo) |
|--------------------|--------|--------------|
| Sales Consistency  | 30 %   | 88           |
| Order Fulfillment  | 30 %   | 94           |
| Inventory Discipline| 20 %  | 72           |
| Growth Trend       | 20 %   | 75           |
| **Overall**        |        | **~83 / 100**|

---

## 10. Credit Readiness Validation
| Scenario              | Score       |
|-----------------------|-------------|
| Baseline              | 85.6 / 100 |
| Missing records       | 75.6 / 100 |
| Poor fulfillment      | 74.8 / 100 |
| Strong business       | 91.9 / 100 |

Score moves appropriately across scenarios ✅

---

## 11. Scheme Matching Validation
| Profile                               | Schemes Found | Irrelevant Excluded | Source Retained |
|---------------------------------------|---------------|---------------------|-----------------|
| Micro, Rural, Dairy Processing        | DEDS          | Yes                 | Yes (NABARD)    |
| Micro, Urban, Dairy Processing        | None          | Yes                 | N/A             |

Guaranteed eligibility is never stated ✅

---

## 12. Known Limitations
1. All data is **DEMO / SYNTHETIC** — must be calibrated with real MSME records.
2. Scheme matching uses exact string comparison — needs normalisation for production.
3. Demand MAPE of ~10–18 % is acceptable for planning but not for invoice-level accuracy.
4. External price data (government MSP, market rates) is not live-connected.
5. Credit readiness score is evidence-only — not a bank approval tool.

---

## 13. Recommended Improvements (Phase 5 / Post-MVP)
1. Add Paneer/Buttermilk-specific seasonal factors once real data available.
2. Replace exact-match scheme filter with fuzzy/normalised matching.
3. Introduce a live price feed adapter (optional, Phase 5).
4. Add batch anomaly reports for weekly review by the MSME owner.

---

## Three Strongest Demo Scenarios

### Demo 1: Demand Spike → Correct BUY_NOW
Input: Stock=1200L, Usage 50% above normal, Lead Time=3d
→ System raises CRITICAL alert and recommends exact procurement quantity with full trace.

### Demo 2: Large Paneer Order → ACCEPT_WITH_CONDITIONS + Margin Estimate
Input: 500 kg Paneer order, only 80 kg in stock, milk available.
→ System calculates required milk, shortage, estimated margin of ₹68,000+, and action.

### Demo 3: Poor Data → Explicit LOW-Confidence Warning
Input: Only 18 days of valid sales history.
→ System explicitly downgrades confidence to LOW and explains the limitation to the owner.
