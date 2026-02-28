'use client';

import { useState } from 'react';

interface StockDisclosureTabProps {
  code: string;
}

// Dummy data for stock-specific disclosures
const getStockDisclosures = (code: string) => {
  const disclosures = {
    '005930': [
      {
        id: '1',
        date: '2026-02-28',
        type: '실적',
        grade: 'A',
        title: '3분기 실적 컨센서스 상회 발표',
        summary: '영업이익 15조 3,842억원 (컨센서스 대비 +21.7%)',
        impact: '메모리 반도체 회복, AI 칩 수요 증가',
        priceReaction: '+5.4%',
        aiAnalysis: '반도체 업사이클 진입, HBM 점유율 확대로 수익성 개선',
        keyMetrics: [
          { label: '매출액', value: '74.1조원', change: '+12.8%' },
          { label: '영업이익', value: '15.4조원', change: '+21.7%' },
          { label: '당기순이익', value: '11.2조원', change: '+18.9%' },
          { label: 'ROE', value: '22.3%', change: '+3.2%p' }
        ]
      },
      {
        id: '2',
        date: '2026-02-25',
        type: '자사주',
        grade: 'A',
        title: '자사주 500만주 취득 결정',
        summary: '총 3조원 규모, 주가 안정화 목적',
        impact: '주주가치 제고, EPS 개선 효과',
        priceReaction: '+2.8%',
        aiAnalysis: '대형주 자사주 매입 시 평균 +4.2% 상승 패턴',
        keyMetrics: [
          { label: '취득 주식수', value: '500만주', change: '신규' },
          { label: '취득 금액', value: '3조원', change: '시가총액 1.2%' },
          { label: '취득 기간', value: '6개월', change: '-' },
          { label: '취득 방법', value: '장내매수', change: '-' }
        ]
      },
      {
        id: '3',
        date: '2026-02-20',
        type: '사업보고서',
        grade: 'B',
        title: '2025년 사업보고서',
        summary: '연간 실적 및 사업 현황 공시',
        impact: 'R&D 투자 확대, 신사업 진출 계획',
        priceReaction: '+0.8%',
        aiAnalysis: 'R&D 집약적 기업의 지속적 투자 확대 긍정적',
        keyMetrics: [
          { label: '매출채권', value: '34.2조원', change: '+8.4%' },
          { label: '재고자산', value: '52.1조원', change: '+12.1%' },
          { label: '차입금', value: '18.7조원', change: '-2.3%' },
          { label: 'R&D비용', value: '27.8조원', change: '+15.6%' }
        ]
      }
    ],
    default: [
      {
        id: '1',
        date: '2026-02-28',
        type: '기타',
        grade: 'B',
        title: '최근 주요 공시 없음',
        summary: '해당 종목의 최근 공시를 준비중입니다.',
        impact: '-',
        priceReaction: '0.0%',
        aiAnalysis: '주요 공시 대기 중',
        keyMetrics: []
      }
    ]
  };
  
  return disclosures[code as keyof typeof disclosures] || disclosures.default;
};

// 애널리스트 리포트 데이터
const getAnalystReports = (code: string) => {
  const reports = {
    '005930': [
      {
        id: '1',
        firm: '한국투자증권',
        analyst: '김반도체',
        date: '2026-02-28',
        rating: 'BUY',
        targetPrice: '95,000',
        currentPrice: '82,500',
        upside: '+15.2%',
        summary: 'AI 반도체 수요 증가로 실적 개선 지속',
        keyPoints: ['HBM 점유율 70% 유지', 'AI 칩 매출 30% 증가', '메모리 가격 회복']
      },
      {
        id: '2',
        firm: '미래에셋증권',
        analyst: '박메모리',
        date: '2026-02-26',
        rating: 'BUY',
        targetPrice: '92,000',
        currentPrice: '82,500',
        upside: '+11.5%',
        summary: '3분기 실적 서프라이즈, 목표가 상향',
        keyPoints: ['컨센서스 상회', 'D램 가격 상승', '파운드리 수익성 개선']
      }
    ],
    default: []
  };
  
  return reports[code as keyof typeof reports] || reports.default;
};

