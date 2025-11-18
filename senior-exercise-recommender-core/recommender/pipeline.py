# recommender/pipeline.py
from typing import List
import os
import pandas as pd

from .types import UserProfile, Location, WeatherInfo, Recommendation
from .utils import haversine_distance_km
from .rules import filter_by_health, filter_by_weather
from .scoring import final_score

DATA_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "data",
    "processed",
    "facility_program_master.parquet",
)

def load_facility_master() -> pd.DataFrame:
    """
    A가 만든 facility_program_master.parquet을 로드.
    없으면 에러 대신 빈 DataFrame 반환(초기 개발용).
    """
    if not os.path.exists(DATA_PATH):
        # 초기 개발 단계에서 데이터가 아직 없을 수 있음
        return pd.DataFrame(columns=[
            "fac_id", "fac_name", "address",
            "lat", "lon",
            "is_indoor",
            "sport_category",
            "program_name",
            "intensity_level",
            "senior_friendly",
            "operating_hours",
        ])
    return pd.read_parquet(DATA_PATH)

def add_distance(df: pd.DataFrame, user_location: Location) -> pd.DataFrame:
    df = df.copy()
    lat_u = user_location["lat"]
    lon_u = user_location["lon"]
    df["dist_km"] = df.apply(
        lambda row: haversine_distance_km(lat_u, lon_u, row["lat"], row["lon"]), axis=1
    )
    return df

def filter_by_radius(df: pd.DataFrame, max_km: float = 3.0) -> pd.DataFrame:
    return df[df["dist_km"] <= max_km].copy()

def recommend(
    user_profile: UserProfile,
    user_location: Location,
    weather_info: WeatherInfo,
    top_k: int = 5,
) -> List[Recommendation]:
    """
    전체 추천 파이프라인:
    1) 시설-프로그램 마스터 로드
    2) 사용자 위치 기준 거리 계산/반경 필터
    3) 건강/날씨 룰 필터링
    4) 점수 계산 및 상위 K개 선택
    5) Recommendation 리스트 반환
    """
    df = load_facility_master()
    if df.empty:
        # 개발 초기용: 빈 리스트 반환
        return []

    # 1) 거리 컬럼 추가
    df = add_distance(df, user_location)

    # 2) 반경 필터링
    df = filter_by_radius(df, max_km=3.0)
    if df.empty:
        return []

    # 3) 룰 기반 필터 (건강, 날씨)
    df = filter_by_health(df, user_profile)
    df = filter_by_weather(df, weather_info)
    if df.empty:
        return []

    # 4) 점수 계산
    df = df.copy()
    df["score"] = df.apply(
        lambda row: final_score(row, user_profile, weather_info),
        axis=1,
    )

    df = df.sort_values("score", ascending=False).head(top_k)

    # 5) Recommendation 형태로 변환
    recommendations: List[Recommendation] = []
    for _, row in df.iterrows():
        rec: Recommendation = {
            "facility_name": str(row["fac_name"]),
            "program_name": str(row["program_name"]),
            "sport_category": str(row["sport_category"]),
            "distance_km": float(row["dist_km"]),
            "intensity_level": str(row["intensity_level"]),
            "is_indoor": bool(row["is_indoor"]),
            "reason": _build_reason(row, user_profile, weather_info),
        }
        recommendations.append(rec)

    return recommendations

def _build_reason(row, user_profile: UserProfile, weather: WeatherInfo) -> str:
    """
    간단한 추천 설명 생성 (템플릿 기반).
    나중에 문장 조금씩만 바꿔줘도 충분히 그럴듯해짐.
    """
    pieces = []

    # 건강 관련
    health_issues = user_profile.get("health_issues", [])
    goals = user_profile.get("goals", [])
    sport = row["sport_category"]

    if "knee_pain" in health_issues:
        pieces.append("무릎 통증을 고려하여 충격이 적은 운동을 우선으로 선택했습니다.")
    if "hypertension" in health_issues:
        pieces.append("혈압 관리에 도움이 되는 저중강도 유산소/스트레칭 위주의 프로그램입니다.")
    if "weight" in goals:
        pieces.append("체중 관리 목표에 도움이 되는 활동량을 고려했습니다.")

    # 날씨 관련
    if row["is_indoor"]:
        if weather["rain_prob"] > 0.5 or weather["pm10"] > 80:
            pieces.append("현재 날씨/대기질을 고려해 실내 시설을 우선 추천했습니다.")
    else:
        pieces.append("야외 활동을 선호하시는 점을 반영했습니다.")

    if not pieces:
        pieces.append("연령과 건강 상태, 거리, 날씨를 종합적으로 고려한 추천입니다.")

    return " ".join(pieces)
