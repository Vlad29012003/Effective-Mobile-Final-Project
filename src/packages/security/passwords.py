import base64
import hashlib
import os
import secrets


class PasswordHasher:
    """PBKDF2-HMAC-SHA256 password hasher with per-password salt.

    Stored format: iterations$salt_b64$hash_b64
    """

    def __init__(self, iterations: int = 390_000, salt_size: int = 16) -> None:
        self._iterations = iterations
        self._salt_size = salt_size

    def hash(self, password: str) -> str:
        salt = os.urandom(self._salt_size)
        digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, self._iterations)
        return (
            f"{self._iterations}"
            f"${base64.b64encode(salt).decode()}"
            f"${base64.b64encode(digest).decode()}"
        )

    def verify(self, password: str, encoded: str) -> bool:
        try:
            iterations_str, salt_b64, hash_b64 = encoded.split("$")
            iterations = int(iterations_str)
            salt = base64.b64decode(salt_b64)
            expected = base64.b64decode(hash_b64)
        except Exception:
            return False

        digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, iterations)
        return secrets.compare_digest(digest, expected)
