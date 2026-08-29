def calculate_business_health(sales_consistency_score: float, order_fulfillment_rate: float, 
                              inventory_discipline_score: float, growth_trend_score: float) -> dict:
    
    overall = (sales_consistency_score * 0.3) + (order_fulfillment_rate * 0.3) + \
              (inventory_discipline_score * 0.2) + (growth_trend_score * 0.2)
              
    return {
        "overall_health_score": round(overall, 2),
        "components": {
            "sales_consistency": round(sales_consistency_score, 2),
            "order_fulfillment": round(order_fulfillment_rate, 2),
            "inventory_discipline": round(inventory_discipline_score, 2),
            "growth_trend": round(growth_trend_score, 2)
        },
        "evidence": "Computed deterministically from 180-day operational averages."
    }

def generate_business_health_summary(health_data: dict) -> str:
    score = health_data['overall_health_score']
    comps = health_data['components']
    
    strong = []
    weak = []
    
    for k, v in comps.items():
        if v > 80:
            strong.append(k.replace('_', ' '))
        elif v < 60:
            weak.append(k.replace('_', ' '))
            
    summary = f"Business Health: {score}/100\n\n"
    if strong:
        summary += "Strong:\n- " + "\n- ".join(strong) + "\n\n"
    if weak:
        summary += "Weak:\n- " + "\n- ".join(weak) + "\n\n"
        summary += "Recommended improvement: Focus on addressing weak operational areas."
        
    return summary
