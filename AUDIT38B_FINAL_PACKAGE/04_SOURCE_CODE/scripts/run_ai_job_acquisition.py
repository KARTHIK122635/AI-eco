"""
Execution Script for Phase II - Stage 2: AI Job Acquisition.
Ingests, normalizes, serializes canonical exports (JSONL, CSV),
and synchronizes SQLite persistence in data/normalized/ai_ecosystem.db.
"""

import os
import sys
import json
import csv
import sqlite3
import asyncio
import logging
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sources.ai_job_collector import AIJobCollector

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("run_ai_job_acquisition")

CANONICAL_JSONL_PATH = "data/canonical/canonical_jobs.jsonl"
CANONICAL_CSV_PATH = "data/canonical/canonical_jobs.csv"
DB_PATH = "data/normalized/ai_ecosystem.db"


def export_canonical_jsonl(jobs: list, filepath: str):
    """Write canonical JSONL export with standardized envelope."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        for j in jobs:
            canonical_obj = {
                "schemaVersion": "1.0",
                "recordType": "AI_JOB",
                "source": {
                    "name": j["sourceName"],
                    "url": j["applicationUrl"]
                },
                "content": {
                    "entityName": j["jobTitle"],
                    "data": {
                        "jobId": j["jobId"],
                        "jobTitle": j["jobTitle"],
                        "companyName": j["companyName"],
                        "category": j["category"],
                        "jobDescription": j["jobDescription"],
                        "requiredSkills": j["requiredSkills"],
                        "experienceLevel": j["experienceLevel"],
                        "location": j["location"],
                        "remoteType": j["remoteType"],
                        "salaryMin": j["salaryMin"],
                        "salaryMax": j["salaryMax"],
                        "currency": j["currency"],
                        "employmentType": j["employmentType"],
                        "vacancyStatus": j["vacancyStatus"],
                        "applicationUrl": j["applicationUrl"],
                        "postedAt": j["postedAt"],
                        "sourceName": j["sourceName"],
                        "provenance": j["provenance"],
                        "collectedAt": j["collectedAt"]
                    }
                },
                "collectedAt": j["collectedAt"]
            }
            f.write(json.dumps(canonical_obj, ensure_ascii=False) + "\n")
    logger.info(f"Wrote {len(jobs)} records to {filepath}")


def export_canonical_csv(jobs: list, filepath: str):
    """Write canonical CSV export with standard column headers."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    headers = [
        "job_id",
        "job_title",
        "company_name",
        "category",
        "job_description",
        "required_skills",
        "experience_level",
        "location",
        "remote_type",
        "salary_min",
        "salary_max",
        "currency",
        "employment_type",
        "vacancy_status",
        "application_url",
        "posted_at",
        "source_name",
        "provenance",
        "collected_at"
    ]

    with open(filepath, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(headers)
        for j in jobs:
            skills_str = json.dumps(j["requiredSkills"], ensure_ascii=False) if j["requiredSkills"] else "[]"
            writer.writerow([
                j["jobId"],
                j["jobTitle"],
                j["companyName"],
                j["category"],
                j["jobDescription"] or "",
                skills_str,
                j["experienceLevel"] or "",
                j["location"] or "",
                j["remoteType"] or "",
                j["salaryMin"] if j["salaryMin"] is not None else "",
                j["salaryMax"] if j["salaryMax"] is not None else "",
                j["currency"] or "",
                j["employmentType"] or "",
                j["vacancyStatus"] or "ACTIVE",
                j["applicationUrl"],
                j["postedAt"] or "",
                j["sourceName"],
                j["provenance"],
                j["collectedAt"]
            ])
    logger.info(f"Wrote {len(jobs)} rows to {filepath}")


def sync_sqlite_db(jobs: list, db_path: str):
    """Create ai_jobs table and insert canonical jobs while strictly preserving existing tables."""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Create ai_jobs table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS ai_jobs (
        job_id TEXT PRIMARY KEY,
        job_title TEXT NOT NULL,
        company_name TEXT NOT NULL,
        category TEXT NOT NULL,
        job_description TEXT,
        required_skills TEXT,
        experience_level TEXT,
        location TEXT,
        remote_type TEXT,
        salary_min REAL,
        salary_max REAL,
        currency TEXT,
        employment_type TEXT,
        vacancy_status TEXT NOT NULL,
        application_url TEXT NOT NULL,
        posted_at TEXT,
        source_name TEXT NOT NULL,
        provenance TEXT NOT NULL,
        collected_at TEXT NOT NULL
    )
    """)

    # Clear only ai_jobs table if it already exists
    cur.execute("DELETE FROM ai_jobs")

    insert_sql = """
    INSERT INTO ai_jobs (
        job_id, job_title, company_name, category, job_description,
        required_skills, experience_level, location, remote_type,
        salary_min, salary_max, currency, employment_type, vacancy_status,
        application_url, posted_at, source_name, provenance, collected_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    rows_to_insert = []
    for j in jobs:
        skills_str = json.dumps(j["requiredSkills"], ensure_ascii=False) if j["requiredSkills"] else "[]"
        rows_to_insert.append((
            j["jobId"],
            j["jobTitle"],
            j["companyName"],
            j["category"],
            j["jobDescription"],
            skills_str,
            j["experienceLevel"],
            j["location"],
            j["remoteType"],
            j["salaryMin"],
            j["salaryMax"],
            j["currency"],
            j["employmentType"],
            j["vacancyStatus"],
            j["applicationUrl"],
            j["postedAt"],
            j["sourceName"],
            j["provenance"],
            j["collectedAt"]
        ))

    cur.executemany(insert_sql, rows_to_insert)
    conn.commit()
    logger.info(f"Synchronized {len(rows_to_insert)} rows into table 'ai_jobs' in {db_path}")

    # Verify all table counts in database
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [r[0] for r in cur.fetchall()]
    table_counts = {}
    for t in tables:
        cur.execute(f"SELECT count(*) FROM {t}")
        table_counts[t] = cur.fetchone()[0]

    conn.close()
    return table_counts


async def main():
    logger.info("=== Starting Stage 2: AI Job Acquisition ===")
    collector = AIJobCollector(timeout=15.0)
    jobs = await collector.run()

    if len(jobs) < 1000:
        logger.error(f"Target of at least 1,000 unique jobs not met: collected {len(jobs)}")
        sys.exit(1)

    logger.info(f"Target exceeded successfully: {len(jobs)} unique AI job vacancies collected.")

    # 1. Export JSONL
    export_canonical_jsonl(jobs, CANONICAL_JSONL_PATH)

    # 2. Export CSV
    export_canonical_csv(jobs, CANONICAL_CSV_PATH)

    # 3. SQLite Synchronization
    table_counts = sync_sqlite_db(jobs, DB_PATH)
    logger.info("Database Table Counts:")
    for t, cnt in table_counts.items():
        logger.info(f"  {t}: {cnt} rows")

    logger.info("=== Stage 2 Job Acquisition Complete ===")


if __name__ == "__main__":
    asyncio.run(main())
