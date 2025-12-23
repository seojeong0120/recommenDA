# 프로젝트명 (recommenDA)

> 시니어를 위한 날씨·위치·건강 상태 기반 맞춤형 운동/시설 추천 및 LLM 설명 생성 서비스  
> “정량 알고리즘으로 후보를 만들고, LLM으로 설명가능성과 개인화 문장화를 강화”하는 하이브리드 추천 시스템

---

## 1. 프로젝트 개요 (Overview)

### 배경
- 고령 인구 증가와 함께, **시니어 맞춤형 운동 추천**에 대한 수요가 증가하고 있음.
- 기존 운동 추천/앱들은:
  - 날씨·공기질·위치 정보를 충분히 반영하지 못하거나,
  - 시니어의 질환/통증·안전 이슈를 세밀하게 고려하지 못하고,
  - “왜 이 운동이 나에게 맞는지”에 대한 **설명(Explanation)**이 부족함.

### 목표
- **목표**: 시니어의 건강 상태, 위치, 날씨·공기질 정보를 종합해 **안전하고 이해 가능한 운동/시설 추천**을 제공하는 서비스 구축.
- **입력 → 처리 → 출력**
  - 입력:
    - 사용자 프로필: 나이대, 건강 이슈, 운동 목표, 실내/실외 선호, 위치
    - 외부 컨텍스트: 날씨(기온, 강수, 미세먼지), 시간대
    - 운동/시설 데이터: 공공 운동시설 프로그램, 운동 영상 메타데이터
  - 처리:
    1. 룰/스코어 기반 후보 생성 (시설/운동 Top-K)
    2. 위험 날씨 판단 및 실내 운동 전환
    3. LLM 기반 리랭킹 + 추천 근거/주의사항/다음 행동 생성
  - 출력:
    - 시설 추천 리스트 + 요약 사유
    - 날씨 정보
    - (위험 시) 운동 영상 + LLM이 생성한 **추천 근거·주의사항·오늘의 액션(next_step)** 텍스트

---

## 2. 문제 정의 (Problem Statement)

- **문제 정의**  
  - “시니어 사용자의 건강 상태와 날씨/위치 정보를 반영하여, **안전하고 이해 가능한 운동/시설 추천**을 자동으로 제공하는 시스템 구축”
- **대상**
  - 시니어 개인 사용자
  - 시니어 운동 프로그램을 운영하는 지자체·기관
  - 모바일 앱(Flutter) 클라이언트
- **정량적/질적 목표**
  - 위험 날씨(폭염/한파/미세먼지 고농도) 상황에서 **실외 대신 실내 운동으로 자동 전환**.
  - LLM을 활용해 각 추천에 대해 **2~4줄 근거 + 1~2개 주의사항 + 오늘의 액션**을 제공하여 설명가능성을 향상.
  - 룰/스코어 기반 Top-K 후보 위에 LLM을 올려, **재현성(정량 알고리즘) + UX(자연어 설명)**를 동시에 확보.

---

## 3. 전체 시스템 구조 (System Architecture)

```
[Input]
  - User Profile (나이대, 건강이슈, 목표, 선호 환경, 위치)
  - Weather / Air Quality (기온, 강수확률, 미세먼지)
  - Exercise / Facility Data
        ↓
[Preprocessing]
  - 날씨/위치 기반 위험도 평가
  - 운동/시설 메타데이터 전처리 (신체부위, 체력항목, 장비 등)
        ↓
[Model / Core Logic]
  - Rule/Scoring 기반 후보 생성 (시설, 운동 영상 Top-K)
  - LLM Reranker + Explainer
        ↓
[Post-processing]
  - LLM 출력 JSON 검증(Pydantic)
  - 후보 ID 매핑 및 최종 추천 리스트 구성
        ↓
[Output]
  - /api/recommend JSON 응답:
    - recommendations (시설 추천)
    - weather_info
    - exercise_videos (LLM 근거/주의/next_step 포함)
```

- **주요 컴포넌트**
  - `service/api.py` : FastAPI 기반 REST API, Flutter 앱과 연동
  - `recommender/` :
    - `pipeline.py` : 시설 추천 파이프라인
    - `exercise_recommender.py` : 운동 영상 추천 및 LLM 후보 생성/리랭킹
    - `llm/` : LLM 클라이언트, 프롬프트, 스키마, 리랭커
  - `db/` : 사용자 정보, 추천 이력 관리
  - `data/processed/` : 운동 영상/시설 데이터

