import json
import csv
import sqlite3
import os

startups_file = "data/canonical/canonical_startups.jsonl"
products_file = "data/canonical/canonical_products.jsonl"
papers_file = "data/canonical/canonical_research_papers.jsonl"

with open(startups_file, "r", encoding="utf-8") as f:
    startups = [json.loads(line) for line in f]

with open(products_file, "r", encoding="utf-8") as f:
    products = [json.loads(line) for line in f]

with open(papers_file, "r", encoding="utf-8") as f:
    papers = [json.loads(line) for line in f]

all_canonical = startups + products + papers
print(f"Total Canonical Entities: {len(all_canonical):,}")
print(f"  - Startups: {len(startups):,}")
print(f"  - Products: {len(products):,}")
print(f"  - Research Papers: {len(papers):,}")

# 1. Regenerate canonical_submission_all.jsonl
with open("data/canonical/canonical_submission_all.jsonl", "w", encoding="utf-8") as f:
    for item in all_canonical:
        f.write(json.dumps(item, ensure_ascii=False) + "\n")

# 2. Regenerate canonical_submission_all.csv
headers = [
    "record_type", "canonical_id", "entity_name", "primary_url",
    "source_name", "source_url", "secondary_url", "category_or_domain",
    "metric_or_size", "pricing_model", "license", "access_type", "actual_price",
    "description_or_abstract", "collected_at"
]

rows = []

for s in startups:
    d = s["content"]["data"]
    rows.append([
        s["recordType"],
        d.get("startupId"),
        s["content"]["entityName"],
        d.get("website") or s["source"]["url"],
        s["source"]["name"],
        s["source"]["url"],
        d.get("website") or "",
        d.get("aiFocusArea") or "",
        str(d.get("employeeCount")) if d.get("employeeCount") is not None else "",
        d.get("pricingModel") or "",
        "",  # license
        "Enterprise / Commercial",
        "",  # actual_price
        d.get("description") or "",
        s.get("collectedAt")
    ])

for p in products:
    d = p["content"]["data"]
    metric_val = ""
    if d.get("metrics"):
        metric_val = str(d["metrics"].get("likes") or d["metrics"].get("downloads") or "")
    rows.append([
        p["recordType"],
        d.get("productId"),
        p["content"]["entityName"],
        p["source"]["url"],
        p["source"]["name"],
        p["source"]["url"],
        d.get("developerProfileUrl") or "",
        d.get("aiTaskCategory") or d.get("productType") or "",
        metric_val,
        d.get("pricingModel") or "",
        d.get("license") or "",
        d.get("accessType") or "",
        d.get("actualPrice") or "",
        d.get("description") or "",
        p.get("collectedAt")
    ])

for r in papers:
    d = r["content"]["data"]
    rows.append([
        r["recordType"],
        d.get("paperId"),
        r["content"]["entityName"],
        d.get("paperUrl") or r["source"]["url"],
        r["source"]["name"],
        r["source"]["url"],
        d.get("githubUrl") or "",
        ", ".join(d.get("categories", [])) if isinstance(d.get("categories"), list) else str(d.get("categories") or ""),
        str(d.get("githubStars")) if d.get("githubStars") is not None else "",
        "Open Access",
        "arXiv Non-exclusive / CC",
        "Open Access Preprint",
        "",  # actual_price
        d.get("abstract") or "",
        r.get("collectedAt")
    ])

with open("data/canonical/canonical_submission_all.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(headers)
    writer.writerows(rows)

# 3. Synchronize ai_ecosystem.db (ensure 3 clean separate tables)
with sqlite3.connect("data/normalized/ai_ecosystem.db") as conn:
    c = conn.cursor()
    
    # Table 1: ai_startups
    c.execute("DROP TABLE IF EXISTS ai_startups")
    c.execute("""
    CREATE TABLE ai_startups (
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
        description TEXT,
        collected_at TEXT
    )
    """)
    for s in startups:
        d = s["content"]["data"]
        prov = "; ".join(d.get("provenanceSources", [])) if isinstance(d.get("provenanceSources"), list) else str(d.get("provenanceSources") or "")
        ev = "; ".join(d.get("aiEvidence", [])) if isinstance(d.get("aiEvidence"), list) else str(d.get("aiEvidence") or "")
        c.execute("INSERT INTO ai_startups VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (
            d.get("startupId"), s["content"]["entityName"], d.get("aiFocusArea"),
            ev, d.get("employeeCount"), d.get("pricingModel"), d.get("website"),
            s["source"]["url"], prov, d.get("headquarters"), d.get("batchOrFounded"),
            d.get("description"), s.get("collectedAt")
        ))
        
    # Table 2: ai_products
    c.execute("DROP TABLE IF EXISTS ai_products")
    c.execute("""
    CREATE TABLE ai_products (
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
        actual_price TEXT,
        original_source_url TEXT,
        provenance_source TEXT,
        description TEXT,
        collected_at TEXT
    )
    """)
    for p in products:
        d = p["content"]["data"]
        c.execute("INSERT INTO ai_products VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (
            d.get("productId"), p["content"]["entityName"], d.get("productType"),
            d.get("aiTaskCategory"), d.get("developerOrCompany"), d.get("developerProfileUrl"),
            d.get("officialCompanyWebsite"), d.get("pricingModel"), d.get("license"),
            d.get("accessType"), d.get("actualPrice"), p["source"]["url"],
            p["source"]["name"], d.get("description"), p.get("collectedAt")
        ))
        
    # Table 3: ai_research_papers
    c.execute("DROP TABLE IF EXISTS ai_research_papers")
    c.execute("""
    CREATE TABLE ai_research_papers (
        paper_id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        authors TEXT,
        publication_date TEXT,
        categories TEXT,
        paper_url TEXT,
        github_url TEXT,
        github_stars INTEGER,
        github_star_source TEXT,
        github_star_retrieved_at TEXT,
        provenance TEXT,
        abstract TEXT,
        collected_at TEXT
    )
    """)
    for r in papers:
        d = r["content"]["data"]
        authors_str = "; ".join(d.get("authors", [])) if isinstance(d.get("authors"), list) else str(d.get("authors") or "")
        cats_str = "; ".join(d.get("categories", [])) if isinstance(d.get("categories"), list) else str(d.get("categories") or "")
        c.execute("INSERT INTO ai_research_papers VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (
            d.get("paperId"), r["content"]["entityName"], authors_str,
            d.get("publicationDate"), cats_str, d.get("paperUrl") or r["source"]["url"],
            d.get("githubUrl"), d.get("githubStars"), d.get("githubStarSource"),
            d.get("githubStarRetrievedAt"), r["source"]["name"], d.get("abstract"),
            r.get("collectedAt")
        ))
    conn.commit()

# 4. Synchronize root backward-compatibility files
with open("data/startups_and_products.jsonl", "w", encoding="utf-8") as f:
    for item in all_canonical:
        f.write(json.dumps(item, ensure_ascii=False) + "\n")

with open("data/startups_and_products.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(headers)
    writer.writerows(rows)

# Copy to root startups_and_products.db
import shutil
shutil.copy2("data/normalized/ai_ecosystem.db", "data/startups_and_products.db")

print("All canonical files and databases regenerated and synchronized successfully!")
