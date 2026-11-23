"""
Stage 3 Write-Protected Database Update Applicator
===================================================
Applies explicitly human-approved Stage 3 enrichment proposals to the canonical
SQLite database.

STRICT CONSTRAINTS & SAFEGUARDS (Audit 27 Hardened):
1. Canonical database updates remain strictly disabled until explicit human authorization.
2. Only proposals with approval_status='APPROVED' and validation_status='VERIFIED' may be applied.
3. Schema Compatibility Guard: Rejects any proposal targeting a column that does not exist in
   the canonical schema allowlist (BLOCKED_SCHEMA prevention).
4. SQL Identifier Allowlisting: Strictly validates all table and column names to prevent injection.
5. Requires explicit proposal ID (--proposal-id) and explicit confirmation flag (--confirm-write-authorized).
6. Revalidates original record and field concurrency before applying.
7. Preserves complete before-image and after-image.
8. Writes immutable audit log entries into enrichment_audit_log.
9. Executes strictly inside an atomic SQLite transaction (ROLLBACK on any failure).
10. Never modifies, deletes, or overwrites the 366 historical Audit 19 archive records.
11. DO NOT EXECUTE THIS SCRIPT DURING STAGE 3 GEMINI ENRICHMENT TURN.
"""

import argparse
import json
import logging
import os
import sqlite3
import sys
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from src.stage3.schema_mapping import (
    CANONICAL_TABLE_SCHEMAS,
    ENTITY_TABLE_MAP,
    check_proposal_schema_compatibility,
    is_column_allowed,
    is_valid_sql_identifier,
)

logger = logging.getLogger("stage3.apply_approved")


