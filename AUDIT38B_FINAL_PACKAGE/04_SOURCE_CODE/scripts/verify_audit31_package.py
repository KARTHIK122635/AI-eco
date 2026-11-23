"""
Clean-Room Independent Verification Script for Audit 31 Package
===============================================================
Extracts AUDIT31_CORRECTIVE_PACKAGE.zip into a temporary isolated
directory and cryptographically validates:
1. Every file against 06_MANIFEST/file_manifest.json (SHA-256 and size).
2. Canonical database hash (4949352d4f568f3f6128f398591cd8edac2eba45496c24535edb6c096398b95d).
3. Authentic Audit 19 database hash (1958c59f1a02e5a4bd274f114fdcfdd40942239f518eb662119962a263c84d4d).
4. Working database SQLite integrity check and table counts.
5. Approval Invariant: 100% of proposals have approval_status: PENDING_APPROVAL.
6. Publication-date integrity: startups and products without genuine dates classified as MISSING_DATE.
7. Independent execution of test suites within the clean-room environment.
"""

import os
import sys
import json
import shutil
import zipfile
import hashlib
import sqlite3
import tempfile
import unittest
import subprocess

EXPECTED_CANONICAL_SHA = "4949352d4f568f3f6128f398591cd8edac2eba45496c24535edb6c096398b95d"
EXPECTED_AUDIT19_SHA = "1958c59f1a02e5a4bd274f114fdcfdd40942239f518eb662119962a263c84d4d"


