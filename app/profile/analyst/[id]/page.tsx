import { notFound } from 'next/navigation';
import { analysts } from '@/data/analystData';
import AnalystProfileClient from './AnalystProfileClient';

// 정적 경로 생성
export function generateStaticParams() {
  return analysts.map((analyst) => ({
    id: analyst.id,
  }));
}

export default function AnalystProfilePage({ params }: { params: { id: string } }) {
  const analyst = analysts.find(a => a.id === params.id);
  
  if (!analyst) {
    notFound();
  }

  return <AnalystProfileClient analyst={analyst} />;
}