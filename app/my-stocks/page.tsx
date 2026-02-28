'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { getLatestInfluencerSignals } from '@/lib/supabase';
import FeedCard from '@/components/FeedCard';

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

// 통합 피드 아이템 타입
interface FeedItem {
  id: string;
  type: 'influencer' | 'analyst' | 'disclosure' | 'news';
  icon: string;
  categoryName: string;
  stockName: string;
  stockCode: string;
  title: string;
  subtitle?: string;
  time: string;
  date: string;
  timestamp: number; // 정렬용
  source: string;
  signal?: string;
  keyQuote?: string;
  reasoning?: string;
  profileLink?: string;
  detailLink?: string;
}

// 더미 애널리스트 리포트 데이터
const dummyAnalystReports = [
  {
    id: 'analyst_1',
    stockName: '삼성전자',
    stockCode: '005930',
    firm: '한국투자증권',
    analyst: '김선우',
    rating: 'BUY',
    targetPrice: '85,000원',
    summary: '3분기 실적 서프라이즈, HBM 수요 증가',
    publishedAt: new Date(Date.now() - 5 * 60 * 60 * 1000).toISOString(), // 5시간 전
  },
  {
    id: 'analyst_2',
    stockName: '현대차',
    stockCode: '005380',
    firm: '미래에셋증권',
    analyst: '박자동차',
    rating: 'BUY',
    targetPrice: '220,000원',
    summary: '전기차 판매 증가, 인도법인 호조',
    publishedAt: new Date(Date.now() - 3 * 60 * 60 * 1000).toISOString(), // 3시간 전
  },
  {
    id: 'analyst_3',
    stockName: 'SK하이닉스',
    stockCode: '000660',
    firm: 'KB증권',
    analyst: '이메모리',
    rating: 'BUY',
    targetPrice: '190,000원',
    summary: 'AI 반도체 수요 지속, D램 가격 회복',
    publishedAt: new Date(Date.now() - 1 * 60 * 60 * 1000).toISOString(), // 1시간 전
  }
];

// 더미 공시 데이터
const dummyDisclosures = [
  {
    id: 'disclosure_1',
    stockName: '삼성전자',
    stockCode: '005930',
    title: '자사주 500만주 취득 결정',
    grade: 'A',
    amount: '3조원',
    publishedAt: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(), // 4시간 전
  },
  {
    id: 'disclosure_2',
    stockName: '카카오',
    stockCode: '035720',
    title: '3분기 실적 공시',
    grade: 'A',
    amount: '매출 1.8조원',
    publishedAt: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(), // 2시간 전
  }
];

// 더미 뉴스 데이터
const dummyNews = [
  {
    id: 'news_1',
    stockName: 'LG에너지',
    stockCode: '373220',
    title: 'GM과 배터리 공급계약 연장 협의',
    source: '서울경제',
    publishedAt: new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString(), // 6시간 전
  },
  {
    id: 'news_2',
    stockName: 'NAVER',
    stockCode: '035420',
    title: 'AI 클로바X 글로벌 확장 계획 발표',
    source: '매일경제',
    publishedAt: new Date(Date.now() - 30 * 60 * 1000).toISOString(), // 30분 전
  }
];

