#!/usr/bin/env python3
"""
최종 시그널 개수 확인
"""
import json
import urllib.request
import ssl

SUPABASE_URL = "https://arypzhotxflimroprmdk.supabase.co"
ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIwMDYxMTAsImV4cCI6MjA4NzU4MjExMH0.qcqFIvYRiixwu609Wjj9H3HxscU8vNpo9nS_KQ3f00A"

def check_counts():
    ssl_ctx = ssl.create_default_context()
    
    # 총 시그널 수 확인
    url = f"{SUPABASE_URL}/rest/v1/influencer_signals?select=id"
    req = urllib.request.Request(url, headers={
        "apikey": ANON_KEY,
        "Authorization": f"Bearer {ANON_KEY}",
        "Content-Type": "application/json",
    })
    
    try:
        resp = urllib.request.urlopen(req, context=ssl_ctx)
        signals = json.loads(resp.read().decode())
        total_signals = len(signals)
        
        print(f"현재 총 시그널 수: {total_signals}개")
        print(f"목표 100개까지: {100 - total_signals}개 남음")
        print(f"달성률: {total_signals/100*100:.1f}%")
        
        return total_signals
        
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    check_counts()