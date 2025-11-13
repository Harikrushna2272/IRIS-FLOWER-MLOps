# MLflow Integration Guide

## What is MLflow?

**MLflow** is an open-source platform for managing the ML lifecycle, including:
- **Experiment Tracking**: Log parameters, metrics, and results
- **Model Registry**: Store and version models
- **Model Deployment**: Deploy models to production
- **Reproducibility**: Track all experiments for reproducibility

## Why Use MLflow?

- Track all your predictions and experiments in one place
- Compare different model versions
- Monitor model performance over time
- Easy collaboration with team members
- Keep history of all predictions with their inputs and outputs

---

## How It Works in Our Project

```
User → API Service → Makes Prediction → Logs to MLflow → View in MLflow UI
```

**What Gets Logged:**
- Input features (sepal_length, sepal_width, petal_length, petal_width)
- Prediction result (flower class)
- Inference time (how long prediction took)
- Model version tag

---

## Architecture

```
┌──────────────────┐
│   API Service    │  (Port 8000)
│  Makes Predictions│
└────────┬─────────┘
         │ Logs predictions
         ▼
┌──────────────────┐
│  MLflow Server   │  (Port 5000)
│  Tracks Experiments│
└──────────────────┘
```

---

## Implementation Steps

### 1. Add MLflow Service to Docker Compose

```yaml
services:
  mlflow:
    image: ghcr.io/mlflow/mlflow:v2.9.2
    container_name: mlflow
    ports:
      - "5001:5000"  # External:Internal (5001 on host, 5000 in container)
    volumes:
      - mlflow_data:/mlflow
    command: mlflow server --host 0.0.0.0 --port 5000 --backend-store-uri sqlite:///mlflow/mlflow.db --default-artifact-root /mlflow/artifacts
    restart: unless-stopped

  api:
    # ... other config
    depends_on:
      - mlflow
    environment:
      - MLFLOW_TRACKING_URI=http://mlflow:5000  # Internal network uses port 5000

volumes:
  mlflow_data:
```

### 2. Install MLflow in Your Application

```toml
# pyproject.toml
dependencies = [
    "mlflow>=2.9.2",
]
```

### 3. Configure MLflow in Your Code

```python
import mlflow
import mlflow.sklearn
import os

# Get MLflow tracking URI from environment
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5001")

# Configure MLflow
mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
mlflow.set_experiment("iris-flower-prediction")
```

### 4. Log Predictions to MLflow

```python
import time

@app.post("/predict")
async def predict(sepal_length, sepal_width, petal_length, petal_width):
    start_time = time.time()
    
    # Make prediction
    features = np.array([sepal_length, sepal_width, petal_length, petal_width]).reshape(1, -1)
    pred = model.predict(features)
    flower_name = iris_classes.get(pred[0])
    
    inference_time = time.time() - start_time
    
    # Log to MLflow
    with mlflow.start_run(run_name=f"prediction_{int(time.time())}"):
        # Log input parameters
        mlflow.log_params({
            "sepal_length": sepal_length,
            "sepal_width": sepal_width,
            "petal_length": petal_length,
            "petal_width": petal_width,
        })
        
        # Log metrics
        mlflow.log_metrics({
            "prediction_class": int(pred[0]),
            "inference_time_ms": inference_time * 1000,
        })
        
        # Log tags
        mlflow.set_tag("prediction", flower_name)
        mlflow.set_tag("model_version", "v1.0")
    
    return {"prediction": flower_name}
```

---

## Using MLflow UI

### Access MLflow

Open your browser and go to: **http://localhost:5001**

**Note:** MLflow uses port 5001 instead of 5000 because macOS Control Center uses port 5000 by default.

### View Experiments

1. **Experiments Page**: 
   - Shows all experiments (e.g., "iris-flower-prediction")
   - Click on experiment name to see all runs

2. **Runs Page**:
   - Each prediction creates a new "run"
   - See parameters, metrics, and tags for each run

3. **Compare Runs**:
   - Select multiple runs using checkboxes
   - Click "Compare" button
   - View side-by-side comparison

### Understanding the UI

**Main Sections:**

1. **Experiments** (Left sidebar):
   - List of all experiments
   - Click to view runs

2. **Runs Table** (Center):
   - All runs in selected experiment
   - Columns: Start Time, Duration, Parameters, Metrics
   - Sort and filter runs

3. **Run Details** (Click on a run):
   - **Parameters**: Input features
   - **Metrics**: Prediction class, inference time
   - **Tags**: Prediction result, model version
   - **Artifacts**: Saved models or files (if any)

---

## What Gets Logged

### Parameters (Inputs)
```
sepal_length: 5.1
sepal_width: 3.5
petal_length: 1.4
petal_width: 0.2
```

