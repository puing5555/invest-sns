"""OpenClaw 브라우저 스크립트 패널에서 자막 추출 결과를 파일로 저장하는 헬퍼"""
import json, sys

# stdin에서 JSON 배열 읽어서 파일로 저장
def save(vid, channel, data_json, out_dir='C:/Users/Mario/work/subs'):
    data = json.loads(data_json)
    path = f'{out_dir}/{channel}_{vid}.json'
    with open(path, 'w', encoding='utf-8') as f:
        json.dump({
            'video_id': vid,
            'channel': channel,
            'subtitles': data
        }, f, ensure_ascii=False, indent=2)
    print(f'Saved {len(data)} segments to {path}')

if __name__ == '__main__':
    vid = sys.argv[1]
    channel = sys.argv[2]
    data = sys.stdin.read()
    save(vid, channel, data)
