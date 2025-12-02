# PostgreSQL 데이터베이스 연결 가이드

## 1. 환경변수 설정

프로젝트 루트 디렉토리(`recommenDA/senior-exercise-recommender-core/`)에 `.env` 파일을 생성하고 아래 내용을 추가하세요:

```env
DATABASE_URL=postgresql://postgres:비밀번호@localhost:5432/senior_exercise
```

### 설정 방법

1. **로컬 개발 환경**:
   ```env
   DATABASE_URL=postgresql://postgres:your_password@localhost:5432/senior_exercise
   ```
   - `your_password`: PostgreSQL 설치 시 설정한 postgres 사용자 비밀번호
   - `localhost`: 로컬에서 실행하는 경우
   - `5432`: PostgreSQL 기본 포트
   - `senior_exercise`: 데이터베이스 이름

2. **배포 환경** (나중에):
   ```env
   DATABASE_URL=postgresql://username:password@your-server.com:5432/senior_exercise
   ```

## 2. 필요한 패키지 설치

```bash
pip install -r requirements.txt
```

필요한 패키지:
- `psycopg2-binary`: PostgreSQL 연결
- `bcrypt`: 비밀번호 해시
- `python-dotenv`: 환경변수 로드

## 3. 데이터베이스 테이블 생성

psql에서 테이블을 생성했는지 확인하세요:

```sql
-- psql 접속
psql -U postgres

-- 데이터베이스 선택
\c senior_exercise

-- 테이블 확인
\d users
```

테이블이 없으면 `db/recreate_users_table.sql` 파일의 내용을 실행하세요.

## 4. 연결 테스트

Python에서 연결을 테스트할 수 있습니다:

```python
from db.database import test_connection

test_connection()
```

## 5. API 서버 실행

```bash
# 프로젝트 루트에서
cd recommenDA/senior-exercise-recommender-core
python -m service.api
```

또는 uvicorn으로:

```bash
uvicorn service.api:app --reload --host 0.0.0.0 --port 8000
```

## 6. API 엔드포인트

### 회원가입
```http
POST /api/auth/signup
Content-Type: application/json

{
  "email": "test@example.com",
  "password": "my_password",
  "name": "홍길동",
  "birth_date": "500101",
  "gender": "남성",
  "health_conditions": ["무릎 통증", "고혈압"],
  "exercise_goals": ["혈압 조절", "체중 감량"],
  "preferred_location": "실내",
  "phone": "010-1234-5678",
  "guardian_phone": "010-9876-5432",
  "address_road": "서울특별시 강남구 테헤란로 123",
  "latitude": 37.566535,
  "longitude": 126.977969
}
```

### 로그인
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "test@example.com",
  "password": "my_password"
}
```

## 7. 문제 해결

### 연결 오류
- PostgreSQL이 실행 중인지 확인: `pg_isready` 또는 서비스 확인
- 비밀번호가 올바른지 확인
- 방화벽 설정 확인 (로컬이면 보통 문제 없음)

### 테이블이 없다는 오류
- psql에서 `\d users`로 테이블 존재 확인
- 없으면 `db/recreate_users_table.sql` 실행

### 패키지 설치 오류
- `psycopg2-binary` 설치 시 문제가 있으면:
  ```bash
  pip install psycopg2-binary --upgrade
  ```

