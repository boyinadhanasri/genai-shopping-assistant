"""
OTP Generation, Email Dispatch, and Verification Service for ShopAI
Implements 6-digit numeric OTPs with 10-minute expirations.
Supports real SMTP (Gmail, Outlook, SendGrid, etc.) and development console logging.
"""

import os
import smtplib
import secrets
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from fastapi import APIRouter

from backend.database.db import (
    get_user_by_email,
    set_verification_otp,
    verify_user_otp,
    set_reset_otp,
    verify_reset_otp_only
)

logger = logging.getLogger("ShopAI.OTPService")
router = APIRouter()

# In-memory storage of dispatched OTP emails (for debugging, live testing, simulator)
SENT_OTP_EMAILS: List[Dict[str, Any]] = []

# Optional SMTP Settings from Environment
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL", SMTP_USER or "noreply@shopai.com")
SMTP_FROM_NAME = os.getenv("SMTP_FROM_NAME", "ShopAI Assistant")


def generate_6digit_otp() -> str:
    """Generates a random 6-digit numeric OTP string (e.g. '483921')."""
    return str(secrets.randbelow(900000) + 100000)


def get_otp_expiry_timestamp(minutes: int = 10) -> str:
    """Returns an ISO 8601 UTC timestamp 10 minutes in the future."""
    return (datetime.now(timezone.utc) + timedelta(minutes=minutes)).isoformat()


def _dispatch_smtp_email(to_email: str, subject: str, text_content: str, html_content: str) -> bool:
    """Attempts to send real email via SMTP if credentials are provided."""
    if not SMTP_USER or not SMTP_PASSWORD:
        return False

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{SMTP_FROM_NAME} <{SMTP_FROM_EMAIL}>"
        msg["To"] = to_email

        part1 = MIMEText(text_content, "plain")
        part2 = MIMEText(html_content, "html")
        msg.attach(part1)
        msg.attach(part2)

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_FROM_EMAIL, [to_email], msg.as_string())

        logger.info(f"✓ [SMTP] Email sent successfully to {to_email}")
        return True
    except Exception as e:
        logger.warning(f"⚠️ [SMTP] Failed to send email to {to_email}: {e}")
        return False


def send_verification_otp_email(email: str, name: str, otp: str) -> Dict[str, Any]:
    """
    Sends 6-digit verification code email.
    Subject: 'Verify your ShopAI account'
    """
    clean_email = email.strip().lower()
    subject = "Verify your ShopAI account"
    text_content = f"Hi {name},\n\nYour ShopAI verification code is:\n\n{otp}\n\nThis code expires in 10 minutes."
    html_content = f"""
        <div style="font-family: sans-serif; max-width: 480px; margin: auto; padding: 24px; border: 1px solid #e2e8f0; border-radius: 16px; background-color: #ffffff;">
            <h2 style="color: #4f46e5; margin-bottom: 8px;">Verify your ShopAI account</h2>
            <p style="color: #475569; font-size: 14px;">Hi {name},</p>
            <p style="color: #475569; font-size: 14px;">Use the 6-digit verification code below to complete your registration:</p>
            <div style="background-color: #f8fafc; border: 2px dashed #cbd5e1; border-radius: 12px; text-align: center; padding: 18px; margin: 20px 0;">
                <span style="font-size: 32px; font-weight: 800; letter-spacing: 6px; color: #1e1b4b; font-family: monospace;">{otp}</span>
            </div>
            <p style="color: #64748b; font-size: 12px;">This code will expire in <strong>10 minutes</strong>. If you did not create an account with ShopAI, please ignore this email.</p>
        </div>
    """

    record = {
        "to": clean_email,
        "name": name,
        "subject": subject,
        "otp": otp,
        "type": "REGISTRATION_OTP",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "text_content": text_content,
        "html_content": html_content
    }
    SENT_OTP_EMAILS.append(record)

    # Attempt real SMTP delivery if configured
    smtp_sent = _dispatch_smtp_email(clean_email, subject, text_content, html_content)
    
    # Always log clearly to console for immediate visibility during development
    print(f"\n=======================================================")
    print(f"📩 [SHOPAI OTP EMAIL] To: {clean_email}")
    print(f"🔑 VERIFICATION OTP CODE: {otp}")
    print(f"⏱️  Valid for 10 minutes | Status: {'Dispatched via SMTP' if smtp_sent else 'Logged to Console (Dev Mode)'}")
    print(f"=======================================================\n")
    logger.info(f"[OTP SERVICE] Verification OTP for {clean_email}: {otp}")

    return record


