import json
import csv
import sqlite3
import pandas as pd

# Load startups to build official company website lookup
with open("data/canonical/canonical_startups.jsonl", "r", encoding="utf-8") as f:
    startups = [json.loads(line) for line in f]

org_to_website = {}
for s in startups:
    name = s["content"]["entityName"].lower().strip()
    web = s["content"]["data"].get("website")
    if web:
        org_to_website[name] = web

# Add common major AI lab mappings
major_mappings = {
    "mistralai": "https://mistral.ai",
    "meta-llama": "https://about.meta.com",
    "meta": "https://about.meta.com",
    "openai": "https://openai.com",
    "cohere": "https://cohere.com",
    "stabilityai": "https://stability.ai",
    "google": "https://about.google",
    "deepseek-ai": "https://www.deepseek.com",
    "deepseek": "https://www.deepseek.com",
    "qwen": "https://qwenlm.github.io",
    "alibaba": "https://www.alibabagroup.com",
    "microsoft": "https://www.microsoft.com",
    "anthropic": "https://www.anthropic.com",
    "elevenlabs": "https://elevenlabs.io",
    "lightricks": "https://www.lightricks.com",
    "minimaxai": "https://www.minimaxi.com",
    "huggingface": "https://huggingface.co"
}
org_to_website.update(major_mappings)

# Process products
with open("data/canonical/canonical_products.jsonl", "r", encoding="utf-8") as f:
    products = [json.loads(line) for line in f]

updated_products = []
for p in products:
    data = p["content"]["data"]
    dev = data.get("developerOrCompany", "").strip()
    dev_lower = dev.lower()

    # Determine developer profile URL
    source_url = p["source"]["url"]
    if "huggingface.co" in source_url:
        dev_profile = f"https://huggingface.co/{dev}"
    elif "producthunt.com" in source_url:
        dev_profile = source_url
    else:
        dev_profile = None

    # Determine official corporate website
    official_web = None
    if dev_lower in org_to_website:
        official_web = org_to_website[dev_lower]
    elif dev.replace("-", " ").lower() in org_to_website:
        official_web = org_to_website[dev.replace("-", " ").lower()]

    # Explicitly separate fields
    data["developerProfileUrl"] = dev_profile
    data["officialCompanyWebsite"] = official_web
    data["companyWebsite"] = official_web  # Reconcile so companyWebsite represents actual corporate website

    updated_products.append(p)

# Write updated canonical_products.jsonl
with open("data/canonical/canonical_products.jsonl", "w", encoding="utf-8") as f:
    for p in updated_products:
        f.write(json.dumps(p, ensure_ascii=False) + "\n")

# Write updated canonical_products.csv
with open("data/canonical/canonical_products.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow([
        "product_id", "entity_name", "product_type", "ai_task_category",
        "developer_or_company", "developer_profile_url", "official_company_website",
        "pricing_model", "license", "original_source_url", "provenance_source",
        "description", "collected_at"
    ])
    for cp in updated_products:
        d = cp["content"]["data"]
        writer.writerow([
            d["productId"], cp["content"]["entityName"], d["productType"],
            d["aiTaskCategory"], d["developerOrCompany"], d["developerProfileUrl"],
            d["officialCompanyWebsite"], d["pricingModel"], d["license"],
            cp["source"]["url"], cp["source"]["name"], d["description"], cp["collectedAt"]
        ])

# Update ai_ecosystem.db table ai_products
with sqlite3.connect("data/normalized/ai_ecosystem.db") as conn:
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS ai_products")
    cursor.execute("""
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
        original_source_url TEXT,
        provenance_source TEXT,
        description TEXT,
        collected_at TEXT
    )
    """)
    for cp in updated_products:
        d = cp["content"]["data"]
        cursor.execute("INSERT INTO ai_products VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (
            d["productId"], cp["content"]["entityName"], d["productType"],
            d["aiTaskCategory"], d["developerOrCompany"], d["developerProfileUrl"],
            d["officialCompanyWebsite"], d["pricingModel"], d["license"],
            cp["source"]["url"], cp["source"]["name"], d["description"], cp["collectedAt"]
        ))
    conn.commit()

# Re-generate canonical_submission_all.jsonl
with open("data/canonical/canonical_startups.jsonl", "r", encoding="utf-8") as f:
    startups_all = [json.loads(line) for line in f]
with open("data/canonical/canonical_research_papers.jsonl", "r", encoding="utf-8") as f:
    papers_all = [json.loads(line) for line in f]

with open("data/canonical/canonical_submission_all.jsonl", "w", encoding="utf-8") as f:
    for item in startups_all + updated_products + papers_all:
        f.write(json.dumps(item, ensure_ascii=False) + "\n")

# Update root backward compatibility files
with open("data/startups_and_products.jsonl", "w", encoding="utf-8") as f:
    for item in startups_all + updated_products + papers_all:
        f.write(json.dumps(item, ensure_ascii=False) + "\n")

print(f"Products updated: {len(updated_products):,} records with distinct developerProfileUrl vs officialCompanyWebsite.")
web_count = sum(1 for p in updated_products if p["content"]["data"]["officialCompanyWebsite"] is not None)
profile_count = sum(1 for p in updated_products if p["content"]["data"]["developerProfileUrl"] is not None)
print(f"  - Populated developerProfileUrl: {profile_count:,} / {len(updated_products):,}")
print(f"  - Populated officialCompanyWebsite: {web_count:,} / {len(updated_products):,}")
