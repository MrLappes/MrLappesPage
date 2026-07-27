#!/usr/bin/env python3
"""Interactive helper to generate an Argon2 password hash and a JWT secret
for the .env file. Nothing is written to disk — copy the output yourself.

    python hash_password.py
"""
import getpass
import secrets

from argon2 import PasswordHasher


def main() -> None:
    ph = PasswordHasher()
    print("PlatePal Wiki — admin bootstrap credential generator\n")
    pw1 = getpass.getpass("Bootstrap admin password: ")
    pw2 = getpass.getpass("Repeat password: ")
    if pw1 != pw2:
        raise SystemExit("Passwords do not match.")
    if len(pw1) < 12:
        print("Warning: fewer than 12 chars. You will be forced to change it on first login anyway.")

    print("\nAdd these lines to your .env file:\n")
    print(f"JWT_SECRET={secrets.token_urlsafe(48)}")
    print(f"ADMIN_PASSWORD_HASH={ph.hash(pw1)}")
    print("\n(ADMIN_USERNAME defaults to 'admin' — change it in .env if you like.)")


if __name__ == "__main__":
    main()
