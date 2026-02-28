'use client';

import { useState } from 'react';

interface SignalDetail {
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
}

interface SignalDetailModalProps {
  signal: SignalDetail | null;
  onClose: () => void;
}

export default function SignalDetailModal({ signal, onClose }: SignalDetailModalProps) {
  const [showMemoInput, setShowMemoInput] = useState(false);
  const [memoText, setMemoText] = useState('');
  const [liked, setLiked] = useState(false);

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
    if (seconds && signal.videoUrl.includes('youtube.com') || signal.videoUrl.includes('youtu.be')) {
      const sep = signal.videoUrl.includes('?') ? '&' : '?';
      return `${signal.videoUrl}${sep}t=${seconds}`;
    }
    return signal.videoUrl;
  };

  // 호스트 판단: 발언자명이 채널명에 포함되면 호스트 → 채널명 표시, 아니면 게스트 → 채널명 숨김
  const isHost = signal.channelName && signal.influencer && signal.channelName.includes(signal.influencer);
  const showChannel = isHost && signal.channelName !== signal.influencer;

  const handleLike = () => {
    if (liked) {
      setLiked(false);
      setShowMemoInput(false);
      return;
    }
    setLiked(true);
    setShowMemoInput(true);
  };

  const handleSaveMemo = () => {
    console.log('Memo saved:', memoText);
    setShowMemoInput(false);
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
              {/* */}
            </div>
            <div className="flex items-center gap-1">
              <button
                onClick={handleLike}
                className={`transition-colors text-sm px-2 py-1 rounded-lg ${liked ? 'text-red-500' : 'text-[#8b95a1] hover:text-red-400'}`}
              >
                {liked ? '❤️' : '🤍'}
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
            {/* 영상 제목 + 날짜 한 줄 */}
            <div>
              <h2 className="text-lg font-bold text-[#191f28] leading-snug">
                {signal.videoTitle || signal.quote?.slice(0, 40) + '...'}
              </h2>
              <p className="text-sm text-[#8b95a1] mt-1">{formatDate(signal.date)}</p>
            </div>

            {/* 발언자 · 채널 */}
            <div className="text-sm text-[#8b95a1]">
              발언자: <span className="font-medium text-[#191f28]">{signal.influencer}</span>
              {showChannel && (
                <span> · 채널: <span className="font-medium text-[#191f28]">{signal.channelName}</span></span>
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
            {signal.analysis_reasoning && (
              <div>
                <div className="text-xs font-medium text-[#8b95a1] mb-2">영상 내용 요약</div>
                <p className="text-sm text-[#333d4b] leading-relaxed whitespace-pre-wrap">
                  {signal.analysis_reasoning}
                </p>
              </div>
            )}

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

            {/* 영상보기 버튼 - 타임스탬프 시점부터 재생 */}
            {videoHref && (
              <a
                href={videoHref}
                target="_blank"
                rel="noopener noreferrer"
                className="block w-full text-center bg-[#ff0000] hover:bg-[#cc0000] text-white font-medium py-3.5 rounded-xl transition-colors text-[15px]"
              >
                ▶️ 영상보기 →
              </a>
            )}
          </div>
        </div>
      </div>
    </>
  );
}
