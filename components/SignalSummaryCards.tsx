'use client';

const summaryCards = [
  { icon: '📋', title: 'A등급 공시 2건', sub: '아이빔테크 공급계약, 씨케이솔루션 자사주소각', bg: 'bg-green-50 border-green-200' },
  { icon: '👤', title: '인플루언서 콜 5건', sub: '에코프로 3명 동시 콜 🔥', bg: 'bg-blue-50 border-blue-200' },
  { icon: '👔', title: '임원 매수 감지 1건', sub: '삼성전자 부사장 3일연속 매수', bg: 'bg-yellow-50 border-yellow-200' },
  { icon: '🎯', title: '애널 목표가 상향 3건', sub: 'SK하이닉스 컨센 상향 집중', bg: 'bg-purple-50 border-purple-200' },
];

export default function SignalSummaryCards() {
  return (
    <div className="flex gap-3 overflow-x-auto pb-2">
      {summaryCards.map((c, i) => (
        <div
          key={i}
          className={`min-w-[180px] flex-shrink-0 rounded-xl border p-4 cursor-pointer hover:shadow-md transition-shadow ${c.bg}`}
        >
          <div className="text-2xl mb-2">{c.icon}</div>
          <p className="font-bold text-sm text-gray-900">{c.title}</p>
          <p className="text-xs text-gray-500 mt-1">{c.sub}</p>
        </div>
      ))}
    </div>
  );
}
