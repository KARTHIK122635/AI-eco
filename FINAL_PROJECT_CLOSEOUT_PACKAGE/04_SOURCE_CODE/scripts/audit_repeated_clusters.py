import json
from collections import Counter, defaultdict

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    records = [json.loads(line)['content']['data'] for line in f]

counts = Counter(r['classificationReason'] for r in records)

print("=== AUDIT OF ALL REPEATED CLUSTERS (>= 10) ===")
for reason, count in counts.most_common():
    if count >= 10:
        matching = [r for r in records if r['classificationReason'] == reason]
        titles = sorted(list(set(r['jobTitle'] for r in matching)))
        categories = Counter(r['category'] for r in matching)
        print(f"\n[{count} records] Cat: {dict(categories)} | Reason: {reason[:80]}...")
        if count not in (282, 155, 117):
            print(f"  Titles ({len(titles)}): {titles[:15]}")
            if len(titles) > 15:
                print(f"  ... plus {len(titles)-15} more titles")
