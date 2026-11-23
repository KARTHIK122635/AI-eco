"""
Audit 28 Proposal Revalidation, Parity Reconciler & Review Queue Synchronizer
=============================================================================
1. Enforces Audit 28 EvidenceValidator rules:
   - Rejects application-generated label prefixes (e.g. 'AI Focus:')
   - Grounds quotations strictly in raw stored database fields
   - Flags duplication against canonical ai_focus_area and ai_evidence
2. Synchronizes JSONL and CSV with 100% field parity:
   - CSV evidence_quote == JSONL evidence_quote
   - Explanatory model evidence preserved in separate column (explanatory_evidence)
   - Preserves proposal_id, evidence_url, validation_status, schema_status, duplication_status
   - Strictly preserves approval_status = 'PENDING_APPROVAL' across all 37 proposals
3. Updates summary JSON metrics.
"""

import csv
import json
import os
import sys
import sqlite3
from typing import Any, Dict, List

sys.path.insert(0, os.path.abspath("."))

from core.enrichment.engine import EnrichmentEngine
from core.enrichment.schemas import EnrichmentResult, ValidationStatus, compute_canonical_source_version
from core.enrichment.validator import EvidenceValidator
from src.stage3.schema_mapping import (
    CANONICAL_TABLE_SCHEMAS,
    ENTITY_TABLE_MAP,
    check_proposal_schema_compatibility,
)


