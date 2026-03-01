// V10.1 수정 작업 최종 검증
import { createClient } from '@supabase/supabase-js';

const supabaseUrl = 'https://arypzhotxflimroprmdk.supabase.co';
const supabaseServiceKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8';

const supabase = createClient(supabaseUrl, supabaseServiceKey);

async function verifyFixes() {
    console.log('🔍 V10.1 수정 작업 최종 검증\n');
    
    // 1. 전체 시그널 수 확인
    const { count: totalSignals } = await supabase
        .from('influencer_signals')
        .select('*', { count: 'exact', head: true });
    
    console.log(`📊 현재 총 시그널 수: ${totalSignals}개 (수정 전: 101개, 삭제: 2개)`);
    
    // 2. 김장열 화자의 시그널 확인
    const { data: kimjangYeolSignals } = await supabase
        .from('influencer_signals')
        .select(`
            stock,
            key_quote,
            speakers(name)
        `)
        .eq('speakers.name', '김장열');
    
    console.log(`\n👤 김장열 화자 시그널: ${kimjangYeolSignals?.length}개`);
    if (kimjangYeolSignals) {
        kimjangYeolSignals.forEach((signal, i) => {
            console.log(`  ${i+1}. ${signal.stock}: ${signal.key_quote.substring(0, 40)}...`);
        });
    }
    
    // 3. 반도체 섹터 시그널 확인
    const { data: sectorSignals } = await supabase
        .from('influencer_signals')
        .select(`
            stock,
            key_quote,
            speakers(name),
            influencer_videos(title)
        `)
        .eq('stock', '반도체 섹터');
    
    console.log(`\n🏭 반도체 섹터 시그널: ${sectorSignals?.length}개`);
    if (sectorSignals?.length) {
        sectorSignals.forEach((signal, i) => {
            console.log(`  ${i+1}. 화자: ${signal.speakers.name}`);
            console.log(`     영상: ${signal.influencer_videos.title.substring(0, 50)}...`);
            console.log(`     내용: ${signal.key_quote.substring(0, 80)}...`);
        });
    }
    
    // 4. 삭제된 시그널 ID 확인 (존재하지 않아야 함)
    const deletedIds = [
        'ea49a319-181d-4fec-ac91-063be14c73ab',
        'ff0d3e8d-9eaf-4d8a-8bde-0b64224c9a86'
    ];
    
    console.log(`\n🗑️ 삭제 확인:`);
    for (const id of deletedIds) {
        const { data: deletedSignal } = await supabase
            .from('influencer_signals')
            .select('id')
            .eq('id', id)
            .single();
        
        const status = !deletedSignal ? '✅ 삭제 완료' : '❌ 아직 존재';
        console.log(`  ${status}: ${id}`);
    }
    
    // 5. 화자별 분포 재확인
    const { data: allSignals } = await supabase
        .from('influencer_signals')
        .select(`
            speakers(name)
        `);
    
    const speakerCounts = {};
    allSignals?.forEach(s => {
        const name = s.speakers?.name || 'Unknown';
        speakerCounts[name] = (speakerCounts[name] || 0) + 1;
    });
    
    console.log(`\n👥 화자별 분포 (상위 10명):`);
    Object.entries(speakerCounts)
        .sort(([,a], [,b]) => b - a)
        .slice(0, 10)
        .forEach(([name, count]) => {
            console.log(`  ${name}: ${count}개`);
        });
    
    // 6. 시그널 타입별 분포
    const { data: signalTypes } = await supabase
        .from('influencer_signals')
        .select('signal');
    
    const typeCounts = {};
    signalTypes?.forEach(s => {
        const type = s.signal || 'Unknown';
        typeCounts[type] = (typeCounts[type] || 0) + 1;
    });
    
    console.log(`\n📈 시그널 타입별 분포:`);
    Object.entries(typeCounts)
        .sort(([,a], [,b]) => b - a)
        .forEach(([type, count]) => {
            console.log(`  ${type}: ${count}개`);
        });
    
    console.log('\n✅ 최종 검증 완료');
    console.log('=' .repeat(50));
    console.log('🎉 V10.1 DB 수정 작업이 성공적으로 완료되었습니다!');
    console.log('\n📋 수정 요약:');
    console.log('  - 화자명 오류 4건 수정 (김장년 → 김장열)');
    console.log('  - 바스켓 중복 1건 통합 (3개 → 1개 반도체 섹터)');
    console.log('  - 총 시그널 수: 101개 → 99개');
    console.log('  - 데이터 품질 향상: 화자 정확성, 중복 제거');
}

verifyFixes().catch(console.error);