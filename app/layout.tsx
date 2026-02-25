import type { Metadata } from "next";
import "./globals.css";
import MainLayout from "@/components/MainLayout";

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
        <MainLayout>{children}</MainLayout>
      </body>
    </html>
  );
}
