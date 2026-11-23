import os
import hashlib

files = [
    'data/canonical/canonical_jobs.jsonl',
    'data/canonical/canonical_jobs.csv',
    'data/normalized/ai_ecosystem.db',
    'reports/stage2_semantic_classification_audit.csv',
    'reports/stage2_classification_reason_quality_audit.csv',
    'reports/stage2_url_validation.csv',
    'reports/stage2_ai_relevance_audit.csv',
    'reports/stage2_quality_metrics.json',
    'reports/audit10_uncertain_records_inspection.md'
]

print("=== DELIVERABLE SIZES & SHA-256 CHECKSUMS (AUDIT 13) ===")
for p in files:
    h = hashlib.sha256()
    size = os.path.getsize(p)
    with open(p, 'rb') as f:
        while chunk := f.read(65536):
            h.update(chunk)
    print(f"{p} | {size:,} bytes | {h.hexdigest()}")
