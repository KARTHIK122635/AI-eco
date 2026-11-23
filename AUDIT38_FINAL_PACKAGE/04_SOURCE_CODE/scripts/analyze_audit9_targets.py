import json
from collections import Counter, defaultdict

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    records = [json.loads(line)['content']['data'] for line in f]

backend_records = [r for r in records if r['classificationReason'] == 'Designs, builds, and maintains backend services, distributed systems, and APIs supporting AI platforms.']
biz_records = [r for r in records if r['classificationReason'] == 'Coordinates cross-functional business operations, program delivery, and operational planning cadences.']

with open('reports/backend_282_details.txt', 'w', encoding='utf-8') as f:
    for r in backend_records:
        f.write(f"ID: {r['jobId']} | Title: {r['jobTitle']} | Co: {r['companyName']} | Cat: {r['category']}\n")
        f.write(f"  Resp: {r.get('responsibilityEvidence', '')[:120]}\n")

with open('reports/biz_155_details.txt', 'w', encoding='utf-8') as f:
    for r in biz_records:
        f.write(f"ID: {r['jobId']} | Title: {r['jobTitle']} | Co: {r['companyName']} | Cat: {r['category']}\n")
        f.write(f"  Resp: {r.get('responsibilityEvidence', '')[:120]}\n")

print(f"Written {len(backend_records)} backend records and {len(biz_records)} biz records.")
