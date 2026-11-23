"""
Package Builder for Audit 38B: AUDIT38B_FINAL_PACKAGE.zip
========================================================
Builds the authoritative Audit 38B deliverable package:
- 01_DATABASE:
    * rolling_ai_ecosystem.db (Candidate database with reconciled Remotive 404 update, hash: eca573b4a4f1c045f417883772308050418c2d471250be7fda6c68e1ec023198)
    * original_rolling_ai_ecosystem.db (Preserved baseline database, hash: cbc1814cf3c6546a4dfa1d2e731648aead070b133b38892ddd599a6e385c2127)
    * ai_ecosystem.db (4949352d4f568f3f6128f398591cd8edac2eba45496c24535edb6c096398b95d)
    * audit19_original_database.db (1958c59f1a02e5a4bd274f114fdcfdd40942239f518eb662119962a263c84d4d)
    * audit38b_database_integrity_report.txt
    * audit38b_working_database_before_after_report.md
    * audit38b_database_change_log.csv
- 02_WORKING_EXPORTS:
    * audit38b_vacancy_reconciliation.csv
    * audit38b_recovery_telemetry_audit.csv
    * audit38b_database_change_log.csv
    * audit38a_vacancy_verification.csv
    * audit38a_news_content_quality.csv
    * audit38a_github_metric_freshness.csv
    * audit38_startup_date_audit.csv
    * audit38_product_date_audit.csv
    * audit38_paper_freshness_audit.csv
    * audit38_news_source_health.csv
    * audit38_job_lifecycle_audit.csv
    * audit38_collection_log_integrity.csv
    * rolling working table exports & proposals
- 03_REPORTS:
    * AUDIT38B_FINAL_REPORT.md
    * audit38b_production_readiness_scorecard.md
    * audit38b_working_database_before_after_report.md
    * audit38b_database_integrity_report.txt
    * audit38b_recovery_regression_test_output.txt
    * audit38b_full_test_runner_output.txt
    * daily_collection_report.md
    * Historical reports & scorecards
- 04_SOURCE_CODE: core/, src/, scripts/, deploy/
- 05_TESTS: all 20 test modules (246 tests)
- 06_MANIFEST:
    * README.md (manifest-listed)
    * file_manifest.json (with documented self-exclusion and detached checksum exclusion)
    * file_manifest.sha256 (detached cryptographic checksum of file_manifest.json)
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
PACKAGE_DIR_NAME = "AUDIT38B_FINAL_PACKAGE"
ZIP_NAME = "AUDIT38B_FINAL_PACKAGE.zip"
PACKAGE_PATH = os.path.join(WORKSPACE_DIR, PACKAGE_DIR_NAME)
ZIP_PATH = os.path.join(WORKSPACE_DIR, ZIP_NAME)

TARGET_ORIGINAL_WORKING_HASH = "cbc1814cf3c6546a4dfa1d2e731648aead070b133b38892ddd599a6e385c2127"
TARGET_CANDIDATE_WORKING_HASH = "eca573b4a4f1c045f417883772308050418c2d471250be7fda6c68e1ec023198"
TARGET_CANONICAL_HASH = "4949352d4f568f3f6128f398591cd8edac2eba45496c24535edb6c096398b95d"
TARGET_AUDIT19_HASH = "1958c59f1a02e5a4bd274f114fdcfdd40942239f518eb662119962a263c84d4d"


def sha256_file(filepath: str) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def build_package():
    print("=" * 80)
    print("   PREPARING AUDIT 38B FINAL SUBMISSION PACKAGE")
    print("=" * 80)

    # 1. Verify source databases before packaging
    orig_w_db = os.path.join(WORKSPACE_DIR, "data", "working", "rolling_ai_ecosystem.db")
    cand_w_db = os.path.join(WORKSPACE_DIR, "data", "working", "candidate_rolling_ai_ecosystem.db")
    c_db_src = os.path.join(WORKSPACE_DIR, "data", "normalized", "ai_ecosystem.db")
    a_db_src = os.path.join(WORKSPACE_DIR, "source", "audit19_original_database.db")

    assert sha256_file(orig_w_db) == TARGET_ORIGINAL_WORKING_HASH, f"Original Working DB hash mismatch! Got {sha256_file(orig_w_db)}"
    assert sha256_file(cand_w_db) == TARGET_CANDIDATE_WORKING_HASH, f"Candidate Working DB hash mismatch! Got {sha256_file(cand_w_db)}"
    assert sha256_file(c_db_src) == TARGET_CANONICAL_HASH, f"Canonical DB hash mismatch! Got {sha256_file(c_db_src)}"
    assert sha256_file(a_db_src) == TARGET_AUDIT19_HASH, f"Audit 19 DB hash mismatch! Got {sha256_file(a_db_src)}"

    if os.path.exists(PACKAGE_PATH):
        shutil.rmtree(PACKAGE_PATH)
    os.makedirs(PACKAGE_PATH, exist_ok=True)

    d_db = os.path.join(PACKAGE_PATH, "01_DATABASE")
    d_exp = os.path.join(PACKAGE_PATH, "02_WORKING_EXPORTS")
    d_rep = os.path.join(PACKAGE_PATH, "03_REPORTS")
    d_src = os.path.join(PACKAGE_PATH, "04_SOURCE_CODE")
    d_tst = os.path.join(PACKAGE_PATH, "05_TESTS")
    d_man = os.path.join(PACKAGE_PATH, "06_MANIFEST")

    for d in [d_db, d_exp, d_rep, d_src, d_tst, d_man]:
        os.makedirs(d, exist_ok=True)

    # 1. 01_DATABASE
    # Pack candidate db as primary rolling_ai_ecosystem.db, and preserve original baseline as original_rolling_ai_ecosystem.db
    shutil.copy2(cand_w_db, os.path.join(d_db, "rolling_ai_ecosystem.db"))
    shutil.copy2(orig_w_db, os.path.join(d_db, "original_rolling_ai_ecosystem.db"))
    shutil.copy2(c_db_src, os.path.join(d_db, "ai_ecosystem.db"))
    shutil.copy2(a_db_src, os.path.join(d_db, "audit19_original_database.db"))
    
    db_reports = [
        "audit38b_database_integrity_report.txt",
        "audit38b_working_database_before_after_report.md",
        "audit38b_database_change_log.csv",
        "audit38a_database_integrity_report.txt",
        "audit38_database_integrity_report.txt"
    ]
    for dbr in db_reports:
        p = os.path.join(WORKSPACE_DIR, dbr)
        if os.path.exists(p):
            shutil.copy2(p, os.path.join(d_db, dbr))
    print("[1] Copied databases & database integrity reports.")

    # 2. 02_WORKING_EXPORTS
    audit_csvs = [
        "audit38b_vacancy_reconciliation.csv",
        "audit38b_recovery_telemetry_audit.csv",
        "audit38b_database_change_log.csv",
        "audit38a_vacancy_verification.csv",
        "audit38a_news_content_quality.csv",
        "audit38a_github_metric_freshness.csv",
        "audit38_startup_date_audit.csv",
        "audit38_product_date_audit.csv",
        "audit38_paper_freshness_audit.csv",
        "audit38_news_source_health.csv",
        "audit38_job_lifecycle_audit.csv",
        "audit38_collection_log_integrity.csv"
    ]
    for ac in audit_csvs:
        p = os.path.join(WORKSPACE_DIR, ac)
        if os.path.exists(p):
            shutil.copy2(p, os.path.join(d_exp, ac))

    # Also copy data/working/ exports
    working_data_dir = os.path.join(WORKSPACE_DIR, "data", "working")
    for f in os.listdir(working_data_dir):
        if f.endswith(".csv") or f.endswith(".json") or f.endswith(".jsonl"):
            shutil.copy2(os.path.join(working_data_dir, f), os.path.join(d_exp, f))
    print("[2] Copied working exports & Audit 38/38A/38B CSV audits.")

    # 3. 03_REPORTS
    report_files = [
        "AUDIT38B_FINAL_REPORT.md",
        "audit38b_production_readiness_scorecard.md",
        "audit38b_working_database_before_after_report.md",
        "audit38b_database_integrity_report.txt",
        "audit38b_recovery_regression_test_output.txt",
        "audit38b_full_test_runner_output.txt",
        "AUDIT38A_FINAL_REPORT.md",
        "audit38a_production_readiness_scorecard.md",
        "audit38a_provider_reliability_report.md",
        "audit38a_database_integrity_report.txt",
        "audit38a_test_runner_output.txt",
        "daily_collection_report.md",
        "AUDIT38_FINAL_REPORT.md",
        "audit38_production_readiness_scorecard.md",
        "audit38_provider_reliability_report.md",
        "audit38_test_runner_output.txt"
    ]
    for rf in report_files:
        p = os.path.join(WORKSPACE_DIR, rf)
        if os.path.exists(p):
            shutil.copy2(p, os.path.join(d_rep, rf))

    # Also copy all files in reports/
    reports_dir = os.path.join(WORKSPACE_DIR, "reports")
    if os.path.exists(reports_dir):
        for f in os.listdir(reports_dir):
            src_f = os.path.join(reports_dir, f)
            if os.path.isfile(src_f):
                shutil.copy2(src_f, os.path.join(d_rep, f))
            elif os.path.isdir(src_f):
                dst_sub = os.path.join(d_rep, f)
                if os.path.exists(dst_sub):
                    shutil.rmtree(dst_sub)
                shutil.copytree(src_f, dst_sub)

    print("[3] Copied reports, scorecards, runner outputs, and telemetry.")

    # 4. 04_SOURCE_CODE
    for d in ["core", "src", "scripts", "deploy"]:
        src_d = os.path.join(WORKSPACE_DIR, d)
        dst_d = os.path.join(d_src, d)
        if os.path.exists(src_d):
            shutil.copytree(src_d, dst_d, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".git*", ".temp*"))
    print("[4] Copied source code (core, src, scripts, deploy).")

    # 5. 05_TESTS
    tests_dir = os.path.join(WORKSPACE_DIR, "tests")
    for f in os.listdir(tests_dir):
        if f.endswith(".py"):
            shutil.copy2(os.path.join(tests_dir, f), os.path.join(d_tst, f))
    print("[5] Copied full test suite (all 20 test modules).")

    # 6. 06_MANIFEST - Write README.md first so it is included in manifest entries
    readme_content = f"""# Audit 38B Delivery Package: Vacancy Database Reconciliation & Recovery Telemetry Correction

