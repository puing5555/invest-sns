'use client';

import { useState } from 'react';
import { Report, analysts, targetPriceHistory } from '@/data/analystData';
import StarRating from './StarRating';
import AccuracyCircle from './AccuracyCircle';
import { insertSignalReport } from '@/lib/supabase';

interface ReportDetailProps {
  report: Report | null;
  isOpen: boolean;
  onClose: () => void;
}

export default function ReportDetail({ report, isOpen, onClose }: ReportDetailProps) {
  const [liked, setLiked] = useState(false);
  const [likeCount, setLikeCount] = useState(0);
  const [showReportModal, setShowReportModal] = useState(false);
  const [reportReason, setReportReason] = useState('');
  const [reportDetail, setReportDetail] = useState('');
  const [isSubmittingReport, setIsSubmittingReport] = useState(false);

  if (!isOpen || !report) return null;

  const analyst = analysts.find(a => a.name === report.analystName);

  const handleLike = () => {
    setLiked(!liked);
    setLikeCount(prev => liked ? prev - 1 : prev + 1);
  };

  const handleReport = () => {
    setShowReportModal(true);
  };

  const handleReportSubmit = async () => {
    if (!reportReason) {
      alert('신고 사유를 선택해주세요.');
      return;
    }
    if (reportDetail.trim().length < 10) {
      alert('상세 사유를 최소 10자 이상 입력해주세요.');
      return;
    }
    setIsSubmittingReport(true);
    try {
      await insertSignalReport(
        report.id || 'report-unknown',
        reportReason,
        reportDetail.trim()
      );
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
    <div className="fixed inset-0 z-50 flex">
      {/* Backdrop */}
      <div 
        className="flex-1 bg-black/20"
        onClick={onClose}
      />
      
      {/* Panel */}
      <div className="w-[400px] bg-white h-full shadow-xl overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-white border-b border-gray-200 p-4 flex items-center justify-between">
          <h2 className="font-bold text-lg">리포트 상세</h2>
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
            <button
              onClick={onClose}
              className="w-8 h-8 flex items-center justify-center rounded-full hover:bg-[#f8f9fa] transition-colors text-[#8b95a1] text-lg"
            >
              ✕
            </button>
          </div>
        </div>

        <div className="p-4 space-y-6">
          {/* Stock & Title */}
          <div>
            <h3 className="font-bold text-xl text-gray-900 mb-1">{report.stockName}</h3>
            <p className="text-gray-700 mb-2">{report.title}</p>
            <p className="text-sm text-gray-600">
              {report.firm} • {report.analystName} • {report.date}
            </p>
          </div>

          {/* Full AI Summary */}
          <div className="bg-gray-50 p-4 rounded-lg">
            <h4 className="font-semibold mb-2">AI 분석 요약</h4>
            <p className="text-sm text-gray-700 leading-relaxed">
              {report.aiSummaryFull}
            </p>
          </div>

          {/* Target Price History */}
          {report.id === '1' && (
            <div>
              <h4 className="font-semibold mb-3">목표가 히스토리</h4>
              <div className="bg-gray-50 rounded-lg overflow-hidden">
                <table className="w-full text-sm">
                  <thead className="bg-gray-100">
                    <tr>
                      <th className="text-left p-2 font-medium">날짜</th>
                      <th className="text-left p-2 font-medium">목표가</th>
                      <th className="text-left p-2 font-medium">애널리스트</th>
                    </tr>
                  </thead>
                  <tbody>
                    {targetPriceHistory.map((item, index) => (
                      <tr key={index} className="border-t border-gray-200">
                        <td className="p-2">{item.date}</td>
                        <td className="p-2 font-medium">
                          {item.price.toLocaleString()}원
                        </td>
                        <td className="p-2">{item.analyst} ({item.firm})</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Analyst Profile Mini Card */}
          {analyst && (
            <div className="border border-gray-200 rounded-lg p-3">
              <h4 className="font-semibold mb-2">애널리스트 프로필</h4>
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                  <span className="font-medium text-blue-700">
                    {analyst.name.charAt(0)}
                  </span>
                </div>
                <div>
                  <p className="font-medium">{analyst.name}</p>
                  <p className="text-sm text-gray-600">{analyst.firm} • {analyst.sector}</p>
                </div>
                <div className="flex-1 flex justify-end">
                  <AccuracyCircle 
                    percentage={analyst.accuracy}
                    successful={analyst.successful}
                    total={analyst.total}
                    size={48}
                  />
                </div>
              </div>
            </div>
          )}

          {/* Same Stock Other Analysts */}
          <div>
            <h4 className="font-semibold mb-3">동일종목 다른 애널리스트</h4>
            <div className="space-y-2">
              <div className="flex items-center justify-between p-2 bg-gray-50 rounded">
                <div>
                  <span className="font-medium text-sm">박XX (미래에셋)</span>
                  <span className="text-xs text-gray-600 ml-2">목표가 195,000원</span>
                </div>
                <div className="flex items-center space-x-1">
                  <StarRating rating={3} size="sm" />
                  <span className="text-xs">67%</span>
                </div>
              </div>
              <div className="flex items-center justify-between p-2 bg-gray-50 rounded">
                <div>
                  <span className="font-medium text-sm">이YY (KB증권)</span>
                  <span className="text-xs text-gray-600 ml-2">목표가 185,000원</span>
                </div>
                <div className="flex items-center space-x-1">
                  <StarRating rating={4} size="sm" />
                  <span className="text-xs">59%</span>
                </div>
              </div>
            </div>
          </div>

          {/* Community Vote */}
          <div>
            <h4 className="font-semibold mb-3">이 리포트 동의?</h4>
            <div className="mb-3">
              <div className="flex items-center justify-between text-sm mb-1">
                <span>동의</span>
                <span>72%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div className="bg-green-500 h-2 rounded-full" style={{ width: '72%' }}></div>
              </div>
              <div className="flex items-center justify-between text-sm mt-1">
                <span className="text-gray-600">비동의 28%</span>
                <span className="text-gray-600">총 147명 참여</span>
              </div>
            </div>
            
            {/* Sample Comments */}
            <div className="space-y-2 text-sm">
              <div className="bg-gray-50 p-2 rounded">
                <span className="font-medium">투자고수</span>
                <span className="text-gray-600 ml-2">HBM 수혜 맞는듯. 실적 좋아질 것 같아요</span>
              </div>
              <div className="bg-gray-50 p-2 rounded">
                <span className="font-medium">주린이</span>
                <span className="text-gray-600 ml-2">210,000원은 너무 높은 것 아닌가요?</span>
              </div>
            </div>
          </div>

          {/* Related Influencer */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
            <div className="flex items-center space-x-2">
              <span className="text-blue-600">👤</span>
              <span className="text-sm text-blue-700">
                <span className="font-medium">코린이아빠</span>도 이 종목 콜함
              </span>
            </div>
          </div>
        </div>

        {/* 신고 모달 */}
        {showReportModal && (
          <div className="fixed inset-0 bg-black/50 z-[60] flex items-center justify-center p-4" onClick={() => setShowReportModal(false)}>
            <div className="bg-white rounded-xl p-5 w-full max-w-sm" onClick={(e) => e.stopPropagation()}>
              <h3 className="text-lg font-bold text-[#191f28] mb-4">리포트 신고</h3>
              
              <div className="space-y-3 mb-4">
                {['부정확한 정보', '스팸', '기타'].map((reason) => (
                  <label key={reason} className="flex items-center gap-3 cursor-pointer">
                    <input
                      type="radio"
                      name="reportReason"
                      value={reason}
                      checked={reportReason === reason}
                      onChange={(e) => {
                        setReportReason(e.target.value);
                        setReportDetail('');
                      }}
                      className="w-4 h-4 text-[#3182f6]"
                    />
                    <span className="text-sm text-[#191f28]">{reason}</span>
                  </label>
                ))}
              </div>

              {reportReason && (
                <div className="mb-4">
                  <textarea
                    value={reportDetail}
                    onChange={(e) => setReportDetail(e.target.value)}
                    placeholder="상세 사유를 입력해주세요"
                    className="w-full border border-gray-300 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-[#3182f6] p-2 text-sm"
                    rows={4}
                  />
                  {reportDetail.length > 0 && reportDetail.length < 10 && (
                    <p className="text-xs mt-1 text-red-500">
                      최소 10자 이상 입력해주세요 ({reportDetail.length}/10)
                    </p>
                  )}
                </div>
              )}

              <div className="flex gap-2">
                <button
                  onClick={() => {
                    setShowReportModal(false);
                    setReportReason('');
                    setReportDetail('');
                  }}
                  className="flex-1 py-2.5 text-sm text-[#8b95a1] bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
                >
                  취소
                </button>
                <button
                  onClick={handleReportSubmit}
                  disabled={isSubmittingReport || !reportReason || reportDetail.length < 10}
                  className="flex-1 py-2.5 text-sm text-white bg-[#3182f6] rounded-lg hover:bg-[#1b64da] disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  {isSubmittingReport ? '처리 중...' : '신고'}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}