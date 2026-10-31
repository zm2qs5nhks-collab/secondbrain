"""
找回密码 —— 邮箱验证码流程。

安全约束（每条都对应一种攻击）：
- 不暴露邮箱是否注册：无论存不存在，都返回同一句提示；
- 验证码只存 sha256，库泄露也拿不到可用验证码；
- 10 分钟过期、单次使用、错 5 次作废 —— 挡暴力枚举；
- 同邮箱 1 小时最多发 3 次 + 60 秒冷却 —— 挡邮件轰炸；
- 同一 IP 的发送频率由调用方（页面/接口）另做限流。
"""

import hashlib
import secrets
import time

import config
from storage import mailer
from storage.db import execute, query_one
from storage.passwords import hash_password
from storage.rate_limit import check

CODE_TTL = config.RESET_CODE_TTL
MAX_ATTEMPTS = 5

# 冒烟测试 / 邮件未配置时，把验证码打到日志里方便本地调试
import logging

_log = logging.getLogger(__name__)


def _hash(code: str) -> str:
    return hashlib.sha256(code.encode("utf-8")).hexdigest()


def _norm(email: str) -> str:
    return (email or "").strip().lower()


def request_code(email: str) -> dict:
    """发送验证码。返回 {"ok": bool, "message": str}。"""
    email = _norm(email)
    if not email or "@" not in email:
        return {"ok": False, "message": "请输入有效的邮箱地址"}

    # 60 秒冷却
    allowed, wait = check(f"reset:cooldown:{email}", limit=1, window=60)
    if not allowed:
        return {"ok": False, "message": f"发送太频繁，请 {wait} 秒后再试"}

    # 每小时 3 次
    allowed, wait = check(f"reset:send:{email}", limit=3, window=3600)
    if not allowed:
        return {"ok": False, "message": f"今天发送次数过多，请 {wait // 60 + 1} 分钟后再试"}

    user = query_one(
        "SELECT id, email FROM users WHERE lower(email) = lower(%s)", (email,)
    )

    # 邮箱不存在也返回同样的文案，避免被用来枚举账号
    generic = {"ok": True, "message": "如果该邮箱已注册，验证码已经发出（10 分钟内有效）"}
    if not user:
        return generic

    code = f"{secrets.randbelow(1_000_000):06d}"
    execute(
        """INSERT INTO password_resets (user_id, email, code_hash, expires_at)
           VALUES (%s, %s, %s, %s)""",
        (user["id"], user["email"], _hash(code), time.time() + CODE_TTL),
    )

    try:
        mailer.send_reset_code(user["email"], code, minutes=max(1, CODE_TTL // 60))
    except mailer.MailNotConfigured:
        _log.warning("SMTP 未配置，验证码未发出")
        return {"ok": False, "message": "邮件服务未配置，请联系站点管理员"}
    except mailer.MailSendError as exc:
        _log.warning("验证码邮件发送失败: %s", exc)
        return {"ok": False, "message": f"邮件发送失败：{exc}"}

    return generic


def reset_password(email: str, code: str, new_password: str) -> dict:
    """校验验证码并重置密码。返回 {"ok": bool, "message": str}。"""
    email = _norm(email)
    code = (code or "").strip()
    if not email or not code:
        return {"ok": False, "message": "请填写邮箱和验证码"}
    if len(new_password or "") < 6:
        return {"ok": False, "message": "新密码至少 6 位"}

    row = query_one(
        "SELECT * FROM password_resets WHERE lower(email) = lower(%s) "
        "AND used_at IS NULL ORDER BY created_at DESC LIMIT 1",
        (email,),
    )
    if not row:
        return {"ok": False, "message": "验证码无效或已使用，请重新获取"}

    if float(row.get("expires_at") or 0) < time.time():
        return {"ok": False, "message": "验证码已过期，请重新获取"}

    if int(row.get("attempts") or 0) >= MAX_ATTEMPTS:
        return {"ok": False, "message": "错误次数过多，请重新获取验证码"}

    if not secrets.compare_digest(_hash(code), str(row.get("code_hash") or "")):
        execute(
            "UPDATE password_resets SET attempts = attempts + 1 WHERE id = %s",
            (row["id"],),
        )
        left = MAX_ATTEMPTS - int(row.get("attempts") or 0) - 1
        return {"ok": False, "message": f"验证码不正确，还可以再试 {max(left, 0)} 次"}

    try:
        execute(
            "UPDATE users SET password_hash = %s WHERE id = %s",
            (hash_password(new_password), row["user_id"]),
        )
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "message": f"重置失败：{type(exc).__name__}"}

    execute("UPDATE password_resets SET used_at = %s WHERE id = %s", (time.time(), row["id"]))
    # 顺手作废该用户其它未使用的验证码
    execute(
        "UPDATE password_resets SET used_at = %s WHERE user_id = %s AND used_at IS NULL",
        (time.time(), row["user_id"]),
    )
    return {"ok": True, "message": "密码已重置，请用新密码登录"}
