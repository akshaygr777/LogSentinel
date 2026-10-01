"""
Configuration constants for LogSentinel.
"""

# Log format regex components
# Example log: 2026-09-30 10:15:32 | INFO | GET | /api/users | 200 | 124 | 192.168.1.10
LOG_PATTERN = r"^(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\s*\|\s*(?P<level>\w+)\s*\|\s*(?P<method>\w+)\s*\|\s*(?P<endpoint>\S+)\s*\|\s*(?P<status_code>\d+)\s*\|\s*(?P<response_time>\d+)\s*\|\s*(?P<ip_address>\S+)$"

# Anomaly Detection Defaults
Z_SCORE_THRESHOLD = 3.0
ROLLING_WINDOW_SIZE = 10  # number of recent requests for rolling anomaly
ERROR_SPIKE_WINDOW = "1min" # Pandas offset alias for error grouping
REQUEST_BURST_WINDOW = "1min"
REQUEST_BURST_BASELINE = 40 # requests per window threshold
ERROR_SPIKE_BASELINE_MULTIPLIER = 3.0 # How many times the mean to be considered a spike

# Risk Scoring Weights (Total = 100)
WEIGHT_RESPONSE_ANOMALY = 25
WEIGHT_ERROR_ANOMALY = 30
WEIGHT_REQUEST_BURST = 25
WEIGHT_SERVER_ERROR = 20

# Severity Thresholds
RISK_THRESHOLD_HIGH = 70
RISK_THRESHOLD_MEDIUM = 40
# Below 40 is LOW

# Database
DB_PATH = "database/logsentinel.db"
