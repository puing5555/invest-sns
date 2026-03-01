# db_inserter_rest.py - Supabase REST API 직접 호출 모듈
import json
import uuid
import requests
from datetime import datetime
from typing import List, Dict, Any, Optional
from pipeline_config import PipelineConfig

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
                'url': str,
                'name': str,
                'subscriber_count': int,
                'video_count': int,
                'description': str
            }
        
        Returns:
            channel_id (UUID)
        """
        try:
            # 기존 채널 확인
            response = requests.get(
                f"{self.base_url}/influencer_channels",
                headers=self.headers,
                params={'url': f'eq.{channel_info["url"]}', 'select': 'id'}
            )
            response.raise_for_status()
            
            data = response.json()
            if data:
                channel_id = data[0]['id']
                print(f"[OK] 기존 채널 발견: {channel_id}")
                return channel_id
            
            # 새 채널 생성
            channel_data = {
                'id': str(uuid.uuid4()),
                'name': channel_info['name'],
                'url': channel_info['url'],
                'description': channel_info.get('description', ''),
                'subscriber_count': channel_info.get('subscriber_count', 0),
                'video_count': channel_info.get('video_count', 0),
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            response = requests.post(
                f"{self.base_url}/influencer_channels",
                headers=self.headers,
                json=channel_data
            )
            response.raise_for_status()
            
            print(f"[OK] 새 채널 생성: {channel_data['id']}")
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
            # 기존 영상 확인
            response = requests.get(
                f"{self.base_url}/influencer_videos",
                headers=self.headers,
                params={'video_id': f'eq.{video_info["video_id"]}', 'select': 'id'}
            )
            response.raise_for_status()
            
            data = response.json()
            if data:
                video_uuid = data[0]['id']
                print(f"[OK] 기존 영상 발견: {video_uuid}")
                return video_uuid
            
            # 새 영상 생성
            video_data = {
                'id': str(uuid.uuid4()),
                'video_id': video_info['video_id'],
                'channel_id': channel_id,
                'title': video_info['title'],
                'upload_date': video_info['upload_date'],
                'duration': video_info.get('duration', 0),
                'view_count': video_info.get('view_count', 0),
                'description': video_info.get('description', ''),
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            response = requests.post(
                f"{self.base_url}/influencer_videos",
                headers=self.headers,
                json=video_data
            )
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
        
        Args:
            video_uuid: 영상 UUID
            status: 상태 ('pending', 'processing', 'completed', 'failed')
        
        Returns:
            bool: 성공 여부
        """
        try:
            update_data = {
                'analysis_status': status,
                'updated_at': datetime.now().isoformat()
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
            print(f"[ERROR] 영상 상태 업데이트 실패: {e}")
            return False

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