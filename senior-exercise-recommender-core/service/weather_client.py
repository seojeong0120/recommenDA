# service/weather_client.py
"""
통합 날씨 정보 조회 모듈
기상청 API를 사용하여 WeatherInfo 타입에 맞는 날씨 정보를 반환
"""
import os
import datetime as dt
from typing import Dict, Any, Tuple, Optional
from pathlib import Path
import requests
from dotenv import load_dotenv
from recommender.types import WeatherInfo

# .env 파일 로드
BASE_DIR = Path(__file__).parent.parent
load_dotenv(BASE_DIR / ".env")

KMA_BASE_URL = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0"
KMA_SERVICE_KEY = os.getenv("KMA_SERVICE_KEY")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

# 단기예보 발표 시각
VILAGE_BASE_HOURS: list[int] = [2, 5, 8, 11, 14, 17, 20, 23]


def lat_lon_to_grid(lat: float, lon: float) -> Tuple[int, int]:
    """
    위도/경도를 기상청 격자 좌표(nx, ny)로 변환
    
    기상청 격자 좌표 변환 공식 사용
    """
    RE = 6371.00877  # 지구 반경(km)
    GRID = 5.0  # 격자 간격(km)
    SLAT1 = 30.0  # 투영 위도1(degree)
    SLAT2 = 60.0  # 투영 위도2(degree)
    OLON = 126.0  # 기준점 경도(degree)
    OLAT = 38.0  # 기준점 위도(degree)
    XO = 43  # 기준점 X좌표(GRID)
    YO = 136  # 기준점 Y좌표(GRID)
    
    import math
    
    DEGRAD = math.pi / 180.0
    RADDEG = 180.0 / math.pi
    
    re = RE / GRID
    slat1 = SLAT1 * DEGRAD
    slat2 = SLAT2 * DEGRAD
    olon = OLON * DEGRAD
    olat = OLAT * DEGRAD
    
    sn = math.tan(math.pi * 0.25 + slat2 * 0.5) / math.tan(math.pi * 0.25 + slat1 * 0.5)
    sn = math.log(math.cos(slat1) / math.cos(slat2)) / math.log(sn)
    sf = math.tan(math.pi * 0.25 + slat1 * 0.5)
    sf = math.pow(sf, sn) * math.cos(slat1) / sn
    ro = math.tan(math.pi * 0.25 + olat * 0.5)
    ro = re * sf / math.pow(ro, sn)
    
    ra = math.tan(math.pi * 0.25 + (lat) * DEGRAD * 0.5)
    ra = re * sf / math.pow(ra, sn)
    theta = lon * DEGRAD - olon
    if theta > math.pi:
        theta -= 2.0 * math.pi
    if theta < -math.pi:
        theta += 2.0 * math.pi
    theta *= sn
    
    nx = int(ra * math.sin(theta) + XO + 0.5)
    ny = int(ro - ra * math.cos(theta) + YO + 0.5)
    
    return nx, ny


def _get_ultra_nowcast_base_datetime(now: Optional[dt.datetime] = None) -> Tuple[str, str]:
    """초단기실황 base_date, base_time 계산"""
    if now is None:
        now = dt.datetime.now()
    now_minus_10 = now - dt.timedelta(minutes=10)
    base_date = now_minus_10.strftime("%Y%m%d")
    base_time = now_minus_10.strftime("%H00")
    return base_date, base_time


