# AI Ecosystem Intelligence Pipeline — Comprehensive Project Cleanup Plan

**Project**: Six-Month Rolling AI Ecosystem Intelligence Pipeline  
**Document**: Operational Cleanup Plan & Reorganization Blueprint  
**Date**: 2026-11-23  
**Status**: Ready for User Review & Explicit Approval (Zero Files Modified)  

---

## 1. Operational Overview & Safety Constraints

This cleanup plan defines the phased, reversible reorganization of the AI Ecosystem Intelligence Pipeline. 

### Mandatory Governance Constraints
- **ZERO FILE MODIFICATIONS IN THIS TURN**: In accordance with the prompt's instructions, no files have been moved, renamed, merged, or deleted.
- **DATABASE IMMUTABILITY**: All four database SHA-256 hashes must remain bit-for-bit identical across all cleanup operations:
  - Canonical DB (`data/normalized/ai_ecosystem.db`): `4949352d4f568f3f6128f398591cd8edac2eba45496c24535edb6c096398b95d`
  - Authentic Audit19 DB (`source/audit19_original_database.db`): `1958c59f1a02e5a4bd274f114fdcfdd40942239f518eb662119962a263c84d4d`
  - Baseline Working DB (`data/working/rolling_ai_ecosystem.db`): `cbc1814cf3c6546a4dfa1d2e731648aead070b133b38892ddd599a6e385c2127`
  - Candidate Working DB (`data/working/candidate_rolling_ai_ecosystem.db`): `eca573b4a4f1c045f417883772308050418c2d471250be7fda6c68e1ec023198`
- **PROPOSALS PRESERVATION**: All 20 proposals in `candidate_rolling_ai_ecosystem.db` remain in `PENDING_APPROVAL`.
- **EVIDENCE PRESERVATION**: Zero historical audit reports, verification outputs, or manifests will be destroyed.

---

## 2. Inventory & Action Summary

| Action Code | Description | File Count | Disk Space Impact | Risk Level | Execution State |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **KEEP** | Remain in current active location | **435** | 280 MB | Critical / High / Medium | **HELD (UNTOUCHED)** |
| **ARCHIVE** | Move to structured subdirectories in `archive/` | **4,462** | 1,640 MB | Low | **PENDING USER APPROVAL** |
| **DELETE_CANDIDATE** | Ephemeral bytecode caches (`__pycache__`, `*.pyc`) | **432** | 38 MB | None (Auto-regenerable) | **HELD (UNTOUCHED)** |
| **TOTAL** | | **5,329** | **1,958 MB** | | **ZERO MODIFICATIONS** |

---

## 3. Detailed Action Breakdown by Functional Group

### Group 1: Essential Production Code & Core Modules (Action: `KEEP`)
- **File Count**: 144 files
- **Locations**: `core/`, `sources/`, `src/stage3/`, `deploy/`, `main.py`, `requirements.txt`
- **Dependency Analysis**: Core pipeline orchestrator, data collectors, Google Sheets integration client, database engines, schema definitions.
- **Risk Level**: **CRITICAL / HIGH**
- **Action**: Retain in current locations. Ensure zero disruption to Python import paths.

### Group 2: Configuration & Credentials (Action: `KEEP`)
- **File Count**: 15 files (11 Configuration + 4 Security Sensitive)
- **Locations**: `config/`, `secrets/`, `.env`, `.env.example`, `.gitignore`, `crontab.txt`, `.vscode/settings.json`
- **Dependency Analysis**: Required for OAuth Desktop authentication, scheduler configuration, rate limits, and Git exclusions.
- **Risk Level**: **CRITICAL**
- **Action**: Retain in current locations. Maintain strict exclusion of `secrets/` and `.env` from Git.

### Group 3: Active Testing & Verification Suites (Action: `KEEP`)
- **File Count**: 20 files
- **Location**: `tests/*.py`
- **Dependency Analysis**: Master integration test, schema compliance suites, recovery regression test suites (test_audit30 through test_audit38b).
- **Risk Level**: **MEDIUM**
- **Action**: Retain in `tests/` directory to preserve automated test discovery via `pytest` and `unittest`.

### Group 4: Canonical, Working & Archive Databases (Action: `KEEP`)
- **File Count**: 69 files
- **Locations**: `data/normalized/`, `source/`, `data/working/`, `data/backups/`, `data/recovery/`
- **Dependency Analysis**: Four protected database assets + point-in-time recovery ledgers and backups.
- **Risk Level**: **CRITICAL**
- **Action**: Retain in existing locations. SHA-256 hashes must be verified before and after any operational maintenance.

### Group 5: Authoritative Phase I–IV Reports (Action: `KEEP`)
- **File Count**: 187 files
- **Location**: `reports/`
- **Dependency Analysis**: Formal audit reports, API connectivity ledgers, historical table exports, and Phase IV integration verification reports.
- **Risk Level**: **LOW**
- **Action**: Retain in `reports/` as the single authoritative repository for audit documentation.

---

### Group 6: Root-Level Package Zip Bundles (Action: `ARCHIVE`)
- **File Count**: 18 zip files (approx. 450 MB)
- **Original Path**: Project root (`AUDIT31_CORRECTIVE_PACKAGE.zip`, `AUDIT32_FINAL_PACKAGE.zip`, ..., `FINAL_PROJECT_CLOSEOUT_PACKAGE.zip`, `SIX_MONTH_ROLLING_AI_ECOSYSTEM_PACKAGE.zip`, etc.)
- **Proposed Destination**: `archive/package_bundles/<filename>`
- **Reason**: Clutters the repository root. These are frozen, static snapshots created at the conclusion of historical audit milestones.
- **Dependency Analysis**: Not referenced by any active Python module or execution workflow.
- **Risk Level**: **LOW**
- **Reversibility**: **YES** (Can be moved back to root in seconds).

