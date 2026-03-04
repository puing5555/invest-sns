import os, requests
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env.local'))
url = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
key = os.getenv('NEXT_PUBLIC_SUPABASE_ANON_KEY')
headers = {'apikey': key, 'Authorization': 'Bearer ' + key}
resp = requests.get(url + '/rest/v1/influencer_signals?select=id,stock,signal,key_quote,reasoning&limit=1000', headers=headers)
data = resp.json()
print("Total:", len(data))

short = [d for d in data if d.get('reasoning') and len(d['reasoning']) < 50]
medium = [d for d in data if d.get('reasoning') and 50 <= len(d['reasoning']) < 100]
long_r = [d for d in data if d.get('reasoning') and len(d['reasoning']) >= 100]
no_reason = [d for d in data if not d.get('reasoning')]
print("reasoning none:", len(no_reason))
print("reasoning <50:", len(short))
print("reasoning 50-100:", len(medium))
print("reasoning 100+:", len(long_r))

short_kq = [d for d in data if d.get('key_quote') and len(d['key_quote']) < 30]
print("key_quote <30:", len(short_kq))

target = len(data) - len(long_r)
print("\nTarget for enhancement:", target)
cost = target * 250 / 1e6 * 3 + target * 200 / 1e6 * 15
print("Est cost: $%.2f" % cost)
print("API calls:", target)

if short:
    s = short[0]
    print("\nExample short reasoning:")
    print("  stock:", s["stock"], "/ signal:", s["signal"])
    print("  key_quote:", (s.get("key_quote") or "")[:100])
    print("  reasoning:", s.get("reasoning") or "")
