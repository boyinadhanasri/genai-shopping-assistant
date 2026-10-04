"""
Forgot Password Handler for ShopAI E-Commerce Authentication
Enforces rate limits (5/hr), user enumeration prevention, and 6-digit reset OTP dispatch.
"""

from typing import Dict, Any
from pydantic import BaseModel
from fastapi import APIRouter

from backend.database.db import get_user_by_email, set_reset_otp, verify_reset_otp_only
from backend.auth.otp_service import (
    generate_6digit_otp, 
    get_otp_expiry_timestamp, 
    send_reset_otp_email
)
from backend.auth.security import check_forgot_password_rate_limit

router = APIRouter()


class RequestResetOtpDto(BaseModel):
    email: str


class VerifyResetOtpDto(BaseModel):
    email: str
    otp: str


@router.post("/forgot-password")
def request_reset_otp(data: RequestResetOtpDto):
    """
    Sends a 6-digit password reset OTP if the account exists.
    Always returns a generic message to prevent email enumeration.
    """
    clean_email = (data.email or "").strip().lower()
    if not clean_email:
        return {
            "success": True, 
            "message": "If an account exists, a reset code has been sent."
        }

    # Rate limiting (max 5 requests per hour)
    allowed, rate_msg = check_forgot_password_rate_limit(clean_email)
    if not allowed:
        return {"success": False, "message": rate_msg}

    user = get_user_by_email(clean_email)
    if user:
        otp = generate_6digit_otp()
        expiry = get_otp_expiry_timestamp(10)
        set_reset_otp(clean_email, otp, expiry)
        send_reset_otp_email(clean_email, user["name"], otp)

    # Standard enumeration-safe response
    return {
        "success": True,
        "message": "If an account exists, a reset code has been sent."
    }


@router.post("/verify-reset-otp")
def verify_reset_otp_endpoint(data: VerifyResetOtpDto):
    """
    Validates the 6-digit reset OTP before allowing password creation.
    """
    clean_email = data.email.strip().lower()
    result = verify_reset_otp_only(clean_email, data.otp)
    
    if result["status"] == "success":
        return {
            "success": True,
            "message": "OTP verified successfully. Please enter your new password.",
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
