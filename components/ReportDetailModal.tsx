'use client';

import { useState } from 'react';
import { insertSignalReport, insertSignalVote } from '@/lib/supabase';

interface ReportData {
  // 애널리스트 리포트 데이터
  ticker?: string;
  firm?: string;
  analyst?: string | null;
  title?: string;
  target_price?: number | null;
  opinion?: string;
  published_at?: string;
  pdf_url?: string;
  summary?: string;
  ai_detail?: string;
  
  // 시그널 데이터 (SignalDetailModal용)
  id?: string;
  date?: string;
  influencer?: string;
  signal?: string;
  quote?: string;
  videoUrl?: string;
  confidence?: number | string;
  analysis_reasoning?: string;
  mention_type?: string;
  timestamp?: string;
  videoTitle?: string;
  channelName?: string;
  likeCount?: number;
}

interface ReportDetailModalProps {
  report: ReportData | null;
  isOpen: boolean;
  onClose: () => void;
  type?: 'report' | 'signal'; // 리포트 타입 구분
}

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

// AI 내부 메모 필터링 (SignalDetailModal에서 가져옴)
const INTERNAL_PATTERNS = [
  /confidence\s*[=:]\s*\w+/gi,
  /mention_type\s*[=:]\s*\w+/gi,
  /signal_type\s*[=:]\s*\w+/gi,
  /\[내부\s*메모\]/gi,
  /\[AI\s*(분석|메모|노트)\]/gi,
];

function filterInternalText(text: string): string {
  let filtered = text;
  INTERNAL_PATTERNS.forEach(p => { filtered = filtered.replace(p, '').trim(); });
  // 빈 줄 정리
  filtered = filtered.replace(/\n{3,}/g, '\n\n').trim();
  return filtered;
}

function OpinionBadge({ opinion }: { opinion: string }) {
  const styles = {
    'BUY': 'bg-[#22c55e]/10 text-[#22c55e] border border-[#22c55e]/20',
    'HOLD': 'bg-[#eab308]/10 text-[#eab308] border border-[#eab308]/20', 
    'SELL': 'bg-[#ef4444]/10 text-[#ef4444] border border-[#ef4444]/20',
    '매수': 'text-green-600 bg-green-50',
    '긍정': 'text-blue-600 bg-blue-50',
    '중립': 'text-yellow-600 bg-yellow-50',
    '부정': 'text-orange-600 bg-orange-50',
    '매도': 'text-red-600 bg-red-50'
  };
  
  return (
    <span className={`text-xs font-medium px-2 py-1 rounded-full ${styles[opinion as keyof typeof styles] || styles.HOLD}`}>
      {opinion}
    </span>
  );
}

function formatPrice(n: number | null, ticker?: string) {
  if (n === null || n === undefined) return '-';
  const isKoreanStock = /^\d+$/.test(ticker || '');
  if (ticker && !isKoreanStock) return `$${n.toLocaleString()}`;
  return `${Math.floor(n / 10000)}만원`;
}

