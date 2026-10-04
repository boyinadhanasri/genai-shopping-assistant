"""
End-to-End Verification of Required Queries on Real Master Catalog
Tests:
1. "jeans under 1500"
2. "laptops under 70000"
3. "wireless earbuds"
4. "books on python"
"""

import sys
import json
import urllib.request
from pathlib import Path

# Setup paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.search_engine import search_products
from backend.ai.query_understanding import understand_query

QUERIES = [
    {
        "query": "jeans under 1500",
        "expected_category": "Fashion",
        "expected_max_budget": 1500.0,
    },
    {
        "query": "laptops under 70000",
        "expected_category": "Electronics",
        "expected_max_budget": 70000.0,
    },
    {
        "query": "wireless earbuds",
        "expected_category": "Electronics",
        "expected_max_budget": None,
    },
    {
        "query": "books on python",
        "expected_category": "Books",
        "expected_max_budget": None,
    },
]


def test_via_python_engine():
    print("=" * 70)
    print("PART 1: TESTING DIRECT SEARCH ENGINE & QUERY UNDERSTANDING")
    print("=" * 70)

    all_passed = True

    for test in QUERIES:
        q = test["query"]
        print(f"\n[QUERY]: '{q}'")
        
        parsed = understand_query(q)
        print(f"  -> Extracted Category:    {parsed.get('category')} (Expected: {test['expected_category']})")
        print(f"  -> Extracted Subcategory: {parsed.get('subcategory')}")
        print(f"  -> Extracted Budget:      {parsed.get('budget')} (Expected: {test['expected_max_budget']})")

        # Category check
        if parsed.get("category") != test["expected_category"]:
            print(f"  ❌ FAILED: Category mismatch! Got {parsed.get('category')}, expected {test['expected_category']}")
            all_passed = False

        # Budget check
        if test["expected_max_budget"] is not None and parsed.get("budget") != test["expected_max_budget"]:
            print(f"  ❌ FAILED: Budget mismatch! Got {parsed.get('budget')}, expected {test['expected_max_budget']}")
            all_passed = False

        results = search_products(
            query=q,
            top_k=10,
            category=parsed.get("category"),
            budget=parsed.get("budget"),
            subcategory=parsed.get("subcategory")
        )

        print(f"  -> Results Found: {len(results)}")
        if not results:
            print("  ❌ FAILED: No results found!")
            all_passed = False
            continue

        for idx, item in enumerate(results[:5], start=1):
            prod = item.get("product", item)
            score = item.get("score", 0.0)
            print(f"     {idx}. [{score:.4f}] {prod['brand']} - {prod['title'][:50]}... | ₹{prod['price']:,.2f} | Cat: {prod['category']}")

            # Verification: Category must match
            if prod["category"].lower() != test["expected_category"].lower():
                print(f"     ❌ CROSS-CATEGORY CONTAMINATION: {prod['title']} is {prod['category']}, expected {test['expected_category']}")
                all_passed = False

            # Verification: Budget must be respected
            if test["expected_max_budget"] is not None and prod["price"] > test["expected_max_budget"]:
                print(f"     ❌ BUDGET EXCEEDED: {prod['title']} is ₹{prod['price']}, exceeds {test['expected_max_budget']}")
                all_passed = False

    return all_passed


def test_via_api():
    print("\n" + "=" * 70)
    print("PART 2: TESTING LIVE FASTAPI CHAT ENDPOINT (/api/chat)")
    print("=" * 70)

    url = "http://127.0.0.1:8002/api/chat"
    api_passed = True

    for test in QUERIES:
        q = test["query"]
        print(f"\n[API TEST]: Query: '{q}'")
        payload = json.dumps({"message": q, "category": None, "user_id": f"test_{int(abs(hash(q)))}"}).encode("utf-8")
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})

        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            print(f"  ❌ API Request Error: {e}")
            api_passed = False
            continue

        extracted = data.get("extracted", {})
        products = data.get("products", [])
        answer = data.get("answer", "")

        print(f"  -> API Extracted: {extracted}")
        print(f"  -> Products Returned: {len(products)}")
        print(f"  -> Assistant Answer: {answer[:100]}...")

        # Verify extracted
        if extracted.get("category") != test["expected_category"]:
            print(f"  ❌ Extracted category mismatch: got {extracted.get('category')}, expected {test['expected_category']}")
            api_passed = False
        else:
            print(f"  ✅ Extracted category matched: {extracted.get('category')}")

        if test["expected_max_budget"] is not None:
            if extracted.get("budget") != test["expected_max_budget"]:
                print(f"  ❌ Extracted budget mismatch: got {extracted.get('budget')}, expected {test['expected_max_budget']}")
                api_passed = False
            else:
                print(f"  ✅ Extracted budget matched: ₹{extracted.get('budget')}")

        # Verify products
        for p in products[:5]:
            cat = p.get("category")
            price = p.get("price")
            title = p.get("title")
            brand = p.get("brand")

            if cat.lower() != test["expected_category"].lower():
                print(f"  ❌ WRONG CATEGORY: {title} has category '{cat}', expected '{test['expected_category']}'")
                api_passed = False

            if test["expected_max_budget"] is not None and price > test["expected_max_budget"]:
                print(f"  ❌ EXCEEDS BUDGET: {title} costs ₹{price} > ₹{test['expected_max_budget']}")
                api_passed = False

        if products:
            print(f"  ✅ Top Pick: {products[0]['brand']} {products[0]['title'][:40]} | ₹{products[0]['price']} | {products[0]['category']}")

    return api_passed


if __name__ == "__main__":
    p1 = test_via_python_engine()
    p2 = test_via_api()

    print("\n" + "=" * 70)
    if p1 and p2:
        print("🎉 ALL VERIFICATION TESTS PASSED SUCCESSFULLY! ZERO CROSS-CATEGORY CONTAMINATION!")
    else:
        print("⚠️ SOME TESTS FAILED. CHECK LOGS ABOVE.")
    print("=" * 70)
