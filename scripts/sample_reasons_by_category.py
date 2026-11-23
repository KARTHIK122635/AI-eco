import json
import random
from collections import defaultdict
import sys
sys.path.append('scripts')
from test_comprehensive_audit7_reasons import generate_audit7_reason

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    records = [json.loads(line)['content']['data'] for line in f]

by_cat = defaultdict(list)
for r in records:
    by_cat[r['category']].append(r)

random.seed(42)
for cat, recs in sorted(by_cat.items()):
    print(f"=== Category: {cat} (Total {len(recs)}) ===")
    samples = random.sample(recs, min(3, len(recs)))
    for s in samples:
        new_reason = generate_audit7_reason(s)
        print(f"  [{s['companyName']}] {s['jobTitle']}")
        print(f"    Old: {s['classificationReason']}")
        print(f"    New: {new_reason}")
        print()
