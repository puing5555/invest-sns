"""종목왕 김정수 @joungsoo - flat-playlist로 빠르게 전체 목록"""
import subprocess, sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=== @joungsoo 전체 영상 flat-playlist 크롤링 ===\n")

# Step 1: flat-playlist로 전체 ID+제목 (빠름)
r = subprocess.run(
    [sys.executable, '-m', 'yt_dlp', '--flat-playlist',
     '--print', '%(id)s\t%(title)s',
     'https://www.youtube.com/@joungsoo/videos'],
    capture_output=True, text=True, timeout=300
)

videos = []
for line in r.stdout.strip().split('\n'):
    if not line.strip():
        continue
    parts = line.split('\t', 1)
    if len(parts) == 2:
        videos.append({'id': parts[0], 'title': parts[1]})

print(f"전체 영상: {len(videos)}개\n")

# Step 2: 최근 50개만 날짜 확인 (no-flat-playlist, 제한)
print("최근 50개 날짜 확인 중...")
r2 = subprocess.run(
    [sys.executable, '-m', 'yt_dlp', '--skip-download', '--no-flat-playlist',
     '--print', '%(id)s\t%(upload_date)s',
     '--playlist-end', '50',
     'https://www.youtube.com/@joungsoo/videos'],
    capture_output=True, text=True, timeout=600
)

date_map = {}
for line in r2.stdout.strip().split('\n'):
    if not line.strip():
        continue
    parts = line.split('\t', 1)
    if len(parts) == 2:
        vid_id, date = parts
        d = date
        date_fmt = f"{d[:4]}-{d[4:6]}-{d[6:]}" if len(d) == 8 and d != 'NA' else d
        date_map[vid_id] = date_fmt

print(f"날짜 확인: {len(date_map)}개\n")

# 투자 키워드
invest_kw = [
    '종목', '매수', '매도', '추천', '목표가', '분석', '전망', '주가', '급등', '급락',
    '상승', '하락', '수익률', '배당', '실적', '차트', '눌림목', '반등', '돌파',
    '지지', '저항', '테마', '섹터', '대장주', '수급', '외국인', '기관',
    '코스피', '코스닥', '나스닥', '반도체', '2차전지', '배터리', 'AI', '로봇',
    '바이오', '제약', '자동차', '조선', '방산', '원전', '전력', '에너지',
    '삼성', 'SK', 'LG', '현대', '카카오', '네이버', '셀트리온', 'HPSP',
    '테슬라', '엔비디아', '애플', '마이크로소프트', '구글', '아마존', '팔란티어',
    '비트코인', 'BTC', '이더리움', '코인',
    '사야', '팔아야', '담아', '물타기', '손절', '익절',
    '포트폴리오', '편입', '비중', '시황', '증시', '장전', '장후', '마감', '개장',
    '수익', '손실', '계좌', '투자', '주식', '매매', '트레이딩', '스윙', '단타',
    'PER', 'PBR', 'EPS', 'ROE', '밸류에이션', '저평가', '고평가',
    '관세', '금리', '환율', '달러', '유가', '금값',
]

skip_kw = [
    '브이로그', 'vlog', '먹방', '일상', 'Q&A', 'QnA', '라이브', 'LIVE',
    '구독자', '이벤트', '당첨', '공지', '인사', '감사', '축하',
    '요리', '운동', '헬스', '골프', '여행', '맛집', '카페', '언박싱',
]

invest_videos = []
non_invest = []

for v in videos:
    v['date'] = date_map.get(v['id'], '?')
    title_lower = v['title'].lower()
    
    if any(kw.lower() in title_lower for kw in skip_kw):
        non_invest.append(v)
        continue
    
    if any(kw.lower() in title_lower for kw in invest_kw):
        invest_videos.append(v)
    else:
        non_invest.append(v)

print(f"━━━━━━━━━━━━━━━━━━")
print(f"전체: {len(videos)}개")
print(f"투자 관련: {len(invest_videos)}개")
print(f"비투자/미분류: {len(non_invest)}개")
print(f"━━━━━━━━━━━━━━━━━━\n")

print(f"=== 투자 관련 영상 ({len(invest_videos)}개) ===\n")
for i, v in enumerate(invest_videos, 1):
    print(f"  {i:3d}. [{v['date']}] {v['title']} | {v['id']}")

print(f"\n=== 비투자/미분류 ({len(non_invest)}개) ===\n")
for i, v in enumerate(non_invest, 1):
    print(f"  {i:3d}. [{v['date']}] {v['title']} | {v['id']}")

# 저장
with open('joungsoo_videos.json', 'w', encoding='utf-8') as f:
    json.dump({'total': len(videos), 'invest': len(invest_videos), 
               'invest_videos': invest_videos, 'non_invest_videos': non_invest}, f, ensure_ascii=False, indent=2)
print(f"\n저장: joungsoo_videos.json")
