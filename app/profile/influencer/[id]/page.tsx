import InfluencerProfileClient from './InfluencerProfileClient';

export default function InfluencerProfilePage({ params }: { params: { id: string } }) {
  return <InfluencerProfileClient id={params.id} />;
}

export async function generateStaticParams() {
  return [{ id: 'syuka' }];
}
