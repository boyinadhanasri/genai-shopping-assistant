"""
Train Embeddings & FAISS Index Pipeline

1. Load data/master_catalog.csv (Real products)
2. Generate combined_text = title + brand + category + description
3. Encode embeddings using sentence-transformers/all-MiniLM-L6-v2
4. Save:
   - data/faiss.index
   - data/product_metadata.pkl
   - data/products.index (alias for compatibility)
   - data/embeddings.npy
5. Verify index.ntotal == len(master_catalog)
"""

import os
import sys
import pickle
from pathlib import Path
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
import faiss

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
MODEL_NAME = "all-MiniLM-L6-v2"


def main():
    print("=" * 60)
    print("TRAINING FAISS EMBEDDINGS & PRODUCT METADATA")
    print("=" * 60)

    catalog_path = DATA_DIR / "master_catalog.csv"
    if not catalog_path.exists():
        raise FileNotFoundError(f"Catalog not found at {catalog_path}. Run create_master_catalog.py first.")

    df = pd.read_csv(catalog_path).fillna("")
    print(f"Loaded {len(df)} real products from {catalog_path}")

    # Create combined text = title + brand + category + description
    combined_text = (
        df["title"].astype(str)
        + " "
        + df["brand"].astype(str)
        + " "
        + df["category"].astype(str)
        + " "
        + df["description"].astype(str)
    ).str.strip().tolist()

    print(f"Sample combined text:\n{combined_text[0][:160]}...\n")

    # Generate embeddings
    print(f"Generating dense embeddings with SentenceTransformer('{MODEL_NAME}')...")
    model = SentenceTransformer(MODEL_NAME)
    embeddings = model.encode(
        combined_text,
        batch_size=64,
        show_progress_bar=True,
        normalize_embeddings=True
    )
    embeddings = np.array(embeddings, dtype=np.float32)
    dim = embeddings.shape[1]
    print(f"Generated embeddings matrix of shape: {embeddings.shape}")

    # Build FAISS Index (Inner Product on normalized vectors = Cosine Similarity)
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)
    print(f"Indexed {index.ntotal} products into FAISS IndexFlatIP")

    if index.ntotal != len(df):
        raise ValueError(f"FAISS index count mismatch: {index.ntotal} != {len(df)}")

    # 1. Save data/faiss.index
    faiss_path = DATA_DIR / "faiss.index"
    faiss.write_index(index, str(faiss_path))
    print(f"Saved FAISS index to {faiss_path}")

    # 2. Save data/products.index (for compatibility)
    products_index_path = DATA_DIR / "products.index"
    faiss.write_index(index, str(products_index_path))
    print(f"Saved products.index to {products_index_path}")

    # 3. Save data/product_metadata.pkl
    metadata = {
        "df": df,
        "ids": df["id"].tolist(),
        "categories": df["category"].tolist(),
        "brands": df["brand"].tolist(),
        "titles": df["title"].tolist(),
        "prices": df["price"].tolist(),
        "ratings": df["rating"].tolist(),
        "descriptions": df["description"].tolist(),
        "image_urls": df["image_url"].tolist(),
        "embedding_dim": dim,
        "total_products": len(df),
    }
    metadata_path = DATA_DIR / "product_metadata.pkl"
    with open(metadata_path, "wb") as f:
        pickle.dump(metadata, f)
    print(f"Saved product metadata to {metadata_path}")

    # 4. Save data/embeddings.npy
    npy_path = DATA_DIR / "embeddings.npy"
    np.save(str(npy_path), embeddings)
    print(f"Saved embeddings array to {npy_path}")

    print("\n" + "=" * 60)
    print("SUCCESS: All vector artifacts generated and verified successfully!")
    print(f"  - {faiss_path.name}")
    print(f"  - {metadata_path.name}")
    print(f"  - {products_index_path.name}")
    print(f"  - {npy_path.name}")
    print("=" * 60)


if __name__ == "__main__":
    main()
