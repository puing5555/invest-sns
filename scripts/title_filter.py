# title_filter.py - 제목 필터링 로직
import re
from typing import List, Tuple
from pipeline_config import PipelineConfig

class TitleFilter:
    def __init__(self):
        self.skip_keywords = PipelineConfig.SKIP_KEYWORDS
        self.pass_keywords = PipelineConfig.PASS_KEYWORDS
    
    def should_skip(self, title: str) -> Tuple[bool, str]:
        """
        제목을 기반으로 영상을 건너뛸지 판단
        
        Returns:
            (should_skip: bool, reason: str)
        """
        title_lower = title.lower()
        
        # 멤버십/회원전용 체크 (최우선)
        for keyword in ["멤버십", "멤버쉽", "members only", "회원전용", "유료회원", "구독자전용", "vip전용"]:
            if keyword in title_lower:
                return True, f"멤버십/회원전용 콘텐츠: '{keyword}'"
        
        # Skip 키워드 체크
        for keyword in self.skip_keywords:
            if keyword.lower() in title_lower:
                return True, f"Skip 키워드 매치: '{keyword}'"
        
        # Pass 키워드 체크
        for keyword in self.pass_keywords:
            if keyword.lower() in title_lower:
                return False, f"Pass 키워드 매치: '{keyword}'"
        
        # 종목명 패턴 체크 (한국 주식)
        korean_stock_patterns = [
            r'삼성전자', r'SK하이닉스', r'LG에너지솔루션', r'현대차', r'기아',
            r'NAVER', r'카카오', r'셀트리온', r'삼성바이오로직스',
            r'삼성SDI', r'LG화학', r'포스코홀딩스', r'KB금융',
            r'신한지주', r'하나금융지주', r'우리금융지주',
            # 일반적인 종목명 패턴
            r'\w+전자', r'\w+케미칼', r'\w+제약', r'\w+바이오',
            r'\w+건설', r'\w+중공업', r'\w+화학'
        ]
        
        for pattern in korean_stock_patterns:
            if re.search(pattern, title):
                return False, f"한국 종목명 패턴 감지: '{pattern}'"
        
        # 미국 주식 심볼 패턴 체크
        us_stock_patterns = [
            r'\bAAPL\b', r'\bTSLA\b', r'\bNVDA\b', r'\bMSFT\b', r'\bGOOGL\b',
            r'\bAMZN\b', r'\bMETA\b', r'\bNFLX\b', r'\bTSMC\b', r'\bASML\b',
            # 일반적인 미국 주식 심볼 패턴 (대문자 3-4자리)
            r'\b[A-Z]{3,4}\b'
        ]
        
        for pattern in us_stock_patterns:
            if re.search(pattern, title):
                return False, f"미국 종목 심볼 패턴 감지: '{pattern}'"
        
        # 크립토 키워드 체크
        crypto_keywords = [
            r'비트코인', r'이더리움', r'BTC', r'ETH', r'코인', r'암호화폐',
            r'블록체인', r'디파이', r'NFT', r'웹3', r'메타버스'
        ]
        
        for pattern in crypto_keywords:
            if re.search(pattern, title, re.IGNORECASE):
                return False, f"크립토 키워드 감지: '{pattern}'"
        
        # 시장/경제 관련 키워드
        market_keywords = [
            r'금리', r'인플레이션', r'GDP', r'경제', r'증시',
            r'연준', r'Fed', r'ECB', r'한은', r'통화정책',
            r'실적', r'어닝', r'배당', r'분할', r'합병'
        ]
        
        for pattern in market_keywords:
            if re.search(pattern, title, re.IGNORECASE):
                return False, f"시장/경제 키워드 감지: '{pattern}'"
        
        # 기본적으로 skip (투자 관련성이 명확하지 않음)
        return True, "투자 관련 키워드 없음"
    
    def filter_videos(self, videos: List[dict]) -> Tuple[List[dict], List[dict]]:
        """
        영상 목록을 필터링
        
        Args:
            videos: [{'title': str, 'url': str, ...}, ...]
        
        Returns:
            (passed_videos, skipped_videos)
        """
        passed = []
        skipped = []
        
        for video in videos:
            should_skip, reason = self.should_skip(video['title'])
            
            if should_skip:
                video['skip_reason'] = reason
                skipped.append(video)
            else:
                video['pass_reason'] = reason
                passed.append(video)
        
        return passed, skipped
    
    def print_filter_results(self, passed: List[dict], skipped: List[dict]):
        """필터링 결과 출력"""
        total = len(passed) + len(skipped)
        
        print(f"\n=== 제목 필터링 결과 ===")
        print(f"총 영상: {total}개")
        print(f"통과: {len(passed)}개")
        print(f"건너뛰기: {len(skipped)}개")
        
        print(f"\n--- 통과한 영상 ({len(passed)}개) ---")
        for i, video in enumerate(passed[:10], 1):  # 최대 10개만 표시
            print(f"{i}. {video['title']}")
            print(f"   └ {video['pass_reason']}")
        
        if len(passed) > 10:
            print(f"   ... 외 {len(passed) - 10}개")
        
        print(f"\n--- 건너뛴 영상 ({len(skipped)}개) ---")
        # 건너뛴 이유별로 그룹핑
        skip_reasons = {}
        for video in skipped:
            reason = video['skip_reason']
            if reason not in skip_reasons:
                skip_reasons[reason] = []
            skip_reasons[reason].append(video['title'])
        
        for reason, titles in skip_reasons.items():
            print(f"{reason}: {len(titles)}개")
            for title in titles[:3]:  # 각 이유별로 3개만 예시
                print(f"  - {title}")
            if len(titles) > 3:
                print(f"  ... 외 {len(titles) - 3}개")