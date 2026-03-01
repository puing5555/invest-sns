// DB 스키마 확인 스크립트
import { createClient } from '@supabase/supabase-js';

const supabaseUrl = 'https://arypzhotxflimroprmdk.supabase.co';
const supabaseServiceKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8';

const supabase = createClient(supabaseUrl, supabaseServiceKey);

async function checkSchema() {
    console.log('🔍 DB 스키마 확인 중...\n');

    try {
        // influencer_videos 테이블 샘플 조회
        console.log('📹 influencer_videos 테이블:');
        const { data: videos, error: videosError } = await supabase
            .from('influencer_videos')
            .select('*')
            .limit(1);

        if (videosError) {
            console.error('영상 테이블 오류:', videosError);
        } else if (videos && videos.length > 0) {
            console.log('컬럼들:', Object.keys(videos[0]));
            console.log('샘플 데이터:', videos[0]);
        }

        console.log('\n👤 speakers 테이블:');
        const { data: speakers, error: speakersError } = await supabase
            .from('speakers')
            .select('*')
            .limit(3);

        if (speakersError) {
            console.error('화자 테이블 오류:', speakersError);
        } else if (speakers && speakers.length > 0) {
            console.log('컬럼들:', Object.keys(speakers[0]));
            console.log('샘플 데이터:');
            speakers.forEach((speaker, i) => {
                console.log(`  ${i+1}. ${speaker.name} (${speaker.title || '제목없음'})`);
            });
        }

        console.log('\n📊 influencer_signals 테이블:');
        const { data: signals, error: signalsError } = await supabase
            .from('influencer_signals')
            .select('*')
            .limit(1);

        if (signalsError) {
            console.error('시그널 테이블 오류:', signalsError);
        } else if (signals && signals.length > 0) {
            console.log('컬럼들:', Object.keys(signals[0]));
            console.log('샘플 데이터:', {
                id: signals[0].id,
                stock: signals[0].stock,
                signal_type: signals[0].signal_type,
                speaker_id: signals[0].speaker_id,
                video_id: signals[0].video_id
            });
        }

        // 문제가 있는 시그널 하나만 조회해보기
        console.log('\n🔍 문제 시그널 조회:');
        const { data: problemSignal, error: problemError } = await supabase
            .from('influencer_signals')
            .select(`
                *,
                speakers(name, title),
                influencer_videos(*)
            `)
            .eq('id', '0d83bde0-d91c-45da-af79-0a360db6c6ad')
            .single();

        if (problemError) {
            console.error('문제 시그널 조회 오류:', problemError);
        } else {
            console.log('문제 시그널 데이터:');
            console.log('  시그널:', {
                stock: problemSignal.stock,
                signal_type: problemSignal.signal_type
            });
            console.log('  화자:', problemSignal.speakers);
            console.log('  영상 컬럼들:', Object.keys(problemSignal.influencer_videos));
            console.log('  영상 제목:', problemSignal.influencer_videos.title);
        }

    } catch (error) {
        console.error('전체 오류:', error);
    }
}

checkSchema();