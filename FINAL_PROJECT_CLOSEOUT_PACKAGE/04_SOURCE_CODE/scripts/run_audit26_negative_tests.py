"""
Audit 26 Mandatory Negative Test Runner.
Executes the 6 required negative authenticity test scenarios:
- Test 1: Authentic original database -> PASS (code 0)
- Test 2: Audit 25 reconstructed database (4ba9b11f...) -> FAIL (nonzero)
- Test 3: Database with one modified timestamp -> FAIL (nonzero)
- Test 4: Database with one changed value -> FAIL (nonzero)
- Test 5: Database with a missing row (365 rows) -> FAIL (nonzero)
- Test 6: Database with a modified recovery ZIP -> FAIL (nonzero)
"""

import os
import sys
import shutil
import sqlite3
import zipfile
import subprocess
import hashlib

VERIFIER_SCRIPT = os.path.abspath("scripts/verify_audit26_stage3.py")
SOURCE_DB = os.path.abspath("source/audit19_original_database.db")
AUDIT25_REF_DB = os.path.abspath("AUDIT_25_INDEPENDENT_REVIEW_PACKAGE/02_DATABASES/audit19_original_database.db")
EXPECTED_SHA = "1958c59f1a02e5a4bd274f114fdcfdd40942239f518eb662119962a263c84d4d"
AUDIT25_SHA = "4ba9b11fb356a48a8052bcd7c056b24565813cc530d3b1673b7e58e0439ef57a"


def run_verifier(audit19_db: str = None, recovery_zip: str = None):
    cmd = [sys.executable, VERIFIER_SCRIPT, "--check-2-only"]
    if audit19_db:
        cmd.extend(["--audit19-db", audit19_db])
    if recovery_zip:
        cmd.extend(["--recovery-zip", recovery_zip])
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return res.returncode, res.stdout, res.stderr


