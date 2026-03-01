'use client';

const V9_SIGNAL_COLORS: Record<string, string> = {
  '매수': 'bg-green-600 text-white',
  '긍정': 'bg-blue-600 text-white',
  '중립': 'bg-gray-500 text-white',
  '경계': 'bg-yellow-600 text-white',
  '매도': 'bg-red-800 text-white',
};

interface SignalCardProps {
  signal: string;
  stock: string;
  speaker: string;
  channelName?: string;
  confidence?: string;
  keyQuote?: string;
  reasoning?: string;
  videoTitle?: string;
  date: string;
  videoUrl?: string;
  onClick?: () => void;
}

export default function SignalCard({
  signal, stock, speaker, channelName,
  keyQuote, reasoning, videoTitle, date, videoUrl, onClick,
}: SignalCardProps) {
  const signalColor = V9_SIGNAL_COLORS[signal] || 'bg-gray-500 text-white';

  // 호스트: 채널명만. 게스트: 화자 이름만
  const isHost = channelName && speaker && (channelName.includes(speaker) || speaker.includes(channelName) || speaker === channelName);

  return (
    <div
      className="bg-white rounded-xl p-5 shadow-sm border border-gray-100 hover:shadow-md transition-shadow cursor-pointer"
      onClick={onClick}
    >
      <div className="flex items-center space-x-3 mb-2">
        <div className={`px-3 py-1 rounded-full text-xs font-medium ${signalColor}`}>
          {signal}
        </div>
        <span className="font-bold text-lg text-gray-900">{stock}</span>
        <span className="text-sm text-gray-500">
          {isHost ? channelName : speaker}
        </span>
      </div>
      {(keyQuote || reasoning) && (
        <p className="text-[15px] text-gray-700 italic mb-2 leading-relaxed line-clamp-2">
          &ldquo;{keyQuote || reasoning}&rdquo;
        </p>
      )}
      {videoTitle && (
        <p className="text-sm text-gray-500 mb-2 line-clamp-1">
          📹 {videoTitle}
        </p>
      )}
      <div className="flex items-center space-x-4 text-xs text-gray-400">
        <span>{date}</span>
        {videoUrl && videoUrl !== '#' && (
          <a href={videoUrl} target="_blank" rel="noopener noreferrer"
             className="text-blue-500 hover:text-blue-700"
             onClick={(e) => e.stopPropagation()}>
            영상보기 →
          </a>
        )}
      </div>
    </div>
  );
}
