"""
Category Budget Rules Configuration for ShopAI GenAI Shopping Assistant
Defines curated budget tiers, labels, and robust numerical parsing across all product categories.
"""

import re
from typing import Dict, List, Any, Optional

CATEGORY_BUDGET_TIERS: Dict[str, List[Dict[str, Any]]] = {
    "Home & Kitchen": [
        {"label": "Under ₹500", "value": 500.0, "is_max": True},
        {"label": "Under ₹1,000", "value": 1000.0, "is_max": True},
        {"label": "Under ₹2,500", "value": 2500.0, "is_max": True},
        {"label": "Under ₹5,000", "value": 5000.0, "is_max": True},
        {"label": "Under ₹10,000", "value": 10000.0, "is_max": True},
        {"label": "Premium", "value": None, "is_max": False},
    ],
    "Books": [
        {"label": "Under ₹200", "value": 200.0, "is_max": True},
        {"label": "Under ₹500", "value": 500.0, "is_max": True},
        {"label": "Under ₹1,000", "value": 1000.0, "is_max": True},
        {"label": "Premium", "value": None, "is_max": False},
    ],
    "Sports": [
        {"label": "Under ₹500", "value": 500.0, "is_max": True},
        {"label": "Under ₹1,500", "value": 1500.0, "is_max": True},
        {"label": "Under ₹3,000", "value": 3000.0, "is_max": True},
        {"label": "Under ₹5,000", "value": 5000.0, "is_max": True},
        {"label": "Premium", "value": None, "is_max": False},
    ],
    "Smartphones": [
        {"label": "Under ₹10,000", "value": 10000.0, "is_max": True},
        {"label": "Under ₹20,000", "value": 20000.0, "is_max": True},
        {"label": "Under ₹30,000", "value": 30000.0, "is_max": True},
        {"label": "Under ₹50,000", "value": 50000.0, "is_max": True},
        {"label": "Premium Flagships", "value": None, "is_max": False},
    ],
    "Laptops": [
        {"label": "Under ₹30,000", "value": 30000.0, "is_max": True},
        {"label": "Under ₹50,000", "value": 50000.0, "is_max": True},
        {"label": "Under ₹70,000", "value": 70000.0, "is_max": True},
        {"label": "Under ₹1 Lakh", "value": 100000.0, "is_max": True},
        {"label": "Premium Workstations", "value": None, "is_max": False},
    ],
    "Fashion": [
        {"label": "Under ₹500", "value": 500.0, "is_max": True},
        {"label": "Under ₹1,000", "value": 1000.0, "is_max": True},
        {"label": "Under ₹2,000", "value": 2000.0, "is_max": True},
        {"label": "Under ₹5,000", "value": 5000.0, "is_max": True},
        {"label": "Premium Fashion", "value": None, "is_max": False},
    ],
    "Beauty": [
        {"label": "Under ₹200", "value": 200.0, "is_max": True},
        {"label": "Under ₹500", "value": 500.0, "is_max": True},
        {"label": "Under ₹1,000", "value": 1000.0, "is_max": True},
        {"label": "Under ₹2,000", "value": 2000.0, "is_max": True},
        {"label": "Premium Beauty", "value": None, "is_max": False},
    ],
    "Electronics": [
        {"label": "Under ₹5,000", "value": 5000.0, "is_max": True},
        {"label": "Under ₹10,000", "value": 10000.0, "is_max": True},
        {"label": "Under ₹25,000", "value": 25000.0, "is_max": True},
        {"label": "Under ₹50,000", "value": 50000.0, "is_max": True},
        {"label": "Premium Flagships", "value": None, "is_max": False},
    ],
    "Cameras": [
        {"label": "Under ₹25,000", "value": 25000.0, "is_max": True},
        {"label": "Under ₹50,000", "value": 50000.0, "is_max": True},
        {"label": "Under ₹75,000", "value": 75000.0, "is_max": True},
        {"label": "₹1 Lakh+", "value": None, "is_max": False},
    ],
    "Audio": [
        {"label": "Under ₹1,500", "value": 1500.0, "is_max": True},
        {"label": "Under ₹3,000", "value": 3000.0, "is_max": True},
        {"label": "Under ₹5,000", "value": 5000.0, "is_max": True},
        {"label": "Premium Hi-Fi", "value": None, "is_max": False},
    ],
    "Toys": [
        {"label": "Under ₹300", "value": 300.0, "is_max": True},
        {"label": "Under ₹500", "value": 500.0, "is_max": True},
        {"label": "Under ₹1,000", "value": 1000.0, "is_max": True},
        {"label": "Under ₹2,000", "value": 2000.0, "is_max": True},
        {"label": "Premium Collections", "value": None, "is_max": False},
    ],
}


def get_budget_options_for_category(category: str) -> List[str]:
    """Returns human-friendly clickable budget options for a category."""
    if not category:
        return [t["label"] for t in CATEGORY_BUDGET_TIERS.get("Home & Kitchen", [])]
    norm_cat = category.strip()
    # Case-insensitive lookup
    for k, tiers in CATEGORY_BUDGET_TIERS.items():
        if k.lower() == norm_cat.lower() or norm_cat.lower() in k.lower():
            return [t["label"] for t in tiers]
    return [t["label"] for t in CATEGORY_BUDGET_TIERS.get("Home & Kitchen", [])]


def parse_budget_from_option(option_text: str) -> Optional[float]:
    """Converts a budget option or query (e.g. 'Under ₹2500', '₹500', 'under 10k') into a numerical budget."""
    if not option_text:
        return None
    raw = str(option_text).lower().replace(",", "").strip()

    if "premium" in raw:
        return None

    # Lakh handling
    if "lakh" in raw:
        m = re.search(r"(\d+(?:\.\d+)?)\s*lakh", raw)
        if m:
            return float(m.group(1)) * 100000.0
        if "1" in raw or "one" in raw:
            return 100000.0
        if "2" in raw or "two" in raw:
            return 200000.0

    # 'k' suffix handling (e.g. '10k', '2.5k', '50k')
    k_match = re.search(r"(\d+(?:\.\d+)?)\s*k\b", raw)
    if k_match:
        return float(k_match.group(1)) * 1000.0

    # Standard currency pattern matching (e.g. 'under ₹2500', 'under 500', 'rs. 1000', 'budget 5000')
    patterns = [
        r"(?:under|below|less\s+than|within|max|budget\s+of)\s*(?:rs\.?|inr|₹)?\s*(\d+)",
        r"(?:rs\.?|inr|₹)\s*(\d+)",
        r"(\d+)\s*(?:rs|rupees|inr|budget)",
        r"(\d+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, raw)
        if match:
            try:
                val = float(match.group(1))
                if val >= 50:  # Minimum realistic budget threshold in INR
                    return val
            except ValueError:
                pass
    return None
