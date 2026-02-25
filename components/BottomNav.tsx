'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

const bottomNavItems = [
  { icon: '📡', label: '시그널', href: '/' },
  { icon: '🏠', label: '피드', href: '/feed' },
  { icon: '📋', label: '공시', href: '/disclosure' },
  { icon: '🔔', label: '알림', href: '/notifications' },
  { icon: '👤', label: '프로필', href: '/profile' },
];

export default function BottomNav() {
  const pathname = usePathname();

  return (
    <div className="md:hidden fixed bottom-0 left-0 right-0 bg-[#f7f9fa] border-t border-[#e5e7eb] z-50">
      <nav className="flex">
        {bottomNavItems.map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex-1 flex flex-col items-center py-3 px-2 ${
                isActive ? 'text-[#00d4aa]' : 'text-[#6b7280]'
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