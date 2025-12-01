# 기능 통합 요약

## 통합 완료 사항

### 1. 파일 경로 통일
- ✅ `exercise_recommender.py`: `data/processed/exercise_video.json` 사용하도록 수정
- ✅ 이력 저장: `db/exercise_history.json` (나중에 SQL로 전환 예정)

### 2. 중복 제거
- ✅ `exercise_video_client.py`: `exercise_recommender.py`의 `load_exercises()` 함수 재사용
- ✅ 역할 분리:
  - `exercise_recommender.py`: 개인 운동 추천 (이력 관리 포함)
  - `exercise_video_client.py`: 그룹 운동 영상 추천 (커뮤니티용)

### 3. 날씨 기능 분리
- ✅ `weather_client.py`: OpenWeatherMap API (기존 운동 추천용)
- ✅ `weather.py`: 기상청 API (알림 기능용)
- ✅ 두 기능은 서로 다른 용도이므로 충돌 없음

### 4. API 통합
- ✅ `/api/notification/exercise`: 날씨 기반 운동 알림 엔드포인트 추가
- ✅ 기존 엔드포인트와 충돌 없이 작동

## 현재 구조

### 운동 영상 관련
1. **`recommender/exercise_recommender.py`**
   - 운동 영상 로드 (`load_exercises`)
   - 신체부위 그룹화 (`group_exercises_by_body_part`)
   - 이력 관리 (`load_history`, `save_history`)
   - 개인 운동 추천 (`choose_exercise_for_today`)
   - **용도**: 날씨 위험 시 개인 운동 알림

2. **`service/exercise_video_client.py`**
   - 그룹 운동 필터링 (`filter_group_exercises`)
   - 그룹 운동 영상 추천 (`recommend_group_exercise_videos`)
   - **용도**: 커뮤니티 운동 성사 시 함께 할 운동 추천

### 날씨 관련
1. **`service/weather_client.py`**
   - OpenWeatherMap API 사용
   - 온도, 강수 확률, PM10 조회
   - **용도**: 기존 운동 추천 시스템 (시설 기반)

2. **`service/weather.py`**
   - 기상청 API 사용
   - 초단기실황, 단기예보 조회
   - 위험 평가 (`evaluate_weather_danger`)
   - **용도**: 날씨 위험 알림 시스템

### 알림 관련
1. **`service/exercise_notification.py`**
   - 날씨 위험 평가 후 알림 생성
   - 독립적으로 사용 가능
   - **용도**: 스크립트 실행 또는 API에서 호출

2. **`service/api.py`**
   - `/api/notification/exercise` 엔드포인트
   - `exercise_notification.py`의 로직을 API에 통합

## API 엔드포인트

### 기존 엔드포인트 (유지)
- `POST /api/recommend` - 시설 기반 운동 추천 (OpenWeatherMap 사용)
- `POST /api/exercise-videos/group` - 그룹 운동 영상 추천
- `POST /api/community/join` - 커뮤니티 세션 참여
- 기타 사용자 관리, 세션 관리 엔드포인트

### 새로 추가된 엔드포인트
- `POST /api/notification/exercise` - 날씨 기반 운동 알림 (기상청 API 사용)

## 데이터 흐름

### 1. 날씨 기반 운동 알림 흐름
```
[날씨 조회] (기상청 API)
    ↓
[위험 평가] (evaluate_weather_danger)
    ↓
위험하지 않음? → [알림 없음] → 종료
    ↓
위험함!
    ↓
[운동 영상 로드] (exercise_recommender.load_exercises)
    ↓
[이력 확인] (exercise_history.json)
    ↓
오늘 이미 추천함? → [같은 운동 반환]
    ↓
아니면
    ↓
[신체부위 그룹화] (group_exercises_by_body_part)
    ↓
[이전과 다른 부위 선택]
    ↓
[그 부위에서 랜덤 선택]
    ↓
[이력 저장] (exercise_history.json)
    ↓
[알림 메시지 생성] → 반환
```

### 2. 커뮤니티 운동 영상 추천 흐름
```
[커뮤니티 운동 성사]
    ↓
[그룹 운동 영상 필터링] (혼자여부 == "n")
    ↓
[사용자 프로필/프로그램 매칭]
    ↓
[점수 계산 및 정렬]
    ↓
[상위 N개 반환]
```

## 이력 저장

현재: `db/exercise_history.json`
```json
{
  "user_id": {
    "last_date": "2024-01-15",
    "last_body": "등/허리",
    "today_exercise": {...}
  }
}
```

추후 SQL 전환 시: `exercise_history` 테이블에 저장 예정

## 환경 변수

`.env` 파일에 필요한 키:
```
OPENWEATHER_API_KEY=your_openweather_api_key  # 기존 운동 추천용
KMA_SERVICE_KEY=your_kma_service_key          # 알림 기능용 (기상청 API)
```

## 충돌 없는 이유

1. **운동 영상 로드**: `exercise_recommender.py`가 메인, `exercise_video_client.py`가 재사용
2. **날씨 API**: 용도가 다름 (OpenWeatherMap vs 기상청)
3. **이력 관리**: 개인 운동 알림에만 사용, 그룹 운동 추천과 분리
4. **API 엔드포인트**: 각각 다른 경로로 분리

