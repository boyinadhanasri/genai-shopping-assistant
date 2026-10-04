"""
Security and Rate Limiting Middleware for ShopAI Authentication
Enforces account lockout (5 attempts -> 15 min lock), OTP throttling (3 / 10 min), and Forgot Password limits (5 / hour).
"""

from datetime import datetime, timezone
from typing import Optional, Dict, Any
from fastapi import Header, HTTPException, Request

from backend.database.db import (
    get_user_by_email, 
    get_user_by_id, 
    record_rate_limit_event, 
    count_recent_events
)
from backend.auth.jwt_handler import verify_access_token


def is_account_locked(email: str) -> tuple[bool, Optional[str]]:
    """
    Checks if account is locked due to 5 consecutive failed login attempts.
    Returns (is_locked, locked_until_iso).
    """
    user = get_user_by_email(email)
    if not user:
        return False, None

    locked_until_str = user.get("account_locked_until")
    if locked_until_str:
        try:
            locked_dt = datetime.fromisoformat(locked_until_str)
            if datetime.now(timezone.utc) < locked_dt:
                return True, locked_until_str
        except Exception:
            pass
    return False, None


def check_otp_rate_limit(email: str) -> tuple[bool, str]:
    """
    Enforces maximum 3 OTP requests every 10 minutes per email.
    """
    clean_email = email.strip().lower()
    recent_count = count_recent_events(clean_email, "otp_request", window_minutes=10)
    if recent_count >= 3:
        return False, "Too many OTP requests. Please wait 10 minutes before requesting again."
    record_rate_limit_event(clean_email, "otp_request")
    return True, ""


def check_forgot_password_rate_limit(email: str) -> tuple[bool, str]:
    """
    Enforces maximum 5 forgot password requests per hour.
    """
    clean_email = email.strip().lower()
    recent_count = count_recent_events(clean_email, "forgot_password", window_minutes=60)
    if recent_count >= 5:
        return False, "Too many password reset requests. Please wait 1 hour."
    record_rate_limit_event(clean_email, "forgot_password")
    return True, ""


def get_current_user_dependency(authorization: Optional[str] = Header(None)) -> Dict[str, Any]:
    """
    FastAPI dependency for verifying JWT and returning the authenticated user.
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Authentication token missing.")

    payload = verify_access_token(authorization)
    if not payload or not payload.get("user_id"):
        raise HTTPException(status_code=401, detail="Invalid or expired authentication token.")

    user = get_user_by_id(payload["user_id"])
    if not user:
        raise HTTPException(status_code=401, detail="User account not found or removed.")

    return user