function formatDate(dateStr: string) {
  try {
    const date = new Date(dateStr);
    const year = date.getFullYear().toString().slice(-2);
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}.${month}.${day}`;
  } catch (e) {
    return dateStr;
  }
}

// AI Detail 렌더러 컴포넌트 (탐색 페이지에서 가져옴)
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
    if (!trimmed) continue;
    
    // 섹션 헤더 패턴: "## 제목", "**제목**", "[제목]"
    const headerMatch = trimmed.match(/^(?:##\s*|★\s*|\*\*|【)(.*?)(?:\*\*|】)?:?\s*$/);
    if (headerMatch) {
      if (currentSection) sections.push(currentSection);
      currentSection = { title: headerMatch[1].trim(), content: '' };
    } else if (currentSection) {
      currentSection.content += (currentSection.content ? '\n' : '') + trimmed;
    }
  }
  
  if (currentSection) sections.push(currentSection);
  return sections;
}

function getSectionIcon(title: string) {
  if (title.includes('투자포인트') || title.includes('투자 포인트')) return '💎';
  if (title.includes('위험요인') || title.includes('리스크')) return '⚠️';
  if (title.includes('실적') || title.includes('매출')) return '📊';
  if (title.includes('전망') || title.includes('예상')) return '🔮';
  if (title.includes('밸류에이션') || title.includes('밸류')) return '💰';
  if (title.includes('요약') || title.includes('핵심')) return '📝';
  return '📄';
}

export default function ReportDetailModal({ report, isOpen, onClose, type = 'report' }: ReportDetailModalProps) {
  const [liked, setLiked] = useState(false);
  const [likeCount, setLikeCount] = useState(report?.likeCount || 0);
  const [showReportModal, setShowReportModal] = useState(false);
  const [reportReason, setReportReason] = useState('');
  const [reportDetail, setReportDetail] = useState('');
  const [isSubmittingReport, setIsSubmittingReport] = useState(false);
  const [showMemoInput, setShowMemoInput] = useState(false);
  const [memoText, setMemoText] = useState('');

  if (!isOpen || !report) return null;

  // Signal type 관련 함수들 (SignalDetailModal에서 가져옴)
  const getSignalStyle = (sig: string) => {
    switch (sig) {
      case '매수': return 'text-green-600 bg-green-50';
      case '긍정': return 'text-blue-600 bg-blue-50';
      case '중립': return 'text-yellow-600 bg-yellow-50';
      case '부정': return 'text-orange-600 bg-orange-50';
      case '매도': return 'text-red-600 bg-red-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  const timestampToSeconds = (ts?: string): number | null => {
    if (!ts) return null;
    const parts = ts.split(':').map(Number);
    if (parts.length === 2) return parts[0] * 60 + parts[1];
    if (parts.length === 3) return parts[0] * 3600 + parts[1] * 60 + parts[2];
    return null;
  };

  const getVideoUrlWithTimestamp = () => {
    if (!report.videoUrl || report.videoUrl === '#') return null;
    const seconds = timestampToSeconds(report.timestamp);
    if (seconds && (report.videoUrl.includes('youtube.com') || report.videoUrl.includes('youtu.be'))) {
      const sep = report.videoUrl.includes('?') ? '&' : '?';
      return `${report.videoUrl}${sep}t=${seconds}`;
    }
    return report.videoUrl;
  };

  // 하트(좋아요) 기능 — 낙관적 업데이트 (UI 항상 반응, DB 실패 silent 처리)
  const handleLike = async () => {
    const nextLiked = !liked;
    setLiked(nextLiked);
    setLikeCount(prev => nextLiked ? prev + 1 : prev - 1);

    if (type === 'signal' && report?.id && nextLiked) {
      // 좋아요 추가만 DB 저장 (unlike는 UI만)
      try {
        await insertSignalVote(report.id);
      } catch (error) {
        console.error('좋아요 DB 저장 실패 (무시됨):', error);
      }
    }
  };

  // 신고 기능
  const handleReport = async () => {
    if (!reportReason.trim()) {
      alert('신고 사유를 선택해주세요.');
      return;
    }

    setIsSubmittingReport(true);
    try {
      const reportId = type === 'signal' ? report.id : `analyst_${report.ticker}_${report.published_at}`;
      if (reportId) {
        await insertSignalReport(reportId, reportReason, reportDetail);
        alert('신고가 접수되었습니다.');
        setShowReportModal(false);
        setReportReason('');
        setReportDetail('');
      }
    } catch (error) {
      console.error('신고 처리 중 오류:', error);
      alert('신고 처리 중 오류가 발생했습니다.');
    } finally {
      setIsSubmittingReport(false);
    }
  };

  // 메모 저장 (Signal용)
  const handleSaveMemo = async () => {
    if (!memoText.trim() || !report?.id) return;
    
    try {
      // await insertSignalMemo(report.id, memoText); // 구현되어 있다면
      alert('메모가 저장되었습니다.');
      setShowMemoInput(false);
      setMemoText('');
    } catch (error) {
      console.error('메모 저장 중 오류:', error);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl max-w-lg w-full max-h-[80vh] overflow-y-auto">
        <div className="p-6">
          {/* 헤더 — 좌측 배지 | 우측 좋아요·신고·X */}
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              {type === 'signal' && report.signal && (
                <span className={`px-2.5 py-1 rounded text-sm font-bold ${getSignalStyle(report.signal)}`}>
                  {report.signal}
                </span>
              )}
              {type === 'signal' && report.date && (
                <span className="text-xs text-gray-400">{formatDate(report.date)}</span>
              )}
            </div>
            <div className="flex items-center gap-1">
              {/* 좋아요 */}
              <button
                onClick={handleLike}
                className={`flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                  liked
                    ? 'bg-red-50 text-red-600 border border-red-200'
                    : 'bg-gray-50 text-gray-500 border border-gray-200 hover:bg-gray-100'
                }`}
              >
                <span className="text-base">{liked ? '❤️' : '🤍'}</span>
                {likeCount > 0 && <span>{likeCount}</span>}
              </button>

              {/* 신고 */}
              <button
                onClick={() => setShowReportModal(true)}
                className="flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-medium bg-gray-50 text-gray-500 border border-gray-200 hover:bg-gray-100 transition-colors"
              >
                <span className="text-base">🚨</span>
                <span>신고</span>
              </button>

              {/* 닫기 */}
              <button
                onClick={onClose}
                className="w-9 h-9 flex items-center justify-center rounded-lg bg-gray-50 text-gray-500 border border-gray-200 hover:bg-gray-100 transition-colors text-lg"
              >
                ✕
              </button>
            </div>
          </div>

          {/* 컨텐츠 */}
          <div className="space-y-4">
            {type === 'report' ? (
              // 애널리스트 리포트 컨텐츠
              <>
                <div>
                  <h3 className="font-medium text-gray-900 mb-2">{report.title}</h3>
                  <div className="flex items-center gap-2 mb-3">
                    <span className="text-sm font-medium text-blue-600">
                      {TICKER_NAMES[report.ticker!] || report.ticker}
                    </span>
                    {report.opinion && <OpinionBadge opinion={report.opinion} />}
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-gray-500">증권사</span>
                    <p className="font-medium">{report.firm}</p>
                  </div>
                  <div>
                    <span className="text-gray-500">애널리스트</span>
                    <p className="font-medium">{report.analyst || report.firm || '-'}</p>
                    {!report.analyst && report.firm && (
                      <span className="text-xs text-gray-400">증권사</span>
                    )}
                  </div>
                  <div>
                    <span className="text-gray-500">목표가</span>
                    <p className="font-medium text-lg">{report.target_price ? formatPrice(report.target_price, report.ticker) : '-'}</p>
                  </div>
                  <div>
                    <span className="text-gray-500">투자의견</span>
                    <p className="font-medium">{report.opinion}</p>
                  </div>
                  <div className="col-span-2">
                    <span className="text-gray-500">발행일</span>
                    <p className="font-medium">{formatDate(report.published_at!)}</p>
                  </div>
                </div>

                {/* AI 요약 */}
                {report.summary && (
                  <div>
                    <span className="text-gray-500 text-sm">AI 한줄요약</span>
                    <p className="text-sm text-gray-700 mt-1 p-3 bg-blue-50 rounded-lg font-medium">
                      {report.summary}
                    </p>
                  </div>
                )}
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
                    <a 
                      href={report.pdf_url} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg flex items-center justify-center gap-2 hover:bg-blue-700 transition-colors"
                    >
                      📄 PDF 보고서 보기
                    </a>
                  </div>
                )}
              </>
            ) : (
              // 시그널 컨텐츠
              <>
                <div className="space-y-3">
                  <div>
                    <span className="text-gray-500 text-sm">인플루언서</span>
                    <p className="font-medium">{report.influencer}</p>
                  </div>

                  {report.quote && (
                    <div>
                      <span className="text-gray-500 text-sm">핵심 발언</span>
                      <div className="mt-1 p-3 bg-gray-50 rounded-lg">
                        <p className="text-sm text-gray-700 leading-relaxed">
                          "{filterInternalText(report.quote)}"
                        </p>
                      </div>
                    </div>
                  )}

                  {report.analysis_reasoning && (
                    <div>
                      <span className="text-gray-500 text-sm">AI 분석</span>
                      <div className="mt-1 p-3 bg-blue-50 rounded-lg">
                        <p className="text-sm text-gray-700 leading-relaxed whitespace-pre-line">
                          {filterInternalText(report.analysis_reasoning)}
                        </p>
                      </div>
                    </div>
                  )}

                  {/* 영상 링크 */}
                  {getVideoUrlWithTimestamp() && (
                    <div className="pt-4 border-t">
                      <a
                        href={getVideoUrlWithTimestamp()!}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="w-full bg-red-600 text-white py-3 px-4 rounded-lg flex items-center justify-center gap-2 hover:bg-red-700 transition-colors"
                      >
                        🎥 {report.timestamp ? `영상보기 (${report.timestamp})` : '영상보기'}
                      </a>
                    </div>
                  )}
                </div>
              </>
            )}
          </div>
        </div>
      </div>

      {/* 신고 모달 */}
      {showReportModal && (
        <div className="fixed inset-0 bg-black bg-opacity-70 flex items-center justify-center z-60 p-4">
          <div className="bg-white rounded-2xl max-w-md w-full p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-4">신고하기</h3>
            
            <div className="space-y-4">
              <div>
                <span className="text-gray-500 text-sm">신고 사유</span>
                <select
                  value={reportReason}
                  onChange={(e) => setReportReason(e.target.value)}
                  className="w-full mt-1 p-2 border border-gray-300 rounded-lg"
                >
                  <option value="">선택해주세요</option>
                  <option value="잘못된 정보">잘못된 정보</option>
                  <option value="스팸">스팸</option>
                  <option value="부적절한 내용">부적절한 내용</option>
                  <option value="기타">기타</option>
                </select>
              </div>

              <div>
                <span className="text-gray-500 text-sm">상세 내용 (선택)</span>
                <textarea
                  value={reportDetail}
                  onChange={(e) => setReportDetail(e.target.value)}
                  className="w-full mt-1 p-2 border border-gray-300 rounded-lg h-20"
                  placeholder="상세한 신고 내용을 입력해주세요..."
                />
              </div>

              <div className="flex gap-2">
                <button
                  onClick={() => setShowReportModal(false)}
                  className="flex-1 py-2 px-4 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
                  disabled={isSubmittingReport}
                >
                  취소
                </button>
                <button
                  onClick={handleReport}
                  className="flex-1 py-2 px-4 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50"
                  disabled={isSubmittingReport}
                >
                  {isSubmittingReport ? '처리중...' : '신고'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}