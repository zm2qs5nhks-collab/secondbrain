"""
执行 migrations/ 下的 SQL 文件（幂等，可重复执行）。

用法（在项目根目录）：
    venv/bin/python migrations/apply.py 003_note_attachments.sql
    venv/bin/python migrations/apply.py          # 不带参数 = 按文件名顺序全跑

为什么不用 psql：服务器上不一定装了客户端，而 venv 里一定有 psycopg2，
而且连接参数直接复用 config.py，不会出现「psql 连的库和程序连的库不是同一个」。
"""

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from storage.db import get_conn  # noqa: E402


def main(argv: list[str]) -> int:
    if argv:
        files = [pathlib.Path(a) for a in argv]
    else:
        files = sorted((ROOT / "migrations").glob("*.sql"))

    files = [f for f in files if f.exists()]
    if not files:
        print("没有找到要执行的 SQL 文件")
        return 1

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
