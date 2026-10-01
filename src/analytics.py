import pandas as pd

class LogAnalytics:
    def __init__(self, df):
        """Initializes with a cleaned pandas DataFrame."""
        self.df = df

    def get_overall_metrics(self):
        """Calculates high-level metrics."""
        if self.df.empty:
            return {
                "total_requests": 0,
                "successful_requests": 0,
                "client_errors": 0,
                "server_errors": 0,
                "total_errors": 0,
                "error_rate": 0.0,
                "avg_response_time": 0.0,
                "median_response_time": 0.0,
                "max_response_time": 0,
                "min_response_time": 0
            }
            
        total_requests = len(self.df)
        successful = len(self.df[self.df['status_code'].between(200, 299)])
        client_errors = len(self.df[self.df['status_code'].between(400, 499)])
        server_errors = len(self.df[self.df['status_code'].between(500, 599)])
        total_errors = client_errors + server_errors
        
        return {
            "total_requests": total_requests,
            "successful_requests": successful,
            "client_errors": client_errors,
            "server_errors": server_errors,
            "total_errors": total_errors,
            "error_rate": (total_errors / total_requests) * 100 if total_requests > 0 else 0.0,
            "avg_response_time": self.df['response_time'].mean(),
            "median_response_time": self.df['response_time'].median(),
            "max_response_time": self.df['response_time'].max(),
            "min_response_time": self.df['response_time'].min()
        }

    def get_endpoint_metrics(self):
        """Calculates metrics grouped by endpoint."""
        if self.df.empty:
            return pd.DataFrame()
            
        # Group by endpoint
        grouped = self.df.groupby('endpoint')
        
        metrics = grouped.agg(
            request_count=('timestamp', 'count'),
            avg_response_time=('response_time', 'mean'),
            max_response_time=('response_time', 'max')
        ).reset_index()
        
        # Calculate errors
        error_df = self.df[self.df['status_code'] >= 400]
        error_counts = error_df.groupby('endpoint').size().reset_index(name='error_count')
        
        # Merge
        result = pd.merge(metrics, error_counts, on='endpoint', how='left').fillna(0)
        result['error_count'] = result['error_count'].astype(int)
        
        # Calculate error rate
        result['error_rate'] = (result['error_count'] / result['request_count']) * 100
        
        return result

    def get_status_code_distribution(self):
        """Calculates distribution of HTTP status codes."""
        if self.df.empty:
            return {"2xx": 0, "3xx": 0, "4xx": 0, "5xx": 0}
            
        return {
            "2xx": len(self.df[self.df['status_code'].between(200, 299)]),
            "3xx": len(self.df[self.df['status_code'].between(300, 399)]),
            "4xx": len(self.df[self.df['status_code'].between(400, 499)]),
            "5xx": len(self.df[self.df['status_code'].between(500, 599)])
        }
