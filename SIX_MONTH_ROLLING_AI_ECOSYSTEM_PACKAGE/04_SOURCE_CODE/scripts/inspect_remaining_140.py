import json
from build_audit9_reasons import generate_audit9_reason

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    records = [json.loads(line)['content']['data'] for line in f]

backend_fallback = "Designs, builds, and maintains backend services, distributed systems, and APIs supporting AI platforms."
remaining_140 = [r for r in records if generate_audit9_reason(r) == backend_fallback]

print(f"Total remaining in backend fallback: {len(remaining_140)}")
from collections import Counter
titles = Counter(r['jobTitle'] for r in remaining_140)
for t, c in titles.most_common():
    print(f"  {c:2d}x: {t}")
