"""
ShopAI Phase-2 Validation Test Suite
Tests all 7 phases:
- Phase 1: Home & Kitchen Intelligence & Budgets
- Phase 2: Books Intelligence & Specific queries (e.g. Python books under ₹500)
- Phase 3: Sports Intelligence & Budgets
- Phase 4: Advanced Category Mapping
- Phase 5: AI Shopping Assistant Flow & Conversational Memory
- Phase 6: Product Ranking 2.0 (Formula check & Strictly Top 2)
- Phase 7: No Product Found Flow & Closest Options
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.ai.query_understanding import understand_query, rule_based_query_understanding
from backend.search_engine import search_products, get_budget_fallback
from backend.ranking.ranker import calculate_product_score, ProductRanker
from backend.memory.conversation_store import conversation_store

def run_tests():
    print("=" * 70)
    print("STARTING SHOPAI PHASE-2 PRODUCTION TEST SUITE")
    print("=" * 70)

    # -------------------------------------------------------------
    # TEST 1: Phase 1 - Home & Kitchen Intelligence
    # -------------------------------------------------------------
    print("\n[TEST 1] Phase 1 - Home & Kitchen Flow & Mapping...")
    hk_flow = understand_query("Home & Kitchen")
    assert hk_flow.get("needs_clarification") is True, "Home & Kitchen should trigger clarification"
    assert "Cookware" in str(hk_flow.get("clarification_options")), "Options must include Cookware"
    assert "Kitchen Appliances" in str(hk_flow.get("clarification_options")), "Options must include Kitchen Appliances"
    print("  ✓ Home & Kitchen flow trigger verified")

    hk_search = search_products("Cookware fry pan under 1000", category="Home & Kitchen", budget=1000.0)
    assert len(hk_search) > 0, "Should return cookware"
    assert len(hk_search) <= 2, "Should return top 2 products"
    for p in hk_search:
        p_data = p.get("product", p)
        assert p_data["price"] <= 1000.0, f"Product {p_data['title']} exceeds budget"
        assert p_data["category"] == "Home & Kitchen", "Must be Home & Kitchen"
    print(f"  ✓ Cookware under ₹1000 search returned {len(hk_search)} strictly within budget items")

    # -------------------------------------------------------------
    # TEST 2: Phase 2 - Books Intelligence
    # -------------------------------------------------------------
    print("\n[TEST 2] Phase 2 - Books Intelligence & Python Books Under ₹500...")
    bk_flow = understand_query("Books")
    assert bk_flow.get("needs_clarification") is True, "Books should trigger clarification"
    assert "Programming" in str(bk_flow.get("clarification_options")), "Options must include Programming"
    print("  ✓ Books flow trigger verified")

    py_query = "Python books under 500"
    py_parsed = understand_query(py_query)
    assert py_parsed["category"] == "Books", f"Expected Books, got {py_parsed['category']}"
    assert py_parsed["budget"] == 500.0, f"Expected budget 500, got {py_parsed['budget']}"
    
    py_search = search_products(py_query, category=py_parsed["category"], budget=py_parsed["budget"], subcategory=py_parsed.get("subcategory"))
    assert len(py_search) > 0, "Should return Python books"
    assert len(py_search) <= 2, "Should return top 2 products"
    for p in py_search:
        p_data = p.get("product", p)
        assert p_data["price"] <= 500.0, f"Book {p_data['title']} price ₹{p_data['price']} exceeds ₹500"
        assert "python" in p_data["title"].lower() or "python" in p_data["description"].lower(), "Must be a Python book"
    print(f"  ✓ 'Python books under ₹500' returned strictly Python books: {[p['product']['title'][:30] for p in py_search]}")

    # -------------------------------------------------------------
    # TEST 3: Phase 3 - Sports Intelligence
    # -------------------------------------------------------------
    print("\n[TEST 3] Phase 3 - Sports Intelligence & Cricket...")
    sp_flow = understand_query("Sports")
    assert sp_flow.get("needs_clarification") is True, "Sports should trigger clarification"
    assert "Cricket" in str(sp_flow.get("clarification_options")), "Options must include Cricket"
    print("  ✓ Sports flow trigger verified")

    sp_search = search_products("Cricket bat under 1500", category="Sports", budget=1500.0, subcategory="Cricket")
    assert len(sp_search) > 0, "Should return cricket bat"
    assert len(sp_search) <= 2, "Should return top 2 products"
    for p in sp_search:
        p_data = p.get("product", p)
        assert p_data["price"] <= 1500.0, f"Cricket item {p_data['title']} exceeds budget"
        assert "cricket" in p_data["title"].lower() or "bat" in p_data["title"].lower(), "Must be cricket"
    print(f"  ✓ 'Cricket bat under ₹1500' returned top {len(sp_search)} items: {[p['product']['title'][:30] for p in sp_search]}")

    # -------------------------------------------------------------
    # TEST 4: Phase 4 - Advanced Category Mappings
    # -------------------------------------------------------------
    print("\n[TEST 4] Phase 4 - Advanced Category Mappings...")
    mappings = [
        ("bat", "Sports", "Cricket"),
        ("cricket bat", "Sports", "Cricket"),
        ("dumbbells", "Sports", "Gym Equipment"),
        ("weights", "Sports", "Gym Equipment"),
        ("python book", "Books", "Programming"),
        ("data science book", "Books", "Data Science"),
        ("machine learning book", "Books", "AI & ML"),
        ("bedsheet", "Home & Kitchen", "Bedsheets"),
        ("curtain", "Home & Kitchen", "Curtains"),
        ("sofa cover", "Home & Kitchen", "Home Decor"),
        ("air fryer", "Home & Kitchen", "Air Fryers"),
        ("mixer grinder", "Home & Kitchen", "Mixer Grinders"),
        ("cooker", "Home & Kitchen", "Cookers"),
    ]
    for q, expected_cat, expected_subcat in mappings:
        res = understand_query(q)
        assert res["category"] == expected_cat, f"Query '{q}': expected category '{expected_cat}', got '{res['category']}'"
        assert res["subcategory"] == expected_subcat, f"Query '{q}': expected subcategory '{expected_subcat}', got '{res['subcategory']}'"
        print(f"  ✓ '{q}' -> {res['category']} > {res['subcategory']}")

    # -------------------------------------------------------------
    # TEST 5: Phase 5 - Conversational AI Assistant Multi-turn Flows
    # -------------------------------------------------------------
    print("\n[TEST 5] Phase 5 - Conversational Assistant Multi-Turn...")
    # Laptop flow: "Need a laptop" -> Clarification: Coding / Gaming / College
    laptop_turn1 = understand_query("Need a laptop")
    assert laptop_turn1["needs_clarification"] is True, "Need a laptop should ask for purpose"
    assert "Coding" in str(laptop_turn1["clarification_options"]), "Should provide Coding option"
    print("  ✓ 'Need a laptop' asks for purpose with intelligent options")

    # Phone flow: "Need a phone" -> Clarification: Camera / Battery / Performance
    phone_turn1 = understand_query("Need a phone")
    assert phone_turn1["needs_clarification"] is True, "Need a phone should ask for priority"
    assert "Camera" in str(phone_turn1["clarification_options"]), "Should provide Camera option"
    print("  ✓ 'Need a phone' asks for top feature priority")

    # Shoes flow: "Need shoes" -> Clarification: Running / Casual / Formal
    shoes_turn1 = understand_query("Need shoes")
    assert shoes_turn1["needs_clarification"] is True, "Need shoes should ask for type"
    assert "Running" in str(shoes_turn1["clarification_options"]), "Should provide Running option"
    print("  ✓ 'Need shoes' asks for shoe type")

    # Multi-turn session memory
    user_id = "test_user_phase2"
    conversation_store.update_preferences_from_query(user_id, {"raw_query": "reset"})
    
    # Turn 1: user expresses interest in Programming Books
    p1 = understand_query("Programming books")
    eff1 = conversation_store.get_effective_parameters(user_id, p1)
    assert eff1["category"] == "Books"
    assert eff1["subcategory"] == "Programming"

    # Turn 2: user says "under ₹500"
    p2 = understand_query("under 500")
    eff2 = conversation_store.get_effective_parameters(user_id, p2)
    assert eff2["category"] == "Books", "Memory should preserve category=Books"
    assert eff2["subcategory"] == "Programming", "Memory should preserve subcategory=Programming"
    assert eff2["budget"] == 500.0, "Memory should record budget=500"
    print("  ✓ Conversational multi-turn memory successfully preserved across turns")

    # -------------------------------------------------------------
    # TEST 6: Phase 6 - Product Ranking 2.0
    # -------------------------------------------------------------
    print("\n[TEST 6] Phase 6 - Product Ranking 2.0 Formula & Top 2...")
    prod_sample = {
        "title": "Prestige Omega Select Plus Non-Stick Fry Pan 24cm",
        "category": "Home & Kitchen",
        "subcategory": "Cookware",
        "brand": "Prestige",
        "price": 749.0,
        "rating": 4.5,
        "review_count": 1200,
        "description": "Non-stick induction fry pan durable coating"
    }
    score_res = calculate_product_score(prod_sample, budget=1000.0, query_type="Cookware", raw_query="fry pan under 1000")
    assert score_res["final_score"] > 80.0, f"Expected high ranking score, got {score_res['final_score']}"
    print(f"  ✓ Score calculation verified: Final={score_res['final_score']}/100, Breakdown={score_res}")

    # Verify strictly Top 2 returned
    search_res = search_products("Cookware under 5000", category="Home & Kitchen", budget=5000.0)
    assert len(search_res) == 2, f"Expected strictly 2 products, got {len(search_res)}"
    assert search_res[0]["product"]["rank"] == 1
    assert search_res[1]["product"]["rank"] == 2
    assert search_res[0]["product"]["why_recommended"] is not None
    print(f"  ✓ Strict Top 2 return verified with Why explanations: {search_res[0]['product']['why_recommended']}")

    # -------------------------------------------------------------
    # TEST 7: Phase 7 - No Product Found Flow
    # -------------------------------------------------------------
    print("\n[TEST 7] Phase 7 - No Product Found Flow & Closest Options...")
    # Laptop under ₹500 does not exist
    unreal_search = search_products("Laptop under 500", category="Laptops", budget=500.0, subcategory="Laptop")
    assert unreal_search.success is False, "Should fail budget filter"
    assert len(unreal_search) == 0, "Must NEVER return products outside budget"
    assert "Sorry, I couldn't find any products matching your budget" in unreal_search.message
    assert "Closest options" in unreal_search.message
    assert len(unreal_search.alternatives) > 0
    print(f"  ✓ No Product Found Flow message:\n{unreal_search.message}")

    print("\n" + "=" * 70)
    print("ALL TESTS PASSED SUCCESSFULLY! PRODUCTION READY 🚀")
    print("=" * 70)

if __name__ == "__main__":
    run_tests()
