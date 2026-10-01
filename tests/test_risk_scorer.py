import pytest
from src.risk_scorer import calculate_risk_score, determine_severity

def test_risk_scorer_low():
    # Small deviation
    score = calculate_risk_score("Z_SCORE_ANOMALY", deviation_factor=1.1, is_server_error=False)
    assert score < 40
    assert determine_severity(score) == "LOW"

def test_risk_scorer_medium():
    score = calculate_risk_score("ERROR_SPIKE", deviation_factor=1.5, is_server_error=False)
    assert 40 <= score < 70
    assert determine_severity(score) == "MEDIUM"
    
def test_risk_scorer_high():
    # High deviation and server error
    score = calculate_risk_score("ERROR_SPIKE", deviation_factor=3.0, is_server_error=True)
    assert score >= 70
    assert determine_severity(score) == "HIGH"

def test_risk_scorer_max():
    score = calculate_risk_score("REQUEST_BURST", deviation_factor=100.0, is_server_error=True)
    assert score <= 100
