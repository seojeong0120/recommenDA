# recommender/pipeline.py
from typing import List
import os
import json
import pandas as pd
from pathlib import Path

from .types import UserProfile, Location, WeatherInfo, Recommendation
from .utils import haversine_distance_km
from .rules import filter_by_health, filter_by_weather
from .scoring import final_score

BASE_DIR = Path(__file__).resolve().parents[1]
JSON_PATH = BASE_DIR / "data" / "processed" / "facility_program_master.json"

def load_facility_master() -> pd.DataFrame:
    """
    facility_program_master.json 파일을 직접 로드하여 DataFrame으로 변환.
    없으면 에러 대신 빈 DataFrame 반환(초기 개발용).
    """
    if not JSON_PATH.exists():
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
    
    # JSON 파일 로드
    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if not data:
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
    
    # JSON 데이터를 DataFrame으로 변환
    rows = []
    for idx, item in enumerate(data):
        # 필수 필드 추출
        fac_name = str(item.get('시설명', '')).strip() if pd.notna(item.get('시설명')) else ''
        address = str(item.get('주소', '')).strip() if pd.notna(item.get('주소')) else ''
        lat = item.get('시설위도')
        lon = item.get('시설경도')
        is_indoor_str = str(item.get('실내여부', '')).strip() if pd.notna(item.get('실내여부')) else ''
        sport_category = str(item.get('시설유형명', '')).strip() if pd.notna(item.get('시설유형명')) else ''
        
        # 좌표가 유효한지 확인
        if pd.isna(lat) or pd.isna(lon) or not fac_name:
            continue
        
        # 실내여부 변환
        is_indoor = is_indoor_str == '실내' if is_indoor_str else True
        
        # 프로그램 정보 처리
        programs = item.get('programs')
        
        # programs가 배열이거나 NaN인지 확인
        is_programs_empty = (
            pd.isna(programs) if not isinstance(programs, (list, dict)) else False
        ) or programs is None or programs == '' or (isinstance(programs, list) and len(programs) == 0)
        
        if is_programs_empty:
            # 프로그램 정보가 없으면 빈 문자열로 설정 (기본값 생성하지 않음)
            program_name = ''
            intensity_level = 'medium'  # 기본값
            senior_friendly = True  # 기본값
            operating_hours = '평일 오전'
        else:
            # programs가 있으면 처리 (나중에 확장 가능)
            # 일단 기본값으로 처리
            program_name = f'{sport_category} 프로그램' if sport_category else '일반 운동 프로그램'
            intensity_level = 'medium'
            senior_friendly = True
            operating_hours = '평일 오전'
        
        rows.append({
            'fac_id': f'F{len(rows):06d}',
            'fac_name': fac_name,
            'address': address,
            'lat': float(lat),
            'lon': float(lon),
            'is_indoor': is_indoor,
            'sport_category': sport_category if sport_category else 'general',
            'program_name': program_name,
            'intensity_level': intensity_level,
            'senior_friendly': senior_friendly,
            'operating_hours': operating_hours,
        })
    
    if not rows:
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
    
    # DataFrame 생성
    df = pd.DataFrame(rows)
    
    # 중복 제거 (같은 시설, 같은 프로그램, 같은 위치)
    df = df.drop_duplicates(subset=['fac_name', 'program_name', 'lat', 'lon'])
    
    return df

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
    max_radius_km: float = 20.0,
) -> List[Recommendation]:
    """
    전체 추천 파이프라인:
    1) 시설-프로그램 마스터 로드
    2) 사용자 위치 기준 거리 계산
    3) 건강/날씨 룰 필터링 (거리 필터보다 먼저 적용)
    4) 동적 반경 확장으로 최소 추천 개수 보장
    5) 점수 계산 및 상위 K개 선택
    6) Recommendation 형태로 변환
    
    Args:
        max_radius_km: 최대 반경 (기본 20km, 데이터가 적을 때 확장)
    """
    df = load_facility_master()
    if df.empty:
        return []

    # 1) 거리 컬럼 추가
    df = add_distance(df, user_location)

    # 2) 룰 기반 필터 (건강, 날씨) - 거리 필터보다 먼저 적용
    # 이렇게 하면 건강/날씨 조건에 맞는 시설 중에서 거리순으로 추천 가능
    df = filter_by_health(df, user_profile)
    df = filter_by_weather(df, weather_info)
    
    if df.empty:
        return []

    # 3) 동적 반경 확장: 최소 top_k개 추천 보장
    # 3km -> 5km -> 10km -> 20km 순으로 확장
    radius_candidates = [3.0, 5.0, 10.0, max_radius_km]
    df_filtered = pd.DataFrame()
    
    for radius in radius_candidates:
        df_filtered = filter_by_radius(df, max_km=radius)
        if len(df_filtered) >= top_k:
            break
    
    # 최소한의 추천을 위해 반경 내 모든 후보 사용 (top_k보다 적어도)
    if df_filtered.empty:
        # 반경 확장 후에도 없으면 거리순으로 상위 후보 사용
        df_filtered = df.nsmallest(min(top_k * 2, len(df)), "dist_km")
    
    if df_filtered.empty:
        return []

    # 4) 점수 계산
    df_filtered = df_filtered.copy()
    df_filtered["score"] = df_filtered.apply(
        lambda row: final_score(row, user_profile, weather_info),
        axis=1,
    )

    # 5) 상위 K개 선택
    df_filtered = df_filtered.sort_values("score", ascending=False).head(top_k)

    # 6) Recommendation 형태로 변환
    recommendations: List[Recommendation] = []
    for _, row in df_filtered.iterrows():
        rec: Recommendation = {
            "fac_id": str(row["fac_id"]),
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
    프로그램명이 없으면 시설명만 언급하는 멘트로 생성.
    """
    program_name = str(row.get("program_name", "")).strip()
    facility_name = str(row.get("fac_name", "")).strip()
    
    # 프로그램명이 없으면 시설명만 언급
    if not program_name:
        return f"오늘은 {facility_name}에서 운동 어떠세요?"
    
    # 프로그램명이 있으면 기존 로직 사용
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
