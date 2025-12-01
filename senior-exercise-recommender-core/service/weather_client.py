# service/weather_client.py
import os
import requests
from datetime import datetime
from typing import Optional
from recommender.types import WeatherInfo


def fetch_weather(lat: float, lon: float) -> WeatherInfo:
    """
    외부 날씨/대기질 API를 호출하여 WeatherInfo 반환.
    실패 시 기본값으로 fallback.
    
    현재는 OpenWeatherMap과 한국 대기질 API를 사용하는 예시를 제공하지만,
    실제 API 키가 없으면 기본값 반환.
    """
    try:
        # OpenWeatherMap API 예시 (실제 API 키 필요)
        api_key = os.getenv("OPENWEATHER_API_KEY")
        if api_key:
            weather_data = _fetch_openweather(lat, lon, api_key)
            air_data = _fetch_air_quality_kr(lat, lon)
            
            if weather_data and air_data:
                current_hour = datetime.now().hour
                is_daytime = 6 <= current_hour < 20
                
                return {
                    "temp": weather_data.get("temp", 20.0),
                    "rain_prob": weather_data.get("rain_prob", 0.0),
                    "pm10": air_data.get("pm10", 50.0),
                    "is_daytime": is_daytime,
                }
    except Exception as e:
        print(f"날씨 API 호출 실패: {e}")
    
    # Fallback: 기본값 반환
    current_hour = datetime.now().hour
    return {
        "temp": 20.0,
        "rain_prob": 0.0,
        "pm10": 50.0,
        "is_daytime": 6 <= current_hour < 20,
    }


def _fetch_openweather(lat: float, lon: float, api_key: str) -> Optional[dict]:
    """
    OpenWeatherMap API 호출.
    """
    try:
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            "lat": lat,
            "lon": lon,
            "appid": api_key,
            "units": "metric",
            "lang": "kr",
        }
        response = requests.get(url, params=params, timeout=5)
        if response.status_code == 200:
            data = response.json()
            # 강수 확률 추출 (현재 날씨 기준)
            rain_prob = 0.0
            if "rain" in data:
                rain_prob = 0.8  # 비가 오고 있다면
            elif "weather" in data and data["weather"]:
                weather_main = data["weather"][0].get("main", "").lower()
                if "rain" in weather_main or "drizzle" in weather_main:
                    rain_prob = 0.7
            
            return {
                "temp": data.get("main", {}).get("temp", 20.0),
                "rain_prob": rain_prob,
            }
    except Exception as e:
        print(f"OpenWeather API 호출 실패: {e}")
    return None


def _fetch_air_quality_kr(lat: float, lon: float) -> Optional[dict]:
    """
    한국 대기질 API 호출 (예: 에어코리아 또는 OpenWeather Air Pollution API).
    """
    try:
        # 예시: OpenWeather Air Pollution API
        api_key = os.getenv("OPENWEATHER_API_KEY")
        if api_key:
            url = "http://api.openweathermap.org/data/2.5/air_pollution"
            params = {
                "lat": lat,
                "lon": lon,
                "appid": api_key,
            }
            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                components = data.get("list", [{}])[0].get("components", {})
                pm10 = components.get("pm10", 50.0)
                return {"pm10": pm10}
    except Exception as e:
        print(f"대기질 API 호출 실패: {e}")
    
    # 기본값
    return {"pm10": 50.0}

