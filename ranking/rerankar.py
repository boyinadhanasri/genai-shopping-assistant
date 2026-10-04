"""
Reranker backed by Intelligent Product Ranking Engine.
Returns strictly TOP 2 products with scores and Why Recommended badges.
"""

from typing import List
from backend.models.product import Product, QuerySlots
from backend.ranking.ranker import rank_products


def rerank(products: List[Product], slots: QuerySlots, top_k: int = 2) -> List[Product]:
    """
    Reranks candidates and returns strictly top 2 (or top_k) products.
    """
    if not products:
        return []
    
    candidates = []
    for p in products:
        candidates.append({
            "product": {
                "id": p.id,
                "product_id": p.id,
                "title": p.title,
                "brand": p.brand,
                "category": p.category,
                "price": p.price,
                "rating": p.rating,
                "description": p.description,
                "image_url": p.image_url,
                "source": p.source,
                "availability": p.availability,
                "discount_percent": p.discount_percent,
            }
        })
        
    ranked_dicts = rank_products(
        candidates=candidates,
        budget=slots.budget_max,
        raw_query=slots.raw_query,
        top_k=top_k
    )
    
    result = []
    for r in ranked_dicts:
        p_dict = r["product"]
        p_obj = Product(
            id=p_dict["id"],
            category=p_dict["category"],
            brand=p_dict["brand"],
            title=p_dict["title"],
            price=p_dict["price"],
            rating=p_dict.get("rating"),
            description=p_dict.get("description", ""),
            image_url=p_dict.get("image_url", ""),
            source=p_dict.get("source", "Real Catalog"),
            availability=p_dict.get("availability", "In stock"),
            discount_percent=p_dict.get("discount_percent"),
            badge=p_dict.get("badge"),
            why_recommended=p_dict.get("why_recommended", []),
            score=p_dict.get("score"),
            rank=p_dict.get("rank"),
            rank_label=p_dict.get("rank_label"),
        )
        result.append(p_obj)
        
    return result
