// V10.1 바스켓 중복 8건 통합 스크립트
import { createClient } from '@supabase/supabase-js';
import fs from 'fs/promises';

const supabaseUrl = 'https://arypzhotxflimroprmdk.supabase.co';
const supabaseServiceKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8';

const supabase = createClient(supabaseUrl, supabaseServiceKey);

// 중복으로 확인된 8개 시그널 ID
const DUPLICATE_ISSUES = [
    'cd3a96b4-8c52-4dce-884f-5e89a8e228d5', // TSMC, 배재규
    '764703cc-157e-46fe-b265-f2253a1d66ba', // 삼성전자, 이효석  
    '1cda9f77-c6cf-43b6-83be-6542e9930f58', // SK하이닉스, 이효석
    'c250cb34-04cb-4174-9843-8c069f731271', // SK하이닉스, 조진표
    'ea49a319-181d-4fec-ac91-063be14c73ab', // 엔비디아, 배재규
    '7ba0f471-6950-4436-8e8f-2ee5989748ce', // 삼성전자, 조진표
    'ffa1dc33-167c-4ea8-9691-5f8aa1bf1f4c', // 삼성전자, 이영수
    'ff0d3e8d-9eaf-4d8a-8bde-0b64224c9a86'  // SK하이닉스, 배재규
];

// 중복 시그널 그룹 찾기
async function findDuplicateGroups() {
    const groups = {};

    for (const signalId of DUPLICATE_ISSUES) {
        try {
            // 시그널 정보 조회
            const { data: signal, error } = await supabase
                .from('influencer_signals')
                .select(`
                    *,
                    speakers(name),
                    influencer_videos(id, title, created_at)
                `)
                .eq('id', signalId)
                .single();

            if (error) {
                console.error(`시그널 조회 오류 (${signalId}):`, error);
                continue;
            }

            const key = `${signal.video_id}_${signal.speaker_id}`;
            
            if (!groups[key]) {
                groups[key] = {
                    videoId: signal.video_id,
                    speakerId: signal.speaker_id,
                    speakerName: signal.speakers.name,
                    videoTitle: signal.influencer_videos.title,
                    videoDate: signal.influencer_videos.created_at,
                    signals: []
                };
            }

            groups[key].signals.push({
                id: signal.id,
                stock: signal.stock,
                signal_type: signal.signal_type,
                key_quote: signal.key_quote,
                timestamp: signal.timestamp,
                created_at: signal.created_at
            });

        } catch (error) {
            console.error(`처리 중 오류 (${signalId}):`, error);
        }
    }

    return groups;
}

// 두 시그널이 중복인지 판단
function isDuplicate(signal1, signal2) {
    // 1. 같은 종목인지 확인
    if (signal1.stock !== signal2.stock) return false;
    
    // 2. 타임스탬프가 비슷한지 확인 (±30초)
    const timeDiff = Math.abs(signal1.timestamp - signal2.timestamp);
    if (timeDiff > 30) return false;
    
    // 3. key_quote의 유사도 확인 (간단한 단어 겹침 체크)
    const words1 = signal1.key_quote.split(/\s+/).filter(w => w.length > 1);
    const words2 = signal2.key_quote.split(/\s+/).filter(w => w.length > 1);
    
    const commonWords = words1.filter(word => words2.includes(word));
    const similarity = commonWords.length / Math.max(words1.length, words2.length);
    
    return similarity > 0.4; // 40% 이상 겹치면 중복으로 판단
}

