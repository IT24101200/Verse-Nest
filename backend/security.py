# -*- coding: utf-8 -*-
"""
VerseNest Originals - Security & Cryptographic Authentication Engine
Implements PBKDF2-HMAC-SHA256 password hashing with salt,
cryptographic token signing, secret rotation, and environment variable management.
"""
import os
import hmac
import hashlib
import secrets
import time
from typing import Tuple, Optional

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
        print(f"[Security] Generated new .env file with secure secrets.")

ensure_env_file()
load_env()

SECRET_KEY = os.environ.get("VERSENEST_SECRET_KEY", "")
if not SECRET_KEY:
    SECRET_KEY = secrets.token_hex(32)
    os.environ["VERSENEST_SECRET_KEY"] = SECRET_KEY

def hash_password(password: str) -> str:
    """Hashes a plaintext password using PBKDF2-HMAC-SHA256 with a 16-byte random salt."""
    salt = secrets.token_bytes(16)
    pwd_hash = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100000)
    return f"pbkdf2_sha256$100000${salt.hex()}${pwd_hash.hex()}"

def verify_password(password: str, stored_hash: str) -> bool:
    """Verifies a password against a stored PBKDF2-HMAC-SHA256 hash."""
    try:
        parts = stored_hash.split("$")
        if len(parts) != 4 or parts[0] != "pbkdf2_sha256":
            return False
        iterations = int(parts[1])
        salt = bytes.fromhex(parts[2])
        expected_hash = bytes.fromhex(parts[3])
        computed_hash = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
        return hmac.compare_digest(expected_hash, computed_hash)
    except Exception:
        return False

def generate_session_token(username: str, duration_hours: int = 8) -> str:
    """Generates an HMAC-signed session bearer token with expiration."""
    expiry = int(time.time()) + (duration_hours * 3600)
    payload = f"{username}:{expiry}"
    sig = hmac.new(SECRET_KEY.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256).hexdigest()
    return f"{payload}:{sig}"

def verify_session_token(token: Optional[str]) -> Tuple[bool, Optional[str]]:
    """
    Verifies token signature and expiration.
    Returns (is_valid, username).
    """
    if not token:
        return False, None
    parts = token.split(":")
    if len(parts) != 3:
        return False, None
    username, expiry_str, sig = parts
    try:
        expiry = int(expiry_str)
        if time.time() > expiry:
            return False, None
        expected_sig = hmac.new(SECRET_KEY.encode("utf-8"), f"{username}:{expiry}".encode("utf-8"), hashlib.sha256).hexdigest()
        if hmac.compare_digest(sig, expected_sig):
            return True, username
        return False, None
    except Exception:
        return False, None
