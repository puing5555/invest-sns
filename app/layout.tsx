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
      <body className="bg-[#0a0a0a] text-white">
        <div className="flex justify-center min-h-screen">
          <Sidebar />
          <main className="flex-1 min-w-[600px] max-w-[700px] border-l border-r border-[#2a2a2a] mb-16 md:mb-0">
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
