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

## 기술 스택

### 백엔드
- Python 3.11
- FastAPI
- PostgreSQL
- Docker

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
