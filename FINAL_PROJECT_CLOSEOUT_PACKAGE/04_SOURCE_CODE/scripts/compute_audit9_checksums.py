import hashlib
import os

files = [
    'data/canonical/canonical_jobs.jsonl',
    'data/canonical/canonical_jobs.csv',
    'data/normalized/ai_ecosystem.db',
    'reports/stage2_semantic_classification_audit.csv',
    'reports/audit9_sample_150_inspection.md',
    'reports/stage2_quality_metrics.json',
    'reports/stage2_ai_relevance_audit.csv'
]

print("SHA-256 Checksums for Stage 2 Audit 9 Deliverables:\n")
for path in files:
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        while chunk := f.read(65536):
            h.update(chunk)
    size = os.path.getsize(path)
    print(f"| `{os.path.basename(path)}` | `{h.hexdigest()}` | {size:,} bytes |")