// 바스켓 시그널 통합
async function consolidateBasketSignals(group) {
    const signals = group.signals;
    const consolidated = [];
    const toDelete = [];

    console.log(`\n📦 그룹 분석: ${group.speakerName} in ${group.videoTitle.substring(0, 50)}...`);
    console.log(`시그널 ${signals.length}개 발견`);

    // 중복 제거 로직
    for (let i = 0; i < signals.length; i++) {
        let isDuplicateOfExisting = false;
        
        for (let j = 0; j < consolidated.length; j++) {
            if (isDuplicate(signals[i], consolidated[j])) {
                console.log(`  중복 발견: ${signals[i].stock} (${signals[i].key_quote.substring(0, 30)}...)`);
                toDelete.push(signals[i].id);
                isDuplicateOfExisting = true;
                break;
            }
        }
        
        if (!isDuplicateOfExisting) {
            consolidated.push(signals[i]);
        }
    }

    // 바스켓 패턴 확인 (3개 이상 종목이 비슷한 시간대에 있으면)
    if (consolidated.length >= 3) {
        const timeSpread = Math.max(...consolidated.map(s => s.timestamp)) - 
                          Math.min(...consolidated.map(s => s.timestamp));
        
        if (timeSpread <= 60) { // 1분 이내
            console.log(`  🔄 바스켓 패턴 발견: ${consolidated.length}개 종목을 섹터로 통합 검토`);
            
            // 반도체 섹터 확인
            const semiconductorStocks = ['삼성전자', 'SK하이닉스', 'TSMC', 'ASML', '엔비디아', '마이크론'];
            const foundSemis = consolidated.filter(s => semiconductorStocks.includes(s.stock));
            
            if (foundSemis.length >= 3) {
                console.log(`  ✅ 반도체 섹터로 통합: ${foundSemis.map(s => s.stock).join(', ')}`);
                
                // 가장 포괄적인 key_quote를 가진 시그널을 베이스로 사용
                const baseSignal = foundSemis.sort((a, b) => b.key_quote.length - a.key_quote.length)[0];
                
                // 나머지는 삭제 대상에 추가
                foundSemis.filter(s => s.id !== baseSignal.id).forEach(s => {
                    if (!toDelete.includes(s.id)) {
                        toDelete.push(s.id);
                    }
                });
                
                // 베이스 시그널을 섹터로 업데이트
                const sectorQuote = `반도체 섹터 포트폴리오 추천: ${foundSemis.map(s => s.stock).join(', ')} 등 주요 반도체 종목들의 집중 투자 전략`;
                
                return {
                    updateSignal: {
                        id: baseSignal.id,
                        stock: '반도체 섹터',
                        key_quote: sectorQuote
                    },
                    deleteSignals: toDelete
                };
            }
        }
    }

    return {
        updateSignal: null,
        deleteSignals: toDelete
    };
}

// 시그널 업데이트
async function updateSignal(signalId, updates) {
    const { error } = await supabase
        .from('influencer_signals')
        .update(updates)
        .eq('id', signalId);
    
    if (error) {
        console.error(`업데이트 오류 (${signalId}):`, error);
        return false;
    }
    
    return true;
}

// 시그널 삭제 (soft delete)
async function softDeleteSignal(signalId) {
    const { error } = await supabase
        .from('influencer_signals')
        .update({ 
            deleted_at: new Date().toISOString(),
            deleted_reason: 'V10.1_duplicate_consolidation'
        })
        .eq('id', signalId);
    
    if (error) {
        console.error(`삭제 오류 (${signalId}):`, error);
        return false;
    }
    
    return true;
}

async function main() {
    console.log('🚀 V10.1 바스켓 중복 통합 시작');
    
    const results = {
        total: DUPLICATE_ISSUES.length,
        groupsFound: 0,
        signalsUpdated: 0,
        signalsDeleted: 0,
        details: []
    };

    // 1. 중복 그룹 찾기
    console.log('\n1️⃣ 중복 시그널 그룹 분석 중...');
    const groups = await findDuplicateGroups();
    results.groupsFound = Object.keys(groups).length;
    
    console.log(`발견된 그룹: ${results.groupsFound}개`);

    // 2. 각 그룹별 통합 처리
    for (const [groupKey, group] of Object.entries(groups)) {
        if (group.signals.length < 2) {
            console.log(`⏭️ 그룹 스킵: ${group.speakerName} (시그널 1개만 있음)`);
            continue;
        }

        const consolidation = await consolidateBasketSignals(group);
        
        // 업데이트할 시그널이 있으면
        if (consolidation.updateSignal) {
            const updateSuccess = await updateSignal(
                consolidation.updateSignal.id,
                {
                    stock: consolidation.updateSignal.stock,
                    key_quote: consolidation.updateSignal.key_quote
                }
            );
            
            if (updateSuccess) {
                results.signalsUpdated++;
                console.log(`✅ 시그널 업데이트 완료: ${consolidation.updateSignal.stock}`);
            }
        }
        
        // 삭제할 시그널들
        for (const deleteId of consolidation.deleteSignals) {
            const deleteSuccess = await softDeleteSignal(deleteId);
            if (deleteSuccess) {
                results.signalsDeleted++;
                console.log(`🗑️ 중복 시그널 삭제: ${deleteId}`);
            }
        }

        results.details.push({
            groupKey,
            speakerName: group.speakerName,
            videoTitle: group.videoTitle.substring(0, 50) + '...',
            originalCount: group.signals.length,
            updated: consolidation.updateSignal ? 1 : 0,
            deleted: consolidation.deleteSignals.length
        });

        // 짧은 대기
        await new Promise(resolve => setTimeout(resolve, 200));
    }

    console.log('\n📊 통합 결과 요약');
    console.log(`처리된 그룹: ${results.groupsFound}개`);
    console.log(`업데이트된 시그널: ${results.signalsUpdated}개`);
    console.log(`삭제된 시그널: ${results.signalsDeleted}개`);

    // 결과를 파일로 저장
    await fs.writeFile(
        'scripts/v10_basket_fix_results.json',
        JSON.stringify(results, null, 2)
    );

    console.log('\n결과가 scripts/v10_basket_fix_results.json에 저장되었습니다.');
}

main().catch(console.error);