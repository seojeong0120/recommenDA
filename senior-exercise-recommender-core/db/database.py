# db/database.py
import os
import sqlite3
from pathlib import Path
from typing import Optional

DB_DIR = Path(__file__).resolve().parent
DB_PATH = DB_DIR / "db.sqlite3"
SCHEMA_PATH = DB_DIR / "schema.sql"


def get_db_connection() -> sqlite3.Connection:
    """
    SQLite 데이터베이스 연결 반환.
    없으면 생성하고 스키마 적용.
    """
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row  # 딕셔너리처럼 접근 가능
    return conn


def init_database():
    """
    데이터베이스가 없으면 생성하고 스키마를 적용.
    """
    if not DB_PATH.exists():
        conn = get_db_connection()
        try:
            # 여러 인코딩 시도 (UTF-8, CP949, EUC-KR)
            encodings = ['utf-8', 'cp949', 'euc-kr', 'latin-1']
            schema_sql = None
            for encoding in encodings:
                try:
                    with open(SCHEMA_PATH, "r", encoding=encoding) as f:
                        schema_sql = f.read()
                    break
                except UnicodeDecodeError:
                    continue
            if schema_sql is None:
                raise ValueError(f"schema.sql 파일을 읽을 수 없습니다. 지원되는 인코딩을 시도했지만 실패했습니다.")
            conn.executescript(schema_sql)
            conn.commit()
        finally:
            conn.close()


def reset_database():
    """
    개발/테스트용: 데이터베이스 초기화.
    """
    if DB_PATH.exists():
        DB_PATH.unlink()
    init_database()

