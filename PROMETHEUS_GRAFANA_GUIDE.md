# Prometheus & Grafana Monitoring Guide

## What are Prometheus and Grafana?

- **Prometheus**: Collects and stores metrics (numbers) from your application
- **Grafana**: Creates beautiful dashboards to visualize those metrics

## How It Works

```
Your App → Exposes /metrics endpoint → Prometheus scrapes it → Grafana visualizes it
```

---

## Step-by-Step Implementation

### 1. Add Prometheus Client to Your Application

**Install the library:**
```toml
# In pyproject.toml
dependencies = [
    "prometheus-client>=0.21.1"
]
```

**Add metrics to your code:**
```python
from prometheus_client import Counter, Histogram, generate_latest
from fastapi.responses import PlainTextResponse

# Define metrics
REQUEST_COUNT = Counter('api_requests_total', 'Total API requests')
PREDICTION_COUNT = Counter('predictions_total', 'Total predictions made')
PREDICTION_TIME = Histogram('prediction_duration_seconds', 'Prediction time')

# Create /metrics endpoint
@app.get("/metrics", response_class=PlainTextResponse)
async def metrics():
    return generate_latest()

# Use metrics in your endpoints
@app.get("/")
async def home():
    REQUEST_COUNT.inc()  # Increment counter
    return {"message": "Hello"}

@app.post("/predict")
async def predict():
    with PREDICTION_TIME.time():  # Track time
        PREDICTION_COUNT.inc()
        # Your prediction logic here
```

### 2. Add Prometheus & Grafana to Docker Compose

```yaml
version: "3.8"

services:
  # Your existing services (api, db, etc.)

  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - "--config.file=/etc/prometheus/prometheus.yml"
      - "--storage.tsdb.path=/prometheus"
    restart: unless-stopped

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana/datasources.yml:/etc/grafana/provisioning/datasources/datasources.yml
      - ./grafana/dashboards/dashboard.yml:/etc/grafana/provisioning/dashboards/dashboard.yml
      - ./grafana/dashboards/iris-mlops-dashboard.json:/var/lib/grafana/dashboards/iris-mlops-dashboard.json
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
      - GF_SECURITY_ADMIN_USER=admin
    depends_on:
      - prometheus
    restart: unless-stopped

volumes:
  prometheus_data:
  grafana_data:
```

### 3. Configure Prometheus

Create `prometheus/prometheus.yml`:

```yaml
global:
  scrape_interval: 15s  # How often to collect metrics

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'api_service'
    static_configs:
      - targets: ['api_service:8000']  # Your service name and port

  - job_name: 'db_service'
    static_configs:
      - targets: ['db_service:8001']
```

### 4. Configure Grafana Datasource

Create `grafana/datasources.yml`:

```yaml
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    uid: prometheus
    isDefault: true
    editable: true
```

### 5. Configure Dashboard Provisioning

Create `grafana/dashboards/dashboard.yml`:

```yaml
apiVersion: 1

providers:
  - name: 'IRIS MLOps'
    orgId: 1
    folder: ''
    type: file
    disableDeletion: false
    updateIntervalSeconds: 10
    allowUiUpdates: true
    options:
      path: /var/lib/grafana/dashboards
```

### 6. Create Dashboard JSON

Create `grafana/dashboards/your-dashboard.json`:

```json
{
  "title": "My App Monitoring",
  "panels": [
    {
      "id": 1,
      "type": "timeseries",
      "title": "Total API Requests",
      "targets": [
        {
          "expr": "api_requests_total",
          "refId": "A"
        }
      ],
      "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0}
    }
  ],
  "refresh": "5s",
  "uid": "my-dashboard"
}
```

---

## Common Metric Types

### Counter
Counts things that only go up (requests, errors, etc.)
```python
REQUEST_COUNT = Counter('requests_total', 'Total requests')
REQUEST_COUNT.inc()  # Increment by 1
REQUEST_COUNT.inc(5)  # Increment by 5
```

### Gauge
Measures current value (CPU usage, memory, queue size)
```python
QUEUE_SIZE = Gauge('queue_size', 'Current queue size')
QUEUE_SIZE.set(42)  # Set to specific value
QUEUE_SIZE.inc()    # Increase by 1
QUEUE_SIZE.dec()    # Decrease by 1
```

### Histogram
Measures distributions (response times, request sizes)
```python
RESPONSE_TIME = Histogram('response_seconds', 'Response time')
with RESPONSE_TIME.time():
    # Code to measure
    do_something()
```

---

## Useful Prometheus Queries (PromQL)

```promql
# Current value
api_requests_total

# Rate per second
rate(api_requests_total[1m])

# Average response time
rate(response_time_sum[1m]) / rate(response_time_count[1m])

# Sum across all instances
sum(api_requests_total)

# Filter by label
api_requests_total{job="api_service"}
```

---

## Accessing the Tools

1. **Prometheus**: http://localhost:9090
   - View raw metrics
   - Test queries
   - Check targets status

2. **Grafana**: http://localhost:3000
   - Login: admin/admin
   - Create/view dashboards
   - Set up alerts

---

## Testing Your Setup

**1. Check metrics endpoint:**
```bash
curl http://localhost:8000/metrics
```

**2. Check Prometheus targets:**
- Go to http://localhost:9090/targets
- All targets should show "UP"

**3. Test query in Prometheus:**
- Go to http://localhost:9090/graph
- Enter: `api_requests_total`
- Click "Execute"

**4. View in Grafana:**
- Go to http://localhost:3000
- Login: admin/admin
- Navigate to your dashboard

---

## Troubleshooting

### No data in Grafana?
1. Check if Prometheus is scraping: http://localhost:9090/targets
2. Verify datasource connection in Grafana: Configuration → Data sources
3. Test query in Prometheus first

### Metrics endpoint returns 404?
- Make sure you added the `/metrics` endpoint to your code
- Rebuild Docker images: `docker compose build --no-cache`

### Grafana shows "data source not found"?
- Stop everything: `docker compose down -v`
- Start fresh: `docker compose up -d`
- The `-v` flag removes old volumes

---

## Quick Start Commands

```bash
# Stop everything and remove volumes
docker compose down -v

# Start fresh
docker compose up -d

# Generate test traffic
for i in {1..50}; do
  curl http://localhost:8000/
  sleep 1
done

# Check metrics
curl http://localhost:8000/metrics

# View logs
docker logs prometheus
docker logs grafana
```

---

## Summary

1. **Add prometheus-client** to your app dependencies
2. **Create metrics** (Counter, Gauge, Histogram) in your code
3. **Expose /metrics endpoint** that returns `generate_latest()`
4. **Configure Prometheus** to scrape your service
5. **Configure Grafana** to connect to Prometheus
6. **Create dashboards** to visualize your metrics

That's it! You now have monitoring for your application.
