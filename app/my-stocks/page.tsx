'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { getLatestInfluencerSignals } from '@/lib/supabase';

// 관심종목 칩 데이터
const stockChips = [
  { name: '전체', code: '', change: '', isPositive: true, isActive: true },
  { name: '삼성전자', code: '005930', change: '+0.8%', isPositive: true, isActive: false },
  { name: '현대차', code: '005380', change: '+2.1%', isPositive: true, isActive: false },
  { name: '카카오', code: '035720', change: '-1.2%', isPositive: false, isActive: false },
  { name: 'SK하이닉스', code: '000660', change: '+1.5%', isPositive: true, isActive: false },
  { name: 'LG에너지', code: '373220', change: '+0.5%', isPositive: true, isActive: false },
  { name: 'NAVER', code: '035420', change: '-0.3%', isPositive: false, isActive: false },
];

// 타임라인 이벤트 타입
interface TimelineEvent {
  id: number;
  type: 'disclosure' | 'influencer' | 'report' | 'insider' | 'earnings' | 'news';
  icon: string;
  categoryName: string;
  stockName: string;
  stockCode: string;
  title: string;
  time: string;
  date: string;
  source?: string;
  channelName?: string;
  signal?: string;
  keyQuote?: string;
  reasoning?: string;
  influencerId?: string;
  originalData?: any;
}

