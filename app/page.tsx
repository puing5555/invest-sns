'use client';

import { useState } from 'react';
import FeedCompose from '../components/FeedCompose';
import FeedPost, { PostData } from '../components/FeedPost';

// Real signal data converted from 3protv_signals.json
import { feedPosts as realFeedPosts } from '../data/feedData';

// Convert feedPosts to PostData format
const convertFeedPost = (feedPost: any, index: number) => ({
  id: index + 1,
  name: feedPost.author.name,
  handle: feedPost.author.id,
  avatar: feedPost.author.avatar === '/avatars/default.jpg' ? 'https://i.pravatar.cc/150?img=' + (index % 50 + 1) : feedPost.author.avatar,
  verified: feedPost.author.verified,
  accuracy: feedPost.type === 'signal' ? Math.floor(70 + Math.random() * 25) : undefined,
  time: new Date(feedPost.timestamp).toLocaleTimeString('ko-KR', { 
    hour: '2-digit', 
    minute: '2-digit',
    hour12: false 
  }).replace(':', '시 ') + '분전',
  text: feedPost.content.text + (feedPost.content.signal 
    ? `\n\n🎯 ${feedPost.content.signal.stock} ${feedPost.content.signal.direction}\n신뢰도: ${feedPost.content.signal.confidence === 'high' ? '높음' : feedPost.content.signal.confidence === 'medium' ? '보통' : '낮음'}`
    : ''),
  comments_count: feedPost.engagement.comments,
  reposts: feedPost.engagement.shares,
  likes: feedPost.engagement.likes,
  views: Math.floor(feedPost.engagement.likes * (3 + Math.random() * 10)),
});

// Convert real feed posts to PostData format
const POSTS: PostData[] = realFeedPosts.slice(0, 15).map(convertFeedPost);

const TABS = ['추천', '팔로잉', '구독중'] as const;

export default function FeedPage() {
  const [activeTab, setActiveTab] = useState<string>('추천');

  return (
    <div className="bg-[#f4f4f4] min-h-screen">
      {/* Tabs */}
      <div className="flex border-b border-[#f0f0f0] sticky top-0 bg-white/80 backdrop-blur-md z-10">
        {TABS.map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className="flex-1 py-3.5 text-[15px] font-medium text-[#8b95a1] hover:bg-[#f2f4f6] transition-colors relative"
          >
            <span className={activeTab === tab ? 'font-bold text-[#191f28]' : ''}>
              {tab}
            </span>
            {activeTab === tab && (
              <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-14 h-1 rounded-full bg-[#3182f6]" />
            )}
          </button>
        ))}
      </div>

      {activeTab === '추천' ? (
        <>
          <FeedCompose />
          <div>
            {POSTS.map((post) => (
              <FeedPost key={post.id} post={post} />
            ))}
          </div>
        </>
      ) : (
        <div className="flex items-center justify-center h-60 text-[#8b95a1] text-sm">
          준비중
        </div>
      )}
    </div>
  );
}