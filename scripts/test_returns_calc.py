#!/usr/bin/env python3
"""안유화 69개 시그널로 수익률 자동 계산 테스트"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db_inserter_rest import DatabaseInserter

db = DatabaseInserter()
result = db.calculate_returns_for_signals()

print(f"\n=== 최종 결과 ===")
print(f"업데이트: {result['updated']}")
print(f"스킵: {result['skipped']}")
print(f"에러: {len(result['errors'])}")
if result['errors'][:10]:
    print("\n에러 샘플:")
    for e in result['errors'][:10]:
        print(f"  {e.get('stock','?')} ({e.get('ticker','?')}): {e.get('reason','?')}")
