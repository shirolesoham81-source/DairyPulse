# Member 3 — Setup & Reproducibility Guide

> This document contains the exact commands to install, test, and run the DairyPulse Business Intelligence & Decision Engine (Member 3) on any supported system.

---

## System Requirements

| Requirement | Value |
|---|---|
| Python | ≥ 3.10 (tested on **3.14.0**) |
| Operating System | Windows 10+, Ubuntu 20.04+, macOS 12+ |
| Memory | 512 MB minimum |
| Disk | 200 MB for dependencies + data |

---

## Installation

### Step 1 — Clone or open the workspace

```
cd dairypulse/
```

### Step 2 — (Recommended) Create a virtual environment

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

### Step 3 — Install dependencies

```bash
pip install -r requirements.txt
```

**Current `requirements.txt`**:
```
pandas>=2.0.0
pytest>=7.0.0
faker>=19.0.0
openpyxl>=3.1.0
fastapi>=0.95.0
uvicorn>=0.21.0
scikit-learn>=1.2.0
```

> [!NOTE]
> `scikit-learn` is listed as a dependency for potential future use. The current MVP uses only deterministic SMA/rule-based algorithms with no sklearn estimators. It can be removed if deployment size is a concern.

---

## Configuration Files

All business-logic thresholds are stored in:

```
config/
├── business_rules.json     ← inventory thresholds, pricing sigma, health weights, lead times
└── demo_business.json      ← synthetic demo scenario for testing and demos
```

**Never hardcode thresholds in Python files.** Always read from `_cfg()` in `service.py`.

---

## Running Tests

```bash
# Run all tests (quiet)
pytest -q

# Run all tests (verbose, shows each test name)
pytest -v

# Run only integration tests
pytest tests/test_integration.py -v

# Run only owner-facing output tests
pytest tests/test_owner_integration.py -v

# Run only edge-case tests
pytest tests/test_edge_cases.py -v
```

**Expected result (current)**:
```
41 passed, 2 skipped in 0.53s
```

The 2 skipped tests (`test_inventory_balance`, `test_sales_positive`) are from the data-generator module. They only run after the synthetic data generation script is executed.

> [!IMPORTANT]
> Do NOT modify test assertions to force them to pass. If a test fails, fix the implementation.

---

## Running the Demo CLI

```bash
python -m src.intelligence.demo
```

**Expected output format**:
```
=== DAIRYPULSE BUSINESS INTELLIGENCE DEMO ===

TODAY:
  sales_inr: 84,500
  orders_pending: 4

DEMAND:
  paneer_expected_kg_per_day: 195
  trend: INCREASING

INVENTORY:
  milk_litres: 1,500
  milk_days_cover: 3
  risk: CRITICAL
  recommendation: Procure immediately to avoid stockout.

PRICE:
  milk_current_per_litre: 48
  milk_trend: INCREASING
  milk_30d_change_pct: 5.49

ACTION:
  BUY

ORDER:
  product: Paneer
  qty_kg: 500
  decision: ACCEPT_WITH_CONDITIONS
  estimated_margin_inr: 40,500

BUSINESS HEALTH: 84.60/100
CREDIT READINESS: 85.05/100
SCHEME MATCHES: 1 potentially relevant

TOP ACTIONS:
  - Procure milk
  - Review New Order Feasibility
  - Review procurement timing

Disclaimer: This is simulated demo data. All numbers are synthetic.
```

---

## Running the Intelligence Service (FastAPI)

If Member 2 is integrating via HTTP:

```bash
uvicorn src.main:app --reload --port 8000
```

Then access:
- `GET  http://localhost:8000/intelligence/summary?business_id=demo-001`
- `GET  http://localhost:8000/intelligence/owner-view?business_id=demo-001`
- `POST http://localhost:8000/intelligence/order-feasibility` (with JSON body)

> [!NOTE]
> The FastAPI integration (`src/main.py`, `src/api/`) is implemented but the primary tested interface is the Python service layer (`src/intelligence/service.py`). Member 2 can call the functions directly in Python OR route HTTP calls through FastAPI.

---

## Reproducibility Settings

All outputs are **fully deterministic** given the same input data:

| Component | Seed / Determinism |
|---|---|
| Demand SMA | Deterministic — pure rolling average |
| Price MA | Deterministic — pure rolling average |
| Inventory risk | Deterministic — threshold comparison |
| Procurement decision | Deterministic — rule-based |
| Order feasibility | Deterministic — arithmetic |
| Business health | Deterministic — weighted sum |
| Credit readiness | Deterministic — weighted sum |
| Anomaly detection | Deterministic — z-score |
| Scheme matching | Deterministic — keyword rules |
| What-if simulation | Deterministic — arithmetic |

Random seeds (`random.seed(42)`) are set in any helper that uses randomness (currently only data generation scripts, not intelligence modules).

---

## Verifying Environment

```bash
python -c "import pandas; import pytest; print('OK')"
```

```bash
python -c "from src.intelligence.service import get_business_summary; print(get_business_summary('demo-001')['status'])"
# Expected: success
```

---

## Version Registry

| Component | Version |
|---|---|
| Demand model | `demand-sma-v1.0` |
| Price model | `price-ma-v1.0` |
| Business rules | `rules-v1.2` |
| Credit readiness | `readiness-v1.1` |
| Service layer | `service-v1.0` |

Version strings are embedded in every API response under the `versions` key.
