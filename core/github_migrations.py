"""
core/github_migrations.py
=========================
Manages creation and safe, non-destructive schema migrations for the isolated
Phase V working database: data/working/phase5_github_candidate.db.

CRITICAL SAFETY:
- Never modifies the canonical, authentic audit19, baseline, or candidate databases.
- Performs bit-for-bit initial copy from candidate database.
- Verifies SHA-256 before and after copy.
- Applies non-destructive ALTER TABLE migrations.
- Executes full SQLite integrity check.
"""

import os
import shutil
import sqlite3
import hashlib
from typing import Dict, Any, Tuple, List, Optional
from datetime import datetime, timezone

EXPECTED_CANDIDATE_HASH = "eca573b4a4f1c045f417883772308050418c2d471250be7fda6c68e1ec023198"
DEFAULT_SOURCE_PATH = "data/working/candidate_rolling_ai_ecosystem.db"
DEFAULT_TARGET_PATH = "data/working/phase5_github_candidate.db"


def compute_sha256(filepath: str) -> str:
    """Computes SHA-256 hash of a file."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def initialize_phase5_database(
    source_path: str = DEFAULT_SOURCE_PATH,
    target_path: str = DEFAULT_TARGET_PATH,
    force_recreate: bool = False
) -> Dict[str, Any]:
    """
    Creates an isolated copy of candidate_rolling_ai_ecosystem.db at target_path.
    Verifies hashes before and after copy to ensure zero modification of source.
    """
    source_abs = os.path.abspath(source_path)
    target_abs = os.path.abspath(target_path)

    if not os.path.exists(source_abs):
        raise FileNotFoundError(f"Source candidate database not found at {source_abs}")

    source_hash_before = compute_sha256(source_abs)
    if source_path == DEFAULT_SOURCE_PATH and source_hash_before != EXPECTED_CANDIDATE_HASH:
        raise ValueError(
            f"Candidate DB hash mismatch! Expected {EXPECTED_CANDIDATE_HASH}, got {source_hash_before}"
        )

    if os.path.exists(target_abs) and not force_recreate:
        return {
            "status": "EXISTING",
            "source_path": source_abs,
            "target_path": target_abs,
            "source_hash": source_hash_before,
            "target_hash": compute_sha256(target_abs),
            "message": "Phase V database already exists. Using existing file."
        }

    # Ensure target directory exists
    os.makedirs(os.path.dirname(target_abs), exist_ok=True)

    # Perform bit-for-bit file copy
    shutil.copy2(source_abs, target_abs)

    source_hash_after = compute_sha256(source_abs)
    if source_hash_before != source_hash_after:
        raise RuntimeError(
            f"FATAL: Source candidate DB was modified during copy! Hash before: {source_hash_before}, after: {source_hash_after}"
        )

    target_hash = compute_sha256(target_abs)
    if target_hash != source_hash_before:
        raise RuntimeError("FATAL: Target database does not match source database byte-for-byte!")

    return {
        "status": "INITIALIZED",
        "source_path": source_abs,
        "target_path": target_abs,
        "source_hash": source_hash_before,
        "target_hash": target_hash,
        "message": "Successfully created isolated Phase V database copy."
    }


def apply_phase5_migrations(target_path: str = DEFAULT_TARGET_PATH) -> Dict[str, Any]:
    """
    Applies non-destructive schema migrations to the Phase V database:
    1. Extends github_repositories with full metadata columns.
    2. Extends github_metrics_history with open_issues and tracking columns.
    3. Creates github_repository_associations table.
    4. Seeds associations from existing 190 records.
    5. Runs PRAGMA integrity_check.
    """
    target_abs = os.path.abspath(target_path)
    if not os.path.exists(target_abs):
        raise FileNotFoundError(f"Database file not found: {target_abs}")

    conn = sqlite3.connect(target_abs)
    conn.execute("PRAGMA foreign_keys = ON;")
    fk_status = conn.execute("PRAGMA foreign_keys;").fetchone()[0]
    assert fk_status == 1, "Foreign key enforcement failed to activate!"
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    migrations_applied = []

    try:
        # Check and extend github_repositories
        cursor.execute("PRAGMA table_info(github_repositories);")
        existing_repo_cols = {row["name"] for row in cursor.fetchall()}

        repo_cols_to_add = [
            ("full_name", "TEXT"),
            ("primary_language", "TEXT"),
            ("topics", "TEXT"),  # JSON list string
            ("latest_open_issues", "INTEGER DEFAULT 0"),
            ("created_timestamp", "TEXT"),
            ("updated_timestamp", "TEXT"),
            ("pushed_timestamp", "TEXT"),
            ("default_branch", "TEXT"),
            ("is_fork", "INTEGER DEFAULT 0"),
            ("license_spdx_id", "TEXT"),
            ("collection_run_id", "TEXT"),
        ]

        for col_name, col_def in repo_cols_to_add:
            if col_name not in existing_repo_cols:
                cursor.execute(f"ALTER TABLE github_repositories ADD COLUMN {col_name} {col_def};")
                migrations_applied.append(f"github_repositories.{col_name}")

        # Ensure full_name is populated for existing repos where repo_id is owner/repo
        cursor.execute("UPDATE github_repositories SET full_name = repo_id WHERE full_name IS NULL OR full_name = '';")

        # Check and extend github_metrics_history
        cursor.execute("PRAGMA table_info(github_metrics_history);")
        existing_metrics_cols = {row["name"] for row in cursor.fetchall()}

        metrics_cols_to_add = [
            ("open_issues_count", "INTEGER DEFAULT 0"),
            ("change_open_issues_delta", "INTEGER DEFAULT 0"),
            ("source_api", "TEXT DEFAULT 'github_rest_api_v3'"),
            ("collection_run_id", "TEXT"),
        ]

        for col_name, col_def in metrics_cols_to_add:
            if col_name not in existing_metrics_cols:
                cursor.execute(f"ALTER TABLE github_metrics_history ADD COLUMN {col_name} {col_def};")
                migrations_applied.append(f"github_metrics_history.{col_name}")

        # Create github_repository_associations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS github_repository_associations (
                association_id TEXT PRIMARY KEY,
                source_entity_type TEXT NOT NULL,
                source_entity_id TEXT NOT NULL,
                repo_id TEXT NOT NULL,
                evidence_url TEXT,
                evidence_type TEXT NOT NULL,
                confidence TEXT NOT NULL,
                discovery_timestamp TEXT NOT NULL,
                verification_status TEXT NOT NULL,
                notes TEXT,
                FOREIGN KEY (repo_id) REFERENCES github_repositories(repo_id)
            );
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_assoc_source ON github_repository_associations(source_entity_id, source_entity_type);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_assoc_repo ON github_repository_associations(repo_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_assoc_status ON github_repository_associations(verification_status);")
        cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_assoc_unique ON github_repository_associations(source_entity_type, source_entity_id, repo_id);")

        migrations_applied.append("CREATE TABLE github_repository_associations")

        # Seed initial associations from existing 190 repos with associated_paper_id
        cursor.execute("""
            SELECT repo_id, owner, repo_name, html_url, associated_paper_id, last_checked_at
            FROM github_repositories
            WHERE associated_paper_id IS NOT NULL AND associated_paper_id != '';
        """)
        seeded_count = 0
        now_iso = datetime.now(timezone.utc).isoformat()
        for row in cursor.fetchall():
            paper_id = row["associated_paper_id"]
            repo_id = row["repo_id"]
            assoc_id = f"assoc_{paper_id}_{repo_id.replace('/', '_')}"
            disc_ts = row["last_checked_at"] or now_iso
            cursor.execute("""
                INSERT OR IGNORE INTO github_repository_associations (
                    association_id, source_entity_type, source_entity_id, repo_id,
                    evidence_url, evidence_type, confidence, discovery_timestamp,
                    verification_status, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                assoc_id, "research_paper", paper_id, repo_id,
                row["html_url"], "CANONICAL_FIELD", "HIGH", disc_ts,
                "VERIFIED", "Inherited from Phase I-III canonical research paper association"
            ))
            seeded_count += 1

        # Commit changes
        conn.commit()

        # Run integrity check
        cursor.execute("PRAGMA integrity_check;")
        integrity_result = cursor.fetchall()
        integrity_ok = len(integrity_result) == 1 and integrity_result[0][0] == "ok"
        if not integrity_ok:
            raise RuntimeError(f"Integrity check failed on {target_path}: {integrity_result}")

        # Get counts
        cursor.execute("SELECT count(*) FROM github_repositories;")
        repo_count = cursor.fetchone()[0]
        cursor.execute("SELECT count(*) FROM github_metrics_history;")
        metric_count = cursor.fetchone()[0]
        cursor.execute("SELECT count(*) FROM github_repository_associations;")
        assoc_count = cursor.fetchone()[0]

        conn.close()

        final_hash = compute_sha256(target_abs)

        return {
            "status": "MIGRATED",
            "target_path": target_abs,
            "target_hash": final_hash,
            "migrations_applied": migrations_applied,
            "seeded_associations": seeded_count,
            "total_repositories": repo_count,
            "total_metrics": metric_count,
            "total_associations": assoc_count,
            "integrity_check": "ok"
        }

    except Exception as e:
        conn.rollback()
        conn.close()
        raise e


if __name__ == "__main__":
    init_res = initialize_phase5_database(force_recreate=True)
    print("Init Result:", init_res)
    mig_res = apply_phase5_migrations()
    print("Migration Result:", mig_res)
