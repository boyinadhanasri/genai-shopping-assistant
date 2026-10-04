"""
LLM & Expert Rule-Based Query Understanding Module for ShopAI
Deep Category Flow Intelligence for Home & Kitchen, Books, Sports, Laptops, Smartphones, Fashion, Beauty, Audio, Toys.

Extracts:
- category (Home & Kitchen, Books, Sports, Smartphones, Laptops, Fashion, Beauty, Audio, Cameras, Toys, Electronics)
- subcategory (Cookware, Air Fryers, Mixer Grinders, Cricket, Gym Equipment, Programming, Python Book, Smartphone, Laptop, Shoes, etc.)
- brand (Samsung, Apple, Prestige, Hawkins, Yonex, Nivia, O'Reilly, Pearson, Levi's, Philips, etc.)
- budget (Numerical max budget)
- purpose (Coding, Student, Gaming, Video Editing, Office)
- priority (Camera, Battery, Performance, Gaming, AI Features, ANC, Deep Bass)
- gender (Men, Women, Unisex, Kids)
- use_case & constraints
- intent (product_search, product_recommendation, product_comparison, category_exploration, flow_step)
- comparison_targets (e.g. ["iPhone 15", "Samsung S24"])
"""

import os
import re
import json
import logging
from typing import Any, Dict, List, Optional

from backend.config.category_budget_rules import parse_budget_from_option
from backend.config.category_flow_rules import (
    SHOPPING_WELCOME_FLOW,
    CATEGORY_SHOPPING_FLOWS,
    normalize_category_name,
)

logger = logging.getLogger(__name__)

