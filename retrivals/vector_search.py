"""
Semantic search at query time — embeds the user's query text and
searches the FAISS index built by embeddings.py, returning matching
product ids in similarity order.

catalog.py imports semantic_search() and merges these ids into the
structured results. If no index exists yet for a category (embeddings.py
hasn't been run for it), this raises FileNotFoundError, which
catalog.py catches and treats as "structured search only" — a missing
index is a normal, expected state early in the project, not an error
to crash on.
"""

import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

_index_cache: dict = {}
_ids_cache: dict = {}
_model = None


def _get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        from retrivals.embeddings import MODEL_NAME
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def _load_index(category_slug: str):
    import faiss

    if category_slug not in _index_cache:
        index_path = DATA_DIR / f"{category_slug}_faiss.index"
        ids_path = DATA_DIR / f"{category_slug}_ids.json"
        if not index_path.exists() or not ids_path.exists():
            raise FileNotFoundError(f"No FAISS index for '{category_slug}' yet — run embeddings.py first")

        _index_cache[category_slug] = faiss.read_index(str(index_path))
        with open(ids_path, "r", encoding="utf-8") as f:
            _ids_cache[category_slug] = json.load(f)

    return _index_cache[category_slug], _ids_cache[category_slug]


def semantic_search(category: str, query_text: str, top_k: int = 10) -> list[str]:
    import numpy as np
    from backend.models.product import category_slug as slugify

    if not query_text.strip():
        return []

    index, ids = _load_index(slugify(category))
    model = _get_model()
    vector = np.asarray(model.encode([query_text], normalize_embeddings=True), dtype="float32")

    scores, positions = index.search(vector, min(top_k, len(ids)))
    return [ids[i] for i in positions[0] if i != -1]
