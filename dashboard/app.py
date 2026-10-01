import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import sys

# Add parent directory to path to import src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.parser import LogParser
from src.analytics import LogAnalytics
from src.anomaly_detector import AnomalyDetector
from src.database import DatabaseManager
from src.log_generator import generate_logs
from src.config import DB_PATH

# Page config
st.set_page_config(page_title="LogSentinel", page_icon="🛡️", layout="wide")

# Initialize database
db = DatabaseManager(DB_PATH)

def load_data():
    """Load data from database."""
    logs_df = db.get_all_logs()
    anomalies_df = db.get_all_anomalies()
    return logs_df, anomalies_df

def process_log_file(filepath):
    """Process a log file and store results in DB."""
    with st.spinner(f"Parsing {os.path.basename(filepath)}..."):
        parser = LogParser()
        df = parser.parse_file(filepath)
        
    if df.empty:
        st.error("No valid logs found in the file.")
        return False
        
    with st.spinner("Detecting anomalies..."):
        detector = AnomalyDetector(df)
        anomalies = detector.detect_all()
        
    with st.spinner("Storing results..."):
        db.insert_logs(df)
        db.insert_anomalies(anomalies)
        
    st.success(f"Successfully processed {len(df)} logs and detected {len(anomalies)} anomalies.")
    return True

# Sidebar
st.sidebar.title("🛡️ LogSentinel")
st.sidebar.markdown("Intelligent Application Log Anomaly Detection")

# File Upload / Generation
st.sidebar.header("Data Source")
uploaded_file = st.sidebar.file_uploader("Upload Log File", type=["log", "txt"])

if st.sidebar.button("Process Uploaded File"):
    if uploaded_file is not None:
        # Save temp file
        temp_path = os.path.join("data", "temp_upload.log")
        os.makedirs("data", exist_ok=True)
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        if process_log_file(temp_path):
            st.rerun()
    else:
        st.sidebar.warning("Please upload a file first.")

st.sidebar.markdown("---")
st.sidebar.header("Sample Data")
num_samples = st.sidebar.selectbox("Number of sample logs", [1000, 5000, 10000], index=1)
if st.sidebar.button("Generate & Process Sample Data"):
    db.clear_database() # Clear old data for demo
    sample_path = "data/sample_logs/generated.log"
    with st.spinner("Generating sample logs..."):
        generate_logs(num_samples, sample_path)
    if process_log_file(sample_path):
        st.rerun()
        
if st.sidebar.button("Clear Database"):
    db.clear_database()
    st.sidebar.success("Database cleared.")
    st.rerun()

# Main Content
st.title("System Dashboard")

logs_df, anomalies_df = load_data()

if logs_df.empty:
    st.info("No data available. Please upload a log file or generate sample data from the sidebar.")
    st.stop()

# Filters
st.sidebar.markdown("---")
st.sidebar.header("Filters")

# Date range filter
min_date = logs_df['timestamp'].min().date()
max_date = logs_df['timestamp'].max().date()
date_range = st.sidebar.date_input("Date Range", [min_date, max_date], min_value=min_date, max_value=max_date)

endpoints = ["All"] + list(logs_df['endpoint'].unique())
selected_endpoint = st.sidebar.selectbox("Endpoint", endpoints)

# Apply filters
filtered_logs = logs_df.copy()
filtered_anomalies = anomalies_df.copy() if not anomalies_df.empty else pd.DataFrame()

if len(date_range) == 2:
    start_dt = pd.to_datetime(date_range[0])
    # Add 1 day minus 1 second to end_dt to include the whole day
    end_dt = pd.to_datetime(date_range[1]) + pd.Timedelta(days=1, seconds=-1)
    
    filtered_logs = filtered_logs[(filtered_logs['timestamp'] >= start_dt) & (filtered_logs['timestamp'] <= end_dt)]
    if not filtered_anomalies.empty:
        filtered_anomalies = filtered_anomalies[(filtered_anomalies['timestamp'] >= start_dt) & (filtered_anomalies['timestamp'] <= end_dt)]

if selected_endpoint != "All":
    filtered_logs = filtered_logs[filtered_logs['endpoint'] == selected_endpoint]
    if not filtered_anomalies.empty:
        filtered_anomalies = filtered_anomalies[(filtered_anomalies['endpoint'] == selected_endpoint) | (filtered_anomalies['endpoint'] == 'MULTIPLE')]


# Analytics processing
analytics = LogAnalytics(filtered_logs)
metrics = analytics.get_overall_metrics()

# 1. Overview Section
st.header("Overview")
col1, col2, col3, col4, col5, col6 = st.columns(6)
col1.metric("Total Requests", f"{metrics['total_requests']:,}")
col2.metric("Total Errors", f"{metrics['total_errors']:,}")
col3.metric("Error Rate", f"{metrics['error_rate']:.2f}%")
col4.metric("Avg Response Time", f"{metrics['avg_response_time']:.0f} ms")

