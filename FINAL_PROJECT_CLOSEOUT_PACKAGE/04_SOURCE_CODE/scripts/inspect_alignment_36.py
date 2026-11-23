import csv

with open('reports/stage2_classification_reason_quality_audit.csv', 'r', encoding='utf-8') as f:
    q_rows = list(csv.DictReader(f))

alignment_reviews = [r for r in q_rows if 'CATEGORY_ALIGNMENT_REVIEW_RECOMMENDED' in r['defects_detected']]
print(f"Total CATEGORY_ALIGNMENT_REVIEW_RECOMMENDED records: {len(alignment_reviews)}")

for i, r in enumerate(alignment_reviews, 1):
    print(f"[{i}] {r['job_id']} | {r['company_name']} | {r['job_title']} | Cat: {r['category']}")
    print(f"    Reason: {r['classification_reason']}")
    print(f"    Note: {r['defects_detected']}")
