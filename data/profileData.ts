export interface Activity {
  id: string;
  description: string;
  icon: string;
  timeAgo: string;
}

export interface Call {
  id: string;
  stockName: string;
  type: '매수' | '매도';
  price: number;
  date: string;
  returnRate: number;
  status: '진행중' | '적중' | '손절';
}

export interface Profile {
  nickname: string;
  joinDate: string;
  bio: string;
  followers: number;
  following: number;
  calls: number;
  totalCalls: number;
  winRate: number;
  avgReturn: number;
}

export const profileData: Profile = {
  nickname: '투자고수김',
  joinDate: '2025.01.15',
  bio: '2차전지/반도체 스윙 트레이더',
  followers: 128,
  following: 45,
  calls: 23,
  totalCalls: 23,
  winRate: 65,
  avgReturn: 8.4,
};

export const activitiesData: Activity[] = [
  {
    id: '1',
    description: '에코프로 공시에 댓글',
    icon: '💬',
    timeAgo: '2시간 전',
  },
  {
    id: '2',
    description: '아이빔테크 호재 투표',
    icon: '🗳',
    timeAgo: '5시간 전',
  },
  {
    id: '3',
    description: '코린이아빠 팔로우',
    icon: '👤',
    timeAgo: '어제',
  },
  {
    id: '4',
    description: 'SK하이닉스 매수콜 등록',
    icon: '📡',
    timeAgo: '어제',
  },
  {
    id: '5',
    description: '삼성전자 메모 작성',
    icon: '📝',
    timeAgo: '2일 전',
  },
];

export const callsData: Call[] = [
  {
    id: '1',
    stockName: '에코프로',
    type: '매수',
    price: 248000,
    date: '02/20',
    returnRate: 3.2,
    status: '진행중',
  },
  {
    id: '2',
    stockName: 'SK하이닉스',
    type: '매수',
    price: 175000,
    date: '02/18',
    returnRate: 4.0,
    status: '적중',
  },
  {
    id: '3',
    stockName: '카카오',
    type: '매수',
    price: 52000,
    date: '02/10',
    returnRate: -5.1,
    status: '손절',
  },
  {
    id: '4',
    stockName: '아이빔테크',
    type: '매수',
    price: 30000,
    date: '02/08',
    returnRate: 8.0,
    status: '적중',
  },
  {
    id: '5',
    stockName: 'HD한국조선',
    type: '매수',
    price: 180000,
    date: '02/05',
    returnRate: 4.2,
    status: '적중',
  },
];