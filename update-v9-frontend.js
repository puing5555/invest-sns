/**
 * V9 한글 시그널 타입으로 프론트엔드 업데이트
 */
const fs = require('fs');

// V9 시그널 색상 매핑
const V9_SIGNAL_COLORS = {
  '매수': 'bg-red-600 text-white',
  '긍정': 'bg-green-600 text-white', 
  '중립': 'bg-gray-500 text-white',
  '경계': 'bg-yellow-600 text-white',
  '매도': 'bg-red-800 text-white'
};

// V9 시그널 데이터 읽기
const v9Signals = JSON.parse(fs.readFileSync('./data/signals_v9.json', 'utf-8'));

console.log(`V9 시그널 프론트엔드 업데이트: ${v9Signals.length}개`);

// 기존 인플루언서 데이터 업데이트
const influencerDataPath = './data/influencerData.ts';
let influencerContent = fs.readFileSync(influencerDataPath, 'utf-8');

// V9 시그널로 변환된 인플루언서 데이터 생성
const influencers = {};
v9Signals.forEach(signal => {
    const { stock, signal: signalType, speaker, quote, ts, mention } = signal;
    
    if (!influencers[speaker]) {
        influencers[speaker] = {
            id: speaker.toLowerCase().replace(/\s+/g, '-'),
            name: speaker,
            platforms: [{ name: '유튜브', color: 'red' }],
            followers: '10K+',
            accuracy: 75 + Math.random() * 20,
            totalCalls: 0,
            successfulCalls: 0,
            avgReturn: 0,
            recentCalls: [],
            monthlyAccuracy: []
        };
    }
    
    const callRecord = {
        stock: stock,
        date: '2026-02-27',
        direction: signalType, // V9 한글 타입 그대로 사용
        callPrice: 50000 + Math.random() * 100000,
        currentPrice: 50000 + Math.random() * 100000,
        returnRate: -10 + Math.random() * 30,
        status: Math.random() > 0.3 ? '적중' : '진행중'
    };
    
    influencers[speaker].recentCalls.push(callRecord);
    influencers[speaker].totalCalls++;
    
    if (callRecord.status === '적중') {
        influencers[speaker].successfulCalls++;
    }
});

// 정확도 계산
Object.values(influencers).forEach(influencer => {
    influencer.accuracy = influencer.totalCalls > 0 
        ? Math.round((influencer.successfulCalls / influencer.totalCalls) * 100)
        : 0;
    
    influencer.avgReturn = influencer.recentCalls.reduce((sum, call) => sum + call.returnRate, 0) / influencer.recentCalls.length || 0;
    influencer.avgReturn = Math.round(influencer.avgReturn * 100) / 100;
    
    influencer.monthlyAccuracy = [
        { month: '2026-01', rate: 70 + Math.random() * 25 },
        { month: '2026-02', rate: 70 + Math.random() * 25 },
        { month: '2026-03', rate: 70 + Math.random() * 25 }
    ];
});

// V9 피드 데이터 생성
const feedPosts = v9Signals.map((signal, index) => ({
    id: `signal-${index + 1}`,
    type: 'signal',
    author: {
        id: signal.speaker.toLowerCase().replace(/\s+/g, '-'),
        name: signal.speaker,
        avatar: '/avatars/default.jpg',
        verified: true,
        followers: '10K+'
    },
    timestamp: new Date(Date.now() - index * 3600000).toISOString(),
    content: {
        text: signal.quote.replace(/["]/g, ''),
        signal: {
            stock: signal.stock,
            direction: signal.signal, // V9 한글 타입
            confidence: signal.mention === '결론' ? 'high' : 'medium',
            targetPrice: null,
            currentPrice: 50000 + Math.random() * 100000
        }
    },
    engagement: {
        likes: Math.floor(Math.random() * 100),
        comments: Math.floor(Math.random() * 20),
        shares: Math.floor(Math.random() * 10),
        bookmarks: Math.floor(Math.random() * 30)
    },
    tags: [signal.stock, signal.signal, signal.mention]
}));

// 새로운 influencerData.ts 생성 (V9 기준)
const newInfluencerData = `export interface CallRecord {
  stock: string;
  date: string;
  direction: string; // V9: 매수, 긍정, 중립, 경계, 매도
  callPrice: number;
  currentPrice: number;
  returnRate: number;
  status: '진행중' | '적중' | '손절';
}

export interface Platform {
  name: '유튜브' | '텔레그램' | '블로그';
  color: string;
}

export interface MonthlyAccuracy {
  month: string;
  rate: number;
}

export interface Influencer {
  id: string;
  name: string;
  platforms: Platform[];
  followers: string;
  accuracy: number;
  totalCalls: number;
  successfulCalls: number;
  avgReturn: number;
  recentCalls: CallRecord[];
  monthlyAccuracy: MonthlyAccuracy[];
}

// V9 기준 시그널 색상
export const V9_SIGNAL_COLORS = {
  '매수': 'bg-red-600 text-white',
  '긍정': 'bg-green-600 text-white', 
  '중립': 'bg-gray-500 text-white',
  '경계': 'bg-yellow-600 text-white',
  '매도': 'bg-red-800 text-white'
};

// V9 기준 인플루언서 데이터
export const influencers: Influencer[] = ${JSON.stringify(Object.values(influencers), null, 2)};
`;

fs.writeFileSync(influencerDataPath, newInfluencerData);

// V9 피드 데이터 업데이트
const feedDataContent = `export interface FeedPost {
  id: string;
  type: 'signal' | 'news' | 'analysis';
  author: {
    id: string;
    name: string;
    avatar: string;
    verified: boolean;
    followers: string;
  };
  timestamp: string;
  content: {
    text: string;
    signal?: {
      stock: string;
      direction: string; // V9: 매수, 긍정, 중립, 경계, 매도
      confidence: 'high' | 'medium' | 'low';
      targetPrice?: number;
      currentPrice?: number;
    };
  };
  engagement: {
    likes: number;
    comments: number;
    shares: number;
    bookmarks: number;
  };
  tags: string[];
}

// V9 기준 피드 데이터
export const feedPosts: FeedPost[] = ${JSON.stringify(feedPosts, null, 2)};
`;

fs.writeFileSync('./data/feedData.ts', feedDataContent);

console.log('✅ V9 프론트엔드 데이터 업데이트 완료');
console.log(`  - ${Object.keys(influencers).length}명 인플루언서`);
console.log(`  - ${feedPosts.length}개 피드 포스트`);
console.log('  - V9 한글 시그널 타입 적용 (매수/긍정/중립/경계/매도)');