"""
운동 알림 메시지 생성 서비스
- 날씨가 위험할 때 실내 운동 영상을 추천하는 알림 생성
"""
import sys
import datetime as dt
from pathlib import Path

# 직접 실행 시 프로젝트 루트를 경로에 추가 (import 전에 실행)
_is_main = __name__ == "__main__"
if _is_main:
    PROJECT_ROOT = Path(__file__).parent.parent
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))

# import 처리 (직접 실행 시와 모듈로 import 시 모두 지원)
try:
    from .weather_client import fetch_kma_ultra_nowcast, evaluate_weather_danger
    from ..recommender.exercise_recommender import load_exercises, choose_exercise_for_today
except ImportError:
    # 직접 실행 시 상대 import가 실패하면 절대 import 사용
    from service.weather_client import fetch_kma_ultra_nowcast, evaluate_weather_danger
    from recommender.exercise_recommender import load_exercises, choose_exercise_for_today


def build_notification_message(
    user_id: str = "default_user",
    today_date: dt.date | None = None,
) -> str | None:
    """
    1) 오늘 초단기실황 조회
    2) 위험한 날씨이면 운동 영상 추천 + 알림 문장 생성
    3) 위험하지 않으면 None 반환 (또는 다른 문장으로 바꿔도 됨)
    """
    # 1) 날씨 조회 (서울 기본값, 실제로는 위치 정보 필요)
    lat, lon = 37.5665, 126.9780  # 서울 기본값
    weather = fetch_kma_ultra_nowcast(lat, lon)
    if not weather:
        return None
    is_dangerous, weather_text = evaluate_weather_danger(weather)

    if not is_dangerous:
        # 위험하지 않은 날이면 알림 안 보내거나, 다른 문구를 써도 됨.
        # 여기서는 None을 반환하도록 구현.
        return None

    # 2) 운동 영상 추천
    exercises = load_exercises()
    if not exercises:
        return None

    exercise = choose_exercise_for_today(
        exercises, user_id=user_id, today_date=today_date
    )
    url = exercise.get("url")
    name = exercise.get("Name", "운동")

    # 3) 알림 문장 생성
    # weather_text 예: "비나 눈이 오는 / 강한 바람이 부는 날씨"
    message = (
        f"오늘은 {weather_text}입니다. "
        f"밖에 나가지 말고 집 안에서 운동하는 것이 좋겠어요. "
        f"{url} 이 운동({name})을 하는 것을 추천드릴게요."
    )

    return message


# ==========================
# 직접 실행
# ==========================
if __name__ == "__main__":
    # 사용자 ID를 명령행 인자로 받거나 기본값 사용
    user_id = sys.argv[1] if len(sys.argv) > 1 else "default_user"
    
    # 운동 추천 이력 관리를 위한 날짜 설정 (선택사항)
    import os
    test_date_str = None
    if len(sys.argv) > 2:
        test_date_str = sys.argv[2]
    if not test_date_str:
        test_date_str = os.getenv("TEST_DATE")
    
    test_date = None
    if test_date_str:
        try:
            test_date = dt.datetime.strptime(test_date_str, "%Y-%m-%d").date()
            print(f"[날짜 지정] {test_date}")
        except ValueError:
            print(f"날짜 형식 오류: {test_date_str} (예: 2024-11-25)")
            sys.exit(1)
    
    print(f"[사용자 ID: {user_id}] 알림 메시지 생성 중...")
    print("-" * 50)
    
    try:
        # 날씨 정보 조회 및 출력
        from service.weather_client import fetch_kma_ultra_nowcast
        lat, lon = 37.5665, 126.9780  # 서울 기본값
        weather = fetch_kma_ultra_nowcast(lat, lon)
        if not weather:
            print("날씨 정보 조회 실패")
            sys.exit(1)
        
        # 주요 날씨 정보 출력
        temp = weather.get("T1H", "N/A")  # 현재 기온 (초단기실황)
        pty = weather.get("PTY", "N/A")
        wsd = weather.get("WSD", "N/A")
        reh = weather.get("REH", "N/A")
        rn1 = weather.get("RN1", "N/A")
        
        # 단기예보는 제거 (필요시 별도 조회)
        tmax = None
        tmin = None
        wmax = None
        wmin = None
        
        # 강수형태 코드를 텍스트로 변환
        pty_text = {
            0: "없음",
            1: "비",
            2: "비/눈",
            3: "눈",
            4: "소나기",
            5: "빗방울",
            6: "빗방울눈날림",
            7: "눈날림"
        }.get(int(pty) if isinstance(pty, (int, float)) else 0, f"코드:{pty}")
        
        print(f"[날씨 정보]")
        print(f"  현재 기온: {temp}℃ (초단기실황)")
        if tmax is not None and tmin is not None:
            print(f"  오늘 예상 기온: {tmin}℃ ~ {tmax}℃ (단기예보)")
        print(f"  강수형태: {pty_text} (코드: {pty})")
        print(f"  현재 풍속: {wsd} m/s")
        if wmax is not None and wmin is not None:
            print(f"  오늘 예상 풍속: {wmin} ~ {wmax} m/s")
        print(f"  습도: {reh}%")
        if rn1 != "N/A" and float(rn1) > 0:
            print(f"  강수량: {rn1} mm")
        print("-" * 50)
        
        msg = build_notification_message(user_id=user_id, today_date=test_date)
        if msg:
            print(msg)
        else:
            print("오늘은 나가도 괜찮은 날씨입니다. (위험 기준 이하)")
    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
