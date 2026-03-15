import InfluencerProfileClient from './InfluencerProfileClient';
import speakerSlugMap from '@/data/speaker_slugs.json';

export default function InfluencerProfilePage({ params }: { params: { id: string } }) {
  return <InfluencerProfileClient id={params.id} />;
}

export function generateStaticParams() {
  // data/speaker_slugs.json: { slug: name } 형태
  const slugs = Object.keys(speakerSlugMap as Record<string, string>);
  return slugs.map(slug => ({ id: slug }));
}