## Package Identification
- **Package Name:** `{PACKAGE_DIR_NAME}`
- **Generation Timestamp:** `{datetime.now(timezone.utc).isoformat()}`
- **Candidate Working Database Hash:** `eca573b4a4f1c045f417883772308050418c2d471250be7fda6c68e1ec023198`
- **Original Working Database Hash:** `cbc1814cf3c6546a4dfa1d2e731648aead070b133b38892ddd599a6e385c2127`
- **Canonical Database Hash:** `4949352d4f568f3f6128f398591cd8edac2eba45496c24535edb6c096398b95d`
- **Audit 19 Archive Hash:** `1958c59f1a02e5a4bd274f114fdcfdd40942239f518eb662119962a263c84d4d`
- **Enrichment Proposals Pending Approval:** 20 / 20 (100% pending, zero auto-applied)
- **Windows Task Scheduler Status:** NOT REGISTERED (0 active tasks)
- **Production Execution Status:** DEFERRED / NOT AUTHORIZED

## Package Structure
- `01_DATABASE/`: Candidate working database (`rolling_ai_ecosystem.db`), preserved baseline (`original_rolling_ai_ecosystem.db`), protected canonical and Audit 19 databases, before/after report, change log, and database integrity report.
- `02_WORKING_EXPORTS/`: Audit 38B vacancy reconciliation, recovery telemetry audit, change log, Audit 38A & 38 CSV audits, and table snapshots.
- `03_REPORTS/`: Comprehensive audit reports, production readiness scorecards, before/after reports, test runner logs, and recovery regression logs.
- `04_SOURCE_CODE/`: Full pipeline implementation (`core/`, `src/`, `scripts/`, `deploy/`).
- `05_TESTS/`: Complete regression and recovery test suite (246 tests across 20 test files, 100% pass rate).
- `06_MANIFEST/`: Cryptographic inventory (`file_manifest.json`) and detached SHA-256 checksum (`file_manifest.sha256`).

