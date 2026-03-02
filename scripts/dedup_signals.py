#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
종목명 정규화 + 중복 시그널 정리 스크립트
- 같은 종목 다른 이름 매핑
- 같은 video_id + 같은 종목 중복 삭제
- ticker 없는 시그널에 ticker 채우기
"""

import json
import sys
import io
import os
from urllib.request import Request, urlopen
from urllib.parse import quote
from pathlib import Path
from collections import defaultdict

if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = PROJECT_ROOT / ".env.local"

def load_env():
    env = {}
    for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip()
    return env

ENV = load_env()
SUPABASE_URL = ENV["NEXT_PUBLIC_SUPABASE_URL"]
SUPABASE_KEY = ENV.get("SUPABASE_SERVICE_ROLE_KEY") or ENV["NEXT_PUBLIC_SUPABASE_ANON_KEY"]

# ─── 종목명 → ticker 정규화 매핑 ─────────────────────────────────────────────
# key: 종목명에 포함되면 매칭, value: (정규화된 이름, ticker)
STOCK_NORMALIZE = {
    # 한글 변형 → 정규화
    "팔라티어": ("팔란티어", "PLTR"),
    "팔란티어": ("팔란티어", "PLTR"),
    "비트코인": ("비트코인", "BTC"),
    "이더리움": ("이더리움", "ETH"),
    "솔라나": ("솔라나", "SOL"),
    "테슬라": ("테슬라", "TSLA"),
    "엔비디아": ("엔비디아", "NVDA"),
    "마이크론": ("마이크론", "MU"),
    "도지코인": ("도지코인", "DOGE"),
    "리플": ("리플", "XRP"),
    "애플": ("애플", "AAPL"),
    "마이크로소프트": ("마이크로소프트", "MSFT"),
    "아마존": ("아마존", "AMZN"),
    "구글": ("구글", "GOOG"),
    "알파벳": ("구글", "GOOG"),
    "메타": ("메타", "META"),
    "페이스북": ("메타", "META"),
    "코인베이스": ("코인베이스", "COIN"),
    "마이크로스트래티지": ("마이크로스트래티지", "MSTR"),
    "스트래티지": ("마이크로스트래티지", "MSTR"),
    "브로드컴": ("브로드컴", "AVGO"),
    "AMD": ("AMD", "AMD"),
    "인텔": ("인텔", "INTC"),
    "퀄컴": ("퀄컴", "QCOM"),
    "아크": ("ARK", "ARKK"),
    "ARM": ("ARM", "ARM"),
    "팔란티어 테크놀로지": ("팔란티어", "PLTR"),
    "수이": ("수이", "SUI"),
    "에이다": ("에이다", "ADA"),
    "카르다노": ("에이다", "ADA"),
    "체인링크": ("체인링크", "LINK"),
    "아발란체": ("아발란체", "AVAX"),
    "폴카닷": ("폴카닷", "DOT"),
    "유니스왑": ("유니스왑", "UNI"),
    "앱토스": ("앱토스", "APT"),
    "삼성전자": ("삼성전자", "005930"),
    "SK하이닉스": ("SK하이닉스", "000660"),
}


def supabase_get(table, params="select=*"):
    all_rows = []
    limit = 1000
    offset = 0
    while True:
        sep = "&" if params else ""
        url = f"{SUPABASE_URL}/rest/v1/{table}?{params}{sep}limit={limit}&offset={offset}"
        req = Request(url, headers={
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Prefer": "count=exact",
        })
        resp = urlopen(req)
        data = json.loads(resp.read())
        if not data:
            break
        all_rows.extend(data)
        if len(data) < limit:
            break
        offset += limit
    return all_rows


def supabase_delete(table, ids):
    deleted = 0
    for i in range(0, len(ids), 50):
        batch = ids[i:i+50]
        id_filter = ",".join(str(x) for x in batch)
        url = f"{SUPABASE_URL}/rest/v1/{table}?id=in.({quote(id_filter)})"
        req = Request(url, method="DELETE", headers={
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Prefer": "return=minimal",
        })
        urlopen(req)
        deleted += len(batch)
    return deleted


def supabase_patch(table, row_id, data):
    url = f"{SUPABASE_URL}/rest/v1/{table}?id=eq.{row_id}"
    body = json.dumps(data).encode("utf-8")
    req = Request(url, data=body, method="PATCH", headers={
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal",
    })
    urlopen(req)


def normalize_stock(stock_name, ticker=None):
    """종목명에서 정규화된 (이름, ticker) 반환"""
    if not stock_name:
        return stock_name, ticker
    
    name = stock_name.strip()
    
    # 이미 "종목명 (TICKER)" 형식이면 ticker 추출
    import re
    m = re.match(r'^(.+?)\s*\(([A-Z0-9.]+)\)\s*$', name)
    if m:
        base_name = m.group(1).strip()
        extracted_ticker = m.group(2)
        # base_name도 정규화
        for key, (norm_name, norm_ticker) in STOCK_NORMALIZE.items():
            if key in base_name:
                return norm_name, norm_ticker
        return base_name, extracted_ticker
    
    # ticker로 먼저 매칭
    if ticker:
        for key, (norm_name, norm_ticker) in STOCK_NORMALIZE.items():
            if norm_ticker == ticker.upper():
                return norm_name, norm_ticker
    
    # 이름으로 매칭
    for key, (norm_name, norm_ticker) in STOCK_NORMALIZE.items():
        if key in name:
            return norm_name, norm_ticker
    
    return name, ticker


def main():
    print("=" * 60)
    print("🔧 종목명 정규화 + 중복 시그널 정리")
    print("=" * 60)
    
    # 1. 전체 시그널 가져오기
    signals = supabase_get("influencer_signals")
    print(f"\n📊 전체 시그널: {len(signals)}개")
    
    # 2. 종목명 분석
    print("\n─── 종목명 분석 ───")
    stock_names = defaultdict(list)
    for s in signals:
        stock = s.get("stock", "") or ""
        stock_names[stock].append(s)
    
    print(f"고유 종목명: {len(stock_names)}개")
    
    # 정규화 매핑 결과 미리보기
    norm_groups = defaultdict(list)  # (norm_name, ticker) -> [original names]
    for stock_name in stock_names:
        norm_name, norm_ticker = normalize_stock(stock_name)
        key = (norm_name, norm_ticker or "")
        if stock_name not in norm_groups[key]:
            norm_groups[key].append(stock_name)
    
    # 다른 이름으로 존재하는 그룹만 표시
    print("\n📋 같은 종목 다른 이름:")
    for (norm_name, ticker), names in sorted(norm_groups.items()):
        if len(names) > 1:
            canonical = f"{norm_name} ({ticker})" if ticker else norm_name
            print(f"  {canonical} ← {names}")
    
    # 3. 중복 찾기 (같은 video_id + 같은 종목)
    print("\n─── 중복 시그널 찾기 (같은 영상 + 같은 종목) ───")
    
    # Group by video_id
    by_video = defaultdict(list)
    for s in signals:
        vid = s.get("video_id")
        if vid:
            by_video[vid].append(s)
    
    to_delete = []
    for vid, sigs in by_video.items():
        # Group by normalized stock within this video
        by_norm_stock = defaultdict(list)
        for s in sigs:
            norm_name, norm_ticker = normalize_stock(s.get("stock", ""), s.get("ticker"))
            key = norm_ticker or norm_name  # ticker 기준, 없으면 이름
            if key:
                by_norm_stock[key].append(s)
        
        for key, group in by_norm_stock.items():
            if len(group) <= 1:
                continue
            
            # 정렬: ticker 있는 거 우선, 그 다음 created_at 오래된 거 우선
            group.sort(key=lambda s: (
                0 if s.get("ticker") else 1,
                s.get("created_at", "")
            ))
            
            keeper = group[0]
            for dup in group[1:]:
                to_delete.append(dup)
                print(f"  🗑️ 삭제: [{dup.get('stock')}] signal={dup.get('signal')} (video={vid[:20]}...)")
                print(f"     유지: [{keeper.get('stock')}] signal={keeper.get('signal')}")
    
    print(f"\n중복 삭제 대상: {len(to_delete)}개")
    
    if to_delete:
        ids = [s["id"] for s in to_delete]
        deleted = supabase_delete("influencer_signals", ids)
        print(f"✅ {deleted}개 삭제 완료")
        
        # Remove deleted from signals list
        deleted_ids = set(ids)
        signals = [s for s in signals if s["id"] not in deleted_ids]
    
    # 4. 종목명 통일 + ticker 채우기
    print("\n─── 종목명 통일 + ticker 채우기 ───")
    updated = 0
    for s in signals:
        stock = s.get("stock", "") or ""
        ticker = s.get("ticker") or ""
        norm_name, norm_ticker = normalize_stock(stock, ticker)
        
        if not norm_ticker:
            continue
        
        canonical = f"{norm_name} ({norm_ticker})"
        changes = {}
        
        if stock != canonical:
            changes["stock"] = canonical
        if ticker != norm_ticker:
            changes["ticker"] = norm_ticker
        
        if changes:
            try:
                supabase_patch("influencer_signals", s["id"], changes)
                updated += 1
                if updated <= 20:
                    print(f"  📝 {stock} → {canonical}")
            except Exception as e:
                print(f"  ❌ 업데이트 실패 {s['id'][:8]}: {e}")
    
    if updated > 20:
        print(f"  ... 외 {updated - 20}개")
    print(f"✅ {updated}개 업데이트 완료")
    
    # 최종 결과
    print("\n" + "=" * 60)
    print(f"📊 최종 시그널: {len(signals)}개")
    print(f"🗑️ 삭제: {len(to_delete)}개")
    print(f"📝 업데이트: {updated}개")
    print("=" * 60)


if __name__ == "__main__":
    main()
