import json
from collections import defaultdict, Counter

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    records = [json.loads(line)['content']['data'] for line in f]

by_cat = defaultdict(list)
for r in records:
    by_cat[r['category']].append(r)

for cat in ['AI_INFRASTRUCTURE', 'UNCERTAIN', 'NON_AI_TECH', 'CORE_AI_ML', 'AI_PRODUCT_SOLUTIONS']:
    print(f"=== {cat} ({len(by_cat[cat])} records) ===")
    for r in by_cat[cat][:15]:
        print(f"  [{r['companyName']}] {r['jobTitle']}")
    print()
