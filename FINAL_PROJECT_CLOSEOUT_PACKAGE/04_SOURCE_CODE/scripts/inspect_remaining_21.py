import os
import sys
sys.path.insert(0, os.path.abspath('.'))
import json

with open('reports/all_109_targets.json', 'r', encoding='utf-8') as f:
    targets = {t['jobId']: t for t in json.load(f)}

check_ids = [
    'job_8d17c9b890a373ab', 'job_fd37980b24dac13a',
    'job_d93736d1ee4a9098', 'job_d3b042fdf4d449c3',
    'job_0887970c910f71b5', 'job_088711206e853a98',
    'job_9da6bbbe6ce9c2c6', 'job_03efa7167566fada',
    'job_4c2a3234c5f58949', 'job_8836aeb7b2444909',
    'job_af0d701a2b68fde4', 'job_6b706fa6b3fac5a0',
    'job_fb3b97caf24d3590', 'job_02a67152c4e32baf',
    'job_e7b91d4cbd86b68f', 'job_beb466c57c7e3e6e',
    'job_df0e763acd964f03', 'job_e86f546d333b6cd8',
    'job_350a930679a271b8', 'job_2cb4170746e06d9c',
    'job_2131aa478b54ee53'
]

for jid in check_ids:
    t = targets[jid]
    print(f"=== {jid} | {t['company']} | {t['title']} ===")
    print(f"Reason: {t['reason']}")
    print(f"Current Ev: {t['current_evidence']}")
    desc = t['description']
    # find responsibilities or you will
    for marker in ['Responsibilities', 'Responsibilities:', 'What you’ll do', 'What you\'ll do', 'You will:', 'In this role, you will', 'What You’ll Do', 'Role:']:
        p = desc.find(marker)
        if p != -1:
            print(f"--- Marker: {marker} ---")
            print(desc[p:p+500])
            break
    print("-" * 60)
