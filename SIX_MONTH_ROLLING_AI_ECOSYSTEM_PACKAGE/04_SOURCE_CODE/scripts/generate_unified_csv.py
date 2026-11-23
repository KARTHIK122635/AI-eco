import json
import csv

startups_file = "data/canonical/canonical_startups.jsonl"
products_file = "data/canonical/canonical_products.jsonl"
papers_file = "data/canonical/canonical_research_papers.jsonl"

output_jsonl = "data/canonical/canonical_submission_all.jsonl"
output_csv = "data/canonical/canonical_submission_all.csv"

with open(startups_file, "r", encoding="utf-8") as f:
    startups = [json.loads(line) for line in f]

with open(products_file, "r", encoding="utf-8") as f:
    products = [json.loads(line) for line in f]

with open(papers_file, "r", encoding="utf-8") as f:
    papers = [json.loads(line) for line in f]

# 1. Write unified JSONL
all_entities = startups + products + papers
with open(output_jsonl, "w", encoding="utf-8") as f:
    for item in all_entities:
        f.write(json.dumps(item, ensure_ascii=False) + "\n")

# Also update root backward-compatibility file
with open("data/startups_and_products.jsonl", "w", encoding="utf-8") as f:
    for item in all_entities:
        f.write(json.dumps(item, ensure_ascii=False) + "\n")

# 2. Write unified CSV
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
        d.get("website"),
        d.get("aiFocusArea"),
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
        d.get("categories") or "",
        str(d.get("githubStars")) if d.get("githubStars") is not None else "",
        "Open Access",
        "arXiv Non-exclusive / CC",
        "Open Access Preprint",
        "",  # actual_price
        d.get("abstract") or "",
        r.get("collectedAt")
    ])

with open(output_csv, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(headers)
    writer.writerows(rows)

print(f"Exported {len(all_entities):,} canonical items to {output_jsonl} and {output_csv}")
