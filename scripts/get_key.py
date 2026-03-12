import re
content = open('C:/Users/Mario/work/invest-sns/scripts/batch_download_insert.py', encoding='utf-8').read()
key = re.search(r'SUPABASE_KEY\s*=\s*["\']([^"\']+)["\']', content)
if key:
    print(key.group(1))
