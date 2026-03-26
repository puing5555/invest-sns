#!/usr/bin/env python3
"""
삼프로TV 전체 영상 메타데이터 수집 + 제목 분석
- yt-dlp로 제목+날짜만 수집 → data/3protv_metadata.json
- stock_tickers.json 종목명으로 매칭
- 게스트 이름 패턴 매칭
"""

import json
import os
import re
import sys
import yt_dlp

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CHANNEL_URL = "https://www.youtube.com/@3protv"

def step1_collect():
    """yt-dlp로 삼프로TV 전체 영상 메타데이터 수집 (제목+날짜만)"""
    output_path = os.path.join(PROJECT_ROOT, "data", "3protv_metadata.json")

    ydl_opts = {
        "extract_flat": True,
        "quiet": True,
        "no_warnings": True,
        "playlistend": None,  # 전체
    }

    print(f"[Step 1] 삼프로TV 영상 목록 수집 중...")

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"{CHANNEL_URL}/videos", download=False)

    videos = []
    for entry in info.get("entries", []):
        if entry is None:
            continue
        videos.append({
            "id": entry.get("id", ""),
            "title": entry.get("title", ""),
            "upload_date": entry.get("upload_date", ""),
            "url": f"https://www.youtube.com/watch?v={entry.get('id', '')}",
        })

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(videos, f, ensure_ascii=False, indent=2)

    print(f"  → {len(videos)}개 영상 수집 완료 → {output_path}")
    return videos


def extract_guest_names(title):
    """
    삼프로TV 제목에서 게스트 이름 추출.

    주요 패턴:
    1. "제목 | 이름 소속 직함 [프로그램]" — 마지막 구분자 뒤
    2. "제목 ㅣ 이름1, 이름2 소속 직함 [프로그램]"
    3. "제목 l 이름 소속 [프로그램]" (소문자 L)
    """
    # 비이름 단어 (직함, 소속, 프로그램, 일반어)
    NON_NAMES = {
        # 직함
        '교수', '대표', '박사', '위원', '팀장', '부장', '센터장', '원장',
        '이사', '소장', '실장', '본부장', '사장', '회장', '전무', '상무',
        '수석', '차장', '과장', '연구원', '작가', '기자', '앵커', '편집장',
        '부센터장', '선임', '의원', '변호사', '판사', '장관', '차관',
        '비서관', '대변인', '국장', '처장', '청장',
        # 소속 관련
        '증권', '투자', '연구', '리서치', '센터', '지점', '글로벌',
        '삼프로', '경제', '자산', '운용', '금융', '하나', '교보',
        '네이버', '카카오', '신한', '국민', '우리',
        # 프로그램명
        '인사이드', '인터뷰', '뉴스', '마켓', '클로징벨', '라이브',
        '시황', '더블', '크루', '체크', '아침', '월가', '레전드',
        '취재팀장', '이코노미스트', '리서치센터',
        # 장소
        '명동', '영업부', '인천', '경인',
        # 일반 단어 (제목 내용이 게스트로 잡히는 것 방지)
        '한국어', '트럼프', '바이든', '시진핑', '푸틴', '젤렌스키',
        '네타냐후', '호르무즈', '이스라엘', '우크라이나', '러시아',
        '미국', '한국', '중국', '일본', '이란', '북한',
    }

    # 포함하면 안 되는 서브스트링 패턴
    NON_NAME_CONTAINS = ['증권', '투자', '연구', '센터', '지점', '본부',
                         '그룹', '전자', '바이오', '에너지', '케미칼']

    def is_valid_name(name):
        if name in NON_NAMES:
            return False
        if any(kw in name for kw in NON_NAME_CONTAINS):
            return False
        if len(name) < 2 or len(name) > 4:
            return False
        return True

    guests = []

    # Step 1: 구분자로 분리 — 마지막 세그먼트만 사용
    # |, ｜, ㅣ(\u3163), 또는 공백으로 둘러싼 소문자 l
    segments = re.split(r'\s*[|｜\u3163]\s*|\s+l\s+', title)

    guest_segment = None
    if len(segments) >= 2:
        # 마지막 세그먼트에 [프로그램명]이 있으면 그게 게스트 세그먼트
        last = segments[-1].strip()
        if re.search(r'\[', last):
            guest_segment = last
        # 없으면 뒤에서 두 번째 체크 (3+ 세그먼트)
        elif len(segments) >= 3:
            second_last = segments[-2].strip()
            if re.search(r'\[', second_last):
                guest_segment = second_last

    if guest_segment:
        # [프로그램명] 제거
        clean = re.sub(r'\[.*?\]', '', guest_segment).strip()

        # 한국 이름 추출: 2~4자 한글, 앞뒤가 비한글(공백/콤마/시작/끝)
        # 한글 뒤에 한글이 더 오면 조직명 일부일 수 있으므로 제외
        names = re.findall(r'(?:^|[,\s·])([가-힣]{2,4})(?=[^가-힣]|$)', clean)

        for name in names:
            if is_valid_name(name):
                guests.append(name)

    # Step 2: 구분자 없지만 "이름 소속 직함 [프로그램]" 패턴
    if not guests and '[' in title:
        # [프로그램] 바로 앞 부분에서 이름 추출
        # 패턴: "... 이름 소속명 직함 [프로그램]" 또는 "... 이름1, 이름2 [프로그램]"
        before_bracket = title[:title.rfind('[')].strip()

        # 쉼표로 구분된 이름 나열 패턴 (끝 부분)
        # "홍선애, 김장열, 이권희" 같은 패턴
        comma_pattern = re.search(
            r'([가-힣]{2,4}(?:\s*[,·]\s*[가-힣]{2,4})+)\s*$',
            before_bracket
        )
        if comma_pattern:
            found = re.findall(r'[가-힣]{2,4}', comma_pattern.group(1))
            for name in found:
                if is_valid_name(name):
                    guests.append(name)

        # 단일 이름 + 소속 패턴
        if not guests:
            m = re.search(
                r'([가-힣]{2,4})\s+[가-힣A-Za-z]+(?:증권|투자|자산운용|경제연구소|연구소|금융)[가-힣]*\s*[가-힣]*\s*$',
                before_bracket
            )
            if m and is_valid_name(m.group(1)):
                guests.append(m.group(1))

    return list(dict.fromkeys(guests))  # 중복 제거, 순서 유지


