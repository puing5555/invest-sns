'use client';

import { useState } from 'react';
import Link from 'next/link';

export default function InfluencerPage() {
  const [activeTab, setActiveTab] = useState('latest');
  const [categoryFilter, setCategoryFilter] = useState('전체');
  const [searchQuery, setSearchQuery] = useState('');

  const tabs = [
    { id: 'latest', label: '최신 발언' },
    { id: 'influencers', label: '유튜버 모음' },
    { id: 'stocks', label: '종목별 검색' }
  ];

  const categoryOptions = ['전체', '한국주식', '미국주식', '코인'];

  // 최신 발언 더미 데이터 (발언자 = 실제 발언한 사람 이름)
  const latestComments = [
    {
      id: 1,
      speaker: '슈카',
      speakerId: 'syuka',
      stock: '삼성전자',
      stockCode: '005930',
      signal: 'BUY',
      quote: '실적 개선 전망으로 지금이 매수 타이밍이라고 봅니다. Q4 실적 발표 이후 반등할 것으로 예상합니다.',
      date: '2026-02-25',
      time: '14:25',
      videoUrl: 'https://youtube.com/watch?v=sample1',
      category: '한국주식'
    },
    {
      id: 2,
      speaker: '김작가',
      speakerId: 'kimjakkga',
      stock: '테슬라',
      stockCode: 'TSLA',
      signal: 'POSITIVE',
      quote: '자율주행 기술 발전과 중국 시장 회복으로 긍정적 전망을 유지합니다.',
      date: '2026-02-24',
      time: '16:42',
      videoUrl: 'https://youtube.com/watch?v=sample2',
      category: '미국주식'
    },
    {
      id: 3,
      speaker: '홍춘욱',
      speakerId: 'hongchunuk',
      stock: '비트코인',
      stockCode: 'BTC',
      signal: 'NEUTRAL',
      quote: '단기적으로는 횡보 구간이지만, 중장기적으로는 상승 기조를 유지할 것으로 봅니다.',
      date: '2026-02-23',
      time: '10:15',
      videoUrl: 'https://youtube.com/watch?v=sample3',
      category: '코인'
    },
    {
      id: 4,
      speaker: '박세익',
      speakerId: 'parkseik',
      stock: 'SK하이닉스',
      stockCode: '000660',
      signal: 'CONCERN',
      quote: '메모리 반도체 수요 둔화 우려가 있어 신중한 접근이 필요해 보입니다.',
      date: '2026-02-22',
      time: '09:33',
      videoUrl: 'https://youtube.com/watch?v=sample4',
      category: '한국주식'
    },
    {
      id: 5,
      speaker: '이효석',
      speakerId: 'leehyoseok',
      stock: '엔비디아',
      stockCode: 'NVDA',
      signal: 'SELL',
      quote: '고점 대비 과열 구간에 진입했다고 판단됩니다. 차익실현을 권장합니다.',
      date: '2026-02-21',
      time: '15:47',
      videoUrl: 'https://youtube.com/watch?v=sample5',
      category: '미국주식'
    },
    {
      id: 6,
      speaker: '신사임당',
      speakerId: 'sinsaimdang',
      stock: '이더리움',
      stockCode: 'ETH',
      signal: 'POSITIVE',
      quote: 'ETF 승인 기대감과 스테이킹 수익률로 상승 모멘텀이 지속될 것 같습니다.',
      date: '2026-02-20',
      time: '11:22',
      videoUrl: 'https://youtube.com/watch?v=sample6',
      category: '코인'
    },
    {
      id: 7,
      speaker: '슈카',
      speakerId: 'syuka',
      stock: 'NAVER',
      stockCode: '035420',
      signal: 'BUY',
      quote: 'AI 사업부문 확장과 클라우드 서비스 성장으로 새로운 성장 동력을 확보했습니다.',
      date: '2026-02-19',
      time: '13:18',
      videoUrl: 'https://youtube.com/watch?v=sample7',
      category: '한국주식'
    },
    {
      id: 8,
      speaker: '김작가',
      speakerId: 'kimjakkga',
      stock: '애플',
      stockCode: 'AAPL',
      signal: 'NEUTRAL',
      quote: 'Vision Pro 판매는 부진하지만 서비스 부문 성장으로 장기적으로는 긍정적입니다.',
      date: '2026-02-18',
      time: '12:55',
      videoUrl: 'https://youtube.com/watch?v=sample8',
      category: '미국주식'
    },
    {
      id: 9,
      speaker: '홍춘욱',
      speakerId: 'hongchunuk',
      stock: '현대차',
      stockCode: '005380',
      signal: 'POSITIVE',
      quote: '전기차 라인업 확대와 배터리 기술 혁신으로 경쟁력이 강화되고 있습니다.',
      date: '2026-02-17',
      time: '14:40',
      videoUrl: 'https://youtube.com/watch?v=sample9',
      category: '한국주식'
    }
  ];

  // 유튜버 더미 데이터 (적중률, 수익률 삭제)
  const youtubers = [
    {
      id: 1,
      name: '슈카',
      slug: 'syuka',
      avatar: '🎭',
      subscribers: '128만',
      totalSignals: 245,
      category: '한국주식',
      tags: ['삼성전자', 'SK하이닉스', 'NAVER']
    },
    {
      id: 2,
      name: '김작가',
      slug: 'kimjakkga',
      avatar: '📚',
      subscribers: '85만',
      totalSignals: 189,
      category: '미국주식',
      tags: ['테슬라', '애플', '마이크로소프트']
    },
    {
      id: 3,
      name: '홍춘욱',
      slug: 'hongchunuk',
      avatar: '📊',
      subscribers: '156만',
      totalSignals: 312,
      category: '한국주식',
      tags: ['현대차', 'LG화학', '카카오']
    },
    {
      id: 4,
      name: '박세익',
      slug: 'parkseik',
      avatar: '⚡',
      subscribers: '92만',
      totalSignals: 167,
      category: '미국주식',
      tags: ['애플', '구글', '아마존']
    },
    {
      id: 5,
      name: '이효석',
      slug: 'leehyoseok',
      avatar: '💎',
      subscribers: '203만',
      totalSignals: 398,
      category: '미국주식',
      tags: ['엔비디아', '마이크로소프트', '테슬라']
    },
    {
      id: 6,
      name: '신사임당',
      slug: 'sinsaimdang',
      avatar: '👑',
      subscribers: '67만',
      totalSignals: 145,
      category: '코인',
      tags: ['비트코인', '이더리움', '솔라나']
    },
    {
      id: 7,
      name: '투자왕김작가',
      slug: 'tujawang',
      avatar: '🧠',
      subscribers: '174만',
      totalSignals: 267,
      category: '한국주식',
      tags: ['셀트리온', '삼성바이오', 'LG에너지']
    }
  ];

  // 인기 종목 더미 데이터 (대표 유튜버들과 함께 표시)
  const popularStocks = [
    {
      id: 1,
      name: '삼성전자',
      code: '005930',
      mentionCount: 15,
      topYoutubers: ['슈카', '김작가', '투자왕김작가'],
      otherCount: 12,
      category: '한국주식'
    },
    {
      id: 2,
      name: '비트코인',
      code: 'BTC',
      mentionCount: 18,
      topYoutubers: ['신사임당', '슈카', '홍춘욱'],
      otherCount: 15,
      category: '코인'
    },
    {
      id: 3,
      name: '테슬라',
      code: 'TSLA',
      mentionCount: 12,
      topYoutubers: ['슈카', '신사임당', '박세익'],
      otherCount: 9,
      category: '미국주식'
    },
    {
      id: 4,
      name: '엔비디아',
      code: 'NVDA',
      mentionCount: 14,
      topYoutubers: ['이효석', '김작가', '박세익'],
      otherCount: 11,
      category: '미국주식'
    },
    {
      id: 5,
      name: 'SK하이닉스',
      code: '000660',
      mentionCount: 9,
      topYoutubers: ['슈카', '박세익', '홍춘욱'],
      otherCount: 6,
      category: '한국주식'
    },
    {
      id: 6,
      name: '이더리움',
      code: 'ETH',
      mentionCount: 11,
      topYoutubers: ['신사임당', '이효석', '김작가'],
      otherCount: 8,
      category: '코인'
    },
    {
      id: 7,
      name: 'NAVER',
      code: '035420',
      mentionCount: 8,
      topYoutubers: ['슈카', '홍춘욱', '투자왕김작가'],
      otherCount: 5,
      category: '한국주식'
    },
    {
      id: 8,
      name: '애플',
      code: 'AAPL',
      mentionCount: 10,
      topYoutubers: ['김작가', '박세익', '이효석'],
      otherCount: 7,
      category: '미국주식'
    },
    {
      id: 9,
      name: '현대차',
      code: '005380',
      mentionCount: 7,
      topYoutubers: ['홍춘욱', '슈카', '투자왕김작가'],
      otherCount: 4,
      category: '한국주식'
    }
  ];

  const getSignalColor = (signal: string) => {
    switch (signal) {
      case 'BUY': return 'bg-blue-100 text-[#3182f6] border-blue-200';
      case 'POSITIVE': return 'bg-green-100 text-[#22c55e] border-green-200';
      case 'NEUTRAL': return 'bg-yellow-100 text-[#eab308] border-yellow-200';
      case 'CONCERN': return 'bg-orange-100 text-[#f97316] border-orange-200';
      case 'SELL': return 'bg-red-100 text-[#ef4444] border-red-200';
      default: return 'bg-gray-100 text-gray-600 border-gray-200';
    }
  };

  const getSignalText = (signal: string) => {
    switch (signal) {
      case 'BUY': return '매수';
      case 'POSITIVE': return '긍정';
      case 'NEUTRAL': return '중립';
      case 'CONCERN': return '경계';
      case 'SELL': return '매도';
      default: return signal;
    }
  };

  const filterData = (data: any[], category: string) => {
    if (category === '전체') return data;
    return data.filter(item => item.category === category);
  };

  const renderLatestTab = () => {
    const filteredComments = filterData(latestComments, categoryFilter);

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
            <div key={comment.id} className="bg-white rounded-lg border border-[#e8e8e8] p-6 hover:shadow-md transition-shadow">
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
                    {getSignalText(comment.signal)}
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
    const filteredStocks = filterData(popularStocks, categoryFilter).filter(stock => 
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
    </div>
  );
}