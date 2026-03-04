import StockDetailClient from './StockDetailClient';
import stockTickers from '@/data/stock_tickers.json';

interface StockDetailPageProps {
  params: {
    code: string;
  };
}

export async function generateStaticParams() {
  // 로컬 JSON 파일에서 ticker 목록 읽기 (빌드 시 네트워크 의존성 제거)
  // data/stock_tickers.json은 빌드 전 스크립트로 생성됨
  const tickers = stockTickers as string[];
  console.log('Generated static params for stock codes:', tickers.length, 'codes');
  return tickers.map((code) => ({ code }));
}

export default function StockDetailPage({ params }: StockDetailPageProps) {
  return <StockDetailClient code={params.code} />;
}