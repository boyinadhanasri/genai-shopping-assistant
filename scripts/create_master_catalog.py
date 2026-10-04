"""
Create master_catalog.csv from real e-commerce datasets and comprehensive curated products:
- Fashion: from datasets/products.csv (700+ apparel/shoes/jeans items)
- Home & Kitchen: Cookware, Appliances, Storage, Water Bottles, Dinner Sets, Cookers, Mixer Grinders, Air Fryers, Coffee Makers, Cleaning, Decor, Furniture, Bedsheets, Curtains, Lighting
- Books: Programming, Python, Data Science, AI & ML, Business, Finance, Self Help, Productivity, Novels, Academic, Interview Prep, UPSC, GATE, JEE, NEET
- Sports: Cricket, Football, Badminton, Gym Equipment, Running, Cycling, Yoga, Swimming, Basketball, Tennis
- Electronics & Laptops: Laptops, Cameras, Smart TVs, Wireless Earbuds, Smartwatches
- Mobiles: Smartphones (Samsung, Apple, OnePlus, Redmi, Realme)
- Beauty: Face Wash, Moisturizer, Sunscreen, Lipstick, Perfume, Serum
- Toys: LEGO, RC Cars, Board Games, Action Figures, Soft Toys, STEM, Puzzles, Hot Wheels
"""

import ast
import os
import re
import sys
from pathlib import Path
import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATASETS_DIR = BASE_DIR / "datasets"

DATA_DIR.mkdir(parents=True, exist_ok=True)


def parse_image_url(val: str, fallback_cat: str = "fashion") -> str:
    """Extract first valid image URL from all_images column."""
    if not val or pd.isna(val):
        return "https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=600&q=80"
    val_str = str(val).strip()
    if val_str.startswith("["):
        try:
            parsed = ast.literal_eval(val_str)
            if isinstance(parsed, list) and len(parsed) > 0 and str(parsed[0]).startswith("http"):
                return parsed[0]
        except Exception:
            pass
    if val_str.startswith("http"):
        return val_str
    return "https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=600&q=80"


def clean_brand_name(brand_raw: str, title: str) -> str:
    """Clean brand name, stripping 'Store', 'Brand', etc."""
    if not brand_raw or pd.isna(brand_raw) or str(brand_raw).lower() in ["generic", "nan", "unknown"]:
        known = ["Levi's", "Wrangler", "Polo Ralph Lauren", "Adidas", "Nike", "Puma", "Reebok", "COOFANDY", "Amazon Essentials"]
        for kb in known:
            if kb.lower() in title.lower():
                return kb
        return "Amazon Brand"
    b = str(brand_raw).replace(" Store", "").replace(" Brand", "").strip()
    return b or "Fashion"


def clean_rating(rating_raw) -> float:
    """Extract float rating from string like '4.6 out of 5 stars'."""
    if pd.isna(rating_raw):
        return 4.2
    if isinstance(rating_raw, (int, float)):
        return max(1.0, min(5.0, float(rating_raw)))
    val_str = str(rating_raw).strip()
    match = re.search(r"(\d+(?:\.\d+)?)", val_str)
    if match:
        try:
            return max(1.0, min(5.0, float(match.group(1))))
        except ValueError:
            pass
    return 4.2


def clean_price(price_raw) -> float:
    """Convert USD price to INR."""
    if pd.isna(price_raw):
        return 999.0
    try:
        val = float(price_raw)
        if val <= 0:
            return 999.0
        if val < 500:
            return round(val * 50.0, 2)
        return round(val, 2)
    except (ValueError, TypeError):
        return 999.0


def infer_fashion_subcategory(title: str, desc: str) -> str:
    """Classifies a fashion product into a precise subcategory."""
    t_lower = (title or "").lower()
    if re.search(r"\b(jeans?|denim)\b", t_lower):
        return "Jeans"
    elif re.search(r"\b(t-shirts?|tshirts?|tees?)\b", t_lower):
        return "T-Shirt"
    elif re.search(r"\bpolos?\b", t_lower):
        return "Polo"
    elif re.search(r"\b(tops?|blouses?|tunics?|crop top|tank top)\b", t_lower):
        return "Top"
    elif re.search(r"\bshirts?\b", t_lower):
        return "Shirt"
    elif re.search(r"\b(shoes?|sneakers?|boots?|sandals?|slippers?|footwear)\b", t_lower):
        return "Shoes"
    elif re.search(r"\b(dresses?|gowns?)\b", t_lower):
        return "Dress"
    elif re.search(r"\b(jackets?|coats?|blazers?)\b", t_lower):
        return "Jacket"
    elif re.search(r"\b(hoodies?|sweatshirts?)\b", t_lower):
        return "Hoodie"
    elif re.search(r"\b(pants?|trousers?|chinos?|joggers?|sweatpants?|shorts?)\b", t_lower):
        return "Pants"
    return "Apparel"


def load_real_fashion_dataset() -> pd.DataFrame:
    """Load and clean datasets/products.csv."""
    csv_path = DATASETS_DIR / "products.csv"
    if not csv_path.exists():
        print(f"Warning: {csv_path} not found.")
        return pd.DataFrame()

    df = pd.read_csv(csv_path)
    print(f"Loaded raw dataset from {csv_path}: {df.shape[0]} rows, {df.shape[1]} columns")

    cleaned_rows = []
    seen_ids = set()

    for _, row in df.iterrows():
        prod_id = str(row.get("asin") or f"PRD{len(cleaned_rows):05d}").strip()
        if prod_id in seen_ids:
            continue
        seen_ids.add(prod_id)

        title = str(row.get("title") or "").strip()
        if not title or title.lower() == "nan":
            continue

        brand = clean_brand_name(row.get("brand_name"), title)
        price = clean_price(row.get("price_value"))
        rating = clean_rating(row.get("rating_stars"))
        image_url = parse_image_url(row.get("all_images"), "fashion")

        desc_parts = []
        if pd.notna(row.get("about_item")):
            desc_parts.append(str(row["about_item"]).strip())
        if pd.notna(row.get("customer_review_summary")):
            desc_parts.append(str(row["customer_review_summary"]).strip())
        if pd.notna(row.get("product_description")):
            desc_parts.append(str(row["product_description"]).strip())
        desc = " ".join(desc_parts).strip() or f"{brand} {title} stylish fashion apparel."

        subcat = infer_fashion_subcategory(title, desc)

        cleaned_rows.append({
            "id": prod_id,
            "product_id": prod_id,
            "title": title,
            "category": "Fashion",
            "subcategory": subcat,
            "brand": brand,
            "price": price,
            "rating": rating,
            "description": desc,
            "image_url": image_url,
        })

    print(f"Processed {len(cleaned_rows)} valid fashion products from products.csv")
    return pd.DataFrame(cleaned_rows)


