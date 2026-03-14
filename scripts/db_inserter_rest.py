# db_inserter_rest.py - Supabase REST API 직접 호출 모듈
import json
import uuid
import requests
from datetime import datetime
from typing import List, Dict, Any, Optional
from pipeline_config import PipelineConfig


def _safe_int(val):
    """값을 int로 변환. 변환 불가(None/문자열 등)이면 None 반환."""
    if val is None:
        return None
    try:
        return int(val)
    except (TypeError, ValueError):
        return None

class DatabaseInserter:
    def __init__(self):
        self.config = PipelineConfig()
        self.base_url = self.config.SUPABASE_URL + "/rest/v1"
        self.headers = {
            'apikey': self.config.SUPABASE_SERVICE_KEY,
            'Authorization': f'Bearer {self.config.SUPABASE_SERVICE_KEY}',
            'Content-Type': 'application/json'
        }
    
    def get_or_create_channel(self, channel_info: Dict[str, Any]) -> str:
        """
        채널 정보 확인/생성
        
        Args:
            channel_info: {
                'url': str,           # channel_url에 매핑
                'name': str,          # channel_name에 매핑 (channel_title 우선)
                'channel_title': str, # channel_name 우선 사용
                'subscriber_count': int,
                'description': str
            }
        
        Returns:
            channel_id (UUID)
        """
        try:
            # channel_url: 'url' 키 사용 (channel_info['url'] = channel_url)
            channel_url = channel_info.get('url', '')

            # 기존 채널 확인 — channel_url 컬럼으로 조회
            response = requests.get(
                f"{self.base_url}/influencer_channels",
                headers=self.headers,
                params={'channel_url': f'eq.{channel_url}', 'select': 'id'}
            )
            response.raise_for_status()
            
            data = response.json()
            if data:
                channel_id = data[0]['id']
                print(f"[OK] 기존 채널 발견: {channel_id}")
                return channel_id
            
            # channel_name: channel_title > name 우선순위
            channel_name = (
                channel_info.get('channel_title') or
                channel_info.get('name') or
                'Unknown'
            )

            # channel_handle: URL에서 @handle 추출
            import re as _re
            handle_match = _re.search(r'@([^/?#]+)', channel_url)
            channel_handle = handle_match.group(1) if handle_match else ''

            # 새 채널 생성 — 실제 테이블 컬럼명 사용
            channel_data = {
                'id': str(uuid.uuid4()),
                'channel_name': channel_name,
                'channel_handle': channel_handle,
                'channel_url': channel_url,
                'platform': 'youtube',
                'description': channel_info.get('description', ''),
                'subscriber_count': channel_info.get('subscriber_count', 0),
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            insert_headers = dict(self.headers)
            insert_headers['Content-Type'] = 'application/json; charset=utf-8'
            
            response = requests.post(
                f"{self.base_url}/influencer_channels",
                headers=insert_headers,
                data=json.dumps(channel_data, ensure_ascii=False).encode('utf-8')
            )
            response.raise_for_status()
            
            print(f"[OK] 새 채널 생성: {channel_data['id']} ({channel_name})")
            return channel_data['id']
            
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] 채널 생성/확인 실패: {e}")
            raise

    def get_or_create_video(self, video_info: Dict[str, Any], channel_id: str) -> str:
        """
        영상 정보 확인/생성
        
        Args:
            video_info: {
                'video_id': str,
                'title': str,
                'upload_date': str,
                'duration': int,
                'view_count': int,
                'description': str
            }
            channel_id: UUID string
        
        Returns:
            video_uuid (UUID)
        """
        try:
            vid_id = video_info.get("video_id", "")
            # 기존 영상 확인
            response = requests.get(
                f"{self.base_url}/influencer_videos",
                headers=self.headers,
                params={'video_id': f'eq.{vid_id}', 'select': 'id'}
            )
            if not response.ok:
                print(f"[ERROR] 영상 GET 실패 {response.status_code} (vid={vid_id}): {response.text[:300]}")
            response.raise_for_status()

            data = response.json()
            if data:
                video_uuid = data[0]['id']
                print(f"[OK] 기존 영상 발견: {video_uuid}")
                return video_uuid
            
            # 새 영상 생성 (실제 DB 스키마: published_at, duration_seconds)
            # upload_date (YYYYMMDD) → published_at (YYYY-MM-DD)
            raw_date = video_info.get('upload_date', '') or video_info.get('published_at', '')
            if raw_date and len(str(raw_date)) == 8 and str(raw_date).isdigit():
                published_at = f"{raw_date[:4]}-{raw_date[4:6]}-{raw_date[6:]}T00:00:00+00:00"
            elif raw_date:
                published_at = str(raw_date)
            else:
                published_at = None

            video_data = {
                'id': str(uuid.uuid4()),
                'video_id': video_info['video_id'],
                'channel_id': channel_id,
                'title': video_info['title'],
                'published_at': published_at,
                'duration_seconds': _safe_int(video_info.get('duration_seconds') or video_info.get('duration')),
                'created_at': datetime.now().isoformat(),
            }
            
            response = requests.post(
                f"{self.base_url}/influencer_videos",
                headers=self.headers,
                json=video_data
            )
            if not response.ok:
                print(f"[ERROR] 영상 INSERT 실패 {response.status_code}: {response.text[:300]}")
            response.raise_for_status()

            print(f"[OK] 새 영상 생성: {video_data['id']}")
            return video_data['id']

        except requests.exceptions.RequestException as e:
            print(f"[ERROR] 영상 생성/확인 실패: {e}")
            raise

    def insert_signal(self, signal_data: Dict[str, Any]) -> bool:
        """
        시그널 데이터 삽입
        
        Args:
            signal_data: {
                'video_uuid': str,
                'stock_symbol': str,
                'signal_type': str,
                'confidence': float,
                'reasoning': str,
                'timestamp_start': int,
                'timestamp_end': int,
                'context': str,
                'speaker_name': str,
                'analysis_version': str
            }
        
        Returns:
            bool: 성공 여부
        """
        try:
            # 중복 확인
            response = requests.get(
                f"{self.base_url}/signal_extractions",
                headers=self.headers,
                params={
                    'video_uuid': f'eq.{signal_data["video_uuid"]}',
                    'stock_symbol': f'eq.{signal_data["stock_symbol"]}',
                    'select': 'id'
                }
            )
            response.raise_for_status()
            
            data = response.json()
            if data:
                print(f"[WARNING] 중복 시그널 스킵: {signal_data['stock_symbol']} @ {signal_data['video_uuid'][:8]}...")
                return False
            
            # 시그널 삽입
            signal_insert_data = {
                'id': str(uuid.uuid4()),
                'video_uuid': signal_data['video_uuid'],
                'stock_symbol': signal_data['stock_symbol'],
                'signal_type': signal_data['signal_type'],
                'confidence': signal_data['confidence'],
                'reasoning': signal_data['reasoning'],
                'timestamp_start': signal_data['timestamp_start'],
                'timestamp_end': signal_data.get('timestamp_end', signal_data['timestamp_start']),
                'context': signal_data['context'],
                'speaker_name': signal_data.get('speaker_name', ''),
                'analysis_version': signal_data['analysis_version'],
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            response = requests.post(
                f"{self.base_url}/signal_extractions",
                headers=self.headers,
                json=signal_insert_data
            )
            response.raise_for_status()
            
            print(f"[OK] 시그널 삽입 성공: {signal_data['stock_symbol']} ({signal_data['signal_type']})")
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] 시그널 삽입 실패: {e}")
            return False

    def batch_insert_signals(self, signals: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        여러 시그널 일괄 삽입
        
        Args:
            signals: 시그널 데이터 리스트
        
        Returns:
            Dict[str, int]: {'success': 성공 수, 'failed': 실패 수, 'duplicates': 중복 수}
        """
        stats = {'success': 0, 'failed': 0, 'duplicates': 0}
        
        for signal in signals:
            try:
                result = self.insert_signal(signal)
                if result:
                    stats['success'] += 1
                else:
                    stats['duplicates'] += 1
            except Exception as e:
                print(f"[ERROR] 시그널 삽입 오류: {e}")
                stats['failed'] += 1
        
        return stats

    def get_existing_signals(self, video_url: str) -> List[Dict[str, Any]]:
        """
        특정 영상의 기존 시그널 조회
        
        Args:
            video_url: 영상 URL
        
        Returns:
            List[Dict]: 기존 시그널 목록
        """
        try:
            response = requests.get(
                f"{self.base_url}/investment_signals",
                headers=self.headers,
                params={
                    'video_url': f'eq.{video_url}',
                    'select': '*'
                }
            )
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            print(f"[ERROR] 기존 시그널 조회 실패: {e}")
            return []

    def get_existing_videos(self, channel_id: str) -> List[str]:
        """
        채널의 기존 영상 ID 목록 조회
        
        Args:
            channel_id: 채널 UUID
        
        Returns:
            List[str]: 영상 ID 목록
        """
        try:
            response = requests.get(
                f"{self.base_url}/influencer_videos",
                headers=self.headers,
                params={
                    'channel_id': f'eq.{channel_id}',
                    'select': 'video_id'
                }
            )
            response.raise_for_status()
            
            data = response.json()
            return [item['video_id'] for item in data]
            
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] 기존 영상 목록 조회 실패: {e}")
            return []

    def update_video_analysis_status(self, video_uuid: str, status: str) -> bool:
        """
        영상 분석 상태 업데이트
        ⚠️ influencer_videos 테이블에는 analysis_status/updated_at 컬럼이 없음.
        analyzed_at 컬럼만 사용 (completed 상태일 때만 업데이트).
        """
        try:
            if status != 'completed':
                return True  # pending/processing 은 DB 업데이트 불필요

            update_data = {
                'analyzed_at': datetime.now().isoformat(),
            }

            response = requests.patch(
                f"{self.base_url}/influencer_videos",
                headers=self.headers,
                params={'id': f'eq.{video_uuid}'},
                json=update_data
            )
            response.raise_for_status()
            return True

        except requests.exceptions.RequestException as e:
            print(f"[ERROR] 영상 상태 업데이트 실패 ({video_uuid[:8]}): {e}")
            return False

    def insert_analysis_results(self, channel_info: Dict[str, Any],
                                analysis_results: Any,
                                skip_existing: bool = False) -> Dict[str, int]:
        """
        auto_pipeline.py에서 호출: 분석 결과 배치를 DB에 INSERT
        analysis_results 구조:
          {'results': [{'video_id', 'video_uuid', 'signals', 'video_data', ...}, ...]}
        video_uuid는 이미 _process_single_video에서 확보된 상태여야 함.
        """
        stats = {'inserted_videos': 0, 'inserted_signals': 0, 'skipped_videos': 0}

        # analysis_results가 dict이면 results 리스트 추출
        if isinstance(analysis_results, dict):
            results_list = analysis_results.get('results', [])
        else:
            results_list = analysis_results  # 이미 리스트인 경우

        for result in results_list:
            video_uuid = result.get('video_uuid')
            signals = result.get('signals', [])

            if not video_uuid:
                print(f"  [WARNING] video_uuid 없음 — 건너뜀: {result.get('video_id', '?')}")
                stats['skipped_videos'] += 1
                continue

            # skip_existing: 이미 해당 video_uuid에 시그널이 있으면 스킵
            if skip_existing:
                try:
                    chk = requests.get(
                        f"{self.base_url}/influencer_signals",
                        headers=self.headers,
                        params={'video_id': f'eq.{video_uuid}', 'select': 'id', 'limit': '1'}
                    )
                    if chk.ok and chk.json():
                        print(f"  [SKIP] 기존 시그널 존재: {video_uuid[:8]}...")
                        stats['skipped_videos'] += 1
                        continue
                except Exception:
                    pass

            stats['inserted_videos'] += 1

            # 시그널 INSERT (run_corinpapa_batch.py 패턴과 동일)
            for signal in signals:
                try:
                    ok = self._insert_signal_for_video(video_uuid, signal)
                    if ok:
                        stats['inserted_signals'] += 1
                except Exception as e:
                    print(f"  [ERROR] 시그널 INSERT 실패: {e}")

        print(f"[DB] 영상 {stats['inserted_videos']}개, 시그널 {stats['inserted_signals']}개 INSERT 완료")
        return stats

    def _insert_signal_for_video(self, video_uuid: str, signal: Dict[str, Any]) -> bool:
        """단일 시그널 INSERT (influencer_signals 테이블, REST API)"""
        stock = signal.get('stock') or signal.get('stock_symbol', '')
        if not stock:
            return False

        signal_val = (signal.get('signal') or signal.get('signal_type') or
                      signal.get('mention_type') or 'NEUTRAL')

        # 영문 → 한글 변환 (DB check constraint: 한글 5단계만 허용)
        EN_TO_KO = {
            'BUY': '매수', 'STRONG_BUY': '매수',
            'POSITIVE': '긍정',
            'NEUTRAL': '중립', 'HOLD': '중립',
            'CONCERN': '부정', 'NEGATIVE': '부정',
            'SELL': '매도', 'STRONG_SELL': '매도',
        }
        signal_val = EN_TO_KO.get(signal_val.upper() if isinstance(signal_val, str) else signal_val,
                                  signal_val)
        # 여전히 영문이면 '중립' 폴백
        VALID_KO = {'매수', '긍정', '중립', '부정', '매도'}
        if signal_val not in VALID_KO:
            signal_val = '중립'

        # 중복 확인
        try:
            chk = requests.get(
                f"{self.base_url}/influencer_signals",
                headers=self.headers,
                params={
                    'video_id': f'eq.{video_uuid}',
                    'stock': f'eq.{stock}',
                    'select': 'id'
                }
            )
            if chk.ok and chk.json():
                print(f"  [DUP] {stock} ({signal_val}) — 스킵")
                return False
        except Exception:
            pass

        # 발언자 처리
        speaker_name = signal.get('speaker_name') or signal.get('speaker', '')
        speaker_id = None
        if speaker_name:
            speaker_id = self._get_or_create_speaker(speaker_name)

        # confidence: DB는 문자열 허용값 ('low', 'medium', 'high', 'very_high')
        raw_conf = signal.get('confidence', 'medium')
        if isinstance(raw_conf, str) and raw_conf.lower() in ('low', 'medium', 'high', 'very_high', 'very_low'):
            conf_val = raw_conf.lower()
        elif isinstance(raw_conf, (int, float)):
            # 숫자 → 문자열 변환 (1-10 스케일 또는 0-1 스케일 모두 처리)
            num = float(raw_conf)
            if num > 1.0:  # 1-10 스케일
                if num >= 8: conf_val = 'high'
                elif num >= 6: conf_val = 'medium'
                else: conf_val = 'low'
            else:  # 0-1 스케일
                if num >= 0.8: conf_val = 'high'
                elif num >= 0.5: conf_val = 'medium'
                else: conf_val = 'low'
        else:
            conf_val = 'medium'

        data = {
            'id': str(uuid.uuid4()),
            'video_id': video_uuid,
            'stock': stock,
            'ticker': signal.get('ticker', ''),
            'market': signal.get('market', 'OTHER'),
            'signal': signal_val,
            'mention_type': signal.get('mention_type', '결론'),
            'confidence': conf_val,
            'timestamp': signal.get('timestamp', signal.get('timestamp_start', '00:00')),
            'key_quote': signal.get('key_quote', signal.get('reasoning', '')),
            'reasoning': signal.get('reasoning', signal.get('key_quote', '')),
            'created_at': datetime.now().isoformat(),
        }
        if speaker_id:
            data['speaker_id'] = speaker_id

        resp = requests.post(
            f"{self.base_url}/influencer_signals",
            headers={**self.headers, 'Prefer': 'return=minimal'},
            json=data
        )
        if resp.ok:
            print(f"  [OK] INSERT: {stock} / {signal_val}")
            return True
        else:
            print(f"  [ERROR] INSERT 실패 {resp.status_code}: {resp.text[:200]}")
            return False

    def _get_or_create_speaker(self, speaker_name: str) -> Optional[str]:
        """발언자 확인/생성 (influencer_speakers 테이블)"""
        try:
            resp = requests.get(
                f"{self.base_url}/influencer_speakers",
                headers=self.headers,
                params={'name': f'eq.{speaker_name}', 'select': 'id'}
            )
            if resp.ok and resp.json():
                return resp.json()[0]['id']
            # 없으면 생성
            new_id = str(uuid.uuid4())
            cr = requests.post(
                f"{self.base_url}/influencer_speakers",
                headers={**self.headers, 'Prefer': 'return=minimal'},
                json={'id': new_id, 'name': speaker_name,
                      'created_at': datetime.now().isoformat()}
            )
            return new_id if cr.ok else None
        except Exception:
            return None

    def update_signal_prices_json(self) -> list:
        """
        signal_prices.json 업데이트를 위한 데이터 수집 (REST API 버전)
        auto_pipeline.py Step 7 이후 호출됨.
        """
        try:
            print("\n=== signal_prices.json 업데이트 준비 ===")
            resp = requests.get(
                f"{self.base_url}/influencer_signals",
                headers=self.headers,
                params={'select': 'stock,ticker,market'}
            )
            resp.raise_for_status()

            unique_stocks = {}
            for sig in resp.json():
                stock = sig.get('stock', '')
                if stock and stock not in unique_stocks:
                    unique_stocks[stock] = {
                        'stock': stock,
                        'ticker': sig.get('ticker', ''),
                        'market': sig.get('market', 'OTHER')
                    }

            print(f"고유 종목 수: {len(unique_stocks)}개")
            stocks_list = list(unique_stocks.values())

            # 저장
            import os as _os
            import json as _json
            out_path = _os.path.join(
                _os.path.dirname(_os.path.abspath(__file__)),
                'stocks_for_price_update.json'
            )
            with open(out_path, 'w', encoding='utf-8') as f:
                _json.dump(stocks_list, f, ensure_ascii=False, indent=2)
            print(f"[OK] 저장: {out_path}")
            return stocks_list

        except Exception as e:
            print(f"[ERROR] update_signal_prices_json 실패: {e}")
            return []

    def get_signal_stats(self) -> Dict[str, int]:
        """
        시그널 통계 조회
        
        Returns:
            Dict[str, int]: 통계 정보
        """
        try:
            response = requests.get(
                f"{self.base_url}/signal_extractions",
                headers=self.headers,
                params={'select': 'id,signal_type'}
            )
            response.raise_for_status()
            
            data = response.json()
            stats = {'total': len(data)}
            
            for signal in data:
                signal_type = signal['signal_type']
                stats[signal_type] = stats.get(signal_type, 0) + 1
            
            return stats
            
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] 시그널 통계 조회 실패: {e}")
            return {'total': 0}