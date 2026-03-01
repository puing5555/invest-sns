// V10.1 정확한 DB 수정 작업
import { createClient } from '@supabase/supabase-js';
import fs from 'fs/promises';

const supabaseUrl = 'https://arypzhotxflimroprmdk.supabase.co';
const supabaseServiceKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8';

const supabase = createClient(supabaseUrl, supabaseServiceKey);

// 화자명 수정이 필요한 4개 시그널 (김장년 → 김장열)
const SPEAKER_CORRECTIONS = [
    {
        id: '75042710-e161-4b46-bb9e-ae97f1e0d98a', 
        stock: '마이크론',
        wrongSpeaker: '김장년',
        correctSpeaker: '김장열'
    },
    {
        id: '7ed86fea-e0bb-4604-b0c1-3ba7788966c1',
        stock: '삼성전자', 
        wrongSpeaker: '김장년',
        correctSpeaker: '김장열'
    },
    {
        id: '83d4e654-d9db-4e5a-9a69-ac85b0ce0699',
        stock: 'SK하이닉스',
        wrongSpeaker: '김장년', 
        correctSpeaker: '김장열'
    },
    {
        id: 'dfa9fdbc-5485-4a48-a007-14dab596ab31',
        stock: '엔비디아',
        wrongSpeaker: '김장년',
        correctSpeaker: '김장열'
    }
];

// 바스켓 중복 통합 대상
const BASKET_CONSOLIDATIONS = [
    {
        group: '배재규_반도체_바스켓',
        baseSignal: 'cd3a96b4-8c52-4dce-884f-5e89a8e228d5', // TSMC - 가장 긴 설명
        deleteSignals: [
            'ea49a319-181d-4fec-ac91-063be14c73ab', // 엔비디아
            'ff0d3e8d-9eaf-4d8a-8bde-0b64224c9a86'  // SK하이닉스
        ],
        newStock: '반도체 섹터',
        newQuote: 'GPU 생태계 핵심 포트폴리오: 엔비디아(설계) 20% + TSMC(생산) 20% + SK하이닉스(HBM) 20%로 AI 반도체 전체 밸류체인에 투자하라'
    }
];

async function fixSpeakerNames() {
    console.log('🔧 화자명 수정 작업 시작\n');
    
    const results = [];
    
    // 1. 올바른 화자 ID 찾기
    const { data: correctSpeaker } = await supabase
        .from('speakers')
        .select('id, name')
        .eq('name', '김장열')
        .single();
    
    if (!correctSpeaker) {
        console.log('❌ 김장열 화자를 찾을 수 없음');
        return [];
    }
    
    console.log(`✅ 김장열 화자 ID: ${correctSpeaker.id}`);
    
    // 2. 각 시그널 수정
    for (const correction of SPEAKER_CORRECTIONS) {
        try {
            const { error } = await supabase
                .from('influencer_signals')
                .update({ speaker_id: correctSpeaker.id })
                .eq('id', correction.id);
            
            if (error) {
                console.error(`❌ 수정 실패 (${correction.id}):`, error.message);
                results.push({ ...correction, success: false, error: error.message });
            } else {
                console.log(`✅ 수정 완료: ${correction.stock} - ${correction.wrongSpeaker} → ${correction.correctSpeaker}`);
                results.push({ ...correction, success: true });
            }
            
        } catch (error) {
            console.error(`오류 (${correction.id}):`, error.message);
            results.push({ ...correction, success: false, error: error.message });
        }
    }
    
    return results;
}

