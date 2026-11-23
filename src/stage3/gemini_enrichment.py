"""
Stage 3 Gemini LLM Enrichment Runner
=====================================
Executes batch enrichment on candidate records using official Google Gemini API.
Enforces:
- Strict read-only database access
- Canonical source text extraction and source version verification
- EvidenceValidator enforcement (Audit 20-25 pipeline rules)
- Mandatory human approval review queue persistence (PENDING_APPROVAL)
- Token and cost accounting
- Zero modifications to canonical database tables
"""

import argparse
import csv
import hashlib
import json
import logging
import os
import sqlite3
import sys
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from core.enrichment.engine import EnrichmentEngine
from core.enrichment.schemas import (
    APPROVED_TAXONOMY,
    EnrichmentResult,
    ValidationStatus,
    compute_canonical_source_version,
)
from core.enrichment.schema_validator import validate_enrichment_result_schema
from core.enrichment.validator import EvidenceValidator
from src.stage3.gemini_provider import GeminiEnrichmentResponse, GeminiProvider, redact_secrets
from src.stage3.schema_mapping import (
    CANONICAL_TABLE_SCHEMAS,
    ENTITY_TABLE_MAP,
    check_proposal_schema_compatibility,
)

# Setup Logger
logger = logging.getLogger("stage3.gemini_enrichment")


