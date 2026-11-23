"""
CLI Entrypoint and Runner for Phase II — Stage 3: LLM Fallback and Enrichment.
Phase II - Stage 3: LLM Fallback and Enrichment
Audit 19 - Multi-Table Persistence, Verification, and Reporting
"""

import os
import sys
sys.path.insert(0, os.path.abspath('.'))
import argparse
import json
import logging
from datetime import datetime, timezone

from core.llm.factory import get_llm_provider
from core.enrichment.engine import EnrichmentEngine

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("Stage3Runner")


def main():
    parser = argparse.ArgumentParser(description="Run Stage 3 LLM Fallback and Enrichment Pipeline")
    parser.add_argument("--provider", type=str, default=None, help="LLM Provider (gemini, openai, groq, ollama, offline)")
    parser.add_argument("--model", type=str, default=None, help="Specific model name override")
    parser.add_argument("--sample-per-entity", type=int, default=10, help="Number of incomplete candidates to sample per entity (default: 10)")
    parser.add_argument("--db-path", type=str, default="data/normalized/ai_ecosystem.db", help="Path to normalized SQLite database")
    parser.add_argument("--reset-stage3-tables", action="store_true", default=False, help="Explicitly reset Stage 3 enrichment tables (default preserves append-only history)")
    parser.add_argument("--dry-run", action="store_true", help="Run without persisting to SQLite tables")
    args = parser.parse_args()

    print("=" * 75)
    print("   PHASE II — STAGE 3: LLM FALLBACK AND ENRICHMENT PIPELINE (AUDIT 21)")
    print("=" * 75)

    if args.reset_stage3_tables and not args.dry_run:
        import sqlite3
        conn = sqlite3.connect(args.db_path)
        cur = conn.cursor()
        backup_ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        print(f"[0] Reset requested with backup timestamp: {backup_ts}")
        
        # Audit 21 Requirement 4: Back up tables and NEVER drop enrichment_audit_log
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='enrichment_audit_log'")
        if cur.fetchone():
            cur.execute(f"CREATE TABLE IF NOT EXISTS enrichment_audit_log_backup_{backup_ts} AS SELECT * FROM enrichment_audit_log")
            print(f"  - Preserved and backed up 'enrichment_audit_log' to 'enrichment_audit_log_backup_{backup_ts}'")

        for tbl in ["llm_enrichment_results", "llm_enrichment_logs", "llm_provider_usage", "llm_review_queue"]:
            cur.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{tbl}'")
            if cur.fetchone():
                cur.execute(f"CREATE TABLE IF NOT EXISTS {tbl}_backup_{backup_ts} AS SELECT * FROM {tbl}")
                cur.execute(f"DROP TABLE IF EXISTS {tbl}")
                print(f"  - Backed up and reset '{tbl}'")

        conn.commit()
        conn.close()
        print("[0] Safely backed up previous tables; legacy enrichment_audit_log preserved.")

    # 1. Initialize provider
    provider = get_llm_provider(
        provider_name=args.provider,
        model_name=args.model
    )
    print(f"\n[1] LLM Provider Initialized:")
    print(f"  - Provider: {provider.name}")
    print(f"  - Model:    {provider.model}")
    print(f"  - Status:   {'Active & Available' if provider.is_available() else 'Offline / Degraded'}")

    # 2. Initialize Enrichment Engine
    engine = EnrichmentEngine(
        provider=provider,
        db_path=args.db_path
    )

    # 3. Execute Pipeline
    print(f"\n[2] Executing Enrichment Pipeline (sample_per_entity={args.sample_per_entity}, dry_run={args.dry_run})...")
    summary = engine.run_enrichment_pipeline(
        sample_per_entity=args.sample_per_entity,
        save_to_db=not args.dry_run
    )

    # 4. Display Results
    print(f"\n[3] Pipeline Summary:")
    print(f"  - Total Enrichment Operations: {summary['enrichment_metrics']['total_enrichment_operations']}")
    print(f"  - Status Breakdown:")
    for status, count in summary['enrichment_metrics']['validation_status_breakdown'].items():
        print(f"      * {status:25s}: {count:5d}")
    print(f"  - Entity Breakdown:")
    for ent, count in summary['enrichment_metrics']['entity_type_breakdown'].items():
        print(f"      * {ent:25s}: {count:5d}")
    print(f"  - Token Usage:")
    u = summary['cumulative_token_usage']
    print(f"      * Prompt Tokens:     {u['prompt_tokens']:,}")
    print(f"      * Completion Tokens: {u['completion_tokens']:,}")
    print(f"      * Total Tokens:      {u['total_tokens']:,}")
    print(f"      * Estimated Cost:    ${u['estimated_cost_usd']:.4f}")

    print("\n[4] Output Artifacts:")
    print(f"  - Results JSONL:       reports/stage3_enrichment_results.jsonl")
    print(f"  - Summary JSON:        reports/stage3_enrichment_summary.json")
    print(f"  - Provider Usage JSON: reports/stage3_provider_usage.json")
    print(f"  - Review Queue CSV:    reports/stage3_review_queue.csv")
    print(f"  - Validation MD:       reports/stage3_validation_report.md")
    print(f"  - Enrichment MD:       reports/stage3_enrichment_report.md")
    print(f"  - File Manifest JSON:  reports/stage3_file_manifest.json")
    if not args.dry_run:
        print(f"  - SQLite Multi-Table:  {args.db_path} (llm_enrichment_results, llm_enrichment_logs, llm_provider_usage, llm_review_queue)")

    print("\n" + "=" * 75)
    print("   STAGE 3 AUDIT 19 PIPELINE COMPLETED SUCCESSFULLY")
    print("=" * 75)


if __name__ == "__main__":
    main()
