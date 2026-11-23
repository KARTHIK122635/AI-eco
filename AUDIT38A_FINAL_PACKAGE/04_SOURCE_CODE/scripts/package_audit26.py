"""
Audit 26 Packaging Script.
Builds the complete AUDIT_26_INDEPENDENT_REVIEW_PACKAGE folder and AUDIT_26_INDEPENDENT_REVIEW_PACKAGE.zip.
"""

import os
import shutil
import zipfile
import hashlib
import json
import csv
from datetime import datetime, timezone

PKG_DIR = "AUDIT_26_INDEPENDENT_REVIEW_PACKAGE"
ZIP_NAME = "AUDIT_26_INDEPENDENT_REVIEW_PACKAGE.zip"


def main():
    print("=== PACKAGING AUDIT 26 INDEPENDENT REVIEW PACKAGE ===")

    if os.path.exists(PKG_DIR):
        shutil.rmtree(PKG_DIR)
    os.makedirs(PKG_DIR, exist_ok=True)

    # 1. Structure folders
    folders = [
        "01_SOURCE_CODE",
        "02_DATABASES",
        "02_DATABASES/database_backups",
        "03_ENRICHMENT_OUTPUTS",
        "04_HISTORY_AND_RECOVERY",
        "04_HISTORY_AND_RECOVERY/historical_table_exports",
        "05_AUDIT_REPORTS",
        "06_VERIFICATION",
        "core",
        "core/enrichment",
        "core/enrichment/entity_enrichers",
        "core/llm",
        "core/llm/providers",
        "data",
        "data/normalized",
        "deliverables_audit22",
        "reports",
        "scripts",
        "source",
        "tests"
    ]
    for f in folders:
        os.makedirs(os.path.join(PKG_DIR, f), exist_ok=True)

    # Copy 01_SOURCE_CODE
    shutil.copytree("core", os.path.join(PKG_DIR, "01_SOURCE_CODE/core"), dirs_exist_ok=True)
    shutil.copytree("scripts", os.path.join(PKG_DIR, "01_SOURCE_CODE/scripts"), dirs_exist_ok=True)
    shutil.copytree("tests", os.path.join(PKG_DIR, "01_SOURCE_CODE/tests"), dirs_exist_ok=True)
    if os.path.exists("requirements.txt"):
        shutil.copy2("requirements.txt", os.path.join(PKG_DIR, "01_SOURCE_CODE/requirements.txt"))
        shutil.copy2("requirements.txt", os.path.join(PKG_DIR, "requirements.txt"))

    # Copy Runnable root files
    shutil.copytree("core", os.path.join(PKG_DIR, "core"), dirs_exist_ok=True)
    shutil.copytree("scripts", os.path.join(PKG_DIR, "scripts"), dirs_exist_ok=True)
    shutil.copytree("tests", os.path.join(PKG_DIR, "tests"), dirs_exist_ok=True)

    # Copy databases
    shutil.copy2("deliverables_audit22/ai_ecosystem.db", os.path.join(PKG_DIR, "deliverables_audit22/ai_ecosystem.db"))
    shutil.copy2("deliverables_audit22/ai_ecosystem.db", os.path.join(PKG_DIR, "02_DATABASES/audit22_submitted.db"))

    shutil.copy2("source/audit19_original_database.db", os.path.join(PKG_DIR, "source/audit19_original_database.db"))
    shutil.copy2("source/audit19_original_database.db", os.path.join(PKG_DIR, "02_DATABASES/audit19_original_database.db"))
    shutil.copy2("source/audit19_original_database.db", os.path.join(PKG_DIR, "02_DATABASES/audit19_original_baseline.db"))

    shutil.copy2("data/normalized/ai_ecosystem.db", os.path.join(PKG_DIR, "data/normalized/ai_ecosystem.db"))
    shutil.copy2("reports/audit26_corrected.db", os.path.join(PKG_DIR, "02_DATABASES/audit26_corrected.db"))
    shutil.copy2("reports/audit26_corrected.db", os.path.join(PKG_DIR, "reports/audit26_corrected.db"))

    shutil.copy2("reports/audit19_recovery_source_bundle.zip", os.path.join(PKG_DIR, "02_DATABASES/audit19_recovery_source_bundle.zip"))
    shutil.copy2("reports/audit19_recovery_source_bundle.zip", os.path.join(PKG_DIR, "reports/audit19_recovery_source_bundle.zip"))

    # Copy backup tables
    audit25_backups = "AUDIT_25_INDEPENDENT_REVIEW_PACKAGE/02_DATABASES/database_backups"
    if os.path.exists(audit25_backups):
        for f in os.listdir(audit25_backups):
            shutil.copy2(os.path.join(audit25_backups, f), os.path.join(PKG_DIR, "02_DATABASES/database_backups", f))
            shutil.copy2(os.path.join(audit25_backups, f), os.path.join(PKG_DIR, "04_HISTORY_AND_RECOVERY/historical_table_exports", f))

    # Copy 03_ENRICHMENT_OUTPUTS
    for rep in [
        "stage3_enrichment_results.jsonl",
        "stage3_review_queue.csv",
        "stage3_enrichment_summary.json",
        "stage3_provider_usage.json",
        "stage3_validation_report.md",
        "stage3_enrichment_report.md"
    ]:
        if os.path.exists(f"reports/{rep}"):
            shutil.copy2(f"reports/{rep}", os.path.join(PKG_DIR, f"03_ENRICHMENT_OUTPUTS/{rep}"))
            shutil.copy2(f"reports/{rep}", os.path.join(PKG_DIR, f"reports/{rep}"))

    # Copy 04_HISTORY_AND_RECOVERY
    for hist in [
        "audit19_original_366_records.json",
        "audit19_to_audit23_reconciliation.csv",
        "history_preservation_report.md",
        "audit19_original_baseline.db"
    ]:
        if os.path.exists(f"reports/{hist}"):
            shutil.copy2(f"reports/{hist}", os.path.join(PKG_DIR, f"04_HISTORY_AND_RECOVERY/{hist}"))
            shutil.copy2(f"reports/{hist}", os.path.join(PKG_DIR, f"reports/{hist}"))

    if os.path.exists("AUDIT_25_INDEPENDENT_REVIEW_PACKAGE/04_HISTORY_AND_RECOVERY/all_attempt_ids.csv"):
        shutil.copy2("AUDIT_25_INDEPENDENT_REVIEW_PACKAGE/04_HISTORY_AND_RECOVERY/all_attempt_ids.csv", os.path.join(PKG_DIR, "04_HISTORY_AND_RECOVERY/all_attempt_ids.csv"))

    # Copy 05_AUDIT_REPORTS
    for audit_rep in [
        "audit26_remediation_report.md",
        "audit26_database_hash_report.md",
        "audit26_verifier_output.txt",
        "audit26_test_output.txt",
        "audit26_negative_test_output.txt"
    ]:
        if os.path.exists(f"reports/{audit_rep}"):
            shutil.copy2(f"reports/{audit_rep}", os.path.join(PKG_DIR, f"05_AUDIT_REPORTS/{audit_rep}"))
            shutil.copy2(f"reports/{audit_rep}", os.path.join(PKG_DIR, f"reports/{audit_rep}"))

    # Copy 06_VERIFICATION
    shutil.copy2("scripts/verify_audit26_stage3.py", os.path.join(PKG_DIR, "06_VERIFICATION/verify_audit26_stage3.py"))
    shutil.copy2("scripts/run_audit26_negative_tests.py", os.path.join(PKG_DIR, "06_VERIFICATION/run_audit26_negative_tests.py"))
    shutil.copy2("reports/stage3_file_manifest.json", os.path.join(PKG_DIR, "06_VERIFICATION/stage3_file_manifest.json"))
    shutil.copy2("reports/audit26_file_manifest.json", os.path.join(PKG_DIR, "06_VERIFICATION/audit26_file_manifest.json"))
    shutil.copy2("reports/stage3_file_manifest.json", os.path.join(PKG_DIR, "reports/stage3_file_manifest.json"))
    shutil.copy2("reports/audit26_file_manifest.json", os.path.join(PKG_DIR, "reports/audit26_file_manifest.json"))

    # Write README_AUDIT26.md
    readme_content = """# Phase II — Stage 3: Audit 26 Independent Review Package
## Final Historical Authenticity Correction & Hardened Independent Verification

### Executive Overview
This package resolves the remaining critical finding from Audit 25: restoring the authentic original Audit 19 database directly from `audit19_recovery_source_bundle.zip` without programmatic reconstruction, and hardcoding strict cryptographic hash verification into Check 2.

### Authenticity Verification
- **Original Audit 19 Database**: `source/audit19_original_database.db`
  - SHA-256: `1958c59f1a02e5a4bd274f114fdcfdd40942239f518eb662119962a263c84d4d`
  - File Size: `20,770,816` bytes
  - Rows: `366` | Unique Keys: `366` | Columns: `13`
  - NULL counts: `original_value`: 0 (354 empty strings), `enriched_value`: 0 (50 empty strings)
  - Timestamps: Authentic UTC timestamps preserved verbatim.
  - SQLite PRAGMA `integrity_check`: `ok`

### Package Directory Structure
- `01_SOURCE_CODE/`: Full runnable Python source code, schemas, and tests.
- `02_DATABASES/`:
  - `audit19_original_database.db` (SHA-256: `1958c59f...`)
  - `audit19_original_baseline.db` (SHA-256: `1958c59f...`)
  - `audit22_submitted.db` (Canonical reference: 6,745 records)
  - `audit26_corrected.db` (Active pipeline database with synchronized archive table)
  - `audit19_recovery_source_bundle.zip` (Supplied recovery bundle)
  - `database_backups/` (All 9 historical backup tables in CSV and JSON)
- `03_ENRICHMENT_OUTPUTS/`: Current Stage 3 results JSONL, review queue CSV, and summaries.
- `04_HISTORY_AND_RECOVERY/`: Historical reconciliation CSV (390 rows) and original JSON records.
- `05_AUDIT_REPORTS/`: Remediation report, hash report, verifier output, test outputs.
- `06_VERIFICATION/`: Independent verifier, negative test runner, and cryptographic manifests.
- Root directory contains complete runnable project copy.

### Verification Commands
```bash
# 1. Run all 18 independent verification checks
python scripts/verify_audit26_stage3.py

# 2. Run all 6 negative authenticity tests
python scripts/run_audit26_negative_tests.py

# 3. Run complete unit test suite (114 tests)
python -m unittest discover -s tests -p "test_*.py"
```
"""
    with open(os.path.join(PKG_DIR, "README_AUDIT26.md"), "w", encoding="utf-8") as f:
        f.write(readme_content)

    # Generate complete inventory
    inventory = []
    for root, dirs, files in os.walk(PKG_DIR):
        for f in files:
            p = os.path.join(root, f)
            rel = os.path.relpath(p, PKG_DIR).replace("\\", "/")
            sz = os.path.getsize(p)
            h = hashlib.sha256()
            with open(p, "rb") as fh:
                while chunk := fh.read(65536):
                    h.update(chunk)
            inventory.append({
                "file_path": rel,
                "size_bytes": sz,
                "sha256": h.hexdigest()
            })

    inventory.sort(key=lambda x: x["file_path"])

    inv_csv = os.path.join(PKG_DIR, "submission_inventory.csv")
    with open(inv_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["file_path", "size_bytes", "sha256"])
        writer.writeheader()
        writer.writerows(inventory)

    inv_txt = os.path.join(PKG_DIR, "reports/audit26_file_inventory.txt")
    with open(inv_txt, "w", encoding="utf-8") as f:
        for item in inventory:
            f.write(f"{item['file_path']} | {item['size_bytes']} bytes | {item['sha256']}\n")

    shutil.copy2(inv_txt, "reports/audit26_file_inventory.txt")
    shutil.copy2(inv_csv, "submission_inventory.csv")

    print(f"Generated submission inventory with {len(inventory)} files.")

    # 2. Build ZIP
    if os.path.exists(ZIP_NAME):
        os.remove(ZIP_NAME)

    print(f"Creating {ZIP_NAME}...")
    with zipfile.ZipFile(ZIP_NAME, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(PKG_DIR):
            for f in files:
                p = os.path.join(root, f)
                arcname = os.path.relpath(p, ".")
                zf.write(p, arcname)

    zip_sz = os.path.getsize(ZIP_NAME)
    zip_h = hashlib.sha256(open(ZIP_NAME, "rb").read()).hexdigest()
    print(f"Successfully created {ZIP_NAME} ({zip_sz / (1024*1024):.2f} MB). SHA-256: {zip_h}")
    print("=== PACKAGING COMPLETED SUCCESSFULLY ===")


if __name__ == "__main__":
    main()
