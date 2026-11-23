import json
from collections import Counter
from build_155_reasons import get_155_reason

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    records = [json.loads(line)['content']['data'] for line in f]

biz_records = [r for r in records if r['classificationReason'] == 'Coordinates cross-functional business operations, program delivery, and operational planning cadences.']

gen_reason = "Coordinates cross-functional business operations, program delivery, and operational planning cadences."
matches = [r for r in biz_records if get_155_reason(r) == gen_reason]

print(f"Total remaining matches for general reason: {len(matches)}")
for r in matches:
    print(f"{r['jobId']} | {r['companyName']} | {r['jobTitle']}")
    print(f"   Resp: {r.get('responsibilityEvidence', '')[:120]}")
