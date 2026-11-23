import os
import sys
sys.path.insert(0, os.path.abspath('.'))
import json

with open('reports/all_109_targets.json', 'r', encoding='utf-8') as f:
    targets = {t['jobId']: t for t in json.load(f)}

failing_ids = [
    'job_4f4361d44526f5d7',
    'job_8341f8a6faee8aef',
    'job_4657d6865ca86588',
    'job_381568cdf3c8852a',
    'job_d4a04d0d1fa3c68e',
    'job_a13a84ccd21c0d5d',
    'job_4ede00298715cd84',
    'job_3a10b52751a1502a',
    'job_9da6bbbe6ce9c2c6',
    'job_03efa7167566fada',
    'job_4c2a3234c5f58949',
    'job_8836aeb7b2444909',
    'job_02a67152c4e32baf',
    'job_350a930679a271b8',
    'job_2cb4170746e06d9c'
]

for jid in failing_ids:
    t = targets[jid]
    print(f"=== {jid} | {t['company']} | {t['title']} ===")
    desc = t['description']
    # search for responsibilities or you will
    for marker in ['Responsibilities', 'Responsibilities:', 'What You’ll Do', 'What you’ll do', 'What you will do', 'You will:', 'In this role, you will', 'What You’ll Do:']:
        p = desc.find(marker)
        if p != -1:
            print(f"--- Marker: {marker} ---")
            print(repr(desc[p:p+400]))
            break
    print("-" * 60)
