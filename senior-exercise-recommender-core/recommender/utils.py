# recommender/utils.py
import math

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
