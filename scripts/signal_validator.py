#!/usr/bin/env python3
"""
signal_validator.py - 시그널 품질 검증 모듈 (14개 항목)
DB INSERT 전 자동 검증. reject된 건 별도 로그 저장.

검증 항목 (14개):
1.  key_quote 길이 (20~200자)
2.  reasoning 길이 (200자 이상)
3.  종목명 검증 (사람/회사/개념 필터링)
4.  signal_type 유효성
5.  mention_type 유효성
6.  confidence 유효성
7.  중복 체크 (영상+화자+종목+시그널)
8.  타임스탬프 검증 (0:00 reject, 영상 길이 초과 reject)
9.  날짜 검증 (미래/5년 이상 과거 reject)
10. 종목코드 매핑 검증 (ticker 존재 여부)
11. 화자 검증 (채널 출연자 확인)
12. 언어 검증 (key_quote가 자막에 실제 존재하는지 — AI 날조 방지)
13. 수익률 범위 검증 (±500% 이상 reject)
14. 과잉 추출 경고 (한 영상 시그널 10개 이상)

사용법:
    from signal_validator import SignalValidator
    validator = SignalValidator()
    result = validator.validate(signal_dict, subtitle_text="...", video_duration=600)
    if result.passed:
        # DB INSERT
    else:
        # result.reasons에 reject 사유 목록
"""

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from difflib import SequenceMatcher

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
    '로버트 기요사키', '마크 큐반', '팀 드레이퍼', '비탈릭 부테린',
    # 회사/기관 (투자대상이 아닌 것)
    '피델리티', '블랙록', '뱅가드', 'JP모건', '골드만삭스',
    '모건스탠리', '시타델', '그레이스케일', 'SEC', '한국은행',
    '연준', '연방준비제도', 'IMF', '세계은행',
    # 개념/일반
    'N/A', 'n/a', '', '없음', '해당없음', '스테이블코인',
    '달러', '원화', '엔화', '유로', '금리', '인플레이션',
}

