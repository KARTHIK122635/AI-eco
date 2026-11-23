import json
from collections import Counter

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    records = [json.loads(line)['content']['data'] for line in f]

prod_records = [r for r in records if r['category'] == 'AI_PRODUCT_SOLUTIONS']
print(f"Total AI_PRODUCT_SOLUTIONS records: {len(prod_records)}")

counts = Counter(r['classificationReason'] for r in prod_records)
for r_text, c in counts.most_common():
    print(f"{c:2d}x: {r_text[:75]}...")