def send_reset_otp_email(email: str, name: str, otp: str) -> Dict[str, Any]:
    """
    Sends 6-digit password reset OTP email.
    Subject: 'Reset your ShopAI password'
    """
    clean_email = email.strip().lower()
    subject = "Reset your ShopAI password"
    text_content = f"Hi {name},\n\nYour ShopAI password reset code is:\n\n{otp}\n\nThis code expires in 10 minutes."
    html_content = f"""
        <div style="font-family: sans-serif; max-width: 480px; margin: auto; padding: 24px; border: 1px solid #e2e8f0; border-radius: 16px; background-color: #ffffff;">
            <h2 style="color: #4f46e5; margin-bottom: 8px;">Reset your ShopAI password</h2>
            <p style="color: #475569; font-size: 14px;">Hi {name},</p>
            <p style="color: #475569; font-size: 14px;">Use the 6-digit OTP code below to reset your ShopAI account password:</p>
            <div style="background-color: #f8fafc; border: 2px dashed #cbd5e1; border-radius: 12px; text-align: center; padding: 18px; margin: 20px 0;">
                <span style="font-size: 32px; font-weight: 800; letter-spacing: 6px; color: #1e1b4b; font-family: monospace;">{otp}</span>
            </div>
            <p style="color: #64748b; font-size: 12px;">This code is valid for <strong>10 minutes</strong>. If you did not request a password reset, please secure your account immediately.</p>
        </div>
    """

    record = {
        "to": clean_email,
        "name": name,
        "subject": subject,
        "otp": otp,
        "type": "PASSWORD_RESET_OTP",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "text_content": text_content,
        "html_content": html_content
    }
    SENT_OTP_EMAILS.append(record)

    smtp_sent = _dispatch_smtp_email(clean_email, subject, text_content, html_content)
    
    print(f"\n=======================================================")
    print(f"📩 [SHOPAI PASSWORD RESET EMAIL] To: {clean_email}")
    print(f"🔑 PASSWORD RESET OTP CODE: {otp}")
    print(f"⏱️  Valid for 10 minutes | Status: {'Dispatched via SMTP' if smtp_sent else 'Logged to Console (Dev Mode)'}")
    print(f"=======================================================\n")
    logger.info(f"[OTP SERVICE] Password Reset OTP for {clean_email}: {otp}")

    return record


def get_latest_otp_for(email: str) -> Optional[str]:
    """Helper for testing: fetches the most recent OTP sent to an email."""
    clean = email.strip().lower()
    for rec in reversed(SENT_OTP_EMAILS):
        if rec["to"].strip().lower() == clean:
            return rec.get("otp")
    return None


# DTO Models
class VerifyOtpDto(BaseModel):
    email: str
    otp: str


class ResendOtpDto(BaseModel):
    email: str


@router.post("/verify-otp")
def verify_otp_endpoint(data: VerifyOtpDto):
    """Verifies registration OTP."""
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
            "message": "Verification code expired. Request a new code."
        }
    else:
        return {
            "success": False,
            "message": "Invalid verification code."
        }


@router.post("/resend-otp")
def resend_otp_endpoint(data: ResendOtpDto):
    """Generates and resends a new 6-digit registration OTP."""
    clean_email = data.email.strip().lower()
    user = get_user_by_email(clean_email)
    if not user:
        return {"success": False, "message": "Account not found."}

    if user.get("is_verified", 0):
        return {"success": True, "message": "Account is already verified. Please sign in."}

    new_otp = generate_6digit_otp()
    expiry = get_otp_expiry_timestamp(10)
    set_verification_otp(clean_email, new_otp, expiry)
    send_verification_otp_email(clean_email, user["name"], new_otp)

    return {
        "success": True,
        "message": "A new verification code has been sent to your email.",
        "otp": new_otp  # Included for simulator and fast testing
    }
