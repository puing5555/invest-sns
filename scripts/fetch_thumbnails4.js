const handles = ['@syuka','@dalant','@hyoseok','@이효석','@effglobal','@LeeHyoseokAcademy','@효석'];
async function main() {
  for (const h of handles) {
    try {
      const res = await fetch(`https://www.youtube.com/${h}`);
      const html = await res.text();
      const m = html.match(/https:\/\/yt3\.googleusercontent\.com\/[^"'\s>]+/g);
      if (m) console.log(h, '->', m[0]);
      else console.log(h, '-> NOT FOUND (status:', res.status+')');
    } catch(e) { console.log(h, '-> ERROR'); }
  }
}
main();
