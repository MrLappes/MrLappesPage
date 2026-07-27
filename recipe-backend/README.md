# PlatePal Recipe Wiki — Backend

A small, security-focused FastAPI + SQLite backend that powers the public recipe
wiki. Everyone can read recipes and ingredients; only the single admin (protected
by a password + TOTP two-factor auth) can create or edit content.

## Highlights

- **Argon2** password hashing.
- **Forced first-login setup**: change the bootstrap password, then enable 2FA.
- **TOTP two-factor auth** (Google Authenticator / Aegis / 1Password, etc.) with a
  QR code and **single-use recovery codes** shown once.
- **Short-lived access JWTs** (15 min, kept in browser memory) + **rotating refresh
  tokens** in an httpOnly cookie, with reuse detection.
- **Brute-force protection** with per-IP exponential lockout.
- **Server-side HTML sanitisation** (`nh3`) of all rich text — no stored XSS.
- **Image hardening**: uploads are validated, stripped of metadata, downscaled and
  re-encoded to WEBP, stored as BLOBs.
- **Full multilingual** content: every recipe/ingredient must have all locales
  (`en, de, cs, jp`).
- **Automatic nutrition** totals and per-serving values computed from ingredients.

No secrets live in the repo — `.env` and the database are git-ignored.

## Setup

```bash
cd recipe-backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# generate JWT_SECRET + ADMIN_PASSWORD_HASH
python hash_password.py

cp .env.example .env
# paste the generated values into .env
# for local http dev keep COOKIE_SECURE=false
```

## Run

```bash
source venv/bin/activate
uvicorn app.main:app --host 127.0.0.1 --port 8091 --reload
# or: python -m app.main
```

Health check: `GET http://127.0.0.1:8091/api/health`

The Vite dev server proxies `/wiki-api` → this backend (`/api`).

## First login

1. Log in with the bootstrap username/password.
2. You are forced to set a new strong password.
3. Scan the QR code with an authenticator app and confirm a code to enable 2FA.
4. **Save the recovery codes** — they are shown only once.

Subsequent logins require the password + a current 2FA code (or a recovery code).

## Production notes

- Set `COOKIE_SECURE=true` and serve over HTTPS.
- Set `ALLOWED_ORIGINS` to your real frontend origin.
- Keep `.env` and `recipes.db` off version control (already git-ignored).

## Docker deployment

The backend ships as a container that binds to `127.0.0.1:8091` (loopback only —
nginx is the sole entry point). SQLite is persisted on a named volume.

```bash
cd recipe-backend
cp .env.example .env      # then fill in prod values:
                          #   COOKIE_SECURE=true
                          #   ALLOWED_ORIGINS=https://plate-pal.de
                          #   DATABASE_PATH=/app/data/recipes.db
sudo docker compose up -d --build
```

Then wire nginx (see `deploy/nginx/platepal.conf`): add the `/wiki-api/`
location to the `plate-pal.de` server block so `https://plate-pal.de/wiki-api/*`
proxies to the container's `/api/*`, and reload nginx:

```bash
sudo nginx -t && sudo systemctl reload nginx
curl https://plate-pal.de/wiki-api/health   # -> {"status":"ok"}
```

