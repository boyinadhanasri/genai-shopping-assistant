import os
import uuid
import logging
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, Query, Body, Depends
import pandas as pd
from backend.auth.security import get_current_user_dependency

from backend.models.product import (
    Product,
    QuerySlots,
    QueryRequest,
    QueryResponse,
    CompareRequest,
    CompareResponse,
    RegisterRequest,
    LoginRequest,
    LoginResponse,
    AuthResponse,
    UserProfile,
    ChatRequest,
    ChatResponse,
)
from backend.database.db import get_user_by_email, get_user_by_id, create_user
from backend.security.hashing import hash_password, verify_password
from backend.ai.query_understanding import understand_query
from backend.memory.conversation_store import conversation_store
from backend.search_engine import search_products, get_catalog, get_budget_fallback
from comparison.comparison_engine import build_comparison
from backend.services.analytics import log_search_event, get_analytics_summary

logger = logging.getLogger(__name__)
router = APIRouter()

SUPPORTED_CATEGORIES = [
    {"id": "home_and_kitchen", "name": "Home & Kitchen", "icon": "Home", "count": 150, "description": "Cookware, Appliances, Decor & Furniture"},
    {"id": "books", "name": "Books", "icon": "BookOpen", "count": 100, "description": "Programming, AI/ML, Business & Exams"},
    {"id": "sports", "name": "Sports", "icon": "Dumbbell", "count": 100, "description": "Cricket, Gym, Running & Yoga Gear"},
    {"id": "electronics", "name": "Electronics", "icon": "Cpu", "count": 150, "description": "Laptops, Audio, Cameras & Wearables"},
    {"id": "mobiles", "name": "Mobiles", "icon": "Smartphone", "count": 150, "description": "Smartphones & Mobile Accessories"},
    {"id": "fashion", "name": "Fashion", "icon": "Shirt", "count": 150, "description": "Apparel, Shoes & Accessories"},
    {"id": "beauty", "name": "Beauty", "icon": "Sparkles", "count": 150, "description": "Skincare, Makeup & Fragrances"},
    {"id": "toys", "name": "Toys", "icon": "Gamepad2", "count": 150, "description": "Building Blocks, Games & Action Figures"},
]

CATEGORY_IMAGE_FALLBACKS = {
    "electronics": [
        "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=600&q=80",
        "https://images.unsplash.com/photo-1546868871-7041f2a55e12?auto=format&fit=crop&w=600&q=80",
        "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=600&q=80",
    ],
    "mobiles": [
        "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?auto=format&fit=crop&w=600&q=80",
        "https://images.unsplash.com/photo-1592899677977-9c10ca588bbd?auto=format&fit=crop&w=600&q=80",
    ],
    "fashion": [
        "https://images.unsplash.com/photo-1521572267360-ee0c2909d518?auto=format&fit=crop&w=600&q=80",
        "https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=600&q=80",
    ],
    "beauty": [
        "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?auto=format&fit=crop&w=600&q=80",
        "https://images.unsplash.com/photo-1598440947619-2c35fc9aa908?auto=format&fit=crop&w=600&q=80",
    ],
    "home & kitchen": [
        "https://images.unsplash.com/photo-1556911220-e15b29be8c8f?auto=format&fit=crop&w=600&q=80",
        "https://images.unsplash.com/photo-1584269600464-37b1b58a9fe7?auto=format&fit=crop&w=600&q=80",
    ],
    "books": [
        "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?auto=format&fit=crop&w=600&q=80",
        "https://images.unsplash.com/photo-1512820790803-83ca734da794?auto=format&fit=crop&w=600&q=80",
    ],
    "sports": [
        "https://images.unsplash.com/photo-1517838277536-f5f99be501cd?auto=format&fit=crop&w=600&q=80",
        "https://images.unsplash.com/photo-1584735935682-2f2b69dff9d2?auto=format&fit=crop&w=600&q=80",
    ],
    "toys": [
        "https://images.unsplash.com/photo-1558060370-d644479cb6f7?auto=format&fit=crop&w=600&q=80",
        "https://images.unsplash.com/photo-1566576912321-d58ddd7a6088?auto=format&fit=crop&w=600&q=80",
    ],
}


