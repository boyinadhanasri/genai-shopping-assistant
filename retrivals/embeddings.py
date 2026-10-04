"""
Embeddings — turns each product's title + brand + specs into a vector
and builds a FAISS index per category, for the semantic half of the
hybrid retrieval layer.

Requires `sentence-transformers` and `faiss-cpu` (see requirements.txt)
and, the first time it runs, an internet connection to download the
model weights from Hugging Face. That download only needs to happen
once per machine — after that the model is cached locally.

Run this after retrivals/preprocessing.py has written the per-category
catalog JSON files:

    python retrivals/embeddings.py Electronics
    python retrivals/embeddings.py Mobiles
    ...or with no argument to build every catalog found in data/.
"""

import json
import sys
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
MODEL_NAME = "all-MiniLM-L6-v2"  # small, fast, good enough for a prototype

_model = None  # lazy-loaded singleton so importing this module is cheap


def _get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def _product_text(product: dict) -> str:
    """What actually gets embedded — grounded only in catalog fields."""
    spec_bits = " ".join(f"{k} {v}" for k, v in product.get("specs", {}).items())
    return f"{product['brand']} {product['title']} {spec_bits}".strip()


def build_index_for_category(category_slug: str) -> dict:
    import numpy as np
    import faiss

    catalog_path = DATA_DIR / f"{category_slug}_catalog.json"
    if not catalog_path.exists():
        raise FileNotFoundError(f"No catalog found at {catalog_path} — run preprocessing.py first")

    with open(catalog_path, "r", encoding="utf-8") as f:
        products = json.load(f)

    if not products:
        return {"category": category_slug, "indexed": 0}

    model = _get_model()
    texts = [_product_text(p) for p in products]
    vectors = model.encode(texts, normalize_embeddings=True)
    vectors = np.asarray(vectors, dtype="float32")

    index = faiss.IndexFlatIP(vectors.shape[1])  # cosine similarity via normalized inner product
    index.add(vectors)

    faiss.write_index(index, str(DATA_DIR / f"{category_slug}_faiss.index"))
    with open(DATA_DIR / f"{category_slug}_ids.json", "w", encoding="utf-8") as f:
        json.dump([p["id"] for p in products], f)

    return {"category": category_slug, "indexed": len(products)}


if __name__ == "__main__":
    if len(sys.argv) > 1:
        targets = [sys.argv[1].lower()]
    else:
        targets = [p.stem.replace("_catalog", "") for p in DATA_DIR.glob("*_catalog.json")]

    for slug in targets:
        print(json.dumps(build_index_for_category(slug), indent=2))
