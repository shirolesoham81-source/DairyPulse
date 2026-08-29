def calculate_credit_readiness(sales_consistency: float, order_fulfillment: float, 
                               business_activity: float, inventory_discipline: float, 
                               growth_trend: float, record_completeness: float) -> dict:
                               
    score = (sales_consistency * 0.25) + (order_fulfillment * 0.20) + \
            (business_activity * 0.15) + (inventory_discipline * 0.15) + \
            (growth_trend * 0.15) + (record_completeness * 0.10)
            
    strengths = []
    risks = []
    
    if sales_consistency > 80: strengths.append("stable sales")
    if order_fulfillment > 90: strengths.append("good order fulfillment")
    if inventory_discipline < 50: risks.append("working-capital pressure")
    if record_completeness < 100: risks.append("incomplete recent financial records")
    
    return {
        "readiness_indicator_score": round(score, 2),
        "strengths": strengths,
        "risks": risks,
        "missing_information": ["latest financial statement"] if record_completeness < 100 else [],
        "source_records": "Based strictly on platform transactional data."
    }

def generate_credit_readiness_summary(readiness_data: dict) -> str:
    summary = f"Overall readiness: {readiness_data['readiness_indicator_score']}/100\n\n"
    
    if readiness_data['strengths']:
        summary += "Positive evidence:\n- " + "\n- ".join(readiness_data['strengths']) + "\n\n"
        
    if readiness_data['risks']:
        summary += "Weakness:\n- " + "\n- ".join(readiness_data['risks']) + "\n\n"
        
    if readiness_data['missing_information']:
        summary += "Missing evidence:\n- " + "\n- ".join(readiness_data['missing_information']) + "\n\n"
        summary += "Potential next action: Complete missing records before sharing the lender report.\n"
        
    summary += "\n*Note: This is NOT a bank approval decision, only structured evidence.*"
    return summary
