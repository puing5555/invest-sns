const { createClient } = require('@supabase/supabase-js');
const Anthropic = require('@anthropic-ai/sdk');
const fs = require('fs').promises;
const path = require('path');

// 환경 설정
const SUPABASE_URL = 'https://arypzhotxflimroprmdk.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIwMDYxMTAsImV4cCI6MjA4NzU4MjExMH0.qcqFIvYRiixwu609Wjj9H3HxscU8vNpo9nS_KQ3f00A';
const ANTHROPIC_API_KEY = process.env.ANTHROPIC_API_KEY;

const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
const anthropic = new Anthropic({ apiKey: ANTHROPIC_API_KEY });

// 텔레그램 로깅 함수
async function logToTelegram(message) {
    try {
        // OpenClaw 메시지 도구 사용을 위해 별도로 구현하지 않고 콘솔 로깅
        console.log(`[TELEGRAM LOG] ${message}`);
    } catch (error) {
        console.error('Telegram logging failed:', error);
    }
}

// 딜레이 함수
const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));

// 1단계: Haiku 검증
async function verifyWithHaiku(signals, batchSize = 10) {
    const results = [];
    const total = signals.length;
    
    console.log(`Starting Haiku verification for ${total} signals...`);
    await logToTelegram(`🔍 Haiku 검증 시작: ${total}개 시그널`);
    
    for (let i = 0; i < signals.length; i += batchSize) {
        const batch = signals.slice(i, i + batchSize);
        console.log(`Processing batch ${Math.floor(i/batchSize) + 1}/${Math.ceil(total/batchSize)} (${i + 1}-${Math.min(i + batchSize, total)})`);
        
        const batchPromises = batch.map(async (signal) => {
            try {
                const prompt = `다음 시그널의 품질을 검증하세요.

영상 제목: ${signal.video_title || 'N/A'}
시그널 종목: ${signal.stock} (${signal.ticker})
시그널 타입: ${signal.signal}
핵심 발언: ${signal.key_quote}
근거: ${signal.reasoning}
confidence: ${signal.confidence}

판정: 정상/의심/불량. JSON으로만:
{"verdict": "정상", "reason": "한줄"}`;

                const response = await anthropic.messages.create({
                    model: 'claude-3-haiku-20240307',
                    max_tokens: 100,
                    messages: [{ role: 'user', content: prompt }]
                });
                
                const content = response.content[0].text.trim();
                let verdict;
                
                try {
                    verdict = JSON.parse(content);
                } catch (parseError) {
                    // JSON 파싱 실패 시 텍스트에서 추출 시도
                    if (content.includes('의심')) {
                        verdict = { verdict: '의심', reason: 'JSON 파싱 실패, 텍스트 추출' };
                    } else if (content.includes('불량')) {
                        verdict = { verdict: '불량', reason: 'JSON 파싱 실패, 텍스트 추출' };
                    } else {
                        verdict = { verdict: '정상', reason: 'JSON 파싱 실패, 기본값' };
                    }
                }
                
                return {
                    ...signal,
                    haiku_verdict: verdict.verdict,
                    haiku_reason: verdict.reason
                };
                
            } catch (error) {
                console.error(`Error processing signal ${signal.id}:`, error);
                
                // 429 에러 처리
                if (error.status === 429) {
                    console.log('Rate limited, waiting 30 seconds...');
                    await delay(30000);
                    // 재시도
                    return await verifyWithHaiku([signal], 1);
                }
                
                return {
                    ...signal,
                    haiku_verdict: '의심',
                    haiku_reason: `API 오류: ${error.message}`
                };
            }
        });
        
        const batchResults = await Promise.all(batchPromises);
        results.push(...batchResults);
        
        // 배치 완료 후 딜레이
        await delay(500);
        
        // 100건마다 텔레그램 로깅
        if ((i + batchSize) % 100 === 0 || i + batchSize >= total) {
            const processed = Math.min(i + batchSize, total);
            const suspicious = results.filter(r => r.haiku_verdict === '의심').length;
            const defective = results.filter(r => r.haiku_verdict === '불량').length;
            
            await logToTelegram(`📊 진행상황 ${processed}/${total} | 의심: ${suspicious} | 불량: ${defective}`);
        }
    }
    
    return results;
}

