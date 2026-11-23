"""
Audit 27 Proposal Store & Review Queue Annotation Script
=========================================================
Annotates Stage 3 proposals with:
- schema_status: SCHEMA_COMPATIBLE vs BLOCKED_SCHEMA
- schema_target_table: Canonical table name
- schema_target_column: Canonical column name or NONE (Column does not exist)
- duplication_status: DUPLICATE_OF_EXISTING_CANONICAL_DATA vs NO_DUPLICATION
- STRICT PRESERVATION: All 37 proposals remain in PENDING_APPROVAL status.
"""

import csv
import json
import os
import sys
import sqlite3
from typing import Any, Dict, List

sys.path.insert(0, os.path.abspath("."))

from src.stage3.schema_mapping import (
    CANONICAL_TABLE_SCHEMAS,
    ENTITY_TABLE_MAP,
    check_proposal_schema_compatibility,
)


def annotate_stage3_artifacts(
    db_path: str = "data/normalized/ai_ecosystem.db",
    jsonl_path: str = "data/stage3/gemini_enrichment_results.jsonl",
    csv_path: str = "data/stage3/gemini_review_queue.csv",
    summary_path: str = "data/stage3/gemini_enrichment_summary.json",
):
    # Connect read-only to database
    uri = f"file:{os.path.abspath(db_path)}?mode=ro"
    conn = sqlite3.connect(uri, uri=True)
    cursor = conn.cursor()

    # 1. Read JSONL
    proposals: List[Dict[str, Any]] = []
    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                proposals.append(json.loads(line))

    # 2. Annotate proposals
    for p in proposals:
        et = p.get("entity_type")
        fn = p.get("field_name")
        rid = p.get("record_id")
        tbl, _ = ENTITY_TABLE_MAP.get(et, ("unknown", "unknown"))

        is_compat, status_code, reason = check_proposal_schema_compatibility(et, fn)
        p["schema_status"] = status_code
        p["schema_target_table"] = tbl
        p["schema_target_column"] = fn if is_compat else "NONE (Column does not exist)"
        p["schema_rationale"] = reason

        # Strict preservation of approval state
        p["approval_status"] = "PENDING_APPROVAL"

        # Duplication check against canonical record
        dup_status = "NO_DUPLICATION"
        if et == "startup":
            cursor.execute("SELECT ai_focus_area, ai_evidence FROM ai_startups WHERE startup_id = ?", (rid,))
            row = cursor.fetchone()
            if row:
                focus_val = (row[0] or "").strip().lower()
                ev_val = (row[1] or "").strip().lower()
                val = p.get("proposed_value")
                if fn == "ai_specialization" and isinstance(val, str) and val.strip().lower() == focus_val:
                    dup_status = "DUPLICATE_OF_EXISTING_CANONICAL_DATA"
                elif fn == "technologies" and isinstance(val, list):
                    if all(isinstance(item, str) and item.strip().lower() in ev_val for item in val if item):
                        dup_status = "DUPLICATE_OF_EXISTING_CANONICAL_DATA"

        p["duplication_status"] = dup_status

    conn.close()

    # 3. Write annotated JSONL
    with open(jsonl_path, "w", encoding="utf-8") as f:
        for p in proposals:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")
    print(f"Annotated JSONL written to {jsonl_path} ({len(proposals)} records)")

    # 4. Write annotated Review Queue CSV
    csv_headers = [
        "proposal_id",
        "record_id",
        "entity_type",
        "field_name",
        "original_value",
        "proposed_value",
        "evidence_quote",
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
        for p in proposals:
            writer.writerow({
                "proposal_id": p.get("proposal_id", ""),
                "record_id": p.get("record_id", ""),
                "entity_type": p.get("entity_type", ""),
                "field_name": p.get("field_name", ""),
                "original_value": p.get("original_value", "") if p.get("original_value") is not None else "",
                "proposed_value": json.dumps(p.get("proposed_value"), ensure_ascii=False) if isinstance(p.get("proposed_value"), (list, dict)) else str(p.get("proposed_value") or ""),
                "evidence_quote": p.get("evidence", ""),
                "evidence_url": p.get("evidence_url", "") or p.get("source_url", ""),
                "validation_status": p.get("validation_status", ""),
                "validation_rationale": p.get("validation_rationale", ""),
                "confidence_score": str(p.get("confidence", "") or p.get("confidence_score", "")),
                "schema_status": p.get("schema_status", ""),
                "schema_target_table": p.get("schema_target_table", ""),
                "schema_target_column": p.get("schema_target_column", ""),
                "duplication_status": p.get("duplication_status", ""),
                "approval_status": "PENDING_APPROVAL",
                "reviewer": p.get("reviewer", "") or "",
                "reviewed_at": p.get("reviewed_at", "") or "",
                "review_notes": p.get("review_notes", "") or "",
            })
    print(f"Annotated CSV written to {csv_path}")

    # 5. Update Summary JSON
    if os.path.exists(summary_path):
        with open(summary_path, "r", encoding="utf-8") as f:
            summary = json.load(f)
    else:
        summary = {}

    compat_count = sum(1 for p in proposals if p["schema_status"] == "SCHEMA_COMPATIBLE")
    blocked_count = sum(1 for p in proposals if p["schema_status"] == "BLOCKED_SCHEMA")
    dup_count = sum(1 for p in proposals if p["duplication_status"] == "DUPLICATE_OF_EXISTING_CANONICAL_DATA")
    verified_blocked = sum(1 for p in proposals if p["validation_status"] == "VERIFIED" and p["schema_status"] == "BLOCKED_SCHEMA")

    summary["schema_compatibility"] = {
        "schema_compatible_count": compat_count,
        "schema_blocked_count": blocked_count,
        "verified_blocked_by_schema_count": verified_blocked,
        "duplicated_canonical_data_count": dup_count,
        "governance_note": (
            "Proposals targeting non-existent canonical columns are strictly blocked from database writes "
            "with status BLOCKED_SCHEMA. All proposals remain PENDING_APPROVAL."
        )
    }

    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f"Updated summary written to {summary_path}")


if __name__ == "__main__":
    annotate_stage3_artifacts()
