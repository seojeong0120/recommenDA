"""
기상청 API를 통한 날씨 정보 조회 및 위험 평가 모듈
"""
import os
import datetime as dt
from typing import Tuple, Dict, Any, List
from pathlib import Path
import requests
from dotenv import load_dotenv

# .env 파일 로드 (프로젝트 루트 기준)
BASE_DIR = Path(__file__).parent.parent
load_dotenv(BASE_DIR / ".env")

KMA_BASE_URL = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0"
KMA_SERVICE_KEY = os.getenv("KMA_SERVICE_KEY")
# 경도위도 하드코딩 (서울 기준)
KMA_NX = 60   # 경도
KMA_NY = 127  # 위도

# 단기예보(getVilageFcst) 발표 시각 (정시)
VILAGE_BASE_HOURS: List[int] = [2, 5, 8, 11, 14, 17, 20, 23]


# ============================================================================
# 초단기실황(현재 날씨) 조회
# ============================================================================

def _get_ultra_nowcast_base_datetime(
    now: dt.datetime | None = None
) -> Tuple[str, str]:
    """
    초단기실황(base_date, base_time) 계산
    - 문서 기준: 매시간 정시에 생성되고 10분 이후부터 사용 가능.
    - 구현: 현재 시각에서 10분 빼고, 그 시각의 시(hour)를 base_time으로 사용.
    """
    if now is None:
        now = dt.datetime.now()  # 서버 로컬 타임 (실제 서비스면 KST 타임존 맞추는 게 좋음)
    now_minus_10 = now - dt.timedelta(minutes=10)
    base_date = now_minus_10.strftime("%Y%m%d")
    base_time = now_minus_10.strftime("%H00")  # e.g. "0600"
    return base_date, base_time


def fetch_ultra_nowcast(
    service_key: str | None = None,
    nx: int = KMA_NX,
    ny: int = KMA_NY,
) -> dict:
    """
    기상청 초단기실황(getUltraSrtNcst) 조회해서
    {category: value} 형태의 딕셔너리로 반환.

    주요 category 예:
    - T1H: 기온(℃)
    - RN1: 1시간 강수량(mm)
    - PTY: 강수형태 코드 (0: 없음, 1: 비, 2: 비/눈, 3: 눈, 5/6/7: 빗방울, 눈날림 등)
    - REH: 습도(%)
    - WSD: 풍속(m/s)
    """
    if service_key is None:
        service_key = KMA_SERVICE_KEY
    if not service_key:
        raise ValueError("KMA_SERVICE_KEY를 환경변수나 인자로 설정해주세요.")

    base_date, base_time = _get_ultra_nowcast_base_datetime()
    params = {
        "serviceKey": service_key,
        "numOfRows": 100,
        "pageNo": 1,
        "dataType": "JSON",
        "base_date": base_date,
        "base_time": base_time,
        "nx": nx,
        "ny": ny,
    }
    url = f"{KMA_BASE_URL}/getUltraSrtNcst"
    resp = requests.get(url, params=params, timeout=5)
    resp.raise_for_status()
    data = resp.json()

    # 응답 구조: response -> body -> items -> item(list)
    items = data["response"]["body"]["items"]["item"]
    weather = {}
    for item in items:
        category = item["category"]
        value_str = item["obsrValue"]
        # 숫자 변환 시도
        try:
            value = float(value_str)
        except ValueError:
            value = value_str
        weather[category] = value

    return weather


# ============================================================================
# 단기예보(오늘 하루 예보) 기반 최고/최저 기온·풍속 조회
# ============================================================================

def _get_vilage_fcst_base_datetime(
    now: dt.datetime | None = None,
) -> Tuple[str, str]:
    """
    단기예보(getVilageFcst)용 base_date, base_time 계산.

    - 단기예보는 02, 05, 08, 11, 14, 17, 20, 23시에 발표됨.
    - 약간의 발표 지연을 고려해 현재 시각에서 45분을 빼고,
      그 시점 기준 가장 가까운 과거 발표시각을 선택.
    """
    if now is None:
        now = dt.datetime.now()

    now_minus_45 = now - dt.timedelta(minutes=45)
    h = now_minus_45.hour

    # 현재 시점 기준 사용할 발표시각(hour) 선택
    candidates = [bh for bh in VILAGE_BASE_HOURS if bh <= h]
    if candidates:
        base_hour = max(candidates)
        base_date = now_minus_45.date()
    else:
        # 오늘 새벽 2시 발표 이전이라면, 전날 23시 발표를 사용
        base_hour = 23
        base_date = now_minus_45.date() - dt.timedelta(days=1)

    base_date_str = base_date.strftime("%Y%m%d")
    base_time_str = f"{base_hour:02d}00"  # "0200", "1400" 같은 형식
    return base_date_str, base_time_str


