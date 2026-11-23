import json
from collections import Counter

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    records = [json.loads(line)['content']['data'] for line in f]

core_records = [r for r in records if r['category'] == 'CORE_AI_ML']
print(f"Total CORE_AI_ML records: {len(core_records)}")

counts = Counter(r['classificationReason'] for r in core_records)
for r_text, c in counts.most_common():
    print(f"{c:2d}x: {r_text[:75]}...")
