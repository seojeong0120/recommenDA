# API Usage Guide for `recommend()` Function

본 문서는 추천 엔진의 핵심 함수인 `recommend()`의 입력 구조, 출력 구조, 호출 방식,
그리고 전체 처리 흐름을 기술합니다.

---

## 1. Overview

`recommend()` 함수는 다음 세 가지 정보를 기반으로 운동/시설 TOP-N 리스트를 반환합니다.

- **UserProfile** (사용자 신체 상태 및 운동 목표)
- **Location** (사용자 위치)
- **WeatherInfo** (현재 또는 예측 날씨 정보)

추천 엔진은  
① 사용자 건강 상태 기반 안전 필터  
② 날씨 기반 실내/실외 조건 판단  
③ 거리/목표 적합도/시니어 친화도/강도 적합도 기반 점수 계산  
④ 최종 Top-N 프로그램 반환  
으로 구성됩니다.

---

## 2. Input Types

### UserProfile

```json
{
  "age_group": "65-69",
  "health_issues": ["knee_pain"],
  "goals": ["blood_pressure", "flexibility"],
  "preference_env": "indoor"
}
