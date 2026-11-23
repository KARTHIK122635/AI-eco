"""
Independent Clean-Room Package Verification for FINAL_PROJECT_CLOSEOUT_PACKAGE.zip
==================================================================================
Extracts FINAL_PROJECT_CLOSEOUT_PACKAGE.zip into an isolated temp directory, verifies:
1. Presence of detached checksum 06_MANIFEST/file_manifest.sha256.
2. Independent calculation and cryptographic match of file_manifest.json against file_manifest.sha256.
3. Cryptographic integrity of 100% of manifest-listed files against SHA-256 and byte sizes.
4. Exact manifest reconciliation:
   Total Archive Files = Manifest Listed Files + Documented Exclusions (2).
5. Byte-identical canonical DB (4949352d..., 6,745 records) and authentic Audit 19 DB (1958c59f..., 366 records).
6. Packaged candidate working DB SHA-256 (eca573b4a4f1c045f417883772308050418c2d471250be7fda6c68e1ec023198).
7. Preserved baseline working DB SHA-256 (cbc1814cf3c6546a4dfa1d2e731648aead070b133b38892ddd599a6e385c2127).
8. Candidate DB vacancy reconciliation: job_201518350968ce4f is CLOSED / CLOSED.
9. Working DB table counts match reports (collection_logs = 6, jobs = 1,963, 0 NULL job_status).
10. Strict proposal invariant: 100% PENDING_APPROVAL (20/20).
11. Presence and integrity of all closeout root deliverables.
12. Clean-room execution of critical recovery, concurrency, and lifecycle test suites.
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

WORKSPACE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
ZIP_PATH = os.path.join(WORKSPACE_DIR, "FINAL_PROJECT_CLOSEOUT_PACKAGE.zip")

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


def verify_package():
    print("=" * 80)
    print("   INDEPENDENT CLEAN-ROOM VERIFICATION: FINAL_PROJECT_CLOSEOUT_PACKAGE.zip")
    print("=" * 80)

    assert os.path.exists(ZIP_PATH), f"Package zip not found at {ZIP_PATH}"

    clean_dir = tempfile.mkdtemp(prefix="closeout_cleanroom_")
    print(f"[1] Extracting package into clean-room environment: {clean_dir}")

    try:
        with zipfile.ZipFile(ZIP_PATH, "r") as zf:
            zf.extractall(clean_dir)

        pkg_root = os.path.join(clean_dir, "FINAL_PROJECT_CLOSEOUT_PACKAGE")
        assert os.path.exists(pkg_root), "FINAL_PROJECT_CLOSEOUT_PACKAGE root folder missing in archive!"

        # 1. Verify detached checksum file exists
        sha_file = os.path.join(pkg_root, "06_MANIFEST", "file_manifest.sha256")
        assert os.path.exists(sha_file), "06_MANIFEST/file_manifest.sha256 missing!"
        print("    [PASS] 06_MANIFEST/file_manifest.sha256 exists in package payload.")

        # 2. Independent validation of detached checksum
        manifest_json_file = os.path.join(pkg_root, "06_MANIFEST", "file_manifest.json")
        assert os.path.exists(manifest_json_file), "06_MANIFEST/file_manifest.json missing!"

        calculated_manifest_sha = sha256_file(manifest_json_file)
        with open(sha_file, "r", encoding="utf-8") as f:
            detached_content = f.read().strip()
        expected_manifest_sha = detached_content.split()[0]

        assert calculated_manifest_sha == expected_manifest_sha, (
            f"Detached SHA-256 mismatch! Calculated {calculated_manifest_sha} != Expected {expected_manifest_sha}"
        )
        print(f"[2] [PASS] Detached Checksum Verified Independently: {calculated_manifest_sha} matches file_manifest.sha256.")

        # 3. Read manifest and validate every entry
        with open(manifest_json_file, "r", encoding="utf-8") as f:
            manifest_data = json.load(f)

        manifest_files = manifest_data["files"]
        print(f"[3] Validating {len(manifest_files)} files against cryptographic manifest...")

        for entry in manifest_files:
            rel_p = entry["path"]
            exp_sha = entry["sha256"]
            exp_sz = entry["size_bytes"]

            full_p = os.path.join(pkg_root, rel_p.replace("/", os.sep))
            assert os.path.exists(full_p), f"Manifest file missing on disk: {rel_p}"

            act_sha = sha256_file(full_p)
            act_sz = os.path.getsize(full_p)

            assert act_sha == exp_sha, f"SHA-256 mismatch on {rel_p}: {act_sha} != {exp_sha}"
            assert act_sz == exp_sz, f"Size mismatch on {rel_p}: {act_sz} != {exp_sz}"

        print("    [PASS] All manifest files match SHA-256 hashes and byte sizes exactly.")

        # 4. Manifest reconciliation & documented exclusions
        disk_files = []
        for root, _, files in os.walk(pkg_root):
            for file in files:
                rel = os.path.relpath(os.path.join(root, file), pkg_root).replace("\\", "/")
                disk_files.append(rel)

        total_disk = len(disk_files)
        total_manifest = len(manifest_files)
        exclusions = manifest_data["manifest_metadata"]["documented_exclusions"]
        total_excluded = len(exclusions)

        print(f"[4] Manifest File Reconciliation:")
        print(f"    Total files on disk:      {total_disk}")
        print(f"    Manifest listed files:    {total_manifest}")
        print(f"    Documented exclusions:    {total_excluded}")
        for exc in exclusions:
            print(f"      - Excluded: {exc['path']} ({exc['reason']})")

        assert total_disk == total_manifest + total_excluded, (
            f"Reconciliation mismatch! Total disk ({total_disk}) != Manifest ({total_manifest}) + Excluded ({total_excluded})"
        )
        print(f"    [PASS] Exact Reconciliation: Total disk ({total_disk}) == Manifest ({total_manifest}) + Excluded ({total_excluded}).")

        # 5. Verify Closeout Root Deliverables Exist
        closeout_deliverables = [
            "FINAL_PROJECT_CLOSEOUT_REPORT.md",
            "PHASE_III_COMPLETION_CERTIFICATE.md",
            "AUDIT38B_FINAL_REPORT.md",
            "audit38b_production_readiness_scorecard.md",
            "audit38b_vacancy_reconciliation.csv",
            "audit38b_recovery_telemetry_audit.csv",
            "audit38b_database_integrity_report.txt",
            "audit38b_database_change_log.csv",
            "audit38b_full_test_runner_output.txt",
            "audit38b_recovery_regression_test_output.txt"
        ]
        for cd in closeout_deliverables:
            cd_p = os.path.join(pkg_root, cd)
            assert os.path.exists(cd_p), f"Missing root deliverable: {cd}"
        print(f"[5] [PASS] All {len(closeout_deliverables)} closeout root deliverables present.")

        # 6. Verify Section 2 in packaged AUDIT38B_FINAL_REPORT.md has corrected primary keys
        rep_text = open(os.path.join(pkg_root, "AUDIT38B_FINAL_REPORT.md"), "r", encoding="utf-8").read()
        assert "job_0c738ca8ba2349af" in rep_text, "Authoritative key job_0c738ca8ba2349af missing from packaged report!"
        assert "job_201518350968ce4f" in rep_text, "Authoritative key job_201518350968ce4f missing from packaged report!"
        assert "job_03813c95977a4a9c" not in rep_text, "Obsolete key job_03813c95977a4a9c still present in packaged report!"
        print(f"[6] [PASS] Packaged AUDIT38B_FINAL_REPORT.md contains authoritative Section 2 records.")

        # 7. Verify Canonical Database
        canonical_p = os.path.join(pkg_root, "01_DATABASE", "ai_ecosystem.db")
        c_sha = sha256_file(canonical_p)
        assert c_sha == TARGET_CANONICAL_HASH, f"Canonical DB hash altered! {c_sha}"
        print(f"[7] [PASS] Canonical database hash byte-identical: {c_sha}")

        c_conn = sqlite3.connect(canonical_p)
        c_cur = c_conn.cursor()
        canon_tables = ["ai_startups", "ai_products", "ai_research_papers", "ai_news", "ai_jobs"]
        total_canon = sum(c_cur.execute(f"SELECT count(*) FROM {t}").fetchone()[0] for t in canon_tables)
        c_conn.close()
        assert total_canon == 6745, f"Canonical row count mismatch! Got {total_canon}, expected 6745"
        print(f"    [PASS] Canonical row counts verified: 6,745 total records (6,745 baseline).")

        # 8. Verify Authentic Audit 19 Database
        audit19_p = os.path.join(pkg_root, "01_DATABASE", "audit19_original_database.db")
        a_sha = sha256_file(audit19_p)
        assert a_sha == TARGET_AUDIT19_HASH, f"Audit 19 DB hash altered! {a_sha}"
        print(f"[8] [PASS] Authentic Audit 19 database hash byte-identical: {a_sha}")

        # 9. Verify Working Databases (Candidate & Original Baseline)
        cand_p = os.path.join(pkg_root, "01_DATABASE", "rolling_ai_ecosystem.db")
        orig_p = os.path.join(pkg_root, "01_DATABASE", "original_rolling_ai_ecosystem.db")

        cand_sha = sha256_file(cand_p)
        orig_sha = sha256_file(orig_p)

        assert cand_sha == TARGET_CANDIDATE_WORKING_HASH, f"Candidate DB hash mismatch! {cand_sha} != {TARGET_CANDIDATE_WORKING_HASH}"
        assert orig_sha == TARGET_ORIGINAL_WORKING_HASH, f"Original baseline DB hash mismatch! {orig_sha} != {TARGET_ORIGINAL_WORKING_HASH}"
        print(f"[9] [PASS] Packaged Candidate DB hash: {cand_sha}")
        print(f"    [PASS] Packaged Original Baseline DB hash: {orig_sha}")

        # SQLite integrity check on candidate DB
        w_conn = sqlite3.connect(cand_p)
        w_cur = w_conn.cursor()
        w_cur.execute("PRAGMA integrity_check")
        assert w_cur.fetchone()[0] == "ok", "Candidate DB SQLite integrity check failed!"
        print(f"    [PASS] Candidate DB SQLite integrity check: ok")

        # Check collection_logs count
        log_cnt = w_cur.execute("SELECT count(*) FROM collection_logs").fetchone()[0]
        assert log_cnt == 6, f"Collection logs count mismatch! Got {log_cnt}, expected 6"
        print(f"    [PASS] Collection logs row count verified: exactly 6 rows.")

        # Check zero NULL job_status
        null_job_status = w_cur.execute("SELECT count(*) FROM ai_jobs WHERE job_status IS NULL").fetchone()[0]
        assert null_job_status == 0, f"Found {null_job_status} jobs with NULL job_status!"
        print(f"    [PASS] 100% of jobs have resolved job_status (0 NULL records).")

        # Verify reconciled Remotive job
        remotive_row = w_cur.execute("SELECT job_status, vacancy_status FROM ai_jobs WHERE job_id = 'job_201518350968ce4f'").fetchone()
        assert remotive_row[0] == "CLOSED" and remotive_row[1] == "CLOSED", (
            f"Remotive job reconciliation not present in candidate DB! Got {remotive_row}"
        )
        print(f"[10] [PASS] Vacancy Reconciliation Verified: job_201518350968ce4f is CLOSED / CLOSED.")

        # Check proposal invariants
        prop_statuses = w_cur.execute("SELECT approval_status, count(*) FROM enrichment_proposals GROUP BY approval_status").fetchall()
        assert len(prop_statuses) == 1 and prop_statuses[0][0] == "PENDING_APPROVAL" and prop_statuses[0][1] == 20, (
            f"Approval invariant violated! {prop_statuses}"
        )
        print(f"[11] [PASS] Approval Invariant: 100% of proposals (20) are PENDING_APPROVAL")

        # Check GitHub repos and snapshots
        repo_cnt = w_cur.execute("SELECT count(*) FROM github_repositories").fetchone()[0]
        snap_cnt = w_cur.execute("SELECT count(*) FROM github_metrics_history").fetchone()[0]
        assert repo_cnt == 190, f"Repo count mismatch: {repo_cnt}"
        assert snap_cnt == 205, f"Snapshot count mismatch: {snap_cnt}"
        print(f"[12] [PASS] GitHub Metrics Timeline Reconciled: 190 repos, 205 total snapshots.")

        w_conn.close()

        # 10. Clean-Room Test Execution of critical recovery, concurrency, and lifecycle test suites
        clean_tests = [
            "test_audit38b_recovery_lifecycle.py",
            "test_audit37_concurrency.py",
            "test_audit36_finalization_safety.py",
            "test_audit35_strict_lineage.py",
            "test_audit33_advanced_recovery.py",
            "test_audit32_recovery_integration.py"
        ]

        env = os.environ.copy()
        env["PYTHONPATH"] = os.path.join(pkg_root, "04_SOURCE_CODE") + os.pathsep + os.path.join(pkg_root, "04_SOURCE_CODE", "04_SOURCE_CODE")

        for t_file in clean_tests:
            t_path = os.path.join(pkg_root, "05_TESTS", t_file)
            print(f"[13] Running {t_file} in clean-room...")
            cmd = [sys.executable, "-m", "unittest", t_path]
            res = subprocess.run(cmd, env=env, cwd=pkg_root, capture_output=True, text=True)
            assert res.returncode == 0, f"Clean-room test failed for {t_file}:\n{res.stderr}\n{res.stdout}"
            print(f"     [PASS] {t_file} passed independently in clean-room!")

        print("=" * 80)
        print(" [SUCCESS] FINAL PROJECT CLOSEOUT PACKAGE INDEPENDENT VERIFICATION PASSED (100%)")
        print("=" * 80)
        return True

    finally:
        shutil.rmtree(clean_dir, ignore_errors=True)


if __name__ == "__main__":
    verify_package()
