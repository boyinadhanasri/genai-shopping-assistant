"""
Automated live verification of GenAI Shopping Assistant API
Tests live HTTP endpoints on http://127.0.0.1:8000
"""

import sys
import json
import urllib.request
import urllib.parse
from typing import Any, Dict

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_URL = "http://127.0.0.1:8000"


def make_request(method: str, path: str, payload: Dict[str, Any] = None) -> Dict[str, Any]:
    url = f"{BASE_URL}{path}"
    headers = {"User-Agent": "LiveSearchVerifier/1.0", "Content-Type": "application/json"}
    data = json.dumps(payload).encode("utf-8") if payload else None

    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=30) as resp:
        body = resp.read().decode("utf-8")
        return {"status": resp.status, "data": json.loads(body)}


def main():
    print("=" * 65)
    print("LIVE HTTP ENDPOINT VERIFICATION (http://127.0.0.1:8000)")
    print("=" * 65)

    endpoints = [
        ("GET", "/", None, "Health Check"),
        ("GET", "/api/categories", None, "Categories Taxonomy"),
        ("GET", "/api/products?limit=3", None, "Paginated Products"),
        ("GET", "/api/products/trending?limit=3", None, "Trending Items"),
        ("GET", "/api/search?q=laptop&top_k=2", None, "Hybrid Search"),
        ("POST", "/api/chat", {"message": "Need a phone under 20000", "category": "Mobiles"}, "Chat Assistant Turn 1"),
        ("POST", "/api/chat", {"message": "Only Samsung", "category": "Mobiles"}, "Chat Assistant Turn 2 (Follow-up)"),
        ("POST", "/api/compare", {"product_ids": ["FKP0000010", "FKP0000023"], "category": "Electronics"}, "Side-by-Side Comparison"),
        ("GET", "/api/analytics", None, "Analytics Summary"),
    ]

    all_passed = True
    for method, path, payload, desc in endpoints:
        try:
            res = make_request(method, path, payload)
            status = res["status"]
            preview = str(res["data"])[:60].replace("\n", " ")
            print(f"[{status}] {method:5s} {path:35s} | {desc:25s} | {preview}")
        except Exception as e:
            print(f"[FAIL] {method:5s} {path:35s} | {desc:25s} | Error: {e}")
            all_passed = False

    print("=" * 65)
    if all_passed:
        print("ALL LIVE HTTP ENDPOINTS OPERATING NORMALLY!")
    else:
        print("SOME ENDPOINTS FAILED")
    print("=" * 65)


if __name__ == "__main__":
    main()