def fetch_vilage_forecast(
    service_key: str | None = None,
    nx: int = KMA_NX,
    ny: int = KMA_NY,
) -> List[Dict[str, Any]]:
    """
    기상청 단기예보(getVilageFcst) 호출.
    API에서 items 리스트를 그대로 반환.
    """
    if service_key is None:
        service_key = KMA_SERVICE_KEY
    if not service_key:
        raise ValueError("KMA_SERVICE_KEY를 환경변수나 인자로 설정해주세요.")

    base_date, base_time = _get_vilage_fcst_base_datetime()

    params = {
        "serviceKey": service_key,
        "numOfRows": 1000,       # 넉넉하게
        "pageNo": 1,
        "dataType": "JSON",
        "base_date": base_date,
        "base_time": base_time,
        "nx": nx,
        "ny": ny,
    }

    url = f"{KMA_BASE_URL}/getVilageFcst"
    resp = requests.get(url, params=params, timeout=5)
    resp.raise_for_status()
    data = resp.json()

    items: List[Dict[str, Any]] = data["response"]["body"]["items"]["item"]
    return items


def _is_missing_value(value: float) -> bool:
    """
    기상청 단기예보/초단기예보 공통 규칙:
    +900 이상, -900 이하는 결측값으로 처리.
    """
    return abs(value) >= 900.0


def compute_today_extremes_from_items(
    items: List[Dict[str, Any]],
    today: dt.date | None = None,
) -> Dict[str, Any]:
    """
    단기예보 items에서 'today'에 해당하는 값만 모아서
    - 최고기온 / 최저기온 (tmax / tmin)
        * 우선 TMX / TMN 사용
        * 없으면 TMP(1시간 기온)의 max/min으로 대체
    - 최고풍속 / 최저풍속 (wmax / wmin)
        * 오늘 날짜의 WSD(풍속, m/s)에서 max/min

    ※ WSD가 코드값(1~3)이 되는 건 글피/그글피 같은 연장구간이라
       오늘(today) 기준에는 실수값(m/s)이라고 가정.
    """
    if today is None:
        today = dt.date.today()
    today_str = today.strftime("%Y%m%d")

    tmax_list: List[float] = []
    tmin_list: List[float] = []
    tmp_list: List[float] = []
    wsd_list: List[float] = []

    for item in items:
        if item.get("fcstDate") != today_str:
            continue

        category = item.get("category")
        value_str = item.get("fcstValue")

        try:
            value = float(value_str)
        except (TypeError, ValueError):
            continue

        # 결측값(+900 이상, -900 이하는 skip)
        if _is_missing_value(value):
            continue

        if category == "TMX":
            tmax_list.append(value)
        elif category == "TMN":
            tmin_list.append(value)
        elif category == "TMP":
            tmp_list.append(value)
        elif category == "WSD":
            wsd_list.append(value)

    # 1) TMX/TMN이 있으면 그걸 우선 사용
    #    (발표시각에 따라 오늘 TMX/TMN이 없을 수 있으므로)
    if (not tmax_list or not tmin_list) and tmp_list:
        # 오늘에 대해 TMP가 있다면, 거기서 대체값 계산
        if not tmax_list:
            tmax_list = [max(tmp_list)]
        if not tmin_list:
            tmin_list = [min(tmp_list)]

    tmax = max(tmax_list) if tmax_list else None
    tmin = min(tmin_list) if tmin_list else None
    wmax = max(wsd_list) if wsd_list else None
    wmin = min(wsd_list) if wsd_list else None

    return {
        "tmax": tmax,
        "tmin": tmin,
        "wmax": wmax,
        "wmin": wmin,
    }


def fetch_today_extremes(
    service_key: str | None = None,
    nx: int = KMA_NX,
    ny: int = KMA_NY,
    target_date: dt.date | None = None,
) -> Dict[str, Any]:
    """
    한 번에:
    1) 단기예보 호출
    2) 오늘 날짜 기준 최고/최저 기온·풍속 계산

    target_date는 극값 계산 시 사용할 날짜 (기본값: 오늘).
    """
    items = fetch_vilage_forecast(
        service_key=service_key,
        nx=nx,
        ny=ny,
    )
    if target_date is None:
        target_date = dt.date.today()
    return compute_today_extremes_from_items(items, today=target_date)


# ============================================================================
# 노인 기준 위험 평가 로직
# ============================================================================

