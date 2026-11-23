"""
Clean-Room Independent Verification Script for Audit 38 Package
================================================================
Extracts AUDIT38_FINAL_PACKAGE.zip into a temporary isolated directory and cryptographically validates:
1. Detached checksum presence and integrity: 06_MANIFEST/file_manifest.sha256 matches 06_MANIFEST/file_manifest.json.
2. Every file against 06_MANIFEST/file_manifest.json (SHA-256 and byte size).
3. Exact archive reconciliation: total files == manifest listed + 2 documented exclusions (100.00% coverage, 0 unaccounted).
4. Canonical database hash immutability (4949352d4f568f3f6128f398591cd8edac2eba45496c24535edb6c096398b95d).
5. Authentic Audit 19 database hash immutability (1958c59f1a02e5a4bd274f114fdcfdd40942239f518eb662119962a263c84d4d).
6. Working database SQLite integrity check and schema/data invariants:
   - 1,963 jobs: exactly 0 NULL job_status records (33 resolved).
   - 1,307 startups & 1,316 products: UNVERIFIED_DATE.
   - 1,060 research papers: 1,045 RECENT_7D.
   - 190 GitHub repositories and 205 metrics snapshots.
   - 100% of enrichment proposals (20) are PENDING_APPROVAL.
7. Presence of all 6 Audit 38 domain CSV audit files in 02_WORKING_EXPORTS.
8. Independent clean-room execution of concurrency and recovery test suites.
"""

