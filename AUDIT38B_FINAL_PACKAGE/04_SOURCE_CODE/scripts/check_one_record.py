import json

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    records = [json.loads(line)['content']['data'] for line in f]

for r in records:
    if 'speech & ai technologies' in r['jobTitle'].lower():
        print(f"ID: {r['jobId']} | Title: {r['jobTitle']} | Co: {r['companyName']} | Cat: {r['category']}")
        print(f"  Reason: {r['classificationReason']}")
        print(f"  Resp: {r.get('responsibilityEvidence', '')}")
        print(f"  Desc: {r.get('jobDescription', '')[:300]}")
