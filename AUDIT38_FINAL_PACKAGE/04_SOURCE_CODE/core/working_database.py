"""
Working SQLite Database Architecture for Rolling AI Ecosystem Pipeline
======================================================================
Manages data/working/rolling_ai_ecosystem.db.
Maintains:
- Active 6-Month rolling views & historical archived records
- Primary entities: ai_startups, ai_products, ai_research_papers, ai_news, ai_jobs
- GitHub repositories registry & metrics snapshot history (github_metrics_history)
- Idempotent execution checkpoints & collection logs (collection_logs)
- Stage 3 enrichment proposals queue (enrichment_proposals)

CRITICAL INVARIANTS:
- Canonical SQLite database (data/normalized/ai_ecosystem.db) is STRICTLY READ-ONLY.
- Authentic Audit 19 database (source/audit19_original_database.db) is STRICTLY READ-ONLY.
- Original record IDs, provenance, evidence, and timestamps are 100% preserved.
- Expired jobs are never deleted; vacancy_status is transitioned to EXPIRED.
"""

import os
import sqlite3
import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from core.rolling_window import (
    compute_rolling_window,
    classify_freshness,
    parse_publication_timestamp
)


class WorkingDatabaseManager:
    """Manages the separate rolling working SQLite database."""

    def __init__(
        self,
        working_db_path: str = "data/working/rolling_ai_ecosystem.db",
        canonical_db_path: str = "data/normalized/ai_ecosystem.db",
    ):
        self.working_db_path = os.path.abspath(working_db_path)
        self.canonical_db_path = os.path.abspath(canonical_db_path)
        os.makedirs(os.path.dirname(self.working_db_path), exist_ok=True)

    def get_connection(self) -> sqlite3.Connection:
        """Returns SQLite connection to working database with WAL mode."""
        conn = sqlite3.connect(self.working_db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode = WAL")
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def initialize_schema(self) -> None:
        """Creates working tables, relationships, and performance indexes."""
        conn = self.get_connection()
        c = conn.cursor()

        # 1. AI Startups
        c.execute("""
            CREATE TABLE IF NOT EXISTS ai_startups (
                startup_id TEXT PRIMARY KEY,
                entity_name TEXT NOT NULL,
                ai_focus_area TEXT,
                ai_evidence TEXT,
                employee_count INTEGER,
                pricing_model TEXT,
                website TEXT,
                primary_source_url TEXT,
                provenance_sources TEXT,
                headquarters TEXT,
                batch_or_founded TEXT,
                founding_date TEXT,
                announcement_date TEXT,
                date_type TEXT DEFAULT 'UNVERIFIED_DATE',
                date_provenance TEXT,
                description TEXT,
                published_at TEXT,
                first_seen_at TEXT,
                collected_at TEXT,
                freshness_status TEXT,
                in_rolling_window INTEGER DEFAULT 0
            )
        """)
        c.execute("CREATE INDEX IF NOT EXISTS idx_startups_name ON ai_startups(entity_name)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_startups_window ON ai_startups(in_rolling_window)")

        # 2. AI Products
        c.execute("""
            CREATE TABLE IF NOT EXISTS ai_products (
                product_id TEXT PRIMARY KEY,
                entity_name TEXT NOT NULL,
                product_type TEXT,
                ai_task_category TEXT,
                developer_or_company TEXT,
                developer_profile_url TEXT,
                official_company_website TEXT,
                pricing_model TEXT,
                license TEXT,
                access_type TEXT,
                actual_price REAL,
                original_source_url TEXT,
                provenance_source TEXT,
                launch_date TEXT,
                release_date TEXT,
                date_type TEXT DEFAULT 'UNVERIFIED_DATE',
                date_provenance TEXT,
                description TEXT,
                published_at TEXT,
                first_seen_at TEXT,
                collected_at TEXT,
                freshness_status TEXT,
                in_rolling_window INTEGER DEFAULT 0
            )
        """)
        c.execute("CREATE INDEX IF NOT EXISTS idx_products_name ON ai_products(entity_name)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_products_window ON ai_products(in_rolling_window)")

        # 3. AI Research Papers
        c.execute("""
            CREATE TABLE IF NOT EXISTS ai_research_papers (
                paper_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                authors TEXT,
                publication_date TEXT,
                date_type TEXT DEFAULT 'RESEARCH_PUBLICATION_DATE',
                date_provenance TEXT,
                categories TEXT,
                paper_url TEXT,
                github_url TEXT,
                github_stars INTEGER DEFAULT 0,
                github_forks INTEGER DEFAULT 0,
                github_star_source TEXT,
                github_star_retrieved_at TEXT,
                provenance TEXT,
                abstract TEXT,
                first_seen_at TEXT,
                collected_at TEXT,
                freshness_status TEXT,
                in_rolling_window INTEGER DEFAULT 1
            )
        """)
        c.execute("CREATE INDEX IF NOT EXISTS idx_papers_title ON ai_research_papers(title)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_papers_window ON ai_research_papers(in_rolling_window)")

        # 4. AI News
        c.execute("""
            CREATE TABLE IF NOT EXISTS ai_news (
                news_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                summary TEXT,
                content TEXT,
                source_name TEXT,
                article_url TEXT UNIQUE,
                author TEXT,
                published_at TEXT,
                date_type TEXT DEFAULT 'NEWS_PUBLICATION_DATE',
                date_provenance TEXT,
                category TEXT,
                related_companies TEXT,
                first_seen_at TEXT,
                collected_at TEXT,
                provenance TEXT,
                freshness_status TEXT,
                in_rolling_window INTEGER DEFAULT 1
            )
        """)
        c.execute("CREATE INDEX IF NOT EXISTS idx_news_url ON ai_news(article_url)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_news_window ON ai_news(in_rolling_window)")

        # 5. AI Jobs
        c.execute("""
            CREATE TABLE IF NOT EXISTS ai_jobs (
                job_id TEXT PRIMARY KEY,
                job_title TEXT NOT NULL,
                company_name TEXT NOT NULL,
                company_website TEXT,
                category TEXT,
                classification_reason TEXT,
                responsibility_evidence TEXT,
                qualification_evidence TEXT,
                classification_confidence REAL,
                job_description TEXT,
                required_skills TEXT,
                preferred_skills TEXT,
                experience_level TEXT,
                location TEXT,
                remote_type TEXT,
                salary_min REAL,
                salary_max REAL,
                currency TEXT,
                compensation_type TEXT,
                compensation_period TEXT,
                employment_type TEXT,
                job_status TEXT,
                vacancy_status TEXT DEFAULT 'ACTIVE',
                application_url TEXT UNIQUE,
                posted_at TEXT,
                date_type TEXT DEFAULT 'JOB_POSTING_DATE',
                date_provenance TEXT,
                source_name TEXT,
                provenance TEXT,
                first_seen_at TEXT,
                collected_at TEXT,
                freshness_status TEXT,
                in_rolling_window INTEGER DEFAULT 1
            )
        """)
        c.execute("CREATE INDEX IF NOT EXISTS idx_jobs_url ON ai_jobs(application_url)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_jobs_window ON ai_jobs(in_rolling_window)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_jobs_vacancy ON ai_jobs(vacancy_status)")

        # 6. GitHub Repositories Registry
        c.execute("""
            CREATE TABLE IF NOT EXISTS github_repositories (
                repo_id TEXT PRIMARY KEY,
                owner TEXT NOT NULL,
                repo_name TEXT NOT NULL,
                html_url TEXT NOT NULL,
                description TEXT,
                associated_paper_id TEXT,
                is_archived INTEGER DEFAULT 0,
                latest_stars INTEGER DEFAULT 0,
                latest_forks INTEGER DEFAULT 0,
                last_checked_at TEXT,
                status TEXT DEFAULT 'ACTIVE'
            )
        """)
        c.execute("CREATE INDEX IF NOT EXISTS idx_repos_paper ON github_repositories(associated_paper_id)")

        # 7. GitHub Metrics History (Snapshot Timeline)
        c.execute("""
            CREATE TABLE IF NOT EXISTS github_metrics_history (
                snapshot_id INTEGER PRIMARY KEY AUTOINCREMENT,
                repo_id TEXT NOT NULL,
                snapshot_timestamp TEXT NOT NULL,
                stars_count INTEGER NOT NULL,
                forks_count INTEGER NOT NULL,
                change_stars_delta INTEGER DEFAULT 0,
                change_forks_delta INTEGER DEFAULT 0,
                retrieval_status TEXT NOT NULL,
                provenance TEXT,
                FOREIGN KEY (repo_id) REFERENCES github_repositories(repo_id)
            )
        """)
        c.execute("CREATE INDEX IF NOT EXISTS idx_metrics_repo ON github_metrics_history(repo_id)")

        # 8. Collection Logs & Checkpoints
        c.execute("""
            CREATE TABLE IF NOT EXISTS collection_logs (
                run_id TEXT PRIMARY KEY,
                scheduled_time TEXT,
                start_time TEXT NOT NULL,
                end_time TEXT,
                execution_type TEXT NOT NULL,
                rolling_window_start TEXT NOT NULL,
                rolling_window_end TEXT NOT NULL,
                new_startups INTEGER DEFAULT 0,
                new_products INTEGER DEFAULT 0,
                new_papers INTEGER DEFAULT 0,
                new_news INTEGER DEFAULT 0,
                new_jobs INTEGER DEFAULT 0,
                updated_metrics_count INTEGER DEFAULT 0,
                fresh_24h_count INTEGER DEFAULT 0,
                duplicates_rejected INTEGER DEFAULT 0,
                failed_requests_count INTEGER DEFAULT 0,
                llm_requests_count INTEGER DEFAULT 0,
                llm_prompt_tokens INTEGER DEFAULT 0,
                llm_completion_tokens INTEGER DEFAULT 0,
                llm_cost_usd REAL DEFAULT 0.0,
                status TEXT DEFAULT 'IN_PROGRESS',
                checkpoint_data TEXT,
                error_log TEXT,
                lease_owner TEXT,
                process_id INTEGER,
                host_name TEXT,
                claim_timestamp TEXT,
                last_heartbeat TEXT,
                recovery_run_id TEXT,
                original_run_id TEXT
            )
        """)

        # 9. Enrichment Proposals (Strictly PENDING_APPROVAL)
        c.execute("""
            CREATE TABLE IF NOT EXISTS enrichment_proposals (
                proposal_id TEXT PRIMARY KEY,
                run_id TEXT,
                record_id TEXT NOT NULL,
                entity_type TEXT NOT NULL,
                field_name TEXT NOT NULL,
                original_value TEXT,
                proposed_value TEXT,
                evidence_quote TEXT,
                reasoning TEXT,
                confidence_score REAL,
                validation_status TEXT,
                validation_rationale TEXT,
                schema_status TEXT,
                schema_target_table TEXT,
                schema_target_column TEXT,
                duplication_status TEXT,
                approval_status TEXT DEFAULT 'PENDING_APPROVAL',
                active_tier TEXT,
                active_provider TEXT,
                active_model TEXT,
                prompt_tokens INTEGER DEFAULT 0,
                completion_tokens INTEGER DEFAULT 0,
                cost_usd REAL DEFAULT 0.0,
                created_at TEXT
            )
        """)
        c.execute("CREATE INDEX IF NOT EXISTS idx_prop_rec ON enrichment_proposals(record_id)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_prop_status ON enrichment_proposals(approval_status)")

        # Ensure schema backward-compatibility by adding columns if tables already existed
        tables_to_columns = {
            "ai_startups": [
                ("announcement_date", "TEXT"),
                ("date_type", "TEXT DEFAULT 'UNVERIFIED_DATE'"),
                ("date_provenance", "TEXT"),
            ],
            "ai_products": [
                ("launch_date", "TEXT"),
                ("release_date", "TEXT"),
                ("date_type", "TEXT DEFAULT 'UNVERIFIED_DATE'"),
                ("date_provenance", "TEXT"),
            ],
            "ai_research_papers": [
                ("date_type", "TEXT DEFAULT 'RESEARCH_PUBLICATION_DATE'"),
                ("date_provenance", "TEXT"),
            ],
            "ai_news": [
                ("date_type", "TEXT DEFAULT 'NEWS_PUBLICATION_DATE'"),
                ("date_provenance", "TEXT"),
            ],
            "ai_jobs": [
                ("date_type", "TEXT DEFAULT 'JOB_POSTING_DATE'"),
                ("date_provenance", "TEXT"),
            ],
            "collection_logs": [
                ("lease_owner", "TEXT"),
                ("process_id", "INTEGER"),
                ("host_name", "TEXT"),
                ("claim_timestamp", "TEXT"),
                ("last_heartbeat", "TEXT"),
                ("recovery_run_id", "TEXT"),
                ("original_run_id", "TEXT"),
            ],
        }
        for tbl, cols in tables_to_columns.items():
            existing = [r[1] for r in c.execute(f"PRAGMA table_info({tbl})").fetchall()]
            for col_name, col_def in cols:
                if col_name not in existing:
                    c.execute(f"ALTER TABLE {tbl} ADD COLUMN {col_name} {col_def}")

        # Backfill default provenance/date_type for any rows where they are NULL
        c.execute("UPDATE ai_startups SET date_type = 'UNVERIFIED_DATE' WHERE date_type IS NULL")
        c.execute("UPDATE ai_startups SET date_provenance = coalesce(provenance_sources, 'Canonical Baseline') WHERE date_provenance IS NULL")
        c.execute("UPDATE ai_products SET date_type = 'UNVERIFIED_DATE' WHERE date_type IS NULL")
        c.execute("UPDATE ai_products SET date_provenance = coalesce(provenance_source, 'Canonical Baseline') WHERE date_provenance IS NULL")
        c.execute("UPDATE ai_research_papers SET date_type = 'RESEARCH_PUBLICATION_DATE' WHERE date_type IS NULL")
        c.execute("UPDATE ai_research_papers SET date_provenance = coalesce(provenance, 'arXiv / HF Papers') WHERE date_provenance IS NULL")
        c.execute("UPDATE ai_news SET date_type = 'NEWS_PUBLICATION_DATE' WHERE date_type IS NULL")
        c.execute("UPDATE ai_news SET date_provenance = coalesce(provenance, 'RSS Feed') WHERE date_provenance IS NULL")
        c.execute("UPDATE ai_jobs SET date_type = 'JOB_POSTING_DATE' WHERE date_type IS NULL")
        c.execute("UPDATE ai_jobs SET date_provenance = coalesce(provenance, 'ATS / Job Board API') WHERE date_provenance IS NULL")

        conn.commit()
        conn.close()

    def seed_from_canonical(self, ref_time: Optional[datetime] = None) -> Dict[str, int]:
        """
        Seeds working database from canonical ai_ecosystem.db (strictly read-only).
        Classifies records into dynamic rolling 6-month window without modifying canonical database.
        """
        now = ref_time or datetime.now(timezone.utc)
        start_w, end_w = compute_rolling_window(now, months=6)

        self.initialize_schema()
        conn_w = self.get_connection()
        c_w = conn_w.cursor()

        # Connect read-only to canonical
        uri = f"file:{self.canonical_db_path}?mode=ro"
        conn_c = sqlite3.connect(uri, uri=True)
        conn_c.row_factory = sqlite3.Row
        c_c = conn_c.cursor()

        stats = {
            "startups": 0,
            "products": 0,
            "papers": 0,
            "news": 0,
            "jobs": 0,
            "repos": 0,
            "snapshots": 0,
        }

        # 1. Startups (Founding/Batch date is NOT a publication date; canonical has no published_at)
        c_c.execute("SELECT * FROM ai_startups")
        for r in c_c.fetchall():
            d = dict(r)
            founding = d.get("batch_or_founded")
            coll_dt = d.get("collected_at")
            pub_dt = None  # Canonical startups have no publication timestamp
            f_eval = classify_freshness(pub_dt, now, start_w, date_type="UNVERIFIED_DATE")
            c_w.execute("""
                INSERT OR IGNORE INTO ai_startups (
                    startup_id, entity_name, ai_focus_area, ai_evidence, employee_count,
                    pricing_model, website, primary_source_url, provenance_sources,
                    headquarters, batch_or_founded, founding_date, announcement_date, date_type, date_provenance,
                    description, published_at, first_seen_at, collected_at, freshness_status, in_rolling_window
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                d["startup_id"], d["entity_name"], d.get("ai_focus_area"), d.get("ai_evidence"),
                d.get("employee_count"), d.get("pricing_model"), d.get("website"),
                d.get("primary_source_url"), d.get("provenance_sources"), d.get("headquarters"),
                founding, founding, None, "UNVERIFIED_DATE", d.get("provenance_sources") or "Canonical Baseline",
                d.get("description"), None, coll_dt, coll_dt,
                f_eval["status"], 1 if f_eval["in_rolling_window"] else 0
            ))
            stats["startups"] += 1

        # 2. Products (Canonical products have no publication date; collected_at is an operational timestamp)
        c_c.execute("SELECT * FROM ai_products")
        for r in c_c.fetchall():
            d = dict(r)
            coll_dt = d.get("collected_at")
            pub_dt = None  # Canonical products have no publication timestamp
            f_eval = classify_freshness(pub_dt, now, start_w, date_type="UNVERIFIED_DATE")
            c_w.execute("""
                INSERT OR IGNORE INTO ai_products (
                    product_id, entity_name, product_type, ai_task_category, developer_or_company,
                    developer_profile_url, official_company_website, pricing_model, license,
                    access_type, actual_price, original_source_url, provenance_source, launch_date,
                    release_date, date_type, date_provenance, description, published_at, first_seen_at,
                    collected_at, freshness_status, in_rolling_window
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                d["product_id"], d["entity_name"], d.get("product_type"), d.get("ai_task_category"),
                d.get("developer_or_company"), d.get("developer_profile_url"), d.get("official_company_website"),
                d.get("pricing_model"), d.get("license"), d.get("access_type"), d.get("actual_price"),
                d.get("original_source_url"), d.get("provenance_source"), None,
                None, "UNVERIFIED_DATE", d.get("provenance_source") or "Canonical Baseline", d.get("description"),
                None, coll_dt, coll_dt,
                f_eval["status"], 1 if f_eval["in_rolling_window"] else 0
            ))
            stats["products"] += 1

        # 3. Papers
        c_c.execute("SELECT * FROM ai_research_papers")
        for r in c_c.fetchall():
            d = dict(r)
            pub_dt = parse_publication_timestamp(d.get("publication_date"))
            coll_dt = d.get("collected_at")
            f_eval = classify_freshness(pub_dt, now, start_w)
            c_w.execute("""
                INSERT OR IGNORE INTO ai_research_papers (
                    paper_id, title, authors, publication_date, date_type, date_provenance,
                    categories, paper_url, github_url, github_stars, github_forks, github_star_source,
                    github_star_retrieved_at, provenance, abstract, first_seen_at, collected_at,
                    freshness_status, in_rolling_window
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                d["paper_id"], d["title"], d.get("authors"), d.get("publication_date"),
                "RESEARCH_PUBLICATION_DATE", d.get("provenance") or "arXiv / HF Papers",
                d.get("categories"), d.get("paper_url"), d.get("github_url"),
                d.get("github_stars") or 0, d.get("github_forks") or 0,
                d.get("github_star_source"), d.get("github_star_retrieved_at"),
                d.get("provenance"), d.get("abstract"), coll_dt, coll_dt,
                f_eval["status"], 1 if f_eval["in_rolling_window"] else 0
            ))
            stats["papers"] += 1

            # Seed GitHub repository if present
            gh_url = d.get("github_url")
            if gh_url and "github.com/" in gh_url:
                parts = gh_url.split("github.com/")[-1].strip("/").split("/")
                if len(parts) >= 2:
                    owner, repo = parts[0], parts[1].removesuffix(".git")
                    repo_id = f"{owner}/{repo}"
                    stars = d.get("github_stars") or 0
                    forks = d.get("github_forks") or 0
                    retrieved = d.get("github_star_retrieved_at") or now.isoformat()

                    c_w.execute("""
                        INSERT OR IGNORE INTO github_repositories (
                            repo_id, owner, repo_name, html_url, associated_paper_id,
                            latest_stars, latest_forks, last_checked_at, status
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        repo_id, owner, repo, f"https://github.com/{owner}/{repo}",
                        d["paper_id"], stars, forks, retrieved, "ACTIVE"
                    ))
                    stats["repos"] += 1

                    # Seed initial metrics snapshot
                    c_w.execute("""
                        INSERT INTO github_metrics_history (
                            repo_id, snapshot_timestamp, stars_count, forks_count,
                            change_stars_delta, change_forks_delta, retrieval_status, provenance
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        repo_id, retrieved, stars, forks, 0, 0,
                        d.get("github_star_source") or "canonical_seed", d.get("provenance") or "ai_ecosystem.db"
                    ))
                    stats["snapshots"] += 1

        # 4. News
        c_c.execute("SELECT * FROM ai_news")
        for r in c_c.fetchall():
            d = dict(r)
            pub_dt = parse_publication_timestamp(d.get("published_at"))
            coll_dt = d.get("collected_at")
            f_eval = classify_freshness(pub_dt, now, start_w)
            c_w.execute("""
                INSERT OR IGNORE INTO ai_news (
                    news_id, title, summary, content, source_name, article_url,
                    author, published_at, date_type, date_provenance, category, related_companies,
                    first_seen_at, collected_at, provenance, freshness_status, in_rolling_window
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                d["news_id"], d["title"], d.get("summary"), d.get("content"),
                d.get("source_name"), d.get("article_url"), d.get("author"),
                d.get("published_at"), "NEWS_PUBLICATION_DATE", d.get("provenance") or "RSS Feed",
                d.get("category"), d.get("related_companies"),
                coll_dt, coll_dt, d.get("provenance"),
                f_eval["status"], 1 if f_eval["in_rolling_window"] else 0
            ))
            stats["news"] += 1

        # 5. Jobs
        c_c.execute("SELECT * FROM ai_jobs")
        for r in c_c.fetchall():
            d = dict(r)
            pub_dt = parse_publication_timestamp(d.get("posted_at"))
            coll_dt = d.get("collected_at")
            f_eval = classify_freshness(pub_dt, now, start_w)
            c_w.execute("""
                INSERT OR IGNORE INTO ai_jobs (
                    job_id, job_title, company_name, company_website, category,
                    classification_reason, responsibility_evidence, qualification_evidence,
                    classification_confidence, job_description, required_skills, preferred_skills,
                    experience_level, location, remote_type, salary_min, salary_max, currency,
                    compensation_type, compensation_period, employment_type, job_status,
                    vacancy_status, application_url, posted_at, date_type, date_provenance,
                    source_name, provenance, first_seen_at, collected_at, freshness_status, in_rolling_window
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                d["job_id"], d["job_title"], d["company_name"], d.get("company_website"),
                d.get("category"), d.get("classification_reason"), d.get("responsibility_evidence"),
                d.get("qualification_evidence"), d.get("classification_confidence"),
                d.get("job_description"), d.get("required_skills"), d.get("preferred_skills"),
                d.get("experience_level"), d.get("location"), d.get("remote_type"),
                d.get("salary_min"), d.get("salary_max"), d.get("currency"),
                d.get("compensation_type"), d.get("compensation_period"), d.get("employment_type"),
                d.get("job_status"), d.get("vacancy_status") or "ACTIVE", d["application_url"],
                d.get("posted_at"), "JOB_POSTING_DATE", d.get("provenance") or "ATS / Job Board API",
                d.get("source_name"), d.get("provenance"),
                coll_dt, coll_dt,
                f_eval["status"], 1 if f_eval["in_rolling_window"] else 0
            ))
            stats["jobs"] += 1

        conn_c.close()
        conn_w.commit()
        conn_w.close()

        return stats

    def recalculate_freshness(self, ref_time: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Recalculates freshness status and in_rolling_window flags for all records in the
        working database using true six-calendar-month rolling window boundaries.
        Explicitly enforces:
        - Never use collected_at as a substitute for published_at.
        - Products without genuine publication dates are classified as MISSING_DATE.
        - Startups without genuine publication dates are classified as MISSING_DATE.
        - Records outside the 6-month window are retained in SQLite archive (in_rolling_window = 0).
        """
        now = ref_time or datetime.now(timezone.utc)
        start_w, end_w = compute_rolling_window(now, months=6)

        conn = self.get_connection()
        c = conn.cursor()

        stats = {
            "window_start": start_w.isoformat(),
            "window_end": end_w.isoformat(),
            "datasets": {}
        }

        # 1. Startups
        c.execute("SELECT startup_id, published_at FROM ai_startups")
        startups = c.fetchall()
        st_summary = {"total": len(startups), "valid_pub": 0, "in_window": 0, "outside_window": 0, "missing_dates": 0, "future_anomalies": 0}
        for s_id, pub_at in startups:
            pub_dt = parse_publication_timestamp(pub_at) if pub_at else None
            f_eval = classify_freshness(pub_dt, now, start_w)
            c.execute("UPDATE ai_startups SET freshness_status = ?, in_rolling_window = ? WHERE startup_id = ?",
                      (f_eval["status"], 1 if f_eval["in_rolling_window"] else 0, s_id))
            if pub_dt:
                st_summary["valid_pub"] += 1
            if f_eval["in_rolling_window"]:
                st_summary["in_window"] += 1
            elif f_eval["status"] == "OUTSIDE_WINDOW":
                st_summary["outside_window"] += 1
            elif f_eval["status"] in ("MISSING_DATE", "UNVERIFIED_DATE"):
                st_summary["missing_dates"] += 1
            elif f_eval["status"] == "FUTURE_TIMESTAMP_ANOMALY":
                st_summary["future_anomalies"] += 1
        stats["datasets"]["ai_startups"] = st_summary

        # 2. Products
        c.execute("SELECT product_id, published_at FROM ai_products")
        products = c.fetchall()
        prod_summary = {"total": len(products), "valid_pub": 0, "in_window": 0, "outside_window": 0, "missing_dates": 0, "future_anomalies": 0}
        for p_id, pub_at in products:
            pub_dt = parse_publication_timestamp(pub_at) if pub_at else None
            f_eval = classify_freshness(pub_dt, now, start_w)
            c.execute("UPDATE ai_products SET freshness_status = ?, in_rolling_window = ? WHERE product_id = ?",
                      (f_eval["status"], 1 if f_eval["in_rolling_window"] else 0, p_id))
            if pub_dt:
                prod_summary["valid_pub"] += 1
            if f_eval["in_rolling_window"]:
                prod_summary["in_window"] += 1
            elif f_eval["status"] == "OUTSIDE_WINDOW":
                prod_summary["outside_window"] += 1
            elif f_eval["status"] in ("MISSING_DATE", "UNVERIFIED_DATE"):
                prod_summary["missing_dates"] += 1
            elif f_eval["status"] == "FUTURE_TIMESTAMP_ANOMALY":
                prod_summary["future_anomalies"] += 1
        stats["datasets"]["ai_products"] = prod_summary

        # 3. Papers
        c.execute("SELECT paper_id, publication_date FROM ai_research_papers")
        papers = c.fetchall()
        paper_summary = {"total": len(papers), "valid_pub": 0, "in_window": 0, "outside_window": 0, "missing_dates": 0, "future_anomalies": 0}
        for p_id, pub_at in papers:
            pub_dt = parse_publication_timestamp(pub_at) if pub_at else None
            f_eval = classify_freshness(pub_dt, now, start_w)
            c.execute("UPDATE ai_research_papers SET freshness_status = ?, in_rolling_window = ? WHERE paper_id = ?",
                      (f_eval["status"], 1 if f_eval["in_rolling_window"] else 0, p_id))
            if pub_dt:
                paper_summary["valid_pub"] += 1
            if f_eval["in_rolling_window"]:
                paper_summary["in_window"] += 1
            elif f_eval["status"] == "OUTSIDE_WINDOW":
                paper_summary["outside_window"] += 1
            elif f_eval["status"] == "MISSING_DATE":
                paper_summary["missing_dates"] += 1
            elif f_eval["status"] == "FUTURE_TIMESTAMP_ANOMALY":
                paper_summary["future_anomalies"] += 1
        stats["datasets"]["ai_research_papers"] = paper_summary

        # 4. News
        c.execute("SELECT news_id, published_at FROM ai_news")
        news = c.fetchall()
        news_summary = {"total": len(news), "valid_pub": 0, "in_window": 0, "outside_window": 0, "missing_dates": 0, "future_anomalies": 0}
        for n_id, pub_at in news:
            pub_dt = parse_publication_timestamp(pub_at) if pub_at else None
            f_eval = classify_freshness(pub_dt, now, start_w)
            c.execute("UPDATE ai_news SET freshness_status = ?, in_rolling_window = ? WHERE news_id = ?",
                      (f_eval["status"], 1 if f_eval["in_rolling_window"] else 0, n_id))
            if pub_dt:
                news_summary["valid_pub"] += 1
            if f_eval["in_rolling_window"]:
                news_summary["in_window"] += 1
            elif f_eval["status"] == "OUTSIDE_WINDOW":
                news_summary["outside_window"] += 1
            elif f_eval["status"] == "MISSING_DATE":
                news_summary["missing_dates"] += 1
            elif f_eval["status"] == "FUTURE_TIMESTAMP_ANOMALY":
                news_summary["future_anomalies"] += 1
        stats["datasets"]["ai_news"] = news_summary

        # 5. Jobs
        c.execute("SELECT job_id, posted_at FROM ai_jobs")
        jobs = c.fetchall()
        job_summary = {"total": len(jobs), "valid_pub": 0, "in_window": 0, "outside_window": 0, "missing_dates": 0, "future_anomalies": 0}
        for j_id, pub_at in jobs:
            pub_dt = parse_publication_timestamp(pub_at) if pub_at else None
            f_eval = classify_freshness(pub_dt, now, start_w)
            c.execute("UPDATE ai_jobs SET freshness_status = ?, in_rolling_window = ? WHERE job_id = ?",
                      (f_eval["status"], 1 if f_eval["in_rolling_window"] else 0, j_id))
            if pub_dt:
                job_summary["valid_pub"] += 1
            if f_eval["in_rolling_window"]:
                job_summary["in_window"] += 1
            elif f_eval["status"] == "OUTSIDE_WINDOW":
                job_summary["outside_window"] += 1
            elif f_eval["status"] == "MISSING_DATE":
                job_summary["missing_dates"] += 1
            elif f_eval["status"] == "FUTURE_TIMESTAMP_ANOMALY":
                job_summary["future_anomalies"] += 1
        stats["datasets"]["ai_jobs"] = job_summary

        conn.commit()
        conn.close()
        return stats

    def refresh_github_metric(
        self,
        repo_id: str,
        stars: int,
        forks: int,
        is_archived: bool = False,
        retrieval_status: str = "HTTP_200_OK",
        provenance: str = "official_github_rest_api",
        ref_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Updates github_repositories and appends snapshot to github_metrics_history with delta tracking.
        """
        now_iso = (ref_time or datetime.now(timezone.utc)).isoformat()
        conn = self.get_connection()
        c = conn.cursor()

        # Get latest known stars
        c.execute("SELECT latest_stars, latest_forks FROM github_repositories WHERE repo_id = ?", (repo_id,))
        row = c.fetchone()
        prev_stars = row["latest_stars"] if row else 0
        prev_forks = row["latest_forks"] if row else 0

        delta_stars = stars - prev_stars
        delta_forks = forks - prev_forks

        # Update repository record
        c.execute("""
            UPDATE github_repositories
            SET latest_stars = ?, latest_forks = ?, is_archived = ?, last_checked_at = ?, status = ?
            WHERE repo_id = ?
        """, (stars, forks, 1 if is_archived else 0, now_iso, "ACTIVE" if retrieval_status == "HTTP_200_OK" else retrieval_status, repo_id))

        # Append snapshot
        c.execute("""
            INSERT INTO github_metrics_history (
                repo_id, snapshot_timestamp, stars_count, forks_count,
                change_stars_delta, change_forks_delta, retrieval_status, provenance
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (repo_id, now_iso, stars, forks, delta_stars, delta_forks, retrieval_status, provenance))

        conn.commit()
        conn.close()

        return {
            "repo_id": repo_id,
            "stars": stars,
            "forks": forks,
            "delta_stars": delta_stars,
            "delta_forks": delta_forks,
            "is_archived": is_archived
        }

    def update_job_vacancy_status(self, job_id: str, status: str) -> bool:
        """Transitions job vacancy status (ACTIVE vs EXPIRED). Never deletes."""
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("UPDATE ai_jobs SET vacancy_status = ? WHERE job_id = ?", (status, job_id))
        updated = c.rowcount > 0
        conn.commit()
        conn.close()
        return updated

    def log_collection_checkpoint(self, log_entry: Dict[str, Any]) -> None:
        """
        Records an execution checkpoint into collection_logs with strict lease validation
        and heartbeat persistence.
        - Separate INSERT for new runs vs atomic conditional UPDATE for existing runs.
        - Existing leased rows reject updates if lease_owner is omitted or mismatched.
        - Recovery-owned rows validate both lease_owner and recovery execution identity.
        - Preserves existing metadata fields not explicitly modified.
        - Rejects stale owners without modifying the database.
        """
        conn = self.get_connection()
        c = conn.cursor()

        run_id = log_entry["run_id"]
        incoming_lease = log_entry.get("lease_owner")

        # Check if record already exists
        c.execute("SELECT * FROM collection_logs WHERE run_id = ?", (run_id,))
        existing_row = c.fetchone()

        if existing_row is None:
            # NEW RUN INSERTION: Separate from update path (no INSERT OR REPLACE)
            cp_data = log_entry.get("checkpoint_data", {})
            if isinstance(cp_data, (dict, list)):
                cp_str = json.dumps(cp_data)
            else:
                cp_str = str(cp_data) if cp_data else None

            c.execute("""
                INSERT INTO collection_logs (
                    run_id, scheduled_time, start_time, end_time, execution_type,
                    rolling_window_start, rolling_window_end, new_startups, new_products,
                    new_papers, new_news, new_jobs, updated_metrics_count, fresh_24h_count,
                    duplicates_rejected, failed_requests_count, llm_requests_count,
                    llm_prompt_tokens, llm_completion_tokens, llm_cost_usd, status,
                    checkpoint_data, error_log, lease_owner, process_id, host_name,
                    claim_timestamp, last_heartbeat, recovery_run_id, original_run_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                run_id, log_entry.get("scheduled_time"), log_entry.get("start_time"),
                log_entry.get("end_time"), log_entry.get("execution_type", "DAILY_INCREMENTAL"),
                log_entry.get("rolling_window_start"), log_entry.get("rolling_window_end"),
                log_entry.get("new_startups", 0), log_entry.get("new_products", 0),
                log_entry.get("new_papers", 0), log_entry.get("new_news", 0),
                log_entry.get("new_jobs", 0), log_entry.get("updated_metrics_count", 0),
                log_entry.get("fresh_24h_count", 0), log_entry.get("duplicates_rejected", 0),
                log_entry.get("failed_requests_count", 0), log_entry.get("llm_requests_count", 0),
                log_entry.get("llm_prompt_tokens", 0), log_entry.get("llm_completion_tokens", 0),
                log_entry.get("llm_cost_usd", 0.0), log_entry.get("status", "IN_PROGRESS"),
                cp_str, log_entry.get("error_log"),
                incoming_lease, log_entry.get("process_id"), log_entry.get("host_name"),
                log_entry.get("claim_timestamp"), log_entry.get("last_heartbeat"),
                log_entry.get("recovery_run_id"), log_entry.get("original_run_id")
            ))
            conn.commit()
            conn.close()
            return

        # EXISTING RUN UPDATE PATH: Strict Lease Validation & Conditional UPDATE
        existing = dict(existing_row)
        existing_lease = existing.get("lease_owner")
        existing_recovery_id = existing.get("recovery_run_id")
        incoming_recovery_id = log_entry.get("recovery_run_id")
        existing_orig_id = existing.get("original_run_id")
        incoming_orig_id = log_entry.get("original_run_id")

        # 1. Existing leased rows must not be updated by a caller that omits lease_owner
        if existing_lease and not incoming_lease:
            conn.close()
            raise PermissionError(
                f"Lease validation error: run '{run_id}' is leased to '{existing_lease}', "
                f"but incoming checkpoint update omitted lease_owner."
            )

        # 2. Existing leased rows must not be updated by a different lease owner
        if existing_lease and incoming_lease != existing_lease:
            conn.close()
            raise PermissionError(
                f"Stale lease rejection: incoming lease '{incoming_lease}' "
                f"cannot overwrite run '{run_id}' owned by active lease '{existing_lease}'."
            )

        # 3. Recovery-owned rows must validate both lease owner and recovery execution identity
        if existing_recovery_id and incoming_recovery_id and incoming_recovery_id != existing_recovery_id:
            conn.close()
            raise PermissionError(
                f"Recovery identity mismatch: run '{run_id}' has active recovery_run_id '{existing_recovery_id}', "
                f"cannot be updated with incoming recovery_run_id '{incoming_recovery_id}'."
            )

        if existing_orig_id and incoming_orig_id and incoming_orig_id != existing_orig_id:
            conn.close()
            raise PermissionError(
                f"Lineage mismatch: run '{run_id}' has original_run_id '{existing_orig_id}', "
                f"cannot be updated with incoming original_run_id '{incoming_orig_id}'."
            )

        # 4. Merge entry to preserve existing metadata fields caller did not intend to change
        merged = dict(existing)
        for k, v in log_entry.items():
            if v is not None or k in ("end_time", "error_log"):
                merged[k] = v

        merged_cp_data = merged.get("checkpoint_data", {})
        if isinstance(merged_cp_data, (dict, list)):
            merged_cp_str = json.dumps(merged_cp_data)
        else:
            merged_cp_str = str(merged_cp_data) if merged_cp_data else None

        # 5. Atomic conditional UPDATE operation
        where_clauses = ["run_id = ?"]
        where_params = [run_id]

        if existing_lease:
            where_clauses.append("lease_owner = ?")
            where_params.append(existing_lease)
        else:
            where_clauses.append("(lease_owner IS NULL OR lease_owner = '')")

        if existing_recovery_id:
            where_clauses.append("(recovery_run_id IS NULL OR recovery_run_id = ?)")
            where_params.append(existing_recovery_id)

        where_sql = " AND ".join(where_clauses)

        update_sql = f"""
            UPDATE collection_logs
            SET scheduled_time = ?,
                start_time = ?,
                end_time = ?,
                execution_type = ?,
                rolling_window_start = ?,
                rolling_window_end = ?,
                new_startups = ?,
                new_products = ?,
                new_papers = ?,
                new_news = ?,
                new_jobs = ?,
                updated_metrics_count = ?,
                fresh_24h_count = ?,
                duplicates_rejected = ?,
                failed_requests_count = ?,
                llm_requests_count = ?,
                llm_prompt_tokens = ?,
                llm_completion_tokens = ?,
                llm_cost_usd = ?,
                status = ?,
                checkpoint_data = ?,
                error_log = ?,
                lease_owner = ?,
                process_id = ?,
                host_name = ?,
                claim_timestamp = ?,
                last_heartbeat = ?,
                recovery_run_id = ?,
                original_run_id = ?
            WHERE {where_sql}
        """

        update_params = [
            merged.get("scheduled_time"), merged.get("start_time"),
            merged.get("end_time"), merged.get("execution_type"),
            merged.get("rolling_window_start"), merged.get("rolling_window_end"),
            merged.get("new_startups", 0), merged.get("new_products", 0),
            merged.get("new_papers", 0), merged.get("new_news", 0),
            merged.get("new_jobs", 0), merged.get("updated_metrics_count", 0),
            merged.get("fresh_24h_count", 0), merged.get("duplicates_rejected", 0),
            merged.get("failed_requests_count", 0), merged.get("llm_requests_count", 0),
            merged.get("llm_prompt_tokens", 0), merged.get("llm_completion_tokens", 0),
            merged.get("llm_cost_usd", 0.0), merged.get("status", "IN_PROGRESS"),
            merged_cp_str, merged.get("error_log"),
            incoming_lease if incoming_lease else existing_lease,
            merged.get("process_id"), merged.get("host_name"),
            merged.get("claim_timestamp"), merged.get("last_heartbeat"),
            merged.get("recovery_run_id"), merged.get("original_run_id")
        ] + where_params

        c.execute(update_sql, tuple(update_params))
        if c.rowcount == 0:
            conn.commit()
            conn.close()
            raise PermissionError(
                f"Stale lease rejection: conditional update matched 0 rows for run '{run_id}'. "
                f"Active lease or state was modified concurrently."
            )

        conn.commit()
        conn.close()

    def update_heartbeat(self, run_id: str, lease_owner: Optional[str] = None, ref_time: Optional[datetime] = None) -> bool:
        """Updates the heartbeat timestamp for an active run/recovery lease tied strictly to lease owner."""
        now_iso = (ref_time or datetime.now(timezone.utc)).isoformat()
        conn = self.get_connection()
        c = conn.cursor()
        if lease_owner:
            c.execute("""
                UPDATE collection_logs
                SET last_heartbeat = ?
                WHERE run_id = ? AND lease_owner = ?
            """, (now_iso, run_id, lease_owner))
        else:
            c.execute("""
                UPDATE collection_logs
                SET last_heartbeat = ?
                WHERE run_id = ? AND lease_owner IS NULL
            """, (now_iso, run_id))
        updated = c.rowcount > 0
        conn.commit()
        conn.close()
        return updated