def fetch_kma_ultra_nowcast(lat: float, lon: float) -> Optional[Dict[str, Any]]:
    """기상청 초단기실황 조회 (공개 함수)"""
    if not KMA_SERVICE_KEY:
        return None
    
    try:
        nx, ny = lat_lon_to_grid(lat, lon)
        base_date, base_time = _get_ultra_nowcast_base_datetime()
        
        params = {
            "serviceKey": KMA_SERVICE_KEY,
            "numOfRows": 100,
            "pageNo": 1,
            "dataType": "JSON",
            "base_date": base_date,
            "base_time": base_time,
            "nx": nx,
            "ny": ny,
        }
        url = f"{KMA_BASE_URL}/getUltraSrtNcst"
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        
        items = data.get("response", {}).get("body", {}).get("items", {}).get("item", [])
        if not items:
            return None
        
        weather = {}
        for item in items:
            category = item.get("category")
            value_str = item.get("obsrValue", "0")
            try:
                value = float(value_str)
            except (ValueError, TypeError):
                value = 0.0
            weather[category] = value
        
        return weather
    except Exception as e:
        print(f"기상청 초단기실황 API 호출 실패: {e}")
        return None


def _fetch_kma_forecast(lat: float, lon: float) -> Optional[Dict[str, Any]]:
    """기상청 단기예보에서 강수 확률 조회"""
    if not KMA_SERVICE_KEY:
        return None
    
    try:
        nx, ny = lat_lon_to_grid(lat, lon)
        now = dt.datetime.now()
        now_minus_45 = now - dt.timedelta(minutes=45)
        h = now_minus_45.hour
        
        candidates = [bh for bh in VILAGE_BASE_HOURS if bh <= h]
        if candidates:
            base_hour = max(candidates)
            base_date = now_minus_45.date()
        else:
            base_hour = 23
            base_date = now_minus_45.date() - dt.timedelta(days=1)
        
        base_date_str = base_date.strftime("%Y%m%d")
        base_time_str = f"{base_hour:02d}00"
        
        params = {
            "serviceKey": KMA_SERVICE_KEY,
            "numOfRows": 1000,
            "pageNo": 1,
            "dataType": "JSON",
            "base_date": base_date_str,
            "base_time": base_time_str,
            "nx": nx,
            "ny": ny,
        }
        url = f"{KMA_BASE_URL}/getVilageFcst"
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        
        items = data.get("response", {}).get("body", {}).get("items", {}).get("item", [])
        if not items:
            return None
        
        # 현재 시간 이후의 POP(강수 확률) 찾기
        today_str = dt.date.today().strftime("%Y%m%d")
        current_hour = now.hour
        next_fcst_time = f"{(current_hour + 1):02d}00"
        
        pop_list = []
        for item in items:
            if (item.get("fcstDate") == today_str and 
                item.get("category") == "POP" and
                item.get("fcstTime", "0000") >= next_fcst_time):
                try:
                    pop = float(item.get("fcstValue", 0))
                    if pop >= 0:
                        pop_list.append(pop)
                except (ValueError, TypeError):
                    continue
        
        # 평균 강수 확률 반환 (0.0~1.0으로 정규화)
        avg_pop = (sum(pop_list) / len(pop_list) / 100.0) if pop_list else 0.0
        
        return {"POP": avg_pop}
    except Exception as e:
        print(f"기상청 단기예보 API 호출 실패: {e}")
        return None


def _fetch_openweather_air_quality(lat: float, lon: float) -> Optional[Dict[str, Any]]:
    """OpenWeatherMap 대기질 API 호출"""
    if not OPENWEATHER_API_KEY:
        return None
    
    try:
        url = "http://api.openweathermap.org/data/2.5/air_pollution"
        params = {
            "lat": lat,
            "lon": lon,
            "appid": OPENWEATHER_API_KEY,
        }
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            components = data.get("list", [{}])[0].get("components", {})
            pm10 = components.get("pm10", 50.0)
            return {"pm10": pm10}
    except Exception as e:
        print(f"OpenWeather 대기질 API 호출 실패: {e}")
    
    return None


