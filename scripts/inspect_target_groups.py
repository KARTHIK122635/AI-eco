import json
from collections import defaultdict

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    records = [json.loads(line)['content']['data'] for line in f]

target_reasons = [
    'Technical engineering position at CoreWeave',
    'Technical engineering position at Anthropic',
    'Corporate operational function at Anthropic',
    'Core software, platform, security, or data engineering supporting AI systems at Anthropic',
    'AI solutions architecture, forward-deployed customer engineering, developer advocacy, or technical AI product management at Databricks'
]

grouped = defaultdict(list)
for r in records:
    if r['classificationReason'] in target_reasons:
        grouped[r['classificationReason']].append(r)

for target in target_reasons:
    recs = grouped[target]
    print(f"=== {target} ({len(recs)} records) ===")
    for r in recs[:5]:
        resp = (r.get('responsibilityEvidence') or '')[:100]
        print(f"  - [{r['category']}] {r['jobTitle']} ({r['jobId']})")
        print(f"    Evidence: {resp}...")
print(f"Total records in these 5 groups: {sum(len(v) for v in grouped.values())}")
