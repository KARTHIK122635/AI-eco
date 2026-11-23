import csv
import json

with open('reports/stage2_classification_reason_quality_audit.csv', 'r', encoding='utf-8') as f:
    q_rows = list(csv.DictReader(f))

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = {j['jobId']: j for j in [json.loads(line)['content']['data'] for line in f]}

reviews = [r for r in q_rows if r['audit_status'] == 'REQUIRES_REVIEW']
print(f"Total reviews: {len(reviews)}")

for i, r in enumerate(reviews, 1):
    jid = r['job_id']
    j = jobs[jid]
    print(f"[{i}] {jid} | {r['company_name']} | {r['job_title']}")
    print(f"    Category: {r['category']}")
    print(f"    Reason: {r['classification_reason']}")
    print(f"    Defect: {r['defects_detected']}")
    print(f"    Evidence: {j.get('responsibilityEvidence')[:150]}...")
    print("-" * 70)
