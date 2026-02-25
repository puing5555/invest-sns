'use client';

interface ChatMessageProps {
  message: string;
  isUser: boolean;
  timestamp?: string;
}

export default function ChatMessage({ message, isUser, timestamp }: ChatMessageProps) {
  // Function to parse **bold** text to JSX
  const parseMessage = (text: string) => {
    const parts = text.split(/(\*\*.*?\*\*)/);
    return parts.map((part, index) => {
      if (part.startsWith('**') && part.endsWith('**')) {
        const boldText = part.slice(2, -2);
        // If bold text contains stock names, make them clickable style
        const stockPattern = /(?ì½”?„ë¡œ|?„ì´ë¹”í…Œ?¬ë?ë¡œì?|?¼ì„±?„ì)/;
        if (stockPattern.test(boldText)) {
          return (
            <strong key={index} className="font-bold text-[#3182f6] cursor-pointer hover:underline">
              {boldText}
            </strong>
          );
        }
        return <strong key={index} className="font-bold">{boldText}</strong>;
      }
      return part;
    });
  };

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div className={`flex ${isUser ? 'flex-row-reverse' : 'flex-row'} items-start max-w-[80%]`}>
        {/* Avatar */}
        {!isUser && (
          <div className="w-8 h-8 bg-[#3182f6] rounded-full flex items-center justify-center mr-3 flex-shrink-0">
            <span className="text-white text-sm font-bold">?¤–</span>
          </div>
        )}

        {/* Message bubble */}
        <div
          className={`px-4 py-3 ${
            isUser 
              ? 'bg-[#3182f6] text-white rounded-2xl rounded-tr-sm' 
              : 'bg-[#f2f4f6] text-[#191f28] rounded-2xl rounded-tl-sm'
          } max-w-full word-break`}
        >
          <div className="whitespace-pre-wrap">{parseMessage(message)}</div>
          {timestamp && (
            <div className={`text-xs mt-1 ${isUser ? 'text-green-100' : 'text-[#8b95a1]'}`}>
              {timestamp}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}