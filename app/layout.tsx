import type { Metadata } from "next";
import "./globals.css";
import Sidebar from "@/components/Sidebar";
import RightSidebar from "@/components/RightSidebar";
import BottomNav from "@/components/BottomNav";
import Header from "@/components/Header";

export const metadata: Metadata = {
  title: "투자SNS",
  description: "투자 소셜 네트워크 서비스",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ko">
      <body className="bg-white text-[#111827]">
        <div className="flex min-h-screen w-full">
          <Sidebar />
          <main className="flex-1 min-w-0 border-l border-r border-[#e5e7eb] mb-16 md:mb-0">
            <Header />
            {children}
          </main>
          <RightSidebar />
          <BottomNav />
        </div>
      </body>
    </html>
  );
}
