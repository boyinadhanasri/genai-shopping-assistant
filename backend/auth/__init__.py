"""
Authentication package for ShopAI
"""
from backend.auth.auth_routes import auth_router
from backend.auth.check_email import check_email_exists
from backend.auth.register import register_user
from backend.auth.login import authenticate_user
from backend.auth.otp_service import (
    generate_6digit_otp, 
    send_verification_otp_email, 
    send_reset_otp_email
)
from backend.auth.jwt_handler import create_access_token, verify_access_token
from backend.auth.password_utils import hash_password, verify_password, validate_password_strength

__all__ = [
    "auth_router",
    "check_email_exists",
    "register_user",
    "authenticate_user",
    "generate_6digit_otp",
    "send_verification_otp_email",
    "send_reset_otp_email",
    "create_access_token",
    "verify_access_token",
    "hash_password",
    "verify_password",
    "validate_password_strength",
]
