'use client';

import { useState, useMemo } from 'react';
import reportsData from '@/data/analyst_reports.json';
import stockPricesData from '@/data/stockPrices.json';
import { isKoreanStock } from '@/lib/currency';
import ReportDetailModal from '@/components/ReportDetailModal';

const TICKER_NAMES: Record<string, string> = {
  '105560': 'KB금융', '240810': '원익QnC', '259960': '크래프톤', '284620': '카이', '298040': '효성중공업',
  '352820': '하이브', '403870': 'HPSP', '051910': 'LG화학', '000720': '현대건설', '079160': 'CJ CGV',
  '039490': '키움증권', '042700': '한미반도체', '005930': '삼성전자', '006400': '삼성SDI',
  '016360': '삼성증권', '036930': '주성엔지니어링', '005380': '현대자동차', '005940': 'NH투자증권',
  '090430': '아모레퍼시픽', '071050': '한국금융지주', '000660': 'SK하이닉스', '036570': '엔씨소프트',
  '035420': 'NAVER', '055550': '신한지주', '068270': '셀트리온', '005490': 'POSCO홀딩스',
  '012330': '현대모비스', '066570': 'LG전자', '028260': '삼성물산', '000270': '기아',
  '096770': 'SK이노베이션', '003550': 'LG', '034730': 'SK', '032830': '삼성생명',
  '011200': 'HMM', '018260': '삼성에스디에스', '009150': '삼성전기', '030200': 'KT',
  '086790': '하나금융지주', '035720': '카카오', '004020': '현대제철', '003670': '포스코퓨처엠',
  '010130': '고려아연', '011170': '롯데케미칼', '017670': 'SK텔레콤',
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
  price_at_signal?: number;
  price_current?: number;
  return_3m?: number | null;
  return_6m?: number | null;
  return_12m?: number | null;
  target_achieved?: boolean;
}

const data = reportsData as Record<string, Report[]>;
const stockPrices = stockPricesData as Record<string, { currentPrice: number }>;

const allReports: Report[] = Object.values(data).flat();

// 종목별 성과 데이터 타입
interface StockPerformance {
  ticker: string;
  stockName: string;
  reports: Report[];
  totalReports: number;
  achievementRate: number;
  avgReturn: number;
  validReports: number;
  latestReport: Report;
}

// 애널리스트 분석 데이터 타입
interface AnalystStats {
  analyst: string;
  firm: string;
  reports: Report[];
  reportCount: number;
  stockCount: number;
  achievementRate: number;
  avgReturn: number;
  avgReturn12m: number; // 12개월 forward return 평균
  validReports: number; // 목표가가 있는 리포트 수
  stockPerformances: StockPerformance[]; // 종목별 성과
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

    // 12개월 forward return 평균 계산
    const reportsWithReturn12m = analystReports.filter(r => r.return_12m != null);
    const avgReturn12m = reportsWithReturn12m.length > 0
      ? reportsWithReturn12m.reduce((sum, r) => sum + (r.return_12m || 0), 0) / reportsWithReturn12m.length
      : 0;

    // 종목별 성과 계산
    const stockPerformances: StockPerformance[] = [];
    const stockMap = new Map<string, Report[]>();
    
    // 종목별로 리포트 그룹화
    analystReports.forEach(report => {
      if (!stockMap.has(report.ticker)) {
        stockMap.set(report.ticker, []);
      }
      stockMap.get(report.ticker)!.push(report);
    });
    
    stockMap.forEach((stockReports, ticker) => {
      const stockName = TICKER_NAMES[ticker] || ticker;
      const validStockReports = stockReports.filter(r => 
        r.target_price && r.target_price > 0 && stockPrices[r.ticker]
      );
      
      let stockAchievementRate = 0;
      let stockAvgReturn = 0;
      
      if (validStockReports.length > 0) {
        const achievedStockCount = validStockReports.filter(r => {
          const currentPrice = stockPrices[r.ticker]?.currentPrice;
          return currentPrice && currentPrice >= (r.target_price || 0);
        }).length;
        
        stockAchievementRate = (achievedStockCount / validStockReports.length) * 100;
        
        const stockReturns = validStockReports.map(r => {
          const currentPrice = stockPrices[r.ticker]?.currentPrice;
          const targetPrice = r.target_price;
          if (currentPrice && targetPrice) {
            return ((currentPrice - targetPrice) / targetPrice) * 100;
          }
          return 0;
        });
        
        stockAvgReturn = stockReturns.reduce((sum, ret) => sum + ret, 0) / stockReturns.length;
      }
      
      const latestReport = [...stockReports].sort((a, b) => b.published_at.localeCompare(a.published_at))[0];
      
      stockPerformances.push({
        ticker,
        stockName,
        reports: stockReports,
        totalReports: stockReports.length,
        achievementRate: Math.round(stockAchievementRate * 10) / 10,
        avgReturn: Math.round(stockAvgReturn * 10) / 10,
        validReports: validStockReports.length,
        latestReport
      });
    });
    
