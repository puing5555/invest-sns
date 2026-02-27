'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { 
  getLatestInfluencerSignals, 
  getInfluencerChannels, 
  getStockSignalGroups,
  getSignalColor,
  reverseSignalMapping 
} from '@/lib/supabase';

export default function InfluencerPage() {
  const [activeTab, setActiveTab] = useState('latest');
  const [categoryFilter, setCategoryFilter] = useState('전체');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedComment, setSelectedComment] = useState<any>(null);
  const router = useRouter();

  // Supabase 데이터 상태
  const [latestSignals, setLatestSignals] = useState<any[]>([]);
  const [influencerChannels, setInfluencerChannels] = useState<any[]>([]);
  const [stockGroups, setStockGroups] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // 데이터 로드
  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        setError(null);
        const [signals, channels, stocks] = await Promise.all([
          getLatestInfluencerSignals(50),
          getInfluencerChannels(),
          getStockSignalGroups()
        ]);
        
        setLatestSignals(signals || []);
        setInfluencerChannels(channels || []);
        setStockGroups(stocks || []);
      } catch (error) {
        console.error('Error loading data:', error);
        setError('데이터를 불러오는데 실패했습니다.');
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, []);

  const tabs = [
    { id: 'latest', label: '최신 발언' },
    { id: 'influencers', label: '유튜버 모음' },
    { id: 'stocks', label: '종목별 검색' }
  ];

  const categoryOptions = ['전체', '한국주식', '미국주식', '코인'];

  // 신호 텍스트 변환 함수
  const getSignalText = (signal: string) => {
    // DB는 한글로 저장되어 있으므로 그대로 사용
    return signal;
  };

  // 카테고리별 필터링 함수 (현재는 전체만 지원)
  const filterData = (data: any[], category: string) => {
    if (category === '전체') return data;
    // TODO: 실제 카테고리 필터링 로직 추가 (한국주식/미국주식/코인)
    return data;
  };

  // 실시간 데이터를 UI용 형태로 변환
  const transformSignalToComment = (signal: any) => {
    const publishedDate = signal.influencer_videos?.published_at 
      ? new Date(signal.influencer_videos.published_at)
      : new Date();
    
    const videoUrl = signal.influencer_videos?.video_id 
      ? `https://youtube.com/watch?v=${signal.influencer_videos.video_id}`
      : '#';

    return {
      id: signal.id,
      speaker: signal.speakers?.name || 'Unknown',
      speakerId: signal.influencer_videos?.influencer_channels?.channel_handle || 'unknown',
      stock: signal.stock,
      stockCode: signal.ticker,
      signal: signal.signal,
      quote: signal.key_quote || '키 인용문이 없습니다.',
      timestamp: signal.timestamp ? `[${Math.floor(signal.timestamp / 60)}:${String(signal.timestamp % 60).padStart(2, '0')}]` : '[0:00]',
      videoTitle: signal.influencer_videos?.title || 'Unknown Video',
      summary: signal.reasoning || '분석 내용이 없습니다.',
      date: publishedDate.toISOString().split('T')[0],
      time: publishedDate.toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' }),
      videoUrl,
      category: '한국주식' // TODO: 실제 카테고리 분류 로직 추가
    };
  };

  // 채널 데이터를 UI용 형태로 변환
  const transformChannelToYoutuber = (channel: any) => {
    return {
      id: channel.id,
      name: channel.channel_name,
      slug: channel.channel_handle,
      avatar: '📺',
      subscribers: channel.subscriber_count ? `${Math.floor(channel.subscriber_count / 10000)}만` : 'N/A',
      totalSignals: channel.totalSignals || 0,
      category: '한국주식', // TODO: 실제 카테고리 분류 로직 추가
      tags: [] // TODO: 주요 종목 태그 추가
    };
  };

  const renderLatestTab = () => {
    if (loading) {
      return (
        <div className="text-center py-8">
          <div className="text-lg text-[#8b95a1]">데이터를 불러오는 중...</div>
        </div>
      );
    }

    const comments = latestSignals.map(transformSignalToComment);
    const filteredComments = filterData(comments, categoryFilter);

    return (
      <div className="space-y-4">
        {/* 카테고리 필터 */}
        <div className="flex gap-2 mb-6">
          {categoryOptions.map((category) => (
            <button
              key={category}
              onClick={() => setCategoryFilter(category)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                categoryFilter === category
                  ? 'bg-[#3182f6] text-white'
                  : 'bg-[#f8f9fa] text-[#8b95a1] hover:bg-[#e9ecef]'
              }`}
            >
              {category}
            </button>
          ))}
        </div>

        {/* 발언 카드 목록 */}
        <div className="space-y-4">
          {filteredComments.map((comment) => (
            <div key={comment.id} onClick={() => setSelectedComment(comment)} className="bg-white rounded-lg border border-[#e8e8e8] p-6 hover:shadow-md transition-shadow cursor-pointer">
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 rounded-full bg-[#f8f9fa] flex items-center justify-center text-xl">
                    📺
                  </div>
                  <div>
                    <Link 
                      href={`/profile/influencer/${comment.speakerId}`}
                      className="font-medium text-[#191f28] hover:text-[#3182f6] transition-colors cursor-pointer"
                    >
                      {comment.speaker}
                    </Link>
                    <div className="text-sm text-[#8b95a1]">{comment.date} {comment.time}</div>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <span className={`px-3 py-1 rounded-full text-xs font-medium border ${getSignalColor(comment.signal)}`}>
                    {comment.signal}
                  </span>
                </div>
              </div>
              
              <div className="mb-4">
                <div className="inline-block bg-[#f2f4f6] text-[#8b95a1] px-3 py-1 rounded-full text-sm font-medium mb-3">
                  {comment.stock}
                </div>
                <p className="text-[#191f28] leading-relaxed mb-4">{comment.quote}</p>
                <a 
                  href={comment.videoUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-2 text-[#3182f6] hover:text-[#2563eb] text-sm font-medium transition-colors"
                >
                  ▶ 영상보기
                </a>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  };

  const renderInfluencersTab = () => {
    if (loading) {
      return (
        <div className="text-center py-8">
          <div className="text-lg text-[#8b95a1]">데이터를 불러오는 중...</div>
        </div>
      );
    }

    const youtubers = influencerChannels.map(transformChannelToYoutuber);
    const filteredYoutubers = filterData(youtubers, categoryFilter);

    return (
      <div className="space-y-4">
        {/* 카테고리 필터 */}
        <div className="flex gap-2 mb-6">
          {categoryOptions.map((category) => (
            <button
              key={category}
              onClick={() => setCategoryFilter(category)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                categoryFilter === category
                  ? 'bg-[#3182f6] text-white'
                  : 'bg-[#f8f9fa] text-[#8b95a1] hover:bg-[#e9ecef]'
              }`}
            >
              {category}
            </button>
          ))}
        </div>

        {/* 유튜버 카드 그리드 */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredYoutubers.map((youtuber) => (
            <Link key={youtuber.id} href={`/profile/influencer/${youtuber.slug}`}>
              <div className="bg-white rounded-lg border border-[#e8e8e8] p-6 hover:shadow-md transition-shadow cursor-pointer">
                <div className="text-center mb-4">
                  <div className="w-16 h-16 mx-auto rounded-full bg-[#f8f9fa] flex items-center justify-center text-2xl mb-3">
                    {youtuber.avatar}
                  </div>
                  <h3 className="font-bold text-[#191f28] text-lg">{youtuber.name}</h3>
                  <div className="text-sm text-[#8b95a1] mt-1">구독자 {youtuber.subscribers}</div>
                </div>
                
                <div className="space-y-2 mb-4">
                  <div className="flex justify-between text-sm">
                    <span className="text-[#8b95a1]">총 신호 수</span>
                    <span className="font-medium text-[#191f28]">{youtuber.totalSignals}개</span>
                  </div>
                </div>

                <div>
                  <div className="text-xs text-[#8b95a1] mb-2">주요 종목</div>
                  <div className="flex flex-wrap gap-1">
                    {youtuber.tags.slice(0, 3).map((tag, index) => (
                      <span key={index} className="text-xs bg-[#f2f4f6] text-[#8b95a1] px-2 py-1 rounded">
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </Link>
          ))}
        </div>
      </div>
    );
  };

  const renderStocksTab = () => {
    if (loading) {
      return (
        <div className="text-center py-8">
          <div className="text-lg text-[#8b95a1]">데이터를 불러오는 중...</div>
        </div>
      );
    }

    const stocks = stockGroups.map((group: any) => ({
      id: group.ticker,
      name: group.name,
      code: group.ticker,
      mentionCount: group.mentionCount,
      topYoutubers: group.topSpeakers || [],
      otherCount: group.otherCount || 0,
      category: '한국주식' // TODO: 실제 카테고리 분류 로직 추가
    }));

    const filteredStocks = filterData(stocks, categoryFilter).filter(stock => 
      searchQuery === '' || stock.name.toLowerCase().includes(searchQuery.toLowerCase())
    );

    return (
      <div className="space-y-4">
        {/* 카테고리 필터 */}
        <div className="flex gap-2 mb-6">
          {categoryOptions.map((category) => (
            <button
              key={category}
              onClick={() => setCategoryFilter(category)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                categoryFilter === category
                  ? 'bg-[#3182f6] text-white'
                  : 'bg-[#f8f9fa] text-[#8b95a1] hover:bg-[#e9ecef]'
              }`}
            >
              {category}
            </button>
          ))}
        </div>

        {/* 검색창 */}
        <div className="relative mb-6">
          <input
            type="text"
            placeholder="종목명을 검색하세요..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-3 border border-[#e8e8e8] rounded-lg focus:outline-none focus:ring-2 focus:ring-[#3182f6] focus:border-transparent"
          />
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <svg className="w-5 h-5 text-[#8b95a1]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
        </div>

        {/* 인기 종목 목록 */}
        <div className="bg-white rounded-lg border border-[#e8e8e8] overflow-hidden">
          <div className="px-6 py-4 border-b border-[#e8e8e8] bg-[#f8f9fa]">
            <h3 className="font-medium text-[#191f28]">인기 종목 (유튜버 언급 순)</h3>
          </div>
          <div className="divide-y divide-[#f0f0f0]">
            {filteredStocks.map((stock) => (
              <Link 
                key={stock.id} 
                href={`/stock/${stock.code}?tab=influencer`}
                className="block px-6 py-4 hover:bg-[#f8f9fa] cursor-pointer transition-colors"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 rounded-full bg-[#f8f9fa] flex items-center justify-center text-lg">
                      📈
                    </div>
                    <div>
                      <div className="font-medium text-[#191f28] text-lg mb-1">{stock.name}</div>
                      <div className="text-sm text-[#8b95a1]">
                        {stock.topYoutubers.slice(0, 2).join(', ')}, {stock.topYoutubers[2]}
                        {stock.otherCount > 0 && ` 외 ${stock.otherCount}명`}
                      </div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-lg font-bold text-[#3182f6]">{stock.mentionCount}명</div>
                    <div className="text-sm text-[#8b95a1]">언급</div>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-[#f4f4f4]">
      <div className="bg-white border-b border-[#e8e8e8]">
        {/* 헤더 */}
        <div className="px-4 py-6">
          <h1 className="text-2xl font-bold text-[#191f28]">인플루언서</h1>
          <p className="text-[#8b95a1] mt-1">유튜버들의 투자 신호를 추적해보세요</p>
        </div>

        {/* 탭 */}
        <div className="px-4">
          <div className="flex overflow-x-auto scrollbar-hide">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => {
                  setActiveTab(tab.id);
                  setCategoryFilter('전체');
                  setSearchQuery('');
                }}
                className={`flex-shrink-0 px-6 py-3 text-sm font-medium transition-colors relative ${
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

      {/* 콘텐츠 */}
      <div className="px-4 py-6">
        {activeTab === 'latest' && renderLatestTab()}
        {activeTab === 'influencers' && renderInfluencersTab()}
        {activeTab === 'stocks' && renderStocksTab()}
      </div>

      {/* 영상 분석 팝업 */}
      {selectedComment && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4" onClick={() => setSelectedComment(null)}>
          <div className="bg-white rounded-2xl max-w-lg w-full max-h-[85vh] overflow-y-auto shadow-2xl" onClick={(e) => e.stopPropagation()}>
            {/* 팝업 헤더 */}
            <div className="flex items-center justify-between px-6 py-4 border-b border-[#e8e8e8]">
              <h3 className="font-bold text-[#191f28] text-lg">▶ 영상 분석</h3>
              <div className="flex items-center gap-2">
                <button className="w-9 h-9 rounded-full bg-[#f8f9fa] flex items-center justify-center text-[#8b95a1] hover:bg-[#e9ecef] transition-colors" title="메모 저장">
                  ♡
                </button>
                <button className="w-9 h-9 rounded-full bg-[#f8f9fa] flex items-center justify-center text-[#8b95a1] hover:bg-[#e9ecef] transition-colors" title="신고">
                  ⚠️
                </button>
                <button onClick={() => setSelectedComment(null)} className="w-9 h-9 rounded-full bg-[#f8f9fa] flex items-center justify-center text-[#8b95a1] hover:bg-[#e9ecef] transition-colors">
                  ✕
                </button>
              </div>
            </div>

            <div className="px-6 py-5">
              {/* 종목 + 신호 */}
              <div className="flex items-center gap-3 mb-4">
                <span className="text-xl font-bold text-[#191f28]">{selectedComment.stock}</span>
                <span className={`px-3 py-1 rounded-full text-xs font-medium border ${getSignalColor(selectedComment.signal)}`}>
                  {selectedComment.signal}
                </span>
              </div>

              {/* 영상 제목 + 날짜 */}
              <p className="text-sm text-[#8b95a1] mb-5">{selectedComment.videoTitle} · {selectedComment.date}</p>

              {/* 발언 내용 */}
              <div className="mb-5">
                <div className="text-xs font-medium text-[#8b95a1] mb-2">💬 발언 내용</div>
                <div className="bg-[#f8f9fa] rounded-xl p-4 border border-[#e8e8e8]">
                  <p className="text-[#191f28] leading-relaxed text-[15px]">"{selectedComment.quote}"</p>
                  <p className="text-xs text-[#3182f6] mt-2">타임스탬프: {selectedComment.timestamp}</p>
                </div>
              </div>

              {/* 영상 요약 */}
              <div className="mb-6">
                <div className="text-xs font-medium text-[#8b95a1] mb-2">📎 영상 요약</div>
                <p className="text-[#4e5968] text-sm leading-relaxed">{selectedComment.summary}</p>
              </div>

              {/* 버튼 2개 */}
              <div className="flex gap-3">
                <button
                  onClick={() => { setSelectedComment(null); router.push(`/stock/${selectedComment.stockCode}?tab=influencer`); }}
                  className="flex-1 py-3.5 bg-[#e8f4fd] text-[#3182f6] rounded-xl text-center font-medium hover:bg-[#d0e8fc] transition-colors border border-blue-200"
                >
                  📊 차트보기
                </button>
                <a
                  href={selectedComment.videoUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex-1 py-3.5 bg-[#3182f6] text-white rounded-xl text-center font-medium hover:bg-[#2171e5] transition-colors"
                >
                  ▶ 영상보기
                </a>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}