"""
scripts/reconciliation_audit_runner.py
======================================
Read-only inspection script for Phase V GitHub Integration Reconciliation Audit.
Executes non-mutating SQL queries and inspections across:
- Section 2: Phase V DB hash, integrity, tables, schemas, constraints
- Section 3: Investigation A - Repository association reconciliation
- Section 4: Investigation B - Lifecycle classification
- Section 5: Investigation C - Historical growth calculations
- Section 6: Investigation D - Research paper discovery & evidence quality
- Section 7: Investigation E - Schema safety & repeatability
- Section 8: Cross-check reported analytics
"""

import os
import sys
import json
import hashlib
import sqlite3
import csv
from datetime import datetime, timezone

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

PHASE5_DB = "data/working/phase5_github_candidate.db"
CANDIDATE_DB = "data/working/candidate_rolling_ai_ecosystem.db"
BASELINE_DB = "data/working/rolling_ai_ecosystem.db"
AUDIT19_DB = "source/audit19_original_database.db"
CANONICAL_DB = "data/normalized/ai_ecosystem.db"

EXPECTED_HASHES = {
    "Canonical": (CANONICAL_DB, "4949352d4f568f3f6128f398591cd8edac2eba45496c24535edb6c096398b95d"),
    "Audit19": (AUDIT19_DB, "1958c59f1a02e5a4bd274f114fdcfdd40942239f518eb662119962a263c84d4d"),
    "Baseline": (BASELINE_DB, "cbc1814cf3c6546a4dfa1d2e731648aead070b133b38892ddd599a6e385c2127"),
    "Candidate": (CANDIDATE_DB, "eca573b4a4f1c045f417883772308050418c2d471250be7fda6c68e1ec023198"),
    "Phase5": (PHASE5_DB, "dfa04c1b43204db50b998a34884a12ab7f48d9911dd0a3c07c3824a04711735a")
}


def compute_sha256(filepath):
    h = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def audit_section_2():
    print("=" * 80)
    print("SECTION 2: DATABASE VERIFICATION & SCHEMA INSPECTION")
    print("=" * 80)
    for name, (path, expected) in EXPECTED_HASHES.items():
        actual = compute_sha256(path)
        match = (actual == expected)
        print(f"  {name:12}: Match={match!s:5} Actual={actual}")
        if not match:
            print(f"    WARNING: {name} expected {expected}")

    conn = sqlite3.connect(f"file:{PHASE5_DB}?mode=ro", uri=True)
    c = conn.cursor()
    c.execute("PRAGMA integrity_check;")
    integ = c.fetchall()
    print(f"\n  Phase5 DB Integrity Check: {integ}")

    # Tables & counts
    c.execute("SELECT name, type FROM sqlite_master WHERE type IN ('table', 'view') ORDER BY name;")
    objects = c.fetchall()
    print("\n  Objects & Counts in Phase5 DB:")
    for name, otype in objects:
        if name == "sqlite_sequence":
            continue
        c.execute(f"SELECT count(*) FROM {name};")
        cnt = c.fetchone()[0]
        print(f"    {otype:6} {name:32}: {cnt:,} rows")

    # Indexes
    c.execute("SELECT tbl_name, name, sql FROM sqlite_master WHERE type='index' ORDER BY tbl_name, name;")
    indexes = c.fetchall()
    print(f"\n  Total Indexes: {len(indexes)}")
    for tbl, idx_name, sql in indexes:
        print(f"    Table {tbl:30} -> Index {idx_name:35} (SQL: {sql})")

    # Triggers
    c.execute("SELECT name, tbl_name FROM sqlite_master WHERE type='trigger';")
    triggers = c.fetchall()
    print(f"\n  Triggers: {len(triggers)}")
    for tname, tbl in triggers:
        print(f"    {tname} on {tbl}")

    # Inspect github_repositories, github_metrics_history, github_repository_associations
    target_tables = ["github_repositories", "github_metrics_history", "github_repository_associations"]
    print("\n  Table Schemas:")
    for t in target_tables:
        print(f"\n  --- {t} ---")
        c.execute(f"PRAGMA table_info({t});")
        cols = c.fetchall()
        for col in cols:
            # cid, name, type, notnull, dflt_value, pk
            print(f"    col #{col[0]}: {col[1]:25} {col[2]:12} notnull={col[3]} default={str(col[4]):10} pk={col[5]}")

        # Foreign keys
        c.execute(f"PRAGMA foreign_key_list({t});")
        fks = c.fetchall()
        print(f"    Foreign Keys ({len(fks)}):")
        for fk in fks:
            print(f"      fk: id={fk[0]} from={fk[3]} to={fk[2]}.{fk[4]} on_update={fk[5]} on_delete={fk[6]}")

    conn.close()


