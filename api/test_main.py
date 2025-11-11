"""
Unit tests for the API service
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import numpy as np

# Mock the model loading before importing main
with patch("builtins.open", MagicMock()):
    with patch("pickle.load", return_value=MagicMock()):
        from main import app

client = TestClient(app)


def test_home_endpoint():
    """Test the home endpoint returns HTML"""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_show_result_endpoint():
    """Test the show-result endpoint"""
    with patch("aiohttp.ClientSession") as mock_session:
        # Mock the async context managers and response
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.json = MagicMock(return_value=[])

        mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = mock_resp

        response = client.get("/show-result")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]


@patch("main.model")
@patch("aiohttp.ClientSession")
def test_predict_endpoint(mock_session, mock_model):
    """Test the prediction endpoint"""
    # Mock the model prediction
    mock_model.predict.return_value = np.array([0])

    # Mock the async HTTP request to DB service
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_resp

    # Test data
    test_data = {
        "sepal_length": 5.1,
        "sepal_width": 3.5,
        "petal_length": 1.4,
        "petal_width": 0.2,
    }

    response = client.post("/predict", data=test_data)
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert mock_model.predict.called


@patch("main.model")
def test_prediction_logic(mock_model):
    """Test that prediction logic works correctly"""
    # Mock different predictions
    test_cases = [(0, "Setosa"), (1, "Versicolor"), (2, "Virginica")]

    for pred_value, expected_class in test_cases:
        mock_model.predict.return_value = np.array([pred_value])

        with patch("aiohttp.ClientSession"):
            response = client.post(
                "/predict",
                data={
                    "sepal_length": 5.0,
                    "sepal_width": 3.0,
                    "petal_length": 1.5,
                    "petal_width": 0.3,
                },
            )

            assert response.status_code == 200
            assert expected_class in response.text


def test_invalid_prediction_data():
    """Test prediction with invalid data"""
    with patch("main.model"):
        # Missing required fields
        response = client.post("/predict", data={"sepal_length": 5.0})
        assert response.status_code == 422  # Unprocessable Entity


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
