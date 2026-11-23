import json
from collections import Counter, defaultdict

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    records = [json.loads(line)['content']['data'] for line in f]

backend_records = [r for r in records if r['classificationReason'] == 'Designs, builds, and maintains backend services, distributed systems, and APIs supporting AI platforms.']
biz_records = [r for r in records if r['classificationReason'] == 'Coordinates cross-functional business operations, program delivery, and operational planning cadences.']

print("=== BACKEND CLUSTER (282 records) ===")
cat_counts = Counter(r['category'] for r in backend_records)
print("Categories:", cat_counts)

print("\nSample records in Backend Cluster:")
for r in backend_records[:35]:
    print(f"{r['jobId']} | {r['category']} | {r['companyName']} | {r['jobTitle']}")

print("\n=== BUSINESS OPERATIONS CLUSTER (155 records) ===")
cat_counts_biz = Counter(r['category'] for r in biz_records)
print("Categories:", cat_counts_biz)

print("\nSample records in Business Operations Cluster:")
for r in biz_records[:35]:
    print(f"{r['jobId']} | {r['category']} | {r['companyName']} | {r['jobTitle']}")
