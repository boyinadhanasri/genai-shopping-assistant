"""
Password Utilities for ShopAI Authentication
Enforces strict production password complexity rules and secure hashing.
"""

import re
import hashlib
import secrets
import hmac
from typing import Tuple, List

try:
    import bcrypt
    HAS_BCRYPT = True
except ImportError:
    HAS_BCRYPT = False

# Minimum length
MIN_PASSWORD_LENGTH = 8

# Special characters allowed
SPECIAL_CHARS_PATTERN = r'[!@#$%^&*(),.?":{}|<>_\-+=\[\]\\/`~;\'"]'


def validate_password_strength(password: str) -> Tuple[bool, List[str]]:
    """
    Validates that the password meets production complexity standards:
    - Minimum 8 characters
    - At least one uppercase letter (A-Z)
    - At least one lowercase letter (a-z)
    - At least one number (0-9)
    - At least one special character (!@#$%^&*...)
    """
    errors: List[str] = []

    if not password:
        return False, ["Password cannot be empty."]

    if len(password) < MIN_PASSWORD_LENGTH:
        errors.append(f"Password must be at least {MIN_PASSWORD_LENGTH} characters long.")

    if not re.search(r'[A-Z]', password):
        errors.append("Password must contain at least one uppercase letter (A-Z).")

    if not re.search(r'[a-z]', password):
        errors.append("Password must contain at least one lowercase letter (a-z).")

    if not re.search(r'[0-9]', password):
        errors.append("Password must contain at least one number (0-9).")

    if not re.search(SPECIAL_CHARS_PATTERN, password):
        errors.append("Password must contain at least one special character (!@#$%^&*...).")

    return (len(errors) == 0, errors)


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

    salt = secrets.token_hex(16)
    iterations = 100_000
    key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), iterations)
    return f"pbkdf2_sha256${iterations}${salt}${key.hex()}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain text password against a stored hash."""
    if not plain_password or not hashed_password:
        return False

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

    if HAS_BCRYPT:
        try:
            return bcrypt.checkpw(
                plain_password.encode("utf-8"),
                hashed_password.encode("utf-8")
            )
        except Exception:
            return False

    return False
