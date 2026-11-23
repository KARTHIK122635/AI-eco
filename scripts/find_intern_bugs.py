import json
import re

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    records = [json.loads(line)['content']['data'] for line in f]

for r in records:
    tl = r['jobTitle'].lower()
    if 'intern' in tl and not re.search(r'\bintern\b|\binternship\b|\binterns\b', tl):
        print(f"False intern match: {r['jobId']} | {r['category']} | {r['jobTitle']}")
        print(f"   Reason: {r['classificationReason']}")
