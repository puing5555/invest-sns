'use client';

import { useState, useEffect } from 'react';
import { insertSignalReport, insertSignalVote, insertSignalMemo } from '@/lib/supabase';

interface SignalDetail {
  id?: string;
  date: string;
  influencer: string;
  signal: string;
  quote: string;
  videoUrl: string;
  confidence?: number | string;
  analysis_reasoning?: string;
  mention_type?: string;
  timestamp?: string;
  videoTitle?: string;
  channelName?: string;
  ticker?: string;
  likeCount?: number;
}

// AI 내부 메모 필터링
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

interface SignalDetailModalProps {
  signal: SignalDetail | null;
  onClose: () => void;
}

export default function SignalDetailModal({ signal, onClose }: SignalDetailModalProps) {
  const [showMemoInput, setShowMemoInput] = useState(false);
  const [memoText, setMemoText] = useState('');
  const [liked, setLiked] = useState(false);
  const [likeCount, setLikeCount] = useState(signal?.likeCount || 0);
  const [showReportModal, setShowReportModal] = useState(false);
  const [reportReason, setReportReason] = useState('');
  const [reportDetail, setReportDetail] = useState('');
  const [isSubmittingReport, setIsSubmittingReport] = useState(false);

  if (!signal) return null;

  const getSignalStyle = (sig: string) => {
    switch (sig) {
      case '매수': return 'text-green-600 bg-green-50';
      case '긍정': return 'text-blue-600 bg-blue-50';
      case '중립': return 'text-yellow-600 bg-yellow-50';
      case '경계': return 'text-orange-600 bg-orange-50';
      case '매도': return 'text-red-600 bg-red-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  const formatDate = (d: string) => {
    try {
      return new Date(d).toLocaleDateString('ko-KR', { year: 'numeric', month: 'long', day: 'numeric' });
    } catch { return d; }
  };

  // timestamp "3:52" → seconds 232
  const timestampToSeconds = (ts?: string): number | null => {
    if (!ts) return null;
    const parts = ts.split(':').map(Number);
    if (parts.length === 2) return parts[0] * 60 + parts[1];
    if (parts.length === 3) return parts[0] * 3600 + parts[1] * 60 + parts[2];
    return null;
  };

  const getVideoUrlWithTimestamp = () => {
    if (!signal.videoUrl || signal.videoUrl === '#') return null;
    const seconds = timestampToSeconds(signal.timestamp);
    if (seconds && (signal.videoUrl.includes('youtube.com') || signal.videoUrl.includes('youtu.be'))) {
      const sep = signal.videoUrl.includes('?') ? '&' : '?';
      return `${signal.videoUrl}${sep}t=${seconds}`;
    }
    return signal.videoUrl;
  };

  // influencer: 호스트=채널명, 게스트=화자명. channelName으로 구분
  const isHost = !signal.channelName || !signal.influencer || signal.channelName === signal.influencer || signal.channelName.includes(signal.influencer) || signal.influencer.includes(signal.channelName);

  const handleLike = async () => {
    if (!signal?.id) {
      alert('시그널 ID가 없습니다.');
      return;
    }

    if (liked) {
      setLiked(false);
      setShowMemoInput(false);
      return;
    }

    try {
      await insertSignalVote(signal.id);
      setLiked(true);
      setLikeCount(prev => prev + 1);
      setShowMemoInput(true);
    } catch (error) {
      console.error('좋아요 처리 중 오류:', error);
      alert('좋아요 처리에 실패했습니다.');
    }
  };

  const handleSaveMemo = async () => {
    if (!signal?.id || !memoText.trim()) {
      alert('메모 내용을 입력해주세요.');
      return;
    }

    try {
      await insertSignalMemo(signal.id, memoText.trim());
      alert('저장되었습니다');
      setShowMemoInput(false);
      setMemoText('');
    } catch (error) {
      console.error('메모 저장 중 오류:', error);
      alert('메모 저장에 실패했습니다.');
    }
  };

  const handleReport = () => {
    if (!signal?.id) {
      alert('시그널 ID가 없습니다.');
      return;
    }
    setShowReportModal(true);
  };

  const handleReportSubmit = async () => {
    if (!signal?.id || !reportReason) {
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
        signal.id, 
        reportReason, 
        reportDetail.trim()
      );
      
      alert('신고가 접수되었습니다.');
      setShowReportModal(false);
      setReportReason('');
      setReportDetail('');
    } catch (error) {
      console.error('신고 처리 중 오류:', error);
      alert('신고 접수에 실패했습니다. 다시 시도해주세요.');
    } finally {
      setIsSubmittingReport(false);
    }
  };

  const videoHref = getVideoUrlWithTimestamp();

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
          {/* Top bar: 시그널 (left) / 좋아요·신고·X (right) */}
          <div className="sticky top-0 bg-white z-10 px-4 pt-4 pb-2 flex items-center justify-between rounded-t-2xl">
            <div className="flex items-center gap-2">
              <span className={`px-2.5 py-1 rounded-full text-xs font-bold ${getSignalStyle(signal.signal)}`}>
                {signal.signal}
              </span>
            </div>
            <div className="flex items-center gap-1">
              <button
                onClick={handleLike}
                className={`transition-colors text-lg px-3 py-2 rounded-lg flex items-center gap-1 border-none outline-none ${liked ? 'text-red-500' : 'text-[#8b95a1] hover:text-red-400'}`}
              >
                {liked ? '❤️' : '♡'}{likeCount > 0 && <span className="text-sm">{likeCount}</span>}
              </button>
              <button 
                onClick={handleReport}
                className="text-[#8b95a1] hover:text-red-500 transition-colors text-sm px-2 py-1 rounded-lg"
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

          <div className="px-5 pb-5 space-y-4">
            {/* 영상 제목 + 날짜 한 줄 */}
            <div>
              <h2 className="text-lg font-bold text-[#191f28] leading-snug">
                {signal.videoTitle || signal.quote?.slice(0, 40) + '...'}
              </h2>
              <p className="text-sm text-[#8b95a1] mt-1">{formatDate(signal.date)}</p>
            </div>

            {/* 발언자 표시: influencer 필드에 이미 올바른 형태 */}
            <div className="text-sm text-[#8b95a1]">
              {isHost ? (
                <>채널: <span className="font-medium text-[#191f28]">{signal.influencer}</span></>
              ) : (
                <>발언자: <span className="font-medium text-[#191f28]">{signal.influencer}</span></>
              )}
            </div>

            {/* 핵심발언 인용 블록 */}
            <div className="bg-[#f8f9fa] rounded-xl p-4 border-l-4 border-[#3182f6]">
              <div className="text-xs font-medium text-[#8b95a1] mb-2">핵심발언</div>
              <p className="text-[15px] text-[#191f28] leading-relaxed italic">
                &ldquo;{signal.quote}&rdquo;
              </p>
            </div>

            {/* 영상 내용 요약 */}
            <div>
              <div className="text-xs font-medium text-[#8b95a1] mb-2">내용요약</div>
              {signal.analysis_reasoning ? (
                <p className="text-sm text-[#333d4b] leading-relaxed whitespace-pre-wrap">
                  {filterInternalText(signal.analysis_reasoning)}
                </p>
              ) : (
                <p className="text-sm text-[#8b95a1] italic">이 영상은 요약이 제공되지 않습니다</p>
              )}
            </div>

            {/* 메모 입력 (좋아요 클릭 시) */}
            {showMemoInput && (
              <div className="bg-[#fffbeb] rounded-xl p-4 border border-[#fde68a]">
                <div className="text-xs font-medium text-[#92400e] mb-2">💛 메모 남기기</div>
                <textarea
                  value={memoText}
                  onChange={(e) => setMemoText(e.target.value)}
                  placeholder="이 시그널에 대한 메모를 남겨보세요..."
                  className="w-full text-sm border border-[#fde68a] rounded-lg p-2 resize-none h-20 focus:outline-none focus:ring-1 focus:ring-[#f59e0b]"
                />
                <div className="flex justify-end gap-2 mt-2">
                  <button
                    onClick={() => setShowMemoInput(false)}
                    className="text-xs text-[#8b95a1] px-3 py-1.5 rounded-lg hover:bg-[#f8f9fa]"
                  >
                    취소
                  </button>
                  <button
                    onClick={handleSaveMemo}
                    className="text-xs text-white bg-[#f59e0b] px-3 py-1.5 rounded-lg hover:bg-[#d97706] font-medium"
                  >
                    저장
                  </button>
                </div>
              </div>
            )}

            {/* 버튼: 차트보기 + 영상보기 */}
            <div className="flex gap-3">
              {signal.ticker && (
                <a
                  href={`/invest-sns/stock/${signal.ticker}?tab=influencer`}
                  className="flex-1 text-center bg-[#3182f6] hover:bg-[#1b64da] text-white font-medium py-3.5 rounded-xl transition-colors text-[15px]"
                >
                  📊 차트보기
                </a>
              )}
              {videoHref && (
                <a
                  href={videoHref}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex-1 text-center bg-[#ff0000] hover:bg-[#cc0000] text-white font-medium py-3.5 rounded-xl transition-colors text-[15px]"
                >
                  ▶️ 영상보기
                </a>
              )}
            </div>

            {/* 신고 모달 */}
            {showReportModal && (
              <div className="absolute inset-0 bg-black/50 rounded-2xl flex items-center justify-center p-4">
                <div className="bg-white rounded-xl p-5 w-full max-w-sm">
                  <h3 className="text-lg font-bold text-[#191f28] mb-4">시그널 신고</h3>
                  
                  <div className="space-y-3 mb-4">
                    {['시그널 틀림', '종목 오류', '발언 왜곡', '기타'].map((reason) => (
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
                    <div className="mb-4" style={{ animation: 'fadeIn 0.2s ease-in' }}>
                      <textarea
                        value={reportDetail}
                        onChange={(e) => setReportDetail(e.target.value)}
                        placeholder="상세 사유를 입력해주세요"
                        className="w-full border border-gray-300 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-[#3182f6]"
                        style={{ padding: '8px', fontSize: '14px', lineHeight: '1.5' }}
                        rows={4}
                      />
                      {reportDetail.length > 0 && reportDetail.length < 10 && (
                        <p className="text-xs mt-1" style={{ color: '#ef4444' }}>
                          최소 10자 이상 입력해주세요 ({reportDetail.length}/10)
                        </p>
                      )}
                    </div>
                  )}

                  <style jsx>{`
                    @keyframes fadeIn {
                      from { opacity: 0; transform: translateY(-4px); }
                      to { opacity: 1; transform: translateY(0); }
                    }
                  `}</style>

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
      </div>
    </>
  );
}
