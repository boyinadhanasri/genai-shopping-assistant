import pytest
from backend.models.product import Product
from comparison.comparison_engine import build_comparison


def test_comparison_requires_at_least_two_products():
    with pytest.raises(ValueError):
        build_comparison([Product(id="a", category="Mobiles", brand="Sony", title="X", price=100)])


def test_missing_spec_shown_as_not_specified_not_guessed():
    p1 = Product(id="a", category="Mobiles", brand="Sony", title="X", price=100,
                 specs={"battery": "4000 mAh"})
    p2 = Product(id="b", category="Mobiles", brand="Apple", title="Y", price=200,
                 specs={"color": "black"})  # no battery spec at all

    result = build_comparison([p1, p2])
    row_b = next(r for r in result["rows"] if r["id"] == "b")
    assert row_b["battery"] == "Not specified"
    assert "battery" in result["attributes"]
    assert "color" in result["attributes"]


def test_core_attributes_always_present():
    p1 = Product(id="a", category="Mobiles", brand="Sony", title="X", price=100)
    p2 = Product(id="b", category="Mobiles", brand="Apple", title="Y", price=200)
    result = build_comparison([p1, p2])
    for attr in ["Brand", "Price", "Rating", "Availability", "Source"]:
        assert attr in result["attributes"]
