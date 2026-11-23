import asyncio
import json
import csv
import sqlite3
import os
import sys
sys.path.insert(0, ".")

from sources.ai_news_collector import AINewsCollector

async def main():
    print("=" * 70)
    print("STAGE 1: AI NEWS ACQUISITION PIPELINE")
    print("=" * 70)

    collector = AINewsCollector()
    news_items = await collector.collect_all(target_count=1050)

    print(f"\nTotal raw articles collected: {len(news_items):,}")

    # Deduplicate strictly by canonical article_url and title
    unique_map = {}
    for item in news_items:
        url = item["article_url"]
        title_lower = item["title"].lower().strip()
        if url not in unique_map and title_lower not in [x["title"].lower().strip() for x in unique_map.values()]:
            unique_map[url] = item

    unique_news = list(unique_map.values())
    print(f"Total unique verified AI news records: {len(unique_news):,}")

    # 1. Format into Canonical JSON Schema
    canonical_objects = []
    for n in unique_news:
        canonical_objects.append({
            "schemaVersion": "1.0",
            "recordType": "AI_NEWS",
            "source": {
                "name": n["source_name"],
                "url": n["article_url"]
            },
            "content": {
                "entityName": n["title"],
                "data": {
                    "newsId": n["news_id"],
                    "title": n["title"],
                    "summary": n["summary"],
                    "content": n["content"],
                    "sourceName": n["source_name"],
                    "articleUrl": n["article_url"],
                    "author": n["author"],
                    "publishedAt": n["published_at"],
                    "category": n["category"],
                    "relatedCompanies": n["related_companies"],
                    "provenance": n["provenance"]
                }
            },
            "collectedAt": n["collected_at"]
        })

    # Write data/canonical/canonical_news.jsonl
    jsonl_path = "data/canonical/canonical_news.jsonl"
    with open(jsonl_path, "w", encoding="utf-8") as f:
        for obj in canonical_objects:
            f.write(json.dumps(obj, ensure_ascii=False) + "\n")
    print(f"Exported {len(canonical_objects):,} records to {jsonl_path}")

    # 2. Write data/canonical/canonical_news.csv
    csv_path = "data/canonical/canonical_news.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "news_id", "title", "summary", "content", "source_name",
            "article_url", "author", "published_at", "category",
            "related_companies", "collected_at", "provenance"
        ])
        for obj in canonical_objects:
            d = obj["content"]["data"]
            cos_str = "; ".join(d.get("relatedCompanies", []))
            writer.writerow([
                d.get("newsId"),
                d.get("title"),
                d.get("summary"),
                d.get("content"),
                d.get("sourceName"),
                d.get("articleUrl"),
                d.get("author"),
                d.get("publishedAt"),
                d.get("category"),
                cos_str,
                obj.get("collectedAt"),
                d.get("provenance")
            ])
    print(f"Exported {len(canonical_objects):,} rows to {csv_path}")

    # 3. Synchronize SQLite Table in data/normalized/ai_ecosystem.db
    db_path = "data/normalized/ai_ecosystem.db"
    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        c.execute("DROP TABLE IF EXISTS ai_news")
        c.execute("""
        CREATE TABLE ai_news (
            news_id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            summary TEXT,
            content TEXT,
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
        for obj in canonical_objects:
            d = obj["content"]["data"]
            cos_str = "; ".join(d.get("relatedCompanies", []))
            c.execute("INSERT INTO ai_news VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (
                d.get("newsId"),
                d.get("title"),
                d.get("summary"),
                d.get("content"),
                d.get("sourceName"),
                d.get("articleUrl"),
                d.get("author"),
                d.get("publishedAt"),
                d.get("category"),
                cos_str,
                obj.get("collectedAt"),
                d.get("provenance")
            ))
        conn.commit()
    print(f"Synchronized table 'ai_news' in {db_path} with {len(canonical_objects):,} records.")

if __name__ == "__main__":
    asyncio.run(main())
