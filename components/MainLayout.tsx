'use client';

import { usePathname } from 'next/navigation';
import Sidebar from './Sidebar';
import RightSidebar from './RightSidebar';
import BottomNav from './BottomNav';
import Header from './Header';

export default function MainLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const showRightSidebar = pathname === '/';

  return (
    <div className="flex min-h-screen w-full">
      <Sidebar />
      <main className="flex-1 min-w-0 border-l border-r border-[#e8e8e8] mb-16 md:mb-0">
        <Header />
        {children}
      </main>
      {showRightSidebar && <RightSidebar />}
      <BottomNav />
    </div>
  );
}
