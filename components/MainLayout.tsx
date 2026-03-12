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

  // auth loading 중에도 레이아웃 바로 렌더 (공개 접근 허용)
  // loading 블로킹 제거 — Supabase auth 응답 기다리지 않음

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
