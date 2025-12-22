from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Dict, Any

Intensity = Literal["low", "moderate", "high"]
EnvType = Literal["indoor", "outdoor", "either", "any"]

class ExerciseCandidate(BaseModel):
    id: str
    name: str
    body_parts: List[str] = []
    fitness_item: Optional[str] = None   # 체력항목
    equipment: Optional[str] = None      # 운동도구
    solo_ok: Optional[str] = None        # 혼자여부 (y/n)
    url: Optional[str] = None

    # 룰 기반 후보 생성에서 계산한 점수/메타
    score: float = 0.0
    intensity: Intensity = "low"
    env: EnvType = "indoor"
    contraindications: List[str] = []
    features: Dict[str, Any] = Field(default_factory=dict)

class LLMRankedItem(BaseModel):
    id: str
    rank: int = Field(..., ge=1)
    why: List[str] = Field(..., description="2~4줄 근거")
    cautions: List[str] = Field(default_factory=list, description="1~2개 주의")
    next_step: str

class LLMExerciseOutput(BaseModel):
    ranked_recommendations: List[LLMRankedItem]
    user_friendly_summary: str
    safety_flags: List[str] = []
