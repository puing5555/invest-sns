'use client';

import { useState, useMemo } from 'react';
import reportsData from '@/data/analyst_reports.json';

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
  title: string;
  target_price: number;
  opinion: string;
  published_at: string;
  pdf_url: string;
}

const data = reportsData as Record<string, Report[]>;

const allReports: Report[] = Object.values(data).flat();

function OpinionBadge({ opinion }: { opinion: string }) {
  const color = opinion === 'BUY' ? 'bg-green-100 text-green-700'
    : opinion === 'SELL' ? 'bg-red-100 text-red-700'
    : opinion === 'HOLD' ? 'bg-yellow-100 text-yellow-700'
    : 'bg-gray-100 text-gray-600';
  return <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${color}`}>{opinion}</span>;
}

function formatPrice(n: number) {
  return n.toLocaleString('ko-KR') + '원';
}

export default function AnalystPage() {
  const [activeTab, setActiveTab] = useState('latest');
  const [search, setSearch] = useState('');
  const q = search.toLowerCase();

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

  const tabs = [
    { id: 'latest', label: '🔥 최신 리포트' },
    { id: 'firm', label: '👩‍💼 증권사별' },
    { id: 'stock', label: '📈 종목별' },
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
              <div key={i} className="bg-white rounded-xl p-4 shadow-sm">
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-xs text-gray-400">{r.published_at}</span>
                      <OpinionBadge opinion={r.opinion} />
                    </div>
                    <p className="font-medium text-gray-900 text-sm truncate">{r.title}</p>
                    <div className="flex items-center gap-2 mt-1">
                      <span className="text-xs text-blue-600 font-medium">{TICKER_NAMES[r.ticker] || r.ticker}</span>
                      <span className="text-xs text-gray-400">·</span>
                      <span className="text-xs text-gray-500">{r.firm}</span>
                      <span className="text-xs text-gray-400">·</span>
                      <span className="text-xs text-gray-700 font-medium">목표 {formatPrice(r.target_price)}</span>
                    </div>
                  </div>
                  <a href={r.pdf_url} target="_blank" rel="noopener noreferrer" className="ml-2 text-lg hover:scale-110 transition-transform">📄</a>
                </div>
              </div>
            ))}
            {filteredReports.length === 0 && <p className="text-center text-gray-400 py-10 text-sm">검색 결과가 없습니다</p>}
          </div>
        )}

        {/* 👩‍💼 증권사별 */}
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
                  <div className="border-t border-gray-100 px-4 pb-3">
                    {g.reports.slice(0, 20).map((r, i) => (
                      <div key={i} className="flex items-center justify-between py-2 border-b border-gray-50 last:border-0">
                        <div className="flex-1 min-w-0">
                          <p className="text-sm text-gray-800 truncate">{r.title}</p>
                          <div className="flex items-center gap-2 mt-0.5">
                            <span className="text-xs text-gray-500">{r.firm}</span>
                            <span className="text-xs text-gray-400">{r.published_at}</span>
                            <OpinionBadge opinion={r.opinion} />
                            <span className="text-xs text-gray-700">목표 {formatPrice(r.target_price)}</span>
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
      </div>
    </div>
  );
}
