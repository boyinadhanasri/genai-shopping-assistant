"""
Comprehensive Test Suite for Intelligent Product Ranking Engine.
"""

import sys
from pathlib import Path

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(root_dir))

from backend.config.brand_scores import get_brand_score, get_normalized_brand_score, BRAND_SCORES
from backend.ranking.ranker import (
    calculate_product_score,
    compute_budget_score,
    compute_rating_score,
    compute_review_score,
    compute_brand_score,
    compute_query_relevance,
    compute_popularity_score,
    generate_why_recommended,
    rank_products,
)
from backend.search_engine import search_products, get_budget_fallback


def test_brand_scores():
    print("\n--- 1. Testing Brand Scores ---")
    assert get_brand_score("APPLE") == 10.0, "Apple score should be 10"
    assert get_brand_score("SAMSUNG") == 10.0, "Samsung score should be 10"
    assert get_brand_score("SONY") == 9.0, "Sony score should be 9"
    assert get_brand_score("DELL") == 9.0, "Dell score should be 9"
    assert get_brand_score("HP") == 8.0, "HP score should be 8"
    assert get_brand_score("ASUS") == 8.0, "Asus score should be 8"
    assert get_brand_score("ACER") == 7.0, "Acer score should be 7"
    assert get_brand_score("BOAT") == 7.0, "Boat score should be 7"
    assert get_brand_score("REALME") == 7.0, "Realme score should be 7"
    assert get_brand_score("UNKNOWN_BRAND_XYZ") == 4.0, "Unknown brand score should be 4"
    print("✓ All Brand Scores verified successfully!")


def test_budget_scoring():
    print("\n--- 2. Testing Budget Scoring ---")
    budget = 25000.0
    score_24999 = compute_budget_score(24999.0, budget)
    score_24500 = compute_budget_score(24500.0, budget)
    score_5000 = compute_budget_score(5000.0, budget)
    score_30000 = compute_budget_score(30000.0, budget)

    print(f"Budget: ₹25,000 | ₹24,999 score: {score_24999:.4f}")
    print(f"Budget: ₹25,000 | ₹24,500 score: {score_24500:.4f}")
    print(f"Budget: ₹25,000 | ₹5,000 score: {score_5000:.4f}")
    print(f"Budget: ₹25,000 | ₹30,000 score (over-budget): {score_30000:.4f}")

    assert score_24999 > score_24500 > score_5000, "Higher budget utilization must yield higher score within budget"
    assert score_30000 == 0.0, "Over budget products must yield 0 score"
    print("✓ Budget scoring verified successfully!")


def test_review_scoring():
    print("\n--- 3. Testing Review Scoring ---")
    score_15 = compute_review_score(15)
    score_8000 = compute_review_score(8000)

    print(f"15 reviews score: {score_15:.4f}")
    print(f"8,000 reviews score: {score_8000:.4f}")

    assert score_8000 > score_15, "8000 reviews must score significantly higher than 15 reviews"
    print("✓ Review scoring verified successfully!")


def test_strict_query_relevance():
    print("\n--- 4. Testing Strict Query Relevance & Cross-Type Rejection ---")
    cam_rel = compute_query_relevance(
        product_title="Canon EOS 1500D DSLR Camera",
        product_category="Electronics",
        product_subcategory="Camera",
        query_type="camera",
        raw_query="camera under 25000"
    )
    earbud_rel = compute_query_relevance(
        product_title="boAt Airdopes 141 True Wireless Earbuds",
        product_category="Electronics",
        product_subcategory="Earbuds",
        query_type="camera",
        raw_query="camera under 25000"
    )
    watch_rel = compute_query_relevance(
        product_title="Noise ColorFit Pro 4 Smartwatch",
        product_category="Electronics",
        product_subcategory="Smartwatch",
        query_type="camera",
        raw_query="camera under 25000"
    )

    print(f"Camera product relevance for 'camera under 25000': {cam_rel}")
    print(f"Earbuds product relevance for 'camera under 25000': {earbud_rel}")
    print(f"Smartwatch product relevance for 'camera under 25000': {watch_rel}")

    assert cam_rel >= 0.95, "Camera product should have full relevance"
    assert earbud_rel == 0.0, "Earbuds product must receive 0 relevance for camera query"
    assert watch_rel == 0.0, "Smartwatch product must receive 0 relevance for camera query"
    print("✓ Strict Query Relevance verified successfully!")


def test_top_2_recommendations():
    print("\n--- 5. Testing Top 2 Best Recommendations Limit ---")
    res = search_products("Laptop under 50000", category="Electronics", subcategory="Laptop", budget=50000.0, top_k=2)
    print(f"Results returned count: {len(res)}")
    assert len(res) <= 2, f"Search must return at most 2 products, got {len(res)}"
    assert len(res) > 0, "Should find matching laptops under 50000"
    
    for idx, item in enumerate(res):
        p = item.get("product", item)
        print(f"\n{p.get('rank_label', f'#{idx+1}')}: {p.get('brand')} {p.get('title')}")
        print(f"Price: ₹{p.get('price'):,} | Score: {p.get('score')}/100")
        print("Why:")
        for r in p.get("why_recommended", []):
            print(f"  {r}")
            assert r.startswith("✓"), "Why reasons must start with ✓"
            
    print("✓ Top 2 recommendations verified successfully!")


def test_out_of_budget_fallback():
    print("\n--- 6. Testing Out of Budget Smart Fallback ---")
    res = search_products("Laptop under 10000", category="Electronics", subcategory="Laptop", budget=10000.0, top_k=2)
    assert not res.success, "Should report no products within ₹10,000 budget"
    assert len(res) == 0, "No products should be returned in product list"
    assert "Sorry, I couldn't find any matching products under ₹10,000" in res.message
    assert "Closest options:" in res.message
    assert "Would you like to:" in res.message
    print("Fallback Message Output:")
    print(res.message)
    print("✓ Out of budget fallback verified successfully!")


if __name__ == "__main__":
    test_brand_scores()
    test_budget_scoring()
    test_review_scoring()
    test_strict_query_relevance()
    test_top_2_recommendations()
    test_out_of_budget_fallback()
    print("\n========================================================")
    print("ALL INTELLIGENT RANKING ENGINE TESTS PASSED SUCCESSFULLY!")
    print("========================================================")
