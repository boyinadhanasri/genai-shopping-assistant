"""
Intent & slot extraction — turns a free-text query into structured
slots: category, budget ceiling, brand (if named), and leftover text
to hand to semantic search.

This rule-based version is what actually runs today. It's deliberately
simple so the whole pipeline is demoable and debuggable without an API
key. llm_parser.py in this same folder is the drop-in replacement that
calls GPT-4o mini with function-calling — swap CURRENT_PARSER at the
bottom of that file when you're ready, and nothing else in the project
needs to change (backend/services/intent.py already calls this module,
not the other way around).
"""

import re
from backend.models.product import QuerySlots

# Keep this in sync with the categories that actually exist in your
# catalog data (data/*_catalog.json) — these are the ones present in
# the Flipkart sample dataset.
CATEGORY_KEYWORDS = {
    "Electronics": ["tv", "television", "speaker", "headphone", "earbud", "camera", "electronics"],
    "Mobiles": ["phone", "mobile", "smartphone", "iphone"],
    "Appliances": ["fridge", "refrigerator", "washing machine", "microwave", "ac", "air conditioner", "appliance"],
    "Home & Kitchen": ["kitchen", "cookware", "mixer", "utensil", "home"],
    "Fashion": ["shirt", "dress", "shoe", "jeans", "jacket", "fashion", "wear"],
    "Beauty": ["makeup", "skincare", "shampoo", "beauty", "cosmetic"],
    "Sports": ["cricket", "football", "gym", "fitness", "sports", "bat", "ball"],
    "Toys": ["toy", "lego", "puzzle", "kids"],
}

KNOWN_BRANDS = ["Adidas", "Apple", "Boat", "Dell", "HP", "LG", "Nike", "Philips",
                "Prestige", "Puma", "Redmi", "Reebok", "Samsung", "Sony", "Whirlpool"]


def _detect_category(query: str, fallback: str) -> str:
    lowered = query.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(kw in lowered for kw in keywords):
            return category
    return fallback  # trust the category chip the user already selected in the UI


def _detect_brand(query: str) -> str | None:
    lowered = query.lower()
    for brand in KNOWN_BRANDS:
        if brand.lower() in lowered:
            return brand
    return None


def extract_slots(query: str, category_hint: str) -> QuerySlots:
    budget_max = None
    match = re.search(r"(\d[\d,]{2,})", query)
    if match:
        budget_max = float(match.group(1).replace(",", ""))

    category = _detect_category(query, fallback=category_hint)

    return QuerySlots(category=category, budget_max=budget_max, raw_query=query)


def detect_brand(query: str) -> str | None:
    return _detect_brand(query)
