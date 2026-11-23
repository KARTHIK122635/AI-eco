import json
from collections import Counter

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    records = [json.loads(line)['content']['data'] for line in f]

counts = Counter(r['classificationReason'] for r in records)

with open('reports/medium_clusters_utf8.txt', 'w', encoding='utf-8') as f:
    for reason, count in counts.most_common():
        if 10 <= count <= 45:
            matching = [r for r in records if r['classificationReason'] == reason]
            f.write(f"\n--- {count} records: {reason} ---\n")
            for m in matching:
                f.write(f"    {m['jobId']} | {m['category']} | {m['companyName']} | {m['jobTitle']}\n")

print("Written reports/medium_clusters_utf8.txt successfully.")
