import os
import json
from typing import Dict, Any
import requests

class LLMClient:
    def __init__(self):
        self.provider = os.getenv("LLM_PROVIDER", "local_stub")
        self.model = os.getenv("LLM_MODEL", "solar-pro")
        self.api_key = os.getenv("LLM_API_KEY", "")
        self.upstage_base_url = os.getenv("UPSTAGE_BASE_URL", "https://api.upstage.ai/v1/solar")

    def generate_json(self, system_prompt: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        # 0) 개발용 폴백(LLM 없이도 동작)
        if self.provider == "local_stub":
            cands = payload.get("candidates", [])
            cands = sorted(cands, key=lambda x: x.get("score", 0), reverse=True)[:3]
            ranked = []
            for i, c in enumerate(cands):
                ranked.append({
                    "id": c["id"],
                    "rank": i + 1,
                    "why": [
                        f"기본 점수(score={c.get('score', 0):.2f})가 높습니다.",
                        f"부위: {', '.join(c.get('body_parts', [])) or '기타'} / 도구: {c.get('equipment') or '없음'}",
                    ],
                    "cautions": c.get("contraindications", [])[:2],
                    "next_step": "오늘은 10~20분 가볍게 시작해보세요.",
                })
            return {
                "ranked_recommendations": ranked,
                "user_friendly_summary": "오늘 컨디션과 안전을 고려해 실내 운동을 추천드려요.",
                "safety_flags": [],
            }

        # 1) Upstage Solar Chat Completions
        if self.provider == "upstage":
            if not self.api_key:
                raise ValueError("LLM_PROVIDER=upstage 인데 LLM_API_KEY가 비어있습니다.")

            url = f"{self.upstage_base_url}/chat/completions"  # .../v1/solar/chat/completions
            headers = {
                "Authorization": f"Bearer {self.api_key}",  # Bearer 형식 :contentReference[oaicite:4]{index=4}
                "Content-Type": "application/json",
            }

            # LLM이 JSON만 내도록 강제 (JSON mode) :contentReference[oaicite:5]{index=5}
            body = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
                ],
                "temperature": 0.2,
                "response_format": {"type": "json_object"},
            }

            resp = requests.post(url, headers=headers, json=body, timeout=20)
            resp.raise_for_status()
            data = resp.json()

            # OpenAI 호환: data["choices"][0]["message"]["content"]에 문자열로 들어오는 경우가 흔함
            content = data["choices"][0]["message"]["content"]
            content = content.strip()

            # content가 이미 dict로 오는 경우도 대비
            if isinstance(content, dict):
                return content

            # 문자열이면 JSON 파싱
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                # 혹시 앞뒤 잡텍스트가 붙으면 { ... }만 잘라 파싱
                start = content.find("{")
                end = content.rfind("}")
                if start != -1 and end != -1 and end > start:
                    return json.loads(content[start:end+1])
                raise

        raise NotImplementedError(f"지원하지 않는 LLM_PROVIDER={self.provider}")