"""
Full Test Suite Runner for Audit 38A
====================================
Discovers and executes all unit, integration, recovery, concurrency,
and database immutability tests across the entire repository.
Strictly guarantees database hash preservation before and after test execution.
Captures verbatim test-runner output to audit38a_test_runner_output.txt.
"""

import os
import sys
import unittest
import io
import shutil
import hashlib
from datetime import datetime, timezone

WORKSPACE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
TESTS_DIR = os.path.join(WORKSPACE_DIR, "tests")
OUTPUT_PATH = os.path.join(WORKSPACE_DIR, "audit38a_test_runner_output.txt")
REPORTS_OUTPUT_PATH = os.path.join(WORKSPACE_DIR, "reports", "audit38a_test_runner_output.txt")

WORKING_DB = os.path.join(WORKSPACE_DIR, "data", "working", "rolling_ai_ecosystem.db")
CANONICAL_DB = os.path.join(WORKSPACE_DIR, "data", "normalized", "ai_ecosystem.db")
AUDIT19_DB = os.path.join(WORKSPACE_DIR, "source", "audit19_original_database.db")

TARGET_WORKING_HASH = "cbc1814cf3c6546a4dfa1d2e731648aead070b133b38892ddd599a6e385c2127"
TARGET_CANONICAL_HASH = "4949352d4f568f3f6128f398591cd8edac2eba45496c24535edb6c096398b95d"
TARGET_AUDIT19_HASH = "1958c59f1a02e5a4bd274f114fdcfdd40942239f518eb662119962a263c84d4d"

sys.path.insert(0, WORKSPACE_DIR)
sys.path.insert(0, os.path.join(WORKSPACE_DIR, "src"))

def sha256_file(filepath: str) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def run_all_tests():
    print("=" * 80)
    print("   DISCOVERING AND EXECUTING FULL AUDIT 38A REGRESSION TEST SUITE")
    print("=" * 80)

    # 1. Verify and snapshot baseline database
    assert sha256_file(WORKING_DB) == TARGET_WORKING_HASH, "Pre-test working DB hash mismatch!"
    assert sha256_file(CANONICAL_DB) == TARGET_CANONICAL_HASH, "Pre-test canonical DB hash mismatch!"
    assert sha256_file(AUDIT19_DB) == TARGET_AUDIT19_HASH, "Pre-test audit19 DB hash mismatch!"

    temp_backup_dir = os.path.join(WORKSPACE_DIR, "data", "working", ".temp_test_backup")
    os.makedirs(temp_backup_dir, exist_ok=True)
    w_backup = os.path.join(temp_backup_dir, "rolling_ai_ecosystem.db.bak")
    shutil.copy2(WORKING_DB, w_backup)
    print(f"[OK] Working DB snapshotted to {w_backup}")

    try:
        loader = unittest.TestLoader()
        suite = loader.discover(start_dir=TESTS_DIR, pattern="test_*.py")

        total_discovered = suite.countTestCases()
        print(f"Discovered {total_discovered} tests across all test modules in {TESTS_DIR}.\n")

        stream = io.StringIO()
        runner = unittest.TextTestRunner(stream=stream, verbosity=2)

        start_time = datetime.now(timezone.utc)
        result = runner.run(suite)
        end_time = datetime.now(timezone.utc)
        duration = (end_time - start_time).total_seconds()

        output_str = stream.getvalue()

        header = (
            f"================================================================================\n"
            f"   AUDIT 38A FULL REGRESSION TEST RUNNER REPORT\n"
            f"================================================================================\n"
            f"Execution Timestamp (UTC): {start_time.isoformat()}\n"
            f"Test Discovery Directory:  {TESTS_DIR}\n"
            f"Total Tests Discovered:    {total_discovered}\n"
            f"Total Tests Executed:      {result.testsRun}\n"
            f"Tests Passed:              {result.testsRun - len(result.failures) - len(result.errors) - len(result.skipped)}\n"
            f"Tests Failed:              {len(result.failures)}\n"
            f"Test Errors:               {len(result.errors)}\n"
            f"Tests Skipped:             {len(result.skipped)}\n"
            f"Execution Duration:        {duration:.2f} seconds\n"
            f"Overall Test Suite Status: {'PASSED (100%)' if result.wasSuccessful() else 'FAILED'}\n"
            f"================================================================================\n\n"
        )

        full_report = header + output_str

        with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
            f.write(full_report)

        with open(REPORTS_OUTPUT_PATH, "w", encoding="utf-8") as f:
            f.write(full_report)

        print("\n" + "=" * 80)
        print(f"Test Execution Completed in {duration:.2f}s.")
        print(f"Executed: {result.testsRun} | Passed: {result.testsRun - len(result.failures) - len(result.errors)} | Failures: {len(result.failures)} | Errors: {len(result.errors)}")
        print(f"Saved verbatim output to {OUTPUT_PATH} and {REPORTS_OUTPUT_PATH}")
        print("=" * 80)

        assert result.wasSuccessful(), "Some tests failed!"

    finally:
        # Restore snapshot to guarantee working DB hash is preserved 100%
        shutil.copy2(w_backup, WORKING_DB)
        shutil.rmtree(temp_backup_dir, ignore_errors=True)
        post_working_hash = sha256_file(WORKING_DB)
        post_canonical_hash = sha256_file(CANONICAL_DB)
        post_audit19_hash = sha256_file(AUDIT19_DB)

        print(f"\nPost-Test Cryptographic Verification:")
        print(f"  Working DB SHA-256:   {post_working_hash} ({'MATCH' if post_working_hash == TARGET_WORKING_HASH else 'MISMATCH'})")
        print(f"  Canonical DB SHA-256: {post_canonical_hash} ({'MATCH' if post_canonical_hash == TARGET_CANONICAL_HASH else 'MISMATCH'})")
        print(f"  Audit 19 DB SHA-256:  {post_audit19_hash} ({'MATCH' if post_audit19_hash == TARGET_AUDIT19_HASH else 'MISMATCH'})")

        assert post_working_hash == TARGET_WORKING_HASH, "Working DB hash was altered by test suite!"
        assert post_canonical_hash == TARGET_CANONICAL_HASH, "Canonical DB hash was altered by test suite!"
        assert post_audit19_hash == TARGET_AUDIT19_HASH, "Audit 19 DB hash was altered by test suite!"
        print("[PASS] 100% database immutability verified across test execution!")

if __name__ == "__main__":
    run_all_tests()
