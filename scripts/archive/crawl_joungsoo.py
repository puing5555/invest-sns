"""종목왕 김정수 @joungsoo 채널 전체 영상 크롤링 + 투자 필터링"""
import subprocess, sys, io, re, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=== @joungsoo 채널 전체 영상 크롤링 중... ===")
print("(시간 걸릴 수 있음)\n")

# 전체 영상 목록 (no-flat-playlist로 날짜 포함)
r = subprocess.run(
    [sys.executable, '-m', 'yt_dlp',
     '--skip-download', '--no-flat-playlist',
     '--print', '%(upload_date)s\t%(title)s\t%(id)s\t%(duration)s',
     'https://www.youtube.com/@joungsoo/videos'],
    capture_output=True, text=True, timeout=1800  # 30분
)

videos = []
for line in r.stdout.strip().split('\n'):
    if not line.strip():
        continue
    parts = line.split('\t', 3)
    if len(parts) >= 3:
        date, title, vid_id = parts[0], parts[1], parts[2]
        dur = parts[3] if len(parts) == 4 else 'NA'
        d = date
        date_fmt = f"{d[:4]}-{d[4:6]}-{d[6:]}" if len(d) == 8 and d != 'NA' else d
        videos.append({'date': date_fmt, 'title': title, 'id': vid_id, 'duration': dur})

print(f"전체 영상: {len(videos)}개\n")

# 에러 체크
member_count = 0
if r.stderr:
    for line in r.stderr.split('\n'):
        if 'members' in line.lower():
            member_count += 1
if member_count:
    print(f"멤버십 전용: {member_count}개 (접근 불가)\n")

# 투자 키워드
invest_keywords = [
    '종목', '매수', '매도', '추천', '목표가', '분석', '전망', '주가', '급등', '급락',
    '상승', '하락', '수익률', '배당', '실적', '어닝', '시가총액', '차트', '눌림목',
    '반등', '돌파', '지지', '저항', '테마', '섹터', '대장주', '수급', '외국인',
    '기관', '개인', '공매도', '코스피', '코스닥', '나스닥', 'S&P', '다우',
    '삼성', 'SK', 'LG', '현대', '카카오', '네이버', '셀트리온', '삼전',
    '반도체', '2차전지', '배터리', 'AI', '로봇', '바이오', '제약', '자동차',
    '조선', '방산', '원전', '태양광', '풍력', '수소', '전력',
    '테슬라', '엔비디아', 'NVDA', '애플', '마이크로소프트', '구글', '아마존',
    '팔란티어', 'PLTR', '비트코인', 'BTC', '이더리움', 'ETH',
    '사야', '팔아야', '담아', '물타기', '손절', '익절',
    '포트폴리오', '리밸런싱', '편입', '비중',
    '시황', '증시', '장전', '장후', '마감', '개장',
]

# 비투자 키워드
skip_keywords = [
    '브이로그', 'vlog', '먹방', '일상', 'Q&A', 'QnA', '라이브', 'LIVE',
    '구독자', '이벤트', '당첨', '공지', '인사', '감사', '축하',
    '요리', '운동', '헬스', '골프', '여행', '맛집', '카페',
    '언박싱', 'unboxing',
]

invest_videos = []
non_invest = []

for v in videos:
    title_lower = v['title'].lower()
    
    # 비투자 키워드 체크
    if any(kw.lower() in title_lower for kw in skip_keywords):
        non_invest.append(v)
        continue
    
    # 투자 키워드 체크
    if any(kw.lower() in title_lower for kw in invest_keywords):
        invest_videos.append(v)
    else:
        # 키워드 없지만 제목이 애매한 것은 일단 non_invest
        non_invest.append(v)

print(f"━━━━━━━━━━━━━━━━━━")
print(f"전체: {len(videos)}개")
print(f"투자 관련: {len(invest_videos)}개")
print(f"비투자/기타: {len(non_invest)}개")
print(f"━━━━━━━━━━━━━━━━━━\n")

print(f"=== 투자 관련 영상 ({len(invest_videos)}개) ===\n")
for i, v in enumerate(invest_videos, 1):
    print(f"  {i:3d}. {v['date']} | {v['title']} | {v['id']}")

print(f"\n=== 비투자/미분류 영상 ({len(non_invest)}개) ===\n")
for i, v in enumerate(non_invest, 1):
    print(f"  {i:3d}. {v['date']} | {v['title']} | {v['id']}")

# JSON 저장
result = {
    'total': len(videos),
    'invest': len(invest_videos),
    'non_invest': len(non_invest),
    'membership': member_count,
    'invest_videos': invest_videos,
    'non_invest_videos': non_invest,
}
with open('joungsoo_videos.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print(f"\n결과 저장: joungsoo_videos.json")
