'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';

const navItems = [
  { icon: '🏠', label: '피드', href: '/' },
  { icon: '📡', label: '시그널', href: '/signal' },
  { icon: '📋', label: '공시', href: '/disclosure' },
  { icon: '👤', label: '인플루언서', href: '/influencer' },
  { icon: '🎯', label: '애널리스트', href: '/analyst' },
  { icon: '🐋', label: '투자 구루', href: '/guru' },
  { icon: '⭐️', label: '관심종목', href: '/watchlist' },
  { icon: '🤖', label: 'AI봇', href: '/ai-bot' },
  { icon: '🧪', label: '전략연구실', href: '/lab' },
  { icon: '📰', label: '뉴스', href: '/news' },
  { icon: '🔔', label: '알림', href: '/notifications' },
  { icon: '📝', label: '메모', href: '/memo' },
  { icon: '👤', label: '프로필', href: '/profile' },
];

export default function Sidebar() {
  const pathname = usePathname();
  const { user, signOut } = useAuth();

  return (
    <div className="hidden md:flex flex-col w-[240px] xl:w-[240px] lg:w-[70px] h-screen bg-white border-r border-[#e8e8e8] sticky top-0">
      {/* Logo and Title */}
      <div className="p-6 border-b border-[#e8e8e8]">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 bg-[#3182f6] rounded-full flex items-center justify-center">
            <span className="text-white font-bold">$</span>
          </div>
          <span className="font-bold text-xl xl:block lg:hidden text-[#191f28]">투자SNS</span>
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
              className={`flex items-center space-x-3 p-3 rounded-2xl hover:bg-[#f8f9fa] transition-colors ${
                isActive 
                  ? 'bg-[#f2f4f6] text-[#3182f6] font-semibold' 
                  : 'text-[#191f28]'
              }`}
            >
              <span className="text-xl">{item.icon}</span>
              <span className="xl:block lg:hidden">{item.label}</span>
            </Link>
          );
        })}
      </nav>

      {/* User Profile */}
      <div className="p-4 border-t border-[#e8e8e8]">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-[#3182f6] rounded-full flex items-center justify-center">
            <span className="text-white font-medium">{user?.email?.[0]?.toUpperCase() || '?'}</span>
          </div>
          <div className="xl:block lg:hidden flex-1 min-w-0">
            <p className="font-medium text-[#191f28] truncate text-sm">{user?.email || '사용자'}</p>
            <button
              onClick={signOut}
              className="text-xs text-[#8b95a1] hover:text-red-500 transition"
            >
              로그아웃
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}