class ApprovedUpdateApplicator:
    """Safely applies approved enrichment proposals with atomic transaction rollback and schema validation."""

    def __init__(
        self,
        db_path: str = "data/normalized/ai_ecosystem.db",
        queue_csv_path: str = "data/stage3/gemini_review_queue.csv",
        results_jsonl_path: str = "data/stage3/gemini_enrichment_results.jsonl",
    ):
        self.db_path = os.path.abspath(db_path)
        self.queue_csv_path = os.path.abspath(queue_csv_path)
        self.results_jsonl_path = os.path.abspath(results_jsonl_path)

    def load_proposal(self, proposal_id: str) -> Optional[Dict[str, Any]]:
        """Loads a proposal by ID from the JSONL store."""
        if not os.path.exists(self.results_jsonl_path):
            return None
        with open(self.results_jsonl_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    data = json.loads(line)
                    if data.get("proposal_id") == proposal_id:
                        return data
        return None

    def apply_proposal(
        self,
        proposal_id: str,
        confirm_authorized: bool = False,
    ) -> Tuple[bool, str]:
        """
        Applies a single human-approved proposal to the canonical database.
        Strictly guarded by confirm_authorized flag and schema compatibility allowlist.
        """
        # Guard 1: Authorization flag
        if not confirm_authorized:
            return False, (
                "WRITE PROTECTION ABORT: Database updates remain disabled. "
                "Must supply --confirm-write-authorized with explicit user authorization."
            )

        # Guard 2: Load proposal
        proposal = self.load_proposal(proposal_id)
        if not proposal:
            return False, f"Proposal ID '{proposal_id}' not found in results store."

        # Guard 3: Approval status check
        app_status = proposal.get("approval_status")
        if app_status != "APPROVED":
            return False, (
                f"APPROVAL VIOLATION: Proposal '{proposal_id}' status is '{app_status}'. "
                "Only proposals explicitly marked 'APPROVED' by a human reviewer may be applied."
            )

        # Guard 4: Validation status check
        val_status = proposal.get("validation_status")
        if val_status != "VERIFIED":
            return False, (
                f"VALIDATION VIOLATION: Proposal '{proposal_id}' validation status is '{val_status}'. "
                "Only VERIFIED proposals may be applied to the canonical database."
            )

        entity_type = proposal.get("entity_type")
        record_id = proposal.get("record_id")
        field_name = proposal.get("field_name")
        proposed_val = proposal.get("proposed_value")
        orig_val = proposal.get("original_value")

        # Guard 5: Schema Compatibility & Identifier Allowlist (Static Allowlist Guard)
        is_compat, status_code, schema_reason = check_proposal_schema_compatibility(
            entity_type, field_name
        )
        if not is_compat:
            return False, f"SCHEMA COMPATIBILITY ABORT: {schema_reason}"

        # Guard 5b: Duplication Status Guard (Audit 29: Require strict NO_DUPLICATION)
        dup_status = proposal.get("duplication_status")
        if dup_status != "NO_DUPLICATION":
            return False, (
                f"DUPLICATION ABORT: Proposal '{proposal_id}' duplication_status is '{dup_status}'. "
                "Only proposals explicitly verified as 'NO_DUPLICATION' may be applied."
            )

        # Guard 5c: Schema Status Guard (Audit 29: Require strict SCHEMA_COMPATIBLE)
        schema_status = proposal.get("schema_status")
        if schema_status != "SCHEMA_COMPATIBLE":
            return False, (
                f"SCHEMA COMPATIBILITY ABORT: Proposal '{proposal_id}' schema_status is '{schema_status}'. "
                "Only proposals verified as 'SCHEMA_COMPATIBLE' may be applied."
            )

        table_name, id_col = ENTITY_TABLE_MAP[entity_type]

        # Serialization for list/dict proposed values
        db_proposed_val = proposed_val
        if isinstance(proposed_val, (list, dict)):
            db_proposed_val = json.dumps(proposed_val, ensure_ascii=False)

        # Guard 6: Connect and execute transaction
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        try:
            conn.execute("BEGIN IMMEDIATE TRANSACTION;")

            # 6a. Runtime Physical Schema Verification via PRAGMA table_info (Audit 28)
            cursor.execute(f"PRAGMA table_info({table_name});")
            pragma_rows = cursor.fetchall()
            pragma_cols = [row[1] if isinstance(row, tuple) else row["name"] for row in pragma_rows]
            if not pragma_cols:
                conn.rollback()
                conn.close()
                return False, f"RUNTIME SCHEMA ERROR: Physical table '{table_name}' does not exist in SQLite database."

            if field_name not in pragma_cols:
                conn.rollback()
                conn.close()
                return False, (
                    f"RUNTIME SCHEMA ABORT: Physical column '{field_name}' does not exist in table "
                    f"'{table_name}' (PRAGMA table_info verified). SQLite UPDATE rejected."
                )

            # 6b. Retrieve current canonical record (Concurrency Check)
            cursor.execute(f"SELECT * FROM {table_name} WHERE {id_col} = ?", (record_id,))
            current_row = cursor.fetchone()
            if not current_row:
                conn.rollback()
                conn.close()
                return False, f"Record '{record_id}' not found in canonical table '{table_name}'."

            current_dict = dict(current_row)
            current_field_val = current_dict.get(field_name)

            # 6c. Dynamic Duplication Safeguard against actual stored row (Audit 28)
            if entity_type == "startup":
                if field_name in ("ai_specialization", "ai_focus_area"):
                    existing_focus = (current_dict.get("ai_focus_area") or "").strip().lower()
                    if isinstance(proposed_val, str) and proposed_val.strip().lower() == existing_focus:
                        conn.rollback()
                        conn.close()
                        return False, (
                            f"DUPLICATION REJECTED: Proposed value '{proposed_val}' duplicates existing "
                            f"canonical ai_focus_area ('{current_dict.get('ai_focus_area')}')."
                        )
                elif field_name == "technologies" and isinstance(proposed_val, list):
                    existing_ev = (current_dict.get("ai_evidence") or "").strip().lower()
                    if existing_ev and all(isinstance(t, str) and t.strip().lower() in existing_ev for t in proposed_val if t):
                        conn.rollback()
                        conn.close()
                        return False, (
                            f"DUPLICATION REJECTED: Proposed technologies {proposed_val} already exist "
                            f"in canonical ai_evidence. No new enrichment achieved."
                        )

            # Check if value changed concurrently since proposal generation
            orig_val_serialized = (
                json.dumps(orig_val, ensure_ascii=False)
                if isinstance(orig_val, (list, dict))
                else orig_val
            )
            curr_val_serialized = (
                json.dumps(current_field_val, ensure_ascii=False)
                if isinstance(current_field_val, (list, dict))
                else current_field_val
            )

            # Audit 29: Exact before-image match (empty string "" vs None/NULL strictly triggers conflict)
            if orig_val_serialized != curr_val_serialized:
                conn.rollback()
                return False, (
                    f"CONCURRENCY CONFLICT: Field '{field_name}' on '{record_id}' was modified "
                    f"after proposal generation. Expected: {repr(orig_val_serialized)}, Current: {repr(curr_val_serialized)}."
                )

            # 6b. Update Canonical Table (Safe parameterized SQL)
            cursor.execute(
                f"UPDATE {table_name} SET {field_name} = ? WHERE {id_col} = ?",
                (db_proposed_val, record_id),
            )

            # 6c. Insert Immutable Audit Log Entry
            audit_id = str(uuid.uuid4())
            now_ts = datetime.now(timezone.utc).isoformat()
            cursor.execute(
                """
                INSERT INTO enrichment_audit_log (
                    audit_id, entity_type, record_id, field_name,
                    original_value, enriched_value, source_url,
                    evidence_used, confidence_score, enrichment_method,
                    provider, model, audit_phase, enriched_at, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    audit_id,
                    entity_type,
                    record_id,
                    field_name,
                    curr_val_serialized,
                    db_proposed_val,
                    proposal.get("evidence_url") or "",
                    proposal.get("evidence_quote") or proposal.get("evidence") or "",
                    proposal.get("confidence_score", 1.0),
                    "gemini_human_approved",
                    "google-gemini",
                    proposal.get("model_id", "gemini-3.1-flash-lite"),
                    "STAGE_3_GEMINI_APPLIED",
                    now_ts,
                    now_ts,
                ),
            )

            # Commit Transaction
            conn.commit()
            logger.info(f"Successfully applied proposal {proposal_id} to {record_id}.{field_name}")
            return True, f"Proposal '{proposal_id}' successfully applied to {record_id}.{field_name}."

        except Exception as e:
            conn.rollback()
            logger.error(f"Transaction rolled back while applying proposal {proposal_id}: {e}")
            return False, f"Transaction error (ROLLED BACK): {e}"
        finally:
            conn.close()


def main():
    parser = argparse.ArgumentParser(description="Stage 3 Write-Protected Database Update Applicator")
    parser.add_argument("--proposal-id", required=True, help="Explicit approved proposal ID to apply")
    parser.add_argument("--confirm-write-authorized", action="store_true", help="Explicit human confirmation flag")
    parser.add_argument("--db-path", default="data/normalized/ai_ecosystem.db", help="Path to database")

    args = parser.parse_args()

    applicator = ApprovedUpdateApplicator(db_path=args.db_path)
    success, msg = applicator.apply_proposal(
        proposal_id=args.proposal_id,
        confirm_authorized=args.confirm_write_authorized,
    )

    if success:
        print(f"[SUCCESS] {msg}")
        sys.exit(0)
    else:
        print(f"[BLOCKED] {msg}")
        sys.exit(1)


if __name__ == "__main__":
    main()
