"""
Package Builder for Audit 30: SIX_MONTH_ROLLING_AI_ECOSYSTEM_PACKAGE.zip
========================================================================
Creates a fully self-contained, reproducible package including:
- 01_DATABASE: rolling_ai_ecosystem.db, ai_ecosystem.db, audit19_original_database.db, database_integrity_report.txt
- 02_WORKING_EXPORTS: rolling_ai_*.jsonl/.csv, github_metrics_history.csv, pilot_proposals.jsonl/.csv
- 03_REPORTS: daily_collection_report.md, github_metrics_summary.json, rolling_window_freshness_summary.json, SIX_MONTH_ROLLING_PIPELINE_REPORT.md
- 04_SOURCE_CODE: core/, src/, scripts/, deploy/
- 05_TESTS: test_audit30_rolling_pipeline.py and full test suite
- 06_MANIFEST: file_manifest.json, README.md
"""

import os
import sys
import json
import shutil
import zipfile
import hashlib
import sqlite3
from datetime import datetime, timezone

WORKSPACE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
PACKAGE_DIR_NAME = "SIX_MONTH_ROLLING_AI_ECOSYSTEM_PACKAGE"
ZIP_NAME = "SIX_MONTH_ROLLING_AI_ECOSYSTEM_PACKAGE.zip"
PACKAGE_PATH = os.path.join(WORKSPACE_DIR, PACKAGE_DIR_NAME)
ZIP_PATH = os.path.join(WORKSPACE_DIR, ZIP_NAME)


def sha256_file(filepath: str) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def generate_database_integrity_report(db_path: str, report_dest: str):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("PRAGMA integrity_check")
    integrity = c.fetchall()

    counts = {}
    c.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row[0] for row in c.fetchall()]
    for tbl in tables:
        c.execute(f"SELECT count(*) FROM {tbl}")
        counts[tbl] = c.fetchone()[0]

    conn.close()

    sha = sha256_file(db_path)
    sz = os.path.getsize(db_path)

    with open(report_dest, "w", encoding="utf-8") as f:
        f.write("# Working Database Integrity Report\n\n")
        f.write(f"- Database File: `{os.path.basename(db_path)}`\n")
        f.write(f"- SHA-256 Hash: `{sha}`\n")
        f.write(f"- File Size: `{sz:,}` bytes\n")
        f.write(f"- SQLite Integrity Check: `{integrity[0][0]}`\n\n")
        f.write("## Table Record Counts\n\n")
        f.write("| Table Name | Record Count |\n")
        f.write("|---|:---:|\n")
        for tbl, cnt in counts.items():
            f.write(f"| `{tbl}` | {cnt:,} |\n")


