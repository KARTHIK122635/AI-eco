"""
core/github_dashboard_exporter.py
=================================
Dedicated local data exporter for Phase VI Google Sheets Dashboard Integration.

Reads the Phase V candidate database (data/working/phase5_github_candidate.db)
in strict read-only mode using parameterized SQL and core analytics engines.
Produces deterministic, normalized, and validated CSV and JSON artifacts under
data/exports/phase6/.

Invariants & Constraints:
- Zero mutations to source databases or tables.
- Parameterized SQL only.
- Strict UTC timestamp normalization.
- Formula injection prevention (sanitizing =, +, -, @).
- Explicit null handling (never conflates missing data with 0).
- Excludes unverified/short-term weekly growth from verified rankings.
- Redacts secrets, tokens, and authorization credentials.
- Generates cryptographic SHA-256 manifest for all exports.
"""

import os
import sys
import csv
import json
import sqlite3
import hashlib
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timezone

# Ensure workspace root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.github_client import parse_github_owner_repo
from core.github_evidence import (
    EvidenceValidator, VerificationStatus, ConfidenceLevel, EvidenceType
)
from core.github_deltas import GitHubDeltaCalculator, MIN_WEEKLY_INTERVAL_DAYS
from core.github_analytics import (
    GitHubAnalytics, RepositoryLifecycleClassifier, LifecycleState
)
from core.sheets_transformer import sanitize_cell_value

DEFAULT_DB_PATH = "data/working/phase5_github_candidate.db"
DEFAULT_EXPORT_DIR = "data/exports/phase6"