if __name__ == '__main__':
    audit_section_2()


def audit_investigation_a():
    print("\n" + "=" * 80)
    print("SECTION 3: INVESTIGATION A — REPOSITORY ASSOCIATION RECONCILIATION")
    print("=" * 80)
    conn = sqlite3.connect(f"file:{PHASE5_DB}?mode=ro", uri=True)
    c = conn.cursor()

    queries = {
        "1. Total unique repositories in github_repositories": "SELECT count(DISTINCT repo_id) FROM github_repositories;",
        "2. Total association rows in github_repository_associations": "SELECT count(*) FROM github_repository_associations;",
        "3. Total unique associated repositories": "SELECT count(DISTINCT repo_id) FROM github_repository_associations;",
        "4. Total unique research-paper IDs associated with repositories": "SELECT count(DISTINCT source_entity_id) FROM github_repository_associations WHERE source_entity_type = 'research_paper';",
        "5. Total unique product IDs associated with repositories": "SELECT count(DISTINCT source_entity_id) FROM github_repository_associations WHERE source_entity_type = 'product';",
        "6. Total unique startup IDs associated with repositories": "SELECT count(DISTINCT source_entity_id) FROM github_repository_associations WHERE source_entity_type = 'startup';",
        "7. Number of verified associations": "SELECT count(*) FROM github_repository_associations WHERE verification_status = 'VERIFIED';",
        "8. Number of unverified associations": "SELECT count(*) FROM github_repository_associations WHERE verification_status = 'UNVERIFIED';",
        "9. Number of papers with at least one verified repository": "SELECT count(DISTINCT source_entity_id) FROM github_repository_associations WHERE source_entity_type = 'research_paper' AND verification_status = 'VERIFIED';",
        "10. Number of repositories associated with multiple papers": "SELECT count(*) FROM (SELECT repo_id, count(DISTINCT source_entity_id) as cnt FROM github_repository_associations WHERE source_entity_type = 'research_paper' GROUP BY repo_id HAVING cnt > 1);",
        "11. Number of papers associated with multiple repositories": "SELECT count(*) FROM (SELECT source_entity_id, count(DISTINCT repo_id) as cnt FROM github_repository_associations WHERE source_entity_type = 'research_paper' GROUP BY source_entity_id HAVING cnt > 1);",
        "12. Duplicate association records": "SELECT count(*) FROM (SELECT source_entity_type, source_entity_id, repo_id, count(*) as cnt FROM github_repository_associations GROUP BY source_entity_type, source_entity_id, repo_id HAVING cnt > 1);",
        "13. Orphaned associations (repo_id not in github_repositories)": "SELECT count(*) FROM github_repository_associations WHERE repo_id NOT IN (SELECT repo_id FROM github_repositories);",
        "13b. Orphaned associations (source_entity_id not in source tables)": """
            SELECT count(*) FROM github_repository_associations
            WHERE (source_entity_type = 'research_paper' AND source_entity_id NOT IN (SELECT paper_id FROM ai_research_papers))
               OR (source_entity_type = 'product' AND source_entity_id NOT IN (SELECT product_id FROM ai_products))
               OR (source_entity_type = 'startup' AND source_entity_id NOT IN (SELECT startup_id FROM ai_startups));
        """
    }

    for label, q in queries.items():
        c.execute(q)
        res = c.fetchone()[0]
        print(f"  {label}: {res}")

    # Inspect the discrepancy: 191 paper associations vs 190 unique papers!
    print("\n  Detailed inspection: Why are there 191 paper associations for 190 unique papers?")
    c.execute("""
        SELECT source_entity_id, count(repo_id) as repo_count, group_concat(repo_id, '; ')
        FROM github_repository_associations
        WHERE source_entity_type = 'research_paper'
        GROUP BY source_entity_id
        HAVING repo_count > 1;
    """)
    multi_repos = c.fetchall()
    print(f"  Papers associated with MORE THAN ONE repository ({len(multi_repos)}):")
    for r in multi_repos:
        print(f"    Paper: {r[0]}, Count: {r[1]}, Repos: {r[2]}")

    c.execute("""
        SELECT repo_id, count(source_entity_id) as paper_count, group_concat(source_entity_id, '; ')
        FROM github_repository_associations
        WHERE source_entity_type = 'research_paper'
        GROUP BY repo_id
        HAVING paper_count > 1;
    """)
    multi_papers = c.fetchall()
    print(f"  Repositories associated with MORE THAN ONE paper ({len(multi_papers)}):")
    for r in multi_papers:
        print(f"    Repo: {r[0]}, Count: {r[1]}, Papers: {r[2]}")

    # Inspect the 1 product association
    c.execute("SELECT * FROM github_repository_associations WHERE source_entity_type = 'product';")
    prod_assocs = c.fetchall()
    print(f"\n  Product associations ({len(prod_assocs)}):")
    for r in prod_assocs:
        print(f"    {r}")

    # Check github_repositories associated_paper_id vs associations
    c.execute("""
        SELECT count(*) FROM github_repositories
        WHERE associated_paper_id IS NOT NULL AND associated_paper_id != '';
    """)
    repos_with_assoc_paper_col = c.fetchone()[0]
    print(f"\n  github_repositories with non-empty associated_paper_id column: {repos_with_assoc_paper_col}")

    # Check newly added repositories in github_repositories
    c.execute("""
        SELECT repo_id, owner, repo_name, full_name, html_url, associated_paper_id, status
        FROM github_repositories
        WHERE repo_id NOT IN (
            SELECT repo_id FROM github_repository_associations WHERE source_entity_type = 'research_paper' AND evidence_type = 'CANONICAL_FIELD'
        );
    """)
    new_or_diff_repos = c.fetchall()
    print(f"\n  Repositories NOT in initial canonical research-paper seed ({len(new_or_diff_repos)}):")
    for r in new_or_diff_repos:
        print(f"    {r}")

    conn.close()


