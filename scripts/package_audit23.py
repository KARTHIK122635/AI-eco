import os
import shutil
import hashlib
import json
import csv
import zipfile
import sqlite3
from datetime import datetime, timezone

def compute_sha256(filepath):
    h = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def package():
    base_dir = os.path.abspath('.')
    pkg_dir = os.path.join(base_dir, 'AUDIT_23_INDEPENDENT_REVIEW_PACKAGE')

    if os.path.exists(pkg_dir):
        shutil.rmtree(pkg_dir)

    # 1. Create subfolders
    subfolders = [
        '01_SOURCE_CODE',
        '01_SOURCE_CODE/core',
        '01_SOURCE_CODE/scripts',
        '01_SOURCE_CODE/tests',
        '02_DATABASES',
        '02_DATABASES/database_backups',
        '03_ENRICHMENT_OUTPUTS',
        '04_HISTORY_AND_RECOVERY',
        '04_HISTORY_AND_RECOVERY/historical_table_exports',
        '05_AUDIT_REPORTS',
        '06_VERIFICATION'
    ]
    for sf in subfolders:
        os.makedirs(os.path.join(pkg_dir, sf), exist_ok=True)

    print("Created package directory structure.")

    # 2. Copy source code
    # Copy core
    shutil.copytree(os.path.join(base_dir, 'core'), os.path.join(pkg_dir, '01_SOURCE_CODE', 'core'), dirs_exist_ok=True, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    
    # Copy scripts
    script_files = [
        'verify_audit23_stage3.py',
        'run_stage3_enrichment.py',
        'reconcile_audit19.py',
        'export_attempts.py',
        'export_historical_tables.py',
        'verify_canonical_baseline.py',
        'generate_manifest.py'
    ]
    for s in script_files:
        src = os.path.join(base_dir, 'scripts', s)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(pkg_dir, '01_SOURCE_CODE', 'scripts', s))

    # Copy tests
    shutil.copytree(os.path.join(base_dir, 'tests'), os.path.join(pkg_dir, '01_SOURCE_CODE', 'tests'), dirs_exist_ok=True, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))

    # Copy requirements.txt
    shutil.copy2(os.path.join(base_dir, 'requirements.txt'), os.path.join(pkg_dir, '01_SOURCE_CODE', 'requirements.txt'))

    # 3. Copy databases
    # audit19_original_baseline.db.MISSING.txt
    shutil.copy2(os.path.join(base_dir, 'reports', 'audit19_original_baseline.db.MISSING.txt'), os.path.join(pkg_dir, '02_DATABASES', 'audit19_original_baseline.db.MISSING.txt'))
    
    # audit22_submitted.db
    shutil.copy2(os.path.join(base_dir, 'deliverables_audit22', 'ai_ecosystem.db'), os.path.join(pkg_dir, '02_DATABASES', 'audit22_submitted.db'))

    # audit23_corrected.db
    shutil.copy2(os.path.join(base_dir, 'data', 'normalized', 'ai_ecosystem.db'), os.path.join(pkg_dir, '02_DATABASES', 'audit23_corrected.db'))

    # database backups
    hist_exp_dir = os.path.join(base_dir, 'reports', 'historical_table_exports')
    if os.path.exists(hist_exp_dir):
        for f in os.listdir(hist_exp_dir):
            shutil.copy2(os.path.join(hist_exp_dir, f), os.path.join(pkg_dir, '02_DATABASES', 'database_backups', f))

    # 4. Copy enrichment outputs
    enrichment_outputs = [
        'stage3_enrichment_results.jsonl',
        'stage3_review_queue.csv',
        'llm_review_queue.csv',
        'stage3_provider_usage.json',
        'stage3_enrichment_summary.json'
    ]
    for eo in enrichment_outputs:
        src = os.path.join(base_dir, 'reports', eo)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(pkg_dir, '03_ENRICHMENT_OUTPUTS', eo))

    # 5. Copy history and recovery
    hist_files = [
        'audit19_original_366_records.json',
        'audit19_to_audit23_reconciliation.csv',
        'all_attempt_ids.csv',
        'history_preservation_report.md'
    ]
    for hf in hist_files:
        src = os.path.join(base_dir, 'reports', hf)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(pkg_dir, '04_HISTORY_AND_RECOVERY', hf))

    if os.path.exists(hist_exp_dir):
        for f in os.listdir(hist_exp_dir):
            shutil.copy2(os.path.join(hist_exp_dir, f), os.path.join(pkg_dir, '04_HISTORY_AND_RECOVERY', 'historical_table_exports', f))

    # 6. Copy audit reports
    report_files = [
        'stage3_enrichment_report.md',
        'stage3_validation_report.md',
        'audit23_findings.md',
        'audit23_test_summary.md'
    ]
    for rf in report_files:
        src = os.path.join(base_dir, 'reports', rf)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(pkg_dir, '05_AUDIT_REPORTS', rf))

    # 7. Copy verification files
    ver_files = [
        'audit23_verification_output.txt',
        'test_output.txt',
        'stage3_file_manifest.json',
        'reproduction_commands.md'
    ]
    for vf in ver_files:
        src = os.path.join(base_dir, 'reports', vf)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(pkg_dir, '06_VERIFICATION', vf))

    # 8. Copy README_AUDIT23.md to root
    shutil.copy2(os.path.join(base_dir, 'reports', 'README_AUDIT23.md'), os.path.join(pkg_dir, 'README_AUDIT23.md'))

    # 9. Compute SHA-256 for all files in pkg_dir and generate sha256_checksums.txt and submission_inventory.csv
    file_records = []
    checksum_lines = []

    descriptions = {
        "README_AUDIT23.md": "Comprehensive Audit 23 submission documentation, architecture, and results",
        "requirements.txt": "Project dependency specification",
        "validator.py": "Strict field-level evidence validator with sentence-level context isolation",
        "schemas.py": "Enrichment dataclasses and taxonomy definitions with corrected Set/Tuple typing imports",
        "schema_validator.py": "Schema validation engine for enrichment records",
        "engine.py": "Multi-table orchestration and persistence pipeline engine",
        "verify_audit23_stage3.py": "Standalone 14-check independent audit verification script",
        "run_stage3_enrichment.py": "Stage 3 LLM fallback and enrichment runner CLI",
        "reconcile_audit19.py": "Script generating 366-record Audit 19 reconciliation",
        "export_attempts.py": "Historical attempt ID aggregator script",
        "export_historical_tables.py": "Row-by-row historical table exporter",
        "verify_canonical_baseline.py": "Canonical dataset immutability verifier",
        "generate_manifest.py": "Cryptographic file manifest generator",
        "audit19_original_baseline.db.MISSING.txt": "Technical limitation report explaining Audit 20 overwrite of Audit 19 database",
        "audit22_submitted.db": "Exact SQLite database submitted in Audit 22",
        "audit23_corrected.db": "Corrected Audit 23 SQLite database with 6,745 canonical records and Stage 3 tables",
        "stage3_enrichment_results.jsonl": "37 Stage 3 validated enrichment records",
        "stage3_review_queue.csv": "37 queued records requiring human review",
        "llm_review_queue.csv": "Mirrored CSV of review queue records",
        "stage3_provider_usage.json": "Provider token usage report (0 tokens, $0.00 cost)",
        "stage3_enrichment_summary.json": "Stage 3 pipeline execution summary JSON",
        "audit19_original_366_records.json": "Structured JSON reconciliation of all 366 original Audit 19 records",
        "audit19_to_audit23_reconciliation.csv": "Row-by-row recovery status CSV for Audit 19 through Audit 23 (390 rows)",
        "all_attempt_ids.csv": "Inventory of all 169 historical unique attempt IDs across all runs",
        "history_preservation_report.md": "Multi-table preservation audit report with row-by-row comparisons",
        "stage3_enrichment_report.md": "Stage 3 enrichment metrics and distribution report",
        "stage3_validation_report.md": "Stage 3 evidence validation report",
        "audit23_findings.md": "Technical findings and remediation report for Audit 22 review findings",
        "audit23_test_summary.md": "Complete test suite execution summary (88/88 passing)",
        "audit23_verification_output.txt": "Execution log from verify_audit23_stage3.py (14/14 checks PASS)",
        "test_output.txt": "Execution log from python -m unittest discover tests -v (88 tests PASS)",
        "stage3_file_manifest.json": "Cryptographic file manifest of tracked Stage 3 deliverables",
        "reproduction_commands.md": "Exact CLI instructions for independent reproduction"
    }

    for root, dirs, files in os.walk(pkg_dir):
        for f in files:
            full_path = os.path.join(root, f)
            rel_path = os.path.relpath(full_path, pkg_dir).replace('\\', '/')
            if rel_path in ['sha256_checksums.txt', 'submission_inventory.csv', '06_VERIFICATION/sha256_checksums.txt']:
                continue
            sz = os.path.getsize(full_path)
            sha = compute_sha256(full_path)

            desc = descriptions.get(f, f"Component file: {f}")
            file_records.append({
                "relative_path": rel_path,
                "file_size_bytes": sz,
                "sha256_hash": sha,
                "description": desc
            })
            checksum_lines.append(f"{sha}  {rel_path}")

    # Write sha256_checksums.txt in 06_VERIFICATION
    sha_path = os.path.join(pkg_dir, '06_VERIFICATION', 'sha256_checksums.txt')
    with open(sha_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(sorted(checksum_lines)) + "\n")

    # Add sha256_checksums.txt itself to inventory
    sha_sz = os.path.getsize(sha_path)
    sha_hash = compute_sha256(sha_path)
    file_records.append({
        "relative_path": "06_VERIFICATION/sha256_checksums.txt",
        "file_size_bytes": sha_sz,
        "sha256_hash": sha_hash,
        "description": "Full 64-character SHA-256 checksums of all package artifacts"
    })

    # Write submission_inventory.csv in root of pkg_dir
    inv_path = os.path.join(pkg_dir, 'submission_inventory.csv')
    with open(inv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["relative_path", "file_size_bytes", "sha256_hash", "description"])
        writer.writeheader()
        for rec in sorted(file_records, key=lambda x: x["relative_path"]):
            writer.writerow(rec)

    print(f"Inventoried {len(file_records)} files into submission_inventory.csv and sha256_checksums.txt.")

    # 10. Create ZIP archive
    zip_path = os.path.join(base_dir, 'AUDIT_23_INDEPENDENT_REVIEW_PACKAGE.zip')
    if os.path.exists(zip_path):
        os.remove(zip_path)

    print("Creating ZIP archive...")
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(pkg_dir):
            for file in files:
                abs_file = os.path.join(root, file)
                arcname = os.path.relpath(abs_file, base_dir)
                zipf.write(abs_file, arcname)

    zip_size = os.path.getsize(zip_path)
    zip_sha256 = compute_sha256(zip_path)

    print(f"\nZIP Archive Created:")
    print(f"  Path:        {zip_path}")
    print(f"  Size:        {zip_size:,} bytes ({zip_size / (1024*1024):.2f} MB)")
    print(f"  SHA-256:     {zip_sha256}")

    # 11. Test ZIP Extraction
    test_extract_dir = os.path.join(base_dir, 'reports', 'test_zip_extract')
    if os.path.exists(test_extract_dir):
        shutil.rmtree(test_extract_dir)
    os.makedirs(test_extract_dir, exist_ok=True)

    print("\nTesting ZIP extraction integrity...")
    with zipfile.ZipFile(zip_path, 'r') as zipf:
        entries = zipf.namelist()
        zipf.extractall(test_extract_dir)
        print(f"  Extracted entries: {len(entries)}")

    # Check for empty files
    empty_files = []
    for root, dirs, files in os.walk(test_extract_dir):
        for f in files:
            p = os.path.join(root, f)
            if os.path.getsize(p) == 0:
                empty_files.append(os.path.relpath(p, test_extract_dir))

    print(f"  Empty files found: {len(empty_files)} ({empty_files if empty_files else 'None'})")
    assert len(empty_files) == 0, f"Empty files found: {empty_files}"

    # Verify extracted audit23_corrected.db integrity
    ext_db = os.path.join(test_extract_dir, 'AUDIT_23_INDEPENDENT_REVIEW_PACKAGE', '02_DATABASES', 'audit23_corrected.db')
    conn = sqlite3.connect(ext_db)
    cur = conn.cursor()
    cur.execute("PRAGMA integrity_check")
    integ = cur.fetchone()[0]
    cur.execute("SELECT count(*) FROM ai_jobs")
    jobs_cnt = cur.fetchone()[0]
    conn.close()

    print(f"  Extracted DB integrity: {integ}, jobs count: {jobs_cnt}")
    assert integ == "ok"
    assert jobs_cnt == 1930

    shutil.rmtree(test_extract_dir)
    print("Test extraction verified successfully. Cleanup complete.")

    return {
        "zip_path": zip_path,
        "zip_size_bytes": zip_size,
        "zip_sha256": zip_sha256,
        "entries_count": len(entries)
    }

if __name__ == '__main__':
    package()
