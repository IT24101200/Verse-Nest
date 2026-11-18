# -*- coding: utf-8 -*-
"""
VerseNest Originals - Security & Cryptographic Authentication Engine
Upgraded security implementation:
- PBKDF2-HMAC-SHA256 with 600,000 iterations and 16-byte cryptographically secure salt.
- Automatic hash migration from older iteration counts (< 600,000) to 600,000 iterations.
- Protection against known default or weak credentials.
- IP and username login rate limiting with sliding window tracking in SQLite.
- Cryptographic session token signing, expiration, and server-side revocation / logout.
- Environment variable persistence and automated production secret generation.
"""
import os
import hmac
import hashlib
import secrets
import time
from typing import Tuple, Optional, Dict, Any
from database import get_db_connection

# Load or generate .env file
ENV_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")

def load_env():
    """Loads environment variables from .env file if present."""
    if os.path.exists(ENV_PATH):
        with open(ENV_PATH, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip())

def ensure_env_file():
    """Ensures a secure .env file exists with generated cryptographically strong secrets."""
    if not os.path.exists(ENV_PATH):
        jwt_sec = secrets.token_hex(32)
        admin_pass = secrets.token_urlsafe(16)
        content = f"""# VerseNest Production Environment Configuration
# Automatically generated secure secrets
VERSENEST_SECRET_KEY={jwt_sec}
ADMIN_USER=admin
ADMIN_PASS={admin_pass}
ENVIRONMENT=production
"""
        with open(ENV_PATH, "w", encoding="utf-8") as f:
            f.write(content)

ensure_env_file()
load_env()

SECRET_KEY = os.environ.get("SECRET_KEY") or os.environ.get("VERSENEST_SECRET_KEY", "")
if not SECRET_KEY:
    SECRET_KEY = secrets.token_hex(32)
    os.environ["SECRET_KEY"] = SECRET_KEY
    os.environ["VERSENEST_SECRET_KEY"] = SECRET_KEY

ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME") or os.environ.get("ADMIN_USER", "admin")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD") or os.environ.get("ADMIN_PASS", "")

def bootstrap_admin_user():
    """
    Ensures administrator credentials provided via environment variables
    are safely hashed and synchronized to the SQLite admin_users table.
    """
    if ADMIN_PASSWORD:
        allowed, _ = is_password_allowed(ADMIN_PASSWORD)
        if allowed:
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                pwd_hash = hash_password(ADMIN_PASSWORD, iterations=PBKDF2_ITERATIONS)
                cursor.execute("""
                    INSERT INTO admin_users (username, password_hash, role)
                    VALUES (?, ?, 'admin')
                    ON CONFLICT(username) DO UPDATE SET password_hash = excluded.password_hash;
                """, (ADMIN_USERNAME, pwd_hash))
                conn.commit()
                conn.close()
            except Exception as e:
                print(f"[SECURITY] Warning during admin bootstrap: {e}")

# Security parameters
PBKDF2_ITERATIONS = 600000
DISALLOWED_DEFAULT_PASSWORDS = {"versenest2026", "admin", "admin123", "password", "12345678", "guest"}
MAX_FAILED_LOGIN_ATTEMPTS = 5
RATE_LIMIT_WINDOW_SECONDS = 300  # 5 minutes

def hash_password(password: str, iterations: int = PBKDF2_ITERATIONS) -> str:
    """Hashes a password using PBKDF2-HMAC-SHA256 with a 16-byte random salt and 600,000 iterations."""
    salt = secrets.token_bytes(16)
    pwd_hash = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return f"pbkdf2_sha256${iterations}${salt.hex()}${pwd_hash.hex()}"

def verify_and_check_rehash(password: str, stored_hash: str) -> Tuple[bool, bool]:
    """
    Verifies password against stored PBKDF2 hash.
    Returns (is_valid, needs_rehash).
    needs_rehash is True if iteration count is less than 600,000.
    """
    try:
        parts = stored_hash.split("$")
        if len(parts) != 4 or parts[0] != "pbkdf2_sha256":
            return False, False
        iterations = int(parts[1])
        salt = bytes.fromhex(parts[2])
        expected_hash = bytes.fromhex(parts[3])
        computed_hash = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
        is_valid = hmac.compare_digest(expected_hash, computed_hash)
        needs_rehash = is_valid and (iterations < PBKDF2_ITERATIONS)
        return is_valid, needs_rehash
    except Exception:
        return False, False

def verify_password(password: str, stored_hash: str) -> bool:
    """Convenience wrapper for verify_and_check_rehash."""
    is_valid, _ = verify_and_check_rehash(password, stored_hash)
    return is_valid

