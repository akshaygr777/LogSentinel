import pytest
import os
import pandas as pd
from src.database import DatabaseManager
import tempfile

@pytest.fixture
def db():
    # Use a temp file for testing
    fd, temp_path = tempfile.mkstemp()
    os.close(fd)
    db_manager = DatabaseManager(temp_path)
    yield db_manager
    # Clean up
    try:
        os.remove(temp_path)
    except PermissionError:
        pass # Ignore on Windows if still locked

def test_insert_and_get_logs(db):
    data = {
        'timestamp': pd.to_datetime(['2026-09-30 10:00:00']),
        'level': ['INFO'],
        'method': ['GET'],
        'endpoint': ['/api/users'],
        'status_code': [200],
        'response_time': [100],
        'ip_address': ['192.168.1.1']
    }
    df = pd.DataFrame(data)
    
    db.insert_logs(df)
    
    retrieved_df = db.get_all_logs()
    assert len(retrieved_df) == 1
    assert retrieved_df.iloc[0]['endpoint'] == '/api/users'

def test_insert_and_get_anomalies(db):
    anomalies = [{
        "timestamp": "2026-09-30 10:00:00",
        "endpoint": "/api/users",
        "ip_address": "192.168.1.1",
        "anomaly_type": "Z_SCORE_ANOMALY",
        "observed_value": 1500.0,
        "baseline_value": 100.0,
        "anomaly_score": 7.5,
        "risk_score": 80,
        "severity": "HIGH",
        "reason": "Test"
    }]
    
    db.insert_anomalies(anomalies)
    
    retrieved_df = db.get_all_anomalies()
    assert len(retrieved_df) == 1
    assert retrieved_df.iloc[0]['anomaly_type'] == 'Z_SCORE_ANOMALY'
