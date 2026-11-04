"""
手动管理账号 —— 关闭公开注册后，给熟人开号用。

为什么做成命令行而不是网页：
- 网页上的"用户管理"页需要额外的权限判断，一旦判错就是提权漏洞；
- 命令行只有能 SSH 登录服务器的人才能用，天然安全；
- 没有新增任何 HTTP 入口，攻击面为零。

用法（在项目根目录）：
    venv/bin/python tools/create_user.py --list
    venv/bin/python tools/create_user.py new  someone@example.com
    venv/bin/python tools/create_user.py new  someone@example.com --password 自定义密码
    venv/bin/python tools/create_user.py reset someone@example.com
    venv/bin/python tools/create_user.py disable someone@example.com

不传 --password 时会交互式输入（不回显），避免密码留在 shell 历史里。
"""

import argparse
import getpass
import pathlib
import secrets
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from storage.db import execute, query_all, query_one  # noqa: E402
from storage.passwords import hash_password  # noqa: E402

MIN_LEN = 8


def _norm(email: str) -> str:
    return (email or "").strip().lower()


def _ask_password() -> str:
    while True:
        pwd = getpass.getpass("设置密码（至少 8 位，输入不显示）: ")
        if len(pwd) < MIN_LEN:
            print(f"  密码太短，至少 {MIN_LEN} 位")
            continue
        if pwd != getpass.getpass("再输一次: "):
            print("  两次不一致，重来")
            continue
        return pwd


def _gen_password() -> str:
    alphabet = "abcdefghijkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    return "".join(secrets.choice(alphabet) for _ in range(12))


def cmd_list(_args) -> int:
    rows = query_all("SELECT email, created_at FROM users ORDER BY created_at DESC")
    if not rows:
        print("还没有任何账号")
        return 0
    print(f"共 {len(rows)} 个账号：")
    for r in rows:
        print(f"  {r['email']}")
    return 0


def cmd_new(args) -> int:
    email = _norm(args.email)
    if "@" not in email:
        print("[x] 邮箱格式不对")
        return 1
    if query_one("SELECT id FROM users WHERE lower(email) = lower(%s)", (email,)):
        print(f"[x] {email} 已存在")
        return 1

    pwd = args.password or _ask_password()
    if len(pwd) < MIN_LEN:
        print(f"[x] 密码至少 {MIN_LEN} 位")
        return 1

    execute(
        "INSERT INTO users (email, password_hash) VALUES (%s, %s)",
        (email, hash_password(pwd)),
    )
    print(f"[ok] 已创建：{email}")
    if not args.password:
        print("     密码就是你刚才输入的那个，直接发给对方即可")
    return 0


def cmd_reset(args) -> int:
    email = _norm(args.email)
    row = query_one("SELECT id FROM users WHERE lower(email) = lower(%s)", (email,))
    if not row:
        print(f"[x] 没有这个账号：{email}")
        return 1

    pwd = args.password or _ask_password()
    if len(pwd) < MIN_LEN:
        print(f"[x] 密码至少 {MIN_LEN} 位")
        return 1

    execute("UPDATE users SET password_hash = %s WHERE id = %s", (hash_password(pwd), row["id"]))
    print(f"[ok] 已重置：{email}")
    return 0


def cmd_random(args) -> int:
    """生成一个随机密码并创建账号，适合批量发给熟人。"""
    email = _norm(args.email)
    if query_one("SELECT id FROM users WHERE lower(email) = lower(%s)", (email,)):
        print(f"[x] {email} 已存在")
        return 1
    pwd = _gen_password()
    execute(
        "INSERT INTO users (email, password_hash) VALUES (%s, %s)",
        (email, hash_password(pwd)),
    )
    print(f"[ok] 已创建：{email}")
    print(f"     初始密码：{pwd}")
    print("     让对方登录后自行改密码（忘记密码走邮箱验证码）")
    return 0


def main(argv) -> int:
    parser = argparse.ArgumentParser(description="手动管理第二大脑的账号")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_list = sub.add_parser("list", help="列出所有账号")
    p_list.set_defaults(func=cmd_list)

    p_new = sub.add_parser("new", help="新建账号（交互式设密码）")
    p_new.add_argument("email")
    p_new.add_argument("--password", help="直接在命令里给密码（会留在 shell 历史，不推荐）")
    p_new.set_defaults(func=cmd_new)

    p_rand = sub.add_parser("random", help="新建账号并生成随机密码")
    p_rand.add_argument("email")
    p_rand.set_defaults(func=cmd_random)

    p_reset = sub.add_parser("reset", help="重置某个账号的密码")
    p_reset.add_argument("email")
    p_reset.add_argument("--password")
    p_reset.set_defaults(func=cmd_reset)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
