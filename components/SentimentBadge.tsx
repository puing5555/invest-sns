interface SentimentBadgeProps {
  sentiment: 'positive' | 'neutral' | 'negative';
  size?: 'sm' | 'md';
}

export default function SentimentBadge({ sentiment, size = 'sm' }: SentimentBadgeProps) {
  const getSentimentStyle = () => {
    switch (sentiment) {
      case 'positive':
        return 'bg-green-100 text-green-700 border-green-200';
      case 'neutral':
        return 'bg-yellow-100 text-yellow-700 border-yellow-200';
      case 'negative':
        return 'bg-red-100 text-red-700 border-red-200';
      default:
        return 'bg-gray-100 text-gray-700 border-gray-200';
    }
  };

  const getSentimentText = () => {
    switch (sentiment) {
      case 'positive':
        return '🟢 긍정';
      case 'neutral':
        return '🟡 중립';
      case 'negative':
        return '🔴 부정';
      default:
        return '⚪ 미분류';
    }
  };

  const sizeClasses = size === 'md' ? 'px-3 py-1.5 text-sm' : 'px-2 py-1 text-xs';

  return (
    <span
      className={`inline-flex items-center rounded-full border font-medium ${getSentimentStyle()} ${sizeClasses}`}
    >
      {getSentimentText()}
    </span>
  );
}