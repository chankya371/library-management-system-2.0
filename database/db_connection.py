import sqlite3
import os
from contextlib import contextmanager
from typing import Generator

DB_FILENAME = "library_system.db"
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, DB_FILENAME)


def get_db_path() -> str:
    return DB_PATH


def set_db_path(path: str) -> None:
    global DB_PATH
    DB_PATH = path


def get_connection(db_path: str = None) -> sqlite3.Connection:
    """Creates a new SQLite connection with foreign keys enabled and row factory configured."""
    target_path = db_path or DB_PATH
    conn = sqlite3.connect(target_path, timeout=10.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


@contextmanager
def get_db_cursor(db_path: str = None, commit: bool = True) -> Generator[sqlite3.Cursor, None, None]:
    """Context manager for safe transactional database operations."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    try:
        yield cursor
        if commit:
            conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()
