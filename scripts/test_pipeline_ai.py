# test_pipeline_ai.py - AI 분석 파이프라인 테스트
import sys
import os
import uuid

# 현재 디렉토리를 scripts에 추가
sys.path.append(os.path.dirname(__file__))

from signal_analyzer_rest import SignalAnalyzer
from db_inserter_rest import DatabaseInserter

def test_ai_pipeline():
    """샘플 데이터로 AI 분석 파이프라인 테스트"""
    
    # 1. 샘플 투자 자막 데이터 (세상101 스타일)
    sample_subtitle = """
    안녕하세요 세상학개론입니다. 오늘은 비트코인의 미래에 대해서 얘기해보려고 합니다. 
    
    최근에 트럼프가 당선되면서 비트코인이 9만 달러를 넘어섰는데요, 정말 놀라운 상승이었습니다.
    
    저는 개인적으로 비트코인을 100만 달러까지 갈 수 있다고 봅니다. 그 이유는 세 가지인데요.
    
    첫째, 기관 투자자들의 유입이 계속되고 있습니다. 블랙록, 피델리티 같은 자산운용사들이 
    비트코인 ETF를 운용하면서 꾸준히 매수하고 있거든요.
    
    둘째, 정부 차원에서의 지원입니다. 트럼프 정부는 암호화폐 친화적인 정책을 펼칠 것으로 
    예상되고 있습니다.
    
    셋째, 공급량의 한계입니다. 비트코인은 2100만 개로 제한되어 있기 때문에 수요가 늘어나면 
    가격 상승은 필연적입니다.
    
    그렇다고 해서 무작정 매수하라는 건 아닙니다. 적정 비중으로 포트폴리오에 편입하시고,
    장기 투자 관점에서 접근하시기 바랍니다.
    
    다음으로 팔란티어에 대해서도 얘기해보겠습니다. 팔란티어는 최근 실적 발표에서 
    매출이 30% 성장했다고 발표했는데요.
    
    AI와 빅데이터 분야에서 독보적인 기술력을 가지고 있고, 정부 계약도 늘어나고 있어서 
    저는 팔란티어에 대해서 긍정적으로 보고 있습니다.
    
    목표가는 50달러 정도로 잡고 있고요, 현재 가격에서 매수해도 좋을 것 같습니다.
    
    마지막으로 엔비디아 얘기도 잠깐 하자면, AI 붐이 계속되는 한 엔비디아의 성장도 
    지속될 것으로 봅니다. 다만 밸류에이션이 부담스러운 수준이라 신중하게 접근하시기 바랍니다.
    
    오늘 영상은 여기까지입니다. 구독과 좋아요 부탁드려요!
    """
    
    # 2. 영상 데이터 준비
    video_data = {
        'title': '비트코인 100만 달러 전망과 팔란티어 투자 의견',
        'video_id': 'test123456',
        'url': 'https://www.youtube.com/watch?v=test123456',
        'duration': '15:30',
        'upload_date': '20241201'
    }
    
    channel_url = 'https://www.youtube.com/@sesang101'
    
    try:
        print("=== 1. AI 시그널 분석 ===")
        analyzer = SignalAnalyzer()
        
        analysis_result = analyzer.analyze_video_subtitle(
            channel_url, 
            video_data, 
            sample_subtitle
        )
        
        if analysis_result:
            print(f"[SUCCESS] AI 분석 완료!")
            print(f"원본 분석 결과:")
            if isinstance(analysis_result, dict):
                for key, value in analysis_result.items():
                    if key == 'signals' and isinstance(value, list):
                        print(f"  {key}: {len(value)}개 시그널")
                        for i, signal in enumerate(value):
                            print(f"    {i+1}. {signal}")
                    else:
                        print(f"  {key}: {value}")
            else:
                print(f"  {analysis_result}")
            
            # 3. 데이터베이스 형식 변환
            print(f"\n=== 2. 데이터베이스 형식 변환 ===")
            test_video_uuid = str(uuid.uuid4())
            signals = analyzer.convert_to_database_format(
                analysis_result, 
                test_video_uuid
            )
            
            print(f"변환된 시그널 수: {len(signals)}")
            for signal in signals:
                print(f"- {signal['stock_symbol']}: {signal['signal_type']} (신뢰도: {signal['confidence']})")
                print(f"  근거: {signal['reasoning'][:100]}...")
                print(f"  타임스탬프: {signal['timestamp_start']}초")
            
            # 4. DB 연결 테스트 (실제 INSERT는 하지 않음)
            print(f"\n=== 3. DB 연결 테스트 ===")
            try:
                db_inserter = DatabaseInserter()
                print("[SUCCESS] DB 연결 성공!")
                
                # 채널 정보 테스트 (실제로는 하지 않음)
                print("DB 설정:")
                print(f"  Supabase URL: {db_inserter.base_url}")
                print(f"  Headers: API Key 설정됨")
                
            except Exception as e:
                print(f"[ERROR] DB 연결 실패: {e}")
            
            return True, signals
            
        else:
            print("[ERROR] AI 분석 실패")
            return False, []
            
    except Exception as e:
        print(f"[ERROR] 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False, []

if __name__ == "__main__":
    success, signals = test_ai_pipeline()
    
    print(f"\n=== 파이프라인 테스트 결과 ===")
    print(f"상태: {'성공' if success else '실패'}")
    if signals:
        print(f"추출된 시그널: {len(signals)}개")
        print("\n요약:")
        for signal in signals:
            print(f"  • {signal['stock_symbol']}: {signal['signal_type']}")
    else:
        print("추출된 시그널 없음")