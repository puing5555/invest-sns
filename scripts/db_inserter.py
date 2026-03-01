# db_inserter.py - Supabase DB INSERT 모듈
import json
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from supabase import create_client, Client
from pipeline_config import PipelineConfig

class DatabaseInserter:
    def __init__(self):
        self.config = PipelineConfig()
        self.supabase: Client = create_client(
            self.config.SUPABASE_URL,
            self.config.SUPABASE_SERVICE_KEY
        )
    
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
            response = self.supabase.table('influencer_channels') \
                .select('id') \
                .eq('url', channel_info['url']) \
                .execute()
            
            if response.data:
                channel_id = response.data[0]['id']
                print(f"✓ 기존 채널 발견: {channel_id}")
                return channel_id
            
            # 새 채널 생성
            channel_data = {
                'id': str(uuid.uuid4()),
                'name': channel_info['name'],
                'url': channel_info['url'],
                'description': channel_info.get('description', ''),
                'subscriber_count': channel_info.get('subscriber_count', 0),
                'video_count': channel_info.get('video_count', 0),
                'created_at': datetime.now().isoformat()
            }
            
            response = self.supabase.table('influencer_channels') \
                .insert(channel_data) \
                .execute()
            
            channel_id = response.data[0]['id']
            print(f"✓ 새 채널 생성: {channel_id} ({channel_info['name']})")
            return channel_id
            
        except Exception as e:
            print(f"❌ 채널 생성 에러: {e}")
            raise
    
    def get_or_create_speaker(self, speaker_name: str) -> str:
        """
        발언자 정보 확인/생성
        
        Args:
            speaker_name: 발언자 이름
        
        Returns:
            speaker_id (UUID)
        """
        try:
            # 기존 발언자 확인 (이름 정규화 고려)
            response = self.supabase.table('speakers') \
                .select('id') \
                .eq('name', speaker_name) \
                .execute()
            
            if response.data:
                speaker_id = response.data[0]['id']
                return speaker_id
            
            # 새 발언자 생성
            speaker_data = {
                'id': str(uuid.uuid4()),
                'name': speaker_name,
                'created_at': datetime.now().isoformat()
            }
            
            response = self.supabase.table('speakers') \
                .insert(speaker_data) \
                .execute()
            
            speaker_id = response.data[0]['id']
            print(f"✓ 새 발언자 생성: {speaker_name} ({speaker_id})")
            return speaker_id
            
        except Exception as e:
            print(f"❌ 발언자 생성 에러: {e}")
            raise
    
    def insert_video(self, channel_id: str, video_data: Dict[str, Any]) -> str:
        """
        영상 정보 INSERT
        
        Args:
            channel_id: 채널 ID
            video_data: 영상 데이터
        
        Returns:
            video_id (UUID)
        """
        try:
            # 기존 영상 확인 (URL 기준)
            response = self.supabase.table('influencer_videos') \
                .select('id') \
                .eq('url', video_data['url']) \
                .execute()
            
            if response.data:
                video_id = response.data[0]['id']
                print(f"기존 영상 발견: {video_id}")
                return video_id
            
            # 유튜브 video_id 추출
            import re
            youtube_id_match = re.search(r'(?:watch\?v=|youtu\.be\/)([^&\n?#]+)', video_data['url'])
            youtube_video_id = youtube_id_match.group(1) if youtube_id_match else ''
            
            # 새 영상 INSERT
            video_insert_data = {
                'id': str(uuid.uuid4()),
                'channel_id': channel_id,
                'youtube_video_id': youtube_video_id,
                'title': video_data['title'],
                'url': video_data['url'],
                'thumbnail_url': video_data.get('thumbnail', ''),
                'duration': video_data.get('duration', ''),
                'view_count': video_data.get('view_count', 0),
                'upload_date': video_data.get('upload_date', datetime.now().isoformat()),
                'subtitle': video_data.get('subtitle', ''),
                'video_summary': video_data.get('video_summary', ''),
                'created_at': datetime.now().isoformat()
            }
            
            response = self.supabase.table('influencer_videos') \
                .insert(video_insert_data) \
                .execute()
            
            video_id = response.data[0]['id']
            print(f"✓ 새 영상 INSERT: {video_id}")
            return video_id
            
        except Exception as e:
            print(f"❌ 영상 INSERT 에러: {e}")
            raise
    
    def insert_signals(self, video_id: str, signals: List[Dict[str, Any]]) -> int:
        """
        시그널 데이터 INSERT
        
        Args:
            video_id: 영상 ID
            signals: 시그널 리스트
        
        Returns:
            INSERT된 시그널 수
        """
        if not signals:
            return 0
        
        inserted_count = 0
        
        try:
            for signal in signals:
                # 발언자 확인/생성
                speaker_id = self.get_or_create_speaker(signal['speaker'])
                
                # 중복 시그널 확인
                response = self.supabase.table('influencer_signals') \
                    .select('id') \
                    .eq('video_id', video_id) \
                    .eq('speaker_id', speaker_id) \
                    .eq('stock', signal['stock']) \
                    .execute()
                
                if response.data:
                    print(f"중복 시그널 건너뛰기: {signal['speaker']} - {signal['stock']}")
                    continue
                
                # 시그널 INSERT
                signal_data = {
                    'id': str(uuid.uuid4()),
                    'video_id': video_id,
                    'speaker_id': speaker_id,
                    'stock': signal['stock'],
                    'ticker': signal.get('ticker', ''),
                    'market': signal.get('market', 'OTHER'),
                    'mention_type': signal.get('mention_type', '결론'),
                    'signal': signal['signal'],
                    'confidence': signal.get('confidence', 'medium'),
                    'timestamp': signal.get('timestamp', '00:00'),
                    'key_quote': signal.get('key_quote', ''),
                    'reasoning': signal.get('reasoning', ''),
                    'created_at': datetime.now().isoformat()
                }
                
                response = self.supabase.table('influencer_signals') \
                    .insert(signal_data) \
                    .execute()
                
                if response.data:
                    inserted_count += 1
                    print(f"✓ 시그널 INSERT: {signal['speaker']} - {signal['stock']} ({signal['signal']})")
                
        except Exception as e:
            print(f"❌ 시그널 INSERT 에러: {e}")
            raise
        
        return inserted_count
    
    def check_existing_video(self, url: str) -> bool:
        """기존 영상 존재 여부 확인"""
        try:
            response = self.supabase.table('influencer_videos') \
                .select('id') \
                .eq('url', url) \
                .execute()
            
            return len(response.data) > 0
        except:
            return False
    
    def insert_analysis_results(self, channel_info: Dict[str, Any], 
                              analysis_results: List[Dict[str, Any]], 
                              skip_existing: bool = False) -> Dict[str, int]:
        """
        분석 결과를 DB에 INSERT
        
        Args:
            channel_info: 채널 정보
            analysis_results: 분석 결과 리스트
            skip_existing: 기존 영상 건너뛰기 여부
        
        Returns:
            INSERT 통계
        """
        stats = {
            'total_videos': len(analysis_results),
            'inserted_videos': 0,
            'skipped_videos': 0,
            'total_signals': 0,
            'inserted_signals': 0
        }
        
        try:
            print(f"\n=== DB INSERT 시작 ===")
            
            # 1. 채널 확인/생성
            channel_id = self.get_or_create_channel(channel_info)
            
            # 2. 영상 및 시그널 INSERT
            for i, result in enumerate(analysis_results):
                print(f"\n진행: {i+1}/{len(analysis_results)} - {result['title'][:50]}...")
                
                # 기존 영상 건너뛰기 옵션
                if skip_existing and self.check_existing_video(result['url']):
                    print(f"기존 영상 건너뛰기: {result['url']}")
                    stats['skipped_videos'] += 1
                    continue
                
                # 영상 INSERT
                video_id = self.insert_video(channel_id, result)
                stats['inserted_videos'] += 1
                
                # 시그널 INSERT
                if 'signals' in result and result['signals']:
                    signal_count = self.insert_signals(video_id, result['signals'])
                    stats['inserted_signals'] += signal_count
                    stats['total_signals'] += len(result['signals'])
            
            print(f"\n=== DB INSERT 완료 ===")
            print(f"채널: {channel_info['name']}")
            print(f"영상 INSERT: {stats['inserted_videos']}개")
            print(f"영상 건너뛰기: {stats['skipped_videos']}개")
            print(f"시그널 INSERT: {stats['inserted_signals']}/{stats['total_signals']}개")
            
            return stats
            
        except Exception as e:
            print(f"❌ DB INSERT 에러: {e}")
            raise
    
    def update_signal_prices_json(self):
        """signal_prices.json 업데이트를 위한 데이터 수집"""
        try:
            print("\n=== signal_prices.json 업데이트 준비 ===")
            
            # 모든 시그널에서 고유 종목 목록 수집
            response = self.supabase.table('influencer_signals') \
                .select('stock, ticker, market') \
                .execute()
            
            # 중복 제거하여 고유 종목 목록 생성
            unique_stocks = {}
            for signal in response.data:
                stock = signal['stock']
                if stock not in unique_stocks:
                    unique_stocks[stock] = {
                        'stock': stock,
                        'ticker': signal.get('ticker', ''),
                        'market': signal.get('market', 'OTHER')
                    }
            
            print(f"고유 종목 수: {len(unique_stocks)}개")
            
            # yfinance 스크립트 호출을 위한 종목 목록 저장
            stocks_for_price_update = list(unique_stocks.values())
            
            with open('scripts/stocks_for_price_update.json', 'w', encoding='utf-8') as f:
                json.dump(stocks_for_price_update, f, ensure_ascii=False, indent=2)
            
            print("✓ 가격 업데이트용 종목 목록 저장: scripts/stocks_for_price_update.json")
            print("다음 명령어로 가격 업데이트를 실행하세요:")
            print("python scripts/gen_prices.py")
            
            return stocks_for_price_update
            
        except Exception as e:
            print(f"❌ 가격 업데이트 준비 에러: {e}")
            return []