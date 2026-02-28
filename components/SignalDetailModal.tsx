'use client';

interface SignalDetail {
  date: string;
  influencer: string;
  signal: string;
  quote: string;
  videoUrl: string;
  confidence?: number;
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
  if (!signal) return null;

  const getSignalBadge = (sig: string) => {
    switch (sig) {
      case '매수': return { emoji: '🔵', color: 'text-blue-600 bg-blue-50 border-blue-200' };
      case '긍정': return { emoji: '🟢', color: 'text-green-600 bg-green-50 border-green-200' };
      case '중립': return { emoji: '🟡', color: 'text-yellow-600 bg-yellow-50 border-yellow-200' };
      case '경계': return { emoji: '🟠', color: 'text-orange-600 bg-orange-50 border-orange-200' };
      case '매도': return { emoji: '🔴', color: 'text-red-600 bg-red-50 border-red-200' };
      default: return { emoji: '⚪', color: 'text-gray-600 bg-gray-50 border-gray-200' };
    }
  };

  const badge = getSignalBadge(signal.signal);

  const getMentionTypeLabel = (type?: string) => {
    switch (type) {
      case 'main_topic': return '메인 주제';
      case 'detailed_analysis': return '상세 분석';
      case 'brief_mention': return '간단 언급';
      case 'comparison': return '비교 언급';
      default: return type || '-';
    }
  };

  return (
    <>
      {/* Overlay */}
      <div
        className="fixed inset-0 bg-black/50 z-50 transition-opacity"
        onClick={onClose}
      />
      {/* Modal */}
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4" onClick={onClose}>
        <div
          className="bg-white rounded-2xl shadow-2xl w-full max-w-md max-h-[85vh] overflow-y-auto"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div className="sticky top-0 bg-white border-b border-[#f0f0f0] p-4 flex items-center justify-between rounded-t-2xl">
            <h3 className="text-lg font-bold text-[#191f28]">시그널 상세</h3>
            <button
              onClick={onClose}
              className="w-8 h-8 flex items-center justify-center rounded-full hover:bg-[#f8f9fa] transition-colors text-[#8b95a1]"
            >
              ✕
            </button>
          </div>

          <div className="p-5 space-y-5">
            {/* Signal badge + influencer */}
            <div className="flex items-center gap-3">
              <div className={`flex items-center gap-2 px-3 py-2 rounded-lg border ${badge.color}`}>
                <span className="text-lg">{badge.emoji}</span>
                <span className="font-bold text-sm">{signal.signal}</span>
              </div>
              {signal.confidence != null && (
                <span className="text-xs text-[#8b95a1] bg-[#f8f9fa] px-2 py-1 rounded-full">
                  확신도 {signal.confidence}%
                </span>
              )}
            </div>

            {/* Info grid */}
            <div className="space-y-3">
              <div className="flex items-center gap-3">
                <span className="text-sm text-[#8b95a1] w-16 flex-shrink-0">발언자</span>
                <span className="text-sm font-medium text-[#191f28]">{signal.influencer}</span>
              </div>
              {signal.channelName && (
                <div className="flex items-center gap-3">
                  <span className="text-sm text-[#8b95a1] w-16 flex-shrink-0">채널</span>
                  <span className="text-sm text-[#191f28]">{signal.channelName}</span>
                </div>
              )}
              <div className="flex items-center gap-3">
                <span className="text-sm text-[#8b95a1] w-16 flex-shrink-0">날짜</span>
                <span className="text-sm text-[#191f28]">
                  {new Date(signal.date).toLocaleDateString('ko-KR', { year: 'numeric', month: 'long', day: 'numeric' })}
                </span>
              </div>
              {signal.timestamp && (
                <div className="flex items-center gap-3">
                  <span className="text-sm text-[#8b95a1] w-16 flex-shrink-0">시점</span>
                  <span className="text-sm text-[#191f28]">{signal.timestamp}</span>
                </div>
              )}
              {signal.mention_type && (
                <div className="flex items-center gap-3">
                  <span className="text-sm text-[#8b95a1] w-16 flex-shrink-0">언급유형</span>
                  <span className="text-sm text-[#191f28]">{getMentionTypeLabel(signal.mention_type)}</span>
                </div>
              )}
            </div>

            {/* Key quote */}
            <div>
              <h4 className="text-sm font-medium text-[#8b95a1] mb-2">핵심발언</h4>
              <div className="bg-[#f8f9fa] rounded-lg p-4 border-l-4 border-[#3182f6]">
                <p className="text-sm text-[#191f28] leading-relaxed whitespace-pre-wrap">
                  &ldquo;{signal.quote}&rdquo;
                </p>
              </div>
            </div>

            {/* Analysis reasoning */}
            {signal.analysis_reasoning && (
              <div>
                <h4 className="text-sm font-medium text-[#8b95a1] mb-2">분석 근거</h4>
                <div className="bg-[#fffbeb] rounded-lg p-4 border-l-4 border-[#f59e0b]">
                  <p className="text-sm text-[#191f28] leading-relaxed whitespace-pre-wrap">
                    {signal.analysis_reasoning}
                  </p>
                </div>
              </div>
            )}

            {/* Video title */}
            {signal.videoTitle && (
              <div>
                <h4 className="text-sm font-medium text-[#8b95a1] mb-2">영상</h4>
                <p className="text-sm text-[#191f28]">{signal.videoTitle}</p>
              </div>
            )}

            {/* Watch button */}
            {signal.videoUrl && signal.videoUrl !== '#' && (
              <a
                href={signal.videoUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="block w-full text-center bg-[#ff0000] hover:bg-[#cc0000] text-white font-medium py-3 rounded-lg transition-colors"
              >
                ▶ 영상보기 →
              </a>
            )}
          </div>
        </div>
      </div>
    </>
  );
}
