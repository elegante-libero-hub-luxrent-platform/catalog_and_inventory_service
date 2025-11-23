import os
import mysql.connector
from mysql.connector import pooling
from dotenv import load_dotenv

load_dotenv()

DATABASE_CONFIG = {
    "host": os.getenv("DB_HOST", "127.0.0.1"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "catalog"),
}

pool = pooling.MySQLConnectionPool(
    pool_name="catalog_pool",
    pool_size=5,
    pool_reset_session=True,
    **DATABASE_CONFIG
)


def get_conn():
    return pool.get_connection()