def is_password_allowed(password: str) -> Tuple[bool, str]:
    """Checks whether password meets basic security standards and is not a known default."""
    if not password or len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if password.lower() in DISALLOWED_DEFAULT_PASSWORDS:
        return False, "The default password is disabled for production security. Please choose a unique password."
    return True, ""

# ==================== LOGIN RATE LIMITING ====================

def check_login_rate_limit(ip: str, username: str) -> Tuple[bool, int]:
    """
    Checks if client IP or username has exceeded allowed failed login attempts.
    Returns (is_allowed, retry_after_seconds).
    """
    now = int(time.time())
    cutoff = now - RATE_LIMIT_WINDOW_SECONDS

    conn = get_db_connection()
    cursor = conn.cursor()

    # Clean old attempts older than 1 hour
    cursor.execute("DELETE FROM login_attempts WHERE attempted_at < ?;", (now - 3600,))

    # Count failed attempts for this IP or username in current window
    cursor.execute("""
        SELECT COUNT(*), MAX(attempted_at) FROM login_attempts
        WHERE (ip = ? OR username = ?) AND success = 0 AND attempted_at >= ?;
    """, (ip, username, cutoff))
    row = cursor.fetchone()
    failed_count = row[0] if row else 0
    latest_attempt = row[1] if row and row[1] else now

    conn.commit()
    conn.close()

    if failed_count >= MAX_FAILED_LOGIN_ATTEMPTS:
        retry_after = max(1, RATE_LIMIT_WINDOW_SECONDS - (now - latest_attempt))
        return False, retry_after

    return True, 0

def record_login_attempt(ip: str, username: str, success: bool):
    """Records a login attempt (success or failure) for security auditing."""
    now = int(time.time())
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO login_attempts (ip, username, attempted_at, success)
        VALUES (?, ?, ?, ?);
    """, (ip, username, now, 1 if success else 0))

    # If login was successful, clear previous failures for this IP/username
    if success:
        cursor.execute("""
            DELETE FROM login_attempts WHERE (ip = ? OR username = ?) AND success = 0;
        """, (ip, username))

    conn.commit()
    conn.close()

# ==================== SESSION TOKEN MANAGEMENT & REVOCATION ====================

def generate_session_token(username: str, duration_hours: int = 8) -> str:
    """Generates an HMAC-signed session bearer token with timestamp."""
    expiry = int(time.time()) + (duration_hours * 3600)
    nonce = secrets.token_hex(8)
    payload = f"{username}:{expiry}:{nonce}"
    sig = hmac.new(SECRET_KEY.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256).hexdigest()
    return f"{payload}:{sig}"

def is_token_revoked(token_sig: str) -> bool:
    """Checks whether token signature has been revoked in database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    now = int(time.time())
    # Clean expired revoked tokens
    cursor.execute("DELETE FROM revoked_tokens WHERE expires_at < ?;", (now,))
    cursor.execute("SELECT 1 FROM revoked_tokens WHERE token_sig = ?;", (token_sig,))
    revoked = cursor.fetchone() is not None
    conn.commit()
    conn.close()
    return revoked

def revoke_token(token: str) -> bool:
    """Revokes a session bearer token on logout."""
    if not token:
        return False
    parts = token.split(":")
    if len(parts) != 4:
        return False
    _, expiry_str, _, sig = parts
    try:
        expiry = int(expiry_str)
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO revoked_tokens (token_sig, expires_at)
            VALUES (?, ?);
        """, (sig, expiry))
        conn.commit()
        conn.close()
        return True
    except Exception:
        return False

def verify_session_token(token: Optional[str]) -> Tuple[bool, Optional[str]]:
    """
    Verifies token signature, expiration, and ensures it has not been revoked.
    Returns (is_valid, username).
    """
    if not token:
        return False, None
    parts = token.split(":")
    if len(parts) != 4:
        # Also support legacy 3-part tokens without nonce during transition
        if len(parts) == 3:
            username, expiry_str, sig = parts
            try:
                expiry = int(expiry_str)
                if time.time() > expiry:
                    return False, None
                expected_sig = hmac.new(SECRET_KEY.encode("utf-8"), f"{username}:{expiry}".encode("utf-8"), hashlib.sha256).hexdigest()
                if hmac.compare_digest(sig, expected_sig) and not is_token_revoked(sig):
                    return True, username
            except Exception:
                pass
        return False, None

    username, expiry_str, nonce, sig = parts
    try:
        expiry = int(expiry_str)
        if time.time() > expiry:
            return False, None
        payload = f"{username}:{expiry}:{nonce}"
        expected_sig = hmac.new(SECRET_KEY.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(sig, expected_sig):
            return False, None
        if is_token_revoked(sig):
            return False, None
        return True, username
    except Exception:
        return False, None
