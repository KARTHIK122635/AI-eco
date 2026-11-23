import os
import json
import hashlib
from datetime import datetime, timezone

def generate_manifest():
    files = [
        "data/normalized/ai_ecosystem.db",
        "source/audit19_original_database.db",
        "reports/audit19_original_baseline.db",
        "reports/audit19_recovery_source_bundle.zip",
        "reports/audit19_original_366_records.json",
        "reports/audit19_to_audit23_reconciliation.csv",
        "reports/audit26_corrected.db",
        "reports/stage3_enrichment_results.jsonl",
        "reports/stage3_review_queue.csv",
        "reports/stage3_provider_usage.json",
        "reports/stage3_enrichment_summary.json",
        "reports/stage3_validation_report.md",
        "reports/stage3_enrichment_report.md",
        "reports/history_preservation_report.md",
        "core/enrichment/validator.py",
        "core/enrichment/schemas.py",
        "core/enrichment/schema_validator.py",
        "core/enrichment/engine.py",
        "core/llm/providers/offline_provider.py",
        "scripts/verify_audit26_stage3.py",
        "scripts/run_audit26_negative_tests.py",
        "tests/test_evidence_validator.py",
        "tests/test_persistence_and_logging.py",
        "tests/test_pipeline_integration.py",
        "tests/test_audit26_negative_authenticity.py"
    ]

    manifest = {
        "manifest_version": "2.6.0",
        "audit": "Audit 26",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "files": {}
    }

    for fpath in sorted(files):
        if os.path.exists(fpath):
            h = hashlib.sha256()
            with open(fpath, "rb") as f:
                while chunk := f.read(65536):
                    h.update(chunk)
            manifest["files"][fpath] = {
                "sha256": h.hexdigest(),
                "size_bytes": os.path.getsize(fpath)
            }
        else:
            print(f"Warning: {fpath} does not exist!")

    for out_path in ["reports/stage3_file_manifest.json", "reports/audit26_file_manifest.json"]:
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)
        print(f"Manifest written to {out_path} with {len(manifest['files'])} entries.")

if __name__ == '__main__':
    generate_manifest()
