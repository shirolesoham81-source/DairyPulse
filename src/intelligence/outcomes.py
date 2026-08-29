"""
src/intelligence/outcomes.py
============================
Feedback Capture and Decision Outcome Tracking for DairyPulse.
Saves user interaction and real-world evaluation metrics to scratch storage.
"""

import os
import json
from datetime import datetime, timezone

# We target the scratch space inside the artifacts folder to avoid modifying raw records.
SCRATCH_DIR = r"C:\Users\SOHAM\.gemini\antigravity-ide\brain\9dc9cc3b-9583-415e-91d5-65ec34fb7a3a\scratch"
DB_PATH = os.path.join(SCRATCH_DIR, "recommendation_outcomes.json")


def _init_db():
    if not os.path.exists(SCRATCH_DIR):
        os.makedirs(SCRATCH_DIR, exist_ok=True)
    if not os.path.exists(DB_PATH):
        with open(DB_PATH, "w") as f:
            json.dump({"feedback": {}, "outcomes": {}}, f, indent=2)


def record_recommendation_feedback(
    recommendation_id: str,
    decision: str,
    owner_action: str,  # ACCEPTED / REJECTED / MODIFIED
    final_quantity: float,
    reason_if_rejected: str | None = None,
) -> dict:
    """
    Saves whether the MSME owner followed, changed, or ignored the recommendations.
    Ensures feedback isn't lost and supports audit reviews.
    """
    _init_db()
    
    if owner_action not in ["ACCEPTED", "REJECTED", "MODIFIED"]:
        raise ValueError("owner_action must be ACCEPTED, REJECTED, or MODIFIED.")

    with open(DB_PATH, "r") as f:
        db = json.load(f)

    entry = {
        "recommendation_id": recommendation_id,
        "decision": decision,
        "owner_action": owner_action,
        "final_quantity": final_quantity,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "reason_if_rejected": reason_if_rejected
    }
    
    db["feedback"][recommendation_id] = entry

    with open(DB_PATH, "w") as f:
        json.dump(db, f, indent=2)

    return entry


def track_decision_outcome(
    recommendation_id: str,
    actual_purchase_quantity: float,
    stockout_occurred: bool,
) -> dict:
    """
    Stores actual operational outcomes after a decision cycle completes.
    Allows comparing recommendations against real events to compute decision accuracy.
    """
    _init_db()

    with open(DB_PATH, "r") as f:
        db = json.load(f)

    entry = {
        "recommendation_id": recommendation_id,
        "actual_purchase_quantity": actual_purchase_quantity,
        "stockout_occurred": stockout_occurred,
        "recorded_at": datetime.now(timezone.utc).isoformat()
    }
    
    db["outcomes"][recommendation_id] = entry

    with open(DB_PATH, "w") as f:
        json.dump(db, f, indent=2)

    return entry


def load_all_outcomes() -> dict:
    """Load the outcomes data database for local report compiling."""
    _init_db()
    with open(DB_PATH, "r") as f:
        return json.load(f)
