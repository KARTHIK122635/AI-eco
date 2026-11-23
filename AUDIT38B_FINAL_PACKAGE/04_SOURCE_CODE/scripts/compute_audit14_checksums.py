import os
import sys
sys.path.insert(0, os.path.abspath('.'))
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

results = []
for p in files:
    size = os.path.getsize(p)
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        while chunk := f.read(65536):
            h.update(chunk)
    results.append((p, size, h.hexdigest()))

print(f"{'File Path':<55} | {'Size (Bytes)':<12} | {'SHA-256 Hash'}")
print("-" * 135)
for p, s, digest in results:
    print(f"{p:<55} | {s:<12} | {digest}")
