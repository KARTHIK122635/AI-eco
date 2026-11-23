import csv

with open('reports/stage2_classification_reason_quality_audit.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row['audit_status'] != 'PASS':
            print(f"{row['job_id']} | {row['company_name']} | {row['job_title']} | {row['category']} | Status: {row['audit_status']} | Defects: {row['defects_detected']}")
            print(f"   Reason: {row['classification_reason']}")
