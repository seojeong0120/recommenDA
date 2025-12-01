# db/user_repository.py
import json
from typing import Optional, Dict, Any
import sqlite3
from .database import get_db_connection


def create_user(
    nickname: str,
    age_group: str,
    health_issues: list[str],
    goals: list[str],
    preference_env: str = "any",
    home_lat: Optional[float] = None,
    home_lon: Optional[float] = None,
) -> int:
    """
    새 사용자 생성하고 user_id 반환.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO user (nickname, age_group, health_issues, goals, preference_env, home_lat, home_lon)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                nickname,
                age_group,
                json.dumps(health_issues, ensure_ascii=False),
                json.dumps(goals, ensure_ascii=False),
                preference_env,
                home_lat,
                home_lon,
            ),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def get_user(user_id: int) -> Optional[Dict[str, Any]]:
    """
    사용자 정보 조회.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        if row is None:
            return None
        
        return {
            "id": row["id"],
            "nickname": row["nickname"],
            "age_group": row["age_group"],
            "health_issues": json.loads(row["health_issues"] or "[]"),
            "goals": json.loads(row["goals"] or "[]"),
            "preference_env": row["preference_env"],
            "home_lat": row["home_lat"],
            "home_lon": row["home_lon"],
        }
    finally:
        conn.close()

