"""투자 관련 영상 자막 다운로드"""
import subprocess, sys, os, time

SUBS_DIR = 'C:/Users/Mario/work/invest-sns/subs'

# V9 필터링 통과한 영상들
VIDEOS = {
    # 슈카월드
    'ksA4IT452_4': '삼성전자 사야 돼요?',
    'nm5zQxZSkbk': '스트래티지는 어떻게 비트코인을 계속 살 수 있을까?',
    'XveVkr3JHs4': '연초 이후 +24%, 코스피는 왜 강한가',
    'N7xO-UWCM5w': '삼성전자 시총 1,000조 돌파, 코스피 불꽃 상승',
    
    # 부읽남TV
    'Xv-wNA91EPE': '삼성전자 절대 팔지 마세요 [조진표]',
    'BVRoApF0c8k': '전세계 돈 다 빨아들일 겁니다 이 4개 주식 사세요 [배재규]',
    
    # 달란트투자 (한국어 영상 선별)
    '5mvn3PfKf9Y': '현대가 2조에 인수한다 세계최초 SMR 착공',
    
    # 이효석
    'fDZnPoK5lyc': '반도체 다음 무섭게 치고나갈 충격적 4종목',
    'ZXuQCpuVCYc': '국장 뜨겁다 코스피 ETF는 이거 사세요',
    'tSXkj2Omz34': '코스피 6000 돌파 7900 논리 공개',
    'B5owNUs_DFw': '소프트웨어 주식 사면 망합니다 헤지펀드가 몰래 산 ETF',
    'bmXgryWXNrw': '하이닉스 추가 매수 고민하는 분들',
}

for vid, title in VIDEOS.items():
    srt_path = f'{SUBS_DIR}/{vid}.ko.srt'
    vtt_path = f'{SUBS_DIR}/{vid}.ko.vtt'
    
    if os.path.exists(srt_path) or os.path.exists(vtt_path):
        print(f"[SKIP] {vid} - already have subtitles")
        continue
    
    url = f'https://www.youtube.com/watch?v={vid}'
    print(f"[DL] {vid} - {title}")
    
    cmd = [sys.executable, '-m', 'yt_dlp', 
           '--write-auto-sub', '--sub-lang', 'ko',
           '--skip-download', '--convert-subs', 'srt',
           '-o', f'{SUBS_DIR}/{vid}',
           url]
    
    result = subprocess.run(cmd, capture_output=True, timeout=60)
    
    if result.returncode == 0:
        # Check if srt was created
        if os.path.exists(srt_path):
            size = os.path.getsize(srt_path)
            print(f"  OK: {size} bytes")
        else:
            print(f"  WARN: no subtitle file created")
    else:
        stderr = result.stderr.decode('utf-8', errors='replace')
        if '429' in stderr:
            print(f"  RATE LIMITED - waiting 30s")
            time.sleep(30)
        else:
            print(f"  FAIL: {stderr[:150]}")
    
    time.sleep(3)

print("\n=== Summary ===")
for vid in VIDEOS:
    srt = f'{SUBS_DIR}/{vid}.ko.srt'
    exists = os.path.exists(srt)
    size = os.path.getsize(srt) if exists else 0
    status = f"OK ({size}B)" if exists else "MISSING"
    print(f"  {vid}: {status}")
