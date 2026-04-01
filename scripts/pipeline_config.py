# -*- coding: utf-8 -*-
# pipeline_config.py - 파이프라인 설정 파일
import os
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env.local'), override=True)

class PipelineConfig:
    # Supabase 설정
    SUPABASE_URL = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
    SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    # Anthropic API 설정
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
    ANTHROPIC_MODEL = "claude-sonnet-4-20250514"
    
    # Webshare 프록시 설정
    WEBSHARE_PROXY_URL = os.getenv('WEBSHARE_PROXY_URL', '')
    
    # 레이트리밋 설정 (초)
    RATE_LIMIT_REQUESTS = 3  # 요청 간 3초
    RATE_LIMIT_429_WAIT = 60  # 429 에러 시 60초 대기
    RATE_LIMIT_BATCH_BREAK = 5 * 60  # 20개마다 5분 휴식
    RATE_LIMIT_BATCH_SIZE = 30
    RATE_LIMIT_API_REQUESTS = 5  # API 요청 간 5초
    
    # 프롬프트 설정
    PROMPT_VERSION = "V15.2"
    PROMPT_PATH = os.path.join(os.path.dirname(__file__), '..', 'prompts', 'pipeline_v15.2.md')
    
    # 시그널 타입 (한글 5단계)
    SIGNAL_TYPES = ["매수", "긍정", "중립", "경계", "매도"]
    
    # 필터 제외 키워드
    SKIP_KEYWORDS = [
        # 구독/Q&A
        "Q&A", "질문", "방청객", "구독자", "시청자", "팬덤",
        
        # 일상/브이로그
        "일상", "브이로그", "VLOG", "출장", "여행", "먹방",
        
        # 채널 공지
        "공지", "안내", "알림", "공식", "업데이트",
        
        # 교육/자기계발
        "교육", "강의", "공부", "독서", "자기계발", "학생",
        
        # 영어 콘텐츠
        "English", "english", "영어",
        
        # 쇼츠/광고
        "쇼츠", "Shorts", "shorts", "광고", "스팟",
        
        # 멤버십/회원전용
        "멤버십", "멤버쉽", "Members only", "회원전용", "유료회원", "구독자전용", "VIP전용"
    ]
    
    # 통과 키워드 (투자 관련 종목 언급, 시장 전망 등)
    PASS_KEYWORDS = [
        # 시장/시황 전망
        "전망", "동향", "시장", "증시", "코스피", "나스닥", "시황", "bubble", "panic", "crash",
        
        # 매매 의견
        "매수", "매도", "추천", "관심", "정리", "종목", "buy", "sell", "investment", "investing",
        
        # 경제지표
        "금리", "인플레이션", "GDP", "실적", "어닝", "trump", "fed", "economy", "economic",
        
        # 종목 관련
        "종목", "기업", "회사", "주식", "투자", "stock", "stocks", "equity", "portfolio",
        
        # 암호화폐
        "bitcoin", "ethereum", "btc", "eth", "crypto", "blockchain", "coin", "비트코인", "이더리움", "코인", "암호화폐",
        
        # 주요 종목
        "palantir", "pltr", "tesla", "tsla", "nvidia", "nvda", "apple", "aapl", "amazon", "amzn",
        "microsoft", "msft", "google", "googl", "meta", "팔란티어", "테슬라", "엔비디아", "애플",
        
        # 투자 관련
        "asset", "wealth", "portfolio", "diversification", "analysis", "valuation", "risk",
        "return", "yield", "dividend", "earnings", "profit", "loss", "finance", "financial"
    ]

    # 채널 → 운영자 매핑 (speaker 구분용)
    CHANNEL_OWNERS = {
        '이효석아카데미': '이효석',
        '안경투 (안유화의 경제투자론)': '안유화',
        '부읽남TV': '부읽남',
        '삼프로TV': None,  # 패널 채널, 단일 운영자 없음
        'Godofit': '이형수 (IT의신)',
        '코린이 아빠': '코린이 아빠',
        '위즈덤투스': '위즈덤투스',
        '표상록의 코인 포트폴리오': '표상록',
        '슈카월드': '슈카',
        '양정길': '양정길',
        '듀딜 | Due Diligence - Videos': '듀딜',
        '달란트투자': '달란트투자',
        '세상학개론': '세상학개론',
        '월가아재': '월가아재',
        '올랜도 킴 미국주식': '올랜도 킴',
        '대니월드(Danny World)': '대니월드',
        '윤수목의 생존투자훈련소': '윤수목',
        '경제 읽어주는 남자(김광석TV)': '김광석',
        '강환국': '강환국',
        '할 수 있다! 알고 투자': '강환국',
    }

    @classmethod
    def get_channel_owner(cls, channel_name):
        """채널명으로 운영자 이름 반환"""
        return cls.CHANNEL_OWNERS.get(channel_name)

    @classmethod
    def load_prompt(cls):
        """V15.2 프롬프트 로드"""
        try:
            with open(cls.PROMPT_PATH, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            print(f"프롬프트 파일을 찾을 수 없습니다: {cls.PROMPT_PATH}")
            return ""
    
    @classmethod
    def get_proxy_config(cls):
        """프록시 설정 반환"""
        if cls.WEBSHARE_PROXY_URL:
            return {
                'http': cls.WEBSHARE_PROXY_URL,
                'https': cls.WEBSHARE_PROXY_URL
            }
        return None
