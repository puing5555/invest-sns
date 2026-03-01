const handles = ['@hyoseok_academy','@syukasworld','@dalant_invest','@hyoseokacademy','@syukaworld','@dalantinvest'];

async function main() {
  for (const h of handles) {
    try {
      const res = await fetch(`https://www.youtube.com/${h}`);
      const html = await res.text();
      const m = html.match(/https:\/\/yt3\.googleusercontent\.com\/[^"'\s>]+/g);
      console.log(h, '->', m ? m[0] : 'NOT FOUND', `(status: ${res.status}, found: ${m ? m.length : 0})`);
    } catch(e) {
      console.log(h, '-> ERROR', e.message);
    }
  }
}
main();
