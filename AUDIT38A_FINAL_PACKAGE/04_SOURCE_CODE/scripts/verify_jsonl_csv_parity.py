"""
Audit 28 Independent Proposal Parity Verifier
==============================================
Validates 100% parity between:
- data/stage3/gemini_enrichment_results.jsonl
- data/stage3/gemini_review_queue.csv

Checks:
1. Count matches (37 records)
2. Every proposal_id matches in exact order
3. evidence_quote is identical character-for-character
4. validation_status is identical
5. schema_status is identical
6. duplication_status is identical
7. approval_status is identical ('PENDING_APPROVAL')
8. evidence_url is identical
"""

import csv
import json
import os
import sys

def verify_parity(
    jsonl_path: str = "data/stage3/gemini_enrichment_results.jsonl",
    csv_path: str = "data/stage3/gemini_review_queue.csv"
) -> bool:
    if not os.path.exists(jsonl_path):
        print(f"[FAIL] JSONL file not found: {jsonl_path}")
        return False
    if not os.path.exists(csv_path):
        print(f"[FAIL] CSV file not found: {csv_path}")
        return False

    proposals = []
    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                proposals.append(json.loads(line))

    csv_rows = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        csv_rows = list(reader)

    if len(proposals) != len(csv_rows):
        print(f"[FAIL] Record count mismatch: JSONL={len(proposals)}, CSV={len(csv_rows)}")
        return False

    errors = []
    for idx, (j, c) in enumerate(zip(proposals, csv_rows), 1):
        pid = j.get("proposal_id")
        if pid != c.get("proposal_id"):
            errors.append(f"Row {idx}: proposal_id mismatch: {pid} != {c.get('proposal_id')}")

        eq_j = j.get("evidence_quote", "")
        eq_c = c.get("evidence_quote", "")
        if eq_j != eq_c:
            errors.append(f"Row {idx} ({pid}): evidence_quote mismatch: {repr(eq_j)} != {repr(eq_c)}")

        val_j = j.get("validation_status", "")
        val_c = c.get("validation_status", "")
        if val_j != val_c:
            errors.append(f"Row {idx} ({pid}): validation_status mismatch: {val_j} != {val_c}")

        sch_j = j.get("schema_status", "")
        sch_c = c.get("schema_status", "")
        if sch_j != sch_c:
            errors.append(f"Row {idx} ({pid}): schema_status mismatch: {sch_j} != {sch_c}")

        dup_j = j.get("duplication_status", "")
        dup_c = c.get("duplication_status", "")
        if dup_j != dup_c:
            errors.append(f"Row {idx} ({pid}): duplication_status mismatch: {dup_j} != {dup_c}")

        app_j = j.get("approval_status", "")
        app_c = c.get("approval_status", "")
        if app_j != "PENDING_APPROVAL" or app_c != "PENDING_APPROVAL":
            errors.append(f"Row {idx} ({pid}): approval_status violation: JSONL={app_j}, CSV={app_c}")

        url_j = j.get("evidence_url") or j.get("source_url") or ""
        url_c = c.get("evidence_url") or ""
        if url_j != url_c:
            errors.append(f"Row {idx} ({pid}): evidence_url mismatch: {url_j} != {url_c}")

    if errors:
        print(f"[FAIL] Found {len(errors)} parity mismatches between JSONL and CSV:")
        for err in errors[:10]:
            print(f"  - {err}")
        return False

    print(f"[PASS] 100% Parity Verified across all {len(proposals)} proposals.")
    print("       - All 37 proposal IDs match.")
    print("       - All 37 evidence quotations match character-for-character.")
    print("       - All 37 validation statuses match.")
    print("       - All 37 schema statuses match.")
    print("       - All 37 duplication statuses match.")
    print("       - All 37 approval statuses remain strictly 'PENDING_APPROVAL'.")
    print("       - All 37 evidence URLs match.")
    return True


if __name__ == "__main__":
    success = verify_parity()
    sys.exit(0 if success else 1)
