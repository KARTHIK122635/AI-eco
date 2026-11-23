import os
import sys
sys.path.insert(0, os.path.abspath('.'))
import json
import csv
import re
from collections import Counter
from scripts.design_audit13_fixes import REASON_UPDATES, CATEGORY_UPDATES
from scripts.test_audit13_evidence_cleanup import clean_evidence_v13, is_promotional

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = [json.loads(line)['content']['data'] for line in f]

print(f"Total jobs: {len(jobs)}")

# 1. Test Category & Reason updates
for jid, new_cat in CATEGORY_UPDATES.items():
    job = [j for j in jobs if j['jobId'] == jid][0]
    print(f"Category update {jid}: {job['category']} -> {new_cat}")

for jid, new_reason in REASON_UPDATES.items():
    job = [j for j in jobs if j['jobId'] == jid][0]
    assert new_reason.endswith('.'), f"Reason missing period: {new_reason}"
    assert len(new_reason.split()) >= 5, f"Reason too short: {new_reason}"

# 2. Test Evidence extraction
non_verbatim = 0
promo_count = 0
updated_ev_count = 0

for j in jobs:
    ev, ch = clean_evidence_v13(j)
    desc = j.get('jobDescription') or ''
    if ch:
        updated_ev_count += 1
    if ev not in desc:
        non_verbatim += 1
        print(f"Non-verbatim on {j['jobId']}: {ev}")
    if is_promotional(ev):
        promo_count += 1
        print(f"Promo on {j['jobId']}: {ev}")

print(f"Total evidence updated: {updated_ev_count}")
print(f"Non-verbatim errors: {non_verbatim}")
print(f"Promotional errors: {promo_count}")
assert non_verbatim == 0
assert promo_count == 0
print("Evidence pipeline test passed successfully!")