    // 종목별 성과를 적중률 순으로 정렬
    stockPerformances.sort((a, b) => b.achievementRate - a.achievementRate);
    
    analystStats.push({
      analyst,
      firm,
      reports: analystReports,
      reportCount,
      stockCount,
      achievementRate: Math.round(achievementRate * 10) / 10,
      avgReturn: Math.round(avgReturn * 10) / 10,
      avgReturn12m: Math.round(avgReturn12m * 10) / 10,
      validReports: validReports.length,
      stockPerformances
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

// 내용 없는 섹션 감지 패턴
const EMPTY_SECTION_PATTERNS = [
  /제시되지 않았습니다/,
  /명시되지 않았습니다/,
  /언급되지 않았습니다/,
  /확인되지 않았습니다/,
  /포함되어 있지 않/,
  /구체적인.{0,20}없습니다/,
  /직접적으로.{0,20}없습니다/,
  /별도.{0,10}언급.{0,10}없/,
  /본문에서.{0,20}않았습니다/,
  /본 리포트에서.{0,20}않았습니다/,
];

function isSectionEmpty(content: string): boolean {
  return EMPTY_SECTION_PATTERNS.some(pattern => pattern.test(content));
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

  const validSections = sections.filter(s => !isSectionEmpty(s.content));
  if (validSections.length === 0) {
    return (
      <div className="p-3 bg-gray-50 rounded-lg text-sm text-gray-600 whitespace-pre-line leading-relaxed">
        {content}
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {validSections.map((section, index) => (
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

export default function AnalystPage() {
  const [activeTab, setActiveTab] = useState('latest');
  const [search, setSearch] = useState('');
  const [selectedReport, setSelectedReport] = useState<Report | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [analystSort, setAnalystSort] = useState<'achievement' | 'reports' | 'return' | 'return_12m'>('reports');
  const [expandedAnalyst, setExpandedAnalyst] = useState<string | null>(null);
  const [expandedTicker, setExpandedTicker] = useState<string | null>(null);
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

  // 종목별 그룹 (최근 2주 리포트 수 많은 순 정렬)
  const tickerGroups = useMemo(() => {
    const twoWeeksAgo = new Date();
    twoWeeksAgo.setDate(twoWeeksAgo.getDate() - 14);
    
    return Object.entries(data)
      .map(([ticker, reports]) => {
        const name = TICKER_NAMES[ticker] || ticker;
        const sorted = [...reports].sort((a, b) => b.published_at.localeCompare(a.published_at));
        const firms = [...new Set(reports.map(r => r.firm))];
        
        // 최근 2주 내 리포트 수 계산
        const recentReports = reports.filter(r => new Date(r.published_at) >= twoWeeksAgo);
        const recentReportCount = recentReports.length;
        
        return { 
          ticker, 
          name, 
          reports: sorted, 
          firms, 
          latest: sorted[0],
          recentReportCount 
        };
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
          case 'return_12m':
            return b.avgReturn12m - a.avgReturn12m;
          default:
            return b.achievementRate - a.achievementRate;
        }
      });
  }, [q, analystSort]);

  const tabs = [
    { id: 'latest', label: '🔥 최신 리포트' },
    { id: 'stock', label: '📈 종목별' },
    { id: 'analyst', label: '👤 애널리스트별' },
  ];

  return (
    <div className="min-h-screen bg-[#f8f9fa]">
      {/* 헤더 */}
      <div className="bg-white border-b border-gray-100 px-4 py-4">
        <h1 className="text-xl font-bold text-gray-900">📊 애널리스트 리포트</h1>
        <p className="text-sm text-gray-500 mt-1">{Object.keys(data).length}종목 · {allReports.length.toLocaleString()}개 리포트</p>
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
            {filteredReports.slice(0, 200).map((r, i) => (
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

        {/* 📈 종목별 */}
        {activeTab === 'stock' && (
          <div className="space-y-2">
            {tickerGroups.map(g => {
              // 컨센서스 계산 (최근 3개월)
              const threeMonthsAgo = new Date();
              threeMonthsAgo.setDate(threeMonthsAgo.getDate() - 90);
              const recentReports = g.reports.filter(r => new Date(r.published_at) >= threeMonthsAgo);
              const recentWithTarget = recentReports.filter(r => r.target_price && r.target_price > 0);
              const buyCount = recentReports.filter(r => r.opinion === 'BUY').length;
              const holdCount = recentReports.filter(r => r.opinion === 'HOLD').length;
              const sellCount = recentReports.filter(r => r.opinion === 'SELL').length;
              const totalRecent = recentReports.length;
              const consensusOpinion = buyCount >= totalRecent / 2 ? 'BUY' : holdCount >= totalRecent / 2 ? 'HOLD' : totalRecent > 0 ? 'BUY' : 'HOLD';
              const targetPrices = recentWithTarget.map(r => r.target_price!);
              const minTarget = targetPrices.length > 0 ? Math.min(...targetPrices) : null;
              const maxTarget = targetPrices.length > 0 ? Math.max(...targetPrices) : null;
              const avgTarget = targetPrices.length > 0 ? targetPrices.reduce((a, b) => a + b, 0) / targetPrices.length : null;
              const currentPrice = stockPrices[g.ticker]?.currentPrice;
              const upside = avgTarget && currentPrice ? ((avgTarget - currentPrice) / currentPrice * 100) : null;

              return (
              <div key={g.ticker} className="bg-white rounded-xl shadow-sm overflow-hidden">
                <button
                  onClick={() => setExpandedTicker(expandedTicker === g.ticker ? null : g.ticker)}
                  className="w-full px-4 py-3 flex items-center justify-between"
                >
                  <div>
                    <p className="font-medium text-gray-900 text-sm">{g.name}</p>
                    <p className="text-xs text-gray-500 mt-0.5">
                      {g.reports.length}건
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    <OpinionBadge opinion={g.latest.opinion} />
                    <span className="text-gray-400 text-sm">{expandedTicker === g.ticker ? '▲' : '▼'}</span>
                  </div>
                </button>
                {expandedTicker === g.ticker && (
                  <div className="border-t border-gray-100">
                    {/* 컨센서스 요약 카드 */}
                    <div className="p-4 bg-gray-50 border-b border-gray-100">
                      <div className="flex items-center justify-between mb-2">
                        <div>
                          <h4 className="font-bold text-gray-900 text-sm">애널리스트 컨센서스</h4>
                          <p className="text-xs text-gray-500">최근 3개월 리포트 기준</p>
                        </div>
                        {g.reports.length > 0 && (
                          <div className="text-right">
                            <p className="text-xs text-gray-700 font-medium truncate max-w-[180px]">{g.reports[0].title}</p>
                            <p className="text-xs text-gray-400">{g.reports[0].firm} · {formatDate(g.reports[0].published_at)}</p>
                          </div>
                        )}
                      </div>
                      
                      {totalRecent > 0 ? (
                        <>
                          <div className="flex items-center gap-3 mb-3">
                            <span className={`text-xs font-bold px-2.5 py-1 rounded-full ${
                              consensusOpinion === 'BUY' ? 'bg-green-100 text-green-700' :
                              consensusOpinion === 'SELL' ? 'bg-red-100 text-red-700' :
                              'bg-yellow-100 text-yellow-700'
                            }`}>{consensusOpinion}</span>
                            <span className="text-sm text-gray-700 font-medium">
                              {totalRecent}명 중 {buyCount}명 매수
                              {holdCount > 0 && ` · ${holdCount}명 중립`}
                              {sellCount > 0 && ` · ${sellCount}명 매도`}
                            </span>
                            {upside !== null && (
                              <>
                                <span className="text-gray-300">|</span>
                                <span className={`text-sm font-bold ${upside >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                  {upside >= 0 ? '+' : ''}{upside.toFixed(1)}%
                                </span>
                                <span className="text-xs text-gray-500">평균 목표가 vs 현재가</span>
                              </>
                            )}
                          </div>
                          
                          {/* 목표가 범위 바 */}
                          {minTarget && maxTarget && currentPrice && (
                            <div className="mb-2">
                              <div className="flex justify-between text-xs text-gray-500 mb-1">
                                <span>최저 {formatPrice(minTarget, g.ticker)}</span>
                                <span>● 현재가 {formatPrice(currentPrice, g.ticker)}</span>
                                <span>최고 {formatPrice(maxTarget, g.ticker)}</span>
                              </div>
                              <div className="relative h-2 bg-gradient-to-r from-red-200 via-yellow-200 to-green-200 rounded-full">
                                {/* 현재가 위치 표시 */}
                                <div 
                                  className="absolute top-1/2 -translate-y-1/2 w-3 h-3 bg-blue-600 rounded-full border-2 border-white shadow"
                                  style={{ 
                                    left: `${Math.max(0, Math.min(100, ((currentPrice - minTarget) / (maxTarget - minTarget)) * 100))}%` 
                                  }}
                                />
                              </div>
                              <p className="text-xs text-gray-500 mt-1">
                                최근 90일: ↑ {totalRecent}건 {buyCount > 0 ? `${buyCount}건 매수` : ''}
                              </p>
                            </div>
                          )}
                        </>
                      ) : (
                        <p className="text-xs text-gray-400">최근 3개월 리포트 없음</p>
                      )}
                    </div>

                    {/* 컨센서스 상세 - 테이블 형태 리포트 목록 */}
                    <div className="px-4 pb-3">
                      <h4 className="font-medium text-gray-900 mt-3 mb-3 text-sm flex items-center gap-2">
                        컨센서스 상세 ({g.reports.length}건)
                        <span className="text-xs text-gray-400 font-normal">애널리스트 리포트 전체 목록</span>
                      </h4>
                      
                      {/* 테이블 헤더 */}
                      <div className="hidden sm:grid grid-cols-12 gap-2 text-xs text-gray-500 font-medium pb-2 border-b border-gray-200 mb-1">
                        <div className="col-span-2">날짜</div>
                        <div className="col-span-2">애널리스트</div>
                        <div className="col-span-1 text-center">투자의견</div>
                        <div className="col-span-2 text-center">목표가</div>
                        <div className="col-span-5">제목</div>
                      </div>
                      
                      {g.reports.map((r, i) => (
                        <div 
                          key={i} 
                          className="grid grid-cols-12 gap-2 items-center py-3 border-b border-gray-50 last:border-0 cursor-pointer hover:bg-blue-50/50 rounded transition-colors"
                          onClick={() => openReportModal(r)}
                        >
                          {/* 날짜 */}
                          <div className="col-span-2 sm:col-span-2">
                            <span className="text-xs text-gray-500">{formatDate(r.published_at)}</span>
                          </div>
                          
                          {/* 애널리스트 + 증권사 */}
                          <div className="col-span-3 sm:col-span-2">
                            <p className="text-sm font-medium text-gray-900 truncate">{r.analyst || '-'}</p>
                            <p className="text-xs text-gray-500 truncate">{r.firm}</p>
                          </div>
                          
                          {/* 투자의견 */}
                          <div className="col-span-2 sm:col-span-1 text-center">
                            <OpinionBadge opinion={r.opinion} />
                          </div>
                          
                          {/* 목표가 */}
                          <div className="col-span-2 sm:col-span-2 text-center">
                            <span className="text-sm font-bold text-gray-900">{formatPrice(r.target_price, r.ticker)}</span>
                          </div>
                          
                          {/* 제목 + AI요약 */}
                          <div className="col-span-12 sm:col-span-5 mt-1 sm:mt-0">
                            <p className="text-sm font-medium text-gray-900 truncate">{r.title}</p>
                            {r.summary && (
                              <p className="text-xs text-gray-500 truncate mt-0.5">{r.summary}</p>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
              );
            })}
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
                <button
                  onClick={() => setAnalystSort('return_12m')}
                  className={`text-xs px-2 py-1 rounded-full ${
                    analystSort === 'return_12m'
                      ? 'bg-blue-100 text-blue-700 font-medium'
                      : 'text-gray-500 hover:text-gray-700'
                  }`}
                >
                  12개월 수익률순
                </button>
              </div>
              <p className="text-xs text-gray-500">
                💡 적중률: 목표가 달성 비율 | 수익률: 목표가 대비 현재가 | 12개월 수익률: forward return 12M 평균
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

                          {analyst.avgReturn12m !== 0 && (
                            <div className={`flex items-center gap-1 px-2 py-1 rounded-full border ${
                              analyst.avgReturn12m >= 0 ? 'bg-purple-50 border-purple-200' : 'bg-red-50 border-red-200'
                            }`}>
                              <span className="text-xs">📅</span>
                              <span className={`text-xs font-bold ${analyst.avgReturn12m >= 0 ? 'text-purple-700' : 'text-red-700'}`}>
                                {analyst.avgReturn12m >= 0 ? '+' : ''}{analyst.avgReturn12m}%
                              </span>
                              <span className={`text-[10px] ${analyst.avgReturn12m >= 0 ? 'text-purple-500' : 'text-red-500'}`}>12M</span>
                            </div>
                          )}

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