"""
PostgreSQL 数据库连接
"""

import psycopg2
import psycopg2.extras
import config

_conn = None


def _connect():
    return psycopg2.connect(
        host=config.DB_HOST,
        port=config.DB_PORT,
        dbname=config.DB_NAME,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        sslmode="disable",
    )


def get_conn():
    global _conn
    if _conn is None or _conn.closed:
        _conn = _connect()
        _conn.autocommit = False
    return _conn


def _reset():
    global _conn
    if _conn is not None:
        try:
            _conn.close()
        except Exception:
            pass
    _conn = None


def _run(sql, params, fetch, returning):
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        cur.execute(sql, params)
        if fetch:
            row = cur.fetchone() if returning else cur.fetchall()
            result = dict(row) if (returning and row) else ([dict(r) for r in row] if row else [])
        else:
            conn.commit()
            result = None
    except psycopg2.OperationalError:
        _reset()
        conn = get_conn()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql, params)
        if fetch:
            row = cur.fetchone() if returning else cur.fetchall()
            result = dict(row) if (returning and row) else ([dict(r) for r in row] if row else [])
        else:
            conn.commit()
            result = None
    finally:
        cur.close()
    return result


def query_one(sql: str, params=None) -> dict | None:
    return _run(sql, params, fetch=True, returning=True)


def query_all(sql: str, params=None) -> list[dict]:
    return _run(sql, params, fetch=True, returning=False)


def execute(sql: str, params=None):
    _run(sql, params, fetch=False, returning=False)


def execute_returning(sql: str, params=None) -> dict | None:
    return _run(sql, params, fetch=True, returning=True)
