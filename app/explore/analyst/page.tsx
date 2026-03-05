'use client';

import { useState, useMemo } from 'react';
import reportsData from '@/data/analyst_reports.json';
import stockPricesData from '@/data/stockPrices.json';
import TargetPriceChart from '@/components/TargetPriceChart';
import { isKoreanStock } from '@/lib/currency';
import ReportDetailModal from '@/components/ReportDetailModal';

const TICKER_NAMES: Record<string, string> = {
  '240810': '원익QnC', '284620': '카이', '298040': '효성중공업', '352820': '하이브', '403870': 'HPSP',
  '090430': '아모레퍼시픽', '000660': 'SK하이닉스', '079160': 'CJ CGV', '005380': '현대자동차',
  '005930': '삼성전자', '036930': '주성엔지니어링', '042700': '한미반도체', '006400': '삼성SDI',
  '000720': '현대건설', '005940': 'NH투자증권', '016360': '삼성증권', '039490': '키움증권',
  '051910': 'LG화학', '036570': '엔씨소프트', '071050': '한국금융지주',
};

interface Report {
  ticker: string;
  firm: string;
  analyst: string | null;
  title: string;
  target_price: number | null;
  opinion: string;
  published_at: string;
  pdf_url: string;
  summary?: string;
  ai_detail?: string;
}

const data = reportsData as Record<string, Report[]>;
const stockPrices = stockPricesData as Record<string, { currentPrice: number }>;

const allReports: Report[] = Object.values(data).flat();

// 애널리스트 분석 데이터 타입
interface AnalystStats {
  analyst: string;
  firm: string;
  reports: Report[];
  reportCount: number;
  stockCount: number;
  achievementRate: number;
  avgReturn: number;
  validReports: number; // 목표가가 있는 리포트 수
}

// 애널리스트별 성과 계산 함수
function calculateAnalystStats(reports: Report[]): AnalystStats[] {
  const analystMap = new Map<string, Report[]>();
  
  // 애널리스트별로 리포트 그룹화
  reports.forEach(report => {
    if (!report.analyst) return;
    const key = `${report.analyst}_${report.firm}`;
    if (!analystMap.has(key)) {
      analystMap.set(key, []);
    }
    analystMap.get(key)!.push(report);
  });
  
  const analystStats: AnalystStats[] = [];
  
  analystMap.forEach((analystReports, key) => {
    const [analyst, firm] = key.split('_');
    
    // 기본 통계
    const reportCount = analystReports.length;
    const stockCount = new Set(analystReports.map(r => r.ticker)).size;
    
    // 목표가가 있는 리포트만 필터링
    const validReports = analystReports.filter(r => 
      r.target_price && r.target_price > 0 && stockPrices[r.ticker]
    );
    
    let achievementRate = 0;
    let avgReturn = 0;
    
    if (validReports.length > 0) {
      // 적중률 계산 (현재가 >= 목표가인 비율)
      const achievedCount = validReports.filter(r => {
        const currentPrice = stockPrices[r.ticker]?.currentPrice;
        return currentPrice && currentPrice >= (r.target_price || 0);
      }).length;
      
      achievementRate = (achievedCount / validReports.length) * 100;
      
      // 평균 수익률 계산
      const returns = validReports.map(r => {
        const currentPrice = stockPrices[r.ticker]?.currentPrice;
        const targetPrice = r.target_price;
        if (currentPrice && targetPrice) {
          return ((currentPrice - targetPrice) / targetPrice) * 100;
        }
        return 0;
      });
      
      avgReturn = returns.reduce((sum, ret) => sum + ret, 0) / returns.length;
    }
    
    analystStats.push({
      analyst,
      firm,
      reports: analystReports,
      reportCount,
      stockCount,
      achievementRate: Math.round(achievementRate * 10) / 10,
      avgReturn: Math.round(avgReturn * 10) / 10,
      validReports: validReports.length
    });
  });
  
  return analystStats;
}

