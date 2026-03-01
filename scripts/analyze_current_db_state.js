// 현재 DB 상태 상세 분석
import { createClient } from '@supabase/supabase-js';
import fs from 'fs/promises';

const supabaseUrl = 'https://arypzhotxflimroprmdk.supabase.co';
const supabaseServiceKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8';

const supabase = createClient(supabaseUrl, supabaseServiceKey);

// V10 이슈에서 언급된 19개 시그널 ID
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

async function analyzeSpeakerIssues() {
    console.log('🔍 화자 식별 이슈 분석\n');
    
    const results = [];
    
    for (const signalId of SPEAKER_ISSUES) {
        try {
            const { data: signal, error } = await supabase
                .from('influencer_signals')
                .select(`
                    *,
                    speakers(name),
                    influencer_videos(title)
                `)
                .eq('id', signalId)
                .single();

            if (error) {
                console.log(`❌ ${signalId}: 조회 실패 - ${error.message}`);
                continue;
            }

            const videoTitle = signal.influencer_videos?.title || '제목 없음';
            const currentSpeaker = signal.speakers?.name || 'Unknown';
            
            // 영상 제목에서 게스트 추출
            const guestMatch = videoTitle.match(/\|\s*([가-힣]{2,4})\s+/);
            const extractedGuest = guestMatch ? guestMatch[1] : null;
            
            const analysis = {
                signalId,
                stock: signal.stock,
                currentSpeaker,
                videoTitle: videoTitle.substring(0, 60) + '...',
                extractedGuest,
                isCorrect: extractedGuest ? (currentSpeaker === extractedGuest) : 'unclear',
                signal_type: signal.signal,
                key_quote: signal.key_quote?.substring(0, 50) + '...'
            };
            
            results.push(analysis);
            
            const status = analysis.isCorrect === true ? '✅ 정확' : 
                          analysis.isCorrect === false ? '❌ 불일치' : '❓ 불분명';
            
            console.log(`${status} ${signal.stock} - ${currentSpeaker}`);
            console.log(`    영상: ${videoTitle.substring(0, 50)}...`);
            if (extractedGuest) {
                console.log(`    추출된 게스트: ${extractedGuest}`);
            }
            console.log('');
            
        } catch (error) {
            console.error(`오류 (${signalId}):`, error.message);
        }
    }
    
    return results;
}

async function analyzeDuplicateIssues() {
    console.log('\n🔍 중복 시그널 분석\n');
    
    const DUPLICATE_ISSUES = [
        'cd3a96b4-8c52-4dce-884f-5e89a8e228d5',
        '764703cc-157e-46fe-b265-f2253a1d66ba',
        '1cda9f77-c6cf-43b6-83be-6542e9930f58',
        'c250cb34-04cb-4174-9843-8c069f731271',
        'ea49a319-181d-4fec-ac91-063be14c73ab',
        '7ba0f471-6950-4436-8e8f-2ee5989748ce',
        'ffa1dc33-167c-4ea8-9691-5f8aa1bf1f4c',
        'ff0d3e8d-9eaf-4d8a-8bde-0b64224c9a86'
    ];
    
    const results = [];
    
    for (const signalId of DUPLICATE_ISSUES) {
        try {
            const { data: signal, error } = await supabase
                .from('influencer_signals')
                .select(`
                    *,
                    speakers(name),
                    influencer_videos(title, published_at)
                `)
                .eq('id', signalId)
                .single();

            if (error) {
                console.log(`❌ ${signalId}: 조회 실패`);
                continue;
            }

            const analysis = {
                signalId,
                stock: signal.stock,
                speaker: signal.speakers?.name || 'Unknown',
                videoTitle: signal.influencer_videos?.title?.substring(0, 40) + '...' || '제목 없음',
                timestamp: signal.timestamp,
                key_quote: signal.key_quote?.substring(0, 30) + '...',
                videoDate: signal.influencer_videos?.published_at
            };
            
            results.push(analysis);
            
            console.log(`📊 ${signal.stock} - ${signal.speakers?.name}`);
            console.log(`    시간: ${signal.timestamp}초, 영상: ${signal.influencer_videos?.title?.substring(0, 40)}...`);
            console.log(`    내용: ${signal.key_quote?.substring(0, 40)}...`);
            console.log('');
            
        } catch (error) {
            console.error(`오류 (${signalId}):`, error.message);
        }
    }
    
    // 중복 그룹별로 분류
    const groups = {};
    results.forEach(r => {
        const key = `${r.speaker}_${r.videoDate}`;
        if (!groups[key]) {
            groups[key] = [];
        }
        groups[key].push(r);
    });
    
    console.log('\n📊 중복 그룹별 분석:');
    for (const [key, signals] of Object.entries(groups)) {
        if (signals.length > 1) {
            console.log(`\n🔄 그룹: ${key} (${signals.length}개 시그널)`);
            signals.forEach((s, i) => {
                console.log(`  ${i+1}. ${s.stock} (${s.timestamp}초): ${s.key_quote}`);
            });
        }
    }
    
    return results;
}

