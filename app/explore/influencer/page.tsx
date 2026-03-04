'use client';
import { useState, useEffect } from 'react';
import Link from 'next/link';
import { influencers } from '@/data/influencerData';
import { getLatestInfluencerSignals, getInfluencerSignalsSampled, getSignalVoteCounts } from '@/lib/supabase';
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

// 채널 프로필 이미지 (YouTube 썸네일)
const CHANNEL_THUMBNAILS: Record<string, string> = {
  '@3protv': 'https://yt3.googleusercontent.com/--qajlNgqpwDCjcupwfYwXsgXS3szfhMEEFGI1ouLTj4CKOtwGOyXGR7xl8-tzOGCDFt9umfqQ=s88-c-k-c0x00ffffff-no-rj',
  '@corinpapa1106': 'https://yt3.googleusercontent.com/-HGE7apiUHRw_vzmDlM__1kyxVOFXNhvRp-uhM-3UgkeC5otDLa72I36kErIOpBPMGFybQVdeA=s88-c-k-c0x00ffffff-no-rj',
  '@buiknam_tv': 'https://yt3.googleusercontent.com/YVgyZe175-BfqGiPUFccAuScDra7tjebtCUWknMRLPrmQb5u9_yqox8ZoLpauXAU-k4gnQTArw=s88-c-k-c0x00ffffff-no-rj',
  '@hyoseok_academy': 'https://yt3.googleusercontent.com/ytc/AIdro_md5qYQnpwKbDcxHTdMG2zhXe1GbATSYBGmdJiMuO1N2L6lIeC8v1Efuu-zcc-_ytvViw=s88-c-k-c0x00ffffff-no-rj',
  '@syukasworld': 'https://yt3.googleusercontent.com/ytc/AIdro_nMJ-JJFKw5B0TPk88VDQW9c7cBZwlM5krM_Uphz8HN4jQ=s88-c-k-c0x00ffffff-no-rj',
  '@dalant_invest': 'https://yt3.googleusercontent.com/ytc/AIdro_mIGlqIYYtCZsZjLU94fyeijqO7zN80pJGCEL9w-uNr2PTUIGNAmRqf5z40HG5jVFRm1w=s88-c-k-c0x00ffffff-no-rj',
};

const STOCK_CODE_MAP: Record<string, string> = {
  '삼성전자': '005930', 'SK하이닉스': '000660', '현대차': '005380',
  '네이버': '035420', 'NAVER': '035420', 'LG화학': '051910',
  '에코프로': '086520', '한국가스공사': '009540', '퓨처켐': '399720',
  '현대건설': '000720', '신세계': '004170', 'POSCO홀딩스': '005490',
  '효성중공업': '298040', '솔브레인': '357780', '삼성전기': '009150',
  'NC소프트': '036570', 'HD현대일렉트릭': '267260', '아이덴': '284620',
  '현대차그룹주': '005380',
};

