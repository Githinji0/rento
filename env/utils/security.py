import hashlib
import hmac
import os

PBKDF2_ITERATIONS = 240000


def hash_password(password):
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        PBKDF2_ITERATIONS,
    )
    return digest.hex(), salt.hex()


def verify_password(password, password_hash, password_salt):
    derived = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        bytes.fromhex(password_salt),
        PBKDF2_ITERATIONS,
    )
    return hmac.compare_digest(derived.hex(), password_hash)