### Metrics (Measurements)
```
prediction_class: 0 (0=Setosa, 1=Versicolor, 2=Virginica)
inference_time_ms: 2.5 (milliseconds)
```

### Tags (Labels)
```
prediction: Setosa
model_version: v1.0
```

---

## Common Use Cases

### 1. Track All Predictions
Every prediction is logged automatically. You can see:
- When prediction was made
- What inputs were provided
- What output was returned
- How long it took

### 2. Monitor Model Performance
- Check inference times over time
- Identify slow predictions
- Track prediction distribution

### 3. Debug Issues
- Find predictions that took too long
- See exact inputs that caused errors
- Reproduce any prediction

### 4. A/B Testing
```python
# Test two different models
with mlflow.start_run():
    mlflow.set_tag("model_version", "v1.0")
    prediction_v1 = model_v1.predict(features)
    mlflow.log_metric("prediction", prediction_v1)

with mlflow.start_run():
    mlflow.set_tag("model_version", "v2.0")
    prediction_v2 = model_v2.predict(features)
    mlflow.log_metric("prediction", prediction_v2)

# Compare both versions in MLflow UI
```

---

## Advanced Features

### 1. Log the Model Itself

```python
# During training
with mlflow.start_run():
    # Train model
    model.fit(X_train, y_train)
    
    # Log model
    mlflow.sklearn.log_model(model, "iris_model")
    
    # Log training metrics
    mlflow.log_metrics({
        "accuracy": accuracy_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred, average='weighted'),
    })
```

### 2. Register Models

```python
# Register best model
model_uri = f"runs:/{run_id}/iris_model"
mlflow.register_model(model_uri, "IrisClassifier")
```

### 3. Load Models from MLflow

```python
# Load specific version
model = mlflow.sklearn.load_model("models:/IrisClassifier/1")

# Load latest production model
model = mlflow.sklearn.load_model("models:/IrisClassifier/Production")
```

### 4. Search and Filter Runs

```python
# Search for specific runs
runs = mlflow.search_runs(
    experiment_ids=["1"],
    filter_string="metrics.inference_time_ms < 5",
    order_by=["metrics.inference_time_ms DESC"]
)
```

---

## Integration with Prometheus & Grafana

MLflow complements monitoring tools:

| Tool | Purpose |
|------|---------|
| **Prometheus** | Real-time metrics (requests/sec, latency) |
| **Grafana** | Real-time dashboards and alerts |
| **MLflow** | Detailed experiment tracking, model versioning |

**Example Workflow:**
1. Grafana alerts you about high latency
2. Check MLflow to see which predictions are slow
3. Analyze input patterns causing slow predictions
4. Fix and deploy new model version
5. Track improvement in MLflow

---

## API Endpoints

### MLflow Server Endpoints

```bash
# Get all experiments
curl http://localhost:5001/api/2.0/mlflow/experiments/list

# Get runs for an experiment
curl http://localhost:5001/api/2.0/mlflow/runs/search -d '{"experiment_ids": ["1"]}'

# Get run details
curl http://localhost:5001/api/2.0/mlflow/runs/get?run_id={run_id}
```

---

## Troubleshooting

### MLflow UI not loading?
```bash
# Check if MLflow container is running
docker ps | grep mlflow

# Check MLflow logs
docker logs mlflow

# Restart MLflow
docker compose restart mlflow
```

### Predictions not appearing in MLflow?
```bash
# Check API can reach MLflow
docker exec api_service curl http://mlflow:5000/health

# Check environment variable
docker exec api_service env | grep MLFLOW

# Check API logs for MLflow errors
docker logs api_service | grep mlflow
```

### Database locked error?
```bash
# Stop all services
docker compose down

# Remove MLflow volume
docker volume rm trial_mlops_mlflow_data

# Start fresh
docker compose up -d
```

---

## Quick Commands

```bash
# Start all services
docker compose up -d

# View MLflow logs
docker logs -f mlflow

# Access MLflow UI
open http://localhost:5001

# Generate test predictions
for i in {1..10}; do
  curl -X POST "http://localhost:8000/predict" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "sepal_length=5.1&sepal_width=3.5&petal_length=1.4&petal_width=0.2"
  sleep 1
done

# Check MLflow database
docker exec mlflow ls -lh /mlflow/mlflow.db
```

---

## Summary

**MLflow gives you:**
- ✅ Complete history of all predictions
- ✅ Detailed tracking of inputs and outputs  
- ✅ Performance metrics for each prediction
- ✅ Model versioning and registry
- ✅ Easy comparison between experiments
- ✅ Reproducibility of any prediction

**Perfect for:**
- Debugging production issues
- Understanding model behavior
- Comparing model versions
- Regulatory compliance (audit trail)
- Team collaboration

**Access MLflow at:** http://localhost:5001
