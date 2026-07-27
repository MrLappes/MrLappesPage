"""Two-factor authentication helpers (TOTP + QR + recovery codes).

Uses the open-source libraries:
- pyotp  (MIT)  -> RFC-6238 TOTP secrets & verification
- qrcode (BSD)  -> renders the otpauth:// URI to a PNG
- argon2 (MIT)  -> hashes single-use recovery codes
"""
import base64
import io
import secrets

import pyotp
import qrcode
from argon2 import PasswordHasher
from argon2.exceptions import Argon2Error

from .config import get_settings

_ph = PasswordHasher()


# --- TOTP ------------------------------------------------------------------
def generate_secret() -> str:
    return pyotp.random_base32()


def provisioning_uri(secret: str, username: str) -> str:
    settings = get_settings()
    return pyotp.TOTP(secret).provisioning_uri(name=username, issuer_name=settings.totp_issuer)


def verify_totp(secret: str, code: str) -> bool:
    if not secret or not code:
        return False
    # valid_window=1 tolerates a +/-30s clock drift.
    return pyotp.TOTP(secret).verify(code.strip().replace(" ", ""), valid_window=1)


def qr_png_data_url(uri: str) -> str:
    img = qrcode.make(uri)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode("ascii")
    return f"data:image/png;base64,{b64}"


# --- Recovery codes --------------------------------------------------------
def generate_recovery_codes(count: int) -> list[str]:
    # Human-friendly grouped codes, e.g. "a1b2c3d4-e5f6g7h8".
    codes = []
    for _ in range(count):
        raw = secrets.token_hex(8)
        codes.append(f"{raw[:8]}-{raw[8:]}")
    return codes


def hash_recovery_code(code: str) -> str:
    return _ph.hash(code)


def verify_recovery_code(code: str, code_hash: str) -> bool:
    try:
        return _ph.verify(code_hash, code)
    except (Argon2Error, ValueError, TypeError):
        return False
