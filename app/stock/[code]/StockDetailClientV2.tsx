'use client';

import { useState, useEffect } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { getStockSignals, getSignalColor } from '@/lib/supabase';
import StockChart from '@/components/StockChart';
import { influencers } from '@/data/influencerData';

interface StockDetailClientProps {
  code: string;
}

// 종목별 타임라인 이벤트
interface StockTimelineEvent {
  id: number;
  type: string;
  icon: string;
  categoryName: string;
  title: string;
  time: string;
  tab: string;
}

const getStockTimeline = (code: string): StockTimelineEvent[] => {
  const timelines: { [key: string]: StockTimelineEvent[] } = {
    '005930': [
      { id: 1, type: 'disclosure', icon: '🔵', categoryName: '공시', title: 'A등급 공시 - 3분기 실적 컨센서스 상회', time: '3분 전', tab: 'disclosure' },
      { id: 2, type: 'influencer', icon: '🟢', categoryName: '인플루언서', title: '슈카월드 긍정 신호', time: '1시간 전', tab: 'influencer' },
      { id: 3, type: 'report', icon: '📊', categoryName: '리포트', title: '한국투자증권 목표가 상향', time: '2시간 전', tab: 'reports' },
      { id: 4, type: 'insider', icon: '👔', categoryName: '임원매매', title: '이재용 사장 매수 5만주', time: '3시간 전', tab: 'insider' },
      { id: 5, type: 'earnings', icon: '📈', categoryName: '실적', title: '3분기 영업이익 컨센서스 상회', time: '5시간 전', tab: 'earnings' },
      { id: 6, type: 'influencer', icon: '🟢', categoryName: '인플루언서', title: '코린이아빠 매수 신호', time: '8시간 전', tab: 'influencer' },
      { id: 7, type: 'disclosure', icon: '🔵', categoryName: '공시', title: '자사주 매입 결정', time: '1일 전', tab: 'disclosure' },
    ],
    '005380': [
      { id: 1, type: 'report', icon: '📊', categoryName: '리포트', title: '한국투자증권 목표가 상향', time: '2시간 전', tab: 'reports' },
      { id: 2, type: 'earnings', icon: '📈', categoryName: '실적', title: '3분기 영업이익 컨센서스 상회', time: '5시간 전', tab: 'earnings' },
      { id: 3, type: 'disclosure', icon: '🔵', categoryName: '공시', title: '전기차 신모델 출시 공시', time: '1일 전', tab: 'disclosure' },
    ],
  };
  return timelines[code] || [
    { id: 1, type: 'disclosure', icon: '🔵', categoryName: '공시', title: '최근 공시 없음', time: '-', tab: 'disclosure' },
  ];
};

// 탭 정의
const tabs = [
  { id: 'feed', label: '피드', icon: '📱' },
  { id: 'influencer', label: '인플루언서', icon: '📈' },
  { id: 'analyst', label: '애널리스트', icon: '📊' },
  { id: 'disclosure', label: '공시', icon: '📋' },
  { id: 'earnings', label: '실적', icon: '📈' },
  { id: 'reports', label: '리포트', icon: '📄' },
  { id: 'insider', label: '임원매매', icon: '💼' },
  { id: 'calendar', label: '일정', icon: '📅' },
  { id: 'memo', label: '메모', icon: '📝' },
];

// 더미 종목 데이터
const getStockData = (code: string) => {
  const stockMap: { [key: string]: any } = {
    '005930': { name: '삼성전자', price: 68500, change: 1200, changePercent: 1.78 },
    '000660': { name: 'SK하이닉스', price: 178000, change: -2100, changePercent: -1.16 },
    '035420': { name: 'NAVER', price: 185500, change: 3200, changePercent: 1.76 },
    '051910': { name: 'LG화학', price: 412000, change: -5500, changePercent: -1.32 },
    '005380': { name: '현대차', price: 221000, change: 4500, changePercent: 2.08 },
  };

  return stockMap[code] || { name: `종목 ${code}`, price: 50000, change: 0, changePercent: 0 };
};

