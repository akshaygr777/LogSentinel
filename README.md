# LogSentinel

**Intelligent Application Log Anomaly Detection Platform**

LogSentinel is a local application that accepts application/server log files, parses and analyzes them, detects abnormal behavior using statistical techniques, assigns anomaly severity/risk scores, stores historical results, and presents them through an interactive dashboard.

This project was built as a demonstration of software engineering, data processing, statistics, and DevOps practices using Python.

## Features

- **Robust Log Parsing:** Parses and cleans application logs.
- **Statistical Anomaly Detection:** Identifies abnormal response times and frequencies.
- **Risk Scoring:** Assigns interpretable severity (LOW, MEDIUM, HIGH) to anomalies based on deviation and error rates.
- **Interactive Dashboard:** Built with Streamlit and Plotly to visualize metrics, error rates, and endpoints.
- **Data Persistence:** Stores logs and anomalies in a local SQLite database.
- **Export Data:** Allows exporting anomaly results to CSV for further review.
- **Dockerized:** Fully deployable via Docker and Docker Compose.
- **CI/CD:** Automated testing using GitHub Actions.

## Architecture

LogSentinel's architecture follows a clean pipeline:

```mermaid
flowchart TD
    A[Log File / Upload] --> B(Log Parser)
    B --> C(Data Validation / Cleaning)
    C --> D(Structured DataFrame)
    D --> E(Analytics Engine)
    D --> F(Anomaly Detection Engine)
    
    subgraph Anomaly Detection
    F1[Z-Score Detection]
    F2[Rolling-Window]
    F3[Error Spike Detection]
    F4[Request Burst Detection]
    end
    F --> F1 & F2 & F3 & F4
    
    F1 & F2 & F3 & F4 --> G(Risk Scoring Engine)
    G --> H[(SQLite Database)]
    E --> H
    
    H --> I[Streamlit Dashboard]
```

## Technology Stack

- **Python 3.12+**: Core language.
- **Pandas & NumPy**: For efficient data manipulation and statistical calculations.
- **scikit-learn**: Used where complex mathematical utilities are needed.
- **SQLite**: Lightweight, zero-configuration local database to persist historical analysis.
- **Streamlit**: Fast, Python-native framework for building the interactive dashboard.
- **Plotly**: For rich, interactive data visualizations.
- **pytest**: For deterministic unit testing.
- **Docker & Docker Compose**: For containerization and easy deployment without local dependency issues.
- **GitHub Actions**: For Continuous Integration (CI).

## Detection Algorithms

LogSentinel uses multiple statistical techniques to identify suspicious patterns:

- **Z-Score Detection**: Identifies global outliers in response time (e.g., requests taking significantly longer than the overall historical average).
- **Rolling-Window Detection**: Detects localized sudden changes in response time per endpoint, evaluating current requests against recent historical behavior.
- **Error Spike Detection**: Groups logs into time windows and flags periods where error counts significantly exceed the baseline.
- **Request Burst Detection**: Analyzes request frequencies by IP address to find unusual traffic surges (potential abuse or misconfigured clients).
- **Risk Scoring**: Combines the magnitude of deviation, error types, and anomaly characteristics to calculate a transparent 0-100 score, classified into LOW, MEDIUM, and HIGH severity.

## Database Schema

### `logs` table
| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER | Primary Key |
| `timestamp` | DATETIME | Time of the request |
| `level` | TEXT | INFO, WARN, ERROR |
| `method` | TEXT | HTTP Method |
| `endpoint` | TEXT | Request endpoint |
| `status_code` | INTEGER | HTTP Status Code |
| `response_time`| INTEGER | Latency in ms |
| `ip_address` | TEXT | Client IP |

### `anomalies` table
| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER | Primary Key |
| `timestamp` | DATETIME | Time of the anomaly |
| `endpoint` | TEXT | Endpoint involved |
| `ip_address` | TEXT | Client IP involved |
| `anomaly_type` | TEXT | Type of anomaly detected |
| `observed_value`| REAL | Actual value recorded |
| `baseline_value`| REAL | Expected / Historical mean |
| `anomaly_score` | REAL | Statistical deviation |
| `risk_score` | INTEGER | 0-100 severity score |
| `severity` | TEXT | LOW, MEDIUM, HIGH |
| `reason` | TEXT | Human-readable explanation|

## Installation

### Local Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/LogSentinel.git
   cd LogSentinel
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   # Windows:
   .\venv\Scripts\activate
   # Linux/Mac:
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Docker Installation

1. Clone the repository and navigate to the directory.
2. Run Docker Compose:
   ```bash
   docker-compose up --build
   ```
3. The dashboard will be available at `http://localhost:8501`.

## Usage

1. **Start Application (Local)**:
   ```bash
   streamlit run dashboard/app.py
   ```
2. **Generate Sample Data** (if needed):
   Use the sidebar in the dashboard to generate and process a dataset containing simulated anomalies.
3. **Upload Logs**: Use the file uploader in the sidebar to ingest custom application logs.
4. **Analyze Logs**: The main dashboard displays overall metrics, response time trends, error distributions, and endpoint performance.
5. **Inspect Anomalies**: Navigate to the Anomaly Explorer section to filter and review detected issues.
6. **Export Results**: Click the "Download Anomalies as CSV" button to save findings locally.

## Testing

Run the test suite using pytest:
```bash
pytest tests/
```

## Screenshots

<<<<<<< HEAD



=======
<img width="1905" height="841" alt="1s" src="https://github.com/user-attachments/assets/5e8fc4c1-31ab-4973-8ada-b2dfbab8592d" />

<img width="1885" height="855" alt="2s" src="https://github.com/user-attachments/assets/2a2742c8-3bf6-4d9b-a41a-c81ad93a218e" />

<img width="1887" height="851" alt="3s" src="https://github.com/user-attachments/assets/5926b7c4-82d1-4226-ab92-9200724317bd" />

<img width="1915" height="860" alt="4s" src="https://github.com/user-attachments/assets/96434518-7089-4b1a-9ec5-a2f0207e0053" />

<img width="1876" height="852" alt="5s" src="https://github.com/user-attachments/assets/be04a466-8497-4b56-bb3a-6e18736be8ef" />

<img width="1902" height="856" alt="6s" src="https://github.com/user-attachments/assets/124f0789-e0f5-4fc2-8075-b98e7b21fd94" />






>>>>>>> a7b844157a3643ff1bd4480458caeccd97f31309