# 알려진 유효 ticker (캐시, 필요시 Yahoo Finance/KRX에서 확인)
_TICKER_CACHE: Dict[str, bool] = {}


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
    def __init__(self, log_dir: str = None, channel_speakers: Dict[str, List[str]] = None,
                 verify_ticker: bool = False):
        """
        Args:
            log_dir: reject 로그 저장 디렉토리
            channel_speakers: 채널별 출연자 매핑 {'channel_id': ['스피커1', '스피커2']}
            verify_ticker: True면 Yahoo Finance/KRX에서 ticker 존재 확인 (느림)
        """
        self.log_dir = Path(log_dir) if log_dir else Path(__file__).parent.parent / 'logs'
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.reject_log = self.log_dir / f'rejected_signals_{datetime.now().strftime("%Y%m%d")}.jsonl'
        self.seen_combos: Set[Tuple] = set()
        self.video_signal_counts: Dict[str, int] = {}  # video_id -> count
        self.channel_speakers = channel_speakers or {}
        self.verify_ticker = verify_ticker
        self._stats = {'total': 0, 'passed': 0, 'rejected': 0, 'warnings': 0}
    
    def validate(self, signal: Dict, subtitle_text: str = None,
                 video_duration: int = None, published_at: str = None) -> ValidationResult:
        """
        시그널 검증 (14개 항목).
        
        Args:
            signal: 시그널 딕셔너리
            subtitle_text: 자막 원문 (언어 검증용)
            video_duration: 영상 길이 초 (타임스탬프 검증용)
            published_at: 영상 게시일 ISO format (날짜 검증용)
        """
        self._stats['total'] += 1
        result = ValidationResult()
        
        stock = signal.get('stock', '') or ''
        sig = signal.get('signal', '')
        kq = signal.get('key_quote', '') or ''
        reasoning = signal.get('reasoning', '') or ''
        video_id = signal.get('video_id', '')
        
        # === 1. key_quote 길이 (20~200자) ===
        if len(kq) < 20:
            result.reject(f'[1] key_quote 너무 짧음 ({len(kq)}자, 최소 20자)')
        elif len(kq) > 200:
            result.warn(f'[1] key_quote 길음 ({len(kq)}자, 권장 200자 이하)')
        
        # === 2. reasoning 길이 (200자 이상) ===
        if len(reasoning) < 200:
            result.reject(f'[2] reasoning 너무 짧음 ({len(reasoning)}자, 최소 200자)')
        
        # === 3. 종목명 검증 ===
        if not stock or stock.strip() == '':
            result.reject('[3] 종목명 비어있음')
        elif stock in KNOWN_NON_STOCKS:
            result.reject(f'[3] 종목이 아님: "{stock}" (사람/회사/개념)')
        elif len(stock) > 50:
            result.reject(f'[3] 종목명 너무 김: "{stock[:30]}..." ({len(stock)}자)')
        
        # === 4. signal_type 유효성 ===
        if sig not in VALID_SIGNALS:
            result.reject(f'[4] 잘못된 시그널: "{sig}" (허용: {VALID_SIGNALS})')
        
        # === 5. mention_type 유효성 ===
        mt = signal.get('mention_type', '')
        if mt and mt not in VALID_MENTION_TYPES:
            result.reject(f'[5] 잘못된 mention_type: "{mt}" (허용: {VALID_MENTION_TYPES})')
        
        # === 6. confidence 유효성 ===
        conf = signal.get('confidence', '')
        if conf and conf not in VALID_CONFIDENCE:
            result.warn(f'[6] 잘못된 confidence: "{conf}"')
        
        # === 7. 중복 체크 ===
        combo = (video_id, signal.get('speaker_id', ''), stock, sig)
        if combo[0] and combo in self.seen_combos:
            result.reject(f'[7] 중복: {stock} ({sig}) - 같은 영상+화자+종목+시그널')
        else:
            if combo[0]:
                self.seen_combos.add(combo)
        
        # === 8. 타임스탬프 검증 ===
        ts = signal.get('timestamp', '')
        if ts and ts not in ('N/A', 'null', None, ''):
            ts_str = str(ts)
            # 0:00 체크
            if ts_str in ('0:00', '00:00', '0:00:00', '00:00:00'):
                result.reject(f'[8] 타임스탬프 0:00 (영상 시작 = 유효하지 않음)')
            else:
                # 초로 변환
                ts_seconds = self._parse_timestamp(ts_str)
                if ts_seconds is not None:
                    if video_duration and ts_seconds > video_duration:
                        result.reject(f'[8] 타임스탬프 초과: {ts_str} ({ts_seconds}초 > 영상 {video_duration}초)')
                elif not re.match(r'^\d{1,2}:\d{2}(:\d{2})?$', ts_str):
                    result.warn(f'[8] 타임스탬프 형식 이상: "{ts_str}"')
        
        # === 9. 날짜 검증 ===
        if published_at:
            try:
                pub_date = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                now = datetime.now(timezone.utc)
                if pub_date > now:
                    result.reject(f'[9] 미래 날짜: {published_at}')
                elif (now - pub_date).days > 365 * 5:
                    result.reject(f'[9] 5년 이상 오래된 날짜: {published_at}')
            except (ValueError, TypeError):
                result.warn(f'[9] 날짜 파싱 실패: {published_at}')
        
        # === 10. 종목코드 매핑 검증 ===
        ticker = signal.get('ticker', '')
        if ticker and self.verify_ticker:
            if not self._verify_ticker_exists(ticker, signal.get('market', '')):
                result.warn(f'[10] ticker 미확인: "{ticker}" (시장에 존재하지 않을 수 있음)')
        
        # === 11. 화자 검증 ===
        channel_id = signal.get('channel_id', '')
        speaker_name = signal.get('speaker_name', '')
        if channel_id and speaker_name and self.channel_speakers:
            allowed = self.channel_speakers.get(channel_id, [])
            if allowed and speaker_name not in allowed:
                result.warn(f'[11] 화자 "{speaker_name}"이 채널 {channel_id}의 출연자 목록에 없음')
        
        # === 12. 언어 검증 (AI 날조 방지) ===
        if subtitle_text and kq and len(kq) >= 20:
            similarity = self._check_quote_in_subtitle(kq, subtitle_text)
            if similarity < 0.4:
                result.warn(f'[12] key_quote가 자막에서 발견되지 않음 (유사도 {similarity:.0%}) — AI 날조 가능성')
            elif similarity < 0.6:
                result.warn(f'[12] key_quote 자막 유사도 낮음 ({similarity:.0%})')
        
        # === 13. 수익률 범위 검증 ===
        return_pct = signal.get('return_pct')
        if return_pct is not None:
            try:
                ret = float(return_pct)
                if abs(ret) > 500:
                    result.reject(f'[13] 비현실적 수익률: {ret}% (±500% 초과)')
                elif abs(ret) > 200:
                    result.warn(f'[13] 높은 수익률: {ret}% (확인 필요)')
            except (ValueError, TypeError):
                pass
        
        target_price = signal.get('target_price')
        if target_price is not None:
            try:
                tp = float(target_price)
                if tp <= 0:
                    result.reject(f'[13] 비현실적 목표가: {tp}')
                elif tp > 10_000_000:
                    result.warn(f'[13] 극단적 목표가: {tp} (확인 필요)')
            except (ValueError, TypeError):
                pass
        
        # === 14. 과잉 추출 경고 ===
        if video_id:
            self.video_signal_counts[video_id] = self.video_signal_counts.get(video_id, 0) + 1
            count = self.video_signal_counts[video_id]
            if count > 10:
                result.warn(f'[14] 과잉 추출: 영상 {video_id[:12]}...에서 {count}개 시그널')
            elif count == 10:
                result.warn(f'[14] 과잉 추출 경고: 영상에서 10개 시그널 도달')
        
        # === 결과 처리 ===
        if result.passed:
            self._stats['passed'] += 1
        else:
            self._stats['rejected'] += 1
            self._log_reject(signal, result)
        
        if result.warnings:
            self._stats['warnings'] += 1
        
        return result
    
    def _parse_timestamp(self, ts: str) -> Optional[int]:
        """타임스탬프 문자열을 초로 변환"""
        try:
            parts = ts.split(':')
            parts = [int(p) for p in parts]
            if len(parts) == 3:
                return parts[0] * 3600 + parts[1] * 60 + parts[2]
            elif len(parts) == 2:
                return parts[0] * 60 + parts[1]
            elif len(parts) == 1:
                return parts[0]
        except (ValueError, IndexError):
            pass
        return None
    
    def _check_quote_in_subtitle(self, quote: str, subtitle: str) -> float:
        """key_quote가 자막에 존재하는지 유사도 체크 (0~1)"""
        # 공백/구두점 정규화
        def normalize(s):
            return re.sub(r'\s+', ' ', re.sub(r'[^\w\s가-힣]', '', s)).strip().lower()
        
        norm_quote = normalize(quote)
        norm_sub = normalize(subtitle)
        
        if not norm_quote or not norm_sub:
            return 0.0
        
        # 정확한 부분 문자열 매칭
        if norm_quote in norm_sub:
            return 1.0
        
        # 슬라이딩 윈도우 유사도
        quote_len = len(norm_quote)
        best = 0.0
        # 성능을 위해 stride 사용
        stride = max(1, quote_len // 4)
        for i in range(0, max(1, len(norm_sub) - quote_len + 1), stride):
            window = norm_sub[i:i + quote_len + 20]
            ratio = SequenceMatcher(None, norm_quote, window).ratio()
            if ratio > best:
                best = ratio
                if best > 0.8:
                    break
        
        return best
    
    def _verify_ticker_exists(self, ticker: str, market: str = '') -> bool:
        """ticker가 실제 존재하는지 확인 (캐시 사용)"""
        cache_key = f"{ticker}:{market}"
        if cache_key in _TICKER_CACHE:
            return _TICKER_CACHE[cache_key]
        
        exists = True  # 기본값: 존재한다고 가정
        try:
            import requests
            if market in ('KR', '') and re.match(r'^\d{6}$', ticker):
                # KRX 종목코드 확인
                r = requests.get(
                    f'https://finance.naver.com/item/main.naver?code={ticker}',
                    timeout=5, headers={'User-Agent': 'Mozilla/5.0'}
                )
                exists = r.status_code == 200 and '종목' in r.text
            elif market in ('US', 'US_ADR', '') and re.match(r'^[A-Z]{1,5}$', ticker):
                # Yahoo Finance 확인
                r = requests.get(
                    f'https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?range=1d',
                    timeout=5, headers={'User-Agent': 'Mozilla/5.0'}
                )
                data = r.json()
                exists = 'chart' in data and data['chart'].get('result')
            # CRYPTO는 ticker 형식이 다양하므로 기본 통과
        except Exception:
            exists = True  # 네트워크 에러시 통과
        
        _TICKER_CACHE[cache_key] = exists
        return exists
    
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
        print(f"\n=== 검증 결과 (14개 항목) ===")
        print(f"총: {s['total']}, 통과: {s['passed']}, reject: {s['rejected']}, 경고: {s['warnings']}")
        if s['rejected'] > 0:
            print(f"reject 로그: {self.reject_log}")
        
        # 과잉 추출 영상 보고
        over = {vid: cnt for vid, cnt in self.video_signal_counts.items() if cnt >= 10}
        if over:
            print(f"과잉 추출 영상: {len(over)}개")
            for vid, cnt in sorted(over.items(), key=lambda x: -x[1])[:5]:
                print(f"  {vid[:12]}...: {cnt}개")
    
    @staticmethod
    def fix_mention_type(mt: str) -> str:
        """잘못된 mention_type → 유효 값 매핑"""
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
        CONF_MAP = {'very high': 'very_high', 'veryhigh': 'very_high',
                    '높음': 'high', '중간': 'medium', '낮음': 'low'}
        if conf in VALID_CONFIDENCE:
            return conf
        return CONF_MAP.get(conf.lower() if conf else '', 'medium')
    
    @staticmethod
    def fix_market(market: str) -> str:
        if market in VALID_MARKETS:
            return market
        m = (market or '').upper()
        if 'CRYPTO' in m:
            return 'CRYPTO'
        if m in ('', 'N/A', 'NULL', 'NONE'):
            return 'OTHER'
        return 'OTHER'


if __name__ == '__main__':
    v = SignalValidator()
    
    # 테스트: 14개 항목 전부
    fake_subtitle = "비트코인은 디지털 금이다. 장기적으로 반드시 올라간다. ETF 승인 이후 기관 자금이 몰리고 있다."
    
    tests = [
        # PASS: 모든 조건 충족
        {
            'stock': '비트코인', 'signal': '매수', 'video_id': 'test1',
            'key_quote': '비트코인은 디지털 금이다. 장기적으로 반드시 올라간다.',
            'reasoning': '발언자는 비트코인의 희소성과 기관 투자 증가를 근거로 장기 상승을 전망했다. ' * 5,
            'mention_type': '결론', 'confidence': 'high', 'timestamp': '5:30',
        },
        # REJECT: 짧은 reasoning + 종목 아님
        {
            'stock': '라울 팔', 'signal': '매수', 'video_id': 'test2',
            'key_quote': '라울 팔이 비트코인 좋다고 했다',
            'reasoning': '짧음',
            'mention_type': '분석', 'timestamp': '0:00',
        },
        # REJECT: 미래 날짜 + 비현실적 수익률
        {
            'stock': '테슬라', 'signal': '매수', 'video_id': 'test3',
            'key_quote': '테슬라는 반드시 10배 간다고 확신합니다.',
            'reasoning': '발언자가 테슬라의 자율주행 기술 발전과 에너지 사업 확대를 근거로 강력한 매수 의견을 제시했다. ' * 4,
            'mention_type': '결론', 'confidence': 'high',
            'return_pct': 700,
        },
    ]
    
    for t in tests:
        pub = '2030-01-01T00:00:00+00:00' if t.get('stock') == '테슬라' else '2024-06-15T00:00:00+00:00'
        r = v.validate(t, subtitle_text=fake_subtitle, video_duration=600, published_at=pub)
        status = 'PASS' if r.passed else 'REJECT'
        issues = r.reasons + [f'⚠ {w}' for w in r.warnings]
        print(f"[{status}] {t.get('stock','?')}: {issues or 'OK'}")
    
    v.print_stats()
