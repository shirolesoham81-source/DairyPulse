import pytest
from src.credit.readiness import calculate_credit_readiness
from src.schemes.matcher import match_government_schemes

def test_credit_readiness_missing_records():
    res1 = calculate_credit_readiness(90, 90, 90, 90, 90, 100)
    res2 = calculate_credit_readiness(90, 90, 90, 90, 90, 0) # 0 record completeness
    
    assert res2['readiness_indicator_score'] < res1['readiness_indicator_score']
    assert "incomplete recent financial records" in res2['risks']

def test_scheme_matching_accuracy():
    # Matching Micro, Rural, Dairy Processing
    matches = match_government_schemes("Micro", "Rural", "Dairy Processing")
    
    # Based on dummy schemes created in Phase 2
    # PMEGP matches Micro, Rural, Manufacturing/Service (Not Dairy Processing explicitly) -> Maybe missed if exact
    # DEDS matches Micro, Rural, Dairy Processing -> Should match
    
    found_deds = any(m['scheme_name'] == "Dairy Entrepreneurship Development Scheme (DEDS)" for m in matches)
    assert found_deds is True
