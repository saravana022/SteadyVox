"""Security & Field-Level Encryption at Rest for SteadyVox.

Protects sensitive patient identifying information (PII) at rest using AES-128-CBC
via symmetric Fernet tokens derived from SECRET_KEY.

RESEARCH SCREENING TOOL ONLY — NOT A MEDICAL DIAGNOSIS.
"""

import base64
import hashlib
from typing import Optional
from cryptography.fernet import Fernet
from backend.app.core.config import settings


def _get_fernet() -> Fernet:
    """Derives a deterministic 32-byte URL-safe base64 key from settings.SECRET_KEY."""
    raw_key = hashlib.sha256(settings.SECRET_KEY.encode("utf-8")).digest()
    url_safe_key = base64.urlsafe_b64encode(raw_key)
    return Fernet(url_safe_key)


def encrypt_field(value: Optional[str]) -> Optional[str]:
    """Encrypts plaintext string using Fernet token. Returns None if value is None."""
    if not value:
        return None
    f = _get_fernet()
    return f.encrypt(value.encode("utf-8")).decode("utf-8")


def decrypt_field(token: Optional[str]) -> Optional[str]:
    """Decrypts Fernet ciphertext token. Returns None or original if invalid."""
    if not token:
        return None
    try:
        f = _get_fernet()
        return f.decrypt(token.encode("utf-8")).decode("utf-8")
    except Exception:
        # Fallback to returning token if it was unencrypted/plain
        return token
