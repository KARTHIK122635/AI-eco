import os
import sys
sys.path.insert(0, os.path.abspath('.'))
import json
import re

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = [json.loads(line)['content']['data'] for line in f]

# Let's check which records in canonical_jobs are:
# 1. The 73 flagged from CHECK_WORDS + manual
# 2. The explicit priority roles mentioned in prompt

with open('reports/audit14_73_flagged_candidates.json', 'r', encoding='utf-8') as f:
    c73 = json.load(f)

c73_ids = {c['jobId'] for c in c73}

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

priority_jobs = [j for j in jobs if any(p.lower() in j['jobTitle'].lower() for p in priority_phrases)]

print(f"c73 count: {len(c73_ids)}")
print(f"priority_jobs count: {len(priority_jobs)}")
priority_not_in_c73 = [j for j in priority_jobs if j['jobId'] not in c73_ids]
print(f"Priority jobs not in c73: {len(priority_not_in_c73)}")
for pj in priority_not_in_c73:
    print(f"  {pj['jobId']} | {pj['companyName']} | {pj['jobTitle']}")
    print(f"     Ev: {pj.get('responsibilityEvidence', '')[:100]}...")
