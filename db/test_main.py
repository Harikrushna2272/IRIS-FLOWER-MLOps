"""
Unit tests for the DB service
"""

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_root_endpoint():
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello from DB"}


def test_health_endpoint():
    """Test the health endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_prediction():
    """Test creating a prediction"""
    test_prediction = {
        "sepal_length": 5.1,
        "sepal_width": 3.5,
        "petal_length": 1.4,
        "petal_width": 0.2,
        "predicted_class": "Setosa",
    }

    response = client.post("/prediction", json=test_prediction)
    assert response.status_code == 200

    data = response.json()
    assert "id" in data
    assert data["sepal_length"] == test_prediction["sepal_length"]
    assert data["sepal_width"] == test_prediction["sepal_width"]
    assert data["petal_length"] == test_prediction["petal_length"]
    assert data["petal_width"] == test_prediction["petal_width"]
    assert data["predicted_class"] == test_prediction["predicted_class"]


def test_get_all_predictions():
    """Test getting all predictions"""
    response = client.get("/prediction")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_prediction_validation():
    """Test prediction creation with invalid data"""
    # Missing required field
    invalid_prediction = {
        "sepal_length": 5.1,
        "sepal_width": 3.5,
        "petal_length": 1.4,
        # missing petal_width and predicted_class
    }

    response = client.post("/prediction", json=invalid_prediction)
    assert response.status_code == 422  # Unprocessable Entity


def test_multiple_predictions():
    """Test creating multiple predictions"""
    predictions = [
        {
            "sepal_length": 5.1,
            "sepal_width": 3.5,
            "petal_length": 1.4,
            "petal_width": 0.2,
            "predicted_class": "Setosa",
        },
        {
            "sepal_length": 6.7,
            "sepal_width": 3.0,
            "petal_length": 5.2,
            "petal_width": 2.3,
            "predicted_class": "Virginica",
        },
    ]

    for pred in predictions:
        response = client.post("/prediction", json=pred)
        assert response.status_code == 200

    # Verify all predictions are stored
    response = client.get("/prediction")
    assert response.status_code == 200
    all_predictions = response.json()
    assert len(all_predictions) >= 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