def _enrich_product(p: Product) -> Product:
    """Ensures product has a valid image and reasons."""
    if not p.image_url or not p.image_url.startswith("http"):
        cat_key = p.category.strip().lower()
        images = CATEGORY_IMAGE_FALLBACKS.get(cat_key, CATEGORY_IMAGE_FALLBACKS.get("electronics", []))
        idx = abs(hash(p.id)) % len(images) if images else 0
        p.image_url = images[idx] if images else ""

    if not p.why_recommended:
        p.why_recommended = [
            f"Rated ★ {p.rating:.1f}/5.0 by verified shoppers",
            f"Competitive price point in {p.category}",
            f"Verified specifications from {p.brand}"
        ]
    return p


# 1. Authentication Endpoints

# 1.1 User Registration (POST /api/auth/register)
@router.post("/api/auth/register", response_model=AuthResponse)
def register(request: RegisterRequest) -> AuthResponse:
    name = (request.name or "").strip()
    email = (request.email or "").strip().lower()
    password = request.password or ""
    confirm_password = request.confirm_password or ""

    # Validation: empty fields
    if not name:
        return AuthResponse(success=False, message="Full Name is required.")
    if not email:
        return AuthResponse(success=False, message="Email address is required.")
    if not password:
        return AuthResponse(success=False, message="Password is required.")
    if not confirm_password:
        return AuthResponse(success=False, message="Please confirm your password.")

    # Validation: password match
    if password != confirm_password:
        return AuthResponse(success=False, message="Passwords do not match.")

    # Validation: password strength minimum
    if len(password) < 4:
        return AuthResponse(success=False, message="Password must be at least 4 characters long.")

    # Duplicate Email Check
    existing_user = get_user_by_email(email)
    if existing_user:
        return AuthResponse(
            success=False,
            message="An account with this email already exists. Please sign in or use a different email."
        )

    # Hash Password and Store User
    try:
        pw_hash = hash_password(password)
        new_user = create_user(name=name, email=email, password_hash=pw_hash)
        
        token = f"jwt_{uuid.uuid4().hex}"
        user_profile = UserProfile(
            id=new_user["id"],
            name=new_user["name"],
            email=new_user["email"],
            avatar=f"https://api.dicebear.com/7.x/avataaars/svg?seed={new_user['name']}",
        )

        return AuthResponse(
            success=True,
            message="Registration successful",
            token=token,
            user=user_profile
        )
    except Exception as e:
        logger.error(f"Registration error: {e}")
        return AuthResponse(success=False, message="Registration failed. Please try again.")


# 1.2 User Login (POST /api/auth/login)
@router.post("/api/auth/login", response_model=LoginResponse)
def login(request: LoginRequest) -> LoginResponse:
    email = (request.email or "").strip().lower()
    password = request.password or ""

    if not email:
        return LoginResponse(success=False, message="Email address is required.")
    if not password:
        return LoginResponse(success=False, message="Password is required.")

    # Lookup user by email in database
    user = get_user_by_email(email)
    if not user:
        return LoginResponse(success=False, message="Account not found.")

    # Verify hashed password
    if not verify_password(password, user["password_hash"]):
        return LoginResponse(success=False, message="Incorrect password.")

    # Successful login
    token = f"jwt_{uuid.uuid4().hex}"
    user_profile = UserProfile(
        id=user["id"],
        name=user["name"],
        email=user["email"],
        avatar=f"https://api.dicebear.com/7.x/avataaars/svg?seed={user['name']}",
    )

    return LoginResponse(
        success=True,
        message="Login successful",
        token=token,
        user=user_profile
    )


# 2. Categories
@router.get("/api/categories")
def get_categories():
    return {"categories": SUPPORTED_CATEGORIES}


# 3. Product Catalog List (GET /api/products)
@router.get("/api/products")
def list_products(
    category: Optional[str] = Query(None, description="Category filter"),
    limit: int = Query(20, description="Items limit"),
    offset: int = Query(0, description="Offset index")
):
    catalog_df = get_catalog()
    filtered = catalog_df
    if category:
        filtered = catalog_df[catalog_df["category"].str.lower() == category.strip().lower()]

    total = len(filtered)
    rows = filtered.iloc[offset:offset+limit].to_dict(orient="records")

    prods = []
    for r in rows:
        p = Product(
            id=str(r["product_id"]),
            category=str(r["category"]),
            brand=str(r["brand"]),
            title=str(r["title"]),
            price=float(r["price"]),
            rating=float(r["rating"]),
            description=str(r["description"]),
            image_url=str(r.get("image_url", "")),
            source=str(r.get("source", "Flipkart")),
        )
        prods.append(_enrich_product(p))

    return {"total": total, "limit": limit, "offset": offset, "products": prods}


