"""
Intelligent Hybrid Search & Ranking Engine 2.0 for GenAI Shopping Assistant

Search & Ranking Flow:
Step 1: Strict Category filter (Home & Kitchen, Books, Sports, Laptops, Smartphones, Fashion, etc.)
Step 2: Strict Subcategory / Product type filter (FILTER FIRST BEFORE RANKING!)
Step 3: Strict Budget filter (MUST happen BEFORE ranking! product.price <= user_budget)
Step 4: Product Ranking 2.0 (40% Query Match + 20% Rating + 15% Review Count + 10% Brand + 10% Budget Fit + 5% Popularity)
Step 5: Strictly Top 2 Recommendation Selection (#1 Top Recommendation, #2 Runner Up)
Step 6: Smart No-Results / Closest-Match response if 0 products match budget
"""

import os
import sys
import math
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd

from backend.ranking.ranker import (
    calculate_product_score,
    generate_why_recommended,
    ProductRanker,
    PRODUCT_TYPE_KEYWORDS,
)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

MODEL_NAME = "all-MiniLM-L6-v2"

# Detect project data directory reliably across working directories
POSSIBLE_DATA_DIRS = [
    Path(__file__).resolve().parent.parent / "data",
    Path.cwd() / "data",
    Path("C:/project folders/genai-shopping-assistant/genai-shopping-assistant/data"),
]
DATA_DIR = next((d for d in POSSIBLE_DATA_DIRS if d.exists()), POSSIBLE_DATA_DIRS[0])

# Cached singletons (lazy loaded on first request)
_index = None
_catalog_df: Optional[pd.DataFrame] = None
_model = None
_embeddings: Optional[np.ndarray] = None


