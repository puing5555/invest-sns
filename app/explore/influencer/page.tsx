'use client';
import { useState, useEffect } from 'react';
import Link from 'next/link';
import { influencers } from '@/data/influencerData';
import { getLatestInfluencerSignals } from '@/lib/supabase';
import { speakerToSlug } from '@/lib/speakerSlugs';
import SignalCard from '@/components/SignalCard';
import SignalDetailModal from '@/components/SignalDetailModal';

// V9 기준 한글 시그널 타입 색상
const V9_SIGNAL_COLORS: Record<string, string> = {
  '매수': 'bg-green-600 text-white',
  '긍정': 'bg-blue-600 text-white',
  '중립': 'bg-gray-500 text-white',
  '경계': 'bg-yellow-600 text-white',
  '매도': 'bg-red-800 text-white'
};

const CRYPTO_TICKERS = new Set(['CC', 'BTC', 'ETH', 'XRP', 'SOL', 'DOGE', 'ADA', 'DOT', 'AVAX', 'MATIC', 'LINK', 'UNI', '비트코인', '이더리움', '리플']);

function classifySignal(signal: { stock: string; ticker?: string | null }): 'kr' | 'us' | 'crypto' {
  const t = signal.ticker || '';
  const s = signal.stock || '';
  if (CRYPTO_TICKERS.has(t) || CRYPTO_TICKERS.has(s) || s.includes('비트코인') || s.includes('이더리움') || s.includes('크립토') || s.includes('코인')) return 'crypto';
  if (/^\d+$/.test(t)) return 'kr';
  // Korean name heuristic: contains hangul
  if (/[가-힣]/.test(s) && !t) return 'kr';
  if (/^[A-Z]{1,5}$/.test(t)) return 'us';
  // Default: if stock name is Korean → kr
  if (/[가-힣]/.test(s)) return 'kr';
  return 'us';
}

const STOCK_CODE_MAP: Record<string, string> = {
  '삼성전자': '005930', 'SK하이닉스': '000660', '현대차': '005380',
  '네이버': '035420', 'NAVER': '035420', 'LG화학': '051910',
  '에코프로': '086520', '한국가스공사': '009540', '퓨처켐': '399720',
  '현대건설': '000720', '신세계': '004170', 'POSCO홀딩스': '005490',
};

