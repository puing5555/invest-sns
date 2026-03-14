# -*- coding: utf-8 -*-
import base64, sys

with open(r'C:\Users\Mario\work\invest-sns\scripts\migration_v2_fixed.sql', 'r', encoding='utf-8') as f:
    sql = f.read()

b64 = base64.b64encode(sql.encode('utf-8')).decode('ascii')

js = f"""() => {{
  try {{
    const b64 = '{b64}';
    const sql = decodeURIComponent(escape(atob(b64)));
    const models = window.monaco?.editor?.getModels();
    if(models && models.length > 0) {{
      models[0].setValue(sql);
      return 'OK: ' + sql.length + ' chars injected';
    }}
    return 'monaco not found';
  }} catch(e) {{ return 'error: ' + e.message; }}
}}"""

with open(r'C:\Users\Mario\work\invest-sns\scripts\inject_sql.js', 'w', encoding='utf-8') as f:
    f.write(js)

print(f"B64 length: {len(b64)}")
print(f"SQL length: {len(sql)}")
print("inject_sql.js written")
