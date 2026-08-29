"""
src/intelligence/response.py
============================
Standard response builder for the DairyPulse Intelligence Service.

Every function in service.py must return one of these envelopes to
guarantee a consistent JSON contract across all endpoints.
"""

from datetime import datetime, timezone
from typing import Any
from src.intelligence.version import get_version_manifest


def success(
    data: Any,
    *,
    warnings: list[str] | None = None,
    data_quality: dict | None = None,
    model_version: str = "service-v1.0",
    sources: list[str] | None = None,
) -> dict:
    """Build a standard success response envelope."""
    return {
        "status": "success",
        "data": data,
        "warnings": warnings or [],
        "data_quality": data_quality or {},
        "sources": sources or [],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "model_version": model_version,
        "versions": get_version_manifest(),
    }


def error(
    error_code: str,
    message: str,
    *,
    warnings: list[str] | None = None,
) -> dict:
    """Build a standard error response envelope."""
    return {
        "status": "error",
        "error_code": error_code,
        "message": message,
        "warnings": warnings or [],
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


def data_quality_block(
    *,
    period_days: int,
    valid_records: int,
    missing_rate: float = 0.0,
    reliability: str = "HIGH",
    assumptions: list[str] | None = None,
) -> dict:
    """Build the standard data_quality block embedded in every analytical result."""
    warnings = []
    if missing_rate > 0.5:
        warnings.append(f"High missing-data rate ({missing_rate*100:.0f}%). Reliability reduced to LOW.")
    elif missing_rate > 0.2:
        warnings.append(f"Moderate missing-data rate ({missing_rate*100:.0f}%). Use results with caution.")
    return {
        "data_period_days": period_days,
        "valid_records": valid_records,
        "missing_rate": round(missing_rate, 3),
        "reliability": reliability,
        "assumptions": assumptions or ["DEMO synthetic data. Calibrate with real MSME records."],
        "warnings": warnings,
    }
