"""
Tests for GET /api/search endpoint using FastAPI TestClient
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_search_book_endpoint():
    response = client.get("/api/search?q=book")
    assert response.status_code == 200

    data = response.json()
    assert "products" in data
    products = data["products"]
    assert len(products) > 0

    # Ensure top result contains book category or book related info
    top_item = products[0]
    prod = top_item.get("product", top_item)
    assert "title" in prod
    assert "category" in prod
    assert top_item.get("score") is not None


def test_search_laptop_endpoint():
    response = client.get("/api/search?q=laptop%20under%2060000")
    assert response.status_code == 200

    data = response.json()
    assert "products" in data
    products = data["products"]
    assert len(products) > 0

    # Top results should be electronics
    top_item = products[0]
    prod = top_item.get("product", top_item)
    assert prod.get("category") == "Electronics"
    assert float(prod.get("price", 0)) <= 60000.0


def test_search_empty_query():
    response = client.get("/api/search?q=")
    assert response.status_code == 200
    data = response.json()
    assert data["products"] == []