export default function InfluencerPage() {
  const [activeTab, setActiveTab] = useState('latest');
  const [searchQuery, setSearchQuery] = useState('');
  const [dbSignals, setDbSignals] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedSignal, setSelectedSignal] = useState<any>(null);
  const [categoryFilter, setCategoryFilter] = useState<Set<string>>(new Set(['kr', 'us', 'crypto']));

  // DB에서 시그널 로드
  useEffect(() => {
    const loadSignals = async () => {
      try {
        const signals = await getLatestInfluencerSignals(100); // 전부 가져오기
        const transformed = signals.map((s: any) => ({
          id: s.id,
          stock: s.stock,
          signal_type: s.signal,
          speaker: s.speakers?.name || s.influencer_videos?.influencer_channels?.channel_name || 'Unknown',
          channelName: s.influencer_videos?.influencer_channels?.channel_name || '',
          content_snippet: s.key_quote || `${s.stock} ${s.signal}`,
          key_quote: s.key_quote,
          video_published_at: s.influencer_videos?.published_at || s.created_at,
          confidence: s.confidence,
          reasoning: s.reasoning,
          videoSummary: s.influencer_videos?.video_summary,
          videoUrl: s.influencer_videos?.video_id ? `https://youtube.com/watch?v=${s.influencer_videos.video_id}` : '#',
          videoTitle: s.influencer_videos?.title,
          ticker: s.ticker || null,
        }));
        setDbSignals(transformed);
      } catch (e) {
        console.error('Failed to load signals:', e);
      } finally {
        setLoading(false);
      }
    };
    loadSignals();
  }, []);

  // 로컬 데이터 fallback (DB 비어있을 때)
  const localSignals = influencers.flatMap(influencer =>
    influencer.recentCalls.slice(0, 3).map(call => ({
      id: `${influencer.id}-${call.stock}`,
      stock: call.stock,
      signal_type: call.direction,
      speaker: influencer.name,
      channelName: influencer.name,
      content_snippet: `${call.stock} ${call.direction} 추천`,
      key_quote: null,
      video_published_at: call.date,
      confidence: null,
      reasoning: null,
      videoUrl: '#',
      videoTitle: null,
    }))
  );

  const allSignals = dbSignals.length > 0 ? dbSignals : localSignals;

  // 종목별 그룹
  const stockGroups = allSignals.reduce((groups: any[], signal) => {
    const existing = groups.find(g => g.stock === signal.stock);
    if (existing) {
      existing.signals.push(signal);
      existing.signal_count++;
    } else {
      groups.push({
        stock: signal.stock,
        ticker: signal.ticker || STOCK_CODE_MAP[signal.stock] || null,
        signal_count: 1,
        latest_signal: signal.signal_type,
        latest_date: signal.video_published_at,
        signals: [signal]
      });
    }
    return groups;
  }, []).sort((a, b) => b.signal_count - a.signal_count);

  const getSignalColor = (signalType: string) => {
    return V9_SIGNAL_COLORS[signalType] || 'bg-gray-500 text-white';
  };

  const formatDate = (dateStr: string) => {
    if (!dateStr) return '';
    const date = new Date(dateStr);
    const now = new Date();
    const diffHours = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60));
    if (diffHours < 24) return `${diffHours}시간 전`;
    const diffDays = Math.floor(diffHours / 24);
    if (diffDays < 30) return `${diffDays}일 전`;
    return date.toLocaleDateString('ko-KR', { month: 'short', day: 'numeric' });
  };

  const toggleCategory = (cat: string) => {
    setCategoryFilter(prev => {
      const next = new Set(prev);
      if (next.has(cat)) next.delete(cat); else next.add(cat);
      return next;
    });
  };

  const filteredSignals = allSignals.filter(signal => {
    if (categoryFilter.size > 0 && !categoryFilter.has(classifySignal(signal))) return false;
    return searchQuery === '' ||
      signal.stock.toLowerCase().includes(searchQuery.toLowerCase()) ||
      signal.speaker.toLowerCase().includes(searchQuery.toLowerCase());
  }).sort((a, b) => (b.video_published_at || '').localeCompare(a.video_published_at || ''));

  const filteredInfluencers = influencers.filter(influencer =>
    searchQuery === '' ||
    influencer.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const filteredStockGroups = stockGroups.filter(group =>
    searchQuery === '' ||
    group.stock.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="bg-[#f8f9fa] min-h-screen">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <h1 className="text-xl font-bold text-gray-900">📈 인플루언서 시그널</h1>
            <div className="flex items-center space-x-4">
              <div className="relative">
                <input
                  type="text"
                  placeholder="종목명 또는 인플루언서 검색..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-64 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                />
              </div>
            </div>
          </div>

          {/* Tabs */}
          <div className="flex space-x-8 -mb-px">
            {[
              { id: 'latest', label: '🔥 최신 시그널', count: allSignals.length },
              { id: 'influencers', label: '👥 인플루언서', count: influencers.length },
              { id: 'stocks', label: '📊 종목별', count: stockGroups.length }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`pb-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                {tab.label} <span className="text-xs bg-gray-100 px-2 py-1 rounded-full ml-1">{tab.count}</span>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'latest' && (
          <div className="space-y-4">
            <div className="text-sm text-gray-600 mb-3">
              총 {filteredSignals.length}개 시그널 {loading && '(로딩 중...)'}
            </div>
            <div className="flex gap-2 mb-4">
              {([['kr', '🇰🇷 한국주식'], ['us', '🇺🇸 미국주식'], ['crypto', '₿ 크립토']] as const).map(([key, label]) => (
                <button
                  key={key}
                  onClick={() => toggleCategory(key)}
                  className={`px-3 py-1.5 rounded-full text-xs font-medium border transition-colors ${
                    categoryFilter.has(key)
                      ? 'bg-[#3182f6] text-white border-[#3182f6]'
                      : 'bg-white text-gray-500 border-gray-300 hover:border-gray-400'
                  }`}
                >
                  {label}
                </button>
              ))}
            </div>
            {filteredSignals.map((signal) => (
              <SignalCard
                key={signal.id}
                signal={signal.signal_type}
                stock={signal.stock}
                speaker={signal.speaker}
                channelName={signal.channelName}
                confidence={signal.confidence}
                keyQuote={signal.key_quote}
                reasoning={signal.reasoning}
                videoTitle={signal.videoTitle}
                date={formatDate(signal.video_published_at)}
                videoUrl={signal.videoUrl}
                onClick={() => setSelectedSignal({
                  date: signal.video_published_at,
                  influencer: signal.speaker,
                  signal: signal.signal_type,
                  quote: signal.key_quote || '',
                  videoUrl: signal.videoUrl || '#',
                  analysis_reasoning: signal.videoSummary || signal.reasoning,
                  videoTitle: signal.videoTitle,
                  channelName: signal.channelName,
                  ticker: signal.ticker || STOCK_CODE_MAP[signal.stock] || null,
                })}
              />
            ))}
          </div>
        )}

        {activeTab === 'influencers' && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {(() => {
              // DB 시그널에서 발언자별 카운트 + 최신 시그널 + 채널 추출
              const speakerMap = new Map<string, { count: number; channels: Set<string>; latestSignal: string; latestDate: string; stockCounts: Map<string, number> }>();
              allSignals.forEach(s => {
                const existing = speakerMap.get(s.speaker);
                if (existing) {
                  existing.count++;
                  if (s.channelName) existing.channels.add(s.channelName);
                  if (s.stock) existing.stockCounts.set(s.stock, (existing.stockCounts.get(s.stock) || 0) + 1);
                  if (s.video_published_at > existing.latestDate) {
                    existing.latestSignal = s.signal_type;
                    existing.latestDate = s.video_published_at;
                  }
                } else {
                  const channels = new Set<string>();
                  if (s.channelName) channels.add(s.channelName);
                  const stockCounts = new Map<string, number>();
                  if (s.stock) stockCounts.set(s.stock, 1);
                  speakerMap.set(s.speaker, {
                    count: 1,
                    channels,
                    latestSignal: s.signal_type,
                    latestDate: s.video_published_at || '',
                    stockCounts,
                  });
                }
              });
              const speakers = Array.from(speakerMap.entries())
                .map(([name, data]) => ({
                  name,
                  ...data,
                  channelList: Array.from(data.channels),
                  topStocks: Array.from(data.stockCounts.entries())
                    .sort((a, b) => b[1] - a[1])
                    .slice(0, 3)
                    .map(([stock]) => stock),
                }))
                .filter(s => searchQuery === '' || s.name.toLowerCase().includes(searchQuery.toLowerCase()))
                .sort((a, b) => b.count - a.count);

              return speakers.map((speaker) => {
                const speakerId = speakerToSlug(speaker.name);
                return (
                  <Link key={speaker.name} href={`/profile/influencer/${speakerId}`}>
                    <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100 hover:shadow-lg transition-all cursor-pointer">
                      <div className="flex items-center space-x-4 mb-4">
                        <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white font-bold text-lg">
                          {speaker.name.charAt(0)}
                        </div>
                        <div>
                          <h3 className="font-bold text-gray-900">{speaker.name}</h3>
                        </div>
                      </div>
                      <div className="flex items-center justify-between mb-3">
                        <div className="text-center">
                          <div className="text-2xl font-bold text-[#3182f6]">{speaker.count}</div>
                          <div className="text-xs text-gray-500">시그널 수</div>
                        </div>
                      </div>
                      {speaker.topStocks.length > 0 && (
                        <div className="text-xs text-gray-400 truncate">
                          {speaker.topStocks.join(' · ')}
                        </div>
                      )}
                    </div>
                  </Link>
                );
              });
            })()}
          </div>
        )}

        {activeTab === 'stocks' && (
          <div className="space-y-4">
            <div className="text-sm text-gray-600 mb-4">
              총 {filteredStockGroups.length}개 종목
            </div>
            {filteredStockGroups.map((group) => {
              const speakers = [...new Set(group.signals.map((s: any) => s.speaker))];
              const speakerText = speakers.length <= 2
                ? speakers.join(', ')
                : `${speakers.slice(0, 2).join(', ')} 외 ${speakers.length - 2}명`;
              const stockUrl = group.ticker ? `/stock/${group.ticker}?tab=influencer` : null;

              const cardContent = (
                <div className={`bg-white rounded-xl p-5 shadow-sm border border-gray-100 ${stockUrl ? 'cursor-pointer hover:shadow-lg hover:border-[#3182f6]/30 transition-all' : ''}`}>
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center space-x-3">
                      <h3 className={`font-bold text-lg ${stockUrl ? 'text-[#3182f6]' : 'text-gray-900'}`}>{group.stock}</h3>
                      <div className={`px-2 py-1 rounded text-xs font-medium ${getSignalColor(group.latest_signal)}`}>
                        최신: {group.latest_signal}
                      </div>
                    </div>
                    <span className="text-sm text-gray-500">{group.signal_count}개 시그널</span>
                  </div>
                  <div className="text-sm text-gray-600 mb-3">
                    👤 {speakerText}
                  </div>
                  {(() => {
                    const latestQuote = group.signals.find((s: any) => s.key_quote);
                    return latestQuote ? (
                      <p className="text-sm text-gray-500 italic line-clamp-2">
                        &ldquo;{latestQuote.key_quote}&rdquo;
                        <span className="not-italic text-gray-400 ml-1">— {latestQuote.speaker}</span>
                      </p>
                    ) : null;
                  })()}
                </div>
              );

              return stockUrl ? (
                <Link key={group.stock} href={stockUrl}>{cardContent}</Link>
              ) : (
                <div key={group.stock}>{cardContent}</div>
              );
            })}
          </div>
        )}
      </div>

      <SignalDetailModal signal={selectedSignal} onClose={() => setSelectedSignal(null)} />
    </div>
  );
}
