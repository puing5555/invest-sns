'use client';

import { usePathname } from 'next/navigation';
import Sidebar from './Sidebar';
import RightSidebar from './RightSidebar';
import BottomNav from './BottomNav';
import Header from './Header';
import { AuthProvider, useAuth } from '@/context/AuthContext';

const AUTH_PAGES = ['/login', '/signup'];

function LayoutInner({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const { user, loading } = useAuth();
  const isAuthPage = AUTH_PAGES.includes(pathname);
  const showRightSidebar = pathname === '/';

  // Auth pages: no sidebar, no header
  if (isAuthPage) {
    return <>{children}</>;
  }

  // Loading state
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#f4f4f4]">
        <div className="text-center">
          <div className="text-4xl mb-3">📡</div>
          <div className="text-[#8b95a1]">로딩 중...</div>
        </div>
      </div>
    );
  }

  // Not logged in → redirect to login
  if (!user) {
    if (typeof window !== 'undefined') {
      window.location.href = '/invest-sns/login';
    }
    return null;
  }

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

export default function MainLayout({ children }: { children: React.ReactNode }) {
  return (
    <AuthProvider>
      <LayoutInner>{children}</LayoutInner>
    </AuthProvider>
  );
}