---

## 4. 기술 스택 (Tech Stack)

### Backend / Core
- **Language**: Python 3.11
- **Framework**: FastAPI
- **Model / Algorithm**:
  - Rule/Scoring 기반 후보 생성 로직 (시설/운동 영상)
  - Upstage Solar LLM 기반 **JSON 모드 리랭커 + 설명 생성기**
  - Pydantic 기반 스키마 검증

### System / Infra
- **OS**: Linux (Docker 컨테이너 기준), macOS 개발 환경
- **Container / Deployment**: Docker, Uvicorn

### Data / Storage
- **Dataset**:
  - 공공 운동시설/프로그램 데이터 (`facility_program_master.json`)
  - 운동 영상 메타데이터 (`exercise_video.json`)
- **DB / File Format**:
  - PostgreSQL (사용자/세션/커뮤니티)
  - JSON 파일 (운동 영상, 추천 이력 등 일부 로컬 스토리지)

---

## 5. 데이터 설명 (Dataset)

- **데이터 출처**
  - 공공데이터 포털 등에서 수집한 운동시설/프로그램 정보
  - 수집·정제한 시니어 운동 영상 메타데이터
- **데이터 규모**
  - 시설/프로그램: 수십만 건 수준 (`facility_program_master.json`)
  - 운동 영상: 수백 개 수준 (`exercise_video.json`)
- **입력 / 출력 형태**
  - 입력: 체육시설 ID, 프로그램명, 좌표, 운동 종류, 신체부위, 체력항목, 장비, URL 등
  - 출력: 추천 시설/운동 리스트 + LLM이 생성한 자연어 설명 필드

| 항목       | 설명 |
|-----------|------|
| 데이터 수 | 시설/프로그램: 수십만 건, 운동 영상: 수백 건 내외 |
| 입력 형태 | JSON (공공데이터 → 전처리 후 `data/processed/*.json`) |
| 출력 형태 | FastAPI JSON 응답 (`/api/recommend`, `/api/exercise-videos/*`) |
| 전처리    | 결측/이상치 처리, 신체부위 파싱(`등/허리` → `["등","허리"]`), 장비/환경 플래그 생성 등 |

---

## 6. 핵심 방법론 (Methodology)

1. **Rule/Scoring 기반 후보 생성**
   - 사용자 목표(근력/유연성/균형)와 체력항목, 장비 유무, 전날 사용 부위를 반영해 **운동 영상 후보 Top-K**를 생성 (`generate_exercise_candidates`).
   - 시설 추천도 거리, 실내/실외, 프로그램 카테고리 등을 스코어링하여 Top-K 선정.

2. **날씨 위험도 평가 및 실내 전환**
   - 기상청 초단기예보 + 미세먼지 정보를 바탕으로, 고위험(폭염, 한파, 고농도 미세먼지) 시 **실외 운동 대신 실내 운동 영상**을 추천.

3. **LLM Reranker + Explainer**
   - 입력(JSON):
     - `user_profile`: 나이대, 건강이슈, 목표, 선호 환경 등
     - `context`: 날씨 요약, 기온, 강수확률, 시간대, 최대 이동 거리 등
     - `candidates`: 룰/스코어 기반으로 생성된 운동 영상 후보 Top-K (`ExerciseCandidate`)
   - 출력(JSON, Pydantic 스키마 강제):
     - `ranked_recommendations: [{id, rank, why[], cautions[], next_step}]`
     - `user_friendly_summary: str`
     - `safety_flags: [str]`
   - LLM은 **후보를 새로 만들지 않고**, 주어진 후보들만 재정렬(rerank)하며, 각 후보에 대해:
     - 추천 근거(2~4줄)
     - 주의사항(1~2개)
     - 오늘 실행할 액션(next_step)을 생성.

4. **LLM 출력 검증 및 폴백**
   - Upstage Solar LLM은 `response_format={"type": "json_object"}`로 호출.
   - 응답은 `LLMExerciseOutput` (Pydantic)으로 검증하고, 실패 시 **룰/스코어 기반 기본 추천**으로 폴백.

---

## 7. 실험 및 결과 (Experiments & Results)


### 실험 설정
- 실험 환경: Python 3.11, FastAPI, PostgreSQL, Upstage Solar LLM
- 비교 대상:
  - **Baseline**: 룰/스코어 기반 추천만 사용하는 경우
  - **Proposed**: 룰/스코어 + LLM 리랭킹/설명 결합

