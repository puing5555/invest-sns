# -*- coding: utf-8 -*-
"""올랜도 킴 영상 제목 필터링 (규칙 기반 + 애매한 건 목록)"""
import sys, json, re
sys.stdout.reconfigure(encoding='utf-8')

with open('data/orlando_kim_videos.txt', 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f if l.strip()]

videos = []
for l in lines:
    parts = l.split('|')
    if len(parts) >= 2:
        videos.append({
            'id': parts[0],
            'title': parts[1],
            'date': parts[2] if len(parts) > 2 else 'NA',
            'duration': parts[3] if len(parts) > 3 else 'NA'
        })

# 제외 키워드 (시황/매크로/교육/라이브/광고)
EXCLUDE_PREFIXES = ['시황분석', '주간시황', '월간시황', '긴급시황', '이란전쟁']
EXCLUDE_KEYWORDS = ['시장 정리', '금리 전망', '주식 시작', 'PER이란', '실시간', '라이브',
                    '멤버십 전용', '유료 리포트', '뉴스 정리', '시장 전망', '경제 전망']

# 종목 키워드 (추출 대상)
STOCK_KEYWORDS = [
    '아이온큐', '테슬라', '팔란티어', '엔비디아', '아이렌', '삼성전자', '하이닉스',
    'SK하이닉스', '비트코인', '샌디스크', '애플', 'AMD', 'TSMC', '마이크로소프트',
    '아마존', '구글', '메타', '넷플릭스', '코인베이스', '로블록스', '스노우플레이크',
    '크라우드스트라이크', '데이터독', '유니티', '리비안', '루시드', '니오', '샤오미',
    'IONQ', 'TSLA', 'PLTR', 'NVDA', 'IREN', 'AAPL', 'MSFT', 'AMZN', 'GOOG', 'META',
    'NFLX', 'COIN', 'RBLX', 'SNOW', 'CRWD', 'DDOG', 'RIVN', 'LCID', 'NIO',
    '반도체', '원전', '우라늄', '양자컴퓨터', '로봇', 'AI주'
]

SIGNAL_KEYWORDS = ['사야', '팔아야', '매수', '매도', '10배', '유망', '텐베거', 
                   '상승', '폭락', '급등', '실적', '목표가', '밸류', '저평가', '고평가',
                   '관심종목', '추천', '26년 유망', '25년 유망']

include = []
exclude = []
ambiguous = []

for v in videos:
    title = v['title']
    
    # Extract prefix if exists
    prefix = ''
    if '(' in title and ')' in title:
        prefix = title[title.index('(')+1:title.index(')')]
    
    # Check exclude first
    if prefix in EXCLUDE_PREFIXES:
        # But check if title also has stock keywords
        has_stock = any(kw in title for kw in STOCK_KEYWORDS)
        if has_stock:
            ambiguous.append(v)
        else:
            exclude.append(v)
        continue
    
    if any(kw in title for kw in EXCLUDE_KEYWORDS):
        exclude.append(v)
        continue
    
    # Check include
    has_stock = any(kw in title for kw in STOCK_KEYWORDS)
    has_signal = any(kw in title for kw in SIGNAL_KEYWORDS)
    
    if has_stock or has_signal or prefix in ['아이온큐', '테슬라', '팔란티어', '엔비디아', '아이렌',
                                              '관심종목', '26년 유망주', '텐베거', '샌디스크', '비트코인',
                                              '삼성전자,하이닉스', '반도체', '상승 가능종목']:
        include.append(v)
    else:
        ambiguous.append(v)

print(f"=== 필터링 결과 ===")
print(f"✅ 추출 대상 (O): {len(include)}개")
print(f"❌ 제외 대상 (X): {len(exclude)}개")  
print(f"🟡 판단 필요: {len(ambiguous)}개")
print()

# Save results
with open('data/orlando_filter_include.json', 'w', encoding='utf-8') as f:
    json.dump(include, f, ensure_ascii=False, indent=2)

with open('data/orlando_filter_ambiguous.json', 'w', encoding='utf-8') as f:
    json.dump(ambiguous, f, ensure_ascii=False, indent=2)

print("--- 추출 대상 샘플 ---")
for v in include[:10]:
    print(f"  {v['title']}")

print()
print("--- 판단 필요 ---")
for v in ambiguous:
    print(f"  [{v['id']}] {v['title']}")
