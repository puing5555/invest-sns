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
      <body className="bg-[#f4f4f4] text-[#191f28]">
        <MainLayout>{children}</MainLayout>
      </body>
    </html>
  );
}