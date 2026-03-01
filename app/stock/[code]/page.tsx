import StockDetailClient from './StockDetailClient';

interface StockDetailPageProps {
  params: {
    code: string;
  };
}

export async function generateStaticParams() {
  try {
    // Supabase에서 고유 ticker 목록을 가져오기
    const response = await fetch(
      'https://arypzhotxflimroprmdk.supabase.co/rest/v1/influencer_signals?select=ticker',
      {
        headers: {
          'apikey': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIwMDYxMTAsImV4cCI6MjA4NzU4MjExMH0.qcqFIvYRiixwu609Wjj9H3HxscU8vNpo9nS_KQ3f00A',
          'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIwMDYxMTAsImV4cCI6MjA4NzU4MjExMH0.qcqFIvYRiixwu609Wjj9H3HxscU8vNpo9nS_KQ3f00A'
        }
      }
    );
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    
    // null을 제거하고 고유 ticker 목록 생성 (한국 종목코드 6자리만 필터링)
    const uniqueTickers = [...new Set(
      data
        .map((item: any) => item.ticker)
        .filter((ticker: string | null) => 
          ticker && 
          /^[0-9]{6}$/.test(ticker) // 6자리 숫자인 한국 종목코드만
        )
    )];
    
    // 기존 하드코딩 종목도 포함 (중복 제거됨)
    const hardcodedCodes = ['005930', '086520', '000660', '399720', '009540'];
    const allCodes = [...new Set([...uniqueTickers, ...hardcodedCodes])];
    
    console.log('Generated static params for stock codes:', allCodes.length, 'codes');
    
    return allCodes.map((code) => ({
      code: code,
    }));
  } catch (error) {
    console.error('Error fetching stock codes for static generation:', error);
    // 오류 시 기존 하드코딩 종목으로 폴백
    const fallbackCodes = ['005930', '086520', '000660', '399720', '009540'];
    return fallbackCodes.map((code) => ({
      code: code,
    }));
  }
}

export default function StockDetailPage({ params }: StockDetailPageProps) {
  return <StockDetailClient code={params.code} />;
}