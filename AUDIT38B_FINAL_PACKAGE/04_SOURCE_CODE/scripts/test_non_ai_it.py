import json
import re

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    records = [json.loads(line)['content']['data'] for line in f]

# Let's inspect NON_AI_TECH 38 records
it_reason = "Develops, maintains, and supports internal IT systems, enterprise applications, and corporate technology."
non_ai_it = [r for r in records if r['category'] == 'NON_AI_TECH' and r['classificationReason'] == it_reason]

print(f"NON_AI_TECH records with generic IT reason: {len(non_ai_it)}")
for r in non_ai_it:
    print(f"  {r['jobId']} | {r['jobTitle']}")
