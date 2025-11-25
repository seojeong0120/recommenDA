
"""더미 facility_program_master 데이터를 생성해 파이프라인을 테스트한다."""

from __future__ import annotations

import random
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
OUTPUT_PATH = BASE_DIR / "data" / "processed" / "facility_program_master.parquet"


def _sample_rows() -> list[dict]:
    """테스트용 시설/프로그램 행 몇 개 생성."""
    facilities = [
        ("F001", "은평구민체육센터", 37.619, 126.922, True, "서대문구 연희로 20"),
        ("F002", "마포노인체육관", 37.552, 126.955, True, "마포구 백범로 10"),
        ("F003", "월드컵공원 걷기코스", 37.569, 126.894, False, "마포구 월드컵로 243"),
        ("F004", "망원한강야외체육장", 37.555, 126.902, False, "마포구 포은로 32"),
        ("F005", "불광동문화체육센터", 37.610, 126.933, True, "은평구 불광로 48"),
    ]

    programs = [
        ("실버 요가", "yoga", "low", True, "평일 오전"),
        ("맞춤형 필라테스", "stretching", "medium", True, "평일 오후"),
        ("걷기 동호회", "walking", "low", False, "주말 오전"),
        ("저충격 근력강화", "light_strength", "medium", True, "평일 오전"),
        ("수중 재활", "water_exercise", "low", True, "평일 오전"),
        ("시니어 댄스", "dance", "medium", True, "주말 오후"),
    ]

    rows: list[dict] = []
    random.seed(42)
    for fac in facilities:
        for program in random.sample(programs, k=2):
            rows.append(
                {
                    "fac_id": fac[0],
                    "fac_name": fac[1],
                    "address": fac[5],
                    "lat": fac[2],
                    "lon": fac[3],
                    "is_indoor": fac[4] if program[1] != "walking" else False,
                    "sport_category": program[1],
                    "program_name": program[0],
                    "intensity_level": program[2],
                    "senior_friendly": program[3],
                    "operating_hours": program[4],
                }
            )
    return rows


def build_fake_master() -> Path:
    rows = _sample_rows()
    df = pd.DataFrame(rows)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(OUTPUT_PATH, index=False)

    return OUTPUT_PATH


if __name__ == "__main__":
    path = build_fake_master()
    print(f"[fake_master_generator] Wrote {path}")