SUBCATEGORY_MAP: Dict[str, tuple] = {
    # =========================================================================
    # HOME & KITCHEN INTELLIGENCE (Phase 1 & Phase 4)
    # =========================================================================
    # Cookware
    "cookware": ("Home & Kitchen", "Cookware"),
    "fry pan": ("Home & Kitchen", "Cookware"),
    "frying pan": ("Home & Kitchen", "Cookware"),
    "pan": ("Home & Kitchen", "Cookware"),
    "kadai": ("Home & Kitchen", "Cookware"),
    "kadhai": ("Home & Kitchen", "Cookware"),
    "tawa": ("Home & Kitchen", "Cookware"),
    "skillet": ("Home & Kitchen", "Cookware"),
    "saucepan": ("Home & Kitchen", "Cookware"),
    "pot": ("Home & Kitchen", "Cookware"),
    "pots": ("Home & Kitchen", "Cookware"),
    "non-stick pan": ("Home & Kitchen", "Cookware"),
    "non stick pan": ("Home & Kitchen", "Cookware"),

    # Kitchen Appliances
    "kitchen appliance": ("Home & Kitchen", "Kitchen Appliances"),
    "kitchen appliances": ("Home & Kitchen", "Kitchen Appliances"),
    "appliance": ("Home & Kitchen", "Kitchen Appliances"),
    "appliances": ("Home & Kitchen", "Kitchen Appliances"),
    "toaster": ("Home & Kitchen", "Kitchen Appliances"),
    "electric kettle": ("Home & Kitchen", "Kitchen Appliances"),
    "kettle": ("Home & Kitchen", "Kitchen Appliances"),
    "induction": ("Home & Kitchen", "Kitchen Appliances"),
    "induction cooktop": ("Home & Kitchen", "Kitchen Appliances"),
    "hand blender": ("Home & Kitchen", "Kitchen Appliances"),
    "blender": ("Home & Kitchen", "Kitchen Appliances"),
    "juicer": ("Home & Kitchen", "Kitchen Appliances"),

    # Air Fryers
    "air fryer": ("Home & Kitchen", "Air Fryers"),
    "air fryers": ("Home & Kitchen", "Air Fryers"),
    "airfryer": ("Home & Kitchen", "Air Fryers"),

    # Mixer Grinders
    "mixer grinder": ("Home & Kitchen", "Mixer Grinders"),
    "mixer grinders": ("Home & Kitchen", "Mixer Grinders"),
    "mixer": ("Home & Kitchen", "Mixer Grinders"),
    "grinder": ("Home & Kitchen", "Mixer Grinders"),
    "juicer mixer grinder": ("Home & Kitchen", "Mixer Grinders"),

    # Cookers
    "cooker": ("Home & Kitchen", "Cookers"),
    "cookers": ("Home & Kitchen", "Cookers"),
    "pressure cooker": ("Home & Kitchen", "Cookers"),
    "pressure cookers": ("Home & Kitchen", "Cookers"),
    "rice cooker": ("Home & Kitchen", "Cookers"),

    # Coffee Makers
    "coffee maker": ("Home & Kitchen", "Coffee Makers"),
    "coffee makers": ("Home & Kitchen", "Coffee Makers"),
    "coffee machine": ("Home & Kitchen", "Coffee Makers"),
    "espresso": ("Home & Kitchen", "Coffee Makers"),
    "espresso machine": ("Home & Kitchen", "Coffee Makers"),
    "french press": ("Home & Kitchen", "Coffee Makers"),

    # Storage Containers
    "storage container": ("Home & Kitchen", "Storage Containers"),
    "storage containers": ("Home & Kitchen", "Storage Containers"),
    "container": ("Home & Kitchen", "Storage Containers"),
    "containers": ("Home & Kitchen", "Storage Containers"),
    "spice container": ("Home & Kitchen", "Storage Containers"),
    "food container": ("Home & Kitchen", "Storage Containers"),
    "food containers": ("Home & Kitchen", "Storage Containers"),
    "jar": ("Home & Kitchen", "Storage Containers"),
    "jars": ("Home & Kitchen", "Storage Containers"),

    # Water Bottles
    "water bottle": ("Home & Kitchen", "Water Bottles"),
    "water bottles": ("Home & Kitchen", "Water Bottles"),
    "bottle": ("Home & Kitchen", "Water Bottles"),
    "bottles": ("Home & Kitchen", "Water Bottles"),
    "flask": ("Home & Kitchen", "Water Bottles"),
    "thermos": ("Home & Kitchen", "Water Bottles"),
    "sipper": ("Home & Kitchen", "Water Bottles"),

    # Dinner Sets
    "dinner set": ("Home & Kitchen", "Dinner Sets"),
    "dinner sets": ("Home & Kitchen", "Dinner Sets"),
    "dinnerware": ("Home & Kitchen", "Dinner Sets"),
    "plates": ("Home & Kitchen", "Dinner Sets"),
    "bowls": ("Home & Kitchen", "Dinner Sets"),
    "cutlery": ("Home & Kitchen", "Dinner Sets"),
    "tableware": ("Home & Kitchen", "Dinner Sets"),

    # Cleaning Supplies
    "cleaning supply": ("Home & Kitchen", "Cleaning Supplies"),
    "cleaning supplies": ("Home & Kitchen", "Cleaning Supplies"),
    "mop": ("Home & Kitchen", "Cleaning Supplies"),
    "spin mop": ("Home & Kitchen", "Cleaning Supplies"),
    "microfiber cloth": ("Home & Kitchen", "Cleaning Supplies"),
    "vacuum cleaner": ("Home & Kitchen", "Cleaning Supplies"),
    "broom": ("Home & Kitchen", "Cleaning Supplies"),

    # Home Decor
    "home decor": ("Home & Kitchen", "Home Decor"),
    "decor": ("Home & Kitchen", "Home Decor"),
    "vase": ("Home & Kitchen", "Home Decor"),
    "flower vase": ("Home & Kitchen", "Home Decor"),
    "wall art": ("Home & Kitchen", "Home Decor"),
    "canvas": ("Home & Kitchen", "Home Decor"),
    "candle": ("Home & Kitchen", "Home Decor"),
    "candles": ("Home & Kitchen", "Home Decor"),
    "sofa cover": ("Home & Kitchen", "Home Decor"),
    "cushion cover": ("Home & Kitchen", "Home Decor"),
    "cushion covers": ("Home & Kitchen", "Home Decor"),

    # Furniture
    "furniture": ("Home & Kitchen", "Furniture"),
    "study desk": ("Home & Kitchen", "Furniture"),
    "desk": ("Home & Kitchen", "Furniture"),
    "office chair": ("Home & Kitchen", "Furniture"),
    "chair": ("Home & Kitchen", "Furniture"),
    "table": ("Home & Kitchen", "Furniture"),
    "coffee table": ("Home & Kitchen", "Furniture"),
    "recliner": ("Home & Kitchen", "Furniture"),
    "bookshelf": ("Home & Kitchen", "Furniture"),

    # Bedsheets
    "bedsheet": ("Home & Kitchen", "Bedsheets"),
    "bedsheets": ("Home & Kitchen", "Bedsheets"),
    "bed sheet": ("Home & Kitchen", "Bedsheets"),
    "bed sheets": ("Home & Kitchen", "Bedsheets"),
    "bed cover": ("Home & Kitchen", "Bedsheets"),
    "bed linen": ("Home & Kitchen", "Bedsheets"),

    # Curtains
    "curtain": ("Home & Kitchen", "Curtains"),
    "curtains": ("Home & Kitchen", "Curtains"),
    "window curtain": ("Home & Kitchen", "Curtains"),
    "door curtain": ("Home & Kitchen", "Curtains"),
    "drapes": ("Home & Kitchen", "Curtains"),
    "sheer curtain": ("Home & Kitchen", "Curtains"),

    # Lighting
    "lighting": ("Home & Kitchen", "Lighting"),
    "lamp": ("Home & Kitchen", "Lighting"),
    "lamps": ("Home & Kitchen", "Lighting"),
    "table lamp": ("Home & Kitchen", "Lighting"),
    "ceiling light": ("Home & Kitchen", "Lighting"),
    "pendant light": ("Home & Kitchen", "Lighting"),
    "study lamp": ("Home & Kitchen", "Lighting"),

    # =========================================================================
    # BOOKS INTELLIGENCE (Phase 2 & Phase 4)
    # =========================================================================
    "book": ("Books", "Book"),
    "books": ("Books", "Book"),
    "reading": ("Books", "Book"),
    "programming": ("Books", "Programming"),
    "programming book": ("Books", "Programming"),
    "programming books": ("Books", "Programming"),
    "coding book": ("Books", "Programming"),
    "python": ("Books", "Programming"),
    "python book": ("Books", "Programming"),
    "python books": ("Books", "Programming"),
    "clean code": ("Books", "Programming"),
    "javascript book": ("Books", "Programming"),
    "java book": ("Books", "Programming"),
    "c++ book": ("Books", "Programming"),
    "grokking algorithms": ("Books", "Programming"),
    "data science": ("Books", "Data Science"),
    "data science book": ("Books", "Data Science"),
    "data science books": ("Books", "Data Science"),
    "machine learning": ("Books", "AI & ML"),
    "machine learning book": ("Books", "AI & ML"),
    "ai book": ("Books", "AI & ML"),
    "ai books": ("Books", "AI & ML"),
    "deep learning": ("Books", "AI & ML"),
    "deep learning book": ("Books", "AI & ML"),
    "artificial intelligence": ("Books", "AI & ML"),
    "business": ("Books", "Business"),
    "business book": ("Books", "Business"),
    "business books": ("Books", "Business"),
    "startup book": ("Books", "Business"),
    "zero to one": ("Books", "Business"),
    "lean startup": ("Books", "Business"),
    "finance": ("Books", "Finance"),
    "finance book": ("Books", "Finance"),
    "finance books": ("Books", "Finance"),
    "psychology of money": ("Books", "Finance"),
    "rich dad poor dad": ("Books", "Finance"),
    "intelligent investor": ("Books", "Finance"),
    "stock market book": ("Books", "Finance"),
    "self help": ("Books", "Self Help"),
    "self help book": ("Books", "Self Help"),
    "self help books": ("Books", "Self Help"),
    "atomic habits": ("Books", "Self Help"),
    "ikigai": ("Books", "Self Help"),
    "productivity": ("Books", "Productivity"),
    "productivity book": ("Books", "Productivity"),
    "deep work": ("Books", "Productivity"),
    "novel": ("Books", "Novels"),
    "novels": ("Books", "Novels"),
    "fiction": ("Books", "Novels"),
    "academic": ("Books", "Academic"),
    "academic book": ("Books", "Academic"),
    "textbook": ("Books", "Academic"),
    "interview prep": ("Books", "Interview Preparation"),
    "interview preparation": ("Books", "Interview Preparation"),
    "cracking the coding interview": ("Books", "Interview Preparation"),
    "system design interview": ("Books", "Interview Preparation"),
    "upsc": ("Books", "UPSC"),
    "upsc book": ("Books", "UPSC"),
    "upsc books": ("Books", "UPSC"),
    "gate": ("Books", "GATE"),
    "gate book": ("Books", "GATE"),
    "jee": ("Books", "JEE"),
    "jee book": ("Books", "JEE"),
    "neet": ("Books", "NEET"),
    "neet book": ("Books", "NEET"),

    # =========================================================================
    # SPORTS INTELLIGENCE (Phase 3 & Phase 4)
    # =========================================================================
    "sport": ("Sports", "Sports"),
    "sports": ("Sports", "Sports"),
    "fitness": ("Sports", "Sports"),
    "cricket": ("Sports", "Cricket"),
    "cricket bat": ("Sports", "Cricket"),
    "cricket bats": ("Sports", "Cricket"),
    "bat": ("Sports", "Cricket"),
    "bats": ("Sports", "Cricket"),
    "cricket ball": ("Sports", "Cricket"),
    "cricket kit": ("Sports", "Cricket"),
    "cricket helmet": ("Sports", "Cricket"),
    "cricket pads": ("Sports", "Cricket"),
    "cricket gloves": ("Sports", "Cricket"),
    "football": ("Sports", "Football"),
    "footballs": ("Sports", "Football"),
    "soccer": ("Sports", "Football"),
    "soccer ball": ("Sports", "Football"),
    "shin guard": ("Sports", "Football"),
    "goalkeeper gloves": ("Sports", "Football"),
    "badminton": ("Sports", "Badminton"),
    "badminton racket": ("Sports", "Badminton"),
    "badminton rackets": ("Sports", "Badminton"),
    "racket": ("Sports", "Badminton"),
    "rackets": ("Sports", "Badminton"),
    "shuttlecock": ("Sports", "Badminton"),
    "shuttlecocks": ("Sports", "Badminton"),
    "shuttle": ("Sports", "Badminton"),
    "gym": ("Sports", "Gym Equipment"),
    "gym equipment": ("Sports", "Gym Equipment"),
    "dumbbell": ("Sports", "Gym Equipment"),
    "dumbbells": ("Sports", "Gym Equipment"),
    "weights": ("Sports", "Gym Equipment"),
    "weight": ("Sports", "Gym Equipment"),
    "weight bench": ("Sports", "Gym Equipment"),
    "resistance band": ("Sports", "Gym Equipment"),
    "resistance bands": ("Sports", "Gym Equipment"),
    "pull up bar": ("Sports", "Gym Equipment"),
    "gym kit": ("Sports", "Gym Equipment"),
    "kettlebell": ("Sports", "Gym Equipment"),
    "running": ("Sports", "Running"),
    "running shoes": ("Sports", "Running"),
    "running gear": ("Sports", "Running"),
    "cycling": ("Sports", "Cycling"),
    "cycle": ("Sports", "Cycling"),
    "bicycle": ("Sports", "Cycling"),
    "cycling helmet": ("Sports", "Cycling"),
    "bike helmet": ("Sports", "Cycling"),
    "yoga": ("Sports", "Yoga"),
    "yoga mat": ("Sports", "Yoga"),
    "yoga mats": ("Sports", "Yoga"),
    "yoga block": ("Sports", "Yoga"),
    "yoga blocks": ("Sports", "Yoga"),
    "yoga strap": ("Sports", "Yoga"),
    "swimming": ("Sports", "Swimming"),
    "swimming goggles": ("Sports", "Swimming"),
    "swim goggles": ("Sports", "Swimming"),
    "swim cap": ("Sports", "Swimming"),
    "swimming cap": ("Sports", "Swimming"),
    "kickboard": ("Sports", "Swimming"),
    "basketball": ("Sports", "Basketball"),
    "basketball hoop": ("Sports", "Basketball"),
    "tennis": ("Sports", "Tennis"),
    "tennis racket": ("Sports", "Tennis"),
    "tennis ball": ("Sports", "Tennis"),

    # =========================================================================
    # ELECTRONICS, LAPTOPS, SMARTPHONES, CAMERAS, AUDIO
    # =========================================================================
    "laptop": ("Laptops", "Laptop"),
    "laptops": ("Laptops", "Laptop"),
    "notebook": ("Laptops", "Laptop"),
    "macbook": ("Laptops", "Laptop"),
    "chromebook": ("Laptops", "Laptop"),
    "ultrabook": ("Laptops", "Laptop"),
    "pc": ("Laptops", "Laptop"),
    "computer": ("Laptops", "Laptop"),

    "smartphone": ("Smartphones", "Smartphone"),
    "smartphones": ("Smartphones", "Smartphone"),
    "phone": ("Smartphones", "Smartphone"),
    "phones": ("Smartphones", "Smartphone"),
    "camera phone": ("Smartphones", "Smartphone"),
    "gaming phone": ("Smartphones", "Smartphone"),
    "5g phone": ("Smartphones", "Smartphone"),
    "mobile": ("Smartphones", "Smartphone"),
    "mobiles": ("Smartphones", "Smartphone"),
    "iphone": ("Smartphones", "Smartphone"),
    "android": ("Smartphones", "Smartphone"),
    "galaxy": ("Smartphones", "Smartphone"),

    "earbuds": ("Audio", "Earbuds"),
    "earbud": ("Audio", "Earbuds"),
    "airpods": ("Audio", "Earbuds"),
    "airdopes": ("Audio", "Earbuds"),
    "tws": ("Audio", "Earbuds"),
    "earphones": ("Audio", "Earbuds"),
    "headphones": ("Audio", "Headphones"),
    "headphone": ("Audio", "Headphones"),
    "speaker": ("Audio", "Speaker"),
    "speakers": ("Audio", "Speaker"),
    "soundbar": ("Audio", "Speaker"),

    "camera": ("Cameras", "Camera"),
    "cameras": ("Cameras", "Camera"),
    "dslr": ("Cameras", "Camera"),
    "mirrorless": ("Cameras", "Camera"),
    "vlog": ("Cameras", "Camera"),
    "vlogging": ("Cameras", "Camera"),
    "action camera": ("Cameras", "Camera"),
    "gopro": ("Cameras", "Camera"),

    "smartwatch": ("Electronics", "Smartwatch"),
    "smart watch": ("Electronics", "Smartwatch"),
    "watch": ("Electronics", "Smartwatch"),
    "tv": ("Electronics", "TV"),
    "tvs": ("Electronics", "TV"),
    "television": ("Electronics", "TV"),

    # =========================================================================
    # FASHION & SHOES
    # =========================================================================
    "shoe": ("Shoes", "Shoes"),
    "shoes": ("Shoes", "Shoes"),
    "sneaker": ("Shoes", "Shoes"),
    "sneakers": ("Shoes", "Shoes"),
    "sandals": ("Shoes", "Shoes"),
    "footwear": ("Shoes", "Shoes"),
    "casual shoes": ("Shoes", "Shoes"),
    "formal shoes": ("Shoes", "Shoes"),
    "trekking shoes": ("Shoes", "Shoes"),
    "boots": ("Shoes", "Shoes"),
    "top": ("Fashion", "Top"),
    "tops": ("Fashion", "Top"),
    "tshirt": ("Fashion", "T-Shirt"),
    "t-shirt": ("Fashion", "T-Shirt"),
    "t-shirts": ("Fashion", "T-Shirt"),
    "tee": ("Fashion", "T-Shirt"),
    "shirt": ("Fashion", "Shirt"),
    "shirts": ("Fashion", "Shirt"),
    "polo": ("Fashion", "Polo"),
    "jeans": ("Fashion", "Jeans"),
    "jean": ("Fashion", "Jeans"),
    "denim": ("Fashion", "Jeans"),
    "trousers": ("Fashion", "Pants"),
    "pants": ("Fashion", "Pants"),
    "dress": ("Fashion", "Dress"),
    "jacket": ("Fashion", "Jacket"),
    "hoodie": ("Fashion", "Hoodie"),

    # =========================================================================
    # BEAUTY & PERSONAL CARE
    # =========================================================================
    "face wash": ("Beauty", "Face Wash"),
    "facewash": ("Beauty", "Face Wash"),
    "cleanser": ("Beauty", "Face Wash"),
    "moisturizer": ("Beauty", "Moisturizer"),
    "moisturiser": ("Beauty", "Moisturizer"),
    "cream": ("Beauty", "Moisturizer"),
    "lipstick": ("Beauty", "Lipstick"),
    "lipsticks": ("Beauty", "Lipstick"),
    "perfume": ("Beauty", "Perfume"),
    "perfumes": ("Beauty", "Perfume"),
    "fragrance": ("Beauty", "Perfume"),
    "sunscreen": ("Beauty", "Sunscreen"),
    "sunscreens": ("Beauty", "Sunscreen"),
    "serum": ("Beauty", "Serum"),

    # =========================================================================
    # TOYS & GAMES
    # =========================================================================
    "toy": ("Toys", "Toy"),
    "toys": ("Toys", "Toy"),
    "lego": ("Toys", "Building Blocks"),
    "building blocks": ("Toys", "Building Blocks"),
    "rc car": ("Toys", "RC Toys"),
    "drone": ("Toys", "RC Toys"),
    "board game": ("Toys", "Board Games"),
    "action figure": ("Toys", "Action Figures"),
    "soft toy": ("Toys", "Soft Toys"),
    "stem kit": ("Toys", "STEM Toys"),
    "puzzle": ("Toys", "Puzzles"),
}

