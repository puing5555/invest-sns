'use client';

import { useState } from 'react';
import Link from 'next/link';

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
  source?: string;
}

// 타임라인 더미 데이터
const timelineEvents: TimelineEvent[] = [
  {
    id: 1,
    type: 'disclosure',
    icon: '🔵',
    categoryName: '공시',
    stockName: '삼성전자',
    stockCode: '005930',
    title: 'A등급 공시 - 3분기 실적 컨센서스 상회',
    time: '3분 전'
  },
  {
    id: 2,
    type: 'influencer',
    icon: '🟢',
    categoryName: '인플루언서',
    stockName: '삼성전자',
    stockCode: '005930',
    title: '슈카월드 긍정 신호',
    time: '1시간 전',
    source: '슈카월드'
  },
  {
    id: 3,
    type: 'report',
    icon: '📊',
    categoryName: '리포트',
    stockName: '현대차',
    stockCode: '005380',
    title: '한국투자증권 목표가 상향',
    time: '2시간 전',
    source: '한국투자증권'
  },
  {
    id: 4,
    type: 'insider',
    icon: '👔',
    categoryName: '임원매매',
    stockName: '삼성전자',
    stockCode: '005930',
    title: '이재용 사장 매수 5만주',
    time: '3시간 전'
  },
  {
    id: 5,
    type: 'earnings',
    icon: '📈',
    categoryName: '실적',
    stockName: '현대차',
    stockCode: '005380',
    title: '3분기 영업이익 컨센서스 상회',
    time: '5시간 전'
  },
  {
    id: 6,
    type: 'news',
    icon: '📰',
    categoryName: '뉴스',
    stockName: '카카오',
    stockCode: '035720',
    title: 'AI 플랫폼 사업 확대 발표',
    time: '6시간 전'
  },
  {
    id: 7,
    type: 'disclosure',
    icon: '🔵',
    categoryName: '공시',
    stockName: 'LG에너지',
    stockCode: '373220',
    title: '北美 배터리 공장 증설 계획 공개',
    time: '8시간 전'
  },
  {
    id: 8,
    type: 'report',
    icon: '📊',
    categoryName: '리포트',
    stockName: 'NAVER',
    stockCode: '035420',
    title: '미래에셋 투자의견 상향',
    time: '10시간 전',
    source: '미래에셋증권'
  },
  {
    id: 9,
    type: 'influencer',
    icon: '🟢',
    categoryName: '인플루언서',
    stockName: 'SK하이닉스',
    stockCode: '000660',
    title: '코린이아빠 매수 신호',
    time: '12시간 전',
    source: '코린이아빠'
  },
  {
    id: 10,
    type: 'earnings',
    icon: '📈',
    categoryName: '실적',
    stockName: '카카오',
    stockCode: '035720',
    title: '모빌리티 부문 흑자 전환',
    time: '1일 전'
  }
];

export default function MyStocksPage() {
  const [selectedChip, setSelectedChip] = useState('전체');

  // 선택된 종목에 따른 이벤트 필터링
  const getFilteredEvents = () => {
    if (selectedChip === '전체') {
      return timelineEvents;
    }
    const selectedStock = stockChips.find(chip => chip.name === selectedChip);
    if (!selectedStock) return timelineEvents;
    
    return timelineEvents.filter(event => event.stockName === selectedChip);
  };

  const filteredEvents = getFilteredEvents();

  const handleEventClick = (event: TimelineEvent) => {
    // 해당 종목 페이지로 이동
    window.location.href = `/stock/${event.stockCode}`;
  };

  return (
    <div className="min-h-screen bg-[#f4f4f4]">
      {/* Header */}
      <div className="bg-white border-b border-[#e8e8e8] px-4 py-4">
        <div className="flex items-center justify-between">
          <h1 className="text-xl font-bold text-[#191f28]">⭐ 내 종목</h1>
        </div>
      </div>

      {/* 관심종목 칩 필터 */}
      <div className="bg-white border-b border-[#e8e8e8] px-4 py-4">
        <div className="flex gap-2 overflow-x-auto scrollbar-hide pb-1">
          {stockChips.map((chip, index) => (
            <button
              key={index}
              onClick={() => setSelectedChip(chip.name)}
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
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* 타임라인 리스트 */}
      <div className="max-w-4xl mx-auto px-4 py-6">
        <div className="bg-white rounded-lg border border-[#e8e8e8] overflow-hidden">
          {filteredEvents.length > 0 ? (
            <div className="divide-y divide-[#f0f0f0]">
              {filteredEvents.map((event) => (
                <div
                  key={event.id}
                  onClick={() => handleEventClick(event)}
                  className="px-4 py-4 hover:bg-[#f8f9fa] cursor-pointer transition-colors"
                >
                  <div className="flex items-center gap-3">
                    {/* 이벤트 아이콘 */}
                    <div className="w-10 h-10 rounded-full bg-[#f8f9fa] flex items-center justify-center text-lg flex-shrink-0">
                      {event.icon}
                    </div>
                    
                    {/* 이벤트 내용 */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-sm font-medium text-[#8b95a1] bg-[#f2f4f6] px-2 py-0.5 rounded">
                          {event.categoryName}
                        </span>
                        <span className="text-sm font-bold text-[#191f28]">
                          {event.stockName}
                        </span>
                        {event.source && (
                          <span className="text-xs text-[#8b95a1]">
                            • {event.source}
                          </span>
                        )}
                      </div>
                      <h3 className="text-[15px] font-medium text-[#191f28] leading-[1.4] mb-1">
                        {event.title}
                      </h3>
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-[#8b95a1]">
                          {event.time}
                        </span>
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
                해당 종목의 이벤트가 없습니다
              </div>
              <div className="text-sm text-[#8b95a1]">
                다른 종목을 선택하거나 전체를 확인해보세요
              </div>
            </div>
          )}
        </div>

        {/* 이벤트가 있는 경우 하단 설명 */}
        {filteredEvents.length > 0 && (
          <div className="mt-4 text-center">
            <p className="text-sm text-[#8b95a1]">
              이벤트를 클릭하면 해당 종목 페이지로 이동합니다
            </p>
          </div>
        )}
      </div>
    </div>
  );
}