"""Invidious 인스턴스 테스트"""
import requests

instances = [
    'https://vid.puffyan.us',
    'https://invidious.fdn.fr',
    'https://inv.nadeko.net',
    'https://invidious.nerdvpn.de',
    'https://yt.artemislena.eu',
    'https://yewtu.be',
    'https://inv.tux.pizza',
    'https://invidious.protokoll.zone',
    'https://iv.datura.network',
    'https://invidious.lunar.icu',
    'https://inv.in.projectsegfau.lt',
]

video_id = 'Ke7gQMbIFLI'

for inst in instances:
    try:
        r = requests.get(f'{inst}/api/v1/captions/{video_id}', timeout=10)
        if r.status_code == 200:
            data = r.json()
            captions = data.get('captions', [])
            labels = [c.get('label', '') for c in captions]
            print(f'[OK] {inst} - {len(captions)} captions: {labels}')
            
            # 한국어 자막 다운로드 시도
            for cap in captions:
                if 'ko' in cap.get('language_code', '') or 'Korean' in cap.get('label', ''):
                    caption_url = f"{inst}{cap['url']}"
                    r2 = requests.get(caption_url, timeout=10)
                    if r2.status_code == 200:
                        print(f'  -> Korean subtitle downloaded: {len(r2.text)} chars')
                        print(f'  -> Sample: {r2.text[:200]}')
                    else:
                        print(f'  -> Korean subtitle failed: {r2.status_code}')
                    break
            break
        else:
            print(f'[FAIL] {inst} - {r.status_code}')
    except Exception as e:
        print(f'[FAIL] {inst} - {type(e).__name__}: {str(e)[:80]}')
