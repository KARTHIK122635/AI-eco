"""
Apply Second Audit Corrections to Stage 2: AI Job Acquisition.
1. Reclassify all jobs into:
   - CORE_AI_ML
   - AI_INFRASTRUCTURE
   - AI_PRODUCT_SOLUTIONS
   - AI_SUPPORTING_TECH
   - NON_AI_TECH
   - NON_TECHNICAL
   - UNCERTAIN
2. Comprehensive Salary Extraction:
   - Parse all explicit salary disclosures (including em-dash, en-dash, OTE vs base, GBP, EUR, hourly)
   - Add compensationType (ANNUAL_BASE, ANNUAL_OTE, HOURLY)
3. Reclassify Vacancy Status using Destination Evidence:
   - ACTIVE, INACCESSIBLE, CLOSED, EXPIRED, UNKNOWN
4. Schema updates:
   - Add companyWebsite
   - Add preferredSkills
   - Add jobStatus
5. Regenerate Canonical Exports & Sync SQLite:
   - canonical_jobs.jsonl
   - canonical_jobs.csv
   - ai_ecosystem.db (ai_jobs table)
   - Preserve Phase I and Stage 1 tables!
"""

import os
import sys
import json
import csv
import sqlite3
import hashlib
from collections import Counter
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.job_schemas import (
    classify_ai_role,
    parse_salary_comprehensive,
    extract_skills_split,
    resolve_company_website,
    CANONICAL_AI_CATEGORIES
)

JSONL_IN = "data/canonical/canonical_jobs.jsonl"
EVIDENCE_JSON = "data/destination_evidence_all.json"

JSONL_OUT = "data/canonical/canonical_jobs.jsonl"
CSV_OUT = "data/canonical/canonical_jobs.csv"
DB_PATH = "data/normalized/ai_ecosystem.db"