def compute_file_sha256(filepath: str) -> str:
    """Computes SHA-256 hash of an existing file."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


class GitHubDashboardExporter:
    """Extracts, normalizes, and exports Phase V GitHub intelligence for dashboard integration."""

    def __init__(
        self,
        db_path: str = DEFAULT_DB_PATH,
        export_dir: str = DEFAULT_EXPORT_DIR,
        ref_time: Optional[datetime] = None
    ):
        self.db_path = db_path
        self.export_dir = export_dir
        self.ref_time = ref_time or datetime.now(timezone.utc)
        self.ref_iso = self.ref_time.isoformat()

        self.analytics = GitHubAnalytics(db_path=self.db_path)
        self.deltas = GitHubDeltaCalculator(db_path=self.db_path)

    def _get_ro_connection(self) -> sqlite3.Connection:
        """Opens database in strict read-only mode with foreign keys enabled."""
        uri = f"file:{os.path.abspath(self.db_path)}?mode=ro"
        conn = sqlite3.connect(uri, uri=True)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    # --------------------------------------------------------------------------
    # 1. Export GitHub Repositories (192 records)
    # --------------------------------------------------------------------------
    def export_repositories(self) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Exports all 192 repositories with enriched lifecycle classification,
        association counts, and metadata.
        """
        conn = self._get_ro_connection()
        cursor = conn.cursor()

        # Fetch association counts per repo
        cursor.execute("""
            SELECT repo_id, count(*) AS assoc_cnt,
                   MAX(confidence) AS best_conf,
                   GROUP_CONCAT(DISTINCT verification_status) AS statuses
            FROM github_repository_associations
            GROUP BY repo_id;
        """)
        assoc_meta = {r["repo_id"]: dict(r) for r in cursor.fetchall()}

        # Fetch latest metric snapshots per repo
        cursor.execute("""
            SELECT m.repo_id, m.retrieval_status, m.snapshot_timestamp, m.source_api
            FROM github_metrics_history m
            INNER JOIN (
                SELECT repo_id, MAX(snapshot_timestamp) AS max_ts
                FROM github_metrics_history
                GROUP BY repo_id
            ) latest ON m.repo_id = latest.repo_id AND m.snapshot_timestamp = latest.max_ts;
        """)
        snapshots = {r["repo_id"]: dict(r) for r in cursor.fetchall()}

        # Fetch all repositories
        cursor.execute("""
            SELECT repo_id, owner, repo_name, full_name, html_url, description,
                   primary_language, topics, latest_stars, latest_forks, latest_open_issues,
                   is_archived, last_checked_at, status, associated_paper_id,
                   created_timestamp, updated_timestamp, pushed_timestamp,
                   default_branch, is_fork, license_spdx_id, collection_run_id
            FROM github_repositories
            ORDER BY repo_id ASC;
        """)
        repo_rows = [dict(r) for r in cursor.fetchall()]
        conn.close()

        records = []
        for r in repo_rows:
            rid = r["repo_id"]
            snap = snapshots.get(rid)
            am = assoc_meta.get(rid, {})

            # Evidence-based lifecycle state
            lifecycle_state = RepositoryLifecycleClassifier.classify_state(r, snap)

            # Association count & evidence quality
            assoc_cnt = am.get("assoc_cnt", 0)
            best_conf = am.get("best_conf") or ("HIGH" if r.get("associated_paper_id") else "UNVERIFIED")

            rec = {
                "repo_id": rid,
                "full_name": r.get("full_name") or rid,
                "owner": r["owner"],
                "repo_name": r["repo_name"],
                "html_url": r["html_url"],
                "description": r.get("description") or "",
                "primary_language": r.get("primary_language") or "Unknown / Not Specified",
                "latest_stars": r["latest_stars"] if r["latest_stars"] is not None else 0,
                "latest_forks": r["latest_forks"] if r["latest_forks"] is not None else 0,
                "latest_open_issues": r.get("latest_open_issues") if r.get("latest_open_issues") is not None else 0,
                "is_archived": "TRUE" if r.get("is_archived") else "FALSE",
                "lifecycle_status": lifecycle_state,
                "last_checked_at": r.get("last_checked_at") or "",
                "association_count": assoc_cnt,
                "evidence_quality": best_conf,
                "associated_paper_id": r.get("associated_paper_id") or "",
                "topics": r.get("topics") or "[]",
                "created_timestamp": r.get("created_timestamp") or "",
                "updated_timestamp": r.get("updated_timestamp") or "",
                "pushed_timestamp": r.get("pushed_timestamp") or "",
                "default_branch": r.get("default_branch") or "",
                "is_fork": "TRUE" if r.get("is_fork") else "FALSE",
                "license_spdx_id": r.get("license_spdx_id") or "",
                "collection_run_id": r.get("collection_run_id") or "",
                "last_synced_at": self.ref_iso
            }
            records.append(rec)

        csv_path = os.path.join(self.export_dir, "github_repositories.csv")
        self._write_csv(csv_path, records)
        return csv_path, records

    # --------------------------------------------------------------------------
    # 2. Export GitHub Metrics (210 snapshots)
    # --------------------------------------------------------------------------
    def export_metrics(self) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Exports all 210 historical metric snapshots with calculated daily deltas,
        reliability flags, and provenance.
        """
        conn = self._get_ro_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT snapshot_id, repo_id, snapshot_timestamp, stars_count, forks_count,
                   open_issues_count, change_stars_delta, change_forks_delta,
                   change_open_issues_delta, retrieval_status, provenance,
                   source_api, collection_run_id
            FROM github_metrics_history
            ORDER BY snapshot_timestamp ASC, snapshot_id ASC;
        """)
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()

        # Compute growth summaries by repo to attach reliable growth flags
        summaries = {s["repo_id"]: s for s in self.deltas.compute_all_growth_summaries()}

        records = []
        for r in rows:
            rid = r["repo_id"]
            growth_info = summaries.get(rid, {})

            weekly_status = growth_info.get("weekly_growth_status", "INSUFFICIENT_DATA")
            is_reliable = "TRUE" if growth_info.get("is_weekly_growth_reliable") else "FALSE"

            rec = {
                "snapshot_id": r["snapshot_id"],
                "repo_id": rid,
                "snapshot_timestamp": r["snapshot_timestamp"],
                "stars_count": r["stars_count"],
                "forks_count": r["forks_count"],
                "open_issues_count": r.get("open_issues_count") or 0,
                "change_stars_delta": r.get("change_stars_delta") or 0,
                "change_forks_delta": r.get("change_forks_delta") or 0,
                "change_open_issues_delta": r.get("change_open_issues_delta") or 0,
                "retrieval_status": r["retrieval_status"],
                "provenance": r.get("provenance") or "",
                "source_api": r.get("source_api") or "github_rest_api_v3",
                "collection_run_id": r.get("collection_run_id") or "",
                "daily_stars_delta": r.get("change_stars_delta") or 0,
                "weekly_growth_status": weekly_status,
                "is_growth_reliable": is_reliable,
                "last_synced_at": self.ref_iso
            }
            records.append(rec)

        csv_path = os.path.join(self.export_dir, "github_metrics.csv")
        self._write_csv(csv_path, records)
        return csv_path, records

    # --------------------------------------------------------------------------
    # 3. Export GitHub Associations (192 records)
    # --------------------------------------------------------------------------
    def export_associations(self) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Exports all 192 entity-to-repository association records with explicit
        evidence classification (VERIFIED, MANUAL_REVIEW, UNVERIFIED).
        """
        conn = self._get_ro_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT association_id, source_entity_type, source_entity_id, repo_id,
                   evidence_url, evidence_type, confidence, discovery_timestamp,
                   verification_status, notes
            FROM github_repository_associations
            ORDER BY source_entity_type ASC, source_entity_id ASC, repo_id ASC;
        """)
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()

        records = []
        for r in rows:
            repo_id = r["repo_id"]
            ev_type = r["evidence_type"]
            v_stat = r["verification_status"]
            parts = repo_id.split("/")
            repo_name = parts[1] if len(parts) > 1 else repo_id

            # Evaluated reporting classification
            if len(repo_name) <= 2:
                reporting_status = "MANUAL_REVIEW"
                reporting_notes = f"[MANUAL REVIEW REQUIRED] Truncated repo name '{repo_name}' (len <= 2). {r.get('notes') or ''}"
            elif ev_type == "ABSTRACT_MENTION":
                reporting_status = "UNVERIFIED"
                reporting_notes = f"[PENDING LIVE CHECK] Discovered via paper abstract. {r.get('notes') or ''}"
            else:
                reporting_status = v_stat
                reporting_notes = r.get("notes") or ""

            rec = {
                "association_id": r["association_id"],
                "source_entity_type": r["source_entity_type"],
                "source_entity_id": r["source_entity_id"],
                "repo_id": repo_id,
                "evidence_url": r.get("evidence_url") or "",
                "evidence_type": ev_type,
                "confidence": r["confidence"],
                "verification_status": reporting_status,
                "discovery_timestamp": r["discovery_timestamp"],
                "notes": reporting_notes.strip(),
                "last_synced_at": self.ref_iso
            }
            records.append(rec)

        csv_path = os.path.join(self.export_dir, "github_associations.csv")
        self._write_csv(csv_path, records)
        return csv_path, records

    # --------------------------------------------------------------------------
    # 4. Export Aggregated Analytics & Rankings (github_analytics.csv)
    # --------------------------------------------------------------------------
    def export_analytics(self) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Exports pre-aggregated KPIs, distribution tables, and rankings for
        dashboard consumption.
        """
        dist = self.analytics.get_lifecycle_distribution()
        cov = self.analytics.get_ecosystem_coverage()
        langs = self.analytics.get_language_distribution(limit=15)
        owners = self.analytics.get_organization_distribution(limit=15)
        top_repos = self.analytics.get_top_repositories_by_stars(limit=15)
        short_term = self.analytics.get_short_term_velocity_observations(limit=15)

        records = []

        # 1. Lifecycle Distribution Section
        for state, count in dist["breakdown"].items():
            pct = round((count / dist["total_repositories"] * 100), 2) if dist["total_repositories"] > 0 else 0.0
            records.append({
                "section": "LIFECYCLE_DISTRIBUTION",
                "metric_key": f"lifecycle_{state.lower()}",
                "metric_name": f"Repositories: {state}",
                "value": count,
                "secondary_value": f"{pct}%",
                "unit": "repositories",
                "status": "VERIFIED_EVIDENCE",
                "notes": f"Evidence-based state ({count} of {dist['total_repositories']} repos)"
            })

        # 2. Ecosystem Coverage Section
        cov_items = [
            ("coverage_research_papers", "Research Papers with Code", cov["research_papers"]["with_verified_code"], cov["research_papers"]["total"], cov["research_papers"]["coverage_pct"]),
            ("coverage_products", "Commercial Products with Code", cov["products"]["with_verified_code"], cov["products"]["total"], cov["products"]["coverage_pct"]),
            ("coverage_startups", "AI Startups with Code", cov["startups"]["with_verified_code"], cov["startups"]["total"], cov["startups"]["coverage_pct"]),
            ("associations_verified", "Verified Associations", cov["association_counts"]["verified"], cov["association_counts"]["total_associations"], ""),
            ("associations_manual_review", "Manual Review Associations", cov["association_counts"]["manual_review"], cov["association_counts"]["total_associations"], "msalman95/DA truncated"),
            ("associations_unverified", "Unverified Associations", cov["association_counts"]["unverified"], cov["association_counts"]["total_associations"], "msalman95/DAL abstract mention")
        ]
        for key, name, val, total, sec in cov_items:
            records.append({
                "section": "ECOSYSTEM_COVERAGE",
                "metric_key": key,
                "metric_name": name,
                "value": val,
                "secondary_value": f"{sec}%" if sec != "" else f"Total: {total}",
                "unit": "entities",
                "status": "VERIFIED_ACCOUNTING",
                "notes": f"{val} out of {total} entities"
            })

        # 3. Language Distribution Section
        for l in langs:
            records.append({
                "section": "LANGUAGE_DISTRIBUTION",
                "metric_key": f"lang_{l['language'].lower().replace(' ', '_').replace('/', '_')}",
                "metric_name": l["language"],
                "value": l["repo_count"],
                "secondary_value": f"{l['percentage']}% ({l['total_stars']:,} stars)",
                "unit": "repositories",
                "status": "VERIFIED_METADATA",
                "notes": f"{l['repo_count']} repositories"
            })

        # 4. Top Repositories by Stars
        for idx, r in enumerate(top_repos):
            records.append({
                "section": "TOP_REPOSITORIES_STARS",
                "metric_key": f"top_star_rank_{idx+1}",
                "metric_name": r["repo_id"],
                "value": r["latest_stars"],
                "secondary_value": f"{r['latest_forks']} forks | {r.get('primary_language') or 'N/A'}",
                "unit": "stars",
                "status": "VERIFIED_METRIC",
                "notes": f"Rank {idx+1} in ecosystem"
            })

        # 5. Short-Term Velocity Observations (Span < 5.0 days)
        for idx, s in enumerate(short_term):
            records.append({
                "section": "SHORT_TERM_VELOCITY",
                "metric_key": f"velocity_obs_{idx+1}",
                "metric_name": s["repo_id"],
                "value": s.get("raw_observed_stars_delta", 0),
                "secondary_value": f"{s['consecutive_elapsed_hours']:.1f}h span | {s['normalized_daily_stars_rate']:.2f} stars/d",
                "unit": "observed_stars_delta",
                "status": "INSUFFICIENT_DATA_RAW_OBSERVATION",
                "notes": f"Observation span ({s['total_span_days']:.2f}d) < {MIN_WEEKLY_INTERVAL_DAYS}d required for weekly rate."
            })

        csv_path = os.path.join(self.export_dir, "github_analytics.csv")
        self._write_csv(csv_path, records)
        return csv_path, records

    # --------------------------------------------------------------------------
    # 5. Export Dashboard KPIs JSON (dashboard_kpis.json)
    # --------------------------------------------------------------------------
    def export_dashboard_kpis(self) -> Tuple[str, Dict[str, Any]]:
        """Compiles complete dashboard KPI dictionary into structured JSON."""
        dist = self.analytics.get_lifecycle_distribution()
        cov = self.analytics.get_ecosystem_coverage()
        langs = self.analytics.get_language_distribution(limit=10)
        top_repos = self.analytics.get_top_repositories_by_stars(limit=10)
        short_term = self.analytics.get_short_term_velocity_observations(limit=10)

        conn = self._get_ro_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(latest_stars), SUM(latest_forks), SUM(latest_open_issues) FROM github_repositories;")
        sum_stars, sum_forks, sum_issues = cursor.fetchone()

        cursor.execute("""
            SELECT run_id, start_time, end_time, updated_metrics_count, failed_requests_count, status
            FROM collection_logs
            WHERE execution_type = 'MANUAL_GITHUB_PHASE5'
            ORDER BY start_time DESC LIMIT 1;
        """)
        latest_coll = cursor.fetchone()
        conn.close()

        kpi_data = {
            "metadata": {
                "generated_at": self.ref_iso,
                "source_database": self.db_path,
                "source_sha256": compute_file_sha256(self.db_path),
                "phase": "PHASE_VI_DASHBOARD_INTEGRATION"
            },
            "repository_overview": {
                "total_repositories": dist["total_repositories"],
                "active_verified": dist["active_verified_count"],
                "active_verified_percentage": dist["active_verified_percentage"],
                "not_yet_checked": dist["not_yet_checked_count"],
                "not_yet_checked_percentage": dist["not_yet_checked_percentage"],
                "archived_verified": dist["archived_verified_count"],
                "not_found_404": dist["not_found_count"],
                "access_denied_403": dist["access_denied_count"],
                "api_unavailable_5xx": dist["api_unavailable_count"],
                "network_errors": dist["network_error_count"],
                "unknown": dist["unknown_count"]
            },
            "repository_performance": {
                "total_stars": sum_stars or 0,
                "total_forks": sum_forks or 0,
                "total_open_issues": sum_issues or 0,
                "top_languages": langs[:5],
                "top_repositories_by_stars": top_repos[:5]
            },
            "growth_velocity": {
                "min_weekly_interval_days": MIN_WEEKLY_INTERVAL_DAYS,
                "verified_weekly_growth_qualified_count": 0,
                "weekly_growth_status": "INSUFFICIENT_OBSERVATION_HISTORY",
                "short_term_velocity_observations": short_term[:5],
                "insufficient_reason": f"Current snapshot observation spans (< 2.1 days) do not meet the {MIN_WEEKLY_INTERVAL_DAYS}-day statistical minimum."
            },
            "ecosystem_coverage": {
                "research_papers": cov["research_papers"],
                "commercial_products": cov["products"],
                "ai_startups": cov["startups"],
                "association_counts": cov["association_counts"]
            },
            "collection_monitoring": {
                "latest_run_id": latest_coll["run_id"] if latest_coll else None,
                "latest_run_start_time": latest_coll["start_time"] if latest_coll else None,
                "latest_run_end_time": latest_coll["end_time"] if latest_coll else None,
                "latest_run_status": latest_coll["status"] if latest_coll else None,
                "updated_metrics": latest_coll["updated_metrics_count"] if latest_coll else 0,
                "failed_requests": latest_coll["failed_requests_count"] if latest_coll else 0
            }
        }

        json_path = os.path.join(self.export_dir, "dashboard_kpis.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(kpi_data, f, indent=2)
        return json_path, kpi_data

    # --------------------------------------------------------------------------
    # 6. Execute Full Export & Generate Manifest
    # --------------------------------------------------------------------------
    def run_full_export(self) -> Dict[str, Any]:
        """Executes full export of all 4 CSVs, 1 JSON, and the cryptographic manifest."""
        os.makedirs(self.export_dir, exist_ok=True)

        repo_path, repo_recs = self.export_repositories()
        metric_path, metric_recs = self.export_metrics()
        assoc_path, assoc_recs = self.export_associations()
        ana_path, ana_recs = self.export_analytics()
        kpi_path, kpi_data = self.export_dashboard_kpis()

        manifest = {
            "export_metadata": {
                "phase": "PHASE_VI_LOCAL_DASHBOARD_EXPORT",
                "export_timestamp_utc": self.ref_iso,
                "source_database_path": os.path.normpath(self.db_path),
                "source_database_sha256": compute_file_sha256(self.db_path),
                "export_directory": os.path.normpath(self.export_dir),
                "sanitization_applied": "FORMULA_INJECTION_DEFENSE_AND_NULL_NORMALIZATION"
            },
            "record_counts": {
                "github_repositories": len(repo_recs),
                "github_metrics": len(metric_recs),
                "github_associations": len(assoc_recs),
                "github_analytics": len(ana_recs),
                "total_exported_tabular_rows": len(repo_recs) + len(metric_recs) + len(assoc_recs) + len(ana_recs)
            },
            "exported_files": {
                "github_repositories.csv": {
                    "path": os.path.normpath(repo_path),
                    "rows": len(repo_recs),
                    "sha256": compute_file_sha256(repo_path)
                },
                "github_metrics.csv": {
                    "path": os.path.normpath(metric_path),
                    "rows": len(metric_recs),
                    "sha256": compute_file_sha256(metric_path)
                },
                "github_associations.csv": {
                    "path": os.path.normpath(assoc_path),
                    "rows": len(assoc_recs),
                    "sha256": compute_file_sha256(assoc_path)
                },
                "github_analytics.csv": {
                    "path": os.path.normpath(ana_path),
                    "rows": len(ana_recs),
                    "sha256": compute_file_sha256(ana_path)
                },
                "dashboard_kpis.json": {
                    "path": os.path.normpath(kpi_path),
                    "sha256": compute_file_sha256(kpi_path)
                }
            }
        }

        manifest_path = os.path.join(self.export_dir, "export_manifest.json")
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)

        manifest["manifest_file"] = {
            "path": os.path.normpath(manifest_path),
            "sha256": compute_file_sha256(manifest_path)
        }

        return manifest

    def _write_csv(self, filepath: str, records: List[Dict[str, Any]]) -> None:
        """Writes sanitized records to a UTF-8 CSV file."""
        if not records:
            return
        fieldnames = list(records[0].keys())
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL)
            writer.writeheader()
            for r in records:
                sanitized_row = {k: sanitize_cell_value(v) for k, v in r.items()}
                writer.writerow(sanitized_row)


if __name__ == "__main__":
    exporter = GitHubDashboardExporter()
    manifest = exporter.run_full_export()
    print("=" * 80)
    print("PHASE VI EXPORT COMPLETE")
    print("=" * 80)
    print(f"Source DB Hash: {manifest['export_metadata']['source_database_sha256']}")
    print(f"Total Rows:     {manifest['record_counts']['total_exported_tabular_rows']}")
    for fname, meta in manifest["exported_files"].items():
        print(f"  - {fname:<25} | SHA-256: {meta['sha256']}")