# 4. Trending Products
@router.get("/api/products/trending")
def get_trending_products(
    category: Optional[str] = Query(None, description="Category filter"),
    limit: int = Query(8, description="Number of items")
):
    catalog_df = get_catalog()
    df = catalog_df

    if category and category.strip().lower() not in ["all", "any", "general"]:
        cat_clean = category.strip().lower()
        cat_match = df[df["category"].str.lower() == cat_clean]
        if cat_match.empty:
            cat_match = df[df["category"].str.lower().str.replace("&", "and").str.replace(" ", "_") == cat_clean.replace("&", "and").replace(" ", "_")]
        if cat_match.empty:
            cat_match = df[df["subcategory"].str.lower() == cat_clean]
        if not cat_match.empty:
            df = cat_match

    # High-rated items in that category
    high_rated = df[df["rating"] >= 4.5].copy()
    if high_rated.empty:
        high_rated = df.sort_values(by="rating", ascending=False)
    
    sample_size = min(len(high_rated), limit)
    selected_rows = high_rated.head(limit * 2)
    if len(selected_rows) > sample_size:
        sampled = selected_rows.sample(sample_size)
    else:
        sampled = selected_rows.head(sample_size)

    prods = []
    for _, r in sampled.iterrows():
        p = Product(
            id=str(r.get("product_id") or r.get("id")),
            category=str(r["category"]),
            brand=str(r["brand"]),
            title=str(r["title"]),
            price=float(r["price"]),
            rating=float(r["rating"]),
            description=str(r["description"]),
            image_url=str(r.get("image_url", "")),
            source=str(r.get("source", "Real Catalog")),
        )
        prods.append(_enrich_product(p))

    return {"products": prods}


# 5. Recommended Products
@router.get("/api/products/recommended")
def get_recommended_products(
    category: Optional[str] = Query(None, description="Category filter"),
    limit: int = Query(12, description="Number of items")
):
    catalog_df = get_catalog()
    df = catalog_df

    if category and category.strip().lower() not in ["all", "any", "general"]:
        cat_clean = category.strip().lower()
        cat_match = df[df["category"].str.lower() == cat_clean]
        if cat_match.empty:
            cat_match = df[df["category"].str.lower().str.replace("&", "and").str.replace(" ", "_") == cat_clean.replace("&", "and").replace(" ", "_")]
        if cat_match.empty:
            cat_match = df[df["subcategory"].str.lower() == cat_clean]
        if not cat_match.empty:
            df = cat_match

    sample_size = min(len(df), limit)
    # Give priority to top rated items in the category
    top_candidates = df.sort_values(by="rating", ascending=False).head(max(sample_size * 2, sample_size))
    if len(top_candidates) > sample_size:
        sampled = top_candidates.sample(sample_size)
    else:
        sampled = top_candidates

    prods = []
    for _, r in sampled.iterrows():
        p = Product(
            id=str(r.get("product_id") or r.get("id")),
            category=str(r["category"]),
            brand=str(r["brand"]),
            title=str(r["title"]),
            price=float(r["price"]),
            rating=float(r["rating"]),
            description=str(r["description"]),
            image_url=str(r.get("image_url", "")),
            source=str(r.get("source", "Real Catalog")),
        )
        prods.append(_enrich_product(p))

    return {"products": prods}


# 5.1 Category Budget Rules Configuration
@router.get("/api/config/budget-rules")
def get_category_budget_rules():
    from backend.config.category_budget_rules import CATEGORY_BUDGET_TIERS
    return {"budget_rules": CATEGORY_BUDGET_TIERS}


# 6. Single Product Details
@router.get("/api/products/{product_id}")
def get_product_details(product_id: str):
    catalog_df = get_catalog()
    match = catalog_df[catalog_df["product_id"] == product_id]
    if match.empty:
        raise HTTPException(status_code=404, detail=f"Product with id '{product_id}' not found")

    r = match.iloc[0]
    p = Product(
        id=str(r["product_id"]),
        category=str(r["category"]),
        brand=str(r["brand"]),
        title=str(r["title"]),
        price=float(r["price"]),
        rating=float(r["rating"]),
        description=str(r["description"]),
        image_url=str(r.get("image_url", "")),
        source=str(r.get("source", "ShopAI Catalog")),
    )
    return _enrich_product(p)


