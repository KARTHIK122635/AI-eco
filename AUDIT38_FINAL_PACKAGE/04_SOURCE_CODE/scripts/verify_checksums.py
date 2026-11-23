import hashlib
import os

files = [
    # Stage 2 Deliverables (Audit 4)
    'data/canonical/canonical_jobs.jsonl',
    'data/canonical/canonical_jobs.csv',
    'data/normalized/ai_ecosystem.db',
    'reports/stage2_independent_audit_report.md',
    'reports/stage2_duplicate_audit.csv',
    'reports/stage2_url_validation.csv',
    'reports/stage2_ai_relevance_audit.csv',
    'reports/stage2_quality_metrics.json',
    # Stage 1 Deliverables
    'data/canonical/canonical_news.jsonl',
    'data/canonical/canonical_news.csv',
    # Phase I Deliverables
    'data/canonical/canonical_startups.jsonl',
    'data/canonical/canonical_startups.csv',
    'data/canonical/canonical_products.jsonl',
    'data/canonical/canonical_products.csv',
    'data/canonical/canonical_research_papers.jsonl',
    'data/canonical/canonical_research_papers.csv'
]

print("=" * 140)
print(f"{'File Path':<50} | {'Size (Bytes)':<12} | {'SHA-256 Cryptographic Checksum'}")
print("=" * 140)
for p in files:
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        while chunk := f.read(65536):
            h.update(chunk)
    sz = os.path.getsize(p)
    print(f"{p:<50} | {sz:<12} | {h.hexdigest()}")
print("=" * 140)
