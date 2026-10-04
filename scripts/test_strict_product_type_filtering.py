"""
Comprehensive Test Script for Strict Product Type Filtering & No-Results Handling

Verifies:
Case 1: Best Electronics under 25000 -> Camera (Only Camera or closest camera fallback)
Case 2: Best Electronics under 25000 -> Smartphone (Only Smartphones)
Case 3: Best Electronics under 25000 -> TV (Only TVs)
Case 4: Fashion under 1500 -> Jeans (Only Jeans)
Case 5: Laptop under 30000 (No laptops under 30000, closest laptop options)
"""

import os
import sys
from pathlib import Path

# Ensure UTF-8 output
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from backend.models.product import ChatRequest
from backend.api.routes import chat_assistant_endpoint
from backend.memory.conversation_store import conversation_store


def run_tests():
    print("=" * 70)
    print("RUNNING STRICT PRODUCT TYPE FILTERING & NO-RESULTS TEST SUITE")
    print("=" * 70)

    # -------------------------------------------------------------------------
    # CASE 1: Best Electronics under 25000 -> Camera
    # -------------------------------------------------------------------------
    user_1 = "test_user_case_1"
    conversation_store.clear(user_1)

    print("\n>>> CASE 1: Turn 1 - 'Best Electronics under 25000'")
    req1 = ChatRequest(user_id=user_1, message="Best Electronics under 25000")
    res1 = chat_assistant_endpoint(req1)
    print(f"Needs Clarification: {res1.needs_clarification}")
    print(f"Message: {res1.message}")
    print(f"Options: {res1.options}")
    assert res1.needs_clarification is True
    assert "Camera" in res1.options

    print("\n>>> CASE 1: Turn 2 - 'Camera'")
    req2 = ChatRequest(user_id=user_1, message="Camera")
    res2 = chat_assistant_endpoint(req2)
    print(f"Needs Clarification: {res2.needs_clarification}")
    print(f"Message: {res2.message}")
    print(f"Products count: {len(res2.products)}")
    for p in res2.products:
        print(f"  - [{p.category}] {p.brand} {p.title} | ₹{p.price}")
        assert "camera" in p.title.lower() or "camera" in p.description.lower()

    # If 0 cameras under 25000:
    if len(res2.products) == 0:
        print("Verified smart fallback for cameras:")
        assert "Camera" in res2.message or "Cameras" in res2.message
        assert "Earbuds" not in res2.message
        assert "Laptops" not in res2.message
        assert "Smartphones" not in res2.message

    print("✓ CASE 1 PASSED: Strict camera handling & no unrelated products.")

    # -------------------------------------------------------------------------
    # CASE 2: Best Electronics under 25000 -> Smartphone
    # -------------------------------------------------------------------------
    user_2 = "test_user_case_2"
    conversation_store.clear(user_2)

    print("\n>>> CASE 2: Turn 1 - 'Best Electronics under 25000'")
    req1 = ChatRequest(user_id=user_2, message="Best Electronics under 25000")
    res1 = chat_assistant_endpoint(req1)
    assert res1.needs_clarification is True

    print("\n>>> CASE 2: Turn 2 - 'Smartphone'")
    req2 = ChatRequest(user_id=user_2, message="Smartphone")
    res2 = chat_assistant_endpoint(req2)
    print(f"Products count: {len(res2.products)}")
    assert len(res2.products) > 0
    for p in res2.products:
        print(f"  - [{p.category}] {p.brand} {p.title} | ₹{p.price}")
        assert p.price <= 25000.0
        # Ensure only smartphones
        assert any(k in p.title.lower() for k in ["galaxy", "5g", "phone", "redmi", "oneplus", "realme", "narzo", "smartphone"])
        assert "earbuds" not in p.title.lower()
        assert "tv" not in p.title.lower()
        assert "laptop" not in p.title.lower()

    print("✓ CASE 2 PASSED: Only Smartphones returned.")

    # -------------------------------------------------------------------------
    # CASE 3: Best Electronics under 25000 -> TV
    # -------------------------------------------------------------------------
    user_3 = "test_user_case_3"
    conversation_store.clear(user_3)

    print("\n>>> CASE 3: Turn 1 - 'Best Electronics under 25000'")
    req1 = ChatRequest(user_id=user_3, message="Best Electronics under 25000")
    res1 = chat_assistant_endpoint(req1)
    assert res1.needs_clarification is True

    print("\n>>> CASE 3: Turn 2 - 'TV'")
    req2 = ChatRequest(user_id=user_3, message="TV")
    res2 = chat_assistant_endpoint(req2)
    print(f"Products count: {len(res2.products)}")
    assert len(res2.products) > 0
    for p in res2.products:
        print(f"  - [{p.category}] {p.brand} {p.title} | ₹{p.price}")
        assert p.price <= 25000.0
        assert "tv" in p.title.lower() or "television" in p.title.lower()
        assert "earbuds" not in p.title.lower()
        assert "laptop" not in p.title.lower()

    print("✓ CASE 3 PASSED: Only TVs returned.")

    # -------------------------------------------------------------------------
    # CASE 4: Fashion under 1500 -> Jeans
    # -------------------------------------------------------------------------
    user_4 = "test_user_case_4"
    conversation_store.clear(user_4)

    print("\n>>> CASE 4: Turn 1 - 'Fashion under 1500'")
    req1 = ChatRequest(user_id=user_4, message="Fashion under 1500")
    res1 = chat_assistant_endpoint(req1)
    assert res1.needs_clarification is True
    assert "Jeans" in res1.options

    print("\n>>> CASE 4: Turn 2 - 'Jeans'")
    req2 = ChatRequest(user_id=user_4, message="Jeans")
    res2 = chat_assistant_endpoint(req2)
    print(f"Products count: {len(res2.products)}")
    assert len(res2.products) > 0
    for p in res2.products:
        print(f"  - [{p.category}] {p.brand} {p.title} | ₹{p.price}")
        assert p.price <= 1500.0
        assert "jean" in p.title.lower() or "denim" in p.title.lower() or "jeans" in p.description.lower()

    print("✓ CASE 4 PASSED: Only Jeans returned.")

    # -------------------------------------------------------------------------
    # CASE 5: Laptop under 30000
    # -------------------------------------------------------------------------
    user_5 = "test_user_case_5"
    conversation_store.clear(user_5)

    print("\n>>> CASE 5: Single Turn - 'Laptop under 30000'")
    req1 = ChatRequest(user_id=user_5, message="Laptop under 30000")
    res1 = chat_assistant_endpoint(req1)
    print(f"Products count: {len(res1.products)}")
    print(f"Message:\n{res1.message}")
    print(f"Alternatives: {res1.alternatives}")
    assert len(res1.products) == 0
    assert "Laptop" in res1.message or "Laptops" in res1.message
    assert "30,000" in res1.message
    assert "Closest Laptop options:" in res1.message

    print("✓ CASE 5 PASSED: Proper no-results message and closest laptops.")

    print("\n" + "=" * 70)
    print("ALL 5 TEST CASES PASSED PERFECTLY!")
    print("=" * 70)


if __name__ == "__main__":
    run_tests()
