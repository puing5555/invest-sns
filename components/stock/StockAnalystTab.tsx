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
  ai_detail?: string;
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

// AI Detail 파서 & 렌더러
function parseAiDetail(content: string) {
  const sections: { title: string; content: string }[] = [];
  const lines = content.split('\n');
  let currentSection: { title: string; content: string } | null = null;

  for (const line of lines) {
    const trimmed = line.trim();
    if (trimmed.startsWith('## ')) {
      if (currentSection) sections.push(currentSection);
      currentSection = { title: trimmed.slice(3).trim(), content: '' };
    } else if (currentSection && trimmed) {
      currentSection.content += (currentSection.content ? '\n' : '') + trimmed;
    }
  }
  if (currentSection) sections.push(currentSection);
  return sections;
}

function getSectionIcon(title: string) {
  const iconMap: Record<string, string> = {
    '투자포인트': '📌', '실적전망': '📊', '밸류에이션': '💰', '리스크': '⚠️', '결론': '✅'
  };
  return iconMap[title] || '📄';
}

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
          <p className="text-sm text-gray-700 leading-relaxed whitespace-pre-line">{section.content}</p>
        </div>
      ))}
    </div>
  );
}

const TICKER_NAMES: Record<string, string> = {
  '005930': '삼성전자', '000660': 'SK하이닉스', '005380': '현대차', '006400': '삼성SDI',
  '051910': 'LG화학', '035420': 'NAVER', '036570': '엔씨소프트', '005940': 'NH투자증권',
  '009540': 'HD한국조선해양', '016360': '삼성증권', '036930': '주성엔지니어링',
  '039490': '키움증권', '042700': '한미반도체', '071050': '한국금융지주', '079160': 'CJ CGV',
  '084370': '유진테크', '086520': '에코프로', '090430': '아모레퍼시픽', '095610': '테스',
  '240810': '원익IPS', '267260': 'HD현대일렉트릭', '284620': '카카오헬스케어',
  '298040': '효성중공업', '352820': '하이브', '357780': '솔브레인', '399720': '가온칩스',
  '403870': 'HPSP', '004170': '신세계', '000720': '현대건설', '095610': '테스',
};

function AnalystReportModal({ report, code, onClose }: AnalystReportModalProps) {
  if (!report) return null;

  const stockName = TICKER_NAMES[code] || code;

  return (
    <>
      <div className="fixed inset-0 bg-black/50 z-50" onClick={onClose} />
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4" onClick={onClose}>
        <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg max-h-[85vh] overflow-y-auto" onClick={(e) => e.stopPropagation()}>
          <div className="p-6">
            {/* 헤더 */}
            <div className="flex items-start justify-between mb-4">
              <h2 className="text-lg font-bold text-gray-900">리포트 상세</h2>
              <button onClick={onClose} className="text-gray-400 hover:text-gray-600 text-xl">✕</button>
            </div>

            <div className="space-y-4">
              {/* 제목 + 종목/의견 */}
              <div>
                <h3 className="font-medium text-gray-900 mb-2">{report.title}</h3>
                <div className="flex items-center gap-2 mb-3">
                  <span className="text-sm font-medium text-blue-600">{stockName}</span>
                  <OpinionBadge opinion={report.opinion} />
                </div>
              </div>

              {/* 정보 그리드 */}
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-gray-500">증권사</span>
                  <p className="font-medium">{report.firm}</p>
                </div>
                <div>
                  <span className="text-gray-500">애널리스트</span>
                  <p className="font-medium">{report.analyst || '-'}</p>
                </div>
                <div>
                  <span className="text-gray-500">목표가</span>
                  <p className="font-medium">{formatTargetPrice(report.target_price, code)}</p>
                </div>
                <div>
                  <span className="text-gray-500">투자의견</span>
                  <p className="font-medium">{report.opinion}</p>
                </div>
                <div className="col-span-2">
                  <span className="text-gray-500">발행일</span>
                  <p className="font-medium">{formatDate(report.published_at)}</p>
                </div>
              </div>

              {/* AI 한줄요약 */}
              {report.summary && (
                <div>
                  <span className="text-gray-500 text-sm">AI 한줄요약</span>
                  <p className="text-sm text-gray-700 mt-1 p-3 bg-blue-50 rounded-lg font-medium">
                    {report.summary}
                  </p>
                </div>
              )}

              {/* AI 상세 분석 - 섹션 카드 */}
              {report.ai_detail && (
                <div>
                  <span className="text-gray-500 text-sm">상세 분석</span>
                  <div className="mt-1">
                    <AiDetailRenderer content={report.ai_detail} />
                  </div>
                </div>
              )}

              {/* PDF 링크 */}
              {report.pdf_url && (
                <div className="pt-4 border-t">
                  <a href={report.pdf_url} target="_blank" rel="noopener noreferrer"
                    className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg flex items-center justify-center gap-2 hover:bg-blue-700 transition-colors">
                    📄 PDF 보고서 보기
                  </a>
                </div>
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
                  <th className="px-4 py-3 text-left text-sm font-medium text-[#8b95a1]">투자의견</th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-[#8b95a1]">리포트</th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-[#8b95a1]">목표가</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#f0f0f0]">
                {sortedReports.map((report, index) => (
                  <tr key={index} className="hover:bg-[#f8f9fa] transition-colors cursor-pointer" onClick={() => setSelectedReport(report)}>
                    <td className="px-4 py-4 text-sm text-[#191f28] whitespace-nowrap">{formatDate(report.published_at)}</td>
                    <td className="px-4 py-4 text-sm text-[#191f28] whitespace-nowrap">
                      <div>{report.analyst || '-'}</div>
                      <div className="text-xs text-[#8b95a1]">{report.firm}</div>
                    </td>
                    <td className="px-4 py-4"><OpinionBadge opinion={report.opinion} /></td>
                    <td className="px-4 py-4 text-sm max-w-md">
                      <div className="text-[#191f28] font-medium truncate hover:text-[#3182f6] transition-colors">{report.title}</div>
                      {report.summary && <div className="text-xs text-[#8b95a1] mt-0.5 truncate">{report.summary}</div>}
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
