# recommender/utils.py
import math
from typing import Any

def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    지구 표면에서 두 좌표 사이의 대략적인 거리(km)를 계산.
    """
    R = 6371.0  # 지구 반경(km)

    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    r_lat1 = math.radians(lat1)
    r_lat2 = math.radians(lat2)

    a = math.sin(d_lat / 2) ** 2 + math.cos(r_lat1) * math.cos(r_lat2) * math.sin(d_lon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))

    return R * c

def linear_score(x: float, x_min: float, x_max: float, reverse: bool = False) -> float:
    """
    x를 [x_min, x_max] 구간에서 0~1 사이로 선형 스케일링.
    reverse=True면 큰 값일수록 점수가 작게.
    """
    if x_min == x_max:
        return 0.0
    v = (x - x_min) / (x_max - x_min)
    v = max(0.0, min(1.0, v))
    return 1.0 - v if reverse else v

def is_weather_dangerous(weather: Any) -> bool:
    """
    날씨 정보(dict 또는 WeatherInfo 객체)를 받아
    '실외 활동이 위험한지' 여부를 판단.

    기준 (보수적, 시니어 기준):
    - 강수확률 >= 60%
    - 미세먼지(PM10) >= 81 (나쁨 이상)
    - 기온 <= -5℃ 또는 >= 33℃
    """

    def _get(obj: Any, key: str, default=None):
        if obj is None:
            return default
        if isinstance(obj, dict):
            return obj.get(key, default)
        return getattr(obj, key, default)

    rain_prob = _get(weather, "rain_prob")
    pm10 = _get(weather, "pm10")
    temp = _get(weather, "temp")

    # 값이 전부 없으면 위험 아님으로 처리
    if rain_prob is None and pm10 is None and temp is None:
        return False

    if rain_prob is not None and float(rain_prob) >= 60:
        return True

    if pm10 is not None and float(pm10) >= 81:
        return True

    if temp is not None:
        t = float(temp)
        if t <= -5 or t >= 33:
            return True

    return False
