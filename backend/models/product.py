"""
Generic product schema — the ONE shape every category maps into.

Whatever source feeds the catalog later (a permitted product API, a
refreshed dataset snapshot, or a manually-curated CSV), the ingestion
script for that source is responsible for producing records in this
shape. Nothing downstream (retrieval, ranking, comparison) needs to
know or care which category or source a record came from.
"""

from pydantic import BaseModel
from typing import Dict, Optional, Any, List


def category_slug(category: str) -> str:
    """
    One normalization rule, used everywhere a category name becomes a
    filename (data/<slug>_catalog.json) or an index name. Keeping this
    in one place is what stops preprocessing.py and catalog.py from
    silently drifting apart on how "Home & Kitchen" gets slugged.
    """
    return category.strip().lower().replace(" & ", "_and_").replace(" ", "_")


class Product(BaseModel):
    id: str
    category: str            # e.g. "Electronics" | "Mobiles" | "Appliances" | "Home & Kitchen" | ...
    brand: str
    title: str
    price: float
    rating: Optional[float] = None
    description: Optional[str] = ""
    why_recommended: Optional[list[str]] = []
    specs: Dict[str, str | int | float] = {}   # flexible per-category attributes
    availability: str = "In stock"
    badge: Optional[str] = None                # e.g. "#1 Top Recommendation", "#2 Runner Up"
    rank: Optional[int] = None                 # 1 or 2
    rank_label: Optional[str] = None           # e.g. "#1 Top Recommendation"
    score: Optional[int] = None                # Weighted score out of 100
    review_count: Optional[int] = None
    discount_percent: Optional[int] = None     # e.g. 15, 20
    image_url: Optional[str] = ""
    product_url: Optional[str] = ""
    source: str = "Real Dataset"
    last_updated: Optional[str] = None


class QuerySlots(BaseModel):
    category: str
    budget_max: Optional[float] = None
    raw_query: str


class QueryRequest(BaseModel):
    query: str
    category: Optional[str] = None


class QueryResponse(BaseModel):
    success: bool = True
    message: Optional[str] = None
    suggestion: Optional[str] = None
    alternatives: list[str] = []
    slots: QuerySlots
    products: list[Product]
    extracted: Optional[Dict[str, Any]] = None


class CompareRequest(BaseModel):
    product_ids: list[str]
    category: Optional[str] = None


class CompareResponse(BaseModel):
    attributes: list[str]
    rows: list[dict]
    summary: Optional[str] = ""
    ai_takeaway: Optional[str] = ""


class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str
    confirm_password: str


class LoginRequest(BaseModel):
    email: Optional[str] = "shopper@shopai.com"
    password: Optional[str] = None
    name: Optional[str] = None


class UserProfile(BaseModel):
    id: str
    name: str
    email: str
    avatar: str


class AuthResponse(BaseModel):
    success: bool = True
    message: str = ""
    token: Optional[str] = None
    user: Optional[UserProfile] = None


class LoginResponse(BaseModel):
    success: bool = True
    message: Optional[str] = "Login successful"
    token: Optional[str] = None
    user: Optional[UserProfile] = None


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    category: Optional[str] = None
    history: Optional[list[ChatMessage]] = []
    user_id: Optional[str] = "default_user"


class ChatResponse(BaseModel):
    success: bool = True
    answer: str = ""
    reply: str = ""
    message: Optional[str] = None
    suggestion: Optional[str] = None
    alternatives: list[str] = []
    needs_clarification: bool = False
    options: list[str] = []
    products: list[Product] = []
    comparison: Optional[dict] = None
    slots: Optional[QuerySlots] = None
    suggested_queries: list[str] = []
    extracted: Optional[Dict[str, Any]] = None


