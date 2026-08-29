import uuid
from datetime import datetime

class DecisionTrace:
    @staticmethod
    def create_trace(decision: str, item: str, quantity: float, evidence: dict, reason: str, action_desc: str) -> dict:
        return {
            "recommendation_id": f"REC-{datetime.now().strftime('%Y')}-{str(uuid.uuid4())[:6]}",
            "decision": decision,
            "item": item,
            "quantity": quantity,
            "evidence": evidence,
            "reason": reason,
            "explainability": {
                "WHAT": decision,
                "WHY": reason,
                "EVIDENCE": evidence,
                "ACTION": action_desc
            }
        }
