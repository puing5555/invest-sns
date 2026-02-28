'use client';

import { useState } from 'react';

// Dummy data for earnings season
const earningsData = {
  seasonStats: {
    quarter: '2026Q1',
    totalCompanies: 2847,
    reportedCount: 1234,
    scheduledCount: 1613,
    surpriseRate: 68.3,
    shockRate: 12.7,
    avgBeatMargin: '+4.2%',
    avgMissMargin: '-6.8%'
  },
  surprises: [
    {
      id: '1',
      company: '삼성전자',
      sector: '반도체',
      reportDate: '2026-02-25',
      earnings: '3,842억',
      consensus: '3,156억',
      beatMargin: '+21.7%',
      priceReaction: '+5.4%',
      grade: 'MEGA',
      keyFactors: ['메모리 가격 상승', 'AI 반도체 수요', 'HBM 점유율 확대']
    },
    {
      id: '2',
      company: '카카오',
      sector: '인터넷',
      reportDate: '2026-02-26',
      earnings: '2,134억',
      consensus: '1,789억',
      beatMargin: '+19.3%',
      priceReaction: '+8.2%',
      grade: 'SUPER',
      keyFactors: ['광고수익 회복', '게임 매출 증가', '톡비즈 성장']
    },
    {
      id: '3',
      company: '현대차',
      sector: '자동차',
      reportDate: '2026-02-27',
      earnings: '1,567억',
      consensus: '1,289억',
      beatMargin: '+21.6%',
      priceReaction: '+3.1%',
      grade: 'SUPER',
      keyFactors: ['전기차 판매 증가', '인도 법인 흑자', '고급차 수익성']
    }
  ],
  shocks: [
    {
      id: '4',
      company: '스튜디오드래곤',
      sector: '엔터테인먼트',
      reportDate: '2026-02-24',
      earnings: '-45억',
      consensus: '156억',
      missMargin: '-128.8%',
      priceReaction: '-15.2%',
      grade: 'MEGA',
      keyFactors: ['콘텐츠 제작비 증가', '중국향 수출 감소', '신작 부진']
    },
    {
      id: '5',
      company: '카카오뱅크',
      sector: '핀테크',
      reportDate: '2026-02-26',
      earnings: '234억',
      consensus: '378억',
      missMargin: '-38.1%',
      priceReaction: '-8.7%',
      grade: 'LARGE',
      keyFactors: ['대출 증가율 둔화', '충당금 증가', '마케팅비 상승']
    }
  ],
  upcoming: [
    {
      id: '6',
      company: '네이버',
      sector: '인터넷',
      scheduledDate: '2026-03-05',
      consensus: '1,856억',
      previousBeat: '+12.3%',
      keyWatchPoints: ['광고사업 회복', '클라우드 성장', '웹툰 수익화']
    },
    {
      id: '7',
      company: 'SK하이닉스',
      sector: '반도체',
      scheduledDate: '2026-03-07',
      consensus: '2,134억',
      previousBeat: '+34.7%',
      keyWatchPoints: ['HBM 출하량', 'AI 반도체 수요', '메모리 가격']
    },
    {
      id: '8',
      company: 'LG에너지솔루션',
      sector: '배터리',
      scheduledDate: '2026-03-10',
      consensus: '892억',
      previousBeat: '-8.4%',
      keyWatchPoints: ['북미 공장 가동률', 'ESS 수주', '원자재 가격']
    }
  ],
  consensusChanges: [
    { company: '삼성전자', change: '+15.2%', direction: 'up' },
    { company: '카카오', change: '+12.8%', direction: 'up' },
    { company: 'SK하이닉스', change: '+8.9%', direction: 'up' },
    { company: '현대차', change: '+6.7%', direction: 'up' },
    { company: '네이버', change: '-3.2%', direction: 'down' }
  ]
};

