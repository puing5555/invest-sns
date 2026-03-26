"""
대담/인터뷰 의심 영상 V15.2 재분석 스크립트
- DB subtitle_text 우선, 없으면 yt-dlp로 추출
- V15.2 프롬프트 + channel_info + 20000자 한도
- --apply 플래그: 기존 시그널 DELETE → 새 시그널 INSERT
- --dry-run (기본): 결과만 출력, DB 미반영
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import json, requests, time, argparse
from pathlib import Path

# 프로젝트 루트 기준 환경변수
BASE_DIR = Path(__file__).parent.parent
env = {}
for line in (BASE_DIR / '.env.local').read_text(encoding='utf-8').splitlines():
    if '=' in line and not line.startswith('#'):
        k, v = line.split('=', 1)
        env[k.strip()] = v.strip()

SUPABASE_URL = env['NEXT_PUBLIC_SUPABASE_URL']
SUPABASE_KEY = env.get('SUPABASE_SERVICE_ROLE_KEY') or env.get('NEXT_PUBLIC_SUPABASE_ANON_KEY', '')
HEADERS = {'apikey': SUPABASE_KEY, 'Authorization': f'Bearer {SUPABASE_KEY}', 'Content-Type': 'application/json'}

from signal_analyzer_rest import SignalAnalyzer
from pipeline_config import PipelineConfig
from subtitle_extractor import SubtitleExtractor

SUBTITLE_LIMIT = 20000

# === 대상 영상 목록 (제목 키워드로 검색) ===
HYOSEOK_KEYWORDS = [
    '쇼미더 연수르',
    '스파클링 투자클럽',
    '스파클링',
    '함께효',
    '에릭',
    '유사남',
    '설명왕 테이버',
    '테슬라 전문가 몰아보기',
    '히치하이커를 위한 인터뷰',
]

ANYUHWA_KEYWORD = '안유화쇼'


def fetch_target_videos():
    """대상 영상 목록 조회"""
    videos = []
    seen_ids = set()

    # 이효석 대담 의심 영상
    for kw in HYOSEOK_KEYWORDS:
        r = requests.get(
            f'{SUPABASE_URL}/rest/v1/influencer_videos?select=id,video_id,title,published_at,subtitle_text,duration_seconds,'
            f'influencer_channels(channel_name,channel_type)'
            f'&title=like.*{kw}*&order=published_at.desc&limit=20',
            headers=HEADERS
        )
        for v in r.json():
            ch = (v.get('influencer_channels') or {}).get('channel_name', '')
            if '이효석' in ch and v['id'] not in seen_ids:
                seen_ids.add(v['id'])
                videos.append(v)

    # 안유화쇼 (자막 있는 것만)
    r = requests.get(
        f'{SUPABASE_URL}/rest/v1/influencer_videos?select=id,video_id,title,published_at,subtitle_text,duration_seconds,'
        f'influencer_channels(channel_name,channel_type)'
        f'&title=like.*{ANYUHWA_KEYWORD}*&subtitle_text=not.is.null&order=published_at.desc&limit=20',
        headers=HEADERS
    )
    for v in r.json():
        if v['id'] not in seen_ids:
            seen_ids.add(v['id'])
            videos.append(v)

    return videos


def get_existing_signals(video_uuid):
    """영상의 기존 시그널 조회"""
    r = requests.get(
        f'{SUPABASE_URL}/rest/v1/influencer_signals?select=id,stock,signal,speaker_id,speakers(name)'
        f'&video_id=eq.{video_uuid}&limit=50',
        headers=HEADERS
    )
    return r.json()


def delete_signals_for_video(video_uuid):
    """영상의 기존 시그널 삭제"""
    r = requests.delete(
        f'{SUPABASE_URL}/rest/v1/influencer_signals?video_id=eq.{video_uuid}',
        headers=HEADERS
    )
    return r.status_code in [200, 204]


def get_speaker_id(speaker_name, channel_name):
    """speaker_name → speaker_id 변환. 없으면 채널 운영자 speaker_id 반환."""
    if speaker_name and speaker_name != 'unknown_guest':
        # speakers 테이블에서 이름으로 검색
        r = requests.get(
            f'{SUPABASE_URL}/rest/v1/speakers?select=id&name=eq.{speaker_name}&limit=1',
            headers=HEADERS
        )
        sp = r.json()
        if sp:
            return sp[0]['id']

    # 채널 운영자 speaker_id (채널명으로 가장 많은 시그널의 speaker 조회)
    owner_name = PipelineConfig.get_channel_owner(channel_name)
    if owner_name:
        r = requests.get(
            f'{SUPABASE_URL}/rest/v1/speakers?select=id&name=eq.{owner_name}&limit=1',
            headers=HEADERS
        )
        sp = r.json()
        if sp:
            return sp[0]['id']

    return None


def insert_signals(signals, channel_name):
    """새 시그널 INSERT"""
    inserted = 0
    for sig in signals:
        speaker_name = sig.get('speaker_name', '')
        speaker_id = get_speaker_id(speaker_name, channel_name)

        if not speaker_id:
            print(f'    [WARN] speaker_id 찾을 수 없음: speaker={speaker_name}, channel={channel_name}')
            continue

        # signal_type: DB에서 사용하는 형태 (한글)
        raw_type = sig.get('signal_type', '중립')
        # convert_to_database_format이 영문으로 변환했으므로 다시 한글로
        eng_to_kr = {'BUY': '매수', 'POSITIVE': '긍정', 'NEUTRAL': '중립', 'CONCERN': '부정', 'SELL': '매도',
                     'STRONG_BUY': '매수', 'STRONG_SELL': '매도'}
        signal_val = eng_to_kr.get(raw_type, raw_type)

        # confidence 숫자 → 문자열
        conf = sig.get('confidence', 0.5)
        if isinstance(conf, (int, float)):
            if conf >= 0.9:
                conf_str = 'very_high'
            elif conf >= 0.7:
                conf_str = 'high'
            elif conf >= 0.5:
                conf_str = 'medium'
            else:
                conf_str = 'low'
        else:
            conf_str = str(conf)

        row = {
            'video_id': sig['video_uuid'],
            'speaker_id': speaker_id,
            'stock': sig.get('stock', ''),
            'ticker': sig.get('ticker', ''),
            'market': sig.get('market', 'OTHER'),
            'mention_type': '결론',
            'signal': signal_val,
            'confidence': conf_str,
            'key_quote': sig.get('key_quote', ''),
            'reasoning': sig.get('reasoning', ''),
            'timestamp': sig.get('timestamp'),
            'pipeline_version': 'V15.2',
        }

        r = requests.post(
            f'{SUPABASE_URL}/rest/v1/influencer_signals',
            headers={**HEADERS, 'Prefer': 'return=minimal'},
            json=row
        )
        if r.status_code in [200, 201]:
            inserted += 1
        else:
            print(f'    [WARN] INSERT 실패: {r.status_code} {r.text[:100]}')

    return inserted


def main():
    parser = argparse.ArgumentParser(description='대담 의심 영상 V15.2 재분석')
    parser.add_argument('--apply', action='store_true', help='DB에 반영 (기본: dry-run)')
    args = parser.parse_args()

    mode = 'APPLY' if args.apply else 'DRY-RUN'
    print(f'=== 대담 의심 영상 V15.2 재분석 [{mode}] ===\n')

    sa = SignalAnalyzer()
    se = SubtitleExtractor()

    videos = fetch_target_videos()
    print(f'대상 영상: {len(videos)}건\n')

    results = []
    total_old = 0
    total_new = 0
    total_guest = 0

    for i, v in enumerate(videos):
        ch = v.get('influencer_channels') or {}
        ch_name = ch.get('channel_name', '')
        ch_type = ch.get('channel_type', 'solo')
        owner = PipelineConfig.get_channel_owner(ch_name)
        title = v['title'][:60]

        print(f'[{i+1}/{len(videos)}] {title}')
        print(f'  채널: {ch_name} | 운영자: {owner} | 유형: {ch_type}')

        # 자막 확보
        subtitle = v.get('subtitle_text') or ''
        if len(subtitle) < 100:
            print(f'  자막 DB 없음 → yt-dlp 추출 중...')
            url = f'https://www.youtube.com/watch?v={v["video_id"]}'
            subtitle = se.extract_subtitle(url) or ''
            if not subtitle:
                print(f'  ❌ 자막 추출 실패, 건너뜀\n')
                continue
            print(f'  ✅ 자막 {len(subtitle)}자 추출')
        else:
            print(f'  DB 자막 사용 ({len(subtitle)}자)')

        subtitle = subtitle[:SUBTITLE_LIMIT]

        # 기존 시그널
        old_sigs = get_existing_signals(v['id'])
        total_old += len(old_sigs)
        print(f'  기존 시그널 {len(old_sigs)}건:')
        for s in old_sigs:
            sp = (s.get('speakers') or {}).get('name', 'null')
            print(f'    {s["stock"]} ({s["signal"]}) → speaker={sp}')

        # V15.2 재분석
        channel_info = {
            'channel_name': ch_name,
            'owner_name': owner or '불명',
            'channel_type': ch_type,
        }
        result = sa.analyze_video_subtitle(
            f'https://www.youtube.com/c/{ch_name}',
            {
                'title': v['title'],
                'url': f'https://www.youtube.com/watch?v={v["video_id"]}',
                'upload_date': (v.get('published_at') or '')[:10],
                'duration_seconds': v.get('duration_seconds'),
                'duration': f"{(v.get('duration_seconds') or 0)//60}:{(v.get('duration_seconds') or 0)%60:02d}",
            },
            subtitle,
            channel_info=channel_info
        )

        if not result or 'signals' not in result:
            print(f'  ❌ 분석 실패\n')
            continue

        new_sigs = result['signals']
        total_new += len(new_sigs)
        guest_count = sum(1 for s in new_sigs if s.get('speaker_name') and s['speaker_name'] != '')
        total_guest += guest_count

        print(f'  → V15.2 {len(new_sigs)}건 시그널 (게스트 {guest_count}건):')
        for s in new_sigs:
            sp = s.get('speaker_name') or 'null(=운영자)'
            marker = ' ★' if s.get('speaker_name') else ''
            print(f'    {s.get("stock","")} ({s.get("signal_type","")}) → speaker={sp}{marker} | conf={s.get("confidence","")}')

        # DB 반영
        if args.apply and new_sigs:
            print(f'  [APPLY] 기존 {len(old_sigs)}건 삭제 중...')
            if delete_signals_for_video(v['id']):
                # convert_to_database_format 사용
                db_signals = sa.convert_to_database_format(result, v['id'], 'V15.2', channel_info)
                db_signals = sa.deduplicate_signals(db_signals, v['title'])
                inserted = insert_signals(db_signals, ch_name)
                print(f'  [APPLY] {inserted}건 INSERT 완료')
            else:
                print(f'  [APPLY] DELETE 실패!')

        results.append({
            'title': v['title'][:50],
            'old': len(old_sigs),
            'new': len(new_sigs),
            'guest': guest_count,
        })

        print()
        if i < len(videos) - 1:
            time.sleep(5)

    # 요약
    print('='*60)
    print(f'=== 요약 [{mode}] ===')
    print(f'대상: {len(videos)}건 영상')
    print(f'기존 시그널: {total_old}건')
    print(f'V15.2 시그널: {total_new}건')
    print(f'게스트 감지: {total_guest}건')
    print()
    for r in results:
        print(f'  {r["title"]}: {r["old"]}→{r["new"]} (게스트 {r["guest"]}건)')


if __name__ == '__main__':
    main()
