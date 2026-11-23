import json

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    records = [json.loads(line)['content']['data'] for line in f]

infra_records = [r for r in records if r['category'] == 'AI_INFRASTRUCTURE']
print(f"Total AI_INFRASTRUCTURE records: {len(infra_records)}")

for r in infra_records:
    print(f"{r['jobId']} | {r['companyName']} | {r['jobTitle']}")
    print(f"   Reason: {r['classificationReason']}")
