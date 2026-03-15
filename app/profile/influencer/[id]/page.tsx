import InfluencerProfileClient from './InfluencerProfileClient';
import speakerSlugs from '@/data/speaker_slugs.json';

export default function InfluencerProfilePage({ params }: { params: { id: string } }) {
  return <InfluencerProfileClient id={params.id} />;
}

export function generateStaticParams() {
  // data/speaker_slugs.json에서 읽음 (빌드 전 node scripts/generate_speaker_slugs.js로 생성)
  const slugs = speakerSlugs as string[];
  return slugs.map(slug => ({ id: slug }));
}
