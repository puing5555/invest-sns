import StockDetailClient from './StockDetailClient';

interface StockDetailPageProps {
  params: {
    code: string;
  };
}

export async function generateStaticParams() {
  const stockCodes = ['005930', '086520', '000660', '399720', '009540'];
  
  return stockCodes.map((code) => ({
    code: code,
  }));
}

export default function StockDetailPage({ params }: StockDetailPageProps) {
  return <StockDetailClient code={params.code} />;
}