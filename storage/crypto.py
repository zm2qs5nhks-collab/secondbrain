"""
加密工具 —— 用于 API Key 等敏感信息加密存储
"""

import os
import base64
from cryptography.fernet import Fernet

_KEY_FILE = os.path.join(os.path.dirname(__file__), "..", ".secret_key")
_fernet = None


def _load_or_create_key() -> bytes:
    global _fernet
    if _fernet is not None:
        return _fernet._signing_key if hasattr(_fernet, '_signing_key') else b""

    env_key = os.getenv("FERNET_KEY", "")
    if env_key:
        _fernet = Fernet(env_key.encode())
        return env_key.encode()

    if os.path.exists(_KEY_FILE):
        with open(_KEY_FILE, "r") as f:
            _fernet = Fernet(f.read().strip().encode())
            return _fernet._signing_key

    key = Fernet.generate_key().decode()
    with open(_KEY_FILE, "w") as f:
        f.write(key)
    os.chmod(_KEY_FILE, 0o600)
    _fernet = Fernet(key.encode())
    return key.encode()


def encrypt(plaintext: str) -> str:
    f = Fernet(_load_or_create_key())
    return "ENC:" + f.encrypt(plaintext.encode()).decode()


def decrypt(ciphertext: str) -> str:
    if not ciphertext.startswith("ENC:"):
        return ciphertext
    f = Fernet(_load_or_create_key())
    return f.decrypt(ciphertext[4:].encode()).decode()


def is_encrypted(value: str) -> bool:
    return isinstance(value, str) and value.startswith("ENC:")
