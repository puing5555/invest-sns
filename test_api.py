#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Anthropic API 테스트
"""

from anthropic import Anthropic

# API 클라이언트 초기화
client = Anthropic()

def test_api():
    try:
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=100,
            messages=[
                {
                    "role": "user",
                    "content": "안녕하세요! 간단히 인사해주세요."
                }
            ]
        )
        
        print("API 테스트 성공!")
        print("응답:", response.content[0].text)
        return True
        
    except Exception as e:
        print(f"API 테스트 실패: {e}")
        return False

if __name__ == "__main__":
    test_api()