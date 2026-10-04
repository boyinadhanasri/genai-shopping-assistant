"""
JWT Access Token & Refresh Token Handler for ShopAI
Implements RFC 7519 HS256 JWT generation and validation with zero external dependencies
(supports PyJWT if installed with automatic standard-library fallback).
"""

import os
import json
import hmac
import base64
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any

try:
    import jwt as pyjwt
    HAS_PYJWT = True
except ImportError:
    HAS_PYJWT = False

JWT_SECRET_KEY = os.getenv("SHOPAI_JWT_SECRET", "shopai_super_secret_jwt_key_prod_2026_x99a")
JWT_REFRESH_SECRET_KEY = os.getenv("SHOPAI_JWT_REFRESH_SECRET", "shopai_refresh_secret_prod_key_2026_y88b")
JWT_ALGORITHM = "HS256"

# Expiration periods
DEFAULT_ACCESS_HOURS = 24
REMEMBER_ME_DAYS = 30
REFRESH_TOKEN_DAYS = 60


def _b64url_encode(data: bytes) -> str:
    """Encodes bytes to base64url string without padding."""
    return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")


def _b64url_decode(s: str) -> bytes:
    """Decodes base64url string with proper padding restoration."""
    padding = "=" * ((4 - len(s) % 4) % 4)
    return base64.urlsafe_b64decode(s + padding)


def _encode_jwt_pure(payload: dict, secret: str) -> str:
    """Pure Python RFC 7519 compliant HS256 JWT encoding."""
    header = {"alg": "HS256", "typ": "JWT"}
    header_json = json.dumps(header, separators=(",", ":"), sort_keys=True).encode("utf-8")
    payload_json = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")

    header_b64 = _b64url_encode(header_json)
    payload_b64 = _b64url_encode(payload_json)

    signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")
    signature = hmac.new(secret.encode("utf-8"), signing_input, hashlib.sha256).digest()
    sig_b64 = _b64url_encode(signature)

    return f"{header_b64}.{payload_b64}.{sig_b64}"


def _decode_jwt_pure(token: str, secret: str) -> Optional[Dict[str, Any]]:
    """Pure Python RFC 7519 compliant HS256 JWT decoding and validation."""
    if not token or not isinstance(token, str):
        return None

    parts = token.strip().split(".")
    if len(parts) != 3:
        return None

    header_b64, payload_b64, sig_b64 = parts

    try:
        # 1. Verify Signature
        signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")
        expected_sig = hmac.new(secret.encode("utf-8"), signing_input, hashlib.sha256).digest()
        actual_sig = _b64url_decode(sig_b64)

        if not hmac.compare_digest(expected_sig, actual_sig):
            return None

        # 2. Decode Payload
        payload_bytes = _b64url_decode(payload_b64)
        payload = json.loads(payload_bytes.decode("utf-8"))

        # 3. Check Expiry
        exp = payload.get("exp") or payload.get("expiry")
        if exp is not None:
            now_ts = int(datetime.now(timezone.utc).timestamp())
            if now_ts > int(exp):
                return None  # Token expired

        return payload
    except Exception:
        return None


def create_access_token(
    user_id: str, 
    email: str, 
    name: str = "", 
    remember_me: bool = False,
    extra_data: Optional[Dict[str, Any]] = None
) -> str:
    """
    Creates signed Access Token containing:
    user_id, email, name, issued_at (iat), expiry (exp), remember_me.
    """
    now = datetime.now(timezone.utc)
    if remember_me:
        expire = now + timedelta(days=REMEMBER_ME_DAYS)
    else:
        expire = now + timedelta(hours=DEFAULT_ACCESS_HOURS)

    payload = {
        "user_id": user_id,
        "sub": user_id,
        "email": email.strip().lower(),
        "name": name,
        "issued_at": int(now.timestamp()),
        "iat": int(now.timestamp()),
        "expiry": int(expire.timestamp()),
        "exp": int(expire.timestamp()),
        "remember_me": remember_me,
        "type": "access",
    }

    if extra_data:
        payload.update(extra_data)

    if HAS_PYJWT:
        try:
            return pyjwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
        except Exception:
            pass

    return _encode_jwt_pure(payload, JWT_SECRET_KEY)


def create_refresh_token(user_id: str, email: str) -> str:
    """
    Creates long-lived Refresh Token (60 days).
    """
    now = datetime.now(timezone.utc)
    expire = now + timedelta(days=REFRESH_TOKEN_DAYS)
    payload = {
        "user_id": user_id,
        "sub": user_id,
        "email": email.strip().lower(),
        "issued_at": int(now.timestamp()),
        "iat": int(now.timestamp()),
        "expiry": int(expire.timestamp()),
        "exp": int(expire.timestamp()),
        "type": "refresh",
    }

    if HAS_PYJWT:
        try:
            return pyjwt.encode(payload, JWT_REFRESH_SECRET_KEY, algorithm=JWT_ALGORITHM)
        except Exception:
            pass

    return _encode_jwt_pure(payload, JWT_REFRESH_SECRET_KEY)


def verify_access_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Validates Access Token and returns payload.
    """
    if not token:
        return None
    if token.startswith("Bearer "):
        token = token[7:].strip()

    if HAS_PYJWT:
        try:
            return pyjwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        except (pyjwt.ExpiredSignatureError, pyjwt.PyJWTError):
            return None
        except Exception:
            pass

    return _decode_jwt_pure(token, JWT_SECRET_KEY)


def verify_refresh_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Validates Refresh Token and returns payload.
    """
    if not token:
        return None
    if token.startswith("Bearer "):
        token = token[7:].strip()

    if HAS_PYJWT:
        try:
            return pyjwt.decode(token, JWT_REFRESH_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        except (pyjwt.ExpiredSignatureError, pyjwt.PyJWTError):
            return None
        except Exception:
            pass

    return _decode_jwt_pure(token, JWT_REFRESH_SECRET_KEY)
