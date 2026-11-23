import json

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    records = [json.loads(line)['content']['data'] for line in f]

for r in records:
    tl = r['jobTitle'].lower()
    if 'sourcing' in tl or 'sourcer' in tl:
        print(f"{r['jobId']} | {r['category']} | {r['jobTitle']}")
        print(f"   Reason: {r['classificationReason']}")
