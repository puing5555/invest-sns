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
      className={`px-4 py-3 border-b border-[#eff3f4] transition-colors hover:bg-[#f7f9fa] cursor-pointer ${
        isSystem ? 'border-l-2 border-l-[#ff4444] bg-[#fff8f8]' : ''
      }`}
    >
      <div className="flex gap-3">
        {/* Avatar */}
        {isSystem ? (
          <div className="w-10 h-10 flex items-center justify-center flex-shrink-0 text-xl">
            🔴
          </div>
        ) : (
          <div className="w-10 h-10 rounded-full bg-[#2a2a4e] flex items-center justify-center text-white font-bold text-sm flex-shrink-0">
            {post.initial}
          </div>
        )}

        {/* Content */}
        <div className="flex-1 min-w-0">
          {/* Header */}
          <div className="flex items-center gap-1 text-[15px]">
            <span className="font-bold text-gray-900 truncate">{post.name}</span>
            <span className="text-gray-500 truncate">@{post.handle}</span>
            <span className="text-gray-500">·</span>
            <span className="text-gray-500 whitespace-nowrap">{post.time}</span>
            <button className="ml-auto text-gray-400 hover:text-gray-600 flex-shrink-0">
              ···
            </button>
          </div>

          {/* Body */}
          <p className="text-[15px] text-gray-900 mt-0.5 whitespace-pre-wrap leading-relaxed">
            {post.text}
          </p>

          {/* Poll (system posts) */}
          {post.poll && (
            <VotePoll options={post.poll.options} totalVotes={post.poll.totalVotes} />
          )}

          {/* Action bar */}
          <div className="flex items-center justify-between mt-3 max-w-[420px]">
            <ActionBtn icon="💬" count={post.comments} hoverColor="hover:text-blue-500" />
            <ActionBtn icon="🔄" count={post.reposts} hoverColor="hover:text-green-500" />
            <ActionBtn icon="❤️" count={post.likes} hoverColor="hover:text-red-500" />
            <ActionBtn icon="📊" count={post.views} hoverColor="hover:text-blue-400" />
            <div className="flex items-center gap-1">
              <button className="text-gray-400 hover:text-blue-500 text-xs transition-colors">🔗</button>
              <button className="text-gray-400 hover:text-blue-500 text-xs transition-colors">🔖</button>
            </div>
          </div>
        </div>
      </div>
    </article>
  );
}

function ActionBtn({
  icon,
  count,
  hoverColor,
}: {
  icon: string;
  count: number;
  hoverColor: string;
}) {
  return (
    <button
      className={`flex items-center gap-1 text-gray-400 ${hoverColor} text-xs transition-colors group`}
    >
      <span className="group-hover:scale-110 transition-transform">{icon}</span>
      <span>{formatNum(count)}</span>
    </button>
  );
}
