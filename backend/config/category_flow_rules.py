"""
Category Flow Rules Configuration for ShopAI GenAI Shopping Assistant
Defines curated conversational shopping journeys, interactive question trees,
category priorities, and use-case prompts mirroring Amazon, Flipkart, and Perplexity Shopping.
"""

from typing import Dict, List, Any, Optional

SHOPPING_WELCOME_FLOW = {
    "title": "Welcome to ShopAI 👋",
    "message": (
        "Welcome to **ShopAI** 👋 your personal GenAI Shopping Assistant!\n\n"
        "What are you shopping for today?\n\n"
        "**Popular Shopping Categories:**\n"
        "• 🍳 **Home & Kitchen** (Cookware, Appliances, Decor, Furniture)\n"
        "• 📚 **Books** (Programming, AI/ML, Business, Self-Help, Novels)\n"
        "• 🏃 **Sports & Fitness** (Cricket, Football, Badminton, Gym, Yoga)\n"
        "• 💻 **Laptops** (Coding, Gaming, College, Video Editing)\n"
        "• 📱 **Smartphones** (Camera, Battery, Performance, Gaming)\n"
        "• 👗 **Fashion & Shoes** (Sneakers, Running, Formal, Jeans, Tops)\n"
        "• ✨ **Beauty & Skincare** (Face Wash, Moisturizer, Sunscreen)\n"
        "• 🎧 **Audio** (ANC Earbuds, Headphones, Speakers)\n\n"
        "Tell me what you're looking for or select an option below to get started!"
    ),
    "options": [
        "🍳 Home & Kitchen",
        "📚 Books",
        "🏃 Sports",
        "💻 Laptops",
        "📱 Smartphones",
        "👗 Fashion & Shoes",
        "✨ Beauty",
        "🎧 Audio",
    ]
}

