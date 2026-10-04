"""
User Login & Token Refresh Handler for ShopAI Authentication
Enforces account lockout (5 failed attempts -> 15 min lock), unverified account guards, and issues Access & Refresh JWTs.
"""

import uuid
from typing import Dict, Any, Optional
from pydantic import BaseModel
from fastapi import APIRouter

from backend.database.db import (
    get_user_by_email, 
    record_failed_login, 
    reset_failed_login_attempts
)
from backend.auth.password_utils import verify_password
from backend.auth.jwt_handler import (
    create_access_token, 
    create_refresh_token, 
    verify_refresh_token
)
from backend.auth.security import is_account_locked

router = APIRouter()


class LoginDto(BaseModel):
    email: Optional[str] = None
    password: Optional[str] = None
    remember_me: Optional[bool] = False


class RefreshTokenDto(BaseModel):
    refresh_token: str


def authenticate_user(
    email: Optional[str], 
    password: Optional[str], 
    remember_me: bool = False
) -> Dict[str, Any]:
    """
    Authenticates credentials with lockout protection and issues JWT access/refresh tokens.
    """
    clean_email = (email or "").strip().lower()
    if not clean_email or not password:
        return {"success": False, "message": "Invalid email or password."}

    # 1. Check Account Lockout
    locked, locked_until = is_account_locked(clean_email)
    if locked:
        return {
            "success": False,
            "message": "Account temporarily locked due to 5 failed login attempts. Please try again in 15 minutes or reset your password.",
            "account_locked": True
        }

    user = get_user_by_email(clean_email)
    
    # 2. Verify Credentials
    if not user or not verify_password(password, user["password_hash"]):
        # Increment failed login attempts
        lock_info = record_failed_login(clean_email, lock_duration_minutes=15)
        if lock_info.get("locked"):
            return {
                "success": False,
                "message": "Account locked for 15 minutes due to 5 consecutive failed login attempts.",
                "account_locked": True
            }
        return {"success": False, "message": "Invalid email or password."}

    # 3. Check Verification Status
    if not user.get("is_verified", 0):
        return {
            "success": False,
            "message": "Please verify your email before logging in.",
            "requires_verification": True,
            "email": user["email"]
        }

    # 4. Successful Login -> Reset failed attempt counter
    reset_failed_login_attempts(clean_email)

    # 5. Issue Access & Refresh Tokens
    access_token = create_access_token(
        user_id=user["id"],
        email=user["email"],
        name=user["name"],
        remember_me=remember_me
    )
    refresh_token = create_refresh_token(user_id=user["id"], email=user["email"])

    return {
        "success": True,
        "message": "Login successful",
        "token": access_token,
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "is_verified": True,
            "created_at": user.get("created_at"),
            "avatar": f"https://api.dicebear.com/7.x/avataaars/svg?seed={user['name']}",
        }
    }


@router.post("/login")
def login_endpoint(data: LoginDto):
    return authenticate_user(
        email=data.email,
        password=data.password,
        remember_me=bool(data.remember_me)
    )


@router.post("/refresh")
def refresh_token_endpoint(data: RefreshTokenDto):
    """
    Exchanges a valid Refresh Token for a fresh Access Token.
    """
    payload = verify_refresh_token(data.refresh_token)
    if not payload or not payload.get("user_id"):
        return {"success": False, "message": "Invalid or expired refresh token."}

    user = get_user_by_email(payload.get("email", ""))
    if not user:
        return {"success": False, "message": "User account no longer exists."}

    new_access_token = create_access_token(
        user_id=user["id"],
        email=user["email"],
        name=user["name"],
        remember_me=False
    )

    return {
        "success": True,
        "access_token": new_access_token,
        "token": new_access_token
    }
