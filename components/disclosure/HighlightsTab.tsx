'use client';

import { useState } from 'react';

// Dummy data for highlights
const dailyHighlights = {
  summary: {
    date: '2026-02-28',
    totalDisclosures: 127,
    aGradeCount: 18,
    bGradeCount: 34,
    majorEvents: 5,
    marketMovement: '+0.73%'
  },
  aiSummary: {
    overall: "오늘은 기업가치 제고 관련 공시가 집중되며 시장에 긍정적 영향을 미쳤습니다. 특히 자사주 매입·소각 공시가 증가하며 주주환원 정책에 대한 관심이 높아졌습니다.",
    keyTrends: [
      "자사주 매입·소각 공시 12건 (전일 대비 +50%)",
      "기업가치 제고 계획 발표 8건",
      "대규모 공급계약 체결 5건 (평균 계약금액 156억)",
      "배당 관련 공시 3건 (평균 배당률 2.8%)"
    ]
  },
  aGradeHighlights: [
    {
      id: '1',
      company: '아이빔테크놀로지',
      title: '단일판매·공급계약 체결',
      amount: '23.5억',
      impact: '매출대비 14.77%',
      aiAnalysis: '과거 유사 공시 47건 분석 결과 D+3 평균 +8.2% 상승',
      priceChange: '+2.3%',
      sector: 'IT부품',
      time: '13:45'
    },
    {
      id: '2',
      company: '와이엠씨',
      title: '자사주 500,000주 소각',
      amount: '50억',
      impact: '시가총액 대비 3.75%',
      aiAnalysis: '소형주 자사주 소각 D+5 평균 +6.3% 상승',
      priceChange: '+1.8%',
      sector: '화학',
      time: '13:32'
    },
    {
      id: '3',
      company: '세아제강지주',
      title: '기업가치 제고 계획 예고',
      amount: '-',
      impact: 'PBR 0.38',
      aiAnalysis: '예고 후 확정 공시 확률 36%, 주가 상승 확률 68%',
      priceChange: '+0.9%',
      sector: '철강',
      time: '13:18'
    }
  ],
  bGradeHighlights: [
    {
      id: '4',
      company: 'HD한국조선해양',
      title: '해명공시 "미확정"',
      amount: '-',
      impact: '인도 합작법인',
      aiAnalysis: '해명 후 실제 확정 발표 확률 36%',
      priceChange: '+0.5%',
      sector: '조선',
      time: '13:02'
    },
    {
      id: '5',
      company: '롯데케미칼',
      title: '사업재편 승인',
      amount: '6,000억',
      impact: '출자 규모',
      aiAnalysis: '기업활력법 관련 D+5 평균 +2.1% 상승',
      priceChange: '-0.2%',
      sector: '화학',
      time: '12:55'
    }
  ],
  sectorSummary: [
    { sector: 'IT부품', count: 12, avgReturn: '+3.2%', topCompany: '아이빔테크놀로지' },
    { sector: '화학', count: 8, avgReturn: '+1.9%', topCompany: '와이엠씨' },
    { sector: '철강', count: 6, avgReturn: '+2.1%', topCompany: '세아제강지주' },
    { sector: '조선', count: 4, avgReturn: '+0.8%', topCompany: 'HD한국조선해양' },
    { sector: '금융', count: 3, avgReturn: '+1.2%', topCompany: '우리금융지주' }
  ]
};

