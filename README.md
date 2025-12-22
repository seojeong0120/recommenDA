# recommenDA

시니어를 위한 맞춤형 운동 추천 및 커뮤니티 서비스

## 프로젝트 개요

recommenDA는 시니어의 건강 상태, 위치, 날씨 정보를 종합적으로 분석하여 최적의 운동 프로그램과 시설을 추천하는 서비스입니다.

## 프로젝트 구조

```
recommenDA/
├── senior-exercise-recommender-core/  # 백엔드 API 서버
│   ├── service/                       # FastAPI 서비스
│   ├── recommender/                   # 추천 엔진
│   ├── db/                            # 데이터베이스 관련
│   └── data/                          # 데이터 파일
├── example1/                          # Flutter 모바일 앱
├── Dockerfile                         # Docker 설정
└── README.md                          # 프로젝트 메인 문서
```

## 주요 기능

- **맞춤형 운동 추천**: 사용자의 건강 상태, 목표, 선호도를 기반으로 운동 추천
- **날씨 기반 추천**: 실내/실외 운동 자동 판단
- **위치 기반 추천**: 사용자 위치 기반 가까운 운동 시설 추천
- **커뮤니티 기능**: 운동 기록 및 공유
- **LLM 기반 리랭킹 및 설명 생성**: 룰/스코어 기반으로 생성한 운동 영상 후보 Top-K에 대해 LLM이 재정렬(rerank)하고, 추천 근거/주의사항/요약 문장을 자연어로 생성

## 기술 스택

### 백엔드
- Python 3.11
- FastAPI
- PostgreSQL
- Docker
- Upstage Solar (LLM, 선택적으로 사용)

### 프론트엔드
- Flutter
- Dart

## 시작하기

### 백엔드 서버 실행

1. Docker를 사용한 실행:
```bash
docker build -t recommenda-api .
docker run -p 8000:8000 recommenda-api
```

2. 로컬 실행:
```bash
cd senior-exercise-recommender-core
pip install -r requirements.txt
uvicorn service.api:app --host 0.0.0.0 --port 8000
```

### LLM(Upstage) 연동 설정

기본값은 개발용 더미(`LLM_PROVIDER=local_stub`)로 동작하며, 실제 Upstage Solar LLM을 쓰려면 아래 환경 변수를 설정합니다.

- **LLM_PROVIDER**: `upstage`
- **LLM_MODEL**: `solar-pro` 등 사용하고 싶은 모델 이름
- **LLM_API_KEY**: Upstage API 키
- **UPSTAGE_BASE_URL**: (선택) 기본값 `https://api.upstage.ai/v1/solar`

추천 파이프라인에서는 다음 순서로 LLM을 사용합니다.

1. 룰/스코어 기반 후보 생성: `generate_exercise_candidates`가 운동 영상 데이터에서 안전하고 합리적인 Top-K 후보를 만듭니다.
2. LLM 리랭킹 + 설명/주의 생성: `LLMRerankerExplainer`가 후보들을 사용자 프로필/날씨 컨텍스트에 맞게 재정렬하고, 각 운동의 추천 근거(`why`), 주의사항(`cautions`), 오늘의 액션(`next_step`), 전역 안전 플래그(`safety_flags`)를 JSON으로 생성합니다.
3. API 응답: `/api/recommend`에서 날씨가 위험한 경우, 위 LLM 결과를 이용해 실내 운동 영상과 함께 설명/주의사항을 클라이언트에 반환합니다.

### 프론트엔드 앱 실행

자세한 내용은 [example1/README.md](./senior-exercise-recommender-core/example1/README.md)를 참고하세요.

## API 문서

API 서버 실행 후 다음 주소에서 확인할 수 있습니다:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 환경 설정

백엔드 환경 설정은 `senior-exercise-recommender-core/ENV_SETUP.md`를 참고하세요.

## 라이선스

이 프로젝트는 공모전용 프로젝트입니다.
