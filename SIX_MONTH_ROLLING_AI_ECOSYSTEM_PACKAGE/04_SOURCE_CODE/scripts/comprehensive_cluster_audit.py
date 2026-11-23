import json
from collections import Counter

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    records = [json.loads(line)['content']['data'] for line in f]

counts = Counter(r['classificationReason'] for r in records)

print("=== ALL REPEATED CLUSTERS (count >= 10) ===")
for r_text, count in counts.most_common():
    if count >= 10:
        matching = [r for r in records if r['classificationReason'] == r_text]
        print(f"\n[{count}] {r_text[:75]}...")
        # Check title diversity
        distinct_titles = sorted(list(set(m['jobTitle'] for m in matching)))
        if len(distinct_titles) > 10:
            print(f"  Distinct titles: {len(distinct_titles)} (e.g. {distinct_titles[:5]})")
        else:
            print(f"  Titles ({len(distinct_titles)}): {distinct_titles}")
