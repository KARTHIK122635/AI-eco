import json

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    records = [json.loads(line)['content']['data'] for line in f]

biz_records = [r for r in records if r['classificationReason'] == 'Coordinates cross-functional business operations, program delivery, and operational planning cadences.']

with open('reports/biz_titles_all.txt', 'w', encoding='utf-8') as f:
    for i, r in enumerate(sorted(biz_records, key=lambda x: x['jobTitle']), 1):
        f.write(f"[{i:3d}] {r['jobId']} | {r['companyName']} | {r['jobTitle']}\n")
        f.write(f"      Resp: {r.get('responsibilityEvidence', '')[:140]}\n")

print(f"Dumped {len(biz_records)} biz records sorted by title.")