if __name__ == '__main__':
    audit_section_2()
    audit_investigation_a()


def audit_paper_24597():
    print("\n--- Deep Dive on arxiv_2611_24597 ---")
    conn = sqlite3.connect(f"file:{PHASE5_DB}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT paper_id, title, paper_url, github_url, abstract FROM ai_research_papers WHERE paper_id = 'arxiv_2611_24597';")
    r = c.fetchone()
    print("Paper ID:", r["paper_id"])
    print("Title:   ", r["title"])
    print("GitHub URL in paper:", r["github_url"])
    print("Abstract:", r["abstract"][:300])

    c.execute("SELECT repo_id, owner, repo_name, full_name, html_url, associated_paper_id, status FROM github_repositories WHERE repo_id IN ('msalman95/DA', 'msalman95/DAL');")
    print("\nRepositories:")
    for row in c.fetchall():
        print(" ", dict(row))

    c.execute("SELECT * FROM github_repository_associations WHERE source_entity_id = 'arxiv_2611_24597';")
    print("\nAssociations:")
    for row in c.fetchall():
        print(" ", dict(row))
    conn.close()


if __name__ == '__main__':
    audit_paper_24597()


def audit_investigation_b():
    print("\n" + "=" * 80)
    print("SECTION 4: INVESTIGATION B — REPOSITORY LIFECYCLE CLASSIFICATION")
    print("=" * 80)
    conn = sqlite3.connect(f"file:{PHASE5_DB}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    # 1. Inspect status and is_archived values in github_repositories
    c.execute("SELECT status, count(*) FROM github_repositories GROUP BY status;")
    print("  Distinct status values in github_repositories:")
    for r in c.fetchall():
        print(f"    status='{r[0]}': {r[1]} repos")

    c.execute("SELECT is_archived, count(*) FROM github_repositories GROUP BY is_archived;")
    print("\n  Distinct is_archived values in github_repositories:")
    for r in c.fetchall():
        print(f"    is_archived={r[0]}: {r[1]} repos")

    # 2. Inspect last_checked_at and collection_run_id distribution
    c.execute("""
        SELECT
            CASE
                WHEN last_checked_at IS NULL THEN 'NULL'
                WHEN last_checked_at LIKE '2026-11-23%' THEN '2026-11-23 (Phase V)'
                WHEN last_checked_at LIKE '2026-11-22%' THEN '2026-11-22 (Audit 38a)'
                ELSE 'Earlier / Unknown'
            END AS check_period,
            count(*) as repo_count
        FROM github_repositories
        GROUP BY check_period;
    """)
    print("\n  last_checked_at freshness distribution:")
    for r in c.fetchall():
        print(f"    {r[0]}: {r[1]} repos")

    # 3. Check repos that were actually verified via GitHub API in Phase V vs inherited
    c.execute("""
        SELECT count(*) FROM github_repositories
        WHERE collection_run_id LIKE 'run_gh_%';
    """)
    checked_in_phase5 = c.fetchone()[0]
    print(f"\n  Repositories with Phase V collection_run_id: {checked_in_phase5}")

    # Inspect the 3 repos checked in Phase V:
    c.execute("""
        SELECT repo_id, status, is_archived, latest_stars, latest_forks, latest_open_issues, last_checked_at, collection_run_id
        FROM github_repositories
        WHERE collection_run_id LIKE 'run_gh_%';
    """)
    print("  Phase V checked repos:")
    for r in c.fetchall():
        print("   ", dict(r))

    # Inspect the 1 repo marked DISCOVERED:
    c.execute("SELECT repo_id, status, is_archived, last_checked_at FROM github_repositories WHERE status = 'DISCOVERED';")
    print("  Repos with status='DISCOVERED':")
    for r in c.fetchall():
        print("   ", dict(r))

    # Inspect remaining 188 repos:
    c.execute("""
        SELECT count(*) FROM github_repositories
        WHERE status = 'ACTIVE' AND (collection_run_id IS NULL OR collection_run_id NOT LIKE 'run_gh_%');
    """)
    inherited_active = c.fetchone()[0]
    print(f"  Repos with inherited status='ACTIVE' (not polled during Phase V collection): {inherited_active}")

    # Inspect retrieval_status in github_metrics_history
    c.execute("SELECT retrieval_status, count(*) FROM github_metrics_history GROUP BY retrieval_status;")
    print("\n  Distinct retrieval_status in github_metrics_history:")
    for r in c.fetchall():
        print(f"    {r[0]}: {r[1]} snapshots")

    conn.close()


if __name__ == '__main__':
    audit_investigation_b()


def audit_investigation_c():
    print("\n" + "=" * 80)
    print("SECTION 5: INVESTIGATION C — HISTORICAL GROWTH CALCULATIONS")
    print("=" * 80)
    conn = sqlite3.connect(f"file:{PHASE5_DB}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    target_repos = [
        "be2rlab/ACCORD",
        "DreamTechAI/Direct3D-V3",
        "kyutai-labs/aura"
    ]

    for repo_id in target_repos:
        print(f"\n  --- Repository: {repo_id} ---")
        c.execute("""
            SELECT repo_id, full_name, latest_stars, latest_forks, latest_open_issues, last_checked_at
            FROM github_repositories WHERE repo_id = ?;
        """, (repo_id,))
        repo = c.fetchone()
        if repo:
            print(f"    Repository ID:       {repo['repo_id']}")
            print(f"    Full Name:           {repo['full_name']}")
            print(f"    Latest Stars/Forks:  {repo['latest_stars']} stars, {repo['latest_forks']} forks")
            print(f"    Last Checked At:     {repo['last_checked_at']}")

        c.execute("""
            SELECT snapshot_id, repo_id, snapshot_timestamp, stars_count, forks_count,
                   open_issues_count, change_stars_delta, change_forks_delta,
                   retrieval_status, provenance, collection_run_id
            FROM github_metrics_history
            WHERE repo_id = ?
            ORDER BY snapshot_timestamp ASC, snapshot_id ASC;
        """, (repo_id,))
        snapshots = [dict(r) for r in c.fetchall()]
        print(f"    Total Snapshots:     {len(snapshots)}")
        for idx, s in enumerate(snapshots, 1):
            print(f"      Snapshot #{idx}: id={s['snapshot_id']}, time={s['snapshot_timestamp']}, stars={s['stars_count']}, forks={s['forks_count']}, issues={s['open_issues_count']}, delta_stars={s['change_stars_delta']}, status={s['retrieval_status']}, prov={s['provenance']}")

        if len(snapshots) >= 2:
            t1 = datetime.fromisoformat(snapshots[0]["snapshot_timestamp"].replace("Z", "+00:00"))
            t2 = datetime.fromisoformat(snapshots[-1]["snapshot_timestamp"].replace("Z", "+00:00"))
            elapsed_seconds = (t2 - t1).total_seconds()
            elapsed_days = elapsed_seconds / 86400.0
            elapsed_hours = elapsed_seconds / 3600.0
            raw_delta_stars = snapshots[-1]["stars_count"] - snapshots[0]["stars_count"]
            daily_growth = raw_delta_stars / elapsed_days if elapsed_days > 0 else 0.0
            weekly_growth = daily_growth * 7.0
            print(f"    Actual Elapsed Time: {elapsed_days:.4f} days ({elapsed_hours:.2f} hours)")
            print(f"    Calculated Raw Delta Stars: {raw_delta_stars}")
            print(f"    Normalized Daily Growth:    {daily_growth:.4f} stars/day")
            print(f"    Normalized Weekly Growth:   {weekly_growth:.4f} stars/week")
        else:
            print("    Only 1 snapshot available! Cannot compute elapsed interval.")

    # Inspect the implementation of calculate_repo_growth in core/github_deltas.py
    print("\n  Code Inspection of calculate_repo_growth in core/github_deltas.py:")
    with open("core/github_deltas.py", "r", encoding="utf-8") as f:
        code_lines = f.readlines()
        for idx, line in enumerate(code_lines):
            if "def calculate_repo_growth" in line:
                print("".join(code_lines[idx:idx+45]))
                break

    conn.close()


if __name__ == '__main__':
    audit_investigation_c()


def audit_investigation_d():
    print("\n" + "=" * 80)
    print("SECTION 6: INVESTIGATION D — RESEARCH EVIDENCE QUALITY AUDIT")
    print("=" * 80)
    conn = sqlite3.connect(f"file:{PHASE5_DB}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    # Query all research-paper associations joined with ai_research_papers
    c.execute("""
        SELECT
            a.association_id,
            a.source_entity_type,
            a.source_entity_id AS paper_id,
            p.title AS paper_title,
            a.repo_id,
            r.html_url AS repo_url,
            a.evidence_url,
            a.evidence_type,
            a.confidence,
            a.verification_status,
            a.notes,
            p.github_url AS paper_github_url,
            p.paper_url,
            p.abstract
        FROM github_repository_associations a
        JOIN ai_research_papers p ON a.source_entity_id = p.paper_id
        LEFT JOIN github_repositories r ON a.repo_id = r.repo_id
        WHERE a.source_entity_type = 'research_paper'
        ORDER BY a.source_entity_id, a.repo_id;
    """)
    rows = c.fetchall()
    print(f"  Total research-paper associations to audit: {len(rows)}")

    # Classify each into required taxonomy:
    # - DIRECT_OFFICIAL_REPOSITORY_LINK
    # - PAPER_PUBLISHER_LINK
    # - AUTHOR_OR_LAB_OFFICIAL_LINK
    # - OFFICIAL_PROJECT_WEBSITE_LINK
    # - ABSTRACT_TEXT_MENTION
    # - DEVELOPER_PROFILE_MATCH
    # - NAME_SIMILARITY_ONLY
    # - UNKNOWN_EVIDENCE

    audit_records = []
    downgrade_count = 0
    taxonomy_counts = {}

    for row in rows:
        paper_id = row["paper_id"]
        title = row["paper_title"]
        repo_id = row["repo_id"]
        repo_url = row["repo_url"] or f"https://github.com/{repo_id}"
        ev_url = row["evidence_url"] or ""
        ev_type = row["evidence_type"]
        confidence = row["confidence"]
        status = row["verification_status"]
        paper_gh = row["paper_github_url"] or ""
        paper_url = row["paper_url"] or ""
        abstract = row["abstract"] or ""

        # Determine exact source field
        if ev_type == "CANONICAL_FIELD":
            source_field = "ai_research_papers.github_url"
            classified_evidence = "DIRECT_OFFICIAL_REPOSITORY_LINK"
        elif ev_type == "ABSTRACT_MENTION":
            source_field = "ai_research_papers.abstract"
            classified_evidence = "ABSTRACT_TEXT_MENTION"
        elif "arxiv.org" in ev_url:
            source_field = "ai_research_papers.paper_url"
            classified_evidence = "PAPER_PUBLISHER_LINK"
        else:
            source_field = "unknown"
            classified_evidence = "UNKNOWN_EVIDENCE"

        taxonomy_counts[classified_evidence] = taxonomy_counts.get(classified_evidence, 0) + 1

        # Check for potential issues:
        # 1. Truncated URLs (like msalman95/DA)
        # 2. Abstract mentions that have not been confirmed live via API
        # 3. Discrepancy between owner/repo and title
        recommended_status = status
        audit_note = "Valid official association."

        if repo_id == "msalman95/DA":
            recommended_status = "MANUAL_REVIEW"
            audit_note = "Likely truncated URL in canonical database (should be msalman95/DAL)."
            downgrade_count += 1
        elif classified_evidence == "ABSTRACT_TEXT_MENTION":
            # If repo has status == 'DISCOVERED' and has not been verified live via API
            if repo_id == "msalman95/DAL":
                recommended_status = "UNVERIFIED"
                audit_note = "Abstract mention only; pending live API verification (status is DISCOVERED)."
                downgrade_count += 1

        audit_records.append({
            "paper_id": paper_id,
            "paper_title": title,
            "repo_id": repo_id,
            "repo_url": repo_url,
            "evidence_url": ev_url,
            "evidence_type": ev_type,
            "classified_evidence_category": classified_evidence,
            "source_field": source_field,
            "recorded_confidence": confidence,
            "recorded_status": status,
            "recommended_status": recommended_status,
            "audit_justification": audit_note
        })

    print(f"\n  Evidence Category Distribution:")
    for cat, cnt in taxonomy_counts.items():
        print(f"    {cat:32}: {cnt} associations")
    print(f"\n  Associations Recommended for Downgrade/Review: {downgrade_count}")

    # Export to reports/phase5_github/reconciliation_audit/04_research_evidence_audit.csv
    out_dir = "reports/phase5_github/reconciliation_audit"
    os.makedirs(out_dir, exist_ok=True)
    csv_path = os.path.join(out_dir, "04_research_evidence_audit.csv")

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        fieldnames = [
            "paper_id", "paper_title", "repo_id", "repo_url", "evidence_url",
            "evidence_type", "classified_evidence_category", "source_field",
            "recorded_confidence", "recorded_status", "recommended_status",
            "audit_justification"
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(audit_records)

    print(f"  Successfully exported {len(audit_records)} records to {csv_path}")
    conn.close()


if __name__ == '__main__':
    audit_investigation_d()


def audit_investigation_e():
    print("\n" + "=" * 80)
    print("SECTION 7: INVESTIGATION E — MIGRATION & SCHEMA SAFETY AUDIT")
    print("=" * 80)
    import tempfile
    import shutil
    from core.github_migrations import apply_phase5_migrations

    # Create disposable copy of candidate DB
    temp_dir = tempfile.mkdtemp()
    disposable_db = os.path.join(temp_dir, "disposable_test.db")
    shutil.copy2(CANDIDATE_DB, disposable_db)
    print(f"  Created disposable test database at: {disposable_db}")

    # Inspect candidate schema before migration
    conn_pre = sqlite3.connect(f"file:{disposable_db}?mode=ro", uri=True)
    c_pre = conn_pre.cursor()
    c_pre.execute("PRAGMA table_info(github_repositories);")
    pre_repo_cols = [r[1] for r in c_pre.fetchall()]
    c_pre.execute("PRAGMA table_info(github_metrics_history);")
    pre_metrics_cols = [r[1] for r in c_pre.fetchall()]
    c_pre.execute("SELECT count(*) FROM github_repositories;")
    pre_repo_count = c_pre.fetchone()[0]
    conn_pre.close()

    print(f"  Candidate DB before migration:")
    print(f"    github_repositories columns ({len(pre_repo_cols)}): {pre_repo_cols}")
    print(f"    github_metrics_history columns ({len(pre_metrics_cols)}): {pre_metrics_cols}")
    print(f"    github_repositories rows: {pre_repo_count}")

    # Run migration Pass 1
    res1 = apply_phase5_migrations(disposable_db)
    print(f"\n  Migration Pass 1 Result: status={res1['status']}, applied={len(res1['migrations_applied'])} changes")

    # Check columns after Pass 1
    conn_post1 = sqlite3.connect(f"file:{disposable_db}?mode=ro", uri=True)
    c_post1 = conn_post1.cursor()
    c_post1.execute("PRAGMA table_info(github_repositories);")
    post1_repo_cols = [r[1] for r in c_post1.fetchall()]
    c_post1.execute("PRAGMA table_info(github_metrics_history);")
    post1_metrics_cols = [r[1] for r in c_post1.fetchall()]
    c_post1.execute("PRAGMA table_info(github_repository_associations);")
    post1_assoc_cols = [r[1] for r in c_post1.fetchall()]
    c_post1.execute("SELECT count(*) FROM github_repositories;")
    post1_repo_count = c_post1.fetchone()[0]
    c_post1.execute("SELECT count(*) FROM github_repository_associations;")
    post1_assoc_count = c_post1.fetchone()[0]
    conn_post1.close()

    added_repo_cols = [col for col in post1_repo_cols if col not in pre_repo_cols]
    added_metrics_cols = [col for col in post1_metrics_cols if col not in pre_metrics_cols]

    print(f"\n  Added columns on github_repositories ({len(added_repo_cols)}): {added_repo_cols}")
    print(f"  Added columns on github_metrics_history ({len(added_metrics_cols)}): {added_metrics_cols}")
    print(f"  github_repository_associations columns ({len(post1_assoc_cols)}): {post1_assoc_cols}")
    print(f"  github_repositories rows: {post1_repo_count}")
    print(f"  github_repository_associations rows: {post1_assoc_count}")

    # Run migration Pass 2 (Repeatability / Idempotency Test)
    try:
        res2 = apply_phase5_migrations(disposable_db)
        print(f"\n  Migration Pass 2 (Idempotency Test): status={res2['status']}, applied={len(res2['migrations_applied'])} changes")
        pass2_success = True
    except Exception as e:
        print(f"\n  Migration Pass 2 FAILED: {str(e)}")
        pass2_success = False

    # Check migration version tracking table
    conn_v = sqlite3.connect(f"file:{disposable_db}?mode=ro", uri=True)
    c_v = conn_v.cursor()
    c_v.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%migrat%';")
    mig_tables = c_v.fetchall()
    print(f"\n  Migration version tracking tables: {mig_tables}")

    # Check foreign key enforcement
    c_v.execute("PRAGMA foreign_keys;")
    fk_status = c_v.fetchone()[0]
    print(f"  SQLite default PRAGMA foreign_keys: {fk_status} (0=OFF, 1=ON)")

    # Integrity check
    c_v.execute("PRAGMA integrity_check;")
    integ = c_v.fetchall()
    print(f"  Disposable DB PRAGMA integrity_check: {integ}")
    conn_v.close()

    # Clean up disposable DB
    shutil.rmtree(temp_dir)
    print(f"\n  Cleaned up disposable test directory {temp_dir}.")


if __name__ == '__main__':
    audit_investigation_e()


def audit_section_8_analytics():
    print("\n" + "=" * 80)
    print("SECTION 8: ANALYTICS CROSS-CHECK & RECALCULATION")
    print("=" * 80)
    conn = sqlite3.connect(f"file:{PHASE5_DB}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    # 1. Total tracked repositories
    c.execute("SELECT count(*) FROM github_repositories;")
    total_repos = c.fetchone()[0]

    # 2. Total historical snapshots
    c.execute("SELECT count(*) FROM github_metrics_history;")
    total_snapshots = c.fetchone()[0]

    # 3. Verified associations by entity type
    c.execute("SELECT count(*) FROM github_repository_associations WHERE source_entity_type = 'research_paper' AND verification_status = 'VERIFIED';")
    verified_papers = c.fetchone()[0]

    c.execute("SELECT count(*) FROM github_repository_associations WHERE source_entity_type = 'product' AND verification_status = 'VERIFIED';")
    verified_products = c.fetchone()[0]

    c.execute("SELECT count(*) FROM github_repository_associations WHERE source_entity_type = 'startup' AND verification_status = 'VERIFIED';")
    verified_startups = c.fetchone()[0]

    # 4. Coverage
    c.execute("SELECT count(*) FROM ai_research_papers;")
    total_paper_entities = c.fetchone()[0]
    c.execute("SELECT count(DISTINCT source_entity_id) FROM github_repository_associations WHERE source_entity_type = 'research_paper' AND verification_status = 'VERIFIED';")
    unique_papers_with_code = c.fetchone()[0]
    paper_coverage_pct = (unique_papers_with_code / total_paper_entities) * 100.0

    c.execute("SELECT count(*) FROM ai_products;")
    total_product_entities = c.fetchone()[0]
    c.execute("SELECT count(DISTINCT source_entity_id) FROM github_repository_associations WHERE source_entity_type = 'product' AND verification_status = 'VERIFIED';")
    unique_products_with_code = c.fetchone()[0]
    product_coverage_pct = (unique_products_with_code / total_product_entities) * 100.0

    c.execute("SELECT count(*) FROM ai_startups;")
    total_startup_entities = c.fetchone()[0]
    c.execute("SELECT count(DISTINCT source_entity_id) FROM github_repository_associations WHERE source_entity_type = 'startup' AND verification_status = 'VERIFIED';")
    unique_startups_with_code = c.fetchone()[0]
    startup_coverage_pct = (unique_startups_with_code / total_startup_entities) * 100.0

    # 5. Active vs Archived
    c.execute("SELECT count(*) FROM github_repositories WHERE is_archived = 1;")
    archived_count = c.fetchone()[0]
    c.execute("SELECT count(*) FROM github_repositories WHERE is_archived = 0;")
    unarchived_count = c.fetchone()[0]
    c.execute("SELECT count(*) FROM github_repositories WHERE status = 'ACTIVE';")
    status_active_count = c.fetchone()[0]
    c.execute("SELECT count(*) FROM github_repositories WHERE status = 'DISCOVERED';")
    status_discovered_count = c.fetchone()[0]

    print(f"  1. Total tracked repositories:           {total_repos}")
    print(f"  2. Total historical snapshots:           {total_snapshots}")
    print(f"  3. Verified research-paper associations: {verified_papers}")
    print(f"  4. Verified product associations:        {verified_products}")
    print(f"  5. Verified startup associations:        {verified_startups}")
    print(f"  6. Research-paper code coverage:         {unique_papers_with_code}/{total_paper_entities} ({paper_coverage_pct:.2f}%)")
    print(f"  7. Product code coverage:                {unique_products_with_code}/{total_product_entities} ({product_coverage_pct:.2f}%)")
    print(f"  8. Startup code coverage:                {unique_startups_with_code}/{total_startup_entities} ({startup_coverage_pct:.2f}%)")
    print(f"  9. Archived repository count:            {archived_count}")
    print(f"  10. Unarchived repository count:         {unarchived_count}")
    print(f"  10b. Repos with status='ACTIVE':         {status_active_count}")
    print(f"  10c. Repos with status='DISCOVERED':     {status_discovered_count}")

    # 6. Top repositories by stars
    c.execute("""
        SELECT repo_id, full_name, latest_stars, latest_forks, latest_open_issues, primary_language, status
        FROM github_repositories
        ORDER BY latest_stars DESC
        LIMIT 10;
    """)
    top_stars = c.fetchall()
    print("\n  Top 10 Repositories by Stars:")
    for idx, r in enumerate(top_stars, 1):
        print(f"    #{idx:2}: {r['repo_id']:40} {r['latest_stars']:,} stars | {r['latest_forks']:,} forks | {r['primary_language']} | status={r['status']}")

    # 7. Language distribution
    c.execute("""
        SELECT COALESCE(primary_language, 'Unknown / Unchecked') AS lang,
               count(*) as repo_count,
               SUM(latest_stars) as total_stars
        FROM github_repositories
        GROUP BY COALESCE(primary_language, 'Unknown / Unchecked')
        ORDER BY repo_count DESC;
    """)
    langs = c.fetchall()
    print("\n  Language Distribution:")
    for r in langs:
        pct = (r['repo_count'] / total_repos) * 100.0
        print(f"    {r['lang']:25}: {r['repo_count']:3} repos ({pct:5.2f}%) | {r['total_stars']:,} stars")

    # 8. Growth rankings cross-check
    from core.github_deltas import GitHubDeltaCalculator
    calc = GitHubDeltaCalculator(db_path=PHASE5_DB)
    growth_summaries = calc.compute_all_growth_summaries()

    # Sort by weekly_stars_delta
    sorted_growth = sorted(growth_summaries, key=lambda x: x.get("weekly_stars_delta", 0), reverse=True)
    print("\n  Top 5 Growth Rankings (as currently calculated by core/github_deltas.py):")
    for idx, g in enumerate(sorted_growth[:5], 1):
        print(f"    #{idx}: {g['repo_id']:35} weekly_delta={g['weekly_stars_delta']} | all_time={g['all_time_stars_growth']} | snapshots={g['snapshot_count']}")

    conn.close()


if __name__ == '__main__':
    audit_section_8_analytics()
