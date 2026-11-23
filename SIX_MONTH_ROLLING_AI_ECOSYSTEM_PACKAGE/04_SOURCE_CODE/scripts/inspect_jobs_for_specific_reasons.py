import json
import re

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    records = [json.loads(line)['content']['data'] for line in f]

# Find all records with repeated reasons (appearing >= 5 times)
from collections import Counter
counts = Counter(r['classificationReason'] for r in records)
repeated_records = [r for r in records if counts[r['classificationReason']] >= 5]
print(f"Total records with repeated reasons: {len(repeated_records)}")

# Let's inspect some of these jobs across different companies
for comp in ['Anthropic', 'CoreWeave', 'Databricks', 'Scale AI', 'Together AI', 'Cresta', 'SambaNova Systems']:
    comp_jobs = [r for r in repeated_records if r['companyName'].lower() == comp.lower()]
    print(f"\n--- {comp}: {len(comp_jobs)} jobs with repeated reasons ---")
    for j in comp_jobs[:6]:
        print(f"ID: {j['jobId']} | Title: {j['jobTitle']} | Cat: {j['category']}")
        print(f"   Old Reason: {j['classificationReason']}")
        print(f"   Resp Ev: {repr(j['responsibilityEvidence'])[:90]}...")