def step2_analyze(videos):
    """제목 분석: 종목명 매칭 + 게스트 이름 패턴"""

    # 1. signal_prices.json에서 종목명 로드
    prices_path = os.path.join(PROJECT_ROOT, "data", "signal_prices.json")
    with open(prices_path, "r", encoding="utf-8") as f:
        prices = json.load(f)

    # 종목명 → 티커 매핑 (2글자 이상만)
    stock_names = {}
    for ticker, info in prices.items():
        name = info.get("name", "")
        if name and len(name) >= 2:
            stock_names[name] = ticker

    # 미국 티커 (대문자 2~5자)
    tickers_path = os.path.join(PROJECT_ROOT, "data", "stock_tickers.json")
    with open(tickers_path, "r", encoding="utf-8") as f:
        all_tickers = json.load(f)

    us_tickers = set()
    for t in all_tickers:
        if re.match(r'^[A-Z]{2,5}$', t):
            us_tickers.add(t)

    # 너무 일반적인 단어 제외
    common_words = {
        "AI", "CEO", "ETF", "GDP", "IMF", "IPO", "IT", "LP", "TV",
        "VS", "GO", "NOW", "BE", "US", "TOP", "NEW", "BIG", "THE",
        "HOT", "ALL", "MY", "NO", "UP", "ON", "ONE", "TWO", "WAR",
        "WIN", "END", "DAY", "LIVE", "BEST", "REAL", "FREE", "FULL",
        "HIGH", "PART", "PLAN", "SHOW", "TALK", "TIME", "NEWS",
        "PB", "WTI", "CIO", "GTC",
        "H", "S", "U",
    }
    us_tickers -= common_words

    # 종목명 중 제목에서 오탐 유발하는 것들 분리
    # "코스피", "나스닥" 등은 지수이지 개별종목이 아님
    index_names = {"코스피", "나스닥", "코스닥"}

    print(f"\n[Step 2] 제목 분석")
    print(f"  종목명 {len(stock_names)}개 + 미국 티커 {len(us_tickers)}개로 매칭")

    has_stock = []
    has_guest = []
    has_both = []

    stock_match_details = {}
    guest_names_count = {}

    for v in videos:
        title = v["title"]

        # --- 종목명 매칭 ---
        matched_stocks = set()

        # 한국 종목명
        for name, ticker in stock_names.items():
            if name in title:
                matched_stocks.add(name)

        # 미국 티커 (단어 경계)
        for ticker in us_tickers:
            if re.search(r'\b' + re.escape(ticker) + r'\b', title):
                matched_stocks.add(ticker)

        # 지수 이름 제외 (별도 카운트용)
        matched_stocks_no_index = matched_stocks - index_names

        # --- 게스트 이름 매칭 ---
        guests = extract_guest_names(title)

        v["matched_stocks"] = list(matched_stocks)
        v["matched_stocks_individual"] = list(matched_stocks_no_index)
        v["guest_names"] = guests

        is_stock = len(matched_stocks_no_index) > 0
        is_guest = len(guests) > 0

        if is_stock:
            has_stock.append(v)
            for s in matched_stocks_no_index:
                stock_match_details[s] = stock_match_details.get(s, 0) + 1

        if is_guest:
            has_guest.append(v)
            for g in guests:
                guest_names_count[g] = guest_names_count.get(g, 0) + 1

        if is_stock and is_guest:
            has_both.append(v)

    # --- 결과 출력 ---
    total = len(videos)
    stock_ids = set(v['id'] for v in has_stock)
    guest_ids = set(v['id'] for v in has_guest)
    either = stock_ids | guest_ids

    print(f"\n{'='*60}")
    print(f"삼프로TV 영상 제목 분석 결과")
    print(f"{'='*60}")
    print(f"총 영상 수: {total:,}개")
    print()
    print(f"1. 개별 종목명 포함:  {len(has_stock):,}개 ({len(has_stock)/total*100:.1f}%)")
    print(f"2. 게스트 이름 포함:  {len(has_guest):,}개 ({len(has_guest)/total*100:.1f}%)")
    print(f"3. 둘 다 포함:        {len(has_both):,}개 ({len(has_both)/total*100:.1f}%)")
    print(f"4. 어느 하나라도:     {len(either):,}개 ({len(either)/total*100:.1f}%)")
    print(f"5. 둘 다 없음:        {total - len(either):,}개 ({(total-len(either))/total*100:.1f}%)")

    # 종목 TOP 30
    print(f"\n--- 개별 종목 매칭 TOP 30 (지수 제외) ---")
    for name, cnt in sorted(stock_match_details.items(), key=lambda x: -x[1])[:30]:
        ticker = stock_names.get(name, name)
        print(f"  {name:12s} ({ticker:10s}): {cnt:>4}회")

    # 지수 매칭 (참고용)
    print(f"\n--- 지수 매칭 (참고) ---")
    for v in videos:
        for idx_name in index_names:
            if idx_name in v.get("title", ""):
                stock_match_details.setdefault(f"[지수]{idx_name}", 0)
                stock_match_details[f"[지수]{idx_name}"] += 1
    for name in sorted(stock_match_details.keys()):
        if name.startswith("[지수]"):
            print(f"  {name}: {stock_match_details[name]}회")

    # 게스트 TOP 30
    print(f"\n--- 게스트 이름 TOP 30 ---")
    for name, cnt in sorted(guest_names_count.items(), key=lambda x: -x[1])[:30]:
        print(f"  {name}: {cnt}회")

    # 오탐 의심 게스트 (1회만 등장)
    one_timers = [n for n, c in guest_names_count.items() if c == 1]
    print(f"\n  (1회만 등장: {len(one_timers)}명 — 오탐 가능성 있음)")

    # 둘 다 있는 영상 예시 15개
    print(f"\n--- 종목+게스트 둘 다 있는 영상 예시 (최대 15개) ---")
    for v in has_both[:15]:
        date = v.get('upload_date', '')
        if date and len(date) == 8:
            date = f"{date[:4]}-{date[4:6]}-{date[6:]}"
        print(f"  [{date}] {v['title']}")
        print(f"    → 종목: {v['matched_stocks_individual']}, 게스트: {v['guest_names']}")

    return {
        "total": total,
        "has_stock": len(has_stock),
        "has_guest": len(has_guest),
        "has_both": len(has_both),
    }


if __name__ == "__main__":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

    # 비이름 단어 세트 (extract_guest_names 내부에서도 쓰이지만 여기서 정의)
    non_names = set()  # extract_guest_names 함수 내부에 정의됨

    # 이미 수집한 파일이 있으면 재사용
    meta_path = os.path.join(PROJECT_ROOT, "data", "3protv_metadata.json")
    if os.path.exists(meta_path) and "--force" not in sys.argv:
        print(f"[Skip] 기존 파일 사용: {meta_path}")
        with open(meta_path, "r", encoding="utf-8") as f:
            videos = json.load(f)
        print(f"  → {len(videos):,}개 영상")
    else:
        videos = step1_collect()

    results = step2_analyze(videos)
