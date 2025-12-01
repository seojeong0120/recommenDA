"""
운동 영상 기반 추천 시스템
- 운동 영상 로딩 및 부위별 그룹화
- 사용자별 운동 추천 이력 관리
- 매일 신체부위를 번갈아가며 추천
"""
import json
import random
import datetime as dt
from pathlib import Path
from typing import List, Dict
import os

# 데이터 파일 경로
BASE_DIR = Path(os.path.dirname(os.path.dirname(__file__)))
EXERCISE_FILE = BASE_DIR / "data" / "processed" / "exercise_video.json"
HISTORY_FILE = BASE_DIR / "db" / "exercise_history.json"  # 나중에 SQL로 전환 예정


def load_exercises(path: Path = EXERCISE_FILE) -> List[Dict]:
    """
    exercise_video.json 로딩.
    구조 예:
    [
        {
            "Name": "척추 스트레칭",
            "체력항목": "유연성",
            "운동도구": "폼롤러",
            "신체부위": "등/허리",
            "혼자여부": "y",
            "url": "https://..."
        },
        ...
    ]
    """
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def group_exercises_by_body_part(exercises: List[Dict]) -> Dict[str, List[Dict]]:
    """
    신체부위 기준으로 운동을 묶는다.
    - 신체부위가 "/", "//", "" 등 애매하면 "기타"로 뭉뚱그림.
    - "등/허리"처럼 슬래시가 있는 경우는 split해서 각 부위별로 포함시킴.
    """
    grouped: Dict[str, List[Dict]] = {}
    for ex in exercises:
        body = ex.get("신체부위", "").strip()
        if not body or body in {"/", "//"}:
            body_parts = ["기타"]
        else:
            # "/"로 split하고 공백 제거
            body_parts = [b.strip() for b in body.split("/") if b.strip()]
            if not body_parts:
                body_parts = ["기타"]
        
        # 각 부위별로 운동 추가
        for part in body_parts:
            grouped.setdefault(part, []).append(ex)
    return grouped


def load_history(path: Path = HISTORY_FILE) -> Dict:
    """사용자별 운동 추천 이력 로딩"""
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}


def save_history(history: Dict, path: Path = HISTORY_FILE) -> None:
    """사용자별 운동 추천 이력 저장"""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def choose_exercise_for_today(
    exercises: List[Dict],
    user_id: str = "default_user",
    today_date: dt.date | None = None,
) -> Dict:
    """
    - 매일 '신체부위'를 번갈아가며 추천하는 전략.
    - 로직:
      1) history에서 해당 user의 어제 기록(last_body, last_date, today_exercise) 확인
      2) 오늘 이미 추천한 적 있으면 같은 운동 그대로 리턴 (하루에 여러 번 호출해도 동일)
      3) 아니라면:
         - 어제 사용한 부위를 제외한 부위 중에서 랜덤으로 1개 선택
         - 그 부위 안에서 랜덤으로 1개 영상 선택
         - history에 오늘 날짜, 부위, 추천한 영상 저장
    """
    grouped = group_exercises_by_body_part(exercises)
    body_parts = list(grouped.keys())

    if not body_parts:
        raise ValueError("운동 데이터에 '신체부위' 정보가 없습니다.")

    history = load_history()
    today = (today_date if today_date else dt.date.today()).isoformat()
    user_hist = history.get(user_id, {})
    last_date = user_hist.get("last_date")
    last_body = user_hist.get("last_body")
    today_ex = user_hist.get("today_exercise")

    # 1) 오늘 이미 추천한 운동이 있으면 그대로 사용
    if last_date == today and today_ex:
        return today_ex

    # 2) 어제와 다른 부위 선택 (가능하면)
    candidate_bodies = [b for b in body_parts if b != last_body] or body_parts
    chosen_body = random.choice(candidate_bodies)

    # 3) 그 부위 안에서 랜덤으로 1개 운동 선택
    chosen_ex = random.choice(grouped[chosen_body])

    # 4) 히스토리 업데이트
    history[user_id] = {
        "last_date": today,
        "last_body": chosen_body,
        "today_exercise": chosen_ex,
    }
    save_history(history)

    return chosen_ex