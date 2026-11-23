import json
from collections import Counter
from build_282_reasons import get_282_reason

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    records = [json.loads(line)['content']['data'] for line in f]

backend_records = [r for r in records if r['classificationReason'] == 'Designs, builds, and maintains backend services, distributed systems, and APIs supporting AI platforms.']

common_reason = "Designs, builds, and scales core backend services, distributed systems, and API infrastructure supporting AI platforms."
common_matches = [r for r in backend_records if get_282_reason(r) == common_reason]

print(f"Total matching common reason: {len(common_matches)}")
titles = Counter(r['jobTitle'] for r in common_matches)
for t, c in titles.most_common():
    print(f"  {c:2d}x: {t}")