def run_revalidation_and_reconciliation(
    db_path: str = "data/normalized/ai_ecosystem.db",
    jsonl_path: str = "data/stage3/gemini_enrichment_results.jsonl",
    csv_path: str = "data/stage3/gemini_review_queue.csv",
    summary_path: str = "data/stage3/gemini_enrichment_summary.json",
):
    print("=" * 80)
    print("   AUDIT 28: REVALIDATING PROPOSALS & SYNCHRONIZING CSV/JSONL PARITY")
    print("=" * 80)

    # Connect read-only to canonical DB
    uri = f"file:{os.path.abspath(db_path)}?mode=ro"
    conn = sqlite3.connect(uri, uri=True)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # 1. Load existing proposals
    proposals: List[Dict[str, Any]] = []
    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                proposals.append(json.loads(line))
    print(f"[1] Loaded {len(proposals)} proposals from {jsonl_path}")

    status_counts = {"VERIFIED": 0, "NEEDS_REVIEW": 0, "INSUFFICIENT_EVIDENCE": 0, "FAILED": 0}
    schema_counts = {"SCHEMA_COMPATIBLE": 0, "BLOCKED_SCHEMA": 0}
    dup_counts = {"DUPLICATE_OF_EXISTING_CANONICAL_DATA": 0, "NO_DUPLICATION": 0}

    # 2. Revalidate each proposal with Audit 28 rules
    revalidated_proposals: List[Dict[str, Any]] = []
    for idx, p in enumerate(proposals, 1):
        pid = p["proposal_id"]
        et = p["entity_type"]
        rid = p["record_id"]
        fn = p["field_name"]
        orig_val = p.get("original_value")
        prop_val = p.get("proposed_value")
        raw_eq = p.get("evidence_quote") or ""
        raw_ev = p.get("evidence") or ""
        src_url = p.get("evidence_url") or p.get("source_url") or ""

        # Fetch canonical record
        table_name, id_col = ENTITY_TABLE_MAP.get(et, ("unknown", "unknown"))
        cursor.execute(f"SELECT * FROM {table_name} WHERE {id_col} = ?", (rid,))
        row = cursor.fetchone()
        canonical_rec = dict(row) if row else None

        # Build context
        source_text = EnrichmentEngine.build_canonical_source_text(et, canonical_rec) if canonical_rec else ""
        expected_ver = compute_canonical_source_version(et, canonical_rec) if canonical_rec else ""

        # Check schema compatibility
        is_compat, schema_code, schema_reason = check_proposal_schema_compatibility(et, fn)
        schema_counts[schema_code] = schema_counts.get(schema_code, 0) + 1

        # Check duplication against canonical data
        dup_status = "NO_DUPLICATION"
        if canonical_rec and et == "startup":
            existing_focus = (canonical_rec.get("ai_focus_area") or "").strip().lower()
            existing_ev = (canonical_rec.get("ai_evidence") or "").strip().lower()
            if fn in ("ai_specialization", "ai_focus_area"):
                if isinstance(prop_val, str) and prop_val.strip().lower() == existing_focus:
                    dup_status = "DUPLICATE_OF_EXISTING_CANONICAL_DATA"
            elif fn == "technologies" and isinstance(prop_val, list):
                if existing_ev and all(isinstance(t, str) and t.strip().lower() in existing_ev for t in prop_val if t):
                    dup_status = "DUPLICATE_OF_EXISTING_CANONICAL_DATA"

        dup_counts[dup_status] = dup_counts.get(dup_status, 0) + 1

        # Create EnrichmentResult for validator
        # We test raw_eq (the verbatim quote) as the evidence to validate
        result_obj = EnrichmentResult(
            attempt_id=pid,
            record_id=rid,
            entity_type=et,
            field_name=fn,
            original_value=orig_val,
            enriched_value=prop_val,
            source_url=src_url,
            evidence=raw_eq if raw_eq else raw_ev,
            source_version=expected_ver,
            confidence_score=p.get("confidence_score") or p.get("confidence") or 0.0,
            enrichment_method=p.get("enrichment_method") or "llm_extraction",
            provider=p.get("provider") or "google-gemini",
            model=p.get("model_id") or "gemini-3.1-flash-lite",
            enriched_at=p.get("created_at") or "",
            validation_status="NEEDS_REVIEW",
            validation_rationale="",
            retry_count=p.get("retry_count", 0),
        )
        setattr(result_obj, "evidence_quote", raw_eq)

        # Run Audit 28 validator
        val_status, val_rationale = EvidenceValidator.validate_enrichment(
            result_obj, source_text, canonical_record=canonical_rec
        )

        status_counts[val_status.value] = status_counts.get(val_status.value, 0) + 1

        # Update proposal dict
        p["validation_status"] = val_status.value
        p["validation_rationale"] = val_rationale
        p["schema_status"] = schema_code
        p["schema_target_table"] = table_name
        p["schema_target_column"] = fn if is_compat else "NONE (Column does not exist)"
        p["schema_rationale"] = schema_reason
        p["duplication_status"] = dup_status
        p["approval_status"] = "PENDING_APPROVAL"
        p["evidence_quote"] = raw_eq
        p["evidence"] = raw_ev

        revalidated_proposals.append(p)

    conn.close()

    print(f"\n[2] Revalidation Outcome Summary:")
    print(f"    - VERIFIED:              {status_counts['VERIFIED']}")
    print(f"    - NEEDS_REVIEW:          {status_counts['NEEDS_REVIEW']}")
    print(f"    - FAILED:                {status_counts['FAILED']}")
    print(f"    - INSUFFICIENT_EVIDENCE: {status_counts['INSUFFICIENT_EVIDENCE']}")
    print(f"    - Schema Compatible:     {schema_counts['SCHEMA_COMPATIBLE']}")
    print(f"    - Schema Blocked:        {schema_counts['BLOCKED_SCHEMA']}")
    print(f"    - Duplicate Canonical:   {dup_counts['DUPLICATE_OF_EXISTING_CANONICAL_DATA']}")

    # 3. Write Revalidated JSONL
    with open(jsonl_path, "w", encoding="utf-8") as f:
        for p in revalidated_proposals:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")
    print(f"[3] Written {len(revalidated_proposals)} records to {jsonl_path}")

    # 4. Write Synchronized CSV with 100% field parity
    csv_headers = [
        "proposal_id",
        "record_id",
        "entity_type",
        "field_name",
        "original_value",
        "proposed_value",
        "evidence_quote",           # EXACT verbatim quote matching JSONL evidence_quote
        "explanatory_evidence",     # Model explanation separated (from JSONL evidence)
        "reasoning",                # Model reasoning
        "evidence_url",
        "validation_status",
        "validation_rationale",
        "confidence_score",
        "schema_status",
        "schema_target_table",
        "schema_target_column",
        "duplication_status",
        "approval_status",
        "reviewer",
        "reviewed_at",
        "review_notes",
    ]

    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=csv_headers)
        writer.writeheader()
        for p in revalidated_proposals:
            prop_str = (
                json.dumps(p.get("proposed_value"), ensure_ascii=False)
                if isinstance(p.get("proposed_value"), (list, dict))
                else str(p.get("proposed_value") or "")
            )
            orig_str = (
                json.dumps(p.get("original_value"), ensure_ascii=False)
                if isinstance(p.get("original_value"), (list, dict))
                else ("" if p.get("original_value") is None else str(p.get("original_value")))
            )
            writer.writerow({
                "proposal_id": p.get("proposal_id", ""),
                "record_id": p.get("record_id", ""),
                "entity_type": p.get("entity_type", ""),
                "field_name": p.get("field_name", ""),
                "original_value": orig_str,
                "proposed_value": prop_str,
                "evidence_quote": p.get("evidence_quote", ""),        # Exact match to JSONL
                "explanatory_evidence": p.get("evidence", ""),        # Separate explanation
                "reasoning": p.get("reasoning", ""),                  # Model reasoning
                "evidence_url": p.get("evidence_url", "") or p.get("source_url", ""),
                "validation_status": p.get("validation_status", ""),
                "validation_rationale": p.get("validation_rationale", ""),
                "confidence_score": str(p.get("confidence_score") or p.get("confidence") or ""),
                "schema_status": p.get("schema_status", ""),
                "schema_target_table": p.get("schema_target_table", ""),
                "schema_target_column": p.get("schema_target_column", ""),
                "duplication_status": p.get("duplication_status", ""),
                "approval_status": "PENDING_APPROVAL",
                "reviewer": p.get("reviewer", ""),
                "reviewed_at": p.get("reviewed_at", ""),
                "review_notes": p.get("review_notes", ""),
            })
    print(f"[4] Written {len(revalidated_proposals)} synchronized records to {csv_path}")

    # 5. Update summary JSON
    if os.path.exists(summary_path):
        with open(summary_path, "r", encoding="utf-8") as f:
            summary = json.load(f)
    else:
        summary = {}

    summary["status_distribution"] = status_counts
    summary["approval_distribution"] = {
        "PENDING_APPROVAL": len(revalidated_proposals),
        "APPROVED": 0,
        "REJECTED": 0,
        "REQUEST_REVIEW": 0,
    }
    summary["schema_compatibility"] = {
        "schema_compatible_count": schema_counts["SCHEMA_COMPATIBLE"],
        "schema_blocked_count": schema_counts["BLOCKED_SCHEMA"],
        "verified_blocked_by_schema_count": sum(1 for p in revalidated_proposals if p["validation_status"] == "VERIFIED" and p["schema_status"] == "BLOCKED_SCHEMA"),
        "duplicated_canonical_data_count": dup_counts["DUPLICATE_OF_EXISTING_CANONICAL_DATA"],
        "governance_note": (
            "Proposals targeting non-existent canonical columns are strictly blocked from database writes "
            "with status BLOCKED_SCHEMA. All proposals remain PENDING_APPROVAL."
        ),
    }

    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f"[5] Updated {summary_path}")

    # 6. Verify Parity
    print("\n[6] Verifying 100% JSONL-to-CSV Parity...")
    csv_rows = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        csv_rows = list(reader)

    assert len(csv_rows) == len(revalidated_proposals), f"Row count mismatch: CSV={len(csv_rows)}, JSONL={len(revalidated_proposals)}"

    mismatches = []
    for i, (j_rec, c_rec) in enumerate(zip(revalidated_proposals, csv_rows)):
        pid_j = j_rec["proposal_id"]
        pid_c = c_rec["proposal_id"]
        if pid_j != pid_c:
            mismatches.append(f"Row {i+1}: proposal_id mismatch: {pid_j} vs {pid_c}")

        eq_j = j_rec.get("evidence_quote", "")
        eq_c = c_rec.get("evidence_quote", "")
        if eq_j != eq_c:
            mismatches.append(f"Row {i+1} ({pid_j}): evidence_quote mismatch: {repr(eq_j)} vs {repr(eq_c)}")

        val_j = j_rec.get("validation_status", "")
        val_c = c_rec.get("validation_status", "")
        if val_j != val_c:
            mismatches.append(f"Row {i+1} ({pid_j}): validation_status mismatch: {val_j} vs {val_c}")

        sch_j = j_rec.get("schema_status", "")
        sch_c = c_rec.get("schema_status", "")
        if sch_j != sch_c:
            mismatches.append(f"Row {i+1} ({pid_j}): schema_status mismatch: {sch_j} vs {sch_c}")

        dup_j = j_rec.get("duplication_status", "")
        dup_c = c_rec.get("duplication_status", "")
        if dup_j != dup_c:
            mismatches.append(f"Row {i+1} ({pid_j}): duplication_status mismatch: {dup_j} vs {dup_c}")

    if mismatches:
        print(f"[FAIL] Found {len(mismatches)} parity mismatches:")
        for m in mismatches:
            print(f"  - {m}")
        sys.exit(1)
    else:
        print(f"[SUCCESS] 100% Parity Verified across all {len(csv_rows)} records (0 mismatches).")


if __name__ == "__main__":
    run_revalidation_and_reconciliation()
