import csv

with open('reports/stage2_classification_reason_quality_audit.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    fails = [r for r in reader if r['audit_status'] == 'FAIL']

print(f"Total fails: {len(fails)}")
for i, f in enumerate(fails):
    print(f"[{i+1:2d}] {f['job_id']} | {f['category']} | {f['defects_detected']}")
    print(f"     Title: {f['company_name']} - {f['job_title']}")
    print(f"     Reason: {f['classification_reason']}")
