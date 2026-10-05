"""
Verification of Clarification Flow and Conversational Memory

Verifies:
1. Best Electronics under 25000 -> Smartphone (Only phones <= 25000, budget preserved, no phones over budget)
2. Best Electronics under 25000 -> Laptop (No laptops under 25000, lowest starts at 36990, budget preserved)
3. Best Electronics under 25000 -> Earbuds (Only earbuds <= 25000, budget preserved)
4. Best Fashion under 1000 -> Jeans (Only jeans <= 1000, budget preserved)
5. Direct specific query "wireless earbuds" -> No clarification needed

Assertions:
- budget_before == budget_after
- budget must never become null after clarification
"""

import sys
import json
from pathlib import Path

# Add project root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from backend.main import app
from backend.auth.jwt_handler import create_access_token
from backend.database.db import get_user_by_email, create_user

# Fix Windows console encoding for Unicode checkmarks
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

test_user = get_user_by_email("test_clarify@example.com")
if not test_user:
    test_user = create_user("Test Clarify User", "test_clarify@example.com", "hash", is_verified=1)
auth_headers = {"Authorization": f"Bearer {create_access_token(test_user['id'], test_user['email'])}"}

client = TestClient(app)


def send_chat(message: str, user_id: str, category=None):
    res = client.post(
        "/api/chat",
        json={"message": message, "category": category, "user_id": user_id},
        headers=auth_headers
    )
    return res.json()



