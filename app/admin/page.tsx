'use client';

import { useEffect, useState } from 'react';
import { getSignalReports, updateReportStatus, getAdminStats, supabase } from '@/lib/supabase';
import { callAnthropicAPI } from '@/lib/anthropicClient';

// AI 응답에서 JSON 안전 추출 (```json 백틱, markdown 제거)
function parseAiJson(text: string): any {
  let s = text.trim();
  // markdown 코드블록 제거
  s = s.replace(/^```(?:json)?\s*\n?/i, '').replace(/\n?```\s*$/i, '');
  // 혹시 앞뒤 설명 텍스트가 있으면 JSON 부분만 추출
  const jsonMatch = s.match(/\{[\s\S]*\}/);
  if (jsonMatch) s = jsonMatch[0];
  return JSON.parse(s);
}

interface SignalReport {
  id: string;
  reason: string;
  detail: string | null;
  created_at: string;
  status: string;
  ai_review: string | null;
  ai_suggestion: string | null;
  influencer_signals: {
    id: string;
    stock: string;
    ticker: string | null;
    signal: string;
    key_quote: string;
    reasoning: string | null;
    influencer_videos: {
      title: string;
      published_at: string;
      video_id: string;
      influencer_channels: {
        channel_name: string;
        channel_handle: string;
      } | null;
    } | null;
    speakers: {
      name: string;
    } | null;
  } | null;
}

interface AdminStats {
  totalSignals: number;
  totalVotes: number;
  totalReports: number;
  totalMemos: number;
  pendingReports: number;
  reviewedReports: number;
  resolvedReports: number;
  participationRate: number;
}

