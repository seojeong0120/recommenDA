# service/community_client.py
from datetime import date
from typing import Dict, Any, Optional
import sqlite3
from db.database import get_db_connection


def join_session(
    user_id: int,
    fac_id: str,
    program_name: str,
    session_date: date,
    time_block: str,
    fac_name: str,
    max_participants: int = 4,
) -> Dict[str, Any]:
    """
    사용자가 그룹 세션에 참여.
    
    (6-1) group_session 테이블 조회
    (6-2) 없으면 새 row 생성
    (6-3) group_participant에 user_id 추가
    (6-4) group_session.current_participants += 1 업데이트
    (6-5) current_participants == max_participants 면 status = "filled"
    
    Returns:
        {
            "status": "joined",
            "current_participants": n,
            "max_participants": m,
            "session_filled": bool,
            "session_id": int
        }
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # (6-1) 같은 세션 찾기
        cursor.execute(
            """
            SELECT id, current_participants, max_participants, status
            FROM group_session
            WHERE fac_id = ? AND program_name = ? AND session_date = ? AND time_block = ?
            """,
            (fac_id, program_name, str(session_date), time_block),
        )
        session_row = cursor.fetchone()
        
        session_id: Optional[int] = None
        current_participants: int = 0
        session_status: str = "open"
        
        if session_row is None:
            # (6-2) 새 세션 생성
            cursor.execute(
                """
                INSERT INTO group_session 
                (fac_id, fac_name, program_name, session_date, time_block, max_participants, current_participants, status)
                VALUES (?, ?, ?, ?, ?, ?, 0, 'open')
                """,
                (fac_id, fac_name, program_name, str(session_date), time_block, max_participants),
            )
            session_id = cursor.lastrowid
            current_participants = 0
        else:
            session_id = session_row["id"]
            current_participants = session_row["current_participants"]
            session_status = session_row["status"]
            
            # 이미 가득 찬 경우
            if session_status == "filled":
                return {
                    "status": "error",
                    "message": "이 세션은 이미 정원이 찼습니다.",
                    "current_participants": current_participants,
                    "max_participants": session_row["max_participants"],
                    "session_filled": True,
                }
            
            # 이미 참여 중인 경우
            cursor.execute(
                "SELECT id FROM group_participant WHERE session_id = ? AND user_id = ?",
                (session_id, user_id),
            )
            if cursor.fetchone() is not None:
                return {
                    "status": "already_joined",
                    "message": "이미 이 세션에 참여 중입니다.",
                    "current_participants": current_participants,
                    "max_participants": session_row["max_participants"],
                    "session_filled": current_participants >= session_row["max_participants"],
                }
        
        # (6-3) group_participant에 추가
        try:
            cursor.execute(
                "INSERT INTO group_participant (session_id, user_id) VALUES (?, ?)",
                (session_id, user_id),
            )
        except sqlite3.IntegrityError:
            # 이미 참여 중이면 위에서 체크했지만, 동시성 이슈 대비
            conn.rollback()
            return {
                "status": "error",
                "message": "이미 참여 중인 세션입니다.",
            }
        
        # (6-4) current_participants 증가
        current_participants += 1
        cursor.execute(
            "UPDATE group_session SET current_participants = ? WHERE id = ?",
            (current_participants, session_id),
        )
        
        # (6-5) 가득 찬지 확인
        session_filled = current_participants >= max_participants
        if session_filled:
            cursor.execute(
                "UPDATE group_session SET status = 'filled' WHERE id = ?",
                (session_id,),
            )
        
        conn.commit()
        
        return {
            "status": "joined",
            "current_participants": current_participants,
            "max_participants": max_participants,
            "session_filled": session_filled,
            "session_id": session_id,
        }
        
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def get_session_participants(session_id: int) -> list[Dict[str, Any]]:
    """
    세션 참여자 목록 조회.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT u.id, u.nickname
            FROM group_participant gp
            JOIN user u ON gp.user_id = u.id
            WHERE gp.session_id = ?
            ORDER BY gp.joined_at
            """,
            (session_id,),
        )
        rows = cursor.fetchall()
        return [{"id": row["id"], "nickname": row["nickname"]} for row in rows]
    finally:
        conn.close()

