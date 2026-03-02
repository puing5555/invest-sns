import os, json, sys
sys.path.insert(0, os.path.dirname(__file__))

# All video IDs from yt-dlp crawl
all_ids = """Ke7gQMbIFLI
4wCO1fdl9iU
4cCGQFHrbK4
BdNikaqw238
UVeJSmWGzRw
zMHD_MYLZtU
wLwygCnx7V8
ZM589mmdDcc
iLUIU1sU1Ug
4kJxnR-XIfY
Lszaj6NhNcA
LXzCL-duG14
-3odSn4Wi2E
iNAlXUEw9tc
A2l1-lyzq4Q
q4vz1jhWS4s
JzzXPN5v1BI
6Bk_eG77-5g
1xfjt7moZEg
AnHiiYa48Y0
UVS-61j-76o
yxt087-C1zk
QajNAfX5YvI
BQY0eh1lcUk
79PFFmQQjOw
4bClsFvaoLs
RXdOkIaSIzc
BeEHwOe-J98
4UvO-6eecv8
W0Jdfz35WE0
1bcmmTZRX5Q
uMglUc_vQ6A
EaclBpfxjCI
0z8e_heKtKk
vpLSDLs6Fis
cfwN1eWNlFA
NlWaAL3SOxE
blAWrFLQ_Lc
qkpmS6yfO_g
KvuATAaRxe8
j3x7149DzDQ
KkxAjOp-6H4
Y9JMqS87HEM
YkTfK92S8jA
sU0zaA0oJVk
bk-2Y0tjnZQ
lFb4s3I5cKc
un9IHz9LnrA
rde-ahZ29UQ
P-XpZ3l9DtQ
cjKV1A7UTvI
E0l6aYaff0U
vE55S-x-6Lc
CN_T1V1ocjg
VdxXXSCbiEc
Qowcv46AneI
Ol6u0WgN6E4
aW0cZ-rmzz8
NcijgSSeJVU
zRGNYWXHfV4
IOVmGeSwAMM
Cgj6y_1_sS4
oiAMDjdr334
Te7EzydvBT4
YbbV60KVe_c
u9okzlmKq_E
vR-IeyHBRkg
EYjyQFDTmfg
awxGkVGfQ_w
4yZDpfDT7K8
4Bay6eXJH1Q
UCX7_tJGgc4
qXsMMse-vos
5ZpG1gxdDfg
FrOAHoV0pH4
3NUs0JElPvs
QJf40N2wvh8
zre4X1a4QlY
vMmuwRuxpGA
5I9wb6NKNUs
NVieilk8oHI
RNvKFfEru-o
HK9jUm9lcEA
5Py7WIb8iYw
pmlsIYTKiw4
yWWdUIrVf34
OadsiFLklsM
qMhEf1864vc
-JsPLE90h1Q
PPsCEEUIGqk
tR5OyzvKCgE
MlFXn9P0YsM
4h-fPWoA2W4
5aGn5CqbQls
ni_DydrX_uI
AaJTT_GTkKY
RrSo7nQFSGY
XKisExNmEGc
peYoNFd3z9E
J5_S29fQybw
WVYVfmpLg4Q
eiC2ndorjDQ
Du_VW1HIG5s
U3Xa3h3kztg
7UoMvJPj0gw
O0OVrGY7JUc
eXlKZ1D-mwM
7mzsY68IhhI
9cg-iVIkg20
JF34kovcvPk
ojsKQd_mJmk""".strip().split('\n')

print(f"Total videos from channel: {len(all_ids)}")

# Load env
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env.local'))

import requests

url = os.environ['NEXT_PUBLIC_SUPABASE_URL']
key = os.environ['SUPABASE_SERVICE_ROLE_KEY']

headers = {
    'apikey': key,
    'Authorization': f'Bearer {key}',
}

# Get all existing video_ids for sesang101
r = requests.get(
    f"{url}/rest/v1/influencer_videos?channel_id=eq.d68f8efd-64c8-4c07-9d34-e98c2954f4e1&select=video_id,title,published_at",
    headers=headers
)
existing = r.json()
existing_ids = set(v['video_id'] for v in existing)
print(f"Existing in DB: {len(existing_ids)}")

missing = [vid for vid in all_ids if vid not in existing_ids]
print(f"Missing: {len(missing)}")
for vid in missing:
    print(f"  https://youtube.com/watch?v={vid}")
