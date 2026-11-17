# -*- coding: utf-8 -*-
"""
VerseNest Originals - Admin User Management CLI
Safely creates, rotates, and manages securely hashed administrator credentials in SQLite.
Enforces 600,000 iterations PBKDF2-HMAC-SHA256 and blocks default credentials.
"""
import argparse
import os
import sys
from database import get_db_connection, init_db
from security import hash_password, load_env, is_password_allowed

def set_admin_credentials(username: str, password: str, role: str = "admin"):
    """Inserts or updates an administrator user with PBKDF2 600,000-iteration hash."""
    allowed, msg = is_password_allowed(password)
    if not allowed:
        print(f"[Admin CLI Error] {msg}")
        sys.exit(1)

    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()

    pwd_hash = hash_password(password, iterations=600000)
    cursor.execute("""
        INSERT INTO admin_users (username, password_hash, role)
        VALUES (?, ?, ?)
        ON CONFLICT(username) DO UPDATE SET
            password_hash = excluded.password_hash,
            role = excluded.role;
    """, (username, pwd_hash, role))
    conn.commit()
    conn.close()
    print(f"[Admin CLI] Admin user '{username}' successfully configured with 600,000-iteration PBKDF2 password hash.")

if __name__ == "__main__":
    load_env()
    parser = argparse.ArgumentParser(description="Manage VerseNest Administrator Credentials")
    parser.add_argument("--username", default=os.environ.get("ADMIN_USER", "admin"), help="Admin username")
    parser.add_argument("--password", default=os.environ.get("ADMIN_PASS", ""), help="Admin password")
    parser.add_argument("--role", default="admin", help="Admin role")
    args = parser.parse_args()

    if not args.password:
        import secrets
        args.password = secrets.token_urlsafe(16)
        print(f"[Admin CLI] No password provided. Generated temporary password: {args.password}")

    set_admin_credentials(args.username, args.password, args.role)
