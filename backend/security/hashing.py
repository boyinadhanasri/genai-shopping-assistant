"""
Password Hashing and Security Utility for ShopAI
Supports bcrypt with automatic standard-library PBKDF2-HMAC-SHA256 fallback.
"""

import hashlib
import secrets
import hmac

try:
    import bcrypt
    HAS_BCRYPT = True
except ImportError:
    HAS_BCRYPT = False


def hash_password(password: str) -> str:
    """Hashes a plain text password using bcrypt (if available) or PBKDF2-SHA256."""
    if not password:
        raise ValueError("Password cannot be empty")
    
    if HAS_BCRYPT:
        try:
            salt = bcrypt.gensalt(rounds=12)
            hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
            return hashed.decode("utf-8")
        except Exception:
            pass

    # Standard library fallback (PBKDF2-HMAC-SHA256)
    salt = secrets.token_hex(16)
    iterations = 100_000
    key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), iterations)
    return f"pbkdf2_sha256${iterations}${salt}${key.hex()}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain text password against stored hash."""
    if not plain_password or not hashed_password:
        return False

    # Check for PBKDF2 format
    if hashed_password.startswith("pbkdf2_sha256$"):
        try:
            parts = hashed_password.split("$")
            if len(parts) != 4:
                return False
            iterations = int(parts[1])
            salt = parts[2]
            stored_key = parts[3]
            calculated_key = hashlib.pbkdf2_hmac(
                "sha256", plain_password.encode("utf-8"), salt.encode("utf-8"), iterations
            ).hex()
            return hmac.compare_digest(stored_key, calculated_key)
        except Exception:
            return False

    # Check for bcrypt
    if HAS_BCRYPT:
        try:
            return bcrypt.checkpw(
                plain_password.encode("utf-8"),
                hashed_password.encode("utf-8")
            )
        except Exception:
            return False

    return False
