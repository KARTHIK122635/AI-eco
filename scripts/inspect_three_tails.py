import os
import sys
sys.path.insert(0, os.path.abspath('.'))
import json

with open('reports/all_109_targets.json', 'r', encoding='utf-8') as f:
    targets = {t['jobId']: t for t in json.load(f)}

check_ids = ['job_8341f8a6faee8aef', 'job_350a930679a271b8', 'job_2cb4170746e06d9c']

for jid in check_ids:
    t = targets[jid]
    print(f"=== {jid} | {t['company']} | {t['title']} ===")
    desc = t['description']
    print(desc[1600:3000])
    print("-" * 60)
