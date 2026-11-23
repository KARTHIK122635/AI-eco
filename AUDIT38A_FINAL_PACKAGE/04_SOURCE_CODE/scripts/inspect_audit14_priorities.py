import os
import sys
sys.path.insert(0, os.path.abspath('.'))
import json

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = [json.loads(line)['content']['data'] for line in f]

priorities = [
    'Finance Fellow',
    'Billing Platform',
    'Chip Design RL',
    'Code RL',
    'Principal Software Engineer, GPS',
    'Medical Fellow',
    'Product Marketing Manager, Healthcare',
    'Data Center Technician'
]

for p in priorities:
    matches = [j for j in jobs if p.lower() in j['jobTitle'].lower()]
    print(f"=== Pattern: {p} (matches: {len(matches)}) ===")
    for m in matches:
        print(f"{m['jobId']} | {m['companyName']} | {m['jobTitle']} | Cat: {m['category']}")
        print(f"Reason: {m['classificationReason']}")
        print(f"RespEv: {m['responsibilityEvidence']}")
        print(f"Desc snippet: {m['jobDescription'][:300]}...")
        print("-" * 60)