PRODUCT_TYPE_SYNONYMS = {
    # Home & Kitchen
    "cookware": ["cookware", "fry pan", "frying pan", "kadai", "pan", "tawa", "skillet", "saucepan", "pot"],
    "kitchen appliances": ["kitchen appliance", "appliance", "toaster", "kettle", "electric kettle", "induction", "blender", "hand blender", "juicer"],
    "air fryers": ["air fryer", "air fryers", "airfryer"],
    "air fryer": ["air fryer", "air fryers", "airfryer"],
    "mixer grinders": ["mixer grinder", "mixer grinders", "mixer", "grinder", "juicer mixer"],
    "mixer grinder": ["mixer grinder", "mixer grinders", "mixer", "grinder", "juicer mixer"],
    "cookers": ["cooker", "cookers", "pressure cooker", "rice cooker"],
    "cooker": ["cooker", "cookers", "pressure cooker", "rice cooker"],
    "coffee makers": ["coffee maker", "espresso", "french press", "coffee machine"],
    "coffee maker": ["coffee maker", "espresso", "french press", "coffee machine"],
    "storage containers": ["storage container", "container", "containers", "jar", "jars", "spice container", "food container"],
    "storage container": ["storage container", "container", "containers", "jar", "jars", "spice container", "food container"],
    "water bottles": ["water bottle", "water bottles", "bottle", "bottles", "flask", "sipper", "thermos"],
    "water bottle": ["water bottle", "water bottles", "bottle", "bottles", "flask", "sipper", "thermos"],
    "dinner sets": ["dinner set", "dinner sets", "plate set", "plates", "bowls", "cutlery", "tableware"],
    "dinner set": ["dinner set", "dinner sets", "plate set", "plates", "bowls", "cutlery", "tableware"],
    "cleaning supplies": ["cleaning supply", "cleaning supplies", "mop", "spin mop", "microfiber", "vacuum cleaner", "broom"],
    "cleaning supply": ["cleaning supply", "cleaning supplies", "mop", "spin mop", "microfiber", "vacuum cleaner", "broom"],
    "home decor": ["home decor", "decor", "vase", "flower vase", "wall art", "painting", "candle", "candles", "sofa cover", "cushion cover"],
    "furniture": ["furniture", "study desk", "desk", "chair", "table", "coffee table", "recliner", "bookshelf"],
    "bedsheets": ["bedsheet", "bedsheets", "bed sheet", "bed cover", "bed linen"],
    "bedsheet": ["bedsheet", "bedsheets", "bed sheet", "bed cover", "bed linen"],
    "curtains": ["curtain", "curtains", "window curtain", "door curtain", "drapes", "sheer curtain"],
    "curtain": ["curtain", "curtains", "window curtain", "door curtain", "drapes", "sheer curtain"],
    "lighting": ["lighting", "lamp", "lamps", "table lamp", "ceiling light", "pendant light", "led light"],

    # Books
    "programming": ["programming", "python", "clean code", "coding", "java", "javascript", "c++", "grokking", "pragmatic"],
    "python": ["python", "python crash course", "automate the boring stuff", "fluent python"],
    "data science": ["data science", "statistics", "pandas", "numpy", "data analysis"],
    "ai & ml": ["machine learning", "deep learning", "artificial intelligence", "ai & ml", "neural network", "generative ai"],
    "business": ["business", "startup", "zero to one", "lean startup", "good to great", "blue ocean"],
    "finance": ["finance", "psychology of money", "rich dad poor dad", "intelligent investor", "stock market", "investing"],
    "self help": ["self help", "atomic habits", "ikigai", "subtle art", "mindset", "personal growth"],
    "productivity": ["productivity", "deep work", "getting things done", "make time", "7 habits"],
    "novels": ["novel", "novels", "fiction", "alchemist", "1984", "sapiens", "midnight library"],
    "academic": ["academic", "calculus", "university physics", "chemistry", "textbook"],
    "interview preparation": ["interview prep", "interview preparation", "cracking the coding interview", "system design interview", "elements of programming"],
    "upsc": ["upsc", "civil services", "laxmikanth", "polity", "spectrum history", "indian economy"],
    "gate": ["gate", "gate computer science", "gate exam"],
    "jee": ["jee", "iit", "hc verma", "concepts of physics", "irodov"],
    "neet": ["neet", "ncert biology", "biology neet", "trueman"],
    "book": ["book", "books", "novel", "programming", "guide", "paperback"],
    "books": ["book", "books", "novel", "programming", "guide", "paperback"],

    # Sports
    "cricket": ["cricket", "cricket bat", "bat", "cricket ball", "cricket kit", "cricket gloves", "cricket pads", "cricket helmet"],
    "football": ["football", "soccer", "fifa", "shin guard", "goalkeeper gloves"],
    "badminton": ["badminton", "badminton racket", "racket", "shuttlecock", "shuttle", "mavis 350", "yonex"],
    "gym equipment": ["gym equipment", "dumbbell", "dumbbells", "weights", "weight bench", "resistance band", "pull up bar", "kettlebell"],
    "running": ["running shoes", "running gear", "jogging", "marathon", "running"],
    "cycling": ["cycling", "cycle", "bicycle", "mountain bike", "cycling helmet", "cycle light"],
    "yoga": ["yoga", "yoga mat", "yoga block", "yoga strap", "meditation"],
    "swimming": ["swimming", "swimming goggles", "swim cap", "goggles", "kickboard"],
    "basketball": ["basketball", "basketball hoop", "basketball net", "spalding"],
    "tennis": ["tennis", "tennis racket", "tennis ball", "wilson"],

    # Laptops & Computers
    "laptops": ["laptop", "notebook", "vivobook", "macbook", "thinkpad", "inspiron", "aspire"],
    "laptop": ["laptop", "notebook", "vivobook", "macbook", "thinkpad", "inspiron", "aspire"],

    # Smartphones
    "smartphones": ["phone", "mobile", "smartphone", "galaxy", "iphone", "redmi", "oneplus", "xiaomi", "realme", "pixel"],
    "smartphone": ["phone", "mobile", "smartphone", "galaxy", "iphone", "redmi", "oneplus", "xiaomi", "realme", "pixel"],
    "phone": ["phone", "mobile", "smartphone", "galaxy", "iphone", "redmi", "oneplus", "xiaomi", "realme", "pixel"],
    "phones": ["phone", "mobile", "smartphone", "galaxy", "iphone", "redmi", "oneplus", "xiaomi", "realme", "pixel"],
    "mobiles": ["phone", "mobile", "smartphone", "galaxy", "iphone", "redmi", "oneplus", "xiaomi", "realme", "pixel"],
    "mobile": ["phone", "mobile", "smartphone", "galaxy", "iphone", "redmi", "oneplus", "xiaomi", "realme", "pixel"],

    # Audio & Wearables
    "wireless earbuds": ["earbud", "earbuds", "airdopes", "airpods", "earphones", "buds"],
    "earbuds": ["earbud", "earbuds", "airdopes", "airpods", "earphones", "buds"],
    "earbud": ["earbud", "earbuds", "airdopes", "airpods", "earphones", "buds"],
    "headphones": ["headphone", "headphones", "headset"],
    "headphone": ["headphone", "headphones", "headset"],
    "smartwatch": ["smartwatch", "smart watch", "watch", "watches", "colorfit", "wave call"],
    "smart watch": ["smartwatch", "smart watch", "watch", "watches", "colorfit", "wave call"],
    "tv": ["tv", "tvs", "television", "smart tv", "bravia", "crystal 4k"],
    "cameras": ["camera", "cameras", "dslr", "mirrorless", "eos", "alpha", "powershot", "lumix"],
    "camera": ["camera", "cameras", "dslr", "mirrorless", "eos", "alpha", "powershot", "lumix"],

    # Fashion & Shoes
    "shoes": ["shoe", "shoes", "sneaker", "sneakers", "boot", "boots", "footwear", "running shoes"],
    "shoe": ["shoe", "shoes", "sneaker", "sneakers", "boot", "boots", "footwear", "running shoes"],
    "jeans": ["jean", "jeans", "denim"],
    "jean": ["jean", "jeans", "denim"],
    "top": ["top", "tops", "tee", "tees", "t-shirt", "tshirt", "shirt", "polo", "tank", "tunic", "blouse"],
    "tops": ["top", "tops", "tee", "tees", "t-shirt", "tshirt", "shirt", "polo", "tank", "tunic", "blouse"],
    "shirt": ["shirt", "shirts", "polo", "top"],
    "t-shirt": ["tshirt", "t-shirt", "tee", "tees", "top"],

    # Beauty
    "face wash": ["face wash", "facewash", "cleanser", "skin cleanser"],
    "facewash": ["face wash", "facewash", "cleanser"],
    "moisturizer": ["moisturizer", "moisturiser", "cream", "lotion"],
    "sunscreen": ["sunscreen", "sunscreens", "sunblock", "spf"],
    "lipstick": ["lipstick", "lip stick", "lip color"],
    "perfume": ["perfume", "perfumes", "fragrance"],
}