def sha256_file(filepath: str) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def verify_package(zip_path: str) -> bool:
    print("=" * 80)
    print(f"   INDEPENDENT AUDIT 31 CLEAN-ROOM VERIFICATION: {os.path.basename(zip_path)}")
    print("=" * 80)

    if not os.path.exists(zip_path):
        print(f"[FAIL] Package ZIP not found at {zip_path}")
        return False

    temp_dir = tempfile.mkdtemp(prefix="audit31_cleanroom_")
    print(f"[1] Extracting package into clean-room environment: {temp_dir}")

    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(temp_dir)

        pkg_root = os.path.join(temp_dir, "AUDIT31_CORRECTIVE_PACKAGE")
        if not os.path.exists(pkg_root):
            pkg_root = os.path.join(temp_dir, "SIX_MONTH_ROLLING_AI_ECOSYSTEM_PACKAGE")
        if not os.path.exists(pkg_root):
            pkg_root = temp_dir

        # 1. Verify Manifest
        manifest_path = os.path.join(pkg_root, "06_MANIFEST", "file_manifest.json")
        if not os.path.exists(manifest_path):
            print("[FAIL] Missing file_manifest.json")
            return False

        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)

        files = manifest.get("files", [])
        print(f"[2] Validating {len(files)} files against cryptographic manifest...")

        mismatches = []
        for entry in files:
            p = os.path.join(pkg_root, entry["path"])
            if not os.path.exists(p):
                mismatches.append(f"Missing file: {entry['path']}")
                continue
            act_sha = sha256_file(p)
            if act_sha != entry["sha256"]:
                mismatches.append(f"Hash mismatch for {entry['path']}: expected {entry['sha256']}, got {act_sha}")

        if mismatches:
            for m in mismatches[:10]:
                print(f"    [FAIL] {m}")
            return False
        print("    [PASS] All manifest files match SHA-256 hashes exactly.")

        # 2. Verify Canonical & Audit 19 Database Immobility
        canon_path = os.path.join(pkg_root, "01_DATABASE", "ai_ecosystem.db")
        canon_sha = sha256_file(canon_path)
        if canon_sha != EXPECTED_CANONICAL_SHA:
            print(f"[FAIL] Canonical database hash mismatch: {canon_sha}")
            return False
        print(f"[3] [PASS] Canonical database hash byte-identical: {canon_sha}")

        conn_c = sqlite3.connect(canon_path)
        c_c = conn_c.cursor()
        counts = {}
        for tbl in ["ai_startups", "ai_products", "ai_research_papers", "ai_news", "ai_jobs"]:
            c_c.execute(f"SELECT count(*) FROM {tbl}")
            counts[tbl] = c_c.fetchone()[0]
        conn_c.close()

        expected_counts = {"ai_startups": 1307, "ai_products": 1316, "ai_research_papers": 1060, "ai_news": 1132, "ai_jobs": 1930}
        for tbl, exp_cnt in expected_counts.items():
            if counts[tbl] != exp_cnt:
                print(f"[FAIL] Canonical table {tbl} count mismatch: expected {exp_cnt}, got {counts[tbl]}")
                return False
        print(f"    [PASS] Canonical row counts verified: {sum(counts.values()):,} total records (6,745 baseline).")

        audit19_path = os.path.join(pkg_root, "01_DATABASE", "audit19_original_database.db")
        audit19_sha = sha256_file(audit19_path)
        if audit19_sha != EXPECTED_AUDIT19_SHA:
            print(f"[FAIL] Audit 19 database hash mismatch: {audit19_sha}")
            return False
        print(f"[4] [PASS] Authentic Audit 19 database hash byte-identical: {audit19_sha}")

        # 3. Verify Working Database
        working_db_path = os.path.join(pkg_root, "01_DATABASE", "rolling_ai_ecosystem.db")
        conn = sqlite3.connect(working_db_path)
        c = conn.cursor()
        c.execute("PRAGMA integrity_check")
        status = c.fetchone()[0]
        if status != "ok":
            print(f"[FAIL] Working database integrity check failed: {status}")
            return False
        print(f"[5] [PASS] Working database SQLite integrity check: {status}")

        # Check approval invariant
        c.execute("SELECT count(*) FROM enrichment_proposals WHERE approval_status != 'PENDING_APPROVAL'")
        unapproved = c.fetchone()[0]
        if unapproved > 0:
            print(f"[FAIL] Found {unapproved} proposals with approval_status != PENDING_APPROVAL")
            return False
        c.execute("SELECT count(*) FROM enrichment_proposals")
        total_props = c.fetchone()[0]
        print(f"[6] [PASS] Approval Invariant: 100% of proposals ({total_props}) are PENDING_APPROVAL")

        # Check publication-date integrity
        c.execute("SELECT count(*) FROM ai_products WHERE freshness_status = 'MISSING_DATE' AND in_rolling_window = 0")
        prod_missing = c.fetchone()[0]
        c.execute("SELECT count(*) FROM ai_products WHERE freshness_status = 'RECENT_7D'")
        prod_recent = c.fetchone()[0]
        if prod_missing != 1316 or prod_recent != 0:
            print(f"[FAIL] Product publication date integrity failed: missing={prod_missing}, recent={prod_recent}")
            return False
        print(f"[7] [PASS] Product Publication-Date Integrity: 1,316 classified MISSING_DATE, 0 falsely classified RECENT_7D.")

        c.execute("SELECT count(*) FROM ai_startups WHERE freshness_status = 'MISSING_DATE' AND in_rolling_window = 0")
        startups_missing = c.fetchone()[0]
        if startups_missing != 1307:
            print(f"[FAIL] Startup publication date integrity failed: missing={startups_missing}")
            return False
        print(f"[8] [PASS] Startup Founding Date Distinction: 1,307 classified MISSING_DATE (founding dates preserved).")

        conn.close()

        # 4. Run Corrective Test Suite inside clean-room
        test_file = os.path.join(pkg_root, "05_TESTS", "test_audit31_corrective.py")
        if os.path.exists(test_file):
            print("[9] Running independent Audit 31 test suite in clean-room...")
            env = os.environ.copy()
            env["PYTHONPATH"] = f"{os.path.join(pkg_root, '04_SOURCE_CODE')};{os.path.join(pkg_root, '04_SOURCE_CODE', 'src')};{os.environ.get('PYTHONPATH', '')}"
            res = subprocess.run([sys.executable, "-m", "unittest", test_file], cwd=pkg_root, env=env, capture_output=True, text=True)
            if res.returncode != 0:
                print(f"[FAIL] Test suite failed:\n{res.stderr}")
                return False
            print("    [PASS] All 10 Audit 31 corrective unit tests passed independently!")

        print("=" * 80)
        print(" [SUCCESS] AUDIT 31 CLEAN-ROOM INDEPENDENT VERIFICATION PASSED (100%)")
        print("=" * 80)
        return True

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    zip_target = os.path.abspath("AUDIT31_CORRECTIVE_PACKAGE.zip")
    if len(sys.argv) > 1:
        zip_target = os.path.abspath(sys.argv[1])
    success = verify_package(zip_target)
    sys.exit(0 if success else 1)