def fetch_weather(lat: float, lon: float) -> WeatherInfo:
    """
    위도/경도를 받아서 WeatherInfo 타입의 날씨 정보를 반환
    
    우선순위:
    1. 기상청 초단기실황 (기온, 강수형태)
    2. 기상청 단기예보 (강수 확률)
    3. OpenWeather 대기질 API (미세먼지)
    """
    current_hour = dt.datetime.now().hour
    is_daytime = 6 <= current_hour < 20
    
    # 기본값
    temp = 20.0
    rain_prob = 0.0
    pm10 = 50.0
    
    # 1. 기상청 초단기실황 조회 (기온, 강수형태)
    kma_nowcast = fetch_kma_ultra_nowcast(lat, lon)
    if kma_nowcast:
        temp = kma_nowcast.get("T1H", temp)  # 현재 기온
        
        # 강수형태(PTY)를 바탕으로 강수 확률 추정
        pty = int(kma_nowcast.get("PTY", 0))
        if pty != 0:  # 비/눈이 오고 있으면
            rain_prob = 0.8
        else:
            # 1시간 강수량(RN1) 확인
            rn1 = kma_nowcast.get("RN1", 0.0)
            if rn1 > 0:
                rain_prob = 0.7
    
    # 2. 기상청 단기예보에서 강수 확률 확인 (더 정확함)
    kma_forecast = _fetch_kma_forecast(lat, lon)
    if kma_forecast and "POP" in kma_forecast:
        rain_prob = max(rain_prob, kma_forecast["POP"])
    
    # 3. OpenWeather 대기질 API 조회
    air_quality = _fetch_openweather_air_quality(lat, lon)
    if air_quality:
        pm10 = air_quality.get("pm10", pm10)
    
    return {
        "temp": temp,
        "rain_prob": rain_prob,
        "pm10": pm10,
        "is_daytime": is_daytime,
    }


def evaluate_weather_danger(
    weather: Dict[str, Any],
    has_chronic_disease: bool = False,
    air_quality_risky: bool = False,
) -> Tuple[bool, str]:
    """
    노인(65세 이상) 기준 '밖에 나가기 위험한지' 여부와 문구 리턴.
    기상청 날씨 데이터를 기반으로 평가.
    """
    reasons: list[str] = []
    
    # 0) 강수형태: 비/눈이면 기본적으로 위험
    pty = int(weather.get("PTY", 0))
    if pty != 0:
        reasons.append("비나 눈이 오는")
    
    # 1) 바람
    wsd = float(weather.get("WSD", 0.0))
    if wsd >= 14.0:
        reasons.append("강풍 주의보 수준의 매우 강한 바람이 부는")
    elif wsd >= 9.0:
        reasons.append("노인에게 낙상 위험이 큰 강한 바람이 부는")
    
    # 2) 기온
    temp = float(weather.get("T1H", 20.0))
    
    if temp >= 33.0:
        reasons.append("폭염주의보 수준의 매우 더운")
    elif temp >= 30.0:
        reasons.append("노인에게 열사병 위험이 커지는 더운")
    
    if temp <= -12.0:
        reasons.append("한파주의보 수준의 매우 추운")
    elif temp <= -5.0:
        reasons.append("노인에게 저체온·결빙 위험이 커지는 추운")
    
    # 3) 바람 + 저온
    if temp <= 0 and wsd >= 5.0:
        reasons.append("바람과 추위가 함께해 체감온도가 크게 낮은")
    
    # 4) 낙상 위험
    if pty != 0 and (temp <= 2.0 or wsd >= 5.0):
        reasons.append("노인에게 미끄럼·낙상 위험이 큰")
    
    # 5) 대기오염
    if air_quality_risky:
        reasons.append("대기오염으로 실외 활동이 부담스러운")
    
    # 6) 기저질환
    if has_chronic_disease:
        if 28.0 <= temp < 30.0:
            reasons.append("기저질환이 있는 노인에게는 더위가 부담되는")
        if 0.0 < temp <= 3.0:
            reasons.append("기저질환이 있는 노인에게는 추위가 부담되는")
    
    # 최종 판단
    if not reasons:
        return False, "노인이 나들이하기에 비교적 안전한 날씨"
    
    reasons = list(dict.fromkeys(reasons))
    reason_text = " / ".join(reasons) + " 날씨"
    return True, reason_text
