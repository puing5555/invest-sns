#!/usr/bin/env python3
"""
signal_validator.py - 시그널 품질 검증 모듈
DB INSERT 전 자동 검증. reject된 건 별도 로그 저장.

사용법:
    from signal_validator import SignalValidator
    validator = SignalValidator()
    result = validator.validate(signal_dict)
    if result.passed:
        # DB INSERT
    else:
        # result.reasons에 reject 사유 목록
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

# 유효한 값 정의
VALID_SIGNALS = {'매수', '긍정', '중립', '경계', '매도'}
VALID_MENTION_TYPES = {'결론', '티저', '교육', '컨센서스', '보유', '논거', '뉴스', '리포트'}
VALID_CONFIDENCE = {'very_high', 'high', 'medium', 'low'}
VALID_MARKETS = {'KR', 'US', 'US_ADR', 'CRYPTO', 'CRYPTO_DEFI', 'ETF', 'SECTOR', 'INDEX', 'OTHER'}

# 종목이 아닌 것들 (사람/회사/개념)
KNOWN_NON_STOCKS = {
    # 사람
    '라울 팔', '워런 버핏', '일론 머스크', '피터 린치', '레이 달리오',
    '캐시 우드', '짐 크레이머', '마이클 세일러', '찰리 멍거',
    # 회사/기관 (투자대상이 아닌 것)
    '피델리티', '블랙록', '뱅가드', 'JP모건', '골드만삭스',
    # 개념/일반
    'N/A', 'n/a', '', '없음', '해당없음', '스테이블코인',
}

# 알려진 유효 종목 패턴
KNOWN_STOCK_PATTERNS = [
    r'^[A-Z]{1,5}$',           # US ticker (AAPL, TSLA)
    r'^\d{6}$',                # KR code (005930)
    r'^[가-힣]{2,10}$',        # Korean name (삼성전자)
    r'^[가-힣]+\s?\(.+\)$',    # Korean with ticker (비트코인 (BTC))
    r'^[A-Za-z\s\.\-]{2,30}$', # English name (Rocket Lab)
]


class ValidationResult:
    def __init__(self):
        self.passed = True
        self.reasons: List[str] = []
        self.warnings: List[str] = []
    
    def reject(self, reason: str):
        self.passed = False
        self.reasons.append(reason)
    
    def warn(self, reason: str):
        self.warnings.append(reason)


class SignalValidator:
    def __init__(self, log_dir: str = None):
        self.log_dir = Path(log_dir) if log_dir else Path(__file__).parent.parent / 'logs'
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.reject_log = self.log_dir / f'rejected_signals_{datetime.now().strftime("%Y%m%d")}.jsonl'
        self.seen_combos: Set[Tuple] = set()
        self._stats = {'total': 0, 'passed': 0, 'rejected': 0}
    
    def validate(self, signal: Dict) -> ValidationResult:
        """시그널 검증. ValidationResult 반환."""
        self._stats['total'] += 1
        result = ValidationResult()
        
        # 1. key_quote 길이 체크 (20~100자)
        kq = signal.get('key_quote', '') or ''
        if len(kq) < 20:
            result.reject(f'key_quote 너무 짧음 ({len(kq)}자, 최소 20자)')
        elif len(kq) > 200:
            result.warn(f'key_quote 길음 ({len(kq)}자, 권장 100자 이하)')
        
        # 2. reasoning 길이 체크 (200자 이상)
        reasoning = signal.get('reasoning', '') or ''
        if len(reasoning) < 200:
            result.reject(f'reasoning 너무 짧음 ({len(reasoning)}자, 최소 200자)')
        
        # 3. 종목명 검증
        stock = signal.get('stock', '') or ''
        if not stock or stock.strip() == '':
            result.reject('종목명 비어있음')
        elif stock in KNOWN_NON_STOCKS:
            result.reject(f'종목이 아님: "{stock}" (사람/회사/개념)')
        elif len(stock) > 50:
            result.reject(f'종목명 너무 김: "{stock[:30]}..." ({len(stock)}자)')
        
        # 4. signal_type 유효성
        sig = signal.get('signal', '')
        if sig not in VALID_SIGNALS:
            result.reject(f'잘못된 시그널: "{sig}" (허용: {VALID_SIGNALS})')
        
        # 5. mention_type 유효성
        mt = signal.get('mention_type', '')
        if mt and mt not in VALID_MENTION_TYPES:
            result.reject(f'잘못된 mention_type: "{mt}" (허용: {VALID_MENTION_TYPES})')
        
        # 6. confidence 유효성
        conf = signal.get('confidence', '')
        if conf and conf not in VALID_CONFIDENCE:
            result.warn(f'잘못된 confidence: "{conf}" (허용: {VALID_CONFIDENCE})')
        
        # 7. market 유효성
        market = signal.get('market', '')
        if market and market not in VALID_MARKETS:
            result.warn(f'잘못된 market: "{market}" (허용: {VALID_MARKETS})')
        
        # 8. 중복 체크 (video_id + speaker_id + stock + signal)
        combo = (
            signal.get('video_id', ''),
            signal.get('speaker_id', ''),
            stock,
            sig,
        )
        if combo in self.seen_combos:
            result.reject(f'중복: {stock} ({sig}) - 같은 영상+화자+종목+시그널')
        else:
            self.seen_combos.add(combo)
        
        # 9. timestamp 체크
        ts = signal.get('timestamp', '')
        if ts and ts not in ('N/A', 'null', None, ''):
            # 간단한 형식 체크 (M:SS 또는 H:MM:SS)
            if not re.match(r'^\d{1,2}:\d{2}(:\d{2})?$', str(ts)):
                result.warn(f'타임스탬프 형식 이상: "{ts}"')
        
        # 로그
        if result.passed:
            self._stats['passed'] += 1
        else:
            self._stats['rejected'] += 1
            self._log_reject(signal, result)
        
        return result
    
    def _log_reject(self, signal: Dict, result: ValidationResult):
        """reject 로그 저장"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'stock': signal.get('stock', ''),
            'signal': signal.get('signal', ''),
            'video_id': signal.get('video_id', ''),
            'reasons': result.reasons,
            'warnings': result.warnings,
        }
        with open(self.reject_log, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')
    
    def get_stats(self) -> Dict:
        return self._stats.copy()
    
    def print_stats(self):
        s = self._stats
        print(f"\n=== 검증 결과 ===")
        print(f"총: {s['total']}, 통과: {s['passed']}, reject: {s['rejected']}")
        if s['rejected'] > 0:
            print(f"reject 로그: {self.reject_log}")
    
    @staticmethod
    def fix_mention_type(mt: str) -> str:
        """잘못된 mention_type을 가장 가까운 유효 값으로 매핑"""
        MT_MAP = {
            '분석': '논거', '투자': '논거', '추천': '논거', '팁': '논거',
            '언급': '논거', '전망': '논거', '핵심발언': '논거', '시장전망': '논거',
            '긍정': '논거', '매수': '논거', '중립': '논거', '경계': '논거', '매도': '논거',
        }
        if mt in VALID_MENTION_TYPES:
            return mt
        return MT_MAP.get(mt, '논거')
    
    @staticmethod
    def fix_confidence(conf: str) -> str:
        """잘못된 confidence 수정"""
        CONF_MAP = {
            'very high': 'very_high', 'veryhigh': 'very_high',
            '높음': 'high', '중간': 'medium', '낮음': 'low',
        }
        if conf in VALID_CONFIDENCE:
            return conf
        return CONF_MAP.get(conf.lower() if conf else '', 'medium')
    
    @staticmethod  
    def fix_market(market: str) -> str:
        """잘못된 market 수정"""
        if market in VALID_MARKETS:
            return market
        m = (market or '').upper()
        if 'CRYPTO' in m:
            return 'CRYPTO'
        if m in ('', 'N/A', 'NULL', 'NONE'):
            return 'OTHER'
        return 'OTHER'


# CLI 테스트
if __name__ == '__main__':
    v = SignalValidator()
    
    # 테스트 케이스
    tests = [
        {'stock': '삼성전자', 'signal': '매수', 'key_quote': '삼성전자가 앞으로 좋아질 것이다', 'reasoning': '발언자가 긍정적', 'mention_type': '논거', 'confidence': 'high'},
        {'stock': '비트코인', 'signal': '매수', 'key_quote': '비트코인은 디지털 금이다. 장기적으로 반드시 올라간다.', 'reasoning': '발언자는 비트코인의 희소성과 기관 투자 증가를 근거로 장기 상승을 전망했다. 특히 ETF 승인 이후 기관 자금 유입이 가속화되고 있으며, 반감기 사이클에 따라 2025년이 상승장의 정점이 될 수 있다고 분석했다.', 'mention_type': '결론', 'confidence': 'high'},
        {'stock': '라울 팔', 'signal': '매수', 'key_quote': '라울 팔이 좋다고 했다', 'reasoning': '짧음', 'mention_type': '분석'},
        {'stock': '', 'signal': '무효', 'key_quote': '', 'reasoning': ''},
    ]
    
    for t in tests:
        r = v.validate(t)
        status = 'PASS' if r.passed else 'REJECT'
        print(f"[{status}] {t.get('stock','?')}: {r.reasons or r.warnings or 'OK'}")
    
    v.print_stats()
