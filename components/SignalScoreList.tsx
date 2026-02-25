'use client';

import SignalScoreItem, { SignalScoreData } from './SignalScoreItem';

const scores: SignalScoreData[] = [
  {
    rank: 1, stock: '에코프로', score: 87,
    tags: [{ label: '인플루언서3명콜', score: 45 }, { label: '기관순매수', score: 20 }, { label: '거래량급증', score: 12 }, { label: '뉴스긍정', score: 10 }],
    price: '248,000', change: '+3.2%', sparkData: [235, 238, 240, 237, 242, 245, 248],
  },
  {
    rank: 2, stock: 'SK하이닉스', score: 78,
    tags: [{ label: '애널목표가상향', score: 30 }, { label: '외국인순매수', score: 25 }, { label: '실적서프라이즈', score: 23 }],
    price: '182,000', change: '+1.8%', sparkData: [175, 173, 176, 178, 177, 180, 182],
  },
  {
    rank: 3, stock: '삼성전자', score: 72,
    tags: [{ label: '임원매수', score: 25 }, { label: '애널상향', score: 20 }, { label: '배당공시', score: 15 }, { label: '기관순매수', score: 12 }],
    price: '71,200', change: '+0.8%', sparkData: [70, 69, 70, 71, 70, 71, 71.2],
  },
  {
    rank: 4, stock: '아이빔테크놀로지', score: 65,
    tags: [{ label: 'A등급공시', score: 35 }, { label: '인플루언서콜', score: 15 }, { label: '거래량급증', score: 15 }],
    price: '32,400', change: '+5.1%', sparkData: [28, 29, 30, 29, 31, 30, 32.4],
  },
  {
    rank: 5, stock: 'HD한국조선해양', score: 61,
    tags: [{ label: '애널목표가상향', score: 20 }, { label: '외국인순매수', score: 20 }, { label: '뉴스긍정', score: 12 }, { label: '테마강세', score: 9 }],
    price: '187,500', change: '+2.1%', sparkData: [180, 182, 179, 183, 185, 184, 187.5],
  },
];

export default function SignalScoreList() {
  return (
    <div className="bg-white border border-[#f0f0f0] rounded-xl overflow-hidden">
      {scores.map((d) => (
        <SignalScoreItem key={d.rank} d={d} />
      ))}
    </div>
  );
}
