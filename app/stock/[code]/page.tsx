interface StockDetailPageProps {
  params: {
    code: string;
  };
}

export async function generateStaticParams() {
  // For static export, we need to define the possible stock codes
  // In a real app, this would come from an API or database
  const stockCodes = ['005930', '086520', '000660', '399720', '009540'];
  
  return stockCodes.map((code) => ({
    code: code,
  }));
}

export default function StockDetailPage({ params }: StockDetailPageProps) {
  return (
    <div className="min-h-screen bg-white flex items-center justify-center">
      <div className="text-center">
        <h1 className="text-2xl font-bold text-gray-800">
          종목 상세 - {params.code}
        </h1>
        <p className="text-gray-500 mt-2">상세 페이지를 준비중입니다</p>
      </div>
    </div>
  );
}