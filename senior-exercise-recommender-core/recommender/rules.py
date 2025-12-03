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
    노인 기준으로 보수적으로 필터링.
    """
    df = candidates.copy()
    rain_prob = weather["rain_prob"]
    pm10 = weather["pm10"]
    temp = weather.get("temp", 20.0)  # 기온 정보

    # 1) 비 올 확률이 크면 실외 운동 제거
    if rain_prob > 0.6:
        # 비 올 확률이 60% 이상이면 모든 실외 운동 제거
        df = df[df["is_indoor"] == True]

    # 2) 미세먼지가 매우 높으면 실외 운동 제거 (PM10 > 150: 나쁨)
    if pm10 > 150:
        # 실외 운동 모두 제거
        df = df[df["is_indoor"] == True]
    elif pm10 > 80:
        # 미세먼지가 높으면 실외 고강도 운동 제거
        df = df[~((df["is_indoor"] == False) & (df["intensity_level"] == "high"))]

    # 3) 기온이 너무 높거나 낮으면 실외 운동 제거
    # 노인 기준: 30도 이상 또는 -5도 이하
    if temp >= 30.0 or temp <= -5.0:
        # 폭염/한파 상황에서는 실외 운동 제거
        df = df[df["is_indoor"] == True]
    elif temp >= 28.0 or temp <= 0.0:
        # 더위/추위가 심하면 실외 고강도 운동 제거
        df = df[~((df["is_indoor"] == False) & (df["intensity_level"] == "high"))]

    return df
