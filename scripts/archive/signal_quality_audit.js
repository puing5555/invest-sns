const { createClient } = require('@supabase/supabase-js');
const Anthropic = require('@anthropic-ai/sdk');
const fs = require('fs').promises;
const path = require('path');

// ?섍꼍 ?ㅼ젙
const SUPABASE_URL = 'https://arypzhotxflimroprmdk.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIwMDYxMTAsImV4cCI6MjA4NzU4MjExMH0.qcqFIvYRiixwu609Wjj9H3HxscU8vNpo9nS_KQ3f00A';
const ANTHROPIC_API_KEY = process.env.ANTHROPIC_API_KEY;

const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
const anthropic = new Anthropic({ apiKey: ANTHROPIC_API_KEY });

// ?붾젅洹몃옩 濡쒓퉭 ?⑥닔
async function logToTelegram(message) {
    try {
        // OpenClaw 硫붿떆吏 ?꾧뎄 ?ъ슜???꾪빐 蹂꾨룄濡?援ы쁽?섏? ?딄퀬 肄섏넄 濡쒓퉭
        console.log(`[TELEGRAM LOG] ${message}`);
    } catch (error) {
        console.error('Telegram logging failed:', error);
    }
}

// ?쒕젅???⑥닔
const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));

// 1?④퀎: Haiku 寃利?
async function verifyWithHaiku(signals, batchSize = 10) {
    const results = [];
    const total = signals.length;
    
    console.log(`Starting Haiku verification for ${total} signals...`);
    await logToTelegram(`?뵇 Haiku 寃利??쒖옉: ${total}媛??쒓렇??);
    
    for (let i = 0; i < signals.length; i += batchSize) {
        const batch = signals.slice(i, i + batchSize);
        console.log(`Processing batch ${Math.floor(i/batchSize) + 1}/${Math.ceil(total/batchSize)} (${i + 1}-${Math.min(i + batchSize, total)})`);
        
        const batchPromises = batch.map(async (signal) => {
            try {
                const prompt = `?ㅼ쓬 ?쒓렇?먯쓽 ?덉쭏??寃利앺븯?몄슂.

?곸긽 ?쒕ぉ: ${signal.video_title || 'N/A'}
?쒓렇??醫낅ぉ: ${signal.stock} (${signal.ticker})
?쒓렇????? ${signal.signal}
?듭떖 諛쒖뼵: ${signal.key_quote}
洹쇨굅: ${signal.reasoning}
confidence: ${signal.confidence}

?먯젙: ?뺤긽/?섏떖/遺덈웾. JSON?쇰줈留?
{"verdict": "?뺤긽", "reason": "?쒖쨪"}`;

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
                    // JSON ?뚯떛 ?ㅽ뙣 ???띿뒪?몄뿉??異붿텧 ?쒕룄
                    if (content.includes('?섏떖')) {
                        verdict = { verdict: '?섏떖', reason: 'JSON ?뚯떛 ?ㅽ뙣, ?띿뒪??異붿텧' };
                    } else if (content.includes('遺덈웾')) {
                        verdict = { verdict: '遺덈웾', reason: 'JSON ?뚯떛 ?ㅽ뙣, ?띿뒪??異붿텧' };
                    } else {
                        verdict = { verdict: '?뺤긽', reason: 'JSON ?뚯떛 ?ㅽ뙣, 湲곕낯媛? };
                    }
                }
                
                return {
                    ...signal,
                    haiku_verdict: verdict.verdict,
                    haiku_reason: verdict.reason
                };
                
            } catch (error) {
                console.error(`Error processing signal ${signal.id}:`, error);
                
                // 429 ?먮윭 泥섎━
                if (error.status === 429) {
                    console.log('Rate limited, waiting 30 seconds...');
                    await delay(30000);
                    // ?ъ떆??
                    return await verifyWithHaiku([signal], 1);
                }
                
                return {
                    ...signal,
                    haiku_verdict: '?섏떖',
                    haiku_reason: `API ?ㅻ쪟: ${error.message}`
                };
            }
        });
        
        const batchResults = await Promise.all(batchPromises);
        results.push(...batchResults);
        
        // 諛곗튂 ?꾨즺 ???쒕젅??
        await delay(500);
        
        // 100嫄대쭏???붾젅洹몃옩 濡쒓퉭
        if ((i + batchSize) % 100 === 0 || i + batchSize >= total) {
            const processed = Math.min(i + batchSize, total);
            const suspicious = results.filter(r => r.haiku_verdict === '?섏떖').length;
            const defective = results.filter(r => r.haiku_verdict === '遺덈웾').length;
            
            await logToTelegram(`?뱤 吏꾪뻾?곹솴 ${processed}/${total} | ?섏떖: ${suspicious} | 遺덈웾: ${defective}`);
        }
    }
    
    return results;
}

// 2?④퀎: Sonnet ?ш?利?
async function reverifyWithSonnet(suspiciousSignals) {
    const results = [];
    const total = suspiciousSignals.length;
    
    if (total === 0) {
        console.log('No suspicious signals to reverify');
        return [];
    }
    
    console.log(`Starting Sonnet reverification for ${total} suspicious signals...`);
    await logToTelegram(`?뵮 Sonnet ?ш?利??쒖옉: ${total}媛??섏떖/遺덈웾 ?쒓렇??);
    
    for (let i = 0; i < suspiciousSignals.length; i++) {
        const signal = suspiciousSignals[i];
        console.log(`Reverifying signal ${i + 1}/${total}: ${signal.id}`);
        
        try {
            const prompt = `?ㅼ쓬 ?쒓렇?먯쓽 ?덉쭏???꾧꺽?섍쾶 ?ш?利앺븯?몄슂.

?곸긽 ?쒕ぉ: ${signal.video_title || 'N/A'}
?쒓렇??醫낅ぉ: ${signal.stock} (${signal.ticker})
?쒓렇????? ${signal.signal}
?듭떖 諛쒖뼵: ${signal.key_quote}
洹쇨굅: ${signal.reasoning}
confidence: ${signal.confidence}

1李??먯젙: ${signal.haiku_verdict} (${signal.haiku_reason})

理쒖쥌 ?먯젙???대젮二쇱꽭?? ?뺤긽/遺덈웾留?援щ텇?섎ŉ, JSON?쇰줈留?
{"verdict": "?뺤긽", "reason": "?곸꽭??洹쇨굅"}`;

            const response = await anthropic.messages.create({
                model: 'claude-sonnet-4-6',
                max_tokens: 200,
                messages: [{ role: 'user', content: prompt }]
            });
            
            const content = response.content[0].text.trim();
            let verdict;
            
            try {
                verdict = JSON.parse(content);
            } catch (parseError) {
                // JSON ?뚯떛 ?ㅽ뙣 ???띿뒪?몄뿉??異붿텧
                if (content.includes('遺덈웾')) {
                    verdict = { verdict: '遺덈웾', reason: 'JSON ?뚯떛 ?ㅽ뙣, ?띿뒪??異붿텧' };
                } else {
                    verdict = { verdict: '?뺤긽', reason: 'JSON ?뚯떛 ?ㅽ뙣, 湲곕낯媛? };
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
            
            // 429 ?먮윭 泥섎━
            if (error.status === 429) {
                console.log('Rate limited, waiting 30 seconds...');
                await delay(30000);
                i--; // ?꾩옱 ?몃뜳???ㅼ떆 ?쒕룄
                continue;
            }
            
            results.push({
                ...signal,
                sonnet_verdict: '遺덈웾',
                sonnet_reason: `API ?ㅻ쪟: ${error.message}`,
                final_verdict: '遺덈웾'
            });
        }
        
        // 媛??붿껌留덈떎 ?쒕젅??
        await delay(1000);
    }
    
    return results;
}

// 硫붿씤 ?⑥닔
async function main() {
    try {
        console.log('?? Starting Signal Quality Audit...');
        
        // 1. ?곗씠??媛?몄삤湲?
        console.log('?뱤 Fetching signals from database...');
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
        
        // 鍮꾨뵒???쒕ぉ ?뚮옒??
        const flattenedSignals = signals.map(signal => ({
            ...signal,
            video_title: signal.influencer_videos?.title || 'N/A'
        }));
        
        console.log(`Found ${flattenedSignals.length} signals`);
        await logToTelegram(`?뱤 珥?${flattenedSignals.length}媛??쒓렇??諛쒓껄, 寃利??쒖옉`);
        
        // 2. 1?④퀎: Haiku 寃利?
        const haikuResults = await verifyWithHaiku(flattenedSignals);
        
        // ?섏떖/遺덈웾 ?쒓렇??異붿텧
        const suspiciousSignals = haikuResults.filter(s => 
            s.haiku_verdict === '?섏떖' || s.haiku_verdict === '遺덈웾'
        );
        
        console.log(`Haiku found ${suspiciousSignals.length} suspicious signals`);
        
        // 3. 2?④퀎: Sonnet ?ш?利?
        const sonnetResults = await reverifyWithSonnet(suspiciousSignals);
        
        // 4. 理쒖쥌 寃곌낵 ?⑹튂湲?
        const finalResults = haikuResults.map(haikuResult => {
            const sonnetResult = sonnetResults.find(s => s.id === haikuResult.id);
            return sonnetResult || {
                ...haikuResult,
                final_verdict: haikuResult.haiku_verdict === '?뺤긽' ? '?뺤긽' : haikuResult.haiku_verdict
            };
        });
        
        // 5. 寃곌낵 ?듦퀎
        const stats = {
            total: finalResults.length,
            normal: finalResults.filter(s => s.final_verdict === '?뺤긽').length,
            defective: finalResults.filter(s => s.final_verdict === '遺덈웾').length,
            haiku_suspicious: haikuResults.filter(s => s.haiku_verdict === '?섏떖').length,
            haiku_defective: haikuResults.filter(s => s.haiku_verdict === '遺덈웾').length,
            sonnet_reverified: sonnetResults.length
        };
        
        console.log('?뱤 Final Statistics:', stats);
        
        // 6. data ?대뜑 ?앹꽦
        await fs.mkdir('data', { recursive: true });
        
        // 7. JSON 寃곌낵 ???
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
        
        // 8. 遺덈웾 ?쒓렇??留덊겕?ㅼ슫 由ы룷???앹꽦
        const defectiveSignals = finalResults.filter(s => s.final_verdict === '遺덈웾');
        
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
            markdownReport += `## No Defective Signals Found! ?럦\n\n`;
        }
        
        await fs.writeFile('data/signal_defects.md', markdownReport, 'utf8');
        
        // 9. 理쒖쥌 濡쒓렇
        await logToTelegram(`??寃利??꾨즺! 珥?${stats.total}媛?以?遺덈웾 ${stats.defective}媛?(${(stats.defective/stats.total*100).toFixed(1)}%)`);
        
        console.log('??Signal Quality Audit completed successfully!');
        console.log(`?뱚 Results saved to:`);
        console.log(`   - data/signal_quality_full_audit.json`);
        console.log(`   - data/signal_defects.md`);
        
        return stats;
        
    } catch (error) {
        console.error('??Audit failed:', error);
        await logToTelegram(`??寃利??ㅽ뙣: ${error.message}`);
        throw error;
    }
}

// ?ㅽ뻾
if (require.main === module) {
    main()
        .then(stats => {
            console.log('?럦 Audit completed with statistics:', stats);
            process.exit(0);
        })
        .catch(error => {
            console.error('?뮙 Fatal error:', error);
            process.exit(1);
        });
}

module.exports = { main };