def test_clarification():
    print("=" * 70)
    print("TESTING CLARIFICATION FLOW & CONVERSATIONAL MEMORY")
    print("=" * 70)

    # =========================================================================
    # SCENARIO 1: "Best Electronics under 25000" -> "Smartphone"
    # =========================================================================
    user_phone = "session_test_phone_001"
    print("\n--- SCENARIO 1: Best Electronics under 25000 -> Smartphone ---")
    print("[Turn 1]: User sends: 'Best Electronics under 25000'")
    res1 = send_chat("Best Electronics under 25000", user_phone)
    budget_before = res1.get("extracted", {}).get("budget")
    print("  -> needs_clarification:", res1.get("needs_clarification"))
    print("  -> extracted budget_before:", budget_before)
    print("  -> options:", res1.get("options"))

    assert res1.get("needs_clarification") is True, "Expected needs_clarification=True"
    assert budget_before == 25000.0, f"Expected budget_before=25000.0, got {budget_before}"
    assert len(res1.get("products", [])) == 0, "Products should NOT be retrieved immediately"

    print("\n[Turn 2]: User clarifies: 'Smartphone'")
    res2 = send_chat("Smartphone", user_phone)
    budget_after = res2.get("extracted", {}).get("budget")
    print("  -> needs_clarification:", res2.get("needs_clarification"))
    print("  -> extracted budget_after:", budget_after)
    print("  -> extracted category:", res2.get("extracted", {}).get("category"))
    print("  -> extracted subcategory:", res2.get("extracted", {}).get("subcategory"))
    print("  -> products returned count:", len(res2.get("products", [])))
    print("  -> success:", res2.get("success"))
    print("  -> message:", res2.get("message"))
    print("  -> suggestion:", res2.get("suggestion"))

    # ASSERTIONS (TASK 5)
    assert budget_after is not None, "Budget must never become null after clarification!"
    assert budget_before == budget_after, f"budget_before ({budget_before}) != budget_after ({budget_after})"
    assert res2.get("needs_clarification") is False, "Expected needs_clarification=False"
    assert res2.get("extracted", {}).get("category") in ["Mobiles", "Smartphones"], "Expected category=Mobiles/Smartphones for Smartphone"
    assert res2.get("extracted", {}).get("subcategory") == "Smartphone", "Expected subcategory=Smartphone"

    # Strict budget verification: all phones returned must be <= 25000
    for p in res2.get("products", []):
        assert p["price"] <= 25000.0, f"Phone price {p['price']} exceeds budget 25000!"
    assert len(res2.get("products", [])) > 0, "Expected matching phones <= 25000"
    print("  ✅ Scenario 1 Passed: Budget 25,000 preserved, category=Mobiles/Smartphones, only phones <= 25,000 returned!")

    # =========================================================================
    # SCENARIO 2: "Best Electronics under 25000" -> "Laptop"
    # =========================================================================
    user_laptop = "session_test_laptop_002"
    print("\n--- SCENARIO 2: Best Electronics under 25000 -> Laptop ---")
    print("[Turn 1]: User sends: 'Best Electronics under 25000'")
    res1_lap = send_chat("Best Electronics under 25000", user_laptop)
    budget_before_lap = res1_lap.get("extracted", {}).get("budget")

    print("\n[Turn 2]: User clarifies: 'Laptop'")
    res2_lap = send_chat("Laptop", user_laptop)
    budget_after_lap = res2_lap.get("extracted", {}).get("budget")
    print("  -> extracted budget_after:", budget_after_lap)
    print("  -> products returned count:", len(res2_lap.get("products", [])))
    print("  -> message:", res2_lap.get("message"))
    print("  -> suggestion:", res2_lap.get("suggestion"))

    # ASSERTIONS (TASK 5)
    assert budget_after_lap is not None, "Budget must never become null after clarification!"
    assert budget_before_lap == budget_after_lap, f"budget_before ({budget_before_lap}) != budget_after ({budget_after_lap})"
    assert len(res2_lap.get("products", [])) == 0, "No laptops <= 25000 exist in catalog"
    assert any(p in str(res2_lap.get("message", "")) or p in str(res2_lap.get("suggestion", "")) for p in ["34,990", "36,990"]), "Expected suggestion mentioning lowest laptop at 34,990 / 36,990"
    print("  ✅ Scenario 2 Passed: Budget 25,000 preserved, lowest laptop suggested!")


    # =========================================================================
    # SCENARIO 3: "Best Electronics under 25000" -> "Earbuds"
    # =========================================================================
    user_earbuds = "session_test_earbuds_003"
    print("\n--- SCENARIO 3: Best Electronics under 25000 -> Earbuds ---")
    print("[Turn 1]: User sends: 'Best Electronics under 25000'")
    res1_ear = send_chat("Best Electronics under 25000", user_earbuds)
    budget_before_ear = res1_ear.get("extracted", {}).get("budget")

    print("\n[Turn 2]: User clarifies: 'Earbuds'")
    res2_ear = send_chat("Earbuds", user_earbuds)
    budget_after_ear = res2_ear.get("extracted", {}).get("budget")
    print("  -> extracted budget_after:", budget_after_ear)
    print("  -> products returned count:", len(res2_ear.get("products", [])))

    # ASSERTIONS (TASK 5)
    assert budget_after_ear is not None, "Budget must never become null after clarification!"
    assert budget_before_ear == budget_after_ear, f"budget_before ({budget_before_ear}) != budget_after ({budget_after_ear})"
    assert len(res2_ear.get("products", [])) > 0, "Earbuds within budget 25000 exist in catalog"
    for p in res2_ear.get("products", []):
        assert p["price"] <= 25000.0, f"Earbud price {p['price']} exceeds budget 25000!"
        print(f"     - {p['brand']} {p['title'][:35]} | ₹{p['price']}")
    print("  ✅ Scenario 3 Passed: Budget 25,000 preserved, only earbuds <= 25,000 returned!")

    # =========================================================================
    # SCENARIO 4: "Best Fashion under 1000" -> "Jeans"
    # =========================================================================
    user_jeans = "session_test_jeans_004"
    print("\n--- SCENARIO 4: Best Fashion under 1000 -> Jeans ---")
    print("[Turn 1]: User sends: 'Best Fashion under 1000'")
    res1_jean = send_chat("Best Fashion under 1000", user_jeans)
    budget_before_jean = res1_jean.get("extracted", {}).get("budget")

    print("\n[Turn 2]: User clarifies: 'Jeans'")
    res2_jean = send_chat("Jeans", user_jeans)
    budget_after_jean = res2_jean.get("extracted", {}).get("budget")
    print("  -> extracted budget_after:", budget_after_jean)
    print("  -> products returned count:", len(res2_jean.get("products", [])))

    # ASSERTIONS (TASK 5)
    assert budget_after_jean is not None, "Budget must never become null after clarification!"
    assert budget_before_jean == budget_after_jean, f"budget_before ({budget_before_jean}) != budget_after ({budget_after_jean})"
    assert len(res2_jean.get("products", [])) > 0, "Jeans within budget 1000 exist in catalog"
    for p in res2_jean.get("products", []):
        assert p["price"] <= 1000.0, f"Jeans price {p['price']} exceeds budget 1000!"
        print(f"     - {p['brand']} {p['title'][:35]} | ₹{p['price']}")
    print("  ✅ Scenario 4 Passed: Budget 1,000 preserved, only jeans <= 1,000 returned!")

    # =========================================================================
    # SCENARIO 5: Direct Specific Query "wireless earbuds"
    # =========================================================================
    print("\n--- SCENARIO 5: Direct specific query: 'wireless earbuds' ---")
    res5 = send_chat("wireless earbuds", "session_direct_005")
    assert res5.get("needs_clarification") is False, "Specific queries should NOT require clarification"
    assert len(res5.get("products", [])) > 0, "Specific queries should immediately return products"
    print("  ✅ Scenario 5 Passed: Specific query immediately returned products without clarification!")

    print("\n" + "=" * 70)
    print("🎉 ALL 5 CLARIFICATION & MEMORY SCENARIOS PASSED PERFECTLY!")
    print("=" * 70)


if __name__ == "__main__":
    test_clarification()
