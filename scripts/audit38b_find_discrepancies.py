"""
Audit 38B: Identify the 9 Vacancy Discrepancies
==============================================
Compares audit38a_vacancy_verification.csv against ai_jobs in data/working/rolling_ai_ecosystem.db.
Identifies:
- 8 Lever records (Palantir & Zilliz):
    Audit CSV: EMPLOYER_CONFIRMED_OPEN / ACTIVE
    Database:  EMPLOYER_CONFIRMED_OPEN / EXPIRED
- 1 Remotive record:
    Audit CSV: CLOSED / CLOSED
    Database:  AGGREGATOR_LISTED / SOURCE_LISTED
"""

import sqlite3
import csv
import os

WORKSPACE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
DB_PATH = os.path.join(WORKSPACE_DIR, "data", "working", "rolling_ai_ecosystem.db")
AUDIT_CSV = os.path.join(WORKSPACE_DIR, "audit38a_vacancy_verification.csv")

def find_discrepancies():
    # Read audit CSV
    audit_records = {}
    with open(AUDIT_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            audit_records[r["job_id"]] = r

    print(f"Loaded {len(audit_records)} records from {AUDIT_CSV}")

    # Read database records
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    discrepancies = []
    for job_id, a_rec in audit_records.items():
        c.execute("""
            SELECT job_id, company_name, job_title, source_name, application_url, 
                   job_status, vacancy_status, posted_at, collected_at 
            FROM ai_jobs WHERE job_id = ?
        """, (job_id,))
        row = c.fetchone()
        if not row:
            print(f"[MISSING IN DB] {job_id}")
            continue

        db_job_status = row["job_status"]
        db_vacancy_status = row["vacancy_status"]
        aud_job_status = a_rec["audited_job_status"]
        aud_vacancy_status = a_rec["audited_vacancy_status"]

        if db_job_status != aud_job_status or db_vacancy_status != aud_vacancy_status:
            discrepancies.append({
                "job_id": job_id,
                "company_name": row["company_name"],
                "job_title": row["job_title"],
                "source_name": row["source_name"],
                "application_url": row["application_url"],
                "posted_at": row["posted_at"],
                "db_job_status": db_job_status,
                "db_vacancy_status": db_vacancy_status,
                "audit_job_status": aud_job_status,
                "audit_vacancy_status": aud_vacancy_status,
                "audit_evidence": a_rec.get("actual_vacancy_status_evidence", ""),
                "http_status": a_rec.get("http_status", "")
            })

    conn.close()

    print(f"\nFound {len(discrepancies)} discrepancies between database and audit CSV:")
    print("-" * 100)
    for idx, d in enumerate(discrepancies, 1):
        print(f"[{idx}] Job ID: {d['job_id']}")
        print(f"    Company: {d['company_name']} | Source: {d['source_name']}")
        print(f"    Title:   {d['job_title']}")
        print(f"    URL:     {d['application_url']}")
        print(f"    DB:      job_status={d['db_job_status']} | vacancy_status={d['db_vacancy_status']}")
        print(f"    Audit:   job_status={d['audit_job_status']} | vacancy_status={d['audit_vacancy_status']}")
        print(f"    HTTP:    {d['http_status']} | Evidence: {d['audit_evidence']}")
        print("-" * 100)

if __name__ == "__main__":
    find_discrepancies()
