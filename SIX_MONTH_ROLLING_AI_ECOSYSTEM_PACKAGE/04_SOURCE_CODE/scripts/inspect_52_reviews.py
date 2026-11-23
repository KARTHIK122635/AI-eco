import csv
import json

with open('reports/stage2_classification_reason_quality_audit.csv', 'r', encoding='utf-8') as f:
    q_rows = list(csv.DictReader(f))

reviews = [r for r in q_rows if r['audit_status'] == 'REQUIRES_REVIEW']
print(f"Total REQUIRES_REVIEW records: {len(reviews)}")

for i, r in enumerate(reviews, 1):
    print(f"{i}. {r['job_id']} | {r['company_name']} | {r['job_title']} | Category: {r['category']}")
    print(f"   Reason: {r['classification_reason']}")
    print(f"   Defects/Notes: {r['defects_detected']}")
    print()
