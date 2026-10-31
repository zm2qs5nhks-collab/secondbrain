"""
邮件发送（SMTP）—— 目前只用于「找回密码」验证码。

设计原则：
- 未配置 SMTP 时，抛 MailNotConfigured，由调用方转成一句用户能看懂的提示，
  不要让整个页面崩掉；
- 发送失败抛 MailSendError，带上原始异常类型，方便排查是认证失败还是网络不通；
- 只发纯文本，不放任何账号信息（避免被转发后泄露）。

QQ 邮箱：smtp.qq.com:465（SSL），SMTP_PASS 填「授权码」而不是登录密码。
"""

import smtplib
import ssl
from email.message import EmailMessage
from email.utils import formataddr

import config


class MailNotConfigured(RuntimeError):
    """没有配置 SMTP。"""


class MailSendError(RuntimeError):
    """配置了但发送失败（认证错、网络不通、被限流等）。"""


def is_configured() -> bool:
    return bool(config.SMTP_HOST and config.SMTP_USER and config.SMTP_PASS)


def send_mail(to_email: str, subject: str, body: str) -> None:
    if not is_configured():
        raise MailNotConfigured("邮件服务未配置（SMTP_HOST / SMTP_USER / SMTP_PASS）")

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = formataddr(("第二大脑", config.SMTP_FROM or config.SMTP_USER))
    msg["To"] = to_email
    msg.set_content(body)

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(
            config.SMTP_HOST, config.SMTP_PORT, context=context, timeout=15
        ) as smtp:
            smtp.login(config.SMTP_USER, config.SMTP_PASS)
            smtp.send_message(msg)
    except Exception as exc:  # noqa: BLE001
        raise MailSendError(f"{type(exc).__name__}: {exc}") from exc


def send_reset_code(to_email: str, code: str, minutes: int = 10) -> None:
    body = (
        "你好，\n\n"
        "你正在重置「第二大脑」的登录密码，验证码是：\n\n"
        f"    {code}\n\n"
        f"{minutes} 分钟内有效，且只能使用一次。\n"
        "如果这不是你本人的操作，请忽略这封邮件，密码不会被修改。\n"
    )
    send_mail(to_email, "【第二大脑】重置密码验证码", body)