### 결과 (예시 양식)

| Metric                 | Baseline | Proposed |
|------------------------|----------|----------|
| 사용자 만족도(설문)      |    -     |    -     |
| 위험 날씨 실외 추천 비율 |    -     |    -     |
| 설명 이해도 점수        |    -     |    -     |

- 정량·정성 평가 결과를 통해:
  - 위험 상황에서의 안전성 향상
  - 추천 근거가 있는 자연어 설명 제공으로, 시니어 사용자의 **신뢰감/이해도** 향상 등을 기술.

---

## 8. 실행 방법 (How to Run)

### 8.1 백엔드 서버 실행

#### (1) Docker 실행

```bash
docker build -t recommenda-api .
docker run -p 8000:8000 recommenda-api
```

#### (2) 로컬 실행

```bash
cd senior-exercise-recommender-core
pip install -r requirements.txt
uvicorn service.api:app --host 0.0.0.0 --port 8000
```

### 8.2 LLM(Upstage) 연동 설정

기본값은 개발용 더미(`LLM_PROVIDER=local_stub`)로 동작하며, 실제 Upstage Solar LLM을 쓰려면 아래 환경 변수를 설정합니다.

- `LLM_PROVIDER=upstage`
- `LLM_MODEL=solar-pro` (또는 사용하고 싶은 모델명)
- `LLM_API_KEY=<YOUR_UPSTAGE_API_KEY>`
- `UPSTAGE_BASE_URL=https://api.upstage.ai/v1/solar` (기본값)

### 8.3 프론트엔드 앱 실행

- Flutter 예제 앱은 `example1/` 디렉토리에 있으며, 자세한 실행 방법은 해당 디렉토리의 README를 참고합니다.

### 8.4 실행 시 주의사항

- PostgreSQL 연결 정보, 기상청 API 키 등은 `.env` 또는 `ENV_SETUP.md` 안내에 따라 설정합니다.
- LLM 연동이 불안정할 경우에도, 서버는 **local_stub 모드**로 기본 추천을 제공하도록 설계되어 있습니다.

---

## 9. 프로젝트 구조 (Directory Structure)

```bash
recommenDA/
├── senior-exercise-recommender-core/
│   ├── service/                # FastAPI 서비스 (엔드포인트 정의)
│   │   └── api.py
│   ├── recommender/            # 추천 엔진 및 LLM 모듈
│   │   ├── pipeline.py         # 시설 추천 파이프라인
│   │   ├── exercise_recommender.py  # 운동 영상 추천/LLM 후보 생성
│   │   ├── llm/                # LLM 클라이언트, 프롬프트, 스키마, 리랭커
│   │   └── rules.py            # 추천 룰/스코어링 로직
│   ├── db/                     # DB 초기화 및 사용자/세션 관리
│   ├── data/
│   │   └── processed/          # 전처리된 시설/운동 데이터(JSON)
│   ├── requirements.txt
│   └── ENV_SETUP.md
├── example1/                   # Flutter 모바일 앱 예제
├── Dockerfile                  # 백엔드 Docker 설정
└── README.md                   # 프로젝트 메인 문서
```

---

## 10. 한계점 및 향후 계획 (Limitations & Future Work)

- **한계점**
  - 운동/시설 데이터 출처가 특정 시점/지역에 한정되어 있음.
  - LLM 출력 품질이 프롬프트/모델 버전에 따라 달라질 수 있음.
  - 현재는 주로 “개인 맞춤 + 안전”에 초점이 맞춰져 있고, 커뮤니티/사회적 연결 기능은 제한적.

- **향후 계획**
  - 더 다양한 지역/시설 데이터 통합 및 실시간 업데이트.
  - 사용자 피드백을 활용한 **학습형 랭킹/설명** 고도화.
  - 세션/커뮤니티 기능 강화 (동네별 그룹 운동 추천, 참여 경험 기반 추천 등).
  - LLM 다국어 지원 및 음성 인터페이스 연동.

---

## 11. 팀 구성 및 역할 (Team)

| 이름 | 역할 |
|------|------|
| 홍길동 | 데이터 전처리 / 추천 엔진 |
| 김서정 | 백엔드/추천 엔진 개발 / LLM/프롬프트 엔지니어링 |
| 김현수 | 데이터 전처리 / 프론트엔드(Flutter) 개발 |
| 안시연  | 프론트엔드(Flutter) 개발 |

