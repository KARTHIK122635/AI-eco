import os
import sys
import re
import json
import sqlite3

def audit_file_content(path, title, search_terms):
    print(f"\n=== {title} ({path}) ===")
    if not os.path.exists(path):
        print("  FILE NOT FOUND!")
        return
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()
    print(f"  Line count: {len(lines)}")
    for term in search_terms:
        matches = [idx + 1 for idx, line in enumerate(lines) if re.search(r'\b' + term + r'\b', line, re.IGNORECASE)]
        print(f"  Term '{term}': {len(matches)} occurrences (e.g. lines {matches[:5]})")

# Phase III details
audit_file_content("core/llm/multi_tier_engine.py", "Phase III Multi-Tier Engine", ["chunk", "429", "413", "backoff", "fallback", "retry", "SemanticChunker"])
audit_file_content("core/llm/base.py", "Phase III Base LLM", ["RateLimiter", "TokenUsage", "BaseLLMProvider", "backoff"])
audit_file_content("src/stage3/gemini_provider.py", "Phase III Gemini Provider", ["429", "413", "retry", "backoff", "chunk", "gemini"])
audit_file_content("core/enrichment/engine.py", "Phase III Enrichment Engine", ["enrich", "proposal", "validate", "confidence", "evidence"])

# Phase IV details
audit_file_content("core/entity_resolution.py", "Phase IV Entity Resolution", ["resolve", "match", "similarity", "dedup", "threshold", "canonical"])
audit_file_content("core/deduplicator.py", "Phase IV Deduplicator", ["deduplicate", "hash", "exact", "fuzzy", "key"])
audit_file_content("core/canonical.py", "Phase IV Canonical", ["normalize", "domain", "canonical", "clean"])

# Phase V details
audit_file_content("core/github_client.py", "Phase V GitHub Client", ["rate_limit", "backoff", "retry", "token", "headers", "user-agent", "crawl", "async"])
audit_file_content("core/github_discovery.py", "Phase V GitHub Discovery", ["discover", "arxiv", "paper", "product", "extract", "association"])
audit_file_content("core/github_metrics.py", "Phase V GitHub Metrics", ["snapshot", "stars", "forks", "issues", "poll"])
audit_file_content("core/github_deltas.py", "Phase V GitHub Deltas", ["MIN_WEEKLY_INTERVAL_DAYS", "delta", "velocity", "growth", "reliable"])
audit_file_content("core/github_analytics.py", "Phase V GitHub Analytics", ["LifecycleState", "ACTIVE_VERIFIED", "classify", "coverage"])

# Phase VI details
audit_file_content("core/sheets_sync_engine.py", "Phase VI Sheets Sync Engine", ["sync", "batch", "update", "write", "audit"])
audit_file_content("core/sheets_dashboard_builder.py", "Phase VI Dashboard Builder", ["chart", "card", "formula", "grid", "format"])
audit_file_content("core/sheets_transformer.py", "Phase VI Sheets Transformer", ["sanitize_cell_value", "formula", "injection", "normalize"])
audit_file_content("core/github_dashboard_exporter.py", "Phase VI Dashboard Exporter", ["export", "manifest", "sha256", "repositories", "metrics"])

# Deliverables checks
print("\n=== SPECIAL DELIVERABLES AUDIT ===")
for fname in ["README.md", "requirements.txt", "architecture.pdf", "main.py"]:
    exists = os.path.exists(fname)
    size = os.path.getsize(fname) if exists else 0
    print(f"File '{fname}': Exists={exists}, Size={size} bytes")

# Check for any .pdf file in repository
pdf_files = []
for root, dirs, files in os.walk("."):
    for f in files:
        if f.lower().endswith(".pdf"):
            pdf_files.append(os.path.join(root, f))
print(f"All PDF files in repo: {pdf_files}")

# Check Phase VI Reports in reports/phase6_dashboard
print("\n=== PHASE VI REPORTS AUDIT ===")
p6_reports_dir = "reports/phase6_dashboard"
if os.path.exists(p6_reports_dir):
    for f in sorted(os.listdir(p6_reports_dir)):
        p = os.path.join(p6_reports_dir, f)
        print(f"  {f:<40} | Size: {os.path.getsize(p)} bytes")
else:
    print("  reports/phase6_dashboard NOT FOUND")

def audit_database_counts():
    print("\n=== DATABASE COUNTS AUDIT ===")
    dbs = {
        'Canonical': 'data/normalized/ai_ecosystem.db',
        'Audit19': 'source/audit19_original_database.db',
        'Baseline': 'data/working/rolling_ai_ecosystem.db',
        'Candidate': 'data/working/candidate_rolling_ai_ecosystem.db',
        'Phase V Candidate': 'data/working/phase5_github_candidate.db'
    }

    for name, path in dbs.items():
        print(f"\n--- {name} ({path}) ---")
        if not os.path.exists(path):
            print("  FILE NOT FOUND!")
            continue
        conn = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
        c = conn.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        tables = [r[0] for r in c.fetchall()]
        total_records = 0
        for t in sorted(tables):
            c.execute(f"SELECT count(*) FROM \"{t}\";")
            cnt = c.fetchone()[0]
            total_records += cnt
            print(f"  {t:<35}: {cnt:>6} rows")
        print(f"  TOTAL ROWS IN DB: {total_records:>6}")
        conn.close()

if __name__ == "__main__":
    audit_database_counts()
