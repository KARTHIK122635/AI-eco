import json

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    records = [json.loads(line)['content']['data'] for line in f]

non_ai_tech = [r for r in records if r['category'] == 'NON_AI_TECH']
print(f"Total NON_AI_TECH records: {len(non_ai_tech)}")

for r in non_ai_tech:
    print(f"{r['jobId']} | {r['companyName']} | {r['jobTitle']}")
    print(f"   Reason: {r['classificationReason']}")