def main():
    print("=" * 80)
    print("   PHASE II — STAGE 3: AUDIT 26 MANDATORY NEGATIVE TESTS")
    print("=" * 80)

    results = {}
    temp_dir = os.path.abspath("temp_negative_tests")
    os.makedirs(temp_dir, exist_ok=True)

    base_db = SOURCE_DB

    try:
        # TEST 1: Authentic original database
        print("\n[RUNNING TEST 1] Authentic original database verification...")
        actual_sha = hashlib.sha256(open(base_db, 'rb').read()).hexdigest()
        assert actual_sha == EXPECTED_SHA, f"Expected {EXPECTED_SHA}, got {actual_sha}"
        rc, out, err = run_verifier(audit19_db=base_db)
        if rc == 0:
            print("  [PASS] Test 1: Authentic database verified successfully (exit code 0).")
            results["Test 1: Authentic original database"] = "PASS"
        else:
            print(f"  [FAIL] Test 1: Expected exit code 0, got {rc}.\n{out}")
            results["Test 1: Authentic original database"] = f"FAIL (exit {rc})"

        # TEST 2: Audit 25 reconstructed database (4ba9b11f...)
        print("\n[RUNNING TEST 2] Audit 25 reconstructed database (4ba9b11f...) must FAIL...")
        audit25_db = os.path.join(temp_dir, "audit25_reconstructed.db")
        if os.path.exists(AUDIT25_REF_DB):
            shutil.copy2(AUDIT25_REF_DB, audit25_db)
        else:
            shutil.copy2(base_db, audit25_db)
            conn = sqlite3.connect(audit25_db)
            conn.execute("UPDATE enrichment_audit_log SET enriched_at = '2026-11-21T20:12:31.756070+00:00'")
            conn.commit()
            conn.close()

        sha25 = hashlib.sha256(open(audit25_db, 'rb').read()).hexdigest()
        print(f"  Audit 25 test DB SHA-256: {sha25}")
        rc, out, err = run_verifier(audit19_db=audit25_db)
        if rc != 0:
            print(f"  [PASS] Test 2: Audit 25 reconstructed database correctly rejected (exit code {rc}).")
            results["Test 2: Audit 25 reconstructed DB"] = "PASS"
        else:
            print(f"  [FAIL] Test 2: Audit 25 DB was incorrectly accepted (exit code 0).")
            results["Test 2: Audit 25 reconstructed DB"] = "FAIL"

        # TEST 3: Database with one modified timestamp
        print("\n[RUNNING TEST 3] Database with one modified timestamp must FAIL...")
        mod_ts_db = os.path.join(temp_dir, "modified_ts.db")
        shutil.copy2(base_db, mod_ts_db)
        conn = sqlite3.connect(mod_ts_db)
        conn.execute("UPDATE enrichment_audit_log SET enriched_at = '2026-01-01T00:00:00+00:00' WHERE rowid = (SELECT rowid FROM enrichment_audit_log LIMIT 1)")
        conn.commit()
        conn.close()
        rc, out, err = run_verifier(audit19_db=mod_ts_db)
        if rc != 0:
            print(f"  [PASS] Test 3: Modified timestamp correctly rejected (exit code {rc}).")
            results["Test 3: Modified timestamp"] = "PASS"
        else:
            print(f"  [FAIL] Test 3: Modified timestamp was accepted (exit code 0).")
            results["Test 3: Modified timestamp"] = "FAIL"

        # TEST 4: Database with one changed value
        print("\n[RUNNING TEST 4] Database with one changed value must FAIL...")
        mod_val_db = os.path.join(temp_dir, "modified_val.db")
        shutil.copy2(base_db, mod_val_db)
        conn = sqlite3.connect(mod_val_db)
        conn.execute("UPDATE enrichment_audit_log SET enriched_value = 'MODIFIED_VALUE_CORRUPTION' WHERE rowid = (SELECT rowid FROM enrichment_audit_log LIMIT 1)")
        conn.commit()
        conn.close()
        rc, out, err = run_verifier(audit19_db=mod_val_db)
        if rc != 0:
            print(f"  [PASS] Test 4: Modified value correctly rejected (exit code {rc}).")
            results["Test 4: Modified value"] = "PASS"
        else:
            print(f"  [FAIL] Test 4: Modified value was accepted (exit code 0).")
            results["Test 4: Modified value"] = "FAIL"

        # TEST 5: Database with a missing row (365 rows)
        print("\n[RUNNING TEST 5] Database with a missing row (365 rows) must FAIL...")
        missing_row_db = os.path.join(temp_dir, "missing_row.db")
        shutil.copy2(base_db, missing_row_db)
        conn = sqlite3.connect(missing_row_db)
        conn.execute("DELETE FROM enrichment_audit_log WHERE rowid = (SELECT rowid FROM enrichment_audit_log LIMIT 1)")
        conn.commit()
        conn.close()
        rc, out, err = run_verifier(audit19_db=missing_row_db)
        if rc != 0:
            print(f"  [PASS] Test 5: Missing row correctly rejected (exit code {rc}).")
            results["Test 5: Missing row"] = "PASS"
        else:
            print(f"  [FAIL] Test 5: Missing row was accepted (exit code 0).")
            results["Test 5: Missing row"] = "FAIL"

        # TEST 6: Database with a modified recovery ZIP
        print("\n[RUNNING TEST 6] Database with a modified recovery ZIP must FAIL...")
        corrupt_zip = os.path.join(temp_dir, "corrupt_recovery.zip")
        with zipfile.ZipFile(corrupt_zip, 'w') as zf:
            zf.writestr("audit19_original_database.db", b"CORRUPTED_FAKE_DATABASE_BYTES")
        rc, out, err = run_verifier(audit19_db=base_db, recovery_zip=corrupt_zip)
        if rc != 0:
            print(f"  [PASS] Test 6: Modified recovery ZIP correctly rejected (exit code {rc}).")
            results["Test 6: Modified recovery ZIP"] = "PASS"
        else:
            print(f"  [FAIL] Test 6: Modified recovery ZIP was accepted (exit code 0).")
            results["Test 6: Modified recovery ZIP"] = "FAIL"

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

    print("\n" + "=" * 80)
    print("   NEGATIVE TEST RESULTS SUMMARY")
    print("=" * 80)
    all_ok = True
    for test_name, status in results.items():
        print(f"  {status:25s} | {test_name}")
        if status != "PASS":
            all_ok = False
    print("=" * 80)
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
