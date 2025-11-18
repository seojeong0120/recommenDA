# recommender/scoring.py
from .types import UserProfile, WeatherInfo
from .utils import linear_score

def distance_score(dist_km: float, max_distance_km: float = 3.0) -> float:
    """
    0km일 때 1점, max_distance_km 이상이면 0점에 가깝게.
    """
    return linear_score(dist_km, 0.0, max_distance_km, reverse=True)

def goal_match_score(sport_category: str, goals: list[str]) -> float:
    """
    사용자 목표(혈압, 체중, 근력, 유연성, 사회활동)와
    운동 카테고리 매칭 정도를 0~1로.
    일단 간단한 룰 기반으로 시작.
    """
    goals_set = set(goals)
    score = 0.0

    # 예시 매핑 (나중에 테이블로 빼도 됨)
    if "blood_pressure" in goals_set and sport_category in ["walking", "water_exercise", "yoga"]:
        score += 0.7
    if "weight" in goals_set and sport_category in ["walking", "jogging", "light_strength"]:
        score += 0.7
    if "strength" in goals_set and sport_category in ["light_strength", "strength"]:
        score += 0.7
    if "flexibility" in goals_set and sport_category in ["yoga", "stretching"]:
        score += 0.7
    if "social" in goals_set and sport_category in ["group_class", "dance"]:
        score += 0.7

    return min(score, 1.0)

def weather_suitability_score(is_indoor: bool, weather: WeatherInfo) -> float:
    """
    날씨가 나쁠수록 실내 점수 ↑, 좋을수록 실외도 괜찮게.
    """
    rain_prob = weather["rain_prob"]
    pm10 = weather["pm10"]

    if is_indoor:
        # 날씨가 나쁠수록 더 좋게
        badness = 0.5 * rain_prob + 0.5 * (pm10 / 100.0)
        return min(1.0, 0.5 + badness)  # 0.5~1.0 사이
    else:
        # 날씨가 좋으면 1에 가깝게
        badness = 0.5 * rain_prob + 0.5 * (pm10 / 100.0)
        return max(0.0, 1.0 - badness)

def senior_friendly_score(is_senior_friendly: bool) -> float:
    return 1.0 if is_senior_friendly else 0.5

def intensity_fit_score(intensity_level: str, age_group: str, health_issues: list[str]) -> float:
    """
    연령대/건강 상태 대비 강도 적합도.
    """
    # 기본 값
    base = 0.7 if intensity_level == "medium" else 0.9 if intensity_level == "low" else 0.5

    if "hypertension" in health_issues or "heart_disease" in health_issues:
        if intensity_level == "high":
            base = 0.1

    if age_group in ["70-74", "75+"] and intensity_level == "high":
        base = 0.2

    return max(0.0, min(1.0, base))

def final_score(row, user_profile: UserProfile, weather: WeatherInfo) -> float:
    """
    후보(row: pandas Series)에 대해 최종 점수 계산.
    """
    dist_km = float(row["dist_km"])
    sport_category = str(row["sport_category"])
    is_indoor = bool(row["is_indoor"])
    intensity_level = str(row["intensity_level"])
    senior_flag = bool(row.get("senior_friendly", False))

    goals = user_profile.get("goals", [])
    age_group = user_profile.get("age_group", "65-69")
    health_issues = user_profile.get("health_issues", [])

    d_score = distance_score(dist_km)
    g_score = goal_match_score(sport_category, goals)
    w_score = weather_suitability_score(is_indoor, weather)
    s_score = senior_friendly_score(senior_flag)
    i_score = intensity_fit_score(intensity_level, age_group, health_issues)

    # 가중치 합
    return (
        0.35 * d_score +
        0.25 * g_score +
        0.20 * w_score +
        0.10 * s_score +
        0.10 * i_score
    )
