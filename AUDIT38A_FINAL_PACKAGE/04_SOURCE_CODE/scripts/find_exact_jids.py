import json

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = [json.loads(line)['content']['data'] for line in f]

titles_to_find = [
    'Systems & Core',
    'Observability',
    'AI/BI',
    'STEM Fellow',
    'grant program',
    'External Artifacts'
]

for t in titles_to_find:
    print(f"=== Search: {t} ===")
    for j in jobs:
        if t.lower() in j['jobTitle'].lower() or t.lower() in (j.get('classificationReason') or '').lower():
            print(f"  {j['jobId']} | {j['companyName']} | {j['jobTitle']} | Cat: {j['category']}")
