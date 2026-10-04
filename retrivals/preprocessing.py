"""
Preprocessing — turns a raw dataset (any of the CSVs the team collected)
into the generic product schema defined in backend/models/product.py,
and writes one JSON catalog file per category into data/, named
"<category_lower>_catalog.json" so backend/services/catalog.py can
load them directly with zero extra wiring.

This is the "Data cleaning and normalization" box in the architecture
doc. Whatever real-time source replaces the CSV later (a product API,
a scheduled scrape of a permitted feed, a manually refreshed sheet),
it only needs to produce a DataFrame with recognisable columns and
call `normalize_and_save()` below — nothing else in the project needs
to change.

Currently wired up: the Flipkart sample dataset (flipkart.csv).
Add a `load_<source>()` function the same shape as `load_flipkart()`
for each new source (Amazon 30k data, products.csv, dataset.csv) —
they just need to end up as a DataFrame with the same target columns.
"""

import json
import re
from pathlib import Path
from datetime import datetime, timezone

import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

# Cap how many rows we keep per category. The full Flipkart sample has
# ~10k rows per category — plenty for a real catalog, but slow to
# embed and re-index for a college prototype demo. Raise or remove
# this once you're ready to run the full pipeline.
MAX_ROWS_PER_CATEGORY = 150


def _clean_price(value) -> float:
    if pd.isna(value):
        return 0.0
    if isinstance(value, str):
        value = re.sub(r"[^\d.]", "", value)
        return float(value) if value else 0.0
    return float(value)


def load_flipkart(path: str) -> pd.DataFrame:
    """Load and map flipkart.csv into the generic schema's column names."""
    df = pd.read_csv(path)

    out = pd.DataFrame({
        "id": df["product_id"],
        "category": df["category"],
        "brand": df["brand"],
        "title": df["product_name"],
        "price": df["final_price"].apply(_clean_price),
        "rating": df["rating"],
        "availability": df["stock_available"].apply(lambda n: "In stock" if n and n > 0 else "Out of stock"),
        "image_url": "",
        "product_url": "",
        "source": "Flipkart (sample dataset)",
        "last_updated": df["listing_date"],
    })

    # Everything else becomes part of the flexible specs dict, grounded
    # in whatever the source actually provided — never invented.
    spec_cols = ["color", "size", "warranty_months", "weight_g", "delivery_days",
                 "return_policy_days", "payment_modes", "seller", "seller_city",
                 "units_sold", "review_count"]
    out["specs"] = df[spec_cols].apply(
        lambda row: {k: v for k, v in row.items() if pd.notna(v) and v != ""},
        axis=1,
    )

    return out


def normalize_and_save(df: pd.DataFrame, max_per_category: int = MAX_ROWS_PER_CATEGORY) -> dict:
    """
    Validate rows against the Product schema, sample per category, and
    write one <category>_catalog.json per category. Rows that fail
    validation are dropped and counted rather than silently coerced —
    that count is worth checking after a real-source ingestion run.
    """
    # Import here (not at module top) so this file has no hard
    # dependency on the backend package layout when run standalone.
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from backend.models.product import Product, category_slug

    DATA_DIR.mkdir(exist_ok=True)
    written = {}
    dropped = 0

    for category, group in df.groupby("category"):
        sample = group.head(max_per_category)
        records = []
        for _, row in sample.iterrows():
            try:
                product = Product(**row.to_dict())
                records.append(json.loads(product.model_dump_json()))
            except Exception:
                dropped += 1
                continue

        out_path = DATA_DIR / f"{category_slug(str(category))}_catalog.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(records, f, indent=2)
        written[category] = {"count": len(records), "file": out_path.name}

    return {"written": written, "dropped": dropped, "generated_at": datetime.now(timezone.utc).isoformat()}


if __name__ == "__main__":
    # Example: python retrivals/preprocessing.py /path/to/flipkart.csv
    import sys
    csv_path = sys.argv[1] if len(sys.argv) > 1 else "flipkart.csv"
    df = load_flipkart(csv_path)
    summary = normalize_and_save(df)
    print(json.dumps(summary, indent=2))
