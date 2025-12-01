# 시니어 운동 추천 API 문서

FastAPI 기반 REST API 서버입니다. Flutter 앱에서 사용할 수 있습니다.

## 실행 방법

```bash
cd senior-exercise-recommender-core
pip install -r requirements.txt
python service/api.py
```

또는 uvicorn으로 직접 실행:

```bash
uvicorn service.api:app --host 0.0.0.0 --port 8000 --reload
```

서버가 실행되면:
- API 서버: http://localhost:8000
- API 문서 (Swagger UI): http://localhost:8000/docs
- API 문서 (ReDoc): http://localhost:8000/redoc

## API 엔드포인트

### 1. 헬스 체크

**GET** `/api/health`

서버 상태 확인

**응답:**
```json
{
  "status": "healthy"
}
```

---

### 2. 운동 추천 (날씨 기반)

**POST** `/api/recommend`

사용자 프로필과 위치를 기반으로 날씨 정보를 조회하고 운동/시설을 추천합니다.

**요청 본문:**
```json
{
  "user_profile": {
    "age_group": "65-69",
    "health_issues": ["knee_pain"],
    "goals": ["flexibility", "strength"],
    "preference_env": "indoor"
  },
  "location": {
    "lat": 37.5665,
    "lon": 126.9780
  },
  "top_k": 5
}
```

**응답:**
```json
{
  "recommendations": [
    {
      "fac_id": "F001",
      "facility_name": "은평구민체육센터",
      "program_name": "실버 요가",
      "sport_category": "yoga",
      "distance_km": 1.2,
      "intensity_level": "low",
      "is_indoor": true,
      "reason": "무릎 통증을 고려하여 충격이 적은 운동을 우선으로 선택했습니다. 현재 날씨/대기질을 고려해 실내 시설을 우선 추천했습니다."
    }
  ],
  "weather_info": {
    "temp": 12.76,
    "rain_prob": 0.0,
    "pm10": 191.5,
    "is_daytime": false
  }
}
```

---

### 3. 사용자 생성

**POST** `/api/user`

새 사용자를 생성합니다.

**요청 본문:**
```json
{
  "nickname": "김영희",
  "age_group": "65-69",
  "health_issues": ["knee_pain"],
  "goals": ["flexibility"],
  "preference_env": "indoor",
  "home_lat": 37.5665,
  "home_lon": 126.9780
}
```

**응답:**
```json
{
  "id": 1,
  "nickname": "김영희",
  "age_group": "65-69",
  "health_issues": ["knee_pain"],
  "goals": ["flexibility"],
  "preference_env": "indoor",
  "home_lat": 37.5665,
  "home_lon": 126.9780
}
```

---

### 4. 사용자 정보 조회

**GET** `/api/user/{user_id}`

사용자 정보를 조회합니다.

**응답:**
```json
{
  "id": 1,
  "nickname": "김영희",
  "age_group": "65-69",
  "health_issues": ["knee_pain"],
  "goals": ["flexibility"],
  "preference_env": "indoor",
  "home_lat": 37.5665,
  "home_lon": 126.9780
}
```

---

### 5. 커뮤니티 세션 참여

**POST** `/api/community/join`

사용자가 그룹 운동 세션에 참여합니다.

**요청 본문:**
```json
{
  "user_id": 1,
  "fac_id": "F001",
  "program_name": "실버 요가",
  "session_date": "2024-01-15",
  "time_block": "오전",
  "fac_name": "은평구민체육센터",
  "max_participants": 4
}
```

**응답:**
```json
{
  "status": "joined",
  "current_participants": 2,
  "max_participants": 4,
  "session_filled": false,
  "session_id": 1,
  "message": null
}
```

**상태 코드:**
- `joined`: 성공적으로 참여
- `already_joined`: 이미 참여 중
- `error`: 오류 발생

---

### 6. 세션 참여자 목록 조회

**GET** `/api/community/session/{session_id}/participants`

세션에 참여한 사용자 목록을 조회합니다.

**응답:**
```json
{
  "participants": [
    {
      "id": 1,
      "nickname": "김영희"
    },
    {
      "id": 2,
      "nickname": "이철수"
    }
  ]
}
```

---

### 7. 함께 할 수 있는 운동 영상 추천

**POST** `/api/exercise-videos/group`

커뮤니티 운동이 성사되었을 때 함께 할 수 있는 운동 영상을 추천합니다.

**요청 본문:**
```json
{
  "user_profile": {
    "age_group": "65-69",
    "health_issues": [],
    "goals": ["flexibility"],
    "preference_env": "any"
  },
  "program_name": "실버 요가",
  "max_results": 3
}
```

**응답:**
```json
{
  "videos": [
    {
      "name": "줄 따라 걷기",
      "체력항목": "협응력",
      "운동도구": "줄",
      "신체부위": "전신",
      "혼자여부": "n",
      "url": "https://youtu.be/SdUIfqqUgdw",
      "info": "체력항목: 협응력 | 도구: 줄 | 부위: 전신"
    }
  ]
}
```

---

## CORS 설정

현재 모든 도메인에서 접근 가능하도록 설정되어 있습니다 (`allow_origins=["*"]`).
프로덕션 환경에서는 특정 도메인으로 제한하는 것을 권장합니다.

## 환경 변수

`.env` 파일에 다음 변수를 설정하세요:

```
OPENWEATHER_API_KEY=your_api_key_here
```

---

### 8. 날씨 기반 운동 알림

**POST** `/api/notification/exercise`

날씨가 위험할 때 실내 운동 영상을 추천하는 알림을 생성합니다.

**요청 본문:**
```json
{
  "user_id": "user_123",
  "lat": 37.5665,
  "lon": 126.9780,
  "has_chronic_disease": false,
  "air_quality_risky": false
}
```

**응답 (위험한 날씨):**
```json
{
  "has_notification": true,
  "message": "오늘은 비나 눈이 오는 날씨입니다. 밖에 나가지 말고 집 안에서 운동하는 것이 좋겠어요. https://youtu.be/... 이 운동(척추 스트레칭)을 하는 것을 추천드릴게요.",
  "exercise": {
    "name": "척추 스트레칭",
    "체력항목": "유연성",
    "운동도구": "폼롤러",
    "신체부위": "등/허리",
    "혼자여부": "y",
    "url": "https://youtu.be/...",
    "info": "체력항목: 유연성 | 도구: 폼롤러 | 부위: 등/허리"
  },
  "weather_info": {
    "status": "dangerous",
    "text": "비나 눈이 오는 날씨"
  }
}
```

**응답 (안전한 날씨):**
```json
{
  "has_notification": false,
  "message": null,
  "exercise": null,
  "weather_info": {
    "status": "safe",
    "text": "노인이 나들이하기에 비교적 안전한 날씨"
  }
}
```

**동작 방식:**
1. 기상청 API로 날씨 조회
2. 위험 평가 (비/눈, 강풍, 폭염, 한파 등)
3. 위험하면 운동 영상 추천 (신체부위 이력 관리 포함)
4. 알림 메시지 생성

**참고:**
- 이력은 `db/exercise_history.json`에 저장됩니다 (나중에 SQL로 전환 예정)
- 같은 날에는 같은 운동을 반환합니다
- 매일 다른 신체부위를 추천합니다

---

## 데이터베이스

SQLite 데이터베이스가 `db/db.sqlite3`에 자동으로 생성됩니다.
첫 실행 시 스키마가 자동으로 적용됩니다.

운동 추천 이력은 현재 `db/exercise_history.json`에 저장되며, 추후 SQL로 전환 예정입니다.

