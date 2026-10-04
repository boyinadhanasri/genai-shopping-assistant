from backend.models.product import Product, QuerySlots
from ranking.scoring import score_product
from ranking.rerankar import rerank


def make_product(id, price, rating, availability="In stock"):
    return Product(id=id, category="Mobiles", brand="Sony", title=f"Phone {id}",
                   price=price, rating=rating, availability=availability)


def test_over_budget_scores_lower_than_within_budget():
    slots = QuerySlots(category="Mobiles", budget_max=20000, raw_query="phone under 20000")
    within = make_product("a", 18000, 4.5)
    over = make_product("b", 30000, 4.5)
    assert score_product(within, slots) > score_product(over, slots)


def test_out_of_stock_scores_lower_than_in_stock():
    slots = QuerySlots(category="Mobiles", budget_max=None, raw_query="a phone")
    in_stock = make_product("a", 15000, 4.0, availability="In stock")
    out_of_stock = make_product("b", 15000, 4.0, availability="Out of stock")
    assert score_product(in_stock, slots) > score_product(out_of_stock, slots)


def test_rerank_sorts_best_first_and_respects_top_k():
    slots = QuerySlots(category="Mobiles", budget_max=20000, raw_query="phone under 20000")
    products = [
        make_product("cheap_low_rating", 5000, 2.0),
        make_product("best_fit", 18000, 4.8),
        make_product("over_budget", 30000, 4.9),
    ]
    ranked = rerank(products, slots, top_k=2)
    assert len(ranked) == 2
    assert ranked[0].id == "best_fit"