async function consolidateBaskets() {
    console.log('\n🔄 바스켓 중복 통합 작업 시작\n');
    
    const results = [];
    
    for (const consolidation of BASKET_CONSOLIDATIONS) {
        try {
            console.log(`📦 ${consolidation.group} 통합 중...`);
            
            // 1. 베이스 시그널 업데이트
            const { error: updateError } = await supabase
                .from('influencer_signals')
                .update({
                    stock: consolidation.newStock,
                    key_quote: consolidation.newQuote
                })
                .eq('id', consolidation.baseSignal);
            
            if (updateError) {
                console.error(`❌ 베이스 시그널 업데이트 실패:`, updateError.message);
                continue;
            }
            
            console.log(`✅ 베이스 시그널 업데이트: ${consolidation.newStock}`);
            
            // 2. 중복 시그널들 삭제
            let deletedCount = 0;
            for (const deleteId of consolidation.deleteSignals) {
                const { error: deleteError } = await supabase
                    .from('influencer_signals')
                    .delete()
                    .eq('id', deleteId);
                
                if (deleteError) {
                    console.error(`❌ 시그널 삭제 실패 (${deleteId}):`, deleteError.message);
                } else {
                    deletedCount++;
                    console.log(`🗑️ 중복 시그널 삭제: ${deleteId}`);
                }
            }
            
            results.push({
                group: consolidation.group,
                baseUpdated: !updateError,
                deletedCount: deletedCount,
                totalDeleted: consolidation.deleteSignals.length
            });
            
        } catch (error) {
            console.error(`오류 (${consolidation.group}):`, error.message);
        }
    }
    
    return results;
}

async function verifyChanges() {
    console.log('\n🔍 변경사항 검증\n');
    
    // 화자명 수정 검증
    console.log('화자명 수정 검증:');
    for (const correction of SPEAKER_CORRECTIONS) {
        const { data: signal } = await supabase
            .from('influencer_signals')
            .select(`
                stock,
                speakers(name)
            `)
            .eq('id', correction.id)
            .single();
        
        if (signal) {
            const currentSpeaker = signal.speakers?.name;
            const status = currentSpeaker === '김장열' ? '✅' : '❌';
            console.log(`  ${status} ${correction.stock}: ${currentSpeaker}`);
        }
    }
    
    // 바스켓 통합 검증
    console.log('\n바스켓 통합 검증:');
    const { data: baseSignal } = await supabase
        .from('influencer_signals')
        .select('stock, key_quote')
        .eq('id', BASKET_CONSOLIDATIONS[0].baseSignal)
        .single();
    
    if (baseSignal) {
        console.log(`  ✅ 통합 시그널: ${baseSignal.stock}`);
        console.log(`  내용: ${baseSignal.key_quote.substring(0, 60)}...`);
    }
    
    // 삭제된 시그널 확인
    for (const deleteId of BASKET_CONSOLIDATIONS[0].deleteSignals) {
        const { data: deletedSignal } = await supabase
            .from('influencer_signals')
            .select('id')
            .eq('id', deleteId)
            .single();
        
        const status = !deletedSignal ? '✅ 삭제됨' : '❌ 아직 존재';
        console.log(`  ${status}: ${deleteId}`);
    }
}

async function main() {
    console.log('🚀 V10.1 정확한 DB 수정 작업 시작');
    console.log('=' .repeat(60));
    
    const startTime = Date.now();
    
    try {
        // 1. 화자명 수정
        const speakerResults = await fixSpeakerNames();
        
        // 2. 바스켓 중복 통합
        const basketResults = await consolidateBaskets();
        
        // 3. 변경사항 검증
        await verifyChanges();
        
        // 4. 결과 요약
        const summary = {
            timestamp: new Date().toISOString(),
            speakerCorrections: speakerResults,
            basketConsolidations: basketResults,
            summary: {
                speakerFixed: speakerResults.filter(s => s.success).length,
                speakerFailed: speakerResults.filter(s => !s.success).length,
                basketsConsolidated: basketResults.length,
                signalsDeleted: basketResults.reduce((sum, b) => sum + b.deletedCount, 0)
            }
        };
        
        await fs.writeFile(
            'scripts/v10_precise_fixes_results.json',
            JSON.stringify(summary, null, 2)
        );
        
        const endTime = Date.now();
        const duration = Math.round((endTime - startTime) / 1000);
        
        console.log('\n📊 최종 결과 요약');
        console.log('=' .repeat(60));
        console.log(`화자명 수정: ${summary.summary.speakerFixed}/${speakerResults.length}건 성공`);
        console.log(`바스켓 통합: ${summary.summary.basketsConsolidated}그룹 처리`);
        console.log(`시그널 삭제: ${summary.summary.signalsDeleted}건`);
        console.log(`총 소요시간: ${duration}초`);
        console.log('\n✅ V10.1 DB 수정 작업 완료!');
        console.log('결과 파일: scripts/v10_precise_fixes_results.json');
        
    } catch (error) {
        console.error('\n💥 작업 중 오류 발생:', error);
        process.exit(1);
    }
}

main().catch(console.error);