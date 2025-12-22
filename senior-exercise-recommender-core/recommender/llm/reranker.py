from typing import Dict, Any, List
from pydantic import ValidationError

from .client import LLMClient
from .prompts import SYSTEM_PROMPT
from .schemas import ExerciseCandidate, LLMExerciseOutput

class LLMRerankerExplainer:
    def __init__(self, client: LLMClient):
        self.client = client

    def rerank_and_explain(
        self,
        user_profile: Dict[str, Any],
        context: Dict[str, Any],
        candidates: List[ExerciseCandidate],
        top_n: int = 3,
    ) -> LLMExerciseOutput:
        payload = {
            "user_profile": user_profile,
            "context": context,
            "candidates": [c.model_dump() for c in candidates],
        }

        raw = self.client.generate_json(SYSTEM_PROMPT, payload)

        try:
            out = LLMExerciseOutput.model_validate(raw)
        except ValidationError:
            # 폴백: candidates score 순
            sorted_c = sorted(candidates, key=lambda x: x.score, reverse=True)[:top_n]
            fallback = {
                "ranked_recommendations": [
                    {
                        "id": c.id,
                        "rank": i + 1,
                        "why": [f"기본 점수(score={c.score:.2f})가 높습니다."],
                        "cautions": c.contraindications[:2],
                        "next_step": "오늘은 10~20분 가볍게 시작해보세요.",
                    }
                    for i, c in enumerate(sorted_c)
                ],
                "user_friendly_summary": "기본 추천 로직에 따라 운동을 추천드렸어요.",
                "safety_flags": [],
            }
            out = LLMExerciseOutput.model_validate(fallback)

        out.ranked_recommendations = sorted(out.ranked_recommendations, key=lambda x: x.rank)[:top_n]
        return out
