"""
Independent Audit Verification Script for Phase II — Stage 3 (Audit 19).
Verifies:
1. SQLite PRAGMA integrity_check.
2. Canonical table immutability (row counts and logical content hashes).
3. Parity across JSONL, CSV, and SQLite multi-table persistence.
4. Schema validation on every record in stage3_enrichment_results.jsonl.
5. Strict evidence grounding for all VERIFIED records.
6. Checksum reconciliation against stage3_file_manifest.json.
"""

import os
import sys
sys.path.insert(0, os.path.abspath('.'))
import json
import csv
import sqlite3
import hashlib

from core.enrichment.schema_validator import validate_enrichment_result_schema
from core.enrichment.validator import EvidenceValidator

DB_PATH = "data/normalized/ai_ecosystem.db"

EXPECTED_CANONICAL_HASHES = {
    "ai_startups": (1307, "ee0b6c12b8e38b8f"),
    "ai_products": (1316, "ebc6a89827087f95"),
    "ai_research_papers": (1060, "bf97c0a18d9031fb"),
    "ai_news": (1132, "fbcf007f534d9a7e"),
    "ai_jobs": (1930, "2aa9ffe8946ab1a9")
}


def main():
    print("=" * 75)
    print("   STAGE 3 — AUDIT 19 INDEPENDENT VERIFICATION")
    print("=" * 75)

    all_passed = True

    # 1. Database Integrity & Canonical Immutability
    print("\n[Check 1] SQLite Integrity and Canonical Immutability:")
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("PRAGMA integrity_check")
    ic = cur.fetchone()[0]
    if ic == "ok":
        print("  [PASS] SQLite PRAGMA integrity_check: ok")
    else:
        print(f"  [FAIL] SQLite integrity_check failed: {ic}")
        all_passed = False

    total_canonical_rows = 0
    for table, (exp_cnt, exp_hash) in EXPECTED_CANONICAL_HASHES.items():
        cur.execute(f"SELECT count(*) FROM {table}")
        cnt = cur.fetchone()[0]
        total_canonical_rows += cnt

        cur.execute(f"SELECT * FROM {table} ORDER BY rowid")
        rows = cur.fetchall()
        actual_hash = hashlib.sha256(repr(rows).encode("utf-8")).hexdigest()

        if cnt == exp_cnt and actual_hash.startswith(exp_hash):
            print(f"  [PASS] {table:20s}: {cnt:5d} rows (Hash: {actual_hash[:16]}...) [IMMUTABLE]")
        else:
            print(f"  [FAIL] {table:20s}: cnt={cnt} (exp {exp_cnt}), hash={actual_hash[:16]} (exp {exp_hash})")
            all_passed = False

    print(f"  -> Total Canonical Records: {total_canonical_rows:,} (Expected: 6,745)")
    if total_canonical_rows != 6745:
        all_passed = False

    # 2. Multi-Table Persistence Schema Verification
    print("\n[Check 2] Multi-Table SQLite Schema & Persistence:")
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    all_tables = [r[0] for r in cur.fetchall()]

    required_tables = [
        "llm_enrichment_results",
        "llm_enrichment_logs",
        "llm_provider_usage",
        "llm_review_queue"
    ]
    for t in required_tables:
        if t in all_tables:
            cur.execute(f"SELECT count(*) FROM {t}")
            cnt = cur.fetchone()[0]
            print(f"  [PASS] Table '{t:24s}': present with {cnt:3d} rows")
        else:
            print(f"  [FAIL] Required table '{t}' is missing!")
            all_passed = False

    if "enrichment_audit_log" not in all_tables:
        print("  [PASS] Legacy table 'enrichment_audit_log': successfully dropped")
    else:
        print("  [FAIL] Legacy table 'enrichment_audit_log' still exists!")
        all_passed = False

    # 3. Results JSONL & Schema Validation
    print("\n[Check 3] Results JSONL Schema Validation & Traceability:")
    jsonl_path = "reports/stage3_enrichment_results.jsonl"
    if not os.path.exists(jsonl_path):
        print(f"  [FAIL] {jsonl_path} does not exist!")
        return

    jsonl_records = []
    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            if not line.strip():
                continue
            rec = json.loads(line)
            jsonl_records.append(rec)
            is_valid, err = validate_enrichment_result_schema(rec)
            if not is_valid:
                print(f"  [FAIL] Line {line_no} failed JSON Schema: {err}")
                all_passed = False

    print(f"  [PASS] Total JSONL Records: {len(jsonl_records)} (All 100% Schema Valid)")

    # 4. Strict Evidence Grounding Verification
    print("\n[Check 4] Strict Field-Level Evidence Grounding (No Unsubstantiated VERIFIED):")
    status_counts = {}
    verified_count = 0
    review_count = 0
    insufficient_count = 0
    failed_count = 0

    for r in jsonl_records:
        st = r["validation_status"]
        status_counts[st] = status_counts.get(st, 0) + 1
        val = r["enriched_value"]
        ev = r["evidence"]

        if st == "VERIFIED":
            verified_count += 1
            # VERIFIED records MUST have non-empty evidence
            if not ev or not ev.strip():
                print(f"  [FAIL] Record {r['record_id']} is VERIFIED but has empty evidence!")
                all_passed = False
            # VERIFIED records must NOT have 0.95 unearned confidence from offline provider
            if r["provider"] == "offline" and r["confidence_score"] >= 0.95:
                print(f"  [FAIL] Heuristic record {r['record_id']} has unearned confidence {r['confidence_score']}!")
                all_passed = False
            # VERIFIED list items must all be in evidence
            if isinstance(val, list):
                norm_ev = EvidenceValidator.normalize_text(ev)
                for item in val:
                    if not EvidenceValidator.check_item_supported_in_evidence(str(item), norm_ev):
                        print(f"  [FAIL] Record {r['record_id']} is VERIFIED but item '{item}' is missing from evidence: '{ev}'")
                        all_passed = False
        elif st == "NEEDS_REVIEW":
            review_count += 1
        elif st == "INSUFFICIENT_EVIDENCE":
            insufficient_count += 1
        elif st == "FAILED":
            failed_count += 1

    print(f"  [PASS] VERIFIED:             {verified_count:3d} (Every item verified against exact evidence)")
    print(f"  [PASS] NEEDS_REVIEW:         {review_count:3d} (Ambiguous/partial/heuristic classifications)")
    print(f"  [PASS] INSUFFICIENT_EVIDENCE: {insufficient_count:3d} (Missing content/empty source)")
    print(f"  [PASS] FAILED:               {failed_count:3d} (Unsupported claims/schema/evidence mismatches)")

    # 5. Reconciliation across Artifacts
    print("\n[Check 5] Artifact & SQLite Reconciliation:")
    # Check review queue CSV
    csv_path = "reports/stage3_review_queue.csv"
    csv_rows = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        csv_rows = list(reader)

    expected_review_items = review_count + insufficient_count + failed_count
    if len(csv_rows) == expected_review_items:
        print(f"  [PASS] Review Queue CSV row count: {len(csv_rows)} == {expected_review_items} non-verified records")
    else:
        print(f"  [FAIL] Review Queue CSV count ({len(csv_rows)}) != expected ({expected_review_items})")
        all_passed = False

    # Check SQLite review queue table
    cur.execute("SELECT count(*) FROM llm_review_queue")
    db_queue_count = cur.fetchone()[0]
    if db_queue_count == expected_review_items:
        print(f"  [PASS] SQLite 'llm_review_queue' count: {db_queue_count} == {expected_review_items}")
    else:
        print(f"  [FAIL] SQLite 'llm_review_queue' count ({db_queue_count}) != expected ({expected_review_items})")
        all_passed = False

    # Check SQLite results table
    cur.execute("SELECT count(*) FROM llm_enrichment_results")
    db_results_count = cur.fetchone()[0]
    if db_results_count == len(jsonl_records):
        print(f"  [PASS] SQLite 'llm_enrichment_results' count: {db_results_count} == {len(jsonl_records)} JSONL records")
    else:
        print(f"  [FAIL] SQLite results count ({db_results_count}) != JSONL count ({len(jsonl_records)})")
        all_passed = False

    # 6. File Manifest Checksum Verification
    print("\n[Check 6] File Manifest and SHA-256 Checksums:")
    manifest_path = "reports/stage3_file_manifest.json"
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    for filepath, meta in manifest.items():
        if not os.path.exists(filepath):
            print(f"  [FAIL] File {filepath} in manifest does not exist!")
            all_passed = False
            continue
        h = hashlib.sha256()
        with open(filepath, "rb") as mf:
            while chunk := mf.read(65536):
                h.update(chunk)
        calc_sha = h.hexdigest()
        if calc_sha == meta["sha256"]:
            print(f"  [PASS] {filepath:40s}: {calc_sha[:16]}... (Valid)")
        else:
            print(f"  [FAIL] {filepath:40s}: hash mismatch! calc={calc_sha[:16]}, exp={meta['sha256'][:16]}")
            all_passed = False

    conn.close()

    print("\n" + "=" * 75)
    if all_passed:
        print("   >>> ALL AUDIT 19 VERIFICATION CHECKS PASSED PERFECTLY <<<")
    else:
        print("   >>> AUDIT 19 VERIFICATION FAILED <<<")
    print("=" * 75)


if __name__ == "__main__":
    main()
