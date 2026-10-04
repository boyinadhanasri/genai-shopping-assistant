"""
Email Check Module for ShopAI Real-World E-Commerce Authentication
Implements Step 1 & 2 email-first verification (Amazon/Flipkart style).
"""

from typing import Dict, Any
from pydantic import BaseModel
from fastapi import APIRouter
from backend.database.db import get_user_by_email

router = APIRouter()


class CheckEmailDto(BaseModel):
    email: str


def check_email_exists(email: str) -> Dict[str, Any]:
    """
    Checks whether an email is already registered.
    """
    clean_email = (email or "").strip().lower()
    if not clean_email:
        return {"exists": False, "message": "Email cannot be empty."}

    user = get_user_by_email(clean_email)
    exists = user is not None

    return {
        "exists": exists,
        "email": clean_email,
        "is_verified": bool(user.get("is_verified", 0)) if user else False
    }


@router.post("/check-email")
def check_email_endpoint(data: CheckEmailDto):
    return check_email_exists(data.email)