# 7. Query Search (/api/query)
@router.post("/api/query", response_model=QueryResponse)
def query_catalog(
    request: QueryRequest,
    current_user: dict = Depends(get_current_user_dependency)
) -> QueryResponse:
    parsed = understand_query(request.query, request.category)
    slots = QuerySlots(
        category=parsed.get("category") or request.category or "General",
        budget_max=parsed.get("budget"),
        raw_query=request.query
    )

    extracted_dict = {
        "category": slots.category,
        "budget": slots.budget_max
    }
    if parsed.get("subcategory"):
        extracted_dict["subcategory"] = parsed["subcategory"]
    if parsed.get("brand"):
        extracted_dict["brand"] = parsed["brand"]

    # Intelligent Ranking Search Engine strictly returns top 2
    results = search_products(
        query=request.query,
        top_k=2,
        category=slots.category,
        brand=parsed.get("brand"),
        budget=slots.budget_max,
        subcategory=parsed.get("subcategory")
    )

    products = []
    for item in results:
        prod_data = item.get("product", item)
        p = Product(**prod_data)
        p.why_recommended = item.get("why_recommended", prod_data.get("why_recommended", []))
        p.score = item.get("score", prod_data.get("score"))
        p.rank = item.get("rank", prod_data.get("rank"))
        p.rank_label = item.get("rank_label", prod_data.get("rank_label"))
        products.append(_enrich_product(p))

    # Log search event
    log_search_event(request.query, len(products))

    if slots.budget_max is not None and slots.budget_max > 0 and len(products) == 0:
        fallback = getattr(results, "fallback", None) or get_budget_fallback(
            category=slots.category,
            subcategory=parsed.get("subcategory"),
            budget=slots.budget_max
        )
        return QueryResponse(
            success=False,
            message=fallback.get("message"),
            suggestion=fallback.get("suggestion"),
            alternatives=fallback.get("alternatives") or [],
            slots=slots,
            products=[],
            extracted=extracted_dict
        )

    return QueryResponse(slots=slots, products=products[:2], extracted=extracted_dict)


# 8. Compare Products (/api/compare)
@router.post("/api/compare", response_model=CompareResponse)
def compare_products_endpoint(
    request: CompareRequest,
    current_user: dict = Depends(get_current_user_dependency)
) -> CompareResponse:
    catalog_df = get_catalog()
    selected_products: List[Product] = []

    for pid in request.product_ids:
        match = catalog_df[catalog_df["product_id"] == pid]
        if not match.empty:
            r = match.iloc[0]
            p = Product(
                id=str(r["product_id"]),
                category=str(r["category"]),
                brand=str(r["brand"]),
                title=str(r["title"]),
                price=float(r["price"]),
                rating=float(r["rating"]),
                description=str(r["description"]),
                image_url=str(r.get("image_url", "")),
                source=str(r.get("source", "ShopAI Catalog")),
            )
            selected_products.append(_enrich_product(p))

    if len(selected_products) < 2:
        raise HTTPException(status_code=400, detail="Need at least 2 valid product_ids to compare")

    result = build_comparison(selected_products)
    return CompareResponse(**result)