export default function MyStocksPage() {
  const [selectedChip, setSelectedChip] = useState('전체');
  const router = useRouter();
  const [feedItems, setFeedItems] = useState<FeedItem[]>([]);
  const [loading, setLoading] = useState(true);

  // 통합 피드 데이터 로드
  useEffect(() => {
    const loadIntegratedFeed = async () => {
      try {
        setLoading(true);
        console.log('Loading integrated feed...');
        
        // 1. 인플루언서 시그널 가져오기
        const influencerSignals = await getLatestInfluencerSignals(50);
        
        // 2. 모든 데이터 소스를 통합 피드 아이템으로 변환
        const allItems: FeedItem[] = [];
        
        // 인플루언서 시그널 변환
        influencerSignals.forEach((signal, index) => {
          const channelName = signal.influencer_videos?.influencer_channels?.channel_name || 
                            signal.influencer_videos?.influencer_channels?.channel_handle || 
                            '알 수 없는 채널';
          const speakerName = signal.speakers?.name || channelName;
          const publishedAt = signal.influencer_videos?.published_at || signal.created_at;
          
          allItems.push({
            id: `influencer_${signal.id || index}`,
            type: 'influencer',
            icon: getSignalIcon(signal.signal),
            categoryName: '인플루언서',
            stockName: signal.stock || '알 수 없는 종목',
            stockCode: signal.ticker || '',
            title: `${speakerName} → ${signal.stock} ${signal.signal}`,
            subtitle: signal.key_quote || '',
            time: getTimeAgo(publishedAt),
            date: formatDate(publishedAt),
            timestamp: new Date(publishedAt || 0).getTime(),
            source: speakerName,
            signal: signal.signal,
            keyQuote: signal.key_quote,
            reasoning: signal.reasoning,
            profileLink: `/profile/${getInfluencerSlug(channelName)}`,
            detailLink: `/stock/${signal.ticker}?tab=influencer`
          });
        });
        
        // 애널리스트 리포트 변환
        dummyAnalystReports.forEach((report) => {
          allItems.push({
            id: report.id,
            type: 'analyst',
            icon: '📊',
            categoryName: '애널리스트',
            stockName: report.stockName,
            stockCode: report.stockCode,
            title: `${report.firm} ${report.analyst} → ${report.stockName} 목표가 ${report.targetPrice}`,
            subtitle: report.summary,
            time: getTimeAgo(report.publishedAt),
            date: formatDate(report.publishedAt),
            timestamp: new Date(report.publishedAt).getTime(),
            source: `${report.firm} ${report.analyst}`,
            signal: report.rating,
            detailLink: `/stock/${report.stockCode}?tab=analyst`
          });
        });
        
        // 공시 변환
        dummyDisclosures.forEach((disclosure) => {
          allItems.push({
            id: disclosure.id,
            type: 'disclosure',
            icon: '📋',
            categoryName: '공시',
            stockName: disclosure.stockName,
            stockCode: disclosure.stockCode,
            title: `${disclosure.stockName} ${disclosure.title} (${disclosure.grade}등급)`,
            subtitle: disclosure.amount,
            time: getTimeAgo(disclosure.publishedAt),
            date: formatDate(disclosure.publishedAt),
            timestamp: new Date(disclosure.publishedAt).getTime(),
            source: 'DART',
            detailLink: `/stock/${disclosure.stockCode}?tab=disclosure`
          });
        });
        
        // 뉴스 변환
        dummyNews.forEach((news) => {
          allItems.push({
            id: news.id,
            type: 'news',
            icon: '📢',
            categoryName: '뉴스',
            stockName: news.stockName,
            stockCode: news.stockCode,
            title: news.title,
            subtitle: '',
            time: getTimeAgo(news.publishedAt),
            date: formatDate(news.publishedAt),
            timestamp: new Date(news.publishedAt).getTime(),
            source: news.source,
            detailLink: `/stock/${news.stockCode}?tab=feed`
          });
        });
        
        // 시간순 정렬 (최신순)
        allItems.sort((a, b) => b.timestamp - a.timestamp);
        
        console.log('Integrated feed loaded:', allItems.length, 'items');
        setFeedItems(allItems);
      } catch (error) {
        console.error('Error loading integrated feed:', error);
        setFeedItems([]);
      } finally {
        setLoading(false);
      }
    };

    loadIntegratedFeed();
  }, []);

  // 유틸리티 함수들
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

  const getInfluencerSlug = (channelName: string) => {
    if (channelName.includes('슈카') || channelName.includes('syuka')) return 'syuka';
    if (channelName.includes('삼프로') || channelName.includes('3pro')) return '3protv';
    if (channelName.includes('코린이') || channelName.includes('korini')) return 'korini_papa';
    return 'unknown';
  };

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

  // 종목 칩 클릭 핸들러
  const handleChipClick = (chip: typeof stockChips[0]) => {
    if (chip.name === '전체') {
      setSelectedChip('전체');
    } else if (chip.code) {
      // 종목 상세 페이지로 이동
      console.log('Navigating to stock page:', chip.code);
      router.push(`/stock/${chip.code}`);
    }
  };

  // 피드 아이템 클릭 핸들러
  const handleFeedItemClick = (item: FeedItem) => {
    if (item.detailLink) {
      router.push(item.detailLink);
    }
  };

  // 소스 클릭 핸들러 (프로필 페이지로 이동)
  const handleSourceClick = (item: FeedItem, e: React.MouseEvent) => {
    e.stopPropagation();
    
    if (item.profileLink) {
      router.push(item.profileLink);
    }
  };

  return (
    <div className="min-h-screen bg-[#f4f4f4]">
      {/* Header */}
      <div className="bg-white border-b border-[#e8e8e8] px-4 py-4">
        <div className="flex items-center justify-between">
          <h1 className="text-xl font-bold text-[#191f28]">⭐ 내 종목</h1>
          <div className="text-sm text-[#8b95a1]">
            {loading ? '로딩 중...' : `${feedItems.length}개 업데이트`}
          </div>
        </div>
        <p className="text-sm text-[#8b95a1] mt-2">
          관심 종목의 실시간 통합 피드입니다. 종목을 클릭하면 상세 페이지로 이동합니다.
        </p>
      </div>

      {/* 관심종목 칩 */}
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

      {/* 통합 피드 리스트 */}
      <div className="px-4 py-4">
        <div>
          {loading ? (
            <div className="p-8 text-center">
              <div className="text-lg text-[#8b95a1]">통합 피드를 불러오는 중...</div>
            </div>
          ) : feedItems.length > 0 ? (
            <div className="space-y-4">
              {feedItems.map((item) => (
                <FeedCard
                  key={item.id}
                  icon={item.icon}
                  categoryName={item.categoryName}
                  title={item.title}
                  date={item.date}
                  signal={item.signal}
                  onClick={() => handleFeedItemClick(item)}
                />
              ))}
            </div>
          ) : (
            <div className="p-8 text-center">
              <div className="text-4xl mb-4">📱</div>
              <div className="text-lg font-medium text-[#191f28] mb-2">
                아직 업데이트가 없습니다
              </div>
              <div className="text-sm text-[#8b95a1]">
                관심 종목의 새로운 소식이 업데이트될 때까지 기다려주세요
              </div>
            </div>
          )}
        </div>

        {/* 하단 설명 */}
        {feedItems.length > 0 && (
          <div className="mt-4 text-center">
            <p className="text-sm text-[#8b95a1]">
              항목을 클릭하면 해당 종목의 상세 페이지로 이동합니다
            </p>
          </div>
        )}
      </div>
    </div>
  );
}