KNOWN_BRANDS = [
    # Electronics & Tech
    "Samsung", "Apple", "Dell", "HP", "Lenovo", "Asus", "Acer", "Sony", "boAt", "Canon", "Nikon",
    "OnePlus", "Noise", "realme", "Redmi", "Xiaomi", "Oppo", "Vivo", "Nothing",
    # Home & Kitchen
    "Prestige", "Hawkins", "Philips", "Pigeon", "Milton", "Cello", "Solimo", "Wakefit", "Bombay Dyeing", "Havells", "Wipro", "Borosil", "Wonderchef", "Kent", "Agaro", "Spotzero", "Bajaj",
    # Books
    "O'Reilly", "Pearson", "McGraw Hill", "Penguin", "HarperCollins", "Wiley", "Notion Press", "Arihant", "Disha", "Oxford", "Simon & Schuster",
    # Sports
    "Yonex", "Nivia", "Cosco", "Decathlon", "Speedo", "Wilson", "Spalding", "Strauss", "Boldfit", "Li-Ning", "Shimano", "Asics", "Nike", "Adidas", "Puma", "Reebok",
    # Fashion & Shoes
    "Levi's", "Wrangler", "Polo Ralph Lauren", "COOFANDY", "Amazon Essentials", "Lee",
    # Beauty
    "Himalaya", "Cetaphil", "Minimalist", "Plum", "Mamaearth", "Neutrogena", "Pond's", "Dot & Key", "Maybelline", "Sugar", "L'Oreal", "Nivea"
]


