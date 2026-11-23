"""
Verification of Trusted Baseline and Creation of Timestamped Working Backup.
Required by Section 3 of Antigravity Execution Brief:
- Original DB SHA-256: 1958c59f1a02e5a4bd274f114fdcfdd40942239f518eb662119962a263c84d4d
- Corrected DB SHA-256: 4949352d4f568f3f6128f398591cd8edac2eba45496c24535edb6c096398b95d
- Canonical table records: startups=1307, products=1316, papers=1060, news=1132, jobs=1930 (Total=6,745)
- Historical Audit 19 log rows: 366
"""

import os
import sys
import sqlite3
import hashlib
import shutil
from datetime import datetime, timezone

ORIG_DB = "source/audit19_original_database.db"
CORR_DB = "reports/audit26_corrected.db"
ACTIVE_DB = "data/normalized/ai_ecosystem.db"

EXPECTED_ORIG_SHA = "1958c59f1a02e5a4bd274f114fdcfdd40942239f518eb662119962a263c84d4d"
EXPECTED_CORR_SHA = "4949352d4f568f3f6128f398591cd8edac2eba45496c24535edb6c096398b95d"

EXPECTED_CANONICAL = {
    "ai_startups": 1307,
    "ai_products": 1316,
    "ai_research_papers": 1060,
    "ai_news": 1132,
    "ai_jobs": 1930
}


def main():
    print("=" * 80)
    print("   STAGE 3 GEMINI ENRICHMENT: TRUSTED BASELINE VERIFICATION & BACKUP")
    print("=" * 80)

    # 1. Verify Original Database
    assert os.path.exists(ORIG_DB), f"Original DB {ORIG_DB} not found!"
    orig_sha = hashlib.sha256(open(ORIG_DB, 'rb').read()).hexdigest()
    print(f"[1] Original Database ({ORIG_DB}):")
    print(f"    Actual SHA-256:   {orig_sha}")
    print(f"    Expected SHA-256: {EXPECTED_ORIG_SHA}")
    if orig_sha != EXPECTED_ORIG_SHA:
        print(">>> STOP: Original database SHA-256 verification failed! <<<")
        sys.exit(1)
    print("    -> PASS (Exact Match)")

    # 2. Verify Corrected Database
    assert os.path.exists(CORR_DB), f"Corrected DB {CORR_DB} not found!"
    corr_sha = hashlib.sha256(open(CORR_DB, 'rb').read()).hexdigest()
    print(f"\n[2] Corrected Database ({CORR_DB}):")
    print(f"    Actual SHA-256:   {corr_sha}")
    print(f"    Expected SHA-256: {EXPECTED_CORR_SHA}")
    if corr_sha != EXPECTED_CORR_SHA:
        print(">>> STOP: Corrected database SHA-256 verification failed! <<<")
        sys.exit(1)
    print("    -> PASS (Exact Match)")

    # Also verify active database matches corrected database
    active_sha = hashlib.sha256(open(ACTIVE_DB, 'rb').read()).hexdigest()
    print(f"\n[3] Active Database ({ACTIVE_DB}):")
    print(f"    Actual SHA-256:   {active_sha}")
    assert active_sha == EXPECTED_CORR_SHA, "Active DB does not match corrected baseline!"
    print("    -> PASS (Matches Corrected Baseline)")

    # 4. Verify Canonical Record Counts
    conn = sqlite3.connect(ACTIVE_DB)
    cur = conn.cursor()
    print("\n[4] Canonical Baseline Verification (6,745 Records):")
    total_canonical = 0
    for tbl, exp_cnt in EXPECTED_CANONICAL.items():
        cur.execute(f"SELECT COUNT(*) FROM {tbl}")
        actual_cnt = cur.fetchone()[0]
        print(f"    {tbl:22s}: {actual_cnt:5d} (expected {exp_cnt:5d})")
        assert actual_cnt == exp_cnt, f"Count mismatch in {tbl}: {actual_cnt} != {exp_cnt}"
        total_canonical += actual_cnt
    print(f"    {'TOTAL CANONICAL':22s}: {total_canonical:5d} (expected 6745)")
    assert total_canonical == 6745, "Total canonical record count mismatch!"
    print("    -> PASS (All 6,745 Canonical Records Intact)")

    # 5. Verify Historical Audit 19 Log Rows
    cur.execute("SELECT COUNT(*) FROM audit19_enrichment_audit_log_archive")
    arch_cnt = cur.fetchone()[0]
    print(f"\n[5] Historical Audit 19 Archive Rows: {arch_cnt} (expected 366)")
    assert arch_cnt == 366, f"Expected 366 archive rows, got {arch_cnt}"
    print("    -> PASS (Exact 366 Rows Preserved)")

    # PRAGMA integrity_check
    cur.execute("PRAGMA integrity_check")
    ic = cur.fetchone()[0]
    print(f"\n[6] SQLite PRAGMA integrity_check: {ic}")
    assert ic == "ok", f"Integrity check failed: {ic}"
    print("    -> PASS (Integrity OK)")
    conn.close()

    # 6. Create Timestamped Working Backup
    ts_str = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    backup_dir = os.path.abspath(f"data/backups/pre_gemini_{ts_str}")
    os.makedirs(backup_dir, exist_ok=True)
    backup_db_path = os.path.join(backup_dir, "ai_ecosystem_backup.db")
    shutil.copy2(ACTIVE_DB, backup_db_path)
    backup_sha = hashlib.sha256(open(backup_db_path, 'rb').read()).hexdigest()
    print(f"\n[7] Created Timestamped Working Backup:")
    print(f"    Backup Directory: {backup_dir}")
    print(f"    Backup Database:  {backup_db_path}")
    print(f"    Backup SHA-256:   {backup_sha}")
    assert backup_sha == EXPECTED_CORR_SHA, "Backup file corrupted!"
    print("    -> PASS (Backup Verified)")

    print("\n" + "=" * 80)
    print("   ALL BASELINE VERIFICATIONS PASSED — READY FOR GEMINI INTEGRATION")
    print("=" * 80)


if __name__ == "__main__":
    main()
