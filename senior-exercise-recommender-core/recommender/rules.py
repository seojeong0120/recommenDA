# recommender/rules.py
from typing import List
import pandas as pd
from .types import UserProfile, WeatherInfo

def filter_by_health(candidates: pd.DataFrame, user_profile: UserProfile) -> pd.DataFrame:
    """
    건강 상태(무릎/허리/혈압 등)를 기준으로
    '하면 안 되는' 프로그램을 제외하는 함수.

    candidates: facility_program_master에서 뽑은 후보들 (각 row = 한 프로그램)
    기대 컬럼: sport_category, intensity_level 등
    """
    health_issues = set(user_profile.get("health_issues", []))

    df = candidates.copy()

    # 예: 무릎 통증이면 high intensity 운동 제거 (일단 골격만)
    if "knee_pain" in health_issues:
        df = df[df["intensity_level"] != "high"]

    # TODO: 허리 통증, 심혈관, 당뇨 등 세부 룰 추가

    return df

def filter_by_weather(candidates: pd.DataFrame, weather: WeatherInfo) -> pd.DataFrame:
    """
    날씨/미세먼지/시간대 등을 기준으로
    실외 고위험 운동 제거 or 패널티를 줄 때 사용.
    여기서는 '완전 제거' 위주의 간단 필터만 처리.
    """
    df = candidates.copy()
    rain_prob = weather["rain_prob"]
    pm10 = weather["pm10"]

    # 예: 비 올 확률이 크면 실외(high intensity) 프로그램 제거
    if rain_prob > 0.6:
        df = df[~((df["is_indoor"] == False) & (df["intensity_level"] == "high"))]

    # 예: 미세먼지가 매우 높으면 실외 유산소 계열 제거 (여기선 sport_category로 추후 확장)
    # TODO: sport_category 기준으로 더 섬세하게 조정

    return df
