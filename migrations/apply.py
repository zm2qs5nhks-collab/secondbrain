"""
执行 migrations/ 下的 SQL 文件（幂等，可重复执行）。

用法（在项目根目录）：
    venv/bin/python migrations/apply.py 003_note_attachments.sql
    venv/bin/python migrations/apply.py migrations/003_note_attachments.sql
    venv/bin/python migrations/apply.py            # 不带参数 = 按文件名顺序全跑

参数解析规则：
- 绝对路径：原样使用；
- 带目录的相对路径：按当前工作目录解析；
- 只给文件名：先看当前目录，找不到就去 migrations/ 下找。

为什么不用 psql：服务器上不一定装了客户端，而 venv 里一定有 psycopg2，
而且连接参数直接复用 config.py，不会出现「psql 连的库和程序连的库不是同一个」。
"""

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
MIGRATIONS_DIR = ROOT / "migrations"

sys.path.insert(0, str(ROOT))


def resolve(arg: str) -> pathlib.Path:
    """把命令行参数解析成真实的 SQL 文件路径。"""
    p = pathlib.Path(arg)
    if p.is_absolute():
        return p
    if p.exists():
        return p
    # 只给了文件名（或路径写错目录）→ 到 migrations/ 下再找一次
    return MIGRATIONS_DIR / p.name


def main(argv: list[str]) -> int:
    if argv:
        files = [resolve(a) for a in argv]
    else:
        files = sorted(MIGRATIONS_DIR.glob("*.sql"))

    missing = [str(f) for f in files if not f.exists()]
    if missing:
        print(f"[x] 找不到文件：{missing}")
        print(f"    已查找：{MIGRATIONS_DIR}")
        return 1

    if not files:
        print(f"[x] {MIGRATIONS_DIR} 下没有 *.sql 文件")
        return 1

    from storage.db import get_conn  # 延迟导入：方便单测 resolve()

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            for f in files:
                print(f"[apply] {f.name}")
                cur.execute(f.read_text(encoding="utf-8"))
        conn.commit()
        print(f"[ok] 已执行 {len(files)} 个文件")
        return 0
    except Exception as exc:  # noqa: BLE001
        conn.rollback()
        print(f"[fail] {type(exc).__name__}: {exc}")
        return 1
    finally:
        conn.close()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