export default function EarningsSeasonTab() {
  const [activeView, setActiveView] = useState<'surprise' | 'shock' | 'upcoming' | 'consensus'>('surprise');
  const [sortBy, setSortBy] = useState<'date' | 'margin' | 'reaction'>('margin');

  return (
    <div className="py-6 space-y-6">
      {/* Season Statistics */}
      <div className="bg-gradient-to-r from-purple-600 via-blue-600 to-teal-600 rounded-xl p-6 text-white">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-xl font-bold">{earningsData.seasonStats.quarter} 실적 시즌</h2>
            <p className="text-purple-100">전체 {earningsData.seasonStats.totalCompanies}사 중 {earningsData.seasonStats.reportedCount}사 발표 완료</p>
          </div>
          <div className="text-right">
            <div className="text-2xl font-bold">{Math.round((earningsData.seasonStats.reportedCount / earningsData.seasonStats.totalCompanies) * 100)}%</div>
            <div className="text-sm text-purple-200">진행률</div>
          </div>
        </div>
        
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-white/10 rounded-lg p-3 text-center">
            <div className="text-2xl font-bold text-green-300">{earningsData.seasonStats.surpriseRate}%</div>
            <div className="text-xs text-purple-200">서프라이즈</div>
          </div>
          <div className="bg-white/10 rounded-lg p-3 text-center">
            <div className="text-2xl font-bold text-red-300">{earningsData.seasonStats.shockRate}%</div>
            <div className="text-xs text-purple-200">쇼크</div>
          </div>
          <div className="bg-white/10 rounded-lg p-3 text-center">
            <div className="text-lg font-bold text-blue-200">{earningsData.seasonStats.avgBeatMargin}</div>
            <div className="text-xs text-purple-200">평균 비트</div>
          </div>
          <div className="bg-white/10 rounded-lg p-3 text-center">
            <div className="text-lg font-bold text-orange-200">{earningsData.seasonStats.avgMissMargin}</div>
            <div className="text-xs text-purple-200">평균 미스</div>
          </div>
        </div>
      </div>

      {/* View Toggle */}
      <div className="flex flex-wrap gap-2">
        <button
          onClick={() => setActiveView('surprise')}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
            activeView === 'surprise'
              ? 'bg-green-500 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          🚀 서프라이즈 ({earningsData.surprises.length})
        </button>
        <button
          onClick={() => setActiveView('shock')}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
            activeView === 'shock'
              ? 'bg-red-500 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          💥 쇼크 ({earningsData.shocks.length})
        </button>
        <button
          onClick={() => setActiveView('upcoming')}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
            activeView === 'upcoming'
              ? 'bg-blue-500 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          📅 발표 예정 ({earningsData.upcoming.length})
        </button>
        <button
          onClick={() => setActiveView('consensus')}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
            activeView === 'consensus'
              ? 'bg-purple-500 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          📊 컨센서스 변화
        </button>
      </div>

      {/* Surprises View */}
      {activeView === 'surprise' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold text-gray-900">서프라이즈 실적</h3>
            <select 
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as any)}
              className="border border-gray-300 rounded-lg px-3 py-1 text-sm"
            >
              <option value="margin">비트 마진순</option>
              <option value="reaction">주가 반응순</option>
              <option value="date">발표일순</option>
            </select>
          </div>
          
          {earningsData.surprises.map((surprise) => (
            <div key={surprise.id} className="bg-white rounded-xl border-l-4 border-green-500 p-5 shadow-sm">
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <div className="flex items-center space-x-2 mb-2">
                    <h4 className="font-bold text-gray-900">{surprise.company}</h4>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      surprise.grade === 'MEGA' 
                        ? 'bg-purple-100 text-purple-800' 
                        : 'bg-green-100 text-green-800'
                    }`}>
                      {surprise.grade}
                    </span>
                    <span className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded">{surprise.sector}</span>
                  </div>
                  <div className="text-sm text-gray-600 mb-2">발표일: {surprise.reportDate}</div>
                </div>
                <div className="text-right">
                  <div className="text-green-600 font-bold text-lg">{surprise.priceReaction}</div>
                  <div className="text-sm text-gray-500">주가 반응</div>
                </div>
              </div>
              
              <div className="grid md:grid-cols-3 gap-4 mb-4">
                <div className="bg-gray-50 p-3 rounded-lg">
                  <div className="text-sm text-gray-600">실적</div>
                  <div className="font-bold text-gray-900">{surprise.earnings}</div>
                </div>
                <div className="bg-gray-50 p-3 rounded-lg">
                  <div className="text-sm text-gray-600">컨센서스</div>
                  <div className="font-bold text-gray-900">{surprise.consensus}</div>
                </div>
                <div className="bg-green-50 p-3 rounded-lg">
                  <div className="text-sm text-green-700">비트 마진</div>
                  <div className="font-bold text-green-700">{surprise.beatMargin}</div>
                </div>
              </div>
              
              <div className="bg-green-50 p-3 rounded-lg">
                <div className="text-sm text-green-700 font-medium mb-2">주요 요인</div>
                <div className="flex flex-wrap gap-1">
                  {surprise.keyFactors.map((factor, index) => (
                    <span key={index} className="bg-green-100 text-green-800 text-xs px-2 py-1 rounded">
                      {factor}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Shocks View */}
      {activeView === 'shock' && (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-gray-900">쇼크 실적</h3>
          
          {earningsData.shocks.map((shock) => (
            <div key={shock.id} className="bg-white rounded-xl border-l-4 border-red-500 p-5 shadow-sm">
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <div className="flex items-center space-x-2 mb-2">
                    <h4 className="font-bold text-gray-900">{shock.company}</h4>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      shock.grade === 'MEGA' 
                        ? 'bg-red-100 text-red-800' 
                        : 'bg-orange-100 text-orange-800'
                    }`}>
                      {shock.grade}
                    </span>
                    <span className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded">{shock.sector}</span>
                  </div>
                  <div className="text-sm text-gray-600 mb-2">발표일: {shock.reportDate}</div>
                </div>
                <div className="text-right">
                  <div className="text-red-600 font-bold text-lg">{shock.priceReaction}</div>
                  <div className="text-sm text-gray-500">주가 반응</div>
                </div>
              </div>
              
              <div className="grid md:grid-cols-3 gap-4 mb-4">
                <div className="bg-gray-50 p-3 rounded-lg">
                  <div className="text-sm text-gray-600">실적</div>
                  <div className="font-bold text-gray-900">{shock.earnings}</div>
                </div>
                <div className="bg-gray-50 p-3 rounded-lg">
                  <div className="text-sm text-gray-600">컨센서스</div>
                  <div className="font-bold text-gray-900">{shock.consensus}</div>
                </div>
                <div className="bg-red-50 p-3 rounded-lg">
                  <div className="text-sm text-red-700">미스 마진</div>
                  <div className="font-bold text-red-700">{shock.missMargin}</div>
                </div>
              </div>
              
              <div className="bg-red-50 p-3 rounded-lg">
                <div className="text-sm text-red-700 font-medium mb-2">주요 요인</div>
                <div className="flex flex-wrap gap-1">
                  {shock.keyFactors.map((factor, index) => (
                    <span key={index} className="bg-red-100 text-red-800 text-xs px-2 py-1 rounded">
                      {factor}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Upcoming View */}
      {activeView === 'upcoming' && (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-gray-900">실적 발표 예정</h3>
          
          {earningsData.upcoming.map((upcoming) => (
            <div key={upcoming.id} className="bg-white rounded-xl border border-gray-200 p-5 hover:shadow-lg transition-shadow">
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <div className="flex items-center space-x-2 mb-2">
                    <h4 className="font-bold text-gray-900">{upcoming.company}</h4>
                    <span className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded">{upcoming.sector}</span>
                  </div>
                  <div className="text-sm text-gray-600 mb-2">발표 예정일: {upcoming.scheduledDate}</div>
                </div>
                <div className="text-right">
                  <div className="text-blue-600 font-bold">{upcoming.consensus}</div>
                  <div className="text-sm text-gray-500">컨센서스</div>
                </div>
              </div>
              
              <div className="grid md:grid-cols-2 gap-4 mb-4">
                <div className="bg-blue-50 p-3 rounded-lg">
                  <div className="text-sm text-blue-700">이전 분기 실적</div>
                  <div className={`font-bold ${
                    upcoming.previousBeat.startsWith('+') ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {upcoming.previousBeat}
                  </div>
                </div>
                <div className="bg-gray-50 p-3 rounded-lg">
                  <div className="text-sm text-gray-600">컨센서스</div>
                  <div className="font-bold text-gray-900">{upcoming.consensus}</div>
                </div>
              </div>
              
              <div className="bg-gray-50 p-3 rounded-lg">
                <div className="text-sm text-gray-700 font-medium mb-2">주요 관전 포인트</div>
                <div className="flex flex-wrap gap-1">
                  {upcoming.keyWatchPoints.map((point, index) => (
                    <span key={index} className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded">
                      {point}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Consensus Changes View */}
      {activeView === 'consensus' && (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-gray-900">컨센서스 변화 추이</h3>
          
          <div className="bg-white rounded-xl border border-gray-200 p-5">
            <h4 className="font-medium text-gray-900 mb-4">최근 1주간 컨센서스 변화율</h4>
            
            <div className="space-y-3">
              {earningsData.consensusChanges.map((item, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="font-medium text-gray-900">{item.company}</div>
                  <div className={`font-bold ${
                    item.direction === 'up' ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {item.direction === 'up' ? '↗' : '↘'} {item.change}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}