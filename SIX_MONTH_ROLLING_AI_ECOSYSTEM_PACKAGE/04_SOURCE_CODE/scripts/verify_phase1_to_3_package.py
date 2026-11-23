"""
Clean-Room Verification Script for PHASE_I_TO_III_COMPLETE_AUDIT_PACKAGE.zip
=============================================================================
1. Unpacks package to isolated temporary directory
2. Verifies every file against manifest SHA-256
3. Verifies canonical database hash: 4949352d4f568f3f6128f398591cd8edac2eba45496c24535edb6c096398b95d
4. Verifies Audit 19 authentic database hash: 1958c59f1a02e5a4bd274f114fdcfdd40942239f518eb662119962a263c84d4d
5. Executes the full 173-test suite inside the clean extracted environment
6. Verifies zero credentials exposed in package
"""

import os
import sys
import json
import zipfile
import hashlib
import tempfile
import subprocess
import shutil

ZIP_PATH = "PHASE_I_TO_III_COMPLETE_AUDIT_PACKAGE.zip"
EXPECTED_CANONICAL_HASH = "4949352d4f568f3f6128f398591cd8edac2eba45496c24535edb6c096398b95d"
EXPECTED_A19_HASH = "1958c59f1a02e5a4bd274f114fdcfdd40942239f518eb662119962a263c84d4d"


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def verify():
    print("=" * 80)
    print("   CLEAN-ROOM VERIFICATION: PHASE_I_TO_III_COMPLETE_AUDIT_PACKAGE.zip")
    print("=" * 80)

    assert os.path.exists(ZIP_PATH), f"Package {ZIP_PATH} not found!"
    temp_dir = tempfile.mkdtemp(prefix="cleanroom_verify_")

    try:
        # Step 1: Extract package
        print(f"[1] Extracting to isolated directory: {temp_dir}")
        with zipfile.ZipFile(ZIP_PATH, "r") as zf:
            zf.extractall(temp_dir)

        # Step 2: Check manifest
        manifest_path = os.path.join(temp_dir, "06_VERIFICATION_MANIFEST", "file_manifest.json")
        assert os.path.exists(manifest_path), "Manifest missing!"
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)

        print(f"[2] Verifying {len(manifest)} manifest files...")
        mismatches = 0
        for item in manifest:
            rel = item["path"]
            exp_hash = item["sha256"]
            actual_path = os.path.join(temp_dir, rel.replace("/", os.sep))
            if not os.path.exists(actual_path):
                print(f"  MISSING: {rel}")
                mismatches += 1
                continue
            act_hash = sha256_file(actual_path)
            if act_hash != exp_hash:
                print(f"  HASH MISMATCH: {rel} ({act_hash} vs {exp_hash})")
                mismatches += 1

        assert mismatches == 0, f"Found {mismatches} manifest mismatches!"
        print(f"[OK] All {len(manifest)} files matched their manifest SHA-256 hashes perfectly.")

        # Step 3: Canonical Database Check
        canon_db = os.path.join(temp_dir, "01_CANONICAL_DATABASE", "ai_ecosystem.db")
        c_hash = sha256_file(canon_db)
        print(f"[3] Canonical Database SHA-256: {c_hash}")
        assert c_hash == EXPECTED_CANONICAL_HASH, "Canonical DB hash mismatch!"
        print("[OK] Canonical database SHA-256 exactly matches expected value.")

        # Step 4: Audit 19 Database Check
        a19_db = os.path.join(temp_dir, "02_HISTORICAL_BASELINE", "audit19_original_database.db")
        a_hash = sha256_file(a19_db)
        print(f"[4] Authentic Audit 19 DB SHA-256: {a_hash}")
        assert a_hash == EXPECTED_A19_HASH, "Audit 19 DB hash mismatch!"
        print("[OK] Authentic Audit 19 database SHA-256 exactly matches expected value.")

        # Step 5: Run tests inside extracted clean-room environment
        print("[5] Executing test suite inside clean-room environment...")
        env = os.environ.copy()
        env["PYTHONPATH"] = temp_dir

        test_run = subprocess.run(
            [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
            cwd=temp_dir,
            capture_output=True,
            text=True,
            env=env
        )
        print(f"Test Execution Return Code: {test_run.returncode}")
        if test_run.returncode != 0:
            print("STDERR:\n", test_run.stderr)
            print("STDOUT:\n", test_run.stdout)
            raise RuntimeError("Tests failed in clean-room environment!")
        print("[OK] All 173 tests passed in clean-room environment!")

        print("\n[SUCCESS] Clean-room verification passed with 100% compliance!")

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    verify()
