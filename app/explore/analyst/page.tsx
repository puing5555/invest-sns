'use client';

import { useState } from 'react';
import Link from 'next/link';
import { analysts, latestReports, opinionColors, opinionLabels } from '@/data/analystData';

export default function AnalystPage() {
  const [activeTab, setActiveTab] = useState('latest');
  const [sectorFilter, setSectorFilter] = useState('전체');
  const [searchQuery, setSearchQuery] = useState('');

  // 필터링된 데이터
  const filteredReports = latestReports.filter(report => 
    (searchQuery === '' || 
     report.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
     report.analystName.toLowerCase().includes(searchQuery.toLowerCase())) &&
    (sectorFilter === '전체' || 
     analysts.find(a => a.id === report.analystId)?.sector === sectorFilter)
  );

  const filteredAnalysts = analysts.filter(analyst =>
    (searchQuery === '' ||
     analyst.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
     analyst.company.toLowerCase().includes(searchQuery.toLowerCase())) &&
    (sectorFilter === '전체' || analyst.sector === sectorFilter)
  );

  // 종목별 그룹화: 리포트에서 종목명 추출 → 애널리스트+최신 목표가/의견 매핑
  const stockGroups = (() => {
    const map: Record<string, { stock: string; reports: Array<typeof latestReports[0] & { sector: string }> }> = {};
    for (const analyst of analysts) {
      for (const report of analyst.recentReports) {
        // 리포트 제목에서 종목명 추출 (첫 ":" 앞)
        const stockName = report.title.split(':')[0].trim();
        if (!map[stockName]) {
          map[stockName] = { stock: stockName, reports: [] };
        }
        map[stockName].reports.push({
          ...report,
          analystId: analyst.id,
          analystName: analyst.name,
          company: analyst.company,
          accuracyRate: analyst.accuracyRate,
          sector: analyst.sector
        });
      }
    }
    return Object.values(map)
      .map(g => ({
        ...g,
        reports: g.reports.sort((a, b) => new Date(b.publishedAt).getTime() - new Date(a.publishedAt).getTime()),
        avgTarget: Math.round(g.reports.reduce((s, r) => s + r.targetPrice, 0) / g.reports.length),
        currentPrice: g.reports[0].currentPrice,
        analystCount: new Set(g.reports.map(r => r.analystId)).size,
      }))
      .filter(g =>
        searchQuery === '' ||
        g.stock.toLowerCase().includes(searchQuery.toLowerCase())
      )
      .sort((a, b) => b.analystCount - a.analystCount);
  })();

  const sectors = ['전체', ...Array.from(new Set(analysts.map(a => a.sector)))];

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    const now = new Date();
    const diffHours = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60));
    if (diffHours < 24) return `${diffHours}시간 전`;
    return `${Math.floor(diffHours / 24)}일 전`;
  };

  const formatPrice = (price: number) => price.toLocaleString() + '원';

  return (
    <div className="bg-[#f8f9fa] min-h-screen">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <h1 className="text-xl font-bold text-gray-900">📊 애널리스트 리포트</h1>
            
            {/* Search & Filter */}
            <div className="flex items-center space-x-4">
              <select
                value={sectorFilter}
                onChange={(e) => setSectorFilter(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {sectors.map(sector => (
                  <option key={sector} value={sector}>{sector}</option>
                ))}
              </select>
              
              <div className="relative">
                <input
                  type="text"
                  placeholder="종목명 또는 애널리스트 검색..."
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
              { id: 'latest', label: '🔥 최신 리포트', count: filteredReports.length },
              { id: 'analysts', label: '👩‍💼 애널리스트', count: filteredAnalysts.length },
              { id: 'stocks', label: '📈 종목별', count: stockGroups.length }
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
              총 {filteredReports.length}개 리포트
            </div>
            {filteredReports.map((report) => (
              <div key={report.id} className="bg-white rounded-xl p-6 shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <div className={`px-3 py-1 rounded-full text-xs font-medium ${opinionColors[report.investmentOpinion]}`}>
                        {opinionLabels[report.investmentOpinion]}
                      </div>
                      <span className="text-sm text-gray-500">
                        {report.analystName} · {report.company}
                      </span>
                      <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                        적중률 {report.accuracyRate}%
                      </span>
                    </div>
                    
                    <h3 className="text-lg font-bold text-gray-900 mb-2">{report.title}</h3>
                    <p className="text-gray-600 text-sm mb-3">{report.summary}</p>
                    
                    <div className="grid grid-cols-3 gap-4 text-sm">
                      <div>
                        <span className="text-gray-500">목표가: </span>
                        <span className="font-medium">{formatPrice(report.targetPrice)}</span>
                        {report.previousTargetPrice && (
                          <span className="text-xs text-green-600 ml-1">
                            (↑{formatPrice(report.targetPrice - report.previousTargetPrice)})
                          </span>
                        )}
                      </div>
                      <div>
                        <span className="text-gray-500">현재가: </span>
                        <span className="font-medium">{formatPrice(report.currentPrice)}</span>
                      </div>
                      <div>
                        <span className="text-gray-500">상승여력: </span>
                        <span className={`font-medium ${report.upsidePotential > 0 ? 'text-green-600' : 'text-red-600'}`}>
                          {report.upsidePotential > 0 ? '+' : ''}{report.upsidePotential.toFixed(1)}%
                        </span>
                      </div>
                    </div>
                    
                    {report.keyPoints && report.keyPoints.length > 0 && (
                      <div className="mt-3">
                        <div className="text-xs text-gray-500 mb-1">핵심 포인트:</div>
                        <div className="flex flex-wrap gap-1">
                          {report.keyPoints.map((point, index) => (
                            <span key={index} className="text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded">
                              {point}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                  
                  <div className="text-right text-sm text-gray-500 ml-4">
                    {formatDate(report.publishedAt)}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {activeTab === 'analysts' && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredAnalysts.map((analyst) => (
              <Link key={analyst.id} href={`/profile/analyst/${analyst.id}`}>
                <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100 hover:shadow-lg transition-all cursor-pointer">
                  <div className="flex items-center space-x-4 mb-4">
                    <div className="w-12 h-12 bg-gradient-to-br from-green-500 to-blue-600 rounded-full flex items-center justify-center text-white font-bold">
                      {analyst.name.charAt(0)}
                    </div>
                    <div>
                      <h3 className="font-bold text-gray-900">{analyst.name}</h3>
                      <p className="text-sm text-gray-500">{analyst.company}</p>
                    </div>
                  </div>
                  
                  <div className="mb-4">
                    <div className="text-xs text-blue-600 bg-blue-50 px-2 py-1 rounded inline-block mb-2">
                      {analyst.sector} 전문
                    </div>
                    <div className="text-xs text-gray-500">
                      경력 {analyst.experienceYears}년
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-4 text-center mb-4">
                    <div>
                      <div className="text-2xl font-bold text-green-600">{analyst.accuracyRate}%</div>
                      <div className="text-xs text-gray-500">적중률</div>
                    </div>
                    <div>
                      <div className="text-2xl font-bold text-gray-900">{analyst.totalReports}</div>
                      <div className="text-xs text-gray-500">총 리포트</div>
                    </div>
                  </div>
                  
                  <div className="pt-4 border-t border-gray-100">
                    <div className="text-sm text-gray-600">
                      평균 수익률: <span className={`font-medium ${analyst.avgReturn > 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {analyst.avgReturn > 0 ? '+' : ''}{analyst.avgReturn.toFixed(1)}%
                      </span>
                    </div>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}

        {activeTab === 'stocks' && (
          <div className="space-y-6">
            {stockGroups.map((group) => (
              <div key={group.stock} className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h3 className="text-xl font-bold text-gray-900">{group.stock}</h3>
                    <div className="flex items-center space-x-3 mt-1">
                      <span className="text-sm text-gray-500">현재가 {group.currentPrice.toLocaleString()}원</span>
                      <span className="text-sm text-gray-500">·</span>
                      <span className="text-sm text-blue-600 font-medium">평균 목표가 {group.avgTarget.toLocaleString()}원</span>
                      <span className="text-sm text-gray-500">·</span>
                      <span className={`text-sm font-medium ${((group.avgTarget - group.currentPrice) / group.currentPrice * 100) > 0 ? 'text-green-600' : 'text-red-600'}`}>
                        상승여력 {((group.avgTarget - group.currentPrice) / group.currentPrice * 100).toFixed(1)}%
                      </span>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-2xl font-bold text-blue-600">{group.analystCount}</div>
                    <div className="text-xs text-gray-500">커버 애널리스트</div>
                  </div>
                </div>
                
                <div className="space-y-3">
                  {group.reports.map((report) => (
                    <div key={report.id} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
                      <div className="flex items-center space-x-3">
                        <Link href={`/profile/analyst/${report.analystId}`}>
                          <div className="w-9 h-9 bg-gradient-to-br from-green-500 to-blue-600 rounded-full flex items-center justify-center text-white text-sm font-bold cursor-pointer hover:opacity-80">
                            {report.analystName.charAt(0)}
                          </div>
                        </Link>
                        <div>
                          <div className="flex items-center space-x-2">
                            <span className="font-medium text-gray-900">{report.analystName}</span>
                            <span className="text-xs text-gray-500">{report.company}</span>
                            <span className="text-xs bg-blue-50 text-blue-700 px-1.5 py-0.5 rounded">적중률 {report.accuracyRate}%</span>
                          </div>
                          <div className="text-xs text-gray-500 mt-0.5">{report.title}</div>
                        </div>
                      </div>
                      <div className="flex items-center space-x-4 text-sm">
                        <div className={`px-2.5 py-1 rounded-full text-xs font-medium ${opinionColors[report.investmentOpinion]}`}>
                          {opinionLabels[report.investmentOpinion]}
                        </div>
                        <div className="text-right">
                          <div className="font-medium text-gray-900">{report.targetPrice.toLocaleString()}원</div>
                          <div className={`text-xs ${report.upsidePotential > 0 ? 'text-green-600' : 'text-red-600'}`}>
                            {report.upsidePotential > 0 ? '+' : ''}{report.upsidePotential.toFixed(1)}%
                          </div>
                        </div>
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