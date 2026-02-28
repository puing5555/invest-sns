'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { influencers } from '@/data/influencerData';

// V9 기준 한글 시그널 타입 색상
const V9_SIGNAL_COLORS = {
  '매수': 'bg-red-600 text-white',
  '긍정': 'bg-green-600 text-white', 
  '중립': 'bg-gray-500 text-white',
  '경계': 'bg-yellow-600 text-white',
  '매도': 'bg-red-800 text-white'
};

export default function InfluencerPage() {
  const [activeTab, setActiveTab] = useState('latest');
  const [categoryFilter, setCategoryFilter] = useState('전체');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedComment, setSelectedComment] = useState<any>(null);
  const router = useRouter();

  // 로컬 데이터에서 최신 시그널 생성
  const latestSignals = influencers.flatMap(influencer => 
    influencer.recentCalls.slice(0, 3).map(call => ({
      id: `${influencer.id}-${call.stock}`,
      stock: call.stock,
      signal_type: call.direction, // V9 한글 타입 그대로 사용
      speaker: influencer.name,
      content_snippet: `${call.stock} ${call.direction} 추천`,
      video_published_at: call.date,
      accuracy_rate: influencer.accuracy,
      return_rate: call.returnRate,
      status: call.status
    }))
  ).slice(0, 20);

  // 주식별 시그널 그룹화
  const stockGroups = latestSignals.reduce((groups: any[], signal) => {
    const existing = groups.find(g => g.stock === signal.stock);
    if (existing) {
      existing.signals.push(signal);
      existing.signal_count++;
    } else {
      groups.push({
        stock: signal.stock,
        signal_count: 1,
        latest_signal: signal.signal_type,
        latest_date: signal.video_published_at,
        signals: [signal]
      });
    }
    return groups;
  }, []).sort((a, b) => b.signal_count - a.signal_count);

  const getSignalColor = (signalType: string) => {
    return V9_SIGNAL_COLORS[signalType as keyof typeof V9_SIGNAL_COLORS] || 'bg-gray-500 text-white';
  };

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    const now = new Date();
    const diffHours = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60));
    if (diffHours < 24) return `${diffHours}시간 전`;
    return `${Math.floor(diffHours / 24)}일 전`;
  };

  const filteredSignals = latestSignals.filter(signal => 
    searchQuery === '' || 
    signal.stock.toLowerCase().includes(searchQuery.toLowerCase()) ||
    signal.speaker.toLowerCase().includes(searchQuery.toLowerCase())
  );

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
            
            {/* Search */}
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
              { id: 'latest', label: '🔥 최신 시그널', count: latestSignals.length },
              { id: 'influencers', label: '👥 인플루언서', count: influencers.length },
              { id: 'stocks', label: '📊 종목별', count: stockGroups.length }
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
                {tab.label} <span className="text-xs bg-gray-100 px-2 py-1 rounded-full ml-1">{tab.count}</span>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'latest' && (
          <div className="space-y-4">
            <div className="text-sm text-gray-600 mb-4">
              총 {filteredSignals.length}개 시그널
            </div>
            {filteredSignals.map((signal) => (
              <div key={signal.id} className="bg-white rounded-xl p-6 shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-3">
                      <div className={`px-3 py-1 rounded-full text-xs font-medium ${getSignalColor(signal.signal_type)}`}>
                        {signal.signal_type}
                      </div>
                      <span className="font-bold text-lg text-gray-900">{signal.stock}</span>
                      <span className="text-sm text-gray-500">by {signal.speaker}</span>
                    </div>
                    <p className="text-gray-700 text-sm mb-3">{signal.content_snippet}</p>
                    <div className="flex items-center space-x-4 text-xs text-gray-500">
                      <span>정확도 {signal.accuracy_rate}%</span>
                      <span>수익률 {signal.return_rate > 0 ? '+' : ''}{signal.return_rate.toFixed(1)}%</span>
                      <span>상태: {signal.status}</span>
                      <span>{formatDate(signal.video_published_at)}</span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {activeTab === 'influencers' && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredInfluencers.map((influencer) => (
              <Link key={influencer.id} href={`/profile/influencer/${influencer.id}`}>
                <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100 hover:shadow-lg transition-all cursor-pointer">
                  <div className="flex items-center space-x-4 mb-4">
                    <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white font-bold">
                      {influencer.name.charAt(0)}
                    </div>
                    <div>
                      <h3 className="font-bold text-gray-900">{influencer.name}</h3>
                      <p className="text-sm text-gray-500">{influencer.followers} 팔로워</p>
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-4 text-center">
                    <div>
                      <div className="text-2xl font-bold text-blue-600">{influencer.accuracy}%</div>
                      <div className="text-xs text-gray-500">정확도</div>
                    </div>
                    <div>
                      <div className="text-2xl font-bold text-gray-900">{influencer.totalCalls}</div>
                      <div className="text-xs text-gray-500">총 시그널</div>
                    </div>
                  </div>
                  
                  <div className="mt-4 pt-4 border-t border-gray-100">
                    <div className="text-sm text-gray-600">
                      평균 수익률: <span className={`font-medium ${influencer.avgReturn > 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {influencer.avgReturn > 0 ? '+' : ''}{influencer.avgReturn.toFixed(1)}%
                      </span>
                    </div>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}

        {activeTab === 'stocks' && (
          <div className="space-y-4">
            <div className="text-sm text-gray-600 mb-4">
              총 {filteredStockGroups.length}개 종목
            </div>
            {filteredStockGroups.map((group) => (
              <div key={group.stock} className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <h3 className="font-bold text-lg text-gray-900">{group.stock}</h3>
                    <span className="text-sm text-gray-500">{group.signal_count}개 시그널</span>
                    <div className={`px-2 py-1 rounded text-xs font-medium ${getSignalColor(group.latest_signal)}`}>
                      최신: {group.latest_signal}
                    </div>
                  </div>
                </div>
                
                <div className="space-y-2">
                  {group.signals.map((signal: any) => (
                    <div key={signal.id} className="flex items-center justify-between py-2 px-3 bg-gray-50 rounded">
                      <div className="flex items-center space-x-3">
                        <span className="font-medium text-sm">{signal.speaker}</span>
                        <div className={`px-2 py-1 rounded text-xs font-medium ${getSignalColor(signal.signal_type)}`}>
                          {signal.signal_type}
                        </div>
                      </div>
                      <div className="text-sm text-gray-500">
                        {signal.accuracy_rate}% 정확도 · {formatDate(signal.video_published_at)}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}