### Group 7: Unpacked Historical Package Folders (Action: `ARCHIVE` / `CONSOLIDATE`)
- **File Count**: 3,814 files (approx. 980 MB)
- **Original Paths**:
  - `AUDIT38_FINAL_PACKAGE/` (752 files)
  - `AUDIT38A_FINAL_PACKAGE/` (792 files)
  - `AUDIT38B_FINAL_PACKAGE/` (815 files)
  - `FINAL_PROJECT_CLOSEOUT_PACKAGE/` (823 files)
  - `SIX_MONTH_ROLLING_AI_ECOSYSTEM_PACKAGE/` (637 files)
- **Proposed Destination**: `archive/historical_snapshots/<folder_name>/`
- **Reason**: These folders were created as standalone export bundles containing full duplicated copies of the entire project tree, databases, and scripts. Over 99% of their files are exact byte-for-byte duplicates of canonical files.
- **Dependency Analysis**: Zero production code imports from these folders.
- **Risk Level**: **LOW**
- **Reversibility**: **YES** (Folder move).

### Group 8: Root-Level Audit Reports & Text Outputs (Action: `ARCHIVE`)
- **File Count**: 58 files
- **Original Path**: Project root (`AUDIT31_CORRECTION_REPORT.md`, `audit38_test_runner_output.txt`, `file_manifest.json`, etc.)
- **Proposed Destination**: `archive/audit_reports/<filename>`
- **Reason**: Point-in-time audit reports and test logs that were written directly to the project root during audit passes.
- **Dependency Analysis**: Not referenced by active runtime code.
- **Risk Level**: **LOW**
- **Reversibility**: **YES**.

### Group 9: Obsolete & Legacy Scripts in `scripts/` (Action: `ARCHIVE`)
- **File Count**: 870 files
- **Original Path**: `scripts/<legacy_script>.py`
  - Examples: `apply_stage2_corrections_v3.py` .. `v15.py`, `analyze_117_uncertain_details.py`, `analyze_73_candidates.py`, `audit10_uncertain_data.py`, `verify_audit5_comprehensive.py` .. `verify_audit26_stage3.py`.
- **Proposed Destination**: `archive/legacy_scripts/<filename>`
- **Reason**: Ad-hoc patch and exploration scripts from Audits 1–29 whose functionality was permanently merged into canonical database baselines.
- **Dependency Analysis**: Not referenced by active entry points or daily pipeline.
- **Risk Level**: **LOW**
- **Reversibility**: **YES**.

---

### Group 10: Ephemeral Bytecode Caches (Action: `DELETE_CANDIDATE`)
- **File Count**: 432 files (approx. 38 MB)
- **Original Path**: `__pycache__/*.pyc`, `core/__pycache__/*.pyc`, `sources/__pycache__/*.pyc`, `tests/__pycache__/*.pyc`
- **Proposed Destination**: N/A (Deletion candidate)
- **Reason**: Automatically generated Python bytecode cache files.
- **Dependency Analysis**: None. Python automatically recompiles bytecode on execution.
- **Risk Level**: **NONE**
- **Reversibility**: **YES** (Recreated automatically on next execution).
- **Execution Status**: **HELD (NOT DELETED)**. Per prompt instructions, `DELETE_CANDIDATE` actions are not executed during this first pass.

---

## 4. Step-by-Step Cleanup Execution Protocol (Upon Approval)

When explicit approval is granted, cleanup will follow this strict protocol:

1. **Pre-Cleanup Integrity Snapshot**:
   - Verify SHA-256 hashes of all four databases.
   - Record row counts across all SQLite tables.
2. **Directory Structure Creation**:
   - Create `archive/package_bundles/`, `archive/historical_snapshots/`, `archive/legacy_scripts/`, `archive/audit_reports/`.
3. **Phase A: Move Root Zip Bundles to `archive/package_bundles/`**:
   - 18 `.zip` files moved. Zero file deletions.
4. **Phase B: Move Unpacked Snapshot Folders to `archive/historical_snapshots/`**:
   - Move `AUDIT38_FINAL_PACKAGE/`, `AUDIT38A_FINAL_PACKAGE/`, `AUDIT38B_FINAL_PACKAGE/`, `FINAL_PROJECT_CLOSEOUT_PACKAGE/`, `SIX_MONTH_ROLLING_AI_ECOSYSTEM_PACKAGE/`.
5. **Phase C: Move Root Audit Reports to `archive/audit_reports/`**:
   - Move loose `AUDIT*.md`, `audit*.txt`, `audit*.csv`, and root `*manifest*` files.
6. **Phase D: Relocate Legacy Audit Scripts to `archive/legacy_scripts/`**:
   - Move obsolete `apply_stage2_corrections_v*.py` and historical audit probes.
7. **Phase E: Clear Bytecode Cache (`__pycache__`)**:
   - Delete `.pyc` cache files across all directories.
8. **Post-Cleanup Integrity Audit**:
   - Verify bit-for-bit match on all four database SHA-256 hashes.
   - Execute `tests/test_pipeline_integration.py` to confirm zero regression.
   - Verify Google Sheets integration scripts execute without import errors.
