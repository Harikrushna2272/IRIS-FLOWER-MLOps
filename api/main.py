from imp import reload
import os
import pickle

from pydantic.v1.tools import T

import aiohttp
import numpy as np
from dotenv import load_dotenv
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.templating import Jinja2Templates
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

iris_classes = {0: "Setosa", 1: "Versicolor", 2: "Virginica"}

# Prometheus metrics
REQUEST_COUNT = Counter("api_requests_total", "Total API requests")
PREDICTION_COUNT = Counter("predictions_total", "Total predictions made")
PREDICTION_TIME = Histogram("prediction_duration_seconds", "Prediction processing time")

load_dotenv()

DB_SERVICE_URL = os.getenv("DATABASE_SERVICE_URL", "http://localhost:8001")

app = FastAPI(reload=True)
templates = Jinja2Templates(directory="templates")

model = None
with open("model.pkl", "rb") as f:
    model = pickle.load(f)

iris_classes = {0: "Setosa", 1: "Versicolor", 2: "Virginica"}


@app.get("/metrics", response_class=PlainTextResponse)
async def metrics():
    return generate_latest()


@app.get("/", response_class=HTMLResponse)
async def home(request: Request, prediction: str = None):
    REQUEST_COUNT.inc()
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "prediction": prediction,
            "form_data": {
                "sepal_length": "",
                "sepal_width": "",
                "petal_length": "",
                "petal_width": "",
            },
        },
    )


@app.get("/show-result", response_class=HTMLResponse)
async def show_result(request: Request):
    records = []
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{DB_SERVICE_URL}/prediction") as resp:
                if resp.status == 200:
                    records = await resp.json()
                else:
                    print(f"Failed to fetch predictions from DB: {resp.status}")
    except Exception as e:
        print(f"Error connecting to DB service: {e}")

    return templates.TemplateResponse(
        "show-result.html", {"request": request, "records": records}
    )


@app.post("/predict", response_class=HTMLResponse)
async def predict(
    request: Request,
    sepal_length: float = Form(...),
    sepal_width: float = Form(...),
    petal_length: float = Form(...),
    petal_width: float = Form(...),
):
    with PREDICTION_TIME.time():
        PREDICTION_COUNT.inc()
        features = np.array(
            [sepal_length, sepal_width, petal_length, petal_width]
        ).reshape(1, -1)
        pred = model.predict(features)
        ans = pred[0]
        flower_name = iris_classes.get(ans, str(ans))

    # Send prediction to DB microservice
    async with aiohttp.ClientSession() as session:
        payload = {
            "sepal_length": sepal_length,
            "sepal_width": sepal_width,
            "petal_length": petal_length,
            "petal_width": petal_width,
            "predicted_class": flower_name,
        }
        try:
            async with session.post(
                f"{DB_SERVICE_URL}/prediction", json=payload
            ) as resp:
                if resp.status != 200:
                    print(f"Failed to save prediction to DB: {resp.status}")
        except Exception as e:
            print(f"Error connecting to DB service: {e}")

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "prediction": flower_name,
            "form_data": {
                "sepal_length": sepal_length,
                "sepal_width": sepal_width,
                "petal_length": petal_length,
                "petal_width": petal_width,
            },
        },
    )
