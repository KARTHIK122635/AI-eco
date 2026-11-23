import json
from collections import Counter

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    records = [json.loads(line)['content']['data'] for line in f]

print(f"Total records: {len(records)}")

reasons = [r['classificationReason'] for r in records]
counts = Counter(reasons)
print(f"Total distinct reasons: {len(counts)}")

print("\n--- Reasons appearing more than 5 times ---")
for r, c in counts.most_common():
    if c >= 5:
        print(f"{c:3d}x | {r}")