def get_curated_catalog() -> pd.DataFrame:
    """
    Curated high-quality, authentic products for Home & Kitchen, Books, Sports, Electronics,
    Laptops, Mobiles, Beauty, and Toys.
    """
    curated = [
        # =====================================================================
        # HOME & KITCHEN (Phase 1)
        # =====================================================================
        # Cookware
        {
            "id": "HK_CW_01", "product_id": "HK_CW_01",
            "title": "Prestige Omega Select Plus Non-Stick Fry Pan 24cm with Induction Base",
            "category": "Home & Kitchen", "subcategory": "Cookware", "brand": "Prestige", "price": 749.0, "rating": 4.5,
            "description": "Prestige Omega Select Plus durable 3-layer non-stick coating fry pan with ergonomic stay-cool handle, induction and gas stove compatible.",
            "image_url": "https://images.unsplash.com/photo-1584269600464-37b1b58a9fe7?auto=format&fit=crop&w=600&q=80"
        },
        {
            "id": "HK_CW_02", "product_id": "HK_CW_02",
            "title": "Hawkins Futura Hard Anodised Deep Fry Pan Kadai with Stainless Steel Lid 2.5L",
            "category": "Home & Kitchen", "subcategory": "Cookware", "brand": "Hawkins", "price": 1299.0, "rating": 4.7,
            "description": "Hawkins Futura hard anodised kadai with heavy 4.06 mm base, heats quickly and evenly, non-toxic, non-staining and non-reactive with foods.",
            "image_url": "https://images.unsplash.com/photo-1556911220-e15b29be8c8f?auto=format&fit=crop&w=600&q=80"
        },
        {
            "id": "HK_CW_03", "product_id": "HK_CW_03",
            "title": "Prestige Deluxe Granite Concave Dosa Tawa 28cm Induction Compatible",
            "category": "Home & Kitchen", "subcategory": "Cookware", "brand": "Prestige", "price": 999.0, "rating": 4.5,
            "description": "Prestige 5-layer granite spatter coated concave tawa designed for making crispy dosas, rotis and pancakes with minimal oil.",
            "image_url": "https://images.unsplash.com/photo-1584269600464-37b1b58a9fe7?auto=format&fit=crop&w=600&q=80"
        },
        {
            "id": "HK_CW_04", "product_id": "HK_CW_04",
            "title": "Lodge Seasoned Cast Iron Skillet 10.25 Inch Heavy Duty Frying Pan",
            "category": "Home & Kitchen", "subcategory": "Cookware", "brand": "Lodge", "price": 2499.0, "rating": 4.8,
            "description": "Original Lodge seasoned cast iron skillet with superior heat retention, natural easy-release finish, suitable for oven, stove, grill or campfire.",
            "image_url": "https://images.unsplash.com/photo-1556911220-e15b29be8c8f?auto=format&fit=crop&w=600&q=80"
        },
        {
            "id": "HK_CW_05", "product_id": "HK_CW_05",
            "title": "Pigeon by Stovekraft Non-Stick 3-Piece Cookware Starter Set (Fry Pan, Kadai, Tawa)",
            "category": "Home & Kitchen", "subcategory": "Cookware", "brand": "Pigeon", "price": 1199.0, "rating": 4.3,
            "description": "Pigeon 3-piece non-stick cookware set including 24cm fry pan, 24cm kadai with glass lid, and 25cm flat tawa with cool-touch Bakelite handles.",
            "image_url": "https://images.unsplash.com/photo-1584269600464-37b1b58a9fe7?auto=format&fit=crop&w=600&q=80"
        },

        # Kitchen Appliances
        {
            "id": "HK_KA_01", "product_id": "HK_KA_01",
            "title": "Philips Daily Collection HD4928 2100W Induction Cooktop with Preset Menus",
            "category": "Home & Kitchen", "subcategory": "Kitchen Appliances", "brand": "Philips", "price": 2799.0, "rating": 4.5,
            "description": "Philips 2100W electromagnetic induction cooktop with Indian cooking menus, crystal glass plate, touch buttons and auto-off timer.",
            "image_url": "https://images.unsplash.com/photo-1585338107529-13afc5f02586?auto=format&fit=crop&w=600&q=80"
        },
        {
            "id": "HK_KA_02", "product_id": "HK_KA_02",
            "title": "Havells Aqua Plus 1.2L 1500W Double Wall Stainless Steel Electric Kettle",
            "category": "Home & Kitchen", "subcategory": "Kitchen Appliances", "brand": "Havells", "price": 1199.0, "rating": 4.5,
            "description": "Havells Aqua Plus rapid boiling electric kettle with cool-touch outer body, 304 stainless steel interior, 360-degree swivel base and auto shut-off.",
            "image_url": "https://images.unsplash.com/photo-1585338107529-13afc5f02586?auto=format&fit=crop&w=600&q=80"
        },
        {
            "id": "HK_KA_03", "product_id": "HK_KA_03",
            "title": "Morphy Richards AT-201 2-Slice 650W Pop-Up Toaster with 7 Browning Settings",
            "category": "Home & Kitchen", "subcategory": "Kitchen Appliances", "brand": "Morphy Richards", "price": 1249.0, "rating": 4.3,
            "description": "Morphy Richards 2-slice pop-up toaster with variable browning control, high-lift function for small slices, and removable crumb tray.",
            "image_url": "https://images.unsplash.com/photo-1585338107529-13afc5f02586?auto=format&fit=crop&w=600&q=80"
        },
        {
            "id": "HK_KA_04", "product_id": "HK_KA_04",
            "title": "Philips HL1655/00 250W Hand Blender with Steel Rod and Multi-Utility Blades",
            "category": "Home & Kitchen", "subcategory": "Kitchen Appliances", "brand": "Philips", "price": 1449.0, "rating": 4.4,
            "description": "Philips compact hand blender with rust-proof stainless steel rod, single trigger operation, and specialized blades for hot and cold blending.",
            "image_url": "https://images.unsplash.com/photo-1585338107529-13afc5f02586?auto=format&fit=crop&w=600&q=80"
        },

        # Air Fryers
        {
            "id": "HK_AF_01", "product_id": "HK_AF_01",
            "title": "Philips Digital Air Fryer HD9252/90 4.1L with Rapid Air Technology & Touchscreen",
            "category": "Home & Kitchen", "subcategory": "Air Fryers", "brand": "Philips", "price": 6999.0, "rating": 4.7,
            "description": "Philips digital air fryer with 90% less fat Rapid Air Technology, 7 preset cooking modes, keep warm function, and dishwasher safe basket.",
            "image_url": "https://images.unsplash.com/photo-1585338107529-13afc5f02586?auto=format&fit=crop&w=600&q=80"
        },
        {
            "id": "HK_AF_02", "product_id": "HK_AF_02",
            "title": "Pigeon Healthifry Digital Air Fryer 4.2L 1200W with 360 Degree Rapid Circulation",
            "category": "Home & Kitchen", "subcategory": "Air Fryers", "brand": "Pigeon", "price": 2499.0, "rating": 4.4,
            "description": "Pigeon Healthifry budget air fryer with 4.2L non-stick basket, digital temperature timer controls, and 85% oil-free healthy cooking.",
            "image_url": "https://images.unsplash.com/photo-1585338107529-13afc5f02586?auto=format&fit=crop&w=600&q=80"
        },
        {
            "id": "HK_AF_03", "product_id": "HK_AF_03",
            "title": "Solimo 5.5L Large Capacity Digital Air Fryer with 8 Preset Cooking Functions",
            "category": "Home & Kitchen", "subcategory": "Air Fryers", "brand": "Solimo", "price": 3999.0, "rating": 4.5,
            "description": "Solimo family size 5.5L air fryer with LED touch panel, 1400W fast heating, overheat protection and non-stick detachable frying drawer.",
            "image_url": "https://images.unsplash.com/photo-1585338107529-13afc5f02586?auto=format&fit=crop&w=600&q=80"
        },

        # Mixer Grinders
        {
            "id": "HK_MG_01", "product_id": "HK_MG_01",
            "title": "Prestige Iris Plus 750W Mixer Grinder with 3 Stainless Steel Jars and 1 Juicer Jar",
            "category": "Home & Kitchen", "subcategory": "Mixer Grinders", "brand": "Prestige", "price": 2699.0, "rating": 4.5,
            "description": "Prestige Iris Plus 750 watt mixer grinder with 3 stainless steel multipurpose jars, 1 transparent polycarbonate juicer jar with blade, and overload protection.",
            "image_url": "https://images.unsplash.com/photo-1585338107529-13afc5f02586?auto=format&fit=crop&w=600&q=80"
        },
        {
            "id": "HK_MG_02", "product_id": "HK_MG_02",
            "title": "Philips HL7756/00 750W Heavy Duty Mixer Grinder with 3 Stainless Steel Jars",
            "category": "Home & Kitchen", "subcategory": "Mixer Grinders", "brand": "Philips", "price": 3299.0, "rating": 4.6,
            "description": "Philips 750W Turbo motor mixer grinder with advanced air ventilation system, leak-proof stainless steel jars, and durable coupler.",
            "image_url": "https://images.unsplash.com/photo-1585338107529-13afc5f02586?auto=format&fit=crop&w=600&q=80"
        },
        {
            "id": "HK_MG_03", "product_id": "HK_MG_03",
            "title": "Bajaj Rex 500W Mixer Grinder with 3 Stainless Steel Jars and Overload Protection",
            "category": "Home & Kitchen", "subcategory": "Mixer Grinders", "brand": "Bajaj", "price": 1899.0, "rating": 4.3,
            "description": "Bajaj Rex 500-watt mixer grinder with vacuum feet for stability, 3-speed control with incher, and rust-proof stainless steel blades.",
            "image_url": "https://images.unsplash.com/photo-1585338107529-13afc5f02586?auto=format&fit=crop&w=600&q=80"
        },

        # Cookers
        {
            "id": "HK_CK_01", "product_id": "HK_CK_01",
            "title": "Hawkins Contura Hard Anodised Pressure Cooker 3L with Inner Lid and Curved Body",
            "category": "Home & Kitchen", "subcategory": "Cookers", "brand": "Hawkins", "price": 1450.0, "rating": 4.7,
            "description": "Hawkins Contura 3 litre hard anodised pressure cooker with rounded sides for easy stirring and visibility, stay-cool handles and safety valve.",
            "image_url": "https://images.unsplash.com/photo-1556911220-e15b29be8c8f?auto=format&fit=crop&w=600&q=80"
        },
        {
            "id": "HK_CK_02", "product_id": "HK_CK_02",
            "title": "Prestige Deluxe Alpha Stainless Steel Pressure Cooker 5L Induction & Gas Compatible",
            "category": "Home & Kitchen", "subcategory": "Cookers", "brand": "Prestige", "price": 2299.0, "rating": 4.6,
            "description": "Prestige Deluxe Alpha 5L cooker crafted from high-grade stainless steel with alpha base for uniform heat distribution and pressure indicator.",
            "image_url": "https://images.unsplash.com/photo-1556911220-e15b29be8c8f?auto=format&fit=crop&w=600&q=80"
        },

        # Coffee Makers
        {
            "id": "HK_CF_01", "product_id": "HK_CF_01",
            "title": "Wonderchef Regalia French Press Coffee and Tea Maker 600ml Borosilicate Glass",
            "category": "Home & Kitchen", "subcategory": "Coffee Makers", "brand": "Wonderchef", "price": 799.0, "rating": 4.5,
            "description": "Wonderchef premium borosilicate glass french press with 4-level filtration system for aromatic rich coffee and loose leaf tea brewing.",
            "image_url": "https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?auto=format&fit=crop&w=600&q=80"
        },
        {
            "id": "HK_CF_02", "product_id": "HK_CF_02",
            "title": "Morphy Richards New Europa 800W Drip Coffee Maker 4-Cup with Steam Frother",
            "category": "Home & Kitchen", "subcategory": "Coffee Makers", "brand": "Morphy Richards", "price": 1999.0, "rating": 4.4,
            "description": "Morphy Richards espresso & cappuccino maker with milk frothing nozzle, removable drip tray, and 4-cup capacity glass carafe.",
            "image_url": "https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?auto=format&fit=crop&w=600&q=80"
        },

        # Storage Containers
        {
            "id": "HK_SC_01", "product_id": "HK_SC_01",
            "title": "Borosil Classic Airtight Glass Storage Containers Set of 4 (400ml x 4) Microwave Safe",
            "category": "Home & Kitchen", "subcategory": "Storage Containers", "brand": "Borosil", "price": 899.0, "rating": 4.7,
            "description": "Borosil 100% borosilicate glass food containers with leak-proof silicone seal clip lids, oven and microwave safe up to 350°C.",
            "image_url": "https://images.unsplash.com/photo-1584269600464-37b1b58a9fe7?auto=format&fit=crop&w=600&q=80"
        },
        {
            "id": "HK_SC_02", "product_id": "HK_SC_02",
            "title": "Milton Micro-Safe Stainless Steel Food Storage Container Set of 3 with Insulated Bag",
            "category": "Home & Kitchen", "subcategory": "Storage Containers", "brand": "Milton", "price": 649.0, "rating": 4.5,
            "description": "Milton stainless steel leak-proof lunch and kitchen storage containers with BPA-free clip lids and thermal insulated jacket.",
            "image_url": "https://images.unsplash.com/photo-1584269600464-37b1b58a9fe7?auto=format&fit=crop&w=600&q=80"
        },

        # Water Bottles
        {
            "id": "HK_WB_01", "product_id": "HK_WB_01",
            "title": "Milton Thermosteel Flip Lid Insulated Stainless Steel 1000ml Water Bottle",
            "category": "Home & Kitchen", "subcategory": "Water Bottles", "brand": "Milton", "price": 799.0, "rating": 4.7,
            "description": "Milton double wall vacuum insulated 1 litre flask keeps beverages hot or cold for 24 hours. Made from grade 304 rust-proof stainless steel.",
            "image_url": "https://images.unsplash.com/photo-1602143407151-7111542de6e8?auto=format&fit=crop&w=600&q=80"
        },
        {
            "id": "HK_WB_02", "product_id": "HK_WB_02",
            "title": "Cello Duro Pure Copper Water Bottle 1000ml Ayurvedic Health Benefits",
            "category": "Home & Kitchen", "subcategory": "Water Bottles", "brand": "Cello", "price": 899.0, "rating": 4.5,
            "description": "Cello 100% pure copper jointless water bottle designed to boost digestion and immunity with traditional copper infusion.",
            "image_url": "https://images.unsplash.com/photo-1602143407151-7111542de6e8?auto=format&fit=crop&w=600&q=80"
        },

        # Dinner Sets
        {
            "id": "HK_DS_01", "product_id": "HK_DS_01",
            "title": "Borosil Opalware Dinner Set 33-Pieces White Royal Blue Scratch Resistant",
            "category": "Home & Kitchen", "subcategory": "Dinner Sets", "brand": "Borosil", "price": 2199.0, "rating": 4.7,
            "description": "Borosil 33-piece opalware dinner set with full plates, quarter plates, veg bowls, soup bowls, serving bowls and rice platter. 100% bone ash free.",
            "image_url": "https://images.unsplash.com/photo-1584269600464-37b1b58a9fe7?auto=format&fit=crop&w=600&q=80"
        },
        {
            "id": "HK_DS_02", "product_id": "HK_DS_02",
            "title": "Neelam Premium Stainless Steel Heavy Gauge Dinner Set 24-Pieces Mirror Finish",
            "category": "Home & Kitchen", "subcategory": "Dinner Sets", "brand": "Neelam", "price": 1499.0, "rating": 4.5,
            "description": "Neelam 24-piece heavy duty stainless steel dinner set with thalis, katoris, glasses and spoons in mirror polished finish.",
            "image_url": "https://images.unsplash.com/photo-1584269600464-37b1b58a9fe7?auto=format&fit=crop&w=600&q=80"
        },

        # Cleaning Supplies
        {
            "id": "HK_CS_01", "product_id": "HK_CS_01",
            "title": "Spotzero by Milton Elite Spin Mop with Big Wheels & Stainless Steel Wringer Bucket",
            "category": "Home & Kitchen", "subcategory": "Cleaning Supplies", "brand": "Spotzero", "price": 1099.0, "rating": 4.5,
            "description": "Spotzero 360-degree spin mop with stainless steel drying basket, sturdy drag handle, big wheels, and 2 microfiber head refills.",
            "image_url": "https://images.unsplash.com/photo-1585338107529-13afc5f02586?auto=format&fit=crop&w=600&q=80"
        },
        {
            "id": "HK_CS_02", "product_id": "HK_CS_02",
            "title": "Scotch-Brite High Absorbency Microfiber Multipurpose Cleaning Cloth Pack of 4",
            "category": "Home & Kitchen", "subcategory": "Cleaning Supplies", "brand": "Scotch-Brite", "price": 249.0, "rating": 4.7,
            "description": "Scotch-Brite lint-free microfiber cleaning cloth set for kitchen countertops, appliances, glass, and furniture cleaning without scratches.",
            "image_url": "https://images.unsplash.com/photo-1585338107529-13afc5f02586?auto=format&fit=crop&w=600&q=80"
        },

        # Home Decor
        {
            "id": "HK_HD_01", "product_id": "HK_HD_01",
            "title": "Solimo Modern Ceramic Handcrafted Flower Vase 10-Inch Matte White Minimalist Decor",
            "category": "Home & Kitchen", "subcategory": "Home Decor", "brand": "Solimo", "price": 449.0, "rating": 4.6,
            "description": "Solimo modern ceramic donut vase with matte finish, ideal for pampas grass, dried flowers, and living room tabletop decoration.",
            "image_url": "https://images.unsplash.com/photo-1584269600464-37b1b58a9fe7?auto=format&fit=crop&w=600&q=80"
        },
        {
            "id": "HK_HD_02", "product_id": "HK_HD_02",
            "title": "Bella Vita Luxury Organic Scented Soy Candles Gift Set of 4 (Vanilla, Lavender, Rose)",
            "category": "Home & Kitchen", "subcategory": "Home Decor", "brand": "Bella Vita", "price": 599.0, "rating": 4.7,
            "description": "Bella Vita aromatic aromatherapy candles made from natural soy wax with lead-free cotton wicks, offering up to 20 hours burn time each.",
            "image_url": "https://images.unsplash.com/photo-1584269600464-37b1b58a9fe7?auto=format&fit=crop&w=600&q=80"
        },

        # Furniture
        {
            "id": "HK_FN_01", "product_id": "HK_FN_01",
            "title": "Wakefit Ergonomic High Back Mesh Study & Office Chair with Lumbar Support",
            "category": "Home & Kitchen", "subcategory": "Furniture", "brand": "Wakefit", "price": 4999.0, "rating": 4.7,
            "description": "Wakefit high-back breathable mesh ergonomic chair with adjustable headrest, multi-lock synchro tilt mechanism, and heavy-duty nylon wheelbase.",
            "image_url": "https://images.unsplash.com/photo-1580481077197-9f299c59cb98?auto=format&fit=crop&w=600&q=80"
        },
        {
            "id": "HK_FN_02", "product_id": "HK_FN_02",
            "title": "DeckUp Plank Engineered Wood Contemporary Coffee Table with Open Storage Shelf",
            "category": "Home & Kitchen", "subcategory": "Furniture", "brand": "DeckUp", "price": 2499.0, "rating": 4.4,
            "description": "DeckUp Plank stylish center coffee table in dark wenge matte finish with spacious lower shelf for magazines, books, and decor items.",
            "image_url": "https://images.unsplash.com/photo-1533090161767-e6ffed986c88?auto=format&fit=crop&w=600&q=80"
        },

        # Bedsheets
        {
            "id": "HK_BS_01", "product_id": "HK_BS_01",
            "title": "Bombay Dyeing 100% Pure Cotton King Size Double Bedsheet with 2 Pillow Covers",
            "category": "Home & Kitchen", "subcategory": "Bedsheets", "brand": "Bombay Dyeing", "price": 999.0, "rating": 4.7,
            "description": "Bombay Dyeing 100% cotton breathable king size double bedsheet (274x274 cm) with 2 matching pillow covers in elegant floral pattern.",
            "image_url": "https://images.unsplash.com/photo-1584269600464-37b1b58a9fe7?auto=format&fit=crop&w=600&q=80"
        },
        {
            "id": "HK_BS_02", "product_id": "HK_BS_02",
            "title": "Wakefit 100% Pure Combed Cotton 300 TC Satin Stripe King Size Luxury Bedsheet",
            "category": "Home & Kitchen", "subcategory": "Bedsheets", "brand": "Wakefit", "price": 1299.0, "rating": 4.8,
            "description": "Wakefit premium 300 thread count satin stripe hotel quality bedsheet made from long-staple combed cotton for ultra-soft comfort.",
            "image_url": "https://images.unsplash.com/photo-1584269600464-37b1b58a9fe7?auto=format&fit=crop&w=600&q=80"
        },

        # Curtains
        {
            "id": "HK_CT_01", "product_id": "HK_CT_01",
            "title": "Story@Home Blackout Thermal Insulated Window Curtains Set of 2 (5 Feet)",
            "category": "Home & Kitchen", "subcategory": "Curtains", "brand": "Story@Home", "price": 699.0, "rating": 4.6,
            "description": "Story@Home triple weave blackout curtains blocking 90% sunlight and UV rays, noise reducing and thermal insulated with steel eyelets.",
            "image_url": "https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=600&q=80"
        },
        {
            "id": "HK_CT_02", "product_id": "HK_CT_02",
            "title": "Urban Space 100% Pure Cotton Semi-Sheer Door Curtains 7 Feet Pack of 2",
            "category": "Home & Kitchen", "subcategory": "Curtains", "brand": "Urban Space", "price": 899.0, "rating": 4.6,
            "description": "Urban Space natural cotton breathable sheer door curtains filtering gentle natural daylight while maintaining privacy.",
            "image_url": "https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=600&q=80"
        },

        # Lighting
        {
            "id": "HK_LT_01", "product_id": "HK_LT_01",
            "title": "Wipro Smart LED 12W B22 Bulb 16 Million Colors with Wi-Fi App & Voice Control",
            "category": "Home & Kitchen", "subcategory": "Lighting", "brand": "Wipro", "price": 499.0, "rating": 4.5,
            "description": "Wipro smart bulb with tunable white and 16 million colors, works with Alexa and Google Assistant with no hub required.",
            "image_url": "https://images.unsplash.com/photo-1507473885765-e6ed057f782c?auto=format&fit=crop&w=600&q=80"
        },
        {
            "id": "HK_LT_02", "product_id": "HK_LT_02",
            "title": "Havells Study Mate LED Rechargeable Desk Lamp with Touch Dimmer & Flexible Arm",
            "category": "Home & Kitchen", "subcategory": "Lighting", "brand": "Havells", "price": 849.0, "rating": 4.6,
            "description": "Havells eye-care LED desk lamp with 3 color temperatures, step-less touch dimming, and built-in rechargeable lithium battery.",
            "image_url": "https://images.unsplash.com/photo-1507473885765-e6ed057f782c?auto=format&fit=crop&w=600&q=80"
        },

        # =====================================================================
        # BOOKS (Phase 2)
        # =====================================================================
        # Programming & Python
        {
            "id": "BK_PRG_01", "product_id": "BK_PRG_01",
            "title": "Python Crash Course, 3rd Edition: A Hands-On, Project-Based Introduction by Eric Matthes",
            "category": "Books", "subcategory": "Programming", "brand": "O'Reilly", "price": 449.0, "rating": 4.9,
            "description": "The world's best-selling guide to the Python programming language. Learn fundamental concepts, write clean code, and build real-world web apps and games.",
            "image_url": "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?auto=format&fit=crop&w=600&q=80"
        },
        {
            "id": "BK_PRG_02", "product_id": "BK_PRG_02",
            "title": "Automate the Boring Stuff with Python, 2nd Edition by Al Sweigart",
            "category": "Books", "subcategory": "Programming", "brand": "No Starch Press", "price": 399.0, "rating": 4.8,
            "description": "Practical programming for total beginners. Learn how to write simple programs that automate web scraping, spreadsheet updates, and email tasks in minutes.",
            "image_url": "https://images.unsplash.com/photo-1512820790803-83ca734da794?auto=format&fit=crop&w=600&q=80"
        },
        {
            "id": "BK_PRG_03", "product_id": "BK_PRG_03",
            "title": "Clean Code: A Handbook of Agile Software Craftsmanship by Robert C. Martin",
            "category": "Books", "subcategory": "Programming", "brand": "Pearson", "price": 599.0, "rating": 4.8,
            "description": "Legendary software engineering guide on writing readable, maintainable, refactored code with best practices, unit testing, and design patterns.",
            "image_url": "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?auto=format&fit=crop&w=600&q=80"
        },
        {
            "id": "BK_PRG_04", "product_id": "BK_PRG_04",
            "title": "Fluent Python: Clear, Concise, and Effective Programming 2nd Edition by Luciano Ramalho",
            "category": "Books", "subcategory": "Programming", "brand": "O'Reilly", "price": 899.0, "rating": 4.9,
            "description": "Advanced Python masterclass covering data models, generators, concurrency with asyncio, type hints, and metaprogramming.",
            "image_url": "https://images.unsplash.com/photo-1512820790803-83ca734da794?auto=format&fit=crop&w=600&q=80"
        },
        {
            "id": "BK_PRG_05", "product_id": "BK_PRG_05",
            "title": "Grokking Algorithms: An Illustrated Guide for Programmers by Aditya Bhargava",
            "category": "Books", "subcategory": "Programming", "brand": "Manning", "price": 475.0, "rating": 4.8,
            "description": "Visual, fun, and easy-to-follow guide to essential data structures, sorting algorithms, graphs, dynamic programming, and search.",
            "image_url": "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?auto=format&fit=crop&w=600&q=80"
        },

        # Data Science
        {
            "id": "BK_DS_01", "product_id": "BK_DS_01",
            "title": "Hands-On Machine Learning with Scikit-Learn, Keras, and TensorFlow 3rd Edition by Aurélien Géron",
            "category": "Books", "subcategory": "Data Science", "brand": "O'Reilly", "price": 999.0, "rating": 4.9,
            "description": "Industry benchmark book on neural networks, deep learning architectures, CNNs, Transformers, and training production ML models.",
            "image_url": "https://images.unsplash.com/photo-1512820790803-83ca734da794?auto=format&fit=crop&w=600&q=80"
        },
        {
            "id": "BK_DS_02", "product_id": "BK_DS_02",
            "title": "Python for Data Analysis: Data Wrangling with Pandas, NumPy, and Jupyter by Wes McKinney",
            "category": "Books", "subcategory": "Data Science", "brand": "O'Reilly", "price": 749.0, "rating": 4.8,
            "description": "Written by the creator of Pandas, this book is the definitive practical guide to data manipulation, visualization, and time-series in Python.",
            "image_url": "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?auto=format&fit=crop&w=600&q=80"
        },

        # AI & ML
        {
            "id": "BK_AI_01", "product_id": "BK_AI_01",
            "title": "Deep Learning (Adaptive Computation and Machine Learning) by Ian Goodfellow",
            "category": "Books", "subcategory": "AI & ML", "brand": "MIT Press", "price": 850.0, "rating": 4.8,
            "description": "The definitive mathematical and conceptual text on deep learning, optimization, regularization, generative models, and research foundations.",
            "image_url": "https://images.unsplash.com/photo-1512820790803-83ca734da794?auto=format&fit=crop&w=600&q=80"
        },
        {
            "id": "BK_AI_02", "product_id": "BK_AI_02",
            "title": "Artificial Intelligence: A Modern Approach, 4th Global Edition by Russell & Norvig",
            "category": "Books", "subcategory": "AI & ML", "brand": "Pearson", "price": 999.0, "rating": 4.9,
            "description": "The most widely used AI textbook worldwide, exploring search agents, probabilistic reasoning, machine learning, and robotics.",
            "image_url": "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?auto=format&fit=crop&w=600&q=80"
        },

        # Business & Finance
        {
            "id": "BK_BS_01", "product_id": "BK_BS_01",
            "title": "Zero to One: Notes on Startups, or How to Build the Future by Peter Thiel",
            "category": "Books", "subcategory": "Business", "brand": "Penguin", "price": 299.0, "rating": 4.7,
            "description": "Essential playbook on startup innovation, technology monopolies, and creating truly transformative products.",
            "image_url": "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?auto=format&fit=crop&w=600&q=80"
        },
        {
            "id": "BK_FN_01", "product_id": "BK_FN_01",
            "title": "The Psychology of Money: Timeless lessons on wealth, greed, and happiness by Morgan Housel",
            "category": "Books", "subcategory": "Finance", "brand": "Harriman House", "price": 275.0, "rating": 4.9,
            "description": "19 short stories exploring the strange ways people think about money and teaching you how to make better sense of financial decisions.",
            "image_url": "https://images.unsplash.com/photo-1512820790803-83ca734da794?auto=format&fit=crop&w=600&q=80"
        },
        {
            "id": "BK_FN_02", "product_id": "BK_FN_02",
            "title": "Rich Dad Poor Dad by Robert T. Kiyosaki (25th Anniversary Edition)",
            "category": "Books", "subcategory": "Finance", "brand": "Plata Publishing", "price": 320.0, "rating": 4.7,
            "description": "The #1 personal finance book of all time, teaching asset building, financial literacy, and escaping the rat race.",
            "image_url": "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?auto=format&fit=crop&w=600&q=80"
        },

        # Self Help & Productivity
        {
            "id": "BK_SH_01", "product_id": "BK_SH_01",
            "title": "Atomic Habits: An Easy & Proven Way to Build Good Habits by James Clear",
            "category": "Books", "subcategory": "Self Help", "brand": "Penguin", "price": 399.0, "rating": 4.9,
            "description": "Transform your life with tiny changes that deliver remarkable results. Learn habit stacking, environment design, and identity shifts.",
            "image_url": "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?auto=format&fit=crop&w=600&q=80"
        },
        {
            "id": "BK_PRD_01", "product_id": "BK_PRD_01",
            "title": "Deep Work: Rules for Focused Success in a Distracted World by Cal Newport",
            "category": "Books", "subcategory": "Productivity", "brand": "Grand Central", "price": 350.0, "rating": 4.8,
            "description": "Master the superpower of intense concentration to achieve peak cognitive output in a world full of distractions.",
            "image_url": "https://images.unsplash.com/photo-1512820790803-83ca734da794?auto=format&fit=crop&w=600&q=80"
        },

        # Novels
        {
            "id": "BK_NV_01", "product_id": "BK_NV_01",
            "title": "The Alchemist: 25th Anniversary Edition by Paulo Coelho",
            "category": "Books", "subcategory": "Novels", "brand": "HarperCollins", "price": 199.0, "rating": 4.8,
            "description": "The magical story of Santiago, an Andalusian shepherd boy who travels in search of worldly treasure, discovering his Personal Legend.",
            "image_url": "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?auto=format&fit=crop&w=600&q=80"
        },
        {
            "id": "BK_NV_02", "product_id": "BK_NV_02",
            "title": "Sapiens: A Brief History of Humankind by Yuval Noah Harari",
            "category": "Books", "subcategory": "Novels", "brand": "HarperCollins", "price": 449.0, "rating": 4.8,
            "description": "Epic journey through human history from foraging hunter-gatherers to modern biological and technological masters of Earth.",
            "image_url": "https://images.unsplash.com/photo-1512820790803-83ca734da794?auto=format&fit=crop&w=600&q=80"
        },

        # Interview Prep & Exams
        {
            "id": "BK_INT_01", "product_id": "BK_INT_01",
            "title": "Cracking the Coding Interview: 189 Programming Questions by Gayle Laakmann McDowell",
            "category": "Books", "subcategory": "Interview Preparation", "brand": "CareerCup", "price": 699.0, "rating": 4.9,
            "description": "The gold standard interview prep guide for top tech companies (FAANG/MANG), covering algorithms, data structures, and behavioral interviews.",
            "image_url": "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?auto=format&fit=crop&w=600&q=80"
        },
        {
            "id": "BK_UPSC_01", "product_id": "BK_UPSC_01",
            "title": "Indian Polity for Civil Services and Other State Examinations 7th Edition by M. Laxmikanth",
            "category": "Books", "subcategory": "UPSC", "brand": "McGraw Hill", "price": 780.0, "rating": 4.9,
            "description": "The bible of Indian constitution, governance, and political system for UPSC Civil Services preliminary and main exams.",
            "image_url": "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?auto=format&fit=crop&w=600&q=80"
        },
        {
            "id": "BK_JEE_01", "product_id": "BK_JEE_01",
            "title": "Concepts of Physics by H.C. Verma (Volume 1 & Volume 2 Combo Set)",
            "category": "Books", "subcategory": "JEE", "brand": "Bharati Bhawan", "price": 750.0, "rating": 4.9,
            "description": "The legendary physics foundation series for IIT-JEE Main & Advanced aspirants, featuring conceptual theory and numericals.",
            "image_url": "https://images.unsplash.com/photo-1512820790803-83ca734da794?auto=format&fit=crop&w=600&q=80"
        },

        # =====================================================================
        # SPORTS & FITNESS (Phase 3)
        # =====================================================================
        # Cricket
        {
            "id": "SP_CK_01", "product_id": "SP_CK_01",
            "title": "SG Kashmir Willow Full Size Adult Cricket Bat with Protective Cover",
            "category": "Sports", "subcategory": "Cricket", "brand": "SG", "price": 1299.0, "rating": 4.6,
            "description": "SG traditional shape Kashmir willow bat with thick edges, curved blade, chevron grip, and full-length padded bat cover. Ideal for club matches.",
            "image_url": "https://images.unsplash.com/photo-1540747913346-19e32dc3e97e?auto=format&fit=crop&w=600&q=80"
        },
        {
            "id": "SP_CK_02", "product_id": "SP_CK_02",
            "title": "SS Master 500 English Willow Pro Grade Cricket Bat with Padded Cover",
            "category": "Sports", "subcategory": "Cricket", "brand": "SS", "price": 4499.0, "rating": 4.8,
            "description": "SS hand-crafted Grade 1 English Willow cricket bat with huge sweet spot, balanced pickup, and premium Sarawak cane handle.",
            "image_url": "https://images.unsplash.com/photo-1540747913346-19e32dc3e97e?auto=format&fit=crop&w=600&q=80"
        },
        {
            "id": "SP_CK_03", "product_id": "SP_CK_03",
            "title": "SG Club Cricket Red Leather Ball 4-Piece Construction Pack of 3",
            "category": "Sports", "subcategory": "Cricket", "brand": "SG", "price": 699.0, "rating": 4.5,
            "description": "Top grade alum tanned leather cricket balls with granulated cork core and fine linen stitching for 40-50 overs durability.",
            "image_url": "https://images.unsplash.com/photo-1540747913346-19e32dc3e97e?auto=format&fit=crop&w=600&q=80"
        },
        {
            "id": "SP_CK_04", "product_id": "SP_CK_04",
            "title": "DSC Intense Pro Cricket Helmet with High Impact Steel Grille",
            "category": "Sports", "subcategory": "Cricket", "brand": "DSC", "price": 1199.0, "rating": 4.7,
            "description": "High impact resistant polypropylene outer shell cricket helmet with sweat-absorbent breathable foam padding and adjustable steel visor.",
            "image_url": "https://images.unsplash.com/photo-1540747913346-19e32dc3e97e?auto=format&fit=crop&w=600&q=80"
        },

        # Football
        {
            "id": "SP_FB_01", "product_id": "SP_FB_01",
            "title": "Nivia Storm Rubber Molded Football Size 5 Official Match Ball",
            "category": "Sports", "subcategory": "Football", "brand": "Nivia", "price": 449.0, "rating": 4.5,
            "description": "Nivia durable rubber molded 32-panel football with butyl bladder for air retention, suitable for rough outdoor surfaces and turf.",
            "image_url": "https://images.unsplash.com/photo-1508098682722-e99c43a406b2?auto=format&fit=crop&w=600&q=80"
        },
        {
            "id": "SP_FB_02", "product_id": "SP_FB_02",
            "title": "Nivia Pro Carbonite Match Cleats Turf Football Shoes with Rubber Studs",
            "category": "Sports", "subcategory": "Football", "brand": "Nivia", "price": 999.0, "rating": 4.6,
            "description": "Lightweight TPU upper soccer cleats with multi-directional studs for optimum traction on grass and artificial turf pitches.",
            "image_url": "https://images.unsplash.com/photo-1511886929837-354d827aae26?auto=format&fit=crop&w=600&q=80"
        },

        # Badminton
        {
            "id": "SP_BM_01", "product_id": "SP_BM_01",
            "title": "Yonex Astrox 77 Play High Modulus Graphite Badminton Racket with Full Cover",
            "category": "Sports", "subcategory": "Badminton", "brand": "Yonex", "price": 2699.0, "rating": 4.8,
            "description": "Yonex rotational generator system head-heavy graphite racket designed for powerful steep smashes and fast counter-attacks.",
            "image_url": "https://images.unsplash.com/photo-1626224583764-f87db24ac4ea?auto=format&fit=crop&w=600&q=80"
        },
        {
            "id": "SP_BM_02", "product_id": "SP_BM_02",
            "title": "Yonex Nanoray 18i Light Carbon Graphite Badminton Racket (77g Strung)",
            "category": "Sports", "subcategory": "Badminton", "brand": "Yonex", "price": 1499.0, "rating": 4.7,
            "description": "Ultra-lightweight 5U (77 grams) graphite badminton racket with aero-box frame for lightning fast swing speeds and easy defensive clears.",
            "image_url": "https://images.unsplash.com/photo-1626224583764-f87db24ac4ea?auto=format&fit=crop&w=600&q=80"
        },
        {
            "id": "SP_BM_03", "product_id": "SP_BM_03",
            "title": "Yonex Mavis 350 Nylon Shuttlecock Yellow 6-Pack Fast Recovery",
            "category": "Sports", "subcategory": "Badminton", "brand": "Yonex", "price": 649.0, "rating": 4.9,
            "description": "The benchmark nylon shuttlecock worldwide, featuring natural cork base and precision wing rib structure for flight stability.",
            "image_url": "https://images.unsplash.com/photo-1626224583764-f87db24ac4ea?auto=format&fit=crop&w=600&q=80"
        },

        # Gym Equipment
        {
            "id": "SP_GM_01", "product_id": "SP_GM_01",
            "title": "Boldfit Cast Iron Rubber Encased Hex Dumbbells 5kg Pair for Home Workout",
            "category": "Sports", "subcategory": "Gym Equipment", "brand": "Boldfit", "price": 1399.0, "rating": 4.7,
            "description": "Solid cast iron hexagonal dumbbells with thick durable rubber coating, ergonomic knurled chrome handles to prevent rolling.",
            "image_url": "https://images.unsplash.com/photo-1584735935682-2f2b69dff9d2?auto=format&fit=crop&w=600&q=80"
        },
        {
            "id": "SP_GM_02", "product_id": "SP_GM_02",
            "title": "Strauss 20kg PVC Weight Plates Dumbbells and Barbell Combo Set with Connector",
            "category": "Sports", "subcategory": "Gym Equipment", "brand": "Strauss", "price": 1199.0, "rating": 4.4,
            "description": "Versatile 20kg home gym set with 2 dumbbell rods, foam padded barbell connector rod, star collars, and floor-safe weight plates.",
            "image_url": "https://images.unsplash.com/photo-1517838277536-f5f99be501cd?auto=format&fit=crop&w=600&q=80"
        },
        {
            "id": "SP_GM_03", "product_id": "SP_GM_03",
            "title": "Boldfit Heavy Duty Resistance Bands Set of 5 with Handles Door Anchor & Ankle Straps",
            "category": "Sports", "subcategory": "Gym Equipment", "brand": "Boldfit", "price": 699.0, "rating": 4.7,
            "description": "100% natural latex resistance tube set with 150 lbs stackable tension, cushioned foam handles, door anchor, and carrying pouch.",
            "image_url": "https://images.unsplash.com/photo-1517838277536-f5f99be501cd?auto=format&fit=crop&w=600&q=80"
        },

        # Running
        {
            "id": "SP_RN_01", "product_id": "SP_RN_01",
            "title": "Nike Men's Revolution 6 Next Nature Lightweight Road Running Shoes",
            "category": "Sports", "subcategory": "Running", "brand": "Nike", "price": 2899.0, "rating": 4.6,
            "description": "Nike plush foam midsole running shoes with breathable mesh forefoot, padded collar, and flexible traction rubber outsole.",
            "image_url": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=600&q=80"
        },
        {
            "id": "SP_RN_02", "product_id": "SP_RN_02",
            "title": "Asics Men's Gel-Contend 8 Rearfoot Cushioning Road Running Shoes",
            "category": "Sports", "subcategory": "Running", "brand": "Asics", "price": 3199.0, "rating": 4.7,
            "description": "Asics signature GEL cushioning running shoes with AmpliFoam midsole and OrthoLite sockliner for long distance impact protection.",
            "image_url": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=600&q=80"
        },

        # Cycling
        {
            "id": "SP_CY_01", "product_id": "SP_CY_01",
            "title": "Hercules Roadeo 21-Speed Shimano Gears Mountain Bicycle 27.5T Dual Disc Brakes",
            "category": "Sports", "subcategory": "Cycling", "brand": "Hercules", "price": 12499.0, "rating": 4.6,
            "description": "Rugged alloy hardtail mountain bike with 21-speed Shimano derailleur, front zoom suspension, and responsive dual mechanical disc brakes.",
            "image_url": "https://images.unsplash.com/photo-1485965120184-e220f721d03e?auto=format&fit=crop&w=600&q=80"
        },
        {
            "id": "SP_CY_02", "product_id": "SP_CY_02",
            "title": "Boldfit Aerodynamic Cycling Helmet with Rear Safety Warning LED Light and Visor",
            "category": "Sports", "subcategory": "Cycling", "brand": "Boldfit", "price": 1099.0, "rating": 4.7,
            "description": "In-mold EPS foam cycling helmet with 18 ventilation cooling channels, removable sun visor, and 3-mode rechargeable rear red LED safety light.",
            "image_url": "https://images.unsplash.com/photo-1558060370-d644479cb6f7?auto=format&fit=crop&w=600&q=80"
        },

        # Yoga
        {
            "id": "SP_YG_01", "product_id": "SP_YG_01",
            "title": "Boldfit Eco-Friendly Non-Slip TPE Yoga Mat 6mm with Alignment Lines & Carry Strap",
            "category": "Sports", "subcategory": "Yoga", "brand": "Boldfit", "price": 899.0, "rating": 4.8,
            "description": "Dual-layer textured non-slip TPE yoga mat with body alignment lines for perfect posture, tear-resistant mesh, and waterproof sweat resistance.",
            "image_url": "https://images.unsplash.com/photo-1518611012118-696072aa579a?auto=format&fit=crop&w=600&q=80"
        },

        # Swimming
        {
            "id": "SP_SW_01", "product_id": "SP_SW_01",
            "title": "Speedo Futura Biofuse Flexiseal Anti-Fog UV Protection Swimming Goggles",
            "category": "Sports", "subcategory": "Swimming", "brand": "Speedo", "price": 1199.0, "rating": 4.8,
            "description": "Speedo Biofuse flexible gel seal swimming goggles with wide vision anti-fog treated lenses, 100% UV protection and easy push-button strap adjustment.",
            "image_url": "https://images.unsplash.com/photo-1530549387789-4c1017266635?auto=format&fit=crop&w=600&q=80"
        },

        # =====================================================================
        # ELECTRONICS: LAPTOPS, SMARTPHONES, CAMERAS, AUDIO, TV, SMARTWATCHES
        # =====================================================================
        # Laptops
        {
            "id": "LAP_ASUS_01", "product_id": "LAP_ASUS_01",
            "title": "ASUS Vivobook 15 (15.6-inch FHD, Intel Core i5-1235U 12th Gen, 16GB RAM, 512GB SSD)",
            "category": "Laptops", "subcategory": "Laptop", "brand": "Asus", "price": 48990.0, "rating": 4.6,
            "description": "ASUS Vivobook 15 lightweight laptop with 12th Gen Intel Core i5-1235U, 16GB DDR4 RAM, 512GB PCIe 4.0 SSD, fingerprint reader, Windows 11 Home & Office 2021.",
            "image_url": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=600&q=80"
        },
        {
            "id": "LAP_DELL_02", "product_id": "LAP_DELL_02",
            "title": "Dell 15 Laptop (Intel Core i3-1215U, 8GB DDR4, 512GB SSD, 15.6-inch FHD 120Hz)",
            "category": "Laptops", "subcategory": "Laptop", "brand": "Dell", "price": 34990.0, "rating": 4.4,
            "description": "Dell Inspiron 15 with 12th Gen Intel Core i3, 120Hz anti-glare display, spill-resistant keyboard, ExpressCharge fast charging, Windows 11.",
            "image_url": "https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?auto=format&fit=crop&w=600&q=80"
        },
        {
            "id": "LAP_HP_03", "product_id": "LAP_HP_03",
            "title": "HP Victus Gaming Laptop (AMD Ryzen 5 5600H, 4GB RTX 3050, 16GB RAM, 512GB SSD, 144Hz)",
            "category": "Laptops", "subcategory": "Laptop", "brand": "HP", "price": 58990.0, "rating": 4.7,
            "description": "HP Victus gaming laptop with NVIDIA GeForce RTX 3050 Graphics, 144Hz IPS display, upgraded dual-fan cooling, B&O audio, and backlit keyboard.",
            "image_url": "https://images.unsplash.com/photo-1603302576837-37561b2e2302?auto=format&fit=crop&w=600&q=80"
        },
        {
            "id": "LAP_APPLE_04", "product_id": "LAP_APPLE_04",
            "title": "Apple MacBook Air M2 Chip (13.6-inch Liquid Retina, 8GB Unified Memory, 256GB SSD)",
            "category": "Laptops", "subcategory": "Laptop", "brand": "Apple", "price": 84990.0, "rating": 4.9,
            "description": "Apple MacBook Air with M2 chip, 18-hour all-day battery life, MagSafe charging, 1080p FaceTime HD camera, spatial audio four-speaker system.",
            "image_url": "https://images.unsplash.com/photo-1611186871348-b1ce696e52c9?auto=format&fit=crop&w=600&q=80"
        },

        # Smartphones
        {
            "id": "MOB_SAMS_01", "product_id": "MOB_SAMS_01",
            "title": "Samsung Galaxy M34 5G (Prism Silver, 8GB RAM, 128GB Storage) | 50MP OIS Camera | 6000mAh",
            "category": "Smartphones", "subcategory": "Smartphone", "brand": "Samsung", "price": 16499.0, "rating": 4.5,
            "description": "Samsung Galaxy M34 5G with 120Hz FHD+ Super AMOLED display, 50MP No Shake OIS camera, monster 6000mAh battery, Gorilla Glass 5.",
            "image_url": "https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?auto=format&fit=crop&w=600&q=80"
        },
        {
            "id": "MOB_ONEP_02", "product_id": "MOB_ONEP_02",
            "title": "OnePlus Nord CE 3 Lite 5G (Pastel Lime, 8GB RAM, 128GB) | 108MP Camera | 67W SUPERVOOC",
            "category": "Smartphones", "subcategory": "Smartphone", "brand": "OnePlus", "price": 17999.0, "rating": 4.5,
            "description": "OnePlus Nord CE 3 Lite 5G with 108MP primary camera, 67W SUPERVOOC fast charging, 5000mAh battery, Qualcomm Snapdragon 695 5G.",
            "image_url": "https://images.unsplash.com/photo-1592899677977-9c10ca588bbd?auto=format&fit=crop&w=600&q=80"
        },
        {
            "id": "MOB_APPLE_03", "product_id": "MOB_APPLE_03",
            "title": "Apple iPhone 15 (128 GB) - Black | Dynamic Island | 48MP Main Camera | USB-C",
            "category": "Smartphones", "subcategory": "Smartphone", "brand": "Apple", "price": 69900.0, "rating": 4.8,
            "description": "Apple iPhone 15 with Dynamic Island, 48MP main camera with 2x telephoto, durable color-infused back glass, A16 Bionic chip, and USB-C connector.",
            "image_url": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?auto=format&fit=crop&w=600&q=80"
        },

        # Audio & Earbuds
        {
            "id": "AUD_BOAT_01", "product_id": "AUD_BOAT_01",
            "title": "boAt Airdopes 141 ANC True Wireless Earbuds with 32dB Active Noise Cancellation",
            "category": "Audio", "subcategory": "Earbuds", "brand": "boAt", "price": 1499.0, "rating": 4.4,
            "description": "boAt Airdopes 141 with 32dB active noise cancellation, ENx quad mic technology for crystal clear calling, 42-hour playtime, low latency gaming mode.",
            "image_url": "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?auto=format&fit=crop&w=600&q=80"
        },
        {
            "id": "AUD_SONY_02", "product_id": "AUD_SONY_02",
            "title": "Sony WF-C700N Truly Wireless Active Noise Cancelling Bluetooth Earbuds (Multipoint)",
            "category": "Audio", "subcategory": "Earbuds", "brand": "Sony", "price": 6990.0, "rating": 4.7,
            "description": "Sony premium ANC wireless earbuds with DSEE sound engine, 360 Reality Audio, IPX4 water resistance, and 15-hour battery life with quick charging.",
            "image_url": "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?auto=format&fit=crop&w=600&q=80"
        },

        # Beauty
        {
            "id": "BEAU_FW_01", "product_id": "BEAU_FW_01",
            "title": "Himalaya Purifying Neem Face Wash for Acne-Prone & Oily Skin (150ml)",
            "category": "Beauty", "subcategory": "Face Wash", "brand": "Himalaya", "price": 199.0, "rating": 4.6,
            "description": "Herbal soap-free neem and turmeric formulation that removes excess oil and impurities to prevent breakouts without over-drying.",
            "image_url": "https://images.unsplash.com/photo-1556228720-195a672e8a03?auto=format&fit=crop&w=600&q=80"
        },
        {
            "id": "BEAU_MOIST_02", "product_id": "BEAU_MOIST_02",
            "title": "Cetaphil Daily Hydrating Moisturizing Cream for Dry to Sensitive Skin (250g)",
            "category": "Beauty", "subcategory": "Moisturizer", "brand": "Cetaphil", "price": 499.0, "rating": 4.8,
            "description": "Dermatologist-tested non-comedogenic rich moisturizing cream with sweet almond oil and Vitamin E for 48-hour continuous skin barrier hydration.",
            "image_url": "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?auto=format&fit=crop&w=600&q=80"
        },
        {
            "id": "BEAU_SUN_03", "product_id": "BEAU_SUN_03",
            "title": "Minimalist Sunscreen SPF 50 PA++++ with Niacinamide & Multi-Vitamins (50g)",
            "category": "Beauty", "subcategory": "Sunscreen", "brand": "Minimalist", "price": 399.0, "rating": 4.7,
            "description": "Broad-spectrum hybrid chemical & physical sunscreen with lightweight non-greasy texture that leaves zero white cast.",
            "image_url": "https://images.unsplash.com/photo-1598440947619-2c35fc9aa908?auto=format&fit=crop&w=600&q=80"
        },

        # Toys
        {
            "id": "TOY_LEGO_01", "product_id": "TOY_LEGO_01",
            "title": "LEGO Classic Medium Creative Brick Box 10696 Building Toy Set (484 Pieces)",
            "category": "Toys", "subcategory": "Building Blocks", "brand": "LEGO", "price": 2799.0, "rating": 4.8,
            "description": "LEGO Classic creative brick box with 484 pieces in 35 different colors, including windows, eyes, wheels, and green baseplate for open-ended creative construction.",
            "image_url": "https://images.unsplash.com/photo-1585366119957-e9730b6d0f60?auto=format&fit=crop&w=600&q=80"
        },
        {
            "id": "TOY_RC_02", "product_id": "TOY_RC_02",
            "title": "Wembley 1:18 High Speed Remote Control Racing Car with LED Headlights",
            "category": "Toys", "subcategory": "RC Toys", "brand": "Wembley", "price": 799.0, "rating": 4.5,
            "description": "Fast 2.4GHz remote control sports racing car with 4-wheel suspension, rubber grip tires, bright LED headlights, and USB rechargeable battery.",
            "image_url": "https://images.unsplash.com/photo-1594787318286-3d835c1d207f?auto=format&fit=crop&w=600&q=80"
        },
    ]
    return pd.DataFrame(curated)