export default function StockDisclosureTab({ code }: StockDisclosureTabProps) {
  const [selectedFilter, setSelectedFilter] = useState('전체');
  const [expandedDisclosure, setExpandedDisclosure] = useState<string | null>(null);
  const [activeSection, setActiveSection] = useState<'disclosure' | 'reports' | 'agenda'>('disclosure');
  
  const disclosures = getStockDisclosures(code);
  const analystReports = getAnalystReports(code);
  
  const filterOptions = ['전체', 'A등급', 'B등급', '실적', '지분', '자사주', '시설투자', '사업보고서', '기타'];
  
  const filteredDisclosures = disclosures.filter(disclosure => {
    if (selectedFilter === '전체') return true;
    if (selectedFilter === 'A등급') return disclosure.grade === 'A';
    if (selectedFilter === 'B등급') return disclosure.grade === 'B';
    return disclosure.type === selectedFilter;
  });

  return (
    <div className="space-y-6">
      {/* Filter Chips */}
      <div className="flex flex-wrap gap-2">
        {filterOptions.map((filter) => (
          <button
            key={filter}
            onClick={() => setSelectedFilter(filter)}
            className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${
              selectedFilter === filter
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            {filter}
          </button>
        ))}
      </div>

      {/* Section Toggle */}
      <div className="flex space-x-1 bg-gray-100 rounded-lg p-1">
        <button
          onClick={() => setActiveSection('disclosure')}
          className={`flex-1 py-2 px-4 rounded-lg text-sm font-medium transition-colors ${
            activeSection === 'disclosure'
              ? 'bg-blue-500 text-white'
              : 'text-gray-700 hover:text-gray-900'
          }`}
        >
          📋 공시
        </button>
        <button
          onClick={() => setActiveSection('reports')}
          className={`flex-1 py-2 px-4 rounded-lg text-sm font-medium transition-colors ${
            activeSection === 'reports'
              ? 'bg-green-500 text-white'
              : 'text-gray-700 hover:text-gray-900'
          }`}
        >
          📊 리포트
        </button>
        <button
          onClick={() => setActiveSection('agenda')}
          className={`flex-1 py-2 px-4 rounded-lg text-sm font-medium transition-colors ${
            activeSection === 'agenda'
              ? 'bg-purple-500 text-white'
              : 'text-gray-700 hover:text-gray-900'
          }`}
        >
          🏢 주총안건
        </button>
      </div>

      {/* Disclosure List */}
      {activeSection === 'disclosure' && (
        <div className="space-y-4">
          {filteredDisclosures.map((disclosure) => (
            <div key={disclosure.id} className="bg-white rounded-xl border border-gray-200 overflow-hidden">
              <div 
                className="p-4 cursor-pointer hover:bg-gray-50 transition-colors"
                onClick={() => setExpandedDisclosure(
                  expandedDisclosure === disclosure.id ? null : disclosure.id
                )}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      <span className={`inline-block w-6 h-6 text-xs font-bold text-white rounded-full text-center leading-6 ${
                        disclosure.grade === 'A' ? 'bg-red-500' : 'bg-orange-500'
                      }`}>
                        {disclosure.grade}
                      </span>
                      <span className={`px-2 py-1 rounded text-xs font-medium ${
                        disclosure.type === '실적' ? 'bg-green-100 text-green-800' :
                        disclosure.type === '자사주' ? 'bg-blue-100 text-blue-800' :
                        disclosure.type === '사업보고서' ? 'bg-purple-100 text-purple-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {disclosure.type}
                      </span>
                      <span className="text-sm text-gray-500">{disclosure.date}</span>
                      <span className={`text-sm font-medium ${
                        disclosure.priceReaction.startsWith('+') ? 'text-red-500' : 'text-blue-500'
                      }`}>
                        {disclosure.priceReaction}
                      </span>
                    </div>
                    
                    <h3 className="font-semibold text-gray-900 mb-2">{disclosure.title}</h3>
                    <p className="text-gray-700 text-sm mb-2">{disclosure.summary}</p>
                    <p className="text-gray-600 text-xs">{disclosure.impact}</p>
                  </div>
                  
                  <button className="text-gray-400 hover:text-gray-600 transition-colors">
                    <svg className={`w-5 h-5 transform transition-transform ${
                      expandedDisclosure === disclosure.id ? 'rotate-180' : ''
                    }`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  </button>
                </div>
              </div>

              {/* Expanded Content */}
              {expandedDisclosure === disclosure.id && (
                <div className="px-4 pb-4 border-t border-gray-100">
                  <div className="pt-4 space-y-4">
                    {/* AI Analysis */}
                    <div className="bg-blue-50 p-3 rounded-lg">
                      <div className="flex items-start space-x-2">
                        <span className="text-blue-600 font-medium text-sm">🤖 AI 분석:</span>
                        <span className="text-sm text-gray-700">{disclosure.aiAnalysis}</span>
                      </div>
                    </div>

                    {/* Key Metrics for Business Reports */}
                    {disclosure.type === '사업보고서' && disclosure.keyMetrics.length > 0 && (
                      <div className="bg-purple-50 p-4 rounded-lg">
                        <h4 className="font-medium text-purple-800 mb-3">📊 핵심 재무 변동</h4>
                        <div className="grid grid-cols-2 gap-3">
                          {disclosure.keyMetrics.map((metric, index) => (
                            <div key={index} className="bg-white p-3 rounded-lg">
                              <div className="text-sm text-gray-600">{metric.label}</div>
                              <div className="font-semibold text-gray-900">{metric.value}</div>
                              <div className={`text-sm ${
                                metric.change.startsWith('+') ? 'text-green-600' : 
                                metric.change.startsWith('-') ? 'text-red-600' : 'text-gray-600'
                              }`}>
                                {metric.change}
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Key Metrics for Other Types */}
                    {disclosure.type !== '사업보고서' && disclosure.keyMetrics.length > 0 && (
                      <div className="bg-gray-50 p-4 rounded-lg">
                        <h4 className="font-medium text-gray-800 mb-3">주요 지표</h4>
                        <div className="grid grid-cols-2 gap-3">
                          {disclosure.keyMetrics.map((metric, index) => (
                            <div key={index} className="flex justify-between">
                              <span className="text-sm text-gray-600">{metric.label}:</span>
                              <span className="text-sm font-medium text-gray-900">{metric.value}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Action Buttons */}
                    <div className="flex space-x-3">
                      <button className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors">
                        상세 분석
                      </button>
                      <button className="flex-1 bg-gray-100 text-gray-700 py-2 px-4 rounded-lg text-sm font-medium hover:bg-gray-200 transition-colors">
                        관련 공시
                      </button>
                    </div>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Analyst Reports Section */}
      {activeSection === 'reports' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold text-gray-900">실적 추정치 & 애널리스트 연동</h3>
            {analystReports.length > 0 && (
              <span className="text-sm text-gray-500">{analystReports.length}개 리포트</span>
            )}
          </div>

          {analystReports.length > 0 ? (
            <div className="space-y-4">
              {analystReports.map((report) => (
                <div key={report.id} className="bg-white rounded-xl border border-gray-200 p-4">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-2">
                        <h4 className="font-semibold text-gray-900">{report.firm}</h4>
                        <span className="text-sm text-gray-600">{report.analyst}</span>
                        <span className={`px-2 py-1 rounded text-xs font-medium ${
                          report.rating === 'BUY' ? 'bg-green-100 text-green-800' :
                          report.rating === 'HOLD' ? 'bg-yellow-100 text-yellow-800' :
                          'bg-red-100 text-red-800'
                        }`}>
                          {report.rating}
                        </span>
                        <span className="text-sm text-gray-500">{report.date}</span>
                      </div>
                      <p className="text-gray-700 text-sm mb-2">{report.summary}</p>
                    </div>
                    <div className="text-right">
                      <div className="text-lg font-bold text-gray-900">₩{report.targetPrice}</div>
                      <div className={`text-sm font-medium ${
                        report.upside.startsWith('+') ? 'text-green-600' : 'text-red-600'
                      }`}>
                        {report.upside}
                      </div>
                    </div>
                  </div>

                  <div className="bg-gray-50 p-3 rounded-lg">
                    <div className="text-sm text-gray-700 font-medium mb-2">주요 포인트</div>
                    <div className="flex flex-wrap gap-1">
                      {report.keyPoints.map((point, index) => (
                        <span key={index} className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded">
                          {point}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-12">
              <div className="text-4xl mb-4">📊</div>
              <h3 className="text-lg font-bold text-gray-900 mb-2">리포트 준비중</h3>
              <p className="text-gray-600">해당 종목의 애널리스트 리포트를 준비중입니다.</p>
            </div>
          )}
        </div>
      )}

      {/* Shareholders Meeting Agenda */}
      {activeSection === 'agenda' && (
        <div className="text-center py-12">
          <div className="text-4xl mb-4">🏢</div>
          <h3 className="text-lg font-bold text-gray-900 mb-2">주주총회 안건</h3>
          <p className="text-gray-600">주주총회 안건 정보를 준비중입니다.</p>
        </div>
      )}
    </div>
  );
}