export default function AdminPage() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [reports, setReports] = useState<SignalReport[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedReport, setSelectedReport] = useState<SignalReport | null>(null);
  const [isAiProcessing, setIsAiProcessing] = useState(false);
  const [aiProcessingId, setAiProcessingId] = useState<string | null>(null);
  const [stats, setStats] = useState<AdminStats>({
    totalSignals: 0,
    totalVotes: 0,
    totalReports: 0,
    totalMemos: 0,
    pendingReports: 0,
    reviewedReports: 0,
    resolvedReports: 0,
    participationRate: 0
  });

  const tabs = [
    { id: 'dashboard', label: '📊 대시보드', icon: '📊' },
    { id: 'reports', label: '🚨 신고 관리', icon: '🚨' },
    { id: 'ai-suggestions', label: '🤖 AI 제안', icon: '🤖' },
    { id: 'prompts', label: '⚙️ 프롬프트 관리', icon: '⚙️' },
  ];

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [reportsData, statsData] = await Promise.all([
        getSignalReports(),
        getAdminStats()
      ]);
      setReports(reportsData);
      setStats(statsData);
    } catch (error) {
      console.error('데이터 로딩 실패:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleStatusUpdate = async (reportId: string, newStatus: string) => {
    try {
      await updateReportStatus(reportId, newStatus);
      await loadData(); // 전체 데이터 새로고침
      alert('상태가 업데이트되었습니다.');
    } catch (error) {
      console.error('상태 업데이트 실패:', error);
      alert('상태 업데이트에 실패했습니다.');
    }
  };

  // AI 검토 요청 (클라이언트 직접 호출)
  const handleAiReview = async (reportId: string) => {
    try {
      setIsAiProcessing(true);
      setAiProcessingId(reportId);

      // 1. 신고 데이터 조회 (시그널, 자막, 신고 사유 포함)
      const { data: reportData, error: reportError } = await supabase
        .from('signal_reports')
        .select(`
          *,
          influencer_signals (
            id,
            stock,
            ticker,
            signal,
            key_quote,
            timestamp,
            reasoning,
            influencer_videos (
              subtitle_text,
              title,
              published_at
            )
          )
        `)
        .eq('id', reportId)
        .single();

      if (reportError || !reportData) {
        throw new Error('신고 데이터를 찾을 수 없습니다.');
      }

      if (!reportData.influencer_signals?.influencer_videos?.subtitle_text) {
        throw new Error('자막 데이터가 없습니다.');
      }

      // 2. AI 검토 요청
      const signalData = reportData.influencer_signals;
      const subtitleText = signalData.influencer_videos.subtitle_text;

      const reviewPrompt = `
원본 자막과 시그널을 비교해서 신고 사유가 타당한지 검토해 주세요.

**원본 자막:**
${subtitleText}

**추출된 시그널:**
- 종목: ${signalData.stock} (${signalData.ticker || 'N/A'})
- 신호: ${signalData.signal}
- 인용문: ${signalData.key_quote}
- 타임스탬프: ${signalData.timestamp}
- 분석근거: ${signalData.reasoning || 'N/A'}

**신고 정보:**
- 신고 사유: ${reportData.reason}
- 상세 내용: ${reportData.detail || '없음'}

**검토 기준:**
1. 인용문이 실제 자막과 일치하는가?
2. 시그널 타입이 발언 내용과 일치하는가?
3. 타임스탬프가 정확한가?
4. 분석근거가 합리적인가?

**결과 형식:**
상태: [수정필요/문제없음]
근거: [구체적인 근거 설명]
`;

      const aiReview = await callAnthropicAPI({
        model: 'claude-opus-4-6',
        max_tokens: 1000,
        messages: [{ role: 'user', content: reviewPrompt }]
      });

      // 3. AI 검토 결과 저장
      const { error: updateError } = await supabase
        .from('signal_reports')
        .update({ 
          ai_review: aiReview
        })
        .eq('id', reportId);

      if (updateError) {
        throw new Error('AI 검토 결과 저장 실패');
      }

      // 4. "수정필요"인 경우 수정안 생성
      let aiSuggestion = null;
      if (aiReview.includes('수정필요') || aiReview.includes('수정 필요')) {
        const suggestionPrompt = `
이전 검토 결과에 따라 수정된 시그널을 JSON 형태로 생성해 주세요.

**원본 자막:**
${subtitleText}

**기존 시그널:**
- 종목: ${signalData.stock}
- 티커: ${signalData.ticker}
- 신호: ${signalData.signal}
- 인용문: ${signalData.key_quote}
- 타임스탬프: ${signalData.timestamp}
- 분석근거: ${signalData.reasoning}

**검토 결과:**
${aiReview}

**수정안을 다음 JSON 형식으로 제공해 주세요:**
{
  "stock": "종목명",
  "ticker": "티커 또는 null",
  "signal": "매수|긍정|중립|부정|매도",
  "key_quote": "원본 자막에서 추출한 실제 발언 (15자 이상, 반드시 자막 원문 그대로)",
  "timestamp": "MM:SS (자막에서 해당 발언이 시작되는 시점)",
  "reasoning": "자막 내용 기반 구체적 분석근거 (20자 이상, 왜 이 시그널인지 설명)"
}

**절대 금지:**
- key_quote를 빈 문자열("")이나 "N/A"로 채우지 마세요. 반드시 원본 자막에서 실제 발언을 정확히 복사하세요.
- reasoning을 "N/A"나 빈 값으로 채우지 마세요. 자막의 맥락을 분석하여 구체적으로 작성하세요.
- 원본 자막에 없는 내용을 창작하지 마세요.

반드시 순수 JSON만 반환. markdown 코드블록(\`\`\`)으로 감싸지 마세요.
`;

        try {
          aiSuggestion = await callAnthropicAPI({
            model: 'claude-opus-4-6',
            max_tokens: 500,
            messages: [{ role: 'user', content: suggestionPrompt }]
          });

          // 수정안 저장
          await supabase
            .from('signal_reports')
            .update({ 
              ai_suggestion: aiSuggestion
            })
            .eq('id', reportId);
        } catch (suggestionError) {
          console.error('수정안 생성 실패:', suggestionError);
          // 수정안 생성 실패해도 검토는 완료된 것으로 처리
        }
      }

      alert('AI 검토가 완료되었습니다!');
      await loadData(); // 데이터 새로고침
    } catch (error) {
      console.error('AI 검토 실패:', error);
      alert(error instanceof Error ? error.message : 'AI 검토에 실패했습니다.');
    } finally {
      setIsAiProcessing(false);
      setAiProcessingId(null);
    }
  };

  // AI 수정안 승인 (실제 시그널 업데이트)
  const handleApproveAiSuggestion = async (report: SignalReport) => {
    if (!report.ai_suggestion || !report.influencer_signals) {
      alert('AI 수정안이 없습니다.');
      return;
    }

    try {
      const suggestion = parseAiJson(report.ai_suggestion);
      
      // influencer_signals 테이블 업데이트
      const { error } = await supabase
        .from('influencer_signals')
        .update({
          stock: suggestion.stock,
          ticker: suggestion.ticker,
          signal: suggestion.signal,
          key_quote: suggestion.key_quote,
          timestamp: suggestion.timestamp,
          reasoning: suggestion.reasoning
        })
        .eq('id', report.influencer_signals.id);

      if (error) throw error;

      // 신고 상태를 resolved로 변경
      await updateReportStatus(report.id, 'resolved');
      
      alert('AI 수정안이 승인되어 시그널이 업데이트되었습니다.');
      await loadData();
      setSelectedReport(null);
    } catch (error) {
      console.error('승인 처리 실패:', error);
      alert('승인 처리에 실패했습니다.');
    }
  };

  // 신고 거절 (상태만 변경)
  const handleRejectReport = async (reportId: string) => {
    try {
      await updateReportStatus(reportId, 'resolved');
      alert('신고가 거절되었습니다.');
      await loadData();
      setSelectedReport(null);
    } catch (error) {
      console.error('거절 처리 실패:', error);
      alert('거절 처리에 실패했습니다.');
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('ko-KR', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending': return 'bg-yellow-100 text-yellow-800';
      case 'reviewed': return 'bg-blue-100 text-blue-800';
      case 'resolved': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'pending': return '대기';
      case 'reviewed': return '검토';
      case 'resolved': return '완료';
      default: return status;
    }
  };

  const getSignalColor = (signal: string) => {
    switch (signal) {
      case '매수': return 'bg-green-100 text-green-800';
      case '긍정': return 'bg-blue-100 text-blue-800';
      case '중립': return 'bg-yellow-100 text-yellow-800';
      case '부정': return 'bg-orange-100 text-orange-800';
      case '매도': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const renderDashboard = () => (
    <div className="space-y-8">
      {/* 통계 카드 */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-2xl p-6 shadow-sm border">
          <div className="flex items-center justify-between mb-4">
            <div className="bg-blue-100 rounded-full p-3">
              <span className="text-2xl">📈</span>
            </div>
          </div>
          <h3 className="text-2xl font-bold text-gray-900 mb-1">
            {stats.totalSignals.toLocaleString()}
          </h3>
          <p className="text-sm text-gray-600">총 시그널 수</p>
        </div>

        <div className="bg-white rounded-2xl p-6 shadow-sm border">
          <div className="flex items-center justify-between mb-4">
            <div className="bg-yellow-100 rounded-full p-3">
              <span className="text-2xl">🚨</span>
            </div>
          </div>
          <h3 className="text-2xl font-bold text-gray-900 mb-1">
            {stats.totalReports.toLocaleString()}
          </h3>
          <p className="text-sm text-gray-600">총 신고 수</p>
        </div>
      </div>

      {/* 신고 상태별 통계 */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-2xl p-6 shadow-sm border">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-3 h-3 bg-yellow-400 rounded-full"></div>
            <h3 className="font-semibold text-gray-900">대기 중</h3>
          </div>
          <p className="text-3xl font-bold text-yellow-600 mb-1">
            {stats.pendingReports}
          </p>
          <p className="text-sm text-gray-600">검토 대기 신고</p>
        </div>

        <div className="bg-white rounded-2xl p-6 shadow-sm border">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-3 h-3 bg-blue-400 rounded-full"></div>
            <h3 className="font-semibold text-gray-900">검토 중</h3>
          </div>
          <p className="text-3xl font-bold text-blue-600 mb-1">
            {stats.reviewedReports}
          </p>
          <p className="text-sm text-gray-600">검토 진행 신고</p>
        </div>

        <div className="bg-white rounded-2xl p-6 shadow-sm border">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-3 h-3 bg-green-400 rounded-full"></div>
            <h3 className="font-semibold text-gray-900">처리 완료</h3>
          </div>
          <p className="text-3xl font-bold text-green-600 mb-1">
            {stats.resolvedReports}
          </p>
          <p className="text-sm text-gray-600">완료된 신고</p>
        </div>
      </div>
    </div>
  );

  const renderReportsTab = () => (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-sm overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">신고 목록 ({reports.length}건)</h2>
        </div>

        {reports.length === 0 ? (
          <div className="p-8 text-center text-gray-500">
            <div className="text-4xl mb-4">📭</div>
            <p>신고된 시그널이 없습니다.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200 table-fixed">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider" style={{ width: '80px' }}>
                    날짜
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider" style={{ width: '150px' }}>
                    시그널 내용
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider" style={{ width: '100px' }}>
                    신고 사유
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider" style={{ width: '200px' }}>
                    AI 검토 결과
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider" style={{ width: '200px' }}>
                    AI 수정안
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider" style={{ width: '70px' }}>
                    상태
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider" style={{ width: '100px' }}>
                    작업
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {reports.map((report) => (
                  <tr key={report.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {formatDate(report.created_at)}
                    </td>
                    <td className="px-6 py-4" style={{ minWidth: '120px', maxWidth: '180px' }}>
                      <div className="flex flex-col space-y-1">
                        <div className="flex items-center space-x-2">
                          <span className="font-medium text-sm whitespace-nowrap">
                            {report.influencer_signals?.stock || 'Unknown'}
                          </span>
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getSignalColor(report.influencer_signals?.signal || '')}`}>
                            {report.influencer_signals?.signal || 'Unknown'}
                          </span>
                        </div>
                        <div className="text-xs text-gray-500">
                          {report.influencer_signals?.speakers?.name || 
                           report.influencer_signals?.influencer_videos?.influencer_channels?.channel_name || 
                           'Unknown'}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm text-gray-900">{report.reason}</div>
                      {report.detail && (
                        <div className="text-xs text-gray-500 mt-1 truncate max-w-xs">{report.detail}</div>
                      )}
                    </td>
                    <td className="px-4 py-4" style={{ maxWidth: '180px' }}>
                      <div className="text-sm">
                        {report.ai_review ? (() => {
                          const review = report.ai_review;
                          const needsFix = /수정\s*필요|수정필요/i.test(review);
                          const noIssue = /문제\s*없음|문제없음/i.test(review);
                          if (needsFix) {
                            // 근거 줄 찾기
                            const lines = review.split('\n').filter((l: string) => l.trim());
                            const reasonLine = lines.find((l: string) => /근거|이유|문제점/.test(l) && l.includes(':'));
                            let summary = '';
                            if (reasonLine) {
                              const short = reasonLine.replace(/^[\s*#-]*.*?[:：]\s*/, '').replace(/\*+/g, '').slice(0, 35);
                              summary = short ? `: ${short}${short.length >= 35 ? '...' : ''}` : '';
                            }
                            return <span className="text-amber-600">⚠️ 수정필요{summary}</span>;
                          } else if (noIssue) {
                            return <span className="text-green-600">✅ 문제없음</span>;
                          } else if (review === 'test') {
                            return <span className="text-gray-400">테스트</span>;
                          } else {
                            // "수정필요"가 없고 ai_suggestion도 없으면 → 문제없음으로 추정
                            if (!report.ai_suggestion) {
                              return <span className="text-green-600">✅ 문제없음</span>;
                            }
                            const firstLine = review.split('\n').find((l: string) => l.trim() && !l.startsWith('#'))?.replace(/\*+/g, '').trim() || '검토완료';
                            return <span className="text-blue-600">📋 {firstLine.slice(0, 30)}{firstLine.length > 30 ? '...' : ''}</span>;
                          }
                        })() : (
                          <span className="text-yellow-600">대기중</span>
                        )}
                      </div>
                    </td>
                    <td className="px-4 py-4" style={{ maxWidth: '180px' }}>
                      <div className="text-sm text-gray-600">
                        {report.ai_review ? (
                          report.ai_review.includes('수정필요') || report.ai_review.includes('수정 필요') ? (
                            report.ai_suggestion ? (
                              <span className="truncate block max-w-full" title={report.ai_suggestion}>
                                {(() => {
                                  try {
                                    const json = parseAiJson(report.ai_suggestion);
                                    const changes: string[] = [];
                                    const orig = report.influencer_signals;
                                    if (orig && json.stock && json.stock !== orig.stock) changes.push(`종목: ${orig.stock}→${json.stock}`);
                                    if (orig && json.signal && json.signal !== orig.signal) changes.push(`신호: ${orig.signal}→${json.signal}`);
                                    if (json.key_quote) changes.push('인용문 수정');
                                    if (json.reasoning) changes.push('분석근거 수정');
                                    return changes.length > 0 ? changes.slice(0, 2).join(', ') : '수정안 있음';
                                  } catch { return '수정안 있음'; }
                                })()}
                              </span>
                            ) : (
                              <span className="text-yellow-600">생성중...</span>
                            )
                          ) : (
                            <span className="text-gray-400">-</span>
                          )
                        ) : (
                          <span className="text-gray-400">-</span>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(report.status)}`}>
                        {getStatusText(report.status)}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <div className="flex space-x-2">
                        <button
                          onClick={() => setSelectedReport(report)}
                          className="text-[#3182f6] hover:text-[#1b64da] transition-colors"
                        >
                          상세
                        </button>
                        <select
                          value={report.status}
                          onChange={(e) => handleStatusUpdate(report.id, e.target.value)}
                          className="text-xs border border-gray-300 rounded px-2 py-1"
                        >
                          <option value="pending">대기</option>
                          <option value="reviewed">검토</option>
                          <option value="resolved">완료</option>
                        </select>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );

  // AI 제안 탭 상태
  const [qualityIssues, setQualityIssues] = useState<any[]>([]);
  const [loadingIssues, setLoadingIssues] = useState(false);
  const [aiImprovements, setAiImprovements] = useState<Record<string, any>>({});
  const [improvingSignals, setImprovingSignals] = useState<Set<string>>(new Set());

  // 프롬프트 관리 탭 상태
  const [reportPatterns, setReportPatterns] = useState<any>(null);
  const [loadingPatterns, setLoadingPatterns] = useState(false);
  const [promptImprovements, setPromptImprovements] = useState<string>('');
  const [generatingPrompt, setGeneratingPrompt] = useState(false);

  // 품질 이슈 로딩 (클라이언트 직접 호출)
  const loadQualityIssues = async () => {
    try {
      setLoadingIssues(true);
      
      // 품질 이슈가 있는 시그널 조회
      const { data: signals, error } = await supabase
        .from('influencer_signals')
        .select(`
          id,
          stock,
          ticker,
          signal,
          key_quote,
          reasoning,
          confidence,
          created_at,
          influencer_videos (
            title,
            published_at,
            video_id,
            influencer_channels (
              channel_name,
              channel_handle
            )
          ),
          speakers (
            name
          )
        `)
        .order('created_at', { ascending: false })
        .limit(100); // 최근 100개만 검사

      if (error) {
        throw new Error('시그널 데이터 조회 실패: ' + error.message);
      }

      // 품질 이슈 탐지
      const issues: any[] = [];

      signals?.forEach((signal) => {
        const issueTypes: string[] = [];
        const currentValues: Record<string, string> = {};

        // 1. reasoning이 null이거나 20자 미만
        if (!signal.reasoning || signal.reasoning.length < 20) {
          issueTypes.push('분석근거 부족');
          currentValues['분석근거 부족'] = signal.reasoning || 'null';
        }

        // 2. key_quote가 15자 미만
        if (!signal.key_quote || signal.key_quote.length < 15) {
          issueTypes.push('인용문 부족');
          currentValues['인용문 부족'] = signal.key_quote || 'null';
        }

        // 3. confidence가 없는 경우
        if (!signal.confidence) {
          issueTypes.push('신뢰도 누락');
          currentValues['신뢰도 누락'] = 'null';
        }

        // 이슈가 있는 경우에만 추가
        if (issueTypes.length > 0) {
          issues.push({
            id: signal.id,
            stock: signal.stock,
            ticker: signal.ticker,
            signal: signal.signal,
            quote: signal.key_quote,
            analysis_reasoning: signal.reasoning,
            confidence: signal.confidence,
            created_at: signal.created_at,
            influencer_videos: signal.influencer_videos,
            speakers: signal.speakers,
            issueTypes,
            currentValues
          });
        }
      });

      setQualityIssues(issues);
    } catch (error) {
      console.error('품질 이슈 로딩 실패:', error);
      alert(error instanceof Error ? error.message : '품질 이슈 로딩에 실패했습니다.');
    } finally {
      setLoadingIssues(false);
    }
  };

  // 신고 패턴 로딩 (클라이언트 직접 호출)
  const loadReportPatterns = async () => {
    try {
      setLoadingPatterns(true);
      
      // 신고 데이터와 관련 시그널 정보 조회
      const { data: reports, error } = await supabase
        .from('signal_reports')
        .select(`
          id,
          reason,
          detail,
          created_at,
          status,
          influencer_signals (
            stock,
            signal,
            speakers (
              name
            ),
            influencer_videos (
              influencer_channels (
                channel_name
              )
            )
          )
        `)
        .order('created_at', { ascending: false });

      if (error) {
        throw new Error('신고 데이터 조회 실패: ' + error.message);
      }

      // 1. 사유별 신고 건수 집계
      const reasonStats: Record<string, number> = {};
      reports?.forEach((report) => {
        reasonStats[report.reason] = (reasonStats[report.reason] || 0) + 1;
      });

      // 2. 시그널 타입별 신고 빈도
      const signalTypeStats: Record<string, number> = {};
      reports?.forEach((report) => {
        if (report.influencer_signals?.signal) {
          const signal = report.influencer_signals.signal;
          signalTypeStats[signal] = (signalTypeStats[signal] || 0) + 1;
        }
      });

      // 3. 종목별 신고 빈도
      const stockStats: Record<string, number> = {};
      reports?.forEach((report) => {
        if (report.influencer_signals?.stock) {
          const stock = report.influencer_signals.stock;
          stockStats[stock] = (stockStats[stock] || 0) + 1;
        }
      });

      // 4. 화자별 신고 빈도
      const speakerStats: Record<string, number> = {};
      reports?.forEach((report) => {
        const speakerName = report.influencer_signals?.speakers?.name || 
                           report.influencer_signals?.influencer_videos?.influencer_channels?.channel_name;
        if (speakerName) {
          speakerStats[speakerName] = (speakerStats[speakerName] || 0) + 1;
        }
      });

      // 5. 월별 신고 트렌드 (최근 6개월)
      const monthlyStats: Record<string, number> = {};
      reports?.forEach((report) => {
        const reportDate = new Date(report.created_at);
        const monthKey = `${reportDate.getFullYear()}-${String(reportDate.getMonth() + 1).padStart(2, '0')}`;
        monthlyStats[monthKey] = (monthlyStats[monthKey] || 0) + 1;
      });

      // 상위 항목만 추출
      const topReasons = Object.entries(reasonStats)
        .sort(([, a], [, b]) => b - a)
        .slice(0, 10);

      const topSignalTypes = Object.entries(signalTypeStats)
        .sort(([, a], [, b]) => b - a)
        .slice(0, 10);

      const topStocks = Object.entries(stockStats)
        .sort(([, a], [, b]) => b - a)
        .slice(0, 10);

      const topSpeakers = Object.entries(speakerStats)
        .sort(([, a], [, b]) => b - a)
        .slice(0, 10);

      const patterns = {
        totalReports: reports?.length || 0,
        reasonStats: topReasons.map(([reason, count]) => ({ reason, count })),
        signalTypeStats: topSignalTypes.map(([signal, count]) => ({ signal, count })),
        stockStats: topStocks.map(([stock, count]) => ({ stock, count })),
        speakerStats: topSpeakers.map(([speaker, count]) => ({ speaker, count })),
        monthlyStats: Object.entries(monthlyStats)
          .sort(([a], [b]) => a.localeCompare(b))
          .map(([month, count]) => ({ month, count }))
      };

      setReportPatterns(patterns);
    } catch (error) {
      console.error('신고 패턴 로딩 실패:', error);
      alert(error instanceof Error ? error.message : '신고 패턴 로딩에 실패했습니다.');
    } finally {
      setLoadingPatterns(false);
    }
  };

  // AI 개선 요청 (클라이언트 직접 호출)
  const handleAiImprovement = async (signalId: string, issueTypes: string[]) => {
    try {
      setImprovingSignals(prev => new Set(prev).add(signalId));

      // 1. 시그널 데이터 조회 (자막 포함)
      const { data: signalData, error: signalError } = await supabase
        .from('influencer_signals')
        .select(`
          *,
          influencer_videos (
            subtitle_text,
            title,
            published_at
          )
        `)
        .eq('id', signalId)
        .single();

      if (signalError || !signalData) {
        throw new Error('시그널 데이터를 찾을 수 없습니다.');
      }

      if (!signalData.influencer_videos?.subtitle_text) {
        throw new Error('자막 데이터가 없습니다.');
      }

      // 2. AI 개선 요청
      const subtitleText = signalData.influencer_videos.subtitle_text;
      const issueDescription = issueTypes.join(', ');

      const improvePrompt = `
품질 이슈가 발견된 시그널을 개선해 주세요.

**원본 자막:**
${subtitleText}

**기존 시그널:**
- 종목: ${signalData.stock} (${signalData.ticker || 'N/A'})
- 신호: ${signalData.signal}
- 인용문: ${signalData.key_quote || 'null'}
- 타임스탬프: ${signalData.timestamp || 'N/A'}
- 분석근거: ${signalData.reasoning || 'null'}
- 신뢰도: ${signalData.confidence || 'null'}

**발견된 품질 이슈:**
${issueDescription}

**개선 지침:**
1. 분석근거 부족: 자막을 바탕으로 최소 20자 이상의 구체적인 분석근거 작성
2. 인용문 부족: 자막에서 정확한 핵심 발언을 15자 이상 인용
3. 신뢰도 누락: 1-100 점수로 신뢰도 평가
4. 시그널 타입은 반드시 한글 5단계만 사용: 매수/긍정/중립/부정/매도

**개선안을 다음 JSON 형식으로 제공해 주세요:**
{
  "stock": "종목명",
  "ticker": "티커 또는 null",
  "signal": "매수|긍정|중립|부정|매도",
  "key_quote": "원본 자막에서 추출한 실제 발언 (15자 이상, 반드시 자막 원문 그대로)",
  "timestamp": "MM:SS (자막에서 해당 발언이 시작되는 시점)",
  "reasoning": "자막 내용 기반 구체적 분석근거 (20자 이상)",
  "confidence": 85
}

**절대 금지:** key_quote를 빈 문자열("")이나 "N/A"로 채우지 마세요. reasoning도 마찬가지. 반드시 원본 자막에서 실제 내용을 추출하세요.

반드시 순수 JSON만 반환. markdown 코드블록(\`\`\`)으로 감싸지 마세요.
`;

      const improvementSuggestion = await callAnthropicAPI({
        model: 'claude-sonnet-4-20250514',
        max_tokens: 800,
        messages: [{ role: 'user', content: improvePrompt }]
      });

      const data = {
        success: true,
        improvement: improvementSuggestion,
        originalSignal: {
          stock: signalData.stock,
          ticker: signalData.ticker,
          signal: signalData.signal,
          quote: signalData.key_quote,
          timestamp: signalData.timestamp,
          analysis_reasoning: signalData.reasoning,
          confidence: signalData.confidence
        }
      };

      setAiImprovements(prev => ({ ...prev, [signalId]: data }));
      alert('AI 개선안이 생성되었습니다.');
    } catch (error) {
      console.error('AI 개선 요청 실패:', error);
      alert(error instanceof Error ? error.message : '개선안 생성 중 오류가 발생했습니다.');
    } finally {
      setImprovingSignals(prev => {
        const newSet = new Set(prev);
        newSet.delete(signalId);
        return newSet;
      });
    }
  };

  // 개선안 승인
  const handleApproveImprovement = async (signalId: string) => {
    try {
      const improvement = aiImprovements[signalId];
      if (!improvement) return;

      const suggestion = parseAiJson(improvement.improvement);
      
      const { error } = await supabase
        .from('influencer_signals')
        .update({
          stock: suggestion.stock,
          ticker: suggestion.ticker,
          signal: suggestion.signal,
          key_quote: suggestion.key_quote,
          timestamp: suggestion.timestamp,
          reasoning: suggestion.reasoning,
          confidence: suggestion.confidence
        })
        .eq('id', signalId);

      if (error) throw error;

      alert('개선안이 승인되어 시그널이 업데이트되었습니다.');
      
      // AI 개선안 제거하고 이슈 목록 새로고침
      setAiImprovements(prev => {
        const newImprovements = { ...prev };
        delete newImprovements[signalId];
        return newImprovements;
      });
      
      await loadQualityIssues();
    } catch (error) {
      console.error('개선안 승인 실패:', error);
      alert('개선안 승인에 실패했습니다.');
    }
  };

  // 개선안 거절
  const handleRejectImprovement = (signalId: string) => {
    setAiImprovements(prev => {
      const newImprovements = { ...prev };
      delete newImprovements[signalId];
      return newImprovements;
    });
  };

  // 프롬프트 개선안 생성 (클라이언트 직접 호출)
  const generatePromptImprovements = async () => {
    try {
      setGeneratingPrompt(true);

      if (!reportPatterns) {
        throw new Error('신고 패턴 데이터가 필요합니다.');
      }

      // AI 검토 결과가 있는 신고 데이터 가져오기
      const { data: reviewedReports } = await supabase
        .from('signal_reports')
        .select('reason, detail, ai_review, influencer_signals(stock, signal, key_quote)')
        .not('ai_review', 'is', null)
        .neq('ai_review', 'test')
        .limit(10);

      const aiReviewSummary = (reviewedReports || []).map((r: any, i: number) => 
        `   ${i+1}. [${r.reason}] ${r.influencer_signals?.stock || '?'} (${r.influencer_signals?.signal || '?'}) → AI판정: ${r.ai_review?.includes('수정필요') || r.ai_review?.includes('수정 필요') ? '수정필요' : '문제없음'}`
      ).join('\n');

      // AI에게 프롬프트 개선안 요청
      const promptImprovementPrompt = `
신고 패턴 분석 결과와 AI 검토 결과를 바탕으로 파이프라인 프롬프트의 개선 규칙을 제안해 주세요.

**현재 프롬프트 버전:** V10

**신고 패턴 분석:**
1. **사유별 신고 건수 TOP:**
${reportPatterns.reasonStats.map((item: any) => `   - ${item.reason}: ${item.count}건`).join('\n')}

2. **시그널 타입별 신고 빈도:**
${reportPatterns.signalTypeStats.map((item: any) => `   - ${item.signal}: ${item.count}건`).join('\n')}

3. **종목별 신고 빈도 TOP:**
${reportPatterns.stockStats.map((item: any) => `   - ${item.stock}: ${item.count}건`).join('\n')}

4. **화자별 신고 빈도 TOP:**
${reportPatterns.speakerStats.map((item: any) => `   - ${item.speaker}: ${item.count}건`).join('\n')}

5. **총 신고 건수:** ${reportPatterns.totalReports}건

6. **AI 검토 결과 요약:**
${aiReviewSummary || '   (AI 검토 결과 없음)'}

**분석 기준:**
- 자주 신고되는 사유를 줄이기 위한 추출 규칙 강화
- 특정 시그널 타입의 오탐지 방지
- 종목명/티커 정확도 향상
- 인용문 및 분석근거의 품질 향상

**개선안 형식:**
다음과 같이 구체적인 규칙 5-7개를 제안해 주세요:

1. [문제점] → [개선 규칙]
2. [문제점] → [개선 규칙]
...

각 규칙은 구체적이고 실행 가능한 지침이어야 합니다.
`;

      const promptImprovements = await callAnthropicAPI({
        model: 'claude-sonnet-4-20250514',
        max_tokens: 1500,
        messages: [{ role: 'user', content: promptImprovementPrompt }]
      });

      setPromptImprovements(promptImprovements);
    } catch (error) {
      console.error('프롬프트 개선안 생성 실패:', error);
      alert(error instanceof Error ? error.message : '프롬프트 개선안 생성 중 오류가 발생했습니다.');
    } finally {
      setGeneratingPrompt(false);
    }
  };

  // 탭 변경 시 데이터 로딩
  useEffect(() => {
    if (activeTab === 'ai-suggestions' && qualityIssues.length === 0) {
      loadQualityIssues();
    } else if (activeTab === 'prompts' && !reportPatterns) {
      loadReportPatterns();
    }
  }, [activeTab]);

  // AI 제안 탭 렌더링
  const renderAiSuggestionsTab = () => (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">🤖 AI 품질 제안</h2>
          <p className="text-gray-600 mt-1">품질 이슈가 감지된 시그널의 개선안을 확인합니다.</p>
        </div>
        <button
          onClick={loadQualityIssues}
          disabled={loadingIssues}
          className="px-4 py-2 bg-[#3182f6] text-white rounded-lg hover:bg-[#1b64da] transition-colors flex items-center gap-2"
        >
          {loadingIssues ? (
            <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
          ) : (
            '🔄'
          )}
          품질 검사 실행
        </button>
      </div>

      {loadingIssues ? (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#3182f6] mx-auto mb-4"></div>
          <p className="text-gray-600">품질 이슈를 분석하는 중...</p>
        </div>
      ) : qualityIssues.length === 0 ? (
        <div className="text-center py-12">
          <div className="text-6xl mb-4">✅</div>
          <h3 className="text-xl font-bold text-gray-900 mb-2">품질 이슈 없음</h3>
          <p className="text-gray-600">현재 품질 기준을 만족하지 않는 시그널이 없습니다.</p>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow-sm overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900">
              품질 이슈 발견: {qualityIssues.length}건
            </h3>
          </div>
          
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">시그널 정보</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">이슈 유형</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">현재값</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">작업</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {qualityIssues.map((issue) => (
                  <tr key={issue.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4">
                      <div className="flex flex-col space-y-1">
                        <div className="flex items-center space-x-2">
                          <span className="font-medium text-sm">{issue.stock}</span>
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getSignalColor(issue.signal)}`}>
                            {issue.signal}
                          </span>
                        </div>
                        <div className="text-xs text-gray-500">
                          {issue.speakers?.name || issue.influencer_videos?.influencer_channels?.channel_name || 'Unknown'}
                        </div>
                        <div className="text-xs text-gray-400">
                          {formatDate(issue.created_at)}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="space-y-1">
                        {issue.issueTypes.map((issueType: string) => (
                          <span key={issueType} className="inline-block px-2 py-1 bg-red-100 text-red-800 text-xs rounded mr-1">
                            {issueType}
                          </span>
                        ))}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-xs text-gray-600 space-y-1">
                        {Object.entries(issue.currentValues).map(([key, value]) => (
                          <div key={key}>
                            <span className="font-medium">{key}:</span>
                            <span className="ml-1 text-gray-500 truncate max-w-32 inline-block">
                              {String(value)}
                            </span>
                          </div>
                        ))}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      {aiImprovements[issue.id] ? (
                        <div className="space-y-2">
                          <div className="text-xs text-green-600 font-medium">✅ 개선안 생성됨</div>
                          <div className="flex space-x-2">
                            <button
                              onClick={() => handleApproveImprovement(issue.id)}
                              className="px-3 py-1 bg-green-600 text-white text-xs rounded hover:bg-green-700"
                            >
                              승인
                            </button>
                            <button
                              onClick={() => handleRejectImprovement(issue.id)}
                              className="px-3 py-1 bg-gray-300 text-gray-700 text-xs rounded hover:bg-gray-400"
                            >
                              거절
                            </button>
                          </div>
                        </div>
                      ) : (
                        <button
                          onClick={() => handleAiImprovement(issue.id, issue.issueTypes)}
                          disabled={improvingSignals.has(issue.id)}
                          className="px-3 py-1 bg-purple-600 text-white text-xs rounded hover:bg-purple-700 disabled:opacity-50 flex items-center gap-1"
                        >
                          {improvingSignals.has(issue.id) ? (
                            <>
                              <div className="w-3 h-3 border border-white border-t-transparent rounded-full animate-spin"></div>
                              처리중...
                            </>
                          ) : (
                            <>🤖 AI 개선 요청</>
                          )}
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* 개선안 상세 보기 */}
          {Object.entries(aiImprovements).length > 0 && (
            <div className="px-6 py-4 border-t border-gray-200">
              <h4 className="text-lg font-semibold text-gray-900 mb-4">🔧 AI 개선안 상세</h4>
              <div className="space-y-6">
                {Object.entries(aiImprovements).map(([signalId, improvement]: [string, any]) => {
                  try {
                    const suggestion = parseAiJson(improvement.improvement);
                    const original = improvement.originalSignal;
                    const issue = qualityIssues.find(i => i.id === signalId);
                    
                    return (
                      <div key={signalId} className="border rounded-lg p-4">
                        <div className="flex justify-between items-start mb-4">
                          <h5 className="font-medium text-gray-900">
                            {issue?.stock} - {issue?.signal}
                          </h5>
                          <div className="flex space-x-2">
                            <button
                              onClick={() => handleApproveImprovement(signalId)}
                              className="px-3 py-1 bg-green-600 text-white text-sm rounded hover:bg-green-700"
                            >
                              ✅ 승인
                            </button>
                            <button
                              onClick={() => handleRejectImprovement(signalId)}
                              className="px-3 py-1 bg-red-600 text-white text-sm rounded hover:bg-red-700"
                            >
                              ❌ 거절
                            </button>
                          </div>
                        </div>
                        
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div className="bg-red-50 rounded-lg p-3">
                            <h6 className="font-medium text-red-800 mb-2">📋 원본</h6>
                            <div className="space-y-1 text-sm">
                              <div><span className="font-medium">종목:</span> {original.stock}</div>
                              <div><span className="font-medium">신호:</span> {original.signal}</div>
                              <div><span className="font-medium">인용문:</span> {original.key_quote || 'N/A'}</div>
                              <div><span className="font-medium">분석근거:</span> {original.reasoning || 'N/A'}</div>
                              <div><span className="font-medium">신뢰도:</span> {original.confidence || 'N/A'}</div>
                            </div>
                          </div>
                          
                          <div className="bg-green-50 rounded-lg p-3">
                            <h6 className="font-medium text-green-800 mb-2">✅ 개선안</h6>
                            <div className="space-y-1 text-sm">
                              <div><span className="font-medium">종목:</span> {suggestion.stock}</div>
                              <div><span className="font-medium">신호:</span> {suggestion.signal}</div>
                              <div><span className="font-medium">인용문:</span> {suggestion.key_quote}</div>
                              <div><span className="font-medium">분석근거:</span> {suggestion.reasoning}</div>
                              <div><span className="font-medium">신뢰도:</span> {suggestion.confidence}</div>
                            </div>
                          </div>
                        </div>
                      </div>
                    );
                  } catch (e) {
                    return (
                      <div key={signalId} className="border rounded-lg p-4 bg-yellow-50">
                        <p className="text-yellow-800">개선안 파싱 오류</p>
                      </div>
                    );
                  }
                })}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );

  // 프롬프트 관리 탭 렌더링
  const renderPromptsTab = () => (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">⚙️ 프롬프트 관리</h2>
          <p className="text-gray-600 mt-1">신고 패턴을 분석하여 프롬프트 개선안을 제안합니다.</p>
        </div>
        <div className="flex items-center gap-2">
          <span className="px-3 py-1 bg-blue-100 text-blue-800 text-sm rounded-full font-medium">
            현재 버전: V10
          </span>
          <button
            onClick={loadReportPatterns}
            disabled={loadingPatterns}
            className="px-4 py-2 bg-[#3182f6] text-white rounded-lg hover:bg-[#1b64da] transition-colors flex items-center gap-2"
          >
            {loadingPatterns ? (
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
            ) : (
              '📊'
            )}
            패턴 분석
          </button>
        </div>
      </div>

      {loadingPatterns ? (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#3182f6] mx-auto mb-4"></div>
          <p className="text-gray-600">신고 패턴을 분석하는 중...</p>
        </div>
      ) : reportPatterns ? (
        <div className="space-y-6">
          {/* 패턴 요약 카드들 */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-white rounded-lg p-4 shadow-sm border">
              <h3 className="font-semibold text-gray-900 mb-2">총 신고 건수</h3>
              <p className="text-3xl font-bold text-[#3182f6]">{reportPatterns.totalReports}</p>
            </div>
            
            <div className="bg-white rounded-lg p-4 shadow-sm border">
              <h3 className="font-semibold text-gray-900 mb-2">주요 신고 사유</h3>
              <p className="text-lg font-bold text-red-600">
                {reportPatterns.reasonStats[0]?.reason || 'N/A'}
              </p>
              <p className="text-sm text-gray-500">
                {reportPatterns.reasonStats[0]?.count || 0}건
              </p>
            </div>
            
            <div className="bg-white rounded-lg p-4 shadow-sm border">
              <h3 className="font-semibold text-gray-900 mb-2">문제 신호 유형</h3>
              <p className="text-lg font-bold text-orange-600">
                {reportPatterns.signalTypeStats[0]?.signal || 'N/A'}
              </p>
              <p className="text-sm text-gray-500">
                {reportPatterns.signalTypeStats[0]?.count || 0}건
              </p>
            </div>
            
            <div className="bg-white rounded-lg p-4 shadow-sm border">
              <h3 className="font-semibold text-gray-900 mb-2">문제 종목</h3>
              <p className="text-lg font-bold text-purple-600">
                {reportPatterns.stockStats[0]?.stock || 'N/A'}
              </p>
              <p className="text-sm text-gray-500">
                {reportPatterns.stockStats[0]?.count || 0}건
              </p>
            </div>
          </div>

          {/* 상세 패턴 분석 */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* 사유별 통계 */}
            <div className="bg-white rounded-lg p-6 shadow-sm border">
              <h3 className="font-semibold text-gray-900 mb-4">📋 사유별 신고 현황</h3>
              <div className="space-y-3">
                {reportPatterns.reasonStats.slice(0, 5).map((item: any) => (
                  <div key={item.reason} className="flex justify-between items-center">
                    <span className="text-sm text-gray-700">{item.reason}</span>
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-bold">{item.count}건</span>
                      <div className="w-20 h-2 bg-gray-200 rounded-full">
                        <div 
                          className="h-2 bg-red-500 rounded-full"
                          style={{ width: `${(item.count / reportPatterns.totalReports) * 100}%` }}
                        ></div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* 시그널 타입별 통계 */}
            <div className="bg-white rounded-lg p-6 shadow-sm border">
              <h3 className="font-semibold text-gray-900 mb-4">🎯 시그널 타입별 신고</h3>
              <div className="space-y-3">
                {reportPatterns.signalTypeStats.slice(0, 5).map((item: any) => (
                  <div key={item.signal} className="flex justify-between items-center">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getSignalColor(item.signal)}`}>
                      {item.signal}
                    </span>
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-bold">{item.count}건</span>
                      <div className="w-20 h-2 bg-gray-200 rounded-full">
                        <div 
                          className="h-2 bg-orange-500 rounded-full"
                          style={{ width: `${(item.count / reportPatterns.totalReports) * 100}%` }}
                        ></div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* 프롬프트 개선안 생성 */}
          <div className="bg-white rounded-lg p-6 shadow-sm border">
            <div className="flex justify-between items-center mb-4">
              <h3 className="font-semibold text-gray-900">🚀 프롬프트 개선안 생성</h3>
              <button
                onClick={generatePromptImprovements}
                disabled={generatingPrompt}
                className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors flex items-center gap-2"
              >
                {generatingPrompt ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                    AI 분석 중...
                  </>
                ) : (
                  <>🤖 개선안 생성</>
                )}
              </button>
            </div>
            
            {promptImprovements ? (
              <div className="space-y-4">
                <div className="bg-green-50 rounded-lg p-4">
                  <div className="flex justify-between items-start mb-2">
                    <h4 className="font-medium text-green-800">AI 생성 프롬프트 개선 규칙</h4>
                    <button
                      onClick={() => navigator.clipboard.writeText(promptImprovements)}
                      className="px-3 py-1 bg-green-600 text-white text-sm rounded hover:bg-green-700"
                    >
                      📋 복사
                    </button>
                  </div>
                  <div className="text-sm text-green-700 whitespace-pre-wrap bg-white rounded border p-3">
                    {promptImprovements}
                  </div>
                </div>
              </div>
            ) : (
              <p className="text-gray-500 text-sm">
                신고 패턴 분석 결과를 바탕으로 파이프라인 프롬프트의 개선 규칙을 AI가 생성합니다.
              </p>
            )}
          </div>
        </div>
      ) : (
        <div className="text-center py-12">
          <div className="text-6xl mb-4">📊</div>
          <h3 className="text-xl font-bold text-gray-900 mb-2">패턴 분석 대기</h3>
          <p className="text-gray-600">신고 패턴 분석 버튼을 클릭하여 시작하세요.</p>
        </div>
      )}
    </div>
  );

  const renderTabContent = () => {
    switch (activeTab) {
      case 'dashboard':
        return renderDashboard();
      case 'reports':
        return renderReportsTab();
      case 'ai-suggestions':
        return renderAiSuggestionsTab();
      case 'prompts':
        return renderPromptsTab();
      default:
        return renderDashboard();
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#3182f6] mx-auto mb-4"></div>
          <p className="text-gray-600">데이터를 불러오는 중...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        {/* 헤더 */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">관리자 대시보드</h1>
          <p className="text-gray-600">시그널 신고 및 시스템을 관리합니다.</p>
        </div>

        {/* 탭 네비게이션 */}
        <div className="mb-8">
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`py-2 px-1 border-b-2 font-medium text-sm transition-colors ${
                    activeTab === tab.id
                      ? 'border-[#3182f6] text-[#3182f6]'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  {tab.label}
                </button>
              ))}
            </nav>
          </div>
        </div>

        {/* 탭 콘텐츠 */}
        {renderTabContent()}
      </div>

      {/* 신고 상세 모달 */}
      {selectedReport && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg shadow-xl w-full max-w-2xl max-h-[80vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex justify-between items-start mb-6">
                <h3 className="text-xl font-bold text-gray-900">신고 상세 정보</h3>
                <button
                  onClick={() => setSelectedReport(null)}
                  className="text-gray-400 hover:text-gray-600 text-2xl"
                >
                  ×
                </button>
              </div>

              <div className="space-y-6">
                {/* 신고 정보 */}
                <div>
                  <h4 className="text-lg font-semibold text-gray-900 mb-2">신고 정보</h4>
                  <div className="bg-gray-50 rounded-lg p-4 space-y-2">
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">신고 일시:</span>
                      <span className="text-sm font-medium">{formatDate(selectedReport.created_at)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">신고 사유:</span>
                      <span className="text-sm font-medium">{selectedReport.reason}</span>
                    </div>
                    {selectedReport.detail && (
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">상세 내용:</span>
                        <span className="text-sm font-medium">{selectedReport.detail}</span>
                      </div>
                    )}
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">처리 상태:</span>
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(selectedReport.status)}`}>
                        {getStatusText(selectedReport.status)}
                      </span>
                    </div>
                  </div>
                </div>

                {/* 시그널 정보 */}
                {selectedReport.influencer_signals && (
                  <div>
                    <h4 className="text-lg font-semibold text-gray-900 mb-2">시그널 정보</h4>
                    <div className="bg-gray-50 rounded-lg p-4 space-y-3">
                      <div className="flex items-center space-x-2">
                        <span className="font-medium">{selectedReport.influencer_signals.stock}</span>
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getSignalColor(selectedReport.influencer_signals.signal)}`}>
                          {selectedReport.influencer_signals.signal}
                        </span>
                      </div>
                      
                      <div>
                        <div className="text-sm text-gray-600 mb-1">핵심 발언:</div>
                        <div className="text-sm bg-white p-3 rounded border italic">
                          "{selectedReport.influencer_signals.key_quote}"
                        </div>
                      </div>

                      {selectedReport.influencer_signals.reasoning && (
                        <div>
                          <div className="text-sm text-gray-600 mb-1">분석 내용:</div>
                          <div className="text-sm bg-white p-3 rounded border whitespace-pre-wrap">
                            {selectedReport.influencer_signals.reasoning}
                          </div>
                        </div>
                      )}

                      <div className="text-xs text-gray-500">
                        발언자: {selectedReport.influencer_signals.speakers?.name || 
                                selectedReport.influencer_signals.influencer_videos?.influencer_channels?.channel_name || 
                                'Unknown'}
                      </div>
                      
                      {selectedReport.influencer_signals.influencer_videos && (
                        <div className="text-xs text-gray-500">
                          영상: {selectedReport.influencer_signals.influencer_videos.title}
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* AI 검토 결과 */}
                {selectedReport.ai_review && (
                  <div>
                    <h4 className="text-lg font-semibold text-gray-900 mb-2">🤖 AI 검토 결과</h4>
                    <div className="bg-blue-50 rounded-lg p-4">
                      <div className="text-sm whitespace-pre-wrap">{selectedReport.ai_review}</div>
                    </div>
                  </div>
                )}

                {/* AI 수정안 및 비교 */}
                {selectedReport.ai_suggestion && selectedReport.influencer_signals && (
                  <div>
                    <h4 className="text-lg font-semibold text-gray-900 mb-2">🔧 AI 수정안</h4>
                    <div className="space-y-4">
                      {(() => {
                        try {
                          const suggestion = parseAiJson(selectedReport.ai_suggestion);
                          const original = selectedReport.influencer_signals;
                          
                          return (
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                              {/* 원본 */}
                              <div className="bg-red-50 rounded-lg p-4">
                                <h5 className="font-medium text-red-800 mb-2">📋 원본 시그널</h5>
                                <div className="space-y-2 text-sm">
                                  <div><span className="font-medium">종목:</span> {original.stock}</div>
                                  <div><span className="font-medium">티커:</span> {original.ticker || 'N/A'}</div>
                                  <div><span className="font-medium">신호:</span> {original.signal}</div>
                                  <div><span className="font-medium">인용문:</span> "{original.key_quote}"</div>
                                  <div><span className="font-medium">타임스탬프:</span> {original.timestamp}</div>
                                  <div><span className="font-medium">분석근거:</span> {original.reasoning || 'N/A'}</div>
                                </div>
                              </div>
                              
                              {/* 수정안 */}
                              <div className="bg-green-50 rounded-lg p-4">
                                <h5 className="font-medium text-green-800 mb-2">✅ AI 수정안</h5>
                                <div className="space-y-2 text-sm">
                                  <div><span className="font-medium">종목:</span> {suggestion.stock}</div>
                                  <div><span className="font-medium">티커:</span> {suggestion.ticker || 'N/A'}</div>
                                  <div><span className="font-medium">신호:</span> {suggestion.signal}</div>
                                  <div><span className="font-medium">인용문:</span> "{suggestion.key_quote}"</div>
                                  <div><span className="font-medium">타임스탬프:</span> {suggestion.timestamp}</div>
                                  <div><span className="font-medium">분석근거:</span> {suggestion.reasoning || 'N/A'}</div>
                                </div>
                              </div>
                            </div>
                          );
                        } catch (e) {
                          return (
                            <div className="bg-yellow-50 rounded-lg p-4">
                              <p className="text-yellow-800 text-sm">AI 수정안 파싱 오류</p>
                              <pre className="text-xs mt-2 overflow-x-auto">{selectedReport.ai_suggestion}</pre>
                            </div>
                          );
                        }
                      })()}
                    </div>
                  </div>
                )}

                {/* 처리 버튼 */}
                <div className="flex justify-end space-x-3">
                  <button
                    onClick={() => setSelectedReport(null)}
                    className="px-4 py-2 text-sm text-gray-600 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
                  >
                    닫기
                  </button>
                  
                  {/* AI 검토 요청 버튼 - ai_review가 없는 경우에만 표시 */}
                  {!selectedReport.ai_review && (
                    <button
                      onClick={() => handleAiReview(selectedReport.id)}
                      disabled={isAiProcessing && aiProcessingId === selectedReport.id}
                      className="px-4 py-2 text-sm text-white bg-purple-600 rounded-lg hover:bg-purple-700 transition-colors flex items-center gap-2 disabled:opacity-50"
                    >
                      {isAiProcessing && aiProcessingId === selectedReport.id ? (
                        <>
                          <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                          AI 검토 중...
                        </>
                      ) : (
                        <>🤖 AI 검토 요청</>
                      )}
                    </button>
                  )}

                  {/* AI 수정안이 있는 경우 승인 버튼 */}
                  {selectedReport.ai_suggestion && (
                    <button
                      onClick={() => handleApproveAiSuggestion(selectedReport)}
                      className="px-4 py-2 text-sm text-white bg-green-600 rounded-lg hover:bg-green-700 transition-colors flex items-center gap-2"
                    >
                      ✅ 수정안 승인
                    </button>
                  )}

                  {/* 거절 버튼 */}
                  <button
                    onClick={() => handleRejectReport(selectedReport.id)}
                    className="px-4 py-2 text-sm text-white bg-red-600 rounded-lg hover:bg-red-700 transition-colors flex items-center gap-2"
                  >
                    ❌ 신고 거절
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}