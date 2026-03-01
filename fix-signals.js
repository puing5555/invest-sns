const fs = require('fs');
let c = fs.readFileSync('v91-insert.js', 'utf8');
c = c.replaceAll("signal: 'BUY'", "signal: '매수'");
c = c.replaceAll("signal: 'POSITIVE'", "signal: '긍정'");
c = c.replaceAll("signal: 'NEUTRAL'", "signal: '중립'");
fs.writeFileSync('v91-insert.js', c);
console.log('done');
