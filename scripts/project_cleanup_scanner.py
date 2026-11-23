"""
Project Cleanup Scanner & Analyzer for AI Ecosystem Intelligence Pipeline.
Performs recursive file scanning, SHA-256 hashing, duplicate detection,
AST import analysis, dependency mapping, and classification.
"""

import os
import sys
import ast
import csv
import json
import time
import hashlib
from datetime import datetime, timezone
from collections import defaultdict

WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(WORKSPACE_ROOT, "reports", "project_cleanup")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Four established database hashes that MUST be preserved
PROTECTED_DB_HASHES = {
    "Canonical DB": {
        "path": "data/normalized/ai_ecosystem.db",
        "sha256": "4949352d4f568f3f6128f398591cd8edac2eba45496c24535edb6c096398b95d"
    },
    "Authentic Audit19 DB": {
        "path": "source/audit19_original_database.db",
        "sha256": "1958c59f1a02e5a4bd274f114fdcfdd40942239f518eb662119962a263c84d4d"
    },
    "Baseline Working DB": {
        "path": "data/working/rolling_ai_ecosystem.db",
        "sha256": "cbc1814cf3c6546a4dfa1d2e731648aead070b133b38892ddd599a6e385c2127"
    },
    "Candidate Working DB": {
        "path": "data/working/candidate_rolling_ai_ecosystem.db",
        "sha256": "eca573b4a4f1c045f417883772308050418c2d471250be7fda6c68e1ec023198"
    }
}

def compute_sha256(filepath):
    try:
        h = hashlib.sha256()
        with open(filepath, "rb") as f:
            while chunk := f.read(65536):
                h.update(chunk)
        return h.hexdigest()
    except Exception as e:
        return f"ERROR: {e}"