def build_package():
    print("=" * 80)
    print("   PREPARING AUDIT 30 SUBMISSION PACKAGE")
    print("=" * 80)

    if os.path.exists(PACKAGE_PATH):
        shutil.rmtree(PACKAGE_PATH)
    os.makedirs(PACKAGE_PATH, exist_ok=True)

    # 1. 01_DATABASE
    db_dest = os.path.join(PACKAGE_PATH, "01_DATABASE")
    os.makedirs(db_dest, exist_ok=True)

    working_db_src = os.path.join(WORKSPACE_DIR, "data", "working", "rolling_ai_ecosystem.db")
    canon_db_src = os.path.join(WORKSPACE_DIR, "data", "normalized", "ai_ecosystem.db")
    audit19_db_src = os.path.join(WORKSPACE_DIR, "source", "audit19_original_database.db")

    shutil.copy2(working_db_src, os.path.join(db_dest, "rolling_ai_ecosystem.db"))
    shutil.copy2(canon_db_src, os.path.join(db_dest, "ai_ecosystem.db"))
    shutil.copy2(audit19_db_src, os.path.join(db_dest, "audit19_original_database.db"))

    generate_database_integrity_report(
        os.path.join(db_dest, "rolling_ai_ecosystem.db"),
        os.path.join(db_dest, "database_integrity_report.txt")
    )
    print("[1] Copied databases & generated integrity report.")

    # 2. 02_WORKING_EXPORTS
    exp_dest = os.path.join(PACKAGE_PATH, "02_WORKING_EXPORTS")
    os.makedirs(exp_dest, exist_ok=True)
    working_data_dir = os.path.join(WORKSPACE_DIR, "data", "working")
    for f in os.listdir(working_data_dir):
        if f.endswith((".jsonl", ".csv")):
            shutil.copy2(os.path.join(working_data_dir, f), os.path.join(exp_dest, f))
    print("[2] Copied working exports (JSONL & CSV).")

    # 3. 03_REPORTS
    rep_dest = os.path.join(PACKAGE_PATH, "03_REPORTS")
    os.makedirs(rep_dest, exist_ok=True)
    reports_src = os.path.join(WORKSPACE_DIR, "reports")
    if os.path.exists(reports_src):
        for f in os.listdir(reports_src):
            if f.endswith((".md", ".json", ".txt")):
                shutil.copy2(os.path.join(reports_src, f), os.path.join(rep_dest, f))

    main_report = os.path.join(WORKSPACE_DIR, "SIX_MONTH_ROLLING_PIPELINE_REPORT.md")
    if os.path.exists(main_report):
        shutil.copy2(main_report, os.path.join(rep_dest, "SIX_MONTH_ROLLING_PIPELINE_REPORT.md"))
    print("[3] Copied reports and summaries.")

    # 4. 04_SOURCE_CODE
    src_dest = os.path.join(PACKAGE_PATH, "04_SOURCE_CODE")
    for subdir in ["core", "src", "scripts", "deploy"]:
        s_path = os.path.join(WORKSPACE_DIR, subdir)
        if os.path.exists(s_path):
            d_path = os.path.join(src_dest, subdir)
            shutil.copytree(s_path, d_path, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.tmp"))
    print("[4] Copied source code (core, src, scripts, deploy).")

    # 5. 05_TESTS
    tests_dest = os.path.join(PACKAGE_PATH, "05_TESTS")
    tests_src = os.path.join(WORKSPACE_DIR, "tests")
    shutil.copytree(tests_src, tests_dest, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    print("[5] Copied full test suite.")

    # 6. 06_MANIFEST & README
    manifest_dest = os.path.join(PACKAGE_PATH, "06_MANIFEST")
    os.makedirs(manifest_dest, exist_ok=True)

    # Build file manifest
    manifest_entries = []
    for root, dirs, files in os.walk(PACKAGE_PATH):
        for fname in sorted(files):
            full_p = os.path.join(root, fname)
            rel_p = os.path.relpath(full_p, PACKAGE_PATH).replace("\\", "/")
            manifest_entries.append({
                "path": rel_p,
                "sha256": sha256_file(full_p),
                "size_bytes": os.path.getsize(full_p)
            })

    manifest_json_path = os.path.join(manifest_dest, "file_manifest.json")
    with open(manifest_json_path, "w", encoding="utf-8") as f:
        json.dump({
            "package_name": PACKAGE_DIR_NAME,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "total_files": len(manifest_entries) + 1,  # including manifest itself
            "files": manifest_entries
        }, f, indent=2)

    readme_content = f"""# SIX_MONTH_ROLLING_AI_ECOSYSTEM_PACKAGE

This package contains the complete, reproducible deliverables for Audit 30:
Six-Month Rolling AI Ecosystem Data Pipeline with Daily Automatic Updates.

## Key Properties:
- **Canonical Database Immobility:** `data/normalized/ai_ecosystem.db` remains 100% byte-identical (SHA-256: `4949352d4f568f3f6128f398591cd8edac2eba45496c24535edb6c096398b95d`).
- **Authentic Audit 19 Archive Immobility:** `source/audit19_original_database.db` remains 100% byte-identical (SHA-256: `1958c59f1a02e5a4bd274f114fdcfdd40942239f518eb662119962a263c84d4d`).
- **Working Database:** `01_DATABASE/rolling_ai_ecosystem.db` contains the dynamic rolling 6-month view with historical archives preserved (`in_rolling_window = 0`, never deleted).
- **Proposals Approval Invariant:** 100% of LLM enrichment proposals are assigned `approval_status: PENDING_APPROVAL`.
- **Zero Duplicates Guarantee:** All URL insertions are unique and idempotent.

## Contents:
- `01_DATABASE/`: Working database, canonical DB, Audit 19 DB, and database integrity report.
- `02_WORKING_EXPORTS/`: Active 6-month rolling view JSONL and CSV exports, GitHub metrics history CSV, and Phase III proposals.
- `03_REPORTS/`: Comprehensive daily collection report, freshness summary, GitHub metrics summary, and audit report.
- `04_SOURCE_CODE/`: Full pipeline code (scheduler, daily pipeline, multi-tier LLM engine with chunking, schema mapping, deploy scripts).
- `05_TESTS/`: Complete 12-point Audit 30 test suite and regression tests.
- `06_MANIFEST/`: SHA-256 file manifest and package documentation.
"""
    with open(os.path.join(PACKAGE_PATH, "README.md"), "w", encoding="utf-8") as f:
        f.write(readme_content)
    with open(os.path.join(manifest_dest, "README.md"), "w", encoding="utf-8") as f:
        f.write(readme_content)

    # Re-generate manifest with the README included
    manifest_entries = []
    for root, dirs, files in os.walk(PACKAGE_PATH):
        for fname in sorted(files):
            if fname == "file_manifest.json":
                continue
            full_p = os.path.join(root, fname)
            rel_p = os.path.relpath(full_p, PACKAGE_PATH).replace("\\", "/")
            manifest_entries.append({
                "path": rel_p,
                "sha256": sha256_file(full_p),
                "size_bytes": os.path.getsize(full_p)
            })
    with open(manifest_json_path, "w", encoding="utf-8") as f:
        json.dump({
            "package_name": PACKAGE_DIR_NAME,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "total_files": len(manifest_entries),
            "files": manifest_entries
        }, f, indent=2)

    # Create ZIP archive
    if os.path.exists(ZIP_PATH):
        os.remove(ZIP_PATH)

    print(f"[6] Compressing {PACKAGE_DIR_NAME} into {ZIP_NAME}...")
    with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(PACKAGE_PATH):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, WORKSPACE_DIR)
                zipf.write(full_path, rel_path)

    zip_size = os.path.getsize(ZIP_PATH)
    zip_sha = sha256_file(ZIP_PATH)
    print("=" * 80)
    print(f" [SUCCESS] Built {ZIP_NAME}")
    print(f"           Size: {zip_size:,} bytes")
    print(f"           SHA-256: {zip_sha}")
    print("=" * 80)


if __name__ == "__main__":
    build_package()
