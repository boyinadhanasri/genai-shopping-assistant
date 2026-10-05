"""
Verification test suite for Search Engine Budget Filtering

Tests:
1. Laptop under 25000 -> 0 results, success=False, smart suggestion & alternatives
2. Phone under 15000 -> 0 results, success=False, smart suggestion & alternatives
3. Jeans under 1000 -> matching results, ALL price <= 1000
4. Earbuds under 2000 -> matching results, ALL price <= 2000
5. /api/chat, /api/query, and /api/search API endpoint tests
"""

import sys
from pathlib import Path
from fastapi.testclient import TestClient

# Ensure backend can be imported
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.search_engine import search_products, find_cheapest_product, get_budget_fallback
from backend.main import app
from backend.auth.jwt_handler import create_access_token
from backend.database.db import get_user_by_email, create_user

test_user = get_user_by_email("test_budget@example.com")
if not test_user:
    test_user = create_user("Test Budget User", "test_budget@example.com", "hash", is_verified=1)
auth_headers = {"Authorization": f"Bearer {create_access_token(test_user['id'], test_user['email'])}"}

client = TestClient(app)


def test_laptop_under_25000():
    print("\n--- 1. Testing 'Laptop under 25000' ---")
    res = search_products("Laptop under 25000")
    print(f"Success: {res.success}")
    print(f"Products returned count: {len(res)}")
    print(f"Message: {res.message}")
    print(f"Suggestion: {res.suggestion}")
    print(f"Alternatives: {res.alternatives}")

    # Assertions
    assert res.success is False, f"Expected success=False, got {res.success}"
    assert len(res) == 0, f"Expected 0 products, got {len(res)}"
    assert "No laptops found under ₹25,000" in res.message or "No laptop found under ₹25,000" in res.message
    assert any(p in res.suggestion for p in ["34,990", "36,990"])
    assert len(res.alternatives) >= 2
    print("✅ 'Laptop under 25000' PASSED!")


def test_phone_under_15000():
    print("\n--- 2. Testing 'Phone under 15000' ---")
    res = search_products("Phone under 15000")
    print(f"Success: {res.success}")
    print(f"Products returned count: {len(res)}")
    print(f"Message: {res.message}")
    print(f"Suggestion: {res.suggestion}")
    print(f"Alternatives: {res.alternatives}")

    # Assertions
    assert res.success is False, f"Expected success=False, got {res.success}"
    assert len(res) == 0, f"Expected 0 products, got {len(res)}"
    assert "No smartphones found under ₹15,000" in res.message or "No phone found under ₹15,000" in res.message
    assert any(p in res.suggestion for p in ["16,499", "31,999", "34,990"])
    assert len(res.alternatives) >= 2
    print("✅ 'Phone under 15000' PASSED!")


def test_jeans_under_1000():
    print("\n--- 3. Testing 'Jeans under 1000' ---")
    res = search_products("Jeans under 1000")
    print(f"Success: {res.success}")
    print(f"Products returned count: {len(res)}")
    for idx, p in enumerate(res, 1):
        print(f"  {idx}. {p['brand']} - {p['title'][:40]} | ₹{p['price']}")

    # Assertions
    assert res.success is True, f"Expected success=True, got {res.success}"
    assert len(res) > 0, "Expected at least 1 product within budget"
    # STRICT BUDGET RULE: No product may exceed 1000
    for p in res:
        assert p["price"] <= 1000.0, f"Product {p['title']} has price {p['price']} > 1000!"
    print("✅ 'Jeans under 1000' PASSED! (All products <= ₹1,000)")


def test_earbuds_under_2000():
    print("\n--- 4. Testing 'Earbuds under 2000' ---")
    res = search_products("Earbuds under 2000")
    print(f"Success: {res.success}")
    print(f"Products returned count: {len(res)}")
    for idx, p in enumerate(res, 1):
        print(f"  {idx}. {p['brand']} - {p['title'][:40]} | ₹{p['price']}")

    # Assertions
    assert res.success is True, f"Expected success=True, got {res.success}"
    assert len(res) > 0, "Expected at least 1 product within budget"
    # STRICT BUDGET RULE: No product may exceed 2000
    for p in res:
        assert p["price"] <= 2000.0, f"Product {p['title']} has price {p['price']} > 2000!"
    print("✅ 'Earbuds under 2000' PASSED! (All products <= ₹2,000)")


def test_chat_endpoint_budget_fallback():
    print("\n--- 5. Testing POST /api/chat with 'Best laptop under 25000' ---")
    response = client.post("/api/chat", json={"message": "Best laptop under 25000"}, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    print("Chat Response JSON:")
    print(f"  success: {data.get('success')}")
    print(f"  message: {data.get('message')}")
    print(f"  suggestion: {data.get('suggestion')}")
    print(f"  alternatives: {data.get('alternatives')}")
    print(f"  products count: {len(data.get('products', []))}")

    assert data["success"] is False
    assert len(data["products"]) == 0
    assert "No laptops found under ₹25,000" in data["message"] or "No laptop found under ₹25,000" in data["message"]
    assert any(p in data["suggestion"] for p in ["34,990", "36,990"])
    assert len(data["alternatives"]) >= 2
    print("✅ POST /api/chat fallback PASSED!")


def test_query_endpoint_budget_filtering():
    print("\n--- 6. Testing POST /api/query with 'Earbuds under 2000' ---")
    response = client.post("/api/query", json={"query": "Earbuds under 2000"}, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    print(f"  success: {data.get('success')}")
    print(f"  products count: {len(data.get('products', []))}")
    assert data["success"] is True
    assert len(data["products"]) > 0
    for p in data["products"]:
        assert p["price"] <= 2000.0
    print("✅ POST /api/query budget filtering PASSED!")


def test_search_endpoint_budget_fallback():
    print("\n--- 7. Testing GET /api/search with 'laptop under 25000' ---")
    response = client.get("/api/search?q=laptop%20under%2025000")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False
    assert len(data["products"]) == 0
    assert any(p in data["suggestion"] for p in ["34,990", "36,990"])
    print("✅ GET /api/search fallback PASSED!")



if __name__ == "__main__":
    print("==================================================================")
    print("RUNNING BUDGET FILTERING VERIFICATION SUITE")
    print("==================================================================")
    test_laptop_under_25000()
    test_phone_under_15000()
    test_jeans_under_1000()
    test_earbuds_under_2000()
    test_chat_endpoint_budget_fallback()
    test_query_endpoint_budget_filtering()
    test_search_endpoint_budget_fallback()
    print("\n==================================================================")
    print("🎉 ALL 7 BUDGET FILTERING TESTS PASSED PERFECTLY!")
    print("==================================================================")
