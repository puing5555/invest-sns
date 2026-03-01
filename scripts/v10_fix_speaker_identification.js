// V10.1 화자 식별 문제 19건 수정 스크립트
import { createClient } from '@supabase/supabase-js';
import fs from 'fs/promises';

const supabaseUrl = 'https://arypzhotxflimroprmdk.supabase.co';
const supabaseServiceKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8';

const supabase = createClient(supabaseUrl, supabaseServiceKey);

// 화자 식별 문제가 있는 19개 시그널 ID
const SPEAKER_ISSUES = [
    '0d83bde0-d91c-45da-af79-0a360db6c6ad',
    '19d07177-090a-4774-8504-38d177a8117d',
    '33078122-93ea-4001-83bd-58ee6dc8e4df',
    '53975f78-e496-49e8-b92e-8e9c482dbf09',
    '55bf5a77-ff14-4c2b-9da8-a15c7a94ea74',
    '58b2432f-071a-4208-a1d8-90f3f0222517',
    '5a8d8634-625b-4e6a-b93b-47380dbe329c',
    '6ab0f37a-1bac-4010-988a-f14db3e2b1e8',
    '71ff56f8-deb9-49c1-9c18-bc4fd717d666',
    '75042710-e161-4b46-bb9e-ae97f1e0d98a',
    '7ed86fea-e0bb-4604-b0c1-3ba7788966c1',
    '83d4e654-d9db-4e5a-9a69-ac85b0ce0699',
    '9a0f20c2-af24-4c50-b195-5c89d92a6cf9',
    'a9338662-af28-46b7-ac82-84e475646007',
    'ab0044b3-5414-4421-a6a6-5dd9077c3fd0',
    'bb6deb68-005b-489c-9302-1ac7cd050453',
    'c5d155e7-b7da-4127-90a5-02e4cd45c8f7',
    'dfa9fdbc-5485-4a48-a007-14dab596ab31',
    'f13c9ca0-d899-4bb3-9c61-849503831329'
];

// 게스트명 추출 함수 (영상 제목에서 "| 이름 직함" 패턴)
function extractGuestFromTitle(title) {
    const match = title.match(/\|\s*([가-힣]{2,4})\s+([가-힣a-zA-Z]+)/);
    if (match) {
        return {
            name: match[1].trim(),
            title: match[2].trim()
        };
    }
    return null;
}

// 새로운 speaker 생성
async function createSpeaker(name, title, expertise) {
    const { data, error } = await supabase
        .from('speakers')
        .insert({
            name: name,
            title: title,
            expertise: expertise || 'analyst',
            is_influencer: false
        })
        .select()
        .single();

    if (error) {
        console.error(`Speaker 생성 오류 (${name}):`, error);
        return null;
    }

    return data;
}

// 기존 speaker 조회
async function findSpeaker(name) {
    const { data, error } = await supabase
        .from('speakers')
        .select('*')
        .eq('name', name)
        .single();

    if (error && error.code !== 'PGRST116') {
        console.error(`Speaker 조회 오류 (${name}):`, error);
        return null;
    }

    return data;
}

async function fixSpeakerIssue(signalId) {
    try {
        // 1. 시그널 정보 조회 (영상 정보 포함)
        const { data: signal, error: signalError } = await supabase
            .from('influencer_signals')
            .select(`
                *,
                influencer_videos!inner(title, channel_name)
            `)
            .eq('id', signalId)
            .single();

        if (signalError) {
            console.error(`시그널 조회 오류 (${signalId}):`, signalError);
            return false;
        }

        const videoTitle = signal.influencer_videos.title;
        const channelName = signal.influencer_videos.channel_name;
        
        console.log(`\n처리 중: ${signalId}`);
        console.log(`영상 제목: ${videoTitle}`);
        console.log(`채널명: ${channelName}`);

        // 2. 영상 제목에서 게스트 정보 추출
        const guest = extractGuestFromTitle(videoTitle);
        
        if (!guest) {
            console.log(`❌ 게스트 정보를 추출할 수 없음`);
            return false;
        }

        console.log(`추출된 게스트: ${guest.name} ${guest.title}`);

        // 3. 기존 speaker 확인
        let speaker = await findSpeaker(guest.name);
        
        if (!speaker) {
            // 4. 새 speaker 생성
            console.log(`새 Speaker 생성 중: ${guest.name}`);
            speaker = await createSpeaker(guest.name, guest.title, 'analyst');
            
            if (!speaker) {
                console.log(`❌ Speaker 생성 실패`);
                return false;
            }
        }

        // 5. 시그널의 speaker_id 업데이트
        const { error: updateError } = await supabase
            .from('influencer_signals')
            .update({ speaker_id: speaker.id })
            .eq('id', signalId);

        if (updateError) {
            console.error(`시그널 업데이트 오류:`, updateError);
            return false;
        }

        console.log(`✅ 성공: ${guest.name} (ID: ${speaker.id})로 업데이트`);
        return true;

    } catch (error) {
        console.error(`처리 중 오류 (${signalId}):`, error);
        return false;
    }
}

async function main() {
    console.log('🚀 V10.1 화자 식별 문제 수정 시작');
    console.log(`처리할 시그널 수: ${SPEAKER_ISSUES.length}건`);

    const results = {
        total: SPEAKER_ISSUES.length,
        success: 0,
        failed: 0,
        details: []
    };

    for (const signalId of SPEAKER_ISSUES) {
        const success = await fixSpeakerIssue(signalId);
        
        if (success) {
            results.success++;
        } else {
            results.failed++;
        }

        results.details.push({
            signalId,
            success
        });

        // 짧은 대기 (API 제한 방지)
        await new Promise(resolve => setTimeout(resolve, 100));
    }

    console.log('\n📊 수정 결과 요약');
    console.log(`총 처리: ${results.total}건`);
    console.log(`성공: ${results.success}건`);
    console.log(`실패: ${results.failed}건`);
    console.log(`성공률: ${Math.round(results.success / results.total * 100)}%`);

    // 결과를 파일로 저장
    await fs.writeFile(
        'scripts/v10_speaker_fix_results.json',
        JSON.stringify(results, null, 2)
    );

    console.log('\n결과가 scripts/v10_speaker_fix_results.json에 저장되었습니다.');
}

main().catch(console.error);