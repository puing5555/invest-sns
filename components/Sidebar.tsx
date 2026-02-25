'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

const navItems = [
  { icon: '📡', label: '시그널', href: '/' },
  { icon: '🏠', label: '피드', href: '/feed' },
  { icon: '📋', label: '공시', href: '/disclosure' },
  { icon: '👤', label: '인플루언서', href: '/influencer' },
  { icon: '🔔', label: '알림', href: '/notifications' },
  { icon: '🤖', label: 'AI봇', href: '/ai-bot' },
  { icon: '⭐️', label: '관심종목', href: '/watchlist' },
  { icon: '📝', label: '메모', href: '/memo' },
  { icon: '🧪', label: '전략연구실', href: '/lab' },
  { icon: '📰', label: '뉴스', href: '/news' },
  { icon: '🎯', label: '애널리스트', href: '/analyst' },
  { icon: '👑', label: '프리미엄', href: '/premium' },
  { icon: '👤', label: '프로필', href: '/profile' },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <div className="hidden md:flex flex-col w-[240px] xl:w-[240px] lg:w-[70px] h-screen bg-[#1a1a2e] border-r border-[#2a2a2a] sticky top-0">
      {/* Logo and Title */}
      <div className="p-6 border-b border-[#2a2a2a]">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 bg-[#00d4aa] rounded-full flex items-center justify-center">
            <span className="text-black font-bold">$</span>
          </div>
          <span className="font-bold text-xl xl:block lg:hidden">투자SNS</span>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-4 py-6 space-y-2">
        {navItems.map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center space-x-3 p-3 rounded-lg hover:bg-[#2a2a2a] transition-colors ${
                isActive 
                  ? 'bg-[#2a2a2a] font-bold border-l-4 border-[#00d4aa]' 
                  : ''
              }`}
            >
              <span className="text-xl">{item.icon}</span>
              <span className="xl:block lg:hidden">{item.label}</span>
            </Link>
          );
        })}
      </nav>

      {/* User Profile */}
      <div className="p-4 border-t border-[#2a2a2a]">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-gray-600 rounded-full flex items-center justify-center">
            <span className="text-white font-medium">사</span>
          </div>
          <div className="xl:block lg:hidden">
            <p className="font-medium">사용자</p>
            <p className="text-sm text-[#888]">@username</p>
          </div>
        </div>
      </div>
    </div>
  );
}