class SearchResult(list):
    """
    List of product results that provides dictionary-like access and attributes
    for smart budget responses (success, message, suggestion, alternatives, etc.).
    """
    def __init__(
        self,
        products: Optional[List[Dict[str, Any]]] = None,
        success: bool = True,
        message: Optional[str] = None,
        suggestion: Optional[str] = None,
        alternatives: Optional[List[str]] = None,
        fallback: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(products or [])
        self.success = success
        self.message = message
        self.suggestion = suggestion
        self.alternatives = alternatives or []
        self.fallback = fallback or {}

    def get(self, key: str, default: Any = None) -> Any:
        if key == "success":
            return self.success
        if key == "message":
            return self.message
        if key == "suggestion":
            return self.suggestion
        if key == "alternatives":
            return self.alternatives
        if key == "products":
            return list(self)
        if key == "fallback":
            return self.fallback
        return default

    def __getitem__(self, item: Any) -> Any:
        if isinstance(item, str):
            return self.get(item)
        return super().__getitem__(item)

    def __contains__(self, item: Any) -> bool:
        if isinstance(item, str) and item in ["success", "message", "suggestion", "alternatives", "products", "fallback"]:
            return True
        return super().__contains__(item)

    def keys(self) -> List[str]:
        return ["success", "message", "suggestion", "alternatives", "products"]

    def items(self) -> List[Tuple[str, Any]]:
        return [
            ("success", self.success),
            ("message", self.message),
            ("suggestion", self.suggestion),
            ("alternatives", self.alternatives),
            ("products", list(self)),
        ]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "message": self.message,
            "suggestion": self.suggestion,
            "alternatives": self.alternatives,
            "products": list(self),
        }


def get_catalog() -> pd.DataFrame:
    """Loads and caches the master catalog DataFrame lazily upon first request."""
    global _catalog_df
    if _catalog_df is None:
        catalog_path = DATA_DIR / "master_catalog.csv"
        if not catalog_path.exists():
            raise FileNotFoundError(
                f"Master catalog not found at {catalog_path}. Run scripts/create_master_catalog.py first."
            )
        _catalog_df = pd.read_csv(catalog_path).fillna("")
        if "id" not in _catalog_df.columns and "product_id" in _catalog_df.columns:
            _catalog_df["id"] = _catalog_df["product_id"]
        elif "product_id" not in _catalog_df.columns and "id" in _catalog_df.columns:
            _catalog_df["product_id"] = _catalog_df["id"]
    return _catalog_df


