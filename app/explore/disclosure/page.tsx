'use client';

import { useState } from 'react';
import RealTimeFeedTab from '@/components/disclosure/RealTimeFeedTab';
import HighlightsTab from '@/components/disclosure/HighlightsTab';
import EarningsSeasonTab from '@/components/disclosure/EarningsSeasonTab';
import DisclosureSearchTab from '@/components/disclosure/DisclosureSearchTab';

const tabs = [
  { id: 'highlights', label: '오늘의 하이라이트', icon: '⭐' },
  { id: 'realtime', label: '실시간 공시', icon: '📡' },
  { id: 'earnings', label: '실적 시즌', icon: '📊' },
  { id: 'search', label: '공시 DB', icon: '🔍' }
];

export default function DisclosurePage() {
  const [activeTab, setActiveTab] = useState('highlights');

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 sticky top-0 z-40">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-xl font-bold text-gray-900">공시 대시보드</h1>
              <p className="text-sm text-gray-500 mt-1">실시간 공시 분석 및 투자 인사이트</p>
            </div>
            <div className="text-right">
              <div className="text-sm text-gray-500">마지막 업데이트</div>
              <div className="text-sm font-medium text-blue-600">
                {new Date().toLocaleTimeString('ko-KR', { 
                  hour: '2-digit', 
                  minute: '2-digit',
                  second: '2-digit' 
                })}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="bg-white border-b border-gray-200 sticky top-[88px] z-30">
        <div className="container mx-auto px-4">
          <div className="flex overflow-x-auto scrollbar-hide">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center space-x-2 px-4 py-3 border-b-2 whitespace-nowrap transition-colors ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600 font-medium'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                <span className="text-lg">{tab.icon}</span>
                <span>{tab.label}</span>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Tab Content */}
      <div className="container mx-auto px-4">
        {activeTab === 'realtime' && <RealTimeFeedTab />}
        {activeTab === 'highlights' && <HighlightsTab />}
        {activeTab === 'earnings' && <EarningsSeasonTab />}
        {activeTab === 'search' && <DisclosureSearchTab />}
      </div>
    </div>
  );
}