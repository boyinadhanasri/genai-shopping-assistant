"""
Database layer for ShopAI Real-World Production Authentication System
Schema with security columns: failed login attempts, account lockouts, OTP expiry, timestamps.
"""

import os
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any, List

POSSIBLE_DATA_DIRS = [
    Path(__file__).resolve().parent.parent.parent / "data",
    Path(__file__).resolve().parent.parent / "data",
    Path.cwd() / "data",
    Path("C:/project folders/genai-shopping-assistant/genai-shopping-assistant/data"),
]
DATA_DIR = next((d for d in POSSIBLE_DATA_DIRS if d.exists()), POSSIBLE_DATA_DIRS[0])
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DATA_DIR / "shopai_users.db"


def get_connection() -> sqlite3.Connection:
    """Returns a SQLite connection with row factory configured."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Initializes schema and runs column migrations for existing databases."""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # 1. Users Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL COLLATE NOCASE,
                password_hash TEXT NOT NULL,
                is_verified INTEGER DEFAULT 0,
                verification_otp TEXT,
                otp_expiry TEXT,
                reset_otp TEXT,
                reset_expiry TEXT,
                failed_login_attempts INTEGER DEFAULT 0,
                account_locked_until TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_users_email ON users(email);")

        # 2. Rate Limiting Table (for OTP requests, forgot password requests)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rate_limits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT NOT NULL,
                action TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_rate_limits_key_action ON rate_limits(key, action, timestamp);")

        # Dynamic column migrations for users
        cursor.execute("PRAGMA table_info(users)")
        columns = [row["name"] for row in cursor.fetchall()]
        
        if "failed_login_attempts" not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN failed_login_attempts INTEGER DEFAULT 0")
        if "account_locked_until" not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN account_locked_until TEXT")
        if "updated_at" not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN updated_at TEXT")
            
        conn.commit()


def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """Fetches user record by email (case-insensitive)."""
    if not email:
        return None
    clean_email = email.strip().lower()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, name, email, password_hash, is_verified, 
                   verification_otp, otp_expiry, reset_otp, reset_expiry,
                   failed_login_attempts, account_locked_until, created_at, updated_at 
            FROM users WHERE email = ? COLLATE NOCASE
            """, 
            (clean_email,)
        )
        row = cursor.fetchone()
        if row:
            return dict(row)
    return None


def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    """Fetches user record by unique ID."""
    if not user_id:
        return None
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, name, email, password_hash, is_verified, 
                   verification_otp, otp_expiry, reset_otp, reset_expiry,
                   failed_login_attempts, account_locked_until, created_at, updated_at 
            FROM users WHERE id = ?
            """, 
            (user_id,)
        )
        row = cursor.fetchone()
        if row:
            return dict(row)
    return None


def create_user(
    name: str, 
    email: str, 
    password_hash: str, 
    verification_otp: Optional[str] = None,
    otp_expiry: Optional[str] = None,
    is_verified: int = 0
) -> Dict[str, Any]:
    """Creates a new user record with registration OTP."""
    user_id = f"usr_{uuid.uuid4().hex[:12]}"
    clean_name = name.strip()
    clean_email = email.strip().lower()
    now_iso = datetime.now(timezone.utc).isoformat()

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO users (id, name, email, password_hash, is_verified, verification_otp, otp_expiry, created_at, updated_at) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (user_id, clean_name, clean_email, password_hash, is_verified, verification_otp, otp_expiry, now_iso, now_iso)
        )
        conn.commit()

    return {
        "id": user_id,
        "name": clean_name,
        "email": clean_email,
        "is_verified": is_verified,
        "verification_otp": verification_otp,
        "otp_expiry": otp_expiry,
    }


def set_verification_otp(email: str, otp: str, expiry_iso: str) -> bool:
    """Sets a new verification OTP and expiry timestamp."""
    clean_email = email.strip().lower()
    now_iso = datetime.now(timezone.utc).isoformat()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET verification_otp = ?, otp_expiry = ?, updated_at = ? WHERE email = ? COLLATE NOCASE",
            (otp, expiry_iso, now_iso, clean_email)
        )
        conn.commit()
        return cursor.rowcount > 0


def verify_user_otp(email: str, otp: str) -> Dict[str, Any]:
    """Validates registration OTP."""
    user = get_user_by_email(email)
    if not user:
        return {"status": "not_found", "message": "Account not found."}

    stored_otp = user.get("verification_otp")
    stored_expiry = user.get("otp_expiry")

    if not stored_otp or stored_otp != otp.strip():
        return {"status": "invalid", "message": "Invalid OTP."}

    if stored_expiry:
        try:
            expiry_dt = datetime.fromisoformat(stored_expiry)
            if datetime.now(timezone.utc) > expiry_dt:
                return {
                    "status": "expired", 
                    "message": "OTP expired. Request a new OTP."
                }
        except Exception:
            pass

    now_iso = datetime.now(timezone.utc).isoformat()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET is_verified = 1, verification_otp = NULL, otp_expiry = NULL, updated_at = ? WHERE id = ?",
            (now_iso, user["id"])
        )
        conn.commit()

    return {"status": "success", "message": "Email verified successfully.", "user": user}