CATEGORY_SHOPPING_FLOWS: Dict[str, Dict[str, Any]] = {
    "Home & Kitchen": {
        "display_name": "Home & Kitchen",
        "emoji": "🍳",
        "steps": [
            {
                "step_name": "product_type",
                "question": "What are you looking for?",
                "options": [
                    "🍳 Cookware",
                    "⚡ Kitchen Appliances",
                    "🏺 Home Decor",
                    "🛋️ Furniture",
                    "🧹 Cleaning Supplies",
                    "🛏️ Bedsheets & Curtains",
                    "💡 Lighting",
                    "🍶 Storage & Bottles",
                ],
            },
            {
                "step_name": "budget",
                "question": "Select your budget.",
                "options": [
                    "Under ₹500",
                    "Under ₹1,000",
                    "Under ₹2,500",
                    "Under ₹5,000",
                    "Under ₹10,000",
                    "Premium",
                ],
            },
        ],
    },
    "Books": {
        "display_name": "Books & Learning",
        "emoji": "📚",
        "steps": [
            {
                "step_name": "genre",
                "question": "What kind of books are you interested in?",
                "options": [
                    "🐍 Programming",
                    "📊 Data Science",
                    "🤖 AI & ML",
                    "💼 Business & Finance",
                    "🧠 Self Help & Growth",
                    "🎯 Interview Preparation",
                    "🏛️ UPSC / GATE / JEE",
                    "📖 Novels & Fiction",
                ],
            },
            {
                "step_name": "budget",
                "question": "What is your budget per book?",
                "options": [
                    "Under ₹200",
                    "Under ₹500",
                    "Under ₹1,000",
                    "Premium Editions",
                ],
            },
        ],
    },
    "Sports": {
        "display_name": "Sports & Fitness",
        "emoji": "🏃",
        "steps": [
            {
                "step_name": "sport_type",
                "question": "Which sport are you interested in?",
                "options": [
                    "🏏 Cricket",
                    "⚽ Football",
                    "🏸 Badminton",
                    "🏋️ Gym Equipment",
                    "🏃 Running & Fitness",
                    "🧘 Yoga",
                    "🚴 Cycling",
                    "🏊 Swimming",
                    "🏀 Basketball",
                    "🎾 Tennis",
                ],
            },
            {
                "step_name": "budget",
                "question": "What is your target budget?",
                "options": [
                    "Under ₹500",
                    "Under ₹1,500",
                    "Under ₹3,000",
                    "Under ₹5,000",
                    "Premium Sports",
                ],
            },
        ],
    },
    "Laptops": {
        "display_name": "Laptops & Computers",
        "emoji": "💻",
        "steps": [
            {
                "step_name": "purpose",
                "question": "What will you primarily use it for?",
                "options": [
                    "👨‍💻 Coding & Programming",
                    "🎮 Gaming & High Graphics",
                    "🎬 Video Editing & Design",
                    "🎓 College & Student",
                    "💼 Office Work & Productivity",
                ],
            },
            {
                "step_name": "budget",
                "question": "What's your preferred price range?",
                "options": [
                    "Under ₹30,000",
                    "Under ₹50,000",
                    "Under ₹70,000",
                    "Under ₹1 Lakh",
                    "Premium Workstations",
                ],
            },
        ],
    },
    "Smartphones": {
        "display_name": "Smartphones & Mobiles",
        "emoji": "📱",
        "steps": [
            {
                "step_name": "priority",
                "question": "What's more important?",
                "options": [
                    "📸 Camera & Photography",
                    "🔋 2-Day Battery Life",
                    "⚡ Performance & 5G",
                    "🎮 Gaming & High FPS",
                    "✨ AI Features & Flagship",
                ],
            },
            {
                "step_name": "budget",
                "question": "What's your target smartphone budget?",
                "options": [
                    "Under ₹10k",
                    "Under ₹20k",
                    "Under ₹30k",
                    "Under ₹50k",
                    "Premium Flagships",
                ],
            },
        ],
    },
    "Shoes": {
        "display_name": "Footwear & Shoes",
        "emoji": "👟",
        "steps": [
            {
                "step_name": "shoe_type",
                "question": "Which type of shoes are you looking for?",
                "options": [
                    "🏃 Running Shoes",
                    "👟 Casual Sneakers",
                    "👞 Formal Shoes",
                    "⚽ Sports & Training",
                    "🥾 Trekking & Outdoor",
                ],
            },
            {
                "step_name": "budget",
                "question": "What is your target budget?",
                "options": [
                    "Under ₹500",
                    "Under ₹1,000",
                    "Under ₹2,000",
                    "Under ₹5,000",
                    "Premium Choice",
                ],
            },
        ],
    },
    "Fashion": {
        "display_name": "Fashion & Apparel",
        "emoji": "👗",
        "steps": [
            {
                "step_name": "product_type",
                "question": "What type of fashion products are you looking for?",
                "options": ["👖 Jeans", "👕 T-Shirts", "👚 Tops", "👔 Shirts", "👗 Dresses", "👟 Footwear", "🧥 Jackets"],
            },
            {
                "step_name": "gender",
                "question": "Who are you shopping for?",
                "options": ["Men", "Women", "Unisex", "Kids"],
            },
            {
                "step_name": "budget",
                "question": "What is your target budget?",
                "options": ["Under ₹500", "Under ₹1,000", "Under ₹2,000", "Under ₹5,000", "Premium Choice"],
            },
        ],
    },
    "Beauty": {
        "display_name": "Beauty & Personal Care",
        "emoji": "✨",
        "steps": [
            {
                "step_name": "product_type",
                "question": "What type of beauty & personal care products are you looking for?",
                "options": ["🧴 Face Wash", "💧 Moisturizers", "💄 Lipsticks", "🌸 Perfumes", "☀️ Sunscreens", "✨ Serums"],
            },
            {
                "step_name": "skin_type",
                "question": "What is your preference or skin type?",
                "options": ["All Skin Types", "Oily & Acne Prone", "Dry & Sensitive", "Long Lasting Matte"],
            },
            {
                "step_name": "budget",
                "question": "What is your target budget?",
                "options": ["Under ₹200", "Under ₹500", "Under ₹1,000", "Under ₹2,000", "Premium Beauty"],
            },
        ],
    },
    "Audio": {
        "display_name": "Audio & Headphones",
        "emoji": "🎧",
        "steps": [
            {
                "step_name": "audio_type",
                "question": "What type of audio device do you need?",
                "options": ["🎵 True Wireless Earbuds (TWS)", "🎧 Over-Ear ANC Headphones", "🏃 Wireless Neckband", "🔊 Bluetooth Speaker"],
            },
            {
                "step_name": "budget",
                "question": "What's your budget?",
                "options": ["Under ₹1,500", "Under ₹3,000", "Under ₹5,000", "Premium Hi-Fi"],
            },
        ],
    },
    "Toys": {
        "display_name": "Toys & Games",
        "emoji": "🧸",
        "steps": [
            {
                "step_name": "toy_type",
                "question": "What type of toys or games are you looking for?",
                "options": ["🧱 LEGO & Building Blocks", "🏎️ Remote Control Cars", "🎲 Board Games", "🦸 Action Figures", "🧸 Soft Toys", "🔬 STEM Kits"],
            },
            {
                "step_name": "budget",
                "question": "What is your target budget?",
                "options": ["Under ₹300", "Under ₹500", "Under ₹1,000", "Under ₹2,000", "Premium Collections"],
            },
        ],
    },
    "Cameras": {
        "display_name": "Cameras & Photography",
        "emoji": "📷",
        "steps": [
            {
                "step_name": "camera_type",
                "question": "What type of camera are you looking for?",
                "options": ["📸 DSLR Camera", "✨ Mirrorless Camera", "🎥 Vlogging Camera", "🏃 Action Camera"],
            },
            {
                "step_name": "budget",
                "question": "What's your camera budget?",
                "options": ["Under ₹25,000", "Under ₹50,000", "Under ₹75,000", "₹1 Lakh+"],
            },
        ],
    },
}


