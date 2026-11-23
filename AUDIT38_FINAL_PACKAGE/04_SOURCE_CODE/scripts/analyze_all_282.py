import json

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    records = [json.loads(line)['content']['data'] for line in f]

backend_records = [r for r in records if r['classificationReason'] == 'Designs, builds, and maintains backend services, distributed systems, and APIs supporting AI platforms.']

with open('reports/all_282_records.txt', 'w', encoding='utf-8') as f:
    for i, r in enumerate(backend_records, 1):
        f.write(f"[{i}] {r['jobId']} | {r['companyName']} | {r['jobTitle']}\n")
        f.write(f"    Resp: {r.get('responsibilityEvidence', '')}\n")
        f.write(f"    Qual: {r.get('qualificationEvidence', '')}\n")
        f.write("\n")

print(f"Dumped {len(backend_records)} backend records to reports/all_282_records.txt")
