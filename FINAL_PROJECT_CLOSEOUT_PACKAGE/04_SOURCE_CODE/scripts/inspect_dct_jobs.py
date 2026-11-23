import os
import sys
sys.path.insert(0, os.path.abspath('.'))
import json

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = {json.loads(line)['content']['data']['jobId']: json.loads(line)['content']['data'] for line in f}

dct_ids = [
    'job_4f4361d44526f5d7',
    'job_a2b5203844474445',
    'job_de27bd5296f47999',
    'job_e6c5f4d8890b7630',
    'job_509b55147b60eecb',
    'job_7427cacb294b9060',
    'job_f9a9b26d75b45013',
    'job_7d02a7727c51c1d9'
]

for jid in dct_ids:
    j = jobs[jid]
    print(f"=== {jid} | {j['jobTitle']} ===")
    print("Current Ev:", j.get('responsibilityEvidence'))
    desc = j['jobDescription']
    # find responsibilities or duties
    for kw in ['Responsibilities', 'responsibilities', 'About the Role', 'About the role', 'Role:']:
        p = desc.find(kw)
        if p != -1:
            print(f"--- Section {kw} ---")
            print(desc[p:p+500])
            break
    print("-" * 60)