export default function StockDetailClient({ code }: StockDetailClientProps) {
  const [activeTab, setActiveTab] = useState('feed');
  const [isWatched, setIsWatched] = useState(false);
  const [showComments, setShowComments] = useState<{ [key: number]: boolean }>({});
  const [commentInputs, setCommentInputs] = useState<{ [key: number]: string }>({});
  const searchParams = useSearchParams();
  const router = useRouter();
  const stockData = getStockData(code);
  const timeline = getStockTimeline(code);

  // URL 쿼리 파라미터에서 탭 설정
  useEffect(() => {
    const tabParam = searchParams.get('tab');
    if (tabParam && tabs.some(tab => tab.id === tabParam)) {
      setActiveTab(tabParam);
    }
  }, [searchParams]);

  // 해당 종목의 시그널 가져오기
  const getStockSignalsLocal = (code: string, name: string) => {
    const stockMapping: { [key: string]: string[] } = {
      '005930': ['삼성전자', '삼성'],
      '000660': ['SK하이닉스', '하이닉스'],
      '035420': ['네이버', 'NAVER'],
      '051910': ['LG화학'],
      '005380': ['현대차', '현대자동차'],
      '005490': ['POSCO홀딩스', '포스코'],
      'BTC': ['비트코인', 'Bitcoin'],
      'ETH': ['이더리움', 'Ethereum']
    };

    const possibleNames = stockMapping[code] || [name];
    const signals: any[] = [];
    
    influencers.forEach(influencer => {
      influencer.recentCalls.forEach(call => {
        const isMatch = possibleNames.some(stockName => 
          call.stock.includes(stockName) || stockName.includes(call.stock)
        );
        
        if (isMatch) {
          signals.push({
            id: `${influencer.id}-${call.stock}`,
            stock: call.stock,
            signal_type: call.direction,
            speaker: influencer.name,
            content_snippet: `${call.stock} ${call.direction} 추천`,
            date: call.date,
            video_published_at: call.date,
            accuracy_rate: influencer.accuracy,
            return_rate: call.returnRate,
            status: call.status
          });
        }
      });
    });
    
    return signals;
  };

  const stockSignals = getStockSignalsLocal(code, stockData.name);

  const renderTabContent = () => {
    switch (activeTab) {
      case 'feed':
        return (
          <div className="space-y-6">
            {/* 주가 차트 */}
            <StockChart 
              stockCode={code}
              stockName={stockData.name}
              signals={stockSignals}
            />
            
            {/* 타임라인 이벤트 */}
            <div className="space-y-4">
            {timeline.map((event) => (
              <div key={event.id} className="bg-white rounded-lg border border-[#e8e8e8] overflow-hidden">
                <div
                  onClick={() => setActiveTab(event.tab)}
                  className="px-4 py-4 hover:bg-[#f8f9fa] cursor-pointer transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-[#f8f9fa] flex items-center justify-center text-lg flex-shrink-0">
                      {event.icon}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-sm font-medium text-[#8b95a1] bg-[#f2f4f6] px-2 py-0.5 rounded">
                          {event.categoryName}
                        </span>
                      </div>
                      <h3 className="text-[15px] font-medium text-[#191f28] leading-[1.4] mb-1">
                        {event.title}
                      </h3>
                      <span className="text-sm text-[#8b95a1]">{event.time}</span>
                    </div>
                    <div className="text-[#8b95a1] text-sm">→</div>
                  </div>
                </div>
                
                {/* Comment Section */}
                <div className="border-t border-[#f0f0f0] px-4 py-3">
                  <div className="flex items-center gap-2 mb-2">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        setShowComments(prev => ({
                          ...prev,
                          [event.id]: !prev[event.id]
                        }));
                      }}
                      className="text-xs text-[#8b95a1] hover:text-[#191f28] transition-colors"
                    >
                      💬 댓글 {Math.floor(Math.random() * 10) + 1}개
                    </button>
                    <span className="text-xs text-[#8b95a1]">•</span>
                    <button className="text-xs text-[#8b95a1] hover:text-[#191f28] transition-colors">
                      ❤️ 좋아요 {Math.floor(Math.random() * 50) + 5}개
                    </button>
                  </div>
                  
                  {/* Comment Input */}
                  <div className="flex gap-2">
                    <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center text-xs flex-shrink-0">
                      👤
                    </div>
                    <input
                      type="text"
                      placeholder="댓글을 입력하세요..."
                      value={commentInputs[event.id] || ''}
                      onChange={(e) => {
                        setCommentInputs(prev => ({
                          ...prev,
                          [event.id]: e.target.value
                        }));
                      }}
                      onClick={(e) => e.stopPropagation()}
                      className="flex-1 text-sm border border-[#e8e8e8] rounded-full px-3 py-1 focus:outline-none focus:ring-1 focus:ring-[#3182f6] focus:border-transparent"
                    />
                    <button 
                      onClick={(e) => {
                        e.stopPropagation();
                        if (commentInputs[event.id]?.trim()) {
                          // Here you would handle comment submission
                          setCommentInputs(prev => ({
                            ...prev,
                            [event.id]: ''
                          }));
                        }
                      }}
                      className="text-xs px-3 py-1 bg-[#3182f6] text-white rounded-full hover:bg-[#2171e5] transition-colors"
                    >
                      등록
                    </button>
                  </div>
                  
                  {/* Comments List */}
                  {showComments[event.id] && (
                    <div className="mt-3 space-y-2 pl-8">
                      <div className="flex gap-2 text-sm">
                        <div className="w-5 h-5 bg-green-100 rounded-full flex items-center justify-center text-xs flex-shrink-0">
                          🐶
                        </div>
                        <div>
                          <span className="font-medium text-[#191f28]">투자왕</span>
                          <span className="text-[#8b95a1] ml-2">좋은 정보네요!</span>
                        </div>
                      </div>
                      <div className="flex gap-2 text-sm">
                        <div className="w-5 h-5 bg-yellow-100 rounded-full flex items-center justify-center text-xs flex-shrink-0">
                          🎯
                        </div>
                        <div>
                          <span className="font-medium text-[#191f28]">주식초보</span>
                          <span className="text-[#8b95a1] ml-2">매수 타이밍 맞나요?</span>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ))}
            </div>
          </div>
        );

      case 'influencer':
        return <InfluencerTab code={code} />;

      case 'analyst':
        return <AnalystTab code={code} />;

      case 'disclosure':
        return (
          <div className="space-y-4">
            <div className="bg-white rounded-lg border border-[#e8e8e8] p-6">
              <h4 className="font-bold text-[#191f28] mb-4">최근 공시</h4>
              <div className="space-y-3">
                <div className="p-3 border-l-4 border-blue-500 bg-blue-50">
                  <div className="font-medium text-blue-800">3분기 실적 발표</div>
                  <div className="text-sm text-blue-600">2시간 전</div>
                </div>
                <div className="p-3 border-l-4 border-green-500 bg-green-50">
                  <div className="font-medium text-green-800">자사주 매입 결정</div>
                  <div className="text-sm text-green-600">1일 전</div>
                </div>
              </div>
            </div>
          </div>
        );

      case 'earnings':
        return (
          <div className="text-center py-12">
            <div className="text-4xl mb-4">📊</div>
            <h3 className="text-lg font-bold text-[#191f28] mb-2">실적 분석</h3>
            <p className="text-[#8b95a1]">상세 실적 분석을 준비중입니다</p>
          </div>
        );

      case 'reports':
        return (
          <div className="text-center py-12">
            <div className="text-4xl mb-4">📄</div>
            <h3 className="text-lg font-bold text-[#191f28] mb-2">리서치 리포트</h3>
            <p className="text-[#8b95a1]">증권사 리포트를 준비중입니다</p>
          </div>
        );

      case 'insider':
        return (
          <div className="space-y-4">
            <div className="bg-white rounded-lg border border-[#e8e8e8] p-6">
              <h4 className="font-bold text-[#191f28] mb-4">임원 매매 현황</h4>
              <div className="space-y-3">
                <div className="flex items-center justify-between p-3 bg-red-50 rounded-lg">
                  <div>
                    <div className="font-medium text-red-800">김○○ 전무 매도</div>
                    <div className="text-sm text-red-600">5억원 규모 • 3일 전</div>
                  </div>
                  <div className="text-red-600 font-bold">-1.2%</div>
                </div>
                <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
                  <div>
                    <div className="font-medium text-blue-800">박○○ 상무 매수</div>
                    <div className="text-sm text-blue-600">3억원 규모 • 1주 전</div>
                  </div>
                  <div className="text-blue-600 font-bold">+0.8%</div>
                </div>
              </div>
            </div>
          </div>
        );

      case 'calendar':
        return (
          <div className="text-center py-12">
            <div className="text-4xl mb-4">📅</div>
            <h3 className="text-lg font-bold text-[#191f28] mb-2">종목 일정</h3>
            <p className="text-[#8b95a1]">실적발표, 주주총회 등 일정을 준비중입니다</p>
          </div>
        );

      case 'memo':
        return (
          <div className="bg-white rounded-lg border border-[#e8e8e8] p-6">
            <h4 className="font-bold text-[#191f28] mb-4">내 메모</h4>
            <div className="space-y-4">
              <textarea
                placeholder="이 종목에 대한 메모를 작성해보세요..."
                className="w-full h-32 p-3 border border-[#e8e8e8] rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-[#3182f6] focus:border-transparent"
              />
              <div className="flex justify-end">
                <button className="px-4 py-2 bg-[#3182f6] text-white rounded-lg hover:bg-[#2171e5] transition-colors">
                  저장
                </button>
              </div>
            </div>
          </div>
        );

      default:
        return <div>준비중</div>;
    }
  };

  return (
    <div className="min-h-screen bg-[#f4f4f4]">
      {/* Stock Header */}
      <div className="bg-white border-b border-[#e8e8e8] px-4 py-6">
        <div>
          {/* 뒤로가기 버튼 */}
          <div className="mb-4">
            <button
              onClick={() => router.push('/my-stocks')}
              className="flex items-center gap-2 text-[#8b95a1] hover:text-[#191f28] transition-colors"
            >
              <span className="text-lg">←</span>
              <span className="text-sm">내 종목으로</span>
            </button>
          </div>

          <div className="flex justify-between items-start">
            <div>
              <h1 className="text-2xl font-bold text-[#191f28]">
                {stockData.name}
                <span className="text-lg text-[#8b95a1] font-normal ml-2">
                  {code}
                </span>
              </h1>
              <div className="flex items-center gap-4 mt-2">
                <span className="text-3xl font-bold text-[#191f28]">
                  {stockData.price.toLocaleString()}원
                </span>
                <span className={`text-lg font-medium ${
                  stockData.change >= 0 ? 'text-red-500' : 'text-blue-500'
                }`}>
                  {stockData.change >= 0 ? '+' : ''}{stockData.change.toLocaleString()}원
                  ({stockData.change >= 0 ? '+' : ''}{stockData.changePercent}%)
                </span>
              </div>
              
              {/* Coverage Stats */}
              <div className="flex items-center gap-4 mt-3 text-sm text-[#8b95a1]">
                <span>인플루언서 12명</span>
                <span>•</span>
                <span>애널리스트 8명</span>
                <span>•</span>
                <span>투자자 5명</span>
                <span>•</span>
                <span>팔로워 3,247명</span>
              </div>
            </div>
            
            {/* Watch Button */}
            <button
              onClick={() => setIsWatched(!isWatched)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                isWatched
                  ? 'bg-green-100 text-green-700 border border-green-200'
                  : 'bg-[#3182f6] text-white hover:bg-[#2171e5]'
              }`}
            >
              {isWatched ? '✓ 관심종목 등록됨' : '+ 관심종목 추가'}
            </button>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-white border-b border-[#e8e8e8]">
        <div className="px-4">
          <div className="flex overflow-x-auto scrollbar-hide">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex-shrink-0 flex items-center gap-2 px-4 py-3 text-sm font-medium transition-colors relative ${
                  activeTab === tab.id
                    ? 'text-[#3182f6]'
                    : 'text-[#8b95a1] hover:text-[#191f28]'
                }`}
              >
                {tab.label}
                {activeTab === tab.id && (
                  <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-[#3182f6]" />
                )}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="px-4 py-6">
        {renderTabContent()}
      </div>
    </div>
  );
}

// 인플루언서 탭 컴포넌트 (개선된 차트 + 모든 시그널 점 표시)
function InfluencerTab({ code }: { code: string }) {
  const [periodFilter, setPeriodFilter] = useState('전체');
  const [influencerFilter, setInfluencerFilter] = useState('전체');
  const [signalData, setSignalData] = useState<any[]>([]);
  const [influencerOptions, setInfluencerOptions] = useState([
    { name: '전체', count: null }
  ]);
  const [loading, setLoading] = useState(true);

  const periodOptions = ['1개월', '6개월', '1년', '3년', '전체'];

  // 데이터 로드
  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        
        const { getStockSignals } = await import('@/lib/supabase');
        const signals = await getStockSignals(code);
        
        // 데이터를 UI용 형태로 변환
        const transformedSignals = signals.map((signal: any) => {
          const publishedDate = signal.influencer_videos?.published_at 
            ? new Date(signal.influencer_videos.published_at)
            : new Date();
          
          const videoUrl = signal.influencer_videos?.video_id 
            ? `https://youtube.com/watch?v=${signal.influencer_videos.video_id}`
            : '#';

          const speakerName = signal.speakers?.name || '';
          const channelName = signal.influencer_videos?.influencer_channels?.channel_name || '';
          // 게스트면 "스피커 · 채널", 호스트(스피커==채널 or 스피커 없음)면 채널명만
          // 호스트: 채널명만. 게스트: 화자 이름만
          const isHost = !speakerName || !channelName || speakerName === channelName || channelName.includes(speakerName) || speakerName.includes(channelName);
          const influencerDisplay = isHost
            ? (channelName || speakerName || 'Unknown')
            : speakerName;

          return {
            date: publishedDate.toISOString().split('T')[0],
            influencer: influencerDisplay,
            signal: signal.signal,
            quote: signal.key_quote || '키 인용문이 없습니다.',
            return: 'N/A', // TODO: 수익률 계산
            videoUrl,
            price: 0, // TODO: 발언 시점 주가
            timestamp: signal.timestamp
          };
        });
        
        // published_at 우선 최신순 정렬
        transformedSignals.sort((a: any, b: any) => (b.date || '').localeCompare(a.date || ''));
        setSignalData(transformedSignals);
        
        // 인플루언서별 카운트 생성
        const influencerCounts = transformedSignals.reduce((acc: any, signal: any) => {
          acc[signal.influencer] = (acc[signal.influencer] || 0) + 1;
          return acc;
        }, {});
        
        const influencerOpts = [
          { name: '전체', count: null },
          ...Object.entries(influencerCounts).map(([name, count]) => ({
            name,
            count: count as number
          }))
        ];
        
        setInfluencerOptions(influencerOpts);
      } catch (error) {
        console.error('Error loading stock signals:', error);
        setSignalData([]);
      } finally {
        setLoading(false);
      }
    };

    if (code) {
      loadData();
    }
  }, [code]);

  const getLocalSignalColor = (signal: string) => {
    switch (signal) {
      case '매수':
      case 'BUY': return 'text-blue-600 bg-blue-100';
      case '긍정':
      case 'POSITIVE': return 'text-green-600 bg-green-100';
      case '중립':
      case 'NEUTRAL': return 'text-yellow-600 bg-yellow-100';
      case '부정':
      case 'CONCERN': return 'text-orange-600 bg-orange-100';
      case '매도':
      case 'SELL': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getSignalEmoji = (signal: string) => {
    switch (signal) {
      case '매수':
      case 'BUY': return '🔵';
      case '긍정':
      case 'POSITIVE': return '🟢';
      case '중립':
      case 'NEUTRAL': return '🟡';
      case '부정':
      case 'CONCERN': return '🟠';
      case '매도':
      case 'SELL': return '🔴';
      default: return '⚪';
    }
  };

  const getSignalPointColor = (signal: string) => {
    switch (signal) {
      case '매수':
      case 'BUY': return '#3B82F6'; // blue-500
      case '긍정':
      case 'POSITIVE': return '#10B981'; // green-500
      case '중립':
      case 'NEUTRAL': return '#F59E0B'; // yellow-500
      case '부정':
      case 'CONCERN': return '#F97316'; // orange-500
      case '매도':
      case 'SELL': return '#EF4444'; // red-500
      default: return '#6B7280'; // gray-500
    }
  };

  const getSignalText = (signal: string) => {
    return signal;
  };

  // 필터링된 데이터 계산
  const getFilteredSignals = () => {
    let filtered = [...signalData];
    
    // 인플루언서 필터
    if (influencerFilter !== '전체') {
      filtered = filtered.filter(signal => signal.influencer === influencerFilter);
    }
    
    // 기간 필터
    if (periodFilter !== '전체') {
      const now = new Date();
      let cutoffDate = new Date();
      
      switch (periodFilter) {
        case '1개월':
          cutoffDate.setMonth(now.getMonth() - 1);
          break;
        case '6개월':
          cutoffDate.setMonth(now.getMonth() - 6);
          break;
        case '1년':
          cutoffDate.setFullYear(now.getFullYear() - 1);
          break;
        case '3년':
          cutoffDate.setFullYear(now.getFullYear() - 3);
          break;
      }
      
      filtered = filtered.filter(signal => new Date(signal.date) >= cutoffDate);
    }
    
    return filtered;
  };

  const filteredSignals = getFilteredSignals();

  // 차트용 데이터 생성 (개선된 차트)
  const generateChartData = () => {
    const chartWidth = 400;
    const chartHeight = 200;
    const padding = 20;
    
    // 더미 주가 데이터 (실제 데이터로 교체 필요)
    const priceData = Array.from({ length: 30 }, (_, i) => ({
      x: (i / 29) * (chartWidth - 2 * padding) + padding,
      y: Math.sin(i * 0.2) * 30 + chartHeight / 2 + Math.random() * 20 - 10
    }));
    
    // 시그널 점들 (실제 데이터 기반)
    const signalPoints = filteredSignals.map((signal, index) => {
      const x = (index / Math.max(filteredSignals.length - 1, 1)) * (chartWidth - 2 * padding) + padding;
      const y = Math.random() * (chartHeight - 2 * padding) + padding;
      return {
        x,
        y,
        signal: signal.signal,
        influencer: signal.influencer,
        date: signal.date
      };
    });
    
    return { priceData, signalPoints };
  };

  const { priceData, signalPoints } = generateChartData();

  if (loading) {
    return (
      <div className="text-center py-8">
        <div className="text-lg text-[#8b95a1]">데이터를 불러오는 중...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* 필터 섹션 */}
      <div className="bg-white rounded-lg border border-[#e8e8e8] p-6">
        <div className="space-y-4">
          <div>
            <h4 className="font-medium text-[#191f28] mb-3">기간</h4>
            <div className="flex gap-2 flex-wrap">
              {periodOptions.map((period) => (
                <button
                  key={period}
                  onClick={() => setPeriodFilter(period)}
                  className={`px-3 py-1.5 rounded-full text-sm font-medium transition-colors ${
                    periodFilter === period
                      ? 'bg-[#3182f6] text-white'
                      : 'bg-[#f8f9fa] text-[#8b95a1] hover:bg-[#e9ecef]'
                  }`}
                >
                  {period}
                </button>
              ))}
            </div>
          </div>

          <div>
            <h4 className="font-medium text-[#191f28] mb-3">인플루언서</h4>
            <div className="flex gap-2 flex-wrap">
              {influencerOptions.map((option) => (
                <button
                  key={option.name}
                  onClick={() => setInfluencerFilter(option.name)}
                  className={`px-3 py-1.5 rounded-full text-sm font-medium transition-colors ${
                    influencerFilter === option.name
                      ? 'bg-[#3182f6] text-white'
                      : 'bg-[#f8f9fa] text-[#8b95a1] hover:bg-[#e9ecef]'
                  }`}
                >
                  {option.name}
                  {option.count && `(${option.count})`}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* 개선된 차트 영역 */}
      <div className="bg-white rounded-lg border border-[#e8e8e8] p-6">
        <h4 className="font-medium text-[#191f28] mb-4">주가 차트 & 인플루언서 신호 ({filteredSignals.length}개)</h4>
        <div className="relative h-80 bg-[#f8f9fa] rounded-lg overflow-hidden">
          <svg className="w-full h-full" viewBox="0 0 400 200">
            {/* 배경 격자 */}
            <defs>
              <pattern id="influencerGrid" width="40" height="20" patternUnits="userSpaceOnUse">
                <path d="M 40 0 L 0 0 0 20" fill="none" stroke="#e8e8e8" strokeWidth="1"/>
              </pattern>
            </defs>
            <rect width="100%" height="100%" fill="url(#influencerGrid)" />
            
            {/* 주가 라인 (더 부드러운 곡선) */}
            <path
              d={`M ${priceData.map(p => `${p.x} ${p.y}`).join(' L ')}`}
              fill="none"
              stroke="#3182f6"
              strokeWidth="2"
              opacity="0.8"
            />
            
            {/* 모든 시그널 점들 표시 */}
            {signalPoints.map((point, index) => (
              <g key={index}>
                <circle 
                  cx={point.x} 
                  cy={point.y} 
                  r="8" 
                  fill={getSignalPointColor(point.signal)} 
                  stroke="white" 
                  strokeWidth="2"
                  className="cursor-pointer"
                />
                {/* 호버 시 정보 표시 */}
                <title>
                  {point.influencer} - {getSignalText(point.signal)} ({point.date})
                </title>
              </g>
            ))}
            
            {/* Y축 라벨 */}
            <text x="10" y="20" className="text-xs fill-gray-600">높음</text>
            <text x="10" y="190" className="text-xs fill-gray-600">낮음</text>
          </svg>
          
          {/* 범례 (개선됨) */}
          <div className="absolute top-3 right-3 bg-white/90 backdrop-blur-sm rounded-lg p-4 text-xs">
            <div className="font-medium mb-2">시그널 타입</div>
            <div className="grid grid-cols-2 gap-1">
              <span className="flex items-center gap-1"><span className="w-2 h-2 bg-blue-500 rounded-full"></span>매수</span>
              <span className="flex items-center gap-1"><span className="w-2 h-2 bg-green-500 rounded-full"></span>긍정</span>
              <span className="flex items-center gap-1"><span className="w-2 h-2 bg-yellow-500 rounded-full"></span>중립</span>
              <span className="flex items-center gap-1"><span className="w-2 h-2 bg-orange-500 rounded-full"></span>부정</span>
              <span className="flex items-center gap-1"><span className="w-2 h-2 bg-red-500 rounded-full"></span>매도</span>
            </div>
            <div className="mt-2 text-gray-600">
              총 {filteredSignals.length}개 시그널
            </div>
          </div>
        </div>
      </div>

      {/* 신호 테이블 */}
      <div className="bg-white rounded-lg border border-[#e8e8e8] overflow-hidden">
        <div className="p-6 border-b border-[#e8e8e8]">
          <h4 className="font-medium text-[#191f28]">인플루언서 신호 이력</h4>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-[#f8f9fa]">
              <tr>
                <th className="px-4 py-3 text-left text-sm font-medium text-[#8b95a1]">날짜</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-[#8b95a1]">인플루언서</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-[#8b95a1]">신호</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-[#8b95a1]">핵심발언</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-[#8b95a1]">수익률</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-[#8b95a1]">영상링크</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#f0f0f0]">
              {filteredSignals.map((signal, index) => (
                <tr key={index} className="hover:bg-[#f8f9fa]">
                  <td className="px-4 py-4 text-sm text-[#191f28]">
                    {new Date(signal.date).toLocaleDateString('ko-KR', { 
                      month: 'short', 
                      day: 'numeric' 
                    })}
                  </td>
                  <td className="px-4 py-4 text-sm text-[#191f28] whitespace-nowrap">
                    {signal.influencer}
                  </td>
                  <td className="px-4 py-4">
                    <div className="flex items-center gap-2">
                      <span className="text-lg">{getSignalEmoji(signal.signal)}</span>
                      <span className={`px-2 py-1 rounded text-xs font-medium ${getLocalSignalColor(signal.signal)}`}>
                        {getSignalText(signal.signal)}
                      </span>
                    </div>
                  </td>
                  <td className="px-4 py-4 text-sm text-[#191f28] max-w-xs">
                    <div className="truncate" title={signal.quote}>{signal.quote}</div>
                  </td>
                  <td className="px-4 py-4 text-sm font-medium">
                    <span className="text-gray-500">
                      {signal.return}
                    </span>
                  </td>
                  <td className="px-4 py-4">
                    <a
                      href={signal.videoUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-[#3182f6] hover:text-[#2171e5] text-sm font-medium"
                    >
                      영상보기 →
                    </a>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

// 애널리스트 탭 컴포넌트 (차트 형태)
function AnalystTab({ code }: { code: string }) {
  const [periodFilter, setPeriodFilter] = useState('전체');
  const [analystFilter, setAnalystFilter] = useState('전체');
  
  const periodOptions = ['1개월', '6개월', '1년', '3년', '전체'];
  
  // 더미 애널리스트 데이터 (실제 환경에서는 DB에서 가져와야 함)
  const analystSignals = [
    {
      date: '2024-02-20',
      analyst: '김선우',
      firm: '한국투자증권',
      signal: '매수',
      targetPrice: '75,000원',
      quote: '메모리 업사이클 시작으로 실적 개선 기대',
      accuracy: '72%',
      previousPrice: '68,500원',
      upside: '+9.5%'
    },
    {
      date: '2024-02-18',
      analyst: '이미래',
      firm: '미래에셋증권',
      signal: '매수',
      targetPrice: '72,000원',
      quote: '3분기 실적 컨센서스 상회 전망',
      accuracy: '68%',
      previousPrice: '68,500원',
      upside: '+5.1%'
    },
    {
      date: '2024-02-15',
      analyst: '박기술',
      firm: 'NH투자증권',
      signal: '중립',
      targetPrice: '65,000원',
      quote: '단기 조정 후 상승 전망',
      accuracy: '65%',
      previousPrice: '68,500원',
      upside: '-5.1%'
    },
    {
      date: '2024-02-10',
      analyst: '정에너지',
      firm: '삼성증권',
      signal: '매수',
      targetPrice: '78,000원',
      quote: 'AI 반도체 수요 증가로 수혜',
      accuracy: '74%',
      previousPrice: '68,500원',
      upside: '+13.9%'
    },
    {
      date: '2024-02-05',
      analyst: '최금융',
      firm: 'KB증권',
      signal: '긍정',
      targetPrice: '70,000원',
      quote: 'HBM 점유율 확대 지속',
      accuracy: '69%',
      previousPrice: '68,500원',
      upside: '+2.2%'
    }
  ];

  const analystOptions = [
    { name: '전체', count: null },
    { name: '한국투자증권', count: 1 },
    { name: '미래에셋증권', count: 1 },
    { name: 'NH투자증권', count: 1 },
    { name: '삼성증권', count: 1 },
    { name: 'KB증권', count: 1 }
  ];

  const getSignalColor = (signal: string) => {
    switch (signal) {
      case '매수': return 'text-blue-600 bg-blue-100';
      case '긍정': return 'text-green-600 bg-green-100';
      case '중립': return 'text-yellow-600 bg-yellow-100';
      case '부정': return 'text-orange-600 bg-orange-100';
      case '매도': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getSignalEmoji = (signal: string) => {
    switch (signal) {
      case '매수': return '🔵';
      case '긍정': return '🟢';
      case '중립': return '🟡';
      case '부정': return '🟠';
      case '매도': return '🔴';
      default: return '⚪';
    }
  };

  const getTargetPriceColor = (firm: string) => {
    const colors: { [key: string]: string } = {
      '한국투자증권': '#3B82F6',
      '미래에셋증권': '#10B981',
      'NH투자증권': '#F59E0B',
      '삼성증권': '#EF4444',
      'KB증권': '#8B5CF6'
    };
    return colors[firm] || '#6B7280';
  };

  // 필터링된 데이터
  const filteredSignals = analystSignals.filter(signal => {
    if (analystFilter !== '전체' && !signal.firm.includes(analystFilter.replace('증권', ''))) {
      return false;
    }
    
    if (periodFilter !== '전체') {
      const now = new Date();
      let cutoffDate = new Date();
      
      switch (periodFilter) {
        case '1개월':
          cutoffDate.setMonth(now.getMonth() - 1);
          break;
        case '6개월':
          cutoffDate.setMonth(now.getMonth() - 6);
          break;
        case '1년':
          cutoffDate.setFullYear(now.getFullYear() - 1);
          break;
        case '3년':
          cutoffDate.setFullYear(now.getFullYear() - 3);
          break;
      }
      
      if (new Date(signal.date) < cutoffDate) {
        return false;
      }
    }
    
    return true;
  });

  // 평균 목표가 계산
  const avgTargetPrice = filteredSignals.reduce((sum, signal) => {
    return sum + parseInt(signal.targetPrice.replace(/[,원]/g, ''));
  }, 0) / filteredSignals.length;

  return (
    <div className="space-y-6">
      {/* 필터 섹션 */}
      <div className="bg-white rounded-lg border border-[#e8e8e8] p-6">
        <div className="space-y-4">
          <div>
            <h4 className="font-medium text-[#191f28] mb-3">기간</h4>
            <div className="flex gap-2 flex-wrap">
              {periodOptions.map((period) => (
                <button
                  key={period}
                  onClick={() => setPeriodFilter(period)}
                  className={`px-3 py-1.5 rounded-full text-sm font-medium transition-colors ${
                    periodFilter === period
                      ? 'bg-[#3182f6] text-white'
                      : 'bg-[#f8f9fa] text-[#8b95a1] hover:bg-[#e9ecef]'
                  }`}
                >
                  {period}
                </button>
              ))}
            </div>
          </div>

          <div>
            <h4 className="font-medium text-[#191f28] mb-3">증권사</h4>
            <div className="flex gap-2 flex-wrap">
              {analystOptions.map((option) => (
                <button
                  key={option.name}
                  onClick={() => setAnalystFilter(option.name)}
                  className={`px-3 py-1.5 rounded-full text-sm font-medium transition-colors ${
                    analystFilter === option.name
                      ? 'bg-[#3182f6] text-white'
                      : 'bg-[#f8f9fa] text-[#8b95a1] hover:bg-[#e9ecef]'
                  }`}
                >
                  {option.name}
                  {option.count && `(${option.count})`}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* 목표가 차트 영역 (개선됨) */}
      <div className="bg-white rounded-lg border border-[#e8e8e8] p-6">
        <h4 className="font-medium text-[#191f28] mb-4">목표가 추이 & 애널리스트 의견 ({filteredSignals.length}개)</h4>
        <div className="relative h-80 bg-[#f8f9fa] rounded-lg overflow-hidden">
          <svg className="w-full h-full" viewBox="0 0 400 200">
            {/* 배경 격자 */}
            <defs>
              <pattern id="analystGrid" width="40" height="20" patternUnits="userSpaceOnUse">
                <path d="M 40 0 L 0 0 0 20" fill="none" stroke="#e8e8e8" strokeWidth="1"/>
              </pattern>
            </defs>
            <rect width="100%" height="100%" fill="url(#analystGrid)" />
            
            {/* 현재 주가 라인 */}
            <line x1="0" y1="120" x2="400" y2="120" stroke="#666" strokeWidth="2" strokeDasharray="5,5" />
            <text x="10" y="115" className="text-xs fill-gray-600">현재가 68,500원</text>
            
            {/* 평균 목표가 라인 */}
            <line x1="0" y1="80" x2="400" y2="80" stroke="#10B981" strokeWidth="2" strokeDasharray="3,3" />
            <text x="10" y="75" className="text-xs fill-green-600">평균 목표가 {avgTargetPrice.toLocaleString()}원</text>
            
            {/* 목표가 트렌드 라인 */}
            <path
              d="M 50 100 L 120 85 L 200 75 L 280 80 L 350 70"
              fill="none"
              stroke="#10B981"
              strokeWidth="3"
            />
            
            {/* 애널리스트 목표가 점들 */}
            {filteredSignals.map((signal, index) => {
              const x = 50 + (index * 75); 
              const targetPriceNum = parseInt(signal.targetPrice.replace(/[,원]/g, ''));
              const y = 200 - (targetPriceNum / 80000) * 160; 
              
              return (
                <g key={index}>
                  <circle 
                    cx={x} 
                    cy={y} 
                    r="10" 
                    fill={getTargetPriceColor(signal.firm)} 
                    stroke="white" 
                    strokeWidth="2"
                    className="cursor-pointer"
                  />
                  <title>
                    {signal.firm} {signal.analyst} - {signal.targetPrice} ({signal.signal})
                  </title>
                </g>
              );
            })}
          </svg>
          
          {/* 범례 (개선됨) */}
          <div className="absolute top-3 right-3 bg-white/90 backdrop-blur-sm rounded-lg p-4 text-xs">
            <div className="font-medium mb-2">증권사별 목표가</div>
            <div className="space-y-1">
              {filteredSignals.map((signal, index) => (
                <div key={index} className="flex items-center gap-2">
                  <span 
                    className="w-3 h-3 rounded-full" 
                    style={{ backgroundColor: getTargetPriceColor(signal.firm) }}
                  ></span>
                  <span>{signal.firm.replace('증권', '')} {signal.targetPrice}</span>
                </div>
              ))}
            </div>
            <div className="mt-3 pt-2 border-t border-gray-200">
              <div className="font-medium text-green-600">
                평균: {avgTargetPrice.toLocaleString()}원
              </div>
              <div className="text-gray-600">
                상승여력: {((avgTargetPrice - 68500) / 68500 * 100).toFixed(1)}%
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 애널리스트 의견 테이블 */}
      <div className="bg-white rounded-lg border border-[#e8e8e8] overflow-hidden">
        <div className="p-6 border-b border-[#e8e8e8]">
          <h4 className="font-medium text-[#191f28]">애널리스트 의견 이력</h4>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-[#f8f9fa]">
              <tr>
                <th className="px-4 py-3 text-left text-sm font-medium text-[#8b95a1]">날짜</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-[#8b95a1]">애널리스트</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-[#8b95a1]">의견</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-[#8b95a1]">목표가</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-[#8b95a1]">상승여력</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-[#8b95a1]">핵심논거</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-[#8b95a1]">적중률</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#f0f0f0]">
              {filteredSignals.map((signal, index) => (
                <tr key={index} className="hover:bg-[#f8f9fa]">
                  <td className="px-4 py-4 text-sm text-[#191f28]">
                    {new Date(signal.date).toLocaleDateString('ko-KR', { 
                      month: 'short', 
                      day: 'numeric' 
                    })}
                  </td>
                  <td className="px-4 py-4 text-sm font-medium text-[#191f28]">
                    <div>{signal.analyst}</div>
                    <div className="text-xs text-[#8b95a1]">{signal.firm}</div>
                  </td>
                  <td className="px-4 py-4">
                    <div className="flex items-center gap-2">
                      <span className="text-lg">{getSignalEmoji(signal.signal)}</span>
                      <span className={`px-2 py-1 rounded text-xs font-medium ${getSignalColor(signal.signal)}`}>
                        {signal.signal}
                      </span>
                    </div>
                  </td>
                  <td className="px-4 py-4 text-sm font-bold text-[#191f28]">
                    {signal.targetPrice}
                  </td>
                  <td className="px-4 py-4 text-sm font-medium">
                    <span className={signal.upside.startsWith('+') ? 'text-red-600' : 'text-blue-600'}>
                      {signal.upside}
                    </span>
                  </td>
                  <td className="px-4 py-4 text-sm text-[#191f28] max-w-xs">
                    <div className="truncate" title={signal.quote}>{signal.quote}</div>
                  </td>
                  <td className="px-4 py-4 text-sm font-medium text-green-600">
                    {signal.accuracy}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}