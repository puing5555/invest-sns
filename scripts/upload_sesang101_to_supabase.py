#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
?몄긽?숆컻濡??쒓렇?먯쓣 Supabase???낅줈?쒗븯???ㅽ겕由쏀듃
"""

import os
import json
import requests
from datetime import datetime
from typing import Dict, List

# ?섍꼍 蹂??濡쒕뱶
from dotenv import load_dotenv
load_dotenv()

# Supabase ?ㅼ젙
SUPABASE_URL = "https://arypzhotxflimroprmdk.supabase.co"
SUPABASE_SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8"

def load_signals_data():
    """?몄긽?숆컻濡??쒓렇???곗씠??濡쒕뱶"""
    try:
        with open("sesang101_supabase_upload.json", 'r', encoding='utf-8') as f:
            signals = json.load(f)
        
        print(f"[LOAD] {len(signals)}媛??쒓렇??濡쒕뱶")
        return signals
    
    except Exception as e:
        print(f"[ERR] ?쒓렇???곗씠??濡쒕뱶 ?ㅽ뙣: {e}")
        return []

def check_supabase_connection():
    """Supabase ?곌껐 ?뚯뒪??""
    try:
        headers = {
            'apikey': SUPABASE_SERVICE_KEY,
            'Authorization': f'Bearer {SUPABASE_SERVICE_KEY}',
            'Content-Type': 'application/json'
        }
        
        # ?뚯씠釉?援ъ“ ?뺤씤
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/influencer_signals?select=id&limit=1",
            headers=headers
        )
        
        if response.status_code == 200:
            print("[OK] Supabase ?곌껐 ?깃났")
            return True
        else:
            print(f"[ERR] Supabase ?곌껐 ?ㅽ뙣: {response.status_code}")
            return False
    
    except Exception as e:
        print(f"[ERR] ?곌껐 ?뚯뒪???ㅽ뙣: {e}")
        return False

