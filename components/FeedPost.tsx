'use client';

import Link from 'next/link';
import VotePoll from './VotePoll';

export interface PostData {
  id: number;
  name: string;
  handle: string;
  avatar: string; // URL or 'system'
  time: string;
  text: string;
  verified?: boolean;
  accuracy?: number;
  isSystem?: boolean;
  comments_count: number;
  reposts: number;
  likes: number;
  views: number;
  poll?: { options: { label: string; emoji: string; percent: number; color: string }[], totalVotes: number };
  popularComments?: { emoji: string; name: string; handle: string; likes: number; text: string }[];
  totalComments?: number; // for "댓글 X개 모두 보기" link
}

function formatNum(n: number): string {
  if (n >= 10000) return (n / 10000).toFixed(1) + '만';
  if (n >= 1000) return (n / 1000).toFixed(1) + 'K';
  return String(n);
}

// Function to parse hashtags in text
function parseHashtags(text: string) {
  return text.split(/(\s|^)(#[가-힣a-zA-Z0-9]+)/g).map((part, index) => {
    if (part.startsWith('#')) {
      return (
        <span key={index} className="text-[#3182f6] font-medium">
          {part}
        </span>
      );
    }
    return part;
  });
}

export default function FeedPost({ post }: { post: PostData }) {
  const isSystem = post.isSystem;

  return (
    <article
      className={`px-4 py-3 border-b border-[#f0f0f0] transition-colors hover:bg-[#f4f4f4] cursor-pointer ${
        isSystem ? 'bg-[#f8f9ff]' : 'bg-white'
      }`}
    >
      <div className="flex gap-3">
        {/* Avatar */}
        <Link href={`/profile/${post.handle}`} className="flex-shrink-0">
          {isSystem ? (
            <div className="w-10 h-10 rounded-full bg-[#3182f6] flex items-center justify-center text-white text-lg">
              🤖
            </div>
          ) : (
            <img 
              src={post.avatar} 
              alt={post.name}
              className="w-10 h-10 rounded-full object-cover"
            />
          )}
        </Link>

        {/* Content */}
        <div className="flex-1 min-w-0">
          {/* Header */}
          <div className="flex items-center gap-1 mb-1">
            <Link href={`/profile/${post.handle}`} className="flex items-center gap-1">
              <span className="font-bold text-[15px] text-[#191f28] hover:underline cursor-pointer">
                {post.name}
              </span>
              {post.verified && <span className="text-blue-500">✅</span>}
              {post.accuracy && (
                <span className="text-xs text-[#8b95a1] bg-[#f2f4f6] px-1.5 py-0.5 rounded">
                  적중률 {post.accuracy}%
                </span>
              )}
            </Link>
            {!isSystem && (
              <span className="text-sm text-[#8b95a1]">@{post.handle}</span>
            )}
            <span className="text-sm text-[#8b95a1]"> · {post.time}</span>
          </div>

          {/* Text */}
          <div className="text-[15px] text-[#191f28] leading-[1.4] whitespace-pre-line mb-2">
            {parseHashtags(post.text)}
          </div>

          {/* Poll if exists */}
          {post.poll && <VotePoll poll={post.poll} className="mb-3" />}

          {/* Actions */}
          <div className="flex items-center gap-6 pt-1 mb-2">
            <button className="flex items-center gap-1 text-[#8b95a1] hover:text-[#3182f6] transition-colors group">
              <div className="p-1.5 rounded-full group-hover:bg-[#3182f6]/10">
                💬
              </div>
              <span className="text-sm">{formatNum(post.comments_count)}</span>
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

          {/* Popular Comments */}
          {post.popularComments && post.likes >= 1000 && (
            <div className="bg-[#f2f4f6] rounded-lg p-3 mt-2">
              {post.popularComments.map((comment, index) => (
                <div key={index} className="flex gap-2 mb-2 last:mb-0">
                  <span className="text-2xl w-7 h-7 flex items-center justify-center">
                    {comment.emoji}
                  </span>
                  <div className="flex-1">
                    <div className="flex items-center gap-1 mb-1">
                      <span className="font-bold text-[13px] text-[#191f28]">
                        {comment.name}
                      </span>
                      <span className="text-[13px] text-[#8b95a1]">
                        @{comment.handle}
                      </span>
                      <span className="text-[13px] text-[#8b95a1]">
                        👍 {comment.likes}
                      </span>
                    </div>
                    <p className="text-[14px] text-[#191f28]">
                      {comment.text}
                    </p>
                  </div>
                </div>
              ))}
              {post.totalComments && (
                <Link 
                  href="#" 
                  className="text-[#3182f6] text-sm font-medium mt-2 inline-block"
                >
                  💬 댓글 {post.totalComments}개 모두 보기
                </Link>
              )}
            </div>
          )}
        </div>
      </div>
    </article>
  );
}