import json
from pathlib import Path

import pandas as pd


DATA_DIR = Path(__file__).resolve().parents[1] / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"


def load_data():
    programs = pd.read_csv(RAW_DIR / "facility_programs_senior.csv")
    national = pd.read_csv(RAW_DIR / "national_sports.csv")

    programs["lat"] = programs["lat"].round(4)
    programs["lon"] = programs["lon"].round(4)
    programs["좌표"] = programs.apply(
        lambda x: f"({x['lat']}, {x['lon']})",
        axis=1,
    )

    national["lat"] = national["시설위도"].round(4)
    national["lon"] = national["시설경도"].round(4)
    national["좌표"] = national.apply(
        lambda x: f"({x['lat']}, {x['lon']})",
        axis=1,
    )

    return programs, national


def merge_data(programs, national):
    merged = national.merge(programs, on="좌표", how="left")

    # JSON 문자열로 되어있는 programs 컬럼을 리스트로 변환
    merged["programs"] = merged["programs"].apply(
        lambda x: json.loads(x) if isinstance(x, str) else x
    )

    return merged


def save_json(merged, output_path):
    records = merged.to_dict(orient="records")
    records = deduplicate_records(records)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)


def deduplicate_records(records):
    seen = {}
    deduped = []

    for record in records:
        facility_key = record.get("facility_name") or record.get("facility_id")
        serialized = json.dumps(record, sort_keys=True, ensure_ascii=False)
        dedupe_key = facility_key or serialized

        if dedupe_key in seen and seen[dedupe_key] == serialized:
            continue

        seen[dedupe_key] = serialized
        deduped.append(record)

    return deduped


def main():
    programs, national = load_data()
    merged = merge_data(programs, national)
    save_json(merged, PROCESSED_DIR / "facility_program_master.json")


if __name__ == "__main__":
    main()
