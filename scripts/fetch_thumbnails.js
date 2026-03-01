const handles = ['@3protv','@corinpapa1106','@buiknam_tv','@hyoseok_academy','@syukasworld','@dalant_invest'];

async function main() {
  const results = {};
  for (const h of handles) {
    try {
      const res = await fetch(`https://www.youtube.com/${h}`);
      const html = await res.text();
      const m = html.match(/https:\/\/yt3\.googleusercontent\.com\/[^"'\s]+/);
      results[h] = m ? m[0] : null;
    } catch(e) {
      results[h] = null;
    }
  }
  console.log(JSON.stringify(results, null, 2));
}
main();
