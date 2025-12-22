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
from recommender.llm.schemas import ExerciseCandidate

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

def _split_body_parts(body: str) -> List[str]:
    body = (body or "").strip()
    if not body or body in {"/", "//"}:
        return ["기타"]
    parts = [b.strip() for b in body.split("/") if b.strip()]
    return parts or ["기타"]

def generate_exercise_candidates(
    exercises: List[Dict],
    user_profile: Dict,
    context: Dict,
    k: int = 8,
    last_body: str | None = None,
) -> List[ExerciseCandidate]:
    """
    룰/스코어 기반 Top-K 후보 생성
    - LLM에 넘기기 전에 '합리적인 후보군'으로 제한하기 위한 단계
    """
    goals = set(user_profile.get("goals", []))
    health_issues = set(user_profile.get("health_issues", []))

    scored: List[ExerciseCandidate] = []
    for idx, ex in enumerate(exercises):
        name = ex.get("Name", "")
        body_parts = _split_body_parts(ex.get("신체부위", ""))
        fitness_item = ex.get("체력항목", "")
        equipment = ex.get("운동도구", "")
        solo_ok = ex.get("혼자여부", "")
        url = ex.get("url", "")

        # (예시) 아주 단순한 점수: 목표/체력항목 매칭 + 전날 부위 회피 + 도구 없는 운동 선호 등
        score = 0.0

        # 목표-체력항목 대충 매핑
        if "근력" in goals and fitness_item in {"근력", "근지구력"}:
            score += 2.0
        if "유연성" in goals and fitness_item == "유연성":
            score += 2.0
        if "균형" in goals and fitness_item in {"균형성", "민첩성"}:
            score += 2.0

        # 전날 부위 피하기(가능하면)
        if last_body and last_body in body_parts:
            score -= 0.8

        # 도구가 없으면 접근성↑ 가산(반대로 특정 도구가 필요하면 조금 감점)
        if not equipment or equipment == "없음":
            score += 0.5
        else:
            score -= 0.1

        # 건강 이슈가 있으면 강도 높아 보이는 것 감점
        contraindications = []
        intensity = "low"
        joint_load = "low"
        if len(health_issues) > 0:
            # 규칙을 더 세밀히 하고 싶으면 여기서 키워드 기반으로 추가
            contraindications.append("기저질환/통증이 있으면 무리하지 마세요.")
            score -= 0.2

        cand = ExerciseCandidate(
            id=f"ex_{idx}",
            name=name,
            body_parts=body_parts,
            fitness_item=fitness_item,
            equipment=equipment,
            solo_ok=solo_ok,
            url=url,
            score=score,
            intensity=intensity,
            env="indoor",  # 날씨 위험 시 실내 용도로 쓰는 경우가 많으니 indoor로
            contraindications=contraindications,
            features={"raw": ex},
        )
        scored.append(cand)

    scored.sort(key=lambda x: x.score, reverse=True)
    return scored[:k]

def choose_exercises_with_llm_for_today(
    exercises: List[Dict],
    user_profile: Dict,
    context: Dict,
    user_id: str = "default_user",
    today_date: dt.date | None = None,
    top_k: int = 8,
    top_n: int = 3,
) -> Dict:
    """
    반환 형태(예시):
    {
      "date": "YYYY-MM-DD",
      "chosen": {exercise dict},
      "ranked": [ {exercise dict + why/cautions/next_step}, ... ],
      "summary": "...",
      "safety_flags": [...]
    }
    """
    history = load_history()
    today = (today_date if today_date else dt.date.today()).isoformat()
    user_hist = history.get(user_id, {})
    last_date = user_hist.get("last_date")
    last_body = user_hist.get("last_body")

    # 오늘 이미 추천한 기록이 있으면 그대로
    if last_date == today and user_hist.get("llm_result"):
        return user_hist["llm_result"]

    # 1) 후보 Top-K 생성
    candidates = generate_exercise_candidates(
        exercises=exercises,
        user_profile=user_profile,
        context=context,
        k=top_k,
        last_body=last_body,
    )

    # 2) LLM 리랭킹+근거 생성
    from recommender.llm.client import LLMClient
    from recommender.llm.reranker import LLMRerankerExplainer

    reranker = LLMRerankerExplainer(LLMClient())
    llm_out = reranker.rerank_and_explain(
        user_profile=user_profile,
        context=context,
        candidates=candidates,
        top_n=top_n,
    )

    # 3) LLM 결과를 원본 exercise dict로 매핑
    id_to_cand = {c.id: c for c in candidates}

    ranked = []
    chosen_ex = None
    chosen_body = None

    for item in llm_out.ranked_recommendations:
        cand = id_to_cand.get(item.id)
        if not cand:
            continue
        raw_ex = cand.features.get("raw", {})
        packed = {
            **raw_ex,
            "why": item.why,
            "cautions": item.cautions,
            "next_step": item.next_step,
        }
        ranked.append(packed)
        if chosen_ex is None:
            chosen_ex = raw_ex
            chosen_body = (raw_ex.get("신체부위", "") or "").split("/")[0].strip() or "기타"

    result = {
        "date": today,
        "chosen": chosen_ex,
        "ranked": ranked,
        "summary": llm_out.user_friendly_summary,
        "safety_flags": llm_out.safety_flags,
    }

    # 4) 히스토리 저장(오늘은 이 추천을 고정)
    history[user_id] = {
        "last_date": today,
        "last_body": chosen_body,
        "today_exercise": chosen_ex,     # 기존 필드도 유지(호환)
        "llm_result": result,            # 새 필드
    }
    save_history(history)

    return result
