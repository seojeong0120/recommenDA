"""
PostgreSQL 사용자(회원) 데이터베이스 레포지토리
회원가입, 로그인, 조회 기능 제공
"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv
import bcrypt

load_dotenv()


class UserRepository:
    """사용자 데이터베이스 레포지토리"""

    def __init__(self, database_url: Optional[str] = None):
        """
        Args:
            database_url: PostgreSQL 연결 URL
                예: postgresql://postgres:password@localhost:5432/senior_exercise
                환경변수 DATABASE_URL이 있으면 자동으로 사용
        """
        self.database_url = database_url or os.getenv("DATABASE_URL")
        if not self.database_url:
            raise ValueError(
                "DATABASE_URL 환경변수를 설정하거나 database_url 파라미터를 제공해주세요.\n"
                "예: postgresql://postgres:password@localhost:5432/senior_exercise"
            )

    def _get_connection(self):
        """데이터베이스 연결 생성"""
        return psycopg2.connect(self.database_url)

    def create_user(
        self,
        password: str,
        name: str,
        birth_date: str,
        gender: str,
        health_conditions: List[str],
        exercise_goals: List[str],
        preferred_location: str,
        phone: str,
        guardian_phone: str,
        address_road: str,
        latitude: float,
        longitude: float,
    ) -> Dict[str, Any]:
        """
        회원가입 - 새 사용자 생성

        Args:
            password: 비밀번호 (평문, 내부에서 해시 처리)
            name: 이름
            birth_date: 생년월일 6자리 (YYMMDD)
            gender: 성별
            health_conditions: 건강 상태 리스트
            exercise_goals: 운동 목적 리스트
            preferred_location: 선호 장소 ('실내', '실외', '둘 다')
            phone: 전화번호 (로그인 ID로 사용)
            guardian_phone: 보호자 전화번호
            address_road: 집주소 (도로명)
            latitude: 위도
            longitude: 경도

        Returns:
            생성된 사용자 정보 (dict)
        """
        # 비밀번호 해시 생성
        password_hash = bcrypt.hashpw(
            password.encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')

        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    INSERT INTO users (
                        password_hash, name, birth_date, gender,
                        health_conditions, exercise_goals, preferred_location,
                        phone, guardian_phone, address_road, latitude, longitude
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                    RETURNING *
                    """,
                    (
                        password_hash, name, birth_date, gender,
                        health_conditions, exercise_goals, preferred_location,
                        phone, guardian_phone, address_road, latitude, longitude
                    )
                )
                result = cur.fetchone()
                conn.commit()
                return dict(result)

    def get_user_by_phone(self, phone: str) -> Optional[Dict[str, Any]]:
        """
        전화번호로 사용자 조회 (로그인용)

        Args:
            phone: 전화번호

        Returns:
            사용자 정보 (dict) 또는 None
        """
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT * FROM users WHERE phone = %s",
                    (phone,)
                )
                result = cur.fetchone()
                return dict(result) if result else None


    def verify_password(self, password: str, password_hash: str) -> bool:
        """
        비밀번호 검증

        Args:
            password: 입력한 비밀번호 (평문)
            password_hash: DB에 저장된 해시

        Returns:
            비밀번호가 맞으면 True
        """
        return bcrypt.checkpw(
            password.encode('utf-8'),
            password_hash.encode('utf-8')
        )

    def login(self, phone: str, password: str) -> Optional[Dict[str, Any]]:
        """
        로그인 (전화번호 + 비밀번호)

        Args:
            phone: 전화번호
            password: 비밀번호 (평문)

        Returns:
            로그인 성공 시 사용자 정보 (dict), 실패 시 None
        """
        user = self.get_user_by_phone(phone)
        if not user:
            return None

        if self.verify_password(password, user['password_hash']):
            # 비밀번호 해시는 반환하지 않음
            user.pop('password_hash', None)
            # email도 반환하지 않음 (로그인 시 불필요)
            user.pop('email', None)
            return user

        return None

    def get_users_by_health_condition(
        self, condition: str
    ) -> List[Dict[str, Any]]:
        """
        특정 건강 상태를 가진 사용자들 조회

        Args:
            condition: 건강 상태 (예: '무릎 통증')

        Returns:
            사용자 정보 리스트
        """
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT * FROM users WHERE %s = ANY(health_conditions)",
                    (condition,)
                )
                results = cur.fetchall()
                return [dict(row) for row in results]

    def get_users_by_exercise_goal(
        self, goal: str
    ) -> List[Dict[str, Any]]:
        """
        특정 운동 목적을 가진 사용자들 조회

        Args:
            goal: 운동 목적 (예: '혈압 조절')

        Returns:
            사용자 정보 리스트
        """
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT * FROM users WHERE %s = ANY(exercise_goals)",
                    (goal,)
                )
                results = cur.fetchall()
                return [dict(row) for row in results]


# 사용 예시
if __name__ == "__main__":
    # 환경변수에서 DATABASE_URL 읽기
    # .env 파일에 다음과 같이 설정:
    # DATABASE_URL=postgresql://postgres:password@localhost:5432/senior_exercise

    repo = UserRepository()

    # 회원가입 예시
    user = repo.create_user(
        password="my_password_123",
        name="홍길동",
        birth_date="500101",
        gender="남성",
        health_conditions=["무릎 통증", "고혈압"],
        exercise_goals=["혈압 조절", "체중 감량"],
        preferred_location="실내",
        phone="010-1234-5678",
        guardian_phone="010-9876-5432",
        address_road="서울특별시 강남구 테헤란로 123",
        latitude=37.566535,
        longitude=126.977969
    )
    print("회원가입 성공:", user)

    # 로그인 예시 (전화번호 사용)
    logged_in_user = repo.login("010-1234-5678", "my_password_123")
    if logged_in_user:
        print("로그인 성공:", logged_in_user)
    else:
        print("로그인 실패")
