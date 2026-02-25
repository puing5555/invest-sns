'use client';

import VotePoll from './VotePoll';

export interface PostData {
  id: number;
  name: string;
  handle: string;
  time: string;
  initial: string;
  text: string;
  comments: number;
  reposts: number;
  likes: number;
  views: number;
  isSystem?: boolean;
  poll?: {
    options: { label: string; emoji: string; percent: number; color: string }[];
    totalVotes: number;
  };
}

function formatNum(n: number): string {
  if (n >= 10000) return (n / 10000).toFixed(1) + '만';
  if (n >= 1000) return (n / 1000).toFixed(1) + 'K';
  return String(n);
}

export default function FeedPost({ post }: { post: PostData }) {
  const isSystem = post.isSystem;

  return (
    <article
      className={`px-4 py-3 border-b border-[#f0f0f0] transition-colors hover:bg-[#f4f4f4] cursor-pointer ${
        isSystem ? 'border-l-2 border-l-[#f44336] bg-[#fff8f8]' : ''
      }`}
    >
      <div className="flex gap-3">
        {/* Avatar */}
        {isSystem ? (
          <div className="w-10 h-10 flex items-center justify-center flex-shrink-0 text-xl">
            🚨
          </div>
        ) : (
          <div className="w-10 h-10 rounded-full bg-[#2a2a4e] flex items-center justify-center text-white font-bold text-sm flex-shrink-0">
            {post.initial}
          </div>
        )}

        {/* Content */}
        <div className="flex-1 min-w-0">
          {/* Header */}
          <div className="flex items-center gap-1 mb-1">
            <span className="font-bold text-[15px] text-[#191f28] hover:underline cursor-pointer">
              {post.name}
            </span>
            {!isSystem && (
              <span className="text-sm text-[#8b95a1]">@{post.handle}</span>
            )}
            <span className="text-sm text-[#8b95a1]"> · {post.time}</span>
          </div>

          {/* Text */}
          <div className="text-[15px] text-[#191f28] leading-[1.4] whitespace-pre-line mb-2">
            {post.text}
          </div>

          {/* Poll if exists */}
          {post.poll && <VotePoll poll={post.poll} className="mb-3" />}

          {/* Actions */}
          <div className="flex items-center gap-6 pt-1">
            <button className="flex items-center gap-1 text-[#8b95a1] hover:text-[#3182f6] transition-colors group">
              <div className="p-1.5 rounded-full group-hover:bg-[#3182f6]/10">
                💬
              </div>
              <span className="text-sm">{formatNum(post.comments)}</span>
            </button>
            <button className="flex items-center gap-1 text-[#8b95a1] hover:text-[#00c853] transition-colors group">
              <div className="p-1.5 rounded-full group-hover:bg-[#00c853]/10">
                🔄
              </div>
              <span className="text-sm">{formatNum(post.reposts)}</span>
            </button>
            <button className="flex items-center gap-1 text-[#8b95a1] hover:text-[#f44336] transition-colors group">
              <div className="p-1.5 rounded-full group-hover:bg-[#f44336]/10">
                ❤️
              </div>
              <span className="text-sm">{formatNum(post.likes)}</span>
            </button>
            <button className="flex items-center gap-1 text-[#8b95a1] hover:text-[#3182f6] transition-colors group">
              <div className="p-1.5 rounded-full group-hover:bg-[#3182f6]/10">
                📊
              </div>
              <span className="text-sm">{formatNum(post.views)}</span>
            </button>
            <button className="flex items-center gap-1 text-[#8b95a1] hover:text-[#3182f6] transition-colors group ml-auto">
              <div className="p-1.5 rounded-full group-hover:bg-[#3182f6]/10">
                📤
              </div>
            </button>
          </div>
        </div>
      </div>
    </article>
  );
}