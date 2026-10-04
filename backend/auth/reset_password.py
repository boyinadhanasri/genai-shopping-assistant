"""
Password Reset Handler with OTP Validation and Password Reuse Prevention
"""

from typing import Dict, Any
from pydantic import BaseModel
from fastapi import APIRouter

from backend.database.db import (
    get_user_by_email,
    verify_reset_otp_only,
    update_password_with_reset_otp
)
from backend.auth.password_utils import (
    validate_password_strength,
    hash_password,
    verify_password
)

router = APIRouter()


class ResetPasswordDto(BaseModel):
    email: str
    otp: str
    new_password: str
    confirm_password: str


@router.post("/reset-password")
def reset_password_endpoint(data: ResetPasswordDto):
    """
    Validates reset OTP, verifies new password strength, and blocks previous password reuse.
    """
    clean_email = data.email.strip().lower()
    user = get_user_by_email(clean_email)
    if not user:
        return {"success": False, "message": "Account not found."}

    # 1. Verify Reset OTP
    otp_check = verify_reset_otp_only(clean_email, data.otp)
    if otp_check["status"] != "success":
        if otp_check["status"] == "expired":
            return {"success": False, "message": "OTP expired. Request a new OTP."}
        return {"success": False, "message": "Invalid OTP."}

    # 2. Confirm Passwords Match
    if data.new_password != data.confirm_password:
        return {"success": False, "message": "Passwords do not match."}

    # 3. Password Strength Rules
    is_valid, errors = validate_password_strength(data.new_password)
    if not is_valid:
        return {"success": False, "message": " ".join(errors)}

    # 4. Password Reuse Prevention
    if verify_password(data.new_password, user["password_hash"]):
        return {
            "success": False,
            "message": "Cannot reuse previous password."
        }

    # 5. Hash & Update
    new_hash = hash_password(data.new_password)
    update_password_with_reset_otp(clean_email, new_hash)

    return {
        "success": True,
        "message": "Password updated successfully. Please log in with your new password."
    }
