"""
Email Service for ShopAI E-Commerce Authentication
Dispatches HTML and text emails for verification OTPs and password reset OTPs.
"""

import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from backend.auth.otp_service import SENT_OTP_EMAILS, send_verification_otp_email, send_reset_otp_email

logger = logging.getLogger("ShopAI.EmailService")


def get_latest_email_for(email: str) -> Dict[str, Any]:
    """Helper for testing to inspect sent emails."""
    clean = email.strip().lower()
    for rec in reversed(SENT_OTP_EMAILS):
        if rec["to"].strip().lower() == clean:
            return rec
    return {}
