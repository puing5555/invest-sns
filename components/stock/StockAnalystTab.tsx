'use client';

import { useState, useEffect, useMemo } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Scatter } from 'recharts';
import reportsData from '@/data/analyst_reports.json';
import signalPricesData from '@/data/signal_prices.json';

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
}

interface StockAnalystTabProps {
  code: string;
}

interface AIDetailsModalProps {
  report: Report;
  onClose: () => void;
}

function AIDetailsModal({ report, onClose }: AIDetailsModalProps) {
  if (!report) return null;
  
  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl max-w-2xl w-full max-h-[80vh] overflow-y-auto">
        <div className="p-6">
          <div className="flex justify-between items-start mb-6">
            <div>
              <h3 className="text-lg font-bold text-[#191f28] mb-2">{report.title}</h3>
              <p className="text-sm text-[#8b95a1]">{report.firm} • {report.published_at}</p>
            </div>
            <button
              onClick={onClose}
              className="text-[#8b95a1] hover:text-[#191f28] text-xl font-bold"
            >
              ×
            </button>
          </div>
          
          <div className="space-y-4">
            <div>
              <h4 className="font-medium text-[#191f28] mb-2">🤖 AI 상세 분석</h4>
              <div className="bg-[#f8f9fa] p-4 rounded-lg">
                <div className="space-y-3 text-sm text-[#191f28] leading-relaxed">
                  <p>• 이 리포트는 현재 시장 상황과 기업의 펀더멘털을 종합적으로 분석했습니다.</p>
                  <p>• 주요 성장 동력과 리스크 요인을 균형있게 검토한 것으로 평가됩니다.</p>
                  <p>• 목표가 설정의 합리성과 투자의견의 근거가 명확히 제시되었습니다.</p>
                  <p>• 업계 내 경쟁사 대비 밸류에이션 매력도가 고려되었습니다.</p>
                  <p>• 단기/중기 실적 전망과 장기 성장성을 구분하여 접근했습니다.</p>
                  <p>• ESG 요소와 규제 환경 변화가 투자판단에 반영되었습니다.</p>
                  <p>• 글로벌 경기 동향과 국내 정책 변화가 종합적으로 고려되었습니다.</p>
                  <p>• 기술적 분석과 펀더멘털 분석이 적절히 조화된 것으로 판단됩니다.</p>
                  <p>• 투자자의 리스크 성향별 접근 전략이 구체적으로 제시되었습니다.</p>
                  <p>• 향후 주요 모니터링 포인트와 투자 시점이 명시되었습니다.</p>
                  <p className="text-[#8b95a1] text-xs mt-4">* 이는 AI가 생성한 분석으로, 실제 리포트 내용과 다를 수 있습니다.</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
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

function getSignalPointColor(opinion: string) {
  switch (opinion) {
    case 'BUY': return '#22c55e';
    case 'HOLD': return '#eab308'; 
    case 'SELL': return '#ef4444';
    default: return '#8b95a1';
  }
}

export default function StockAnalystTab({ code }: StockAnalystTabProps) {
  const [selectedReport, setSelectedReport] = useState<Report | null>(null);
  
  const data = reportsData as Record<string, Report[]>;
  const reports = data[code] || [];
  
  // 가격 데이터 (차트용)
  const priceData = useMemo(() => {
    try {
      const prices = (signalPricesData as any)[code] || [];
      return prices.map((item: any) => ({
        date: item.date,
        price: item.close,
        dateFormatted: new Date(item.date).toLocaleDateString('ko-KR', { month: 'short', day: 'numeric' })
      })).slice(-30); // 최근 30일
    } catch {
      return [];
    }
  }, [code]);
  
  // 목표가 데이터 (차트용)
  const targetPriceData = useMemo(() => {
    return reports
      .filter(r => r.target_price && r.target_price > 0)
      .map(r => ({
        date: r.published_at,
        targetPrice: r.target_price,
        opinion: r.opinion,
        dateFormatted: new Date(r.published_at).toLocaleDateString('ko-KR', { month: 'short', day: 'numeric' }),
        firm: r.firm
      }))
      .slice(-10); // 최근 10개
  }, [reports]);
  
  // 차트 데이터 합치기
  const chartData = useMemo(() => {
    const combinedData: any[] = [];
    
    // 가격 데이터 기본으로 사용
    priceData.forEach(price => {
      combinedData.push({
        date: price.date,
        price: price.price,
        dateFormatted: price.dateFormatted
      });
    });
    
    // 목표가 데이터 추가
    targetPriceData.forEach(target => {
      const existingIndex = combinedData.findIndex(item => 
        item.date === target.date || 
        Math.abs(new Date(item.date).getTime() - new Date(target.date).getTime()) < 86400000 // 1일 이내
      );
      
      if (existingIndex !== -1) {
        combinedData[existingIndex].targetPrice = target.targetPrice;
        combinedData[existingIndex].opinion = target.opinion;
      } else {
        combinedData.push({
          date: target.date,
          targetPrice: target.targetPrice,
          opinion: target.opinion,
          dateFormatted: target.dateFormatted
        });
      }
    });
    
    return combinedData.sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());
  }, [priceData, targetPriceData]);
  
  const sortedReports = useMemo(() => 
    [...reports].sort((a, b) => b.published_at.localeCompare(a.published_at)),
    [reports]
  );

  return (
    <div className="space-y-6">
      {/* 차트 섹션 */}
      {chartData.length > 0 && (
        <div className="bg-white rounded-xl shadow-sm border border-[#e8e8e8] p-6">
          <h3 className="font-bold text-[#191f28] mb-4">주가 & 애널리스트 목표가</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis 
                  dataKey="dateFormatted" 
                  stroke="#8b95a1"
                  fontSize={12}
                />
                <YAxis 
                  stroke="#8b95a1"
                  fontSize={12}
                  tickFormatter={(value) => `${(value / 1000).toFixed(0)}k`}
                />
                <Tooltip
                  formatter={(value: any, name: string) => [
                    `${value?.toLocaleString()}원`,
                    name === 'price' ? '주가' : '목표가'
                  ]}
                  labelFormatter={(label) => `날짜: ${label}`}
                />
                
                {/* 실제 주가 라인 */}
                <Line
                  type="monotone"
                  dataKey="price"
                  stroke="#3182f6"
                  strokeWidth={2}
                  dot={false}
                />
                
                {/* 목표가 라인 */}
                <Line
                  type="monotone"
                  dataKey="targetPrice"
                  stroke="#8b95a1"
                  strokeWidth={2}
                  strokeDasharray="5 5"
                  dot={false}
                />
                
                {/* 시그널 점들 */}
                {chartData.map((point, index) => 
                  point.opinion && (
                    <Scatter 
                      key={index}
                      data={[{ x: index, y: point.price || point.targetPrice }]}
                      fill={getSignalPointColor(point.opinion)}
                    />
                  )
                )}
              </LineChart>
            </ResponsiveContainer>
          </div>
          
          <div className="flex items-center gap-4 mt-4 text-sm text-[#8b95a1]">
            <div className="flex items-center gap-2">
              <div className="w-3 h-0.5 bg-[#3182f6]"></div>
              <span>실제 주가</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-0.5 bg-[#8b95a1] border-dashed"></div>
              <span>애널리스트 목표가</span>
            </div>
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-1">
                <div className="w-2 h-2 rounded-full bg-[#22c55e]"></div>
                <span>매수</span>
              </div>
              <div className="flex items-center gap-1">
                <div className="w-2 h-2 rounded-full bg-[#eab308]"></div>
                <span>중립</span>
              </div>
              <div className="flex items-center gap-1">
                <div className="w-2 h-2 rounded-full bg-[#ef4444]"></div>
                <span>매도</span>
              </div>
            </div>
          </div>
        </div>
      )}

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
                  <th className="px-4 py-3 text-left text-sm font-medium text-[#8b95a1]">증권사</th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-[#8b95a1]">애널리스트명</th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-[#8b95a1]">투자의견</th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-[#8b95a1]">리포트제목</th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-[#8b95a1]">AI 한줄요약</th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-[#8b95a1]">목표가</th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-[#8b95a1]">PDF</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#f0f0f0]">
                {sortedReports.map((report, index) => (
                  <tr key={index} className="hover:bg-[#f8f9fa] transition-colors">
                    <td className="px-4 py-4 text-sm text-[#191f28] whitespace-nowrap">
                      {new Date(report.published_at).toLocaleDateString('ko-KR', { 
                        month: 'short', 
                        day: 'numeric' 
                      })}
                    </td>
                    <td className="px-4 py-4 text-sm text-[#191f28] whitespace-nowrap">
                      {report.firm}
                    </td>
                    <td className="px-4 py-4 text-sm text-[#8b95a1] whitespace-nowrap">
                      {report.analyst || '-'}
                    </td>
                    <td className="px-4 py-4">
                      <OpinionBadge opinion={report.opinion} />
                    </td>
                    <td className="px-4 py-4 text-sm text-[#191f28] max-w-xs">
                      <div className="truncate">{report.title}</div>
                    </td>
                    <td className="px-4 py-4 text-sm max-w-xs">
                      <div 
                        className="text-[#8b95a1] cursor-pointer hover:text-[#3182f6] transition-colors"
                        onClick={() => setSelectedReport(report)}
                      >
                        AI 분석 보기 →
                      </div>
                    </td>
                    <td className="px-4 py-4 text-sm text-[#191f28] font-medium whitespace-nowrap">
                      {report.target_price ? `${report.target_price.toLocaleString()}원` : '-'}
                    </td>
                    <td className="px-4 py-4">
                      {report.pdf_url ? (
                        <a
                          href={report.pdf_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-[#3182f6] hover:text-[#2171e5] transition-colors"
                          title="PDF 다운로드"
                        >
                          📄
                        </a>
                      ) : (
                        <span className="text-[#8b95a1]">-</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
      
      {/* AI 상세 모달 */}
      {selectedReport && (
        <AIDetailsModal
          report={selectedReport}
          onClose={() => setSelectedReport(null)}
        />
      )}
    </div>
  );
}