#!/usr/bin/env python3
"""
세상학개론 시그널 4가지 문제 수정 - 전체 실행 스크립트

1. key_quote/reasoning 수정 (82개 시그널)
2. 잘못된 종목 정리  
3. 최근 영상 크롤링
4. 해외주식/코인 종목 페이지
5. signal_prices.json 업데이트
6. git commit & build & deploy
"""
import os
import subprocess
import time
from datetime import datetime

def run_command(cmd, description):
    """명령어 실행"""
    print(f"\n🚀 {description}")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode == 0:
            print(f"✅ {description} - SUCCESS")
            if result.stdout.strip():
                print("Output:", result.stdout[:500])
            return True
        else:
            print(f"❌ {description} - FAILED")
            print("Error:", result.stderr[:500])
            return False
            
    except Exception as e:
        print(f"❌ {description} - EXCEPTION: {e}")
        return False

def ask_confirmation(task_name):
    """사용자 확인"""
    response = input(f"\n❓ Execute {task_name}? (y/N): ").lower().strip()
    return response == 'y'

def main():
    print("🎯 세상학개론 시그널 4가지 문제 수정")
    print("="*50)
    
    start_time = time.time()
    results = {}
    
    # 작업 1: key_quote/reasoning 수정 (선택적)
    if ask_confirmation("Task 1: Fix key_quote/reasoning (82 signals)"):
        print("\n📝 작업 1: key_quote/reasoning 수정")
        print("⚠️  This will take 10-15 minutes (2 sec delay per signal)")
        
        if ask_confirmation("Continue with Claude API calls"):
            results['task1'] = run_command(
                ['python', 'fix_all_sesang_signals.py'],
                "Task 1: Fixing key_quote/reasoning with Claude API"
            )
        else:
            results['task1'] = None
            print("⏭️  Task 1 skipped")
    else:
        results['task1'] = None
        print("⏭️  Task 1 skipped")
    
    # 작업 2: 잘못된 종목 정리
    print("\n🧹 작업 2: 잘못된 종목 정리")
    results['task2'] = run_command(
        ['python', 'clean_wrong_stocks.py'],
        "Task 2: Cleaning wrong stock names"
    )
    
    # 작업 3: 최근 영상 크롤링
    print("\n📺 작업 3: 최근 영상 크롤링")
    results['task3'] = run_command(
        ['python', 'crawl_recent_videos.py'],
        "Task 3: Crawling recent videos"
    )
    
    # 작업 4: 해외주식/코인 종목 페이지
    print("\n🌍 작업 4: 해외주식/코인 종목 페이지")
    results['task4'] = run_command(
        ['python', 'add_global_stock_pages.py'],
        "Task 4: Adding global stock pages"
    )
    
    # 작업 5: signal_prices.json 업데이트
    print("\n📊 작업 5: signal_prices.json 업데이트")
    results['task5'] = run_command(
        ['python', 'update_signal_prices.py'],
        "Task 5: Updating signal_prices.json"
    )
    
    # 작업 6: Git 커밋
    print("\n📝 작업 6: Git 커밋")
    
    # Git status 확인
    run_command(['git', 'status'], "Checking git status")
    
    if ask_confirmation("Git add & commit"):
        commit_msg = f"feat: 세상학개론 시그널 개선 작업 완료 - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        results['git_add'] = run_command(
            ['git', 'add', '-A'],
            "Git add all changes"
        )
        
        results['git_commit'] = run_command(
            ['git', 'commit', '-m', commit_msg],
            f"Git commit: {commit_msg}"
        )
    else:
        results['git_add'] = None
        results['git_commit'] = None
        print("⏭️  Git commit skipped")
    
    # 작업 7: Build & Deploy
    if ask_confirmation("Build & Deploy"):
        print("\n🏗️  작업 7: Build & Deploy")
        
        results['build'] = run_command(
            ['npm', 'run', 'build'],
            "Next.js build"
        )
        
        if results['build']:
            results['deploy'] = run_command(
                ['npx', 'gh-pages', '-d', 'out'],
                "GitHub Pages deploy"
            )
        else:
            results['deploy'] = False
            print("❌ Build failed, skipping deploy")
    else:
        results['build'] = None
        results['deploy'] = None
        print("⏭️  Build & Deploy skipped")
    
    # 결과 요약
    end_time = time.time()
    duration = end_time - start_time
    
    print("\n" + "="*50)
    print("🎉 세상학개론 시그널 개선 작업 완료!")
    print(f"⏱️  총 소요시간: {duration/60:.1f}분")
    
    print("\n📊 작업 결과:")
    task_names = {
        'task1': '1. key_quote/reasoning 수정',
        'task2': '2. 잘못된 종목 정리',
        'task3': '3. 최근 영상 크롤링', 
        'task4': '4. 해외주식/코인 종목 페이지',
        'task5': '5. signal_prices.json 업데이트',
        'git_add': '6-1. Git add',
        'git_commit': '6-2. Git commit',
        'build': '7-1. Next.js build',
        'deploy': '7-2. GitHub Pages deploy'
    }
    
    for task, name in task_names.items():
        status = results.get(task)
        if status is None:
            print(f"  ⏭️  {name}: SKIPPED")
        elif status:
            print(f"  ✅ {name}: SUCCESS") 
        else:
            print(f"  ❌ {name}: FAILED")
    
    success_count = sum(1 for r in results.values() if r is True)
    total_count = sum(1 for r in results.values() if r is not None)
    
    print(f"\n🎯 성공률: {success_count}/{total_count} ({success_count/total_count*100:.1f}%)" if total_count > 0 else "")
    
    # 다음 단계 안내
    print("\n📋 다음 단계:")
    print("  1. 각 작업별 결과 파일 확인:")
    print("     - sesang_signals_fixed.json (Task 1)")
    print("     - stock_cleanup_result.json (Task 2)")
    print("     - recent_video_crawl_result.json (Task 3)")  
    print("     - global_stock_pages_result.json (Task 4)")
    print("  2. 웹사이트에서 업데이트된 데이터 확인")
    print("  3. 해외주식/코인 페이지 테스트")
    
    if results.get('deploy'):
        print("  4. 🎉 배포 완료! 사이트를 확인하세요.")

if __name__ == "__main__":
    main()