def evaluate_weather_danger(
    weather: Dict[str, Any],
    has_chronic_disease: bool = False,
    air_quality_risky: bool = False,
) -> Tuple[bool, str]:
    """
    노인(65세 이상) 기준 '밖에 나가기 위험한지' 여부와 문구 리턴.
    - True/False, "폭염 위험 / 강풍으로 낙상 위험" 등의 설명 문구.
    - 미세먼지는 air_quality_risky 플래그로 외부에서 판단해 넣는 것을 가정.

    근거 요약:
    - 고령자는 체온 조절 기능 저하로 일반 성인보다 낮은 기온/덥기에서도
      열사병·저체온 위험이 증가함.
    - 낙상은 노인 사망·장애의 주요 원인으로, 비·눈·강풍, 결빙 가능 온도에서
      실외 보행이 특히 위험해짐.
    """
    reasons: List[str] = []

    # 0) 강수형태: 비/눈이면 기본적으로 위험
    pty = int(weather.get("PTY", 0))
    if pty != 0:
        reasons.append("비나 눈이 오는")

    # 1) 바람: 주의보(14m/s)보다는 낮추되, 낙상 위험을 반영해 보수적으로 설정
    # - 연구·가이드에서 노인은 균형 능력 저하로 바람과 미끄러운 노면에 더 취약.
    wsd = float(weather.get("WSD", 0.0))
    if wsd >= 14.0:
        # 강풍주의보 수준
        reasons.append("강풍 주의보 수준의 매우 강한 바람이 부는")
    elif wsd >= 9.0:
        # 일반 강풍주의보 기준보다 한 단계 낮지만, 노인 낙상 위험 관점에서 위험 처리
        reasons.append("노인에게 낙상 위험이 큰 강한 바람이 부는")

    # 2) 기온(현재기온 T1H 기준, 단기적 외출 안전 판단용)
    temp = float(weather.get("T1H", 20.0))

    # 더위 구간 설정 (노인 기준, 보수적):
    # - 33℃ 이상: 폭염주의보 수준 → 매우 위험.
    # - 30~32℃: 고령자는 열 관련 질환 위험이 유의하게 증가하므로 위험 처리.
    if temp >= 33.0:
        reasons.append("폭염주의보 수준의 매우 더운")
    elif temp >= 30.0:
        reasons.append("노인에게 열사병 위험이 커지는 더운")

    # 추위 구간 설정 (노인 기준, 보수적):
    # - 기상 한파주의보는 보통 아침 최저 -12℃ 이하 등이나,
    #   노인은 더 높은 온도에서도 저체온·심혈관 부담이 증가함.
    # - -12℃ 이하: 한파주의보 수준 → 매우 위험.
    # - -5℃ 이하: 외출 시 결빙·낙상·저체온 위험이 커지는 구간으로 간주.
    if temp <= -12.0:
        reasons.append("한파주의보 수준의 매우 추운")
    elif temp <= -5.0:
        reasons.append("노인에게 저체온·결빙 위험이 커지는 추운")

    # 3) 바람 + 저온(체감온도 개념, 간단히 조합 규칙으로 처리)
    # - 바람과 추위가 겹치면 체감온도가 더 낮아지고, 낙상·저체온 위험이 증가.
    if temp <= 0 and wsd >= 5.0:
        reasons.append("바람과 추위가 함께해 체감온도가 크게 낮은")

    # 4) 낙상 위험: 비/눈 + 저온 또는 강풍
    # - 노인의 바깥 낙상은 비·눈·얼음·바람과 강하게 연관됨.
    if pty != 0 and (temp <= 2.0 or wsd >= 5.0):
        reasons.append("노인에게 미끄럼·낙상 위험이 큰")

    # 5) 기저질환/대기오염에 따른 보수적 플래그
    # - 심혈관·호흡기 등 기저질환이 있으면 더위·추위·오염에 더 취약.
    # - air_quality_risky는 외부 PM2.5 API로 (예: '나쁨' 이상) 판단 후 True로 전달.
    if air_quality_risky:
        reasons.append("대기오염으로 실외 활동이 부담스러운")

    # 기저질환이 있는 노인일 경우, 중간 수준 조건도 위험으로 상향
    if has_chronic_disease:
        # 예: 기온 28~29도 구간을 '주의'로 끌어올림
        if 28.0 <= temp < 30.0:
            reasons.append("기저질환이 있는 노인에게는 더위가 부담되는")
        if 0.0 < temp <= 3.0:
            reasons.append("기저질환이 있는 노인에게는 추위가 부담되는")

    # 최종 판단
    if not reasons:
        return False, "노인이 나들이하기에 비교적 안전한 날씨"

    # 중복된 이유는 정리
    reasons = list(dict.fromkeys(reasons))
    reason_text = " / ".join(reasons) + " 날씨"
    return True, reason_text
