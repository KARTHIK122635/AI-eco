import json
from collections import Counter, defaultdict

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    records = [json.loads(line)['content']['data'] for line in f]

counts = Counter(r['classificationReason'] for r in records)

for reason, count in counts.most_common():
    if count >= 10:
        matching = [r for r in records if r['classificationReason'] == reason]
        print(f"\n========================================================")
        print(f"COUNT: {count} | REASON: {reason}")
        print(f"========================================================")
        for r in matching:
            # Let's print jobId, category, title
            print(f"  {r['jobId']} | {r['category']} | {r['jobTitle']}")
