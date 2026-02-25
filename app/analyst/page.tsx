'use client';

import { useState } from 'react';
import { reports, analysts, Report, Analyst } from '@/data/analystData';
import AnalystTabs from '@/components/AnalystTabs';
import ReportCard from '@/components/ReportCard';
import ReportDetail from '@/components/ReportDetail';
import AnalystCard from '@/components/AnalystCard';
import AnalystDetail from '@/components/AnalystDetail';

type SortOption = 'accuracy' | 'return' | 'reports' | 'recent';
type SectorFilter = '전체' | '반도체' | '2차전지' | '바이오' | '조선' | '방산';

export default function AnalystPage() {
  const [activeTab, setActiveTab] = useState<'reports' | 'analysts'>('reports');
  const [selectedReport, setSelectedReport] = useState<Report | null>(null);
  const [selectedAnalyst, setSelectedAnalyst] = useState<Analyst | null>(null);
  const [reportDetailOpen, setReportDetailOpen] = useState(false);
  const [analystDetailOpen, setAnalystDetailOpen] = useState(false);
  
  // Report filters
  const [searchQuery, setSearchQuery] = useState('');
  const [reportFilters, setReportFilters] = useState({
    upOnly: false,
    newOnly: false,
    recentWeek: false,
    watchlistOnly: false
  });

  // Analyst filters
  const [sortBy, setSortBy] = useState<SortOption>('accuracy');
  const [sectorFilter, setSectorFilter] = useState<SectorFilter>('전체');

  const handleReportClick = (report: Report) => {
    setSelectedReport(report);
    setReportDetailOpen(true);
  };

  const handleAnalystClick = (analyst: Analyst) => {
    setSelectedAnalyst(analyst);
    setAnalystDetailOpen(true);
  };

  // Filter reports
  const filteredReports = reports.filter(report => {
    if (searchQuery && !report.stockName.toLowerCase().includes(searchQuery.toLowerCase()) && 
        !report.title.toLowerCase().includes(searchQuery.toLowerCase())) {
      return false;
    }
    if (reportFilters.upOnly && report.changeType !== 'up') return false;
    if (reportFilters.newOnly && report.changeType !== 'new') return false;
    // For now, recentWeek and watchlistOnly filters are just placeholders
    return true;
  });

  // Sort and filter analysts
  const filteredAndSortedAnalysts = analysts
    .filter(analyst => sectorFilter === '전체' || analyst.sector.includes(sectorFilter))
    .sort((a, b) => {
      switch (sortBy) {
        case 'accuracy':
          return b.accuracy - a.accuracy;
        case 'return':
          return b.avgReturn - a.avgReturn;
        case 'reports':
          return b.total - a.total;
        case 'recent':
          // Mock recent activity sort
          return 0;
        default:
          return 0;
      }
    });

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Sticky Tabs */}
      <div className="sticky top-0 z-10">
        <AnalystTabs activeTab={activeTab} onTabChange={setActiveTab} />
      </div>

      <div className="max-w-6xl mx-auto p-6">
        {activeTab === 'reports' ? (
          <div className="space-y-6">
            {/* Search and Filters */}
            <div className="space-y-4">
              {/* Search Bar */}
              <div className="relative">
                <input
                  type="text"
                  placeholder="종목명 또는 리포트 제목으로 검색"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#3182f6] focus:border-transparent"
                />
                <div className="absolute right-3 top-2.5">
                  <span className="text-gray-400">🔍</span>
                </div>
              </div>

              {/* Filter Buttons */}
              <div className="flex flex-wrap gap-2">
                <button
                  onClick={() => setReportFilters(prev => ({ ...prev, upOnly: !prev.upOnly }))}
                  className={`px-3 py-1.5 text-sm rounded-full border transition-colors ${
                    reportFilters.upOnly
                      ? 'bg-[#3182f6] text-white border-[#3182f6]'
                      : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
                  }`}
                >
                  목표가상향만
                </button>
                <button
                  onClick={() => setReportFilters(prev => ({ ...prev, newOnly: !prev.newOnly }))}
                  className={`px-3 py-1.5 text-sm rounded-full border transition-colors ${
                    reportFilters.newOnly
                      ? 'bg-[#3182f6] text-white border-[#3182f6]'
                      : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
                  }`}
                >
                  신규커버
                </button>
                <button
                  onClick={() => setReportFilters(prev => ({ ...prev, recentWeek: !prev.recentWeek }))}
                  className={`px-3 py-1.5 text-sm rounded-full border transition-colors ${
                    reportFilters.recentWeek
                      ? 'bg-[#3182f6] text-white border-[#3182f6]'
                      : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
                  }`}
                >
                  최근1주
                </button>
                <button
                  onClick={() => setReportFilters(prev => ({ ...prev, watchlistOnly: !prev.watchlistOnly }))}
                  className={`px-3 py-1.5 text-sm rounded-full border transition-colors ${
                    reportFilters.watchlistOnly
                      ? 'bg-[#3182f6] text-white border-[#3182f6]'
                      : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
                  }`}
                >
                  관심종목만
                </button>
              </div>
            </div>

            {/* Report Cards */}
            <div className="space-y-4">
              {filteredReports.map(report => (
                <ReportCard
                  key={report.id}
                  report={report}
                  onClick={() => handleReportClick(report)}
                />
              ))}
            </div>
          </div>
        ) : (
          <div className="space-y-6">
            {/* Sort and Filter Controls */}
            <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0">
              {/* Sort Dropdown */}
              <div className="flex items-center space-x-3">
                <label className="text-sm font-medium text-gray-700">정렬:</label>
                <select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value as SortOption)}
                  className="px-3 py-1.5 text-sm border border-gray-300 rounded-md focus:ring-2 focus:ring-[#3182f6] focus:border-transparent"
                >
                  <option value="accuracy">적중률순</option>
                  <option value="return">수익률순</option>
                  <option value="reports">리포트수순</option>
                  <option value="recent">최근활동순</option>
                </select>
              </div>

              {/* Sector Filter Tabs */}
              <div className="flex flex-wrap gap-1">
                {(['전체', '반도체', '2차전지', '바이오', '조선', '방산'] as SectorFilter[]).map(sector => (
                  <button
                    key={sector}
                    onClick={() => setSectorFilter(sector)}
                    className={`px-3 py-1.5 text-sm rounded-md transition-colors ${
                      sectorFilter === sector
                        ? 'bg-[#3182f6] text-white'
                        : 'bg-white text-gray-700 hover:bg-gray-100 border border-gray-300'
                    }`}
                  >
                    {sector}
                  </button>
                ))}
              </div>
            </div>

            {/* Analyst Cards Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              {filteredAndSortedAnalysts.map(analyst => (
                <AnalystCard
                  key={analyst.id}
                  analyst={analyst}
                  onClick={() => handleAnalystClick(analyst)}
                />
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Detail Panels */}
      <ReportDetail
        report={selectedReport}
        isOpen={reportDetailOpen}
        onClose={() => setReportDetailOpen(false)}
      />
      
      <AnalystDetail
        analyst={selectedAnalyst}
        isOpen={analystDetailOpen}
        onClose={() => setAnalystDetailOpen(false)}
      />
    </div>
  );
}