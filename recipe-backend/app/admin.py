"""Admin account state: bootstrap from .env, then live in the database.

The `.env` only seeds the account on first run. After the forced first-login
password change and 2FA setup, the authoritative state (password hash, TOTP
secret, recovery codes) lives entirely in SQLite.
"""
import sqlite3

from .config import get_settings
from .database import db_cursor

# Ordered login steps the client must complete.
STEP_PASSWORD_CHANGE = "password_change"
STEP_TOTP_SETUP = "totp_setup"
STEP_TOTP = "totp"


def bootstrap_admin() -> None:
    """Seed the single admin row from .env if it does not exist yet."""
    settings = get_settings()
    with db_cursor(commit=True) as cur:
        cur.execute("SELECT id FROM admin_account WHERE id = 1")
        if cur.fetchone() is None:
            cur.execute(
                "INSERT INTO admin_account (id, username, password_hash, must_change_password, "
                "totp_enabled) VALUES (1, ?, ?, 1, 0)",
                (settings.admin_username, settings.admin_password_hash),
            )


def get_admin() -> sqlite3.Row | None:
    with db_cursor() as cur:
        cur.execute("SELECT * FROM admin_account WHERE id = 1")
        return cur.fetchone()


def compute_pending(admin: sqlite3.Row) -> list[str]:
    """Return the remaining login steps for the given admin state."""
    pending: list[str] = []
    if admin["must_change_password"]:
        pending.append(STEP_PASSWORD_CHANGE)
    if not admin["totp_enabled"]:
        pending.append(STEP_TOTP_SETUP)
    if not pending:
        # Password fine + TOTP enabled -> still need a fresh 2FA code this session.
        pending.append(STEP_TOTP)
    return pending


def set_password(new_hash: str) -> None:
    with db_cursor(commit=True) as cur:
        cur.execute(
            "UPDATE admin_account SET password_hash = ?, must_change_password = 0, "
            "updated_at = CURRENT_TIMESTAMP WHERE id = 1",
            (new_hash,),
        )


def set_pending_totp_secret(secret: str) -> None:
    with db_cursor(commit=True) as cur:
        cur.execute(
            "UPDATE admin_account SET pending_totp_secret = ?, updated_at = CURRENT_TIMESTAMP WHERE id = 1",
            (secret,),
        )


def enable_totp(secret: str) -> None:
    with db_cursor(commit=True) as cur:
        cur.execute(
            "UPDATE admin_account SET totp_secret = ?, pending_totp_secret = NULL, "
            "totp_enabled = 1, updated_at = CURRENT_TIMESTAMP WHERE id = 1",
            (secret,),
        )


def replace_recovery_codes(code_hashes: list[str]) -> None:
    with db_cursor(commit=True) as cur:
        cur.execute("DELETE FROM admin_recovery_codes")
        cur.executemany(
            "INSERT INTO admin_recovery_codes (code_hash) VALUES (?)",
            [(h,) for h in code_hashes],
        )


def get_unused_recovery_codes() -> list[sqlite3.Row]:
    with db_cursor() as cur:
        cur.execute("SELECT id, code_hash FROM admin_recovery_codes WHERE used = 0")
        return cur.fetchall()


def mark_recovery_code_used(code_id: int) -> None:
    with db_cursor(commit=True) as cur:
        cur.execute("UPDATE admin_recovery_codes SET used = 1 WHERE id = ?", (code_id,))
