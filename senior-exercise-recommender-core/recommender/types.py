# recommender/types.py
from typing import List, Literal, TypedDict

AgeGroup = Literal["60-64", "65-69", "70-74", "75+"]

class UserProfile(TypedDict):
    age_group: AgeGroup
    health_issues: List[str]      # ["knee_pain", "hypertension"]
    goals: List[str]              # ["blood_pressure", "weight", "strength", "flexibility", "social"]
    preference_env: str           # "indoor" | "outdoor" | "any"

class Location(TypedDict):
    lat: float
    lon: float

class WeatherInfo(TypedDict):
    temp: float
    rain_prob: float
    pm10: float
    is_daytime: bool

class Recommendation(TypedDict):
    facility_name: str
    program_name: str
    sport_category: str
    distance_km: float
    intensity_level: str
    is_indoor: bool
    reason: str