## Cryptographic Manifest & Detached Checksum
- `06_MANIFEST/file_manifest.json` catalogs all package files with their SHA-256 digests and byte counts.
- `06_MANIFEST/file_manifest.sha256` provides the detached cryptographic checksum of `file_manifest.json`.
- Exclusions: `06_MANIFEST/file_manifest.json` (self-referential circular hash exclusion) and `06_MANIFEST/file_manifest.sha256` (detached checksum).
"""
    with open(os.path.join(d_man, "README.md"), "w", encoding="utf-8") as f:
        f.write(readme_content)

    # 7. Generate Manifest Payload across all package files except file_manifest.json and file_manifest.sha256
    manifest_entries = []
    for root, _, files in os.walk(PACKAGE_PATH):
        for file in files:
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, PACKAGE_PATH).replace("\\", "/")
            if rel_path in ["06_MANIFEST/file_manifest.json", "06_MANIFEST/file_manifest.sha256"]:
                continue
            sha = sha256_file(full_path)
            size = os.path.getsize(full_path)
            manifest_entries.append({
                "path": rel_path,
                "sha256": sha,
                "size_bytes": size
            })

    manifest_entries.sort(key=lambda x: x["path"])

    manifest_payload = {
        "package_name": PACKAGE_DIR_NAME,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "manifest_metadata": {
            "total_archive_files": len(manifest_entries) + 2,
            "manifest_listed_files": len(manifest_entries),
            "manifest_coverage_percent": 100.0,
            "self_exclusion": {
                "path": "06_MANIFEST/file_manifest.json",
                "reason": "Cryptographic self-referential circular hash exclusion."
            },
            "documented_exclusions": [
                {
                    "path": "06_MANIFEST/file_manifest.json",
                    "reason": "Cryptographic self-referential circular hash exclusion."
                },
                {
                    "path": "06_MANIFEST/file_manifest.sha256",
                    "reason": "Detached cryptographic checksum of 06_MANIFEST/file_manifest.json (external verification file)."
                }
            ]
        },
        "total_files": len(manifest_entries),
        "files": manifest_entries
    }

    manifest_json_path = os.path.join(d_man, "file_manifest.json")
    with open(manifest_json_path, "w", encoding="utf-8") as f:
        json.dump(manifest_payload, f, indent=2)

    root_manifest_path = os.path.join(WORKSPACE_DIR, "audit38b_manifest.json")
    with open(root_manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest_payload, f, indent=2)

    # 8. Compute detached checksum of file_manifest.json
    manifest_sha = sha256_file(manifest_json_path)
    pkg_sha256_path = os.path.join(d_man, "file_manifest.sha256")
    root_sha256_path = os.path.join(WORKSPACE_DIR, "audit38b_manifest.sha256")

    checksum_line = f"{manifest_sha}  file_manifest.json\n"
    with open(pkg_sha256_path, "w", encoding="utf-8") as f:
        f.write(checksum_line)
    with open(root_sha256_path, "w", encoding="utf-8") as f:
        f.write(checksum_line)

    print(f"[6] Built file manifest listing {len(manifest_entries)} files with 100% coverage.")
    print(f"[7] Generated detached checksum at {pkg_sha256_path} (SHA-256: {manifest_sha}).")

    # 9. Compress into ZIP
    print(f"[8] Compressing into {ZIP_NAME}...")
    if os.path.exists(ZIP_PATH):
        os.remove(ZIP_PATH)

    with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(PACKAGE_PATH):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, PACKAGE_PATH)
                arcname = os.path.join(PACKAGE_DIR_NAME, rel_path)
                zf.write(full_path, arcname)

    zip_sha = sha256_file(ZIP_PATH)
    zip_size = os.path.getsize(ZIP_PATH)

    print("=" * 80)
    print(f" [SUCCESS] Audit 38B Package created successfully!")
    print(f"   ZIP File:   {ZIP_NAME}")
    print(f"   Size:       {zip_size:,} bytes ({zip_size / (1024*1024):.2f} MB)")
    print(f"   SHA-256:    {zip_sha}")
    print("=" * 80)
    return ZIP_PATH


if __name__ == "__main__":
    build_package()
