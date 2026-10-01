from .config import (
    WEIGHT_RESPONSE_ANOMALY,
    WEIGHT_ERROR_ANOMALY,
    WEIGHT_REQUEST_BURST,
    WEIGHT_SERVER_ERROR,
    RISK_THRESHOLD_HIGH,
    RISK_THRESHOLD_MEDIUM
)

def calculate_risk_score(anomaly_type, deviation_factor=1.0, is_server_error=False):
    """
    Calculates a risk score (0-100) based on anomaly type and severity of deviation.
    """
    score = 0
    
    if anomaly_type in ["Z_SCORE_ANOMALY", "ROLLING_WINDOW_ANOMALY"]:
        # Base weight for response time anomaly, scaled by how large the deviation is (cap at 2x weight)
        scaled_weight = min(WEIGHT_RESPONSE_ANOMALY * deviation_factor, WEIGHT_RESPONSE_ANOMALY * 2)
        score += scaled_weight
        
    elif anomaly_type == "ERROR_SPIKE":
        score += min(WEIGHT_ERROR_ANOMALY * deviation_factor, WEIGHT_ERROR_ANOMALY * 2)
        
    elif anomaly_type == "REQUEST_BURST":
        score += min(WEIGHT_REQUEST_BURST * deviation_factor, WEIGHT_REQUEST_BURST * 2)
        
    if is_server_error:
        score += WEIGHT_SERVER_ERROR
        
    return min(100, int(score))

def determine_severity(risk_score):
    """
    Classifies risk score into LOW, MEDIUM, or HIGH severity.
    """
    if risk_score >= RISK_THRESHOLD_HIGH:
        return "HIGH"
    elif risk_score >= RISK_THRESHOLD_MEDIUM:
        return "MEDIUM"
    else:
        return "LOW"
