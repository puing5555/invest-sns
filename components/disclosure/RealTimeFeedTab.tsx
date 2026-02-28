'use client';

import { useState, useEffect } from 'react';

// Dummy data for real-time feed
const realTimeDisclosures = [
  {
    id: '1',
    time: '13:45:23',
    company: '아이빔테크놀로지',
    marketCap: '983억',
    grade: 'A',
    title: '단일판매·공급계약 체결',
    amount: '23.5억',
    percentage: '14.77%',
    aiInsight: '매출대비 14.77%, 과거 유사 47건 D+3 +8.2%',
    priceChange: '+2.3%',
    isNew: true
  },
  {
    id: '2',
    time: '13:32:15',
    company: '와이엠씨',
    marketCap: '1,337억',
    grade: 'A',
    title: '자사주 500,000주 소각',
    amount: '50억',
    percentage: '3.75%',
    aiInsight: '소형주 소각 D+5 +6.3%',
    priceChange: '+1.8%',
    isNew: false
  },
  {
    id: '3',
    time: '13:18:07',
    company: '세아제강지주',
    marketCap: '4,200억',
    grade: 'A',
    title: '기업가치 제고 계획 예고',
    amount: '-',
    percentage: 'PBR 0.38',
    aiInsight: '예고→확정 36%',
    priceChange: '+0.9%',
    isNew: false
  },
  {
    id: '4',
    time: '13:02:44',
    company: 'HD한국조선해양',
    marketCap: '33조',
    grade: 'B',
    title: '해명공시 "미확정"',
    amount: '-',
    percentage: '인도 합작법인',
    aiInsight: '미확정 후 확정 36%',
    priceChange: '+0.5%',
    isNew: false
  },
  {
    id: '5',
    time: '12:55:12',
    company: '롯데케미칼',
    marketCap: '3.8조',
    grade: 'B',
    title: '사업재편 승인',
    amount: '6,000억',
    percentage: '출자',
    aiInsight: '기업활력법 D+5 +2.1%',
    priceChange: '-0.2%',
    isNew: false
  }
];

const todayStats = {
  totalCount: 127,
  aGradeCount: 18,
  bGradeCount: 34,
  majorNews: 5,
  marketImpact: '+0.3%'
};

export default function RealTimeFeedTab() {
  const [expandedItems, setExpandedItems] = useState<string[]>([]);
  const [currentTime, setCurrentTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  const toggleExpanded = (id: string) => {
    setExpandedItems(prev => 
      prev.includes(id) 
        ? prev.filter(item => item !== id)
        : [...prev, id]
    );
  };

  return (
    <div className="py-6 space-y-6">
      {/* Summary Banner */}
      <div className="bg-gradient-to-r from-gray-900 via-gray-800 to-gray-900 rounded-xl p-6 text-white">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-3">
            <div className="w-3 h-3 bg-green-400 rounded-full animate-pulse"></div>
            <h2 className="text-lg font-bold">실시간 공시 현황</h2>
            <span className="text-sm bg-white/20 px-2 py-1 rounded text-gray-200">
              {currentTime.toLocaleTimeString('ko-KR')}
            </span>
          </div>
          <div className="text-sm text-gray-300">
            마켓 임팩트: <span className="text-green-400 font-medium">{todayStats.marketImpact}</span>
          </div>
        </div>
        
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold">{todayStats.totalCount}</div>
            <div className="text-sm text-gray-300">전체 공시</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-red-400">{todayStats.aGradeCount}</div>
            <div className="text-sm text-gray-300">A등급</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-orange-400">{todayStats.bGradeCount}</div>
            <div className="text-sm text-gray-300">B등급</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-400">{todayStats.majorNews}</div>
            <div className="text-sm text-gray-300">주요 뉴스</div>
          </div>
        </div>
      </div>

      {/* Real-time Feed */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-900">실시간 공시 피드</h3>
          <div className="flex items-center space-x-2 text-sm text-gray-500">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
            <span>Live</span>
          </div>
        </div>

        <div className="space-y-3">
          {realTimeDisclosures.map((disclosure) => (
            <div 
              key={disclosure.id}
              className={`bg-white rounded-xl border transition-all duration-200 hover:shadow-lg ${
                disclosure.isNew ? 'ring-2 ring-blue-200 shadow-lg' : 'border-gray-200'
              }`}
            >
              <div 
                className="p-4 cursor-pointer"
                onClick={() => toggleExpanded(disclosure.id)}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      <span className={`inline-block w-6 h-6 text-xs font-bold text-white rounded-full text-center leading-6 ${
                        disclosure.grade === 'A' ? 'bg-red-500' : 'bg-orange-500'
                      }`}>
                        {disclosure.grade}
                      </span>
                      <span className="text-sm text-gray-500">{disclosure.time}</span>
                      {disclosure.isNew && (
                        <span className="bg-blue-100 text-blue-800 text-xs font-medium px-2 py-1 rounded-full">
                          NEW
                        </span>
                      )}
                      <span className={`text-sm font-medium ${
                        disclosure.priceChange.startsWith('+') ? 'text-red-500' : 'text-blue-500'
                      }`}>
                        {disclosure.priceChange}
                      </span>
                    </div>
                    
                    <div className="mb-2">
                      <h4 className="font-semibold text-gray-900 mb-1">
                        {disclosure.company}
                        <span className="text-sm text-gray-500 ml-2">시가총액 {disclosure.marketCap}</span>
                      </h4>
                      <p className="text-gray-700">{disclosure.title}</p>
                      {disclosure.amount !== '-' && (
                        <p className="text-sm text-gray-600">
                          계약금액: <span className="font-medium">{disclosure.amount}</span> 
                          ({disclosure.percentage})
                        </p>
                      )}
                    </div>
                  </div>
                  
                  <button className="text-gray-400 hover:text-gray-600 transition-colors">
                    <svg className={`w-5 h-5 transform transition-transform ${
                      expandedItems.includes(disclosure.id) ? 'rotate-180' : ''
                    }`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  </button>
                </div>
              </div>

              {/* Expanded Content */}
              {expandedItems.includes(disclosure.id) && (
                <div className="px-4 pb-4 border-t border-gray-100">
                  <div className="pt-4">
                    <div className="bg-blue-50 p-3 rounded-lg">
                      <div className="flex items-start space-x-2">
                        <span className="text-blue-600 font-medium text-sm">🤖 AI 분석:</span>
                        <span className="text-sm text-gray-700">{disclosure.aiInsight}</span>
                      </div>
                    </div>
                    
                    <div className="mt-3 flex space-x-3">
                      <button className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors">
                        상세 분석
                      </button>
                      <button className="flex-1 bg-gray-100 text-gray-700 py-2 px-4 rounded-lg text-sm font-medium hover:bg-gray-200 transition-colors">
                        유사 공시
                      </button>
                      <button className="bg-gray-100 text-gray-700 py-2 px-3 rounded-lg text-sm hover:bg-gray-200 transition-colors">
                        ⭐
                      </button>
                    </div>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Load More */}
        <div className="text-center py-6">
          <button className="bg-blue-600 text-white py-2 px-6 rounded-lg hover:bg-blue-700 transition-colors">
            더 많은 공시 보기
          </button>
        </div>
      </div>
    </div>
  );
}