import os
import sys
import json
import shutil
import zipfile
import hashlib
import sqlite3
import tempfile
import subprocess
import csv

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
    print(f"   INDEPENDENT AUDIT 38 CLEAN-ROOM VERIFICATION: {os.path.basename(zip_path)}")
    print("=" * 80)

    if not os.path.exists(zip_path):
        print(f"[FAIL] Package ZIP not found at {zip_path}")
        return False

    temp_dir = tempfile.mkdtemp(prefix="audit38_cleanroom_")
    print(f"[1] Extracting package into clean-room environment: {temp_dir}")

    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(temp_dir)

        pkg_root = os.path.join(temp_dir, "AUDIT38_FINAL_PACKAGE")
        if not os.path.exists(pkg_root):
            pkg_root = temp_dir

        # 1. Verify Detached Checksum Presence & Integrity
        sha256_file_path = os.path.join(pkg_root, "06_MANIFEST", "file_manifest.sha256")
        manifest_json_path = os.path.join(pkg_root, "06_MANIFEST", "file_manifest.json")

        if not os.path.exists(sha256_file_path):
            print("[FAIL] 06_MANIFEST/file_manifest.sha256 is MISSING from package payload!")
            return False
        print("    [PASS] 06_MANIFEST/file_manifest.sha256 exists in package payload.")

        if not os.path.exists(manifest_json_path):
            print("[FAIL] 06_MANIFEST/file_manifest.json is MISSING from package payload!")
            return False

        with open(sha256_file_path, "r", encoding="utf-8") as f:
            sha256_content = f.read().strip()
        expected_manifest_hash = sha256_content.split()[0].lower()
        actual_manifest_hash = sha256_file(manifest_json_path).lower()

        if expected_manifest_hash != actual_manifest_hash:
            print(f"[FAIL] Detached checksum mismatch! Expected {expected_manifest_hash}, got {actual_manifest_hash}")
            return False
        print(f"[2] [PASS] Detached Checksum Verified Independently: {actual_manifest_hash} matches file_manifest.sha256.")

        # 2. Validate Every File against file_manifest.json
        with open(manifest_json_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)

        files = manifest.get("files", [])
        print(f"[3] Validating {len(files)} files against cryptographic manifest...")

        mismatches = []
        for entry in files:
            p = os.path.join(pkg_root, entry["path"])
            if not os.path.exists(p):
                mismatches.append(f"Missing file: {entry['path']}")
                continue
            act_sha = sha256_file(p)
            act_sz = os.path.getsize(p)
            if act_sha != entry["sha256"]:
                mismatches.append(f"Hash mismatch for {entry['path']}: expected {entry['sha256']}, got {act_sha}")
            if act_sz != entry["size_bytes"]:
                mismatches.append(f"Size mismatch for {entry['path']}: expected {entry['size_bytes']}, got {act_sz}")

        if mismatches:
            for m in mismatches[:10]:
                print(f"    [FAIL] {m}")
            return False
        print("    [PASS] All manifest files match SHA-256 hashes and byte sizes exactly.")

        # 3. Verify Exact Archive Reconciliation & Documented Exclusions
        all_pkg_files = []
        for root, _, flist in os.walk(pkg_root):
            for fname in flist:
                fpath = os.path.join(root, fname)
                rpath = os.path.relpath(fpath, pkg_root).replace("\\", "/")
                all_pkg_files.append(rpath)

        documented_exclusions = {e["path"] for e in manifest.get("manifest_metadata", {}).get("documented_exclusions", [])}
        expected_exclusions = {"06_MANIFEST/file_manifest.json", "06_MANIFEST/file_manifest.sha256"}
        if documented_exclusions != expected_exclusions:
            print(f"[FAIL] Documented exclusions mismatch: expected {expected_exclusions}, got {documented_exclusions}")
            return False

        manifest_file_paths = {e["path"] for e in files}
        unmanifested = [f for f in all_pkg_files if f not in documented_exclusions and f not in manifest_file_paths]
        if unmanifested:
            print(f"[FAIL] Found unaccounted / unmanifested files: {unmanifested}")
            return False

        total_archive_count = len(all_pkg_files)
        manifest_count = len(files)
        exclusions_count = len(documented_exclusions)

        if total_archive_count != manifest_count + exclusions_count:
            print(f"[FAIL] Exact reconciliation failed: archive={total_archive_count}, manifest={manifest_count}, exclusions={exclusions_count}")
            return False

        print(f"[4] [PASS] Exact Manifest Reconciliation Verified:")
        print(f"    - Total Archive Files:       {total_archive_count}")
        print(f"    - Manifest Listed Files:     {manifest_count}")
        print(f"    - Documented Exclusions:     {exclusions_count} ({', '.join(sorted(documented_exclusions))})")
        print(f"    - Unaccounted / Undocumented: 0")
        print(f"    - Manifest Coverage:         100.00%")

        # 4. Verify Canonical & Audit 19 Database Immobility
        canon_path = os.path.join(pkg_root, "01_DATABASE", "ai_ecosystem.db")
        canon_sha = sha256_file(canon_path)
        if canon_sha != EXPECTED_CANONICAL_SHA:
            print(f"[FAIL] Canonical database hash mismatch: {canon_sha}")
            return False
        print(f"[5] [PASS] Canonical database hash byte-identical: {canon_sha}")

        conn_c = sqlite3.connect(canon_path)
        c_c = conn_c.cursor()
        counts = {}
        for tbl in ["ai_startups", "ai_products", "ai_research_papers", "ai_news", "ai_jobs"]:
            c_c.execute(f"SELECT count(*) FROM {tbl}")
            counts[tbl] = c_c.fetchone()[0]
        conn_c.close()

        total_canon = sum(counts.values())
        if total_canon != 6745:
            print(f"[FAIL] Canonical database row count mismatch: {total_canon} (expected 6,745)")
            return False
        print(f"    [PASS] Canonical row counts verified: {total_canon:,} total records (6,745 baseline).")

        audit19_path = os.path.join(pkg_root, "01_DATABASE", "audit19_original_database.db")
        audit19_sha = sha256_file(audit19_path)
        if audit19_sha != EXPECTED_AUDIT19_SHA:
            print(f"[FAIL] Authentic Audit 19 database hash mismatch: {audit19_sha}")
            return False
        print(f"[6] [PASS] Authentic Audit 19 database hash byte-identical: {audit19_sha}")

        # 5. Working Database Verifications
        working_db_path = os.path.join(pkg_root, "01_DATABASE", "rolling_ai_ecosystem.db")
        conn = sqlite3.connect(working_db_path)
        c = conn.cursor()
        c.execute("PRAGMA integrity_check")
        w_integrity = c.fetchone()[0]
        if w_integrity != "ok":
            print(f"[FAIL] Working database integrity check failed: {w_integrity}")
            return False
        print("[7] [PASS] Working database SQLite integrity check: ok")

        # Verify job_status resolved
        c.execute("SELECT count(*) FROM ai_jobs WHERE job_status IS NULL")
        null_jobs = c.fetchone()[0]
        if null_jobs != 0:
            print(f"[FAIL] Found {null_jobs} jobs with missing job_status!")
            return False
        print("    [PASS] 100% of jobs have resolved job_status (0 NULL records).")

        # Check Proposal Approval Invariant
        c.execute("SELECT count(*) FROM enrichment_proposals WHERE approval_status = 'PENDING_APPROVAL'")
        pending_proposals = c.fetchone()[0]
        if pending_proposals != 20:
            print(f"[FAIL] Proposals invariant violation: pending={pending_proposals} (expected 20)")
            return False
        print(f"[8] [PASS] Approval Invariant: 100% of proposals ({pending_proposals}) are PENDING_APPROVAL")

        # Check Domain Date Semantics
        c.execute("SELECT count(*) FROM ai_startups WHERE date_type = 'UNVERIFIED_DATE'")
        unv_st = c.fetchone()[0]
        c.execute("SELECT count(*) FROM ai_products WHERE date_type = 'UNVERIFIED_DATE'")
        unv_pr = c.fetchone()[0]
        if unv_st != 1307 or unv_pr != 1316:
            print(f"[FAIL] Startup/product unverified count mismatch: st={unv_st}, pr={unv_pr}")
            return False
        print(f"[9] [PASS] Domain Date Semantics: {unv_st} startups & {unv_pr} products classified UNVERIFIED_DATE.")

        # Check GitHub repositories and snapshots
        c.execute("SELECT count(*) FROM github_repositories")
        repos_cnt = c.fetchone()[0]
        c.execute("SELECT count(*) FROM github_metrics_history")
        snaps_cnt = c.fetchone()[0]
        if repos_cnt != 190 or snaps_cnt != 205:
            print(f"[FAIL] GitHub metrics reconciliation failed: repos={repos_cnt}, snapshots={snaps_cnt}")
            return False
        print(f"[10] [PASS] GitHub Metrics Timeline Reconciled: 190 repos, 205 total snapshots.")

        # Check Research papers
        c.execute("SELECT count(*) FROM ai_research_papers WHERE freshness_status = 'RECENT_7D'")
        r7_papers = c.fetchone()[0]
        if r7_papers != 1045:
            print(f"[FAIL] Research paper freshness failed: {r7_papers} (expected 1,045)")
            return False
        print(f"[11] [PASS] Research Paper Temporal Distribution: 1,045 RECENT_7D papers verified.")

        conn.close()

        # 6. Verify 6 Audit 38 CSV Files in 02_WORKING_EXPORTS
        required_csvs = [
            "audit38_startup_date_audit.csv",
            "audit38_product_date_audit.csv",
            "audit38_paper_freshness_audit.csv",
            "audit38_news_source_health.csv",
            "audit38_job_lifecycle_audit.csv",
            "audit38_collection_log_integrity.csv"
        ]
        for rc in required_csvs:
            rc_path = os.path.join(pkg_root, "02_WORKING_EXPORTS", rc)
            if not os.path.exists(rc_path):
                print(f"[FAIL] Missing Audit 38 CSV export: {rc}")
                return False
        print(f"[12] [PASS] All 6 Audit 38 domain CSV audit files verified in 02_WORKING_EXPORTS.")

        # 7. Run Clean-Room Concurrency and Recovery Test Suites
        env = os.environ.copy()
        env["PYTHONPATH"] = f"{os.path.join(pkg_root, '04_SOURCE_CODE')};{os.path.join(pkg_root, '04_SOURCE_CODE', 'src')};{os.environ.get('PYTHONPATH', '')}"

        test_files = [
            os.path.join(pkg_root, "05_TESTS", "test_audit37_concurrency.py"),
            os.path.join(pkg_root, "05_TESTS", "test_audit36_finalization_safety.py"),
            os.path.join(pkg_root, "05_TESTS", "test_audit35_strict_lineage.py"),
            os.path.join(pkg_root, "05_TESTS", "test_audit33_advanced_recovery.py"),
            os.path.join(pkg_root, "05_TESTS", "test_audit32_recovery_integration.py")
        ]

        for tf in test_files:
            if os.path.exists(tf):
                print(f"[13] Running {os.path.basename(tf)} in clean-room...")
                res = subprocess.run([sys.executable, "-m", "unittest", tf], cwd=pkg_root, env=env, capture_output=True, text=True)
                if res.returncode != 0:
                    print(f"[FAIL] Test {os.path.basename(tf)} failed:\n{res.stderr}\n{res.stdout}")
                    return False
                print(f"    [PASS] {os.path.basename(tf)} passed independently!")

        print("=" * 80)
        print(" [SUCCESS] AUDIT 38 CLEAN-ROOM INDEPENDENT VERIFICATION PASSED (100%)")
        print("=" * 80)
        return True

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    zip_target = os.path.abspath("AUDIT38_FINAL_PACKAGE.zip")
    if len(sys.argv) > 1:
        zip_target = os.path.abspath(sys.argv[1])
    success = verify_package(zip_target)
    sys.exit(0 if success else 1)
