"""Authentication: password login, forced first-login setup (password change +
TOTP + recovery codes), 2FA verification, refresh rotation, logout.

Login flow
----------
1. POST /auth/login {username, password}
     -> { status: "challenge", challenge_token, pending: [...] }
2. Walk the `pending` steps in order, each authorised by the challenge token:
     - "password_change": POST /auth/challenge/password  (first login only)
     - "totp_setup":      POST /auth/challenge/totp/init  -> QR + secret
                          POST /auth/challenge/totp/verify -> enables 2FA,
                              returns recovery codes ONCE + a full session
     - "totp":            POST /auth/mfa {code}  (TOTP or a recovery code)
                              -> full session
A full session = short-lived access token (JSON) + rotating refresh token
(httpOnly cookie).
"""
from fastapi import APIRouter, Depends, HTTPException, Request, Response

from .. import admin as admin_state
from ..admin import STEP_PASSWORD_CHANGE, STEP_TOTP, STEP_TOTP_SETUP
from ..config import get_settings
from ..schemas import CodeRequest, LoginRequest, PasswordChangeRequest
from ..security import (
    check_lockout,
    create_access_token,
    create_challenge_token,
    create_refresh_token,
    get_challenge_subject,
    get_current_admin,
    hash_password,
    register_failed_attempt,
    reset_attempts,
    revoke_refresh_token,
    rotate_refresh_token,
    validate_password_strength,
    verify_password,
)
from ..twofa import (
    generate_recovery_codes,
    generate_secret,
    hash_recovery_code,
    provisioning_uri,
    qr_png_data_url,
    verify_recovery_code,
    verify_totp,
)

router = APIRouter(prefix="/auth", tags=["auth"])


def _client_ip(request: Request) -> str:
    xff = request.headers.get("x-forwarded-for")
    if xff:
        return xff.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def _set_refresh_cookie(response: Response, token: str) -> None:
    settings = get_settings()
    response.set_cookie(
        key=settings.refresh_cookie_name,
        value=token,
        max_age=settings.refresh_token_ttl_days * 86400,
        path=settings.refresh_cookie_path,
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
    )


def _issue_session(response: Response, username: str) -> dict:
    access, expires_in = create_access_token(username)
    _set_refresh_cookie(response, create_refresh_token(username))
    return {
        "status": "authenticated",
        "access_token": access,
        "token_type": "bearer",
        "expires_in": expires_in,
        "username": username,
    }


def _require_step(step: str):
    """Load admin, ensure `step` is the next expected login step, return admin row."""
    admin = admin_state.get_admin()
    if admin is None:
        raise HTTPException(status_code=500, detail="Admin account not initialised")
    pending = admin_state.compute_pending(admin)
    if not pending or pending[0] != step:
        raise HTTPException(status_code=409, detail=f"Unexpected step. Next required: {pending[0] if pending else 'none'}")
    return admin


def _generate_and_store_recovery_codes() -> list[str]:
    settings = get_settings()
    codes = generate_recovery_codes(settings.recovery_code_count)
    admin_state.replace_recovery_codes([hash_recovery_code(c) for c in codes])
    return codes


# --------------------------------------------------------------------------
@router.post("/login")
async def login(payload: LoginRequest, request: Request):
    settings = get_settings()
    identifier = _client_ip(request)
    check_lockout(identifier)

    admin = admin_state.get_admin()
    if admin is None:
        raise HTTPException(status_code=500, detail="Admin account not initialised")

    username_ok = payload.username == admin["username"]
    password_ok = verify_password(payload.password, admin["password_hash"])
    if not (username_ok and password_ok):
        register_failed_attempt(identifier)
        raise HTTPException(status_code=401, detail="Invalid credentials")

    reset_attempts(identifier)
    pending = admin_state.compute_pending(admin)
    return {
        "status": "challenge",
        "challenge_token": create_challenge_token(admin["username"]),
        "pending": pending,
    }


@router.post("/challenge/password")
async def challenge_password(
    payload: PasswordChangeRequest,
    subject: str = Depends(get_challenge_subject),
):
    _require_step(STEP_PASSWORD_CHANGE)
    validate_password_strength(payload.new_password)
    admin_state.set_password(hash_password(payload.new_password))
    admin = admin_state.get_admin()
    return {
        "status": "challenge",
        "challenge_token": create_challenge_token(subject),
        "pending": admin_state.compute_pending(admin),
    }


@router.post("/challenge/totp/init")
async def challenge_totp_init(subject: str = Depends(get_challenge_subject)):
    _require_step(STEP_TOTP_SETUP)
    secret = generate_secret()
    admin_state.set_pending_totp_secret(secret)
    uri = provisioning_uri(secret, subject)
    return {
        "secret": secret,
        "otpauth_uri": uri,
        "qr_png": qr_png_data_url(uri),
    }


@router.post("/challenge/totp/verify")
async def challenge_totp_verify(
    payload: CodeRequest,
    response: Response,
    subject: str = Depends(get_challenge_subject),
):
    admin = _require_step(STEP_TOTP_SETUP)
    secret = admin["pending_totp_secret"]
    if not secret:
        raise HTTPException(status_code=409, detail="Start TOTP setup first")
    if not verify_totp(secret, payload.code):
        raise HTTPException(status_code=401, detail="Invalid authentication code")

    admin_state.enable_totp(secret)
    recovery_codes = _generate_and_store_recovery_codes()
    session = _issue_session(response, subject)
    session["recovery_codes"] = recovery_codes
    return session


@router.post("/mfa")
async def mfa(
    payload: CodeRequest,
    response: Response,
    subject: str = Depends(get_challenge_subject),
):
    admin = _require_step(STEP_TOTP)
    code = payload.code.strip()

    if verify_totp(admin["totp_secret"], code):
        return _issue_session(response, subject)

    # Fall back to a single-use recovery code.
    for row in admin_state.get_unused_recovery_codes():
        if verify_recovery_code(code, row["code_hash"]):
            admin_state.mark_recovery_code_used(row["id"])
            return _issue_session(response, subject)

    raise HTTPException(status_code=401, detail="Invalid authentication or recovery code")


@router.post("/refresh")
async def refresh(request: Request, response: Response):
    settings = get_settings()
    token = request.cookies.get(settings.refresh_cookie_name)
    if not token:
        raise HTTPException(status_code=401, detail="No refresh token")
    _set_refresh_cookie(response, rotate_refresh_token(token))
    access, expires_in = create_access_token(settings.admin_username)
    return {
        "status": "authenticated",
        "access_token": access,
        "token_type": "bearer",
        "expires_in": expires_in,
        "username": settings.admin_username,
    }


@router.post("/logout")
async def logout(request: Request, response: Response):
    settings = get_settings()
    token = request.cookies.get(settings.refresh_cookie_name)
    if token:
        revoke_refresh_token(token)
    response.delete_cookie(settings.refresh_cookie_name, path=settings.refresh_cookie_path)
    return {"message": "Logged out"}


@router.get("/me")
async def me(username: str = Depends(get_current_admin)):
    return {"username": username}


@router.post("/recovery/regenerate")
async def regenerate_recovery(_: str = Depends(get_current_admin)):
    return {"recovery_codes": _generate_and_store_recovery_codes()}
