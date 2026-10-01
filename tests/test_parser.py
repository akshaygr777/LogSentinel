import pytest
import pandas as pd
from src.parser import LogParser
import tempfile
import os

@pytest.fixture
def parser():
    return LogParser()

def test_parse_valid_line(parser):
    line = "2026-09-30 10:15:32 | INFO | GET | /api/users | 200 | 124 | 192.168.1.10\n"
    result = parser.parse_line(line)
    assert result is not None
    assert result['timestamp'] == "2026-09-30 10:15:32"
    assert result['status_code'] == "200"
    assert result['response_time'] == "124"
    assert result['ip_address'] == "192.168.1.10"

def test_parse_malformed_line(parser):
    line = "This is a random garbage line"
    result = parser.parse_line(line)
    assert result is None

def test_parse_file_and_clean_data(parser):
    # Create temp log file
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write("2026-09-30 10:15:32 | INFO | GET | /api/users | 200 | 124 | 192.168.1.10\n")
        f.write("2026-09-30 10:15:33 | ERROR | POST | /api/payment | 500 | 500 | 192.168.1.11\n")
        f.write("Malformed line missing elements\n")
        f.write("2026-09-30 10:15:34 | INFO | GET | /api/users | 200 | INVALID_TIME | 192.168.1.12\n") # Will be dropped in cleaning
        temp_name = f.name
        
    try:
        df = parser.parse_file(temp_name)
        assert len(df) == 2
        assert list(df['status_code']) == [200, 500]
        assert df['response_time'].dtype == 'int32' or df['response_time'].dtype == 'int64'
    finally:
        os.remove(temp_name)
