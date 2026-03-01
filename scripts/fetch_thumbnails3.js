const handles = ['@이효석아카데미','@LeeHyoseok','@슈카월드','@syuka','@달란트투자','@dalant'];
async function main() {
  for (const h of handles) {
    try {
      const res = await fetch(`https://www.youtube.com/${h}`);
      const html = await res.text();
      const m = html.match(/https:\/\/yt3\.googleusercontent\.com\/[^"'\s>]+/g);
      console.log(h, '->', m ? m[0].substring(0,80) : 'NOT FOUND', `(status: ${res.status})`);
    } catch(e) { console.log(h, '-> ERROR'); }
  }
}
main();
