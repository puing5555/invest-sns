'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

const bottomNavItems = [
  { icon: '📊', label: '대시보드', href: '/dashboard' },
  { icon: '🏠', label: '피드', href: '/' },
  { icon: '💼', label: '포트폴리오', href: '/my-portfolio' },
  { icon: '🔍', label: '탐색', href: '/explore' },
  { icon: '👤', label: '프로필', href: '/profile' },
];

export default function BottomNav() {
  const pathname = usePathname();

  return (
    <div className="md:hidden fixed bottom-0 left-0 right-0 bg-white border-t border-[#e8e8e8] z-50">
      <nav className="flex">
        {bottomNavItems.map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex-1 flex flex-col items-center py-3 px-2 ${
                isActive ? 'text-[#3182f6]' : 'text-[#8b95a1]'
              }`}
            >
              <span className="text-xl mb-1">{item.icon}</span>
              <span className="text-xs font-medium">{item.label}</span>
            </Link>
          );
        })}
      </nav>
    </div>
  );
}