async function checkOverallStats() {
    console.log('\n📈 전체 DB 통계\n');
    
    try {
        // 전체 시그널 수
        const { count: totalSignals } = await supabase
            .from('influencer_signals')
            .select('*', { count: 'exact', head: true });
        
        console.log(`전체 시그널: ${totalSignals}개`);
        
        // 화자별 분포
        const { data: speakerStats } = await supabase
            .from('influencer_signals')
            .select(`
                speakers(name),
                stock
            `);
        
        const speakerCounts = {};
        speakerStats?.forEach(s => {
            const name = s.speakers?.name || 'Unknown';
            speakerCounts[name] = (speakerCounts[name] || 0) + 1;
        });
        
        console.log('\n👥 화자별 시그널 수:');
        Object.entries(speakerCounts)
            .sort(([,a], [,b]) => b - a)
            .slice(0, 10)
            .forEach(([name, count]) => {
                console.log(`  ${name}: ${count}개`);
            });
            
        // 시그널 타입 분포
        const { data: signalTypes } = await supabase
            .from('influencer_signals')
            .select('signal');
        
        const typeCounts = {};
        signalTypes?.forEach(s => {
            const type = s.signal || 'Unknown';
            typeCounts[type] = (typeCounts[type] || 0) + 1;
        });
        
        console.log('\n📊 시그널 타입 분포:');
        Object.entries(typeCounts)
            .sort(([,a], [,b]) => b - a)
            .forEach(([type, count]) => {
                console.log(`  ${type}: ${count}개`);
            });
            
    } catch (error) {
        console.error('통계 조회 오류:', error);
    }
}

async function main() {
    console.log('🔍 V10.1 DB 상태 상세 분석 시작\n');
    
    const speakerAnalysis = await analyzeSpeakerIssues();
    const duplicateAnalysis = await analyzeDuplicateIssues();
    await checkOverallStats();
    
    const report = {
        timestamp: new Date().toISOString(),
        speakerIssues: speakerAnalysis,
        duplicateIssues: duplicateAnalysis,
        summary: {
            speakerCorrect: speakerAnalysis.filter(s => s.isCorrect === true).length,
            speakerIncorrect: speakerAnalysis.filter(s => s.isCorrect === false).length,
            speakerUnclear: speakerAnalysis.filter(s => s.isCorrect === 'unclear').length,
            duplicateGroups: duplicateAnalysis.length
        }
    };
    
    await fs.writeFile(
        'scripts/v10_db_analysis_results.json',
        JSON.stringify(report, null, 2)
    );
    
    console.log('\n📋 분석 완료');
    console.log(`화자 정확: ${report.summary.speakerCorrect}개`);
    console.log(`화자 불일치: ${report.summary.speakerIncorrect}개`);
    console.log(`화자 불분명: ${report.summary.speakerUnclear}개`);
    console.log(`중복 시그널: ${report.summary.duplicateGroups}개`);
    console.log('\n결과가 scripts/v10_db_analysis_results.json에 저장되었습니다.');
}

main().catch(console.error);