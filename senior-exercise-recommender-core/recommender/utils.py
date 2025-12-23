# recommender/utils.py
import math
from typing import Any

def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    r_lat1 = math.radians(lat1)
    r_lat2 = math.radians(lat2)

    a = math.sin(d_lat / 2) ** 2 + math.cos(r_lat1) * math.cos(r_lat2) * math.sin(d_lon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))
    return R * c

def linear_score(x: float, x_min: float, x_max: float, reverse: bool = False) -> float:
    if x_min == x_max:
        return 0.0
    v = (x - x_min) / (x_max - x_min)
    v = max(0.0, min(1.0, v))
    return 1.0 - v if reverse else v

def is_weather_dangerous(weather: Any) -> bool:
    """
    실외 활동이 위험한 날씨인지 판단 (시니어 기준)
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
    precip_type = _get(weather, "precip_type", 0)

    # ✅ 1) 현재 비/눈/소나기면 즉시 위험
    try:
        if int(precip_type) != 0:
            return True
    except (ValueError, TypeError):
        pass

    # 값 전부 없으면 안전
    if rain_prob is None and pm10 is None and temp is None:
        return False

    # ✅ 2) 강수확률 (0~1 / 0~100 자동 처리)
    if rain_prob is not None:
        try:
            rp = float(rain_prob)
            rp_pct = rp * 100.0 if rp <= 1.0 else rp
            if rp_pct >= 60.0:
                return True
        except (ValueError, TypeError):
            pass

    # 3) 미세먼지
    if pm10 is not None:
        try:
            if float(pm10) >= 81.0:
                return True
        except (ValueError, TypeError):
            pass

    # 4) 기온
    if temp is not None:
        try:
            t = float(temp)
            if t <= -5.0 or t >= 33.0:
                return True
        except (ValueError, TypeError):
            pass

    return False
