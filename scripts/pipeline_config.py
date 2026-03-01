# pipeline_config.py - 파이프라인 설정 파일
import os
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env.local'))

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
    RATE_LIMIT_BATCH_BREAK = 5 * 60  # 20개 후 5분 휴식
    RATE_LIMIT_BATCH_SIZE = 20
    RATE_LIMIT_API_REQUESTS = 5  # API 요청 간 5초
    
    # 프롬프트 설정
    PROMPT_VERSION = "V10"
    PROMPT_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'prompts', 'pipeline_v10.md')
    
    # 시그널 타입 (한글 5단계)
    SIGNAL_TYPES = ["매수", "긍정", "중립", "경계", "매도"]
    
    # 필터링 키워드
    SKIP_KEYWORDS = [
        # 구독자 Q&A
        "Q&A", "질문", "답변", "구독자", "시청자", "댓글",
        
        # 일상/브이로그
        "일상", "브이로그", "VLOG", "출장", "여행", "먹방",
        
        # 채널 공지
        "공지", "안내", "알림", "소식", "업데이트", 
        
        # 교육/자기계발
        "교육", "강의", "공부", "독서", "자기계발", "인생",
        
        # 영어 콘텐츠
        "English", "english", "영어",
        
        # 인트로/쇼츠
        "인트로", "Shorts", "쇼츠", "예고", "티저",
        
        # 멤버십/회원전용
        "멤버십", "멤버쉽", "Members only", "회원전용", "유료회원", "구독자전용", "VIP전용"
    ]
    
    # 통과 키워드 (특정 종목 언급, 시장 전망 등)
    PASS_KEYWORDS = [
        # 시장/섹터 전망
        "전망", "시황", "시장", "증시", "코스피", "나스닥", "섹터", "bubble", "panic", "crash",
        
        # 매매 의견
        "매수", "매도", "추천", "관망", "정리", "담기", "buy", "sell", "investment", "investing",
        
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

    @classmethod
    def load_prompt(cls):
        """V10 프롬프트 로드"""
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