def set_reset_otp(email: str, otp: str, expiry_iso: str) -> bool:
    """Sets the password reset OTP."""
    clean_email = email.strip().lower()
    now_iso = datetime.now(timezone.utc).isoformat()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET reset_otp = ?, reset_expiry = ?, updated_at = ? WHERE email = ? COLLATE NOCASE",
            (otp, expiry_iso, now_iso, clean_email)
        )
        conn.commit()
        return cursor.rowcount > 0


def verify_reset_otp_only(email: str, otp: str) -> Dict[str, Any]:
    """Validates reset OTP without resetting password yet."""
    user = get_user_by_email(email)
    if not user:
        return {"status": "not_found", "message": "Account not found."}

    stored_otp = user.get("reset_otp")
    stored_expiry = user.get("reset_expiry")

    if not stored_otp or stored_otp != otp.strip():
        return {"status": "invalid", "message": "Invalid OTP."}

    if stored_expiry:
        try:
            expiry_dt = datetime.fromisoformat(stored_expiry)
            if datetime.now(timezone.utc) > expiry_dt:
                return {
                    "status": "expired", 
                    "message": "OTP expired. Request a new OTP."
                }
        except Exception:
            pass

    return {"status": "success", "message": "OTP verified successfully.", "user": user}


def update_password_with_reset_otp(email: str, new_password_hash: str) -> bool:
    """Updates password and clears reset OTP."""
    clean_email = email.strip().lower()
    now_iso = datetime.now(timezone.utc).isoformat()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE users 
            SET password_hash = ?, reset_otp = NULL, reset_expiry = NULL, 
                failed_login_attempts = 0, account_locked_until = NULL, updated_at = ? 
            WHERE email = ? COLLATE NOCASE
            """,
            (new_password_hash, now_iso, clean_email)
        )
        conn.commit()
        return cursor.rowcount > 0


def record_failed_login(email: str, lock_duration_minutes: int = 15) -> Dict[str, Any]:
    """
    Increments failed login attempts.
    Locks account for 15 minutes if attempts reach 5.
    """
    clean_email = email.strip().lower()
    user = get_user_by_email(clean_email)
    if not user:
        return {"locked": False, "attempts": 0}

    attempts = user.get("failed_login_attempts", 0) + 1
    locked_until = None
    if attempts >= 5:
        from datetime import timedelta
        locked_until = (datetime.now(timezone.utc) + timedelta(minutes=lock_duration_minutes)).isoformat()

    now_iso = datetime.now(timezone.utc).isoformat()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET failed_login_attempts = ?, account_locked_until = ?, updated_at = ? WHERE email = ? COLLATE NOCASE",
            (attempts, locked_until, now_iso, clean_email)
        )
        conn.commit()

    return {"locked": locked_until is not None, "attempts": attempts, "locked_until": locked_until}


def reset_failed_login_attempts(email: str) -> None:
    """Resets failed attempts and unlocks account upon successful login."""
    clean_email = email.strip().lower()
    now_iso = datetime.now(timezone.utc).isoformat()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET failed_login_attempts = 0, account_locked_until = NULL, updated_at = ? WHERE email = ? COLLATE NOCASE",
            (now_iso, clean_email)
        )
        conn.commit()


def update_user_name(user_id: str, new_name: str) -> bool:
    """Updates user display name."""
    clean_name = new_name.strip()
    now_iso = datetime.now(timezone.utc).isoformat()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET name = ?, updated_at = ? WHERE id = ?",
            (clean_name, now_iso, user_id)
        )
        conn.commit()
        return cursor.rowcount > 0


def update_user_password_by_id(user_id: str, new_password_hash: str) -> bool:
    """Updates user password by user ID."""
    now_iso = datetime.now(timezone.utc).isoformat()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET password_hash = ?, reset_otp = NULL, reset_expiry = NULL, updated_at = ? WHERE id = ?",
            (new_password_hash, now_iso, user_id)
        )
        conn.commit()
        return cursor.rowcount > 0


# Rate limit tracking helpers
def record_rate_limit_event(key: str, action: str) -> None:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO rate_limits (key, action) VALUES (?, ?)", (key.strip().lower(), action))
        conn.commit()


def count_recent_events(key: str, action: str, window_minutes: int) -> int:
    from datetime import timedelta
    cutoff = (datetime.now(timezone.utc) - timedelta(minutes=window_minutes)).strftime("%Y-%m-%d %H:%M:%S")
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) as count FROM rate_limits WHERE key = ? AND action = ? AND timestamp >= ?",
            (key.strip().lower(), action, cutoff)
        )
        row = cursor.fetchone()
        return row["count"] if row else 0


# Initialize on load
init_db()