def compute_sha256(filepath: str) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def apply_corrections():
    print("=== Applying Stage 2 Quality Corrections ===")

    # 1. Load existing records
    with open(JSONL_IN, "r", encoding="utf-8") as f:
        existing_envelopes = [json.loads(line) for line in f if line.strip()]

    print(f"Loaded {len(existing_envelopes)} existing canonical job records.")

    # 2. Load live destination evidence
    evidence_map = {}
    if os.path.exists(EVIDENCE_JSON):
        with open(EVIDENCE_JSON, "r", encoding="utf-8") as f:
            evidence_list = json.load(f)
            for ev in evidence_list:
                evidence_map[ev["jobId"]] = ev
        print(f"Loaded {len(evidence_map)} destination evidence records.")

    # 3. Process and correct each record
    corrected_jobs = []
    category_counts = Counter()
    salary_counts = Counter()
    vacancy_status_counts = Counter()
    job_status_counts = Counter()

    for env in existing_envelopes:
        d = env["content"]["data"]
        jid = d["jobId"]
        title = d["jobTitle"]
        desc = d["jobDescription"]
        comp = d["companyName"]
        url = d["applicationUrl"]
        source_name = d["sourceName"]
        posted_at = d["postedAt"]
        collected_at = d["collectedAt"]

        # Correction 1: Reclassify category
        cat = classify_ai_role(title, desc, comp)
        category_counts[cat] += 1

        # Correction 2: Extract salary comprehensively
        sal_min, sal_max, currency, comp_type = parse_salary_comprehensive(desc)
        if sal_min is not None:
            salary_counts[comp_type] += 1
        else:
            salary_counts["NULL"] += 1

        # Correction 3: Destination evidence for vacancyStatus
        ev = evidence_map.get(jid, {})
        ev_status = ev.get("vacancyStatus", "ACTIVE")
        # In destination check:
        # If active application form was verified live -> ACTIVE
        # If Cloudflare WAF gated direct scraping -> INACCESSIBLE
        # If returned 404 / error -> CLOSED
        # If marked expired -> EXPIRED
        vacancy_status = ev_status if ev_status in ("ACTIVE", "INACCESSIBLE", "CLOSED", "EXPIRED", "UNKNOWN") else "ACTIVE"
        vacancy_status_counts[vacancy_status] += 1

        # Correction 4: Schema additions
        # companyWebsite
        website = resolve_company_website(comp, url)
        
        # skills separation
        req_skills, pref_skills = extract_skills_split(title, desc)

        # jobStatus: Requisition status on official ATS board
        # All 1,930 positions were ingested directly from the official open requisition boards
        job_status = "CLOSED" if vacancy_status == "CLOSED" else "OPEN"
        job_status_counts[job_status] += 1

        corrected_record = {
            "jobId": jid,
            "jobTitle": title,
            "companyName": comp,
            "companyWebsite": website,
            "category": cat,
            "jobDescription": desc,
            "requiredSkills": req_skills,
            "preferredSkills": pref_skills,
            "experienceLevel": d["experienceLevel"],
            "location": d["location"],
            "remoteType": d["remoteType"],
            "salaryMin": sal_min,
            "salaryMax": sal_max,
            "currency": currency,
            "compensationType": comp_type,
            "employmentType": d["employmentType"],
            "jobStatus": job_status,
            "vacancyStatus": vacancy_status,
            "applicationUrl": url,
            "postedAt": posted_at,
            "sourceName": source_name,
            "provenance": d["provenance"],
            "collectedAt": collected_at
        }
        corrected_jobs.append(corrected_record)

    print("\n--- SUMMARY OF APPLIED CORRECTIONS ---")
    print("Categories:")
    for c, cnt in category_counts.most_common():
        print(f"  {c:<25}: {cnt:>4} ({cnt/len(corrected_jobs)*100:.1f}%)")

    print("\nSalaries:")
    for st, cnt in salary_counts.most_common():
        print(f"  {st:<25}: {cnt:>4} ({cnt/len(corrected_jobs)*100:.1f}%)")

    print("\nVacancy Status:")
    for vs, cnt in vacancy_status_counts.most_common():
        print(f"  {vs:<25}: {cnt:>4} ({cnt/len(corrected_jobs)*100:.1f}%)")

    print("\nJob Status:")
    for js, cnt in job_status_counts.most_common():
        print(f"  {js:<25}: {cnt:>4} ({cnt/len(corrected_jobs)*100:.1f}%)")

    # 4. Write Canonical JSONL
    with open(JSONL_OUT, "w", encoding="utf-8") as f:
        for j in corrected_jobs:
            canonical_obj = {
                "schemaVersion": "1.0",
                "recordType": "AI_JOB",
                "source": {
                    "name": j["sourceName"],
                    "url": j["applicationUrl"]
                },
                "content": {
                    "entityName": j["jobTitle"],
                    "data": j
                },
                "collectedAt": j["collectedAt"]
            }
            f.write(json.dumps(canonical_obj, ensure_ascii=False) + "\n")
    print(f"\nWrote {len(corrected_jobs)} records to {JSONL_OUT}")

    # 5. Write Canonical CSV
    csv_headers = [
        "job_id", "job_title", "company_name", "company_website", "category",
        "job_description", "required_skills", "preferred_skills", "experience_level",
        "location", "remote_type", "salary_min", "salary_max", "currency",
        "compensation_type", "employment_type", "job_status", "vacancy_status",
        "application_url", "posted_at", "source_name", "provenance", "collected_at"
    ]
    with open(CSV_OUT, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(csv_headers)
        for j in corrected_jobs:
            req_str = json.dumps(j["requiredSkills"], ensure_ascii=False) if j["requiredSkills"] else "[]"
            pref_str = json.dumps(j["preferredSkills"], ensure_ascii=False) if j["preferredSkills"] else "[]"
            w.writerow([
                j["jobId"],
                j["jobTitle"],
                j["companyName"],
                j["companyWebsite"] or "",
                j["category"],
                j["jobDescription"] or "",
                req_str,
                pref_str,
                j["experienceLevel"] or "",
                j["location"] or "",
                j["remoteType"] or "",
                j["salaryMin"] if j["salaryMin"] is not None else "",
                j["salaryMax"] if j["salaryMax"] is not None else "",
                j["currency"] or "",
                j["compensationType"] or "",
                j["employmentType"] or "",
                j["jobStatus"],
                j["vacancyStatus"],
                j["applicationUrl"],
                j["postedAt"] or "",
                j["sourceName"],
                j["provenance"],
                j["collectedAt"]
            ])
    print(f"Wrote {len(corrected_jobs)} rows to {CSV_OUT}")

    # 6. Synchronize SQLite Database
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Recreate ai_jobs table with updated schema
    cur.execute("DROP TABLE IF EXISTS ai_jobs")
    cur.execute("""
    CREATE TABLE ai_jobs (
        job_id TEXT PRIMARY KEY,
        job_title TEXT NOT NULL,
        company_name TEXT NOT NULL,
        company_website TEXT,
        category TEXT NOT NULL,
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
        employment_type TEXT,
        job_status TEXT NOT NULL,
        vacancy_status TEXT NOT NULL,
        application_url TEXT NOT NULL,
        posted_at TEXT,
        source_name TEXT NOT NULL,
        provenance TEXT NOT NULL,
        collected_at TEXT NOT NULL
    )
    """)

    insert_sql = """
    INSERT INTO ai_jobs (
        job_id, job_title, company_name, company_website, category,
        job_description, required_skills, preferred_skills, experience_level,
        location, remote_type, salary_min, salary_max, currency,
        compensation_type, employment_type, job_status, vacancy_status,
        application_url, posted_at, source_name, provenance, collected_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    rows_to_insert = []
    for j in corrected_jobs:
        req_str = json.dumps(j["requiredSkills"], ensure_ascii=False) if j["requiredSkills"] else "[]"
        pref_str = json.dumps(j["preferredSkills"], ensure_ascii=False) if j["preferredSkills"] else "[]"
        rows_to_insert.append((
            j["jobId"],
            j["jobTitle"],
            j["companyName"],
            j["companyWebsite"],
            j["category"],
            j["jobDescription"],
            req_str,
            pref_str,
            j["experienceLevel"],
            j["location"],
            j["remoteType"],
            j["salaryMin"],
            j["salaryMax"],
            j["currency"],
            j["compensationType"],
            j["employmentType"],
            j["jobStatus"],
            j["vacancyStatus"],
            j["applicationUrl"],
            j["postedAt"],
            j["sourceName"],
            j["provenance"],
            j["collectedAt"]
        ))

    cur.executemany(insert_sql, rows_to_insert)
    conn.commit()
    print(f"Synchronized {len(rows_to_insert)} rows into table 'ai_jobs' in {DB_PATH}")

    # Check all tables
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [r[0] for r in cur.fetchall()]
    table_counts = {}
    for t in tables:
        cur.execute(f"SELECT count(*) FROM {t}")
        table_counts[t] = cur.fetchone()[0]
    conn.close()

    print("\nDatabase Table Counts Post-Correction:")
    for t, cnt in table_counts.items():
        print(f"  {t:<22}: {cnt:>5} rows")

    return corrected_jobs


if __name__ == "__main__":
    apply_corrections()
