'use client';

import { usePathname } from 'next/navigation';

const pageNames: { [key: string]: string } = {
  '/': '시그널',
  '/feed': '피드',
  '/disclosure': '공시',
  '/influencer': '인플루언서',
  '/notifications': '알림',
  '/ai-bot': 'AI봇',
  '/watchlist': '관심종목',
  '/memo': '메모',
  '/lab': '전략연구실',
  '/news': '뉴스',
  '/analyst': '애널리스트',
  '/guru': '투자 구루',
  '/premium': '프리미엄',
  '/profile': '프로필',
};

export default function Header() {
  const pathname = usePathname();
  const currentPageName = pageNames[pathname] || '페이지';

  return (
    <div className="sticky top-0 z-10 bg-white border-b border-[#e5e7eb] px-6 py-4">
      <h1 className="text-xl font-bold text-[#111827]">{currentPageName}</h1>
    </div>
  );
}