'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { getLatestInfluencerSignals } from '@/lib/supabase';
import { speakerToSlug } from '@/lib/speakerSlugs';
import FeedCard from '@/components/FeedCard';
import SignalCard from '@/components/SignalCard';
import SignalDetailModal from '@/components/SignalDetailModal';

// 관심종목 칩 데이터
const stockChips = [
  { name: '전체', code: '', change: '', isPositive: true },
  { name: '삼성전자', code: '005930', change: '+0.8%', isPositive: true },
  { name: '현대차', code: '005380', change: '+2.1%', isPositive: true },
  { name: '카카오', code: '035720', change: '-1.2%', isPositive: false },
  { name: 'SK하이닉스', code: '000660', change: '+1.5%', isPositive: true },
  { name: 'LG에너지', code: '373220', change: '+0.5%', isPositive: true },
  { name: 'NAVER', code: '035420', change: '-0.3%', isPositive: false },
];

interface FeedItem {
  id: string;
  type: 'influencer' | 'analyst' | 'disclosure' | 'news' | 'insider' | 'report' | 'calendar' | 'earnings';
  icon: string;
  categoryName: string;
  stockName: string;
  stockCode: string;
  title: string;
  subtitle?: string;
  time: string;
  date: string;
  timestamp: number;
  source: string;
  signal?: string;
  keyQuote?: string;
  reasoning?: string;
  confidence?: string;
  channelName?: string;
  videoTitle?: string;
  videoUrl?: string;
  detailLink?: string;
}

// ---- 더미 데이터 제거됨 (실제 데이터 연동 후 교체 예정) ----
const dummyAnalystReports: any[] = [];
const dummyDisclosures: any[] = [];
const dummyNews: any[] = [];
const dummyInsider: any[] = [];
const dummyReports: any[] = [];
const dummyCalendar: any[] = [];
const dummyEarnings: any[] = [];

// ---- 유틸리티 ----

const getTimeAgo = (dateStr?: string) => {
  if (!dateStr) return '';
  const diff = Date.now() - new Date(dateStr).getTime();
  const m = Math.floor(diff / 60000);
  const hr = Math.floor(diff / 3600000);
  const d = Math.floor(diff / 86400000);
  if (d > 0) return `${d}일 전`;
  if (hr > 0) return `${hr}시간 전`;
  if (m > 0) return `${m}분 전`;
  return '방금 전';
};

const fmtDate = (dateStr?: string) => {
  if (!dateStr) return '';
  return new Date(dateStr).toLocaleDateString('ko-KR', { year: 'numeric', month: 'short', day: 'numeric' });
};