def get_model():
    """Loads and caches SentenceTransformer model lazily only when vector search is invoked."""
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def get_faiss_index():
    """Loads and caches FAISS index lazily upon first vector search."""
    global _index
    if _index is None:
        import faiss
        faiss_path = DATA_DIR / "faiss.index"
        products_index_path = DATA_DIR / "products.index"
        idx_file = faiss_path if faiss_path.exists() else products_index_path
        if not idx_file.exists():
            raise FileNotFoundError(
                f"FAISS index not found at {idx_file}. Run scripts/train_embeddings.py first."
            )
        _index = faiss.read_index(str(idx_file))
    return _index


def get_embeddings() -> np.ndarray:
    """Loads and caches pre-computed embeddings array lazily upon first search."""
    global _embeddings
    if _embeddings is None:
        embeddings_path = DATA_DIR / "embeddings.npy"
        if embeddings_path.exists():
            _embeddings = np.load(str(embeddings_path))
        else:
            cat = get_catalog()
            _embeddings = np.zeros((len(cat), 384), dtype=np.float32)
    return _embeddings


def get_search_engine():
    """Returns the lazy-loaded search engine components."""
    return {
        "catalog": get_catalog(),
        "model": get_model(),
        "index": get_faiss_index(),
        "embeddings": get_embeddings(),
    }


def load_index():
    """Backwards-compatible wrapper that loads FAISS index, catalog DataFrame, and model."""
    return get_faiss_index(), get_catalog(), get_model()


def find_closest_products(
    category: Optional[str] = None,
    subcategory: Optional[str] = None,
    budget: Optional[float] = None,
    limit: int = 2
) -> List[Dict[str, Any]]:
    """
    Finds products in the EXACT same subcategory (or category if no subcategory),
    sorted by price ascending, nearest above the budget limit.
    NEVER returns products from an unrelated subcategory or random fallbacks.
    """
    catalog = get_catalog()
    if catalog is None or len(catalog) == 0:
        return []


    candidates = catalog.copy()

    # Step 1: Subcategory filtering (STRICT)
    if subcategory and subcategory.strip():
        sub_lower = subcategory.strip().lower()
        search_terms = PRODUCT_TYPE_SYNONYMS.get(sub_lower, [sub_lower, sub_lower.rstrip("s")])
        search_terms_set = set(t.lower() for t in search_terms)
        search_terms_set.add(sub_lower)

        if "subcategory" in candidates.columns:
            sub_col_mask = candidates["subcategory"].astype(str).str.lower().apply(
                lambda s: s in search_terms_set or any(t == s or t in s for t in search_terms_set)
            )
            if sub_col_mask.any():
                candidates = candidates[sub_col_mask]
            else:
                sub_title_mask = pd.Series(False, index=candidates.index)
                for term in search_terms_set:
                    sub_title_mask = sub_title_mask | candidates["title"].astype(str).str.lower().str.contains(term, regex=False)
                candidates = candidates[sub_title_mask] if sub_title_mask.any() else pd.DataFrame()
        else:
            sub_title_mask = pd.Series(False, index=candidates.index)
            for term in search_terms_set:
                sub_title_mask = sub_title_mask | candidates["title"].astype(str).str.lower().str.contains(term, regex=False)
            candidates = candidates[sub_title_mask] if sub_title_mask.any() else pd.DataFrame()

    elif category and category.strip().lower() not in ["all", "any", "general"]:
        cat_lower = category.strip().lower()
        cat_mask = candidates["category"].astype(str).str.lower().apply(
            lambda c: c == cat_lower or c.replace(" & ", "_and_").replace(" ", "_") == cat_lower.replace(" & ", "_and_").replace(" ", "_")
        )
        if cat_mask.any():
            candidates = candidates[cat_mask]

    if candidates.empty:
        return []

    # Sort ascending by price: nearest above budget first
    if budget is not None and budget > 0:
        above_budget = candidates[candidates["price"] > budget].sort_values(by="price", ascending=True)
        if not above_budget.empty:
            candidates = above_budget
        else:
            candidates = candidates.sort_values(by="price", ascending=True)
    else:
        candidates = candidates.sort_values(by="price", ascending=True)

    results = []
    for _, row in candidates.head(limit).iterrows():
        prod_id = str(row.get("product_id") or row.get("id"))
        results.append({
            "id": prod_id,
            "product_id": prod_id,
            "brand": str(row.get("brand", "")),
            "title": str(row.get("title", "")),
            "category": str(row.get("category", "")),
            "subcategory": str(row.get("subcategory", "")),
            "price": float(row.get("price", 0.0)),
            "rating": float(row.get("rating", 0.0)),
            "image_url": str(row.get("image_url", "")),
            "description": str(row.get("description", "")),
        })
    return results


