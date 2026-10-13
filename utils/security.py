import hashlib
import os
import hmac


def generate_salt() -> str:
    """Generates a cryptographically secure random salt."""
    return os.urandom(16).hex()


def hash_password(password: str, salt: str = None) -> tuple[str, str]:
    """
    Hashes a password using PBKDF2-HMAC-SHA256 with 100,000 iterations.
    Returns (hex_hash, salt).
    """
    if salt is None:
        salt = generate_salt()
    key = hashlib.pbkdf2_hmac(
        hash_name='sha256',
        password=password.encode('utf-8'),
        salt=salt.encode('utf-8'),
        iterations=100000
    )
    return key.hex(), salt


def verify_password(password: str, salt: str, expected_hash: str) -> bool:
    """Verifies a password against the stored salt and hash using constant-time comparison."""
    calculated_hash, _ = hash_password(password, salt)
    return hmac.compare_digest(calculated_hash, expected_hash)
