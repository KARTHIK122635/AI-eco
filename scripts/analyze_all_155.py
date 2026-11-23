import json

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    records = [json.loads(line)['content']['data'] for line in f]

biz_records = [r for r in records if r['classificationReason'] == 'Coordinates cross-functional business operations, program delivery, and operational planning cadences.']

with open('reports/all_155_records.txt', 'w', encoding='utf-8') as f:
    for i, r in enumerate(biz_records, 1):
        f.write(f"[{i}] {r['jobId']} | {r['companyName']} | {r['jobTitle']}\n")
        f.write(f"    Resp: {r.get('responsibilityEvidence', '')}\n")
        f.write(f"    Qual: {r.get('qualificationEvidence', '')}\n")
        f.write("\n")

print(f"Dumped {len(biz_records)} biz records to reports/all_155_records.txt")