def rule_based_query_understanding(query: str, category_hint: Optional[str] = None) -> Dict[str, Any]:
    """
    Production-grade AI Shopping Expert parser:
    - Recognizes welcome & category exploration triggers (Home & Kitchen, Books, Sports, Laptops, Phones, Shoes, etc.)
    - Identifies intent, multi-step parameters, comparison targets, and budgets
    """
    lowered = query.lower().strip()

    # 1. Welcome / Greeting Exploration
    if lowered in ["hi", "hello", "hey", "start", "start shopping", "shop", "help", "explore", "what can you do"]:
        return {
            "category": "General",
            "subcategory": None,
            "brand": None,
            "budget": None,
            "constraints": [],
            "intent": "category_exploration",
            "raw_query": query,
            "needs_clarification": True,
            "clarification_message": SHOPPING_WELCOME_FLOW["message"],
            "clarification_options": SHOPPING_WELCOME_FLOW["options"],
        }

    # 2. Pure Category Inquiry Triggers (e.g. "Home & Kitchen", "Books", "Sports", "Laptops", "Smartphones", "Shoes")
    category_triggers = {
        "Home & Kitchen": ["home & kitchen", "home and kitchen", "home", "kitchen", "cookware", "appliances", "home decor"],
        "Books": ["books", "book", "reading", "study books", "novels"],
        "Sports": ["sports", "sport", "fitness", "gym equipment", "workout gear"],
        "Laptops": ["laptops", "laptop", "need a laptop", "looking for a laptop", "buy laptop", "notebook pc"],
        "Smartphones": ["smartphones", "smartphone", "phones", "phone", "need a phone", "looking for a phone", "buy phone", "mobiles", "mobile"],
        "Shoes": ["shoes", "shoe", "need shoes", "footwear", "sneakers", "buy shoes"],
        "Fashion": ["fashion", "clothing", "apparel", "clothes", "wear"],
        "Beauty": ["beauty", "skincare", "cosmetics", "makeup"],
        "Audio": ["audio", "earbuds", "headphones", "sound"],
        "Cameras": ["cameras", "camera", "dslr"],
        "Toys": ["toys", "toy", "games", "toys & games"],
    }

    for cat_name, triggers in category_triggers.items():
        if lowered in triggers or lowered == f"shop {cat_name.lower()}" or lowered == f"{cat_name.lower()} shopping":
            flow_cfg = CATEGORY_SHOPPING_FLOWS.get(cat_name)
            if flow_cfg:
                first_step = flow_cfg["steps"][0]
                welcome_text = (
                    f"**{flow_cfg['display_name']}** {flow_cfg['emoji']}\n\n"
                    f"{first_step['question']}"
                )
                return {
                    "category": cat_name,
                    "subcategory": None,
                    "brand": None,
                    "budget": None,
                    "constraints": [],
                    "intent": "category_exploration",
                    "raw_query": query,
                    "needs_clarification": True,
                    "clarification_message": welcome_text,
                    "clarification_options": first_step["options"],
                }

    # 3. Detect Comparison Intent & Targets
    intent = "product_search"
    compare_targets = []
    if any(w in lowered for w in ["compare", " vs ", " versus ", " vs.", "difference between"]):
        intent = "product_comparison"
        clean_comp = re.sub(r"^(?:please\s+)?(?:compare|show\s+difference\s+between)\s+", "", lowered)
        parts = re.split(r"\s+(?:and|vs\.?|versus|with)\s+", clean_comp)
        if len(parts) >= 2:
            compare_targets = [p.strip().title() for p in parts if len(p.strip()) > 1]
    elif any(w in lowered for w in ["recommend", "best", "top", "suggest", "popular", "pick"]):
        intent = "product_recommendation"
    elif any(w in lowered for w in ["detail", "specs", "specification", "features"]):
        intent = "product_details"

    # 4. Budget Extraction
    budget = parse_budget_from_option(lowered)

    # 5. Purpose & Use-case Extraction
    detected_purpose = None
    purpose_map = {
        "coding": "Coding & Programming",
        "programming": "Coding & Programming",
        "student": "College & Student",
        "college": "College & Student",
        "study": "College & Student",
        "gaming": "Gaming & High Performance",
        "game": "Gaming & High Performance",
        "video editing": "Video Editing & Design",
        "editing": "Video Editing & Design",
        "office": "Office Work & Productivity",
        "work": "Office Work & Productivity",
    }
    for k, v in purpose_map.items():
        if re.search(r"\b" + re.escape(k) + r"\b", lowered):
            detected_purpose = v
            break

    # 6. Priority Extraction
    detected_priority = None
    priority_map = {
        "camera": "Camera & Photography",
        "photo": "Camera & Photography",
        "photography": "Camera & Photography",
        "battery": "2-Day Battery Life",
        "performance": "Fast Performance & 5G",
        "5g": "Fast Performance & 5G",
        "anc": "Active Noise Cancellation",
        "noise cancellation": "Active Noise Cancellation",
        "bass": "Deep Bass",
        "ai features": "AI Features & Flagship",
    }
    for k, v in priority_map.items():
        if re.search(r"\b" + re.escape(k) + r"\b", lowered):
            detected_priority = v
            break

    # 7. Gender Extraction
    detected_gender = None
    if re.search(r"\b(men|man|mens|boy|boys|male)\b", lowered):
        detected_gender = "Men"
    elif re.search(r"\b(women|woman|womens|girl|girls|female|ladies)\b", lowered):
        detected_gender = "Women"
    elif re.search(r"\b(kid|kids|child|toddler|baby)\b", lowered):
        detected_gender = "Kids"
    elif re.search(r"\bunisex\b", lowered):
        detected_gender = "Unisex"

    # 8. Subcategory & Category Resolution
    detected_category = None
    detected_subcategory = None
    has_specific_product = False

    # Check 3-gram, 2-gram, then 1-gram tokens
    clean_query_words = re.findall(r"\b[a-zA-Z0-9\+\-\']+\b", lowered)

    # 3-grams
    for i in range(len(clean_query_words) - 2):
        tri = f"{clean_query_words[i]} {clean_query_words[i+1]} {clean_query_words[i+2]}"
        if tri in SUBCATEGORY_MAP:
            detected_category, detected_subcategory = SUBCATEGORY_MAP[tri]
            has_specific_product = True
            break

    # 2-grams
    if not detected_category:
        for i in range(len(clean_query_words) - 1):
            bi = f"{clean_query_words[i]} {clean_query_words[i+1]}"
            if bi in SUBCATEGORY_MAP:
                detected_category, detected_subcategory = SUBCATEGORY_MAP[bi]
                has_specific_product = True
                break

    # 1-grams
    if not detected_category:
        for word in clean_query_words:
            if word in SUBCATEGORY_MAP:
                detected_category, detected_subcategory = SUBCATEGORY_MAP[word]
                has_specific_product = True
                break

    if not detected_category and category_hint:
        detected_category = normalize_category_name(category_hint)

    # 9. Brand Extraction
    detected_brand = None
    for brand in KNOWN_BRANDS:
        if brand.lower() in lowered:
            detected_brand = brand
            break

    # 10. Clarification Needed for Broad Under-specified Intent
    needs_clarification = False
    clarification_message = None
    clarification_options = []

    # If query is broad (e.g., "Need a laptop", "Need a phone", "Need shoes", "Home & Kitchen", "Books", "Sports") without budget or specific subcategory:
    if detected_category and not detected_brand and not compare_targets:
        norm_cat = normalize_category_name(detected_category)
        flow_cfg = CATEGORY_SHOPPING_FLOWS.get(norm_cat)

        # Trigger conversational guidance when user expresses intent like "Need a laptop" or "Need a phone" or broad category
        if any(lowered.startswith(p) for p in ["need ", "want ", "looking for ", "show me "]) and not budget and flow_cfg:
            needs_clarification = True
            first_step = flow_cfg["steps"][0]
            clarification_message = f"{first_step['question']}"
            clarification_options = first_step["options"]
        elif not has_specific_product and not detected_purpose and not detected_priority and flow_cfg:
            needs_clarification = True
            first_step = flow_cfg["steps"][0]
            clarification_message = f"{first_step['question']}"
            clarification_options = first_step["options"]

    # 11. Constraints
    constraints = []
    if budget:
        constraints.append(f"budget_max: {budget}")
    if detected_brand:
        constraints.append(f"brand: {detected_brand}")
    if detected_subcategory:
        constraints.append(f"subcategory: {detected_subcategory}")
    if detected_purpose:
        constraints.append(f"purpose: {detected_purpose}")
    if detected_priority:
        constraints.append(f"priority: {detected_priority}")
    if detected_gender:
        constraints.append(f"gender: {detected_gender}")

    return {
        "category": detected_category,
        "subcategory": detected_subcategory,
        "brand": detected_brand,
        "budget": budget,
        "purpose": detected_purpose,
        "priority": detected_priority,
        "gender": detected_gender,
        "constraints": constraints,
        "intent": intent,
        "compare_targets": compare_targets,
        "raw_query": query,
        "needs_clarification": needs_clarification,
        "clarification_message": clarification_message,
        "clarification_options": clarification_options,
    }


