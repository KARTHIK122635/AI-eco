"""
Unit test suite for Audit 26 Negative Authenticity Checks.
"""

import os
import sys
import unittest
import shutil
import sqlite3
import zipfile
import subprocess
import hashlib

def find_path(candidates):
    for c in candidates:
        if os.path.exists(c):
            return os.path.abspath(c)
    return os.path.abspath(candidates[0])

VERIFIER_SCRIPT = find_path(["scripts/verify_audit26_stage3.py", "../scripts/verify_audit26_stage3.py", "07_VERIFICATION/verify_audit26_stage3.py"])
SOURCE_DB = find_path(["source/audit19_original_database.db", "03_DATABASE/source_audit19_original_database.db", "03_DATABASE/audit19_original_database.db"])
AUDIT25_REF_DB = find_path(["AUDIT_25_INDEPENDENT_REVIEW_PACKAGE/02_DATABASES/audit19_original_database.db", "02_DATABASES/audit19_original_database.db"])
EXPECTED_SHA = "1958c59f1a02e5a4bd274f114fdcfdd40942239f518eb662119962a263c84d4d"


def run_verifier(audit19_db: str = None, recovery_zip: str = None):
    cmd = [sys.executable, VERIFIER_SCRIPT, "--check-2-only"]
    if audit19_db:
        cmd.extend(["--audit19-db", audit19_db])
    if recovery_zip:
        cmd.extend(["--recovery-zip", recovery_zip])
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return res.returncode, res.stdout, res.stderr


class TestAudit26Authenticity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp_dir = os.path.abspath("temp_unittest_negative")
        os.makedirs(cls.temp_dir, exist_ok=True)
        cls.base_db = SOURCE_DB

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.temp_dir, ignore_errors=True)

    def test_1_authentic_database_passes(self):
        """Test 1: Authentic original database must PASS with exit code 0."""
        rc, out, err = run_verifier(audit19_db=self.base_db)
        self.assertEqual(rc, 0, f"Authentic database should pass Check 2:\n{out}")
        self.assertIn("PASS", out)

    def test_2_audit25_reconstructed_fails(self):
        """Test 2: Audit 25 reconstructed database (4ba9b11f...) must FAIL with nonzero code."""
        audit25_db = os.path.join(self.temp_dir, "audit25_reconstructed.db")
        if os.path.exists(AUDIT25_REF_DB):
            shutil.copy2(AUDIT25_REF_DB, audit25_db)
        else:
            shutil.copy2(self.base_db, audit25_db)
            conn = sqlite3.connect(audit25_db)
            conn.execute("UPDATE enrichment_audit_log SET enriched_at = '2026-11-21T20:12:31.756070+00:00'")
            conn.commit()
            conn.close()

        rc, out, err = run_verifier(audit19_db=audit25_db)
        self.assertNotEqual(rc, 0, "Audit 25 reconstructed database should fail Check 2")
        self.assertIn("FAIL", out)

    def test_3_modified_timestamp_fails(self):
        """Test 3: Database with modified timestamp must FAIL with nonzero code."""
        mod_ts_db = os.path.join(self.temp_dir, "mod_ts.db")
        shutil.copy2(self.base_db, mod_ts_db)
        conn = sqlite3.connect(mod_ts_db)
        conn.execute("UPDATE enrichment_audit_log SET enriched_at = '2026-01-01T00:00:00+00:00' WHERE rowid = (SELECT rowid FROM enrichment_audit_log LIMIT 1)")
        conn.commit()
        conn.close()
        rc, out, err = run_verifier(audit19_db=mod_ts_db)
        self.assertNotEqual(rc, 0, "Modified timestamp should fail Check 2")
        self.assertIn("FAIL", out)

    def test_4_changed_value_fails(self):
        """Test 4: Database with changed value must FAIL with nonzero code."""
        mod_val_db = os.path.join(self.temp_dir, "mod_val.db")
        shutil.copy2(self.base_db, mod_val_db)
        conn = sqlite3.connect(mod_val_db)
        conn.execute("UPDATE enrichment_audit_log SET enriched_value = 'TAMPERED_VAL' WHERE rowid = (SELECT rowid FROM enrichment_audit_log LIMIT 1)")
        conn.commit()
        conn.close()
        rc, out, err = run_verifier(audit19_db=mod_val_db)
        self.assertNotEqual(rc, 0, "Modified value should fail Check 2")
        self.assertIn("FAIL", out)

    def test_5_missing_row_fails(self):
        """Test 5: Database with missing row (365 rows) must FAIL with nonzero code."""
        missing_row_db = os.path.join(self.temp_dir, "missing_row.db")
        shutil.copy2(self.base_db, missing_row_db)
        conn = sqlite3.connect(missing_row_db)
        conn.execute("DELETE FROM enrichment_audit_log WHERE rowid = (SELECT rowid FROM enrichment_audit_log LIMIT 1)")
        conn.commit()
        conn.close()
        rc, out, err = run_verifier(audit19_db=missing_row_db)
        self.assertNotEqual(rc, 0, "Missing row should fail Check 2")
        self.assertIn("FAIL", out)

    def test_6_modified_recovery_zip_fails(self):
        """Test 6: Database with modified recovery ZIP must FAIL with nonzero code."""
        corrupt_zip = os.path.join(self.temp_dir, "corrupt_recovery.zip")
        with zipfile.ZipFile(corrupt_zip, 'w') as zf:
            zf.writestr("audit19_original_database.db", b"CORRUPTED_FAKE_DATABASE_BYTES")
        rc, out, err = run_verifier(audit19_db=self.base_db, recovery_zip=corrupt_zip)
        self.assertNotEqual(rc, 0, "Modified recovery zip should fail Check 2")
        self.assertIn("FAIL", out)


if __name__ == "__main__":
    unittest.main()