function OpinionBadge({ opinion }: { opinion: string }) {
  const styles = {
    'BUY': 'bg-[#22c55e]/10 text-[#22c55e] border border-[#22c55e]/20',
    'HOLD': 'bg-[#eab308]/10 text-[#eab308] border border-[#eab308]/20', 
    'SELL': 'bg-[#ef4444]/10 text-[#ef4444] border border-[#ef4444]/20'
  };
  
  return (
    <span className={`text-xs font-medium px-2 py-1 rounded-full ${styles[opinion as keyof typeof styles] || styles.HOLD}`}>
      {opinion}
    </span>
  );
}

function formatPrice(n: number | null, ticker?: string) {
  if (n === null || n === undefined) return '-';
  if (ticker && !isKoreanStock(ticker)) return `$${n.toLocaleString()}`;
  return `${Math.floor(n / 10000)}만원`;
}

function formatDate(dateStr: string) {
  try {
    const date = new Date(dateStr);
    const year = date.getFullYear().toString().slice(-2); // 2026 -> 26
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}.${month}.${day}`;
  } catch (e) {
    return dateStr;
  }
}

// AI Detail 렌더러 컴포넌트
function AiDetailRenderer({ content }: { content: string }) {
  const sections = parseAiDetail(content);
  
  if (sections.length === 0) {
    return (
      <div className="p-3 bg-gray-50 rounded-lg text-sm text-gray-600 whitespace-pre-line leading-relaxed">
        {content}
      </div>
    );
  }
  
  return (
    <div className="space-y-3">
      {sections.map((section, index) => (
        <div key={index} className="bg-gray-50 rounded-lg p-3 border-l-4 border-blue-200">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-lg">{getSectionIcon(section.title)}</span>
            <h4 className="font-medium text-gray-900 text-sm">{section.title}</h4>
          </div>
          <p className="text-sm text-gray-700 leading-relaxed whitespace-pre-line">
            {section.content}
          </p>
        </div>
      ))}
    </div>
  );
}

function parseAiDetail(content: string) {
  const sections = [];
  const lines = content.split('\n');
  let currentSection = null;
  
  for (const line of lines) {
    const trimmed = line.trim();
    
    // ## 헤더 감지
    if (trimmed.startsWith('## ')) {
      if (currentSection) {
        sections.push(currentSection);
      }
      currentSection = {
        title: trimmed.slice(3).trim(),
        content: ''
      };
    } else if (currentSection && trimmed) {
      currentSection.content += (currentSection.content ? '\n' : '') + trimmed;
    }
  }
  
  if (currentSection) {
    sections.push(currentSection);
  }
  
  return sections;
}

function getSectionIcon(title: string) {
  const iconMap: Record<string, string> = {
    '투자포인트': '📌',
    '실적전망': '📊',
    '밸류에이션': '💰',
    '리스크': '⚠️',
    '결론': '✅'
  };
  
  return iconMap[title] || '📄';
}

// 리포트 상세 모달 컴포넌트
// ReportModal removed - now using ReportDetailModal component

export default function AnalystPage() {
  const [activeTab, setActiveTab] = useState('latest');
  const [search, setSearch] = useState('');
  const [selectedReport, setSelectedReport] = useState<Report | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [analystSort, setAnalystSort] = useState<'achievement' | 'reports' | 'return'>('achievement');
  const [expandedAnalyst, setExpandedAnalyst] = useState<string | null>(null);
  const q = search.toLowerCase();

  const openReportModal = (report: Report) => {
    setSelectedReport(report);
    setIsModalOpen(true);
  };

  const closeReportModal = () => {
    setIsModalOpen(false);
    setSelectedReport(null);
  };

  // 최신순 정렬된 전체 리포트
  const sortedReports = useMemo(() =>
    [...allReports].sort((a, b) => b.published_at.localeCompare(a.published_at)),
    []
  );

  // 검색 필터
  const filteredReports = useMemo(() =>
    sortedReports.filter(r =>
      !q || r.firm.toLowerCase().includes(q) || (TICKER_NAMES[r.ticker] || '').toLowerCase().includes(q) || r.title.toLowerCase().includes(q)
    ), [sortedReports, q]
  );

  // 증권사별 그룹
  const firmGroups = useMemo(() => {
    const map: Record<string, Report[]> = {};
    for (const r of allReports) {
      (map[r.firm] ??= []).push(r);
    }
    return Object.entries(map)
      .map(([firm, reports]) => ({
        firm,
        reports,
        tickers: new Set(reports.map(r => r.ticker)).size,
      }))
      .filter(g => !q || g.firm.toLowerCase().includes(q))
      .sort((a, b) => b.reports.length - a.reports.length);
  }, [q]);

  // 종목별 그룹
  const tickerGroups = useMemo(() => {
    return Object.entries(data)
      .map(([ticker, reports]) => {
        const name = TICKER_NAMES[ticker] || ticker;
        const sorted = [...reports].sort((a, b) => b.published_at.localeCompare(a.published_at));
        const firms = [...new Set(reports.map(r => r.firm))];
        return { ticker, name, reports: sorted, firms, latest: sorted[0] };
      })
      .filter(g => !q || g.name.toLowerCase().includes(q) || g.firms.some(f => f.toLowerCase().includes(q)))
      .sort((a, b) => b.reports.length - a.reports.length);
  }, [q]);

  // 애널리스트별 통계
  const analystStats = useMemo(() => {
    const stats = calculateAnalystStats(allReports);
    return stats
      .filter(s => !q || s.analyst.toLowerCase().includes(q) || s.firm.toLowerCase().includes(q))
      .sort((a, b) => {
        switch (analystSort) {
          case 'achievement':
            return b.achievementRate - a.achievementRate;
          case 'reports':
            return b.reportCount - a.reportCount;
          case 'return':
            return b.avgReturn - a.avgReturn;
          default:
            return b.achievementRate - a.achievementRate;
        }
      });
  }, [q, analystSort]);

  const tabs = [
    { id: 'latest', label: '🔥 최신 리포트' },
    { id: 'analyst', label: '👤 애널리스트별' },
    { id: 'stock', label: '📈 종목별' },
    { id: 'firm', label: '🏢 증권사별' },
  ];

  const [expandedFirm, setExpandedFirm] = useState<string | null>(null);
  const [expandedTicker, setExpandedTicker] = useState<string | null>(null);

  return (
    <div className="min-h-screen bg-[#f8f9fa]">
      {/* 헤더 */}
      <div className="bg-white border-b border-gray-100 px-4 py-4">
        <h1 className="text-xl font-bold text-gray-900">📊 애널리스트 리포트</h1>
        <p className="text-sm text-gray-500 mt-1">20종목 · {allReports.length}개 리포트</p>
      </div>

      {/* 검색 */}
      <div className="px-4 pt-3">
        <input
          type="text"
          placeholder="종목명, 증권사 검색..."
          value={search}
          onChange={e => setSearch(e.target.value)}
          className="w-full px-4 py-2.5 bg-white rounded-xl border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-blue-200"
        />
      </div>

      {/* 탭 */}
      <div className="flex gap-2 px-4 pt-3 pb-2">
        {tabs.map(t => (
          <button
            key={t.id}
            onClick={() => setActiveTab(t.id)}
            className={`px-3 py-1.5 rounded-full text-sm font-medium transition-colors ${
              activeTab === t.id ? 'bg-gray-900 text-white' : 'bg-white text-gray-600 border border-gray-200'
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      <div className="px-4 pb-20">
        {/* 🔥 최신 리포트 */}
        {activeTab === 'latest' && (
          <div className="space-y-2">
            {filteredReports.slice(0, 100).map((r, i) => (
              <div 
                key={i} 
                className="bg-white rounded-xl p-4 shadow-sm cursor-pointer hover:shadow-md transition-shadow"
                onClick={() => openReportModal(r)}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-xs text-gray-400">{formatDate(r.published_at)}</span>
                      <OpinionBadge opinion={r.opinion} />
                    </div>
                    <p className="font-medium text-gray-900 text-sm truncate">{r.title}</p>
                    {r.summary && (
                      <p className="text-xs text-gray-500 mt-0.5 truncate">{r.summary}</p>
                    )}
                    <div className="flex items-center gap-2 mt-1">
                      <span className="text-xs text-blue-600 font-medium">{TICKER_NAMES[r.ticker] || r.ticker}</span>
                      <span className="text-xs text-gray-400">·</span>
                      <span className="text-xs text-gray-700 font-medium">목표 {formatPrice(r.target_price, r.ticker)}</span>
                    </div>
                  </div>
                  <div className="ml-2 text-lg">📄</div>
                </div>
              </div>
            ))}
            {filteredReports.length === 0 && <p className="text-center text-gray-400 py-10 text-sm">검색 결과가 없습니다</p>}
          </div>
        )}

        {/* 👤 애널리스트별 */}
        {activeTab === 'analyst' && (
          <div className="space-y-4">
            {/* 정렬 옵션 */}
            <div className="bg-white rounded-xl p-4 shadow-sm">
              <div className="flex gap-2 mb-3">
                <span className="text-sm font-medium text-gray-700">정렬:</span>
                <button
                  onClick={() => setAnalystSort('achievement')}
                  className={`text-xs px-2 py-1 rounded-full ${
                    analystSort === 'achievement' 
                      ? 'bg-blue-100 text-blue-700 font-medium' 
                      : 'text-gray-500 hover:text-gray-700'
                  }`}
                >
                  적중률순
                </button>
                <button
                  onClick={() => setAnalystSort('reports')}
                  className={`text-xs px-2 py-1 rounded-full ${
                    analystSort === 'reports' 
                      ? 'bg-blue-100 text-blue-700 font-medium' 
                      : 'text-gray-500 hover:text-gray-700'
                  }`}
                >
                  리포트수순
                </button>
                <button
                  onClick={() => setAnalystSort('return')}
                  className={`text-xs px-2 py-1 rounded-full ${
                    analystSort === 'return' 
                      ? 'bg-blue-100 text-blue-700 font-medium' 
                      : 'text-gray-500 hover:text-gray-700'
                  }`}
                >
                  수익률순
                </button>
              </div>
              <p className="text-xs text-gray-500">
                💡 적중률: 목표가 달성 비율 | 수익률: 목표가 대비 현재가 상승률 평균
              </p>
            </div>

            {/* 애널리스트 카드 리스트 */}
            <div className="space-y-2">
              {analystStats.map((analyst, index) => (
                <div key={`${analyst.analyst}_${analyst.firm}`} className="bg-white rounded-xl shadow-sm overflow-hidden">
                  <button
                    onClick={() => setExpandedAnalyst(
                      expandedAnalyst === `${analyst.analyst}_${analyst.firm}` 
                        ? null 
                        : `${analyst.analyst}_${analyst.firm}`
                    )}
                    className="w-full px-4 py-4 flex items-center justify-between hover:bg-gray-50 transition-colors"
                  >
                    <div className="flex items-center gap-3">
                      {/* 프로필 아이콘 */}
                      <div className="w-12 h-12 bg-gradient-to-br from-blue-100 to-blue-200 rounded-full flex items-center justify-center">
                        <span className="text-lg font-bold text-blue-600">
                          {analyst.analyst.charAt(0)}
                        </span>
                      </div>
                      
                      <div className="text-left">
                        <div className="flex items-center gap-2 mb-1">
                          <h3 className="font-bold text-gray-900 text-sm">{analyst.analyst}</h3>
                          <span className="text-xs text-gray-500">#{index + 1}</span>
                        </div>
                        <p className="text-xs text-gray-600 mb-2">{analyst.firm}</p>
                        
                        {/* 성과 배지 */}
                        <div className="flex items-center gap-2">
                          <div className="flex items-center gap-1 bg-green-50 px-2 py-1 rounded-full border border-green-200">
                            <span className="text-xs text-green-700">🎯</span>
                            <span className="text-xs font-bold text-green-700">
                              {analyst.achievementRate}%
                            </span>
                          </div>
                          
                          <div className="flex items-center gap-1 bg-blue-50 px-2 py-1 rounded-full border border-blue-200">
                            <span className="text-xs text-blue-700">📈</span>
                            <span className="text-xs font-bold text-blue-700">
                              {analyst.avgReturn >= 0 ? '+' : ''}{analyst.avgReturn}%
                            </span>
                          </div>
                          
                          <div className="flex items-center gap-1 bg-gray-50 px-2 py-1 rounded-full border border-gray-200">
                            <span className="text-xs text-gray-700">📄</span>
                            <span className="text-xs font-bold text-gray-700">
                              {analyst.reportCount}건
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-2">
                      <div className="text-right">
                        <p className="text-xs text-gray-500">{analyst.stockCount}종목 커버</p>
                        <p className="text-xs text-gray-400">유효분석 {analyst.validReports}건</p>
                      </div>
                      <span className="text-gray-400 text-sm">
                        {expandedAnalyst === `${analyst.analyst}_${analyst.firm}` ? '▲' : '▼'}
                      </span>
                    </div>
                  </button>
                  
                  {/* 확장된 리포트 목록 */}
                  {expandedAnalyst === `${analyst.analyst}_${analyst.firm}` && (
                    <div className="border-t border-gray-100 px-4 pb-3">
                      <div className="py-3">
                        <h4 className="font-medium text-gray-900 mb-3 text-sm flex items-center gap-2">
                          📊 최근 리포트 
                          <span className="text-xs text-gray-500">
                            (총 {analyst.reportCount}건 중 최신 10건)
                          </span>
                        </h4>
                        
                        {[...analyst.reports]
                          .sort((a, b) => b.published_at.localeCompare(a.published_at))
                          .slice(0, 10)
                          .map((report, i) => (
                            <div 
                              key={i} 
                              className="flex items-center justify-between py-2 border-b border-gray-50 last:border-0 cursor-pointer hover:bg-gray-50 px-2 rounded"
                              onClick={() => openReportModal(report)}
                            >
                              <div className="flex-1 min-w-0">
                                <p className="text-sm text-gray-800 truncate font-medium">{report.title}</p>
                                <div className="flex items-center gap-2 mt-1">
                                  <span className="text-xs text-blue-600 font-medium">
                                    {TICKER_NAMES[report.ticker] || report.ticker}
                                  </span>
                                  <span className="text-xs text-gray-400">
                                    {formatDate(report.published_at)}
                                  </span>
                                  <OpinionBadge opinion={report.opinion} />
                                  <span className="text-xs text-gray-700">
                                    목표 {formatPrice(report.target_price, report.ticker)}
                                  </span>
                                  {/* 현재가와 비교 표시 */}
                                  {report.target_price && stockPrices[report.ticker] && (
                                    <span className={`text-xs font-medium ${
                                      stockPrices[report.ticker].currentPrice >= report.target_price
                                        ? 'text-green-600' 
                                        : 'text-red-600'
                                    }`}>
                                      {stockPrices[report.ticker].currentPrice >= report.target_price 
                                        ? '✅ 달성' 
                                        : '❌ 미달성'}
                                    </span>
                                  )}
                                </div>
                              </div>
                              <button className="ml-2 text-blue-600 hover:text-blue-800">
                                📄
                              </button>
                            </div>
                          ))
                        }
                      </div>
                    </div>
                  )}
                </div>
              ))}
              
              {analystStats.length === 0 && (
                <div className="text-center py-10">
                  <div className="text-4xl mb-4">👤</div>
                  <p className="text-gray-500 text-sm">검색 결과가 없습니다.</p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* 🏢 증권사별 */}
        {activeTab === 'firm' && (
          <div className="space-y-2">
            {firmGroups.map(g => (
              <div key={g.firm} className="bg-white rounded-xl shadow-sm overflow-hidden">
                <button
                  onClick={() => setExpandedFirm(expandedFirm === g.firm ? null : g.firm)}
                  className="w-full px-4 py-3 flex items-center justify-between"
                >
                  <div>
                    <p className="font-medium text-gray-900 text-sm">{g.firm}</p>
                    <p className="text-xs text-gray-500 mt-0.5">{g.reports.length}개 리포트 · {g.tickers}종목 커버</p>
                  </div>
                  <span className="text-gray-400 text-sm">{expandedFirm === g.firm ? '▲' : '▼'}</span>
                </button>
                {expandedFirm === g.firm && (
                  <div className="border-t border-gray-100 px-4 pb-3">
                    {[...g.reports].sort((a, b) => b.published_at.localeCompare(a.published_at)).slice(0, 20).map((r, i) => (
                      <div key={i} className="flex items-center justify-between py-2 border-b border-gray-50 last:border-0">
                        <div className="flex-1 min-w-0">
                          <p className="text-sm text-gray-800 truncate">{r.title}</p>
                          <div className="flex items-center gap-2 mt-0.5">
                            <span className="text-xs text-blue-600">{TICKER_NAMES[r.ticker] || r.ticker}</span>
                            <span className="text-xs text-gray-400">{r.published_at}</span>
                            <OpinionBadge opinion={r.opinion} />
                          </div>
                        </div>
                        <a href={r.pdf_url} target="_blank" rel="noopener noreferrer" className="ml-2">📄</a>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}

        {/* 📈 종목별 */}
        {activeTab === 'stock' && (
          <div className="space-y-2">
            {tickerGroups.map(g => (
              <div key={g.ticker} className="bg-white rounded-xl shadow-sm overflow-hidden">
                <button
                  onClick={() => setExpandedTicker(expandedTicker === g.ticker ? null : g.ticker)}
                  className="w-full px-4 py-3 flex items-center justify-between"
                >
                  <div>
                    <p className="font-medium text-gray-900 text-sm">{g.name}</p>
                    <p className="text-xs text-gray-500 mt-0.5">
                      {g.reports.length}개 리포트 · {g.firms.join(', ')}
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    <OpinionBadge opinion={g.latest.opinion} />
                    <span className="text-gray-400 text-sm">{expandedTicker === g.ticker ? '▲' : '▼'}</span>
                  </div>
                </button>
                {expandedTicker === g.ticker && (
                  <div className="border-t border-gray-100">
                    {/* 목표가 차트 */}
                    <div className="p-4">
                      <TargetPriceChart reports={g.reports} stockName={g.name} />
                    </div>
                    
                    {/* 리포트 목록 */}
                    <div className="px-4 pb-3">
                      <h4 className="font-medium text-gray-900 mb-3 text-sm">📄 리포트 목록</h4>
                      {g.reports.slice(0, 20).map((r, i) => (
                        <div key={i} className="flex items-center justify-between py-2 border-b border-gray-50 last:border-0">
                          <div className="flex-1 min-w-0">
                            <p className="text-sm text-gray-800 truncate">{r.title}</p>
                            <div className="flex items-center gap-2 mt-0.5">
                              <span className="text-xs text-gray-500">{r.firm}</span>
                              <span className="text-xs text-gray-400">{formatDate(r.published_at)}</span>
                              <OpinionBadge opinion={r.opinion} />
                              <span className="text-xs text-gray-700">목표 {formatPrice(r.target_price, r.ticker)}</span>
                            </div>
                          </div>
                          <a href={r.pdf_url} target="_blank" rel="noopener noreferrer" className="ml-2">📄</a>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* 리포트 상세 모달 */}
      <ReportDetailModal 
        report={selectedReport}
        isOpen={isModalOpen}
        onClose={closeReportModal}
        type="report"
      />
    </div>
  );
}
