import csv

with open('reports/stage2_classification_reason_quality_audit.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    fails = [r for r in reader if r['audit_status'] == 'FAIL']

print('Total fails:', len(fails))
for r in fails[:20]:
    print(f"[{r['category']}] {r['company_name']} - {r['job_title']}")
    print(f"  Reason: {r['classification_reason']}")
    print(f"  Defects: {r['defects_detected']}")
    print()
