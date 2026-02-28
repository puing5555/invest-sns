import InfluencerProfileClient from './InfluencerProfileClient';
import { getAllSpeakerSlugs, speakerToSlug } from '@/lib/speakerSlugs';
import { createClient } from '@supabase/supabase-js';

export default function InfluencerProfilePage({ params }: { params: { id: string } }) {
  return <InfluencerProfileClient id={params.id} />;
}

export async function generateStaticParams() {
  // 매핑된 slug + DB의 모든 발언자 slug
  const knownSlugs = getAllSpeakerSlugs();

  try {
    const supabase = createClient(
      process.env.NEXT_PUBLIC_SUPABASE_URL || '',
      process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || ''
    );
    const { data } = await supabase
      .from('influencer_signals')
      .select('speaker_id')
      .limit(500);

    if (data) {
      const dbSpeakers = [...new Set(data.map((d: any) => d.speaker_id).filter(Boolean))];
      const dbSlugs = dbSpeakers.map((name: string) => speakerToSlug(name));
      const allSlugs = [...new Set([...knownSlugs, ...dbSlugs])];
      return allSlugs.map(slug => ({ id: slug }));
    }
  } catch (e) {
    console.error('Failed to fetch speakers from DB:', e);
  }

  return knownSlugs.map(slug => ({ id: slug }));
}
