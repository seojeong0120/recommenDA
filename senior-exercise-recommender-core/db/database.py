import os
import psycopg2
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

def get_db_connection():
    # 1순위: DATABASE_URL 환경변수가 있으면 그걸 사용
    database_url = os.getenv("DATABASE_URL")
    
    # 2순위: 없으면 개별 변수 사용 (기존 방식 호환)
    db_host = os.getenv("DB_HOST", "localhost")
    db_name = os.getenv("DB_NAME", "postgres")
    db_user = os.getenv("DB_USER", "postgres")
    db_password = os.getenv("DB_PASSWORD")  # 기본값 제거: 환경 변수 필수
    db_port = os.getenv("DB_PORT", "5432")
    
    # DATABASE_URL이 없을 때는 개별 변수 방식 사용
    # 이 경우 DB_PASSWORD가 필수 (보안상 기본값 사용 안 함)
    if not database_url and not db_password:
        raise ValueError(
            "DATABASE_URL 또는 DB_PASSWORD 환경 변수가 필요합니다.\n"
            "배포 환경에서는 DATABASE_URL이 자동으로 설정됩니다.\n"
            "로컬 개발 환경에서는 .env 파일에 DATABASE_URL 또는 DB_PASSWORD를 설정하세요."
        )

    conn = None
    try:
        if database_url:
            # URL 방식 접속
            conn = psycopg2.connect(
                database_url,
                # 한글 데이터 깨짐 방지
                options="-c client_encoding=utf8"
            )
        else:
            # 개별 변수 방식 접속
            conn = psycopg2.connect(
                host=db_host,
                database=db_name,
                user=db_user,
                password=db_password,
                port=db_port,
                options="-c client_encoding=utf8"
            )
        return conn
        
    except Exception as e:
        # 윈도우 한글 에러 메시지 깨짐 방지 처리
        print("🚨 DB 연결 실패!")
        try:
            # 에러 메시지를 CP949(한글 윈도우)로 디코딩 시도하거나 그냥 출력
            print(f"에러 내용: {e}")
        except:
            print("에러 메시지 자체가 인코딩 문제로 깨졌습니다. 접속 정보를 확인하세요.")
            print(f"사용된 접속 정보(URL): {database_url if database_url else '개별 변수 사용'}")
        raise e

def init_database():
    """데이터베이스 테이블 초기화 (테이블이 없으면 생성)"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # 1. users 테이블 생성
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                phone VARCHAR(20) UNIQUE NOT NULL, 
                password_hash VARCHAR(255) NOT NULL,
                name VARCHAR(50) NOT NULL,
                birth_date VARCHAR(8),
                gender VARCHAR(10),
                health_conditions TEXT[], 
                exercise_goals TEXT[],    
                preferred_location VARCHAR(20),
                guardian_phone VARCHAR(20),
                address_road VARCHAR(255),
                latitude DOUBLE PRECISION,
                longitude DOUBLE PRECISION,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # 2. facilities 테이블 생성
        cur.execute("""
            CREATE TABLE IF NOT EXISTS facilities (
                id SERIAL PRIMARY KEY,
                fac_id VARCHAR(50) UNIQUE,
                facility_name VARCHAR(100),
                program_name VARCHAR(100),
                sport_category VARCHAR(50),
                address VARCHAR(255),
                latitude DOUBLE PRECISION,
                longitude DOUBLE PRECISION,
                is_indoor BOOLEAN
            );
        """)
        
        conn.commit()
        cur.close()
        conn.close()
        print("✅ PostgreSQL 테이블 초기화 완료")
        
    except Exception as e:
        print("❌ 테이블 생성 실패")
        try:
            print(f"에러: {e}")
        except:
            print("(에러 메시지 인코딩 오류)")