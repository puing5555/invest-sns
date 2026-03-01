'use client';

import { useEffect, useState } from 'react';
import { getSignalReports, updateReportStatus } from '@/lib/supabase';

interface SignalReport {
  id: string;
  reason: string;
  detail: string | null;
  created_at: string;
  status: string;
  influencer_signals: {
    id: string;
    stock: string;
    ticker: string | null;
    signal: string;
    quote: string;
    analysis_reasoning: string | null;
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

export default function AdminReportsPage() {
  const [reports, setReports] = useState<SignalReport[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedReport, setSelectedReport] = useState<SignalReport | null>(null);

  useEffect(() => {
    loadReports();
  }, []);

  const loadReports = async () => {
    try {
      const data = await getSignalReports();
      setReports(data);
    } catch (error) {
      console.error('신고 목록 로딩 실패:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleStatusUpdate = async (reportId: string, newStatus: string) => {
    try {
      await updateReportStatus(reportId, newStatus);
      await loadReports(); // 목록 새로고침
      alert('상태가 업데이트되었습니다.');
    } catch (error) {
      console.error('상태 업데이트 실패:', error);
      alert('상태 업데이트에 실패했습니다.');
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
      case '경계': return 'bg-orange-100 text-orange-800';
      case '매도': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#3182f6] mx-auto mb-4"></div>
          <p className="text-gray-600">신고 목록을 불러오는 중...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">신고 관리</h1>
          <p className="text-gray-600">사용자가 신고한 시그널들을 확인하고 관리합니다.</p>
        </div>

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
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      신고일시
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      시그널
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      신고사유
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      상태
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
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
                      <td className="px-6 py-4">
                        <div className="flex flex-col space-y-1">
                          <div className="flex items-center space-x-2">
                            <span className="font-medium text-sm">
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
                          <div className="text-xs text-gray-500 mt-1">{report.detail}</div>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(report.status)}`}>
                          {getStatusText(report.status)}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
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

      {/* 상세 모달 */}
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
                          "{selectedReport.influencer_signals.quote}"
                        </div>
                      </div>

                      {selectedReport.influencer_signals.analysis_reasoning && (
                        <div>
                          <div className="text-sm text-gray-600 mb-1">분석 내용:</div>
                          <div className="text-sm bg-white p-3 rounded border whitespace-pre-wrap">
                            {selectedReport.influencer_signals.analysis_reasoning}
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

                {/* 처리 버튼 */}
                <div className="flex justify-end space-x-2">
                  <button
                    onClick={() => setSelectedReport(null)}
                    className="px-4 py-2 text-sm text-gray-600 bg-gray-100 rounded hover:bg-gray-200 transition-colors"
                  >
                    닫기
                  </button>
                  {selectedReport.status !== 'resolved' && (
                    <button
                      onClick={() => {
                        handleStatusUpdate(selectedReport.id, 'resolved');
                        setSelectedReport(null);
                      }}
                      className="px-4 py-2 text-sm text-white bg-green-600 rounded hover:bg-green-700 transition-colors"
                    >
                      처리 완료
                    </button>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}