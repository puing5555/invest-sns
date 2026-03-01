# signal_analyzer.py - AI 시그널 분석 모듈
import time
import json
from typing import List, Dict, Any, Optional
import anthropic
from pipeline_config import PipelineConfig

class SignalAnalyzer:
    def __init__(self):
        self.config = PipelineConfig()
        self.client = anthropic.Anthropic(api_key=self.config.ANTHROPIC_API_KEY)
        self.prompt_template = self.config.load_prompt()
        
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
            파싱된 데이터 딕셔너리
        """
        try:
            # JSON 블록 찾기
            import re
            json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
            
            if json_match:
                json_str = json_match.group(1)
                data = json.loads(json_str)
                return data
            
            # JSON 블록이 없으면 전체 응답에서 JSON 찾기 시도
            try:
                # { 로 시작하는 첫 번째 JSON 객체 찾기
                start_idx = response_text.find('{')
                if start_idx != -1:
                    # 균형잡힌 중괄호 찾기
                    brace_count = 0
                    end_idx = start_idx
                    
                    for i in range(start_idx, len(response_text)):
                        if response_text[i] == '{':
                            brace_count += 1
                        elif response_text[i] == '}':
                            brace_count -= 1
                            if brace_count == 0:
                                end_idx = i
                                break
                    
                    json_str = response_text[start_idx:end_idx + 1]
                    data = json.loads(json_str)
                    return data
            except:
                pass
            
            # JSON 파싱 실패 시 텍스트 응답으로 간주
            return {
                "video_summary": response_text,
                "signals": [],
                "analysis_error": "JSON 파싱 실패 - 텍스트 응답으로 처리"
            }
            
        except json.JSONDecodeError as e:
            return {
                "video_summary": response_text[:500] + "...",
                "signals": [],
                "analysis_error": f"JSON 파싱 에러: {str(e)}"
            }
        except Exception as e:
            return {
                "video_summary": "분석 실패",
                "signals": [],
                "analysis_error": f"응답 파싱 에러: {str(e)}"
            }
    
    def validate_signal(self, signal: Dict[str, Any]) -> Dict[str, Any]:
        """
        시그널 데이터 유효성 검증 및 정제
        
        Args:
            signal: 원본 시그널 데이터
        
        Returns:
            검증된 시그널 데이터
        """
        # 필수 필드 확인
        required_fields = ['speaker', 'stock', 'signal', 'confidence']
        for field in required_fields:
            if field not in signal:
                signal[field] = 'unknown'
        
        # signal 값 검증 (한글 5단계만 허용)
        valid_signals = self.config.SIGNAL_TYPES
        if signal['signal'] not in valid_signals:
            # 영어 시그널을 한글로 변환
            signal_mapping = {
                'BUY': '매수', 'STRONG_BUY': '매수',
                'POSITIVE': '긍정',
                'HOLD': '중립', 'NEUTRAL': '중립',
                'CONCERN': '경계', 'CAUTION': '경계',
                'SELL': '매도', 'STRONG_SELL': '매도'
            }
            signal['signal'] = signal_mapping.get(signal['signal'], '중립')
        
        # confidence 값 검증
        valid_confidence = ['very_high', 'high', 'medium', 'low', 'very_low']
        if signal['confidence'] not in valid_confidence:
            signal['confidence'] = 'medium'
        
        # market 값 검증
        valid_markets = ['KR', 'US', 'US_ADR', 'CRYPTO', 'CRYPTO_DEFI', 'SECTOR', 'INDEX', 'ETF', 'OTHER']
        if 'market' not in signal or signal['market'] not in valid_markets:
            signal['market'] = 'OTHER'
        
        # mention_type 값 검증
        valid_mention_types = ['결론', '논거', '뉴스', '리포트', '교육', '티저', '보유', '컨센서스', '세무', '차익거래', '시나리오']
        if 'mention_type' not in signal or signal['mention_type'] not in valid_mention_types:
            signal['mention_type'] = '결론'
        
        # timestamp 형식 확인
        if 'timestamp' not in signal:
            signal['timestamp'] = '00:00'
        
        # key_quote 길이 확인 (V10.1 규칙 30: 최소 20자)
        if 'key_quote' not in signal or len(signal['key_quote']) < 20:
            signal['key_quote'] = f"{signal['stock']} 관련 {signal['signal']} 의견"
        
        # reasoning 필드 확인
        if 'reasoning' not in signal:
            signal['reasoning'] = f"{signal['mention_type']} 타입의 {signal['signal']} 시그널"
        
        return signal
    
    def analyze_video(self, channel_url: str, video_data: dict, subtitle: str) -> Dict[str, Any]:
        """
        단일 영상 분석
        
        Args:
            channel_url: 채널 URL
            video_data: 영상 정보
            subtitle: 자막 텍스트
        
        Returns:
            분석 결과
        """
        if not subtitle:
            return {
                "video_summary": "자막 없음 - 분석 불가",
                "signals": [],
                "analysis_error": "자막 추출 실패"
            }
        
        try:
            print(f"AI 분석 시작: {video_data['title'][:50]}...")
            
            # 프롬프트 생성
            prompt = self.create_analysis_prompt(channel_url, video_data, subtitle)
            
            # Claude API 호출
            response = self.client.messages.create(
                model=self.config.ANTHROPIC_MODEL,
                max_tokens=4000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            response_text = response.content[0].text
            print(f"[OK] AI 분석 완료: {len(response_text)} 글자")
            
            # 응답 파싱
            analysis_result = self.parse_analysis_response(response_text)
            
            # 시그널 검증
            if 'signals' in analysis_result and analysis_result['signals']:
                validated_signals = []
                for signal in analysis_result['signals']:
                    validated_signal = self.validate_signal(signal)
                    validated_signals.append(validated_signal)
                analysis_result['signals'] = validated_signals
                
                print(f"[OK] 시그널 검증 완료: {len(validated_signals)}개")
            else:
                analysis_result['signals'] = []
                print(f"시그널 없음")
            
            return analysis_result
            
        except Exception as e:
            print(f"[ERROR] AI 분석 에러: {e}")
            return {
                "video_summary": f"분석 에러: {str(e)}",
                "signals": [],
                "analysis_error": str(e)
            }
    
    def analyze_videos_batch(self, channel_url: str, videos_with_subtitles: List[Dict]) -> List[Dict]:
        """
        여러 영상 일괄 분석 (레이트리밋 적용)
        
        Args:
            channel_url: 채널 URL
            videos_with_subtitles: 자막이 포함된 영상 목록
        
        Returns:
            분석 결과 목록
        """
        results = []
        
        # 자막이 있는 영상만 필터링
        videos_to_analyze = [v for v in videos_with_subtitles if v.get('subtitle')]
        
        print(f"\n=== AI 분석 시작 ===")
        print(f"분석 대상: {len(videos_to_analyze)}개 영상")
        
        for i, video in enumerate(videos_to_analyze):
            print(f"\n진행: {i+1}/{len(videos_to_analyze)}")
            
            # 영상 분석
            analysis_result = self.analyze_video(channel_url, video, video['subtitle'])
            
            # 원본 영상 데이터와 분석 결과 병합
            video_result = video.copy()
            video_result.update(analysis_result)
            
            results.append(video_result)
            
            # API 레이트리밋 (마지막이 아닐 때만)
            if i < len(videos_to_analyze) - 1:
                print(f"API 대기: {self.config.RATE_LIMIT_API_REQUESTS}초...")
                time.sleep(self.config.RATE_LIMIT_API_REQUESTS)
        
        # 분석 완료 요약
        total_signals = sum(len(r.get('signals', [])) for r in results)
        successful_analyses = sum(1 for r in results if not r.get('analysis_error'))
        
        print(f"\n=== AI 분석 완료 ===")
        print(f"성공: {successful_analyses}/{len(videos_to_analyze)}개")
        print(f"총 시그널: {total_signals}개")
        
        return results
    
    def save_analysis_results(self, results: List[Dict], filename: str):
        """분석 결과를 JSON 파일로 저장"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"[OK] 분석 결과 저장: {filename}")
        except Exception as e:
            print(f"[ERROR] 결과 저장 실패: {e}")