export default function InfluencerPage() {
  const [activeTab, setActiveTab] = useState('latest');
  const [searchQuery, setSearchQuery] = useState('');
  const [dbSignals, setDbSignals] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedSignal, setSelectedSignal] = useState<any>(null);
  const [categoryFilter, setCategoryFilter] = useState<Set<string>>(new Set(['kr', 'us', 'crypto']));
  const [likeCounts, setLikeCounts] = useState<Record<string, number>>({});

  // DB에서 시그널 로드
  useEffect(() => {
    const loadSignals = async () => {
      try {
        const signals = await getLatestInfluencerSignals(1000); // 전체 시그널 최신순
        const transformed = signals.map((s: any) => ({
          id: s.id,
          stock: s.stock,
          signal_type: s.signal,
          speaker: s.speakers?.name || s.influencer_videos?.influencer_channels?.channel_name || 'Unknown',
          channelName: s.influencer_videos?.influencer_channels?.channel_name || '',
          channelHandle: s.influencer_videos?.influencer_channels?.channel_handle || '',
          content_snippet: s.key_quote || `${s.stock} ${s.signal}`,
          key_quote: s.key_quote,
          video_published_at: s.influencer_videos?.published_at || s.created_at,
          confidence: s.confidence,
          reasoning: s.reasoning,
          videoSummary: s.influencer_videos?.video_summary,
          videoUrl: s.influencer_videos?.video_id ? (() => {
            const base = `https://youtube.com/watch?v=${s.influencer_videos.video_id}`;
            const ts = s.timestamp;
            if (!ts) return base;
            const parts = ts.split(':').map(Number);
            let secs = 0;
            if (parts.length === 2) secs = parts[0] * 60 + parts[1];
            else if (parts.length === 3) secs = parts[0] * 3600 + parts[1] * 60 + parts[2];
            return secs > 0 ? `${base}&t=${secs}` : base;
          })() : '#',
          videoTitle: s.influencer_videos?.title,
          ticker: s.ticker || null,
        }));
        setDbSignals(transformed);

        // 좋아요 카운트 가져오기
        if (transformed.length > 0) {
          const signalIds = transformed.map((s: any) => s.id).filter(Boolean);
          if (signalIds.length > 0) {
            try {
              const counts = await getSignalVoteCounts(signalIds);
              setLikeCounts(counts);
            } catch (e) {
              console.error('Failed to load like counts:', e);
            }
          }
        }
      } catch (e) {
        console.error('Failed to load signals:', e);
      } finally {
        setLoading(false);
      }
    };
    loadSignals();
  }, []);

  // DB 데이터만 사용 (mock 데이터 제거)
  const allSignals = dbSignals;

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
              { id: 'latest', label: '🔥 최신 시그널', count: filteredSignals.length },
              { id: 'influencers', label: '👥 인플루언서', count: null },
              { id: 'stocks', label: '📊 종목별', count: null }
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
                {tab.label} {tab.count !== null && <span className="text-xs bg-gray-100 px-2 py-1 rounded-full ml-1">{tab.count}</span>}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* 카테고리 필터 - 전체 탭 공통 */}
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

        {activeTab === 'latest' && (
          <div className="space-y-4">
            <div className="text-sm text-gray-600 mb-3">
              총 {filteredSignals.length}개 시그널 {loading && '(로딩 중...)'}
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
                likeCount={likeCounts[signal.id] || 0}
                onClick={() => setSelectedSignal({
                  id: signal.id,
                  date: signal.video_published_at,
                  influencer: signal.speaker,
                  signal: signal.signal_type,
                  quote: signal.key_quote || '',
                  videoUrl: signal.videoUrl || '#',
                  analysis_reasoning: signal.videoSummary || signal.reasoning,
                  videoTitle: signal.videoTitle,
                  channelName: signal.channelName,
                  ticker: signal.ticker || STOCK_CODE_MAP[signal.stock] || null,
                  likeCount: likeCounts[signal.id] || 0,
                })}
              />
            ))}
          </div>
        )}

        {activeTab === 'influencers' && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {(() => {
              // 카테고리 필터 적용된 시그널로 발언자별 카운트
              const categoryFilteredSignals = allSignals.filter(s => categoryFilter.size === 0 || categoryFilter.has(classifySignal(s)));
              const speakerMap = new Map<string, { count: number; channels: Set<string>; channelHandle: string; latestSignal: string; latestDate: string; stockCounts: Map<string, number>; signalTypes: Map<string, number> }>();
              categoryFilteredSignals.forEach(s => {
                const existing = speakerMap.get(s.speaker);
                if (existing) {
                  existing.count++;
                  if (s.channelName) existing.channels.add(s.channelName);
                  // 자기 채널 핸들 우선 (채널명에 발언자 이름 포함 시)
                  if (s.channelHandle && (!existing.channelHandle || (s.channelName && s.channelName.includes(s.speaker.charAt(0))))) existing.channelHandle = s.channelHandle;
                  if (s.stock) existing.stockCounts.set(s.stock, (existing.stockCounts.get(s.stock) || 0) + 1);
                  if (s.signal_type) existing.signalTypes.set(s.signal_type, (existing.signalTypes.get(s.signal_type) || 0) + 1);
                  if (s.video_published_at > existing.latestDate) {
                    existing.latestSignal = s.signal_type;
                    existing.latestDate = s.video_published_at;
                  }
                } else {
                  const channels = new Set<string>();
                  if (s.channelName) channels.add(s.channelName);
                  const stockCounts = new Map<string, number>();
                  if (s.stock) stockCounts.set(s.stock, 1);
                  const signalTypes = new Map<string, number>();
                  if (s.signal_type) signalTypes.set(s.signal_type, 1);
                  speakerMap.set(s.speaker, {
                    count: 1,
                    channels,
                    channelHandle: s.channelHandle || '',
                    latestSignal: s.signal_type,
                    latestDate: s.video_published_at || '',
                    stockCounts,
                    signalTypes,
                  });
                }
              });

              // 추세 아이콘 결정 함수
              const getTrendIcon = (signalTypes: Map<string, number>) => {
                const buy = (signalTypes.get('매수') || 0) + (signalTypes.get('긍정') || 0);
                const sell = (signalTypes.get('매도') || 0) + (signalTypes.get('경계') || 0);
                const neutral = signalTypes.get('중립') || 0;
                if (buy > sell && buy > neutral) return '🟢';
                if (sell > buy && sell > neutral) return '🟠';
                return '⚪';
              };

              // 최근 활동 텍스트
              const getLastActivity = (dateStr: string) => {
                if (!dateStr) return '';
                const diff = Math.floor((Date.now() - new Date(dateStr).getTime()) / (1000 * 60 * 60 * 24));
                if (diff === 0) return '오늘 활동';
                if (diff === 1) return '어제 활동';
                return `${diff}일 전 활동`;
              };

              const speakers = Array.from(speakerMap.entries())
                .map(([name, data]) => ({
                  name,
                  ...data,
                  channelList: Array.from(data.channels),
                  topStocks: Array.from(data.stockCounts.entries())
                    .sort((a, b) => b[1] - a[1])
                    .slice(0, 3)
                    .map(([stock]) => stock),
                  trendIcon: getTrendIcon(data.signalTypes),
                  lastActivity: getLastActivity(data.latestDate),
                }))
                .filter(s => searchQuery === '' || s.name.toLowerCase().includes(searchQuery.toLowerCase()))
                .sort((a, b) => b.count - a.count);

              return speakers.map((speaker) => {
                const speakerId = speakerToSlug(speaker.name);
                // 호스트 판별: 채널명에 발언자 이름이 포함되거나, 발언자 이름에 채널명이 포함
                const isHost = speaker.channelList.some((ch: string) => 
                  ch.includes(speaker.name) || speaker.name.includes(ch) || ch === speaker.name
                );
                const thumbUrl = isHost && speaker.channelHandle
                  ? CHANNEL_THUMBNAILS[speaker.channelHandle] || null
                  : null;
                return (
                  <Link key={speaker.name} href={`/profile/influencer/${speakerId}`}>
                    <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100 hover:shadow-lg hover:-translate-y-1 transition-all duration-200 cursor-pointer">
                      <div className="flex items-center space-x-4 mb-4">
                        {thumbUrl ? (
                          <img
                            src={thumbUrl}
                            alt={speaker.name}
                            className="w-12 h-12 rounded-full object-cover border-2 border-gray-100"
                            onError={(e) => {
                              // 이미지 로드 실패 시 이니셜로 폴백
                              const target = e.target as HTMLImageElement;
                              target.style.display = 'none';
                              target.nextElementSibling?.classList.remove('hidden');
                            }}
                          />
                        ) : null}
                        <div className={`w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white font-bold text-lg ${thumbUrl ? 'hidden' : ''}`}>
                          {speaker.name.charAt(0)}
                        </div>
                        <div>
                          <h3 className="font-bold text-gray-900">{speaker.name}</h3>
                          {speaker.lastActivity && (
                            <p className="text-xs text-gray-400 mt-0.5">{speaker.lastActivity}</p>
                          )}
                        </div>
                      </div>
                      <div className="mb-3">
                        <span className="text-sm text-gray-500">언급 </span>
                        <span className="text-2xl font-bold text-[#3182f6]">{speaker.count}</span>
                        <span className="text-sm text-gray-500">회</span>
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
            {(() => {
              // 카테고리 필터 적용된 종목 그룹
              const categoryFilteredStocks = stockGroups.filter(group =>
                group.signals.some((s: any) => categoryFilter.size === 0 || categoryFilter.has(classifySignal(s)))
              ).map(group => ({
                ...group,
                signals: group.signals.filter((s: any) => categoryFilter.size === 0 || categoryFilter.has(classifySignal(s))),
                signal_count: group.signals.filter((s: any) => categoryFilter.size === 0 || categoryFilter.has(classifySignal(s))).length,
              })).filter((g: any) => searchQuery === '' || g.stock.toLowerCase().includes(searchQuery.toLowerCase()));

              return (<>
            <div className="text-sm text-gray-600 mb-4">
              총 {categoryFilteredStocks.length}개 종목
            </div>
            {categoryFilteredStocks.map((group) => {
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
              </>);
            })()}
          </div>
        )}
      </div>

      <SignalDetailModal signal={selectedSignal} onClose={() => setSelectedSignal(null)} />
    </div>
  );
}
