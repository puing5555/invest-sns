'use client';

import { useState } from 'react';
import Link from 'next/link';

const exploreCards = [
  {
    title: '인플루언서',
    description: '검증된 주식 인플루언서들의 콜과 실적',
    icon: '👤',
    href: '/explore/influencer',
    color: 'bg-blue-50 border-blue-200 hover:bg-blue-100',
    iconColor: 'text-blue-600',
  },
  {
    title: '애널리스트',
    description: '증권사 애널리스트 리포트와 목표가',
    icon: '🎯',
    href: '/explore/analyst',
    color: 'bg-green-50 border-green-200 hover:bg-green-100',
    iconColor: 'text-green-600',
  },
  {
    title: '공시 대시보드',
    description: 'AI가 분석한 공시와 시그널 스코어',
    icon: '📋',
    href: '/explore/disclosure',
    color: 'bg-purple-50 border-purple-200 hover:bg-purple-100',
    iconColor: 'text-purple-600',
  },
  {
    title: '실적 센터',
    description: '기업 실적과 컨센서스 비교 분석',
    icon: '📊',
    href: '/explore/earnings',
    color: 'bg-orange-50 border-orange-200 hover:bg-orange-100',
    iconColor: 'text-orange-600',
  },
  {
    title: '임원/대주주',
    description: '임원 매매와 대주주 지분 변동 추적',
    icon: '💼',
    href: '/explore/insider',
    color: 'bg-red-50 border-red-200 hover:bg-red-100',
    iconColor: 'text-red-600',
  },
  {
    title: '투자 구루',
    description: '워렌 버핏 등 세계적 투자자들 추적',
    icon: '🐋',
    href: '/explore/guru',
    color: 'bg-teal-50 border-teal-200 hover:bg-teal-100',
    iconColor: 'text-teal-600',
  },
  {
    title: '전략연구실',
    description: '백테스트와 퀀트 전략 실험실',
    icon: '🧪',
    href: '/explore/lab',
    color: 'bg-indigo-50 border-indigo-200 hover:bg-indigo-100',
    iconColor: 'text-indigo-600',
  },
];

const quickSearches = [
  '삼성전자',
  'SK하이닉스',
  'NAVER',
  '카카오',
  'LG에너지',
  '현대차',
  '기아',
  '셀트리온',
];

export default function ExplorePage() {
  const [searchQuery, setSearchQuery] = useState('');

  const filteredCards = exploreCards.filter(card =>
    card.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    card.description.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-[#f4f4f4]">
      {/* Header */}
      <div className="bg-white border-b border-[#e8e8e8] px-4 py-6">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-2xl font-bold text-[#191f28] mb-4">🔍 탐색</h1>
          
          {/* Search Bar */}
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <span className="text-[#8b95a1] text-xl">🔍</span>
            </div>
            <input
              type="text"
              placeholder="종목명, 기업명 또는 키워드 검색..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-12 pr-4 py-3 border border-[#e8e8e8] rounded-lg focus:outline-none focus:ring-2 focus:ring-[#3182f6] focus:border-transparent text-[#191f28] placeholder-[#8b95a1]"
            />
          </div>

          {/* Quick Search Tags */}
          <div className="mt-4">
            <p className="text-sm text-[#8b95a1] mb-2">빠른 검색</p>
            <div className="flex flex-wrap gap-2">
              {quickSearches.map((tag, index) => (
                <button
                  key={index}
                  onClick={() => setSearchQuery(tag)}
                  className="px-3 py-1.5 bg-[#f8f9fa] hover:bg-[#e9ecef] border border-[#e8e8e8] rounded-full text-sm text-[#191f28] transition-colors"
                >
                  {tag}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Cards Grid */}
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredCards.map((card, index) => (
            <Link
              key={index}
              href={card.href}
              className={`block p-6 rounded-lg border-2 transition-all duration-200 hover:scale-105 hover:shadow-lg ${card.color}`}
            >
              <div className="flex items-center mb-4">
                <div className={`text-3xl mr-3 ${card.iconColor}`}>
                  {card.icon}
                </div>
                <h3 className="text-lg font-bold text-[#191f28]">
                  {card.title}
                </h3>
              </div>
              <p className="text-[#8b95a1] text-sm leading-relaxed">
                {card.description}
              </p>
              
              {/* Arrow Icon */}
              <div className="mt-4 flex justify-end">
                <div className={`w-8 h-8 rounded-full bg-white/50 flex items-center justify-center ${card.iconColor}`}>
                  <span className="text-sm">→</span>
                </div>
              </div>
            </Link>
          ))}
        </div>

        {/* No Results */}
        {searchQuery && filteredCards.length === 0 && (
          <div className="text-center py-12">
            <div className="text-6xl mb-4">🔍</div>
            <h3 className="text-xl font-bold text-[#191f28] mb-2">
              검색 결과가 없습니다
            </h3>
            <p className="text-[#8b95a1]">
              다른 키워드로 검색해보세요
            </p>
          </div>
        )}

        {/* Popular Categories */}
        {!searchQuery && (
          <div className="mt-12">
            <h2 className="text-xl font-bold text-[#191f28] mb-6">
              🔥 인기 카테고리
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-white rounded-lg border border-[#e8e8e8] p-4">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-semibold text-[#191f28]">공시 속보</h4>
                  <span className="text-xs text-[#8b95a1]">실시간</span>
                </div>
                <p className="text-sm text-[#8b95a1]">
                  방금 전 올라온 공시를 AI가 분석해서 알려드려요
                </p>
              </div>

              <div className="bg-white rounded-lg border border-[#e8e8e8] p-4">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-semibold text-[#191f28]">시그널 랭킹</h4>
                  <span className="text-xs bg-red-100 text-red-600 px-2 py-0.5 rounded">HOT</span>
                </div>
                <p className="text-sm text-[#8b95a1]">
                  오늘 가장 높은 시그널 스코어를 받은 종목들
                </p>
              </div>

              <div className="bg-white rounded-lg border border-[#e8e8e8] p-4">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-semibold text-[#191f28]">AI 추천</h4>
                  <span className="text-xs bg-blue-100 text-blue-600 px-2 py-0.5 rounded">NEW</span>
                </div>
                <p className="text-sm text-[#8b95a1]">
                  내 투자 성향에 맞는 종목을 AI가 추천해드려요
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}