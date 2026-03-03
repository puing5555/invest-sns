'use client';

import { useState, useMemo } from 'react';
import reportsData from '@/data/analyst_reports.json';
import stockPricesData from '@/data/stockPrices.json';
import StockAnalystChart from '@/components/StockAnalystChart';
import { isKoreanStock } from '@/lib/currency';

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
  code: string;
  onClose: () => void;
}

function formatTargetPrice(price: number | null, ticker?: string): string {
  if (!price) return '-';
  if (ticker && !isKoreanStock(ticker)) return `$${price.toLocaleString()}`;
  return `${Math.floor(price / 10000)}만원`;
}

function formatDate(dateStr: string): string {
  const d = new Date(dateStr);
  const yy = String(d.getFullYear()).slice(2);
  const mm = String(d.getMonth() + 1).padStart(2, '0');
  const dd = String(d.getDate()).padStart(2, '0');
  return `${yy}.${mm}.${dd}`;
}

function OpinionBadge({ opinion }: { opinion: string }) {
  const styles: Record<string, string> = {
    'BUY': 'bg-[#22c55e]/10 text-[#22c55e] border border-[#22c55e]/20',
    'HOLD': 'bg-[#eab308]/10 text-[#eab308] border border-[#eab308]/20',
    'SELL': 'bg-[#ef4444]/10 text-[#ef4444] border border-[#ef4444]/20',
  };
  return (
    <span className={`text-xs font-medium px-2 py-1 rounded-full ${styles[opinion] || styles.HOLD}`}>
      {opinion}
    </span>
  );
}

function AnalystReportModal({ report, code, onClose }: AnalystReportModalProps) {
  if (!report) return null;

  return (
    <>
      <div className="fixed inset-0 bg-black/50 z-50" onClick={onClose} />
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4" onClick={onClose}>
        <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md max-h-[85vh] overflow-y-auto" onClick={(e) => e.stopPropagation()}>
          <div className="sticky top-0 bg-white z-10 px-4 pt-4 pb-2 flex items-center justify-between rounded-t-2xl">
            <div className="flex items-center gap-2">
              <OpinionBadge opinion={report.opinion} />
            </div>
            <div className="flex items-center gap-1">
              <button className="text-[#8b95a1] hover:text-red-400 transition-colors text-lg px-3 py-2 rounded-lg">♡</button>
              <button className="text-[#8b95a1] hover:text-red-500 transition-colors text-sm px-2 py-1 rounded-lg">🚨</button>
              <button onClick={onClose} className="w-8 h-8 flex items-center justify-center rounded-full hover:bg-[#f8f9fa] transition-colors text-[#8b95a1] text-lg">✕</button>
            </div>
          </div>

          <div className="px-5 pb-5 space-y-4">
            <div>
              <h2 className="text-lg font-bold text-[#191f28] leading-snug">{report.title}</h2>
              <p className="text-sm text-[#8b95a1] mt-1">{formatDate(report.published_at)}</p>
            </div>

            {/* 요약: 라벨 없이 텍스트만 */}
            <div className="bg-[#f8f9fa] rounded-xl p-4 border-l-4 border-[#3182f6]">
              <p className="text-[15px] text-[#191f28] leading-relaxed">
                {report.summary || <span className="text-[#8b95a1]">리포트 요약 준비 중</span>}
              </p>
            </div>

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
                <span className="text-sm font-medium text-[#191f28]">{formatTargetPrice(report.target_price, code)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-[#8b95a1]">투자의견</span>
                <span className="text-sm font-medium text-[#191f28]">{report.opinion}</span>
              </div>
            </div>

            <div>
              {report.pdf_url && (
                <a href={report.pdf_url} target="_blank" rel="noopener noreferrer" className="w-full text-center bg-[#ff0000] hover:bg-[#cc0000] text-white font-medium py-3.5 rounded-xl transition-colors text-[15px] block">
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

export default function StockAnalystTab({ code }: StockAnalystTabProps) {
  const [selectedReport, setSelectedReport] = useState<Report | null>(null);

  const data = reportsData as Record<string, Report[]>;
  const reports = data[code] || [];

  const currentPrice = useMemo(() => {
    try {
      const stockData = (stockPricesData as any)[code];
      return stockData?.currentPrice || 0;
    } catch { return 0; }
  }, [code]);

  const sortedReports = useMemo(() =>
    [...reports].sort((a, b) => b.published_at.localeCompare(a.published_at)),
    [reports]
  );

  return (
    <div className="space-y-6">
      <StockAnalystChart
        code={code}
        signals={reports.map(r => ({
          date: r.published_at,
          signal: r.opinion,
          target_price: r.target_price,
          firm: r.firm,
          analyst: r.analyst,
          title: r.title,
        }))}
        currentPrice={currentPrice}
      />

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
                  <th className="px-4 py-3 text-left text-sm font-medium text-[#8b95a1]">애널리스트</th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-[#8b95a1]">증권사</th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-[#8b95a1]">투자의견</th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-[#8b95a1]">리포트 제목</th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-[#8b95a1]">목표가</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#f0f0f0]">
                {sortedReports.map((report, index) => (
                  <tr key={index} className="hover:bg-[#f8f9fa] transition-colors cursor-pointer" onClick={() => setSelectedReport(report)}>
                    <td className="px-4 py-4 text-sm text-[#191f28] whitespace-nowrap">{formatDate(report.published_at)}</td>
                    <td className="px-4 py-4 text-sm text-[#191f28] whitespace-nowrap">{report.analyst || '-'}</td>
                    <td className="px-4 py-4 text-sm text-[#191f28] whitespace-nowrap">{report.firm}</td>
                    <td className="px-4 py-4"><OpinionBadge opinion={report.opinion} /></td>
                    <td className="px-4 py-4 text-sm max-w-xs">
                      <div className="text-[#191f28] font-medium truncate hover:text-[#3182f6] transition-colors">{report.title}</div>
                    </td>
                    <td className="px-4 py-4 text-sm text-[#191f28] font-medium whitespace-nowrap">{formatTargetPrice(report.target_price, code)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {selectedReport && (
        <AnalystReportModal report={selectedReport} code={code} onClose={() => setSelectedReport(null)} />
      )}
    </div>
  );
}
