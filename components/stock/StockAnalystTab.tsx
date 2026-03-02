'use client';

import { useState, useMemo } from 'react';
import reportsData from '@/data/analyst_reports.json';
import stockPricesData from '@/data/stockPrices.json';
import StockAnalystChart from '@/components/StockAnalystChart';

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
}

interface StockAnalystTabProps {
  code: string;
}

interface AnalystReportModalProps {
  report: Report;
  onClose: () => void;
}

// 목표가 포맷팅 함수
function formatTargetPrice(price: number | null): string {
  if (!price) return '-';
  return `${Math.floor(price / 10000)}만원`;
}

// 날짜 포맷팅 (26.02.24)
function formatDate(dateStr: string): string {
  const d = new Date(dateStr);
  const yy = String(d.getFullYear()).slice(2);
  const mm = String(d.getMonth() + 1).padStart(2, '0');
  const dd = String(d.getDate()).padStart(2, '0');
  return `${yy}.${mm}.${dd}`;
}

function AnalystReportModal({ report, onClose }: AnalystReportModalProps) {
  if (!report) return null;
  
  return (
    <>
      {/* Overlay */}
      <div className="fixed inset-0 bg-black/50 z-50" onClick={onClose} />
      
      {/* Modal */}
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4" onClick={onClose}>
        <div
          className="bg-white rounded-2xl shadow-2xl w-full max-w-md max-h-[85vh] overflow-y-auto"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Top bar: Opinion badge (left) / Like·Report·X (right) */}
          <div className="sticky top-0 bg-white z-10 px-4 pt-4 pb-2 flex items-center justify-between rounded-t-2xl">
            <div className="flex items-center gap-2">
              <OpinionBadge opinion={report.opinion} />
            </div>
            <div className="flex items-center gap-1">
              <button className="text-[#8b95a1] hover:text-red-400 transition-colors text-lg px-3 py-2 rounded-lg">
                ♡
              </button>
              <button className="text-[#8b95a1] hover:text-red-500 transition-colors text-sm px-2 py-1 rounded-lg">
                🚨
              </button>
              <button
                onClick={onClose}
                className="w-8 h-8 flex items-center justify-center rounded-full hover:bg-[#f8f9fa] transition-colors text-[#8b95a1] text-lg"
              >
                ✕
              </button>
            </div>
          </div>

          <div className="px-5 pb-5 space-y-4">
            {/* 리포트 제목 + 날짜 */}
            <div>
              <h2 className="text-lg font-bold text-[#191f28] leading-snug">
                {report.title}
              </h2>
              <p className="text-sm text-[#8b95a1] mt-1">
                {formatDate(report.published_at)}
              </p>
            </div>

            {/* AI 한줄요약 */}
            {report.summary && (
              <div className="bg-[#f8f9fa] rounded-xl p-4 border-l-4 border-[#3182f6]">
                <div className="text-xs font-medium text-[#8b95a1] mb-2">🤖 AI 한줄요약</div>
                <p className="text-[15px] text-[#191f28] leading-relaxed">
                  {report.summary}
                </p>
              </div>
            )}

            {/* 상세 정보 */}
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-sm text-[#8b95a1]">증권사</span>
                <span className="text-sm font-medium text-[#191f28]">{report.firm}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-[#8b95a1]">애널리스트</span>
                <span className="text-sm font-medium text-[#191f28]">{report.analyst || '-'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-[#8b95a1]">목표가</span>
                <span className="text-sm font-medium text-[#191f28]">{formatTargetPrice(report.target_price)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-[#8b95a1]">투자의견</span>
                <span className="text-sm font-medium text-[#191f28]">{report.opinion}</span>
              </div>
            </div>

            {/* PDF 보기 버튼 */}
            <div>
              {report.pdf_url && (
                <a
                  href={report.pdf_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="w-full text-center bg-[#ff0000] hover:bg-[#cc0000] text-white font-medium py-3.5 rounded-xl transition-colors text-[15px] block"
                >
                  📄 PDF 보기
                </a>
              )}
            </div>
          </div>
        </div>
      </div>
    </>
  );
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

export default function StockAnalystTab({ code }: StockAnalystTabProps) {
  const [selectedReport, setSelectedReport] = useState<Report | null>(null);
  
  const data = reportsData as Record<string, Report[]>;
  const reports = data[code] || [];
  
  // 현재 주가
  const currentPrice = useMemo(() => {
    try {
      const stockData = (stockPricesData as any)[code];
      return stockData?.currentPrice || 0;
    } catch { return 0; }
  }, [code]);

  // 증권사별 최신 목표가 (바 차트용)
  const firmTargets = useMemo(() => {
    const firmMap: Record<string, { firm: string; target_price: number; opinion: string; date: string }> = {};
    const sorted = [...reports].sort((a, b) => a.published_at.localeCompare(b.published_at));
    for (const r of sorted) {
      if (r.target_price && r.target_price > 0) {
        firmMap[r.firm] = { firm: r.firm, target_price: r.target_price, opinion: r.opinion, date: r.published_at };
      }
    }
    return Object.values(firmMap).sort((a, b) => b.target_price - a.target_price);
  }, [reports]);
  
  const sortedReports = useMemo(() => 
    [...reports].sort((a, b) => b.published_at.localeCompare(a.published_at)),
    [reports]
  );

  // 애널리스트 리포트를 시그널 형태로 변환
  const analystSignals = useMemo(() => {
    return reports.map((report) => ({
      id: `analyst-${report.ticker}-${report.published_at}`,
      signal_type: report.opinion === 'BUY' ? '매수' : 
                   report.opinion === 'HOLD' ? '중립' : 
                   report.opinion === 'SELL' ? '매도' : '중립',
      date: report.published_at,
      speaker: report.firm,
      timestamp: report.published_at
    }));
  }, [reports]);

  return (
    <div className="space-y-6">
      {/* 주가 차트 & 애널리스트 시그널 */}
      <StockAnalystChart
        code={code}
        signals={reports.map(r => ({
          date: r.published_at,
          signal: r.opinion,
          target_price: r.target_price,
          firm: r.firm
        }))}
        currentPrice={currentPrice}
      />

      {/* 리포트 테이블 */}
      <div className="bg-white rounded-xl shadow-sm border border-[#e8e8e8] overflow-hidden">
        <div className="p-6 border-b border-[#e8e8e8]">
          <h4 className="font-bold text-[#191f28]">애널리스트 리포트</h4>
        </div>
        
        {sortedReports.length === 0 ? (
          <div className="p-12 text-center">
            <div className="text-4xl mb-4">📊</div>
            <h3 className="text-lg font-bold text-[#191f28] mb-2">리포트 없음</h3>
            <p className="text-[#8b95a1]">이 종목에 대한 애널리스트 리포트가 없습니다</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-[#f8f9fa]">
                <tr>
                  <th className="px-4 py-3 text-left text-sm font-medium text-[#8b95a1]">날짜</th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-[#8b95a1]">투자의견</th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-[#8b95a1]">리포트</th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-[#8b95a1]">목표가</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#f0f0f0]">
                {sortedReports.map((report, index) => (
                  <tr key={index} className="hover:bg-[#f8f9fa] transition-colors cursor-pointer" onClick={() => setSelectedReport(report)}>
                    <td className="px-4 py-4 text-sm text-[#191f28] whitespace-nowrap">
                      {formatDate(report.published_at)}
                    </td>
                    <td className="px-4 py-4">
                      <OpinionBadge opinion={report.opinion} />
                    </td>
                    <td className="px-4 py-4 text-sm max-w-xs">
                      <div className="group">
                        <div className="text-[#191f28] font-medium truncate group-hover:text-[#3182f6] transition-colors">
                          {report.title}
                          {report.pdf_url && (
                            <a 
                              href={report.pdf_url} 
                              target="_blank" 
                              rel="noopener noreferrer" 
                              onClick={(e) => e.stopPropagation()}
                              className="ml-2 text-[#3182f6] hover:text-[#2171e5] text-xs"
                            >
                              📄
                            </a>
                          )}
                        </div>
                        {report.summary && (
                          <div className="text-xs text-[#8b95a1] mt-1 truncate">
                            {report.summary}
                          </div>
                        )}
                      </div>
                    </td>
                    <td className="px-4 py-4 text-sm text-[#191f28] font-medium whitespace-nowrap">
                      {formatTargetPrice(report.target_price)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
      
      {/* 애널리스트 리포트 모달 */}
      {selectedReport && (
        <AnalystReportModal
          report={selectedReport}
          onClose={() => setSelectedReport(null)}
        />
      )}
    </div>
  );
}