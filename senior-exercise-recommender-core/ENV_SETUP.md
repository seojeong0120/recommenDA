# 환경 변수 설정 가이드

## .env 파일 생성

프로젝트 루트에 `.env` 파일을 생성하고 다음 내용을 입력하세요:

```bash
# OpenWeatherMap API 키 (기존 운동 추천용)
OPENWEATHER_API_KEY=여기에_OpenWeatherMap_API_키_입력

# 기상청 API 키 (알림 기능용)
KMA_SERVICE_KEY=여기에_기상청_API_키_입력
```

## API 키 발급 방법

### 1. OpenWeatherMap API 키

**용도**: 기존 운동 추천 시스템 (`/api/recommend`)

1. **회원가입**: https://openweathermap.org/api
2. **API 키 생성**:
   - 로그인 → "API keys" 메뉴
   - "Create key" 클릭
   - 이름 입력 후 생성
3. **API 키 복사**: 생성된 키를 `.env` 파일에 입력

**무료 플랜 제한:**
- 분당 60회 호출
- 일일 1,000,000회 호출

**참고**: API 키가 없어도 서비스는 작동하지만 기본값(온도 20도, 비 확률 0%, PM10 50)을 사용합니다.

---

### 2. 기상청 API 키 (공공데이터포털)

**용도**: 날씨 위험 알림 기능 (`/api/notification/exercise`)

1. **회원가입**: https://www.data.go.kr/
2. **서비스 신청**:
   - 검색: "기상청_단기예보" 또는 "기상청_초단기실황"
   - 원하는 서비스 선택
   - "활용신청" 클릭
   - 신청 정보 입력 (개인/기관 선택)
3. **승인 대기**: 보통 즉시 또는 몇 시간 내 승인
4. **API 키 확인**:
   - "마이페이지" → "활용신청 현황"
   - 승인된 서비스의 "인증키" 확인
5. **API 키 복사**: 인증키를 `.env` 파일에 입력

**필요한 서비스:**
- 초단기실황조회 (getUltraSrtNcst)
- 단기예보 (getVilageFcst)

**참고**: 기상청 API 키가 없으면 알림 기능이 작동하지 않습니다.

---

## .env 파일 예시

```bash
# OpenWeatherMap API 키
OPENWEATHER_API_KEY=27fa9aceb5e62efad83670a032666c3e

# 기상청 API 키 (공공데이터포털)
KMA_SERVICE_KEY=abcd1234efgh5678ijkl9012mnop3456qrst7890uvwx%3D%3D
```

**주의사항:**
- 따옴표 없이 입력
- 공백 없이 입력
- `=` 앞뒤 공백 없이 입력

## 확인 방법

서버 실행 후 다음 명령어로 확인:

```bash
# OpenWeatherMap API 테스트
curl http://localhost:8000/api/recommend -X POST -H "Content-Type: application/json" -d '{"user_profile": {...}, "location": {...}}'

# 기상청 API 테스트 (알림 기능)
curl http://localhost:8000/api/notification/exercise -X POST -H "Content-Type: application/json" -d '{"user_id": "test"}'
```

## 문제 해결

### API 키가 작동하지 않는 경우

1. **.env 파일 위치 확인**: 프로젝트 루트에 있어야 합니다
2. **파일 형식 확인**: UTF-8 인코딩, 줄바꿈 없이 한 줄로 입력
3. **서버 재시작**: .env 파일 수정 후 서버를 재시작해야 합니다
4. **환경 변수 확인**:
   ```bash
   python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('OPENWEATHER:', os.getenv('OPENWEATHER_API_KEY')[:10] if os.getenv('OPENWEATHER_API_KEY') else 'None'); print('KMA:', os.getenv('KMA_SERVICE_KEY')[:10] if os.getenv('KMA_SERVICE_KEY') else 'None')"
   ```

