"""
OTP Verification & Resend Handler for ShopAI E-Commerce Authentication
"""

from typing import Dict, Any
from pydantic import BaseModel
from fastapi import APIRouter

from backend.database.db import get_user_by_email, set_verification_otp, verify_user_otp
from backend.auth.otp_service import (
    generate_6digit_otp, 
    get_otp_expiry_timestamp, 
    send_verification_otp_email
)
from backend.auth.security import check_otp_rate_limit

router = APIRouter()


class VerifyOtpDto(BaseModel):
    email: str
    otp: str


class ResendOtpDto(BaseModel):
    email: str


@router.post("/verify-otp")
def verify_otp_endpoint(data: VerifyOtpDto):
    """
    Validates the 6-digit registration OTP.
    """
    clean_email = data.email.strip().lower()
    result = verify_user_otp(clean_email, data.otp)
    
    if result["status"] == "success":
        return {
            "success": True,
            "message": "Email verified successfully.",
            "email": clean_email
        }
    elif result["status"] == "expired":
        return {
            "success": False,
            "message": "OTP expired. Request a new OTP."
        }
    else:
        return {
            "success": False,
            "message": "Invalid OTP."
        }


@router.post("/resend-otp")
def resend_otp_endpoint(data: ResendOtpDto):
    """
    Resends a new 6-digit registration OTP with rate limiting (max 3 per 10 mins).
    """
    clean_email = data.email.strip().lower()
    user = get_user_by_email(clean_email)
    if not user:
        return {"success": False, "message": "Account not found."}

    if user.get("is_verified", 0):
        return {"success": True, "message": "Account is already verified. Please sign in."}

    # Rate limiting check
    allowed, rate_msg = check_otp_rate_limit(clean_email)
    if not allowed:
        return {"success": False, "message": rate_msg}

    new_otp = generate_6digit_otp()
    expiry = get_otp_expiry_timestamp(10)
    set_verification_otp(clean_email, new_otp, expiry)
    send_verification_otp_email(clean_email, user["name"], new_otp)

    return {
        "success": True,
        "message": "A new verification code has been sent to your email.",
        "otp": new_otp
    }
