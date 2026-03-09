import urllib.request, json, sys, os
sys.stdout.reconfigure(encoding='utf-8')

env = {}
for line in open('.env.local', encoding='utf-8'):
    line = line.strip()
    if '=' in line and not line.startswith('#'):
        k, v = line.split('=', 1)
        env[k.strip()] = v.strip()

url = env.get('NEXT_PUBLIC_SUPABASE_URL')
key = env.get('SUPABASE_SERVICE_ROLE_KEY') or env.get('NEXT_PUBLIC_SUPABASE_ANON_KEY')
headers = {'apikey': key, 'Authorization': f'Bearer {key}'}

# 코린이아빠 채널 확인
req = urllib.request.Request(
    f'{url}/rest/v1/influencer_channels?channel_handle=ilike.*corinpapa*&select=id,channel_name,channel_handle',
    headers=headers
)
with urllib.request.urlopen(req) as r:
    channels = json.loads(r.read())
print(f'채널 검색 결과: {channels}')

if channels:
    ch_id = channels[0]['id']
    # 비디오 수
    req2 = urllib.request.Request(
        f'{url}/rest/v1/influencer_videos?channel_id=eq.{ch_id}&select=id',
        headers={**headers, 'Prefer': 'count=exact', 'Range': '0-0'}
    )
    with urllib.request.urlopen(req2) as r:
        cr = r.getheader('Content-Range', '?')
        print(f'비디오 수: {cr}')

    # 시그널 수
    req3 = urllib.request.Request(
        f'{url}/rest/v1/influencer_signals?select=id,video_id,influencer_videos!inner(channel_id)&influencer_videos.channel_id=eq.{ch_id}',
        headers={**headers, 'Prefer': 'count=exact', 'Range': '0-0'}
    )
    try:
        with urllib.request.urlopen(req3) as r:
            cr = r.getheader('Content-Range', '?')
            print(f'시그널 수: {cr}')
    except Exception as e:
        print(f'시그널 조회 에러: {e}')
else:
    print('채널 없음 - DB에 코린이아빠 없음')
