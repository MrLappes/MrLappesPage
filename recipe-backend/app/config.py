"""Application configuration loaded from environment / .env.

The .env file holds only the *bootstrap* admin credentials and the JWT secret.
All live security state (current password hash after first-login change, TOTP
secret, recovery-code hashes) lives in the SQLite database, never in the repo.
"""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: str = "production"

    # --- Auth / JWT (required => app refuses to start if unset) ---
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    access_token_ttl_minutes: int = 15
    refresh_token_ttl_days: int = 7
    challenge_token_ttl_minutes: int = 10  # partial-auth window for login/setup steps

    # --- Bootstrap admin (seeds the DB on first run only) ---
    admin_username: str
    admin_password_hash: str  # argon2 hash produced by hash_password.py

    # --- Two-factor auth ---
    totp_issuer: str = "PlatePal Wiki"
    recovery_code_count: int = 10

    # --- Password policy (enforced on first-login change) ---
    password_min_length: int = 12

    # --- Refresh cookie ---
    refresh_cookie_name: str = "wiki_refresh"
    refresh_cookie_path: str = "/wiki-api/auth"
    cookie_secure: bool = True
    cookie_samesite: str = "strict"

    # --- CORS ---
    allowed_origins: str = "http://localhost:5173"

    # --- Database ---
    database_path: str = "recipes.db"

    # --- Uploads ---
    max_image_bytes: int = 5 * 1024 * 1024
    image_max_dimension: int = 1600

    # --- Login brute-force protection ---
    login_max_attempts: int = 5
    login_lockout_seconds: int = 300

    # --- Locales (all required for every translated entity) ---
    supported_locales: str = "en,de,cs,jp"

    @property
    def origins_list(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]

    @property
    def locales_list(self) -> list[str]:
        return [loc.strip() for loc in self.supported_locales.split(",") if loc.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
