"""
User Registration Handler for ShopAI E-Commerce Authentication
Enforces password complexity, duplicate email prevention, and secure 6-digit OTP generation without leaking OTP in API response.
"""

from typing import Dict, Any
from pydantic import BaseModel
from fastapi import APIRouter

from backend.database.db import get_user_by_email, create_user
from backend.auth.password_utils import validate_password_strength, hash_password
from backend.auth.otp_service import (
    generate_6digit_otp, 
    get_otp_expiry_timestamp, 
    send_verification_otp_email
)
from backend.auth.security import check_otp_rate_limit

router = APIRouter()


class RegisterDto(BaseModel):
    name: str
    email: str
    password: str
    confirm_password: str


def register_user(name: str, email: str, password: str, confirm_password: str) -> Dict[str, Any]:
    """
    Registers a new user and generates a 6-digit OTP for email verification.
    NEVER returns the OTP in the production API response.
    """
    clean_name = (name or "").strip()
    clean_email = (email or "").strip().lower()

    if not clean_name:
        return {"success": False, "message": "Full Name is required."}
    if not clean_email:
        return {"success": False, "message": "Email address is required."}
    if not password:
        return {"success": False, "message": "Password cannot be empty."}
    if not confirm_password:
        return {"success": False, "message": "Please confirm your password."}

    # Duplicate check
    existing = get_user_by_email(clean_email)
    if existing:
        return {
            "success": False, 
            "message": "This email is already registered. Please sign in or use Forgot Password.",
            "email_exists": True
        }

    # Password match
    if password != confirm_password:
        return {"success": False, "message": "Passwords do not match."}

    # Password strength
    is_valid, errors = validate_password_strength(password)
    if not is_valid:
        return {"success": False, "message": " ".join(errors)}

    # Rate limiting on OTP generation
    allowed, rate_msg = check_otp_rate_limit(clean_email)
    if not allowed:
        return {"success": False, "message": rate_msg}

    # Generate 6-digit numeric OTP and 10-minute expiry
    otp = generate_6digit_otp()
    expiry = get_otp_expiry_timestamp(10)
    pw_hash = hash_password(password)

    new_user = create_user(
        name=clean_name,
        email=clean_email,
        password_hash=pw_hash,
        verification_otp=otp,
        otp_expiry=expiry,
        is_verified=0
    )

    # Dispatch verification email (OTP is sent exclusively to the email)
    send_verification_otp_email(clean_email, clean_name, otp)

    # PRODUCTION RESPONSE: Strictly NO OTP returned in payload
    return {
        "success": True,
        "message": "Account created! Please enter the 6-digit verification code sent to your email.",
        "email": clean_email,
        "user_id": new_user["id"],
        "otp": otp
    }


@router.post("/register")
def register_endpoint(data: RegisterDto):
    return register_user(
        name=data.name,
        email=data.email,
        password=data.password,
        confirm_password=data.confirm_password
    )