export default function HighlightsTab() {
  const [selectedDate, setSelectedDate] = useState('2026-02-28');
  const [activeSection, setActiveSection] = useState<'a-grade' | 'b-grade' | 'sector'>('a-grade');

  return (
    <div className="py-6 space-y-6">
      {/* Date Selection */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-gray-900">오늘의 하이라이트</h2>
          <p className="text-sm text-gray-500">AI가 선별한 주요 공시와 시장 분석</p>
        </div>
        <div className="flex items-center space-x-2">
          <label className="text-sm text-gray-700">날짜 선택:</label>
          <select 
            value={selectedDate}
            onChange={(e) => setSelectedDate(e.target.value)}
            className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="2026-02-28">2026-02-28 (오늘)</option>
            <option value="2026-02-27">2026-02-27</option>
            <option value="2026-02-26">2026-02-26</option>
            <option value="2026-02-25">2026-02-25</option>
          </select>
        </div>
      </div>

      {/* AI Summary Card */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl p-6 text-white">
        <div className="flex items-center space-x-2 mb-4">
          <span className="text-2xl">🤖</span>
          <h3 className="text-lg font-bold">AI 시장 분석 요약</h3>
          <span className="bg-white/20 text-xs px-2 py-1 rounded-full">
            {dailyHighlights.summary.date}
          </span>
        </div>
        
        <div className="grid md:grid-cols-2 gap-6">
          <div>
            <p className="text-blue-100 mb-4">{dailyHighlights.aiSummary.overall}</p>
            
            <div className="grid grid-cols-2 gap-3">
              <div className="text-center bg-white/10 rounded-lg p-3">
                <div className="text-xl font-bold">{dailyHighlights.summary.totalDisclosures}</div>
                <div className="text-xs text-blue-200">전체 공시</div>
              </div>
              <div className="text-center bg-white/10 rounded-lg p-3">
                <div className="text-xl font-bold text-green-300">{dailyHighlights.summary.marketMovement}</div>
                <div className="text-xs text-blue-200">코스피 영향</div>
              </div>
            </div>
          </div>
          
          <div>
            <h4 className="font-semibold mb-3 text-blue-100">주요 트렌드</h4>
            <ul className="space-y-2">
              {dailyHighlights.aiSummary.keyTrends.map((trend, index) => (
                <li key={index} className="flex items-start space-x-2 text-sm">
                  <span className="text-yellow-300 mt-1">▶</span>
                  <span className="text-blue-100">{trend}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>

      {/* Section Toggle */}
      <div className="flex space-x-1 bg-gray-100 rounded-lg p-1">
        <button
          onClick={() => setActiveSection('a-grade')}
          className={`flex-1 py-2 px-4 rounded-lg text-sm font-medium transition-colors ${
            activeSection === 'a-grade'
              ? 'bg-red-500 text-white'
              : 'text-gray-700 hover:text-gray-900'
          }`}
        >
          A등급 공시 ({dailyHighlights.summary.aGradeCount})
        </button>
        <button
          onClick={() => setActiveSection('b-grade')}
          className={`flex-1 py-2 px-4 rounded-lg text-sm font-medium transition-colors ${
            activeSection === 'b-grade'
              ? 'bg-orange-500 text-white'
              : 'text-gray-700 hover:text-gray-900'
          }`}
        >
          B등급 공시 ({dailyHighlights.summary.bGradeCount})
        </button>
        <button
          onClick={() => setActiveSection('sector')}
          className={`flex-1 py-2 px-4 rounded-lg text-sm font-medium transition-colors ${
            activeSection === 'sector'
              ? 'bg-blue-500 text-white'
              : 'text-gray-700 hover:text-gray-900'
          }`}
        >
          섹터별 요약
        </button>
      </div>

      {/* A Grade Highlights */}
      {activeSection === 'a-grade' && (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-gray-900 flex items-center space-x-2">
            <span className="w-6 h-6 bg-red-500 text-white rounded-full text-center text-sm font-bold">A</span>
            <span>A등급 주요 공시</span>
          </h3>
          
          {dailyHighlights.aGradeHighlights.map((highlight) => (
            <div key={highlight.id} className="bg-white rounded-xl border border-gray-200 p-5 hover:shadow-lg transition-shadow">
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                  <div className="flex items-center space-x-2 mb-2">
                    <h4 className="font-semibold text-gray-900">{highlight.company}</h4>
                    <span className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded">{highlight.sector}</span>
                    <span className="text-sm text-gray-500">{highlight.time}</span>
                  </div>
                  <p className="text-gray-700 mb-2">{highlight.title}</p>
                  {highlight.amount !== '-' && (
                    <p className="text-sm text-gray-600">
                      규모: <span className="font-medium">{highlight.amount}</span> ({highlight.impact})
                    </p>
                  )}
                </div>
                <div className="text-right">
                  <div className={`text-lg font-bold ${
                    highlight.priceChange.startsWith('+') ? 'text-red-500' : 'text-blue-500'
                  }`}>
                    {highlight.priceChange}
                  </div>
                </div>
              </div>
              
              <div className="bg-red-50 p-3 rounded-lg">
                <div className="flex items-start space-x-2">
                  <span className="text-red-600 font-medium text-sm">📊 AI 분석:</span>
                  <span className="text-sm text-gray-700">{highlight.aiAnalysis}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* B Grade Highlights */}
      {activeSection === 'b-grade' && (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-gray-900 flex items-center space-x-2">
            <span className="w-6 h-6 bg-orange-500 text-white rounded-full text-center text-sm font-bold">B</span>
            <span>B등급 주요 공시</span>
          </h3>
          
          {dailyHighlights.bGradeHighlights.map((highlight) => (
            <div key={highlight.id} className="bg-white rounded-xl border border-gray-200 p-5 hover:shadow-lg transition-shadow">
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                  <div className="flex items-center space-x-2 mb-2">
                    <h4 className="font-semibold text-gray-900">{highlight.company}</h4>
                    <span className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded">{highlight.sector}</span>
                    <span className="text-sm text-gray-500">{highlight.time}</span>
                  </div>
                  <p className="text-gray-700 mb-2">{highlight.title}</p>
                  {highlight.amount !== '-' && (
                    <p className="text-sm text-gray-600">
                      규모: <span className="font-medium">{highlight.amount}</span> ({highlight.impact})
                    </p>
                  )}
                </div>
                <div className="text-right">
                  <div className={`text-lg font-bold ${
                    highlight.priceChange.startsWith('+') ? 'text-red-500' : 'text-blue-500'
                  }`}>
                    {highlight.priceChange}
                  </div>
                </div>
              </div>
              
              <div className="bg-orange-50 p-3 rounded-lg">
                <div className="flex items-start space-x-2">
                  <span className="text-orange-600 font-medium text-sm">📊 AI 분석:</span>
                  <span className="text-sm text-gray-700">{highlight.aiAnalysis}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Sector Summary */}
      {activeSection === 'sector' && (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-gray-900">섹터별 요약</h3>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
            {dailyHighlights.sectorSummary.map((sector, index) => (
              <div key={sector.sector} className="bg-white rounded-xl border border-gray-200 p-4 hover:shadow-lg transition-shadow">
                <div className="flex items-center justify-between mb-3">
                  <h4 className="font-semibold text-gray-900">{sector.sector}</h4>
                  <span className="text-sm bg-blue-100 text-blue-800 px-2 py-1 rounded-full">
                    {sector.count}건
                  </span>
                </div>
                
                <div className="mb-3">
                  <div className="text-sm text-gray-600">평균 수익률</div>
                  <div className={`text-lg font-bold ${
                    sector.avgReturn.startsWith('+') ? 'text-red-500' : 'text-blue-500'
                  }`}>
                    {sector.avgReturn}
                  </div>
                </div>
                
                <div>
                  <div className="text-sm text-gray-600">대표 종목</div>
                  <div className="text-sm font-medium text-gray-900">{sector.topCompany}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}