def normalize_category_name(category: Optional[str]) -> str:
    """Normalizes various user inputs to standard flow categories."""
    if not category:
        return "General"
    cat_lower = category.strip().lower()
    if cat_lower in ["home", "kitchen", "home & kitchen", "home and kitchen", "cookware", "appliances", "home decor", "furniture", "bedsheets"]:
        return "Home & Kitchen"
    elif cat_lower in ["book", "books", "reading", "study material", "novel", "novels", "textbook"]:
        return "Books"
    elif cat_lower in ["sport", "sports", "fitness", "gym", "workout", "exercise", "cricket", "football", "badminton", "yoga"]:
        return "Sports"
    elif cat_lower in ["beauty", "skincare", "makeup", "cosmetics", "perfume", "fragrance", "face wash", "moisturizer", "sunscreen", "lipstick"]:
        return "Beauty"
    elif cat_lower in ["shoe", "shoes", "footwear", "sneakers", "sneaker", "boots"]:
        return "Shoes"
    elif cat_lower in ["fashion", "clothing", "clothes", "apparel", "wear", "jeans", "shirt", "t-shirt"]:
        return "Fashion"
    elif cat_lower in ["smartphone", "smartphones", "phone", "phones", "mobile", "mobiles"]:
        return "Smartphones"
    elif cat_lower in ["laptop", "laptops", "notebook", "computer", "pc"]:
        return "Laptops"
    elif cat_lower in ["camera", "cameras", "dslr", "mirrorless"]:
        return "Cameras"
    elif cat_lower in ["audio", "earbuds", "earbud", "headphones", "headphone", "airpods", "speaker"]:
        return "Audio"
    elif cat_lower in ["toy", "toys", "game", "games", "lego", "board games", "puzzle", "action figure"]:
        return "Toys"
    elif cat_lower in ["electronics", "tech", "gadget"]:
        return "Electronics"
    return category.strip()


def get_flow_for_category(category: str) -> Optional[Dict[str, Any]]:
    """Returns flow configuration for a normalized category."""
    norm = normalize_category_name(category)
    return CATEGORY_SHOPPING_FLOWS.get(norm)
