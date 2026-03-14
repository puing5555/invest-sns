"""
gemini_analyzer.py media_resolution=LOW 속도 테스트
영상 1개 분석 시간 측정
"""
import sys, os, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.stdout.reconfigure(encoding='utf-8')

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env.local'))

# DB에서 영상 1개 가져오기
import requests as req
SUPABASE_URL = os.environ['NEXT_PUBLIC_SUPABASE_URL']
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY') or os.environ['NEXT_PUBLIC_SUPABASE_ANON_KEY']
h = {'apikey': SUPABASE_KEY, 'Authorization': f'Bearer {SUPABASE_KEY}'}

r = req.get(
    f'{SUPABASE_URL}/rest/v1/influencer_videos'
    '?select=video_id,title,duration_seconds,channel_id'
    '&video_id=eq.mf2P0Aw3odU',
    headers=h
)
v = r.json()[0]
video_id = v['video_id']
title = v['title']
dur = v.get('duration_seconds', 600)

print(f"테스트 영상: {video_id}")
print(f"제목: {title}")
print(f"길이: {dur}초 ({dur//60}분 {dur%60:02d}초)")
print("-" * 50)

video_data = {
    'video_id': video_id,
    'title': title,
    'url': f'https://www.youtube.com/watch?v={video_id}',
    'duration': dur,
    'duration_seconds': dur,
    'upload_date': '',
    'channel_url': '',
}

from scripts.gemini_analyzer import analyze_video_with_gemini

print("⏱️  분석 시작...")
t0 = time.time()
signals = analyze_video_with_gemini(video_data, retry=1)
elapsed = time.time() - t0

print(f"\n{'='*50}")
print(f"⏱️  소요 시간: {elapsed:.1f}초 ({elapsed/60:.1f}분)")
print(f"📊 추출 시그널: {len(signals)}개")
for s in signals:
    print(f"   - [{s.get('signal_type')}] {s.get('stock')} (confidence={s.get('confidence')})")
