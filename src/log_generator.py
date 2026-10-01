import random
import datetime
import os

def generate_logs(num_logs=5000, output_file="data/sample_logs/sample.log", seed=42):
    random.seed(seed)
    
    endpoints = ["/api/users", "/api/payment", "/api/login", "/api/products", "/api/orders"]
    methods = {"/api/users": "GET", "/api/payment": "POST", "/api/login": "POST", "/api/products": "GET", "/api/orders": "POST"}
    ips = [f"192.168.1.{i}" for i in range(1, 21)]
    
    # Start time
    current_time = datetime.datetime(2026, 9, 30, 8, 0, 0)
    
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    logs = []
    
    burst_ip = "10.0.0.99"
    burst_start = int(num_logs * 0.6)
    burst_end = burst_start + 100
    
    spike_start = int(num_logs * 0.4)
    spike_end = spike_start + 50
    
    latency_spike_start = int(num_logs * 0.2)
    latency_spike_end = latency_spike_start + 20
    
    gradual_slow_endpoint = "/api/products"
    
    for i in range(num_logs):
        # Time increment (average 2 seconds between requests)
        current_time += datetime.timedelta(seconds=random.uniform(0.1, 3.5))
        
        # Default normal behavior
        endpoint = random.choice(endpoints)
        method = methods[endpoint]
        ip = random.choice(ips)
        status_code = random.choices([200, 201, 400, 401, 404, 500], weights=[80, 5, 5, 2, 6, 2], k=1)[0]
        response_time = int(random.gauss(150, 30))
        level = "INFO"
        
        # Scenario A: Sudden latency spike for a short period (any endpoint)
        if latency_spike_start <= i <= latency_spike_end:
            if random.random() < 0.8:
                response_time = int(random.gauss(1500, 200))
                
        # Scenario B: Sudden 500-error spike
        if spike_start <= i <= spike_end:
            if random.random() < 0.7:
                status_code = 500
                level = "ERROR"
        
        # Scenario C: Request burst from one IP
        if burst_start <= i <= burst_end:
            ip = burst_ip
            # Very fast requests
            current_time += datetime.timedelta(milliseconds=random.uniform(10, 50))
            
        # Scenario D: Gradual slowdown on specific endpoint
        if endpoint == gradual_slow_endpoint:
            progress = i / num_logs
            # base response time + gradual increase
            response_time = int(random.gauss(150 + (progress * 800), 50))
            
        # Fix negative response times
        response_time = max(10, response_time)
        
        # Set ERROR level for 5xx
        if status_code >= 500:
            level = "ERROR"
        elif status_code >= 400:
            level = "WARN"
            
        log_line = f"{current_time.strftime('%Y-%m-%d %H:%M:%S')} | {level} | {method} | {endpoint} | {status_code} | {response_time} | {ip}\n"
        logs.append(log_line)
        
    with open(output_file, "w") as f:
        f.writelines(logs)
        
    print(f"Generated {num_logs} logs at {output_file}")

if __name__ == "__main__":
    generate_logs(5000)
