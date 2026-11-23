"""
Comprehensive Independent Quality Audit Script for Phase II - Stage 2: AI Job Acquisition.
Audits:
1. Structural Integrity & Cross-Format Parity (JSONL, CSV, SQLite)
2. Duplicate Detection (IDs, URLs, Normalized Signatures, Cross-Source)
3. AI Relevance & Questionable Record Classification
4. Content Quality, HTML Sanitization & Salary Zero-Fabrication Verification
5. Source Concentration & Provenance Analysis
6. Phase I & Stage 1 Database Preservation
"""

import os
import sys
import json
import csv
import sqlite3
import hashlib
import re
from collections import Counter
from urllib.parse import urlparse

JSONL_PATH = "data/canonical/canonical_jobs.jsonl"
CSV_PATH = "data/canonical/canonical_jobs.csv"
DB_PATH = "data/normalized/ai_ecosystem.db"

DUPLICATES_CSV = "reports/stage2_duplicate_audit.csv"
AI_RELEVANCE_CSV = "reports/stage2_ai_relevance_audit.csv"
QUALITY_METRICS_JSON = "reports/stage2_quality_metrics.json"


def compute_sha256(filepath: str) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def run_comprehensive_audit():
    print("Starting Comprehensive Stage 2 Audit...")

    # 1. Load JSONL
    jsonl_records = []
    with open(JSONL_PATH, "r", encoding="utf-8") as f:
        for idx, line in enumerate(f):
            line = line.strip()
            if line:
                obj = json.loads(line)
                jsonl_records.append(obj)

    # 2. Load CSV
    with open(CSV_PATH, "r", encoding="utf-8") as f:
        csv_rows = list(csv.DictReader(f))

    # 3. Load SQLite
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT * FROM ai_jobs")
    cols = [d[0] for d in cur.description]
    sqlite_rows = [dict(zip(cols, r)) for r in cur.fetchall()]

    # Query all tables in DB
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [r[0] for r in cur.fetchall()]
    table_counts = {}
    for t in tables:
        cur.execute(f"SELECT count(*) FROM {t}")
        table_counts[t] = cur.fetchone()[0]
    conn.close()

    total_records = len(jsonl_records)
    print(f"Loaded records: JSONL={len(jsonl_records)}, CSV={len(csv_rows)}, SQLite={len(sqlite_rows)}")

    # -------------------------------------------------------------
    # AUDIT 1: Structural Integrity & Parity
    # -------------------------------------------------------------
    parity_counts = (len(jsonl_records) == len(csv_rows) == len(sqlite_rows) == 1930)
    
    # Check field alignment
    field_mismatches = 0
    for i in range(total_records):
        j_data = jsonl_records[i]["content"]["data"]
        c_row = csv_rows[i]
        s_row = sqlite_rows[i]
        
        # Check IDs
        if not (j_data["jobId"] == c_row["job_id"] == s_row["job_id"]):
            field_mismatches += 1
        # Check URLs
        if not (j_data["applicationUrl"] == c_row["application_url"] == s_row["application_url"]):
            field_mismatches += 1
        # Check Titles
        if not (j_data["jobTitle"] == c_row["job_title"] == s_row["job_title"]):
            field_mismatches += 1

    # -------------------------------------------------------------
    # AUDIT 2: Duplicate Detection
    # -------------------------------------------------------------
    seen_ids = Counter()
    seen_urls = Counter()
    seen_sigs = Counter()
    near_dups = []
    
    # Store duplicate audit details
    dup_audit_rows = []

    for r in jsonl_records:
        d = r["content"]["data"]
        jid = d["jobId"]
        url = d["applicationUrl"].strip().rstrip("/").lower()
        sig = f"{d['companyName'].strip().lower()}|{d['jobTitle'].strip().lower()}|{d['location'].strip().lower()}"
        
        seen_ids[jid] += 1
        seen_urls[url] += 1
        seen_sigs[sig] += 1

    # Check for possible cross-source duplicates or near duplicates (same company + normalized title)
    title_norm_map = {}
    for r in jsonl_records:
        d = r["content"]["data"]
        # Strip senior, lead, remote, etc. for fuzzy matching
        clean_title = re.sub(r'\b(senior|sr\.?|lead|staff|principal|junior|jr\.?|remote|hybrid|intern|internship)\b', '', d["jobTitle"].lower())
        clean_title = re.sub(r'[^a-z0-9]', ' ', clean_title)
        clean_title = re.sub(r'\s+', ' ', clean_title).strip()
        comp = d["companyName"].lower()
        key = (comp, clean_title)
        if key not in title_norm_map:
            title_norm_map[key] = []
        title_norm_map[key].append(d)

    possible_dups_count = 0
    for (comp, ct), items in title_norm_map.items():
        if len(items) > 1 and len(ct) > 4:
            # Different locations or different levels of same role
            possible_dups_count += (len(items) - 1)
            for item in items:
                dup_audit_rows.append({
                    "job_id": item["jobId"],
                    "company_name": item["companyName"],
                    "job_title": item["jobTitle"],
                    "location": item["location"],
                    "source_name": item["sourceName"],
                    "application_url": item["applicationUrl"],
                    "duplicate_type": "POSSIBLE_ROLE_VARIANT",
                    "notes": f"Shares normalized role '{ct}' across multiple listings/locations"
                })

    confirmed_dups = sum(v - 1 for v in seen_ids.values()) + sum(v - 1 for v in seen_urls.values()) + sum(v - 1 for v in seen_sigs.values())
    print(f"Duplicate check: Confirmed Duplicates={confirmed_dups}, Possible Role Variants={possible_dups_count}")

    # Write duplicate audit CSV
    os.makedirs("reports", exist_ok=True)
    with open(DUPLICATES_CSV, "w", encoding="utf-8", newline="") as f:
        fields = ["job_id", "company_name", "job_title", "location", "source_name", "application_url", "duplicate_type", "notes"]
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(dup_audit_rows)

    # -------------------------------------------------------------
    # AUDIT 4: AI Relevance & Questionable Records
    # -------------------------------------------------------------
    ai_relevance_rows = []
    relevance_counts = Counter()

    # Define non-technical / questionable role keywords
    questionable_keywords = [
        "accounting", "accountant", "payroll", "facilities", "workplace",
        "tax ", "audit ", "financial reporting", "revenue accounting",
        "billing", "legal counsel", "paralegal", "receptionist", "recruiter",
        "people partner", "hr coordinator", "benefits", "equity admin",
        "office manager", "executive assistant", "debt capital", "treasury"
    ]

    core_ai_keywords = [
        "machine learning", "deep learning", "research scientist", "ai engineer",
        "foundation model", "llm", "pre-training", "post-training", "alignment",
        "reinforcement learning", "computer vision", "nlp", "speech", "audio",
        "mlops", "inference", "triton", "cuda", "kernel", "gpu cluster", "perception"
    ]

    ai_enabled_tech_keywords = [
        "software engineer", "infrastructure engineer", "systems engineer",
        "platform engineer", "security engineer", "data engineer", "backend engineer",
        "full stack", "frontend", "devops", "site reliability", "architect"
    ]

    for r in jsonl_records:
        d = r["content"]["data"]
        title_lower = d["jobTitle"].lower()
        desc_lower = (d["jobDescription"] or "")[:1000].lower()
        source = d["sourceName"]
        company = d["companyName"]

        # Classification logic
        classification = "CORE_AI_ML"
        reason = "Direct AI/ML research, algorithm, or model development"

        if any(qk in title_lower for qk in questionable_keywords):
            classification = "QUESTIONABLE_NON_TECH"
            reason = f"Non-technical operational/business role at {company} (e.g. accounting, workplace, HR, finance)"
        elif any(ck in title_lower for ck in core_ai_keywords):
            classification = "CORE_AI_ML"
            reason = "Explicit AI/ML/DL/Research role in title"
        elif any(tk in title_lower for tk in ai_enabled_tech_keywords):
            if "anthropic" in source.lower() or "scale ai" in source.lower() or "together ai" in source.lower() or "coreweave" in source.lower() or "figure" in source.lower() or "cresta" in source.lower() or "snorkel" in source.lower() or "zilliz" in source.lower():
                classification = "AI_ENABLED_TECH"
                reason = f"Engineering / infrastructure role directly supporting AI model training/serving at {company}"
            elif any(ck in desc_lower for ck in core_ai_keywords):
                classification = "AI_ENABLED_TECH"
                reason = "General engineering role with substantive AI/ML tech stack in description"
            else:
                classification = "GENERIC_TECH_POSSIBLY_QUESTIONABLE"
                reason = "General engineering role without heavy AI-specific specialization in description"
        elif d["category"] in ("AI Product & Solutions", "AI Operations & Business"):
            if "product" in title_lower or "solution" in title_lower:
                classification = "AI_PRODUCT_SOLUTIONS"
                reason = "AI Product, Solutions Architecture, or Technical Customer Facing AI role"
            else:
                classification = "QUESTIONABLE_NON_TECH"
                reason = f"Non-engineering function at {company}"
        else:
            # Fallback
            if any(ck in desc_lower for ck in core_ai_keywords):
                classification = "AI_ENABLED_TECH"
                reason = "Role works directly with AI technologies based on description"
            else:
                classification = "GENERIC_TECH_POSSIBLY_QUESTIONABLE"
                reason = "Indirect or peripheral AI relevance"

        relevance_counts[classification] += 1
        ai_relevance_rows.append({
            "job_id": d["jobId"],
            "company_name": company,
            "job_title": d["jobTitle"],
            "category": d["category"],
            "source_name": source,
            "relevance_classification": classification,
            "audit_assessment": reason,
            "application_url": d["applicationUrl"]
        })

    print(f"Relevance Classification Breakdown: {dict(relevance_counts)}")

    with open(AI_RELEVANCE_CSV, "w", encoding="utf-8", newline="") as f:
        fields = ["job_id", "company_name", "job_title", "category", "source_name", "relevance_classification", "audit_assessment", "application_url"]
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(ai_relevance_rows)

    # -------------------------------------------------------------
    # AUDIT 5: Content Quality, HTML Sanitization, Salary Zero-Fabrication
    # -------------------------------------------------------------
    missing_desc = 0
    missing_comp = 0
    missing_url = 0
    html_leaks = 0
    sal_genuine = 0
    sal_null = 0
    sal_mismatches = 0

    for r in jsonl_records:
        d = r["content"]["data"]
        desc = d["jobDescription"]
        if not desc:
            missing_desc += 1
        else:
            # Check for raw HTML tags
            if bool(re.search(r'<[a-z/][^>]*>', desc, re.I)):
                html_leaks += 1
                
        if not d["companyName"]:
            missing_comp += 1
        if not d["applicationUrl"]:
            missing_url += 1

        # Salary check
        if d["salaryMin"] is not None:
            sal_genuine += 1
            # Verify salary against description text
            min_val = int(d["salaryMin"])
            min_str_1 = f"{min_val:,}"
            min_str_2 = f"{min_val//1000}k" if min_val >= 1000 else ""
            if min_str_1 not in desc and (not min_str_2 or min_str_2 not in desc.lower()):
                sal_mismatches += 1
        else:
            sal_null += 1

    print(f"Content quality: Missing Desc={missing_desc}, HTML Leaks={html_leaks}, Genuine Salaries={sal_genuine}, Null Salaries={sal_null}, Salary Mismatches={sal_mismatches}")

    # -------------------------------------------------------------
    # AUDIT 6: Source Distribution & Concentration
    # -------------------------------------------------------------
    source_counts = Counter(r["content"]["data"]["sourceName"] for r in jsonl_records)
    print("\nSource Distribution:")
    for s, c in source_counts.most_common():
        print(f"  {s:<32}: {c:>4} ({c/total_records*100:.1f}%)")

    # -------------------------------------------------------------
    # AUDIT 7: Phase I & Stage 1 Preservation
    # -------------------------------------------------------------
    expected_tables = {
        "ai_startups": 1307,
        "ai_products": 1316,
        "ai_research_papers": 1060,
        "ai_news": 1132,
        "ai_jobs": 1930
    }
    preservation_status = all(table_counts.get(k) == v for k, v in expected_tables.items())
    print(f"\nDatabase preservation status: {preservation_status}")
    print(f"Table counts: {table_counts}")

    # Checksums
    checksums = {
        "canonical_jobs.jsonl": (os.path.getsize(JSONL_PATH), compute_sha256(JSONL_PATH)),
        "canonical_jobs.csv": (os.path.getsize(CSV_PATH), compute_sha256(CSV_PATH)),
        "ai_ecosystem.db": (os.path.getsize(DB_PATH), compute_sha256(DB_PATH))
    }

    # Generate quality metrics JSON
    metrics_data = {
        "auditDate": "2026-11-21T16:20:00Z",
        "auditor": "Antigravity Autonomous Data Intelligence Agent",
        "totalRecords": total_records,
        "crossFormatParity": {
            "jsonlCount": len(jsonl_records),
            "csvCount": len(csv_rows),
            "sqliteCount": len(sqlite_rows),
            "parityStatus": parity_counts,
            "fieldMismatches": field_mismatches
        },
        "duplicateMetrics": {
            "confirmedDuplicates": confirmed_dups,
            "uniqueJobIds": len(seen_ids),
            "uniqueApplicationUrls": len(seen_urls),
            "uniqueCompanyTitleLocationSignatures": len(seen_sigs),
            "possibleRoleVariants": possible_dups_count
        },
        "aiRelevanceMetrics": dict(relevance_counts),
        "contentQualityMetrics": {
            "missingDescriptions": missing_desc,
            "rawHtmlTagLeaks": html_leaks,
            "salariesDisclosedGenuine": sal_genuine,
            "salariesNullPreserved": sal_null,
            "salaryDiscrepancies": sal_mismatches
        },
        "sourceDistribution": dict(source_counts),
        "databasePreservation": {
            "status": preservation_status,
            "actualCounts": table_counts,
            "expectedCounts": expected_tables
        },
        "checksums": {k: {"sizeBytes": v[0], "sha256": v[1]} for k, v in checksums.items()}
    }

    with open(QUALITY_METRICS_JSON, "w", encoding="utf-8") as f:
        json.dump(metrics_data, f, indent=2)

    print(f"\nWritten {QUALITY_METRICS_JSON}")


if __name__ == "__main__":
    run_comprehensive_audit()
