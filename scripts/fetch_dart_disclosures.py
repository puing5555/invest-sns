#!/usr/bin/env python3
"""
DART API에서 실제 공시 20건을 가져와서 v6 등급 시스템에 맞게 변환
"""
import requests
import json
import os
from datetime import datetime, timedelta
import uuid

# DART API 키
DART_API_KEY = "b6ea29c886e5d9009155a3360d3dc8a8932a523b"
DART_BASE_URL = "https://opendart.fss.or.kr/api"

def get_recent_disclosures(limit=20):
    """최근 공시 가져오기"""
    # 오늘부터 5일전까지 검색
    end_date = datetime.now().strftime('%Y%m%d')
    start_date = (datetime.now() - timedelta(days=5)).strftime('%Y%m%d')
    
    url = f"{DART_BASE_URL}/list.json"
    params = {
        'crtfc_key': DART_API_KEY,
        'bgn_de': start_date,
        'end_de': end_date,
        'page_no': '1',
        'page_count': str(limit),
        'corp_cls': 'Y'  # 유가증권 시장만
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if data.get('status') == '000':
            return data.get('list', [])
        else:
            print(f"DART API 에러: {data.get('message')}")
            return []
    except Exception as e:
        print(f"API 요청 실패: {e}")
        return []

def classify_disclosure_type(report_nm):
    """공시 유형 분류"""
    report_nm = report_nm.lower()
    
    if any(x in report_nm for x in ['실적', '손익', '매출', '영업이익', '분기보고서']):
        return "실적"
    elif any(x in report_nm for x in ['자기주식', '자사주']):
        return "자기주식"
    elif any(x in report_nm for x in ['cb', '전환사채', 'bw', '신주인수권']):
        return "CB/BW"
    elif any(x in report_nm for x in ['유상증자', '증자']):
        return "유상증자"
    elif any(x in report_nm for x in ['수주', '계약']):
        return "수주"
    elif any(x in report_nm for x in ['풍문', '조회']):
        return "풍문"
    elif any(x in report_nm for x in ['합병', '분할']):
        return "합병/분할"
    elif any(x in report_nm for x in ['배당']):
        return "배당"
    else:
        return "기타"

def assign_grade_by_type(disclosure_type, report_nm):
    """기획서 v6 등급 기준에 따른 등급 배정"""
    report_nm = report_nm.lower()
    
    # A등급 - 즉시 행동 필요
    if any(x in report_nm for x in ['상장폐지', '감자', '구속', '경영권분쟁']):
        return "A"
    
    # B등급 - 24시간 내 판단
    if disclosure_type == "CB/BW":
        return "B"  # CB는 일단 B등급
    elif disclosure_type == "실적" and any(x in report_nm for x in ['손실', '적자', '감소']):
        return "B"  # 실적 쇼크
    elif any(x in report_nm for x in ['풍문', '조회']):
        return "B"  # 풍문해명
    elif disclosure_type == "수주" and any(x in report_nm for x in ['대규모', '대형']):
        return "B"  # 대형 수주
    
    # C등급 - 참고
    elif disclosure_type == "자기주식":
        return "C"  # 자사주는 일반적으로 C등급
    elif disclosure_type == "수주":
        return "C"  # 일반 수주
    elif disclosure_type == "배당":
        return "C"  # 중간배당
    
    # D등급 - 무시
    elif any(x in report_nm for x in ['ir', '설명회', '공고', '정정']):
        return "D"
    
    return "C"  # 기본값

def convert_to_v6_format(dart_item):
    """DART 공시를 v6 JSON 구조로 변환"""
    disclosure_type = classify_disclosure_type(dart_item['report_nm'])
    grade = assign_grade_by_type(disclosure_type, dart_item['report_nm'])
    
    # 간단한 AI 분석 시뮬레이션 (실제로는 AI API 호출)
    verdict_tone = "neutral"
    if grade == "A":
        verdict_tone = "bearish"
    elif grade == "B" and disclosure_type == "실적":
        verdict_tone = "bearish" if "감소" in dart_item['report_nm'] else "bullish"
    elif disclosure_type == "자기주식":
        verdict_tone = "bullish"
    
    return {
        "id": str(uuid.uuid4()),
        "corp_name": dart_item['corp_name'],
        "corp_code": dart_item['corp_code'],
        "stock_code": dart_item.get('stock_code', ''),
        "market": "kospi" if dart_item.get('corp_cls') == 'Y' else "kosdaq",
        "report_nm": dart_item['report_nm'],
        "rcept_no": dart_item['rcept_no'],
        "rcept_dt": dart_item['rcept_dt'],
        "disclosure_type": disclosure_type,
        "importance": "high" if grade in ["A", "B"] else "medium",
        
        # v6 AI 출력 구조
        "verdict": f"{dart_item['corp_name']} {disclosure_type} 공시",
        "verdict_tone": verdict_tone,
        "grade": grade,
        "what": f"{disclosure_type} 관련 공시입니다.",
        "so_what": "실제 분석은 AI가 수행합니다.",
        "now_what_holding": "보유 중이라면 공시 내용을 검토하세요.",
        "now_what_not_holding": "미보유라면 투자 기회를 검토하세요.",
        "risk": "공시 내용에 따른 주가 변동 가능성",
        "key_date": dart_item['rcept_dt'],
        "size_assessment": "보통",
        "tags": [disclosure_type, grade + "등급"],
        
        "source": "dart",
        "created_at": f"{dart_item['rcept_dt'][:4]}-{dart_item['rcept_dt'][4:6]}-{dart_item['rcept_dt'][6:8]}T09:00:00Z"
    }

def main():
    print("DART API에서 최근 공시 20건을 가져오는 중...")
    
    # 1. DART API에서 공시 가져오기
    dart_disclosures = get_recent_disclosures(20)
    
    if not dart_disclosures:
        print("공시를 가져올 수 없습니다.")
        return
    
    print(f"{len(dart_disclosures)}건의 공시를 가져왔습니다.")
    
    # 2. v6 포맷으로 변환
    v6_disclosures = []
    for item in dart_disclosures:
        v6_item = convert_to_v6_format(item)
        v6_disclosures.append(v6_item)
        print(f"변환: {item['corp_name']} - {item['report_nm'][:50]} -> {v6_item['grade']}등급")
    
    # 3. JSON 파일로 저장
    output_path = "../data/disclosure_seed_20.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(v6_disclosures, f, ensure_ascii=False, indent=2)
    
    print(f"\n[완료] {len(v6_disclosures)}건의 공시가 {output_path}에 저장되었습니다.")
    
    # 등급별 통계
    grade_stats = {}
    for item in v6_disclosures:
        grade = item['grade']
        grade_stats[grade] = grade_stats.get(grade, 0) + 1
    
    print("\n등급별 분포:")
    for grade in ['A', 'B', 'C', 'D']:
        count = grade_stats.get(grade, 0)
        print(f"  {grade}등급: {count}건")

if __name__ == "__main__":
    main()