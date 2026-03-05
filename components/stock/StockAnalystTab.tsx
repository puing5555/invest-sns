'use client';

import { useState, useMemo } from 'react';
import reportsData from '@/data/analyst_reports.json';
import stockPricesData from '@/data/stockPrices.json';
import StockAnalystChart from '@/components/StockAnalystChart';
import { isKoreanStock } from '@/lib/currency';
import { insertSignalReport, insertSignalVote } from '@/lib/supabase';

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
  const [liked, setLiked] = useState(false);
  const [likeCount, setLikeCount] = useState(0);
  const [showReportModal, setShowReportModal] = useState(false);
  const [reportReason, setReportReason] = useState('');
  const [reportDetail, setReportDetail] = useState('');
  const [isSubmittingReport, setIsSubmittingReport] = useState(false);

  if (!report) return null;

  const stockName = TICKER_NAMES[code] || code;
  const reportId = `report-${code}-${report.published_at}-${report.firm}`;

  const handleLike = async () => {
    if (liked) { setLiked(false); return; }
    try {
      await insertSignalVote(reportId);
      setLiked(true);
      setLikeCount(prev => prev + 1);
    } catch (error) {
      console.error('좋아요 처리 중 오류:', error);
    }
  };

  const handleReport = () => setShowReportModal(true);

  const handleReportSubmit = async () => {
    if (!reportReason) { alert('신고 사유를 선택해주세요.'); return; }
    if (reportDetail.trim().length < 10) { alert('상세 사유를 최소 10자 이상 입력해주세요.'); return; }
    setIsSubmittingReport(true);
    try {
      await insertSignalReport(reportId, reportReason, reportDetail.trim());
      alert('신고가 접수되었습니다.');
      setShowReportModal(false);
      setReportReason('');
      setReportDetail('');
    } catch (error) {
      console.error('신고 처리 중 오류:', error);
      alert('신고 접수에 실패했습니다.');
    } finally {
      setIsSubmittingReport(false);
    }
  };

  return (
    <>
      <div className="fixed inset-0 bg-black/50 z-50" onClick={onClose} />
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4" onClick={onClose}>
        <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg max-h-[85vh] overflow-y-auto" onClick={(e) => e.stopPropagation()}>
          <div className="p-6">
            {/* 헤더 */}
            <div className="flex items-start justify-between mb-4">
              <h2 className="text-lg font-bold text-gray-900">리포트 상세</h2>
              <div className="flex items-center gap-1">
                <button
                  onClick={handleLike}
                  className={`transition-colors text-2xl px-4 py-3 rounded-lg flex items-center gap-1 border-none outline-none ${liked ? 'text-red-500' : 'text-[#8b95a1] hover:text-red-400'}`}
                >
                  {liked ? '❤️' : '♡'}{likeCount > 0 && <span className="text-base">{likeCount}</span>}
                </button>
                <button
                  onClick={handleReport}
                  className="text-[#8b95a1] hover:text-red-500 transition-colors text-xl px-3 py-2 rounded-lg"
                >
                  🚨
                </button>
                <button onClick={onClose} className="w-8 h-8 flex items-center justify-center rounded-full hover:bg-[#f8f9fa] transition-colors text-[#8b95a1] text-lg">✕</button>
              </div>
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

              {/* 신고 모달 */}
              {showReportModal && (
                <div className="fixed inset-0 bg-black/50 z-[60] flex items-center justify-center p-4" onClick={() => { setShowReportModal(false); setReportReason(''); setReportDetail(''); }}>
                  <div className="bg-white rounded-xl p-5 w-full max-w-sm" onClick={(e) => e.stopPropagation()}>
                    <h3 className="text-lg font-bold text-[#191f28] mb-4">리포트 신고</h3>
                    <div className="space-y-3 mb-4">
                      {['내용 오류', '목표가 틀림', '종목 오류', '기타'].map((reason) => (
                        <label key={reason} className="flex items-center gap-3 cursor-pointer">
                          <input type="radio" name="reportReason" value={reason} checked={reportReason === reason}
                            onChange={(e) => { setReportReason(e.target.value); setReportDetail(''); }}
                            className="w-4 h-4 text-[#3182f6]" />
                          <span className="text-sm text-[#191f28]">{reason}</span>
                        </label>
                      ))}
                    </div>
                    {reportReason && (
                      <div className="mb-4">
                        <textarea value={reportDetail} onChange={(e) => setReportDetail(e.target.value)}
                          placeholder="상세 사유를 입력해주세요"
                          className="w-full border border-gray-300 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-[#3182f6]"
                          style={{ padding: '8px', fontSize: '14px', lineHeight: '1.5' }} rows={4} />
                        {reportDetail.length > 0 && reportDetail.length < 10 && (
                          <p className="text-xs mt-1" style={{ color: '#ef4444' }}>최소 10자 이상 입력해주세요 ({reportDetail.length}/10)</p>
                        )}
                      </div>
                    )}
                    <div className="flex gap-2">
                      <button onClick={() => { setShowReportModal(false); setReportReason(''); setReportDetail(''); }}
                        className="flex-1 py-2.5 text-sm text-[#8b95a1] bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors">취소</button>
                      <button onClick={handleReportSubmit}
                        disabled={isSubmittingReport || !reportReason || reportDetail.length < 10}
                        className="flex-1 py-2.5 text-sm text-white bg-[#3182f6] rounded-lg hover:bg-[#1b64da] disabled:opacity-50 disabled:cursor-not-allowed transition-colors">
                        {isSubmittingReport ? '처리 중...' : '신고'}
                      </button>
                    </div>
                  </div>
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
  const [showDetails, setShowDetails] = useState(false);

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

  // 컨센서스 계산
  const consensus = useMemo(() => {
    if (reports.length === 0) return null;
    
    const opinions = reports.reduce((acc, report) => {
      acc[report.opinion] = (acc[report.opinion] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    const total = reports.length;
    const buyCount = opinions.BUY || 0;
    const holdCount = opinions.HOLD || 0;
    const sellCount = opinions.SELL || 0;

    let dominantOpinion = 'HOLD';
    if (buyCount > holdCount && buyCount > sellCount) dominantOpinion = 'BUY';
    else if (sellCount > buyCount && sellCount > holdCount) dominantOpinion = 'SELL';

    return {
      opinion: dominantOpinion,
      buyCount,
      holdCount,
      sellCount,
      total,
      text: `${total}명 중 ${buyCount}명 매수`
    };
  }, [reports]);

  // 평균 목표가 및 업사이드 계산
  const targetPriceStats = useMemo(() => {
    const validReports = reports.filter(r => r.target_price && r.target_price > 0);
    if (validReports.length === 0 || currentPrice === 0) return null;

    const targetPrices = validReports.map(r => r.target_price!);
    const avgTarget = targetPrices.reduce((sum, price) => sum + price, 0) / targetPrices.length;
    const minTarget = Math.min(...targetPrices);
    const maxTarget = Math.max(...targetPrices);
    
    const upside = ((avgTarget - currentPrice) / currentPrice) * 100;
    
    return {
      avgTarget,
      minTarget,
      maxTarget,
      upside,
      upsideColor: upside >= 20 ? 'text-green-600 bg-green-50' : 
                   upside <= -10 ? 'text-red-600 bg-red-50' : 
                   'text-gray-600 bg-gray-50'
    };
  }, [reports, currentPrice]);

  // 최근 변화 (30일 내 목표가 변화)
  const recentChanges = useMemo(() => {
    const thirtyDaysAgo = new Date();
    thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
    
    // 간단화: 최근 30일 내 리포트 중 BUY와 SELL 개수로 상향/하향 판단
    const recentReports = reports.filter(r => new Date(r.published_at) >= thirtyDaysAgo);
    const upgrades = recentReports.filter(r => r.opinion === 'BUY').length;
    const downgrades = recentReports.filter(r => r.opinion === 'SELL').length;
    
    return { upgrades, downgrades };
  }, [reports]);

  if (reports.length === 0) {
    return (
      <div className="space-y-6">
        <div className="bg-white rounded-xl shadow-sm border border-[#e8e8e8] p-12 text-center">
          <div className="text-4xl mb-4">📊</div>
          <h3 className="text-lg font-bold text-[#191f28] mb-2">리포트 없음</h3>
          <p className="text-[#8b95a1]">이 종목에 대한 애널리스트 리포트가 없습니다</p>
        </div>
      </div>
    );
  }

  const latestReport = sortedReports[0];

  return (
    <div className="space-y-6">
      {/* 컨센서스 요약 카드 */}
      <div className="bg-white rounded-2xl shadow-sm border border-[#e8e8e8] p-6">
        <div className="flex items-start justify-between mb-6">
          <div>
            <h3 className="text-lg font-bold text-[#191f28] mb-2">애널리스트 컨센서스</h3>
            <p className="text-sm text-[#8b95a1]">전문가들은 이 종목을 어떻게 보고 있을까요?</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* 컨센서스 뱃지 */}
          <div className="space-y-4">
            {consensus && (
              <div className="flex items-center gap-4">
                <div className={`px-6 py-3 rounded-2xl font-bold text-lg ${
                  consensus.opinion === 'BUY' ? 'bg-green-100 text-green-700' :
                  consensus.opinion === 'SELL' ? 'bg-red-100 text-red-700' :
                  'bg-yellow-100 text-yellow-700'
                }`}>
                  {consensus.opinion}
                </div>
                <div className="text-[#191f28] font-medium">
                  {consensus.text}
                </div>
              </div>
            )}

            {/* 업사이드/다운사이드 */}
            {targetPriceStats && (
              <div className="flex items-center gap-3">
                <div className={`px-4 py-2 rounded-xl font-bold text-xl ${targetPriceStats.upsideColor}`}>
                  {targetPriceStats.upside >= 0 ? '+' : ''}{targetPriceStats.upside.toFixed(1)}%
                </div>
                <div className="text-sm text-[#8b95a1]">
                  평균 목표가 vs 현재가
                </div>
              </div>
            )}
          </div>

          {/* 최신 리포트 */}
          <div className="bg-gray-50 rounded-xl p-4">
            <h4 className="text-sm font-medium text-[#8b95a1] mb-2">최신 리포트</h4>
            <div 
              className="cursor-pointer"
              onClick={() => setSelectedReport(latestReport)}
            >
              <p className="text-sm font-medium text-[#191f28] hover:text-blue-600 transition-colors mb-1">
                {latestReport.title}
              </p>
              <div className="flex items-center gap-2 text-xs text-[#8b95a1]">
                <span>{latestReport.analyst || '-'}</span>
                <span>·</span>
                <span>{latestReport.firm}</span>
                <span>·</span>
                <span>{formatDate(latestReport.published_at)}</span>
              </div>
            </div>
          </div>
        </div>

        {/* 목표가 범위 */}
        {targetPriceStats && (
          <div className="mt-6 p-4 bg-gray-50 rounded-xl">
            <h4 className="text-sm font-medium text-[#8b95a1] mb-3">목표가 범위</h4>
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="text-[#8b95a1]">최저</span>
                <span className="font-medium text-[#191f28]">{formatTargetPrice(targetPriceStats.minTarget, code)}</span>
              </div>
              <div className="relative h-2 bg-gray-200 rounded-full">
                {/* 현재가 위치 표시 */}
                <div 
                  className="absolute top-0 w-1 h-2 bg-blue-600 rounded-full"
                  style={{
                    left: `${Math.min(100, Math.max(0, 
                      ((currentPrice - targetPriceStats.minTarget) / 
                       (targetPriceStats.maxTarget - targetPriceStats.minTarget)) * 100
                    ))}%`
                  }}
                />
                <div className="absolute top-0 left-0 w-full h-2 bg-gradient-to-r from-red-200 via-yellow-200 to-green-200 rounded-full opacity-60" />
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-[#8b95a1]">최고</span>
                <span className="font-medium text-[#191f28]">{formatTargetPrice(targetPriceStats.maxTarget, code)}</span>
              </div>
              <div className="text-center text-xs text-[#8b95a1] mt-2">
                <span className="inline-flex items-center gap-1">
                  <div className="w-2 h-2 bg-blue-600 rounded-full" />
                  현재가 {formatTargetPrice(currentPrice, code)}
                </span>
              </div>
            </div>
          </div>
        )}

        {/* 최근 변화 */}
        <div className="mt-4 flex items-center gap-4">
          <h4 className="text-sm font-medium text-[#8b95a1]">최근 30일 변화:</h4>
          <div className="flex items-center gap-3">
            {recentChanges.upgrades > 0 && (
              <div className="flex items-center gap-1 text-green-600">
                <span>↑</span>
                <span className="text-sm font-medium">{recentChanges.upgrades}건 상향</span>
              </div>
            )}
            {recentChanges.downgrades > 0 && (
              <div className="flex items-center gap-1 text-red-600">
                <span>↓</span>
                <span className="text-sm font-medium">{recentChanges.downgrades}건 하향</span>
              </div>
            )}
            {recentChanges.upgrades === 0 && recentChanges.downgrades === 0 && (
              <span className="text-sm text-[#8b95a1]">변화 없음</span>
            )}
          </div>
        </div>
      </div>

      {/* 증권사 상세 (아코디언) */}
      <div className="bg-white rounded-xl shadow-sm border border-[#e8e8e8]">
        <button
          onClick={() => setShowDetails(!showDetails)}
          className="w-full px-6 py-4 flex items-center justify-between text-left hover:bg-gray-50 transition-colors"
        >
          <div>
            <h4 className="font-bold text-[#191f28]">증권사별 상세 ({reports.length}건)</h4>
            <p className="text-sm text-[#8b95a1] mt-1">애널리스트 리포트 전체 목록</p>
          </div>
          <span className={`text-[#8b95a1] transition-transform ${showDetails ? 'rotate-180' : ''}`}>
            ▼
          </span>
        </button>
        
        {showDetails && (
          <div className="border-t border-[#e8e8e8]">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-[#f8f9fa]">
                  <tr>
                    <th className="px-4 py-3 text-left text-sm font-medium text-[#8b95a1]">증권사</th>
                    <th className="px-4 py-3 text-left text-sm font-medium text-[#8b95a1]">애널리스트</th>
                    <th className="px-4 py-3 text-left text-sm font-medium text-[#8b95a1]">목표가</th>
                    <th className="px-4 py-3 text-left text-sm font-medium text-[#8b95a1]">투자의견</th>
                    <th className="px-4 py-3 text-left text-sm font-medium text-[#8b95a1]">날짜</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#f0f0f0]">
                  {sortedReports.map((report, index) => (
                    <tr 
                      key={index} 
                      className="hover:bg-[#f8f9fa] transition-colors cursor-pointer" 
                      onClick={() => setSelectedReport(report)}
                    >
                      <td className="px-4 py-4 text-sm text-[#191f28] font-medium">{report.firm}</td>
                      <td className="px-4 py-4 text-sm text-[#191f28]">{report.analyst || '-'}</td>
                      <td className="px-4 py-4 text-sm text-[#191f28] font-medium">
                        {formatTargetPrice(report.target_price, code)}
                      </td>
                      <td className="px-4 py-4"><OpinionBadge opinion={report.opinion} /></td>
                      <td className="px-4 py-4 text-sm text-[#8b95a1]">{formatDate(report.published_at)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>

      {selectedReport && (
        <AnalystReportModal report={selectedReport} code={code} onClose={() => setSelectedReport(null)} />
      )}
    </div>
  );
}
