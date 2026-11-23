import json
import csv
import sqlite3

# Load canonical products
with open("data/canonical/canonical_products.jsonl", "r", encoding="utf-8") as f:
    products = [json.loads(line) for line in f]

updated_products = []

pricing_model_counts = {}
access_type_counts = {}
actual_price_counts = {"numeric_or_tier": 0, "null": 0}

for p in products:
    d = p["content"]["data"]
    source_name = p["source"]["name"]
    source_url = p["source"]["url"]
    prod_type = d.get("productType", "")
    current_pricing = d.get("pricingModel", "")
    current_license = d.get("license", "")
    
    # 1. Determine Access Type
    if "Foundation Model" in prod_type or "Weights" in prod_type:
        access_type = "Open Weights / Downloadable"
    elif "Interactive Space (gradio)" in prod_type:
        access_type = "Hosted Web Application (Gradio)"
    elif "Interactive Space (static)" in prod_type:
        access_type = "Hosted Web Application (Static)"
    elif "Interactive Space (docker)" in prod_type:
        access_type = "Hosted Container (Docker)"
    elif "Interactive Space (streamlit)" in prod_type:
        access_type = "Hosted Web Application (Streamlit)"
    elif "Product Launch / SaaS" in prod_type or "Product Hunt" in source_name:
        access_type = "Cloud Web Service / SaaS"
    elif "Interactive Space" in prod_type:
        access_type = "Hosted Web Application / Space"
    else:
        access_type = "Cloud Web Service / SaaS"
        
    access_type_counts[access_type] = access_type_counts.get(access_type, 0) + 1

    # 2. Determine Pricing Model (Commercial model, not a price value)
    if "Gated" in current_pricing or "Gated" in str(current_license):
        pricing_model = "Gated Research"
        clean_license = "Gated Open Research"
    elif "Foundation Model" in prod_type or "Weights" in prod_type:
        pricing_model = "Open Source"
        clean_license = current_license if current_license and current_license != "None" else "Open Source"
    elif "Interactive Space" in prod_type or "Space" in source_name:
        pricing_model = "Free Web Application"
        clean_license = "Open Source" if current_license == "Open Source" else current_license
    elif "Product Hunt" in source_name or "Product Launch" in prod_type:
        pricing_model = "Freemium"
        clean_license = None
    else:
        pricing_model = "Open Source"
        clean_license = current_license

    pricing_model_counts[pricing_model] = pricing_model_counts.get(pricing_model, 0) + 1

    # 3. Determine Actual Price (Strictly null for open source weights and free web apps)
    # Never treat "Open Source Weights" or "Free Web App" as an actual price.
    actual_price = None  # None of the collected open models or free gradio demos charge a monetary fee
    actual_price_counts["null"] += 1

    # Update data dictionary
    d["pricingModel"] = pricing_model
    d["license"] = clean_license
    d["accessType"] = access_type
    d["actualPrice"] = actual_price

    updated_products.append(p)

print("Pricing Model Distribution:")
for k, v in pricing_model_counts.items():
    print(f"  {k}: {v}")

print("\nAccess Type Distribution:")
for k, v in access_type_counts.items():
    print(f"  {k}: {v}")

print(f"\nActual Price Completeness: null={actual_price_counts['null']}, populated={actual_price_counts['numeric_or_tier']}")

# Save updated canonical_products.jsonl
with open("data/canonical/canonical_products.jsonl", "w", encoding="utf-8") as f:
    for p in updated_products:
        f.write(json.dumps(p, ensure_ascii=False) + "\n")

# Save updated canonical_products.csv
csv_cols = [
    "product_id", "entity_name", "product_type", "ai_task_category",
    "developer_or_company", "developer_profile_url", "official_company_website",
    "pricing_model", "license", "access_type", "actual_price",
    "original_source_url", "provenance_source", "description", "collected_at"
]

with open("data/canonical/canonical_products.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(csv_cols)
    for cp in updated_products:
        d = cp["content"]["data"]
        writer.writerow([
            d.get("productId"),
            cp["content"]["entityName"],
            d.get("productType"),
            d.get("aiTaskCategory"),
            d.get("developerOrCompany"),
            d.get("developerProfileUrl"),
            d.get("officialCompanyWebsite"),
            d.get("pricingModel"),
            d.get("license"),
            d.get("accessType"),
            d.get("actualPrice"),  # explicitly None -> empty string in CSV
            cp["source"]["url"],
            cp["source"]["name"],
            d.get("description"),
            cp.get("collectedAt")
        ])

# Update SQLite table ai_products
with sqlite3.connect("data/normalized/ai_ecosystem.db") as conn:
    c = conn.cursor()
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
    for cp in updated_products:
        d = cp["content"]["data"]
        c.execute("INSERT INTO ai_products VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (
            d.get("productId"),
            cp["content"]["entityName"],
            d.get("productType"),
            d.get("aiTaskCategory"),
            d.get("developerOrCompany"),
            d.get("developerProfileUrl"),
            d.get("officialCompanyWebsite"),
            d.get("pricingModel"),
            d.get("license"),
            d.get("accessType"),
            d.get("actualPrice"),
            cp["source"]["url"],
            cp["source"]["name"],
            d.get("description"),
            cp.get("collectedAt")
        ))
    conn.commit()

print(f"\nSuccessfully reconciled {len(updated_products)} products across JSONL, CSV, and SQLite.")
