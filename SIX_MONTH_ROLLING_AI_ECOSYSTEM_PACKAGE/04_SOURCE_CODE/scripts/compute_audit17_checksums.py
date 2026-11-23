import os
import hashlib
import json

files_to_hash = [
    'data/canonical/canonical_jobs.jsonl',
    'data/canonical/canonical_jobs.csv',
    'data/normalized/ai_ecosystem.db',
    'reports/stage2_semantic_classification_audit.csv',
    'reports/stage2_classification_reason_quality_audit.csv',
    'reports/stage2_quality_metrics.json',
    'reports/stage2_url_validation.csv',
    'reports/stage2_ai_relevance_audit.csv',
    'reports/audit17_candidates_inspection.json',
    'reports/audit17_9_corrected_records.json',
    'reports/stage2_independent_audit_report.md'
]

print("=== Audit 17 Deliverables Manifest ===")
results = []
for fpath in files_to_hash:
    size = os.path.getsize(fpath)
    h = hashlib.sha256()
    with open(fpath, 'rb') as f:
        while chunk := f.read(65536):
            h.update(chunk)
    digest = h.hexdigest()
    results.append({
        'path': fpath,
        'size': size,
        'sha256': digest
    })
    print(f"File: {fpath}")
    print(f"  Size:   {size:,} bytes")
    print(f"  SHA256: {digest}\n")

with open('reports/audit17_file_manifest.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2)

print("Saved manifest to reports/audit17_file_manifest.json")
