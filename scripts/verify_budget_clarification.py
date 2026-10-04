"""
Test & Verify Budget Constraint Preservation After Clarification Flow
"""

import sys
import json
from pathlib import Path

# Fix Windows console encoding
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

# Ensure backend can be imported
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.ai.query_understanding import understand_query
from backend.memory.conversation_store import conversation_store
from backend.search_engine import search_products, get_budget_fallback
from backend.api.routes import chat_assistant_endpoint
from backend.models.product import ChatRequest, ChatMessage


def run_tests():
    print("=" * 80)
    print("VERIFYING BUDGET PRESERVATION AFTER CLARIFICATION FLOW")
    print("=" * 80)

    # -------------------------------------------------------------------------
    # TEST 1: Best Electronics under 25000 -> Smartphone
    # -------------------------------------------------------------------------
    print("\n--- TEST 1: Best Electronics under 25000 -> Smartphone ---")
    user_id = "test_user_flow_25k"
    conversation_store.clear(user_id)

    # Message 1
    req1 = ChatRequest(message="Best Electronics under 25000", user_id=user_id)
    resp1 = chat_assistant_endpoint(req1)

    print("Message 1 Response:")
    print("  needs_clarification:", resp1.needs_clarification)
    print("  message:", resp1.message)
    print("  options:", resp1.options)
    print("  products len:", len(resp1.products))

    # Check conversation memory state after message 1
    session1 = conversation_store.get_session(user_id)
    pref1 = session1.preferences
    print("Memory after message 1:")
    print(f"  category: {pref1.category}")
    print(f"  budget: {pref1.budget}")
    print(f"  awaiting_product_type: {pref1.awaiting_product_type}")

    assert resp1.needs_clarification is True, "Turn 1 must request clarification"
    assert pref1.category == "Electronics", "Turn 1 category must be Electronics"
    assert pref1.budget == 25000.0, "Turn 1 budget must be 25000"
    assert pref1.awaiting_product_type is True, "Turn 1 awaiting_product_type must be True"
    assert len(resp1.products) == 0, "Turn 1 must not return products immediately"

    # Message 2: "Smartphone"
    print("\nMessage 2: 'Smartphone'")
    req2 = ChatRequest(message="Smartphone", user_id=user_id)
    resp2 = chat_assistant_endpoint(req2)

    session2 = conversation_store.get_session(user_id)
    pref2 = session2.preferences
    print("Memory after message 2:")
    print(f"  category: {pref2.category}")
    print(f"  subcategory: {pref2.subcategory}")
    print(f"  budget: {pref2.budget}")
    print(f"  awaiting_product_type: {pref2.awaiting_product_type}")

    print("Message 2 Response:")
    print("  success:", resp2.success)
    print("  message:", resp2.message)
    print("  products len:", len(resp2.products))

    # Assertions
    assert pref2.category == "Mobiles", "Merged category must be Mobiles"
    assert pref2.budget == 25000.0, "Merged budget must be 25000"
    assert pref2.awaiting_product_type is False, "awaiting_product_type must be cleared"
    assert len(resp2.products) == 0, "No catalog smartphones exist <= 25000, products must be empty!"
    for p in resp2.products:
        assert p.price <= 25000.0, f"Product {p.title} has price {p.price} > 25000!"

    expected_msg = "Sorry, I couldn't find any smartphones under ₹25,000. The cheapest available smartphone starts at ₹31,999."
    assert resp2.message == expected_msg, f"Expected exact message:\n{expected_msg}\nGot:\n{resp2.message}"

    print("✅ TEST 1 PASSED: Memory correctly transitioned to Mobiles + budget 25000, 0 products returned, exact message verified!")

    # -------------------------------------------------------------------------
    # TEST 2: Best Electronics under 10000 -> Smartphone
    # -------------------------------------------------------------------------
    print("\n--- TEST 2: Best Electronics under 10000 -> Smartphone ---")
    user_id_10k = "test_user_flow_10k"
    conversation_store.clear(user_id_10k)

    req2_1 = ChatRequest(message="Best Electronics under 10000", user_id=user_id_10k)
    resp2_1 = chat_assistant_endpoint(req2_1)
    assert resp2_1.needs_clarification is True

    req2_2 = ChatRequest(message="Smartphone", user_id=user_id_10k)
    resp2_2 = chat_assistant_endpoint(req2_2)

    print("Message 2 (10k) Response:")
    print("  message:", resp2_2.message)
    print("  products len:", len(resp2_2.products))

    assert len(resp2_2.products) == 0, "Must return 0 products"
    expected_msg_10k = "Sorry, I couldn't find any smartphones under ₹10,000. The cheapest available smartphone starts at ₹31,999."
    assert resp2_2.message == expected_msg_10k, f"Expected exact message:\n{expected_msg_10k}\nGot:\n{resp2_2.message}"

    print("✅ TEST 2 PASSED: Best Electronics under 10000 -> Smartphone returns exact no-results message and 0 products!")

    # -------------------------------------------------------------------------
    # TEST 3: Best Electronics under 25000 -> Earbuds (Products DO exist <= 25000)
    # -------------------------------------------------------------------------
    print("\n--- TEST 3: Best Electronics under 25000 -> Earbuds ---")
    user_id_ear = "test_user_flow_earbuds"
    conversation_store.clear(user_id_ear)

    chat_assistant_endpoint(ChatRequest(message="Best Electronics under 25000", user_id=user_id_ear))
    resp_ear = chat_assistant_endpoint(ChatRequest(message="Earbuds", user_id=user_id_ear))

    print(f"Products returned count: {len(resp_ear.products)}")
    assert len(resp_ear.products) > 0, "Earbuds <= 25000 exist in catalog"
    for p in resp_ear.products:
        assert p.price <= 25000.0, f"Earbud price {p.price} > 25000!"
        print(f"  - {p.brand} {p.title[:35]} | ₹{p.price}")

    print("✅ TEST 3 PASSED: Best Electronics under 25000 -> Earbuds returns ONLY products <= 25,000!")

    # -------------------------------------------------------------------------
    # TEST 4: History Fallback (State recovery across stateless or reloaded server)
    # -------------------------------------------------------------------------
    print("\n--- TEST 4: Stateless History Recovery ---")
    fresh_user_id = "test_stateless_user"
    conversation_store.clear(fresh_user_id)  # Emulate server reboot or fresh session

    history = [
        ChatMessage(role="user", content="Best Electronics under ₹25,000"),
        ChatMessage(role="assistant", content="What type of electronics? Laptop / Smartphone / Earbuds / Smartwatch / Camera / TV")
    ]
    stateless_req = ChatRequest(
        message="Smartphone",
        user_id=fresh_user_id,
        history=history
    )
    stateless_resp = chat_assistant_endpoint(stateless_req)
    print("Stateless Response:")
    print("  message:", stateless_resp.message)
    print("  products len:", len(stateless_resp.products))
    assert len(stateless_resp.products) == 0
    assert stateless_resp.message == expected_msg
    print("✅ TEST 4 PASSED: Stateless request with history recovered budget 25000 and prevented any leak of expensive phones!")

    print("\n" + "=" * 80)
    print("🎉 ALL TESTS PASSED SUCCESSFULLY!")
    print("=" * 80)


if __name__ == "__main__":
    run_tests()
