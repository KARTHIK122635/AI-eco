import json
from collections import Counter

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    records = [json.loads(line)['content']['data'] for line in f]

backend_records = [r for r in records if r['classificationReason'] == 'Designs, builds, and maintains backend services, distributed systems, and APIs supporting AI platforms.']
biz_records = [r for r in records if r['classificationReason'] == 'Coordinates cross-functional business operations, program delivery, and operational planning cadences.']

print("--- 282 Backend Cluster Unique Titles ---")
titles_282 = sorted(list(set(r['jobTitle'] for r in backend_records)))
print(f"Total unique titles in 282: {len(titles_282)}")
for t in titles_282:
    print(t)

print("\n--- 155 Biz Cluster Unique Titles ---")
titles_155 = sorted(list(set(r['jobTitle'] for r in biz_records)))
print(f"Total unique titles in 155: {len(titles_155)}")
for t in titles_155:
    print(t)
