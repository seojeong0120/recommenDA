# API 서버 실행 가이드

## 빠른 시작

### 1. 패키지 설치

```bash
cd senior-exercise-recommender-core
pip install -r requirements.txt
```

### 2. 서버 실행

**방법 1: Python으로 직접 실행**
```bash
python service/api.py
```

**방법 2: uvicorn으로 실행 (권장)**
```bash
uvicorn service.api:app --host 0.0.0.0 --port 8000 --reload
```

`--reload` 옵션은 코드 변경 시 자동으로 재시작합니다.

### 3. 서버 접속

서버가 실행되면 다음 URL로 접속할 수 있습니다:

- **API 서버**: http://localhost:8000
- **API 문서 (Swagger UI)**: http://localhost:8000/docs
- **API 문서 (ReDoc)**: http://localhost:8000/redoc
- **헬스 체크**: http://localhost:8000/api/health

## API 테스트

### curl로 테스트

```bash
# 헬스 체크
curl http://localhost:8000/api/health

# 운동 추천
curl -X POST http://localhost:8000/api/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "user_profile": {
      "age_group": "65-69",
      "health_issues": ["knee_pain"],
      "goals": ["flexibility"],
      "preference_env": "indoor"
    },
    "location": {
      "lat": 37.5665,
      "lon": 126.9780
    },
    "top_k": 5
  }'
```

### Python 스크립트로 테스트

```bash
python scripts/test_api.py
```

## 환경 변수 설정

`.env` 파일에 OpenWeatherMap API 키를 설정하세요:

```
OPENWEATHER_API_KEY=your_api_key_here
```

## 문제 해결

### 서버가 시작되지 않는 경우

1. 포트 8000이 이미 사용 중인지 확인:
```bash
lsof -i :8000
```

2. 다른 포트로 실행:
```bash
uvicorn service.api:app --host 0.0.0.0 --port 8001
```

### 500 오류가 발생하는 경우

1. 서버 로그를 확인하여 오류 메시지 확인
2. 데이터베이스 파일이 있는지 확인: `db/db.sqlite3`
3. `.env` 파일이 올바르게 설정되어 있는지 확인

## Flutter 앱 연동

Flutter 앱에서 API를 호출할 때:

1. **기본 URL**: `http://your-server-ip:8000`
2. **CORS**: 현재 모든 도메인에서 접근 가능하도록 설정되어 있습니다
3. **요청 헤더**: `Content-Type: application/json`

예시:
```dart
final response = await http.post(
  Uri.parse('http://your-server:8000/api/recommend'),
  headers: {'Content-Type': 'application/json'},
  body: jsonEncode({
    'user_profile': {...},
    'location': {...},
  }),
);
```

