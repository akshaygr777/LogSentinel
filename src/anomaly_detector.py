import pandas as pd
import numpy as np
from .config import (
    Z_SCORE_THRESHOLD, 
    ROLLING_WINDOW_SIZE, 
    ERROR_SPIKE_WINDOW, 
    REQUEST_BURST_WINDOW,
    REQUEST_BURST_BASELINE,
    ERROR_SPIKE_BASELINE_MULTIPLIER
)
from .risk_scorer import calculate_risk_score, determine_severity

class AnomalyDetector:
    def __init__(self, df):
        self.df = df
        self.anomalies = []

    def detect_all(self):
        """Runs all anomaly detection algorithms and returns a list of anomaly dictionaries."""
        if self.df.empty:
            return []
            
        self._detect_z_score()
        self._detect_rolling_window()
        self._detect_error_spikes()
        self._detect_request_bursts()
        
        return self.anomalies

    def _add_anomaly(self, timestamp, endpoint, ip_address, anomaly_type, observed, baseline, anomaly_score, reason, is_server_error=False):
        # Calculate deviation factor for risk scoring
        deviation_factor = 1.0
        if baseline > 0:
            deviation_factor = observed / baseline
        elif anomaly_score > 0: # For z-score
            deviation_factor = anomaly_score / Z_SCORE_THRESHOLD

        risk_score = calculate_risk_score(anomaly_type, deviation_factor, is_server_error)
        severity = determine_severity(risk_score)

        self.anomalies.append({
            "timestamp": timestamp,
            "endpoint": endpoint,
            "ip_address": ip_address,
            "anomaly_type": anomaly_type,
            "observed_value": float(observed),
            "baseline_value": float(baseline),
            "anomaly_score": float(anomaly_score),
            "risk_score": risk_score,
            "severity": severity,
            "reason": reason
        })

    def _detect_z_score(self):
        """Detects unusually high response times across the whole dataset."""
        if len(self.df) < 2:
            return
            
        mean_rt = self.df['response_time'].mean()
        std_rt = self.df['response_time'].std()
        
        if std_rt == 0:
            return
            
        self.df['z_score'] = (self.df['response_time'] - mean_rt) / std_rt
        
        anomalies_df = self.df[self.df['z_score'].abs() > Z_SCORE_THRESHOLD]
        
        for _, row in anomalies_df.iterrows():
            is_5xx = 500 <= row['status_code'] < 600
            self._add_anomaly(
                timestamp=row['timestamp'],
                endpoint=row['endpoint'],
                ip_address=row['ip_address'],
                anomaly_type="Z_SCORE_ANOMALY",
                observed=row['response_time'],
                baseline=mean_rt,
                anomaly_score=row['z_score'],
                reason=f"Response time {row['response_time']}ms exceeded Z-Score threshold ({row['z_score']:.2f})",
                is_server_error=is_5xx
            )

    def _detect_rolling_window(self):
        """Detects response time anomalies based on recent history per endpoint."""
        for endpoint, group in self.df.groupby('endpoint'):
            if len(group) < ROLLING_WINDOW_SIZE + 1:
                continue
                
            group = group.sort_values('timestamp')
            
            # Calculate rolling stats
            rolling_mean = group['response_time'].rolling(window=ROLLING_WINDOW_SIZE, min_periods=ROLLING_WINDOW_SIZE).mean().shift(1)
            rolling_std = group['response_time'].rolling(window=ROLLING_WINDOW_SIZE, min_periods=ROLLING_WINDOW_SIZE).std().shift(1)
            
            group['rolling_mean'] = rolling_mean
            group['rolling_std'] = rolling_std
            
            # Avoid division by zero
            group['rolling_std'] = group['rolling_std'].replace(0, 1)
            
            group['rolling_z'] = (group['response_time'] - group['rolling_mean']) / group['rolling_std']
            
            anomalies = group[group['rolling_z'].abs() > Z_SCORE_THRESHOLD]
            
            for _, row in anomalies.iterrows():
                # Avoid duplicate with Z-score if possible, though it's fine if they overlap
                # as they measure different things (global vs local baseline)
                is_5xx = 500 <= row['status_code'] < 600
                self._add_anomaly(
                    timestamp=row['timestamp'],
                    endpoint=endpoint,
                    ip_address=row['ip_address'],
                    anomaly_type="ROLLING_WINDOW_ANOMALY",
                    observed=row['response_time'],
                    baseline=row['rolling_mean'],
                    anomaly_score=row['rolling_z'],
                    reason=f"Response time {row['response_time']}ms is anomalous compared to recent {ROLLING_WINDOW_SIZE} requests",
                    is_server_error=is_5xx
                )

    def _detect_error_spikes(self):
        """Detects spikes in errors over time windows."""
        # Create a copy with timestamp as index for resampling
        df_time = self.df.set_index('timestamp')
        
        # 1 for error, 0 for success
        df_time['is_error'] = (df_time['status_code'] >= 400).astype(int)
        
        # Resample by window to count errors
        error_counts = df_time['is_error'].resample(ERROR_SPIKE_WINDOW).sum()
        
        if len(error_counts) < 2:
            return
            
        historical_mean = error_counts.mean()
        
        # Define spike threshold (e.g., 3x historical mean or at least 5 errors)
        threshold = max(historical_mean * ERROR_SPIKE_BASELINE_MULTIPLIER, 5)
        
        spikes = error_counts[error_counts > threshold]
        
        for timestamp, count in spikes.items():
            self._add_anomaly(
                timestamp=timestamp,
                endpoint="MULTIPLE",
                ip_address="MULTIPLE",
                anomaly_type="ERROR_SPIKE",
                observed=count,
                baseline=historical_mean,
                anomaly_score=count / historical_mean if historical_mean > 0 else count,
                reason=f"Detected {int(count)} errors in window, historical average is {historical_mean:.2f}",
                is_server_error=True # Treat error spikes heavily
            )

    def _detect_request_bursts(self):
        """Detects unusually high request frequency from a single IP."""
        df_time = self.df.set_index('timestamp')
        
        for ip, group in df_time.groupby('ip_address'):
            # Count requests per window
            counts = group.resample(REQUEST_BURST_WINDOW).size()
            
            if len(counts) < 2:
                continue
                
            baseline = counts.mean()
            threshold = max(baseline * 3, REQUEST_BURST_BASELINE)
            
            bursts = counts[counts > threshold]
            
            for timestamp, count in bursts.items():
                self._add_anomaly(
                    timestamp=timestamp,
                    endpoint="MULTIPLE",
                    ip_address=ip,
                    anomaly_type="REQUEST_BURST",
                    observed=count,
                    baseline=baseline,
                    anomaly_score=count / baseline if baseline > 0 else count,
                    reason=f"IP {ip} made {int(count)} requests in window, baseline is {baseline:.2f}"
                )