# 9. Conversational Chat Assistant (/api/chat)
@router.post("/api/chat", response_model=ChatResponse)
def chat_assistant_endpoint(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user_dependency)
) -> ChatResponse:
    user_id = current_user.get("id") or request.user_id or "default_user"
    user_message = request.message.strip()

    # Step 1: LLM Query Understanding (Phase 4)
    parsed = understand_query(user_message, request.category)

    # Step 2: Conversational Memory Context Merging (Phase 5)
    conversation_store.add_message(user_id, "user", user_message)
    effective_params = conversation_store.get_effective_parameters(user_id, parsed, history=request.history)

    category = effective_params.get("category") or parsed.get("category") or request.category
    subcategory = effective_params.get("subcategory") or parsed.get("subcategory")
    brand = effective_params.get("brand") or parsed.get("brand")
    budget = effective_params.get("budget") or parsed.get("budget")
    min_rating = effective_params.get("min_rating") or parsed.get("min_rating")
    intent = effective_params.get("intent", "product_search")

    extracted_dict = {
        "category": category,
        "budget": budget
    }
    if subcategory:
        extracted_dict["subcategory"] = subcategory
    if brand:
        extracted_dict["brand"] = brand

    slots = QuerySlots(
        category=category or "General",
        budget_max=budget,
        raw_query=user_message
    )

    # Step 2.1: Check if in active multi-step guided category flow
    if effective_params.get("flow_in_progress") and effective_params.get("flow_question"):
        flow_msg = effective_params["flow_question"]
        flow_opts = effective_params["flow_options"] or []
        conversation_store.add_message(user_id, "assistant", flow_msg)
        log_search_event(user_message, 0)
        return ChatResponse(
            needs_clarification=True,
            message=flow_msg,
            options=flow_opts,
            answer=flow_msg,
            reply=flow_msg,
            products=[],
            comparison=None,
            slots=slots,
            suggested_queries=flow_opts[:4],
            extracted=extracted_dict
        )

    # Check if query needs clarification for a broad category without product type
    needs_clarification = effective_params.get("needs_clarification", False) or parsed.get("needs_clarification", False)
    if subcategory or (budget is not None and category and category not in ["Electronics", "General"]):
        needs_clarification = False


    if needs_clarification:
        clarification_msg = (
            parsed.get("clarification_message") 
            or effective_params.get("clarification_message") 
            or f"What type of {category.lower() if category else 'products'} are you looking for?"
        )
        clarification_options = (
            parsed.get("clarification_options") 
            or effective_params.get("clarification_options") 
            or []
        )

        conversation_store.add_message(user_id, "assistant", clarification_msg)
        log_search_event(user_message, 0)

        return ChatResponse(
            needs_clarification=True,
            message=clarification_msg,
            options=clarification_options,
            answer=clarification_msg,
            reply=clarification_msg,
            products=[],
            comparison=None,
            slots=slots,
            suggested_queries=clarification_options[:4],
            extracted=extracted_dict
        )

    # Step 3: Handle Comparison or Retrieval
    comparison_data = None
    compare_targets = effective_params.get("compare_targets") or parsed.get("compare_targets") or []

    if intent == "product_comparison" and compare_targets:
        # Search specifically for comparison targets
        comp_prods = []
        for target in compare_targets:
            target_res = search_products(query=target, top_k=2)
            if target_res:
                p_item = target_res[0].get("product", target_res[0])
                comp_prods.append(_enrich_product(Product(**p_item)))

        if len(comp_prods) >= 2:
            comparison_data = build_comparison(comp_prods)
            comp_answer = (
                f"### ⚖️ Side-by-Side Comparison: {' vs '.join([p.title for p in comp_prods])}\n\n"
                f"{comparison_data.get('summary', '')}"
            )
            conversation_store.add_message(user_id, "assistant", comp_answer)
            log_search_event(user_message, len(comp_prods))
            return ChatResponse(
                needs_clarification=False,
                message=comp_answer,
                options=[],
                answer=comp_answer,
                reply=comp_answer,
                products=comp_prods,
                comparison=comparison_data,
                slots=slots,
                suggested_queries=[f"Show deals on {comp_prods[0].brand}", f"Show deals on {comp_prods[1].brand}", "Compare with another model"],
                extracted=extracted_dict
            )

    results = search_products(
        query=effective_params.get("query") or user_message,
        top_k=2,
        category=category,
        brand=brand,
        budget=budget,
        min_rating=min_rating,
        subcategory=subcategory
    )

    products = []
    for item in results:
        prod_data = item.get("product", item)
        p = Product(**prod_data)
        # Extra safety guarantee: never include any product exceeding user budget
        if budget is not None and budget > 0 and p.price > (budget + 0.99):
            continue
        p.why_recommended = item.get("why_recommended", prod_data.get("why_recommended", []))
        p.score = item.get("score", prod_data.get("score"))
        p.rank = item.get("rank", prod_data.get("rank"))
        p.rank_label = item.get("rank_label", prod_data.get("rank_label"))
        products.append(_enrich_product(p))

    # Check if strict budget filter yielded 0 products
    if (budget is not None and budget > 0 and len(products) == 0) or (hasattr(results, "success") and not results.success):
        fallback = getattr(results, "fallback", None) or get_budget_fallback(
            category=category,
            subcategory=subcategory,
            budget=budget
        )
        fallback_msg = fallback.get("message") or f"Sorry, I couldn't find any matching products under ₹{int(budget):,}."
        fallback_suggestion = fallback.get("suggestion") or ""
        fallback_alts = fallback.get("alternatives") or []
        fallback_reply = fallback.get("reply") or fallback_msg

        conversation_store.add_message(user_id, "assistant", fallback_msg)
        log_search_event(user_message, 0)

        return ChatResponse(
            success=False,
            message=fallback_msg,
            suggestion=fallback_suggestion,
            alternatives=fallback_alts,
            answer=fallback_msg,
            reply=fallback_msg,
            needs_clarification=False,
            options=[],
            products=[],
            comparison=None,
            slots=slots,
            suggested_queries=fallback_alts,
            extracted=extracted_dict
        )

    # Step 4: Synthesize Top 2 Ranked Recommendations with Scores and Why Explanations
    top_2_products = products[:2]
    sections = []
    budget_label = f" under ₹{int(budget):,}" if budget else ""
    cat_label = subcategory or category or "products"

    headline = f"Here are the **Top 2 Best Recommendations** for **{cat_label}**{budget_label}:\n"
    sections.append(headline)

    for idx, p in enumerate(top_2_products):
        rank_num = idx + 1
        rank_label = p.rank_label or f"#{rank_num}"
        score_val = p.score or 90
        why_bullets = "\n".join([f"{r}" for r in (p.why_recommended or [])[:4]])
        
        sections.append(
            f"**{rank_label} {p.brand} {p.title}**\n"
            f"**Score: {score_val}/100** · ₹{p.price:,.0f} (★ {p.rating:.1f})\n\n"
            f"Why:\n"
            f"{why_bullets}\n"
        )

    expert_answer = "\n".join(sections)
    conversation_store.add_message(user_id, "assistant", expert_answer)
    log_search_event(user_message, len(top_2_products))

    suggested = [
        f"Compare these top 2 {cat_label}",
        f"Show details of {top_2_products[0].brand} {top_2_products[0].title[:20]}",
        f"Filter {cat_label} with ★ 4.5+ rating",
    ]

    return ChatResponse(
        needs_clarification=False,
        message=expert_answer,
        options=[],
        answer=expert_answer,
        reply=expert_answer,
        products=top_2_products,
        comparison=None,
        slots=slots,
        suggested_queries=suggested,
        extracted=extracted_dict
    )


