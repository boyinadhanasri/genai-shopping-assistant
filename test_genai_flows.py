from backend.search_engine import search_products
from backend.ai.query_understanding import understand_query
from backend.memory.conversation_store import conversation_store
from backend.models.product import Product
from comparison.comparison_engine import build_comparison

def run_tests():
    print("=== Testing Search Engine & Flow Configs ===")
    store = conversation_store
    session_id = "test-session-genai"

    # Test 1: Fashion Flow
    print("\n--- Test 1: Fashion Flow ---")
    p1 = understand_query("Fashion")
    step1 = store.get_effective_parameters(session_id, p1)
    print(f"Fashion Step 1: Flow Question={step1.get('flow_question')} | Options={step1.get('flow_options')}")
    assert step1.get("flow_options") is not None

    p2 = understand_query("₹1000")
    step2 = store.get_effective_parameters(session_id, p2)
    print(f"Fashion Step 2 (Budget): Budget={step2.get('budget')} | Flow Question={step2.get('flow_question')} | Options={step2.get('flow_options')}")

    p3 = understand_query("Men")
    step3 = store.get_effective_parameters(session_id, p3)
    print(f"Fashion Step 3 (Gender): Gender={step3.get('gender')} | Flow Question={step3.get('flow_question')} | Options={step3.get('flow_options')}")

    # Test 2: Smartphone Flow
    print("\n--- Test 2: Smartphone Flow ---")
    s_sess = "test-session-phone"
    ps1 = understand_query("smartphones")
    s1 = store.get_effective_parameters(s_sess, ps1)
    print(f"Phone Step 1: Flow Question={s1.get('flow_question')} | Options={s1.get('flow_options')}")
    assert any("Under ₹20k" in opt or "20k" in opt for opt in s1.get('flow_options', []))

    ps2 = understand_query("Under ₹30k")
    s2 = store.get_effective_parameters(s_sess, ps2)
    print(f"Phone Step 2: Budget={s2.get('budget')} | Flow Question={s2.get('flow_question')} | Options={s2.get('flow_options')}")
    assert any("Camera" in opt or "Gaming" in opt for opt in s2.get('flow_options', []))

    # Test 3: Recommendation Ranking & Badges
    print("\n--- Test 3: Badges & Rankings ---")
    results = search_products("samsung smartphone", category="Electronics", budget=30000)
    print(f"Found {len(results)} products")
    badges = [p.get("badge") for p in results if p.get("badge")]
    print(f"Assigned Badges: {badges}")
    assert any("Recommendation" in b or "Runner" in b or "#1" in b or "#2" in b or "Overall" in b or "Value" in b or "Popular" in b or "Cheap" in b or "Pick" in b for b in badges)
    if len(results) > 0:
        print(f"Top Product: {results[0].get('title')} | Badge: {results[0].get('badge')} | Why: {results[0].get('why_recommended')}")

    # Test 4: Strict No-Results Fallback (Cameras under 25k shouldn't return earbuds)
    print("\n--- Test 4: Strict Subcategory Fallback ---")
    cam_results = search_products("camera under 25000", category="Electronics", subcategory="Camera", budget=25000)
    print(f"Camera under 25k message: {cam_results.message}")
    for p in cam_results:
        # Verify no earbuds returned
        assert "earbud" not in p.get("title", "").lower() and "airdopes" not in p.get("title", "").lower() and "earphone" not in p.get("title", "").lower()
    print("Passed: No cross-contamination of subcategories in camera search.")

    # Test 5: Brand Memory Retention
    print("\n--- Test 5: Brand Retention Across Turns ---")
    m_sess = "test-session-memory"
    pm1 = understand_query("Show Samsung phones")
    m1 = store.get_effective_parameters(m_sess, pm1)
    sess1 = store.get_session(m_sess)
    print(f"Turn 1 Brand in memory: {sess1.preferences.brand}")
    assert sess1.preferences.brand == "Samsung"
    
    pm2 = understand_query("Show camera phones")
    m2 = store.get_effective_parameters(m_sess, pm2)
    sess2 = store.get_session(m_sess)
    print(f"Turn 2 Brand in memory: {sess2.preferences.brand} | Extracted Brand: {m2.get('brand')}")
    assert sess2.preferences.brand == "Samsung"
    print("Passed: Brand preference remembered across turns.")

    # Test 6: Comparison Engine
    print("\n--- Test 6: Comparison Engine Specs & Verdicts ---")
    p_a = search_products("iPhone 15", category="Electronics")[0]
    p_b = search_products("Samsung S24", category="Electronics")[0]
    comp = build_comparison([Product(**(p_a.get("product") or p_a)), Product(**(p_b.get("product") or p_b))])
    print(f"Comparison Attributes: {comp.get('attributes')}")
    print(f"Verdicts: {comp.get('verdicts')}")
    assert "photography" in comp.get("verdicts", {})
    assert "gaming" in comp.get("verdicts", {})
    assert "value" in comp.get("verdicts", {})
    # Test 7: Toys & Games Shopping Flow
    print("\n--- Test 7: Toys & Games Shopping Flow ---")
    toy_sess = "test-session-toys"
    pt1 = understand_query("Toys")
    t1 = store.get_effective_parameters(toy_sess, pt1)
    print(f"Toys Step 1: Flow Question={t1.get('flow_question')} | Options={t1.get('flow_options')}")
    assert any("Kids" in opt or "Toddlers" in opt for opt in t1.get('flow_options', []))

    pt2 = understand_query("🧒 Kids (4-7 yrs)")
    t2 = store.get_effective_parameters(toy_sess, pt2)
    print(f"Toys Step 2: Purpose={t2.get('purpose')} | Flow Question={t2.get('flow_question')} | Options={t2.get('flow_options')}")
    assert any("LEGO" in opt or "Board Games" in opt for opt in t2.get('flow_options', []))

    pt3 = understand_query("🧱 LEGO & Building Blocks")
    t3 = store.get_effective_parameters(toy_sess, pt3)
    print(f"Toys Step 3: Subcategory={t3.get('subcategory')} | Flow Question={t3.get('flow_question')} | Options={t3.get('flow_options')}")
    assert any("Under ₹2,000" in opt or "500" in opt for opt in t3.get('flow_options', []))

    toy_results = search_products("LEGO building blocks", category="Toys", budget=2000)
    print(f"Toys search found {len(toy_results)} products")
    assert len(toy_results) > 0
    print(f"Top Toy: {toy_results[0].get('title')} | ₹{toy_results[0].get('price')} | {toy_results[0].get('brand')}")

    print("\n🎉 ALL GENAI FLOW & SHOPPING ASSISTANT TESTS PASSED!")

if __name__ == "__main__":
    run_tests()

