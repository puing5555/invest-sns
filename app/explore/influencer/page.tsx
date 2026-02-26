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

  // 최신 발언 더미 데이터
  const latestComments = [
    {
      id: 1,
      youtuber: '슈카월드',
      stock: '삼성전자',
      signal: 'BUY',
      quote: '실적 개선 전망으로 지금이 매수 타이밍이라고 봅니다',
      return: '+12.5%',
      date: '2026-02-25',
      category: '한국주식'
    },
    {
      id: 2,
      youtuber: '김작가',
      stock: '테슬라',
      signal: 'POSITIVE',
      quote: '자율주행 기술 진전으로 긍정적 전망',
      return: '+8.3%',
      date: '2026-02-24',
      category: '미국주식'
    },
    {
      id: 3,
      youtuber: '삼프로',
      stock: '비트코인',
      signal: 'NEUTRAL',
      quote: '단기적으론 횡보, 중장기적으론 상승 전망',
      return: '+3.1%',
      date: '2026-02-23',
      category: '코인'
    },
    {
      id: 4,
      youtuber: '코인왕',
      stock: 'SK하이닉스',
      signal: 'CONCERN',
      quote: '메모리 반도체 수요 둔화 우려',
      return: '-2.8%',
      date: '2026-02-22',
      category: '한국주식'
    },
    {
      id: 5,
      youtuber: '슈카월드',
      stock: '엔비디아',
      signal: 'SELL',
      quote: '고점 대비 차익실현 구간 진입',
      return: '-5.2%',
      date: '2026-02-21',
      category: '미국주식'
    },
    {
      id: 6,
      youtuber: '투자왕김작가',
      stock: '이더리움',
      signal: 'POSITIVE',
      quote: 'ETF 승인으로 상승 모멘텀 지속',
      return: '+15.7%',
      date: '2026-02-20',
      category: '코인'
    },
    {
      id: 7,
      youtuber: '삼프로',
      stock: 'NAVER',
      signal: 'BUY',
      quote: 'AI 사업 확장으로 성장 동력 확보',
      return: '+6.4%',
      date: '2026-02-19',
      category: '한국주식'
    },
    {
      id: 8,
      youtuber: '코인왕',
      stock: '애플',
      signal: 'NEUTRAL',
      quote: 'Vision Pro 판매 부진하지만 장기적으론 긍정적',
      return: '+1.2%',
      date: '2026-02-18',
      category: '미국주식'
    }
  ];

  // 유튜버 더미 데이터
  const youtubers = [
    {
      id: 1,
      name: '슈카월드',
      slug: 'syuka',
      avatar: '🎭',
      subscribers: '128만',
      accuracy: '72%',
      category: '한국주식',
      tags: ['삼성전자', 'SK하이닉스', 'NAVER']
    },
    {
      id: 2,
      name: '김작가',
      slug: 'kimjakkga',
      avatar: '📚',
      subscribers: '85만',
      accuracy: '68%',
      category: '미국주식',
      tags: ['테슬라', '애플', '마이크로소프트']
    },
    {
      id: 3,
      name: '삼프로',
      slug: 'sampro',
      avatar: '⚡',
      subscribers: '156만',
      accuracy: '75%',
      category: '한국주식',
      tags: ['현대차', 'LG화학', '카카오']
    },
    {
      id: 4,
      name: '코인왕',
      slug: 'coinwang',
      avatar: '👑',
      subscribers: '92만',
      accuracy: '64%',
      category: '코인',
      tags: ['비트코인', '이더리움', '리플']
    },
    {
      id: 5,
      name: '투자왕김작가',
      slug: 'tujawang',
      avatar: '💎',
      subscribers: '203만',
      accuracy: '81%',
      category: '미국주식',
      tags: ['엔비디아', '구글', '아마존']
    },
    {
      id: 6,
      name: '주식천재',
      slug: 'stockgenius',
      avatar: '🧠',
      subscribers: '67만',
      accuracy: '69%',
      category: '한국주식',
      tags: ['셀트리온', '삼성바이오', 'LG에너지']
    }
  ];

  // 인기 종목 더미 데이터
  const popularStocks = [
    {
      id: 1,
      name: '삼성전자',
      mentionCount: 15,
      recentSignal: '매수 신호 다수',
      category: '한국주식'
    },
    {
      id: 2,
      name: '테슬라',
      mentionCount: 12,
      recentSignal: '긍정적 전망',
      category: '미국주식'
    },
    {
      id: 3,
      name: '비트코인',
      mentionCount: 18,
      recentSignal: '횡보 전망',
      category: '코인'
    },
    {
      id: 4,
      name: 'SK하이닉스',
      mentionCount: 9,
      recentSignal: '신중론 확산',
      category: '한국주식'
    },
    {
      id: 5,
      name: '엔비디아',
      mentionCount: 14,
      recentSignal: '차익실현 권고',
      category: '미국주식'
    },
    {
      id: 6,
      name: '이더리움',
      mentionCount: 11,
      recentSignal: '상승 모멘텀',
      category: '코인'
    },
    {
      id: 7,
      name: 'NAVER',
      mentionCount: 8,
      recentSignal: '매수 기회',
      category: '한국주식'
    },
    {
      id: 8,
      name: '애플',
      mentionCount: 10,
      recentSignal: '중립적 시각',
      category: '미국주식'
    }
  ];

  const getSignalColor = (signal: string) => {
    switch (signal) {
      case 'BUY': return 'bg-blue-100 text-blue-600';
      case 'POSITIVE': return 'bg-green-100 text-green-600';
      case 'NEUTRAL': return 'bg-yellow-100 text-yellow-600';
      case 'CONCERN': return 'bg-orange-100 text-orange-600';
      case 'SELL': return 'bg-red-100 text-red-600';
      default: return 'bg-gray-100 text-gray-600';
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
                    <div className="font-medium text-[#191f28]">{comment.youtuber}</div>
                    <div className="text-sm text-[#8b95a1]">{comment.date}</div>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <span className={`px-2 py-1 rounded text-xs font-medium ${getSignalColor(comment.signal)}`}>
                    {getSignalText(comment.signal)}
                  </span>
                  <span className={`text-sm font-medium ${
                    comment.return.startsWith('+') ? 'text-red-600' : 'text-blue-600'
                  }`}>
                    {comment.return}
                  </span>
                </div>
              </div>
              
              <div className="mb-3">
                <div className="inline-block bg-[#f2f4f6] text-[#8b95a1] px-2 py-1 rounded text-sm font-medium mb-2">
                  {comment.stock}
                </div>
                <p className="text-[#191f28] leading-relaxed">{comment.quote}</p>
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
                    <span className="text-[#8b95a1]">적중률</span>
                    <span className="font-medium text-[#191f28]">{youtuber.accuracy}</span>
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
              <div key={stock.id} className="px-6 py-4 hover:bg-[#f8f9fa] cursor-pointer transition-colors">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 rounded-full bg-[#f8f9fa] flex items-center justify-center text-lg">
                      📈
                    </div>
                    <div>
                      <div className="font-medium text-[#191f28] text-lg">{stock.name}</div>
                      <div className="text-sm text-[#8b95a1]">{stock.recentSignal}</div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-lg font-bold text-[#3182f6]">{stock.mentionCount}명</div>
                    <div className="text-sm text-[#8b95a1]">언급</div>
                  </div>
                </div>
              </div>
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