// 2단계: Sonnet 재검증
async function reverifyWithSonnet(suspiciousSignals) {
    const results = [];
    const total = suspiciousSignals.length;
    
    if (total === 0) {
        console.log('No suspicious signals to reverify');
        return [];
    }
    
    console.log(`Starting Sonnet reverification for ${total} suspicious signals...`);
    await logToTelegram(`🔬 Sonnet 재검증 시작: ${total}개 의심/불량 시그널`);
    
    for (let i = 0; i < suspiciousSignals.length; i++) {
        const signal = suspiciousSignals[i];
        console.log(`Reverifying signal ${i + 1}/${total}: ${signal.id}`);
        
        try {
            const prompt = `다음 시그널의 품질을 엄격하게 재검증하세요.

영상 제목: ${signal.video_title || 'N/A'}
시그널 종목: ${signal.stock} (${signal.ticker})
시그널 타입: ${signal.signal}
핵심 발언: ${signal.key_quote}
근거: ${signal.reasoning}
confidence: ${signal.confidence}

1차 판정: ${signal.haiku_verdict} (${signal.haiku_reason})

최종 판정을 내려주세요. 정상/불량만 구분하며, JSON으로만:
{"verdict": "정상", "reason": "상세한 근거"}`;

            const response = await anthropic.messages.create({
                model: 'claude-sonnet-4-20250514',
                max_tokens: 200,
                messages: [{ role: 'user', content: prompt }]
            });
            
            const content = response.content[0].text.trim();
            let verdict;
            
            try {
                verdict = JSON.parse(content);
            } catch (parseError) {
                // JSON 파싱 실패 시 텍스트에서 추출
                if (content.includes('불량')) {
                    verdict = { verdict: '불량', reason: 'JSON 파싱 실패, 텍스트 추출' };
                } else {
                    verdict = { verdict: '정상', reason: 'JSON 파싱 실패, 기본값' };
                }
            }
            
            results.push({
                ...signal,
                sonnet_verdict: verdict.verdict,
                sonnet_reason: verdict.reason,
                final_verdict: verdict.verdict
            });
            
        } catch (error) {
            console.error(`Error reverifying signal ${signal.id}:`, error);
            
            // 429 에러 처리
            if (error.status === 429) {
                console.log('Rate limited, waiting 30 seconds...');
                await delay(30000);
                i--; // 현재 인덱스 다시 시도
                continue;
            }
            
            results.push({
                ...signal,
                sonnet_verdict: '불량',
                sonnet_reason: `API 오류: ${error.message}`,
                final_verdict: '불량'
            });
        }
        
        // 각 요청마다 딜레이
        await delay(1000);
    }
    
    return results;
}

