"""
加密工具 —— 用于 API Key 等敏感信息加密存储
"""

import os
from cryptography.fernet import Fernet

_KEY_FILE = os.path.join(os.path.dirname(__file__), "..", ".secret_key")
_fernet = None


def _get_fernet():
    global _fernet
    if _fernet is not None:
        return _fernet

    env_key = os.getenv("FERNET_KEY", "")
    if env_key:
        _fernet = Fernet(env_key.encode())
        return _fernet

    if os.path.exists(_KEY_FILE):
        with open(_KEY_FILE, "r") as f:
            key = f.read().strip()
        try:
            _fernet = Fernet(key.encode())
            return _fernet
        except Exception:
            pass

    key = Fernet.generate_key().decode()
    with open(_KEY_FILE, "w") as f:
        f.write(key)
    os.chmod(_KEY_FILE, 0o600)
    _fernet = Fernet(key.encode())
    return _fernet


def encrypt(plaintext: str) -> str:
    return "ENC:" + _get_fernet().encrypt(plaintext.encode()).decode()


def decrypt(ciphertext: str) -> str:
    if not ciphertext.startswith("ENC:"):
        return ciphertext
    return _get_fernet().decrypt(ciphertext[4:].encode()).decode()


def is_encrypted(value: str) -> bool:
    return isinstance(value, str) and value.startswith("ENC:")
