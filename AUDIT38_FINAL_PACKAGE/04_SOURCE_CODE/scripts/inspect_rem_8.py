import os
import sys
sys.path.insert(0, os.path.abspath('.'))
import json

with open('reports/all_109_targets.json', 'r', encoding='utf-8') as f:
    targets = {t['jobId']: t for t in json.load(f)}

rem_ids = [
    'job_088711206e853a98',
    'job_af0d701a2b68fde4',
    'job_6b706fa6b3fac5a0',
    'job_fb3b97caf24d3590',
    'job_beb466c57c7e3e6e',
    'job_df0e763acd964f03',
    'job_350a930679a271b8',
    'job_2131aa478b54ee53'
]

for jid in rem_ids:
    t = targets[jid]
    print(f"=== {jid} | {t['company']} | {t['title']} ===")
    print(f"Reason: {t['reason']}")
    print(f"Current Ev: {t['current_evidence']}")
    desc = t['description']
    print("DESC SNIPPET (chars 300 to 1200):")
    print(desc[300:1200])
    print("-" * 60)
