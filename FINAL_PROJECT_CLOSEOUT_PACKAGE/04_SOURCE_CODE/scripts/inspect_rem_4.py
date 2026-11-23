import os
import sys
sys.path.insert(0, os.path.abspath('.'))
import json

with open('reports/all_109_targets.json', 'r', encoding='utf-8') as f:
    targets = {t['jobId']: t for t in json.load(f)}

rem_ids = [
    'job_6b706fa6b3fac5a0',
    'job_fb3b97caf24d3590',
    'job_beb466c57c7e3e6e',
    'job_350a930679a271b8'
]

for jid in rem_ids:
    t = targets[jid]
    print(f"=== {jid} | {t['company']} | {t['title']} ===")
    desc = t['description']
    for kw in ['Responsibilities:', 'Responsibilities', 'What You’ll Do:', 'What you’ll do', 'Role']:
        p = desc.find(kw)
        if p != -1:
            print(f"--- Marker: {kw} ---")
            print(desc[p:p+500])
            break
    print("-" * 60)
