import json

def match_government_schemes(enterprise_type: str, location_type: str, business_activity: str) -> list:
    try:
        with open('data/reference/schemes.json', 'r') as f:
            schemes = json.load(f)
    except FileNotFoundError:
        return []
        
    matches = []
    for scheme in schemes:
        if (enterprise_type in scheme['enterprise_criteria'] and 
            location_type in scheme['location_criteria'] and 
            business_activity in scheme['business_activity_criteria']):
            
            matches.append({
                "scheme_name": scheme['scheme_name'],
                "status": "Potentially relevant",
                "why_it_matched": f"Matches {enterprise_type} enterprise in {location_type} for {business_activity}.",
                "what_needs_verification": "Current official eligibility rules.",
                "missing_documents_needed": scheme['required_documents'],
                "official_source": scheme['official_source'],
                "last_verified_date": scheme.get('last_verified_date', 'Unknown')
            })
            
    return matches

def generate_scheme_summary(matches: list) -> str:
    if not matches:
        return "No schemes matched current profile."
        
    summary = ""
    for m in matches:
        summary += f"Scheme name: {m['scheme_name']}\n"
        summary += f"Why potentially relevant: {m['why_it_matched']}\n"
        summary += f"Missing information: {m['what_needs_verification']}\n"
        summary += f"Documents needed: {', '.join(m['missing_documents_needed'])}\n"
        summary += f"Official source: {m['official_source']}\n"
        summary += f"Last verified date: {m['last_verified_date']}\n\n"
        
    summary += "*Disclaimer: Potentially relevant - verify current official eligibility. We do not guarantee eligibility.*"
    return summary