# 10. Semantic Vector Search (/api/search)
@router.get("/api/search")
def search_catalog_endpoint(
    q: str = Query(..., description="Search query string"),
    top_k: int = Query(10, description="Max products to return"),
    category: Optional[str] = Query(None, description="Category filter"),
    brand: Optional[str] = Query(None, description="Brand filter"),
    budget: Optional[float] = Query(None, description="Max budget ceiling"),
    rating: Optional[float] = Query(None, description="Min rating threshold")
):
    clean_q = q.strip()
    if not clean_q:
        return {"products": []}

    # Automatically extract category and budget if not explicitly provided as query params
    parsed = understand_query(clean_q)
    resolved_category = category or parsed.get("category")
    resolved_budget = budget if budget is not None else parsed.get("budget")
    resolved_brand = brand or parsed.get("brand")
    resolved_subcategory = parsed.get("subcategory")

    results = search_products(
        query=clean_q,
        top_k=top_k,
        category=resolved_category,
        brand=resolved_brand,
        budget=resolved_budget,
        min_rating=rating,
        subcategory=resolved_subcategory
    )
    log_search_event(clean_q, len(results))

    if hasattr(results, "success") and not results.success:
        return {
            "success": False,
            "message": results.message,
            "suggestion": results.suggestion,
            "alternatives": results.alternatives,
            "products": []
        }

    return {"success": True, "products": results}


# 11. Analytics (/api/analytics)
@router.get("/api/analytics")
def get_analytics():
    return get_analytics_summary()


# 12. Log Product Click (/api/analytics/click)
@router.post("/api/analytics/click")
def log_product_click(
    query: str = Body("", embed=True),
    product_id: str = Body(..., embed=True)
):
    log_search_event(query, results_count=1, clicked_product=product_id)
    return {"status": "success", "logged_product": product_id}
