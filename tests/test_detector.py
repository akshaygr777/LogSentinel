import pytest
import pandas as pd
import numpy as np
from src.anomaly_detector import AnomalyDetector
from src.config import Z_SCORE_THRESHOLD

def test_z_score_detection():
    # Create dataset with one obvious outlier
    response_times = [100] * 50 + [1500]  # mean ~ 127, std ~ 196. Z for 1500 ~ 7.0
    data = {
        'timestamp': pd.date_range(start='2026-09-30 10:00:00', periods=51, freq='1s'),
        'endpoint': ['/api/test'] * 51,
        'status_code': [200] * 51,
        'response_time': response_times,
        'ip_address': ['192.168.1.1'] * 51
    }
    df = pd.DataFrame(data)
    
    detector = AnomalyDetector(df)
    detector._detect_z_score()
    
    anomalies = detector.anomalies
    assert len(anomalies) == 1
    assert anomalies[0]['anomaly_type'] == 'Z_SCORE_ANOMALY'
    assert anomalies[0]['observed_value'] == 1500

def test_error_spike_detection():
    # 10 minutes of data. First 9 minutes: 1 error per minute. 10th minute: 20 errors.
    times = []
    status_codes = []
    
    for i in range(9):
        # 1 error per minute
        times.extend(list(pd.date_range(start=f'2026-09-30 10:0{i}:00', periods=5, freq='10s')))
        status_codes.extend([200]*4 + [500])
        
    # The spike minute
    times.extend(list(pd.date_range(start='2026-09-30 10:09:00', periods=20, freq='2s')))
    status_codes.extend([500]*20)
    
    data = {
        'timestamp': times,
        'endpoint': ['/api/test'] * len(times),
        'status_code': status_codes,
        'response_time': [100] * len(times),
        'ip_address': ['192.168.1.1'] * len(times)
    }
    df = pd.DataFrame(data)
    
    detector = AnomalyDetector(df)
    detector._detect_error_spikes()
    
    anomalies = detector.anomalies
    assert len(anomalies) >= 1
    assert any(a['anomaly_type'] == 'ERROR_SPIKE' for a in anomalies)
    assert any(a['observed_value'] == 20 for a in anomalies)