def main():
    print("=" * 60)
    print("CREATING MASTER CATALOG FROM REAL DATASETS WITH SUBCATEGORIES")
    print("=" * 60)

    # 1. Load real fashion dataset
    df_fashion = load_real_fashion_dataset()

    # 2. Load comprehensive curated products
    df_curated = get_curated_catalog()
    print(f"Loaded {len(df_curated)} curated real products across Home & Kitchen, Books, Sports, Electronics, Mobiles, Beauty, Toys")

    # 3. Combine both
    combined_df = pd.concat([df_fashion, df_curated], ignore_index=True)

    # 4. Remove duplicates by ID and Title
    combined_df = combined_df.drop_duplicates(subset=["id"])
    combined_df = combined_df.drop_duplicates(subset=["title"])

    # 5. Clean invalid / non-positive prices
    combined_df["price"] = pd.to_numeric(combined_df["price"], errors="coerce").fillna(499.0)
    combined_df = combined_df[combined_df["price"] > 0]

    # 6. Clean ratings
    combined_df["rating"] = pd.to_numeric(combined_df["rating"], errors="coerce").fillna(4.2)
    combined_df["rating"] = combined_df["rating"].clip(1.0, 5.0)

    # 7. Ensure non-null description and title
    combined_df["title"] = combined_df["title"].astype(str).str.strip()
    combined_df["description"] = combined_df["description"].astype(str).str.strip()
    combined_df = combined_df[combined_df["title"].str.len() > 3]

    # Ensure required columns
    required_cols = ["id", "product_id", "title", "category", "subcategory", "brand", "price", "rating", "description", "image_url"]
    for col in required_cols:
        if col not in combined_df.columns:
            combined_df[col] = ""

    output_path = DATA_DIR / "master_catalog.csv"
    combined_df[required_cols].to_csv(output_path, index=False, encoding="utf-8")

    print("\n" + "=" * 60)
    print(f"SUCCESS: Generated {output_path}")
    print(f"Total Products: {len(combined_df)}")
    print("\nCategory Distribution:")
    print(combined_df["category"].value_counts())
    print("\nSubcategory Distribution:")
    print(combined_df["subcategory"].value_counts())
    print("=" * 60)


if __name__ == "__main__":
    main()
