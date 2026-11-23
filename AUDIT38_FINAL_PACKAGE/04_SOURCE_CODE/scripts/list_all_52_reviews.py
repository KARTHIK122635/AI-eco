import sys, os
sys.path.insert(0, os.path.abspath('.'))
import json
import csv
from collections import Counter

from scripts.test_audit10_status_breakdown import results

revs = [r for r in results if r['audit_status'] == 'REQUIRES_REVIEW']
print(f"Total requiring review: {len(revs)}")

by_defect = Counter(r['defects_detected'] for r in revs)
for d, cnt in by_defect.items():
    print(f"({cnt}) {d}")

print("\nList of all records requiring review:")
for i, r in enumerate(revs):
    print(f"[{i+1:2d}] {r['job_id']} | {r['company_name']} | {r['job_title']} | {r['category']} | {r['defects_detected']}")
