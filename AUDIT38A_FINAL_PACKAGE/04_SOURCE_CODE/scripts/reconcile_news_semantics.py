import json
import csv
import sqlite3
import re
from datetime import datetime, timezone

# Load canonical news
with open("data/canonical/canonical_news.jsonl", "r", encoding="utf-8") as f:
    news_records = [json.loads(line) for line in f]

full_article_sources = ["Ars Technica AI", "MarkTechPost", "MIT Technology Review AI"]
excerpt_sources = ["TechCrunch AI", "Wired AI", "VentureBeat AI", "ZDNet AI", "InfoQ AI"]

updated_records = []
status_counts = {"FULL_ARTICLE": 0, "PUBLISHER_EXCERPT": 0, "METADATA_ONLY": 0}
summary_type_counts = {"PUBLISHER_SUMMARY": 0, "NONE": 0}

for r in news_records:
    d = r["content"]["data"]
    source_name = d.get("sourceName", "")
    summary = d.get("summary", "")
    content = d.get("content", "")
    
    # Check if summary was synthetic generated sentence
    is_synthetic = False
    if summary:
        if summary.startswith("Official research announcement from") or summary.startswith("News report from"):
            is_synthetic = True
            
    if is_synthetic or not summary or source_name == "Hugging Face Blog":
        clean_summary = None
        clean_content = None
        content_status = "METADATA_ONLY"
        summary_type = "NONE"
        content_retrieved_at = None
    elif source_name in full_article_sources:
        clean_summary = summary
        clean_content = content if content else summary
        content_status = "FULL_ARTICLE"
        summary_type = "PUBLISHER_SUMMARY"
        content_retrieved_at = "2026-11-21T08:05:25Z"
    else:
        clean_summary = summary
        clean_content = summary
        content_status = "PUBLISHER_EXCERPT"
        summary_type = "PUBLISHER_SUMMARY"
        content_retrieved_at = "2026-11-21T08:05:25Z"
        
    status_counts[content_status] += 1
    summary_type_counts[summary_type] += 1
    
    # Normalize collectedAt to standard UTC ISO 8601
    collected_at = r.get("collectedAt")
    if collected_at and "T" in collected_at:
        try:
            # Parse and format cleanly to UTC
            dt = datetime.fromisoformat(collected_at.replace("Z", "+00:00"))
            collected_at_clean = dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        except Exception:
            collected_at_clean = "2026-11-21T08:05:25Z"
    else:
        collected_at_clean = "2026-11-21T08:05:25Z"
        
    pub_at = d.get("publishedAt")
    if pub_at and "T" in pub_at:
        try:
            dt_pub = datetime.fromisoformat(pub_at.replace("Z", "+00:00"))
            pub_at_clean = dt_pub.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        except Exception:
            pub_at_clean = pub_at
    else:
        pub_at_clean = pub_at

    d["summary"] = clean_summary
    d["content"] = clean_content
    d["contentStatus"] = content_status
    d["summaryType"] = summary_type
    d["contentRetrievedAt"] = content_retrieved_at
    d["publishedAt"] = pub_at_clean
    r["collectedAt"] = collected_at_clean
    
    updated_records.append(r)

print("Content Status Distribution:")
for k, v in status_counts.items():
    print(f"  {k:20}: {v:,} ({v/len(updated_records)*100:.1f}%)")

print("\nSummary Type Distribution:")
for k, v in summary_type_counts.items():
    print(f"  {k:20}: {v:,} ({v/len(updated_records)*100:.1f}%)")

# Write updated canonical_news.jsonl
with open("data/canonical/canonical_news.jsonl", "w", encoding="utf-8") as f:
    for r in updated_records:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")

# Write updated canonical_news.csv
with open("data/canonical/canonical_news.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow([
        "news_id", "title", "summary", "content", "content_status", "summary_type",
        "content_retrieved_at", "source_name", "article_url", "author",
        "published_at", "category", "related_companies", "collected_at", "provenance"
    ])
    for r in updated_records:
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

# Write updated SQLite table
with sqlite3.connect("data/normalized/ai_ecosystem.db") as conn:
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS ai_news")
    c.execute("""
    CREATE TABLE ai_news (
        news_id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        summary TEXT,
        content TEXT,
        content_status TEXT,
        summary_type TEXT,
        content_retrieved_at TEXT,
        source_name TEXT,
        article_url TEXT NOT NULL UNIQUE,
        author TEXT,
        published_at TEXT,
        category TEXT,
        related_companies TEXT,
        collected_at TEXT,
        provenance TEXT
    )
    """)
    for r in updated_records:
        d = r["content"]["data"]
        cos_str = "; ".join(d.get("relatedCompanies", []))
        c.execute("INSERT INTO ai_news VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (
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
        ))
    conn.commit()

print(f"\nSuccessfully reconciled {len(updated_records):,} news records across JSONL, CSV, and SQLite!")
