/**
 * 인플루언서 페이지 V9 시그널 타입 한글화 수정
 */
const fs = require('fs');

const content = fs.readFileSync('./app/explore/influencer/page.tsx', 'utf-8');

// V9 한글 시그널 표시를 위한 수정
const updatedContent = content
  // 시그널 타입 변환 로직 제거 (이미 한글이므로)
  .replace(
    /\{signal\.signal_type === 'BUY' \? '매수' : signal\.signal_type === 'SELL' \? '매도' : '중립'\}/g, 
    '{signal.signal_type}'
  )
  // 종목별 탭에서도 같은 수정
  .replace(
    /\{group\.latest_signal === 'BUY' \? '매수' : group\.latest_signal === 'SELL' \? '매도' : '중립'\}/g,
    '{group.latest_signal}'
  )
  // 개별 시그널에서도 수정  
  .replace(
    /\{signal\.signal_type === 'BUY' \? '매수' : signal\.signal_type === 'SELL' \? '매도' : '중립'\}/g,
    '{signal.signal_type}'
  );

fs.writeFileSync('./app/explore/influencer/page.tsx', updatedContent);

console.log('✅ 인플루언서 페이지 V9 한글 시그널 타입 수정 완료');