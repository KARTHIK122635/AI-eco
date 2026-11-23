import json
from collections import defaultdict, Counter

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    records = [json.loads(line)['content']['data'] for line in f]

by_cat = defaultdict(list)
for r in records:
    by_cat[r['category']].append(r)

for cat in ['AI_SUPPORTING_TECH', 'NON_TECHNICAL']:
    print(f"=== {cat} ({len(by_cat[cat])} records) ===")
    titles = [r['jobTitle'].strip() for r in by_cat[cat]]
    common_titles = Counter(titles).most_common(20)
    for t, c in common_titles:
        print(f"  {c:2d}x: {t}")
    print()