export default function MyStocksPage() {
  const [selectedChip, setSelectedChip] = useState('전체'); // '전체'만 활성 상태 관리
  const router = useRouter();
  const [timelineEvents, setTimelineEvents] = useState<TimelineEvent[]>([]);
  const [loading, setLoading] = useState(true);

  // 데이터 로드
  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        console.log('Loading influencer signals...');
        const signals = await getLatestInfluencerSignals(50); // 더 많은 데이터 로드
        console.log('Loaded signals:', signals.length);
        
        // 인플루언서 시그널을 타임라인 이벤트로 변환
        const events = signals.map((signal, index) => {
          const channelName = signal.influencer_videos?.influencer_channels?.channel_name || 
                            signal.influencer_videos?.influencer_channels?.channel_handle || 
                            '알 수 없는 채널';
          const speakerName = signal.speakers?.name || channelName;
          const publishedAt = signal.influencer_videos?.published_at || signal.timestamp;
          const videoTitle = signal.influencer_videos?.title || '';

          return {
            id: signal.id || index,
            type: 'influencer' as const,
            icon: getSignalIcon(signal.signal),
            categoryName: '인플루언서',
            stockName: signal.stock || '알 수 없는 종목',
            stockCode: signal.ticker || '',
            title: `${speakerName} ${signal.signal} 신호`,
            time: getTimeAgo(publishedAt),
            date: formatDate(publishedAt),
            source: speakerName,
            channelName: channelName,
            signal: signal.signal,
            keyQuote: signal.key_quote || '핵심 발언 없음',
            reasoning: signal.reasoning || '분석 내용 없음',
            influencerId: getInfluencerSlug(channelName),
            originalData: signal
          };
        });

        console.log('Converted events:', events.length);
        setTimelineEvents(events);
      } catch (error) {
        console.error('Error loading data:', error);
        setTimelineEvents([]);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, []);

  // 신호별 아이콘 반환
  const getSignalIcon = (signal: string) => {
    switch (signal) {
      case '매수': return '🔵';
      case '긍정': return '🟢';
      case '중립': return '🟡';
      case '경계': return '🟠';
      case '매도': return '🔴';
      default: return '⚪';
    }
  };

  // 인플루언서 슬러그 생성
  const getInfluencerSlug = (channelName: string) => {
    if (channelName.includes('슈카') || channelName.includes('syuka')) return 'syuka';
    if (channelName.includes('삼프로') || channelName.includes('3pro')) return '3protv';
    if (channelName.includes('코린이') || channelName.includes('korini')) return 'korini_papa';
    if (channelName.includes('달란트')) return 'talent';
    if (channelName.includes('부읽남')) return 'booknam';
    if (channelName.includes('이효석')) return 'hyoseok';
    return 'unknown';
  };

  // 시간 전 표시 함수
  const getTimeAgo = (dateString: string | undefined) => {
    if (!dateString) return '시간 미상';
    
    try {
      const date = new Date(dateString);
      const now = new Date();
      const diff = now.getTime() - date.getTime();
      
      const minutes = Math.floor(diff / (1000 * 60));
      const hours = Math.floor(diff / (1000 * 60 * 60));
      const days = Math.floor(diff / (1000 * 60 * 60 * 24));
      
      if (days > 0) return `${days}일 전`;
      if (hours > 0) return `${hours}시간 전`;
      if (minutes > 0) return `${minutes}분 전`;
      return '방금 전';
    } catch (error) {
      return '시간 미상';
    }
  };

  // 날짜 포맷팅
  const formatDate = (dateString: string | undefined) => {
    if (!dateString) return '날짜 미상';
    
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString('ko-KR', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      });
    } catch (error) {
      return '날짜 미상';
    }
  };

  // 종목 칩 클릭 핸들러 - 종목 상세 페이지로 이동
  const handleChipClick = (chip: typeof stockChips[0]) => {
    if (chip.name === '전체') {
      setSelectedChip('전체'); // 전체 탭만 로컬 상태 유지
    } else if (chip.code) {
      // 종목 상세 페이지로 이동 (9개 탭 구조)
      router.push(`/stock/${chip.code}`);
    }
  };

  // 시그널 카드 클릭 핸들러 - 종목 상세 페이지 인플루언서 탭으로 이동
  const handleEventClick = (event: TimelineEvent) => {
    if (event.stockCode) {
      router.push(`/stock/${event.stockCode}?tab=influencer`);
    }
  };

  // 인플루언서 이름 클릭 핸들러 - 프로필 페이지로 이동
  const handleInfluencerClick = (event: TimelineEvent, e: React.MouseEvent) => {
    e.stopPropagation(); // 카드 클릭 이벤트 중단
    
    if (event.influencerId && event.influencerId !== 'unknown') {
      router.push(`/profile/${event.influencerId}`);
    }
  };

  // 신호별 색상 반환
  const getSignalColor = (signal: string) => {
    switch (signal) {
      case '매수': return 'text-blue-600 bg-blue-50';
      case '긍정': return 'text-green-600 bg-green-50';
      case '중립': return 'text-yellow-600 bg-yellow-50';
      case '경계': return 'text-orange-600 bg-orange-50';
      case '매도': return 'text-red-600 bg-red-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  // 전체 탭에서만 모든 이벤트 표시 (필터링 없음)
  const displayedEvents = timelineEvents;

  return (
    <div className="min-h-screen bg-[#f4f4f4]">
      {/* Header */}
      <div className="bg-white border-b border-[#e8e8e8] px-4 py-4">
        <div className="flex items-center justify-between">
          <h1 className="text-xl font-bold text-[#191f28]">⭐ 내 종목</h1>
          <div className="text-sm text-[#8b95a1]">
            {loading ? '로딩 중...' : `${displayedEvents.length}개 시그널`}
          </div>
        </div>
        <p className="text-sm text-[#8b95a1] mt-2">
          관심 종목의 최신 시그널을 확인하세요. 종목을 클릭하면 상세 페이지로 이동합니다.
        </p>
      </div>

      {/* 관심종목 칩 필터 */}
      <div className="bg-white border-b border-[#e8e8e8] px-4 py-4">
        <div className="flex gap-2 overflow-x-auto scrollbar-hide pb-1">
          {stockChips.map((chip, index) => (
            <button
              key={index}
              onClick={() => handleChipClick(chip)}
              className={`flex-shrink-0 px-4 py-2.5 rounded-full text-sm font-medium transition-colors ${
                selectedChip === chip.name
                  ? 'bg-[#3182f6] text-white'
                  : 'bg-[#f8f9fa] text-[#191f28] hover:bg-[#e9ecef]'
              }`}
            >
              <div className="flex items-center gap-1">
                <span>{chip.name}</span>
                {chip.change && (
                  <span className={`text-xs font-medium ${
                    selectedChip === chip.name 
                      ? 'text-white/90' 
                      : chip.isPositive 
                        ? 'text-[#f44336]' 
                        : 'text-[#3182f6]'
                  }`}>
                    {chip.change}
                  </span>
                )}
                {chip.name !== '전체' && (
                  <span className="text-xs text-gray-400 ml-1">→</span>
                )}
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* 타임라인 리스트 */}
      <div className="px-4 py-4">
        <div className="bg-white rounded-lg border border-[#e8e8e8] overflow-hidden">
          {loading ? (
            <div className="p-8 text-center">
              <div className="text-lg text-[#8b95a1]">데이터를 불러오는 중...</div>
            </div>
          ) : displayedEvents.length > 0 ? (
            <div className="divide-y divide-[#f0f0f0]">
              {displayedEvents.map((event) => (
                <div
                  key={event.id}
                  onClick={() => handleEventClick(event)}
                  className="px-4 py-4 hover:bg-[#f8f9fa] cursor-pointer transition-colors"
                >
                  <div className="flex items-start gap-3">
                    {/* 이벤트 아이콘 */}
                    <div className="w-10 h-10 rounded-full bg-[#f8f9fa] flex items-center justify-center text-lg flex-shrink-0">
                      {event.icon}
                    </div>
                    
                    {/* 이벤트 내용 */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-2">
                        <span className="text-sm font-medium text-[#8b95a1] bg-[#f2f4f6] px-2 py-0.5 rounded">
                          {event.categoryName}
                        </span>
                        <span className="text-sm font-bold text-[#191f28]">
                          {event.stockName}
                        </span>
                        {event.signal && (
                          <span className={`text-xs font-medium px-2 py-0.5 rounded ${getSignalColor(event.signal)}`}>
                            {event.signal}
                          </span>
                        )}
                      </div>

                      <h3 className="text-[15px] font-medium text-[#191f28] leading-[1.4] mb-2">
                        {event.title}
                      </h3>

                      {/* 상세 정보 표시 */}
                      {event.keyQuote && event.keyQuote !== '핵심 발언 없음' && (
                        <div className="mb-2">
                          <div className="text-xs text-[#8b95a1] mb-1">핵심 발언:</div>
                          <div className="text-sm text-[#191f28] bg-[#f8f9fa] px-2 py-1 rounded text-ellipsis line-clamp-2">
                            "{event.keyQuote}"
                          </div>
                        </div>
                      )}

                      {event.reasoning && event.reasoning !== '분석 내용 없음' && (
                        <div className="mb-2">
                          <div className="text-xs text-[#8b95a1] mb-1">분석:</div>
                          <div className="text-sm text-[#191f28] line-clamp-2">
                            {event.reasoning}
                          </div>
                        </div>
                      )}

                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <span className="text-sm text-[#8b95a1]">
                            {event.date} • {event.time}
                          </span>
                          {event.source && (
                            <>
                              <span className="text-xs text-[#8b95a1]">•</span>
                              <button
                                onClick={(e) => handleInfluencerClick(event, e)}
                                className="text-sm text-[#3182f6] hover:underline"
                              >
                                {event.source}
                              </button>
                            </>
                          )}
                        </div>
                        <div className="text-[#8b95a1] text-sm">
                          →
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="p-8 text-center">
              <div className="text-4xl mb-4">📋</div>
              <div className="text-lg font-medium text-[#191f28] mb-2">
                아직 시그널이 없습니다
              </div>
              <div className="text-sm text-[#8b95a1]">
                관심 종목의 새로운 시그널이 업데이트될 때까지 기다려주세요
              </div>
            </div>
          )}
        </div>

        {/* 하단 설명 */}
        {displayedEvents.length > 0 && (
          <div className="mt-4 text-center">
            <p className="text-sm text-[#8b95a1]">
              시그널을 클릭하면 종목 상세 페이지로, 인플루언서 이름을 클릭하면 프로필로 이동합니다
            </p>
          </div>
        )}
      </div>
    </div>
  );
}