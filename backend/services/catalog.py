"""
Catalog service — loads product records and retrieves candidates.

Structured path: reads data/<category_slug>_catalog.json (produced by
retrivals/preprocessing.py from the real dataset) and filters by
budget/availability. This is the "OpenSearch" side of the hybrid
retrieval layer in the architecture doc.

Semantic path: if a FAISS index exists for the category (built by
retrivals/embeddings.py), search() blends in semantically similar
products even when they don't pass the hard budget filter, then lets
ranking/rerankar.py sort the combined set. If no index has been built
yet, it falls back to the structured filter alone — the pipeline
degrades gracefully rather than failing.
"""

import json
from pathlib import Path
from backend.models.product import Product, category_slug

POSSIBLE_DATA_DIRS = [
    Path(__file__).resolve().parent.parent.parent / "data",
    Path(__file__).resolve().parent.parent / "data",
    Path.cwd() / "data",
    Path("C:/project folders/genai-shopping-assistant/genai-shopping-assistant/data"),
]
DATA_DIR = next((d for d in POSSIBLE_DATA_DIRS if d.exists()), POSSIBLE_DATA_DIRS[0])


def get_catalog(category: str) -> list[Product]:
    slug = category_slug(category)
    master_path = DATA_DIR / "master_catalog.csv"
    if master_path.exists():
        import pandas as pd
        df = pd.read_csv(master_path).fillna("")
        slug_clean = slug.lower().replace("_and_", " ").replace("&", " ").replace("_", " ").strip()
        cat_col = df["category"].astype(str).str.lower().str.replace("&", " ").str.replace("_", " ").str.strip()
        matched = df[cat_col == slug_clean]
        if matched.empty:
            matched = df[df["subcategory"].astype(str).str.lower() == slug_clean]
        if not matched.empty:
            prods = []
            for _, row in matched.iterrows():
                prods.append(Product(
                    id=str(row.get("product_id") or row.get("id")),
                    category=str(row["category"]),
                    brand=str(row["brand"]),
                    title=str(row["title"]),
                    price=float(row["price"]),
                    rating=float(row["rating"]) if row.get("rating") else None,
                    description=str(row.get("description", "")),
                    image_url=str(row.get("image_url", "")),
                    source=str(row.get("source", "Real Catalog")),
                ))
            return prods

    path = DATA_DIR / f"{slug}_catalog.json"
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)
        return [Product(**item) for item in raw]

    return []


def search(category: str, budget_max: float | None, query_text: str = "") -> list[Product]:
    catalog = get_catalog(category)
    by_id = {p.id: p for p in catalog}

    # Structured filter (always available)
    if budget_max is not None:
        structured = [p for p in catalog if p.price <= budget_max]
    else:
        structured = list(catalog)

    # Semantic candidates (only if an index has been built for this
    # category — see retrivals/embeddings.py). Merged in even if they
    # miss the hard budget cutoff, since a great match slightly over
    # budget is often worth showing rather than silently dropping.
    try:
        from retrivals.vector_search import semantic_search
        semantic_ids = semantic_search(category, query_text, top_k=10)
        for pid in semantic_ids:
            if pid in by_id and by_id[pid] not in structured:
                structured.append(by_id[pid])
    except Exception:
        pass  # no index built yet for this category — structured-only is fine

    return structured if structured else catalog
