#!/usr/bin/env python3
"""
JSON 파일을 Parquet 형식으로 변환
"""
import json
import pandas as pd
from pathlib import Path
import numpy as np

BASE_DIR = Path(__file__).resolve().parents[1]
JSON_PATH = BASE_DIR / "data" / "processed" / "facility_program_master.json"
PARQUET_PATH = BASE_DIR / "data" / "processed" / "facility_program_master.parquet"


def convert_json_to_parquet():
    """JSON 파일을 Parquet 형식으로 변환"""
    print(f'JSON 파일 로딩: {JSON_PATH}')
    
    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f'총 {len(data)}개 레코드 로드됨')
    
    # JSON 데이터를 DataFrame으로 변환
    rows = []
    for idx, item in enumerate(data):
        # 필수 필드 추출
        fac_name = str(item.get('시설명', '')).strip() if pd.notna(item.get('시설명')) else ''
        address = str(item.get('주소', '')).strip() if pd.notna(item.get('주소')) else ''
        lat = item.get('시설위도')
        lon = item.get('시설경도')
        is_indoor_str = str(item.get('실내여부', '')) if pd.notna(item.get('실내여부')) else ''
        sport_category = str(item.get('시설유형명', '')).strip() if pd.notna(item.get('시설유형명')) else ''
        
        # 좌표가 유효한지 확인
        if pd.isna(lat) or pd.isna(lon) or not fac_name:
            continue
        
        # 실내여부 변환
        is_indoor = is_indoor_str == '실내' if is_indoor_str else True
        
        # 프로그램 정보 처리
        # programs 필드가 있으면 사용, 없으면 기본값
        programs = item.get('programs')
        
        # programs가 배열이거나 NaN인지 확인
        is_programs_empty = (
            pd.isna(programs) if not isinstance(programs, (list, dict)) else False
        ) or programs is None or programs == '' or (isinstance(programs, list) and len(programs) == 0)
        
        if is_programs_empty:
            # 기본 프로그램 정보 생성
            program_name = f'{sport_category} 프로그램' if sport_category else '일반 운동 프로그램'
            intensity_level = 'medium'  # 기본값
            senior_friendly = True  # 기본값
            operating_hours = '평일 오전'
            
            rows.append({
                'fac_id': f'F{len(rows):06d}',
                'fac_name': fac_name,
                'address': address,
                'lat': float(lat),
                'lon': float(lon),
                'is_indoor': is_indoor,
                'sport_category': sport_category if sport_category else 'general',
                'program_name': program_name,
                'intensity_level': intensity_level,
                'senior_friendly': senior_friendly,
                'operating_hours': operating_hours,
            })
        else:
            # programs가 있으면 처리 (나중에 확장 가능)
            # 일단 기본값으로 처리
            program_name = f'{sport_category} 프로그램' if sport_category else '일반 운동 프로그램'
            intensity_level = 'medium'
            senior_friendly = True
            operating_hours = '평일 오전'
            
            rows.append({
                'fac_id': f'F{len(rows):06d}',
                'fac_name': fac_name,
                'address': address,
                'lat': float(lat),
                'lon': float(lon),
                'is_indoor': is_indoor,
                'sport_category': sport_category if sport_category else 'general',
                'program_name': program_name,
                'intensity_level': intensity_level,
                'senior_friendly': senior_friendly,
                'operating_hours': operating_hours,
            })
        
        if (idx + 1) % 10000 == 0:
            print(f'  처리 중: {idx + 1}/{len(data)} ({len(rows)}개 변환됨)')
    
    print(f'\n변환된 레코드: {len(rows)}개')
    
    # DataFrame 생성
    df = pd.DataFrame(rows)
    
    # 중복 제거 (같은 시설, 같은 프로그램, 같은 위치)
    before_dedup = len(df)
    df = df.drop_duplicates(subset=['fac_name', 'program_name', 'lat', 'lon'])
    after_dedup = len(df)
    
    print(f'중복 제거: {before_dedup}개 -> {after_dedup}개')
    print(f'고유 시설 수: {df["fac_name"].nunique()}개')
    
    # Parquet로 저장
    PARQUET_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(PARQUET_PATH, index=False)
    
    print(f'\n✅ Parquet 파일 저장 완료: {PARQUET_PATH}')
    print(f'   파일 크기: {PARQUET_PATH.stat().st_size / (1024*1024):.2f} MB')
    
    # 샘플 확인
    print(f'\n샘플 데이터 (처음 5개):')
    print(df[['fac_name', 'address', 'lat', 'lon', 'is_indoor', 'sport_category']].head(5).to_string())
    
    # 지역별 통계
    print(f'\n지역별 시설 수 (상위 10개):')
    if 'address' in df.columns:
        regions = df['address'].str.split(' ').str[0].value_counts().head(10)
        print(regions)
    
    return df


if __name__ == "__main__":
    convert_json_to_parquet()

