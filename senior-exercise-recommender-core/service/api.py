# service/api.py
from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from db.user_repository import UserRepository

# 🔹 기존 추천 파이프라인
from recommender.pipeline import recommend as recommend_facilities

# 🔹 날씨 (추가)
from service.weather_client import fetch_weather
from recommender.types import WeatherInfo as WeatherInfoPayload

# 🔹 LLM 홈트 추천
from recommender.exercise_recommender import (
    load_exercises,
    choose_exercises_with_llm_for_today,
)

# 🔹 유틸
from recommender.utils import is_weather_dangerous

# =========================================================
# App
# =========================================================
app = FastAPI(title="Senior Exercise Recommendation API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================================================
# Utils
# =========================================================
def normalize_phone(phone: str) -> str:
    digits = re.sub(r"[^0-9]", "", phone or "")
    if digits.startswith("82"):
        digits = "0" + digits[2:]
    return digits


# =========================================================
# Schemas
# =========================================================
class SignUpRequest(BaseModel):
    phone: str
    password: str
    name: str
    birth_date: str
    gender: str
    health_conditions: List[str]
    exercise_goals: List[str]
    preferred_location: str
    guardian_phone: str
    address_road: str
    latitude: float
    longitude: float


class LoginRequest(BaseModel):
    phone: str
    password: str


class UserPublic(BaseModel):
    phone: str
    name: str
    gender: str
    age_group: str


class RecommendRequest(BaseModel):
    user_profile: Dict[str, Any]
    user_location: Dict[str, float]


class WeatherInfoResponse(BaseModel):
    temp: Optional[float]
    rain_prob: Optional[float]
    pm10: Optional[float]
    is_daytime: Optional[bool]


class ExerciseVideoResponse(BaseModel):
    name: str
    체력항목: str
    운동도구: str
    신체부위: str
    혼자여부: str
    url: str
    info: str
    reason: Optional[List[str]] = None
    cautions: Optional[List[str]] = None
    next_step: Optional[str] = None


class RecommendResponse(BaseModel):
    recommendations: List[Dict[str, Any]]
    weather_info: WeatherInfoResponse
    exercise_videos: List[ExerciseVideoResponse]


# =========================================================
# Health
# =========================================================
@app.get("/health")
def health():
    return {"ok": True}


# =========================================================
# Auth
# =========================================================
@app.post("/api/signup")
def signup(req: SignUpRequest):
    repo = UserRepository()
    phone = normalize_phone(req.phone)

    if repo.get_user_by_phone(phone):
        return {"success": False, "message": "이미 가입된 번호입니다."}

    user = repo.create_user(
        phone=phone,
        password=req.password,
        name=req.name,
        birth_date=req.birth_date,
        gender=req.gender,
        health_conditions=req.health_conditions,
        exercise_goals=req.exercise_goals,
        preferred_location=req.preferred_location,
        guardian_phone=req.guardian_phone,
        address_road=req.address_road,
        latitude=req.latitude,
        longitude=req.longitude,
    )

    return {"success": True, "user": user}


@app.post("/api/login")
def login(req: LoginRequest):
    repo = UserRepository()
    phone = normalize_phone(req.phone)

    user = repo.login(phone, req.password)
    if not user:
        return {"success": False, "message": "전화번호 또는 비밀번호가 올바르지 않습니다."}

    return {"success": True, "user": user}


# =========================================================
# Recommendation
# =========================================================

@app.post("/api/recommend", response_model=RecommendResponse)
def recommend(req: RecommendRequest):
    user_profile = req.user_profile
    user_location = req.user_location

    # ✅ 1️⃣ 날씨 먼저 조회 (핵심!)
    weather_raw: WeatherInfoPayload = fetch_weather(
        lat=user_location["lat"],
        lon=user_location["lon"],
    )
    weather_info = WeatherInfoResponse(**weather_raw)

    # ✅ 2️⃣ 시설 추천 (weather_info 반드시 전달)
    facilities = recommend_facilities(
        user_profile=user_profile,
        user_location=user_location,
        weather_info=weather_raw,
        top_k=5,
    )

    exercise_videos: list[ExerciseVideoResponse] = []

    # ✅ 3️⃣ 날씨 위험하면 → LLM 홈트 추천
    if is_weather_dangerous(weather_raw):
        exercises = load_exercises()

        if not exercises:
            exercise_videos.append(
                ExerciseVideoResponse(
                    name="",
                    체력항목="",
                    운동도구="",
                    신체부위="",
                    혼자여부="",
                    url="",
                    info="운동 데이터가 없습니다.",
                )
            )
        else:
            user_id = (
                str(user_profile.get("user_id"))
                or str(user_profile.get("id"))
                or str(user_profile.get("phone"))
                or f"user_{user_location['lat']}_{user_location['lon']}"
            )

            llm_context = {
                "weather_summary": "위험",
                "temperature_c": weather_info.temp,
                "precipitation_prob": weather_info.rain_prob,
                "time_of_day": "day" if weather_info.is_daytime else "night",
            }

            llm_result = None
            try:
                llm_result = choose_exercises_with_llm_for_today(
                    exercises=exercises,
                    user_profile=user_profile,
                    context=llm_context,
                    user_id=user_id,
                    top_k=8,
                    top_n=3,
                )
            except Exception as e:
                # LLM 추천 실패 시 사용자에게 알려주기 위한 fallback
                llm_result = None

            if llm_result and llm_result.get("ranked"):
                for ex in llm_result.get("ranked", []):
                    exercise_videos.append(
                        ExerciseVideoResponse(
                            name=ex.get("Name", ""),
                            체력항목=ex.get("체력항목", ""),
                            운동도구=ex.get("운동도구", ""),
                            신체부위=ex.get("신체부위", ""),
                            혼자여부=ex.get("혼자여부", ""),
                            url=ex.get("url", ""),
                            info=f"체력항목: {ex.get('체력항목')} | "
                                 f"도구: {ex.get('운동도구')} | "
                                 f"부위: {ex.get('신체부위')}",
                            reason=ex.get("why"),
                            cautions=ex.get("cautions"),
                            next_step=ex.get("next_step"),
                        )
                    )
            else:
                exercise_videos.append(
                    ExerciseVideoResponse(
                        name="",
                        체력항목="",
                        운동도구="",
                        신체부위="",
                        혼자여부="",
                        url="",
                        info="LLM 운동 추천을 가져오지 못했습니다.",
                    )
                )

    return RecommendResponse(
        recommendations=facilities,
        weather_info=weather_info,
        exercise_videos=exercise_videos,
    )
