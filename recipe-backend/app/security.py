"""Authentication & authorisation primitives.

- Passwords: Argon2 (memory-hard).
- Access tokens: short-lived signed JWTs (type "access"), kept in browser memory.
- Challenge tokens: short-lived JWTs (type "challenge") that only prove the
  password step passed; they gate the first-login setup and the 2FA step.
- Refresh tokens: opaque, stored only as SHA-256 hashes, rotated on every use;
  reuse of a rotated token revokes the whole family.
- Login attempts: per-client rate limiting with exponential lockout.
"""
import hashlib
import re
import secrets
from datetime import datetime, timedelta, timezone

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import Argon2Error
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .config import get_settings
from .database import db_cursor

_ph = PasswordHasher()
_bearer = HTTPBearer(auto_error=True)

TYPE_ACCESS = "access"
TYPE_CHALLENGE = "challenge"


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _parse_ts(value: str) -> datetime:
    dt = datetime.fromisoformat(value)
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


# --- Password hashing & policy --------------------------------------------
def hash_password(password: str) -> str:
    return _ph.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return _ph.verify(password_hash, password)
    except (Argon2Error, ValueError, TypeError):
        return False


def validate_password_strength(password: str) -> None:
    settings = get_settings()
    errors = []
    if len(password) < settings.password_min_length:
        errors.append(f"at least {settings.password_min_length} characters")
    if not re.search(r"[a-z]", password):
        errors.append("a lowercase letter")
    if not re.search(r"[A-Z]", password):
        errors.append("an uppercase letter")
    if not re.search(r"\d", password):
        errors.append("a digit")
    if errors:
        raise HTTPException(status_code=422, detail="Password must contain " + ", ".join(errors))


# --- JWT: access & challenge ----------------------------------------------
def _encode(claims: dict, ttl_seconds: int, token_type: str, username: str) -> tuple[str, int]:
    settings = get_settings()
    now = _now()
    payload = {
        **claims,
        "sub": username,
        "type": token_type,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(seconds=ttl_seconds)).timestamp()),
    }
    token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return token, ttl_seconds


def create_access_token(username: str) -> tuple[str, int]:
    settings = get_settings()
    return _encode({}, settings.access_token_ttl_minutes * 60, TYPE_ACCESS, username)


def create_challenge_token(username: str) -> str:
    settings = get_settings()
    token, _ = _encode({}, settings.challenge_token_ttl_minutes * 60, TYPE_CHALLENGE, username)
    return token


def _decode(token: str, expected_type: str) -> dict:
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    if payload.get("type") != expected_type or payload.get("sub") != settings.admin_username:
        raise HTTPException(status_code=401, detail="Not authorized")
    return payload


def get_current_admin(credentials: HTTPAuthorizationCredentials = Depends(_bearer)) -> str:
    return _decode(credentials.credentials, TYPE_ACCESS)["sub"]


def get_challenge_subject(credentials: HTTPAuthorizationCredentials = Depends(_bearer)) -> str:
    return _decode(credentials.credentials, TYPE_CHALLENGE)["sub"]


# --- Refresh tokens (opaque, hashed, rotated) ------------------------------
def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def create_refresh_token(username: str) -> str:
    settings = get_settings()
    jti = secrets.token_urlsafe(16)
    raw = secrets.token_urlsafe(48)
    token = f"{jti}.{raw}"
    expires_at = _now() + timedelta(days=settings.refresh_token_ttl_days)
    with db_cursor(commit=True) as cur:
        cur.execute(
            "INSERT INTO admin_refresh_tokens (jti, token_hash, expires_at) VALUES (?, ?, ?)",
            (jti, _hash_token(token), expires_at.isoformat()),
        )
    return token


def rotate_refresh_token(token: str) -> str:
    settings = get_settings()
    if not token or "." not in token:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    jti = token.split(".", 1)[0]
    with db_cursor(commit=True) as cur:
        cur.execute(
            "SELECT token_hash, expires_at, revoked FROM admin_refresh_tokens WHERE jti = ?",
            (jti,),
        )
        row = cur.fetchone()
        if row is None:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        if row["revoked"]:
            cur.execute("UPDATE admin_refresh_tokens SET revoked = 1")  # reuse -> revoke all
            raise HTTPException(status_code=401, detail="Refresh token reuse detected")
        if not secrets.compare_digest(_hash_token(token), row["token_hash"]):
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        if _parse_ts(row["expires_at"]) < _now():
            cur.execute("UPDATE admin_refresh_tokens SET revoked = 1 WHERE jti = ?", (jti,))
            raise HTTPException(status_code=401, detail="Refresh token expired")
        cur.execute("UPDATE admin_refresh_tokens SET revoked = 1 WHERE jti = ?", (jti,))
    return create_refresh_token(settings.admin_username)


def revoke_refresh_token(token: str) -> None:
    if not token or "." not in token:
        return
    jti = token.split(".", 1)[0]
    with db_cursor(commit=True) as cur:
        cur.execute("UPDATE admin_refresh_tokens SET revoked = 1 WHERE jti = ?", (jti,))


def cleanup_expired_tokens() -> None:
    with db_cursor(commit=True) as cur:
        cur.execute("DELETE FROM admin_refresh_tokens WHERE expires_at < ?", (_now().isoformat(),))


# --- Login brute-force protection -----------------------------------------
def check_lockout(identifier: str) -> None:
    with db_cursor() as cur:
        cur.execute("SELECT locked_until FROM login_attempts WHERE id = ?", (identifier,))
        row = cur.fetchone()
    if row and row["locked_until"]:
        locked_until = _parse_ts(row["locked_until"])
        if locked_until > _now():
            retry = int((locked_until - _now()).total_seconds()) + 1
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Too many attempts. Try again in {retry} seconds.",
                headers={"Retry-After": str(retry)},
            )


def register_failed_attempt(identifier: str) -> None:
    settings = get_settings()
    with db_cursor(commit=True) as cur:
        cur.execute("SELECT attempts FROM login_attempts WHERE id = ?", (identifier,))
        row = cur.fetchone()
        attempts = (row["attempts"] if row else 0) + 1
        locked_until = None
        if attempts >= settings.login_max_attempts:
            over = attempts - settings.login_max_attempts
            lock_seconds = settings.login_lockout_seconds * (2 ** min(over, 6))
            locked_until = (_now() + timedelta(seconds=lock_seconds)).isoformat()
        cur.execute(
            "INSERT INTO login_attempts (id, attempts, locked_until, updated_at) "
            "VALUES (?, ?, ?, CURRENT_TIMESTAMP) "
            "ON CONFLICT(id) DO UPDATE SET attempts = excluded.attempts, "
            "locked_until = excluded.locked_until, updated_at = CURRENT_TIMESTAMP",
            (identifier, attempts, locked_until),
        )


def reset_attempts(identifier: str) -> None:
    with db_cursor(commit=True) as cur:
        cur.execute("DELETE FROM login_attempts WHERE id = ?", (identifier,))
