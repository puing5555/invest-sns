import subprocess, json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

result = subprocess.run(
    ['python', '-m', 'yt_dlp', '--flat-playlist', '--dump-json', 'https://www.youtube.com/@wsaj/videos'],
    capture_output=True, text=True, encoding='utf-8'
)
videos = [json.loads(line) for line in result.stdout.strip().split('\n') if line.strip()]
print(f'Total: {len(videos)}')

# Investment-related keywords for filtering
invest_keywords = ['주식', '투자', '매수', '매도', '종목', 'ETF', 'S&P', '나스닥', '코스피', '금리', 
    '인플레이션', 'FOMC', '연준', '달러', '환율', '채권', '배당', 'PER', 'PBR', 
    '실적', '어닝', '테슬라', '엔비디아', 'AI', '반도체', '트럼프', '관세',
    '매크로', '경제', '금융', '시장', '포트폴리오', '자산', '수익률', '밸류에이션',
    '버블', '폭락', '상승', '하락', 'GDP', 'CPI', '물가', '디플레이션',
    'Bitcoin', '비트코인', '암호화폐', 'IPO', '공매도', '헤지펀드', '월가',
    '레버리지', 'TQQQ', 'SOXL', '옵션', '선물', '파생', '거시', '미시',
    '기업분석', '재무제표', '배당금', '리츠', 'REIT', '부동산',
    '40주간의', '월스트리트', '주식기초강의', '경제지표', '시즌']

for i, v in enumerate(videos):
    title = v.get('title', '')
    vid = v.get('id', '')
    date = v.get('upload_date', 'NA')
    is_invest = any(kw in title for kw in invest_keywords)
    marker = '✅' if is_invest else '❌'
    print(f'{marker} {vid} | {title} | {date}')
