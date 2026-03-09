import sys, os, shutil, subprocess, datetime
sys.stdout.reconfigure(encoding='utf-8')
PROJECT = r'C:\Users\Mario\work\invest-sns'
DEPLOY  = r'C:\Users\Mario\invest-sns-deploy'
OUT     = os.path.join(PROJECT, 'out')
for item in os.listdir(OUT):
    s = os.path.join(OUT, item)
    d = os.path.join(DEPLOY, item)
    if os.path.isdir(s):
        if os.path.exists(d): shutil.rmtree(d)
        shutil.copytree(s, d)
    else:
        shutil.copy2(s, d)
open(os.path.join(DEPLOY, '.nojekyll'), 'w').close()
ts = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
for cmd in [['git','add','-A'],['git','commit','-m',f'deploy: {ts}'],['git','push','origin','gh-pages','--force']]:
    r = subprocess.run(cmd, cwd=DEPLOY, capture_output=True, text=True, timeout=120, encoding='utf-8', errors='replace')
    ok = r.returncode == 0 or 'nothing to commit' in (r.stdout+r.stderr)
    print(('OK' if ok else 'FAIL') + ': ' + cmd[1])
print('Done -> https://puing5555.github.io/invest-sns/')
