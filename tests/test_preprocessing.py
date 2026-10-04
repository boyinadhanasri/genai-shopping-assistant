import pandas as pd
from backend.models.product import Product, category_slug
from retrivals.preprocessing import load_flipkart, _clean_price


def test_category_slug_handles_ampersand_and_spaces():
    assert category_slug("Home & Kitchen") == "home_and_kitchen"
    assert category_slug("Mobiles") == "mobiles"


def test_clean_price_strips_currency_symbols():
    assert _clean_price("₹1,615") == 1615.0
    assert _clean_price(499.5) == 499.5


def test_product_schema_requires_core_fields():
    product = Product(
        id="p1", category="Mobiles", brand="Sony", title="Sony X",
        price=999.0, specs={"color": "black"},
    )
    assert product.rating is None
    assert product.specs["color"] == "black"


def test_load_flipkart_maps_expected_columns(tmp_path):
    sample = pd.DataFrame({
        "product_id": ["FKP1"],
        "product_name": ["Test Phone"],
        "category": ["Mobiles"],
        "brand": ["Sony"],
        "seller": ["ValueKart"],
        "seller_city": ["Mumbai"],
        "price": [15000.0],
        "discount_percent": [10],
        "final_price": [13500.0],
        "rating": [4.2],
        "review_count": [120],
        "stock_available": [5],
        "units_sold": [30],
        "listing_date": ["2024-01-01"],
        "delivery_days": [3],
        "weight_g": [180.0],
        "warranty_months": [12],
        "color": ["Black"],
        "size": ["N/A"],
        "return_policy_days": [7],
        "is_returnable": [True],
        "payment_modes": ["UPI,CARD"],
        "shipping_weight_g": [200.0],
        "product_score": [50.0],
        "seller_rating": [4.5],
    })
    csv_path = tmp_path / "sample.csv"
    sample.to_csv(csv_path, index=False)

    df = load_flipkart(str(csv_path))
    row = df.iloc[0]
    assert row["id"] == "FKP1"
    assert row["price"] == 13500.0
    assert row["availability"] == "In stock"
    assert row["specs"]["color"] == "Black"
