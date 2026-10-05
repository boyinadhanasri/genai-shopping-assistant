"""
Tests for GET /api/search endpoint using FastAPI TestClient
"""

import unittest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


class TestSearchEndpoint(unittest.TestCase):
    def test_search_book_endpoint(self):
        response = client.get("/api/search?q=book")
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn("products", data)
        products = data["products"]
        self.assertGreater(len(products), 0)

        # Ensure top result contains book category or book related info
        top_item = products[0]
        prod = top_item.get("product", top_item)
        self.assertIn("title", prod)
        self.assertIn("category", prod)
        self.assertIsNotNone(top_item.get("score"))

    def test_search_laptop_endpoint(self):
        response = client.get("/api/search?q=laptop%20under%2060000")
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn("products", data)
        products = data["products"]
        self.assertGreater(len(products), 0)

        # Top results should be electronics
        top_item = products[0]
        prod = top_item.get("product", top_item)
        self.assertIn(prod.get("category"), ["Electronics", "Laptops"])
        self.assertLessEqual(float(prod.get("price", 0)), 60000.0)

    def test_search_empty_query(self):
        response = client.get("/api/search?q=")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["products"], [])


if __name__ == "__main__":
    unittest.main()