def get_budget_fallback(
    category: Optional[str] = None,
    subcategory: Optional[str] = None,
    budget: Optional[float] = None
) -> Dict[str, Any]:
    """
    Builds structured smart fallback response when 0 products match the requested budget.
    STRICT USER REQUIREMENT (Phase 7):
    Sorry, I couldn't find any products matching your budget.

    Closest options:
    • Product A – ₹Y
    • Product B – ₹Z

    Would you like to:
    1. Increase budget
    2. View closest matches
    3. Explore another category
    """
    closest_items = find_closest_products(category=category, subcategory=subcategory, budget=budget, limit=2)

    budget_val = int(budget) if budget else 0
    budget_formatted = f"₹{budget_val:,}"

    if closest_items:
        closest_lines = []
        for item in closest_items:
            brand_val = item.get("brand", "").strip()
            title_val = item.get("title", "").strip()
            price_val = int(item.get("price", 0))
            if title_val.lower().startswith(brand_val.lower()):
                display_name = title_val
            else:
                display_name = f"{brand_val} {title_val}"
            if len(display_name) > 40:
                display_name = display_name[:40].strip() + "..."
            closest_lines.append(f"• {display_name} – ₹{price_val:,}")

        closest_text = "\n".join(closest_lines)
        min_closest_price = math.ceil(closest_items[0]["price"])
        raw_cat = (subcategory or category or "products").strip().lower()
        cat_plural = raw_cat if raw_cat.endswith("s") else f"{raw_cat}s"
        if "phone" in cat_plural:
            cat_plural = "smartphones"

        message = (
            f"Sorry, I couldn't find any matching products under {budget_formatted} (No {cat_plural} found under {budget_formatted}).\n\n"
            f"Closest options:\n"
            f"{closest_text}\n\n"
            f"Would you like to:\n"
            f"1. Increase budget\n"
            f"2. View closest matches\n"
            f"3. Explore another category"
        )
        suggestion = f"Lowest available {raw_cat} is ₹{min_closest_price:,}. Closest options start at ₹{min_closest_price:,}."
        alternatives = [
            f"Increase budget to ₹{min_closest_price:,}",
            "View closest matches",
            "Explore another category",
        ]
    else:
        raw_cat = (subcategory or category or "products").strip().lower()
        cat_plural = raw_cat if raw_cat.endswith("s") else f"{raw_cat}s"
        if "phone" in cat_plural:
            cat_plural = "smartphones"
        message = (
            f"Sorry, I couldn't find any matching products under {budget_formatted} (No {cat_plural} found under {budget_formatted}).\n\n"
            f"Would you like to:\n"
            f"1. Increase budget\n"
            f"2. View closest matches\n"
            f"3. Explore another category"
        )
        suggestion = "Try increasing your budget or exploring another category."
        alternatives = [
            f"Increase budget to ₹{int(budget * 1.5):,}" if budget else "Increase budget",
            "Explore another category",
        ]



    return {
        "success": False,
        "message": message,
        "suggestion": suggestion,
        "alternatives": alternatives,
        "reply": message,
        "cheapest_product": closest_items[0] if closest_items else None,
        "closest_products": closest_items,
    }


