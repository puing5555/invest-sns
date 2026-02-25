'use client';

import { useState } from 'react';
import FeedCompose from '../components/FeedCompose';
import FeedPost, { PostData } from '../components/FeedPost';

const POSTS: PostData[] = [
  {
    id: 1,
    name: '박두환',
    handle: 'doohwan_park',
    initial: '박',
    time: '13시간',
    text: '비트코인이 $45,000을 돌파했습니다! 다음 저항선은 $48,000 수준으로 보입니다. 단기 조정 가능성도 있으니 리스크 관리 잊지 마세요.',
    comments: 142,
    reposts: 89,
    likes: 1247,
    views: 15600,
  },
  {
    id: 2,
    name: '이효석',
    handle: 'hyoseok_lee',
    initial: '이',
    time: '2시간',
    text: 'NVIDIA 실적 발표 앞두고 있는데, 반도체 섹터 전반적으로 긴장감이 돌고 있네요. AI 관련주들 움직임 주의깊게 봐야겠습니다 📊',
    comments: 67,
    reposts: 134,
    likes: 892,
    views: 8945,
  },
  {
    id: 3,
    name: '코린이 아빠',
    handle: 'korini_papa',
    initial: '코',
    time: '5시간',
    text: '오늘 공시 정리:\n아이빔테크놀로지 공급계약 체결. 매출대비 14.77%.\n과거 유사 패턴 D+3 평균 +8.2%.\n주목할만합니다.',
    comments: 23,
    reposts: 45,
    likes: 567,
    views: 4200,
  },
  {
    id: 4,
    name: '🔴 [A등급 공시 속보]',
    handle: '시스템',
    initial: '!',
    time: '10분전',
    text: '와이엠씨 — 자사주 500,000주 소각 결정 (시총대비 3.75%)\n\n🤖 AI 판단: 소형주 대규모 소각, 과거 유사 D+5 +6.3%\n\n이 공시 어떻게 보시나요?',
    comments: 34,
    reposts: 67,
    likes: 234,
    views: 6700,
    isSystem: true,
    poll: {
      options: [
        { label: '호재', emoji: '🟢', percent: 78, color: '#22c55e' },
        { label: '악재', emoji: '🔴', percent: 3, color: '#ef4444' },
        { label: '모르겠다', emoji: '🟡', percent: 19, color: '#eab308' },
      ],
      totalVotes: 142,
    },
  },
  {
    id: 5,
    name: '주식쟁이김과장',
    handle: 'kim_kwajang',
    initial: '김',
    time: '1시간',
    text: 'HD한국조선해양 해명공시 나왔는데, \'미확정\'이라고 했어요. 사실무근이 아니라 미확정 = 진행중 시그널. 3/24 재공시 예정일 체크하세요.',
    comments: 56,
    reposts: 78,
    likes: 445,
    views: 5600,
  },
];

const TABS = ['추천', '팔로잉', '구독중'] as const;

export default function FeedPage() {
  const [activeTab, setActiveTab] = useState<string>('추천');

  return (
    <div className="bg-white min-h-screen">
      {/* Tabs */}
      <div className="flex border-b border-[#eff3f4] sticky top-0 bg-white/80 backdrop-blur-md z-10">
        {TABS.map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className="flex-1 py-3.5 text-[15px] font-medium text-gray-500 hover:bg-gray-50 transition-colors relative"
          >
            <span className={activeTab === tab ? 'font-bold text-gray-900' : ''}>
              {tab}
            </span>
            {activeTab === tab && (
              <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-14 h-1 rounded-full bg-[#00d4aa]" />
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
        <div className="flex items-center justify-center h-60 text-gray-400 text-sm">
          준비중
        </div>
      )}
    </div>
  );
}
