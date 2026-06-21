"""MySQL 连接管理。从 .env 读取配置，提供连接和游标的上下文管理器。"""

import os
import pymysql
import pymysql.cursors
from contextlib import contextmanager
from dotenv import load_dotenv

load_dotenv()


def _get_config() -> dict:
    return {
        "host":    os.getenv("MYSQL_HOST", "127.0.0.1"),
        "port":    int(os.getenv("MYSQL_PORT", 3306)),
        "user":    os.getenv("MYSQL_USER", "root"),
        "password": os.getenv("MYSQL_PASSWORD", ""),
        "database": os.getenv("MYSQL_DATABASE", "career_guides_au"),
        "charset":  os.getenv("MYSQL_CHARSET", "utf8mb4"),
        "cursorclass": pymysql.cursors.DictCursor,
        "autocommit": False,
    }


def get_connection() -> pymysql.connections.Connection:
    """返回一个新的数据库连接，调用方负责关闭。"""
    return pymysql.connect(**_get_config())


@contextmanager
def get_cursor():
    """
    上下文管理器，自动提交或回滚，自动关闭连接。

    用法：
        with get_cursor() as cursor:
            cursor.execute(...)
    """
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            yield cursor
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