export default function MyStocksPage() {
  const [selectedChip, setSelectedChip] = useState('전체');
  const [selectedSignal, setSelectedSignal] = useState<any>(null);
  const router = useRouter();
  const [feedItems, setFeedItems] = useState<FeedItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      const allItems: FeedItem[] = [];

      // 1. 인플루언서 시그널 (DB 실제)
      try {
        const signals = await getLatestInfluencerSignals(50);
        signals.forEach((s: any, i: number) => {
          const ch = s.influencer_videos?.influencer_channels?.channel_name || '';
          const speaker = s.speakers?.name || ch;
          const pub = s.influencer_videos?.published_at || s.created_at;
          const vid = s.influencer_videos?.video_id;
          allItems.push({
            id: `inf_${s.id || i}`, type: 'influencer', icon: '', categoryName: '인플루언서',
            stockName: s.stock || '알 수 없는 종목', stockCode: s.ticker || '',
            title: `${speaker} → ${s.stock} ${s.signal}`,
            subtitle: s.key_quote || '', time: getTimeAgo(pub), date: fmtDate(pub),
            timestamp: new Date(pub || 0).getTime(), source: speaker,
            signal: s.signal, keyQuote: s.key_quote, reasoning: s.reasoning,
            confidence: s.confidence, channelName: ch,
            videoTitle: s.influencer_videos?.title,
            videoUrl: vid ? `https://youtube.com/watch?v=${vid}` : undefined,
            detailLink: s.ticker ? `/stock/${s.ticker}?tab=influencer` : undefined,
          });
        });
      } catch (e) { console.error(e); }

      // 2. 애널리스트
      dummyAnalystReports.forEach(r => {
        allItems.push({
          id: r.id, type: 'analyst', icon: '📊', categoryName: '애널리스트',
          stockName: r.stockName, stockCode: r.stockCode,
          title: `${r.firm} → ${r.stockName} 목표가 ${r.targetPrice}`,
          subtitle: r.summary, time: getTimeAgo(r.publishedAt), date: fmtDate(r.publishedAt),
          timestamp: new Date(r.publishedAt).getTime(), source: `${r.firm} ${r.analyst}`,
          signal: r.rating, detailLink: `/stock/${r.stockCode}?tab=analyst`,
        });
      });

      // 3. 공시
      dummyDisclosures.forEach(d => {
        allItems.push({
          id: d.id, type: 'disclosure', icon: '📋', categoryName: '공시',
          stockName: d.stockName, stockCode: d.stockCode,
          title: `[${d.grade}등급] ${d.stockName} ${d.title}`,
          time: getTimeAgo(d.publishedAt), date: fmtDate(d.publishedAt),
          timestamp: new Date(d.publishedAt).getTime(), source: 'DART',
          detailLink: `/stock/${d.stockCode}?tab=disclosure`,
        });
      });

      // 4. 뉴스
      dummyNews.forEach(n => {
        allItems.push({
          id: n.id, type: 'news', icon: '📰', categoryName: '뉴스',
          stockName: n.stockName, stockCode: n.stockCode,
          title: `${n.stockName} — ${n.title}`,
          time: getTimeAgo(n.publishedAt), date: fmtDate(n.publishedAt),
          timestamp: new Date(n.publishedAt).getTime(), source: n.source,
          detailLink: `/stock/${n.stockCode}?tab=feed`,
        });
      });

      // 5. 임원매매
      dummyInsider.forEach(ins => {
        allItems.push({
          id: ins.id, type: 'insider', icon: '👔', categoryName: '임원매매',
          stockName: ins.stockName, stockCode: ins.stockCode,
          title: `${ins.exec} ${ins.action} ${ins.shares}`,
          subtitle: ins.stockName, time: getTimeAgo(ins.publishedAt), date: fmtDate(ins.publishedAt),
          timestamp: new Date(ins.publishedAt).getTime(), source: ins.exec,
          detailLink: `/stock/${ins.stockCode}?tab=insider`,
        });
      });

      // 6. 리포트
      dummyReports.forEach(r => {
        allItems.push({
          id: r.id, type: 'report', icon: '📄', categoryName: '리포트',
          stockName: r.stockName, stockCode: r.stockCode,
          title: `${r.firm} — ${r.title}`,
          time: getTimeAgo(r.publishedAt), date: fmtDate(r.publishedAt),
          timestamp: new Date(r.publishedAt).getTime(), source: r.firm,
          signal: r.rating, detailLink: `/stock/${r.stockCode}?tab=reports`,
        });
      });

      // 7. 일정
      dummyCalendar.forEach(c => {
        allItems.push({
          id: c.id, type: 'calendar', icon: '📅', categoryName: '일정',
          stockName: c.stockName, stockCode: c.stockCode,
          title: `${c.stockName} ${c.title}`,
          subtitle: c.date, time: getTimeAgo(c.publishedAt), date: fmtDate(c.publishedAt),
          timestamp: new Date(c.publishedAt).getTime(), source: '캘린더',
          detailLink: `/stock/${c.stockCode}?tab=calendar`,
        });
      });

      // 8. 실적
      dummyEarnings.forEach(e => {
        allItems.push({
          id: e.id, type: 'earnings', icon: e.beat ? '📈' : '📉', categoryName: '실적',
          stockName: e.stockName, stockCode: e.stockCode,
          title: `${e.stockName} ${e.title}`,
          time: getTimeAgo(e.publishedAt), date: fmtDate(e.publishedAt),
          timestamp: new Date(e.publishedAt).getTime(), source: '실적',
          detailLink: `/stock/${e.stockCode}?tab=earnings`,
        });
      });

      allItems.sort((a, b) => b.timestamp - a.timestamp);
      setFeedItems(allItems);
      setLoading(false);
    };
    load();
  }, []);

  const handleChipClick = (chip: typeof stockChips[0]) => {
    if (chip.name === '전체') setSelectedChip('전체');
    else if (chip.code) router.push(`/stock/${chip.code}`);
  };

  const handleFeedItemClick = (item: FeedItem) => {
    if (item.detailLink) {
      router.push(item.detailLink);
    } else if (item.type === 'influencer') {
      setSelectedSignal({
        date: item.date, influencer: item.source, signal: item.signal || '중립',
        quote: item.keyQuote || '', videoUrl: item.videoUrl || '#',
        analysis_reasoning: item.reasoning, videoTitle: item.videoTitle,
        channelName: item.channelName, ticker: item.stockCode,
      });
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
        <p className="text-sm text-[#8b95a1] mt-2">관심 종목의 통합 피드</p>
      </div>

      {/* 관심종목 칩 */}
      <div className="bg-white border-b border-[#e8e8e8] px-4 py-4">
        <div className="flex gap-2 overflow-x-auto scrollbar-hide pb-1">
          {stockChips.map((chip, i) => (
            <button key={i} onClick={() => handleChipClick(chip)}
              className={`flex-shrink-0 px-4 py-2.5 rounded-full text-sm font-medium transition-colors ${
                selectedChip === chip.name ? 'bg-[#3182f6] text-white' : 'bg-[#f8f9fa] text-[#191f28] hover:bg-[#e9ecef]'
              }`}>
              <div className="flex items-center gap-1">
                <span>{chip.name}</span>
                {chip.change && (
                  <span className={`text-xs font-medium ${selectedChip === chip.name ? 'text-white/90' : chip.isPositive ? 'text-[#f44336]' : 'text-[#3182f6]'}`}>
                    {chip.change}
                  </span>
                )}
                {chip.name !== '전체' && <span className="text-xs text-gray-400 ml-1">→</span>}
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* 통합 피드 */}
      <div className="px-4 py-4">
        {loading ? (
          <div className="p-8 text-center text-[#8b95a1]">통합 피드를 불러오는 중...</div>
        ) : feedItems.length > 0 ? (
          <div className="space-y-3">
            {feedItems.map((item) =>
              item.type === 'influencer' ? (
                <SignalCard
                  key={item.id}
                  signal={item.signal || '중립'}
                  stock={item.stockName}
                  speaker={item.source}
                  channelName={item.channelName}
                  confidence={item.confidence}
                  keyQuote={item.keyQuote}
                  videoTitle={item.videoTitle}
                  date={item.date}
                  videoUrl={item.videoUrl}
                  onClick={() => handleFeedItemClick(item)}
                />
              ) : (
                <FeedCard
                  key={item.id}
                  icon={item.icon}
                  categoryName={item.categoryName}
                  title={item.title}
                  date={item.time}
                  signal={item.signal}
                  keyQuote={item.subtitle}
                  onClick={() => handleFeedItemClick(item)}
                />
              )
            )}
          </div>
        ) : (
          <div className="p-8 text-center">
            <div className="text-4xl mb-4">📱</div>
            <div className="text-lg font-medium text-[#191f28] mb-2">아직 업데이트가 없습니다</div>
          </div>
        )}
      </div>

      <SignalDetailModal signal={selectedSignal} onClose={() => setSelectedSignal(null)} />
    </div>
  );
}
