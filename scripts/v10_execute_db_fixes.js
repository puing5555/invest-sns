// V10.1 DB 수정 작업 통합 실행 스크립트
import { spawn } from 'child_process';
import fs from 'fs/promises';
import path from 'path';

function runScript(scriptPath) {
    return new Promise((resolve, reject) => {
        console.log(`\n🔄 실행 중: ${scriptPath}`);
        
        const child = spawn('node', [scriptPath], {
            stdio: 'inherit',
            cwd: process.cwd()
        });

        child.on('close', (code) => {
            if (code === 0) {
                console.log(`✅ 완료: ${scriptPath}`);
                resolve(code);
            } else {
                console.error(`❌ 실패: ${scriptPath} (exit code: ${code})`);
                reject(new Error(`Script failed with exit code ${code}`));
            }
        });

        child.on('error', (error) => {
            console.error(`❌ 오류: ${scriptPath}`, error);
            reject(error);
        });
    });
}

async function generateSummaryReport() {
    try {
        const reports = [];
        
        // 화자 수정 결과 읽기
        try {
            const speakerResults = await fs.readFile('scripts/v10_speaker_fix_results.json', 'utf8');
            const speakerData = JSON.parse(speakerResults);
            reports.push({
                type: '화자 식별 수정',
                ...speakerData
            });
        } catch (e) {
            console.log('화자 수정 결과 파일을 찾을 수 없음');
        }

        // 바스켓 통합 결과 읽기
        try {
            const basketResults = await fs.readFile('scripts/v10_basket_fix_results.json', 'utf8');
            const basketData = JSON.parse(basketResults);
            reports.push({
                type: '바스켓 중복 통합',
                ...basketData
            });
        } catch (e) {
            console.log('바스켓 통합 결과 파일을 찾을 수 없음');
        }

        // 통합 보고서 생성
        const summary = {
            timestamp: new Date().toISOString(),
            totalTasks: reports.length,
            reports: reports,
            overall: {
                totalProcessed: reports.reduce((sum, r) => sum + (r.total || r.groupsFound || 0), 0),
                totalSuccess: reports.reduce((sum, r) => sum + (r.success || r.signalsUpdated || 0), 0),
                totalChanges: reports.reduce((sum, r) => sum + (r.success || r.signalsUpdated + r.signalsDeleted || 0), 0)
            }
        };

        await fs.writeFile(
            'scripts/v10_db_fixes_summary.json',
            JSON.stringify(summary, null, 2)
        );

        console.log('\n📋 V10.1 DB 수정 작업 완료 요약');
        console.log('=' .repeat(50));
        console.log(`실행 시간: ${summary.timestamp}`);
        console.log(`완료된 작업: ${summary.totalTasks}개`);
        console.log(`전체 처리: ${summary.overall.totalProcessed}건`);
        console.log(`성공적 변경: ${summary.overall.totalChanges}건`);
        
        reports.forEach(report => {
            console.log(`\n📌 ${report.type}`);
            if (report.success !== undefined) {
                console.log(`  - 처리: ${report.total}건`);
                console.log(`  - 성공: ${report.success}건`);
                console.log(`  - 실패: ${report.failed}건`);
            } else if (report.signalsUpdated !== undefined) {
                console.log(`  - 그룹: ${report.groupsFound}개`);
                console.log(`  - 업데이트: ${report.signalsUpdated}건`);
                console.log(`  - 삭제: ${report.signalsDeleted}건`);
            }
        });

        console.log('\n📁 상세 결과는 다음 파일들을 확인하세요:');
        console.log('  - scripts/v10_speaker_fix_results.json');
        console.log('  - scripts/v10_basket_fix_results.json');
        console.log('  - scripts/v10_db_fixes_summary.json');

    } catch (error) {
        console.error('요약 보고서 생성 오류:', error);
    }
}

async function main() {
    console.log('🚀 V10.1 DB 수정 작업 시작');
    console.log('=' .repeat(50));
    console.log('작업 1: 화자 식별 문제 19건 수정');
    console.log('작업 2: 바스켓 중복 8건 통합');
    console.log('=' .repeat(50));

    const startTime = Date.now();

    try {
        // 작업 1: 화자 식별 수정
        await runScript('scripts/v10_fix_speaker_identification.js');
        
        // 짧은 대기
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // 작업 2: 바스켓 중복 통합
        await runScript('scripts/v10_fix_basket_duplicates.js');

        // 요약 보고서 생성
        await generateSummaryReport();

        const endTime = Date.now();
        const duration = Math.round((endTime - startTime) / 1000);

        console.log('\n🎉 모든 V10.1 DB 수정 작업이 완료되었습니다!');
        console.log(`총 소요 시간: ${duration}초`);

    } catch (error) {
        console.error('\n💥 작업 중 오류 발생:', error);
        process.exit(1);
    }
}

main().catch(console.error);