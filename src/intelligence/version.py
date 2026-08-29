"""
src/intelligence/version.py
===========================
Model and business-rule version registry for DairyPulse.

Every analytical output should embed the relevant version string so that
reports, dashboards, and audit logs can trace which logic version produced
the result.
"""

# ── Demand forecasting ────────────────────────────────────────────────────────
DEMAND_MODEL_VERSION = "demand-sma-v1.0"
DEMAND_MODEL_DESCRIPTION = "7-day Simple Moving Average baseline (reproducible, no ML dependency)"

# ── Price intelligence ────────────────────────────────────────────────────────
PRICE_MODEL_VERSION = "price-ma-v1.0"
PRICE_MODEL_DESCRIPTION = "30-day rolling average with trend classification"

# ── Business rules ────────────────────────────────────────────────────────────
BUSINESS_RULES_VERSION = "rules-v1.2"
BUSINESS_RULES_DESCRIPTION = "Inventory risk bands, procurement thresholds, margin floor from config/business_rules.json"

# ── Credit readiness ──────────────────────────────────────────────────────────
READINESS_SCORING_VERSION = "readiness-v1.1"
READINESS_SCORING_DESCRIPTION = "Weighted 6-dimension scoring. Weights configurable in business_rules.json"

# ── Service layer ─────────────────────────────────────────────────────────────
SERVICE_VERSION = "service-v1.0"

# ── Python environment ────────────────────────────────────────────────────────
PYTHON_VERSION_MINIMUM = "3.10"
REQUIREMENTS_FILE = "requirements.txt"


def get_version_manifest() -> dict:
    """Return a dict of all version strings — embed in every API response."""
    return {
        "demand_model": DEMAND_MODEL_VERSION,
        "price_model": PRICE_MODEL_VERSION,
        "business_rules": BUSINESS_RULES_VERSION,
        "readiness_scoring": READINESS_SCORING_VERSION,
        "service": SERVICE_VERSION,
    }
