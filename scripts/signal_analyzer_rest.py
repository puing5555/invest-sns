# signal_analyzer_rest.py - AI 시그널 분석 모듈 (REST API 직접 호출)
import time
import json
import requests
from typing import List, Dict, Any, Optional
from pipeline_config import PipelineConfig

class SignalAnalyzer:
    def __init__(self):
        self.config = PipelineConfig()
        self.api_key = self.config.ANTHROPIC_API_KEY
        self.prompt_template = self.config.load_prompt()
        self.api_url = "https://api.anthropic.com/v1/messages"
        
        self.headers = {
            'Content-Type': 'application/json',
            'x-api-key': self.api_key,
            'anthropic-version': '2023-06-01'
        }
        
    def create_analysis_prompt(self, channel_url: str, video_data: dict, subtitle: str) -> str:
        """
        분석용 프롬프트 생성
        
        Args:
            channel_url: 채널 URL
            video_data: 영상 정보 (title, url, duration, upload_date 등)
            subtitle: 자막 텍스트
        
        Returns:
            완성된 프롬프트
        """
        # 기본 프롬프트에서 채널 URL 교체
        prompt = self.prompt_template.replace('{CHANNEL_URL}', channel_url)
        
        # 영상 정보 추가
        video_info = f"""
=== 분석 대상 영상 ===
제목: {video_data['title']}
URL: {video_data['url']}
길이: {video_data.get('duration', 'N/A')}
업로드: {video_data.get('upload_date', 'N/A')}

=== 자막 내용 ===
{subtitle}

=== 분석 지시사항 ===
위 영상의 자막을 V10.1 프롬프트 규칙에 따라 분석하고, JSON 형태로 시그널을 추출해주세요.
"""
        
        return prompt + "\n\n" + video_info
    
    def parse_analysis_response(self, response_text: str) -> Dict[str, Any]:
        """
        Claude 응답을 파싱하여 구조화된 데이터로 변환
        
        Args:
            response_text: Claude 응답 텍스트
        
        Returns:
            파싱된 분석 결과
        """
        try:
            # JSON 블록 찾기 (```json ... ``` 또는 {...} 직접)
            if '```json' in response_text:
                start = response_text.find('```json') + 7
                end = response_text.find('```', start)
                json_str = response_text[start:end].strip()
            elif '{' in response_text and '}' in response_text:
                start = response_text.find('{')
                end = response_text.rfind('}') + 1
                json_str = response_text[start:end]
            else:
                print("[ERROR] JSON 블록을 찾을 수 없습니다")
                return {"error": "No JSON found", "raw_response": response_text}
            
            # JSON 파싱
            result = json.loads(json_str)
            return result
            
        except json.JSONDecodeError as e:
            print(f"[ERROR] JSON 파싱 오류: {e}")
            return {"error": "JSON decode error", "raw_response": response_text}
        except Exception as e:
            print(f"[ERROR] 응답 파싱 오류: {e}")
            return {"error": str(e), "raw_response": response_text}
    
    def analyze_video_subtitle(self, channel_url: str, video_data: dict, subtitle: str, 
                             retry_count: int = 3) -> Optional[Dict[str, Any]]:
        """
        영상 자막을 분석하여 투자 시그널 추출
        
        Args:
            channel_url: 채널 URL
            video_data: 영상 정보
            subtitle: 자막 텍스트  
            retry_count: 재시도 횟수
        
        Returns:
            분석 결과 또는 None (실패 시)
        """
        if not subtitle or len(subtitle.strip()) < 50:
            print(f"[WARNING] 자막이 너무 짧습니다: {len(subtitle)} chars")
            return None
        
        prompt = self.create_analysis_prompt(channel_url, video_data, subtitle)
        
        for attempt in range(retry_count):
            try:
                print(f"[AI] Claude 분석 중... (시도 {attempt + 1}/{retry_count})")
                
                # Anthropic API 호출
                payload = {
                    'model': 'claude-3-haiku-20240307',
                    'max_tokens': 4000,
                    'messages': [
                        {
                            'role': 'user',
                            'content': prompt
                        }
                    ]
                }
                
                response = requests.post(
                    self.api_url,
                    headers=self.headers,
                    json=payload,
                    timeout=60
                )
                
                # 레이트 리밋 처리
                if response.status_code == 429:
                    print("[WAIT] 레이트 리밋 - 60초 대기 중...")
                    time.sleep(60)
                    continue
                
                response.raise_for_status()
                result = response.json()
                
                if 'content' in result and result['content']:
                    response_text = result['content'][0]['text']
                    
                    # 응답 파싱
                    parsed_result = self.parse_analysis_response(response_text)
                    
                    if 'error' not in parsed_result:
                        print(f"[SUCCESS] 분석 완료")
                        return parsed_result
                    else:
                        print(f"[WARNING] 파싱 오류: {parsed_result['error']}")
                        if attempt < retry_count - 1:
                            continue
                        return None
                else:
                    print("[ERROR] 빈 응답")
                    return None
                    
            except requests.exceptions.Timeout:
                print(f"[TIMEOUT] 타임아웃 (시도 {attempt + 1})")
                if attempt < retry_count - 1:
                    time.sleep(2 ** attempt)  # 지수 백오프
                    
            except requests.exceptions.RequestException as e:
                print(f"[ERROR] API 요청 오류: {e}")
                if attempt < retry_count - 1:
                    time.sleep(2 ** attempt)
                else:
                    return None
                    
            except Exception as e:
                print(f"[ERROR] 예상치 못한 오류: {e}")
                return None
        
        print(f"[ERROR] {retry_count}번 시도 모두 실패")
        return None
    
    def convert_to_database_format(self, analysis_result: Dict[str, Any], 
                                 video_uuid: str, analysis_version: str = "V10.3") -> List[Dict[str, Any]]:
        """분석 결과를 데이터베이스 삽입 형식으로 변환"""
        signals = []
        
        # 시그널 타입 매핑 (한글/영문 -> DB 영문)
        signal_type_mapping = {
            '매수': 'BUY', '긍정': 'POSITIVE', '중립': 'NEUTRAL',
            '경계': 'CONCERN', '매도': 'SELL',
            'STRONG_BUY': 'STRONG_BUY', 'BUY': 'BUY', 'POSITIVE': 'POSITIVE',
            'HOLD': 'NEUTRAL', 'NEUTRAL': 'NEUTRAL', 'CONCERN': 'CONCERN',
            'SELL': 'SELL', 'STRONG_SELL': 'STRONG_SELL'
        }
        allowed_types = ['STRONG_BUY', 'BUY', 'POSITIVE', 'NEUTRAL', 'CONCERN', 'SELL', 'STRONG_SELL']
        
        # confidence 문자열 -> 숫자 매핑
        confidence_mapping = {
            'very_high': 0.95, 'high': 0.85, 'medium': 0.65, 'low': 0.45, 'very_low': 0.25
        }
        
        try:
            signal_list = analysis_result.get('signals', [])
            
            for signal in signal_list:
                try:
                    # 종목 심볼
                    stock_symbol = (signal.get('ticker') or signal.get('stock_symbol') 
                                   or signal.get('stock', '')).upper()
                    if not stock_symbol:
                        continue
                    
                    # 시그널 타입
                    raw_signal = signal.get('signal') or signal.get('signal_type') or signal.get('mention_type', '')
                    signal_type = signal_type_mapping.get(raw_signal, raw_signal.upper() if raw_signal else 'NEUTRAL')
                    if signal_type not in allowed_types:
                        signal_type = 'NEUTRAL'
                    
                    # confidence
                    conf = signal.get('confidence', 0.5)
                    if isinstance(conf, str):
                        conf = confidence_mapping.get(conf.lower(), 0.5)
                    
                    # 타임스탬프 (MM:SS -> 초)
                    ts_raw = signal.get('timestamp', signal.get('timestamp_start', 0))
                    if isinstance(ts_raw, str) and ':' in ts_raw:
                        parts = ts_raw.split(':')
                        ts = int(parts[0]) * 60 + int(parts[1])
                    else:
                        ts = int(ts_raw) if ts_raw else 0
                    
                    # reasoning
                    reasoning = signal.get('reasoning', signal.get('key_quote', ''))
                    context = signal.get('context', signal.get('key_quote', ''))
                    speaker = signal.get('speaker_name', signal.get('speaker', ''))
                    
                    db_signal = {
                        'video_uuid': video_uuid,
                        'stock_symbol': stock_symbol,
                        'signal_type': signal_type,
                        'confidence': float(conf),
                        'reasoning': reasoning,
                        'timestamp_start': ts,
                        'timestamp_end': ts,
                        'context': context,
                        'speaker_name': speaker,
                        'analysis_version': analysis_version
                    }
                    signals.append(db_signal)
                except Exception as e:
                    print(f"[WARNING] 시그널 변환 오류 (스킵): {e}")
                    continue
            
            print(f"[SUCCESS] {len(signals)}개 시그널 변환 완료")
            return signals
            
        except Exception as e:
            print(f"[ERROR] 데이터베이스 형식 변환 오류: {e}")
            return []
    
    def batch_analyze_videos(self, channel_url: str, videos_with_subtitles: List[Dict[str, Any]],
                           delay_seconds: int = 3) -> Dict[str, Any]:
        """
        여러 영상 일괄 분석
        
        Args:
            channel_url: 채널 URL
            videos_with_subtitles: 영상+자막 데이터 리스트
            delay_seconds: 요청 간 딜레이
        
        Returns:
            일괄 분석 결과 통계
        """
        stats = {
            'total': len(videos_with_subtitles),
            'success': 0,
            'failed': 0,
            'signals_extracted': 0,
            'results': []
        }
        
        for i, video_data in enumerate(videos_with_subtitles):
            try:
                print(f"\n[VIDEO] [{i+1}/{len(videos_with_subtitles)}] {video_data['title'][:50]}...")
                
                # 분석 실행
                analysis_result = self.analyze_video_subtitle(
                    channel_url, 
                    video_data, 
                    video_data['subtitle']
                )
                
                if analysis_result:
                    # 데이터베이스 형식 변환
                    signals = self.convert_to_database_format(
                        analysis_result, 
                        video_data['video_uuid']
                    )
                    
                    stats['success'] += 1
                    stats['signals_extracted'] += len(signals)
                    stats['results'].append({
                        'video_id': video_data['video_id'],
                        'video_uuid': video_data['video_uuid'],
                        'signals': signals,
                        'analysis_result': analysis_result
                    })
                    
                    print(f"[SUCCESS] 분석 성공: {len(signals)}개 시그널 추출")
                else:
                    stats['failed'] += 1
                    print(f"[ERROR] 분석 실패")
                
                # 레이트 리밋 준수
                if i < len(videos_with_subtitles) - 1:
                    print(f"[WAIT] {delay_seconds}초 대기...")
                    time.sleep(delay_seconds)
                    
                # 20개마다 5분 휴식
                if (i + 1) % 20 == 0 and i < len(videos_with_subtitles) - 1:
                    print(f"[SLEEP] 20개 분석 완료 - 5분 휴식 중...")
                    time.sleep(300)
                    
            except KeyboardInterrupt:
                print("\n[STOP] 사용자 중단")
                break
            except Exception as e:
                print(f"[ERROR] 영상 분석 중 오류: {e}")
                stats['failed'] += 1
        
        return stats