total_anomalies = len(filtered_anomalies) if not filtered_anomalies.empty else 0
high_severity = len(filtered_anomalies[filtered_anomalies['severity'] == 'HIGH']) if not filtered_anomalies.empty else 0

col5.metric("Total Anomalies", total_anomalies)
col6.metric("High Severity", high_severity)

st.markdown("---")

# 2. Response Time Analytics
st.header("Response Time Analytics")
if not filtered_logs.empty:
    fig_rt = px.scatter(
        filtered_logs, 
        x="timestamp", 
        y="response_time", 
        color="endpoint",
        title="Response Time Over Time",
        labels={"timestamp": "Time", "response_time": "Response Time (ms)"},
        opacity=0.6
    )
    
    # Overlay anomalies if any
    if not filtered_anomalies.empty:
        rt_anomalies = filtered_anomalies[filtered_anomalies['anomaly_type'].isin(['Z_SCORE_ANOMALY', 'ROLLING_WINDOW_ANOMALY'])]
        if not rt_anomalies.empty:
            fig_rt.add_trace(go.Scatter(
                x=rt_anomalies['timestamp'],
                y=rt_anomalies['observed_value'],
                mode='markers',
                marker=dict(color='red', size=10, symbol='x'),
                name='Anomalies'
            ))
            
    st.plotly_chart(fig_rt, use_container_width=True)

st.markdown("---")

# 3. Error Analytics
st.header("Error Analytics")
col_err1, col_err2 = st.columns(2)

with col_err1:
    # Errors over time (grouped by minute)
    error_logs = filtered_logs[filtered_logs['status_code'] >= 400]
    if not error_logs.empty:
        errors_over_time = error_logs.set_index('timestamp').resample('1min').size().reset_index(name='count')
        fig_err_time = px.line(errors_over_time, x='timestamp', y='count', title="Errors Over Time (per minute)")
        st.plotly_chart(fig_err_time, use_container_width=True)
    else:
        st.info("No errors found in this time range.")

with col_err2:
    status_dist = analytics.get_status_code_distribution()
    dist_df = pd.DataFrame(list(status_dist.items()), columns=['Status Class', 'Count'])
    fig_status = px.pie(dist_df, values='Count', names='Status Class', title="Status Code Distribution", hole=0.4)
    st.plotly_chart(fig_status, use_container_width=True)

st.markdown("---")

# 4. Endpoint Analysis
st.header("Endpoint Analysis")
endpoint_metrics = analytics.get_endpoint_metrics()
if not endpoint_metrics.empty:
    st.dataframe(
        endpoint_metrics.style.format({
            "avg_response_time": "{:.2f}",
            "error_rate": "{:.2f}%"
        }),
        use_container_width=True
    )
    
    fig_ep_req = px.bar(endpoint_metrics, x='endpoint', y='request_count', title="Requests by Endpoint")
    st.plotly_chart(fig_ep_req, use_container_width=True)

st.markdown("---")

# 5. Anomaly Explorer
st.header("Anomaly Explorer")
if not filtered_anomalies.empty:
    # Distribution chart
    col_anm1, col_anm2 = st.columns(2)
    with col_anm1:
        fig_anm_type = px.pie(filtered_anomalies, names='anomaly_type', title="Anomalies by Type", hole=0.3)
        st.plotly_chart(fig_anm_type, use_container_width=True)
    with col_anm2:
        # Sort so severity has a consistent color mapping
        severity_colors = {'HIGH': 'red', 'MEDIUM': 'orange', 'LOW': 'yellow'}
        fig_sev = px.pie(filtered_anomalies, names='severity', title="Severity Distribution", hole=0.3, 
                         color='severity', color_discrete_map=severity_colors)
        st.plotly_chart(fig_sev, use_container_width=True)
        
    st.subheader("Anomaly Records")
    
    # Optional filtering for the anomalies table
    sev_filter = st.multiselect("Filter by Severity", ["HIGH", "MEDIUM", "LOW"], default=["HIGH", "MEDIUM", "LOW"])
    table_anomalies = filtered_anomalies[filtered_anomalies['severity'].isin(sev_filter)]
    
    display_cols = ['timestamp', 'endpoint', 'ip_address', 'anomaly_type', 'observed_value', 'risk_score', 'severity', 'reason']
    st.dataframe(table_anomalies[display_cols].sort_values('timestamp', ascending=False), use_container_width=True)
    
    # Export CSV
    csv = table_anomalies.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Anomalies as CSV",
        data=csv,
        file_name='logsentinel_anomalies.csv',
        mime='text/csv',
    )
else:
    st.success("No anomalies detected in the current data.")
