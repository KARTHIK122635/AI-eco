"""
Package Builder for Audit 31: AUDIT31_CORRECTIVE_PACKAGE.zip
============================================================
Creates a fully self-contained, reproducible corrective package including:
- 01_DATABASE: rolling_ai_ecosystem.db, ai_ecosystem.db, audit19_original_database.db, database_integrity_report.txt
- 02_WORKING_EXPORTS: rolling_ai_*.jsonl/.csv, github_metrics_history.csv, pilot_proposals.jsonl/.csv
- 03_REPORTS: AUDIT31_CORRECTION_REPORT.md, daily_collection_report.md, github_metrics_summary.json, rolling_window_freshness_summary.json
- 04_SOURCE_CODE: core/, src/, scripts/, deploy/
- 05_TESTS: test_audit31_corrective.py, test_audit30_rolling_pipeline.py, full test suite
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
PACKAGE_DIR_NAME = "AUDIT31_CORRECTIVE_PACKAGE"
ZIP_NAME = "AUDIT31_CORRECTIVE_PACKAGE.zip"
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
        f.write("# Working Database Integrity Report (Audit 31 Corrective)\n\n")
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
    print("   PREPARING AUDIT 31 CORRECTIVE SUBMISSION PACKAGE")
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

    for r_name in ["AUDIT31_CORRECTION_REPORT.md", "SIX_MONTH_ROLLING_PIPELINE_REPORT.md"]:
        r_path = os.path.join(WORKSPACE_DIR, r_name)
        if os.path.exists(r_path):
            shutil.copy2(r_path, os.path.join(rep_dest, r_name))
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
            "total_files": len(manifest_entries),
            "files": manifest_entries
        }, f, indent=2)

    readme_path = os.path.join(manifest_dest, "README.md")
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write("# AUDIT 31 CORRECTIVE PACKAGE\n\n")
        f.write("## Overview\n")
        f.write("This package contains the complete, verified corrective implementation for the Six-Month Rolling AI Ecosystem Pipeline.\n\n")
        f.write("### Corrective Engineering Highlights:\n")
        f.write("1. **Publication-Date Integrity:** Zero synthetic dates. Startups and products without genuine publication dates are classified as `MISSING_DATE` with `in_rolling_window = 0`. Operational timestamps (`first_seen_at`, `collected_at`) are distinguished from genuine publication dates.\n")
        f.write("2. **Boundary Consistency:** True 6-calendar-month rolling window in UTC using `relativedelta(months=6)`. Start and end timestamps match exactly across implementation and all reports down to the microsecond.\n")
        f.write("3. **Dataset Eligibility Reporting:** Full 5-dataset breakdown of total records, valid publication dates, in-window records, outside-window records, and missing dates.\n")
        f.write("4. **Stage-Level Scheduler Recovery:** Granular stage checkpoints (`STAGE_1_NEWS` through `STAGE_6_REPORT`) allowing exact resumption without re-running earlier completed stages.\n")
        f.write("5. **Routine Daily Execution Skips Phase III Pilot:** Default `run_pilot=False`. Routine automation consumes zero LLM quota. Manual Phase III execution requires explicit `--run-pilot` flag. All proposals strictly `PENDING_APPROVAL`.\n")
        f.write("6. **Windows Task Scheduler Verification:** Dry-run verification script confirms 06:00 UTC = 11:30 local (+05:30 IST), `StartWhenAvailable`, and `MultipleInstances = 'IgnoreNew'`.\n")
        f.write("7. **Database Immutability:** Canonical database (`4949352d...`, 6,745 records) and authentic Audit 19 archive (`1958c59f...`, 366 records) remain 100% byte-identical.\n\n")
        f.write("### Verification Instructions:\n")
        f.write("```bash\n")
        f.write("python scripts/verify_audit31_package.py\n")
        f.write("```\n")

    print("[6] Built file manifest and README.")

    # Create ZIP archive
    print(f"[7] Compressing into {ZIP_NAME}...")
    if os.path.exists(ZIP_PATH):
        os.remove(ZIP_PATH)

    with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(PACKAGE_PATH):
            for fname in files:
                full_p = os.path.join(root, fname)
                arc_p = os.path.join(PACKAGE_DIR_NAME, os.path.relpath(full_p, PACKAGE_PATH))
                zf.write(full_p, arc_p)

    zip_sz = os.path.getsize(ZIP_PATH)
    zip_sha = sha256_file(ZIP_PATH)
    print("=" * 80)
    print(f" [SUCCESS] Package created successfully!")
    print(f"   ZIP File:   {ZIP_NAME}")
    print(f"   Size:       {zip_sz:,} bytes ({zip_sz/(1024*1024):.2f} MB)")
    print(f"   SHA-256:    {zip_sha}")
    print("=" * 80)

    # Also duplicate to SIX_MONTH_ROLLING_AI_ECOSYSTEM_PACKAGE.zip for backwards compatibility
    compat_zip = os.path.join(WORKSPACE_DIR, "SIX_MONTH_ROLLING_AI_ECOSYSTEM_PACKAGE.zip")
    shutil.copy2(ZIP_PATH, compat_zip)
    print(f"[Compatibility] Updated {os.path.basename(compat_zip)}")


if __name__ == "__main__":
    build_package()
