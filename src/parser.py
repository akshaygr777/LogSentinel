import pandas as pd
import re
import logging
from .config import LOG_PATTERN

logger = logging.getLogger(__name__)

class LogParser:
    def __init__(self):
        self.pattern = re.compile(LOG_PATTERN)

    def parse_line(self, line):
        """Parses a single log line into a dictionary."""
        match = self.pattern.match(line.strip())
        if match:
            return match.groupdict()
        else:
            return None

    def parse_file(self, filepath):
        """Parses an entire log file and returns a Pandas DataFrame."""
        parsed_data = []
        malformed_lines = 0

        try:
            with open(filepath, 'r') as f:
                for line in f:
                    if not line.strip():
                        continue
                    parsed_record = self.parse_line(line)
                    if parsed_record:
                        parsed_data.append(parsed_record)
                    else:
                        malformed_lines += 1
                        logger.warning(f"Malformed log line skipped: {line.strip()}")
        except FileNotFoundError:
            logger.error(f"File not found: {filepath}")
            raise

        if malformed_lines > 0:
            logger.info(f"Skipped {malformed_lines} malformed lines.")

        if not parsed_data:
            logger.warning("No valid log lines parsed.")
            # Return empty dataframe with expected columns
            return pd.DataFrame(columns=["timestamp", "level", "method", "endpoint", "status_code", "response_time", "ip_address"])
            
        df = pd.DataFrame(parsed_data)
        return self.clean_data(df)

    def clean_data(self, df):
        """Validates and converts types for the parsed DataFrame."""
        if df.empty:
            return df
            
        try:
            df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
            df['status_code'] = pd.to_numeric(df['status_code'], errors='coerce', downcast='integer')
            df['response_time'] = pd.to_numeric(df['response_time'], errors='coerce', downcast='integer')
            
            # Drop rows with NaT in timestamp or NaN in critical numeric fields
            initial_len = len(df)
            df = df.dropna(subset=['timestamp', 'status_code', 'response_time'])
            dropped_len = initial_len - len(df)
            
            if dropped_len > 0:
                logger.warning(f"Dropped {dropped_len} rows due to invalid data types (e.g., bad timestamps).")
            
            # Ensure types
            df['status_code'] = df['status_code'].astype(int)
            df['response_time'] = df['response_time'].astype(int)
            
            # Sort by time
            df = df.sort_values(by='timestamp').reset_index(drop=True)
            
            return df
        except Exception as e:
            logger.error(f"Error during data cleaning: {str(e)}")
            raise
