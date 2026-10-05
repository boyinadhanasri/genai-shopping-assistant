"""
Scoring module backed by Intelligent Product Ranking Engine.
"""

from typing import Dict, Any, Optional
from backend.models.product import Product, QuerySlots
from backend.ranking.ranker import calculate_product_score, generate_why_recommended


def score_product(product: Product, slots: QuerySlots, semantic_rank_score: float = 0.85) -> float:
    """
    Computes weighted ranking score for a Product model.
    """
    prod_dict = {
        "price": product.price,
        "rating": product.rating,
        "brand": product.brand,
        "title": product.title,
        "category": product.category,
        "subcategory": getattr(product, "subcategory", ""),
        "availability": getattr(product, "availability", "In stock"),
    }
    res = calculate_product_score(
        product=prod_dict,
        budget=slots.budget_max,
        raw_query=slots.raw_query,
        semantic_sim=semantic_rank_score
    )
    score = res["final_score"] / 100.0
    if getattr(product, "availability", "").strip().lower() == "out of stock":
        score *= 0.5
    return score

