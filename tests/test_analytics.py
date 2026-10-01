import pytest
import pandas as pd
from src.analytics import LogAnalytics

@pytest.fixture
def sample_df():
    data = {
        'timestamp': pd.to_datetime(['2026-09-30 10:00:00', '2026-09-30 10:00:01', '2026-09-30 10:00:02']),
        'endpoint': ['/api/users', '/api/users', '/api/payment'],
        'status_code': [200, 404, 500],
        'response_time': [100, 50, 500]
    }
    return pd.DataFrame(data)

def test_overall_metrics(sample_df):
    analytics = LogAnalytics(sample_df)
    metrics = analytics.get_overall_metrics()
    
    assert metrics['total_requests'] == 3
    assert metrics['successful_requests'] == 1
    assert metrics['client_errors'] == 1
    assert metrics['server_errors'] == 1
    assert metrics['total_errors'] == 2
    assert metrics['error_rate'] == (2/3) * 100
    assert metrics['avg_response_time'] == (100+50+500)/3
    assert metrics['max_response_time'] == 500

def test_endpoint_metrics(sample_df):
    analytics = LogAnalytics(sample_df)
    metrics = analytics.get_endpoint_metrics()
    
    users_metrics = metrics[metrics['endpoint'] == '/api/users'].iloc[0]
    assert users_metrics['request_count'] == 2
    assert users_metrics['error_count'] == 1
    assert users_metrics['error_rate'] == 50.0
    
def test_status_code_distribution(sample_df):
    analytics = LogAnalytics(sample_df)
    dist = analytics.get_status_code_distribution()
    
    assert dist['2xx'] == 1
    assert dist['3xx'] == 0
    assert dist['4xx'] == 1
    assert dist['5xx'] == 1
