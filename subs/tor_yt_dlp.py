"""Tor를 이용한 yt-dlp 우회 시도"""
import subprocess
import sys
import os
import time
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)

VID = 'ksA4IT452_4'
SUBS_DIR = 'C:/Users/Mario/work/invest-sns/subs'

print("=== Tor + yt-dlp 시도 ===")

# 1. Tor 설치 확인
def check_tor():
    """Tor 설치 상태 확인"""
    try:
        result = subprocess.run(['tor', '--version'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✅ Tor 설치됨")
            return True
    except:
        pass
    
    print("❌ Tor 미설치 - 설치 시도")
    return False

# 2. Tor via Chocolatey 설치 시도
def install_tor():
    """Chocolatey를 통한 Tor 설치"""
    try:
        print("Chocolatey로 Tor 설치 시도...")
        subprocess.run(['choco', 'install', 'tor', '-y'], check=True)
        print("✅ Tor 설치 완료")
        return True
    except:
        print("❌ Chocolatey 설치 실패")
        return False

# 3. Tor 서비스 시작
def start_tor():
    """Tor 서비스 시작"""
    try:
        print("Tor 서비스 시작...")
        # Windows에서 Tor 시작
        tor_process = subprocess.Popen(['tor'], 
                                       stdout=subprocess.PIPE, 
                                       stderr=subprocess.PIPE)
        
        # Tor 시작 대기 (10초)
        print("Tor 부팅 대기 중...")
        time.sleep(10)
        
        return tor_process
    except Exception as e:
        print(f"❌ Tor 시작 실패: {e}")
        return None

# 4. SOCKS5 프록시로 yt-dlp 실행
def download_with_tor():
    """Tor SOCKS5 프록시를 통한 yt-dlp 실행"""
    try:
        print(f"yt-dlp with Tor SOCKS5 프록시...")
        
        cmd = [sys.executable, '-m', 'yt_dlp',
               '--write-auto-sub', '--sub-lang', 'ko',
               '--skip-download', '--convert-subs', 'srt',
               '--proxy', 'socks5://127.0.0.1:9050',  # Tor SOCKS5 포트
               '--socket-timeout', '30',
               '--user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0',
               '-o', f'{SUBS_DIR}/{VID}',
               f'https://www.youtube.com/watch?v={VID}']
        
        print(f"실행: {' '.join(cmd[-4:])}")
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        # 결과 확인
        if os.path.exists(f'{SUBS_DIR}/{VID}.ko.srt') or os.path.exists(f'{SUBS_DIR}/{VID}.ko.vtt'):
            print("✅ Tor 우회 성공!")
            return True
        else:
            print(f"❌ Tor 우회 실패: {result.stderr[:200] if result.stderr else 'No error'}")
            return False
            
    except Exception as e:
        print(f"❌ yt-dlp 실행 오류: {e}")
        return False

# 메인 프로세스
if not check_tor():
    if not install_tor():
        print("Tor 설치 불가 - 다른 방법 시도 필요")
        exit(1)

# Tor 시작
tor_process = start_tor()
if tor_process is None:
    print("Tor 시작 실패")
    exit(1)

try:
    # Tor를 통한 다운로드 시도
    success = download_with_tor()
    
    if success:
        print("🎉 Tor 우회 자막 다운로드 성공!")
    else:
        print("❌ Tor 우회도 실패")
        
finally:
    # Tor 프로세스 종료
    if tor_process:
        print("Tor 프로세스 종료...")
        tor_process.terminate()
        try:
            tor_process.wait(timeout=5)
        except:
            tor_process.kill()
        print("✅ Tor 종료 완료")

# 최종 확인
for ext in ['srt', 'vtt']:
    path = f'{SUBS_DIR}/{VID}.ko.{ext}'
    if os.path.exists(path):
        size = os.path.getsize(path)
        print(f"✅ 자막 파일: {VID}.ko.{ext} ({size} bytes)")
        break
else:
    print("❌ 자막 파일 없음")