def check_existing_signals():
    """湲곗〈 ?몄긽?숆컻濡??쒓렇???뺤씤"""
    try:
        headers = {
            'apikey': SUPABASE_SERVICE_KEY,
            'Authorization': f'Bearer {SUPABASE_SERVICE_KEY}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/influencer_signals?select=id,video_id&channel_name=eq.?몄긽?숆컻濡?,
            headers=headers
        )
        
        if response.status_code == 200:
            existing = response.json()
            print(f"[CHECK] 湲곗〈 ?몄긽?숆컻濡??쒓렇?? {len(existing)}媛?)
            return [signal['video_id'] for signal in existing]
        else:
            print(f"[ERR] 湲곗〈 ?쒓렇??議고쉶 ?ㅽ뙣: {response.status_code}")
            return []
    
    except Exception as e:
        print(f"[ERR] 湲곗〈 ?쒓렇???뺤씤 ?ㅽ뙣: {e}")
        return []

def batch_upload_signals(signals):
    """?쒓렇?먯쓣 諛곗튂濡?Supabase???낅줈??""
    headers = {
        'apikey': SUPABASE_SERVICE_KEY,
        'Authorization': f'Bearer {SUPABASE_SERVICE_KEY}',
        'Content-Type': 'application/json',
        'Prefer': 'resolution=merge-duplicates'
    }
    
    # 湲곗〈 ?쒓렇???뺤씤
    existing_video_ids = set(check_existing_signals())
    
    # ?덈줈???쒓렇?먮쭔 ?꾪꽣留?
    new_signals = []
    for signal in signals:
        if signal['video_id'] not in existing_video_ids:
            new_signals.append(signal)
    
    if not new_signals:
        print("[INFO] ?낅줈?쒗븷 ???쒓렇?먯씠 ?놁뒿?덈떎")
        return True
    
    print(f"[UPLOAD] {len(new_signals)}媛????쒓렇???낅줈???쒖옉")
    
    # 20媛쒖뵫 諛곗튂濡??낅줈??
    batch_size = 20
    success_count = 0
    
    for i in range(0, len(new_signals), batch_size):
        batch = new_signals[i:i+batch_size]
        
        try:
            response = requests.post(
                f"{SUPABASE_URL}/rest/v1/influencer_signals",
                headers=headers,
                json=batch
            )
            
            if response.status_code in [200, 201]:
                success_count += len(batch)
                print(f"[OK] 諛곗튂 {i//batch_size + 1}: {len(batch)}媛??낅줈???깃났")
            else:
                print(f"[ERR] 諛곗튂 {i//batch_size + 1} ?ㅽ뙣: {response.status_code}")
                print(f"[ERR] ?묐떟: {response.text[:500]}")
        
        except Exception as e:
            print(f"[ERR] 諛곗튂 {i//batch_size + 1} ?낅줈???ㅽ뙣: {e}")
    
    print(f"[DONE] 珥?{success_count}/{len(new_signals)}媛??쒓렇???낅줈???꾨즺")
    return success_count > 0

def update_project_status():
    """PROJECT_STATUS.md ?낅뜲?댄듃"""
    try:
        status_file = "PROJECT_STATUS.md"
        
        # ?꾩옱 ?좎쭨 ?쒓컙
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        # ?덈줈???낅뜲?댄듃 ?댁슜
        new_update = f"""
## ?뵦 理쒖떊 ?낅뜲?댄듃 ({now}) ??

### ?몄긽?숆컻濡??쒓렇??遺꾩꽍 + PDF 567嫄?AI ?붿빟 吏꾪뻾以??렞
1. **?몄긽?숆컻濡?98媛??곸긽 ?쒓렇??遺꾩꽍 ?꾨즺** ??
   - batch 1-9 紐⑤뱺 ?곸긽 泥섎━ ?꾨즺
   - ?먮낯 ?쒓렇?? 181媛???以묐났?쒓굅 ?? 87媛?(1?곸긽 1醫낅ぉ 1?쒓렇??
   - 51媛??좉퇋 醫낅ぉ signal_prices.json 異붽?
   - Supabase influencer_signals ?뚯씠釉붿뿉 ?낅줈???꾨즺
   - ?쒓렇??8媛吏 ??? 留ㅼ닔/湲띿젙/以묐┰/寃쎄퀎/留ㅻ룄 ??

2. **PDF 567嫄?AI ?붿빟 諛곗튂 泥섎━ 吏꾪뻾以?* ??
   - Claude API(claude-sonnet-4-6) ?ъ슜
   - AI ?쒖쨪?붿빟 + ?곸꽭?붿빟 + ?좊꼸由ъ뒪?몃챸 異붿텧
   - ?덉씠?몃━諛?以?? 2珥?媛꾧꺽, 50媛쒕쭏??1遺??댁떇
   - analyst_reports ?뚯씠釉붿뿉 ai_summary, ai_detail, analyst_name 而щ읆 ?낅뜲?댄듃 ?덉젙
   - 吏꾪뻾?곹솴: 諛깃렇?쇱슫?쒖뿉??泥섎━ 以?

3. **湲곗닠???꾩꽦??* ??
   - ?쒓렇??以묐났?쒓굅 ?뚯씠?꾨씪??援ъ텞
   - PDF ?띿뒪??異붿텧 + AI ?붿빟 ?쒖뒪??
   - signal_prices.json ?먮룞 ?낅뜲?댄듃
   - public/signal_prices.json ?숆린??

**?ㅼ쓬 ?④퀎**: 
- PDF 567嫄?泥섎━ ?꾨즺 ?湲?
- git commit 諛?諛고룷
- npm run build; npx gh-pages -d out

---

"""
        
        # 湲곗〈 ?뚯씪 ?쎄린
        with open(status_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 泥?踰덉㎏ ## ?낅뜲?댄듃 ?뱀뀡 李얠븘??援먯껜
        lines = content.split('\n')
        new_lines = []
        skip_until_next_section = False
        added_new_update = False
        
        for line in lines:
            if line.startswith('## ?뵦 理쒖떊 ?낅뜲?댄듃') and not added_new_update:
                # ???낅뜲?댄듃 異붽?
                new_lines.extend(new_update.strip().split('\n'))
                added_new_update = True
                skip_until_next_section = True
            elif line.startswith('##') and skip_until_next_section and added_new_update:
                # ?ㅼ쓬 ?뱀뀡 ?쒖옉
                skip_until_next_section = False
                new_lines.append(line)
            elif not skip_until_next_section:
                new_lines.append(line)
        
        # ?뚯씪???곌린
        with open(status_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(new_lines))
        
        print(f"[UPDATE] {status_file} ?낅뜲?댄듃 ?꾨즺")
        
    except Exception as e:
        print(f"[ERR] PROJECT_STATUS.md ?낅뜲?댄듃 ?ㅽ뙣: {e}")

def main():
    """硫붿씤 ?ㅽ뻾 ?⑥닔"""
    print("[START] ?몄긽?숆컻濡??쒓렇??Supabase ?낅줈??n")
    
    # 1. Supabase ?곌껐 ?뺤씤
    if not check_supabase_connection():
        return
    
    # 2. ?쒓렇???곗씠??濡쒕뱶
    signals = load_signals_data()
    if not signals:
        return
    
    # 3. Supabase???낅줈??
    if batch_upload_signals(signals):
        print("[SUCCESS] ?쒓렇???낅줈???깃났!")
    else:
        print("[FAIL] ?쒓렇???낅줈???ㅽ뙣")
        return
    
    # 4. PROJECT_STATUS.md ?낅뜲?댄듃
    update_project_status()
    
    print("\n[DONE] ?몄긽?숆컻濡??쒓렇??泥섎━ ?꾨즺!")

if __name__ == "__main__":
    main()
