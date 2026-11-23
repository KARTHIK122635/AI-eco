import json
import csv
import sqlite3

jsonl_path = "data/canonical/canonical_news.jsonl"
csv_path = "data/canonical/canonical_news.csv"
db_path = "data/normalized/ai_ecosystem.db"

# 1. Load canonical JSONL
with open(jsonl_path, "r", encoding="utf-8") as f:
    records = [json.loads(line) for line in f]

corrected_record = None
for r in records:
    d = r["content"]["data"]
    if d.get("newsId") == "news_54f7ad0b4a0462af" or d.get("title") == "Research Reports":
        print("Found target record:", d.get("title"), "Current status:", d.get("contentStatus"))
        d["contentStatus"] = "PUBLISHER_EXCERPT"
        d["summaryType"] = "PUBLISHER_SUMMARY"
        corrected_record = r
        print("Updated status to:", d.get("contentStatus"))

# 2. Write updated JSONL
with open(jsonl_path, "w", encoding="utf-8") as f:
    for r in records:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")

# 3. Write updated CSV
with open(csv_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow([
        "news_id", "title", "summary", "content", "content_status", "summary_type",
        "content_retrieved_at", "source_name", "article_url", "author",
        "published_at", "category", "related_companies", "collected_at", "provenance"
    ])
    for r in records:
        d = r["content"]["data"]
        cos_str = "; ".join(d.get("relatedCompanies", []))
        writer.writerow([
            d.get("newsId"),
            d.get("title"),
            d.get("summary"),
            d.get("content"),
            d.get("contentStatus"),
            d.get("summaryType"),
            d.get("contentRetrievedAt"),
            d.get("sourceName"),
            d.get("articleUrl"),
            d.get("author"),
            d.get("publishedAt"),
            d.get("category"),
            cos_str,
            r.get("collectedAt"),
            d.get("provenance")
        ])

# 4. Update SQLite table ai_news
with sqlite3.connect(db_path) as conn:
    c = conn.cursor()
    c.execute("""
    UPDATE ai_news
    SET content_status = 'PUBLISHER_EXCERPT', summary_type = 'PUBLISHER_SUMMARY'
    WHERE news_id = 'news_54f7ad0b4a0462af'
    """)
    conn.commit()

print("Successfully applied correction across JSONL, CSV, and SQLite!")
