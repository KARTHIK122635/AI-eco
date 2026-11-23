import os
import sys
sys.path.insert(0, os.path.abspath('.'))
import json
import re

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = {json.loads(line)['content']['data']['jobId']: json.loads(line)['content']['data'] for line in f}

with open('reports/audit14_73_flagged_candidates.json', 'r', encoding='utf-8') as f:
    c73 = json.load(f)

# Priority jobs that might not be in c73:
priority_phrases = [
    'Finance Fellow',
    'Billing Platform',
    'Chip Design RL',
    'Code RL',
    'Principal Software Engineer, GPS',
    'Medical Fellow',
    'Product Marketing Manager, Healthcare',
    'Data Center Technician'
]

all_target_ids = [c['jobId'] for c in c73]
for jid, j in jobs.items():
    if any(p.lower() in j['jobTitle'].lower() for p in priority_phrases):
        if jid not in all_target_ids:
            all_target_ids.append(jid)

print(f"Total targets to resolve: {len(all_target_ids)}")

for idx, jid in enumerate(all_target_ids, 1):
    j = jobs[jid]
    print(f"[{idx}] {jid} | {j['companyName']} | {j['jobTitle']} | Cat: {j['category']}")
    print(f"    Current: {j.get('responsibilityEvidence')}")
