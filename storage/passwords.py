"""
密码哈希 —— bcrypt，并兼容历史遗留的无盐 SHA-256。

设计要点：
1. 新密码一律 bcrypt（cost=12）；
2. 老库里 64 位十六进制的 sha256 仍可登录，登录成功后由调用方
   立刻用 hash_password() 重写，实现「无感迁移」；
3. bcrypt 只使用密码的前 72 字节，这里显式截断，避免不同 bcrypt
   版本（静默截断 / 直接报错）行为不一致；
4. bcrypt 未安装时不阻塞应用启动：老用户仍可登录，只有新建/升级
   密码时会抛出明确提示。
"""

import hashlib
import hmac
import re

try:
    import bcrypt
except ImportError:  # 依赖没装时应用仍能起来，只是不能新建 bcrypt 密码
    bcrypt = None

# 旧版实现：hashlib.sha256(pwd.encode()).hexdigest()，64 位小写十六进制
_SHA256_HEX = re.compile(r"^[0-9a-f]{64}$")
_BCRYPT_PREFIXES = ("$2a$", "$2b$", "$2y$")
_BCRYPT_ROUNDS = 12
_MAX_PASSWORD_BYTES = 72


def _to_bytes(password: str) -> bytes:
    return (password or "").encode("utf-8")[:_MAX_PASSWORD_BYTES]


def _require_bcrypt():
    if bcrypt is None:
        raise RuntimeError(
            "缺少 bcrypt 依赖，请先执行：venv/bin/pip install -r requirements.txt"
        )


def hash_password(password: str) -> str:
    """生成 bcrypt 哈希（新密码、以及登录时的自动升级都走这里）。"""
    _require_bcrypt()
    return bcrypt.hashpw(
        _to_bytes(password), bcrypt.gensalt(rounds=_BCRYPT_ROUNDS)
    ).decode("ascii")


def verify_password(password: str, stored: str | None) -> tuple[bool, bool]:
    """校验密码。

    返回 (是否正确, 是否建议升级哈希)。
    - 旧 sha256 校验通过 -> (True, True)，调用方应立刻重写为 bcrypt；
    - bcrypt 校验通过     -> (True, False)；
    - 失败 / 未知格式     -> (False, False)。
    """
    if not stored:
        return False, False

    stored = str(stored).strip()

    # ① 旧版无盐 sha256（迁移期兼容）
    if _SHA256_HEX.match(stored):
        legacy = hashlib.sha256((password or "").encode("utf-8")).hexdigest()
        ok = hmac.compare_digest(legacy, stored)
        return ok, ok

    # ② bcrypt
    if stored.startswith(_BCRYPT_PREFIXES):
        if bcrypt is None:
            return False, False
        try:
            return bcrypt.checkpw(_to_bytes(password), stored.encode("ascii")), False
        except (ValueError, TypeError):
            return False, False

    # ③ 其它未知格式：拒绝，避免把异常数据当成有效哈希
    return False, False


def is_legacy_hash(stored: str | None) -> bool:
    """用于数据体检：判断某个账号是否还停留在旧 sha256。"""
    return bool(stored) and bool(_SHA256_HEX.match(str(stored).strip()))