// 메인 함수
async function main() {
    try {
        console.log('🚀 Starting Signal Quality Audit...');
        
        // 1. 데이터 가져오기
        console.log('📊 Fetching signals from database...');
        const { data: signals, error } = await supabase
            .from('influencer_signals')
            .select(`
                id, video_id, stock, ticker, signal, key_quote, reasoning, confidence,
                influencer_videos (title)
            `)
            .order('id', { ascending: true });
        
        if (error) {
            throw new Error(`Database error: ${error.message}`);
        }
        
        if (!signals || signals.length === 0) {
            throw new Error('No signals found in database');
        }
        
        // 비디오 제목 플래튼
        const flattenedSignals = signals.map(signal => ({
            ...signal,
            video_title: signal.influencer_videos?.title || 'N/A'
        }));
        
        console.log(`Found ${flattenedSignals.length} signals`);
        await logToTelegram(`📊 총 ${flattenedSignals.length}개 시그널 발견, 검증 시작`);
        
        // 2. 1단계: Haiku 검증
        const haikuResults = await verifyWithHaiku(flattenedSignals);
        
        // 의심/불량 시그널 추출
        const suspiciousSignals = haikuResults.filter(s => 
            s.haiku_verdict === '의심' || s.haiku_verdict === '불량'
        );
        
        console.log(`Haiku found ${suspiciousSignals.length} suspicious signals`);
        
        // 3. 2단계: Sonnet 재검증
        const sonnetResults = await reverifyWithSonnet(suspiciousSignals);
        
        // 4. 최종 결과 합치기
        const finalResults = haikuResults.map(haikuResult => {
            const sonnetResult = sonnetResults.find(s => s.id === haikuResult.id);
            return sonnetResult || {
                ...haikuResult,
                final_verdict: haikuResult.haiku_verdict === '정상' ? '정상' : haikuResult.haiku_verdict
            };
        });
        
        // 5. 결과 통계
        const stats = {
            total: finalResults.length,
            normal: finalResults.filter(s => s.final_verdict === '정상').length,
            defective: finalResults.filter(s => s.final_verdict === '불량').length,
            haiku_suspicious: haikuResults.filter(s => s.haiku_verdict === '의심').length,
            haiku_defective: haikuResults.filter(s => s.haiku_verdict === '불량').length,
            sonnet_reverified: sonnetResults.length
        };
        
        console.log('📊 Final Statistics:', stats);
        
        // 6. data 폴더 생성
        await fs.mkdir('data', { recursive: true });
        
        // 7. JSON 결과 저장
        const auditResult = {
            timestamp: new Date().toISOString(),
            statistics: stats,
            signals: finalResults
        };
        
        await fs.writeFile(
            'data/signal_quality_full_audit.json',
            JSON.stringify(auditResult, null, 2),
            'utf8'
        );
        
        // 8. 불량 시그널 마크다운 리포트 생성
        const defectiveSignals = finalResults.filter(s => s.final_verdict === '불량');
        
        let markdownReport = `# Signal Quality Audit - Defects Report\n\n`;
        markdownReport += `Generated: ${new Date().toLocaleString()}\n\n`;
        markdownReport += `## Summary\n\n`;
        markdownReport += `- Total Signals: ${stats.total}\n`;
        markdownReport += `- Normal: ${stats.normal}\n`;
        markdownReport += `- Defective: ${stats.defective}\n`;
        markdownReport += `- Defect Rate: ${(stats.defective/stats.total*100).toFixed(2)}%\n\n`;
        
        if (defectiveSignals.length > 0) {
            markdownReport += `## Defective Signals (${defectiveSignals.length})\n\n`;
            
            defectiveSignals.forEach((signal, index) => {
                markdownReport += `### ${index + 1}. Signal ID: ${signal.id}\n\n`;
                markdownReport += `- **Video**: ${signal.video_title}\n`;
                markdownReport += `- **Stock**: ${signal.stock} (${signal.ticker})\n`;
                markdownReport += `- **Signal**: ${signal.signal}\n`;
                markdownReport += `- **Quote**: ${signal.key_quote}\n`;
                markdownReport += `- **Reasoning**: ${signal.reasoning}\n`;
                markdownReport += `- **Confidence**: ${signal.confidence}\n`;
                markdownReport += `- **Haiku Verdict**: ${signal.haiku_verdict} - ${signal.haiku_reason}\n`;
                if (signal.sonnet_verdict) {
                    markdownReport += `- **Sonnet Verdict**: ${signal.sonnet_verdict} - ${signal.sonnet_reason}\n`;
                }
                markdownReport += `\n---\n\n`;
            });
        } else {
            markdownReport += `## No Defective Signals Found! 🎉\n\n`;
        }
        
        await fs.writeFile('data/signal_defects.md', markdownReport, 'utf8');
        
        // 9. 최종 로그
        await logToTelegram(`✅ 검증 완료! 총 ${stats.total}개 중 불량 ${stats.defective}개 (${(stats.defective/stats.total*100).toFixed(1)}%)`);
        
        console.log('✅ Signal Quality Audit completed successfully!');
        console.log(`📁 Results saved to:`);
        console.log(`   - data/signal_quality_full_audit.json`);
        console.log(`   - data/signal_defects.md`);
        
        return stats;
        
    } catch (error) {
        console.error('❌ Audit failed:', error);
        await logToTelegram(`❌ 검증 실패: ${error.message}`);
        throw error;
    }
}

// 실행
if (require.main === module) {
    main()
        .then(stats => {
            console.log('🎉 Audit completed with statistics:', stats);
            process.exit(0);
        })
        .catch(error => {
            console.error('💥 Fatal error:', error);
            process.exit(1);
        });
}

module.exports = { main };