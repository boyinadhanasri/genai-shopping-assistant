"""
Unified Router for ShopAI Authentication System
Combines check_email, register, verify_otp, login, forgot_password, and reset_password.
"""

from typing import Optional
from pydantic import BaseModel
from fastapi import APIRouter, Header, HTTPException, Depends

from backend.auth.check_email import router as check_email_router
from backend.auth.register import router as register_router
from backend.auth.verify_otp import router as verify_otp_router
from backend.auth.login import router as login_router
from backend.auth.forgot_password import router as forgot_password_router
from backend.auth.reset_password import router as reset_password_router
from backend.auth.security import get_current_user_dependency
from backend.database.db import update_user_name, update_user_password_by_id
from backend.auth.password_utils import verify_password, validate_password_strength, hash_password

auth_router = APIRouter(prefix="/api/auth", tags=["Authentication"])

# Mount all modular sub-routers
auth_router.include_router(check_email_router)
auth_router.include_router(register_router)
auth_router.include_router(verify_otp_router)
auth_router.include_router(login_router)
auth_router.include_router(forgot_password_router)
auth_router.include_router(reset_password_router)


# Protected Profile DTOs and Endpoints
class UpdateProfileDto(BaseModel):
    name: str


class ChangePasswordDto(BaseModel):
    current_password: str
    new_password: str
    confirm_password: str


@auth_router.get("/me")
def get_current_user_profile(user: dict = Depends(get_current_user_dependency)):
    return {
        "success": True,
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "is_verified": bool(user.get("is_verified", 0)),
            "created_at": user.get("created_at"),
            "avatar": f"https://api.dicebear.com/7.x/avataaars/svg?seed={user['name']}",
        }
    }


@auth_router.put("/profile")
def update_profile_name(data: UpdateProfileDto, user: dict = Depends(get_current_user_dependency)):
    clean_name = data.name.strip()
    if not clean_name:
        return {"success": False, "message": "Name cannot be empty."}
    update_user_name(user["id"], clean_name)
    return {"success": True, "message": "Profile updated successfully.", "name": clean_name}


@auth_router.put("/change-password")
def change_password(data: ChangePasswordDto, user: dict = Depends(get_current_user_dependency)):
    if not verify_password(data.current_password, user["password_hash"]):
        return {"success": False, "message": "Current password is incorrect."}

    if data.new_password != data.confirm_password:
        return {"success": False, "message": "New passwords do not match."}

    is_valid, errors = validate_password_strength(data.new_password)
    if not is_valid:
        return {"success": False, "message": " ".join(errors)}

    if verify_password(data.new_password, user["password_hash"]):
        return {"success": False, "message": "Cannot reuse previous password."}

    new_hash = hash_password(data.new_password)
    update_user_password_by_id(user["id"], new_hash)
    return {"success": True, "message": "Password changed successfully."}
