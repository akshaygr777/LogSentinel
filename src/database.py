import sqlite3
import pandas as pd
import logging
import os
from .config import DB_PATH

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        """Initializes the database schema if it doesn't exist."""
        if self.db_path != ":memory:":
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Create logs table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME,
                    level TEXT,
                    method TEXT,
                    endpoint TEXT,
                    status_code INTEGER,
                    response_time INTEGER,
                    ip_address TEXT
                )
            ''')
            
            # Create anomalies table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS anomalies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME,
                    endpoint TEXT,
                    ip_address TEXT,
                    anomaly_type TEXT,
                    observed_value REAL,
                    baseline_value REAL,
                    anomaly_score REAL,
                    risk_score INTEGER,
                    severity TEXT,
                    reason TEXT
                )
            ''')
            
            conn.commit()

    def insert_logs(self, df):
        """Inserts a pandas DataFrame of logs into the database."""
        if df.empty:
            return
            
        # Ensure we only insert columns that exist in the database schema
        valid_columns = ['timestamp', 'level', 'method', 'endpoint', 'status_code', 'response_time', 'ip_address']
        columns_to_keep = [col for col in valid_columns if col in df.columns]
        
        # Convert timestamp back to string for sqlite
        df_copy = df[columns_to_keep].copy()
        df_copy['timestamp'] = df_copy['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
        
        with self._get_connection() as conn:
            df_copy.to_sql('logs', conn, if_exists='append', index=False)
            
    def insert_anomalies(self, anomalies_list):
        """Inserts a list of anomaly dictionaries into the database."""
        if not anomalies_list:
            return
            
        df = pd.DataFrame(anomalies_list)
        # Convert timestamp
        df['timestamp'] = pd.to_datetime(df['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
        
        with self._get_connection() as conn:
            df.to_sql('anomalies', conn, if_exists='append', index=False)

    def get_all_logs(self):
        """Retrieves all logs as a pandas DataFrame."""
        with self._get_connection() as conn:
            df = pd.read_sql_query("SELECT * FROM logs", conn)
            if not df.empty:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
            return df
            
    def get_all_anomalies(self):
        """Retrieves all anomalies as a pandas DataFrame."""
        with self._get_connection() as conn:
            df = pd.read_sql_query("SELECT * FROM anomalies", conn)
            if not df.empty:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
            return df
            
    def clear_database(self):
        """Clears all data from the tables."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM logs")
            cursor.execute("DELETE FROM anomalies")
            conn.commit()