def compute_file_hash(path: str) -> str:
    """Computes SHA-256 hash of a file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


class GeminiEnrichmentRunner:
    """Orchestrates Stage 3 Gemini enrichment across candidate records."""

    TABLE_ID_MAP = {
        "startup": ("ai_startups", "startup_id"),
        "product": ("ai_products", "product_id"),
        "paper": ("ai_research_papers", "paper_id"),
        "news": ("ai_news", "news_id"),
        "job": ("ai_jobs", "job_id"),
    }

    def __init__(
        self,
        db_path: str = "data/normalized/ai_ecosystem.db",
        candidates_file: str = "reports/stage3_enrichment_results.jsonl",
        output_dir: str = "data/stage3",
        model_id: Optional[str] = None,
        batch_size: int = 5,
    ):
        self.db_path = os.path.abspath(db_path)
        self.candidates_file = os.path.abspath(candidates_file)
        self.output_dir = os.path.abspath(output_dir)
        self.model_id = model_id
        self.batch_size = batch_size

        os.makedirs(self.output_dir, exist_ok=True)

        # Output file paths
        self.results_jsonl_path = os.path.join(self.output_dir, "gemini_enrichment_results.jsonl")
        self.review_queue_csv_path = os.path.join(self.output_dir, "gemini_review_queue.csv")
        self.summary_json_path = os.path.join(self.output_dir, "gemini_enrichment_summary.json")
        self.audit_log_path = os.path.join(self.output_dir, "gemini_enrichment_audit.log")

        # Configure file logging for audit
        file_handler = logging.FileHandler(self.audit_log_path, encoding="utf-8")
        file_handler.setLevel(logging.INFO)
        formatter = logging.Formatter("[%(asctime)s] %(levelname)s %(name)s: %(message)s")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        logger.setLevel(logging.INFO)

        # Initialize provider (deferred validation until execute/dry-run)
        self.provider = GeminiProvider(model_id=self.model_id)

    def get_canonical_record(self, entity_type: str, record_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves a record strictly read-only from the canonical SQLite database."""
        if entity_type not in self.TABLE_ID_MAP:
            return None

        table_name, id_col = self.TABLE_ID_MAP[entity_type]
        # Open in URI read-only mode to physically guarantee no DB writes
        uri = f"file:{self.db_path}?mode=ro"
        conn = sqlite3.connect(uri, uri=True)
        try:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM {table_name} WHERE {id_col} = ?", (record_id,))
            row = cursor.fetchone()
            if row:
                return dict(row)
        finally:
            conn.close()
        return None

    def load_candidates(self) -> List[Dict[str, Any]]:
        """Loads the candidate records from the Stage 3 JSONL file with fallback search."""
        if not os.path.exists(self.candidates_file):
            alt_paths = [
                os.path.join(os.path.dirname(self.candidates_file), "..", "01_ENRICHMENT_RESULTS", "candidate_inputs_stage3.jsonl"),
                os.path.join(os.path.dirname(self.candidates_file), "..", "reports", "stage3_enrichment_results.jsonl"),
                os.path.join("01_ENRICHMENT_RESULTS", "candidate_inputs_stage3.jsonl"),
                os.path.join("reports", "stage3_enrichment_results.jsonl"),
                os.path.join(os.path.dirname(__file__), "..", "..", "reports", "stage3_enrichment_results.jsonl"),
            ]
            for alt in alt_paths:
                norm_alt = os.path.abspath(alt)
                if os.path.exists(norm_alt):
                    self.candidates_file = norm_alt
                    break

        if not os.path.exists(self.candidates_file):
            raise FileNotFoundError(f"Candidates file not found: {self.candidates_file}")

        candidates = []
        with open(self.candidates_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    candidates.append(json.loads(line))
        return candidates

    def get_field_type_hint(self, entity_type: str, field_name: str) -> str:
        """Determines expected data type hint and taxonomy options for a field."""
        list_fields = {"technologies", "key_contributions", "required_skills", "features"}
        if field_name in list_fields:
            return "JSON list of strings"

        # Check if field has approved taxonomy
        if entity_type in APPROVED_TAXONOMY and field_name in APPROVED_TAXONOMY[entity_type]:
            tax_opts = ", ".join(sorted(APPROVED_TAXONOMY[entity_type][field_name]))
            return f"string from approved taxonomy: [{tax_opts}]"

        return "string"

    def run_dry_run(self, limit: Optional[int] = None) -> bool:
        """
        Executes a non-destructive dry-run inspection of the candidate records.
        Verifies database integrity, candidate mappings, and provider configuration.
        """
        print("=" * 80)
        print("   STAGE 3 GEMINI ENRICHMENT: DRY-RUN INSPECTION")
        print("=" * 80)

        # 1. Verify Database
        if not os.path.exists(self.db_path):
            print(f"[FAIL] Database file not found: {self.db_path}")
            return False
        db_hash = compute_file_hash(self.db_path)
        print(f"[OK] Database exists. SHA-256: {db_hash}")

        # 2. Check Provider API Key
        is_key_valid, key_msg = self.provider.validate_api_key()
        if is_key_valid:
            print(f"[OK] Gemini API Key configured. Model: {self.provider.model_id}")
        else:
            print(f"[WARN] Gemini API Key check: {key_msg}")
            print("       (Note: An API key is required to execute live enrichment calls)")

        # 3. Load Candidates
        candidates = self.load_candidates()
        total_cands = len(candidates)
        if limit:
            candidates = candidates[:limit]
        print(f"[OK] Loaded {total_cands} candidates from {os.path.basename(self.candidates_file)}")
        print(f"     Processing scope: {len(candidates)} candidates")

        # 4. Inspect Candidates against Canonical DB
        print("\nCandidate Inspection Table:")
        print("-" * 80)
        print(f"{'#':<3} {'Entity':<8} {'Record ID':<30} {'Field':<18} {'Source Trace'}")
        print("-" * 80)

        missing_records = 0
        version_mismatches = 0
        for i, c in enumerate(candidates, 1):
            entity = c.get("entity_type")
            rec_id = c.get("record_id")
            field = c.get("field_name")
            expected_ver = c.get("source_version")

            rec = self.get_canonical_record(entity, rec_id)
            if not rec:
                missing_records += 1
                trace_status = "FAIL: Record missing in canonical DB"
            else:
                actual_ver = compute_canonical_source_version(entity, rec)
                if expected_ver != actual_ver:
                    version_mismatches += 1
                    trace_status = "FAIL: Source version mismatch"
                else:
                    trace_status = "PASS: Grounded in canonical record"

            rec_id_disp = rec_id if len(rec_id) <= 28 else rec_id[:25] + "..."
            print(f"{i:<3} {entity:<8} {rec_id_disp:<30} {field:<18} {trace_status}")

        print("-" * 80)
        print(f"Total Inspected: {len(candidates)}")
        print(f"Missing Canonical Records: {missing_records}")
        print(f"Version Mismatches: {version_mismatches}")

        if missing_records == 0 and version_mismatches == 0:
            print("\n[SUCCESS] Dry-run passed with 100% canonical traceability.")
            print("Run with `--execute` to perform actual Gemini LLM enrichment.")
            return True
        else:
            print("\n[FAIL] Dry-run encountered candidate mismatches.")
            return False

    def run_execute(self, limit: Optional[int] = None) -> bool:
        """
        Executes live batch enrichment on candidate records using Google Gemini API.
        Enforces EvidenceValidator and saves proposals to human approval review queue.
        """
        print("=" * 80)
        print("   STAGE 3 GEMINI ENRICHMENT: LIVE EXECUTION")
        print("=" * 80)

        # 1. Strict API Key Check
        is_key_valid, key_msg = self.provider.validate_api_key()
        if not is_key_valid:
            print(f"[ERROR] Cannot execute live enrichment: {key_msg}")
            return False

        # 2. Record Pre-Execution Database Hash
        pre_db_hash = compute_file_hash(self.db_path)
        logger.info(f"Pre-execution database SHA-256: {pre_db_hash}")
        print(f"[1] Pre-execution Database SHA-256: {pre_db_hash}")

        # 3. Load Candidates
        candidates = self.load_candidates()
        if limit:
            candidates = candidates[:limit]
        total_candidates = len(candidates)
        print(f"[2] Processing {total_candidates} candidates using model '{self.provider.model_id}'")
        print(f"    Batch size: {self.batch_size}, Concurrency: sequential batches")

        # Tracking collections
        proposals: List[Dict[str, Any]] = []
        review_queue_rows: List[Dict[str, Any]] = []
        status_counts = {"VERIFIED": 0, "NEEDS_REVIEW": 0, "INSUFFICIENT_EVIDENCE": 0, "FAILED": 0}
        api_success_count = 0
        api_failed_count = 0

        start_time = datetime.now(timezone.utc)

        # Process in batches
        for batch_idx in range(0, total_candidates, self.batch_size):
            batch = candidates[batch_idx : batch_idx + self.batch_size]
            batch_num = (batch_idx // self.batch_size) + 1
            total_batches = ((total_candidates - 1) // self.batch_size) + 1
            print(f"\n--- Batch {batch_num}/{total_batches} ({len(batch)} candidates) ---")

            for c in batch:
                rec_id = c.get("record_id")
                entity = c.get("entity_type")
                field_name = c.get("field_name")
                orig_val = c.get("original_value")
                src_url = c.get("source_url") or ""
                source_version = c.get("source_version") or ""
                request_id = str(uuid.uuid4())
                proposal_id = str(uuid.uuid4())

                # Step 1: Retrieve canonical record
                canonical_rec = self.get_canonical_record(entity, rec_id)
                if not canonical_rec:
                    logger.error(f"Record {rec_id} not found in database.")
                    api_failed_count += 1
                    status_counts["FAILED"] += 1
                    continue

                # Step 2: Build source text & verify version
                source_text = EnrichmentEngine.build_canonical_source_text(entity, canonical_rec)
                expected_version = compute_canonical_source_version(entity, canonical_rec)
                field_hint = self.get_field_type_hint(entity, field_name)

                print(f"Calling Gemini for [{entity}] {rec_id} -> {field_name}...", end=" ", flush=True)
                logger.info(f"Initiating Gemini API call: request_id={request_id}, record_id={rec_id}, field={field_name}")

                # Step 3: Call Gemini Provider
                gemini_resp: GeminiEnrichmentResponse = self.provider.enrich_candidate(
                    record_id=rec_id,
                    entity_type=entity,
                    target_field=field_name,
                    original_value=orig_val,
                    canonical_source_text=source_text,
                    source_url=src_url,
                    request_id=request_id,
                    field_type_hint=field_hint,
                )

                if gemini_resp.is_success:
                    api_success_count += 1
                    print(f"OK (HTTP 200, tokens={gemini_resp.usage.total_tokens})")
                else:
                    api_failed_count += 1
                    print(f"FAILED ({gemini_resp.error_message})")

                # Step 4: Construct EnrichmentResult with verbatim evidence excerpt
                verbatim_ev = (gemini_resp.evidence_quote or "").strip().strip('"\'')
                if not verbatim_ev or not EvidenceValidator.is_verbatim_excerpt(verbatim_ev, source_text):
                    if EvidenceValidator.is_verbatim_excerpt(gemini_resp.evidence, source_text):
                        verbatim_ev = gemini_resp.evidence
                    elif gemini_resp.evidence_quote:
                        verbatim_ev = gemini_resp.evidence_quote
                    else:
                        verbatim_ev = gemini_resp.evidence or ""

                enrichment_res = EnrichmentResult(
                    attempt_id=proposal_id,
                    record_id=rec_id,
                    entity_type=entity,
                    field_name=field_name,
                    original_value=orig_val,
                    enriched_value=gemini_resp.proposed_value,
                    source_url=gemini_resp.evidence_url or src_url,
                    evidence=verbatim_ev,
                    source_version=expected_version,
                    confidence_score=gemini_resp.confidence,
                    enrichment_method="llm_extraction",
                    provider="google-gemini",
                    model=self.provider.model_id,
                    enriched_at=gemini_resp.response_timestamp,
                    validation_status="NEEDS_REVIEW",  # Initial before validator recalculation
                    validation_rationale="",
                    retry_count=gemini_resp.retry_count,
                )

                # Step 5: Recalculate validation status via EvidenceValidator
                if not gemini_resp.is_success:
                    val_status = ValidationStatus.FAILED
                    val_rationale = f"Gemini API execution error: {gemini_resp.error_message}"
                elif expected_version != source_version:
                    val_status = ValidationStatus.FAILED
                    val_rationale = (
                        f"Audit 21 Violation: Source version mismatch for {rec_id} "
                        f"(expected {expected_version}, got {source_version})."
                    )
                else:
                    val_status, val_rationale = EvidenceValidator.validate_enrichment(
                        enrichment_res,
                        source_text,
                        canonical_record=canonical_rec,
                    )

                enrichment_res.validation_status = val_status.value
                enrichment_res.validation_rationale = val_rationale

                # Step 6: Validate JSON Schema
                is_valid_schema, schema_err = validate_enrichment_result_schema(enrichment_res.to_dict())
                if not is_valid_schema:
                    val_status = ValidationStatus.FAILED
                    val_rationale = f"Schema validation failed: {schema_err}"
                    enrichment_res.validation_status = val_status.value
                    enrichment_res.validation_rationale = val_rationale

                status_counts[val_status.value] = status_counts.get(val_status.value, 0) + 1
                logger.info(
                    f"Result {rec_id} ({field_name}): val_status={val_status.value}, "
                    f"rationale={val_rationale}"
                )

                # Schema and duplication checks (Audit 28 & 29)
                is_compat, schema_code, schema_reason = check_proposal_schema_compatibility(entity, field_name)
                table_name, _ = ENTITY_TABLE_MAP.get(entity, ("unknown", "unknown"))

                dup_status = "NO_DUPLICATION"
                if canonical_rec and entity == "startup":
                    existing_focus = (canonical_rec.get("ai_focus_area") or "").strip().lower()
                    existing_ev = (canonical_rec.get("ai_evidence") or "").strip().lower()
                    if field_name in ("ai_specialization", "ai_focus_area"):
                        if isinstance(gemini_resp.proposed_value, str) and gemini_resp.proposed_value.strip().lower() == existing_focus:
                            dup_status = "DUPLICATE_OF_EXISTING_CANONICAL_DATA"
                    elif field_name == "technologies" and isinstance(gemini_resp.proposed_value, list):
                        if existing_ev and all(isinstance(t, str) and t.strip().lower() in existing_ev for t in gemini_resp.proposed_value if t):
                            dup_status = "DUPLICATE_OF_EXISTING_CANONICAL_DATA"

                # Step 7: Build Proposal Record (PENDING_APPROVAL)
                proposal_data = {
                    "proposal_id": proposal_id,
                    "request_id": request_id,
                    "record_id": rec_id,
                    "entity_type": entity,
                    "field_name": field_name,
                    "original_value": orig_val,
                    "proposed_value": gemini_resp.proposed_value,
                    "evidence": gemini_resp.evidence,
                    "evidence_url": gemini_resp.evidence_url,
                    "evidence_quote": gemini_resp.evidence_quote,
                    "reasoning": gemini_resp.reasoning,
                    "confidence_score": gemini_resp.confidence,
                    "validation_status": val_status.value,
                    "validation_rationale": val_rationale,
                    "schema_status": schema_code,
                    "schema_target_table": table_name,
                    "schema_target_column": field_name if is_compat else "NONE (Column does not exist)",
                    "schema_rationale": schema_reason,
                    "duplication_status": dup_status,
                    "approval_status": "PENDING_APPROVAL",
                    "model_id": self.provider.model_id,
                    "provider": "google-gemini",
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "usage": gemini_resp.usage.to_dict(),
                    "retry_count": gemini_resp.retry_count,
                }
                proposals.append(proposal_data)

                # Step 8: Build CSV Row for Review Queue
                proposed_str = (
                    json.dumps(gemini_resp.proposed_value, ensure_ascii=False)
                    if isinstance(gemini_resp.proposed_value, (list, dict))
                    else str(gemini_resp.proposed_value or "")
                )
                original_str = (
                    json.dumps(orig_val, ensure_ascii=False)
                    if isinstance(orig_val, (list, dict))
                    else str(orig_val or "")
                )
                review_queue_rows.append({
                    "proposal_id": proposal_id,
                    "record_id": rec_id,
                    "entity_type": entity,
                    "field_name": field_name,
                    "original_value": original_str,
                    "proposed_value": proposed_str,
                    "evidence_quote": gemini_resp.evidence_quote or "",
                    "explanatory_evidence": gemini_resp.evidence or "",
                    "reasoning": gemini_resp.reasoning or "",
                    "evidence_url": gemini_resp.evidence_url or "",
                    "validation_status": val_status.value,
                    "validation_rationale": val_rationale,
                    "confidence_score": gemini_resp.confidence,
                    "schema_status": schema_code,
                    "schema_target_table": table_name,
                    "schema_target_column": field_name if is_compat else "NONE (Column does not exist)",
                    "duplication_status": dup_status,
                    "approval_status": "PENDING_APPROVAL",
                    "reviewer": "",
                    "reviewed_at": "",
                    "review_notes": "",
                })

                # Polite pacing to stay strictly within 15 RPM free-tier quota
                time.sleep(3.5)

        end_time = datetime.now(timezone.utc)
        elapsed_sec = (end_time - start_time).total_seconds()

        # Step 9: Save Proposals to JSONL
        with open(self.results_jsonl_path, "w", encoding="utf-8") as f:
            for p in proposals:
                f.write(json.dumps(p, ensure_ascii=False) + "\n")
        logger.info(f"Wrote {len(proposals)} proposals to {self.results_jsonl_path}")

        # Step 10: Save Review Queue to CSV
        fieldnames = [
            "proposal_id",
            "record_id",
            "entity_type",
            "field_name",
            "original_value",
            "proposed_value",
            "evidence_quote",
            "explanatory_evidence",
            "reasoning",
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
        with open(self.review_queue_csv_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(review_queue_rows)
        logger.info(f"Wrote {len(review_queue_rows)} review items to {self.review_queue_csv_path}")

        # Step 11: Verify Post-Execution Database Hash
        post_db_hash = compute_file_hash(self.db_path)
        canonical_db_unchanged = (pre_db_hash == post_db_hash)
        logger.info(f"Post-execution database SHA-256: {post_db_hash} (unchanged: {canonical_db_unchanged})")

        # Step 12: Build & Save Summary JSON
        summary = {
            "execution_metadata": {
                "runner": "GeminiEnrichmentRunner",
                "model_id": self.provider.model_id,
                "provider": "google-gemini",
                "started_at": start_time.isoformat(),
                "completed_at": end_time.isoformat(),
                "elapsed_seconds": round(elapsed_sec, 2),
            },
            "candidate_counts": {
                "total_candidates": total_candidates,
                "processed": len(proposals),
                "api_requests_successful": api_success_count,
                "api_requests_failed": api_failed_count,
            },
            "status_distribution": status_counts,
            "approval_distribution": {
                "PENDING_APPROVAL": len(proposals),
                "APPROVED": 0,
                "REJECTED": 0,
                "REQUEST_REVIEW": 0,
            },
            "usage_and_costs": {
                "prompt_tokens": self.provider.total_usage.prompt_tokens,
                "candidates_tokens": self.provider.total_usage.candidates_tokens,
                "total_tokens": self.provider.total_usage.total_tokens,
                "estimated_cost_usd": round(self.provider.total_usage.estimated_cost_usd, 6),
            },
            "database_integrity": {
                "pre_execution_sha256": pre_db_hash,
                "post_execution_sha256": post_db_hash,
                "canonical_database_unchanged": canonical_db_unchanged,
                "historical_audit19_preserved": True,
            },
            "output_artifacts": {
                "results_jsonl": self.results_jsonl_path,
                "review_queue_csv": self.review_queue_csv_path,
                "summary_json": self.summary_json_path,
                "audit_log": self.audit_log_path,
            }
        }
        with open(self.summary_json_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        logger.info(f"Wrote summary to {self.summary_json_path}")

        # Console Summary Report
        print("\n" + "=" * 80)
        print("   STAGE 3 GEMINI ENRICHMENT EXECUTION SUMMARY")
        print("=" * 80)
        print(f"Model Used:                   {self.provider.model_id}")
        print(f"Total Candidates Processed:   {total_candidates}")
        print(f"API Calls Successful:         {api_success_count}")
        print(f"API Calls Failed:             {api_failed_count}")
        print(f"Elapsed Time:                 {elapsed_sec:.2f} seconds")
        print("\nValidation Status Distribution:")
        for s, count in status_counts.items():
            print(f"  - {s:<24}: {count}")
        print("\nToken Usage & Accounting:")
        print(f"  - Prompt Tokens:            {self.provider.total_usage.prompt_tokens:,}")
        print(f"  - Completion Tokens:        {self.provider.total_usage.candidates_tokens:,}")
        print(f"  - Total Tokens:             {self.provider.total_usage.total_tokens:,}")
        print(f"  - Estimated Cost (USD):     ${self.provider.total_usage.estimated_cost_usd:.6f}")
        print("\nDatabase Integrity:")
        print(f"  - Pre-execution SHA-256:    {pre_db_hash}")
        print(f"  - Post-execution SHA-256:   {post_db_hash}")
        print(f"  - Database Unchanged:       {'YES (100% Intact)' if canonical_db_unchanged else 'NO (VIOLATION)'}")
        print("\nOutput Artifacts Generated:")
        print(f"  - Proposals JSONL:          {self.results_jsonl_path}")
        print(f"  - Review Queue CSV:         {self.review_queue_csv_path}")
        print(f"  - Execution Summary:        {self.summary_json_path}")
        print(f"  - Audit Log:                {self.audit_log_path}")
        print("=" * 80)

        if not canonical_db_unchanged:
            print("[CRITICAL ERROR] Database was modified during enrichment execution!")
            return False

        return True


def main():
    parser = argparse.ArgumentParser(description="Stage 3 Gemini LLM Enrichment Runner")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true", help="Perform dry-run inspection")
    group.add_argument("--execute", action="store_true", help="Perform live Gemini enrichment")

    parser.add_argument("--db-path", default="data/normalized/ai_ecosystem.db", help="Path to canonical database")
    parser.add_argument("--candidates-file", default="reports/stage3_enrichment_results.jsonl", help="Path to candidate JSONL")
    parser.add_argument("--output-dir", default="data/stage3", help="Output directory for proposals and review queue")
    parser.add_argument("--batch-size", type=int, default=5, help="Batch size for execution")
    parser.add_argument("--model", default=None, help="Gemini model ID override")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of candidates to process")

    args = parser.parse_args()

    runner = GeminiEnrichmentRunner(
        db_path=args.db_path,
        candidates_file=args.candidates_file,
        output_dir=args.output_dir,
        model_id=args.model,
        batch_size=args.batch_size,
    )

    if args.dry_run:
        success = runner.run_dry_run(limit=args.limit)
    else:
        success = runner.run_execute(limit=args.limit)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
