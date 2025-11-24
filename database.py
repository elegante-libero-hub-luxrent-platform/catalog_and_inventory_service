import os
from contextlib import contextmanager
from typing import Any, Dict, Iterable, List, Optional

import mysql.connector
from mysql.connector import pooling


DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "catalog_db")

_pool: Optional[pooling.MySQLConnectionPool] = None


def _get_pool() -> pooling.MySQLConnectionPool:
    """
    Create a MySQL connection pool.
    Supports both Unix socket (Cloud Run with Cloud SQL) and TCP (local development).
    """
    global _pool
    if _pool is None:
        # Check if using Unix socket (Cloud Run with Cloud SQL)
        if DB_HOST and DB_HOST.startswith('/cloudsql/'):
            # Use Unix socket connection for Cloud Run
            _pool = pooling.MySQLConnectionPool(
                pool_name="catalog_pool",
                pool_size=5,
                unix_socket=DB_HOST,  # Use unix_socket parameter, not host
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME,
            )
        else:
            # Use TCP connection for local development
            _pool = pooling.MySQLConnectionPool(
                pool_name="catalog_pool",
                pool_size=5,
                host=DB_HOST,
                port=DB_PORT,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME,
            )
    return _pool


@contextmanager
def get_conn():
    pool = _get_pool()
    conn = pool.get_connection()
    try:
        yield conn
    finally:
        conn.close()


def query_all(sql: str, params: Optional[Iterable[Any]] = None) -> List[Dict[str, Any]]:
    with get_conn() as conn:
        cur = conn.cursor(dictionary=True)
        cur.execute(sql, params or [])
        rows = cur.fetchall()
        cur.close()
        return rows


def query_one(sql: str, params: Optional[Iterable[Any]] = None) -> Optional[Dict[str, Any]]:
    rows = query_all(sql, params)
    return rows[0] if rows else None


def execute(sql: str, params: Optional[Iterable[Any]] = None) -> int:
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(sql, params or [])
        conn.commit()
        rowcount = cur.rowcount
        cur.close()
        return rowcount