def search_products(
    query: str,
    top_k: int = 2,
    category: Optional[str] = None,
    brand: Optional[str] = None,
    budget: Optional[float] = None,
    min_rating: Optional[float] = None,
    subcategory: Optional[str] = None,
) -> SearchResult:
    """
    Intelligent Product Ranking Search Engine 2.0.
    Strictly returns the TOP 2 BEST PRODUCTS (#1 Top Recommendation, #2 Runner Up).
    Never ranks products outside user budget.
    Applies 6-part weighted scoring engine (40% query match, 20% rating, 15% reviews, 10% brand, 10% budget, 5% popularity).
    """
    catalog = get_catalog()
    if len(catalog) == 0:
        return SearchResult([], success=True)

    # Clean query string
    search_query = (query or "").strip()
    if not search_query and not category and not brand and not subcategory:
        return SearchResult([], success=True)

    if not search_query:
        search_query = subcategory or category or brand or "products"

    # Infer missing attributes from query if not explicitly passed
    if category is None or subcategory is None or (budget is None and search_query):
        try:
            from backend.ai.query_understanding import understand_query
            parsed = understand_query(search_query, category_hint=category)
            if category is None:
                category = parsed.get("category")
            if subcategory is None:
                subcategory = parsed.get("subcategory")
            if budget is None and parsed.get("budget") is not None:
                budget = parsed.get("budget")
            if brand is None and parsed.get("brand"):
                brand = parsed.get("brand")
        except Exception:
            pass

    # =========================================================================
    # STEP 1: CATEGORY FILTER
    # =========================================================================
    filtered_indices = catalog.index.tolist()

    if category and category.strip().lower() not in ["all", "any", "general"]:
        cat_lower = category.strip().lower()
        cat_mask = catalog["category"].astype(str).str.lower().apply(
            lambda c: c == cat_lower or c.replace(" & ", "_and_").replace(" ", "_") == cat_lower.replace(" & ", "_and_").replace(" ", "_")
        )
        if cat_mask.any():
            filtered_indices = catalog[cat_mask].index.tolist()
        else:
            cat_sub_mask = catalog["category"].astype(str).str.lower().str.contains(cat_lower, regex=False)
            if cat_sub_mask.any():
                filtered_indices = catalog[cat_sub_mask].index.tolist()

    # =========================================================================
    # STEP 2: STRICT PRODUCT TYPE / SUBCATEGORY FILTER (BEFORE RANKING!)
    # =========================================================================
    if subcategory and subcategory.strip():
        sub_lower = subcategory.strip().lower()
        search_terms = PRODUCT_TYPE_SYNONYMS.get(sub_lower, [sub_lower, sub_lower.rstrip("s")])
        search_terms_set = set(t.lower() for t in search_terms)
        search_terms_set.add(sub_lower)

        # 1. Match against catalog['subcategory'] column if available
        matched_indices = []
        if "subcategory" in catalog.columns:
            sub_col_mask = catalog.loc[filtered_indices, "subcategory"].astype(str).str.lower().apply(
                lambda s: s in search_terms_set or any(t == s or t in s for t in search_terms_set)
            )
            if sub_col_mask.any():
                matched_indices = catalog.loc[filtered_indices][sub_col_mask].index.tolist()

        # 2. Match against title keyword if subcategory column produced 0 matches
        if not matched_indices:
            sub_title_mask = pd.Series(False, index=filtered_indices)
            for term in search_terms_set:
                sub_title_mask = sub_title_mask | catalog.loc[filtered_indices, "title"].astype(str).str.lower().str.contains(term, regex=False)
            if sub_title_mask.any():
                matched_indices = catalog.loc[filtered_indices][sub_title_mask].index.tolist()
            else:
                # Also check catalog-wide for this subcategory if category was overly restrictive
                if "subcategory" in catalog.columns:
                    catwide_mask = catalog["subcategory"].astype(str).str.lower().apply(
                        lambda s: s in search_terms_set or any(t == s or t in s for t in search_terms_set)
                    )
                    if catwide_mask.any():
                        matched_indices = catalog[catwide_mask].index.tolist()

        filtered_indices = matched_indices

    # Brand Filtering if specified
    if brand and brand.strip() and filtered_indices:
        brand_lower = brand.strip().lower()
        brand_mask = catalog.loc[filtered_indices, "brand"].astype(str).str.lower().str.contains(brand_lower, regex=False)
        if brand_mask.any():
            filtered_indices = catalog.loc[filtered_indices][brand_mask].index.tolist()

    # Min Rating Filtering if specified
    if min_rating is not None and min_rating > 0 and filtered_indices:
        rating_mask = catalog.loc[filtered_indices, "rating"] >= min_rating
        if rating_mask.any():
            filtered_indices = catalog.loc[filtered_indices][rating_mask].index.tolist()

    # Record candidates before budget filter
    products_candidates = catalog.loc[filtered_indices] if filtered_indices else pd.DataFrame(columns=catalog.columns)

    # =========================================================================
    # STEP 3: BUDGET FILTER (Strictly BEFORE ranking! product.price <= user_budget)
    # =========================================================================
    if budget is not None and budget > 0:
        if not products_candidates.empty:
            budget_mask = products_candidates["price"] <= (budget + 0.99)
            filtered = products_candidates[budget_mask]
            filtered_indices = filtered.index.tolist()
        else:
            filtered = pd.DataFrame(columns=catalog.columns)
            filtered_indices = []
    else:
        filtered = products_candidates
        filtered_indices = filtered.index.tolist() if not filtered.empty else []

    # Mandatory logging:
    print(f"Ranking Engine: Budget={budget} | Candidates before budget={len(products_candidates)} | Candidates within budget={len(filtered)}")

    # If matching products count == 0:
    # Never recommend products outside the requested budget or random fallback.
    if len(filtered) == 0:
        fallback = get_budget_fallback(
            category=category,
            subcategory=subcategory,
            budget=budget
        )
        return SearchResult(
            products=[],
            success=False,
            message=fallback["message"],
            suggestion=fallback["suggestion"],
            alternatives=fallback["alternatives"],
            fallback=fallback
        )

    # =========================================================================
    # STEP 4: SEMANTIC SIMILARITY COMPUTATION (Lazy-loaded Model & Embeddings)
    # =========================================================================
    model = get_model()
    embeddings = get_embeddings()

    query_vector = model.encode([search_query], normalize_embeddings=True)
    query_vector = np.asarray(query_vector, dtype=np.float32)

    if embeddings is None or len(embeddings) != len(catalog):
        embeddings = model.encode(
            (catalog["title"] + " " + catalog["brand"] + " " + catalog["category"] + " " + catalog["description"]).tolist(),
            normalize_embeddings=True
        )
        embeddings = np.asarray(embeddings, dtype=np.float32)
        global _embeddings
        _embeddings = embeddings

    candidate_vectors = embeddings[filtered_indices]
    sim_scores = np.dot(candidate_vectors, query_vector.T).flatten()

    raw_candidates: List[Dict[str, Any]] = []

    for cat_idx, sim in zip(filtered_indices, sim_scores):
        row = catalog.iloc[cat_idx]
        prod_cat = str(row.get("category", "")).strip()
        prod_sub = str(row.get("subcategory", "")).strip()
        prod_brand = str(row.get("brand", "")).strip()
        prod_price = float(row.get("price", 0.0))
        prod_rating = float(row.get("rating", 4.0))

        prod_id = str(row.get("id") or row.get("product_id") or "")
        prod_dict = {
            "id": prod_id,
            "product_id": prod_id,
            "title": str(row.get("title", "")),
            "brand": prod_brand,
            "category": prod_cat,
            "subcategory": prod_sub,
            "price": prod_price,
            "rating": prod_rating,
            "description": str(row.get("description", "")),
            "image_url": str(row.get("image_url", "")),
            "source": str(row.get("source", "Real Catalog")),
            "specs": {},
            "availability": "In stock",
            "discount_percent": int(row.get("discount_percent", 0) or 0),
            "review_count": float(row.get("review_count", 0) or 0),
            "units_sold": float(row.get("units_sold", 0) or 0),
        }

        raw_candidates.append({
            "product": prod_dict,
            "semantic_score": float(max(0.0, min(1.0, float(sim)))),
        })

    # =========================================================================
    # STEP 5: 6-FACTOR INTELLIGENT PRODUCT RANKING (Strict TOP 2 only)
    # =========================================================================
    ranked_results = ProductRanker.rank_candidates(
        candidates=raw_candidates,
        budget=budget,
        query_type=subcategory,
        raw_query=search_query,
        max_results=2  # STRICTLY TOP 2 PRODUCTS ONLY!
    )

    if not ranked_results:
        fallback = get_budget_fallback(
            category=category,
            subcategory=subcategory,
            budget=budget
        )
        return SearchResult(
            products=[],
            success=False,
            message=fallback["message"],
            suggestion=fallback["suggestion"],
            alternatives=fallback["alternatives"],
            fallback=fallback
        )

    # Return SearchResult containing strictly top 2 products
    return SearchResult(ranked_results[:2], success=True)


search = search_products
find_cheapest_product = find_closest_products
