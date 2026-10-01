FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ src/
COPY dashboard/ dashboard/
COPY tests/ tests/

# Create database and data directories
RUN mkdir -p database
RUN mkdir -p data/sample_logs

# Generate sample logs during build (optional, but good for demo)
RUN python -c "from src.log_generator import generate_logs; generate_logs(5000, 'data/sample_logs/generated.log')"

# Expose Streamlit port
EXPOSE 8501

# Run the application
CMD ["streamlit", "run", "dashboard/app.py", "--server.address=0.0.0.0"]
