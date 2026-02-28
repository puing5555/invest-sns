import InfluencerProfileClient from './InfluencerProfileClient';

export default function InfluencerProfilePage({ params }: { params: { id: string } }) {
  return <InfluencerProfileClient id={params.id} />;
}

export async function generateStaticParams() {
  // URL-encoded speaker names
  const speakers = [
    '이효석', '조진표', '코린이아빠', '박지훈', '배재원',
    '김동훈', '김장년', '고연수', '이건희', '장우진',
    '김장열', '박병창', '박명성', '달란트투자', 'syuka',
  ];
  return speakers.map(name => ({ id: encodeURIComponent(name) }));
}
