import InfluencerProfileClient from './InfluencerProfileClient';
import { getAllSpeakerSlugs } from '@/lib/speakerSlugs';

export default function InfluencerProfilePage({ params }: { params: { id: string } }) {
  return <InfluencerProfileClient id={params.id} />;
}

export async function generateStaticParams() {
  return getAllSpeakerSlugs().map(slug => ({ id: slug }));
}