def extract_python_imports(filepath):
    """Extracts imported module names using AST."""
    imports = set()
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            tree = ast.parse(f.read(), filename=filepath)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for n in node.names:
                    imports.add(n.name.split('.')[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module.split('.')[0])
    except Exception:
        pass
    return imports

def main():
    start_time = time.time()
    print("Starting recursive scan of workspace:", WORKSPACE_ROOT)

    all_files = []
    files_by_hash = defaultdict(list)
    import_map = defaultdict(set) # module_name -> set of files that import it
    all_py_files = []

    total_scanned_dirs = 0

    # 1. Walk entire directory tree
    for root, dirs, files in os.walk(WORKSPACE_ROOT):
        total_scanned_dirs += len(dirs)
        for f in files:
            full_path = os.path.join(root, f)
            rel_path = os.path.relpath(full_path, WORKSPACE_ROOT).replace("\\", "/")
            
            # Skip output files in reports/project_cleanup if running rerun
            if rel_path.startswith("reports/project_cleanup/"):
                continue

            try:
                stat = os.stat(full_path)
                size_bytes = stat.st_size
                mtime_str = datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat()
            except Exception as e:
                size_bytes = 0
                mtime_str = "UNKNOWN"

            ext = os.path.splitext(f)[1].lower()
            all_files.append({
                "rel_path": rel_path,
                "full_path": full_path,
                "filename": f,
                "extension": ext,
                "size_bytes": size_bytes,
                "last_modified": mtime_str,
            })

            if ext == ".py":
                all_py_files.append((rel_path, full_path))

    print(f"Scanned {len(all_files)} total files across {total_scanned_dirs} directories.")

    # 2. Extract AST imports from all python files
    print(f"Analyzing AST imports across {len(all_py_files)} Python files...")
    for rel_path, full_path in all_py_files:
        imported_modules = extract_python_imports(full_path)
        for mod in imported_modules:
            import_map[mod].add(rel_path)

    # 3. Compute hashes
    print("Computing SHA-256 digests...")
    for idx, f_info in enumerate(all_files):
        if idx % 1000 == 0:
            print(f"  Processed {idx}/{len(all_files)} files...")
        h = compute_sha256(f_info["full_path"])
        f_info["sha256"] = h
        files_by_hash[h].append(f_info["rel_path"])

    print(f"Hashing complete. Unique hashes: {len(files_by_hash)}")

    # 4. Identify Duplicate Files
    duplicate_rows = []
    for h, paths in files_by_hash.items():
        if len(paths) > 1 and not h.startswith("ERROR:"):
            # Sort paths: authoritative copy preferred in core/data/source/config
            def path_priority(p):
                if p.startswith("data/normalized/"): return 0
                if p.startswith("source/"): return 1
                if p.startswith("data/working/"): return 2
                if p.startswith("core/"): return 3
                if p.startswith("config/"): return 4
                if p.startswith("sources/"): return 5
                if p.startswith("src/"): return 6
                if p.startswith("scripts/"): return 7
                if p.startswith("reports/"): return 8
                if "PACKAGE" in p: return 11
                return 9

            sorted_paths = sorted(paths, key=path_priority)
            canonical_path = sorted_paths[0]
            for dup_path in sorted_paths[1:]:
                sz = next((x["size_bytes"] for x in all_files if x["rel_path"] == dup_path), 0)
                duplicate_rows.append({
                    "sha256": h,
                    "original_path": canonical_path,
                    "duplicate_path": dup_path,
                    "file_size": sz,
                    "action": "ARCHIVE" if "PACKAGE" in dup_path else "MERGE",
                    "notes": f"Identical content to {canonical_path}"
                })

    print(f"Identified {len(duplicate_rows)} duplicate file instances.")

    # 5. Classify every file into one of A-K
    inventory_rows = []
    classification_rows = []

    for f_info in all_files:
        p = f_info["rel_path"]
        fn = f_info["filename"]
        ext = f_info["extension"]
        sz = f_info["size_bytes"]
        h = f_info["sha256"]
        mtime = f_info["last_modified"]

        base_mod = os.path.splitext(fn)[0]
        is_imported = False
        if base_mod in import_map or (p.startswith("core/") and base_mod in import_map):
            is_imported = True

        is_referenced_config = False
        if any(term in p for term in ["google_sheets", "sources_config", "ecosystem", "rolling"]):
            is_referenced_config = True

        category = "UNKNOWN_REQUIRES_REVIEW"
        action = "MANUAL_REVIEW"
        proposed_dest = p
        justification = ""
        risk_level = "LOW"
        reversibility = "YES"
        req_for_prod = "No"
        safe_to_archive = "No"
        purpose = ""

        # Classification Rules:
        # 1. PROTECTED DATABASES
        if p in [item["path"] for item in PROTECTED_DB_HASHES.values()]:
            category = "DATABASE_AND_DATA"
            action = "KEEP"
            purpose = "Protected canonical or working database baseline"
            justification = "Critical immutable dataset baseline. Mandatory protection."
            risk_level = "CRITICAL"
            reversibility = "NO"
            req_for_prod = "Yes"
            safe_to_archive = "No"

        # 2. SECURITY SENSITIVE
        elif p.startswith("secrets/") or p in [".env", ".env.local"] or "client_secret" in fn or "oauth_client" in fn or "token.json" in fn:
            category = "SECURITY_SENSITIVE"
            action = "KEEP"
            purpose = "OAuth 2.0 Desktop credentials, access/refresh tokens, or environment secrets"
            justification = "Authentication secret required for Google Sheets integration. Excluded from Git."
            risk_level = "CRITICAL"
            reversibility = "NO"
            req_for_prod = "Yes"
            safe_to_archive = "No"

        # 3. CONFIGURATION
        elif p.startswith("config/") or fn in [".env.example", ".gitignore", "crontab.txt", "settings.json"]:
            category = "CONFIGURATION"
            action = "KEEP"
            purpose = "System, scheduler, API, or IDE configuration"
            justification = "Configuration file required for pipeline execution and deployment."
            risk_level = "MEDIUM"
            reversibility = "YES"
            req_for_prod = "Yes"
            safe_to_archive = "No"

        # 4. ESSENTIAL PRODUCTION MODULES
        elif p == "main.py" or p.startswith("core/") or p.startswith("sources/") or p.startswith("src/") or p.startswith("deploy/") or fn == "requirements.txt":
            category = "ESSENTIAL_PRODUCTION"
            action = "KEEP"
            purpose = "Core pipeline engine, data collector, schema definition, or Stage 3 enrichment component"
            justification = "Essential production module actively running the pipeline, Stage 3 enrichment, or Sheets sync."
            risk_level = "HIGH"
            reversibility = "YES"
            req_for_prod = "Yes"
            safe_to_archive = "No"

        # 5. ACTIVE EXECUTION & MAINTENANCE SCRIPTS
        elif p in [
            "scripts/execute_authorized_sync.py",
            "scripts/setup_google_oauth.py",
            "scripts/validate_oauth_credentials.py",
            "scripts/check_sheet_dimensions.py",
            "scripts/verify_clock_and_kpis.py",
            "scripts/verify_final_closeout_package.py",
            "scripts/verify_checksums.py",
            "scripts/verify_baseline_and_backup.py"
        ]:
            category = "ESSENTIAL_PRODUCTION"
            action = "KEEP"
            purpose = "Active synchronization, authentication, or critical verification script"
            justification = "Production entrypoint or gatekeeper verification script."
            risk_level = "HIGH"
            reversibility = "YES"
            req_for_prod = "Yes"
            safe_to_archive = "No"

        # 6. TESTING
        elif p.startswith("tests/") and ext == ".py":
            category = "TESTING"
            action = "KEEP"
            purpose = "Unit, integration, regression, or audit verification test suite"
            justification = "Verification test suite ensuring data integrity, schema validity, and recovery."
            risk_level = "MEDIUM"
            reversibility = "YES"
            req_for_prod = "No"
            safe_to_archive = "No"

        # 7. TEMPORARY & BYTECODE CACHE
        elif "__pycache__" in p or ext in [".pyc", ".pyo", ".pyd"] or fn.startswith("~") or p.endswith(".tmp"):
            category = "TEMPORARY"
            action = "DELETE_CANDIDATE"
            purpose = "Python bytecode cache or temporary execution artifact"
            justification = "Automatically re-generable bytecode cache. Safe to delete."
            risk_level = "NONE"
            reversibility = "YES"
            req_for_prod = "No"
            safe_to_archive = "No"

        # 8. FORMAL HISTORICAL REPORTS DIRECTORY (reports/)
        elif p.startswith("reports/"):
            category = "HISTORICAL_EVIDENCE"
            action = "KEEP"
            purpose = "Authoritative Phase I–IV audit report, reconciliation ledger, or validation export"
            justification = "Mandatory historical audit evidence documenting Phases I–IV data quality."
            risk_level = "LOW"
            reversibility = "YES"
            req_for_prod = "No"
            safe_to_archive = "No"

        # 9. HISTORICAL AUDIT PACKAGES & EVIDENCE ZIPS
        elif (
            "PACKAGE" in p or "deliverables_audit22" in p or ext == ".zip" or
            fn.startswith("AUDIT") or fn.startswith("audit") or fn.startswith("FINAL_PROJECT") or
            fn.startswith("PHASE_") or fn.startswith("STAGE3_") or "audit19" in fn or
            "manifest" in fn or fn == "submission_inventory.csv" or fn == "SIX_MONTH_ROLLING_PIPELINE_REPORT.md"
        ):
            if any(r["duplicate_path"] == p for r in duplicate_rows):
                category = "DUPLICATE"
                action = "ARCHIVE"
                proposed_dest = f"archive/historical_snapshots/{p}"
                purpose = "Historical audit package snapshot copy of existing repository file"
                justification = "Duplicate copy preserved within an audit freeze snapshot folder. Safe to consolidate into archive/."
                risk_level = "LOW"
                reversibility = "YES"
                req_for_prod = "No"
                safe_to_archive = "Yes"
            elif ext in [".md", ".txt", ".csv", ".json", ".sha256"]:
                category = "HISTORICAL_EVIDENCE"
                action = "ARCHIVE"
                proposed_dest = f"archive/audit_reports/{fn}"
                purpose = "Formal audit report, reconciliation artifact, evidence export, or run log in root"
                justification = "Historical audit document in root directory. Proposed to move into structured archive."
                risk_level = "LOW"
                reversibility = "YES"
                req_for_prod = "No"
                safe_to_archive = "Yes"
            elif ext in [".db", ".zip"]:
                category = "HISTORICAL_EVIDENCE"
                action = "ARCHIVE"
                proposed_dest = f"archive/package_bundles/{fn}"
                purpose = "Historical frozen package zip bundle or audit point-in-time database"
                justification = "Audit recovery package or freeze snapshot bundle. Move to archive/ to clean root."
                risk_level = "LOW"
                reversibility = "YES"
                req_for_prod = "No"
                safe_to_archive = "Yes"
            else:
                category = "HISTORICAL_EVIDENCE"
                action = "ARCHIVE"
                proposed_dest = f"archive/historical_misc/{fn}"
                purpose = "Audit milestone evidence or package artifact"
                justification = "Audit archive component."
                risk_level = "LOW"
                reversibility = "YES"
                req_for_prod = "No"
                safe_to_archive = "Yes"

        # 10. DOCUMENTATION IN ROOT
        elif ext == ".md" and fn in ["README.md", "README_AUDIT23.md", "README_AUDIT25.md", "daily_collection_report.md"]:
            category = "DOCUMENTATION"
            action = "KEEP"
            purpose = "Project architecture and engineering documentation"
            justification = "Authoritative project overview and instructions."
            risk_level = "LOW"
            reversibility = "YES"
            req_for_prod = "No"
            safe_to_archive = "No"

        # 11. OBSOLETE SCRIPTS
        elif p.startswith("scripts/") and (
            "apply_stage2_corrections_v" in fn or
            "analyze_" in fn or
            "audit10_" in fn or "audit13_" in fn or "audit14_" in fn or "audit15_" in fn or
            "test_output" in fn or "user_request" in fn
        ):
            category = "OBSOLETE"
            action = "ARCHIVE"
            proposed_dest = f"archive/legacy_scripts/{fn}"
            purpose = "One-off historical correction, target analysis, or debug script"
            justification = "Functionality completed and superseded in database baseline. Archive for historical provenance."
            risk_level = "LOW"
            reversibility = "YES"
            req_for_prod = "No"
            safe_to_archive = "Yes"

        # 12. REMAINING DATA FILES IN data/ or source/
        elif p.startswith("data/") or p.startswith("source/"):
            category = "DATABASE_AND_DATA"
            action = "KEEP"
            purpose = "Pipeline data artifact, backup, or recovery ledger"
            justification = "Data artifact associated with pipeline state."
            risk_level = "MEDIUM"
            reversibility = "YES"
            req_for_prod = "Yes" if "candidate" in p or "normalized" in p else "No"
            safe_to_archive = "No"

        # 13. AUDIT SCRIPTS IN scripts/
        elif p.startswith("scripts/"):
            category = "HISTORICAL_EVIDENCE"
            action = "ARCHIVE"
            proposed_dest = f"archive/audit_scripts/{fn}"
            purpose = "Audit verification or diagnostic utility script"
            justification = "One-time audit tool used during earlier audit cycles."
            risk_level = "LOW"
            reversibility = "YES"
            req_for_prod = "No"
            safe_to_archive = "Yes"

        # DEFAULT UNKNOWN
        else:
            category = "UNKNOWN_REQUIRES_REVIEW"
            action = "MANUAL_REVIEW"
            proposed_dest = p
            purpose = "Unclassified file requiring manual review"
            justification = "Requires explicit inspection prior to any reorganization."
            risk_level = "MEDIUM"
            reversibility = "YES"
            req_for_prod = "No"
            safe_to_archive = "No"

        inventory_rows.append({
            "relative_path": p,
            "filename": fn,
            "extension": ext,
            "size_bytes": sz,
            "last_modified": mtime,
            "sha256": h,
            "category": category,
            "purpose": purpose,
            "referenced_by_imports": "Yes" if is_imported else "No",
            "referenced_by_config": "Yes" if is_referenced_config else "No",
            "referenced_by_scripts": "Yes" if p.startswith("core/") or p.startswith("sources/") or p.startswith("src/") else "No",
            "required_for_production": req_for_prod,
            "safe_to_archive": safe_to_archive
        })

        classification_rows.append({
            "relative_path": p,
            "filename": fn,
            "category": category,
            "action": action,
            "proposed_destination": proposed_dest,
            "justification": justification,
            "risk_level": risk_level,
            "reversibility": reversibility
        })

    # 6. Write CSV Reports
    print("\nWriting project_inventory.csv...")
    inv_file = os.path.join(OUTPUT_DIR, "project_inventory.csv")
    with open(inv_file, "w", newline="", encoding="utf-8") as f:
        fieldnames = [
            "relative_path", "filename", "extension", "size_bytes", "last_modified",
            "sha256", "category", "purpose", "referenced_by_imports", "referenced_by_config",
            "referenced_by_scripts", "required_for_production", "safe_to_archive"
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(inventory_rows)

    print("Writing project_classification.csv...")
    class_file = os.path.join(OUTPUT_DIR, "project_classification.csv")
    with open(class_file, "w", newline="", encoding="utf-8") as f:
        fieldnames = [
            "relative_path", "filename", "category", "action", "proposed_destination",
            "justification", "risk_level", "reversibility"
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(classification_rows)

    print("Writing duplicate_files.csv...")
    dup_file = os.path.join(OUTPUT_DIR, "duplicate_files.csv")
    with open(dup_file, "w", newline="", encoding="utf-8") as f:
        fieldnames = ["sha256", "original_path", "duplicate_path", "file_size", "action", "notes"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(duplicate_rows)

    # 7. Write Protected Files Manifest
    print("Writing protected_files_manifest.json...")
    manifest_file = os.path.join(OUTPUT_DIR, "protected_files_manifest.json")
    
    protected_manifest = {
        "manifest_version": "1.0",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "description": "Authoritative manifest of protected canonical databases, working databases, and sensitive assets.",
        "protected_databases": {},
        "protected_security_assets": [
            "secrets/google_oauth_client.json",
            "secrets/google_sheets_token.json",
            ".env"
        ],
        "protected_core_modules": [
            "core/canonical.py",
            "core/daily_pipeline.py",
            "core/deduplicator.py",
            "core/engine.py",
            "core/enrichment.py",
            "core/entity_resolution.py",
            "core/env_loader.py",
            "core/freshness_engine.py",
            "core/github_client.py",
            "core/google_sheets_client.py",
            "core/job_schemas.py",
            "core/models.py",
            "core/news_schemas.py",
            "core/paper_github_pipeline.py",
            "core/registry.py",
            "core/rolling_window.py",
            "core/scheduler.py",
            "core/schemas.py",
            "core/sheets_dashboard_builder.py",
            "core/sheets_data_dictionary.py",
            "core/sheets_sync_engine.py",
            "core/sheets_transformer.py",
            "core/storage.py",
            "core/working_database.py",
            "main.py",
            "requirements.txt"
        ]
    }

    for name, info in PROTECTED_DB_HASHES.items():
        actual_h = compute_sha256(os.path.join(WORKSPACE_ROOT, info["path"]))
        protected_manifest["protected_databases"][name] = {
            "path": info["path"],
            "expected_sha256": info["sha256"],
            "verified_sha256": actual_h,
            "status": "VERIFIED_BIT_FOR_BIT_MATCH" if actual_h == info["sha256"] else "HASH_MISMATCH"
        }

    with open(manifest_file, "w", encoding="utf-8") as f:
        json.dump(protected_manifest, f, indent=2)

    cat_counts = defaultdict(int)
    action_counts = defaultdict(int)
    for r in classification_rows:
        cat_counts[r["category"]] += 1
        action_counts[r["action"]] += 1

    elapsed = round(time.time() - start_time, 2)
    print("\n" + "=" * 80)
    print("PROJECT SCAN & CLASSIFICATION SUMMARY")
    print("=" * 80)
    print(f"Total Files Scanned      : {len(all_files)}")
    print(f"Total Folders Scanned    : {total_scanned_dirs}")
    print(f"Elapsed Scanning Time    : {elapsed} seconds")
    print("\nFiles by Category:")
    for cat, cnt in sorted(cat_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {cat:<25}: {cnt:>5} files")
    print("\nFiles by Proposed Action:")
    for act, cnt in sorted(action_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {act:<25}: {cnt:>5} files")
    print(f"\nDuplicate Files Detected : {len(duplicate_rows)}")
    print("=" * 80)

if __name__ == "__main__":
    main()