def understand_query(query: str, category_hint: Optional[str] = None) -> Dict[str, Any]:
    """
    Primary Query Understanding entrypoint:
    1. Deterministic high-speed rule-based understanding.
    2. LLM fallback if Groq API key is present.
    """
    rule_parsed = rule_based_query_understanding(query, category_hint)
    if (
        rule_parsed.get("needs_clarification")
        or rule_parsed.get("category")
        or rule_parsed.get("budget")
        or rule_parsed.get("subcategory")
        or rule_parsed.get("intent") == "product_comparison"
    ):
        return rule_parsed

    groq_api_key = os.environ.get("GROQ_API_KEY")
    if not groq_api_key:
        return rule_parsed

    try:
        from groq import Groq
        client = Groq(api_key=groq_api_key, timeout=3.0)

        prompt = f"""You are ShopAI, a production-grade GenAI Shopping Assistant expert.
Extract structured shopping intent from the query in strictly valid JSON format.

Categories: Home & Kitchen, Books, Sports, Smartphones, Laptops, Fashion, Beauty, Audio, Cameras, Toys, Electronics.

JSON format:
{{
  "category": "string (one of available categories)",
  "subcategory": "string or null",
  "brand": "string or null",
  "budget": number or null,
  "purpose": "string or null",
  "priority": "string or null",
  "gender": "string or null",
  "constraints": ["list", "of", "features"],
  "intent": "product_search" | "product_comparison" | "product_recommendation" | "category_exploration"
}}

User query: "{query}"
Category hint: "{category_hint or ''}"

Return ONLY valid JSON:"""

        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a precise JSON query understanding engine."},
                {"role": "user", "content": prompt}
            ],
            model="llama-3.1-8b-instant",
            temperature=0.0,
            max_tokens=200,
        )

        response_content = chat_completion.choices[0].message.content.strip()
        parsed_json = json.loads(response_content)
        parsed_json["raw_query"] = query
        parsed_json["needs_clarification"] = False
        parsed_json["clarification_message"] = None
        parsed_json["clarification_options"] = []
        return parsed_json
    except Exception as e:
        logger.warning(f"LLM parser fallback used rule-based output: {e}")
        return rule_parsed
